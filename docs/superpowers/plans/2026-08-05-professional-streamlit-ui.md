# Professional Streamlit UI Implementation Plan

> **Superseding owner decision (5 August 2026):** Remove the former medical disclaimer and all technical footer metadata from every application state. This decision replaces every disclaimer/footer-retention instruction and example later in this historical plan; inference, privacy, validation, and fail-closed behaviour remain unchanged.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the prominent disclaimer-led interface with a polished, responsive two-step Streamlit experience while leaving the verified CatBoost inference contract unchanged.

**Architecture:** Keep `app/streamlit_app.py` as the UI orchestrator, `app/presentation.py` as the copy/feature-group source, and `app/theme.py` as the semantic CSS-token source. Preserve `src/` without modification; presentation tests drive copy and state changes, theme tests drive CSS changes, and the full existing suite protects inference, schema, validation, privacy, integrity, and deterministic behaviour.

**Tech Stack:** Python 3.13, Streamlit 1.60.0, CatBoost, pytest, Streamlit `AppTest`, semantic CSS embedded through `st.markdown`.

## Global Constraints

- Do not change the CatBoost model, model artefact, model loading, schema validation, feature order, prediction logic, class order, or confidence-score calculations.
- Do not add identifying fields or persist, save, cache, or log prediction input values.
- Call outputs **model confidence scores**, never calibrated probabilities.
- Preserve validation, missing-value handling, fail-closed artefact checks, navigation, reset, and deterministic prediction behaviour.
- Do not add external frontend frameworks or remove privacy/inference tests.
- Keep the two-step five-feature/seven-feature schema mapping exactly unchanged.
- Remove the full yellow **Important information** panel from every application state.
- Do not render the former medical disclaimer or technical project/model footer metadata in any state.
- Maintain accessible contrast, visible focus, 44 px minimum targets, reduced motion, and responsive desktop/tablet/mobile behaviour.

---

### Task 1: Establish the test environment and immutable artefact baseline

**Files:**
- Reference: `requirements.txt`
- Reference: `artifacts/private/models/catboost_balanced_no_gender_production_all_train_v1.cbm`
- Reference: `artifacts/private/schema/production_inference_schema.json`
- Reference: `artifacts/private/schema/feature-schema.json`

**Interfaces:**
- Consumes: repository requirements and ignored private runtime artefacts.
- Produces: a local `.venv`, a recorded baseline test result, and before-change SHA-256 values used again in Task 5.

- [ ] **Step 1: Create an isolated environment and install the locked requirements**

Run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Expected: installation exits with code 0 and installs `streamlit==1.60.0`, `pytest>=8,<9`, CatBoost, NumPy, and pandas.

- [ ] **Step 2: Record immutable file hashes before UI editing**

Run:

```powershell
Get-FileHash artifacts/private/models/catboost_balanced_no_gender_production_all_train_v1.cbm -Algorithm SHA256
Get-FileHash artifacts/private/schema/production_inference_schema.json -Algorithm SHA256
Get-FileHash artifacts/private/schema/feature-schema.json -Algorithm SHA256
```

Expected: the model hash is `EA5F6EA9B060720D063874F9EE6AB0AAE7ED8367E94C1222FFE2608DBE990004`; retain all three outputs for Task 5 comparison.

- [ ] **Step 3: Run the complete baseline suite**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -ra
```

Expected: capture the exact collected, passed, failed, skipped, and warning counts. Stop if existing failures prevent distinguishing redesign regressions.

### Task 2: Drive the requested copy, structure, and interaction hierarchy with failing tests

**Files:**
- Modify: `tests/test_presentation.py`
- Modify: `tests/test_streamlit_app.py`
- Modify: `app/presentation.py`
- Modify: `app/streamlit_app.py`

**Interfaces:**
- Consumes: `GUIDED_STEPS`, `build_payload`, existing session-state keys, `CatBoostPredictor.predict`, and `PredictionResult.confidence_scores`.
- Produces: the exact two-step copy, action hierarchy, result card text, review expander, compact permanent disclaimer/footer, and removal of the prominent yellow warning panel.

- [ ] **Step 1: Update the presentation contract test first**

Replace only the title assertions in `test_guided_steps_cover_each_locked_feature_once` while keeping its exact feature tuple assertions:

```python
assert tuple(step.title for step in GUIDED_STEPS) == (
    "Health-related inputs",
    "Daily routine inputs",
)
assert tuple(step.description for step in GUIDED_STEPS) == (
    "Complete the available fields. Optional numeric values may be left blank.",
    "Complete the remaining fields, review the record and generate a result.",
)
```

- [ ] **Step 2: Replace obsolete UI assertions and add absence checks**

Rename the disclaimer test to `test_app_uses_compact_disclaimer_and_has_no_identifying_fields` and assert:

```python
visible = " ".join(
    item.value
    for collection in (app.markdown, app.info, app.warning, app.caption)
    for item in collection
)
assert "Important information" not in visible
assert "Your answers stay in this session" not in visible
disclaimer_items = [item.value for item in app.markdown if DISCLAIMER in item.value]
assert len(disclaimer_items) == 1
assert 'class="medical-disclaimer"' in disclaimer_items[0]
assert not app.warning
```

Keep the existing identifying-field disjointness assertion unchanged. Update the two-step test to require the exact header, subtitle, step headings, and action labels:

```python
assert app.title[0].value == "Student Health Risk Prediction"
assert "Enter one record to generate a competition-model prediction." in stage_text(app)
assert "Step 1 of 2" in stage_text(app)
assert "Health-related inputs" in stage_text(app)
assert app.button(key="continue_button").label == "Continue"

