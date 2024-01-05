# coding=utf-8
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego service-arguments.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************
from __future__ import absolute_import

from .base import TypeScheme, TypeSchemeMetaclass, empty, Ref, Bool
from .url import better_urlparse
from contextlib import closing

from .exceptions import ImproperlyPassedArguments

class WaitForPort(Bool):

    def __init__(self, hostname, timeout=30, **kwargs):
        super(WaitForPort, self).__init__(**kwargs)
        self._hostname_provider = Ref(hostname)
        self._timeout = timeout

    def _extract_simple_value(self, result, names):
        for name in names:
            if name in result.output_value:
                return result.output_value[name]

        if result.intermediate_value is not None:
            for name in names:
                try:
                    return result.intermediate_value['urlparse'][name]
                except KeyError:
                    pass

        raise ImproperlyPassedArguments('resulting %s does have any field looking like: %r' % (result, names))



    def _extract_hostname_and_port(self, provider):
        assert provider is not None
        result_hostname = provider.get_result(self._hostname_provider.name)
        return (self._extract_simple_value(result_hostname, ('host', 'HOST', 'hostname', 'HOSTNAME')), self._extract_simple_value(result_hostname, ('port', 'PORT')))


    def _parse_decoded(self, value, provider):
        result = super(WaitForPort, self)._parse_decoded(value, provider)

        if result:
            hostname, port = self._extract_hostname_and_port(provider)
            wait_for_port(hostname, port, True, self._timeout)

        return result


def wait_for_port(hostname, port, enabled, timeout):
    import socket
    import time
    if not enabled:
        return

    threshold = time.time() + timeout
    error = None

    while time.time() < threshold:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as connection:
            connection.settimeout(1)
            try:
                connection.connect((hostname, int(port)))
            except socket.error:
                time.sleep(0.1)
            else:
                break
    else:
        raise ImproperlyPassedArguments('failed to wait for %s:%s' % (hostname, port))




