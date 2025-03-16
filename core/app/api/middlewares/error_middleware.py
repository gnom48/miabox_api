from fastapi import Request, status
from fastapi.responses import JSONResponse


async def error_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": e.__str__()})
