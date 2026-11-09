"""Tests for registration, login and token handling."""
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings


def test_register_returns_token_and_public_user(client, valid_user):
    response = client.post("/api/auth/register", json=valid_user)

    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == valid_user["email"]
    assert body["user"]["name"] == valid_user["name"]
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]


def test_register_rejects_duplicate_email_case_insensitively(client, valid_user):
    client.post("/api/auth/register", json=valid_user)

    response = client.post("/api/auth/register", json={**valid_user, "email": valid_user["email"].upper()})

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "email_already_registered"


def test_register_validates_email_and_password(client, valid_user):
    bad_email = client.post("/api/auth/register", json={**valid_user, "email": "not-an-email"})
    short_password = client.post("/api/auth/register", json={**valid_user, "password": "short"})

    assert bad_email.status_code == 422
    assert bad_email.json()["error"]["details"][0]["field"] == "email"
    assert short_password.status_code == 422
    assert short_password.json()["error"]["details"][0]["field"] == "password"


def test_login_with_correct_credentials(client, valid_user):
    client.post("/api/auth/register", json=valid_user)

    response = client.post(
        "/api/auth/login", json={"email": valid_user["email"], "password": valid_user["password"]}
    )

    assert response.status_code == 200
    assert response.json()["user"]["email"] == valid_user["email"]


def test_login_with_wrong_password_and_unknown_email_look_identical(client, valid_user):
    client.post("/api/auth/register", json=valid_user)

    wrong_password = client.post(
        "/api/auth/login", json={"email": valid_user["email"], "password": "wrong-password-here"}
    )
    unknown_email = client.post(
        "/api/auth/login", json={"email": "nobody@example.com", "password": valid_user["password"]}
    )

    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()
    assert wrong_password.json()["error"]["code"] == "invalid_credentials"


def test_me_returns_current_user(client, auth):
    response = client.get("/api/auth/me", headers=auth["headers"])

    assert response.status_code == 200
    assert response.json() == auth["user"]


def test_me_without_token_returns_401(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_expired_token_is_rejected(client, auth):
    settings = get_settings()
    expired = jwt.encode(
        {"sub": auth["user"]["id"], "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired}"})

    assert response.status_code == 401
    assert "expired" in response.json()["error"]["message"].lower()


def test_token_signed_with_wrong_secret_is_rejected(client, auth):
    forged = jwt.encode(
        {"sub": auth["user"]["id"], "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        "attacker-controlled-secret-that-is-long-enough",
        algorithm="HS256",
    )

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {forged}"})

    assert response.status_code == 401


def test_token_for_deleted_user_is_rejected(client, auth, user_repository):
    user_repository._users.clear()

    response = client.get("/api/auth/me", headers=auth["headers"])

    assert response.status_code == 401
