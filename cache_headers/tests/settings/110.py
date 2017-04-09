import os
import glob

from cache_headers.tests.policies import custom_policy


BASE_DIR = os.path.join(
    glob.glob(os.environ["VIRTUAL_ENV"] +  "/lib/*/site-packages")[0],
    "cache_headers"
)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "cache_headers.db"
    }
}

ROOT_URLCONF = "cache_headers.tests.urls"

INSTALLED_APPS = (
    "cache_headers",
    "cache_headers.tests",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
)

SECRET_KEY = "SECRET_KEY"

MIDDLEWARE_CLASSES = (
    "cache_headers.middleware.CacheHeadersMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
        ],
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ]
        },
    },
]

CACHE_HEADERS = {
    "policies": {"custom-policy": custom_policy},
    "timeouts": {
        "all-users": {
            600: (
                "^/all-users/",
            )
        },
        "anonymous-only": {
            600: (
                "^/anonymous-only/",
            )
        },
        "anonymous-and-authenticated": {
            600: (
                "^/anonymous-and-authenticated/",
            )
        },
        "per-user": {
            600: (
                "^/per-user/",
            )
        },
        "custom-policy": {
            600: (
                "^/custom-policy/",
            )
        }
    }
}
