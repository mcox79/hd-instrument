# PREREG (DRAFT): ARCH-A Drosophila 2x2 ablation PRE-FLIGHT -- expansion+WTA stage vs nonlinear-readout, orthogonalized

**Author:** Exp-Dev (Prover)  **Date:** 2026-06-18  **Status:** DRAFT (Anchor 1; laptop-CPU pre-flight; Director handoff exp_dev_handoff_research_ARCH_A_Drosophila_2x_drill).
**Source:** research 2x-drill note (research_2x_drill_ARCH_A_Drosophila_MIDDLE_BAND...); PRED-1/PRED-2 are pre-registered FLOORS (I may TIGHTEN not LOOSEN).
**Trust tier:** the hypothesis is T2/T3 (research, can be wrong); only a cert-grade HARD-PASS promotes it.

## Question (the reframe)
The prior ARCH-A Drosophila MIDDLE_BAND closure was DESIGN-INCOMPLETE: it conflated (axis-1) presence of a fly-MB-style
random-projection + top-k WTA expansion STAGE with (axis-2) linear-vs-nonlinear READOUT. Fly-MB literature (Dasgupta-Tosh
2020; Litwin-Kumar 2017; Dasgupta-Stevens-Navlakha 2017) puts the nonlinearity UPSTREAM at the WTA, with a LINEAR downstream
readout. So "linear readout is the ceiling" (true for ARCH-B/C1 on the canonical substrate) may NOT transfer. This 2x2
orthogonalizes the axes to decide: does Drosophila-class sparse-pattern capability need its OWN upstream expansion+WTA
stage, or is the entmax readout fix (C1) alone sufficient?

## Design (2x2; sparse-pattern associative-memory recall@1)
HELD FIXED across all 4 cells (measured-bounds rule): N=512, M=200, K=20 (K-sparse patterns), noise (query = stored pattern
with bit-corruption), SAME seed family [7,17,23] across cells, modern-Hopfield one-step retrieval, COSINE-normalized scores,
a SINGLE beta tuned ONCE on A2 then FROZEN across all cells (no per-cell beta gaming -- the C1 frozen-beta no-Goodhart discipline).
VARIED: axis-1 expansion+WTA in {off, on}; axis-2 readout in {linear, entmax(alpha=1.5)}.
```
                       | linear readout | entmax readout
WITHOUT expansion+WTA  |  A1 (baseline) | A2  (= C1 replication at small N)
WITH    expansion+WTA  |  A3            | A4
```
- Patterns: M K-sparse bipolar patterns in N dims. Query = p_true with noise_frac bit-corruption (drop active + add spurious).
- Baseline retrieval: scores s = cosine(q, P); readout f -> weights w; reconstruction r = sum_i w_i p_i; recall@1 = (argmax_i cosine(r, p_i) == true).
  - LINEAR readout: w = relu(s) normalized (linear, non-exponential, non-sparsifying -> keeps crosstalk).
  - ENTMAX readout: w = entmax_alpha(beta*s), alpha=1.5 (sparse -> rejects crosstalk).
- Expansion+WTA (fly-MB): fixed random projection R (N_exp = E_FACTOR*N, E_FACTOR pre-set), e = R@x, WTA keep top WTA_FRAC active
  (sparse high-dim code), then the SAME retrieval (scores/readout/recall) in the expanded space. Decorrelation -> lower crosstalk.
- recall@1 = fraction of queries whose top-1 retrieved INDEX is the true stored pattern (over the seed family).

