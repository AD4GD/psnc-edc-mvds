# coding=utf-8
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego service-arguments.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************
from __future__ import print_function
import json
import os
import sys
import unittest
import pytest

from arguments.exceptions import ImproperlySpecifiedArguments, ImproperlyPassedArguments

from arguments import Group, Context, Service
from arguments.cache import REDIS_DRIVER
from arguments.base import PyPath
from arguments.types import *
from arguments import process
from arguments import templates


@pytest.fixture(scope='function')
def empty_environ(request):
    old_environ = os.environ
    os.environ = {}
    yield None
    os.environ = old_environ


def test_database_url_classes():
    assert 'oracle' in DatabaseUrl._schemes


def group_as_service(group):
    service = Service()
    service.add_group(group)
    return service


class ParserTest(object):

    def test_general_setup(empty_environ):

        class Main(Group):
            STR_VAR = 'value'
            INT_VAR = 1
            BOOL_VAR = True

        group_as_service(Main).explode(globals())

        assert STR_VAR == 'value'
        assert INT_VAR == 1
        assert BOOL_VAR == True


    # def test_not_present_without_default(self):
    #     parser = Parser()
    #     with pytest.raises(ImproperlyPassedArguments):
    #         parser.get_value('not_present')

    def test_str(self):
        STR_VAR = 'bar'
        assert 'bar' == TypeScheme.normalize_and_parse('string-value', STR_VAR)
        assert 'bar' == TypeScheme.normalize_and_parse(str, STR_VAR)


    def test_int_with_none_default(self):

        class Main(Group):
            NOT_PRESENT_VAR = Int(None)

        assert group_as_service(Main).get_value('NOT_PRESENT_VAR') is None
        # assert parser.NOT_PRESENT_VAR is None

    def test_float(self):
        assert 33.3 == TypeScheme.normalize_and_parse(float, "33.3")
        assert 12.0 == TypeScheme.normalize_and_parse(float, "12")


    def test_bool(self):

        assert True == Bool().parse('1')
        assert True == Bool().parse('True')
        assert True == Bool().parse('true')
        assert True == Bool().parse('yes')
        assert True == Bool().parse('on')
        assert True == Bool().parse('ok')
        assert True == Bool().parse('y')

        assert False == Bool().parse('0')
        assert False == Bool().parse('False')
        assert False == Bool().parse('false')
        assert False == Bool().parse('no')
        assert False == Bool().parse('off')
        assert False == Bool().parse('n')


    def test_proxied_value(self, empty_environ):

        class Main(Group):
            STR_VAR = 'STR'
            PROXIED_VAR = Str(default=Ref('STR_VAR'))

        os.environ.update(
            STR_VAR='bar',
        )
        assert 'bar' == group_as_service(Main).context.PROXIED_VAR


    def test_int_list(self):
        assert [42, 33] == TypeScheme.normalize_and_parse([int], '42,33')

    def test_variadic_tuple(self):
        variadic = TypeScheme.normalize(("some-string", 1, 2))
        assert ("some-string", 1, 2) == variadic.get_default()
        assert ("other-string", 4, 5) == variadic.parse("other-string,4,5")

        with pytest.raises(ImproperlyPassedArguments):
            variadic.parse("other-string,not-a-number,5")

        assert ("some-pattern-{:03}", 4, 5) == variadic.parse("some-pattern-{:03},4,5")

    def test_int_tuple(self):
        resolution = TypeScheme.normalize((640, 480))
        assert (640, 480) == resolution.get_default()
        assert (123, 456) == resolution.parse('123,456')

        with pytest.raises(ImproperlyPassedArguments):
            resolution.parse('1280')
        with pytest.raises(ImproperlyPassedArguments):
            resolution.parse('1280,920,12')
        with pytest.raises(ImproperlyPassedArguments):
            resolution.parse('1280,a')

    def test_str_list_with_spaces(self):
        assert [' foo', '  bar'] == TypeScheme.normalize_and_parse([str], ' foo,  bar')

    def test_empty_list(self):
        assert [] == TypeScheme.normalize_and_parse([], '')

    def test_dict_value(self):
        assert Dict().parse('a:1,b:2,c:3') == { 'a': '1', 'b': '2', 'c': '3' }
        assert Dict(value=Int).parse('a:1,b:2,c:3') == { 'a': 1, 'b': 2, 'c': 3 }
        assert Dict(key=Int).parse('1:a,2:b,3:c') == { 1: 'a', 2: 'b', 3: 'c' }

        url_dict = Dict(value=GenericUrl).parse('some:127.0.0.1:8080,other:127.0.0.2')
        assert url_dict['some']['hostname'] == '127.0.0.1'
        assert url_dict['some']['port'] == 8080
        assert url_dict['other']['hostname'] == '127.0.0.2'
        assert url_dict['other']['port'] == None

        with pytest.raises(ImproperlyPassedArguments):
            assert Dict(value=Int).parse('a:not-an-integer')



    def test_url_value(self):
        URL = 'http://www.google.com/'
        url = Url().parse(URL)

        # assert url.__class__ == URL_CLASS
        assert url.geturl() == URL

    def test_generic_url(self):
        only_host = GenericUrl().parse('10.0.0.1')
        assert only_host['hostname'] == '10.0.0.1'

        host_port = GenericUrl().parse('10.0.0.1:8000')
        assert host_port['hostname'] == '10.0.0.1'
        assert host_port['port'] == 8000

        query_port = GenericUrl().parse('10.0.0.1?attribute=value')
        assert query_port['hostname'] == '10.0.0.1'
        assert query_port['query']['attribute'] == 'value'

    def test_generic_url_lists(self, empty_environ):
        class Main(Group):
            URL_LIST = [GenericUrl]
            SINGLE_DEFAULT_URL_LIST = [GenericUrl('127.0.0.1')]
            CLEARED_URL_LIST = [GenericUrl('127.0.0.1')]

        os.environ['CLEARED_URL_LIST'] = ''
        context = group_as_service(Main).context

        assert len(context.URL_LIST) == 0
        assert len(context.SINGLE_DEFAULT_URL_LIST) == 1
        assert context.SINGLE_DEFAULT_URL_LIST[0]['hostname'] == '127.0.0.1'
        assert len(context.CLEARED_URL_LIST) == 0
        assert not context.CLEARED_URL_LIST




    def test_json_value(empty_environ):
        JSON_VALUE = {
            'one': 'bar',
            'two': 2,
            'three': 33.44
        }

        class Main(Group):
            JSON_VAR = Json

        os.environ['JSON_VAR'] = json.dumps(JSON_VALUE)

        assert JSON_VALUE == group_as_service(Main).context.JSON_VAR


    def test_path(self):
        PATH_VALUE = '/home/dev'
        assert PyPath(PATH_VALUE) == Path().parse(PATH_VALUE)

    def test_default_schema(self):
        with pytest.raises(ImproperlyPassedArguments):
            DatabaseUrl('oracle://oracle:1521/db').parse('oracle:1521')

        assert 'other-oracle' == OracleUrl('oracle://oracle:1521/db').parse('//other-oracle:1521')['HOST']
        assert 'some-oracle' == OracleUrl().parse('//some-oracle:1521')['HOST']

        assert 'other-oracle' == OracleUrl('oracle://oracle:1521/db').parse('other-oracle:1521')['HOST']
        assert 'some-oracle' == OracleUrl().parse('some-oracle:1521')['HOST']


