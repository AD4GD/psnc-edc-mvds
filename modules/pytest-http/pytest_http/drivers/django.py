## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego pytest-http.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************
from cached_property import cached_property
from django.utils.encoding import force_bytes
from django.conf import settings
from . import base
from .base import wrapped_property
from ..utils import empty
import warnings

class DjangoResponse(base.BaseResponse):

    @property
    def _request(self):
        return self._response.request

    @cached_property
    def http_version(self):
        return 'HTTP/django'

    @cached_property
    def method(self):
        # print(repr(self.request))
        return self._request['REQUEST_METHOD'].upper()

    @cached_property
    def url_path(self):
        return self._request['PATH_INFO']

    @property
    def url(self):
        # TODO: add host here
        return self._request['PATH_INFO']

    @cached_property
    def _request_headers(self):
        return { k[5:].replace('_', '-').title(): v for k, v in self._request.items() if k.startswith('HTTP_') }

    @cached_property
    def _response_headers(self):
        return self._response

    @cached_property
    def reason_phrase(self):
        return self._response.reason_phrase

    @property
    def _status(self):
        return self._response.status_code

    @cached_property
    def content(self):
        return self._response.content

    @wrapped_property(cached=True)
    def headers(self):
        return self._response

    @wrapped_property(cached=True)
    def text(self):
        return self.content.decode()



class DjangoDriver(base.BaseDriver):

    response_class = DjangoResponse

    def __init__(self, client, domain=None, **kwargs):
        self.client = client
        if domain is None:
            domain = settings.ALLOWED_HOSTS[0]
        super(DjangoDriver, self).__init__(domain=domain, **kwargs)


    def _execute_request(self, method, url, verify, **kwargs):

        transformed_kwargs = {}

        transformed_data, default_content_type = self._transform_data(kwargs)

        content_type = kwargs.pop('content_type', default_content_type)

        if content_type is not empty:
            transformed_kwargs['content_type'] = content_type

        if transformed_data is not empty:
            transformed_kwargs['data'] = transformed_data

        headers = kwargs.pop('headers')

        timeout = kwargs.pop('timeout', None)
        if timeout is not None:
            warnings.warn('timeout config parameter is not available for the django backend')


        for k, v in headers.items():
            transformed_kwargs['HTTP_%s' % k.replace('-', '_').upper()] = str(v)

        allow_redirects = kwargs.pop('allow_redirects', False)
        if allow_redirects:
            raise NotImplementedError('following redirections is not yet supported in django test wrapper')

        if 'format' in kwargs:
            transformed_kwargs['format'] = kwargs.pop('format')

        if kwargs:
            raise ValueError('not transformed kwargs: %r' % kwargs)

        # TODO: those headers are passed here only to be available during
        # rendering request representation - it should be removed
        _response = getattr(self.client, method)(path=url, headers=headers, **transformed_kwargs)
        return self.response_class(_response, data=transformed_data)


    def _get_cookie(self, name):
        return self.client.cookies[name]

    def _set_cookie(self, name, value):
        self.client.cookies[name] = value

    def _del_cookie(self, name):
        del self.client.cookies[name]



class DRFApiClientAdditionsMixin(object):

    def _encode_data(self, data, format=None, content_type=None):
        """
        Encode the data returning a two tuple of (bytes, content_type)
        """
        # only format=None is supported, but format is a part of original method
        # interface
        assert format is None

        if data is None:
            # if data is empty, then the content_type is not used, so even
            # None should not surface
            return ('', content_type)

        assert content_type is not None
        return force_bytes(data, settings.DEFAULT_CHARSET), content_type


class DjangoClientAdditionsMixin(object):

    def move(self, path, data=None, format=None, content_type=None,
             follow=False, **extra):
        data, content_type = self._encode_data(data, format, content_type)
        response = self.generic('MOVE', path, data, content_type, **extra)
        if follow:
            response = self._handle_redirects(response, **extra)
        return response


    def request(self, **kwargs):
        if 'HTTP_COOKIE' not in kwargs:
            cookie_header_value = self.cookies.output(header='', sep='; ')
            if cookie_header_value:
                kwargs['HTTP_COOKIE'] = cookie_header_value
        return super().request(**kwargs)
