# CIS6005 Viva Demonstration Guide

## Purpose

Use this 5-7 minute guide during the viva. The deployed application stays
simple for a non-technical student; implementation evidence is demonstrated
from the repository and terminal alongside the working app.

## Setup

From the project root, run:

```powershell
python -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
& '.\.venv\Scripts\python.exe' -m pytest -q
& '.\.venv\Scripts\streamlit.exe' run app\streamlit_app.py
```

Open `http://localhost:8501`. Do not show credentials, raw competition data or
personal information.

## Practical demonstration

1. Show the title, permanent non-diagnostic disclaimer and privacy statement.
2. Explain that the app requests only the 12 features required by the locked
   model and does not collect a name, student ID or contact details.
3. On Step 1, show that numeric fields start blank, categorical fields prompt
   for a choice, and the `+` and `-` controls use sensible increments.
4. Continue to Step 2, use **Not sure** once, then use **Back** to demonstrate
   temporary session-state handling. Return to Step 2 and open **Review all
   answers** to show all 12 features before inference.
5. Select **Get my result**. Show the predicted category, then expand **Show
   confidence details**. Explain that these are model confidence scores, not
   calibrated medical probabilities.
6. Select **Start a new check** to demonstrate reset behaviour.

## Exact function invocation flow

Open each file at the named function while explaining this sequence:

1. `app/streamlit_app.py: render_app()` hosts the Streamlit application.
2. `render_app()` calls `load_runtime()` once through Streamlit's resource
   cache.
3. `src/config.py: AppPaths.from_environment()` resolves model/schema paths.
4. `src/schema.py: load_schema()` validates the feature and class contracts.
5. `src/inference.py: CatBoostPredictor.load()` verifies the model SHA-256 and
   calls CatBoost's `load_model()`.
6. `app/presentation.py: GUIDED_STEPS` defines the friendly input grouping;
   `build_payload()` restores the locked training feature order.
7. Pressing **Get my result** calls
   `src/inference.py: CatBoostPredictor.predict()`.
8. `src/validation.py: prepare_record()` validates inputs, maps missing numeric
   values to `numpy.nan`, maps missing categories to `__MISSING__`, and creates
   a one-row pandas DataFrame.
9. The predictor invokes CatBoost `predict_proba()` and `predict()`.
10. `app/streamlit_app.py: render_result()` presents the class and three
    ordered confidence scores.

## Library responsibilities

- **Streamlit** renders controls, navigation, messages and temporary state.
- **CatBoost** loads the trained 343-tree classifier and performs inference.
- **pandas** creates the one-row table in the saved feature order.
- **NumPy** represents numeric missingness and normalises model arrays.
- **hashlib** verifies the deployed model against its locked SHA-256.
- **pytest and Streamlit AppTest** verify integrity, prediction and UI flow.

## Excellent-criterion evidence map

| Criterion | Viva evidence |
|---|---|
| Clear setup | Run the setup commands and open the working app |
| Pinpoint ML host | Show `render_app()` and `load_runtime()` |
| Explain invocations | Follow the ten calls above in order |
| Explain input processing | Show schema controls, `build_payload()` and `prepare_record()` |
| Explain output processing | Show CatBoost calls, class mapping and `render_result()` |
| Demonstrate libraries | State each library responsibility above |
| Practical demonstration | Complete one prediction, inspect confidence and reset |

## Items still requiring evidence

- Capture current final-interface screenshots for the report if needed.
- Add the final/private Kaggle score and rank only after they are verified.
