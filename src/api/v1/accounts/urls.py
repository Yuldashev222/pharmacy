from django.urls import path, include
from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework_simplejwt.views import TokenObtainPairView

from . import views

from .routers import router

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

    path('directors/create/', views.DirectorCreateAPIView.as_view()),
    path('managers/create/', views.ManagerCreateAPIView.as_view()),
    path('workers/create/', views.WorkerCreateAPIView.as_view()),

    path('directors/<int:pk>/', views.DirectorUpdateDestroyAPIView.as_view()),
    path('managers/<int:pk>/', views.ManagerUpdateDestroyAPIView.as_view()),
    path('workers/<int:pk>/', views.WorkerUpdateDestroyAPIView.as_view()),

    path('profile/', views.OwnerRetrieveUpdateAPIView.as_view(), name='profile'),
    path('', include(router.urls)),
]

