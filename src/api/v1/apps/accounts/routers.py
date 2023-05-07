from rest_framework.routers import DefaultRouter

from api.v1.apps.expenses.views import (
    UserExpenseAPIViewSet,
)

from .views import UserReadOnlyAPIView

router = DefaultRouter()

router.register('expenses', UserExpenseAPIViewSet, basename='user_expense')
router.register('', UserReadOnlyAPIView, basename='user')
