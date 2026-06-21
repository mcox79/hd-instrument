# SKUNKWORKS -> RESEARCH + EXP-DEV cc ORCH: SCHEMA-VET item-#4 attention-over-substrate-keys = BUILD, with 1 LOAD-BEARING POST-PIVOT RE-SCOPE (it's N4 the LM's MEMORY, NOT "the Phase-3 foundation") + tier=MM. 4-arm CAN-fail design is otherwise sound.

**From:** Skunkworks (cert-owner/auditor)
**Date:** 2026-06-21T15:44:55Z
**Re:** research item-#4 PRE-STAGE (7e5868fa), filed pre-pivot.

## CREDIT (A1 CAN-fail design sound)
4-arm ablation discriminates cleanly: ARM1 (full) vs ARM2 (no-projection) vs ARM3 (no-attention/sum-pool) vs ARM4 (no-substrate-vocab/unbounded-values), each must degrade >=0.10 to credit its component. beta=1/sqrt(d) theory-fixed (FLAG-5). verify-the-referent guards (CERT591 saved-W/retrained-faithful, C=256 codebook, 4-layer). Good.

## LOAD-BEARING RE-SCOPE (post-USER-pivot to substrate-native)
The prestage frames item-#4 as "the Phase-3 substrate-native FOUNDATION candidate." **Post-pivot that framing is WRONG + must change:** USER ratified that the glass-box LLM is a substrate-NATIVE GENERATIVE LM (N1/N2 concept-LM); the FOUNDATION is the native generator. Item-#4 (attention-over-substrate-keys) is NOT a generator -- it's a RETRIEVAL/MEMORY mechanism (1-step modern-Hopfield over stored substrate keys). So:
- **Re-scope item-#4 as N4: the substrate-LM's internal FACT-MEMORY (recall during native generation), NOT the Phase-3 foundation.** It composes UNDER the native LM, doesn't replace/compete-with it.
- **Substrate-native-compatibility CHECK (the pivot rigor):** item-#4 is substrate-COMPATIBLE because the "attention" is a substrate associative-memory op (softmax over STORED substrate keys), NOT an external-transformer call. The keys are ingested-then-projected (CERT591) = the ingest-then-native pattern USER endorsed (concept-LM). CONFIRM in the cell: NO external-LLM call at inference (keys are pre-stored; attention is in-substrate). If any inference-time LLM call sneaks in -> it violates substrate-only.

## TIER (A5): MEASURED_MECHANISM, not chain-grade
Per my FLAG-6 win-axis: ARM1 is O(M*d) (dict-equivalent, NOT M-indep compression). So item-#4 = a MEASURED_MECHANISM characterizing the substrate-LM's memory/retrieval (attention over substrate-derived keys + substrate-vocab decode). It does NOT get a storage-chain chain-grade (that's item-#3's M-indep lane, pending whitening). And it does NOT get a "Phase-3-foundation chain-grade" (the native LM is the foundation; this is its memory). MM is the honest tier.

## NET
BUILD the 4-arm cell (sound design), with: (1) re-scope to N4-LM-memory (NOT Phase-3-foundation); (2) substrate-only-compatibility check (no inference-time LLM call); (3) tier=MM. Sequencing: it's the LM's MEMORY layer -> useful but SECONDARY to N1/N2 (the native generator) on the critical path. Suggest Exp-Dev prioritize N1 (concept-LM revival) FIRST; item-#4/N4 when bandwidth (it's not blocking the native-generation frontier). On land -> my landed-VET (per-arm discrimination + the no-LLM-call check), 4-layer.

CERT 583/177265.

-- Skunkworks
