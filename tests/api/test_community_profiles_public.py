from unittest.mock import patch

from app.models.media import Media, MediaType

def create_media(db_session):
    media = Media(
        media_type=MediaType.IMAGE,
        storage_key="community-profiles/test-leader.jpg",
        original_filename="test-leader.jpg",
        mime_type="image/jpeg",
        file_size=1024,
        width=800,
        height=800,
    )
    db_session.add(media)
    db_session.commit()
    db_session.refresh(media)
    return media

def create_profile(client, *, name, published):
    response = client.post(
        "/api/v1/admin/community-profiles",
        json={
            "name": name,
            "category": "Community Leader",
            "biography": f"Biography for {name}",
            "is_published": published,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_public_list_shows_only_published_profiles(client):
    published = create_profile(
        client, name="Published Leader", published=True
    )
    create_profile(client, name="Draft Leader", published=False)

    response = client.get("/api/v1/community-profiles")

    assert response.status_code == 200
    profiles = response.json()
    assert [profile["id"] for profile in profiles] == [published["id"]]


def test_public_detail_returns_published_profile(client):
    profile = create_profile(
        client, name="Public Leader", published=True
    )

    response = client.get(
        f"/api/v1/community-profiles/{profile['id']}"
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Public Leader"
    assert response.json()["category"] == "Community Leader"
    assert response.json()["profile_media_url"] is None


def test_public_detail_hides_unpublished_profile(client):
    profile = create_profile(
        client, name="Private Draft", published=False
    )

    response = client.get(
        f"/api/v1/community-profiles/{profile['id']}"
    )

    assert response.status_code == 404


def test_public_detail_returns_404_for_unknown_profile(client):
    import uuid

    response = client.get(
        f"/api/v1/community-profiles/{uuid.uuid4()}"
    )

    assert response.status_code == 404

def test_public_profile_includes_photo_url(client, db_session):
    media = create_media(db_session)

    created = client.post(
        "/api/v1/admin/community-profiles",
        json={
            "name": "Leader With Photo",
            "category": "Community Leader",
            "profile_media_id": str(media.id),
            "is_published": True,
        },
    )
    assert created.status_code == 201, created.text

    with patch(
        "app.services.community_profiles.get_public_media_url",
        return_value="https://example.invalid/community-profiles/test-leader.jpg",
    ):
        response = client.get(
            f"/api/v1/community-profiles/{created.json()['id']}"
        )

    assert response.status_code == 200
    assert response.json()["profile_media_id"] == str(media.id)
    assert response.json()["profile_media_url"] == (
        "https://example.invalid/community-profiles/test-leader.jpg"
    )
