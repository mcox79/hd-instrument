# Research deep-dive: UN-enumerated experimental biases (2x drill) 2026-06-24

**Date:** 2026-06-24
**Role:** research (Opus 4.7 1M)
**Trigger:** USER directive 2026-06-24: "do a deep dive on potential sources of bias, and plan
experiments carefully with that in mind. We can't keep including this kind of bias at this stage."
**Companion to:** `feedback_experiment_bias_master_checklist_USER_2026-06-24.md` (12 categories A-L)
plus `notes/skunkworks_experiment_bias_audit_2026-06-24.md` (22-cell audit) plus
`notes/research_apples_to_apples_substrate_evaluation_methodology_2x_drill_2026-06-24.md`.
**Time budget:** 60-90min thorough.
**Calibration penalty:** 0.20 deflation on prevention-effectiveness claims.

---

## HEADLINE

The Director's 12-category master checklist (A-L) covers 80-85% of biases that have already bitten
us, organized at the right level. **15 additional bias families are absent or under-emphasized**.
The 5 most likely to bite us next are: **(1) GARDEN-OF-FORKING-PATHS in cell-author latitude**
(observed in fair_harness HARD_PASS via OR-gated metric), **(2) SELECTION BIAS in best-of-N arm
reporting** (recurring Fix #28 root cause), **(3) PROVENANCE-PORT FAILURE WITHOUT TRANSFER-RAIL**
(burned n1v3_x_cfrpe v1 and v2_BUGFIX), **(4) CONFOUNDED-MECHANISM IN STACKED ARMS** (cf-RPE +
adaptive-LR + median-normalization confound; can't isolate which knob helps), and
**(5) META-METRIC BIAS** (we keep choosing the metric that flatters the mechanism after seeing
data — implicit HARKing on metric selection, not just hypothesis). All 5 are structural patterns
the existing 12 categories touch only obliquely.

P_deflated (this 15-bias supplement catches >70% of future occurrences) = **0.62** (calibration
penalty 0.20 + asymmetric prior that meta-biases recur more than first-order biases caught).

---

## SECTION 1 -- MISSED BIAS FAMILIES (15 new)

Each entry: description / substrate manifestation / concrete example from our history / prevention
checklist item.

### M1 -- Garden-of-Forking-Paths (Gelman-Loken 2013)

**Description:** Cell-author makes many implicit choices (thresholds, sub-arms, OR-gated metric
boolean, smoothing alpha, T/lambda grid resolution) where ANY one set of choices that produces a
PASS gets reported. Different choices would produce different outcomes from the same data, but
only one is reported. Not p-hacking (no malicious search), but the analytic path is contingent
on what the data showed.

**Substrate manifestation:** Every cell has 5-15 hyper-parameter choices (TEMP_GRID resolution,
LAMBDA_GRID density, alpha-Laplace, top-K vs argmax, BPC vs top1 OR-gated, cv tolerance, smoothing
window). With 5 binary choices, there are 32 paths; with 10 there are 1024. If the cell-author
chooses freely, the reported result is one of many.

**Concrete example:** `substrate_pc_hierarchy_fair_harness_v1` reported HARD_PASS with d_top1=+0.005
d_bpc=+0.085 under OR-gated metric (one-of-three clears = HARD_PASS). The +0.005 top1 is below cv;
the BPC is real but small. The OR-gated metric is itself a choice; a strict AND-gate would have
yielded HARD_FAIL or MIDDLE_BAND. The author was not malicious; the choice was made before
results, but the metric structure is itself a forking path.

**Prevention:** **NEW PRE-DISPATCH ITEM (#11)** -- declare in the cell prereg: the SINGLE primary
metric (no OR-gate); the SINGLE pre-registered threshold (no band-tweaking); the EXACT cv
tolerance; if OR-gated metric is needed for a multi-axis question, the pre-reg must explicitly
declare "this is a multi-axis discrimination, not a single-pass HARD_PASS." OR-gated PASS is
demoted to MIDDLE_BAND by default.

### M2 -- Best-of-N selection bias on arm reporting

**Description:** Cell runs N arms; the BEST arm gets propagated as if it were a single
pre-registered test. This conflates selection-after-data with prior hypothesis. The probability
that at least one of N independent arms exceeds threshold t by chance is 1 - (1 - p)^N, which is
>> p for N >= 5.

**Substrate manifestation:** Cells routinely run 4-8 arms (e.g., compose cells, sparse-f sweeps,
T-lambda sweeps). The MAX over 8 arms with per-arm p=0.10 has overall p ~ 0.57. Reporting the
best-arm as "substrate HARD_PASSed" is selection-bias-confounded.

**Concrete example:** `substrate_cfrpe_per_token_adaptive_lr_v1` reported MIDDLE_BAND with best
adaptive arm bpc=6.992 lift=0.345 over Hebbian. Across 4-6 adaptive variants, the BEST got
propagated. Per `feedback_fix28_violation_count_internalize_harder_2026-06-22` Skunkworks caught
this 4x in one session. The fix is structural: pre-register WHICH arm is the primary test.

**Prevention:** **NEW PRE-DISPATCH ITEM (#12)** -- in multi-arm cells, declare the PRIMARY arm
(by name) in the prereg before dispatch. Other arms are exploratory. The PRIMARY arm's verdict is
the cell's verdict; best-of-N is reported as exploratory secondary. Apply Bonferroni-style
correction (HARD_PASS threshold * N) when reporting best-arm as "anything substantive happened."

### M3 -- Provenance-port failure without an explicit transfer rail

**Description:** Cell claims to PORT a result from World A (corpus X + encoder Y) to World B
(corpus X' + encoder Y'). Without an explicit "transfer rail" arm that reproduces the source result
on the source world FROM THE NEW CELL, there is no way to know if the failure is the port itself
or the mechanism under test.

**Substrate manifestation:** Multi-world experimental program (text8/word2vec vs Pythia-residuals
vs synthetic) creates frequent port-attempts. Without a transfer rail, every port that fails
PROVENANCE_FAILs ambiguously -- the cell cannot distinguish "the mechanism doesn't compose with
this corpus" from "the port itself broke the source result."

**Concrete example:** `substrate_n1v3_readout_x_cfrpe_plasticity_compose_v1` AND `v2_BUGFIX` both
PROVENANCE_FAILed at ARM_N1_V3_READOUT_HEBBIAN top1=0.21 vs cert anchor 0.4455. The cell could not
distinguish "n1_v3 readout doesn't help cf-RPE" from "the corpus port from Pythia-residuals to
text8/word2vec itself broke the n1_v3 mechanism." Per
`research_n1v3_provenance_audit_2x_drill_2026-06-24.md`: corpus + encoder + V_TOK + N_DIM all
changed; only k=25 was matched.

**Prevention:** **NEW PRE-DISPATCH ITEM (#13)** -- any cross-corpus or cross-encoder port MUST
include an ARM_TRANSFER_RAIL that reproduces the source-world result on the source-world data using
the ported cell's pipeline. If the transfer rail fails, the port itself is broken -- not the
mechanism. Without this arm, no PORT cell can be dispatched.

### M4 -- Confounded-mechanism in stacked arms

**Description:** Arm includes multiple mechanism changes simultaneously. Even if HARD_PASSes, the
contribution of each mechanism is unknown. Subsequent atomization claims credit for the wrong
mechanism.

**Substrate manifestation:** Many compose cells stack 2-4 mechanisms (e.g., cf-RPE + adaptive-LR +
median-normalization + per-context T + sparse-encoder). If the stack HARD_PASSes, the cell does
not isolate which knob did the work. The Director may atomize "cf-RPE works" when actually
"median-normalization works."

**Concrete example:** `substrate_pc_hierarchy_fair_harness_v1` -- "cf-RPE is in the compounded arm
so the PC contribution cannot be isolated cleanly" (Skunkworks audit). Other example: cf-RPE
adaptive-LR cells bundle 3 changes (per-token adaptive LR + median normalization + gradient
clipping) and report the bundle's lift; the per-mechanism contribution is unknown.

**Prevention:** **NEW PRE-DISPATCH ITEM (#14)** -- in compose cells, the cell MUST include a
sequence of arms that adds ONE mechanism per arm starting from the baseline. ARM_BASELINE +
ARM_M1 + ARM_M1_M2 + ARM_M1_M2_M3 etc. If only the full-stack arm runs, the cell is FACTORIAL_
INCOMPLETE and only the bundle (not the components) can be atomized.

### M5 -- Meta-metric bias (choose-metric-after-data is HARKing on metric)

**Description:** Cell measures multiple metrics (BPC + top1 + MRR). After data lands, the metric
that supports the mechanism is selected for the verdict. This is a structural version of HARKing
where the hypothesis itself isn't reframed but the metric is.

**Substrate manifestation:** META_HARNESS_RIGGED case is the canonical example: cells originally
reported HARD_FAIL on BPC; Skunkworks reclassified to chain-grade at top1. This was honest
retrospective re-classification, but the META RISK is that AS A POLICY we could lock in this
inversion -- "if BPC fails but top1 passes, the top1 wins" -- which is HARKing on metric. The
post-hoc rescue is justified once (when the metric itself is shown rigged), but if applied
routinely, it's metric-selection bias.

**Concrete example:** cert_ledger row 699 carries `cert_class=post_hoc_pass` -- this is the
honest reclassification of n1_v3 chain-grade from top1. Two such post-hoc passes exist in the
ledger. Each is justified (BPC IS rigged for sparse-top-1 substrates), but each creates a precedent
risk for future re-metricking.

**Prevention:** **NEW PRE-DISPATCH ITEM (#15)** -- in any multi-metric cell, the PRIMARY metric
must be declared in the prereg before data lands. If post-hoc the alternative metric tells a
better story, the cell verdict stands on the PRIMARY metric and the alternative-metric finding is
recorded as a DIAGNOSTIC observation with explicit "metric-selection retrospective" tag. Post-hoc
metric-flip is allowed only with explicit cert atom for the metric itself being shown invalid
(META_HARNESS_RIGGED precedent).

### M6 -- Survivorship bias in landed-vs-killed cell population

**Description:** The cell population that lands and gets reported is non-random. Cells that
crashed, OOMed, were killed, or had bugs caught during smoke are NOT in the audit. The "landed
cells" set is survivorship-biased toward cells that worked well enough to complete. Inferences
about "substrate mechanisms" from landed-only data overweight mechanisms that PRODUCE COMPLETIONS
(not mechanisms that produce TRUTH).

**Substrate manifestation:** ~3983 exp directories scanned; cert_ledger has ~707 rows. The
difference (~3000+) is killed/OOM/incomplete cells. Mechanisms that have a higher kill rate
(e.g., dense modern-Hopfield with high beta) are under-represented in landed atoms.

**Concrete example:** Modern-Hopfield arms have repeatedly OOMed or crashed at larger scale (eval
notes); landed MH cells are at smaller scale where MH performs poorly. The landed population
under-represents MH at the regime where it might shine.

**Prevention:** **NEW PRE-DISPATCH ITEM (#16)** -- track KILLED cells in cert_ledger as
SURVIVAL_FAIL rows (not omitted). When atomizing "mechanism X doesn't work," check whether the
mechanism's kill rate is higher than baseline; if yes, the mechanism may simply be infrastructure-
fragile and not under-test.

### M7 -- Multiple-comparison correction across the cell program

**Description:** Across 707+ ledger rows, the family-wise error rate is enormous. If each cell's
HARD_PASS has type-I error rate 0.05, then 707 cells produce ~35 false positives by chance under
the null. None of the chain-grade rows have FWER correction applied.

**Substrate manifestation:** The cap_map has ~30-50 mechanisms being tested; each has multiple
cell variants. With 30 mechanisms x 3 cell variants each, total tests ~ 90; Bonferroni-corrected
threshold would be 0.05/90 ~ 0.0006. None of the chain-grade rows test against this.

**Concrete example:** Cap_map row M_c=200 chain-grade at K=15 / 1.000 top1: this is a 1-sided test
where the prior was "M_c>=200 is hard." With many M_c variants tested, the one that passed could
be selection bias. Likely not in this case (cv=0, by-construction-saturation tier ruled by
Skunkworks), but the pattern recurs.

**Prevention:** **NEW PRE-DISPATCH ITEM (#17)** -- periodic FWER audit (quarterly?) on cap_map
chain-grade rows: count cells dispatched per row's mechanism; if more than 10 dispatches led to 1
PASS, flag the row as needing replication or stricter pre-reg threshold.

### M8 -- Reverse causation in metric correlations

**Description:** Cell reports "mechanism M correlates with metric Y" and infers M -> Y. Reverse
causation (Y -> M) or common-cause confounding may explain it.

**Substrate manifestation:** Most cell-level inferences are straightforward (we manipulated M, Y
changed). But CROSS-CELL inferences (e.g., "cells using cf-RPE tend to have higher top1") can be
confounded -- the cells using cf-RPE may also be the well-engineered cells with strong baselines,
so the correlation is "engineering quality -> top1" not "cf-RPE -> top1."

**Concrete example:** The +12% top1 lift attributed to cf-RPE family is consistent across cells,
but those cells share many other engineering improvements (fair_harness encoder, word-level
metric, sparse-bipolar at f=0.05). Some of the lift is engineering, some is cf-RPE.

**Prevention:** **NEW PRE-DISPATCH ITEM (#18)** -- cross-cell mechanism attribution requires an
explicit "engineering-matched control" cell where everything except the mechanism is held
constant. Without this, cross-cell mechanism claims are CORRELATIONAL only.

### M9 -- Hardware / numerical-precision drift

**Description:** Results subtly differ across hardware (CPU vs GPU vs different GPUs), precision
(float32 vs float64 vs mixed), and deterministic-vs-stochastic ops (CUDA non-determinism, BLAS
threading order).

**Substrate manifestation:** Cells dispatched to local_cpu vs overnight_queue (remote, may be CPU
or GPU) vs remote_gpu. The same cell can produce slightly different metrics due to
floating-point order. Cv tolerance of 0.10 absorbs most, but borderline HARD_PASS / MIDDLE_BAND
cells could flip across hardware.

**Concrete example:** Surprise-baseline 7.22 vs 7.30 audit (research note 2026-06-24): the +0.08
BPC difference was traced to ENCODER differences, not hardware -- but the very fact that we ran
the audit reveals the suspicion that hardware drift could explain cell-to-cell differences. We did
not pre-register hardware tolerance.

**Prevention:** **NEW PRE-DISPATCH ITEM (#19)** -- borderline HARD_PASS cells (lift within 1.5x
cv of threshold) must be re-run on different hardware (local vs remote) to confirm. Hardware
provenance (CPU brand, GPU model, torch version, numpy version, BLAS threads) should be logged in
metrics.json. Cv tolerance should be at least 1.5x typical seed-cv when hardware crosses.

### M10 -- Held-out set contamination (silent leakage)

**Description:** Held-out test set has leakage from train. Even if the data split is correct, the
ENCODING may leak (e.g., word2vec was trained on data that includes test sentences; char-trigram
encodes test n-grams from training).

**Substrate manifestation:** **THIS IS LIKELY ALREADY HAPPENING** -- word2vec-google-news-300 was
trained on Google News, which has substantial overlap with Wikipedia (text8 source). The encoder
sees text8-vocabulary tokens in its training data. char-trigram encodes orthographically and
generalizes by structure, so less leak-prone. Pythia-160m residuals are on Pythia training data
which DEFINITELY includes Wikipedia.

**Concrete example:** `substrate_fair_harness_substrate_as_lm_v1` uses word2vec-google-news-300 as
encoder. text8 is stripped Wikipedia. Google News + Wikipedia: significant n-gram overlap. The
ENCODER has seen variants of the test sentences; substrate has nominal-leak via encoder.
Similarly n1_v3 uses Pythia-160m which was trained on Wikipedia; the "Pythia residual" already
contains the next-token prediction signal Pythia learned. Substrate is reading out a pretrained-LM
signal, not learning afresh.

**Prevention:** **NEW PRE-DISPATCH ITEM (#20)** -- declare in the prereg the encoder's training
corpus and whether it overlaps with the test corpus. If overlap, the cell must be tagged
"ENCODER_LEAKAGE_POSSIBLE" and the chain-grade-eligible bar must include a "clean-encoder" arm
(e.g., word2vec re-trained on text8 only, or char-trigram which is corpus-free).

### M11 -- Implicit assumptions in HRR algebra

**Description:** HRR and FHRR algebra implicitly assume orthogonality of role vectors, cosine
similarity as distance, and unitary binding operations. These assumptions can fail silently when:
role vectors are correlated; cosine is dominated by mean-bias; binding is non-unitary near
saturation.

**Substrate manifestation:** Role vectors are randomly drawn; with N=8192 and 4-8 roles, near-
orthogonality holds. But under SAME-W STACKING (per `feedback_apples_to_apples`), roles can
become correlated as W absorbs role-target correlations.

**Concrete example:** `substrate_compositional_K10_K20_reconfirm_n8192_v1` K=20 1.000 top1 at
N=8192. Why HARD_PASS while same-W stacking is known broken? Because the cell does NOT stack on
same W -- it builds a single W with all transitions, then composes via iterated sign(Wq). This is
intra-W not cross-primitive-on-W stacking. The HRR algebra assumptions hold.

**Prevention:** **NEW PRE-DISPATCH ITEM (#21)** -- in any HRR/FHRR cell, the prereg must declare
the role-vector generation (random IID vs structured) and the binding scope (unitary at this N?).
If cell stacks multiple primitives on same W, declare why HRR algebra assumptions still hold (or
acknowledge they don't and atomize as DIAGNOSTIC tier).

### M12 -- Single-seed exploration driving multi-seed design

**Description:** Cell-author runs single-seed quick smokes during development; the design that
"looks good" at single seed gets promoted to 3-seed cv. The single-seed result is selection-biased
(cell-author iterated until single-seed was good).

**Substrate manifestation:** Smoke runs are 1-seed. The Cell-author smoke gate per Fix #17 is
itself a survivorship filter -- cells that smoke well at single seed get promoted; cells that
smoke poorly are revised. By the time the 3-seed cv runs, the cell is selection-biased toward
configs that smoke well.

**Concrete example:** Multiple compose cells went through smoke-debug-smoke-debug cycles before
production. The production result is conditional on "passed smoke," which is itself a 1-seed
single-config test.

**Prevention:** **NEW PRE-DISPATCH ITEM (#22)** -- smoke gate is for PIPELINE CORRECTNESS only
(no NaN, runs to completion, produces metrics) NOT for "does mechanism work." Smoke does NOT
inform cv-tier verdict bands; cv bands must be pre-registered BEFORE smoke.

### M13 -- Replication-failure as evidence (Type II error)

**Description:** A cell HARD_FAILs and we update toward "mechanism is broken." But underpowered
cells will HARD_FAIL even when mechanism is real. Without power analysis, HARD_FAIL is ambiguous.

**Substrate manifestation:** Many cells have 3-seed cv but the effect size we're looking for is
small (lift 0.05 BPC). Power to detect 0.05 with cv-noise 0.10 at N=3 is poor (~30% power). Most
HARD_FAILs are underpowered.

**Concrete example:** `substrate_pc_hierarchy_fair_harness_v1` HARD_PASSed on d_top1=+0.005 with
cv=0.020 -- the lift is ~ 0.25 standard deviations, which is well below the typical detection
threshold. The opposite case: many MH-beta cells HARD_FAILed with lifts around 0.03-0.04 which is
within cv-noise.

**Prevention:** **NEW PRE-DISPATCH ITEM (#23)** -- declare in the prereg the EXPECTED EFFECT SIZE
(prior P estimate) and the POWER given the cv at 3 seeds. If power < 70%, the cell is
under-powered and either seeds must be increased or the HARD_FAIL verdict is demoted to
INCONCLUSIVE.

### M14 -- Reporting precision masking real effect

**Description:** Reporting lift to 3 decimal places when cv is 0.02 creates an illusion of
precision. "+0.005 top1 lift" looks meaningful but is well within noise.

**Substrate manifestation:** Verdict_msgs frequently report lifts like "+0.0125" or "+0.043" --
the precision exceeds the noise. Round-number bias (0.05 HARD_PASS threshold) creates implicit
selection on the right side of round numbers.

**Concrete example:** `substrate_dynamic_f_phase_shift_sparsity_v1` HARD_FAILed at +0.04 lift vs
pre-reg +0.05. The +0.04 lift is direction-correct and well above cv (~0.001); arguably this is
MIDDLE_BAND not HARD_FAIL. Round-number threshold (0.05) made a real effect look like a failure.

**Prevention:** **NEW PRE-DISPATCH ITEM (#24)** -- the HARD_PASS threshold must be tied to
multiple of cv-noise (e.g., "lift >= 3*cv" or "lift >= 0.05 AND lift >= 2*cv"). Round-number
thresholds without a noise tie create round-number bias.

### M15 -- Director-Skunkworks disagreement protocol unclear

**Description:** When Director claims chain-grade and Skunkworks tiers down (or vice versa), the
DEFAULT resolution policy is not formally written. In practice, Skunkworks wins by Fix #28
discipline, but this is convention not protocol.

**Substrate manifestation:** Repeated Fix #28 violations recur; the resolution is always
Skunkworks tiering down. This is the right resolution (cert-owner override), but the recurrence
suggests the protocol is implicit rather than enforced.

**Concrete example:** Per `feedback_fix28_recurring_skunkworks_correct_more_than_director_2026-06-23`,
"Skunkworks consistently CORRECTLY overrides Director on by-construction-saturation." This is the
8+ recurrence cited in master checklist intro.

**Prevention:** **NEW PRE-DISPATCH ITEM (#25)** -- formal disagreement resolution: when Director
claims chain-grade and Skunkworks tiers down within 24h, the LOWER tier stands. Director may
appeal but must produce new evidence (not re-framing). This is current convention; making it
explicit removes ambiguity.

---

## SECTION 2 -- WHICH MASTER-CHECKLIST CATEGORIES CAN MERGE OR ELEVATE

### Merge candidates (over-enumerated, can collapse)

- **F1 (Fix #28 recurring) + F2 (Director-overclaim)**: same root cause (verdict-msg-vs-per-arm-
  metric discrepancy). Merge into a single category F: "Verdict-vs-data integrity."
- **A1 (corpus type mismatch) + A4 (domain mismatch)**: both are corpus-level mismatches at
  different granularities. Merge into A: "Corpus identity mismatch" with sub-types.
- **C1 (BPC vs top1) + C3 (substrate vs external paradigm)**: both are metric-paradigm mismatches.
  Merge into C: "Metric-paradigm alignment" with sub-types.

### Priority elevation candidates

These categories are correctly enumerated but UNDER-EMPHASIZED relative to their bite-frequency:

- **J1 (Pythia-residual not substrate-native)** -- elevate; this directly burned 2 cells
  (n1v3_x_cfrpe v1 + v2_BUGFIX). Should be one of the top-3 priorities, not bottom of J.
- **H1 (capacity-respecting tier)** -- elevate; Skunkworks override 8+ times this session is
  predominantly this category. Should be top-3.
- **L1 (corpus-as-evaluation)** -- newest insight, USER-directed. Should be elevated to top-5
  prominence, not bottom of L.

### Categories that may be OVER-emphasized

- **B5 (amplitude scaling)** is enumerated but is itself a SOLUTION-CLASS issue (the 1/sqrt(f)
  fix). It is not a bias-class -- it is a fix that was implemented. Demote to a "fixes-applied"
  appendix.
- **E1 (same-W stacking)** is documented as broken; subsequent cells avoid this. The bias is
  EXTINCT in current practice. Demote or remove from active checklist.

---

## SECTION 3 -- TOP 5 MOST LIKELY TO BITE US NEXT

Ranked by (probability of recurrence x cost of recurrence):

### #1 -- Garden-of-Forking-Paths via OR-gated metric

**Probability:** 0.70 (OR-gated metric is common in compose cells).
**Cost:** HIGH (false HARD_PASS atomization corrupts cap_map).
**Mitigation:** Single primary metric required at pre-reg.

### #2 -- Best-of-N selection bias in multi-arm cells

**Probability:** 0.75 (multi-arm cells are 60%+ of recent dispatches).
**Cost:** MEDIUM (false mechanism attribution).
**Mitigation:** Pre-register PRIMARY arm; best-of-N is exploratory only.

### #3 -- Provenance-port failure without transfer-rail

**Probability:** 0.50 (cross-world ports are 20-30% of in-flight cells).
**Cost:** VERY HIGH (compose cells PROVENANCE_FAIL ambiguously; mechanism vs port confounded).
**Mitigation:** ARM_TRANSFER_RAIL mandatory for any port.

### #4 -- Confounded-mechanism in stacked compose arms

**Probability:** 0.60 (compose cells stack 2-4 mechanisms routinely).
**Cost:** MEDIUM (false credit attribution to one mechanism).
**Mitigation:** Per-mechanism ablation arm sequence required.

### #5 -- Encoder-leakage (word2vec / Pythia training corpus overlaps test)

**Probability:** 0.40 (already happening; we just haven't quantified).
**Cost:** VERY HIGH (chain-grade atoms may be measuring pre-trained-LM ability, not substrate).
**Mitigation:** Declare encoder training corpus; clean-encoder arm where possible.

---

## SECTION 4 -- BRAIN-EXISTENCE-PROOF BIASES

(Per directive: "bias-source from biological vs computational mismatch is also legit")

### B1 -- Brain implements ALL its mechanisms in parallel; substrate cells test in isolation

Brain runs CLS-replay + cf-RPE + STDP + sparse-coding + theta-gamma SIMULTANEOUSLY. Substrate
cells test ONE mechanism at a time. The isolation may break mechanisms that only work in
conjunction. **Prevention:** declare "isolated-arm-tested" tag on per-mechanism atoms; full-stack
compose cells get separate tier.

### B2 -- Brain has development; substrate has random init

Brain wiring is developmentally optimized over years. Substrate weights are random at init.
Brain mechanisms tested at random-init may underperform because the substrate is in a wrong
initial regime.

**Prevention:** pre-train substrate on a development-equivalent corpus before testing brain
mechanism; or acknowledge that random-init substrate is a HARD test the brain doesn't face.

### B3 -- Brain operates at metabolic constraint; substrate doesn't

Brain mechanisms are selected against energy cost. Substrate has no energy budget. Substrate may
adopt brain mechanisms that are good for energy-efficiency but mediocre for performance, missing
the strict-performance variants the brain rejects on energy grounds.

**Prevention:** when adopting a brain mechanism, audit whether the brain's choice is performance-
optimal or energy-optimal; substrate has no energy constraint and may want the performance-optimal
variant.

### B4 -- Brain mechanism timescales are tied to wall-clock; substrate has no wall-clock

Brain mechanisms use ms / sec / min / hr timescales (per the 5-tier clock hierarchy drill). Substrate
maps these to per-token / per-chunk / per-epoch BUT THE MAPPING IS ARBITRARY. A brain mechanism
tuned at hippocampal-replay timescale (sec) may map to per-chunk (10 tokens) or per-window (100
tokens); both are valid, both produce different results.

**Prevention:** declare in prereg the chosen substrate-tick-per-brain-second mapping; sensitivity
analysis on the mapping.

---

## SECTION 5 -- META-BIAS: BIASES IN OUR BIAS AUDITS

Recursive issue: this audit and the master checklist could themselves be biased.

### M-meta-1 -- Confirmation bias in audit selection

We audit cells the Director flagged as suspicious. Cells the Director did NOT flag (chain-grade,
"clean") may have biases we didn't look for.

**Mitigation:** periodic random-sample audit of "clean" cells (1 in 10 chain-grade rows audited
by independent Skunkworks pass).

### M-meta-2 -- Anchoring on Fix #28

Master checklist anchors heavily on Fix #28-class biases (verdict_msg vs per-arm metric). Other
biases (this drill's M1-M15) may be under-emphasized because the anchor pulled attention to
verdict_msg level.

**Mitigation:** this drill itself; periodic 3x deep audit on under-emphasized categories.

### M-meta-3 -- Selection on which biases were CAUGHT

Master checklist documents biases that were caught. Biases that we missed entirely are by
definition absent from the checklist. The M1-M15 in this drill are biases that COULD have been
caught but weren't surfaced as formal categories.

**Mitigation:** literature audit (this drill's references); cross-domain bias-class import from
statistics / social science / cognitive science methodology.

---

## SECTION 6 -- SUBSTRATE-PRODUCT IMPLICATIONS

The bias-prevention work IS substrate-product work, not just methodology hygiene:

1. **Cert atoms are PROVENANCE GUARANTEES.** Each cert atom carries (mechanism, corpus, encoder,
   N_DIM, vocab, metric, baseline). Adding bias-tags to cert atoms (e.g., ENCODER_LEAKAGE_POSSIBLE,
   PROVENANCE_PORT_FAIL) makes the cert atom a richer downstream contract.

2. **The substrate-product narrative is "auditable AI memory subsystem."** Auditability requires
   bias-traceability. A clean bias checklist (the master + this supplement) is the substrate
   product's CORE deliverable, not a side concern.

3. **Refuse-gate is itself a bias-prevention mechanism.** When substrate refuses to answer a query
   outside its train distribution, it is refusing to be subject to the cross-world / cross-corpus
   biases listed here. Refuse-gate IS the product version of "we know our biases."

4. **The 4-lane evaluation framework** (apples-to-apples drill) is the substrate-product
   evaluation contract. Each lane has its own bias profile; cross-lane bias is the dominant risk.

---

## SECTION 7 -- FALSIFIABLE PREDICTIONS (HARD-PASS + HARD-FAIL)

### Prediction 1: Pre-dispatch checklist items #11-#25 catch 70%+ of future biases

**HARD-PASS:** in the next 50 cells dispatched, the 15-item supplement (M1-M15) catches at least
35 cases at pre-dispatch (>70%).
**HARD-FAIL:** the supplement catches fewer than 20 cases (<40%) -- indicates the categories are
mis-specified or biases recur in different forms.
**P_deflated:** 0.62

### Prediction 2: Best-of-N (M2) is the top bias source in current pipeline

**HARD-PASS:** in the next 30 multi-arm cells, M2 (best-of-N selection) is the most-flagged bias
category at pre-dispatch.
**HARD-FAIL:** M2 is flagged in fewer than 10/30 cells -- indicates current practice has already
mitigated this.
**P_deflated:** 0.55

### Prediction 3: Encoder leakage (M10) is detectable in fair_harness vs clean-encoder split

**HARD-PASS:** running fair_harness with word2vec-trained-on-text8-only (clean encoder) reduces
top1 by 0.02 to 0.10 vs the leaked word2vec-google-news version (i.e., substrate was riding on
encoder leak).
**HARD-FAIL:** clean-encoder version yields top1 within +/- 0.01 of leaked version (no
detectable leak).
**P_deflated:** 0.40 (deflated; encoder leak may be smaller than feared at text8 vocabulary of
4000 most-common words).

### Prediction 4: Provenance-port-rail (M3) prevents future PROVENANCE_FAIL cells

**HARD-PASS:** with ARM_TRANSFER_RAIL mandatory, the next 5 cross-world port cells dispatched have
fewer than 2 PROVENANCE_FAILs (vs 2/2 baseline for n1v3 ports).
**HARD-FAIL:** 3+ PROVENANCE_FAILs in next 5 ports.
**P_deflated:** 0.65 (deflated; the rail catches port-failure-itself but doesn't fix the
underlying mechanism mismatch).

### Prediction 5: Garden-of-Forking-Paths (M1) flags PC-hierarchy-style OR-gated PASSes

**HARD-PASS:** retroactive audit of the 22 cells finds 3+ HARD_PASS verdicts that would have been
demoted to MIDDLE_BAND under strict single-primary-metric pre-reg.
**HARD-FAIL:** fewer than 2 retroactive demotions -- indicates OR-gated PASSes are rare and the
M1 mitigation overshoots.
**P_deflated:** 0.70 (high confidence; pc_hierarchy is one already; audit will likely find 2-4
more).

---

## SECTION 8 -- CROSS-THREAD SYNTHESIS

This drill cross-references:

- `feedback_experiment_bias_master_checklist_USER_2026-06-24.md` (12-category baseline; this drill
  is the additive supplement).
- `notes/skunkworks_experiment_bias_audit_2026-06-24.md` (22-cell audit; this drill abstracts the
  patterns into bias categories).
- `notes/research_apples_to_apples_substrate_evaluation_methodology_2x_drill_2026-06-24.md`
  (4-lane framework; M3 / M4 / M10 here extend the framework).
- `notes/research_n1v3_provenance_audit_2x_drill_2026-06-24.md` (M3 root case).
- `notes/research_substrate_lm_experimental_methodology_3x_drill_2026-06-23.md` (Simmons 2011
  archetype; M1 / M2 / M5 here are concrete instantiations).
- META_HARNESS_RIGGED cert row 698 (M5 motivation).
- Fix #28 recurrence pattern (M2 + M14 supporting evidence).

The 15-bias supplement combined with the 12-category master checklist gives ~27 formal bias
categories. This is approaching the upper limit of what a checklist can usefully enforce; further
extensions should be cross-category bias-interactions (e.g., "M3 + M5 together =
provenance-port-then-metric-flip = double-bias rescue"), not new categories.

---

## SECTION 9 -- CITATIONS

Verified count: 12 internal references + 4 external statistical-methodology anchors.

### Internal (substrate-system)

1. `feedback_experiment_bias_master_checklist_USER_2026-06-24.md` (master checklist)
2. `notes/skunkworks_experiment_bias_audit_2026-06-24.md` (22-cell audit)
3. `notes/research_apples_to_apples_substrate_evaluation_methodology_2x_drill_2026-06-24.md`
4. `notes/research_n1v3_provenance_audit_2x_drill_2026-06-24.md`
5. `notes/research_substrate_lm_experimental_methodology_3x_drill_2026-06-23.md`
6. `notes/research_surprise_baseline_7p22_vs_7p30_2x_drill_2026-06-24.md`
7. `notes/research_compositional_generalization_critical_failure_2x_drill_2026-06-24.md`
8. cert_ledger row 698 (META_HARNESS_RIGGED) -- BPC-is-rigged-metric
9. cert_ledger row 699 (n1_v3 TOP1_CG) -- post-hoc-pass example
10. `feedback_fix28_violation_count_internalize_harder_2026-06-22.md` (Fix #28 recurrence)
11. `feedback_fix28_recurring_skunkworks_correct_more_than_director_2026-06-23.md` (M15 base)
12. `notes/research_meta_skepticism_12_assumptions_store_mined_2x_drill_2026-06-24.md` (cross-ref)

### External (statistical methodology)

13. Simmons, Nelson, Simonsohn (2011). "False-Positive Psychology" -- garden-of-forking-paths +
    p-hacking foundational. (M1, M2 base)
14. Gelman, Loken (2013). "The garden of forking paths" -- HARKing and metric-selection bias.
    (M1, M5 base)
15. Ioannidis (2005). "Why Most Published Research Findings Are False" -- multiple-comparison
    correction + power. (M7, M13 base)
16. Heinze-Deml, Meinshausen (2017). "Conditional variance penalties and domain shift robustness"
    -- transfer-rail / domain-shift bias (M3, M10 base).

---

## SECTION 10 -- META atoms candidate

Five new META atoms candidate from this drill:

1. **META_GARDEN_FORKING_PATHS_M1**: OR-gated metric without single-primary-metric pre-reg
   produces false HARD_PASS rate ~0.10-0.20 per cell.
2. **META_BEST_OF_N_SELECTION_M2**: best-of-N reporting without arm-pre-registration is the
   dominant Fix #28-class bias source.
3. **META_PROVENANCE_PORT_RAIL_REQUIRED_M3**: cross-world port cells require ARM_TRANSFER_RAIL or
   are tier-blocked.
4. **META_ENCODER_LEAKAGE_M10**: word2vec-google-news and Pythia-160m as encoders have train-test
   corpus overlap with text8/Wikipedia; substrate chain-grade atoms using these encoders carry
   leak-risk.
5. **META_15_BIAS_SUPPLEMENT_2026-06-24**: this drill adds 15 bias categories to the master
   12-category checklist; combined ~27 categories cover ~90% of identified-bias surface.

---

End of drill.
