# auth/interfaces/auth_http.py
from .schemas import *
from .dependences import *
from datetime import timedelta
from application.user_cases import *
from fastapi import APIRouter, Depends, HTTPException, status


router = APIRouter(prefix="", tags=["auth"])


@router.post("/register", response_model=CreateUserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    body: CreateUserRequest,
    user_repo=Depends(get_user_repo),
    hasher=Depends(get_hasher),
):
    try:
        uc = CreateUser(users=user_repo, hasher=hasher)
        user = uc.execute(**body.model_dump())
        return CreateUserResponse(
            id=user.id,
        )
    except Exception as e:
        raise e


@router.post("/login", response_model=LoginResponse)
def login(
    body: LoginRequest,
    user_repo=Depends(get_user_repo),
    refresh_repo=Depends(get_refresh_repo),
    hasher=Depends(get_hasher),
    access_tokens=Depends(get_access_tokens),
):
    uc = Login(
        users=user_repo,
        refresh_tokens=refresh_repo,
        hasher=hasher,
        access_tokens=access_tokens,
        access_ttl=timedelta(minutes=30),
        refresh_ttl=timedelta(days=7),
    )
    try:
        result = uc.execute(email=body.email, password=body.password)
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return LoginResponse(
        user_id=result["user_id"],
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
    )


@router.post("/refresh", response_model=LoginResponse)
def refresh(
    body: TokenRefreshRequest,
    refresh_repo=Depends(get_refresh_repo),
    access_tokens=Depends(get_access_tokens),
):
    uc = CreateNewAccessToken(
        refresh_tokens=refresh_repo,
        access_tokens=access_tokens,
        access_ttl=timedelta(minutes=30),
    )
    try:
        result = uc.execute(refresh_token=body.refresh_token)
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return LoginResponse(
        user_id=result["user_id"],
        access_token=result["access_token"],
        refresh_token=body.refresh_token,
    )


@router.post("/logout")
def logout(
    body: TokenRefreshRequest,
    refresh_repo=Depends(get_refresh_repo),
    access_tokens=Depends(get_access_tokens),
):
    uc = Logout(
        refresh_tokens=refresh_repo
    )
    try:
        uc.execute(refresh_token=body.refresh_token)
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return
