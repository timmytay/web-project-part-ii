from django.utils import timezone
from rest_framework.permissions import BasePermission

class SecondFactorPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        second = request.session.get('second')
        expire = request.session.get('second_expire')

        if not second or not expire:
            return False

        if timezone.now().timestamp() > expire:
            
            request.session.pop('second', None)
            request.session.pop('second_expire', None)
            return False

        return True