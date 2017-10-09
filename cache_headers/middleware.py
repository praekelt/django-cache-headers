import hashlib
import logging
import re
import uuid

from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.core.cache import cache
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect

from cache_headers import policies


# Default policies. Settings may override keys.
POLICIES = {
    "all-users": policies.all_users,
    "anonymous-only": policies.anonymous_only,
    "anonymous-and-authenticated": policies.anonymous_and_authenticated,
    "per-user": policies.per_user
}
try:
    POLICIES.update(settings.CACHE_HEADERS["policies"])
except (KeyError, AttributeError):
    pass

try:
    TIMEOUTS = settings.CACHE_HEADERS["timeouts"]
except (KeyError, AttributeError):
    TIMEOUTS = {}

# Build a flat list of rules
rules = []
for cache_type in TIMEOUTS.keys():
    for timeout, strings in TIMEOUTS[cache_type].items():
        for s in strings:
            rules.append((re.compile(r"" + s), timeout, cache_type, len(s)))

# Sort from longest string to shortest
rules.sort(key=lambda x: x[3], reverse=True)

# Subscribe to signals so we can mark the request
def on_user_auth_event(sender, user, request, **kwargs):
    setattr(request, "_dch_auth_event", True)

user_logged_in.connect(on_user_auth_event)
user_logged_out.connect(on_user_auth_event)


class CacheHeadersMiddleware(object):
    """Put this middleware before authentication middleware because response
    runs in reverse order."""

    def process_response(self, request, response):

        # Do not interfere in debug mode
        if settings.DEBUG:
            return response

        # If cache control was set at the start of this method then do nothing
        if ("Cache-Control" in response) or ("cache-control" in response):
            return response

        # Do nothing if response code is not 200
        if response.status_code != 200:
            return response

        # Default policy is to not cache
        response["Cache-Control"] = "no-cache"

        # If there is no user on the request then do nothing
        user = getattr(request, "user", None)
        if not user:
            return response

        # During login and logout we do not cache
        if hasattr(request, "_dch_auth_event"):
            return response

        # If user is anonymous but SESSION_COOKIE_NAME is in cookies and has a
        # value then this is an attempt at tampering.
        if user.is_anonymous() and (settings.SESSION_COOKIE_NAME in request.COOKIES):
            cookie = request.COOKIES[settings.SESSION_COOKIE_NAME]
            if getattr(cookie, "value", cookie):
                raise SuspiciousOperation(
                    "User is anonymous but received a sessionid"
                )

        # Never cache non-GET
        if request.method.lower() not in ("get", "head"):
            return response

        # Don't cache if response sets cookies
        if response.has_header("Set-Cookie"):
            logger = logging.getLogger("django")
            logger.warn(
                "Attempting to cache path %s but Set-Cookie is on the response" \
                    % request.get_full_path()
            )
            return response

        # Determine age and policy. Use cached lookups.
        full_path = request.get_full_path()
        key = "dch-%s" % hashlib.md5(full_path).hexdigest()
        cached = cache.get(key, None)
        if cached is not None:
            age = cached["age"]
            cache_type = cached["cache_type"]
        else:
            age = 0
            cache_type = None
            for pattern, timeout, cache_type, _ in rules:
                if pattern.match(full_path):
                    age = timeout
                    break

            # We can cache this for a long time because settings can't change
            # during the process lifetime.
            cache.set(key, {"age": age, "cache_type": cache_type}, 86400)

        # If request contains messages adjust url so it busts reverse cache.
        # This applies only to paths that would otherwise be cached.
        if age and request:
            pth = full_path
            # Return if already marked
            if "dch-uuid=" in pth:
                return response
            l = 0
            try:
                l = len(request._messages)
            except (AttributeError, TypeError):
                pass
            if l:
                if "?" in pth:
                    pth += "&dch-uuid="
                else:
                    pth += "?dch-uuid="
                pth += str(uuid.uuid1())
                return HttpResponseRedirect(pth)

        if age:
            policy = POLICIES[cache_type]
            policy(request, response, user, age)
        else:
            response["Cache-Control"] = "no-cache"

        return response
