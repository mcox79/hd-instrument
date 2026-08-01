# Persistent schema / consolidation / "is comprehension = model-building" — architecture drill (2026-08-01)

Research drill, Director-authored (no child agents), forward-architecture framing per task. Answers
the motivating question: does learning SCIENCE need a variant mechanism from reading-comprehension,
or is it the same engine plus (a) new relation-types and (b) a persistent-schema/consolidation layer
we don't yet have. KB-checked against `notes/comprehension_situation_model_frontier_scoping.md`
(situation-model design, in-flight) and `notes/consolidation_brain_fidelity_audit_and_redesign_2026-07-28.md`
(CLS/replay/schema-gate mechanism, already deeply drilled at the PER-CONCEPT relational-fact level).
This note does NOT re-derive that mechanism-level design — it extends it one level up: from
"consolidating one concept's mentions" to "consolidating a whole passage's situation model into a
domain schema," and it is the first drill to touch schema-REVISION (accommodation), the
model-building-universality question, and the causal/science-specific addition. Live web search run
(4 queries, generic cognitive-science terms only per query-privacy); citations below are freshly
verified this drill, not recalled-only.

## HEADLINE

The brain runs ONE engine (hierarchical predictive coding: build a generative model, update on
prediction error) at two timescales/stores — a TRANSIENT situation model in working memory per
episode, and a PERSISTENT schema in neocortex built by offline interleaved replay (CLS) — and the
SAME error-driven update logic governs both within-episode updating and cross-episode schema
revision, just gated differently (fast local overwrite in WM vs. slow replay-gated rewrite in
cortex, with a FAST-PATH shortcut when new input is schema-consistent). "Comprehension = model
building" is directionally right but not universal — it strains for procedural/motor skill and
pure statistical/associative learning, which don't obviously instantiate a propositional or
structural model even though they are formally consistent with free-energy minimization at the
sensorimotor level. Science/causal understanding is NOT a new engine — it is the same
error-driven schema-update machinery applied to a richer relation-type (causal, not just temporal/
spatial/social) plus an explicit hypothesis-generation-and-test loop (Bayes-net structure learning
over interventions) that narrative comprehension doesn't need. P_deflated = 0.40 for the "same
engine" unification claim (cross-thread synthesis of well-established but separately-studied
literatures, no single source states it this way); P_deflated = 0.30 for "CRP/MDL discovery gate
IS the same machinery as schema accommodation" (structural analogy, not demonstrated identity).

## 1. Transient situation model vs persistent schema — the two-store, one-engine picture

**Situation model (Kintsch/Zwaan/Radvansky, already in `comprehension_situation_model_frontier_scoping.md`):**
a working-memory-resident, per-text representation of entities/space/time/causation/intention,
built incrementally sentence-by-sentence and updated at "situational discontinuities." It is
volatile — it decays/is overwritten unless something promotes its content out of WM.

