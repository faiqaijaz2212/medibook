from datetime import datetime, timedelta, date, timezone
from typing import Optional, List
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.models.appointment import Appointment
from app.models.doctor import Doctor  # Import Doctor model to support JOIN query


class AppointmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[Appointment]:
        return self.db.query(Appointment).filter(Appointment.id == id).first()

    def get_overlapping_doctor_appointments(
        self, doctor_id: int, time_val: datetime, exclude_id: Optional[int] = None
    ) -> List[Appointment]:
        if time_val.tzinfo is not None:
            time_val = time_val.astimezone(timezone.utc).replace(tzinfo=None)

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
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        department_id: Optional[int] = None,
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

        if department_id is not None:
            # Perform JOIN on Doctor model to filter by department
            query = query.join(Doctor).filter(Doctor.department_id == department_id)

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
        elif start_date is not None and end_date is not None:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.filter(
                Appointment.appointment_date.between(start_datetime, end_datetime)
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
