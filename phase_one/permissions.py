from rest_framework.permissions import BasePermission

class CustomDynamicPermission(BasePermission):
    """
    Custom permission that accepts dynamic permissions.
    """

    def __init__(self, allowed_permissions):
        self.allowed_permissions = allowed_permissions
        print(self.allowed_permissions ,"=======================________________________")
    def has_permission(self, request, view):
        user_permission_list = []
        if request.user.is_authenticated:
            for role in request.user.roles.all():
                for perm in role.permissions.all():
                    user_permission_list.append(perm.name)
            return any(permission in user_permission_list for permission in self.allowed_permissions)
        return False
    
    def __call__(self):
        return self 


# from django.contrib.auth.backends import BaseBackend
# from django.contrib.auth.models import Permission

# class CustomPermissionBackend(BaseBackend):
#     def get_permissions(self, user_obj, obj=None):
#         if not hasattr(user_obj, '_perm_cache'):
#             user_obj._perm_cache = set()
#             roles = user_obj.roles.all()  # Assuming UserModel has a 'roles' ManyToManyField
#             for role in roles:
#                 permissions = role.permissions.all()
#                 user_obj._perm_cache.update(permissions)
#         return user_obj._perm_cache

#     def has_perm(self, user_obj, perm, obj=None):
#         if not hasattr(user_obj, '_perm_cache'):
#             self.get_permissions(user_obj)
#         return perm in user_obj._perm_cache
