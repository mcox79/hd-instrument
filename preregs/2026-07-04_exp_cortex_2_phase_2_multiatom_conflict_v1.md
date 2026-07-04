# Prereg: exp_cortex_2_phase_2_multiatom_conflict_v1

Filed: 2026-07-04 UTC
Author: hdi_exp_dev (Cortex-2 Phase 2 arc)
Anchor: `cortex_2_phase_2_multiatom_conflict_v1_s7`

## Purpose

Add per-op_class `recommendation_priority` field to `_AtomRecord` in
`hdlab/atom_consultation.py` and use it as an additive boost during ranking
so that COMPOSITION-tagged atoms with overlapping op_class coverage
(SHARDED_MASTER_MODERATOR + SCALE_FREE_law_hippo) tie-break by an
op_class-specific priority declared per atom.

Skunkworks VET (task ac067134f58cdc781) landed-VET Recommendation #2 for
Phase 2 apply-probe MM_TENTATIVE. Prompt-quoted rationale:

> Recommendation #2: Multi-atom conflict resolution primitive (case3
> revival): add per-op_class `recommendation_priority` field to
> `_AtomRecord`, tie-break on it after cosine-argmax. Would honor
> SCALE_FREE for case3 while preserving case1 SHARDED. Deferred to Phase 3
> per drill.

Phase: PHASE_2_MULTIATOM_CONFLICT_v1 — primitive extension of Phase 1
ADVISORY-ONLY retrieval; NOT enforcement (no writes to targets). Advisory
retrieval discriminator only. Composes with math #62 Phase 2 v1 SHADOW,
math #63 Phase 2 dose-response DOSE_RESPONSE_STABLE, meta #47 REFUSE-gate
over-rejection at high noise (adjacent discipline family).

## Design (LOCKED)

### Priority field

```python
@dataclass
class _AtomRecord:
    ...
    recommendation_priority: Dict[str, float] = field(default_factory=dict)
```

Missing key → priority 0.0 (neutral). Value MUST be in [0, 1].

### Ranking (two-stage)

Stage 1 (unchanged from Phase 1): op_class tag-filter selects candidate rows.

Stage 2 (unchanged from Phase 1): raw cosine floor at
`_RELEVANCE_FLOOR = 0.20`; sub-floor atoms are DROPPED (priority NEVER
promotes a sub-floor atom into ranking).

Stage 3 (NEW; multi-atom conflict resolution): among above-floor candidates,
sort by `rerank_score = raw_cosine + _PRIORITY_ALPHA * priority[op_class]`
descending. `matched_atoms[i].relevance_cosine` continues to expose RAW
cosine (audit-transparent); the boost is an internal ranking signal only.

### Locked constants

- `_PRIORITY_ALPHA = 0.10` (locked; NOT tunable post-outcome)
- Per-atom-per-op_class priorities LOCKED (NOT tunable post-outcome):

| atom_id                                        | op_class     | priority |
|-----------------------------------------------|--------------|----------|
| STORAGE_STRATEGY_SHARDED_MASTER_MODERATOR_v1  | COMPOSITION  | 0.5      |
| BUNDLED_first_order_phase_transition_v1       | CAPACITY     | 0.5      |
| SCALE_FREE_law_hippo_v1                       | COMPOSITION  | 1.0      |
| SCALE_FREE_law_hippo_v1                       | CAPACITY     | 0.5      |
| axis_aliasing_TOPOLOGY_vs_ALGEBRA_Fix28_v1    | FRAMING      | 0.5      |
| cross_term_both_arms_in_band_META_v1          | VERIFY       | 0.5      |
| sigma0_cleanup_gate_retrieval_v1              | RETRIEVAL    | 0.5      |
| unbind_noise_tolerance_scales_sqrtN_v1        | RETRIEVAL    | 0.5      |

### Calibration (measured off-disk BEFORE lock)

Raw cosines measured 2026-07-04 UTC on the curated 7-atom corpus (see
`scratchpad/measure_cosines2.py`):

