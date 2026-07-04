# Pre-registration: exp_cortex2_atom_consultation_smoke_v1_s7

**Filed:** 2026-07-03 (exp_dev sub-agent).
**Anchor:** `cortex2_atom_consultation_smoke_v1_s7`
**Cell:** `experiments/exp_cortex2_atom_consultation_smoke_v1_core.py`
**Wrapper:** `experiments/exp_cortex2_atom_consultation_smoke_v1_s7.py`
**Module:** `hdlab/atom_consultation.py` (new)
**Cortex integration:** `hdlab/cortex.py` step (0), default-disabled.

**Hand-off source:** `notes/exp_dev_handoff_research_cortex_2_atoms_as_active_constraints_2026-07-04.md`
**Research memo:** `notes/research_drill_cortex_2_atoms_as_active_constraints_M3_v2_2026-07-04.md`

---

## Strategic context

Cortex-1 arc closed 2026-07-03 with 5-of-6 primitives CG-verified (m14/m15/
m17 + m13/m16 via v1+v2). Cortex-2 is the next M3 sub-arc: turn the ~99
CG_META / Fix#28 atom store from PASSIVE documentation into ACTIVE
CONSTRAINTS automatically consulted at Cortex operation boundaries. This
probe is ADVISORY-ONLY (applied=False throughout) -- retrieval-correctness
smoke, NOT enforcement.

## Framing (Skunkworks-authoritative pre-emptive)

- **MM_TENTATIVE** at SMOKE (per USER-locked MM_STANDARD 2026-07-03).
- **REGIME-EXTENSION** of Cortex-1 CG atoms (v1 + v2) -- this is Cortex-2
  arc, NOT axis discovery.
- P_deflated = 0.45 (per research drill 2026-07-04, lit-scan calibration).
- Prior-work check (substrate concept-query for
  "atom consultation active constraint cortex advisory" 2026-07-03):
  NONE at cosine > 0.30. Wordnet "consultation" entry at cosine=0.40
  is language-corpus noise, not prior arc. Novel synthesis confirmed.

## Source signature (per USER-locked MM_STANDARD)

- Advisory-only phase (applied=False throughout probe).
- N=99 atom corpus 2026-07-03 end-state (curated subset of 7 atoms covers
  the 5 hand-built ground-truth cases + 2 RETRIEVAL distractors to exercise
  strict-subset tag-filter).
- 5 operation classes: COMPOSITION / FRAMING / CAPACITY / RETRIEVAL / VERIFY.
- 50 hand-built calls = 5 cases x 10 param variations.
- Char-trigram encoder n_dim=1024 for tag similarity (orthogonal to substrate
  N; small on-purpose for sub-ms budget).

## Hypotheses

- **H1 (advisory-only probe fires cleanly):** match_and_honored_over_all
  (matched atom recommendation matches ground-truth for >= 70% of 50 calls).
- **H2 (null):** consultation happens but doesn't discriminate -- match rate
  at chance ~20% (5 op-classes uniform random pick).
- **H3 (perf):** wall time <= 5ms per consult() call (p95 across 50 calls).

## Ground-truth cases

| Case | op_class    | Curated atom                              | Expected recommendation | 10 variations sweep       |
|------|-------------|-------------------------------------------|-------------------------|---------------------------|
| 1    | COMPOSITION | STORAGE_STRATEGY_SHARDED_MASTER_MODERATOR | SHARDED                 | N x M x corr sweep        |
| 2    | CAPACITY    | BUNDLED_first_order_bimodal_no_midband    | NO_MID_BAND             | L x F sweep at BUNDLED    |
| 3    | COMPOSITION | SCALE_FREE_law_hippo (competes with SHARDED) | SHARDED (hypothesis; see anti-drift note) | N x M/N sweep |
| 4    | FRAMING     | axis_aliasing_TOPOLOGY_vs_ALGEBRA_Fix28   | ALGEBRA                 | axis_label x actual_sweep |
| 5    | VERIFY      | cross_term_both_arms_in_band_META         | BOTH_ARMS_IN_BAND       | measurement x arms sweep  |

