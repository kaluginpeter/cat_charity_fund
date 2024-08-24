from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.crud.charity_project import charity_project_crud
from app.api.validators import (
    check_charity_project_name_duplicate,
    check_charity_project_exist,
    check_is_closed_or_invested_project,
    check_new_full_amount_cant_be_less_than_invested_amount
)
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectUpdate, CharityProjectDB
)
from app.core.user import current_superuser
from app.services.money_transaction import transaction_mechanism


CHARITY_PROJECT_PREFIX_URL = '/charity_project'
CHARITY_PROJECT_ROUTER_TAGS = ['Charity Projects']


router = APIRouter(
    prefix=CHARITY_PROJECT_PREFIX_URL,
    tags=CHARITY_PROJECT_ROUTER_TAGS
)


@router.post(
    '/',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def create_charity_project(
    charity_project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Эндпоинт для создания нового благотворительного проекта.
    Доступен только для суперпользователей!
    """
    await check_charity_project_name_duplicate(
        charity_project.name, session
    )
    new_charity_project = await charity_project_crud.create(
        charity_project, session
    )
    await transaction_mechanism.launch_investing_proccess(session)
    await session.refresh(new_charity_project)
    return new_charity_project


@router.get(
    '/',
    response_model=list[CharityProjectDB]
)
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session)
):
    """
    Эндпоинт для получения всех благотворительных проектов.
    Доступен любому пользователю.
    """
    charity_projects = await charity_project_crud.get_multi(session)
    return charity_projects


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Эндпоинт для удаления благотворительного проекта.
    Проект в который уже инвестировали деньги не может быть удален.
    Доступен долько для суперпользователей!
    """
    await check_charity_project_exist(project_id, session)
    await check_is_closed_or_invested_project(
        project_id,
        is_closed=True,
        is_invested=True,
        session=session
    )
    charity_project = await charity_project_crud.get(project_id, session)
    charity_project = await charity_project_crud.remove(
        charity_project, session
    )
    return charity_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def partial_update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Эндпоинт для изменения благотворительного проекта.
    Закрытый проект не может быть изменен.
    Доступен долько для суперпользователей!
    """
    await check_charity_project_exist(project_id, session)
    await check_is_closed_or_invested_project(
        project_id,
        is_closed=True,
        session=session
    )
    if obj_in.full_amount:
        await check_new_full_amount_cant_be_less_than_invested_amount(
            project_id, obj_in.full_amount, session
        )
    charity_project = await charity_project_crud.get(project_id, session)
    await check_charity_project_name_duplicate(
        obj_in.name, session, charity_project.id
    )
    charity_project = await charity_project_crud.update(
        charity_project, obj_in, session
    )
    await transaction_mechanism.recalculate_project_status(
        charity_project, session
    )
    await session.refresh(charity_project)
    return charity_project
