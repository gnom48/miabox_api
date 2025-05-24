from io import BytesIO
from time import time
from fastapi import FastAPI, Header, Request, APIRouter, Depends, Response, UploadFile, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from app.models import *
from app.services import AuthApiService, CoreApiService
from app.settings import templates, Settings
import uuid

main_router = APIRouter(prefix="/base")


@main_router.get("/teams", response_class=HTMLResponse)
async def get_teams_page(
    request: Request,
    response: Response,
    token: str | None = Header(alias="Authorization", default=None),
    session_id: str | None = Header(alias="X-Session-Id", default=None),
    auth_api_service: AuthApiService = Depends(AuthApiService.service_factory),
    core_api_service: CoreApiService = Depends(CoreApiService.service_factory)
):
    session_data: SessionData = None
    if session_id is not None:
        session_data = await Settings.session_manager.get_session(session_id)
        if session_data is None:
            if token is None:
                return RedirectResponse(url="/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            session_data = SessionData(
                user_id="",
                access_token=token,
                teams={},
                set_at=int(time())
            )
    else:
        if token is None:
            return RedirectResponse(url="/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        session_data = SessionData(
            user_id="",
            access_token=token,
            teams={},
            set_at=int(time())
        )
        session_id = str(uuid.uuid4())

    def __get_my_role(members: List[Member], my_id: str) -> str:
        for member in members:
            if member.user.id == my_id:
                return member.role
        return 'USER'

    async with auth_api_service:
        who_am_i_response = await auth_api_service.who_am_i(token)
        if not who_am_i_response or not who_am_i_response.user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        if not who_am_i_response.user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        async with core_api_service:
            teams_response = await core_api_service.get_my_teams(token=token)
            if not teams_response or len(teams_response.teams) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail='No teams founded')
            session_data.user_id = who_am_i_response.user.id
            session_data.set_at = int(time())
            session_data.teams = {
                team_response.team.id: {"name": team_response.team.name, "is_admin": __get_my_role(team_response.members, who_am_i_response.user.id) == 'OWNER'} for team_response in teams_response.teams
            }
            await Settings.session_manager.update_session(session_id, session_data)
            response.headers["X-Session-Id"] = session_id
            return templates.TemplateResponse(
                request=request, name="list_teams.html", context={
                    "teams": session_data.teams,
                    "session_id": session_id
                }
            )


@main_router.get("/{team_id}", response_class=HTMLResponse)
async def get_knowledgebase_by_team_id(
    request: Request,
    team_id: str,
    session_id: str | None = Header(alias="X-Session-Id", default=None),
    core_api_service: CoreApiService = Depends(CoreApiService.service_factory)
):
    if session_id is None:
        return RedirectResponse(url="/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    session_data = await Settings.session_manager.get_session(session_id)
    if session_data is None:
        return RedirectResponse(url="/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    async with core_api_service:
        try:
            return templates.TemplateResponse(
                request=request, name="knowledgebase_container.html", context={
                    "team_id": team_id,
                    "team_name": session_data.teams[team_id]["name"],
                    "html_content": await core_api_service.download_file(session_data.access_token, team_id),
                    "is_admin": session_data.teams[team_id]["is_admin"]
                }
            )
        except:
            return RedirectResponse(url="/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@main_router.post("/upload", response_class=HTMLResponse)
async def upload(
    request: Request,
    session_id: str | None = Header(alias="X-Session-Id", default=None),
    team_id: str | None = Header(alias="X-Team-Id", default=None),
    core_api_service: CoreApiService = Depends(CoreApiService.service_factory)
):
    if session_id is None:
        return RedirectResponse(url="/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    session_data = await Settings.session_manager.get_session(session_id)
    if session_data is None:
        return RedirectResponse(url="/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    text = await request.body()
    text = text.decode('utf-8')
    file_content = BytesIO(text.encode('utf-8'))
    file = UploadFile(filename=f"{team_id}.html", file=file_content)

    async with core_api_service:
        file_id_response = await core_api_service.upload_file(team_id=team_id, token=session_data.access_token, file=file)
        if not file_id_response:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Unable to post')
        return file_id_response
