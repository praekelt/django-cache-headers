Django Cache Headers
====================

.. figure:: https://travis-ci.org/praekelt/django-cache-headers.svg?branch=develop
   :align: center
   :alt: Travis

Overview
--------

Django Cache Headers allows you to set HTTP caching headers for URL patterns
according to certain policies. It does not perform any caching itself - it
merely sets the headers on the response which are then interpreted by eg. Nginx.

Installation
------------

1. Install or add ``django-cache-headers`` to your Python path.
2. Add ``cache_headers`` to your ``INSTALLED_APPS`` setting.
3. Add ``cache_headers.middleware.CacheHeadersMiddleware`` before
   SessionMiddleware and AuthenticationMiddleware to your ``MIDDLEWARE_CLASSES`` setting.

Policies
--------
Django Cache Headers provides four caching policies. You may define your own policies.:

1. all-users - response is marked as cached once for all users.
2. anonymous-only - response is marked as cached once only for anonymous users.
3. anonymous-and-authenticated - response is marked as cached once for anonymous users and once for authenticated users.
4. per-user - response is marked as cached once for anonymous users and for each authenticated user individually.

Sample Varnish config file
--------------------------

    # Use 4.0 format
    vcl 4.0;

    # Default upstream
    backend default {
        .host = "127.0.0.1";
        .port = "8080";
    }

    # Access control
    acl purge {
        "localhost";
        "127.0.0.1";
    }

    # vcl_recv adapted from the Varnish default
    sub vcl_recv {
        if (req.method == "PURGE") {
            if (!client.ip ~ purge) {
                return(synth(405, "Not allowed."));
            }
            return(purge);
        }

        if (req.method == "PRI") {
            # We do not support SPDY or HTTP/2.0
            return(synth(405));
        }

        if (req.method != "GET" &&
          req.method != "HEAD" &&
          req.method != "PUT" &&
          req.method != "POST" &&
          req.method != "TRACE" &&
          req.method != "OPTIONS" &&
          req.method != "DELETE") {
            # Non-RFC2616 or CONNECT which is weird
            return(pipe);
        }

        if (req.method != "GET" && req.method != "HEAD") {
            # We only deal with GET and HEAD by default
            return(pass);
        }
        if (req.http.Authorization) {
            # Not cacheable by default
            return(pass);
        }
        return(hash);
    }

    # Useful headers
    sub vcl_deliver {
        if (obj.hits > 0) {
            set resp.http.X-Cache = "HIT";
        } else {
            set resp.http.X-Cache = "MISS";
        }
    }

    sub vcl_hash {
        # Cache even with cookies present. Note we don't delete the cookies.
        # Also, we only consider cookies in X-Cookie-Hash as part of the hash.
        # This value is set by the relevant Django Cache Headers policy.
        set req.http.X-Cookie-Hash = "";
        if (req.http.X-Hash-Cookies) {
            set req.http.X-Cookie-Pattern = ";("  + req.http.X-Hash-Cookies + ")=";
            set req.http.X-Cookie-Hash = ";" + req.http.Cookie;
            # VCL does not currently support variables in regsuball, so hardcode
            #set req.http.X-Cookie-Hash = regsuball(req.http.X-Cookie-Hash, req.http.X-Cookie-Pattern, "; \1=");
            if (req.http.X-Cookie-Hash == "messages") {
                    set req.http.X-Cookie-Hash = regsuball(req.http.X-Cookie-Hash, ";(messages)=", "; \1=");
            }
            if (req.http.X-Cookie-Hash == "messages|isauthenticated") {
                    set req.http.X-Cookie-Hash = regsuball(req.http.X-Cookie-Hash, ";(messages|isauthenticated)=", "; \1=");
            }
            if (req.http.X-Cookie-Hash == "messages|sessionid") {
                    set req.http.X-Cookie-Hash = regsuball(req.http.X-Cookie-Hash, ";(messages|sessionid)=", "; \1=");
            }
            set req.http.X-Cookie-Hash = regsuball(req.http.X-Cookie-Hash, ";[^ ][^;]*", "");
            set req.http.X-Cookie-Hash = regsuball(req.http.X-Cookie-Hash, "^[; ]+|[; ]+$", "");
        }
        hash_data(req.http.X-Cookie-Hash);
    }

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

