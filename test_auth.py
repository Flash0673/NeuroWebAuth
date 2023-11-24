# TODO: рефакторинг тестов с помощью conftest.py
import time

from fastapi.testclient import TestClient
from tests.auth.utils import get_db, prepare_db_to_test, create_test_user
from main import app

client = TestClient(app)
test_email = "test@test.com"
test_password = "test_password"
test_username = "test_user"


def test_test():
    response = client.get("/api/v1/check-alive")
    assert response.status_code == 200
    assert response.json() == {"msg": "I'm alive"}


def test_protected():
    response = client.get("/protected-route")
    assert response.status_code == 401


def test_unprotected():
    response = client.get("/unprotected-route")
    assert response.status_code == 200
    assert response.json() == {"msg": f"Hello, anonym"}


def test_registration():
    db = next(get_db())
    prepare_db_to_test(email=test_email, db=db)
    data = {
        "email": test_email,
        "password": test_password,
        "is_active": True,
        "is_superuser": True,
        "is_verified": False,
        "username": test_username,
    }
    response = client.post("/auth/register", json=data)
    assert response.status_code == 201


def test_registration_existing_user():
    db = next(get_db())
    data = {
        "email": test_email,
        "password": test_password,
        "is_active": True,
        "is_superuser": True,
        "is_verified": False,
        "username": test_username,
    }
    create_test_user(db, test_email, data)
    response = client.post("/auth/register", json=data)
    assert response.status_code == 400


def test_log_in_non_existing_user():
    db = next(get_db())
    prepare_db_to_test(test_email, db)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = f"username={test_email}&password={test_password}"
    response = client.post(f"/auth/jwt/login", headers=headers, data=data)
    assert response.status_code == 400


def test_log_in():
    db = next(get_db())
    prepare_db_to_test(test_email, db)
    data = {
        "email": test_email,
        "password": test_password,
        "is_active": True,
        "is_superuser": True,
        "is_verified": False,
        "username": test_username,
    }
    create_test_user(db, test_email, data)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = f"username={test_email}&password={test_password}"
    response = client.post(f"/auth/jwt/login", headers=headers, data=data)
    assert response.status_code == 204
    assert "neuro_token" in response.cookies


# TODO: доделать
# def test_logout():
#     prepare_db_to_test(test_email, db)
#     data = {
#         "email": test_email,
#         "password": test_password,
#         "is_active": True,
#         "is_superuser": True,
#         "is_verified": False,
#         "username": test_username,
#     }
#     create_test_user(db, test_email, data)
#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded"
#     }
#     data = f"username={test_email}&password={test_password}"
#     response = client.post(f"/auth/jwt/login", headers=headers, data=data)
#     headers = {
#         "Cookie": f"neuro_token={response.cookies.get('neuro_token')}"
#     }
#     print(headers)
#     response = client.post("/auth/jwt/logout", headers=headers)
#     assert response.status_code == 200
