from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from app.schemas.doctor import DoctorResponse
from app.schemas.patient import PatientResponse


class AppointmentStatus(str, Enum):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    RESCHEDULED = "Rescheduled"


class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: datetime
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentReschedule(BaseModel):
    appointment_date: datetime


class AppointmentUpdateStatus(BaseModel):
    status: AppointmentStatus


class AppointmentResponse(AppointmentBase):
    id: int
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AppointmentDetailResponse(AppointmentResponse):
    doctor: DoctorResponse
    patient: PatientResponse
