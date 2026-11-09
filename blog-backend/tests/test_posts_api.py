"""End-to-end tests of the posts API, using in-memory repositories."""
from app.api.dependencies import get_post_repository
from app.main import app
from tests.fakes import UnavailableDatabaseRepository


def create(client, post, headers):
    response = client.post("/api/posts", json=post, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


# --- Create ------------------------------------------------------------------


def test_create_post_returns_201_with_id_author_and_timestamps(client, valid_post, auth):
    body = create(client, valid_post, auth["headers"])

    assert body["id"]
    assert body["title"] == valid_post["title"]
    assert body["content"] == valid_post["content"]
    assert body["author"] == auth["user"]["name"]
    assert body["owner_id"] == auth["user"]["id"]
    assert body["created_at"] == body["updated_at"]


def test_create_post_requires_sign_in(client, valid_post):
    response = client.post("/api/posts", json=valid_post)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "not_authenticated"
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_create_post_rejects_invalid_token(client, valid_post):
    response = client.post("/api/posts", json=valid_post, headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401


def test_create_post_strips_surrounding_whitespace(client, valid_post, auth):
    body = create(client, {**valid_post, "title": "   Spaced title   "}, auth["headers"])
    assert body["title"] == "Spaced title"


def test_create_post_rejects_whitespace_only_title(client, valid_post, auth):
    response = client.post("/api/posts", json={**valid_post, "title": "     "}, headers=auth["headers"])

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert error["details"][0]["field"] == "title"


def test_create_post_rejects_missing_fields(client, auth):
    response = client.post("/api/posts", json={"title": "Only a title"}, headers=auth["headers"])

    assert response.status_code == 422
    fields = {d["field"] for d in response.json()["error"]["details"]}
    assert fields == {"content"}


def test_create_post_rejects_client_supplied_author_or_id(client, valid_post, auth):
    for extra in ({"_id": "hacked"}, {"author": "Impostor"}, {"owner_id": "someone"}):
        response = client.post("/api/posts", json={**valid_post, **extra}, headers=auth["headers"])
        assert response.status_code == 422, extra


def test_create_post_rejects_too_long_title(client, valid_post, auth):
    response = client.post("/api/posts", json={**valid_post, "title": "x" * 151}, headers=auth["headers"])
    assert response.status_code == 422


# --- Read (public) -----------------------------------------------------------


def test_list_posts_empty(client):
    response = client.get("/api/posts")

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "skip": 0, "limit": 20}


def test_list_posts_newest_first_with_pagination(client, valid_post, auth):
    for i in range(3):
        create(client, {**valid_post, "title": f"Post number {i}"}, auth["headers"])

    response = client.get("/api/posts", params={"skip": 1, "limit": 1})

    body = response.json()
    assert body["total"] == 3
    assert [p["title"] for p in body["items"]] == ["Post number 1"]


def test_list_posts_rejects_limit_above_maximum(client):
    response = client.get("/api/posts", params={"limit": 101})
    assert response.status_code == 422


def test_get_post_by_id_without_signing_in(client, valid_post, auth):
    created = create(client, valid_post, auth["headers"])

    response = client.get(f"/api/posts/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_missing_post_returns_404(client):
    response = client.get("/api/posts/does-not-exist")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "post_not_found"


# --- Update ------------------------------------------------------------------


def test_owner_can_update_post(client, valid_post, auth):
    created = create(client, valid_post, auth["headers"])
    changes = {**valid_post, "title": "Edited title"}

    response = client.put(f"/api/posts/{created['id']}", json=changes, headers=auth["headers"])

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Edited title"
    assert body["author"] == auth["user"]["name"]
    assert body["created_at"] == created["created_at"]
    assert body["updated_at"] >= created["updated_at"]


def test_other_user_cannot_update_post(client, valid_post, auth, other_auth):
    created = create(client, valid_post, auth["headers"])

    response = client.put(f"/api/posts/{created['id']}", json=valid_post, headers=other_auth["headers"])

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "forbidden"
    assert client.get(f"/api/posts/{created['id']}").json()["title"] == valid_post["title"]


def test_update_requires_sign_in(client, valid_post, auth):
    created = create(client, valid_post, auth["headers"])
    response = client.put(f"/api/posts/{created['id']}", json=valid_post)
    assert response.status_code == 401


def test_update_missing_post_returns_404(client, valid_post, auth):
    response = client.put("/api/posts/does-not-exist", json=valid_post, headers=auth["headers"])
    assert response.status_code == 404


def test_update_with_invalid_data_returns_422(client, valid_post, auth):
    created = create(client, valid_post, auth["headers"])
    response = client.put(
        f"/api/posts/{created['id']}", json={**valid_post, "content": "short"}, headers=auth["headers"]
    )
    assert response.status_code == 422


# --- Delete ------------------------------------------------------------------


def test_owner_can_delete_post(client, valid_post, auth):
    created = create(client, valid_post, auth["headers"])

    response = client.delete(f"/api/posts/{created['id']}", headers=auth["headers"])

    assert response.status_code == 204
    assert client.get(f"/api/posts/{created['id']}").status_code == 404


def test_other_user_cannot_delete_post(client, valid_post, auth, other_auth):
    created = create(client, valid_post, auth["headers"])

    response = client.delete(f"/api/posts/{created['id']}", headers=other_auth["headers"])

    assert response.status_code == 403
    assert client.get(f"/api/posts/{created['id']}").status_code == 200


def test_delete_requires_sign_in(client, valid_post, auth):
    created = create(client, valid_post, auth["headers"])
    response = client.delete(f"/api/posts/{created['id']}")
    assert response.status_code == 401


def test_delete_missing_post_returns_404(client, auth):
    response = client.delete("/api/posts/does-not-exist", headers=auth["headers"])
    assert response.status_code == 404


# --- Infrastructure ----------------------------------------------------------


def test_database_outage_returns_503_without_leaking_details(client):
    app.dependency_overrides[get_post_repository] = lambda: UnavailableDatabaseRepository()

    response = client.get("/api/posts")

    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "database_unavailable"
    assert "connection refused" not in error["message"]


def test_unknown_route_uses_standard_error_format(client):
    response = client.get("/api/nope")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "http_error"


def test_responses_include_request_id_header(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]
