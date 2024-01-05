# coding=utf-8
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego service-arguments.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************
from __future__ import absolute_import

from .url import SchemedUrl

from .base import Int, Bool, Str

import re

from six.moves import urllib_parse as urlparse

class CeleryUrl(SchemedUrl):

    scheme = 'celery'



class CeleryRabbitMQUrl(CeleryUrl):

    scheme = 'celery+rabbitmq'

    QUERY = {
        'CELERY_TASK_DEFAULT_EXCHANGE': Str,
    }

    def _prepare_root(self, value, url):
        path = self._get_clean_path(url)
        try:
            vhost, default_queue_name = path.split('/')
        except ValueError:
            raise ValueError('invalid path component: %r' % path)

        return {
            'CELERY_BROKER_URL': 'amqp://{user}:{password}@{host}:{port}/{vhost}'.format(
                user=self._parse_username(url),
                password=self._parse_password(url),
                host=self._parse_hostname(url),
                port=self._parse_port(url),
                vhost=vhost,
            ),
            'CELERY_TASK_DEFAULT_QUEUE': default_queue_name,
            'CELERY_BROKER_TRANSPORT_OPTIONS': {},
        }


class CelerySQSUrl(CeleryUrl):

    scheme = 'celery+sqs'

    QUERY = {
        'CELERY_TASK_DEFAULT_EXCHANGE': Str,
    }

    def _prepare_root(self, value, url):
        path = self._get_clean_path(url)
        try:
            account_id, default_queue_name = path.split('/')
        except ValueError:
            raise ValueError('invalid path component: %r' % path)

        transport_options = {}

        host = self._parse_hostname(url)
        matched_region = re.match(r'sqs\.(?P<region>[^\.]+)\.amazonaws\.com', host)
        if matched_region:
            transport_options['region'] = matched_region.group('region')

        return {
            'CELERY_BROKER_URL': 'sqs://{access_key_id}:{secret_access_key}@'.format(
                access_key_id=self._parse_username(url),
                secret_access_key=self._parse_password(url),
            ),
            'CELERY_TASK_DEFAULT_QUEUE': default_queue_name,
            'CELERY_BROKER_TRANSPORT_OPTIONS': transport_options,
        }

def quote_or_none(value):
    if not value:
        return ''
    return urlparse.quote_plus(value)

def transform_celery_settings(source, prefix, target_prefix='CELERY'):
    try:
        transport = source[prefix + '_TRANSPORT']
        user = source[prefix + '_USER']
        password = source[prefix + '_PASS']
        host = source[prefix + '_HOST']
        port = source[prefix + '_PORT']
        vhost = source[prefix + '_VHOST']
        queue = source[prefix + '_QUEUE']
    except KeyError as e:
        raise ValueError('undefined parameter: %s' % e)

    if transport in {'amqp', 'amqps'}:
        return {
            (target_prefix + '_BROKER_URL'): '{transport}://{user}:{password}@{host}:{port}/{vhost}'.format(
                transport=transport.strip() if transport else None,
                user=quote_or_none(user.strip() if user else None),
                password=quote_or_none(password.strip() if password else None),
                host=host.strip() if host else None,
                port=port,
                vhost=vhost.strip() if vhost else None,
            ),
            (target_prefix + '_TASK_DEFAULT_QUEUE'): queue.strip(),
            (target_prefix + '_BROKER_TRANSPORT_OPTIONS'): {},
        }

    if transport == 'sqs':
        # vhost is account_id

        transport_options = {}

        matched_region = re.match(r'sqs\.(?P<region>[^\.]+)\.amazonaws\.com', host)
        if matched_region:
            transport_options['region'] = matched_region.group('region')

        return {
            (target_prefix + '_BROKER_URL'): 'sqs://{access_key_id}:{secret_access_key}@'.format(
                access_key_id=quote_or_none(user),
                secret_access_key=quote_or_none(password),
            ),
            (target_prefix + '_TASK_DEFAULT_QUEUE'): queue,
            (target_prefix + '_BROKER_TRANSPORT_OPTIONS'): transport_options,
        }

    raise ValueError('uknonwn transport: %s' % transport)


