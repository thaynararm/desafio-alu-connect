from django.urls import path, include
from rest_framework import routers
from instructor.views import InstructorViewSet

router = routers.DefaultRouter()
router.register(r"", InstructorViewSet, basename="register")

urlpatterns = [
    path("", include(router.urls)),
]
