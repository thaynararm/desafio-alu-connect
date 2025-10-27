from rest_framework import serializers
from student.models import Student
from user.models import User


class StudentSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="uuid")

    class Meta:
        model = Student
        fields = [
            "uuid",
            "user",
            "bio",
        ]

    def validate_user(self, value):
        if value.profile != "MEMBER":
            raise serializers.ValidationError("O usuário deve ter profile 'MEMBER'.")
        return value
