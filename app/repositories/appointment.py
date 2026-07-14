from datetime import datetime, timedelta, date, timezone
from typing import Optional, List
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.models.appointment import Appointment


class AppointmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[Appointment]:
        return self.db.query(Appointment).filter(Appointment.id == id).first()

    def get_overlapping_doctor_appointments(
        self, doctor_id: int, time_val: datetime, exclude_id: Optional[int] = None
    ) -> List[Appointment]:
        # Ensure time_val is naive UTC
        if time_val.tzinfo is not None:
            time_val = time_val.astimezone(timezone.utc).replace(tzinfo=None)
        
        # Overlap check: +/- 30 minutes from proposed time_val
        start_time = time_val - timedelta(minutes=29)
        end_time = time_val + timedelta(minutes=29)

        query = self.db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.status.in_(["Scheduled", "Rescheduled"]),
                Appointment.appointment_date.between(start_time, end_time),
            )
        )
        if exclude_id is not None:
            query = query.filter(Appointment.id != exclude_id)
        return query.all()

    def get_overlapping_patient_appointments(
        self, patient_id: int, time_val: datetime, exclude_id: Optional[int] = None
    ) -> List[Appointment]:
        # Ensure time_val is naive UTC
        if time_val.tzinfo is not None:
            time_val = time_val.astimezone(timezone.utc).replace(tzinfo=None)

        start_time = time_val - timedelta(minutes=29)
        end_time = time_val + timedelta(minutes=29)

        query = self.db.query(Appointment).filter(
            and_(
                Appointment.patient_id == patient_id,
                Appointment.status.in_(["Scheduled", "Rescheduled"]),
                Appointment.appointment_date.between(start_time, end_time),
            )
        )
        if exclude_id is not None:
            query = query.filter(Appointment.id != exclude_id)
        return query.all()

    def get_all(
        self,
        doctor_id: Optional[int] = None,
        patient_id: Optional[int] = None,
        status_val: Optional[str] = None,
        date_val: Optional[date] = None,
        upcoming: bool = False,
        today: bool = False,
    ) -> List[Appointment]:
        query = self.db.query(Appointment)

        if doctor_id is not None:
            query = query.filter(Appointment.doctor_id == doctor_id)
        if patient_id is not None:
            query = query.filter(Appointment.patient_id == patient_id)
        if status_val is not None:
            query = query.filter(Appointment.status == status_val)

        if today:
            now_dt = datetime.utcnow()
            start_of_day = datetime.combine(now_dt.date(), datetime.min.time())
            end_of_day = datetime.combine(now_dt.date(), datetime.max.time())
            query = query.filter(
                Appointment.appointment_date.between(start_of_day, end_of_day)
            )
        elif date_val is not None:
            start_of_day = datetime.combine(date_val, datetime.min.time())
            end_of_day = datetime.combine(date_val, datetime.max.time())
            query = query.filter(
                Appointment.appointment_date.between(start_of_day, end_of_day)
            )

        if upcoming:
            query = query.filter(
                and_(
                    Appointment.status.in_(["Scheduled", "Rescheduled"]),
                    Appointment.appointment_date >= datetime.utcnow(),
                )
            )

        return query.order_by(Appointment.appointment_date.asc()).all()

    def create(self, **kwargs) -> Appointment:
        # Convert appointment_date to naive UTC if it is aware
        if "appointment_date" in kwargs and kwargs["appointment_date"].tzinfo is not None:
            kwargs["appointment_date"] = kwargs["appointment_date"].astimezone(timezone.utc).replace(tzinfo=None)
            
        db_app = Appointment(**kwargs)
        self.db.add(db_app)
        self.db.commit()
        self.db.refresh(db_app)
        return db_app

    def update(self, db_app: Appointment, **kwargs) -> Appointment:
        if "appointment_date" in kwargs and kwargs["appointment_date"].tzinfo is not None:
            kwargs["appointment_date"] = kwargs["appointment_date"].astimezone(timezone.utc).replace(tzinfo=None)
            
        for key, value in kwargs.items():
            if value is not None:
                setattr(db_app, key, value)
        self.db.commit()
        self.db.refresh(db_app)
        return db_app
