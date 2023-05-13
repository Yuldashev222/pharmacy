from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from api.v1.apps.general.routers import router
from api.v1.apps.general.views import company_details

from .yasg import urlpatterns as doc_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/wages/', include('api.v1.apps.wages.urls')),
    path('api/v1/accounts/', include('api.v1.apps.accounts.urls')),
    path('api/v1/', include(router.urls)),
    path('api/v1/companies/details', company_details, name='company-details'),
]

urlpatterns += doc_urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('auth/', include('rest_framework.urls'))]