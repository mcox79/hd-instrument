# Pre-registration: substrate_three_tier_generational_v1p1

**Date:** 2026-07-01 (v1 authored + smoke HP; v1.1 shipped after full 4hr-timeout stall)
**Anchor:** substrate_three_tier_generational_v1p1
**Queue:** local_cpu_queue (CPU-only numpy; smoke wall verified <60s post-v1.1 batched scoring; full <45min per seed)
**N:** 8192, **Seeds (full):** [7, 13, 19], **M_atoms (full):** 200, **T (full):** [10, 50, 100]

## v1.1 changes (CRITICAL — supersedes v1 dispatch)

**Root cause of v1 full-run stall:** v1 core used per-atom score_atom_importance loop (M matmuls of (N,N)@(N,) per promotion) at O(M * N_RETRIEVE_STEPS * N^2). At M=200, N=8192 that's 200 promotion cycles * 5 * 8192^2 = 6.7e10 ops per promotion, and t=100 arm has ~400 promotions = 2.7e13 ops/arm. Measured actual wall v1 t=10 arm: TWO_TIER=1833s, THREE_TIER=3191s. Extrapolated t=100: ~30000s per arm = 24hr full run. Runner 4hr timeout killed seed_7 after 2 of 6 arms (both at t=10).

**v1.1 fix:** `score_atoms_batched()` replaces per-atom loop with a batched matmul: `(N,N) @ (N,M)` in a single call, O(M) faster via BLAS. Correctness verified via T8 selftest (corr=1.0 vs per-atom on same seed). Expected wall reduction: 100-200x on numpy BLAS. Revised full-run forecast: ~500s per seed = ~25min total for 3 seeds.

**Salvaged v1 measurements (seed_7 t=10 partial arms, discarded due to core change):**
- ARM_TWO_TIER_t10: final_forget=0.29 (TWO_TIER wins at low replay)
- ARM_THREE_TIER_t10: final_forget=0.80 (THREE_TIER loses at low replay)
- delta at t=10 = -0.51 (THREE_TIER underperforms at low t; expected — mechanism designed for high t)
This reinforces pre-reg framing: discriminator is at t=100 not t=10.

## Scientific question

