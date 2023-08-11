from typing import Any

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, Integer, MetaData, func, inspect

from gql.exceptions import ValidationError

meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)
Base: Any = declarative_base(metadata=meta)


class BaseModel(Base):
    __abstract__ = True

    id: int = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self) -> str:
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)

    def __str__(self) -> str:
        return self.name if hasattr(self, "name") else super().__str__()


def validate_column(self, key, value: str):
    if hasattr(inspect(self).mapper.columns, key):
        column = getattr(inspect(self).mapper.columns, key)
        if not value and not column.nullable:
            raise ValidationError({key: f'The {key} is required'})
        if value:
            if value.isspace():
                raise ValidationError({key: f'The {key} only contains spaces'})
            elif len(value) > column.type.length:
                raise ValidationError({key: f"{key} cannot be longer than {column.type.length} characters"})
    return value
