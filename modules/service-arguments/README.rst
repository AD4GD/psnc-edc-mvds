Service-arguments
=================

Service-arguments allows you to utilize 12factor inspired environment variables to configure your Django application or your contenerized service.

This module is a derivative of a great django-environ, enriched with:

- more strict option parsing,
- better support for service operators,
- improved in-place extensibility.

Service-arguments can be used for two independent purposes:

- to be an entry point to instrument Django application,
- to generate configuration files from Jinja2 templates - designed to be used on container startup.

Django settings
=================

This is how your `settings.py` file might look like file before you have installed **service-arguments**:

.. code-block:: python

    DEBUG = True

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'database',
            'USER': 'user',
            'PASSWORD': 'githubbedpassword',
            'HOST': '127.0.0.1',
            'PORT': '8458',
        }
        'extra': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(SITE_ROOT, 'database.sqlite')
        }
    }

    SECRET_KEY = '...im incredibly still here...'

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': [
                '127.0.0.1:11211', '127.0.0.1:11212', '127.0.0.1:11213',
            ]
        },
        'redis': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': '127.0.0.1:6379:1',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'PASSWORD': 'redis-githubbed-password',
            }
        }
    }

And this how it will look like once you will get back control over your Django application using service-arguments:

.. code-block:: python

    from arguments import Parser, Group
    from arguments.types import *

    PARSER = Parser(
        Group('main',
            DEBUG=False,
            SECRET_KEY=Str(),
        ),
        Group('databases',
            DEFAULT_DATABASE=DatabaseUrl(), # Raises ImproperlyConfigured exception if DEFAULT_DATABASE is not found in environment
            EXTRA_DATABASE=DatabaseUrl('sqlite:////tmp/my-tmp-sqlite.db'),
        ),
        Group('caches',
            DEFAULT_CACHE=CacheUrl(),
            REDIS_CACHE=RedisUrl(),
        ),
    )

    for env_file in os.environ.get('ENV_FILE', '').split(','):
        if env_file:
            PARSER.read_env(env_file)

    PARSER.explode(globals())

    DATABASES = {
        'default': DEFAULT_DATABASE,
        'extra': EXTRA_DATABASE,
    }

    CACHES = {
        'default': DEFAULT_CACHE,
        'redis': REDIS_CACHE,
    }



Create a ``app.env`` file (and point to it with ENV_FILE environment variable):

.. code-block:: bash

    DEBUG=True
    SECRET_KEY=your-secret-key
    DEFAULT_DATABASE=psql://urser:un-githubbedpassword@127.0.0.1:8458/database
    DEFAULT_CACHE=memcache://127.0.0.1:11211,127.0.0.1:11212,127.0.0.1:11213
    REDIS_CACHE=rediscache://127.0.0.1:6379:1?client_class=django_redis.client.DefaultClient&password=redis-un-githubbed-password


Configuration templates
=======================

Service-arguments can also be used to generate service configuration files from provided templates.

Templates are processed with **Jinja2** engine and use variables parsed using the same mechanisms as Django settings.

Following recipe presents an example of configuring a simple HAProxy with several backends - their IP's and ports will be given dynamically using environment variable.

Create directory for the source template context in your code repository:

.. code-block:: bash

    $ cd your-git-repository
    $ mkdir haproxy-config


In the created directory, create the ``context.py`` file with the declaration of accepted environment variables, and the list of template files.

.. code-block:: python

    context.groups(
        Group(
            # single address with default value
            BIND=GenericUrl('0.0.0.0:8000'),
            # list of addresses, with default value of a single address
            BACKENDS=[ GenericUrl('127.0.0.1:8000') ],
        )
    )

    context.glob_templates("/etc/haproxy", "*.cfg")


Create some template files - here ``haproxy.cfg`` is used as an example:

.. code-block:: django

    listen myproxy {{ BIND.hostname }}:{{ BIND.port }}
        mode http
        stats enable
        stats uri /haproxy?stats
        balance roundrobin
        option httpclose
        option forwardfor
        {% for backend in BACKENDS %}
        server backend-{{ loop.index0 }} {{ backend.hostname }}:{{ backend.port }} check
        {% endfor %}


In your Dockerfile place line looking like this (your base image has to enabled with Service-Arguments before that TODO):

.. code-block:: docker

    COPY haproxy-context /etc/arguments/haproxy


After building your container and running it the following way:

.. code-block:: bash

    docker run -e BACKENDS=10.0.0.1:8000,10.0.0.2:8003 haproxy-image


You will see a starting container with file ``/etc/haproxy/haproxy.cfg`` filled with following content:

.. code-block:: django

    listen myproxy 0.0.0.0:8000
        mode http
        stats enable
        stats uri /haproxy?stats
        balance roundrobin
        option httpclose
        option forwardfor
        server backend-0 10.0.0.1:8000 check
        server backend-1 10.0.0.2:8003 check


How to install
==============

::

    $ pip install service-arguments


Supported Types
===============


Tips
====


Tests
=====

::

    $ git clone git@github.com:sniegu/service-arguments.git
    $ cd service-arguments/arguments/
    $ py.test


License
=======

service-arguments is licensed under the MIT License - see the `LICENSE`_ file for details

Changelog
=========

0.5.1 - 28-November-2017
-------------------------
  - Add `Django Elasticsearch DSL <https://github.com/sabricot/django-elasticsearch-dsl>`_ support


0.5.0 - 23-September-2016
-------------------------
  - Full rewrite based on original django-environ

Credits
=======

- `12factor`_
- `12factor-django`_
- `Two Scoops of Django`_
- `django-environ`_


.. _12factor: http://www.12factor.net/
.. _12factor-django: http://www.wellfireinteractive.com/blog/easier-12-factor-django/
.. _`Two Scoops of Django`: http://twoscoopspress.org/
.. _`django-environ`: https://github.com/joke2k/django-environ

.. _Distribute: http://pypi.python.org/pypi/distribute
.. _`modern-package-template`: http://pypi.python.org/pypi/modern-package-template


.. _LICENSE: https://github.com/sniegu/service-arguments/blob/master/LICENSE.txt
