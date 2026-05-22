import sqlite3
from datetime import date
from pathlib import Path
from typing import List

from src.model.patient import PatientRecord

_DATE_FMT = "%Y-%m-%d"


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _format_date(value: date) -> str:
    return value.isoformat()


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._create_schema()

    def _create_schema(self) -> None:
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_fio TEXT NOT NULL,
                address TEXT NOT NULL,
                birth_date TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                doctor_fio TEXT NOT NULL,
                conclusion TEXT NOT NULL
            )
            """)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def _row_to_record(self, row: tuple) -> PatientRecord:
        return PatientRecord(
            id=row[0],
            patient_fio=row[1],
            address=row[2],
            birth_date=_parse_date(row[3]),
            appointment_date=_parse_date(row[4]),
            doctor_fio=row[5],
            conclusion=row[6],
        )

    def fetch_all(self) -> List[PatientRecord]:
        cursor = self._conn.execute("""
            SELECT id, patient_fio, address, birth_date, appointment_date,
                   doctor_fio, conclusion
            FROM patients
            ORDER BY id
            """)
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def insert(self, record: PatientRecord) -> PatientRecord:
        cursor = self._conn.execute(
            """
            INSERT INTO patients
                (patient_fio, address, birth_date, appointment_date, doctor_fio, conclusion)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                record.patient_fio,
                record.address,
                _format_date(record.birth_date),
                _format_date(record.appointment_date),
                record.doctor_fio,
                record.conclusion,
            ),
        )
        self._conn.commit()
        record.id = cursor.lastrowid
        return record

    def delete_by_ids(self, ids: List[int]) -> int:
        if not ids:
            return 0
        placeholders = ",".join("?" * len(ids))
        cursor = self._conn.execute(
            f"DELETE FROM patients WHERE id IN ({placeholders})",
            ids,
        )
        self._conn.commit()
        return cursor.rowcount

    def replace_all(self, records: List[PatientRecord]) -> None:
        self._conn.execute("DELETE FROM patients")
        for record in records:
            self.insert(record)

    @classmethod
    def load_from_file(cls, db_path: Path) -> List[PatientRecord]:
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.execute("""
                SELECT id, patient_fio, address, birth_date, appointment_date,
                       doctor_fio, conclusion
                FROM patients
                ORDER BY id
                """)
            rows = cursor.fetchall()
        finally:
            conn.close()
        return [
            PatientRecord(
                id=row[0],
                patient_fio=row[1],
                address=row[2],
                birth_date=_parse_date(row[3]),
                appointment_date=_parse_date(row[4]),
                doctor_fio=row[5],
                conclusion=row[6],
            )
            for row in rows
        ]

    def save_to_file(self, db_path: Path) -> None:
        records = self.fetch_all()
        target = Database(db_path)
        try:
            target.replace_all(records)
        finally:
            target.close()
