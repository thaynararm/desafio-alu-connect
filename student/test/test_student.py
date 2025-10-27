import pytest
from rest_framework.test import APIClient
from user.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from student.models import Student
from course.models import *


@pytest.fixture
def member_user(db):
    from user.models import User

    return User.objects.create_user(
        username="member_user_test",
        password="12345678",
        full_name="Member User Test",
        birth_date="2000-01-01",
        cpf="83426220024",
        profile="MEMBER",
        email="member_user_test@example.com",
    )


@pytest.fixture
def admin_user(db):
    from user.models import User

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
def student(member_user):
    return Student.objects.create(user=member_user)


def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


@pytest.mark.django_db
def test_create_student_with_admin_user_success(admin_user, member_user):
    client = APIClient()

    token = get_token_for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "user": str(member_user.uuid),
    }

    response = client.post("/students/", data, format="json")
    assert response.status_code == 201


@pytest.mark.django_db
def test_create_student_with_admin_user_failed(admin_user, member_user):
    client = APIClient()

    token = get_token_for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "user": str(admin_user.uuid),
    }

    response = client.post("/students/", data, format="json")
    error = response.data["user"][0]
    assert response.status_code == 400
    assert error == "O usuário deve ter profile 'MEMBER'."


@pytest.mark.django_db
def test_create_student_with_member_user(member_user):
    client = APIClient()

    token = get_token_for_user(member_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "user": str(member_user.uuid),
    }

    response = client.post("/students/", data, format="json")
    assert response.status_code == 403
    assert "You do not have permission to perform this action." in response.data.get(
        "detail"
    )


@pytest.mark.django_db
def test_update_student_with_admin_user_success(admin_user, student, member_user):
    client = APIClient()

    token = get_token_for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {"user": str(member_user.uuid), "bio": "Teste"}

    response = client.put(f"/students/{str(student.uuid)}/", data, format="json")
    assert response.status_code == 200
    assert response.data.get("bio") == "Teste"


@pytest.mark.django_db
def test_update_student_with_member_user_success(student, member_user):
    client = APIClient()

    token = get_token_for_user(member_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {"user": str(member_user.uuid), "bio": "Teste"}

    response = client.put(f"/students/{str(student.uuid)}/", data, format="json")
    assert response.status_code == 200
    assert response.data.get("bio") == "Teste"


@pytest.mark.django_db
def test_get_students_with_admin_user_success(member_user, admin_user):
    client = APIClient()

    token = get_token_for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get(f"/students/", format="json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_students_with_member_user_failed(member_user):
    client = APIClient()

    token = get_token_for_user(member_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get(f"/students/", format="json")
    assert response.status_code == 403
    assert "You do not have permission to perform this action." in response.data.get(
        "detail"
    )


@pytest.mark.django_db
def test_get_students_with_admin_user_success(member_user, student):
    client = APIClient()

    token = get_token_for_user(member_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get(f"/students/{str(student.uuid)}/", format="json")
    assert response.status_code == 200


@pytest.fixture
def instructor_for_student(student):
    from instructor.models import Instructor

    instructor, created = Instructor.objects.get_or_create(user=student.user)
    return instructor


@pytest.fixture
def course_1(student, instructor_for_student):
    course = Course.objects.create(title="Curso 1", description="Curso 1")
    course.students.add(student)
    course.instructors.add(instructor_for_student)
    return course


@pytest.fixture
def course_2(student, instructor_for_student):
    course = Course.objects.create(title="Curso 2", description="Curso 2")
    course.students.add(student)
    course.instructors.add(instructor_for_student)
    return course


@pytest.mark.django_db
def test_get_student_courses_success(student, member_user, course_1, course_2):
    client = APIClient()
    token = get_token_for_user(member_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get(f"/students/{str(student.uuid)}/courses/")
    assert response.status_code == 200

    data = response.json()
    course_uuids = [c["uuid"] for c in data]
    assert str(course_1.uuid) in course_uuids
    assert str(course_2.uuid) in course_uuids


@pytest.mark.django_db
def test_get_student_progress(student, member_user, course_1, course_2):
    StudentProgress.objects.create(student=student, course=course_1)
    StudentProgress.objects.create(student=student, course=course_2)

    client = APIClient()
    token = get_token_for_user(member_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get(f"/students/{student.uuid}/progress/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    course_titles = [p["course"] for p in data]
    assert course_1.title in course_titles
    assert course_2.title in course_titles


@pytest.mark.django_db
def test_get_student_course_progress(student, member_user, course_1):
    lesson1 = Lesson.objects.create(course=course_1, title="Aula 1", order=1)
    lesson2 = Lesson.objects.create(course=course_1, title="Aula 2", order=2)

    progress = StudentProgress.objects.create(student=student, course=course_1)
    progress.completed_lessons.add(lesson1)
    progress.save()

    client = APIClient()
    token = get_token_for_user(member_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get(f"/students/{student.uuid}/courses/{course_1.uuid}/progress/")
    assert response.status_code == 200

    data = response.json()
    assert data["student"] == student.user.full_name
    assert data["course"] == course_1.title
    assert data["status"] == progress.status
    completed_uuids = [l["uuid"] for l in data["completed_lessons"]]
    assert str(lesson1.uuid) in completed_uuids
    assert str(lesson2.uuid) not in completed_uuids


@pytest.mark.django_db
def test_get_student_course_progress_not_found(student, member_user):
    from uuid import uuid4

    client = APIClient()
    token = get_token_for_user(member_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    random_uuid = uuid4()
    response = client.get(f"/students/{student.uuid}/courses/{random_uuid}/progress/")
    assert response.status_code == 404
    assert response.data["detail"] == "Progresso não encontrado."
