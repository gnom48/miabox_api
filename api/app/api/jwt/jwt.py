from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta
from ...database.models import UserOrm
from ..models import User
from ...repository import Repository


SECRET_KEY = "pro_nedvish"
ALGORITHM = "HS256"


def create_jwt_token(user: User):
    return jwt.encode(payload={'sub': user.id}, key=SECRET_KEY, algorithm=ALGORITHM)


async def verify_jwt_token(token: str) -> UserOrm:
    if token is None:
        raise HTTPException(status_code=400, detail="invalid token")

    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=['HS256', 'RS256'])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="invalid token")
    
    user = await Repository.get_user_by_id(payload['sub'])
    if not user:
        raise HTTPException(status_code=400, detail="invalid token")

    return user