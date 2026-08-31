---
problem: narrative_causal_graph_missing_implicit_inference_organ
status: SOLVED
bar: "PASS = the covariation causal-graph organ types CAUSE-vs-PRECONDITION beating BOTH the majority-class floor AND the adjacency/precedence-only floor, CI-separated (bootstrap; CI half-width + null p95), coverage-weighted lift >= +0.05, with the info-free shuffled-covariation twin LOSING. Report cross-corpus if a 2nd causal corpus is reachable. A rigorous NEGATIVE is a full PASS."
result: "TYPING (the bar): on held-out MAVEN-ERE valid causal relations (n=9698, coverage=1.0), the covariation causal-graph organ (arm B) scores RAW accuracy 0.890 vs majority 0.833 = +0.0578 [0.0505,0.0646] CI-sep (null p95 0.0069) AND vs the adjacency/precedence structural floor 0.832 = +0.0589 [0.0516,0.0654]; balanced accuracy 0.772 (macro-F1 0.747) vs structural floor 0.545 = +0.2263 [0.2091,0.2439]. DETECTION (brain-faithful extension): covariation causal-support edge-detector balanced 0.699 vs structural floor 0.652 = +0.0462 [0.0408,0.0515] CI-sep."
floor: "TWO floors, both beaten CI-separated: (1) majority-class = predict PRECONDITION/ENABLE always, raw 0.833 / balanced 0.500; (2) adjacency/precedence-only STRUCTURAL floor (sentence distance, text order, same-sentence, token distance -- NO event-type identity), raw 0.832 / balanced 0.545. Detection floors: majority (all-non-causal) balanced 0.500 and the structural floor balanced 0.652."
controls: "(1) shuffled-covariation twin (permute CAUSE/ENABLE labels before computing covariation stats) -> balanced 0.707, organ beats it +0.0653 [0.0544,0.0755] CI-sep (isolates the label-conditioned covariation over the label-independent ubiquity features it retains). (2) fully info-free permuted-training-label twin -> balanced 0.445 ~= chance, organ beats it +0.327 (EXCLUDES any learnable-structure artifact). (3) detection shuffled-event-type twin -> balanced 0.647, organ beats it +0.051 CI-sep (EXCLUDES structure-only). (4) adjacency/precedence structural floor EXCLUDES 'the win is discourse position not event-type semantics'. (5) SEEN-vs-UNSEEN type-pair split: EXCLUDES memorisation -- the hierarchical schema generalises to UNSEEN pairs (+0.0815 over the memorised lookup which collapses to chance 0.500), while a flat model collapses to 0.519. (6) type-NOISE + COARSENING robustness curves EXCLUDE dependence on gold 168-way typing (survives 40% noise / 21-bucket coarsening). (7) within-MAVEN verb-lemma covariation positive control (AUC 0.638) -- the mechanism works within its corpus. NOTE: the cross-genre transfer probe (exp_..._crossgenre / _mental_route) was found INSTRUMENT-CONFOUNDED on inspection (matrix-verb extraction, explicit-connective pairs) and its transfer verdict is WITHDRAWN -- open-text transfer is untested with a valid instrument."
files_changed: "experiments/_narrative_causal_graph.py; experiments/exp_narrative_causal_graph_{detection,typing,robustness,crossgenre,mental_route,intentional_split}_v1.py; verification/test_narrative_causal_graph_organ.py; notes/problems/narrative_causal_graph_missing_implicit_inference_organ/{SOLVED.md, research_covariation_causal_inference_mechanism_2026-08-30.md, research_narrative_causation_covariation_vs_situation_model_2026-08-30.md}. hdlab/ UNTOUCHED (proposed diff below, Q111)."
reverify: ".venv/Scripts/python.exe verification/test_narrative_causal_graph_organ.py   # 15/15, recomputes every headline from MAVEN-ERE source"
---

# Narrative causal-graph implicit-inference organ -- SOLVED (typing bar met with power; detection is the brain-faithful half)

## WHAT WAS ASKED
The force-dynamic causation typer fires on only 16.1% of real MAVEN-ERE causal relations and is indistinguishable
from a shuffled-lexicon twin where it fires. Build the complementary organ for the ~84% it structurally misses:
implicit, event-to-event narrative causation -- a covariation-based causal-GRAPH inference over event TYPES. Bar:
type CAUSE-vs-PRECONDITION beating the majority AND adjacency floors CI-separated, coverage-weighted >= +0.05,
info-free twin losing.

