"""Комплексные unit-тесты для интеллектуальной системы.

Тесты покрывают модули exceptions, utils, core и interface.
Используются pytest, unittest.mock и tmp_path для изоляции файловой системы.
"""

import json
import os
import random
from datetime import datetime
from unittest.mock import patch, mock_open
import pytest

from src.exceptions.exceptions import (
    IntelligentSystemException,
    SensorException,
    AlgorithmException,
    StateException,
    DataException,
    FeedbackException,
)
from src.utils.validators import DataValidator
from src.utils.serializers import JSONSerializer
from src.core.sensors import Sensor, TemperatureSensor, HumiditySensor, LightSensor
from src.core.data import DataPoint, DataSet
from src.core.feedback import Feedback, FeedbackCollector
from src.core.algorithms import SimpleThresholdAlgorithm
from src.core.decisions import DecisionEngine
from src.core.state import SystemState
from src.core.system import IntelligentSystem
from src.interface.cli import IntelligentSystemCLI


# ==================== EXCEPTIONS ====================

class TestExceptions:
    """Тесты пользовательских исключений."""

    def test_base_exception(self):
        exc = IntelligentSystemException("Test error", code=42)
        assert str(exc) == "Test error"
        assert exc.code == 42
        assert exc.message == "Test error"

    def test_inheritance(self):
        assert issubclass(SensorException, IntelligentSystemException)
        assert issubclass(AlgorithmException, IntelligentSystemException)
        assert issubclass(StateException, IntelligentSystemException)
        assert issubclass(DataException, IntelligentSystemException)
        assert issubclass(FeedbackException, IntelligentSystemException)

        exc = SensorException("Sensor failed", code=10)
        assert isinstance(exc, IntelligentSystemException)


# ==================== VALIDATORS ====================

class TestValidators:
    """Тесты модуля валидации данных."""

    def test_validate_not_none(self):
        DataValidator.validate_not_none("value", "field")
        with pytest.raises(ValueError, match="не может быть None"):
            DataValidator.validate_not_none(None, "field")

    def test_validate_type(self):
        DataValidator.validate_type(42, int, "num")
        with pytest.raises(TypeError, match="должно быть типа int"):
            DataValidator.validate_type("str", int, "num")

    def test_validate_range(self):
        DataValidator.validate_range(5.0, min_value=0.0, max_value=10.0)
        with pytest.raises(ValueError, match="не меньше"):
            DataValidator.validate_range(-1.0, min_value=0.0)
        with pytest.raises(ValueError, match="не больше"):
            DataValidator.validate_range(11.0, max_value=10.0)
        # None bounds should pass
        DataValidator.validate_range(100.0, min_value=None, max_value=None)

    def test_validate_non_empty_string(self):
        DataValidator.validate_non_empty_string(" valid ", "name")
        with pytest.raises(ValueError, match="не может быть пустым"):
            DataValidator.validate_non_empty_string("   ", "name")
        with pytest.raises(TypeError):
            DataValidator.validate_non_empty_string(123, "name")

    def test_validate_positive_number(self):
        DataValidator.validate_positive_number(1.0, "val")
        with pytest.raises(ValueError, match="положительным"):
            DataValidator.validate_positive_number(0, "val")
        with pytest.raises(ValueError):
            DataValidator.validate_positive_number(-5, "val")

    def test_validate_dict_structure(self):
        DataValidator.validate_dict_structure({"a": 1, "b": 2}, ["a", "b"])
        with pytest.raises(ValueError, match="не содержит обязательные ключи"):
            DataValidator.validate_dict_structure({"a": 1}, ["a", "b"])


# ==================== SERIALIZERS ====================

class TestSerializers:
    """Тесты сериализации JSON."""

    def test_serialize_deserialize(self):
        data = {"key": "value", "num": 42, "list": [1, 2]}
        json_str = JSONSerializer.serialize(data)
        assert JSONSerializer.deserialize(json_str) == data

    def test_serialize_datetime(self):
        dt = datetime(2024, 1, 1, 12, 0, 0)
        result = JSONSerializer.serialize({"time": dt})
        assert "2024-01-01T12:00:00" in result

    def test_serialize_custom_object(self):
        class MockObj:
            def to_dict(self): return {"x": 1}

        obj = MockObj()
        result = JSONSerializer.serialize({"obj": obj})
        assert json.loads(result)["obj"] == {"x": 1}

    def test_save_load_file(self, tmp_path):
        filepath = tmp_path / "test.json"
        JSONSerializer.save_to_file({"a": 1}, str(filepath))
        assert JSONSerializer.load_from_file(str(filepath)) == {"a": 1}

    def test_load_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            JSONSerializer.load_from_file(str(tmp_path / "missing.json"))

    def test_unserializable_object(self):
        with pytest.raises(TypeError, match="is not JSON serializable"):
            JSONSerializer.serialize(object())


