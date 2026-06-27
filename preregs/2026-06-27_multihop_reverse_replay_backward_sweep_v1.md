# Pre-reg: multihop_reverse_replay_backward_sweep_v1

**Authored:** 2026-06-27 (exp_dev under USER NO LOCAL directive; M5 brain-mechanism cell)
**Anchor:** `multihop_reverse_replay_backward_sweep_v1`
**Cell:** `experiments/exp_multihop_reverse_replay_backward_sweep_v1.py`
**Routing:** `remote_cpu_queue` (per USER NO LOCAL 2026-06-27)
**Source drill:** `notes/research_drill_brain_multihop_M5_reverse_replay_backward_sweep_3x_2026-06-27.md`
**Companion cells:** `substrate_multihop_bidirectional_meet_middle_v2_META_M7_rail` (CERT-eligible chain-grade; M3 bidirectional); `substrate_continual_NREM_replay_v1` (CERT proven-bound; forward-replay only).

---

## Scientific question

Brain mechanism #5: hippocampal reverse-replay during sharp-wave ripples (Foster-Wilson 2006; Diba-Buzsaki 2007; Ambrose-Pfeiffer-Foster 2016) propagates reward signal back to upstream states in REVERSE temporal order. Substrate's existing sequence-binding S matrix and `replay_cycle` primitive are forward-only. Does adding a SEPARATE reverse-temporal-order store (S_back) lift substrate multi-hop chain accuracy over the forward-only baseline? Specifically: (a) does the composition with M3 bidirectional meet-in-middle (arm D) clear chain-grade over forward-only (arm A); and (b) is the lift driven by TEMPORAL ORDER (vs "any extra replay helps") as discriminated by a shuffled-temporal-order control (arm F)?

## Cell-spec — Six arms

| Arm | Mechanism | Discriminator role |
|------|-----------|--------------------|
| A: BASELINE_FORWARD_REPLAY_ONLY | substrate current state — forward W only | baseline rail |
| B: REVERSE_REPLAY_ONLY | S_back only (W frozen); end-to-start walk | control: does reverse alone work? |
| C: WITH_REVERSE_REPLAY | both forward W AND S_back; equal-weight blend | mechanism |
| D: BIDIRECTIONAL_BOTH | C + meet-in-middle inference on chain queries | M3 composition |
| E: REWARD_GATED_REVERSE | reverse-replay fires only when forward top-1 conf > tau | brain-grounded selectivity (Ambrose-Pfeiffer-Foster 2016) |
| F: RANDOM_REVERSE_REPLAY_DISCRIMINATOR | reverse-replay over SHUFFLED temporal order | **critical**: tests "temporal order matters" vs "any replay helps" |

## Pre-registered bands (LOCKED via module-init asserts in cell)

**HARD_PASS_CHAIN_GRADE_REVERSE_REPLAY:**
- mean over 3 depths {2, 3, 5} and 3 seeds {7, 17, 23}: D top1 - A top1 >= 0.20
- AND C top1 - F top1 >= 0.10 (temporal-order load-bearing)

**MIDDLE_BAND_PARTIAL_REVERSE_REPLAY:**
- D - A in [0.05, 0.20), OR
- D - A >= 0.20 but C - F < 0.10 (lift exists but not temporal-order-driven)

**HARD_FAIL_REVERSE_REPLAY_DOESNT_HELP:**
- D top1 - A top1 <= 0.05 (composition adds nothing measurable above forward-only)

## Calibration rationale

- HP_D_LIFT_OVER_A = 0.20: matches META_M7 bidirectional cell's empirical lift of +0.297 (BIDIR_MEET_MID 0.620 over SINGLE_FWD 0.323); 0.20 is a conservative pass band (~70% of the demonstrated lift) to allow for the S_back-vs-W.T difference in this cell's reverse-walk implementation.
- HP_C_OVER_F = 0.10: discriminator threshold; smaller than the main mechanism lift but big enough to reject "any extra replay helps". F is the exact same machinery as C but with temporal order shuffled in S_back ingest; the only thing changed is temporal order.
- HF_D_NO_HELP = 0.05: well within seed-variance band (cv 0.05-0.07 typical for these regimes); ensures HARD_FAIL is honest "no mechanism" not just noise.

## CARDINALITY_OK (META_RULE_H mandatory)

- Full: 6 arms x 3 seeds x 3 depths = 54 units; EXPECTED_N_UNITS = 54
- Smoke: 6 arms x 1 seed x 3 depths = 18 units; EXPECTED_N_UNITS_SMOKE = 18
- HARD_FAIL_CARDINALITY_BREACH fires if observed < expected (cell-level guard in `verdict_from`).

## N-suffix section

Cell does NOT carry _n<N> in anchor name per author convention (anchor encodes mechanism family, not N). Full N=8192 enforced at module init via `N_DIM = 8192` constant in non-smoke branch. Smoke N=2048.

## Smoke gate (BLOCKS full dispatch)

- N=2048, V_C=80, n_chains=30, seeds=[7], depths=[2, 3, 5]
- All 6 arms must produce top1 in [0, 1]
- Discriminator survives scale: at smoke, C - F gap should be measurable (>= 0.02 minimum trace of mechanism); if C ~ F at smoke, suspect the discriminator is dead and BLOCK full dispatch for re-investigation
- `--self-test` exits 0 (module-init `_selftest()` runs all arms on tiny config)

