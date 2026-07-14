from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class PatientBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=0, le=150)
    gender: str = Field(..., min_length=2, max_length=20)
    blood_group: Optional[str] = Field(None, min_length=1, max_length=10)
    phone: str = Field(..., min_length=5, max_length=20)
    address: Optional[str] = None
    emergency_contact: Optional[str] = Field(None, min_length=5, max_length=100)
    allergies: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[str] = Field(None, min_length=2, max_length=20)
    blood_group: Optional[str] = Field(None, min_length=1, max_length=10)
    phone: Optional[str] = Field(None, min_length=5, max_length=20)
    address: Optional[str] = None
    emergency_contact: Optional[str] = Field(None, min_length=5, max_length=100)
    allergies: Optional[str] = None


class PatientResponse(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
