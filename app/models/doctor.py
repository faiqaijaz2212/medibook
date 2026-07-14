from typing import Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Doctor(Base, TimestampMixin):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    qualification: Mapped[str] = mapped_column(String(100), nullable=False)
    experience: Mapped[int] = mapped_column(Integer, nullable=False)  # In years
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=False
    )
    department: Mapped["Department"] = relationship(
        "Department", back_populates="doctors"
    )

    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
    )
