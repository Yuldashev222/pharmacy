from django.urls import path
from drf_yasg import openapi
from rest_framework import permissions
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title='Pharmacy API\'s',
        default_version='v1',
        description='Pharmacy test API\'s for frontend and mobile app',
        license=openapi.License(name='BSD Licence'),
    ),
    public=True,
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]
)

urlpatterns = [
    path(r'swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(r'redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
]
