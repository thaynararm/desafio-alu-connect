from rest_framework import viewsets, permissions
from student.models import Student
from student.serializers import StudentSerializer
from setup.utils.custom_permissions import IsAdmin, IsStudentOrAdmin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from course.serializers import *
from course.models import *


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    authentication_classes = [JWTAuthentication]
    lookup_field = "uuid"

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsAdmin]
        else:
            permission_classes = [IsStudentOrAdmin]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.profile == "ADMIN":
            return Student.objects.all()
        elif user.profile == "MEMBER":
            return Student.objects.filter(user=user)
        return Student.objects.none()

    @action(
        detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def courses(self, request, uuid=None):
        student = self.get_object()
        courses = student.courses.filter(is_active=True)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        url_path="progress",
        permission_classes=[permissions.IsAuthenticated],
    )
    def progress(self, request, uuid=None):
        student = self.get_object()
        progresses = StudentProgress.objects.filter(student=student)
        serializer = StudentProgressSerializer(progresses, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        url_path="courses/(?P<course_uuid>[^/.]+)/progress",
        permission_classes=[permissions.IsAuthenticated],
    )
    def course_progress(self, request, uuid=None, course_uuid=None):
        student = self.get_object()
        try:
            progress = StudentProgress.objects.get(
                student=student, course__uuid=course_uuid
            )
        except StudentProgress.DoesNotExist:
            return Response({"detail": "Progresso não encontrado."}, status=404)

        completed_lessons = progress.completed_lessons.all()
        completed_data = [
            {"uuid": l.uuid, "title": l.title, "order": l.order}
            for l in completed_lessons
        ]

        return Response(
            {
                "student": student.user.full_name,
                "course": progress.course.title,
                "status": progress.status,
                "completed_lessons": completed_data,
            }
        )