## Pre-registered bands (PRED-1 + PRED-2 from the drill; I may tighten)
```
PRED-1 (expansion+WTA IS the Drosophila lever):
  recall@1 targets: A1 0.55+/-0.05 | A2 0.72+/-0.05 (C1 replication) | A3 >=0.70+/-0.05 | A4 >=0.78+/-0.05
  HARD-PASS: A3 >> A1 (expansion closes >=60% of the A1->best gap) AND A4 >= A3 (entmax-on-expansion additive/neutral, not inferior).
  HARD-FAIL: A3 <= A1 + 0.05 (expansion adds nothing) -> Drosophila-class question CLOSED as a substrate addition; entmax readout fix was sufficient.
  MIDDLE_BAND: A3 in (A1+0.05, A2) -- expansion helps but readout helps more; expansion = marginal-not-load-bearing optional layer.
PRED-2 (linear readout on KC sparse code is sufficient; Dasgupta-Tosh):
  HARD-PASS: |A4 - A3| < 0.05 (entmax-on-top-of-expansion gives ~no additional lift -> WTA IS the nonlinearity).
  HARD-FAIL: A4 >> A3 + 0.10 (entmax still substantially helps even with expansion -> Dasgupta-Tosh regime not satisfied here).
```
EFFECT-SIZE floor: deltas must exceed >=0.05 (the drill's threshold) to count as a real lift, not seed noise (report per-seed spread).

## Discipline / guards
- NO-GOODHART: beta tuned ONCE on A2, FROZEN across all 4 cells; do NOT tune per-cell to hit the predicted table. The predictions
  are interpretation bands, NOT targets -- measure faithfully and report what happens (HARD-FAIL is an acceptable, product-positive outcome).
- COSINE-normalized scores so beta is comparable across baseline/expanded regimes (avoids the self-dominance/raw-dot scale trap).
- SYMMETRIC read (NEGATIVITY-BIAS rule): report both directions -- expansion may help (PRED-1 PASS) OR be redundant (HARD-FAIL); both are honest product stories.
- measured-bounds: the result is the envelope at N=512/M=200/K=20/E_FACTOR/WTA_FRAC/noise of THIS method, NOT fundamental.
- DESIGN-COMPLETE check (the #93 lesson): each axis varies ONE mechanism with the other held fixed -> the 2x2 IS orthogonal (the fix for the prior design-incomplete closure).

## Compute + cert-chain
- Pre-flight = laptop-CPU super-fast (N=512; no large NxN at scale) per USER compute policy -> runs locally, no GPU, no remote dispatch.
- Smoke (tiny: N=128, M=40, 1 seed) verifies wiring + the 2x2 harness + recall computation; then the pre-flight FULL (N=512, 3 seeds).
- Verdict against the pre-registered bands -> route to Skunkworks VERDICT-VET (honest-negative discipline) + Director.
- Anchor 2 (full-mode N=4096) is GATED on PRED-1 HARD-PASS and requires committed prereg + the BLOCKING remote-dispatch checklist (NOT this pre-flight).
- Structured provenance fields (run_mode/branch_path/metrics_source/run_started_utc/cell_commit) via the shared helper; --self-test writes no metrics.

## Closure provenance (per handoff autonomy)
- If pre-flight HARD-FAILS PRED-1 (A3<=A1+0.05): the prior ARCH-A MIDDLE_BAND closure is RATIFIED (honest-acceptance; entmax readout fix sufficient).
- If pre-flight HARD-PASSES PRED-1: ARCH-A closure preserved as cert-grade-but-DESIGN-INCOMPLETE; new finding (expansion+WTA stage) lands as a SEPARATE cap_map row (NOT a retraction).

-- Exp-Dev (Prover) [DRAFT]

---
## ADDENDUM (2026-06-18): OPTION B -- expansion-axis NOISE-ROBUSTNESS metric (Skunkworks VERDICT-VET: capacity-curve disfavors binary codes; test the fly-MB mechanism on ITS claimed benefit = noise-robust separation). B is FINAL for the expansion axis (pre-commit; no third metric).

READOUT axis: SETTLED -- capacity-curve VET PASS (A1 linear M*=48.5 vs A2 entmax M*>2048 censored = C1 REPLICATED, ">=42x censored" lower bound). Cert-grade-eligible positive.

EXPANSION axis (option B), PRE-REGISTERED + FROZEN before the official run:
- FIXED LOAD M_fixed = 30 (N=256); FAIR-START precondition: both raw-linear AND expanded-linear must be >= 0.95 retrieval accuracy at noise=0.0 (verified in probe; else NON_TEST -> lower load).
- NOISE GRID = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5] (bit-flip fraction); SEEDS >= 3.
- METRIC: re-nearest retrieval accuracy at M_fixed per noise; noise_at_half = the noise level where accuracy crosses 0.5 (higher = MORE noise-robust). Compare raw-linear (A1) vs expanded-linear (A3) -- the canonical fly-MB claim (WTA is the nonlinearity, readout linear).
- HARD-PASS: expanded-linear noise_at_half > raw-linear noise_at_half + 0.03 (the fly-MB expansion adds noise-robustness) -> ARCH-A capability recovers WITH the upstream WTA stage (scoped to noise-robustness; #93).
- HARD-FAIL: expanded-linear noise_at_half <= raw-linear noise_at_half (no noise-robustness advantage) -> RE-AFFIRMS the ARCH-A MIDDLE_BAND closure; entmax readout fix sufficient.
- MIDDLE: |delta| < 0.03 (essentially equal).
- NON_TEST: fair-start fails (expanded < 0.95 at noise=0 at M_fixed).
- B is FINAL: whatever B returns disposition the expansion axis; no third metric (no-Goodhart switch-once guarantee).
