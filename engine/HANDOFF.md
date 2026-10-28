# Engine notes

Current-state notes for anyone changing the engine. History is in [`docs/phase-log.md`](../docs/phase-log.md), decisions in
[`docs/07-decisions.md`](../docs/07-decisions.md), and everything unverified or known to be wrong in [`TO-CONFIRM.md`](../TO-CONFIRM.md).
Last reviewed 2026-10-13 (through pe-update36).

**Spelling:** American English (D36). The page, exports, tests, code, docs and code comments use it. What stays British on purpose: published titles and quotations; the `colours` key in `engine/fixtures/ou_luo_table1.json`; the humour, glamour and tranquillity entries in the matcher's `WORD_FORMS`; the lexicon and emotion-weights data files; `aria-labelledby`; the `colour-science` library (`import colour`) and the OSF data's `colour` column; Pantone's "Warm Grey" names; and the file name `docs/08-data-and-licences.md`. The full list, with reasons, is in the pe-update20 summary.

## Module map

| File | Module | Exports |
| --- | --- | --- |
| `color.js` | M1 | `parseColor`, `toBytes`, `oklch`, `labD50`, `inSrgbGamut`, `mapToSrgb`, `hexFromOklch`, `roundOklch`, `normalize` |
| `lut.js` | M2 | `decodeLut`, `lookup`, `roundCmyk`, `tac` |
| `gamut.js` | M3 | `screenGamut`, `printGamut` |
| `spot.js` | M4 | `parseEntries`, `score`, `band`, `BANDS` |
| `harmony.js` | M5 | `harmonyCandidates`, `allCandidates`, `LENSES`, `accessibilityOf`, `nearestPassingLightness`, `ouLuoModel`, `ouLuoHarmony`, `OU_LUO_K` |
| `palette.js` | M6 | `buildPalette(seed, supporting, {overrides})`, `nearestPassingTone`, `hctOf`, `referenceScheme`. Needs the bundle (rule 6). Material 2021 spec by default |
| `checks.js` | M7 | `contrastRatio`, `textContrast`, `nonTextContrast`, `contrastMatrix`, `apcaScore`, `simulateCvd`, `cvdDistinctPairs`, `printLegibility` |
| `matcher.js` | M8 | `indexLexicon`, `matchTerms`, `matchDescriptors`, `ouScores` (JS mirror of `build_lexicon.ou_scores`), `WORD_FORMS`, `baseForms`, `lowerTier`, `leanTestedRange` |
| `analyze.js` | glue | `analyze(input, luts)`: screen record, print per profile, gamut, P3 flag |
| `de.js` | shared | `de00` |
| `project.js` | state | default state, strict validate and parse of project files |
| `export/` | exports | `model.js` (one shared model), `forge.js` (Forge tokens and the W3C DTCG file), `css.js`, `markdown.js`, `ase.js`, `zip.js`, `sheet.js` (PDF), `files.js` (formats, names, `saveShape`), `index.js` |

Outside `engine/`: `web/` (page: `style.css`, `app.js`, `harness.mjs` and the Playwright suites), `build/` (Python LUT and lexicon builds, esbuild bundle, page
and example builders), `data/` (LUTs, lexicon, accuracy report), `examples/fernhill-bakery/` (fictional brand with committed outputs).

`color.js` is the hub every other module pulls OKLCH and Lab D50 numbers from, rather than re-instantiating culori converters.

## Rules every module follows

1. **Never call culori's `differenceCiede2000()` directly.** It converts inputs to D65 Lab first, which shifted results by up to 26 ΔE00 in testing. Always use
   `de00()` from `de.js`, passing two `{l, a, b}` objects in the same frame (D50 everywhere in this engine).
2. **Lab frame is D50** (culori mode `'lab'`). culori's sRGB to Lab D50 agrees with LittleCMS within ΔE00 0.004 over 11,000 colors. The one place D65 is used is
   Ou's color-emotion models and the Ou & Luo harmony model, because that is how they were measured (`build_lexicon.ou_scores`, `harmony.js`).
