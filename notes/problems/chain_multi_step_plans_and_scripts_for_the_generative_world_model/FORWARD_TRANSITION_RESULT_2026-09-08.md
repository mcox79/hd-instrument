# Forward event-transition model -- the missing organ, BUILT to the pinned brain-foundational spec, tested

**problem:** chain_multi_step_plans_and_scripts_for_the_generative_world_model | **date:** 2026-09-08
**cell:** experiments/exp_multistep_forward_transition_v1.py | **gold:** TellMeWhy non-adjacent (Lal 2021), n=256
**research backing:** notes/research_forward_event_transition_n400_causal_2026-09-08.md (SEM/TEM/Rabovsky pins)

## WHY THIS WORK (the owner directive)
Owner: "make sure the ENTIRE CHAIN is brain foundational; FULLY understand what that means; research where you don't
know." The per-component audit (BRAIN_FOUNDATIONAL_ANALYSIS sec.12) found only 3/9 components 100% brain-foundational;
the missing load-bearing organ is I2's FORWARD half -- a FORWARD EVENT-TRANSITION model so the N400 is a genuine
forward prediction-ERROR (n400_coherence_monitor is backward-only, forward_expect_fn=None). The backward-only N400 was
prototype-confirmed ANTI-selective (predint -0.1445). This cell BUILDS the forward organ and tests the load-bearing
bet: is a DIRECTIONAL forward-prediction signal SELECTIVE for the causal edge where every SYMMETRIC proxy was
promiscuous (object-sharing != causation)?

## WHAT I BUILT (to the research-pinned spec -- copy the computation, sweep the realization)
The cause of q is the antecedent C from which q is generatively PREDICTABLE (sufficiency criterion: van den Broek 1990/
2000; Graesser-Singer-Trabasso 1994 predictive inferences). Realized glass-box, NO external LLM, offline static assets:
1. GROUNDED MEANING CHANNEL (I3 proxy): event -> a 300-d meaning vector over the associative store
   (data/frontend_assets/associative_similarity_store_v1.npz, 80k x 300). Flat content-word mean AND the pinned
   SEM-style BOUND representation (HRR circular-convolution role-filler binding: norm(sum PRED (x) g(verb) + sum ARG
   (x) g(noun)) -- Franklin-Norman-Ranganath-Zacks-Gershman 2020; the flat feature bag is explicitly rejected by SEM).
2. FORWARD TRANSITION OPERATOR T (the missing organ): learn e_next ~= T . e_current by ridge over 141k-147k ATOMIC
   event->consequence pairs (at:xEffect / at:oEffect / /r/Causes -- general commonsense, PersonX templates, NOT
   narrative text, so NO leakage into TellMeWhy). Two operator forms: a single GLOBAL linear operator, AND the pinned
   SCHEMA-CONDITIONED nonlinear form = a MIXTURE of per-schema linear experts (k-means the head events into K schemas,
   one ridge per schema = SEM per-event-type theta_e / TEM per-relation D_a). glass-box, no gradient/long training.
3. N400 = UPDATE MAGNITUDE (the pinned scalar): Rabovsky-Hansen-McClelland 2018 -- N400 = L1 |change| in the meaning
   representation, NOT literal surprisal (surprisal is disconfirmed on reversal anomalies / Federmeier-Kutas). Scored
   as fwd_upd = the L1 update-magnitude REDUCTION C gives q (base L1 - L1 given C), diagnostically normalized.
4. DIAGNOSTIC normalization (inverse-planning, Baker-Saxe-Tenenbaum): subtract q's baseline predictability across
   candidates, so a promiscuous forward-predictor is penalized -- q must be UNUSUALLY predicted by C.
5. CLOSED FORWARD LOOP: forward_expect_fn = T . gist is now available to supply to n400_coherence_monitor (I2).

## PRE-REGISTERED CONTROLS (from the research note)
- OPERATOR SMOKE-GATE: Cohen's d of cos(T.head, TRUE consequent) vs cos(T.head, SHUFFLED), over the fitted pairs.
  >=0.5 = the operator learned real forward event-transition structure (a CONSTRUCTION proof, separate from the task).
- SHARED-PARTICIPANT-CONFOUND SUBSET (n=192): items where the SYMMETRIC topical proxy is fooled (picks a non-cause).
  Report the forward signal there + its INFO-FREE TWIN (permute the signal across candidates) -- HARD-PASS needs
  >=15pt over base AND CI-sep AND beating the twin (rules out subset-selection artifact).
- FULL info-free twin, item-level paired bootstrap, per-population (GOAL/OTHER).

