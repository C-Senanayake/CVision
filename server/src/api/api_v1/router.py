from fastapi import APIRouter

from api.api_v1.endpoints import user
from api.api_v1.endpoints import pdf

router = APIRouter()

# register routes
router.include_router(user.router, tags=["users"], prefix="/users")
router.include_router(pdf.router, tags=["pdf"], prefix="/pdf")