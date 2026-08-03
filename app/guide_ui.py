from __future__ import annotations

from collections.abc import Mapping

import pandas as pd
import streamlit as st

from app.demonstration import (
    FUNCTION_FLOW,
    LIBRARY_ROLES,
    DemonstrationError,
    build_invocation_trace,
    extract_function_source,
    load_runtime_metadata,
)
from app.presentation import format_category, human_label
from src.config import AppPaths
from src.inference import CatBoostPredictor, PredictionResult
from src.schema import InferenceSchema


SOURCE_SEGMENTS = (
    ("Application host: render_app()", "app/streamlit_app.py", "render_app"),
    ("Runtime loader: load_runtime()", "app/streamlit_app.py", "load_runtime"),
    (
        "Prediction coordinator: CatBoostPredictor.predict()",
        "src/inference.py",
        "CatBoostPredictor.predict",
    ),
    ("Input processor: prepare_record()", "src/validation.py", "prepare_record"),
    ("Output presenter: render_result()", "app/streamlit_app.py", "render_result"),
)


def _section_heading(number: int, title: str) -> None:
    st.markdown(f"## {number}. {title}")


def _render_setup(paths: AppPaths) -> None:
    with st.container(border=True):
        _section_heading(1, "Setup and application host")
        st.write(
            "The application runs locally and performs predictions without "
            "an active Colab session."
        )
        st.markdown("**Launch command**")
        st.code(
            "streamlit run app/streamlit_app.py",
            language="powershell",
        )
        st.markdown(
            "**Application host:** `app/streamlit_app.py` → `render_app()`"
        )
        st.caption(
            "The host loads the verified runtime, maintains the current "
            "session and selects either the prediction journey or this guide."
        )


def _render_runtime(
    paths: AppPaths,
    schema: InferenceSchema,
    predictor: CatBoostPredictor,
) -> None:
    with st.container(border=True):
        _section_heading(2, "Verified runtime")
        try:
            metadata = load_runtime_metadata(
                paths.training_record_path,
                schema,
                predictor,
            )
        except DemonstrationError as exc:
            st.warning(f"Runtime metadata could not be verified: {exc}")
            return

        st.success("The loaded model and saved training record match.")
        first, second, third = st.columns(3)
        first.metric("Training records", f"{metadata.training_rows:,}")
        second.metric("CatBoost trees", f"{metadata.tree_count:,}")
        third.metric("Model size", f"{metadata.model_size_bytes / 1024:.1f} KiB")
        st.markdown(f"**Experiment ID:** `{schema.experiment_id}`")
        st.markdown(f"**Schema version:** `{schema.schema_version}`")
        st.markdown(f"**Features:** {len(schema.feature_order)} in locked order")
        st.markdown(
            "**Ordered classes:** "
            + " → ".join(format_category(label) for label in schema.class_labels)
        )
        st.markdown("**Complete model SHA-256**")
        st.code(predictor.model_sha256)


def _render_function_flow(paths: AppPaths) -> None:
    with st.container(border=True):
        _section_heading(3, "Function invocation flow")
        st.write(
            "A prediction follows these calls in order. Each function has "
            "one clear responsibility."
        )
        for index, item in enumerate(FUNCTION_FLOW, start=1):
            st.markdown(
                f"**{index}. `{item.function}`** — {item.responsibility}  \n"
                f"`{item.file}`"
            )

        with st.expander("Show exact code segments", expanded=False):
            for title, relative_path, dotted_name in SOURCE_SEGMENTS:
                st.markdown(f"### {title}")
                st.caption(relative_path)
                try:
                    source = extract_function_source(
                        paths.project_root,
                        relative_path,
                        dotted_name,
                    )
                except DemonstrationError as exc:
                    st.warning(f"This code segment is unavailable: {exc}")
                else:
                    st.code(source, language="python")


def _render_trace(
    schema: InferenceSchema,
    values: Mapping[str, object],
    result: PredictionResult | None,
) -> None:
    with st.container(border=True):
        _section_heading(4, "Live invocation trace")
        if result is None:
            st.markdown(
                "**Run a prediction in Use the model** to create a live "
                "current-session trace."
            )
            st.info(
                "Run a prediction in Use the model, then return here to see "
                "the current session move through the verified pipeline."
            )
            return

        try:
            trace = build_invocation_trace(values, schema, result)
        except DemonstrationError as exc:
            st.warning(f"The current-session trace is unavailable: {exc}")
            return

        st.markdown(
            f"**{len(trace.rows)} inputs received**  \n"
            f"**Prepared record: {trace.shape[0]} × {trace.shape[1]}**"
        )
        first, second = st.columns(2)
        first.metric("Input contract", f"{len(trace.rows)} inputs received")
        second.metric(
            "Model-ready shape",
            f"Prepared record: {trace.shape[0]} × {trace.shape[1]}",
        )
        rows = pd.DataFrame(
            (
                {
                    "Feature": human_label(row.feature),
                    "Input value": row.input_value,
                    "Prepared model value": (
                        f"`{row.prepared_value}`"
                        if row.prepared_value == "__MISSING__"
                        else row.prepared_value
                    ),
                }
                for row in trace.rows
            )
        )
        st.table(rows)
        st.markdown("**Exact ordered model columns**")
        st.code(" → ".join(trace.columns))
        st.markdown(f"**Experiment ID:** `{trace.experiment_id}`")
        st.markdown(f"**Model SHA-256:** `{trace.model_sha256}`")
        st.markdown(
            f"### Output: {format_category(trace.predicted_category)}"
        )
        for label, score in trace.confidence_scores.items():
            st.progress(
                score,
                text=f"{format_category(label)} confidence: {score:.1%}",
            )
        st.caption(
            "This trace is reconstructed from the current in-memory session. "
            "It is not written to a file, database or application log."
        )


def _render_libraries() -> None:
    with st.container(border=True):
        _section_heading(5, "Library responsibilities")
        st.write(
            "The implementation uses each library for a specific, "
            "demonstrable part of the system."
        )
        for item in LIBRARY_ROLES:
            st.markdown(f"**{item.library}**  \n{item.responsibility}")


def render_implementation_guide(
    schema: InferenceSchema,
    predictor: CatBoostPredictor,
    values: Mapping[str, object],
    result: PredictionResult | None,
    paths: AppPaths,
) -> None:
    st.header("Implementation guide")
    st.write(
        "Follow the application from setup to model output using verified "
        "runtime facts and the current prediction session."
    )
    _render_setup(paths)
    _render_runtime(paths, schema, predictor)
    _render_function_flow(paths)
    _render_trace(schema, values, result)
    _render_libraries()
