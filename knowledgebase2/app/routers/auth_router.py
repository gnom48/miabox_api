from fastapi import FastAPI, Header, Request, Response, APIRouter, Depends, UploadFile, status, HTTPException
from fastapi.responses import HTMLResponse
from app.models import *
from app.services import AuthApiService
from app.settings import templates, Settings
from time import time

auth_router = APIRouter(prefix="")


@auth_router.get("/", response_class=HTMLResponse)
async def get_auth_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="auth_page.html", context={}
    )


@auth_router.post("/sign_in", response_class=HTMLResponse)
async def post_sign_in_data(
    response: Response,
    auth_data: SignInRequest,
    auth_api_service: AuthApiService = Depends(AuthApiService.service_factory)
):
    async with auth_api_service:
        token = await auth_api_service.sign_in(auth_data.login, auth_data.password)
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        resp = SignInRespose(regular_token=token)
        session_id = await Settings.session_manager.create_session(
            SessionData(
                user_id="",
                access_token=token,
                teams={},
                set_at=int(time())
            )
        )
        response.headers["X-Session-Id"] = session_id
        return resp.model_dump_json()
