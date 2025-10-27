import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from user.models import User
from student.models import Student
from instructor.models import Instructor
from course.models import *


@pytest.fixture
def student_user(db):

    return User.objects.create_user(
        username="student_user_test",
        password="12345678",
        full_name="Student User Test",
        birth_date="2000-01-01",
        cpf="83426220024",
        profile="MEMBER",
        email="student_user_test@example.com",
    )


@pytest.fixture
def instructor_user(db):
    return User.objects.create_user(
        username="instructor_user_test",
        password="12345678",
        full_name="Instructor User Test",
        birth_date="2000-01-01",
        cpf="20632488000",
        profile="MEMBER",
        email="instructor_user_test@example.com",
    )


@pytest.fixture
def instructor_user_2(db):
    return User.objects.create_user(
        username="instructor_user_2_test",
        password="12345678",
        full_name="Instructor User Test",
        birth_date="2000-01-01",
        cpf="18280201092",
        profile="MEMBER",
        email="instructor_user_2_test@example.com",
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username="admin_user_test",
        password="12345678",
        full_name="Admin User Test",
        birth_date="2000-01-01",
        cpf="18292873031",
        profile="ADMIN",
        email="admin_user_test@example.com",
    )


@pytest.fixture
def student(student_user):
    return Student.objects.create(user=student_user)


@pytest.fixture
def instructor(instructor_user):
    return Instructor.objects.create(user=instructor_user)


@pytest.fixture
def unlinked_instructor(instructor_user_2):
    return Instructor.objects.create(user=instructor_user_2)


@pytest.fixture
def course(instructor, student):
    c = Course.objects.create(title="Curso Teste", description="Descrição")
    c.instructors.add(instructor)
    c.students.add(student)
    return c


@pytest.fixture
def lesson(course):
    return Lesson.objects.create(
        course=course,
        title="Aula 1",
        description="Descrição da aula",
        order=1,
        content_url="http://example.com",
        duration_minutes=30,
    )


def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


@pytest.mark.django_db
def test_create_lesson_with_instructor(course, instructor):
    client = APIClient()
    token = get_token_for_user(instructor.user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "course": course.uuid,
        "title": "Nova Aula",
        "description": "Descrição",
        "order": 2,
        "content_url": "http://example.com/aula",
        "duration_minutes": 45,
        "is_active": True,
    }

    response = client.post(f"/courses/{course.uuid}/lessons/", data, format="json")
    assert response.status_code == 201
    assert response.data["title"] == "Nova Aula"


