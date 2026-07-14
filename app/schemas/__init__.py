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
]
