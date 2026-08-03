# Calm Wellness UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the text-heavy student screen with a calm, compact and accessible wellness interface without changing inference behaviour.

**Architecture:** Keep the existing Streamlit wizard and production inference modules. Change only student-facing copy and the CSS palette/layout, with UI contract and contrast tests protecting the intended experience.

**Tech Stack:** Python, Streamlit, CSS, pytest, Streamlit AppTest

## Global Constraints

- Preserve the 12-feature schema, feature order, validation and CatBoost model.
- Keep the required non-diagnostic disclaimer and privacy statement visible.
- Do not add images, animation, navigation or a theme selector.
- Maintain WCAG AA contrast, visible focus and 44-pixel touch targets.
- Keep technical implementation details in the separate viva guide.

---

### Task 1: Compact student-facing hierarchy

**Files:**
- Modify: `tests/test_streamlit_app.py`
- Modify: `app/streamlit_app.py`

**Interfaces:**
- Consumes: existing `render_header()`, `render_progress()` and guided stages
- Produces: compact title/copy and one visible safety/privacy panel

- [ ] **Step 1: Write a failing AppTest assertion**

Assert that the app shows `Student Health Check`, `A quick four-step check`,
and one `Important information` disclosure while the old long introductory and
feature-standard sentences are absent.

- [ ] **Step 2: Run the focused test and verify RED**

Run `python -m pytest tests/test_streamlit_app.py::test_app_uses_compact_student_facing_copy -q` and confirm failure on the missing title.

- [ ] **Step 3: Implement minimal copy and hierarchy changes**

Replace the verbose header content with the approved compact heading and one
combined safety/privacy panel. Shorten stage and review instructions without
changing widget keys or navigation.

- [ ] **Step 4: Run Streamlit UI tests and verify GREEN**

Run `python -m pytest tests/test_streamlit_app.py -q` and require all tests to pass.

### Task 2: Calm accessible palette and surfaces

**Files:**
- Modify: `tests/test_theme.py`
- Modify: `app/theme.py`

**Interfaces:**
- Consumes: `ThemePalette`, `contrast_ratio()` and `build_theme_css("light")`
- Produces: warm neutral background, navy text, teal primary and compact card CSS

- [ ] **Step 1: Write failing palette tests**

Assert exact approved light tokens and contrast ratios of at least 4.5:1 for
body text/background and primary button text/background.

- [ ] **Step 2: Run focused theme tests and verify RED**

Run `python -m pytest tests/test_theme.py -q` and confirm failure against the old cyan palette.

- [ ] **Step 3: Implement palette and layout CSS**

Use warm off-white `#F7F8F4`, navy `#17324D`, teal `#187C72`, white surfaces,
sage `#EAF3EE`, border `#D8E2DC`, muted slate `#5F6F7A`, and compact spacing.
Style primary actions, inputs, alerts, cards and progress consistently.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run `python -m pytest tests/test_theme.py tests/test_streamlit_app.py -q` and require all tests to pass.

### Task 3: Evidence and release verification

**Files:**
- Modify: `README.md`
- Modify: `reports/evidence/app/runtime-metadata.json`

**Interfaces:**
- Consumes: completed UI and full test count
- Produces: accurate documentation and release evidence

- [ ] **Step 1: Update documentation**

Describe the compact wellness presentation and retain the separate viva guide.

- [ ] **Step 2: Run release checks**

Run the full pytest suite, `git diff --check`, parse runtime JSON, scan for
removed copy, and verify the model SHA-256 against runtime metadata.

- [ ] **Step 3: Commit and publish**

Commit the implementation to `simplify-health-check`, push it, and update pull
request #3.
