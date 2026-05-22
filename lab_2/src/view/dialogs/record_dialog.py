from typing import Callable

from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
                             QMessageBox, QTextEdit, QVBoxLayout, QWidget)

from src.model.patient import PatientRecord
from src.view.widgets.date_picker import DatePicker


class RecordDialog(QDialog):
    """Диалог добавления записи о пациенте."""

    def __init__(
        self,
        parent: QWidget,
        on_save: Callable[[PatientRecord], None],
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Добавить запись")
        self.setModal(True)
        self._on_save = on_save

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.patient_fio = QLineEdit()
        self.address = QLineEdit()
        self.birth_date = DatePicker()
        self.appointment_date = DatePicker()
        self.doctor_fio = QLineEdit()
        self.conclusion = QTextEdit()
        self.conclusion.setMaximumHeight(100)

        form.addRow("ФИО пациента:", self.patient_fio)
        form.addRow("Адрес прописки:", self.address)
        form.addRow("Дата рождения:", self.birth_date)
        form.addRow("Дата приёма:", self.appointment_date)
        form.addRow("ФИО врача:", self.doctor_fio)
        form.addRow("Заключение:", self.conclusion)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Сохранить")
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _save(self) -> None:
        patient_fio = self.patient_fio.text().strip()
        address = self.address.text().strip()
        doctor_fio = self.doctor_fio.text().strip()
        conclusion = self.conclusion.toPlainText().strip()

        if not all([patient_fio, address, doctor_fio, conclusion]):
            QMessageBox.warning(self, "Проверка", "Заполните все обязательные поля.")
            return

        record = PatientRecord(
            patient_fio=patient_fio,
            address=address,
            birth_date=self.birth_date.get_date(),
            appointment_date=self.appointment_date.get_date(),
            doctor_fio=doctor_fio,
            conclusion=conclusion,
        )
        self._on_save(record)
        self.accept()
