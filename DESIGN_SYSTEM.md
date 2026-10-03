# Design system — Material Design 3

Both web outputs (`docs/dashboard.html` and `docs/index.html`) follow Google's
Material Design 3 (M3). This page records where each value comes from, how it
was checked, and where the design intentionally departs from the spec.

## Sources

- **Color** — generated with Google's
  [`material-color-utilities`](https://github.com/material-foundation/material-color-utilities)
  (`SchemeTonalSpot`, seed `#0F5C6E`, the tracker's original teal). Light and
  dark schemes are both included and follow the device setting
  (`prefers-color-scheme`).
- **Shape, state, type, motion** — Google's
  [`material-web`](https://github.com/material-components/material-web) token
  files (`tokens/versions/latest`). m3.material.io is JavaScript-rendered, so
  the token source is the machine-readable reference.
- **Layout and accessibility** — m3.material.io Layout (window size classes)
  and Accessibility (touch targets) guidance.

To regenerate colors from a different seed, run `SchemeTonalSpot` with the new
hex and replace the `--md-*` values at the top of the `<style>` block in
`build_dashboard.py` and `build_mobile.py`.

## What's applied

| Area | M3 guidance | Implementation |
|---|---|---|
| Color roles | primary, surface, surface-container-*, outline-variant, error-container… | CSS custom properties `--md-*` |
| Dark theme | M3 defines paired light/dark schemes | automatic via `prefers-color-scheme` |
| Shape | corner scale 4/8/12/16/28/full | selects 4, chips 8, cards 12, list/filter panel 16, buttons full |
| State layers | hover 8%, focus 10%, pressed 10% | `.sl` overlay using `currentColor` |
| Focus | 3px indicator, 2px outer offset | `:focus-visible` ring in `secondary` |
| Buttons | 40dp container, full corner, label-large | filled / tonal / outlined / text variants |
| Touch targets | ≥48×48dp, ~8dp apart | buttons and chips extend their hit area to 48dp |
| Progress indicator | linear, 4dp, primary on surface-container-highest | native `<progress>` on the mobile Refresh; indeterminate from 200 ms, determinate after 5 s; start/finish announced via a polite live region |
| Empty / error state | what happened, why, one primary action | shown when no data is loaded or a live fetch fails; never substitutes sample rows |
| Text fields | outlined, 56dp, extra-small corner, visible label | filter `<select>`s and the search field (one text-field variant per region) |
| Cards | outlined card, medium (12dp) corner, 1dp outline-variant | KPIs and chart panels |
| Lists | one-line 56dp, two-line 72dp, three-line 88dp | desktop rows 56dp; compact 72dp; mobile 88dp |
| Type scale | display → label roles | headline, title, body, label roles |
| Motion | standard easing `cubic-bezier(0.2,0,0,1)`, short4 200ms | state layers; chevron uses an Expressive-style spring approximated with CSS `linear()`; under reduced motion movement is dropped and opacity/color changes stay |
| Layout | five window size classes: compact <600, medium 600–839, expanded 840–1199, large 1200–1599, extra-large ≥1600 | desktop: single pane below 840, two panes from 840, content max-width 1280px (1560px at ≥1600). Margins: 16dp compact, 24dp medium and up. Large/extra-large margins are **not verified** against the spec. Mobile app keeps a fixed 840px reading column on purpose. |

## Verification

- **axe-core (WCAG 2.2 AA, incl. target-size):** 0 violations on both pages,
  light and dark, populated and empty states, at 1280/1700px (desktop) and 390/320px (mobile).
- **Text spacing (WCAG 1.4.12):** line-height 1.5, letter-spacing 0.12em, word-spacing 0.16em, paragraph spacing 2x applied in a browser test; no clipped controls and no horizontal overflow at 320px.
- **Security:** every record field is HTML-escaped before rendering, only `https:` source links render, loaded files are shape-checked, and CSV exports prefix cells starting with `= + - @` with `'` (formula injection).
- **Contrast (computed from the tokens):** body text 8.4–16:1; severity labels
  ~4.8:1 (light) and ~8.7:1 (dark) against their containers — all above the
  4.5:1 text minimum. axe can't reliably test text inside SVG charts, so chart
  labels rely on this token math (on-surface-variant on surface ≥ 8.4:1).
- **Overflow:** no horizontal page overflow at 320, 390, and 700px.

## Intentional deviations

1. **Typeface.** M3's baseline is Roboto, but no webfont is loaded so the files
   stay offline and self-contained. The stack lists Roboto first and falls back
   to the system sans (Segoe UI on Windows, SF on iOS).
2. **Native selects.** M3 describes custom menus for select. Native `<select>` is kept for screen-reader and mobile-picker support (a choice recorded by the owner). Labels sit above fields, which M3 permits as an adjacent label, so that part is not a deviation.
3. **Static tags.** Agency, status, and "confounder" labels are chip-shaped but
   non-interactive. M3 chips are interactive and M3 badges are for counts, so
   there's no exact match for a static label.
4. **Notices.** M3 has no banner component; notices use filled containers
   (error, secondary, and a custom warning container).
5. **Warning color.** M3's baseline has no warning role. An amber custom color
   (`--warn-container`) is generated as an M3 tonal palette.
6. **Data-visualization colors.** M3 doesn't specify charts. Severity colors
   (Class I red, II amber, III teal, Public Health Alert violet) are M3 tonal
   palettes built from the original hues but **not harmonized** to the seed, so
   their meaning isn't shifted. Colors are never the only cue: class names
   appear as text on every row and in legends.
7. **Data list.** M3 has no data-table component. The desktop list uses M3 list
   metrics (56dp rows, 16dp insets) with column alignment and sortable headers.
8. **Pressed feedback.** Pressed states use the flat 10% state layer rather
   than an animated ripple.
9. **Density.** Filter fields keep the full 56dp height on desktop; no reduced
   density is applied.
10. **Contrast measurement.** Pass/fail uses the WCAG 2.x ratio; APCA values, where shown, are informational only.
11. **Expressive motion.** Springs are approximated with CSS `linear()` easing curves, not true physics-based springs, so velocity is not preserved when an interaction is interrupted.
12. **Large and extra-large layout.** The spec's margin values for these classes are unverified here; the 24dp medium-and-up margin is reused.

The Excel workbook shares the light-scheme **colors** only; M3 governs screen
UI, so its fonts and layout stay spreadsheet-native.
