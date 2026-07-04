# Pre-registration -- exp_cortex_task_analog_downstream_v4 (2026-07-04)

## Scope + Provenance

**Revival attempt of cortex-task-analog-downstream arc** (v1/v2/v2b/v3 all
HARD_FAIL) under theory-grounded corridor design per LDPC-Maxwell / Sharp-
Capacity-Thresholds research drill.

Prior versions:
- v1 (commit 1ae012b60): H3_gap=-0.167 utility-artifact.
- v2 (commit ac201f6a6): H3_gap=-0.058 CLARIFY tier gained nothing.
- v2b (commit 7345bbbbe): H3_gap=-0.033 multi-round oracle-leak.
- v3 (commit tbd): H3_gap negative at high-noise regime.

**Research drill authority (2026-07-04):**
`notes/research_drill_LDPC_Maxwell_construction_VSA_multi_round_analog_2026-07-04.md`

**Primary citation:**
Sharp Capacity Thresholds in Linear Associative Memory, arxiv 2605.05189 (2026-05).
- TOP-1 argmax capacity: d^2 >= n log n
- LISTWISE (multi-round soft-evidence): d^2 >= n
- Listwise strictly dominates argmax iff `n <= d^2 <= 2 n log n`.

## Diagnosis of v1/v2/v2b/v3

All four prior versions ran at N=8192, M=300 -> `d^2/(n log n) = 39000`
(FAR ABOVE dominance-corridor upper bound of 2). Theory predicts null result
in this regime -- empirically confirmed. Revival requires:
- (a) enter corridor: `d^2/(n log n) in [1/log n, 2]`
- (b) real soft-evidence Round 2 (v2b/v3 used oracle-leak partial-mask reveal)

## v4 Design (theory-clean)

### Step 1: PRE-FLIGHT CORRIDOR TEST

Compute d^2/(n log n) at intended regime; **gate on IN CORRIDOR** at cell-init.
If FAIL -> abort cell with sentinel; do not run.

### Step 2: Corridor-entering parameters

**Primary (v4 default):**
- N_DIM = 512
- M_ITEMS = 20000
- V_CB = 32 (M/V_CB = 625 items/class supports listwise pooling)
- `d^2 = 262144`, `n log n = 197,952`, `d^2/(n log n) = 1.324` **IN CORRIDOR**
- corridor bounds `[1/ln(20000), 2] = [0.101, 2.0]`

**Kill-switch cascade** (if primary fails w/ H3_gap < 0.02, ordered priority):
- (a) N=400, M=10000: `d^2/(n log n) = 1.737` IN CORRIDOR
- (b) N=300, M=6000:  `d^2/(n log n) = 1.724` IN CORRIDOR

### Step 3: SOFT-EVIDENCE ROUND 2 (no oracle leak)

v2b/v3 used ground-truth target_key partial-mask reveal (oracle leak).
v4 mechanism (theory-clean):
- Round 1: argmax over sims; log-margin = sims[top_1] - sims[top_2]
- CLARIFY if log-margin < MARGIN_TAU = 0.05 (~0.8 * SEM(sim))
- Round 2 (LISTWISE VALUE-MARGINALIZATION):
  - top_K = 20 (~log2(20000))
  - value_scores[v] = logsumexp_{i in top_K, val[i]==v} sims[i]
  - answer = argmax_v value_scores[v]
- **No ground-truth used at any point.** Only sims distribution + kb_val_indices metadata.

## SUBSTRATE-ENVELOPE CAVEAT (transparency)

`hdlab.cortex.CortexConfig` envelope declares `N_DIM >= 8192` (inherited from
M1.5+M1.7 THRESHOLD_ANCHORED_AT_N_DIM). v4 uses N=512 which BREAKS envelope;
therefore v4 CANNOT use `cortex.forward`.

v4 instead implements the **LISTWISE MECHANISM CONCEPT** directly (argmax +
logsumexp value-marginalization over top-K). **v4 is a THEORY-CONCEPT
VALIDATION of listwise-dominance-in-corridor, NOT a test of the cortex facade
code.** Cortex facade code arc-closure is a SEPARATE question at N>=8192.

## Arm Structure

