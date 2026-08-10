# Pre-reg: crutch_discriminative_selection_coherence_tom_v2 (iter-2 of the DISCRIMINATIVE selection
# cell -- strengthen top-down coherence + ToM-aware relation-gating, drop the bottom-up drag)

Filed by: exp_dev (Sonnet). Task per Director spawn prompt "Run ONE mechanism-indicated iteration on
the crutch discriminator (iter-1 = 79c354a6d landed scramble-clean but real-but-weak)"
(`notes/design_crutch_discriminator_iter2_coherence_tom_2026-08-10.md`).

## Prior-work check (mandatory, USER-locked 2026-07-01)

`bash tools/substrate_query.sh "coherence retrieve-validate ToM relation-gating discriminator SIQa
mentalizing crutch"` (2026-08-10, kb_version=v1, confidence=0.3291). Top-5 hits: (1) `CN_discriminating`
cosine=0.3291 -- a generic concept-graph node, matches only on the surface word "discriminating" via
the char-trigram encoder; (2) "Discriminating regime" cosine=0.3096 -- unrelated capacity-regime notes
from a different (Hebbian-superposition) research line; (3) an entity-grid coherence-metric research
note (`chain_grade_decision_slate_reading_frontier_2026-07-17.md`) cosine=0.3076 -- a DIFFERENT task
(discourse READING-ORDER coherence via permutation tests, Barzilay-Lapata entity grids), not retrieval
discrimination; (4)/(5) more `CN_discriminating`/`discriminating`/wordnet antonym nodes, same surface
match. **None of these is a prior cell on this question** -- all are noise from "discriminat-" token
overlap, not substantive matches. VERDICT: genuinely novel iteration on this program's own iter-1 cell
(79c354a6d / `experiments/exp_crutch_discriminative_selection_multicue_v1.py`), not a rediscovery.

Additionally: both this design note and iter-1's design note pointed to a "Stage-2A retrieve-VALIDATE
loop (hdlab, HARD_PASS)" as the coherence organ. iter-1's own pre-reg already documents grepping
`hdlab/`, `notes/`, `preregs/`, `experiments/` for this name and finding ZERO hits. This cell repeats
that finding (no such organ exists in the codebase under that name) and again implements the
retrieve-validate coherence check NATIVELY, reusing the SAME owned `spreading_activation_scores`
primitive (seeds/target swapped for the backward direction) rather than importing an unverified
label -- per wire-don't-island "read the code not the label" discipline.

## iter-1 finding this cell acts on (MEASURED, not hypothesized)

`data/exp_crutch_discriminative_selection_multicue_v1/metrics.json` (79c354a6d, FULL, n=1954 dev):
BoW-only overall=0.3501. All 3 arms fired on ~41-44% of dev but landed at real margins A=-0.0037
B=-0.0101 C=-0.0046 (all HARD_FAIL, below the +0.02 MIDDLE_BAND floor) -- essentially BoW parity.
Scramble margins -0.10 to -0.15 (well past the +0.03 collapse ceiling on the SAFE side -- the
decisive control is clean, even over-collapsed). Per-feature ablation (`arm_C_ablation.F_conv`):
dropping the raw multi-cue CONVERGENCE-COUNT feature nudges real margin to +0.013 (still short of
+0.02) while scramble stays deeply collapsed (-0.167) -- convergence-count got the LARGEST learned
weight (0.123, MEASURED@`arm_C.weight_vectors.7`) despite being a net drag: it correlates on TRAIN
(dense small-world graph, many spurious multi-cue coincidences) but does not generalize. Dropping
F_path (path-directness) instead INVERTED scramble collapse to +0.176 (non-discriminative) --
F_path is the single most load-bearing feature for the decisive scramble control.

## What this cell changes (ONE mechanism-indicated iteration; retrieval/evidence-gathering UNCHANGED)

