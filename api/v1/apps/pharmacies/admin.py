from django.contrib import admin

from .models import Pharmacy


@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'company']
    list_display_links = list_display
