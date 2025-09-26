from __future__ import annotations
from .schemas import *
from .dependences import *
from domain.entities import *
from application.ports import *
from application.user_cases import *
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/offers", tags=["offers"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ----- Endpoints -----


@router.post("", response_model=CreateOfferResponse, status_code=status.HTTP_201_CREATED)
def create_offer(
    body: CreateOfferRequest,
    user_repo=Depends(get_user_repo),
    offer_repo=Depends(get_offer_repo),
    current_user=Depends(require_auth)
):
    try:
        uc = CreateOffer(users=user_repo, offers=offer_repo)
        offer = uc.execute(
            user_id=Id(current_user.user_id),
            title=body.title,
            requirements=body.requirements,
            description=body.description,
            location=body.location,
            salary=body.salary,
            start_date=body.start_date,
            end_date=body.end_date,
        )

        return CreateOfferResponse(
            id=Id(offer.id),
        )
    except Exception as e:
        raise e


@router.get("/{offer_id}", response_model=OfferResponse)
def get_offer(
    offer_id: str,
    offer_repo=Depends(get_offer_repo),
):
    try:
        offer = GetOffer(offers=offer_repo).execute(offer_id=offer_id)
        return OfferResponse(
            id=Id(offer.id.value),
            user_id=Id(offer.user_id.value),
            description={
                "title": offer.description.title,
                "location": offer.description.location,
                "salary": offer.description.salary,
                "requirements": offer.description.requirements,
                "description": offer.description.description,
                "start_date": offer.description.start_date,
                "end_date": offer.description.end_date,
            },
            applications=[str(app) for app in offer.applications],
        )
    except Exception as e:
        raise e


@router.get("", response_model=list[OfferResponse])
def get_offers(
    offer_repo=Depends(get_offer_repo),
):
    try:
        offers = GetOffers(offers=offer_repo).execute()
        return [OfferResponse(
            id=Id(offer.id.value),
            user_id=Id(offer.user_id.value),
            description={
                "title": offer.description.title,
                "location": offer.description.location,
                "salary": offer.description.salary,
                "requirements": offer.description.requirements,
                "description": offer.description.description,
                "start_date": offer.description.start_date,
                "end_date": offer.description.end_date,
            },
            applications=[str(app) for app in offer.applications],
        ) for offer in offers]
    except Exception as e:
        raise e


@router.post("/{offer_id}/apply", status_code=status.HTTP_201_CREATED)
def apply_offer(
    offer_id: str,
    offer_repo=Depends(get_offer_repo),
    user_repo=Depends(get_user_repo),
    current_user=Depends(require_auth)
):
    try:
        offer = ApplyOffer(offers=offer_repo, users=user_repo).execute(
            offer_id=offer_id, user_id=current_user.user_id)
        return offer
    except Exception as e:
        raise e
