from io import BytesIO
import uuid
from fastapi import FastAPI, Header, Request, APIRouter, Depends, UploadFile, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.models import *
from app.services import AuthApiService, CoreApiService
from starlette.middleware.sessions import SessionMiddleware
from app.toml_helper import load_var_from_toml

app = FastAPI(title='Knowledgebase')

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

app.add_middleware(SessionMiddleware,
                   secret_key=load_var_from_toml("access", "secret_key"))

# uvicorn app.main:app --host 0.0.0.0 --port 80 --reload --log-level debug

base_router = APIRouter(prefix="/base")


@base_router.get("/teams", response_class=HTMLResponse)
async def get_teams_page(
    request: Request,
    token: str | None = Header(alias="Authorization", default=None),
    auth_api_service: AuthApiService = Depends(AuthApiService.service_factory),
    core_api_service: CoreApiService = Depends(CoreApiService.service_factory)
):
    if token is None:
        return RedirectResponse(url="/main", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

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
            return templates.TemplateResponse(
                request=request, name="list_teams.html", context={
                    "teams": {
                        team_response.team.id: {"name": team_response.team.name, "is_admin": __get_my_role(team_response.members, who_am_i_response.user.id) == 'OWNER'} for team_response in teams_response.teams
                    }
                }
            )


@base_router.post("/upload", response_class=HTMLResponse)
async def upload(
    request: Request,
    token: str | None = Header(alias="Authorization", default=None),
    team_id: str | None = Header(alias="X-Team-Id", default=None),
    auth_api_service: AuthApiService = Depends(AuthApiService.service_factory),
    core_api_service: CoreApiService = Depends(CoreApiService.service_factory)
):
    if token is None:
        return RedirectResponse(url="/main", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    async with auth_api_service:  # REVIEW: не нужно для функционал - можно убрать
        who_am_i_response = await auth_api_service.who_am_i(token)
        if not who_am_i_response or not who_am_i_response.user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        if not who_am_i_response.user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        text = await request.body()
        text = text.decode('utf-8')

        file_content = BytesIO(text.encode('utf-8'))
        file = UploadFile(
            filename=f"{team_id}.html", file=file_content)

        async with core_api_service:
            file_id_response = await core_api_service.upload_file(team_id=team_id, token=token, file=file)
            if not file_id_response:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Unable to post')
            return file_id_response


@base_router.get("/{team_id}", response_class=HTMLResponse)
async def get_knowledgebase_by_team_id(
    request: Request,
    team_id: str,
    is_admin: bool | None = Header(alias="X-Is-Admin", default=False),
    token: str | None = Header(alias="Token", default=None),
    core_api_service: CoreApiService = Depends(CoreApiService.service_factory)
):
    if token is None:
        return RedirectResponse(url="/main", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    async with core_api_service:
        return templates.TemplateResponse(
            request=request, name="knowledgebase_container.html", context={
                "team_id": team_id,
                "html_content": await core_api_service.download_file(token, team_id),
                # "html_content": """<div class="section-wrapper" style="position: relative;"><h2 class="section-title" contenteditable="true">XYQ рwefowefpqwerfаздела</h2><div class="editor" contenteditable="true">wefmqwenfgger<div>g</div><div>ertghwr</div><div>th</div><div>wrt</div><div>h</div><div>rt</div><div>h</div><div>rwt</div><div>hwr</div><div>th</div><div>wrt</div><div>h</div><div>r</div><div>th</div><div>rt</div><div>h</div><div>rt</div><div>h</div></div><div class="delete-button">✖</div></div><div class="section-wrapper" style="position: relative;"><h2 class="section-title" contenteditable="true">Название раздwefq3w4eg34g3ergerела</h2><div class="editor" contenteditable="true">er<div>g</div><div>er</div><div>g</div><div>er</div><div>gqe</div><div>rg</div><div>45eg45eg5rg</div><div>ergre</div><div>g</div><div><br></div><div>erggggggggggggggggggggggggggggggggggggggggggggggerggggggggggggggggggggggggggggggggggggggggggggggerggggggggggggggggggggggggggggggggggggggggggggggerggggggggggggggggggggggggggggggggggggggggggggggerggggggggggggggggggggggggggggggggggggggggggggggerggggggggggggggggggggggggggggggggggggggggggggggerggggggggggggggggggggggggggggggggggggggggggggggerggggggggggggggggggggggggggggggggggggggggggggggerggggggggggggggggggggggggggggggggggggggggggggggerggggggggggggggggggggggggggggggggggggggggggggggergggggggggggggggggggggggggggggggggggggggggggggg</div><div><br></div><div>f</div><div>g</div><div><br></div><div>gg</div><div><br></div><div>g</div><div><br></div><div><br></div><div><br></div><div>ff</div></div><div class="delete-button">✖</div></div>""",
                "is_admin": is_admin
            }
        )


app.include_router(base_router)


auth_router = APIRouter(prefix="/main")


@auth_router.get("/", response_class=HTMLResponse)
async def get_auth_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="auth_page.html", context={}
    )


@auth_router.post("/sign_in", response_class=HTMLResponse)
async def post_sign_in_data(
    auth_data: SignInRequest,
    auth_api_service: AuthApiService = Depends(AuthApiService.service_factory)
):
    async with auth_api_service:
        token = await auth_api_service.sign_in(auth_data.login, auth_data.password)
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        resp = SignInRespose(regular_token=token)
        return resp.model_dump_json()


app.include_router(auth_router)
