from rest_framework import viewsets, permissions
from instructor.models import Instructor
from instructor.serializers import InstructorSerializer
from setup.utils.custom_permissions import IsAdmin, IsInstructorOrAdmin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from course.models import Course
from course.serializers import CourseSerializer
from rest_framework.response import Response


class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    authentication_classes = [JWTAuthentication]
    lookup_field = "uuid"

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsAdmin]
        else:
            permission_classes = [IsInstructorOrAdmin]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.profile == "ADMIN":
            return Instructor.objects.all()
        elif user.profile == "MEMBER":
            return Instructor.objects.filter(user=user)
        return Instructor.objects.none()

    @action(
        detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def courses(self, request, uuid=None):
        instructor = self.get_object()
        courses = Course.objects.filter(instructors=instructor)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
