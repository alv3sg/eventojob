from typing import Iterable
from pymongo.collection import Collection
from pymongo import ASCENDING, ReturnDocument

from application.ports import OfferRepository, NotFound
from domain.entities import Offer
from ._mappers import *


class MongoOfferRepository(OfferRepository):
    def __init__(self, col: Collection):
        self.col = col
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        self.col.create_index([("user_id", ASCENDING)])
        self.col.create_index([("created_at", ASCENDING)])

    def create(self, offer: Offer) -> None:
        try:
            self.col.insert_one(offer_to_doc(offer))
        except Exception as e:
            raise e

    def read(self, offer_id: Id) -> Offer:
        offer_id = id_to_db(offer_id)
        try:
            doc = self.col.find_one({"_id": offer_id})
            if not doc:
                raise NotFound("Offer não encontrado")
            return offer_from_doc(doc)
        except Exception as e:
            raise e

    def update(self, offer: Offer) -> None:
        try:
            self.col.update_one(
                {"_id": offer.id.value}, {"$set": offer_to_doc_update(offer)})
        except Exception as e:
            raise e

    def delete(self, offer_id: Id) -> None:
        offer_id = id_to_db(offer_id)
        try:
            self.col.delete_one({"_id": offer_id})
        except Exception as e:
            raise e

    def save(self, offer: Offer) -> None:
        doc = offer_to_doc(offer)
        res = self.col.find_one_and_replace(
            {"_id": offer.id.value}, doc, return_document=ReturnDocument.AFTER)
        if not res:
            raise NotFound("Offer não encontrado")

    def get_by_user_id(self, *, user_id: Id, limit: int = 50, offset: int = 0) -> Iterable[Offer]:
        user_id = id_to_db(user_id)
        cursor = self.col.find({"user_id": user_id})
        for doc in cursor:
            yield offer_from_doc(doc)

    def list(self, *, limit: int = 50, offset: int = 0) -> Iterable[Offer]:
        cursor = (self.col.find({})
                  .sort("created_at", ASCENDING)
                  .skip(offset)
                  .limit(limit))
        for doc in cursor:
            yield offer_from_doc(doc)
