# Pre-registration: exp_cortex2_atom_consultation_smoke_v1_1_warmup_fix_s7

**Filed:** 2026-07-04 (hdi_exp_dev sub-agent, per Skunkworks landed-VET
branch (a) recommendation).
**Anchor:** `cortex2_atom_consultation_smoke_v1_1_warmup_fix_s7`
**Cell:** `experiments/exp_cortex2_atom_consultation_smoke_v1_1_warmup_fix_core.py`
**Wrapper:** `experiments/exp_cortex2_atom_consultation_smoke_v1_1_warmup_fix_s7.py`
**Parent atom:** math atom #54 `MM_TENTATIVE_ADVISORY` (v1 landed
2026-07-03 HARD_FAIL_WALL_BUDGET; steady-state calls 25-49 clean).
**Skunkworks task:** `ac63eee40ecd0f2d2` (landed-VET recommended branch (a)
warmup-fix as standard benchmarking hygiene, NOT p-hacking).
**Parent cell:** `experiments/exp_cortex2_atom_consultation_smoke_v1_core.py`

---

## Strategic context

Cortex-2 first probe (v1, task `aa3a65d9a961996f1`, commit `a5d36e244`)
landed SMOKE HARD_FAIL_WALL_BUDGET on 2026-07-03:

- MEASURED@`d:/AI/hd-instrument/data/exp_cortex2_atom_consultation_smoke_v1_s7_smoke/metrics.json:wall_ms_p95` = 6.307ms (> 5ms budget)
- MEASURED@same:wall_ms_p50 = 1.401ms
- MEASURED@same:wall_ms_max = 9.584ms
- MEASURED@same:match_and_honored_over_all = 0.800 (retrieval discriminator
  clean; unchanged from _selftest run 0.800)
- MEASURED@same:n_tag_filter_bypass = 0
- Skunkworks-VET (task ac63eee40ecd0f2d2) verified: cold-start tail
  (calls 0-2) had identical n_scanned=2 as steady-state; cold-start is
  OS/JIT, NOT primitive-latency divergence.
- Steady-state (calls 25-49): p50=0.97ms, p95=2.63ms, max=3.80ms
  (all under 5ms budget; retrieval preserved).

Branch (a) fix: add 3 warmup calls BEFORE the 50 measured calls. Warmup
= standard benchmarking hygiene; NOT p-hacking. The scientific question
was always "does AtomConsultant serve queries within sub-ms steady-state
budget once JIT/cache warm" -- v1 measurement conflated OS cold-start
with primitive latency.

## Framing (Skunkworks-authoritative pre-emptive)

- **MM_TENTATIVE_ADVISORY** at SMOKE (unchanged from v1 arc position;
  per USER-locked MM_STANDARD 2026-07-03).
- **REGIME-EXTENSION** of Cortex-1 CG atoms (v1 + v2) -- Cortex-2 arc.
- **arc-continuation != arc-closure** (per feedback_arc_continuation_vs_arc_closure
  2026-07-03). SMOKE HARD_PASS on v1.1 still MM_TENTATIVE at most.
- Prior-work concept-query for "atom consultation active constraint cortex
  advisory warmup benchmarking" 2026-07-03:
  NONE at cosine > 0.30. Same as v1 (novel synthesis).

## Source signature (per USER-locked MM_STANDARD)

**v1.1 warmup-fix, cortex-2 arc, N=99 corpus 2026-07-03 end-state
(curated subset of 7 atoms covering 5 ground-truth cases), 5 operation
classes, 50 measured + 3 warmup calls, advisory-only phase, char-trigram
encoder N=1024 for tag similarity.**

## Delta from v1

- ADD: 3 warmup calls at cell startup BEFORE the 50 measured calls.
- Warmup case = SHARDED / COMPOSITION (case 1 variation 0) FIXED
  a-priori (pre-committed here; NOT tunable). `_WARMUP_OP_CLASS =
  "COMPOSITION"`, `_WARMUP_PARAMS = {"storage": "BUNDLED", "N": 1024,
  "M": 6400, "corr": 0.85}`.
- Warmup wall recorded to `metrics.json.warmup_wall_ms` for audit
  (Skunkworks can verify cold-start pattern is real).
- Warmup wall EXCLUDED from every discriminator (p50, p95, max,
  match_and_honored, tag_filter_bypass, cardinality).
- IDENTICAL: 5 ground-truth cases, 10 variations each = 50 measured
  calls; same encoder, AtomConsultant, corpus, source_signature axes,
  PASS/FAIL bands.

## PRE-COMMITTED predictions

