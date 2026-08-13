# Multi-source unknown-word / concept LOOKUP: what exists, what runs, what is reachable (2026-08-13)

READ-ONLY audit. No code modified, nothing committed, `data/exp_anchor_pool_expansion_v1/` untouched.
Every claim below carries a file:line or a disk-verified artifact path. Self-tests were RUN, not
assumed. Written to answer: *when the substrate hits a word or concept it does not know, does a
learning system look it up across a number of databases to find a grounded definition it can bank?*

---

## HEADLINE (three sentences)

1. **A multi-source GATHER -> REASON -> GATE -> FOUNDATION/MIDDLE loop genuinely EXISTS as working,
   self-tested, HARD_PASS-on-real-data code** (`hdlab/three_tier_loop.py` + `hdlab/gather_reason.py`
   + `hdlab/prelim_tier.py`, plus 4 experiment drivers, one of which reads CSKG / CauseNet /
   ProPara-KB / go.obo as four genuinely distinct sources). The user is right that it was built.
2. **It is NOT reachable from the reading loop.** `hdlab/reading_grounding_loop.py`'s runtime
   transitive import closure is 40 `hdlab.*` modules and contains none of them; zero experiment
   cells import both. When an unknown lemma is encountered, the ONLY thing that happens is a
   context-vector trace is flagged into a Library — no database is consulted.
3. **It is CONCEPT-level, not word-level, and its items are (subject, relation, candidate) triples
   over KG entity strings — never a dictionary definition of a lemma.** The registry itself already
   records this honestly: every relevant row is `integration_status: "WIRED"` **and**
   `pipeline_status: "WIRED_BUT_NOT_PIPELINE_REACHABLE"`.

---

## 1. INVENTORY — what exists

### 1a. The three-tier multi-source loop (hdlab organs)

| Path | Lines | What the code actually does |
|---|---|---|
| `hdlab/three_tier_loop.py` | 214 | Assembly glue. `ThreeTierLoop` = strict GATE (`grounding_acquisition_loop.consolidation_pass`, exposure>=8 + consistency>=0.75) writing into an `HDFactStore` FOUNDATION, plus a retain-forever MIDDLE tier (`prelim_tier.TierState`) swept for near-concept clusters. `answer()` (`:197-208`) is **priority-order** FOUNDATION -> MIDDLE -> UNRESOLVED, explicitly **not** score fusion. One documented wiring choice: `self.tier_state.native_store_gen = self.foundation_store` (`:159`). |
| `hdlab/gather_reason.py` | 298 | The "GATHER". `ca3_relevance_gather` (`:82`) is a CA3/DG matching-pursuit peel-loop over a **caller-supplied in-memory FHRR codebook**; `fanout_two_hop` (`:116`) is a K<=2 hop over `hdlab.kg_traversal.KGStore`. **It queries no database.** The "sources" are whatever the caller pre-loaded into the codebook/KGStore. |
| `hdlab/prelim_tier.py` | 495 | The MIDDLE tier: `TierState.prelim_lib` is a `Library` deliberately never routed through `consolidation_pass`, so items never leave PENDING (retain-forever); `prelim_store` is a second `HDFactStore` at `TRUST_LOW`, answered from BEFORE any raw source. `update_prelim_and_generalize` does the CA3/DG cluster sweep + combined-evidence promotion. |
| `hdlab/gap_driven_reader.py` | 450 | "What should I read next": `PrereqTracker` co-occurrence bookkeeping x `GapDetector.familiarity` -> `identify_missing_prerequisites` (`:151`) -> `rank_material` (`:192`). **Ranks unread documents; it does not look anything up.** |
| `hdlab/gap_detector.py` | 326 | The "do I already know this" familiarity/novelty margin (CA3/CA1). Detects the gap; has no resolution path. |

### 1b. The one genuine dictionary-lookup organ (word-level)

