from django.apps import AppConfig


class CourseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "course"

    def ready(self):
        from course.utils.create_template import create_certificate_template

        create_certificate_template()
