from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class PatientRecord:
    patient_fio: str
    address: str
    birth_date: date
    appointment_date: date
    doctor_fio: str
    conclusion: str
    id: Optional[int] = None

    def patient_surname(self) -> str:
        parts = self.patient_fio.strip().split()
        return parts[0] if parts else ""
