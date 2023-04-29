from rest_framework.routers import DefaultRouter

from .views import CompanyAPIViewSet

router = DefaultRouter()

router.register('', CompanyAPIViewSet, basename='company')
