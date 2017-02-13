import datetime

from cache_headers.utils import httpdate


def custom_policy(request, response, user, age):
    if user.username == "user":
        response["X-Is-Special-User"] = 1
    else:
        response["X-Is-Special-User"] = 0
    response["Vary"] = "Accept-Encoding,X-Is-Special-User"
