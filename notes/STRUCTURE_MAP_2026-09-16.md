# THE STRUCTURE MAP — every part of the reader, the brain structure it stands in for, what it computes, who else computes the same thing, what it costs to read, and what each job uses versus what it should use

**Built 2026-09-16 by the pri-142 solver.** Documents + registry fields + one measured cost table. **No file
under `hdlab/` or `tools/` was changed** (the witness is `git diff --stat -- hdlab tools`, empty for this
solver's commits). The consolidations this map ranks are pri 143 (one competition engine), pri 144 (one
register), pri 145 (collapse the copies).

---

## 0. THE SHORT VERSION, IN PLAIN LANGUAGE

The reader is built from **278 parts**, not the ~70 the brief estimated. Sorted by the brain structure each
one stands in for, they fall into **21 structures plus two non-brain buckets** (measurement scaffolding and
compute-budget plumbing). Three findings carry the rest of this document:

1. **One structure holds 28 parts, and they all make decisions the same way: score the options, pick the
   best.** The engine that does it properly already exists as a module (`graded_competition`) and two organs
   route through it. Three of the biggest decisions in the reader — who the agent is, which place a sentence
   is about, and which entity a pronoun means — each carry their own private copy of the scoring, with
   **hand-set weights instead of weights counted from reading**. That group is **17% of read time**.
2. **Reading one document takes 45 seconds, and 61% of it is one operation** — the meaning organ's
   spreading-activation walk over the dictionary graph, run 672 times on six documents, inside the
   harm/help judgement of every event. It is the single largest cost in the system by a wide margin, and
   nothing about the reader's structure makes that visible until you profile it.
3. **The four "registers" that are supposed to be one situation model are three different data shapes.**
   Two (state, location) keep time intervals per entity and are near-identical code; one (world state)
   keeps intervals per *object*; and two (goals, affect) keep a flat list with no time index at all, while
   belief keeps nothing and recomputes from the event list on every question. **A goal is therefore closed
   by a verb and an agent, never by the state register's result state** — exactly the coordination gap the
   owner named.

**The ranked list of what to merge is in §7.** The top item is not a merge at all: it is a measured
optimisation worth **27 seconds per document** that fell out of the cost table.

---

## 1. HOW TO READ THIS MAP, AND WHAT IT IS GRADED ON

- **The unit is the STRUCTURE, not the module.** §4 lists 21 brain structures; each organ is an arm or a
  copy inside one of them.
- **Every module gets a row** (§4 table): its structure, the computation as one sentence of math, its
  brain-foundational status reconciled against `notes/bf_status_registry.jsonl`, its read cost from §6, its
  importer count, whether a second copy exists under `experiments/`, whether the capability registry has a
  row for it, and **`src`: whether the computation in that row was read from the CODE this pass (`MATH`) or
  taken from the module's own stated computation (`DOC`)**. That last column is the map auditing itself —
  see §9(vi).
- **`BF` column vocabulary** is the disk's, not this map's: `BF` (copies the brain's math), `BF_SPIRIT` (a
  defensible model with open details), `NOT_BF` (a stand-in), `unrated` (no row in the BF registry).
- **Where documents disagree, the disk wins and the disagreement is a row** (§3).

---

## 2. THE COUNTS

| quantity | count | basis |
|---|---|---|
| `.py` modules under `hdlab/` | **278** | `os.walk`, excluding `__pycache__` (265 at the package root + 7 `learner/` + 6 `dashboard/`) |
| modules mapped to a structure | **278 / 278** | §4; zero unmapped |
| brain structures named | **21** | §4 A–U |
| modules that stand in for NO brain structure (honestly) | **46** | 37 instrumentation + 9 compute-budget primitives (§4 V, W) |
| modules with a brain-foundational rating on disk | **94 / 278** | `notes/bf_status_registry.jsonl`: 8 `BF`, 80 `BF_SPIRIT`, 6 `NOT_BF` |
| **modules with NO rating at all** | **184 / 278 (66%)** | the audit's "~5 of 38" describes 38 organs, not the 278 files |
| capability-registry rows | 264 | `data/capability_registry.jsonl` |
| registry rows carrying `brain_structure` **before** this pass | **59 / 264 (22%)** | the brief said "every row"; the disk said 59 — **a disagreement, and a row** (§3) |
| modules with **no registry row at all** | **75 / 278** | filled by this pass via the locked writer |
| organs that exist TWICE (an `experiments/_X.py` copy) | **16**, 14 drifted, 2 thin shims | `verification/test_organ_copies_are_one_object.py`, re-run 2026-09-16, 4/4 PASS |
| reader dimensions default-ON | **23** | 17 literal `track_*` + 6 more dimension flags (§8) — the brief's "23 `track_*`" reconciled |
| modules that actually executed in one full read | **56** | §6, the profile's own attribution |
| read time per document (honest wall clock, unprofiled) | **44.7 s** | 268.4 s over 6 GUM documents; 0.559 s per sentence |

**The single-sentence version.** *Two hundred and seventy-eight parts stand in for twenty-one brain
structures; one structure holds twenty-eight of them making the same decision five different ways; two
thirds of the parts have never been rated for brain-faithfulness at all; and sixty-one per cent of the time
it takes to read a document goes into one graph walk that nothing in the architecture names.*

---

## 3. WHERE THE DOCUMENTS DISAGREE WITH THE DISK (the disk wins; each is a row)

| claim | source | the disk, 2026-09-16 | verdict |
|---|---|---|---|
| "about seventy parts" | pri-142 brief §1 | **278** `.py` files under `hdlab/` | brief understated by 4x; the map uses 278 |
| "the registry's `brain_structure` field exists on every row" | pri-142 brief §4 | **59 of 264** rows carried it | brief wrong; this pass fills the rest |
| "155 `.py` files in `hdlab/`" | `notes/ORGAN_MAP.md` §1 (2026-08-15) | **278** | ORGAN_MAP is a month stale on the file count |
| "5 of 38 organs compute the brain's equation" | `ORGAN_MAP.md` §1 / audit §3 | 8 `BF` + 80 `BF_SPIRIT` + 6 `NOT_BF` of **278**; 184 unrated | not contradicted, but it describes a 38-organ enumeration, not the module set. **Reconciled in §5.** |
| "the lexical-read group is three organs (`lexicon_foundation`, `meaning_foundation`, animacy, supersense)" | pri-142 brief §3 | pri 127 **already consolidated** every read-time lexical lookup behind `lexicon_foundation`; `nltk` survives at read time in **zero** modules (`goal_achievement` and `morphology` import it for offline/asset paths only) | **the lexical-read group is DONE and is the model case** (§5.3) |
| "`strengths_from_counts` shared by the role labels and the non-argument arm … the agent pick carries its own scoring" | pri-142 brief §4 | confirmed: `experiments/exp_agent_pick_reweigh_v1.py::agent_strengths_from_counts` is a second implementation of the identical math; the live `AGENT_VALIDITIES` are **hand-set constants** (`preverbal 3.0, core_arg 2.0, animacy 2.0, salience 2.0, adjacency 1.0, byagent 6.0, structure 2.5, byhead 2.0`) | confirmed, with the numbers |
| "three parse sources for the space organ (pri 137)" | pri-142 brief §4 | `space_reader` imports `PosTagger` and `ArcParser` at module level **and** `frontend` lazily at :257 | confirmed and generalised: `pos_tagger_ud_ewt_upos.json` is loaded by **7** modules, `arc_parser_hashed_ud_ewt.npz` by **4** |
| "~90k redundant re-parses in one arm" (INFERRED) | pri-142 brief §4 | on the live read the redundancy is **2.17 arc-scorings and 1.98 category posteriors per sentence**, not 90k (§6.3). The 90k figure belongs to an arm, not to the reader. | **the inference is directionally right and an order of magnitude smaller than stated** |

---

## 4. THE MAP — EVERY ORGAN, BY STRUCTURE

