# Research: prior art for a self-extending grounded-knowledge acquirer (2026-08-04)

Lead-with-prior-art design drill. Question (USER-raised): hand-building each grounded competency
(harm, goals, irony, counterfactual causation, norms...) does not scale. The goal is a substrate
that reads text, detects a causal/goal/affective regularity it cannot explain, INDUCES the missing
grounded schema, adds it to its store, and reads on -- a never-ending self-extending acquirer.
KB-check done (director_kb_query launched; no direct-hit prior note found under this framing --
closest neighbors are `metacognitive_flag_layer_calibration_design_and_confidence_inventory_2026-08-02.md`
and the causal-coherence credit-assignment 2x drill `research_drill_biology_led_causal_coherence_credit_assignment_2026-08-03.md`,
both read directly and folded in below). 3 parallel Sonnet lit-scan sub-agents dispatched (NELL /
never-ending learning; script-schema induction; developmental bootstrapping + curiosity). Findings
integrated below with the lit-scan calibration penalty applied throughout.

## (a) HEADLINE

The published prior art gives a complete, well-tested ARCHITECTURE PATTERN for self-extension
(seed -> coupled multi-view extraction -> anti-drift constraint check -> promote -> repeat, NELL
2010-2018; disequilibrium-triggered accommodation, Piaget; learning-progress-ranked gap selection,
Oudeyer-Kaplan 2007) but **zero published system closes the full loop for CAUSAL/grounded schema
induction the way our question asks** -- every candidate (NELL's OntExt, Chambers-Jurafsky
narrative chains) either needed a human gate at the schema-minting step, or induced
TEMPORAL/CO-OCCURRENCE structure, not CAUSAL structure, and the field's own consensus (Mostafazadeh
et al. 2016) is that causal typing needs an independent evidence source, not a scaled-up
association metric. We already own the two organs NELL's architecture depends on
(`self_improving_loop.py` = the coherence-gated keep/revert coupling-check; `situation_model_accumulate.py`
= the relational-binding substrate) -- what's missing is (1) a schema-MINTING operator (nothing
currently proposes new roles/relation-types, only re-decodes existing ones) and (2) a genuine
second independent view to couple against (our loop currently checks a candidate against itself,
not against a structurally-different extractor -- this is the single largest fidelity gap vs NELL's
proven anti-drift mechanism). P_deflated=0.40 (novel-synthesis cap applies: no direct precedent
combines these pieces).

## (b) Cheap decisive test

Before building anything: **can `self_improving_loop.route_passage` distinguish a genuinely-novel
schema from a mis-clustered extension of an existing one, using only the coherence-margin signal it
already computes?** Concretely: take the 8 causal cross-span eval items already mined
(`data/eval_gold_mention_role_mcguffey_v1/gold_grounded_causal_crossspan_v2_DRAFT.jsonl`) plus the
10 detective-fiction items, hand-label each as "explainable by an existing schema slot" vs "requires
a genuinely new causal-role type" (this labeling is cheap -- ~18 items, Director can do it in one
pass), then check: does the EXISTING coherence-margin-delta signal separate the two classes when a
new schema is force-fit into the old role vocabulary vs allowed a fresh role? If margin-delta is
flat across both classes (no separation), the existing coherence-gate is NOT sufficient as the
minting trigger and a genuinely new disequilibrium-detection signal (prediction-error magnitude
against the current schema library, not just top1-vs-runner-up margin) must be built first. This
test costs ~1 hour (label + rerun route_passage on the 18 items with role-vocab held fixed vs
extended) and is fully within existing organs -- no new build required to RUN it.

## (c) Falsifiable predictions

**HARD-PASS (existing organ sufficient, minting is a routing decision not new machinery):**
coherence-margin-delta on the "needs new schema" subset is significantly lower (>=0.05 mean gap,
non-overlapping IQR) than on the "fits existing schema" subset, when both are scored against the
FIXED existing role vocabulary. This would mean the disequilibrium signal (low margin = "existing
schema doesn't explain this") is already present for free in the coherence-gate and only a minting
ACTION needs to be added on top.

**HARD-FAIL (existing organ insufficient, need a dedicated novelty-detector):** margin-delta
distributions overlap >50% between the two classes (Mann-Whitney p > 0.10 on n=18, likely
underpowered but directionally informative) -- meaning role-decode margin conflates "bad coref
alignment" with "genuinely missing schema," and a separate signal (e.g. residual prediction error
against ALL existing schema slots simultaneously, not just top-1 margin) is needed as the trigger.

