# Can the sensorimotor channel tell SET_P from SET_S at all? (2026-08-18)

Cell: `experiments/exp_sensorimotor_channel_discrimination_v1.py` (CODE_VERSION v1.2).
Pre-commitment: `notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md` sec 6.43, commit `73edbca69`, written
BEFORE the cell existed. Data risk register: `notes/admissible_supervision_sources_drill_2026-08-18.md`
sec 3.2. Disciplines that shaped it: `notes/STATUS.md` 13, 14, 15, 16, 18.

**THIS IS A DISCRIMINATION TEST, NOT A SUPERVISION BUILD.** Nothing was trained on the norms. The
question is only whether the signal can separate the two cells at all, because **a signal that
cannot discriminate cannot teach.**

---

## 1. Method, and what was reused rather than rebuilt

**The pairs are not mine.** They are the licensed dissociation instrument's own matched cells, taken
from its persisted checkpoint `data/exp_dissociation_score_instrument_v1/units.jsonl`, unit
`POPULATION|v1.7|full` -- the version whose `metrics.json` reads
`DISSOCIATION_INSTRUMENT_LICENSED__STOP_IF_iii_COOCCURRENCE_DIAGNOSIS_CONFIRMED`, 242 matched units,
all nouns. No matcher was written and **no caliper, stratum or threshold was loosened to buy n**; the
population only ever SHRANK. A regression gate re-asserts n_matched, the licensing block and every
post-match SMD against that `metrics.json` before anything runs.

**The row-order assumption was verified independently, not assumed.** The cell subsets the
instrument's persisted per-pair score arrays by index, which is only valid if `SCORES|v1.7|full` is
in the same row order as `POPULATION|v1.7|full`. `scratch/_verify_score_row_order.py` recomputes two
of those arms (`F_FREQUENCY`, `F_CONSTANT_PROTOTYPE`) from the words themselves: **exact match
(max abs diff 0.0 and 3e-08)**, and a shuffled-order control returns False, so the check can fail.

**The norms.** `data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv`, 39,707 rows
parsed, the 11 mean dimensions. Rows with any unparseable dimension are DROPPED, never imputed.
Brysbaert concreteness is loaded alongside as a clearly-labelled 1-dimensional REFERENCE arm.

**The sweep, and its resolution is part of the verdict (discipline 15).** 3 representations (RAW,
per-dimension Z, CENTERED) x 2 metrics (cosine, negative euclidean) = **6 grid points**, each scored
on **166 SET_P pair scores + 166 SET_S pair scores = 332 queries per point**. Population statistics
(means, sds, mean vector) come from the instrument's own covered word population, never from all
39,707 rows. Note what this grid does NOT sweep: **the channel's dimensionality**, which is the
variable branch (B) would indict.

---

## 2. Coverage, and what every control actually removed (discipline 16 corollary)

| stage | count |
|---|---|
| matched units from the licensed instrument | 242 |
| distinct words across both cells | 617 |
| of those, present in the Lancaster norms | **557 = 90.3%** |
| SET_P pairs with both words covered | 218 / 242 |
| SET_S pairs with both words covered | 187 / 242 |
| **matched units surviving (all FOUR words covered)** | **166 / 242** |
| **units REMOVED by the coverage filter** | **76** |
| candidate pairs dropped UPSTREAM by the licensed caliper | 3,555 of 3,912 SET_P candidates |

A unit is dropped unless all four of its words are covered: dropping one side would destroy the 1:1
matched structure the instrument was licensed on. **The 90.3% word coverage exactly reproduces the
drill's sec 3.2 figure** on this population, computed independently here.

**Controls that remove nothing by design still have to prove they are controls.** Each scramble floor
reports the fraction of pair scores it actually changed (1.0 for every arm), its rank-correlation
with the unscrambled arm, and a multi-seed distribution. That last one earned its place: at the
smoke's n=80 a single scramble draw landed at 0.6075 while the 5-seed distribution for the same arm
centred on 0.5073 -- **a single-seed scramble draw is a draw, not a floor value**, and it is flagged
as such. At n=166 the scramble floors sit where they should (0.4669 / 0.5000 / 0.5297 / 0.5056).

---

## 3. Floors rebuilt on THIS representation -- nothing imported

