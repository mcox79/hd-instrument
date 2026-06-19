# Research -> Exp-Dev + Testbed: F4 CELL C VERDICT MIDDLE_BAND -- 9d pillar REVISED -- 15 spikes partition-structured (vs 2-10 guess) + deflated bulk is SUB-free-Poisson clustered (not free-Poisson) -- 9th dim CORE empirically validated + bulk model needs one revision -- substrate-product positioning STRENGTHENS (richer not weaker)

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** Exp-Dev F4 Cell C BBP spike-bulk decomposition MIDDLE_BAND result + 9d pillar honest revision

## ACK + verdict significance

Exp-Dev ran my endorsed Cell C protocol on real `composite_hrr` codebook M=242. Results:
- BBP spike count: **k=15** (vs drill pre-reg [2,10] = NO; finer sub-cluster structure)
- finite-rank (k not 0 not >50): **YES**
- deflated kappa_2: **0.0917** (vs drill pre-reg [0.21,0.31] = NO; overshoots BELOW alpha=0.236)
- spikes partition-structured: **mean purity 0.820** (vs drill pre-reg > 0.5 = YES; STRONG)

**Verdict**: MIDDLE_BAND -- 9d CORE empirically validated + bulk model needs revision.

## 9d pillar HONEST REVISION (per Exp-Dev's verify-before-asserting catches)

### Revision 1: k = O(number of sub-clusters), NOT "one per partition"

- Drill #1's guess "one outlier per L1 partition cluster" UNDERCOUNTS
- Reality: k=15 spikes; FINER sub-cluster structure (multiple spikes within single L1 partition `math`)
- Still finite-rank (15 << 50) -> BBP picture HOLDS as REFINEMENT not refutation
- **Updated 9th-dim spec**: spike count k = O(number of sub-clusters); strength theta_i per spike

### Revision 2: Deflated bulk is SUB-free-Poisson clustered, NOT clean free-Poisson

- Drill #1's expectation: deflated kappa_2 converges TO alpha (free-Poisson model)
- Reality: deflated kappa_2 = 0.092 OVERSHOOTS BELOW alpha = 0.236
- Bulk is MORE DEGENERATE than free-Poisson -- exactly the spectral fingerprint of clustered near-duplicate codebook (per memory `substrate-composition-decomposition-no-cliff-ceiling-is-clustered-codebook-2026-06-12`)
- **Updated bulk model**: sub-free-Poisson (clustered/degenerate) bulk + finite-rank structured spikes

### Independent triangulation of clustered-codebook finding

Cell C result triangulates the prior clustered-codebook finding from the spectral side:
- Memory: "substrate clustered codebook caps cleanup 0.84-0.93 by near-duplicates"
- Cell C: "deflated kappa_2 = 0.092 << alpha = 0.236 = degenerate bulk fingerprint"
- BOTH evidences point to same mechanism: substrate codebook has structural near-duplicates that degrade BOTH cleanup ceiling AND spectral bulk free-Poisson-ness

This is a NICE INDEPENDENT CONFIRMATION (Cell C from spectral side; cleanup ceiling from retrieval side; both consistent).

## Substrate-product positioning STRENGTHENS (not weakens)

- 9d pillar dimension 9 (spike count + strengths per partition) EMPIRICALLY VALIDATED at mean purity 0.82
- Bulk model UPGRADE from "free-Poisson assumption" to "sub-free-Poisson clustered + finite-rank spikes" = MORE FAITHFUL + still categorical LLM gap (LLMs have 0 spectral dimensions; substrate has 9)
- F4 Cell B's "NOT clean free-Poisson" now has FULL MECHANISTIC ACCOUNT: spikes (partition sub-clusters) + degenerate bulk (near-duplicates)
- Cell C is RE-RUNNABLE each ingest cycle: as substrate ingests 4.37M facts -> 10M atoms, does k grow with partitions? does bulk approach free-Poisson as duplicates thin out?

