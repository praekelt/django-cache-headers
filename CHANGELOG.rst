Changelog
=========

0.4
---
#. Django 2.0 and Python 3 compatibility. Django 1.9 support has been dropped.

0.3.3
-----
#. Fix anonymous-only policy to consider isauthenticated cookie.

0.3.2
-----
#. Ensure isauthenticated cookie expires at end of session if session is set to do so.

0.3.1
-----
#. An anonymous user may in fact have a session. Handle this case gracefully.

0.3
---
#. Added vcl generation management command, to be used in tandem with varnish. sample.vcl updated to reflect usage.
#. Make use of on_user_auth_event to ensure no-cache header is set during login and logout.
#. Extra protection against tampered session cookie.
#. Policies no longer makes an assumption on the session cookie name.

0.2.2
-----
#. Iterate over regexes in order of most specific (longest) to least specific (shortest).
#. Revert OrderedDict change since it is not required anymore due to the above change.

0.2.1
-----
#. Use an OrderedDict for guaranteed policy iteration order.

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

