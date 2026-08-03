from src.config import AppPaths
from src.schema import load_schema

from app.presentation import (
    GUIDED_STEPS,
    build_payload,
    format_category,
    format_review_value,
    human_label,
)


def test_guided_steps_cover_each_locked_feature_once():
    paths = AppPaths.from_environment()
    schema = load_schema(paths.inference_schema_path, paths.feature_schema_path)
    grouped = tuple(
        feature for step in GUIDED_STEPS for feature in step.features
    )
    assert len(grouped) == len(set(grouped)) == 12
    assert set(grouped) == set(schema.feature_order)
    assert tuple(step.title for step in GUIDED_STEPS) == (
        "Sleep and body",
        "Activity and daily habits",
        "Lifestyle and wellbeing",
    )


def test_build_payload_restores_locked_order_and_preserves_missing_values():
    paths = AppPaths.from_environment()
    schema = load_schema(paths.inference_schema_path, paths.feature_schema_path)
    reversed_values = {
        name: None if name == "sleep_duration" else index
        for index, name in enumerate(reversed(schema.feature_order))
    }
    payload = build_payload(reversed_values, schema)
    assert tuple(payload) == schema.feature_order
    assert payload["sleep_duration"] is None


def test_review_formatting_is_friendly_without_changing_model_values():
    assert format_review_value(None) == "I don't know"
    assert format_category("non-veg") == "Non-veg"
    assert format_category("very_high") == "Very high"
    assert human_label("bmi") == "BMI"
    assert human_label("smoking_alcohol") == "Smoking and alcohol"
