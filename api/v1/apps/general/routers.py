from rest_framework.routers import DefaultRouter

from api.v1.apps.firms.views import FirmAPIViewSet
from api.v1.apps.clients.views import ClientAPIViewSet
from api.v1.apps.companies.views import CompanyAPIViewSet
from api.v1.apps.pharmacies.views import PharmacyAPIViewSet

router = DefaultRouter()

router.register('firms', FirmAPIViewSet, basename='firm')
router.register('pharmacies', PharmacyAPIViewSet, basename='pharmacy')
router.register('companies', CompanyAPIViewSet, basename='company')
router.register('clients', ClientAPIViewSet, basename='client')
