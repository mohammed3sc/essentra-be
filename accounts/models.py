from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser,Group, Permission


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    permissions = models.ManyToManyField(Permission)

    def __str__(self):
        return self.name
    class Meta:
        # managed = False
        db_table = 'roles'

class CustomPermission(models.Model):
    permission = models.OneToOneField(Permission, on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return self.permission.name
    
    class Meta:
        # managed = False
        db_table = 'custom_permission'

class UserModel(AbstractUser):
    phone_no=models.IntegerField(null=True,blank=True)
    # profile_img=models.ImageField(upload_to='profile_images',null=True,blank=True)
    roles = models.ManyToManyField(Role, blank=True)
    class Meta:
        # managed = False
        db_table = 'user'
    




        
