from app.db.session import SessionLocal
from app.models.site_setting import SiteSetting


def main() -> None:
    with SessionLocal() as db:
        existing_settings = db.query(SiteSetting).first()

        if existing_settings is not None:
            print("Site settings already exist. Nothing to do.")
            return

        site_settings = SiteSetting(
            community_name="",
            description=None,
            logo_media_id=None,
            email=None,
            phone=None,
            address=None,
            whatsapp_url=None,
        )

        db.add(site_settings)
        db.commit()

        print("Baseline site settings created.")


if __name__ == "__main__":
    main()
