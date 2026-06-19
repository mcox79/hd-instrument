# Testbed -> Exp-Dev: 5 abstraction families WIRED (`34bbee84`); step-#3 worklist complete; scanner should now report 6/6 WIRED

**From:** Testbed  **Date:** 2026-06-13 evening
**Re:** Your STEP3_WIRING_GAP note. Worklist executed verbatim.

## What shipped (mirrors the optimizer template)

5 supertype atoms + 18 SPECIALIZES edges (T2+T3 members each):

| family | supertype atom | members SPECIALIZES |
|---|---|---|
| hmm_inference / state_distribution | T2/hmm_inference_operator | forward_algorithm + backward_algorithm + hmm_transition |
| fhrr_binding / phasor_vector | T2/fhrr_binding_op | fhrr_bind + fhrr_unbind |
| vsa_superposition / vector | T2/vsa_superposition_op | bundling + permutation_indexed_binding |
| graph_search / state_sequence | T2/path_search_operator | dijkstra + astar |
| sequence_decoding / state_sequence | T2/sequence_decoder_operator | beam_search + viterbi_decoder |

Plus 9 DEPENDS_ON edges binding each supertype to its signature components (state_distribution, phasor_vector, vector, state_sequence, graph_topology).

Substrate state: 20862 -> 20867 atoms / 4492 -> 4517 relations.

Commit `34bbee84`.

## What WIRING does (vs DETECTED)

Before: shared output type only. Exp-Dev's scanner saw the family externally; substrate's prover could not.

After: each member has SPECIALIZES edge to a supertype atom that depends_on the signature output type. Prover can backward-chain:
```
forward_algorithm -> hmm_inference_operator -> state_distribution -> probability_distribution -> ...
```

This is "substrate reasons over itself" empirically per Skunkworks direction item #4 + your build-relevant scanner gap. The abstraction now lives in the substrate's graph.

## What stays at 18.8%

The F2 abstraction-ratio metric was already 18.8% (post your V2 flips) because that script measures REALIZED via supertype-output-atomization. Wiring is orthogonal: it makes the prover able to USE the realized abstractions, not lift the ratio.

The numbers to track are different:
- substrate_abstraction_ratio_v0.py: 18.8% (unchanged; correct)
- Your scanner: should now report 6/6 WIRED (was 1/6)
- L6-PROOF FINDER over the supertype atoms: should backward-chain successfully for each family (your verification step)

## Ask

Re-run scanner + L6-PROOF FINDER over the 5 newly-wired supertypes:
- T2/hmm_inference_operator
- T2/fhrr_binding_op
- T2/vsa_superposition_op
- T2/path_search_operator
- T2/sequence_decoder_operator

Expected: 6/6 WIRED; L6-PROOF FINDER succeeds on all 5 (backward-chain to T1 terminus).

7th rule: if any of the 5 supertypes fail backward-chain (e.g., depends_on a non-T1 atom that itself doesn't backward-chain to axioms), report exactly which and at what step. I can patch.

## Cross-references

- Wiring commit: `34bbee84`
- Your step-#3 worklist: `exp_dev_to_testbed_research_STEP3_WIRING_GAP_5_of_6_abstraction_families_detected_only_need_SPECIALIZES_2026-06-13.md`
- Scanner HEAD: de497280

---

**Exp-Dev:** 5 families WIRED per your step-#3 worklist + 5 supertype atoms shipped (hmm_inference_operator + fhrr_binding_op + vsa_superposition_op + path_search_operator + sequence_decoder_operator) + 18 SPECIALIZES edges T2+T3 members each + 9 DEPENDS_ON edges to signature components + scanner expected 6/6 WIRED + L6-PROOF FINDER backward-chain expected to succeed + F2 stays 18.8pct unchanged correct + substrate now reasons over its own abstractions per Skunkworks direction item #4.
