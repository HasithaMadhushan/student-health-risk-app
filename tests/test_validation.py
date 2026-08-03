import math

import numpy as np
import pytest

from src.config import AppPaths
from src.schema import load_schema
from src.validation import InputValidationError, prepare_record


@pytest.fixture()
def schema():
    paths = AppPaths.from_environment()
    return load_schema(paths.inference_schema_path, paths.feature_schema_path)


@pytest.fixture()
def valid_payload():
    return {
        "sleep_duration": 7.0,
        "heart_rate": 72.0,
        "bmi": 23.0,
        "calorie_expenditure": 2200.0,
        "step_count": 8000.0,
        "exercise_duration": 35.0,
        "water_intake": 2.0,
        "diet_type": "balanced",
        "stress_level": "medium",
        "sleep_quality": "average",
        "physical_activity_level": "moderate",
        "smoking_alcohol": "no",
    }


def test_prepare_record_preserves_exact_order(schema, valid_payload):
    frame = prepare_record(valid_payload, schema)
    assert tuple(frame.columns) == schema.feature_order
    assert frame.shape == (1, 12)


def test_prepare_record_maps_missing_values(schema, valid_payload):
    payload = dict(valid_payload)
    payload["sleep_duration"] = None
    payload["diet_type"] = None
    frame = prepare_record(payload, schema)
    assert np.isnan(frame.at[0, "sleep_duration"])
    assert frame.at[0, "diet_type"] == "__MISSING__"


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("sleep_duration", math.inf, "finite"),
        ("sleep_duration", True, "numeric"),
        ("sleep_duration", 2.9, "observed range"),
        ("diet_type", "unknown", "allowed category"),
    ],
)
def test_prepare_record_rejects_invalid_values(
    schema, valid_payload, field, value, message
):
    payload = dict(valid_payload)
    payload[field] = value
    with pytest.raises(InputValidationError, match=message):
        prepare_record(payload, schema)


def test_prepare_record_rejects_missing_and_unexpected_keys(schema, valid_payload):
    missing = dict(valid_payload)
    missing.pop("bmi")
    with pytest.raises(InputValidationError, match="Missing input"):
        prepare_record(missing, schema)
    unexpected = dict(valid_payload, student_id="123")
    with pytest.raises(InputValidationError, match="Unexpected input"):
        prepare_record(unexpected, schema)
