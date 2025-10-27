import pytest
from rest_framework.test import APIClient
from user.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from instructor.models import Instructor
from course.models import Course


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
def instructor(member_user):
    return Instructor.objects.create(user=member_user)


def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


@pytest.mark.django_db
def test_create_instructor_with_admin_user_success(admin_user, member_user):
    client = APIClient()

    token = get_token_for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "user": str(member_user.uuid),
    }

    response = client.post("/instructors/", data, format="json")
    assert response.status_code == 201


@pytest.mark.django_db
def test_create_instructor_with_admin_user_failed(admin_user, member_user):
    client = APIClient()

    token = get_token_for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "user": str(admin_user.uuid),
    }

    response = client.post("/instructors/", data, format="json")
    error = response.data["user"][0]
    assert response.status_code == 400
    assert error == "O usuário deve ter profile 'MEMBER'."


@pytest.mark.django_db
def test_create_instructor_with_member_user(member_user):
    client = APIClient()

    token = get_token_for_user(member_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "user": str(member_user.uuid),
    }

    response = client.post("/instructors/", data, format="json")
    assert response.status_code == 403
    assert "You do not have permission to perform this action." in response.data.get(
        "detail"
    )


@pytest.mark.django_db
def test_update_instructor_with_admin_user_success(admin_user, instructor, member_user):
    client = APIClient()

    token = get_token_for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {"user": str(member_user.uuid), "bio": "Teste"}

    response = client.put(f"/instructors/{str(instructor.uuid)}/", data, format="json")
    assert response.status_code == 200
    assert response.data.get("bio") == "Teste"


@pytest.mark.django_db
def test_update_instructor_with_member_user_success(instructor, member_user):
    client = APIClient()

    token = get_token_for_user(member_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {"user": str(member_user.uuid), "bio": "Teste"}

    response = client.put(f"/instructors/{str(instructor.uuid)}/", data, format="json")
    assert response.status_code == 200
    assert response.data.get("bio") == "Teste"


@pytest.mark.django_db
def test_get_instructors_with_admin_user_success(member_user, admin_user):
    client = APIClient()

    token = get_token_for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get(f"/instructors/", format="json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_instructors_with_member_user_failed(member_user):
    client = APIClient()

    token = get_token_for_user(member_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get(f"/instructors/", format="json")
    assert response.status_code == 403
    assert "You do not have permission to perform this action." in response.data.get(
        "detail"
    )


@pytest.mark.django_db
def test_get_instructors_with_admin_user_success(member_user, instructor):
    client = APIClient()

    token = get_token_for_user(member_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get(f"/instructors/{str(instructor.uuid)}/", format="json")
    assert response.status_code == 200


@pytest.fixture
def course_1(instructor):
    course = Course.objects.create(title="Curso 1", description="Curso 1")
    course.instructors.add(instructor)
    return course


@pytest.fixture
def course_2(instructor):
    course = Course.objects.create(title="Curso 2", description="Curso 2")
    course.instructors.add(instructor)
    return course


@pytest.mark.django_db
def test_get_instructor_courses_success(instructor, member_user, course_1, course_2):
    client = APIClient()
    token = get_token_for_user(member_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get(f"/instructors/{str(instructor.uuid)}/courses/")
    assert response.status_code == 200

    data = response.json()
    course_uuids = [c["uuid"] for c in data]
    assert str(course_1.uuid) in course_uuids
    assert str(course_2.uuid) in course_uuids