**Schema (long-term, cortical, domain-general):** an abstract associative/relational structure
(e.g., "restaurant script," "flavor-place map," eventually "Newtonian mechanics") built up over
MANY episodes, stored in neocortex, slow to change under the standard CLS account but capable of
FAST assimilation once mature (Tse et al. 2007, 2011 — flavor-place paired-associate task in
rats: once a schema existed, a single new trial's memory became persistent and rapidly
hippocampus-independent; PubMed 17412951, Science 2007 "Schemas and Memory Consolidation").
Follow-up work (Wang, Tse, Morris et al., "Anterior cingulate cortex in schema assimilation and
expression," PMC3407937) implicates vmPFC/ACC interacting with hippocampus and posterior
neocortex as the circuit that lets a prior schema accelerate encoding of schema-consistent new
material — i.e., there is a dedicated "does this fit what I already know" gate wired into the
consolidation circuit itself, not a post-hoc filter.

**How content moves transient -> persistent:** exactly the mechanism already drilled in
`consolidation_brain_fidelity_audit_and_redesign_2026-07-28.md` section 1 — hippocampal one-shot
binding, then OFFLINE interleaved SWR replay (Wilson & McNaughton 1994; Buzsaki), prioritized by
prediction-error/salience, captured into cortex via synaptic tagging (Frey & Morris 1997), with a
SCHEMA-CONSISTENT fast-path (Tse/Morris) that skips most of the slow replay dosage. That drill
already fully specifies the mechanism (`cls_discrete_budget_consolidate`, certified, HARD_PASS) at
the PER-CONCEPT relational-fact grain. The new piece this drill adds: the SAME replay+schema-gate
mechanism is the plausible substrate-analog for consolidating an entire SITUATION MODEL (not just
one concept's mentions) into the SCHEMA layer — the "item" being replayed/gated is a bound
relational structure (who-did-what-to-whom, or eventually a causal edge), not a single concept
vector. Nothing in the existing design forbids this generalization; it has just never been tried
at structure-grain instead of concept-grain.

**Trigger for consolidation:** repetition/consistency-across-episodes (does this situation-model
content recur or generalize across multiple read passages -> schema-worthy), plus offline
replay/sleep providing the compute budget, plus salience/prediction-error setting priority. This
is unchanged from the existing consolidation drill; restated here only because it is the load-bearing
answer to "what triggers consolidation" in the motivating question.

## 2. Schema revision — is it the same machinery as the discovery gate?

**Two failure modes a persistent schema must handle:** (a) new input EXTENDS an existing schema
(assimilation — cheap, schema-consistent, Tse/Morris fast-path) and (b) new input CONTRADICTS an
existing schema (accommodation — the schema itself must change). Classical developmental theory
(Piaget) named this distinction descriptively; the modern computational restatement is Bayesian
belief revision under the free-energy principle: perception/learning = continuously minimizing
prediction error by updating a generative model's parameters (assimilation, small posterior shift)
OR, when local parameter updates cannot reduce surprise below some threshold, revising the model's
STRUCTURE itself (accommodation) — the well-established "surprise drives belief update, large or
structural surprise drives model revision" claim (Bayesian-brain / free-energy literature: Corlett
et al. "Surprise and the Bayesian Brain," PMC6447687; general Bayesian-brain synthesis,
ScienceDirect S0306452224007048; Friston-line free-energy summaries, arXiv:1901.07945). Note the
"myth of the Bayesian brain" critique (PubMed 40569419) exists and should temper confidence — the
Bayesian-brain framing is contested as literally true neural computation vs. a useful abstraction;
treat "prediction-error-driven revision" as the ROBUST claim and "the brain literally computes
posteriors" as the CONTESTED claim.

**Does this unify with our planned discovery gate (CRP/MDL allocate-new-vs-reuse)?** Structurally,
yes, at the level of the DECISION RULE: both are "does the current structure explain this new
observation well enough (assimilate/reuse) or does a structural change pay for itself
(accommodate/allocate-new)" — a model-selection decision gated by a surprise/description-length
threshold. CRP is exactly a "new table vs join existing table" allocation rule keyed on a
concentration parameter; MDL is exactly "does adding a new component reduce total description
length enough to pay for its complexity cost." Schema accommodation in the neuroscience literature
is the SAME shape of decision applied to a persistent structure instead of a within-episode
entity-slot allocation. This is a strong STRUCTURAL analogy — not a demonstrated mechanistic
identity (no source in this drill claims hippocampal schema accommodation literally implements a
CRP or an MDL criterion; that mapping is our own synthesis). Cap this claim at P=0.30
(novel-synthesis cap already applies; deflate further because the analogy, while clean, has not
been tested against any brain data specifically designed to distinguish CRP/MDL-shaped allocation
from a generic threshold rule).

**What would make this a BUILD, not just an analogy:** if the SAME allocate-or-revise decision
function (with the SAME threshold-learning mechanism) governs entity-slot allocation in the
within-passage situation-model loop AND schema-level allocate-new-topic-node-vs-revise-existing-
node in the persistent layer, that is a strong glass-box economy argument (one gate, two grains) —
worth testing empirically once both layers exist, not before.

## 3. Is comprehension = model-building, universally? Honest boundary.

**Where it holds cleanly:** perception (predictive coding's original domain — visual/auditory
hierarchical inference), language comprehension (situation models, N400-as-prediction-error,
already grounded in `comprehension_situation_model_frontier_scoping.md`), causal/scientific
reasoning (section 4 below), and social cognition (theory-of-mind as generative-model-of-other-
agents, a well-established free-energy extension). The free-energy principle's own literature
explicitly frames itself as spanning perception, action, and learning as the SAME variational
objective (arXiv:2107.00140, arXiv:1901.07945) — this is the strongest form of the "it's all
models" claim and it is a genuinely broad, actively-defended research program, not a fringe view.

**Where it strains:** (a) PROCEDURAL/MOTOR skill — the free-energy literature DOES extend to motor
primitives (arXiv:2005.05151, motor-primitive learning as free-energy minimization; Friston's
active-inference account of motor control) but the "model" there is a low-level sensorimotor
forward model (predicted proprioceptive/kinesthetic consequences of action), not a propositional
or relational structure in any sense that resembles a "situation model" or "schema." Calling this
"the same kind of model-building" as narrative/causal comprehension is technically consistent but
practically stretches the word "model" to cover something architecturally very different (a
continuous-control forward model vs. a discrete relational structure) — arXiv:2301.05832's own
survey frames this as an open integration challenge ("frontiers and challenges"), not a solved
unification. (b) PURE STATISTICAL/ROTE learning (e.g., memorizing an arbitrary list, priming,
implicit statistical learning of transition probabilities) is also formally compatible with
"minimize prediction error over a generative model," but the "model" degenerates to a lookup/
frequency table with no structural content to speak of — at that limit "comprehension = model-
building" is true but VACUOUS (it says nothing more than "learning happens"), which is the honest
boundary: the FRAMEWORK is near-universal as a description of adaptive learning, but it stops
being an informative ARCHITECTURAL claim once the "model" has no structure worth naming. The useful
reading for substrate design: "comprehension = model-building" is a good GUIDING PRINCIPLE for
anything requiring RELATIONAL/PROPOSITIONAL structure (narrative, causal, scientific, social); it
should NOT be used to justify building a heavyweight schema/consolidation apparatus for tasks that
are genuinely rote or purely sensorimotor.

## 4. What does SCIENCE/causal understanding add beyond narrative situation models?

**Gopnik et al.'s "theory theory" / causal maps (Psychological Review 2004, "A Theory of Causal
Learning in Children: Causal Maps and Bayes Nets," philpapers/PubMed 14756583 verified this
drill):** children build an abstract, coherent representation of causal relations among events —
formally a directed graphical causal model (Bayes net) — and their causal learning from
observation/intervention is well-modeled by Bayes-net structure learning and inference. This is
explicitly framed by Gopnik as children (and by extension adults doing science) engaging in
scientific-like reasoning: hypothesis generation, evidence-driven structure revision, and,
critically, INTERVENTION (doing an action and observing the counterfactual-relevant outcome) as a
qualitatively different evidence source from mere co-occurrence.

