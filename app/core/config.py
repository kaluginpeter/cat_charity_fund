from typing import Optional

from pydantic import BaseSettings

APP_TITLE = 'Благотворительный фонд для кошек Cat Charity Fund'
APP_DESCRIPTION = (
    'Собирает средства на проекты для помощи '
    'пушистыми, оказавшимся в сложной жизненной ситуации.'
)
DEFAULT_SECRET_KEY = 'supersecret'


class Settings(BaseSettings):
    app_title: str = APP_TITLE
    app_description: str = APP_DESCRIPTION
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = DEFAULT_SECRET_KEY
    first_superuser_email: Optional[str] = None
    first_superuser_password: Optional[str] = None

    class Config:
        env_file = '.env'


settings = Settings()