1. **DROP raw convergence-count (`F_conv`) as a scoring feature entirely.** Retained only as the
   existing structural "covered" definition (`F_conv[j] > 0` still gates the abstain/no-regression
   architecture, unchanged from iter-1 -- this is NOT the scoring change, just bookkeeping continuity).
2. **STRENGTHEN coherence into a proper retrieve-VALIDATE check.** iter-1's `F_coh` was a single
   bundled backward BFS call (candidate's concepts -> one scalar toward the whole context bundle).
   iter-2's `F_coh`: per covered candidate, a per-cue BACKWARD spreading-activation pass (mirrors the
   forward per-cue loop, same owned `spreading_activation_scores` primitive, seeds=candidate concepts
   / target=single cue) -- RETRIEVE. Counted only if the candidate's backward evidence converges on
   `MIN_COH_CONVERGENCE=2` DISTINCT context cues -- VALIDATE (a single-path "coherent" hit could be a
   hub-adjacency artifact; multi-anchor convergence is the actual validation, the same coincidence-
   detection principle iter-1 used forward, reapplied here as a GATE rather than a raw magnitude --
   the mechanistic fix for why raw F_conv failed: convergence-as-a-count is an overfit-prone magnitude,
   convergence-as-a-validation-THRESHOLD on an already-strong signal is a different, more conservative
   use of the same underlying evidence).
