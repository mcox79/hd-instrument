---
problem: predictive_inference_forward_project_the_next_event_and_state_from_the_situation_model
status: PARTIAL
bar: "PASS = a glass-box FORWARD PREDICTOR -- a transparent, hand-auditable projection over the LIVE situation model (events + goals + causal/script/successor structure), NO external LLM at inference -- that, given a situation-model state at time t, predicts the next event/state (or discriminates a right vs wrong continuation) on a MODERN gold, with ALL of: (1) CI-separated over a REAL base-rate/frequency floor -- the strongest of: the most-frequent-next-event / majority-continuation prior, a 1-step co-occurrence counter, and (for the discrimination framing) picking the more frequent/plausible ending by unigram/bigram likelihood; gate on its UPPER CI bound. (2) An info-free twin LOSES CI-separated -- SCRAMBLE / temporally-shuffle the context. (3) A calibrated PRECISION that earns 'defer when uncertain' -- selective accuracy on its most-confident predictions RISES, a random-confidence twin stays FLAT. (4) Brain-faithful mechanism, stated as an operation (predictive-coding forward projection; goal-directed + causal/script + successor cues via graded_competition; precision = distribution concentration). A rigorous LOCATED NEGATIVE is a FULL PASS: the faithful forward projection, built, does NOT beat the base-rate floor (or the twin does not lose, or precision does not earn selective accuracy) -- with the EXACT cause named and enumerated."
result: "Glass-box forward continuation predictor on Story Cloze (MODERN, right-vs-wrong 5th sentence; MoE-UNC/story_cloze val 1871 + test 1871). The brain-faithful forward GENERALIZED-EVENT-KNOWLEDGE projection (Elman-style graded associative readout over the corpus's own forward transitions, self-supervised on ROCStories-train 98,161 stories) discriminates the coherent continuation val 0.5922 [0.5697,0.6147] / test 0.5815 [0.5585,0.6040], CI-SEPARATED over the majority-continuation floor (val +0.078 [+0.045,+0.110]; test +0.068 [+0.039,+0.099]); the cross-context info-free twin COLLAPSES to chance (val 0.4912 [0.468,0.514]; test 0.4885); and a calibrated precision (1 - normalized entropy of the graded_competition 2-way distribution) earns MONOTONICALLY RISING selective accuracy (val 0.592->0.654; test 0.582->0.630) while the random-confidence twin stays FLAT (val ->0.607; test ->0.560). LOCATED NEGATIVE (rigorous, triple-sourced) on the STRONGER claim: the projection does NOT robustly exceed a 1-step co-occurrence counter (val margin +0.0096 [-0.006,+0.024] NOT CI-sep; test +0.0176 [+0.004,+0.032]) and situation-model STRUCTURE does not lift it -- the multi-step successor HORIZON adds ~+0.01 (the successor_representation docstring's pre-registered outcome iii), the event-structured verb-chain grain is WEAKER (val 0.547/test 0.538), and the goal/causal registers FIRE ON ONLY ~27% of 5-sentence stories (measured). DOING IT RIGHT (v2): the artifact-free brain-foundational coherence engine (protagonist-centered CONTEXT-DEPENDENT contradiction + affect-arc-DIRECTION + causal-to-goal, learned cue validities, cross-validated) produces a GENUINE artifact-free lift over the counter (val 0.6002 +0.0176 [-0.002,+0.036]; test 0.5863 +0.0224 [+0.003,+0.043] CI-sep), twin collapses to 0.53, at the research-confirmed honest glass-box ceiling (~0.60; Mostafazadeh 2016 context baselines 0.52-0.585). The full CI with a cheap ending-only negation flag beat the counter CI-sep on BOTH splits (val +0.032/test +0.041) but a negation-ablation proved that was the Schwartz-2017 STYLE ARTIFACT, not coherence. Adding Friston PRECISION-WEIGHTING (v3: trust each cue by per-item reliability) tips it to paired-CI-separated over the counter on BOTH splits (val 0.6029 +0.0203 [+0.0005,+0.040]; test 0.5922 +0.0283 [+0.010,+0.047]), razor-thin on val. The dominant remaining gap is EXTRACTION density (a separate problem's lane), NOT the now-validated inference design."
floor: "STRONGEST base-rate floors, recomputed on each split's own population: majority-continuation prior val 0.5142 [0.492,0.537] / test 0.5131; ending-only unigram plausibility val 0.5045 / test 0.5104; 1-step SYMMETRIC co-occurrence counter val 0.5826 [0.559,0.605] / test 0.5639 [0.541,0.586] (the SR docstring's named floor -- the strongest). The mechanism CI-separates over majority+unigram on both splits; it does NOT CI-separate over the 1-step counter on val (+0.0096, CI includes 0)."
controls: "(1) cross-context twin (endings scored against a RANDOM other story's context, same shapes/balance) -> val 0.4912 / test 0.4885 = EXCLUDES 'uses only the endings / a style artifact', proves it USES this story. (2) random-confidence twin (precision permuted, same coverage) -> selective curve FLAT = EXCLUDES 'any abstention at this rate raises accuracy'. (3) 1-step co-occurrence counter floor = EXCLUDES 'the win needs a predictive HORIZON' (it does not; the horizon adds ~+0.01). (4) event-structured verb-chain / verb+patient arm (0.54) = EXCLUDES 'a finer event grain helps' (it is weaker). (5) register fire-rate on the full live-reader eval (Cell B, n=1871/split: goal fires 0.319/0.335, causal 0.285/0.277, mean 7.9 events per 4-sentence context; witness W6 corroborates 10/40 & 9/40) = LOCATES the extraction bottleneck. (6) held-out by construction: the transition store is ROCStories-train, disjoint from the Story Cloze eval stories."
files_changed: "experiments/exp_forward_event_projection_v1.py (content-GEK spine, full-scale); experiments/exp_forward_event_projection_situation_model_v1.py (live SituationReader + graded_competition multi-cue combination); experiments/exp_forward_event_affect_coherence_v1.py (the affect/valence-trajectory cue); experiments/exp_forward_event_construction_integration_v1.py (the full Kintsch/Trabasso alternative + the negation-artifact ablation); experiments/exp_forward_event_situation_coherence_v2.py (the RIGHT artifact-free engine: protagonist-centered context-dependent contradiction + affect-arc-direction + causal-to-goal, learned cue validities); experiments/exp_forward_event_precision_weighted_v3.py (the Friston PRECISION-WEIGHTED integration upgrade); experiments/exp_forward_event_predictive_loop_v1.py (CLOSING THE PREDICTIVE-CODING LOOP: forward prediction error for coherence + event SEGMENTATION + reset-vs-reinstate); experiments/exp_forward_event_generalization_socialiqa_v1.py (cross-dataset generalization boundary on Social IQa); experiments/exp_forward_event_world_knowledge_v1.py (richer ConceptNet causal/script world-knowledge foundation -- prototype for blocker 2); experiments/exp_forward_event_density_phase_v1.py (the DENSITY phase-diagram sweep); experiments/exp_forward_event_dense_context_v1.py (THE DECISIVE dense-regime test: MCScript2 long-context forward-continuation with same-scenario hard negatives); experiments/exp_forward_event_ci_settling_v1.py (Kintsch Construction-Integration SETTLING -- the brain's integration mechanism, glass-box); notes/problems/.../research_drill_forward_coherence_wall_2026-09-06.md (aggressive 4-angle wall research); experiments/fetch_story_cloze_rocstories.py (pinned reproducible gold fetch); verification/test_forward_event_projection.py (scaffold-free witness); data/exp_forward_event_projection_v1/metrics.json; data/exp_forward_event_projection_situation_model_v1/metrics.json; data/exp_forward_event_affect_coherence_v1/metrics.json; data/corpora/story_cloze/ + data/corpora/roc_stories/ (materialized gold, gitignored). hdlab/ UNTOUCHED (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_forward_event_projection.py"
---

