from pydantic import BaseModel, ConfigDict
from datetime import datetime


class PatientDocumentResponse(BaseModel):
    id: int
    patient_id: int
    filename: str
    document_type: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
