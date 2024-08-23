from fastapi import APIRouter

from app.core.user import auth_backend, fastapi_users
from app.schemas.user import UserRead, UserCreate, UserUpdate

AUTH_ROUTER_PREFIX = '/auth/jwt'
REGISTER_ROUTER_PREFIX = '/auth'
USER_ROUTER_PREFIX = '/users'
AUTH_ROUTER_TAGS = ['auth']
USER_ROUTER_TAGS = ['users']
USER_DELETE_ENDPOINT_NAME = 'users:delete_user'

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix=AUTH_ROUTER_PREFIX,
    tags=AUTH_ROUTER_TAGS,
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix=REGISTER_ROUTER_PREFIX,
    tags=AUTH_ROUTER_TAGS,
)

users_router = fastapi_users.get_users_router(UserRead, UserUpdate)
users_router.routes = [
    rout for rout in users_router.routes
    if rout.name != USER_DELETE_ENDPOINT_NAME
]
router.include_router(
    users_router,
    prefix=USER_ROUTER_PREFIX,
    tags=USER_ROUTER_TAGS,
)
