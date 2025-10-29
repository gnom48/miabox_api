import time
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query, status
from app.database.repositories import TeamsRepository, UsersRepository, StatisticsRepository, AddressesRepository, CallsRepository
from app.api.models import Team, UserTeam, UserStatuses
from app.api.middlewares import get_user_from_request
from app.api.models import UserCredentials
from app.common.models import *

router_teams = APIRouter(prefix="/teams", tags=["Команды"])


@router_teams.post("/", status_code=status.HTTP_201_CREATED, description="Создает команду и делает текущего пользователя ее Owner")
async def create_team(
    team: Team,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    teams_repository: TeamsRepository = Depends(
        TeamsRepository.repository_factory)
):
    async with teams_repository:
        team_id = await teams_repository.add_team(team, user_credentials.id)
        if not team_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to create team")
        return team_id


@router_teams.delete("/{team_id}", status_code=status.HTTP_200_OK, description="Удаляет команду по Id, если текущий пользователь явялется в ней Owner")
async def delete_team(
    team_id: str,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    teams_repository: TeamsRepository = Depends(
        TeamsRepository.repository_factory)
):
    async with teams_repository:
        if not teams_repository.is_user_team_owner(user_id=user_credentials.id, team_id=team_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")
        success = await teams_repository.delete_team(team_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Team not found or unable to delete")
        return {"detail": "Team deleted successfully"}


@router_teams.post("/{team_id}/join", status_code=status.HTTP_200_OK, description="Присоединиться к команде по Id с ролью User; приграсить в команду может только пользователь с ролью Owner")
async def join_team(
    team_id: str,
    joined_by: str,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    teams_repository: TeamsRepository = Depends(
        TeamsRepository.repository_factory)
):
    async with teams_repository:
        if not teams_repository.is_user_team_owner(user_id=joined_by, team_id=team_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")

        user_team = UserTeam(role=UserStatuses.USER,
                             team_id=team_id, user_id=user_credentials.id)
        success = await teams_repository.join_to_team(user_team)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to join team")
        return {"detail": "Joined team successfully"}


@router_teams.put("/{team_id}/leave", status_code=status.HTTP_200_OK, description="Покинуть команду")
async def leave_team(
    team_id: str,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    teams_repository: TeamsRepository = Depends(
        TeamsRepository.repository_factory)
):
    async with teams_repository:
        success = await teams_repository.leave_team(user_credentials.id, team_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to leave team")
        return {"detail": "Left team successfully"}


@router_teams.put("/{team_id}/user/{user_id}/role", status_code=status.HTTP_200_OK, description="Назначить участнику команды новую роль; для этого действия текущий пользователь должен являться Owner в этой команде")
async def set_user_role_in_team(
    team_id: str,
    user_id: str,
    role: UserStatuses,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    teams_repository: TeamsRepository = Depends(
        TeamsRepository.repository_factory)
):
    async with teams_repository:
        if not teams_repository.is_user_team_owner(user_id=user_credentials.id, team_id=team_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")
        success = await teams_repository.move_team_user_role(team_id, user_id, role)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to change role")
        return {"detail": "Role changed successfully"}


@router_teams.get("/", status_code=status.HTTP_200_OK, description="Возвращяет полную информацию обо всех командах, в которых состоит текущий пользователь; также об их участниках и статистиках (пока только статистики), если текущий пользователь является Owner")
async def get_my_teams(
    show_stats: bool = Query(default=False),
    show_addresses: bool = Query(default=False),
    show_calls: bool = Query(default=False),
    user_credentials: UserCredentials = Depends(get_user_from_request),
    teams_repository: TeamsRepository = Depends(
        TeamsRepository.repository_factory),
    statistics_repository: StatisticsRepository = Depends(
        StatisticsRepository.repository_factory),
    address_repository: AddressesRepository = Depends(
        AddressesRepository.repository_factory),
    calls_repository: CallsRepository = Depends(
        CallsRepository.repository_factory)
):
    async with teams_repository:
        teams = await teams_repository.get_all_teams_by_user_id(user_credentials.id)
        if teams is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No teams found")
        if show_stats:
            async with statistics_repository:
                now = datetime.now()
                first_day_of_month = datetime(now.year, now.month, 1)
                start_unix = int(time.mktime(first_day_of_month.timetuple()))
                if now.month == 12:
                    last_day_of_month = datetime(
                        now.year + 1, 1, 1) - timedelta(days=1)
                else:
                    last_day_of_month = datetime(
                        now.year, now.month + 1, 1) - timedelta(days=1)
                end_unix = int(time.mktime(last_day_of_month.timetuple()))
                # NOTE: здесь start и end - это первое и последнее число текущего календарного месяца
                for t in teams:
                    for m in t.members:
                        m.stats = await statistics_repository.get_statistics_in_period(m.user.id, start_unix, end_unix)
                        m.kpi = await statistics_repository.get_last_month_kpi(m.user.id)
        if show_calls:
            async with calls_repository:
                # TODO: потом дописать
                ...
        if show_addresses:
            async with address_repository:
                # TODO: потом дописать
                ...
        return teams
