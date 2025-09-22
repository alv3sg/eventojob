from __future__ import annotations
from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from interfaces.dependences import require_auth
from core.infrastructure.db.settings import MongoSettings
from infrastructure.jwt_access_token import JwtAccessToken
from core.infrastructure.db.mongodb import get_mongo_client, get_db
from infrastructure.argon2_hasher import Argon2PasswordHasher
from infrastructure.mongo_user_repository import MongoUserRepository
from infrastructure.mongo_refresh_token_repository import MongoRefreshTokenRepository
from interfaces.errors import install_exception_handlers
from infrastructure.mongo_offer_repository import MongoOfferRepository
from interfaces.user_http import router as users_router
from interfaces.offer_http import router as offers_router
from interfaces.apply_http import router as apply_router
from interfaces.auth_http import router as auth_router

load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(title="FreeJob")

    # Infra adapters
    client = get_mongo_client(MongoSettings())
    db = get_db(client)
    app.state.hasher = Argon2PasswordHasher()
    app.state.access_tokens = JwtAccessToken()
    app.state.user_repo = MongoUserRepository(db["users"])
    app.state.offer_repo = MongoOfferRepository(db["offers"])
    app.state.refresh_repo = MongoRefreshTokenRepository(db["refresh_tokens"])

    # Interfaces
    app.include_router(users_router, prefix="/v1",
                       tags=["users"], dependencies=[Depends(require_auth)])
    app.include_router(offers_router, prefix="/v1",
                       tags=["offers"], dependencies=[Depends(require_auth)])
    app.include_router(apply_router, prefix="/v1",
                       tags=["apply"], dependencies=[Depends(require_auth)])
    app.include_router(auth_router, prefix="/v1", tags=["auth"])

    install_exception_handlers(app)
    return app


app = create_app()
