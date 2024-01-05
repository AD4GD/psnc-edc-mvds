# coding=utf-8
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego service-arguments.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************

from .utils import cached_property, append_to_dict
from collections import OrderedDict
from .exceptions import ImproperlyPassedArguments
import os
from arguments.base import PyPath, Result
from jinja2 import FileSystemLoader, Environment, Template, StrictUndefined
from . import templates
from six import with_metaclass, string_types
from .group import Group
import sys
import re


class ContextProxy(object):

    def __init__(self, service):
        self.service = service

    def __getattr__(self, name):
        return self.service.get_value(name)


class ServiceMetaclass(type):

    def __new__(meta, name, bases, attributes):

        static_group_classes = OrderedDict()
        attributes['_static_group_classes'] = static_group_classes

        for attribute in list(attributes.values()):
            if isinstance(attribute, type) and issubclass(attribute, Group):
                group_class = attribute
                append_to_dict(static_group_classes, group_class.get_group_class_name(), group_class, 'group')

        result = super(ServiceMetaclass, meta).__new__(meta, name, bases, attributes)

        return result


class Service(with_metaclass(ServiceMetaclass, object)):

    def __init__(self, directory=None):
        self._read_values = {}
        self._groups = OrderedDict()
        self._arguments_groups = {}
        self._arguments = OrderedDict()
        self._result_context = OrderedDict()

        self.directory = PyPath(str(directory)) if directory is not None else directory
        self.postprocessors = []
        self.initializers = []
        self.context = ContextProxy(self)

        for group_class in self._static_group_classes.values():
            self._add_group(group_class())


    @classmethod
    def setup(cls, _globals):
        service = cls()
        _globals['SERVICE'] = service
        service.explode(_globals)


    def _add_group(self, group):
         append_to_dict(self._groups, group.name, group, 'group')
         for argument_name, argument in group._arguments.items():
             append_to_dict(self._arguments_groups, argument_name, group, 'argument')
             append_to_dict(self._arguments, argument_name, argument, 'argument')


    def add_group(self, group):
        if isinstance(group, Group):
            self._add_group(group)
        elif isinstance(group, type) and issubclass(group, Group):
            self._add_group(group())
        else:
            raise ImproperlySpecifiedArguments('not a group')


    def get_context(self):
        return { name: self.get_value(name) for name in self._arguments.keys() }


    def _get_final_context(self):
        context = self.get_context()

        if self.postprocessors:
            for postprocessor in self.postprocessors:
                extra = {}
                postprocessor(context, extra)
                context.update(extra)

        return context


    @cached_property
    def template_environment(self):
        assert self.directory is not None
        return Environment(
            loader=FileSystemLoader(str(self.directory)),
            undefined=StrictUndefined,
        )


    def render(self, target, highlight=False, context=None):
        if context is None:
            context = self._get_final_context()

        source = self.templates[target]
        template = self.template_environment.get_template(source)
        output = templates.process_template(template, context)

        if highlight:
            output = self.highlight(target, output)

        return output


    def highlight(self, target, content):
        try:
            import pygments.lexers
            from pygments import highlight
            from pygments.formatters import TerminalFormatter
            from pygments.util import ClassNotFound
        except ImportError:
            return content

        try:
            lexer = pygments.lexers.guess_lexer_for_filename(str(target), content)
        except ClassNotFound:
            return content

        output = highlight(content, lexer, TerminalFormatter())
        return output


    def process(self, root):
        context = self._get_final_context()

        for initializer in self.initializers:
            initializer(context)

        for template_target in self.templates.keys():
            output = self.render(template_target, context=context)

            final_target = PyPath(template_target)

            if not final_target.isabs():
                final_target = self.directory.joinpath(final_target)

            if root is not None:
                final_target = PyPath(root) / final_target.relpath('/')

            final_target.dirname().makedirs_p()
            final_target.write_bytes(output.encode('utf-8'))


    def get_result(self, name):
        if name in self._result_context:
            return self._result_context[name]

        value = self._get_result(name)
        self._result_context[name] = value

        return value

    def get_value(self, name):
        return self.get_result(name).output_value


    def _get_result(self, name):

        try:
            argument = self._arguments[name]
        except KeyError:
            raise ImproperlyPassedArguments('argument "%s" is not in service' % name)

        try:
            try:
                value = self.get_raw_value(name)
            except KeyError:
                return argument.get_default_result(self)

            parsed = argument.parse_into_result(value, self)
            return parsed
        except ImproperlyPassedArguments as e:
            raise
            # t, v, tb = sys.exc_info()
            # raise (t, ImproperlyPassedArguments("invalid arguments %s: " % name + e.message), tb)



    def read_from_files(self, environment_variable_name='ENV_FILE'):
        for env_file in os.environ.get('ENV_FILE', '').split(','):
            if env_file:
                self.read_env(env_file)


    def read_env(self, env_file):
        """Read a .env file into Env instance.
        """

        try:
            with open(env_file) if isinstance(env_file, string_types) else env_file as f:
                content = f.read()
        except IOError:
            raise ImproperlyPassedArguments("not reading %s - it doesn't exist." % env_file)

        for line in content.splitlines():
            m1 = re.match(r'\A([A-Za-z_0-9]+)=(.*)\Z', line)
            if m1:
                key, val = m1.group(1), m1.group(2)
                m2 = re.match(r"\A'(.*)'\Z", val)
                if m2:
                    val = m2.group(1)
                m3 = re.match(r'\A"(.*)"\Z', val)
                if m3:
                    val = re.sub(r'\\(.)', r'\1', m3.group(1))
                self._read_values[key] = str(val)


    def get_raw_value(self, name):
        try:
            return os.environ[name]
        except KeyError:
            pass
        return self._read_values[name]


    def explode(self, output):
        for group in self.groups:
            for argument in group.arguments:
                output[argument.name] = self.get_value(argument.name)
            # self.explode_group(group, output)

    @property
    def groups(self):
        return self._groups.values()

