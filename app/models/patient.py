from typing import List, Optional
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Patient(Base, TimestampMixin):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    blood_group: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    phone: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, nullable=False
    )
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    emergency_contact: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    allergies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment",
        back_populates="patient",
        cascade="all, delete-orphan",
    )

    documents: Mapped[List["PatientDocument"]] = relationship(
        "PatientDocument",
        back_populates="patient",
        cascade="all, delete-orphan",
    )
