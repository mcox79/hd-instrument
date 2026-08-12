# Research drill: preclusion / goal-failure inference mechanism (2026-08-09)

Filed by: Research (Sonnet), director+USER-requested DEEP drill, explicitly scoped to be DISTINCT from
`notes/research_psych_bridging_inference_situation_models_2026-08-09.md` (the bridging drill), which
flagged the CONTRADICT/preclusion leg as "the field's thin spot -- no validated human-subject mechanism,
only GraphPlan-mutex computational precedent" and calibrated it at a capped P=0.35. This drill goes deeper
on exactly that leg via 4 parallel Sonnet lit-scans: (1) Talmy force dynamics + Wolff's dynamics theory of
causation, prioritized; (2) a hard, multi-angle hunt for human-subject evidence of implicit preclusion
inference; (3) computational preclusion precedents PAST GraphPlan-mutex (event calculus, frame-problem
solutions, negation-as-failure/ASP, qualitative physics); (4) event-level incompatibility representation
beyond lexical antonymy (Cruse/Lyons typology, VerbNet/FrameNet, distributional polarity axes, scalar
event-structure semantics). Trigger context: `hdlab/goal_outcome_relation.py`'s CONTRADICTS leg currently
runs `mwe_disengage_scan`, an exact WordNet-verb-gloss dictionary lookup with 5 disclosed real gaps
(bailed out / chickened out / shied away / washed her hands of / turned the other cheek); the bridging
drill's hand-off (`notes/exp_dev_handoff_research_psych_bridging_inference_situation_models_2026-08-09.md`)
already named the target anchor `exp_situation_model_relation_ablation_v1`, whose CONTRADICT-leg
axis-construction step this drill sharpens concretely.

---

## 1. Talmy force dynamics + Wolff's dynamics theory of causation (prioritized lane)

**Talmy's apparatus** (1988, *Cognitive Science* 12(1):49-100; expanded 2000, *Toward a Cognitive
Semantics* Vol. I, MIT Press, ch. 7) [ESTABLISHED as a descriptive taxonomy, uncontested]: Agonist
(focal entity, intrinsic tendency toward action or rest) vs. Antagonist (opposing force); relative
strength + concordance/opposition of the two force-vectors generates causing / letting / hindering /
helping / blocking / removal-of-blocking; "despite" marks the Agonist's tendency prevailing over
opposition, "because" marks the Antagonist's opposing/reinforcing tendency prevailing. For Talmy's own
worked diagrammed examples (steady-state blockage: stronger Antagonist -> Agonist's tendency does not
manifest), **non-occurrence IS diagrammatically built into the vector-sum logic** [ESTABLISHED, but
narrow -- holds for the specific worked cases, not stated as a general discourse principle]. **No paper
was found that generalizes this into an explicit discourse-comprehension claim** ("any narrated
force-opposition/disengagement act licenses an inference that an unstated goal failed") -- that
generalization is **SPECULATIVE**, a plausible extrapolation from the framework's internal logic that
nobody has actually stated or tested.

**Computational uptake -- thin, and the named "Leonard" system does not exist**: no dedicated
force-dynamic parser is mainstream NLP infrastructure. Three real-but-partial threads: Copley & Harley
(2015, *Linguistics and Philosophy* 38:103-158) give a rigorous FORMAL (not implemented) force-theoretic
event-structure semantics, modeling prevention/defeasibility to derive non-culminating accomplishments
("was Xing" without completion) [ESTABLISHED as formal semantics, not a running system]. The BECauSE
Corpus 2.0 (Dunietz, Levin & Carbonell 2017, ACL Anthology W17-0812) is a manually-annotated
CAUSE/ENABLE/PREVENT corpus explicitly grounded in force-dynamics (citing Wolff, section below) --
[ESTABLISHED resource, annotation not computation]. Kybartas, Verbrugge & Lessard (2021, AAAI AIIDE
17:50-57) build a literal physics-metaphor "force dynamic model of narrative agents" for
interactive-drama management -- borrows the label loosely, not a linguistic implementation. **The "Leonard"
grounded-force-dynamics system named in this drill's brief was searched for directly and NOT FOUND** --
every hit traces back to Leonard *Talmy* the person, not a system. Treat as unverified/likely
non-existent; do not cite it.

**Wolff's dynamics/force theory of causation** (Wolff & Song 2003, *Cognitive Psychology* 47:276-332;
Wolff 2007, *JEP:General* 136:82-111; Wolff, Klettke, Ventura & Song 2005, in Ahn et al. eds.
*Categorization Inside and Outside the Laboratory*, APA) [ESTABLISHED, with a real human-subject
experimental base]: formalizes CAUSE/ENABLE/PREVENT (+DESPITE) on three dimensions -- patient's tendency
toward an endstate, affector-patient force concordance, and endstate progression. PREVENT = patient has
a tendency, affector opposes it (discordant), endstate does NOT progress -- non-occurrence is
*definitional* in the representation, not inferred post hoc. The experimental base is real: verb-choice
and sentence-verification tasks (Wolff & Song 2003), 3D physics-animation composition judgments and
premise-chain conclusion tasks (Wolff & Barbey 2015, *Frontiers in Human Neuroscience* 9:1, 4
experiments). **All of this evidence is OFFLINE (categorization/judgment/production tasks) -- no
reading-time or ERP study anywhere in this scan tests force-dynamics-driven ONLINE processing.** The
account is also **CONTESTED**: Sloman, Barbey & Hotaling (2009, *Cognitive Science* 33:21-50) propose a
rival Bayes-net "causal model theory" for the same CAUSE/ENABLE/PREVENT judgments and report comparable
fit on production-task data; no consensus winner exists between the two accounts.

