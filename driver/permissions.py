from rest_framework import permissions



class IsDriver(permissions.BasePermission):
    def has_permission(self, request, view):
         u = request.user

         return bool(u and u.is_authenticated and hasattr(u, "driver_profile"))
    
