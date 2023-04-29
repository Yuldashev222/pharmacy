from rest_framework.routers import DefaultRouter

from .views import DirectorAPIViewSet

router = DefaultRouter()

router.register('directors', DirectorAPIViewSet, basename='director')
