from pathlib import Path
from typing import List, Optional

from src.model import xml_io
from src.model.criteria import SearchCriteria, matches
from src.model.database import Database
from src.model.patient import PatientRecord


class PatientRepository:
    """Модель: хранение и операции над записями пациентов."""

    def __init__(self, db_path: Path) -> None:
        self._db = Database(db_path)

    def close(self) -> None:
        self._db.close()

    def get_all(self) -> List[PatientRecord]:
        return self._db.fetch_all()

    def add(self, record: PatientRecord) -> PatientRecord:
        return self._db.insert(record)

    def search(self, criteria: SearchCriteria) -> List[PatientRecord]:
        return [r for r in self.get_all() if matches(r, criteria)]

    def delete_matching(self, criteria: SearchCriteria) -> int:
        to_delete = self.search(criteria)
        ids = [r.id for r in to_delete if r.id is not None]
        return self._db.delete_by_ids(ids)

    def load_xml(self, path: Path, append: bool = False) -> int:
        records = xml_io.read_xml(path)
        if append:
            for record in records:
                self.add(record)
        else:
            self._db.replace_all(records)
        return len(records)

    def save_xml(self, path: Path) -> None:
        xml_io.write_xml(path, self.get_all())

    def load_database(self, path: Path, append: bool = False) -> int:
        records = Database.load_from_file(path)
        if append:
            for record in records:
                record.id = None
                self.add(record)
        else:
            self._db.replace_all(records)
        return len(records)

    def save_database(self, path: Path) -> None:
        self._db.save_to_file(path)

    def replace_all(self, records: List[PatientRecord]) -> None:
        self._db.replace_all(records)
