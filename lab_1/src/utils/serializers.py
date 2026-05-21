"""Модуль сериализации для сохранения и загрузки состояния системы.

Предоставляет функции для сериализации объектов в JSON формат
и десериализации из JSON формата.
"""

import json
from datetime import datetime
from typing import Any, Dict


class JSONSerializer:
    """Сериализатор для преобразования объектов в JSON и обратно.

    Поддерживает сериализацию стандартных типов Python,
    включая datetime и пользовательские классы с методом to_dict().
    """

    @staticmethod
    def serialize(obj: Any) -> str:
        """Сериализует объект в JSON строку.

        Args:
            obj: Объект для сериализации.

        Returns:
            JSON строка представления объекта.

        Raises:
            TypeError: Если объект не может быть сериализован.
        """
        return json.dumps(obj, default=JSONSerializer._default_serializer, indent=2)

    @staticmethod
    def deserialize(json_str: str) -> Any:
        """Десериализует JSON строку в объект Python.

        Args:
            json_str: JSON строка для десериализации.

        Returns:
            Десериализованный объект Python.

        Raises:
            json.JSONDecodeError: Если строка не является валидным JSON.
        """
        return json.loads(json_str)

    @staticmethod
    def save_to_file(data: Dict[str, Any], filepath: str) -> None:
        """Сохраняет данные в файл в формате JSON.

        Args:
            data: Словарь с данными для сохранения.
            filepath: Путь к файлу для сохранения.

        Raises:
            IOError: Если не удается записать в файл.
        """
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, default=JSONSerializer._default_serializer, indent=2)

    @staticmethod
    def load_from_file(filepath: str) -> Dict[str, Any]:
        """Загружает данные из файла JSON.

        Args:
            filepath: Путь к файлу для загрузки.

        Returns:
            Словарь с загруженными данными.

        Raises:
            FileNotFoundError: Если файл не найден.
            json.JSONDecodeError: Если файл содержит невалидный JSON.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _default_serializer(obj: Any) -> Any:
        """Метод для сериализации нестандартных типов.

        Args:
            obj: Объект для сериализации.

        Returns:
            Сериализуемое представление объекта.

        Raises:
            TypeError: Если объект не может быть сериализован.
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
