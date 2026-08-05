from __future__ import annotations

import sys
from dataclasses import dataclass
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
from src.config import AppPaths
from src.inference import ArtifactError, CatBoostPredictor, PredictionResult
from src.schema import FeatureSpec, InferenceSchema, SchemaError, load_schema
from src.validation import InputValidationError

STEP_KEY = "guided_step"
VALUES_KEY = "guided_values"
RESULT_KEY = "prediction_result"
MISSING_LABEL = "Not sure"
TOTAL_STAGES = len(GUIDED_STEPS)


@dataclass(frozen=True)
class NumericInputDisplay:
    label: str
    placeholder: str
    step: float
    number_format: str
    display_minimum: float | None = None
    display_maximum: float | None = None


NUMERIC_INPUTS = {
    "sleep_duration": NumericInputDisplay(
        "Sleep duration (hours)",
        "e.g. 8.5 hours",
        0.5,
        "%.1f",
    ),
    "heart_rate": NumericInputDisplay(
        "Heart rate (bpm)",
        "e.g. 72 bpm",
        1.0,
        "%.0f",
    ),
    "bmi": NumericInputDisplay(
        "BMI",
        "e.g. 24.5",
        0.1,
        "%.1f",
    ),
    "calorie_expenditure": NumericInputDisplay(
        "Daily energy use",
        "e.g. 2500",
        50.0,
        "%.0f",
    ),
    "step_count": NumericInputDisplay(
        "Daily step count",
        "e.g. 8000",
        500.0,
        "%.0f",
        1500.0,
        14500.0,
    ),
    "exercise_duration": NumericInputDisplay(
        "Exercise duration (minutes)",
        "e.g. 30 minutes",
        1.0,
        "%.0f",
    ),
    "water_intake": NumericInputDisplay(
        "Water intake (litres)",
        "e.g. 2.5 litres",
        0.1,
        "%.1f",
    ),
}


@st.cache_resource
def load_runtime() -> tuple[InferenceSchema, CatBoostPredictor]:
    paths = AppPaths.from_environment()
    schema = load_schema(paths.inference_schema_path, paths.feature_schema_path)
    predictor = CatBoostPredictor.load(paths.model_path, schema)
    return schema, predictor


def default_values(schema: InferenceSchema) -> dict[str, object]:
    return {name: None for name in schema.feature_order}


def initialise_state(schema: InferenceSchema) -> None:
    st.session_state.setdefault(STEP_KEY, 0)
    st.session_state.setdefault(VALUES_KEY, default_values(schema))
    st.session_state.setdefault(RESULT_KEY, None)


def render_header() -> None:
    st.title("Student Health Risk Prediction")
    st.write("Enter one record to generate a competition-model prediction.")


def inject_styles() -> None:
    st.markdown(
        build_theme_css("light"),
        unsafe_allow_html=True,
    )


def render_progress(step_index: int) -> None:
    step = GUIDED_STEPS[step_index]
    st.caption(f"Step {step_index + 1} of {TOTAL_STAGES}")
    st.progress((step_index + 1) / TOTAL_STAGES)
    st.subheader(step.title)
    st.caption(step.description)


def render_numeric_input(name: str, spec: FeatureSpec) -> None:
    value_key = f"value::{name}"
    values = st.session_state[VALUES_KEY]
    display = NUMERIC_INPUTS[name]
    entered = st.number_input(
        display.label,
        min_value=(
            display.display_minimum
            if display.display_minimum is not None
            else float(spec.minimum)
        ),
        max_value=(
            display.display_maximum
            if display.display_maximum is not None
            else float(spec.maximum)
        ),
        value=values[name],
        step=display.step,
        format=display.number_format,
        key=value_key,
        placeholder=display.placeholder,
    )
    values[name] = entered


def render_categorical_input(name: str, spec: FeatureSpec) -> None:
    value_key = f"value::{name}"
    values = st.session_state[VALUES_KEY]
    options = (*spec.categories, MISSING_LABEL)
    current = values[name]
    selected_index = (
        options.index(current) if current in options else None
    )
    selected = st.selectbox(
        human_label(name),
        options=options,
        index=selected_index,
        key=value_key,
        placeholder="Select an answer",
        format_func=(
            lambda value: (
                MISSING_LABEL
                if value == MISSING_LABEL
                else format_category(value)
            )
        ),
    )
    values[name] = (
        None if selected in (None, MISSING_LABEL) else selected
    )


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
        if widget_value in (None, MISSING_LABEL):
            values[name] = None
        else:
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


def render_continue() -> None:
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
    with st.container(border=True):
        columns = st.columns(2, gap="large")
        for index, name in enumerate(step.features):
            with columns[index % 2]:
                render_feature(name, schema)


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


def render_review_summary(values: dict[str, object]) -> None:
    with st.expander("Review entered values", expanded=False):
        for step in GUIDED_STEPS:
            render_review_group(step.title, step.features, values)


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
    with st.expander("View model confidence scores", expanded=False):
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
        st.subheader("Prediction result")
        st.caption("Predicted competition category")
        st.markdown(f"## {format_category(result.label)}")
        st.write(
            "This category was generated by the trained competition model."
        )
        render_confidence_details(result)
        st.button(
            "Start a new prediction",
            key="reset_button",
            type="primary",
            on_click=reset_check,
            use_container_width=True,
        )


def render_step_two_actions(
    schema: InferenceSchema,
    predictor: CatBoostPredictor,
) -> None:
    values = st.session_state[VALUES_KEY]
    render_review_summary(values)

    back_column, predict_column = st.columns(2)
    with back_column:
        back_requested = st.button(
            "Back",
            key="back_button",
            use_container_width=True,
        )
        if back_requested:
            go_back()
            st.rerun()
    with predict_column:
        submitted = st.button(
            "Generate prediction",
            key="predict_button",
            type="primary",
            use_container_width=True,
        )
    if submitted:
        store_visible_values()
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
        page_title="Student Health Risk Prediction",
        layout="centered",
    )
    inject_styles()
    render_header()
    try:
        schema, predictor = load_runtime()
    except (SchemaError, ArtifactError):
        st.error(
            "The application is temporarily unavailable. Please try again later."
        )
        st.empty()
        st.stop()

    initialise_state(schema)
    step_index = st.session_state[STEP_KEY]
    render_progress(step_index)
    result = st.session_state[RESULT_KEY]
    if result is not None:
        render_result(result)
        render_review_summary(st.session_state[VALUES_KEY])
        st.empty()
        return

    render_data_entry_step(step_index, schema)
    if step_index == 0:
        render_continue()
    else:
        render_step_two_actions(schema, predictor)
    st.empty()


if __name__ == "__main__":
    render_app()