- **wall_p95 <= 5ms** (post-3-warmup, over 50 measured calls) -- PASS
- **match_and_honored_over_all preserves 0.80 +/- 0.05** (retrieval
  discriminator unchanged; identical corpus + identical cases)
- **n_silent_contradictions == 0** (bucket-ii per-call flagged)
- **n_tag_filter_bypass == 0**
- **cardinality_ok** (50 measured calls)
- **FAIL branch:** wall_p95 still > 5ms after warmup -> 6.31ms is
  intrinsic OR primitive-code-path is inefficient; escalate branch (b)
  diagnostic cell (investigate 6.31ms tail cause).

## Envelope + PRE-COMMITTED bands

### HARD_PASS (chain-grade advisory-only smoke, v1.1)

- `match_and_honored_over_all >= 0.70` over 50 measured calls AND
- `n_silent_contradictions == 0` (by-construction per_call flagging) AND
- `wall_ms_p95 <= 5.0` (post-warmup) AND
- `n_tag_filter_bypass == 0` (strict subset preserved on all 50 measured
  calls).

### MIDDLE_BAND

- `0.20 <= match_and_honored_over_all < 0.70`.

### HARD_FAIL_DECORATIVE

- `match_and_honored_over_all < 0.20`.

### HARD_FAIL_WALL_BUDGET

- `wall_ms_p95 > 5.0` on the 50 measured calls (post-3-warmup).
- **Interpretation:** if triggered, wall budget is intrinsic; escalate
  to branch (b) diagnostic cell to profile the 6.31ms tail source.

### HARD_FAIL_TAG_FILTER_BYPASS

- Any measured `n_tag_filter_bypass > 0`.

### HARD_FAIL_CARDINALITY_BREACH (META_RULE_H)

- `len(per_call) < EXPECTED_N_UNITS (50)`.

## Warmup discipline (anti-drift)

- **`N_WARMUP_CALLS = 3`** locked in cell + prereg BEFORE running.
- **Warmup case fixed:** case 1 variation 0 (SHARDED / COMPOSITION at
  N=1024, M=6400, BUNDLED, corr=0.85). No cherry-picking across
  variations after seeing p95.
- Warmup calls print `[warmup] ... DISCARDED` and are recorded in
  `warmup_wall_ms` field for Skunkworks audit.
- Discriminator computation ONLY on the 50 measured calls (per_call
  records index 0..49; warmup calls not in per_call).
- **Selftest asserts** `wall_ms_p95 <= 5.0` AND
  `match_and_honored_over_all >= 0.70` -- if selftest fails wall gate,
  v1.1 approach itself is falsified (cold-start not the cause) and
  branch (b) diagnostic is triggered directly (no smoke dispatch).

## Compute architecture (mandatory field)

- **Class:** (b) sequential-CPU with justification.
- **Justification:** cell IS the substrate-primitive being validated.
  AtomConsultant is stateless in-memory tag-filtered retrieval; no
  GPU-batchable work. Wall expected: (3 warmup + 50 measured) x ~1ms/call
  = ~53ms total. Well under 10s threshold. NO_STORAGE primitive.
- **Storage strategy declaration:** NO_STORAGE.

## SCHEMA-VET pre-dispatch checklist

- `cardinality_ok`: True at EXPECTED_N_UNITS=50 measured (warmup not
  counted).
- `arms_differ_verified`: True (5 op-classes = guaranteed-distinct
  atoms).
- `final_metrics_atomicity`: `tmp_replace` (META_RULE_AH).
- `except SystemExit: raise` before `except Exception`: verified.
- `crlb_n_a`: unchanged from v1; chance-baseline 0.20; HP 0.70 >> 0.24
  (floor + 5% band-width).
- `baseline_in_band`: chance = 0.20 in (0.05, 0.95).
- HP strictly above floor + 5% band-width: 0.70 >> 0.24.
- `HP_SCOPE`: `{match_and_honored: [PROBE_ARM]}`.
- `discriminator_reachability`: True (v1 self-test measured 0.80;
  identical corpus in v1.1).
- `discriminating_fraction`: N/A.
- `composition_edges`: N/A.
- `positive_control_arms`: v1 IS the positive control at the same regime
  (identical corpus + cases; only warmup added). Reproduction expected:
  match_and_honored_over_all = 0.80 +/- 0.05 (tolerance 0.05); if
  deviates, v1.1 changed something it shouldn't have.
