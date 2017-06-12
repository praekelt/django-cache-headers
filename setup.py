import multiprocessing
from setuptools import setup, find_packages


setup(
    name="django-cache-headers",
    version="0.2",
    description="Configurable middleware to add HTTP caching headers for URL's.",
    long_description = open("README.rst", "r").read() + open("AUTHORS.rst", "r").read() + open("CHANGELOG.rst", "r").read(),
    author="Praekelt Consulting",
    author_email="dev@praekelt.com",
    license="BSD",
    url="http://github.com/praekelt/django-cache-headers",
    packages = find_packages(),
    install_requires = [
        "django",
    ],
    include_package_data=True,
    tests_require=[
        "tox",
    ],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    zip_safe=False,
)
