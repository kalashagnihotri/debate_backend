"""
URL configuration for onlineDebatePlatform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenRefreshView
from users.jwt_views import CustomTokenObtainPairView

# API documentation schema configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Online Debate Platform API",
        default_version="v1",
        description="API documentation for the Online Debate Platform",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),
    # API documentation
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # API endpoints
    path(
        "api/v1/",
        include(
            [
                path("users/", include("users.urls")),
                path("debates/", include("debates.urls")),
                path("notifications/", include("notifications.urls")),
                # JWT Authentication endpoints
                path(
                    "token/",
                    CustomTokenObtainPairView.as_view(),
                    name="token_obtain_pair",
                ),
                path(
                    "token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
                ),
            ]
        ),
    ),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
