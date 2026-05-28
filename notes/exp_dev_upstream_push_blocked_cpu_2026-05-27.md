# exp_dev upstream push: 3 blocked CPU experiments needing Strategy redesign

**Filed:** 2026-05-27  
**From:** exp_dev sub-agent  
**To:** Strategy (next cycle)

## Summary

Three CPU candidates designed and smoke-tested this cycle were blocked by
INSTRUMENTATION_SUSPECT or fundamental metric issues. All three need
Strategy-level redesign before re-attempt.

---

## (1) mct_k_extended_v1 -- INSTRUMENTATION_SUSPECT

**Script:** experiments/exp_mct_k_extended_v1.py  
**Problem:** `retrieval_accuracy` using `overlap > 0.5` threshold returns acc=1.0 at
ALL K values from K=141 to K=2000 (well above BSC capacity K_c=141).
The "50% overlap" threshold does not distinguish between well-retrieved
(overlap=0.99) and poorly-retrieved (overlap=0.53) patterns. The metric
needs to be replaced with `mean_overlap` (continuous) or `perfect retrieval rate`
(fraction where all N bits match).

**Evidence:** python check at K=2000: acc=0.833 with mean_overlap=0.526. But
K < 2000 gives acc=1.0 regardless of how far above capacity we go.

**Recommendation:** Redesign metric to use `mean_overlap` (continuous value).
Then the decay from ~0.99 at K=141 to ~0.53 at K=2000 may reveal MCT power-law.
NOTE: v242 MIDDLE_BAND conclusion at K=[1..192] used a DIFFERENT metric
(via mode_coupling_theory_substrate_v1). The v242 probe has its own design; this
is about the EXTENDED K version above capacity.

---

## (2) pb2_correlation_length_v1 / pb2_corr_len_bsc_v1 -- metric vacuous

**Scripts:** experiments/exp_pb2_correlation_length_v1.py, exp_pb2_corr_len_bsc_v1.py  
**Problem:** Measuring "correlation length" via argmax-change after single-rank-1
weight edit. At N=1024 with Kerdock codebook (pb2_v1) or BSC random keys (pb2_bsc_v1),
zero argmax changes were observed across all M/N conditions including M=200 (above
BSC alpha_c). 

Root cause: single rank-1 W edit changes W@v response by up to 103 units, but the
stored pattern overlap (N >> noise) overwhelms the perturbation. The edit never
flips a retrieval result because no pattern is near the retrieval boundary.

**What we actually want:** A probe that measures how edits propagate through
the SIMILARITY structure (delta_sim metric: how much do all stored-pattern
similarities shift after one W edit). This is a genuine correlation-length measurement
that doesn't require argmax changes.

**Recommendation:** Redesign PB-2 with `delta_sim = sum_{i != target} |sim(p_i, W_new) - sim(p_i, W_old)|`.
Near capacity (M/N close to alpha_c), delta_sim should diverge as more patterns
are near the retrieval boundary. This is the proper correlation-length observable.

---

## (3) kf2_cpu_v1 -- same Kerdock isolation issue

**Script:** experiments/exp_kf2_cpu_v1.py  
**Problem:** KF-2 Edit-with-Impact-Prediction measures r = correlation between
predicted delta_retention and actual delta_retention after edits. Uses argmax
change as the observable. With Kerdock codebook at N=1024, no argmax changes occur
after edits (same root cause as PB-2). All r=0, delta=0.

**Recommendation:** Same byte-LM redesign as PB-2. The delta_sim metric would
enable KF-2 to measure "how accurately can we predict the similarity-structure
change after an edit?" which is the correct product-relevant question.

---

## Common theme

All three probes need to transition from argmax-change observables to
similarity-shift observables. The argmax-change metric is fundamentally broken
at N=1024 with well-separated stored patterns (Kerdock or BSC at sub-capacity).
The correct metric is `delta_sim` = change in raw similarity scores.

This redesign aligns with the deletion-certificate killer feature: what the
compliance officer needs is not "which pattern is retrieved" but "by how much did
the similarity landscape change." The delta_sim metric is exactly that.