@pytest.mark.django_db
def test_create_lesson_with_student(course, student):
    client = APIClient()
    token = get_token_for_user(student.user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "course": course.uuid,
        "title": "Nova Aula",
        "description": "Descrição",
        "order": 2,
        "content_url": "http://example.com/aula",
        "duration_minutes": 45,
        "is_active": True,
    }

    response = client.post(f"/courses/{course.uuid}/lessons/", data, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_lesson_with_unlinked_instructor(course, unlinked_instructor):

    client = APIClient()
    token = get_token_for_user(unlinked_instructor.user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "course": course.uuid,
        "title": "Aula Não Permitida",
        "description": "Tentativa de criação por instrutor não vinculado",
        "order": 2,
        "content_url": "http://example.com/aula",
        "duration_minutes": 45,
        "is_active": True,
    }

    response = client.post(f"/courses/{course.uuid}/lessons/", data, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_list_lessons(course, lesson, student):
    client = APIClient()
    token = get_token_for_user(student.user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get(f"/courses/{course.uuid}/lessons/")
    assert response.status_code == 200
    assert len(response.data) >= 1


@pytest.mark.django_db
def test_get_lesson_detail(course, lesson, student):
    client = APIClient()
    token = get_token_for_user(student.user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get(f"/courses/{course.uuid}/lessons/{lesson.uuid}/")
    assert response.status_code == 200
    assert response.data["title"] == lesson.title


@pytest.mark.django_db
def test_update_lesson_with_instructor(course, lesson, instructor):
    client = APIClient()
    token = get_token_for_user(instructor.user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "course": course.uuid,
        "title": "Aula Atualizada",
        "description": lesson.description,
        "order": lesson.order,
        "content_url": lesson.content_url,
        "duration_minutes": lesson.duration_minutes,
        "is_active": lesson.is_active,
    }

    response = client.put(
        f"/courses/{course.uuid}/lessons/{lesson.uuid}/", data, format="json"
    )
    assert response.status_code == 200
    assert response.data["title"] == "Aula Atualizada"


@pytest.mark.django_db
def test_delete_lesson_with_instructor(course, lesson, instructor):
    client = APIClient()
    token = get_token_for_user(instructor.user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.delete(f"/courses/{course.uuid}/lessons/{lesson.uuid}/")
    assert response.status_code == 204


@pytest.mark.django_db
def test_delete_lesson_with_student(course, lesson, student):
    client = APIClient()
    token = get_token_for_user(student.user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.delete(f"/courses/{course.uuid}/lessons/{lesson.uuid}/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_lesson_with_unlinked_instructor(course, lesson, unlinked_instructor):
    client = APIClient()
    token = get_token_for_user(unlinked_instructor.user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.delete(f"/courses/{course.uuid}/lessons/{lesson.uuid}/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_lesson_with_unlinked_instructor(course, lesson, unlinked_instructor):

    client = APIClient()
    token = get_token_for_user(unlinked_instructor.user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "course": course.uuid,
        "title": "Atualização Não Permitida",
        "description": lesson.description,
        "order": lesson.order,
        "content_url": lesson.content_url,
        "duration_minutes": lesson.duration_minutes,
        "is_active": lesson.is_active,
    }

    response = client.put(
        f"/courses/{course.uuid}/lessons/{lesson.uuid}/", data, format="json"
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_lesson_with_student(course, lesson, student):
    client = APIClient()
    token = get_token_for_user(student.user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "course": course.uuid,
        "title": "Atualização Não Permitida pelo Estudante",
        "description": lesson.description,
        "order": lesson.order,
        "content_url": lesson.content_url,
        "duration_minutes": lesson.duration_minutes,
        "is_active": lesson.is_active,
    }

    response = client.put(
        f"/courses/{course.uuid}/lessons/{lesson.uuid}/", data, format="json"
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_mark_lesson_progress_with_student(course, lesson, student):
    client = APIClient()
    token = get_token_for_user(student.user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.post(f"/courses/{course.uuid}/lessons/{lesson.uuid}/progress/")
    assert response.status_code == 200
    assert "marcada como concluída" in response.data["detail"]

    progress = StudentProgress.objects.get(student=student, course=course)
    assert lesson in progress.completed_lessons.all()
    assert progress.status in ["IN_PROGRESS", "COMPLETED"]


@pytest.mark.django_db
def test_mark_lesson_progress_twice(course, lesson, student):
    client = APIClient()
    token = get_token_for_user(student.user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    client.post(f"/courses/{course.uuid}/lessons/{lesson.uuid}/progress/")

    response = client.post(f"/courses/{course.uuid}/lessons/{lesson.uuid}/progress/")
    assert response.status_code == 400
    assert "Não é possível alterar o progresso de um curso concluído." in response.data["detail"]

    progress = StudentProgress.objects.get(student=student, course=course)
    assert progress.completed_lessons.count() == 1


@pytest.mark.django_db
def test_mark_lesson_progress_with_non_student(course, lesson, instructor_user):
    client = APIClient()
    token = get_token_for_user(instructor_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.post(f"/courses/{course.uuid}/lessons/{lesson.uuid}/progress/")
    assert response.status_code == 403
    assert "Apenas alunos podem marcar progresso" in response.data["detail"]


@pytest.mark.django_db
def test_mark_lesson_progress_invalid_lesson(course, student):
    client = APIClient()
    token = get_token_for_user(student.user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    invalid_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.post(f"/courses/{course.uuid}/lessons/{invalid_uuid}/progress/")
    assert response.status_code == 404
