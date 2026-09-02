"""Tests for electronic-fence voice alarm edge detection."""

from beidou_gazebo.elderly_voice_alarm import GeofenceExitDetector
from beidou_gazebo.piper_chinese_tts import dependency_errors


def test_safe_to_out_of_bounds_triggers_once():
    detector = GeofenceExitDetector()
    assert detector.update(True) is False
    assert detector.update(False) is True
    assert detector.update(False) is False
    assert detector.update(False) is False


def test_return_to_safe_rearms_alarm():
    detector = GeofenceExitDetector()
    assert detector.update(True) is False
    assert detector.update(False) is True
    assert detector.update(True) is False
    assert detector.update(False) is True


def test_initial_out_of_bounds_does_not_trigger_without_safe_baseline():
    detector = GeofenceExitDetector()
    assert detector.update(False) is False
    assert detector.update(False) is False


def test_safe_updates_do_not_trigger():
    detector = GeofenceExitDetector()
    assert detector.update(True) is False
    assert detector.update(True) is False


def test_piper_dependencies_are_reported(tmp_path):
    errors = dependency_errors(
        str(tmp_path / 'missing-piper'),
        str(tmp_path / 'missing-model.onnx'),
        str(tmp_path / 'missing-aplay'),
    )
    assert len(errors) == 4
    assert 'Piper executable not found' in errors[0]
    assert 'Piper Chinese model not found' in errors[1]
    assert 'Piper model config not found' in errors[2]
    assert 'Audio player not found' in errors[3]