| Path | Lines | What it does |
|---|---|---|
| `hdlab/wordnet_polarity_propagation.py` | ~300 | `dictionary_lookup(lemma)` (`:159`) — a **live** `nltk.corpus.wordnet` query: Stage A antonym-opposition against a 52-word anchor, Stage B `path_similarity` neighbour vote. Returns `DictLookup(polarity, confidence, ...)`. |
| `hdlab/word_learning_tool.py` | ~110 | "look the OOV word up in the dictionary FIRST, then confirm/refine through story CONSEQUENCE" (module docstring, USER 2026-08-06). Converts dictionary confidence to Bayesian pseudo-counts injected once into `consequence_learning_loop.learn_corpus(dictionary_priors=...)`. |

**Scope limit, load-bearing:** this returns a **POS/NEG result-valence for an outcome VERB**. It is
not a definition, not a sense, not a gloss, and it banks into
`verb_lexical_similarity.ACQUIRED_OUTCOME_VERB_FEATURES` — not into the foundation fact store.

### 1c. The multi-source ARENA + external-lookup active-learning family (experiment cells)

- `experiments/exp_multisource_arena_v1.py` (+ 6 siblings: combination_menu, conjunction_menu,
  continual_retention, phase_boundary, temporal_accrual_fair, temporal_hold_recover) — a 4-axis
  (unexpectedness / schema_fit / recurrence / importance) **ingest-gate arena**. Pure numpy over
  four synthetic generative processes; it is a gate-design testbed, not a live lookup.
- `experiments/exp_active_learning_loop_gap_detect_lookup_revise_v1.py` / `_v2.py` (45KB / 78KB) —
  literally "gap-detect -> internal-retrieve -> **external-lookup** -> reliability/coherence gate ->
  provenance-revise". **Caveat from its own docstring:** the lookup content is real Princeton
  WordNet gloss text *harvested once at authoring time and FROZEN as static Python literals* — the
  cell has "NO nltk/network dependency at runtime". It is a wiring proof over a frozen 48-item
  fixture, not a live database call.

### 1d. The GATHER organ that really does span many databases

`hdlab/director_kb.py` + `director_kb_query.py` + `director_kb_chunk_ingest.py`, index at
`data/substrate_director_kb_v1/` (manifest read this pass): **1,288,991 entities / 2,643,704 triples
/ 167,384 chunks**, sources = wordnet, verbnet, framenet, gene_ontology, kegg_pathway, neurolex,
ConceptNet-derived concept_relations, plus notes/preregs/metrics. Last ingest **2026-08-13 09:45**
(live). The design audit classifies it correctly: *"a **build-time indexer**, not a live per-question
fan-out-and-fuse"* (`notes/director_three_tier_knowledge_architecture_design_audit_2026-08-11.md:74`).
Grep for consumers inside `hdlab/`: exactly one mention, in `kb_encoder_registry.py:4`. It is the
**Director's** KB, queried by `tools/director_kb_query.py` for the agent — not by the substrate at
read time.

---

## 2. DOES IT RUN? (design note vs code exists vs code works)

All commands run this pass with `.venv/Scripts/python.exe`.

| Target | Command | Result |
|---|---|---|
| `hdlab/gather_reason.py` | `python -m hdlab.gather_reason` | **PASS** — `ALL SELF-TESTS PASSED`; `restrict_hop1_to_load_bearing: true` |
| `hdlab/prelim_tier.py` | `python hdlab/prelim_tier.py` | **PASS** — `ALL SELF-TESTS PASSED` (fidelity_guard, hub_exclusion, cluster_key_fn + coherence_fn load-bearing) |
| `hdlab/three_tier_loop.py` | `python -m hdlab.three_tier_loop` | **N/A by design** — prints "assembly module, no standalone self-test payload"; witness is the pytest below |
| `hdlab/gap_driven_reader.py` | `python hdlab/gap_driven_reader.py` | **PASS** — 9 self-tests incl. end-to-end real-code-path identify-and-ground |
| `hdlab/word_learning_tool.py` | `python hdlab/word_learning_tool.py` | **PASS** — `ALL SELF-TESTS PASSED` |
| `hdlab/wordnet_polarity_propagation.py` | `python hdlab/wordnet_polarity_propagation.py` | **PASS** — incl. `scramble_flips_polarity: true` |
| witnesses | `pytest verification/test_three_tier_loop_e2e.py test_prelim_tier.py test_gather_reason.py -q` | **9 passed in 57.96s** |

