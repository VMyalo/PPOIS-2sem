from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional

from src.model.patient import PatientRecord


class SearchMode(Enum):
    SURNAME_OR_ADDRESS = "surname_or_address"
    BIRTH_DATE = "birth_date"
    DOCTOR_OR_APPOINTMENT = "doctor_or_appointment"


@dataclass
class SearchCriteria:
    """Критерии поиска/удаления."""

    mode: SearchMode
    surname: str = ""
    address: str = ""
    birth_date: Optional[date] = None
    doctor_surname: str = ""
    doctor_name: str = ""
    doctor_patronymic: str = ""
    appointment_date: Optional[date] = None


def _contains(part: str, text: str) -> bool:
    return part.strip().lower() in text.lower()


def _doctor_matches(record: PatientRecord, criteria: SearchCriteria) -> bool:
    parts = [criteria.doctor_surname, criteria.doctor_name, criteria.doctor_patronymic]
    filled = [p.strip() for p in parts if p.strip()]
    if not filled:
        return False
    fio = record.doctor_fio.lower()
    return all(p.lower() in fio for p in filled)


def matches(record: PatientRecord, criteria: SearchCriteria) -> bool:
    if criteria.mode == SearchMode.SURNAME_OR_ADDRESS:
        surname_ok = False
        address_ok = False
        if criteria.surname.strip():
            surname_ok = _contains(criteria.surname, record.patient_surname())
        if criteria.address.strip():
            address_ok = _contains(criteria.address, record.address)
        if criteria.surname.strip() and criteria.address.strip():
            return surname_ok or address_ok
        if criteria.surname.strip():
            return surname_ok
        if criteria.address.strip():
            return address_ok
        return False

    if criteria.mode == SearchMode.BIRTH_DATE:
        return (
            criteria.birth_date is not None and record.birth_date == criteria.birth_date
        )

    if criteria.mode == SearchMode.DOCTOR_OR_APPOINTMENT:
        doctor_ok = _doctor_matches(record, criteria)
        date_ok = (
            criteria.appointment_date is not None
            and record.appointment_date == criteria.appointment_date
        )
        has_doctor = any(
            p.strip()
            for p in (
                criteria.doctor_surname,
                criteria.doctor_name,
                criteria.doctor_patronymic,
            )
        )
        has_date = criteria.appointment_date is not None
        if has_doctor and has_date:
            return doctor_ok or date_ok
        if has_doctor:
            return doctor_ok
        if has_date:
            return date_ok
        return False

    return False
