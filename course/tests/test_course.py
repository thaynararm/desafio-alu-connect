import pytest
from rest_framework.test import APIClient
from user.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from student.models import Student
from instructor.models import Instructor
from course.models import Course


@pytest.fixture
def student_user(db):
    from user.models import User

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
    from user.models import User

    return User.objects.create_user(
        username="instructor_user_test",
        password="12345678",
        full_name="instructor User Test",
        birth_date="2000-01-01",
        cpf="20632488000",
        profile="MEMBER",
        email="instructor_user_test@example.com",
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
def student(student_user):
    return Student.objects.create(user=student_user)


@pytest.fixture
def instructor(instructor_user):
    return Instructor.objects.create(user=instructor_user)


@pytest.fixture
def course_1():
    return Course.objects.create(
        title="Curso Teste",
        description="Curso Teste",
    )


@pytest.fixture
def course_2(instructor):
    course_2 = Course.objects.create(
        title="Curso Teste",
        description="Curso Teste",
    )
    course_2.instructors.add(instructor)
    return course_2


def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


@pytest.mark.django_db
def test_create_course_with_admin_user(admin_user, instructor, student):
    client = APIClient()

    token = get_token_for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "title": "Curso Teste",
        "description": "Curso Teste",
        "instructors": [instructor.uuid],
        "students": [student.uuid],
        "is_active": True,
    }

    response = client.post("/courses/", data, format="json")
    assert response.status_code == 201


@pytest.mark.django_db
def test_create_course_with_instructor_user(instructor_user, instructor, student):
    client = APIClient()

    token = get_token_for_user(instructor_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "title": "Curso Teste",
        "description": "Curso Teste",
        "instructors": [instructor.uuid],
        "students": [student.uuid],
        "is_active": True,
    }

    response = client.post("/courses/", data, format="json")
    assert response.status_code == 201


@pytest.mark.django_db
def test_create_course_with_student_user(student_user, instructor, student):
    client = APIClient()

    token = get_token_for_user(student_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "title": "Curso Teste",
        "description": "Curso Teste",
        "instructors": [instructor.uuid],
        "students": [student.uuid],
        "is_active": True,
    }

    response = client.post("/courses/", data, format="json")
    assert response.status_code == 403
    assert "You do not have permission to perform this action." in response.data.get(
        "detail"
    )


@pytest.mark.django_db
def test_update_course_with_admin_user(admin_user, instructor, student, course_1):
    client = APIClient()

    token = get_token_for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "title": "Curso Teste 1",
        "description": "Curso Teste 1",
        "instructors": [instructor.uuid],
        "students": [student.uuid],
        "is_active": True,
    }

    response = client.put(f"/courses/{str(course_1.uuid)}/", data, format="json")
    assert response.status_code == 200
    assert response.data.get("title") == "Curso Teste 1"


@pytest.mark.django_db
def test_update_course_with_instructor_user_success(
    instructor_user, instructor, student, course_2
):
    client = APIClient()

    token = get_token_for_user(instructor_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "title": "Curso Teste 1",
        "description": "Curso Teste 1",
        "instructors": [instructor.uuid],
        "students": [student.uuid],
        "is_active": True,
    }

    response = client.put(f"/courses/{str(course_2.uuid)}/", data, format="json")
    assert response.status_code == 200
    assert response.data.get("title") == "Curso Teste 1"


@pytest.mark.django_db
def test_update_course_with_instructor_user_failed(
    instructor_user, instructor, student, course_1
):
    client = APIClient()

    token = get_token_for_user(instructor_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "title": "Curso Teste 1",
        "description": "Curso Teste 1",
        "instructors": [instructor.uuid],
        "students": [student.uuid],
        "is_active": True,
    }

    response = client.put(f"/courses/{str(course_1.uuid)}/", data, format="json")
    assert response.status_code == 403
    assert (
        "O curso informado não está disponível para este instrutor."
        in response.data.get("detail")
    )


@pytest.mark.django_db
def test_update_course_with_student_user(student_user, instructor, student, course_2):
    client = APIClient()

    token = get_token_for_user(student_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "title": "Curso Teste 1",
        "description": "Curso Teste 1",
        "instructors": [instructor.uuid],
        "students": [student.uuid],
        "is_active": True,
    }

    response = client.put(f"/courses/{str(course_2.uuid)}/", data, format="json")
    assert response.status_code == 403
    assert "You do not have permission to perform this action." in response.data.get(
        "detail"
    )


@pytest.mark.django_db
def test_get_courses_with_admin_user(admin_user):
    client = APIClient()

    token = get_token_for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get(f"/courses/", format="json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_courses_with_instructor_user(instructor_user):
    client = APIClient()

    token = get_token_for_user(instructor_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get(f"/courses/", format="json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_courses_with_student_user(student_user):
    client = APIClient()

    token = get_token_for_user(student_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get(f"/courses/", format="json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_enroll_student_success(student_user, student, course_1):
    client = APIClient()
    token = get_token_for_user(student_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.post(f"/courses/{str(course_1.uuid)}/enroll/")
    assert response.status_code == 200
    assert response.data.get("detail") == "Inscrição realizada com sucesso."

    # Verifica se o aluno foi realmente adicionado ao curso
    course_1.refresh_from_db()
    assert student in course_1.students.all()


@pytest.mark.django_db
def test_enroll_non_student_user(instructor_user, course_1):
    client = APIClient()
    token = get_token_for_user(instructor_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.post(f"/courses/{str(course_1.uuid)}/enroll/")
    assert response.status_code == 403
    assert response.data.get("detail") == "Apenas alunos podem se inscrever."