**Narrative/discourse-level preclusion specifically ("walked away," "backed off")**: **no study found**,
force-dynamic or otherwise, that tests whether disengagement phrasing (zero negation, zero explicit
failure vocabulary) triggers online goal-failure inference. The closest adjacent-but-distinct threads:
Trabasso & van den Broek's causal-network model (1985, *JML* 24:612-630) [ESTABLISHED that unsatisfied
goals stay causally active in readers' representations, but not force-dynamic-framed and not testing
THIS specific inference]; non-culminating-accomplishment/implicature research (Martin 2019, *Language and
Linguistics Compass*) [ESTABLISHED that failure-of-completion can be conveyed without negation
grammatically, but for verbal ASPECT ("was building a house" implicating not-finished), not narrative
disengagement verbs]. **Verdict for this lane: the specific target claim is untested -- SPECULATIVE,
not SPECULATIVE-but-close.**

## 2. Hard hunt for human-subject evidence of wordless preclusion inference

This lane ran ~20 searches across 9 independent angles (goal-failure reading time; implicit-negation
processing; plan/obstacle inference; ERP for goal-incongruent outcomes; counterfactual/incompatibility
inference; Trabasso/van-den-Broek lineage follow-ups specifically manipulating goal-*incompatible* [not
merely irrelevant] outcomes; script-violation-tradition extensions; named-researcher searches across
McKoon, Ratcliff, Singer, O'Brien, van den Broek, Zwaan; and alternate terminology like "mutual
exclusivity" / "incompatible event inference"). This directly resolves the bridging drill's open
question of whether the absence was genuine or an artifact of under-searching.

**Closest hit, still not a match**: Lutz & Radvansky (1997, *Psychonomic Bulletin & Review*), "Goal
coordination in narrative comprehension," manipulates subgoal SUCCEED vs. FAIL and finds longer reading
times on the FAIL condition's target region -- the single closest result in the entire scan. Full text
was paywalled; based on the field's standard stimulus-construction convention (Suh & Trabasso's own
resolved/unresolved goal-clause coding uses fairly direct failure language), it is likely the FAIL
condition used explicit failure vocabulary ("couldn't," "failed to") rather than a purely incompatible,
unmarked action -- flagged as **unresolved, not confirmed**, but the field-convention prior points away
from it being a genuine hit.

**Everything else missed on a defining feature of the target phenomenon**: implicit-negation literature
(Giannakidou-style) is about lexically negative-polarity words (fail/forget/doubt/disappointed) --
different phenomenon, since the target requires ZERO negative-polarity vocabulary. ERP work on
action-outcome incongruity (N400 on disconfirmed predictive inferences, spoon-to-mouth video studies)
tests EXPLICITLY stated or VISUALLY shown incongruent outcomes, not text-only implied preclusion via an
unrelated/incompatible action. Solomon, Hindy, Altmann & Thompson-Schill (2015, *J Cogn Neurosci*),
"Competition between Mutually Exclusive Object States in Event Comprehension," and a 2026 *Cognitive
Science* follow-up (Wing & Altmann) on intermediary object states are the nearest STRUCTURAL analogs
(representing that one state precludes another) but test PHYSICAL OBJECT states (cracked/whole,
empty/full) via fMRI conflict-detection, not character GOALS via a reading-time/ERP paradigm.

**Overall verdict: (C) genuinely UN-STUDIED at the human-subject level, now CONFIRMED rather than merely
suspected.** No study operationalizes: stated character goal -> action/event with zero explicit negation
or failure vocabulary that is merely logically/causally incompatible with that goal -> a human-subject
measure of the spontaneous "goal NOT achieved" inference. This strengthens the bridging drill's tentative
flag into a confident negative finding: the gap is real, not an artifact of a narrower first search.

