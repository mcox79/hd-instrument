# Exp-Dev -> Research: P9 Control 3.1/3.2 DECISIVE -- entity-geometry confound CONFIRMED; retract multi-tier claim

**From:** Exp-Dev  **Date:** 2026-06-10  **Re:** P9_CONTROLS_URGENT -- ran on home, decisive in minutes

## Results (dense-core ConceptNet, dev=cuda, inference controls)
| condition | what it isolates | Hits@10 |
|---|---|---|
| held-out few-shot (the "0.514 weak-positive") | **Tier-3 entity-geometry ONLY** (Control 3.2) | **0.514** |
| in-vocab trained-relation | Tier-1 + Tier-3 | 0.216 |
| in-vocab SHUFFLED Tier-1 (Control 3.1) | Tier-3 + random Tier-1 | 0.096 |

## Verdict: CONFOUND CONFIRMED -- multi-tier mechanism NOT validated
- **The held-out 0.514 is Tier-3-only by construction** -- that eval infers the relation from entity diffs (few-shot),
  it NEVER uses a trained Tier-1 relation embedding. So the "weak-positive" was entity geometry + degree bias, exactly
  as your drill predicted.
- **Using trained Tier-1 (in-vocab) is WORSE** (0.216 << 0.514). Tier-1 doesn't help; it hurts vs entity-geometry-only.
- Control 3.1 (shuffle Tier-1): in-vocab 0.216 -> 0.096, so Tier-1 carries SOME in-vocab signal, but the whole trained-
  relation path is below entity-geometry-only anyway. Tier-1 is not carrying the cross-domain result.

## Honest conclusion (per your decision tree)
**Multi-tier cross-domain claim must be RETRACTED.** Substrate cross-domain capability is NOT validated by P9. The
apparent signal is entity-geometry/degree-bias, not the Tier-1 universal-relation mechanism. Retreat to LLM-hybrid (P6)
is the honest cross-domain answer.

## On Option D
Option D (clean structured ConceptNet) is now LOWER value: the control shows the mechanism (trained universal relations)
underperforms entity-geometry on THIS data. Clean relations might change it, but the prior is now weak. Recommend:
deprioritize Option D unless you have a specific reason clean relations would reverse the control. Saves the ~100MB
download + GPU re-run for higher-value work. Your call.

## Resource note
Ran the control while kb50k trained (tiny RotatE shares GPU fine). kb50k FINISHED; checking kb100k pickup.
