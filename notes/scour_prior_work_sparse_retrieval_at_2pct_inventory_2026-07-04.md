# Scour of our own experiments: prior work on sparse retrieval at ~2-3% (inventory + verdicts)

**Author:** Director (Research) | **Date:** 2026-07-04
**Trigger:** USER 5x-drill ANGLE 1 -- "scour our existing experiments" for a FORGOTTEN result that unlocks
retrieval (ret_agree10 >= 0.35) at ~2% sparse. Problem: trained retrieval at 2% = 0.20 vs code-ceiling 0.43;
rank-loss / OPQ-rotation / annealed-STE all failed. USER intuition: "should be EASIER."
**Method:** git log grep + git ls-files (experiments/ + notes/) + off-disk metrics.json reads + ledger grep.
Numbers below are MEASURED@ the cited metrics.json (verified this cycle), not recalled.

---

## HEADLINE (the single load-bearing forgotten number)

**The zero-training code-capacity ceiling was already measured at FULL N=177,899, and it says the block-argmax
code is NOT the bottleneck -- the trained map is.**

`data/exp_encoder_ceiling_density_curve_v1/metrics.json` (commit `27f238e88`, run_mode=full, teacher_n_concepts=177899,
n_test=17790, n_dim=4096, `DIAGNOSTIC_COMPLETE`) is the "bypass-the-student / teacher-through-sparsifier"
diagnostic that the same-day reachability drill (below) recommended as the single cheapest decisive test --
and it was ALREADY RUN, at full scale. Per-arm, zero training, teacher embeddings straight through each code:

| arm (code type) | active % | ret_agree10 | spearman_all | hi80_cos |
|---|---|---|---|---|
| RAW_ISOMETRIC (dense float, identity) | 100 | **1.000** | 1.000 | 0.841 |
| RAW_RANDOM (dense random projection) | 100 | **0.894** | 0.995 | **0.839** |
| ORTHO_K128 (block-argmax, production code) | 3.125 | **0.4295** | **0.848** | 0.404 |
| RANDOM_K128 (random-codebook block sparse) | 3.125 | 0.4249 | 0.820 | 0.410 |
| RANDOM_BLOCK_K128 (control: random block assign) | 3.125 | 0.0006 | -0.002 | 0.001 |
| CHARPOS (orthographic baseline) | -- | 0.067 | 0.669 | 0.550 |
| ORTHO_K256 / K512 / K1024 / K2048 / K4096 | 6.25..100 | 0.546 / 0.650 / 0.736 / **0.794** / 0.794 | 0.915..0.987 | 0.457..0.639 |

**Trained student, same K128, full N** (`data/exp_encoder_retrieval_regime_density_curve_v1/metrics.json`,
`DIAGNOSTIC_COMPLETE`): native BLOCK v5_K128 = **0.197**, v5_K256 = 0.290, v3e = 0.211; RAW_CONTINUOUS trained
mean = 0.169; DENSE_SIGN trained mean = 0.124.

**Reading:**
1. **The block-argmax code at K128 already CLEARS the retrieval target at zero training** (ret_agree10 0.43 >
   target 0.35) and already hits **spearman_all 0.848 ~ the 0.85 rank-fidelity target**. The trained map reaches
   only ~0.20. **The entire deficit is a training/objective gap of 0.43 -> 0.20, NOT a code-capacity gap.**
   This is exactly what `notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md` R1 (landmark/anchor RKD so
   graded geometry is supervised independent of in-batch co-occurrence) is built to fix. => USER's "should be
   EASIER" is CORRECT: we are chasing a trainable map up to a ceiling the existing code already provides.
2. **The `cosine 0.85` leg looks structurally UNREACHABLE by ANY block-sparse code.** hi80_cos caps at 0.639
   at K2048/50% active and is 0.404 at K128; only DENSE (0.839) reaches it. If "cosine 0.85" means
   pair/reconstruction cosine calibration, no sparse block code in the ceiling family meets it (measured cap
   0.64). If "0.85" means rank/spearman fidelity, it is ALREADY met at the K128 ceiling (0.848). This is a
   metric-definition fork worth surfacing to USER -- the retrieval + rank legs are reachable; the magnitude-cosine
   leg may be the wrong (or impossible) target on a bipolar sparse code.
