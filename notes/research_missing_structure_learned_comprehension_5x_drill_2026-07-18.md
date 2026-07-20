# 5x drill: is there a MISSING capability/structure for LEARNED comprehension (not hand-rule-fed)?

**Date:** 2026-07-18. **Filed by:** research (3 parallel Sonnet lit-scans + Sonnet/director synthesis).
**Trigger:** direct 5-angle drill request diagnosing why comprehension/parsing stays hand-ruled
(extraction wall ~40% precision on complex prose; ~0.19 precision reading noisy real text; reader
gains this cycle are all hand-built, not learned).

**Method note (2x/depth discipline):** this arc already has FIVE directly-adjacent notes from the
last 48h — `research_wm_barrier_glassbox_parsing_2026-07-17.md`,
`research_hardrule_vs_predictive_parsing_barrier_2026-07-17.md`,
`research_how_brain_does_broad_construction_parsing_synthesis_2026-07-17.md`,
`research_drill_relation_comprehension_reader_thematic_roles_glassbox_2026-07-18.md`,
`research_learned_parser_clause_seg_np_head_blueprint_2026-07-18.md`. Angles 1/2 (acquisition,
neuroscience) and parts of angle 4 (ML history) had NOT been drilled yet in this arc — those got
fresh lit-scans. Angle 3 (hierarchy/recursion in VSA specifically) also had NOT been drilled — fresh
lit-scan. This note's job is to fill those two real gaps and then INTEGRATE with the five prior notes
into one ranked verdict, not to re-run ground already covered (WM-as-structural-memory, multi-cue role
assignment, DOP/construction-grammar convergence are already landed findings, cited not re-derived).

Lit-scan calibration penalty applied throughout (deflate P 0.15-0.25; novel-synthesis P capped 0.50).

---

## HEADLINE

**The missing piece is NOT a single absent capability — it is two separable things, one nearly free
and already-owned, one genuinely big and only partially built, and the literature converges hard on
both from acquisition, neuroscience, and ML-history angles independently.**

1. **(Cheap, near-zero-cost, mostly UNUSED not unbuilt) Recursive/nested composition.** The formal
   literature draws a clean line: flat finite-state models provably cannot represent *unbounded*
   recursion (Chomsky hierarchy), but sequential models WITH sufficient internal memory structure can
   represent *bounded*-depth hierarchy just fine (Hewitt et al. 2020 EMNLP — RNNs generate bounded
   Dyck-(k,m) languages with O(m log k) units, no explicit tree needed). Real prose overwhelmingly
   exercises bounded embedding (2-3 levels, rare beyond that) — this matches the arc's own WM-barrier
   finding (`research_wm_barrier_glassbox_parsing_2026-07-17.md` Prediction 4: an unbounded stack
   should show no degradation on real-prose nesting because deep nesting barely occurs). Our
   bind/unbind/resonator machinery can represent bounded recursion EXACTLY today (a filler can already
   be a previously-bound sub-structure — that's what nested/nested binding calls already do
   mathematically), but the current hand-rule reader never calls it that way: it emits FLAT triples,
   never a role whose filler is itself a bound proposition. **This is an underuse of an existing
   primitive, not a missing one** — cheapest lever in this note.