class CustomDatabaseUrl(DatabaseUrl):
    QUERY = {
        'empty_factor:OPTIONS.empty_factor': Int,
        'default_factor:OPTIONS.nested.default_factor': Int(2),
    }

    scheme = 'custom'
    engine = 'just.custom'



class AdvancedSchemesTests(object):

    def test_nested_options(self):
        custom_url = CustomDatabaseUrl().parse('custom://host:password@host:1234/db?default_factor=3')
        assert custom_url['OPTIONS']['nested']['default_factor'] == 3
        assert 'empty_factor' not in custom_url['OPTIONS']

        other_custom_url = CustomDatabaseUrl().parse('custom://host:password@host:1234/db?empty_factor=4')
        assert other_custom_url['OPTIONS']['nested']['default_factor'] == 2
        assert other_custom_url['OPTIONS']['empty_factor'] == 4

    # def test_lambda_defaults(self):
    #     parser = Parser(
    #         ORIGINAL=True,
    #         DERIVED=Bool(Not('ORIGINAL')),
    #     )

    #     assert parser.DERIVED == False

    #     os.environ['ORIGINAL'] = 'False'
    #     parser.resest()

    #     assert parser.DERIVED == True



class ParserUtilitiesTests(object):


    def test_result_access(self):

        class Other(Group):
            STR = 'strvalue'
            BOOL = True
            SQL = DatabaseUrl('oracle://user:pass@host:1234/database?timeout=1')
            EMPTY = Str(default=None)
            EMPTY_LIST = []

        service = group_as_service(Other)
        context = service.context

        assert 'strvalue' == context.STR
        assert True == context.BOOL
        assert None == context.EMPTY
        assert [] == context.EMPTY_LIST

        service.explode(globals())
        assert 'strvalue' == STR
        assert True == BOOL

        assert 'user' == SQL['USER']
        assert 1 == SQL['OPTIONS']['timeout']

    def test_groups(self):

        class TestService(Service):

            class Main(Group):

                MAIN_STR = 'str'

            class Misc(Group):

                MISC_INT = 1

        service = TestService()

        assert len(service.groups) == 2

        service.explode(globals())
        assert MAIN_STR == 'str'
        assert MISC_INT == 1







