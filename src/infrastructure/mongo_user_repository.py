from pymongo.collection import Collection
from pymongo import ASCENDING, ReturnDocument
from application.ports import *
from domain.entities import *
from ._mappers import *


class MongoUserRepository(UserRepository):
    def __init__(self, col: Collection):
        self.col = col
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        self.col.create_index([("email", ASCENDING)], unique=True)
        self.col.create_index([("created_at", ASCENDING)])

    def create(self, user: User) -> None:
        try:
            self.col.insert_one(user_to_doc(user))
        except Exception as e:
            msg = str(e).lower()
            if "duplicate key" in msg or "e11000" in msg:
                raise AlreadyExists("Email já registrado") from e
            raise

    def read(self, user_id: Id) -> User:
        doc = self.col.find_one({"_id": user_id.value})
        if not doc:
            raise NotFound("Usuário não encontrado")
        return user_from_doc(doc)

    def read_all(self, limit: int = 50, offset: int = 0) -> Iterable[User]:
        docs = self.col.find()
        return [user_from_doc(doc) for doc in docs]

    def update(self, user: User) -> None:
        doc = user_to_doc(user)
        res = self.col.find_one_and_replace(
            {"_id": user.id.value}, doc, return_document=ReturnDocument.AFTER)
        if not res:
            raise NotFound("Usuário não encontrado")

    def delete(self, user_id: Id) -> None:
        res = self.col.delete_one({"_id": user_id.value})
        if not res.deleted_count:
            raise NotFound("Usuário não encontrado")

    def save(self, user: User) -> None:
        self.update(user)

    def exists_by_email(self, email: Email) -> bool:
        email = email.value
        return self.col.count_documents({"email": email}, limit=1) > 0

    def get_auth_view_by_email(self, email: Email):
        email = email.value
        doc = self.col.find_one(
            {"email": email},
            {"_id": 1, "password_hash": 1, "status": 1}
        )
        if not doc:
            raise NotFound("User not found")
        # adapt to your stored formats
        return (
            Id(doc["_id"]),
            PasswordHash(doc["password_hash"]),
            doc["status"]
        )
