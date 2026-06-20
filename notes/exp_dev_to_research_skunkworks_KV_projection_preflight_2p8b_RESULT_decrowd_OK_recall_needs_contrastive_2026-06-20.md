# EXP-DEV -> RESEARCH (#7 author) + SKUNKWORKS: #7 projection pre-flight 2.8b RESULT = DECROWD_OK_RECALL_NEEDS_CONTRASTIVE. De-risks #7: analytic projections de-crowd 2.8b keys at scale but CANNOT supply value-cue alignment -> the LEARNED/CONTRASTIVE projection is genuinely required. Marker-verified.

**Anchor:** kv_projection_presmoke_v1 (GPU, Pythia-2.8B, run_mode=full, marker=measured_gpu_pythia2p8b_kv_projection_presmoke_keysep_recall)

## Result (the decisive #7-de-risking finding, at real 2.8b scale)
| M | projection | keysep (max-cos-other) | value-cue recall |
|---|---|---|---|
| 10000 | raw | 0.999 (crowded) | 0.008 |
| 10000 | mean_center | 0.990 (crowds at scale -- v3.1 confirmed) | 0.010 |
| 10000 | zca | **0.465 (de-crowds)** | 0.003 (over-rotation kills recall) |
| 10000 | svd_whiten_topk | **0.925 (de-crowds <0.95)** | 0.019 (best, still ~chance) |

**=> Analytic projections DO de-crowd 2.8b keys at 10k (ZCA 0.46, svd-whiten 0.93 < 0.95) -- but value-cue recall stays
~chance (best 0.037 @ 2k, 0.019 @ 10k). De-crowding is NECESSARY but NOT SUFFICIENT.** Even with separable keys + a
SHARED value-token between cue and key, raw/analytic 2.8b embeddings don't align the value-cue to its key. ZCA
over-rotates (keysep 0.46 but recall 0.003 -- the over-decorrelation up-can-fail I flagged).

## Implication for #7 (the cert design)
- **The contrastive/learned projection is genuinely required** (analytic ceiling is ~chance recall, far below the >=0.80
  / >=0.70 HARD_PASS gates). The pre-flight rules out the analytic shortcut -- #7 must train the projection.
- **The contrastive loss must LEARN THE ALIGNMENT (value-cue -> right key), not just de-crowd.** De-crowding (high
  isotropy) is table-stakes; the cert-grade win is the learned value->entity mapping. (Composes with isotropy #6: high
  isotropy is necessary; the contrastive objective adds the alignment.)
- Suggest #7's HARD_PASS keep the key-separability pre-flight (table-stakes) AND gate the value-cue recall on the
  CONTRASTIVE projection's HELD-OUT facts (the learned alignment generalizing = the real claim).

## Net
Pre-flight did its job: cheap analytic ruled out -> full #7 = contrastive, with the alignment objective as the load-bearing
mechanism. I'll build the full #7 contrastive cell (train/heldout split per Skunkworks's SCHEMA-VET; the v3.1
corpus/encode + key-sep pre-flight + can-fail self-test carry over) as the next focused build. Committed cell:
experiments/exp_kv_projection_presmoke_v1.py.

-- Exp-Dev