**Three states, explicitly:**
- **DESIGN NOTE ONLY:** true holistic multi-source SCORE FUSION ("combination of ALL sources"). Named
  Gap **G1** in the design audit (`:212-216`) and re-disclosed in `three_tier_loop.py:54-60`. Nothing
  on disk does this; `answer()` is first-hit priority order.
- **CODE EXISTS + WORKS (self-tested and run on real data):** three_tier_loop, gather_reason,
  prelim_tier, gap_driven_reader, gap_detector, wordnet dictionary_lookup, word_learning_tool.
- **CODE EXISTS BUT MEASURED-FAILED:** `exp_combined_dictionary_consequence_word_learning_tool_v1`
  (**HARD_FAIL**, dict=0.2222 / conseq=0.1944 / combined=0.1944 vs floor 0.6389, dict coverage
  6/33); `exp_crutch_fade_social_iqa_v1` (**HARD_FAIL**);
  `exp_three_tier_loop_genuine_cross_source_corroboration_v1` (**HARD_FAIL**, see §7).

---

## 3. REACHABILITY — the decisive question

### 3a. Forward trace: reading loop -> lookup? **NO.**

Runtime transitive closure, computed by importing the module and listing `sys.modules`:

```
python -c "import hdlab.reading_grounding_loop; [print(k) for k in sorted(sys.modules) if k.startswith('hdlab')]"
-> 40 modules
```

The 40: ablation, animacy_lexicon, atoms, binding, bundling, cleanup_family, closed_class_lexicon,
consequence_learning_loop, coreference_resolver, event_bundle, frame_induction, gap_detector,
goal_typing, grounded_similarity, grounding_acquisition_loop, hd_fact_store, iterative_attractor,
learner(+core/registry/4 plugins), lexical_similarity, memory, modulators, reading_grounding_loop,
role_slot_summarizer, self_improving_loop, semantic, situation_model_accumulate, snapshots,
state_of_mind, thematic_role_labeler, tracing, verb_lexical_similarity, working_memory.

**Absent: `three_tier_loop`, `gather_reason`, `prelim_tier`, `gap_driven_reader`, `kg_traversal`,
`director_kb*`, `word_learning_tool`, `wordnet_polarity_propagation`.**

Direct imports (`hdlab/reading_grounding_loop.py:86-103`): grounding_acquisition_loop,
hd_fact_store, gap_detector, thematic_role_labeler(`lemma_word`), closed_class_lexicon.
`hdlab/grounding_acquisition_loop.py:71-76`: consequence_learning_loop (`credit_window`,
`_credit_targets`, `teacher_verdict` only — **not** `learn_corpus`, so the `dictionary_priors`
hook at `consequence_learning_loop.py:292` is never on this path), self_improving_loop,
verb_lexical_similarity, hd_fact_store.

**What actually happens on an unknown word** — `process_sentence`, `hdlab/reading_grounding_loop.py`:
- `:1050` iterate `content_lemmas(sentence)`
- `:1068` `if not is_gap(state, lemma): continue` — the gap IS detected (`GapDetector`)
- `:1075` `ctx = _encode(sentence, lemma)` — a bag-of-content-words context vector
- `:1078` `state.library.flag(lemma, episode_id, "POS", ctx, pass_idx, ...)`
- ...and that is the end of it. There is no branch, hook, or callable parameter on
  `process_sentence` or `checkpoint` that could reach an external source.

Meaning-candidate pool (confirming `notes/downstream_bottleneck_trace_2026-08-13.md`): `state.space`
is written at exactly three sites — `:1055` seed vocabulary, `:1297` `seed_from_bundle` for a lemma
this same loop just grounded, and `:1063` the default-OFF `anchor_pool` (only
`experiments/exp_anchor_pool_expansion_v1.py` passes it). `canonicalize()` (`:599`) argmaxes over
that pool. **No external source can enter it.**