# ==================== SENSORS ====================

class TestSensors:
    """Тесты сенсоров."""

    def test_sensor_init(self):
        s = Sensor("test_type", sensor_id="123")
        assert s.sensor_id == "123"
        assert s.sensor_type == "test_type"
        assert s.is_active is True

    def test_sensor_empty_type(self):
        with pytest.raises(ValueError):
            Sensor("  ")

    def test_collect_data_active(self):
        s = TemperatureSensor("t1")
        with patch.object(s, "_read_value", return_value=25.5):
            data = s.collect_data()
            assert data["value"] == 25.5
            assert data["sensor_type"] == "temperature"

    def test_collect_data_inactive(self):
        s = Sensor("type", "id")
        s.is_active = False
        with pytest.raises(SensorException):
            s.collect_data()

    def test_sensor_serialization(self):
        s = HumiditySensor("h1")
        s.is_active = False
        d = s.to_dict()
        restored = HumiditySensor.from_dict(d)
        assert restored.sensor_id == s.sensor_id
        assert restored.is_active is False

    @patch("random.uniform")
    def test_temperature_range(self, mock_uniform):
        mock_uniform.return_value = 20.0
        s = TemperatureSensor()
        assert s._read_value() == 20.0
        mock_uniform.assert_called_with(-50.0, 50.0)

    @patch("random.uniform")
    def test_light_range(self, mock_uniform):
        mock_uniform.return_value = 500.0
        s = LightSensor()
        assert s._read_value() == 500.0
        mock_uniform.assert_called_with(0.0, 10000.0)


# ==================== DATA ====================

class TestData:
    """Тесты структур данных."""

    def test_data_point_init(self):
        dp = DataPoint({"v": 1}, meta={"k": "v"})
        assert dp.get_value("v") == 1
        assert dp.metadata["k"] == "v"
        dp.set_value("new", 2)
        assert dp.get_value("new") == 2

    def test_data_point_empty_values(self):
        with pytest.raises(ValueError):
            DataPoint({})

    def test_data_point_serialization(self):
        dp = DataPoint({"x": 1})
        restored = DataPoint.from_dict(dp.to_dict())
        assert restored.point_id == dp.point_id
        assert restored.values == dp.values

    def test_dataset_operations(self):
        ds = DataSet("test")
        dp1 = DataPoint({"sensor_type": "temp", "value": 10})
        dp2 = DataPoint({"sensor_type": "hum", "value": 20})
        ds.add_data_point(dp1)
        ds.add_data_point(dp2)

        assert ds.size() == 2
        assert len(ds.get_data_points_by_type("temp")) == 1
        assert ds.get_latest_data(1)[0] == dp2

        ds.clear()
        assert ds.size() == 0

    def test_dataset_serialization(self):
        ds = DataSet("ds")
        ds.add_data_point(DataPoint({"v": 1}))
        restored = DataSet.from_dict(ds.to_dict())
        assert restored.name == ds.name
        assert restored.size() == 1


# ==================== FEEDBACK ====================

class TestFeedback:
    """Тесты обратной связи."""

    def test_feedback_init(self):
        f = Feedback(4.5, user_id="u1", comment="good")
        assert f.is_positive() is True
        assert f.is_negative() is False
        assert f.rating == 4.5

    def test_feedback_rating_bounds(self):
        with pytest.raises(ValueError):
            Feedback(0.5)
        with pytest.raises(ValueError):
            Feedback(6.0)

    def test_feedback_serialization(self):
        f = Feedback(2.0, comment="bad")
        restored = Feedback.from_dict(f.to_dict())
        assert restored.rating == f.rating

    def test_feedback_collector(self):
        fc = FeedbackCollector()
        fc.create_feedback(5.0)
        fc.create_feedback(1.0)
        assert fc.get_average_rating() == 3.0
        assert len(fc.get_positive_feedbacks()) == 1
        assert len(fc.get_negative_feedbacks()) == 1
        fc.clear()
        assert fc.size() == 0 if hasattr(fc, 'size') else len(fc.feedbacks) == 0


