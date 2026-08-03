from __future__ import annotations

import ast
import json
import math
import textwrap
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from app.presentation import build_payload, format_review_value
from src.inference import CatBoostPredictor, PredictionResult
from src.schema import InferenceSchema
from src.validation import prepare_record


class DemonstrationError(RuntimeError):
    pass


@dataclass(frozen=True)
class RuntimeMetadata:
    tree_count: int
    training_rows: int
    model_size_bytes: int


@dataclass(frozen=True)
class TraceRow:
    feature: str
    input_value: str
    prepared_value: str


@dataclass(frozen=True)
class InvocationTrace:
    rows: tuple[TraceRow, ...]
    shape: tuple[int, int]
    columns: tuple[str, ...]
    experiment_id: str
    model_sha256: str
    predicted_category: str
    confidence_scores: Mapping[str, float]


@dataclass(frozen=True)
class FunctionFlowItem:
    function: str
    file: str
    responsibility: str


@dataclass(frozen=True)
class LibraryRole:
    library: str
    responsibility: str


FUNCTION_FLOW = (
    FunctionFlowItem(
        "render_app()",
        "app/streamlit_app.py",
        "Hosts the application, loads the runtime and selects the visible mode.",
    ),
    FunctionFlowItem(
        "load_runtime()",
        "app/streamlit_app.py",
        "Loads the locked schemas and hash-verified production model once.",
    ),
    FunctionFlowItem(
        "AppPaths.from_environment()",
        "src/config.py",
        "Resolves private artefact paths without embedding credentials.",
    ),
    FunctionFlowItem(
        "load_schema()",
        "src/schema.py",
        "Rejects changed feature order, class order or schema version.",
    ),
    FunctionFlowItem(
        "CatBoostPredictor.load()",
        "src/inference.py",
        "Checks the complete model SHA-256 before deserialising CatBoost.",
    ),
    FunctionFlowItem(
        "guided input renderers",
        "app/streamlit_app.py",
        "Collect the 12 schema-driven values without identifying information.",
    ),
    FunctionFlowItem(
        "build_payload()",
        "app/presentation.py",
        "Reconstructs the mapping in the exact saved training order.",
    ),
    FunctionFlowItem(
        "CatBoostPredictor.predict()",
        "src/inference.py",
        "Coordinates record preparation and invokes the production classifier.",
    ),
    FunctionFlowItem(
        "prepare_record()",
        "src/validation.py",
        "Validates values and creates the ordered one-row pandas DataFrame.",
    ),
    FunctionFlowItem(
        "CatBoost predict_proba() and predict()",
        "src/inference.py",
        "Returns the three confidence scores and predicted competition class.",
    ),
    FunctionFlowItem(
        "render_result()",
        "app/streamlit_app.py",
        "Presents the class, optional scores and permanent disclaimer.",
    ),
)


LIBRARY_ROLES = (
    LibraryRole(
        "Streamlit",
        "Renders the web interface, widgets, session state, cached runtime "
        "and user feedback.",
    ),
    LibraryRole(
        "CatBoost",
        "Loads the verified .cbm artefact and performs predict() and "
        "predict_proba() inference.",
    ),
    LibraryRole(
        "pandas",
        "Constructs the exact ordered one-row DataFrame expected by the model.",
    ),
    LibraryRole(
        "NumPy",
        "Represents numeric missing values and normalises CatBoost outputs "
        "for ordered mapping.",
    ),
    LibraryRole(
        "hashlib",
        "Calculates the model SHA-256 before model deserialisation.",
    ),
    LibraryRole(
        "pytest and Streamlit AppTest",
        "Repeat the contract, inference, privacy and user-interface checks.",
    ),
)


def _prepared_display(value: object) -> str:
    if isinstance(value, float) and math.isnan(value):
        return "NaN"
    return str(value)


def build_invocation_trace(
    values: Mapping[str, object],
    schema: InferenceSchema,
    result: PredictionResult,
) -> InvocationTrace:
    payload = build_payload(values, schema)
    frame = prepare_record(payload, schema)
    rows = tuple(
        TraceRow(
            feature=name,
            input_value=format_review_value(payload[name]),
            prepared_value=_prepared_display(frame.at[0, name]),
        )
        for name in schema.feature_order
    )
    return InvocationTrace(
        rows=rows,
        shape=frame.shape,
        columns=tuple(frame.columns),
        experiment_id=result.experiment_id,
        model_sha256=result.model_sha256,
        predicted_category=result.label,
        confidence_scores=MappingProxyType(dict(result.confidence_scores)),
    )


def load_runtime_metadata(
    path: Path,
    schema: InferenceSchema,
    predictor: CatBoostPredictor,
) -> RuntimeMetadata:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload["model_sha256"] != predictor.model_sha256:
            raise ValueError
        if payload["production_experiment_id"] != schema.experiment_id:
            raise ValueError
        if tuple(payload["features_in_order"]) != schema.feature_order:
            raise ValueError
        if tuple(payload["class_labels_in_code_order"]) != schema.class_labels:
            raise ValueError
        tree_count = int(payload["tree_count"])
        training_rows = int(payload["training_rows"])
        model_size_bytes = int(payload["model_size_bytes"])
        if min(tree_count, training_rows, model_size_bytes) <= 0:
            raise ValueError
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise DemonstrationError(
            "Verified training metadata is unavailable or inconsistent"
        ) from exc
    return RuntimeMetadata(
        tree_count=tree_count,
        training_rows=training_rows,
        model_size_bytes=model_size_bytes,
    )


def _find_source_node(
    tree: ast.Module,
    dotted_name: str,
) -> ast.FunctionDef | ast.AsyncFunctionDef:
    parts = dotted_name.split(".")
    if len(parts) == 1:
        candidates = (
            node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        )
        for node in candidates:
            if node.name == parts[0]:
                return node
    elif len(parts) == 2:
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == parts[0]:
                for member in node.body:
                    if isinstance(
                        member,
                        (ast.FunctionDef, ast.AsyncFunctionDef),
                    ) and member.name == parts[1]:
                        return member
    raise DemonstrationError("Requested application code segment was not found")


def extract_function_source(
    project_root: Path,
    relative_path: str,
    dotted_name: str,
) -> str:
    root = project_root.resolve()
    target = (root / relative_path).resolve()
    if not target.is_relative_to(root):
        raise DemonstrationError("Source path is outside the application project")
    try:
        source = target.read_text(encoding="utf-8")
        tree = ast.parse(source)
        node = _find_source_node(tree, dotted_name)
        start = min(
            (decorator.lineno for decorator in node.decorator_list),
            default=node.lineno,
        )
        end = node.end_lineno
        if end is None:
            raise DemonstrationError(
                "Requested application code segment has no source span"
            )
    except (OSError, SyntaxError) as exc:
        raise DemonstrationError(
            "Requested application source could not be inspected"
        ) from exc
    return textwrap.dedent("\n".join(source.splitlines()[start - 1 : end]))
