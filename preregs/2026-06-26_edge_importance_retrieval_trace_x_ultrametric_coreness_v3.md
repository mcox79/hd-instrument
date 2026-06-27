# Prereg: edge_importance_retrieval_trace_x_ultrametric_coreness_v3

Date: 2026-06-26
Anchor: edge_importance_retrieval_trace_x_ultrametric_coreness_v3
Cell: experiments/exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3.py
Primitives composed:
  - hdlab/edge_importance.py (chain-grade; shipped 2026-06-26)
  - hdlab/ultrametric_clustering.py (chain-grade; shipped 2026-06-26)

## Motivation

v1 (alpha=0.977) saturated. v2 (alpha=1.953) lifted RETRIEVED-vs-RANDOM
spread but landed MIDDLE_BAND with sel_unretr asymmetry +0.030, well below
the +0.10 PASS floor.

Research drill (math + brain) confirmed PageRank-style E_rowsum on the
co-query graph is CATEGORICALLY wrong for the sel_unretr discriminator:
centrality has zero information about retrieval HISTORY. Brain importance is
retrieval-coupled + temporally-tagged (STC, BTSP, engram lit). 2025 engram
work explicit: "higher edge weights -> more readily retrievable;
unretrieved obscured" -- use-count IS the importance signal.

## v3 mechanism (compositional)

```
importance_score[atom] = retrieval_trace_score[atom]
                          * (1 + lambda * ultrametric_coreness[atom])
```

- `retrieval_trace_score[atom]` = per-atom cleanup-argmax hit counter
  during composite-query operation (brain STC analog).
- `ultrametric_coreness[atom]` = 1 if atom belongs to a qualifying
  cluster in `hdlab.ultrametric_clustering.filter_qualifying_clusters`
  output (cosine_thresh=0.85, min_cluster_size=5), else 0.
- `lambda` modulator tested at {0.1, 0.3, 0.5}; pick best by sel_unretr.
- Pruning: all arms prune the SAME N_PRUNE atoms (LOWEST-importance);
  only the SELECTION differs across arms.

## Regime

- N = 512, M_OLD = 600, M_RECENT = 400, alpha = 1.953
- J_composite = 3000, arity = 3, USE_FRAC = 0.40, N_USE = 240
- DOWNSCALE_SCALE = 0.20, N_PRUNE_FRAC = 0.30
- SEEDS = [7, 17, 23], N_QUERIES = 200 per subset per arm
- LAMBDA_LIST = [0.1, 0.3, 0.5]
- ULTRAMETRIC_COSINE_THRESH = 0.85, ULTRAMETRIC_MIN_CLUSTER_SIZE = 5

## Arms (4 mandatory)

- ARM_BASELINE_RANDOM_IMPORTANCE -- random importance (control rail)
- ARM_TRACE_ONLY                  -- importance = retrieval_trace_score
- ARM_ULTRAMETRIC_ONLY            -- importance = ultrametric_coreness
                                     (control: does composition help vs
                                      coreness alone?)
- ARM_TRACE_X_CORENESS            -- importance = trace * (1 + lambda *
                                     coreness)  -- the MECHANISM

## Pre-reg bands (load-bearing)

### HARD_PASS (all must hold)
- COMPOSITION (best lambda) sel_unretr asymmetry >= 0.15
  (rec_UNRETR_random - rec_UNRETR_composition)
- COMPOSITION rec_RETRIEVED >= 0.80 (mechanism doesn't kill retrieved
  as a side effect)
- cor(importance, |W|) < 0.30 (USER fairness gate; orthogonal to
  magnitude)
- mechanism fires (n_downscaled > 0 in COMPOSITION arm)
- COMPOSITION sel_unretr asymmetry >= TRACE_ONLY sel_unretr asymmetry
  + 0.03 (composition value-add over trace alone)
- COMPOSITION sel_unretr asymmetry >= ULTRAMETRIC_ONLY sel_unretr
  asymmetry + 0.03 (composition value-add over coreness alone)

### HARD_FAIL (any one trips)
- All four arms within 0.05 of each other on rec_RETRIEVED (saturation)
- cor(importance, |W|) >= 0.30 (fairness regression)
- n_downscaled == 0 in COMPOSITION arm (mechanism inert)
- H_n_edges < 50 (workload did not populate H -- retrieval traces
  won't either)
- COMPOSITION sel_unretr UNDERPERFORMS TRACE_ONLY by > 0.02
  (composition actively hurts)
- any caught exception (D3 no-silent-except)
- D4 cardinality_ok breach (per-seed arm count != 3 + len(LAMBDA_LIST))

### MIDDLE_BAND
- fairness held (cor < 0.50) + rec_RETR >= 0.60 + sel_unretr > 0.0 +
  mechanism fired; full PASS bands not all cleared.

## New disciplines applied (META rules per 2026-06-26)

- D1 Discriminator-must-survive-scale: smoke runs at FULL-N parameters
  (same N=512, M_OLD=600, M_RECENT=400, J_composite reduced). Mechanism
  must show a sel_unretr asymmetry >= 0.03 above TRACE_ONLY at smoke
  or STOP and route back.

- D2 Smoke-must-FIRE-discriminator: verdict enforces n_downscaled > 0
  AND H_n_edges >= 50 AND trace_total > 0 (mechanism observed
  retrievals).

- D3 No-silent-except: setup + each arm wrapped; any exception RECORDED
  into the seed result.

- D4 cardinality_ok: per-seed expected arm count = 3 single arms +
  len(LAMBDA_LIST) composition arms = 6. HARD_FAIL on breach.

## Substrate-only-decode gate

n_llm_calls = 0 by structural-guarantee. Decode is sign(W @ key) cosine
cleanup against value matrix.

## REQUIRED_FIELDS

`verdict`, `verdict_msg`, `elapsed_s`, `summary`.

## Composition rationale (brain + math grounding)

- retrieval_trace_score IS the brain STC analog of synaptic tag-and-
  capture: synapses that fired are tagged; tagged synapses are
  preferentially consolidated. Translating to substrate: atoms that
  fired (cleanup-argmax hit during composite-query operation) are
  retrieval-traced.
- ultrametric_coreness IS the brain schema/engram analog of clustered
  synaptic plasticity (Govindarajan-Israely-Huang-Tonegawa 2011): atoms
  that cluster together at high cosine similarity tend to be jointly
  protected. Translating to substrate: cluster-resident atoms get a
  small importance bonus.
- The MULTIPLICATIVE composition (1 + lambda * coreness) means cluster
  atoms ONLY get the bonus IF they have non-zero retrieval trace.
  Cluster-resident but never-retrieved atoms are still pruned. This
  matches the brain prediction: cluster membership alone doesn't
  protect a never-used synapse.

## ASCII-only; no unicode; no emojis; no em-dashes.
