from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, update
from app.database.models import TeamOrm, UserTeamOrm, UserStatusesOrm, UserOrm, AddressOrm, CallOrm
from .base_repository import BaseRepository
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.api.models import *
    from app.common.models import *


class TeamsRepository(BaseRepository):
    """
    Класс репозиторий для работы с командами в базе данных.
    """

    @staticmethod
    def repository_factory():
        return TeamsRepository()

    async def get_all_teams_by_user_id(self, user_id: str) -> list['TeamWithInfo'] | None:
        """Возвращает все команды, связанные с пользователем, с дополнительной информацией."""
        from app.common.models import TeamWithInfo, UserWithRole
        from app.api.models import Team, User, Address, Call, StatisticAggregated, Kpi
        try:
            async with self.session:
                query = select(UserTeamOrm).where(
                    UserTeamOrm.user_id == user_id)
                result = await self.session.execute(query)
                user_teams = result.scalars().all()

                teams_with_info = []
                for user_team in user_teams:
                    team = await self.session.get(TeamOrm, user_team.team_id)

                    query_userteam = select(UserTeamOrm).where(
                        UserTeamOrm.team_id == team.id)
                    result_team_users = await self.session.execute(query_userteam)
                    team_users = result_team_users.scalars().all()

                    teams_with_info.append(TeamWithInfo(team=Team.from_orm(team), members=[
                        UserWithRole(
                            user=User.from_orm(await self.session.get(UserOrm, team_user.user_id)),
                            role=team_user.role.name
                        ) for team_user in team_users
                    ]))
                return teams_with_info
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return None

    async def is_user_team_owner(self, user_id: str, team_id: str) -> bool:
        """Может ли пользователь пригласить пользователя в команду."""
        try:
            async with self.session:
                query = select(UserTeamOrm).where(
                    UserTeamOrm.user_id == user_id)
                result = await self.session.execute(query)
                team_user = result.scalars().first()
                return team_user.role == UserStatusesOrm.OWNER
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return None

    async def add_team(self, data: 'Team', user_id: str) -> str | None:
        """Добавляет новую команду в базу данных."""
        from app.api.models import Team, UserTeam, UserStatuses
        try:
            async with self.session:
                new_team = TeamOrm(**data.model_dump())
                new_team.id = None
                self.session.add(new_team)
                await self.session.commit()

                self.session.add(UserTeam(
                    role=UserStatuses.OWNER,
                    team_id=new_team.id,
                    user_id=user_id
                ))
                await self.session.commit()
                # await self.join_to_team(user_team)

                return new_team.id
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return None

    async def delete_team(self, team_id: str) -> bool:
        """Удаляет команду из базы данных."""
        try:
            async with self.session:
                team_to_delete = await self.session.get(TeamOrm, team_id)
                if team_to_delete:
                    await self.session.delete(team_to_delete)
                    await self.session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return False

    async def edit_team(self, data: 'Team') -> bool:
        """Редактирует информацию о команде в базе данных."""
        from app.api.models import Team
        try:
            async with self.session:
                team_to_edit = await self.session.get(TeamOrm, data.id)
                if team_to_edit:
                    team_to_edit.name = data.name
                    await self.session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return False

    async def join_to_team(self, data: 'UserTeam') -> bool:
        """Добавляет пользователя в команду."""
        from app.api.models import UserTeam
        try:
            async with self.session:
                self.session.add(UserTeamOrm(**data.model_dump()))
                await self.session.commit()
                return True
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return False

    async def move_team_user_role(self, team_id: str, user_id: str, role: 'UserStatuses') -> bool:
        """Изменяет роль пользователя в команде."""
        from app.api.models import UserStatuses
        try:
            async with self.session:
                role_orm = UserStatusesOrm.OWNER if role == UserStatuses.OWNER else UserStatusesOrm.USER
                query = (
                    update(UserTeamOrm)
                    .where(UserTeamOrm.team_id == team_id, UserTeamOrm.user_id == user_id)
                    .values(role=role_orm)
                )
                await self.session.execute(query)
                await self.session.commit()
                return True
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return False

    async def leave_team(self, user_id: str, team_id: str) -> bool:
        """Удаляет пользователя из команды."""
        try:
            async with self.session:
                query = select(UserTeamOrm).where(
                    UserTeamOrm.user_id == user_id, UserTeamOrm.team_id == team_id)
                result = await self.session.execute(query)
                user_team_to_delete = result.scalars().first()
                if user_team_to_delete:
                    await self.session.delete(user_team_to_delete)
                    await self.session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return False