2. **(Big, genuinely under-built) A LEARNED, grounding/comprehension-scored construction-induction
   mechanism** — i.e., exactly the "grow a glass-box construction inventory from reading" direction
   already identified in `research_how_brain_does_broad_construction_parsing_synthesis_2026-07-17.md`
   and the disambiguation-scorer direction in
   `research_hardrule_vs_predictive_parsing_barrier_2026-07-17.md`. THIS drill's acquisition and ML-history
   lit-scans independently reinforce it from two new angles: (a) Tomasello's usage-based item-to-schema
   generalization (children build ONE construction per verb first, then abstract via analogy over many
   exemplars — a LEARNING PROCEDURE, not a rule table) is the biological existence proof that
   comprehension-grammar is GROWN not installed; (b) the ML-history angle shows the historical
   hand-rule -> statistical transition was driven by BOTH more data AND a genuine structural-prior
   change (lexicalization, discriminative feature weighting, recursive composition) — not coverage
   alone (Collins's lexicalized-vs-unlexicalized ablation isolates this) — confirming that "just add
   more hand rules" is not what closed the historical gap even in the well-resourced supervised regime.

**The sharpest new finding this drill adds (not previously in the arc): the SUPERVISED-VS-GROUNDED
FAIRNESS QUESTION has a stark, sobering, literature-documented answer.** Penn-Treebank-style supervised
parsing (85-92% F1) requires gold trees a human already disambiguated — categorically closer to
distillation-from-an-oracle than to acquisition. The fair analog for a system with no rule-writer and
no gold trees is UNSUPERVISED/grounded grammar induction, and that regime's own honest ceiling is
**~40-70% directed accuracy, on SHORT sentences (<=10 words), and even that typically leaks gold POS
tags as scaffolding** (Klein & Manning 2004 DMV; unsupervised POS induction alone is "significantly
worse"). Grounded (non-linguistic-context-paired) structure learning specifically is thin in the
literature — mature grounded work is about word-referent mapping (cross-situational learning), not
syntax induction; there is no mature "grounded-syntax-from-near-nothing" system to point to as an
existence proof beyond the lexical-grounding case we already have. **This means: a "grow it yourself"
learned construction-inventory should NOT be expected to approach supervised-parser accuracy on hard
prose — the honest ceiling is real-and-lower, and is REGISTER-dependent** (already-flagged elsewhere
in the arc that grade-1 SVO plausibly reaches 0.80-0.95 per
`research_drill_relation_comprehension_reader_thematic_roles_glassbox_2026-07-18.md`, while complex
prose sits in the unsupervised-induction ballpark, not the supervised one).

---

## (1) Human language acquisition — mechanism, citation, structure implied

- **Statistical/distributional learning is real and does load-bearing work with zero rules.**
  Saffran, Aslin & Newport (1996, *Science*) — 8-month-olds segment word-like units from a continuous
  synthetic speech stream using only syllable transitional probabilities, ~2 minutes exposure, no
  lexicon/stress/rules supplied. Established, heavily replicated (Aslin, Saffran & Newport 1998).
  **Structure implied: a co-occurrence-statistics accumulator over a sliding window is sufficient for
  the SEGMENTATION sub-problem** — this is a capability our substrate already has analogs for
  (frequency counting, PPMI-style co-occurrence) but is not currently wired to word/construction
  *boundary-finding* specifically.
- **Semantic bootstrapping (Pinker 1984, established as an influential hypothesis)**: children map
  pre-linguistic semantic categories (agent/patient/event) onto syntactic categories using KNOWN word
  meanings as scaffolding, before grammar exists. **Structure implied: grounding-first is a load-bearing
  precondition for syntax acquisition, not an optional nicety** — directly validates the substrate's own
  sequencing (grounded words already done up-front, per the relation-comprehension note's strength
  column) as the biologically-correct order of operations, not just a convenient one.
- **Syntactic bootstrapping (Gleitman 1990) is complementary, not competing** — 2024 review reframes
  both as JOINT/interactive inference, not one-directional (single-study/emerging framing). No separate
  named theory exists in the literature for "known meaning guides parsing AND parsing grows knowledge"
  beyond this joint-inference framing plus usage-based construction grammar generally — flag honestly:
  we would be naming/operationalizing this loop ourselves, not looking one up.
- **Usage-based/Construction Grammar (Tomasello 2000/2003, established, dominant alternative to
  nativist parameter-setting)**: verb-island hypothesis — each verb gets its OWN local construction
  first; generalization across verbs is gradual, exemplar-driven, via distributional analogy — governed
  by entrenchment (frequency) and preemption (retreat from overgeneralization). A 2024 Royal Society
  Open Science computational instantiation shows item-based -> emergent-category networks built purely
  from distributional pattern-finding (single-study proof-of-concept, consistent with theory).
  **Structure implied: a GROWN, frequency-scored inventory of item-specific-then-generalized
  constructions** — this is precisely the "grow the inventory from reading" direction already flagged
  in the 07-17 CxG synthesis note; this drill's fresh citations (Tomasello's actual mechanism —
  entrenchment/preemption as the generalization/retreat dynamic) supply the missing HOW that note
  flagged as under-specified.
- **Poverty-of-stimulus debate: genuinely contested, no clean consensus (report honestly).** Nativist
  (Berwick, Pietroski, Yankama & Chomsky 2011) defends that structure-DEPENDENCE (not linear order) is
  what generalizes, arguing surface statistics alone can't deliver it. Empiricist rebuttal (Reali &
  Christiansen 2005) shows simple bigram/trigram/RNN models trained on child-directed speech achieve
  high accuracy on the classic aux-fronting test WITHOUT built-in structural bias. Middle position
  (Perfors, Tenenbaum & Regier 2011, rational Bayesian model selection): hierarchical grammars are
  favored by DOMAIN-GENERAL inductive bias operating over actual input, not language-specific innate
  content. **Structure implied: at minimum, SOME bias toward hierarchical-over-flat grammar hypotheses
  helps generalization — but the literature does NOT establish this bias must be language-specific or
  hand-installed; a domain-general preference-for-structure operating over real exposure is a live,
  credible account.** This directly informs the ranked verdict below: build a bias TOWARD trying
  hierarchical/constructional hypotheses (not a hard-coded universal grammar), scored by fit to data —
  exactly the "coherence-gated, frequency-scored" loop.