class SchemaParserTests(object):

    def test_schema(self, empty_environ):
        # TODO
        class Main(Group):
            INT_VAR = int
            NOT_PRESENT_VAR = float(33.3)
            STR_VAR = str
            NON_DEFAULT_INT_LIST = [Int]
            DEFAULT_MULTIPLE_STR_LIST = ['x', 'y', 'z']

        context = group_as_service(Main).context

        os.environ.update(
            INT_VAR='42',
            STR_VAR='bar',
            INT_LIST='42,33',
            NON_DEFAULT_INT_LIST='1,2'
        )

        assert 42 == context.INT_VAR
        assert 33.3 == context.NOT_PRESENT_VAR

        assert 'bar' == context.STR_VAR
        assert [1, 2] == context.NON_DEFAULT_INT_LIST
        assert ['x', 'y', 'z'] == context.DEFAULT_MULTIPLE_STR_LIST

        # assert [42, 33] == parser.INT_LIST
        # assert [2] == parser.DEFAULT_LIST



class DatabaseTestSuite(unittest.TestCase):


    def test_postgres_parsing(self):
        pg_config = DatabaseUrl().parse('postgres://uf07k1:wegauwhg@ec2-107-21-253-135.compute-1.amazonaws.com:5431/d8r82722')
        assert pg_config['ENGINE'] == 'django.db.backends.postgresql_psycopg2'
        assert pg_config['NAME'] == 'd8r82722'
        assert pg_config['HOST'] == 'ec2-107-21-253-135.compute-1.amazonaws.com'
        assert pg_config['USER'] == 'uf07k1'
        assert pg_config['PASSWORD'] == 'wegauwhg'
        assert pg_config['PORT'] == 5431

    def test_postgis_parsing(self):
        url = DatabaseUrl().parse('postgis://uf07k1i6d8ia0v:wegauwhgeuioweg@ec2-107-21-253-135.compute-1.amazonaws.com:5431/d8r82722r2kuvn')
        assert url['ENGINE'] == 'django.contrib.gis.db.backends.postgis'
        assert url['NAME'] == 'd8r82722r2kuvn'
        assert url['HOST'] == 'ec2-107-21-253-135.compute-1.amazonaws.com'
        assert url['USER'] == 'uf07k1i6d8ia0v'
        assert url['PASSWORD'] == 'wegauwhgeuioweg'
        assert url['PORT'] == 5431

    def test_mysql_parsing(self):
        mysql_config = DatabaseUrl().parse('mysql://bea6eb0:69772142@us-cdbr-east.cleardb.com/heroku_97681?reconnect=true')
        assert mysql_config['ENGINE'] == 'django.db.backends.mysql'
        assert mysql_config['NAME'] == 'heroku_97681'
        assert mysql_config['HOST'] == 'us-cdbr-east.cleardb.com'
        assert mysql_config['USER'] == 'bea6eb0'
        assert mysql_config['PASSWORD'] == '69772142'
        assert mysql_config['PORT'] == ''

    def test_mysql_gis_parsing(self):
        mysql_gis_config  = DatabaseUrl().parse('mysqlgis://user:password@127.0.0.1/some_database')
        assert mysql_gis_config['ENGINE'] == 'django.contrib.gis.db.backends.mysql'
        assert mysql_gis_config['NAME'] == 'some_database'
        assert mysql_gis_config['HOST'] == '127.0.0.1'
        assert mysql_gis_config['USER'] == 'user'
        assert mysql_gis_config['PASSWORD'] == 'password'
        assert mysql_gis_config['PORT'] == ''

    def test_oracle_tns_parsing(self):
        oracle_tns_config = DatabaseUrl().parse('oracle://user:password@sid/')
        assert oracle_tns_config['ENGINE'] == 'django.db.backends.oracle'
        assert oracle_tns_config['NAME'] == 'sid'
        assert oracle_tns_config['HOST'] == ''
        assert oracle_tns_config['USER'] == 'user'
        assert oracle_tns_config['PASSWORD'] == 'password'
        self.assertFalse('PORT' in oracle_tns_config)

    def test_oracle_parsing(self):
        oracle_config = DatabaseUrl().parse('oracle://user:password@host:1521/sid?timeout=10')
        assert oracle_config['ENGINE'] == 'django.db.backends.oracle'
        assert oracle_config['NAME'] == 'sid'
        assert oracle_config['HOST'] == 'host'
        assert oracle_config['USER'] == 'user'
        assert oracle_config['PASSWORD'] == 'password'
        assert isinstance(oracle_config['PORT'], str)
        assert oracle_config['PORT'] == '1521'
        assert oracle_config['OPTIONS']['timeout'] == 10

    def test_oracle_pool_options_parsing(self):
        oracle_config = DatabaseUrl().parse('oracle://user:password@host:1521/sid?pool_timeout=1&pool_max=5')
        assert oracle_config['ENGINE'] == 'django.db.backends.oracle'
        assert oracle_config['POOL']['timeout'] == 1
        assert oracle_config['POOL']['max'] == 5




    def test_mysql_gis_parsing(self):
        url = DatabaseUrl().parse('mysqlgis://uf07k1i6d8ia0v:wegauwhgeuioweg@ec2-107-21-253-135.compute-1.amazonaws.com:5431/d8r82722r2kuvn')
        assert url['ENGINE'] == 'django.contrib.gis.db.backends.mysql'


    def test_cleardb_parsing(self):
        url = DatabaseUrl().parse('mysql://bea6eb025ca0d8:69772142@us-cdbr-east.cleardb.com/heroku_97681db3eff7580?reconnect=true')

        assert url['ENGINE'] == 'django.db.backends.mysql'
        assert url['NAME'] == 'heroku_97681db3eff7580'
        assert url['HOST'] == 'us-cdbr-east.cleardb.com'
        assert url['USER'] == 'bea6eb025ca0d8'
        assert url['PASSWORD'] == '69772142'
        assert url['PORT'] == ''
        assert url['OPTIONS']['reconnect'] == True

    def test_mysql_no_password(self):
        url = DatabaseUrl().parse('mysql://travis@localhost/test_db')

        assert url['ENGINE'] == 'django.db.backends.mysql'
        assert url['NAME'] == 'test_db'
        assert url['HOST'] == 'localhost'
        assert url['USER'] == 'travis'
        assert url['PASSWORD'] == ''
        assert url['PORT'] == ''

    def test_sqlite_parsing(self):
        sqlite_config = DatabaseUrl().parse('sqlite:////full/path/to/your/database/file.sqlite')
        assert sqlite_config['ENGINE'] == 'django.db.backends.sqlite3'
        assert sqlite_config['NAME'] == '/full/path/to/your/database/file.sqlite'

    def test_empty_sqlite_url(self):
        url = DatabaseUrl().parse('sqlite://')

        assert url['ENGINE'] == 'django.db.backends.sqlite3'
        assert url['NAME'] == ':memory:'

    def test_memory_sqlite_url(self):
        url = DatabaseUrl().parse('sqlite://:memory:')

        assert url['ENGINE'] == 'django.db.backends.sqlite3'
        assert url['NAME'] == ':memory:'

    def test_database_options_parsing(self):
        url = DatabaseUrl().parse('postgres://user:pass@host:1234/dbname?conn_max_age=600')
        assert url['CONN_MAX_AGE'] == 600

        url = DatabaseUrl().parse('mysql://user:pass@host:1234/dbname?init_command=SET storage_engine=INNODB')
        assert url['OPTIONS'] == { 'init_command': 'SET storage_engine=INNODB' }

    def test_database_ldap_url(self):
        url = 'ldap://cn=admin,dc=nodomain,dc=org:some_secret_password@ldap.nodomain.org/'
        url = DatabaseUrl().parse(url)

        assert url['ENGINE'] == 'ldapdb.backends.ldap'
        assert url['HOST'] == 'ldap.nodomain.org'
        assert url['PORT'] == ''
        assert url['NAME'] == 'ldap://ldap.nodomain.org'
        assert url['USER'] == 'cn=admin,dc=nodomain,dc=org'
        assert url['PASSWORD'] == 'some_secret_password'


