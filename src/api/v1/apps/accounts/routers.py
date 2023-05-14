from rest_framework.routers import DefaultRouter

from api.v1.apps.expenses.views import (
    UserExpenseAPIViewSet, UserExpenseTypeAPIViewSet,
)

from .views import UserReadOnlyAPIView

router = DefaultRouter()

router.register('expenses/types', UserExpenseTypeAPIViewSet, basename='user_expense_type')
router.register('expenses', UserExpenseAPIViewSet, basename='user_expense')
router.register('', UserReadOnlyAPIView, basename='user')
