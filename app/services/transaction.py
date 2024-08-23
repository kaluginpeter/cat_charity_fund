from datetime import datetime

from sqlalchemy import select, not_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charity_project import CharityProject
from app.models.donation import Donation


class TransactionInvesting:
    async def recalculate_project_status(
        self,
        project: CharityProject,
        session: AsyncSession
    ) -> None:
        """"
        Проводит проверку того, что после редактирования проекта,
        его необходимая сумма не набрана. Если сумма набранна, то
        проект закрывается, в проитвном случае ничего не происходит.
        """
        if project.full_amount == project.invested_amount:
            project.fully_invested = True
            project.close_date = datetime.now()
            session.add(project)
            await session.commit()

    async def launch_investing_proccess(self, session: AsyncSession) -> None:
        """
        Проводит процесс транзакции для начисления денег с
        доступных пожертвований в проекты.
        Использует алгоритм "Двух указателей", чтобы выполнить
        необходимые расчеты.
        Логика работы:
        open_charity_projects - список всех доступных проектов, если он пуст,
            то функция прерывается.
        available_donations - списко доступных пожертвований, если список пуст,
            то функция прерывается.
        project_index и donation_index служат указателями на текущий эелемент
            в списках по своему названию соответственно.
        Далее запускаем цикл, пока не переберем все доступные проекты
            или пожертвования. В теле цикла инициализируем переменные:
        current_project и current_donation извлекают экземпляр модели из списка
            по индексам
        needed_project_amount - означает, сколько денег необходимо,
            чтобы набрать необходимую сумму для проекта.
        actual_donation_amount - означает, сколько денег доступно с текущего
            пожертвования
        Возможны 3 варианта в дереве принятия решений:
        - 1-ый) actual_donation_amount больше actual_donation_amount:
           Перерасчитываем остаток доступных денег с пожертвования;
            Устанавливаем проекту необходимую сумму;
            Помечаем проект, как, закрытый и устанавливаем
            время закрытия функцией datetime.now();
            Увеличиваем project_index на 1;
        - 2-ой) actual_donation_amount равна actual_donation_amount:
            Устанавливаем пожертвование, как полностью потраченное
                и закрываем его, устанавливаем при этом время закрытия;
            Устанавливаем проект, как закрытый и помечаем соответсвующее поле,
                указываем время закрытия;
            Увеличиваем project_index и donation_index на 1;
        - 3-ий) actual_donation_amount меньше actual_donation_amount:
            Устанавливаем пожертвование, как полностью потраченное
                и закрываем его, устанавливаем при этом время закрытия;
            Перерасчитываем необходмую сумму для проекта;
            Увеличивем donation_index на 1;
        В конце каждой итерации добавляем current_project и current_donation
        в индекс базы данных методом session.add(obj)
        После конца цикла закрепляем изменения в базе данных,
            методом session.commit()

        Асимптотическая сложность алгоритма O(N + M), где
            N - размер списка с доступными проектами,
            и M - разрмер списка с доступными пожертвованиями.
        Пространственная сложность аналогична асимптотической.
        """
        open_charity_projects = await session.execute(
            select(CharityProject).where(
                not_(CharityProject.fully_invested)
            ).order_by(CharityProject.create_date)
        )
        open_charity_projects = open_charity_projects.scalars().all()
        if not open_charity_projects:
            return

        available_donations = await session.execute(
            select(Donation).where(
                not_(Donation.fully_invested)
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
                current_donation.invested_amount += needed_project_amount

                current_project.invested_amount = current_project.full_amount
                current_project.fully_invested = True
                current_project.close_date = datetime.now()

                project_index += 1
            elif actual_donation_amount == needed_project_amount:
                current_donation.invested_amount = current_donation.full_amount
                current_donation.fully_invested = True
                current_donation.close_date = datetime.now()

                current_project.invested_amount = current_project.full_amount
                current_project.fully_invested = True
                current_project.close_date = datetime.now()

                project_index += 1
                donation_index += 1
            else:
                current_project.invested_amount += actual_donation_amount

                current_donation.invested_amount = current_donation.full_amount
                current_donation.fully_invested = True
                current_donation.close_date = datetime.now()

                donation_index += 1

            session.add(current_donation)
            session.add(current_project)
        await session.commit()


transaction_mechanism = TransactionInvesting()
