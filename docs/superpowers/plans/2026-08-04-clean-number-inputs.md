# Clean Numeric Inputs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the low-contrast native numeric steppers with clean, directly typed fields while preserving the verified two-step CatBoost application.

**Architecture:** Keep Streamlit's native `st.number_input` widgets for schema-compatible numeric entry and accessibility. Move all presentation changes into input metadata and theme CSS; inference, validation, schema order and session-state flow remain unchanged.

**Tech Stack:** Python 3.12, Streamlit 1.60, pytest, Streamlit AppTest, CSS.

## Global Constraints

- Numeric inputs remain blank by default and missing values remain supported.
- Do not add dependencies, JavaScript components, persistence or identifying fields.
- Do not modify `src/inference.py`, `src/validation.py`, saved schemas or the production model.
- Do not invent clinical units for unresolved competition features.
- All visible controls must remain at least 44 pixels high with keyboard focus.

---

### Task 1: Direct-entry numeric field contract

**Files:**
- Modify: `tests/test_streamlit_app.py`
- Modify: `app/streamlit_app.py`

**Interfaces:**
- Consumes: `NumericInputDisplay` and `render_numeric_input(name, spec)`.
- Produces: blank direct-entry `st.number_input` widgets without per-field help icons.

- [ ] **Step 1: Write the failing tests**

Add assertions that each numeric widget has `help is None`, remains blank, and exposes the approved concise placeholder. Remove the increment/decrement behavioural test because direct typing is the approved interaction.

- [ ] **Step 2: Run the focused tests and verify RED**

Run `python -m pytest tests/test_streamlit_app.py::test_numeric_inputs_start_blank_without_ambiguous_checkboxes tests/test_streamlit_app.py::test_numeric_inputs_use_clean_direct_entry -q` and confirm failure because numeric widgets still receive `help_text`.

- [ ] **Step 3: Implement the minimal metadata change**

Remove `help_text` from `NumericInputDisplay`, stop passing `help=` to `st.number_input`, and use examples only where supported by feature names: `e.g. 7.5 hours`, `e.g. 72 bpm`, `e.g. 24.5`, `Enter value`, `e.g. 8000`, `e.g. 30 minutes`, `Enter value`.

- [ ] **Step 4: Run the focused tests and verify GREEN**

Run the two focused tests again and confirm both pass.

- [ ] **Step 5: Commit**

Commit `app/streamlit_app.py` and `tests/test_streamlit_app.py` with message `Simplify numeric field guidance`.

### Task 2: Unified accessible field styling

**Files:**
- Modify: `tests/test_theme.py`
- Modify: `app/theme.py`

**Interfaces:**
- Consumes: `build_theme_css(theme_override)`.
- Produces: CSS that hides native steppers and styles number and select inputs consistently.

- [ ] **Step 1: Write the failing CSS contract test**

Assert that generated CSS contains the exact selectors for `[data-testid="stNumberInput"] button { display: none !important; }`, readable placeholders, 52-pixel input height, tabular numerals and matching select controls.

- [ ] **Step 2: Run the focused test and verify RED**

Run `python -m pytest tests/test_theme.py::test_clean_numeric_input_css_contract -q` and confirm failure because stepper hiding and the unified field contract are absent.

- [ ] **Step 3: Implement the CSS contract**

Hide native number-input buttons, give number/select groups a white surface, `1.5px` slate border, `10px` radius and `52px` minimum height, set placeholder text to the secondary colour, use tabular numerals, and retain the existing yellow focus outline with blue focus border.

- [ ] **Step 4: Run theme and Streamlit tests and verify GREEN**

Run `python -m pytest tests/test_theme.py tests/test_streamlit_app.py -q` and confirm all focused tests pass.

- [ ] **Step 5: Commit**

Commit `app/theme.py` and `tests/test_theme.py` with message `Polish numeric input styling`.

### Task 3: Evidence, documentation and release verification

**Files:**
- Modify: `README.md`
- Modify: `docs/ASSESSOR_DEMONSTRATION.md`
- Modify: `reports/evidence/app/runtime-metadata.json`
- Modify: `reports/evidence/app/guided-step-1.png`
- Modify: `reports/evidence/app/guided-review.png`
- Modify: `reports/evidence/app/guided-result.png`

**Interfaces:**
- Consumes: completed application and production artefacts.
- Produces: assessor-ready documentation and current browser evidence.

- [ ] **Step 1: Update user and assessor documentation**

Replace references to plus/minus increments with direct numeric entry, readable placeholders and the unchanged 12-feature review/prediction flow.

- [ ] **Step 2: Run the full automated suite**

Run `python -m pytest -q`; expected result is all tests passing with zero failures.

- [ ] **Step 3: Run browser verification**

Verify direct numeric entry, Back-state preservation, all 12 review labels, prediction, confidence details, reset, desktop layout and 390-pixel mobile layout without horizontal overflow.

- [ ] **Step 4: Refresh evidence**

Capture Step 1, expanded review and result screenshots and update runtime metadata with the verified behaviours and current test count.

- [ ] **Step 5: Verify protected artefacts and repository quality**

Confirm `git diff --check` succeeds and the production model SHA-256 remains `ea5f6ea9b060720d063874f9ee6ab0aae7ed8367e94c1222ffe2608dbe990004`.

- [ ] **Step 6: Commit**

Commit documentation and evidence with message `Refresh clean input evidence`.

