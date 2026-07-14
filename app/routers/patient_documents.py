import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.patient_document import PatientDocumentResponse
from app.repositories.patient import PatientRepository
from app.repositories.patient_document import PatientDocumentRepository
from app.services.auth import RoleChecker

router = APIRouter(
    prefix="/patients",
    tags=["Patient Documents"],
)

any_role = RoleChecker(["admin", "doctor", "receptionist"])
UPLOAD_DIR = "uploads"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post(
    "/{patient_id}/documents",
    response_model=PatientDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    patient_id: int,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(any_role),
):
    pat_repo = PatientRepository(db)
    if not pat_repo.get_by_id(patient_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )

    # Generate unique secure filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{patient_id}_{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save file contents
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}",
        )

    doc_repo = PatientDocumentRepository(db)
    return doc_repo.create(
        patient_id=patient_id,
        filename=file.filename,
        file_path=file_path,
        document_type=document_type,
    )


@router.get(
    "/{patient_id}/documents", response_model=List[PatientDocumentResponse]
)
def list_documents(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(any_role),
):
    pat_repo = PatientRepository(db)
    if not pat_repo.get_by_id(patient_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )

    doc_repo = PatientDocumentRepository(db)
    return doc_repo.get_by_patient_id(patient_id)


@router.get("/{patient_id}/documents/{document_id}/download")
def download_document(
    patient_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(any_role),
):
    doc_repo = PatientDocumentRepository(db)
    doc = doc_repo.get_by_id(document_id)
    if not doc or doc.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    if not os.path.exists(doc.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on storage server",
        )

    return FileResponse(
        path=doc.file_path,
        filename=doc.filename,
        media_type="application/octet-stream",
    )


@router.delete(
    "/{patient_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    patient_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(any_role),
):
    doc_repo = PatientDocumentRepository(db)
    doc = doc_repo.get_by_id(document_id)
    if not doc or doc.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    # Delete from disk
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception as e:
            # Log but continue to delete DB record
            print(f"Error removing file from disk: {e}")

    doc_repo.delete(doc)
