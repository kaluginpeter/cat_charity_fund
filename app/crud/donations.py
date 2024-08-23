from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import BaseCRUD
from app.schemas.donation import DonationCreate, DonationDB, DonationUpdate
from app.models.donation import Donation


class DonationCRUD(
    BaseCRUD[Donation, DonationCreate, DonationUpdate]
):
    async def get_by_user(
        self,
        user_id: int,
        session: AsyncSession
    ) -> list[DonationDB]:
        donations = (
            await session.execute(
                select(Donation).where(Donation.user_id == user_id)
            )
        )
        return donations.scalars().all()


donation_crud = DonationCRUD(Donation)