3. **Gamut flag (M3):** `de00(screenLabD50, lookup(lut, rgb).rtLab) > 2.0` means out of gamut. `gamut.js#printGamut()` shows `rtLab` (converted to hex) as the printable
   neighbor. Pure black always flags, with a note (ink black is lighter than screen black).
4. **P3 flag:** `gamut.js#screenGamut()` uses culori `inGamut('rgb')` on the OKLCH color; if false it maps with `toGamut('rgb', 'oklch')` (CSS Color 4 chroma
   reduction, exposed as `color.js#mapToSrgb`) and keeps the original in `screen.mappedFrom`.
5. **CMYK display:** `roundCmyk()` (half up), and show TAC against the profile's limit (320 / 300 / 280 for the three US conditions, 300 / 300 for the two PSO conditions; the FOGRA39 file states none, so nothing is checked for it, D38).
6. **Material color utilities** must be bundled (esbuild) where M6 needs them; their files use extensionless imports. M1, M2, M3, M4 and M7 run unbundled on culori
   and apca-w3 alone. Run `npm run bundle` before tests that import `dist/engine.mjs`.
7. **WCAG vs APCA:** WCAG 2.2 (`checks.js#textContrast`) is the pass/fail floor. APCA (`checks.js#apcaScore`) is advisory only, never a gate, never applied to print
   (its license restricts it to web content).
8. **CVD simulation is Machado et al. 2009** via culori's `filterDeficiencyProt/Deuter/Trit` at full severity. `checks.js#cvdDistinctPairs` flags role pairs whose
   simulated ΔE00 is under 10.
9. **Evidence shown beside accessibility.** Every suggestion shows its evidence tier and its accessibility side by side, in the same card treatment. Rank by
   evidence fit. Accessibility never silently re-ranks or hides a candidate; offer filters instead. Report each accessibility problem with its fix where one exists
   (the nearest passing tone in the same hue).
10. **Export gate.** Unresolved WCAG AA role-pair failures (no fix, no accepted note) block every export except the project file (`ExportBlockedError`).
11. **The page declares only the `downloads` capability.** Never declare `db`; it makes the page organization-only.

## Tests

`npm test` builds the bundle and page, then runs every engine test (`test_lut`, `lab`, `spot`, `color`, `gamut`, `checks`, `harmony`, `ouluo`, `matcher`,
`palette`, `analyze`, `export`, `ase`, `project`, `sheet`, `files`, `example`), `web/test_tokens.mjs`, and the Playwright suites (`test_export_ui`, `test_e2e`) in
headless Chromium. The Python lexicon test runs separately (`python build/test_lexicon.py`). CI runs both. Details and what each test can and cannot catch:
[`docs/06-testing.md`](../docs/06-testing.md).

The PDF and zip tests need `poppler-utils` (pdftotext, pdftoppm), `qpdf` and `unzip` installed. Vectors: `py_vectors.json`, `de_vectors.json`. Fixtures:
`engine/fixtures/` (a third-party ASE sample, and Ou & Luo Table I).

**Running the tests on Windows (found 2026-10-13).** Use `npm.cmd` in PowerShell (the `npm` script is blocked by the execution policy). Windows PowerShell 5.1 has no `&&`, and `test:engine` uses a bash loop, so run `npm.cmd test --script-shell "C:\Program Files\Git\bin\bash.exe"` (or use Git Bash); this also puts `unzip` on the path. Keep the repo outside Documents, or allow `node.exe` through Controlled folder access, or `npm install` hangs. The project uses `playwright-core`, so install the browser once with `npx.cmd playwright-core install chromium`. The lexicon test needs `pip install colour-science numpy`. `test_sheet.mjs` needs poppler-utils and qpdf (C29). The test and build scripts build paths with `fileURLToPath`, not `URL.pathname`, so they also run on Windows.

## Things to know

- **Lexicon input for M8:** `data/lexicon.json` from `build/build_lexicon.py` (approved rows only). Targets carry `L`, `C`, `hueWeights`, `colorTerms`, `nudges`
  and `models`.
