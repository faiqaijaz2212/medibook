from typing import List, Optional
from datetime import datetime, date, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentReschedule,
    AppointmentUpdateStatus,
    AppointmentResponse,
    AppointmentDetailResponse,
    AppointmentStatus,
)
from app.repositories.appointment import AppointmentRepository
from app.repositories.doctor import DoctorRepository
from app.repositories.patient import PatientRepository
from app.services.auth import RoleChecker

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
)

write_required = RoleChecker(["admin", "receptionist"])
read_required = RoleChecker(["admin", "receptionist", "doctor"])


def validate_scheduling_rules(
    repo: AppointmentRepository,
    doctor_repo: DoctorRepository,
    patient_repo: PatientRepository,
    doctor_id: int,
    patient_id: int,
    appointment_date: datetime,
    exclude_id: Optional[int] = None,
):
    # 1. Date cannot be in the past
    naive_date = appointment_date
    if appointment_date.tzinfo is not None:
        naive_date = appointment_date.astimezone(timezone.utc).replace(
            tzinfo=None
        )

    if naive_date <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot book appointments in the past",
        )

    # 2. Validate Doctor exists
    if not doctor_repo.get_by_id(doctor_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found"
        )

    # 3. Validate Patient exists
    if not patient_repo.get_by_id(patient_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )

    # 4. Prevent overlapping doctor bookings (30-minute slots)
    overlapping_doc = repo.get_overlapping_doctor_appointments(
        doctor_id, appointment_date, exclude_id
    )
    if overlapping_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor has an overlapping appointment at this time",
        )

    # 5. Prevent overlapping patient bookings
    overlapping_pat = repo.get_overlapping_patient_appointments(
        patient_id, appointment_date, exclude_id
    )
    if overlapping_pat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient has an overlapping appointment at this time",
        )


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def book_appointment(
    app_in: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(write_required),
):
    repo = AppointmentRepository(db)
    doc_repo = DoctorRepository(db)
    pat_repo = PatientRepository(db)

    validate_scheduling_rules(
        repo,
        doc_repo,
        pat_repo,
        app_in.doctor_id,
        app_in.patient_id,
        app_in.appointment_date,
    )

    return repo.create(**app_in.model_dump())


@router.get("", response_model=List[AppointmentDetailResponse])
def get_appointments(
    doctor_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    status_val: Optional[AppointmentStatus] = None,
    date_val: Optional[date] = None,
    upcoming: bool = False,
    today: bool = False,
    db: Session = Depends(get_db),
    current_user=Depends(read_required),
):
    repo = AppointmentRepository(db)
    return repo.get_all(
        doctor_id=doctor_id,
        patient_id=patient_id,
        status_val=status_val.value if status_val else None,
        date_val=date_val,
        upcoming=upcoming,
        today=today,
    )


@router.get("/{id}", response_model=AppointmentDetailResponse)
def get_appointment(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(read_required),
):
    repo = AppointmentRepository(db)
    appointment = repo.get_by_id(id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    return appointment


@router.put("/{id}/reschedule", response_model=AppointmentResponse)
def reschedule_appointment(
    id: int,
    resched_in: AppointmentReschedule,
    db: Session = Depends(get_db),
    current_user=Depends(write_required),
):
    repo = AppointmentRepository(db)
    doc_repo = DoctorRepository(db)
    pat_repo = PatientRepository(db)

    appointment = repo.get_by_id(id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    validate_scheduling_rules(
        repo,
        doc_repo,
        pat_repo,
        appointment.doctor_id,
        appointment.patient_id,
        resched_in.appointment_date,
        exclude_id=id,
    )

    return repo.update(
        appointment,
        appointment_date=resched_in.appointment_date,
        status="Rescheduled",
    )


@router.put("/{id}/status", response_model=AppointmentResponse)
def update_appointment_status(
    id: int,
    status_in: AppointmentUpdateStatus,
    db: Session = Depends(get_db),
    current_user=Depends(write_required),
):
    repo = AppointmentRepository(db)
    appointment = repo.get_by_id(id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    return repo.update(appointment, status=status_in.status.value)
