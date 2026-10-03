# Checklist: US Food Recall Monitor

Generated from the rules pack (UI/UX rules pack 0.1.0). Do not edit by hand; change the JSON and regenerate.
Baseline: WCAG 2.2 AA (decision 6); Material Design 3 as the primary system (decision 2).
Areas not loaded yet: foundations, undo-history, direct-manipulation, saving, keyboard, feedback-status, empty-errors, sharing.

- Tiers: **MUST** = WCAG 2.2 A/AA, breaks the tool, or security (decisions 5, 61). **SHOULD** = M3 or strong guidance; deviate only on purpose. **CONSIDER** = helpful, optional or contested.
- Confidence: Well-established · Supported, contested · Low confidence · Speculative (decision 111).
- Rules marked *(proposed)* are not approved yet (decision 112).

## Tool profile

Features: Forms and text fields, Opens files, CSV export, Long operations.

### Tool choices

- **Select controls:** Keep native <select> elements for the filter and year fields, for screen-reader and mobile-picker support. Labels sit above the fields. (decision 50)
- **Search field:** Outlined text field with a visible "Search" label above it; the placeholder is a hint only. Matches the outlined selects (one text-field variant per region).
- **First run and no data:** Pages open to an empty state with one primary action (refresh or load a file). Sample rows are never shown; on a failed live fetch the mobile app shows an error state, or the last published snapshot if one exists. (decision 84)
- **Loading feedback:** Native <progress> on the mobile Refresh: indeterminate from 200 ms, determinate (sources finished of 2) after 5 s. Start, finish and failure are announced through a polite live region. (decision 78)
- **Opened files:** A loaded file must be an array of objects with recall_id, agency and classification, or it is rejected and the current data is kept. Every field is HTML-escaped and only https links render. (decision 95)
- **CSV export:** Cells starting with = + - @ tab or CR are prefixed with an apostrophe. (decision 91)
- **Restore on return:** Not applicable: the tool keeps no work in browser storage.
- **Large and extra-large margins:** Reuse the 24dp medium-and-up margin; the spec values for these window size classes are not verified. (decision 13) *(open)*

## Layer 2 · Interaction patterns · Forms

### F1 Every input has a visible, persistent label *(proposed)*

- [ ] **MUST** F1.1 Every input has a visible text label that stays visible while typing and after a value is entered.
  WCAG 3.3.2 (A) · Well-established · Check: manual · Applies to: Forms and text fields

### F2 Placeholders are never the label

- [ ] **SHOULD** F2.1 A placeholder is never the only label and never holds essential information.
  Low confidence · Check: code review · Applies to: Forms and text fields

### F3 The visible label is part of the accessible name *(proposed)*

- [ ] **MUST** F3.1 Each control's accessible name contains its visible label text.
  WCAG 2.5.3 (A) · Well-established · Check: automated · Applies to: Forms and text fields

### F4 Labels are programmatically associated *(proposed)*

- [ ] **MUST** F4.1 Every label is associated with its control (&lt;label for&gt;, or fieldset and legend for groups).
  WCAG 1.3.1 (A) · Well-established · Check: automated · Applies to: Forms and text fields

### F5 Helper text is short, below the field, and linked *(proposed)*

- [ ] **SHOULD** F5.1 Helper text is short, sits below its field, and is visible at least while the field is focused.
  Well-established · Check: manual · Applies to: Forms and text fields
- [ ] **SHOULD** F5.2 Helper text is linked to its input with aria-describedby.
  Low confidence · Check: automated · Applies to: Forms and text fields

### F7 Validate on blur and on submit

- [ ] **SHOULD** F7.1 Client-side checks run when the person leaves a field and again on submit; server or whole-form checks run on submit.
  Low confidence · Check: manual · Applies to: Forms and text fields
- [ ] **SHOULD** F7.2 An error clears as soon as the value becomes valid.
  Low confidence · Check: manual · Applies to: Forms and text fields

### F8 Errors are identified in text *(proposed)*

- [ ] **MUST** F8.1 Every detected error is described in text that names the field and the problem; color or an icon alone is never the only cue.
  WCAG 3.3.1 (A) · Well-established · Check: manual · Applies to: Forms and text fields

