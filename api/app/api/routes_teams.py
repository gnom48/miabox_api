from fastapi import APIRouter, HTTPException, Header
from .jwt.jwt import verify_jwt_token
from api.app.database.models import UserStatusesOrm, UserTeamOrm
from api.app.repository import Repository
from .models import Team, UserTeam, UserStatuses


router_teams = APIRouter(prefix="/team", tags=["Команды"])


@router_teams.post("/create")
async def team_add(team: Team, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await verify_jwt_token(token_authorization)
    ret_val_team_id = await Repository.add_team(data=team, user_id=user.id)
    if not ret_val_team_id:
        raise HTTPException(status_code=402, detail="not able to create team")
    return ret_val_team_id


@router_teams.delete("/delete")
async def team_delete(team_id: str, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await verify_jwt_token(token_authorization)
    return await Repository.del_team(team_id)


@router_teams.post("/join")
async def team_join(team_id: str, joined_by: str, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await verify_jwt_token(token_authorization)
    try:
        if not await Repository.get_user_by_id(joined_by):
            raise HTTPException(status_code=404, detail="Пригласитель не действителен!")
    except:
        raise HTTPException(status_code=404, detail="Пригласитель не действителен!")
    user_team = UserTeamOrm()
    user_team.role = UserStatusesOrm.USER
    user_team.team_id = team_id
    user_team.user_id = user.id
    return await Repository.join_to_team(user_team)


@router_teams.put("/leave")
async def team_leave(team_id: str, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await verify_jwt_token(token_authorization)
    return await Repository.leave_team(user_id=user.id, team_id=team_id)


@router_teams.put("/move_team_role")
async def move_team_role(team_id: str, user_id: str, role: UserStatuses, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await verify_jwt_token(token_authorization)
    return await Repository.move_team_user_role(user_id=user.id, team_id=team_id, role=role)


@router_teams.get("/my_teams")
async def my_teams(token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await verify_jwt_token(token_authorization)
    return await Repository.get_all_teams_by_user_id(user.id)


