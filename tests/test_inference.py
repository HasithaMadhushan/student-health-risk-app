import shutil

import numpy as np
import pytest
from catboost import CatBoostClassifier

from src.config import AppPaths, EXPECTED_MODEL_SHA256
from src.inference import ArtifactError, CatBoostPredictor, sha256_file
from src.schema import load_schema
from src.validation import prepare_record


@pytest.fixture()
def paths():
    return AppPaths.from_environment()


@pytest.fixture()
def schema(paths):
    return load_schema(paths.inference_schema_path, paths.feature_schema_path)


@pytest.fixture()
def payload():
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


def test_verified_model_hash(paths):
    assert sha256_file(paths.model_path) == EXPECTED_MODEL_SHA256


def test_hash_mismatch_fails_closed(paths, schema, tmp_path):
    altered = tmp_path / "altered.cbm"
    shutil.copyfile(paths.model_path, altered)
    altered.write_bytes(altered.read_bytes() + b"x")
    with pytest.raises(ArtifactError, match="integrity"):
        CatBoostPredictor.load(altered, schema)


def test_prediction_is_ordered_and_deterministic(paths, schema, payload):
    predictor = CatBoostPredictor.load(paths.model_path, schema)
    first = predictor.predict(payload)
    second = predictor.predict(payload)
    assert first == second
    assert first.label in schema.class_labels
    assert tuple(first.confidence_scores) == schema.class_labels
    assert sum(first.confidence_scores.values()) == pytest.approx(1.0)


def test_predictor_matches_direct_catboost_call(paths, schema, payload):
    predictor = CatBoostPredictor.load(paths.model_path, schema)
    result = predictor.predict(payload)
    direct = CatBoostClassifier()
    direct.load_model(str(paths.model_path))
    frame = prepare_record(payload, schema)
    direct_scores = np.asarray(direct.predict_proba(frame))[0]
    assert list(result.confidence_scores.values()) == pytest.approx(direct_scores)
