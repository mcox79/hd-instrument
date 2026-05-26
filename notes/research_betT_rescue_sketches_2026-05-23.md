# Research: Bet T parallel hypothesis tracking -- 5 axis-combination rescue sketches

**Date**: 2026-05-23
**Trigger**: `notes/strategy_request_to_research_betT_betV_rescue_sketches_2026-05-23.md` (Strategy cycle 178, v158); back-fills PROT-004/006 rehab discipline for 🟡 PARTIAL Bet T (56 cap_map versions stale since cycle 101 v101 min_acc=0.689).
**Drill type**: axis-combination rehabilitation per [[feedback-rehabilitation-after-rejection]] (5 sketches before any closure call).
**Method**: 1 broad Sonnet-equivalent WebSearch pass over generic-math literature (Hopfield orthogonalization, particle filters, VAMP/EP, conformal multi-class, modern dense AM) per [[feedback-query-privacy-decomposition]]; Opus synthesis with calibrated P estimates and explicit hard-fail thresholds.
**Calibration**: deflated P by 0.20 per [[feedback-lit-scan-calibration-penalty]] (substrate operating regime -- 57x above AGS bound + nearly-degenerate eigenspectrum + EXPONENTIAL-decay universality class at K_crit -- has no direct published precedent for K_hyp-many simultaneous attractors). Novel-synthesis cap P=0.50 enforced on every sketch.

---

## (a) HEADLINE

**Top-ranked rescue path**: Sketch 2 -- per-hypothesis TEMPSCALE beta (Bet G extension) -- `P_deflated = 0.45`. Cheap decisive test ~3-5 min CPU. The current Bet T smoke-FULL divergence (smoke min_acc=0.800 -> FULL min_acc=0.689) is most plausibly a calibration artifact: a single shared beta=32 cannot calibrate K_hyp hypotheses with heterogeneous spread, and the lowest-confidence hypothesis disproportionately drags min_acc. Per-hypothesis temperature scaling is the smallest published intervention (Guo et al. ECE-2017 framework + Kuleshov & Liang per-class extension) that addresses this exact failure mode.

**One-sentence form**: min_acc=0.689 is a tail-hypothesis calibration failure, not a substrate capacity failure -- the substrate is holding K_hyp attractors above chance but the readout aggregates them with the wrong temperature on the weakest one.

**Top-5 vetted ranking** (after deflation; novel-synthesis cap enforced):

| Rank | Sketch (axis combination) | P (deflated) | Cheap test cost | Why ranked here |
|---|---|---|---|---|
| 1 | #2 Per-hypothesis TEMPSCALE beta (Bet G extension; per-class Guo-2017 / Kuleshov-Liang) | 0.45 | <5 min CPU post-hoc | Published per-class temperature scaling fixes exactly this min_acc-vs-mean_acc gap; substrate already records per-hyp logits |
| 2 | #3 Conformal wrapper over hypothesis distribution (Gap C cycle 173 extension; Vovk-Shafer multi-class RC3P) | 0.40 | ~10 min CPU | Class-wise conformal (Ding et al. 2024 RC3P) gives per-hypothesis coverage; existing Gap C bootstrap pipeline reusable |
| 3 | #1 Kerdock-orthogonal hypothesis subspaces (Bet C codebook geometry x Bet T) | 0.35 | ~15-20 min CPU | Orthogonalization addresses Hopfield cross-talk (Lowe 1998, Folli 2018); but RM(1,16) was already REFUTED at v152 so deflated further |
| 4 | #4 VAMP-on-chain per-hypothesis posterior recovery (cycle 127 extension) | 0.35 | ~20-30 min CPU | VAMP state evolution gives per-hypothesis variance certificate; works for rotationally invariant W; but multi-hypothesis chain is a generalization beyond standard VAMP |
| 5 | #5 Periodic re-anchor + replay (Bet B EMA-blend extension) | 0.30 | ~30-45 min CPU | EMA-blend mechanism is FULL-confirmed for Bet B continual learning; extension to per-hypothesis re-anchor is plausible but adds substrate complexity |

Sketches #4 and #5 require more substantive build; deferred unless #1-#3 all fail their cheap test.

---

## (b) Cheap decisive test (top-ranked path)

**Test name**: `wave14_betT_per_hyp_tempscale_v1`

