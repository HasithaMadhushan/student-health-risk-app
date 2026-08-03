from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Literal, Mapping

from src.config import EXPECTED_SCHEMA_VERSION

LOCKED_FEATURE_ORDER = (
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
LOCKED_CLASS_ORDER = ("at-risk", "fit", "unhealthy")


class SchemaError(ValueError):
    pass


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    kind: Literal["numeric", "categorical"]
    nullable: bool
    minimum: float | None = None
    maximum: float | None = None
    categories: tuple[str, ...] = ()


@dataclass(frozen=True)
class InferenceSchema:
    schema_version: str
    experiment_id: str
    model_sha256: str
    feature_order: tuple[str, ...]
    class_labels: tuple[str, ...]
    missing_category_token: str
    disclaimer: str
    features: Mapping[str, FeatureSpec]


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SchemaError(f"Unable to read schema: {path.name}") from exc


def load_schema(inference_path: Path, feature_path: Path) -> InferenceSchema:
    inference = _read_json(inference_path)
    feature = _read_json(feature_path)
    if feature.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        raise SchemaError("Unsupported schema version")
    order = tuple(inference.get("features_in_training_order", ()))
    if order != LOCKED_FEATURE_ORDER:
        raise SchemaError("Production feature order does not match the locked contract")
    classes = tuple(inference.get("class_labels_in_model_code_order", ()))
    if classes != LOCKED_CLASS_ORDER:
        raise SchemaError("Production class order does not match the locked contract")
    columns = {item["name"]: item for item in feature.get("columns", ())}
    numeric = set(inference.get("numeric_features", ()))
    categorical = set(inference.get("categorical_features", ()))
    specs: dict[str, FeatureSpec] = {}
    for name in order:
        meta = columns.get(name)
        if meta is None:
            raise SchemaError(f"Feature metadata missing for {name}")
        if name in numeric:
            specs[name] = FeatureSpec(
                name=name,
                kind="numeric",
                nullable=bool(meta["nullable_in_train"]),
                minimum=float(meta["observed_train_min"]),
                maximum=float(meta["observed_train_max"]),
            )
        elif name in categorical:
            specs[name] = FeatureSpec(
                name=name,
                kind="categorical",
                nullable=bool(meta["nullable_in_train"]),
                categories=tuple(meta["observed_train_categories"]),
            )
        else:
            raise SchemaError(f"Feature type missing for {name}")
    return InferenceSchema(
        schema_version=feature["schema_version"],
        experiment_id=inference["production_experiment_id"],
        model_sha256=inference["production_model_sha256"],
        feature_order=order,
        class_labels=classes,
        missing_category_token=inference["categorical_missing_token"],
        disclaimer=inference["medical_disclaimer_required"],
        features=MappingProxyType(specs),
    )
