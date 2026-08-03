# CIS6005 Student Health Risk Demonstrator

This repository contains the local Streamlit application for the CIS6005
Computational Intelligence project. It performs one-record inference with the
verified production CatBoost model trained for Kaggle competition
`playground-series-s6e7`.

> Educational and research risk-screening demonstrator only. This output is not
> a medical diagnosis and must not replace advice from a qualified healthcare
> professional.

## Scope and privacy

The application requests only the 12 model features. It excludes `id` and
`gender`, does not request names or contact details, and does not write
prediction inputs to files, databases, or logs. Numeric ranges shown in the
interface are observed competition-data bounds, not clinical reference ranges.
Outputs are labelled model confidence scores because probability calibration
has not been established.

## Two application modes

The default **Use the model** mode is designed for non-technical users and
divides one prediction into four clear stages:

1. **Sleep and body** collects sleep duration, heart rate, BMI and sleep
   quality.
2. **Activity and daily habits** collects calorie expenditure, step count,
   exercise duration, water intake and physical activity level.
3. **Lifestyle and wellbeing** collects diet type, stress level and smoking
   and alcohol information.
4. **Review and result** shows all 12 responses before the verified production
   model is invoked.

Every field provides an **I don't know** choice. Back and Continue preserve
the entered values. The result presents the predicted competition category
first; all three model confidence scores remain available under **Show
confidence details**. **Start a new check** clears the temporary screen state
and returns to the first stage.

The **Implementation guide** mode provides assessor-facing evidence without
changing or bypassing the production inference path. It identifies the
application host, verifies the loaded runtime, maps the ordered function calls,
shows exact source segments, explains library responsibilities and—after a
prediction—reconstructs a 12-row live invocation trace from the current
in-memory session. Switching modes preserves the current stage, entered values
and result. Trace data is not written or logged.

The visible **Appearance** control provides matching accessible light and dark
presentations without relying on Streamlit's developer menu.

The application model is
`catboost_balanced_no_gender_production_all_train_v1.cbm`, a 343-tree CatBoost
classifier trained on all 690,088 labelled rows after the candidate was locked.
This deployment model is distinct from the later Kaggle-only ensemble; no
ensemble components are required to run the application.

## Project structure

Public source and evidence:

```text
app/streamlit_app.py       Streamlit user interface
app/presentation.py        Guided stages, friendly labels and payload ordering
app/guide_ui.py             Assessor guide and current-session trace display
app/demonstration.py        Verified metadata, call flow and source extraction
app/theme.py                Accessible paired light and dark themes
src/config.py              Paths and locked model constants
src/schema.py              Verified schema loading and contract checks
src/validation.py          Input validation and ordered DataFrame construction
src/inference.py           SHA-256 verification and CatBoost invocation
tests/                     Automated contract, inference, privacy and UI tests
reports/evidence/app/      Runtime metadata and generated test evidence
```

Private files, excluded by `.gitignore`:

```text
artifacts/private/models/catboost_balanced_no_gender_production_all_train_v1.cbm
artifacts/private/schema/production_inference_schema.json
artifacts/private/schema/feature-schema.json
artifacts/private/metadata/production_training_record.json
```

## Setup and operation

From the project root in PowerShell:

```powershell
python -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
& '.\.venv\Scripts\python.exe' -m pytest -v
& '.\.venv\Scripts\streamlit.exe' run app\streamlit_app.py
```

The application opens at `http://localhost:8501` and runs independently of
Google Colab. The private model and schemas must be present before startup.
They are intentionally excluded from this public repository because the
competition artefacts must not be redistributed.

## Exact functional flow

1. `render_app()` in `app/streamlit_app.py` displays the permanent disclaimer
   and calls `load_runtime()`.
2. `AppPaths.from_environment()` in `src/config.py` resolves private artifact
   paths. Optional environment variables can override them without changing
   source code.
3. `load_schema()` in `src/schema.py` reads the two JSON contracts. It rejects
   an unsupported schema version, reordered features, changed class order, or
   missing feature metadata.
4. `CatBoostPredictor.load()` in `src/inference.py` calls `sha256_file()` and
   compares the complete model digest with the locked SHA-256. It then invokes
   `CatBoostClassifier.load_model()`.
5. `GUIDED_STEPS` in `app/presentation.py` groups every locked feature exactly
   once for the three input stages. Streamlit keeps the current stage and
   entered responses in temporary session state.
6. `build_payload()` reconstructs the final mapping in
   `schema.feature_order`, regardless of the order in which controls were
   displayed. The review screen displays all 12 values before inference.
7. When **Show my result** is pressed,
   `CatBoostPredictor.predict()` calls
   `prepare_record()` in `src/validation.py`.
8. `prepare_record()` rejects missing or unexpected keys, non-finite or
   out-of-range numbers, and unknown categories. Missing numeric values become
   `numpy.nan`; missing categorical values become `__MISSING__`. Pandas creates
   a one-row DataFrame in the exact saved training order.
9. The predictor invokes CatBoost `predict_proba()` and `predict()`. The three
   scores are mapped in the verified class order: `at-risk`, `fit`,
   `unhealthy`.
10. Streamlit displays the predicted category and permanent disclaimer first.
    The ordered scores are available in a collapsed confidence-details panel,
    and verified implementation evidence is available in **Implementation
    guide**.

## Libraries and technical components

- Streamlit provides the form, safe messages, cached runtime, and local server.
- CatBoost loads the locked `.cbm` artifact and performs classification.
- pandas constructs the exact one-row tabular input expected by the model.
- NumPy represents numeric missingness and normalises model outputs for mapping.
- `hashlib` verifies the artifact before deserialisation.
- pytest and Streamlit AppTest verify configuration, schema, input processing,
  integrity failure, deterministic inference, direct CatBoost parity, privacy,
  guided navigation, value persistence, review content, missing-input support,
  reset behaviour, UI content, and successful prediction.

## Error handling

Schema or model integrity failures stop the application before inference and
show a controlled error. Invalid input is rejected before CatBoost is called.
CatBoost load or inference exceptions are converted to `ArtifactError`, so raw
stack traces and private input payloads are not displayed by application code.

## Practical demonstration and verification

Run:

```powershell
& '.\.venv\Scripts\python.exe' -m pytest --junitxml=reports\evidence\app\pytest-results.xml -v
```

The suite includes a direct parity check comparing application confidence
scores with a separately loaded `CatBoostClassifier.predict_proba()` call, a
determinism check, and a filesystem test confirming that prediction creates no
files.

The repeatable 5–7 minute assessor walkthrough is documented in
`docs/ASSESSOR_DEMONSTRATION.md`. The final evidence set also includes:

- `assessor-setup-runtime.png` for the verified runtime and local host;
- `assessor-function-flow.png` for the ordered invocation flow;
- `assessor-live-trace.png` for current inputs, prepared values and output;
- `assessor-dark-theme.png` for the accessible dark presentation.

Browser evidence for the practical demonstration is stored in
`reports/evidence/app/`:

- `guided-step-1.png` shows the introductory disclaimer, privacy message,
  progress indicator and first guided stage.
- `guided-review.png` shows grouped review cards generated from the 12 saved
  responses.
- `guided-result.png` shows the model category, non-diagnostic wording and
  expandable confidence-score presentation.

The flow was checked at 1280×720 and 375×812. The narrow viewport had no
horizontal overflow.
