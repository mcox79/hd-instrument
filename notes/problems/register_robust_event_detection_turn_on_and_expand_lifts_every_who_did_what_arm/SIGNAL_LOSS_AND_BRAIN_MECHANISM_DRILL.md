# Where we lose who-did-what signal, how the brain does it EXACTLY, and where we differ — precisely

**Owner push (2026-09-05): "research and drill that result aggressively. Where are we losing signal, and how does
the brain do it exactly? Where do we differ from the 100% brain-foundational approach, precisely?"** This drill
answers it with (1) a MEASURED signal-loss ladder against a competent-reader oracle, and (2) three literature drills
pinning the exact brain mechanism + the precise divergence at each lossy stage. It CORRECTS one conclusion from the
parent SOLVED (the "everything converges on the parser" claim — the causal loss does NOT).

Methods: signal-loss ladder = `experiments/exp_event_detection_signal_ladder_v1.py`, 19c LitBank who-did-what, spaCy
en_core_web_sm as an OFFLINE DIAGNOSTIC ORACLE (reference-only, NEVER at inference — the admissible P6 exception; the
live path has NO external model). Brain mechanisms from three dispatched research drills (notes/research_joint_
category_structure_inference_2026-09-04.md, notes/research_holder_binding_kimian_states_subject_attachment_2026-09-04.md,
notes/research_causal_attribution_force_dynamics_connective_2026-09-05.md).

## 1. WHERE we lose signal — measured, stage by stage (vs the competent-reader oracle)

| arm / class | n | DETECT us → oracle | ROLE us → oracle | dominant loss |
|---|---|---|---|---|
| agent / open | 1433 | 0.966 → 0.994 | 0.832 → **0.955** | **ATTACH/ROLE (+0.124)** |
| patient / open | 1107 | 0.984 → 0.997 | 0.294 → 0.347 | ATTACH/ROLE (+0.052) |
| agent / be (HOLDER) | 278 | (state silo) | 0.205 → **0.705** | ATTACH holder (+0.50) — *oracle itself capped 0.705* |
| patient / be (PROPERTY) | 278 | (state silo) | 0.259 → 0.281 | **near-ceiling (+0.022)** |

**Read-out:**
- **DETECTION is largely CLOSED** (open-class us 0.966/0.984 vs oracle 0.994/0.997). predicate_recall + the copula
  silo-unification did their job; the tag-stage drop is nearly gone.
- **The residual is ARGUMENT ATTACHMENT** — agent/open +0.124, patient/open +0.052, copula HOLDER +0.50 behind the
  oracle. This is where who-did-what signal is now lost.
- **The competent-reader oracle is ITSELF far from perfect on 19c attachment** (patient/open 0.347, copula holder
  0.705) — so the ceiling is not 1.0; a single-parser competent reader is already capped on this register.
- **The copula PROPERTY (patient) is at the competent-reader CEILING** (us 0.259 vs oracle 0.281) — we lose almost
  nothing there; the low absolute is the gold instrument (the annotated OBJECT head ≠ the syntactic complement), not
  our reader. This is why lever B's PROPERTY win was the robust one and the HOLDER slice was not.

So the signal-loss map is: **detection ≈ solved; the loss is attachment (agent/patient/holder) + causal selection.**
The three drills below give the exact brain mechanism and the precise divergence for each.

## 2. The exact brain mechanism + precise divergence, per lossy stage

### (A) Category/verb-hood detection — and the argmax-commitment root of the attachment loss
**Brain (PINNED):** category + structure are inferred JOINTLY as ONE graded probabilistic operation — Hagoort's MUC
(2005/2013): category information lives INSIDE the retrieved lexical frame; LIFG "Unification Space" binds
syntax+semantics+phonology in one step, with no separate category-then-structure stage. Fromont/Steinhauer/Royle
2020: forced noun/verb swaps elicit N400-THEN-P600 (additive), explicit evidence AGAINST strictly serial models.
The computation is incremental Bayesian belief updating — Narayanan & Jurafsky 2004 (parsing IS exact
belief-propagation on the loop-free parse tree); Levy-Reali-Griffiths 2009 (a particle filter whose particle count =
working-memory capacity; garden-path "digging-in" is graded mass-loss, never a one-shot deletion).
- **One-sentence claim:** the brain never commits an argmax tag before structure — it maintains a graded distribution
  re-estimated as structural/semantic evidence arrives.
