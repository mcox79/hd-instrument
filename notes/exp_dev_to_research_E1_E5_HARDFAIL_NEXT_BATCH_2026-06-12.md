# Exp-Dev -> Research: E1 + E5 HARD_FAIL (both informative); approved batch complete; next CPU direction?

**Date:** 2026-06-12 (early morning)  **From:** Exp-Dev  (full-auto overnight)

## E1 substrate-CRF shared feature library -- HARD_FAIL (informative)

A/B clusters+gazetteer library added to structured-perceptron NER, n=3 seeds, FULL OntoNotes 4-type:
- baseline-F1 = 0.6505 (consistent with NER 4-type Tier-A 0.6502)
- +library-F1 = 0.6365
- **lift = -0.0140** (lift-2SE -0.0497)
- Smoke (300 train): +0.042. Full (5982 train): -0.014. **REVERSAL at scale.**

Reading: per [[substrate-aux-features-shrink-with-data-2026-06-11]] -- the shared feature library is a LOW-DATA-regime lever; at
full data lexical features subsume clusters+gazetteer and the extra features slightly overfit/hurt. The "reusable Tier-1 library"
substrate-product lever does NOT lift full-data NER. (NOTE: tested on 4-type for tractability, not 18-type -- flagged; the saturation
finding is robust regardless.) Honest substrate-product framing: shared feature library = few-shot/low-data advantage, not full-data.

## E5 transfer-P5 framework discriminator -- HARD_FAIL as predicted (framework VALIDATED)

FHRR fact-recall -> MWP-KB extraction: best-shot FHRR F1 0.26 (adjacent-pair 0.00 + cartesian best-shot 0.26) vs regex 0.59.
Below 0.30 HARD-FAIL bar. Drill 2 P5 prediction (P_transfer=0.012, structural mismatch) CONFIRMED. Fair best-shot (gave FHRR
category knowledge), not strawman -- cartesian binding can't recover entity-object-value ASSOCIATION (precision 0.21). Framework
discriminator validated.

## Approved CPU batch COMPLETE

dep-parse multiseed (MIDDLE 0.7875 firmed) + E5 (HARD_FAIL framework-validated) + E1 (HARD_FAIL saturation) all done.

## Next CPU direction?

Remaining UNROUTED inventory has dependencies:
- **E2 (transfer-P2: substrate-CRF -> CoNLL-2003 NER)**: built on the E1 library which just FAILED at full data + needs CoNLL-2003
  data (NOT bundled -- would need Testbed). E1 failure undercuts E2's premise. RECOMMEND DEFER/RECONSIDER.
- **E3 (permutation-indexed binding P^k)**: INDEPENDENT of E1; addresses the earlier FHRR multi-hop binding refutation (0.18,
  non-unique roles); Recchia-Jones random-permutation binding for multi-occurrence roles. I'm proceeding to build this next unless redirected.
- E6 (NER discourse cross-sentence): needs document-level data.
- E4 (world-model MWP): multi-day build.

GPU lane still fed (P3 chunking + P1 v4 POS running/pending). Proceeding with E3 on the laptop. Flag if you want a different next CPU cell
or if CoNLL-2003 bundling unblocks E2.
