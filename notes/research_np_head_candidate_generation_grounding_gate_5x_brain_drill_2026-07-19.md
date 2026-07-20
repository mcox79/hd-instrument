# BRAIN-DRILL (5x): NP-HEAD-FINDING / ARGUMENT-HEAD CANDIDATE GENERATION — grounding-gated glass-box design

**Date:** 2026-07-19. **Filed by:** research (3 parallel Sonnet lit-scans + director synthesis).
**Trigger:** direct USER 5-angle brain-drill on the VET-confirmed break-0.50 bottleneck: the LCCP
argument-structure parser's CANDIDATE GENERATION step (not the reranker, not coref, not factorization)
proposes wrong-token heads — non-entities like `fields`/`regular`/`bank`/`table` — that no downstream
component can fix because the correct head was never in the candidate set. Confirmed directly in code:
`experiments/exp_attachment_coref_lever_lccp_break050_v1.py` already isolates and flags this exact failure
mode as `CANDIDATE_GEN_JUNK` (`is_junk_agent()`, line ~142) — "non-entity token the coref/deixis overlay has
NOTHING to resolve (candidate-generation loss)" — and explicitly localizes residual error to LCCP candidate
generation, not coref. That function currently uses a **hand-enumerated `FUNC_JUNK` blocklist**, i.e. a
closed, hand-authored list of known-bad tokens — not a principled, generalizing gate. This drill designs the
principled replacement.

Sits directly upstream of, and composes with, the same-day sibling drills
`research_learned_argument_structure_parser_5x_brain_drill_2026-07-19.md` (LCCP's Steps 1-6, which explicitly
**assumed** "reuse candidate generation as-is, do not discard it — the fix is in what happens AFTER" — this
drill shows that assumption needs a caveat: candidate generation itself has a real defect, not just a
missing learned-scoring layer on top of it) and
`research_coherence_schema_fit_gate_brain_drill_2026-07-19.md` (coherence gate as the training signal).
Also builds on `research_wm_barrier_glassbox_parsing_2026-07-17.md` (dependency stack) and
`research_classical_openie_glassbox_parsing_2026-07-17.md` (construction inventory).

Lit-scan calibration penalty applied throughout (deflate P 0.15-0.25 from raw literature-agreement;
novel-synthesis capped at P<=0.50), per [[feedback-lit-scan-calibration-penalty]].

---

## HEADLINE

**Two literatures converge on the SAME two-gate architecture, independently arrived at by separate lit-scans:**
(1) a cheap, high-recall **STRUCTURAL/positional gate** (X-bar endocentricity, Collins 1999 head-percolation,
open-class-vs-closed-class category filtering, Xue & Palmer 2004's walk-up-the-tree constituent pruning,
99.3% recall) that excludes tokens by **grammatical position and category**, and (2) a **GROUNDING/entity-hood
gate** (semantic bootstrapping — Pinker 1984/Grimshaw 1981 — plus concreteness norms — Brysbaert, Warriner &
Kuperman 2014 — plus WordNet hypernym-root distance to `physical_entity` vs `abstraction`) that excludes
tokens by **semantic type**, independent of position. **Critically, these two gates catch DIFFERENT failure
subclasses of the task's own named examples:** `regular` (an adjective/non-entity-concept token — WordNet
gives it no strong concrete-noun sense) is a **Gate-2 (grounding) failure**; `fields` and `table` (genuine,
concrete, WordNet-groundable common nouns, just occupying the WRONG constituent/dependency position for this
verb's argument slot — e.g. object of an adjunct PP, not the verb's true argument) are **Gate-1 (structural
position) failures that a grounding gate alone cannot catch**, because WordNet would happily classify
`table` as a `physical_entity`. **A single-gate fix (grounding-only OR structural-only) will not close the
whole residual; both gates are structurally necessary and non-redundant.** No published source combines
WordNet-hypernym-root-based hard gating with structural head-position pruning as a joint pre-candidate
filter — this specific combination is genuine novel-synthesis (each sub-agent independently flagged this),
capped at P<=0.50.

