# 5x-Drill (2 of 3): Regime-Switch Calibration Recovery — Dense Readout Calibrated to Teacher Cosine Without Sacrificing Ranking

Date: 2026-07-04
Angle: lit + best recipe. LIVE shot 2 of 2 on regime-switch viability.
Prior-work check (substrate KB, v2 flags): DONE — see "Prior arc work" below.

---

## HEADLINE

Relational distillation gives good RANKING (ret_agree10=0.65) and bad CALIBRATION (calib_err=0.37, hi80_cos=0.48) because relational/RKD losses are **invariant to the absolute scale of the student's cosine map by construction** — they transfer pairwise *relations* (distance-ratio, angle) and throw away the absolute magnitude. Ranking and calibration are **decoupled, not in tension**: ranking is the *order* of scores; calibration is a *monotone reparameterization* of the score. Therefore a monotone post-hoc recalibration (isotonic regression, or a 2-param Platt/temperature affine) can slash calib_err **without touching ranking at all** (order-preserving => ret_agree10 exactly unchanged). The training-time root-cause fix is to add a small-weight **absolute pairwise cosine-anchor term** that restores the magnitude the relational loss discarded. Best recipe = anchor term (root cause) + isotonic post-hoc (polish). Regime-switch (dense query / sparse-compressed store) is **not a smell** — it is textbook Asymmetric Distance Computation (ADC) and hybrid dense-sparse IR (SPLADE, BGE-M3, ColBERT-PQ, Matryoshka), used in every production ANN system.

---

## Prior arc work on this concept (substrate KB concept-query, MANDATORY pre-write)

Ran `bash tools/substrate_query.sh` on two concept vectors. Top hits + overlap:
- `notes/research_drill_cell3_distillation_alternatives_2x_2026-06-07.md` (cosine 0.41) — **HIGHLY relevant, complementary.** Established the *inverse* failure: MSE distillation preserves MAGNITUDE but tanks DIRECTION/cosine (val_cos 0.79 vs 0.95 target), because L2 rewards magnitude-matching not angle. Fix ladder: cosine loss / InfoNCE factor magnitude OUT. **This drill is the mirror image**: relational loss factors magnitude out (good direction/rank) and we need to put a *calibrated* magnitude back — without the MSE trap of distorting direction.
- `notes/research_to_exp_dev_NEGATIVE_RESCUES_2026-06-08.md` (cosine 0.33) — RESC-CONF-1 "temperature scaling on cosine scores" + RESC-CONF-2 "rank-based calibration" already filed as rescue anchors for a *conformal-coverage* miss. Same tool family (monotone post-hoc score transform); different target metric. Precedent that temperature/rank recalibration is in-repertoire.
- `notes/research_5x_drill_N_scaling_analytical_formula_2026-07-01.md` (cosine 0.44) — "Calibration deflation" refers to the P-deflation discipline, not embedding calibration. No mechanism overlap.

