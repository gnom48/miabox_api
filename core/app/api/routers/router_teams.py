from fastapi import APIRouter, HTTPException, Depends, status
from app.database.repositories import TeamsRepository, UsersRepository
from app.api.models import Team, UserTeam, UserStatuses
from app.api.middlewares import get_user_from_request
from app.api.models import UserCredentials

router_teams = APIRouter(prefix="/team", tags=["Команды"])


@router_teams.post("/create", status_code=status.HTTP_201_CREATED)
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


@router_teams.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_team(
    team_id: str,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    teams_repository: TeamsRepository = Depends(
        TeamsRepository.repository_factory)
):
    async with teams_repository:
        success = await teams_repository.delete_team(team_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Team not found or unable to delete")
        return {"detail": "Team deleted successfully"}


@router_teams.post("/join", status_code=status.HTTP_200_OK)
async def join_team(
    team_id: str,
    joined_by: str,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    teams_repository: TeamsRepository = Depends(
        TeamsRepository.repository_factory)
):
    async with teams_repository:
        if not teams_repository.can_user_invite(user_id=user_credentials.id, team_id=team_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")

        user_team = UserTeam(role=UserStatuses.USER,
                             team_id=team_id, user_id=user_credentials.id)
        success = await teams_repository.join_to_team(user_team)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to join team")
        return {"detail": "Joined team successfully"}


@router_teams.put("/leave", status_code=status.HTTP_200_OK)
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


@router_teams.put("/move_team_role", status_code=status.HTTP_200_OK)
async def move_team_role(
    team_id: str,
    user_id: str,
    role: UserStatuses,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    teams_repository: TeamsRepository = Depends(
        TeamsRepository.repository_factory)
):
    async with teams_repository:
        success = await teams_repository.move_team_user_role(team_id, user_id, role)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to change role")
        return {"detail": "Role changed successfully"}


@router_teams.get("/my_teams", status_code=status.HTTP_200_OK)
async def get_my_teams(
    user_credentials: UserCredentials = Depends(get_user_from_request),
    teams_repository: TeamsRepository = Depends(
        TeamsRepository.repository_factory)
):
    async with teams_repository:
        # await teams_repository.get_all_teams_by_user_id(user_credentials.id)
        teams = []
        if teams is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No teams found")
        return teams