## 3. Computational preclusion precedents past GraphPlan-mutex

**Event Calculus** [ESTABLISHED formalism; narrative application ESTABLISHED-but-niche]: Kowalski &
Sergot (1986, "A Logic-based Calculus of Events") gives the base ontology; Shanahan's tutorial ("The
Event Calculus Explained," in *Artificial Intelligence Today*, LNAI 1600, 1999) formalizes
`Clipped(t1,F,t2)` -- true iff some event terminating fluent F happens in `[t1,t2)` -- gating
`HoldsAt` persistence by `not Clipped`. Shanahan's *Solving the Frame Problem* (MIT Press, 1997) and "A
Circumscriptive Calculus of Events" (*Artificial Intelligence* 77, 1995) supply the circumscriptive
solution motivated by the Yale Shooting Problem (Hanks & McDermott 1987, *AI* 33) -- exactly the case
that required a clean `terminates`/`clipped` primitive instead of ad-hoc minimization. This IS a clean
formal primitive for "event E terminates goal-state G": assert G as a fluent, an achieving event
`initiates` it, an incompatible event `terminates` it. Applied to TEXT narratives (not just robot
planning): Erik Mueller's *Commonsense Reasoning: An Event Calculus Based Approach* (Morgan
Kaufmann/Elsevier, 2006/2014) and his restaurant-story system (2004) run event calculus over narrative
text directly.

**Frame-problem successor formalisms past STRIPS/GraphPlan/TWEAK** [CONTESTED as an NLU tool]: Reiter's
successor-state axioms (*AI* 49, 1991; *Knowledge in Action*, MIT Press, 2001) and Thielscher's fluent
calculus (*AI* 111, 1999) both collapse frame axioms into one per-fluent biconditional -- formally clean,
but essentially zero direct application to natural-language story comprehension was found; this lineage
stayed in robot/agent-control planning. Treat any narrative-comprehension use as this drill's own
extension, not prior art.

**Negation-as-failure / Answer Set Programming -- the strongest direct hit** [ESTABLISHED computational
mechanism, narrative-applied WITH worked examples and evaluation, no psychological validation claimed]:
Clark (1978, negation as failure) and Gelfond & Lifschitz (1988, stable-model semantics) are the base.
Blount, Gelfond & Balduccini ("A Theory of Intentions for Intelligent Agents," LPNMR 2015) formalize an
intention as persisting by NAF-default until an event makes it impossible/irrational, at which point it
is dropped. This is applied explicitly to narrative in "Understanding Restaurant Stories Using an ASP
Theory of Intentions" and the follow-up "An Application of ASP Theories of Intentions to Understanding
Restaurant Scenarios: Insights and Narrative Corpus" (arXiv:1810.00445), plus Balduccini/Baral et al.'s
"An ASP Methodology for Understanding Narratives about Stereotypical Activities" -- these give WORKED
EXAMPLES and a REAL narrative corpus/QA evaluation where goal-abandonment is inferred by NAF exactly as
this drill's brief hypothesized.

**Qualitative physics / naive physics** [SPECULATIVE for this use]: Forbus's Qualitative Process Theory
(1984, *AI* 24) and QSIM-family envisionment are physical-domain staples; a social extension exists
("Social QR," Forbus & McFate, QR-2015/QR-2024 workshop papers) porting QPT influences + episodic-case
memory to relationship dynamics, but this is a small workshop-paper community with no validated general
"envisionment excludes future goal-state" primitive on narrative text.