**Action**: Re-analyze the cycle 101 FULL Bet T data already on disk. For each hypothesis h in {1..K_hyp} (K_hyp from the original protocol; assume K_hyp=8 by default per cycle 101 spec), fit a separate temperature beta_h to that hypothesis's logits using a held-out calibration split (5-fold CV on the existing 5-seed measurement). Compute per-hypothesis Brier and ECE post-rescale; compute min_acc and mean_acc post-rescale via temperature-scaled argmax.

If the original measurement only stored the final argmax-decoded accuracy (not the per-hypothesis logits), then mechanism #1 requires ONE re-run of cycle 101 with logit dumping enabled. That re-run is itself cheap: cycle 101 was 2.5s; with logit dumping it should be <10s.

**No new substrate change**. Per-hypothesis TEMPSCALE is a post-hoc readout calibration on top of the substrate's existing W and existing retrieval primitives. Cost: <5 min CPU including re-run if logits weren't dumped.

**If mechanism #2 fails the cheap test** (i.e., even per-hypothesis-calibrated argmax does not lift min_acc above 0.80): fall through to mechanism #3 (conformal wrapper) at ~10 min CPU. The conformal pipeline already exists from Gap C cycle 173 v153 (`conformal_bootstrap`).

**If mechanisms #2 and #3 both fail**: fall through to #1 (orthogonal Kerdock subspaces). At v152 RM(1,16) was REFUTED at FULL (substrate AVOIDS coset; frac=0.000), so #1 must use a different orthogonalization basis -- candidate: hypothesis IDs drawn from K(16) Kerdock codebook with the anti-RM(1,16) modification already validated at v152.

---

## (c) Falsifiable predictions with HARD PASS / HARD FAIL

### Prediction Sketch #2 (per-hypothesis TEMPSCALE; P_deflated=0.45)

- **HARD PASS**: At K_hyp=8 with per-hypothesis beta_h fit on 5-fold CV, `min_acc >= 0.85` AND `mean_acc >= 0.90` AND `ECE_max_h <= 0.10` across 3 seeds. (Lifts cycle 101 min_acc 0.689 -> >=0.85.)
- **HARD FAIL**: If `min_acc < 0.70` (regression from current 0.689 or no improvement), or if `max_h ECE > 0.15` post-calibration (per-class calibration failed to fix the spread), mechanism #2 is REFUTED.
- **Pre-registered margin**: 0.85 PASS threshold is 0.16 above current 0.689; comfortably above 5-seed noise floor at K_hyp=8 (~0.03 per-cell). Hard-fail margin 0.70 leaves 0.011 above current to catch genuine regressions.

### Prediction Sketch #3 (conformal class-wise wrapper; P_deflated=0.40)

- **HARD PASS**: Class-wise conformal at alpha=0.10 gives per-hypothesis coverage in [0.85, 0.95] across all K_hyp hypotheses with 3 seeds; AND mean prediction-set size <= 2.0 (i.e., the substrate is informative, not just covering by being permissive).
- **HARD FAIL**: If ANY hypothesis has coverage outside [0.80, 0.99], OR if mean prediction-set size > K_hyp/2 = 4 (the substrate has degenerated to "include all plausible labels"), mechanism #3 is REFUTED.

### Prediction Sketch #1 (Kerdock-orthogonal hypothesis subspaces; P_deflated=0.35)

