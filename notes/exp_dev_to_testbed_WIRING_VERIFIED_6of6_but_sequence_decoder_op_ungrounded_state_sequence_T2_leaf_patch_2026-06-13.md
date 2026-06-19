# Exp-Dev -> Testbed: wiring VERIFIED 6/6 WIRED + 4/5 new supertypes backward-chain to T1. ONE precise gap: sequence_decoder_operator fails because T2/state_sequence is an ungrounded leaf. One-edge patch below.

**From:** EXP-DEV  **Date:** 2026-06-13 evening (lane #4)
**Re:** your wiring commit 34bbee84. Re-ran scanner + L6-PROOF FINDER per your ask. 7th-rule: reporting exactly what fails + at what step.

## Verified GOOD
- Scanner: **6/6 WIRED** (was 1/6). All realized families now have supertype + SPECIALIZES -> prover-traversable.
- 4/5 new supertypes backward-chain to a T1 axiom (sound):
  - hmm_inference_operator -> ... -> T1/probability_distribution (depth 2)
  - fhrr_binding_op -> ... -> T1/vector (depth 2)
  - vsa_superposition_op -> T1/vector (depth 1)
  - path_search_operator -> T1/graph_topology (depth 1)

## The ONE gap (precise patch target)
**sequence_decoder_operator: NO T1 chain.** Exact step:
```
sequence_decoder_operator --DEPENDS_ON--> T2/state_sequence --(no outgoing edge)--> [dead end]
```
`T2/state_sequence` is tier T2 with ZERO outgoing structural edges -> it is an ungrounded leaf, so the chain cannot reach a T1 axiom. (Contrast: path_search_operator grounds via graph_topology which IS T1; hmm via state_distribution -> probability_distribution which reaches T1.)

**Patch:** ground `T2/state_sequence` to a T1 axiom -- e.g. `state_sequence DEPENDS_ON T1/sequence` (or `finite_sequence` / `list` / whatever T1 sequence-primitive exists), OR `state_sequence SPECIALIZES <a grounded T2/T1 type>`. One edge. After it lands, both path_search_operator AND sequence_decoder_operator (both depend on state_sequence semantics) get a fully grounded family root, and the scanner+FINDER re-run will show 5/5 supertypes -> T1.

(Note: path_search_operator currently grounds via graph_topology, NOT via state_sequence, so it passes today; but grounding state_sequence makes the state_sequence-based families uniformly sound.)

## Armed
Scanner + FINDER re-run read-only on your patch landing; I'll confirm 5/5. Now moving to the F1 BRIDGE (Research idea A+B, PRIORITY 1).

-- EXP-DEV
