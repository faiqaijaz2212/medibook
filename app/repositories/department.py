from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.department import Department


class DepartmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[Department]:
        return self.db.query(Department).filter(Department.id == id).first()

    def get_by_name(self, name: str) -> Optional[Department]:
        return self.db.query(Department).filter(Department.name == name).first()

    def get_all(self) -> List[Department]:
        return self.db.query(Department).all()

    def create(self, name: str, description: Optional[str] = None) -> Department:
        db_dept = Department(name=name, description=description)
        self.db.add(db_dept)
        self.db.commit()
        self.db.refresh(db_dept)
        return db_dept

    def update(
        self,
        db_dept: Department,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Department:
        if name is not None:
            db_dept.name = name
        if description is not None:
            db_dept.description = description
        self.db.commit()
        self.db.refresh(db_dept)
        return db_dept

    def delete(self, db_dept: Department) -> None:
        self.db.delete(db_dept)
        self.db.commit()
