from rest_framework.routers import DefaultRouter

from api.v1.apps.expenses.views import UserExpenseAPIViewSet
from api.v1.apps.accounts.reports import (
    WorkerReportAPIView,
    WorkerReportMontAPIView,
    WorkerReportMontExcelAPIView,
    WorkerReportExcelAPIView
)
from .views import UserReadOnlyAPIView

router = DefaultRouter()

router.register('expenses', UserExpenseAPIViewSet, basename='user_expense')
router.register('reports/months/downloads/excel', WorkerReportMontExcelAPIView, basename='user_report_month_excel')
router.register('reports/downloads/excel', WorkerReportExcelAPIView, basename='user_report_excel')
router.register('reports/months', WorkerReportMontAPIView, basename='user_report_month')
router.register('reports', WorkerReportAPIView, basename='user_report')
router.register('', UserReadOnlyAPIView, basename='user')
