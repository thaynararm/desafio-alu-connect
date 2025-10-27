from django.db import models
from setup.models import AbstractBaseModel
from instructor.models import Instructor
from student.models import Student
from django.utils import timezone


class Course(AbstractBaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    instructors = models.ManyToManyField(Instructor, related_name="courses")
    students = models.ManyToManyField(Student, related_name="courses")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Lesson(AbstractBaseModel):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="lessons")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField()
    content_url = models.URLField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "order"], name="unique_order_per_course"
            )
        ]

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class StudentProgress(AbstractBaseModel):
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='progress')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='student_progress')
    completed_lessons = models.ManyToManyField(Lesson, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.user.username} - {self.course.title} ({self.status})"

    def mark_lesson_completed(self, lesson):
        if self.status == 'COMPLETED':
            raise ValueError("Não é possível alterar o progresso de um curso concluído.")
        if lesson.course != self.course:
            raise ValueError("A aula não pertence a este curso.")
        self.completed_lessons.add(lesson)
        # verifica se todas as aulas do curso foram concluídas
        if self.completed_lessons.count() == self.course.lessons.filter(is_active=True).count():
            self.status = 'COMPLETED'
            self.completed_at = timezone.now()
        self.save()