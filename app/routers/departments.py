from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
)
from app.repositories.department import DepartmentRepository
from app.services.auth import RoleChecker

router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)

admin_required = RoleChecker(["admin"])
any_role = RoleChecker(["admin", "doctor", "receptionist"])


@router.post(
    "", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED
)
def create_department(
    dept_in: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):
    repo = DepartmentRepository(db)
    existing = repo.get_by_name(dept_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department with this name already exists",
        )
    return repo.create(name=dept_in.name, description=dept_in.description)


@router.get("", response_model=List[DepartmentResponse])
def get_departments(
    db: Session = Depends(get_db), current_user=Depends(any_role)
):
    repo = DepartmentRepository(db)
    return repo.get_all()


@router.get("/{id}", response_model=DepartmentResponse)
def get_department(
    id: int, db: Session = Depends(get_db), current_user=Depends(any_role)
):
    repo = DepartmentRepository(db)
    dept = repo.get_by_id(id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
        )
    return dept


@router.put("/{id}", response_model=DepartmentResponse)
def update_department(
    id: int,
    dept_in: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):
    repo = DepartmentRepository(db)
    dept = repo.get_by_id(id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
        )
    if dept_in.name:
        existing = repo.get_by_name(dept_in.name)
        if existing and existing.id != id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department name already taken",
            )
    return repo.update(dept, name=dept_in.name, description=dept_in.description)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    id: int, db: Session = Depends(get_db), current_user=Depends(admin_required)
):
    repo = DepartmentRepository(db)
    dept = repo.get_by_id(id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
        )
    repo.delete(dept)
