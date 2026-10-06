from fastapi import APIRouter

from app.api.v1.admin.categories import router as admin_categories_router
from app.api.v1.auth.auth import router as auth_router
from app.api.v1.public.categories import router as categories_router
from app.api.v1.public.events import router as public_events_router
from app.api.v1.admin.authors import router as admin_authors_router
from app.api.v1.admin.posts import router as admin_posts_router
from app.api.v1.public.posts import router as public_posts_router
from app.api.v1.admin.events import router as admin_events_router
from app.api.v1.admin.media import router as admin_media_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(categories_router)
router.include_router(admin_categories_router)
router.include_router(admin_authors_router)
router.include_router(admin_posts_router)
router.include_router(public_posts_router)
router.include_router(admin_events_router)
router.include_router(public_events_router)
router.include_router(admin_media_router)