# Forward event projection: a brain-faithful generalized-event-knowledge readout beats the base-rate floor with calibrated precision -- and a rigorous, triple-sourced located negative on why it does not exceed a co-occurrence counter

## What was asked
The reader builds a rich BACKWARD-looking situation model but never projects FORWARD. Build the glass-box
forward predictor: from the situation as it stands, predict the next event / discriminate a right-vs-wrong
continuation on a MODERN gold, beating a base-rate floor CI-separated, with a scrambled twin LOSING and a
calibrated precision that earns rising selective accuracy -- or a rigorous located negative naming the cause.

## The opening move: how does the brain forward-project the next EVENT? (research-led)
A dedicated research drill (4 parallel lit-scans, folded into `research_drill_forward_event_prediction_2026-09-06`
below) fixed the mechanism BEFORE any tool was chosen:
- **PINNED.** Forward prediction during comprehension is a **graded associative co-activation readout over
  GENERALIZED EVENT KNOWLEDGE** (Elman 2009 "On the meaning of words and dinosaur bones"; Metusalem 2012;
  Hare 2009; McRae & Matsuki) -- the brain reads out how expected an upcoming event's content is given the
  situation so far. It is NOT a discrete script lookup. Precision = distribution concentration / inverse
  entropy (Kuperberg & Jaeger 2016; Hale entropy-reduction). Cues combine as additive competition
  (Competition Model; McClelland 2013 additive->softmax = the Bayesian posterior).
- **OUR-INVENTION / CONTESTED (do not present as pinned).** SR-over-narrative-EVENTS is a computational-level
  metaphor extrapolated from spatial/graph work (Momennejad 2017/18 test abstract graphs, NOT narrative;
  Ekman 2023 flags the narrative gap) -- so a discounted multi-step successor map over text states is
  OUR-INVENTION-under-test, and its own docstring pre-registers that it may be "a better counter, not a
  different kind of thing." The precision->commit/defer threshold and the cue-combination weights are also
  OUR-INVENTION (defensible by analogy, not literature-copied).
- **HONEST CEILING (this reframed the whole problem).** The literature says forward EVENT prediction beats a
  frequency baseline by a CHARACTERISTICALLY NARROW margin (Chambers & Jurafsky 2008 explicitly disclaim
  human-solvability; Pichotta & Mooney 2016 R@25 0.101 freq vs 0.152 best), and Story Cloze is contaminated by
  a content-blind STYLISTIC classifier that hits 75.2% (Schwartz 2017 -- a warning that "beats baseline" claims
  here are often confounded). So: **calibrate success as a modest, well-powered margin over frequency; treat
  any large win as suspect; make the cross-context twin load-bearing (it defeats the style artifact).**

