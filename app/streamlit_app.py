from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.presentation import (
    GUIDED_STEPS,
    build_payload,
    format_category,
    format_review_value,
    human_label,
)
from app.theme import build_theme_css
from src.config import AppPaths, DISCLAIMER
from src.inference import ArtifactError, CatBoostPredictor, PredictionResult
from src.schema import FeatureSpec, InferenceSchema, SchemaError, load_schema
from src.validation import InputValidationError

STEP_KEY = "guided_step"
VALUES_KEY = "guided_values"
RESULT_KEY = "prediction_result"
MISSING_LABEL = "I don't know"
TOTAL_STAGES = len(GUIDED_STEPS) + 1


@st.cache_resource
def load_runtime() -> tuple[InferenceSchema, CatBoostPredictor]:
    paths = AppPaths.from_environment()
    schema = load_schema(paths.inference_schema_path, paths.feature_schema_path)
    predictor = CatBoostPredictor.load(paths.model_path, schema)
    return schema, predictor


def default_values(schema: InferenceSchema) -> dict[str, object]:
    values: dict[str, object] = {}
    for name in schema.feature_order:
        spec = schema.features[name]
        if spec.kind == "numeric":
            values[name] = float((spec.minimum + spec.maximum) / 2)
        else:
            values[name] = spec.categories[0]
    return values


def initialise_state(schema: InferenceSchema) -> None:
    st.session_state.setdefault(STEP_KEY, 0)
    st.session_state.setdefault(VALUES_KEY, default_values(schema))
    st.session_state.setdefault(RESULT_KEY, None)


def render_header() -> None:
    st.title("Student Health Risk Demonstrator")
    st.write(
        "Follow four short stages to receive a model-generated category "
        "for the Kaggle competition task."
    )
    st.warning(DISCLAIMER)
    st.info(
        "Privacy: this application does not ask for your name, contact "
        "details or student ID, and it does not store your responses."
    )
    st.caption(
        "Feature meanings, units and observed ranges have not been "
        "independently established as clinical standards."
    )


def inject_styles() -> None:
    st.markdown(
        build_theme_css("light"),
        unsafe_allow_html=True,
    )


def render_progress(step_index: int) -> None:
    title = (
        GUIDED_STEPS[step_index].title
        if step_index < len(GUIDED_STEPS)
        else "Review and result"
    )
    st.caption(f"Step {step_index + 1} of {TOTAL_STAGES}")
    st.progress((step_index + 1) / TOTAL_STAGES, text=title)
    st.subheader(title)


def render_numeric_input(name: str, spec: FeatureSpec) -> None:
    missing_key = f"missing::{name}"
    value_key = f"value::{name}"
    values = st.session_state[VALUES_KEY]
    current = values[name]
    if value_key not in st.session_state:
        st.session_state[value_key] = float(
            current
            if current is not None
            else (spec.minimum + spec.maximum) / 2
        )
    missing = st.checkbox(
        "I don't know",
        key=missing_key,
        help=f"Select this if {human_label(name).lower()} is not available.",
    )
    entered = st.number_input(
        human_label(name),
        min_value=float(spec.minimum),
        max_value=float(spec.maximum),
        key=value_key,
        disabled=missing,
        help=(
            "Allowed limits are the observed competition-data range, "
            "not a clinical reference range."
        ),
    )
    values[name] = None if missing else entered


def render_categorical_input(name: str, spec: FeatureSpec) -> None:
    value_key = f"value::{name}"
    values = st.session_state[VALUES_KEY]
    current = values[name]
    options = (MISSING_LABEL, *spec.categories)
    if value_key not in st.session_state:
        st.session_state[value_key] = (
            MISSING_LABEL if current is None else current
        )
    selected = st.selectbox(
        human_label(name),
        options=options,
        key=value_key,
        format_func=(
            lambda value: (
                MISSING_LABEL
                if value == MISSING_LABEL
                else format_category(value)
            )
        ),
    )
    values[name] = None if selected == MISSING_LABEL else selected


def render_feature(name: str, schema: InferenceSchema) -> None:
    spec = schema.features[name]
    if spec.kind == "numeric":
        render_numeric_input(name, spec)
    else:
        render_categorical_input(name, spec)


def store_visible_values() -> None:
    if STEP_KEY not in st.session_state or VALUES_KEY not in st.session_state:
        return
    step_index = st.session_state[STEP_KEY]
    if step_index >= len(GUIDED_STEPS):
        return
    values = st.session_state[VALUES_KEY]
    for name in GUIDED_STEPS[step_index].features:
        widget_value = st.session_state.get(f"value::{name}")
        if st.session_state.get(f"missing::{name}", False):
            values[name] = None
        elif widget_value == MISSING_LABEL:
            values[name] = None
        elif widget_value is not None:
            values[name] = widget_value


