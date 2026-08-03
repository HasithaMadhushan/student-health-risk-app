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


def reach_review(app):
    for _ in range(3):
        app.button(key="continue_button").click().run(timeout=30)
    return app


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
        widget.label.casefold()
        for collection in (app.number_input, app.selectbox, app.checkbox)
        for widget in collection
    }
    assert labels.isdisjoint(
        {"name", "student id", "email", "phone", "phone number"}
    )


def test_app_exposes_only_the_student_health_check_journey():
    app = AppTest.from_file(str(APP)).run(timeout=30)
    visible = " ".join(
        item.value
        for collection in (
            app.title,
            app.markdown,
            app.caption,
            app.info,
            app.warning,
        )
        for item in collection
    )
    assert "Student Health Risk Demonstrator" in visible
    assert "Step 1 of 4" in visible
    assert "Implementation guide" not in visible
    assert "Appearance" not in visible
    assert not app.segmented_control


def test_app_guides_user_through_four_stages_and_preserves_values():
    app = AppTest.from_file(str(APP)).run(timeout=30)
    assert "Step 1 of 4" in stage_text(app)
    sleep = next(
        item
        for item in app.number_input
        if item.key == "value::sleep_duration"
    )
    sleep.set_value(8.0)
    app.button(key="continue_button").click().run(timeout=30)
    assert "Step 2 of 4" in stage_text(app)
    app.button(key="back_button").click().run(timeout=30)
    assert "Step 1 of 4" in stage_text(app)
    sleep = next(
        item
        for item in app.number_input
        if item.key == "value::sleep_duration"
    )
    assert sleep.value == 8.0


def test_review_stage_contains_every_feature_and_no_result_before_submission():
    app = reach_review(AppTest.from_file(str(APP)).run(timeout=30))
    assert "Step 4 of 4" in stage_text(app)
    review = " ".join(item.value for item in app.markdown)
    for label in (
        "Sleep duration",
        "Heart rate",
        "BMI",
        "Calorie expenditure",
        "Step count",
        "Exercise duration",
        "Water intake",
        "Diet type",
        "Stress level",
        "Sleep quality",
        "Physical activity level",
        "Smoking and alcohol",
    ):
        assert label in review
    assert not app.success


def test_result_is_simple_first_and_confidence_details_are_available():
    app = reach_review(AppTest.from_file(str(APP)).run(timeout=30))
    app.button(key="predict_button").click().run(timeout=30)
    assert not app.exception
    visible = stage_text(app)
    assert "Your model result" in visible
    assert "Predicted category" in visible
    assert any(
        item.label == "Show confidence details" for item in app.expander
    )
    assert len(app.get("progress")) >= 4
    assert "not calibrated probabilities" in visible


def test_every_visible_input_step_offers_i_do_not_know():
    app = AppTest.from_file(str(APP)).run(timeout=30)
    seen = set()
    for step_index in range(3):
        seen.update(
            item.key.removeprefix("missing::")
            for item in app.checkbox
            if item.key and item.key.startswith("missing::")
        )
        seen.update(
            item.key.removeprefix("value::")
            for item in app.selectbox
            if item.key
            and item.key.startswith("value::")
            and "I don't know" in item.options
        )
        if step_index < 2:
            app.button(key="continue_button").click().run(timeout=30)
    assert seen == {
        "sleep_duration",
        "heart_rate",
        "bmi",
        "sleep_quality",
        "calorie_expenditure",
        "step_count",
        "exercise_duration",
        "water_intake",
        "physical_activity_level",
        "diet_type",
        "stress_level",
        "smoking_alcohol",
    }


def test_start_new_check_returns_to_first_stage_without_a_result():
    app = reach_review(AppTest.from_file(str(APP)).run(timeout=30))
    app.button(key="predict_button").click().run(timeout=30)
    app.button(key="reset_button").click().run(timeout=30)
    assert "Step 1 of 4" in stage_text(app)
    assert "Your model result" not in stage_text(app)