app = reach_step_two(app)
assert "Step 2 of 2" in stage_text(app)
assert "Daily routine inputs" in stage_text(app)
assert app.button(key="back_button").label == "Back"
assert app.button(key="predict_button").label == "Generate prediction"
```

Update the review/result/reset assertions to require:

```python
assert any(item.label == "Review entered values" for item in app.expander)
assert "Prediction result" in stage_text(app)
assert "Predicted competition category" in stage_text(app)
assert "This category was generated by the trained competition model." in stage_text(app)
assert any(item.label == "View model confidence scores" for item in app.expander)
assert app.button(key="reset_button").label == "Start a new prediction"
assert "CIS6005 Computational Intelligence project" in " ".join(
    item.value for item in app.markdown
)
assert "Model family: CatBoost" in " ".join(item.value for item in app.markdown)
assert not app.warning
```

- [ ] **Step 3: Run the focused tests and verify the RED state**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_presentation.py tests/test_streamlit_app.py -q
```

Expected: failures report the old headings, old buttons, old result labels, the still-visible yellow warning panel, or the missing compact mandatory disclaimer. Failures must be assertion failures caused by the unimplemented design, not import or fixture errors.

- [ ] **Step 4: Implement the minimal copy and structure changes**

In `app/presentation.py`, change only the two `StepDefinition` titles and descriptions. In `app/streamlit_app.py`:

- remove the `st.warning` call while retaining the `DISCLAIMER` import for compact permanent footer rendering;
- set the page title and visible title to `Student Health Risk Prediction`;
- render the requested subtitle;
- make `render_progress` output only the step label, compact progress bar, heading, and supporting text once;
- change action labels to `Continue`, `Generate prediction`, `Back`, and `Start a new prediction`;
- rename the review expander to `Review entered values`;
- rename result content and confidence expander exactly as specified;
- keep `for label, score in result.confidence_scores.items()` unchanged to preserve saved model class order;
- add `render_footer()` and call it after Step 1, Step 2, fail-closed error display, and result rendering; render the exact `DISCLAIMER` in `.medical-disclaimer` content without a warning panel;
- retain keyed buttons, `store_visible_values`, `go_forward`, `go_back`, `reset_check`, `st.rerun`, and exception handling.

Use this footer implementation:

```python
def render_footer() -> None:
    st.markdown(
        f'<p class="medical-disclaimer">{DISCLAIMER}</p>'
        '<footer class="app-footer">'
        '<span>CIS6005 Computational Intelligence project</span>'
        '<span>Model family: CatBoost</span>'
        '</footer>',
        unsafe_allow_html=True,
    )
```

