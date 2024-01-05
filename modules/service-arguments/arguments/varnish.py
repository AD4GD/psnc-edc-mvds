# coding=utf-8
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego service-arguments.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************
from __future__ import absolute_import
import ipaddress

from .url import SchemedUrl
from .exceptions import ImproperlySpecifiedArguments, ImproperlyPassedArguments
from .base import Int


class VarnishBackend(SchemedUrl):

    scheme = 'varnishbackend'

    QUERY = {
        'MAX_CONNECTIONS': Int,
    }

    def _prepare_root(self, value, url):
        split = {
            'HOST': self._parse_hostname(url),
            'PORT': self._parse_port(url),
            'PATH': self._parse_path(url)
        }

        return {
            '_SPLIT': split,
        }

    def _parse_hostname(self, url):
        hostname = super(VarnishBackend, self)._parse_hostname(url)
        try:
            ipaddress.ip_address(unicode(hostname))
        except ValueError:
            raise ImproperlySpecifiedArguments('Varnish backend url hostname should be valid ip address')

        return hostname

    def _parse_path(self, url):
        if url.path:
            raise ImproperlyPassedArguments('Varnish backend url path should be empty')
        return url.path