**Ranked brain mechanism (name it): the SEMANTIC-BOOTSTRAPPING / ENDOCENTRIC-HEAD CASCADE** — a structural
head-position bias (X-bar endocentricity, present from the earliest parsing) operating in parallel with a
concept-type/entity-hood gate (semantic bootstrapping's known-word-meaning constraint on candidate
referents), with selectional preference (Resnik 1996) and animacy-prominence (Bornkessel-Schlesewsky eADM)
as SOFT re-rankers layered on top of the surviving candidate set, not as replacements for the two hard gates.
Deflated P=0.45 that this exact two-hard-gate-plus-two-soft-rerank layering is the correct brain-faithful
target (component literatures individually sit at P~0.55-0.70; the specific WordNet-hypernym-as-hard-gate
engineering move is novel-synthesis, P<=0.50).

---

## Angle 1 — Headedness in syntax + acquisition

**Mechanism:** X-bar theory (Chomsky; Jackendoff 1977): endocentricity — every phrase XP is headed by a word
of category X that determines the phrase's category/distribution/agreement. Dependency grammar (Tesnière
1959, *Éléments de syntaxe structurale*): asymmetric governor→dependent arcs, with the verb as central node;
Tesnière's *actants* (obligatory arguments) vs *circonstants* (adjuncts) is the direct ancestor of
argument-vs-adjunct theory. Computationally, Collins (1999 thesis, Appendix A head-percolation rules): for
each phrase-structure rule, a hand-written priority table scans child categories (left-to-right or
right-to-left per category) to pick the head — a pure category-position filter, not semantic, widely reused
(Stanford CoreNLP's `CollinsHeadFinder`). Developmentally: determiners (closed-class) are distributionally
identified very early (pre-12mo sensitivity per corpus/statistical-learning studies), and children separate
noun-as-modifier from adjective-as-modifier even in identical prenominal slots — suggesting the
noun/adjective split is not purely positional but keyed to something like referentiality/kind-denotation,
foreshadowing Angle 2.

**Implication:** the wrong-candidate bug is exactly what X-bar endocentricity + Collins-style head rules are
built to prevent — a candidate proposer needs a **hard category-and-position gate keyed to constituent
structure/dependency-arc correctness**, not "any noun-tagged token nearby." This is the mechanism that
catches `fields`/`table`: even though both are grounded entity nouns, if they sit in an adjunct PP or a
different clause, a structural-position gate (not a semantic one) excludes them as candidates for THIS verb's
argument slot.

## Angle 2 — The grounding connection (core angle)

**Mechanism:** Semantic bootstrapping (Grimshaw 1981; Pinker 1984, *Language Learnability and Language
Development*): known conceptual content (object/entity concepts default to noun category; thematic roles
Agent/Patient/Theme map to grammatical relations Subject/Object) lets a child use ALREADY-KNOWN word meaning
to constrain candidate role-fillers — entity-hood/concept-type is diagnostic of nominal-argument status.
Concreteness norms (Brysbaert, Warriner & Kuperman 2014, *Behavior Research Methods*, 40k-lemma norms):
nouns average substantially higher concreteness than verbs; closed-class/function words rate lowest —
directly supporting concreteness-as-signal for entity-hood. Symbol grounding (Harnad 1990, *Physica D*,
independently fetched full text this session): elementary symbols are grounded via sensory/categorical
representations distinguishing REFERRING tokens from purely relational/functional glue — the clearest
theoretical ancestor of "some tokens denote real referents (candidate heads), others are relational glue
(non-candidates)." WordNet-hypernym-depth-as-abstraction-proxy is an established (if imperfect — only
MODERATE correlation with human concreteness ratings) NLP technique, and WordNet's noun hierarchy already
has a single root (`entity`) splitting into `physical_entity` vs `abstraction` (which further contains
attribute/relation/quantity — exactly the classes to exclude from head-candidacy).

