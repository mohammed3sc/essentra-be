from .views import *
from django.urls import path,include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'roles', RoleModelViewSet)

urlpatterns = [ 
    path('', include(router.urls)),
    # path('login/', LoginView.as_view(), name="login"),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('get-access-token/', RefreshTokenView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('edit-user/<int:pk>/', UserDetail.as_view(), name='edit-user'),
    path('edit-user/<int:pk>/', UserDetail.as_view(), name='edit-user'),
    path('reset-password/', reset_password, name='reset_password'),

]