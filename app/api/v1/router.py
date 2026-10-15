from fastapi import APIRouter

from app.api.v1.admin.categories import router as admin_categories_router
from app.api.v1.auth.auth import router as auth_router
from app.api.v1.public.categories import router as categories_router
from app.api.v1.public.events import router as public_events_router

from app.api.v1.admin.site import router as admin_site_router
from app.api.v1.admin.authors import router as admin_authors_router
from app.api.v1.admin.posts import router as admin_posts_router
from app.api.v1.admin.pages import router as admin_pages_router
from app.api.v1.public.posts import router as public_posts_router
from app.api.v1.public.gallery import router as public_gallery_router
from app.api.v1.admin.events import router as admin_events_router
from app.api.v1.admin.media import router as admin_media_router
from app.api.v1.admin.gallery import router as admin_gallery_router

from app.api.v1.public.pages import router as public_pages_router
from app.api.v1.public.site import router as public_site_router
from app.api.v1.public.home import router as public_home_router
from app.api.v1.public.search import router as public_search_router
from app.api.v1.admin.community_profiles import (
    router as admin_community_profiles_router,
)
from app.api.v1.public.community_profiles import (
    router as public_community_profiles_router,
)

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(categories_router)
router.include_router(admin_categories_router)
router.include_router(admin_authors_router)
router.include_router(admin_posts_router)
router.include_router(public_posts_router)
router.include_router(public_gallery_router)
router.include_router(admin_events_router)
router.include_router(public_events_router)
router.include_router(admin_media_router)
router.include_router(admin_gallery_router)
router.include_router(public_pages_router)
router.include_router(admin_pages_router)
router.include_router(public_site_router)
router.include_router(admin_site_router)
router.include_router(public_home_router)
router.include_router(admin_community_profiles_router)
router.include_router(public_community_profiles_router)
router.include_router(public_search_router)
