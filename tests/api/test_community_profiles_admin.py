import uuid

def create_profile(client, *, name, published=False):
    response = client.post(
        "/api/v1/admin/community-profiles",
        json={
            "name": name,
            "category": "Distinguished Figure",
            "is_published": published,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_admin_can_create_and_retrieve_profile(client):
    created = create_profile(client, name="Test Leader")

    response = client.get(
        f"/api/v1/admin/community-profiles/{created['id']}"
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Test Leader"
    assert response.json()["is_published"] is False


def test_admin_can_update_profile_and_clear_biography(client):
    created = client.post(
        "/api/v1/admin/community-profiles",
        json={
            "name": "Original Name",
            "category": "Leader",
            "biography": "Original biography",
        },
    )
    assert created.status_code == 201, created.text
    profile_id = created.json()["id"]

    response = client.patch(
        f"/api/v1/admin/community-profiles/{profile_id}",
        json={
            "name": "Updated Name",
            "biography": None,
            "is_published": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
    assert response.json()["biography"] is None
    assert response.json()["is_published"] is True


def test_admin_list_includes_unpublished_profiles(client):
    create_profile(client, name="Draft Leader")

    response = client.get("/api/v1/admin/community-profiles")

    assert response.status_code == 200
    assert any(
        item["name"] == "Draft Leader"
        and item["is_published"] is False
        for item in response.json()
    )


def test_admin_can_reorder_all_profiles(client):
    first = create_profile(client, name="Alpha")
    second = create_profile(client, name="Beta")

    response = client.patch(
        "/api/v1/admin/community-profiles/order",
        json={"profile_ids": [second["id"], first["id"]]},
    )

    assert response.status_code == 204

    listing = client.get("/api/v1/admin/community-profiles")
    assert listing.status_code == 200
    assert [item["id"] for item in listing.json()] == [
        second["id"], first["id"]
    ]


def test_reorder_rejects_duplicate_ids(client):
    profile = create_profile(client, name="Alpha")

    response = client.patch(
        "/api/v1/admin/community-profiles/order",
        json={"profile_ids": [profile["id"], profile["id"]]},
    )

    assert response.status_code == 422


def test_reorder_requires_every_profile(client):
    create_profile(client, name="Alpha")
    create_profile(client, name="Beta")

    response = client.patch(
        "/api/v1/admin/community-profiles/order",
        json={"profile_ids": []},
    )

    assert response.status_code == 422


def test_admin_can_delete_profile(client):
    profile = create_profile(client, name="Delete Me")

    response = client.delete(
        f"/api/v1/admin/community-profiles/{profile['id']}"
    )
    assert response.status_code == 204

    response = client.get(
        f"/api/v1/admin/community-profiles/{profile['id']}"
    )
    assert response.status_code == 404


def test_admin_routes_require_authentication(client):
    from app.core.dependencies import get_current_user
    from app.main import app

    saved_override = app.dependency_overrides.pop(
        get_current_user, None
    )
    try:
        response = client.get("/api/v1/admin/community-profiles")
        assert response.status_code in (401, 403)
    finally:
        if saved_override is not None:
            app.dependency_overrides[get_current_user] = saved_override


def test_create_rejects_missing_required_fields(client):
    response = client.post(
        "/api/v1/admin/community-profiles",
        json={"biography": "Missing name and category"},
    )

    assert response.status_code == 422

def test_create_rejects_nonexistent_profile_media(client):
    response = client.post(
        "/api/v1/admin/community-profiles",
        json={
            "name": "Invalid Photo",
            "category": "Community Leader",
            "profile_media_id": str(uuid.uuid4()),
        },
    )

    assert response.status_code == 404

def test_create_trims_name_and_category(client):
    response = client.post(
        "/api/v1/admin/community-profiles",
        json={
            "name": "  Test Leader  ",
            "category": "  Community Figure  ",
        },
    )

    assert response.status_code == 201, response.text
    assert response.json()["name"] == "Test Leader"
    assert response.json()["category"] == "Community Figure"


def test_create_rejects_whitespace_only_name(client):
    response = client.post(
        "/api/v1/admin/community-profiles",
        json={
            "name": "   ",
            "category": "Community Figure",
        },
    )

    assert response.status_code == 422


def test_update_rejects_whitespace_only_category(client):
    created = create_profile(client, name="Test Leader")

    response = client.patch(
        f"/api/v1/admin/community-profiles/{created['id']}",
        json={"category": "   "},
    )

    assert response.status_code == 422
