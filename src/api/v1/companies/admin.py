from django.contrib import admin

from api.v1.companies.models import Company


class CompanyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


admin.site.register(Company, CompanyAdmin)
