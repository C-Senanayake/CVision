from fastapi import APIRouter

from api.api_v1.endpoints import user
from api.api_v1.endpoints import job
from api.api_v1.endpoints import cv
from api.api_v1.endpoints import github

router = APIRouter()

# register routes
router.include_router(user.router, tags=["users"], prefix="/users")
router.include_router(job.router, tags=["job"], prefix="/job")
router.include_router(cv.router, tags=["cv"], prefix="/cv")
router.include_router(github.router, tags=["github"], prefix="/github")