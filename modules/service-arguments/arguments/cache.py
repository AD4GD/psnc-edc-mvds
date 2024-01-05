# coding=utf-8
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego service-arguments.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************
from __future__ import absolute_import

from .url import SchemedUrl
from .base import Int, Str, Bool

# back compatibility with redis_cache package
DJANGO_REDIS_DRIVER = 'django_redis.cache.RedisCache'
DJANGO_REDIS_CACHE_DRIVER = 'redis_cache.RedisCache'

REDIS_DRIVER = DJANGO_REDIS_DRIVER
try:
    import redis_cache
    REDIS_DRIVER = DJANGO_REDIS_CACHE_DRIVER
except:
    pass

class CacheUrl(SchemedUrl):

    QUERY = {
        'TIMEOUT': Int,
        'KEY_PREFIX': Str,
        'VERSION': Str,
        'KEY_FUNCTION': Str,
        'BINARY': Bool,
    }


    def _get_first_location(self, value, url):
        location = url.netloc.split(',')
        if len(location) == 1:
            location = location[0]
        return location


    def _parse_location(self, value, url):
        return self._get_first_location(value, url)


    def _prepare_root(self, value, url):
        return {
            'BACKEND': self.backend,
            'LOCATION': self._parse_location(value, url),
        }



class DBCacheUrl(CacheUrl):
    scheme = 'dbcache'
    backend = 'django.core.cache.backends.db.DatabaseCache'

class DummyCacheUrl(CacheUrl):
    scheme = 'dummycache'
    backend = 'django.core.cache.backends.dummy.DummyCache'

class FileCacheUrl(CacheUrl):
    QUERY = {
        'OPTIONS.MAX_ENTRIES': Int,
        'OPTIONS.CULL_FREQUENCY': Int,
    }

    scheme = 'filecache'
    backend = 'django.core.cache.backends.filebased.FileBasedCache'

    def _parse_location(self, value, url):
        return url.netloc + url.path

class LocMemCacheUrl(CacheUrl):
    scheme = 'locmemcache'
    backend = 'django.core.cache.backends.locmem.LocMemCache'

class MemcacheUrl(CacheUrl):
    scheme = 'memcache'
    backend = 'django.core.cache.backends.memcached.MemcachedCache'

    def _parse_location(self, value, url):
        if url.path:
            return 'unix:' + url.path
        else:
            return super(MemcacheUrl, self)._parse_location(value, url)

class PyMemcacheUrl(MemcacheUrl):
    scheme = 'pymemcache'
    backend = 'django.core.cache.backends.memcached.PyLibMCCache'

class RedisCacheUrl(CacheUrl):
    QUERY = {
        'OPTIONS.DB': Int,
        'OPTIONS.PASSWORD': Str,
        'OPTIONS.CLIENT_CLASS': Str,
    }

    scheme = 'rediscache'
    backend = REDIS_DRIVER

    def _parse_location(self, value, url):
        if url.hostname:
            scheme = url.scheme.replace('cache', '')
        else:
            scheme = 'unix'

        return scheme + '://' + url.netloc + url.path

class RedisUrl(RedisCacheUrl):
    scheme = 'redis'
    backend = REDIS_DRIVER