class CacheTestSuite(unittest.TestCase):

    def test_cache_url_value(self):

        cache_config = CacheUrl().parse('memcache://127.0.0.1:11211')
        assert cache_config['BACKEND'] == 'django.core.cache.backends.memcached.MemcachedCache'
        assert cache_config['LOCATION'] == '127.0.0.1:11211'

        redis_config = CacheUrl().parse('rediscache://127.0.0.1:6379:1?client_class=django_redis.client.DefaultClient&password=secret')
        assert redis_config['BACKEND'] == 'django_redis.cache.RedisCache'
        assert redis_config['LOCATION'] == 'redis://127.0.0.1:6379:1'
        assert redis_config['OPTIONS'] == {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': 'secret',
        }

    def test_memcache_parsing(self):
        url = CacheUrl().parse('memcache://127.0.0.1:11211')

        assert url['BACKEND'] == 'django.core.cache.backends.memcached.MemcachedCache'
        assert url['LOCATION'] == '127.0.0.1:11211'

    def test_memcache_pylib_parsing(self):
        url = CacheUrl().parse('pymemcache://127.0.0.1:11211')

        assert url['BACKEND'] == 'django.core.cache.backends.memcached.PyLibMCCache'
        assert url['LOCATION'] == '127.0.0.1:11211'

    def test_memcache_multiple_parsing(self):
        url = CacheUrl().parse('memcache://172.19.26.240:11211,172.19.26.242:11212')

        assert url['BACKEND'] == 'django.core.cache.backends.memcached.MemcachedCache'
        assert url['LOCATION'] == ['172.19.26.240:11211', '172.19.26.242:11212']

    def test_memcache_socket_parsing(self):
        url = CacheUrl().parse('memcache:///tmp/memcached.sock')

        assert url['BACKEND'] == 'django.core.cache.backends.memcached.MemcachedCache'
        assert url['LOCATION'] == 'unix:/tmp/memcached.sock'

    def test_dbcache_parsing(self):
        url = CacheUrl().parse('dbcache://my_cache_table')

        assert url['BACKEND'] == 'django.core.cache.backends.db.DatabaseCache'
        assert url['LOCATION'] == 'my_cache_table'

    def test_filecache_parsing(self):
        url = CacheUrl().parse('filecache:///var/tmp/django_cache')

        assert url['BACKEND'] == 'django.core.cache.backends.filebased.FileBasedCache'
        assert url['LOCATION'] == '/var/tmp/django_cache'

    def test_filecache_windows_parsing(self):
        url = CacheUrl().parse('filecache://C:/foo/bar')

        assert url['BACKEND'] == 'django.core.cache.backends.filebased.FileBasedCache'
        assert url['LOCATION'] == 'C:/foo/bar'

    def test_locmem_parsing(self):
        url = CacheUrl().parse('locmemcache://')

        assert url['BACKEND'] == 'django.core.cache.backends.locmem.LocMemCache'
        assert url['LOCATION'] == ''

    def test_locmem_named_parsing(self):
        url = CacheUrl().parse('locmemcache://unique-snowflake')

        assert url['BACKEND'] == 'django.core.cache.backends.locmem.LocMemCache'
        assert url['LOCATION'] == 'unique-snowflake'

    def test_dummycache_parsing(self):
        url = CacheUrl().parse('dummycache://')

        assert url['BACKEND'] == 'django.core.cache.backends.dummy.DummyCache'
        assert url['LOCATION'] == ''

    def test_redis_parsing(self):
        url = CacheUrl().parse('rediscache://127.0.0.1:6379:1?client_class=django_redis.client.DefaultClient&password=secret')

        assert url['BACKEND'] == REDIS_DRIVER
        assert url['LOCATION'] == 'redis://127.0.0.1:6379:1'
        assert url['OPTIONS'] == {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': 'secret',
        }

    def test_redis_socket_parsing(self):
        url = CacheUrl().parse('rediscache:///path/to/socket:1')
        assert url['BACKEND'] == 'django_redis.cache.RedisCache'
        assert url['LOCATION'] == 'unix:///path/to/socket:1'

    def test_redis_with_password_parsing(self):
        url = CacheUrl().parse('rediscache://:redispass@127.0.0.1:6379/0')
        assert REDIS_DRIVER == url['BACKEND']
        assert url['LOCATION'] == 'redis://:redispass@127.0.0.1:6379/0'

    def test_redis_socket_url(self):
        url = CacheUrl().parse('redis://:redispass@/path/to/socket.sock?db=0')
        assert REDIS_DRIVER == url['BACKEND']
        assert url['LOCATION'] == 'unix://:redispass@/path/to/socket.sock'
        assert url['OPTIONS'] == { 'DB': 0 }

    def test_options_parsing(self):
        url = CacheUrl().parse('filecache:///var/tmp/django_cache?timeout=60&max_entries=1000&cull_frequency=0')

        assert url['BACKEND'] == 'django.core.cache.backends.filebased.FileBasedCache'
        assert url['LOCATION'] == '/var/tmp/django_cache'
        assert url['TIMEOUT'] == 60
        assert url['OPTIONS'] == { 'MAX_ENTRIES': 1000, 'CULL_FREQUENCY': 0 }