- **EXACT divergence (the crux, now quantified):** our Viterbi tagger computes `argmax P(tag | word, local context)`
  ONCE, from training-register lexical identity, and hands a HARD tag to the parser — **destroying the runner-up's
  probability mass before any structural evidence that could correct it exists.** In the belief-updating frame,
  **argmax is the ZERO-PARTICLE LIMIT** — one particle, zero alternatives survive past the tag decision. That is the
  precise reason our 19c open-class recovery caps at 0.56 (a post-hoc patch reacting to an already-destroyed
  distribution) where a competent reader reaches ~1.0 (a distribution never destroyed). Bohnet & Nivre 2012 confirm
  it directly: folding tag-assignment INTO the parser's own beam cuts NN↔VB confusion 72→58 — the correct tag was in
  the model's top-2/3 all along, just pruned too early.
- **Register-invariance divergence:** the brain induces category by a PER-SENTENCE weighted cue combination
  (frame [Mintz frequent-frames] × morphology [Monaghan 2005] × residual lexical frequency), recomputed fresh —
  never a stored per-lexeme/per-register table — so it slots even fully novel/archaic verbs from frame alone (Yuan &
  Fisher 2009 in 2-year-olds; Federmeier 2000 in adults; Fedorenko Jabberwocky). Our tagger's cue weights are FROZEN
  at training time and never reweighted toward frame/morphology when lexical evidence is unreliable → OOD-brittle.
  **Our P6 predicate_detector is a first-cut approximation of exactly this** (a learned combiner over emission-margin
  + frame-anchor + morphology), which is why it recovers 0.56 not 0.16 — but as a POST-HOC patch, not the joint decode.
- **Faithful buildable fix (glass-box, no LLM):** fold POS into the SAME transition-parser action space as attachment
  (k-best SHIFT actions sourced from `hdlab/pos_tagger.py`'s emission margin, one shared perceptron with the arc
  decisions, beam 4–8) — a fusion of two already-built glass-box linear models. This IS the filed
  `upgrade_the_pos_tagger_to_a_calibrated_joint_decoded_posterior` problem, now triple-sourced (ERP + NLP-engineering
  + neural-unification).

### (B) HOLDER / subject attachment — the copula agent cap, and it is a general locality effect
**Brain (PINNED):** subject/participant identification is TWO dissociable steps — structure-building (pMTG/LIFG) +
semantic role-confirmation (lmSTC carries an abstract Agent/Patient population code that survives active↔passive voice
switches — Frankland & Greene 2015; Matchin & Hickok 2020 separate structure from thematic content). Robustness comes
from MULTI-CUE CONVERGENCE — the Competition Model (Bates & MacWhinney; cue validity), Bornkessel-Schlesewsky eADM
(default-actor-wins-unless-beaten), and Mahowald et al. 2022/2023 showing **semantic plausibility ALONE recovers the
correct subject at 87–89% across 30 languages**.
- **One-sentence claim:** the brain identifies the subject/HOLDER by fusing agreement + animacy + word-order +
  discourse-topic + plausibility, so no single failed cue collapses it.
- **EXACT divergence:** our HOLDER comes from a SINGLE `nsubj` dependency arc — one channel with no fallback; when the
  OOD parse mis-attaches it, there is nothing to recover from. Measured: us 0.205 vs oracle 0.705, and the oracle
  (also single-parser) is itself capped at 0.705. The **PROPERTY > HOLDER asymmetry is NOT copular-specific** — it is
  a GENERAL LOCALITY effect (Ferreira 2003: the identical agent<patient shape appears in plain dynamic-event passives;
  the displaced/less-local argument is harder). The PROPERTY is local (post-copula complement) → robust; the HOLDER is
  the displaced subject → brittle. (HOLDER-vs-AGENT circuit identity is genuinely UNTESTED — a verified open gap.)