**0.5431, 0.5943 and 0.6317 appear nowhere in this cell.** They were computed on the bag, human and
arc representations respectively, and 21 arms are currently suspended in this repo for exactly that
error (`notes/AUDIT_floor_provenance_cross_representation_2026-08-18.md`). Every floor here is
recomputed on the 166 surviving pairs, and the two representation-sensitive ones are rebuilt on the
11-dim ratings: `F_CONSTANT_PROTOTYPE__SM11` (pair-mean of each word's cosine to the population mean
vector -- a query-independent genericity score) and `F_PROTOTYPE_MAGNITUDE__SM11` (pair-mean profile
norm), plus a per-arm `F_SCRAMBLE__<arm>` on the same representation.

**CREDIBLE BAR = the max floor's point value + THAT FLOOR'S OWN 95% half-width** (discipline 18). An
arm that beats the floor's point value but not the credible bar **is not a pass and is reported as
not a pass**.

**The instrument was re-licensed at the surviving n**, since shrinking a matched population can
unbalance it. All four of the instrument's own floors still CI-include 0.5 at n=166 (F_ORTHOGRAPHIC
0.5000, F_FREQUENCY 0.4851, F_SCRAMBLE 0.4557, F_CONSTANT_PROTOTYPE 0.5385), post-match SMD stays
tight (mean_log_freq -0.0617, mean_length 0.0026), and the incumbent store still reads 0.0884, far
below chance, exactly as the source run found. **One boundary case, disclosed rather than smoothed:**
the WordNet known-answer arm reads **0.9448 with 95% CI [0.9204, 0.9654]** against the instrument's
0.95 POINT gate -- it fails the strict point gate by 0.005 and passes the CI-inclusive gate. The
branch is driven by the CI-inclusive form and **both are printed on the verdict line every time**,
because declaring the whole measurement untestable on a 0.005 shortfall sitting well inside its own
CI would be discipline 14's error with the sign reversed. This was decided and written into the cell
docstring BEFORE the full run, after the smoke exposed it.

---

## 3b. What the 11 dimensions actually look like on this population (descriptive)

Read-only diagnostic, `scratch/_diag_sensorimotor_profile_structure.py`, same 166 units:

- **Both cells sit in a narrow cone.** Within-pair RAW cosine: SET_P mean **0.8768** (sd 0.0821),
  SET_S mean **0.8434** (sd 0.1006). The 11 ratings are all non-negative, so almost every pair of
  words is "similar"; the cells differ by a small mean shift on a compressed scale, which is exactly
  what a modest AUC on a low-resolution channel looks like.
- **The 11 dimensions are not 11 independent dimensions.** Participation-ratio effective
  dimensionality = **6.26 of 11**; the top 3 principal directions carry 61.0% of the variance.
- **SET_P words are slightly more prototypical than SET_S words** (mean prototype-cosine 0.9148 vs
  0.9037), which is the source of the constant/prototype floor's behaviour in section 4.
- 247 distinct SET_P words, 255 distinct SET_S words, 42 appearing in both cells.

---

## 4. RESULT -- BRANCH (B) FIRED, AND IT FIRED IN THE SHARPEST FORM AVAILABLE

`data/exp_sensorimotor_channel_discrimination_v1/metrics.json`, run mode full, 311 s, 20 arms,
**n = 166 matched pairs per cell.**

**VERDICT: `SENSORIMOTOR_DISCRIMINATION__B_AT_OR_NEAR_CONSTANT_PROTOTYPE_FLOOR`.**

**Best sensorimotor arm `SM11_Z_NEG_EUCLID`, AUC 0.6039, 95% CI [0.5439, 0.6644], half-width 0.0602
(paired-unit CI [0.5465, 0.6620]); credible bar 0.6791; margin -0.0752. It does not merely fail the
credible bar -- it sits BELOW the floor's own POINT value of 0.6195, by -0.0156.** Paired-swap null
p95 = 0.5502 (p = 0.0011), label-shuffle null p95 = 0.5520, tie mass 0.0 so both tie conventions
give the identical number.

