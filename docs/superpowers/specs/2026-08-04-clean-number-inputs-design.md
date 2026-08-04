# Clean Numeric Input Design

## Objective

Replace the visually weak native increment and decrement controls with simple,
professional numeric fields for non-technical student users. The change must
improve legibility and ease of entry without changing the saved schema,
validation rules, feature order, missing-value behaviour, or CatBoost inference
path.

## Approved interaction

- Numeric fields begin blank and accept direct keyboard or mobile numeric-keypad
  entry.
- Native increment and decrement buttons are hidden; users type the value they
  know.
- Every field retains a persistent visible label.
- Placeholders provide short examples where the feature name supports them:
  sleep duration, heart rate, BMI, step count, and exercise duration.
- Features whose units have not been independently verified use neutral wording
  such as `Enter value`; the interface must not invent clinical units.
- The existing two-step journey, Back behaviour, compact review, prediction,
  confidence details, reset and permanent disclaimer remain unchanged.

## Visual treatment

- Numeric inputs and select boxes use the same 52-pixel control height, white
  surface, dark text, 1.5-pixel slate border and 10-pixel corner radius.
- Empty placeholders use a readable secondary colour rather than near-white.
- Focus uses the existing high-visibility yellow outline with a blue border.
- Filled values use tabular numerals to prevent visual movement.
- Help icons are removed from individual numeric labels. One concise instruction
  above the group explains that users may leave unknown values blank.
- The established NHS-inspired blue, green, reduced-glare background and safety
  warning colours remain unchanged.

## Responsive behaviour

- Desktop retains the two-column form.
- Narrow layouts stack controls into one column without horizontal scrolling.
- Controls remain at least 44 pixels high and support keyboard focus.
- No hover-only information or precision tapping is required.

## Implementation boundaries

- `app/streamlit_app.py` continues to use `st.number_input`; only presentation
  metadata and help presentation change.
- `app/theme.py` hides the native number-input stepper buttons and supplies the
  unified input styling.
- No JavaScript component, additional dependency, persistence, logging or
  identifying field is introduced.
- `src/inference.py`, `src/validation.py`, saved schemas and the production model
  are not modified.

## Verification

- Automated tests confirm numeric inputs remain blank by default and no numeric
  help icons or stepper-button styling is exposed.
- Browser checks cover direct entry, Back-state preservation, review of all 12
  inputs, prediction, reset, keyboard focus, 390-pixel mobile width and desktop.
- Screenshots for Step 1, review and result are refreshed after verification.
- The production model SHA-256 must remain
  `ea5f6ea9b060720d063874f9ee6ab0aae7ed8367e94c1222ffe2608dbe990004`.