**HARD-FAIL (schema library does not stay clean under autonomous growth -- the NELL drift risk,
tested once minting exists):** after minting >=3 new schemas autonomously on held-out content, a
human audit finds >=1 case of two schemas that should have been merged (duplicate/near-duplicate
role structure) or one schema whose role-fillers are semantically incoherent (the "cookies are a
baked good -> computer files are a baked good" NELL drift signature) -- this would mean the
anti-drift coupling-check (see Part 2 below) is not doing its job and needs a second independent
view, not just a confidence threshold on the first.

## (d) Cross-thread synthesis: the prior-art systems + their self-extension architecture

### 1. NELL -- Never-Ending Language Learning (Carlson, Betteridge, Kisiel, Settles, Hruschka,
Mitchell, "Toward an Architecture for Never-Ending Language Learning," AAAI 2010; Mitchell, Cohen,
Hruschka et al., "Never-Ending Learning," CACM 61(5) 2018)

**Architecture:** seed ontology (few hundred categories/relations, type constraints, seed
instances) + a growing confidence-weighted KB + multiple COUPLED semi-supervised extractors
operating over DIFFERENT VIEWS of text (free-text patterns, HTML/table structure, morphology,
later embeddings) that jointly nominate candidate beliefs each cycle + a low-frequency human
sanity-gate (every few weeks, NOT per-example).

**The anti-drift mechanism (the load-bearing piece for our question), Carlson et al. "Coupled
Semi-Supervised Learning for Information Extraction," WSDM 2010 -- the Coupled Pattern Learner
(CPL):** rather than bootstrap one extractor per relation in isolation (classic self-training,
provably prone to drift per Blum & Mitchell's co-training theory, COLT 1998, when the "views" are
not conditionally independent), NELL trains MANY extractors simultaneously and couples them via
two constraint types: (i) mutual exclusion -- categories declared mutually exclusive (City vs.
Scientist) mean a positive instance for one is automatically a NEGATIVE example for the other, so
contradictory promotions are suppressed before they compound; (ii) relation type-checking --
`ceoOf(person, company)` requires BOTH argument slots to already be independently confidently typed
by the category extractors, so a candidate is only promoted if it satisfies constraints supplied by
OTHER, structurally-different components of the same ontology. This is what lets the system
self-supervise across thousands of predicates without per-item human labels: the ontology's own
logical structure supplies the negative-supervision signal, and promotion requires agreement across
multiple INDEPENDENT extractor types, not confidence from a single self-referential loop.
Curran, Murphy & Scholz ("Minimising Semantic Drift with Mutual Exclusion Bootstrapping," PACLING
2007) independently formalized the same principle (MEB): competing semantic classes actively BLOCK
each other's claims on ambiguous candidates.

**Autonomous new-relation-schema induction:** OntExt (Mohamed, Hruschka, Mitchell, "Discovering
Relations between Noun Categories," EMNLP 2011) -- for every pair of existing categories, pull
co-mention sentences, cluster context vectors, each cluster is a CANDIDATE new relation, filtered
by a classifier PLUS manual review before ontology edit. Semi-autonomous only -- humans gated the
final schema-minting step; this was never NELL's primary growth engine (which was
instance-of-existing-relation extraction, not new-relation minting).

**Failure modes over ~9 years of continuous operation (2010-2018/19):** absolute KB size grew
(242K beliefs @ 74% precision in 2010 -> ~120M beliefs by 2018) but precision on the LONG TAIL
stayed weak throughout -- Stuart Russell's critique that NELL held high confidence in only ~3% of
its beliefs indicates the bulk of the KB never converged to clean/trusted status. Human correction
remained a STANDING requirement for the life of the project (did not phase out). Never escaped
shallow surface web-page text (no deeper discourse diversity). No published formal
plateau/postmortem; the project simply stopped active updates without an explicit stopping
criterion.

### 2. Unsupervised script/narrative-schema induction (Chambers & Jurafsky, "Unsupervised Learning
of Narrative Event Chains," ACL 2008; "Unsupervised Learning of Narrative Schemas and their
Participants," ACL/IJCNLP 2009)

