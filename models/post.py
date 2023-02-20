import traceback

from datetime import datetime
from typing import List

from flask import url_for, request
from requests import Response

from db import db
from models.user import UserModel


class PostModel(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    owner = db.relationship("UserModel")

    @classmethod
    def find_by_id(cls, _id: int) -> "PostModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all(cls) -> List["PostModel"]:
        return cls.query.order_by(db.desc(cls.created_at)).all()

    @classmethod
    def find_all_by_owner_id(cls, owner_id: int) -> List["PostModel"]:
        return cls.query.filter_by(owner_id=owner_id).order_by(db.desc(cls.created_at)).all()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
