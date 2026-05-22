from pathlib import Path
from typing import List

from PyQt6.QtWidgets import QApplication

from src.model.criteria import SearchCriteria
from src.model.patient import PatientRecord
from src.model.repository import PatientRepository
from src.view.dialogs.delete_dialog import DeleteDialog
from src.view.dialogs.record_dialog import RecordDialog
from src.view.dialogs.search_dialog import SearchDialog
from src.view.main_window import MainWindow


class AppController:
    """Контроллер MVC: связывает модель и представление."""

    def __init__(self, db_path: Path, app: QApplication) -> None:
        self._app = app
        self.repository = PatientRepository(db_path)
        self.view = MainWindow()
        self.view.set_callbacks(
            {
                "add": self.open_add_dialog,
                "search": self.open_search_dialog,
                "delete": self.open_delete_dialog,
                "load_xml": self.load_xml,
                "save_xml": self.save_xml,
                "load_db": self.load_database,
                "save_db": self.save_database,
            }
        )
        self.refresh_view()

    def run(self) -> int:
        self.view.show()
        code = self._app.exec()
        self.repository.close()
        return code

    def refresh_view(self) -> None:
        self.view.set_records(self.repository.get_all())

    def open_add_dialog(self) -> None:
        dialog = RecordDialog(self.view, on_save=self.add_record)
        dialog.exec()

    def add_record(self, record: PatientRecord) -> None:
        self.repository.add(record)
        self.refresh_view()
        self.view.show_info("Запись", "Запись успешно добавлена.")

    def open_search_dialog(self) -> None:
        dialog = SearchDialog(self.view, on_search=self.search_records)
        dialog.show()

    def search_records(self, criteria: SearchCriteria) -> List[PatientRecord]:
        return self.repository.search(criteria)

    def open_delete_dialog(self) -> None:
        dialog = DeleteDialog(self.view, on_delete=self.delete_records)
        dialog.exec()

    def delete_records(self, criteria: SearchCriteria) -> int:
        count = self.repository.delete_matching(criteria)
        self.refresh_view()
        return count

    def load_xml(self) -> None:
        path = self.view.ask_open_xml()
        if not path:
            return
        try:
            count = self.repository.load_xml(Path(path))
            self.refresh_view()
            self.view.show_info("XML", f"Загружено записей: {count}.")
        except Exception as exc:
            self.view.show_error("Ошибка", f"Не удалось загрузить XML:\n{exc}")

    def save_xml(self) -> None:
        path = self.view.ask_save_xml()
        if not path:
            return
        try:
            self.repository.save_xml(Path(path))
            self.view.show_info("XML", "Данные сохранены в файл.")
        except Exception as exc:
            self.view.show_error("Ошибка", f"Не удалось сохранить XML:\n{exc}")

    def load_database(self) -> None:
        path = self.view.ask_open_db()
        if not path:
            return
        try:
            count = self.repository.load_database(Path(path))
            self.refresh_view()
            self.view.show_info("База данных", f"Загружено записей: {count}.")
        except Exception as exc:
            self.view.show_error("Ошибка", f"Не удалось загрузить БД:\n{exc}")

    def save_database(self) -> None:
        path = self.view.ask_save_db()
        if not path:
            return
        try:
            self.repository.save_database(Path(path))
            self.view.show_info("База данных", "Данные сохранены в файл БД.")
        except Exception as exc:
            self.view.show_error("Ошибка", f"Не удалось сохранить БД:\n{exc}")