**Gap found (both sub-agents independently converged on this):** no published work uses hypernym-root
distance / entity-vs-abstraction split as a **hard pre-filter removing tokens from the candidate set before
scoring** — the established computational precedent (Resnik 1996; Zapirain et al. 2013, *Computational
Linguistics* 39(3)) uses WordNet-derived selectional preference as a **soft ranking/classification feature
applied to already-identified candidates**, not a hard admission gate. The field's own history (Katz &
Fodor 1963's hard selectional restrictions abandoned in favor of Resnik-style soft preferences, because hard
filters proved too brittle for idiom/metonymy/metaphor) is a direct, honest warning against a purely hard
implementation of this gate.

**Implication:** `regular` (an adjective — no strong concrete-noun WordNet sense, or a null/low-concreteness
noun sense) is the failure mode THIS gate catches. Build it as **graded, not absolute**: WordNet
hypernym-root-to-`physical_entity` + concreteness score as a strong-but-overridable signal, not an
unconditional hard reject — flagged explicitly to pre-empt the brittleness failure mode the field already
discovered once (metonymy: "the White House announced..."; organizations/institutions that route through
`abstraction`-adjacent synsets like `group`/`social_group` yet are legitimate referential heads).

## Angle 3 — Candidate-space pruning (excluding non-heads)

**Mechanism:** Open-class (noun/verb/adjective/adverb, referring/contentful) vs closed-class
(determiner/preposition/auxiliary/conjunction, grammatical) is textbook-standard; one specific precedent
found: pronouns (closed-class) are explicitly carved out of "function word" exclusion sets in corpus work
BECAUSE pronouns can realize core argument positions — i.e. even within closed-class, referentiality is
graded, not binary. Katz & Fodor (1963, "The Structure of a Semantic Theory"): selectional restrictions as
hard semantic markers on a verb's arguments (e.g. "hit" requires [Physical Object] patient), abandoned later
for brittleness. Resnik (1996, *Cognition* 61) reformulated as information-theoretic selectional
ASSOCIATION over WordNet noun classes (soft, corpus-estimated). Animacy/prominence (Bornkessel-Schlesewsky's
extended Argument Dependency Model, "Two routes to actorhood," *Frontiers in Psychology* 2015): animacy acts
as an early, verb-INDEPENDENT prominence cue biasing Agent-role assignment toward the more animate candidate,
operating alongside, not instead of, selectional matching.

**Implication:** candidates should pass a CASCADE of independent, complementary filters, not one similarity
score: (1) hard category/position gate (Angle 1); (2) graded grounding/entity-hood gate (Angle 2); (3) soft
Resnik-style selectional-association re-rank over survivors; (4) animacy-prominence tie-break specifically
for the agent slot. Folding all four into one score is a likely reason a single-stage generator lets
`regular`/`fields`/`table`-type tokens through — the literature treats these as genuinely separate stages.

## Angle 4 — Learning head-hood / referentiality

**Mechanism:** Christodoulopoulos, Goldwater & Steedman (EMNLP 2010, unsupervised POS-induction survey):
word class (including the open/closed distinction) is recoverable from pure distributional/co-occurrence
statistics, no hand-coded category list required. Mintz (2003, *Cognition*, "frequent frames"): a
lightweight two-word context window around a target word reliably predicts grammatical category in
child-directed speech, with cross-linguistic replications (Chemla & Mintz; Erkelens on Dutch) showing
generalization with language-specific caveats. Determiner/plural-morphology co-occurrence is an established
distributional cue for count-noun/referential status (Reeder/Newport/Aslin; Frontiers 2017). Statistical
preemption/entrenchment (Ambridge et al., multiple 2012-2018 papers): over-generated erroneous forms are
suppressed by competing-form dominance (preemption) or repeated-non-occurrence (entrenchment) — but this
literature targets verb-ARGUMENT-STRUCTURE overgeneralization (wrong frames for a verb), not specifically
head-CANDIDATE exclusion; applying it to suppress specific recurring wrong-head proposals is an **analogical
extension, not established precedent** (both sub-agents flagged this gap independently).

