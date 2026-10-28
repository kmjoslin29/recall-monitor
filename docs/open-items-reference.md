# Open items: a working reference

A plain-language guide to every open item in [`TO-CONFIRM.md`](../TO-CONFIRM.md): what it is, why it matters, what you need, the steps, and how to
record the result. Items are ordered by how soon you can act on them. None of them stops the tool from working; each one limits what the
project can honestly claim.

How results get recorded: change the item's row in `TO-CONFIRM.md` (move it to the Done table with the date), update any file named in the item,
run `npm test`, and commit.

## At a glance

| ID | What | Needs | Effort | Blocks |
| --- | --- | --- | --- | --- |
| C22 | Ask ECI about the derived PSO v3 tables | An email (draft ready) | 15 minutes, then a wait | D2 (public repo) |
| C23 | Say where the FOGRA39 file came from, or swap it | Where you downloaded it | 10 minutes | D2 |
| C24 | Send PRINTING United Alliance the repository, once public | D2 decided | A short email | Nothing |
| C25 | Read Gao & Xin (2006) and Xin et al. (2004) on hue and warm-cool | The two papers | A reading session | Nothing |
| C28 | Obtain and read Suk & Irtel (2010) | The paper (author, ResearchGate request or library) | A wait, then a reading session | Nothing |
| C29 | Run the PDF sheet test and check CI | CI result, or poppler-utils and qpdf installed | A few minutes | Nothing |
| D2 | Decide whether to make the repo public | C22 and C23 answered (or those tables removed) | A decision | Nothing |
| C10 | Review the matcher's constants | Real use | Ongoing | Nothing |
| C15 | Look at the "near-synonym, tier lowered" chips on the live page (the 27 strong synonyms were reviewed and agreed 2026-10-01) | The live page | 10 minutes | Nothing |
| C13 | Screen-reader session | A screen reader (NVDA is free) | 1–2 hours | Nothing |
| C1 | Which version of the lightness-sum equation is right | A later paper or the authors | Unknown | Nothing (score is advisory) |
| C2 | EC constant (−2) in the Ou & Luo model | A second implementation or the authors | Unknown | Nothing |
| C3 | Ou & Luo independent test (r = 0.75) | The authors' raw scores | Unknown | Nothing |
| C6 | Pantone spot-check | A Pantone guide, daylight or a booth | Half a day | Nothing |
| C7 | `.ase` in Adobe apps | A device with Illustrator or InDesign | 30 minutes | `ASE_TESTED_IN_ADOBE` stays false |
| C8 | Adobe's color engine against LittleCMS | An Adobe app | 1 hour | Nothing |

---

## C5 (closed 2026-10-06). IDEAlliance and the derived tables

PRINTING United Alliance answered on 2026-10-01: yes, with their notice included. See `TO-CONFIRM.md` (Done) and `NOTICE.md`.

## C22. May the tables derived from the ECI profiles be published?

**What it is.** PSO Coated v3 and PSO Uncoated v3 may be "used, embedded and exchanged without restriction", but not "distributed, sold or altered" without ECI's written permission.
The tables computed from them are not the profiles, but ECI decides what counts as distributing.

**Steps.** Edit `docs/eci-email-draft.md` to your voice and send it through the contact route on eci.org; note the date in `TO-CONFIRM.md` (C22: "asked 2026-MM-DD"); save the reply in full,
without contact details, and record any notice text. If none in a few weeks, one polite follow-up; silence is not permission.

**Outcomes.** *Yes:* update `NOTICE.md`, the page footer and `docs/08-data-and-licences.md`, close C22. *No or conditions:* the two tables stay out of the public repo (the build rebuilds them from
the profiles); the live page needs another way to get them, a design decision to make together.

## C23. The FOGRA39 file

**What it is.** The file you supplied has no usage terms in it (only "Copyright X-Rite, Inc."), a name that does not say what "VIGC" or "260" mean, and no ink limit its own tables respect.

**Steps.** Tell me where you downloaded it and what that page says about use. If it cannot be cleared, either swap it for the ECI ISO Coated v2 profile (ECI terms, so it follows C22) or remove it (steps in the C23 row).

## C24. Send PRINTING United Alliance the repository

They asked for it once it is ready, to share with members. Wait for D2. A short reply is drafted in `docs/eci-email-draft.md`.

## C25. Does hue matter for warm-cool?

A secondary review (Sanad 2017) says Gao & Xin (2006) found hue insignificant even for warm-cool, while Ou et al. (2004) have a hue term in it. "Cool" gets its hue lean from that term. **Steps.** Read Gao & Xin (2006) and Xin et al. (2004, quantitative part). Valdez & Mehrabian (1994) was read on 2026-10-13 and does not settle it (it did not rate warmth). Record what each paper says about hue in warm-cool. Whether the lean of "cool" changes is your decision. Details in the C25 row of `TO-CONFIRM.md`.

## C26 (closed 2026-10-13). Deng, Elliot and Valdez & Mehrabian

