# Sourcing human causal-strength / necessity ratings for the force-dynamics network typer

**Date:** 2026-08-30 · **For:** SOLVER problem `causation_is_typed_per_clause_not_across_the_causal_network`
**Task:** replace the near-circular hand-coded ordinal (physical>motivational>psychological>enabling)
with a REAL external validation: predict ACTUAL human ratings of causal strength / necessity /
cause-enable-prevent applicability from the force-dynamics necessity+sufficiency estimator, and correlate.

**Provenance grades used:** `FETCHABLE_FILE` (I confirmed a real download URL + format) ·
`PUBLISHED_TABLE_VALUES` (exact numbers verified against an accessible full-text/table) ·
`UNVERIFIED_MEMORY` (reconstructed from memory — confabulation risk, DO NOT use as ground truth).

---

## RANK 1 — CICL `causative-verbs` (Cao, Geiger, Kreiss, Icard & Gerstenberg 2023) — **BEST FETCHABLE**

This is the modern, downloadable re-run of Wolff's exact CAUSE/ENABLE/PREVENT force-dynamics paradigm.
The stimulus itself IS a force configuration and the human response is cause/enable/prevent verb
applicability — a near-perfect target for a force-dynamics typer, with NO hand-coded ordinal in the loop.

- **Provenance:** `FETCHABLE_FILE` (raw CSV URLs confirmed; columns inspected).
- **Repo:** https://github.com/cicl-stanford/causative-verbs
- **Direct downloads:**
  - `data1.csv` (375,681 B, binary yes/no judgments — the main experiment):
    https://raw.githubusercontent.com/cicl-stanford/causative-verbs/main/analysis/data1.csv
  - `data2.csv` (373,122 B, scale/confidence variant):
    https://raw.githubusercontent.com/cicl-stanford/causative-verbs/main/analysis/data2.csv
  - Analysis writeup (verb→category map, scene semantics): `analysis/analysis_083022.md`
- **Items:** 7 force-dynamics scene conditions (3-D animations) × 9 causal verbs. **72 participants**
  (after attention filtering). Verb→category map (from `analysis_083022.md`, verified):
  - **CAUSE** = caused, made, got · **ENABLE** = enabled, allowed, let · **PREVENT** = prevented, stopped, blocked
- **Scale/measure:** `data1` = binary yes/no ("does verb V correctly describe scene S?"); `data2` = confidence scale.
- **Scene encoding (the force config, in the `picture` filename):** e.g. `DOWNHazard100UPHazard0.gif`.
  `UP/DOWN` = the agent/affector's **tendency toward vs away from the endstate**; `Hazard0/Hazard100`
  = **opposing-force strength (0 = none, 100 = strong)**; the sequence of two blocks encodes the
  configuration before/after (obstacle removed then goal pursued, etc.). This is precisely the
  tendency / concordance / opposing-force / result inputs a force-dynamics necessity+sufficiency model consumes.
- **Format:** WIDE csv. Per row = one participant × one scene, carrying `question0..question4` (the verb
  sentences shown) and `yesno-choice0..choice4` (the responses), plus `submission_id, RT, picture,
  trial_name, trial_number`. **You must melt to long** (participant × scene × verb → yes/no), then
  aggregate to **proportion-"yes" per (scene, verb)** = the human causal-applicability rate.
- **Cross-check anchors (PUBLISHED, from the writeup — sanity targets after you aggregate):**
  ENABLE verbs in no-obstacle success ≈ 97% yes; CAUSE verbs in no-obstacle success ≈ 80%;
  PREVENT verbs in obstacle-present failure ≈ 75%; ENABLE verbs in obstacle-absent neutral ≈ 42%.
- **How to map the force-dynamics prediction onto it:** parse each `picture` into (affector tendency,
  opposing-force present?, concordance, result). Run the estimator → continuous necessity+sufficiency →
  threshold to CAUSE/ENABLE/PREVENT (and/or a graded endorsement score per verb-category). Predict
  **proportion-"yes" for each of the 7×9 = 63 (scene, verb) cells**; correlate predicted vs observed
  (Spearman/Pearson across cells), and check the category structure: your CAUSE score should track
  {caused,made,got} endorsement, ENABLE→{enabled,allowed,let}, PREVENT→{prevented,stopped,blocked}.
  This is a real, non-circular external validation: humans gave verb judgments independent of your model.

---

## RANK 2 — Kuperberg, Paczynski & Ditman (2011), *JoCN* 23(5):1230 — **BEST DISCOURSE / NETWORK-LEVEL**

