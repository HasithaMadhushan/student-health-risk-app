from pathlib import Path

import pytest

from app.demonstration import (
    FUNCTION_FLOW,
    DemonstrationError,
    build_invocation_trace,
    extract_function_source,
    load_runtime_metadata,
)
from src.config import AppPaths
from src.inference import CatBoostPredictor
from src.schema import load_schema


@pytest.fixture()
def runtime():
    paths = AppPaths.from_environment()
    schema = load_schema(
        paths.inference_schema_path,
        paths.feature_schema_path,
    )
    predictor = CatBoostPredictor.load(paths.model_path, schema)
    return paths, schema, predictor


@pytest.fixture()
def demonstration_values():
    return {
        "sleep_duration": None,
        "heart_rate": 72.0,
        "bmi": 23.0,
        "calorie_expenditure": 2200.0,
        "step_count": 8000.0,
        "exercise_duration": 35.0,
        "water_intake": 2.0,
        "diet_type": None,
        "stress_level": "medium",
        "sleep_quality": "average",
        "physical_activity_level": "moderate",
        "smoking_alcohol": "no",
    }


def test_trace_uses_locked_order_and_actual_missing_transformations(
    runtime,
    demonstration_values,
):
    _, schema, predictor = runtime
    result = predictor.predict(demonstration_values)
    trace = build_invocation_trace(
        demonstration_values,
        schema,
        result,
    )

    assert trace.shape == (1, 12)
    assert trace.columns == schema.feature_order
    assert tuple(row.feature for row in trace.rows) == schema.feature_order
    assert trace.rows[0].input_value == "I don't know"
    assert trace.rows[0].prepared_value == "NaN"
    assert trace.rows[7].input_value == "I don't know"
    assert trace.rows[7].prepared_value == "__MISSING__"
    assert trace.predicted_category == result.label
    assert tuple(trace.confidence_scores) == schema.class_labels


def test_trace_construction_does_not_create_files(
    runtime,
    demonstration_values,
    tmp_path,
    monkeypatch,
):
    _, schema, predictor = runtime
    result = predictor.predict(demonstration_values)
    monkeypatch.chdir(tmp_path)
    before = set(Path(".").rglob("*"))
    build_invocation_trace(demonstration_values, schema, result)
    after = set(Path(".").rglob("*"))
    assert after == before


def test_training_metadata_must_match_loaded_runtime(runtime):
    paths, schema, predictor = runtime
    metadata = load_runtime_metadata(
        paths.training_record_path,
        schema,
        predictor,
    )
    assert metadata.tree_count == 343
    assert metadata.training_rows == 690088
    assert metadata.model_size_bytes == 815904


def test_mismatched_training_metadata_fails_closed(runtime, tmp_path):
    _, schema, predictor = runtime
    altered = tmp_path / "record.json"
    altered.write_text('{"model_sha256": "wrong"}', encoding="utf-8")
    with pytest.raises(DemonstrationError, match="metadata"):
        load_runtime_metadata(altered, schema, predictor)


def test_source_extraction_returns_only_named_function(runtime):
    paths, _, _ = runtime
    source = extract_function_source(
        paths.project_root,
        "src/inference.py",
        "CatBoostPredictor.predict",
    )
    assert source.lstrip().startswith("def predict(")
    assert "predict_proba" in source
    assert "def sha256_file" not in source


def test_source_extraction_rejects_paths_outside_project(runtime, tmp_path):
    paths, _, _ = runtime
    outside = tmp_path / "outside.py"
    outside.write_text("def example():\n    return 1\n", encoding="utf-8")
    with pytest.raises(DemonstrationError, match="project"):
        extract_function_source(
            paths.project_root,
            str(outside),
            "example",
        )


def test_function_flow_places_validation_before_catboost_inference():
    names = tuple(item.function for item in FUNCTION_FLOW)
    assert names.index("prepare_record()") < names.index(
        "CatBoost predict_proba() and predict()"
    )
