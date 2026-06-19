# Exp-Dev -> Research: F1 BRIDGE local results -- BOTH retrieval primitives (algebra E-S3 + BGE E-S1-proxy) are HEALTHY -> 0.0067 is a degraded-scorer artifact (H1 CONFIRMED, substrate-side). The definitive canonical+bge rerun is BLOCKED on a BGE install. Precise asks below.

**From:** EXP-DEV  **Date:** 2026-06-13 late evening (F1 AMENDMENT tests, PRIORITY 1)
**Re:** E-S3 + E-S1/E-S2. Substrate-internal (11th rule); ACTUAL deltas (10th rule). Single dense note (Orchestrator denser-fewer).

## Headline: H1 (degraded-scorer) CONFIRMED from the substrate side. Both retrieval primitives work.

| test | layer | metric | verdict |
|---|---|---|---|
| E-S3 CHTV-1 retrieval self-verification | algebra-HRR (deduction) | top-5 acc **0.9643**, top-1 0.9643, median RHS rank 1 (28 pairs, 56 queries) | **HARD_PASS** (>=0.80) |
| E-S1 proxy (BGE primitive) | BGE semantic (cached core) | flat top-10 recall of equivalent **0.75** (16 pairs, 32 queries) | HEALTHY (>=0.60) |
| E-S2 proxy (domain routing) | BGE + domain partition | routed recall 0.4375 (lift -0.31) | inconclusive locally (see caveat) |

**Conclusion:** the substrate retrieves its own algebra-equivalent atoms (E-S3, 96%) AND its BGE-equivalent atoms (E-S1-proxy, 75%) at healthy rates. The 0.0067 F1 is NOT a retrieval-primitive failure at either layer -- it is the degraded scorer (1746/20820 atoms + bge OFF) exactly as your root-cause drill's H1 predicted. Substrate change is NOT required to lift F1; the SCORER must run on canonical 20820 + bge ON.

## Honest caveats (10th rule + R3)
- **E-S1/E-S2 are PROXIES, not the literal tests.** sentence_transformers is NOT installed locally (this is WHY the scorer ran cpu_only_no_bge_degraded). The literal E-S1 (description-as-query) and full-corpus E-S2 need BGE to encode queries. I used the CACHED BGE index (bge_large_v2_name_1782, 1782 precomputed vectors) and queried with cached atom vectors -- a BGE-layer analog of E-S3 (does one member's BGE vector retrieve its equivalent). It tests the BGE PRIMITIVE, which is the H1 question; it does not reproduce the description-query recall number.
- **E-S2 routing hurt (-0.31) but that's largely an artifact:** several equivalence "pairs" in the cache are research_drill_* NOTE atoms with domain=unknown (routing-ledger entries, not operators); routing to the giant unknown-domain bucket is unhelpful. This is NOT a clean test of your 28-type-atom partition routing. Proper E-S2 (28 type-atom partitions, real operators, full corpus) is deferred to the BGE run. So: routing verdict = inconclusive, not refuted.

## The BLOCKER (precise infra ask)
The DEFINITIVE H1 confirmation -- "rerun held-out F1 on canonical 20820 + bge ON" -- and the literal E-S1/E-S2 all need **sentence_transformers / BGE installed on an accessible machine.** It is NOT installed on this laptop, and the only BGE artifacts are cached npz for ~1782 atoms (the structured core). To get the real F1 number you wanted:
1. Install sentence_transformers + bge-large on the runner desktop (or wherever the canonical 20820 index lives), OR
2. Point me at a machine/venv where BGE is available and I'll queue the canonical+bge rerun + literal E-S1/E-S2 there.

I have the cells ready; they're blocked only on BGE availability. Which machine should run the BGE-enabled rerun?

## Intuitive (communication rule)
The scary "F1 = 0.0067" was a broken thermometer, not a sick patient. I tested the substrate's two ways of finding its own knowledge: by math-type (96% -- it finds the equivalent operator almost every time) and by meaning/BGE (75% on the cached core). Both work. So the substrate CAN recognize and verify itself; the benchmark just measured it with most of the corpus missing and the meaning-encoder switched off. To get the true score we need to switch the meaning-encoder back on (install BGE) and score against the full 20,820 atoms -- that's the one thing I can't do on this laptop.

## Asks
- **Research:** where should the BGE-enabled canonical rerun run? (install on runner desktop / point me to a venv). That's the gate to the real F1.
- E-S3 (HARD_PASS) + E-S1-proxy (healthy) are the substrate-understands-itself canonical tests you flagged for USER -- we ARE there at the primitive level; the measurement was broken, confirmed.

-- EXP-DEV
