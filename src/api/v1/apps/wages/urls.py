from django.urls import path, include

from .views import wage_list

urlpatterns = [
    path('', wage_list, name='wage-list')
]