- case1 v0 (COMPOSITION, storage=BUNDLED, N=1024): SHARDED cos=0.4082,
  SCALE_FREE cos=0.1367 (BELOW floor 0.20). Gap 0.27 in favor of SHARDED.
- case1 v9 (N=16384): SHARDED cos=0.3809, SCALE_FREE cos=0.1211 (BELOW
  floor). Gap 0.26 in favor of SHARDED.
- case3 v0 (COMPOSITION, N=512, M/N=5): SHARDED cos=0.2266, SCALE_FREE
  cos=0.2559. Gap 0.03 in favor of SCALE_FREE (marginal).
- case3 v9 (N=8192, M/N=10): SHARDED cos=0.2363, SCALE_FREE cos=0.2812.
  Gap 0.045 in favor of SCALE_FREE (marginal).

Priority boost math with alpha=0.10:
- case1: SHARDED rerank = 0.4082 + 0.05 = 0.458; SCALE_FREE sub-floor →
  dropped → SHARDED holds regardless of priority. MEASURED@scratchpad/
  measure_cosines2.py + THEORETICAL@0.4082 + 0.10 * 0.5.
- case3 v0: SHARDED rerank = 0.2266 + 0.05 = 0.277; SCALE_FREE rerank =
  0.2559 + 0.10 = 0.356. Gap 0.079 in favor of SCALE_FREE (robust).
- case3 v9: SHARDED rerank = 0.2363 + 0.05 = 0.286; SCALE_FREE rerank =
  0.2812 + 0.10 = 0.381. Gap 0.095 in favor of SCALE_FREE (robust).

## Pre-committed prediction (BEFORE run)

Cell re-runs the same 5-case × 10-variation smoke as v1.1 warmup-fix
(same anchor structure, same encoder, same queries, same 7-atom corpus)
but WITH case3 expected_rec CORRECTED to `SCALE_FREE` (true ground truth
per Skunkworks VET) AND priority tie-break enabled.

**PREDICT**:
- case1 (COMPOSITION → SHARDED): honored 10/10 (was 10/10)  HYPOTHESIZED@
  cosine gap 0.27 dominates PRIORITY_ALPHA*0.5=0.05 shift
- case2 (CAPACITY → NO_MID_BAND): honored 10/10 (was 10/10)  HYPOTHESIZED@
  distinct op_class; no priority conflict
- case3 (COMPOSITION → SCALE_FREE): honored 10/10 (was 0/10 in v1.1 due
  to case3 expected_rec="SHARDED" documenting the miss)  HYPOTHESIZED@
  cosine gap 0.03 + PRIORITY_ALPHA*0.5=0.05 differential shift → robust
  SCALE_FREE win
- case4 (FRAMING → ALGEBRA): honored 10/10 (was 10/10)  HYPOTHESIZED@
  distinct op_class
- case5 (VERIFY → BOTH_ARMS_IN_BAND): honored 10/10 (was 10/10)  HYPOTHESIZED@
  distinct op_class
- overall match_and_honored_over_all: 50/50 = 1.00 (was 40/50 = 0.80)
  HYPOTHESIZED@sum of per-case predictions

## Pass / fail bands

**HARD_PASS**:
- case3 flips 0/10 → 10/10 honored SCALE_FREE
- case1 preserved at 10/10 honored SHARDED
- cases 2, 4, 5 each preserved at 10/10 honored
- match_and_honored_over_all >= 0.90 (strictly above the 5%-band-width
  floor per META_RULE_L: floor 0.80 + 0.05*(1.00-0.80) = 0.81; HP >= 0.90)
- wall_p95 <= 5ms post-warmup (preserved from v1.1)
- 0 tag_filter_bypass, 50 cardinality, 0 silent contradictions

**HARD_FAIL** (any of):
- case3 stays 0/10 honored (priority tie-break did not flip)
- any of cases 1, 2, 4, 5 regresses (< 10/10 honored)
- overall match_and_honored_over_all < 0.80 (regression from v1.1)
- wall_p95 > 5ms

**MIDDLE_BAND**: 0.80 <= match_and_honored_over_all < 0.90 AND case3
partially flips (>0 but <10 honored).

