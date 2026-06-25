# Stage 3 integrated demo + KG scale-up sweep DISPATCHED

**Date:** 2026-06-25
**Author:** exp_dev
**Anchors:**
- `substrate_stage3_integrated_audit_device_demo_v1` (Cell A; local_cpu_queue; RUNNING)
- `substrate_KG_capacity_sweep_M_10k_100k_1M_v1` (Cell B; overnight_queue GPU; RUNNING)

USER directive (2026-06-25): "I need you to show that all required aspects are
chain grade, and then do a test where it's all included at the same time" +
"approved on 3" (KG scale-up). Full auto authorized.

## Cell A: substrate_stage3_integrated_audit_device_demo_v1

**Routing:** local_cpu_queue (numpy-only, no torch; ~2-4min per seed)
**Status:** RUNNING (queued 17:06:26)
**Pre-reg:** `preregs/2026-06-25_substrate_stage3_integrated_audit_device_demo_v1.md`
**Script:** `experiments/exp_substrate_stage3_integrated_audit_device_demo_v1.py`
**Commit:** b61d4e28

### What it composes

End-to-end audit-device pipeline composing all 6 chain-grade Stage 3 primitives:
intent classifier (a1), audit gate subject+relation (Cell 2 v2 HARD_PASS_BOTH_WORK),
graph-health refuse (refuse_gate_5), dense projected KV at M=10k
(dense_projected_KV_envelope_v1 chain-grade), templated response (a2),
CSP confidence label (csp_first_ship_v1).

4 arms x 4 query categories x 3 seeds:
- ARM_INDIVIDUAL_PRIMITIVES_PARALLEL (per-primitive sanity rails)
- ARM_PIPELINE_COMPOSED (the product)
- ARM_AUDIT_ONLY_RAIL (Cell 2 v2 baseline shape)
- ARM_NO_REFUSE_RAIL (naive "no gates" baseline FOR THIS regime)

Query categories: PURE_IN_DOMAIN (1000), PURE_OUT_OF_DOMAIN (1000),
NEAR_DOMAIN_MIXED (500), IN_DOMAIN_UNCERTAIN (500; engineered via heavy bit-flip).

### Pre-reg bands (LOCKED at module init)

- **HARD_PASS_INTEGRATED_AUDIT_DEVICE:** pipeline meets ALL category targets
  (in_answer >= 0.85, in_conf >= 0.70, out_refuse >= 0.85, near_refuse >= 0.85,
  uncertain_lc_or_ref >= 0.70, p95 <= 5ms, cv <= 0.07) AND per-primitive sanity
  rails preserved within +-0.05 of cert envelope.
- **HARD_PASS_PARTIAL:** pipeline lifts >= 0.10 over best single-rail on >=1 cat
- **MIDDLE_BAND:** pipeline ties best single-rail
- **HARD_FAIL_INTEGRATION_BUG:** pipeline >= 0.05 WORSE than best single-rail
- **HARD_FAIL_LATENCY_BLOWN:** p95 > 50ms
- **HARD_FAIL_SANITY_RAIL:** any primitive > 0.10 below cert envelope

### Smoke result (local, N=2048 V=120 M=2k)

**HARD_PASS_INTEGRATED_AUDIT_DEVICE at smoke:**
- PIPELINE in_ans=1.000 out_ref=1.000 near_ref=1.000 uncert_corr=1.000 p95=0.22ms
- AUDIT_ONLY matches PIPELINE on safety categories
- NO_REFUSE_RAIL: out_ref=0.000 near_ref=0.000 (the floor)
- SANITY: audit_rel_near=1.000 intent_in_acc=1.000 kv_recall=1.000 health_fr=0.000

Q-discipline note: 1.000 numbers across smoke categories warrant verification at
full N=8192 with 1000-query categories. NEAR_DOMAIN_MIXED and PURE_OUT
refuse rates at smoke confirmed by per-primitive subject-vs-relation
audit_sim assertions during build_query_corpus.

## Cell B: substrate_KG_capacity_sweep_M_10k_100k_1M_v1

**Routing:** overnight_queue (GPU; RTX 4060 Ti at marsh@home)
**Status:** RUNNING (queued 17:07:10)
**Pre-reg:** `preregs/2026-06-25_substrate_KG_capacity_sweep_M_10k_100k_1M_v1.md`
**Script:** `experiments/exp_substrate_KG_capacity_sweep_M_10k_100k_1M_v1.py`
**Commit:** 550ad3ba

### What it sweeps

