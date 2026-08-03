from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

EXPECTED_MODEL_SHA256 = (
    "ea5f6ea9b060720d063874f9ee6ab0aae7ed8367e94c1222ffe2608dbe990004"
)
EXPECTED_SCHEMA_VERSION = "1.0.0"
DISCLAIMER = (
    "Educational and research risk-screening demonstrator only. "
    "This output is not a medical diagnosis and must not replace advice "
    "from a qualified healthcare professional."
)


@dataclass(frozen=True)
class AppPaths:
    project_root: Path
    model_path: Path
    inference_schema_path: Path
    feature_schema_path: Path
    training_record_path: Path

    @classmethod
    def from_environment(cls) -> "AppPaths":
        root = Path(__file__).resolve().parents[1]
        private = root / "artifacts" / "private"
        return cls(
            project_root=root,
            model_path=Path(
                os.getenv(
                    "CIS6005_MODEL_PATH",
                    private
                    / "models"
                    / "catboost_balanced_no_gender_production_all_train_v1.cbm",
                )
            ),
            inference_schema_path=Path(
                os.getenv(
                    "CIS6005_INFERENCE_SCHEMA_PATH",
                    private / "schema" / "production_inference_schema.json",
                )
            ),
            feature_schema_path=Path(
                os.getenv(
                    "CIS6005_FEATURE_SCHEMA_PATH",
                    private / "schema" / "feature-schema.json",
                )
            ),
            training_record_path=Path(
                os.getenv(
                    "CIS6005_TRAINING_RECORD_PATH",
                    private / "metadata" / "production_training_record.json",
                )
            ),
        )
