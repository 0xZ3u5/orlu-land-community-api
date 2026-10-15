from app.models.community_profile import CommunityProfile
from app.models.media import Media, MediaType


def test_media_used_by_community_profile_cannot_be_deleted(
    client, db_session, monkeypatch
):
    media = Media(
        media_type=MediaType.IMAGE,
        storage_key="community-profiles/protected.jpg",
        original_filename="protected.jpg",
        mime_type="image/jpeg",
        file_size=1024,
    )
    db_session.add(media)
    db_session.flush()

    profile = CommunityProfile(
        name="Profile With Photo",
        category="Community Leader",
        profile_media_id=media.id,
        is_published=True,
        display_order=0,
    )
    db_session.add(profile)
    db_session.commit()
    media_id = media.id

    def fail_if_r2_is_called():
        raise AssertionError("R2 should not be accessed for referenced media.")

    monkeypatch.setattr(
        "app.api.v1.admin.media.get_r2_client",
        fail_if_r2_is_called,
    )

    response = client.delete(f"/api/v1/admin/media/{media_id}")

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Media is in use. Remove its references before deleting it."
    )
    assert db_session.get(Media, media_id) is not None