| arm | AUC | 95% CI | hw | null p95 | vs bar 0.6791 |
|---|---|---|---|---|---|
| **F_CONSTANT_PROTOTYPE__SM11** (floor) | **0.6195** | [0.5599, 0.6792] | 0.0596 | 0.5530 | -- (sets the bar) |
| SM11_Z_NEG_EUCLID | 0.6039 | [0.5439, 0.6644] | 0.0602 | 0.5502 | **-0.0752 FAIL** |
| SM11_RAW_NEG_EUCLID | 0.6019 | [0.5403, 0.6619] | 0.0608 | 0.5523 | -0.0772 FAIL |
| SM11_CENTERED_NEG_EUCLID | 0.6019 | [0.5420, 0.6608] | 0.0594 | 0.5519 | -0.0772 FAIL |
| SM11_RAW_COSINE | 0.5990 | [0.5386, 0.6580] | 0.0597 | 0.5527 | -0.0801 FAIL |
| SM11_CENTERED_COSINE | 0.5381 | [0.4751, 0.5990] | 0.0619 | 0.5552 | -0.1410 FAIL |
| SM11_Z_COSINE | 0.5358 | [0.4735, 0.5969] | 0.0617 | 0.5543 | -0.1433 FAIL |
| F_PROTOTYPE_MAGNITUDE__SM11 (floor) | 0.4709 | [0.4103, 0.5345] | 0.0621 | 0.5515 | -- |
| F_ORTHOGRAPHIC (floor) | 0.5000 | [0.4880, 0.5120] | 0.0120 | 0.5000 | -- |
| F_FREQUENCY (floor) | 0.4851 | [0.4226, 0.5470] | 0.0622 | 0.5083 | -- |
| F_SCRAMBLE__<arm> (floors) | 0.4669 / 0.5000 / 0.5297 / 0.5056 / 0.5231 / 0.5000 | -- | ~0.062 | ~0.55 | -- |

**0 of 6 grid points clear the credible bar. All 6 have CIs that overlap the constant/prototype
floor's CI.** The two arms that fail hardest are the two that had the prototype direction removed.

### What the channel is actually doing, since "it fails" is not a mechanism

- **The discrimination that exists is mostly genericity, not relation.** A **query-independent**
  per-word score -- how typical a word's sensorimotor profile is, which never looks at the other
  member of the pair -- reads **0.6195, CI-separated above chance**, and BEATS every actual pairwise
  distance. Whatever these 11 numbers separate, they separate it without needing to compare the two
  words at all.
- **Centring confirms it.** Removing the population mean direction drops cosine from 0.5990 to
  0.5381 while leaving euclidean untouched at ~0.602 (euclidean is translation-invariant, so this is
  the expected signature): **the cosine arms' signal was largely carried by the shared prototype
  direction.**
- **The channel is not nothing, and I will not overstate that either.** Every euclidean arm is
  CI-separated above chance (p = 0.0006 to 0.0011) and every scramble floor sits at 0.4669-0.5297,
  so the ordering is real, not an artifact. **It is simply weaker than a score that ignores the
  relation.** Chance is not the bar; the floor is.
- **The cone is the reason.** Within-pair raw cosine is 0.8768 (SET_P) vs 0.8434 (SET_S) -- both
  cells sit in a narrow high-similarity cone because all 11 ratings are non-negative, and the
  channel's **effective dimensionality is 6.26 of 11**.

### The 1-dimensional reference arm, and an imbalance it exposes

`CONC1_NEG_ABSDIFF` (Brysbaert concreteness, one dimension) reads **0.5388 [0.4775, 0.6002]** against
**its own** credible bar of 0.6256 -- also a fail, also beaten by its own constant/prototype floor
(0.5646). **It is reported against its own 1-dim floors and is NOT part of the (A)/(B)/(C) decision.**

One thing it exposes deserves to travel: `F_PROTOTYPE_MAGNITUDE__CONC1` -- pair-mean concreteness,
one query-independent number per word -- reads **0.3195 [0.2640, 0.3772], CI-separated BELOW chance**,
i.e. **SET_S pairs are reliably MORE concrete than SET_P pairs (a two-sided floor strength of
0.6805).** The matched population is balanced on the store's four floors and is **NOT** balanced on
rating-norm properties. That is discipline 16 demonstrated live: **a floor is a property of the
representation, and this population acquires new floors the moment it is viewed through a new one.**

### Is the negative real? (discipline 17's first question, asked before any brain talk)

