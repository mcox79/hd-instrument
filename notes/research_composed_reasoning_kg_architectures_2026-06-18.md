# research: composed reasoning over typed-edge KGs (substrate-internal)

Filed: 2026-06-18 PM
Topic: canonical architectures for substrate-internal multi-hop reasoning + provenance + sleep-consolidation + active-learning ingest
Trigger: USER strategic question on composed-reasoning support (~600 words)
Constraints: NO LLM in reasoning loop; cert-grade answer composition (edge-by-edge auditable); fit with typed-edge graph + 4 LIVE self-cert gates + Lean PROOF_RECORD scaffold

## HEADLINE

Only TWO published patterns are natively edge-by-edge auditable under the "every hop traces to a persisted typed edge, no hallucinated hops" rule: (a) **path-walking RL (MINERVA)** and (b) **symbolic rule mining (AnyBURL/AMIE 3/Path-Ranking)**. Embedding-compositional (RotatE, BoxE) and graph-conv (R-GCN/CompGCN) families are NOT-AUDITABLE under this rule because intermediate hops are vector compositions or implicit layer aggregations with no recoverable stored-edge chain. Neural-LP / NTP / DRUM are PARTIAL — auditable after top-1 hardening of the soft-attention weighting. Offline consolidation + active-ingest patterns from the KG literature are mature and snapshot-friendly.

## (1) Canonical architectures for substrate-internal multi-hop reasoning

| Family | Mechanism (1-line) | Edge-by-edge auditable? | Fit |
|---|---|---|---|
| Path-walking RL — MINERVA / DeepPath | REINFORCE policy picks an outgoing typed edge at each step until landing on the answer; the traversed edge sequence IS the witness chain (Das+18, arxiv.org/abs/1711.05851) | YES — every hop is a stored typed edge | STRONG fit; maps directly to typed-edge graph + cert-grade composition gate |
| Embedding compositional — RotatE / BoxE / QuatE | entity=point, relation=rotation/box; multi-hop = composed rotation; answer = nearest-neighbor in embedding space (Sun+19, arxiv.org/abs/1902.10197) | NO — intermediate hops are vectors, not edges | EXCLUDE for cert path |
| Differentiable rule learning — Neural-LP / NTP / DRUM | learns Horn chains via differentiable matrix products over relation adjacency tensors (Yang+17, arxiv.org/abs/1702.08367) | PARTIAL — auditable post top-1 hardening | USE FOR rule-induction offline; harden at query time |
| Relational graph-conv — R-GCN / CompGCN | typed message passing produces node embeddings used for downstream prediction (Vashishth+20, arxiv.org/abs/1911.03082) | NO — multi-hop is implicit in layer stack | EXCLUDE for cert path |

## (2) Answer-chain provenance / explainable KG QA

| Pattern | Provenance property | Audit/cert protocol |
|---|---|---|
| AnyBURL / AMIE 3 — symbolic rule mining | every prediction backtracks to firing rule + concrete edge instantiations; no neural hallucination surface | YES — published PCA-confidence, head-coverage, support metrics (Meilicke+23, VLDB J., link.springer.com/article/10.1007/s00778-023-00800-5) |
| Neural-LP — differentiable rule learning | inference = chain of relation-matrix multiplications; every hop corresponds to a persisted edge in adjacency tensor | PARTIAL — formal soundness/completeness criteria for extracted rules (Yang+17 + OpenReview faithful-extraction) |
| Path-Ranking Algorithm (PRA) | random walks enumerate bounded-length paths; features ARE concrete paths; predictions cite finite multiset of grounded edge-sequences | Inherent — per-path weights reportable (Lao+11, EMNLP; surveyed arxiv.org/pdf/1503.00759) |

PullNet / GraftNet EXPLICITLY EXCLUDED — GCN aggregation hides hop-level provenance ("cannot produce intermediate reasoning path").

## (3) Sleep consolidation / offline graph optimization (engineering patterns)