def go_forward() -> None:
    store_visible_values()
    st.session_state[STEP_KEY] = min(
        st.session_state[STEP_KEY] + 1,
        TOTAL_STAGES - 1,
    )


def go_back() -> None:
    store_visible_values()
    current_step = st.session_state.get(STEP_KEY, 1)
    st.session_state[STEP_KEY] = max(current_step - 1, 0)
    st.session_state[RESULT_KEY] = None


def render_navigation(show_back: bool, show_continue: bool) -> None:
    back_column, continue_column = st.columns(2)
    with back_column:
        if show_back:
            st.button(
                "Back",
                key="back_button",
                on_click=go_back,
                use_container_width=True,
            )
    with continue_column:
        if show_continue:
            st.button(
                "Continue",
                key="continue_button",
                type="primary",
                on_click=go_forward,
                use_container_width=True,
            )


def render_data_entry_step(
    step_index: int,
    schema: InferenceSchema,
) -> None:
    step = GUIDED_STEPS[step_index]
    st.write(step.description)
    with st.container(border=True):
        for name in step.features:
            render_feature(name, schema)
    render_navigation(show_back=step_index > 0, show_continue=True)


def render_review_group(
    title: str,
    features: tuple[str, ...],
    values: dict[str, object],
) -> None:
    with st.container(border=True):
        st.markdown(f"#### {title}")
        for name in features:
            st.markdown(
                f"**{human_label(name)}**  \n"
                f"{format_review_value(values[name])}"
            )


def reset_check() -> None:
    keys_to_remove = (
        STEP_KEY,
        VALUES_KEY,
        RESULT_KEY,
        *(
            key
            for key in st.session_state
            if key.startswith(("value::", "missing::"))
        ),
    )
    for key in keys_to_remove:
        st.session_state.pop(key, None)
    st.session_state[STEP_KEY] = 0


def render_confidence_details(result: PredictionResult) -> None:
    with st.expander("Show confidence details", expanded=False):
        st.write(
            "The model compared the record with all three competition "
            "categories."
        )
        for label, score in result.confidence_scores.items():
            st.progress(
                score,
                text=f"{format_category(label)}: {score:.1%}",
            )
        st.caption(
            "These are model confidence scores, not calibrated probabilities."
        )


def render_result(result: PredictionResult) -> None:
    with st.container(border=True):
        st.subheader("Your model result")
        st.caption("Predicted category")
        st.markdown(f"## {format_category(result.label)}")
        st.write(
            "This category is a statistical output produced for the Kaggle "
            "competition task. It does not provide a medical interpretation "
            "or personal health advice."
        )
        st.warning(DISCLAIMER)
        render_confidence_details(result)
        st.button(
            "Start a new check",
            key="reset_button",
            type="primary",
            on_click=reset_check,
            use_container_width=True,
        )


def render_review(
    schema: InferenceSchema,
    predictor: CatBoostPredictor,
) -> None:
    result = st.session_state[RESULT_KEY]
    if result is not None:
        render_result(result)
        with st.expander("Review your responses", expanded=False):
            for step in GUIDED_STEPS:
                render_review_group(step.title, step.features, st.session_state[VALUES_KEY])
        return

    st.write(
        "Check your responses before asking the verified model to create "
        "a competition category."
    )
    values = st.session_state[VALUES_KEY]
    for step in GUIDED_STEPS:
        render_review_group(step.title, step.features, values)

    back_column, predict_column = st.columns(2)
    with back_column:
        back_requested = st.button(
            "Back",
            key="review_back_button",
            use_container_width=True,
        )
        if back_requested:
            go_back()
            st.rerun()
    with predict_column:
        submitted = st.button(
            "Show my result",
            key="predict_button",
            type="primary",
            use_container_width=True,
        )
    if submitted:
        payload = build_payload(values, schema)
        try:
            with st.spinner("Creating your model result..."):
                st.session_state[RESULT_KEY] = predictor.predict(payload)
        except (InputValidationError, ArtifactError):
            st.error(
                "A result could not be created. Please review the entries "
                "and try again."
            )
        else:
            st.rerun()


def render_app() -> None:
    st.set_page_config(
        page_title="Student Health Risk Demonstrator",
        layout="centered",
    )
    inject_styles()
    render_header()
    try:
        schema, predictor = load_runtime()
    except (SchemaError, ArtifactError) as exc:
        st.error(
            "The application is temporarily unavailable because its "
            f"verified model files could not be loaded: {exc}"
        )
        st.stop()

    initialise_state(schema)
    step_index = st.session_state[STEP_KEY]
    render_progress(step_index)
    if step_index < len(GUIDED_STEPS):
        render_data_entry_step(step_index, schema)
    else:
        render_review(schema, predictor)


if __name__ == "__main__":
    render_app()
