from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse, reverse_lazy
from django.test import TestCase


all_users = reverse_lazy("all-users")
anonymous_only = reverse_lazy("anonymous-only")
anonymous_and_authenticated = reverse_lazy("anonymous-and-authenticated")
per_user = reverse_lazy("per-user")
custom_policy = reverse_lazy("custom-policy")


class CacheMiddlewareTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(CacheMiddlewareTest, cls).setUpTestData()

        cls.user = get_user_model().objects.create(
            username="user",
            email="user@test.com"
        )
        cls.user.set_password("password")
        cls.user.save()

    def setUp(self):
        super(CacheMiddlewareTest, self).setUp()
        self.client.logout()

    def login(self):
        self.client.login(username="user", password="password")
        # Programmatic login does not do a subsequent redurect to set the
        # is_authenticated cookie. Do an extra fetch to trigger that.
        self.client.get(reverse("home"))

    def test_all_users(self):
        response = self.client.get(all_users)
        self.assertEqual(
            response._headers["cache-control"], ("Cache-Control", "max-age=100, s-maxage=600")
        )
        self.assertEqual(
            response._headers["x-accel-expires"], ("X-Accel-Expires", "600")
        )

        self.login()
        response = self.client.get(all_users)
        self.assertEqual(
            response._headers["cache-control"], ("Cache-Control", "max-age=100, s-maxage=600")
        )
        self.assertEqual(
            response._headers["x-accel-expires"], ("X-Accel-Expires", "600")
        )

    def test_anonymous_only(self):
        response = self.client.get(anonymous_only)
        self.assertEqual(
            response._headers["cache-control"], ("Cache-Control", "max-age=100, s-maxage=600")
        )
        self.assertEqual(
            response._headers["x-accel-expires"], ("X-Accel-Expires", "600")
        )
        self.assertEqual(
            response._headers["x-hash-cookies"],
            ("X-Hash-Cookies", "messages")
        )

        self.login()
        response = self.client.get(anonymous_only)
        self.assertEqual(
            response._headers["cache-control"], ("Cache-Control", "no-cache")
        )

    def test_anonymous_and_authenticated(self):
        response = self.client.get(anonymous_and_authenticated)
        self.assertEqual(
            response._headers["cache-control"], ("Cache-Control", "max-age=100, s-maxage=600")
        )
        self.assertEqual(
            response._headers["x-accel-expires"], ("X-Accel-Expires", "600")
        )
        self.assertEqual(
            response._headers["x-hash-cookies"],
            ("X-Hash-Cookies", "messages|isauthenticated")
        )

        self.login()
        response = self.client.get(anonymous_and_authenticated)
        self.assertEqual(
            response._headers["cache-control"], ("Cache-Control", "max-age=100, s-maxage=600")
        )
        self.assertEqual(
            response._headers["x-accel-expires"], ("X-Accel-Expires", "600")
        )
        self.assertEqual(
            response._headers["x-hash-cookies"],
            ("X-Hash-Cookies", "messages|isauthenticated")
        )

    def test_per_user(self):
        response = self.client.get(per_user)
        self.assertEqual(
            response._headers["cache-control"], ("Cache-Control", "max-age=100, s-maxage=600")
        )
        self.assertEqual(
            response._headers["x-accel-expires"], ("X-Accel-Expires", "600")
        )
        self.assertEqual(
            response._headers["x-hash-cookies"],
            ("X-Hash-Cookies", "messages|sessionid")
        )

        self.login()
        response = self.client.get(per_user)
        self.assertEqual(
            response._headers["cache-control"], ("Cache-Control", "max-age=100, s-maxage=600")
        )
        self.assertEqual(
            response._headers["x-accel-expires"], ("X-Accel-Expires", "600")
        )
        self.assertEqual(
            response._headers["x-hash-cookies"],
            ("X-Hash-Cookies", "messages|sessionid")
        )

    def test_custom_policy(self):
        response = self.client.get(custom_policy)
        self.assertEqual(
            response._headers["x-is-special-user"], ("X-Is-Special-User", "0")
        )
        self.failUnless("X-Is-Special-User" in response._headers["vary"][1])

        self.login()
        response = self.client.get(custom_policy)
        self.assertEqual(
            response._headers["x-is-special-user"], ("X-Is-Special-User", "1")
        )
        self.failUnless("X-Is-Special-User" in response._headers["vary"][1])

