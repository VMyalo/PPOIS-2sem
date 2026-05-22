from typing import Callable

from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QHBoxLayout,
                             QMessageBox, QPushButton, QVBoxLayout, QWidget)

from src.model.criteria import SearchCriteria
from src.view.dialogs.criteria_form import CriteriaForm


class DeleteDialog(QDialog):
    """Диалог удаления записей по условиям."""

    def __init__(
        self,
        parent: QWidget,
        on_delete: Callable[[SearchCriteria], int],
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Удаление записей")
        self.setModal(True)
        self._on_delete = on_delete

        layout = QVBoxLayout(self)
        self.criteria_form = CriteriaForm("Условия удаления", self)
        layout.addWidget(self.criteria_form)

        buttons = QHBoxLayout()
        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self._delete)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addStretch()
        buttons.addWidget(delete_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

    def _delete(self) -> None:
        criteria = self.criteria_form.build_criteria()
        if criteria is None:
            return
        answer = QMessageBox.question(
            self,
            "Подтверждение",
            "Удалить все записи, соответствующие условиям?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        count = self._on_delete(criteria)
        if count > 0:
            QMessageBox.information(self, "Результат", f"Удалено записей: {count}.")
        else:
            QMessageBox.information(
                self,
                "Результат",
                "Записи по заданным условиям не найдены.",
            )
        self.accept()
