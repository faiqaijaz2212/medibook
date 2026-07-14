from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.medical_record import MedicalRecord


class MedicalRecordRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[MedicalRecord]:
        return (
            self.db.query(MedicalRecord).filter(MedicalRecord.id == id).first()
        )

    def get_by_appointment_id(self, appointment_id: int) -> Optional[MedicalRecord]:
        return (
            self.db.query(MedicalRecord)
            .filter(MedicalRecord.appointment_id == appointment_id)
            .first()
        )

    def get_all(self) -> List[MedicalRecord]:
        return self.db.query(MedicalRecord).all()

    def create(self, **kwargs) -> MedicalRecord:
        db_record = MedicalRecord(**kwargs)
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def update(self, db_record: MedicalRecord, **kwargs) -> MedicalRecord:
        for key, value in kwargs.items():
            if value is not None:
                setattr(db_record, key, value)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def delete(self, db_record: MedicalRecord) -> None:
        self.db.delete(db_record)
        self.db.commit()
