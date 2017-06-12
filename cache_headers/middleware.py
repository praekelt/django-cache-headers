import hashlib
import logging
import re
import uuid

from django.conf import settings
from django.core.cache import cache
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

# Pre-compute sorted keys
POLICIES_KEYS = POLICIES.keys()
POLICIES_KEYS.sort()

# Compile regexes
for cache_type in TIMEOUTS.keys():
    for k, v in TIMEOUTS[cache_type].items():
        TIMEOUTS[cache_type][k] = re.compile(r"" + "|".join(v))


class CacheHeadersMiddleware(object):
    """Put this middleware before authentication middleware because response
    runs in reverse order."""

    def process_response(self, request, response):

        # Do not interfere in debug mode
        if settings.DEBUG:
            return response

        # Record whether cache control is set
        has_cache_control = False
        if ("Cache-Control" in response) or ("cache-control" in response):
            has_cache_control = True

        # Do nothing if response code is not 200
        if response.status_code != 200:
            return response

        # Default
        response["Cache-Control"] = "no-cache"

        user = getattr(request, "user", None)
        if not user:
            response["Cache-Control"] = "no-cache"
            return response

        # During login we need to be careful to not accidentally cache. The
        # isauthenticated cookie helps to determine the state.
        if user.is_authenticated() and not request.COOKIES.get("isauthenticated"):
            expires = request.session.get_expiry_date()
            response.set_cookie("isauthenticated", 1, expires=expires)
            response["Cache-Control"] = "no-cache"
            return response

        if not user.is_authenticated() and request.COOKIES.get("isauthenticated"):
            response.delete_cookie("isauthenticated")
            response["Cache-Control"] = "no-cache"
            return response

        # Never cache non-GET
        if request.method.lower() not in ("get", "head"):
            return response

        # If cache control was set at the start of this method then do nothing.
        # We only return here because isauthenticated needs opportunity to be
        # set.
        if has_cache_control:
            return response

        # Determine age and policy. Use cached lookups.
        full_path = request.get_full_path()
        key = "dch-%s" % hashlib.md5(full_path).hexdigest()
        cached = cache.get(key, None)
        if cached is not None:
            age = cached["age"]
            policy = POLICIES[cached["cache_type"]]
        else:
            age = 0
            found = False
            for cache_type in POLICIES_KEYS:
                if found:
                    break
                for key in TIMEOUTS.get(cache_type, {}).keys():
                    if TIMEOUTS[cache_type][key].match(full_path):
                        age = key
                        policy = POLICIES[cache_type]
                        found = True
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
            policy(request, response, user, age)

            # Warn on potentially erroneous usage
            if "Set-Cookie" in response:
                logger = logging.getLogger("django")
                logger.warn(
                    "Caching path %s but Set-Cookie is on the response" \
                        % full_path
                )
        else:
            response["Cache-Control"] = "no-cache"

        return response
