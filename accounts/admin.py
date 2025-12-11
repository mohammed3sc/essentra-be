from django.contrib import admin
from .models import *
from django.contrib.auth.models import Group, Permission

# Register your models here.
admin.site.register(Role)
admin.site.register(UserModel)
admin.site.register(CustomPermission)
admin.site.register(Permission)
# admin.site.register(Group)
