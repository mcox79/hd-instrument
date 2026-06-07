# Research -> Exp-Dev: ZKL methodology 3 pre-tests AUTHORIZED (variance characterization)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** ZKL methodology stability 2x drill output + exp_dev handoff.

## Authorize 3 pre-tests from drill handoff

Per `exp_dev_handoff_research_zkl_methodology_stability_2026-06-07.md`:

### Pre-test A: Seed sweep (10 seeds; ~4 hr CPU)
Quantify coefficient of variation on ZKL(50) at T=1.3 with 10 different seeds. Gives us
the honest CI for customer pitch materials.

HARD-PASS: std < 0.05 (low variance; current methodology is more stable than feared).
BORDER: std 0.05-0.12 (moderate variance; usable with CI framing).
HARD-FAIL: std >= 0.12 (high variance per drill prediction; mean-over-K construction
needed).

### Pre-test B: Mean-vs-max construction (free from A data)
Same A run; compute mean-over-K instead of max-over-K. Compare variance.

HARD-PASS: mean-over-K std < 50% of max-over-K std (significantly more stable).
HARD-FAIL: similar variance (mean doesn't help).

### Pre-test C: Temperature sweep (T=0.5, 1.0, 1.3)
Same KB, varying paraphraser temperature. Identifies if lower T fundamentally reduces
variance.

HARD-PASS: T=0.5 std < 50% of T=1.3 std (lower-T paraphraser is the methodology fix).
HARD-FAIL: variance similar across T (sampling is irreducibly variance-fragile).

## Customer pitch framing depends on results

If A HP (low variance unexpected): current "qualified posture ZKL~0.22" framing is
safe to use as-is.

If A BORDER/HF + B HP (mean-over-K stable): switch to mean-over-K reporting.

If A HF + B HF (irreducibly fragile): customer pitch uses bootstrap CI explicitly:
"ZKL median Y, IQR [X, Z] across 20 seeded runs."

In all cases, Path D for absolute HIPAA stays as the formal-guarantee differentiator.

## What this DOESN'T change

- Locked qualified posture + Path D as PERMANENT v1 customer pitch (decision stands)
- Decline of deterministic-paraphraser leakage harness investment (decision stands)
- ZKL T1-T5 defense-in-depth cells (INLP/VIB/GRL) stay PARKED until methodology
  characterization complete

## Wall time

~5-6 hr total parallel CPU. A and C parallel; B is free from A's data.

## Cross-references

- ZKL methodology stability 2x drill: notes/research_drill_zkl_methodology_stability_2x_2026-06-07.md
- Drill Exp-Dev handoff (pre-test specs): notes/exp_dev_handoff_research_zkl_methodology_stability_2026-06-07.md
- Entropy-max recal result (qualified posture locked): notes/exp_dev_to_research_entropy_max_recal_RESULT_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize all 3 pre-tests (A + C parallel; B free from A). File the variance
characterization on completion. Customer pitch framing decision follows the results per
the matrix above.
