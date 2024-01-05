# coding=utf-8
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego service-arguments.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************
from __future__ import absolute_import

from .url import SchemedUrl

class EmailUrl(SchemedUrl):


    def _prepare_root(self, value, url):
        return {
            'EMAIL_BACKEND': self.backend,
            'EMAIL_FILE_PATH': self._get_clean_path(url), # TODO: is it always needed?
            'EMAIL_HOST_USER': self._parse_username(url),
            'EMAIL_HOST_PASSWORD': self._parse_password(url),
            'EMAIL_HOST': self._parse_hostname(url),
            'EMAIL_PORT': self._parse_port(url),
        }


class SmtpUrl(EmailUrl):
    scheme = 'smtp'
    backend = 'django.core.mail.backends.smtp.EmailBackend'

class SmtpsUrl(EmailUrl):
    scheme = 'smtps'
    backend = 'django.core.mail.backends.smtp.EmailBackend'

    def _postprocess(self, value, url, config):
        config['EMAIL_USE_TLS'] = True


class SmtpTLSUrl(EmailUrl):
    scheme = 'smtp+tls'
    backend = 'django.core.mail.backends.smtp.EmailBackend'

    def _postprocess(self, value, url, config):
        config['EMAIL_USE_TLS'] = True

class SmtpSSLUrl(EmailUrl):
    scheme = 'smtp+ssl'
    backend = 'django.core.mail.backends.smtp.EmailBackend'

    def _postprocess(self, value, url, config):
        config['EMAIL_USE_SSL'] = True

class ConsoleMailUrl(EmailUrl):
    scheme = 'consolemail'
    backend = 'django.core.mail.backends.console.EmailBackend'

class FileMailUrl(EmailUrl):
    scheme = 'filemail'
    backend = 'django.core.mail.backends.filebased.EmailBackend'

class MemoryMailUrl(EmailUrl):
    scheme = 'memorymail'
    backend = 'django.core.mail.backends.locmem.EmailBackend'

class DummyMailUrl(EmailUrl):
    scheme = 'dummymail'
    backend = 'django.core.mail.backends.dummy.EmailBackend'