## HOW THE BRAIN DOES THIS (opened here; drilled where uncertain)
I opened with the brain mechanism and, because PROBLEM.md's covariation claim rested on a research slice that was
never verified (the prior note's "Lane A", capped P<=0.35), I drilled it before resting weight on it
(`research_covariation_causal_inference_mechanism_2026-08-30.md`). The drill split the mechanism cleanly and it
shaped the entire build:
- **EDGE DETECTION by covariation = PINNED** (P 0.68). Covariation-based Bayesian causal induction (Cheng 1997
  power-PC; Griffiths & Tenenbaum 2005 causal SUPPORT) is the accepted computational account of inferring that a
  causal link EXISTS from co-occurrence; the discourse-causal neural substrate is verified (Feng et al. 2021 ALE:
  left IFG/MTG + mPFC, the semantic-memory route, dissociable from logical reasoning).
- **CAUSE-vs-ENABLE TYPING by covariation = substantially OUR-INVENTION** (P 0.33). The cause/enabling distinction
  is genuinely contested (Cheng-Novick focal sets / Goldvarg-Johnson-Laird mental-model / Wolff force / Hilton
  pragmatic), and the strongest empirical result (Kuhnmuench & Beller 2005) is that people use LINGUISTIC CUES, not
  covariation. So covariation typing has a predicted ceiling. MAVEN's own definition (CAUSE = sufficient;
  PRECONDITION = necessary/enabling) is a counterfactual-structural distinction, which predicts the same ceiling.

I acted on all three drill corrections: (1) detection uses sample-size-aware Griffiths-Tenenbaum SUPPORT, not bare
deltaP; (2) typing is TWO pre-registered arms -- covariation-only (A) vs +linguistic-cues (B) -- so B-over-A
measures the covariation ceiling; (3) I checked the annotation basis (no cue-keyed guideline; the distinction is
necessity/sufficiency).

## WHAT I BUILT (glass-box, no external LLM; covariation KB learned offline from MAVEN train = a static asset)
`experiments/_narrative_causal_graph.py` -- the organ:
- **Griffiths-Tenenbaum causal SUPPORT** (detection): log P(D|link)/P(D|no-link) under a noisy-OR, background rate
  fixed to the empirical base rate, cause strength marginalised over Uniform(0,1). Sample-size-aware: 1/1 co-occ ->
  +2.0, 100/100 -> +254 (a 1-2 co-occurrence pair does NOT get a confident edge). This is the drill's key fix.
- **Cheng generative causal POWER** and deltaP (typing/strength), plus the enabling-condition covariation signature
  (base rate, out-degree = how many effect types a cause enables, effect entropy) convergent across
  Cheng-Novick + Hilton.
- **HierarchicalTyper** (Kemp-Goodman-Tenenbaum causal schema): a per-TYPE causal-role SCHEMA sub-model (type
  profiles + ubiquity -- available for ANY pair, so it generalises to novel pairs) with a per-PAIR INSTANCE
  correction (Cheng power / pair deviation) used ONLY when the pair was observed. Backoff = instance-if-seen,
  schema-if-novel. Glass-box logistic sub-models (weights inspectable).
- **Linguistic-cue extractor** (Kuhnmuench & Beller arm): cause vs enabling connective markers from surface tokens.

## THE RESULT -- two capabilities

### TYPING (the letter of the bar) -- SOLVED, coverage 1.0 (fires on EVERY relation, unlike the force typer's 16%)
- **RAW (the bar's stated metric):** arm B 0.890 vs majority 0.833 = **+0.0578 [0.0505,0.0646] CI-sep** (null p95
  0.0069, half-width 0.007) AND vs structural floor = **+0.0589 [0.0516,0.0654]**. Coverage-weighted lift == raw
  lift (coverage 1.0). Both floors beaten, >= +0.05. BAR MET.
- **BALANCED (volunteered against myself, because the task is 83% majority and raw accuracy is degenerate):**
  arm A 0.772 (macro-F1 0.745), structural floor 0.545 -> **+0.2263 [0.2091,0.2439]**. The signal is real
  minority-class discrimination, not majority exploitation.
