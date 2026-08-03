# Two-Step Student Input Flow Design

## Goal

Reduce effort and uncertainty for non-technical users while preserving the
locked 12-feature CatBoost inference contract, privacy rules and disclaimer.

## Research basis

The palette adapts established NHS digital-service colour roles rather than
copying NHS branding. It uses reduced-glare grey, dark text, blue primary
actions, green progress/success, pale-yellow warnings and yellow keyboard
focus. Text pairs must meet WCAG 2.2 AA contrast.

The interaction design follows progressive disclosure, visible labels,
explicit progress, touch targets of at least 44 pixels and clear submission
feedback.

## Two-step structure

### Step 1: Your health basics

- sleep duration
- heart rate
- BMI
- sleep quality
- stress level

The primary action is **Continue to daily routine**.

### Step 2: Your daily routine

- calorie expenditure
- step count
- exercise duration
- water intake
- physical activity level
- diet type
- smoking and alcohol

Step 2 includes a compact collapsed **Review all answers** summary and the
primary action **Get my result**. The user can return to Step 1 with **Back**.
There is no separate review step.

## Numeric inputs

Numeric fields start blank so the application never silently invents a user's
answer. Blank means unavailable and is passed through the existing missing-data
contract. This removes repeated numeric **I don't know** checkboxes.

Each field has a visible human label, non-clinical unit hint and practical
increment:

| Feature | Display label | Hint | Step |
|---|---|---|---:|
| `sleep_duration` | Sleep duration | hours per night | 0.25 |
| `heart_rate` | Heart rate | beats per minute | 1 |
| `bmi` | BMI | body mass index | 0.1 |
| `calorie_expenditure` | Daily energy use | competition units | 50 |
| `step_count` | Daily step count | steps per day | 500 |
| `exercise_duration` | Exercise duration | minutes per day | 5 |
| `water_intake` | Water intake | competition units | 0.25 |

The hints do not claim that unresolved competition units are clinically
verified. Inputs retain the saved observed minimum and maximum limits.

## Categorical inputs

Categorical fields begin with **Select an answer** and include **Not sure**.
Friendly option labels are displayed without changing the raw values passed to
the model. A blank selection or **Not sure** maps to the saved missing-category
token through the existing payload and validation path.

## Review and output

The compact review lists all 12 values before **Get my result**. Blank and
**Not sure** entries appear as **Not provided**. Result behaviour is unchanged:
predicted category first, three confidence scores in a disclosure, permanent
non-diagnostic disclaimer and **Start a new check**.

## Palette

- page background: `#F0F4F5`
- text: `#212B32`
- secondary text: `#4C6272`
- primary blue: `#005EB8`
- blue hover: `#003D78`
- progress/success green: `#007F3B`
- surface: `#FFFFFF`
- border: `#D8DDE0`
- input border: `#4C6272`
- warning surface: `#FFF9C4`
- warning text: `#212B32`
- focus: `#FFEB3B`
- error: `#D5281B`

The forced light presentation must override every alert token, preventing the
current mixed light-page/dark-alert appearance when the operating system uses a
dark preference.

## Technical boundaries

- Do not change the model, schema, feature order or prediction algorithm.
- Do not add clinical advice, clinical ranges or unverified units.
- Do not collect or persist identifying information or inputs.
- Do not move viva/code-flow material into the student application.
- Retain keyboard focus, responsive layout and reduced-motion support.

## Verification

Tests must first fail, then prove:

- exactly two steps and the approved feature grouping;
- blank numeric defaults and field-specific increments;
- categorical **Select an answer** and **Not sure** handling;
- 12-feature compact review on Step 2;
- unchanged payload order, missing-value mapping and production prediction;
- approved palette and WCAG AA contrast;
- one permanent disclaimer, reset, privacy and responsive layout;
- live `+` and `-` increments for representative numeric fields.
