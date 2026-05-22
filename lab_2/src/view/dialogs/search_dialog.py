from typing import Callable, List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QDialog, QHeaderView, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from src.model.criteria import SearchCriteria
from src.model.patient import PatientRecord
from src.view.constants import COLUMNS, HEADERS
from src.view.dialogs.criteria_form import CriteriaForm
from src.view.widgets.pagination import PaginationBar


class SearchDialog(QDialog):
    """Диалог поиска с выводом результата и постраничной навигацией."""

    def __init__(
        self,
        parent: QWidget,
        on_search: Callable[[SearchCriteria], List[PatientRecord]],
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Поиск записей")
        self.resize(960, 520)
        self._on_search = on_search
        self._results: List[PatientRecord] = []

        layout = QVBoxLayout(self)

        self.criteria_form = CriteriaForm("Условия поиска", self)
        layout.addWidget(self.criteria_form)

        find_btn = QPushButton("Найти")
        find_btn.clicked.connect(self._run_search)
        layout.addWidget(find_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(list(HEADERS))
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        self.pagination = PaginationBar(self, on_change=self._refresh_table)
        layout.addWidget(self.pagination)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def _run_search(self) -> None:
        criteria = self.criteria_form.build_criteria()
        if criteria is None:
            return
        self._results = self._on_search(criteria)
        self.pagination.paginator.current_page = 1
        self._refresh_table()

    def _refresh_table(self) -> None:
        page_items = self.pagination.paginator.slice(self._results)
        self.table.setRowCount(len(page_items))
        for row, record in enumerate(page_items):
            values = (
                record.patient_fio,
                record.address,
                record.birth_date.isoformat(),
                record.appointment_date.isoformat(),
                record.doctor_fio,
                record.conclusion,
            )
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))
        self.pagination.update_info(len(self._results), len(page_items))
