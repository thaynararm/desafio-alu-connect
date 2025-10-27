from django.db import models
from setup.models import AbstractBaseModel
from user.models import User


class Student(AbstractBaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"profile": "STUDENT"},
        related_name="user_student",
    )
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.full_name


class StudentCertificate(AbstractBaseModel):
    student = models.ForeignKey(
        "Student", on_delete=models.CASCADE, related_name="certificates"
    )
    course = models.ForeignKey(
        "course.Course", on_delete=models.CASCADE, related_name="certificates"
    )
    file = models.ImageField(
        upload_to="certificates/", help_text="Arquivo PNG do certificado gerado"
    )
    text = models.TextField(help_text="Texto personalizado gerado pela LLM")

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Certificado de {self.student.user.full_name} - {self.course.title}"
