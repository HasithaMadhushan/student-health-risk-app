# Two-Step Input Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the model form faster and easier through two steps, blank optional inputs, clear hints and practical numeric increments.

**Architecture:** Keep schema loading, validation and CatBoost prediction unchanged. Update presentation metadata and Streamlit state/rendering, then replace only the visual tokens in the CSS theme.

**Tech Stack:** Python, Streamlit, CatBoost, pytest, Streamlit AppTest, CSS

## Global Constraints

- Preserve all 12 features in saved training order.
- Blank or Not sure maps to existing missing-value handling.
- Keep the permanent disclaimer, privacy boundary and non-persistence.
- Do not claim unverified clinical units or ranges.
- Use the approved NHS-informed palette with WCAG 2.2 AA contrast.
- Keep 44-pixel targets, keyboard focus and responsive layout.

---

### Task 1: Two-step presentation contract

**Files:**
- Modify: `app/presentation.py`
- Modify: `tests/test_presentation.py`

**Interfaces:**
- Produces: `GUIDED_STEPS` with two `StepDefinition` objects covering every feature once

- [ ] Add a failing test asserting two steps, approved titles and exact feature groups.
- [ ] Run `pytest tests/test_presentation.py -q` and confirm it fails on three steps.
- [ ] Implement the two approved groups and friendly labels.
- [ ] Rerun the focused test and require it to pass.

### Task 2: Human-friendly inputs and review

**Files:**
- Modify: `app/streamlit_app.py`
- Modify: `tests/test_streamlit_app.py`

**Interfaces:**
- Consumes: two-step `GUIDED_STEPS`, schema ranges and existing payload builder
- Produces: blank numeric inputs with practical steps, clearer hints, two-step navigation and compact review on Step 2

- [ ] Add failing AppTests for two-step progress, blank numeric defaults, practical steps, Not sure options, 12-value Step 2 review and result/reset.
- [ ] Run focused AppTests and verify expected failures.
- [ ] Add display metadata for numeric labels, hints, formats and increments.
- [ ] Remove numeric missing checkboxes and treat blank as `None`.
- [ ] Add categorical Select an answer and Not sure handling.
- [ ] Put compact review and Get my result on Step 2; remove the third review state.
- [ ] Rerun Streamlit tests and require all to pass.

### Task 3: Accessible public-service palette

**Files:**
- Modify: `app/theme.py`
- Modify: `tests/test_theme.py`

**Interfaces:**
- Produces: consistent forced-light CSS using approved semantic tokens

- [ ] Add failing exact-token and contrast tests, including warning tokens under forced light.
- [ ] Run theme tests and confirm failure on the old palette.
- [ ] Implement the approved page, text, primary, success, warning, border, focus and error colors.
- [ ] Rerun theme and UI tests and require them to pass.

### Task 4: Documentation, live evidence and release

**Files:**
- Modify: `README.md`
- Modify: `docs/ASSESSOR_DEMONSTRATION.md`
- Modify: `reports/evidence/app/runtime-metadata.json`
- Replace: `reports/evidence/app/guided-step-1.png`
- Replace: `reports/evidence/app/guided-review.png`
- Replace: `reports/evidence/app/guided-result.png`

**Interfaces:**
- Produces: accurate two-step documentation and current deployed-style evidence

- [ ] Update setup, viva sequence and runtime metadata.
- [ ] Run the complete test suite, JSON parse, model SHA check and `git diff --check`.
- [ ] Render desktop and 375-pixel mobile flows; verify no overflow and sensible plus/minus behaviour.
- [ ] Commit, push, open a PR against `main`, merge and confirm the live deployment.