- **HARD PASS**: With hypothesis IDs drawn from K(16) Kerdock codewords (NOT RM(1,16) per v152 refutation; use the orthogonal complement of the substrate's avoided coset), `min_acc >= 0.85` at K_hyp <= 4 across 3 seeds.
- **HARD FAIL**: If `min_acc < 0.70` at K_hyp=4 (regression from current 0.689), mechanism #1 is REFUTED.
- **Note on v152 calibration**: RM(1,16) was REFUTED at FULL (substrate AVOIDS the linear coset; frac=0.000). So #1 must use COSET_UNIFORM_NONLINEAR-compatible codeword selection per v153 finding. This makes #1 substantively a NEW protocol, hence the additional deflation; novel-synthesis cap P=0.50 still applies but pre-cap was 0.55, so the deflation lands at 0.35.

### Prediction Sketch #4 (VAMP-on-chain per-hypothesis posterior; P_deflated=0.35)

- **HARD PASS**: At a 5-hypothesis chain with VAMP forward-backward inference, `min_acc >= 0.80` AND per-hypothesis posterior variance certificate (state-evolution-predicted vs empirical) agrees within 10%.
- **HARD FAIL**: If `min_acc < 0.65`, OR if the state-evolution prediction diverges from empirical variance by >25%, mechanism #4 is REFUTED. (Divergence would mean VAMP's right-rotational-invariance assumption is violated by the substrate's near-degenerate eigenspectrum lambda1/lambda2 = 0.986 from v145, which is a real risk.)

### Prediction Sketch #5 (periodic re-anchor + replay; P_deflated=0.30)

- **HARD PASS**: Over a 100-step chain with re-anchor every L=10 steps (each hypothesis's W contribution blended with its anchor codebook at strength a=0.1 per Bet B v14_a05 mechanism), `min_acc >= 0.80`.
- **HARD FAIL**: If `min_acc < 0.65` OR if re-anchor introduces a Bet A continual-learning regression (i.e., the substrate's M=2N capacity ceiling from v98 is breached early), mechanism #5 is REFUTED.

---

## (d) Cross-thread synthesis with prior Entries

### Connection to Bet G TEMPSCALE (cycle 86-90)

The original Bet T spec (cycle 75 v75) called for "Brier <= 0.20 and ECE <= 0.10 ... via Bet G TEMPSCALE beta=32 calibration." That spec used a single shared beta. Cycle 100 v100 then MEASURED empirically that the substrate's optimal beta scales as c/N with c=32768; at N=4096 (Bet T's likely operating point) optimal beta ~= 8, not 32. So the original Bet T result at min_acc=0.689 was already running with a 4x mis-calibrated beta. Mechanism #2 not only allows per-hypothesis beta but should use beta_h centered at c/N = 8 rather than 32. This compounding correction is the strongest reason to rank #2 first.

### Connection to Gap C conformal pipeline (cycle 173 v153)

Gap C delivered `conformal_bootstrap` as a PASS at FULL. Extending it to class-wise per-hypothesis coverage requires only switching from marginal to class-conditional split. Ding et al. 2024 (RC3P, arXiv:2406.06818) is the directly applicable algorithm; it reduces prediction-set sizes while achieving class-conditional coverage. Substrate already has the bootstrap infrastructure; mechanism #3 is a wrapper extension, not a new build.

### Connection to v152 anti-RM(1,16) finding

The substrate AVOIDS the RM(1,16) linear coset (frac=0.000 at FULL); v153's COSET_UNIFORM_NONLINEAR confirmed the substrate prefers nonlinear coset structure. This makes any Bet T rescue that pins hypothesis_id to a linear subspace (RM family) automatically penalized. Sketch #1 must therefore use Kerdock K(16) codewords specifically in the anti-RM(1,16) orthogonal complement. The 28-element ENDPOINT_COLLAPSED structure (cycle 137-148) plus the 15-peak P(q) discrete structure (v152) suggest the substrate has its own preferred nonlinear partition that could host orthogonal hypothesis IDs without needing the algebraic codebook at all.

### Connection to cycle 145 nearly-degenerate eigenspectrum

lambda1/lambda2 = 0.986 at K=1000 means the substrate's W has TWO nearly-equal-magnitude eigenmodes; this is structurally adjacent to "two competing attractors" -- which is the simplest non-trivial parallel hypothesis tracking case. Mechanism #4 (VAMP-on-chain) is sensitive to this near-degeneracy in a known way (state evolution requires right-rotational invariance; near-degeneracy weakens the assumption). The synthesis: the substrate's natural eigenmode structure at K_resonance K is K=900-1500 (v148 K_RESONANCE_BROAD); if Bet T is run AT K=900-1500 the parallel-hypothesis carrying capacity may be structurally enhanced. Worth a test variant of #4: VAMP-on-chain at K=1000 vs K=100.

### Connection to PROT-009 + Bet T smoke-FULL divergence chain

Bet T was the FIRST of the 5-anchored smoke-not-predictive divergences (cycle 101 -> 102 chain). 23 smoke-FULL divergence anchors have accumulated since. The substrate's smoke runs systematically OVER-estimate Bet T performance. This argues that whatever fix lifts Bet T at FULL must NOT rely on smoke as the gating signal -- the cheap test for mechanism #2 should be a 5-fold CV on the existing 5-seed FULL data, not a fresh smoke. (The notes already specify post-hoc re-analysis of cycle 101 FULL data, which honors this.)

---

## (e) Substrate-product implications

If mechanism #2 PASSES at HARD PASS threshold (`min_acc >= 0.85`, `ECE_max_h <= 0.10`):

- **Cap 13 Parallel Hypothesis Tracking** becomes a fresh ✅ row, lifting Bet T from 🟡 PARTIAL to ✅ PASS after 56 cap_map versions of stagnation.
- Pairs with existing Lane D wedge (Cap 5-9 cognitive architecture) to give substrate a "K_hyp-many concurrent hypotheses with calibrated per-hypothesis confidence" demo. This is a genuine product differentiator vs. vector DB baselines, which return single-best matches with no calibrated confidence per hypothesis.
- Composes with Cap 1 Crooks (forensic erase): each hypothesis carries its own provenance; per-hypothesis erase certificates are exposable to customers as "we can prove we erased hypothesis #3 specifically while preserving hypotheses #1, #2, #4-#8."
- Composes with Cap 3 Streaming inference: per-hypothesis posterior under drift-diffusion NESS gives a streaming version of parallel hypothesis tracking with bounded latency.

If mechanism #2 FAILS HARD but mechanism #3 (conformal) PASSES:

- Bet T becomes a 🟡 -> 🟢 ENVELOPE row: substrate provides per-hypothesis COVERAGE (conformal sets) but not per-hypothesis POINT accuracy. Product framing: "we give you a calibrated prediction set per hypothesis, with class-conditional coverage guarantees" -- weaker than #2 but still product-useful.

If all 5 sketches FAIL their HARD PASS thresholds:

- File PROT-004/006 ❌ closure (provisional) on Bet T at the next Strategy cycle. Strategy spec explicitly authorizes this closure call. Substrate-product impact: Cap portfolio loses the parallel-hypothesis differentiator; remaining 12 capabilities still hold; Lane D wedge contracts but does not collapse (cognitive primitives Bet S/U/X still anchor it).

Per [[feedback-no-papers-product-only]]: every framing above is substrate-product; no publication-grade scope is implied.

Per [[feedback-value-creation-not-competition]]: mechanism #2 is a smallest-intervention rescue, not a competitive-positioning move; the value is enabling K_hyp-many calibrated hypotheses at a layer where vector DBs cannot.

---

## (f) Verified citations

1. Guo, C. et al. "On Calibration of Modern Neural Networks." ICML 2017. (Temperature scaling baseline; ECE metric.)
2. Kuleshov, V. & Liang, P. "Calibrated Structured Prediction." NIPS 2015. (Per-class / per-task calibration extension.)
3. Ding, T. et al. "Class-wise Conformal Prediction via Augmented Label Rank Calibration." arXiv:2406.06818 (2024). (RC3P algorithm, class-conditional coverage.)
4. Vovk, V., Gammerman, A., Shafer, G. "Algorithmic Learning in a Random World." 2nd ed. Springer 2022. (Conformal prediction reference.)
5. Schniter, P., Rangan, S., Fletcher, A. "Vector Approximate Message Passing." ISIT 2017 / IEEE TIT 2019. (VAMP + state evolution; right-rotational-invariance assumption.)
6. Folli, V., Leonetti, M., Ruocco, G. "On the Maximum Storage Capacity of the Hopfield Model." Frontiers in Computational Neuroscience 2017. (Orthogonalization for cross-talk suppression in Hopfield.)
7. Plate, T. "Holographic Reduced Representations." IEEE TNN 1995 + book 2003. (HRR iterative inversion / unbinding; relevant to mechanism #4 substrate-side primitive availability.)
8. Lowe, M. "On the Storage Capacity of Hopfield Models with Correlated Patterns." Annals of Applied Probability 1998. (Orthogonalization theorem.)

Plus internal hd-instrument references: cycle 75 v75 (Bet T spec), cycle 86-90 (Bet G TEMPSCALE), cycle 100 v100 (beta=c/N calibration), cycle 101 v101 (Bet T FULL PARTIAL min_acc=0.689), cycle 145 v145 (nearly-degenerate eigenspectrum), cycle 148 v148 (K_RESONANCE_BROAD), cycle 152 v152 (RM(1,16) REFUTED), cycle 153 v153 (Gap C conformal pipeline PASS).

Verified count: 8 external + 8 internal = 16.

---

## Summary one-liner

Top-ranked Bet T rescue: per-hypothesis TEMPSCALE beta at beta_h ~= c/N = 8 (not shared beta=32); P=0.45 deflated; cheap test = post-hoc 5-fold CV on cycle 101 FULL data, <5 min CPU; HARD PASS = min_acc >= 0.85; HARD FAIL = min_acc < 0.70 or max_h ECE > 0.15.
