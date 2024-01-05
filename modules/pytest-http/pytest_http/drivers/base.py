## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego pytest-http.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************
from bs4 import BeautifulSoup
import contextlib
import json
from cached_property import cached_property
from ..utils import empty
from ..wrapped_property import wrapped_property
import warnings

# INTERNAL_DIVIDER = '-' * 20
INTERNAL_DIVIDER = ''

START_DIVIDER = '=' * 45
MIDDLE_DIVIDER = '-' * 30
END_DIVIDER = '=' * 45


class InvalidStatusException(Exception):
    pass


class CookiesWrapper(object):

    def __init__(self, wrapper):
        self._wrapper = wrapper

    def __getitem__(self, name):
        return self._wrapper._get_cookie(name)

    def __setitem__(self, name, value):
        return self._wrapper._set_cookie(name, value)

    def __detitem__(self, name):
        return self._wrapper._del_cookie(name)

    def __contains__(self, name):
        try:
            self[name]
        except KeyError:
            return False
        else:
            return True


def cut_with_ellipsis(content, length, additional):
    if len(content) <= length:
        return content

    return content[:length] + additional


class EmptyBytesButStillTruthy(bytes):
    # this is a total hack to overcome behaviour of
    # django.test.client.RequestFactory.generic, that on empty data (like:
    # if data:
    # does not put content_type header
    # an alternative approach (and less hacky) would be to explicitly set
    # Content-Type header, but this would require normalizing headers behaviour

    def __bool__(self):
        return True


class BaseResponse(object):

    def __init__(self, response, data):
        self._response = response
        self._data = data


    def __repr__(self):
        return 'HTTPResponse[%s %s -> %s %s]' % (self.method, self.url, self._status, self.reason_phrase)

    @property
    def http_version(self):
        version = self._response.raw.version
        if version == 11:
            return 'HTTP/1.1'
        if version == 10:
            return 'HTTP/1.0'
        raise ValueError('unknown version: %r' % version)

    def _headers_as_lines(self, headers):
        return [ '%s: %s' % (k, v) for k, v in headers.items() ]

    @property
    def method(self):
        return self._request.method

    def _body_as_lines(self, body, content_type):
        if isinstance(body, bytes):
            try:
                body = body.decode()
            except Exception:
                return ['<UNPRINTABLE DATA>']

        nice_body = None

        try:
            if content_type and 'application/json' in content_type:
                nice_body = json.dumps(json.loads(body), indent=2).split('\n')
        except:
            pass

        if nice_body is None:
            nice_body = cut_with_ellipsis(body, 1024, '...').split('\n')

        return cut_with_ellipsis(nice_body, 45, ['...'])


    def _request_data_as_lines(self):
        if self._data is None or self._data is empty:
            return []

        return self._body_as_lines(self._data, None)


    def _response_data_as_lines(self):
        if self.content is None:
            return []

        return [ INTERNAL_DIVIDER ] + self._body_as_lines(self.content, self.headers.get('Content-Type'))


    def request_as_lines(self):
        return [
            '%s %s %s' % (self.method, self.url_path, self.http_version)
        ] + self._headers_as_lines(self._request_headers) + [ INTERNAL_DIVIDER ] + self._request_data_as_lines()


    def as_lines(self):
        return ([ START_DIVIDER ] + self.request_as_lines() + [ MIDDLE_DIVIDER ] + self.response_as_lines() + [ END_DIVIDER ])


    def response_as_lines(self):
        return [
            '%s %s %s' % (self.http_version, self._status, self.reason_phrase)
        ] + self._headers_as_lines(self._response_headers) + self._response_data_as_lines()

    @property
    def assert_repr(self):
        return '\n'.join(self.as_lines())

    __str__ = __repr__

    @cached_property
    def reason_phrase(self):
        return self._response.reason

    @property
    def _status(self):
        return self._response.status_code

    @cached_property
    def status_code(self):
        warnings.warn("status_code is deprecated, use status instead", DeprecationWarning)
        return self._status

    @wrapped_property()
    def status(self):
        return self._status

    @cached_property
    def text(self):
        return self._response.text

    @wrapped_property()
    def headers(self):
        return self._response.headers

    @wrapped_property()
    def request_headers(self):
        return self._request_headers

    @wrapped_property(cached=True)
    def html(self):
        return BeautifulSoup(self.text, 'html.parser')

    @wrapped_property(cached=True)
    def json(self):
        return self._response.json()

    @cached_property
    def _response_headers(self):
        return self._response.headers


