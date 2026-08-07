# PLAN OF RECORD — B (grounding): the WORD -> CONTEXT -> AFFECT superposition map

**Filed:** 2026-08-07 by Director, USER-confirmed direction (B is right; A = learned-free-via-exposure).
This is the authoritative architecture for the grounding program, co-designed with USER across the
2026-08-07 exchange. Supersedes the narrower "social-relational axis" formalize (notes/formalize_deepB_
grounding_social_relational_valence_2026-08-07.md), which becomes one BRICK of Layer 1 here.
Companion (read-the-code basis): hdlab/context_grounded_valence.py (owned physical-harm grounding).

## THE CORE IDEA (USER's design, VSA-native)
A word's meaning+emotion is NOT a fixed value -- it is a **superposition of possible (context ->
sense + affect) bindings that COLLAPSES to the right one when the situation supplies a context KEY.**
"Spoil" holds {ruin-a-thing -> outcome-negative} AND {pamper-a-person -> social-direction depends on
who}; the CONTEXT (privileged person + poor social behavior) collapses it to pamper -> social-negative.
This is exactly the substrate's native operation: bind(context (X) affect), BUNDLE into one vector,
UNBIND with the running context + CLEANUP -> the superposition collapses to the matching entry. USER
reached for "hypervector map that collapses with a context key" = the machine we already own.
MATCHES THE CODE'S OWN DIAGNOSIS: context_grounded_valence's notes name the missing piece as
"CONTEXT-CONDITIONED GROUNDING -- bag-of-words lacks the sense signal; sense resolution is inseparable
from context." USER named the exact gap.

## KEY SIMPLIFICATION (USER 2026-08-07): SOCIAL VALENCE = MENTAL/SOCIAL HARM
Social rejection/shame/exclusion is grounded, in the brain, by the SAME pain machinery as physical
harm (Eisenberger & Lieberman 2003: social exclusion -> dACC + anterior insula, the physical-pain
substrate; "social pain" borrows physical pain). => we do NOT need a separate "social value engine."
The SOCIAL-RELATIONAL channel supplies SOCIAL-HARM events (refuse/scorn/exclude = harm; accept/praise/
befriend = help) as INPUTS to the SAME earned harm<->help valuation we ALREADY own + proved on physical
harm (context_grounded_valence, Bopen=1.0). "Not 1-to-1" = the INPUT CHANNEL differs (social-relation
features vs animacy+force), the VALUATION is SHARED (harm=bad, common currency = OFC/vmPFC). This is
the tractability argument: social grounding REUSES the proven valuation, adds an input channel.

## THE THREE LAYERS
### Layer 1 -- GROUNDED AFFECT PRIMITIVES (the "colors"; B's experiential core)
A small set of FELT affect states (physical-harm/help ALREADY owned + earned; SOCIAL-harm/help = the
gap, grounded AS mental-harm via the shared valuation). Earned by reward-prediction-error over
experienced/simulated consequence (dopamine-analog teacher), NOT hand-labeled. These must be FELT or
the map points at nothing. Layer-1 gap = the social channel; the running experiment (exp_social_
relational_grounding_axis) tests whether it grounds the harm-axis way (supplied-seed first).
### Layer 2 -- the WORD -> CONTEXT -> AFFECT SUPERPOSITION MAP (USER's idea; learned)
Each word = a BUNDLE of (context-key (X) sense+affect) entries. **Dictionary supplies the CANDIDATE
senses** (spoil -> ruin OR pamper, WordNet -- invariant-OK DATA, a menu); the **(context -> which-sense
+ which-affect) binding is LEARNED** from exposure. Stored as a superposition; collapsed by the context
key at read-time. This is the layer USER's A-steer says must come "free through exposure + a robust
learning system" -- data-hungry, high-dimensional, CANNOT be hand-built (that was the detector-grind
anti-pattern).
### Layer 3 -- the CONTEXT-COLLAPSE READ (mostly owned)
The situation model forms the context KEY; unbind the word's superposition; cleanup -> the right sense
+ affect; feed comprehension/valuation. Owned: VSA unbind/cleanup + the situation model (coarse today).

## THE SUPPLIED-vs-EARNED LINE (USER drew it correctly)
- SUPPLIED (DATA, invariant-OK): the dictionary MENU of candidate senses (a word's possible meanings).
- EARNED (learned/grounded): (a) which candidate the context selects; (b) the AFFECT direction it
  carries; (c) the felt primitives themselves. "Spoil a privileged child -> social-negative" is NOT
  guessable -- it must be TAUGHT (USER emphatic). We supply the menu, we EARN the choosing + the feeling.

## THE LEARNING SIGNAL (the crux -- where "this use -> this direction" supervision comes from)
STORIES TEACH IT. When a story USES a word in a context and then SHOWS THE CONSEQUENCE (the spoiled
child behaves badly -> everyone unhappy), the story hands us the (context -> affect-direction)
supervision. Read stories-with-their-outcomes -> bind context->affect -> read more = the SELF-IMPROVING
READER (North Star). BUT this only works once Layer-1 PRIMITIVES are grounded (can't learn "unhappy=bad"
from text if "unhappy" is just a word). => **simulation grounds the felt primitives (Layer 1, small,
hard, once); EXPOSURE learns the map (Layer 2, large, ongoing, free-ish).** This UNIFIES B (ground
primitives) + the A-steer (learn from exposure) into ONE engine.

## BRAIN-FIDELITY (how close; what's missing; how the missing parts compute)
- OWNED + PROVEN: the VALUATION architecture (situation -> earned harm/help value -> read), open-vocab,
  physical harm (OFC-analog earned theta; RPE-analog teacher). The crown jewel.
- OWNED: VSA superposition/unbind/cleanup (Layer 2/3 storage); situation extraction (Layer 3 key, coarse);
  RPE + self-extension loop + learner (the engine to fill Layer 2).
- MISSING #1 -- the SOCIAL input channel (Layer 1 social). Brain: TPJ/mPFC (mind-reading: is the other
  accepting/rejecting me?) -> feeds the shared harm/pain valuation (dACC/insula social-pain overlap).
  Compute: SAME valuation, a social-relation feature channel instead of animacy+force. = the running
  experiment.
