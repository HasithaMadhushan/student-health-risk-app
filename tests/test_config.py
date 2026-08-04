from pathlib import Path

from src.config import (
    DISCLAIMER,
    EXPECTED_MODEL_SHA256,
    EXPECTED_SCHEMA_VERSION,
    AppPaths,
)


def test_default_paths_are_project_relative():
    paths = AppPaths.from_environment()
    assert paths.project_root == Path(__file__).resolve().parents[1]
    assert paths.model_path.name == (
        "catboost_balanced_no_gender_production_all_train_v1.cbm"
    )
    assert paths.inference_schema_path.name == "production_inference_schema.json"
    assert paths.feature_schema_path.name == "feature-schema.json"


def test_locked_constants_match_production_contract():
    assert EXPECTED_SCHEMA_VERSION == "1.0.0"
    assert EXPECTED_MODEL_SHA256 == (
        "ea5f6ea9b060720d063874f9ee6ab0aae7ed8367e94c1222ffe2608dbe990004"
    )
    assert DISCLAIMER.startswith(
        "Educational and research risk-screening demonstrator only."
    )


def test_streamlit_cloud_runtime_is_reproducibly_pinned():
    requirements = (
        Path(__file__).resolve().parents[1] / "requirements.txt"
    ).read_text(encoding="utf-8").splitlines()

    assert "streamlit==1.60.0" in requirements