**Prior arc work on THIS exact concept (calibrating a dense readout's absolute cosine to teacher while preserving rank): NONE.** The 06-07 note covered the opposite direction (recovering direction from magnitude-matching); nothing covers recovering calibrated magnitude from relation-matching. Novel-for-arc, but built on textbook calibration methods (low novelty penalty).

---

## Diagnosis: why relational distillation overshoots magnitude

Relational Knowledge Distillation (Park et al. 2019, RKD) transfers **distance-wise** (ratio of pairwise distances) and **angle-wise** (angle formed by triplets) structure between examples. Both potentials are **invariant to a global scale (and rotation) of the student embedding space by construction** — that invariance is the *feature* that makes RKD robust to student/teacher dimension mismatch. The cost is that nothing in the loss pins the student's *absolute* cosine to the teacher's absolute cosine. The monotone score->cosine curve is left free and drifts.

Reading the numbers: ret_agree10=0.65 (order is decent) but hi80_cos=0.48 (genuinely-similar pairs read only 0.48 vs teacher ~0.83) while the aggregate "overshoots." Fingerprint = **dynamic-range collapse**: the student's angular spread is too small, so the bulk/random pairs are *inflated* (everything looks moderately similar => overshoot on the mass) while the truly-similar top pairs are *compressed downward* (hi80 undershoots). calib_err=0.37 is the aggregate of both. This is exactly what an under-spread relational-only student looks like: correct order, squashed scale.

---

## The lever menu (and why the winner wins)

1. **Absolute pairwise cosine-anchor term (train-time root cause).** Add `L_abs = mean_ij (cos_s(i,j) - cos_t(i,j))^2` over sampled pairs to the relational loss, weight `lambda ~= 0.1-0.3` of the relational term. This directly pins student cosine magnitude to teacher's while RKD keeps the fine local ranking. Restores the dynamic range at the representation level (fixes hi80_cos, not just the readout). **Risk: over-weighting this degenerates toward the MSE trap (06-07 note) — pure magnitude-matching distorts direction and would cost ranking. Keep lambda small; it is a *scale anchor*, not the primary objective.**
2. **Post-hoc monotone recalibration (readout polish, near-free, cannot hurt rank).** Fit a monotone map `g` on a held-out calibration split so `cos_t ~= g(cos_s)`:
   - **Isotonic regression** — non-parametric monotone; handles BOTH the bulk-overshoot and the high-end-undershoot in one fitted curve; most flexible; slight overfit risk on tiny calib sets.
   - **Platt / 2-param affine or temperature** (`g(s) = a*s + b`, or sharpening `sign(s)*|s|^gamma`) — 2 params, robust on small sets, re-expands a compressed range when `a>1` / `gamma>1`.
   Because `g` is monotone increasing, **argsort is invariant => ret_agree10 is bit-for-bit unchanged.** This is the classic decoupling (Guo et al. 2017 temperature scaling preserves argmax/accuracy while fixing ECE). A Jan-2026 result (arXiv 2601.16907) does exactly this for cosine: isotonic calibration to a reference achieves near-perfect calibration while *preserving rank correlation and local stability*.
3. **Scale-matching term (moment matching).** Match the mean/variance of the student cosine distribution to the teacher's (a cheaper, coarser version of #1). Weaker than the pairwise anchor; use only if pair sampling is expensive.

**Post-hoc alone is not guaranteed sufficient:** a monotone map can only fix miscalibration that is *consistent with the student's order*. Where the order is wrong (the ~0.35 of top-10 the student misses), residual `|cos_s - cos_t|` cannot be removed by any `g`. So the *floor* on post-hoc calib_err is set by ranking imperfection. That is why the anchor term (which improves the representation's order AND scale at the high-sim end) is the root-cause partner, and why calib_err~0.01 (very tight) likely needs both, not post-hoc alone.

---

## SINGLE BEST CONCRETE RECIPE

**Keep the relational/RKD loss for ranking. Add an absolute pairwise cosine-anchor term at lambda~=0.2 to restore magnitude, then fit an isotonic (fallback: 2-param Platt affine) monotone recalibration on a held-out split as an order-preserving readout.**

Decisive pre-flight diagnostic (minutes, do FIRST): on the *current* overshooting checkpoint, fit isotonic `g` on a held-out split and measure residual calib_err.
- If residual calib_err collapses (e.g. -> ~0.05) with ret_agree10 unchanged at 0.65 => the miscalibration was mostly global scale; post-hoc alone nearly ships it; the anchor term is polish.
- If residual calib_err floors high (>~0.15) => ranking imperfection is the binding constraint; the anchor term must carry the load (retrain with lambda~=0.2), and expect ret_agree10 to move (target: keep >=0.6).
This single cheap test tells you which regime you are in and how hard the retrain must work — run it before spending a GPU cell.

---

## Can ranking (0.65) and calibration be JOINTLY optimized, or do they trade off? -> YES, they coexist

They are **decoupled objectives on the same score**: ranking = the *order*; calibration = the *monotone function* applied to the order. A monotone post-hoc transform changes calibration while leaving order (and thus every order-based construction: kNN, top-k, threshold graphs, ret_agree10) exactly invariant. So there is **no fundamental trade-off**. The only tension is a *weak, avoidable* one at the representation level: if you force absolute-magnitude matching too hard (pure MSE / large-lambda anchor), you distort direction and lose ranking (the 06-07 MSE failure). At moderate anchor weight + monotone post-hoc, both targets are reachable together. Answer: **YES.**

---

## Is regime-switch (dense query / sparse-compressed store) a legitimate architecture or a smell? -> LEGITIMATE

