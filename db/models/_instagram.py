from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, String, Integer, ForeignKey, JSON

from db.base import BaseModel
from db.models import UserModel


class InstagramModel(BaseModel):
    __tablename__ = "instagram"

    user_id: int = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user: UserModel = relationship('UserModel', uselist=True, backref=backref(
        'instagram_entries', cascade="all, delete-orphan", lazy='selectin'))
    account_username: str = Column(String(100), nullable=True)
    photo_urls = Column(JSON)
