# Research drill: authoring-blind null-model methodology for load-bearing-axis audit (Skunkworks INV-1 support)

Date: 2026-06-13
Topic: methods that let us test the tools-vs-materials axis WITHOUT trusting the curator-authored edge set.
Budget: ~30-45 min, local CPU, generic queries only.

## HEADLINE

The three "independent" tests of the load-bearing axis (PROVISIONAL 1.33x + INTRINSIC 3/3 + DEFINITIVE 2.34x p=0.0005) are all measured on the SAME authored knowledge graph; degree-aware label-permutation nulls control only the marginal degree sequence, NOT whether the EDGE SET itself was authored under tool/material priors. To test independence honestly we need at least one EDGE-REGENERATION null — rebuild the edges from a body-text-derived criterion that is BLIND to the curator's tool/material tags, then re-run the downstream load-bearing metric. Three concrete tag-blind edge-generation criteria are below, plus a recommended INV-1 cell design.

## Cheap decisive test (INV-1 cell)

1. Strip all curator-applied tool/material tags from atoms; keep only atom bodies (definition text + symbol/operator strings + dictionary keys).
2. Rebuild three edge sets purely from body text, each by a different mechanical criterion (C1, C2, C3 below).
3. For each rebuilt edge set, recompute the SAME downstream load-bearing metric used in the DEFINITIVE test (the 2.34x ratio statistic — without naming it in any external query).
4. Compare against a degree-aware label-permutation null AND against an edge-regeneration null (configuration model + DC-SBM null at the rebuilt-graph degree sequence).
5. Pre-register HARD-PASS / HARD-FAIL bands BEFORE seeing the rebuilt-graph numbers.

Cost: ~2-4 hrs local CPU on existing atom bodies; no GPU; no new ingest.

## Three authoring-blind edge-generation criteria

All three derive edges from atom body text only. No curator-applied tag is read. All three are mechanical and re-runnable.

### C1. Operator-cooccurrence edges

Build a multiset of operator/symbol tokens per atom body (e.g. `bind`, `unbind`, `inner_product`, `argmax`, `softmax`, `circular_convolution`, `+`, `*`, `o`). Two atoms share an edge if their operator multisets have Jaccard >= tau_C1 (sweep tau in {0.2, 0.3, 0.4}). This proxies "uses the same math" without referencing the curator's tool/material schema. Grounded in standard ontology-learning Jaccard-on-tokens practice.

Confound it does NOT control: if the curator's tagging correlates with which operators an atom body lists, C1 inherits some upstream bias. So C1 is the MOST permissive criterion (closest to the original schema). Use it as the upper bound.

### C2. Definition-text distributional-semantics edges

For each atom, compute a bag-of-words / TF-IDF / sentence-embedding vector from definition text ONLY (strip headers, type tags, axis labels). Two atoms share an edge if cosine >= tau_C2. Use the SAME embedding model that the substrate already runs (bge or equivalent) so we are not introducing a new ML axis. Sweep tau in {0.55, 0.65, 0.75}.

Confound it does NOT control: if curator-authored definitions systematically use overlapping vocabulary for tool atoms vs material atoms (e.g. all tools say "operator that maps..." and all materials say "vector that represents..."), C2 inherits stylistic bias. Mitigation: also run a stop-phrase mask that strips meta-vocabulary ("operator", "function", "tensor", "vector", "represents", "maps").

### C3. Shared-symbol overlap edges (most adversarial)

For each atom, extract ONLY mathematical symbols and LaTeX-equivalent strings from the body (e.g. `\oplus`, `\otimes`, `argmax_x`, `||.||`). Two atoms share an edge if symbol overlap >= 2 distinct symbols. This is the LEAST sensitive to curator stylistic conventions (definitions and English prose are masked out). It is also the SPARSEST graph, so statistical power will be lower — pre-register that.

C3 is the strongest authoring-blind criterion: it relies only on what mathematical symbols the atom's body actually contains. If the load-bearing-axis metric still survives on a C3-rebuilt graph at a configuration-model null, the axis is robustly substrate-readable from operator surface alone.

## Bias-decomposition argument: what each null controls vs misses