**Implication:** a distributional/frequent-frame layer can supplement the WordNet-hard-gate for
out-of-vocabulary or novel nouns not covered by the grounded lexicon (a real, expected failure mode — WordNet
coverage is finite), and a preemption-style counter can, by direct analogy (not precedent), down-weight
specific hypernym-class-by-verb combinations that keep getting proposed but never confirmed by the coherence
gate — extending the sibling LCCP drill's Step-5 mechanism one stage earlier, to candidate generation itself.

## Angle 5 — THE DESIGN VERDICT

**Ranked brain mechanism, restated:** the SEMANTIC-BOOTSTRAPPING / ENDOCENTRIC-HEAD CASCADE — parallel hard
gates (structural-position + grounded-entity-hood) feeding soft re-rankers (selectional association,
animacy), improving with exposure via distributional referentiality learning (frequent frames) and
analogically-extended preemption suppression of specific recurring false candidates.

### Concrete design: the Grounding-Gated Head Cascade (GHC)

**Composes with, does not replace, existing components:** sits BEFORE the LCCP's existing cue-competition
scorer (from the sibling 07-19 drill) — GHC's job is to prune the candidate LIST that LCCP scores, not to
re-score it. Reuses the grounded word vectors (WordNet) already in the substrate as the lexicon GHC queries.
Directly REPLACES the current hand-enumerated `FUNC_JUNK` blocklist in `is_junk_agent()` with a principled,
generalizing gate (the blocklist approach cannot generalize to unseen junk tokens; the WordNet/structural
gate can).

**Gate 1 — structural/positional (hard, high-recall):** for each verb, walk the dependency/constituent path
from the verb outward (Xue & Palmer 2004-style: collect siblings along the path to the root, plus PP
children) to define the legal candidate CONSTITUENT SET before considering any token inside those
constituents; within each candidate constituent, apply Collins-style head-percolation (rightmost open-class
noun in English NPs) to pick the head token, excluding determiners/adjectives/prepositions from head-hood at
this stage purely by category and position. This is what catches `fields`/`table`-type failures (right word
class, wrong constituent).

