import datetime

from cache_headers.utils import httpdate


def all_users(request, response, user, age):
    """Content is cached once for all users."""

    response["Last-Modified"] = httpdate(datetime.datetime.utcnow())
    # nginx specific but safe to set in all cases
    response["X-Accel-Expires"] = age
    response["Cache-Control"] = "max-age=%d, s-maxage=%d" \
        % (max(age / 6, 30), age)
    response["Vary"] = "Accept-Encoding"


def anonymous_only(request, response, user, age):
    """Content is cached once only for anonymous users."""

    if user.is_anonymous():
        response["Last-Modified"] = httpdate(datetime.datetime.utcnow())
        # nginx specific but safe to set in all cases
        response["X-Accel-Expires"] = age
        response["Cache-Control"] = "max-age=%d, s-maxage=%d" \
            % (max(age / 6, 30), age)
        response["X-Is-Anonymous"] = 1
        response["Vary"] = "Accept-Encoding,X-Is-Anonymous"
    else:
        response["Cache-Control"] = "no-cache"


def anonymous_and_authenticated(request, response, user, age):
    """Content is cached once for anonymous users and once for authenticated
    users. There is an inherent risk in caching authenticated content. It is
    not so much a security risk as a leakage risk. For example, if your site
    has a paywall then it is easy to circumvent the paywall by spoofing the
    X-Is-Authenticated vary header."""

    response["Last-Modified"] = httpdate(datetime.datetime.utcnow())
    # nginx specific but safe to set in all cases
    response["X-Accel-Expires"] = age
    response["Cache-Control"] = "max-age=%d, s-maxage=%d" \
        % (max(age / 6, 30), age)
    response["X-Is-Authenticated"] = user.is_authenticated() and 1 or 0
    response["Vary"] = "Accept-Encoding,X-Is-Authenticated"


def per_user(request, response, user, age):
    """Content is cached once for anonymous users and for each authenticated
    user individually."""

    response["Last-Modified"] = httpdate(datetime.datetime.utcnow())
    # nginx specific but safe to set in all cases
    response["X-Accel-Expires"] = age
    response["Cache-Control"] = "max-age=%d, s-maxage=%d" \
        % (max(age / 6, 30), age)

    if user.is_anonymous():
        response["X-Session"] = 0
        response["Vary"] = "Accept-Encoding,X-Session"
    else:
        # Spoofing X-Session is only possible in case of a man-in-the-middle
        # attack or a very lucky guess. Still, when in doubt don't use this
        # policy and rather adjust your reverse caching proxy to consider the
        # session cookie.
        response["X-Session"] = request.session._session_key
        response["Vary"] = "Accept-Encoding,X-Session"