- [ ] **Step 5: Run the focused tests and verify the GREEN state**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_presentation.py tests/test_streamlit_app.py -q
```

Expected: all focused tests pass.

- [ ] **Step 6: Commit the behaviour-preserving UI structure**

```powershell
git add app/presentation.py app/streamlit_app.py tests/test_presentation.py tests/test_streamlit_app.py
git commit -m "feat: polish Streamlit content and result flow"
```

### Task 3: Drive the restrained responsive visual system with failing tests

**Files:**
- Modify: `tests/test_theme.py`
- Modify: `app/theme.py`

**Interfaces:**
- Consumes: `ThemePalette`, `contrast_ratio`, `build_theme_css`.
- Produces: accessible semantic tokens and responsive CSS for the centred form, cards, controls, progress, result, and footer.

- [ ] **Step 1: Replace the obsolete yellow-panel palette contract**

Update `test_public_service_health_palette_is_used` to assert the selected professional palette:

```python
assert LIGHT_THEME.primary == "#0F766E"
assert LIGHT_THEME.on_primary == "#FFFFFF"
assert LIGHT_THEME.background == "#F8FAFC"
assert LIGHT_THEME.foreground == "#0F172A"
assert LIGHT_THEME.surface == "#FFFFFF"
assert LIGHT_THEME.muted_surface == "#F1F5F9"
assert LIGHT_THEME.border == "#CBD5E1"
assert LIGHT_THEME.secondary_text == "#475569"
assert LIGHT_THEME.focus == "#0D9488"
```

Keep both existing WCAG ratio assertions. Remove assertions that require the yellow alert surface colours, while retaining generic error-component styling.

- [ ] **Step 2: Add a focused layout/CSS contract test**

Add:

```python
def test_professional_layout_is_centered_restrained_and_responsive():
    css = build_theme_css("light")
    assert "max-width: 56.25rem" in css
    assert "radial-gradient" not in css
    assert "linear-gradient" not in css
    assert "box-shadow: 0 6px 20px" in css
    assert "border-radius: 0.875rem" in css
    assert ".app-footer" in css
    assert "@media (max-width: 640px)" in css
    assert "min-height: 48px" in css
    assert "prefers-reduced-motion" in css
```

Update the existing CSS contract to continue requiring visible focus rules, selectbox/number-input styling, hidden number steppers, and 44 px minimum controls.

- [ ] **Step 3: Run the theme tests and verify the RED state**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_theme.py -q
```

Expected: failures identify the old blue/yellow palette, radial decoration, old container width, and missing footer styles.

- [ ] **Step 4: Implement semantic palette and component CSS**

In `app/theme.py`:

- set the approved light and complementary dark semantic tokens;
- set the main container to `max-width: 56.25rem` with balanced desktop/mobile padding;
- remove all decorative gradients;
- use consistent `0.875rem` control radius and `1rem` card radius;
- use a single subtle `0 6px 20px rgba(...)` card shadow;
- keep inputs at least 48 px high, labels visible, and focus rings 3 px;
- style the compact progress track without using colour as the only state signal;
- style `.app-footer` as a responsive, muted, bordered-top row;
- style `[data-testid="stMainBlockContainer"] .medical-disclaimer` with compact spacing, secondary colour, and at least `1rem` body text;
- preserve error component contrast, reduced-motion handling, dropdown legibility, and full-width mobile buttons;
- avoid selectors that hide labels, focus outlines, validation text, or Streamlit accessibility semantics.

- [ ] **Step 5: Run the theme tests and verify the GREEN state**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_theme.py -q
```

Expected: all theme tests pass, including contrast-ratio checks.

- [ ] **Step 6: Run all UI tests together**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_presentation.py tests/test_streamlit_app.py tests/test_theme.py -ra
```

Expected: all UI tests pass with zero failures.

- [ ] **Step 7: Commit the responsive visual system**

```powershell
git add app/theme.py tests/test_theme.py
git commit -m "style: add restrained responsive application theme"
```

### Task 4: Add explicit rerun, result-order, reset, and privacy regression coverage

**Files:**
- Modify: `tests/test_streamlit_app.py`
- Modify: `app/streamlit_app.py` only for compact mandatory disclaimer and safe fail-closed presentation requirements
- Preserve: `tests/test_inference.py`
- Preserve: `tests/test_privacy.py`

**Interfaces:**
- Consumes: keyed prediction/reset buttons, result session state, saved class order, and non-persistent predictor behaviour.
- Produces: test evidence that the redesign does not expose duplicate prediction actions, identifiers, payload metadata, or reordered confidence scores.

- [ ] **Global compatibility: preserve the mandatory compact disclaimer**

Assert the exact `DISCLAIMER` is rendered once with `.medical-disclaimer` styling in Step 1, Step 2, result, and fail-closed states. Assert the prominent yellow warning panel remains absent. Do not remove or weaken the required medical wording.

- [ ] **Step 1: Add result-state regression assertions**

Extend `test_result_is_simple_and_confidence_details_are_available`:

```python
assert all(button.key != "predict_button" for button in app.button)
assert len(app.progress) == 3
score_labels = [item.text for item in app.progress]
assert score_labels[0].startswith("At-risk:")
assert score_labels[1].startswith("Fit:")
assert score_labels[2].startswith("Unhealthy:")
```

If Streamlit 1.60.0 does not expose `Progress.text` through `AppTest`, assert the same order from the app's rendered caption/markdown collection without changing production order.

