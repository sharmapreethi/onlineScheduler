from decouple import config
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("agency/", include("service_agency.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("documentation/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if config("DEBUG", default=False, cast=bool):
    urlpatterns.append(path("_debug_/", include("debug_toolbar.urls")))
    urlpatterns.append(path("silk/", include("silk.urls", namespace="silk")))