**External IO inside the closure** (`grep -c "open(|requests.|urllib|glob.glob|sqlite3|nltk"`):
`reading_grounding_loop` 0, `grounding_acquisition_loop` 0, `gap_detector` 0, `hd_fact_store` 0,
`consequence_learning_loop` 0, `verb_lexical_similarity` 0, `lexical_similarity` 0.
Two non-zero, both benign and neither a definition lookup:
- `closed_class_lexicon.py:76,124,140` — reads/writes a local CoNLL-U-derived cache of function words.
- `animacy_lexicon.py:52,82` — a **live** `nltk.corpus.wordnet` call, reached because
  `thematic_role_labeler.py:49` imports `lookup_animacy`. But the reading loop imports only
  `lemma_word` (`reading_grounding_loop.py:102`, used once at `:195`), and `lemma_word`
  (`thematic_role_labeler.py:241-253`) uses WordNet **morphy for lemmatisation only**.
  So: WordNet is touched on the unknown-word path, purely as a morphological normaliser. No synset,
  no gloss, no hypernym, no bank. Calling that "looking the word up" would be a misread.

Cross-check: of the 13 cells importing `reading_grounding_loop`, **zero** also import
three_tier_loop / gather_reason / prelim_tier / director_kb / conceptnet / cskg.

### 3b. Reverse direction: does the lookup have its own driver? **YES — four of them, all landed.**

Entry point is an experiment cell, invoked as `python experiments/<cell>.py [--self-test|--smoke]`.
Verdicts read off each `data/<cell>/metrics.json` this pass:

| Cell | Mode | Verdict (verbatim) |
|---|---|---|
| `exp_three_tier_loop_real_corpus_gap_stream_v1` | full | `HARD_PASS_three_tier_dynamics_load_bearing_on_real_data` — `delta_B_frac=1.0000`, `delta_C_foundation_frac=0.6452`, scramble 5 vs real 62, no_leak=True |
| `exp_three_tier_loop_concept_coherence_v1` | full | `HARD_PASS_concept_coherence_unblocks_cross_source_paraphrase` — 21/21 previously-blocked 2+-source gaps now retain (n_middle 36 vs 15) |
| `exp_three_tier_loop_independence_weighted_confirm_v1` | full | `HARD_PASS_independence_weighted_corroboration_crosses_gate` — 2+-source crossing 36/36, but **end-to-end `n_combined_promoted=0`** |
| `exp_three_tier_loop_genuine_cross_source_corroboration_v1` | full | `HARD_FAIL_thin_cross_source_not_mechanism_failure` — see §7 |
| `exp_state_of_mind_relevance_gather_reasoning_union_v1` | full | `HARD_PASS_state_of_mind_gather_load_bearing` (N=121; arm3@5=0.3802 vs 0.0413) |
| `exp_gap_driven_reader_controlled_v1` | full | `HARD_PASS` |

**Has it run at scale?** Yes, on real structure: N=121 real MadeOf-bridge gap targets, 62 eligible,
over the full 1,213,912-edge CSKG. **Honest scope limit carried in the registry row itself:** the
6-encounters-per-gap multiplicity in the HARD_PASS cell is *templated-synthetic text embedding real
entity names* — "a real corpus is not claimed to naturally supply 6 independent mentions per gap".
The cell that replaced those with genuine distinct-source encounters is the one that HARD_FAILed.

---

## 4. CONCEPTS vs WORDS — the user's own suspicion is correct

**The lookup path is concept-level. The reading loop is lemma-level. They do not share a
representation.**

- A "concept" in the three-tier path is a **plain entity/concept STRING** taken from a KG
  (CSKG node names such as `wood`, `coal`, `whole0`). Item identity is
  `gap_item_key(subject, relation, candidate) -> "subject||relation||candidate"`
  (`hdlab/three_tier_loop.py:85-95`) — an ordered 3-part gap-FACT key, deliberately generalized from
  `prelim_tier.default_pair_key`'s symmetric 2-part pair. Vector form is FHRR via
  `script_grain_acquisition_loop.build_instance_register` with AGENT/PATIENT = (subject, candidate).
- Concept *identity across paraphrases* is decided by
  `hdlab.lexical_similarity.concept_similarity` over `CONCEPT_FEATURES`
  (`exp_three_tier_loop_concept_coherence_v1.py:173,195`, threshold 0.50). **`CONCEPT_FEATURES` was
  measured this pass to hold 359 entries** (`len(CONCEPT_FEATURES) == 359`), e.g.
  `air -> ['RESPIRATION_MOVE_ROLE','RESPIRATION_DOM']`. A hand-authored 359-concept lexicon is the
  ceiling on what this concept-matcher can call "the same concept".
