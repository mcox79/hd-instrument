# Brain-foundational analysis: multi-step means-ends chaining for the generative world-model

**problem:** chain_multi_step_plans_and_scripts_for_the_generative_world_model | **date:** 2026-09-08 |
**gold:** TellMeWhy non-adjacent (Lal 2021), n=256 | **witness:** verification/test_multistep_meansend_chain.py 12/12

Detailed backing for SOLVED.md checklist items 6 (performance vs the brain / where we lose signal) and 7
(adjacent components). Every number is on disk (data/exp_multistep_meansend_chain_v1/metrics.json).

## 1. How the brain does this (PINNED vs OUR-INVENTION)
Reading "why did she go to the store?" with "she wanted milk" earlier, a competent reader:
1. Maintains a SITUATION MODEL (Zwaan-Radvansky; Kintsch C-I) with COREF-RESOLVED participants and their goals.
2. Runs MULTIPLE intuitive-theory engines IN PARALLEL as generative PRIORS over one shared event model
   (Franklin 2020 SEM; Kuperberg 2021; Rabovsky 2018): psychology (goals/beliefs, Baker-Saxe-Tenenbaum;
   Csibra-Gergely), physics (force dynamics, Talmy/Wolff), affect (appraisal, OCC; Barrett).
3. Does INVERSE PLANNING: a FORWARD ROLLOUT (hippocampal, Pfeiffer-Foster; Mattar-Daw) through plan/script
   knowledge to a goal-state test.
4. The plan/script knowledge is the amodal ATL SEMANTIC HUB (Lambon-Ralph): a LOW-DIMENSIONAL distributed code
   where means-end relations are GEOMETRIC PROXIMITY (generate, not retrieve).
5. The engines COMPETE by explanatory coherence (Thagard ECHO): a COALITION beats a lone strong cue.
6. All inside a RECURRENT top-down loop (Rao-Ballard; Friston; Kuperberg-Jaeger).

## 2. Fidelity verdict per stage
| stage | brain (PINNED) | ours | fidelity |
|---|---|---|---|
| extraction | incremental predictive parse | spaCy arc-eager (greedy) | deviation; NOT the loss here (recall 0.98) |
| coref / binding | resolved discourse referents (Heim/Kamp) | SURFACE lemmas, no live coref | deviation (E3 NEEDS_ADAPTER) -- MEASURED as the dominant full-pop loss |
| plan/script knowledge | ATL amodal low-rank hub | PPMI+SVD over ATOMIC (offline) | FAITHFUL IN KIND; online-learning is the deviation |
| rollout | hippocampal model-based rollout | hub implicit closure; explicit chain hurts | faithful for 2-endpoint reachability |
| goal-state test | inverse planning (Baker-Saxe-Tenenbaum) | diagnosticity = P(a|g)/P(a) | FAITHFUL |
| decision | additive + signed-pairwise coherence + DDM | additive only | partial; coherence/commit unbuilt |
| architecture | ONE recurrent generative loop | feed-forward late-fused scorers | deviation (parent-flagged) |
| engines | goal + physics + mental + affect competing | goal excellent; affect weak; physics/mental unbuilt | 1 of 4 |

## 3. Performance vs the brain, and WHERE we lose signal (oracle ladder, parent, n=256)
```
base 0.277
  +0.016  parent surface means-end        -> 0.293
  +0.148  PERFECT goal simulator (DEPTH)   -> 0.441   <- COVERAGE HALF NOW CLOSED (8.7->88%, win doubled)
  +0.332  PERFECT all-type means-end       -> 0.773   <- the OTHER engines; bounded by the 39% associative slice
  +0.227  gold (extraction/selection)      -> 1.000
```
This work moves the first rung (the goal-engine coverage). The residual within the goal engine is (a) the hub's
edge-correctness (held-out AUC 0.68) and (b) -- dominant on the full population -- the missing COREF (section 8).

## 4. Why the full population ties -- cause-type composition (n=256)
| type | n | share | addressable by |
|---|---|---|---|
| OTHER (untypeable/associative) | 101 | 39% | base topical/Trabasso connectivity -- NO directed engine |
| GOAL | 92 | 36% | the goal engine (now excellent) |
| PHYSICAL | 29 | 11% | a physics engine (unbuilt) |
| MENTAL | 20 | 8% | a mental/ToM engine (unbuilt) |
| AFFECTIVE | 14 | 5% | the affect engine (built, weak) |
The goal engine false-fires on the non-goal 64% (69.5% carry a goal-marked distractor); even a perfect
multi-engine means-end caps at 0.773 because 39% of causes are associative (base is the ceiling there).

