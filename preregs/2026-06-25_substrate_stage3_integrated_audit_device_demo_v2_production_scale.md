# Pre-registration: substrate_stage3_integrated_audit_device_demo_v2_production_scale

**Date:** 2026-06-25
**Anchor:** substrate_stage3_integrated_audit_device_demo_v2_production_scale
**Queue:** overnight_queue (GPU)
**N:** 8192, **Seeds:** [11, 13, 19], **M_KV:** 10000

## Why this cell exists

Research drill 2026-06-25 EXT-1: Stage 3 integrated audit-device at PRODUCTION V.

`exp_substrate_stage3_integrated_audit_device_demo_v1` chain-graded at
V_C_IN=600 / V_REL=8 / M_KV=10k (in_ans=1.000 out_ref=1.000 near_ref=1.000
uncert_corr=1.000 p95=4.39ms cv=0.000). Envelope inheritance from refuse-gate
v2 (V_REL <= 50). Production audit-device needs V_C_IN >= 2000 + V_REL >= 50.

This cell answers: "is the substrate-product shippable at production V."
Highest product-impact cell per Research drill. P(solve) ~ 0.50.

## Mechanism

Same pipeline as v1 (intent -> audit-subject -> audit-relation -> graph-health
-> KV retrieve -> templated response -> CSP confidence). Same chain-grade
primitives. Sweeps 4 production-scale operating points within a single seed
to map the (V_C_IN, V_REL) operating envelope.

## Operating points (4)

- (V_C_IN=1000, V_REL=20)
- (V_C_IN=1000, V_REL=50)
- (V_C_IN=2000, V_REL=20)
- (V_C_IN=2000, V_REL=50)   <-- TARGET (production-scale)

Other constants:
- N=8192
- M_KV=10000
- Seeds [11, 13, 19] (cross-cell consistent)
- 1000 queries per (PURE_IN/PURE_OUT) and 500 per (NEAR/UNCERTAIN)

## Scientific question

Does the Stage 3 integrated pipeline retain chain-grade behavior (all 4 query
categories meeting category targets + p95 <= 10ms + cv <= 0.07) at production
V (V_C_IN=2000 + V_REL=50)?

## Pre-registered bands

**HARD_PASS_PRODUCTION_SCALE:** at (V_C_IN=2000, V_REL=50):
- ARM_PIPELINE_COMPOSED:
  - PURE_IN_DOMAIN answer_rate >= 0.85
  - PURE_OUT_OF_DOMAIN refuse_rate >= 0.85
  - NEAR_DOMAIN_MIXED refuse_rate >= 0.85
  - IN_DOMAIN_UNCERTAIN correct_rate >= 0.70
- AND PIPELINE p95 latency <= 10 ms
- AND cv <= 0.07 across seeds

**CHAIN_GRADE_AT_LOWER_X:**
- ARM_PIPELINE_COMPOSED passes ALL HP targets at ONE OR MORE of:
  (V_C_IN=1000, V_REL=20), (V_C_IN=1000, V_REL=50), (V_C_IN=2000, V_REL=20)
- but DOES NOT pass at the target (V_C_IN=2000, V_REL=50)

**HARD_FAIL_REFUSE_GATE_CLIFF:**
- NEAR_DOMAIN_MIXED refuse_rate < 0.50 at ANY operating point with V_REL >= 20
  (envelope assumption breaks; refuse-gate v2 envelope is at V_REL <= 50)

**HARD_FAIL_LATENCY_BLOWN:**
- pipeline p95 > 50 ms at ANY operating point

**MIDDLE_BAND:**
- no operating point hits all HP targets but no HARD_FAIL trigger fires

## Calibration rationale

- HARD_PASS bands inherited from v1's empirically-validated category targets
  (0.85 / 0.85 / 0.85 / 0.70). At production V the primitives are expected to
  degrade slightly; the 0.85 floor is firm.