# ==================== ALGORITHMS ====================

class TestAlgorithms:
    """Тесты алгоритмов ML."""

    def test_algorithm_init(self):
        algo = SimpleThresholdAlgorithm("alg1", "val")
        assert algo.algorithm_id == "alg1"
        assert algo.is_trained is False

    def test_train_empty_dataset(self):
        algo = SimpleThresholdAlgorithm()
        ds = DataSet()
        algo.train(ds)
        assert algo.is_trained is False

    def test_train_and_predict(self):
        algo = SimpleThresholdAlgorithm(target_key="value")
        ds = DataSet()
        ds.add_data_point(DataPoint({"value": 10}))
        ds.add_data_point(DataPoint({"value": 20}))

        algo.train(ds)
        assert algo.is_trained is True
        assert algo.threshold == 15.0

        res = algo.predict({"value": 18})
        assert res["label"] == "high"
        res = algo.predict({"value": 12})
        assert res["label"] == "low"

    def test_algorithm_serialization(self):
        algo = SimpleThresholdAlgorithm()
        algo.threshold = 42.0
        algo.is_trained = True
        d = algo.to_dict()
        algo2 = SimpleThresholdAlgorithm()
        algo2.from_dict(d)
        assert algo2.threshold == 42.0
        assert algo2.is_trained is True


# ==================== DECISIONS ====================

class TestDecisions:
    """Тесты движка решений."""

    def test_make_decision_high(self):
        engine = DecisionEngine()
        res = engine.make_decision({"label": "high", "threshold": 10})
        assert res["action"] == "alert"
        assert "high" in res["reason"]

    def test_make_decision_low(self):
        engine = DecisionEngine()
        res = engine.make_decision({"label": "low"})
        assert res["action"] == "log"

    def test_make_decision_default(self):
        engine = DecisionEngine()
        res = engine.make_decision({})
        assert res["action"] == "monitor"


# ==================== STATE ====================

class TestState:
    """Тесты управления состоянием."""

    def test_state_config(self):
        st = SystemState()
        st.set_config("k", "v")
        assert st.get_config("k") == "v"
        assert st.get_config("missing", "default") == "default"

    def test_state_data(self):
        st = SystemState()
        st.set_data("algo", {"x": 1})
        assert st.get_data("algo")["x"] == 1

    def test_state_save_load(self, tmp_path):
        filepath = tmp_path / "state.json"
        st = SystemState()
        st.set_config("a", 1)
        st.set_data("b", 2)
        st.save(str(filepath))

        st2 = SystemState()
        assert st2.load(str(filepath)) is True
        assert st2.get_config("a") == 1
        assert st2.get_data("b") == 2

    def test_state_load_missing(self):
        st = SystemState()
        assert st.load("nonexistent.json") is False

    def test_state_save_error(self, tmp_path):
        st = SystemState()
        with patch("builtins.open", side_effect=IOError("Disk full")):
            with pytest.raises(StateException):
                st.save(str(tmp_path / "fail.json"))


# ==================== SYSTEM ====================