3 arms (mapping to v3 structure for cross-version comparability):

| v4 arm | v3 analog | Behavior |
|---|---|---|
| ARM_LISTWISE_ROUND2 | ARM_CORTEX_ON | argmax + listwise Round 2 on low margin |
| ARM_ARGMAX_SINGLESHOT | ARM_CORTEX_OFF | argmax; always accept; no refuse |
| ARM_ARGMAX_WITH_REFUSE | ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION | argmax + refuse gate |

**PRIMARY DISCRIMINATOR:** `H3_gap = util(ARM_LISTWISE_ROUND2) - util(ARM_ARGMAX_WITH_REFUSE)`.
Secondary: `H1_gap = util(LISTWISE) - util(SINGLESHOT)`.

## Envelope-fail-bands (Pre-committed)

**HARD_PASS gate (v4 primary claim):**
- `H3_gap >= +0.05` AND `gap/SEM >= +2.0`
- corridor_gate: `in_corridor == True`
- arms_differ_verified == True
- baseline_in_band: `0.05 < ARM_ARGMAX_WITH_REFUSE utility < 0.95`
- cardinality: 3 arms x 1 seed (smoke) or 3 x 3 seeds (full)

**MIDDLE_BAND:**
- `+0.02 <= H3_gap < +0.05` (marginal advantage, inconclusive)

**HARD_FAIL:**
- `H3_gap < +0.02`, OR
- `H3_gap >= +0.05` but `gap/SEM < +2.0` (not statistically distinguishable), OR
- `in_corridor == False` (regime out-of-corridor sentinel)

**HP_SCOPE:** All 3 arms subject to arms_differ_verified. H3_gap gate applies
ONLY to comparison between ARM_LISTWISE_ROUND2 and ARM_ARGMAX_WITH_REFUSE.

## SCHEMA-VET Fields (mandatory per exp_dev.md sections 5-16)

- `cardinality_ok`: TRUE (3 arms x 1 seed = 3 units)
- `arms_differ_verified`: TRUE (SHA256 hashes of retrieval sequences)
- `final_metrics_atomicity`: `tmp_replace` (`os.replace()` on `metrics.json.tmp`)
- `except_ordering`: `SystemExit -> KeyboardInterrupt -> Exception` (no BaseException)
- `crlb_n/a`: N/A (utility-metric cell; corridor-position is capacity proxy)
- `discriminator_reachability`: TRUE (LDPC drill predicts +0.02-0.10 acc units in corridor)
- `baseline_in_band`: SMOKE gate on `ARM_ARGMAX_WITH_REFUSE utility in (0.05, 0.95)`
- `sweep_alignment_verdict`: N/A (no sweep axis; single regime)
- `discriminating_fraction`: N/A (single regime)
- `composition_edges`: none (single-arm direct-retrieval; no composition chain)
- `positive_control_arms`: none required (v4 is not a re-invocation of prior CG primitive)
- `functional_requirements`:
  - FR1: correct-value retrieval on clean queries (100% expected)
  - FR2: correct-value retrieval on noisy queries via listwise pooling
        (`gap vs argmax` in corridor)
  - FR3: refuse OOB queries at REFUSE_TAU = 0.25
- `progress_logging`: `print_flush_true` (per-arm print with flush=True)
- `start_marker_written`: TRUE (_start_marker.json)
- `crash_diagnostic_present`: TRUE (`_write_crash_metrics` on Exception)
- `heartbeat_present`: TRUE (`emit_heartbeat` per-arm)
- `defensive_error_checking`: passed_all_4_patterns
- `cell_chunked`: TRUE (single-seed-per-cell; _s7 wrapper)
- `arms_differ_exempted`: none
- `calibration_check`: `default_ok_for_this_regime` (fixed thresholds theory-grounded)

## Compute architecture

Class: **(b) sequential-CPU with justification**.
- Per-query cost: 1 matmul (M * N = 10.2M ops) ~= 5-10ms on CPU + logsumexp per class
- 30 queries x 3 arms x ~5-10ms = ~1-2s per seed SMOKE
- FULL (100 queries): ~5-10s per seed
- Below GPU-batching threshold (per-arm wall < 10s); sequential-CPU justified.

