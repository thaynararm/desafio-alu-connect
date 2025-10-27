from rest_framework import serializers
from instructor.models import Instructor
from user.models import User


class InstructorSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="uuid")
    
    class Meta:
        model = Instructor
        fields = [
            "uuid",
            "user",
            "bio",
        ]

    def validate_user(self, value):
        if value.profile != "MEMBER":
            raise serializers.ValidationError("O usuário deve ter profile 'MEMBER'.")
        return value