class SearchTestSuite(unittest.TestCase):


    def test_solr_parsing(self):
        url = SearchUrl().parse('solr://127.0.0.1:8983/solr')

        assert url['ENGINE'] == 'haystack.backends.solr_backend.SolrEngine'
        assert url['URL'] == 'http://127.0.0.1:8983/solr'

    def test_solr_multicore_parsing(self):
        url = SearchUrl().parse('solr://127.0.0.1:8983/solr/solr_index?TIMEOUT=360')

        assert url['ENGINE'] == 'haystack.backends.solr_backend.SolrEngine'
        assert url['URL'] == 'http://127.0.0.1:8983/solr/solr_index'
        assert url['TIMEOUT'] == 360
        assert 'INDEX_NAME' not in url
        assert 'PATH' not in url

    def test_elasticsearch_parsing(self):
        url = SearchUrl().parse('elasticsearch://127.0.0.1:9200/index?TIMEOUT=360')

        assert url['ENGINE'] == 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine'
        assert 'INDEX_NAME' in url.keys()
        assert url['INDEX_NAME'] == 'index'
        assert 'TIMEOUT' in url.keys()
        assert url['TIMEOUT'] == 360
        assert 'PATH' not in url

    def test_whoosh_parsing(self):
        url = SearchUrl().parse('whoosh:///home/search/whoosh_index?STORAGE=file&POST_LIMIT=1234567')

        assert url['ENGINE'] == 'haystack.backends.whoosh_backend.WhooshEngine'
        assert 'PATH' in url.keys()
        assert url['PATH'] == '/home/search/whoosh_index'
        assert 'STORAGE' in url.keys()
        assert url['STORAGE'] == 'file'
        assert 'POST_LIMIT' in url.keys()
        assert url['POST_LIMIT'] == 1234567
        assert 'INDEX_NAME' not in url

    def test_xapian_parsing(self):
        url = SearchUrl().parse('xapian:///home/search/xapian_index?FLAGS=myflags')

        assert url['ENGINE'] == 'haystack.backends.xapian_backend.XapianEngine'
        assert 'PATH' in url.keys()
        assert url['PATH'] == '/home/search/xapian_index'
        assert 'FLAGS' in url.keys()
        assert url['FLAGS'] == 'myflags'
        assert 'INDEX_NAME' not in url

    def test_simple_parsing(self):
        url = SearchUrl().parse('simple:///')

        assert url['ENGINE'] == 'haystack.backends.simple_backend.SimpleEngine'
        assert 'INDEX_NAME' not in url
        assert 'PATH' not in url

    def test_elasticsearchdsl_parsing(self):
        url = ElasticSearchDslUrl().parse('elasticsearchdsl://127.0.0.1:9200/index?timeout=360&use_ssl=true&verify_certs=false')

        assert url['hosts'] == '127.0.0.1'
        assert 'port' in url.keys()
        assert url['port'] == 9200
        assert 'url_prefix' in url.keys()
        assert url['url_prefix'] == 'index'
        assert 'timeout' in url.keys()
        assert url['timeout'] == 360
        assert 'use_ssl' in url.keys()
        assert url['use_ssl'] is True
        assert 'verify_certs' in url.keys()
        assert url['verify_certs'] is False

    def test_common_args_parsing(self):
        excluded_indexes = 'myapp.indexes.A,myapp.indexes.B'
        include_spelling = 1
        batch_size = 100
        params = 'EXCLUDED_INDEXES=%s&INCLUDE_SPELLING=%s&BATCH_SIZE=%s' % (
            excluded_indexes,
            include_spelling,
            batch_size
        )

        url = SearchUrl().parse('solr://127.0.0.1:8983/solr?' + params)

        assert 'EXCLUDED_INDEXES' in url.keys()
        assert 'myapp.indexes.A' in url['EXCLUDED_INDEXES']
        assert 'myapp.indexes.B' in url['EXCLUDED_INDEXES']
        assert 'INCLUDE_SPELLING' in url.keys()
        assert url['INCLUDE_SPELLING']
        assert 'BATCH_SIZE' in url.keys()
        assert url['BATCH_SIZE'] == 100



