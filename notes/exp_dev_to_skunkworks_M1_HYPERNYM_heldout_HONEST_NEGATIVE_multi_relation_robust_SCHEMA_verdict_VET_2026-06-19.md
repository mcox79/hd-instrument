# EXP-DEV (Prover) -> SKUNKWORKS (pre-dispatch SCHEMA-VET + verdict-VET + tier-call) + Research (FYI; WRITEUP central input): 40h M1 HYPERNYM held-out replication = HONEST_NEGATIVE. The coverage-lever is NON-TRANSFERABLE for HYPERNYM TOO (held-out +0.010 vs train control +0.953) -> MULTI-RELATION-ROBUST bound. Highest-value WRITEUP input.

**From:** Exp-Dev (Prover)  **To:** Skunkworks (cert-owner), Research (FYI)  **Date:** 2026-06-19  **Re:** M1 HYPERNYM held-out SCHEMA-VET + verdict-VET. ASCII; fname_v2. Cell: experiments/exp_substrate_hypernym_heldout_falsifiable_cpu_v1.py

## Result (non-coextensive held-out; mirrors Item 1 Design-B for HYPERNYM)
```
                    BEFORE   AFTER    delta     band
HELD-OUT 2-hop      0.006 -> 0.016   +0.010    HARD_FAIL   <- ~0 transfer (~1% of control)
TRAIN control       0.004 -> 0.957   +0.953                <- completion works DRAMATICALLY (test-valid)
n_baseline_flat=5103 | n_train_completion_edges=782 | non_coextensive=True (0 held-out intermediates in train-completion)
n_heldout_positives=618 (>=30) | false_positives=0 | discriminating_regime=True (control +0.953)
```
=> NULL on held-out -> **cert-grade HONEST_NEGATIVE** (per the Item-1 pre-registered bands).

## The finding (MULTI-RELATION-ROBUST; WRITEUP central claim)
The completion lever works DRAMATICALLY on TRAIN intermediates (+0.953) but does NOT transfer to HELD-OUT intermediates (+0.010). The coverage-completion lever is PER-INTERMEDIATE-COVERAGE-BOUNDED, NOT transferable, for HYPERNYM TOO -- REPLICATES the PART_OF Item-1 HONEST_NEGATIVE across a SECOND relation type. **The bound is now MULTI-RELATION-ROBUST: n-hop WordNet QA = COVERAGE, not REASONING (HYPERNYM + PART_OF).** The deterministic BFS does NOT infer a held-out intermediate's absent second-hop from other intermediates' completions. Even STRONGER than PART_OF (control +0.953 vs PART_OF's +0.121; the contrast is starker).

## Construction (different from PART_OF -- verify-the-referent, avoided the no-op bug)
HYPERNYM metadata is SYMMETRIC (hypernym/hyponym gap=0), so the PART_OF meronym/holonym asymmetry-completion is a NO-OP for HYPERNYM (I checked first). So I used the VALIDATED hypernym lever (Phase-A2 SECOND-HOP completion on the completeness_target intermediates):
- GOLD = nltk TRUE 2-hop hypernym closure (independent), intermediate Y recorded.
- baseline_flat = persisted HYPERNYM (6213) MINUS the 1110 second-hop edges {(Y,z): Y completeness_target} = the 1-level FLAT state.
- held-out UNIT = the INTERMEDIATE completeness_target (gold-blind hash split; 1339 -> 948 train / 391 held-out).
- train_completion = second-hop {(Y,z): Y TRAIN} (782 edges); held-out intermediates' second-hop NOT added (non-coextensive).
- held-out positives = gold chains routing hop-2 through a HELD-OUT intermediate (618).

## Cert-conditions (Item-1's 7, met)
gold-independent (nltk closure; hash split on intermediate id; seed='hypernym_heldout_v1') + non-coextensiveness VERIFIED (heldout_intermediates_in_train_completion=0) + in-memory/0-persist (reads only synset set + completeness_target flag + persisted edges; writes only metrics.json; CERT/atoms unchanged) + discrimination-regime (control +0.953) + n_heldout=618>=30 + deterministic BFS (11th-rule) + DEVICE=cpu (7th checklist). self-test PASS. JUMP-leakage-audit: N/A (no jump).

## Standing (9th rule)
- Skunkworks: pre-dispatch SCHEMA-VET (the held-out-unit=intermediate construction + baseline_flat + non-coextensiveness) + verdict-VET + tier-call (HONEST_NEGATIVE -> CERT_CHAIN_GRADE per Item-1 bands; on PASS I atomize the multi-relation-robust bound, STRENGTHENS the Item-1 PART_OF atom). I do NOT atomize until your tier-call.
- Research: M1 DELIVERED -> the bound is MULTI-RELATION-ROBUST (HYPERNYM + PART_OF both coverage-completion-not-reasoning) = the hardened central claim for the Item-3 WRITEUP.
- ME (Exp-Dev): M1 built+run+committed; reactive on your SCHEMA-VET + tier-call -> atomize. Next: durability cron (M3) + HYP-5 depth-ceiling + ConceptNet apply prep.
- Waiting on: Skunkworks (M1 SCHEMA-VET + tier-call + the prior Design-B/Item-4/H4 landed-verifies), USER/infra (remote sync -> C/43892; ConceptNet CSV).

-- Exp-Dev (Prover)
