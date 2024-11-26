try:
    # TODO DV-795: Remove comment "# nosec" and fix warnings about `pickle` module in Bandit
    import cPickle as pickle  # nosec - switch off warning B403:blacklist in Bandit
except ImportError:
    # TODO DV-795: Remove comment "# nosec" and fix warnings about `pickle` module in Bandit
    import pickle  # nosec - switch off warning B403:blacklist in Bandit

import socket
import time
from threading import local

import pymemcache
from django.core.cache.backends.memcached import BaseMemcachedCache
from pymemcache.client.hash import Client, HashClient
from pymemcache.client.rendezvous import RendezvousHash


def serialize_pickle(key, value):  # pylint: disable=W0613
    if isinstance(value, str):
        return value.encode(), 1
    if isinstance(value, bytes):
        return value, 2

    return pickle.dumps(value), 3


def deserialize_pickle(key, value, flags):
    if flags == 1:
        return value.decode()  # encoded string
    if flags == 2:
        return value  # bytes
    if flags == 3:
        # TODO DV-795: Remove comment "# nosec" and fix warnings about `pickle` module in Bandit
        return pickle.loads(value)  # nosec - switch off warning B403:blacklist in Bandit

    raise Exception(f"Unknown flags for entry {key} with value: {value}")


class PatchedHashClient(HashClient):  # pylint: disable=R0902
    def __init__(  # pylint: disable=R0913,R0914
        self,
        servers,
        hasher=RendezvousHash,
        serializer=None,
        deserializer=None,
        connect_timeout=None,
        timeout=None,
        no_delay=False,
        socket_module=socket,
        key_prefix=b"",
        max_pool_size=None,
        lock_generator=None,
        retry_attempts=2,
        retry_timeout=1,
        dead_timeout=60,
        use_pooling=False,
        ignore_exc=False,
        allow_unicode_keys=False,
        default_noreply=True,
    ):
        self.clients = {}
        self.retry_attempts = retry_attempts
        self.retry_timeout = retry_timeout
        self.dead_timeout = dead_timeout
        self.use_pooling = use_pooling
        self.key_prefix = key_prefix
        self.ignore_exc = ignore_exc
        self.allow_unicode_keys = allow_unicode_keys
        self._failed_clients = {}
        self._dead_clients = {}
        self._last_dead_check_time = time.time()

        self.hasher = hasher()

        self.default_kwargs = {
            "connect_timeout": connect_timeout,
            "timeout": timeout,
            "no_delay": no_delay,
            "socket_module": socket_module,
            "key_prefix": key_prefix,
            "serializer": serializer,
            "deserializer": deserializer,
            "allow_unicode_keys": allow_unicode_keys,
            "default_noreply": default_noreply,
        }

        if use_pooling is True:
            self.default_kwargs.update({"max_pool_size": max_pool_size, "lock_generator": lock_generator})

        for server, port in servers:
            self.add_server(server, port)

    def disconnect_all(self):  # pragma: no cover
        for _, client in self.clients.items():
            client.quit()


class PatchedClient(Client):
    disconnect_all = Client.quit


pymemcache.client.base.Client = PatchedClient


class PyMemcacheImproved(BaseMemcachedCache):
    """An implementation of a cache binding using pymemcache.
    Added support for multiple cache servers.
    """

    def __init__(self, server, params=None):
        if params is None:
            params = {}
        self._local = local()
        self._params = params
        self._client_class = None
        self._single_server = None

        super().__init__(
            server=server,
            params=params,
            library=pymemcache,
            value_not_found_exception=ValueError,
        )

    @property
    def _cache(self):  # noqa
        client = getattr(self._local, "client", None)
        if client:
            return client

        options = {
            "serializer": serialize_pickle,
            "deserializer": deserialize_pickle,
        }
        if self._options:
            options.update(**self._options)

        if self._params:
            self._params = {k.lower(): v for k, v in self._params.items()}
            options.update(**self._params)

        self._single_server = len(self._servers) == 1
        self._client_class = PatchedClient if self._single_server else PatchedHashClient

        if self._single_server:
            host, port = self._servers[0].split(":")
            self._local.client = self._client_class((host, int(port)), **options)
        else:  # pragma: no cover
            servers_list = []
            for server in self._servers:
                host, port = server.split(":")
                servers_list.append((host, int(port)))

            self._local.client = self._client_class(servers_list, **options)

        return self._local.client
