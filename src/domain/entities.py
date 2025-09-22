from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
import re
import uuid
from typing import List, ClassVar

# --- Domain Errors ---


class DomainError(Exception):
    ...


class UserLocked(DomainError):
    ...


class TokenExpired(DomainError):
    ...


class InvalidEmail(DomainError):
    ...


class InvalidPasswordHash(DomainError):
    ...


class InvalidUserType(DomainError):
    ...


_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# --- Value Objects / Enums ---


class UserStatus(str, Enum):
    ACTIVE = "active"
    LOCKED = "locked"


class OfferStatus(str, Enum):
    ACTIVE = "active"
    DELETED = "deleted"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class Id:
    value: uuid.UUID

    @staticmethod
    def new() -> "Id":
        return Id(uuid.uuid4())


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        normalized = self.value.strip().lower()
        if not _EMAIL_REGEX.match(normalized):
            raise InvalidEmail("Email inválido")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True)
class PasswordHash:
    value: str

    def __post_init__(self):
        if not self.value or len(self.value) < 20:
            raise InvalidPasswordHash("Hash de senha inválido")


@dataclass(frozen=True)
class Experience:
    activity: str
    months: int

    def __post_init__(self):
        if self.months < 0:
            raise DomainError("Months of experience cannot be negative")


@dataclass(frozen=True)
class OfferDescription:
    title: str
    location: str
    salary: int
    requirements: str
    description: str
    start_date: datetime
    end_date: datetime

# Optional VO to avoid leaking UUIDs around

# --- Entities ---


@dataclass
class User:
    id: Id
    email: Email
    password_hash: PasswordHash
    name: str
    last_name: str
    phone: str
    roles: List[str]
    skills: List[str]
    ratings: List[float]
    status: UserStatus = UserStatus.ACTIVE
    applications: List[str] = field(default_factory=list)
    offer: List[str] = field(default_factory=list)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))

    def change_email(self, new_email: Email) -> None:
        self.email = new_email

    def change_password(self, new_password_hash: PasswordHash) -> None:
        self.password_hash = new_password_hash

    def change_roles(self, new_roles: List[str]) -> None:
        self.roles = new_roles

    def change_skills(self, new_skills: List[str]) -> None:
        self.skills = new_skills

    def change_ratings(self, new_ratings: List[float]) -> None:
        self.ratings = new_ratings

    def applied(self, offer_id: str) -> None:
        self.applications.append(offer_id)

    def offeried(self, offer_id: str) -> None:
        self.offer.append(offer_id)

    def ensure_can_authenticate(self) -> None:
        if self.status != UserStatus.ACTIVE:
            raise UserLocked("Usuário bloqueado")

    def lock(self) -> None:
        self.status = UserStatus.LOCKED

    def issue_refresh_token(
        self,
        token_id: uuid.UUID,
        ttl: timedelta,
        now: datetime | None = None
    ) -> "RefreshToken":
        self.ensure_can_authenticate()
        now = now or datetime.now(timezone.utc)
        return RefreshToken(
            id=token_id,
            user_id=self.id,                    # <-- keep as Id
            issued_at=now,
            expires_at=now + ttl,
            revoked_at=None,
        )

    def issue_offer(self, description: OfferDescription) -> "Offer":
        return Offer(
            id=uuid.uuid4(),
            user_id=self.id,                    # <-- keep as Id
            description=description,
        )


@dataclass
class RefreshToken:
    id: uuid.UUID
    user_id: Id
    issued_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None

    def ensure_active(self, at: datetime | None = None) -> None:
        at = at or datetime.now(timezone.utc)
        if self.revoked_at is not None or at >= self.expires_at:
            raise TokenExpired("Refresh token expirado ou revogado.")

    def revoke(self, at: datetime | None = None) -> None:
        if self.revoked_at is None:
            self.revoked_at = at or datetime.now(timezone.utc)


@dataclass
class Offer:
    id: uuid.UUID
    user_id: Id
    description: OfferDescription
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))
    status: OfferStatus = OfferStatus.ACTIVE
    applications: List[str] = field(default_factory=list)

    def update(self, description: OfferDescription) -> None:
        self.description = description
        self.updated_at = datetime.now(timezone.utc)

    def delete(self) -> None:
        self.status = OfferStatus.DELETED
        self.updated_at = datetime.now(timezone.utc)

    def archive(self) -> None:
        self.status = OfferStatus.ARCHIVED
        self.updated_at = datetime.now(timezone.utc)

    def apply(self, user_id: str) -> None:
        self.applications.append(user_id)