- [ ] **Step 2: Strengthen the review privacy assertion**

In the review test, assert that visible review text excludes internal metadata:

```python
review = " ".join(item.value for item in app.markdown)
for forbidden in ("model_sha256", "experiment_id", "artifacts/private", "student_id"):
    assert forbidden not in review
```

- [ ] **Step 3: Run the new assertions and verify they pass against the Task 2 implementation**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_streamlit_app.py tests/test_inference.py tests/test_privacy.py -ra
```

Expected: all tests pass. If the progress test fails because of the test API shape, inspect the real `AppTest` element interface and assert the rendered ordered labels; do not modify inference or confidence calculations.

- [ ] **Step 4: Commit the regression coverage**

```powershell
git add tests/test_streamlit_app.py
git commit -m "test: protect result order privacy and rerun behaviour"
```

### Task 5: Run full automated, artefact, and live application verification

**Files:**
- Verify: all repository files
- Do not modify: `src/`, `artifacts/`, training notebooks, model results, Kaggle files, or submission evidence

**Interfaces:**
- Consumes: completed UI implementation, full pytest suite, Streamlit runtime, and Task 1 hashes.
- Produces: exact test totals, unchanged artefact evidence, and verified Step 1/Step 2/result behaviour.

- [ ] **Step 1: Run formatting and diff safety checks**

Run:

```powershell
git diff --check
git status --short
git diff --name-only main...HEAD
```

Expected: no whitespace errors; changed production files are limited to `app/`; changed tests are limited to genuine UI expectations; `src/` and `artifacts/` are absent from the changed-file list.

- [ ] **Step 2: Recompute and compare immutable artefact hashes**

Run the three Task 1 `Get-FileHash` commands again.

Expected: every model/schema hash exactly matches its Task 1 value and the model remains `EA5F6EA9B060720D063874F9EE6AB0AAE7ED8367E94C1222FFE2608DBE990004`.

- [ ] **Step 3: Run the complete test suite with summary reporting**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -ra
```

Expected: exit code 0. Record the exact collected, passed, failed, skipped, and warning counts from this fresh output; never infer counts from earlier focused runs.

- [ ] **Step 4: Start the local application**

Run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py --server.headless true --server.address 127.0.0.1 --server.port 8501
```

Expected: Streamlit reports `http://127.0.0.1:8501` and no startup traceback.

- [ ] **Step 5: Verify Step 1 and responsive form behaviour**

At desktop and 375 px mobile widths, verify:

- title, subtitle, Step 1 label, heading, and supporting copy are exact;
- the yellow warning panel and old technical/session strings are absent while the exact compact mandatory medical disclaimer remains visible;
- five correctly mapped fields appear with blank numeric defaults and non-preselected categorical defaults;
- examples, labels, focus states, and Continue are readable and keyboard-operable;
- two columns collapse without horizontal scrolling.

- [ ] **Step 6: Verify navigation, Step 2, missing values, and invalid values**

Enter one Step 1 value, select Continue, return with Back, and confirm the value remains. Continue again and verify seven Step 2 fields, `Review entered values`, Back, and Generate prediction. Generate once with optional numeric values blank. Then enter an invalid/out-of-range value where the widget permits it and confirm concise error presentation without traceback or payload details.

- [ ] **Step 7: Verify result and reset behaviour**

Verify:

- a single Prediction result card appears after one submission;
- the predicted category is text-labelled;
- `View model confidence scores` contains exactly three ordered labelled rows: at-risk, fit, unhealthy;
- scores are called model confidence scores, not probabilities;
- `Review entered values` exposes only friendly labels/values;
- no Generate prediction button remains in the result state;
- Start a new prediction returns to a blank Step 1 state;
- the footer is present and low emphasis in every normal state.

- [ ] **Step 8: Verify privacy and unchanged runtime boundaries**

Search the changed files:

```powershell
rg -n -i "name|student.?id|email|phone|write_text|write_bytes|open\(|logging|print\(" app tests
```

Inspect each match. Expected: no identifying input labels, input persistence, payload logging, internal-path display, or new inference invocation path. Existing static project/model copy may contain the word `name` only in code identifiers unrelated to personal data.

- [ ] **Step 9: Commit any verification-only test corrections and report exact evidence**

If no corrections are needed, create no empty commit. Report:

- every modified file and its reason;
- final pytest collected/passed/failed/skipped/warning counts;
- live states and interactions verified;
- unchanged model/schema hashes;
- any unresolved failure, without bypassing or hiding it.
