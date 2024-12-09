from django.apps import apps
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("example/", include("example.urls")),
    path("pyhub-ai/", include("pyhub_ai.urls")),
    path("", RedirectView.as_view(url="/example/")),
]

# check app install
if apps.is_installed("debug_toolbar"):
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