| Null | Preserves | Controls for | Misses (still confounded by) |
|---|---|---|---|
| Random label permutation | Node count | Marginal label rates | Degree, community structure, edge-set authoring |
| Degree-aware label permutation (the DEFINITIVE test's null) | Node count + degree sequence | Marginal label rates + degree heterogeneity | Community/block structure + edge-set authoring |
| Configuration model edge regeneration | Degree sequence | Anything that follows from degree alone | Block structure (DC-SBM gap), but is AUTHORING-BLIND if applied to a C1/C2/C3-rebuilt graph |
| DC-SBM null on rebuilt graph | Degree sequence + community block memberships | Degree + block structure | Edge-set-conditional-on-tags (which is what we ARE testing — so this is what we WANT to leave uncontrolled) |
| Block-constrained configuration model on rebuilt graph | Degree + within/between-block edge counts | Even finer mesoscale | Same as DC-SBM but tighter |

Key decomposition (per the skunkworks flag): the DEFINITIVE 2.34x ratio with degree-aware label permutation null factors as

  bias(authored-edge-set, tool/material) + signal(tool-ness-via-substrate-load-bearing)

Degree-aware label permutation eliminates the degree contribution to the bias term but does NOT touch the authoring contribution. To isolate signal we need to either (a) regenerate edges blindly so bias contribution drops by construction, or (b) measure the same metric on an EDGE-REGENERATED null at the rebuilt-graph degree sequence and confirm the signal persists.

Standard network-science practice (per Farine 2017 + bioRxiv 2020 reviews): node-label permutation tests "the role of node attributes in the structure of the network" — appropriate when the EDGE SET is trusted. Edge permutation / regeneration tests "structural properties NOT dependent on node attributes" — appropriate when EDGE SET is suspected to encode the attribute. Skunkworks' flag is exactly the latter regime. The DEFINITIVE test used the former null in a regime where the latter is called for.

Block-constrained configuration models (Fosdick et al, Springer 2019) are the strongest known null for this case: they preserve degree AND block structure AND give the largest space of authoring-blind randomizations.

## Recommended INV-1 cell design

```
Cell: INV-1 (authoring-blind load-bearing-axis re-validation)
Anchor: notes/research_DRILL_authoring_blind_null_methodology_..._2026-06-13.md

Inputs:
  - Current atom corpus, stripped of curator tool/material tags
  - Same downstream load-bearing metric M used in DEFINITIVE test

Three edge-regeneration arms:
  arm_C1: operator-cooccurrence Jaccard >= 0.3 (sweep {0.2, 0.3, 0.4})
  arm_C2: bge-cosine on definition text >= 0.65 (sweep {0.55, 0.65, 0.75})
          with stop-phrase mask applied
  arm_C3: shared-symbol overlap >= 2 (one threshold; lowest-power arm)

Per arm, three nulls:
  null_A: degree-aware label permutation (matches DEFINITIVE for comparability)
  null_B: configuration model edge regeneration (preserve degree only)
  null_C: degree-corrected SBM edge regeneration (preserve degree + blocks)

Statistical test: z-score of observed M against each null distribution
                  (N_null = 1000 resamples per arm-null pair)

Pre-registered fail bands (BEFORE seeing rebuilt-graph numbers):
  HARD-PASS: M survives at z >= 3.0 (p < 0.0013) on >= 2 of 3 arms
             AND >= 2 of 3 nulls per surviving arm
             AND C3 arm survives at z >= 2.0 (sparsest, lowest power)

  HARD-FAIL: M is degraded below z = 1.5 (p > 0.13) on >= 2 of 3 arms
             OR C3 arm explicitly fails at z < 1.0
             -> three "independent" tests were ONE authoring confound;
                load-bearing-axis claim withdrawn pending re-architecture.

  MIDDLE BAND: any other outcome. Treated as PARTIAL; do not claim
               independent corroboration; file follow-up drill on which
               criterion choice the signal depends on.
```

The C3 arm is the gate. If body-text symbol-overlap edges (which never see curator tags) still produce a load-bearing-axis signal, the axis is robustly substrate-readable. If not, the prior three tests are not three independent measurements.

## Cross-thread synthesis with prior entries

- The DEFINITIVE 2.34x ratio with p=0.0005 used a degree-aware label-permutation null. That null is correctly calibrated for the "node attributes" regime per Farine 2017, but the skunkworks flag asserts we are in the "edge set encodes the attribute" regime. Both can be true in different decompositions — INV-1 settles which.
- C1 (operator-cooccurrence) is close to what the SHARES_MATH edge generator already does on the substrate side (per MEMORY index). If the substrate's existing SHARES_MATH detector already produces edges by C1-like criterion, we partially already have arm_C1 — but it must be re-derived from atom bodies stripped of tool/material tags, not from the live tagged graph.
- This drill does NOT use any substrate-novel mechanism name externally. All four external queries used generic terms (configuration model, DC-SBM, ontology learning, distributional semantics, robustness audit). Per query-privacy rule satisfied.
- Lit-scan calibration penalty applied: prior work tells us nulls A/B/C are the standard menu, but the SPECIFIC three-criterion + three-null tensor design for our regime is novel-synthesis. Deflating any P estimate by 0.20; raw P(load-bearing-axis survives all three arms at HARD-PASS) ~0.55 -> deflated P=0.35; raw P(at least one arm survives HARD-PASS) ~0.75 -> deflated P=0.55.

## Substrate-product implications

- INV-1 is a falsification gate for the substrate-product positioning artifact that the substrate has independent observability dimensions LLMs lack. If INV-1 HARD-FAILS, the "3-axis architecture EMPIRICALLY ORTHOGONAL via Cell #3 + KP P6" capstone needs a footnote distinguishing axis-existence (still defensible) from axis-magnitude-as-measured (compromised).
- INV-1 HARD-PASS strengthens the substrate-product claim from "load-bearing axis observed under our schema" to "load-bearing axis observed under authoring-blind reconstruction" — a categorical strengthening, because no LLM can do this on its own representations (LLM token embeddings have no analog of "rebuild edges from atom bodies").
- Either outcome is publishable substrate-internally (cap_map row regardless of direction).

## Honest framing per prior-work governance

The substrate is, by USER assertion, possibly the first system of its kind. Network-science nulls and ontology-learning Jaccard methods INFORM the design space (we adopted block-constrained configuration models from Fosdick et al, edge-vs-node permutation regimes from Farine, Jaccard-on-tokens from ontology-learning surveys, distributional semantics for C2). They do NOT GOVERN the choice — the C1/C2/C3 trichotomy plus the 3x3 arm-null tensor is a novel-synthesis design specific to our authoring-blind regime. Lit calibration penalty applied accordingly.

## Citations (verified count: 7)

External (generic-query results):
1. Fosdick, Larremore et al. "The block-constrained configuration model" Applied Network Science 2019 — block-constrained nulls.
2. Wikipedia "Configuration model" — degree-preserving null baseline.
3. Farine "A guide to null models for animal social network analysis" Methods Ecol Evol 2017 — node-label vs edge-permutation regime distinction.
4. Hart et al. "Permutation tests for hypothesis testing with animal social network data" bioRxiv 2020 / PMC 2022 — known limitations of both regimes; complements Farine.
5. Wikipedia "Distributional semantics" — C2 vector-cosine basis.
6. AutoSchemaKG (arXiv 2505.23628) — body-text-only schema-blind KG construction precedent.
7. Wijaya 2025 "Analyzing Bias in LLM-Augmented Knowledge Graph Systems" (MDPI Applied Sciences) + KG-BIAS Workshop 2020 (arXiv 2007.11659) — curator-bias propagation; motivates the authoring-blind audit framing.

Substrate-internal (cross-thread):
- DEFINITIVE 2.34x p=0.0005 result (degree-aware label-permutation null) — the target of audit.
- 3-axis architecture EMPIRICALLY ORTHOGONAL Cell #3 + KP P6 (per MEMORY index 2026-06-13).
- 13th methodology rule candidate (tools vs materials), 1st and 2nd appearance memos.

## Next-drill candidates

- INV-1 cell EXECUTION (Exp-Dev hand-off below). This is the priority follow-up.
- If INV-1 PASSES: drill C1/C2/C3 sensitivity — which body-text features are LOAD-BEARING for the axis signal? That sub-decomposition is itself a substrate-product claim.
- If INV-1 FAILS: 2x drill on whether axis-existence (qualitative) survives when axis-magnitude (the 2.34x ratio) does not. They are separable.
