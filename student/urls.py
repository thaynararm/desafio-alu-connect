from django.urls import path, include
from rest_framework import routers
from student.views import StudentViewSet

router = routers.DefaultRouter()
router.register(r"", StudentViewSet, basename="register")

urlpatterns = [
    path("", include(router.urls)),
]