Read and recorded; see `TO-CONFIRM.md` (Done) and `docs/03-method-and-evidence.md`. No tier or number changed.

## C27 (closed 2026-10-13). The controlled-stimuli sentence on the page

Added to the footer in `web/app.js` with two checks in `web/test_e2e.mjs`; see `TO-CONFIRM.md` (Done). The live page still needs republishing, which waits for C22 and C23 (see `engine/HANDOFF.md`).

## C28. Suk & Irtel (2010)

Cited from its abstract only. Ask the corresponding author (Hyeon-Jeong Suk, KAIST), request the paper on ResearchGate, or use a library; Suk & Irtel (2008) is free on J-STAGE (DOI 10.5057/kei.7.181) and seems related. Record what the full text says about chroma, lightness and hue in `docs/03-method-and-evidence.md`. Details in the C28 row of `TO-CONFIRM.md`.

## C29. The PDF sheet test and CI

`engine/test_sheet.mjs` needs poppler-utils (pdftotext, pdftoppm) and qpdf. It was not run to completion on the Windows machine on 2026-10-13, where those tools are missing. **Steps.** Check that the latest CI run (Linux) is green, or install the two tools and run `node engine/test_sheet.mjs`. Details in the C29 row of `TO-CONFIRM.md`.

## D2. Make the repo public?

Depends on C22 and C23 (C5 is closed). Before flipping it, check: `NOTICE.md` matches the answers; no `.icc` files are committed; `README.md` and the license read
correctly to a stranger; `git log` contains nothing you would not want public (the email address in commits, for example). In GitHub: repository
Settings, then the danger zone at the bottom, then "Change visibility".

## C9. The blue band of the color-word bridge (closed 2026-09-30)

Reviewed and left unchanged; see `TO-CONFIRM.md` (Done) and decision D20. It was not judged against real brand seeds on the live page, so if a blue
ever looks wrong there, reopen it as a new item.

## C14. Labrecque & Milne (2012) coefficients (closed 2026-10-06)

Checked against the printed tables; two missing results added and a separate royal-blue region for the "competent" words (D37). See `TO-CONFIRM.md` (Done).

## C10. Matcher seed-scoring constants

**What it is.** `engine/matcher.js` scores candidate seed colors with settings I chose, not settings a study gave: OKLCH lightness range 0.25–0.95,
15° hue steps, half-strength leans, and a 0.05 minimum OKLab gap between seeds.

**Steps.** Use the tool on three or four real brands (including yours). Where a suggestion feels wrong, note the seed, what you expected, and what
you got. Then bring those notes to me and we change one constant at a time, re-running `npm test` after each. Record accepted changes in
`docs/07-decisions.md`.

**Progress (2026-10-01).** Four runs against 21 published brands are in [`c10/README.md`](c10/README.md): rules fixed before each run, results in `c10/results*.md`, re-run with `node docs/c10/run.mjs [brand-set.json]`. No constant was implicated by the first run; the main finding was vocabulary coverage (C15, widened by D33). Dark colors were then offered (D34), kept inside the lightness the source study tested (D35). Run 4 added the National Park Service (colors eyedropped from its Arrowhead, so approximate). Update 2026-10-03: the synthesized word mappings were reviewed and all 36 kept (they stay speculative). Still to do: judge the seeds by eye on the live page (the dark seeds, the near-synonym chips and the beyond-tested note). Kwade is deferring the seed judgment on purpose until the other items are polished, so that it can be challenged.

## C12. The wording of the claude.ai viewer's save prompt (closed 2026-09-30)

Recorded in `TO-CONFIRM.md` (Done). The page's messages matched the viewer's behavior for the two cases seen.

## C13. Screen-reader session

**What it is.** The automated tests check contrast, accessible names and keyboard focus in Chromium. They cannot tell you whether the page makes
sense when read aloud, or whether the order of announcements is usable.

**What you need.** NVDA (free, Windows) with Chrome or Firefox, or Windows Narrator. Note which you used and its version.

**Steps.**
1. Open the page and start the reader. Move through with Tab only, then with the reader's heading and landmark commands.
2. Walk the main path: choose a seed, look at the palette, read a contrast result, trigger the override, export.
3. Note anything unannounced, announced twice, announced in a confusing order, or unreachable by keyboard.
4. A ready-made script and log are in [`screen-reader-session.md`](screen-reader-session.md).
5. Log each finding as a line in `TO-CONFIRM.md` (or a new item) with the reader and browser used, then we fix them. Label the result
   "screen-reader session, NVDA + Chrome", not "accessible": one session is one data point.

**Progress (2026-10-01).** One session run: NVDA 2026.2 with Firefox 157.0 (not Chrome). It mostly worked; four problems are logged as C18 to C21 in `TO-CONFIRM.md`, and the session is written up in [`screen-reader-session.md`](screen-reader-session.md). C13 stays open: other browsers and readers are untried.

## C1. Which lightness-sum equation is right (Ou & Luo 2006, Eq. 4)

