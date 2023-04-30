from rest_framework import permissions

from .enums import UserRole


class IsDirectorOrOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == UserRole.d.name or request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.director_id or request.method in permissions.SAFE_METHODS


class IsProjectOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == UserRole.p.name


class NotProjectOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role != UserRole.p.name


class IsDirector(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == UserRole.d.name


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == UserRole.m.name


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id
