# Pre-reg: CSKG -> optimized glass-box foundation store v1 (cskg_foundation_v1)

Date: 2026-07-26. Cell: `experiments/exp_cskg_foundation_v1.py`. Author: exp_dev.
Serves THE_PLAN knowledge-acquisition architecture (seed -> read -> sleep). First build of the
knowledge foundation. Data-artifact landing (NOT a canonical substrate_index bank; NO origin push).

## WHAT
Stream the full CSKG (`data/grounding_testbed/cskg.tsv.gz`, 6,001,531 rows), apply the cross-cutting
SPINE relation filter, canonicalize concept identity, dedup, k-core decompose (LABEL the dense 12-14
band; KEEP the sparse periphery as the reader/sleep growth surface), attach 4 grounding-norm sets by
lemma, reserve a held-out edge slice, and land a sharded glass-box foundation store in the
`hdlab/hd_fact_store.py` field schema (SYMBOLIC nodes + typed edges + measured grounding attrs ONLY;
NO borrowed vectors -- concept encoding is LEARNED downstream).

## AUTONOMY DECISIONS (all exp_dev calls; justified)
- **Spine keep-set** (33 relation types): ATOMIC at:* + ConceptNet causal/functional/lateral +
  mw:MayHaveProperty. DROP the 79.1% lexical/taxonomic dilution (RelatedTo/Synonym/Antonym/FormOf/
  DerivedFrom/IsA/HasContext/EtymologicallyRelatedTo/SimilarTo/DistinctFrom/DefinedAs/InstanceOf/
  fn:HasLexicalUnit/dbpedia*/SymbolOf/mw:SameAs). Locked from the FULL measured relation distribution.
- **Store the FULL spine** (~501k nodes / ~1.18M edges), NOT just the dense core. k-core membership
  is a node ATTRIBUTE (`kcore`, `is_dense_core = coreness>=12`), not a filter (coordinator scope
  refinement 2026-07-26: the sparse periphery is the growth surface the reader+sleep loop densifies).
- **Canonicalization = node-URI lemma** (`/c/en/dog/n/wn` -> `dog`; `at:personx_bakes` ->
  `personx_bakes`), then normalize (lower; non-alnum-run -> `_`; strip). Chosen over the CSKG label
  column because that column carries sense-GLOSSES (e.g. `/c/en/act/n/wn/law` -> label "coerce"),
  which OVER-SPLIT identity. DELIBERATELY merges POS/sense suffix variants (sense granularity deferred
  to the learned encoder; glass-box one-lemma-one-node). Surface-collision merge documented; collision
  rate reported.
- **Trust**: source-token -> TRUST_HIGH for curated (CN/WN/WD), TRUST_MID otherwise (AT/VG/FN crowd/
  derived). SOURCE-TRUST vetting, not correctness (per hd_fact_store design).
- **Held-out**: 2% of unique typed edges (seed 20260726), reserved (own file, excluded from shards).
- **Shards**: 16 edge shards by source-node index. nodes/grounding/heldout single files.
- **hd_fact_store variant**: PLAIN/RANDOM-filler HDFactStore only. GloVe/semantic-filler variant is
  FORBIDDEN (no borrowed vectors -- hard project lock). Self-test round-trips the real plain store.

## CAN-FAIL GATE (pre-registered bands; discriminator = relation reconstruction)
Predict a held-out edge's relation from its endpoints' TRAIN relation-affinity:
`score[r] = (#train edges incident to head with rel r) + (#train edges incident to tail with rel r)`;
argmax. Model-free, glass-box. Evaluated on held-out edges whose BOTH endpoints are in the dense core
(coreness>=12) and retain >=3 train incidences (fires the discriminator on the reasoning-capable core).
- Controls: (1) BASE-RATE = predict the single most-frequent relation (mode). (2) SHUFFLED-RELATION =
  permute relation labels across ALL train edges before building affinity -> endpoint relation-profiles
  destroyed -> MUST collapse to base-rate (deterministic seed 424242).
- **HARD_PASS**: real_acc >= base_rate+0.10 AND (real_acc - shuffled_acc) >= 0.10 AND shuffled_acc <=
  base_rate+0.03.
- **HARD_FAIL**: real_acc < base_rate+0.03 (no structure beyond mode) OR shuffled_acc > base_rate+0.10
  (control did not collapse -> gate not discriminating / leak).
- **MIDDLE_BAND**: otherwise.
CAN-FAIL: a foundation with no relational locality (random graph) gives real~=shuffle~=base -> HARD_FAIL.
Shuffle collapse is by-construction the negative control.

## PASS FLOOR (density gate, from blueprint 2026-07-10)
Dense-core (k>=12) must clear >=5000 nodes @ internal avg-deg >=37 on the SPINE (FB15k-237 caliber).

## BLUEPRINT HONESTY ANCHORS (validity check on FULL; report mine vs these)
spine directed edges 1,244,688; spine nodes 501,391; spine simple edges 1,184,796; 12-core 23,632 @
38.4; 13-core 17,793 @ 43.3; 14-core 10,731 @ 55.0; cliff at k=15. (Node count will differ modestly
from 501,391 by the deliberate lemma sense-merge; edges must match closely. An ~80k-node 10-core @ 42
would mean raw CSKG was fed = WRONG.)

## SMOKE (measured this session, FULL-scale stream, node-id canon)
spine edges 1,244,136; nodes 482,588; simple 1,174,080; 12-core 24,336 @ 39.18; 13-core 19,396 @ 43.15;
14-core 13,500 @ 50.89; density-floor PASS. Gate HARD_PASS: real 0.6961, shuffled 0.2368, base 0.2591
(mode /r/LocatedNear); real-shuffle 0.459, real-base 0.437. Grounding frac_any 0.0525 (single-token
concept coverage high: AoA 22,307 / concreteness 18,761 of ~41k single-token nodes; concrete>>abstract,
mean concreteness matched 3.36). collision_rate 0.0367; duplicate_rate 0.0044. All tight to blueprint.

## SCHEMA-VET N/A DECLARATIONS (build cell, not a substrate-physics sweep)
- arms_differ (META_RULE_AF): N/A -- no mechanism-vs-baseline arm tensors; gate is real-vs-shuffle
  accuracy scalars (reported distinct).
- CRLB / capacity-feasibility: `crlb_n/a` -- no HD noise floor; gate is a symbolic count predictor.
- cardinality_ok (META_RULE_H): N/A -- no seed x sweep grid; single deterministic build.
- baseline_in_band (AG): base_rate 0.259 is well inside (0.05, 0.95); real 0.696 not saturated.
- discriminator survives scale: smoke IS full-scale (option A); gate fires at full N.
- final_metrics_atomicity: tmp_replace (os.replace).
- deterministic_seeding: fixed int seeds; sorted() dedupe; no hash()-seeded RNG, no list(set()).
- real_code_path: self-test constructs the REAL plain HDFactStore + round-trips core edges.
- progress_logging: print_flush_true + _heartbeat.jsonl (build < 60s but instrumented).

## LANDS
`data/cskg_foundation_v1/`: nodes.jsonl, edges_shard_00..15.jsonl, heldout_edges.jsonl, metrics.json.
Metrics mirror at `data/exp_cskg_foundation_v1/metrics.json`. VET-able artifact; NOT a canonical bank.
