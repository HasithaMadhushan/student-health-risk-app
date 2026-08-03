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
        title="Sleep and body",
        description=(
            "Start with information about sleep and general body measurements."
        ),
        features=("sleep_duration", "heart_rate", "bmi", "sleep_quality"),
    ),
    StepDefinition(
        title="Activity and daily habits",
        description="Next, add activity and hydration information.",
        features=(
            "calorie_expenditure",
            "step_count",
            "exercise_duration",
            "water_intake",
            "physical_activity_level",
        ),
    ),
    StepDefinition(
        title="Lifestyle and wellbeing",
        description=(
            "Finally, add the remaining lifestyle and wellbeing information."
        ),
        features=("diet_type", "stress_level", "smoking_alcohol"),
    ),
)

FRIENDLY_LABELS = {
    "bmi": "BMI",
    "smoking_alcohol": "Smoking and alcohol",
}


def human_label(name: str) -> str:
    return FRIENDLY_LABELS.get(name, name.replace("_", " ").capitalize())


def format_category(value: str) -> str:
    return value.replace("_", " ").capitalize()


def format_review_value(value: object) -> str:
    if value is None:
        return "I don't know"
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
