from rest_framework.routers import DefaultRouter

from api.v1.apps.firms.views import (
    FirmAPIViewSet, FirmIncomeAPIViewSet, FirmExpenseAPIViewSet, FirmExpenseVerify, FirmReturnProductAPIViewSet,
    FirmReturnProductVerify
)
from api.v1.apps.drugs.views import DrugAPIViewSet
from api.v1.apps.debts.views import debt_from_pharmacy, debt_to_pharmacy
from api.v1.apps.firms.report import FirmReportAPIView, FirmDebtByDateAPIView, FirmDebtByMonthAPIView
from api.v1.apps.clients.views import ClientAPIViewSet
from api.v1.apps.incomes.views import PharmacyIncomeAPIViewSet
from api.v1.apps.receipts.views import ReceiptCreateUpdateAPIView
from api.v1.apps.incomes.report import PharmacyIncomeReportDayAPIView, PharmacyIncomeReportMonthAPIView
from api.v1.apps.expenses.views import PharmacyExpenseAPIViewSet, ExpenseTypeAPIViewSet
from api.v1.apps.pharmacies.views import PharmacyAPIViewSet
from api.v1.apps.expenses.reports.views import ExpenseAPIView, ExpenseReportMonthAPIView

from .reports.incomes import AllPharmacyIncomeReportMonthAPIView
from .reports.expenses import AllExpenseReportMonthAPIView
from .views import TransferMoneyTypeAPIViewSet, CompanyAPIViewSet

router = DefaultRouter()

router.register('pharmacies/debts/not-pagination', debt_to_pharmacy.TodayDebtToPharmacyAPIView, basename='today_debt_to_pharmacy')
router.register('pharmacies/debts/repay', debt_to_pharmacy.DebtRepayFromPharmacyAPIView, basename='debt_repay_from_pharmacy')
router.register('pharmacies/debts', debt_to_pharmacy.DebtToPharmacyAPIView, basename='debt_to_pharmacy')

router.register('pharmacies/to-debts/not-pagination', debt_from_pharmacy.TodayDebtFromPharmacyAPIView, basename='today_debt_from_pharmacy')
router.register('pharmacies/to-debts/repay', debt_from_pharmacy.DebtRepayToPharmacyAPIView, basename='debt_repay_to_pharmacy')
router.register('pharmacies/to-debts', debt_from_pharmacy.DebtFromPharmacyAPIView, basename='debt_from_pharmacy')

router.register('pharmacies/expenses/reports/months', ExpenseReportMonthAPIView, basename='pharmacy_expense_report_months')
router.register('pharmacies/expenses/reports', ExpenseAPIView, basename='pharmacy_expense_report')
router.register('pharmacies/expenses/types', ExpenseTypeAPIViewSet, basename='expense_type')
router.register('pharmacies/expenses', PharmacyExpenseAPIViewSet, basename='pharmacy_expense')

router.register('pharmacies/incomes/reports/days', PharmacyIncomeReportDayAPIView, basename='pharmacy_income_report_day')
router.register('pharmacies/incomes/reports/months', PharmacyIncomeReportMonthAPIView, basename='pharmacy_income_report_month')
router.register('pharmacies/incomes', PharmacyIncomeAPIViewSet, basename='pharmacy_income')

router.register('pharmacies/receipts', ReceiptCreateUpdateAPIView, basename='pharmacy_receipt')
router.register('pharmacies', PharmacyAPIViewSet, basename='pharmacy')

router.register('firms/reports/months', FirmDebtByMonthAPIView, basename='firm_report_month')
router.register('firms/reports', FirmReportAPIView, basename='firm_report')
router.register('firms/expenses/verify', FirmExpenseVerify, basename='firm_expense_verify')
router.register('firms/returns/verify', FirmReturnProductVerify, basename='firm_return_verify')
router.register('firms/returns', FirmReturnProductAPIViewSet, basename='firm_return')
router.register('firms/expenses', FirmExpenseAPIViewSet, basename='firm_expense')
router.register('firms/incomes', FirmIncomeAPIViewSet, basename='firm_income')
router.register('firms/debts', FirmDebtByDateAPIView, basename='firm_debt')
router.register('firms', FirmAPIViewSet, basename='firm')

router.register('companies/reports/expenses', AllExpenseReportMonthAPIView, basename='company_expense_report')
router.register('companies/reports/incomes', AllPharmacyIncomeReportMonthAPIView, basename='company_income_report')
router.register('companies', CompanyAPIViewSet, basename='company')

router.register('clients', ClientAPIViewSet, basename='client')
router.register('drugs', DrugAPIViewSet, basename='drug')
router.register('transfers/types', TransferMoneyTypeAPIViewSet, basename='transfer_type')
