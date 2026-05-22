from datetime import date

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QDateEdit, QWidget


class DatePicker(QWidget):
    """Компонент выбора даты с календарём."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._edit = QDateEdit(self)
        self._edit.setCalendarPopup(True)
        self._edit.setDisplayFormat("yyyy-MM-dd")
        self._edit.setDate(QDate.currentDate())

        from PyQt6.QtWidgets import QHBoxLayout

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._edit)

    def get_date(self) -> date:
        qd = self._edit.date()
        return date(qd.year(), qd.month(), qd.day())

    def set_date(self, value: date) -> None:
        self._edit.setDate(QDate(value.year, value.month, value.day))