## THE MEASURED RESULT (TellMeWhy non-adj, n=256; base_mult 0.2773, topical 0.2500)
| variant | operator gate_d | gate PASS | fwd_upd_add | HEAD-base FULL | twin beaten? | OTHER d | CONFOUND solo (base 0.052) / twin-p95 / beats |
|---|---|---|---|---|---|---|---|
| flat linear      | 0.333 | NO  | 0.285 | +0.0078 CI[-0.055,0.070] | NO | +0.037 | 0.213 / 0.318 / NO |
| BOUND linear     | 0.256 | NO  | 0.293 | +0.0156 CI[-0.051,0.078] | NO | +0.037 | 0.234 / 0.323 / NO |
| flat SCHEMA K=16 | 0.684 | YES | 0.289 | +0.0117 CI[-0.055,0.078] | NO | +0.012 | 0.219 / 0.318 / NO |
| BOUND SCHEMA K=16| 0.636 | YES | 0.297 | +0.0195 CI[-0.051,0.086] | NO | +0.055 | 0.234 / 0.323 / NO |

## THE DECISIVE DISSOCIATION (the deliverable the bar asked for -- ceiling named WITH a number)
- The OPERATOR CAN BE MADE STRONG: the schema-conditioned nonlinear form (the pinned SEM/TEM realization) lifts the
  construction gate from 0.26-0.33 (linear, FAIL) to 0.64-0.68 (PASS >=0.5). So the forward event-transition organ
  genuinely learns forward structure -- it predicts true consequences far better than shuffled ones. The research
  pin (linear-over-content rejected; nonlinear/schema-conditioned needed) was CORRECT and is confirmed on-disk.
- YET THE TASK IS INSENSITIVE TO IT: I MORE THAN DOUBLED the operator's forward-predictive strength (gate 0.256 ->
  0.684, +164%) and the full-population cause-selection delta BARELY MOVED (+0.008 -> +0.019; every variant TIES base,
  NONE CI-separated, NONE beats its info-free twin). Representation (flat vs SEM-bound) and scalar (cosine vs L1
  update-magnitude) likewise do not matter (all tie).
- THE CONFOUND "RECOVERY" IS A TWIN-FAILING ARTIFACT: on the confound subset base is pathologically low (0.052), so
  the forward signal "beats base +16-18pt" -- but it LOSES to its OWN info-free twin (obs 0.21-0.23 vs null p95
  0.32, p=0.85-0.98). A RANDOM reshuffle of the forward signal scores HIGHER than the real signal. So the forward
  signal carries NO real directional information beyond a random pick on exactly the hard items. The pre-registered
  twin caught the artifact the base-comparison missed.
