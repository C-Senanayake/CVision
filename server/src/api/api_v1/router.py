from fastapi import APIRouter

from api.api_v1.endpoints import user

router = APIRouter()

# register routes
router.include_router(user.router, tags=["users"], prefix="/users")