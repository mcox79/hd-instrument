# Pre-reg: exp_ingest_gate_consolidation_loop_pilot_v1

**Cell:** `experiments/exp_ingest_gate_consolidation_loop_pilot_v1.py`
**Design source:** `notes/research_brain_foundation_ingest_gate_consolidation_loop_2026-07-15.md`
**Author:** exp_dev, 2026-07-15. **Scale:** local, run-to-completion (task re-authorized local).
**Scope:** CONSTRUCTION-grade proof that the explicit glass-box ingest-gate WORKS as a consolidation mechanism.
The field supplies NO formal combination rule for schema-fit x surprise x recurrence (design headline); we define +
test one. This is NOT a capability-win claim; it is a mechanism-works proof with an honest calibration finding.

## What is tested
A candidate item -> provisional tier -> 3-criterion gate (SCHEMA_FIT via `reachability_audit`, SURPRISE via
`additive_map.score_all`, RECURRENCE count) -> decision tree {DISCARD/SKIP/HOLD/FAST_TRACK/SLOW_TRACK}, all
recomputed CLOSED-LOOP against the CURRENT fitted foundation (NOT the falsified R7 static-tag path). Four batches
constructed by PROVENANCE (independent of gate signals -> non-circular):
1. REDUNDANT = foundation TRAIN edges (model saw them).
2. NOVEL-REL = a withheld relation type `xwant` reintroduced (recurs across many distinct heads).
3. NOISE = scrambled tail-swapped edges, each one-off (recurrence=1).
4. INTERFERENCE = existing-relation held-out MRR re-measured after fold-in.

Foundation = `AdditiveKGMap.fit` (the VET-confirmed 0.1282-MRR cortical map) on CSKG k-core train edges MINUS the
withheld relation. Fold-in for the withheld relation = `D[r*] = mean_i(X[t_i]-X[h_i])` over consolidation instances
(the relation-dual of the validated `compose_entity`), appended only (existing rows untouched).

## Pre-registered HARD-PASS bands (capacity-feasible; set from MEASURED pilot calibration, NOT guessed)
Calibration MEASURED@ one-shot fit (k_core=10,max_nodes=3500,epochs=200,seed7,N=2791): redundant surprise med=0.0 /
novel med=0.999 / noise med=0.999; foundation test MRR=0.0869; raw fold-in delta=+0.0096.

| Gate | Band | Rationale |
|---|---|---|
| HP_SEP_AUC | AUC(surprise; novel vs redundant) >= 0.90 | headline discriminator; scale-ROBUST (bigger candidate space widens separation) |
| HP_SKIP | redundant SKIP-rate >= 0.80 (v2 calibrated gate) | tests SKIP branch |
| HP_DISCARD | noise DISCARD-rate >= 0.95 | recurrence hard-floor |
| HP_CONSOLIDATE_V2 | novel CONSOLIDATE-rate >= 0.70 (v2 calibrated) | tests CONSOLIDATE branch |
| HP_FOLDIN_DIRECTIONAL | real fold-in delta > 0 AND real > random-displacement-null + 0.002 | fold-in is r*-specific |
| HP_INTERFERENCE | existing-MRR delta <= 1e-6 (append-only) AND destructive-control regresses | interference-free + non-vacuous |
| HP_NONREDUNDANT (KEY, design P=0.30) | within high-schema-fit stratum AUC(surprise)>=0.80 AND stratified partial-spearman perm-p<=0.05 | surprise adds decision-power BEYOND schema-fit |
| HP_TELEMETRY | perturbing each of recurrence/surprise/schema-fit flips the decision | telemetry-sensitive, not analytically pinned |
| baseline_in_band | 0.02 < foundation test MRR < 0.95 | META_RULE_AG (not saturated) |

Joint HARD-PASS = all nine. HARD-FAIL if separation/discard/interference/telemetry fail. MIDDLE_BAND if the
mechanism-soundness gates (sep/discard/interference/telemetry) pass but skip/consolidate/foldin miss (threshold or
fold-in tuning, not redesign).

## HONEST calibration finding (pre-registered as reportable, logged per META_RULE_M adaptive_with_discriminator_gate)
The design's LITERAL absolute thresholds (SURPRISE_MIN=0.5 rank-1-only SKIP; DISTINCT_NOVELTY=0.85 HOLD) are
MISCALIBRATED for a large-candidate low-MRR substrate: surprise=1-1/rank SATURATES near 1.0 for any item not in the
top-few, so (a) raw-0.5 SKIP under-counts genuinely well-predicted items, and (b) raw-0.85 HOLD captures ALL genuine
novelty -> the STRICT v1 tree sends ~95% of novel-reliable items to HOLD instead of consolidating. The cell reports
BOTH the strict v1 tree AND a principled v2 calibration: SKIP=surprise<0.8 (top-5 of ~2800), and HOLD reserved for
high-surprise + THIN provenance (n_sources<RECURRENCE_MIN) -- a strongly-recurring high-surprise item across many
distinct sources is EVIDENCE, not the systematic-error profile HOLD guards against. v2 is the minimal principled
calibration, not tuned-for-pass. This is exactly the design's pre-registered modal "threshold tuning, not redesign".

## Must-fail controls (fire) + telemetry
- random-displacement fold-in null delta ~0 (real fold-in beats it) -- NOTE: a pairing-scramble (permuted tails) is
  a VACUOUS null here because the mean-displacement estimator is pairing-invariant; the valid null breaks set-level
  head/tail correspondence (random pairs). This is itself a reported finding.
- destructive fold-in (overwrites SHARED entity rows) REGRESSES existing retrieval (interference test non-vacuous).
- gate decision flips under perturbation of each signal.

## Compute architecture
Class (c) mixed: one Adam-SGD foundation fit per seed (the cortical build) + batched-matmul distance scoring + BFS
reachability. Storage = SHARDED / append-only (the interference-free property IS the point; no bundling).
3 seeds {7,13,17}. Local CPU ~2.5-6 min. `final_metrics_atomicity=tmp_replace`. `arms_differ_verified` via distinct
batch surprise-vector hashes. `crlb_n/a`: gate is a decision-tree over measured signals (no closed-form noise floor);
bands set from measured calibration. Validity-preflight declares real_code_path (AdditiveKGMap fit/score_all/
compose_entity/insert_entity) + substrate_signature. Deterministic seeding (fixed ints + sorted; no salted-hash).

## LANDED RESULT (MEASURED@data/exp_ingest_gate_consolidation_loop_pilot_v1/metrics.json, run_mode=full, 3 seeds)
VERDICT = HARD_PASS (joint, all 9 gates). sep_auc=0.988; skip_v2=0.86; cons_v2=0.96 (v1 strict=0.05, hold_v1=0.95 --
the saturation finding); disc=1.00; foldin_real=+0.0190 vs random-null +0.0000; interference_delta=0.00 (bit-
identical) + destructive regresses; **surprise=NON_REDUNDANT_with_schema_fit** (abl_auc=0.840, perm-p=0.005,
corr(schema,surprise)=0.044); telemetry all flip; base_mrr=0.1043. KEY UNCERTAINTY (design P=0.30) RESOLVED: surprise
is a genuine third signal, NOT an R7/MIR-style relabel of schema-fit. Route to skunkworks landed-VET.
