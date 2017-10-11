Django Cache Headers
====================

.. figure:: https://travis-ci.org/praekelt/django-cache-headers.svg?branch=develop
   :align: center
   :alt: Travis

Overview
--------

Django Cache Headers allows you to set HTTP caching headers for URL patterns
according to certain policies. It does not perform any caching itself - it
merely sets the headers on the response which are then interpreted by eg. Varnish.

Doing a truly zero-conf Varnish turned out to be fragile, so Django Cache
Headers now generates a VCL file that can be included into or adapted to your
default Varnish configuration file.

Installation
------------

1. Install or add ``django-cache-headers`` to your Python path.
2. Add ``cache_headers`` to your ``INSTALLED_APPS`` setting.
3. Add ``cache_headers.middleware.CacheHeadersMiddleware`` before
   SessionMiddleware and AuthenticationMiddleware and MessageMiddleware to your
   ``MIDDLEWARE_CLASSES`` setting.

Policies
--------
Django Cache Headers provides four caching policies. You may define your own policies.:

1. all-users - response is marked as cached once for all users.
2. anonymous-only - response is marked as cached once only for anonymous users.
3. anonymous-and-authenticated - response is marked as cached once for anonymous users and once for authenticated users.
4. per-user - response is marked as cached once for anonymous users and for each authenticated user individually.

Settings
--------

The ``timeouts`` key combines the policy, timeout in seconds and URL regexes in a nested dictionary::

    CACHE_HEADERS = {
        "timeouts": {
            "all-users": {
                60: (
                    "^/all-users/",
                )
            },
            "anonymous-only": {
                60: (
                    "^/anonymous-only/",
                )
            },
            "anonymous-and-authenticated": {
                60: (
                    "^/anonymous-and-authenticated/",
                )
            },
            "per-user": {
                60: (
                    "^/per-user/",
                )
            },
            "custom-policy": {
                60: (
                    "^/custom-policy/",
                )
            }
        }
    }

Set ``browser-cache-seconds`` to specify how long the browser may cache a
response before it has to revalidate with the server. It defaults to 5 seconds.::

    CACHE_HEADERS = {"browser-cache-seconds": 10}

Set ``enable-tampering-checks`` to enable checks that guard against cache
poising by tampering with the cookies.
Keep this disabled for most unit tests. Unit test's client.login() does not
trigger the normal expected login path.

    CACHE_HEADERS = {"enable-tampering-checks": True}

Varnish configuration
---------------------

Generate the VCL snippet::

    python manage.py generate_vcl > /path/to/generated.vcl

Save the contents of `sample.vcl <sample.vcl>`_ as `/etc/varnish/default.vcl`.
Restart Varnish for the configuration to take effect.

