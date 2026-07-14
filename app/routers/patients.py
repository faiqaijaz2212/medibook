from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from app.repositories.patient import PatientRepository
from app.services.auth import RoleChecker

router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)

write_required = RoleChecker(["admin", "receptionist"])
read_required = RoleChecker(["admin", "receptionist", "doctor"])


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(
    patient_in: PatientCreate,
    db: Session = Depends(get_db),
    current_user=Depends(write_required),
):
    repo = PatientRepository(db)
    existing = repo.get_by_phone(patient_in.phone)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient with this phone number already registered",
        )
    return repo.create(**patient_in.model_dump())


@router.get("", response_model=List[PatientResponse])
def get_patients(
    name: Optional[str] = None,
    phone: Optional[str] = None,
    blood_group: Optional[str] = None,
    gender: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(read_required),
):
    repo = PatientRepository(db)
    return repo.get_all(
        name=name, phone=phone, blood_group=blood_group, gender=gender
    )


@router.get("/{id}", response_model=PatientResponse)
def get_patient(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(read_required),
):
    repo = PatientRepository(db)
    patient = repo.get_by_id(id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    return patient


@router.put("/{id}", response_model=PatientResponse)
def update_patient(
    id: int,
    patient_in: PatientUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(write_required),
):
    repo = PatientRepository(db)
    patient = repo.get_by_id(id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )

    if patient_in.phone:
        existing = repo.get_by_phone(patient_in.phone)
        if existing and existing.id != id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already in use",
            )

    return repo.update(patient, **patient_in.model_dump(exclude_unset=True))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(write_required),
):
    repo = PatientRepository(db)
    patient = repo.get_by_id(id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    repo.delete(patient)