**Gate 2 — grounding/entity-hood (graded, not absolute):** for each token surviving Gate 1, query the
grounded lexicon: does it have a noun sense whose hypernym chain roots in `physical_entity` (vs terminating
in `abstraction`'s attribute/relation/quantity branches), and what is its concreteness score if available? Use
this as a STRONG PRIOR (weight, not veto) favoring concrete/entity-rooted candidates and penalizing
adjective-only or abstraction-rooted tokens — graded specifically to avoid the field's own documented
brittleness failure (metonymy, institutional/organizational referents, idiom). This is what catches
`regular`-type failures (right position, wrong category/no entity sense).

**Gate 3 — selectional-association soft re-rank (Resnik-style):** over the surviving candidate set, score
verb-noun-class compatibility using the grounded lexicon's synset structure — moved EARLIER than the
classical literature applies it (classical SRL uses this only at classification time, per both sub-agents'
independent finding of a gap here) so it prunes/reweights the candidate list itself, not just the final role
choice.

**Gate 4 — animacy-prominence tie-break:** for the AGENT slot specifically, break remaining ties toward the
more animate/prominent surviving candidate (eADM).

**Step 5 — feeds LCCP unchanged:** the pruned, weighted candidate list is handed to the existing LCCP
cue-competition scorer (sibling drill) exactly as today, except the candidate set it operates over has
already had both classes of junk (wrong-constituent nouns, wrong-category non-entities) structurally removed
or down-weighted, rather than relying on the reranker to out-compete junk that should never have been a
candidate.

**Learning/improves-with-exposure layer:** (a) frequent-frame-style distributional referentiality tracking
supplements Gate 2 for tokens absent from the grounded lexicon (OOV nouns); (b) a preemption-style counter,
analogically extended from the sibling drill's per-verb mechanism, tracks (verb, hypernym-class) pairs that
Gate 2/3 keep admitting but the coherence gate never confirms, and down-weights that pairing over time — this
is the mechanism giving GHC a genuine learning curve, flagged as ANALOGICAL EXTENSION (P deflated
accordingly, see below).

---

## The FAIR can-fail test

**Real baseline:** the CURRENT `is_junk_agent()` / hand-enumerated `FUNC_JUNK` blocklist candidate generation
in `exp_attachment_coref_lever_lccp_break050_v1.py` — not a strawman, the system already measuring
`n_candidate_gen_junk` on this exact eval slice.

**Independent gold:** the 280-item LCCP gold + the assembled-cell scorer (per task brief) — never used to
tune GHC's gate thresholds.

**One variable per arm:**
- Arm A: current candidate generation (blocklist-based `is_junk_agent`), unchanged.
- Arm B: Gate 1 (structural/positional) only — isolates whether constituent/position pruning alone reduces
  `fields`/`table`-class junk, holding grounding fixed.
- Arm C: Gate 1 + Gate 2 (+ concreteness) — isolates whether adding the grounding gate reduces `regular`-class
  junk on top of B.
- Arm D: full GHC (Gates 1-4 + learning layer) — isolates the complete design, including the learning curve.

**HARD-PASS (junk reduction):** Arm D reduces `n_candidate_gen_junk` (the exact metric already instrumented
in the existing cell) by >=50% relative to Arm A on the independent gold, AND raises overall agent/patient
head precision by >=10 points, with recall cost (true heads wrongly excluded by the gates) <=5 points net.

**HARD-FAIL (junk reduction):** <15% reduction in `n_candidate_gen_junk`, or precision gain <3 points, or
recall cost exceeds precision gain (net negative) — would mean the two-gate hypothesis does not localize to
this specific failure mode as cleanly as the code-level flagging suggested, or the grounding gate's
brittleness (metonymy/idiom/OOV) dominates its benefit on real prose.

**HARD-PASS (gate decomposition, mechanism-validity check):** Arm B measurably reduces `fields`/`table`-CLASS
junk (structural-position errors on tokens WITH valid entity senses) specifically, while Arm C measurably
reduces `regular`-CLASS junk (category/non-entity errors) specifically, and the two reductions are
LARGELY NON-OVERLAPPING (confirming the headline's "different failure subclasses, both gates necessary"
claim) — cell author defines the exact overlap threshold.

**HARD-FAIL (gate decomposition):** the two gates' junk reductions overlap almost completely (either gate
alone recovers most of the full-design benefit) — would mean the two-hard-gate architecture is
over-engineered relative to a single simpler gate, and the design should be simplified before further
investment.

**Learning-curve measurement (Arm D vs C, required):** report junk-recurrence rate as a function of
cumulative exposure count for the preemption-layer extension. A flat curve falsifies the "improves with
exposure" claim for the learning layer specifically (independent of whether Gates 1-3's static reduction
HARD-PASSes).

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL, consolidated)

**Prediction 1 — Gate 1 (structural/position) reduces wrong-constituent junk (`fields`/`table`-class).**
P=0.50 (deflated; this is the most literature-precedented component — Collins head-percolation and Xue &
Palmer pruning are established, widely-reused techniques, not novel synthesis; capped at 0.50 per the general
novel-synthesis-application ceiling since it has never been validated on THIS specific eval slice).

**Prediction 2 — Gate 2 (grounding/entity-hood) reduces wrong-category junk (`regular`-class).**
P=0.40 (deflated further than Prediction 1: the hard-gate-from-hypernym-root move has NO direct literature
precedent as an admission filter — both sub-agents independently found only soft-scoring precedent for
WordNet-based selectional information — and the field's own history of abandoning hard selectional
restrictions for brittleness reasons is a specific, documented reason to expect this component to underperform
its naive-literature-agreement level).

