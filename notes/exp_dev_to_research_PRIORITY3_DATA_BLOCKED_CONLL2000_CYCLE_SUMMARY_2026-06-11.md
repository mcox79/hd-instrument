# Exp-Dev -> Research: Priority 3 chunking DATA-BLOCKED (CoNLL-2000 unloadable) + consolidated-drills cycle summary

**From:** Exp-Dev  **Date:** 2026-06-12  **Re:** Priorities 1-3 status + request

## Priority 3 chunking: DATA-BLOCKED
CoNLL-2000 is not loadable: `load_dataset('conll2000')` + `eriktks/conll2000` use script-based loaders the installed datasets
version rejects ("Dataset scripts are no longer supported"); `tomaarsen/conll2000` doesn't exist; not in HF cache; runner has no
network. The UD-EWT fallback is CIRCULAR: my UD-EWT chunk labels are DERIVED from POS, so a POS-cascade helps tautologically and
does NOT test the transfer-conditions framework (P1) or the canonical syntactic cascade. A clean Priority-3 test needs human-
annotated CoNLL-2000 chunks (POS = strong-but-imperfect feature).

REQUEST: can Testbed bundle CoNLL-2000 (train.txt/test.txt from the standard CoNLL-2000 distribution -> experiments/data/conll2000.json
with tokens/pos/chunk_bio)? Then I run the PP-364 POS-HMM -> chunking cascade cell (P1 transfer + Tier-4 milestone). Until then,
Priority 3 is blocked.

## Consolidated-drills cycle summary (Priorities completed)
- **Priority 1 BMA: DONE, decisive.** Ensemble gain 0.000 -> MWP errors CORRELATED = comprehension blind-spot at question-language
  level. Validates the math+science INGESTION strategy (corpus deficiency, not mechanism deficiency). MWP banked (0.224->0.385 firmed).
- **Priority 2 NER frame-semantic: HARD_FAIL.** Lift -0.005 (smoke +0.036 collapsed at scale). Anti-shrinkage REFUTED; construction
  frames saturate like lexical features. NER comprehensively feature-saturated (5+ approaches all <=+0.013); ~0.58 OntoNotes-18 /
  0.648 CoNLL-equiv is the in-corpus saturation point. External-resource lever deferred per rule 7/8.
- **Priority 3 chunking: DATA-BLOCKED** (above).
- Priority 4 resonator: DEFERRED for MWP (your call; BMA shows comprehension not binding is the MWP wall).

## Honest state / recommendation
The consolidated drills' top MWP+NER paths are now EMPIRICALLY RESOLVED: MWP comprehension-bound (corpus-deficiency; re-test post-
math+science-ingestion); NER feature-saturated (external-resource-bound). Both honest, both pointing to CORPUS/EXTERNAL-RESOURCE as
the next lever (consistent with the user's ingestion strategy + rule 7/8 external-resource deferral). Recommend: BANK this cycle;
the next genuine lever is the math+science corpus ingestion (re-test MWP after) + a CoNLL-2000 bundle for the chunking transfer test.
Awaiting your direction + the CoNLL-2000 data; will run the chunking cascade the moment it lands.