class ServiceTests(object):

    def test_service(empty_environ):

        class MyService(Service):

            class MainGroup(Group):

                INT_VAR = 2
                STR_VAR = 'str'

            class OtherGroup(Group):

                OTHER_VAR = 3


        MyService.setup(globals())
        assert INT_VAR == 2


class EmailTests(object):


    def test_smtp_parsing(self):
        url = EmailUrl().parse('smtps://user@domain.com:password@smtp.example.com:587')

        assert url['EMAIL_BACKEND'] == 'django.core.mail.backends.smtp.EmailBackend'
        assert url['EMAIL_HOST'] == 'smtp.example.com'
        assert url['EMAIL_HOST_PASSWORD'] == 'password'
        assert url['EMAIL_HOST_USER'] == 'user@domain.com'
        assert url['EMAIL_PORT'] == 587
        assert url['EMAIL_USE_TLS'] == True


@pytest.fixture(scope='session')
def simple_context_setup(tmpdir_factory):
    directory = tmpdir_factory.mktemp('simple')
    directory.join('context.py').write(
        """
        context.groups(
            Group('simple',
                LIST_VAR=[],
                STR_VAR='default-str',
                INT_VAR=2,
            )
        )
        
        @context.postprocess
        def postprocess(variables, extras):
            extras['ANOTHER_VAR'] = 4 * variables['INT_VAR']
            extras['INITIALIZED_VAR'] = 'initialized'
        
        @context.initializer
        def postprocess(variables):
            import os
            os.environ['REPEAT_INITIALIZED_VAR'] = variables['INITIALIZED_VAR']
        
        @context.filter
        def title_filter(value, argument):
            return '%s: %s' % (argument, value)
        
        context.templates({
            "/etc/example/output.conf": "template.conf",
        })
        
        context.glob_templates("/etc/example", "*.conf2")
        
        """)

    directory.join('template.conf').write(
        """
        {{ STR_VAR }}
        {% for element in LIST_VAR %}
        x: {{ element }}
        {% endfor %}
        {{ STR_VAR|title_filter("label") }}
        another: {{ ANOTHER_VAR }}
        """
    )
    directory.join('glob.conf2').write("example")

    return directory


