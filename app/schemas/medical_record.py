from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date
from app.schemas.appointment import AppointmentResponse


class MedicalRecordBase(BaseModel):
    diagnosis: str = Field(..., min_length=2)
    prescription: str = Field(..., min_length=2)
    clinical_notes: Optional[str] = None
    follow_up_date: Optional[date] = None


class MedicalRecordCreate(MedicalRecordBase):
    appointment_id: int


class MedicalRecordUpdate(BaseModel):
    diagnosis: Optional[str] = Field(None, min_length=2)
    prescription: Optional[str] = Field(None, min_length=2)
    clinical_notes: Optional[str] = None
    follow_up_date: Optional[date] = None


class MedicalRecordResponse(MedicalRecordBase):
    id: int
    appointment_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MedicalRecordDetailResponse(MedicalRecordResponse):
    appointment: AppointmentResponse
