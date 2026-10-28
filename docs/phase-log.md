# Phase log

A record of each phase: what it did, what passed, and what it found. The build spec's phase table is the plan; this is what happened. Numbers are from the test
runs at the time.

## Phase 0: Verify (Opus)

Resolved: culori 4.0.2 (MIT: CIEDE2000, gamut mapping, Machado CVD filters), material-color-utilities 0.4.0 (Apache-2.0; needs bundling), apca-w3 0.1.9 (Limited W3
License: web contrast only), LittleCMS available. Tested that Material's primary role is tone 40 (light) and 80 (dark) in both specs, so the brand hex must stay a
separate token. Tokens Studio object colors were still "in discussion", so hex strings stay the default token form. The Ou & Luo equations were found in an open-access
paper. **No openly licensed Pantone Lab dataset exists**, so none is bundled: the designer pastes their own values. The ICC profiles could not be fetched from the cloud
workspace and were downloaded by Kwade.

## Phase 1: Python build step (Opus)

Built 33³ lookup tables for the three profiles with LittleCMS called in double precision (Pillow's ImageCms is 8-bit only). Against LittleCMS on 10,000 random + 500
near-gray + 500 gamut-edge colors (seed 20260928), printed ΔE2000 p95 / max: GRACoL coated 0.14 / 0.73, SWOP 0.15 / 0.71, GRACoL uncoated 0.14 / 0.73 (limits 1.0 / 2.0).
Rounded CMYK identical for 82–85%, off by one for most of the rest. The 49-step alternative was ~91% identical but ~9.4 MB against ~2.9 MB, so 33 stays (Kwade).

## Phase 2: Core engine (Opus for LUT and spot scorer, Sonnet for the rest)

Part A: the JavaScript lookup equals Python on 3 × 11,000 colors; culori's Lab D50 agrees with LittleCMS to ΔE00 0.004; ΔE2000 matches colour-science (1,150 pairs) and
the Sharma, Wu & Dalal pairs. **Found:** culori's built-in ΔE2000 converts to D65 (up to 26 ΔE00 error on D50 input), so all ΔE goes through `de.js`.
Part B: hex → OKLCH → hex exact for 10,000 colors; `#00FF00` flags out of print gamut on GRACoL coated (ΔE00 16.0); neutral grays stay in; `#767676` on white is 4.54:1
(pass), `#777777` is 4.48:1 (fail).

## Phase 3: Lexicon (Opus drafts, Kwade approves)

48 terms (18 perceptual, 20 brand-personality, 10 emotion), each with sources and a tier; the build rejects any row without both. Kwade reviewed every row (approve, edit,
drop). Decisions: brand-personality weights keep only p < .05 results read identically twice; "cool" gains a hue lean from Ou's own term; "calm" uses Ou's passive pole;
emotion weights were rebuilt from the raw survey data with one stated rule and reproduce all 14 published figures; hue families and the color-word bridge approved, blue
band to revisit.

## Phase 4: Palette logic and interface (Sonnet)

Harmony lenses, Material 3 tonal palettes and 29 roles (equal to the library's reference scheme for three seeds, light and dark; four seeds pass AA in both), the descriptor
matcher, and the interface with locks, overrides, rationale notes, filters and gating. **Found and fixed:** the gamut-mapping helper returned black for out-of-sRGB
colors (the older test only checked "valid hex"); two matcher drafts passed tests while returning near-black seeds. Browser checks: both paths, dark theme, phone width, touch
targets, and an automated WCAG AA audit of every text element (found and fixed one 4.27:1 sample). New rule from Kwade: evidence and accessibility side by side on every
suggestion, ranked by evidence, never silently re-ranked.

## Phase 5: Exports (Sonnet)

Seven outputs from one model, each parsed back by an independent reader; the Export step; project save and open; the `downloads` capability. 135 export checks, 30 ASE, 50 project,
53 PDF sheet, 27 file-handling, 43 browser checks. **Found:** the viewer's download allow-list excludes `.css` and `.ase` (zipped there); PDF standard fonts limit characters;
a redraw re-entrancy bug. **Not met:** the ASE has not been opened in Adobe apps. After review the export labels were renamed to plain language (D30 in the decision log).

## Phase 6: Validation (Sonnet; Kwade runs the spot-check)

Shared browser-test harness; a 48-check end-to-end suite covering both entry paths and every step in light and dark at two widths (zero console errors, page errors or failed
requests; WCAG AA text contrast; accessible names; keyboard focus ring; reload; blocked and hostile storage). A fictional sample brand with all outputs, rebuilt by a script and
checked by a test so it cannot go stale. **Found and fixed:** work changed in the last 400 ms before closing the page was not saved. **Not yet done:** the Pantone spot-check
(see [the protocol](spot-check-protocol.md)).

## Phase 7: Repository

Repository structure, this documentation, a continuous-integration workflow, and a clean-clone check (install and run every test from a fresh copy).

## 2026-10-06: European print conditions (D38, pe-update29)

Added PSO Coated v3 (FOGRA51), PSO Uncoated v3 (FOGRA52) and a supplied FOGRA39 file as tables 4 to 6. All pass the D4 limits (printed ΔE00, 10,000 random + 500 near-gray + 500 gamut-edge, seed 20260928): PSO coated p95 0.15 / max 0.99, PSO uncoated 0.14 / 0.70, FOGRA39 file 0.14 / 0.74. The first three tables rebuilt byte-identical. JavaScript and Python lookups agree on 11,000 colors per profile.

## 2026-10-07: Sanad (2017) added as a context reference (D39, C25, pe-update33)

Kwade supplied Sanad (2017), a literature review on the factors that affect color meaning and emotional response. It is recorded as a secondary context source in `docs/03-method-and-evidence.md` and supplies no number to the lexicon or the matcher. The page footer gains one sentence saying the findings are averages across the people studied and that age, culture, design training and setting can shift how a color is rated. The review's one disagreement with a checked source (hue in warm-cool, Gao & Xin 2006 against Ou et al. 2004) is the new open item C25; Kwade is looking for the primary papers.

## 2026-10-13: Two papers reviewed and the Ou et al. (2004) source note widened (C26, pe-update34)

Karthikeyan & Joy (2018), supplied 2026-10-09, was read in full and recorded as reviewed, not used (`docs/03-method-and-evidence.md`). It pointed to two sources worth reading, which are the new open item C26 (Deng et al. 2010; Elliot 2015 with Elliot & Maier 2014). Ou et al. (2004) Part I was re-read against the project record on 2026-10-11: X11 stands, with no equation or code change. Two additions came out of it: the `ou2004` scope note in both lexicon files now records the observers' color-science training, the patch and scoring method, the five-region culture-independence claim for the four modeled scales, and the unstated CIELAB white point; and C25 gains the Tables VIII-X comparison of the Ou, Sato and Xin & Cheng warm-cool models. Note text and docs only. Nothing in code, tiers, weights or page behavior changed, so no republish is needed.

## 2026-10-13: Four papers read and recorded (C26 closed, C27 opened, pe-update35)

Kwade supplied open copies of Deng et al. (2010), Elliot (2015), Elliot & Maier (2014) and Valdez & Mehrabian (1994), and they were read. Deng et al. joins the hue-similarity row as a converging source with the tier held, and is cited in the classical-geometry row as support for emphasis roles. Elliot (2015) and Elliot & Maier (2014) are recorded as reviewed with no number used, beside Sanad (2017). Valdez & Mehrabian is recorded as corroboration only. C26 is closed; C25 gains the Valdez & Mehrabian outcome and two further candidates (Suk & Irtel 2010; Na & Suk 2014, which is not the Suk & Irtel paper); the new item C27 covers one footer sentence about controlled stimuli, which is decided; the edit to `web/app.js` and two checks in `web/test_e2e.mjs` were prepared the same day as a separate package, not yet run. Suk & Irtel (2010) is cited from its abstract only until the paper is obtained (C28). Docs only. Nothing in code, tiers, weights or page behavior changed.

## 2026-10-13: C27 closed and the tests run on Windows (pe-update36)

The footer edit for C27 (`web/app.js`) and its two checks (`web/test_e2e.mjs`) were applied and the suites run on Kwade's Windows machine. The engine suites passed except `test_sheet.mjs`, which could not run there (poppler-utils and qpdf are missing; new item C29). The export UI suite passed 43 checks and the end-to-end suite 71; `test_lexicon.py` passed. Running on Windows exposed paths in the test and build scripts that only worked on Linux (a file URL turned into a path with `.pathname`, and a Windows path inside a Python string); those were fixed in a separate commit and are not part of this package. `engine/HANDOFF.md` gains a short section on running the tests on Windows. Docs only in this package.
