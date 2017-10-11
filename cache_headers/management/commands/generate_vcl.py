from __future__ import print_function

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.http.response import HttpResponse
from django.test.client import RequestFactory

from cache_headers.middleware import POLICIES, rules


TEMPLATE_A = """
sub vcl_hash {
    # Cache even with cookies present. Note we don't delete the cookies. Also,
    # we only consider cookies listed in the Hash-Cookies variable as part
    # of the hash. This list is determined by the relevant Django Cache Headers
    # policy."""

TEMPLATE_B = """
    set req.http.Hash-Value = "x";
    if (req.http.Hash-Cookies) {
        # todo: softcode these checks
        if (req.http.Hash-Cookies ~ "messages") {
            if (req.http.Cookie ~ "messages=") {
                set req.http.Hash-Value = req.http.Hash-Value + regsub(req.http.Cookie, ".*messages=([^;]+).*", "\\1");
            }
        }
        if (req.http.Hash-Cookies == "messages|isauthenticated") {
            if (req.http.Cookie ~ "isauthenticated=1") {
                set req.http.Hash-Value = req.http.Hash-Value + "1";
            }
        }
        else if (req.http.Hash-Cookies == "messages|%(sessionid)s") {
            if (req.http.Cookie ~ "%(sessionid)s=") {
                set req.http.Hash-Value = req.http.Hash-Value + regsub(req.http.Cookie, ".*%(sessionid)s=([^;]+).*", "\\1");
            }
        }
    }

    hash_data(req.http.Hash-Value);

    unset req.http.Hash-Cookies;
    unset req.http.Hash-Value;
}""" % {"sessionid": settings.SESSION_COOKIE_NAME}


class Command(BaseCommand):
    help = "Generate a Varnish VCL snippet from the cache headers settings."

    @transaction.atomic
    def handle(self, *args, **options):
        request = RequestFactory().get("/")
        response = HttpResponse()
        user = User()
        n = 0
        print(TEMPLATE_A)
        for pattern, age, cache_type, dc in rules:
            policy = POLICIES[cache_type]
            policy(request, response, user, age)
            if n == 0:
                print("if", end="")
            else:
                print("else if", end="")
            print(""" (req.url ~ "%s") {""" % pattern.pattern)
            print("""set req.http.Hash-Cookies = "%s";""" % response["X-Hash-Cookies"])
            print("}")
            n += 1
        print(TEMPLATE_B)
