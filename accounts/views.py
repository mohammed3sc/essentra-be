from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import generics
from .models import UserModel
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            
            # Convert days and hours to minutes
            refresh_token_expiry_minutes = refresh.lifetime.total_seconds() / 60
            access_token_expiry_minutes = refresh.access_token.lifetime.total_seconds() / 60

            return Response({
                "id":user.id,
                "username":user.username,
                "roles":[role.name for role in user.roles.all()],
                # "profile":user.profile_img.url,
                "permissions":[perm.name for role in user.roles.all() for perm in role.permissions.all()],
                 
                'refresh_token': str(refresh),
                'refresh_token_expiry_minutes': str(refresh_token_expiry_minutes),
                'access_token': str(refresh.access_token),
                'access_token_expiry_minutes': str(access_token_expiry_minutes)
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

class RefreshTokenView(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh = serializer.validated_data['refresh_token']
        try:
            new_access_token = RefreshToken(refresh).access_token
            lifetime_seconds = RefreshToken(refresh).access_token.lifetime.total_seconds()
            expire_time_minutes = lifetime_seconds / 60
        except Exception as e:
            return Response({"message":str(e)})
        return Response({'access_token': str(new_access_token), "access_token_expiry": expire_time_minutes}, status=status.HTTP_200_OK)

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.parsers import MultiPartParser, FormParser

# class UserDetail(generics.RetrieveUpdateAPIView):
#     authentication_classes = [JWTAuthentication]
#     # permission_classes = [IsAuthenticated]
#     permission_classes = (AllowAny,)
#     queryset = UserModel.objects.all()
#     serializer_class = EditUserSerializer

class UserDetail(generics.RetrieveUpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    queryset = UserModel.objects.all()
    serializer_class = EditUserSerializer
    parser_classes = (MultiPartParser, FormParser)  # Allow file uploads

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        profile_img=request.data.get('profile_img')
        roles=request.data.get('roles')
        print(request.data)
        print(profile_img,"==========",type(profile_img))
        if profile_img and profile_img != 'null':
            print("inside if -----------")
            instance.profile_img=profile_img
            instance.save()
        else:
            print("inside else")
            instance.profile_img=instance.profile_img
            instance.save()
            
        if roles:
            print("inside if roles ----------------------")
            instance.roles.clear()
            for role in roles.split(','):
                role_inst = Role.objects.get(name=role)
                instance.roles.add(role_inst)
        if not roles:
            print("inside not roles---------------")
            instance.roles.clear()
            
        data = request.data.copy()
        data.pop('profile_img')
        data.pop('roles')
        print(data,"-------------data")
        for field, value in data.items():
            setattr(instance, field, value)
        instance.save()
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        # self.perform_update(serializer)
        return Response(serializer.data)


# from rest_framework import status
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework.decorators import api_view, permission_classes

# @api_view(['PUT'])
# @permission_classes([AllowAny])
# def update_profile_image(request, pk):
#     try:
#         user_profile = UserModel.objects.get(id=pk)
#     except UserModel.DoesNotExist:
#         return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

#     serializer = EditUserSerializer(user_profile, data=request.data)
#     user_profile.profile_img=request.data.get('profile_image')
#     user_profile.save()
    
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoleModelViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            new_password = data.get('new_password')

            if not username or not new_password:
                return JsonResponse({"message": "Username and new password are required."}, status=400)

            try:
                user = UserModel.objects.get(username=username)
                user.set_password(new_password)
                user.save()
                return JsonResponse({"message": "Password reset successfully."}, status=200)
            except User.DoesNotExist:
                return JsonResponse({"message": "User does not exist."}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format."}, status=400)
    return JsonResponse({"message": "Invalid request method."}, status=405)