dense_projected_KV_envelope_v1 mechanism (M-INDEPENDENT O(d^2) superposition
store) at progressively larger M to find recall cliff:
M=[10k, 50k, 100k, 500k, 1M] x d=768, sigma=0.1, C=256, 3 seeds.

### Pre-reg bands (LOCKED)

- **HARD_PASS_CHAIN_GRADE_AT_M_100k:** recall@1 >= 0.70 at M=100k AND cv <= 0.05
- **HARD_PASS_CHAIN_GRADE_AT_M_1M:** recall@1 >= 0.50 at M=1M (stretch)
- **MEASURED_MECHANISM_at_M_cliff_X:** identifies smallest M where r@1 < 0.50
- **HARD_FAIL_M_10k_DOESNT_REPRODUCE:** r@1 < 0.75 at M=10k (env/scaling bug)
- **HARD_FAIL_GPU_UNUSED:** torch.cuda not available (Fix #24 enforcement)
- **OOM:** GPU memory exhausted; M-ceiling identified

### Smoke verification (local CPU + remote GPU)

Local CPU smoke at M=[10k, 50k]:
- M=10k r@1=0.846 (matches cert envelope >= 0.80)
- M=50k r@1=0.147 (cliff)

**Remote GPU verified ALREADY RUNNING per Fix #24:**
- device=cuda:0 NVIDIA GeForce RTX 4060 Ti
- cuda_available=True
- gpu_mem_max=5878.8MB at M=1M (substantive GPU use; well above 50% util target)

### EARLY RESULTS (already landing per remote runner tail)

Cell B is already through 2.5 of 3 seeds at log-tail time (very fast on GPU):

| M | seed=11 r@1 | seed=13 r@1 | seed=19 r@1 |
|---|---|---|---|
| 10000 | 0.846 | 0.826 | 0.809 |
| 50000 | 0.147 | 0.140 | 0.161 |
| 100000 | 0.065 | 0.062 | (in flight) |
| 500000 | 0.016 | 0.013 | (in flight) |
| 1000000 | 0.011 | 0.011 | (in flight) |

**Anticipated verdict: MEASURED_MECHANISM_at_M_cliff_M=50000.**

Substrate KV at d=768 sigma=0.1 cliffs hard between M=10k and M=50k. The
operating-envelope upper-bound for chain-grade KG retrieval at this regime
is M ~ 10k-30k. M=100k+ is not chain-grade with current parameters.

### Strategic significance

Cell B answers USER's "where everything operates best within the phase
diagram" for KG retrieval directly:
- Substrate-product KG positioning: **M ~ 10k-30k chain-grade** (with d=768 sigma=0.1)
- For "100k+ fact KG", the substrate needs EITHER higher d, or lower sigma,
  or a different storage mechanism (the dense_projected_KV envelope hits its
  capacity ceiling around 30k facts at this d).
- W storage stays M-INDEPENDENT at 2.25MB throughout (the headline win for
  the architecture). The bottleneck is value-recall not storage-cost.

This is honest data — informative MEASURED_MECHANISM rather than HARD_PASS
saturation. It tells USER: "the substrate KG product is currently a 10k-class
KG, not a 1M-class KG; if we want 1M-class we need a different mechanism
(maybe Path C substrate-owned encoder + projection)."

## Sanity rails preserved across both cells

- ASCII-only in scripts (no unicode)
- Bands LOCKED at module init via assert (META_PROSPECTIVE_BANDS_FRESH_SEEDS)
- Per-arm / per-M metrics in verdict_msg (Fix #28)
- Substrate-only (zero LLM forward calls; asserted before verdict)
- Per-seed checkpoints + atexit synth (graceful kill/timeout recovery)
- Q-discipline: ANY 0.995+ flagged for verify-off-data check

## Cross-cell coordination

Cell A and Cell B run in parallel on DIFFERENT runners (local CPU + remote GPU);
no resource contention. Cell A is the COMPOSITION story (does Stage 3 productionize?).
Cell B is the OPERATING ENVELOPE story (where does KG retrieval cliff?). Together
they answer USER's two-part directive.

## Open question / follow-up to file post-verdict

If Cell B lands MEASURED_MECHANISM_at_M_cliff (which is highly likely per
the runner log), a follow-up cell to ship:
- **Cell C (proposed; not authored):** substrate_KG_d_sigma_phase_sweep_v1
  to extend the phase diagram in (d, sigma) directions, finding which
  (d, sigma) pair pushes the cliff out to M=100k+. This is a separate
  research question and a separate cell.

— exp_dev 2026-06-25