**Prediction 3 — the two gates' benefits are largely non-overlapping (validates the "two distinct failure
subclasses" headline).** P=0.40 (deflated; a genuinely novel claim synthesized from the task's own examples,
not from any cited source — no literature directly tests this decomposition).

**Prediction 4 — the learning layer (analogically-extended preemption) shows a genuine negative-sloped
recurrence curve with exposure.** P=0.30 (most deflated; this is the least-precedented claim — Ambridge et
al.'s preemption/entrenchment literature targets a different phenomenon, verb-argument-structure
overgeneralization, not head-candidate exclusion; applying it here is analogy, not replication).

---

## Brain-check (outcome not pre-assumed)

**NP-head / argument-head identification IS a real, existence-proven brain capability** (children reliably
parse who-did-what across typologically diverse languages from noisy input with no negative evidence). Not a
capability gap in principle.

**Where the brain-check reveals a REAL, shared structural bound (same-limit, accept):** the field's own
documented history — Katz & Fodor's hard selectional restrictions were abandoned specifically because they
misfired on metonymy, idiom, and metaphor, replaced by Resnik's soft preferences — has a direct human-cognition
analog: comprehenders handle exactly these cases (e.g. "the White House announced...", "the ham sandwich
wants his check") via flexible, context-dependent TYPE COERCION (Pustejovsky's Generative Lexicon framework
for logical metonymy — not independently verified this session, flagged as recalled/secondary, but a
well-known account) rather than a rigid categorical gate. **This means a purely hard grounding gate would
create a failure mode that is NOT brain-faithful** — humans do not hard-reject "the White House" as a
candidate agent just because "White House" routes through institution/abstraction-adjacent synsets; they
coerce the reading. Gate 2 must therefore be built graded/overridable (a strong prior, not a veto), exactly as
specified in the Angle 2 design — this is a same-limit-honestly-checked finding: build the gate soft from the
start, don't discover the brittleness the hard way and patch later.

**Where the brain-check licenses a substrate-native departure:** an engineered system can run Gate 1's
structural/dependency-path pruning EXHAUSTIVELY and DETERMINISTICALLY over the whole sentence every time,
something the human parser approximates with fast, sometimes-error-prone heuristics (garden-path effects,
agreement attraction) under real-time/attentional constraints. There is no reason to bound Gate 1's coverage
to what a resource-limited biological parser could compute in real time — this is a place to be MORE
exhaustive than the brain, not merely faithful to it.

**Honest ceiling to carry forward:** per the task brief and the sibling LCCP drill, unsupervised/grounded
parsing sits ~40-70% accuracy on short sentences in the published literature; GHC should be judged against
the DELTA over the current blocklist-based candidate generation on this eval slice, not against an absolute
target borrowed from supervised, in-domain parsing.

---

## Cross-thread synthesis

This drill sits directly upstream of `research_learned_argument_structure_parser_5x_brain_drill_2026-07-19.md`
(same-day sibling): that drill's Angle 1 explicitly recommended "reuse the existing hand-rule reader's
candidate-generation step as-is — do not discard it, the fix is in what happens AFTER candidates are
generated." This drill's code-level confirmation (`CANDIDATE_GEN_JUNK` already flagged and measured in
`exp_attachment_coref_lever_lccp_break050_v1.py`) shows that assumption needs a caveat: the candidate-
generation step has a genuine, measured defect (the `FUNC_JUNK` blocklist misses `fields`/`regular`/`table`-
class errors entirely), separate from and upstream of the LCCP scoring-layer redesign that drill proposed.
The two designs are NOT in conflict — GHC prunes the list LCCP scores; LCCP's Steps 1-6 (cue-competition,
construction-level weight sharing, preemption retreat) are unchanged and now operate over a cleaner candidate
set. GHC's Gate 3 (selectional association) and Gate 4 (animacy) reuse exactly the cue-feature vocabulary
(verb-semantic-class fit, animacy) already specified as LCCP's Step 2 features — this drill supplies WHERE
those features should ALSO gate candidate admission, not just score already-admitted candidates. Also
connects to `research_wm_barrier_glassbox_parsing_2026-07-17.md` (Gate 1's dependency-path walk reuses the
same structural-memory/dependency-stack substrate) and `research_classical_openie_glassbox_parsing_2026-07-17.md`
(construction-typed candidate constituents).

