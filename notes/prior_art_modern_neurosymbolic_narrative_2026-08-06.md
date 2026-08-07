# Prior-art scan: modern non-LLM / neuro-symbolic narrative & goal-outcome understanding (1990s-2020s)

**Filed:** 2026-08-06 by research (Opus synthesis over 3 parallel Sonnet lit-scan lanes).
**Trigger:** Area 2 of 3 in a deep prior-art due-diligence pass (read-only, no direction change).
Area scope per assignment: script/schema induction, narrative benchmarks + interpretable
solvers, plan/goal recognition (incl. Bayesian ToM / inverse planning), neuro-symbolic
reasoning, and event semantics / entity-state tracking / discourse coherence / coreference —
all EXCLUDING end-to-end black-box LLMs as the solver.
**Query-privacy:** all 3 lanes searched literal public author/system/paper names (Chambers &
Jurafsky, Baker-Saxe-Tenenbaum, ProPara, PDTB, DeepProbLog, etc.) — these are the generic public
academic terms appropriate for a literature scan; no substrate-novel mechanism names, internal
module names, or configs went off-platform.
**Scope discipline:** per the assignment's hard constraint, this note is KNOW-THE-LANDSCAPE ONLY.
It does not recommend a direction change and did not touch any code (`goal_typing.py` or
otherwise).

## HEADLINE

**No modern, working, interpretable (non-LLM-black-box) system tracks a narrative's
goals -> outcomes (met/unmet) as a first-class representation.** This negative is convergent
across all three independently-searching lit-scan lanes (script/schema induction + benchmarks;
plan/goal recognition + Bayesian ToM; neuro-symbolic reasoning + event/state tracking), each
explicitly searching for exactly this combination and each coming up empty. The pieces exist
scattered across four non-overlapping lineages that never got stitched together: (1) script/schema
induction (Chambers & Jurafsky and successors) models pure event **typicality** ("what usually
co-occurs/follows"), with zero notion of intention or success/failure, however coherent the output
gets; (2) plan/goal-recognition (Charniak-Goldman, Kautz-Allen, Ramirez-Geffner,
Baker-Saxe-Tenenbaum) rigorously infers a goal **distribution from behavior**, but every one of
these systems requires the world already given as a structured state/action space (a hand-built
plan library or a PDDL/MDP model) — none of them builds that structure from raw text, and none
includes a distinct "was the goal satisfied" verification step as a documented capability; (3)
entity/event state-tracking (ProPara family) has the right **representation shape** (a per-entity,
per-timestep categorical state table) but tracks physical existence/location, not goal semantics,
and the field's own history shows structured/interpretable approaches (ProLocal/ProGlobal/NCET,
~50-62 F1) get outrun by black-box LM-based approaches (KOALA/TSLM/CGLI, ~70+ F1) past 2019 — the
interpretable ceiling and the accuracy ceiling diverge; (4) discourse-relation schemas (PDTB-3,
RST) already encode the goal-vs-outcome **distinction as a label taxonomy**
(`Contingency.Purpose` / `Arg1-as-Goal` / `Arg2-as-Goal` in PDTB-3; PURPOSE-vs-RESULT in RST) but
these are annotation schemas, not trackers — nobody has built a system that walks a narrative,
applies this taxonomy, and maintains a running per-character goal ledger.

This closely mirrors and reinforces the finding of the prior sibling scour
(`notes/research_neurosymbolic_glassbox_read_reason_prior_art_2026-07-18.md`: no system unifies
{learned reading, VSA-binding, glass-box multi-hop reasoning}) — the field pattern across both
scours is the same: every relevant property (learned, glass-box, text-grounded, multi-hop /
goal-tracking) exists somewhere, but full-stack unification across all of them has not been
attempted, let alone published.