## Storage strategy

**SHARDED**: each of M=20000 KB items has its own key vector (float32).
Total KB memory: 20000 * 512 * 4B = 41 MB. In-RAM feasible.

## Pre-committed prediction (LDPC drill authority)

**PREDICT:** `H3_gap >= +0.05` with `gap/SEM >= +2.0` (positive lift 0.02-0.10 acc units per LDPC drill dominance-corridor theory).

**Outcome verdicts:**
- **PASS:** cortex listwise-soft-evidence beats argmax in dominance corridor
  -> atom `LISTWISE_STRICTLY_DOMINATES_ARGMAX_IN_CORRIDOR_v4_MM_TENTATIVE`
  -> single-task arc **REOPENS** at corridor-scoped atom
  -> Skunkworks-authoritative post-VET tier decision
- **MB:** `+0.02 <= H3_gap < +0.05`
  -> escalate to FULL 3-seed CV; needs stronger evidence
- **FAIL:** `H3_gap < +0.02` OR statistical gap
  -> DEFINITIVE atom `NO_LISTWISE_ADVANTAGE_EVEN_IN_THEORY_OPTIMAL_CORRIDOR_v4`
  -> single-task arc **CLOSES** at MM_STANDARD
  -> escalate to research: spatial-coupling analog per LDPC drill (structural not decoding-time)

## Kill-switch cascade

If v4 primary (N=512, M=20000) fails:
1. Try (N=400, M=10000): d^2/(n log n) = 1.74 (upper edge of corridor)
2. Try (N=300, M=6000):  d^2/(n log n) = 1.72 (upper edge of corridor)
3. If BOTH fail: filed as DEFINITIVE cortex-composition negative even under
   theory-optimal regime; single-task arc CLOSES at MM_STANDARD.

## Anti-drift discipline

- Corridor test LOCKED in code + selftest BEFORE running.
- Soft-evidence semantics LOCKED (logsumexp per class over top-K).
- Prediction (H3_gap >= +0.05, gap/SEM >= +2.0) LOCKED before running.
- No threshold re-tune between smoke and full; parameters frozen a-priori.
- If FAIL: honest-negative escalation; NO re-tune; escalate to research.

## Numbers tagged (META_RULE_AC)

- v3 H3_gap = -0.033 to -0.058 range: MEASURED@ v3 metrics.json (prior arc)
- v3 corridor position d^2/(n log n) = 39000: THEORETICAL@ compute_corridor_position(8192, 300)
- v4 corridor position d^2/(n log n) = 1.324: THEORETICAL@ compute_corridor_position(512, 20000)
- Expected listwise lift 0.02-0.10 acc units: CITED@ arxiv 2605.05189 + LDPC drill 2026-07-04
- Random-baseline sim at N=512, M=20000: 0.197: THEORETICAL@ sqrt(2 ln M / N)
- Signal at flip=0.35: 0.30: THEORETICAL@ 1 - 2*flip
- SNR at Round 1: 0.30/0.197 = 1.52x: THEORETICAL@ signal/noise ratio
- REFUSE_TAU = 0.25 (above noise 0.197, below signal 0.30): HYPOTHESIZED@ this-prereg
- MARGIN_TAU = 0.05: HYPOTHESIZED@ this-prereg (~0.8 * SEM)

## Timeout

`--timeout 300` (5 min; smoke wall ~1-2s + startup overhead + safety margin).

## Dispatch

- SMOKE: `local_cpu_queue` (per USER-locked 2026-07-01 rule; SMOKE only local).
- FULL: NOT dispatched from this cell-shipping cycle; escalate via Director on
  smoke verdict (goes through Orchestrator for remote_cpu_queue push).

## Composition rule

**Skunkworks-authoritative pre-emptive:**
- v4 SUPERSEDES v2b/v3 arc-closure IF PASS: revival succeeds under theory-
  grounded design; single-task arc REOPENS at corridor-scoped conditional atom.
- If FAIL: filed as DEFINITIVE cortex-composition negative even under theory-
  optimal regime; single-task arc closes at MM_STANDARD.
- Cite v1/v2/v2b/v3 chain + LDPC drill 2026-07-04 + multi-round retry drill.