TWO_TIER generational W (STM=W_young, LTM=W_old) is chain-grade. Systems consolidation literature (Squire-Alvarez 1995; McClelland-McNaughton-O'Reilly 1995 CLS) posits an INTERMEDIATE stage: labile hippocampal traces stabilize via cortical replay through an intermediate medial-temporal representation before neocortical consolidation. Does adding a middle W_itm tier -- with staged promotions STM->ITM (fast, every M/4 cycles) and ITM->LTM (slower, every M/2 cycles) -- add retention over TWO_TIER at high replay counts (t=100)?

Compose with existing TWO_TIER generational CG (baseline arm) and NREM replay CG (per META_RULE_AT).

## Pre-registered bands (LOCKED via module-init assert)

**HARD_PASS_THREE_TIER_ADDS_RETENTION (all 4 conditions):**
- THREE_TIER retention delta over TWO_TIER >= 0.05 at t=100 replays
- cross-seed pairwise cv on retention gap <= 0.10
- ITM tier state hash distinct from STM + LTM hashes across ALL seeds (META_RULE_AX)
- ITM utilization (W_itm_norm / combined_norm) >= 0.05 at t=100 (tier not vestigial)

**HARD_FAIL_ITM_REDUNDANT:** THREE_TIER final_forget within +/- 0.02 of TWO_TIER at t=100 (intermediate tier not load-bearing at this regime).

**MIDDLE_BAND:** THREE_TIER delta in (0.02, 0.05) at t=100 -- mechanism partial; OR wins at some t but not t=100 (regime-conditional).

## Discriminator-must-survive-scale (META_RULE_AX + smoke discipline)

Smoke uses SAME N=8192 as full (META_M7 capacity-sensitive-dims). Only M_atoms (40 vs 200), T_LIST ([100] vs [10, 50, 100]), and SEEDS (1 vs 3) reduce. Smoke fires the discriminator arm t=100 at full-N. If smoke shows |THREE_TIER_forget - TWO_TIER_forget| < 0.02 at t=100 (HARD_FAIL band), cell will NOT dispatch full -- surviving-scale discriminator honestly failed.

## Calibration rationale

- Retention delta 0.05: matches HARD_PASS_PARTIAL_DRIFT_REDUCTION magnitudes seen in TWO_TIER v1 pre-reg; conservative to avoid over-claiming a small-effect axis-P extension.
- CV ceiling 0.10: relaxed vs TWO_TIER v1 (0.07) because the discriminator is a DIFFERENCE (two_forget - three_forget), not a single-arm measurement -- differences have compounded noise floor.
- ITM utilization floor 0.05: prevents "ghost tier" pass where W_itm receives 1 atom and never fires; anchors "tier is used."
- HARD_FAIL tol 0.02: strict; if the intermediate tier is truly redundant, the difference should be < 0.02 (matches TWO_TIER v1's HARD_FAIL discrimination floor).

## META_RULE compliance

- **META_RULE_AX arm-distinctness:** ITM state hash MUST differ from STM + LTM per seed. Enforced in verdict via `arm_distinctness_by_t[t_disc]` gating HARD_PASS.
- **META_RULE_AT composition:** THREE_TIER composes with (a) TWO_TIER v1 (baseline arm), (b) NREM replay v1 (upstream replay primitive; T7 self-test validates NREM-compose smoke-safe).
- **META_RULE_H CARDINALITY_OK:** expected arm count = 2 structures x len(T_LIST) = 6 arms full / 2 arms smoke. Enforced via module-init `assert len(ARMS) == 2 * len(T_LIST)`.
- **META_RULE_Q suspect-1.000:** if THREE_TIER hits final_forget=0.000 at t=100 while TWO_TIER is 0.500+, verdict-time detail preserves per-arm final_forget for post-hoc audit.
- **META_M7 capacity-sensitive dims:** N=8192 identical smoke/full.

## Anchor-name suffix (PROT-018)

Anchor name does NOT contain _n<N> suffix. Cell's production N=8192 is canonical for the axis-P generational class.

## Timeout estimate (v1.1 REVISED)

Smoke: 1 seed x 2 arms x t=100 replays x M=40 atoms = 8000 cycles per arm at N=8192. v1.1 batched scoring: ~40s per arm; smoke total ~90s under SMOKE_TIMEOUT_S=180.

Full: 3 seeds x 6 arms. Per-arm wall dominated by W matmul (N^2 per cycle) + batched promotion scoring (single O(M*N^2) BLAS matmul per K cycles).
- t=10 arm (2000 cyc): ~5s (measured smoke ratio confirms)
- t=50 arm (10000 cyc): ~25s
- t=100 arm (20000 cyc): ~50s
- promotion overhead now batched: ~50ms per promotion event * ~10 events = 0.5s per arm-seed
- total per seed: ~80s x 2 structures = ~160s per seed
- 3 seeds ~= 480s total, buffered 3x for I/O / GC = 1440s (~24min)

Recommended `--timeout 3600` (1hr; PROT-019 floor for N>=4096; ample margin).

## Compose upstream

- `gap4_two_tier_generational_W_v1` (baseline TWO_TIER arm at every t)
- `exp_substrate_continual_NREM_replay_v1` (NREM replay compose validated via T7 self-test)

## Reference to gap analysis

`notes/research_phase_diagram_gap_analysis_next_cells_2026-07-01.md` sec 4 (Axis P; CG=0.35, payoff=MED)

## Falsifiable outcomes (echo of Research hand-off)

- HARD_PASS: THREE_TIER wins >= 0.05 retention at t=100 across seeds; cv<10%; ITM tier used
- HARD_FAIL: THREE_TIER identical to TWO_TIER (ITM = redundant)
- MIDDLE_BAND: THREE_TIER wins at some t but not others; regime-conditional
