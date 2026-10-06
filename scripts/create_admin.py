from getpass import getpass

from pydantic import EmailStr, TypeAdapter
from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User


def main() -> None:
    email_input = input("Admin email: ").strip()

    try:
        email = TypeAdapter(EmailStr).validate_python(email_input)
    except ValueError:
        print("Invalid email address.")
        return

    password = getpass("Admin password: ")
    password_confirmation = getpass("Confirm password: ")

    if password != password_confirmation:
        print("Passwords do not match.")
        return

    if not password:
        print("Password cannot be empty.")
        return

    with SessionLocal() as db:
        existing_user = db.scalar(select(User).limit(1))

        if existing_user is not None:
            print("A user already exists. Admin bootstrap aborted.")
            return

        user = User(
            email=str(email),
            password_hash=hash_password(password),
            is_active=True,
        )

        db.add(user)
        db.commit()

        print(f"Admin created: {user.email}")


if __name__ == "__main__":
    main()