### F9 Error messages suggest the fix *(proposed)*

- [ ] **MUST** F9.1 When a fix is known, the error message suggests it, unless that would jeopardize security or purpose.
  WCAG 3.3.3 (AA) · Well-established · Check: manual · Applies to: Forms and text fields

### F10 Errors are exposed to assistive technology *(proposed)*

- [ ] **MUST** F10.1 Error messages are announced to assistive technology without taking focus.
  WCAG 4.1.3 (AA) · Well-established · Check: screen reader · Applies to: Forms and text fields
- [ ] **SHOULD** F10.2 A field in error has aria-invalid="true", its message is linked with aria-describedby, and the message sits in a live region: role="alert" for errors, role="status" for non-error results.
  Low confidence · Check: automated · Applies to: Forms and text fields

### F11 Do not disable submit to block invalid input *(proposed)*

- [ ] **SHOULD** F11.1 On long forms, the submit button is not disabled to block invalid input.
  Low confidence · Check: manual · Applies to: Forms and text fields · When: Long forms.

### F12 Error summary on failed submit

- [ ] **CONSIDER** F12.1 On a failed submit, an error summary at the top of the form links to each field in error, and focus moves to the summary.
  Low confidence · Check: manual · Applies to: Forms and text fields

### F14 No unexpected change of context on input *(proposed)*

- [ ] **MUST** F14.1 Changing a control's value does not cause an unexpected change of context (auto-submit, navigation, a new window, a focus jump) unless the person was told beforehand.
  WCAG 3.2.2 (A) · Well-established · Check: manual · Applies to: Forms and text fields

### F18 Single column by default *(proposed)*

- [ ] **SHOULD** F18.1 Fields sit in a single column; fields are side by side only when they belong together.
  Low confidence · Check: manual · Applies to: Forms and text fields

### F19 Labels above fields

- [ ] **SHOULD** F19.1 Labels sit above their fields; an in-container floating label appears only at default density.
  Well-established · Check: manual · Applies to: Forms and text fields

### F21 One text field variant per region

- [ ] **SHOULD** F21.1 Within one region or form, text fields use a single variant (filled or outlined).
  Well-established · Check: manual · Applies to: Forms and text fields

### F22 Outlined field contrast *(proposed)*

- [ ] **MUST** F22.1 An outlined field's container outline has at least 3:1 contrast against the background.
  WCAG 1.4.11 (AA) · Well-established · Check: automated · Applies to: Forms and text fields

### F23 Labels are short and shown in full *(proposed)*

- [ ] **SHOULD** F23.1 Label text is short, never truncated, and never wraps to more than one line.
  Well-established · Check: manual · Applies to: Forms and text fields

### F24 Required fields carry an asterisk

- [ ] **SHOULD** F24.1 Every required field shows an asterisk next to its label, and the asterisk is explained once, in supporting text or in a note at the start of the form.
  Well-established · Check: manual · Applies to: Forms and text fields
- [ ] **SHOULD** F24.2 Required fields have the HTML required attribute, and their accessible name includes the asterisk.
  Well-established · Check: automated · Applies to: Forms and text fields
- [ ] **SHOULD** F24.3 If the required-field note has a color, the asterisk uses the same color.
  Well-established · Check: manual · Applies to: Forms and text fields

### F25 Error text replaces supporting text *(proposed)*

- [ ] **SHOULD** F25.1 Error text replaces the supporting text in the same place; the two are not shown together.
  Well-established · Check: manual · Applies to: Forms and text fields
- [ ] **SHOULD** F25.2 Error text says how to avoid the error; when several errors are possible, it addresses the most likely one.
  Well-established · Check: manual · Applies to: Forms and text fields
- [ ] **SHOULD** F25.3 Space between fields leaves room for an error message to wrap to a second line.
  Well-established · Check: manual · Applies to: Forms and text fields

### F26 Error icon in the error state *(proposed)*

- [ ] **SHOULD** F26.1 The error state shows an error icon as well as color and text; an icon without an action has the accessible label "Error".
  Well-established · Check: manual · Applies to: Forms and text fields

