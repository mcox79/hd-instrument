# Research: The Fading Crutch -- Gap-Driven External Supply + Schema Generalization (2026-08-10)

Filed by: research (Sonnet, foreground, no nested agents per Director OPS). Drill 1 (the crux) of
the USER-cracked pivot: a gap-driven external CRUTCH that fills world-knowledge gaps ONLY when the
substrate flags one, whose fills the substrate GENERALIZES into schemas that cover unseen gaps, so
the crutch fires less over time and FADES. Task: design the crutch + the generalization mechanism,
and honestly assess the fade-curve shape.

KB-CHECK DONE FIRST (mandatory dedup, heavy prior art found -- this note EXTENDS, does not
rediscover): `tools/substrate_query.sh` + `tools/director_kb_query.py` both hit dense prior art.
Load-bearing prior art read in full this cycle:
- `notes/research_prior_art_narrative_schema_learning_2026-08-09.md` -- **already did the
  crutch-source comparison exhaustively** (7 KBs live-verified: ATOMIC/ATOMIC-2020/ConceptNet/
  GLUCOSE/ASER/CausalBank/DeScript) AND already confirmed, by live search, that NO PRIOR WORK does
  incremental/online/self-extending schema induction from a streaming corpus -- this IS the crux
  gap this drill is asked to design for. This note does not re-run that comparison; it inherits its
  verdicts (Section 1) and adds the piece that note explicitly deferred: the fade/generalization
  mechanism design (Sections 3-4) and a fresh, generic-term external check on two angles that note
  did not carry (Sections 3, 5).
- `notes/research_content_causal_associative_knowledge_store_2026-08-09.md` -- the CSKG spine is
  **already landed on disk**: 482,588 nodes / 1,238,686 typed edges, ATOMIC-dominated (711,428
  edges), plus the exact output-form schema (`bind(REL,..)+bind(ARG0,..)+bind(ARG1,..)+
  bind(SOURCE,..)+bind(TRUST,..)`) this note's Section 2 inherits and specializes.
- `notes/direction_b_grounded_knowledge_build_plan_2026-08-09.md` -- the M1-M4 staged plan this
  note's design slots into (M2 = "learn the mapping from exposure," exactly this drill's ask).
- `notes/research_comprehension_barrier_map_brain_foundational_2026-08-10.md` (today, read in
  full) -- names B1 grounding content and B10 CLS-learning as the two barriers this design serves,
  and discloses the one honest negative signal that calibrates Section 4: the ONLY empirical growth
  curve on disk today (`grounding_acquisition_loop`, 0->40 over 5 passes) is **content-hollow**
  (function/light-word dominated), not yet demonstrated on open-content world-knowledge.
- Code read on disk this cycle (not from memory): `hdlab/consequence_learning_loop.py` (the
  INJECT-ONCE dictionary-prior pattern -- this IS a working, self-tested instance of "crutch fires
  once, substrate banks it"), `hdlab/grounding_acquisition_loop.py` (FLAG->LIBRARY->CONSOLIDATE->
  GUARD->BANK), `hdlab/frame_induction.py` (the ONLY organ on disk that demonstrates
  construction-cue generalization to an UNSEEN lexical item, measured: subj-axis acc=0.833,
  obj-axis acc=0.455, both real numbers from `data/exp_frame_induction_oov_psych_real_v1/
  metrics.json`), `hdlab/learner/core.py` + `hdlab/learner/plugins/proginduction_plugin.py`
  (the MDL model-selection engine -- the organ this note names as the missing Level-2 wiring),
  `hdlab/schema_exemplar_bayes.py` (a ROUTER, not a generalizer -- flagged as a common
  misidentification below), `hdlab/wordnet_polarity_propagation.py::pseudo_counts_from_dictionary`
  (the exact pattern this note generalizes from WordNet-antonym-propagation to an external
  structured KB), `data/datasets/conceptnet5_en_100k.jsonl` (disk-read predicate histogram, Section
  1).

External check this cycle (generic math/psycholinguistic terms only, per query-privacy discipline;
no substrate-novel names off-platform): 3 WebSearches -- KB structure/license cross-check, Pinker's
dual-mechanism (words-and-rules) model, and Bayesian/schema-from-few-examples literature. These
sharpen Section 4 (the fade curve) with citations the 08-09 survey did not carry (that survey's
scope was schema-INDUCTION-from-text methods, not the psycholinguistic regular/irregular-frequency
literature this drill's fade-curve question specifically needs).

---

## HEADLINE

**The crutch already exists as landed data (CSKG spine, ATOMIC-dominated, 1.24M edges, zero new
sourcing cost) and its output-form schema is already designed (typed bind-then-bundle with native
SOURCE/TRUST provenance). What does NOT exist is the generalization step that makes it fade.** The
project already owns, self-tested and disk-verified, exactly ONE HALF of a Pinker-style
dual-mechanism acquisition loop: the "irregular/memorize" pathway (`consequence_learning_loop`'s
INJECT-ONCE dictionary-prior + `grounding_acquisition_loop`'s FLAG->LIBRARY->CONSOLIDATE->GUARD->
BANK), which banks a crutch-supplied fact PER ITEM so a repeated encounter of the SAME item never
re-consults the crutch. This pathway fades only via item-repetition (Zipf/Heaps decay) and NEVER
generalizes to a structurally-similar but lexically-unseen gap. The "regular/rule" pathway -- the
one that would let a handful of crutch fills cover a whole CLASS of unseen gaps -- is
`hdlab/learner`'s MDL model-selection engine (estimation / ruleind / proginduction, already wired
and already proven to generalize across an unseen lexical item via construction-cue features in
`frame_induction.py`, subj-axis 0.833 held-out) -- but it has never been fed crutch-typed episodes.
Wiring the crutch's typed relation-label as the learner's target class, with construction-cue (not
identity) features as the input, is the concrete, buildable, not-yet-built step that makes THIS
drill's "generalize into schemas that cover unseen gaps" claim real instead of aspirational. The
honest fade-curve shape, calibrated against Pinker's regular/irregular frequency-inversion finding
and this project's own frame_induction split (0.833 vs 0.455 by axis) and DesireDB's own residual
sizing (~30% bespoke long-tail), is **steep-then-long-tail, never fully flat to zero** -- a real,
useful, brain-consistent result, not a breakthrough that eliminates the crutch.