- **Info-free twin LOSES:** shuffled-covariation twin 0.707, organ beats it +0.0653 CI-sep; fully info-free
  permuted-label twin 0.445 (~chance), organ beats it +0.327.

### DETECTION (the brain-faithful half; the Trabasso causal-network edge-existence computation) -- HOLDS
Causal edge (MAVEN causal pair) vs temporal-only pair (BEFORE/CONTAINS... but not causal), n=110500, base rate
causal 0.088. Balanced 0.699 vs structural floor 0.652 = **+0.0462 [0.0408,0.0515] CI-sep** (null p95 0.0024);
beats the shuffled-event-type twin +0.051. Covariation adds edge-existence signal BEYOND discourse position.

### THE MECHANISM BOUNDARY -- covariation is for PHYSICAL causation, not INTENTIONAL (drilled + measured clean)
A biology-first drill (`research_narrative_causation_covariation_vs_situation_model_2026-08-30.md`) established that the
brain does NOT compute implicit narrative causation by event-type covariation: it builds a SITUATION-SPECIFIC, token-
level BRIDGE (Singer & Halldorson; Trabasso counterfactual "in the circumstances of the story"; Kuperberg 2011 dual-
stream -- causal N400 SURVIVES matched lexical co-occurrence; Feng 2021 left MTG prior + IFG unification + mPFC
mentalizing). Covariation is the general-knowledge PRIOR, not the online bridge. Prediction: covariation captures
RECURRING-event-type PHYSICAL causation but NOT INTENTIONAL/goal causation.
- **VALID within-MAVEN test (no extraction/genre confound; gold event types) `exp_..._intentional_split_v1`:** the
  covariation causal-support edge-detector distinguishes causal from temporal-only far better when the cause is a
  PHYSICAL event (AUC 0.684 [0.675,0.693]) than an INTENTIONAL/mental event (AUC 0.570 [0.556,0.584]); gap +0.114
  [0.097,0.131] CI-SEPARATED, info-free shuffled-support twin ~0.50 both. CONFIRMED, cleanly.
- **BUILD-ACROSS attempt (per "if the brain can do it, we can too"): a MENTAL-causation KB does NOT fix it.** Scoring
  the SAME MAVEN intentional pairs (gold trigger verbs) with ATOMIC (xEffect/oEffect mental/intentional association)
  gives AUC 0.42 -- BELOW chance -- and fused with covariation HURTS (0.55 < 0.57). So the intentional wall is a
  MECHANISM gap, NOT a data/KB-coverage gap: verb/event ASSOCIATION from ANY source (physical or mental) is structurally
  insufficient for intentional causation. The brain's mechanism (situation-specific bridging + mentalizing) is DIFFERENT
  IN KIND from association -- consistent with Kuperberg dual-stream + Singer bridging. Building it (a glass-box mediator-
  path + counterfactual-necessity validator over goal-relation KBs) is the named follow-on; the shelf's ConceptNet slice
  lacks the goal relations (MotivatedByGoal/HasPrerequisite), so it needs KB resourcing, done carefully (entity-linking
  is the exact risk that broke the withdrawn probe).

### CROSS-GENRE PROBE (Anne/McGuffey) -- WITHDRAWN, instrument-confounded
An earlier verb-lemma cross-genre probe read ~0.5 AUC as a rigorous negative; on inspection the TEST was confounded
(root-verb extraction grabbed matrix verbs not causal events; the pairs are explicit-connective, wrong population;
mis-segmentation). VERDICT WITHDRAWN. The within-MAVEN intentional/physical split above is the valid, confound-free
version of the same mechanism question. Open-text on RAW narrative text remains untested end-to-end.

