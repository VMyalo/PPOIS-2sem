"""Точка входа в приложение.

Инициализирует систему и запускает CLI интерфейс.
"""

import os
import sys

from src.core.system import IntelligentSystem
from src.interface.cli import IntelligentSystemCLI

# Добавляем корень проекта в путь, чтобы работали импорты
# Если запуск из корня проекта: python -m src.main.main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main() -> None:
    """Главная функция запуска."""
    try:
        # Создаем экземпляр системы
        system = IntelligentSystem(name="SmartHome_v1")

        # Создаем и запускаем CLI
        cli = IntelligentSystemCLI(system)
        cli.start()

    except KeyboardInterrupt:
        print("\nПринудительное завершение.")
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
