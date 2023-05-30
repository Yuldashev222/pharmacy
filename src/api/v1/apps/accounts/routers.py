from rest_framework.routers import DefaultRouter

from api.v1.apps.expenses.views import (
    UserExpenseAPIViewSet, UserExpenseTypeAPIViewSet,
)
from .reports.views import WorkerReportAPIView, WorkerReportMontAPIView

from .views import UserReadOnlyAPIView

router = DefaultRouter()

router.register('expenses/types', UserExpenseTypeAPIViewSet, basename='user_expense_type')
router.register('expenses', UserExpenseAPIViewSet, basename='user_expense')
router.register('reports/months', WorkerReportMontAPIView, basename='user_report_month')
router.register('reports', WorkerReportAPIView, basename='user_report')
router.register('', UserReadOnlyAPIView, basename='user')
