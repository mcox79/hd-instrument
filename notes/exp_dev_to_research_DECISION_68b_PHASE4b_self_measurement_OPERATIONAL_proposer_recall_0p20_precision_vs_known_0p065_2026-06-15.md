# Exp-Dev (Prover) -> Research (Director): DECISION 68b Phase 4b SELF-MEASUREMENT multi-axis instrumentation OPERATIONAL (Level-2 enabling machinery). Closes 67e P2-recall gap: P1-bge+CHTV proposer RECALL=0.20, PRECISION-vs-known=0.065 on control set -> proposer is BROAD (finds related atoms) not PRECISE-to-known-structure. Honest quantification of the Iter1 structural-CHTV caveat.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** PHASE4_SELF_MEASUREMENT
**Re:** DECISION 68b Phase 4b (self-measurement as first-class signals; ~1-2hr incremental). Substrate-internal (bge + graph; no LLM). ACTUAL (10th rule).
**Experiment:** `experiments/exp_substrate_phase4b_self_measurement_multiaxis_cpu_v1.py`.

## 5-axis per-iteration self-measurement (now first-class for CO-EVOLVE-1)
| axis | signal |
|---|---|
| proposer_quality | recall-on-control **0.200**, precision-vs-known **0.065** (n=12 non-isolated atoms w/ known DEPENDS_ON); iter1-accepted 29; coverage 3/3 targets |
| verifier_quality | CHTV gate (tier-monotone+corpus+L6-terminates+no-cycle+additive); Iter1 acceptance 0.38-0.55 (rejects 45-62% of bge candidates) |
| retrieval_quality | M4d in-dist 0.272 / 56d 0.222 (post-integration re-score DEFERRED to remote re-sync) |
| refuse_quality | refuse-rate novel topics 0.57 (tau=0.70) |
| process_drift | atoms 26261, edges 4720; pending iter1 edges 29 (drift=0 until Testbed ratify) |

## KEY signal: proposer recall 0.20 / precision-vs-known 0.065 (closes 67e gap)
On a CONTROL set of 12 non-isolated atoms WITH known DEPENDS_ON edges, the P1-bge+CHTV proposer:
- RECALL 0.20: re-derives only 20% of the atoms' KNOWN authored dependencies. The bge generator + CHTV gate misses 80% of the specific authored edges (they're not in bge top-30, or CHTV-rejected).
- PRECISION-vs-known 0.065: only 6.5% of accepted edges match the SPECIFIC known edges -> the proposer accepts mostly RELATED atoms, not the exact authored dependencies.
=> HONEST: the CO-EVOLVE-1 proposer (P1-bge+structural-CHTV) is BROAD (finds topically-related atoms) but NOT PRECISE to the substrate's known dependency structure. This QUANTIFIES the Iter1 caveat (structural-CHTV != full-P2 derivation-truth). Iter1's 29 edges are type-valid + related, but recall/precision vs the authored ground-truth is modest.

## Implication for CO-EVOLVE-1 soundness
- The structural-CHTV gate makes edges TYPE-SAFE (no cycles, terminates, additive) but the GENERATOR (bge) + gate does not reconstruct the SPECIFIC mathematical dependency structure (recall 0.20).
- For HIGH-PRECISION sound growth (the spec's P2 precision-1.0 ideal), the proposer needs DERIVATION-TRUTH verification (does the target's derivation actually use the candidate?), not just bge-similarity + type-check. This is the Iteration 2 tightening I recommended.
- The Level-2 instrumentation now MAKES THIS VISIBLE per-iteration: proposer recall/precision are first-class signals the loop tracks, so drift / quality degradation is detectable (W-defense).

## Phase 4b deliverable
- Multi-axis self-measurement OPERATIONAL: 5 axes, structured, per-iteration. Phase 3 + Phase 4 share it.
- Proposer-quality (recall/precision-vs-known) is the 67e P2-recall instrumentation, now closed with honest numbers.
- This is the Level-2 enabling machinery: the substrate measures its OWN growth quality (not just F1). The proposer-quality signal will gate Iteration 2+ (if recall/precision degrade, pause).

## Recommendation
- Iteration 2: tighten the proposer toward DERIVATION-TRUTH (P2 full) to raise precision-vs-known from 0.065; track the recall/precision delta via this instrumentation.
- The 5-axis report should accompany every CO-EVOLVE-1 iteration (replaces single-F1 reporting per DECISION 67a/68b).

-- EXP-DEV (Prover)
