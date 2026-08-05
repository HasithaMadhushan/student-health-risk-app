from pathlib import Path
import subprocess
import sys
from contextlib import nullcontext
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

import app.streamlit_app as streamlit_app
from src.config import AppPaths, DISCLAIMER
from src.inference import PredictionResult
from src.schema import SchemaError, load_schema

APP = Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py"
PROJECT_ROOT = APP.parents[1]


def stage_text(app):
    return " ".join(
        item.value
        for collection in (app.markdown, app.caption, app.subheader)
        for item in collection
    )


def reach_step_two(app):
    app.button(key="continue_button").click().run(timeout=30)
    return app


def make_prediction(app):
    app = reach_step_two(app)
    app.button(key="predict_button").click().run(timeout=30)
    return app


def widget(app, collection, key):
    return next(item for item in collection if item.key == key)


def test_app_script_can_resolve_project_modules():
    completed = subprocess.run(
        [sys.executable, str(APP)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_app_has_no_disclaimer_or_identifying_fields():
    app = AppTest.from_file(str(APP)).run(timeout=30)
    assert not app.exception
    visible = " ".join(
        item.value
        for collection in (app.markdown, app.info, app.warning, app.caption)
        for item in collection
    )
    assert "Important information" not in visible
    assert DISCLAIMER not in visible
    assert 'class="medical-disclaimer"' not in visible
    assert not app.warning
    assert "Your answers stay in this session" not in visible
    labels = {
        item.label.casefold()
        for collection in (app.number_input, app.selectbox, app.checkbox)
        for item in collection
    }
    assert labels.isdisjoint(
        {"name", "student id", "email", "phone", "phone number"}
    )


def test_disclaimer_is_absent_across_normal_app_states():
    states = (
        AppTest.from_file(str(APP)).run(timeout=30),
        reach_step_two(AppTest.from_file(str(APP)).run(timeout=30)),
        make_prediction(AppTest.from_file(str(APP)).run(timeout=30)),
    )
    for current in states:
        visible = " ".join(item.value for item in current.markdown)
        assert DISCLAIMER not in visible
        assert 'class="medical-disclaimer"' not in visible
        assert not current.warning


def test_footer_omits_course_and_model_metadata():
    states = (
        AppTest.from_file(str(APP)).run(timeout=30),
        reach_step_two(AppTest.from_file(str(APP)).run(timeout=30)),
        make_prediction(AppTest.from_file(str(APP)).run(timeout=30)),
    )
    for current in states:
        visible = " ".join(item.value for item in current.markdown)
        assert "CIS6005 Computational Intelligence project" not in visible
        assert "Model family: CatBoost" not in visible


def test_app_uses_exactly_two_clear_steps():
    app = AppTest.from_file(str(APP)).run(timeout=30)
    assert app.title[0].value == "Student Health Risk Prediction"
    assert (
        "Enter one record to generate a competition-model prediction."
        in stage_text(app)
    )
    assert "Step 1 of 2" in stage_text(app)
    assert "Health-related inputs" in stage_text(app)
    assert app.button(key="continue_button").label == "Continue"

    app = reach_step_two(app)
    assert "Step 2 of 2" in stage_text(app)
    assert "Daily routine inputs" in stage_text(app)
    assert app.button(key="back_button").label == "Back"
    assert app.button(key="predict_button").label == "Generate prediction"


def test_numeric_inputs_start_blank_without_ambiguous_checkboxes():
    app = AppTest.from_file(str(APP)).run(timeout=30)
    assert not app.checkbox
    for name in ("sleep_duration", "heart_rate", "bmi"):
        assert widget(app, app.number_input, f"value::{name}").value is None


def test_numeric_inputs_use_clean_direct_entry():
    app = AppTest.from_file(str(APP)).run(timeout=30)
    expected = {
        "sleep_duration": "e.g. 8.5 hours",
        "heart_rate": "e.g. 72 bpm",
        "bmi": "e.g. 24.5",
    }
    for name, placeholder in expected.items():
        field = widget(app, app.number_input, f"value::{name}")
        assert not field.help
        assert field.proto.placeholder == placeholder

    app = reach_step_two(app)
    expected = {
        "calorie_expenditure": "e.g. 2500",
        "step_count": "e.g. 8000",
        "exercise_duration": "e.g. 30 minutes",
        "water_intake": "e.g. 2.5 litres",
    }
    for name, placeholder in expected.items():
        field = widget(app, app.number_input, f"value::{name}")
        assert not field.help
        assert field.proto.placeholder == placeholder

    widget(app, app.number_input, "value::step_count").set_value(8000.0)
    assert widget(app, app.number_input, "value::step_count").value == 8000.0


def test_numeric_inputs_use_human_friendly_units_and_precision():
    app = AppTest.from_file(str(APP)).run(timeout=30)
    step_one = {
        "sleep_duration": ("Sleep duration (hours)", 0.5, "%.1f"),
        "heart_rate": ("Heart rate (bpm)", 1.0, "%.0f"),
        "bmi": ("BMI", 0.1, "%.1f"),
    }
    for name, (label, step, number_format) in step_one.items():
        field = widget(app, app.number_input, f"value::{name}")
        assert field.label == label
        assert field.step == step
        assert field.format == number_format

    app = reach_step_two(app)
    step_two = {
        "calorie_expenditure": ("Daily energy use", 50.0, "%.0f"),
        "step_count": ("Daily step count", 500.0, "%.0f"),
        "exercise_duration": ("Exercise duration (minutes)", 1.0, "%.0f"),
        "water_intake": ("Water intake (litres)", 0.1, "%.1f"),
    }
    for name, (label, step, number_format) in step_two.items():
        field = widget(app, app.number_input, f"value::{name}")
        assert field.label == label
        assert field.step == step
        assert field.format == number_format


def test_categorical_inputs_prompt_for_a_choice_and_offer_not_sure():
    app = AppTest.from_file(str(APP)).run(timeout=30)
    for name in ("sleep_quality", "stress_level"):
        field = widget(app, app.selectbox, f"value::{name}")
        assert field.value is None
        assert "Not sure" in field.options


def test_navigation_preserves_entered_values():
    app = AppTest.from_file(str(APP)).run(timeout=30)
    widget(app, app.number_input, "value::sleep_duration").set_value(8.0)
    app = reach_step_two(app)
    app.button(key="back_button").click().run(timeout=30)
    assert "Step 1 of 2" in stage_text(app)
    assert widget(app, app.number_input, "value::sleep_duration").value == 8.0


def test_step_two_contains_compact_review_of_all_features():
    app = reach_step_two(AppTest.from_file(str(APP)).run(timeout=30))
    assert any(item.label == "Review entered values" for item in app.expander)
    review = " ".join(item.value for item in app.markdown)
    for label in (
        "Sleep duration",
        "Heart rate",
        "BMI",
        "Daily energy use",
        "Daily step count",
        "Exercise duration",
        "Water intake",
        "Diet type",
        "Stress level",
        "Sleep quality",
        "Physical activity level",
        "Smoking and alcohol",
    ):
        assert label in review
    assert "Not provided" in review
    for forbidden in (
        "model_sha256",
        "experiment_id",
        "artifacts/private",
        "student_id",
    ):
        assert forbidden not in review


def test_result_is_simple_and_confidence_details_are_available():
    app = make_prediction(AppTest.from_file(str(APP)).run(timeout=30))
    assert not app.exception
    visible = stage_text(app)
    assert "Prediction result" in visible
    assert "Predicted competition category" in visible
    assert (
        "This category was generated by the trained competition model."
        in visible
    )
    assert any(item.label == "View model confidence scores" for item in app.expander)
    assert app.button(key="reset_button").label == "Start a new prediction"
    assert all(button.key != "predict_button" for button in app.button)
    score_progress = [
        item for item in app.get("progress") if item.proto.text
    ]
    assert len(score_progress) == 3
    score_labels = [item.proto.text for item in score_progress]
    assert score_labels[0].startswith("At-risk:")
    assert score_labels[1].startswith("Fit:")
    assert score_labels[2].startswith("Unhealthy:")
    assert not app.warning


def test_result_rerun_keeps_one_reset_action_and_no_prediction_action():
    app = make_prediction(AppTest.from_file(str(APP)).run(timeout=30))
    app.run(timeout=30)
    reset_actions = [
        button for button in app.button if button.key == "reset_button"
    ]
    assert len(reset_actions) == 1
    assert all(button.key != "predict_button" for button in app.button)


def test_one_prediction_click_invokes_predictor_once_across_result_rerender(
    monkeypatch,
):
    paths = AppPaths.from_environment()
    schema = load_schema(
        paths.inference_schema_path,
        paths.feature_schema_path,
    )
    result = PredictionResult(
        label="at-risk",
        confidence_scores={
            "at-risk": 0.6,
            "fit": 0.2,
            "unhealthy": 0.2,
        },
        experiment_id="test-experiment",
        model_sha256="test-hash",
    )
    predictor = Mock()
    predictor.predict.return_value = result
    state = {
        streamlit_app.STEP_KEY: 1,
        streamlit_app.VALUES_KEY: streamlit_app.default_values(schema),
        streamlit_app.RESULT_KEY: None,
    }
    monkeypatch.setattr(streamlit_app.st, "session_state", state)
    monkeypatch.setattr(streamlit_app, "render_review_summary", lambda values: None)
    monkeypatch.setattr(
        streamlit_app.st,
        "columns",
        lambda count: tuple(nullcontext() for _ in range(count)),
    )
    monkeypatch.setattr(
        streamlit_app.st,
        "button",
        lambda label, key, **kwargs: key == "predict_button",
    )
    monkeypatch.setattr(streamlit_app.st, "spinner", lambda message: nullcontext())
    monkeypatch.setattr(streamlit_app.st, "rerun", lambda: None)

    streamlit_app.render_step_two_actions(schema, predictor)
    assert predictor.predict.call_count == 1

    monkeypatch.setattr(streamlit_app.st, "set_page_config", lambda **kwargs: None)
    monkeypatch.setattr(streamlit_app, "inject_styles", lambda: None)
    monkeypatch.setattr(streamlit_app, "render_header", lambda: None)
    monkeypatch.setattr(streamlit_app, "load_runtime", lambda: (schema, predictor))
    monkeypatch.setattr(streamlit_app, "render_progress", lambda step: None)
    monkeypatch.setattr(streamlit_app, "render_result", lambda value: None)
    streamlit_app.render_app()

    assert predictor.predict.call_count == 1


def test_startup_failure_hides_internal_exception_without_disclaimer(
    monkeypatch,
):
    sentinel = r"C:\artifacts\private\secret-model.cbm::internal_feature_key"
    errors = []
    rendered_markdown = []

    def fail_runtime_load():
        raise SchemaError(sentinel)

    class StopRendering(RuntimeError):
        pass

    monkeypatch.setattr(streamlit_app.st, "set_page_config", lambda **kwargs: None)
    monkeypatch.setattr(streamlit_app, "inject_styles", lambda: None)
    monkeypatch.setattr(streamlit_app, "render_header", lambda: None)
    monkeypatch.setattr(streamlit_app, "load_runtime", fail_runtime_load)
    monkeypatch.setattr(streamlit_app.st, "error", errors.append)
    monkeypatch.setattr(
        streamlit_app.st,
        "markdown",
        lambda body, **kwargs: rendered_markdown.append(body),
    )
    monkeypatch.setattr(
        streamlit_app.st,
        "stop",
        lambda: (_ for _ in ()).throw(StopRendering()),
    )

    with pytest.raises(StopRendering):
        streamlit_app.render_app()

    visible = " ".join((*errors, *rendered_markdown))
    assert sentinel not in visible
    assert "internal_feature_key" not in visible
    assert errors == [
        "The application is temporarily unavailable. Please try again later."
    ]
    assert DISCLAIMER not in visible
    assert 'class="medical-disclaimer"' not in visible
    assert "CIS6005 Computational Intelligence project" not in visible
    assert "Model family: CatBoost" not in visible


def test_start_new_check_returns_to_blank_first_step():
    app = make_prediction(AppTest.from_file(str(APP)).run(timeout=30))
    app.button(key="reset_button").click().run(timeout=30)
    assert "Step 1 of 2" in stage_text(app)
    assert "Prediction result" not in stage_text(app)
    for field in app.number_input:
        assert field.value is None
    for field in app.selectbox:
        assert field.value is None