| Pattern | Mechanism | Offline/online |
|---|---|---|
| Entity resolution / canonicalization | block -> pairwise-similarity (string + embedding) -> cluster -> fuse to canonical node, re-point relations | snapshot batch + delta swap (Paulheim 2017 survey, semantic-web-journal.net/system/files/swj1167.pdf) |
| Rule mining for edge inference + schema evolution — AMIE 3 | mine closed Horn rules with PCA-confidence; materialize high-confidence inferred edges; promote frequent rule heads to new schema relations | pure offline snapshot scan (Lajus+20, ESWC, link.springer.com/chapter/10.1007/978-3-030-49461-2_3) |
| Generative replay (continual KG embedding) | train VAE/diffusion on current triples; interleave replayed samples with new edges to prevent catastrophic forgetting | hybrid — generator offline; replay drives online update (Cui+25 ACL, aclanthology.org/2025.acl-long.537.pdf; Daruna+21 arxiv.org/pdf/2101.05850) |

All three are snapshot-friendly: build delta on copy, validate, swap. AMIE 3 is the most-direct fit for typed-edge graph + cert-condition discipline (PCA refuses to assert absent triples false).

## (4) Active learning / self-improvement for KG ingest

| Pattern | Gap-id signal | Edge-budget / 0-phantom respected? |
|---|---|---|
| Active learning for KGE (uncertainty / Thompson) | triple-score uncertainty near 0.5; oracle confirms before ingest | YES (Kajino+15 WWW, dl.acm.org/doi/10.1145/2736277.2741103) |
| Open-world KG completion — ConMask | entities described in corpus but absent / sparsely-connected in KG | UNCLEAR — needs downstream no-phantom gate (Shi+18 AAAI, arxiv.org/abs/1711.03438) |
| Completeness-aware rule mining — AMIE + PCA + cardinality bounds | PCA confidence drops + class-cardinality estimator flags under-populated (subject, relation) slots | YES — PCA explicitly refuses absent=false; rules surface gaps not auto-assert (Galarraga+20 VLDB J., luisgalarraga.de/docs/amie3.pdf; Tanon+17 ISWC completeness-aware) |

Patterns 1 + 3 are budget-respecting + oracle-gated; map cleanly onto existing Bucket B ingest cert-conditions (edge-budget + 0-phantom + cross-corpus completeness).

## Cheap decisive test

Build a "multi-hop-provenance gate" cert-condition prototype on the existing 41k-atom graph:
- Input: a 2-hop or 3-hop test query with a known answer
- Mechanism: MINERVA-style policy (or symbolic random-walk PRA) over typed edges; record the edge sequence
- Cert check: each hop is verified against the persisted (src, rel_type, tgt) tuple in the Store; if any hop fails the lookup, GATE-FAIL
- Cost: low (~CPU, no LLM, reuse existing relation graph)

## Falsifiable predictions

- HARD-PASS: MINERVA-style path-walk over the existing typed-edge graph yields >=70% answer-found rate on a held-out 2-hop test set built from existing HYPERNYM/IS_A/PART_OF chains, with 100% of returned paths edge-verifiable against the Store.
- HARD-FAIL: <40% answer-found rate, OR ANY returned path contains an edge not present in the Store (would refute the "no-hallucinated-hops" property of the path-walking family for our graph).
- HARD-PASS (provenance gate): a symbolic-rule pass via AnyBURL/AMIE 3 on the 41k atoms produces >=50 rules with PCA-confidence >=0.7 + head-coverage >=0.3 (canonical AMIE thresholds).
- HARD-FAIL (provenance gate): <10 rules above those thresholds (would indicate edge density too low for symbolic rule mining; rescue = drill edge-density gap).

## Cross-thread synthesis

- Composes with the 4 LIVE self-cert gates: a "multi-hop-provenance gate" sits at the same architectural layer as gate-0-both-ends + corpus-completeness — it's a structural deterministic check, not a truth-judgment (consistent with substrate-autonomy directive per [[feedback_substrate_autonomy_path_encode_audit_discipline_as_self_certification_USER_2026-06-17]]).
- Composes with the typed-edge persistence gotcha (per [[reference_store_drops_relation_edge_metadata_role_on_source_atom_2026-06-18]]): rel_TYPE is safe, so MINERVA's reliance on typed-edge selection is structurally supported by our Store; first-class rel_types (lean toward) align with path-walking's discrete typed-edge action space.
- Composes with NEGATIVITY-BIAS rule: do not pre-judge the substrate as edge-sparse (USER 2026-06-18 morning catch found 432 cert-grade positives in a "negative" scour); the AMIE rule-density falsifiable bands are SYMMETRIC.
- Adjacent to [[reference_substrate_corpus_completeness_remote_vs_local_half_data_2026-06-17]]: the active-learning patterns (AMIE+PCA, Kajino uncertainty) operationalize gap-detection as a CERT-CONDITION not a heuristic.

