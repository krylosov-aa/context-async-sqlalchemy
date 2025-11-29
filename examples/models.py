import uuid
from typing import Any
from pydantic import GetCoreSchemaHandler
from pydantic_core.core_schema import IsInstanceSchema, is_instance_schema
from sqlalchemy import text, UUID, Text
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    MappedColumn,
)


class BaseTable(DeclarativeBase):
    """Base table for all tables"""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> IsInstanceSchema:
        return is_instance_schema(cls)


def uuid_pk_column() -> MappedColumn[uuid.UUID]:
    """Allows you to reuse a column definition without inheritance"""
    return mapped_column(
        UUID, primary_key=True, server_default=text("gen_random_uuid()")
    )


class ExampleTable(BaseTable):
    """just a table for example"""

    id: Mapped[uuid.UUID] = uuid_pk_column()
    text: Mapped[str] = mapped_column(Text, nullable=True)

    __tablename__ = "example"