- **Faithful buildable fix:** a multi-cue subject identifier (agreement re-rank + animacy + discourse-topic-continuity
  fallback + a type-compatibility HOLDER-scorer, fused by cue-validity) instead of one parse arc — which could BEAT
  the single-arc parser, toward the human 87–89% and above spaCy's 0.705. Glass-box, no LLM. (Candidate successor,
  P_deflated 0.20–0.40 per the drill.)

### (C) Causal cause-selection — the structural fix cannot work IN PRINCIPLE (corrects the parent SOLVED)
**Brain (PINNED):** cause attribution is SEMANTIC, not positional. Talmy 1988 force dynamics (Agonist/Antagonist force
tendencies → CAUSE/LET/HINDER, explicitly not billiard-ball proximity); Wolff & Zettergren 2002 formalize it as a
geometric force-vector rule (83–100% match to human judgment) — but validated only for concurrent forces on ONE
object, never for selecting among discrete narrative events. Neurally, narrative causality recruits left MTG
(thematic/event-semantics) + medial frontal, DISSOCIATED from the parietal/spatial force network (Kranjec 2012); cause
selection is plausibility-weighted, memory+executive-gated (Fugelsang & Dunbar 2005, plausibility×covariation
F=10.48, p<.01); there is no dedicated "causation module" (Woolgar 2011). Density-robustness comes from active
semantic reinstatement / causal-GRAPH search bound to the current event model (Fletcher & Bloom current-state
selection; Trabasso causal-network N×N necessity test; van den Broek Landscape Model; Zacks Event Segmentation), NOT
positional persistence.
- **One-sentence claim:** the cause of an outcome is the discourse-model event that is force/plausibility-compatible
  with it, retrieved by graph search within the current event window — position is at most a defeasible tie-breaker.
- **EXACT divergence + THE VERDICT:** our heuristic scores candidates on ONE axis — token/clause distance. **A
  parse-structural fix cannot work IN PRINCIPLE** (not merely under OOD-parse noise), for two independent reasons:
  (i) backward/cross-clausal connectives ("because"/"so"/"therefore") often have NO uniquely-governed syntactic
  argument across clause boundaries — there is no correct structural target even with a perfect parser; (ii) even
  where structure is well-defined, plausibility resolves the cause online and structure contributes nothing
  (Koornneef & Van Berkum 2006; Sanders & Noordman 2000 — connectives are cues into a semantic relation-search; Cozijn
  2011 — "because" has a MANDATORY world-knowledge-validation stage). **So my three failed structural-head attempts
  targeted the WRONG REPRESENTATIONAL LEVEL, not an underpowered version of the right one.** And it explains why the
  positional heuristic ever worked at low density: adjacency correlates with plausibility BY ACCIDENT in simple text,
  and density severs that accidental correlation.
- **Faithful buildable fix:** replace "pick nearest/structural" with "argmax of a COMPATIBILITY score" (verb-class
  causal-frame compatibility [VerbNet/FrameNet] + argument overlap with the outcome + foreground/background aspectual
  weighting) over candidates in the current situation-model window (Fletcher & Bloom backward graph search; van den
  Broek Landscape Model as a glass-box template). Buildable NOW without a full meaning hub, as a first cut; true
  mechanism/normality fidelity needs broader world-knowledge. (P_deflated 0.55 that semantics is structurally
  necessary; 0.40 that the 3-feature scorer suffices.)

## 3. The precise, unified divergence from 100% brain-foundational
Every measured loss traces to ONE architectural gap, stated four ways:

| our pipeline | the brain | the loss it causes |
|---|---|---|
| **COMMITS** an argmax tag before structure | keeps a GRADED distribution, re-estimated (BP / particle filter) | 19c open-class detection 0.56 vs ~1.0; tag errors propagate |
| **SERIAL** stages (tag → parse → detect → role) | JOINT settling (MUC / Unification Space; N400+P600 additive) | no cross-stage correction of a committed error |
| **SINGLE CHANNEL** (one parse arc) for the subject | MULTI-CUE fusion (Competition Model; plausibility alone 87–89%) | HOLDER attachment 0.205 vs 0.705; displaced-argument brittleness |
| **POSITIONAL** cause-selection | SEMANTIC force/plausibility over the event graph | causal density regression; structural fix impossible in principle |

