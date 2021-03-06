from django.conf.urls import include, url
from django.views.generic import TemplateView

from cache_headers.tests import views


urlpatterns = [
    url(
        r"^mylogin/$", views.mylogin, name="mylogin"
    ),
    url(
        r"^mylogout/$", views.mylogout, name="mylogout"
    ),
    url(
        r"^all-users/$",
        TemplateView.as_view(template_name="tests/view.html"),
        name="all-users"
    ),
    url(
        r"^anonymous-only/$",
        TemplateView.as_view(template_name="tests/view.html"),
        name="anonymous-only"
    ),
    url(
        r"^anonymous-and-authenticated/$",
        TemplateView.as_view(template_name="tests/view.html"),
        name="anonymous-and-authenticated"
    ),
    url(
        r"^per-user/$",
        TemplateView.as_view(template_name="tests/view.html"),
        name="per-user"
    ),
    url(
        r"^custom-policy/$",
        TemplateView.as_view(template_name="tests/view.html"),
        name="custom-policy"
    ),
    url(
        r"^home/$",
        TemplateView.as_view(template_name="tests/view.html"),
        name="home"
    )
]
