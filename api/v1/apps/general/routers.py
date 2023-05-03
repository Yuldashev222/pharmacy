from rest_framework.routers import DefaultRouter

from api.v1.apps.firms.views import FirmAPIViewSet, FirmIncomeAPIViewSet
from api.v1.apps.clients.views import ClientAPIViewSet
from api.v1.apps.companies.views import CompanyAPIViewSet
from api.v1.apps.pharmacies.views import PharmacyAPIViewSet
from api.v1.apps.debts.views import debt_to_pharmacy, debt_from_pharmacy

router = DefaultRouter()

router.register('pharmacies/debts/repay', debt_to_pharmacy.DebtRepayFromPharmacyAPIView,
                basename='debt_repay_from_pharmacy')
router.register('pharmacies/to-debts/repay', debt_from_pharmacy.DebtRepayToPharmacyAPIView,
                basename='debt_repay_to_pharmacy')
router.register('pharmacies/to-debts', debt_from_pharmacy.DebtFromPharmacyAPIView, basename='debt_from_pharmacy')
router.register('pharmacies/debts', debt_to_pharmacy.DebtToPharmacyAPIView, basename='debt_to_pharmacy')

router.register('firms/incomes', FirmIncomeAPIViewSet, basename='firm_income')
router.register('firms', FirmAPIViewSet, basename='firm')

router.register('pharmacies', PharmacyAPIViewSet, basename='pharmacy')
router.register('companies', CompanyAPIViewSet, basename='company')
router.register('clients', ClientAPIViewSet, basename='client')