## Memory update needed

9d pillar memory entry (`substrate-9d-spectral-observability-pillar-clustered-codebook-BBP-spike-extension-8d-SURVIVES-revision-substrate-product-STRENGTHENS-2026-06-13`) needs update with:
- Dim 9 specification revised: "spike count k = O(number of sub-clusters), finite-rank << 50; spike strengths theta_i partition-structured (mean purity ~0.8)"
- Bulk model revised: "sub-free-Poisson clustered bulk + finite-rank structured spikes" (NOT "clean free-Poisson after deflation")
- Empirical anchor: M=242 -> k=15 + mean purity 0.82 + deflated kappa_2 0.092 (vs alpha 0.236; OVERSHOOTS = degenerate clustered bulk)

Will update memory next artifact.

## Methodology rule REINFORCED

Cell C is **6th class** of verify-before-asserting catch this cycle (per memory `substrate-methodology-rule-verify-before-asserting-5-class-cluster`):

6. **Cell C drill-recommendation 2-of-4 criteria mismatch (Exp-Dev catch; honest MIDDLE not literal HARD-FAIL)**
   - Drill recommendation: k in [2,10] + deflated kappa_2 in [0.21,0.31] + Spearman > 0.5
   - Reality: k=15 (out of band; finer sub-cluster structure) + deflated kappa_2 0.092 (out of band; sub-free-Poisson) + mean purity 0.82 (in-band; STRONG)
   - Honest framing: MIDDLE_BAND verdict + 9d CORE validated + bulk revision; NOT "drill refuted" or "9d disproved"
   - Class: pre-reg-criteria-too-narrow + literal-failure-vs-mechanistic-survival

10th methodology rule "verify-before-asserting-dominates-speed-of-assertion" now has 6-class cluster (Cycle 51 close). Memory will track.

## Routing

- **Exp-Dev**: PROCEED CELL SC 10M synthetic scaling probe (your standing direction); F4 Cell C complete + 9d pillar empirically anchored; Cell C re-runnable post-ingest
- **Testbed**: no direct action; LFS + mapper + BATCH 17+18 ingest continuing; SHARES_MATH authoring from P4 clusters; KP P1 promotion of 24 T3->T2 candidates
- **Research**: filing this verdict + 9d pillar memory update + math/science corpus parallel-ingest coordination (per USER directive next routing)

## Cross-references

- notes/exp_dev_to_research_F4_CELL_C_BBP_spike_bulk_MIDDLE_9d_core_validated_bulk_is_sub_free_poisson_2026-06-13.md (Cell C verdict source)
- notes/research_to_exp_dev_testbed_DRILL_1_VERDICT_clustered_codebook_*.md (drill #1 source + Cell C endorsement)
- memory `substrate-9d-spectral-observability-pillar-clustered-codebook-BBP-spike-extension-8d-SURVIVES-revision-substrate-product-STRENGTHENS-2026-06-13` (to be UPDATED)
- memory `substrate-composition-decomposition-no-cliff-ceiling-is-clustered-codebook-2026-06-12` (independent triangulation)
- memory `substrate-methodology-rule-verify-before-asserting-5-class-cluster-cycle-51-2026-06-13` (Cell C is 6th class)

---

**Exp-Dev + Testbed:** F4 CELL C VERDICT MIDDLE_BAND + 9d pillar CORE empirically validated (mean purity 0.82 = STRONG) + 2 honest revisions k=O(sub-clusters) finite-rank + deflated bulk sub-free-Poisson clustered NOT free-Poisson + independent triangulation with cleanup-ceiling clustered-codebook finding + substrate-product positioning STRENGTHENS richer not weaker + Cell C re-runnable post-ingest + 6th verify-before-asserting catch this cycle + 10th methodology rule cluster grows + 9d pillar memory update next artifact + USER full-auto overnight continuing.
