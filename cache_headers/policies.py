import datetime

from django.conf import settings

from cache_headers.utils import httpdate


try:
    browser_cache_seconds = settings.CACHE_HEADERS["browser-cache-seconds"]
except (KeyError, AttributeError):
    browser_cache_seconds = 5

# We add Cookie to Vary in all cases to compensate for overzealous intermediary
# proxies we have no control over. The presence of Cookie will avoid any
# accidental shared caching of per-user content. Our sample Varnish
# configuration file is smart enough to omit Cookie from the Vary header when
# computing the hash.

def all_users(request, response, user, age):
    """Content is cached once for all users."""

    response["Last-Modified"] = httpdate(datetime.datetime.utcnow())
    # nginx specific but safe to set in all cases
    response["X-Accel-Expires"] = age
    response["Cache-Control"] = "max-age=%d, s-maxage=%d" \
        % (browser_cache_seconds, age)
    response["X-Hash-Cookies"] = "messages"
    response["Vary"] = "Accept-Encoding,Cookie"


def anonymous_only(request, response, user, age):
    """Content is cached once only for anonymous users."""

    if user.is_anonymous:
        response["Last-Modified"] = httpdate(datetime.datetime.utcnow())
        # nginx specific but safe to set in all cases
        response["X-Accel-Expires"] = age
        response["Cache-Control"] = "max-age=%d, s-maxage=%d" \
            % (browser_cache_seconds, age)
    else:
        response["Cache-Control"] = "no-cache"

    response["X-Hash-Cookies"] = "messages|isauthenticated"
    response["Vary"] = "Accept-Encoding,Cookie"


def anonymous_and_authenticated(request, response, user, age):
    """Content is cached once for anonymous users and once for authenticated
    users."""

    response["Last-Modified"] = httpdate(datetime.datetime.utcnow())
    # nginx specific but safe to set in all cases
    response["X-Accel-Expires"] = age
    response["Cache-Control"] = "max-age=%d, s-maxage=%d" \
        % (browser_cache_seconds, age)
    response["X-Hash-Cookies"] = "messages|isauthenticated"
    response["Vary"] = "Accept-Encoding,Cookie"


def per_user(request, response, user, age):
    """Content is cached once for anonymous users and for each authenticated
    user individually."""

    response["Last-Modified"] = httpdate(datetime.datetime.utcnow())
    # nginx specific but safe to set in all cases
    response["X-Accel-Expires"] = age
    response["Cache-Control"] = "max-age=%d, s-maxage=%d" \
        % (browser_cache_seconds, age)
    response["X-Hash-Cookies"] = "messages|%s" % settings.SESSION_COOKIE_NAME
    response["Vary"] = "Accept-Encoding,Cookie"
