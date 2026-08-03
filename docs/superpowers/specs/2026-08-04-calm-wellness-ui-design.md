# Calm Wellness UI Design

## Goal

Make the Streamlit application feel calm, trustworthy and easy to use for a
non-technical student. Reduce visible text while preserving the permanent
non-diagnostic disclaimer, privacy protection, all 12 model inputs and the
verified production inference path.

## Visual direction

Use a restrained wellness palette:

- warm off-white page background;
- white cards and controls;
- deep navy primary text;
- muted slate secondary text;
- soft teal primary actions and progress;
- pale sage information surfaces;
- muted amber only for the medical disclaimer;
- red only for actionable errors.

The interface uses generous whitespace, rounded cards, subtle borders and a
small shadow scale. It must maintain WCAG AA text contrast, visible keyboard
focus and touch targets of at least 44 pixels.

## Information hierarchy

The first viewport contains only:

1. a compact product label;
2. the title **Student Health Check**;
3. one short supporting sentence;
4. one compact **Important information** panel containing the required
   non-diagnostic statement and a short privacy sentence;
5. the current step label, progress bar and first input card.

Remove repeated explanatory paragraphs, unresolved feature-unit commentary and
technical model metadata from the normal user journey. Keep technical evidence
in the separate viva guide.

## Guided input stages

Retain four stages: three data-entry stages followed by review/result. Each
stage shows one clear heading and a short instruction. Inputs remain generated
from the locked schema and retain **I don't know** handling.

Controls sit inside one white surface card. Labels remain visible. Primary
**Continue** and **Show my result** buttons use teal; **Back** is visually
secondary. Entered values remain in Streamlit session state between stages.

## Review and result

The review screen groups all 12 answers into three compact sections. It uses
short labels and values without extra instructional paragraphs.

The result screen leads with the predicted category in a distinct result card,
followed by one sentence explaining that it is a model-generated competition
category. Confidence scores remain behind the existing collapsed disclosure.
The disclaimer remains visible but compact. **Start a new check** is the only
primary follow-up action.

## Responsive behaviour

Use a centered content column with a readable maximum width. Desktop may place
related fields in two columns where Streamlit supports it; mobile remains a
single column with full-width controls and buttons. No horizontal scrolling is
permitted.

## Technical boundaries

- Do not change model, schema, feature order, validation or prediction logic.
- Do not add images, decorative animation, new navigation or theme selectors.
- Do not collect or persist identifying data.
- Keep the required disclaimer text unchanged in meaning and fully visible.
- Keep the separate viva implementation guide outside the application.

## Verification

Automated UI tests will assert the shorter student-facing hierarchy, absence of
removed technical copy, all four stages, all 12 reviewed features, successful
production prediction, confidence disclosure, reset, privacy and disclaimer.
Theme tests will verify accessible contrast for the new palette. The full test
suite and locked model SHA-256 check must pass before publishing.
