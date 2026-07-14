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
from app.schemas.appointment import (
    AppointmentStatus,
    AppointmentBase,
    AppointmentCreate,
    AppointmentReschedule,
    AppointmentUpdateStatus,
    AppointmentResponse,
    AppointmentDetailResponse,
)
from app.schemas.medical_record import (
    MedicalRecordBase,
    MedicalRecordCreate,
    MedicalRecordUpdate,
    MedicalRecordResponse,
    MedicalRecordDetailResponse,
)
from app.schemas.patient_document import PatientDocumentResponse

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
    "AppointmentStatus",
    "AppointmentBase",
    "AppointmentCreate",
    "AppointmentReschedule",
    "AppointmentUpdateStatus",
    "AppointmentResponse",
    "AppointmentDetailResponse",
    "MedicalRecordBase",
    "MedicalRecordCreate",
    "MedicalRecordUpdate",
    "MedicalRecordResponse",
    "MedicalRecordDetailResponse",
    "PatientDocumentResponse",
]
