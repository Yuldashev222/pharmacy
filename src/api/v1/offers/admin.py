from django.contrib import admin

from .models import Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'created_at', 'text']
    search_fields = ['title', 'text']
    # list_filter = ['status', 'answered_at']
    list_display_links = list_display

    # readonly_fields = ['creator', 'status', 'title', 'text', 'answered_at']
    # fields = ['creator', 'status', 'title', 'text']
