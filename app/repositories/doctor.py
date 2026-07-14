from datetime import datetime, timedelta, timezone
from typing import Optional, List
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.models.doctor import Doctor
from app.models.appointment import Appointment  # Import Appointment model for subquery check


class DoctorRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[Doctor]:
        return self.db.query(Doctor).filter(Doctor.id == id).first()

    def get_by_email(self, email: str) -> Optional[Doctor]:
        return self.db.query(Doctor).filter(Doctor.email == email).first()

    def get_by_phone(self, phone: str) -> Optional[Doctor]:
        return self.db.query(Doctor).filter(Doctor.phone == phone).first()

    def get_all(
        self,
        department_id: Optional[int] = None,
        experience_min: Optional[int] = None,
        available_at: Optional[datetime] = None,
    ) -> List[Doctor]:
        query = self.db.query(Doctor)

        if department_id is not None:
            query = query.filter(Doctor.department_id == department_id)

        if experience_min is not None:
            query = query.filter(Doctor.experience >= experience_min)

        if available_at is not None:
            # Ensure available_at is naive UTC
            if available_at.tzinfo is not None:
                available_at = available_at.astimezone(timezone.utc).replace(
                    tzinfo=None
                )
            start_time = available_at - timedelta(minutes=29)
            end_time = available_at + timedelta(minutes=29)

            # Subquery finding doctor_ids having booked scheduled/rescheduled appointments
            booked_doctors = (
                self.db.query(Appointment.doctor_id)
                .filter(
                    and_(
                        Appointment.status.in_(["Scheduled", "Rescheduled"]),
                        Appointment.appointment_date.between(
                            start_time, end_time
                        ),
                    )
                )
                .scalar_subquery()
            )

            query = query.filter(Doctor.id.not_in(booked_doctors))

        return query.all()

    def create(
        self,
        name: str,
        qualification: str,
        experience: int,
        department_id: int,
        phone: str,
        email: str,
        user_id: Optional[int] = None,
    ) -> Doctor:
        db_doc = Doctor(
            name=name,
            qualification=qualification,
            experience=experience,
            department_id=department_id,
            phone=phone,
            email=email,
            user_id=user_id,
        )
        self.db.add(db_doc)
        self.db.commit()
        self.db.refresh(db_doc)
        return db_doc

    def update(self, db_doc: Doctor, **kwargs) -> Doctor:
        for key, value in kwargs.items():
            if value is not None:
                setattr(db_doc, key, value)
        self.db.commit()
        self.db.refresh(db_doc)
        return db_doc

    def delete(self, db_doc: Doctor) -> None:
        self.db.delete(db_doc)
        self.db.commit()