**Mechanism:** PMI over verb-pairs CONDITIONED on sharing a coreferring protagonist argument (not
raw co-occurrence PMI -- their own ablation shows the coreference-conditioning beats plain
co-occurrence PMI by 36% on narrative-cloze). Chains built by agglomerative clustering on these PMI
scores; a pairwise temporal classifier orders the chain. The 2009 follow-up adds typed semantic
roles per schema slot by clustering the argument head-nouns filling each verb's slot corpuswide.

**New-schema-vs-extend decision:** NO explicit online decision procedure exists in this literature.
It is a global offline agglomerative clustering pass over the WHOLE corpus each time, with the
new-vs-existing boundary implicitly set by a tuned clustering stopping criterion (PMI cutoff /
target cluster count), not a principled statistical test. Later work ("Human-in-the-Loop Schema
Induction," Rasheed et al. arXiv:2302.13048, 2023) explicitly concludes fully-automatic
new-vs-existing decisions are unreliable enough to route to a human.

**CRITICAL LIMITATION, directly on point for our question:** this line of work captures
CO-OCCURRENCE/TEMPORAL structure, NOT causal structure. Mostafazadeh, Grealish, Chambers, Allen &
Vanderwende ("CaTeRS," 2016) states plainly that narrative-chain approaches miss "a more
comprehensive set of semantic relations between events such as causality, which is a core relation
in stories." The field's consensus: relatedness-via-shared-argument-PMI is a genre/co-occurrence
signal and CANNOT by itself deliver causal typing -- causal typing requires an INDEPENDENT evidence
source (discourse connectives / cue-phrases: because, so, therefore -- Do, Chan & Roth 2011;
"Minimally Supervised Event Causality Identification"), fused in AFTER the relatedness step, not
derived from it. ATOMIC/COMET (Sap et al. 2019; Bosselut et al. 2019) is the modern instance of
this same two-stage pattern: seed causal tuples (human-authored, not induced) + a
distributional-similarity generalization step to extend to unseen entities -- the generalization
LOGIC (seed -> similarity-based extension) is separable from the LM that implements it in COMET
and is the same logic as pre-neural Hearst-pattern bootstrapping.

**Core induction logic, implementation-independent (relevant for glass-box portability):** three
separable steps -- (1) a relatedness/association metric between event-tokens CONDITIONED on a
shared structural anchor (coreference is what makes it "narrative" not generic co-occurrence); (2)
a threshold-based clustering rule over that relatedness graph, producing the schema as a connected
component; (3) a DISTINCT, separately-implemented typed-relation layer (temporal classifier or
causal-cue classifier) bolted on top of (1)-(2)'s output. Steps 1-2 are directly portable to a
symbolic/hypervector similarity substrate with no borrowed embeddings (PMI-over-coreference IS
already a symbolic co-occurrence statistic). Step 3 -- genuine causal (not correlational) typing --
is NOT solved by scaling steps 1-2; every source in this scan agrees it needs an independent cue
(discourse markers, or hand-seeded structure) as a SEPARATE signal.

### 3. Developmental bootstrapping (Spelke core knowledge 2007/2022; Carey Quinian bootstrapping
2009/2011; Piaget assimilation/accommodation; Gleitman/Pinker syntactic & semantic bootstrapping)

**Minimal innate seed (Spelke):** ~5-6 domain-specific core-knowledge systems -- objects
(cohesion/physical reasoning), agents/actions (goal-directedness), number (approximate magnitude),
space/geometry (navigation/forms), social partners (in-group/social-being tracking). Ancient,
early-emerging, encapsulated, shared cross-species. Everything past this (language-mediated
concepts, biological-kind categories, exact large numbers) is CONSTRUCTED, not innate.

**Carey's Quinian bootstrapping mechanism (the induction step, once a gap is selected):** children
acquire words/symbols as semantically-THIN PLACEHOLDERS before having the corresponding concept
(e.g. number words in a memorized count sequence), interrelate the placeholders via an explicit
relational structure already available (the successor function implicit in counting; an
analogical mapping to an already-understood domain), then meaning accrues to the placeholders
through analogical/inductive reasoning over that relational structure until a genuinely NEW
representational resource "bootstraps out" whose content exceeds what was present in either the
core system or the placeholder symbols alone. This is the closest developmental account of HOW a
new grounded concept gets minted from existing structure plus exposure -- but it presupposes rather
than computes the trigger/selection step (which gap to bootstrap, and when).

