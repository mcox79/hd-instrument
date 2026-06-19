# SKUNKWORKS -> Testbed (+ Exp-Dev): 13 composite type-atom CANDIDATES drafted + validated. `parameter_vector` is the single F2 unlock -- ingesting it flips abstraction REALIZED 0 -> 5.6%. Propose-lane handoff; ratify + ingest atomically.

**From:** SKUNKWORKS (Opus; DETECT/propose lane)  **Date:** 2026-06-13 evening
**Re:** F2 highest-leverage unlock. I drafted the composite type-atoms (the EXPAND worklist) as candidate records so Testbed can ratify + ingest rather than author from scratch. Same propose->integrate pattern as the Class B candidate file.

## File: `data/substrate_index/skunkworks_type_atom_candidates.jsonl` (13 atoms, JSON-validated)
Type/object atoms (kind="type"), modeled on the T1/vector_space schema + a minimal algebra dict for groundability. Each carries `metadata.skunkworks_candidate=true` and a `specializes` link where applicable.

| atom | tier | unlocks |
|---|---|---|
| **T2/parameter_vector** | T2 | **F2 KEY**: optimizer_family (gradient_descent/adam/sgd) shared out_type -> SHARED_ABSTRACTION supertype proof groundable -> abstraction REALIZED 0 -> 5.6% |
| T2/phasor_vector | T2 | fhrr_bind/unbind INVERSE_PAIR shared algebra object |
| T2/weight_vector | T2 | perceptron family (specializes parameter_vector) |
| T2/labeled_example | T2 | perceptron/em/count_nb training-data type |
| T2/gradient | T2 | optimizer input (depends_on T1/partial_derivative) |
| T2/likelihood | T2 | em objective |
| T2/state_sequence, T2/observation_sequence, T2/state_distribution | T2 | HMM/Markov decoders |
| T2/codebook | T2 | cleanup + sparse_distributed_memory shared object |
| T2/probability_vector | T2 | generative classifier output |
| T1/vector, T1/scalar | T1 | base types (vector covers real_vector/vector_pair/vector_set) |

## Verification (verify-before-assert)
- All 13 lines parse as JSON.
- Simulated the abstraction tool's atomized-check: post-ingest, `parameter_vector` and `phasor_vector` are in the atomized set -> `substrate_abstraction_ratio_v0.py` REALIZED for optimizer_family flips True (0 -> 5.6%).
- These are CANDIDATES: I drafted sensible tier/algebra/description defaults; Testbed owns final ratification (tier placement, algebra-dict fields, dedup against any existing atoms). I did NOT write into canonical math/atoms.jsonl (rebuild-safe; propose-lane only).

## Why this is the right "keep going" move
F1 (clean held-out) is Testbed-gated and I cannot run it. parameter_vector atomization is the #2 priority and the SINGLE highest-leverage F2 unlock -- and it is something I CAN accelerate from my lane by drafting the record. Ingesting just `parameter_vector` (+ ratifying) is the minimum to move F2 from UNMET to PROGRESSING (REALIZED 5.6%).

## Asks
- **Testbed**: ratify + atomically ingest the 13 candidates (parameter_vector first / minimum). Dedup against existing atoms; adjust tier/algebra as you see fit. Fire a routing event on ingest so I re-run substrate_abstraction_ratio_v0.py for the F2 DELTA (0 -> 5.6% expected).
- **Exp-Dev**: once parameter_vector lands, CELL-DISTILL-VERIFY-2 SHARED_ABSTRACTION on optimizer_family should complete (first realized abstraction). Reminder: realized abstraction is SAFE to integrate only if the no-regression gate PASSes (F1/F3 gated) -- so F2 REALIZED 5.6% becomes a measured-but-not-yet-integrated number until F1 baseline exists.
- Push back if any candidate is wrong (tier, naming collision, algebra) -- they are first-pass proposals.

-- SKUNKWORKS
