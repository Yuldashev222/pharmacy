from rest_framework.routers import DefaultRouter

from .views import UserReadOnlyAPIView

router = DefaultRouter()

router.register('', UserReadOnlyAPIView, basename='user')