3. **Sparsification, not projection, is the whole loss:** DENSE random projection = 0.894 ret_agree10 (near
   perfect); block-argmax K128 = 0.43. The teacher-projection is fine; block-argmax quantization at 3.125%
   halves retrieval fidelity at zero training. That is the true, measured code ceiling.

---

## Do we ALREADY have a better sparse code than block-argmax (for semantic retrieval)? -- NO.

The ceiling cell tested ORTHO-block, RANDOM-codebook-block, and RANDOM_BLOCK (control) at K=128..4096. ORTHO and
RANDOM tie block-argmax (~0.43 at K128). The only arm that beats it is DENSE (0.894), which is not sparse. No
non-block-argmax SPARSE code has ever been measured to beat block-argmax on semantic ret_agree10. Ledger grep for
a graded/top-k MEASURED semantic-retrieval win returns nothing (only the reasoning-engine writeup, unrelated).

### Graded-sparse / top-k-with-values / sparse-value -- all tested, all HARD_FAIL (but on CAPACITY, not on semantic ret_agree10)
- `data/exp_c1_sparse_value_k10_cpu_v1/metrics.json` -- HARD_FAIL: sparse phasor K=10 cap 132 vs dense 332,
  ratio **0.40**. `notes/exp_dev_to_research_sparse_value_CLOSED_2026-06-08.md`: "sparse-value is CLOSED" (sparse
  phasor carries less energy -> lower SNR vs crosstalk). NOTE: closure explicitly excluded "sparse with a
  sparsity-aware readout, or block-sparse" -- those were NOT tested.
- `data/exp_sparse_value_capacity_cpu_v1/metrics.json` -- HARD_FAIL: ratio **0.94** (sparse still < dense).
- `data/exp_n4_kwta_soft_decode_v1/metrics.json` -- HARD_FAIL: graded **kWTA WORSE than k=1** anchor
  (ceiling_delta = -0.000, best_k=32 == anchor). Soft/graded top-k does not beat hard on bits-per-char ceiling.
- `notes/exp_dev_to_research_DIMSPARSE_result_2026-06-06.md` -- HARD_FAIL: sparse VALUES give ZERO capacity gain;
  capacity was KEY-COLLISION-limited not value-limited; Tsodyks sparse-coding benefit needs sparse KEYS/PATTERNS,
  not sparse values. Dim-expansion (key decorrelation) is the only capacity lever there.

**Caveat that matters:** every graded/value result above is a CAPACITY/algebra task (store-and-recall of random
vectors), NOT the BGE-semantic-neighbor-preservation task. Graded-sparse for semantic ret_agree10 is genuinely
UNTESTED. So "graded sparse lost" is true for capacity, unproven for the current distillation objective.

---

## Factorizers for Sparse Block Codes (IBM/Hersche GSBC line) -- YES, tested (algebra works; planning fails; semantic distill untested)
- `data/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000/metrics.json` -- **HARD_PASS: block-local sparse
  resonator recovers K4=1.00, K8=1.00** (N=1000 smoke). A NON-block-argmax sparse code (K active per block, clean
  unbind) with PERFECT factorizer recall. This is the strongest existing "alternative sparse code" primitive --
  algebra-clean by construction -- but it is a resonator/factorizer recall task on random codebook vectors, NOT
  semantic-neighbor preservation. Repurposable for the free-sparse direction; unmeasured for semantics.
- `data/exp_cross_axis_m_n_k_factorization_beta_5_bridging_v2_seed_7/metrics.json` -- MIDDLE_BAND /
  MEASURED_MECHANISM: substrate factorizes across M/N/K axes at beta=4. `beta_8` SATURATES
  (`notes/exp_dev_findings/exp_cross_axis_m_n_k_factorization_beta_8_bridging_v1_HF_beta8_SATURATES_2026-07-02.md`).
- `data/exp_substrate_hierarchical_block_sparse_v1_smoke/metrics.json` -- **HARD_FAIL: BLOCK_SPARSE_NO_RESCUE**
  (opts=0.100; sbc_cap=310.5). The Hersche GSBC encoding gave NO lift for hierarchical planning
  (`notes/exp_dev_handoff_research_drill_B_hersche_block_sparse_hierarchical_2026-06-28.md`,
  `notes/research_drill_B_hersche_block_sparse_hierarchical_2026-06-28.md`).

