import pytest
from rest_framework.test import APIClient
from user.models import User
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
def test_create_user_admin():
    client = APIClient()

    data = {
        "username": "admin_user_test",
        "password": "12345678",
        "full_name": "Admin User Test",
        "birth_date": "2000-01-01",
        "cpf": "98765432100",
        "profile": "ADMIN",
        "email": "admin_user_test@example.com",
    }

    response = client.post("/user/register/", data, format="json")
    assert response.status_code == 201
    assert User.objects.filter(username="admin_user_test").exists()
    assert User.objects.get(username="admin_user_test").profile == "ADMIN"


@pytest.mark.django_db
def test_create_user_member():
    client = APIClient()

    data = {
        "username": "member_user_test",
        "password": "12345678",
        "full_name": "Member User Test",
        "birth_date": "2000-01-01",
        "cpf": "98765432100",
        "profile": "MEMBER",
        "email": "member_user_test@example.com",
    }

    response = client.post("/user/register/", data, format="json")
    assert response.status_code == 201
    assert User.objects.filter(username="member_user_test").exists()
    assert User.objects.get(username="member_user_test").profile == "MEMBER"


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


def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


@pytest.mark.django_db
def test_get_user_member_token(member_user):
    client = APIClient()
    data = {
        "username": "member_user_test",
        "password": "12345678",
    }

    response = client.post("/user/login/", data, format="json")
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_get_users_with_admin_user(admin_user):
    client = APIClient()

    token = get_token_for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get("/user/register/", format="json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_users_with_member_user(member_user):
    client = APIClient()

    token = get_token_for_user(member_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get("/user/register/", format="json")
    assert response.status_code == 403
    assert "You do not have permission to perform this action." in response.data.get(
        "detail"
    )


@pytest.mark.django_db
def test_get_own_user_with_member_user(member_user):
    client = APIClient()

    token = get_token_for_user(member_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get(f"/user/register/{str(member_user.uuid)}/", format="json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_member_user_with_admin_user(admin_user, member_user):
    client = APIClient()

    token = get_token_for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "username": "member_user_test",
        "password": "12345678",
        "full_name": "Member User Test 1.1",
        "birth_date": "2000-01-01",
        "cpf": "98765432100",
        "profile": "MEMBER",
        "email": "member_user_test_1@example.com",
    }

    response = client.put(
        f"/user/register/{str(member_user.uuid)}/", data, format="json"
    )
    assert response.status_code == 200
    assert response.data.get("profile") == "MEMBER"
    assert response.data.get("full_name") == "Member User Test 1.1"


@pytest.mark.django_db
def test_update_member_user_with_member_user(member_user):
    client = APIClient()

    token = get_token_for_user(member_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "username": "member_user_test",
        "password": "12345678",
        "full_name": "Member User Test 1.1",
        "birth_date": "2000-01-01",
        "cpf": "98765432100",
        "profile": "MEMBER",
        "email": "member_user_test_1@example.com",
    }

    response = client.put(
        f"/user/register/{str(member_user.uuid)}/", data, format="json"
    )
    assert response.status_code == 200
    assert response.data.get("profile") == "MEMBER"
    assert response.data.get("full_name") == "Member User Test 1.1"
