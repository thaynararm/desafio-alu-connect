from django.db import models
from django.utils import timezone
from setup.models import AbstractBaseModel
from user.models import User


class Instructor(AbstractBaseModel):
    user = models.OneToOneField(
        User, on_delete=models.PROTECT, limit_choices_to={"profile": "INSTRUCTOR"}, related_name='user_instructor'
    )
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.full_name
