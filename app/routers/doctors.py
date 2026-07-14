from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.doctor import (
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
    DoctorDetailResponse,
)
from app.repositories.doctor import DoctorRepository
from app.repositories.department import DepartmentRepository
from app.services.auth import RoleChecker

router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"],
)

admin_required = RoleChecker(["admin"])
any_role = RoleChecker(["admin", "doctor", "receptionist"])


@router.post("", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def create_doctor(
    doc_in: DoctorCreate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):
    # Validate department exists
    dept_repo = DepartmentRepository(db)
    dept = dept_repo.get_by_id(doc_in.department_id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
        )

    doc_repo = DoctorRepository(db)
    # Validate unique email
    if doc_repo.get_by_email(doc_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use"
        )
    # Validate unique phone
    if doc_repo.get_by_phone(doc_in.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already in use",
        )

    return doc_repo.create(
        name=doc_in.name,
        qualification=doc_in.qualification,
        experience=doc_in.experience,
        department_id=doc_in.department_id,
        phone=doc_in.phone,
        email=doc_in.email,
        user_id=doc_in.user_id,
    )


@router.get("", response_model=List[DoctorDetailResponse])
def get_doctors(
    department_id: Optional[int] = None,
    experience_min: Optional[int] = None,
    available_at: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user=Depends(any_role),
):
    doc_repo = DoctorRepository(db)
    return doc_repo.get_all(
        department_id=department_id,
        experience_min=experience_min,
        available_at=available_at,
    )


@router.get("/{id}", response_model=DoctorDetailResponse)
def get_doctor(
    id: int, db: Session = Depends(get_db), current_user=Depends(any_role)
):
    doc_repo = DoctorRepository(db)
    doc = doc_repo.get_by_id(id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found"
        )
    return doc


@router.put("/{id}", response_model=DoctorResponse)
def update_doctor(
    id: int,
    doc_in: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):
    doc_repo = DoctorRepository(db)
    doc = doc_repo.get_by_id(id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found"
        )

    if doc_in.department_id is not None:
        dept_repo = DepartmentRepository(db)
        if not dept_repo.get_by_id(doc_in.department_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found",
            )

    if doc_in.email is not None:
        existing = doc_repo.get_by_email(doc_in.email)
        if existing and existing.id != id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )

    if doc_in.phone is not None:
        existing = doc_repo.get_by_phone(doc_in.phone)
        if existing and existing.id != id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already in use",
            )

    return doc_repo.update(doc, **doc_in.model_dump(exclude_unset=True))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(
    id: int, db: Session = Depends(get_db), current_user=Depends(admin_required)
):
    doc_repo = DoctorRepository(db)
    doc = doc_repo.get_by_id(id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found"
        )
    doc_repo.delete(doc)
