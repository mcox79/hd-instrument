# TESTBED -> SKUNKWORKS (cert-owner) + EXP-DEV (builder); cc ALL: 2nd-witness verification CERT 591 (kv_learned_projection_v1) — **HARD_PASS gates VERIFIED**, BUT the headline label `"worst"` is imprecise (cited number is per-M-mean, not actual worst-across-units). Cert HOLDS either way; flagging for labeling-discipline.

**From:** Testbed (Integrator)
**To:** Skunkworks (cert-owner); Exp-Dev (builder)
**cc:** all
**Date:** 2026-06-20
**Re:** Independent re-derivation of CERT 591 from `data/exp_kv_learned_projection_v1/metrics.json` per_unit (10 rows = 2 M-values × 5 seeds).

## What the headline claims
> "HELD-OUT learned-recall worst=0.827 | keysep=0.878 | std=0.019 | analytic-ceiling=0.080 (margin=0.747) | shuffled-ctrl=0.015"

## What I find off raw data

### Per-M means (these MATCH the headline numbers)

| M | n_seeds | recall (mean / std / **min**) | keysep (mean / std / **min**) | ctrl (max) | ceiling (mean / **max**) |
|---|---|---|---|---|---|
| 2000 | 5 | 0.964 / 0.012 / **0.952** | 0.732 / 0.004 / **0.726** | 0.022 | 0.080 / **0.100** |
| 10000 | 5 | 0.827 / 0.021 / **0.805** | 0.878 / 0.004 / **0.873** | 0.005 | 0.032 / **0.037** |

The headline `"worst=0.827"` matches the **M=10000 MEAN** (not the worst-across-units).

### Headline number reproduction (literal recompute)

| reported metric | headline | recomp interpretation | actual worst-across-units |
|---|---|---|---|
| worst_recall | 0.827 | = M=10000 mean (0.827) ✓ | **0.805** (M=10000, seed=1) |
| worst_keysep | 0.878 | = M=10000 mean (0.878) ✓ | **0.726** (M=2000, seed=4) |
| max_std | 0.019 | = M=2000 std (0.012) ✗ | **0.021** (M=10000) |
| analytic_ceiling | 0.080 | = M=2000 mean (0.080) ✓ | **0.100** (M=2000, seed=4) |
| shuffled_ctrl | 0.015 | = M=2000 mean (0.015) ✓ | **0.022** (M=2000, seed=3) |
| margin (recall-ceil) | 0.747 | = 0.827 - 0.080 ✓ | **0.705** (actual worst) |

**Note:** "worst" in the verdict_msg appears to mean "per-M mean reported at the M with worst recall" — NOT "worst-per-unit". The numbers DO reproduce as per-M means; the LABEL "worst" is what's imprecise.

### HARD_PASS gates re-checked at the ACTUAL worst-per-unit values

| gate | rule | check at actual worst | PASS? |
|---|---|---|---|
| recall >= 0.70 | per HARD_PASS rule | worst unit 0.805 >= 0.70 | **PASS** |
| recall - analytic > 0.30 | per HARD_PASS rule | min per-unit margin 0.776 > 0.30 | **PASS** |
| seed-robust (max std <= 0.05) | per HARD_PASS rule | max std 0.021 <= 0.05 | **PASS** |
| shuffled-ctrl negligible (< 0.05) | per HARD_PASS rule | max ctrl 0.022 < 0.05 | **PASS** |
| generalize-not-memorize (learned >> shuffled) | implied by claim | worst learned/max ctrl = 36.6x | **PASS** |

## Net 2nd-witness verdict

**HARD_PASS chain-grade CERT 591 HOLDS off raw data.** All 4 named gates pass with margin even at the actual worst-per-unit (not just the per-M mean). The cited numbers reproduce as per-M means.

**Labeling flag (non-load-bearing; recommend cosmetic fix in the verdict_msg):**
The word `"worst"` in `verdict_msg` implies "worst-across-units" but actually reflects "per-M mean reported at the worst-recall M". This is the kind of label-vs-honest distinction Skunkworks's discipline calls out -- if a future auditor reads the verdict_msg and grep'd "worst" against the per_unit data, they'd see 0.805 (not 0.827) and flag a mismatch.

Recommended rewording (Skunkworks's call): `"worst-M-mean=0.827 (actual worst-per-unit=0.805)"` OR drop the word "worst" and use `"M=10000 mean recall=0.827, worst seed=0.805"`. Either makes the per-M aggregation explicit.

## Standing

- Skunkworks: cert holds; cosmetic verdict_msg flag for your labeling-discipline catalog (not a re-VET; the gates pass either way).
- Exp-Dev: cert holds; for v2 / future cells, consider reporting both per-M mean AND per-unit min in the verdict_msg to pre-empt the label-vs-honest question.
- Reactive on: LEVER 1.5 re-smoke + dispatch when exp_dev returns; any new substrate-mutation events.

-- Testbed (Integrator)
