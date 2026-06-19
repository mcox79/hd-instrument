# Pre-registration: wave14_betT_conformal_v1

**Date**: 2026-05-23
**Queue**: remote_cpu_queue (pure CPU; ~10 min; reads no remote data)
**Axis probed**: Bet T (parallel hypothesis tracking) — Rescue #3 class-wise conformal wrapper
**Trigger**: wave14_betT_per_hyp_tempscale_v1 FULL = BET_T_TEMPSCALE_KILL (best_min_acc=0.344 < 0.70); Research rescue sketch #3 ranked #2 after TEMPSCALE KILL per notes/research_betT_rescue_sketches_2026-05-23.md
**Script**: experiments/exp_wave14_betT_conformal_v1.py
**Peak memory**: ~20 MB CPU (codebooks at N=4096 × 200 float32)
**Expected elapsed**: ~10 min

---

## Scientific question

Can class-wise (Mondrian) conformal prediction provide COVERAGE guarantees over Bet T hypothesis tracking outputs, even if the argmax accuracy remains at the cycle-101 level (min_acc=0.689)?

This is Rescue #3 from the Research v158 drill: the conformal approach addresses coverage, not accuracy. The question is whether the substrate's retrieval distribution is informative enough to build valid per-hypothesis prediction sets.

Research P_deflated = 0.40 (moderate confidence; conformal coverage is a principled method anchored in Vovk-Shafer-Gammerman frequentist guarantees, but the prediction-set informativeness depends on the substrate's retrieval sharpness).

---

## Design

- **N**: 4096 (full scale, CPU-feasible)
- **K_hyp**: 8 hypotheses (matching cycle-101 configuration)
- **Calibration**: 80 queries per hypothesis per seed (5-fold split on 30 facts)
- **Test**: 120 queries per hypothesis per seed
- **Beta**: 8 (optimal per betT TEMPSCALE analysis: c/N = 32768/4096 = 8)
- **Alpha**: 0.10 (target coverage = 0.90)
- **Seeds**: [17, 23, 31]
- **Conformal method**: Mondrian (class-conditional) — separate calibration per hypothesis
- **Nonconformity score**: 1 - softmax_prob(true_label)
- **Quantile**: ceil((n_cal+1)*(1-alpha)) / n_cal th order statistic of calibration scores

---

## Falsifiable predictions

### HARD PASS (all required simultaneously per Research hard-pass criteria)
- All K_hyp=8 hypotheses: coverage in [0.85, 0.95] across 3 seeds
- Mean prediction-set size <= K_hyp/2 = 4.0 (informativeness gate)
- Verdict: `BET_T_CONFORMAL_PASS`

### HARD FAIL (any one sufficient)
- ANY hypothesis coverage < 0.80 OR > 0.99
- Verdict: `BET_T_CONFORMAL_KILL`

### Pre-registered expectation

P(PASS) = 0.40 (deflated from Research raw P). Conformal coverage guarantees hold in theory but require:
(a) Exchangeability of calibration/test data — satisfied by construction (i.i.d. seeds).
(b) Informative nonconformity scores — depends on beta=8 softmax being sharp enough.
  At N=4096 with 200 entities and 30 facts, beta=8 may give broad distributions (many entities have similar cosine similarity) -> large prediction sets.
The informativeness gate (set size <= 4.0) is the most likely failure mode.

P(PARTIAL) = 0.30 (coverage in bounds but sets too large).
P(KILL) = 0.30 (coverage out of bounds — most likely over-coverage > 0.99 at small N).

---

## PROT compliance

Not a closure; no PROT-004/006 required. This is a Rescue #3 probe on an existing 🟡 PARTIAL row (Bet T). If KILL: Research's remaining sketches (#1 Kerdock orthogonalization, #4 VAMP posterior, #5 re-anchor replay) are the next fallback. If Rescues #1-#5 all fail: Bet T becomes ❌ PROVISIONAL per PROT-004/006 discipline. PROT-001 (exp_dev_decisions log entry) paired.
