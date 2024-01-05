## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego pytest-http.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************

from urllib.parse import urlparse
import requests
from cached_property import cached_property
from . import base
from .base import wrapped_property
from ..utils import empty

class RequestsResponse(base.BaseResponse):

    @cached_property
    def _parsed_url(self):
        return urlparse(self._request.url)

    @property
    def url_path(self):
        return self._parsed_url.path

    @property
    def url(self):
        return self._request.url

    @cached_property
    def content(self):
        return self._response.content

    @property
    def _request(self):
        return self._response.request

    @cached_property
    def _request_headers(self):
        return self._request.headers


class RequestsDriver(base.BaseDriver):

    response_class = RequestsResponse

    def __init__(self, **kwargs):
        self.session = requests.Session()
        super(RequestsDriver, self).__init__(**kwargs)

    def _execute_request(self, method, url, **kwargs):
        transformed_kwargs = {}

        transformed_data, default_content_type = self._transform_data(kwargs)

        self._simple_transform('verify', transformed_kwargs, kwargs)
        self._simple_transform('allow_redirects', transformed_kwargs, kwargs)
        # self._simple_transform('content_type', transformed_kwargs, kwargs, default=default_content_type)
        self._simple_transform('headers', transformed_kwargs, kwargs)
        self._simple_transform('timeout', transformed_kwargs, kwargs)

        content_type = kwargs.pop('content_type', default_content_type)
        if content_type is not empty:
            transformed_kwargs['headers']['Content-Type'] = content_type

        if transformed_data is not empty:
            transformed_kwargs['data'] = transformed_data


        if kwargs:
            raise ValueError('not transformed kwargs: %r' % kwargs)
        _response = self.session.request(method, url, **transformed_kwargs)
        return self.response_class(_response, data=transformed_data)

    def _get_cookie(self, name):
        return self.session.cookies[name]

    def _set_cookie(self, name, value):
        self.session.cookies[name] = value

    def _del_cookie(self, name):
        del self.session.cookies[name]
