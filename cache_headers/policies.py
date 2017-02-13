import datetime

from cache_headers.utils import httpdate


def all_users(request, response, user, age):
    """Content is cached once for all users."""

    response["Last-Modified"] = httpdate(datetime.datetime.utcnow())
    response["X-Accel-Expires"] = age
    response["Cache-Control"] = "max-age=%d" % max(age / 6, 30)
    response["Vary"] = "Accept-Encoding"


def anonymous_only(request, response, user, age):
    """Content is cached once only for anonymous users."""

    if user.is_anonymous():
        response["Last-Modified"] = httpdate(datetime.datetime.utcnow())
        response["X-Accel-Expires"] = age
        response["Cache-Control"] = "max-age=%d" % max(age / 6, 30)
        response["X-Is-Anonymous"] = 1
        response["Vary"] = "Accept-Encoding,X-Is-Anonymous"
    else:
        response["Cache-Control"] = "no-cache"


def anonymous_and_authenticated(request, response, user, age):
    """Content is cached once for anonymous users and once for authenticated
    users."""

    response["Last-Modified"] = httpdate(datetime.datetime.utcnow())
    response["X-Accel-Expires"] = age
    response["Cache-Control"] = "max-age=%d" % max(age / 6, 30)
    response["X-Is-Authenticated"] = user.is_authenticated() and 1 or 0
    response["Vary"] = "Accept-Encoding,X-Is-Authenticated"


def per_user(request, response, user, age):
    """Content is cached once for anonymous users and for each authenticated
    user individually."""

    response["Last-Modified"] = httpdate(datetime.datetime.utcnow())
    response["X-Accel-Expires"] = age
    response["Cache-Control"] = "max-age=%d" % max(age / 6, 30)

    if user.is_anonymous():
        response["X-Is-Anonymous"] = 1
        response["Vary"] = "Accept-Encoding,X-Is-Anonymous"
    else:
        # It is vitally important that the page does not leak personal info
        # because spoofing os X-User is trivial. This is the responsibility of
        # the page, not us.
        response["X-User"] = user.pk
        response["Vary"] = "Accept-Encoding,X-User"