- **Ou & Luo (2006):** equations match the printed paper and `test_ouluo.mjs` checks them against the paper's own range and figures. The paper's Fig. 6b disagrees
  with its Eq. (4) at low lightness sums, and the code follows the equation (TO-CONFIRM C1). The score is advisory and labeled "lab-patch model".
- **`mapToSrgb` history:** it once returned black for every out-of-sRGB color (culori's `toGamut('rgb')` returns an RGB-mode color and the code read `.l/.c/.h`
  off it). The original test only checked "valid hex". Fixed, with regression tests. Measured behavior over 20,000 colors: lightness holds (p95 drift 0.017); hue
  holds within 12° for OKLCH L 0.3 to 0.8 and drifts up to about 40° near black and white.
- **Word matching (D33):** term or approved synonym, then study words (`studyWords`, Aaker's items), then word forms (suffix rules in `baseForms` plus the
  irregular `WORD_FORMS` table, with a small block list such as "really"), then `strongSynonyms`, which lower the row's tier one step through
  `lowerTier`. A direct match of a row replaces an earlier strong-synonym match of the same row. Hyphenated words match whole or are flagged whole.
  `test_matcher.mjs` checks that no inflection of a lexicon word lands on a different row.
- **Tie-break and dark colors (D34):** equal scores go first to the direction of the terms' net lightness lean, then to the color nearest the
  study's measured patch (`opts.tieBreak: 'anchor'` restores the old rule for comparison). Color-word band floors for red, green, turquoise, blue and
  purple are L 0.25. The lean is followed only inside the lightness the source study tested (`leanTestedRange`, D35); a seed outside it carries
  `beyondTested` ({ side, range, terms }) and the page says so on the card.
