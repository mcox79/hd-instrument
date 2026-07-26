# KB Foundation Conversion — Scoping (Director-synthesized 2026-07-26)

Synthesized in main thread from a direct filesystem probe + the grounding/CLS/reader sub-agent (a2a544a70) + the optimal-state audit R1 intel, after the parent scoping agent failed to converge on a written doc. Serves THE_PLAN's "KNOWLEDGE-ACQUISITION ARCHITECTURE" (seed -> read -> sleep). READ-ONLY findings; no builds started.

## 1. RAW KB INVENTORY (on disk, verified)
- **ConceptNet 5.7 (FULL):** `data/conceptnet/conceptnet-assertions-5.7.0.csv.gz` (498 MB) + `data/conceptnet/heldout_edges.jsonl` (1.4 MB — a held-out slice ALREADY reserved) + `cached_conceptnet/`.
- **CSKG (FULL, pre-merged):** `data/grounding_testbed/cskg.tsv.gz` (112 MB) + `PROVENANCE_cskg.md`. CSKG already merges ConceptNet + WordNet + Wikidata + others into one typed graph — **the natural base for the foundation.**
- **ATOMIC (FULL):** `data/atomic_kb/v4_atomic_{all_agg,trn,dev,tst}.csv` (~58 MB) — inferential/if-then commonsense.
- **WordNet:** `data/wordnet_cache/` + small extracts `data/wordnet_noun_semantics_kb_v1/kb.json` (65 KB) + `_v2_breadth`.
- **Grounding norms** `data/grounding_testbed/`: Lancaster sensorimotor (39,707 words; 6 perceptual + 5 action modalities), Brysbaert concreteness (39,954), Warriner VAD (13,915), Kuperman AoA (51,715). **Binder-65 experiential set = NOT on disk (VET'd: zero repo hits).** Lancaster is our real experiential grounding.

## 2. IS THERE A PRIOR BUILT FOUNDATION? — NO (full), YES (samples + methodology)
- `data/_cskg_cache/` holds only small experiment SAMPLES: `cskg_core_k10_n3500_s{7,13,17}.pkl` (3,500-node subgraphs) + `cskg_core_k8_n1500`. These are per-experiment cores, NOT a landed full foundation.
- No consolidated full-scale foundation store exists in `data/substrate_index/`. So the "convert to optimized foundation" build IS genuinely needed — but build ON the extensive prior CSKG methodology (dozens of `exp_*_cskg_*` cells) + reuse `hdlab/hd_fact_store.py` (sharded CG store schema, RAM-bound not crosstalk-bound, 100k proven).

## 3. THE SUBSTRATE ALREADY IS OUR PROJECT MEMORY (dogfood — USER point 2026-07-26)
- Director-KB continuous ingest: last run = **2,660,569 triples**; discovered **16,034 notes**, 5,862 metrics, 3,229 preregs, 532 memories, etc. Query via `tools/director_kb_query.py "<question>" --source-class=note` returns glass-box results (cosine + source file + IS_CHUNK_OF/SECTION_HEADER/CHUNK_CONTENT edges). **Search should be a substrate query, not a grep over 26k files.**
- TWO DEFECTS: (a) continuous ingest now FAILS on `OSError WinError 1450 (insufficient system resources)` — the tree is too big; index going stale (4 failed ingests). (b) retrieval relevance modest (~0.30 cosine on a direct topical query) — loops back to the learned-representation mission.
- INSIGHT: the substrate-as-memory loop (ingest -> consolidate -> query our own notes) is the MICROCOSM of the reader->sleep->foundation loop. Making our memory reliable = building the capability. First customer = ourselves.

## 4. READER + SLEEP LOOP ALREADY EXISTS (prototype)
- **Reader:** `hdlab/situation_reader.py` (read) + `hdlab/clarify_gate.py` (flag unknowns) — real, banked.
- **Read->flag->condense->sleep loop:** `exp_ingest_learn_sleep_loop_cycle1_v1` = CYCLE_COMPLETE (knowledge moved the hard probe; gate + MDL-gated rule both fired), cycle2/3 MIDDLE_BAND/coverage-limited. Validated only on small graded-reader curriculum, NOT KB-scale.
- **Sleep-replay consolidation:** `exp_substrate_knowledge_promotion_p4_replay_consolidation` = HARD_PASS (6 coherent clusters from 83 replayed atoms; read-only candidate-surfacer). Fast/slow dual-weight CLS (`exp_two_substrate_fastslow_cls`) = HARD_FAIL on the 0.85 bar (needs work).
- **CLIMB is NOT a reader** — it's a retrieval-QA benchmark harness ("climbing the ARC accuracy curve"), no write-path.

## 5. TARGET "OPTIMIZED FOUNDATION" (glass-box, NO borrowed vectors as encoding)
Stores symbolic nodes + typed vetted edges + measured grounding attributes ONLY (concept encoding is LEARNED downstream by the self-teacher). Pipeline: canonicalize concept identity (surface-string collisions, sense granularity); vet/filter per relation-type (drop noisy/crowd edges); dedup; attach grounding norms by lemma match (partial coverage, concrete >> abstract); reserve a held-out edge slice for proving reasoning-not-parroting (ConceptNet's `heldout_edges.jsonl` already exists as a template).

## 6. INTERFACE TO LEARNING + SLEEP (the coupling)
Foundation = (a) R3/R4 self-teacher's positive-source: a concept's relational neighbors are its positives for EARNING meaning (start from `teacher_free_relational_encoder_cn_subgraph_v1`, RKD-only — NCE is a proven geometry-corruptor; `v4_joint_reverify_relock` already shows dense~0.90 mid-scale via in-batch RKD; open gaps = full-178k scale + teacher-free weaning), and (b) the target the reader adds to and sleep consolidates into.

## RECOMMENDED SEQUENCE (each can-fail, brain-faithful, VET-able)
1. **[HIGHEST LEVERAGE / first build] CSKG -> optimized foundation store, at real scale.** Load full `cskg.tsv.gz`; measure quality (node/edge counts, relation-type distribution + label precision, duplicate rate, concept-identity collisions, grounding-norm coverage %); canonicalize + vet + dedup + attach grounding; land a sharded glass-box foundation store (reuse `hd_fact_store.py`); reserve held-out. Can-fail gate: held-out relation reconstruction / label-precision vs a shuffled-relation control.
2. Wire the teacher-free relational encoder (self-teacher) to learn concept meaning FROM the foundation (R1 objective at scale + R3/R4), judged on held-out-to-new-concept generalization.
3. Scale the reader+sleep loop (situation_reader + clarify_gate + condenser + learner) from graded-reader to KB-scale so new material is added + consolidated into the foundation.
4. (Parallel infra) Fix the director-KB continuous ingest (resource-bound) so the substrate-as-memory stays current — the dogfood microcosm of step 3.
