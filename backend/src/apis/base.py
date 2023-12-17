from apis.routes.route import router as api_router
from fastapi import APIRouter

router = APIRouter()
router.include_router(api_router, prefix="", tags=["upload", "websocket"])