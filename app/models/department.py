from typing import List, Optional
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Department(Base, TimestampMixin):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    doctors: Mapped[List["Doctor"]] = relationship(
        "Doctor",
        back_populates="department",
        cascade="all, delete-orphan",
    )
