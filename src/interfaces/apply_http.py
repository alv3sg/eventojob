from __future__ import annotations
from .schemas import *
from .dependences import *
from domain.entities import *
from application.ports import *
from application.user_cases import *
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/apply", tags=["apply"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ----- Endpoints -----


@router.post("", status_code=status.HTTP_201_CREATED)
def apply_offer(
    offer_id: str,
    user_id: str,
    offer_repo=Depends(get_offer_repo),
    user_repo=Depends(get_user_repo),
):
    try:
        offer = ApplyOffer(offers=offer_repo, users=user_repo).execute(
            offer_id=offer_id, user_id=user_id)
        return offer
    except Exception as e:
        raise e
