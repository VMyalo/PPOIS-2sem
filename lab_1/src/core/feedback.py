"""Модуль обратной связи для обучения и улучшения системы.

Содержит классы для сбора, хранения и обработки обратной связи
от пользователей о работе интеллектуальной системы.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from ..utils.validators import DataValidator


class Feedback:
    """Класс обратной связи.

    Представляет отзыв пользователя о работе системы,
    включая оценку и комментарии.

    Атрибуты:
        feedback_id (str): Уникальный идентификатор обратной связи.
        user_id (str): Идентификатор пользователя.
        rating (float): Оценка (обычно от 1 до 5).
        comment (str): Текстовый комментарий.
        timestamp (datetime): Время создания отзыва.
        context (Dict[str, Any]): Контекст (что оценивалось).
    """

    MIN_RATING = 1.0
    MAX_RATING = 5.0

    def __init__(
        self,
        rating: float,
        user_id: str = "anonymous",
        comment: str = "",
        context: Optional[Dict[str, Any]] = None,
        feedback_id: str = None,
        timestamp: datetime = None,
    ):
        """Инициализация обратной связи.

        Args:
            rating: Оценка (от 1 до 5).
            user_id: Идентификатор пользователя.
            comment: Текстовый комментарий.
            context: Контекст обратной связи.
            feedback_id: Уникальный идентификатор.
            timestamp: Время создания.

        Raises:
            ValueError: Если rating вне допустимого диапазона.
        """
        DataValidator.validate_range(
            rating,
            min_value=self.MIN_RATING,
            max_value=self.MAX_RATING,
            field_name="rating",
        )

        self.feedback_id = feedback_id or str(uuid.uuid4())
        self.user_id = user_id
        self.rating = float(rating)
        self.comment = comment.strip() if comment else ""
        self.context = context.copy() if context else {}
        self.timestamp = timestamp or datetime.now()

    def is_positive(self) -> bool:
        """Проверяет, является ли отзыв положительным.

        Returns:
            True если оценка >= 4, иначе False.
        """
        return self.rating >= 4.0

    def is_negative(self) -> bool:
        """Проверяет, является ли отзыв отрицательным.

        Returns:
            True если оценка < 3, иначе False.
        """
        return self.rating < 3.0

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует обратную связь в словарь.

        Returns:
            Словарь с данными отзыва.
        """
        return {
            "feedback_id": self.feedback_id,
            "user_id": self.user_id,
            "rating": self.rating,
            "comment": self.comment,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Feedback":
        """Создает обратную связь из словаря.

        Args:
            data: Словарь с данными.

        Returns:
            Экземпляр Feedback.
        """
        DataValidator.validate_dict_structure(
            data, ["feedback_id", "rating", "timestamp"], "Данные обратной связи"
        )

        return cls(
            rating=data["rating"],
            user_id=data.get("user_id", "anonymous"),
            comment=data.get("comment", ""),
            context=data.get("context", {}),
            feedback_id=data["feedback_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


class FeedbackCollector:
    """Коллектор обратной связи.

    Управляет сбором и хранением отзывов пользователей,
    предоставляя методы для добавления и анализа обратной связи.

    Атрибуты:
        feedbacks (List[Feedback]): Список собранных отзывов.
    """

    def __init__(self):
        """Инициализация коллектора обратной связи."""
        self.feedbacks: list[Feedback] = []

    def add_feedback(self, feedback: Feedback) -> None:
        """Добавляет обратную связь.

        Args:
            feedback: Отзыв для добавления.

        Raises:
            TypeError: Если feedback не является экземпляром Feedback.
        """
        DataValidator.validate_type(feedback, Feedback, "feedback")
        self.feedbacks.append(feedback)

    def create_feedback(
        self,
        rating: float,
        user_id: str = "anonymous",
        comment: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> Feedback:
        """Создает и добавляет обратную связь.

        Args:
            rating: Оценка.
            user_id: Идентификатор пользователя.
            comment: Комментарий.
            context: Контекст.

        Returns:
            Созданный объект Feedback.
        """
        feedback = Feedback(
            rating=rating, user_id=user_id, comment=comment, context=context
        )
        self.add_feedback(feedback)
        return feedback

    def get_feedbacks(self) -> list[Feedback]:
        """Получает все отзывы.

        Returns:
            Список всех отзывов.
        """
        return self.feedbacks.copy()

    def get_average_rating(self) -> float:
        """Вычисляет среднюю оценку.

        Returns:
            Средняя оценка или 0.0 если отзывов нет.
        """
        if not self.feedbacks:
            return 0.0

        total = sum(f.rating for f in self.feedbacks)
        return round(total / len(self.feedbacks), 2)

    def get_positive_feedbacks(self) -> list[Feedback]:
        """Получает положительные отзывы.

        Returns:
            Список положительных отзывов.
        """
        return [f for f in self.feedbacks if f.is_positive()]

    def get_negative_feedbacks(self) -> list[Feedback]:
        """Получает отрицательные отзывы.

        Returns:
            Список отрицательных отзывов.
        """
        return [f for f in self.feedbacks if f.is_negative()]

    def clear(self) -> None:
        """Очищает все отзывы."""
        self.feedbacks.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует коллектор в словарь.

        Returns:
            Словарь с данными.
        """
        return {"feedbacks": [f.to_dict() for f in self.feedbacks]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeedbackCollector":
        """Создает коллектор из словаря.

        Args:
            data: Словарь с данными.

        Returns:
            Экземпляр FeedbackCollector.
        """
        collector = cls()

        for feedback_data in data.get("feedbacks", []):
            collector.add_feedback(Feedback.from_dict(feedback_data))

        return collector
