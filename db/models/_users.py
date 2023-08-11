from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column, String, Boolean, case

from db.base import BaseModel, validate_column


class UserModel(BaseModel):
    __tablename__ = "user"

    # PERSONAL INFO
    email: str = Column(String(length=320), unique=True, index=True,
                        nullable=False)
    first_name: str = Column(String(100), nullable=True)
    last_name: str = Column(String(100), nullable=True)

    # STATUSES
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    staff_status: bool = Column(Boolean, default=False, nullable=False)

    # SECURITY
    hashed_password: str = Column(String(length=1024), nullable=True)
    verification_token: str = Column(String(500), nullable=True)

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @full_name.expression
    def full_name(cls):
        return case(
            [
                (cls.first_name + " " + cls.last_name),
            ],
            else_=cls.first_name + " " + cls.last_name,
        )

    def __str__(self) -> str:
        return self.email

    @validates('email', 'hashed_password', 'first_name', 'last_name', 'verification_token')
    def validate_column_content(self, key, value):
        return validate_column(self, key, value)