## Ranked actionable anchors (delivered inline per no-routing-file discipline)

1. **[Primary, P=0.40-0.50 per-gate] Build + smoke the GHC Arms A/B/C/D ablation** directly inside/alongside
   `exp_attachment_coref_lever_lccp_break050_v1.py`'s existing `is_junk_agent()` measurement scaffold — it
   already computes `n_candidate_gen_junk` on independent gold, so this is the minimal-diff way to test GHC:
   replace the `FUNC_JUNK` blocklist call with Gate 1 (structural/position, Xue & Palmer-style constituent
   pruning + Collins-style head-percolation) and Gate 2 (WordNet hypernym-root + concreteness, graded not
   hard) in sequence, re-measure the same metric. See "The FAIR can-fail test" for arms/thresholds.
2. **[Secondary, cheap, run alongside anchor 1] Gate-decomposition check (Prediction 3):** confirm Gate 1 and
   Gate 2 catch largely non-overlapping junk-token classes on the independent gold, validating that both are
   structurally necessary (not redundant) before investing in the full 4-gate + learning-layer design.
3. **[Tertiary, contingent on anchor 1 HARD-PASSing] Learning-layer extension (Prediction 4):** only build the
   analogically-extended preemption counter for candidate-generation-level suppression once the static
   two-gate design is confirmed to help; do not build the learning layer first, since it is the least
   literature-precedented component.
4. **[Design constraint, zero-cost, applies regardless of test outcome] Gate 2 must be graded/overridable, never
   an absolute veto** — per the brain-check, a hard entity-vs-abstraction gate reproduces the exact
   brittleness (metonymy, institutional referents, idiom) that the field's own history (Katz-Fodor -> Resnik)
   already discovered and moved away from. Building Gate 2 as a hard reject would risk a HARD-FAIL driven by a
   known, avoidable failure mode rather than a genuine test of the grounding-gate hypothesis.

## Substrate-product implications

Not a publication angle — a build-priority and honesty angle. If GHC's Predictions 1-2 HARD-PASS, the
candidate-generation fix directly raises the ceiling on the reading-axis reader's real-prose precision without
any external LLM call or hand-enumerated blocklist — replacing a brittle, non-generalizing `FUNC_JUNK` list
with a principled gate that automatically extends to any word the grounded lexicon covers (a genuinely
differentiating, glass-box, zero-treebank property). If Prediction 2 (grounding gate) specifically HARD-FAILs
while Prediction 1 (structural gate) HARD-PASSes, the honest fallback is that the structural/positional fix
alone is worth shipping (it is the more literature-solid, lower-risk component), and the grounding gate needs
either a softer weighting scheme or a metonymy/type-coercion fallback (Pustejovsky-style) before it is
trustworthy — a real, incremental win, not a wasted cycle. If Prediction 3 HARD-FAILs (gates overlap heavily),
the honest simplification is to ship whichever single gate captures most of the benefit and defer the second
gate's added complexity.

---

## Citations (verified count)