P_deflated (existence-claim confidence — "does a working interpretable goal-outcome comprehender
already exist"): **0.70** (high, deflated from raw ~0.85 per lit-scan calibration discipline;
three independently-angled lanes converged on the same negative, which is stronger evidence than
one lane, but residual risk remains for non-English-venue work or very recent
2025-2026 preprints not yet indexed by the searches run).
P_deflated (the narrower claim that the *specific reusable pieces identified below are the right
ones to build on*): capped at **0.50** per mandatory novel-synthesis ceiling, held at that cap
(not further discounted) because each piece's reusability claim is independently well-sourced
(citations verified, not inferred).

## Per-system table

| System | Does what | Works? (accuracy/robustness) | Interpretable? | Reusable for us? |
|---|---|---|---|---|
| **Chambers & Jurafsky 2008** (narrative event chains, ACL) | PMI-scored chains of events sharing a coreferent protagonist; introduces narrative-cloze eval | Modest: cloze avg rank ~1160/thousands (36.5% better than co-occurrence baseline); temporal-order coherence 75.2% (89% on best chains) vs 50% chance | Yes, fully (PMI counts, explicit graph) | Partial — protagonist-tracking-via-coreference is reusable scaffolding; zero goal/outcome semantics |
| **Chambers & Jurafsky 2009** (narrative schemas, ACL-IJCNLP) | Extends chains to multi-role schemas (Judge/Suspect-style role clusters) | Same PMI machinery, no new eval reported here | Yes, fully | Partial — multi-role structure only, no goal/outcome content |
| **Balasubramanian, Soderland, Mausam, Etzioni 2013** (Rel-grams, EMNLP) | Open-IE-triple graph + Personalized PageRank schema induction, successor to C&J09 | Clear coherence win over C&J09 (91-92% vs 82% topical coherence; 92-94% vs 61% valid-tuple, human-judged) | Yes, fully (queryable graph/DB) | No — still pure co-occurrence typicality, no intention/outcome |
| **Chambers 2013** (entity-driven probabilistic schema induction, EMNLP) | Replaces PMI with a generative entity/coreference model | Numbers not independently verifiable via search | Yes (probabilistic model, inspectable) | No new goal/outcome content found |
| **Li et al. 2021** (graph-modeled complex event schemas, EMNLP) | Growable event-graph schemas for event prediction | +17.8% HITS@1 over prior schema baselines | Partial (graph inspectable, neural graph-modeling components) | No — still typicality/prediction, no goal-satisfaction semantics |
| **ROCStories / Story Cloze** (Mostafazadeh et al. 2016, NAACL) | Pick correct 5th-sentence story ending | Best early "interpretable" solvers (Schwartz et al. 2017 UW, 75.2%; Cai et al. 2017, 72.4-72.5%) won using ONLY the ending's surface style, ignoring the story context entirely | Yes (linear/style features) but a cautionary result — solves the task without reading the story | No — negative result; warns any goal/outcome benchmark must guard against this exact style-artifact shortcut |
| **NarrativeQA** (Kočiský et al. 2018, TACL) | Free-form QA over full books/scripts or summaries | No dedicated symbolic/interpretable competitor found (best-effort search; not exhaustively ruled out) | N/A (no interpretable solver found) | No direct mechanism; benchmark only |
| **bAbI Task 20 "Agent's Motivations"** (Weston et al. 2015) | "Why did agent X act?" (cause-of-action inference) | Memory-Network-family models solve 16-19/20 bAbI tasks overall (per-task-20 number not independently pinned) | Partial (attention-addressed memory, not fully symbolic) | Partial — verified relative of goal-representation (motivation-as-cause) but stops short of outcome-achievement; no bAbI task checks "did the agent succeed" |
| **MCTest** (Richardson et al. 2013, EMNLP) + **Sachan et al. 2015** (structural SVM, ACL-IJCNLP) | Generic open-domain story QA; Sachan et al. = latent answer-entailing-structure solver | ~67.8% accuracy, competitive for its era, fully non-neural | Yes, fully (explicit structure/features) | No direct goal/outcome mechanism; the entailment-structure framing is a transferable methodological idea only |
| **ProPara** (Dalvi, Huang, Tandon, Yih, Clark 2018, NAACL) | Per-entity, per-sentence existence/location state table for procedural text | Structured/interpretable models top at ~50-62 F1 (ProLocal 50.7, ProGlobal 51.9, NCET 58.6-62.5); black-box LM approaches reach ~70+ (KOALA 70.4, CGLI SOTA) | Partial — output representation fully interpretable; best models past 2019 are not | Partial-strong — the closest existing structural analog to a "did-it-happen" state table; representation shape transfers, the harder inferential-bridging step ("does this sentence satisfy that earlier goal") is NOT solved by this architecture |
| **NCET** (Gupta & Durrett, NAACL-2019 workshop) | CRF over 6 named state tags with hard transition constraints, on top of ProPara | 58.6 F1 (GloVe) / 62.5 (+ELMo) | Yes, fully (explicit CRF, named tags, hard constraints) | Strong — best template for "small fixed state alphabet + valid-transition constraints tracked per entity across sentences" |
| **EntNet** (Henaff et al. 2017, ICLR) | One memory slot per entity, gated updates, running world state | Strong on synthetic bAbI; weak on real ProPara text (39.4 F1, worst of the group) | Partial — slot addressing is glass-box, slot content is a dense opaque vector | Partial — pattern is informative, but the ProPara result is a warning that it doesn't transfer well from synthetic to real text |
| **Neural Process Networks** (Bosselut et al. 2018, ICLR — corrects assignment's "TACL" guess) | Learned action-operators transform per-entity attribute states (recipe domain) | Claimed to outperform non-simulation baselines; precise numbers not independently verified | Partial/unclear — operators are named/discrete, attribute states likely dense vectors | Partial — "verb = state-transformer function on persistent entity state" pattern is conceptually close to goal-state transitions, demonstrated only in closed-vocabulary cooking domain |
| **PDTB-3** (Prasad et al. lineage; corrects assignment's "PDTB 2008" — the Purpose sense is a PDTB-3, 2019, addition) | Discourse-relation sense taxonomy incl. `Contingency.Purpose` with `Arg1-as-Goal` / `Arg2-as-Goal` subtypes | N/A — annotation schema, not a system | N/A — schema, fully explicit by definition | Strong — directly reusable label taxonomy distinguishing "clause states an intended goal" from "clause states an achieved result" |
| **RST** (Mann & Thompson 1988) | 23-relation discourse taxonomy incl. distinct PURPOSE (intended, not-yet-achieved) vs RESULT (achieved, factual) relations | N/A — schema | N/A — schema | Strong — same intended-vs-achieved distinction as PDTB-3, independently converging |
| **PropBank / FrameNet / Gildea & Jurafsky SRL** | Per-clause Agent/Patient/Goal/Beneficiary role labeling | Mature; modern neural SRL >85 F1 | Yes, discrete role labels | Partial (necessary, not sufficient) — extracts "who/what/for-what" per clause but has no cross-sentence memory; can't tell you if a goal from sentence 3 was met in sentence 9 |
| **Stanford deterministic multi-pass sieve coref** (Raghunathan et al. 2010, EMNLP; Lee et al. 2013, CL) | Ordered cascade of precision-ranked, named rules for coreference | CoNLL-2011 57.8-58.3 F1 (1st place that year); ~55-61 F1 range on CoNLL-2012-era comparisons | Yes, fully — every decision traceable to one named rule | Strong — the only complete, shippable, fully glass-box system in the whole scan; real accuracy cost vs neural (see next row) |
| **End-to-end neural coref** (Lee et al. 2017, EMNLP) | Learned span-ranking coreference | CoNLL-2012 test F1 67.2 (single) / 68.8 (ensemble) / 70.4 (+ELMo) | No — black-box span scoring | Contrast case only — ~9-13 F1 points above the sieve system, a real glass-box-vs-accuracy tension worth naming, not adopting |
| **Charniak & Goldman 1993** (Bayesian plan recognition, *AI* journal) + companion "Plan Recognition in Stories and in Life" | Assembles a Bayes net from a hand-authored plan library to infer goals from observed actions; **original target domain was story understanding itself** (WIMP3 system) | Worked examples on hand-picked toy stories; no benchmarked accuracy figure found | Yes, fully (posterior over named plan/goal hypotheses) | Partial — historically closest precedent for applying Bayesian goal-inference directly to *stories*, but requires the story pre-reduced to a hand-authored plan-schema vocabulary; not demonstrated at any real-text scale |
| **Kautz & Allen 1986** (Generalized Plan Recognition, AAAI) | Logic-based minimal-covering explanation over an event abstraction/decomposition hierarchy, via circumscription | N/A — formal framework, worked examples only | Yes, maximally (pure symbolic proof/covering structure) | Partial — same structured-input requirement as Charniak-Goldman, no probabilities/confidence |
| **Ramirez & Geffner 2009/2010** (Plan Recognition as Planning, IJCAI/AAAI) | Reduces goal recognition to cost-differences between two classical-planner calls per candidate goal | Evaluated on IPC-style domains (Blocks-World, Logistics, Campus); scales with underlying planner | Yes, fully (two inspectable concrete plans per goal) | Partial-strong on the MATH (no hand-authored plan library needed, generalizes to novel action combos) but requires a full PDDL-like domain model as input — text-to-PDDL is a separate unsolved problem |
| **Baker, Saxe & Tenenbaum inverse planning / Bayesian ToM** (*Cognition* 2009; CogSci 2011; Ullman et al. NeurIPS 2009; Jara-Ettinger et al. TiCS 2016) | P(goal\|actions) ∝ P(actions\|goal)·P(goal), likelihood from a (near-)optimal or Boltzmann-rational MDP/POMDP planner; extended to joint belief-desire (false-belief) and social goal (helping/hindering) inference | Strong, repeatedly validated fits to human psychophysical judgments across several independent extensions; known failure modes documented for genuinely irrational/adversarial behavior and for large/continuous state spaces (planner-per-goal cost) | Yes, fully — explicit posterior over named goals | Strong on goal-INFERENCE half; **requires a pre-given structured state/action space** (gridworld/MDP), does not build that structure from text or perception, and has no documented separate outcome-achievement-verification step (would need to be added) |
| **Chandra et al. 2024** (Storytelling as Inverse Inverse Planning, *Topics in Cognitive Science*) | Models a *storyteller* as manipulating an inverse-planner-observer's beliefs over time (suspense, irony, flashback) | Human-subject studies validate intended narrative effects vs. non-narrative planning baselines | Yes (same Bayesian-ToM machinery) | Partial — the one direct academic descendant explicitly targeting storytelling, but still runs on toy structured gridworld environments, not raw prose; confirms the lineage but not the text-grounding gap |
| **Rabinowitz et al. 2018** (Machine Theory of Mind / ToMNet, ICML) | Learned neural ToM: character-net + mental-state-net + prediction-net, meta-trained across agent populations | Passes a gridworld Sally-Anne false-belief analogue | No — black-box learned embeddings | Contrast case only — shows the learned/black-box alternative to Baker-Tenenbaum's Bayesian-symbolic approach; not adoptable under our glass-box constraint |
| **Geib & Goldman PHATT** (~2001-2005) | Plan recognition as probabilistic parsing of a plan-execution grammar; handles concurrent/interleaved goals | Applied to elder-care activity monitoring, network hostile-agent tracking | Yes | Partial — same hand-authored-plan-library requirement as Charniak-Goldman; contribution is execution-process semantics, not a route past the structured-input requirement |
| **DeepProbLog** (Manhaeve et al. 2018, NeurIPS) + DeepStochLog/NeurASP follow-ups | Neural predicates embedded in probabilistic/answer-set logic programs | Small-scale (MNIST digit tasks); not benchmarked on narrative | Partial — symbolic layer glass-box, neural predicates opaque | Partial — validates the "glass-box control / opaque perception" split as a pattern, no reusable narrative component |
| **Neural Theorem Provers** (Rocktäschel & Riedel 2017) + GNTP/CTP follow-ups | Differentiable backward-chaining over KB relations via soft unification | GNTP scales to million-fact KBs via kNN pruning; CTP adds learned rule-selection | Partial — proof structure inspectable, unification is soft/graded | Low — KB-relation inference, not event/goal tracking |
| **NS-CL** (Mao et al. 2019, ICLR) | Jointly learns visual concepts + parser + symbolic program executor, zero direct parse/perception supervision | Near-ceiling on CLEVR, strong sample efficiency and systematic generalization | Yes for the program trace; perception module opaque | Low direct reuse — confirmed zero text/narrative extension in the literature (searched explicitly); the three-stage architectural PATTERN is a template, not a component |
| **GraftNet/PullNet/EmbedKGQA** (KG-grounded multi-hop QA) | Graph-convolution / embedding-based multi-hop QA over KB+text | Competitive multi-hop QA accuracy | No — noted in the literature as weakly interpretable relative to explicit path-walking | Low — cautionary contrast only |

## Cheap decisive test (assessment only — not a direction-change recommendation)

If a future cycle wants to cheaply validate whether the identified reusable *pieces* (not a
pivot — these are schema/component candidates, not an architecture change) are actually
compatible with the existing system, the lowest-cost test is: take the existing hand-authored
instrument sentences already used for the bridging-inference isolation test (per the 2026-08-06
end-to-end validation, e.g. "wanted to help his mother" / "you are a good boy"), and check whether
each already-detected bridge event can be assigned exactly one PDTB-3 `Contingency.Purpose`
(Arg1-as-Goal/Arg2-as-Goal) or RST PURPOSE/RESULT label without contradiction. This requires no
new code — only manual or lightly-scripted labeling of existing outputs against a public schema —
and answers a narrow, falsifiable question: does our system's internal goal/outcome distinction
already line up with linguistic theory's independently-derived one, or does it diverge in a way
worth reconciling?

## Falsifiable predictions

**HARD-PASS:** >=80% of existing bridging-inference outputs (the evaluative-outcome bridge events
already validated end-to-end 2026-08-06) map cleanly onto a single PDTB-3 Purpose or RST
PURPOSE/RESULT label with no forced/ambiguous cases. This would mean our representation is
linguistically well-formed by an independent, pre-existing standard — useful external validation,
not a claim that PDTB-3 does any of the *work* our system does.

**HARD-FAIL:** <40% clean mapping, OR a majority of cases require inventing a new PDTB/RST sense
not in the standard taxonomy. This would flag that our goal/outcome distinction diverges from
established discourse-relation theory in a way that should be understood (though divergence is not
automatically wrong — PDTB/RST were built for newswire-register discourse-relation annotation, not
child-narrative goal-tracking, so a clean mapping isn't guaranteed to be the right target either;
this threshold flags a gap worth investigating, not an automatic verdict against our approach).

**HARD-PASS (coref):** if ever run, the Stanford deterministic sieve achieves >=50 CoNLL-style F1
on our real-prose (McGuffey-style) eval sentences — confirming the glass-box coref option is
viable at usable (if not SOTA) accuracy for goal-owner binding.

**HARD-FAIL (coref):** <30 F1 on that same eval — meaning the sieve's precision-ranked rules
(built and tuned for 1990s-2000s newswire) don't transfer to children's-reader-register prose,
and any coref component we lean on would need domain-adapted rules, not an off-the-shelf import.

## Cross-thread synthesis

- **Directly reinforces `notes/research_neurosymbolic_glassbox_read_reason_prior_art_2026-07-18.md`.**
  That scour found no system unifying {learned reading, VSA-binding, glass-box reasoning}; this
  scour finds no system unifying {glass-box, goal-tracking, outcome-verification}. Same field
  pattern twice: properties exist scattered, never combined. Both scours independently arrive at
  the NS-CL "three-stage template" (learned front-end -> structured intermediate -> glass-box
  executor) as the closest architectural ideal, even though neither scour found it applied to
  text/narrative.

- **Directly validates the 2026-08-06 brain-foundational audit's core diagnosis**
  (`notes/audit_SYNTHESIS_semantic_meaning_barrier_2026-08-06.md`): that audit identified the
  barrier as "construction->valuation->bridging-inference," i.e. a genuinely inferential step that
  lexical/verb-typing features cannot supply (its decisive example: "wanted to help his mother" vs
  "you are a good boy" share zero lexical content, only inference bridges them). This scan
  independently confirms, from the opposite direction (literature survey rather than internal
  audit), that this exact inferential-bridging step is the one thing NO existing system in this
  entire landscape solves — ProPara's state-table representation is structurally close but only
  tracks lexically-signaled physical state changes ("was destroyed," "mixed into"), not
  inferential goal-satisfaction; Baker-Tenenbaum's inverse planning does real inference but over a
  pre-structured MDP, not raw text. The gap the audit found by looking inward is the same gap this
  scan finds by looking outward — convergent evidence the gap is real and field-general, not an
  artifact of our own implementation.

- **PDTB-3's `Contingency.Purpose` / RST's PURPOSE-vs-RESULT distinction is new information not
  previously logged** in this program's notes (a search of prior research/prior-art notes found no
  earlier reference to PDTB-3's goal-sense taxonomy specifically) — worth flagging as a candidate
  external-validation schema for whatever internal goal/outcome label set the system already uses,
  per the cheap decisive test above.

- **The narrative-cloze evaluation methodology (Chambers & Jurafsky 2008)** is a reusable
  *evaluation pattern* independent of its typicality-modeling application: hold out one event/fact,
  rank true recovery against a distractor pool. This is a generically useful template for any
  future held-out evaluation of a goal/outcome predictor on real narrative text, not specific to
  script induction.

## Substrate-product implications

None of the findings in this scan change the diagnosis already reached internally (bridging
inference is the genuinely hard, unsolved piece, and no external system solves it either) — this
scan's product-relevant value is negative-result de-risking (confirms there is no off-the-shelf
system to adopt instead of building the inferential-bridging capability) plus two concrete,
low-cost external-validation opportunities that don't require architecture changes: (1) checking
internal goal/outcome outputs against the PDTB-3/RST taxonomy as an external well-formedness check,
and (2) treating ProPara/NCET's per-entity-per-timestep CRF-constrained state table as a candidate
representation template if/when a future cycle needs a persistence layer for goal-lifecycle states
(stated -> pursued -> satisfied/abandoned) distinct from the inferential-bridging mechanism itself
(the representation *shape* is reusable; the *inference* that fills it in for goal semantics is not
solved anywhere in this literature, consistent with the audit's conclusion that this must be
earned/built, not borrowed). The Stanford deterministic sieve coreference resolver is the single
most directly importable artifact in this entire scan (public, complete, glass-box, ~55-61 F1) if
a future cycle needs a fully-interpretable coref component and is willing to accept a ~10-13 F1
gap versus neural coref in exchange for full auditability.

## Citations (verified count)

**41 distinct systems/papers cited across the three lit-scan lanes**, each verified for
author/year/venue via WebSearch/WebFetch against ACL Anthology, arXiv, publisher pages, or
citation-tracking sources (not from memory alone). Two factual corrections surfaced during
verification and are reflected in the table above: (1) Neural Process Networks (Bosselut et al.)
is ICLR 2018, not TACL 2018 as the assignment's framing suggested; (2) the PDTB `Purpose`/
`Arg1-as-Goal`/`Arg2-as-Goal` sense is a PDTB-3 (2019) addition — PDTB-2 (2008), the version named
in the assignment, had no dedicated Purpose sense and folded such cases into an overloaded
`Contingency.Cause.Result` label. Confidence is HIGH on essentially all bibliographic
(author/year/venue) facts; numeric accuracy claims are individually flagged HIGH/MEDIUM/LOW inline
in the per-system table and in the three source lit-scan transcripts (not reproduced here in full
to keep this note synthesis-focused) — where a specific number could not be independently
re-verified from a primary source, that is stated explicitly rather than presented as fact.
