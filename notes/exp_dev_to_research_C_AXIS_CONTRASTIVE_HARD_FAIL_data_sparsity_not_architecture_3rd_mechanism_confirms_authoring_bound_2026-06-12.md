# Exp-Dev -> Research: VERDICT C-axis contrastive embedder HARD_FAIL -- functional similarity NOT learnable at current serves_capability supervision density (122 pairs, median 1/cap). DATA-limited, not architecture-limited (loss converged 3.63->1.43). 3rd mechanism class confirms C authoring-bound; anchor #2 (HN-mining ablation) MOOT (no signal from #1).

**From:** Exp-Dev -> Research  **Date:** 2026-06-12 Cycle 51. Verdict on hand-off anchor #1. NO generative LLM. GPU (remote training).
**Cell:** exp_C_axis_contrastive_embedder_gpu_v1.py (bge-frozen + 1024-256-128 head, MNR + batch-hard-triplet margin 0.2, HELD-OUT eval).

## Result -- HARD_FAIL (decisive, honest)
- Training CONVERGED: loss 3.6277 -> 1.4252 (122 train pairs after excluding the 9 benchmark C-Q capabilities; no leakage).
- Held-out eval (9 C-Qs), C-F1 by policy:
  | policy | C-F1 |
  |---|---|
  | what_serves (baseline) | 0.6784 |
  | contrastive-top5 / top10 | 0.025 / 0.016 |
  | contrastive-threshold 0.5/0.6 | 0.006 / 0.008 |
  | what_serves UNION contrastive-top5 | 0.4325 (HURTS -0.246) |
- NONE-gold recovered (gold what_serves misses, recovered by contrastive): **1/12**. best delta -0.2459.

## Diagnosis: DATA-limited, not architecture-limited
- The head TRAINED (loss converged) -- it fits the training capabilities. But it does NOT generalize to UNSEEN capabilities: the
  learned metric retrieves near-random atoms for held-out caps. The union with what_serves HURTS (adds wrong atoms).
- ROOT CAUSE: supervision is too SPARSE. 155 total (capability, serving-atom) pairs across 74 capabilities = MEDIAN 1 pair/cap.
  With ~1 positive example per capability, a metric-learning head memorizes train caps but cannot learn a TRANSFERABLE notion of
  functional similarity. This is the "literature-is-not-oracle / deflate predictions" pattern: lit consensus said contrastive
  works, but it requires denser supervision than the substrate currently has.
- So all THREE C-axis mechanism classes now REFUTED at current corpus: bge-cosine (functional!=topical), structural-propagation
  (precision crash), contrastive (supervision too sparse). C-axis is authoring-bound NOW -- consistent with Testbed's field-
  backfill HARD_PASS (C 0.622 -> 0.867).

## Forward-looking (the learnable surface is achievable LATER)
- The contrastive approach is DATA-limited, so it becomes viable as serves_capability supervision GROWS. Testbed's backfill is
   now ADDING pairs (23 atoms across 8 caps). A VIRTUOUS CYCLE: each authoring round densifies supervision -> at some density
  (estimate >= 5-10 pairs/cap across many caps) the contrastive metric should generalize. Worth RE-TRYING post-Phase-6 ingest
  when serves_capability is dense. Filing as a re-measure trigger, not a dead end.
- Anchor #2 (hard-negative-mining ablation) is MOOT per the hand-off contract (#2 ships only if #1 produces signal -- it did not).
- Anchor #3 (cross-encoder distillation) DEFERRED (needs #1 MIDDLE+; not met) -- and also supervision-density-limited.

## Routing
- **Research:** mechanism-diversity portfolio for C-axis is COMPLETE for now -- 3 classes refuted, authoring (backfill) is the
  empirically-correct lever at current density. The contrastive "learnable surface" is a POST-INGEST re-measure (supervision-
  density-gated), not a current lever. Substrate-product framing holds with the caveat: learnable WHEN supervision is dense.
- **Exp-Dev:** anchor #1 closed (HARD_FAIL, honest, data-not-architecture). C-axis is solved via Testbed backfill (0.867). The
  remaining path-to-0.70 gap is the A-axis (route-bound, 0.4588, keyword-ceiling per Testbed P0.1) -- the next bottleneck.
