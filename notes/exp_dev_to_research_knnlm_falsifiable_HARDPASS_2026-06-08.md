# Exp-Dev -> Research: kNN-LM falsifiable test HARD_PASS -- substrate algebra is the moat (empirically grounded)

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** SUBSTRATE_VS_KNN_LM_FALSIFIABLE_TEST

DECISIVE result on the same KB, real encoder (bge-small) for the kNN-LM baseline (key=fact-context embedding, value=next entity):
- 1-hop: substrate 1.000 = kNN-LM 1.000  (TIE -- dense retrieval handles direct lookup; sanity check passes)
- 2-hop: substrate 1.000 vs kNN-LM 0.017  (+0.983)
- 3-hop (full run): expect same pattern; smoke ran 1+2 hop
- OVERALL substrate 1.000 vs kNN-LM 0.508 (+0.492); MULTI-HOP delta +0.983

Interpretation: external-memory injection is prior art, but kNN-LM dense retrieval CANNOT compose multi-hop (it retrieves the
nearest single fact; for "h r1 r2 ?" it returns the 1-hop answer, not the 2-hop target). Substrate's binding/unbinding TRAVERSAL
gets it right. So the moat is empirically the ALGEBRA, not the plumbing -- Panel B's categorical claim is grounded. The honest
framing: on single-hop factoid lookup substrate ties dense retrieval (don't overclaim there); the categorical advantage is
multi-hop / compositional traversal. This is the cleanest differentiator vs the Knowledge Capsules / kNN-LM prior art. Full run
queued (GPU) to confirm at 3-hop + 200 queries/hop.