## 5. Adjacent components (candidate next problems -- fidelity + optimization)
- RESOLVED COREF (E3) -- the dominant, MEASURED upstream (section 8). Being updated by the strategy session now.
- The MULTI-ENGINE COMPETITION: physics (force_dynamics_typer + world_state_register directed) + mental
  (_tom_chain inverse) as competing cues; the signed-pairwise ECHO coherence decision + DDM commit (NEW organ).
- The ATL hub edge-correctness (AUC 0.68): sweep SVD dim / relations / WordNet backoff (movable operating point).
- The recurrent generative loop over a shared event model (bound_event_backbone + predictive_reader/n400).

## 6. Controls (summary; full in SOLVED.md)
info-free twin (GOAL loses p=0, FULL not beaten); base ablation; topical floor; parent-rollout (rs) reproduced;
binary-CSKG (ms2) reproduced; OTHER-subset ablation (cross-type damage); teleological router (does not separate);
affect engine (domain too small); multiplicative gate (still damages OTHER); no-regress; from-source
generalization (AUC 0.68 + direction-faithful 6/6); the temporal/script order store (located negative);
the participant-binding UPSTREAM TRACE (section 8).

## 7. The temporal/script order store (strategy's asset), tested
Strategy flagged a landed broadened order store (hdlab.temporal_script_schema, 454k pairs, coverage 0.84 here)
that lifts TRACIE implicit-event ORDERING +0.036. Tested here as a directed cross-type engine (a cause
canonically precedes its effect: torder = 2*(p_before(cand,q)-0.5)). VERDICT: a LOCATED NEGATIVE for cause-
SELECTION -- torder alone full -0.0508 (not sep), and the goal+affect+temporal competition WORSENS OTHER (-0.122
vs goal-alone -0.079). WHY: the context-free SCRIPT PRIOR discriminates canonical ORDER, not which preceding
event is the CAUSE; among candidates that all precede q, order does not separate the cause. This is strategy's
own scope caveat, confirmed. The store is right for its HOME task (implicit-event ordering); not a cause-selection
engine. A high-coverage directed cross-type signal that still does not cross -- because cause comprehension needs
story-specific content, not a canonical prior.

## 8. THE UPSTREAM TRACE -- the full-population residual localized to resolved COREF (the owner's principle, measured)
Owner's principle: a brain-foundational component that fails almost always relies on a non-brain-foundational
upstream. The goal means-end engine IS brain-foundational (ATL hub + inverse-planning diagnosticity), so I traced
the signals it expects back up the chain and MEASURED where they are lost.

The goal engine expects, per candidate: (a) the candidate's GOAL-OBJECT (goal_register / _goal_span), (b) q's
ACTION terms (event extraction, 0.98), (c) the goal to be bound to q's AGENT (the brain binds "who wanted X" to
"who did Y", Heim/Kamp file-cards), (d) hub means-end scores. (c) is the deviation: we have NO live coref
(E3 NEEDS_ADAPTER); the engine uses SURFACE terms and cannot check agent identity.

