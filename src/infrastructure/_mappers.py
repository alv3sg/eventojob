from datetime import datetime
from typing import Any, Dict
import uuid
from domain.entities import *

# Armazenamos UUIDs como strings e datetimes como BSON datetimes (timezone-aware)
# --- DB boundary helpers ---


def id_to_db(value: "Id | uuid.UUID | str") -> str:
    if isinstance(value, Id):
        return str(value.value)
    if isinstance(value, uuid.UUID):
        return str(value)
    return str(value)


def id_from_db(value: str) -> Id:
    return Id(uuid.UUID(value))


def user_to_doc(user: User) -> Dict[str, Any]:
    return {
        "_id": str(user.id.value),
        "email": user.email.value,
        "password_hash": user.password_hash.value,
        "name": user.name,
        "last_name": user.last_name,
        "phone": user.phone,
        "roles": user.roles,
        "skills": user.skills,
        "ratings": user.ratings,
        "status": user.status.value,
        "applications": [offer_id for offer_id in user.applications],
        "offer": [offer_id for offer_id in user.offer],
        "created_at": user.created_at,  # PyMongo salva datetime com timezone
    }


def user_from_doc(doc: Dict[str, Any]) -> User:
    return User(
        id=Id(doc["_id"]),
        email=Email(doc["email"]),
        password_hash=PasswordHash(doc["password_hash"]),
        name=doc["name"],
        last_name=doc["last_name"],
        phone=doc["phone"],
        roles=doc["roles"],
        skills=doc["skills"],
        ratings=doc["ratings"],
        status=UserStatus(doc.get("status", "active")),
        applications=doc.get("applications", []),
        offer=doc.get("offer", []),
        created_at=doc["created_at"] if isinstance(doc["created_at"], datetime)
        else datetime.fromisoformat(doc["created_at"]),
    )


def refresh_to_doc(rt: RefreshToken) -> Dict[str, Any]:
    return {
        "_id": id_to_db(rt.id),
        "user_id": id_to_db(rt.user_id),
        "issued_at": rt.issued_at,
        "expires_at": rt.expires_at,
        "revoked_at": rt.revoked_at,
    }


def refresh_from_doc(doc: Dict[str, Any]) -> RefreshToken:
    return RefreshToken(
        id=id_from_db(doc["_id"]),
        user_id=id_from_db(doc["user_id"]),
        issued_at=doc["issued_at"],
        expires_at=doc["expires_at"],
        revoked_at=doc.get("revoked_at"),
    )


def offer_to_doc(offer: Offer) -> Dict[str, Any]:
    return {
        "_id": str(offer.id),
        "user_id": str(offer.user_id.value),
        "description": {
            "title": offer.description.title,
            "location": offer.description.location,
            "salary": offer.description.salary,
            "requirements": offer.description.requirements,
            "description": offer.description.description,
            "start_date": offer.description.start_date,
            "end_date": offer.description.end_date,
        },
        "created_at": offer.created_at,
        "updated_at": offer.updated_at,
        "status": offer.status.value,
        "applications": [user_id for user_id in offer.applications],
    }


def offer_to_doc_update(offer: Offer) -> Dict[str, Any]:
    return {
        "user_id": str(offer.user_id.value),
        "description": {
            "title": offer.description.title,
            "location": offer.description.location,
            "salary": offer.description.salary,
            "requirements": offer.description.requirements,
            "description": offer.description.description,
            "start_date": offer.description.start_date,
            "end_date": offer.description.end_date,
        },
        "updated_at": offer.updated_at,
        "status": offer.status.value,
        "applications": [user_id for user_id in offer.applications],
    }


def offer_from_doc(doc: Dict[str, Any]) -> Offer:
    return Offer(
        id=Id(doc["_id"]),
        user_id=Id(doc["user_id"]),
        description=OfferDescription(
            title=doc["description"]["title"],
            location=doc["description"]["location"],
            salary=doc["description"]["salary"],
            requirements=doc["description"]["requirements"],
            description=doc["description"]["description"],
            start_date=doc["description"]["start_date"],
            end_date=doc["description"]["end_date"],
        ),
        created_at=doc["created_at"] if isinstance(doc["created_at"], datetime)
        else datetime.fromisoformat(doc["created_at"]),
        updated_at=doc.get("updated_at"),
        status=OfferStatus(doc.get("status", "active")),
        applications=doc.get("applications", []),
    )
