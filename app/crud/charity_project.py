from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import BaseCRUD
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectUpdate
)
from app.models.charity_project import CharityProject

MINIMUM_MONEY_VALUE_FOR_CHARITY_PROJECT = 0


class CharityProjectCrud(
    BaseCRUD[
        CharityProject,
        CharityProjectCreate,
        CharityProjectUpdate
    ]
):
    async def get_closed_or_invested_charity_project(
        self,
        project_id: int,
        is_closed: bool,
        is_invested: Optional[bool],
        session: AsyncSession
    ) -> Optional[CharityProject]:
        if is_invested is not None:
            statement = select(self.model).where(
                self.model.id == project_id,
                or_(
                    self.model.fully_invested == is_closed,
                    (
                        (
                            self.model.invested_amount >
                            MINIMUM_MONEY_VALUE_FOR_CHARITY_PROJECT
                        ) == is_invested
                    )
                )
            )
        else:
            statement = select(self.model).where(
                self.model.id == project_id,
                self.model.fully_invested == is_closed
            )

        charity_project = await session.execute(statement)
        return charity_project.scalars().first()

    async def get_by_name(
        self,
        project_name: str,
        session: AsyncSession
    ) -> Optional[CharityProject]:
        charity_project = (
            await session.execute(
                select(self.model).where(self.model.name == project_name)
            )
        )
        return charity_project.scalars().all()


charity_project_crud = CharityProjectCrud(CharityProject)
