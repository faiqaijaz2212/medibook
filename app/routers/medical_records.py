from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.medical_record import (
    MedicalRecordCreate,
    MedicalRecordUpdate,
    MedicalRecordResponse,
    MedicalRecordDetailResponse,
)
from app.models.user import User
from app.models.doctor import Doctor
from app.repositories.medical_record import MedicalRecordRepository
from app.repositories.appointment import AppointmentRepository
from app.repositories.doctor import DoctorRepository
from app.services.auth import RoleChecker, get_current_user

router = APIRouter(
    prefix="/medical-records",
    tags=["Medical Records"],
)

write_required = RoleChecker(["admin", "doctor"])
read_required = RoleChecker(["admin", "doctor", "receptionist"])


def verify_doctor_assignment(db: Session, current_user: User, doctor_id: int):
    if current_user.role == "admin":
        return
    # Find doctor profile associated with current_user
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor or doctor.id != doctor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to manage medical records for this appointment",
        )


@router.post("", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)
def create_medical_record(
    record_in: MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_required),
):
    app_repo = AppointmentRepository(db)
    appointment = app_repo.get_by_id(record_in.appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    if appointment.status == "Cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create medical records for cancelled appointments",
        )

    # Verify the doctor writing the record is assigned to the appointment
    verify_doctor_assignment(db, current_user, appointment.doctor_id)

    record_repo = MedicalRecordRepository(db)
    existing = record_repo.get_by_appointment_id(record_in.appointment_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medical record already exists for this appointment",
        )

    record = record_repo.create(**record_in.model_dump())
    # Automatically complete the appointment
    app_repo.update(appointment, status="Completed")
    return record


@router.get("", response_model=List[MedicalRecordDetailResponse])
def get_medical_records(
    db: Session = Depends(get_db), current_user: User = Depends(read_required)
):
    repo = MedicalRecordRepository(db)
    return repo.get_all()


@router.get("/{id}", response_model=MedicalRecordDetailResponse)
def get_medical_record(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_required),
):
    repo = MedicalRecordRepository(db)
    record = repo.get_by_id(id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found",
        )
    return record


@router.get(
    "/appointment/{appointment_id}", response_model=MedicalRecordDetailResponse
)
def get_medical_record_by_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_required),
):
    repo = MedicalRecordRepository(db)
    record = repo.get_by_appointment_id(appointment_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found for this appointment",
        )
    return record


@router.put("/{id}", response_model=MedicalRecordResponse)
def update_medical_record(
    id: int,
    record_in: MedicalRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_required),
):
    record_repo = MedicalRecordRepository(db)
    record = record_repo.get_by_id(id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found",
        )

    app_repo = AppointmentRepository(db)
    appointment = app_repo.get_by_id(record.appointment_id)

    # Verify the doctor writing the record is assigned to the appointment
    verify_doctor_assignment(db, current_user, appointment.doctor_id)

    return record_repo.update(
        record, **record_in.model_dump(exclude_unset=True)
    )
