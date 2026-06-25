# Cell H spec — extended-depth multi-hop via consolidation + cleanup-every-step + multi-W per-depth

Director pre-authored cell spec; USER directive: "cleanup every hop should extend to much more hops, with memory should make even better right? and could even store every hop iteratively or multiple storage vectors?"

Validated by today's anisotropic encoder drill: Cell 4 consolidation integration has P_deflated=0.55, the highest of any Stage 1.5 path. **Lane A: build on Cell 4's breakthrough rather than chase encoder rabbits.**

## Strategic

Cell 4 (Wave E multihop_consolidation) just landed HARD_PASS at **CONS_IMMEDIATE top1=1.000 vs NAIVE 0.847 (lift +0.153)** for 2-hop. The mechanism: when a 2-hop chain is traversed, write a direct compound atom `bind(A, R_compound_R1R2, C)` into W. Multi-hop becomes 1-hop chain-grade.

USER extension (this turn): combine three insights to go to DEEP multi-hop (K=5, 10, 50+):

1. **Cleanup-every-step (Store-proven)**: Wave14R K50 at N=16384 already chain-grade at acc_1=0.987, acc_5=0.913, acc_50=0.487 with per-step cleanup
2. **Consolidation memory primitive (Cell 4)**: frequent paths → direct compound atoms
3. **Iterative hop storage (USER idea)**: don't just consolidate 2-hop; consolidate at EVERY depth k=1,2,3,...K. Each consolidated atom is a "shortcut" at depth k
4. **Multiple W matrices per depth (USER idea)**: separate W_1, W_2, W_3, ..., W_K — each storing the compound atoms for THAT specific hop depth

Combining gives: substrate retrieves at depth k by querying W_k directly (1-hop in W_k space, even though it represents k-hop in concept space). For depths not yet consolidated, fall back to cleanup-every-step traversal.

Brain analog: HIERARCHICAL TIME-SCALE memory.
- Hippocampus = cleanup-every-step (working memory; novel sequences)
- Posterior cortex = consolidated 1-2 hop shortcuts (recent semantic)
- Anterior cortex (ATL) = highly consolidated multi-step shortcuts (longstanding semantic)
- Each region operates at different timescale + storage capacity

## Cell anchor

`substrate_multihop_extended_depth_consolidation_per_hop_W_v1`

## Lane / routing / config

- Lane 1 (substrate-native; no LLM)
- Routing: remote_cpu_queue (matmul-heavy at depth but no per-step training; should fit in CPU)
- Config: V_C=200, V_P=10, N=8192, K_SET=20, n_chains_per_depth=200, K_max=10 (test depths 1, 2, 3, 5, 10), 3 seeds [7,17,23]
- Storage: K_max=10 separate W matrices (W_1 through W_10); each O(V·N) sparse-bipolar

## Arms (6; one knob = mechanism)

