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

class DatabaseUrl(SchemedUrl):

    QUERY = {
        'CONN_MAX_AGE': Int,
        'ATOMIC_REQUESTS': Bool,
        'AUTOCOMMIT': Bool,
    }


    def _parse_name(self, url):
        return self._get_clean_path(url)

    def _prepare_root(self, value, url):
        return {
            'ENGINE': self.engine,
            'NAME': self._parse_name(url),
            'USER': self._parse_username(url),
            'PASSWORD': self._parse_password(url),
            'HOST': self._parse_hostname(url),
            'PORT': self._parse_port(url),
        }




class OracleUrl(DatabaseUrl):
    scheme = 'oracle'
    engine = 'django.db.backends.oracle'

    QUERY = {
        'OPTIONS.timeout': Int,
        'pool_min:POOL.min': Int,
        'pool_max:POOL.max': Int,
        'pool_increment:POOL.increment': Int,
        'pool_timeout:POOL.timeout': Int,
    }

    def _parse_name(self, url):
        if self._get_clean_path(url) == '':
            return url.hostname
        return super(OracleUrl, self)._parse_name(url)

    def _parse_hostname(self, url):
        if url.path == '/':
            return ''
        else:
            return url.hostname

    def _parse_port(self, url):
        return str(super(OracleUrl, self)._parse_port(url))

    def _postprocess(self, value, url, config):
        if not config['PORT']:
            del(config['PORT']) # Django oracle/base.py strips port and fails on None


class PostgresUrl(DatabaseUrl):
    scheme = 'postgres'
    engine = 'django.db.backends.postgresql_psycopg2'

class PostgreSQLUrl(PostgresUrl):
    scheme = 'postgresql'

class PSQLUrl(PostgresUrl):
    scheme = 'psql'

class PGSQLUrl(PostgresUrl):
    scheme = 'pgsql'

class PostGISUrl(PostgresUrl):
    scheme = 'postgis'
    engine = 'django.contrib.gis.db.backends.postgis'

class MySQLUrl(DatabaseUrl):
    QUERY = {
        'OPTIONS.reconnect': Bool,
        'OPTIONS.init_command': Str,
    }

    scheme = 'mysql'
    engine = 'django.db.backends.mysql'

class MySQL2Url(MySQLUrl):
    scheme = 'mysql2'

class MySQLGISUrl(MySQLUrl):
    scheme = 'mysqlgis'
    engine = 'django.contrib.gis.db.backends.mysql'

class SpatialiteUrl(DatabaseUrl):
    scheme = 'spatialite'
    engine = 'django.contrib.gis.db.backends.spatialite'

class SqliteUrl(DatabaseUrl):
    scheme = 'sqlite'
    engine = 'django.db.backends.sqlite3'

    def _parse_name(self, url):
        if self._get_clean_path(url) == '':
            return ':memory:'
        return super(SqliteUrl, self)._parse_name(url)

    def _parse_scheme(self, value, url):
        if value == 'sqlite://:memory:':
            # this is a special case, because if we pass this URL into
            # urlparse, urlparse will choke trying to interpret "memory"
            # as a port number
            return {
                'ENGINE': self.engine,
                'NAME': ':memory:'
            }

        return super(SqliteUrl, self)._parse_scheme(value, url)


class LdapUrl(DatabaseUrl):

    scheme = 'ldap'
    engine = 'ldapdb.backends.ldap'

    def _parse_name(self, url):
        path = '{scheme}://{hostname}'.format(scheme=url.scheme, hostname=url.hostname)
        if url.port:
            path += ':{port}'.format(port=url.port)
        return path


class CassandraUrl(DatabaseUrl):

    QUERY = {
        'replication:OPTIONS.replication.replication_factor': Int(3),
        'timeout:OPTIONS.session.default_timeout': Int,
        'fetch_size:OPTIONS.session.default_fetch_size': Int,
        'lazy:OPTIONS.connection.lazy_connect': Bool,
        'retry:OPTIONS.connection.retry_connect': Bool,
    }

    scheme = 'cassandra'
    engine = 'django_cassandra_engine'
