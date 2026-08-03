from __future__ import annotations

import math
from collections.abc import Mapping

import numpy as np
import pandas as pd

from src.schema import InferenceSchema


class InputValidationError(ValueError):
    pass


def prepare_record(
    payload: Mapping[str, object], schema: InferenceSchema
) -> pd.DataFrame:
    keys = set(payload)
    expected = set(schema.feature_order)
    missing = expected - keys
    unexpected = keys - expected
    if missing:
        raise InputValidationError(f"Missing input fields: {sorted(missing)}")
    if unexpected:
        raise InputValidationError(f"Unexpected input fields: {sorted(unexpected)}")
    row: dict[str, object] = {}
    for name in schema.feature_order:
        spec = schema.features[name]
        value = payload[name]
        if value is None:
            row[name] = (
                np.nan if spec.kind == "numeric" else schema.missing_category_token
            )
            continue
        if spec.kind == "numeric":
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise InputValidationError(f"{name} must be numeric")
            numeric = float(value)
            if not math.isfinite(numeric):
                raise InputValidationError(f"{name} must be finite")
            if numeric < spec.minimum or numeric > spec.maximum:
                raise InputValidationError(
                    f"{name} must be within the observed range "
                    f"{spec.minimum} to {spec.maximum}"
                )
            row[name] = numeric
        else:
            if not isinstance(value, str) or value not in spec.categories:
                raise InputValidationError(
                    f"{name} must be an allowed category: {spec.categories}"
                )
            row[name] = value
    return pd.DataFrame([row], columns=schema.feature_order)
