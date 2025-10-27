from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from course.models import *
from course.serializers import *
from setup.utils.custom_permissions import *
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from course.tasks import generate_certificate

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [JWTAuthentication]
    lookup_field = "uuid"

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsInstructorOrAdmin]
        else:
            permission_classes = [permissions.AllowAny]
        return [perm() for perm in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Course.objects.filter(is_active=True)

        if user.profile == "ADMIN":
            return Course.objects.all()
        if hasattr(user, "user_instructor"):
            courses = Course.objects.filter(instructors__user=user)
            if not courses.exists():
                raise PermissionDenied(
                    "O curso informado não está disponível para este instrutor."
                )
            return courses
        if hasattr(user, "user_student"):
            return Course.objects.filter(is_active=True)
        return Course.objects.none()

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def enroll(self, request, uuid=None):
        course_uuid = uuid or self.kwargs.get("uuid")
        try:
            course = Course.objects.get(uuid=course_uuid)
        except Course.DoesNotExist:
            return Response(
                {"detail": "Curso não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        user = request.user

        if user.profile == "ADMIN":
            data = request.data
            student_uuid = data.get("uuid_student")

            if not student_uuid:
                return Response(
                    {
                        "detail": "Insira o campo 'uuid_student' para inscrever um aluno."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                student = Student.objects.get(uuid=student_uuid)
            except Student.DoesNotExist:
                return Response(
                    {
                        "detail": "O student com uuid informado não está cadastrado no banco."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        elif hasattr(user, "user_student"):
            student = user.user_student

        else:
            return Response(
                {"detail": "Apenas alunos podem se inscrever."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if course.students.filter(id=student.id).exists():
            return Response(
                {"detail": "O aluno já está matriculado neste curso."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        course.students.add(student)
        course.save()

        return Response(
            {"detail": "Inscrição realizada com sucesso."},
            status=status.HTTP_200_OK,
        )


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    authentication_classes = [JWTAuthentication]
    lookup_field = "uuid"

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsInstructorOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [perm() for perm in permission_classes]

    def get_queryset(self):
        user = self.request.user
        course_uuid = self.kwargs.get("course_uuid")
        base_qs = Lesson.objects.all()

        if course_uuid:
            base_qs = base_qs.filter(course__uuid=course_uuid)

        if not user.is_authenticated:
            return base_qs.filter(course__is_active=True, is_active=True)

        if user.profile == "ADMIN":
            return base_qs
        if hasattr(user, "user_instructor"):
            lessons = base_qs.filter(course__instructors__user=user)
            if not lessons.exists():
                raise PermissionDenied(
                    "O curso informado não está disponível para este instrutor."
                )
            return lessons
        if hasattr(user, "user_student"):
            return base_qs.filter(course__is_active=True, is_active=True)

        return Lesson.objects.none()

    def perform_create(self, serializer):
        course_uuid = self.kwargs.get("course_uuid")
        course = Course.objects.get(uuid=course_uuid)
        user = self.request.user

        if (
            hasattr(user, "user_instructor")
            and not course.instructors.filter(user=user).exists()
        ):
            raise PermissionDenied(
                "Usuário não tem permissão para criar aula neste curso."
            )

        try:
            serializer.save(course=course)
        except IntegrityError as e:
            if "unique_order_per_course" in str(e):
                raise serializers.ValidationError(
                    {"order": "Já existe uma aula com essa ordem neste curso."}
                )
            raise e

    @action(
        detail=True,
        methods=["post"],
        url_path="progress",
        permission_classes=[permissions.IsAuthenticated],
    )
    def mark_progress(self, request, course_uuid=None, uuid=None):
        user = request.user
        if user.profile == "ADMIN":
            student_uuid = request.data.get("uuid_student")
            if not student_uuid:
                return Response(
                    {"detail": "Insira o campo 'uuid_student' para marcar o progresso de um aluno."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                student = Student.objects.get(uuid=student_uuid)
            except Student.DoesNotExist:
                return Response(
                    {"detail": "O student com uuid informado não está cadastrado no banco."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        elif hasattr(user, "user_student"):
            student = user.user_student
        else:
            return Response(
                {"detail": "Apenas alunos podem marcar progresso."},
                status=status.HTTP_403_FORBIDDEN,
            )

        course = get_object_or_404(Course, uuid=course_uuid)
        lesson = get_object_or_404(Lesson, uuid=uuid, course=course)

        progress, _ = StudentProgress.objects.get_or_create(
            student=student,
            course=course,
            defaults={"status": "IN_PROGRESS"},
        )
        try:
            progress.mark_lesson_completed(lesson)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        all_lessons = course.lessons.filter(is_active=True)
        completed_lessons = progress.completed_lessons.all()

        response_detail = f"Aula '{lesson.title}' marcada como concluída."

        if set(all_lessons) == set(completed_lessons):
            generate_certificate.delay(student.id, course.id)
            response_detail += " Parabéns! Todas as aulas foram concluídas. O certificado está sendo gerado."

        return Response(
            {"detail": response_detail},
            status=status.HTTP_200_OK,
        )
