from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.doctor import Doctor


class DoctorRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[Doctor]:
        return self.db.query(Doctor).filter(Doctor.id == id).first()

    def get_by_email(self, email: str) -> Optional[Doctor]:
        return self.db.query(Doctor).filter(Doctor.email == email).first()

    def get_by_phone(self, phone: str) -> Optional[Doctor]:
        return self.db.query(Doctor).filter(Doctor.phone == phone).first()

    def get_all(self) -> List[Doctor]:
        return self.db.query(Doctor).all()

    def create(
        self,
        name: str,
        qualification: str,
        experience: int,
        department_id: int,
        phone: str,
        email: str,
        user_id: Optional[int] = None,
    ) -> Doctor:
        db_doc = Doctor(
            name=name,
            qualification=qualification,
            experience=experience,
            department_id=department_id,
            phone=phone,
            email=email,
            user_id=user_id,
        )
        self.db.add(db_doc)
        self.db.commit()
        self.db.refresh(db_doc)
        return db_doc

    def update(self, db_doc: Doctor, **kwargs) -> Doctor:
        for key, value in kwargs.items():
            if value is not None:
                setattr(db_doc, key, value)
        self.db.commit()
        self.db.refresh(db_doc)
        return db_doc

    def delete(self, db_doc: Doctor) -> None:
        self.db.delete(db_doc)
        self.db.commit()
