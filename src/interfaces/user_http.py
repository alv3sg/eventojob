from __future__ import annotations
from .schemas import *
from .dependences import *
from domain.entities import *
from application.ports import *
from application.user_cases import *
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/users", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ----- Endpoints -----


@router.get("", response_model=UserResponse)
def get_user(
    user_repo=Depends(get_user_repo),
    current_user=Depends(require_auth),
):
    try:
        uc = GetUser(users=user_repo)
        user = uc.execute(user_id=Id(current_user.user_id))
        return UserResponse(
            id=user.id,
            email=user.email.value,
            name=user.name,
            last_name=user.last_name,
            phone=user.phone,
            roles=user.roles,
            skills=user.skills,
            ratings=user.ratings,
            status=user.status,
            created_at=user.created_at,
            applications=user.applications,
            offer=user.offer,
        )
    except Exception as e:
        raise e


@router.get("/all", response_model=list[UserResponse])
def get_users(
    user_repo=Depends(get_user_repo),
):
    try:
        uc = GetUsers(users=user_repo)
        users = uc.execute()
        return [UserResponse(
            id=user.id,
            email=user.email.value,
            name=user.name,
            last_name=user.last_name,
            phone=user.phone,
            roles=user.roles,
            skills=user.skills,
            ratings=user.ratings,
            status=user.status,
            created_at=user.created_at,
            applications=user.applications,
            offer=user.offer,
        ) for user in users]
    except Exception as e:
        raise e
