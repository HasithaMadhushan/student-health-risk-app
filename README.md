# CIS6005 Student Health Risk Demonstrator

This private repository contains the Streamlit inference application for the
CIS6005 Computational Intelligence project. It uses the verified production
CatBoost model trained for Kaggle competition `playground-series-s6e7`.

> Educational and research risk-screening demonstrator only. This output is not
> a medical diagnosis and must not replace advice from a qualified healthcare
> professional.

## User experience and privacy

The application uses an accessible public-service health presentation for
non-technical users: reduced-glare grey, dark text, blue actions, green
progress and one concise safety/privacy panel. One health check has two steps:

1. **Your health basics**
2. **Your daily routine**, followed by a compact review and result action

Numeric fields start blank and categorical fields prompt for an answer or
**Not sure**. Practical increments make the `+` and `-` controls useful for
each feature. Back and Continue preserve temporary answers, and the Step 2
review shows all 12 model inputs before prediction. The
result displays the predicted competition category first; the three model
confidence scores are available in a collapsed panel. They are not described
as calibrated probabilities.

The app excludes `id` and `gender`, does not request identifying or contact
information, and does not write prediction inputs to files, databases or logs.
Displayed numeric limits are observed competition-data bounds, not clinical
reference ranges.

Technical assessor content is deliberately excluded from the student-facing
interface. A separate viva walkthrough is provided in
`docs/ASSESSOR_DEMONSTRATION.md`.

## Verified production runtime

- Model: `catboost_balanced_no_gender_production_all_train_v1.cbm`
- Experiment: `catboost_balanced_no_gender_production_all_train_v1`
- Trees: 343
- Training rows: 690,088
- Features: 12, excluding `gender`
- Classes: `at-risk`, `fit`, `unhealthy`
- SHA-256: `ea5f6ea9b060720d063874f9ee6ab0aae7ed8367e94c1222ffe2608dbe990004`

This deployment model is distinct from any later Kaggle-only ensemble.

## Project structure

```text
app/streamlit_app.py       Streamlit host, navigation and output UI
app/presentation.py        Friendly labels, guided stages and payload ordering
app/theme.py               Accessible student-facing visual theme
src/config.py              Paths, disclaimer and locked constants
src/schema.py              Saved schema loading and contract checks
src/validation.py          Input validation and ordered DataFrame creation
src/inference.py           SHA-256 verification and CatBoost prediction
tests/                     Automated schema, inference, privacy and UI tests
docs/ASSESSOR_DEMONSTRATION.md  Separate viva code walkthrough
reports/evidence/app/      Runtime metadata and interface evidence
```

Private deployment artifacts are stored under `artifacts/private/`. Do not
make this repository public while the model and schemas are tracked. Raw Kaggle
data and generated submission CSV files are not included.

## Setup and operation

From the project root in PowerShell:

```powershell
python -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
& '.\.venv\Scripts\python.exe' -m pytest -q
& '.\.venv\Scripts\streamlit.exe' run app\streamlit_app.py
```

The application opens at `http://localhost:8501` and does not depend on an
active Google Colab session.

## Exact inference flow

1. `render_app()` displays the header and calls cached `load_runtime()`.
2. `AppPaths.from_environment()` resolves the model/schema locations.
3. `load_schema()` checks schema version, feature order and class order.
4. `CatBoostPredictor.load()` verifies the model SHA-256 before loading it.
5. `GUIDED_STEPS` groups the 12 locked features across two input steps.
6. `build_payload()` restores exact training feature order.
7. **Get my result** invokes `CatBoostPredictor.predict()`.
8. `prepare_record()` validates values and creates a one-row pandas DataFrame.
9. CatBoost `predict_proba()` and `predict()` create scores and a class.
10. `render_result()` displays the category and optional confidence details.

Streamlit handles presentation and temporary state; CatBoost performs
classification; pandas builds the ordered record; NumPy represents numeric
missingness; `hashlib` verifies artifact integrity; pytest and Streamlit AppTest
verify the end-to-end contract.

## Evidence

The repeatable viva walkthrough is in `docs/ASSESSOR_DEMONSTRATION.md`.
Interface screenshots in `reports/evidence/app/` cover the first guided stage,
12-feature review and prediction result. The interface was previously checked
at desktop and narrow mobile viewports without horizontal overflow.
