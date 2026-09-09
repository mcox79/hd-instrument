# CROSS-SOLVER GROUNDING SYNTHESIS (2026-09-08) -- the grounding frontier, mapped

**Purpose:** after cycles 25-27 concluded "mechanisms are brain-foundational; the KNOWLEDGE substrate is ungrounded
text co-occurrence; the missing ingredient is GROUNDING," an Explore agent mapped the substrate + sibling solvers.
This is the load-bearing shared context for the grounding program. Read after SOLVED.md + the handoff RESUME block.

## THE CONVERGENT VERDICT (3 independent threads agree)
1. THIS problem (cycles 24-27): every KNOWLEDGE form -- static-associative (meaning_foundation), static-directed
   (ATOMIC), online-learned-generative (MINERVA echo) -- is NOT load-bearing; STRUCTURE (role-binding) is. The
   online forward model is AT CHANCE on its native task (Story Cloze 0.517). Diagnosis: ungrounded knowledge.
2. The converging causal-edge solver (`generate_dont_retrieve_causal_edges_for_unmarked_narrative_causation`,
   owner-DONE): "causation is ORTHOGONAL to association"; the gold is a POSITION ARTIFACT anti-correlated with
   predictive coherence (position_earliest 0.668 vs PC-criterion 0.236); the goal slice wins because it is the one
   place we SIMULATE (inverse planning). Brain does grounded mental simulation (Craik/Barsalou/Battaglia).
3. `grounding_does_not_accumulate...` (SOLVED): the correct sense is RETRIEVABLE but UNSELECTABLE by any
   distributional read-out (AUC ~0.49 = chance); GROUNDED sensorimotor+affect features (11 Lancaster + 3 Warriner)
   roughly DOUBLE correct selection (0.20 -> 0.35-0.48 CI-sep). Grounding carries signal co-occurrence lacks.

## WHAT ALREADY EXISTS (build ON, do NOT duplicate)
- **A WORKING online-learned generative world-model, AMODAL** (causal-edge solver, owner-DONE): `worldmodel_v1`
  online Rescorla-Wagner + Rao-Ballard predictive coding over verb-concept transitions (simplewiki, glass-box, NO
  LLM/gold/batch): held-out surprisal PC 7.247 < freq 7.531 < random 8.229, +0.247 bits CI-sep. `intrinsic_reader_v1`
  counterfactual-necessity over it: reader necessity 0.345 vs nearest 0.111 vs random 0.036 vs earliest 0.005,
  +0.308 bits CI-sep; antecedent is the nearest event only 32% (ESCAPES POSITION); converges with participants
  (0.649 vs 0.610 +0.038 CI-sep). Unbuilt levers THEY named: explicit FHRR participant-binding into the model +
  2-layer hierarchical Rao-Ballard. **RW delta-rule ~ Cheng ΔP contingency -> contingency is already partly done.**
- Sibling `chain_multi_step_plans...` (PARTIAL): ATL-hub means-end GOAL-subset **0.5326 vs base 0.2935 (+0.239
  CI-sep)**, coverage 8.7%->88%; forward event-transition organ over 141k ATOMIC pairs (full-pop ties base).
- `bridging_inference` (SOLVED): Kintsch PPR spreading-activation settling BEATS the static estimator held-out
  (0.531 vs 0.441) -- reusable "select the coherent link by settling" mechanism; named first live consumer of the
  latent meaning channel.
- `narrative_causal_graph` (SOLVED): covariation causal induction (Cheng power-PC / Griffiths-Tenenbaum, PINNED
  P0.68) types CAUSE-vs-PRECONDITION raw 0.890 vs majority 0.833 -- reusable "does a causal link EXIST" via ΔP.
- `close_the_recurrent_predictive_coding_loop...` (PARTIAL): closed-loop forward/backward EST monitor + SEM
  segmenter; coherence loop-closure PASSES +0.067 CI-sep.

