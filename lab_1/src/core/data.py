"""Модуль управления данными интеллектуальной системы.

Содержит классы для хранения, обработки и управления данными,
собираемыми сенсорами и используемыми алгоритмами машинного обучения.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..utils.validators import DataValidator


class DataPoint:
    """Класс точки данных.

    Представляет единичное измерение или наблюдение,
    полученное от сенсора или созданное системой.

    Атрибуты:
        point_id (str): Уникальный идентификатор точки данных.
        timestamp (datetime): Время создания точки данных.
        values (Dict[str, Any]): Словарь с данными (ключ-значение).
        metadata (Dict[str, Any]): Дополнительные метаданные.
    """

    def __init__(
        self,
        values: Dict[str, Any],
        meta: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        point_id: str = None,
        timestamp: datetime = None,
    ):
        """Инициализация точки данных.

        Args:
            values: Словарь с данными.
            metadata: Дополнительные метаданные (по умолчанию None).
            point_id: Уникальный идентификатор (генерируется автоматически).
            timestamp: Время создания (по умолчанию текущее время).

        Raises:
            ValueError: Если values пустой.
        """
        DataValidator.validate_type(values, dict, "values")
        if not values:
            raise ValueError("values не может быть пустым словарем")

        if meta is not None and metadata is not None:
            raise ValueError("Нельзя одновременно передавать meta и metadata")

        metadata = metadata if metadata is not None else meta

        self.point_id = point_id or str(uuid.uuid4())
        self.timestamp = timestamp or datetime.now()
        self.values = values.copy()
        self.metadata = metadata.copy() if metadata else {}

    def get_value(self, key: str, default: Any = None) -> Any:
        """Получает значение по ключу.

        Args:
            key: Ключ для поиска.
            default: Значение по умолчанию (если ключ не найден).

        Returns:
            Значение по ключу или default.
        """
        return self.values.get(key, default)

    def set_value(self, key: str, value: Any) -> None:
        """Устанавливает значение по ключу.

        Args:
            key: Ключ.
            value: Значение.
        """
        self.values[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует точку данных в словарь.

        Returns:
            Словарь с данными точки.
        """
        return {
            "point_id": self.point_id,
            "timestamp": self.timestamp.isoformat(),
            "values": self.values,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataPoint":
        """Создает точку данных из словаря.

        Args:
            data: Словарь с данными.

        Returns:
            Экземпляр DataPoint.
        """
        DataValidator.validate_dict_structure(
            data, ["point_id", "timestamp", "values"], "Данные точки"
        )

        return cls(
            values=data["values"],
            metadata=data.get("metadata", {}),
            point_id=data["point_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


class DataSet:
    """Класс набора данных.

    Управляет коллекцией точек данных, предоставляя методы
    для добавления, удаления, фильтрации и получения данных.

    Атрибуты:
        name (str): Имя набора данных.
        data_points (List[DataPoint]): Список точек данных.
        created_at (datetime): Время создания набора.
    """

    def __init__(self, name: str = "default_dataset"):
        """Инициализация набора данных.

        Args:
            name: Имя набора данных.

        Raises:
            ValueError: Если name пустой.
        """
        DataValidator.validate_non_empty_string(name, "name")

        self.name = name.strip()
        self.data_points: List[DataPoint] = []
        self.created_at = datetime.now()

    def add_data_point(self, data_point: DataPoint) -> None:
        """Добавляет точку данных в набор.

        Args:
            data_point: Точка данных для добавления.

        Raises:
            TypeError: Если data_point не является экземпляром DataPoint.
        """
        DataValidator.validate_type(data_point, DataPoint, "data_point")
        self.data_points.append(data_point)

    def add_data_point_from_dict(self, data: Dict[str, Any]) -> None:
        """Создает и добавляет точку данных из словаря.

        Args:
            data: Словарь с данными точки.
        """
        data_point = DataPoint.from_dict(data)
        self.add_data_point(data_point)

    def get_data_points(self) -> List[DataPoint]:
        """Получает все точки данных.

        Returns:
            Список всех точек данных.
        """
        return self.data_points.copy()

    def get_data_points_by_type(self, sensor_type: str) -> List[DataPoint]:
        """Фильтрует точки данных по типу сенсора.

        Args:
            sensor_type: Тип сенсора для фильтрации.

        Returns:
            Список точек данных указанного типа.
        """
        return [
            dp for dp in self.data_points if dp.values.get("sensor_type") == sensor_type
        ]

    def get_latest_data(self, count: int = 1) -> List[DataPoint]:
        """Получает последние N точек данных.

        Args:
            count: Количество точек данных (по умолчанию 1).

        Returns:
            Список последних точек данных.
        """
        DataValidator.validate_positive_number(count, "count")
        sorted_points = sorted(
            self.data_points, key=lambda x: x.timestamp, reverse=True
        )
        return sorted_points[: int(count)]

    def clear(self) -> None:
        """Очищает все точки данных."""
        self.data_points.clear()

    def size(self) -> int:
        """Получает количество точек данных.

        Returns:
            Количество точек данных.
        """
        return len(self.data_points)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует набор данных в словарь.

        Returns:
            Словарь с данными набора.
        """
        return {
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "data_points": [dp.to_dict() for dp in self.data_points],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataSet":
        """Создает набор данных из словаря.

        Args:
            data: Словарь с данными.

        Returns:
            Экземпляр DataSet.
        """
        DataValidator.validate_dict_structure(
            data, ["name", "created_at", "data_points"], "Данные набора"
        )

        dataset = cls(name=data["name"])
        dataset.created_at = datetime.fromisoformat(data["created_at"])

        for point_data in data["data_points"]:
            dataset.add_data_point(DataPoint.from_dict(point_data))

        return dataset