This is the CROSS-SENTENCE causal-relatedness dataset — exactly this problem's level (the reader typing
the edge between two separate sentences). Humans rated how causally related a final sentence is to a
2-sentence context, on a graded scale. Directly tests the discourse-network necessity claim.

- **Provenance:** condition means = `PUBLISHED_TABLE_VALUES` (verified via PMC full text);
  stimulus set + EEG = `FETCHABLE_FILE`; per-item relatedness norms = **not confirmed present in the deposit** (see caveat).
- **Full text (verified):** https://pmc.ncbi.nlm.nih.gov/articles/PMC3141815/
- **Verified numbers — Table 1, causal-relatedness rating, 1–7 scale (1 = weak, 7 = strong):**
  - Highly causally related: **M = 6.37 (SD 0.61)**
  - Intermediately related: **M = 4.79 (SD 1.04)**
  - Causally unrelated: **M = 2.14 (SD 0.99)**
  - Design: 231 three-sentence triplets constructed → **159 triplets** used in the ERP study after
    norming; relatedness norming by **12 undergraduate raters**. (N400 mean amplitudes in µV are NOT
    tabulated — only F/p stats — so N400-by-condition is not usable as item ground truth here.)
- **Stimuli + raw EEG deposit (fetchable):** https://datashare.ed.ac.uk/handle/10283/2128
  (bulk zip: https://datashare.ed.ac.uk/download/DS_10283_2128.zip ). Deposit is EEG-heavy (26+ `.bdf`
  files ~280–360 MB each); it contains the **stimulus set** (the 3-sentence scenarios + condition labels)
  but I could NOT confirm the per-triplet relatedness numbers are included — treat the 3 condition
  means above as the reliable ground truth and the deposit as the source of the actual sentence stimuli.
- **How to map the prediction onto it:** build the causal network over each triplet, type/score the
  edge from the context to the final sentence for **graded causal necessity**, and predict the
  3-way ordinal (highly > intermediately > unrelated). Correlate your continuous necessity against the
  condition means (6.37 / 4.79 / 2.14), or — if you extract per-item norms from the deposit/stimulus
  file — against the 159 item ratings. This is the honest test of "does the network typer's necessity
  track human cross-sentence causal strength?"

---

## RANK 3 — OSF "Normed causality statements" (bvzvy) — **CONFIRMED PUBLIC ITEM-LEVEL NORMS**

Item-level agreement-strength norms for generic causal statements ("smoking causes cancer"), including
causality AND prevention statements. Large, item-level, downloadable — weaker construct-fit than the
force-dynamics scenes (no explicit force config; requires world knowledge), but a real normed set.

- **Provenance:** `FETCHABLE_FILE` (public OSF component with raw/processed data confirmed via API);
  exact CSV column schema `UNVERIFIED` (I did not drill into the processed-data folder — one more step needed).
- **Project:** https://osf.io/bvzvy/ — title *"Normed causality statements"*, description *"Norms for
  strength of agreement with statements of causality and prevention (e.g., 'smoking causes cancer')"*.
