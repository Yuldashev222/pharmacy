from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from api.v1.apps.accounts.routers import router as accounts_router
from api.v1.apps.pharmacies.routers import router as pharmacies_router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/accounts/', include(accounts_router.urls)),
    path('api/v1/pharmacies/', include(pharmacies_router.urls)),
    path('api/v1/wages/', include('api.v1.apps.wages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('auth/', include('rest_framework.urls'))]
