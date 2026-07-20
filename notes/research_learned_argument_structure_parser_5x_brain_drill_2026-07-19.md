# BRAIN-DRILL (5x): LEARNED PARSING / ARGUMENT-STRUCTURE ASSIGNMENT — how the brain learns who-did-what-to-whom, and a glass-box learned-parser design

**Date:** 2026-07-19. **Filed by:** research (4 parallel Sonnet lit-scans + director synthesis). **Trigger:**
direct USER 5-angle brain-drill. Confirmed load-bearing bottleneck: the reader mis-attaches arguments in
grammatical-but-wrong ways ("came,boy,eyes"; "took,herbert,one"; "passed,it,harm") — plausible parses that
are simply wrong, which a coherence-gate cannot catch because they cohere. Directly upstream of, and
composes with, the sibling same-day drill `research_coherence_schema_fit_gate_brain_drill_2026-07-19.md`
(which found the brain's coherence-monitoring is itself split into a graded N400-style score + a discrete
P600-style structural-incoherence flag, and that "coherent-but-wrong" is a well-documented human failure
mode too — good-enough processing / Moses illusion). This drill asks the upstream question: how does the
PARSE that feeds the coherence gate get built correctly in the first place, and how is it LEARNED.

Also builds directly on `research_wm_barrier_glassbox_parsing_2026-07-17.md` (found: the missing lever is
incremental STRUCTURAL memory of open dependencies — a dependency-parser stack — not bigger buffer
capacity; content-addressable interference-aware retrieval is the separate, not-yet-built piece for
long-distance cases) and `research_classical_openie_glassbox_parsing_2026-07-17.md` (found: adopt a
ClausIE-style clause-typology parser for coverage; abstain-gate for precision; open-class relation
vocabulary, not a closed set).

Lit-scan calibration penalty applied throughout (deflate P 0.15-0.25 from raw literature-agreement;
novel-synthesis capped at P<=0.50), per [[feedback-lit-scan-calibration-penalty]].

---

## HEADLINE