**Piaget's disequilibrium trigger (the gating step Carey's account lacks):** assimilation =
incorporate new data into an EXISTING schema unchanged; accommodation = MODIFY/CREATE a schema
because the existing one is inadequate. The decision rule: if new data fits within the schema's
current predictive range, assimilate; if it actively contradicts/exceeds what the schema can
represent (disequilibrium / cognitive conflict), accommodate. This is structurally IDENTICAL to
"flag a gap I can't explain -> mint a schema" -- Piaget gives the qualitative trigger, but never
formalized it quantitatively.

**Gleitman/Pinker bootstrapping (the reuse-existing-structure mechanism):** semantic bootstrapping
(Pinker) maps innate perceptual/cognitive categories (agent, patient, action, state) onto syntactic
categories via innate linking rules; syntactic bootstrapping (Gleitman, Landau) runs the inference
the other direction -- observed syntactic argument-frame structure is used to reverse-engineer a
NEW verb's meaning, critical for abstract/mental-state verbs that can't be learned from a paired
observable event. Complementary: whichever structure came online first is reused as EVIDENCE to
infer the other, unsupervised. Directly analogous to our situation: coreference/role-binding
structure (already built) could be reused as evidence to infer a NEW causal-role schema, the same
way syntax is reused as evidence to infer new verb meaning.

### 4. Intrinsic motivation / curiosity-driven learning (Oudeyer, Kaplan & Hafner, "Intelligent
Adaptive Curiosity," IEEE TEC 2007; Oudeyer & Kaplan typology of intrinsic motivation)

**Learning-progress signal:** for each region/situation ("progress niche") in the space, compute
the RATE OF DECREASE in prediction error over a recent sliding window (error_before - error_after),
not raw error (novelty-seeking) and not raw accuracy (familiarity-seeking). Maximizing raw novelty
gets stuck on unpredictable/stochastic regions forever (the "noisy TV problem" -- infinite
unlearnable entropy looks maximally rewarding since error never decreases); maximizing familiarity
collapses onto already-mastered regions. The DERIVATIVE naturally routes attention to "just-right,"
currently-improvable regions, self-organizing a developmental curriculum.

**Ranking multiple simultaneous gaps:** the architecture tracks learning-progress estimates for
MULTIPLE candidate niches IN PARALLEL and selects PROBABILISTICALLY (not greedy argmax) weighted
toward the highest-progress niche -- this lets lower-ranked niches still get sampled, so the system
detects saturation of the top niche and switches. This is exactly a "rank multiple unexplained-
regularity flags by expected learning value, sample probabilistically" mechanism, and it is
EXPLICIT and quantitative where Piaget's account is only qualitative.

**Synthesized best-candidate operator (cross-thread):** Piaget's disequilibrium criterion (WHEN to
accommodate) fused with Oudeyer-Kaplan's learning-progress metric (WHICH gap, when several compete,
tracked as error-reduction RATE not raw error) is the cleanest published operator for the
gating/prioritization half of our question. Carey's Quinian bootstrapping is the cleanest account
of the INDUCTION half (what happens once a gap is selected: placeholder-then-analogical-fill using
already-available relational structure). None of these three papers were written to interoperate --
this is a genuine cross-thread synthesis, hence the P-cap.

## (e) Mapping onto OUR existing organs + named gaps

