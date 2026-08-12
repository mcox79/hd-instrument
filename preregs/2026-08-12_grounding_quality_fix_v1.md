# PRE-REG: grounding quality fix (tautology refusal / filler refusal / provenance) -- 2026-08-12

anchor_name: reading_grounding_loop_cycle3_groundingfix_v1
cell: experiments/exp_reading_grounding_loop_cycle3_groundingfix_v1.py
full design + rationale: notes/grounding_quality_fix_2026-08-12.md (written BEFORE implementation)
corrects: notes/foundation_grounding_sample_2026-08-12.md (audit of data/foundation/reading_grounding_v1)

## Question
Does refusing to record non-groundings (self-tautologies; closed-class objects) and attaching
per-fact provenance produce a foundation whose GROUNDED_MEANING facts are actually meaningful,
measured against the prior audit's own rubric and baselines?

## Compute architecture
class: (b) sequential-CPU with justification. The loop is inherently sequential (curriculum order;
each checkpoint's ConceptSpace anchors depend on every prior checkpoint's groundings -- a genuine
step-N-depends-on-step-N-1 chain). Storage strategy: sharded (HDFactStore holds one vector per
fact; no bundling of facts). No GPU speedup available: the hot path is GapDetector's codebook scan
and per-lemma cosine over a few thousand 256-d anchors, not a large matmul. Measured v1 wall time
5 segments = 3120 s total.

## Bands (expected direction in notes doc section 2)
- B1 tautology_rate_new_facts: BEFORE 0.657 (2328/3544). PASS == 0.000. FAIL > 0.
- B2 closed_class_object_share_new_facts: BEFORE measured on v1. PASS == 0.000. FAIL > 0.
- B3 fresh 50-pair audit (seed=42, same rubric): baselines mixed 4/6/90, cross-only 35/25/40.
  PASS MEANINGFUL >= 0.35 AND NOISE <= 0.40. MIDDLE_BAND MEANINGFUL in [0.15, 0.35).
  FAIL MEANINGFUL < 0.15 OR NOISE > 0.60.
- B4 n_grounded_concepts: BEFORE 3544. Expected to DROP SHARPLY (a CORRECTION, not a regression).
  PASS 300 <= n <= 1400. FAIL n == 0 or n >= 3000.
- B5 provenance_coverage: BEFORE 0.000. PASS == 1.000. FAIL < 1.000.
- B6 backward_compat_v1_loads: PASS loads with 7966 facts unchanged. FAIL raises or count differs.

## FAIL declaration (pre-registered)
See notes doc section 2a, items 1-7. The load-bearing one: MEANINGFUL < 0.15 in B3 means removing
tautologies shrank the store without improving it -- a clean negative, to be reported plainly.

## Anti-tuning
SENSE_MATCH_THRESH=0.45, MIN_CONFIRM=4, PATIENCE_MAX=3, SCHEMA_THRESH_FULL and the closed-class
criterion are FROZEN. No post-hoc adjustment after seeing B3.

## Schema-vet fields
- cardinality_ok: true -- EXPECTED_N_SEGMENTS = 5 (bootstrap, ele_cont, int_cont, adv_new, bio_new);
  finalize refuses to emit a verdict if any segment summary is missing.
- calibration_check: "default_ok_for_this_regime" -- every threshold is inherited unchanged from
  the v1 run being corrected, so the ONLY manipulated variable is the refusal rule. Changing a
  threshold as well would confound the comparison.
- final_metrics_atomicity: "tmp_replace"
- start_marker_written: true
- crash_diagnostic_present: true
- heartbeat_present: true (per-chunk [progress] flush + exp_checkpoint units.jsonl)
- progress_logging: per-chunk print(..., flush=True); segment wall > 1800 s expected for bio_new.
- cell_chunked: false (no seed axis; one deterministic run. Resumability is per-SEGMENT via the
  persisted foundation directory, plus per-chunk units.jsonl records.)
- defensive_error_checking: "passed_all_4_patterns"
- arms_differ_verified: the comparison is v1 store vs v2 store, two distinct on-disk directories;
  arm difference is measured directly as fact-set difference, not asserted.
- discriminator: B1/B2 are structural (can only be 0 if the refusal fires); B3 is the real
  discriminator and CAN FAIL (a fix that removes tautologies without improving the survivors lands
  MEANINGFUL < 0.15).
- real_code_path: verification/test_grounding_refusal.py constructs the REAL HDFactStore +
  ReadingLoopState + checkpoint() path at tiny scale, not a synthetic branch.
- crlb_n/a: "no quantitative noise floor -- the metrics are rates over discrete stored facts and a
  human-bucketed sample, not an estimator against a Cramer-Rao bound."
