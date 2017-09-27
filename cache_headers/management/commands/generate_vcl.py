from __future__ import print_function

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.http.response import HttpResponse
from django.test.client import RequestFactory
from cache_headers.middleware import POLICIES, rules


class Command(BaseCommand):
    help = "Generate a Varnish VCL snippet from the cache headers settings."

    @transaction.atomic
    def handle(self, *args, **options):
        request = RequestFactory().get("/")
        response = HttpResponse()
        user = User()
        n = 0
        for pattern, age, cache_type, dc in rules:
            policy = POLICIES[cache_type]
            policy(request, response, user, age)
            if n == 0:
                print("if", end="")
            else:
                print ("else if", end="")
            print(""" (req.url ~ "%s") {""" % pattern.pattern)
            print("""set req.http.Hash-Cookies = "%s";""" % response["X-Hash-Cookies"])
            print("}")
            n += 1