Deflated confidence: **P ~= 0.55** that "grow via usage-based item-to-schema generalization,
grounding-first" is the correct high-level acquisition mechanism to imitate (established as the dominant
account, but the poverty-of-stimulus debate genuinely isn't settled, so full endorsement is capped).

---

## (2) Neuroscience of syntax/comprehension — mechanism, citation, structure implied

- **Two-region division of labor (established, Friederici; Hagoort MUC model).** Left posterior
  temporal cortex = lexical-semantic storage/argument-structure retrieval (MEMORY). Left inferior
  frontal gyrus, specifically BA44 = hierarchical syntactic combination/UNIFICATION, connected via the
  dorsal pathway. **Structure implied: comprehension is architecturally TWO mechanisms, not one** — a
  retrieval/lookup store (we have this: the grounded lexicon) and a SEPARATE combination engine that
  builds structure over what's retrieved (this is the part that's thin — see verdict).
- **Agent-first default heuristic + syntactic override, tested by damage (established phenomenon,
  contested mechanism).** Classic agrammatic-aphasia finding: patients fail on reversible passives ("the
  girl was kicked by the boy," either NP plausible) but succeed on non-reversible ones where world
  knowledge disambiguates (Caramazza & Zurif lineage). Grodzinsky's Trace-Deletion Hypothesis (1986/95)
  explains this as: damage to the combinatorial mechanism causes fallback to a default
  first-NP-as-agent heuristic. This is ACTIVELY contested (Caramazza, Capitani, Rey & Berndt 2001 dispute
  whether patients reliably show the predicted agent-first bias at all) — but the PHENOMENON (a fast
  default heuristic that gets overridden by an intact combinatorial mechanism, and reverts to the
  heuristic when that mechanism is damaged) is a clean existence-proof for the two-mechanism structure
  itself, independent of which specific theory of the damage is right. **This directly validates the
  arc's already-built multi-cue role-assigner** (`research_drill_relation_comprehension_reader_thematic_roles_glassbox_2026-07-18.md`)
  as the "default heuristic" layer — the missing piece is the SEPARATE combinatorial-override layer that
  should out-rank the heuristic when structure disambiguates, which our current pipeline doesn't clearly
  distinguish as a separate stage.
- **Hierarchical constituent tracking is a real, established, online neural phenomenon** (Ding, Melloni,
  Zhang, Tian & Poeppel 2016, *Nature Neuroscience*, MEG, landmark/heavily replicated): cortical activity
  entrains simultaneously at syllable/phrase/sentence rates with NO acoustic phrase-boundary cues present
  — direct evidence the brain builds abstract hierarchical structure online, not just linear sequence
  tracking. **Structure implied: hierarchy-building is not a post-hoc analysis step, it happens
  incrementally, word-by-word, DURING comprehension** — reinforcing the WM-barrier note's "incremental
  structural memory, not a batch parse" conclusion from an independent (neuroscience, not
  engineering-benchmark) angle.
- Verb-driven predictive slot-filling: established general phenomenon (N400 predictability effects) but
  whether it is genuinely ROLE-sensitive vs a simpler word-co-occurrence effect is actively debated
  (Chow et al. "bag-of-arguments" vs bag-of-words critiques) — flag as contested, do not over-claim a
  clean "verb pre-activates its argument ROLES" story.

