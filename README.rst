Django Layers
=============

.. figure:: https://travis-ci.org/hedleyroos/django-layers.svg?branch=develop
   :align: center
   :alt: Travis

   Travis

--------------

Django Layers makes it possible to serve a set of templates and
static resources as defined in ``settings.py``. This means you can serve
different HTML, Javascript and CSS to eg. basic mobile devices, smart
phones and desktop browsers. These template sets (aka layers) also
stack, so if you create ``foo.html`` for basic devices it is
automatically available for desktop browsers as well. You can override
``foo.html`` for desktop browsers.

Installation
------------

1. Install or add ``django-layers-hr`` to your Python path.
2. Add ``layers`` after ``django.contrib.static`` to your ``INSTALLED_APPS`` setting.
3. Ensure the app that you will be creating layers for appears first in
   ``INSTALLED_APPS`` else template override won't work.

Example
-------

Note: there is a working example in the ``example`` subdirectory.

We have sites example.com, basic.example.com and smart.example.com. Each
of the sites have their own ``settings.py``, thus different Django
processes.

Directory structure
^^^^^^^^^^^^^^^^^^^

::

    templates
        - basic
            - foo.html (1)
            - bar.html (2)
        - smart
            - bar.html (3)
        - web
            - bar.html (4)

    static
        - basic
            - foo.css (5)
            - bar.css (6)
        - smart
            - bar.css (7)
        - web
            - bar.css (8)

Settings
^^^^^^^^

We define an "inheritance" hierarchy using a list-of-lists notation.

Two lines of inheritance: basic-smart and basic-web::

    LAYERS = {'tree': ['basic', ['smart'], ['web']]}

One lines of inheritance: basic-smart-web.::

    LAYERS = {'tree': ['basic', ['smart', ['web']]]}

There are two ways to configure layer lookup for system: specify the current
layer in a settings file or look it up from the request. Omit the ``current``
key to enable request based lookups::

    LAYERS = {'tree': ['basic', ['smart'], ['web']], 'current': 'web'}

Legacy settings require layers to be defined in separate settings files. The example
below means we have three settings files, and thus three Django processes.
Please migrate to the default ``tree`` format.

-  Desktop settings has ``LAYERS = {'layers': ['basic', 'web']}``.
-  Basic settings has ``LAYERS = {'layers': ['basic']}``.
-  Smart settings has ``LAYERS = {'layers': ['basic', 'smart']}``.

Add the loaders and finders to settings. The order is
important.

::

    INSTALLED_APPS = (
        'myapp',
        'layers',
        ...
    )

    TEMPLATE_LOADERS = (
        'layers.loaders.filesystem.Loader',
        'django.template.loaders.filesystem.Loader',
        'layers.loaders.app_directories.Loader',
        'django.template.loaders.app_directories.Loader',
    )

    STATICFILES_FINDERS = (
        'layers.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'layers.finders.AppDirectoriesFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )

Template results
^^^^^^^^^^^^^^^^

-  http://example.com/foo yields (1).
-  http://example.com/bar yields (4).
-  http://basic.example.com/foo yields (1).
-  http://basic.example.com/bar yields (2).
-  http://smart.example.com/foo yields (1).
-  http://smart.example.com/foo yields (3).

Static results
^^^^^^^^^^^^^^

-  http://example.com/static/foo.css yields (5).
-  http://example.com/static/bar.css yields (8).
-  http://basic.example.com/static/foo.css yields (5).
-  http://basic.example.com/static/bar.css yields (6).
-  http://smart.example.com/static/foo.css yields (5).
-  http://smart.example.com/static/foo.css yields (7).

Overriding templates from other apps
------------------------------------

The normal template resolution rules apply. Creating eg.
``templates/web/registration/login.html`` will override the login page
for web only.

Collectstatic
-------------

Collectstatic remains unaffected. The collector delegates to finders, so
all layer aware resources end up with partial paths under the
``STATIC_ROOT`` directory.

Decorators
----------
A user could follow a link that leads him to a layer that serves a broken page. For example a web site
is served on www.site.com with an accompanying basic site m.site.com. Visiting www.site.com/flashy-dashboard
with a basic device like a Samsung E250 will result in the user being redirected to m.site.com/flashy-dashboard.
That page probably does not exist for basic devices because it can't render it well enough. In such a case a
decorator ``exclude_from_layers`` is provided that renders a friendly page instead of a 404 or 500 error::

    class WebOnlyView(TemplateView):
        template_name = "layers/web_only_view.html"

        @exclude_from_layers(layers=("basic",))
        def get(self, *args, **kwargs):
            return super(WebOnlyView, self).get(*args, **kwargs)

Request based layer lookup
--------------------------
The preferred way of layer lookup is through the presense of an
``X-Django-Layer`` header in the request. Django Layers layer lookup is very
similar to the site object lookup done in ``django.contrib.sites``. If a layer
is explicitly defined in settings then that is used, else the request headers
are inspected.

During development you will likely define the layer in your settings file, but
in a production environment you don't want a Django process per layer, so
request based lookups are preferred.

Layer objects
-------------
The management command `load_layers` creates a `Layer` object for each layer in
your project. It is useful for doing layer based filtering at database level.

Can I add my own layers?
------------------------
Yes! Basic, smart and web are just examples. You can define any hierarchy with
any names.

Authors
-------

-  Hedley Roos

Changelog
---------

0.2
^^^

1. Inevitable package rename.

0.1
^^^

1. Initial release.

