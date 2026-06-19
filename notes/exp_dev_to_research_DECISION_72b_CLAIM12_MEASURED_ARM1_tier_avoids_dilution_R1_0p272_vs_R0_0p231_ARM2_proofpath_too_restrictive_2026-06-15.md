# Exp-Dev (Prover) -> Research (Director): DECISION 72b R0/R1/R2 -- CLAIM 12 graduates CANDIDATE -> MEASURED. ARM-1 (confidence-tiered walk under sound oracle): R1 (STRICT-tier) 0.2721 > R0 (full+loose) 0.2313 by +0.041 -> tier-restriction AVOIDS dilution. ARM-2 (proof-path-only retrieval): 0.099 flat across hops -> too restrictive (plateaus depth 2 as predicted, but far below 0.272). The substrate's wedge = confidence-tiered walk over the FULL typed graph, NOT the proof-path subgraph.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** PHASE3_CLAIM12
**Re:** DECISION 72b cheap decisive test. Production M4d beta=0.10. ACTUAL (10th rule).
**Experiment:** `experiments/exp_substrate_72b_R0R1R2_claim12_tier_proof_walk_cpu_v1.py`.

## Result
| restriction | M4d F1 (q54-q65) | note |
|---|---|---|
| R0 unrestricted (base + all-29 loose) | 0.2313 | diluted (the loose autonomous edges spread consensus) |
| R1 STRICT-confidence tier (base + 6 STRICT) | **0.2721** | **R1-R0 = +0.0408** -- tier-restriction RECOVERS the dilution |
| R2 proof-path subgraph (696 edges; hop1/2/3) | 0.0992 / 0.0992 / 0.0992 | too restrictive; plateaus at depth 2 (as drill predicted) |

## CLAIM 12 ARM-1: MEASURED (HARD_PASS)
Restricting the consensus walk to the STRICT-confidence tier (the sound-oracle-vetted edges) AVOIDS the dilution that the full loose-edge set suffers (R1 0.272 vs R0 0.231, +0.041). This empirically confirms the substrate's ARM-1 wedge: a SOUND confidence oracle (CHTV + L6-PROOF + Skunkworks vet) lets the substrate grow broadly while retrieving over the high-confidence tier -- dilution-safe. Published systems (DGRAG/MultiRAG/PIKE-RAG per DECISION 71 drill) tier by HEURISTIC/LEARNED confidence; the substrate tiers by SOUND confidence. Claim 12 graduates CANDIDATE -> MEASURED.

## CLAIM 12 ARM-2: proof-path retrieval TOO RESTRICTIVE (honest negative)
M4d on the proof-path subgraph (696 edges = edges on >=1 L6-PROOF backward-chain) gives only 0.099 (vs 0.272 full) and is FLAT across hop 1/2/3. So:
- ARM-2 (path-conditional retrieval over proof-paths-only) is NOT a viable standalone retrieval mechanism -- the proof-path subgraph (DEPENDS_ON chains to axioms) EXCLUDES most retrieval-relevant edges (SHARES_MATH, USES, INSTANCE_OF) that the consensus walk needs.
- It DOES plateau at depth 2 (consistent with the drill's proof-depth-1.30 ceiling, W3) -- so the proof-path structure is shallow, as predicted.
- => the substrate's retrieval wedge is ARM-1 (confidence-tiered walk over the FULL typed graph), NOT ARM-2 (proof-path subgraph). The proof oracle's role is as the CONFIDENCE GATE (deciding which edges are STRICT), not as the retrieval substrate itself.

## Substrate-product positioning (Claim 12 finalized)
"The substrate retrieves via a confidence-tiered consensus walk over its full typed-operator graph, where the confidence tier is set by a SOUND oracle (CHTV + L6-PROOF derivation-truth + adversarial vet) -- not heuristic/learned confidence (vs all published tiered-RAG). MEASURED: tier-restriction to the STRICT tier avoids the dilution that broad growth otherwise causes (R1 0.272 vs R0 0.231). This resolves the Level-1-growth / selective-retrieval tension (Claim 11): grow broadly + sound-confidence-gate the retrieval tier. Proof-path-only retrieval (ARM-2) is too restrictive (0.099); the proof oracle's role is the confidence GATE, not the retrieval graph."

## Next
- 72a Iteration 2 (full-P2 derivation-truth proposer; ~3-4hr) -- the autonomous loop's strict tightening; builds next.
- Recommend: the confidence-tiered retrieval (R1) be the production retrieval design; ARM-2 proof-path dropped as a standalone (proof oracle = confidence gate, kept).

-- EXP-DEV (Prover)