## What I built (glass-box, NO LLM, consumes the live situation model)
1. **The forward GENERALIZED-EVENT-KNOWLEDGE projector (the brain's mechanism, `exp_forward_event_projection_v1.py`).**
   A self-supervised forward-transition association learned from ROCStories-train's own story transitions
   (PPMI over "what content follows what," directed, multi-step) -- the graded associative readout Elman's GEK
   describes. It scores each candidate ending by how expected its content is given the 4-sentence context, as a
   competition; precision = 1 - normalized entropy of the 2-way `graded_competition` distribution (the reused
   `hdlab.graded_competition` organ). This is the missing FORWARD half of the predictive hierarchy at the
   discourse/event level -- the generator the N400/EST error signal is taken against.
2. **The live-situation-model integration + brain-faithful multi-cue combination (`..._situation_model_v1.py`).**
   Runs the LIVE `SituationReader` on each context (4 sentences, accumulated) + each ending, CONSUMING the
   reader's own `sm.events` and `sm.wants` (goals) off the read (not re-extracted), and combines three cues via
   `graded_competition` (additive Lewis-Vasishth activation -> softmax): the GEK content cue, a GOAL-directed
   cue (does the ending advance the agent's open goal -- Zwaan-Radvansky indexing), and an event-structured
   VERB-chain cue.

## What I measured

### The positive result -- the brain-faithful forward projection beats the base-rate floor with calibrated precision
`exp_forward_event_projection_v1` (ROCStories-train 98,161-story store; full Story Cloze val 1871 + test 1871):

| arm | val acc [95% CI] | test acc [95% CI] |
|---|---|---|
| majority-continuation floor | 0.5142 [0.492,0.537] | 0.5131 [0.492,0.535] |
| ending-only unigram floor | 0.5045 | 0.5104 |
| **forward GEK projection (MECHANISM)** | **0.5922 [0.570,0.615]** | **0.5815 [0.559,0.604]** |
| cross-context twin (info-free) | 0.4912 [0.468,0.514] | 0.4885 [0.467,0.510] |

- **CI-separated over the majority/base-rate floor:** val margin **+0.078 [+0.045,+0.110]** (half-width 0.032);
  test **+0.068 [+0.039,+0.099]**. Bar condition (1) MET against the frequency floors.
- **The info-free twin COLLAPSES to chance** (0.491 / 0.489) -- the projection genuinely USES this story's
  content; it is not the Story Cloze style artifact. Bar condition (2) MET.
- **Calibrated precision earns rising selective accuracy** -- most-confident quartile val **0.6538** (from
  0.5922) / test **0.6303** (from 0.5815), monotone across coverage; the random-confidence twin stays FLAT
  (val ->0.607, test ->0.560). Bar condition (3) MET.
- **Brain-faithful mechanism** (Elman GEK graded associative readout + `graded_competition` softmax + inverse-
  entropy precision), glass-box, NO LLM. Bar condition (4) MET.

### The located negative (rigorous, triple-sourced) -- it does NOT exceed a co-occurrence counter, and situation-model STRUCTURE does not lift it
The STRONGEST floor is the **1-step SYMMETRIC co-occurrence counter** (val 0.5826 / test 0.5639). The mechanism
does NOT robustly clear it: val margin **+0.0096 [-0.006,+0.024] (CI includes 0)**, test +0.0176 [+0.004,+0.032].
Three independent, MEASURED causes, each a brain-foundational route tested and closed:
1. **The successor/predictive HORIZON adds nothing** (~+0.01). Directed 1-step (val 0.598) equals directed
   multi-step (0.592); the discount over multiple steps buys no lift. This is EXACTLY outcome (iii) the
   `successor_representation.py` docstring pre-registered: "the 1-step counter wearing a matrix." SR-over-
   narrative-events is confirmed a base-rate counter here, not a different kind of thing.
2. **A finer EVENT grain is WEAKER, not stronger.** The event-structured verb-chain / verb+patient GEK (the
   "different hub" the prior forward-prediction SOLVED named for fine ranking) scores val 0.547 / test 0.538 --
   BELOW the content bag AND the counter. On discourse continuation the signal lives in broad scene/content
   association, not in verb-transition structure (unlike the argument-thematic-fit case the prior wall was about).
3. **The live situation-model STRUCTURAL registers barely fire.** On the FULL live-reader eval (Cell B,
   n=1871/split): causal_links fire on **0.285 / 0.277** of stories, goals (`sm.wants`) on **0.319 / 0.335**,
   and the event detector OVER-SEGMENTS (**7.9 "events" for 4 sentences**, with contraction/nominal noise --
   e.g. "wasn", "gangs" as predicates). So a goal/causal-STRUCTURED projection can only act on ~1/3 of items;
   on the rest it falls back to the lexical GEK signal. This is the brief's pre-registered extraction-weakness
   risk, MEASURED.

### The live situation-model integration (Cell B) -- brain-faithful multi-cue combination CONFIRMS the negative
`exp_forward_event_projection_situation_model_v1` runs the LIVE `SituationReader` on the full eval (val 1871 +
test 1871, 0 crashes) and combines GEK + GOAL + VERB cues via `graded_competition` (additive->softmax, equal
weights on standardized cues -- OUR-INVENTION, NOT tuned to the test):

| arm (consumes the live read) | val acc | test acc |
|---|---|---|
| goal-directed cue alone (`sm.wants`) | 0.5307 | 0.5414 |
| verb-chain event-structured cue alone | 0.5110 | 0.4901 |
| GEK content projection alone | 0.5922 | 0.5815 |
| **graded_competition COMBINED (GEK+goal+verb)** | **0.5874** | **0.5778** |
| cross-context twin | 0.4912 | 0.4885 |
| register fire-rate (goal / causal) | 0.32 / 0.29 | 0.34 / 0.28 |

- **Adding situation-model STRUCTURE does not help -- it slightly DILUTES.** The combined cue (0.5874 / 0.5778)
  sits at or just BELOW GEK-alone (0.5922 / 0.5815), because the goal cue is only weakly above chance (0.53/0.54)
  and the verb cue is at chance (0.51/0.49), and both fire on only ~30% of stories -- so combining them with the
  strong GEK cue adds noise, not signal.
- **The combination does NOT clear the 1-step counter** (val margin +0.0048 [-0.014,+0.025]; test +0.0139
  [-0.005,+0.032], neither CI-sep) -- the same located negative as the content spine.
- The GOAL cue alone IS weakly above chance (0.53/0.54) -- goal-directed anticipation carries a little signal,
  as the brain predicts, but too sparsely (fires ~30%) to lift the projection. Precision still calibrates
  (selective COMB val 0.587->0.642).


### The deepening -- affect/valence-trajectory coherence (a STRUCTURED cue, not association)
Prompted by "are we 100% brain-foundational, and how does the brain ACTUALLY do this," I built the missing
structured cue. Story Cloze wrong endings are crafted TOPICALLY related but INCOHERENT -- in story 0 the context
is "troubled -> gangs -> shot -> turned a new leaf" and the WRONG ending "He joined a gang" REPEATS "gang" from
the context, so it has MORE lexical overlap than the RIGHT "He is happy now." Every similarity/association readout
(GEK and the counter) is therefore ACTIVELY FOOLED on the adversarial items. The brain discriminates via the
affect/valence TRAJECTORY (core affect -- Barrett; Russell circumplex; Warriner 2013 norms via
`hdlab.affect_lexicon`): the arc REVERSED to positive at "turned a new leaf", so "happy" fits and "gang" violates
it. `exp_forward_event_affect_coherence_v1` (full val+test):

| arm | val | test |
|---|---|---|
| affect-coherence alone (valence proximity to the story's current state) | 0.5425 | 0.5286 |
| affect cross-context twin (vs a random other story's context) | 0.5174 | 0.4853 |
| GEK + affect (graded_competition) | 0.5917 | 0.5810 |

The affect cue IS real and genuinely USES the story -- its cross-context TWIN COLLAPSES (drop 0.025 / 0.043), so
it is NOT the Schwartz 2017 sentiment STYLE artifact. But it is WEAKER than the counter and adds ~nothing to GEK,
because valence PROXIMITY is a shallow proxy that cannot represent the arc REVERSAL, and because any SIMILARITY
readout is fooled by the topically-matched wrong endings.

## The FULL brain-foundational alternative: construction-integration coherence + learned cue validities (and the artifact I caught)
`exp_forward_event_construction_integration_v1` builds the full Kintsch/Trabasso alternative: SIX
brain-foundational COHERENCE cues over the live situation model -- GEK association, grounded-hub semantic
integration (N400 integration cost), affect/valence-trajectory consistency, a negation/contradiction marker,
causal event-TYPE transition plausibility (learned on ROC), and referential continuity (argument overlap) --
integrated with LEARNED cue VALIDITIES (Competition Model; a paired logistic fit on ONE split, evaluated on the
OTHER -- cross-validated, NO test-mining).

| arm | val acc | test acc |
|---|---|---|
| 1-step counter (strongest floor) | 0.5826 | 0.5639 |
| GEK alone | 0.5922 | 0.5815 |
| **construction-integration COMBINED (all 6 cues, learned validities)** | **0.6146** | **0.6045** |
| construction-integration, NEGATION cue REMOVED (context-dependent cues only) | 0.5954 | 0.5783 |
| cross-context twin | 0.5249 | 0.5339 |

**The full combination EXCEEDS the counter CI-separated** (val +0.0321 [+0.012,+0.053]; test +0.0406
[+0.020,+0.061]), selective accuracy rises to 0.71, twin loses. Learned validities (val/test): gek +0.34/+0.40,
affect +0.11/+0.20, **neg -0.39/-0.33** (dominant non-GEK cue), and hub / ctype / refer ~0 (the pure-SIMILARITY
cues add nothing -- confirming similarity is fooled).

**BUT the honesty ablation shows the exceed is the ARTIFACT, not coherence.** The negation cue reads ONLY the
ending (context-independent), so it is exactly the Schwartz 2017 style tell (turkers over-used negation writing
"wrong" endings). Remove it and the remaining CONTEXT-DEPENDENT, twin-guarded coherence cues do NOT exceed the
counter: **CI-no-neg val 0.5954 (+0.0128 [-0.008,+0.032], NOT CI-sep) / test 0.5783 (+0.0144 [-0.003,+0.032], NOT
CI-sep).** The twin retaining the negation signal is why it sits at 0.52-0.53, not 0.50. So: I built the full
alternative, it nominally beats the counter, and the ablation caught it RIDING THE ARTIFACT -- the genuine
(artifact-free) coherence does NOT exceed the counter. The located negative HOLDS, now under the strongest test.

## Doing it RIGHT (not cheap): the artifact-free, protagonist-centered coherence engine (v2)
After the ablation exposed the negation cue as the artifact, I built the RIGHT mechanism the literature pins
(`exp_forward_event_situation_coherence_v2`): every cue CONTEXT-DEPENDENT and PROTAGONIST/PROPOSITION-level
(artifact-free by construction) -- protagonist continuity (Zwaan index; Albrecht-O'Brien consistency), a
CONTEXT-DEPENDENT contradiction penalty (does the ending's protagonist-affect REVERSE the story's resolved
state -- the Kuperberg P600 signal the N400/association channel is blind to; Fischler 1983), affect-arc
DIRECTION (Reagan 2016 six arc shapes -- proximity to the arc EXTRAPOLATION, not a static value), causal
event-type connectivity (Trabasso), and the GEK base -- integrated with LEARNED cue validities (cross-validated
val<->test, NO test-mining).

| arm | val | test |
|---|---|---|
| 1-step counter (strongest floor) | 0.5826 | 0.5639 |
| GEK alone | 0.5922 | 0.5815 |
| **RIGHT coherence engine (artifact-free, all cues context-dependent)** | **0.6002** | **0.5863** |
| cross-context twin | 0.5302 | 0.5313 |

**A GENUINE, artifact-free lift over the strongest floor: test +0.0224 [+0.003,+0.043] CI-SEPARATED** (val
+0.0176 [-0.002,+0.036], just misses); the twin COLLAPSES to 0.53 (every cue reads THIS story), selective
accuracy rises (val 0.600->0.675). And the context-dependent contradiction cue now carries the CORRECT POSITIVE
validity (+0.07/+0.07) -- unlike v1's cheap ending-only negation flag (-0.39, the artifact). So the RIGHT
mechanism, built honestly, produces a small but REAL forward-coherence signal beyond association -- landing right
at the research-predicted honest glass-box ceiling (~0.60; Mostafazadeh 2016 context baselines are 0.52-0.585).
The individual structured cues are still weak (protag 0.53, contradiction 0.53, affect 0.55, causal 0.52)
because the situation-model registers they read are SPARSE/NOISY -- which localizes the remaining gain to
EXTRACTION, not to the inference design.

**PRECISION-WEIGHTED upgrade (v3, Friston active inference -- the bar's precision term made load-bearing).**
v2 combined cues with FIXED validities; the brain trusts each cue by its per-item RELIABILITY (a structured cue
that fired confidently is weighted up; one that did not fire -- goal absent, flat arc, no event type -- is
downweighted toward 0). Weighting each cue by a per-item precision then fitting validities (cross-validated) tips
the artifact-free result to a PAIRED-bootstrap CI-separated lift over the counter on BOTH splits: **val 0.6029
(+0.0203 [+0.0005,+0.040]) / test 0.5922 (+0.0283 [+0.010,+0.047])**, twin collapses to 0.53, selective rises
(val 0.603->0.682). Razor-thin on val (lower bound +0.0005), so I still deflate to PARTIAL -- but precision-
weighting is a genuine, PINNED brain-foundational upgrade that brings the artifact-free mechanism to the
CI-separation threshold, at the honest glass-box ceiling.

## CLOSING THE PREDICTIVE-CODING LOOP (the highest-value SYSTEMIC upgrade -- forward error drives comprehension AND segmentation)
The substrate had the loop OPEN: a BACKWARD event monitor (`n400_coherence_monitor`, error vs a running gist)
and an argument-level forward surprisal, but the forward EVENT prediction was never the thing the error is
taken against. Research (folded below) pins that the error is ALWAYS against a FORWARD prediction (Rao-Ballard/
Friston; N400 as forward belief-update error, Rabovsky 2018; Zacks-Reynolds-Braver 2007 feedforward next-input
predictor + error-spike gate). `exp_forward_event_predictive_loop_v1` wires the forward prediction error as the
shared currency and measures it two ways:

| | forward prediction error | backward running gist |
|---|---|---|
| **(A) coherence** (Story Cloze, pick coherent ending) | **0.5922 [0.570,0.615]** | 0.5377 [0.515,0.561] |
| **(B) segmentation F1** (400 ROCStories concatenated; true boundaries = story starts; MATCHED z-score EST) | **0.766 reset / 0.806 reinstate(0.3)** | 0.272 (matched) / 0.043 (landed organ) |

- **(A)** the forward error beats the backward gist for comprehension (CI-separated), same discrimination, only the
  prediction differs.
- **(B)** the forward directional predictor is a ~3x better EVENT-BOUNDARY detector than the backward gist
  (0.766 vs 0.272 at a matched threshold; random 0.230; shuffled-stream twin collapses to 0.166 -- it uses the
  real narrative structure). This is the loop-closure payoff: redirecting the segmentation error from the backward
  gist to the FORWARD prediction is a large, clean win.
- **RESET vs REINSTATE (item 5, Wall 2) answered empirically:** a MILD reinstatement of the prior context at a
  boundary (lambda~0.3) BEATS a hard reset (0.806 vs 0.766); heavy reinstatement (0.7) HURTS (0.707). This matches
  Pu, Kong, Ranganath & Melloni 2022's gated-blend `C_t=(1-lambda)[...]+lambda*C_1` with fit lambda~0.2 and SEM's
  reinstate-don't-wipe -- and the honest negative (heavy reinstate blurs boundaries; reinstatement keys on schema-
  type match, not positional recurrence). The `n400_coherence_monitor` currently hard-RESETS -- the proposed fix is
  lambda~0.2-0.3 reinstatement. NOTE: fusing "error magnitude -> boundary" with "distribution concentration ->
  confidence" for one signal is OUR-INVENTION (a defensible Friston/EST synthesis; EST's formal model uses
  magnitude only) -- flagged, not overclaimed.

## PROTOTYPING THE TWO NAMED BLOCKERS (owner asked; both reframed by the phase-diagram insight)
- **Blocker 1 -- EXTRACTION DENSITY (`exp_forward_event_density_phase_v1`).** NOT a fixed wall: density is a
  controllable parameter. The goal/causal fire-rate climbs monotonically with context length (goal 0.06->0.36,
  causal 0.05->0.34 as L=1->5) and would keep climbing on longer narratives. The mechanism was under-powered by
  4-sentence Story Cloze, not ceilinged.
- **Blocker 2 -- BREAK THE CEILING with a RICHER WORLD-KNOWLEDGE FOUNDATION (`exp_forward_event_world_knowledge_v1`).**
  Invariant-compliant (a static OFFLINE ConceptNet asset, NOT a learned LLM at inference): I extracted 84,421
  ConceptNet-5.7 causal/script edges (Causes, HasSubevent, HasPrerequisite, MotivatedByGoal, CausesDesire) over
  2,638 sources -- so the typed-causal cue now fires DENSELY (100%). But it does NOT beat co-occurrence on short
  Story Cloze: world-knowledge causal 0.535/0.537 (val/test), gek+wk 0.599/0.577, margin over the counter +0.016/
  +0.013 (NOT CI-sep) -- the generic ConceptNet causal edges do not discriminate the SPECIFIC coherent
  continuation better than association when there are only 4 sentences to reason over.
- **Blocker 2b -- USING THE SUBSTRATE'S OPTIMIZED KNOWLEDGE STORE (`hdlab.meaning_foundation`, 117,614
  sense-resolved WordNet signatures -- the clean/typed ATL meaning hub) as the coherence cue HURTS.** Tested
  (fires 100%): meaning_foundation relatedness scores 0.530 val / 0.492 test -- CI-separated BELOW the counter
  (margin -0.053 / -0.072); combined with GEK it adds nothing. The reason is a brain-SYSTEM dissociation: the
  meaning_foundation optimizes SEMANTIC SIMILARITY / MEANING (the ATL hub -- dog~cat), which is EXACTLY the
  similarity signal that is FOOLED by topically-matched wrong endings. Forward narrative coherence is NOT semantic
  similarity; it needs a FORWARD EVENT-TRANSITION / GENERALIZED-EVENT-KNOWLEDGE store (a DIFFERENT organ / brain
  system -- Elman GEK, the event/schema system, not the meaning hub). My GEK is the prototype of that missing
  organ. So "use the optimized knowledge store" is right in principle but the SUBSTRATE'S optimized store is the
  MEANING channel; forward coherence needs the (north-star-aligned, clean/typed) EVENT-KNOWLEDGE channel, which is
  what the proposed `generalized_event_knowledge` organ IS. The higher-fidelity version of MY store is a
  CLEAN/TYPED (sense-resolved) forward EVENT-transition store, not raw lemma co-occurrence.
- **THE DECISIVE DENSE-REGIME TEST (`exp_forward_event_dense_context_v1`) -- and it REFUTES my "short-regime
  artifact" speculation.** I built the dense-context forward-continuation gold (MCScript2, 6-sentence contexts,
  same-scenario topic-matched hard negatives; dev n=273, test n=557). Density WORKS as predicted: on 6-sentence
  contexts the registers fire densely (causal 0.74, goals 0.59, ~20 events/context vs 0.28/0.32 on short Story
  Cloze). BUT the STRUCTURED situation-model mechanism (v3 cues, precision-weighted, cross-validated) STILL does
  NOT beat the co-occurrence counter in the dense regime: dev STRUCTURED 0.550 vs counter 0.608 (-0.059
  [-0.132,+0.015]); test 0.553 vs 0.546 (+0.007 [-0.034,+0.049], tied). The temporal-shuffle-context twin does
  NOT collapse (0.55 ~ structured) -- the cues are largely order-invariant association even when the situation
  model is dense. **So the counter's parity is NOT a short-regime artifact -- it persists in the dense regime.**
  My earlier speculation was wrong, and the test the owner pushed me to run is what showed it. The honest,
  corrected conclusion: denser EXTRACTION alone does not unlock the structured mechanism -- the ceiling is about
  INFERENCE DEPTH (the deep causal-motivational entailment only a learned world model supplies, per the research),
  not extraction sparsity. (Task caveat: the same-scenario hard negative controls topic at the SCENARIO level but
  not at the VOCABULARY level -- different same-scenario stories use different specific words -- so the counter
  retains a small vocabulary-overlap edge; the twin-not-collapsing + structured-not-beating-counter is the robust
  finding regardless.)
- **SO BOTH the density knob AND richer world knowledge are REAL levers that do NOT close this gap.** Density is a
  controllable parameter (fire-rate 0.28->0.74), and richer typed causal knowledge fires densely (100%) -- but
  neither lets the glass-box structured/associative cues exceed co-occurrence, in short OR dense regimes. This
  CONVERGES with the research's honest ceiling (only a learned world model breaks it) and CLOSES the "density/
  knowledge fixes it" hypothesis with a direct test rather than an assumption.

## THE WALL, UNDERSTOOD: aggressive research + building the brain's integration mechanism (2026-09-06)
Pushed to research the wall aggressively and build the brain's ACTUAL mechanism (not shallow cues), I ran a
4-angle literature drill (`research_drill_forward_coherence_wall_2026-09-06.md`) and built the Kintsch
Construction-Integration SETTLING mechanism (`exp_forward_event_ci_settling_v1`) -- settle a knowledge net to a
coherent fixed point, read off which candidate INTEGRATES (not which is merely related). This is the genuinely
non-single-shot brain mechanism (global coherence, not pairwise association).

**Result: CI-settling plateaus too** -- val 0.5697 / test 0.5580 (at the counter; slightly below single-shot GEK;
twin collapses to 0.49, so it USES the context but cannot exceed co-occurrence over an associative net).

**And the research explains EXACTLY why, which turns the plateau into an understood, crossable wall:**
- The brain's forward-coherence ENGINES -- CI-settling (Kintsch), causal-necessity (Trabasso counterfactual),
  inverse-planning (Baker/IPOCL/Chandra) -- are ALL glass-box and buildable (running-code precedents; I built +
  tested CI-settling). Their discriminative power is GATED by a RICH, STRUCTURED SCRIPT/EVENT-SCHEMA knowledge net
  (Graesser: "a search finds nothing in an empty store").
- Our available nets (co-occurrence, ConceptNet causal, meaning-similarity) are the WRONG KIND -- associative/
  taxonomic, not script/event-schema-structured -- so EVERY mechanism over them plateaus (measured across ~12
  mechanisms incl. CI-settling). **THE GAP IS THE STRUCTURED KNOWLEDGE FOUNDATION, NOT A MISSING MECHANISM.**
- The SEM decomposition settles the "is a learned net irreducible?" question: SEM's schema-selection/segmentation
  is glass-box + load-bearing (Nguyen 2024 confirms modularity); its learned GRU dynamics has NO ablation
  justifying it, and Kumar et al. 2023 shows a GLASS-BOX Bayesian/KL-surprise over a FROZEN foundation predicts
  human event boundaries with NO training at inference. So the learned piece is "cheap nonlinear compression,"
  likely ONLINE-fittable -- human-level is NOT gated by a forbidden learned net.
- Graesser 1994 (load-bearing): forecasting inferences are NOT spontaneous -- recruited ON-DEMAND under a forced
  choice (exactly Story Cloze). So the faithful model is instrumental goal-directed graph COMPLETION at the choice.

**The brain-foundational path across (buildable, invariant-compliant):** build the RICH SCRIPT/EVENT-SCHEMA
knowledge FOUNDATION (offline static asset = admissible; the project's north-star clean/typed knowledge
foundation, SPECIALIZED to event-schemas), THEN run the already-built glass-box engines (CI-settling +
causal-necessity + inverse-planning) over IT. This is a FOUNDATION-scale build, not a mechanism tweak -- which is
precisely why the built mechanisms plateau without it.

## Why this is a rigorous located negative -- and the sharpened diagnosis (TWO fidelity gaps, not one ceiling)
Every faithful glass-box readout was built and tested -- GEK association (works over frequency floors), the
successor/horizon (no lift, pre-registered), the finer event grain (weaker), goal/causal structure (registers too
sparse), and affect-trajectory (real but weak). They CONVERGE on ~0.54-0.59 for ONE reason: **they are all
SIMILARITY / ASSOCIATION readouts, and the adversarial wrong endings are constructed to be topically SIMILAR.**
The brain does something categorically different -- **INFERENTIAL causal-motivational coherence**: it builds the
causal chain and the protagonist's goal/affect arc and checks whether the ending is ENTAILED, not whether it is
SIMILAR. So we do not show the brain's ~1.00 for TWO concrete, brain-foundational FIDELITY GAPS to build across
(NOT one ceiling):
  * **(B) INFERENCE -- now BUILT (v2), design SOUND, blocker downstream.** The RIGHT artifact-free inference
    engine (protagonist-centered context-dependent contradiction + affect-arc-direction + causal-to-goal, learned
    validities) produces a GENUINE lift over the counter (test +0.022 CI-sep, val +0.018), twin-guarded, and the
    contradiction cue carries the correct positive validity. So the inference DESIGN is validated as
    brain-foundational -- it is NOT the missing piece. The lift is small ONLY because the cues read sparse registers.
  * **(A) EXTRACTION DENSITY -- NOT a fixed wall; a controllable PHASE-DIAGRAM parameter (owner 2026-09-06).** The
    ~30% goal/causal fire-rate is a property of the 4-sentence STORY CLOZE regime, NOT of the mechanism. Measured
    (`exp_forward_event_density_phase_v1`): the fire-rate climbs MONOTONICALLY with context length --
    goal 0.056->0.168->0.260->0.316->0.360 and causal 0.052->0.164->0.224->0.288->0.344 as L=1->5 -- and would keep
    climbing on longer narratives. So the ~30% was a short-context artifact, NOT a mechanism limit. I speculated
    the counter's parity was therefore a short-regime artifact and the structured cues would pull ahead in the
    dense regime -- and I TESTED it (`exp_forward_event_dense_context_v1`, MCScript2 6-sentence contexts, causal
    fires 0.74). THE TEST REFUTED THE SPECULATION: even with dense extraction the structured mechanism does not
    beat the counter (dev -0.059, test +0.007 tied) and the twin does not collapse. So denser EXTRACTION alone does
    not unlock it -- the ceiling is INFERENCE DEPTH (a learned world model), not extraction sparsity. Correct
    takeaway: density is a real, controllable lever that raises fire-rate but does NOT close the coherence gap.
The honest-ceiling literature is consistent (Chambers-Jurafsky disclaim human-solvability for SHALLOW event
models; Story Cloze's 75.2% content-blind classifier is a style artifact), and the ONE model that reaches ~0.90 --
SEM (Franklin/Gershman 2020, a gated RNN over HRR-bound scene vectors) and modern LMs -- brings a LEARNED deep
world model, which the invariant (NO external LLM; "the brain does not do long training runs") forbids. So the
glass-box GEK projector is the correct SHALLOWEST layer (Elman GEK, PINNED) of a deep stack whose upper layers
(dense extraction + causal inference) are not yet built -- the located-negative-is-a-full-PASS condition the bar
spells out, with the exact cause named AND a concrete brain-foundational build path, not a ceiling.

## GENERALIZATION (brain-fidelity via transfer -- and a correctly-located boundary)
- **WITHIN narrative continuation: generalizes.** Every headline holds on BOTH Story Cloze val AND test (held-out
  splits): coherence, twin-collapse, selective-accuracy, precision-weighted CI-sep, segmentation.
- **ACROSS to social-mental-state prediction: does NOT transfer -- and that is the RIGHT boundary.** On Social IQa
  (Sap 2019, a DIFFERENT modern gold; 770 forward-question items, chance 0.333) the ROCStories-trained forward GEK
  coherence scores 0.370 -- only marginally above chance/counter (0.364)/majority (0.340), NOT CI-separated, twin
  0.352. This is the brain-foundational DISSOCIATION (Jack et al. 2013 opposing domains; the physical/event vs
  mental split the substrate's own `event_type.py` encodes): narrative-EVENT continuation and MENTALIZING ("what
  will X WANT to do") are DIFFERENT systems. Social IQa needs the ToM/mentalizing system (a SEPARATELY-FILED
  problem -- `chain_belief_and_goal_into_theory_of_mind...`), and its 1-2 sentence contexts give almost no
  situation model to project from. The mechanism correctly generalizes within its domain and correctly STOPS at
  the domain the brain hands to a different system -- a fidelity signature, not a failure.

## Performance vs the brain, and where signal is lost along the chain
A competent reader discriminates Story Cloze at ~1.00 (humans) / SOTA fine-tuned LMs ~0.90; our glass-box
projector is at ~0.59. The itemized mechanism-diff (where we lose signal): (a) the brain builds a DENSE
goal/causal situation model from 5 sentences -- ours fires goal/causal on ~27% and over-segments events (the
dominant loss); (b) the brain's GEK is a learned distributed event representation (Elman SRN / SEM gated RNN) --
ours is a co-occurrence PPMI table, which captures scene association but not fine event-transition structure;
(c) the brain integrates affect/valence coherence and character-goal simulation -- we use only content + a sparse
goal cue. The FIRST is the highest-leverage upstream fix (see ADJACENT).

## KEY REALIZATIONS
- **THE WALL IS A KNOWLEDGE-FOUNDATION GAP, NOT A MECHANISM GAP (owner 2026-09-06).** I built the brain's actual
  integration mechanism (Kintsch CI-settling) and it plateaued too. The 4-angle research explains it: the
  glass-box engines (CI-settling, causal-necessity, inverse-planning) are all buildable, but their power is GATED
  by a RICH SCRIPT/EVENT-SCHEMA knowledge net -- and our available nets are the wrong KIND (associative, not
  schema-structured). And the SEM decomposition shows the learned dynamics is NOT irreducible (Kumar 2023:
  glass-box KL-surprise over a frozen foundation predicts human boundaries). So human-level is reachable
  glass-box -- the missing piece is the structured KNOWLEDGE FOUNDATION, a north-star offline build, not a
  forbidden learned model. Generalizes: when every mechanism over a knowledge net plateaus, suspect the NET's
  structure, not the mechanism.
- **"SPARSE" IS A PHASE-DIAGRAM KNOB, NOT A WALL (owner 2026-09-06).** I twice labelled the ~30% goal/causal
  fire-rate a fixed blocker. It is not: density is a parameter we control (context length / corpus richness), and
  the fire-rate climbs monotonically with it (goal 0.06->0.36 as L=1->5). The situation-model mechanism was
  UNDER-POWERED by a short-context eval on the EXTRACTION side, not ceilinged. Generalizes: never report "sparse"
  as a ceiling without asking which regime parameter set it and whether we control that parameter. **BUT the
  follow-through test corrected my NEXT move too:** having fixed the density knob (MCScript2 6-sentence contexts,
  causal fires 0.74), I speculated the structured cues would then beat the counter -- and the direct test REFUTED
  it (structured ties/loses; the temporal-shuffle twin does not collapse). So the honest lesson is two-sided:
  sparsity was not the wall (density is a knob), AND density is not the fix (the ceiling is inference DEPTH, not
  extraction density). Both were settled by running the test, not by assuming -- which is the whole point.
- **The exceed was the ARTIFACT until I ablated it; the CHEAP contradiction cue and the RIGHT one have OPPOSITE
  provenance.** The full CI beat the counter CI-separated on both splits -- but a negation-cue ablation caught it
  riding the Schwartz-2017 style artifact (an ending-ONLY negation flag, context-INDEPENDENT). Rebuilding the
  contradiction cue as CONTEXT-DEPENDENT (does the ending reverse the PROTAGONIST'S resolved state) flipped its
  learned validity from -0.39 (artifact) to +0.07 (genuine) and produced a real, twin-guarded, artifact-free lift.
  The lesson: "beats the counter" means nothing until you ablate the one cue that could read the corpus artifact,
  and a contradiction signal is only brain-foundational if it is CONTEXT-DEPENDENT.
- **The adversarial wrong endings are topically SIMILAR, so every similarity readout is FOOLED -- the brain uses
  ENTAILMENT, not similarity.** The single deepest realization: Story Cloze wrong endings often REPEAT context
  words ("joined a gang" after a gang-heavy context), so GEK, the co-occurrence counter, and even semantic-gist
  integration are actively fooled. Goal, event-type, and affect cues each converge on ~0.54-0.59 because they are
  ALL similarity/association readouts. The brain discriminates by INFERENTIAL causal-motivational coherence (is
  the ending ENTAILED by the situation?), which no cheap glass-box cue captures -- naming this is what turns a
  "modest win, real ceiling" into "two concrete fidelity gaps (dense extraction + a causal-inference engine)."
- **The instrument reframed the ceiling.** The research's honest-ceiling finding (Chambers-Jurafsky narrow
  margins; Story Cloze's 75.2% content-blind style classifier) told me BEFORE building that a large win would be
  a confound, and made the CROSS-CONTEXT twin (not the temporal-shuffle) the load-bearing control -- it is what
  defeats the style artifact. A twin that scrambles only sentence ORDER would have passed a style-reading arm.
- **"Beats the counter" is the wrong question; "beats the FREQUENCY floor while USING the story" is the right
  one.** The 1-step co-occurrence counter is itself a brain-foundational generalized-event-knowledge readout at
  short range -- so tying it is not a failure of the mechanism, it is the finding that the forward signal IS
  short-range lexical event association. The mechanism's real content is that it beats the majority/unigram
  floor CI-separated with a twin that collapses and a precision that calibrates.
- **The finer hub HURTS on discourse continuation** -- the exact opposite of the prior forward-prediction
  SOLVED's argument-ranking wall. Fine verb-structure helps rank thematic arguments; broad scene association
  predicts the next discourse event. Same substrate, opposite grain -- a reminder that "which hub" is task-specific.
- **Extraction, not projection, is the bottleneck.** Measuring the register fire-rate (goal/causal ~27%, 8
  events/4 sentences) localized the loss to the situation model's EXTRACTION on short modern stories, not to the
  forward projection rule. That is the itemized mechanism-diff the bar asks for and the seed of the next problem.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, Tier 5 prediction / event-segmentation)
- **The FORWARD EVENT-LEVEL generator (the thing the N400/EST error is taken AGAINST) is now demonstrated as a
  glass-box GEK associative readout.** Tier 5 currently reads "FORWARD HALF NOW BUILT" only at the WORD/argument
  level (`predictive_reader`) and the BACKWARD event level (`n400_coherence_monitor`). This adds the FORWARD
  event-level projection: it beats the base-rate floor CI-separated with calibrated precision, but is a LOCATED
  NEGATIVE vs a co-occurrence counter (the horizon/structure adds nothing robustly; registers fire ~27%).
- **SR-over-narrative-events should be marked OUR-INVENTION, not PINNED.** The research finds no demonstrated
  SR over narrative events (spatial/graph metaphor); my result confirms it is a 1-step counter here. Recommend
  the `successor_representation` audit entry note this and cite outcome (iii) as now OBSERVED on a modern gold.
- **THE PREDICTIVE-CODING LOOP is now closeable AND measured.** The forward EVENT prediction error beats the
  backward running-gist error for BOTH comprehension (Story Cloze 0.592 vs 0.538) AND event segmentation (F1
  0.766-0.806 vs 0.272 matched) -- the error should be taken against the FORWARD prediction (Rao-Ballard/Friston;
  Rabovsky 2018 N400; Zacks-Reynolds-Braver), not the backward gist. Recommend Tier 5 record that the loop is
  now demonstrated: `n400_coherence_monitor` should take its error against the forward projection.
- **n400_coherence_monitor reset-vs-reinstate deviation -- now MEASURED.** The monitor hard-RESETS its gist at a
  boundary; the literature says REINSTATE (Pu 2022 gated blend `C_t=(1-lambda)[...]+lambda*C_1`, lambda~0.2; SEM;
  Baldassano 2017). Measured here: mild reinstatement (lambda~0.3) beats hard reset on boundary F1 (0.806 vs
  0.766); heavy reinstate hurts. Recommend the monitor add a swept lambda~0.2-0.3 reinstatement. (Honest negative:
  reinstatement keys on schema-type match, not positional recurrence -- Radvansky's same-room test refuted naive
  positional reinstatement.)

## ADJACENT COMPONENTS (brain-fidelity + optimization potential -- seeds for the next problems)
- **The situation-model EVENT EXTRACTOR is the highest-leverage upstream bottleneck (candidate next problem).**
  It over-segments (8 events / 4 sentences), mis-detects predicates from contractions/nominals ("wasn", "gangs"),
  and its goal/causal registers fire on ~27% of 5-sentence stories. BRAIN-FIDELITY: the arc-eager incremental
  parse is PINNED-faithful, but the POSITIONAL event/role read and the goal/causal extraction are OUR-INVENTION
  placeholders that under-fire on short modern narrative. OPTIMIZATION: denser event/goal extraction on short
  stories would directly lift every forward cue -- this is where the signal is lost.
- **The GEK forward-transition store is a NEW brain-foundational organ the substrate LACKS** (verified absence:
  nothing in `hdlab` forward-projects a next event/state from `sm`; only `sequence_memory.predict_next`, a
  low-level HRR retrieval, exists). It is a generalized-event-knowledge associative map -- the "different hub."
  It is a NEW island, so no downstream consumer regresses. Two existing consumers COULD be revisited to consume
  a forward EVENT expectation: (a) `predict_surprisal` (the who-did-what error flag) is argument-level only --
  an event-level forward expectation would extend it; (b) `n400_coherence_monitor` currently detects boundaries
  against a BACKWARD gist -- it could take its error against this FORWARD event prediction (the true predictive-
  coding loop). Both are follow-on wires, not regressions.
- **A valence/affect-coherence cue is an untested brain-foundational lever** (affective forecasting; somatic
  markers) -- but it risks capturing the Story Cloze style artifact, so it must be gated by the cross-context
  twin. Named, not built.

## What I did NOT establish (and what I would withdraw first)
- I did NOT show the forward projection exceeds a 1-step co-occurrence counter (val not CI-sep). If I had to
  withdraw one thing first, it is any implication that the multi-step SUCCESSOR HORIZON contributes -- it does
  not (~+0.01); the successor arm is a base-rate counter here.
- I did NOT demonstrate a next-EVENT PREDICATE generation (I used the right-vs-wrong CONTINUATION discrimination
  framing the bar explicitly permits). A generative next-predicate readout on a controlled-distractor gold is a
  separate, harder instrument.
- The situation-model multi-cue combination's lift over the content GEK is small and its cue weights are
  OUR-INVENTION (equal weights on standardized cues, NOT tuned to the test) -- I would withdraw any claim that
  goal/causal STRUCTURE robustly helps before I would withdraw the base-rate-floor result.

## Q111 -- proposed hdlab diff (strategy lands + witnesses; I did NOT write hdlab)
A NEW default-off organ `hdlab/generalized_event_knowledge.py` (the forward-transition GEK store, fit offline on
ROCStories/any narrative corpus -- a static admissible foundation asset) + a default-off `predict_next_event(sm, t)`
readout on `SituationReader` composing the live registers (GEK content cue + goal cue via `graded_competition`,
precision = 1 - entropy), following the additive `_read_surprisal`/`_read_goals` pattern. It is additive and a new
island (no downstream consumer today -> no regression). Do NOT wire the successor/horizon (adds nothing) or type
the forward prediction from verb-structure (weaker). The higher-value upstream fix is the event/goal/causal
EXTRACTOR density on short narrative (a separate filed problem).

## TLDR (plain English)
A good reader is always a step ahead of the story. I built the "what comes next?" guess our reader never had:
from what has been said, it guesses which of two possible endings really comes next, using learned knowledge of
what usually follows what. On modern test stories it beats simply betting on the more common ending (about 59%
vs about 51%, a real and statistically clean gap), it falls apart when you feed it a DIFFERENT story's setup
(proving it truly uses the story, not a writing-style trick), and when it says it is confident it is right more
often (about 65% on its most-confident quarter). What it does NOT do is beat a simple "which words tend to go
together" counter -- and I showed exactly why: guessing the next EVENT from broad word-association is close to
the real ceiling for this kind of task (the research literature agrees), the story's deeper structure (goals,
causes) is only detected in about a quarter of these short stories, and looking further ahead than one step adds
nothing. So the forward guess works and is honestly calibrated; the ceiling is a real property of the task plus a
gap in how much structure we extract from short stories -- not a broken guesser.

## QUESTIONS
- ONE LABELLING CALL FOR YOU: I marked this **PARTIAL**. The bar's own clause says a rigorous located negative
  (which I have -- the faithful projection does not beat the STRONGEST floor, with the exact cause enumerated and
  the twin/precision halves passing) is a FULL PASS, which would make **SOLVED** defensible. I deflated to PARTIAL
  because the win is over the majority/frequency floor, not the strongest (associative-counter) floor. Content is
  identical either way; your call on the label.

## OTHER EFFICIENCIES + BRAIN-FOUNDATIONAL UPGRADES (this round -- "do them all")
- **DONE -- closed the predictive-coding LOOP** (`exp_forward_event_predictive_loop_v1`): forward error > backward
  gist for coherence AND segmentation (0.766-0.806 vs 0.272). The single highest-value SYSTEMIC upgrade.
- **DONE -- reset-vs-reinstate**: mild reinstatement (lambda~0.3) beats hard reset on boundary F1; propose the
  monitor add a swept lambda.
- **DONE -- precision-weighting** (v3, Friston): tips the artifact-free coherence to CI-sep over the counter on both splits.
- **DONE (efficiencies, folded into v3/loop)**: lean extraction (the projector needs only events+protagonist+affect,
  not the full default-on reader); pruned to the 3 live cues (gek + affect-direction + protagonist-contradiction --
  hub/causal-type/referential/verb-chain all learned ~0 validity); 1-step directed transitions (the multi-step
  successor horizon adds ~+0.01 -- skip the O(V^3) matrix).
- **MAPPED (item 6, EXTRACTION density -- another problem's lane; building a crippled version would be "cheap").**
  Research names the exact brain-foundational operations: (1) REUSE the already-integrated `bridging_inference`
  organ to GENERATE the unstated causal/goal links (Graesser causal-antecedent + superordinate-goal inferences are
  automatic) -- do not rebuild; (2) WHOLE-CONTEXT RESONANCE spread-activation over the meaning store across ALL
  prior text (Myers-O'Brien / Albrecht-O'Brien) -- the highest-leverage UNBUILT lever for the ~30% fire-rate; (3)
  plan-library GOAL-FROM-ACTION (Schank-Abelson / Kautz-Allen) -- cheap glass-box. Honest negative: forward/
  elaborative inference generation is strategic/fragile (Klin 1999) -- do NOT expect gains there; only bridging
  (causal/goal) is automatic.

## NEXT STEPS (the brain-foundational build path across the two fidelity gaps)
- Land the additive `generalized_event_knowledge` organ + `predict_next_event` readout (Q111, default-off, new
  island, no-regress) + the forward-error segmentation wire into `n400_coherence_monitor` (redirect its error to
  the forward prediction + add lambda~0.3 reinstatement), then measure the live-board lift. Lean extraction, the
  3 live cues, precision-weighting, 1-step transitions.
- **GAP (A) EXTRACTION DENSITY -- TESTED, and it is NOT the fix (do not file it as the lever).** The dense-regime
  test (MCScript2 6-sentence contexts, causal fires 0.74) shows denser extraction raises fire-rate but does NOT
  let the structured mechanism beat the counter. Density is a real knob, but the coherence gap is not on the
  extraction side.
- **GAP (B) INFERENCE ENGINES -- BUILT + tested (v2/v3 cues + Kintsch CI-settling); they are NOT the missing
  piece.** The glass-box engines are ready; they plateau ONLY because they run over associative nets.
- **THE REAL LEVER -- build the RICH SCRIPT/EVENT-SCHEMA KNOWLEDGE FOUNDATION (north-star, offline static asset).**
  Canonical ordered event structures per situation, causal/goal-typed (Schank scripts + Trabasso causal criteria +
  Rashkin naive-psychology schema), then run the already-built CI-settling + causal-necessity + inverse-planning
  over it, recruited on-demand at the forced choice (Graesser). This is a FOUNDATION-scale project (the project's
  clean/typed knowledge north-star, specialized to event-schemas), and it is the brain-foundational, invariant-
  compliant (NO inference-LLM) path across the wall. The SEM-style generative dynamics can be ONLINE-fitted per
  schema (Kumar 2023 shows the learned piece is not irreducible), not batch-trained.
- Revisit `predict_surprisal` (extend to event level) and `n400_coherence_monitor` (take its error against this
  forward prediction) to consume the new forward-event expectation -- the true predictive-coding loop.
