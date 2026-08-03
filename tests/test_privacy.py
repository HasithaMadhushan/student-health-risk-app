from pathlib import Path

from src.config import AppPaths
from src.inference import CatBoostPredictor
from src.schema import load_schema


def test_prediction_does_not_create_files(tmp_path, monkeypatch):
    paths = AppPaths.from_environment()
    schema = load_schema(paths.inference_schema_path, paths.feature_schema_path)
    predictor = CatBoostPredictor.load(paths.model_path, schema)
    payload = {
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
    monkeypatch.chdir(tmp_path)
    before = set(Path(".").rglob("*"))
    predictor.predict(payload)
    after = set(Path(".").rglob("*"))
    assert after == before