**Answer: new relation-type on the same engine, not a new engine.** The causal-map account is
literally a graphical MODEL (nodes + directed edges + conditional structure) built and revised by
prediction-error-driven updating — the same "build a generative model, revise on error" logic as
section 2, applied to a relation-type (CAUSAL, directional, supports intervention/counterfactual
reasoning) that narrative situation models mostly do NOT require (situation models track temporal/
spatial/social/intentional relations; narrative causation is usually simpler, sequential "and then"
rather than a full interventionist causal graph). Three concrete additions science needs beyond the
narrative situation-model competency library:
  1. **A causal (directed, interventional) relation-type** — added to the growing competency
     library per the standing USER discipline (comprehension = growing library of construction
     competencies), same shape as adding "passive voice" or "coreference" competencies, just a
     harder relation semantics (supports do-calculus-style counterfactual queries, not just
     co-occurrence).
  2. **Abstraction/generalization over instances (induction)** — a causal MAP is by definition
     a structure that applies across many specific episodes (this fire causes this burn, in
     general, not just in this one story) — this is exactly the schema/consolidation layer's job
     (section 1-2), not a new mechanism: a causal schema is a schema whose edges are typed CAUSAL
     rather than typed ASSOCIATIVE/TEMPORAL/SOCIAL.
  3. **An explicit hypothesis-test loop for intervention-based evidence** — this is the one
     genuinely NEW functional piece (not present in passive reading comprehension): science
     involves ACTING to generate evidence (intervene, observe, update), not just READING and
     updating on what arrives. Architecturally this is still "generative model + prediction-error
     update" but the error signal now comes from a self-generated intervention rather than passive
     next-token/next-sentence prediction — closer to the active-inference (action-selects-observations)
     branch of the same free-energy literature (arXiv:1901.07945) than to pure perceptual predictive
     coding. This is the piece most likely to require new substrate machinery LATER (a query/probe
     interface into whatever environment supplies the "intervention" — irrelevant until the
     substrate has any actuation/query surface, correctly out of scope now).

**Bottom line for the motivating question:** science does NOT need a variant comprehension engine.
It needs (a) causal as a new relation-type in the same competency library, (b) the persistent-
schema/consolidation layer (needed anyway, not science-specific) generalized to typed-causal edges,
and (c) — later, not now — an intervention/hypothesis-test loop, which is a NEW input modality
(self-generated queries) to the same error-driven update logic, not a new update logic.

## 5. Glass-box design for the persistent schema/consolidation layer (forward architecture)

This is NOT a now-build (per task framing) — it is the roadmap's next frontier after the
in-flight situation-model work (`comprehension_situation_model_frontier_scoping.md`) lands. Design,
brain-faithful and inspectable:

**Two-tier store, reusing certified primitives, nothing new invented at the storage-mechanism
level:**
- **Tier 1 (transient, exists in the entity-slot design already scoped):** the per-passage
  situation model — a small set of addressable entity/relation slots in working memory, written by
  the learned content-gated write mechanism (`comprehension_situation_model_frontier_scoping.md`
  design A/C). Nothing here changes.
- **Tier 2 (persistent, the new layer):** a SCHEMA STORE keyed by topic/domain identity (not
  per-passage entity identity) holding typed relational structures (subject-relation-object edges,
  eventually causal-typed edges per section 4) accumulated ACROSS many passages. Consolidation
  from Tier 1 -> Tier 2 reuses `hdlab.hippocampal_encoder.cls_discrete_budget_consolidate`
  (already certified, HARD_PASS, `data/exp_cls_ca3complete_consolidation_v1/metrics.json`) exactly
  as already specified in `consolidation_brain_fidelity_audit_and_redesign_2026-07-28.md` section
  3 (offline discrete-budget SWR replay + CA3 completion + Hebbian write), generalized so the
  "item" being replayed is a bound relational EDGE extracted from a completed situation model,
  not a single concept-mention vector. The replay ORDER (surprise-first) and CAPTURE gate
  (schema-consistency-first) design from that note applies unchanged.

**The schema-REVISION gate (the genuinely new piece this drill adds):** when a newly-completed
situation-model edge CONTRADICTS (not merely extends) an existing Tier-2 schema edge for that
domain, the standard schema-consistency check (already spec'd: does the CA3-completed value agree
with the domain's existing relational neighborhood) returns LOW consistency for a DIFFERENT reason
than "novel-and-unrelated" (section 3 of the consolidation note only handled novel-vs-known, not
contradicts-known). The design extension: distinguish (i) novel-but-compatible (extend — normal
fast-track or slow-replay-then-write, existing design), (ii) novel-and-orthogonal (new schema node
— the CRP/MDL "new table" branch, needs the discovery-gate work to land first), and (iii)
directly-contradicts (revise — requires locating the SPECIFIC conflicting edge, not just checking
aggregate neighborhood consistency, and either overwriting it with a replay-weighted blend across
BOTH the old evidence and new evidence, mirroring accommodation, or flagging genuine ambiguity for
more replay dosage before commit). (iii) is the one case with no existing design and no existing
primitive — it needs a "find the specific conflicting edge, not just a consistency score" retrieval
step, which is a graph nearest-conflicting-edge query against Tier 2, not a new learning mechanism.

**One most tractable first piece, when this frontier is reached:** do NOT build the full
contradiction/revision machinery first. Build the Tier-2 SCHEMA STORE itself as a passive
consolidation target — reuse `cls_discrete_budget_consolidate` verbatim, feed it completed
situation-model edges (once Tier 1 exists and produces edges) instead of concept-mention vectors,
and measure whether cross-passage schema accumulation (assimilation only, extend-only case) shows
the same brain-signature (retains old schema edges while acquiring new ones under a fixed replay
budget, non-catastrophic) that the certified per-concept cell already showed. This is a pure WIRING
task (near-zero new mechanism risk, matching the "cheapest defensible next build" framing the prior
consolidation note already used for the concept-grain version) and it produces the substrate
artifact (an inspectable, queryable Tier-2 schema graph) that every later piece (revision gate,
causal relation-type, intervention loop) depends on. Contradiction-handling (iii above) is
correctly deferred — it requires Tier 1 (situation models) and passive Tier-2 consolidation both
proven first, and depends on the discovery-gate (CRP/MDL) work for the orthogonal-vs-contradicts
distinction.

## Cheap decisive test (for when this frontier is reached, not now)

Once Tier 1 (situation-model entity-slot design) lands and produces at least a few hundred
completed cross-passage relational edges: run the passive Tier-2 consolidation wiring (edges
in, `cls_discrete_budget_consolidate` unchanged, no revision gate) and measure schema-edge
retention (old-edge AUC after N new-passage cycles) vs. a no-consolidation control (edges just
overwritten/discarded each passage). HARD_PASS: retention gap >= the certified cell's own bar
(compare against its 0.913 gap as an upper reference, not a required match — any statistically
clear non-catastrophic retention under fixed replay budget counts) AND new-edge acquisition AUC
improves over passage-count (schema genuinely grows, not just retains). HARD_FAIL: retention
collapses to the no-consolidation control's level (wiring didn't transfer from concept-grain to
edge-grain) OR new-edge AUC is flat despite more passages (the flat-result-means-broken-experiment
discipline applies — diagnose before concluding a ceiling).

