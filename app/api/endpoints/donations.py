from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.donation import DonationDB, DonationCreate
from app.core.db import get_async_session
from app.crud.donations import donation_crud
from app.core.user import current_superuser, current_user
from app.models.user import User
from app.services.transaction import transaction_mechanism

DONATIONS_PREFIX_URL = '/donation'
DONATIONS_ROUTER_TAGS = ['donations']
EXCLUDE_DONATIONS_FIELDS_FOR_REGISTER_USER = {
    'user_id', 'invested_amount', 'fully_invested', 'close_date'
}


router = APIRouter(
    prefix=DONATIONS_PREFIX_URL,
    tags=DONATIONS_ROUTER_TAGS
)


@router.get(
    '/',
    response_model=list[DonationDB],
    dependencies=[Depends(current_superuser)]
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session)
):
    """
    Эндпоинт для получения списка всех пожертвований.
    Доступен только для суперпользователей!
    """
    donations = await donation_crud.get_multi(session)
    return donations


@router.get(
    '/my',
    response_model=list[DonationDB],
    response_model_exclude=EXCLUDE_DONATIONS_FIELDS_FOR_REGISTER_USER
)
async def get_donations_by_user(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Эндпоинт для получения пожертвований сделанных текущим пользователем.
    Доступен только для авторизованных пользователей!
    """
    donations = await donation_crud.get_by_user(user.id, session)
    return donations


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude=EXCLUDE_DONATIONS_FIELDS_FOR_REGISTER_USER
)
async def create_donation(
    donation_data: DonationCreate,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Эндпоинт для создания пожертвования.
    Доступен только для авторизованных пользователей!
    """
    donation = await donation_crud.create(donation_data, session, user)
    await transaction_mechanism.launch_investing_proccess(session)
    await session.refresh(donation)
    return donation
