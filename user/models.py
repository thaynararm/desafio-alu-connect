from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from setup.models import AbstractBaseModel


@receiver(user_logged_in)
def update_last_login(sender, request, user, **kwargs):
    user.last_login = timezone.now()
    user.save(update_fields=["last_login"])


class CustomUserManager(BaseUserManager):
    def create_user(
        self,
        email,
        username,
        full_name,
        birth_date,
        cpf,
        profile,
        password=None,
        **extra_fields,
    ):
        if not email:
            raise ValueError("O email é obrigatório.")
        if not username:
            raise ValueError("O username é obrigatório.")
        if not full_name:
            raise ValueError("O nome completo é obrigatório.")
        if not birth_date:
            raise ValueError("A data de nascimento é obrigatória.")
        if not cpf:
            raise ValueError("O CPF é obrigatório.")
        if not profile:
            raise ValueError("O perfil é obrigatório (ADMIN, INSTRUCTOR ou STUDENT).")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            full_name=full_name,
            birth_date=birth_date,
            cpf=cpf,
            profile=profile,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, username, full_name, birth_date, cpf, password=None, **extra_fields
    ):
        extra_fields.setdefault("profile", "ADMIN")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusuário deve ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusuário deve ter is_superuser=True.")

        return self.create_user(
            email,
            username,
            full_name,
            birth_date,
            cpf,
            "ADMIN",
            password,
            **extra_fields,
        )


class User(AbstractBaseUser, PermissionsMixin, AbstractBaseModel):
    PROFILE_CHOICES = [
        ("ADMIN", "Administrator"),
        ("MEMBER", "Member")
    ]

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    birth_date = models.DateField()
    cpf = models.CharField(max_length=11, unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    profile = models.CharField(max_length=12, choices=PROFILE_CHOICES)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "full_name", "birth_date", "cpf"]

    def __str__(self):
        return f"{self.username} ({self.get_profile_display()})"
