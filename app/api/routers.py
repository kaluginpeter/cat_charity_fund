from fastapi import APIRouter

from app.api.endpoints import (
    user_router, charity_project_router, donations_router
)

main_router = APIRouter()

main_router.include_router(user_router)

main_router.include_router(charity_project_router)

main_router.include_router(donations_router)
