from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charity_project import CharityProject
from app.models.donation import Donation


class TransactionInvesting:
    async def recalculate_project_status(
        self,
        project: CharityProject,
        session: AsyncSession
    ) -> None:
        if project.full_amount == project.invested_amount:
            project.fully_invested = True
            project.close_date = datetime.now()
            session.add(project)
            await session.commit()

    async def launch_investing_proccess(self, session: AsyncSession) -> None:
        """
        Проводит процесс транзакции для начисления денег с
        доступных пожертвований в проекты.
        """
        open_charity_projects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested == False
            ).order_by(CharityProject.create_date)
        )
        open_charity_projects = open_charity_projects.scalars().all()
        if not open_charity_projects:
            return

        available_donations = await session.execute(
            select(Donation).where(
                Donation.fully_invested == False
            ).order_by(Donation.create_date)
        )
        available_donations = available_donations.scalars().all()
        if not available_donations:
            return

        project_index = 0
        donation_index = 0
        while (
            project_index < len(open_charity_projects) and
            donation_index < len(available_donations)
        ):
            current_project: CharityProject = (
                open_charity_projects[project_index]
            )
            needed_project_amount = (
                current_project.full_amount - current_project.invested_amount
            )
            current_donation: Donation = available_donations[donation_index]
            actual_donation_amount = (
                current_donation.full_amount - current_donation.invested_amount
            )
            if actual_donation_amount > needed_project_amount:
                remainder_donation_amount = (
                    actual_donation_amount - needed_project_amount
                )
                current_donation.invested_amount = (
                    current_donation.full_amount - remainder_donation_amount
                )

                current_project.invested_amount = current_project.full_amount
                current_project.fully_invested = True
                current_project.close_date = datetime.now()

                session.add(current_donation)
                session.add(current_project)
                project_index += 1
            elif actual_donation_amount == needed_project_amount:
                current_donation.invested_amount = current_donation.full_amount
                current_donation.fully_invested = True
                current_donation.close_date = datetime.now()

                current_project.invested_amount = current_project.full_amount
                current_project.fully_invested = True
                current_project.close_date = datetime.now()

                session.add(current_donation)
                session.add(current_project)
                project_index += 1
                donation_index += 1
            else:
                current_project.invested_amount += actual_donation_amount
                needed_project_amount -= actual_donation_amount

                current_donation.invested_amount = current_donation.full_amount
                current_donation.fully_invested = True
                current_donation.close_date = datetime.now()

                session.add(current_donation)
                session.add(current_project)
                donation_index += 1

            await session.commit()


transaction_mechanism = TransactionInvesting()
