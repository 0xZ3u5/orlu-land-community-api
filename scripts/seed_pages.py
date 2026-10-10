from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.page import Page


PAGES = [
    {
        "slug": "about",
        "title": "About Us",
        "content": "",
    },
    {
        "slug": "contact",
        "title": "Contact Us",
        "content": "",
    },
]


def main() -> None:
    with SessionLocal() as db:
        for page_data in PAGES:
            existing_page = db.scalar(
                select(Page).where(Page.slug == page_data["slug"])
            )

            if existing_page is not None:
                print(f"Page already exists: {page_data['slug']}")
                continue

            page = Page(**page_data)
            db.add(page)
            print(f"Created page: {page_data['slug']}")

        db.commit()


if __name__ == "__main__":
    main()
