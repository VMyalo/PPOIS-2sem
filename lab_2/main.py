#!/usr/bin/env python3
"""Точка входа: учёт пациентов, лабораторная №2, вариант 5."""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.controller.app_controller import AppController


def main() -> None:
    app = QApplication(sys.argv)
    data_dir = ROOT / "data"
    db_path = data_dir / "patients.db"
    controller = AppController(db_path, app)
    sys.exit(controller.run())


if __name__ == "__main__":
    main()
