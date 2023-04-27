from rest_framework.routers import DefaultRouter

from .views import PharmacyAPIViewSet

router = DefaultRouter()

router.register('', PharmacyAPIViewSet, basename='pharmacies')
