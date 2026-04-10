"""Модуль валидации данных для интеллектуальной системы.

Предоставляет функции для проверки корректности данных,
вводимых пользователем или получаемых от сенсоров.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional


class DataValidator:
    """Валидатор данных для проверки корректности входных данных.

    Предоставляет методы для проверки типов, диапазонов значений
    и структуры данных.
    """

    @staticmethod
    def validate_not_none(value: Any, field_name: str) -> None:
        """Проверяет, что значение не является None.

        Args:
            value: Значение для проверки.
            field_name: Имя поля для сообщения об ошибке.

        Raises:
            ValueError: Если значение равно None.
        """
        if value is None:
            raise ValueError(f"Поле '{field_name}' не может быть None")

    @staticmethod
    def validate_type(value: Any, expected_type: type, field_name: str) -> None:
        """Проверяет тип значения.

        Args:
            value: Значение для проверки.
            expected_type: Ожидаемый тип.
            field_name: Имя поля для сообщения об ошибке.

        Raises:
            TypeError: Если тип значения не соответствует ожидаемому.
        """
        if not isinstance(value, expected_type):
            raise TypeError(
                f"Поле '{field_name}' должно быть типа {expected_type.__name__}, "
                f"получено {type(value).__name__}"
            )

    @staticmethod
    def validate_range(
        value: float,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        field_name: str = "Значение",
    ) -> None:
        """Проверяет, что значение находится в заданном диапазоне.

        Args:
            value: Значение для проверки.
            min_value: Минимально допустимое значение (None если не ограничено).
            max_value: Максимально допустимое значение (None если не ограничено).
            field_name: Имя поля для сообщения об ошибке.

        Raises:
            ValueError: Если значение выходит за пределы диапазона.
        """
        if min_value is not None and value < min_value:
            raise ValueError(
                f"{field_name} должно быть не меньше {min_value}, получено {value}"
            )
        if max_value is not None and value > max_value:
            raise ValueError(
                f"{field_name} должно быть не больше {max_value}, получено {value}"
            )

    @staticmethod
    def validate_non_empty_string(value: str, field_name: str) -> None:
        """Проверяет, что строка не пустая.

        Args:
            value: Строка для проверки.
            field_name: Имя поля для сообщения об ошибке.

        Raises:
            ValueError: Если строка пустая или содержит только пробелы.
        """
        DataValidator.validate_type(value, str, field_name)
        if not value.strip():
            raise ValueError(f"Поле '{field_name}' не может быть пустым")

    @staticmethod
    def validate_positive_number(value: float, field_name: str) -> None:
        """Проверяет, что число положительное.

        Args:
            value: Число для проверки.
            field_name: Имя поля для сообщения об ошибке.

        Raises:
            ValueError: Если число не положительное.
        """
        DataValidator.validate_type(value, (int, float), field_name)
        if value <= 0:
            raise ValueError(f"{field_name} должно быть положительным числом")

    @staticmethod
    def validate_dict_structure(
        data: Dict[str, Any], required_keys: List[str], dict_name: str = "Словарь"
    ) -> None:
        """Проверяет наличие обязательных ключей в словаре.

        Args:
            data: Словарь для проверки.
            required_keys: Список обязательных ключей.
            dict_name: Имя словаря для сообщения об ошибке.

        Raises:
            ValueError: Если отсутствуют обязательные ключи.
        """
        DataValidator.validate_type(data, dict, dict_name)
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            raise ValueError(
                f"{dict_name} не содержит обязательные ключи: {', '.join(missing_keys)}"
            )
