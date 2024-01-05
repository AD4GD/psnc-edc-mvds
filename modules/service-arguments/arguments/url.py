# coding=utf-8
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego service-arguments.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************
from __future__ import absolute_import

from six import with_metaclass
from six.moves import urllib_parse as urlparse
import inspect
import re

from .base import TypeScheme, TypeSchemeMetaclass, empty, Result
from .exceptions import ImproperlyPassedArguments, ImproperlySpecifiedArguments


# return int if possible
def _cast_int(v):
    return int(v) if hasattr(v, 'isdigit') and v.isdigit() else v

def urlencode_transform(value):
    return urlparse.quote_plus(value)


url_transforms = {
    'urlencode': urlencode_transform,
}

def url_transformer(match):
    transform_name = match.group('transform')
    transform = url_transforms[transform_name]
    return transform(match.group('value'))


def better_urlparse(value):
    if not re.match(r'([\w\+]+:)?\/\/', value):
        value = '//' + value

    value = re.sub(r'(?P<transform>\w+)\((?P<value>[^)]+)\)', url_transformer, value)
    return urlparse.urlparse(value)


class Url(TypeScheme):

    def _parse_decoded(self, value, provider):
        return better_urlparse(value)


class GenericUrl(TypeScheme):

    def _parse_decoded(self, value, provider):
        url = better_urlparse(value)
        return {
            'scheme': url.scheme,
            'hostname': url.hostname,
            'port': url.port,
            'username': url.username,
            'password': url.password,
            'path': url.path,
            'query': { k: v[0] for k, v in urlparse.parse_qs(url.query).items() },
        }

COMPONENTS = ('scheme', 'username', 'password', 'hostname', 'port', 'path')

class MatchUrl(TypeScheme):

    def __init__(self, **kwargs):
        self._components = { name: kwargs.pop(name, None) for name in COMPONENTS }
        super(MatchUrl, self).__init__(**kwargs)

    def _parse_decoded(self, value, provider):
        url = better_urlparse(value)
        for name in COMPONENTS:
            component = self._components[name]
            if component is not None:
                if component is empty:
                    if getattr(url, name):
                        raise ImproperlyPassedArguments('%s should be empty in %r' % (name, value))

        return value




class Query(object):

    @classmethod
    def construct(cls, name, scheme):
        if ':' in name:
            input_name, output_path = name.split(':')
        else:
            if '.' in name:
                output_path = name
                input_name = name.split('.')[-1]
            else:
                input_name = name
                output_path = name

        return cls(input_name.lower(), output_path.split('.'), scheme)


    def __init__(self, input_name, output_path, scheme):
        self.input_name = input_name
        self.output_path = output_path
        self.scheme = scheme


class SchemedUrlMetaclass(TypeSchemeMetaclass):


    def __new__(meta, name, bases, attributes):
        attributes['_schemes'] = {}

        aggregated_queries = {}

        attributes['_aggregated_queries'] = aggregated_queries

        for base in bases:
            if hasattr(base, '_aggregated_queries'):
                aggregated_queries.update(base._aggregated_queries)


        if 'QUERY' in attributes:

            for query_name, query_scheme in attributes['QUERY'].items():
                query = Query.construct(query_name, TypeScheme.normalize(query_scheme))
                aggregated_queries[query.input_name] = query




        result = super(SchemedUrlMetaclass, meta).__new__(meta, name, bases, attributes)


        if hasattr(result, 'scheme'):
            for base in inspect.getmro(result):
                if issubclass(base, SchemedUrl):
                    assert result.scheme not in base._schemes
                    base._schemes[result.scheme] = result



        return result


class SchemedUrl(with_metaclass(SchemedUrlMetaclass, TypeScheme)):


    def _get_clean_path(self, url):
        path = url.path
        if path.startswith('/'):
            path = path[1:]
        return path

    def _parse_username(self, url):
        return url.username or ''

    def _parse_password(self, url):
        return url.password or ''

    def _parse_hostname(self, url):
        return url.hostname or ''

    def _parse_port(self, url):
        return _cast_int(url.port) or ''

    def _process_query(self, value, url, config):

        actual_queries = urlparse.parse_qs(url.query)
        actual_queries = { k.lower(): v for k, v in actual_queries.items() }

        for query in self._aggregated_queries.values():

            try:
                query_value = actual_queries.pop(query.input_name)[0]
            except KeyError:
                if not query.scheme.has_default():
                    continue
                parsed_value = query.scheme.get_default()
            else:
                parsed_value = query.scheme.parse(query_value)

            current = config
            for element in query.output_path[:-1]:
                if element not in current:
                    current[element] = {}
                current = current[element]
            current[query.output_path[-1]] = parsed_value

        if actual_queries:
            raise ImproperlyPassedArguments('unknown queries found in %s: %s' % (value, ', '.join(actual_queries.keys())))



    def _prepare_root(self, value, url):
        return {}

    def _parse_scheme(self, value, url):
        config = self._prepare_root(value, url)

        self._process_query(value, url, config)

        self._postprocess(value, url, config)

        if '_SPLIT' in config:
            intermediate_value = dict(config['_SPLIT'])
        else:
            intermediate_value = {}

        # try auto fill intermediate value
        if 'urlparse' not in intermediate_value:
            intermediate_value['urlparse'] = {}

            for attribute_name in ('scheme', 'hostname', 'port', 'username', 'password', 'path'):
                try:
                    intermediate_value['urlparse'][attribute_name] = getattr(url, attribute_name)
                except ValueError:
                    pass

        return Result(output_value=config, intermediate_value=intermediate_value)

    def _postprocess(self, value, url, config):
        pass

    def _parse_decoded(self, value, provider):
        url = better_urlparse(value)
        if not url.scheme and not hasattr(self, 'scheme'):
            raise ImproperlyPassedArguments('no scheme passed and no default set for %s' % value)

        if url.scheme:
            scheme_name = url.scheme
        else:
            assert self.scheme
            scheme_name = self.scheme

        try:
            scheme = self._schemes[scheme_name]
        except KeyError:
            raise ImproperlyPassedArguments('unknown scheme: "%s"' % scheme_name)
        else:
            return scheme()._parse_scheme(value, url)