- There is **no synset / sense-ID / ConceptNet-URI representation anywhere** in the loop. Nothing
  maps an unknown surface lemma to a concept node.
- The reading loop's unit is a normalized lemma string (`normalize_lemma`, `:186`) whose "meaning"
  is another lemma string chosen by `canonicalize` argmax. So even if the two were wired, the
  handoff (lemma -> KG concept node) does not exist as code.
- The word-level lookup that DOES exist (`wordnet_polarity_propagation.dictionary_lookup`) is
  restricted to `wn.synsets(lemma, pos=wn.VERB)` (`:176`) and returns a polarity, not a definition.

---

## 5. KB DATA ON DISK, and who reads it

| Resource | Path | Size / rows (counted this pass) | Live reader? |
|---|---|---|---|
| CSKG foundation v1 | `data/cskg_foundation_v1/edges_shard_00..15.jsonl` | 16 shards, **1,213,912 rows**, ~200MB | Experiment cells only (`exp_state_of_mind_...:88` `CSKG_GLOB`, three_tier cells). No `hdlab/` module reads it. |
| ConceptNet 5.7 assertions | `data/conceptnet/conceptnet-assertions-5.7.0.csv.gz` | 498 MB | No live reader found; `backend/kb/conceptnet_ingest.py` is a one-shot ingester |
| ConceptNet held-out edges | `data/conceptnet/heldout_edges.jsonl` | **20,219 rows** | eval only |
| ATOMIC v4 | `data/atomic_kb/v4_atomic_all_agg.csv` | **24,313 rows** | folded into CSKG at build time |
| CauseNet-precision | `data/bio_kb_cache/causenet/causenet-precision.jsonl.bz2` | 11.6M pairs (cited) | streamed by `exp_state_of_mind_...:185` and the cross-source cell |
| Gene Ontology | `data/bio_kb_cache/go/go.obo` (36.7MB), `go-basic.obo` (32.2MB) | — | scanned by the cross-source cell; **measured to contribute ZERO** genuine evidence |
| KEGG / NeuroLex / FrameNet / VerbNet / WordNet caches | `data/bio_kb_cache/*`, `data/{framenet,verbnet,wordnet}_cache` | — | ingested into director_kb (build-time) |
| ProPara process-physics KB | `data/benchmark_trap_check/propara_process_physics_kb_v1.json` | 10.8 KB | cross-source cell |
| ProPara x ConceptNet index | `data/benchmark_trap_check/propara_conceptnet_index_traindev_v1.json` | 12.6 MB | benchmark cells |
| director_kb index | `data/substrate_director_kb_v1/` | 1,288,991 entities / 2,643,704 triples / 167,384 chunks; `E.pt` 10.6 GB; **ingested 2026-08-13 09:45** | **YES, live** — but by the *agent's* query tool, not the substrate's read path |
| Wikidata | `backend/kb/wikidata_dump_ingest.py`, `scripts/download_wikidata_dump.py` | ingest scripts exist under `backend/`/`scripts/` | Not part of `hdlab/`; no live reader in the grounding arc |

**Summary:** there is a great deal of KB data on disk and one live index over it (director_kb), but
**nothing in the reading/grounding path reads any of it.** The only KB touched at read time is
WordNet-morphy for lemmatisation (§3a).

---

## 6. REGISTRY — verbatim statuses (READ ONLY; file not modified)

`data/capability_registry.jsonl`, 123 rows. `integration_status` takes exactly four values across
the whole file: `WIRED` (72), `ISLAND` (25), `TRAPPED_SHARED` (24), `N_A_SHELVED` (2).

