from django.contrib import admin

from .models import Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['creator', 'created_at', 'text']
    search_fields = ['title', 'text']
    # list_filter = ['status', 'answered_at']
    list_display_links = list_display

    readonly_fields = ['creator', 'status', 'title', 'text', 'answered_at']
    fields = ['text', 'creator', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
