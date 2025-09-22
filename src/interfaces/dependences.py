from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID
from application.ports import AccessTokenEncoder, UserRepository
import jwt
from domain.entities import UserLocked, Id
bearer_scheme = HTTPBearer(auto_error=True)

# ----- Dependency helpers pulling adapters from app.state -----


def get_user_repo(request: Request):
    return request.app.state.user_repo


def get_hasher(request: Request):
    return request.app.state.hasher


def get_access_tokens(request: Request):
    return request.app.state.access_tokens


def get_offer_repo(request: Request):
    return request.app.state.offer_repo


def get_refresh_repo(request: Request):
    return request.app.state.refresh_repo


class CurrentUser:
    def __init__(self, user_id: UUID, scope: str):
        self.user_id = user_id
        self.scope = scope


def require_auth(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    tokens: AccessTokenEncoder = Depends(get_access_tokens),
    users: UserRepository = Depends(get_user_repo),
) -> CurrentUser:
    token = creds.credentials
    try:
        claims = tokens.decode(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    user_id = claims["sub"]
    user = users.read(Id(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # Apply your domain rule (locked users cannot authenticate)
    try:
        user.ensure_can_authenticate()
    except UserLocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is locked")

    return CurrentUser(user_id=user_id, scope=claims.get("scope", ""))