## Substrate-product implications

- **NEAR-TERM ANCHOR (composed reasoning v0)**: ship a MINERVA-shape path-walking prototype as a substrate-internal multi-hop query primitive. Audit gate = each hop verified against the (src, rel_type, tgt) Store tuple. NO LLM in the loop. This converts the 4-gate self-cert engine into a 5-gate engine with the new multi-hop-provenance gate.
- **MID-TERM ANCHOR (sleep consolidation v0)**: ship AMIE 3 over the 41k-atom snapshot in an offline pass; materialize a delta of inferred edges + a candidate set of new schema rel_types (rule-head promotion); review-gate before merge. Cost-model tier; substrate-novel because cert-gated.
- **MID-TERM ANCHOR (active ingest v0)**: wire Kajino-style uncertainty sampling + AMIE-PCA cardinality flags into the Bucket B ingest pipeline as a "next-ingest decision" subsystem; the existing edge-budget + 0-phantom + cross-corpus completeness gates compose cleanly.
- **EXCLUDE from cert-path**: RotatE/BoxE compositional embeddings + R-GCN/CompGCN layer-stacks. They are useful as ranking auxiliaries but cannot serve as the cert-grade composition primitive.

## Calibration

Lit-scan calibration penalty applied (per [[feedback-lit-scan-calibration-penalty]]):
- Path-walking RL (MINERVA) for OUR typed-edge graph: published P ~0.70 on standard benchmarks; deflated to **P=0.50** for our 41k-atom graph (uncharted density regime; substrate-novel relation set).
- AMIE 3 rule mining: published P ~0.80 for finding usable rules on Wikidata-scale; deflated to **P=0.55** for our smaller graph (edge density may not yet support rich rules).
- ConMask / Kajino active learning: P=0.50 (cap; pattern is architecturally compatible, integration cost dominates).

Novel-synthesis cap at 0.50 honored: the multi-hop-provenance gate as a CERT-CONDITION (not just a metric) is substrate-novel; cap respected.

## Citations (verified count: 12)

1. Das et al., MINERVA, ICLR 2018 — https://arxiv.org/abs/1711.05851
2. Sun et al., RotatE, ICLR 2019 — https://arxiv.org/abs/1902.10197
3. Yang/Yang/Cohen, Neural LP, NeurIPS 2017 — https://arxiv.org/abs/1702.08367
4. Vashishth et al., CompGCN, ICLR 2020 — https://arxiv.org/abs/1911.03082
5. Meilicke et al., AnyBURL, VLDB J. 2023 — https://link.springer.com/article/10.1007/s00778-023-00800-5
6. Lao/Mitchell/Cohen, PRA, EMNLP 2011; Nickel et al. survey 2015 — https://arxiv.org/pdf/1503.00759
7. Paulheim, KG Refinement Survey, Semantic Web J. 2017 — https://www.semantic-web-journal.net/system/files/swj1167.pdf
8. Lajus/Galarraga/Suchanek, AMIE 3, ESWC 2020 — https://link.springer.com/chapter/10.1007/978-3-030-49461-2_3
9. Cui et al., Generative Adaptive Replay for Temporal KG, ACL 2025 — https://aclanthology.org/2025.acl-long.537.pdf
10. Daruna et al., Continual Learning of KG Embeddings, 2021 — https://arxiv.org/pdf/2101.05850
11. Kajino et al., Active Learning for Multi-relational Data Construction, WWW 2015 — https://dl.acm.org/doi/10.1145/2736277.2741103
12. Shi & Weninger, ConMask Open-World KG Completion, AAAI 2018 — https://arxiv.org/abs/1711.03438

Next-drill candidate: **provenance-gate falsification math** — derive the path-density / rule-density floors below which MINERVA/AMIE structurally cannot pass on our graph (substrate-physics framework synthesis; not a lit-scan).
