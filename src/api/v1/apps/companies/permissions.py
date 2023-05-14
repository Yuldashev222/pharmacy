from datetime import date
from rest_framework import permissions


class WorkerTodayObject(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.shift == obj.shift and obj.report_date == date.today()
