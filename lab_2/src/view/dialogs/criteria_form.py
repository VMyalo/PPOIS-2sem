from typing import Optional

from PyQt6.QtWidgets import (QCheckBox, QFormLayout, QGroupBox, QLineEdit,
                             QMessageBox, QRadioButton, QStackedWidget,
                             QVBoxLayout, QWidget)

from src.model.criteria import SearchCriteria, SearchMode
from src.view.widgets.date_picker import DatePicker


class CriteriaForm(QGroupBox):
    """Форма ввода условий поиска/удаления."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(title, parent)
        self._mode = SearchMode.SURNAME_OR_ADDRESS

        layout = QVBoxLayout(self)

        self._radio_surname = QRadioButton("По фамилии пациента или адресу")
        self._radio_birth = QRadioButton("По дате рождения")
        self._radio_doctor = QRadioButton("По ФИО врача или дате приёма")
        self._radio_surname.setChecked(True)

        for rb, mode in (
            (self._radio_surname, SearchMode.SURNAME_OR_ADDRESS),
            (self._radio_birth, SearchMode.BIRTH_DATE),
            (self._radio_doctor, SearchMode.DOCTOR_OR_APPOINTMENT),
        ):
            layout.addWidget(rb)
            rb.clicked.connect(lambda _checked=False, m=mode: self._on_mode_changed(m))

        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

        self._build_surname_page()
        self._build_birth_page()
        self._build_doctor_page()
        self._stack.setCurrentIndex(0)

    def _on_mode_changed(self, mode: SearchMode) -> None:
        self._mode = mode
        index = {
            SearchMode.SURNAME_OR_ADDRESS: 0,
            SearchMode.BIRTH_DATE: 1,
            SearchMode.DOCTOR_OR_APPOINTMENT: 2,
        }[mode]
        self._stack.setCurrentIndex(index)

    def _build_surname_page(self) -> None:
        page = QWidget()
        form = QFormLayout(page)
        self.surname_entry = QLineEdit()
        self.address_entry = QLineEdit()
        form.addRow("Фамилия пациента:", self.surname_entry)
        form.addRow("Адрес прописки:", self.address_entry)
        self._stack.addWidget(page)

    def _build_birth_page(self) -> None:
        page = QWidget()
        form = QFormLayout(page)
        self.birth_picker = DatePicker()
        form.addRow("Дата рождения:", self.birth_picker)
        self._stack.addWidget(page)

    def _build_doctor_page(self) -> None:
        page = QWidget()
        form = QFormLayout(page)
        self.doc_surname = QLineEdit()
        self.doc_name = QLineEdit()
        self.doc_patronymic = QLineEdit()
        self.use_appointment = QCheckBox("Использовать дату приёма")
        self.appointment_picker = DatePicker()
        form.addRow("Фамилия врача:", self.doc_surname)
        form.addRow("Имя врача:", self.doc_name)
        form.addRow("Отчество врача:", self.doc_patronymic)
        form.addRow(self.use_appointment)
        form.addRow("Дата приёма:", self.appointment_picker)
        self._stack.addWidget(page)

    def build_criteria(self) -> Optional[SearchCriteria]:
        mode = self._mode
        if mode == SearchMode.SURNAME_OR_ADDRESS:
            surname = self.surname_entry.text().strip()
            address = self.address_entry.text().strip()
            if not surname and not address:
                QMessageBox.warning(
                    self,
                    "Проверка",
                    "Укажите фамилию пациента и/или адрес прописки.",
                )
                return None
            return SearchCriteria(mode=mode, surname=surname, address=address)

        if mode == SearchMode.BIRTH_DATE:
            return SearchCriteria(mode=mode, birth_date=self.birth_picker.get_date())

        doc_parts = (
            self.doc_surname.text().strip(),
            self.doc_name.text().strip(),
            self.doc_patronymic.text().strip(),
        )
        has_doctor = any(doc_parts)
        appointment = (
            self.appointment_picker.get_date()
            if self.use_appointment.isChecked()
            else None
        )
        if not has_doctor and appointment is None:
            QMessageBox.warning(
                self,
                "Проверка",
                "Укажите элемент ФИО врача и/или отметьте дату приёма.",
            )
            return None
        return SearchCriteria(
            mode=mode,
            doctor_surname=doc_parts[0],
            doctor_name=doc_parts[1],
            doctor_patronymic=doc_parts[2],
            appointment_date=appointment,
        )
