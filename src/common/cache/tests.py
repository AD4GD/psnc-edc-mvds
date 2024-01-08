import time

from common.cache import pymemcached


class TestCache:
    @staticmethod
    def test_pymemcache_client():
        # pylint: disable=W0212

        # single cache server
        single_server_pymemcached_cache = pymemcached.PyMemcacheImproved(
            server="memcached:11211",
            params=dict(default_noreply=False),
        )
        single_server_pymemcached_cache.clear()
        # clear method does not empty cache, only invalidates items, waiting for items expiring is required here
        while single_server_pymemcached_cache._cache.stats()[b"curr_items"] > 0:
            time.sleep(0.05)
        single_server_pymemcached_cache.clear()
        # clear method does not empty cache, only invalidates items, waiting for items expiring is required here
        while single_server_pymemcached_cache._cache.stats()[b"curr_items"] > 0:
            time.sleep(0.05)

        # test string
        single_server_pymemcached_cache.add("str", "zażółć gęślą jaźń")
        assert single_server_pymemcached_cache.get("str") == "zażółć gęślą jaźń"
        assert single_server_pymemcached_cache._cache.stats()[b"curr_items"] == 1

        single_server_pymemcached_cache.delete("str")
        assert single_server_pymemcached_cache._cache.stats()[b"curr_items"] == 0

        # test bytes
        single_server_pymemcached_cache.add("bytes", b"quick brown fox jumps over the lazy dog")
        assert single_server_pymemcached_cache.get("bytes") == b"quick brown fox jumps over the lazy dog"
        assert single_server_pymemcached_cache._cache.stats()[b"curr_items"] == 1

        single_server_pymemcached_cache.delete("bytes")
        assert single_server_pymemcached_cache._cache.stats()[b"curr_items"] == 0

        # test integer
        single_server_pymemcached_cache.add("int", 234)
        assert single_server_pymemcached_cache.get("int") == 234
        assert single_server_pymemcached_cache._cache.stats()[b"curr_items"] == 1

        single_server_pymemcached_cache.delete("int")
        assert single_server_pymemcached_cache._cache.stats()[b"curr_items"] == 0

        # test multiple cache servers
        pymemcache_cache = pymemcached.PyMemcacheImproved(
            server="memcached:11211,memcached_alias:11211",
            params=dict(use_pooling=True, default_noreply=False),
        )

        pooling_clients = [val for _, val in pymemcache_cache._cache.clients.items()]
        assert pymemcache_cache._cache.use_pooling is True

        pymemcache_cache.clear()
        while pooling_clients[0].stats()[b"curr_items"] > 0 or pooling_clients[1].stats()[b"curr_items"] > 0:
            time.sleep(0.05)

        pymemcache_cache.add("a", 123)
        assert pymemcache_cache.get("a") == 123

        assert pooling_clients[0].stats()[b"curr_items"] == 1 and pooling_clients[1].stats()[b"curr_items"] == 1

        pymemcache_cache.delete("a")
        assert pymemcache_cache.get("a") is None
        assert pooling_clients[0].stats()[b"curr_items"] == 0 and pooling_clients[1].stats()[b"curr_items"] == 0