3. **Make relation-gating ToM-AWARE with a TIGHTENED ATOMIC-only map** (design note: why/want ->
   xIntent/xWant; feel -> xReact/oReact; next/consequence -> xEffect/oEffect). iter-1's map mixed in
   ConceptNet relations (hasproperty, mayhaveproperty, motivatedbygoal, hasprerequisite, causes,
   capableof, hassubevent) that dilute the ToM-specific signal (Social IQa is a mentalizing-network
   benchmark; ConceptNet's generic property/location relations are not mental-state inferences).
   Applied to BOTH the forward evidence (`gate_delta`, same construction as iter-1) AND the backward
   coherence pass (NEW -- reuses the SAME hop-1 driving-relation lookup computed once per (cue,
   candidate) pair, since a pair_key's relation TYPE is direction-independent even though the BFS
   activation itself is not).
4. **KEEP path-directness (`F_path`)** unchanged -- the ablation's most load-bearing feature for
   scramble-collapse.

Net: `FEATURE_NAMES` shrinks from iter-1's 4 (`F_conv, F_path, gate_delta, F_coh`) to iter-2's 3
(`F_path, gate_delta, F_coh`), with `gate_delta` and `F_coh` both substantively redefined (gate_delta
moved to path-sum scale for unit-consistency with F_path/F_coh, matching-scale being the diagnosed
fix for F_conv's raw-count/scale-mismatch failure mode; F_coh gained the retrieve-VALIDATE gate + ToM
gating).

## Two arms (per Director spawn; retrieval/evidence-gathering UNCHANGED, ONE variable = combiner)

- **D1 (fixed principled weights, no label-fitting):** `D1_score = F_path + gate_delta + F_coh`.
  Algebraically this collapses to `F_path_gated + F_coh` (since `gate_delta = F_path_gated - F_path`
  by construction) -- i.e. "ToM-relation-gated path-directness plus validated backward coherence," a
  single interpretable quantity, exposed as 3 addends only so the ablation can drop each term
  independently. Zero label-fitting, zero normalization (all three terms are already on the same
  decayed-activation scale) -- the honest, no-p-hacking-risk arm.
- **D2 (learned):** same 3 features, z-score normalized via TRAIN-population mean/std (unsupervised
  stats, not label-fit), linear combination fit by full-batch softmax-GD on TRAIN's gap-flagged +
  covered items (`TRAIN_FIT_CAP` capped, deterministic file order), 3 seeds {7, 13, 19}, evaluated on
  HELD-OUT dev. **WIQA-lesson guard (identical to iter-1):** REAL-trained `w` applied AS-IS to
  SCRAMBLE-graph features at eval time, never retrained on scramble -- if it still discriminates
  there, it memorized a structural artifact.
- **Per-feature ablation (BOTH arms):** 3 refits/reformulations each dropping one of
  `{F_path, gate_delta, F_coh}` (zeroed at train+eval), reporting covered-subset margin delta vs the
  full-feature arm -- answers "which feature carries the discrimination," specifically whether the
  STRENGTHENED COHERENCE (`F_coh`) is the driver (the brain's top-down-control prediction per the
  design note).

## Augment-not-replace abstain gate (unchanged from iter-1, no-regression by construction)

`covered[cand] = F_conv[cand] > 0` (structural, retained). `n_covered = count(covered)`. An arm FIRES
on an item only if `n_covered >= 2` (real 3-way competition) AND its own score has a STRICT
top1>top2 winner. Otherwise ABSTAIN -> BoW prediction. BoW always-on underneath every arm.

## Compute architecture

Sequential-CPU, justified (same class as iter-1): (a) retrieval stage reuses the owned hub-capped BFS;
(b) genuine sequential per-item dependency, checkpointed via `tools/exp_checkpoint.py`
(unit_key=(side, item_idx)); (c) this cell issues MORE backward BFS calls per item than iter-1 (up to
`CUES_PER_ITEM` per-cue backward passes per covered candidate, vs iter-1's single bundled backward
call) -- compute-bounded by restricting the backward pass to forward-covered candidates only (typically
1-2 of 3 candidates per item, and only on the ~41-44% of dev items with any coverage at all, per
iter-1's measured fire-fraction). No GPU: pure dict/set BFS over a symbolic graph. Storage strategy:
no_storage (read-only graph traversal + a tiny in-memory 3-feature linear fit).

**Wall-time estimate (THEORETICAL, to be MEASURED at smoke and used to set the FULL timeout):**
iter-1 FULL (122.6s, ~55k total BFS calls at ~2.2ms/call average, MEASURED@
`data/exp_crutch_discriminative_selection_multicue_v1/metrics.json:elapsed_s`) issued ~5 forward +
1-3 bundled-backward calls per item. iter-2 adds up to `CUES_PER_ITEM=5` per-cue backward calls per
covered candidate (vs iter-1's 1 bundled call), gated by the SAME forward-coverage compute-bound, so
the expected multiplier is roughly 2-3x iter-1's wall time (estimate ~250-400s FULL) -- MEASURED at
smoke below, not assumed; FULL timeout is computed from the measured smoke wall via the standard
`ceil(1.5 * smoke_wall_s * (1954/SMOKE_DEV_CAP))` scaling used by iter-1.

## Modes

- `--self-test`: tiny synthetic CSKG (~10 nodes) with THREE planted cases: (1) retrieve-VALIDATE
  coherence gate -- a 2-cue-converged candidate (`candalpha`) passes `MIN_COH_CONVERGENCE=2` and gets
  `F_coh>0`; a 1-cue-converged candidate (`candbeta`) fails the gate and gets `F_coh=0` even though its
  raw single-path backward activation is nonzero; also verifies D1's algebraic identity
  (`F_path+gate_delta == F_path_gated`); (2) ToM-relation-gating FLIP restricted to pure ATOMIC
  relations (`candpsi` reached via 2 ConceptNet-irrelevant relations loses to `candquin` reached via 1
  ATOMIC-relevant `xreact` relation, once gated) -- plus explicit assertions that ConceptNet relations
  (`hasproperty`, `motivatedbygoal`, `capableof`) are NOT in the tightened `RELEVANT_RELATIONS` map;
  (3) abstain when `n_covered<2`. Also verifies: D2 GD fit+generalize on a tiny synthetic pattern,
  `exp_checkpoint` real round-trip, determinism (bit-identical repeated feature computation), no bare
  `except:`, `SystemExit`/`KeyboardInterrupt` ordering, atomic metrics, question-type classifier
  sanity. **MEASURED: self-test PASSED in 0.06s** (local `.venv`, 2026-08-10).
- `--smoke`: FULL real CSKG index (graph is the discriminator, can't be shrunk) + capped dev
  (`SMOKE_DEV_CAP=250`, CITED@iter-1) + capped train-fit population (`SMOKE_TRAIN_FIT_CAP=300`,
  CITED@iter-1) -- discriminator-preview per DISCRIMINATOR-MUST-SURVIVE-SCALE option (A). Verifies:
  BoW baseline reproduces the base cell's own BoW accuracy at this population; positive control
  reproduces the 0.2465 reference; each arm fires at a non-trivial rate; real and scramble margins
  both computable; arms differ (D1 vs D2 prediction-vector digests).
- `--full`: all 1954 dev items (matches iter-1's population exactly) x 2 sides (real, scramble);
  TRAIN fit population capped `TRAIN_FIT_CAP=4000` (compute-bounding, disclosed, not a benchmark
  population, CITED@iter-1).

## HARD-PASS / MIDDLE_BAND / HARD-FAIL bands (identical numeric bands to iter-1, per-arm, never
aggregated -- Director's task spawn explicitly reuses these)

Let `CoveredAcc_real(arm)` = accuracy of arm's fired predictions on the REAL-side covered subset;
`BowAcc_real(subset)` = BoW's own accuracy on that SAME subset. Same notation with `_scramble`.
`margin_real(arm) = CoveredAcc_real(arm) - BowAcc_real(subset)`; `margin_scramble(arm)` analogously.

**HARD_PASS** (arm) requires ALL:
1. `margin_real(arm) >= +0.05`.
2. `margin_scramble(arm) <= +0.03` (decisive, load-bearing control).
3. `overall_accuracy(arm, with abstain) >= bow_only_overall_accuracy - 0.005` (no-regression).
4. `n_covered_real >= 0.05 * n_dev` (non-vacuous fire rate).

**MIDDLE_BAND** (arm) if `margin_real(arm) in [+0.02, +0.05)` AND `margin_scramble(arm) <= +0.03` AND
no-regression AND gate 4 -- "a scramble-CLEAN win of ANY size is the meaningful result" (design note;
iter-1's own ablation already landed real_margin=+0.013, just short of this floor).

**HARD_FAIL** (arm) if ANY: `margin_scramble(arm) > margin_real(arm) - 0.02` (non-discriminative);
`margin_real(arm) < 0`; no-regression fails; gate 4 fails.

Top-level `verdict` = best across D1/D2 (HARD_PASS if either HARD_PASS, else MIDDLE_BAND if either
MIDDLE_BAND, else HARD_FAIL); per-arm detail in metrics.json is authoritative.

## Honest exit criterion (Director design note, disclosed up front)

If iter-2 ALSO lands real-but-small (scramble-clean, real margin < +0.05, i.e. HARD_FAIL-by-magnitude
or at best MIDDLE_BAND), that is the mechanism-indicated signal to STOP grinding discrimination-feature
iteration and do the honest ceiling synthesis: the glass-box crutch-retrieval-discrimination path tops
out near BoW for SIQa. This is disclosed as the pre-registered interpretation of a repeat-small result,
not a post-hoc excuse -- reported plainly in the completion hand-off either way.

## Positive control (Gate D)

`positive_control_1hop_coverage`: reproduce `crutch_candidate_scores`'s own 1-hop coverage_rate on
this cell's loaded CSKG index + dev population -- must land within 0.02 abs of the committed 0.2465
(593fe79b0 / re-measured 0.24653 in iter-1's FULL run), proving data-loading fidelity before trusting
any downstream number. Unaffected by the feature-set change (uses `crutch_candidate_scores` directly,
identical code path to iter-1).

## SCHEMA-VET fields

```yaml
cell_chunked: true                       # per-(side,item_idx) unit; tools/exp_checkpoint.py
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: passed_all_4_patterns
final_metrics_atomicity: tmp_replace
arms_differ_verified: true               # D1/D2 prediction-vector digests differ, verified at smoke
deterministic_seeding: true              # hashlib-seeded scramble draws + np.random.default_rng(int
  # seed) for D2 GD init; sorted() node_list; no hash(), no list(set())
progress_logging: print_flush_true
calibration_check: adaptive_with_discriminator_gate  # GATE_THRESH = median(bow_margin) over dev,
  # CITED@iter-1 fix, reused verbatim; RELEVANT_RELATIONS map + MIN_COH_CONVERGENCE are
  # HYPOTHESIZED@author-design (never fit on labels)
crlb_n/a: "discrete 3-way classification accuracy on a real benchmark; no capacity/noise-floor
  discriminator threshold applies"
discriminator_reachability: true         # self-test's planted retrieve-validate + gating-flip cases
  # prove the mechanism can, in principle, produce the intended discrimination before real-data run
compute_architecture: sequential-CPU justification above
storage_strategy: no_storage
real_code_path_exercised: [load_cskg_index, extract_concepts, crutch_candidate_scores,
  spreading_activation_scores]
substrate_signature_checked: n/a (pure function-level reuse of the two owned cells' module-level
  functions, no KGStore/fit-module live-signature dependency)
guard_baseline_valid: n/a (scramble-collapse IS the control, handled by the HARD_FAIL gate above)
positive_control_arms: [{arm: positive_control_1hop_coverage, cited_prior_atom: "593fe79b0
  coverage_audit / 79c354a6d re-measurement", cited_prior_metric: 0.2465, tolerance: 0.02}]
functional_requirements:
  - requirement: "validate coherence via multi-anchor backward convergence, not a single bundled path"
    primitive: new per-cue backward calls to the OWNED spreading_activation_scores (seeds/target
    swapped), gated by MIN_COH_CONVERGENCE>=2 (retrieve-VALIDATE)
  - requirement: "gate relation relevance using ATOMIC's own mental-state relation vocabulary"
    primitive: tightened RELEVANT_RELATIONS map (ATOMIC-only), applied via the OWNED relation_family
    lookup to BOTH forward (gate_delta) and backward (F_coh) evidence
  - requirement: "keep path-directness"
    primitive: F_path unchanged (CITED@iter-1)
  - requirement: "fixed principled combination (no label-fit)"
    primitive: new D1 = unweighted sum of the 3 unit-consistent top-down features
  - requirement: "learn the combination weighting from data, held out"
    primitive: CITED@iter-1's fit_arm_c mechanics, F=3 instead of F=4 (fit_arm_d2)
```

## Dispatch (per exp_dev role: local smoke, hand off remote FULL)

Self-test PASSED locally (0.06s, `.venv`, 2026-08-10). Smoke run LOCAL foreground (`.venv`, `--smoke`)
next; wall time measured there sets the FULL timeout via
`ceil(1.5 * smoke_wall_s * (1954/SMOKE_DEV_CAP))`. Per USER-LOCKED 2026-07-01 ("SMOKE ONLY on
local_cpu_queue"), FULL routes to `remote_cpu_queue` (CPU-only cell, no GPU primitive) -- exp_dev
returns the exact `queue_add.sh` command; does not SCP-ship it.

## Guardrails (per Director spawn)

Branch `dataprep/mcguffey-graded-corpus` (not main/origin). ONE variable (the discriminator/combiner
stage's top-down feature strengthening; retrieval/evidence-gathering unchanged). Real held-out dev
(certified 1954-item validation split). Targeted commits only (never `git add -A`). Resumable per-unit
via `tools/exp_checkpoint.py`. VET every arm on disk AS HARD AS a positive, per-axis never aggregated;
scramble-collapse is the load-bearing control for both arms independently.