Net: the IBM SBC-factorizer line WAS tested -- it is algebra-clean (resonator recall 1.00; cross-axis factorizes)
but does not help COMPOSITION/planning, and was never applied to semantic distillation.

---

## Metric / readout finding worth repurposing: rank survives, magnitude/cosine does not
`data/exp_metric_dependence_top_k_semantic_v3_seed_7/metrics.json` -- **HARD_PASS (FULL, 3-seed)**:
`HP_CLIFF_BRACKET + HP_METRIC_DIFFERENTIATION`, max top10-top1 gap = **+0.288**. Empirically confirms the
sparse-Hopfield (NeurIPS 2023) top-K-survival prediction: under any degradation, **top-K rank-order readout
survives while cosine/top-1 collapse immediately** (cos05/cos08 = 0.000 while top1 = 0.22-0.68). This is a
substrate-noise readout task, not the encoder -- but it is convergent, independent evidence for HEADLINE point 2:
**cosine-threshold is the wrong metric on this substrate class; rank-order (which ret_agree10 already is) is the
right one.** Reinforces decoupling the cosine-0.85 leg from the retrieval leg.
(`notes/exp_dev_findings/exp_metric_dependence_top_k_semantic_v3_HP_CLIFF_METRIC_DIFF_2026-07-01.md`.)

---

## What is genuinely UNTESTED (the real open levers, per today's reachability drill)
`notes/research_drill_encoder_cardinality_capacity_ceiling_0.85_reachability_2026-07-04.md` (4-scan lit synthesis):
the rigid block-WTA IS Product Quantization; it pays an axis-misalignment tax. OPQ-rotation (Rank 2 partial) and
rank-aware loss (Rank 1) map onto levers USER says already FAILED (OPQ commit `39b41a533`; rank-loss). What is
NOT yet tested from that drill's menu:
- **Free global top-k selection** (top-k across all 4096, not one-per-block) -- a genuinely different selection
  mechanism, never tested for semantic retrieval (P_deflated ~0.30-0.35).
- **Additive Quantization (AQ)** -- unconstrained multi-codebook, never tested.
- **Block-local K>1 sparse** (reuse the blocklocal-K26 resonator code, which is already algebra-clean, as the
  semantic code) -- never tested for semantic distillation.

---

## Bottom line for USER strategy
1. **We do NOT already have a better sparse code.** The best existing non-block-argmax sparse primitive
   (blocklocal-K26 resonator, recall 1.00) is algebra-proven but semantically unmeasured; graded/value/soft-topk
   all lost on capacity (untested on semantics).
2. **We do NOT need one to hit the RETRIEVAL target.** The measured zero-training ceiling of the existing
   block-argmax code (ret_agree10 0.43, spearman 0.848 at full N) already clears ret_agree10 >= 0.35 and the
   0.85 rank-fidelity bar. The trained map reaching only 0.20 is a pure objective-scaling gap -> R1 landmark-RKD.
3. **The `cosine 0.85` leg is the one that looks structurally hard** (measured ceiling 0.64 for any block-sparse
   code; only dense reaches 0.85), and two independent findings (ceiling hi80_cos + metric_dependence_v3) say
   magnitude-cosine is the wrong metric on this substrate. Recommend surfacing to USER: decouple the retrieval/
   rank targets (reachable, blocked only by training) from the cosine-0.85 target (may require dense or a
   genuinely different code type; free-top-k / AQ are the untested candidates).

## Key file paths
- Ceiling (LOAD-BEARING): `d:/AI/hd-instrument/data/exp_encoder_ceiling_density_curve_v1/metrics.json` (commit `27f238e88`)
- Trained curve: `d:/AI/hd-instrument/data/exp_encoder_retrieval_regime_density_curve_v1/metrics.json`
- Rescue plan (fix target): `d:/AI/hd-instrument/notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md`
- Reachability drill: `d:/AI/hd-instrument/notes/research_drill_encoder_cardinality_capacity_ceiling_0.85_reachability_2026-07-04.md`
- Blocklocal resonator: `d:/AI/hd-instrument/data/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000/metrics.json`
- Metric survival: `d:/AI/hd-instrument/data/exp_metric_dependence_top_k_semantic_v3_seed_7/metrics.json`
- Sparse-value closures: `exp_c1_sparse_value_k10_cpu_v1`, `exp_sparse_value_capacity_cpu_v1`, `exp_n4_kwta_soft_decode_v1`
</content>