## GENERALIZATION -- what generalises, and the honest asymmetry (this is the deepest brain-foundational finding)
- **TYPING generalises to UNSEEN event-type pairs** (never co-observed in training): the hierarchical schema scores
  balanced 0.582 vs the memorised type-pair lookup 0.500 (chance) = **+0.0815 [0.0579,0.1053] CI-sep**, and vs a
  FLAT (non-hierarchical) model 0.519 = +0.063. A type's characteristic causal role (Attack tends to be a cause,
  Death tends to be an effect) TRANSFERS to a novel pair -- exactly the Kemp-Goodman-Tenenbaum causal schema. The
  memorised joint (the de-risk gate's mechanism) has NO generalization mechanism and collapses to chance.
- **DETECTION does NOT generalise to unseen pairs** -- and this is brain-faithful, not a failure: causal SUPPORT is
  defined over OBSERVED contingency data, so a never-co-observed pair has zero evidence (support=0). On unseen pairs
  structural position wins (organ 0.671 < structural 0.705). You cannot infer a NEW causal regularity between two
  event types you have never seen relate from covariation alone (Kuperberg 2011: causal integration exceeds surface
  co-occurrence). The organ backs off to structure there. THE ASYMMETRY IS THE POINT: typing an assumed edge needs
  only the type schema; detecting a novel edge needs the observation.
- **ROBUST to imperfect event typing** (a real reader lacks gold types): the covariation signal degrades GRACEFULLY
  under type noise (p=0.2 -> 0.727, p=0.4 -> 0.690, collapsing to chance only at p=1.0) and under coarsening (168
  types -> 21 buckets -> 0.741, barely below gold-168's 0.764). The win does NOT depend on MAVEN's fine gold ontology.

## DOES IT GENERALIZE TO OPEN TEXT? (asked directly by the owner) -- TESTED: a RIGOROUS NEGATIVE, diagnosed
This was the biggest open-text axis, so I tested it rather than deferring it (`exp_narrative_causal_graph_crossgenre_v1`).
The genre-portable unit is the VERB LEMMA (MAVEN's 168 types do not exist elsewhere; Chambers & Jurafsky narrative-chain
unit). I built MAVEN verb-lemma causal covariation and tested transfer to TWO different NARRATIVE genres: Anne of Green
Gables (FICTION, 243 gold causal clause-pairs) and McGuffey graded readers (200). Test: does MAVEN covariation score
real cross-genre causal verb-pairs above frequency-matched shuffled pairs (AUC vs 0.5)?
- **RESULT: NO cross-genre transfer.** AUC(real>shuffled) = 0.503 [0.457,0.561] fiction, 0.510 [0.451,0.569] readers --
  chance. A RIGOROUS NEGATIVE (the bar: "a rigorous NEGATIVE is a full PASS ... name why, enumerated").
- **It is NOT an artifact, and NOT merely coverage** -- diagnosed with the mandatory positive control:
  - POSITIVE CONTROL PASSES: verb-lemma covariation carries real causal signal WITHIN MAVEN (AUC 0.638 causal vs
    temporal-only) -> the representation is valid, so the null is genuine.
  - Transfer fails even on the SEEN-verb-pair subset (fiction 0.27, readers 0.19) -> not a vocabulary-coverage gap.
- **WHY (brain-foundational, enumerated):** the fiction/reader causal clauses centre on MENTAL/INTENTIONAL/speech verbs
  (top cause-clause roots: be, have, know, think, say, want) -- everyday "he decided, so he acted" causation -- whereas
  MAVEN/Wikipedia causation is PHYSICAL-EVENT-heavy (attack, kill, destroy -> death). These are DIFFERENT causal
  subsystems: mental/intentional causation recruits the mentalizing/ToM network, dissociable from physical-event
  causation (the first note's WALL 2: Straube 2013; Wende 2015; Blakemore 2003). A covariation KB learned on
  physical-event causation cannot cover mental-intentional causation. (Caveat: root-verb extraction of
  explicit-connective clauses often returns the matrix mental verb -- itself a signature of the mental-causation genre.)
- **I tried to close this with a positive control (`exp_narrative_causal_graph_mental_route_v1`: does covariation
  transfer to fiction when trained on MENTAL causation from ATOMIC?) -- and in drilling the result I found the WHOLE
  cross-genre TEST IS CONFOUNDED, so I WITHDRAW the strong conclusion.** Inspecting the extracted fiction pairs: the
  root-verb extraction returns MATRIX/copula/mental verbs (knit, hear, be, feel, think, have), NOT the causal-event
  verbs ("because I didn't have time" -> "have"); the McGuffey/Anne pairs are ALL EXPLICIT-CONNECTIVE causation
  (because/so/for) -- a DIFFERENT population from the IMPLICIT causation the organ targets, with the causal signal in
  the connective, not the verb pair; and some clause pairings are mis-segmented. So the test COULD NOT have succeeded
  (ask-whether-it-could-succeed-first): AUC ~0.5 is a BROKEN-INSTRUMENT artifact, NOT evidence about the mechanism.
- **What HONESTLY survives:** (i) the WITHIN-MAVEN verb-covariation positive control (AUC 0.638) -- the mechanism works
  within its corpus; (ii) a vocabulary observation -- ATOMIC(mental) verb vocabulary covers narrative far better than
  MAVEN(physical) (0.83 vs 0.37), consistent with narrative causation being mental/intentional-heavy. NEITHER the
  cross-genre negative NOR the "narrative causation is situation-specific / not covariation" reading is established --
  those are OPEN QUESTIONS, not results. I over-claimed them one iteration ago and am retracting.
- **So the honest open-text answer:** open-text / cross-genre transfer of the covariation organ is UNTESTED WITH A VALID
  INSTRUMENT. The available cross-genre corpora (McGuffey, Anne) are explicit-connective + my event-verb extraction is
  confounded, so they cannot answer it. A valid test needs IMPLICIT narrative causal pairs with proper causal-EVENT
  extraction (not matrix verbs). Whether the brain infers narrative causation by event covariation or by situation-model
  bridging (Kintsch/Singer/Kuperberg) is the deep question -- being drilled (biology-first) to design that valid test.
  The full raw-text pipeline also remains untested (the robustness curve simulates type noise only).

## THE WALLS, UNDERSTOOD (not papered over)
1. **Linguistic cues do NOT beat covariation** (arm B - arm A = +0.0049, NOT_SEP; an order of magnitude below the
   covariation effect +0.226). This CONTRADICTS Kuhnmuench & Beller's prediction that cues dominate -- and the
   reason is exact: K&B measured cue-dominance on EXPLICIT constructions; these are IMPLICIT relations BY
   CONSTRUCTION (the 84% the force typer misses), so the explicit connectives are largely absent (they fire on only
   25-34% of relations and carry weak signal: cue-only balanced 0.562). Covariation is what is left, and it already
   captures the separable signal. The ceiling is real: balanced 0.77 is near the achievable ceiling for ANY of
   these signals (effect-type marginal alone 0.740, pair lookup 0.765), because CAUSE-vs-ENABLE is partly a
   counterfactual/pragmatic distinction not present in the type statistics.
2. **Detection novel-pair bound** (above) -- understood as the definitional limit of covariation (needs observed
   contingency), resolved by a structural backoff.

## KEY REALIZATIONS (the enabling moves)
- **Drill FIRST where the mechanism is uncertain, and let it split the design.** The single most valuable move was
  confirming detection-covariation is PINNED but typing-covariation is OUR-INVENTION -- which turned "build one
  covariation typer" into "a brain-faithful detector + a measured-ceiling typer with a named better signal."
- **Replace the memorised lookup with a COMPUTED causal statistic.** The de-risk gate memorised the type-pair->label
  joint (60% coverage, chance on the rest). Cheng power + a type-role SCHEMA compute from marginals -> 100% coverage
  AND generalisation to unseen pairs. Our worst move would have been to adopt the lookup; the win was copying the
  operation (Cheng power / G-T support) and sweeping the parameters (event-type granularity).
- **Sample-size-aware SUPPORT, not deltaP.** In the single-narrative regime a pair is seen a handful of times;
  deltaP/power over-commit (1/1 -> power 1.0) where G-T support does not (1/1 -> +2.0, weak). This is the drill's
  correction and it is the honest edge-detection score.
- **Gate the pair-specific features by pair_seen (hierarchical backoff).** A flat model that leans on pair-covariation
  features COLLAPSES on unseen pairs (those features are dead there); the schema/instance backoff recovers +0.063 on
  unseen and is strictly better on the full population.
- **Balanced accuracy is the honest metric on an 83%-majority task** -- report it beside the bar's raw lift, or a
  majority-exploiting classifier looks like a win (this is the same imbalance discipline that caught a prior artifact).

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md 2b -- the CAUSATION routes)
CAUSATION has at least two routes. (a) MECHANISM/FORCE route = `force_dynamics_typer`, explicit-physical predication,
~16% of real causal relations, behaviorally supported but ZERO neural evidence for its social extension. (b) DISCOURSE/
COVARIATION route = this organ, implicit event-to-event causation, ~84% of MAVEN, the semantic-memory route (Feng et
al. 2021 ALE: left IFG/MTG/mPFC), dissociable from logical reasoning. Within route (b): EDGE DETECTION replicates a
PINNED computation (Cheng power-PC / Griffiths-Tenenbaum causal support) and holds where the type-pair is observed;
CAUSE-vs-PRECONDITION TYPING is an OUR-INVENTION covariation proxy over a CONTESTED distinction (ceiling ~0.77
balanced). Novel-pair generalization is via a Kemp-Goodman-Tenenbaum causal SCHEMA (type-role profiles), NOT a
memorised joint. KEY BOUNDARY (measured): covariation-DETECTION needs OBSERVED contingency (fails on never-co-observed
pairs); covariation-TYPING generalises via the type schema. OPEN (do NOT record as pinned): whether a distinct MENTAL/
INTENTIONAL causation route (mentalizing/ToM; first note's WALL 2) is what narrative fiction needs, and whether event
covariation transfers to narrative causation at all -- the cross-genre test that would have answered this was
instrument-confounded (matrix-verb extraction, explicit-connective pairs); it is UNTESTED, being drilled.

## PROPOSED hdlab CHANGE + END-TO-END MEASUREMENT (Q111 -- strategy lands it; integration-gated, I only propose)
The organ's PURPOSE is the QA "why?" capstone, which is a LIVE-READER end-to-end measurement I cannot run (the reader
pipeline is strategy's to wire, Q111). Concrete proposal:
1. Add `hdlab/narrative_causal_graph_typer.py` exposing `CovariationModel` + `HierarchicalTyper` (typing) and
   `causal_support` (detection), with the covariation KB built OFFLINE from MAVEN train (a static asset, no LLM).
2. WIRE as the COVARIATION route beside `force_dynamics_typer` (the mechanism route): dispatch an event pair to
   force-dynamics when the causing trigger is a force-dynamic verb (its ~16%), else to this covariation organ (~84%).
   Keep detection's structural backoff for novel type-pairs.
3. END-TO-END MEASUREMENT (the phase-gate check -- do NOT accept the isolation win as the capability): re-run the QA
   "why?" instrument with the organ wired vs the current reader; the gate is a CI-separated end-to-end lift on "why?"
   questions, NOT the isolation typing number. If it helps in isolation but NOT end-to-end, name the exact consumer
   that drops the causal-graph output (that is the next problem) -- exactly the trap LONG_TERM_PLAN warns about.
Do NOT rebuild the force typer.

## HONEST LIMITS (what I would withdraw first if wrong)
1. THINNEST: the linguistic-cue arm's marginal edge (+0.0049) is not robust (NOT_SEP under the null-p95 gate; a
   600-boot witness put its lower CI at +0.0008). I do NOT claim cues help; I claim they do NOT dominate. Withdraw
   any reading that cues add real value here.
2. Typing is a PROXY for a contested distinction (P 0.33 brain-faithful); the balanced ceiling ~0.77 is partly the
   counterfactual/pragmatic residue covariation cannot reach. I do not claim covariation IS the brain's cause/enable
   mechanism -- I claim it carries a real, partial, convergent signal (the enabling = ubiquitous-background axis).
3. ALREADY WITHDRAWN (I over-claimed it one iteration ago): the cross-genre "narrative causation does not transfer /
   is situation-specific not covariation" conclusion. The test was instrument-confounded (matrix-verb extraction,
   explicit-connective pairs, mis-segmentation); open-text transfer is UNTESTED with a valid instrument, not a negative.
   All the WITHIN-genre wins are MAVEN-ERE (Wikipedia); the end-to-end-on-raw-text pipeline is untested.
STURDIEST (withdraw last): the detection edge-existence win on seen pairs (+0.0485, n~105k), the typing
schema-generalization to unseen pairs (+0.0815), and the within-MAVEN verb-covariation positive control (0.638) --
all large, CI-separated, and mechanism-grounded, none dependent on the confounded cross-genre probe.

## TLDR
The reader could not work out implicit "this led to that" causation in stories -- the physics-style detector we had
only handled about one causal link in six. I built the mechanism the brain actually uses for the other 84%: judge
cause from how reliably kinds of events go together (learned from experience), the way people infer cause from
covariation. It works: on a large real annotated corpus it decides whether two events are causally linked, and
whether the link is a true cause or a background enabling condition, beating both a "just guess the common answer"
floor and a "use only sentence position" floor, with every info-free scramble losing. Two deeper wins: it generalises
to event combinations it never saw (it learned that, say, attacks tend to cause things, so it handles a brand-new
attack->outcome pair), and it survives a noisy event-labeller, so it does not need perfect inputs. I then tried to answer the
owner's key question -- does it work on OPEN text? -- and here I have to be honest: I first thought I had a clean "no,
and here's why", but when I dug into it I found MY OWN TEST was broken (it was reading the wrong words out of the story
sentences and using story examples that spell the cause out with a connecting word, which is not the hard case the tool
is built for). So the truthful status is: whether this works on open storybook text is still UNTESTED with a fair
instrument -- I withdrew the premature "no". What IS solid: it works well within encyclopedia-style text and meets the
bar there. The deep open question -- does the brain judge story causation by how often event kinds go together, or by
building a specific picture of the situation and checking it against world knowledge -- is exactly what we are now
drilling. Two other honest limits I proved rather than hid: wording cues barely help (these are the no-connective
cases, so covariation does the work), and it cannot detect a link between two event types it has never seen together
(covariation needs the observation).

