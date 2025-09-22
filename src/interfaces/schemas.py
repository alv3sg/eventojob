from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Dict
from uuid import UUID
from datetime import datetime
from domain.entities import *
# ---- Requests ----


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str
    last_name: str
    phone: str | None = None
    roles: List[str] | None = None
    skills: List[str] | None = None


class CreateOfferRequest(BaseModel):
    title: str
    location: str
    salary: int
    requirements: str
    description: str
    start_date: datetime
    end_date: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str

# ---- Responses ----


class UserResponse(BaseModel):
    id: Id
    email: EmailStr
    name: str
    last_name: str
    phone: str | None = None
    roles: List[str] | None = None
    skills: List[str] | None = None
    ratings: List[float] | None = None
    status: UserStatus
    applications: list[str]
    offer: list[str]
    created_at: datetime


class CreateOfferResponse(BaseModel):
    id: Id


class CreateUserResponse(BaseModel):
    id: Id


class OfferResponse(BaseModel):
    id: Id
    description: OfferDescription
    applications: list[str]


class LoginResponse(BaseModel):
    user_id: Id
    access_token: str
    token_type: str = "bearer"
    refresh_token: str
