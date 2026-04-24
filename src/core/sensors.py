"""Модуль сенсоров для сбора данных из окружающей среды.

Содержит классы сенсоров различных типов для сбора данных,
необходимых для работы интеллектуальной системы.
"""

import random
import uuid
from datetime import datetime
from typing import Any, Dict

from ..exceptions import SensorException


class Sensor:
    """Базовый класс сенсора для сбора данных.

    Атрибуты:
        sensor_id (str): Уникальный идентификатор сенсора.
        sensor_type (str): Тип сенсора (температура, влажность и т.д.).
        is_active (bool): Флаг активности сенсора.
    """

    def __init__(self, sensor_type: str, sensor_id: str = None):
        """Инициализация сенсора.

        Args:
            sensor_type: Тип сенсора.
            sensor_id: Уникальный идентификатор (генерируется автоматически, если не указан).

        Raises:
            ValueError: Если sensor_type пустой.
        """
        if not sensor_type or not sensor_type.strip():
            raise ValueError("Тип сенсора не может быть пустым")

        self.sensor_id = sensor_id or str(uuid.uuid4())
        self.sensor_type = sensor_type.strip()
        self.is_active = True

    def collect_data(self) -> Dict[str, Any]:
        """Собирает данные с сенсора.

        Returns:
            Словарь с данными сенсора, включающий:
                - sensor_id: Идентификатор сенсора
                - sensor_type: Тип сенсора
                - value: Значение данных
                - timestamp: Время сбора данных

        Raises:
            SensorException: Если сенсор не активен.
        """
        if not self.is_active:
            raise SensorException(f"Сенсор {self.sensor_id} не активен")

        return {
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type,
            "value": self._read_value(),
            "timestamp": datetime.now().isoformat(),
        }

    def _read_value(self) -> Any:
        """Считывает значение с сенсора.

        Returns:
            Значение, полученное от сенсора.

        Note:
            Этот метод должен быть переопределен в подклассах.
        """
        raise NotImplementedError(
            "Метод _read_value должен быть реализован в подклассе"
        )

    def calibrate(self) -> None:
        """Калибрует сенсор.

        Note:
            Этот метод может быть переопределен в подклассах
            для реализации специфичной калибровки.
        """
        pass

    def activate(self) -> None:
        """Активирует сенсор."""
        self.is_active = True

    def deactivate(self) -> None:
        """Деактивирует сенсор."""
        self.is_active = False

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует сенсор в словарь.

        Returns:
            Словарь с данными сенсора.
        """
        return {
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type,
            "is_active": self.is_active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Sensor":
        """Создает сенсор из словаря.

        Args:
            data: Словарь с данными сенсора.

        Returns:
            Экземпляр сенсора.
        """
        # Если восстанавливаем базовый Sensor, попробуем подобрать подходящий подкласс по sensor_type.
        if cls is Sensor:
            sensor_type = (data.get("sensor_type") or "").strip().lower()
            sensor_cls = _SENSOR_TYPE_TO_CLASS.get(sensor_type)
            if sensor_cls is not None:
                return sensor_cls.from_dict(data)

        # Подклассы (TemperatureSensor/HumiditySensor/LightSensor) принимают только sensor_id,
        # базовый Sensor — sensor_type и sensor_id.
        try:
            sensor = cls(
                sensor_type=data["sensor_type"], sensor_id=data.get("sensor_id")
            )
        except TypeError:
            sensor = cls(sensor_id=data.get("sensor_id"))
        sensor.is_active = data.get("is_active", True)
        return sensor


class TemperatureSensor(Sensor):
    """Сенсор температуры.

    Симулирует сбор данных о температуре окружающей среды.
    """

    def __init__(self, sensor_id: str = None):
        """Инициализация температурного сенсора.

        Args:
            sensor_id: Уникальный идентификатор сенсора.
        """
        super().__init__(sensor_type="temperature", sensor_id=sensor_id)
        self.min_temp = -50.0
        self.max_temp = 50.0

    def _read_value(self) -> float:
        """Считывает температуру.

        Returns:
            Температура в градусах Цельсия (симулированное значение).
        """
        return round(random.uniform(self.min_temp, self.max_temp), 2)


class HumiditySensor(Sensor):
    """Сенсор влажности.

    Симулирует сбор данных о влажности окружающей среды.
    """

    def __init__(self, sensor_id: str = None):
        """Инициализация сенсора влажности.

        Args:
            sensor_id: Уникальный идентификатор сенсора.
        """
        super().__init__(sensor_type="humidity", sensor_id=sensor_id)

    def _read_value(self) -> float:
        """Считывает влажность.

        Returns:
            Влажность в процентах (симулированное значение).
        """
        return round(random.uniform(0.0, 100.0), 2)


class LightSensor(Sensor):
    """Сенсор освещенности.

    Симулирует сбор данных об уровне освещенности.
    """

    def __init__(self, sensor_id: str = None):
        """Инициализация сенсора освещенности.

        Args:
            sensor_id: Уникальный идентификатор сенсора.
        """
        super().__init__(sensor_type="light", sensor_id=sensor_id)

    def _read_value(self) -> float:
        """Считывает уровень освещенности.

        Returns:
            Уровень освещенности в люксах (симулированное значение).
        """
        return round(random.uniform(0.0, 10000.0), 2)


_SENSOR_TYPE_TO_CLASS: dict[str, type[Sensor]] = {
    "temperature": TemperatureSensor,
    "humidity": HumiditySensor,
    "light": LightSensor,
}
