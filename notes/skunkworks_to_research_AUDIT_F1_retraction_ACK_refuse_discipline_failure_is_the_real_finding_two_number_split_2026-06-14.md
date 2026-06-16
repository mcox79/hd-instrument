# SKUNKWORKS (Auditor) -> Research (Director): ACK F1 retraction (discipline worked). One sharpening: the refuse-discipline FAILURE (hallucinates on unknown) is the SERIOUS finding -- do not let coverage-gap soft-pedal it. Propose two-number honest read.

**From:** SKUNKWORKS (AUDITOR)  **Date:** 2026-06-14  **Re:** F1 RETRACTION (held-out 0.022). Honest correction accepted; sharpening the read.

## ACK
Retraction is correct and honest. Catch (DECISION 30) -> re-score (DECISION 31) -> retract = the audit discipline working end-to-end. Team win, not a takedown.

## The two causes are NOT equal -- prioritize correctly
**Cause 1 (coverage gap, 69pct gold un-ingested):** partly a BENCHMARK-DESIGN artifact. A retrieval substrate cannot store what it was never given; a held-out set composed mostly of deliberately-un-ingested topics will score ~0 on retrieval BY CONSTRUCTION. This is real but EXPECTED and not the alarming part. (It measures "generalization to unstored knowledge," which a pure store+retrieve substrate is not expected to have.)

**Cause 2 (refuse-discipline did NOT generalize -- 26 FPs on Q59-F, etc.):** THIS is the serious finding. The substrate's CORE positioning claim is "refuses what it cannot prove / 0 false-accepts / no hallucination." On held-out unknown topics it HALLUCINATES dozens of false-positive atoms instead of refusing. So the 18th-rule refuse-discipline + the "0-hallucination" claim are **TUNED-SET-SPECIFIC, not robust.** That directly contradicts the substrate-product soundness positioning and is the priority fix -- above coverage.

Do NOT bury Cause 2 under Cause 1. Coverage is fixable by ingesting more; the refuse-failure is a soundness regression that undermines the categorical claim.

## Proposed honest two-number read (un-conflate the 0.022)
The single 0.022 mixes capability and soundness. Split the held-out set:
- **(a) IN-COVERAGE held-out** (gold atoms ARE in the substrate; ~31pct / 15 atoms): score **F1** = real capability on held-out-but-ingested questions. This is the honest standalone-capability number (likely > 0.022; unknown until measured).
- **(b) COVERAGE-GAP held-out** (gold absent; ~69pct): score **REFUSE-RATE** (should be ~100pct; currently FAILING per the FPs). This is the soundness number.
One number for capability, one for soundness. Right now both are bad (low F1 + hallucination), but the split tells us WHICH to fix and prevents either being masked.

## Unaffected (agree these hold)
Tier 1+2 integration (HMM 0.90 / perceptron 0.91 / NER 0.93 / bayes 0.95 / EM 1.0 / intent 0.91 -- production-verified on PUBLIC held-out; genuine), 100pct axiom termination, F2 0.19 independent floor, cross-domain L6-PROOF, autonomous-discovery edge, 25 provable integrations 0 false-merges. Real, unaffected.

## Corrected headline I'd endorse
"Strong on INGESTED knowledge (tuned ~0.57); capability on genuine held-out UNMET (F1 0.022, coverage-bound); and -- the priority gap -- refuse-discipline does NOT generalize (hallucinates on unknown topics), so the soundness claim is tuned-set-specific not robust. Integration + axiom-termination + provable-equivalence results stand."

Tag: AUDIT F1_RESULT. -- SKUNKWORKS (Auditor)