- **Matcher constants are engineering choices** (low confidence), in `matcher.js`: OKLCH L grid 0.25 to 0.95, 15° hue steps, two-level lightness and chroma leans
  (half the study's beta), 0.05 OKLab minimum gap between variants (TO-CONFIRM C10).
- **Material 3 mechanics used:** 48px touch targets, 40px buttons (24px side padding), 32px chips, 48px tabs with a 3px indicator, 52 by 32px switch, state layers
  8% hover, 10% focus, 10% pressed (12% on chips, switches and tabs), 3px focus ring with 2px offset, disabled 38%. Source: Material Web 2.5.0 tokens (Apache-2.0);
  m3.material.io itself could not be read by the tools used. Intentional deviations: field labels sit above the field instead of floating inside the outline; the tab
  bar is used as a wizard stepper with a done mark; the visual design is not Material's.
- **State** is saved in browser storage (flushed on `pagehide` and when the page is hidden) and in a project file (Export step).
- **ASE:** structure checked by three independent readers (engine `parseAse`, the `ase-util` package, a Python struct reader) plus a third-party sample, but never in
  Adobe (TO-CONFIRM C7). `ASE_TESTED_IN_ADOBE` in `web/app.js` drives the on-page notice; flip it only after that check. No ICC profile is carried; SWOP and the three European conditions are not in
  the ASE (six print conditions since D38; the first three keep positions 0 to 2 because the ASE and summary tables read them by position); the spot group appears only with pasted values.
- **Downloads:** the claude.ai viewer's allow-list has no `.css` or `.ase`, so those two are saved inside a `.zip` on that route (`saveShape` in `files.js`). The
  browser fallback keeps native names.
- **PDF** uses pdf-lib standard fonts (WinAnsi). Characters outside it become "?" and are reported as warnings. Δ, arrows, ≥, ≤ and ✓ are transliterated. Print
  swatches are drawn as the printable-neighbor RGB.
- **DTCG file** omits `$version` and `$themes` (the format leaves modes to its resolver module); the Forge file keeps both. Forge's old bare `$extensions.cmyk` is
  replaced by the namespaced `com.kwadejoslin.palette` extension. Kwade imported the DTCG file into Tokens Studio without problems (2026-09-29).
- **Step bar (C18):** follows the WAI-ARIA tabs pattern with manual activation. The selected tab is the one Tab stop (roving `tabindex`); arrow keys, Home and End move focus between the open tabs; Enter or Space opens the focused one. Activation is manual because opening a step moves focus into its panel. Disabled tabs are skipped. Tested in `web/test_e2e.mjs`; not yet re-tested with a screen reader.
- **Render guard:** `app.js` has a re-entrancy guard, because a focused field removed mid-render fired its change handler.

## Starting a new session

**State on 2026-10-13 (pe-update36).** The tool has six print conditions in two regions (D38). North America: GRACoL 2013 coated (default), SWOP 2013, GRACoL 2013 uncoated. Europe: PSO Coated v3 (FOGRA51), PSO Uncoated v3 (FOGRA52) and a FOGRA39 file ("Coated FOGRA39L (VIGC 260)", no stated ink limit). The last full run of `npm test` (pe-update33) passed 595 checks, 70 of them in the browser; that total was not recomputed. On 2026-10-13, on Windows after the C27 footer change, every engine suite passed except `test_sheet.mjs` (not run to completion; C29), the export UI suite passed 43 checks, the end-to-end suite 71 (two new footer checks), and `python build/test_lexicon.py` passed. Work is delivered as `pe-updateNN.zip` packages (changed files only) with a summary file and a commit message; Kwade applies and commits them from his own tree, and the working copy here never pushes.

**Read in this order:** `TO-CONFIRM.md` (the one open list), `docs/07-decisions.md` (D33 to D39 are the recent ones), `docs/phase-log.md`, then this file. In the claude.ai Project, `claude/project-file-index.md` says which copy of each document is canonical.

**What is waiting, and on whom**

| Waiting on | Items |
| --- | --- |
| ECI's reply | C22: may the tables derived from the PSO profiles be published. |
| Kwade, about the FOGRA39 file | C23: where the file came from and its terms, or replace it with the ECI ISO Coated v2 profile, or remove it (steps in C23). |
| Kwade, when the repo is ready | C24: send the repository and usage notes to PRINTING United Alliance, after D2 (public or not) is decided. |
| The Ou & Luo authors | C1, C2 (asked 2026-10-01; no reply yet). |
| The primary papers | C25 (Gao & Xin 2006; Xin et al. 2004) and C28 (Suk & Irtel 2010, cited from its abstract only). Kwade is looking for them. |
| CI, or tools for the PDF test | C29: confirm CI is green, or install poppler-utils and qpdf and run `node engine/test_sheet.mjs`. |
| A screen-reader session | C18, C20 (re-test), then C19 (step navigation), then C21 (reading load). |
| Equipment Kwade does not have | C6 (Pantone guide), C7 and C8 (Adobe). |
| Kwade's judgment, deferred on purpose | C10 (seed quality on the live page), C15 (the near-synonym chip, not yet seen by him), C13 (stays open). |

**Decisions that need Kwade before anything changes:** the matcher tie-break and the color-word bands (D34, D35) are not changed without asking. Brand data comes from published sources only. No researcher or contact email addresses go in the repo.

**Not done, and why**
- The live page (https://claude.ai/artifact/UU1bGD978nRCUUiFcbfnhN) has not been republished since the pe-update25 era. It lacks the pe-update28 lexicon, the pe-update33 and C27 footer sentences and all six tables. Republishing now would publish the ECI and FOGRA39 tables before C22 and C23 are answered; one republish after those should cover everything.
- The ASE has no groups for SWOP or the European conditions (two GRACoL groups, spec section 7).
- The share of identical rounded CMYK values between conditions is not measured for the three European tables.
- `Palette Engine.zip` in the project holds the three-profile build on purpose (same licensing reason).

**Housekeeping each update.** Zip of changed files (`git diff --name-only HEAD~1 HEAD | zip -q tmp/pe-updateNN.zip -@`), a summary file, a commit message ending with the attribution lines the session gives, refreshed `palette-engine-repo/` copies in the Project with the "Repo copy as of" header, an `update-log.md` entry, and the file index "as of" notes.

## Open items

See [`TO-CONFIRM.md`](../TO-CONFIRM.md). Not repeated here so there is one list.