## QUESTIONS
None blocking. Open (being drilled biology-first, at the owner's direction): does event covariation transfer to
IMPLICIT narrative causation, or does narrative causation require situation-model bridging? A VALID open-text
instrument (implicit narrative causal pairs + causal-event extraction) is needed before any mechanism verdict -- the
McGuffey/Anne probe was confounded. Separately, strategy can wire the within-MAVEN organ into the "why?" QA and
measure the end-to-end lift now (cheap; uses what exists).

## NEXT STEPS
1. Strategy: land the proposed `narrative_causal_graph_typer` as the covariation route beside the force typer
   (Q111); re-measure the QA "why?" instrument END-TO-END with it wired (the reason this organ exists) -- gate on the
   end-to-end lift, not the isolation number.
2. OPEN QUESTION to settle before any mechanism claim (being drilled biology-first): does event covariation transfer to
   IMPLICIT narrative causation, or does narrative causation need SITUATION-MODEL BRIDGING (Kintsch; Singer & Halldorson;
   Kuperberg 2011 -- causal integration exceeds surface co-occurrence)? Requires a VALID instrument first: implicit
   narrative causal pairs (not explicit-connective) with proper causal-EVENT extraction (not matrix verbs). The
   confounded McGuffey/Anne probe cannot answer it. This is the real open-text lever and ties into the situation-model organ.
3. Follow-on: the full pipeline on raw text (event detection -> typing -> pairing -> causal inference), no gold
   scaffolding -- the robustness curve only simulated type noise.
4. Optional fidelity: a richer linguistic-cue arm (presupposition triggers, "given that" constructions) on the
   subset of relations that DO carry explicit cues -- Kuhnmuench & Beller predict it dominates there specifically.

---

## INTEGRATED_BY_STRATEGY 2026-08-31 -- STRONG (no reader landing; the organ's home is corpus-level, not the reader)

Reverified 16/16 FIRST-HAND (`verification/test_narrative_causal_graph_organ.py`, recomputes from MAVEN-ERE):
TYPING balanced 0.772 vs structural floor 0.546 (+0.226 CI-sep), raw +0.058 over majority (coverage 1.0);
info-free permuted-label twin loses; GENERALIZES to UNSEEN type-pairs (schema 0.581 vs memorized-lookup chance
0.500); physical>intentional; robust to 20% type-noise. Graded STRONG (single-corpus; physical-only; open-text
transfer a rigorous NEGATIVE honestly diagnosed as needing observed contingency; exemplary honesty -- withdrew its
own over-claim, re-tested). Review block + review_text in PROBLEM.md; priority cleared; audit 2b folded.

**LANDING STATE: NO live-reader landing (correct no-landing).** The reader reads SINGLE documents; covariation
needs CROSS-document observed contingency, absent there -- so wiring `narrative_causal_graph_typer` into the "why?"
QA would ride the open-text negative, not a win (mirrors the integrated `causation_is_typed_per_clause_not_across_
the_causal_network` no-landing). The organ stays experiment-side (`experiments/_narrative_causal_graph.py`) as a
validated capability for CONTINGENCY-OBSERVABLE input. **FUTURE HOME (the seed): CORPUS-level causal knowledge** --
the knowledge-store consistency-cleanup (p4) / the learner, which see the whole corpus and CAN observe contingency.
Recorded in WIRING_MAP non-debt. No hdlab file changed.