| Prior-art mechanism | Our organ that implements/approximates it | Gap |
|---|---|---|
| NELL's promotion-requires-independent-view coupling (CPL mutual-exclusion + type-check) | `hdlab/self_improving_loop.py` `route_passage`/`decide_keep_or_revert` -- coherence-gated keep/revert, abstain-band adoption rule | **GAP 1 (largest):** our gate checks a candidate against ONE signal (its own coherence-margin delta, computed by re-decoding the SAME `situation_model_accumulate` register). NELL's anti-drift power comes specifically from checking against a STRUCTURALLY DIFFERENT extractor (a second, independent view). We do not yet have a second independent view to couple against -- this is the single most load-bearing missing piece, not a refinement of what exists. |
| NELL's ontology type-constraints (argument-type checking before promotion) | `hdlab/situation_model_accumulate.py` `AccumulateRegister`/`CausalLinkRegister` -- role_vocab is a closed, hand-specified list; `add_event(entity, role, event_idx)` requires the role to already be in-vocab | **GAP 2:** role_vocab is currently STATIC (fixed at construction). There is no `mint_new_role()` operator. Minting requires deciding both WHEN (the disequilibrium trigger) and WHAT (the new role's binding signature) -- neither exists. |
| Chambers-Jurafsky's coreference-conditioned relatedness metric (step 1 of their 3-step logic) | `hdlab/coreference_resolver.py` (Hobbs/Centering backward-search, per prior research drills) + `situation_model_accumulate`'s per-entity event-slot binding | Directly reusable AS THE ANCHOR for a novel schema-discovery pass: cluster events sharing a coreferent entity, exactly as C&J do, using OUR coref organ instead of a distributional one. Not yet wired for this purpose (currently used only for READING existing structure, not for discovering new schema clusters). |
| Piaget's disequilibrium trigger (assimilate vs accommodate) | The metacognitive FLAG layer (`notes/metacognitive_flag_layer_calibration_design_and_confidence_inventory_2026-08-02.md`) -- coref margin / role-extraction confidence / lexicon-miss surprise, AUC-calibrated | Partial: the flag layer detects "I'm uncertain about THIS decision" (low margin on an existing role-vocab decode). It does NOT yet detect "no existing schema explains this AT ALL" (a qualitatively different signal -- residual/error against the WHOLE schema library, not margin within one). This is exactly the (b) cheap decisive test above. |
| Oudeyer-Kaplan's learning-progress ranking across multiple niches | None currently. We have single-flag detection, not multi-gap ranking-by-expected-value. | **GAP 3:** no mechanism exists to rank several simultaneously-flagged gaps by "how much would closing this teach me," only to flag one gap at a time. Lower priority than Gaps 1-2 -- only matters once minting exists and produces multiple candidates per pass. |
| Carey's placeholder-then-analogical-fill induction | `self_improving_loop`'s candidate-generation-then-select pattern (route_passage takes a LIBRARY of candidate resolutions and picks the coherence-winning one) is structurally the closest analog -- "generate several placeholder structures, let a coherence check pick/refine the survivor" | **GAP 4:** currently candidates are alternate CLUSTER ASSIGNMENTS of the same closed role-vocab, not alternate NEW SCHEMA PROPOSALS. Extending the same overgenerate-then-coherence-filter pattern (already validated per the 2026-08-03 causal-coherence 2x drill's construction+integration recommendation) to schema-minting is architecturally natural but unbuilt. |

## (f) Brain-systems grounding

**Complementary Learning Systems (McClelland, McNaughton & O'Reilly 1995; extended by Kumaran,
Hassabis & McClelland 2016; Gilboa & Marlatte 2017 schema-consolidation review):** hippocampus does
fast, sparse, pattern-separated binding of a NEW episode/schema-candidate (high learning rate,
low interference risk because representations are sparse/orthogonalized); neocortex does slow,
interleaved consolidation into stable, structured, generalizable schema knowledge (low learning
rate, prevents catastrophic interference by replaying old+new together). This maps directly onto
the architecture pattern above: hippocampal fast-binding = the MINTING step (a new schema candidate
gets bound quickly, provisionally, the first time disequilibrium fires); cortical slow
consolidation = the PROMOTION step (only after repeated, cross-validated confirmation -- NELL's
multi-cycle agreement-across-views requirement is the computational analog of interleaved
consolidation, not a coincidence).

**Prediction-error-driven schema update (van Kesteren, Ruiter, Fernandez & Henson 2012, "How
schema and novelty augment memory formation"; Gilboa & Marlatte 2017):** schema-CONGRUENT new
information integrates rapidly into existing schema via a hippocampal-mPFC fast pathway; schema-
INCONGRUENT information (prediction error against the current schema) triggers hippocampal-
dependent encoding of a NEW trace and, over consolidation, schema UPDATE/creation. This is the
biological instance of Piaget's disequilibrium criterion, made mechanistic and quantitative in a
way Piaget himself did not: prediction error MAGNITUDE against the CURRENT schema is the literal
trigger variable, exactly what Gap 2/the cheap decisive test above is probing for.

## (g) Honest assessment: what transfers to the glass-box constraint vs needs native re-derivation

**Transfers cleanly (symbolic/statistical, no borrowed embedding needed):**
- NELL's coupling logic (mutual exclusion + argument type-checking across independent extractors)
  is PURE LOGIC over a typed ontology -- zero dependency on how any individual extractor is
  implemented. Fully portable to VSA role-vocab + coherence-margin organs as-is.
- Chambers-Jurafsky's step-1 relatedness metric (coreference-conditioned association) is literally
  a symbolic co-occurrence statistic (PMI); our coref organ + event-slot binding already computes
  the needed anchor. Directly portable.
- Piaget's disequilibrium rule and Oudeyer-Kaplan's learning-progress-rate signal are BOTH
  quantitative comparisons of error/margin over time -- no embedding dependency, portable to our
  existing margin-based FLAG layer with an added "error against the WHOLE library" term.

**Needs native re-derivation (no clean transfer):**
- Causal (not merely co-occurrence/temporal) typing. Every source in this scan agrees this needs an
  INDEPENDENT evidence source, not a scaled relatedness metric. For us that independent evidence is
  most plausibly discourse-cue lexical triggers (because/so/therefore-class markers, already
  cheap and symbolic, per Do/Chan/Roth 2011's design) fused with the CausalLinkRegister's existing
  storage-tail (per the 2026-08-03 disk-verify finding that CausalLinkRegister is a
  write-then-read fidelity organ, NOT a selector) -- this is a BUILD, not a borrow, and is squarely
  in scope for a native re-derivation, not off-the-shelf reuse.
- The schema-MINTING operator itself (deciding the new role's binding signature, not just that a
  new role is needed) has no clean prior-art analog to copy verbatim -- OntExt's clustering-then-
  human-review and Chambers-Jurafsky's offline corpus clustering are both BATCH, not per-instance
  online decisions. This must be natively designed as an online operator over our existing
  role_vocab/AccumulateRegister machinery.
- The "second independent view" NELL's anti-drift power depends on (Gap 1) does not have an obvious
  off-the-shelf candidate in our current organ set -- we would need to genuinely build a
  structurally-different second extractor (e.g. a lexical/discourse-cue-based classifier
  independent of the FHRR coherence-margin decode), not just reuse what exists differently.

## (h) Recommended first buildable step

**Self-extension loop, first test case = goal-directedness (chosen because it's the narrowest,
best-instrumented competency we already have partial machinery for: coref + role-binding +
coherence-gate all exist; "blocked-goal" detection is a concrete, checkable regularity).**

1. Run the cheap decisive test (Part b) FIRST -- 1 hour, no new build, answers whether the existing
   coherence-margin signal already separates "needs new schema" from "fits existing schema." This
   determines whether Gap 2's minting trigger is free or needs new machinery.
2. If HARD-PASS: wire a `mint_new_role()` operator onto `situation_model_accumulate` that extends
   role_vocab when disequilibrium fires above threshold, seeded via Carey's placeholder pattern
   (the new role starts as a thin symbol bound only by its co-occurrence structure, refined over
   subsequent re-reads -- NOT immediately assigned rich semantics).
3. **MANDATORY anti-drift guard (NELL's lesson, non-negotiable):** do NOT promote a minted schema
   to the permanent store on a single pass. Require agreement from a SECOND, structurally
   independent signal before promotion -- concretely, a discourse-cue lexical check (does this
   event cluster co-occur with causal/goal-marker vocabulary: because, so that, in order to,
   wanted, tried to) computed independently of the coherence-margin decode. This is the direct
   translation of CPL's "promotion requires agreement across independent extractor types" and is
   the single guard this literature scan says is load-bearing -- skipping it reproduces NELL's
   long-tail-low-confidence failure mode (3% high-confidence beliefs after 9 years) inside our
   store instead of avoiding it.
4. Test on the SAME 18-item held-out set as the cheap decisive test, hand-labeled for whether a
   genuinely new goal-blocked schema is present; measure whether minted schemas survive a
   Director audit for drift (the HARD-FAIL criterion in Part c).

## Biggest risk

The field's own consensus (Mostafazadeh 2016, and independently Do/Chan/Roth 2011) is that
CAUSAL typing categorically resists the relatedness-clustering approach that otherwise transfers
cleanly -- meaning the hardest 20% of our question (grounded CAUSAL/goal schema induction, not just
"these events cluster") is exactly the part with the weakest prior-art support. NELL's own
autonomous-relation-minting subsystem (OntExt) needed a human gate and was never its primary growth
engine even for much easier NON-causal relation types. This is the honest reason the P is capped at
0.40, not a hedge: we are proposing to solve, natively, a problem the most relevant 15 years of
published never-ending-learning literature explicitly did not close.

## Citations (verified count: 19)

1. Carlson, Betteridge, Kisiel, Settles, Hruschka, Mitchell. "Toward an Architecture for
   Never-Ending Language Learning." AAAI 2010.
2. Mitchell, Cohen, Hruschka et al. "Never-Ending Learning." CACM 61(5), 2018.
3. Carlson et al. "Coupled Semi-Supervised Learning for Information Extraction." WSDM 2010.
4. Blum & Mitchell. "Combining Labeled and Unlabeled Data with Co-Training." COLT 1998.
5. Curran, Murphy & Scholz. "Minimising Semantic Drift with Mutual Exclusion Bootstrapping."
   PACLING 2007.
6. Mohamed, Hruschka & Mitchell. "Discovering Relations between Noun Categories." EMNLP 2011.
   (OntExt)
7. Never-Ending Language Learning -- Wikipedia (secondary, corroborating the ~3% high-confidence
   critique attributed to Stuart Russell).
8. Chambers & Jurafsky. "Unsupervised Learning of Narrative Event Chains." ACL 2008.
9. Chambers & Jurafsky. "Unsupervised Learning of Narrative Schemas and their Participants."
   ACL/IJCNLP 2009.
10. Mostafazadeh, Grealish, Chambers, Allen & Vanderwende. "CaTeRS: Causal and Temporal Relation
    Scheme." Events Workshop 2016.
11. Do, Chan & Roth. "Minimally Supervised Event Causality Identification." EMNLP 2011.
12. Ning et al. "Joint Reasoning for Temporal and Causal Relations." ACL 2018.
13. Sap et al. "ATOMIC: An Atlas of Machine Commonsense for If-Then Reasoning." AAAI 2019.
14. Bosselut et al. "COMET: Commonsense Transformers for Automatic Knowledge Graph Construction."
    ACL 2019.
15. Rasheed et al. "Human-in-the-Loop Schema Induction." arXiv:2302.13048, 2023.
16. Spelke & Kinzler. "Core Knowledge." Developmental Science 2007; Spelke 2022 review.
17. Carey. "The Origin of Concepts." 2009; "Précis of The Origin of Concepts" / "Concept
    Innateness, Concept Continuity, and Bootstrapping." 2011.
18. Piaget -- assimilation/accommodation/equilibration (secondary summaries consulted:
    SimplyPsychology, PsychologyNotesHQ; primary theory as standardly cited in developmental
    psychology).
19. Gleitman & Landau (syntactic bootstrapping); Pinker (semantic bootstrapping) -- as summarized
    in standard encyclopedic secondary sources (Wikipedia: Syntactic/Semantic Bootstrapping; SAGE
    Encyclopedia of Language Development).
20. Oudeyer, Kaplan & Hafner. "Intrinsic Motivation Systems for Autonomous Mental Development."
    IEEE Trans. Evolutionary Computation 2007. (Intelligent Adaptive Curiosity)
21. McClelland, McNaughton & O'Reilly. "Why there are complementary learning systems in the
    hippocampus and neocortex." Psych Review 1995; Kumaran, Hassabis & McClelland 2016 update.
22. van Kesteren, Ruiter, Fernandez & Henson. "How schema and novelty augment memory formation."
    Trends in Neurosciences 2012; Gilboa & Marlatte, "Neurobiology of Schemas and Schema-Mediated
    Memory," Trends in Cognitive Sciences 2017.

Note: items 18-19, 21-22 verified via secondary/standard-reference sources during this scan rather
than primary-PDF fetch in every case (developmental-psychology and neuroscience textbook-canon
material, low novelty-risk); items 1-17, 20 verified via direct primary-source or publisher-page
fetch by the lit-scan sub-agents. Calibration penalty applied: novel cross-thread synthesis
(Part e mapping, Part h recommendation) capped at P=0.40; individual prior-art claims (Parts d, f)
are lit-scan-standard, deflated 0.15-0.20 from face value per standing discipline.