class BaseDriver(object):

    response_class = BaseResponse
    print_requests = False

    def __init__(self, **kwargs):

        root_url = kwargs.pop('root_url', None)
        if root_url:
            if 'scheme' in kwargs or 'prefix' in kwargs or 'domain' in 'kwargs':
                raise ValueError('virtual root_url config parameter cannot be specified together with scheme, prefix nor domain')
            import urllib.parse
            parsed_root_url = urllib.parse.urlparse(root_url)
            kwargs['scheme'] = parsed_root_url.scheme
            kwargs['domain'] = parsed_root_url.netloc
            kwargs['prefix'] = parsed_root_url.path.rstrip('/')

        self.config = {
            'domain': kwargs.pop('domain', None),
            'subdomain': kwargs.pop('subdomain', None),
            'origin': kwargs.pop('origin', None),
            'authorization': kwargs.pop('authorization', None),
            'referer': kwargs.pop('referer', None),
            'timeout': kwargs.pop('timeout', None),
            'prefix': kwargs.pop('prefix', ''),
            'scheme': kwargs.pop('scheme', 'http'),
            'verify': kwargs.pop('verify', True),
            'address': kwargs.pop('address', None),
            'headers': kwargs.pop('headers', {}),
            'print_requests': kwargs.pop('print_requests', self.print_requests),
            'verify_status': kwargs.pop('verify_status', False),
            'verify_status_mode': kwargs.pop('verify_status_mode', 'assert'),
            'verbose_exceptions': kwargs.pop('verbose_exceptions', True),
        }
        self._last_response = None
        assert not kwargs, 'unknown kwargs found: %r' % (kwargs.keys())
        # self.default_subdomain = default_subdomain

    @property
    def last(self):
        assert self._last_response is not None
        return self._last_response

    @property
    def cookies(self):
        return CookiesWrapper(self)


    def _transform_data_rules(self, data_argument_name, data_argument_value):

        if data_argument_name == 'json_data':
            # TODO: probably some more explicit encoding should happen here (to be done when needed)
            return json.dumps(data_argument_value).encode(), 'application/json'

        if data_argument_name == 'binary_data':
            assert isinstance(data_argument_value, bytes)
            if not data_argument_value:
                data = EmptyBytesButStillTruthy()
            else:
                data = data_argument_value
            return data, 'application/octet-stream'

        if data_argument_name == 'multipart_data':
            # this code is taken directly from Django
            from django.test.client import encode_multipart

            media_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
            BOUNDARY = 'BoUnDaRyStRiNg'

            if hasattr(data_argument_value, 'items'):
                for key, value in data_argument_value.items():
                    assert not isinstance(value, dict), (
                        "Test data contained a dictionary value for key '%s', "
                        "but multipart uploads do not support nested data. "
                        "You may want to consider using format='json' in this "
                        "test case." % key
                    )

            return encode_multipart(BOUNDARY, data_argument_value), media_type

        if data_argument_name == 'form_data':

            from urllib.parse import urlencode
            assert isinstance(data_argument_value, dict)

            return urlencode(data_argument_value, doseq=True).encode(), 'application/x-www-form-urlencoded'

        raise ValueError('unsupported data_argument_name: %s' % data_argument_name)

    def _transform_data(self, kwargs):
        assert 'data' not in kwargs
        data_arguments_names = set(kwargs.keys()) & {'json_data', 'binary_data', 'form_data', 'multipart_data'}

        assert len(data_arguments_names) <= 1, 'too many _data arguments: %s' % ', '.join(data_arguments_names)

        if data_arguments_names:
            data_argument_name = list(data_arguments_names)[0]
            data_argument_value = kwargs.pop(data_argument_name)

            return self._transform_data_rules(data_argument_name, data_argument_value)
        else:
            return empty, empty

    def _simple_transform(self, name, transformed_kwargs, source_kwargs, default=empty):
        if name in source_kwargs:
            transformed_kwargs[name] = source_kwargs.pop(name)
        else:
            if default is not empty:
                transformed_kwargs[name] = default


    def _execute_request_outer(self, method, path, pass_referrer=False, **kwargs):

        effective_domain = ((self.config['subdomain'] + '.' if self.config['subdomain'] is not None else '') + self.config['domain'])
        headers_to_use = {}
        headers_to_use.update(self.config['headers'])

        if self.config['referer'] is not None:
            headers_to_use['Referer'] = self.config['referer']

        if pass_referrer and self._last_response is not None:
            headers_to_use['Referer'] = self.last._request.url

        if self.config['origin'] is not None:
            headers_to_use['Origin'] = self.config['origin']

        if self.config['authorization'] is not None:
            headers_to_use['Authorization'] = self.config['authorization']

        headers_to_use['Host'] = effective_domain

        if 'headers' in kwargs:
            headers_to_use.update(kwargs.pop('headers'))

        for k, v in kwargs.items():
            assert not k.startswith("HTTP_"), "%s shape of passing headers is not supported, instead use explicite headers argument: headers={ %r: %r }" % (k, k[5:].replace('_', '-').title(), v)

        self._last_response = None
        effective_address = self.config['address'] if self.config['address'] is not None else effective_domain

        url = '%s://%s%s%s' % (self.config['scheme'], effective_address, self.config['prefix'], path)
        self._last_response = self._execute_request(method=method, url=url, verify=self.config['verify'], timeout=self.config['timeout'], allow_redirects=False, headers=headers_to_use, **kwargs)

        if self.config['print_requests']:
            print()
            print('\n'.join(self._last_response.as_lines()))

        if self.config['verify_status']:
            if self.config['verify_status_mode'] == 'assert':
                # assert verify_status_mode is typically used in pytest environment
                assert 200 <= self._last_response.status < 300
            elif self.config['verify_status_mode'] == 'raise':
                # raise verify_status_mode is typically used in non-pytest
                # environment, like locust, etc.
                if not 200 <= self._last_response.status < 300:
                    raise InvalidStatusException('invalid url status: %r' % self._last_response if self.config['verbose_exceptions'] else '%s %s' % (self._last_response._status, self._last_response.reason_phrase))
            else:
                raise ValueError('invalid verify_status_mode: %r' % self.config['verify_status_mode'])

        return self._last_response

    def bind_method(method):

        def wrapped(self, *args, **kwargs):
            return self._execute_request_outer(method, *args, **kwargs)

        wrapped.__name__ = method
        return wrapped

    head = bind_method('head')
    get = bind_method('get')
    post = bind_method('post')
    put = bind_method('put')
    delete = bind_method('delete')
    options = bind_method('options')
    patch = bind_method('patch')
    move = bind_method('move')


    @contextlib.contextmanager
    def switch_config(self, key, value, switcher):
        old_value = self.config.get(key)
        self.config[key] = switcher(value, old_value)
        yield
        self.config[key] = old_value


    def bind_switch_config(name, switcher=(lambda new_value, old_value: new_value)):

        def binder(self, value):
            return self.switch_config(name, value, switcher)

        return binder

    subdomain = bind_switch_config('subdomain')
    scheme = bind_switch_config('scheme')
    origin = bind_switch_config('origin')
    timeout = bind_switch_config('timeout')
    authorization = bind_switch_config('authorization')
    prefix = bind_switch_config('prefix')
    append_prefix = bind_switch_config('prefix', lambda new_value, old_value: old_value + new_value)
    verify_status = bind_switch_config('verify_status')

    def __repr__(self):
        return 'RequestsWrapper({scheme!r}, {subdomain!r}, {prefix!r})'.format(**self.config)
