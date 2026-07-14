from app.repositories.department import DepartmentRepository
from app.repositories.doctor import DoctorRepository
from app.repositories.patient import PatientRepository
from app.repositories.appointment import AppointmentRepository
from app.repositories.medical_record import MedicalRecordRepository
from app.repositories.patient_document import PatientDocumentRepository

__all__ = [
    "DepartmentRepository",
    "DoctorRepository",
    "PatientRepository",
    "AppointmentRepository",
    "MedicalRecordRepository",
    "PatientDocumentRepository",
]
