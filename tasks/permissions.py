from rest_framework.permissions import BasePermission

class CanCreatePermission(BasePermission):
    message = "няв :("
    def has_permission(self, request, view):

        return request.user.has_perm('tasks.can_create')

class SecondFactorPermission(BasePermission):
    message = "няв :("
    def has_permission(self, request, view):

        return request.session.get('second') == True