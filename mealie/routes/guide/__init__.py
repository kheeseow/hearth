from fastapi import APIRouter

from .guide_crud_routes import router as guide_router

router = APIRouter()
router.include_router(guide_router)