P_deflated = **0.38** for "this two-level design, as specified, clears its Section 6 cheap decisive
test" (novel-synthesis cap 0.50; net revision from an initial 0.40: +0.02 for a concurrent same-day
audit finding a SECOND, already-validated Level-2 mechanism this note's own code read had missed,
-0.04 for a second, sharper concurrent audit finding that BANK's current write target structurally
CANNOT fade at all -- a flat side-table dict, not a migrating trust-weighted engram -- meaning the
Section 6 test as specified would need the `hd_fact_store` migration as a precondition, not an
optional nicety, before its own consult-rate measurement means what it claims to mean). Three
independent things must now hold, not two: (i) Level 1's crutch connector must target the
schema-consistency-guarded consolidator, not the weaker one it is wired to today (Section 3b); (ii)
BANK output must migrate into a natively-read, trust-weighted structure (`hd_fact_store`) rather
than a permanent side-table, or no fade curve -- Level 1 or Level 2 -- is structurally measurable
(this section); (iii) a Level-2 mechanism (MDL rule or CA3/DG attractor clustering, both isolated-
precedent-validated) must actually generalize when fed EXTERNAL-KB-typed content specifically, which
neither this note nor either concurrent drill has tested. Each is independently a small, named,
buildable piece; none has been composed with the others yet.

---

## 1. THE CRUTCH -- source recommendation (inherits the 08-09 survey; adds disk + license checks)

The 08-09 schema-learning survey already rated 7 candidate resources for exactly this use case
(coverage of everyday-narrative causal/script/role knowledge, structure, vetted-ness, license). Its
verdicts, cross-checked against a fresh external search this cycle (converges, no contradiction
found) and against what is **actually on disk today**:

| Resource | Structure | Everyday-narrative fit | Vetted | License/availability | Verdict |
|---|---|---|---|---|---|
| **ATOMIC / ATOMIC-2020** (Sap et al. 2019 AAAI; Hwang et al. 2021 AAAI) | 9 (orig) / 23 (2020) TYPED if-then relations (xIntent/xNeed/xWant/xEffect/xReact + oEffect/oWant/oReact + physical-entity + event-centered) | HIGH -- purpose-built for social/psychological event->reaction commonsense, exactly the goal/intent/outcome axis B1 grounding needs | Crowdsourced (MTurk), 86.2% annotation validity measured | CC-BY (2020 dataset confirmed this cycle); static TSV, symbolic half fully separable from the neural COMET generator (COMET is reference-only -- do not touch) | **PRIMARY -- already the dominant edge mass of the on-disk CSKG spine (711,428/1,238,686 edges, 57%)** |
| **ConceptNet 5.5** | 34 typed relations; narrative-relevant subset `Causes`/`HasSubevent`/`MotivatedByGoal`/`CausesDesire`/`UsedFor`/`ObstructedBy` | MEDIUM -- 90% of ConceptNet's 3.4M tuples are taxonomic/lexical (IsA/RelatedTo/DerivedFrom), not causal/script; the narrative-relevant subset is real but sparse next to ATOMIC | Merged expert (WordNet) + crowdsourced (OMCS) + games-with-a-purpose | CC BY-SA 4.0; already on disk (`data/datasets/conceptnet5_en_100k.jsonl`, 100K-edge slice) | **SECONDARY -- already 219,637 edges in the landed CSKG spine.** Disk-verified this cycle: the LOCAL 100K-slice on disk is narrower than the full CSKG ingest (only 8 predicates present: AtLocation 27,797 / CapableOf 22,677 / Antonym 19,066 / Causes 16,801 / DerivedFrom 6,535 / CausesDesire 4,688 / DefinedAs 2,173 / CreatedBy 263 -- **no HasSubevent, no MotivatedByGoal, no UsedFor in THIS slice**, even though the CSKG spine's own ingest evidently drew a different/fuller ConceptNet pull with those relations present per the causal-store note's table). Flag for a follow-up disk-reconciliation, not a re-source. |
| **GLUCOSE** (Mostafazadeh et al. 2020 EMNLP) | 10 causal dimensions, semi-structured (typed dimension slot + a `specific-statement` AND a `general-rule` template pair per instance) | HIGHEST narrative fit of any candidate -- grounded IN ROCStories 5-sentence narratives (story-register, not template/newswire-register like ATOMIC/ConceptNet) | Crowdsourced elicitation | Research-use, static tuples; not yet on disk | **TERTIARY / scale-up option #1.** The one candidate whose fit to actual STORY prose (vs ATOMIC's closed event-template vocabulary) is best-evidenced -- correctly ranked #1 scale-up by the 08-09 note. Its `general-rule` field is semi-free-text (a light template, not a closed relation vocabulary) -- usable as crutch content but needs a thin structuring pass before matching Section 2's typed-edge form. |
| **ASER** | 15 PDTB-style relations, fully automatic extraction (no crowd validation) | MEDIUM-HIGH scale, LOWER precision (co-occurrence-weighted, reporting-bias) | Automatic, not vetted | MIT-licensed; not on disk | Scale-up option #2, noisier than ATOMIC -- correct to rank below GLUCOSE. |
| **CausalBank** | (cause-span, effect-span) SENTENCE-PAIR tuples -- spans are free text, NOT typed relation edges | LOW structure fit -- this is the one candidate that fails the task's own hard "structure not prose" requirement; a span still needs its own extraction/parse before it is usable, which reopens the B5 extraction wall this whole program exists to route around | Fully automatic (connective-template mining) | GitHub release; not on disk | **Ranked last for THIS use case specifically** (correctly deprioritized by the 08-09 note for a different, milder reason -- explicit-connective coverage bias; this note adds the sharper reason: free-text spans violate the crutch's own "must emit structure" requirement). |

**Recommendation: the crutch is not something to build or download -- it is already landed.** The
CSKG spine (`cskg_foundation_v1`, 1,238,686 typed edges, ATOMIC-dominant) is the crutch. The one
concrete follow-up this drill's disk audit surfaces (not a blocker, a cheap housekeeping item): the
100K-line ConceptNet slice found separately on disk (`data/datasets/conceptnet5_en_100k.jsonl`) is
missing the script/goal-relevant relations (`HasSubevent`, `MotivatedByGoal`, `UsedFor`) that the
causal-store note's own table claims ARE present in the landed spine (219,637 ConceptNet edges) --
reconcile which ConceptNet pull is authoritative before relying on those specific relation types for
Level-2 construction-cue labels (Section 3). GLUCOSE remains the correct scale-up target if the
ATOMIC-dominated spine proves too template-bound on real story prose (a risk the 08-09 note already
flagged and this note does not re-litigate).

