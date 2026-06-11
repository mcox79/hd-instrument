# Pre-registration: cls_rescue4_plus_rescue2_cpu_v1

**Date:** 2026-06-11
**Anchor:** cls_rescue4_plus_rescue2_cpu_v1
**Queue:** local_cpu_queue
**N_fast:** 2048, **N_slow:** 8192, **Seeds:** 1 (n=5 follow-up if passes)

## Scientific question
The two_substrate_fastslow_cls cell HARD_FAILed. Per the CLS 2x DEEP drill, the robust rescue is RESCUE-2 (asymmetric
capacity: small fast substrate for recent, large slow for durable) + RESCUE-4 (offline dedicated consolidation pass that
migrates only high-confidence >=3-retrieval patterns from fast to slow). Does this recover both recent recall (from fast)
and old-consolidated recall (from slow), without the threshold-gaming the generic rescue would require?

## Pre-registered bands

**HARD-PASS:** recent_recall >= 0.85 AND old_consolidated_recall >= 0.70 AND old_consolidated > old_from_fast
(consolidation is necessary, not a no-op).

**MIDDLE:** one of {recent>=0.85, old_consolidated>=0.70} holds and consolidation helps.

**HARD-FAIL:** neither holds, or old_consolidated <= old_from_fast.

## Calibration rationale
0.85 recent / 0.70 old are the drill's targets. The fast substrate is recency-decayed (DECAY=0.995, ~200 effective items
in N=2048), so recent items are recallable and old items forgotten -- the old_from_fast baseline must be LOW to prove the
consolidation (migrating old-important to the durable N=8192 slow store) is doing the work. A clean separation
(recent high, old-from-fast low, old-consolidated high) validates the architectural CLS rescue.

## N-suffix section
Asymmetric: N_fast=2048, N_slow=8192. Numpy CPU, seconds. n=1 exploratory; multi-seed n=5 follow-up if HARD_PASS.
