from datetime import date
from pathlib import Path
from typing import List
from xml.dom.minidom import Document
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

from src.model.patient import PatientRecord

_ROOT_TAG = "patients"
_RECORD_TAG = "patient"


class _PatientSaxHandler(ContentHandler):
    def __init__(self) -> None:
        self.records: List[PatientRecord] = []
        self._current_tag: str | None = None
        self._buffer: List[str] = []
        self._fields: dict[str, str] = {}

    def startElement(self, name: str, attrs) -> None:
        if name == _RECORD_TAG:
            self._fields = {}
        self._current_tag = name
        self._buffer = []

    def characters(self, content: str) -> None:
        if content.strip():
            self._buffer.append(content)

    def endElement(self, name: str) -> None:
        if name == _RECORD_TAG:
            self.records.append(_record_from_fields(self._fields))
            self._fields = {}
        elif name not in (_ROOT_TAG, _RECORD_TAG):
            self._fields[name] = "".join(self._buffer).strip()
        self._current_tag = None
        self._buffer = []


def _record_from_fields(fields: dict[str, str]) -> PatientRecord:
    return PatientRecord(
        patient_fio=fields["patient_fio"],
        address=fields["address"],
        birth_date=date.fromisoformat(fields["birth_date"]),
        appointment_date=date.fromisoformat(fields["appointment_date"]),
        doctor_fio=fields["doctor_fio"],
        conclusion=fields["conclusion"],
    )


def read_xml(path: Path) -> List[PatientRecord]:
    text = path.read_text(encoding="utf-8")
    handler = _PatientSaxHandler()
    parser = make_parser()
    parser.setContentHandler(handler)
    parser.feed(text)
    parser.close()
    return handler.records


def write_xml(path: Path, records: List[PatientRecord]) -> None:
    doc = Document()
    root = doc.createElement(_ROOT_TAG)
    doc.appendChild(root)

    for record in records:
        node = doc.createElement(_RECORD_TAG)
        for tag, value in (
            ("patient_fio", record.patient_fio),
            ("address", record.address),
            ("birth_date", record.birth_date.isoformat()),
            ("appointment_date", record.appointment_date.isoformat()),
            ("doctor_fio", record.doctor_fio),
            ("conclusion", record.conclusion),
        ):
            child = doc.createElement(tag)
            child.appendChild(doc.createTextNode(value))
            node.appendChild(child)
        root.appendChild(node)

    xml_bytes = doc.toprettyxml(indent="  ", encoding="utf-8")
    path.write_bytes(xml_bytes)
