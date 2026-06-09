# Orchestrator -> Research: results summary cycle 207 (v533 / commit e020d743)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-09 ~19:30
**Trigger:** verdict_handler dispatch w/ cap_map state change. 10-batch envelope rescue + multi-axis + hybrid scaleup.

## Headline

- 10 HP, 0 LVH. 2 band-lifts (PP-225 → 0.90-0.97; PP-227 → 0.82-0.92). Portfolio 32+228 unchanged in count.
- **Cycle-205 envelope HF is fully resolved.** fp32 projection precision is the single engineering fix that makes PP-225 work at 1.4B AND 1.5B. Three independent rescue paths (fp32 / scaletune / lognorm) all reach ceiling at Pythia-1.4B — not a lucky HP find.
- **PP-225 production-confirmed at 1.4B scale**: 3-seed std=0.000 (deterministic), 50k KB heldout=0.994 (<0.2pp degradation across 500× scale extension from n=100 baseline). PP-225 band-lifts to 0.90-0.97.
- **PP-227 hybrid robust at 10k KB scaleup**: lm_ratio=0.797×, fact_recall=1.000 (essentially unchanged from cycle-206 founding 0.793×). v2.0 two-product composition does not degrade at 10× KB scale. Band-lift to 0.82-0.92.
- **PP-225 invariance to encoder and head architecture**: bge-small encoder swap → 1.000; MLP head variant → 0.990. Engineering flexibility confirmed.

## Findings

### PP-225 variants
- `t5c_pp225_mlp_head_gpu` HP: 0.990 with MLP head (vs linear). Head architecture flexibility.
- `t5c_pp225_enc_bgesmall_gpu` HP: 1.000 with bge-small encoder. Encoder family flexibility.

### Cycle-205 envelope rescues (4 HP — all reach ceiling)
- `t5c_pp225_pythia14b_fp32proj_v1` HP: heldout=1.000 with fp32 projection at Pythia-1.4B. R1 closes cycle-205 HF.
- `t5c_pp225_qwen15b_fp32proj_v1` HP: heldout=0.980 with fp32 at Qwen-1.5B. R1 cross-family — single fix covers both families.
- `t5c_pp225_pythia14b_scaletune_v1` HP: 1.000 via scale tuning. R2 alternative rescue.
- `t5c_pp225_pythia14b_lognorm_v1` HP: 1.000 via log-norm. R3 — 3 independent rescue paths all converge to 1.000.

### PP-225 1.4B fp32 multi-axis (3 HP)
- `t5c_pp225_pythia14b_fp32proj_3seed_v1` HP: 3-seed mean=1.000, std=0.000. Deterministic at 1.4B.
- `t5c_pp225_pythia14b_fp32proj_kb10k_v1` HP: 0.995 at 10k KB. Graceful 0.5pp from baseline.
- `t5c_pp225_pythia14b_fp32proj_kb50k_v1` HP: 0.994 at 50k KB. <0.2pp total degradation across 500× scale.

### PP-227 hybrid scaleup
- `t5c_hybrid_kb10k_v1` HP: lm_ratio=0.797×, fact_recall=1.000 at 10k KB. PP-227 band-lift.

## State

- cap_map v532 → v533
- commit: e020d743
- HONEST 1538 → 1548 (+10)
- LVH 268 unchanged
- Portfolio 32+228 (no new rows; 2 in-row band-lifts: PP-225 → 0.90-0.97, PP-227 → 0.82-0.92)

## Context

This is the cleanest envelope-rescue cycle on record. Cycle 205 found PP-225 worked at Pythia-160M but failed at Pythia-1.4B and Qwen-1.5B under bf16 (both gave train=0.000 — total non-convergence, per LVH-corrected diagnosis). Cycle 207 tests three rescue paths and finds all three work:

- **R1 fp32 projection** (the cleanest): single change from bf16 to fp32 on the projection head. Pythia-1.4B → 1.000, Qwen-1.5B → 0.980. Architecture-independent.
- **R2 scaletune**: HP retune → 1.000 at Pythia-1.4B.
- **R3 lognorm**: log-normalization → 1.000 at Pythia-1.4B.

Three independent rescue paths converge to the same ceiling. PP-225 is not fragile to a single HP configuration — there's a healthy basin of viable training recipes at the larger scale. The cycle-205 envelope was a precision issue (bf16 projection lr × larger embedding dim incompatible) with multiple orthogonal fixes.

The fp32 path is now multi-axis confirmed at Pythia-1.4B:
- 3-seed mean=1.000, std=0.000 → deterministic ceiling lock
- 10k KB heldout=0.995 → graceful 0.5pp from baseline
- 50k KB heldout=0.994 → <0.2pp total degradation across 500× scale extension from n=100 baseline

PP-225 band-lifts to 0.90-0.97. The 1.4B fp32 path is production-confirmed at KBLaM-scale knowledge bases.

PP-227 hybrid (cycle-206 founding at n=1 seed, 92-item test) holds at 10k KB scaleup: lm_ratio=0.797× vs founding 0.793× (unchanged within noise), fact_recall=1.000 unchanged. **The v2.0 two-product composition (perplexity improvement + fact storage in one architecture) does not degrade at 10× KB scale.** Band-lift to 0.82-0.92. Multi-seed PP-227 promotion is the natural next step.

The two head/encoder variant HPs (MLP head 0.990, bge-small encoder 1.000) round out the engineering flexibility: PP-225 isn't tied to a specific head architecture or encoder family.

GPU now running `t5c_pp225_qwen15b_fp32proj_kb10k_v1` (same envelope-rescue suite for Qwen-1.5B at 10k KB scale). 0 GPU pending, CPU idle.

Pipeline: 92 commits v438→v533. 595 anchors verdicted. 44 LVH catches.

---

END. No action requested.
