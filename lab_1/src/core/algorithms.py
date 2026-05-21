"""Модуль алгоритмов машинного обучения.

Содержит базовые классы и реализации алгоритмов, используемых
интеллектуальной системой для анализа данных и обучения.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ..utils.validators import DataValidator
from .data import DataSet


class MLAlgorithm(ABC):
    """Абстрактный базовый класс для алгоритмов машинного обучения.

    Определяет интерфейс, который должны реализовывать все алгоритмы,
    используемые в системе (обучение, предсказание, обновление).
    """

    def __init__(self, algorithm_id: str, algorithm_type: str):
        """Инициализация алгоритма.

        Args:
            algorithm_id: Уникальный идентификатор алгоритма.
            algorithm_type: Тип алгоритма (например, 'classification', 'regression').
        """
        self.algorithm_id = algorithm_id
        self.algorithm_type = algorithm_type
        self.is_trained = False

    @abstractmethod
    def train(self, data: DataSet) -> None:
        """Обучает алгоритм на предоставленных данных.

        Args:
            data: Набор данных для обучения.
        """
        pass

    @abstractmethod
    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Выполняет предсказание на основе входных данных.

        Args:
            input_data: Словарь с входными признаками.

        Returns:
            Словарь с результатами предсказания (label, confidence и т.д.).
        """
        pass

    def update(self, feedback: "Feedback") -> None:
        """Обновляет параметры алгоритма на основе обратной связи.

        По умолчанию ничего не делает. Переопределяется в подклассах.

        Args:
            feedback: Объект обратной связи от пользователя.
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Сериализует состояние алгоритма.

        Returns:
            Словарь с параметрами алгоритма.
        """
        return {
            "algorithm_id": self.algorithm_id,
            "algorithm_type": self.algorithm_type,
            "is_trained": self.is_trained,
        }


class SimpleThresholdAlgorithm(MLAlgorithm):
    """Простой алгоритм порогового обнаружения.

    Обучается на определении среднего значения по ключу.
    Предсказывает, превышает ли новое значение порог (среднее).
    """

    def __init__(self, algorithm_id: str = "threshold_v1", target_key: str = "value"):
        """Инициализация.

        Args:
            algorithm_id: Идентификатор.
            target_key: Ключ в данных, по которому происходит анализ.
        """
        super().__init__(algorithm_id, "threshold_detection")
        self.target_key = target_key
        self.threshold = 0.0
        self._training_count = 0

    def train(self, data: DataSet) -> None:
        """Вычисляет порог как среднее значение по истории данных.

        Args:
            data: Набор данных.
        """
        values = []
        for point in data.get_data_points():
            val = point.values.get(self.target_key)
            if val is not None:
                try:
                    values.append(float(val))
                except (ValueError, TypeError):
                    continue

        if values:
            self.threshold = sum(values) / len(values)
            self.is_trained = True
            self._training_count += 1

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Сравнивает входное значение с порогом.

        Args:
            input_data: Входные данные.

        Returns:
            Результат: {'label': 'high'/'low', 'threshold': float}
        """
        val = input_data.get(self.target_key, 0)
        label = "high" if val > self.threshold else "low"

        return {"label": label, "threshold": self.threshold, "value": val}

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"threshold": self.threshold, "target_key": self.target_key})
        return base

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Восстанавливает состояние из словаря."""
        self.threshold = data.get("threshold", 0.0)
        self.target_key = data.get("target_key", "value")
        self.is_trained = data.get("is_trained", False)
