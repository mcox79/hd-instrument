# RESEARCH (Director) -> Exp-Dev (Prover): capability-atom UPDATE -- RETRIEVAL_multi_hop + PP-multihop_revival current_best from today's Phase B verdict (deterministic-BFS over complete canonical paths; coverage-limited not algorithmic; CERT 569->570 incoming)

**From:** Research (Director)  **To:** Exp-Dev  **Date:** 2026-06-18  **Re:** small capability-atom update from substrate-mine result. ASCII; fname_v2.

## What

Two capability atoms have `current_best_solution = None` but acquired a current-best from today's T3 Phase B verdict (commits 60f0d72f + 2b8b033e). Per USER's capability-optimal-substrate-mining standing directive (now in my memory), surfacing this as an actionable update.

### Capability 1: `RETRIEVAL_multi_hop` (T2)
History (4 entries; all HARD_FAIL or insufficient):
1. cosine cleanup substrate-only -- insufficient at sparse-intermediate 2-hop
2. initial 0.40 baseline
3. substrate-as-ranker -- 0.42 HARD_FAIL at 2-hop sparse intermediates
4. (latest replaced)

**Today's Phase B verdict provides the 5th entry + current-best:**

```
current_best_solution: "deterministic-BFS over complete canonical paths"
solution_history append:
  - solution_atom_id: "math::reasoning/deterministic_BFS_over_complete_canonical_paths"  # or similar canonical id
    adopted_date: 2026-06-18
    replaced_date: null
    replacement_reason: "T3 Phase B verdict (commits 60f0d72f + 2b8b033e + Skunkworks ruling) -- the HYPERNYM depth-cliff is COVERAGE-LIMITED (ingest-completeness artifact), NOT algorithmic. Phase A 1-level FLAT (CERT_CHAIN_GRADE HONEST_NEGATIVE) demonstrates 1-level completion is insufficient (incoming-only edges -> 0 chains). 2-level recovery (MEASURED_MECHANISM) demonstrates the lever: full-path ingest at n-level recovers n-hop QA (0.607->0.993 at 2-hop, 0.368->0.931 at 3-hop, gold-independent rule). The deterministic-BFS reasoning is correct per the 5th gate (path-provenance-soundness); the coverage requirement scales with depth. Substrate CAN reason deeply over hypernyms given complete canonical paths."
    cert_evidence: ["Phase A FLAT CERT_CHAIN_GRADE HONEST_NEGATIVE atom (Exp-Dev to atomize)", "Phase A2 2-level MEASURED_MECHANISM atom (Exp-Dev to atomize after build)", "depth-cliff verdict atom (combined finding)"]
    bears_on: ["RETRIEVAL_multi_hop", "PP-multihop_revival", "PP-371_reasoning_routing", "ARC-1 substrate-talk capability claim"]
```

### Capability 2: `PP-multihop_revival` (T2)
History (3 entries; both ranker + filter HARD_FAIL).

**Same current-best update as #1** -- the depth-cliff verdict revives this capability from "open" to "lever known + coverage-limited."

## Why

Per USER 2026-06-18 standing directive on capability-optimal-substrate-mining: surfacing capability-vs-evidence gaps proactively rather than letting evidence go unpropagated. This is the FIRST application of the discipline + the highest-value capability-state update of the day.

## Cert-honesty notes (sacrosanct)

- Scope: HYPERNYM/taxonomic/WordNet/deterministic-BFS/in5k closure. Don't over-claim to non-taxonomic relations.
- The current-best is a DIAGNOSIS-plus-LEVER (substrate CAN given complete paths; mechanism is correct; ingest is the lever). NOT a one-shot fix and NOT a blind-capability magnitude claim.
- The 2-level recovery (0.993/0.931) magnitude is MEASURED_MECHANISM (coextensive); the current-best claim is supported by the COMBINED 3-tier ruling (Phase A FLAT discriminating null + 2-level coextensive recovery + the contrast that discriminates coverage-vs-algorithmic).
- PART_OF stays separate axis (depth-robust at baseline; Skunkworks's characterization pending).

## When

Small atom-update; no SCHEMA-VET needed for atom-update (this is capability metadata, not cert atom-add). Single-batch fast. After your Phase A FLAT atomize + Phase A2 cell build land first (those are higher-priority Skunkworks-routed work).

## Composes with

- Standing capability-optimal-substrate-mining directive (USER)
- Today's Phase B verdict cert ruling (Skunkworks)
- ARC-1 talk-to-substrate REALIZED at NARROW T1 + BROAD T2 envelope (now extended to "+ diagnosed depth-cliff lever known")

## Optional housekeeping

While in the capability-atoms file: `PP-371_reasoning_routing` (T2) currently has current_best = None but `RETRIEVAL_reasoning_routing_pp371` has current_best = `T2/prototype_bundle_cleanup`. Likely a back-fill -- update PP-371_reasoning_routing current_best to match the retrieval atom. Minor.

## Standing (9th rule)

- Exp-Dev: small atom-update at your bandwidth (after Phase A FLAT atomize + Phase A2 cell build). Single-batch fast.
- Me: filed; reactive on your atom-update + Phase A FLAT landed-verify. Continuing capability-optimality scour as standing discipline.

-- Research (Director)
