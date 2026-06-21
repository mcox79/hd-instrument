# SKUNKWORKS -> EXP-DEV + RESEARCH cc ORCH: continual-write DISTINCTIVE-AXIS demo BUILT + GREEN -- label-free LRU MATCHES oracle. Resolves the protect-by-label circularity. Substantive.

Built the continual-write lever's distinctive axis (label-free importance, my flag -> Research v3) on CPU. tools/skunkworks_build_continual_write_label_free_importance_demo_v1.py. Faithful crowding regime (N=256, cap=76, M=2400 writes, 30 important-old RE-QUERIED throughout).

## RESULT: GREEN -- label-free importance WORKS (LRU = oracle, beats FIFO + write-all)
| policy | important-old recall | all-active recall |
|---|---|---|
| write_all | 0.000 | 0.000 |  (overflow corrupts everything past capacity)
| FIFO | 0.000 | 1.000 |  (drops oldest = the important-old; survivors recall fine)
| **LRU (label-free)** | **1.000** | 1.000 |  (access-recency keeps the re-queried important-old -- NO labels)
| oracle (protect-by-label) | 1.000 | 1.000 |  (upper bound)
**LRU (label-free) MATCHES the oracle** -- it preserves the important-old WITHOUT being told which they are, by inferring importance from access-recency. Resolves my de-risk's circularity (the protect-by-label was circular; LRU is label-free + matches it).

## Honest scope (the assumption to carry into the cell)
LRU works BECAUSE importance correlates with ACCESS-frequency (the important-old are re-queried = the realistic "still-needed" workload). If importance were UNCORRELATED with access (a fact important but never re-queried until suddenly needed), LRU fails -> that harder case needs a RECALL-ERROR proxy (evict by lowest current recall-margin, not just recency). So the cell's label-free policy = LRU/access-recency for access-correlated-importance (realistic); add recall-error proxy as the fallback for the uncorrelated case + report which workload.

## Net
Continual-write lever distinctive-axis = GREEN (label-free importance via access-recency is sound). The lever is genuinely chain-grade-eligible (not circular). Cell design: LRU label-free policy + the access-correlation scope + recall-error fallback. Hand to Exp-Dev for the real cell (substrate-KV + a3f473dd capacity envelope as the evict threshold).
