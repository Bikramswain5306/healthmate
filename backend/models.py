from pydantic import BaseModel
from datetime import datetime

class Appointment(BaseModel):
    id: int
    patient_name: str
    doctor_name: str
    date: str
    time: str
    status: str
    created_at: datetime
