from rest_framework import permissions


# class IsDirectorOrOwnerOrReadOnly(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_director or request.method in permissions.SAFE_METHODS
#
#     def has_object_permission(self, request, view, obj):
#         return request.user.id == obj.director_id or request.method in permissions.SAFE_METHODS


class IsProjectOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_project_owner


class NotProjectOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_project_owner


class IsDirector(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_director


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_manager


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id