## Self-test (runs at module init; BLOCKS dispatch if any fails)

- T1: all 6 arms produce top1 in [0, 1] at depths {2, 3, 5}
- T2: S_back norm is non-zero (ingest worked)
- T3: shuffled S_back norm also non-zero (shuffle didn't destroy magnitude, only order)
- T4: bands locked numerics (HP, MID, HF)
- T5: EXPECTED_N_UNITS matches 6 * len(SEEDS) * len(DEPTHS)
- T6: LLM call counter == 0
- T7: reward-gate tau calibrates to a finite float

## Timeout estimate

Smoke ~ ~30s at N=2048 (single seed, ~30 chains, 6 arms x 3 depths; arm D is V_C-loop so dominates).

Full formula: `timeout_s = ceil(1.5 * smoke_wall_s * (8192/2048)^1.5 * (3/1)) = 1.5 * 30 * 8 * 3 = 1080s` per seed for arms A-C, E, F; arm D scales as V_C * (DEPTH-MID) * N which at V_C=200, depth=5, N=8192 is the dominant cost. META_M7 cell at same V_C=200 spent ~900s per seed on arm D alone. For 3 seeds x 3 depths x 6 arms with arm-D ~900s at depth=5 (proportionally less at depths 2/3): per-seed estimate ~3000s; 3 seeds ~9000-12000s.

**timeout_s = 14400** (4hr ceiling; per-experiment requirement; safety factor 1.2x over upper estimate).

## Routing

- Queue: `remote_cpu_queue` (CPU-bound matmul; USER NO LOCAL 2026-06-27)
- Timeout: 14400s
- Push prerequisite: laptop commit must land on origin/main BEFORE dispatch (exp_dev harness-DENIED push; route via Orchestrator)

## What this cell answers

- **HARD_PASS_CHAIN_GRADE_REVERSE_REPLAY**: reverse-replay (with M3 composition) is chain-grade-eligible mechanism for substrate multi-hop; promote S_back to permanent hdlab/ primitive; ratify reward-gating; route to Skunkworks landed-VET tier classification.
- **MIDDLE_BAND_PARTIAL_REVERSE_REPLAY**: lift exists but doesn't clear chain-grade bar OR temporal order isn't load-bearing; route to Skunkworks for tier classification (likely MM not chain-grade).
- **HARD_FAIL**: reverse-replay primitive not load-bearing for substrate composition; retire and re-route to other M-mechanisms (M1 schema, M2 PFC scratchpad, M4 belief-prop, M6 external scratchpad).

## Risk register

- BIAS-Q (suspect 1.000): if any arm at depth-2 lands top1 = 1.000 at V_C=200, surface W-saturation flag in verdict_msg
- BIAS-N (Cramer-Rao referent-verdict-field): per-arm metrics path is `per_seed[*].per_depth[*].{A,B,C,D,E,F}_*_top1` AND `per_seed[*].arm_<name>_mean_top1`; NOT just verdict_msg framing
- BIAS-S (band-calibration regime check): HP_D_LIFT_OVER_A = 0.20 calibrated against META_M7 cell at SAME V_C=200 N=8192 regime; cross-cell-comparable
- Discriminator-must-survive-scale: smoke MUST show C-vs-F gap measurable; if C ~ F at smoke, suspect discriminator dead at scale and BLOCK full dispatch
- Fix #28: verdict reads PER-ARM mean_top1 from `arm_<name>_mean_top1` keys, NOT a summary string
- META_RULE_H CARDINALITY_OK: EXPECTED_N_UNITS=54 explicit; HARD_FAIL_CARDINALITY_BREACH fires if observed < expected
- Reward-gate (arm E) calibration: tau computed at runtime as 75th-percentile of forward-depth-2 top-1 conf; NOT hard-coded; surfaces as `reward_gate_tau` in per-seed metrics

## Companion primitive hoists (this cycle)

1. `hdlab/sequence_memory.py`: added `S_back` matrix + `bind_pair_reverse(k_prev, k_next)` + `predict_prev(k_next)` + `bind_sequence_reverse(keys)`. Forward S unchanged.
2. `hdlab/multi_hop.py`: added `bidirectional_chain(kg, start, end_candidates, relations, midpoint_hop=None)` as a hdlab/ primitive — hoisted from META_M7 cell's chain-grade-validated mechanism. Same-cycle hoist per results-to-application discipline.
3. `hdlab/continual.py`: extended `replay_cycle` with `direction='forward'|'reverse'|'both'` + `W_back` kwarg. Forward direction bit-equivalent to prior version (backward-compatible).

## Strategy-route on landing

- HARD_PASS_CHAIN_GRADE_REVERSE_REPLAY -> Skunkworks landed-VET tier classification + atomization
- MIDDLE_BAND_PARTIAL_REVERSE_REPLAY -> Skunkworks landed-VET (likely MM); Research 2x revival drill on temporal-order arm
- HARD_FAIL -> Research 2x post-mortem (per standing USER rule); route to alternative M-mechanism
