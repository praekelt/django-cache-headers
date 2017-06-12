Changelog
=========

0.2
---
#. Ignoring cookies completely when setting headers turned out to be a mistake due to too many security concerns. Restore them.

0.1.3
-----
#. Handle case where user may also be logged in and a cookie not being set.

0.1.2
-----
#. Use the s-maxage header for compatability with Varnish.

0.1.1
-----
#. Leave response untouched if status code is not 200.

0.1
---
#. Initial release.