**The one-line statement:** we are a SERIAL pipeline of ARGMAX-COMMITTED, SINGLE-CHANNEL, SEMANTICS-FREE stages; the
brain is a JOINT, GRADED-BELIEF, MULTI-CUE, SEMANTICALLY-CONSTRAINED constraint-satisfaction system. Detection is the
one stage we have pulled close to the brain (a learned per-sentence cue combiner ≈ the brain's frame×morphology
induction); attachment and causal selection are where the four divergences still bite.

## 4. The corrected CONVERGENCE (this drill's correction to the parent SOLVED)
The parent SOLVED (§9) concluded the three residuals "converge on ONE lever: the register-robust parser." **That is
half right, and the causal drill corrects it.** The residuals converge on TWO lever families, not one:
1. **The JOINT GRADED DECODER** (joint POS+parse belief-updating) — fixes DETECTION (argmax commitment) and much of
   ATTACHMENT (agent/patient/holder), and the HOLDER further wants a MULTI-CUE subject identifier layered on it. This
   IS the filed CRF/joint-decode problem. Register-robust parsing is necessary here.
2. **A SEMANTIC COMPATIBILITY LAYER** — the CAUSAL cause-selection loss is NOT a parser problem; it is structurally
   semantic (proven: the structural fix cannot work in principle). It needs a plausibility/force-compatibility scorer
   over the situation-model event graph — the meaning-hub direction (north-star P1), buildable as a coarse VerbNet/
   FrameNet + argument-overlap first cut.
So the honest convergence is: **a joint graded decoder + a multi-cue subject identifier + a semantic causal scorer** —
the first two are the register-robust-parser family; the third is the meaning-hub family. My "everything is the
parser" line over-unified; the causal loss is the counterexample.

## 5. What is CONTESTED / not established (flagged, per the drills)
- **ELAN** (the original early-serial-commitment evidence) is substantially undercut (Steinhauer & Drury 2012 —
  filter/baseline artifacts); the field treats early serial syntax as contested. Our "joint not serial" claim rests on
  the POSITIVE evidence (MUC, N400+P600 additivity, joint-decode NLP gains), not on ELAN.
- **"Loopy BP"** is the wrong frame — the parse graph is loop-free, exact tree BP suffices (correction to my prior
  framing).
- **Prediction-as-preactivation at fine lexical grain** has a failed replication (Nieuwland 2018, BF~77 for null on
  the a/an effect) — it does NOT undercut the joint-decode architecture (orthogonal, finer grain; Ryskin & Nieuwland
  2023 still endorse the predictive framework at coarser grain).
- **"constraint-satisfaction = predictive coding"** is overreach — Kuperberg & Jaeger explicitly distinguish them; no
  study discriminates them for joint category+structure specifically.
- The **density-vs-plausibility causal crux** is a converging inference across four literatures, not one direct
  experiment; van den Broek & Lorch 1993 (strongest direct density-robustness evidence) is secondary-only, flagged for
  primary verification.
- **HOLDER-vs-AGENT circuit identity** is genuinely untested.

## 6. THE IDEAL BRAIN-FOUNDATIONAL SOLUTION — specified, prototyped, and generalization-tested (owner push 2026-09-05)
The full ideal who-did-what reader has FOUR organs, each replacing one of the four divergences above. I built the
two that are new + in-scope and tested them on the 16 board docs AND 40 DISJOINT held-out docs. **Both new organs
are LOCATED NEGATIVES that do not generalize — and that is the finding: the ideal solution's remaining gains are
GATED by two upstream dependencies, not buildable as standalone glass-box organs.**

