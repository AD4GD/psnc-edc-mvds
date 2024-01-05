# coding=utf-8
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego service-arguments.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************
from . import types
from .base import TypeSchemeMetaclass
from six import exec_
from arguments.base import PyPath
from .utils import append_to_dict
from .group import Group
from .service import Service

class LegacyContextBuilder(object):

    def __init__(self, service):
        self.service = service
        self._groups = []
        self._filters = {}
        self._templates = {}


    def groups(self, *groups):
        for group in groups:
            self.service.add_group(group)

    def filter(self, template_filter):
        self._filters[template_filter.__name__] = template_filter

    def templates(self, templates_dict):
        self._templates.update(templates_dict)

    def postprocess(self, postprocess_function):
        self.service.postprocessors.append(postprocess_function)

    def initializer(self, initializer_function):
        self.service.initializers.append(initializer_function)

    def glob_templates(self, output_directory, pattern):
        assert self.service.directory is not None
        output_directory = PyPath(output_directory)
        for child in self.service.directory.glob(pattern):
            child = child.relpath(self.service.directory)
            self._templates[str(output_directory / child)] = str(child)


class Context(object):

    def _add_service(self, service):
        self._services.append(service)
        for template_target in service.templates.keys():
            append_to_dict(self._target_services, template_target, service, 'template')


    def _try_add_directory(self, directory):
        if directory.joinpath('context.py').exists():
            service = Service(directory)
            builder = LegacyContextBuilder(service)

            exec_locals = {
                'Group': Group,
                'context': builder,
            }
            TypeSchemeMetaclass.explode_registry(exec_locals)

            code = (directory / 'context.py').text(encoding='utf-8')
            exec_(code, exec_locals)

            service.templates = builder._templates
            service.template_environment.filters.update(builder._filters)

            self._add_service(service)

            return True


        if directory.joinpath('service.py').exists():
            assert 0
            # self._add_service(service)
            return True


        return False




    def __init__(self, directories):
        self._services = []
        self._target_services = {}

        for directory in directories:
            directory = PyPath(directory)
            if not self._try_add_directory(directory):
                for child in directory.dirs():
                    self._try_add_directory(child)

        # TODO: check conflicts between output paths

    def render(self, target, highlight=False):
        return self._target_services[target].render(target, highlight=highlight)


    def process(self, root=None):
        for service in self._services:
            service.process(root)



