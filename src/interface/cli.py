"""Модуль интерфейса командной строки (CLI)."""

import sys

from ..core.algorithms import SimpleThresholdAlgorithm
from ..core.sensors import HumiditySensor, LightSensor, TemperatureSensor
from ..core.system import IntelligentSystem


class IntelligentSystemCLI:
    """Класс CLI для управления системой."""

    def __init__(self, system: IntelligentSystem):
        """Инициализация CLI."""
        self.system = system

    def start(self) -> None:
        """Запускает основной цикл CLI."""
        print(f"=== Запуск интеллектуальной системы '{self.system.name}' ===")

        # Всегда создаем алгоритм сначала и загружаем состояние в него.
        algo = SimpleThresholdAlgorithm()
        self.system.algorithm = algo

        is_loaded = self.system.load_state(algorithm=algo)
        print(
            "[INFO] Состояние системы успешно загружено."
            if is_loaded
            else "[INFO] Создана новая сессия."
        )

        # Сенсоры теперь могут быть восстановлены из состояния. Если сенсоров нет (или не хватает),
        # подключаем дефолтные, но не дублируем уже существующие.
        self._ensure_default_sensors()
        active = [
            s.sensor_type for s in self.system.sensors if getattr(s, "is_active", False)
        ]
        if active:
            print("[INFO] Активные сенсоры: " + ", ".join(active))
        else:
            print("[INFO] Нет активных сенсоров.")

        # Сразу покажем состояние после инициализации (это помогает понять, что загрузилось).
        print("\n" + self.system.get_status_report())

        self._main_loop()

    def _ensure_default_sensors(self) -> None:
        """Добавляет стандартные сенсоры, если их нет (или они не все подключены)."""
        existing_types = {
            s.sensor_type for s in self.system.sensors if hasattr(s, "sensor_type")
        }

        if "temperature" not in existing_types:
            self.system.add_sensor(TemperatureSensor())
        if "humidity" not in existing_types:
            self.system.add_sensor(HumiditySensor())
        if "light" not in existing_types:
            self.system.add_sensor(LightSensor())

    def _main_loop(self) -> None:
        """Основной цикл обработки команд."""
        while True:
            self._print_menu()
            choice = input("\nВыберите действие: ").strip()

            if choice == "1":
                self._cmd_collect()
            elif choice == "2":
                self._cmd_train()
            elif choice == "3":
                self._cmd_adapt()
            elif choice == "4":
                self._cmd_decide()
            elif choice == "5":
                self._cmd_feedback()
            elif choice == "6":
                self._cmd_save()
            elif choice == "7":
                self._cmd_status()
            elif choice == "0":
                print("Выход из системы. Сохранение...")
                self.system.save_state()
                print("Состояние сохранено. До свидания!")
                break
            else:
                print("Неверный ввод. Попробуйте снова.")

    @staticmethod
    def _print_menu() -> None:
        """Выводит меню действий."""
        print("\n--- Меню ---")
        print("1. Собрать данные с сенсоров")
        print("2. Обучить систему")
        print("3. Адаптировать к среде")
        print("4. Принять решение")
        print("5. Оставить отзыв")
        print("6. Сохранить состояние")
        print("7. Посмотреть состояние системы")  # Новая кнопка
        print("0. Выход")
        print("--------------")

    def _cmd_collect(self) -> None:
        """Команда сбора данных."""
        try:
            data = self.system.collect_environment_data()
            print("\n[Данные]:")
            for k, v in data.items():
                print(f"  {k}: {v}")
        except Exception as e:
            print(f"[Ошибка]: {e}")

    def _cmd_train(self) -> None:
        """Команда обучения."""
        print("\n[Обучение]...")
        result = self.system.train_system()
        print(result)

    def _cmd_adapt(self) -> None:
        """Команда адаптации."""
        print("\n[Адаптация]...")
        result = self.system.adapt_to_environment()
        print(result)

    def _cmd_decide(self) -> None:
        """Команда принятия решения."""
        print("\n[Принятие решения]...")
        decision = self.system.make_decision()
        print(f"Действие: {decision['action']}")
        print(f"Причина: {decision['reason']}")

    def _cmd_feedback(self) -> None:
        """Команда обратной связи."""
        try:
            rating = float(input("Введите оценку (1.0 - 5.0): "))
            comment = input("Комментарий (Enter для пропуска): ")
            result = self.system.update_algorithms(rating, comment)
            print(result)
        except ValueError:
            print("Ошибка: Рейтинг должен быть числом.")

    def _cmd_save(self) -> None:
        """Команда сохранения."""
        self.system.save_state()
        print("Состояние успешно сохранено.")

    def _cmd_status(self) -> None:
        """Команда просмотра состояния."""
        print("\n" + self.system.get_status_report())
