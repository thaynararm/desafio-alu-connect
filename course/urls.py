from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from course.views import CourseViewSet, LessonViewSet

router = routers.DefaultRouter()
router.register(r"", CourseViewSet, basename="course")

courses_router = nested_routers.NestedDefaultRouter(router, r"", lookup="course")
courses_router.register(r"lessons", LessonViewSet, basename="course-lessons")


urlpatterns = [
    path("", include(router.urls)),
    path("", include(courses_router.urls)),
]