Asymmetric-encoder / asymmetric-distance retrieval is **industry-standard, not a smell**:
- **Asymmetric Distance Computation (ADC)** — the canonical PQ precedent (Jegou et al. 2011): the *query stays full-precision/dense*, the *database is stored as compressed quantized codes*, distance is computed asymmetrically via lookup tables. Regime-switch is ADC generalized. OpenSearch ships ADC for binary quantization (2024-25) precisely to boost recall of on-disk compressed indexes queried by full-precision vectors.
- **Hybrid dense+sparse IR**: SPLADE (sparse lexical store) + dense; **BGE-M3** emits dense + sparse-lexical + multi-vector from ONE encoder and lets the caller switch per use-case — direct validation of "one substrate, multiple regimes." ColBERT stores compressed per-token vectors (PQ/residual) and reranks; two-stage retrieve-then-rerank (compressed IVFPQ recall, dense rerank) is universal in FAISS/ScaNN.
- **Matryoshka (MRL)**: one model, truncation regimes selected per cost/accuracy — "switch the regime per query" is the design intent.

Mapping to us: dense-on-demand for RETRIEVAL + 2% sparse code for STORAGE/ALGEBRA is a coherent instance of the same pattern. **The one smell-check** (the condition that separates legit from smell): the two regimes must be **derivable from one consistent underlying representation** so the sparse store and dense readout agree on geometry. If the sparse code is a lossy but faithful projection of the dense readout (or both are views of one calibrated space), it is legit and battle-tested. If they are independently trained and can *disagree on ordering*, that is the smell. Our path (both are readouts of one annealed encoder) is on the legit side — provided the dense readout is calibrated (this drill's job) so the two views' geometries reconcile.

---

## P assessment (deflated)

- P_theoretical ~0.85: monotone post-hoc **provably** preserves ranking and fixes global-scale miscalibration; anchor term restores dynamic range. Mechanism is textbook (Guo 2017; RKD 2019; arXiv 2601.16907 does the cosine case in Jan 2026).
- P_empirical ~0.62: risk is the *tightness of the joint gate*, esp. calib_err~0.01 (aggressive) — that floor is bounded by ranking imperfection (ret_agree10=0.65 is not near-perfect), which post-hoc cannot cross and the anchor term only partly closes. Reaching a *shippable* joint pass (hi80_cos near ~0.83, calib_err low enough to pass the joint gate HONESTLY, ret>=0.6) is more likely than the ~0.01 aspiration.
- Deflation -0.20 (finite calib split; tight joint target; single-encoder joint pass not yet demonstrated on this checkpoint). Novel-synthesis cap (0.50) does **not** bind — this is established-method application, not novel synthesis.
- **P_deflated = 0.55** that this recipe recovers calibration to a shippable regime-switch while holding ret>=0.6.

---

## Handoff to the in-flight exp_dev cell

1. Run the isotonic-residual diagnostic on the CURRENT overshooting checkpoint FIRST (minutes) — tells you post-hoc-sufficient vs anchor-required before spending a retrain.
2. If retrain: RKD + absolute cosine-anchor at lambda~=0.2; sweep lambda in {0.1, 0.2, 0.3}; watch ret_agree10 does not drop below 0.6 (anchor-too-strong = MSE trap).
3. Always append isotonic (fallback Platt affine) post-hoc fit on a held-out split; report ret_agree10 BEFORE and AFTER post-hoc (must be identical — if not, the map is not monotone / has a bug).
4. Report calib_err and hi80_cos post-recalibration; the joint gate must pass on RAW-then-recalibrated, and the false-pass overshoot check must be re-run so recalibration is not itself gaming the gate.

## Cross-references
- notes/research_drill_cell3_distillation_alternatives_2x_2026-06-07.md (inverse failure: direction-from-magnitude)
- notes/research_to_exp_dev_NEGATIVE_RESCUES_2026-06-08.md (RESC-CONF-1/2 temperature+rank recal precedent)
- External: Park et al. 2019 RKD; Guo et al. 2017 temperature scaling; Jegou et al. 2011 PQ/ADC; arXiv 2601.16907 (Jan 2026) calibrated cosine via isotonic; BGE-M3; OpenSearch ADC binary quantization.