- `functional_requirements`: unchanged from v1 (3 requirements).
- `cell_chunked`: False (single-seed by design).
- `start_marker_written`: True (`_start_marker.json` at main entry).
- `crash_diagnostic_present`: True.
- `heartbeat_present`: N/A (elapsed_s expected < 60s).
- `defensive_error_checking`: `passed_all_4_patterns`.
- `progress_logging`: `line_buffered_stdout`. Warmup prints
  `[warmup] ... DISCARDED` per call; audit-sample every 10 measured
  calls. timeout_s well under 1800s so pre-reg field not mandatory but
  declared anyway.

## Sweep-alignment audit (META_RULE_15 gate A)

- `swept_params`: 5 case_ids x 10 variations = 50 measured calls.
- `effective_params_per_primitive`: AtomConsultant.consult sees exactly
  the (op_class, params, query_hint) tuple.
- `sweep_alignment_verdict`: ALIGNED.

## Discriminating-band audit (META_RULE_15 gate B)

- Predicted match_and_honored_over_all = (10+10+0+10+10)/50 = 0.80
  (unchanged from v1 self-test MEASURED@
  `d:/AI/hd-instrument/data/exp_cortex2_atom_consultation_smoke_v1_s7_selftest/metrics.json:match_and_honored_over_all` = 0.800).
- `discriminating_fraction`: 4/5 cases predicted in [0.30, 1.00] band.

## Signal-shape compatibility (META_RULE_15 gate C)

- Only composition edge: `Cortex.forward()` -> `AtomConsultant.consult()`.
- Verdict: SHAPE_MATCH (unchanged from v1).

## Reproduce-prior-chain-grade (META_RULE_15 gate D)

- Parent = v1 (not yet chain-grade; MM_TENTATIVE_ADVISORY). v1.1 does
  reproduce v1's retrieval discriminator (0.80 +/- 0.05) AT MATCHED
  REGIME (identical corpus + cases) as positive control -- if v1.1
  deviates > 0.05 on match_and_honored, warmup added something
  unintended.

## Post-SMOKE outcomes

- **HARD_PASS (v1.1 wall gate passes + retrieval preserved):** v1.1 fix
  accepted; atom #54 gets amendment note "wall budget passes
  post-warmup". Cortex-2 arc advances to Phase 2 (advisory +
  Skunkworks-audit gate + one narrow named atom class promoted to
  applied=True).
- **HARD_FAIL_WALL_BUDGET (wall_p95 still > 5ms):** wall budget is
  intrinsic. Honest-negative atom filed
  (`CORTEX2_ATOM_CONSULTATION_WALL_BUDGET_INTRINSIC_v1_1`). Escalate to
  branch (b) diagnostic cell investigating 6.31ms tail cause.
- **MIDDLE_BAND / HARD_FAIL_DECORATIVE:** retrieval regressed vs v1
  (unexpected; warmup should be no-op for retrieval). Investigate v1.1
  code delta for accidental discriminator change.

## Dispatch

- Queue: `local_cpu_queue` (SMOKE only; per USER-LOCKED 2026-07-01
  smoke-only-on-laptop).
- Timeout: 120s (probe wall << 1s; timeout is queue-runner floor).
- SELFTEST_OK: to be verified via `--self-test` on `.venv` before
  queue_add.

## Independence

Independent of Orchestrator queue burst + Testbed `_seed_checkpoint.py`
argv bug hunt + Probe 16 SHARDED-cliff + Skunkworks v2b VET (all in
flight; different files).

---

## Discipline signature

- Prior-work concept-query: NONE at cosine>0.30.
- Mechanism-abstraction-lossy citation: source_signature declared in
  cell metrics + this pre-reg (v1.1 warmup-fix, 50 measured + 3 warmup).
- Regime-mismatch: N/A (identical regime to v1; only warmup added).
- Anti-drift: 3 warmup calls locked BEFORE running; case fixed
  a-priori; NOT tunable to force pass.
- No hallucinated numbers:
  - v1 landed p95 = 6.307ms MEASURED@`d:/AI/hd-instrument/data/exp_cortex2_atom_consultation_smoke_v1_s7_smoke/metrics.json:wall_ms_p95`
  - v1 landed p50 = 1.401ms MEASURED@same:wall_ms_p50
  - v1 landed match_and_honored = 0.800 MEASURED@same:match_and_honored_over_all
  - v1 landed n_tag_filter_bypass = 0 MEASURED@same
  - Steady-state (calls 25-49) p50/p95/max stats CITED@Skunkworks landed-VET
    task ac63eee40ecd0f2d2 (per-call subrange computation).
  - v1.1 wall_p95 <= 5ms is HYPOTHESIZED@this prereg:PRE-COMMITTED bands
    based on steady-state Skunkworks measurement.
