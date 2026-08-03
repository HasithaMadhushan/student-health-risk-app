# CIS6005 Practical Demonstration

## Purpose

This 5–7 minute walkthrough demonstrates that the application uses the
verified production CatBoost model, explains the exact implementation flow
and shows how a new record becomes a model output. Use only the safe
competition example values shown by the application.

## Before the demonstration

From the project root, run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app\streamlit_app.py
```

Confirm that the application opens locally. Do not show private dataset files,
credentials or personal information.

## Demonstration sequence

### 1. Establish the application purpose — 30 seconds

- Show the title, permanent non-diagnostic disclaimer and privacy statement.
- Explain that this is an educational Kaggle classifier, not a medical tool.
- Point out that no name, student ID, email or phone number is collected.

### 2. Demonstrate new-data input — 90 seconds

- Keep **Use the model** selected.
- Move through the three input stages.
- Explain that the controls are generated from the locked feature schema.
- Select **I don't know** for one numeric and one categorical field to
  demonstrate missing-value handling.
- Use **Back** once to show that current values remain in the session.
- On the review page, show that all 12 features are present before inference.

### 3. Demonstrate the production output — 45 seconds

- Select **Show my result**.
- Show the predicted competition category.
- Open **Show confidence details** and explain that the three values are model
  confidence scores, not calibrated probabilities.
- Reconfirm that the disclaimer remains visible.

### 4. Pinpoint setup and verified runtime — 60 seconds

- Switch to **Implementation guide**.
- In **Setup and application host**, identify
  `app/streamlit_app.py` and `render_app()` as the host.
- In **Verified runtime**, show the 343 trees, 690,088 training records,
  12 features, three ordered classes and complete SHA-256.
- Explain that startup rejects a model whose hash does not match the schema.

### 5. Navigate the exact function flow — 90 seconds

- Follow **Function invocation flow** from `render_app()` to
  `render_result()`.
- Open **Show exact code segments**.
- Point out:
  - `load_runtime()` loads the schema and verified model;
  - `CatBoostPredictor.predict()` coordinates inference;
  - `prepare_record()` validates and orders one record;
  - CatBoost `predict_proba()` and `predict()` create the scores and class;
  - `render_result()` presents the output and disclaimer.
- Explain the roles of Streamlit, CatBoost, pandas, NumPy and `hashlib`.

### 6. Demonstrate the live invocation trace — 60 seconds

- Show **12 inputs received** and **Prepared record: 1 × 12**.
- In the 12-row table, point out that numeric missingness becomes `NaN` and
  categorical missingness becomes `__MISSING__`.
- Show the exact ordered columns, experiment ID, model hash, predicted class
  and three scores.
- Explain that the trace is reconstructed from current in-memory values and is
  not persisted or logged.

### 7. Close with verification — 30 seconds

- Switch back to **Use the model** and show that the result remains.
- State that automated tests cover schema integrity, hash verification,
  missing-value processing, prediction parity, privacy and navigation.
- State the limitation: this proves a working competition application, not
  clinical validity.

## Excellent-criterion evidence map

| Marking requirement | Evidence to demonstrate |
|---|---|
| Clear and structured setup | Launch command and application host in section 1 |
| Pinpoint the ML application code | Exact host, loader, predictor, processor and result source segments |
| Understand function invocations | Ordered 11-step function flow |
| Navigate functional flow | Move from input controls through validation, CatBoost and output |
| Understand libraries | Library responsibilities section and exact runtime roles |
| Explain input/output processing | 12-row live trace, 1 × 12 shape, missing transformations and ordered scores |
| Outstanding practical demonstration | Real prediction, preserved state, verified hash and live current-session evidence |

## Evidence still requiring later replacement

- Add the final/private Kaggle leaderboard score and rank only after the
  competition closes and the result is verified.
- If the submitted report contains screenshots, capture the current final
  interface and label each figure with its demonstrated criterion.