## 2. THE OUTPUT FORM -- what the crutch hands the substrate at a gap (inherited, specialized)

Already designed, not invented here (`research_content_causal_associative_knowledge_store_2026-08-09.md`
Section 3, re-cited because it is THE answer to this deliverable): a crutch fill is a single typed,
bound, glass-box fact vector, never free text:

```
fact_vec = quantize( bind(REL, relation_type)          # e.g. "at:xEffect", "cn:Causes", "at:oReact"
                    + bind(ARG0, cause_or_subject_concept)
                    + bind(ARG1, effect_or_object_concept)
                    + bind(SOURCE, "ATOMIC" | "ConceptNet" | "GLUCOSE" | "learned")
                    + bind(TRUST, trust_level) )
```

`REL`/`ARG0`/`ARG1` are recoverable by unbind+cleanup (`hdlab/hd_fact_store.py::FactRecord`,
`hdlab/situation_model_accumulate.py::CausalLinkRegister` for the event-to-event special case).
`SOURCE`/`TRUST` are natively bound in, not side metadata -- a query can always answer "why do you
believe this" by unbinding SOURCE, which is the auditability differentiator the barrier-map note
names as the substrate's defensible product edge. **This is exactly right for THIS drill's
requirement that the crutch emit structure, not prose**: a crutch consult returns a `(REL, ARG0,
ARG1)` triple straight from ATOMIC's/ConceptNet's own typed schema, with zero parsing/extraction
step on the crutch side -- the extraction wall (B5, the barrier map's binding constraint) is a
REAL-PROSE-INPUT problem, not a crutch-OUTPUT problem, and this design never conflates the two.

**One addition this drill makes** (not previously specified): for the generalization step in
Section 3 to work, a crutch fill needs a SECOND, parallel payload alongside `fact_vec` --
the CONSTRUCTION-CUE feature list of the gap-context that TRIGGERED the crutch consult (the
surface cues at the gap site: argument structure, animacy, particle/preposition, voice -- the same
`REAL_CONSTRUCTION_ATOMS`-shaped feature set `frame_induction.py` already declares). This is cheap
(the features are already being computed by the extraction front end to LOCATE the gap in the
first place) and is what lets the crutch fill become a training EPISODE for Section 3's learner,
not just a stored fact.

## 3. THE GENERALIZATION MECHANISM (the crux) -- mapped to owned organs, concrete abstraction step

**Where the substrate flags a gap (the trigger)** -- three already-built, disk-verified trigger
patterns, no new mechanism needed here:
1. **Lexical/concept OOV** -- plain dict-membership (`frame_induction.is_oov`,
   `consequence_learning_loop`'s `in_lexicon` check). A word/concept not in the grounded lexicon.
2. **Causal-query miss** -- `CausalLinkRegister.query_effect_of`/`query_cause_of` (or a KGStore
   `pull_in`) returns None / below-confidence. The store was asked a question it cannot answer.
3. **Generic novelty/surprise** -- `hdlab/predictive_coding.py::threshold_gate`, a residual-
   magnitude gate (Rao-Ballard/Friston predictive-coding residual) already used as the general
   PROPOSE trigger in the 08-06 acquisition-loop spec. This is the brain-general version of (1)/(2).

**What is ALREADY BUILT (Level 1 -- the "irregular/memorize" pathway, Pinker's terms, Section 4):**
`hdlab/consequence_learning_loop.py::learn_corpus(dictionary_priors=...)` is a working, self-tested
instance of "external crutch fires once, substrate consolidates and stops asking again" --
`pseudo_counts_from_dictionary`-shaped priors are seeded INTO the vote counter EXACTLY ONCE (not
per-pass, a specific bug-class the self-test guards against by name: "prior tripled/mutated across
passes"), real corpus exposures accumulate additively on top, and `consolidate()` gates a per-LEMMA
POS/NEG/GROUNDED_NEUTRAL/PENDING decision via an abstain-band vote margin
(`self_improving_loop.decide_keep_or_revert`'s architecture, reused verbatim). Once consolidated, the
lemma is registered into a Tier-3 overlay (`verb_lexical_similarity.register_acquired_outcome`) that
production lookups consult BEFORE ever re-flagging that lemma as a gap. `grounding_acquisition_loop.py`
generalizes this one level: FLAG (credit scan) -> LIBRARY (per-item trace store, kept SEPARATE per
Trueswell propose-verify, never averaged at intake) -> CONSOLIDATE ("sleep" pass, schema-consistency
gated, not just vote-margin) -> GUARD (escalate-don't-force-commit, rejects 3/3 adversarial probes in
its own self-test) -> BANK. **This pathway is per-ITEM.** It fades a specific gap (that exact lemma)
permanently after enough confirmatory exposures. It does **not** generalize to a DIFFERENT, unseen
lemma that shares only a construction-level resemblance to an already-banked one -- every new item
still needs its own crutch consult(s) before Level 1 can bank it.

**What is NOT YET BUILT (Level 2 -- the "regular/rule" pathway, the actual crux of this drill):**
the piece that lets a handful of crutch fills cover a whole CLASS of unseen gaps is
`hdlab/learner`'s MDL model-selection engine (`registry.learn`/`apply`, auto-selecting across
`estimation` / `ruleind` / `proginduction` / `gam` plugins by two-part-code compression,
`per_cluster_gate`: promote a hypothesis only if it compresses PAST the null/memorize code,
`mdl_select`: pick the best-compressing eligible hypothesis). This is not a new engine to build --
it is the SAME organ `frame_induction.py` already uses for a structurally-identical problem (induce
a construction -> role mapping that transfers to an unseen VERB via construction overlap, the verb
lemma NEVER a feature). `frame_induction`'s measured result is the existence proof this pattern can
work: subj-axis held-out accuracy 0.833 (`data/exp_frame_induction_oov_psych_real_v1/metrics.json`,
MIDDLE_BAND but real, non-hand-authored generalization to a genuinely unseen lemma via construction
cues alone) -- but it has never been fed crutch-typed labels; its hypothesis space is a hand-declared
`{AGENT, EXPERIENCER}` role vocabulary, not an ATOMIC/ConceptNet relation-type vocabulary.

**The concrete abstraction step (specifics -> schema), stated precisely:**

1. Every time the crutch fires (Section 2), emit an EPISODE: `{feats: construction_cue_list(gap_context),
   gold_class: relation_type}` -- exactly `frame_induction.build_episode`'s shape, with
   `relation_type` (e.g. `at:xEffect`, `cn:Causes`, `at:oWant`) standing in for `gold_subj_role`.
2. Accumulate episodes per relation-type FAMILY (not globally -- `schema_exemplar_bayes.py`'s
   k-means schema-clustering is the right ROUTER here, misidentified as a "schema-induction" organ
   in casual reading of its name: it is a retrieval-locality COMPRESSOR/router over already-stored
   facts, not a generalizer over unseen inputs -- flagged explicitly so this design does not
   mis-cite it as doing Level 2's job).
3. Periodically (the B10/CLS consolidation pass, offline, "sleep"-timed per the same
   Dumay-Gaskell/van-Kesteren schema-consistency literature `grounding_acquisition_loop` already
   cites), call `hdlab.learner.registry.learn(episodes, feat_fn, hypothesis_space_spec)` per
   relation-type family. `mdl_select` promotes a `proginduction` or `ruleind` hypothesis ONLY if it
   compresses past the null/per-item-memorize code (`per_cluster_gate`) -- this IS the "the crutch
   fires less as the substrate accumulates evidence a rule holds" criterion, made formal and
   glass-box (not a vibes-based "seems general enough" heuristic): a family with too little data, or
   genuinely idiosyncratic (no compressible construction regularity), correctly STAYS episodic
   (`KEEP_EPISODIC`) -- an honest, measurable, non-forced degrade, not a silent failure.
4. A promoted hypothesis is consulted BEFORE any future crutch call for that relation-type family: a
   NEW, never-crutch-consulted gap whose construction cues satisfy the induced rule/program is typed
   WITHOUT a crutch consult at all. This is the mechanism that makes a whole CLASS of future gaps
   fade, not just the one item Level 1 already handles -- the qualitative difference the Director's
   "generalizes into schemas that cover unseen gaps" framing is asking for.

**Brain-motivated framing, not just an engineering convenience** (own docstring already claims this,
worth restating precisely): `hdlab/learner`'s own header analogizes the design to "hippocampal
replay feeding a cortical model-selection process over domain-specific priors" -- i.e. Level 1
(item-by-item banking, gated by an abstain-band vote margin) IS the fast hippocampal leg; Level 2
(periodic MDL re-fit that promotes a compact rule) IS the slow cortical-consolidation leg of
Complementary Learning Systems (McClelland-McNaughton-O'Reilly 1995), already cited elsewhere in
this program (barrier-map B10). This drill's contribution is naming that the SAME two-leg CLS
structure, already built for LEXICAL acquisition, is the right and ALREADY-OWNED shape for CRUTCH-
sourced world-knowledge acquisition too -- a wiring/composition claim, not a new mechanism claim.

## 3b. RECONCILIATION WITH A CONCURRENT SAME-DAY DRILL (found at status-log check, after Section 3
was drafted -- corrects two claims rather than leaving them stale)

`notes/research_crutch_fade_loop_owned_organ_wiring_2026-08-10.md` ("DRILL 3," internal owned-organ
code audit, zero external citations, live self-test re-runs) landed in the status log while this
note was in progress and answers a materially overlapping question from a different angle (pure
code-wiring audit vs this note's source-comparison + generalization-design + fade-curve angle). Two
corrections to Section 3 above, credited honestly rather than silently reconciled:

1. **Level 1 is not simply "already built" -- it is built but MISWIRED to the weaker of two
   consolidation lineages.** DRILL 3 found `wordnet_polarity_propagation.pseudo_counts_from_dictionary`
   (a dictionary crutch, structurally the same INJECT-ONCE pattern this note's Level 1 describes)
   feeds `consequence_learning_loop.learn_corpus`'s OWN vote-margin-only `consolidate()`
   ("Lineage A"), never `grounding_acquisition_loop.consolidation_pass` ("Lineage B"), which adds
   the mandatory schema-consistency split-half guard against Warren et al. 2014's false-consolidation
   failure mode. Lineage A alone (no schema-consistency second gate) is exactly the false-memory-
   vulnerable configuration Warren's finding warns against. **This note's Level 1 design (Section 3)
   should be read as targeting Lineage B specifically**, not the currently-wired Lineage A path --
   DRILL 3's Section 3 connector #3 (extend `Library.flag`/add `flag_prior`, feed the vote-
   margin/patience accounting but EXCLUDE the crutch from `schema_consistency_split_half`'s own
   coherence computation) is the correct, concrete fix and this note adopts it rather than
   re-deriving an equivalent.
2. **A second, already-built-and-validated Level-2 mechanism exists that this note's own code read
   missed**: `hdlab/script_grain_acquisition_loop.py::ScriptLibrary.match_or_spawn` clusters raw
   episode vectors into recurring event-TYPES via CA3/DG attractor keying
   (`hdlab.cleanup_family.iterative_attractor`) -- an EXEMPLAR/ATTRACTOR-similarity route to schema
   formation at the event/script grain, complementary to (not a substitute for) this note's Section
   3 proposal of an explicit MDL feature->label rule over construction cues
   (`hdlab.learner`/`frame_induction`'s pattern). DRILL 3 re-ran its self-test live this session:
   PASS (matched-pair cosine 0.361 vs wrong-pair -0.013, scramble control collapses to 0.003). This
   means Level 2's MECHANISM-EXISTENCE risk is lower than this note's Section 4 P-estimate assumed
   for the attractor-clustering route specifically -- but the crutch-CONNECTOR into it (feeding
   CSKG-typed fills as episodes `ScriptLibrary` clusters) is, per DRILL 3's own Section 3 connector
   #4, a genuine "does not exist in either direction today" gap, same as this note's own
   not-yet-built claim for the MDL-rule route. Net effect: TWO independent, complementary Level-2
   generalization mechanisms exist and are validated in isolation; NEITHER has ever been fed
   crutch-sourced (ATOMIC/ConceptNet/CSKG) content. The Section 6 cheap decisive test below should
   be read as applicable to BOTH routes, run in parallel where cheap to do so (they consume the same
   episode payload from Section 2's construction-cue addition).
3. Independent convergent confirmation, not new: both drills independently flagged
   `hdlab/schema_exemplar_bayes.py` as a mislabeled retrieval-compression router, not a schema-
   induction organ. DRILL 3 additionally flags the registry's separate "schema_abstraction" row
   (`exp_read_grow_schema_abstraction_predictive_precision_v2.py`) as a THIRD mislabel -- UD-
   dependency syntactic-fragment abstraction (dropping function-word children from a construction
   shape), a real but SYNTAX-grain mechanism, not the semantic/event-grain schema induction either
   drill's design needs. Filed here so a future session does not reach for either mislabeled organ.

This does not change Section 1 (crutch source), Section 2 (output form), or Section 4/5 (fade-curve,
brain grounding) below -- DRILL 3 did not address the external-KB comparison, the fade-curve
question, or the psycholinguistic/developmental grounding, which remain this note's distinct
contribution. It sharpens Section 3's "not yet built" claim into a more precise, more actionable
form (miswired + unconnected, not absent) and modestly UPGRADES this note's confidence that a
Level-2 mechanism will exist and work in isolation (P revised in Section 4/HEADLINE accordingly),
while leaving the crutch-specific connector work -- and therefore the core fade-curve claim -- as
genuinely untested by either drill.

**A third same-day drill, `notes/research_brain_scaffolding_that_fades_2026-08-10.md` ("DRILL 2,"
a solo brain-fidelity element audit specifically of THE FADE), lands a correction sharp enough that
this note's Section 4 below has been revised to incorporate it rather than stand alongside it
uncorrected.** DRILL 2's headline finding: **the fade is not merely unbuilt, it is structurally
IMPOSSIBLE in the current wiring.** `register_acquired_outcome` (the BANK step both this note's
Level 1 and DRILL 3's Lineage B target) writes into `verb_lexical_similarity.
ACQUIRED_OUTCOME_VERB_FEATURES`, a plain in-memory Python dict -- a permanent SEPARATE side-table,
never merged into the base similarity scorer/codebook that produces lookup-free "native" predictions
for already-known words. Structurally this is an annotation ("this fact has been looked up"), not a
migration ("this fact is now represented the same way old facts are") -- and the brain's fade is
literally the latter (Logan 1988 Instance Theory; Fitts & Posner 1967 cognitive->associative->
autonomous staged transfer). DRILL 2 independently converges on DRILL 3's own flagged fix
(`hdlab/hd_fact_store.py`, source-trust-vetted, provenance+trust NATIVELY bound into the fact
vector) as the concrete destination -- which is not a coincidence relative to THIS note's own
Section 2 design (`bind(SOURCE,..)+bind(TRUST,..)` already specified there): a "crutch-sourced fact
starts low-trust, promotes toward full-trust as consistent corroborating real-corpus evidence
accumulates" design turns Section 2's provenance binding into the literal fade mechanism DRILL 2
finds is currently missing, rather than a mere audit-trail decoration. Section 4 below is revised to
carry DRILL 2's sharper, more quantitative fade-shape citations (power law of practice; instance
theory; consistent-mapping automaticity) in place of this note's own weaker original framing, and to
name the flat-dict-vs-hd_fact_store distinction as a precondition for ANY fade claim, Level 1 or
Level 2, to be structurally true rather than aspirational.

## 4. HONEST FADE-CURVE ASSESSMENT

**Precondition, per Section 3b/DRILL 2, stated first because it gates everything below: a fade
curve can only be TRUE, not aspirational, if BANK output migrates into the same natively-read
structure used for old knowledge (`hd_fact_store`'s trust-weighted fact vectors, per Section 2's
own SOURCE/TRUST design), not a permanent side-table dict. With that precondition met, the shape
question below is answerable; without it, "the crutch fades" is a label, not a measured property.**

**The shape, once the precondition is met: STAGED and STEEP-THEN-TAIL, never fully flat to zero.
Not a breakthrough that eliminates the crutch; a real, useful, brain-consistent reduction.**

The sharpest, most quantitative calibration anchor for this claim, per DRILL 2's live literature
scan (credited, not re-derived here): **Fitts & Posner 1967's three-stage skill-acquisition model**
(cognitive -> associative -> autonomous) names the STAGES a fade curve should pass through -- this
project's current design has only two (`PENDING` -> `GROUNDED_*`, a binary bit, no associative
middle stage where retrieval is consolidating but not yet automatic) -- and **Newell & Rosenbloom
1981's power law of practice** (T = T1 * N^-b, replicated across an enormous range of skills; a
live exponential-decay counter-account, Heathcote/Brown/Mewhort 2000, contests the exact functional
FORM but not the qualitative shape) gives the precise mathematical family for "steep-then-tail":
large gains from the first few resolutions of a given gap, then rapidly diminishing marginal
reduction in crutch-reliance per additional exposure, approaching but never fully reaching zero.
This supersedes and sharpens this note's own initial framing (a looser Heaps'-law/Zipf-decay
analogy, retained below only as a second, independent, corpus-linguistics-side confirmation of the
same qualitative shape, not the primary citation). **Two concrete, already-computed predictors of
fade SPEED**, per DRILL 2: Logan 1988's Instance Theory (exposure/trace COUNT predicts automaticity)
and Schneider & Shiffrin 1977's Consistent-Mapping finding (automaticity develops ONLY when the
stimulus-outcome mapping is consistent across exposures -- an inconsistent/noisy item never
automatizes regardless of count). Both quantities (`len(traces)`, `_vote_margin`) already exist in
`grounding_acquisition_loop`/`consequence_learning_loop`'s code today, computed for gating/labeling
but never wired to a continuous fade/trust-promotion output -- which is exactly the missing
connector Section 3's design (and Section 2's TRUST-binding) needs to close.

A second, independent calibration anchor for the same qualitative shape, found this cycle (external,
generic search, no prior KB hit on this specific literature, and not carried by DRILL 2 which drew
its citations from the skill-acquisition/automaticity literature rather than the psycholinguistic
morphology literature): **Pinker's dual-mechanism ("words and rules") model of English past-tense
morphology** (Pinker & Prince; Pinker 1999 *Words and Rules*). Regular
inflection is computed by ONE general default RULE that applies productively to any novel form
(a "wug"-test generalizes with zero prior exposure to that exact item); irregular forms are
individually stored in the lexicon and never generalize past their own trained analogical
neighborhood. The decisive, quantitatively sharp finding for THIS drill's question: **there is a
massive, robust correlation between token FREQUENCY and IRREGULARITY -- all ten of the most frequent
English verbs are irregular, all ten of the least frequent are regular.** High-frequency items
survive as memorized exceptions (repetition props them up against the regularizing pressure of the
rule); low-frequency/novel items default to the rule. This is a precise, independently-derived
analogue of Section 3's two-level design: Level 1 (per-item banking) is exactly the "irregular"
pathway -- it will keep firing forever for genuinely idiosyncratic, individually-frequent-enough
items (specific idioms, culturally-bound scripts, a particular character's particular quirk).
Level 2 (MDL-promoted construction rule) is exactly the "regular" pathway -- it closes an entire
class in a bounded number of supporting exposures and then generalizes for free, INCLUDING to items
the crutch has never seen.

Three more anchors, all already ON DISK (no fresh number invented for this note):

- **`frame_induction`'s own measured split (0.833 vs 0.455 by axis)** is direct, disk-verified
  evidence that construction-cue generalization is NOT uniform across knowledge types -- it works
  well for one syntactic axis (subject-experiencer marking, a genuinely regular/rule-governed
  phenomenon) and near-chance for another (object-experiencer, a more lexically-idiosyncratic
  phenomenon in English psych-verbs). Applied to crutch content: expect Level 2 to close FAST for
  physical/causal/force-dynamic regularities (Talmy's ~6-10 privileged relation types, already
  identified as a bake-in candidate in `research_innate_scaffolding_core_knowledge_kernel_2026-07-09.md`
  -- e.g. "an obstacle blocks a goal" is a productive construction-level schema) and close SLOWLY or
  NOT AT ALL for socially/culturally-specific relation instances (a specific idiom's specific
  meaning, a specific character-typical reaction) that have no shared construction signature across
  instances.
- **DesireDB's own residual sizing** (barrier-map / DesireDB-arc prior art): roughly 45% of the hard
  residual on that real corpus was data-noise, ~30% BESPOKE LONG-TAIL (genuinely idiosyncratic,
  unlikely to compress under any rule), leaving the tractable/rule-governed slice as a real but
  MINORITY share of the hardest cases. This is an independent, real-corpus-measured floor estimate
  for the long-tail fraction Level 2 will never close -- consistent with, not contradicted by,
  Pinker's frequency-irregularity account.
- **The one existing empirical growth curve is content-hollow** (barrier-map B10, disclosed
  honestly, not swept): `grounding_acquisition_loop`'s measured 0->40-over-5-passes curve is
  function/light-word dominated, not yet demonstrated on open-content world-knowledge specifically.
  This means Section 3's design is CORRECTLY MOTIVATED and mechanism-plausible but **UNVALIDATED on
  the actual content axis this drill cares about** -- the honest state is "designed, not proven,"
  and Section 6's cheap decisive test exists specifically to close that gap before any larger
  build commitment.

**Breakthrough or slog -- the honest answer is BOTH, split by content type, not a single verdict.**
For the physical/causal/goal-blocking regularities that recur across many distinct narrative
surface forms (a real but bounded set, Talmy/Mandler-sized, maybe low hundreds of construction
FAMILIES, not thousands), Level 2 is a genuine, brain-consistent, cheap-after-a-bounded-number-of-
exposures win -- this is where "the crutch fades" is a true, measurable, product-relevant claim.
For the idiosyncratic long tail (proper-noun-specific facts, culturally-bound idioms, individual
authorial style), Level 1's per-item banking is the correct and sufficient mechanism, but it is a
SLOG in the precise sense that it never stops needing new crutch consults as genuinely novel
long-tail items keep appearing (a Heaps'-law-shaped, sub-linear-but-nonzero-forever vocabulary-
growth curve is the right mental model, not an asymptote to zero). **This is not a design flaw --
it is the same shape human vocabulary/idiom acquisition has (adults keep learning new idioms their
whole life via slow, low-frequency exposure-based routes); a fully-flat, zero-forever crutch would
itself be an UNFAITHFUL claim.**

## 5. Brain-foundational grounding

- **Fast mapping (Carey & Bartlett 1978; Carey 2011, "Beyond Fast Mapping," *Lang. Learning &
  Development* 6(3))**: one exposure creates a WEAK, GRADED, placeholder entry, not a firm binding
  -- directly licenses Level 1's design (a single crutch consult writes a PENDING/low-confidence
  trace, `MIN_CONFIRM`-gated before consolidation, never a one-shot firm commit). Already the exact
  citation base the 2026-08-06 acquisition-loop spec used for the sibling lexical-acquisition
  design; this note extends the SAME citation to crutch-sourced world-knowledge content, not a
  fresh literature claim.
- **Schema abstraction from few examples (Gick & Holyoak 1983, "Schema Induction and Analogical
  Transfer," *Cognitive Psychology* 15)**: examining as few as TWO analogs induces a transferable
  schema that preserves shared relational structure while discarding surface detail -- the classic
  developmental/cognitive result that a SMALL number of crutch-sourced instances (not thousands) is
  plausibly sufficient for Level 2 to detect a compressible construction regularity, consistent with
  `consequence_learning_loop`'s own `MIN_CONFIRM=3`/`grounding_acquisition_loop`'s
  `MIN_CONFIRM=4`-per-half design constants (already independently in the right ballpark, not
  re-tuned by this note).
- **Bayesian program induction (Lake, Salakhutdinov, Tenenbaum 2015, "Human-level concept learning
  through probabilistic program induction," *Science* 350(6266))**: concepts represented as short
  programs, selected by a Bayesian/MDL criterion over a small number of examples, is the DIRECT
  computational ancestor of `hdlab/learner`'s `proginduction_plugin` (bounded enumerative DSL search
  + two-part-code MDL selection) -- this is not an engineering-convenience choice, it is the
  standard computational account of exactly the schema-abstraction-from-few-examples phenomenon
  this drill is asking the substrate to reproduce.
- **Xu & Tenenbaum 2007 size-principle / suspicious-coincidence generalization** (already in this
  project's KB via the 07-09 innate-scaffolding note): ONE example licenses a BROAD, prior-dominated
  generalization; several confirming examples of the SAME narrow category sharpen it to a NARROW
  one. This is the correct brain-consistent caution against Level 2 over-generalizing from a single
  crutch fill -- `per_cluster_gate`'s must-beat-the-null-code requirement is the substrate's formal
  analogue of "suspicious coincidence" (a rule is only trusted once enough evidence makes the
  narrow/general choice actually likely, not merely possible).
- **How a child generalizes from a few tellings**: the usage-based construction-grammar account
  (Tomasello 2003, cited in the 07-09 note) of "generalize, then retreat from overgeneralization" is
  the correct developmental analogue for Level 2's own necessary FAILURE MODE -- an MDL-promoted
  rule that later over-fires on a construction it should not cover is expected to be caught and
  narrowed by the SAME re-fit mechanism on the next consolidation pass (more episodes -> the
  compression comparison re-runs -> an over-general rule that starts costing more data-bits than a
  narrower one loses `mdl_select`), not a static one-shot commitment.
- **Complementary Learning Systems as the two-level split itself** (McClelland-McNaughton-O'Reilly
  1995; already the barrier-map's B10 citation): fast hippocampal one-shot capture (Level 1) feeding
  slow, schema-gated cortical consolidation (Level 2) is not an analogy of convenience -- it is the
  SAME two-timescale architecture `hdlab/learner`'s own docstring already claims, now given a
  concrete crutch-specific payload (Section 3) instead of a generic claim.

---

## Cheap decisive test

Build the Section 3 pipeline at SMALL scale on the already-in-use real corpus (DesireDB or
MCScript2.0, whichever has an open extraction pass this cycle) with the already-landed CSKG spine as
the crutch. For a sample of B1/B8-flagged gaps (Section 3 triggers): (a) LEVEL-1-ONLY arm -- consult
CSKG, bank per-item via `consequence_learning_loop.learn_corpus(dictionary_priors=...)`, measure the
crutch-consult RATE over N corpus passes. (b) LEVEL-1+LEVEL-2 arm -- additionally extract
construction-cue features per crutch-fill (Section 2's addition), periodically MDL-fit via
`hdlab.learner` per relation-type family, and test whether the induced hypothesis correctly predicts
the CSKG relation-type for a HELD-OUT lemma/event the crutch has never been consulted on. Compare the
two arms' crutch-consult-rate curves over passes, plus a construction-feature-SCRAMBLE negative
control (the project's standing pairscramble-must-collapse discipline) to confirm any Level-2 win
uses real construction structure, not majority-class guessing.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**HARD-PASS** (both required):
- Level-1+Level-2 arm's crutch-consult rate at pass 5 is **>= 15 percentage points lower** than
  Level-1-only's rate for the SAME relation-type family (construction-level generalization
  measurably reduces crutch dependency beyond item-repeat decay alone).
- Held-out-construction relation-type accuracy (Level 2's induced hypothesis, on lemmas/events never
  crutch-consulted) beats a majority-class baseline by **>= 15 percentage points**, AND a
  construction-feature scramble control collapses that margin to within 3pp of the baseline.

**HARD-FAIL** (either triggers, subject to a mandatory pre-check: confirm the crutch trigger and the
episode-emission path actually fire on >= 50% of gap events in the eval slice first -- a flat result
from a non-firing harness is a harness bug, not a mechanism verdict, per the standing "flat result =
broken experiment" discipline):
- Level-1+Level-2 consult-rate is statistically indistinguishable (within 5pp) from Level-1-only at
  pass 5.
- Held-out-construction accuracy does not beat the majority-class baseline by more than 5pp, OR the
  scramble control does not collapse an observed margin.

A HARD-FAIL here is a genuinely informative negative, not a program-ending one: it would mean
construction-cue features carry no usable signal for CRUTCH-TYPED relation labels on this corpus
specifically (as opposed to frame_induction's hand-labeled AGENT/EXPERIENCER axis, where the same
mechanism partially works) -- Level 1 alone remains valid, useful, and already-built; only the
"whole classes of gaps fade" claim would be falsified, leaving a slower, Pinker-irregular-only fade
curve as the honest fallback.

## Cross-thread synthesis

Extends `notes/research_prior_art_narrative_schema_learning_2026-08-09.md` Section 5's confirmed
literature gap (no prior work does incremental/online schema growth from a streaming corpus) by
supplying the concrete mechanism design that gap calls for, built entirely from organs that note's
OWN Section 10 recommended (`hdlab.learner`'s `hypothesis_space_spec` contract, item 3) plus organs
built the following day (`consequence_learning_loop`, `grounding_acquisition_loop`) that note could
not yet cite. Extends `notes/research_content_causal_associative_knowledge_store_2026-08-09.md`'s
already-designed output-form schema (Section 2 here, credited not reinvented) with the
construction-cue companion payload Level 2 needs. Answers the open half of
`notes/direction_b_grounded_knowledge_build_plan_2026-08-09.md`'s M2 milestone ("LEARN the
idiom/concept -> attribute-effect mapping from exposure... held-out UNSEEN idioms generalize via
grounded-feature overlap") with a concrete organ-level design instead of a milestone description.
Calibrates against `notes/research_comprehension_barrier_map_brain_foundational_2026-08-10.md`'s
disclosed B10 finding (content-hollow growth curve) rather than ignoring it -- this note's P_deflated
is set where it is BECAUSE of that disclosed negative, not despite it. Reconciled (Section 3b) with
`notes/research_crutch_fade_loop_owned_organ_wiring_2026-08-10.md` ("DRILL 3," a concurrent same-day
internal owned-organ wiring audit that this note's own KB-check predates): that drill independently
confirms this note's Section 1-2 framing is compatible with the on-disk store/provenance design, adds
a second validated Level-2 mechanism (`script_grain_acquisition_loop`'s CA3/DG attractor script
clustering) this note's own code read missed, and supplies the exact small connector (route the
WordNet/CSKG dictionary-style crutch into `grounding_acquisition_loop`'s schema-consistency-guarded
consolidator, not the older vote-margin-only one) that Section 3's Level-1 design should target.
Also reconciled with `notes/research_brain_scaffolding_that_fades_2026-08-10.md` ("DRILL 2," a
concurrent same-day solo brain-fidelity audit of THE FADE specifically): that drill's headline
finding -- BANK writes into a permanent side-table dict, not a migrating trust-weighted structure,
so the fade is structurally impossible in the CURRENT wiring regardless of Level-1/Level-2 mechanism
quality -- is incorporated as Section 4's precondition, and its sharper skill-acquisition-literature
citations (Fitts & Posner 3-stage transfer; Newell & Rosenbloom power law of practice; Logan Instance
Theory; Schneider & Shiffrin consistent-mapping) supersede this note's own initial, weaker
fade-shape framing. DRILL 2 and DRILL 3 independently converge on the same fix
(`hdlab/hd_fact_store.py` as the BANK destination) from two different audit methods
(brain-fidelity-first vs registry/wiring-first) without either having read the other at drafting
time -- this note's Section 2 (SOURCE/TRUST binding, drafted before either was read) turns out to
already specify the representational form that fix needs, which this note treats as a convergent
confirmation across three independent same-day analyses, not a coincidence to gloss over.

## Substrate-product implications

If Section 3's Level 2 clears its cheap decisive test, the product claim becomes concrete and
auditable: a user can ask "why did the substrate infer that" and get either a crutch citation
(SOURCE=ATOMIC, this specific edge) for a still-idiosyncratic item, or a RULE citation (this
construction pattern, learned from N prior crutch-confirmed instances, compression ratio X) for a
generalized item -- and critically, the second case shows the substrate's dependency on any external
KB is SHRINKING and NAMEABLE over time, which is a defensible, literally-true "learns and needs the
crutch less" claim rather than a permanent external-lookup dependency dressed up as learning. If
Level 2 HARD-FAILs, the fallback (Level 1 only, already built) is still shippable and honest: a
glass-box, provenance-tagged, per-item-banked grounding layer that never claims more generalization
than it has earned -- which is itself a real product improvement over today's hand-curated
Tier-1/Tier-2 seed lists (the exact gap the 2026-08-06 acquisition-loop drill named), independent of
whether Level 2 pans out.

## Citations (verified count)

**Inherited, credited, re-verified live this cycle where flagged** (from the two 2026-08-09 prior-art
notes, not re-derived): Sap et al. 2019 AAAI (ATOMIC); Hwang et al. 2021 AAAI (ATOMIC-2020); Speer,
Chin, Havasi 2017 AAAI (ConceptNet 5.5); Mostafazadeh et al. 2020 EMNLP (GLUCOSE); Zhang, Liu, Pan,
Song, Leung 2020 WWW (ASER); Li, Ding, Liu 2020 IJCAI (CausalBank); Bosselut et al. 2019 ACL (COMET,
reference-only); McClelland, McNaughton, O'Reilly 1995 *Psych. Review* 102(3) (CLS); Talmy 1988
*Cognitive Science* 12 (force-dynamics privileged basis); Tomasello 2003 *Constructing a Language*
(usage-based generalize-then-retreat); Xu & Tenenbaum 2007 *Psych. Review* 114(2) (size-principle);
Trueswell, Medina, Hafri, Gleitman 2013 *Cog. Psych.* 66(1) (propose-but-verify, cited by
`grounding_acquisition_loop`'s own docstring); Dumay & Gaskell 2007; van Kesteren et al. 2012 (SLIMM
schema-gate); Warren et al. 2014 (false-consolidation double-edge).

**Credited from concurrent same-day drills** (Section 3b/4, not re-derived): Fitts & Posner 1967
*Human Performance* (3-stage skill acquisition); Newell & Rosenbloom 1981 (power law of practice);
Heathcote, Brown & Mewhort 2000 *Psychonomic Bulletin & Review* 7 (exponential-law counter-account);
Logan 1988 *Psychol Review* 95(4) (Instance Theory of Automaticity); Schneider & Shiffrin 1977
*Psychol Review* 84(1) (consistent-mapping automaticity) -- all via
`notes/research_brain_scaffolding_that_fades_2026-08-10.md`, live-verified there this session, not
independently re-verified here.

**Newly verified live this cycle** (3 generic WebSearches, sources listed): Pinker's dual-mechanism
/ words-and-rules model of regular-rule vs irregular-lookup morphology and the token-frequency /
irregularity correlation -- [Words and Rules (Wikipedia)](https://en.wikipedia.org/wiki/Words_and_Rules),
[Words and Rules -- Steven Pinker](https://stevenpinker.com/publications/words-and-rules),
[Dual-Mechanism Morphology overview](https://www.researchgate.net/publication/242411920_Dual-Mechanism_Morphology);
Carey & Bartlett 1978 / Carey 2011 fast mapping (already in this project's KB via the 2026-08-06
note, re-confirmed not re-searched this cycle); Gick & Holyoak 1983 schema induction from analog
pairs and Lake, Salakhutdinov, Tenenbaum 2015 *Science* 350(6266) Bayesian program induction --
[Human-level concept learning through probabilistic program induction](https://www.science.org/doi/10.1126/science.aab3050),
schema-induction summary via
[Abstraction and Analogy-Making in Artificial Intelligence survey](https://arxiv.org/pdf/2102.10717);
ATOMIC-2020 CC-BY license + GLUCOSE scale confirmation via
[allenai/comet-atomic-2020 GitHub](https://github.com/allenai/comet-atomic-2020) and the
[COMET-ATOMIC 2020 AAAI paper](https://cdn.aaai.org/ojs/16792/16792-13-20286-1-2-20210518.pdf).

Total distinct citations this note relies on: ~18, of which 3 (Pinker dual-mechanism, Gick & Holyoak,
Lake/Salakhutdinov/Tenenbaum) are genuinely new to this drill's KB and live-verified this cycle; the
remainder are credited re-use of the two 2026-08-09 prior-art notes' own live-verified citation
bases (not re-derived from memory). Per [[feedback-lit-scan-calibration-penalty]]: this note's
overall P is capped at the novel-synthesis ceiling (0.50) and reported at 0.40 (see HEADLINE),
reflecting that Level 1 is a near-certain wiring exercise over proven organs but Level 2 (the actual
crux) has exactly one split-result on-disk precedent and zero literature precedent for the specific
combination (crutch-sourced typed labels + construction-cue MDL generalization), per the 08-09
survey's own confirmed-negative search.
