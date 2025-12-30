from acts.views import register_view
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register/", register_view, name="register"),
    path("", include("acts.urls")),
]
