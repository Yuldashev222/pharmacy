from datetime import date
from rest_framework import permissions


class IsTodayDateReport(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.report.report_date == date.today()
