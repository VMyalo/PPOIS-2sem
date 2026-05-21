# Интеллектуальная система (ЛР №1, вариант 38)

Проект моделирует интеллектуальную систему, которая:
- собирает данные с сенсоров;
- обучает простой ML-алгоритм;
- адаптируется к новым данным;
- принимает решения (`alert`, `log`, `monitor`);
- сохраняет и восстанавливает состояние из JSON.

## Возможности

- **Сенсоры**: температура, влажность, освещенность.
- **Алгоритм**: `SimpleThresholdAlgorithm` (пороговая модель).
- **Решения**: через `DecisionEngine` на основе предсказания алгоритма.
- **Хранение состояния**:
  - `algorithm_state` (состояние алгоритма),
  - `system_state` (имя системы, сенсоры, dataset, feedback).
- **CLI**: интерактивное меню для всех основных операций.

## Требования

- Python 3.12+ (в проекте используется `python3`).
- Зависимости из `requirements.txt` (если файл пустой, достаточно `pytest` и `pytest-cov` для тестов/coverage).

## Установка и запуск

### 1) Клонирование и вход в каталог проекта

```bash
cd "/home/vsevolod/Рабочий стол/ppois-2sem/lab_1"
```

### 2) (Опционально) виртуальное окружение

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3) Установка зависимостей

```bash
python3 -m pip install -U pip
python3 -m pip install -r requirements.txt
python3 -m pip install pytest pytest-cov
```

### 4) Запуск приложения (CLI)

```bash
python3 -m src.main.main
```

Если этот модуль не используется в вашей локальной версии, запускайте точку входа, которая есть в проекте (например, отдельный `main.py`).

## Меню CLI

- `1` — собрать данные с сенсоров;
- `2` — обучить систему;
- `3` — адаптировать к среде;
- `4` — сделать решение;
- `5` — оставить отзыв;
- `6` — сохранить состояние;
- `7` — показать статус;
- `0` — выход (с автосохранением).

## Тестирование

### Запуск всех тестов

```bash
python3 -m pytest -q
```

### Запуск тестов с coverage

```bash
python3 -m pytest --cov=src --cov-report=term-missing --cov-report=html
```

HTML-отчет появится в каталоге `htmlcov/`.

## Структура проекта

```text
src/
  core/
    algorithms.py      # ML-алгоритмы
    data.py            # DataPoint/DataSet
    decisions.py       # DecisionEngine
    feedback.py        # Feedback/FeedbackCollector
    sensors.py         # Sensor + конкретные сенсоры
    state.py           # SystemState (save/load)
    system.py          # Главный класс IntelligentSystem
  interface/
    cli.py             # CLI-интерфейс
  exceptions/
    exceptions.py      # Пользовательские исключения
  utils/
    serializers.py     # JSON сериализация
    validators.py      # Валидации
tests/
  unittests.py
uml/
  classes_IntelligentSystem.puml
  packages_IntelligentSystem.puml
  states_IntelligentSystem.puml
```

## Формат состояния (`system_state.json`)

Состояние хранится в `data`:
- `algorithm_state`: сериализованное состояние алгоритма;
- `system_state`:
  - `name`
  - `sensors[]`
  - `dataset` (включая `data_points`)
  - `feedback` (список отзывов)

Это позволяет восстанавливать не только алгоритм, но и контекст сессии.

## Примечания по логике решений

- Алгоритм по умолчанию использует `target_key="value"`.
- В системе введен `primary_sensor_type` (по умолчанию `temperature`), чтобы не смешивать шкалы разных сенсоров при обучении.
- Если модель обучить на данных только температуры, решения становятся стабильнее и предсказуемее.
