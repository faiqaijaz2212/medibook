from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.patient_document import PatientDocument


class PatientDocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[PatientDocument]:
        return (
            self.db.query(PatientDocument).filter(PatientDocument.id == id).first()
        )

    def get_by_patient_id(self, patient_id: int) -> List[PatientDocument]:
        return (
            self.db.query(PatientDocument)
            .filter(PatientDocument.patient_id == patient_id)
            .all()
        )

    def create(self, **kwargs) -> PatientDocument:
        db_doc = PatientDocument(**kwargs)
        self.db.add(db_doc)
        self.db.commit()
        self.db.refresh(db_doc)
        return db_doc

    def delete(self, db_doc: PatientDocument) -> None:
        self.db.delete(db_doc)
        self.db.commit()