class TestSystem:
    """Тесты интеллектуальной системы."""

    def test_init(self):
        sys = IntelligentSystem("TestSys")
        assert sys.name == "TestSys"
        assert len(sys.sensors) == 0

    def test_load_and_initialize(self, tmp_path):
        filepath = tmp_path / "sys_state.json"
        # Сохраняем состояние заранее
        st = SystemState()
        st.set_data('algorithm_state', {'threshold': 99.0, 'is_trained': True})
        st.save(str(filepath))

        with patch.object(SystemState, 'load', return_value=True):
            with patch.object(SystemState, 'get_data', return_value={'threshold': 99.0, 'is_trained': True}):
                sys = IntelligentSystem()
                algo = SimpleThresholdAlgorithm()
                res = sys.load_and_initialize(algo)
                assert res is True
                assert algo.threshold == 99.0

    def test_add_sensor_and_collect(self):
        sys = IntelligentSystem()
        s = TemperatureSensor()
        sys.add_sensor(s)

        with patch.object(s, "_read_value", return_value=25.0):
            data = sys.collect_environment_data()
            assert "temperature" in data
            assert data["temperature"] == 25.0

    def test_collect_no_sensors(self):
        sys = IntelligentSystem()
        with pytest.raises(SensorException):
            sys.collect_environment_data()

    def test_train_system(self):
        sys = IntelligentSystem()
        algo = SimpleThresholdAlgorithm()
        sys.algorithm = algo
        sys.dataset.add_data_point(DataPoint({"value": 10}))
        sys.dataset.add_data_point(DataPoint({"value": 20}))

        res = sys.train_system()
        assert "успешно обучена" in res
        assert algo.is_trained is True

    def test_train_empty(self):
        sys = IntelligentSystem()
        sys.algorithm = SimpleThresholdAlgorithm()
        assert "Недостаточно данных" in sys.train_system()

    def test_adapt(self):
        sys = IntelligentSystem()
        sys.algorithm = SimpleThresholdAlgorithm()
        # Добавляем 5 точек
        for i in range(5):
            sys.dataset.add_data_point(DataPoint({"value": i}))
        res = sys.adapt_to_environment()
        assert "адаптировалась" in res

    def test_adapt_insufficient(self):
        sys = IntelligentSystem()
        sys.algorithm = SimpleThresholdAlgorithm()
        sys.dataset.add_data_point(DataPoint({"value": 1}))
        assert "Недостаточно свежих данных" in sys.adapt_to_environment()

    def test_make_decision(self):
        sys = IntelligentSystem()
        sys.algorithm = SimpleThresholdAlgorithm()
        sys.sensors.append(TemperatureSensor())

        with patch.object(sys.algorithm, "predict", return_value={"label": "high"}):
            with patch.object(sys.sensors[0], "_read_value", return_value=20.0):
                res = sys.make_decision()
                assert res["action"] == "alert"

    def test_make_decision_error(self):
        sys = IntelligentSystem()
        sys.algorithm = SimpleThresholdAlgorithm()
        sys.sensors = []  # Вызовет ошибку при collect
        res = sys.make_decision()
        assert res["action"] == "error"

    def test_status_report(self):
        sys = IntelligentSystem("RepSys")
        sys.algorithm = SimpleThresholdAlgorithm()
        sys.algorithm.threshold = 50.0
        sys.algorithm.is_trained = True
        sys.dataset.add_data_point(DataPoint({"v": 1}))

        report = sys.get_status_report()
        assert "RepSys" in report
        assert "50.0" in report
        assert "Да" in report


# ==================== CLI ====================

class TestCLI:
    """Тесты CLI интерфейса (мокаем ввод/вывод)."""

    @patch("builtins.input", side_effect=["7", "0"])  # Status -> Exit
    @patch("builtins.print")
    def test_cli_menu_navigation(self, mock_print, mock_input):
        sys = IntelligentSystem()
        sys.algorithm = SimpleThresholdAlgorithm()
        sys.sensors.append(TemperatureSensor())
        cli = IntelligentSystemCLI(sys)

        # Патчим start, чтобы не застрять в цикле, тестируем обработчики напрямую
        # Но для покрытия цикла вызовем start с быстрым выходом
        with patch.object(sys, "load_state", return_value=False):
            with patch.object(sys, "save_state"):
                try:
                    cli.start()
                except SystemExit:
                    pass

        # Проверяем, что print вызывался для меню и статуса
        printed = "\n".join([str(c) for c in mock_print.call_args_list])
        assert "Меню" in printed or "Посмотреть состояние" in printed

    def test_cli_cmd_collect(self, capsys):
        sys = IntelligentSystem()
        sys.sensors.append(TemperatureSensor())
        cli = IntelligentSystemCLI(sys)

        with patch.object(sys.sensors[0], "_read_value", return_value=22.0):
            cli._cmd_collect()
            captured = capsys.readouterr()
            assert "temperature: 22.0" in captured.out

    def test_cli_cmd_train(self, capsys):
        sys = IntelligentSystem()
        sys.algorithm = SimpleThresholdAlgorithm()
        cli = IntelligentSystemCLI(sys)
        cli._cmd_train()
        captured = capsys.readouterr()
        assert "Недостаточно данных" in captured.out

    def test_cli_cmd_feedback_invalid(self, capsys):
        sys = IntelligentSystem()
        sys.algorithm = SimpleThresholdAlgorithm()
        cli = IntelligentSystemCLI(sys)

        with patch("builtins.input", side_effect=["abc", "5", "0"]):
            cli._cmd_feedback()
            captured = capsys.readouterr()
            assert "Ошибка: Рейтинг должен быть числом" in captured.out