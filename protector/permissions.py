from rest_framework import permissions



class IsProtector(permissions.BasePermission):
    def has_permission(self, request, view):
         u = request.user

         return bool(u and u.is_authenticated and hasattr(u, "protector_profile"))
    