**No single textbook mechanism does this — the brain runs a layered system, and the four literatures
converge on the SAME layering, independently.** (1) A universal, very-early (~15mo) STRUCTURAL bias maps
NP-count/position to participant-role count (syntactic bootstrapping, Gleitman/Fisher) and generates
candidate parses; (2) known word/argument SEMANTICS (animacy, causality) supplies a complementary cue that
converges with (1), not a rival account (semantic bootstrapping, Pinker; the two operate simultaneously
from early on, no clean hand-off age) (3) the surface cues (word order, case, animacy, agreement) then
COMPETE with LANGUAGE-SPECIFIC LEARNED WEIGHTS (Competition Model, MacWhinney-Bates) acquired via
exposure-driven, error-corrected reweighting — this weighting is neurally instantiated as a
prominence-weighted "actor-first" default (Bornkessel-Schlesewsky's Argument Dependency Model) that IFG
(Broca's area) overrides for non-canonical structures, and whose override capacity is exactly what fails in
agrammatic aphasia (chance performance on reversible passives specifically); (4) generalization to NOVEL
verb+frame combinations is NOT per-verb memorization but CONSTRUCTION-level abstraction built bottom-up from
item-based (Tomasello "verb island") exposure via type-frequency/Zipfian-skew schema induction (Goldberg,
Casenhiser); (5) overgeneralization is corrected NOT by negative evidence/treebank-style correction but by
purely distributional, exposure-driven RETREAT — statistical preemption (a competing correct form
repeatedly winning suppresses the erroneous one) + entrenchment + verb-semantic-class fit (Ambridge's graded
probabilistic account); and (6) the entire system's improvement signal, at the neural level, is a genuine
PREDICTION-ERROR signal (P600) that recent connectionist work (Fitz & Chang 2019) explicitly implements as
literal backpropagated error in a Dual-path network reproducing both N400 and P600 as instances of ONE
error-driven learning mechanism — i.e., **coherence-mismatch IS a brain-validated training signal for parse
revision**, not just an engineering convenience.

**Ranked brain mechanism (name it): LEARNED CUE-COMPETITION PARSING, scaffolded by usage-based
CONSTRUCTION ABSTRACTION for generalization, corrected via PREEMPTION/ENTRENCHMENT retreat, driven by a
genuine PREDICTION-ERROR (coherence-mismatch) learning signal.** Deflated P=0.45 that this specific
six-part layering is the correct brain-faithful target to build around (novel-synthesis capped; individual
component literatures sit higher, P~=0.55-0.70, see per-angle sections).

---

## Angle 1 — Syntactic + semantic bootstrapping (how the candidate parse itself is proposed)

**Mechanism:** Gleitman's syntactic bootstrapping (Gleitman 1990, *Language Acquisition*; Fisher & Gleitman
lineage): a universal structural bias maps each NP in a sentence onto a participant role in the underlying
event representation, so NP-count/position in the FRAME (not verb meaning) constrains the interpretation of
a novel verb. Naigles (1990, *J. Child Language*) — 25-month-olds shown simultaneous causal/non-causal
scenes with a novel verb in a transitive vs. intransitive frame look preferentially at the scene the frame
implies, syntax alone steering interpretation. Yuan & Fisher (2009, *Cognitive Psychology*) pushed this to
frame-only exposure via **overheard dialogue with no depicted scene** — children still used the stored
frame later, showing the cue is tracked and stored independent of simultaneous grounding. Onset ~15mo for
NP-role mapping (Fisher et al. 2020, *Topics in Cognitive Science*), ~21-23mo for systematic
transitive/intransitive use, ~28-30mo for distributional-pattern extraction from dialogue alone.
Complementary semantic bootstrapping (Pinker 1984, *Language Learnability and Language Development*; via
Grimshaw 1981): known conceptual content (agent/patient, animacy, causality) cues syntactic
category/structure — the mirror-image direction. Fisher/Gertner/Scott/Yuan (2010, WIREs Cog Sci) explicitly
frame the two as **complementary, operating simultaneously from early on, with no clean developmental
hand-off** — later work adds a scene-free, purely-distributional syntactic channel from ~28-30mo onward,
layered atop, not replacing, earlier scene-grounded bootstrapping.

**Learning signal:** NOT gradual associative accumulation for the core hypothesis-forming step. Trueswell,
Medina, Hafri & Gleitman (2013, *Cognitive Psychology*) propose **"propose-but-verify"**: one hypothesis per
exposure, confirmed or discarded (win-stay/lose-shift) on the NEXT occurrence — an explicitly error-driven,
per-exposure correction dynamic, not slow statistical drift.

**Implication for the learned parser:** the CANDIDATE-GENERATION step should be a cheap, universal,
structural NP-count/position → role-slot mapping (reuse the existing hand-rule reader's candidate generator
as-is — do not discard it), with a separate, LEARNED per-verb confirmation/disconfirmation trace updated by
propose-but-verify dynamics (one candidate proposed, confirmed/discarded against the next coherence-checked
outcome), not a batch-statistics update. **P=0.40** (deflated) that propose-but-verify, not gradual
Competition-Model reweighting, is the right update rule specifically for the FIRST-verb-exposure regime
(new verb, no prior weight) — the two mechanisms are not mutually exclusive; propose-but-verify may govern
cold-start, Competition-Model reweighting the steady state (see Angle 2).

## Angle 2 — The Competition Model, learned (cue-weight acquisition dynamics)

**Mechanism:** Bates & MacWhinney's Competition Model: interpretation cues (word order, animacy, case,
agreement, stress/prosody) COMPETE; each cue's strength = **cue validity = availability × reliability**.
Cross-linguistic sentence-interpretation experiments (Bates/MacWhinney/Sokolov 1984, and extensions to
Hungarian, Turkish, Japanese, Serbo-Croatian — verified this session across multiple independent sources)
show LANGUAGE-SPECIFIC learned weightings: English weights word order so heavily it overrides
animacy/agreement; Italian weights agreement extremely heavily; German weights agreement+animacy; Hungarian
weights case marking above all else even in young children; Japanese (flexible word order, frequent
case-marker omission) weights animacy instead, because case is statistically less reliable in practice there.
The **same cue TYPE (e.g. animacy) carries near-zero validity in one language and dominant validity in
another purely as a function of that language's own input statistics** — the weighting is learned, not
innate.

