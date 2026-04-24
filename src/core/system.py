"""Модуль основной интеллектуальной системы.

Содержит класс IntelligentSystem, который объединяет все компоненты
и управляет жизненным циклом.
"""

from typing import Any, Dict, List, Optional

from ..exceptions import SensorException
from .algorithms import MLAlgorithm
from .data import DataSet
from .decisions import DecisionEngine
from .feedback import FeedbackCollector
from .sensors import Sensor
from .state import SystemState


class IntelligentSystem:
    """Главный класс интеллектуальной системы."""

    def __init__(self, name: str = "IS_v1"):
        """Инициализация системы."""
        self.name = name
        self.sensors: List[Sensor] = []
        self.algorithm: MLAlgorithm = None
        self.decision_engine = DecisionEngine()
        self.state = SystemState()
        self.dataset = DataSet(name=f"{name}_dataset")
        self.feedback_collector = FeedbackCollector()
        # Какой сенсор считаем "основным" для обучения/решения по умолчанию.
        # Это защищает от смешивания разных шкал (например, light vs temperature).
        self.primary_sensor_type: str = "temperature"

        self._initialized = False

    def load_and_initialize(self, algorithm: MLAlgorithm) -> bool:
        """Загружает состояние и инициализирует систему с переданным алгоритмом.

        Args:
            algorithm: Экземпляр алгоритма, в который нужно загрузить данные.

        Returns:
            True если состояние успешно загружено, иначе False.
        """
        self.algorithm = algorithm
        return self.load_state(algorithm=algorithm)

    def load_state(self, filepath: str = None, algorithm: MLAlgorithm = None) -> bool:
        """Загружает состояние системы (совместимость с CLI/тестами).

        Если передан algorithm, будет восстановлено его состояние; иначе будет
        использован self.algorithm (если он задан).
        """
        algo = algorithm or self.algorithm
        loaded = self.state.load(filepath)
        if not loaded:
            return False

        if algo is not None:
            algo_state = self.state.get_data("algorithm_state")
            if algo_state:
                algo.from_dict(algo_state)
            self.algorithm = algo

        system_state = self.state.get_data("system_state")
        if isinstance(system_state, dict):
            self._load_system_state_dict(system_state)

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Сериализует систему (без DecisionEngine/State как объектов)."""
        return {
            "name": self.name,
            "sensors": [s.to_dict() for s in self.sensors],
            "dataset": self.dataset.to_dict(),
            "feedback": self.feedback_collector.to_dict(),
        }

    def _load_system_state_dict(self, data: Dict[str, Any]) -> None:
        """Восстанавливает данные системы из словаря (частично, без алгоритма)."""
        try:
            name = data.get("name")
            if isinstance(name, str) and name.strip():
                self.name = name.strip()
        except Exception:
            pass

        try:
            sensors_data = data.get("sensors", [])
            if isinstance(sensors_data, list):
                self.sensors = [
                    Sensor.from_dict(s) for s in sensors_data if isinstance(s, dict)
                ]
        except Exception:
            # Не мешаем загрузке, если сенсоры повреждены
            pass

        try:
            dataset_data = data.get("dataset")
            if isinstance(dataset_data, dict):
                self.dataset = DataSet.from_dict(dataset_data)
        except Exception:
            pass

        try:
            fb_data = data.get("feedback")
            if isinstance(fb_data, dict):
                self.feedback_collector = FeedbackCollector.from_dict(fb_data)
        except Exception:
            pass

    def add_sensor(self, sensor: Sensor) -> None:
        """Добавляет сенсор в систему."""
        self.sensors.append(sensor)

    def collect_environment_data(self) -> Dict[str, Any]:
        """Собирает данные со всех активных сенсоров."""
        if not self.sensors:
            raise SensorException("Нет подключенных сенсоров")

        collected_data = {}
        for sensor in self.sensors:
            if sensor.is_active:
                try:
                    data = sensor.collect_data()
                    collected_data[sensor.sensor_type] = data["value"]

                    from .data import DataPoint

                    dp = DataPoint(
                        values={
                            "sensor_id": sensor.sensor_id,
                            "sensor_type": sensor.sensor_type,
                            "value": data["value"],
                        }
                    )
                    self.dataset.add_data_point(dp)
                except SensorException:
                    continue
        return collected_data

    def train_system(self) -> str:
        """Запускает процесс обучения системы."""
        if self.dataset.size() == 0:
            return "Недостаточно данных для обучения (набор пуст)."

        try:
            self.algorithm.train(self._get_training_dataset())
            # Сразу сохраняем состояние алгоритма в объект State
            self.state.set_data("algorithm_state", self.algorithm.to_dict())
            return "Система успешно обучена."
        except Exception as e:
            return f"Ошибка обучения: {str(e)}"

    def adapt_to_environment(self) -> str:
        """Адаптирует систему к текущим условиям."""
        if not self.algorithm:
            return "Система не инициализирована."

        try:
            latest_data = self._get_training_dataset().get_latest_data(count=5)
            if len(latest_data) < 2:
                return "Недостаточно свежих данных для адаптации."

            from .data import DataSet

            adapt_dataset = DataSet("adapt_temp")
            for dp in latest_data:
                adapt_dataset.add_data_point(dp)

            self.algorithm.train(adapt_dataset)
            self.state.set_data("algorithm_state", self.algorithm.to_dict())
            return "Система адаптировалась к изменениям среды."
        except Exception as e:
            return f"Ошибка адаптации: {str(e)}"

    def make_decision(self) -> Dict[str, Any]:
        """Принимает решение на основе текущих данных."""
        try:
            env_data = self.collect_environment_data()

            # Важно: алгоритмы (например, SimpleThresholdAlgorithm) ожидают признаки вида {"value": ...},
            # а collect_environment_data возвращает {"temperature": ..., "humidity": ...}.
            features: Dict[str, Any] = dict(env_data)
            target_key: Optional[str] = getattr(self.algorithm, "target_key", None)
            if target_key and target_key not in features:
                # Самый безопасный дефолт: если есть ровно 1 активный сенсор — используем его значение.
                if len(env_data) == 1:
                    features[target_key] = next(iter(env_data.values()))
                # Если сенсоров несколько — попробуем предпочтительно температуру, иначе первое значение.
                elif self.primary_sensor_type in env_data:
                    features[target_key] = env_data[self.primary_sensor_type]
                elif "temperature" in env_data:
                    features[target_key] = env_data["temperature"]
                elif env_data:
                    features[target_key] = next(iter(env_data.values()))

            prediction = self.algorithm.predict(features)
            decision = self.decision_engine.make_decision(
                prediction,
                context={"timestamp": None, "env_data": env_data, "features": features},
            )
            return decision
        except Exception as e:
            return {"action": "error", "reason": str(e)}

    def update_algorithms(self, rating: float, comment: str = "") -> str:
        """Обновляет алгоритмы на основе обратной связи."""
        try:
            self.feedback_collector.create_feedback(rating, comment=comment)
            return "Обратная связь принята."
        except Exception as e:
            return f"Ошибка: {str(e)}"

    def save_state(self) -> None:
        """Сохраняет текущее состояние системы на диск."""
        # Обновляем данные алгоритма перед сохранением
        if self.algorithm:
            self.state.set_data("algorithm_state", self.algorithm.to_dict())
        # Сохраняем расширенное состояние системы
        self.state.set_data("system_state", self.to_dict())
        self.state.save()

    def get_status_report(self) -> str:
        """Формирует текстовый отчет о текущем состоянии системы.

        Returns:
            Строка с описанием состояния.
        """
        report = []
        report.append(f"=== Состояние системы '{self.name}' ===")

        if self.algorithm:
            algo_dict = self.algorithm.to_dict()
            report.append(f"Алгоритм: {algo_dict.get('algorithm_id', 'Неизвестно')}")
            report.append(f"Обучен: {'Да' if self.algorithm.is_trained else 'Нет'}")
            report.append(f"Текущий порог: {algo_dict.get('threshold', 'N/A')}")
        else:
            report.append("Алгоритм: Не инициализирован")

        report.append(f"Данных в наборе: {self.dataset.size()}")
        report.append(f"Основной сенсор: {self.primary_sensor_type}")
        report.append(
            f"Активных сенсоров: {len([s for s in self.sensors if s.is_active])}"
        )
        report.append(f"Отзывов получено: {len(self.feedback_collector.feedbacks)}")
        report.append("==================================")

        return "\n".join(report)

    def _get_training_dataset(self) -> DataSet:
        """Возвращает набор данных для обучения (по возможности, одного типа сенсора)."""
        points = self.dataset.get_data_points()
        has_sensor_type = any(
            isinstance(getattr(p, "values", None), dict) and "sensor_type" in p.values
            for p in points
        )
        if not has_sensor_type:
            return self.dataset

        from .data import DataSet

        ds = DataSet(name=f"{self.dataset.name}_{self.primary_sensor_type}")
        for p in points:
            try:
                if p.values.get("sensor_type") == self.primary_sensor_type:
                    ds.add_data_point(p)
            except Exception:
                continue
        return ds