@pytest.fixture(scope='session')
def simple_arguments_setup(tmpdir_factory):
    directory = tmpdir_factory.mktemp('simple')
    directory.join('service.py').write(
        """
        from arguments import *
        
        class SimpleService(Service)
        
            class Simple(Group):
                LIST_VAR = []
                STR_VAR = 'default-str'
                INT_VAR = 2
        
            def postprocess_data(variables, extras):
                extras['ANOTHER_VAR'] = 4 * variables['INT_VAR']
                extras['INITIALIZED_VAR'] = 'initialized'
        
            def initialize_vars(variables):
                import os
                os.environ['REPEAT_INITIALIZED_VAR'] = variables['INITIALIZED_VAR']
        
            @filter
            def title_filter(value, argument):
                return '%s: %s' % (argument, value)
        
            templates = {
                "/etc/example/output.conf": "template.conf",
            }
        
            glob_templates = (
                ("/etc/example", "*.conf2"),
            )
        
        """)

    directory.join('template.conf').write(
        """
        {{ STR_VAR }}
        {% for element in LIST_VAR %}
        x: {{ element }}
        {% endfor %}
        {{ STR_VAR|title_filter("label") }}
        another: {{ ANOTHER_VAR }}
        """
    )
    directory.join('glob.conf2').write("example")

    return directory



