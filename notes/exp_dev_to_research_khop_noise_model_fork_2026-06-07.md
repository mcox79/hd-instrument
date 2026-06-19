# Exp-Dev -> Research: INTRACTABLE -- K-hop cross-shard noise model B-direction fork

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** bundle_noise_khop (Chain3 Drill3) + production_scaling (Chain3 Drill4)

## The intractable problem (escalating per standing instruction)

The K-hop bundle-noise anchors are ambiguous on **how cross-shard relay noise scales with bundling factor B**, and I cannot resolve it from the handoffs alone. The two handoffs imply OPPOSITE directions:

- **Drill 3 handoff** predicts K_max **DECREASES** with B (B=2 -> K_max>=18, B=10 -> K_max>=12). This implies fan-out across B shards **adds** distractor noise (B-1 interferers bundled in).
- **Standard HDC superposition physics** (what I implemented) says bundling B noisy relay copies **AVERAGES** noise down ~sqrt(B), so K_max **INCREASES** with B. My battery measured exactly this: K_max(B1)=8 -> B10=20 (smoke), increasing.

These are different physical models of the coordinator's relay step:
- **Model A (averaging):** the B shards each return a noisy copy of the SAME target association; coordinator averages -> noise/sqrt(B). K_max grows with B.
- **Model B (distractor):** fan-out hits B shards, only 1 holds the true association, the other B-1 return distractors that get bundled in -> noise grows with B. K_max shrinks with B.

**I implemented Model A** (defensible HDC physics) in `khop_bundle_noise_battery_gpu_v1` and `khop_sparse_bsweep_battery_gpu_v1`. If Drill 3's intent is Model B, both cells need the relay step rewritten.

## Additional empirical finding (Model A, full run)
- `khop_bundle_noise_battery_gpu_v1` FULL run: **HARD_FAIL, K_max(B2)<15** at production V_C=4000 (vs K_max(B2)=17 at smoke V_C=512). Larger codebook = more distractor floor = lower K_max even under averaging. Cross-shard K-hop is noise-limited at production codebook sizes regardless of B-direction.

## What I need from Research
1. **Specify the relay mechanism** (Model A averaging vs Model B distractor-accumulation, or a hybrid). This determines the cell design for ALL K-hop anchors (Drill 3 + Drill 4 sparse B-sweep + adversarial-concentration).
2. Confirm whether the pre-reg bands (K_max(B2)>=18 etc.) assume Model B; if so I'll rebuild with distractor-accumulation and re-pre-register.

## Currently queued (Model A) pending your call
- `khop_bundle_noise_battery_gpu_v1` (GPU, full ran HARD_FAIL Model A)
- `khop_sparse_bsweep_battery_gpu_v1` (GPU, queued; B in {1,10,30,100,300,1000} x dense/sparse, sparse/dense K_max gain vs sqrt(10))

Holding the Drill-4 adversarial-concentration + annealing-schedule anchors until the model fork is resolved (they inherit the same relay step).
