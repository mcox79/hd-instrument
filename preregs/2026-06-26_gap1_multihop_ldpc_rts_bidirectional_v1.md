# Pre-registration: gap1_multihop_ldpc_rts_bidirectional_v1

**Date:** 2026-06-26
**Anchor:** gap1_multihop_ldpc_rts_bidirectional_v1
**Queue:** local_cpu_queue (default per handoff; route to remote_cpu_queue via orchestrator if smoke shows > 2h wall)
**Script:** experiments/exp_gap1_multihop_ldpc_rts_bidirectional_v1.py
**Cell-author:** exp_dev (spawn under Agent-Teams Phase 3)
**Driver hand-off:** notes/exp_dev_handoff_research_gap1_multihop_5x_drill_2026-06-26.md
**Source drill:** notes/research_gap1_multihop_5x_drill_2026-06-26.md

## Scientific question

Does BIDIRECTIONAL forward-backward refinement of substrate multi-hop chains
lift depth-5 retrieval accuracy from the 0.145 floor at production
random-bipolar regime (V_C=200, V_P=10, K_set=20, n_chains=200, N_DIM=8192)?

Specifically test TWO mechanisms that share forward-pass infrastructure:
1. **LDPC sum-product** (Anchor 1): 3 sweep iterations of forward + backward
   soft-message passing on the chain factor graph; lit anchor MacKay-Neal 1996.
2. **RTS smoother** (Anchor 2): one forward + one backward pass with
   Gaussian-mixture product per hop; lit anchor Sarkka 2013 / Foster-Wilson 2006
   brain-grounded reverse-replay analog.

Both target the FORWARD-ONLY HARD-DECISION CHAINING pathology that all 5
prior multi-hop attempts (consolidation, pointer-chain, WM-scaffold, CSP-gated,
the v2 baseline-rail-fixed cell) share -- per-hop accuracy sequence
[0.69, 0.485, 0.31, 0.205, 0.145] is BIT-IDENTICAL across them, indicating they
reduce to the same downstream-of-cleanup primitive on a crosstalk-saturated W.

## Discipline / disciplines applied (load-bearing)

- ASCII-only in script + prereg + verdict.
- Synthetic random-bipolar atoms (clean methodology per `feedback-clean-encoder-tests`).
- Sanity rail: ARM_BASELINE_pointer_chain_v2 MUST reproduce 0.145 +/- 0.02 on
  majority of seeds (otherwise verdict = SANITY_BREACH, no anchor claims).
