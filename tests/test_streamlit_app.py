from pathlib import Path
import subprocess
import sys

from streamlit.testing.v1 import AppTest

from src.config import DISCLAIMER

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


def test_app_renders_disclaimer_and_no_identifying_fields():
    app = AppTest.from_file(str(APP)).run(timeout=30)
    assert not app.exception
    visible = " ".join(
        item.value
        for collection in (app.markdown, app.info, app.warning, app.caption)
        for item in collection
    )
    assert DISCLAIMER in visible
    labels = {
        item.label.casefold()
        for collection in (app.number_input, app.selectbox, app.checkbox)
        for item in collection
    }
    assert labels.isdisjoint(
        {"name", "student id", "email", "phone", "phone number"}
    )


def test_app_uses_exactly_two_clear_steps():
    app = AppTest.from_file(str(APP)).run(timeout=30)
    assert "Step 1 of 2" in stage_text(app)
    assert "Your health basics" in stage_text(app)
    assert "A quick two-step check" in stage_text(app)
    assert "Implementation guide" not in stage_text(app)

    app = reach_step_two(app)
    assert "Step 2 of 2" in stage_text(app)
    assert "Your daily routine" in stage_text(app)
    assert all(button.key != "continue_button" for button in app.button)


def test_numeric_inputs_start_blank_without_ambiguous_checkboxes():
    app = AppTest.from_file(str(APP)).run(timeout=30)
    assert not app.checkbox
    for name in ("sleep_duration", "heart_rate", "bmi"):
        assert widget(app, app.number_input, f"value::{name}").value is None


def test_numeric_inputs_use_clean_direct_entry():
    app = AppTest.from_file(str(APP)).run(timeout=30)
    expected = {
        "sleep_duration": "e.g. 7.5 hours",
        "heart_rate": "e.g. 72 bpm",
        "bmi": "e.g. 24.5",
    }
    for name, placeholder in expected.items():
        field = widget(app, app.number_input, f"value::{name}")
        assert not field.help
        assert field.proto.placeholder == placeholder

    app = reach_step_two(app)
    expected = {
        "calorie_expenditure": "Enter value",
        "step_count": "e.g. 8000",
        "exercise_duration": "e.g. 30 minutes",
        "water_intake": "Enter value",
    }
    for name, placeholder in expected.items():
        field = widget(app, app.number_input, f"value::{name}")
        assert not field.help
        assert field.proto.placeholder == placeholder

    widget(app, app.number_input, "value::step_count").set_value(8000.0)
    assert widget(app, app.number_input, "value::step_count").value == 8000.0


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
    assert any(item.label == "Review all answers" for item in app.expander)
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


def test_result_is_simple_and_confidence_details_are_available():
    app = make_prediction(AppTest.from_file(str(APP)).run(timeout=30))
    assert not app.exception
    visible = stage_text(app)
    assert "Your model result" in visible
    assert "Predicted category" in visible
    assert any(
        item.label == "Show confidence details" for item in app.expander
    )
    assert "not calibrated probabilities" in visible
    assert len(app.warning) == 1


def test_start_new_check_returns_to_blank_first_step():
    app = make_prediction(AppTest.from_file(str(APP)).run(timeout=30))
    app.button(key="reset_button").click().run(timeout=30)
    assert "Step 1 of 2" in stage_text(app)
    assert "Your model result" not in stage_text(app)
    assert widget(app, app.number_input, "value::sleep_duration").value is None
