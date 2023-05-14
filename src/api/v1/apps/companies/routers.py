from rest_framework.routers import DefaultRouter

from api.v1.apps.clients.views import ClientAPIViewSet
from api.v1.apps.drugs.views import DrugAPIViewSet
from api.v1.apps.pharmacies.views import PharmacyAPIViewSet
from api.v1.apps.expenses.views import PharmacyExpenseAPIViewSet, PharmacyExpenseTypeAPIViewSet
from api.v1.apps.debts.views import debt_from_pharmacy, debt_to_pharmacy
from api.v1.apps.incomes.views import PharmacyIncomeAPIViewSet
from api.v1.apps.firms.views import (
    FirmAPIViewSet, FirmIncomeAPIViewSet, FirmFromPharmacyExpenseAPIViewSet,
    FirmFromDebtExpenseAPIViewSet, FirmExpenseVerify
)

from .views import TransferMoneyTypeAPIViewSet, CompanyAPIViewSet

router = DefaultRouter()

router.register('pharmacies/debts/repay', debt_to_pharmacy.DebtRepayFromPharmacyAPIView,
                basename='debt_repay_from_pharmacy')
router.register('pharmacies/to-debts/repay', debt_from_pharmacy.DebtRepayToPharmacyAPIView,
                basename='debt_repay_to_pharmacy')

router.register('pharmacies/to-debts', debt_from_pharmacy.DebtFromPharmacyAPIView, basename='debt_from_pharmacy')
router.register('pharmacies/debts', debt_to_pharmacy.DebtToPharmacyAPIView, basename='debt_to_pharmacy')

router.register('pharmacies/incomes', PharmacyIncomeAPIViewSet, basename='pharmacy_income')

router.register('pharmacies/expenses/types', PharmacyExpenseTypeAPIViewSet, basename='pharmacy_expense_type')
router.register('pharmacies/expenses', PharmacyExpenseAPIViewSet, basename='pharmacy_expense')

router.register('pharmacies', PharmacyAPIViewSet, basename='pharmacy')

router.register('firms/expenses/verify', FirmExpenseVerify, basename='firm_expense_verify')
router.register('firms/expenses/from-pharmacies', FirmFromPharmacyExpenseAPIViewSet,
                basename='firm_expense_from_pharmacy')
router.register('firms/expenses/from-debt', FirmFromDebtExpenseAPIViewSet, basename='firm_expense_from_debt')
router.register('firms/incomes', FirmIncomeAPIViewSet, basename='firm_income')
router.register('firms', FirmAPIViewSet, basename='firm')

router.register('companies', CompanyAPIViewSet, basename='company')
router.register('clients', ClientAPIViewSet, basename='client')
router.register('drugs', DrugAPIViewSet, basename='drug')

router.register('transfers/types', TransferMoneyTypeAPIViewSet, basename='transfer_type')
