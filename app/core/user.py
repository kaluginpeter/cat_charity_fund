from typing import Optional, Union
import logging

from fastapi import Depends, Request
from fastapi_users import (
    BaseUserManager, FastAPIUsers, IntegerIDMixin, InvalidPasswordException
)
from fastapi_users.authentication import (
    AuthenticationBackend, BearerTransport, JWTStrategy
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_async_session
from app.models.user import User
from app.schemas.user import UserCreate

BEARER_TRANSPORT_URL = 'auth/jwt/login'
JWT_TOKEN_LIFETIME = 3600
AUTH_BACKEND_NAME = 'jwt'
MIN_PASSWORD_LENGTH = 3
TOO_LOW_PASSWORD_LENGTH = 'Пароль должен быть длиннее 3 символов!'
EMAIL_IN_PASSWORD_ERROR = 'Пароль не должен содержать емаил адрес!'
AFTER_USER_REGISTRATION_MESSAGE = (
    'Пользователь {} был успешно зарегистрирован!'
)


async def get_user_db(
    session: AsyncSession = Depends(get_async_session)
):
    yield SQLAlchemyUserDatabase(session, User)


bearer_transport = BearerTransport(tokenUrl=BEARER_TRANSPORT_URL)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(settings.secret, lifetime_seconds=JWT_TOKEN_LIFETIME)


auth_backend = AuthenticationBackend(
    name=AUTH_BACKEND_NAME,
    transport=bearer_transport,
    get_strategy=get_jwt_strategy
)


class UserManager(IntegerIDMixin, BaseUserManager):
    async def validate_password(
        self,
        password: str,
        user: Union[UserCreate, User]
    ) -> None:
        if len(password) < MIN_PASSWORD_LENGTH:
            raise InvalidPasswordException(
                reason=TOO_LOW_PASSWORD_LENGTH
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason=EMAIL_IN_PASSWORD_ERROR
            )

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ) -> None:
        logging.info(AFTER_USER_REGISTRATION_MESSAGE.format(user))


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db)
):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager=get_user_manager,
    auth_backends=[auth_backend]
)

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