## GROUNDED ASSETS ON DISK (honest state)
- `hdlab/grounded_similarity.py`: 12-d Lancaster sensorimotor + concreteness, 39,707 words (cover >=30000). GENUINELY
  PERCEPTUAL but a SIMILARITY metric capped 0.45 -- encodes "how I perceive/interact with X", NOT "what leads to X",
  nothing causal. LIVE as OOV fallback. Cannot separate antonyms (grounded cos(in,out)=0.556).
- `hdlab/grounded_semantic_graph.py`: WordNet++ (117k synsets, ConceptNet Causes/UsedFor/HasPrerequisite), PPR.
  Relational grounding (LANDED), not perceptual, not causal-simulation.
- `data/corpora/word_image_early_vocab/`: the ONLY true visual asset (Quick,Draw! bitmaps) -- UNBUILT stub.
- All rich (200-300d) reps (hub_ppmi_svd, meaning_foundation, associative_similarity, entity_type_spoke) = text
  co-occurrence = the ungrounded substance diagnosed.

## THE DECISIVE OPEN QUESTION (the wall, precisely)
DIRECTED CAUSAL/AFFORDANCE dynamics ("a store affords obtaining milk"; "studying produces preparedness") are
encoded by NO on-disk representation -- not the perceptual spoke (similarity, not dynamics), not the associative
hubs (co-occurrence), not the relational graph. The causal STRUCTURE must be LEARNED ONLINE. Text learning gives
association (co-occurrence) or contingency (RW/ΔP) -- the causal-edge solver showed contingency works on INTRINSIC
prediction/necessity but is INERT on the anti-correlated gold. So two candidate root-causes remain, to be
SEPARATED by experiment:
  (R1) MECHANISM lacks causation-isolation -> FIX: Cheng ΔP causal-power transitions (contrast vs base rate),
       not co-occurrence. [partly done via RW; test explicitly in the structured carrier.]
  (R2) REPRESENTATION lacks grounding -> FIX: perceptual sensorimotor fillers (proven to select where
       distributional cannot). [NEVER done inside a forward/world-model -- MY unique, non-duplicative contribution.]
  (R3) The GOLD is anti-correlated (position-artifact/best-explanation) -> use an INTRINSIC criterion or the GOAL
       slice (where simulation is the discriminator) as the instrument, not the full-pop explanation gold.

## THE PLAN (brain-foundational, non-duplicative; the cron drives it)
DECISIVE DRILL: separate R1/R2 in ONE structured world-model on the GOAL slice (the achievable target both solvers
agree on) + an intrinsic necessity criterion:
  - events = EventBundleCodec structured bind (the confirmed carrier; accepts an injectable symbol_codebook).
  - REPRESENTATION arm: amodal random fillers (cycle-27 baseline) vs GROUNDED perceptual fillers (project the 12-d
    Lancaster sensorimotor vector into the codec space) -> tests R2.
  - TRANSITION arm: co-occurrence-weighted vs Cheng ΔP causal-power-weighted (contrast vs base rate) -> tests R1.
  - controls: grounded-shuffle twin, contingency-shuffle twin, bind-shuffle; no-leak; goal slice + necessity.
  If grounding and/or ΔP lift where amodal-co-occurrence does not -> the lever is identified (validate, hand to
  strategy). If neither lifts even on the goal slice -> directed causal DYNAMICS are a genuine foundation to build
  (embodied/interaction learning we don't have), and that is the banked structural verdict.
KEY REUSE: `hdlab.event_bundle.EventBundleCodec` (inject grounded symbol_codebook), `hdlab.grounded_similarity`
(12-d perceptual), covariation ΔP (from `narrative_causal_graph` / Cheng power-PC), goal slice + necessity from the
cycle-13/27 machinery. LLM-free at inference. DO NOT rebuild the amodal PC world-model (causal-edge solver owns it).