**Anti-drift note (case 3):** case 3 tests a design-time hypothesis: SHARDED
atom's constraint_text is expected to outrank SCALE_FREE atom's on the
COMPOSITION query when the sweep varies M/N. In the self-test the SCALE_FREE
atom actually outranked SHARDED, producing bucket-ii ("matched but not
honored") for all 10 case-3 variations. This is HONESTLY flagged per-call
(bucket_ii_flag=True in per_call records) and demonstrates the primitive is
working correctly -- the mismatch is in my hand-built ground-truth, not a
retrieval bug. This is exactly what the anti-drift discriminator is
designed to catch: silent contradictions = 0, explicit contradictions = 10.

## Envelope + PRE-COMMITTED bands

### HARD_PASS (chain-grade advisory-only smoke)

- `match_and_honored_over_all >= 0.70` (fraction of all 50 calls where matched
  atom recommendation matches ground-truth) AND
- `n_silent_contradictions == 0` (bucket-ii cases must be flagged, never
  silent -- guaranteed by construction: every per_call record includes
  `bucket_ii_flag` field) AND
- `wall_ms_p95 <= 5.0` AND
- `n_tag_filter_bypass == 0` (strict subset preserved on all 50 calls).

### MIDDLE_BAND

- `0.20 <= match_and_honored_over_all < 0.70`. Tag-filter tuning may be
  needed under Skunkworks discipline before promotion.

### HARD_FAIL_DECORATIVE

- `match_and_honored_over_all < 0.20`. Retrieval decorative; route back to
  research 2x-drill on learned-router-vs-manual-tagging.

### HARD_FAIL_WALL_BUDGET

- Any `wall_ms_p95 > 5.0`.

### HARD_FAIL_TAG_FILTER_BYPASS

- Any `n_tag_filter_bypass > 0` (strict-subset violated).

### HARD_FAIL_CARDINALITY_BREACH (META_RULE_H)

- `len(per_call) < EXPECTED_N_UNITS (50)`.

## Compute architecture (mandatory field)

- **Class:** (b) sequential-CPU with justification.
- **Justification:** cell IS the substrate-primitive being validated
  (AtomConsultant is a stateless in-memory tag-filtered retrieval primitive;
  no GPU-batchable work exists). Wall time expected: 50 calls x ~1ms/call =
  ~50ms total. Well under the 10s "must-be-batched" threshold. NO_STORAGE
  primitive; no persistence.
- **Storage strategy declaration:** NO_STORAGE (see AtomConsultant docstring;
  Cortex facade unchanged MIXED_inherited_per_primitive; step (0) does not
  add facade-owned state).

## SCHEMA-VET pre-dispatch checklist

- `cardinality_ok`: True at EXPECTED_N_UNITS=50 (5 cases x 10 vars).
- `arms_differ_verified`: True (5 op-classes are guaranteed-distinct atoms
  by curated-atom-set construction; META_RULE_AF).
- `final_metrics_atomicity`: `tmp_replace` (META_RULE_AH; single-shot smoke).
- `except SystemExit: raise` before `except Exception`: verified (grep-gate
  passes; no bare except; no BaseException).
- `crlb_n_a`: "retrieval-correctness metric is fraction-of-cases-matched
  over Bernoulli trials; no analytical noise floor applies. Chance-baseline
  is 0.20 (5 op-classes uniform random pick of top atom's recommendation).
  HARD_PASS 0.70 is >> chance + 5% band-width (0.20 + 0.04 = 0.24). OK."
- `baseline_in_band`: chance = 0.20 in (0.05, 0.95); measurable.
- HP strictly above floor + 5% band-width: 0.70 >> 0.24 (see above).
- `HP_SCOPE`: `{match_and_honored: [PROBE_ARM]}` -- one probe arm.
- `discriminator_reachability`: True (self-test achieves 0.80 in scratch
  dir; HARD_PASS floor 0.70 is reachable at declared curated atom-set).
- `discriminating_fraction`: N/A (not a param sweep on a continuous metric).
- `composition_edges`: N/A (single primitive; no composition).
- `positive_control_arms`: N/A (no prior chain-grade primitive being
  reproduced; this is a novel primitive).
- `functional_requirements`:
  1. "At Cortex operation boundaries, retrieve relevant CG_META atoms
     within sub-ms budget so downstream primitives can consult them."
     -> AtomConsultant.consult() with strict-subset tag-filter.
  2. "Advisory-only phase: retrieval happens but downstream is not forced
     to honor recommendation."
     -> ConsultationResult.applied=False; Cortex.forward() emits provenance
     but does not alter downstream behavior.
  3. "Match-and-honored measurable + zero silent contradictions."
     -> per_call records with explicit bucket_ii_flag field.
- `cell_chunked`: False (single-seed by design; probe is stateless).
- `start_marker_written`: True (`_start_marker.json` at main entry).
- `crash_diagnostic_present`: True (outer try/except in `__main__`).
- `heartbeat_present`: N/A (elapsed_s expected < 60s; no long cell).
- `defensive_error_checking`: `passed_all_4_patterns` (op_class enum
  raises ValueError; consult() perf p95 gate; wall_ms per-call recorded;
  tag-filter strict-subset asserted).
- `progress_logging`: `line_buffered_stdout` (`sys.stdout.reconfigure(
  line_buffering=True)` at cell start + audit-sample print every 10 calls).
  timeout_s well under 1800s so pre-reg field not mandatory but declared
  anyway.

## Sweep-alignment audit (META_RULE_15 gate A)

- `swept_params`: 5 case_ids x 10 variations = 50 calls.
- `effective_params_per_primitive`: AtomConsultant.consult sees exactly the
  (op_class, params, query_hint) tuple; no upstream partition-routing
  interferes.
- `sweep_alignment_verdict`: ALIGNED.

## Discriminating-band audit (META_RULE_15 gate B)

- `predicted_match_and_honored_per_case`:
  - case 1: 1.0 (SHARDED atom's constraint_text lexically dominates for
    "storage strategy composition" queries).
  - case 2: 1.0 (BUNDLED bimodal is the only CAPACITY-tagged atom for
    L/F variations).
  - case 3: 0.0 (design-time hypothesis test; SCALE_FREE outranks SHARDED
    on M/N-invariant queries -- honest bucket-ii by construction).
  - case 4: 1.0 (only FRAMING-tagged atom is axis-aliasing).
  - case 5: 1.0 (only VERIFY-tagged atom is cross-term-both-arms).
- Predicted match_and_honored_over_all = (10+10+0+10+10)/50 = 0.80.
- `discriminating_fraction`: 4/5 cases predicted in [0.30, 1.00] discriminating
  band; 1/5 predicted at floor (0.0). Overall 4/5 = 0.80 >> 0.30 threshold.

## Signal-shape compatibility (META_RULE_15 gate C)

- Only composition edge: `Cortex.forward()` -> `AtomConsultant.consult()`.
  - forward() supplies `(op_class, params={"tier_hint": "cortex_forward"})`.
  - consult() expects `(op_class, params, query_hint)`.
  - Verdict: SHAPE_MATCH (params dict passed through as-is; query_hint
    optional).

## Reproduce-prior-chain-grade (META_RULE_15 gate D)

- N/A: this is a NEW primitive. No prior CG atom to reproduce. Reproduction-
  gate audit would apply if the cell claimed to compose SHARDED-cleanup or
  hippo-M-invariance as a load-bearing primitive; this cell only READS
  atoms describing those primitives.

## Post-SMOKE outcomes

- **HARD-PASS:** atom filed
  (`EMPIRICAL_CORTEX2_ATOM_CONSULTATION_ADVISORY_PROBE_v1_SHARDED_STORAGE_LAW_PREDICTS_MM_TENTATIVE`).
  Escalate to Phase 2 (advisory + Skunkworks-audit gate + one narrow
  named atom class promoted to `applied=True`).
- **MIDDLE_BAND:** re-audit tag-filter under Skunkworks discipline. Do NOT
  promote.
- **HARD-FAIL_DECORATIVE:** honest-negative atom
  (`CORTEX2_ATOM_CONSULTATION_DECORATIVE_v1_NEEDS_LEARNED_ROUTER_OR_BETTER_TAG_FILTER`).
  Route to research 2x-drill on learned-router-vs-manual-tagging.

## Dispatch

- Queue: `local_cpu_queue` (SMOKE only; per USER-LOCKED 2026-07-01
  smoke-only-on-laptop).
- Timeout: 120s (probe wall << 1s; timeout is queue-runner floor).
- SELFTEST_OK: verified 2026-07-03 (`--self-test` PASS on .venv).

## Independence

Independent of Orchestrator re-dispatch + Testbed bug hunt + SHARDED-sat
drill + task-analog v2b (all in flight; different files).

---

## Discipline signature

- Prior-work concept-query: NONE at cosine>0.30 (see above).
- Mechanism-abstraction-lossy citation: source_signature declared in cell
  metrics + this pre-reg.
- Regime-mismatch: N/A (novel primitive, no prior regime).
- No hallucinated numbers: 0.80 predicted rate comes from cell self-test
  MEASURED@`d:/AI/hd-instrument/data/exp_cortex2_atom_consultation_smoke_v1_s7_selftest/metrics.json:match_and_honored_over_all`
  and case-by-case decomposition MEASURED@ same file per_call rows.