Columns: **organ · computation (one sentence of math) · BF status (disk) · read cost (self seconds / calls
over 6 GUM documents) · importers · copy under `experiments/` · registry row · src (MATH = read from code
this pass, DOC = the module's own stated computation)**.

"0 (not on this read)" means the module did not execute during the profiled read — it is built but off the
live reading path, not that it is free.

<!-- BEGIN GENERATED TABLE -->

### A_VWFA — VISUAL WORD FORM AREA (left occipito-temporal) -- orthography to an invariant lexical code

*Citation:* Dehaene et al. 2005; Grainger & Whitney 2004 (open-bigram coding; update rule UNPINNED)

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `char_positional_encoder` | sign(SUM_i bind(char_hd[c_i], pos_hd[i])) -- position is a hashed atom, not a rotation. | unrated | 0 (not on this read) | 16 | — | yes | MATH |
| `char_trigram_encoder` | bag of character trigrams bundled into one bipolar hypervector; order destroyed. | unrated | 0 (not on this read) | 63 | — | yes | MATH |
| `morphology` | lemma(w) = stored irregular form, else the first affix-detached candidate passing the lexical check, POS order n/v/a/r; dual-route frequency race on collision. | BF | 4.97 / 1,075,331 | 29 | — | **NO ROW** | MATH |
| `vwfa` | acc += weight * SUM_scale (n-gram, scale) hashed bipolar HV optionally bound to position, then sign(). | unrated | 0 (not on this read) | 6 | — | yes | MATH |

### B_LEXSTORE — ANTERIOR TEMPORAL LEXICAL STORE -- content-addressed read of a developmentally laid-down lexicon

*Citation:* Patterson, Nestor & Rogers 2007; Binder & Desai 2011 (acquisition offline, retrieval a read)

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `animacy_lexicon` | word/lemma -> {animacy, category, agent_capable} by a frozen WordNet hypernym-closure lookup. | unrated | 0.45 / 30,775 | 84 | — | yes | DOC |
| `closed_class_lexicon` | membership test: is this word a function/discourse word (so it cannot be a content word's meaning). | unrated | 0 (not on this read) | 31 | — | yes | DOC |
| `definitional_extraction` | symbolic detector for the surface constructions by which text states what a word means. | unrated | 0 (not on this read) | 27 | — | yes | DOC |
| `definitional_predicate_v61` | recovers the PREDICATE of a process definition from the definitional construction. | unrated | 0 (not on this read) | 3 | — | yes | DOC |
| `event_type` | verb -> WordNet supersense -> a folk-psychological event ontology class. | BF_SPIRIT | 0 (not on this read) | 24 | — | **NO ROW** | MATH |
| `force_dynamics_lexicon` | frozen verb -> force class (CAUSE/ENABLE/PREVENT) lexicon from FrameNet causation frames. | BF_SPIRIT | 0 (not on this read) | 29 | **Y** | yes | DOC |
| `gender_organ` | glass-box natural-gender inference for a nominal (no gold, no LLM). | unrated | 0 (not on this read) | 1 | — | **NO ROW** | DOC |
| `idiom_grounding` | idiom / colloquialism -> attribute polarity grounding. | unrated | 0 (not on this read) | 3 | — | yes | DOC |
| `idiom_lexicon` | a frozen stored-unit multiword-expression lexicon (the brain stores idioms whole). | unrated | 0 (not on this read) | 1 | — | **NO ROW** | DOC |
| `lexical_utils` | the BF lexical helpers (head lemma, person synset, concept lemma) split out of the NOT_BF commonnoun_binder. | BF_SPIRIT | 0.13 / 21,478 | 10 | — | **NO ROW** | DOC |
| `lexicon_foundation` | content-addressed read of a frozen sqlite lexical store (senses, supersenses, taxonomy, frames, polarity) -- ONE store, many reads, no library in the call chain. | BF_SPIRIT | 13.44 / 6,455,629 | 38 | — | yes | MATH |
| `meaning_foundation` | loader for the frozen curated sense-signature foundation (117,614 WordNet senses). | BF_SPIRIT | 0 (not on this read) | 37 | — | **NO ROW** | DOC |
| `psych_verb_frames` | psych verbs -> which argument is the EXPERIENCER (subject or object). | BF_SPIRIT | 0.01 / 1,567 | 8 | — | **NO ROW** | DOC |
| `quality_relation` | two-channel adjective opposition/relation detection (WordNet antonymy + a learned channel). | BF_SPIRIT | 0 (not on this read) | 1 | — | yes | DOC |
| `who_is_who_lexicon` | a frozen relational lexicon: title -> role, possessed -> type. | BF_SPIRIT | 0 (not on this read) | 2 | — | **NO ROW** | DOC |
| `wordnet_polarity_propagation` | propagate result-valence to an OOV verb through the WordNet graph, voted against a seed set. | unrated | 0 (not on this read) | 13 | — | yes | DOC |

### C_HUBSPOKE — ATL AMODAL HUB + MODALITY SPOKES -- one graded meaning code converged from modality channels

*Citation:* Rogers et al. 2004; Lambon Ralph et al. 2017 (hub-spoke double dissociation; combination rule UNPINNED)

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `bridging_inference` | construction-integration antecedent selection: score candidate antecedents by ATL relatedness and commit the best unstated link. | BF_SPIRIT | 0 (not on this read) | 8 | — | **NO ROW** | DOC |
| `composed_encoder_v3` | score-level late combination of a VWFA orthographic stream and a PPMI/SVD distributional stream. | unrated | 0 (not on this read) | 4 | — | yes | DOC |
| `concept_encoder` | competitive-Hebbian sparse coding of a concept-label-conditioned embedding. | unrated | 0 (not on this read) | 13 | — | yes | DOC |
| `conceptual_meaning` | definitional/conceptual meaning channel over the ATL hub -- the reader's second meaning system. | BF_SPIRIT | 3.98 / 4,167,130 | 31 | — | yes | DOC |
| `distributional_meaning_channel` | PPMI over the reading loop's separable co-occurrence store -> a taught substitutability read-out. | unrated | 0 (not on this read) | 31 | — | yes | DOC |
| `fractional_power_encoding` | FPE magnitude code: z^x with fractional exponent -- a log-Weber scalar magnitude representation. | unrated | 0 (not on this read) | 8 | — | yes | MATH |
| `grounded_semantic_graph` | spreading activation as personalised PageRank r = (1-d)p + d*T^T r over a WordNet++ synset graph. | unrated | 14.83 / 2,591 | 13 | — | yes | MATH |
| `grounded_similarity` | perceptual-grounding fallback similarity for OOV words. | BF_SPIRIT | 0.01 / 2,867 | 146 | — | yes | DOC |
| `hub_spoke_word` | word_vector(w) = Q(SUM_s bind(spoke_key[s], facet_s)) -- one vector that stays internally addressable. | unrated | 0 (not on this read) | 5 | — | yes | MATH |
| `late_combine` | weighted integration of N parallel streams into one vector (an N400-window analog). | unrated | 0 (not on this read) | 2 | — | yes | DOC |
| `lexical_similarity` | shared-feature lexical similarity over typed concept features. | unrated | 0 (not on this read) | 33 | — | yes | DOC |
| `meaning_fusion` | equal-weight z-fusion of a reading spoke and a grounded spoke (complementary, not distillation). | unrated | 0 (not on this read) | 2 | — | yes | MATH |
| `ppmi_sparse_encoder` | PPMI/SVD then threshold -> a sparse distributional code. | unrated | 0 (not on this read) | 13 | — | yes | MATH |
| `random_indexing` | forward-only Hebbian co-occurrence: each word's context vector accumulates its neighbours' sparse index vectors. | unrated | 0 (not on this read) | 10 | — | yes | MATH |
| `scalar_adjective_operation` | gradable adjective -> a magnitude on its dimension (the 'ruler' meaning operation). | unrated | 0 (not on this read) | 3 | — | yes | DOC |
| `semantic_hub` | one shared nonlinear layer over five graded spokes, consolidated by denoising reconstruction + precision-weighted consensus. | BF_SPIRIT | 0 (not on this read) | 1 | — | **NO ROW** | DOC |
| `sensorimotor_spoke` | a modality-specific spoke feeding the hub; the candidate nearest in spoke space is the meaning (selection rule OUR-INVENTION). | BF_SPIRIT | 0 (not on this read) | 7 | — | yes | DOC |
| `structured_matcher` | the SIGN/TYPE store complementing the polarity-blind distributional hub: typed, directed role-filler match. | BF_SPIRIT | 0 (not on this read) | 2 | **Y** | **NO ROW** | DOC |
| `typed_spokes` | frozen TYPED, DIRECTED world-knowledge spokes (is-a, part-of, ...) on the ATL hub -- the additive fix for the superposition ceiling. | BF_SPIRIT | 4.18 / 1,845,195 | 32 | — | **NO ROW** | DOC |
| `verb_lexical_similarity` | open-vocabulary verb-class shared-feature similarity (the verb sibling of lexical_similarity). | unrated | 0 (not on this read) | 33 | — | yes | DOC |

### D_SEMCTL — SEMANTIC CONTROL (LIFG / pMTG) -- conflict-gated suppression of the frequency-dominant meaning

*Citation:* Jefferies & Lambon Ralph 2006; Noonan et al. 2013; biased competition Desimone & Duncan 1995

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `coref_distractor_suppress` | suppress generic/non-referential distractor candidates and abstain when no candidate clears. | unrated | 0 (not on this read) | 12 | — | yes | DOC |
| `diagnostic_context_wsd` | biased-competition sense readout: the diagnostic context word biases the sense competition. | unrated | 0 (not on this read) | 60 | — | **NO ROW** | DOC |
| `layer_075_structural_slot_filter` | narrow a PPR candidate set to the few facts a composition query actually needs. | unrated | 0 (not on this read) | 2 | — | yes | DOC |
| `low_information_filter` | refuse a grounding object that carries too little information to be a meaning. | unrated | 0 (not on this read) | 5 | — | yes | DOC |
| `meaning_operation_router` | dispatch the meaning read-out by word class -- the semantic-control routing step. | unrated | 0 (not on this read) | 4 | — | yes | DOC |
| `semantic_control` | LIFG/pMTG conflict-gated suppression: let context override the frequency-dominant sense. | unrated | 0 (not on this read) | 7 | — | yes | DOC |
| `underspecified_sense_reader` | commit the underspecified shared-core sense of a target word over the decorrelated sense hub. | BF_SPIRIT | 0 (not on this read) | 18 | — | **NO ROW** | DOC |

### E_SELECT — CORTEX - BASAL GANGLIA SELECTION LOOP / COMPETITION MODEL -- candidates scored by summed cue validities, argmax gated

*Citation:* Bates & MacWhinney 1982/1989; Lewis & Vasishth 2005; McClelland 2013 (additive+softmax = the posterior); Redgrave, Prescott & Gurney 1999 (one selection loop, many domains)

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `affected_entity_resolver` | argmax over Principle-B-legal candidates of ln(ACT-R salience) + g_g*1[role match] + g_t*1[patient]; gammas HAND-SWEPT, not learned log-odds. | BF_SPIRIT | 0.56 / 152,591 | 18 | — | **NO ROW** | MATH |
| `attachment_arm` | arc score(h->j) = config strength + SUM_cues log-odds contrast(cue value / config); tree = single-root MAP or incremental beam with decaying hold expectations. | BF_SPIRIT | 17.48 / 1,900,991 | 46 | — | **NO ROW** | MATH |
| `commonnoun_binder` | situation-gated common-noun referent forming. NOT_BF and empirically dead on the live path (its BF lexical helpers were split out to lexical_utils). | NOT_BF | 0 (not on this read) | 22 | — | **NO ROW** | DOC |
| `convergent_cue_reader` | combine two cues by reliability weighting w_i proportional to 1/sigma_i^2 (Ernst-Banks / Ma-Pouget), not a post-hoc AND. | BF_SPIRIT | 0 (not on this read) | 6 | — | yes | MATH |
| `coref` | the reference backbone: a per-sentence pass that opens entities and resolves pronouns against the running overlay by ACT-R activation x phi agreement. | BF_SPIRIT | 0.65 / 77,989 | 160 | — | yes | MATH |
| `coreference_resolver` | canonical match-or-allocate identity tracking across clauses. | unrated | 0 (not on this read) | 36 | — | yes | DOC |
| `crf_tagger` | calibrated joint-decoded POS posterior (a CRF over the same features). Supervised weights -> NOT_BF. | unrated | 0 (not on this read) | 10 | — | yes | DOC |
| `crosstype_bridge` | definite -> prior NAME binding by in-text predication (precise constructs) x ACT-R cue retrieval. | BF_SPIRIT | 0.08 / 14,051 | 15 | — | **NO ROW** | DOC |
| `crosstype_live_adapter` | runs the crosstype bridge gold-free off the reader's own live parse and online cluster labels. | BF_SPIRIT | 0.16 / 5,986 | 6 | — | **NO ROW** | DOC |
| `entity_resolver` | ONE ACT-R retrieval core A_i = B_i + SUM_cue W_cue*match_cue(i) with mention-type-routed cue arms (Ariel accessibility) -- the model consolidation. | BF_SPIRIT | 4.53 / 1,463,047 | 5 | — | **NO ROW** | MATH |
| `entity_world_model_resolver` | entity resolution seeded with a world-knowledge role/kinship prior. | BF_SPIRIT | 0 (not on this read) | 4 | — | **NO ROW** | DOC |
| `event_centrality_coref` | event/situation centrality as a tie-break cue in the coreference decision. | BF_SPIRIT | 0 (not on this read) | 25 | — | yes | DOC |
| `gated_fusion` | learned convex-gate fusion of two retrieval streams. | unrated | 0 (not on this read) | 1 | — | yes | DOC |
| `goal_owner_select` | directed coherence scoring to pick WHOSE goal a purpose clause states. | unrated | 0 (not on this read) | 25 | — | yes | DOC |
| `graded_competition` | THE engine: A_i = SUM_c w_c*support_c(i); softmax(gain*A) = the posterior; argmax = the task-triggered collapse; normalised entropy = difficulty. | unrated | 4.06 / 28,708 | 68 | — | yes | MATH |
| `graded_coref_pick` | the antecedent pick as graded competition: softmax over ACT-R + phi supports, argmax the pick, entropy the confidence. | unrated | 0 (not on this read) | 35 | — | yes | MATH |
| `graded_role_assigner` | role = argmax_k SUM_cues strength[cue][cfg/value][k]; strengths = log P(k/cfg,value) - log P(k/cfg) from counts (strengths_from_counts) -- THE ONE learned-validity implementation. | BF_SPIRIT | 6.19 / 790,891 | 103 | — | yes | MATH |
| `intent_classifier` | Hebbian-bound prototype bundles; intent = argmax similarity to a prototype. | unrated | 0 (not on this read) | 3 | — | yes | DOC |
| `lexical_categories` | P(c_i/words) by forward-backward over count-estimated log P(w/c), P(suffix/c), log P(c/c_prev); fixed-lag (2) incremental revision; argmax = the tag. | BF_SPIRIT | 20.08 / 1,101,469 | 33 | — | **NO ROW** | MATH |
| `online_entity_cluster` | Heim file-change + Lewis-Vasishth ACT-R retrieval: cluster each new mention onto the most active compatible file, else open one. | BF_SPIRIT | 0 (not on this read) | 5 | — | **NO ROW** | MATH |
| `pos_tagger` | averaged structured perceptron + Viterbi -> UPOS. NOT_BF (max-margin fitted weights, not counted cue validities); superseded on the live path by lexical_categories. | NOT_BF | 0 (not on this read) | 277 | — | yes | MATH |
| `salience_binder` | B = ln(SUM_k w(role_k) * dt_k^-decay) -- ACT-R base-level activation x Centering prominence; THE shared base term of every retrieval organ. | BF | 1.38 / 407,688 | 47 | — | yes | MATH |
| `selection_weighted_sharded_typer` | discriminativeness-weighted, role-sharded VSA superposition typing of pragmatic constructions. | unrated | 0 (not on this read) | 3 | — | yes | DOC |
| `thematic_role_labeler` | role = argmax over AGENT/PATIENT/EXPERIENCER/... of integrated probabilistic surface cues (word order, animacy, frame) -- Competition Model, its own cue table. | BF_SPIRIT | 1.36 / 173,554 | 229 | — | yes | DOC |
| `typed_coref` | typed common-noun coreference: bind a definite to a prior mention of a compatible TYPE. | BF_SPIRIT | 0 (not on this read) | 31 | — | **NO ROW** | DOC |
| `verb_role_exemplar_selector` | pick WHICH argument fills a verb's role from a structured exemplar store, not a coarse centroid. | unrated | 0 (not on this read) | 9 | — | **NO ROW** | DOC |
| `verb_role_integrated` | construction-conditional integration of the verb-role exemplar store with position. | unrated | 0 (not on this read) | 0 | — | **NO ROW** | DOC |
| `world_state_entity_binding` | stage-1 dispatcher: a raw participant mention -> a canonical discourse-entity key (deixis / expletive / retrieval routing). | BF_SPIRIT | 0 (not on this read) | 5 | — | yes | DOC |

### F_SYNTAX — SYNTACTIC STRUCTURE BUILDING (left pIFG / pSTG) -- incremental attachment under memory limits

*Citation:* MacDonald, Pearlmutter & Seidenberg 1994; Lewis & Vasishth 2005; Levy 2008; Gibson DLT

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `arc_labeler` | supervised averaged perceptron over arc features -> UD deprel; argmax over label lanes. NOT_BF (a fitted discriminative classifier, not cue competition). | NOT_BF | 0 (not on this read) | 96 | — | yes | MATH |
| `arc_parser` | hashed arc-factored averaged perceptron scoring head->dep, decoded to a tree. NOT_BF (fitted weights, no cue contrasts). | NOT_BF | 0 (not on this read) | 183 | — | yes | DOC |
| `arceager_parser` | arc-eager transition system with Zhang-Nivre non-local features; argmax over legal actions. NOT_BF (fitted). | NOT_BF | 0 (not on this read) | 79 | — | yes | MATH |
| `candidate_generator` | sentence -> tokens -> categories -> arcs -> the SET of (verb, argument-candidate) pairs the parse licenses. | unrated | 0 (not on this read) | 76 | — | yes | DOC |
| `frontend` | THE one shared reading frontend: categories and heads for every consumer, honouring the organ switches. | BF_SPIRIT | 0.09 / 9,450 | 40 | — | **NO ROW** | MATH |
| `graded_parser` | globally normalised arc marginals over the arc-factored scorer (keep alternatives alive). | unrated | 0 (not on this read) | 81 | — | **NO ROW** | DOC |
| `incremental_parser` | left-corner Now-or-Never eager attachment -- the noise->0 limit of graded competition. | BF_SPIRIT | 0.10 / 6,376 | 31 | — | yes | DOC |
| `joint_relation_frontend` | parse the clause ONCE and read every relation channel off the SAME dependency structure (the brain extracts a clause's relations jointly). | BF_SPIRIT | 0 (not on this read) | 11 | **Y** | **NO ROW** | DOC |
| `np_head_reduce` | reduce an NP span to its head (stage A of who-did-what role assignment). | BF_SPIRIT | 0 (not on this read) | 14 | — | yes | DOC |
| `predicate_argument_frontend` | the shared shallow-SRL front end: a parsed clause -> argument roles. | BF_SPIRIT | 0.37 / 51,795 | 84 | — | yes | DOC |
| `predicate_detector` | register-robust predicate (verbhood) recall from counted cues, recovering events the tagger misses. | BF_SPIRIT | 1.43 / 292,968 | 7 | — | yes | DOC |
| `relcl_resolver` | filler-gap role assignment for relative clauses as cue-based retrieval of the filler, no arc graph. | BF_SPIRIT | 0.16 / 33,433 | 61 | — | yes | DOC |
| `semantic_parser` | intent + role-slot extraction from a composed HD bundle by unbinding. | unrated | 0 (not on this read) | 1 | — | yes | DOC |
| `structural_do` | is this a bare post-verbal direct object (structural evidence overriding an intransitivity veto). | BF_SPIRIT | 0 (not on this read) | 2 | — | **NO ROW** | DOC |
| `verb_subcat` | verb -> P(has an overt patient); suppress a bound patient below threshold. | unrated | 0.01 / 4,440 | 15 | — | yes | DOC |
| `verb_subcat_frames` | verb -> its infinitival frame, separating a purpose adjunct from a complement. | BF_SPIRIT | 0 (not on this read) | 6 | — | **NO ROW** | DOC |

### G_SITMODEL — HIPPOCAMPAL-CORTICAL SITUATION MODEL -- one indexed event model with dimensions

*Citation:* Zwaan & Radvansky 1998 event-indexing; Glenberg, Meyer & Lindem 1987; Zacks, Speer & Reynolds 2009

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `affect_register` | a per-character LIST of extracted affect records with query callables; no time-indexed fold (the register-group deviation). | BF_SPIRIT | 0.06 / 875 | 4 | — | **NO ROW** | MATH |
| `belief_timeline` | belief(agent, obj, t) RECOMPUTED at query time from the event list x the observation set; no folded register (the register-group deviation). | BF_SPIRIT | 0 (not on this read) | 14 | — | yes | MATH |
| `copular_binding` | bind a copular predication to its subject as a typed (holder, property) state. | BF_SPIRIT | 0.06 / 1,871 | 11 | — | yes | DOC |
| `goal_register` | a LIST of extracted goals with a status marked by predicate+agent match in a strictly later sentence; no interval fold, no result-state read (the register-group deviation). | BF_SPIRIT | 0.21 / 37,505 | 60 | — | **NO ROW** | MATH |
| `location_register` | per-entity spatial INTERVALS: open_interval(node,t), node_at(t); fold(entities, motion events) -- the interval bookkeeping the state register shares. | BF_SPIRIT | 0 (not on this read) | 20 | — | **NO ROW** | MATH |
| `polarity_operator` | event negation operator + Johnson-Laird quantifier cardinality over an already-extracted proposition. | BF_SPIRIT | 0.36 / 96,872 | 4 | **Y** | **NO ROW** | DOC |
| `possession_operators` | derive the world-state TRANSFER operators from FrameNet rather than a hand-authored verb list. | BF_SPIRIT | 0 (not on this read) | 13 | — | yes | DOC |
| `referent_per_np` | open ONE discourse referent per content-noun-head NP (DRT file cards), not only per coref mention. | BF_SPIRIT | 0.10 / 9,407 | 14 | — | **NO ROW** | DOC |
| `situation_model_accumulate` | per-entity register: bundle(bind(role, event-slot)) accumulated, decoded by unbind + cleanup argmax (accumulate, never overwrite). | unrated | 0.06 / 760 | 143 | — | yes | MATH |
| `situation_model_multibank` | the same register sub-bundled across banks to lift the flat-bundle capacity wall. | unrated | 0 (not on this read) | 12 | — | yes | DOC |
| `situation_reader` | THE integration layer: one in-order pass over a passage producing a SituationModel with 23 default-on dimensions. | unrated | 1.65 / 101,664 | 301 | — | yes | MATH |
| `state_of_mind` | a symbolic salience-weighted working-memory discourse overlay (an entity tracker, NOT theory of mind). | unrated | 0.08 / 37,862 | 81 | — | yes | DOC |
| `state_register` | per-entity state INTERVALS: add_state(value, polarity, aspect, t); active_at(t); fold(entities, events) -- the same interval bookkeeping as the location register, a different attribute. | BF_SPIRIT | 0.01 / 1,509 | 11 | — | yes | MATH |
| `unified_referent` | ONE discourse referent per entity (Heim/Kamp DRT file change). | unrated | 0 (not on this read) | 6 | — | **NO ROW** | DOC |
| `world_state_register` | STRIPS-style operators over relational predicates: per-SLOT set(value,t) / value_at(t); fold(events) -- interval bookkeeping keyed on the OBJECT, not the entity. | BF_SPIRIT | 0.01 / 2,886 | 14 | — | yes | MATH |

### H_EPISODIC — HIPPOCAMPUS / CLS -- DG pattern separation, CA3 completion, replay to neocortex

*Citation:* Marr 1971; McClelland, McNaughton & O'Reilly 1995; Yonelinas dual-process

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `bound_event_backbone` | tiers the bound event tokens into one assembly so the reader's dimensions share one episodic backbone. | BF_SPIRIT | 0.31 / 18,358 | 2 | — | yes | DOC |
| `ca3_completer` | CA3 auto-associative completion from a partial cue, routed through an address. DEFAULT-OFF. | unrated | 0 (not on this read) | 2 | — | yes | DOC |
| `content_addressable_retrieval` | additive Lewis-Vasishth cue-based retrieval: A_i = SUM_cue w_cue * match_cue(i); retrieve argmax (partial-cue, not exact-key). | unrated | 0 (not on this read) | 5 | — | yes | DOC |
| `cortical_recall` | retrieval from the CONSOLIDATED (cortical) store rather than the episodic sketchpad -- the CLS position fix. | unrated | 0 (not on this read) | 8 | — | yes | DOC |
| `dg_ca3_recollection_gate` | DG expansive random projection + k-WTA, then CA3 completion; the gate's own confidence self-certifies. | unrated | 0 (not on this read) | 2 | — | yes | MATH |
| `dg_pattern_separation` | expansive random projection + top-k sparsify -> orthogonalised codes (the anti-over-merge stage). | unrated | 0 (not on this read) | 6 | — | yes | DOC |
| `factorized_entity_store` | episodic store factorised as CONTENT x graded TEMPORAL CONTEXT x within-moment ORDER. | unrated | 0 (not on this read) | 1 | — | yes | DOC |
| `gather_reason` | state-of-mind-conditioned CA3 relevance gather, then bounded K<=2 fan-out reasoning. | unrated | 0 (not on this read) | 10 | — | yes | DOC |
| `hd_fact_store` | a fact as one role-slot-bound hypervector with source and trust bound into the same bundle. | unrated | 0 (not on this read) | 87 | — | yes | MATH |
| `hippocampal_encoder` | DG expansion + top-K sparsify + sign, then CA3 Marr-style auto-association -- the CLS write path. | unrated | 1.61 / 953 | 27 | — | yes | MATH |
| `kg_traversal` | substrate-native single-hop and n-hop KG traversal: E @ (W @ key). | unrated | 0 (not on this read) | 65 | — | yes | MATH |
| `multi_hop` | multi-hop chain traversal with iterative (modern-Hopfield) cleanup between hops. | unrated | 0 (not on this read) | 7 | — | yes | DOC |
| `perirhinal_conjunctive` | sparse CONJUNCTIVE feature coding (perirhinal), the code DG/CA3 operate over. DEFAULT-OFF. | unrated | 0 (not on this read) | 3 | — | yes | DOC |
| `schema_exemplar_bayes` | log-sum-exp Bayesian routing to a compressed schema centroid. | unrated | 0 (not on this read) | 5 | — | yes | DOC |

### I_WM — WORKING MEMORY -- a bounded focus of attention with active maintenance (PFC + parietal)

*Citation:* Cowan 2001 (~4 chunks); Baddeley; slot-based maintenance

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `bundle_focus_coref` | a bounded Cowan-4 event-bundle focus fed back into cross-sentence pronoun resolution. | unrated | 0 (not on this read) | 1 | — | yes | DOC |
| `context_retention` | two-tier multi-turn dialogue context retention. | unrated | 0 (not on this read) | 6 | — | yes | DOC |
| `entity_slot_gate` | a small addressable entity-slot memory with a learned write gate over frozen encoder states. | unrated | 0 (not on this read) | 1 | — | yes | DOC |
| `situation_focus` | a bounded ~4-chunk superposition of the most recent event bundles, hierarchically chunked, gracefully forgetting. | BF_SPIRIT | 0.33 / 5,622 | 8 | — | yes | MATH |
| `slot_attention_wm` | slot-attention working memory: competing slots bind the input by attention, maintained across steps. | unrated | 0 (not on this read) | 6 | — | yes | DOC |
| `working_memory` | K-item capacity via per-bank cleanup (multi-bank working memory). | unrated | 0 (not on this read) | 3 | — | yes | MATH |

### J_VSA — BINDING ALGEBRA -- the substrate's vector binding primitive (implementation UNPINNED in the brain; kept as a defensible computational-level model)

*Citation:* Plate 1995 HRR; Gayler 2003; SEM/Franklin 2020 as the computational-level model (owner 2026-08-26)

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `atoms` | FHRR/HRR atom generation and similarity: random unit-phase vectors, cosine/phase similarity. | unrated | 0 (not on this read) | 79 | — | yes | DOC |
| `binding` | bind = elementwise complex multiply (FHRR) / circular convolution (HRR) / bipolar multiply (BSC); unbind = the conjugate. | unrated | 0.13 / 3,515 | 216 | — | yes | MATH |
| `bundling` | superposition: recency-weighted sum of hypervectors, then quantise. | unrated | 0 (not on this read) | 78 | — | yes | MATH |
| `cleanup_family` | four cleanup primitives mapping a noisy retrieved vector to the nearest stored item. | BF | 0 (not on this read) | 34 | — | yes | DOC |
| `event_bundle` | event_vec = quantize(SUM_r bind(role_key[r], filler_vec[r])) -- one event as one role-slot-bound hypervector. | BF | 0.41 / 9,483 | 31 | — | yes | MATH |
| `gsbc_graded_encoder` | generalised sparse block code: block-wise top-m positive survivors, unit-L1 per block. | unrated | 0 (not on this read) | 4 | — | yes | MATH |
| `iterative_attractor` | iterative attractor settling (CAN-bump / Wilson-Cowan style) replacing one-shot argmax cleanup. | BF | 0 (not on this read) | 35 | — | yes | MATH |
| `memory` | cleanup memory: nearest stored named atom under an attention-gated cosine floor. | unrated | 0 (not on this read) | 28 | — | yes | MATH |
| `modern_hopfield_readout` | modern-Hopfield softmax retrieval over a stored HD table (interpolating readout). | unrated | 0 (not on this read) | 2 | — | yes | MATH |
| `role_slot_summarizer` | hierarchical role-slot binding summarisation: sharded per-role slots over the same bind/bundle primitives. | BF | 1.03 / 8,722 | 22 | — | yes | MATH |
| `sequence_memory` | offline-Hebbian-bound ordered pair store (the S matrix); successor prediction by unbind + cleanup. | unrated | 0 (not on this read) | 12 | — | yes | MATH |
| `vsa_cleanup_memory` | a real Plate-style cleanup memory: a separate item memory the noisy unbind result is cleaned against. | unrated | 0 (not on this read) | 2 | — | yes | DOC |

### K_PREDICT — PREDICTIVE CODING / N400 -- forward expectation and the precision-weighted update it is scored by

*Citation:* Rao & Ballard 1999; Rabovsky & McClelland 2018; Kuperberg & Jaeger 2016; Elman 2009 GEK

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `composed_hub_predictor` | forward prediction from a ~200-d ATL hub code by precision-weighted composed-exemplar retrieval. | unrated | 0 (not on this read) | 4 | **Y** | **NO ROW** | DOC |
| `generalized_event_knowledge` | score(cont/ctx) = SUM_a PPMI(a->c) over story transitions; precision = 1 - normalised entropy. | BF_SPIRIT | 0 (not on this read) | 43 | — | **NO ROW** | MATH |
| `n400_coherence_monitor` | //Delta situation-model// as the integration cost of the incoming item; a relative-threshold boundary on it. | unrated | 0.04 / 1,840 | 10 | — | yes | MATH |
| `predictive_coding` | predict(key) = sign(W @ key); write only when the residual exceeds threshold (gated write). | unrated | 0 (not on this read) | 30 | — | yes | MATH |
| `predictive_reader` | the verb pre-activates its role filler; surprisal at the filler is the prediction error. | BF_SPIRIT | 0.12 / 7,260 | 19 | — | yes | DOC |
| `predictive_world_model` | online event-transition model; leave-one-out predictive relevance log[P(B/ctx)/P(B/ctx-A)]. | BF_SPIRIT | 0 (not on this read) | 15 | — | **NO ROW** | MATH |
| `typed_selectional_preference` | Resnik class-based selectional association over the noun-supersense cut, from the reading-grown store. | BF_SPIRIT | 0.06 / 14,097 | 7 | — | **NO ROW** | DOC |

### L_SEGMENT — EVENT SEGMENTATION (SEM) -- a schema switch when prediction error crosses a relative threshold

*Citation:* Zacks et al. 2007; Reynolds, Zacks & Braver 2007; Franklin, Norman, Ranganath, Zacks & Gershman 2020

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `scene_segment` | scene segmentation + per-scene topical-protagonist coreference; also the reader's sentence/token parse entry. | BF_SPIRIT | 0.15 / 24 | 89 | — | yes | DOC |
| `sem_event_segmenter` | SEM schema switch: start a new event when prediction error crosses a relative threshold (Franklin/Zacks). | unrated | 0 (not on this read) | 4 | **Y** | **NO ROW** | DOC |

### M_AFFECT — VALUATION / AFFECT (OFC-vmPFC, amygdala, nociception) -- core affect as valence x arousal

*Citation:* Russell 1980 circumplex; Barrett constructed emotion; Talmy 1988 / Wolff 2007 force dynamics for harm

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `affect_lexicon` | word -> (valence, arousal) core-affect coordinates read from a frozen norm table. | BF_SPIRIT | 0.07 / 17,207 | 101 | — | **NO ROW** | DOC |
| `context_grounded_valence` | harm/neutral for an extracted (verb, patient) pair, flipped by the patient's grounded properties. | BF_SPIRIT | 0.06 / 2,866 | 14 | — | yes | DOC |
| `force_dynamics_valence` | HARM/HELP = sign(result-state valence) gated by force type and affectedness >= tau. | BF_SPIRIT | 0.23 / 15,327 | 21 | — | **NO ROW** | MATH |
| `occ_appraisal` | OCC appraisal: goal-conduciveness x prospect -> OCC emotion type + valence. | BF_SPIRIT | 0 (not on this read) | 3 | **Y** | **NO ROW** | MATH |
| `valence_polarity_channel` | the SIGNED evaluative axis that un-blinds meaning to antonymy (love vs hate). | BF_SPIRIT | 0 (not on this read) | 2 | — | **NO ROW** | DOC |

### N_GOALS — GOAL / INTENTION SYSTEM (mPFC-ACC) -- an agent's goal is a state about an object at a time, closed by a matching outcome

*Citation:* Trabasso & van den Broek 1985 causal network; Zwaan & Radvansky intentionality dimension; OCC appraisal

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `goal_achievement` | three inspectable channels composed by an explicit precedence policy into a goal-fulfilment verdict. | unrated | 0 (not on this read) | 14 | — | yes | DOC |
| `goal_hierarchy_graph` | a goal -> subgoal hierarchy graph for plot structure. | BF_SPIRIT | 0.01 / 1,358 | 5 | — | **NO ROW** | DOC |
| `goal_outcome_relation` | does an outcome semantically relate to the goal (the abstain-cohort residual). | unrated | 0 (not on this read) | 6 | — | yes | DOC |
| `goal_outcome_relation_grounded` | the graded situation-model ablation of the goal-outcome relation. | unrated | 0 (not on this read) | 1 | — | yes | DOC |
| `goal_typing` | type a goal by three validated construction signals. | unrated | 0 (not on this read) | 57 | — | yes | DOC |
| `outcome_event_extraction` | extract the outcome event and feed it to the already-proven goal-outcome organs. | unrated | 0 (not on this read) | 1 | — | yes | DOC |
| `parse_goal_extraction` | extract the goal referent from the parse structure. | unrated | 0 (not on this read) | 2 | — | yes | DOC |

### O_TOM — MENTALIZING NETWORK (rTPJ / mPFC) -- a per-agent belief partition and the action it predicts

*Citation:* Saxe & Kanwisher 2003; Apperly & Butterfill 2009; Baker/Tenenbaum inverse planning

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `belief_partition` | believed_location(observed, initial, final) = final if observed else initial, held as an FHRR binding read back by cleanup argmax. | unrated | 0 (not on this read) | 7 | — | yes | MATH |
| `belief_reader` | drives the belief timeline from the live reader's own extraction on real prose. | BF_SPIRIT | 0 (not on this read) | 3 | **Y** | **NO ROW** | DOC |
| `perceptual_access_ledger` | did agent A perceive event E: a glass-box observation-cue front end for Theory of Mind. | BF_SPIRIT | 0 (not on this read) | 16 | — | yes | DOC |
| `theory_of_mind` | believes(A,F,t) x wants(A) -> predicted action (the forward mentalizing chain). | BF_SPIRIT | 0 (not on this read) | 3 | — | **NO ROW** | MATH |

### P_CAUSE — FORCE-DYNAMIC CAUSAL SYSTEM -- CAUSE / ENABLE / PREVENT read off the force vectors of a clause

*Citation:* Talmy 1988; Wolff 2007 force theory; Wolff & Song 2003; Gopnik/Schulz intervention learning

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `causal_network` | build a running cause->effect graph over event bundles and mark on-chain vs dead-end by reachability to the outcome. | BF_SPIRIT | 0 (not on this read) | 3 | **Y** | **NO ROW** | DOC |
| `causal_reasoner` | multi-hop chain traversal + counterfactual necessity by simulated intervention over the reader's own causal links. | BF_SPIRIT | 0 (not on this read) | 20 | **Y** | **NO ROW** | DOC |
| `causal_sign_channel` | the increase/decrease SIGN of a causal edge, read from mined directed testimony. | BF_SPIRIT | 0 (not on this read) | 4 | — | **NO ROW** | DOC |
| `causation_typing` | force-dynamic CAUSE/ENABLE/PREVENT typing of within-clause causatives from the verb's force class x patient tendency. | BF_SPIRIT | 0 (not on this read) | 23 | — | yes | DOC |
| `coherence_reader` | SDRT-lite: infer RESULT/EXPLANATION edges across sentences from causal world knowledge, not connectives. | BF_SPIRIT | 0 (not on this read) | 4 | — | **NO ROW** | DOC |
| `force_dynamics_typer` | read CAUSE/ENABLE/PREVENT off the verb's force class (Wolff/Talmy). | unrated | 0 (not on this read) | 5 | — | **NO ROW** | DOC |
| `patient_tendency` | estimate the patient's own tendency (toward or against the result) for the force-dynamic typer. | unrated | 0.03 / 4,291 | 28 | **Y** | yes | DOC |

### Q_SPACE — SPATIAL SYSTEM (hippocampal place / boundary cells; parietal frames) -- where each entity is, and the relations between grounds

*Citation:* O'Keefe & Nadel 1978; Franklin & Tversky 1990; Glenberg, Meyer & Lindem 1987 foregrounding

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `space_reader` | ground selection by a FIRST-MATCH linear scan with hand-ordered fallbacks (PP ground, then direct object, then anticipated) -- NOT a competition (the selection-group deviation). | unrated | 0.25 / 28,933 | 4 | **Y** | **NO ROW** | MATH |
| `spatial_relational_model` | transitive region nesting (containment) + Franklin-Tversky relative position + Goal-over-Source path reasoning. | BF | 0 (not on this read) | 3 | — | **NO ROW** | DOC |

### R_TIME — TEMPORAL SYSTEM -- event order, tense as a Reichenbach relation, intervals as Allen relations, and a graded temporal context signal

*Citation:* Reichenbach 1947; Allen 1983; Howard & Kahana 2002 temporal context; Zwaan time dimension

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `aspect_interval` | aspect -> interval endpoints; Allen relations computed over the endpoints. | BF_SPIRIT | 0 (not on this read) | 2 | **Y** | **NO ROW** | DOC |
| `graded_temporal_context` | a bindable multi-timescale temporal context vector (the 'when' of an episodic trace). | unrated | 0 (not on this read) | 13 | — | yes | MATH |
| `successor_representation` | M = (I - gamma*P)^-1 -- the one fully pinned closed form in the substrate. | unrated | 0 (not on this read) | 6 | — | yes | MATH |
| `temporal_model` | THE one temporal ORDER organ in three layers: single-frame cue ordering, cross-sentence constraint graph + toposort, passage-level before/after register. | BF_SPIRIT | 0.08 / 2,108 | 12 | — | **NO ROW** | MATH |
| `temporal_order_register` | backward-compatible SHIM onto temporal_model layer 3 (the consolidation model case). | BF_SPIRIT | 0 (not on this read) | 1 | **Y** | **NO ROW** | MATH |
| `temporal_ordering` | backward-compatible SHIM onto temporal_model layer 1. | BF_SPIRIT | 0 (not on this read) | 2 | **Y** | **NO ROW** | MATH |
| `temporal_ordering_multiframe` | backward-compatible SHIM onto temporal_model layer 2. | BF_SPIRIT | 0 (not on this read) | 1 | **Y** | **NO ROW** | MATH |
| `temporal_reasoner` | integrated before/after with signal-class provenance + Allen OVERLAP over aspect-derived endpoints. | BF_SPIRIT | 0 (not on this read) | 6 | — | **NO ROW** | DOC |
| `temporal_script_schema` | script/schema ordering of IMPLICIT events the text never states. | unrated | 0 (not on this read) | 8 | — | **NO ROW** | DOC |
| `temporal_trace` | Foldiak post-synaptic exponential-decay trace over temporally contiguous input. | unrated | 0 (not on this read) | 2 | — | yes | MATH |
| `tense_preserving_detector` | compositional Reichenbach tense reading (E, R, S relations) preserved through event detection. | BF_SPIRIT | 0.08 / 14,702 | 1 | — | **NO ROW** | DOC |
| `transitive_ordering` | transitive closure over pairwise comparisons into a total magnitude order. | unrated | 0 (not on this read) | 13 | — | **NO ROW** | MATH |
| `uds_time_duration` | typical duration per event type (no LLM). | unrated | 0 (not on this read) | 1 | — | **NO ROW** | DOC |

### S_ACTSEL — BASAL GANGLIA GO / NOGO ACTION SELECTION + DOPAMINE PREDICTION ERROR -- gate one action, learn its value

*Citation:* Frank 2005; Schultz 1998; Redgrave et al. 1999

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `action_selection` | Go_i = w_m*manifold_i + a*goal_sim_i + w_r*reach_i; gate = argmax_i Go_i (winner-take-all disinhibition). | unrated | 0 (not on this read) | 2 | — | yes | MATH |
| `modulators` | named scalar control variables (arousal, attention) wired to specific substrate operations -- the neuromodulator analog. | unrated | 0 (not on this read) | 15 | — | yes | DOC |

### T_LEARN — PLASTICITY AND CONSOLIDATION -- Hebbian association from experience, gated admission to the slow store, model selection by evidence

*Citation:* Hebb 1949; McClelland et al. 1995 CLS; Anderson & Schooler 1991; MDL / Bayesian model selection

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `additive_map` | an additive (CLS cortical-schema) KG map: entity coordinates accumulated by summation rather than by multiplicative binding. | unrated | 0 (not on this read) | 15 | — | yes | DOC |
| `bayesian_inference` | posterior from prior x likelihood; MAP = argmax_k P(H_k/E); EM responsibilities. | unrated | 0 (not on this read) | 5 | — | yes | MATH |
| `cls_growth` | keep-both-stores safe growth: admit to the slow store only under a reversible gate. | unrated | 0 (not on this read) | 4 | — | yes | DOC |
| `compose_freq_routing` | gate stored associative traces by the target's composition frequency. | unrated | 0 (not on this read) | 1 | — | yes | DOC |
| `consequence_learning_loop` | learn an OOV outcome verb's result valence from the episode's own computed consequence. | unrated | 0 (not on this read) | 15 | — | yes | DOC |
| `consolidation_gate` | the knowledge-admission quality gate: refuse raw co-occurrence into the slow store unless it passes. | unrated | 0 (not on this read) | 4 | — | yes | DOC |
| `continual` | NREM-replay consolidation with a companion drift bound. | unrated | 0 (not on this read) | 15 | — | yes | DOC |
| `edge_importance` | a per-pair importance matrix H[i,j] orthogonal to per-atom weight magnitude. | unrated | 0 (not on this read) | 12 | — | yes | DOC |
| `excitability` | a per-atom excitability tensor E[i] (CREB / synaptic tag-and-capture analog) orthogonal to /W[i]/. | unrated | 0 (not on this read) | 3 | — | yes | DOC |
| `frame_induction` | induce an OOV verb's thematic frame from the constructions it is observed in. | BF_SPIRIT | 0.05 / 9,232 | 13 | — | yes | DOC |
| `grounding_acquisition_loop` | flag -> library -> consolidate -> guard -> bank: the closed self-growing grounding loop. | unrated | 0 (not on this read) | 50 | — | yes | DOC |
| `induced_categories` | the reading-acquired category inventory: distributional substitution classes with no labels. | unrated | 0 (not on this read) | 1 | — | **NO ROW** | DOC |
| `learner.__init__` | learner package marker. | unrated | 0 (not on this read) | 0 | — | **NO ROW** | MATH |
| `learner.core` | ONE model-selection engine: pick the hypothesis whose two-part (MDL) / Laplace evidence is best. | unrated | 0 (not on this read) | 21 | — | yes | MATH |
| `learner.plugins.__init__` | plugin package marker. | unrated | 0 (not on this read) | 0 | — | **NO ROW** | MATH |
| `learner.plugins.estimation_plugin` | frequency-estimation hypothesis class (Laplace-smoothed condensed counts). | unrated | 0 (not on this read) | 0 | — | yes | DOC |
| `learner.plugins.gam_plugin` | additive graded shape functions with explicit pairwise interactions. | unrated | 0 (not on this read) | 0 | — | yes | DOC |
| `learner.plugins.proginduction_plugin` | bounded enumerative symbolic regression over a small boolean DSL. | unrated | 0 (not on this read) | 0 | — | yes | DOC |
| `learner.plugins.ruleind_plugin` | MDL-gated sequential-covering rule induction. | unrated | 0.01 / 337 | 0 | — | yes | DOC |
| `learner.registry` | hypothesis-class plugin registry for the learner core. | unrated | 0 (not on this read) | 1 | — | yes | DOC |
| `learning` | W[t+1] = (1-decay)*W[t] + arousal*reward for co-active pairs -- reward-modulated Hebbian update. | unrated | 0 (not on this read) | 11 | — | yes | MATH |
| `perceptron` | Collins averaged structured perceptron with Viterbi decoding -- a supervised learning primitive. | unrated | 0 (not on this read) | 3 | — | yes | MATH |
| `prelim_tier` | the middle tier: retain-forever + accumulate + DG/CA3 combined-evidence generalisation. | unrated | 0 (not on this read) | 8 | — | yes | DOC |
| `reading_grounding_loop` | read-to-grow: accumulate co-occurrence from real text, ground concepts, criterion-gate what is admitted. | BF_SPIRIT | 0 (not on this read) | 272 | — | yes | DOC |
| `result_type_induction` | learn the speech-act / result type from construction-cue features. | unrated | 0 (not on this read) | 5 | — | yes | DOC |
| `script_grain_acquisition_loop` | the grounding acquisition loop at the recurring-event-type (script) grain. | unrated | 0 (not on this read) | 14 | — | yes | DOC |
| `three_tier_loop` | the assembled three-tier knowledge loop (fast / prelim / consolidated). | unrated | 0 (not on this read) | 7 | — | yes | DOC |
| `ultrametric_clustering` | single-linkage agglomerative coarse-graining of high-cosine atom clusters into representative + residual codes. | unrated | 0 (not on this read) | 12 | — | yes | MATH |
| `word_acquisition_loop` | online grounded word acquisition for one dimension at a time. | unrated | 0 (not on this read) | 4 | — | yes | DOC |
| `word_learning_tool` | look the OOV word up first, then confirm or override that sense through story consequence. | unrated | 0 (not on this read) | 1 | — | yes | DOC |

### U_META — METACOGNITION AND FORAGING (ACC / frontopolar) -- when to stop, when to refuse, what to read next

*Citation:* Charnov 1976 Marginal Value Theorem; Green & Swets SDT; Fleming & Lau confidence

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `atom_consultation` | consult a constraint store at operation boundaries: encode the query, K x d matmul + argmax against stored constraints. | unrated | 0 (not on this read) | 6 | — | yes | DOC |
| `clarify_gate` | detect an under-specified query and ask rather than answer; a turn-taking gate. | unrated | 0 (not on this read) | 15 | — | yes | DOC |
| `completeness_checker` | graded sentence-completeness check over the front-end parse. | unrated | 0 (not on this read) | 2 | — | yes | DOC |
| `conformal` | split-conformal: accept iff the nonconformity score is below the (1-alpha) calibration quantile. | unrated | 0 (not on this read) | 4 | — | yes | MATH |
| `gap_detector` | online detection of what the fact store does not contain. | unrated | 0 (not on this read) | 7 | — | yes | DOC |
| `gap_driven_reader` | rank candidate reading material by how well it supplies a specific missing prerequisite. | unrated | 0 (not on this read) | 12 | — | yes | DOC |
| `glass_box_loop` | retrieve -> gate -> audit -> requery -> commit, with every step inspectable. | unrated | 0 (not on this read) | 7 | — | yes | DOC |
| `information_foraging` | patch-leaving under the Marginal Value Theorem: leave when the instantaneous gain drops below the environment's average. | unrated | 0 (not on this read) | 16 | — | yes | MATH |
| `parse_confidence` | calibrated per-arc reliability for precision-weighting head-driven readers. NOT_BF (a fitted calibrator). | NOT_BF | 0 (not on this read) | 18 | — | **NO ROW** | DOC |
| `quality_proxy` | a cheap glass-box check on whether a learned (subject, object) fact is likely to mean anything. | unrated | 0 (not on this read) | 2 | — | yes | DOC |
| `reasoner` | the composed verification-by-derivation reasoner: an inspectable derivation chain. | unrated | 0 (not on this read) | 9 | — | yes | DOC |
| `refuse_gate` | calibrate tau maximising 0.5*(accept_rate + refuse_rate) on paired in/out-of-distribution scores. | unrated | 0 (not on this read) | 12 | — | yes | MATH |
| `safe_kb_gate` | a familiarity gate making a broad/noisy entity KB safe to consult. | BF | 0 (not on this read) | 1 | — | **NO ROW** | DOC |
| `self_improving_loop` | coherence-gated autonomous keep/revert controller for its own changes. | unrated | 0 (not on this read) | 32 | — | yes | DOC |
| `self_manager` | content-free scalar meta-controllers tuning the gain/threshold of the gates below them. | unrated | 0 (not on this read) | 2 | — | yes | DOC |

### V_INSTR — NO BRAIN STRUCTURE -- instrumentation, harness, storage, profiling and reporting scaffolding

*Citation:* not applicable: this is measurement or plumbing, not a model of a neural system

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `__init__` | package marker; no computation. | unrated | — | 0 | — | **NO ROW** | MATH |
| `ablation` | context managers that mask a relation/edge/modulator so a causal probe can run. | unrated | — | 1 | — | yes | DOC |
| `bigram_gap_measurement` | standardised bigram baseline: predict argmax_t' count(t_prev,t') with add-alpha smoothing; a measurement floor. | unrated | — | 3 | — | yes | DOC |
| `corpus_registry` | an enumerable registry over the corpora on disk -- 'what should I read next' made representable. | unrated | — | 60 | — | yes | DOC |
| `cortex` | a facade composing five cortex primitives behind one forward() API. | unrated | — | 8 | — | yes | DOC |
| `dashboard.__init__` | dashboard package marker. | unrated | — | 0 | — | **NO ROW** | MATH |
| `dashboard.__main__` | CLI entry for the PDF observability report. | unrated | — | 0 | — | yes | MATH |
| `dashboard.app` | Streamlit live-observability app. | unrated | — | 0 | — | yes | DOC |
| `dashboard.panels.__init__` | dashboard panel package marker. | unrated | — | 0 | — | **NO ROW** | MATH |
| `dashboard.report` | multi-page PDF trace report. | unrated | — | 5 | — | yes | DOC |
| `director_kb` | ingest the project's own notes/metrics into a KB of typed triples. | unrated | — | 16 | — | yes | DOC |
| `director_kb_bio_sources` | bio/neuro source fetchers for the KB ingest. | unrated | — | 3 | — | yes | DOC |
| `director_kb_chunk_ingest` | content-chunk KB ingest (DEPRECATED, folded into director_kb). | unrated | — | 11 | — | yes | DOC |
| `director_kb_math_sources` | math source fetchers for the KB ingest. | unrated | — | 2 | — | yes | DOC |
| `director_kb_query` | query the Director-KB by trigram encode + KG traversal. | unrated | — | 20 | — | yes | DOC |
| `encoder_retrain_persist` | opt-in loader making a retrained encoder a discoverable asset. | unrated | — | 4 | — | yes | DOC |
| `experiment` | declarative experiment harness: seeded RNG, traced execution, persisted artifacts. | unrated | — | 34 | — | yes | DOC |
| `foundation_persistence` | deterministic save/reload of the reading-grounded foundation. | unrated | — | 18 | — | yes | DOC |
| `generation` | substrate-native sequence emission from the sequence matrix with Langevin noise. | unrated | — | 3 | — | yes | DOC |
| `harness` | re-export shim for high-reuse experiment helpers. | unrated | — | 0 | — | yes | DOC |
| `ingest_profiles` | named lean ingest profiles -- read a corpus FOR A PURPOSE. | unrated | — | 1 | — | **NO ROW** | DOC |
| `kb_encoder_registry` | resolve a KB encoder by manifest name. | unrated | — | 3 | — | yes | DOC |
| `lm_eval_harness` | top-K + temperature-calibrated BPC + bigram-gap LM evaluation harness. | unrated | — | 4 | — | yes | DOC |
| `mcscript_extraction` | MCScript2.0 XML parsing + parse-structure role extraction for benchmarking. | unrated | — | 7 | — | yes | DOC |
| `metrics` | standard metric suite (health, composition fidelity, capacity, calibration). | unrated | — | 3 | — | yes | DOC |
| `morphology_leakage` | strip morphological leakage from a gold set so a spelling control cannot win on form. | unrated | — | 4 | — | yes | DOC |
| `per_item_log` | one persisted row per held-out item for stage/cause attribution. | unrated | — | 5 | — | yes | DOC |
| `profiling` | per-op latency, FLOPs and memory-access profiling. | unrated | — | 0 | — | yes | DOC |
| `reachability_audit` | graph traversal certifying each entity's reachability to grounded content. | unrated | — | 17 | — | yes | DOC |
| `semantic` | semantic trace-event emit helpers (the WHY layer of the trace bus). | unrated | — | 1 | — | yes | DOC |
| `session_log` | append-only JSONL event log for cross-session recovery. | unrated | — | 240 | — | yes | DOC |
| `snapshots` | timestamped connection-state snapshots emitted onto the trace bus. | unrated | — | 1 | — | yes | DOC |
| `store` | persistent trace storage on DuckDB. | unrated | — | 1 | — | yes | DOC |
| `substrate` | THE assembled substrate object that holds the organs and runs them. | unrated | — | 46 | — | yes | DOC |
| `token_vocab` | deterministic-hash token -> id -> content-free bipolar codebook. | unrated | — | 3 | — | yes | DOC |
| `tracing` | structured trace event bus for every public operation. | unrated | — | 27 | — | yes | DOC |
| `typed_rule_parser` | TSV tablestore -> typed rule-graph rows for the reasoner. | unrated | — | 2 | — | yes | DOC |

### W_ENGINEER — NO BRAIN STRUCTURE -- an engineering primitive for compute or memory budget (the phase-diagram knobs, not an organ)

*Citation:* not applicable: a hardware/scale accommodation, swept not adopted

| organ | computation (one sentence of math) | BF | read cost s / calls | imp | copy | reg | src |
|---|---|---|---|---|---|---|---|
| `chunked_attention` | streaming log-sum-exp attention over M keys in chunks; a memory-budget primitive. | unrated | — | 11 | — | yes | DOC |
| `gpu_generated_streaming_attention` | generate keys/vals on GPU per chunk instead of materialising them. | unrated | — | 3 | — | yes | DOC |
| `gpu_memory_budget` | project peak GPU memory and refuse to start above budget. | unrated | — | 4 | — | yes | DOC |
| `int8_dense` | int8 dense workspace utilities (0.25x memory at matched recall). | unrated | — | 10 | — | yes | DOC |
| `k_cliff_scaling` | closed-form sequence-binding capacity K_cliff(N) = 0.87*N/log2(N). | unrated | — | 3 | — | yes | MATH |
| `lock_in_amp` | phase-sensitive detection for coherent signal recovery. | unrated | — | 1 | — | yes | DOC |
| `noise_channel` | stochastic noise injection at the substrate-cortex boundary. | unrated | — | 4 | — | yes | DOC |
| `streaming_attention` | CPU-resident streaming attention for M >> VRAM. | unrated | — | 1 | — | yes | DOC |
| `whitening` | ZCA / PCA whitening of encoder residuals. | unrated | — | 2 | — | yes | DOC |
<!-- END GENERATED TABLE -->

---

## 5. THE SAME-COMPUTATION GROUPS, FOUND BY READING THE MATH

### 5.1 THE SELECTION GROUP — 28 organs, one equation, five private implementations. **16.8% of read time.**

**The shared equation** (`hdlab/graded_competition.py`, read from code):

```
A_i  = SUM_c  w_c * support_c(i)                     additive Lewis-Vasishth activation
P(i) = softmax(gain * A)_i                           = the Bayesian/FLMP posterior for discrete cue
                                                       integration (McClelland 2013: net = log P(h) +
                                                       SUM log P(e|h))
pick = argmax_i A_i                                  a task-triggered COLLAPSE, not the native output
difficulty = normalised entropy of P                 (Levy 2008)
```

**Where each member sits relative to that equation** (every line below was read from the code, not the name):

| organ | its form of `w_c` | its form of `support_c` | deviation from the shared equation |
|---|---|---|---|
| `graded_competition` | supplied by the caller | supplied by the caller | **none — this IS the engine**; 68 importers, but only two organs actually feed it their decision |
| `graded_role_assigner.coarse_roles` | `strengths_from_counts`: `log P(k｜cfg,value) − log P(k｜cfg)`, Dirichlet-shrunk, **learned by counting the organ's own perceived heads** | per-cue value indicator within a configuration | **none — this is the reference member.** THE ONE implementation of the strength math. |
| `attachment_arm.arc_scores` | the same log-odds contrast form, but built by **`tools/build_attachment_validities.py`**, a separate builder | one dense/sparse cue table per cue family, indexed by (config, value) | **same equation, second table builder.** It does not call `strengths_from_counts`. |
| `graded_role_assigner.agent_competition_pick` | **hand-set constants** `AGENT_VALIDITIES` (3.0 / 2.0 / 2.0 / 2.0 / 1.0 / 6.0 / 2.5 / 2.0), "validity-seeded, swept, not adopted" | 0/1 and 1/(1+distance) indicators | **THE DEVIATION THAT MATTERS: the weights are not counted from reading.** Pri 140 owns this. |
| `affected_entity_resolver.score_and_pick` | hand-swept `gamma_g`, `gamma_t` | `ln`(ACT-R salience) + role-match + patient indicators | same additive-log-evidence argmax, **hand-set gammas**; Principle-B filter applied before the argmax |
| `entity_resolver._retrieve` | per-arm cue weights, **mention-type routed** (Ariel accessibility) | `salience_binder.actr_activation` base + phi / type / predication match | **none in form — this is the consolidation MODEL CASE** (pri 136: six resolvers became one core with arms) |
| `graded_coref_pick` | supplied | ACT-R + phi supports | **none — routes through `graded_competition.graded_pick`** |
| `salience_binder.actr_activation` | Centering role prominence `w(role)` | `dt^-decay` | **not a competition — it is the shared BASE TERM `B_i`** every retrieval member calls. Correctly factored already. |
| `space_reader._pp_ground` / `_dobj_ground` / `_anticipated_ground` | **none** | **none** | **NOT A COMPETITION AT ALL.** Ground selection is a first-match linear scan with hand-ordered fallbacks; `_anticipated_ground` fires only when exactly one candidate exists. The "where-is" row scores 59 in 100. |
| `arc_labeler.predict` | supervised averaged-perceptron weights | hashed arc features | **NOT_BF**: max-margin fitted weights, not counted cue validities |
| `pos_tagger.tag` | supervised averaged-perceptron weights | hashed token features | **NOT_BF**; superseded on the live path by `lexical_categories` |
| `lexical_categories.posterior` | counted `log P(w｜c)`, `log P(suffix｜c)`, `log P(c｜c_prev)` | forward-backward over the sentence, fixed lag 2 | same additive-log-evidence family, **settled by forward-backward instead of a single argmax** — a legitimate arm, not a deviation |
| `thematic_role_labeler` | its own probabilistic cue table | word order, animacy, frame | **a third cue table** for the same Competition-Model decision |
| `convergent_cue_reader` | `w_i ∝ 1/σ_i²` (Ernst-Banks / Ma-Pouget) | calibrated cue values | **the reliability-weighted form** — the principled way to set the weights the agent pick sets by hand |
| the other 14 (`coref`, `coreference_resolver`, `crosstype_bridge`, `crosstype_live_adapter`, `online_entity_cluster`, `typed_coref`, `event_centrality_coref`, `goal_owner_select`, `verb_role_exemplar_selector`, `verb_role_integrated`, `world_state_entity_binding`, `selection_weighted_sharded_typer`, `intent_classifier`, `gated_fusion`, `entity_world_model_resolver`, `commonnoun_binder`, `crf_tagger`) | various | various | wrappers and cue-producers around the same argmax; `commonnoun_binder` and `crf_tagger` are `NOT_BF` |

**The evidence that they are the same computation, not merely similar:** (a) `graded_role_assigner`'s own
docstring says the agent side reuses `graded_competition.net_activation` **verbatim** and the code confirms
it (`A = net_activation(S, w); return c[argmax(A)]`); (b) `attachment_arm`'s per-arc score is built from the
identical `log P(k|cfg,value) − log P(k|cfg)` contrast, from a different builder; (c) `entity_resolver` and
`affected_entity_resolver` and `coref` and `graded_coref_pick` **all four call the same
`salience_binder.actr_activation`** for their base term — the retrieval math is already shared; only the
wrappers are not; (d) the only member with no competition at all is `space_reader`, and that is a finding,
not a classification problem.

**Cost:** 56.55 s of 337.4 s profiled self time (**16.8%**), 6.1M calls.

### 5.2 THE REGISTER GROUP — 6 organs, 3 incompatible data shapes. **0.8% of read time, and the largest coordination gap.**

**The shared computation the brain performs** (Zwaan & Radvansky event-indexing; Zacks event segmentation):
*new evidence is indexed against the current model; a mismatch triggers an update; continuity leaves the
index standing; the index is keyed by the entity and stamped with a time.*

| organ | its data shape (read from code) | update entry point | keyed by | time-indexed? | deviation |
|---|---|---|---|---|---|
| `state_register` | `EntityStateTrack` → list of `StateSpan` intervals | `add_state(value, polarity, aspect, t)`, `apply_event`, `fold(entities, events)` | **entity** | **yes** — `active_at(t)`, `active_spans(t)` | the reference shape |
| `location_register` | `Interval` per entity | `open_interval(node, t)`, `apply_motion`, `fold(entities, events)` | **entity** | **yes** — `node_at(t)` | **near-identical code to `state_register`, different attribute.** `state_register`'s own docstring says so: *"Sibling of `hdlab/location_register.py`: the SAME per-entity interval bookkeeping, a DIFFERENT attribute."* |
| `world_state_register` | `_Slot` per (object, relation) | `set(value, t)`, `apply_event`, `fold(events)` | **OBJECT, not entity** | yes — `value_at(t)` | same interval shape, **a different key space**; `holder_of(obj, t)` is possession, so the entity is the *value*, not the key |
| `goal_register` | a flat `List[Goal]` | `track_status(goals, events)` after the fact | agent **string** | **no** — status is a field, not an interval | **no fold, no revise-on-surprise, no decay.** Satisfaction = predicate + agent match in a strictly later SENTENCE. |
| `affect_register` | a flat `List[Affect]` | none — constructed from `extract_affect(...)` | experiencer **string** | **no** | **no update mechanism at all**; it is an extraction result with query methods |
| `belief_timeline` | **no state** | none | — | recomputed per query | `timeline_belief(events, observed, agent, obj, t)` walks the event list **on every question**. Not a register. |

**The coordination consequence, stated as the owner stated it:** a goal is closed by a verb and an agent and
nothing else. `_read_goals` imports `goal_hierarchy_graph`, `goal_register`, `polarity_operator`,
`verb_subcat_frames` — **and no register at all** (traced from the AST of `situation_reader._read_goals`).
The result state that would tell it whether the goal was actually achieved is sitting in `state_register`,
written by `_read_entity_states`, which runs **earlier in the same read**. Pri 144 owns this.

**Cost:** 2.60 s (0.8%). *Cheap to run, expensive to be wrong.*

### 5.3 THE LEXICAL-READ GROUP — **already consolidated; this is the model case. 4.2% of read time.**

Pri 127 put every read-time lexical lookup behind **one** content-addressed store
(`hdlab/lexicon_foundation.py`, a 78 MB sqlite read at an address). 37 hdlab modules import it; **zero**
modules call `nltk` on the read path (`state_register`'s three WordNet calls go through
`lexicon_foundation.wordnet`, a shim). The surviving frozen lexicons (`animacy_lexicon`, `affect_lexicon`,
`closed_class_lexicon`, `idiom_lexicon`, `force_dynamics_lexicon`, `who_is_who_lexicon`, `event_type`,
`psych_verb_frames`, `meaning_foundation`) are **arms over different relation types**, which is the correct
shape — one store, many reads.

**Cost:** 14.03 s (4.2%) on **6.5 million calls** — 13,449 lexical reads per sentence. That is the shape of
a store being read at an address, and it is the second-largest optimisable surface after §5.1's PPR
(a per-read memo on the hottest accessor is the obvious follow-on; not measured here).

**Why this group matters to pri 143 and 144:** it is the proof that "one structure, many arms" lands without
regression in this substrate. Both other groups should be executed the same way — byte-identical per arm
first, then the shared repair.

### 5.4 THE FOURTH GROUP THE BRIEF INFERRED — the TYPERS, and the inference is only half right

The brief guessed a fourth group: "trackers/typers that classify by a frozen table." Reading the math, those
split in two:

- **Frozen-table typers** (`event_type`, `force_dynamics_lexicon`, `animacy_lexicon`, `who_is_who_lexicon`,
  `idiom_lexicon`, `psych_verb_frames`) are **not a separate computation** — they are §5.3's arms. Merging
  them again would be merging what is already merged.
- **Counted typers** (`force_dynamics_typer`, `causation_typing`, `patient_tendency`, `goal_typing`,
  `predicate_detector`, `verb_subcat`, `selection_weighted_sharded_typer`) score a class by summed evidence
  and take the argmax — **they are §5.1**, not a group of their own.

**So there are three groups, not four**, and the third is done.

### 5.5 THE FIFTH GROUP THE BRIEF DID NOT NAME — the PARSE SOURCES

Four different objects can produce heads for the same sentence: `arc_parser` (hashed perceptron, `NOT_BF`),
`arceager_parser` (transition, `NOT_BF`), `graded_parser` (marginals over the arc-factored scorer), and
`attachment_arm` (the BF cue competition, live default behind `frontend`). The frozen assets say who reads
what: `pos_tagger_ud_ewt_upos.json` is loaded by **7** modules (`arc_parser`, `definitional_extraction`,
`joint_relation_frontend`, `parse_goal_extraction`, `predictive_world_model`, `situation_reader`,
`space_reader`) and `arc_parser_hashed_ud_ewt.npz` by **4** (`graded_parser`, `joint_relation_frontend`,
`situation_reader`, `space_reader`). `hdlab/frontend.py` exists to be the one source and has **40**
importers — so the consolidation is half done and the residue is enumerable. This belongs in pri 143's scope
as the *input* side of the same engine.

---

## 6. THE COST TABLE — one profiled full read, 6 GUM documents, 480 sentences

**Cell:** `experiments/exp_structure_map_cost_v1.py --run --docs 6` (output dir from `get_output_dir` per
Q115; `--self-test` 3/3). **Corpus:** the board's own GUM TEST split (odd document index), evenly spaced
across genres — modern gold only.

**Contention check (required by the brief):** every document was read a second time in the same process,
unprofiled. Ratios were **0.78, 0.81, 0.80, 0.78, 0.81, 0.78** — every repeat *faster* than its profiled
first pass and all six within 4% of each other. **No document was unstable; all six rows are used.** The
laptop had 10 python processes running (a product board and another solver), and the profile still
reproduced to within 4 percentage points across six independent documents.

- **Honest wall clock (unprofiled repeats): 268.4 s for 6 documents = 44.7 s per document, 0.559 s per sentence.**
- Profiled wall clock 337.4 s (cProfile inflates absolute time ~26%; the **shares** and the **ranking** are
  what the consolidation list uses).

### 6.1 BY STRUCTURE GROUP

| structure group | self seconds | share | calls |
|---|---|---|---|
| *(builtins, attributed separately by the profiler)* | 222.22 | 65.9% | 22.5 M |
| **E — selection / competition** | **56.55** | **16.8%** | 6,116,965 |
| **C — ATL hub + spokes** | **23.00** | **6.8%** | 6,017,783 |
| **B — lexical store** | **14.03** | **4.2%** | 6,509,449 |
| A — word form (`morphology`) | 4.97 | 1.5% | 1,075,331 |
| G — situation-model registers | 2.60 | 0.8% | 291,211 |
| F — syntax | 2.16 | 0.6% | 398,462 |
| H — episodic / CLS | 1.92 | 0.6% | 19,311 |
| J — binding algebra | 1.57 | 0.5% | 21,720 |
| M — affect | 0.36 | 0.1% | 35,400 |
| I — working memory | 0.33 | 0.1% | 5,622 |
| Q — space | 0.25 | 0.1% | 28,933 |
| K — prediction | 0.23 | 0.1% | 23,197 |
| R — time | 0.16 | 0.0% | 16,810 |
| L — segmentation | 0.15 | 0.0% | 24 |
| T — learning | 0.07 | 0.0% | 9,569 |
| P — causation | 0.03 | 0.0% | 4,291 |
| N — goals | 0.01 | 0.0% | 1,358 |
| D, O, S, U, V, W | ~0 | — | — |

*The `<builtin>` row is the profiler's own accounting of C-level calls made from inside the organs above; it
is not a 66% idle. §6.2 shows where it actually goes.*

### 6.2 THE TEN MOST EXPENSIVE THINGS IN A READ (by cumulative time)

| rank | what | cumulative s | calls | share of the read |
|---|---|---|---|---|
| 1 | `situation_reader._read_events` → `_read_events_wired` | 236.20 | 6 | **70.0%** |
| 2 | `situation_reader._assign_affect` | 219.94 | 917 | 65.2% |
| 3 | `context_grounded_valence.score_item` | 212.51 | 612 | 63.0% |
| 4 | `force_dynamics_valence.force_dynamics_event_type` | 212.24 | 612 | 62.9% |
| 5 | **`grounded_semantic_graph._ppr`** (spreading activation) | **204.51** | **672** | **60.6%** |
| 6 | — of which `scipy.sparse.csr_matvec` | 184.81 | 20,160 | 54.8% |
| 7 | `force_dynamics_valence.context_sense_sign` | 126.15 | 441 | 37.4% |
| 8 | `grounded_semantic_graph.select_sense_blended` | 125.98 | 437 | 37.3% |
| 9 | `force_dynamics_valence.sense_posterior_in_context` | 83.57 | 447 | 24.8% |
| 10 | `crosstype_live_adapter.merge_crosstype_bridge` | 24.94 | 6 | 7.4% |

**Read this chain carefully, because it is the map's biggest single finding.** *Sixty-one per cent of the
time it takes to read a document is one operation: `r = (1−d)·p + d·Tᵀr`, thirty power iterations over the
frozen dictionary graph, run 672 times — once for each word sense the harm/help judgement needs to
disambiguate inside the event reader.* The affect/valence dimension is 0.1% of the cost table **by its own
module**, because all of its time is spent inside the meaning organ it calls.

### 6.3 THE REDUNDANT WORK, COUNTED

| what | calls | per sentence | verdict |
|---|---|---|---|
| `attachment_arm.arc_scores` | 1,040 | **2.17×** | every sentence's arcs are scored **twice**; the in-order decoder runs 513 times (1.07×) |
| `lexical_categories.posterior` | 952 | **1.98×** | the category posterior is settled **twice** per sentence, despite pri 112's in-order feed |
| `lexical_categories.tag` | 460 | 0.96× | the point tag itself is served from the per-read cache — pri 112 works |
| `lexical_categories.feed_passage` | 6 | 1 per document | **the one in-order feed is genuinely one pass** |
| `scene_segment.parse_conll_sentences` | 24 | **4× per document** | the token stream is read off disk four times per document |
| `coref.parse_litbank_conll` | 12 | **2× per document** | the mention stream twice (the annotated + text-only contract, by design) |

*The brief's INFERRED "~90k redundant re-parses" is directionally right and an order of magnitude smaller at
the reader level: the waste is a factor of ~2, not a factor of hundreds. It is still worth removing, but it
is not where the time is — §6.2 is.*

---

## 7. THE RANKED CONSOLIDATION LIST

Ranked by **duplicated computation × read-time cost × product rows affected**. "Rows" are the eight scored
board rows (pronoun coref, salience, common-noun coref, entity set, who-did-what agent, who-did-what patient,
state, word sense) plus where-is.

| # | target | duplicated computation | cost today | rows it touches | owner |
|---|---|---|---|---|---|
| **1** | **Memoise the meaning organ's spreading-activation walk per read.** Not a consolidation — a measured optimisation the cost table handed us, **now measured end to end (§7.3)**. | 26–40% of its runs inside ONE document ask the identical question | **60.6% of read time; MEASURED saving 28–39% of the whole read = 12.5–17.4 s per document** | **all nine** — it is read latency, so it is every experiment's iteration time | **new brief-ready text, §7.1** |
| **2** | **One cue-competition engine.** `agent_competition_pick`, `space_reader` ground selection, `affected_entity_resolver.score_and_pick` and `attachment_arm`'s table builder become arms of `graded_competition` with `strengths_from_counts` validities. | 5 private scorers for one equation; 2 with hand-set weights; 1 (space) with no competition at all | **16.8% of read time** | agent, patient, pronoun coref, entity set, where-is, state — **6 of 9** | **pri 143** |
| **3** | **One situation-model register.** `state` + `location` + `world_state` share one interval fold; `goals` + `affect` gain one; `belief` stops recomputing. One entity id space. | 3 data shapes for 1 mechanism; 2 dimensions with no update mechanism at all | 0.8% of read time — **cheap to run, and the reason a goal closes on the wrong event** | state, entity set, where-is + the goal/belief/affect abilities off-board | **pri 144** |
| **4** | **Collapse the 14 drifted copies.** | 14 modules exist twice, 834–891 lines apart in the worst case | 0 at read time (the copies are not on the read path) — the cost is **measurement validity**: every cell importing a copy measures a phantom | indirect: any row whose evidence came from a cell that imported a copy | **pri 145** |
| **5** | **One parse source.** Retire the 7-way `pos_tagger_ud_ewt_upos.json` and 4-way `arc_parser_hashed_ud_ewt.npz` reads behind `frontend`. | 4 head producers, 2 of them `NOT_BF` | included in §6.3's 2.17× arc-scoring | agent, patient, state, where-is | **pri 143** (the input side of the same engine) |
| **6** | **Remove the second category posterior and the 4× on-disk token read.** | 1.98 posteriors and 4 disk parses per sentence/document | ~2% of read time | all reader rows | fold into #1's brief |
| **7** | **Rate the 184 unrated modules.** | — | — | none directly; it is the BF audit's own coverage | **new brief-ready text, §7.2** |

### 7.1 BRIEF-READY TEXT FOR ITEM 1 (the optimisation)

> **PROBLEM: sixty-one per cent of the time it takes to read a document is one graph walk, and nothing in
> the architecture says so.** `grounded_semantic_graph._ppr` runs `r = (1−d)p + d·Tᵀr` for 30 iterations,
> 672 times on six GUM documents, driven from `force_dynamics_valence.force_dynamics_event_type` inside
> `situation_reader._assign_affect`. 184.8 of 337.4 profiled seconds are the sparse matrix-vector product
> alone (20,160 of them). The organ is correct and brain-foundational (spreading activation over a
> content-addressed semantic store is the right operation); what is wrong is that it is re-run per event
> rather than per distinct question, and that the reader's own plasticity makes a naive memo unsafe (§8.1).
> The brief: measure how many of the 672 runs ask the identical question within one document, establish
> whether a per-read memo keyed on the exact seed index tuple preserves the read exactly given the organ's
> `observe` paths, and if it does not, find the safe key. **§7.3 has already done that measurement: the
> memo is certified byte-identical on the document where the reader was stable, and it saves 28–39% of the
> whole read.** What is left for the brief is the plastic case and the landing.

### 7.3 THE MEASUREMENT (QUALITY PUSH — `--cache-probe`, 2 GUM TEST documents, one process)

The probe wraps (never edits) `grounded_semantic_graph._ppr` with a counting shim, answers a repeated call
from a per-read memo keyed on the exact seed index tuple, and **returns the memoised value verbatim** so the
read is unchanged by construction. It carries its own control: **each document is first read TWICE
un-shimmed**, so a genuinely unsafe cache is told apart from the reader's own plasticity.

| document | sentences | PPR runs | distinct | **repeats** | read | with memo | **saved** | reader plastic read-to-read? | **memo read byte-identical?** |
|---|---|---|---|---|---|---|---|---|---|
| `GUM_academic_census` | 35 | 116 | 70 | **46 (40%)** | 15.11 s | 9.25 s | **5.86 s (39%)** | **yes** | not certifiable — the *reader* changed between the two un-shimmed reads, so the comparison cannot attribute the difference to the memo (and it did **not** differ beyond that plasticity) |
| `GUM_letter_marcie3` | 28 | 27 | 20 | **7 (26%)** | 3.18 s | 2.24 s | **0.94 s (28%)** | **no** | **YES — identical read, 28% faster** |

**What this establishes, honestly.** On the document where the reader was stable, a per-read memo on the
spreading-activation walk produced a **byte-identical situation model and removed 28% of the read time**.
On the document where the reader was not stable, the memo saved 39% and did not change the read beyond that
plasticity. **Between a quarter and two fifths of the walks in a single document ask the identical
question.** Mean seed size 89–131 synsets.

**And the probe found a second thing worth more than the cache: the reader is PLASTIC within a process.**
Two consecutive un-shimmed reads of `GUM_academic_census` do not agree, because `lexical_categories` and the
validity tables `observe` while they read. That is correct and brain-faithful (§9 iv) — but it means **no
experiment may assume a repeated read is a repeated measurement**, and the first version of this very probe
asserted exactly that and failed. The control is now in the cell.

**A caution on absolute seconds.** This probe ran when the laptop was quieter than the §6 profile did: the
same document reads in 15.1 s here and 48.9 s there. **The ratios within one process are the stable
quantity**; the seconds-per-document figures in §7 apply the measured *percentage* to §6's
contention-checked 44.7 s per document.

### 7.2 BRIEF-READY TEXT FOR ITEM 7 (the rating gap)

> **PROBLEM: two thirds of the substrate has never been rated for brain-faithfulness, and the unrated set
> includes the most expensive organ in the system, the integration layer itself, and the competition
> engine.** `notes/bf_status_registry.jsonl` carries 94 rows against 278 modules on disk. 56 modules execute
> on a live read: 4 `BF`, 39 `BF_SPIRIT`, **13 unrated** —
> `animacy_lexicon`, `binding`, **`graded_competition`**, **`grounded_semantic_graph`**,
> `hippocampal_encoder`, `learner.plugins.ruleind_plugin`, `n400_coherence_monitor`, `patient_tendency`,
> `situation_model_accumulate`, **`situation_reader`**, **`space_reader`**, `state_of_mind`, `verb_subcat`.
> Three of those are load-bearing to this map's own findings: `grounded_semantic_graph` is 60.6% of read
> time, `graded_competition` is the engine pri 143 is built around, and `space_reader` is one of the four
> stand-ins on the live chain. The brief: rate these 13 first, then the remaining 171, using the audit's own
> vocabulary, and record each in the registry's `fidelity_basis` field, which this pass has now made present
> on every row.

---

## 8. THE COORDINATION MAP — what each job uses today, and what the brain would use

Traced from the AST of `hdlab/situation_reader.py` (every `from hdlab …` inside each `_read_*` body plus
every module-level name that body references), 2026-09-16, against the files as they sit on disk this
morning. **Landings in flight** (`entity_resolver.py`, `coref.py`, `situation_reader.py` at 07:46–07:47;
`graded_role_assigner.py` 02:15; `goal_register.py` 2026-09-15 21:45) are mapped **as they were on disk when
read**.

| board row / ability | the reader call | structures it USES today (traced) | structures the brain would ALSO use (cited) | the missing conjunction | rows it would touch |
|---|---|---|---|---|---|
| **who-did-what AGENT** | `_read_events` → `_read_events_wired` | E (`graded_role_assigner`, `thematic_role_labeler`, `np_head_reduce`, `predicate_argument_frontend`), F (`structural_do`), H (`event_bundle`), I (`situation_focus`) | **E with LEARNED validities** (Bates & MacWhinney: cue validity = availability × reliability, *learned*, not set) | the agent pick's weights are 8 hand-set constants while the patient side next to it learns its own from counting. **Same organ, two epistemologies.** | agent, patient |
| **who-did-what PATIENT** | same | same | **K** (`generalized_event_knowledge`: the joint P(patient-kind｜agent, verb), PINNED as joint) | GEK is default-ON but its forward store is not consulted in the patient decision | patient |
| **STATE ("the sky is blue")** | `_read_entity_states` | E (`lexical_categories`, `attachment_arm`), F (`arc_parser`, `pos_tagger` — **its own private parse path**), G (`state_register`, `copular_binding`), R (`temporal_model`) | **G's sibling arms** — a state change is an EVENT the time arm orders and the goal arm reads | it imports `pos_tagger` and `arc_parser` directly instead of `frontend`: a second parse source inside the one row that scores 79/100 | state, where-is |
| **pronoun COREF** | `_read_entities` → `coref` | E (`coref`, `salience_binder`, `graded_coref_pick`, `entity_resolver`), B (`animacy_lexicon`) | **G** (the situation-model foreground: Glenberg-Meyer-Lindem availability, PINNED) and **L** (an event boundary resets the foreground) | `affected_entity_resolver` **has** the foreground window and Principle A/B; `coref` (the scored row) does not read it | coref, entity set, salience |
| **who was AFFECTED** | `_read_affected_entity` | E (`affected_entity_resolver`, `graded_role_assigner`), R (`temporal_model`) | **G** (`state_register` — the result state the undergoer is left in) and **E** (`entity_resolver` — the same object files) | it builds its own entity keys; the object-file organ's ids are a different space (744 negative / 345 positive / 0 shared) | coref, entity set |
| **common-noun COREF** | `read` → `_resolve_commonnouns` | E (`typed_coref`, `entity_resolver`, `crosstype_live_adapter`) | **C** (the hub's type code) — already partly wired via `typed_spokes` | — (this one is in reasonable shape; it is the row that LOSES to the simple rule, so the gap is quality not wiring) | common-noun coref |
| **ENTITY SET** | `read` → `_build_entities` | E (`entity_resolver.cluster`, `crosstype_live_adapter`, `online_entity_cluster`) | **G** (one id space shared with every register) | the registers key on strings; the object-file organ keys on ints. **Pri 132's one id space.** | entity set, state, where-is, goals, belief |
| **WHERE-IS** | `_read_space` → `space_reader` | Q (`location_register`), F (`pos_tagger`, `arc_parser` — **its own private parse**), E (lazily `frontend`) | **E** (ground selection as a competition, not a first-match scan) and **G** (a motion event the time arm orders) | ground selection has no competition at all (§5.1); the row scores 59/100 | where-is |
| **WORD SENSE (WiC)** | `_read_senses` (lazy) + `grounded_semantic_graph` inside affect | C (`grounded_semantic_graph`, `underspecified_sense_reader`), D (`diagnostic_context_wsd`, `semantic_control`) | **G** (the situation model as the disambiguating context, not the sentence window) | the sense read is passage-blind: it seeds PPR from context words, not from the situation model's own entities and events | word sense, agent, patient (the sense feeds harm/help) |
| **GOALS** (off-board ability) | `_read_goals` | N (`goal_register`, `goal_hierarchy_graph`, `verb_subcat_frames`), G (`polarity_operator`) | **G (`state_register`)** — Trabasso: an outcome closes a goal only when it matches the goal's CONTENT; **R** for ordering | **the owner's named gap: the goal register decides closure without the state register's result state** | the goal abilities; state indirectly |
| **BELIEF** (off-board ability) | `_read_belief` | O (`belief_reader`, `belief_timeline`, `perceptual_access_ledger`) | **E (`entity_resolver`)** — a belief is about an ENTITY, so it needs the object-file id | **belief binds nothing: the id spaces are disjoint** | belief; entity set |
| **AFFECT** (off-board ability) | `_read_affect` | M (`affect_lexicon`), G (`affect_register`), N (`goal_register`), B (`psych_verb_frames`) | **E** for the experiencer bind; **G** for the state | affect **does** read goals — the one dimension that already coordinates, and the template for the rest | affect |

### 8.1 THE 23 DEFAULT-ON DIMENSIONS, AND WHICH ROW SCORES EACH (pri 139 mapped 10; here are all 23)

The brief says "23 default-ON `track_*`". The disk says **17 literal `track_*` flags default-ON, 1 OFF
(`track_coherence`), plus 6 further dimension flags** — `timeline_register`, `bind_event_tokens`,
`bind_entity_states`, `predict_revise`, `predict_surprisal`, `read_polarity`. **17 + 6 = 23.** That is the
reconciliation.

| # | flag | field it writes | eager or lazy | which board row / ability scores it |
|---|---|---|---|---|
| 1 | `track_space` | `sm.locations` | eager | **where-is** ("picking out place information", 59/100) |
| 2 | `track_belief` | `sm.believes` / `sm.knows` | eager | belief ability (65/100) |
| 3 | `track_world_state` | `sm.world_state` | eager | "keeping a fact true until something changes it" (100/100) |
| 4 | `track_goals` | `sm.goal_register` | eager | "whether an event helps or blocks a goal" (98/100) |
| 5 | `track_goal_thwart` | goal status | eager | same row |
| 6 | `track_affect` | `sm.affect_register` | eager | "who is having the feeling" (21/100) |
| 7 | `track_tom_action` | `sm.predict_action` | **lazy closure** | **NO ROW** — island |
| 8 | `track_infer_emotion` | `sm.infer_emotion` | **lazy closure** | "how a character probably feels" (90/100) |
| 9 | `track_bridges` | `sm.bridges` | **lazy closure** | "resolving 'the animal' to the dog just mentioned" (57/100) |
| 10 | `track_senses` | `sm.select_sense` | **lazy closure** | **word sense (WiC)** — but the PPR that costs 61% runs from the *affect* path, not from here |
| 11 | `track_affected_entity` | `sm.affected_entity` | eager | "who was affected by what happened" (42/100) |
| 12 | `track_prediction` | `sm.predict_next_event` | **lazy closure** | **NO ROW** — the module says "NEW ISLAND — no downstream consumer today" |
| 13 | `track_causal_reasoning` | `sm.causal_reasoner` | **lazy closure** | "following a chain of causes" (26/100), "why when the cause is sentences away" (25/100) |
| 14 | `track_spatial_reasoning` | `sm.spatial_reasoner` | **lazy closure** | "where things are relative to each other" (20/100) |
| 15 | `track_predictive_causal` | `sm.causal_antecedent` | **lazy closure** | "whether one event was needed for another" (35/100) |
| 16 | `track_temporal_reasoning` | `sm.temporal_reasoner` | **lazy closure** | "which of two events came first" (59/100), "same time" (99/100) |
| 17 | `track_natural_logic` | `sm.entails` | **lazy closure** | "is a kind of" (77/100), "all/some/none" (83/100), "not" (92/100) |
| 18 | `timeline_register` | `sm.timeline_order` | eager | "event order when the text does not say it outright" (56/100) |
| 19 | `bind_event_tokens` | `sm.event_tokens`, `sm.episodic_store` | eager | **NO ROW** — the episodic backbone is unscored |
| 20 | `bind_entity_states` | `sm.entity_states`, `sm.state_register` | eager | **board row `state`** (79/100) |
| 21 | `predict_revise` | fills dropped patients | eager | **board row `who_did_what_patient`** |
| 22 | `predict_surprisal` | surprisal + abstain flag | eager | "knowing when to hold back on who was acted on" (96/100) |
| 23 | `read_polarity` | `EventRecord.polarity`, `.quantity` | eager | **NO ROW** — the module says the QA/coref/goal/causal consumers still read propositions polarity-blind |
| (24) | `track_coherence` | `sm.inferred_coherence_links` | **default OFF, with a measured reason** | would score "why when the cause is sentences away" |

**Four of the 23 have no consumer at all** (`track_tom_action`, `track_prediction`, `bind_event_tokens`,
`read_polarity`). Ten are lazy closures that cost nothing until invoked — so the "N parallel silos" worry is
**cheaper than it looks at read time and exactly as disconnected as it looks in the wiring**.

---

## 9. THE OWNER'S PUSH SCRIPT, ANSWERED WITH NUMBERS

**(i) For each rung of the live chain: which brain structure, and is our organ its computation or a stand-in?**

| rung | organ | structure | computation or stand-in |
|---|---|---|---|
| tokens & case | `scene_segment` | L (segmentation) / plumbing | **plumbing** — the tokens come off the CoNLL column; no computation claimed |
| word categories | `lexical_categories` | **E** — Competition Model readout | **the computation** (counted `log P(w｜c)` + suffix + transition, forward-backward, fixed lag 2). `BF_SPIRIT`. |
| lemma | `morphology` | **A** — morpho-orthographic decomposition | **the computation** — byte-identical to WordNet morphy over 6.3M comparisons. `BF`, one of the 8. |
| heads | `attachment_arm` | **E/F** — cue competition + incremental attachment | **the computation**, with its own table builder instead of `strengths_from_counts` (§5.1). `BF_SPIRIT`. |
| grammatical roles | `graded_role_assigner.coarse_roles` | **E** | **the computation** — the reference member of the selection group. `BF_SPIRIT`. |
| **agent pick** | `graded_role_assigner.agent_competition_pick` | **E** | **a STAND-IN on the weights**: 8 hand-set constants where the sibling learns from counting |
| mention discovery | `coref` / `referent_per_np` | **E/G** | **the computation** (ACT-R + phi). `BF_SPIRIT`. |
| entity files | `entity_resolver` / `online_entity_cluster` | **E** | **the computation**, and the consolidation model case. `BF_SPIRIT`. |
| events | `event_bundle` | **J** | **the computation** (FHRR role-slot binding). `BF`. |
| states | `state_register` | **G** | **the computation** for intervals; **a stand-in for the update rule** (no revise-on-surprise, no decay) |
| time | `temporal_model` | **R** | **the computation** in three layers; the consolidation model case for pri 145 |
| goals | `goal_register` | **N/G** | **a STAND-IN**: a list with a status field, not an indexed register (§5.2) |
| belief | `belief_reader` / `belief_timeline` | **O/G** | **a STAND-IN**: recomputed per query, binds no entity id |
| causes | `causation_typing` | **P** | **the computation** (Talmy/Wolff force vectors). `BF_SPIRIT`. |
| word senses | `grounded_semantic_graph` | **C** | **the computation** (spreading activation as PPR) — and 61% of read time |
| **where-is** | `space_reader` | **Q/E** | **a STAND-IN**: first-match linear scan, no competition |

**Four stand-ins on the live chain: the agent pick's weights, the goal register, the belief timeline, and
ground selection.** Three of the four are inside pri 143 or pri 144's scope; the fourth (belief) is pri 132's
id space.

**(ii) Which consolidations let ONE improvement reach SEVERAL tasks at once?**

- **Pri 143 (one engine):** a single change to the engine — learned validities instead of hand-set weights,
  a graded decision instead of an argmax, a clause-scope gate — reaches **who-did-what agent, who-did-what
  patient, pronoun coref, entity set, where-is and state: 6 of the 9 scored rows**, plus 16.8% of read time.
- **Pri 144 (one register):** one update rule reaches **state, where-is, entity set** on the board and the
  **goal, belief and affect** abilities off it — and it is the only way the goal register ever sees a result
  state.
- **Pri 145 (collapse the copies):** reaches no row directly; it reaches **every future measurement**, which
  is why it is fourth and not first.
- **Item 1 (the PPR memo):** reaches **all nine rows** because it is latency, not accuracy — it makes every
  board run and every solver iteration 2.5x faster.

**(iii) Which tasks would gain from a structure they do not read today, and what bounds the gain?**

| task | structure it does not read | the number that bounds the gain |
|---|---|---|
| **goals** | `state_register`'s result state | pri 135's population: **212 goals**. Today closure = predicate + agent match in a later sentence; the object/theme is ignored ("buy bread" is satisfied by "bought milk"). The bound is the share of those 212 whose closing event carries a result state the state register already holds — **unmeasured, and cheap to measure** (§10). |
| **pronoun coref** (the scored row) | the event-model FOREGROUND, which `affected_entity_resolver` already computes | the foreground is worth **+0.0084 alone and CI-separated in combination** on the affected-entity population (`BRAIN_MATH_REFERENCE` §A), with the window-scramble twin collapsing to 0.216. The coref row does not read it. |
| **who-did-what patient** | `generalized_event_knowledge`'s joint P(patient-kind｜agent, verb) | PINNED as joint; the marginal stand-ins were **REFUTED-AS-BUILT** (−0.045…−0.118 CI-sep when fused over 18 candidates). The bound is the in-focus top-3 ceiling: **0.753 vs 0.540 today** on THIRD pronouns. |
| **where-is** | the competition engine | the row is **59 in 100** against a simple rule at 52. A first-match scan cannot express "two grounds compete". |
| **belief** | the object-file id space | **0 shared ids** between the two spaces today (744 negative / 345 positive). The bound is total: belief binds nothing. |
| **word sense** | the situation model | the sense read seeds from context words, not from `sm.entities`/`sm.events`; the WiC row is **85 in 100** already, so the gain here is to the *downstream* harm/help and patient rows, not to WiC |

**(iv) Anything frozen that the brain keeps plastic?**

Measured, not asserted. The reader **is** plastic within a process — two consecutive un-shimmed reads of the
same GUM document do not produce identical `SituationModel`s (`--cache-probe`'s plasticity control, §10),
because `lexical_categories` and the validity tables `observe` while they read. That is correct and
brain-faithful. What is **frozen and should not be**:

- `AGENT_VALIDITIES` — 8 constants in source, no `observe` path. The sibling role table has one.
- `affected_entity_resolver`'s `GAMMA_G` / `GAMMA_T` — swept constants, no accrual.
- `space_reader`'s fallback ORDER — a hand-written precedence, not a learned validity.
- `attachment_arm`'s validities are learned but rebuilt **offline** by `tools/build_attachment_validities.py`;
  the online `observe` path exists for the role table and not for the arc table.
- `goal_register` has no learning path of any kind.

**(v) How the literature organises reading comprehension by structure, and where we deviate.**

| the literature's structure | what it says | our map | deviation |
|---|---|---|---|
| **Event indexing** (Zwaan & Radvansky 1998) | ONE situation model, five dimensions (space, time, protagonist, causation, intentionality) sharing one indexing mechanism | group **G**, 15 modules | **we have the dimensions and not the shared mechanism** — 3 data shapes (§5.2). This is the single clearest deviation in the map. |
| **The Competition Model** (Bates & MacWhinney) | role assignment by cue validity = availability × reliability, **learned from the language** | group **E**, 28 modules | the form is right everywhere; **two members set their weights by hand** instead of learning them |
| **Hub-and-spoke** (Patterson/Lambon Ralph/Rogers) | one amodal ATL hub, modality spokes, a double dissociation | group **C** (20) + group **B** (16) | **the store is consolidated (B is done); the hub REPRESENTATION landed but readers are not repointed at it** (`semantic_hub`, 1 importer) |
| **Basal-ganglia selection** (Redgrave/Prescott/Gurney; Frank) | ONE selection loop reused across motor, attention, WM and language | group **E** + group **S** | **we have the loop as a module (`graded_competition`, `action_selection`) and five organs that do not call it** |
| **Construction-integration** (Kintsch) | a propositional net settles into a coherent representation | `bridging_inference`, `coherence_reader` | present; `track_coherence` is default-OFF with a measured reason |
| **Cue-based retrieval** (Lewis & Vasishth 2005) | one content-addressable retrieval serving binding, coreference, filler-gap | `salience_binder` + `entity_resolver` + `content_addressable_retrieval` | **this one we did right**: four organs share the one `actr_activation` base term |

**(vi) Audit of this map: which rows were assigned by NAME rather than by reading the math?**

**83 of 278 rows (30%) were read from the code this pass** (`src = MATH`); **195 (70%) take the module's own
stated computation** (`src = DOC`). The honest position: the DOC rows are not guesses — this codebase states
its computation in the docstring as a discipline — but they are **not independently verified by me**, and a
docstring can be stale the way `ORGAN_MAP.md`'s file count is stale. Every row load-bearing to §5 (the
groups), §7 (the ranking) and §9(i) (the live chain) is a MATH row. The DOC rows are concentrated in groups
V (instrumentation), W (compute budget), T (learning) and the long tail of unwired islands — precisely the
places where being wrong costs the next brief nothing. **If pri 143/144/145 touch a DOC row, that row must be
re-read from code first.**

**(vii) Prior work on disk, checked before ranking.**

- **pri 134** (`the_fine_non_argument_relations…`, SOLVED): four organs reused for one rung, and the finding
  that the crosstype bridge was **landed and not live** (292 of 292 mentions out of range). The model for
  "reuse what exists"; its lesson — *repairing either half alone buys exactly nothing* — is why §7's items 2
  and 5 are one owner (pri 143), not two.
- **pri 137/139** (aliases): pri 137 collapsed the space parse sources; pri 139 built
  `verification/test_organ_copies_are_one_object.py`, the standing witness this map re-ran (16 pairs, 14
  drifted, 2 thin shims, 4/4 checks PASS, 0 new drift since the 2026-09-16 baseline).
- **The `temporal_model` consolidation of 2026-09-11**: three modules (`temporal_ordering`,
  `temporal_ordering_multiframe`, `temporal_order_register`) became three LAYERS of one organ with
  backward-compatible shims. **That is the template pri 145 should follow**, and it is the only place in the
  substrate where a consolidation has already been executed end to end.

---

## 10. WHAT THIS MAP DID NOT MEASURE (named, not hidden)

- **The PPR memo is measured on 2 documents, not 6, and certified on 1.** §7.3 has the numbers and the
  control. The identity certificate exists for `GUM_letter_marcie3` (stable reader, byte-identical read, 28%
  saved); for `GUM_academic_census` the reader's own plasticity makes an identity claim unavailable, and the
  39% there is reported as a timing, not as a certified equivalence. **The saving is demonstrated; its
  universality is not.** A landing brief needs the plastic case.
- **The goal↔state coordination gain is sized by its population (212 goals), not by a run.** Measuring it
  needs the goal register and the state register in one process with a shared id — which is pri 144's first
  deliverable, so it is correctly that brief's opening measurement, not this map's.
- **Only the `annotated` input contract was profiled.** The text-only contract (pri 125's honest product
  path) will spend more in pronoun discovery and less in mention parsing; the ranking is unlikely to move
  because item 1 is 60.6% and item 2 is 16.8%.
- **`<builtin>` at 65.9%** is the profiler's attribution of C-level calls made from inside the organs, 54.8
  points of which §6.2 traces to `scipy.sparse.csr_matvec` inside the PPR. The remaining ~11 points are
  dict/list operations spread across the 6.5M lexical reads and 6.1M selection calls; they are not a
  separate organ.
