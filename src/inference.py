from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

import numpy as np
from catboost import CatBoostClassifier

from src.schema import InferenceSchema
from src.validation import prepare_record


class ArtifactError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    if not path.is_file():
        raise ArtifactError(f"Model artefact is unavailable: {path.name}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class PredictionResult:
    label: str
    confidence_scores: Mapping[str, float]
    experiment_id: str
    model_sha256: str


class CatBoostPredictor:
    def __init__(
        self,
        model: CatBoostClassifier,
        schema: InferenceSchema,
        model_sha256: str,
    ) -> None:
        self._model = model
        self.schema = schema
        self.model_sha256 = model_sha256

    @classmethod
    def load(
        cls, model_path: Path, schema: InferenceSchema
    ) -> "CatBoostPredictor":
        actual = sha256_file(model_path)
        if actual != schema.model_sha256:
            raise ArtifactError("Model artefact integrity check failed")
        model = CatBoostClassifier()
        try:
            model.load_model(str(model_path))
        except Exception as exc:
            raise ArtifactError("Unable to load the CatBoost model artefact") from exc
        return cls(model, schema, actual)

    def predict(self, payload: Mapping[str, object]) -> PredictionResult:
        frame = prepare_record(payload, self.schema)
        try:
            scores = np.asarray(self._model.predict_proba(frame))[0]
            prediction = self._model.predict(frame)
        except Exception as exc:
            raise ArtifactError("Model inference failed") from exc
        raw_label = np.asarray(prediction).reshape(-1)[0]
        label = str(raw_label)
        if label not in self.schema.class_labels:
            label = self.schema.class_labels[int(raw_label)]
        ordered = MappingProxyType(
            {
                class_label: float(score)
                for class_label, score in zip(self.schema.class_labels, scores)
            }
        )
        return PredictionResult(
            label=label,
            confidence_scores=ordered,
            experiment_id=self.schema.experiment_id,
            model_sha256=self.model_sha256,
        )