**What it is.** The printed equation and the paper's own Fig. 6b disagree by about 0.11 rms, worst at low lightness sums (curve about −0.44 vs
about −0.26 from the equation). Figs. 4b, 8 and 10a match their equations, so only this one is in doubt. The code follows the printed equation.
An earlier conference version of the model uses different forms and cannot settle it.

**What would settle it.**
- A later paper that restates the model with its constants (the group's follow-up papers, or the chapter on color emotion and color harmony in the
  Handbook of Color Psychology; I have not verified that chapter prints the equation).
- The authors. Search for their current institutions and publications; a short, specific question ("Fig. 6b appears to sit below Eq. 4 at low
  lightness sums; is there an erratum or a different constant set?") is easy to answer.
- A university library or an interlibrary loan for the published version and any erratum, since Wiley is paywalled for you.

**If Fig. 6b turns out to be right.** Change `ls0`–`ls3` in `OU_LUO_K` (`engine/harmony.js`) to the fitted values (about 0.2023, 0.6484, −3.1851,
0.0258, or the authors' numbers), update the documented-gap check in `engine/test_ouluo.mjs` (it currently expects the printed constants to sit
0.07–0.16 rms from the figure), and update the note in `TO-CONFIRM.md`. Until then the score stays labeled **advisory**.

**Progress (2026-10-01).** Asked the authors in one email covering C1 and C2 (sent by Kwade; no reply yet). Save any reply in full under `docs/correspondence/` and ask their permission before committing it if it contains personal details. If there is no reply in a few weeks, send one polite follow-up; silence is not an answer.

## C2. The EC constant (−2)

**What it is.** EC = 0.5 + 0.5·tanh(−2 + 0.5C*) weights how strongly a color's hue effect counts, by its chroma. The paper has no figure for it, and the
range test cannot tell −2 from −2.5. The hue-curve constants were pinned by digitizing Fig. 10a (done).

**What would close it.** A second, independent implementation of the model, or the authors' data. Not something you can do alone; ask in the same
message as C1.

## C3. The independent test (r = 0.75)

**What it is.** The 2006 paper says its model correlated at 0.75 with a separate 30-pair data set (Gurura et al.). I read the source (AIC 2004,
pp. 239–242): it gives no per-pair scores and used many backgrounds, so the number cannot be reproduced. What is checked: the model ranks the 22
"harmonious" pairs above the 8 "disharmonious" ones (AUC 0.86; gray/brown is an inference from a footnote typo).

**What would close it.** The raw ratings from Gurura's experiment on the gray background. Ask the authors of the AIC paper (the paper prints contact
addresses for all three authors on p. 242, from 2004, so they may be out of date; take them from your copy of the paper, not from this repo).

**Progress (2026-10-01).** Re-read in the full proceedings volume: no per-pair scores are printed, and the 22/8 labels come from the paper's first experiment. See `TO-CONFIRM.md` (C3) for the detail. Still open.

## C6. Pantone spot-check

The full procedure is in [`spot-check-protocol.md`](spot-check-protocol.md); results go in [`spot-check-log.md`](spot-check-log.md). In short:
you need a physical Pantone guide (note its edition and year), daylight or a D50/D65 booth, and a display you trust. Pick 20 entries and 5 target
colors, paste 20 licensed values into the spot scorer, and compare by eye. Pass means every entry matches or has an explained offset, and the
tool's first choice agrees with yours (within one place) for at least 4 of 5 targets. The result is labeled "spot-checked (visual)"; only a
spectrophotometer reading may be called "measured". Do not change thresholds to fit the result. Until it is done, do not call spot-match results verified.

## C7. `.ase` in Adobe Illustrator and InDesign

**What you need.** A device with Illustrator or InDesign (a friend, a library, a school lab, or a trial).

**Steps.**
1. Take `examples/fernhill-bakery/output/fernhill-bakery.ase` (or export a new one from the page; the viewer gives it inside a zip).
2. Import it as swatches in each app.
3. Check: group names, color modes (RGB vs CMYK vs Lab as intended), color names, and that the counts match the Markdown spec.
4. If everything is right, set `ASE_TESTED_IN_ADOBE = true` in `web/app.js`, run `npm test`, and record the app versions in `TO-CONFIRM.md`.
   If not, record exactly what differed and bring it to me.

**Meanwhile.** You use Affinity. Opening the `.ase` there is a partial check; if you do it, log it as "Affinity, partial" in `docs/spot-check-log.md`
or `TO-CONFIRM.md` and leave the Adobe flag false.

## C8. Adobe's color engine against LittleCMS

**What it is.** The print tables use LittleCMS with relative colorimetric intent and black-point compensation. Adobe apps use their own engine
and may land about a point of CMYK away.

**Steps.** In an Adobe app with the same profile loaded (GRACoL2013_CRPC6, for instance), set the same intent and black point compensation on, convert a
few known RGB values to CMYK, and compare them with the tool's numbers. Record the differences. If they stay within about a point, say so in the accuracy
notes; if not, the page's "print preview" copy should say the numbers are LittleCMS's, not Adobe's.
