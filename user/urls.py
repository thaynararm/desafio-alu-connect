from django.urls import path, include
from rest_framework import routers
from user.views import UserViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = routers.DefaultRouter()
router.register(r'register', UserViewSet, basename='register')

urlpatterns = [
    path('', include(router.urls)),

    # Rotas JWT
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