| id | `integration_status` | `pipeline_status` |
|---|---|---|
| `three_tier_loop` | `"WIRED"` | `"WIRED_BUT_NOT_PIPELINE_REACHABLE"` |
| `gather_reason` | `"WIRED"` | `"WIRED_BUT_NOT_PIPELINE_REACHABLE"` |
| `prelim_tier` | `"WIRED"` | `"WIRED_BUT_NOT_PIPELINE_REACHABLE"` |
| `gap_driven_reader_self_directed_order` | `"WIRED"` | `"WIRED_BUT_NOT_PIPELINE_REACHABLE"` |
| `gap_detector_familiarity_gate` | `"WIRED"` | `"WIRED_BUT_NOT_PIPELINE_REACHABLE"` |
| `reading_grounding_loop_definitional_reading_pipeline` | `"WIRED"` | `"WIRED_BUT_NOT_PIPELINE_REACHABLE"` |
| `cskg_foundation_v1` | `"ISLAND"` | (gate_decision `ALREADY_WIRED_VIA_DATA_ARTIFACT`) |
| `hd_fact_store` | `"WIRED"` | `"WIRED_BUT_NOT_PIPELINE_REACHABLE"` |
| `kg_ingest` (`hdlab/kg_traversal.py`) | `"WIRED"` | — |

**Do not read `WIRED` as "reachable".** Two rows say so in their own words:
- `gap_driven_reader_self_directed_order.gate_decision_target`: *"Validated standalone
  (exp_gap_driven_reader_controlled_v1 HARD_PASS full run); **NOT YET imported by
  hdlab/reading_grounding_loop.py itself as of this audit (grep-verified: zero hits)** — next step is
  to wire its read-selection into that loop's per-cycle ordering, currently hand-ordered curriculum."*
- `prelim_tier.gate_decision_target`: *"integration_status will read ISLAND/TRAPPED_SHARED until a
  real consumer imports the module (only the witness does today) — that is expected and honest for a
  same-day promotion, not a defect."*

**No registry row exists for** `word_learning_tool`, `wordnet_polarity_propagation`,
`grounding_acquisition_loop`, the `active_learning_loop` cells, or the `multisource_arena` family
(consistent with registry-hygiene gap **G7**).

---

## 7. PRIOR VERDICTS — dead ends and revival criteria (do not rediscover)

