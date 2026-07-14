from app.schemas.user import UserRole, UserCreate, UserResponse, Token, TokenData
from app.schemas.department import (
    DepartmentBase,
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
)
from app.schemas.doctor import (
    DoctorBase,
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
    DoctorDetailResponse,
)
from app.schemas.patient import (
    PatientBase,
    PatientCreate,
    PatientUpdate,
    PatientResponse,
)

__all__ = [
    "UserRole",
    "UserCreate",
    "UserResponse",
    "Token",
    "TokenData",
    "DepartmentBase",
    "DepartmentCreate",
    "DepartmentUpdate",
    "DepartmentResponse",
    "DoctorBase",
    "DoctorCreate",
    "DoctorUpdate",
    "DoctorResponse",
    "DoctorDetailResponse",
    "PatientBase",
    "PatientCreate",
    "PatientUpdate",
    "PatientResponse",
]
