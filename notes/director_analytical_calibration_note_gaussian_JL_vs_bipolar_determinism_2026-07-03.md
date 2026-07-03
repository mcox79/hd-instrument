# Director analytical calibration note — Gaussian-JL vs bipolar-determinism scope refinement

**Filed:** 2026-07-03 (Director main-thread; Skunkworks-endorsed (iv) epistemic hygiene action)
**Trigger:** Cell 4 episodic-formal discriminative-regime SMOKE HF (commit `1350c7789`); Skunkworks self-audit VET commit reference in cert_ledger 2026-07-03
**Composes with:**
- `META_DISCIPLINE_CELL_AUTHOR_SELF_CORRECTION_3RD_WITNESS` CG_META tier
- `MATH_COSINE_ARGMAX_ROBUST_AT_EXTREME_SPARSE_CUE_JL_ORTHOGONALITY` MM_STANDARD atom (finding stands, mechanism annotation refined)
- `META_SKUNKWORKS_ANALYTICAL_MODEL_CALIBRATION_GAUSSIAN_JL_ASSUMPTION_FAILS_AT_BIPOLAR_DIM_ZERO_CUE_DETERMINISM` MM_TENTATIVE atom (Skunkworks amendment)

## What happened

**Skunkworks analytical prediction (2026-07-03 ~04:20Z):** at flip_frac=0.026 cluster_cos≈0.90 with cosine-JL analysis, expected sig-sib margin ≈ 0.022 vs sib_std ≈ 0.017 → z_sib_beats ≈ 1.29 → P(sib beats signal) ≈ 10% → cosine baseline expected to degrade to r@1 ≤ 0.90 at this regime.

**Cell 4 empirical (2026-07-03 ~05:30Z):** at N=500 ADV_CLUSTER 75% partial-cue and 90% partial-cue, cosine baseline saturates at r@1 = 1.000 across ALL probed regimes including N=800 76% of Tsodyks-Feigelman capacity. **The analytical prediction was quantitatively wrong.**

**Cell-author's independent diagnosis (Cell 4 report):** at n_dim=2048 bipolar geometry with 75% dim-zero cue, remaining 512 active dims are BIT-IDENTICAL to target vector. Deterministic cos(query, target)=0.5000 (variance ZERO). In-cluster sibling deterministic cos(query, sib_filler)=0.4500 (deterministic 0.05 margin). Argmax always resolves to correct target — cosine saturates. Gaussian-JL assumption in Skunkworks analytical model treated sib_cos as Gaussian variance around 0.4500, but bipolar geometry makes the signal channel purely deterministic within cue-active dims.

**Skunkworks self-audit (2026-07-03 ~05:45Z):** independent .venv re-derivation CONFIRMED cell-author diagnosis. sig cos = 0.5000 with variance ZERO on 512 cue-active dims. sib cos = 0.4500 ± 0.00963. Deterministic margin 5.19σ; P(any of 4 sibs beats sig) ≈ 4.18e-7.

## What stands vs what's refined

**FINDING STANDS:** cosine argmax IS remarkably robust at extreme sparse cue on bipolar random codebook geometry. The prior atom `MATH_COSINE_ARGMAX_ROBUST_AT_EXTREME_SPARSE_CUE_JL_ORTHOGONALITY_MM_STANDARD` (2026-07-03 ~04:20Z) empirical claim is validated by Cell 4's cosine=1.000 saturation across all tested regimes.

**MECHANISM ANNOTATION REFINED:** the "JL orthogonality" mechanism attribution was scope-inappropriate for bipolar geometry with dim-zero cue. The correct attribution is:
- **Bipolar + dim-zero cue:** signal channel is DETERMINISTIC BIT-IDENTITY (variance zero on cue-active dims); sibling channel has small Gaussian variance; deterministic margin dominates. Robustness follows from bit-identity determinism, not JL orthogonality.
- **Gaussian filler geometry + dim-zero cue:** would follow Gaussian-JL analysis; sib_std matters; regime where original prediction could hold. Untested empirically.
- **Real-valued sparse filler + moderate corruption:** intermediate; requires empirical characterization

## Discipline lessons

1. **Analytical models MUST specify geometry assumption at atom-time.** The prior atom body was written for Gaussian filler geometry (as implicit assumption of "sib_std" analysis) but was applied to bipolar. This is a scope-drift between atom-body's implicit assumption and application context. Future analytical atoms MUST explicitly state filler geometry constraint.

2. **Skunkworks-side analytical calibration is now a discipline witness.** Cell-author self-correction pattern (CG_META tier, 3+ witnesses previously) now extends to Skunkworks-side analytical predictions being caught by cell-author empirical results. This is healthy audit-of-audit behavior — the epistemic hygiene works at every layer.

3. **Trigger-word discipline extends to analytical predictions.** When Skunkworks issues an analytical prediction (as in the 2-gate promotion criterion Gate 2 reframe recommending cue_zero=0.99), that prediction should be scope-annotated with the filler-geometry assumption AND flagged as HYPOTHESIZED@ until empirically confirmed. Cell 4 exposed that a Skunkworks-derived analytical prediction was HYPOTHESIZED@ but framed as a prescriptive path — appropriate self-correction.

4. **Composes with Cell 3 CG_META cell-author-self-correction pattern.** Now 7+ witnesses of the pattern across:
   - Cell-authors self-correcting own verdict_msg overclaims (3-4 witnesses)
   - Cell-authors catching Skunkworks-side analytical prediction failures (Cell 4)
   - Skunkworks self-auditing when caught (this note references)
   
   Full-pipeline epistemic hygiene is functioning as designed.

## Revival criterion for the amendment atom

`META_SKUNKWORKS_ANALYTICAL_MODEL_CALIBRATION_GAUSSIAN_JL_ASSUMPTION_FAILS_AT_BIPOLAR_DIM_ZERO_CUE_DETERMINISM` MM_TENTATIVE promotes to MM_STANDARD via:
1. Second witness of Skunkworks-side analytical prediction failure at a different regime OR
2. Empirical confirmation of the original JL prediction at Gaussian-filler geometry (the counterfactual regime) — cell-author's downstream request 3 dispatched as (ii) after this note

## Discipline anchor

Any future analytical prediction (either Director-derived, Skunkworks-derived, or cell-author-derived) that includes information-theoretic quantities (SNR, σ margins, capacity bounds, JL orthogonality, robustness thresholds) MUST include the filler-geometry constraint AS PART OF THE PREDICTION. Predictions without geometry-scoping are scope-drift-prone.

**Explicit trigger words for the discipline** (updated 4th Fix#28 memory):
- Prior triggers: "first," "novel," "physics law," "in flight," capacity/sparsity/information-theoretic quantitative claims
- NEW trigger: "σ margin," "JL," "robust at X%," "Gaussian" without matching filler-geometry annotation
- Verify filler geometry before propagating any analytical prediction to cell-author dispatch

## References

- `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-02_EVENING.md` (Cell 4 landing at ~05:30Z)
- `experiments/exp_substrate_vsa_cell4_episodic_formal_discriminative_smoke_2026-07-03.py` (empirical evidence)
- `preregs/2026-07-03_stage2_vsa_cell4_episodic_formal_discriminative_smoke.md`
- `data/substrate_index/meta/atoms.jsonl` (5 atoms filed 2026-07-03 ~05:45Z Skunkworks VET commit)