Primary source: `notes/director_three_tier_knowledge_architecture_design_audit_2026-08-11.md`
(32.8 KB, design/audit only, records the USER's 5-step architecture verbatim at `:8-18`).

Its **HEADLINE FINDING** (`:24-32`): *"The user's exact 5-step architecture is not hypothetical — an
~80%-complete implementation of it was already built and run end-to-end this session, and it
HARD_FAILED at full scale... the FADE half worked, the CONSOLIDATE/SWEEP/PROMOTE half did not clear
its own gates."*

Honest gaps (`:210-245`), all still open:
- **G1 — no live multi-source SCORE FUSION.** Every validated precedent takes the first hit in
  priority order. True fusion is *new work, not a wire-up*.
- **G2 — the SWEEP's clustering key is the diagnosed root cause** of the one real HARD_FAIL
  (`relation_family` = raw CSKG relation type is too coarse; only 2 clusters formed). Named the
  single highest-leverage fix. *Partially addressed since:*
  `exp_three_tier_loop_concept_coherence_v1` HARD_PASSed with a `concept_similarity` key.
- **G3 — the FHRR superposition store is unit-sound but real-corpus HARD_FAILED** (no rise, no
  fade/lesion gap, scramble didn't collapse). Diagnose before reusing in PARSE.
- **G4 — middle tier islanded in one cell.** *Closed 2026-08-11* by promoting `prelim_tier`.
- **G5 — the MDL conjunctive gate (`hdlab/learner`) was never actually invoked** (`mdl_gate_fn=None`
  at both call sites). Cheap untried lever.
- **G6 — `hdlab/reasoner.DerivationReasoner` is a disclosed dead end** ("below-bands walls on every
  arm", abandoned 2026-07-27). Do not silently reuse.
- **G7 — registry hygiene** (see §6).

Other landed negatives with revival criteria:
- `exp_three_tier_loop_genuine_cross_source_corroboration_v1`: **`HARD_FAIL_thin_cross_source_not_mechanism_failure`**
  — `g_full_combined_promotions=0`; `max_trace_g_full=3 < MIN_CONFIRM=4`. Measured: only 54/121 gaps
  (44.6%) have >=2 real distinct sources, max observed 3 (CSKG+CauseNet+ProPara-KB); go.obo
  contributes 0. **Revival criterion is explicit: this is a SOURCE-THINNESS failure, not a mechanism
  failure — it needs MORE independent databases, not different code.**
  `notes/research_three_tier_knowledge_sourcing_gather_layer_2026-08-11.md` (33 KB) is the ranked
  shopping list: Reactome + Rhea (typed reaction roles, CC BY/CC0) as the highest-fidelity pickup,
  CauseNet for scale, WorldTree for precision (EULA-gated), and a free near-zero-cost fix
  (`go-basic.obo` -> `go.obo`/`go-plus`, already partly done — `go.obo` is on disk).
- `exp_crutch_fade_social_iqa_v1` / `_v2_semantic_cluster_key`: both **HARD_FAIL**; registry row
  `crutch_fade_social_iqa` `gate_decision: SHELVE`,
  `status: honest_negative_fade_works_lift_below_band_2026-08-10`.
- `exp_combined_dictionary_consequence_word_learning_tool_v1`: **HARD_FAIL** (combined 0.1944 vs
  floor 0.6389; dictionary coverage only 6/33 lemmas, 3/16 on content verbs). The WordNet-lookup
  word-learning tool the USER asked for on 2026-08-06 was built, run, and did not clear its bands.
  Follow-up diagnosis: `notes/brain_fidelity_audit_word_learning_2026-08-12.md` (38.7 KB).
- `exp_active_learning_loop_gap_detect_lookup_revise_v1`: VET'd as a construction-determined
  **wiring proof**; v2 removed three named crutches and reached HARD_PASS — but on a frozen
  48-item WordNet-gloss fixture, not live lookup.
- `grounded_word_acquisition_loop_increment1`: registry `gate_decision: SHELVE`,
  `status: built_measured_HARD_FAIL_shelved_2026-08-06`.

**Current-arc silence, which is itself evidence:** `notes/STATUS.md`, `notes/WHERE_WE_ARE_NOW.md`
and `notes/THE_PLAN.md` contain **zero** occurrences of "three-tier", "multi-source", "gather" or
"lookup" (grepped this pass). The live arc is entirely reading-loop read-out quality; the
multi-source loop is not in it.

---

## 8. WHAT I COULD NOT VERIFY

1. **Whether the three-tier loop would help the reading loop if wired.** Nothing tests that pairing;
   no cell imports both. Any claim in either direction would be speculation.
2. **The FULL-scale numbers of the three-tier cells beyond their `metrics.json` verdict strings.**
   I read verdicts and headline fields; I did not recompute any arm off raw per-unit data, and I did
   not re-run any FULL cell (a detached experiment is live; re-running was out of scope).
3. **Whether `exp_active_learning_loop_gap_detect_lookup_revise_v2` (78 KB) contains a live-lookup
   code path somewhere past its docstring.** The docstring is explicit that content is frozen
   literals with "NO nltk/network dependency at runtime"; I verified the claim's presence, not every
   one of its ~1,800 lines.
4. **ConceptNet / Wikidata exact row counts.** `conceptnet-assertions-5.7.0.csv.gz` (498 MB gz) and
   the Wikidata dumps were not decompressed/counted — too expensive for this pass. Sizes and paths
   are reported instead. CSKG, ATOMIC and heldout_edges WERE counted line-by-line.
5. *(resolved during this pass — `hd_fact_store` was re-read directly and does carry
   `pipeline_status: "WIRED_BUT_NOT_PIPELINE_REACHABLE"`; all rows in §6 are first-hand.)*
6. **Historical git state.** I did not `git log` these modules to check whether a wired-then-unwired
   transition ever existed. The current tree is what is reported.
7. **`Glob` was avoided entirely** per the standing false-negative warning; all discovery used
   `Grep` with absolute paths, `ls` + `grep` on directory listings, and a live Python import trace.
   The `experiments/` directory holds 5,818 files and two `Grep`/`ls -t` calls timed out on it —
   those were re-run as narrower `ls | grep` and completed. No permission denials occurred.
