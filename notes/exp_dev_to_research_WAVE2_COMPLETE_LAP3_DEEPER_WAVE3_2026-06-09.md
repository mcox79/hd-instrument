# Exp-Dev -> Research: WAVE-2 complete (~16 HP) + LAP-3 deeper issue + need wave-3

**From:** Exp-Dev  **Date:** 2026-06-09 (full-auto overnight)

## WAVE-2 essentially COMPLETE -- HARD_PASS:
LAP2-1 paracons, LAP2-2 belief-revision, LAP2-3 meta-substrate, LAP2-4 cultural-conventions, LAP2-5 10-hop, LAP2-6 k-hop-aggregate, LAP2-7 cyclic-validate, LAP2-8 continuous-binding(temporal), LAP2-9 predictive-coding, LAP2-10 per-token-audit, LAP2-12 PII(recall1.0/FP0.0), LAP-12 modal-amplitude, STRETCH2-1 temporal-interval(Allen), STRETCH2-2 causal-do-chains, STRETCH2-3 planning-STRIPS(rescued, solved 1.0), STRETCH2-4 active-inference(Friston, converge 1.0). Deferred: LAP2-11 haiku.

## LAP-3 deeper issue (need decision)
Option-3 (relational homomorphism over FB15K same-relation pairs) ALSO does not work on RAW FHRR atoms: mean over same-relation pairs of E[t]*conj(E[h]) -> ~0 for random entity vectors (no shared transform exists unless the embedding ENCODES relational structure). Options:
1. **Train TransE-style relation embeddings** over FB15K-237 (closed-form or gradient; ~30min CPU) so E[h] bound R[r] ~ E[t]; THEN proportional analogy works. Real but a learned relational layer (not raw substrate).
2. Accept proportional-analogy is NOT a raw-substrate primitive (it needs a learned relational projection -- which is fine, it's the PP-225-style head).
3. Test analogy over role-filler RECORDS (retrieval, not transform-analogy).
I lean option 1 or 2. Which?

## LAP2-11 haiku
Needs a syllable-annotated vocab + constraint-fill. Build with a hardcoded ~80-word syllable vocab (synthetic-but-valid), or skip (NLG not core substrate)?

## Need WAVE-3 (laptop low again)
~16 wave-2 HP done; laptop out of authorized anchors. Send wave-3 pure-numpy/VSA batch OR redirect (harder-regime re-tests, a specific capability deep-dive, or pivot me to GPU-verdict collection as the torch batch lands).

## GPU status
Torch batch all running/queued (long, sequential): qwen-kb50k (running) + pp225_multihop + pp225_multihop_3hop(GPU-8) + hybrid_3seed(GPU-9) + hybrid_1.4B(GPU-10) + pp225_export(Testbed checkpoint). Verdicts over next hours; export .pt pending. GPU dispatch now reliable (local queue_add.sh SCPs directly, bypasses the home dirty-tree).
