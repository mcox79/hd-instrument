# META: cert chain lives in cert_ledger SEMANTICS, not relations.jsonl TOPOLOGY

Date: 2026-06-22
Triggered by: substrate_self_map_v2 single-seed full-scale run (HELD by Exp-Dev,
not dispatched); pre-reg-vs-empirical discrepancy.

## The empirical discovery

substrate_self_map_v2 was authored to map cert_ledger relational structure
substrate-side via the natural cell mechanism: (a) load chain-grade atom_ids
from `cert_ledger.jsonl`, (b) load relations.jsonl across all corpora and
restrict to triples where BOTH endpoints are chain-grade, (c) ingest into
KGStore + traverse via multi_hop, (d) cluster anchors by neighborhood Jaccard.

The pre-reg estimated the chain-grade subgraph would contain ~8000 relations
across ~17 relation types -- the FULL-Store inventory.

Actual measurement on the real data:

- 447 chain-grade atoms
- 16 relations with both endpoints chain-grade
- 7 non-trivial relations after dropping self-loops
- 2 distinct relation types in the chain-grade subgraph

Cell-author's single-seed full-scale verdict:
- clusters = 1
- avg_J = 0.020
- recall = 1.000
- n_llm = 0

Mechanism null on this scope; would HARD_FAIL by substrate-resemblance floor.

## The META insight

The cert chain is not a TOPOLOGICAL structure (atoms linked via relations).
The cert chain is a SEMANTIC label borne by individual atom records in
cert_ledger.jsonl -- each chain-grade atom is tagged `cert_status:
chain_grade` and carries provenance via `cell_commit`, `referent_pointer`,
`verdict`, etc. Chain-grade atoms relate to each other primarily by
co-membership in the cert ledger, by shared experimental authorship, by
verdict-class co-occurrence -- not by edges in relations.jsonl.

Relations.jsonl is dense over the FULL atomized Store (200k+ relations over
~177k atoms). Most relations involve T1/T2 primitives (vector_space,
inner_product, cosine_similarity, etc) that are NOT chain-grade --
chain-grade atoms are mostly T3 EXP_* experiment records. The relations
that DO involve chain-grade atoms typically point OUTWARD (an experiment
DEPENDS_ON a primitive), with the experiment being chain-grade and the
primitive being only atomized.

## Mechanism implication

Substrate self-mapping cannot find structure by restricting to chain-grade-
internal relations -- the subgraph is empty. Mechanism implications:

1. v2b (broadened scope, in flight): admit triples where EITHER endpoint is
   chain-grade. Substrate maps how chain-grade atoms sit in the broader
   atomized Store via outward DEPENDS_ON / IS_A / SPECIALIZES edges.

2. Option 2 (deferred): ingest the FULL relations.jsonl (~200k relations
   over ~177k atoms). Substrate maps the entire Store topologically.
   Chain-grade atoms are still the anchors but the codebook is the full
   atomized universe.

3. Cert-chain SEMANTICS is the OTHER kind of evidence: substrate could
   self-map via co-membership in cert_ledger fields (shared cell_commit
   prefix, shared atomized_by, shared verdict-class, supersedes-chain
   structure). That is a separate cell (not Option 1 or Option 2).

## Pre-reg discipline note

The substrate-resemblance HARD_FAIL band (avg_J < 0.10) was correct in
pre-reg, given v1's chain-grade family clustering. The v2 cell did not fail
the gate by mistake; it correctly identified that the chain-grade-internal
relation subgraph cannot support substrate-side clustering. The fix is to
broaden the scope (v2b) or change the relational substrate entirely
(Option 2), not to relax the band.

## Counts (frozen 2026-06-22)

- Total atomized atoms (atoms.jsonl across all corpora): ~177k
- Total relations (relations.jsonl across all corpora): ~200k (estimate;
  not directly counted here)
- Chain-grade atoms (cert_ledger.jsonl, chain_grade after supersedes-fold): 447
- Chain-grade-internal relations (both endpoints chain-grade): 16
- Chain-grade-internal relations, self-loops dropped: 7
- Distinct relation types in chain-grade subgraph: 2

## Atomize this finding

This META insight is a candidate atom (T3 META cert-architecture). Suggested
atom_id: `META/cert_chain_in_ledger_semantics_not_relations_topology_v1`.
Atomization is deferred to Skunkworks per role-separation; this note exists
to capture the empirical discovery + mechanism implication for downstream
substrate-self-mapping work.