- MISSING #2 -- the SOCIAL EXPERIENCE to earn from. Brain: years of lived social episodes + dopamine-RPE
  write the values. Compute: IDENTICAL learning rule, run over SOCIAL outcomes. What we lack is the
  EXPERIENCE (training data of felt social consequence) -- the field's 45-yr wall. Fix: minimal
  experiential-social simulation (earn) and/or small supplied social seed (bootstrap) + exposure.
- MISSING #3 -- CONTEXT-CONDITIONED collapse at scale (Layer 2 learned). Brain: ATL semantic hub
  represents a word's meaning as CONTEXT-MODULATED (situation biases which sense/affect is active).
  Compute: the superposition-map + learned context->affect bindings = a faithful VSA realization of
  context-modulated hub semantics.

## HONEST HARD EDGES
1. The context KEY must be rich enough to distinguish the cases (spoil-cake vs spoil-privileged-child) --
   but rich social context is itself the thing we're building = a mild bootstrap (key + map co-sharpen).
2. The map is high-dimensional + data-hungry -> ONLY works as a learning system, never hand-built.
3. The learning signal (edge above): primitives need grounding first (simulation/innate seed), THEN the
   map learns from stories-with-consequences.

## BUILD ORDER (can-fail per stage)
1. **[✅ DONE = HARD_PASS, ca1d70d1a, Director-VET'd] Social affect primitive GROUNDS the harm-axis way.**
   exp_social_relational_grounding_axis_v1 (isolated, 5 seeds, full): a 12-word supplied social seed
   (praise/accept/... vs refuse/scorn/...) propagated to open vocab via wordnet_polarity_propagation
   (the "no free WordNet social axis" risk had a working substitute already in the codebase), fed the
   SAME frozen appraisal-sim theta valuation as physical harm. MEASURED (Director confirmed off
   metrics.json): open-vocab acc 0.833 on 12 HELD-OUT test verbs (appreciate/humiliate/snub/spurn/... ,
   test_disjoint_from_seed=True); scramble 0.483 (lift 0.35); seed-ablation 0.000 (seed IS the lever);
   random-theta 0.467 (near chance -> the EARNED valuation, not noise, does the work). => **CONFIRMED:
   social valence grounds like physical harm (= mental harm, shared valuation), via supplied-seed +
   WordNet propagation + the owned earned theta -- Layer-1 social primitive is REAL, not vacuous.**
   Open: this is the SUPPLIED-seed version; the deeper experiential-social-simulation (EARN the seed)
   is Stage 5. But the architecture (social channel -> shared harm valuation) is proven.
2. **Layer-1 social channel** wired into the owned valuation (social-harm events -> earned harm value).
3. **[✅ MECHANISM PROVEN = HARD_PASS, 04af969c4, Director-VET'd] Layer-2 superposition map + taught
   context-collapse.** exp_word_context_affect_superposition_map_v1: each word = bundle(bind(context_key
   (X) sense)) over FHRR senses; context key = patient animacy (owned); (context->sense) binding TAUGHT
   from labeled TRAIN, tested on HELD-OUT TEST nouns; sense affect = Stage-1's valuation. 6 words (spoil/
   beat/strike/whip/crush + cherish single-sense). MEASURED (5 seeds, Director confirmed off code+metrics):
   held-out collapse 1.000; SCRAMBLE 0.400 (lift 0.600 -> bindings are LEARNED not lookup = the decisive
   control); context-driven divergence 1.000; single-sense baseline 1.000 stable. **DECISIVE ANTI-CONFOUND
   (real in code): `spoil` polarity DELIBERATELY REVERSED vs beat/strike/whip/crush -> the SAME animacy
   feature selects OPPOSITE senses per word -> a generic "animate->X" heuristic would FAIL spoil; it
   doesn't -> the map learned WORD-SPECIFIC bindings.** => USER's superposition-map + taught-collapse
   architecture is PROVEN at the mechanism level. HONEST BOUNDARY: coarse context key (2-way animacy) +
   HAND-TAUGHT bindings -> a mechanism proof, NOT rich generalization; next = richer context keys +
   LEARN-from-exposure (stage 4).
4. **Layer-2 learning from exposure**: fill the map by reading stories-with-consequences (self-improving
   reader); the RPE/learner writes context->affect bindings. Can-fail: held-out words' affect learned
   from exposure, not seeded.
5. **Earned primitives** (deeper): swap supplied seeds for experiential-simulation-earned affect.

## INVARIANTS
Glass-box always; dictionary MENU = supplied data OK; selection+affect+primitives = EARNED (no
hand-labeled per-word valence, no borrowed embedding/LLM at inference); VSA-native storage; reuse the
owned valuation + VSA + learner (wire-don't-island); brain-faithful (shared valuation, social=mental-
harm, context-modulated hub). Formalize-first honored (this doc); build stage-by-stage, can-fail, VET
each, USER-visible.

## STATUS
Direction USER-confirmed. Stage 1 IN FLIGHT (Director will VET + fold in). Stages 2-5 are the program.
This doc = the B plan of record; the situation-model competency work (polarity 11->17, owner 18->13,
dialogue-goals) is the STRUCTURAL reading that this grounding will feed with felt meaning.
