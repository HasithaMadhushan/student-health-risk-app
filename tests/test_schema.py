import json

import pytest

from src.config import AppPaths
from src.schema import SchemaError, load_schema

EXPECTED_FEATURES = (
    "sleep_duration",
    "heart_rate",
    "bmi",
    "calorie_expenditure",
    "step_count",
    "exercise_duration",
    "water_intake",
    "diet_type",
    "stress_level",
    "sleep_quality",
    "physical_activity_level",
    "smoking_alcohol",
)


def test_schema_loads_locked_feature_and_class_contract():
    paths = AppPaths.from_environment()
    schema = load_schema(paths.inference_schema_path, paths.feature_schema_path)
    assert schema.feature_order == EXPECTED_FEATURES
    assert schema.class_labels == ("at-risk", "fit", "unhealthy")
    assert schema.missing_category_token == "__MISSING__"
    assert "gender" not in schema.feature_order
    assert "id" not in schema.feature_order


def test_schema_preserves_verified_ranges_and_categories():
    paths = AppPaths.from_environment()
    schema = load_schema(paths.inference_schema_path, paths.feature_schema_path)
    assert schema.features["sleep_duration"].minimum == 3.0
    assert schema.features["sleep_duration"].maximum == 10.0
    assert schema.features["diet_type"].categories == (
        "veg",
        "non-veg",
        "balanced",
    )


def test_schema_rejects_reordered_production_features(tmp_path):
    paths = AppPaths.from_environment()
    payload = json.loads(paths.inference_schema_path.read_text(encoding="utf-8"))
    payload["features_in_training_order"] = list(
        reversed(payload["features_in_training_order"])
    )
    altered = tmp_path / "altered.json"
    altered.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(SchemaError, match="feature order"):
        load_schema(altered, paths.feature_schema_path)
