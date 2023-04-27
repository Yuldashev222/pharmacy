from rest_framework.routers import DefaultRouter

from .views import UserReadOnlyModelAPIViewSet

router = DefaultRouter()

router.register('', UserReadOnlyModelAPIViewSet)
