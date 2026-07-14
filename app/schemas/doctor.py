from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import datetime
from app.schemas.department import DepartmentResponse


class DoctorBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    qualification: str = Field(..., min_length=2, max_length=100)
    experience: int = Field(..., ge=0)
    department_id: int
    phone: str = Field(..., min_length=5, max_length=20)
    email: EmailStr
    user_id: Optional[int] = None


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    qualification: Optional[str] = Field(None, min_length=2, max_length=100)
    experience: Optional[int] = Field(None, ge=0)
    department_id: Optional[int] = None
    phone: Optional[str] = Field(None, min_length=5, max_length=20)
    email: Optional[EmailStr] = None
    user_id: Optional[int] = None


class DoctorResponse(DoctorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DoctorDetailResponse(DoctorResponse):
    department: DepartmentResponse