Yes, and each check is a measurement, not an assurance:
1. **The instrument is still licensed at n=166** -- all four of its own floors CI-include 0.5;
   known-answer 0.9448 [0.9204, 0.9654] (strict point gate FAIL by 0.005, CI-inclusive gate PASS,
   both printed); incumbent store still 0.0884.
2. **The cell can return (A).** Its planted-separable self-test runs at the deciding n and must read
   AUC > 0.95 with CI lower bound > 0.9 or the cell aborts. **The discriminator is proven able to
   fire at the scale that decides.**
3. **The controls are real controls.** Scramble changes 100% of pair scores and decorrelates;
   the coverage filter removed 76 units; the upstream caliper dropped 3,555 candidates.
4. **This is not a power problem, and that matters.** More n would tighten the bar (166 -> ~770 for
   a +-0.03 floor half-width), but **the best arm is below the floor's POINT value**, so no amount
   of extra precision converts this into a pass. The ordering is wrong, not just the resolution.

### Brain-fidelity drill (discipline 17; internal reasoning only, no external query)

**Which structure?** The transmodal hub (ATL) fed by modality-specific cortices -- pinned by semantic
dementia, inhibitory rTMS, and impaired acquisition after ATL damage.
**Are we replicating it or substituting something convenient?** **Substituting.** The hub integrates
high-dimensional patterns arriving from each sensory cortex. We handed it **one scalar per modality,
derived from humans REPORTING ON their experience of a word** -- a summary about experience, not the
convergent code itself. Measured here, that summary has 6.26 effective dimensions.
**What would close the gap?** Not a better metric over these 11 numbers -- the sweep already shows
the metric is not the binding constraint. Either (i) **more dimensions**, or (ii) **a different KIND
of signal**: relations derived from images rather than ratings about words, which is convergence
rather than description.

### What resolution would be needed -- the trade, stated rather than the conclusion 6.43 forbids

**THIS IS A REFUTATION OF THIS RESOLUTION, NOT OF GROUNDING.** Binder's 65 dimensions discriminate
far better but cover **9.2% of eval words / 5.0% of anchors**. On this instrument a unit needs all
four of its words covered; Lancaster's 90.3% word coverage already costs 76 of 242 units, so at
9.2% word coverage the surviving-unit count collapses to essentially nothing -- **far below the
"a win on 20 pairs is not a win" line.** So the honest statement is a **COVERAGE-RESOLUTION TRADE
with no currently-held asset on the good side of it**: the high-resolution norms cannot reach this
population, and the norms that reach it lack the resolution. The named third option is the
**image-derived relational subset (57.9% of eval words)**, which changes the KIND of signal rather
than trading coverage for dimensions -- and it is a separate cell with its own pre-commitment.

**What this closes.** The sensorimotor RATING channel is not an admissible teaching signal for
SET_P/SET_S substitutability at this resolution, and **nothing downstream should be built on it.**
One cell spent, not five, which is what 6.43 was for.

---

## 5. Artifacts

- cell: `experiments/exp_sensorimotor_channel_discrimination_v1.py` (v1.2)
- FULL metrics: `data/exp_sensorimotor_channel_discrimination_v1/metrics.json` (+ `units.jsonl`, per-arm)
- smoke metrics: `data/exp_sensorimotor_channel_discrimination_v1_reduced/metrics.json`
- logs: `scratch/sensorimotor_full_stdout.log`, `scratch/sensorimotor_full_stderr.log`, PID file
  `scratch/sensorimotor_full.pid`
- row-order verification: `scratch/_verify_score_row_order.py`
- descriptive structure diagnostic: `scratch/_diag_sensorimotor_profile_structure.py`
- coverage probe: `scratch/_probe_sensorimotor_coverage.py`

**Prior work built on, with credit:** `experiments/exp_grounding_measured_attribute_concreteness_v1.py`
(join convention, scrambled-attribute control, load-bearing-channel discipline) and
`notes/sensorimotor_anchoring_scope_2026-08-13.md` (a coverage/scope analysis on a DIFFERENT
population -- banked store facts and blind samples -- which shelved sensorimotor anchoring as a
read-out filter; its finding that **Lancaster and Brysbaert are near-perfectly nested** is
independently reproduced here: 166 units survive Lancaster, 167 survive Brysbaert, **166 in common**).
Its retained AUC 0.685 and its 0.8060/0.8071 random-word-pair figures are from that other instrument
and population and are **NOT** imported or compared to anything here.