**Learning dynamics:** children first latch onto the most AVAILABLE (frequent/salient) cue regardless of
reliability, then gradually re-weight toward the more RELIABLE cue as evidence accumulates — a slow
reorganization, not an instant reset. MacWhinney's own connectionist simulations (from ~1989, English/
German/Hungarian) frame this as an error-driven, associative-strengthening process: cues whose use
correlates with successful/confirmed interpretation get strengthened, competing cues that predict incorrect
interpretations get weakened — closer to Hebbian/gradient error-correction + frequency tracking than to
explicit Bayesian updating (flagged: this specific learning-rule characterization is a secondary-source
synthesis, the primal 1989 paper's exact equations were not independently re-verified this session).

**Critiques:** insufficient neurobiological grounding in the original formulation; scaling to adult/L2
learning required MacWhinney's later "Unified Competition Model" patch (secondary sources).

**Implication for the learned parser:** cue-weight vectors should be attached to the CONSTRUCTION (see
Angle 3), not globally or per-verb, exactly mirroring how a language's word-order-vs-case weighting is a
property of the language's whole grammar, not of individual sentences. The weight-update rule should be
error-driven (cue strengthened when it led to a subsequently-CONFIRMED/coherent interpretation, weakened
otherwise) — this is the steady-state complement to Angle 1's cold-start propose-but-verify. **P=0.40**
(deflated) that error-driven cue-reweighting (vs. some other update rule, e.g. pure frequency-counting) is
the correct mechanism for a glass-box implementation — the human data strongly supports the OUTCOME (learned,
language-specific weights matching corpus cue-validity) but the exact update-rule mechanics are less firmly
pinned down in the literature than the outcome is.

## Angle 3 — Usage-based construction induction (generalization + retreat from overgeneralization)

**Mechanism:** Tomasello's Verb Island Hypothesis (1992, *First Verbs*): children's earliest argument-
structure knowledge is item-based (per-verb "islands"), with abstraction to construction-level schemas
(transitive = X-acts-on-Y) emerging gradually, not fully adult-like until ~3-4+ years (Tomasello 2000, 2003).
Abstraction driver: TYPE frequency (many distinct verbs occurring in one frame) rather than token frequency
of a single verb. **Important caveat, directly relevant here:** Ninio's "No Verb Is an Island" and
Pine/Lieven/Rowland (1998) show substantial inter-item transfer even in early syntax, and much of the
apparent "verb island" effect is organized around high-frequency pronouns/proper nouns rather than being
verb-specific — i.e., the strict item-based-only story is empirically weakened; some abstraction happens
earlier/more generally than Tomasello's strongest version claims. Goldberg's Construction Grammar (1995,
2006): argument-structure constructions are themselves independent form-meaning pairs (the caused-motion
construction supplies causation/motion meaning even for an intransitive verb like "sneeze," as in "she
sneezed the napkin off the table"). Casenhiser & Goldberg (2005): 5-6-year-olds learn a novel artificial
SOV construction's meaning fastest when exposure follows a **Zipfian-skewed type-frequency distribution**
(one high-frequency verb anchoring early exemplars, enabling "progressive alignment" generalization to
other verbs) — directly paralleling the Zipfian skew found in real child-directed speech.

**Overgeneralization + retreat** (the direct analog of "coherent-but-wrong" mis-attachments): classic errors
("don't giggle me," dative-alternation errors) are corrected via three converging, purely DISTRIBUTIONAL
mechanisms, none requiring negative evidence: (a) **statistical preemption** (Ambridge, Pine, Rowland 2012-
2018; Boyd & Goldberg 2011) — hearing the correct competing form in a context where the error would be
expected suppresses it; (b) **entrenchment** (Braine & Brooks) — repeated attested use in ONE construction
alone probabilistically strengthens "absence of evidence as evidence of absence" for the alternative; (c)
**verb-semantic-class fit** (Pinker 1989's broad-range/narrow-range rules; Ambridge et al.'s graded
probabilistic unification) — a verb's fine-grained semantic class constrains which constructions it may
enter, learned as a graded, not categorical, fit score. Ambridge, Pine, Rowland & Young (2008) show children
use verb-SEMANTIC-fit specifically (independent of raw frequency) to judge grammaticality of novel-verb
generalizations — i.e., the retreat signal includes a genuine "does this meaning make sense for this verb"
component, not just frequency counting.

**Implication for the learned parser:** cue-weights and role-templates should live at the CONSTRUCTION level
(clustered by distributional similarity of surface-cue profile + downstream coherence outcome), inheriting
across verbs — this is exactly what licenses compositional generalization to a HELD-OUT verb+construction
combination never jointly seen in training (the task's explicit generalization requirement). Retreat from a
specific mis-attachment (e.g., a coherent-but-wrong "came,boy,eyes" binding) should be implemented as
per-verb PREEMPTION/ENTRENCHMENT tracking: each time a competing candidate binding for the SAME verb gets
confirmed by downstream coherence instead, the erroneous cue-combination for that verb is measurably
suppressed — no explicit negative-evidence/treebank correction required. **P=0.40** (deflated) that
construction-level (not verb-level, not global) weight-sharing is the correct generalization unit for a
glass-box system — well-precedented in humans, untested whether an engineered symbolic system's clustering
step actually recovers the same construction boundaries without supervision.

## Angle 4 — Neural + error-driven mechanisms (what physically implements the competition and the error signal)

**Mechanism:** Left posterior MTG/pSTS carries lexical-semantic verb-argument representations (selectional
frames); left IFG (Broca's, BA44/45) supports syntactic combinatorics and is preferentially engaged by
NON-CANONICAL word order (object-relatives, passives, unaccusatives) — recent MEG/fMRI work (2024) suggests
posterior temporal cortex resolves structure earliest (~300ms), IFG engaged later (~500ms), consistent with
IFG's role being controlled OVERRIDE/reanalysis rather than first-pass structure-building. The default
"actor-first" heuristic (assume first-encountered NP = agent) is formalized cross-linguistically as
Bornkessel-Schlesewsky & Schlesewsky's Argument Dependency Model — a prominence-weighted default (animacy,
case, person, position all feed a single "actorhood" scale). Caramazza & Zurif (1976, *Brain and Language*)
— the classic heuristic/algorithmic dissociation: Broca's/conduction aphasics perform near-ceiling when
world-knowledge heuristics suffice, but drop to CHANCE specifically on REVERSIBLE passives (where only
syntax disambiguates) — Grodzinsky's Trace Deletion Hypothesis (1995, 2000) formalizes this as an inability
to represent syntactic movement traces, forcing a fallback to the linear/agent-first default. **This is the
single clearest biological demonstration that "override the default cue-competition winner" is a distinct,
separately-damageable capacity from "run the default competition at all."**

**Error-driven parse revision:** Friederici's ELAN→N400→P600 model; P600 ("monitoring theory") is
specifically framed as arising from a MISMATCH between expected and actual parse, triggering reanalysis —
a genuine structural prediction-error signal, not passive difficulty. Kuperberg & Jaeger (2016) frame
comprehension as hierarchical probabilistic prediction (predictive-coding-style) across semantic/syntactic/
phonological levels. **Most directly load-bearing finding for this drill:** Fitz & Chang (2019, *Cognitive
Psychology*), "Language ERPs reflect learning through prediction error propagation" — a connectionist
Dual-path model instantiates N400 as prediction error at the lexical/output layer and P600 as
BACK-PROPAGATED prediction error at the sequencing/hidden layer, successfully simulating garden-path P600
effects AND semantic-role-reversal anomalies as instances of ONE error-driven learning mechanism. **This is
the direct empirical bridge validating "coherence-mismatch as the training signal, not treebank labels" as
brain-consistent, not merely an engineering shortcut.**

**Developmental angle:** reanalysis ability itself develops (4-year-olds markedly worse than 5-year-olds/
adults at garden-path recovery) and improves with richer language exposure (bilingual/L2 literature: earlier,
richer naturalistic exposure improves garden-path revision vs. late/instructed learners) — i.e., reanalysis
is itself a LEARNED skill, consistent with the task's requirement that the parser "improves with exposure."

**Implication for the learned parser:** the OVERRIDE-the-default-competition-winner capacity (Angle 4's
IFG-analog) should be a distinct, separately-trainable component from the base cue-competition itself — this
directly explains WHY the current hand-rule reader's mis-attachments are "coherent but wrong": it likely has
only the equivalent of the actor-first/positional default (per the 07-17 WM-barrier note's finding that the
current pipeline is positional/flat), with no learned override mechanism for non-canonical cue
configurations. **P=0.45** (deflated, moderately well-precedented) that error-signal-driven weight updates
(the Fitz & Chang mechanism, generalized) are directly implementable as the update rule for both Angle 2's
cue-reweighting and Angle 3's retreat tracking — i.e., angles 2, 3, and 4 are NOT three separate mechanisms
but one error-driven update rule operating at three different granularities (cue-weight, construction-schema,
verb-specific-preemption).

---

## Angle 5 — THE DESIGN VERDICT: a glass-box LEARNED PARSER built around the ranked mechanism

**Ranked brain mechanism, restated:** LEARNED CUE-COMPETITION PARSING (the actor-first default +
language/construction-specific learned cue weights), scaffolded by USAGE-BASED CONSTRUCTION ABSTRACTION
(so weights generalize across verbs, not memorize per-verb), corrected via PREEMPTION/ENTRENCHMENT retreat
(so specific coherent-but-wrong mis-attachments get suppressed with exposure, no treebank needed), all
driven by a genuine PREDICTION-ERROR / coherence-mismatch learning signal (brain-validated by Fitz & Chang's
literal error-propagation implementation of N400/P600). This is the single mechanism-family that best
explains all four angles' convergent findings and is buildable directly on the existing substrate.

### Concrete design: the Learned Cue-Competition Parser (LCCP)

**Composes with, does not replace, existing components:**
- Reuses the existing hand-rule reader's candidate-GENERATION step as-is (Angle 1's structural NP→role
  mapping bias is cheap and universal — do not discard it; the fix is in what happens AFTER candidates are
  generated, not in generating them).
- Reuses the incremental structural-memory / dependency-stack recommendation already landed in
  `research_wm_barrier_glassbox_parsing_2026-07-17.md` — the stack of open dependencies is the SAME
  structural substrate the LCCP's candidate set operates over; this drill's contribution is the LEARNED
  scoring/selection layer riding atop that stack, not a competing architecture.
- Reuses the validated structure-content factorization / role-filler binding (the additive_map compositional
  readout) as the downstream consumer: LCCP's job is only to pick WHICH candidate binding wins; the binding
  representation itself is unchanged.
- Reuses the coherence gate from the sibling drill (`research_coherence_schema_fit_gate_brain_drill_2026-07-19.md`)
  as the SOURCE of the training/error signal below — this is the concrete mechanism that closes the loop
  between "parse a sentence" and "learn to parse it better."

**Step 1 — candidate generation (unchanged):** for each verb-frame instance, enumerate the small set of
grammatically-licensed role-assignment candidates (per NP-count/position, the existing hand-rule reader's
own logic).

**Step 2 — cue-feature extraction per candidate:** word-order position, animacy (already present in grounded
word vectors), verb-semantic-class fit (does the filler's grounded-vector semantic neighborhood match the
verb's typical argument class — a graded, learned score, not a hand-authored one), construction-type
membership (which schema, see Step 4), recency/prominence in the discourse-state overlay.

**Step 3 — LEARNED cue-competition scoring:** a small weight vector over the Step-2 features, ATTACHED TO
THE CONSTRUCTION (not globally, not per-verb — Angle 3's finding), scores each candidate; highest score wins
as the tentative parse (the actor-first-style default, Angle 4). This is a small, interpretable linear (or
low-order polynomial) scoring function over named features — fully glass-box, inspectable per decision.

**Step 4 — construction-level abstraction:** cluster verb-frame surface-cue profiles by distributional
similarity + downstream coherence outcome into a small number of CONSTRUCTIONS (transitive, caused-motion,
ditransitive, etc. — reuse the ClausIE-style clause-type taxonomy already recommended in the 07-17 Open-IE
note as the initial construction inventory, rather than inducing it from scratch cold). Each construction
carries its OWN Step-3 weight vector. New verbs inherit the weight vector of whichever construction their
frame matches — this is the mechanism that gives compositional generalization to held-out verb+construction
pairs (Prediction 2 below).

**Step 5 — error-driven weight update (the learning signal, coherence not treebank):** feed the winning
candidate's bound representation through the coherence gate (sibling drill's Score 1 graded prediction-error
+ Score 2 discrete structural-incoherence flag). If CONFIRMED coherent (and, where available, later
context/downstream continuation does not contradict it): positive update — strengthen the cue-weights (Step
3) that favored this candidate, for this construction. If FLAGGED incoherent or later contradicted: negative
update — weaken those cue-weights for this construction, AND separately increment a per-verb PREEMPTION
counter recording that this specific cue-combination lost for this specific verb (Angle 3's retreat
mechanism) — so a verb-specific mis-attachment pattern gets suppressed even before the construction-level
weights fully converge. This update rule directly implements the Fitz & Chang error-propagation mechanism
(Angle 4) at two granularities simultaneously: construction-level cue-weight (Angle 2) and verb-level
preemption (Angle 3).

**Step 6 — DEFERRED cases:** candidates that the coherence gate places in its own DEFERRED/middle band
(sibling drill's third state) do NOT generate a weight update in either direction — an ambiguous outcome is
not treated as either confirming or disconfirming evidence, avoiding poisoning the cue-weights with
noisy/uncertain signal. This directly reuses the sibling drill's DEFERRED-state design rather than inventing
a separate mechanism.

**Why this FIXES coherent-but-wrong mis-attachments specifically:** the current hand-rule reader has, in
effect, only Step 1 + a fixed (not learned) version of Step 3 — it always picks the same positional default
regardless of whether that default has previously been disconfirmed for this verb/construction. The LCCP's
Step 5 update is exactly the missing piece: a mis-attachment that COHERES on any single sentence (so the
coherence gate alone cannot catch it) will, with repeated exposure, accumulate disconfirming evidence
whenever a competing candidate is confirmed instead for the same verb/construction — this is the
preemption/entrenchment mechanism operating exactly as it does in child language acquisition, where
"don't giggle me" is never corrected by a single explicit negative instance but by the cumulative statistical
dominance of the correct competing form.

**Why this generalizes compositionally:** because weights live on the CONSTRUCTION (Step 4), a novel verb in
a familiar construction inherits that construction's already-learned cue-weights, rather than starting cold
— this is the direct mechanism answering the task's "generalizes compositionally to novel combinations"
requirement, and is the single most novel (least literature-precedented AS AN ENGINEERED SYSTEM) claim in
this design.

**Why this improves with exposure (the flexible/Matthew property):** cue-weights (Step 3) and preemption
counters (Step 5) are running statistics that update every time a sentence is processed — accuracy on a
given construction/verb should show a genuine LEARNING CURVE, not a fixed one-shot rule set, and — per the
sibling drill's compounding-learning framing — later exposures are judged against an increasingly accurate
weight vector, so the SAME verb gets easier to parse correctly over time without any rule being hand-edited.

---

## The FAIR can-fail test

**Real baseline:** the CURRENT hand-rule reader (fixed positional default, no learned reweighting, no
preemption tracking) — the ~0.18-0.40 precision wall already measured on real prose (per
`research_glass_box_reading_robust_parsing_ceiling_2026-07-16.md` / `research_classical_openie_glassbox_parsing_2026-07-17.md`).
Not a strawman: it is the system already in production on this eval slice.

**Independent gold:** all measurements against an EXTERNAL held-out gold-annotated slice never used to
produce the candidates being scored — guards against the construction-determined-outcome trap
([[feedback-synthetic-toy-corpus-outcomes-can-be-construction-determined]]).

**One variable per arm:**
- Arm A: hand-rule reader, unchanged (baseline).
- Arm B: LCCP with Steps 1-3 only (learned cue-competition, no construction-level sharing — weights either
  global or per-verb-only) — isolates whether learned reweighting alone (without the generalization
  mechanism) helps.
- Arm C: full LCCP (Steps 1-6, construction-level weight-sharing + preemption + DEFERRED-state exclusion)
  — isolates the full design.
- Held-out split: verb x construction combinations partitioned so some (verb, construction) pairs are NEVER
  jointly seen in the training/learning-update stream, only at held-out eval time — this is the mechanism
  that actually tests compositional generalization, not just in-distribution accuracy.

**HARD-PASS (mis-attachment reduction):** Arm C reduces the coherent-but-wrong mis-attachment FP rate by
>=15 points vs. Arm A on matched construction types, measured against independent gold, after a specified
number of learning-update exposures (order-of-magnitude: hundreds to low-thousands of sentences — exact
count is cell-author's to pre-register, not prescribed here).

**HARD-FAIL (mis-attachment reduction):** <5-point reduction, or no measurable reduction — would mean the
coherence-mismatch signal is too weak/sparse to drive retreat on cases that are, by construction, coherent
(the hardest case for a coherence-only signal), and an auxiliary signal beyond pure coherence (e.g. explicit
cross-sentence continuity/consistency checks, per the brain-check below) is needed instead of or alongside
preemption tracking.

**HARD-PASS (compositional generalization):** on held-out (verb, construction) pairs never jointly seen in
training, Arm C's accuracy is within 10 points of its accuracy on seen (verb, construction) pairs of the same
construction type — demonstrating weights genuinely live on the construction, not memorized per-verb.

**HARD-FAIL (compositional generalization):** held-out accuracy drops >25 points relative to seen pairs —
would indicate the construction-clustering step (Step 4) is not actually recovering shared structure (the
Tomasello verb-island failure mode reproduced in the engineered system), and construction-level weight-
sharing is not functioning as designed.

**Learning-curve measurement (required, not optional):** report per-verb and per-construction mis-attachment
rate as a function of cumulative exposure count — a flat curve (no improvement with exposure) falsifies the
"flexible, improves with exposure" property even if the FINAL accuracy numbers pass the other bars.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL, consolidated)

**Prediction 1 — LCCP (Arm C) reduces coherent-but-wrong mis-attachment FPs vs. the hand-rule reader.**
P=0.35 (deflated; directly targets the task's named failure mode, but untested on an engineered system and
capped per novel-synthesis rule). HARD-PASS/FAIL as specified above.

**Prediction 2 — compositional generalization to held-out verb x construction combinations.**
P=0.30 (deflated further — the highest-novelty-risk claim; construction-level weight-sharing recovering the
right generalization boundaries without supervision is the single least-precedented-as-engineering claim in
this design). HARD-PASS/FAIL as specified above.

**Prediction 3 — cue-weights shift in the theoretically-predicted direction when a cue's reliability is
synthetically degraded (construct-validity / mechanism-sanity check).**
P=0.40 (deflated; lower risk, this is a mechanism-validity check rather than a capability claim). HARD-PASS:
degrading the informativeness of one cue in a held-out training slice (e.g. synthetically randomizing
word-order consistency while keeping coherence-checkable structure) causes the learned weight on that cue to
measurably DROP relative to a control run where the cue stays reliable. HARD-FAIL: weight stays statistically
unchanged — would mean the "learning" is not actually cue-validity-sensitive, a construction-determined/
vacuous result per the synthetic-toy-outcomes discipline, and the update rule needs re-design before any
capability claim is trusted.

**Prediction 4 — per-verb mis-attachment rate shows a genuine negative-sloped learning curve vs. exposure
count, without negative/treebank evidence.**
P=0.35 (deflated). HARD-PASS: statistically significant negative slope, holding construction type fixed.
HARD-FAIL: no significant slope or immediate plateau at first-exposure rate — the single most concerning
outcome, since it would mean coherence-only feedback is not informative enough to drive retreat on cases
that are, by definition, coherent (see brain-check below for the honest fallback if this HARD-FAILs).

---

## Brain-check (outcome not pre-assumed)

**Argument-structure acquisition IS a real, existence-proven brain capability** — children reliably learn it,
across typologically very different languages, from noisy naturalistic input with no negative evidence.
This is not a case of the brain lacking the capability.

**Where the brain-check reveals a REAL, shared structural bound (same-limit, accept):** the human system's
own error-correction for coherent-but-wrong readings is itself imperfect and slow — agreement attraction,
garden-path "lingering misinterpretation" (Christianson et al. 2001, cited in the sibling coherence-gate
drill), and the Moses illusion all show that PLAUSIBLE-BUT-WRONG interpretations routinely survive human
comprehension, sometimes into durable memory. If Prediction 4 HARD-FAILs (no learning curve from
coherence-only feedback), that would NOT be a substrate-specific failure — it would replicate a genuine,
well-documented human limitation: coherence/plausibility alone is demonstrably NOT always sufficient
disambiguating signal, in human wetware either. Per the two-frontiers doctrine, this is a case where
"same-limit" should be checked honestly rather than assumed away.

**Where the brain-check licenses a substrate-native departure (brain fails the same way -> fix is native,
not brain-imitative):** humans default to an EFFORT-GATED coherence check (per the sibling drill: only ~50-
60% detection rate on controlled semantic-anomaly paradigms) precisely because full verification is
metabolically/attentionally expensive. An engineered LCCP has no such constraint — it can run an ALWAYS-ON,
exhaustive cross-sentence/cross-document consistency check (not just local sentence-level coherence) as part
of the Step 5 error signal, which the brain structurally cannot afford to do continuously. If Prediction 4
HARD-FAILs under LOCAL coherence-only feedback, the substrate-native fallback (not a brain-copied mechanism,
an explicit engineering departure) is to widen the error signal to document-scope consistency-checking
(reuse the DEFERRED-state re-scoring mechanism from the sibling coherence-gate drill) before concluding the
whole LCCP design is unworkable — this gives the retreat mechanism access to disambiguating signal a
biological reader, bounded by working-memory/attention, structurally cannot use.

**Honest ceiling to carry forward:** per the earlier scour cited in the task brief, unsupervised/grounded
parsing sits around 40-70% accuracy on short sentences in the published literature; a glass-box, coherence-
driven (not treebank-supervised) LCCP should be judged against THAT honest range, not against fully-supervised
neural-parser accuracy (~90%+ on in-domain newswire) — the relevant comparison for HARD-PASS/FAIL purposes
is the delta over the current hand-rule reader on THIS eval slice, not an absolute accuracy target borrowed
from a different (supervised, in-domain) regime.

---

## Cross-thread synthesis

This drill sits directly upstream of and composes with `research_coherence_schema_fit_gate_brain_drill_2026-07-19.md`
(same day, same arc): that drill designed the two-signal (graded + discrete) coherence gate and its DEFERRED
state; THIS drill supplies the learning signal's CONSUMER — a parser whose candidate-selection weights are
literally updated by that gate's accept/flag/reject output (Step 5 above). Neither drill's design is complete
without the other: the coherence gate needs a parser that generates GOOD candidates to score, and the parser
needs the coherence gate's output as its only training signal (per the task's explicit requirement: "learning
signal = coherence/grounding, NOT treebank"). This drill also directly extends
`research_wm_barrier_glassbox_parsing_2026-07-17.md` (incremental structural memory / dependency stack is the
SUBSTRATE the LCCP's candidates are generated and held over — same lever, not competing) and
`research_classical_openie_glassbox_parsing_2026-07-17.md` (construction inventory = reuse the ClausIE
clause-type taxonomy already recommended there as Step 4's starting point, rather than inducing constructions
from scratch). All four notes, independently arrived at across different literatures and different drill
sessions, converge on the same underlying architectural shape: a graded, situation/construction-conditioned
score, an explicit ambiguous/deferred state (not forced binary), and a mechanism that gets cheaper/better as
the foundation grows (the Matthew-effect/compounding-learning property already established for memory-
consolidation in `research_compounding_learning_missing_structure_schema_gated_consolidation_2026-07-18.md`,
now re-derived here for comprehension/parsing).

## Ranked actionable anchors (delivered inline per no-routing-file discipline)

1. **[Primary, novel-synthesis P=0.35-0.45] Build + smoke the Learned Cue-Competition Parser (LCCP) Arms
   A/B/C ablation** on the existing coherent-but-wrong mis-attachment eval slice — Arm A = current hand-rule
   reader (baseline, unchanged); Arm B = LCCP Steps 1-3 only (learned cue-competition, no construction-level
   weight-sharing); Arm C = full LCCP Steps 1-6 (construction-sharing + preemption + DEFERRED-state
   exclusion). Held-out split: (verb, construction) pairs never jointly seen during the learning-update
   stream, only at eval time. See "Angle 5" for the full step-by-step design and "The FAIR can-fail test" for
   the complete arm/threshold spec.
2. **[Secondary, cheap, run alongside anchor 1] Mechanism-validity sanity check (Prediction 3):** synthetically
   degrade one cue's reliability in a held-out training slice and confirm the learned weight on that cue
   measurably drops relative to a control run — guards against a vacuous/construction-determined "learning"
   result before trusting anchor 1's larger findings.
3. **[Tertiary, contingent on anchor 1's Prediction 4 result] Substrate-native always-on document-scope
   consistency check**, widening the Step 5 error signal beyond local-sentence coherence — only build if
   Prediction 1 HARD-PASSes but Prediction 4 (learning curve from coherence-only feedback) HARD-FAILs; reuses
   the DEFERRED-state re-scoring mechanism from the sibling coherence-gate drill
   (`research_coherence_schema_fit_gate_brain_drill_2026-07-19.md`). Do not build before anchor 1's result is
   in.
4. **[Design constraint, zero-cost, applies regardless of test outcome] Cue-weights and role-templates must
   live at the CONSTRUCTION level (Step 4), never globally or per-verb-only** — this is the single mechanism
   licensing compositional generalization to held-out verb+construction combinations (Angle 3); building Arm
   B without ever building Arm C would silently forgo the generalization property the task specifically
   requires.

## Substrate-product implications

Not a publication angle — a build-priority and honesty angle. If the LCCP design's Prediction 1/2 HARD-PASS,
the product gains a genuinely differentiating property most competing pipelines lack: a parser that
IMPROVES its own argument-structure assignment from exposure using only its own coherence-check output, with
zero treebank/human-annotation dependency and zero external LLM call — directly on-thesis for the glass-box,
no-LLM read-and-grow pipeline. If Prediction 2 (compositional generalization) specifically HARD-FAILs while
Prediction 1 (in-distribution mis-attachment reduction) HARD-PASSes, the honest fallback is that the system
has a genuine, useful per-verb/per-construction learning capability but does NOT yet generalize
compositionally — a real, sellable "gets better with your data" property, just not (yet) the stronger
"generalizes to unseen combinations" property; this would redirect further investment toward improving Step
4's construction-clustering specifically, not toward abandoning the design. If Prediction 4 HARD-FAILs even
under the substrate-native always-on/document-scope fallback (brain-check section), the honest ceiling is
that coherence/grounding alone is insufficient signal for retreat and a genuinely different signal (e.g.
lightweight, cheap-to-produce partial gold/spot-checked correction on a small seed set, still far short of
full treebank supervision) would need to be considered as a supplement — flagged now so this is not a
surprise if it happens.

---

## Citations (verified count)

**~35 distinct primary/named sources**, freshly verified via live search this session across four parallel
lit-scans (flagged inline per sub-agent where recalled-from-training/secondary-sourced rather than
independently fetched): Gleitman 1990; Naigles 1990; Fisher & Gleitman (WIREs); Yuan & Fisher 2009; Fisher
et al. 2020 (*Topics in Cognitive Science*); Trueswell, Medina, Hafri & Gleitman 2013 (propose-but-verify);
Gillette et al. 1999 (Human Simulation Paradigm); Grimshaw 1981; Pinker 1984 (*Language Learnability and
Language Development*); Pinker 1994 (*Lingua*, secondary-paraphrase flagged); Fisher, Gertner, Scott & Yuan
2010 (WIREs); Tomasello 1992 (*First Verbs*), 2000, 2003; Ninio ("No Verb Is an Island"); Pine, Lieven &
Rowland 1998; Goldberg 1995, 2006; Casenhiser & Goldberg 2005; Goldberg, Casenhiser & Sethuraman 2004;
Bowerman (overgeneralization); Braine & Brooks (entrenchment); Ambridge, Pine, Rowland 2012/2014/2018;
Boyd & Goldberg 2011; Robenalt & Goldberg 2016; Ambridge et al. 2015 (PLOS ONE, preemption vs. entrenchment);
Ambridge, Pine, Rowland & Young 2008; Pinker 1989 (*Learnability and Cognition*, broad/narrow-range rules);
Bates, MacWhinney, Sokolov et al. 1984 (cross-linguistic cue validity, English/German/Italian); Hungarian,
Turkish, Japanese, Serbo-Croatian Competition Model extensions (multiple authors, verified via independent
searches); MacWhinney connectionist cue-weight simulations (~1989, secondary-source characterization flagged);
Gibson 1992 (Competition Model critique); Caramazza & Zurif 1976 (*Brain and Language*); Grodzinsky 1995/2000
(Trace Deletion Hypothesis); Bornkessel-Schlesewsky & Schlesewsky (Argument Dependency Model); Friederici
(ELAN/N400/P600 neurocognitive model); Kuperberg & Jaeger 2016; Fitz & Chang 2019 (*Cognitive Psychology*,
Dual-path error-propagation model of N400/P600); developmental garden-path-recovery studies (4yo vs. 5yo/
adult); bilingual/L2 garden-path-revision literature.

## Calibration

Per [[feedback-lit-scan-calibration-penalty]]: all falsifiable predictions capped at P<=0.45 as
novel-synthesis (application of established acquisition/neurolinguistics literature to an as-yet-untested
engineered system). The overall ranked-mechanism synthesis (LEARNED CUE-COMPETITION + CONSTRUCTION
ABSTRACTION + PREEMPTION RETREAT + PREDICTION-ERROR SIGNAL, unified as one architecture) is this drill's own
inference across four independently-sourced literatures, not a claim made by any single cited source — held
at P=0.45, the low end of the calibration band, reflecting that no cited source proposes this exact
six-part unification; each component individually sits at the higher P~=0.55-0.70 band reported per-angle
above.

---

## VERDICT (one line)

**The brain does NOT use one learned-parsing mechanism — it layers a universal structural candidate-
generation bias (syntactic/semantic bootstrapping), LANGUAGE/CONSTRUCTION-specific learned cue-competition
weights (Competition Model), usage-based construction-level abstraction for generalization (Tomasello/
Goldberg), and purely distributional preemption/entrenchment retreat (Ambridge) — all driven by a genuine,
brain-validated PREDICTION-ERROR signal (Fitz & Chang's literal error-propagation account of N400/P600) —
and this maps cleanly onto a buildable glass-box Learned Cue-Competition Parser (LCCP) that reuses the
existing candidate-generator, dependency-stack structural memory, and coherence gate, updating small
CONSTRUCTION-level (not global, not per-verb) cue-weight vectors plus per-verb preemption counters from the
coherence gate's own accept/flag/reject output — with the single largest open risk (Prediction 4, deflated
P=0.35) being whether coherence-only feedback is informative enough to drive retreat on cases that are, by
construction, coherent, for which the honest brain-check fallback is a substrate-native (not brain-copied)
always-on document-scope consistency check the biological system cannot afford to run continuously.**