## Anti-drift

- PRIORITY_ALPHA = 0.10 locked in prereg BEFORE running. If SMOKE fails,
  cell FAILS; alpha is NOT retuned in the same cell. Iteration to new
  alpha requires a NEW prereg + NEW cell (arc-continuation != arc-closure
  per USER 2026-07-03).
- Priority values per-atom-per-op_class locked in prereg (table above).
- Case3 expected_rec changed from "SHARDED" (v1.1 known-miss framing) to
  "SCALE_FREE" (true ground truth); this is the Skunkworks-authoritative
  correction, NOT a post-hoc verdict change.
- Warmup discipline: 3 calls case1 SHARDED first variation (identical to
  v1.1); warmup wall discarded from every discriminator.

## SCHEMA-VET gates

- `arms_differ_verified`: True — cases 1/2/3/4/5 fire on different atoms
  by construction (case3's atom now flips to SCALE_FREE_law_hippo_v1)
- `final_metrics_atomicity`: `tmp_replace` (single-shot smoke)
- `cardinality_ok`: EXPECTED_N_UNITS = 5 * 10 = 50 MEASURED (warmup excluded)
- `crlb_n/a`: retrieval-correctness metric; discriminator floor is chance
  = 0.20 (5 op-classes uniform random of top atom)
- `baseline_in_band`: chance baseline ~0.20 in [0.05, 0.95]
- `HARD_PASS strictly above floor + 5%-band-width`: HP=0.90 vs floor
  0.80 + 0.05*(1-0.80) = 0.81; 0.90 >> 0.81
- `HP_SCOPE`: {match_and_honored: [PROBE_ARM]} — single arm
- `discriminator_reachability`: True (case3 rerank gap 0.08-0.10 in favor
  of SCALE_FREE, well above numerical tolerance)
- `sweep_alignment_verdict`: N/A (no sweep axis; 50 = 5 cases * 10 vars)
- `discriminating_fraction`: N/A (no sweep bracket; case-based structure)
- `progress_logging`: `line_buffered_stdout` (smoke < 1min; META_RULE 17
  N/A but included for hygiene)

## Compute architecture

- Class: (b) sequential-CPU with justification. The consult() call is a
  ~20 x 1024 matmul + argmax + 7-element rerank sort; per-call sub-ms on
  CPU. Total 50 measured + 3 warmup ~= 25-100ms. GPU offers no meaningful
  speedup for this scale. No genuine sequential dependency; simply too
  small for GPU launch overhead to amortize.
- Storage strategy: no_storage (stateless AtomConsultant; each consult()
  is pure read over frozen 7-atom curated table).
- No composition axis; cell is retrieval-correctness discriminator only.

## Composed atoms (context, not modified)

- math #62 (Phase 2 v1 SHADOW): PHASE_2_APPLY_WITH_NONCE_v1 primitive land
- math #63 (Phase 2 dose-response DOSE_RESPONSE_STABLE): quantitative
  monotone response validated
- meta #47 (REFUSE-gate over-rejection at high noise): adjacent-family
  discipline that Phase 2 apply-probe should not silently ratify

This cell is orthogonal to those atoms (no primitive from them is invoked);
the composition is arc-level (Cortex-2 Phase 2 chain), not code-level.

## Post-SMOKE outcome plan

- HARD_PASS: candidate atom
  `EMPIRICAL_CORTEX_2_PHASE_2_MULTIATOM_CONFLICT_RESOLUTION_v1_MM_TENTATIVE`
  filed for Skunkworks landed-VET. Downstream arc: promote to Phase 3
  full-N stacked drill on augmented atom set (open question: does priority
  hold as atom_count grows from 7 to 99 to 970k?).
- HARD_FAIL: honest-negative; escalate to research on retrieval-priority
  formalization (Bayesian conflict resolution? learned priority? drop
  priority in favor of per-query re-weighting?).
- MIDDLE_BAND: escalate to Skunkworks discriminator audit; likely needs
  higher alpha or better constraint-text engineering.
