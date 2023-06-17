from django.contrib import admin
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.contrib.auth.models import Group

from .enums import UserRole
from .models import CustomUser

admin.site.unregister([OutstandingToken, BlacklistedToken, Group])


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone_number', 'date_joined']
    search_fields = ['first_name', 'last_name', 'phone_number']
    list_display_links = list_display

    fields = ['first_name', 'last_name', 'phone_number', 'password', 'is_active']

    def save_model(self, request, obj, form, change):
        password = make_password(obj.password)
        if not obj.id:
            obj.password = password
        elif obj.password != CustomUser.objects.get(id=obj.id).password:
            obj.password = password
        obj.creator_id = request.user.id
        obj.role = UserRole.d.name
        obj.save()
