"""Модуль управления состоянием системы.

Отвечает за сохранение и загрузку параметров системы,
обеспечивая персистентность между запусками.
"""

import os
from typing import Any, Dict, Optional

from ..exceptions import StateException
from ..utils.serializers import JSONSerializer
from ..utils.validators import DataValidator


class SystemState:
    """Класс состояния системы.

    Хранит конфигурацию и данные, необходимые для восстановления
    работы системы после перезагрузки.

    Атрибуты:
        state_id (str): Идентификатор состояния.
        version (int): Версия структуры данных.
        config (Dict): Словарь с конфигурацией.
        data (Dict): Словарь с сохраненными данными (например, веса алгоритмов).
    """

    DEFAULT_STATE_FILE = "system_state.json"

    def __init__(self, state_id: str = "main"):
        """Инициализация состояния.

        Args:
            state_id: Идентификатор состояния.
        """
        self.state_id = state_id
        self.version = 1
        self.config: Dict[str, Any] = {}
        self.data: Dict[str, Any] = {}

    def set_config(self, key: str, value: Any) -> None:
        """Устанавливает параметр конфигурации.

        Args:
            key: Ключ параметра.
            value: Значение.
        """
        self.config[key] = value

    def get_config(self, key: str, default: Any = None) -> Any:
        """Получает параметр конфигурации.

        Args:
            key: Ключ параметра.
            default: Значение по умолчанию.

        Returns:
            Значение параметра или default.
        """
        return self.config.get(key, default)

    def set_data(self, key: str, value: Any) -> None:
        """Сохраняет данные в состояние.

        Args:
            key: Ключ данных.
            value: Данные.
        """
        self.data[key] = value

    def get_data(self, key: str, default: Any = None) -> Any:
        """Получает данные из состояния.

        Args:
            key: Ключ данных.
            default: Значение по умолчанию.

        Returns:
            Данные или default.
        """
        return self.data.get(key, default)

    def save(self, filepath: Optional[str] = None) -> None:
        """Сохраняет состояние в файл.

        Args:
            filepath: Путь к файлу (по умолчанию DEFAULT_STATE_FILE).

        Raises:
            StateException: Если не удалось сохранить.
        """
        path = filepath or self.DEFAULT_STATE_FILE
        try:
            state_dict = {
                "state_id": self.state_id,
                "version": self.version,
                "config": self.config,
                "data": self.data,
            }
            JSONSerializer.save_to_file(state_dict, path)
        except Exception as e:
            raise StateException(f"Ошибка сохранения состояния: {str(e)}")

    def load(self, filepath: Optional[str] = None) -> bool:
        """Загружает состояние из файла.

        Args:
            filepath: Путь к файлу.

        Returns:
            True если загрузка успешна, иначе False.
        """
        path = filepath or self.DEFAULT_STATE_FILE
        if not os.path.exists(path):
            return False

        try:
            state_dict = JSONSerializer.load_from_file(path)
            self.state_id = state_dict.get("state_id", self.state_id)
            self.version = state_dict.get("version", self.version)
            self.config = state_dict.get("config", {})
            self.data = state_dict.get("data", {})
            return True
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Сериализует состояние.

        Returns:
            Словарь с данными состояния.
        """
        return {
            "state_id": self.state_id,
            "version": self.version,
            "config": self.config,
            "data": self.data,
        }
