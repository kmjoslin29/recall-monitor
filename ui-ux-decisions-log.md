# UI/UX Rules Pack: Decisions Log

Last updated: 2026-10-02 (decisions 1 to 105; see "Sync flag" below)
Purpose: the single record of what the owner has decided, so schema and rule drafting follow it. If this log and another document disagree, this log wins.

> **Sync flag (2026-10-02).** The rules pack (`rules-pack.zip`) cites decisions 106 to 112 (for example 106 rule ids never reused, 107 check structure, 108 features list, 109 tool profiles, 110 overridable params, 111 and 112). This copy of the log ends at 105. The newer rows are missing here and need to be merged in from wherever the owner keeps the master copy. No new numbers were assigned in this update, to avoid colliding with 106 to 112.

## Locked decisions

| # | Topic | Decision | Date |
|---|---|---|---|
| 1 | Platform | Web apps first, with mobile-friendly rules. Tools mostly hosted on GitHub (static hosting) and shared with friends | 2026-10-01 |
| 2 | Primary system | Material Design 3. Apple standards take over only if a tool becomes iOS-specific | 2026-10-01 |
| 3 | Layers | 1 Foundations, 2 Interaction patterns, 3 Pro-tool workflow heuristics, 4 Shareability (opted into per tool) | 2026-10-01 |
| 4 | Format | JSON rule entries plus generated Markdown. Checklist is the main use, advisory guidance secondary | 2026-10-01 |
| 5 | Severity tiers | Must / Should / Consider, attached to each rule. Must = WCAG A/AA, breaks the tool, or security (security added by decision 61) | 2026-10-01 |
| 6 | Accessibility baseline | WCAG 2.2 AA | 2026-10-01 |
| 7 | Contrast method | WCAG 2.x ratio as pass/fail, APCA Lc shown as information | 2026-10-01 |
| 8 | M3 Expressive | Borrow Expressive ideas where CSS can implement them | 2026-10-01 |
| 9 | Foundation order | Foundations, then forms and workflows, then the palette engine | 2026-10-01 |
| 10 | D1 Touch targets | Split accepted: Must 24 (WCAG 2.5.8), Should 48 (M3), Consider 44 (WCAG 2.5.5 AAA) | 2026-10-01 |
| 11 | D2 Motion default | Expressive scheme everywhere | 2026-10-01 |
| 12 | D3 Reduced motion | Tier is Should. Can be raised to Must later if needed | 2026-10-01 |
| 13 | D4 Breakpoints | All five M3 window size classes (compact < 600, medium 600 to < 840, expanded 840 to < 1200, large 1200 to < 1600, extra-large >= 1600) | 2026-10-01 |
| 14 | D5 Type scale | M3 baseline 15 styles adopted as the default | 2026-10-01 |
| 15 | D6 State layers | Hover 8%, focus 10%, pressed 10%, dragged 16% (disabled container 12%, content 38%). Accepted after a source check (see note). Confidence upgraded 2026-10-02 to Well-established for hover, focus, pressed, dragged and disabled content (read directly from Material Web's token file); the disabled container 12% is not in that file and stays unverified | 2026-10-01 (upgraded 2026-10-02) |
| 16 | O1 Compact density | Pro-tool layer gets a named compact density for controls. Floor stays at the WCAG 24px minimum with spacing; values set in decision 23 | 2026-10-01 |
| 17 | O2 Dense type | Smaller type variants included for dense tools, alongside the M3 baseline. Sizes set in decision 24 | 2026-10-01 |
| 18 | O3 Reduced motion | Under `prefers-reduced-motion`, keep opacity and color changes; drop movement and overshoot | 2026-10-01 |
| 19 | D7 Spacing unit | M3 8dp scale plus 4dp half-steps for icons, text alignment and inner padding | 2026-10-01 |
| 20 | D8 Shape scale | Core scale only (0, 4, 8, 12, 16, 28dp, full). Expressive additions (20, 32, 48dp) and shape morphing left out | 2026-10-01 |
| 21 | D9 Margins | 16dp compact, 24dp from medium up, 24dp spacer between panes | 2026-10-01 |
| 22 | D10 Elevation | Six levels at 0 / 1 / 3 / 6 / 8 / 12dp adopted. Shadow recipes set in decision 26 | 2026-10-01 |
| 23 | O4 Density values | Three densities. Default: 40dp control, 48dp target. Compact: 32px control (pro-tool panels). Dense: 24px control (tables, lists, icon strips). Spacing: 4dp within clusters, 8dp between groups, 12px horizontal padding at 32px height. Compact and dense apply only under `(pointer: fine)`; touch stays at default. Heights sourced from Carbon, Spectrum medium scale and Material density; spacing and pointer rule are our own proposals (speculative) | 2026-10-01 |
| 24 | O5 Dense type | Readable-text floor 12px; 11px allowed only for non-essential labels (M3 label small). Dense body 14px / 18px line height. Dense label 12px / 16px line height. Table row text 12px or 14px by row height | 2026-10-01 |
| 25 | WCAG 1.4.12 text spacing | Must: no container, including dense ones, may clip or overlap text when users apply WCAG text-spacing overrides (line height 1.5, paragraph spacing 2x, letter spacing 0.12em, word spacing 0.16em). Dense sizes must not use fixed heights that clip text | 2026-10-01 |
| 26 | O7 Elevation shadows | Our own labeled shadow recipes for the six levels for now; revisit if needed. Recipes must be marked as ours, not M3's | 2026-10-01 |
| 27 | Forms Q1 Label pattern | Top-aligned (adjacent) labels by default, with M3's in-container floating label allowed at default density only. M3 itself permits adjacent labels, so top-aligned is not a deviation | 2026-10-01 |
| 28 | Forms Q2 Validation timing | On blur plus on submit (rule F7); errors clear as soon as the value is valid | 2026-10-01 |
| 29 | Forms Q3 Error summary | Included as a Consider rule (F12). Source still unread; confidence Low | 2026-10-01 |
| 30 | Forms Q4 Conditional rules | F15 to F17 (input purpose, redundant entry, accessible authentication) kept as rules that switch on per tool (`applies_when` field in the schema) | 2026-10-01 |
| 31 | Forms Q5 Placeholder rule | F2 stays at Should | 2026-10-01 |
| 32 | F-Q7 Text field height | Text fields step one notch above other controls: 56dp at default (M3), 40dp compact, 32dp dense. Compact and dense text fields go below M3's 48dp target, which M3 warns about; this is why they stay opt-in (decision 35) | 2026-10-01 |
| 33 | F-Q8 Required marking | M3: asterisk on every required field plus one explanation (note at form start or supporting text). The `required` attribute and an accessible name including the asterisk stay. Replaces the Carbon minority-marking rule (F6) | 2026-10-01 |
| 34 | F-Q9 Text field variant | Follow M3: filled and outlined are equivalent in function; pick per tool by visual style, goals and distinctness from buttons and surroundings; one variant per region, never mixed in the same form. No project-wide default | 2026-10-01 |
| 35 | F-Q10 Density selection | Compact and dense are available only under `(pointer: fine)` and opted into by the person or tool through a visible control whose targets are at least 48px. Default is always standard density. Applies to text fields (M3) and, per option C, may differ for buttons and table rows: those can switch to compact automatically in pro-tool panels | 2026-10-01 |
| 36 | Workflows Q1 WCAG 3.3.4 scope | Work stored only in the browser (saved palettes, settings) is treated as in scope: rule U1 is a Must for those tools | 2026-10-01 |
| 37 | Workflows Q2 Default pattern | Undo-first for reversible actions; confirmation for irreversible ones (rules U2 and U3) | 2026-10-01 |
| 38 | Workflows Q3 Undo notice | Stays until dismissed or the next action. M3 agrees that a snackbar with an action stays until acted on or dismissed; the "or the next action" clearing is our addition (see addendum) | 2026-10-01 |
| 39 | Workflows Q4 Undo depth | Multi-level undo and redo for editing tools, plus a visible history list for pro tools (history list stays Consider: pro-tool convention not checked) | 2026-10-01 |
| 40 | Workflows Q5 Unsaved changes | Browser warning (`beforeunload`) only while unsaved changes exist | 2026-10-01 |
| 41 | Workflows Q7 Next-action clearing | Keep decision 38 as set: the undo snackbar clears on the person's next edit, with undo still reachable from the history list and by shortcut. Our extension of M3, flagged as a deviation | 2026-10-01 |
| 42 | Workflows Q8 Confirm buttons | Disable the confirming action only when a required choice is missing; never otherwise | 2026-10-01 |
| 43 | Workflows Q9 Inline feedback tier | Rule U12 (auto-dismissing messages also shown inline) stays at Should | 2026-10-01 |
| 44 | Workflows Q10 Dialog and snackbar accessibility | M3 dialog and snackbar accessibility sections read (pasted by the owner). The focus, keyboard and labeling rules in addendum section 5 (U5, U19 to U22) are proposals; approved in decision 45 | 2026-10-01 |
| 45 | Workflows area 1 rules approved | Owner approved U5 and U19 to U22 (snackbar announcement and focus, dialog keyboard and labeling, large-text fit, dialogs for critical information only) as written in the area 1 addendum, section 5 | 2026-10-01 |
| 46 | Workflows area 2 Q1 Non-drag set | Numeric text field beside every slider whose value matters, kept in sync both ways, plus keyboard operation (rules L4, L6). M3's slider page says the same: optional outside text field, slider and field update each other, Tab reaches the field directly after the slider | 2026-10-01 |
| 47 | Workflows area 2 Q2 Undo granularity | One undo entry per completed gesture, merging rapid repeats on the same control within a short window (L19). Window length not set: see O8 | 2026-10-01 |
| 48 | Workflows area 2 Q3 Escape cancels a drag | Adopted as a Consider rule (L20) | 2026-10-01 |
| 49 | Workflows area 2 Q4 Responsiveness | Interaction to Next Paint of 200 ms or better is a Should for all tools (L16). Drag-time update budgets are left to each tool's judgment | 2026-10-01 |
| 50 | Workflows area 2 Q5 Native or custom | Custom controls throughout, for consistent M3 styling. Consequence: custom sliders and pickers must expose name, role, value and state themselves (WCAG 4.1.2) and be keyboard operable (2.1.1); see addendum L25 | 2026-10-01 |
| 51 | Workflows area 2 Q7 Palette controls | The palette engine's direct manipulation is sliders and/or a two-dimensional picker (owner's current expectation; "I think") | 2026-10-01 |
| 52 | Area 2 Q8 Slider size by density | Default density M (40dp track, 52dp handle), compact S (24dp), dense XS (16dp), mirroring decision 23. Handle hit area follows decision 56 | 2026-10-01 |
| 53 | Area 2 Q9 Slider keys | M3's keys only: Tab to the handle, arrows change by one value or stop, Space plus arrows changes by a larger interval. APG's Home, End, Page Up and Page Down are not required. Arrow-key operation still meets WCAG 2.1.1. Flag: this departs from the ARIA Authoring Practices key set; the numeric field (decision 46) is the route to precise or distant values | 2026-10-01 |
| 54 | Area 2 Q10 2D picker | Allowed only when per-axis sliders are also on the page (rule L26 as the accessible interface for each axis) | 2026-10-01 |
| 55 | Area 2 Q11 Color descriptions | On hold until the palette project's lexicon draft has been read. The lexicon has now been read (addendum section 6); closed by decision 57 | 2026-10-01 |
| 56 | Area 2 Q12 Hit area | Rely on WCAG 2.5.8's equivalent-control exception where a numeric field is present on the same page and itself meets 24 by 24 px; otherwise the handle's hit area must be at least 24 px wide | 2026-10-01 |
| 57 | Area 2 Q13 Color descriptions | Adopted as a Consider rule (L27). The vocabulary is left open: a tool may use any description scheme (including React Aria's, or one derived from the palette lexicon). Numeric values stay alongside. Closes decision 55 | 2026-10-01 |
| 58 | Area 3 Q1 File route | Save to file and open from file for tools with presets or projects; optional for tools that only keep settings (rule S2) | 2026-10-01 |
| 59 | Area 3 Q2 Autosave | Autosave to browser storage plus explicit export (rule S6) | 2026-10-01 |
| 60 | Area 3 Q3 "Unsaved changes" | Means changed since the last file save. Interaction to watch: with autosave to browser storage (decision 59), the `beforeunload` warning of decision 40 will fire whenever changes have not been exported, even though they are autosaved; revisit if that proves noisy | 2026-10-01 |
| 61 | Area 3 Q4 Security tier | Rule S10 (treat imported files as untrusted) is a Must. Decision 5's definition of Must is extended: WCAG A/AA, breaks the tool, or security | 2026-10-01 |
| 62 | Area 3 Q5 Presets | Rule S13 kept as a Speculative Consider rule; no preset research for now | 2026-10-01 |
| 63 | Area 3 Q6 Restore on return | Decided per tool (rule S16) | 2026-10-01 |
| 64 | Area 3 Q7 Palette save format | Read in the palette pass, not now | 2026-10-01 |
| 65 | Area 4 Q1 Shortcut policy | Modifier combinations only (Ctrl or Cmd plus a key). No single-character shortcuts in our tools, which removes the WCAG 2.1.4 turn-off or remap burden. If a tool later needs single-key shortcuts, that is a new decision | 2026-10-01 |
| 66 | Area 4 Q2 Undo and redo keys | Ctrl or Cmd with Z for undo; Ctrl or Cmd with Shift with Z for redo; Ctrl with Y also on Windows. Conventions, not verified against a source | 2026-10-01 |
| 67 | Area 4 Q3 Snackbar focus shortcut | Adopt M3's example, Alt+G, to move focus to a snackbar with an action (rule U20). Not tested against browser collisions: Alt plus a letter can be an `accesskey` trigger in some Windows browsers (MDN), which we do not use (rule K8). Document it in the tool's shortcut help; revisit if a collision shows up | 2026-10-01 |
| 68 | Area 4 Q4 Platform labels | Detect the platform and show Ctrl or the Cmd symbol accordingly (K5) | 2026-10-01 |
| 69 | Area 4 Q5 Keyboard layouts | Use `KeyboardEvent.key` for letter shortcuts, and give critical commands a layout-independent route (arrow keys, digits or function keys) (K6) | 2026-10-01 |
| 70 | Area 4 Q6 Findability | Visible Shortcuts button, hints beside controls and in tooltips, and `aria-keyshortcuts` (K7). No command palette | 2026-10-01 |
| 71 | Area 4 Q7 Command access | Rule K13 (command palette) left as a Speculative Consider rule; no research | 2026-10-01 |
| 72 | Area 5 Q1 Progress indicators | Native `<progress>` styled with CSS where it can match M3. Where it cannot (for example M3's stop indicator or its grow-and-shrink indeterminate animation), a custom indicator is allowed and then must meet rule P5 (role, accessible name, value attributes). The fallback clause is my reading of "where it can match M3" | 2026-10-01 |
| 73 | Area 5 Q2 Duration thresholds | Keep Carbon's wording ("a few seconds") in rules P1 and P3. Flag: M3's progress page, pasted in the same message, gives concrete thresholds (see addendum, Q7); the owner may want those instead | 2026-10-01 |
| 74 | Area 5 Q3 Announcements | Announce start and finish (plus errors) only (rule P7) | 2026-10-01 |
| 75 | Area 5 Q4 Flashing | Rule P12 (WCAG 2.3.1) applied to automatic animation; user-driven scrubbing treated as out of scope. Caveat: W3C's page does not exempt user-initiated or gradual changes, so this is a scoping choice that could fail an audit, not a W3C exemption | 2026-10-01 |
| 76 | Area 5 Q5 Change feedback | Rule P14 stays a Consider rule | 2026-10-01 |
| 77 | Area 5 Q6 M3 progress guidance | M3 progress indicator guidance and specs pasted by the owner and read; findings in `ui-ux-workflows-5-addendum-v0.2.md` (proposals) | 2026-10-01 |
| 78 | Area 5 Q7 Thresholds | M3's numbers are the default in P1, P3 and P15: under 200 ms no indicator, 200 ms to 5 s a loading indicator, over 5 s a progress indicator. A tool may set its own thresholds. Supersedes decision 73 (Carbon's "a few seconds"). Note: waits over 5 s still need the P10 (WCAG 2.2.2) check | 2026-10-01 |
| 79 | Area 5 Q8 Wavy shape | Wavy active indicator allowed as an optional Expressive style, tier Consider (P22); flat is the baseline. Feasibility in CSS/SVG not yet verified (decision 8) | 2026-10-01 |
| 80 | Area 5 Q9 Reduced motion | Indeterminate indicators under `prefers-reduced-motion`: static indicator plus "Loading" text, with an optional opacity pulse (P23) | 2026-10-01 |
| 81 | Area 5 Q10 Approval | P16 to P21 approved as written (group indicator, one variant per process, accuracy and switching, contrast and stop indicator, button indicators, size and placement) | 2026-10-01 |
| 82 | Area 6 Q1 Empty-state anatomy | Adopt Carbon's three types (no data, user action, error) and one primary action per empty state (E2 to E4) | 2026-10-01 |
| 83 | Area 6 Q2 First-run policy | No intro by default; contextual cues in empty states; any intro must be brief, skippable and optional (E7 to E9). Evidence is NN/g mobile research (Supported, contested) | 2026-10-01 |
| 84 | Area 6 Q3 Starting state | Tools open blank with a helpful empty state, not sample data. E11 (sample or default state) is not adopted | 2026-10-01 |
| 85 | Area 6 Q4 Error tone | No apology in field and inline errors; "Sorry" allowed on whole-tool failure messages (E21) | 2026-10-01 |
| 86 | Area 6 Q5 Failure pages | Owner asked to verify and propose. GitHub Docs read: a custom page is a file named `404.html` (or `404.md` with `permalink: /404.html`) in the publishing source; the docs state no limits for project sites or subpaths, so behavior at a project-site subpath is unverified. Rule E26 drafted in the area 6 addendum, awaiting approval | 2026-10-01 |
| 87 | Area 6 Q6 M3 | Owner could not find an M3 page for this area. Area 6 rules rest on Carbon, GOV.UK, NN/g and WCAG; no M3 backing for them | 2026-10-01 |
| 88 | Area 6 Q7 Approval | E13 to E20 approved as written | 2026-10-01 |
| 89 | Area 6 Q8 Not-found page | Rule E26 (plain `404.html` with one link back) stays a Consider rule | 2026-10-01 |
| 90 | Area 7 Q3 Native share | Web Share API included as an enhancement (X8): feature-detect with `canShare()`, handle rejection, and always offer Copy link or a download as the fallback | 2026-10-01 |
| 91 | Area 7 Q5 CSV guarding | Rule X12 (guard against CSV formula injection) is a Should | 2026-10-01 |
| 92 | Area 7 Q6 Research | Research done on share and export patterns (Carbon community export pattern, Figma Help). Findings and new rules X15 (revised), X17 to X20 are in `ui-ux-workflows-7-addendum-v0.2.md`, awaiting approval (approved in decision 97) | 2026-10-01 |
| 93 | Area 7 Q1 Routes | Per tool: the shareability layer lists file, link, and image or text as options; each opt-in tool declares which it offers (X1, X2). The file route stays required for tools with presets or projects (decision 58) | 2026-10-01 |
| 94 | Area 7 Q2 Link state | Shared links carry state in the URL fragment only (X4). Still unverified: whether fragments appear in Referer, and URL length limits | 2026-10-01 |
| 95 | Area 7 Q4 Link as import | Opening a shared link is treated exactly like importing a file: untrusted input, security Must (decision 61), undo or confirm before replacing work (X7) | 2026-10-01 |
| 96 | Area 7 Q7 Approval | X3, X6, X9, X10, X13 and X14 approved as written. X6 stays Should because Referer behavior for fragments is unverified | 2026-10-01 |
| 97 | Area 7 Q8 New rules | X15 (revised), X17, X18, X19 and X20 approved at Consider | 2026-10-01 |
| 98 | Area 7 Q9 Confirmation | Owner answered "B" (change some) but gave explicit answers matching my four recommendations (Q1 C, Q2 A, Q4 A, Q7 approved). I logged the explicit answers as decisions 93 to 96 and asked what, if anything, B meant to change | 2026-10-01 |
| 99 | Palette Q1 Controls | Add per-axis sliders with numeric fields beside them (decisions 46, 50, 51, 52, 56), plus an optional 2D picker only alongside the sliders (decision 54). Whether the native color input stays as an extra route was not stated; assumed replaced, since decision 50 says custom controls throughout. Build is Sonnet work once the spec is settled | 2026-10-01 |
| 100 | Palette Q2 Undo unit | Every change to the project gets an undo entry: seed, supporting colors, locks, overrides and rationale notes (decisions 39, 47) | 2026-10-01 |
| 101 | Palette Q3 Leaving the page | Warn with `beforeunload` when the project has changed since the last project file save (decision 60 as written). Expect it to fire often, since the browser copy autosaves; revisit if noisy | 2026-10-01 |
| 102 | Palette Q4 New project | Keep the current timed click-again confirm. Flags kept open: it conflicts with decision 37 (undo-first) and may fall under WCAG 2.2.1 (applicability to a confirmation that expires is contested) | 2026-10-01 |
| 103 | Palette Q5 Format versions | New Should rule S17: a tool with a saved format adds a migration step before changing the saved shape (extends S9). Palette file is version 1 only today | 2026-10-01 |
| 104 | Palette Q6 Color descriptions | Describe colors with hue-family names plus plain lightness and chroma words, and also offer the nearest lexicon terms. The lexicon-term part is Speculative (the lexicon maps words to colors, not colors to words) and must be labeled so on the page. Applies L27 (decision 57) | 2026-10-01 |
| 105 | Palette Q7 Sharing routes | Palette offers text copy (hex values), an image of the palette, and a link carrying the seed and choices in the URL fragment, on top of the existing exports (decisions 93 to 97). Web Share and clipboard inside the claude.ai viewer are unverified and must be tested first | 2026-10-01 |

### Note on decision 15 (how the check went)
- Round 1 (2026-10-01): the Material Web token file could not be read directly, because GitHub blocked automated fetching. Every independent implementation found gave the same values. Confidence was held at "Supported, secondary".
- Round 2 (2026-10-02): `tokens/versions/latest/sass/_md-sys-state.scss` in `material-components/material-web` was read directly. It gives hover 0.08, focus 0.10, pressed 0.10, dragged 0.16 and disabled 0.38. Confidence for those values is upgraded to **Well-established**, with the owner's approval.
- Older Material systems used other values: 12% for focus and pressed in earlier M3 drafts and M2, and 4% hover in the legacy web switch. Those are outdated.
- The disabled container 12% is **not** in that file. It stays unverified, with the confidence it had before.

## Recall Monitor decisions (2026-10-02, numbers pending)
Owner choices made while auditing the US Food Recall Monitor against this log. Not numbered here because the pack already uses 106 to 112 (see Sync flag); assign numbers when the logs are merged.
- **Empty state, not sample data (applies decision 84).** Remove sample rows, the sample banner and the "Sample rows" chip from the built pages. With no data, show an empty state with one primary action. On a failed live fetch the mobile app shows an error state, or the last published snapshot if one exists. `fetch_recalls.py --sample` stays for testing only.
- **Native selects kept (exception to decision 50).** The owner chose native `<select>` for the filter and year fields for screen-reader and mobile-picker support. Per-tool exception; recorded in `tools/recall-monitor.json`.
- **Search field.** Outlined text field with a visible label above it (rules F1, F2, F21), matching the outlined selects.
- **Decision 15 upgrade approved** (see the note above).

## Open items awaiting the owner

| # | Question | Options |
|---|---|---|
| O8 | Undo merge window: how long (in seconds) rapid repeats on the same control are merged into one undo entry (decision 47) | To be set when history rules are drafted |
| O6 | Reduced-motion detail: should the fallback keep the *duration* of the effects curves (150 to 300 ms) or shorten it? | To be decided when motion rules are drafted |


## Not yet verified (carried forward)
- Spacing token steps, expanded / large / extra-large margins, shadow values, component default shapes (addendum sections list the confidence for each)
- Direct read of M3 spec pages (site is JavaScript-only)
- Apple HIG primary pages (needed only if a tool becomes iOS-specific)

## Related documents
- `ui-ux-source-map.md` (v0.1): sources by layer
- `ui-ux-foundations-v0.1.md`: constants with sources and confidence
- `ui-ux-forms-v0.1.md` and `ui-ux-forms-v0.2-addendum.md`: forms pass (v0.2 adds M3 text-field findings; F-Q7 to F-Q10 decided in 32 to 35)
- `ui-ux-palette-pass-v0.1.md`: palette pass (decisions 99 to 105)
- `ui-ux-workflows-7-sharing-export-v0.1.md` and `ui-ux-workflows-7-addendum-v0.2.md`: workflows area 7 (decisions 90 to 98)
- `ui-ux-workflows-6-empty-first-run-errors-v0.1.md` and `ui-ux-workflows-6-addendum-v0.2.md`: workflows area 6 (decisions 82 to 89)
- `ui-ux-workflows-5-feedback-status-v0.1.md` and `ui-ux-workflows-5-addendum-v0.2.md`: workflows area 5 (decisions 72 to 81)
- `ui-ux-workflows-4-keyboard-shortcuts-v0.1.md`: workflows area 4 (decisions 65 to 71)
- `ui-ux-workflows-3-saving-presets-v0.1.md`: workflows area 3 (decisions 58 to 64)
- `ui-ux-workflows-2-direct-manipulation-v0.1.md` and `ui-ux-workflows-2-addendum-v0.2.md`: workflows area 2 (decisions 46 to 57)
- `ui-ux-workflows-1-undo-history-v0.1.md` and `ui-ux-workflows-1-addendum-v0.2.md`: workflows area 1 (decisions 36 to 45)
- `ui-ux-foundations-v0.2-addendum.md`: closes spacing, shape, elevation, margins and the six W3C criteria; proposes D7 to D10 (the six W3C pages are now verified there)