**~28 distinct primary/named sources**, gathered via three parallel lit-scans this session (live web search;
flagged inline per sub-agent where recalled-from-training/secondary-sourced rather than independently
fetched): Chomsky/Jackendoff 1977 (X-bar theory); Tesnière 1959 (*Éléments de syntaxe structurale*); Collins
1999 PhD thesis (head-percolation rules; Stanford `CollinsHeadFinder` reuse); Grimshaw 1981; Pinker 1984
(*Language Learnability and Language Development*); Brysbaert, Warriner & Kuperman 2014 (*Behavior Research
Methods*, concreteness norms); Harnad 1990 (*Physica D*, symbol grounding — independently fetched full text
this session); Grimm & McNally (nominalization typology, fetch attempt 404'd, secondary-sourced); Katz & Fodor
1963 ("The Structure of a Semantic Theory"); Resnik 1996 (*Cognition* 61, selectional association); Zapirain,
Agirre, Màrquez & Surdeanu 2013 (*Computational Linguistics* 39(3), selectional preferences for SRL);
Bornkessel-Schlesewsky & Schlesewsky (extended Argument Dependency Model; *Frontiers in Psychology* 2015 "Two
routes to actorhood"); Christodoulopoulos, Goldwater & Steedman 2010 (EMNLP, unsupervised POS-induction
survey); Mintz 2003 (*Cognition*, frequent frames; Chemla & Mintz and Erkelens cross-linguistic follow-ups);
Reeder/Newport/Aslin (distributional subcategory learning); Ambridge et al. multiple 2012-2018 papers
(preemption/entrenchment, *WIREs Cognitive Science* 2013 review, PLOS ONE 2014/2015); Tomasello, Goldberg
(usage-based construction grammar, general characterization); Gildea & Jurafsky 2002 (*Computational
Linguistics* 28(3), two-stage SRL — argument identification vs classification); Xue & Palmer 2004 (EMNLP,
constituent-pruning algorithm, 99.3% recall); span-based SRL argument-pruning-network follow-on work
(AAAI, uncited specific paper, secondary); WordNet hierarchy structure (`entity` root, `physical_entity` vs
`abstraction` split; multiple independent search-confirmed sources); Pustejovsky's Generative Lexicon /
logical metonymy and type coercion (recalled/secondary, not independently fetched this session, flagged in
brain-check).

## Calibration

Per [[feedback-lit-scan-calibration-penalty]]: individual literature components (X-bar theory, Collins
head-finding, semantic bootstrapping, concreteness norms, selectional preference, animacy prominence) sit at
well-established textbook-to-strong-single-program confidence (P~0.55-0.70 each, not independently re-derived
from primary text in every case — several fetches 403'd/404'd and are search-snippet-level, flagged per
angle above). The SPECIFIC engineering synthesis this drill proposes — WordNet hypernym-root distance as a
graded ADMISSION gate ahead of structural constituent pruning, jointly, as a two-stage candidate-generation
pre-filter feeding an unchanged LCCP scorer — has NO direct literature precedent (both grounding-angle and
learning-angle sub-agents independently confirmed this gap) and is held at P<=0.50 per the novel-synthesis
cap, with the learning-layer extension (Prediction 4) deflated further to P=0.30 as the least-precedented
component (analogical, not replicated, use of preemption/entrenchment).

---

## VERDICT (one line)

**The brain does not use one head-finding mechanism — it runs a hard STRUCTURAL/endocentric position gate
(X-bar/Collins-style) in parallel with a graded GROUNDING/entity-hood gate (semantic bootstrapping +
concreteness), feeding soft selectional-association and animacy re-rankers — and the task's own two named
failure examples (`fields`/`table` = wrong-position errors on genuine entity nouns; `regular` = wrong-category
error on a non-entity token) map cleanly onto exactly these two DIFFERENT, NON-REDUNDANT gates, meaning a
single-gate fix cannot close the residual; the design (the Grounding-Gated Head Cascade, GHC) directly
replaces the current hand-enumerated `FUNC_JUNK` blocklist in `is_junk_agent()` with a principled,
generalizing two-gate filter feeding the existing LCCP scorer unchanged, with the single largest identified
risk (deflated P=0.40) being that a hard grounding gate reproduces the exact metonymy/idiom brittleness the
field's own history (Katz-Fodor -> Resnik) already discovered once, which the brain-check resolves by
specifying Gate 2 as graded/overridable from the start rather than an absolute veto.**