- p95 <= 10ms (vs v1's 5ms ceiling): production V doubles the matmul cost
  (subject library + relation library grow); 10ms is the production-acceptable
  ceiling.
- cv <= 0.07 because substrate is deterministic per-seed.
- HARD_FAIL_REFUSE_GATE_CLIFF at near_ref < 0.50: refuse-gate v2 envelope says
  V_REL <= 50; if it breaks at V_REL=20, the envelope assumption was wrong.
- HARD_FAIL_LATENCY_BLOWN at p95 > 50ms: well outside production envelope.

## Q-discipline (BIAS-Q: suspect 1.000 results)

v1 produced 1.000/1.000/1.000/1.000 at small V (suspect saturation due to
discriminating regime: in-domain perfectly separable from OOD in the small-V
limit). At V_C_IN=2000 with V_REL=50, the audit primitive's near-domain
disambiguation should produce values < 1.000 if real disambiguation is
happening (signal that the substrate is exercised, not saturated). If all 4
categories produce 1.000 at production V, raise as suspect Q-saturation per
Skunkworks tiering.

## Capacity-feasibility analysis

- Subject library V_C_IN=2000 + relation V_REL=50 at N=8192:
  W_subjects shape (2000, 8192) = 16MB; W_relations (50, 8192) = 400KB.
  Cleanup chain-grade envelope: N >= 8192 for V <= 4000 (per cleanup-integrity
  rule). V_C_IN=2000 is well below; cleanup should be intact.
- Joint (subject_atom x relation_atom) composition introduces effective 100k
  bindings; the audit-gate has separate subject + relation primitives (not
  joint binding) so capacity is V_C_IN + V_REL = 2050, not V_C_IN * V_REL.
- KV dense store M_KV=10000 d=768 sigma=0.1 chain-grade per dense_projected_KV
  envelope.

Capacity feasible; the envelope test is on COMPOSITION at production V.

## N-suffix section

Anchor name does NOT contain `_n<N>` suffix; the cell sweeps V_C_IN x V_REL
at fixed N=8192. PROT-018 does not apply.

## Timeout estimate

Smoke ~ 60-120s at N=2048, 1 seed, 2 operating points (V_C_IN=200, V_REL=8 ;
V_C_IN=400, V_REL=16), 25 queries per cat.
FULL: N=8192, 3 seeds, 4 operating points, up to 1000 queries per cat.
Per-arm matmul: queries * (V_C_IN + V_REL + M_KV) cost.
Scaling: per-arm O(N * (V_C_IN + V_REL)); 4 arms; 4 points.
formula: ceil(1.5 * 120 * (8192/2048)^1.5 * (3/1) * (4_points/2_smoke_points))
       = ceil(1.5 * 120 * 8 * 3 * 2) = 8640s
With overhead for KV matmul + per-query latency + 4 arms (3 evaluated):
budget timeout_s = 14400 (4 h). At PROT-019 ceiling; GPU acceleration via
torch is expected to bring this down to 2-3h actual on overnight queue.
timeout_s = 14400

## Provenance rail

ARM_AUDIT_ONLY_RAIL at (V_C_IN=1000, V_REL=20) must reproduce v1's
audit-only-rail baseline within +/- 0.10 (v1 had near_ref ~ 1.000). If
breaches, raises method-skew flag (the audit primitive itself may have a
regression beyond the V-sweep being tested).

## Fix #24 GPU-actually-used verification

Per Fix #24 (USER 2026-06-22): routing to overnight_queue doesn't make a cell
use GPU; we're using NumPy matmul which runs on CPU even on a GPU machine.
This cell does NOT torch-port. ACK that the cell is CPU-bound even on GPU
machine. The REASON for GPU routing is RAM (V_C_IN=2000 x M_KV=10000 substrate
state) + per-machine parallelism across seeds. GPU cell-author follow-up:
torch-port primitive matmul (would be a separate cell upgrade).

## Cross-cell apples-to-apples

Seeds [11, 13, 19] cross-cell consistent with EXT-3 + EXT-6 + partition_routing_v2.
v1 used [11, 13, 19] (same). Direct comparison.