- **Structure (top-node osfstorage is empty; data is in child components):**
  - `65j4u` = **Data** → folders `1 raw data`, `2 screened data`, `3 processed data`, `codebooks`,
    plus `processing.rmd` (https://osf.io/download/f2nty/) and `screening.rmd` (https://osf.io/download/9u6mk/).
    Component page: https://osf.io/65j4u/ · Bulk zip: https://files.osf.io/v1/resources/65j4u/providers/osfstorage/?zip=
  - `e8hm5` = Measures and stimuli · `4r3a2` = Study details · `3cfsp` = Analyses and plots.
- **Items / scale:** individual causal + prevention statements rated for strength-of-agreement
  (the codebooks folder + `processing.rmd` define columns; read those first to get exact fields/scale).
- **How to map the prediction onto it:** for each "A causes/prevents B" statement, feed the A→B relation
  to the estimator → necessity/sufficiency → predict agreement strength; correlate. Prevention statements
  give a clean PREVENT arm. Caveat: these are knowledge-based generic claims, so a miss may reflect
  missing world knowledge rather than the typer — keep it a secondary validation behind Ranks 1–2.

---

## RANK 4 — Wolff (2007) *JEP:G* 136:82 / Wolff & Song (2003) *Cog Psych* 47:276 — **the paradigm, but scrape-blocked**

The original force-dynamics CAUSE/ENABLE/PREVENT categorization-proportion data.

- **Provenance:** `PUBLISHED_TABLE_VALUES` in principle, but **I could NOT verify the proportions off a
  fetch** — the philsci-archive PDF (https://philsci-archive.pitt.edu/3126/1/WolffJEPG20072.pdf) returned
  a WAF "Request Rejected". **I am NOT quoting any Wolff proportion — that would be `UNVERIFIED_MEMORY`.**
- **Why you can skip it:** Rank 1 (`causative-verbs`) is the modern, downloadable implementation of
  exactly this paradigm (same cause/enable/prevent verbs, same force-config→verb-judgment logic), so use
  that CSV instead of scraping Wolff's original tables. Papers remain citable for the theory.

---

## RANK 5 — Trabasso & van den Broek (1985) / Trabasso, van den Broek & Suh (1989) / Warren, Nicholas & Trabasso (1979) — **the "necessity in the circumstances" origin, but UNVERIFIABLE numbers**

This is the source of the reader's causal-network model AND of the physical/motivational/psychological/
enabling category scheme the solver hand-encoded. It is conceptually the closest to "necessity," but:

- **Provenance of any per-category mean necessity value:** `UNVERIFIED_MEMORY`. The 1985 paper is
  available only as a **scanned-image PDF** (https://cs.uky.edu/~sgware/reading/papers/trabassovandenbroek1985causal.pdf)
  — not text-extractable via fetch, and I have no poppler to OCR locally. The 1989 "Logical Necessity
  and Transitivity of Causal Relations in Stories" (*Discourse Processes* 12(1)) is where naive judges
  rated clause-pair relation strength, but I found no fetchable full text.
- **DO NOT** treat any specific physical/motivational/psychological/enabling necessity mean as ground
  truth from memory. **The hand-coded ordinal the solver is trying to escape traces to THIS scheme — so
  validating against a memory-reconstructed version of it would re-introduce the circularity.** Prefer
  Ranks 1–2 (both have verified numbers).
- If these specific numbers are wanted, the honest path is a library/institutional PDF pull + OCR, or an
  ILL request — not a memory quote.

---

## Also-ran (available but WRONG construct — noted so it isn't mistaken for a fit)

- **Ferstl, Garnham & Manouilidou (2011), implicit-causality corpus of ~305 English verbs** (Sussex
  Research Data / Psychonomic archive) — `FETCHABLE_FILE`, but it measures **NP1-vs-NP2 re-mention bias**
  (who the pronoun refers back to), NOT causal strength/necessity. Do not use as a causal-strength gold.

---

## Bottom line / recommended validation plan

1. **Primary (do this first):** `causative-verbs/data1.csv` — melt to (participant × scene × verb → yes/no),
   aggregate to proportion-yes per (scene, verb), parse `picture` into the force config, predict
   proportion-yes per cell from necessity+sufficiency, correlate across the 63 cells + check the
   cause/enable/prevent category structure. Fully fetchable, force-config stimuli, no hand-coded ordinal.
2. **Secondary (the discourse/network level this problem targets):** Kuperberg 2011 — predict the
   graded cross-sentence necessity ordinal against the verified condition means 6.37 / 4.79 / 2.14
   (1–7), using the stimulus triplets from the Edinburgh deposit.
3. **Tertiary (item-level breadth, incl. a PREVENT arm):** OSF `bvzvy` normed causality/prevention
   statements — read `codebooks` + `processing.rmd` for the exact scale/columns before using.
4. **Retire the Trabasso ordinal as "ground truth":** its per-category numbers are not verifiably
   sourceable here and re-using them re-introduces the circularity you are trying to remove.

**TLDR (plain):** The best real data I could actually download is a Stanford study where people watched
little physics animations and said whether words like "caused", "enabled", or "prevented" fit — that
is a direct, fair test for a force-based causal labeller, and the file is one click away. For the
"across two sentences" case (this problem's real target), a Tufts reading study gives trustworthy
average causal-strength scores (about 6.4 vs 4.8 vs 2.1 on a 1-to-7 scale for strong / medium / unrelated
links). A third public dataset rates everyday "X causes Y" statements. The old Trabasso necessity numbers
that the current hand-coded ordinal came from are NOT safely retrievable — I refuse to quote them from
memory, and using them again would just re-create the circular test you want to escape.

**QUESTIONS:** none.

**NEXT STEPS:** fetch `data1.csv` + `data2.csv`; build the `picture`→force-config parser; run the
necessity+sufficiency estimator over the 7 scenes; correlate predicted proportion-yes against observed
per (scene, verb). Then pull the Kuperberg triplets from the Edinburgh deposit for the cross-sentence arm.
