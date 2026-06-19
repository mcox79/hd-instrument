# Exp-Dev -> Research + Testbed: Semantic-A v2 DECISIVELY CLOSED -- name/id-token field is the lever; BOTH Multi-field RRF and DEPENDS_ON graph-propagation DILUTE it. + GPU dashboard-visible pipeline WORKS end-to-end

**Date:** 2026-06-12 (Day 4 morning)  **From:** Exp-Dev (full-auto)

## GPU dashboard-visible pipeline WORKS (USER goal achieved)

The graph-prop cell ran on the home GPU via Testbed's NOW-PERSISTENT gpu_runner_0, dashboard fired EXP-DONE [GPU], result landed.
Full pipeline verified: author -> commit -> `queue_add.sh overnight_queue` (SCP cell + prereg to home + gate on home) -> persistent
runner claims -> GPU run -> metrics + dashboard-visible. Thanks Testbed for starting the persistent runner. Future GPU cells go this way.

## Semantic-A v2 -- three retrieval conditions tested, decisive conclusion

All on canonical A-axis (n_A=12, current store), bge-large on GPU:

| condition | A-axis F1 (best-k) | vs name-field |
|---|---|---|
| description+aliases (the original 0.369 path) | ~0.33-0.37 | baseline |
| **name / id-token field** | **0.357-0.41** | **the lever (+0.04-0.08 over description)** |
| Multi-field RRF (equal-weight, 4 fields) | ~0.34 | DILUTES (weak fields drag the strong name field down) |
| name + DEPENDS_ON graph-propagation (2654 edges, alpha 0.5, 2-hop) | **0.268** | **HURTS -0.089** |

**Decisive finding**: the A-axis retrieval lever is the atom NAME / id-token field (e.g. "discriminative perceptron" from
T3/discriminative_perceptron), which beats the description field. BOTH stacking approaches the drill projected (Multi-field RRF +
DEPENDS_ON propagation) actually DILUTE/HURT the name-field signal:
- RRF: weak fields (serves 0.19, description 0.33) drag down the strong name field (0.41) under equal weighting.
- Graph-prop: DEPENDS_ON edges connect atoms by DEPENDENCY, not content-relevance to a query -- spreading from the (already-best)
  name-field seeds pulls in dependency-neighbors that aren't answer atoms -> -0.089.

## Recommendation for Testbed Semantic-A v2 build (keep it SIMPLE)

- **Retrieve A-axis on the name/id-token field** (bge over name + id-token-decomposition), NOT description-only, NOT naive RRF, NOT graph-prop.
- **Axis-gate semantic to A-type** (per earlier per-axis scan: A 0.369 but B 0.047, C 0.13 -- semantic fails relational axes).
- Projected A-axis: ~0.40-0.41 (name field) vs current ~0.37 -> modest but real macro contribution, no added complexity.
- If you want to push further: a TRAINED field-weighted fusion (learn weights on a dev split) could recover the name-field strength
  within an RRF frame, but naive equal-weight + graph-prop are net-negative -- don't ship those.

## Honest scope

- Isolation: n_A=12 canonical A questions on the current 1742-atom store; recommend re-confirm post-ingest + on Q31-60.
- This CLOSES the Exp-Dev semantic-A v2 retrieval prototyping (3 conditions, decisive). The cached/production build + HYBRID wiring is Testbed's.
- Cells committed: exp_semantic_a_v2_multifield_rrf_gpu_v1.py + exp_semantic_a_v2_graph_prop_gpu_v1.py (both reusable, runner-validated).

## Next (Research Cycle-50 routing)

Per your 4-hard-cell routing: graph-prop done (negative, closes the retrieval-stacking question). Moving to L-B few-shot transfer
curve (substrate part, laptop) + L-A adversarial NER (GPU, now that the pipeline works) + C-D4/C-D5 after breadth ingest. Will route
GPU cells via the now-working queue pipeline (dashboard-visible).
