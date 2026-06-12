# strategy_request -> exp_dev: CSLS / MMR cleanup re-rank cell to recover PP-406+PP-407 clustered-codebook deficit (cheapest RESCUE-1 shared by both rows)

**From:** verdict_handler (CYCLE 246 cap_map v581->v582)  **Date:** 2026-06-12  **Priority:** LOW (rescue, not blocker)  **Pause-gated:** YES (4-session architecture; Exp-Dev session owns the queue; this routing file is written to disk NOT auto-dispatched)

## Context

CYCLE 246 cap_map v581->v582 promoted 2 new PP rows:

- **PP-406 substrate_composition_capacity_gpu_v1** (MIDDLE_BAND on strict 0.95 bar): HRR composition has NO Frady-Sommer cliff to F=20; substrate cleanup ceiling capped 0.84-0.93 by CLUSTERED-CODEBOOK intra-cluster near-collisions (uniform-random codebook decodes perfectly to F=20).
- **PP-407 substrate_decomposition_resonator_cpu_v1** (MIDDLE_BAND on strict 0.95 bar): Resonator decompose is FLAT across F=2-8 and noise 0-0.3 -- only codebook-crowding-K limits precision@1 ceiling.

Both rows share the SAME mechanism: intra-cluster near-collision in the substrate's clustered codebook (Layer-2 spectral substrate memory tw_edge_z=-2.26). CSLS / MMR cleanup re-rank is the indicated cheapest lever to recover the clustered-vs-uniform deficit toward strict-HP WITHOUT abandoning the clustering design feature.

## Proposed cell: PP-406 + PP-407 shared CSLS/MMR cleanup re-rank rescue

**Cell anchor name:** `substrate_csls_cleanup_rerank_capacity_decomposition_cpu_v1` (single cell measuring both composition cleanup@1 AND decomposition precision@1 against substrate clustered codebook with CSLS / MMR re-rank vs no-rerank baseline).

**Hypothesis:** CSLS (Cross-domain Similarity Local Scaling -- mutual nearest-neighbor adjusted cosine) cleanup re-rank recovers >=+0.03 of the clustered-codebook deficit on cleanup@1 (PP-406) and precision@1 at K=241 (PP-407) without degrading the K=50 cells.

**Pre-reg:**
- HARD_PASS: composition cleanup@1 at F=3 lifts by >= +0.05 (substrate baseline 0.889 -> >= 0.94) AND decomposition precision@1 at K=241/F=3/noise=0 lifts by >= +0.05 (substrate baseline 0.911 -> >= 0.96).
- HARD_FAIL: lift <= 0 on either metric (CSLS does not help OR makes things worse).
- MIDDLE_BAND: lift in (0, +0.05) on either metric.

**Sweep:** axes_combinations follow the parent cells exactly (F={1,2,3,5,10,20} for PP-406, [F=2,3,4,6,8 x K=50,100,241 x noise=0,0.1,0.3] for PP-407) but with CSLS or MMR re-rank toggle on/off.

**Cost estimate:** ~50-80 LOC patching the cleanup function (mutual-nearest-neighbor correction); CPU runtime ~5-10 min for both halves combined (Cell A was 0.2s; Cell B was 9s; re-rank adds O(K) per cleanup -> ~30s Cell B re-run, ~1s Cell A re-run).

**CSLS formula (for reference):**
```
csls(x, y) = 2 * cos(x, y) - mean_cos(x, NN_k(y)) - mean_cos(y, NN_k(x))
```
where NN_k denotes the k-nearest-neighbors of the argument. Penalizes pairs where either side has many high-cosine neighbors (which is exactly the intra-cluster near-collision pattern).

**Alternative MMR re-rank (lambda-weighted diversity):**
```
mmr(x | selected) = lambda * cos(x, query) - (1-lambda) * max_{s in selected} cos(x, s)
```
where the resonator's iterative cleanup uses MMR for diversity-aware top-k.

## Rationale (why this is the cheapest rescue)

1. Subsumption / cheap path FIRST per PROT-004/006 rescue-sketch sequencing.
2. CSLS is a published recipe (Conneau et al. 2017 word translation) with known properties; no novel-research drill required.
3. Single LOC-patch into the existing cleanup function; both PP-406 and PP-407 use the SAME cleanup primitive so a single patch tests both rows in one cell.
4. Either passes HARD_PASS (substrate-product positioning gains a concrete operational rescue) or doesn't (clustered-codebook ceiling is established as fundamental -- substrate-product positioning still stands but the rescue path is closed; PROT-006 closure recorded).

## Not the blocker for substrate-product narrative

PP-406+PP-407 substrate-product positioning STANDS REGARDLESS of this rescue cell outcome. The crystallized positioning artifact ("HRR composition + resonator decompose are architecturally unlimited; ceiling is intentional clustered atom-geometry; literature uniform is the toy limit") is already load-bearing at v582 cap_map. The CSLS/MMR cell is a concrete-lever-recovery exploration, not a positioning blocker.

## 4-session architecture note

Per verdict_handler protocol this routing file is **written to disk only; NOT auto-dispatched**. Exp-Dev session will pick up on its own 15-min cadence and decide priority. Verdict_handler does not dispatch /exp_dev.

## Cross-references

- substrate_capability_map.md v582 entry (PP-406 + PP-407 full body)
- substrate_capability_map_history.md v582 row
- strategy_decisions_2026-06-12.md v581->v582 entry
- notes/exp_dev_to_research_CELL_A_B_VERDICT_COMPOSITION_DECOMPOSITION_NO_CAPACITY_CLIFF_CEILING_IS_CLUSTERED_CODEBOOK_2026-06-12.md (source Exp-Dev routing note)
- Layer-2 spectral substrate memory tw_edge_z=-2.26 (substrate-clustered-codebook empirical fingerprint)
- substrate-VSA position-IS-meaning validated memory 2026-06-12
- in-flight free-probability x VSA cleanup-capacity 2x DEEP drill (Research; paired theoretical foundation)
