
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, inspect, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

import app.models  # Register all ORM models.
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User


# Never allow this test suite to target the development or production DB.
_database_url = make_url(settings.database_url)

if _database_url.host not in ("localhost", "127.0.0.1", "::1"):
    raise RuntimeError("Tests require a local PostgreSQL database.")

TEST_DATABASE_URL = _database_url.set(database="community_test_db")

if TEST_DATABASE_URL.database != "community_test_db":
    raise RuntimeError("Unexpected test database name.")

test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(scope="session", autouse=True)
def verify_test_schema():
    """Require a migrated test schema; never create/drop tables implicitly."""
    inspector = inspect(test_engine)
    required_tables = {"users", "media", "community_profiles"}
    missing = required_tables - set(inspector.get_table_names())

    if missing:
        raise RuntimeError(
            "Test database schema is incomplete. "
            f"Missing tables: {sorted(missing)}. "
            "Apply Alembic migrations to community_test_db first."
        )

    yield
    test_engine.dispose()


@pytest.fixture(autouse=True)
def clean_test_data(verify_test_schema):
    """Clear rows only in the explicitly guarded test database."""
    with test_engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(delete(table))


@pytest.fixture
def db_session():
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    fake_admin = User(
        id=uuid.uuid4(),
        email="test-admin@example.invalid",
        password_hash="not-used-in-tests",
        is_active=True,
    )

    def override_get_db():
        session = TestSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: fake_admin

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)