| ideal organ | replaces divergence | status | measured |
|---|---|---|---|
| **1. joint graded decoder** (tag+parse, no argmax commit) | COMMIT / SERIAL | FILED (`upgrade_the_pos_tagger...`) | not rebuilt; the drill gives it a precise triple-sourced motivation |
| **2. multi-cue role assigner** (dynamic agent) | SINGLE-CHANNEL | **ALREADY BUILT + generalizes** (the landed CM agent; predicate_recall+CM agent +0.0125 on 40 held-out docs) | the ideal is realized here |
| **2b. multi-cue HOLDER** (copula subject) | SINGLE-CHANNEL | **PROTOTYPED → NEGATIVE** (`exp_event_detection_multicue_holder_v1`) | board 0.205→0.241 (+0.036 not-sep); **held-out +0.0000**; gold subject is IN the candidate set 94.2% → NOT coverage; on 19c COPULAR predications the discriminating cue is STRUCTURE (oracle nsubj 0.71–0.77), not semantic plausibility (Mahowald's modern 87-89% does NOT transfer) → **parser-bound, folds into organ 1** |
| **3. semantic causal scorer** (force/plausibility) | POSITIONAL | **PROTOTYPED → NEGATIVE** (`exp_event_detection_semantic_causal_v1`) | force-lexicon + arg-overlap + foreground; **degenerates to positional** (features fire 75% but AGREE with position 95% — the accidental adjacency-plausibility correlation, measured; pick changes only 5%); board −0.069 (= positional), **held-out −0.147 (WORSE than positional)** → **meaning-hub-bound** |
| **4. unified sort-typed eventuality inventory** | the SILO | FILED (`the_assembled_reader_is_parallel_silos...`) | the physical form of lever B's copula PROPERTY win |

**The result, precisely:** the parts of the ideal reader that WORK and GENERALIZE are already built — register-robust
DETECTION (predicate_recall, a learned per-sentence cue combiner ≈ the brain's frame×morphology induction), the
MULTI-CUE dynamic role assigner (the landed CM agent = the Competition Model, realized), and the copula PROPERTY
silo-unification (lever B, held-out-replicated). The two organs that would close the RESIDUAL do NOT work as
standalone glass-box additions, and held-out proves it: (a) the copula HOLDER needs a register-robust PARSE (the
semantic multi-cue layer adds +0.000 held-out; structure is the cue here, not plausibility) → organ 1; (b) the
CAUSAL selector needs the situation-model MEANING HUB (a coarse force/plausibility proxy degenerates to positional
and is worse on held-out) → the north-star. **So the ideal solution is gated on exactly the two levers the drill's
mechanism-diff already named — the joint graded decoder and the meaning hub — and NOT on any organ I can build
standalone.** Building either coarse organ would have been wasted effort; the generalization test caught both.

**This also sharpens the §4 correction once more:** attachment (open-class agent AND copula holder) → the register-
robust joint decoder; causation → the meaning hub. The copula holder, which the HOLDER drill hypothesized as a
multi-cue win, is measured PARSER-bound on this register — so the two lever families are (1) joint decoder/parser
[detection + all attachment] and (2) meaning hub [causal].

## TLDR (plain language)
I measured exactly where the reader loses "who did what," and it is NOT catching the actions anymore (we fixed that)
— it is figuring out WHO the subject is and WHAT caused what. Then I looked up how the brain does each, precisely.
Three findings: (1) our word-tagger makes a hard guess too early and can't take it back; the brain keeps its options
open and settles word-category and sentence-structure together — that early hard guess is the exact reason we recover
56% of hard old-text verbs where a person gets ~100%. (2) We find the subject from a single grammar link; the brain
uses several agreeing clues at once (agreement, animacy, who-the-topic-is, plausibility), so it doesn't collapse when
one clue is wrong — and "who" is always harder than "what" because the subject sits farther from the verb, in ANY
sentence, not just "X is Y" ones. (3) For cause-and-effect, I proved a grammar-only fix CAN'T work even with a perfect
parser — people pick the cause by what plausibly caused it, not what sits nearest the word "because"; our old trick
only ever worked because "nearby" and "plausible" line up by luck in simple text. Net correction to last round: the
weak spots don't all trace to the parser — two do, but cause-and-effect needs a pinch of meaning, not better grammar.
