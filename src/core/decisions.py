"""Модуль принятия решений.

Содержит логику анализа предсказаний алгоритмов
и формирования действий системы.
"""

from typing import Any, Dict


class DecisionEngine:
    """Движок принятия решений.

    Анализирует результаты алгоритмов и контекст среды,
    чтобы выдать решение о действиях системы.
    """

    def __init__(self):
        """Инициализация движка."""
        self.rules = []

    def make_decision(
        self, prediction: Dict[str, Any], context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Принимает решение на основе предсказания.

        Args:
            prediction: Результат работы алгоритма ML.
            context: Дополнительный контекст (опционально).

        Returns:
            Словарь с принятым решением (action, reason).
        """
        action = "monitor"
        reason = "No specific action required"

        # Простая логика на основе метки предсказания
        label = prediction.get("label")

        if label == "high":
            action = "alert"
            reason = f"Detected high value (> {prediction.get('threshold', 0)})"
        elif label == "low":
            action = "log"
            reason = "Value within normal range"

        return {
            "action": action,
            "reason": reason,
            "prediction": prediction,
            "timestamp": context.get("timestamp") if context else None,
        }
