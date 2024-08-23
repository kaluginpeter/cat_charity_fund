from http import HTTPStatus
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.charity_project import CharityProject
from app.crud.charity_project import charity_project_crud


CHARITY_PROJECT_DUPLICATE_NAME_ERROR = (
    'Благотворительный фонд с таким именем уже существует!'
)
NOT_FOUND_CHARITY_PROJECT_ERROR = 'Благотворительный фонд не найден!'
INVESTED_OR_CLOSED_CHARITY_PROJECT_ERROR = (
    'Нельзя изменять закрыйтый или инвестированный проект!'
)
NEW_FULL_AMOUNT_LESS_THAN_OLD_ERROR = (
    'Новая необходимая сумма не может быть меньше вложенных денег!'
)


async def check_charity_project_name_duplicate(
    project_name: str,
    session: AsyncSession,
    old_project_id: Optional[int] = None,
) -> None:
    """
    Проверяет, что при обновлении проекта, его
    новое имя не может быть дубликатом(исключая текущее имя).
    """
    charity_project = await charity_project_crud.get_by_name(
        project_name, session
    )
    if charity_project and charity_project.id != old_project_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=CHARITY_PROJECT_DUPLICATE_NAME_ERROR
        )


async def check_charity_project_exist(
    project_id: int,
    session: AsyncSession
) -> CharityProject:
    """
    Проверяет, что благотворительный проект с указанным
    идентификатором существует, если это не так,
    то выбрасывает исключение.
    Если нет, и объект существует, то возвращает его.
    """
    charity_project = await charity_project_crud.get(project_id, session)
    if charity_project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=NOT_FOUND_CHARITY_PROJECT_ERROR
        )
    return charity_project


async def check_is_closed_or_invested_project(
    project_id: int,
    is_closed: bool,
    session: AsyncSession,
    is_invested: Optional[bool] = None,
) -> None:
    """
    Проверяет, что проект с указанным идентификатором не был
    закрыт или в него были инвестированны деньги.
    Если проект попадает в указанные критерии, то выбрасывается
    исключение или же просто ничего не происходит.
    Принимаемые аргументы для фильтрации:
    is_closed - закрыт ли проект, значения True или False.
    is_invested (опциональный, если не указан, то в вычислении не используется)
        означает, были ли инвестированы в проект деньги.
    """
    charity_project = (
        await charity_project_crud.get_closed_or_invested_charity_project(
            project_id, is_closed, is_invested, session
        )
    )
    if charity_project is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=INVESTED_OR_CLOSED_CHARITY_PROJECT_ERROR
        )


async def check_new_full_amount_cant_be_less_than_invested_amount(
    project_id: int,
    new_full_amount: int,
    session: AsyncSession
) -> None:
    """
    Проверяет, что при обновлении проекта, новая необходимая сумма
    не может быть меньше уже внесенных в проект денег.
    Если это условие нарушается - то выбрасывается исключение.
    Если условие верно, то ничего не просиходит.
    """
    charity_project = await charity_project_crud.get(project_id, session)
    if charity_project.invested_amount > new_full_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=NEW_FULL_AMOUNT_LESS_THAN_OLD_ERROR
        )