1. **ARM_NAIVE_HARD_KHOP** (control; reproduces last night's beta-sweep 0.65 at 2-hop, and Wave14R-equivalent at 5-hop)
2. **ARM_CLEANUP_EVERY_STEP_NO_MEMORY** (Wave14R K50 mechanism reproduced; cleanup at each hop but no compound atoms; chain-grade-eligible at depth K=50 per Store)
3. **ARM_CONSOLIDATE_DEPTH_K2_ONLY** (Cell 4 mechanism reproduced; consolidate only 2-hop pairs)
4. **ARM_CONSOLIDATE_PER_DEPTH_PARALLEL_W** (USER's idea: K separate W_k matrices; each consolidates at depth k for ALL traversed chains of that depth)
5. **ARM_HYBRID_CLEANUP_PLUS_PARALLEL_W** (combines ARMS 2 and 4: cleanup for unconsolidated, parallel W lookup for consolidated)
6. **ARM_HYBRID_PLUS_THRESHOLD** (above + K_THRESH=3 frequency threshold for consolidation; resource-efficient real-world variant)

## Per-arm metric (test at K depths 1, 2, 3, 5, 10)

- top1 at each depth
- top5 at each depth
- per-hop retention rate (top1[k] / top1[k-1])
- consolidation memory usage (atoms stored per W per depth)
- retrieval wall time at each depth

## HARD bands

- **HARD_PASS_BREAK_CEILING_K10**: ARM_HYBRID or ARM_PARALLEL_W achieves top1[K=10] ≥ 0.85 (Wave14R K50 retains 0.487 at K=50; this band is intermediate)
- **HARD_PASS_DEPTH_RETENTION**: per-hop retention rate ≥ 0.95 (each hop loses ≤ 5% of accuracy; brain-aligned exponential retention)
- **HARD_PASS**: ARM_HYBRID beats ARM_CLEANUP_EVERY_STEP at K=5+ by ≥ 0.10
- **HARD_FAIL**: ARM_HYBRID within ±0.03 of ARM_CLEANUP_EVERY_STEP (parallel-W consolidation doesn't add value over pure cleanup)

## Discriminators (load-bearing per Fix #28)

- **Memory primitive value**: ARM_3 vs ARM_2 — does CONSOLIDATE alone help past 2-hop? (Cell 4 proved 2-hop; here we test K=3, 5, 10)
- **Parallel-W value**: ARM_4 vs ARM_3 — does per-depth W storage scale better than single-W consolidation?
- **Hybrid value**: ARM_5 vs ARM_4 — does cleanup add anything when parallel-W consolidation exists?
- **Threshold value**: ARM_6 vs ARM_5 — does K_THRESH=3 frequency gating preserve performance while reducing storage cost?

## Sanity rails

- ARM_NAIVE_HARD_2HOP must reproduce ~0.65 (or 0.847 per Cell 4 harness; sanity-rail check on which baseline regime)
- ARM_CLEANUP_EVERY_STEP_K50 should approach Wave14R K50's acc_50=0.487 within ±0.05 (cross-validates the Store cell at this regime)

## Storage cost analysis

| Arm | Storage cost at K_max=10 | Scaling |
|---|---|---|
| ARM_NAIVE | 1 × W (single) | O(V) atoms |
| ARM_CLEANUP | 1 × W | O(V) atoms |
| ARM_CONSOL_K2 | 1 × W + 1 W_2hop_cache | O(V²) at worst |
| ARM_PARALLEL_W | K × W (one per depth) | O(K·V·#chains) atoms |
| ARM_HYBRID | K × W | O(K·V·#chains) |
| ARM_HYBRID_THRESHOLD | K × W (sparse) | O(K·V_frequent) — much smaller |

Storage cost is REAL — at K=10 V=200 #chains=200, parallel-W needs 200·200·10 = 400k compound atoms. At N=8192 sparse_f=0.02, that's ~1.6M nonzeros per W; 10 Ws = 16M nonzeros total. Memory budget: ~128MB. Feasible.

## Timeout

3600s (CPU; no training, pure storage + retrieval)

## Cross-thread

Depends on Cell 4 (consolidation 2-hop) chain-grade tier ruling from Skunkworks (in flight). If Cell 4 ruled MM-by-construction, the parallel-W extension is also at risk of by-construction tier. If Cell 4 ruled CHAIN_GRADE, this cell tests the extension.

Per drill `notes/research_optimal_anisotropic_encoder_construction_5x_drill_2026-06-25.md`: this is Lane A (Barrier 1 via memory primitive). Highest P_deflated of any Stage 1.5 path (0.55). Build on Cell 4's breakthrough.

## Skunkworks pre-emptive flag

- **By-construction concern**: ARM_PARALLEL_W stores the answer pre-encoded at every depth. If consolidation is "trivially perfect by construction," tier should be MM. Discriminator: does the STORAGE COST analysis show genuine compute/memory tradeoff that suggests substantive architecture (not just "memorize everything")?
- **Sanity-rail**: NAIVE_HARD_KHOP at the cell's harness needs to match either last night's beta-sweep (0.65 at K=2) OR Cell 4's harness (0.847 at K=2). Document which.

## Substrate-product implications

If HARD_PASS:
- Substrate-product story: substrate can do K=10 hops at chain-grade with per-depth consolidated memory + threshold-gated frequency
- Brain alignment: hierarchical timescale memory (HC + posterior + ATL); each layer at different consolidation depth
- Storage-vs-compute tradeoff: substrate sacrifices storage (K × W) for compute (1-hop direct retrieval) — opposite of transformer's compute-heavy attention
- Multi-modal extension: parallel W matrices natural for multi-modal sources (W_text, W_image, W_graph all retrieved at consolidated 1-hop)

If HARD_FAIL:
- Multi-hop ceiling at K>2 is MORE FUNDAMENTAL than 2-hop ceiling — consolidation doesn't scale
- Pivot to D-prime hybrid encoder (Lane B per drill)

## Dispatch sequence (proposed)

1. Wait for Skunkworks tier ruling on Cell 4 (in flight) to confirm consolidation is genuine
2. Wait for Wave F bug fixes to land (4 cells reauthored) so we have clean push-lane evidence
3. Then dispatch Cell H

OR — dispatch in parallel if compute available (remote CPU is idle; this cell would saturate it during fix-and-redispatch of Wave F).

## Status

NOT dispatched. Awaiting USER green-light + Skunkworks tier ruling on Cell 4.