def test_basic_context_load(empty_environ, simple_context_setup, capsys):
    assert 'simple' in str(simple_context_setup)
    assert 'group' in simple_context_setup.join('context.py').read()
    process.main("-d", str(simple_context_setup), "templates")
    output, _ = capsys.readouterr()
    assert '/etc/example/output.conf' in output
    assert 'template.conf' in output

    assert '/etc/example/glob.conf2' in output
    # assert 'glob.conf2' in output

# def test_new_service_load(empty_environ, simple_arguments_setup, capsys):
#     # assert 'group' in simple_context_setup.join('context.py').read()
#     process.main("-d", str(simple_arguments_setup), "templates")
#     assert '/etc/example/output.conf' in output


def test_basic_context_process(empty_environ, simple_context_setup):
    output_root = simple_context_setup.join('output')

    os.environ['STR_VAR'] = 'hello'
    os.environ['LIST_VAR'] = 'one,two,three'
    os.environ['REPEAT_INITIALIZED_VAR'] = 'not initialized'

    process.main("-d", str(simple_context_setup), "process", "--root", str(output_root))
    assert os.environ['REPEAT_INITIALIZED_VAR'] == 'initialized'

    output = output_root.join('etc/example/output.conf').read()
    assert 'hello' in output
    assert 'x: one' in output
    assert 'x: two' in output
    assert 'label: hello' in output
    assert 'another: 8' in output


def test_render_command(empty_environ, simple_context_setup, capsys):
    os.environ['STR_VAR'] = 'again'
    os.environ['LIST_VAR'] = 'x,y,z'

    process.main("-d", str(simple_context_setup), "render", '-t', '/etc/example/output.conf')
    output, _ = capsys.readouterr()

    assert 'again' in output
    assert 'x: x' in output
    assert 'x: y' in output


def test_example_varnish_vcl(empty_environ):

    os.environ['APP_BACKENDS'] = '10.0.0.1:8000,10.0.0.2:8001'

    group = Group(
        APP_BACKENDS=[GenericUrl],
    )
    service = group_as_service(group)

    template = templates.load_template_from_string(
        """
        {% for backend in APP_BACKENDS %}
        backend app_backend_{{ loop.index }} {
            .host = "{{ backend.hostname }}";
            .port = "{{ backend.port }}";
        }
        {% endfor %}
        """
    )
    output = templates.process_template(template, service.get_context())
    assert "app_backend_1" in output
    assert "app_backend_2" in output
    assert "app_backend_3" not in output
    assert "10.0.0.1" in output


def test_user_password():
    assert UserPassword().parse('testuser:testpassword') == { 'USER': 'testuser', 'PASSWORD': 'testpassword' }


def test_match_url():
    no_password_url = MatchUrl(password=empty)
    no_password_url.parse('http://user@host/path') == 'http://user@host/path'
    with pytest.raises(ImproperlyPassedArguments):
        no_password_url.parse('http://user:password@host/path')


def test_encoding():
    encoded_json = Json(encoding='base64')
    assert encoded_json.parse('eyJ4IjogInh4IiwgInkiOiAieXkiLCAieiI6IFsieiIsICJ6eiIsICJ6enoiXX0K') == {"x": "xx", "y": "yy", "z": ["z", "zz", "zzz"]}

@pytest.fixture(scope='function')
def disable_socket_connect(monkeypatch):

    def patched_connect(_socket, host_port):
        return 0

    import socket

    monkeypatch.setattr(socket.socket, 'connect', patched_connect)


def test_wait_for(empty_environ, disable_socket_connect):

    class TestService(Service):

        class Main(Group):

            OTHER_SERVICE = SearchUrl('elasticsearch://127.0.0.1:9210/some-index')
            WAIT_FOR_OTHER_SERVICE = WaitForPort(hostname='OTHER_SERVICE', default=False, timeout=2)

    service = TestService()
    service.explode(globals())
    assert service.get_result('OTHER_SERVICE').intermediate_value is not None
    assert service.get_result('OTHER_SERVICE').intermediate_value['urlparse']['hostname'] == '127.0.0.1'

    assert WAIT_FOR_OTHER_SERVICE == False
    assert OTHER_SERVICE['INDEX_NAME'] == 'some-index'

    os.environ['WAIT_FOR_OTHER_SERVICE'] = 'True'

    waiting_service = TestService()
    waiting_service.explode(globals())

    assert WAIT_FOR_OTHER_SERVICE == True

    # assert MAIN_STR == 'str'
    # assert MISC_INT == 1
