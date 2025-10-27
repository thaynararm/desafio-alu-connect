from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import User
from user.serializers import UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from setup.utils.custom_permissions import *


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Atualiza o último acesso no momento do login
        self.user.last_login = timezone.now()
        self.user.save(update_fields=["last_login"])
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication] 
    lookup_field = "uuid"

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        if self.action in ["retrieve", "update", "partial_update"]:
            print('aqui')
            return [IsAdminOrInstructorOrStudent()]
        if self.action in ["list", "destroy"]:
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]
    