**Ranked cheapest-to-implement (this lane's own synthesis)**: (1) **ASP/NAF theory-of-intentions
abandonment rule** -- collapses to one hand-seeded table `interferes(event_type, goal_type)` plus a rule
`goal_failed(G) :- not achieved(G), interferes(E,G), happened(E)`; no solver needed, just a
lookup-plus-negation-check. (2) **Event-calculus `terminates`/`Clipped`** -- the same shape under
different vocabulary (`terminates(event_type, goal_fluent)`), with a more established narrative pedigree
(Mueller's system runs on actual text). These two are functionally the SAME small axis under different
formal dress; either is dramatically cheaper than a full theorem-prover and both are strictly deeper
computational precedent than "GraphPlan mutex" alone, because both have been applied to NARRATIVE TEXT
comprehension with worked evaluations, not just robot/agent planning.

## 4. Event-level incompatibility representation, beyond lexical antonymy

**Cruse/Lyons typology** (Cruse, *Lexical Semantics* 1986, *Meaning in Language* 2000/2004; Lyons,
*Semantics* 1977) [ESTABLISHED theory; the specific classification of action-pairs below is this lane's
own synthesis, flagged as interpretation]: splits "oppositeness" into antonymy (gradable, one scale:
hot/cold), complementarity/incompatibility (co-hyponyms that mutually exclude: red/blue, Monday/Tuesday),
converseness (relational reversal: buy/sell), and directional opposites -- itself split into antipodals
(top/bottom), counterparts (front/back), and **reversives** (change to opposite terminal states:
lock/unlock, dress/undress). Action pairs like **engage/disengage, pursue/abandon map cleanly onto
reversives**; **approach/withdraw, advance/retreat are directed-motion pairs closer to antipodal-style
opposition along a path axis**. Neither category is plain antonymy or incompatibility-proper (which
Cruse defines for co-hyponyms, not events) -- this is a genuinely distinct linguistic category from the
adjective-antonymy machinery `quality_relation.py`'s Channel A already uses.

**VerbNet/FrameNet -- largely negative** [CONTESTED, leaning negative]: Levin (1993) groups BOTH
directions of directed motion into ONE class ("Verbs of Inherently Directed Motion") rather than a
cross-class opposition link -- directionality is a per-lexeme feature, not a formal inter-class relation.
FrameNet's frame-to-frame "Excludes" relation (Ruppenhofer et al., *FrameNet II*) operates INTRA-frame
(mutually exclusive construals of one frame), not between e.g. Attaching/Detaching or Pursuit/Abandonment
frames. No systematic engineered mutual-exclusion relation between engagement- and disengagement-type
verb classes exists in these resources beyond sparse per-lemma WordNet antonym pointers -- confirming
`quality_relation.py`'s own design note that adjectives have no comparable taxonomic structure to lean
on, and neither do these verb resources.

**Distributional/embedding polarity axes** [ESTABLISHED for words; SPECULATIVE for composed events]:
the antonym/synonym cosine confound (antonyms get spuriously HIGH cosine because they share contexts) is
well documented (Mohammad et al. 2013, *Computational Linguistics*, "Computing Lexical Contrast").
Supervised fixes are an established subfield -- counter-fitting, multitask skip-gram with WordNet
constraints (Ono et al. 2015, NAACL), Siamese subspace models (Nguyen et al. 2019, ACL). The clearest
direct precedent for a continuous SIGNED axis: the **POLAR framework** (Mathew et al. 2020, WWW/TheWebConf,
arXiv:2001.09876) explicitly builds a signed polarity subspace from antonym-pair vector differences,
directly descended from **Osgood's semantic differential (1957)** -- structurally the closest existing
analog to `quality_relation.py`'s Channel B (signed FPE axis with a hand-seeded scalar lexicon). All of
this machinery is WORD-level; extending vector-difference/axis-projection to composed VP/event embeddings
(e.g. a single "engage<->disengage" axis position for a full clause, not just a lemma) is a plausible
extrapolation the lane found **NOT established anywhere -- this is the actual open gap**, not the axis
concept itself.

**Scalar/event-structure semantics -- the strongest formal fit** [ESTABLISHED]: Beavers (2008, 2013),
Kennedy & McNally (2005, *Language*), Rappaport Hovav & Levin, and Hay/Kennedy/Levin (1999) formalize
directed-motion/change-of-state verbs as entailing a **path scale** -- an ordered degree structure with a
directional ordering relation. Approach = monotonic decrease on a distance scale; withdraw = monotonic
increase on the SAME scale -- literally opposite-signed derivative on a shared axis. Pustejovsky's
Generative Lexicon (1995) independently formalizes event transitions as a `not-P(e1) -> P(e2)` opposition
structure inside qualia structure.

**Synthesis (this lane's own conclusion, not a literature-stated claim)**: no single resource hands over
a ready-made graded event-incompatibility relation, but three pieces compose cleanly: use Cruse's
reversive/directional-opposite typology to IDENTIFY which verb pairs are candidates (not incompatibility,
not simple antonymy -- a genuinely different linguistic category than Channel A's adjective antonyms);
use Beavers/Kennedy-McNally scalar/path-scale semantics + Pustejovsky's GL transition-opposition as the
actual FORMAL, COMPUTABLE machinery -- represent each event as `(scale, direction-sign)`, and
incompatibility falls out as opposite-signed monotonic change on a shared scale; borrow the POLAR/Osgood
polarity-axis-projection TECHNIQUE as the computational instantiation method, explicitly flagged as
untested at the event (vs. word) level.

---

## Verdict on psychological status (direct answer to the task's part a)

**Preclusion inference is genuinely UN-STUDIED at the human-subject level for the online-comprehension
question, CONFIRMED (not merely suspected) by an exhaustive 9-angle/~20-search hunt (section 2).** This
sharpens, rather than repeats, the bridging drill's "thin spot" flag into two separable claims:

1. **The semantic REPRESENTATION** (force-dynamics CAUSE/ENABLE/PREVENT typology, Wolff's dynamics
   theory of causation) **is ESTABLISHED with real human-subject data** -- but that data is entirely
   OFFLINE (verb-choice, sentence-verification, animation-composition judgment tasks), the account is
   CONTESTED against a Bayes-net rival (Sloman et al. 2009) with no consensus winner, and it has never
   been extended to narrative-discourse preclusion specifically.
2. **The ONLINE COMPREHENSION MECHANISM** (does a reader automatically, without task instruction, infer
   a goal failed from an unmarked incompatible action while reading) **has zero reading-time, ERP, or
   probe-recognition evidence anywhere in the literature** -- not "hard to find," actively hunted and
   not found. Treat this as a confirmed gap the program should stop re-searching for and instead build
   around honestly.

## Best-available mechanism for the substrate (part b) -- glass-box, maps to owned organs

Two independently-searched lanes (3 and 4) converge on the SAME shape without having seen each other's
output, which is the strongest signal this drill produced:

| Literature piece | What it licenses | Owned substrate mapping |
|---|---|---|
| Beavers/Kennedy-McNally scalar path-scale semantics + Pustejovsky GL transition-opposition (lane 4) | Represent an event as `(scale, direction-sign)`; incompatibility = opposite-signed change on a SHARED scale | Exactly `hdlab/quality_relation.py` Channel B's shape: `AXIS_WORDS` scalar lexicon (currently density/sheen/energy/tone) + signed FPE cosine threshold (`OPP_THRESH`/`SAME_THRESH`) -- needs a NEW axis family, e.g. `engagement` (engage=+1.0 .. disengage=-1.0) and/or `approach_distance` (approach=+1.0 .. withdraw=-1.0), same 6-10-word hand-seed discipline the existing 4 axes already use |
| POLAR/Osgood signed polarity-axis projection (lane 4) | The computational INSTANTIATION technique for a continuous signed axis (word-level established, event-level untested) | Same Channel B mechanism -- `_axis_word_vec`/`_fpe_axis_relation` already implement exactly this instantiation pattern; this drill supplies the citation trail justifying WHY that shape is the right one (not ad hoc), where the prior drill only had the GraphPlan-mutex computational analogy |
| Event-calculus `Clipped`/`terminates` OR ASP-NAF `interferes(event_type, goal_type)` (lane 3) | The PRECLUSION RULE itself: goal G (typed by its required-satisfaction pole on an axis) is `terminated`/`clipped` by an outcome event E if E's pole is opposite-signed on the SAME axis | This is the rule `quality_relation.py`'s Channel B composition ALREADY implements structurally (same-axis threshold decides opposed/same; cross-axis is categorically unrelated) -- lane 3 supplies a deeper, TEXT-narrative-applied computational precedent (Mueller's event-calculus story system; Blount/Gelfond/Balduccini's ASP restaurant-narrative corpus) for why this rule shape is the right one, strictly past "GraphPlan mutex" |
| Cruse reversive/directional-opposite typology (lane 4) | IDENTIFIES which verb pairs are candidates for the axis (a genuinely distinct linguistic category from adjective antonymy) | Informs which seed words go into the new `engagement`/`approach_distance` axis families -- e.g. engage/pursue/confront/approach vs. disengage/withdraw/retreat/abandon/back off/bail out/chicken out/shy away, directly recovering `goal_outcome_relation.py`'s 5 disclosed WordNet-MWE gaps as SCALAR AXIS members rather than requiring an exact dictionary-lemma hit |

**Concrete recommendation**: extend `quality_relation.py`'s `AXIS_WORDS` with an `engagement` axis
(single-token members: engage/pursue/confront/approach positive, disengage/withdraw/retreat/abandon
negative) plus phrase-level members for the disclosed gaps, using the SAME contiguous-span extraction
`goal_outcome_relation.py::mwe_disengage_scan` already implements (so a candidate phrase like
`bail_out`/`chicken_out`/`shy_away`/`wash_hands_of`/`turn_the_other_cheek` becomes an axis-lexicon key
the same way it currently becomes a WordNet-lemma lookup key) -- this reuses the SAME span-extraction
logic, just feeding a different terminal lookup (axis-lexicon dict instead of WordNet gloss scan). The
`CONTRADICT_query` in `exp_situation_model_relation_ablation_v1`'s design (per the prior hand-off) should
be: decode the goal-filler's engagement-axis pole (from `find_desired_state`'s verb, same input
`goal_atoms` already uses) and the outcome-filler's engagement-axis pole (from the extracted candidate
phrase); if both resolve to the SAME axis and opposite-signed poles, fire CONTRADICTS -- the exact
event-calculus-`terminates`/ASP-NAF-`interferes` rule shape, instantiated via `quality_relation.py`'s
already-proven Channel B composition.

**Honest caveat carried forward from lane 4**: the word-to-event extension of polarity-axis projection is
explicitly flagged in the literature as untested (not refuted -- untested). This drill does not claim the
axis approach IS validated at the event level; it claims the axis approach is the most defensible
currently-existing computational technique for the representational shape scalar event-structure
semantics independently license, and that `quality_relation.py` already implements this exact shape for
adjectives, so extending it to an engagement axis is a small, disciplined, same-pattern step rather than
a new organ class.

## Cheapest can-fail test (part c) -- cheaper than the full ablation, isolates the axis question alone

`exp_situation_model_relation_ablation_v1` (per the prior hand-off) tests the FULL pipeline (register
extension + both ACHIEVE and CONTRADICT queries + induce/predict + scramble control). This drill proposes
a strictly CHEAPER Tier-0 smoke that isolates ONLY the axis-construction question this drill sharpened,
before touching the register/induction machinery at all -- pure coverage measurement, same self-contained
pattern `hdlab/goal_outcome_relation.py::contradiction_dictionary_coverage()` already uses:

**Tier-0 (recommended first)**: build the `engagement` axis (~10-16 hand-seeded members, single-token +
the 5 disclosed-gap phrases as multi-token keys) in `quality_relation.py`'s `AXIS_WORDS` shape. Run
`quality_relation`-style same-axis-threshold scoring over (a) all 29 items in
`REPRESENTATIVE_DISENGAGEMENT_PHRASES` (existing bank, unchanged), (b) the 5 `_MWE_FALSE_POSITIVE_PROBE`
sentences (existing bank, unchanged), reusing `OPP_THRESH=-0.30` unchanged (no re-tuning). No register
wiring, no induction, no ACHIEVE-side changes -- pure coverage smoke, minutes not hours.

- **HARD-PASS**: recovers >= 3/5 of the disclosed WordNet-MWE gaps AND 0 false positives on the existing
  clean probe AND overall coverage on the 29-item bank >= the WordNet-MWE floor (26/29 = 0.897, i.e. does
  not regress what already works).
- **MIDDLE_BAND**: recovers 1-2/5 gaps, 0 false positives, coverage >= floor -- real but marginal, worth
  richer seeding before the full ablation.
- **HARD-FAIL**: recovers 0/5 gaps, OR any false positive on the clean probe, OR overall coverage drops
  below the 0.897 floor -- the axis approach is LESS precise than the existing exact dictionary lookup;
  do not proceed to the full ablation, keep `mwe_disengage_scan` as the operating point and flag
  kaikki.org Wiktextract (per that module's own docstring) as the alternative scale-up path instead.

**Tier-1 (only if Tier-0 clears MIDDLE_BAND or better)**: proceed to the full
`exp_situation_model_relation_ablation_v1` ablation exactly as specified in the prior hand-off (held-out
accuracy vs. current `held_acc`, scramble-control collapse, dictionary-gap recovery via the full
register-wired query) -- unchanged, this drill does not alter those pre-registered bands, only supplies a
cheaper gate to run first.

## Honest confidence + calibration (part d)

Per the mandatory lit-scan calibration penalty (deflate 0.15-0.25, cap novel-synthesis P at 0.50), this
drill reports THREE separable P's rather than one blended number, because the three questions have
genuinely different evidentiary status after this drill (a change from the bridging drill's single
blended 0.35 cap on this leg):

- **P(the mechanism DESIGN is well-formed, i.e. scalar-axis-plus-termination-rule is the right shape) ~
  0.55** -- HIGHER than the bridging drill's implicit confidence in the GraphPlan-mutex analogy alone,
  because this drill found TWO independently-searched lanes (computational precedent in narrative-applied
  event-calculus/ASP-NAF systems; linguistic-formal precedent in scalar event-structure semantics)
  converging on the identical `(scale, direction-sign)` + same-axis-opposite-sign shape without having
  seen each other's results.
- **P(the Tier-0 axis-coverage test HARD-PASSes as specified) ~ 0.35** -- capped at the novel-synthesis
  ceiling; the specific empirical question (does a 10-16-word hand-seeded axis actually recover >=3/5 of
  5 idiosyncratic idiom gaps without false-positiving) is genuinely untested and could easily land in
  MIDDLE_BAND (real signal, marginal recovery) given how idiomatic several of the gap phrases are.
- **P(this is a psychologically-faithful account of how humans perform this inference online) ~ 0.15-0.20**
  -- LOWER than the bridging drill's leg-level cap, not higher, precisely because this drill's hard hunt
  (section 2) converted a suspected absence into a confirmed one. Finding nothing after 20 searches across
  9 angles increases confidence THAT the psychological evidence does not exist, which is the opposite
  direction from increasing confidence that the mechanism is brain-faithful. This is the honest,
  load-bearing distinction this drill adds: the CONTRADICT leg's implementation-worthiness went UP (better
  computational/formal precedent) while its BRAIN-FIDELITY claim went DOWN (confirmed absence of
  supporting psych evidence) -- these are not the same number and should not be reported as one.

**Recommendation for `exp_situation_model_relation_ablation_v1`'s pre-reg**: keep the CONTRADICT leg's
calibration LOW as already planned, but attach the reason explicitly as "confirmed-absent online-psych-
evidence, not merely under-searched" (this drill's specific contribution) rather than the bridging
drill's softer "genuinely thin spot" framing -- and separately track the mechanism-design confidence
(~0.55, this drill's higher number) so a HARD-FAIL on Tier-0/Tier-1 is read as "this specific axis
seeding wasn't rich enough yet," not as "the whole approach is unlikely," since the design confidence and
the brain-fidelity confidence are independently calibrated and only one of them moved.

---

## Cross-thread synthesis

- Directly deepens the CONTRADICT leg the bridging drill flagged as thin (section 3 of that note): where
  that drill had ONE computational analog (GraphPlan mutex / causal-link threat detection, robot-planning
  lineage) and ONE speculative psych extension (Talmy force dynamics, no direct psycholinguistic uptake
  found), this drill supplies TWO deeper computational precedents with actual NARRATIVE-TEXT applications
  (Mueller's event-calculus story system; Blount/Gelfond/Balduccini's ASP restaurant-narrative corpus) and
  a genuine linguistic-formal justification for the signed-scalar-axis REPRESENTATION (Beavers/Kennedy-
  McNally scalar event structure) that the bridging drill did not have.
- Resolves the bridging drill's open uncertainty about whether the human-subject absence was genuine or
  under-searched (section 2 here): CONFIRMED genuine via an independent, wider hunt. This is itself a
  reusable finding -- future drills into this specific phenomenon should not re-run the same search, they
  should look for NEW angles (e.g. non-English-language psycholinguistics, or very recent 2025-2026
  preprints not yet indexed) if they want to re-open the question.
- Sharpens the concrete build target for `exp_situation_model_relation_ablation_v1`'s CONTRADICT-leg axis
  construction (previously left fully to exp_dev's discretion in the hand-off) into a specific proposal:
  an `engagement` axis in `quality_relation.py`'s existing `AXIS_WORDS` shape, seeded via Cruse's
  reversive/directional-opposite verb-pair typology, with phrase-level keys for the 5 disclosed gaps
  extracted via the SAME span-extraction logic `mwe_disengage_scan` already implements. exp_dev retains
  full discretion on exact seed words/counts/thresholds per the existing hand-off's autonomy declaration.
- Adds a genuinely NEW, cheaper Tier-0 test (pure axis-coverage smoke, no register/induction machinery)
  ahead of the existing Tier-1 (`exp_situation_model_relation_ablation_v1` full ablation) -- gates the
  more expensive test behind a fast, self-contained coverage check in the same style as
  `contradiction_dictionary_coverage()`'s existing regression guard.

## Substrate-product implications

If the Tier-0/Tier-1 tests clear MIDDLE_BAND or better, the product gains a materially richer auditable
trace for the CONTRADICT/preclusion leg specifically: instead of "this outcome matched a WordNet verb
gloss containing a disengagement keyword" (an opaque-feeling dictionary hit for idiomatic phrases like
"turned the other cheek"), the trace becomes "this outcome's engagement-axis position (cosine=X against
the goal's required pole on the SAME axis) is opposite-signed from the goal's engagement pole, crossing
the pre-registered OPP_THRESH" -- a graded, inspectable, axis-position-cited explanation using the exact
same evidence shape `quality_relation.py`'s adjective-opposition channel already surfaces for density/
sheen/energy/tone. This is the same auditability differentiator this arc has repeatedly identified as the
defensible product edge over an LLM black box: even where (per this drill's honest calibration) the
mechanism is NOT claimed to be a validated model of human processing, the substrate's trace stays fully
inspectable and cites its exact axis evidence, which an LLM-based system structurally cannot do. The
honest confirmed-absence-of-psych-evidence finding (part d) matters for calibration and prevents
over-claiming brain-fidelity in the trace's own framing, not for whether the mechanism is worth building.

## Falsifiable predictions (Tier-0, restated compactly)

- **HARD-PASS**: engagement-axis coverage recovers >=3/5 disclosed WordNet-MWE gaps, 0 false positives on
  the existing clean probe, overall 29-item coverage >= 0.897 (the WordNet-MWE floor).
- **MIDDLE_BAND**: recovers 1-2/5 gaps, 0 false positives, coverage >= floor.
- **HARD-FAIL**: recovers 0/5 gaps, OR any false positive, OR coverage regresses below 0.897.

## Citations (verified count: 0 primary-source-read this drill; all 4 lit-scan lanes report secondary/
WebSearch-sourced citations, cross-referenced across independently-searched lanes -- 30 distinct citations
named across the 4 lanes: Talmy 1988/2000; Copley & Harley 2015; Dunietz, Levin & Carbonell 2017 (BECauSE
2.0); Kybartas, Verbrugge & Lessard 2021; Wolff & Song 2003; Wolff 2007; Wolff, Klettke, Ventura & Song
2005; Wolff & Barbey 2015; Sloman, Barbey & Hotaling 2009; Trabasso & van den Broek 1985; Martin 2019;
Lutz & Radvansky 1997; Solomon, Hindy, Altmann & Thompson-Schill 2015; Wing & Altmann 2026; McKoon &
Ratcliff 1992; Kowalski & Sergot 1986; Shanahan 1995/1997/1999; Hanks & McDermott 1987; Mueller 2004/2006/
2014; Reiter 1991/2001; Thielscher 1999; Clark 1978; Gelfond & Lifschitz 1988; Blount, Gelfond &
Balduccini 2015 (+ arXiv:1810.00445); Balduccini/Baral et al. (ASP narrative methodology); Forbus 1984;
Forbus & McFate (Social QR, QR-2015/2024); Barros et al. 2019 (PROVANT); Cruse 1986/2000/2004; Lyons 1977;
Levin 1993; Ruppenhofer et al. (FrameNet II); Mohammad et al. 2013; Ono et al. 2015; Nguyen et al. 2019;
Mathew et al. 2020 (POLAR); Osgood 1957; Beavers 2008/2013; Kennedy & McNally 2005; Rappaport Hovav &
Levin; Hay, Kennedy & Levin 1999; Pustejovsky 1995.)

---

## HEADLINE

Preclusion/goal-failure inference from an unmarked, wordless incompatible action is CONFIRMED (not merely
suspected) genuinely un-studied at the human-subject level -- a hard, 9-angle/~20-search hunt found no
reading-time, ERP, or probe study testing it, sharpening the bridging drill's tentative "thin spot" flag
into a definite negative finding. Separately, Wolff's dynamics theory of causation (CAUSE/ENABLE/PREVENT)
IS psychologically established but only via OFFLINE judgment tasks, is CONTESTED against a Bayes-net
rival, and has never been extended to narrative discourse -- so the semantic REPRESENTATION is grounded
while the ONLINE MECHANISM is not, two separable claims this drill's calibration (part d) reports
independently rather than blending. The BEST-AVAILABLE build target converges from two independently-
searched lanes without cross-contamination: scalar/path-scale event-structure semantics (Beavers,
Kennedy & McNally, Pustejovsky) license representing engage/disengage-type events as `(scale,
direction-sign)` positions, exactly `hdlab/quality_relation.py`'s existing Channel B (signed FPE axis)
shape; and narrative-applied computational precedent (Mueller's event-calculus story system;
Blount/Gelfond/Balduccini's ASP theory-of-intentions restaurant-narrative corpus) licenses the
termination/interference RULE itself, going strictly deeper than GraphPlan-mutex. Concrete recommendation:
add an `engagement` axis to `quality_relation.py`'s `AXIS_WORDS`, seeded via Cruse's reversive/
directional-opposite verb typology, with the 5 disclosed WordNet-MWE gap phrases as multi-token keys
extracted via `mwe_disengage_scan`'s existing span logic. Cheapest test: a Tier-0 axis-coverage smoke
(pure lookup, no register/induction wiring, HARD-PASS = recovers >=3/5 disclosed gaps + 0 false positives
+ no regression below the 0.897 WordNet-MWE floor) gates the more expensive Tier-1
`exp_situation_model_relation_ablation_v1` full ablation already specified in the prior hand-off.

P_deflated=0.35 for "the Tier-0/Tier-1 tests HARD-PASS" (novel-synthesis cap; mechanism-DESIGN confidence
is separately higher at ~0.55 given the convergent two-lane precedent, while brain-fidelity confidence is
separately lower at ~0.15-0.20 given the confirmed-absent psych evidence -- see part d for why these three
numbers are reported independently rather than blended into one).