### F27 Accessible text for supporting text and counters *(proposed)*

- [ ] **SHOULD** F27.1 Supporting text has its own accessible text, and a character counter reads like "Character count, 5/20".
  Well-established · Check: screen reader · Applies to: Forms and text fields

### F28 Supporting text and counters *(proposed)*

- [ ] **SHOULD** F28.1 Supporting text is ideally one line and is either always visible or visible on focus.
  Well-established · Check: manual · Applies to: Forms and text fields
- [ ] **SHOULD** F28.2 A field with a character or word limit shows a counter of used and total.
  Well-established · Check: manual · When: Fields with a character or word limit. · Applies to: Forms and text fields

### F29 Icons inside fields *(proposed)*

- [ ] **MUST** F29.1 Interactive icons inside fields have an accessible name that says what they do and a role, such as a "Show password" button.
  WCAG 4.1.2 (A) · Well-established · Check: automated · Applies to: Forms and text fields
- [ ] **SHOULD** F29.2 A clear icon appears only when the field has text.
  Well-established · Check: manual · Applies to: Forms and text fields
- [ ] **SHOULD** F29.3 Images inside fields are 24dp high.
  Well-established · Check: code review · Applies to: Forms and text fields

### F30 Prefix and suffix text is announced *(proposed)*

- [ ] **SHOULD** F30.1 Prefix and suffix text has its own accessible text.
  Well-established · Check: screen reader · Applies to: Forms and text fields

### F31 Read-only fields *(proposed)*

- [ ] **SHOULD** F31.1 Read-only fields look like regular fields and are clearly labeled as read-only.
  Well-established · Check: manual · Applies to: Forms and text fields

### F32 Fixed-height text areas on the web *(proposed)*

- [ ] **SHOULD** F32.1 Long input uses a fixed-height text area, not an auto-growing multi-line field, and its height fits within mobile screens.
  Well-established · Check: manual · Applies to: Forms and text fields

### F33 Adaptive field width *(proposed)*

- [ ] **SHOULD** F33.1 From medium windows up, fields are bounded by flexible margins or containers, margins are not kept fixed as layouts grow, and fields are never full width on large screens.
  Well-established · Check: manual · Applies to: Forms and text fields

### F34 Every field state is visible *(proposed)*

- [ ] **SHOULD** F34.1 Each field has visible enabled, hovered, focused, disabled and error states, in empty and populated versions.
  Well-established · Check: manual · Applies to: Forms and text fields
- [ ] **SHOULD** F34.2 Field colors follow M3 roles: filled uses surface container highest for the container and on surface variant for label and icons; outlined uses outline for the container; both use primary when focused.
  Well-established · Check: code review · Applies to: Forms and text fields

### F35 Text field measurements *(proposed)*

- [ ] **SHOULD** F35.3 Horizontal padding is 16dp without icons and 12dp with icons, with 16dp between an icon and the text.
  Well-established · Check: code review · Applies to: Forms and text fields
- [ ] **SHOULD** F35.4 Supporting text and the counter have 4dp of top padding and 16dp between them.
  Well-established · Check: code review · Applies to: Forms and text fields
- [ ] **SHOULD** F35.5 The filled variant has 8dp top and bottom padding; the outlined variant's populated label has 4dp left and right padding.
  Well-established · Check: code review · Applies to: Forms and text fields

### F36 Text field density is opt-in

- [ ] **SHOULD** F36.1 Text fields use standard density by default; compact and dense are switched on by the person or the tool, never applied by default.
  Well-established · Check: manual · Applies to: Forms and text fields
- [ ] **SHOULD** F36.3 Compact and dense are offered only under a fine pointer ((pointer: fine)); touch stays at standard density.
  Speculative · Check: manual · Applies to: Forms and text fields

### F37 Text field height by density

- [ ] **SHOULD** F37.1 At default density, the text field container and its target are 56dp high.
  Well-established · Check: code review · Applies to: Forms and text fields

## Not applicable to this tool

Rules whose features the tool does not declare: F13, F15, F16, F17.

---
45 checks.