Deflated confidence: **P ~= 0.55** that "two separable mechanisms — fast multi-cue default heuristic +
a distinct hierarchical-combination override, built incrementally" is the correct architectural
characterization (established core findings, but exact division-of-labor claims and the
override-mechanism's precise computation remain contested in the primary literature).

---

## (3) The hierarchy/composition question — mechanism, citation, structure implied

**This is the angle most directly load-bearing for a VSA/HDC substrate and had not been drilled in this
arc before.**

- **PROVEN (formal, established):** flat finite-state models (n-grams, bounded-memory HMMs) cannot
  recognize general context-free languages — unbounded center-embedding, arbitrary-distance agreement —
  because that requires unbounded stack memory (Chomsky hierarchy, textbook result). BUT this
  impossibility is scoped to genuinely UNBOUNDED recursion. Hewitt, Hahn, Ganguli, Liang & Manning
  (EMNLP 2020) show RNNs — sequential, no explicit tree data structure — can generate BOUNDED-depth
  hierarchical (Dyck-(k,m)) languages with only O(m log k) hidden units, exponentially better than naive
  bounds. **The strict impossibility result does not bite at the depths real prose actually uses.**
- **ARGUED/contested (linguistic theory, not resolved):** Hauser, Chomsky & Fitch (2002) argue recursion
  (Merge) is the singular human-specific combinatorial operation. Major pushback: Christiansen & Chater
  (2008 BBS; 2015 Frontiers) argue recursive processing emerges from domain-general sequential-learning
  constraints and most attested language uses only shallow/bounded embedding, not unbounded recursion.
  Frank & Bod (2011, *Psychological Science*) found sequential (non-hierarchical) surprisal models
  predict human reading times as well as hierarchical PSG-based models — contested, single-study-caliber,
  but cited heavily on both sides. **No settled answer on whether human language "needs" unbounded
  recursion — but strong, convergent evidence that ATTESTED language mostly doesn't exercise it.**
- **ENGINEERING-DEMONSTRATED:** hierarchy CAN be learned from flat text without being told the tree in
  advance, but only given SOME structural inductive bias layered onto a flat model — a CFG-shaped
  backbone (compound PCFG, Kim/Dyer/Rush 2019), a recursive inside-outside composition function (DIORA,
  Drozdov et al. 2019), or ordered/gated memory units (ON-LSTM, Shen et al. 2019, cumax gating recovers
  hierarchy from a standard LSTM with no explicit tree scaffold). **A fully bias-free flat model has not
  been shown to spontaneously discover hierarchy** — some inductive-bias assist is required, but it does
  not have to be an explicit symbolic tree structure; a soft/gated bias suffices.
- **Vector-symbolic representation of trees — the substrate-relevant core finding.** Smolensky's (1990)
  Tensor Product Representations are exactly, mathematically recursive: a filler CAN be another bound
  structure (binding-of-bindings), but dimensionality grows exponentially with recursion depth —
  established mathematical cost. Plate's Holographic Reduced Representations (1995) fix the
  dimensionality blowup via circular convolution, keeping bound structures at fixed width — established
  — but the unbind (quasi-inverse) operation is LOSSY, and noise accumulates per binding depth, which
  practically bounds usable recursion depth. **This is the exact VSA-native analog of the RNN
  "bounded-not-unbounded" finding above** — recursive binding is mathematically available, exact for
  bounded depth, degrading (not catastrophically failing) beyond some noise-limited ceiling. Fodor &
  Pylyshyn's (1988) systematicity challenge to connectionism remains explicitly UNRESOLVED as of very
  recent (2025-2026) papers specifically on whether flat/distributed binding achieves human-like
  systematic compositionality — recent VSA surveys agree flat single-level role-filler binding is
  straightforward and well-understood, but NESTED/recursive binding-of-bindings for genuine tree
  structure is the harder, still-actively-researched case, not a solved problem even in the general
  field (not just for us).

**Verdict for this angle: flat, single-level binding is NOT structurally sufficient for hierarchical
predicate-argument structure with real (if bounded) embedding — but the fix is not "invent a new
capability," it is "use the ALREADY-AVAILABLE recursive/nested binding operation as the compositional
target of the reader," which our bind/unbind/resonator primitive supports today for bounded depth. The
genuinely open research problem (unbounded recursion, exact-vs-noisy tradeoff at depth) is a live field-
wide gap we do not need to solve to make real-prose progress, because real prose rarely exercises depth
beyond where the noise-accumulation ceiling would bite.**

Deflated confidence: **P ~= 0.50 (capped, novel-synthesis)** that "nested/recursive binding as the
compositional target, applied incrementally, closes the hierarchical-structure gap for real-prose-typical
bounded embedding" — the formal/engineering literature strongly supports the BOUNDED-depth claim, but no
source directly tests THIS substrate's specific bind/unbind/resonator implementation at nested depth, so
the mapping from "the literature says bounded recursive VSA binding should work" to "ours specifically
will" is this drill's own inference, held at the calibration cap.

---

## (4) ML NLP history — what beat hand rules, and which regime is the fair analog

- **The arc (established):** hand-written ATN/LFG/HPSG grammars (1960s-80s) -> treebank-supervised
  statistical parsers (Penn Treebank 1993; Charniak 1996 treebank-grammar PCFGs; Collins 1997/99
  lexicalized PCFG; Charniak 2000 ~90.1% F1) -> dependency parsing (Nivre transition-based, McDonald
  graph-based MST, complementary strengths per McDonald & Nivre 2007/2011) -> neural (Chen & Manning
  2014 first neural transition parser eliminating hand feature templates; Kiperwasser & Goldberg 2016
  BiLSTM features; Socher et al. 2013 recursive compositional vector grammars; Tai et al. 2015
  Tree-LSTMs generalizing recursive composition).
- **What carried each gain (established, not just coverage):** Collins's lexicalized-vs-unlexicalized
  ablation isolates a real STRUCTURAL change (head-word conditioning), not just more rules — ~75% to
  ~85% bracketing accuracy from that one change. Hindle & Rooth (1993) is a clean existence-proof that
  pure distributional/lexical-association statistics (~80% accuracy) beat hard structural heuristics
  (Right Association/Minimal Attachment, ~55%) on identical PP-attachment decisions — the SAME
  finding independently re-surfaced in the arc's own `research_hardrule_vs_predictive_parsing_barrier_2026-07-17.md`.
  **This drill's fresh citations corroborate that note's central claim from the primary ML-history
  literature, not just from the substrate's own rung data** — real convergence, not restated hunch.
- **The fairness question (this drill's sharpest new contribution):** Penn Treebank supervision requires
  ~1M words of HAND-DISAMBIGUATED gold trees — a human already resolved every ambiguity being learned
  from. This is a fundamentally different regime from acquisition or from a substrate with no rule-writer
  and no gold trees. The literature's own honest ceiling for the FAIR (no-gold-trees) regime:
  unsupervised grammar induction (Klein & Manning 2004 DMV, EM-based) reaches roughly **~40-70% directed
  accuracy on WSJ10 (sentences <=10 words)** vs supervised parsers at 90%+ on full-length sentences —
  and even that unsupervised number typically LEAKS gold POS tags as scaffolding (bare unsupervised POS
  induction is "significantly worse," per Klein & Manning's own finding). Grounded (non-gold-tree,
  perception-paired) structure-induction work specifically is thin — mature grounded-language literature
  (Yu & Ballard cross-situational learning) is almost entirely about WORD-REFERENT mapping, not syntax;
  there is no mature "grounded-syntax-from-near-nothing" benchmark to point to.

**Fair-analog verdict: unsupervised/grounded induction is the correct analog for a system building from
near-nothing — NOT supervised treebank parsing — and the honest achievable ceiling in that regime is
real, documented, and meaningfully BELOW supervised numbers, especially on longer/harder sentences.**
This should temper (not abandon) the "grow a construction inventory from reading" ambition already in
the arc: expect something in the ballpark the field's own honest unsupervised numbers show (worse on
hard/long prose, much better on simple/short prose — consistent with the arc's own register-dependent
estimates: 0.80-0.95 on grade-1 SVO vs 0.44 on complex textbook prose).

Deflated confidence: **P ~= 0.60** that unsupervised/grounded induction is the fair regime and its
honest ceiling sits well below supervised parsing (established finding, direct citation, but the exact
size of the gap on OUR specific register/corpus is untested — flagged as extrapolation from WSJ10
numbers to our text, which may not transfer cleanly in either direction).

---

## (5) THE STRUCTURAL VERDICT — ranked

Given all five angles plus the five prior arc notes, ranked by cost x convergence x leverage:

1. **[RANK 1 — do FIRST, near-zero-cost, mostly UNDERUSE not absence] Recursive/nested composition as
   the reader's compositional target.** Rewire the extractor from flat-triple emission to an incremental
   stack of open dependencies where a role's FILLER can itself be a previously-bound sub-proposition
   (nested bind-of-bind) — the exact operation our bind/unbind/resonator primitive already supports
   mathematically for bounded depth (angle 3), independently re-derived from the WM-barrier note's
   dependency-stack conclusion (angle 3 + prior WM-barrier note convergence) and the neuroscience angle's
   "hierarchy is built incrementally, not batch" finding (angle 2, Ding et al. 2016). This is a
   near-zero architectural cost because the PRIMITIVE already exists; the gap is that the current
   pipeline never calls it recursively.
2. **[RANK 2 — the BIG, genuinely-open build] A learned, grounding/comprehension-scored construction
   induction + disambiguation mechanism**, i.e. the arc's already-identified "grow-from-reading" +
   "surprisal-scored disambiguator" directions (07-17 CxG note, 07-17 hardrule-vs-predictive note),
   reinforced from two NEW angles this drill supplies: (a) Tomasello's item-to-schema generalization
   mechanism (entrenchment/preemption) as the concrete LEARNING RULE — not previously specified in this
   much mechanistic detail in the arc; (b) the ML-history confirmation that structural priors (not
   coverage alone) drove historical gains, cross-validating the substrate's own rung-data finding from
   an independent literature. This is where the ACTUAL "learned not hand-fed" capability gap lives —
   everything upstream (grounding) and downstream (binding, storage, coref) is already a substrate
   strength per the relation-comprehension note; this is the one real missing capability.
3. **[RANK 3 — a training PROCEDURE for #2, not a separate structural ingredient] The
   bootstrapping-loop + coherence-gate** (known meaning/constructions score candidate parses ->
   successful/coherent parses get counted into the construction-frequency table -> table informs future
   scoring, gated by schema-fit so bad parses don't poison the store). This is HOW #2 gets built and
   kept honest, not a fourth independent structure — folding it into #2's scope, per the acquisition
   angle's usage-based mechanism and the standing dragonfly/comprehension-loop memory anchor.
4. **[Explicitly NOT the primary gap, contra a naive reading of the WM literature]** A bigger/unbounded
   memory BUFFER is not the lever — this is the WM-barrier note's already-landed conclusion, and this
   drill's formal/engineering literature (Hewitt et al. 2020; chart-parsing memoization results) directly
   corroborates it: buffer SIZE is not the bottleneck axis; STRUCTURE (recursive composition) and
   LEARNED SCORING (disambiguation) are.

**Honest tempering, stated plainly:** rank 2 is real and big, and its ceiling (per angle 4) is
literature-documented to sit below what hand-rule-plus-supervision can reach on hard/long prose — this
is not a shortfall of ambition or effort, it is a field-wide, well-replicated finding about what
unsupervised/grounded structure-learning achieves. Register matters enormously: expect near-supervised
performance on simple/short/grade-1-style text and a real, honest gap on complex/long prose, for the
foreseeable future, for ANY system (human-inspired or engineered) that must build from near-nothing.

---

## Concrete glass-box-buildable proposal

**Stage A (cheap, do first, near-zero new capability — wiring not invention):** Rewire the current
hand-rule extractor from flat SVO-triple emission into an incremental shift-reduce-style structure
builder: maintain an explicit stack of open dependencies; when a role's filler is itself a clause
(relative clause, coordinated VP with a shared subject, complement clause), BIND it as a nested
sub-proposition (bind-of-bind) rather than flattening it or dropping it. This composes directly with:
grounded words (already done, feeds the leaf bindings), the multi-cue role-assigner
(`research_drill_relation_comprehension_reader_thematic_roles_glassbox_2026-07-18.md`, feeds each
binding decision), the working-memory/discourse overlay (holds the open subject across a coordination
boundary — reuses existing machinery per the learned-parser-blueprint note), and coref (binds mentions
into the nested structure across sentences).

**Stage B (bigger, sequenced after A, the real "learned not hand-fed" build):** A small, named,
enumerable construction inventory (SV/SVO/SVOO/reduced-RC-on-subject/compound-noun-head/PP-attachment,
per the constructions already named in the arc's prior notes), each construction scored by a
frequency-ratio / log-probability-ratio quantity computed from CORPUS COUNTS (Jurafsky-style — e.g.
verb-transitivity-bias x reduced-RC base rate for the reduced-RC case; left/right head-preference
counts for compound nouns) — reusing the substrate's EXISTING KL/Bayesian-surprise primitive (already
built for the memory-ingest gate, per the hardrule-vs-predictive note's finding that this is literally
the same math object redeployed at a different grain). The table is UPDATED via the bootstrap loop:
score candidates using current counts -> the winning parse, if it passes a coherence/schema-fit gate,
increments the count for the construction it used -> future scoring improves. Every number in this
system is a named, auditable count or ratio — no learned embeddings, no LLM, glass-box by construction.

**Composition with what we already have:** Stage A supplies the STRUCTURE (where ambiguity/composition
lives); Stage B supplies the SCORING (which structure wins when more than one is grammatically
admissible); the existing grounded lexicon, role-assigner, WM/discourse overlay, and coref resolver are
untouched inputs/consumers. This is not a parallel new pipeline — it is the SAME reader, with its
compositional target changed from flat-triple to nested-binding, and its disambiguation changed from
fixed-rule to frequency-scored.

---

## FAIR can-fail test

**Real baseline:** the CURRENT hand-rule flat-SVO extractor (not abstain-all, not a strawman) — must be
beaten, not merely matched, on identical sentences.

**Difficulty ON (must include, not optional):** reduced-relative-clause-on-subject sentences,
compound-noun head ambiguity (proper-name vs descriptive compound), PP-attachment ambiguity (manner vs
location), coordinated-VP shared-subject cases, and at least a few real 2-level-embedding sentences if
present in the corpus — these are the SAME named residual failure modes already isolated in this arc's
own VET record (Rung 5b/7/8) and blueprint notes, not invented for this test.

**One variable per arm:**
- Stage-A test isolates ONLY the structural-memory variable: hold rule vocabulary fixed, compare flat
  positional assignment vs incremental nested-binding structure-building on the SAME sentences.
  HARD-PASS: >=10 points accuracy/F1 gain specifically on constructions requiring non-adjacent or nested
  role resolution (relative clause, coordinated shared-subject), holding everything else fixed
  (this reuses the WM-barrier note's Prediction 1 design exactly).
  HARD-FAIL: <3 point gain — would indicate the recommended gains are coming from rule vocabulary, not
  from having nested structure per se.
- Stage-B test isolates ONLY the scorer: hold the (now nested-capable) structural parser fixed, compare
  fixed-rule preference vs learned frequency-ratio construction scorer on the two named ambiguous
  constructions. HARD-PASS: construction-scoped accuracy on reduced-RC-on-subject rises from current
  declared 0% to >=60% using ONLY named auditable frequency counts, zero regression on already-correct
  cases (reuses hardrule-vs-predictive note's Cell 1 design exactly). HARD-FAIL: stays <35%, or requires
  semantic/world-knowledge features beyond simple two-factor counts — a real (not implementation)
  ceiling for this construction at this scope.
- Independent gold: gold relations/constructions from an EXTERNAL source (held-out human-labeled slice),
  never emitted by the same generator that made the test sentences — guards against the
  construction-determined-outcome trap already flagged in the relation-comprehension note.

**MIDDLE-band handling:** if Stage A HARD-PASSes but Stage B HARD-FAILs (or vice versa), the honest
read is that ONE of the two ranked levers is load-bearing and the other should be deferred — do not
force both into the story if the data only supports one.

---

## Cross-thread synthesis

This drill's job was explicitly to fill the two gaps the existing arc had NOT yet covered
(acquisition/neuroscience biology-first grounding, and the hierarchy/recursion-in-VSA question) and then
integrate. The integration lands cleanly: every one of the five prior notes' conclusions is CORROBORATED
by an independent literature angle here, not contradicted —
`research_wm_barrier_glassbox_parsing_2026-07-17.md`'s "structural memory not buffer size" claim is
independently reinforced by the neuroscience angle (Ding et al.'s online hierarchy-building) and the
formal-language angle (Hewitt et al.'s bounded-vs-unbounded RNN result);
`research_hardrule_vs_predictive_parsing_barrier_2026-07-17.md`'s "disambiguation needs graded scoring"
claim is independently reinforced by this drill's fresh Hindle & Rooth / Collins ML-history citations;
`research_how_brain_does_broad_construction_parsing_synthesis_2026-07-17.md`'s "grow the inventory,
don't install it" claim gets its missing mechanistic HOW from Tomasello's entrenchment/preemption
dynamic (this drill's acquisition angle). The one genuinely NEW finding this drill adds to the arc is
the supervised-vs-grounded fairness verdict (angle 4) — an honest, literature-documented ceiling for
what a from-near-nothing system should expect, which the arc had been implicitly optimistic about.

## Substrate-product implications

Two build items, sequenced by cost: (1) near-zero-cost — wire the existing nested-bind primitive into
the reader as its compositional target instead of flat-triple emission; (2) a real but bounded build —
a small, named construction-scorer reusing the existing KL/surprise-gate math, trained via a
bootstrap+coherence-gate loop, targeted narrowly at the already-isolated disambiguation tail (not a
general PCFG/statistical-parser rebuild). Both keep the no-LLM-at-runtime invariant fully intact — every
number is a named, auditable count. Expect register-dependent results: near-ceiling performance on
simple/grade-1 text, a real and literature-documented (not implementation-embarrassing) gap on complex
prose — set expectations accordingly rather than treating a lower complex-prose number as a bug.

## Citations (verified count)

**~35** distinct primary sources freshly verified via live search this session across the three
lit-scans (Saffran, Aslin & Newport 1996/1998; Pinker 1984; Gleitman 1990; Tomasello 2000/2003; Berwick,
Pietroski, Yankama & Chomsky 2011; Reali & Christiansen 2005; Perfors, Tenenbaum & Regier 2011;
Friederici/Trettenbrein 2025; Hagoort MUC; Caramazza & Zurif lineage; Grodzinsky 1986/95; Caramazza,
Capitani, Rey & Berndt 2001; Ding, Melloni, Zhang, Tian & Poeppel 2016; Hickok & Poeppel 2007; Klein &
Manning 2001/2002/2004; Kim, Dyer & Rush 2019; Drozdov et al. 2019; Shen et al. 2019 ON-LSTM; Hewitt,
Hahn, Ganguli, Liang & Manning 2020; Hauser, Chomsky & Fitch 2002; Christiansen & Chater 2008/2015;
Frank & Bod 2011; Smolensky 1990; Plate 1995; recent 2025-2026 Fodor & Pylyshyn systematicity-challenge
papers; Woods ATN; Marcus et al. 1993 Penn Treebank; Charniak 1996/2000; Collins 1997/99; Hindle & Rooth
1993; Nivre / McDonald 2007/2011; Chen & Manning 2014; Kiperwasser & Goldberg 2016; Socher et al. 2013;
Tai et al. 2015; Yu & Ballard cross-situational learning). Plus the five prior-arc notes cited and
cross-checked against, not re-derived. Several claims (exact DeLong-style ERP numbers, precise
Frank & Bod effect sizes, MacWhinney Competition Model specifics) are flagged inline by the sub-agents
as recalled-from-training/secondary-sourced rather than freshly re-verified — excluded from load-bearing
predictions.

## Calibration

Per [[feedback-lit-scan-calibration-penalty]]: all P estimates deflated 0.15-0.25 from raw
literature-agreement reads. The two genuinely novel-synthesis claims in this note — "flat single-level
binding suffices for bounded real-prose hierarchy via the existing bind/unbind primitive, applied
recursively" (angle 3 verdict) and "the ranked verdict integrating all five arc notes plus fresh
acquisition/neuroscience/ML-history citations" (angle 5) — are capped at P<=0.50. Established literature
claims (Saffran, Tomasello, Ding et al., Hewitt et al., Collins, Hindle & Rooth, Klein & Manning) sit at
the higher P~=0.55-0.65 band reported per-section above. HYPOTHESIS-generating throughout; VET-pending.