TEST (a crude surface agent proxy = first pronoun/proper-noun subject, used ONLY to attribute the loss):
- Agent-gating the goal means-end (suppress a candidate whose known surface agent differs from q's) RECOVERS
  ~61% of the OTHER damage: me_diag OTHER -0.0793 -> -0.0305 (CI now includes 0).
- 67% of the goal engine's non-goal false-flips (base right -> me_diag wrong) are DIFFERENT-agent goals (10/15);
  NONE were valid-but-secondary causes (boosted-in-helpful = 0) -> the damage is NOT gold-incompleteness or an
  intrinsic means-end flaw; it is the engine boosting a DIFFERENT participant's goal.
- 97% of non-goal stories are multi-agent -> coref genuinely CAN disambiguate.
- BUT the surface proxy HALVES the goal-subset win (+0.174 -> +0.098) because it cannot resolve she==Mary (a
  pronoun in q vs a proper name in the goal sentence) -> the fix needs RESOLVED coref, not surface matching.

## 9. THE COMPLETING TEST -- resolved coref, MEASURED, and WHY it only partially recovers (deep decomposition)
I did not stop at the surface proxy. I built a RECENCY-CENTERING resolver (a pronoun binds to the most-recent
name -- the PINNED Centering cue) and re-bound the goal means-end on RESOLVED participants. MEASURED (n=256):
- recency coref KEEPS the goal-subset win CI-separated (+0.152 vs the surface proxy's halved +0.098) -- it
  correctly keeps she==Mary when they are the same protagonist.
- it PARTIALLY recovers OTHER (-0.061 from -0.079) but the FULL population STILL TIES (+0.0156, twin not beaten).

DECOMPOSITION of the 15 OTHER-subset flips (goal boost turned a correct base pick wrong), the deep WHY:
- A = SAME-REFERENT OVER-FIRE: 5/15 (33%). The boosted wrong goal belongs to the SAME participant as q; the goal
  engine fires on a non-causal goal the agent genuinely has. COREF CANNOT FIX THIS.
- B = DIFFERENT-AGENT, recency keeps distinct: 2/15 (13%). Recency coref suppresses these.
- C = RECENCY-MERGED a different surface agent: 8/15 (53%). Different agents (she/he/different names) that recency
  WRONGLY merges, so recency binding fails. A GENDER/NUMBER-AWARE coref would separate + suppress these.
- boosted-in-helpful = 0 -> none were valid-but-unmarked gold causes (NOT gold-incompleteness; genuinely wrong).

So the OTHER damage is 67% COREF-ADDRESSABLE (B+C = 10/15) and 33% INTRINSIC over-fire (A). This maps exactly to
the numbers: recency recovers only B (2) -> OTHER -0.061; the surface-gate recovers B+C (10) -> OTHER -0.031 but
wrongly hits same-referent goal-causes on GOAL (halving +0.174 -> +0.098). The two proxies bracket the tradeoff.

CONCLUSION -- the exact signal-loss points, quantified: (i) MISSING GENDER/NUMBER-AWARE COREF (E3) for the 67%
(recency is insufficient -- the 53% C slice is exactly what recency cannot separate); (ii) the goal engine's own
PROMISCUITY for the 33% (A), which no coref touches and which needs the MULTI-ENGINE COMPETITION (the correct
engine for the actual non-goal cause out-competing the goal boost on the same agent). CORRECTED crossing estimate:
gender/number-aware coref lifts FULL to ~0.33 (borderline; the A residual caps it); the full crossing needs coref
AND the competition. The strategy session is CURRENTLY building coref -- the clean next test is to re-bind on the
reader's GENDER/NUMBER-aware resolved participants and re-measure, then add the competing engines for the A residual.

## 10. CORRECTION (reading the actual items SUPERSEDES the surface decomposition of sections 8-9)
I plugged in the LANDED gender/number-aware resolver (WorkingOverlay phi-agreement + Centering salience + name-gender
gazetteer): plumbing SOUND (subject-found 97%, pronoun-resolution 95%, gazetteer 62%) but it did NOT beat recency
(OTHER -0.085 vs -0.061; GOAL +0.130 vs +0.152; FULL ties). That tell prompted DUMPING AND READING all 15 flips
(metrics.json flip_items), which CORRECTS sections 8-9:
- The "different surface agents" (q="he", boosted="Ike") are the SAME PERSON; recency merges them correctly. So the
  "C recency-merged / needs gender-aware coref" slice is NOT a coref error, and gender-aware coref does not fix it --
  exactly why the landed resolver did not help. COREF IS NOT THE LEVER on this gold; the surface-agent decomposition
  misattributed the damage.
- The true non-goal signal loss, from reading: (1) GOLD-INCOMPLETENESS ~4/15 -- the engine finds a VALID goal-cause
  the sparse TellMeWhy gold did not annotate ("Ike loved to fish"; "Brian wanted to play golf"; "Derek wanted to
  cook") -> scored wrong, arguably right, so the full-pop tie UNDERSTATES true quality; (2) SHALLOW LEXICAL-OVERLAP
  OVER-FIRE ~4/15 -- the hub fires on a shared WORD without verified causal DIRECTION ("give up on a TREE" <- "buy a
  christmas TREE") = a hub precision problem; (3) DEGENERATE items ~2/15 (non-causal q; base picking an effect).
- CORRECTED LEVERS: (a) a directional CAUSE->EFFECT gate on the hub; (b) a COMPLETE / multi-reference eval;
  (c) the multi-engine competition for the 36%-scope. NOT coref (demoted for this gold).
- LESSON: reading the items beat the aggregate decomposition -- an audit checks the shape you thought to check;
  reading the data checks all of them. Sections 8-9 (the surface/recency decomposition) are retained for the trail
  but are SUPERSEDED by this item-level reading.
