from typing import Callable, List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (QCheckBox, QFileDialog, QHeaderView, QMainWindow,
                             QMessageBox, QStackedWidget, QTableWidget,
                             QTableWidgetItem, QToolBar, QTreeWidget,
                             QTreeWidgetItem, QVBoxLayout, QWidget)

from src.model.patient import PatientRecord
from src.view.constants import COLUMNS, FIELD_LABELS, HEADERS
from src.view.widgets.pagination import PaginationBar


class MainWindow(QMainWindow):
    """Главное окно приложения (представление)."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Учёт пациентов — лабораторная №2, вариант 5")
        self.resize(1100, 620)

        self._callbacks: dict[str, Callable] = {}
        self._records: List[PatientRecord] = []

        self._build_menu()
        self._build_toolbar()
        self._build_body()

    def set_callbacks(self, callbacks: dict[str, Callable]) -> None:
        self._callbacks = callbacks

    def _call(self, name: str) -> None:
        if name in self._callbacks:
            self._callbacks[name]()

    def _build_menu(self) -> None:
        menubar = self.menuBar()

        record_menu = menubar.addMenu("Записи")
        record_menu.addAction("Добавить", lambda: self._call("add"))
        record_menu.addAction("Поиск", lambda: self._call("search"))
        record_menu.addAction("Удалить", lambda: self._call("delete"))

        view_menu = menubar.addMenu("Вид")
        self._tree_action = QAction("Отображение деревом", self)
        self._tree_action.setCheckable(True)
        self._tree_action.triggered.connect(self._toggle_view)
        view_menu.addAction(self._tree_action)

        file_menu = menubar.addMenu("Файл")
        file_menu.addAction("Загрузить XML…", lambda: self._call("load_xml"))
        file_menu.addAction("Сохранить XML…", lambda: self._call("save_xml"))
        file_menu.addSeparator()
        file_menu.addAction("Загрузить БД…", lambda: self._call("load_db"))
        file_menu.addAction("Сохранить БД…", lambda: self._call("save_db"))

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Действия")
        self.addToolBar(toolbar)

        for text, action in (
            ("Добавить", "add"),
            ("Поиск", "search"),
            ("Удалить", "delete"),
            ("Загрузить XML", "load_xml"),
            ("Сохранить XML", "save_xml"),
            ("Загрузить БД", "load_db"),
            ("Сохранить БД", "save_db"),
        ):
            toolbar.addAction(text, lambda _checked=False, a=action: self._call(a))

        self._tree_checkbox = QCheckBox("Дерево")
        self._tree_checkbox.stateChanged.connect(self._on_tree_checkbox)
        toolbar.addWidget(self._tree_checkbox)

    def _build_body(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(list(HEADERS))
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._stack.addWidget(self.table)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self._stack.addWidget(self.tree)

        self.pagination = PaginationBar(central, on_change=self._refresh_display)
        layout.addWidget(self.pagination)

    def _on_tree_checkbox(self) -> None:
        self._tree_action.setChecked(self._tree_checkbox.isChecked())
        self._toggle_view()

    def _toggle_view(self) -> None:
        tree_mode = self._tree_action.isChecked()
        self._tree_checkbox.blockSignals(True)
        self._tree_checkbox.setChecked(tree_mode)
        self._tree_checkbox.blockSignals(False)
        self._stack.setCurrentIndex(1 if tree_mode else 0)
        self._refresh_display()

    def set_records(self, records: List[PatientRecord]) -> None:
        self._records = records
        self._refresh_display()

    def _refresh_display(self) -> None:
        page_items = self.pagination.paginator.slice(self._records)
        if self._stack.currentIndex() == 0:
            self._fill_table(page_items)
        else:
            self._fill_tree(page_items)
        self.pagination.update_info(len(self._records), len(page_items))

    def _fill_table(self, page_items: List[PatientRecord]) -> None:
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

    def _fill_tree(self, page_items: List[PatientRecord]) -> None:
        self.tree.clear()
        for idx, record in enumerate(page_items, start=1):
            root = QTreeWidgetItem(
                [f"Запись #{record.id or idx}: {record.patient_fio}"]
            )
            self.tree.addTopLevelItem(root)
            for key in COLUMNS:
                value = getattr(record, key)
                if hasattr(value, "isoformat"):
                    value = value.isoformat()
                child = QTreeWidgetItem([f"{FIELD_LABELS[key]}: {value}"])
                root.addChild(child)
            root.setExpanded(True)

    def ask_open_xml(self) -> Optional[str]:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить XML",
            "",
            "XML файлы (*.xml);;Все файлы (*.*)",
        )
        return path or None

    def ask_save_xml(self) -> Optional[str]:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить XML",
            "",
            "XML файлы (*.xml)",
        )
        return path or None

    def ask_open_db(self) -> Optional[str]:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить базу данных",
            "",
            "SQLite (*.db);;Все файлы (*.*)",
        )
        return path or None

    def ask_save_db(self) -> Optional[str]:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить базу данных",
            "",
            "SQLite (*.db)",
        )
        return path or None

    def show_info(self, title: str, message: str) -> None:
        QMessageBox.information(self, title, message)

    def show_error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)
