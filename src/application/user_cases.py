# app/auth/application/use_cases.py
from __future__ import annotations
from dataclasses import dataclass
from domain.entities import *
from .ports import *
from uuid import uuid4


@dataclass
class CreateUser:
    users: UserRepository
    hasher: PasswordHasher

    def execute(self, *, email: str, password: str, name: str, last_name: str, phone: str | None = None, roles: List[str] | None = None, skills: List[str] | None = None, ratings: List[float] | None = None) -> User:
        try:
            email_vo = Email(email)
            self.users.exists_by_email(email_vo)
        except Exception as e:
            raise e
        try:
            password_hash = PasswordHash(self.hasher.hash(password))
        except Exception as e:
            raise e
        try:
            user = User(
                id=Id.new(),
                email=email_vo,
                password_hash=password_hash,
                name=name,
                last_name=last_name,
                phone=phone,
                roles=roles,
                skills=skills,
                ratings=ratings,
                status=UserStatus.ACTIVE,
            )
            self.users.create(user)
            return user
        except Exception as e:
            raise e


@dataclass
class GetUser:
    users: UserRepository

    def execute(self, *, user_id: Id) -> User:
        try:
            user = self.users.read(user_id)
            return user
        except Exception as e:
            raise e


@dataclass
class GetUsers:
    users: UserRepository

    def execute(self, *, limit: int = 50, offset: int = 0) -> list[User]:
        try:
            users = self.users.read_all(limit=limit, offset=offset)
            return users
        except Exception as e:
            raise e


@dataclass
class CreateOffer:
    offers: OfferRepository
    users: UserRepository

    def execute(self, *, user_id: Id, title: str, requirements: str, description: str, location: str, salary: int, start_date: datetime, end_date: datetime):

        try:
            user = self.users.read(user_id)
        except Exception as e:
            raise e
        try:
            offerDescription = OfferDescription(
                title=title,
                location=location,
                salary=salary,
                requirements=requirements,
                description=description,
                start_date=start_date,
                end_date=end_date,
            )
            offer = user.issue_offer(description=offerDescription)
            self.offers.create(offer)
            user.offeried(str(offer.id))
            self.users.save(user)
            return offer
        except Exception as e:
            raise e


@dataclass
class GetOffer:
    offers: OfferRepository

    def execute(self, *, offer_id: Id) -> Offer:
        try:
            offer = self.offers.read(offer_id)
            return offer
        except Exception as e:
            raise e


@dataclass
class GetOffers:
    offers: OfferRepository

    def execute(self, *, limit: int = 50, offset: int = 0) -> list[Offer]:
        try:
            offers = self.offers.list(limit=limit, offset=offset)
            return offers
        except Exception as e:
            raise e


@dataclass
class ApplyOffer:
    offers: OfferRepository
    users: UserRepository

    def execute(self, *, offer_id: str, user_id: str):
        try:
            user = self.users.read(Id(user_id))
        except Exception as e:
            raise e
        try:
            offer = self.offers.read(Id(offer_id))
        except Exception as e:
            raise e
        try:
            offer.apply(user_id)
            self.offers.update(offer)
            user.applied(offer_id)
            self.users.update(user)
            return offer
        except Exception as e:
            raise e


@dataclass
class Login:
    users: UserRepository
    refresh_tokens: RefreshTokenRepository
    hasher: PasswordHasher
    access_tokens: AccessTokenEncoder
    access_ttl: timedelta = timedelta(minutes=30)
    refresh_ttl: timedelta = timedelta(days=7)

    def execute(self, *, email: str, password: str):
        email_vo = Email(email)

        try:
            user_id, pwd_hash, status = self.users.get_auth_view_by_email(
                email_vo)
        except NotFound:
            raise Unauthorized("Invalid credentials.")

        if status != UserStatus.ACTIVE.value:
            raise Unauthorized("Invalid credentials.")

        if not self.hasher.verify(password, pwd_hash.value):
            raise Unauthorized("Invalid credentials.")

        user = self.users.read(user_id)
        refresh = user.issue_refresh_token(
            token_id=uuid4(), ttl=self.refresh_ttl)
        self.refresh_tokens.create(refresh)

        access = self.access_tokens.encode(
            AccessTokenClaims(
                sub=str(user_id.value),
                exp=datetime.now(timezone.utc) + self.access_ttl,
                iat=datetime.now(timezone.utc),
                jti=str(uuid4()),
                typ="access",
            )
        )

        return {"user_id": user_id, "access_token": access, "refresh_token": str(refresh.id)}


@dataclass
class CreateNewAccessToken:
    refresh_tokens: RefreshTokenRepository
    access_tokens: AccessTokenEncoder
    access_ttl: timedelta = timedelta(minutes=30)
    refresh_ttl: timedelta = timedelta(days=7)

    def execute(self, *, refresh_token: str):
        try:
            refresh = self.refresh_tokens.read(refresh_token)
        except NotFound:
            raise Unauthorized("Invalid refresh token.")
        try:
            refresh.ensure_active(datetime.now(timezone.utc))
        except TokenExpired:
            raise Unauthorized("Invalid refresh token.")
        access = self.access_tokens.encode(
            AccessTokenClaims(
                sub=str(refresh.user_id.value),
                exp=datetime.now(timezone.utc) + self.access_ttl,
                iat=datetime.now(timezone.utc),
                jti=str(uuid4()),
                typ="access",
            )
        )
        return {"user_id": refresh.user_id, "access_token": access}


@dataclass
class Logout:
    refresh_tokens: RefreshTokenRepository

    def execute(self, *, refresh_token: str):
        try:
            refresh = self.refresh_tokens.read(refresh_token)
        except NotFound:
            raise Unauthorized("Invalid refresh token.")
        try:
            refresh.revoke()
            self.refresh_tokens.save(refresh)
        except TokenExpired:
            raise Unauthorized("Invalid refresh token.")
