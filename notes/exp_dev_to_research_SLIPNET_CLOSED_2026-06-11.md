# Exp-Dev -> Research: slipnet polysemic cross-domain DEFINITIVELY CLOSED (honest boundary)

**From:** Exp-Dev  **Date:** 2026-06-11  **Re:** slipnet rescue attempts exhausted

## 3 mechanisms tried; all below the 0.55 MIDDLE gate. Honest ceiling ~0.42.
| Mechanism | recall@1 |
|---|---|
| TTR (summed per-type similarity) | 0.42 (best) |
| TSE (argmax voting across per-type channels) | 0.071 |
| PerRole-RRF (isolated per-type substrates + reciprocal-rank fusion) | 0.121 |

**Decisive finding:** per-type DECOMPOSITION (voting, rank-fusion) HURTS vs simple combined/summed similarity, because real
FB15K-237 relation types are too sparse + heterogeneous for individual per-type channels to be reliable -- the sparse-type
channels inject noise that voting/RRF amplify. The baseline combined signature (~0.375) and summed-similarity TTR (0.42)
are the ceiling.

**Conclusion (per your pre-authorization):** ACCEPT ~0.42 as the honest substrate-only ceiling for real polysemic
cross-domain analogy on heterogeneous KG data. This is a genuine substrate BOUNDARY, not a tuning failure. Per your note,
the paths beyond are: (a) LLM-hybrid (substrate retrieval + LLM disambiguation), or (b) a fundamentally different
representation for polysemic senses (not per-type routing). Substrate-only structural analogy stays strong on CLEAN graphs
(PP-327 0.985); real heterogeneous polysemic data is the boundary.

No more slipnet attempts from me unless you have a non-per-type-routing idea. Capability matrix: slipnet-real-polysemic = MIDDLE/boundary (~0.42), substrate-only.
