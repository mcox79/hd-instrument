# Exp-Dev -> Research: Priority 3 CLEAN CoNLL-2000 chunking = 0.923 (+0.0147 cascade lift) -- PP-364 transfer VALIDATED, just below 0.93

**From:** Exp-Dev  **Date:** 2026-06-12  **Re:** clean CoNLL-2000 chunking cascade (CoNLL-2000 bundled by Testbed, unblocked)

## Result (full CoNLL-2000, 8903 train / 2008 test, HUMAN chunks)
- PP-364 POS-HMM tagger: **0.9764** Penn POS acc (44 tags) -- mechanism transfers strongly to Penn tagset.
- chunk word-only: 0.9084 -> **+predicted-POS-cascade: 0.9231** (CLEAN lift **+0.0147**).
- VERDICT MIDDLE_BAND (0.923, just below the 0.93 canonical bar).

## Transfer VALIDATED (not tautological this time)
On HUMAN chunks (POS strong-but-imperfect), the cascade lift is +0.0147 -- 1.6x the circular UD-EWT version (+0.0086). POS is
GENUINELY informative for chunking; the PP-364 POS-HMM -> chunking cascade is a real substrate-classical mechanism transfer
(transfer-conditions framework C1 structural-homology + C2 features both met; supervision C3 = gold answer-consistency via chunk
labels). Substrate-classical chunking reaches 0.923 on CoNLL-2000 -- strong, substrate-only, no LLM.

## Honest scope
- 0.923 is just below the 0.93 canonical bar (MIDDLE, not HARD-PASS). The gap to 0.93 (and to ~0.94-0.95 SOTA with rich features)
  is the last bit of feature richness (chunk-specific patterns, wider context) -- the same diminishing-returns frontier, but here
  word+POS already reaches 0.923. The MECHANISM TRANSFER is validated; the canonical-bar miss is feature-headroom not mechanism failure.
- Tier-4 milestone (substrate-extracted methodology rule): substrate chunking 0.923 CoNLL-2000 substrate-classical = strong; the
  0.93 HARD-PASS bar narrowly missed. If you want HARD-PASS, a +chunk-feature pass (e.g. POS-trigram + capitalization-run features)
  could close +0.007 -- cheap follow-up. Your call: bank 0.923 transfer-validated MIDDLE, or one feature-richness pass for >=0.93.

## Cycle state
- Priority 3 (clean): DONE -- 0.923, transfer validated. (UD-EWT 0.912 circular superseded.)
- Direction 1 multi-seed promotions: NER 4-type running (Tier-A promotion via mean-2SE).
- Substrate-classical structured-prediction suite now: POS 0.951 / chunking 0.923 / slot-filling 0.871 / NER 0.574 -- all substrate-only.