- ITEM-LEVEL READ (n=256; gold-cause forward-rank mean 0.475 vs 0.5 random; frac gold ranked #1 = 0.27 ~= base 0.277):
  the forward model is a WEAK-BUT-REAL, GOLD-LIMITED signal, not noise. It gets CLEAN forward-transition cases right
  ("looked in classified ads for a job" -> "got a job offer"; "owner will enjoy his addition" -> "took photos"). It
  fails three ways: (a) GOLD-INCOMPLETENESS -- it picks a VALID alternate cause the sparse gold did not annotate
  ("Jay is an alumni" -> trip to college; "thrust the tool, the rock gave way"; "looked for clean pants" -> "looked in
  car") -> the tie UNDERSTATES true quality (same finding as the goal engine; Lal 2021 crowdsourced gold is
  non-exhaustive); (b) DIRECTION BLUR -- for subtle physical causation it prefers a consequence-like sentence ("it
  crumbled" over "pressed harder"); (c) FINE MARGINS -- many near-ties (0.637 vs 0.639).

## CONCLUSION -- the ceiling, and what it means for "is the chain brain-foundational"
THE CEILING (named, with a number): a CONSTRUCTION-VALIDATED forward event-transition model (Cohen's d = 0.68
true-vs-shuffled, clearing the pre-registered 0.5 bar) contributes +0.012-0.019 (CI includes 0) to full-population
cause-selection and NO real signal on the confound subset (loses to its info-free twin, p=0.85-0.98). The DIRECTIONAL
forward-prediction bet (research-calibrated P=0.15-0.20, UNTESTED before this work) is a LOCATED NEGATIVE, proven NOT
to be a weak-operator artifact: forward prediction over GENERAL commonsense (ATOMIC) does not discriminate WHICH
specific antecedent in a specific story is the cause, because the forward-predicted consequence of the true cause is
no better aligned with q than a distractor's at the granularity a general KB + a distributed meaning channel provide.
This CONVERGES with (a) the parent's ~8-way triangulation (every proxy is promiscuous), (b) the research's own point-D
caveat (ATOMIC is a general social-commonsense prior, not story-specific), and (c) the goal-engine gold-incompleteness
finding. It is the 9th independent triangulation point, and the STRONGEST: the operator-strength dissociation shows the
wall is STRUCTURAL (knowledge-granularity + gold-sparsity), not an implementation weakness.

WHAT THIS ADVANCES FOR THE CHAIN'S BRAIN-FIDELITY (the owner's actual ask):
- The one genuinely-MISSING organ (the forward event-transition model, audit I2's forward half) is now BUILT and
  CONSTRUCTION-VALIDATED to the full pinned spec (SEM bound representation + schema-conditioned nonlinear transition +
  Rabovsky N400-update-magnitude + inverse-planning diagnosticity). The forward loop CAN now be closed: forward_expect_
  fn = FT.predict(gist) is ready to supply to n400_coherence_monitor. This makes I2 brain-foundational IN FORM.
- BUT closing the loop does NOT lift THIS task, because the full-population cause-selection ceiling is the causal-edge-
  determination problem (knowledge-granularity + gold-sparsity), which the forward organ -- however strong -- does not
  cross with general commonsense knowledge. The only mechanism the evidence leaves open is a STORY-SPECIFIC generative
  model (online-learned event dynamics inside the recurrent loop, the parent's named MAIN EVENT), not a general
  forward prior. That is a multi-cell program.

## PROPOSED hdlab LANDING (strategy lands; Q111 -- I do not write hdlab/)
The forward organ is a real, validated chain-fidelity asset even though it does not lift THIS task. Two honest options:
1. LAND the forward event-transition operator as a foundation asset (ForwardTransition: schema-conditioned, gate 0.68)
   + wire forward_expect_fn into n400_coherence_monitor so the N400 is a genuine forward prediction-error (closing I2).
   This is brain-fidelity progress (the loop closes) and is VALIDATED on its OWN construction gate; it should be wired
   for its HOME benefit (the +0.067 CI-sep coherence win the monitor already documents on Story Cloze with a forward
   fn), NOT as a TellMeWhy cause-selection booster (measured tie).
2. Do NOT wire it into _read_causation (I1) as a cause-selection cue on TellMeWhy: measured tie + confound-artifact.
   The causal-edge determination needs the story-specific recurrent generative loop, not a general forward prior.
NO hdlab written here (Q111). owner_verdict not set (out of scope).

## REVERIFY
.venv/Scripts/python.exe experiments/exp_multistep_forward_transition_v1.py --self-test      # smoke (n=500, ~operator cached)
.venv/Scripts/python.exe experiments/exp_multistep_forward_transition_v1.py --run --n 1500 [--bound] [--schema 16]
Operators cached in data/exp_multistep_forward_transition_v1/forward_operator_{flat,bound}[_k16]_v1.npz;
metrics_{flat,bound,flat_k16,bound_k16}.json hold the four variants.

## TLDR (plain English)
A good reader explains an event by predicting it forward: the cause is the earlier thing that makes the later thing
UN-surprising. Our reader never did this forward step (it only looked backward), so I built the missing part -- a
"what-happens-next" model learned offline from a big commonsense list of everyday cause-and-effect, in the exact form
brain science describes (predicting the MEANING of the next event, measuring surprise as how much the mind's picture
has to CHANGE). I proved the new model really works: it predicts true consequences far better than random ones,
passing the quality bar. But when I used it to pick the cause in short stories, it did no better than our plain
baseline -- and, tellingly, no better than a SCRAMBLED version of its own signal on the hard cases. I made the model
more than twice as strong and the story score didn't budge. Reading the actual cases explains it: the model often
picks a DIFFERENT but still-valid reason the answer key didn't list, and on subtle cases it can't tell the cause from
the effect. So the honest result: the missing brain part is now built and verified, and we learned -- with numbers --
that a GENERAL "what happens next" model is not enough to pick the right cause in a specific story; that needs a model
that learns THIS story's own dynamics as it reads (the bigger recurrent build). The chain is now more brain-faithful
(the forward loop can close), but closing it alone does not win this particular task.

## QUESTIONS
None blocking. One labelling note for the owner: this is a rigorous LOCATED NEGATIVE (the bar's blessed full pass --
it names the ceiling WITH a number: a gate-0.68 forward model contributes +0.012-0.019, CI includes 0, confound
twin-failing) PLUS a concrete chain-fidelity advance (the missing forward organ, built + construction-validated). I
keep the problem PARTIAL (no full-population win); owner_verdict is yours.

## NEXT STEPS
- P1 (the only route the evidence leaves open): the STORY-SPECIFIC recurrent generative loop -- online-learn the
  current story's event dynamics (not a general ATOMIC prior) inside the predict->error->update loop over
  bound_event_backbone with resolved participants (the parent's MAIN EVENT + Franklin SEM online mode). The forward
  organ built here is the offline prior half; the missing half is the online, story-specific transition.
- P2 (measurement, likely the real lever): a COMPLETE / multi-reference eval -- the item-read shows a meaningful
  fraction of "errors" are valid alternate causes the sparse TellMeWhy gold omits, so the tie UNDERSTATES quality.
- WIRE FOR ITS HOME BENEFIT: supply forward_expect_fn to n400_coherence_monitor (closes I2; the monitor's own +0.067
  coherence win), independent of TellMeWhy cause-selection.
- DO NOT REDO: linear operator over content-bag (rejected pin, ties); the flat vs bound A/B (bound does not help on
  the task); cosine vs L1-update-magnitude (equivalent on the task); the confound subset as a "win" (twin-failing).
