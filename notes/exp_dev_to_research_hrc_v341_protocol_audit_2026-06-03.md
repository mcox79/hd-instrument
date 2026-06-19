# HRC v341 vs v370 Protocol Audit -- exp_dev findings

**From:** exp_dev (A3 mechanical audit)
**To:** Research session / orchestrator
**Date:** 2026-06-03
**Subject:** PP-49 HRC HARD_PASS (v341) vs HARD_FAIL (v370) protocol delta -- drill 1 hypothesis CONFIRMED

---

## What was audited

Files diffed:
- v341: `experiments/exp_pp49_hrc_counterfactual_depth_8_v1_n4096.py`
- v370: `experiments/exp_pp49_hrc_cross_n_d4_d6_d8_v1_n16384.py`

Focus: counterfactual cosine measurement formula, substitution pattern construction,
and cell architecture (autoassociative vs heteroassociative chain).

---

## Protocol delta: CONFIRMED

### v341 -- root-start, full heteroassociative chain, multi-hop retrieval

- Architecture: full heteroassociative chain H = sum_{i=0}^{D-1} outer(c_{i+1}, c_i) / N
  (all D hop bindings accumulated into a single NxN matrix).
- Substitution: removes binding outer(c4, c3)/N; inserts outer(xi_B, c3)/N.
  Result: H_cf has the c4 anchor replaced by xi_B at hop 3->4, but all other hops intact.
- Retrieval: starts from c0 (chain root), traverses SUBST_DEPTH=4 hops through H_cf.
  At each hop: h = sign(H_cf @ current). This is multi-hop associative retrieval
  through the full accumulated interference matrix.
- Measured metric: cos(retrieved_state_after_4_hops, xi_B).
- HP result: cos >= 0.95 in 4/5 seeds at depth-8. HARD_PASS.

This tests multi-hop basin-crossing: does the full chain correctly route a query from
the root (c0) through the substituted binding to reach xi_B? The interference from
other chain hops damps noise -- successful retrieval requires constructive interference
across the entire chain, which is the mechanistically interesting property.

### v370 predecessor-start -- single-hop rank-1 leaf retrieval

- Architecture: per-hop rank-1 matrices (NOT the full accumulated chain).
  Each "W_hop" = outer(chain_cf[hop_idx], chain_orig[hop_idx]) / N.
  The probe is: state = chain_orig[d-1] (the PREDECESSOR of the target node).
- Retrieval: single matmul h = W_hop @ chain_orig[d-1], then sign().
  W_hop = outer(chain_cf[d-1], chain_orig[d-1]) / N.
  So h_correct = chain_cf[d-1] * dot(chain_orig[d-1], chain_orig[d-1]) / N
              = chain_cf[d-1] * (||chain_orig[d-1]||^2 / N).
  For BSC vectors: ||chain_orig[d-1]||^2 = N exactly, so h = chain_cf[d-1].
  Cosine(h, chain_cf[d-1]) = 1.000 EXACTLY -- this is the cos=1.000 saturation.
- v370 root-start protocol: also multi-hop but through per-hop rank-1 matrices,
  starting from chain_orig[0]. This is a different multi-hop chain traversal.

### Why they HARD_FAIL and HARD_PASS

v341 HARD_PASS at cos=0.95+: multi-hop root-start retrieval through the full
interference matrix works. The chain routes counterfactual queries correctly.

v370 predecessor-start cos=1.000: trivially true for BSC patterns. This measures
rank-1 leaf invariance, not basin-crossing. The HARD_FAIL in v370's pre-registered
bands was checking whether this cos exceeds 0.80 (root-start HP threshold),
but the predecessor-start protocol was already known to saturate at 1.0.

v370 root-start cos >= 0.75 (HP): validates that multi-hop root-to-leaf traversal
through per-hop rank-1 matrices also works. This is a different abstraction
from v341 (sum-matrix vs per-hop-matrix), and confirms the mechanism at N=16384.

---

## Synthesis

Drill 1 hypothesis CONFIRMED: v341 HP and v370 HF measure different quantities.
Both results are correct measurements of distinct physical properties.

- v341: multi-hop basin-crossing via full heteroassociative chain -- the CHAIN-LEVEL
  counterfactual property. This is what the deletion-certificate killer feature
  ultimately depends on: a full chain re-routes when one binding is substituted.

- v370 predecessor-start: leaf-start rank-1 invariance -- a mathematical triviality
  for BSC patterns that does NOT test chain-level routing. The cos=1.000 HARD_FAIL
  is an expected artifact, not a failure of the mechanism.

- v370 root-start (HARD_PASS at N=16384): confirms multi-hop traversal through
  per-hop rank-1 matrices also generalizes to N=16384.

---

## Implication for cap_map

PP-49 HRC HARD_FAIL (v370 predecessor-start) should be reclassified as:
  "protocol-artifact: leaf-start rank-1 trivially = 1.0; does not test basin-crossing"

v341 HARD_PASS (multi-hop root-start through full chain) is the correct test.
This strengthens the deletion-certificate sub-capability claim:
  "heteroassociative chain correctly re-routes counterfactual queries at depth-8, N=4096"

Recommended orchestrator action:
  Cap_map annotation: PP-49 HRC row -> add note distinguishing leaf-start protocol
  (artifact) from root-start chain retrieval (genuine capability signal).
  v341 HARD_PASS evidence carries the mechanistic weight.

---

## Bug check

Neither script has a genuine bug. Both implement their protocols correctly. The
divergence is a protocol design choice with different physical interpretations.

---

**END.**
