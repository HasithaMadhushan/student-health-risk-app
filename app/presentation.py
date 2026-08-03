from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from src.schema import InferenceSchema


@dataclass(frozen=True)
class StepDefinition:
    title: str
    description: str
    features: tuple[str, ...]


GUIDED_STEPS = (
    StepDefinition(
        title="Your health basics",
        description="Add what you know. You can leave any number blank.",
        features=(
            "sleep_duration",
            "heart_rate",
            "bmi",
            "sleep_quality",
            "stress_level",
        ),
    ),
    StepDefinition(
        title="Your daily routine",
        description="One final group, then review your answers and get a result.",
        features=(
            "calorie_expenditure",
            "step_count",
            "exercise_duration",
            "water_intake",
            "physical_activity_level",
            "diet_type",
            "smoking_alcohol",
        ),
    ),
)

FRIENDLY_LABELS = {
    "bmi": "BMI",
    "calorie_expenditure": "Daily energy use",
    "step_count": "Daily step count",
    "smoking_alcohol": "Smoking and alcohol",
}


def human_label(name: str) -> str:
    return FRIENDLY_LABELS.get(name, name.replace("_", " ").capitalize())


def format_category(value: str) -> str:
    return value.replace("_", " ").capitalize()


def format_review_value(value: object) -> str:
    if value is None:
        return "Not provided"
    if isinstance(value, str):
        return format_category(value)
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def build_payload(
    values: Mapping[str, object],
    schema: InferenceSchema,
) -> dict[str, object]:
    return {name: values.get(name) for name in schema.feature_order}
