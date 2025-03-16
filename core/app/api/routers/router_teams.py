from fastapi import APIRouter, HTTPException, Header, Depends
from app.database import UserStatusesOrm, UserTeamOrm, Repository
from api.models import Team, UserTeam, UserStatuses
from app.api import get_user_from_request, UserCredentials


router_teams = APIRouter(prefix="/team", tags=["Команды"])


@router_teams.post("/create")
async def team_add(team: Team, user_credentials: UserCredentials = Depends(get_user_from_request)):
    ret_val_team_id = await Repository.add_team(data=team, user_id=user.id)
    if not ret_val_team_id:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="not able to create team")
    return ret_val_team_id


@router_teams.delete("/delete")
async def team_delete(team_id: str, user_credentials: UserCredentials = Depends(get_user_from_request)):
    return await Repository.del_team(team_id)


@router_teams.post("/join")
async def team_join(team_id: str, joined_by: int, user_credentials: UserCredentials = Depends(get_user_from_request)):
    try:
        if not await Repository.get_user_by_id(joined_by):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Пригласитель не действителен!")
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пригласитель не действителен!")
    user_team = UserTeamOrm()
    user_team.role = UserStatusesOrm.USER
    user_team.team_id = team_id
    user_team.user_id = user.id
    return await Repository.join_to_team(user_team)


@router_teams.put("/leave")
async def team_leave(team_id: str, user_credentials: UserCredentials = Depends(get_user_from_request)):
    return await Repository.leave_team(user_id=user.id, team_id=team_id)


@router_teams.put("/move_team_role")
async def move_team_role(team_id: str, user_id: str, role: UserStatuses, user_credentials: UserCredentials = Depends(get_user_from_request)):
    return await Repository.move_team_user_role(user_id=user.id, team_id=team_id, role=role)


@router_teams.get("/my_teams")
async def my_teams(user_credentials: UserCredentials = Depends(get_user_from_request)):
    return await Repository.get_all_teams_by_user_id(user.id)
