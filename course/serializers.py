from rest_framework import serializers
from course.models import *
from instructor.serializers import InstructorSerializer


class CourseSerializer(serializers.ModelSerializer):
    instructors = serializers.SlugRelatedField(
        queryset=Instructor.objects.all(), slug_field="uuid", many=True
    )
    students = serializers.SlugRelatedField(
        queryset=Student.objects.all(), slug_field="uuid", many=True, required=False
    )

    class Meta:
        model = Course
        fields = [
            "uuid",
            "title",
            "description",
            "instructors",
            "students",
            "is_active",
            "created_at",
        ]


class LessonSerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(
        slug_field="uuid", read_only=True
    )

    class Meta:
        model = Lesson
        fields = [
            "uuid",
            "course",
            "title",
            "description",
            "order",
            "content_url",
            "duration_minutes",
            "is_active",
        ]


class StudentProgressSerializer(serializers.ModelSerializer):
    completed_lessons = serializers.SerializerMethodField(read_only=True)
    completed_lesson_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Lesson.objects.all(), write_only=True, required=False
    )
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), write_only=True
    )
    course = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = StudentProgress
        fields = [
            "uuid",
            "student",
            "course_id",
            "course",
            "completed_lessons",
            "completed_lesson_ids",
            "status",
            "started_at",
            "completed_at",
            
        ]
        read_only_fields = ["status", "started_at", "completed_at", "student"]

    def get_completed_lessons(self, obj):
        return [lesson.uuid for lesson in obj.completed_lessons.all()]

    def update(self, instance, validated_data):
        lessons = validated_data.pop("completed_lesson_ids", [])
        for lesson in lessons:
            instance.mark_lesson_completed(lesson)
        return super().update(instance, validated_data)
