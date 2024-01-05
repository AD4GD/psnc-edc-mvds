# coding=utf-8
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego service-arguments.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************
from __future__ import absolute_import

from .url import SchemedUrl, urlparse

from .base import Int, Bool, Str, List

class SearchUrl(SchemedUrl):

    QUERY = {
        'EXCLUDED_INDEXES': List(Str()),
        'INCLUDE_SPELLING': Bool,
        'BATCH_SIZE': Int,
    }

    def _prepare_root(self, value, url):
        return {
            'ENGINE': self.engine,
        }


class ElasticSearchUrl(SearchUrl):

    scheme = "elasticsearch"
    engine = "haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine"

    QUERY = {
        'TIMEOUT': Int,
        'KWARGS': Str
    }


    def _prepare_root(self, value, url):
        path = self._get_clean_path(url)
        if path.endswith("/"):
            path = path[:-1]

        split = path.rsplit("/", 1)
        if len(split) > 1:
            path = "/".join(split[:-1])
            index = split[-1]
        else:
            path = ""
            index = split[0]

        return {
            'ENGINE': self.engine,
            'URL': urlparse.urlunparse(('http', url[1], path, '', '', '')),
            'INDEX_NAME': index
        }


class SolrUrl(SearchUrl):

    scheme = "solr"
    engine = "haystack.backends.solr_backend.SolrEngine"

    QUERY = {
        'TIMEOUT': Int,
        'KWARGS': Str,
    }

    def _prepare_root(self, value, url):
        path = self._get_clean_path(url)
        if path.endswith("/"):
            path = path[:-1]

        return {
            'ENGINE': self.engine,
            'URL': urlparse.urlunparse(('http', url[1], path, '', '', '')),
        }


class WhooshUrl(SearchUrl):

    scheme = "whoosh"
    engine = "haystack.backends.whoosh_backend.WhooshEngine"

    QUERY = {
        'STORAGE': Str,
        'POST_LIMIT': Int,
    }

    def _prepare_root(self, value, url):
        return {
            'ENGINE': self.engine,
            'PATH': url.path,
        }


class XapianUrl(SearchUrl):

    scheme = "xapian"
    engine = "haystack.backends.xapian_backend.XapianEngine"

    QUERY = {
        'FLAGS': Str,
    }

    def _prepare_root(self, value, url):
        return {
            'ENGINE': self.engine,
            'PATH': url.path,
        }


class SimpleUrl(SearchUrl):

    scheme = "simple"
    engine = "haystack.backends.simple_backend.SimpleEngine"


class ElasticSearchDslUrl(SchemedUrl):
    scheme = "elasticsearchdsl"

    QUERY = {
        'timeout': Int,
        'use_ssl': Bool,
        'verify_certs': Bool,
    }

    def _prepare_root(self, value, url):
        ret = {
            'hosts': url.hostname,
        }

        if url.port is not None:
            ret['port'] = url.port
        if url.path is not None:
            ret['url_prefix'] = url.path[1:]  # strip first char -- slash
        if url.username is not None:
            ret['url_prefix'] = (url.username, url.passowrd)

        return ret