- Per-arm metrics (Fix #28): each arm's top1 / per_step_acc / mechanism
  readable independently from `per_seed[i][arm_name]`.
- Zero LLM forward calls at inference (counter + assert == 0).
- Per-seed CONFIG_VERSION-gated checkpoint via experiments/_seed_checkpoint;
  atexit synth recovers partials on kill/timeout (PROT-021 not formally
  required at this timeout but checkpoint enabled anyway -- best practice).
- BIAS-Q saturation guard: bands carry HARD_FAIL paths even at top1 near 1.0.
- META_M7 smoke matches full on capacity-sensitive dims (depth=5 in both).
- LOCK pre-reg bands at module init via assert chain (see source lines 96-103).

## Pre-registered bands (LOCKED at module init)

### Sanity rail (cell-wide gate)
- ARM_BASELINE_pointer_chain_v2 mean depth-5 in [0.125, 0.165] on majority of
  seeds. If breached, cell verdict = SANITY_BREACH (no anchor claims).

### ARM_LDPC_BIDIR (Anchor 1)
- **HARD_PASS:** mean depth-5 >= 0.50 AND > ARM_SOFT_FWD + 0.10 AND sd <= 0.06.
- **HARD_FAIL:** mean depth-5 <= 0.25 OR LDPC - SOFT_FWD <= 0.03.
- **MIDDLE:** 0.30 <= mean depth-5 < 0.50 (structural lift, not chain-grade).

### ARM_RTS_SMOOTH (Anchor 2)
- **HARD_PASS:** mean depth-5 >= 0.50 AND super-additive over MAX(BASELINE,
  BACKWARD_ONLY) by 0.10 AND sd <= 0.06.
- **HARD_FAIL:** mean depth-5 <= 0.25 OR smoothed mean <= 1.05 * MAX(BASELINE,
  BACKWARD_ONLY).
- **MIDDLE:** 0.30 <= mean depth-5 < 0.50.

### Cell-wide verdict
- **SANITY_BREACH:** majority of seeds violate sanity rail.
- **HARD_PASS_GAP1_BIDIRECTIONAL_LIFT:** either anchor hits HARD_PASS.
- **MIDDLE_BAND_GAP1_PARTIAL_LIFT:** either anchor hits MIDDLE_BAND (and neither HARD_PASS).
- **HARD_FAIL_GAP1_BIDIRECTIONAL_REFUTED:** both anchors HARD_FAIL.
- **UNDETERMINED_GAP1:** neither bands met cleanly (rare; investigate).

### Decision logic per source drill section 'CHEAP DECISIVE TEST'
- If LDPC OR RTS chain-grade: dispatch follow-up cells for N2 (VTE-MCTS) +
  P1 (MPS) + R1 (particle-filter) to determine best overall.
- If both MIDDLE_BAND: pivot to N2 VTE-MCTS as next-best.
- If both HARD_FAIL: pivot to P1 MPS bond-truncation as orthogonal angle.
- If P1 also HARD_FAIL: dispatch X1 dense-Hopfield primitive replacement.

## Config (handoff-mandated production regime)

- **N_DIM:** 8192 (handoff: "production regime constants").
- **V_C:** 200 atoms per partition (concept vocabulary).
- **V_P:** 10 predicates.
- **K_SET:** 20 (top-K cleanup width; substrate primitive default).
- **n_chains:** 200 chains for testing.
- **depth:** 5 (focal depth per Gap-1 drill).
- **seeds:** [7, 17, 23, 31, 41] (5 seeds for sd-tightness per handoff).
- **ldpc_sweeps:** 3 (lower bound of handoff's "3-5 sweeps to LLR convergence").

Smoke config (N=2048, n_chains=40, 1 seed) chosen to fit under the gate's
SMOKE_TIMEOUT_S=180 ceiling; same depth=5 (META_M7 compliance on the
capacity-sensitive dim).

## Calibration rationale

Per source drill: P_deflated for at-least-one-HARD_PASS among
{LDPC, RTS, VTE-MCTS, MPS, particle-filter} = 0.45-0.60 (correlated). For
this specific bundled cell (LDPC + RTS): P_deflated = 0.45 each (highest in
Gap-1 drill).

The "BIDIRECTIONAL adds 0.10 over the better single-direction arm" delta
encodes the structural-lift claim: simple soft-forward + reverse-replay are
ABLATIONS; if EITHER bidirectional mechanism is to be CHAIN-GRADE distinct,
it must beat the ablation by at least the structural margin. This is the
super-additivity discipline that distinguishes a real bidirectional lift
from a passive averaging benefit.

The 0.50 HARD_PASS floor is set per handoff section 5 ("at least one of
{C1, N1, N2, P1, R1} delivers ARM-mean depth-5 >= 0.50 with sd <= 0.06 over 5
seeds at production regime"). Chance at V_C=200 = 0.005. Random-bipolar
single-hop W cleanup at this regime gives ~0.69; the depth-5 floor of 0.145
reflects 0.69^5 = 0.156 compounding. A jump to 0.50 implies the bidirectional
refinement is effectively HALVING the per-hop error rate (loose interpretation;
floor calculation involves not just per-hop accuracy but the message-passing
information gain across hops).

## Compute / timeout estimate

Per-seed wall (estimated from v2 BASELINE_RAIL_FIXED elapsed):
- Setup + W ingest: ~5s
- ARM_BASELINE pointer-chain at depth-5: ~25s (v2 measured)
- ARM_SOFT_FWD: ~25s (same shape; one extra (V_C, N_DIM) matmul per hop)
- ARM_BACKWARD_ONLY: ~30s (backward soft + forward re-derive)
- ARM_LDPC_BIDIR (3 sweeps x fwd+bwd): ~150s
- ARM_RTS_SMOOTH (1 fwd + 1 bwd + product): ~50s
- Total per seed: ~285s
- 5 seeds: ~1425s = 24 min wall

Timeout: 5400s (90 min, ~3.8x estimate) to absorb noise / mid-run variance.

## Routing

- **Default:** local_cpu_queue (per handoff "Local CPU default").
- **Escalation:** if smoke shows > 2h wall on laptop CPU AND cell is
  matmul-bound, route to remote_cpu_queue via hdi_orchestrator (Fix #24
  reaction). Current handoff context (local_cpu_queue blocked on NESS hang
  until ~23:26 PDT timeout) suggests smoke first; queue insertion will land
  behind 7 pending entries.

## Risk class / scope

- **Lane:** PRIMITIVE_TEST_synthetic_apples_to_apples.
- **Risk class:** structural-additive. LOW (no new primitives; wiring change
  on existing pointer-chain + sum-product readout addition).
- **Corpus provenance:** synthetic_random_atoms_M{chains*depth}_VC200_VP10_K20_N8192_seeds_7_17_23_31_41.

## Mapping back to Gap-1 substrate-product implications (per drill section)

If LDPC OR RTS HARD_PASS lifts depth-5 from 0.145 to >= 0.50: unlocks 5-hop
reasoning at production V_C/V_P regime (audit-chain capability with per-hop
covariance/LLR as native refuse-gate signals). Composes directly with the
audit-trail rail (Gap-4 product story).

If both HARD_FAIL: per the drill, signals to pivot to (a) N2 VTE-MCTS
speculative rollout, (b) P1 MPS bond-truncated tensor-network, or (c) the
primitive-replacement candidate X1 dense-Hopfield + sparse-bipolar.

## Hand-off acknowledgements

- Research drill ranking + bands: `notes/research_gap1_multihop_5x_drill_2026-06-26.md`
- exp_dev handoff: `notes/exp_dev_handoff_research_gap1_multihop_5x_drill_2026-06-26.md`
  (cell-author parameters chosen within pre-registered bands per handoff
  autonomy declaration; combine ANCHOR 1+2 in single 5-arm cell as recommended
  in handoff Recommended dispatch sequence #1).
- Predispatch check (Fix #26): `python tools/predispatch_check.py
  gap1_multihop_ldpc_rts` -> PROCEED (no prior landings or atoms;
  zero false-positive risk).

## Skunkworks landed-VET ask (post-land)

- Re-derive {LDPC, RTS, SOFT_FWD, BACKWARD_ONLY} headline numbers off
  `per_seed[i][arm_name].top1` independently (don't trust verdict_msg).
- Verify sanity rail: per-seed `arm_baseline_pointer_chain_v2.per_step_acc[4]`
  in [0.125, 0.165] -- the SACRED 0.145 anchor.
- Audit LDPC convergence: `mean_sweeps_to_converge` should be < n_sweeps_max=3
  on a meaningful fraction of chains (indicates real iterative refinement,
  not stuck at sweep-0 single pass).
- Cross-check super-additivity claim on RTS: arm_rts_smooth.top1 vs
  MAX(arm_baseline_pointer_chain_v2.top1, arm_backward_only.top1).
- LLM-call counter assert: `metrics["_llm_forward_calls_at_inference"]` == 0.