## Falsifiable predictions

- HARD-PASS (unification claim, section 2): if/when both Tier-1 entity-slot allocation and Tier-2
  schema allocate-new-vs-revise are built, a SHARED threshold/gate function governs both without
  degrading either's individually-tuned performance -> supports "one gate, two grains."
  HARD-FAIL: the shared-gate design underperforms two independently-tuned gates by a clear margin
  on BOTH layers' own held-out metrics -> the CRP/MDL-schema-accommodation analogy is structural
  resemblance only, not a shared mechanism; keep them separate, deflate this claim to near-zero.
- HARD-PASS (causal relation-type, section 4): a causal-typed edge added to the schema store, using
  the SAME consolidation/replay/gate machinery as associative edges, shows the SAME retention
  signature (no special-casing needed) -> "same engine, new relation-type" confirmed.
  HARD-FAIL: causal edges require a qualitatively different consolidation rule to avoid corruption
  (e.g., directionality gets scrambled by symmetric replay averaging) -> causal relations need a
  structural extension to the write primitive (asymmetric Hebbian, not the current form), a real
  but bounded new-mechanism cost, not a new engine.

## Cross-thread synthesis

Builds directly on, does not duplicate: `notes/comprehension_situation_model_frontier_scoping.md`
(Tier 1, in-flight) and `notes/consolidation_brain_fidelity_audit_and_redesign_2026-07-28.md`
(the CLS/replay/schema-gate mechanism this note's Tier 2 reuses verbatim, per WIRE-DON'T-ISLAND).
New material this drill contributes: the transient/persistent TWO-TIER framing as an explicit
architecture (prior notes each covered one tier), the schema-REVISION/contradiction gate (genuinely
unaddressed by either prior note, which both only handle novel-vs-known, not conflicts-with-known),
the "is comprehension=model-building universal" boundary analysis (motor/procedural/rote as the
honest limit), and the causal/science relation-type analysis grounding Gopnik's causal-maps account
directly against our own relation-type/competency-library discipline.

## Substrate-product implications

A user-facing "the substrate learned X and can tell you how" story becomes stronger with a visible
Tier-2 schema store: not just "it read this passage and understood it" (Tier 1, transient,
disappears) but "it has accumulated a durable, inspectable, growing model of topic Y across
everything it's read" — a directly demonstrable glass-box artifact (a queryable schema graph a user
can browse) that a black-box LLM cannot offer (no LLM exposes an inspectable persistent domain
model distinct from its opaque weights). This is a genuine product differentiator, not just a
research nicety, WHEN Tier 1 is solid enough to feed it — correctly sequenced as "next frontier,"
not now.

## Citations (verified count: 6 fresh this drill)

1. Tse, Langston, Kaag, Morris et al. — schema-consistent one-trial hippocampus-independent
   consolidation (Science 2007, PubMed 17412951; verified via WebSearch this drill).
2. Wang, Tse, Morris et al. — "Anterior cingulate cortex in schema assimilation and expression"
   (PMC3407937; verified this drill).
3. Corlett et al. — "'Surprise' and the Bayesian Brain: Implications for Psychotherapy Theory and
   Practice" (PMC6447687; verified this drill).
4. "The myth of the Bayesian brain" (PubMed 40569419; verified this drill — the contested-claim
   counterweight, used to bound confidence in section 2).
5. Gopnik, Glymour, Schulz, Kushnir, Danks — "A Theory of Causal Learning in Children: Causal Maps
   and Bayes Nets," Psychological Review 2004 (PubMed 14756583; verified this drill).
6. Free-energy-principle/active-inference surveys spanning perception/action/motor learning
   (arXiv:2107.00140, arXiv:2005.05151, arXiv:2301.05832; verified this drill — used for the
   universality-boundary discussion in section 3).

Plus prior-drill citations already verified/logged in `consolidation_brain_fidelity_audit_and_redesign_2026-07-28.md`
(McClelland/O'Reilly 1995, Marr 1971, Frey/Morris 1997, Wilson/McNaughton 1994, Diba/Buzsaki 2007,
Buzsaki 1989/2015) — not re-verified this drill, carried by reference per that note's own caveat.

P_deflated summary: "same engine, two-tier/two-timescale" unification = 0.40. "CRP/MDL discovery
gate = schema accommodation gate" structural identity = 0.30 (novel-synthesis cap applied).
"Comprehension = model-building" as a universal claim = 0.55 for the FRAMEWORK (well-supported,
actively-researched) but explicitly bounded/non-universal as an ARCHITECTURAL claim (motor/rote
boundary, section 3) — do not read the framework-level number as endorsing "build one mechanism for
everything."
