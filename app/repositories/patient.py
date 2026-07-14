from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.patient import Patient


class PatientRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[Patient]:
        return self.db.query(Patient).filter(Patient.id == id).first()

    def get_by_phone(self, phone: str) -> Optional[Patient]:
        return self.db.query(Patient).filter(Patient.phone == phone).first()

    def get_all(
        self,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        blood_group: Optional[str] = None,
        gender: Optional[str] = None,
    ) -> List[Patient]:
        query = self.db.query(Patient)
        if name:
            query = query.filter(Patient.name.ilike(f"%{name}%"))
        if phone:
            query = query.filter(Patient.phone.like(f"%{phone}%"))
        if blood_group:
            query = query.filter(Patient.blood_group == blood_group)
        if gender:
            query = query.filter(Patient.gender == gender)
        return query.all()

    def create(self, **kwargs) -> Patient:
        db_patient = Patient(**kwargs)
        self.db.add(db_patient)
        self.db.commit()
        self.db.refresh(db_patient)
        return db_patient

    def update(self, db_patient: Patient, **kwargs) -> Patient:
        for key, value in kwargs.items():
            if value is not None:
                setattr(db_patient, key, value)
        self.db.commit()
        self.db.refresh(db_patient)
        return db_patient

    def delete(self, db_patient: Patient) -> None:
        self.db.delete(db_patient)
        self.db.commit()
