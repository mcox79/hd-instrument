# M1.10 Response Planner primitive - design drill

**Date:** 2026-07-02
**Author:** research (Director main-thread, inline; sister to M1.9 SemanticParser design shipped earlier today)
**Trigger:** USER 2026-07-02 - M1.9 CG'd at K=5 compositional depth; M1.10 is the OUTPUT-composition sister primitive.

**Framing discipline (LOAD-BEARING, USER 2026-07-02):** all cortex mechanism primitives operate on HD vectors, NOT English text. M1.10 does NOT "generate a response in words." It takes an HD (intent + retrieved-fact context + slot-fillers) and produces an HD (response frame + response role-slots) that a future Stage 4 decoder will translate to tokens. See `feedback_never_narrate_synthetic_HD_bundles_as_english_language_capability_USER_2026-07-02.md`.

---

## 1. Prior-work check (substrate-KB concept-queries with cosine)

Four substrate-KB queries run BEFORE this design. Top hits:

| Query | Top hit | Cosine | Interpretation |
|---|---|---|---|
| "response planner output composition generation" | "Text-vision composition (caption generation)" | 0.4502 | Loose composition, not M1.10-specific. No prior M1.10 work. |
| "bind bundle role slot codebook construct output hd" | "Codebook construction (Maiorana-McFarland)" | 0.2646 | Mechanism-level bind primitives well-established; no output-side application. |
| "template retrieval nearest neighbor codebook response" | "O(1) retrieval - fundamental or approximate?" | 0.3096 | Retrieval mechanism CG'd; template-based-NLG lit hit at 0.30 (Reiter/Gatt & Krahmer 2018 - 50-100 templates give 80-90% domain coverage). |
| "M1.9 semantic parser unbind cleanup slot extraction" | prior M1.9 drill discussion of unbind + cleanup | 0.2793 | Sister primitive design known; forward direction of same group operation. |

**Conclusion:** no prior arc work explicitly on M1.10 / response planner. **Substrate-KB EMPTY on this concept.** Design is genuine (not rediscovery). Adjacent CG'd primitives (IntentClassifier, HRR/BSC bind-unbind, sharded storage per CG_META, template-based generation research) all leverageable.

---

## 2. Brain analog - Broca's area + dlPFC + procedural memory

**Plain-English intuition (for USER):**

Think of Broca's area as a mailroom clerk assembling shipping packages. Given a shipping label (intent) and a list of items to send (slot-fillers), the clerk grabs the right pre-labeled box template from a shelf (response frame), stuffs each item into its labeled compartment, and hands the whole package to the delivery guy (Stage 4 decoder, deferred). The clerk does NOT invent new boxes - they PICK a box from a fixed shelf and FILL it. That is what M1.10 does. In substrate terms: retrieve a response-frame HD from a codebook, then bind response-role keys to slot-filler HDs and bundle everything into a single response HD.

**Formal brain grounding:**

**Broca's area (left inferior frontal gyrus, BA 44/45)** - production-side compositional assembly. Kaan & Swaab 2002, Friederici 2011 phase III (reanalysis + integration), Sahin et al 2009 Science "Sequential processing of lexical, grammatical, and phonological information within Broca's area" - Broca serially binds lexical items into a grammatical structure. Substrate analog: bind role_keys with slot_fillers, bundle into response_hd.

**dorsolateral PFC (dlPFC)** - task/goal maintenance across the plan-generation window. Miller & Cohen 2001 Annu Rev Neurosci "An integrative theory of prefrontal cortex function" - dlPFC holds the goal representation active while lower areas assemble the response. Substrate analog: `intent_hd` (from M1.9 output) is held active as the top-level bind key that anchors the entire response composition.

**Basal ganglia + procedural memory (response schemas / templates)** - Graybiel 1998, Ashby & Ennis 2006 "Motor and cognitive schemas in the basal ganglia" - action / response schemas stored in striatum; PFC selects among them. Substrate analog: response-frame codebook. Selection = cleanup against frame codebook. This is where template-retrieval literature (Reiter 2019) meets brain-grounded mechanism.

**Fedorenko-Piantadosi 2024 Nature "Language is primarily a tool for communication rather than thought":** the language production network is DISTINCT from the reasoning network. Production is a specialized bind/assembly operation, NOT general problem-solving. Substrate implication: M1.10 is a SPECIALIZED primitive (frame + slot bind), not a general classifier. Matches M1.9's symmetric specialization on the parse side.

**Cite ledger:**
- Sahin, Pinker, Cash, Schomer, Halgren 2009 Science "Sequential processing of lexical, grammatical, and phonological information within Broca's area"
- Miller & Cohen 2001 Annu Rev Neurosci "An integrative theory of prefrontal cortex function"
- Ashby & Ennis 2006 J Cog Neurosci "The role of the basal ganglia in category learning" (schema-selection)
- Reiter 2019 blog + Gatt & Krahmer 2018 JAIR survey (template-based NLG coverage bounds)
- Fedorenko, Piantadosi, Gibson 2024 Nature "Language is primarily a tool for communication rather than thought"

---

## 3. Mechanism candidates (a/b/c/d)

The design-question options, weighed against substrate primitives available and brain analog:

**(a) Retrieval-style (template pick)** - given query HD, nearest-neighbor over response-template codebook, emit template as response_hd. Simple. Matches Reiter template-NLG (50-100 templates = 80-90% coverage). BUT: no slot filling; response is FROZEN at template granularity. No compositionality. Loses the reason we have a substrate.

**(b) Transformation-style (learned/fixed transform)** - given query HD, apply single transform to produce response HD. Substrate-native but degenerate: what IS the transform? If fixed, it is a permutation - no expressive power. If learned, we are outside chain-grade territory (learning is Stage 4 territory).

**(c) Composition-style (bind + bundle response role-slots)** - symmetric to M1.9. Given intent_hd + retrieved facts, bind response_role_keys with response_slot_fillers, bundle everything. Substrate-native. Provably invertible by group algebra (bind = HRR circular conv / BSC XOR; both invertible). Loses: no "shape" constraint on the response - risks producing bundles that are structurally invalid (missing role, wrong count).

**(d) Hybrid - RECOMMENDED - frame retrieval + slot binding**
- Step 1: retrieve response_frame_hd from a frame codebook (basal-ganglia analog).
- Step 2: unpack the frame's ROLE_SET (which roles this frame requires).
- Step 3: for each required role, bind response_role_key with the appropriate slot_filler (from M1.9 slots, from retrieval facts, or from intent-driven defaults).
- Step 4: bundle frame_hd + all bound (role, slot) pairs into response_hd.

This is the CORRECT answer because:
- Matches brain analog (dlPFC intent + basal-ganglia frame + Broca's slot-assembly).
- Symmetric to M1.9 (M1.9 UNBINDS role_key from a bundled input to recover slot; M1.10 BINDS role_key with slot to produce bundle - INVERSE operation, same algebra).
- Roundtrip discriminator becomes cheap: M1.9(M1.10(intent, slots)) should recover (intent, slots) up to cleanup tolerance. This is a STRONG mechanism proof.
- Frame retrieval bounds the response shape (avoids structurally invalid bundles from pure (c)).
- Chain-grade primitives cover every step: nearest-neighbor cleanup (CG), bind (CG_META), bundle (CG_META), sharded frame codebook (CG_META storage strategy).

**Winner: (d) Hybrid frame-retrieval + role-slot binding. Bake in as v1.**

---

## 4. Concrete cell design (Stage 3 v1)

**Anchor:** `substrate_response_planner_frame_slot_composition_v1`

**Substrate-KB concept-query BEFORE ship:** MANDATORY - re-run this drill's queries plus `bash tools/substrate_query.sh "response planner frame slot composition v1 cell"` before cell-author ships. Verify no rediscovery risk.

**Cell file:** `experiments/exp_substrate_response_planner_frame_slot_composition_v1.py`

**Config:**
- `n_dim = 8192` (inherited from cortex primitives)
- `n_response_frames = 20` (Stage 3 personal-assistant domain: ACKNOWLEDGE, ANSWER_FACT, ANSWER_YESNO, CLARIFY, DEFER, REFUSE, LIST, COMPARE, ...)
- `n_response_roles = 5` (SUBJECT, OBJECT, ATTRIBUTE, TIME, LOCATION - symmetric to M1.9)
- `slot_dict_size_per_role = 100` (sharded per CG_META)
- `n_train_examples = 300` (frame codebook prewired; slot dicts inherited from M1.9)
- `n_test_examples = 200`
- `seeds = [11, 17, 23]` (3-seed smoke gate mandatory per Skunkworks META CG 2026-07-02)
- Inputs: (intent_hd, {role: slot_filler_hd}) tuples generated from a synthetic Stage 3 schema (SAME schema as M1.9 for roundtrip test to work).

**Arms (per-arm smoke at full-N per DISCRIMINATOR_MUST_SURVIVE_SCALE):**
- `ARM_TEMPLATE_ONLY`: response = retrieved frame HD, no slot filling. Establishes template-selection floor.
- `ARM_COMPOSE_ONLY`: bind role+value bundle, NO frame retrieval. Establishes pure-composition floor.
- `ARM_HYBRID`: frame retrieval + role-slot binding (RECOMMENDED mechanism).
- `ARM_SHUFFLED_RESPONSE_ROLE_KEYS`: shuffle role_keys before bind; roundtrip fidelity MUST collapse (sanity control that role-binding is doing real work).
- `ARM_M19_ROUNDTRIP`: END-TO-END roundtrip - M1.9 parse (intent_gt, slots_gt) -> M1.10 plan (response_hd) -> M1.9 parse again (intent_recovered, slots_recovered). Check intent + slots recovered. THIS is the strongest mechanism proof; it validates that the substrate can COMPOSE AND DECOMPOSE round-trip without information loss.

**Discriminator + bands:**
- Frame-match accuracy: does cleanup of response_hd against frame codebook recover the expected frame? Measured against synthetic ground-truth.
- Roundtrip slot fidelity: does M1.9 re-parse of response_hd recover the input slots? Per-role accuracy averaged.
- Sanity collapse: ARM_SHUFFLED_RESPONSE_ROLE_KEYS roundtrip slot fidelity MUST drop toward random.

**Bands:**
- **HARD_PASS:** frame-match >= 0.85 (matches IntentClassifier CG floor); ARM_M19_ROUNDTRIP slot fidelity >= 0.80; ARM_HYBRID beats ARM_TEMPLATE_ONLY on slot fidelity by >= 0.30 (proves compositional slot fill is doing work beyond template-alone); ARM_SHUFFLED collapses to <= 0.20; 3 seeds all pass.
- **MIDDLE_BAND:** frame-match in [0.70, 0.85) OR roundtrip fidelity in [0.60, 0.80) - partial composition; investigate frame-slot cross-talk.
- **HARD_FAIL:** frame-match < 0.70 OR roundtrip fidelity < 0.60 OR ARM_SHUFFLED > 0.30 (role-binding not doing work).

**Envelope-fail bands:**
- If ARM_TEMPLATE_ONLY frame-match < 0.95 on synthetic data: SCHEMA_BROKEN (templates should be trivially recoverable when no compositional work is required), halt and repair.
- If ARM_COMPOSE_ONLY roundtrip fidelity > ARM_HYBRID roundtrip fidelity by > 0.03: frame retrieval is HURTING, cell has an integration bug, HARD_FAIL.

**CARDINALITY_OK field:** MANDATORY per META_RULE_H - declare EXPECTED_N_UNITS = 5 arms x 3 seeds x 200 test = 3000 rows. HARD_FAIL_CARDINALITY_BREACH if observed < 2800.

**Sharded storage:** response_frame_hd stored in a S-bank; slot dictionaries INHERITED from M1.9 (composition proof - same dicts serve parse AND plan). This is the cleanest possible composition test.

**Multi-seed smoke gate:** MANDATORY per Skunkworks META CG 2026-07-02. Smoke on local CPU (per USER 2026-07-01 smoke-only-local-cpu rule); FULL on remote_cpu_queue.

**Runtime estimate:**
- Smoke (3 seeds x 5 arms x 200 test): ~7 min local CPU (Hebbian binds O(n_dim); cleanup O(n_dim * codebook_size) per emit).
- FULL (3 seeds x 5 arms x 1000 test): ~20 min remote CPU. Not GPU-required (no matmul-batch heavy enough per GPU-batching-mandatory rule); CPU appropriate.

**Metrics.json REQUIRED_FIELDS (per SCHEMA-VET checklist):**
- `frame_match_acc_per_seed_per_arm`
- `roundtrip_slot_fidelity_per_role_per_seed_per_arm`
- `roundtrip_slot_fidelity_overall_per_seed_per_arm`
- `hybrid_vs_template_only_slot_lift`
- `arm_shuffled_response_role_keys_collapse_metric`
- `n_rows_observed`
- `n_rows_expected`
- `cardinality_ok`
- `run_mode` ("smoke" | "full" per METRICS_PATH_DISAMBIGUATION discipline)

---

## 5. P_CG estimate + justification

**P_CG = 0.60.**

Justification (per lit-scan calibration penalty - deflate 0.15-0.25; extension of CG primitives so 0.50 novel-synthesis cap does NOT apply):

**Initial estimate before penalty: 0.75.**
- M1.10 is the INVERSE algebraic direction of M1.9 (which just CG'd at K=5). VSA bind is provably invertible by group algebra; if unbind works, bind works.
- Frame-codebook retrieval is textbook cleanup (Kanerva 1988 SDM, Plate 1995 HRR) - established, chain-grade.
- Response-frame retrieval + slot fill matches template-NLG lit (Reiter & Dale 2000; Gatt & Krahmer 2018 - 80-90% domain coverage from 50-100 templates; we have 20 for a narrower Stage 3 domain).
- Roundtrip discriminator with M1.9 is CHEAP and STRONG - if the bind-unbind pair preserves information, M1.9(M1.10(x)) = x up to cleanup tolerance.
- Sharded storage per CG_META, HRR/BSC bind-unbind chain-grade, IntentClassifier/cleanup CG - every leg leverages existing CG primitives.

**Deflate 0.15 for:**
- Frame-vs-slot cross-talk: if response_frame_hd similarity is high to slot-filler distributions, bundling may corrupt frame identifiability during roundtrip. Empirical unknown - penalize.
- Roundtrip discriminator novelty: no prior CG evidence of this exact metric; risk of unforeseen calibration issues.
- Bundle capacity at 20 frames + 5 roles x 100 slots each: fits at N=8192 comfortably per capacity_optimal work, but roundtrip fidelity depends on cleanup working from a noisy bundle - noise budget shrinks as frame_hd + 5 bound role_slot pairs are all superposed.

**Boost 0.10 for M1.9 sister symmetry:** M1.9 CG at K=5 compositional depth today means the bind-unbind primitive is validated in one direction; algebraically it works in the other direction by construction. This session evidence tilts P upward beyond pure lit-scan floor.

**NOT novel synthesis** - this extends existing CG primitives (bind-unbind, sharded storage, cleanup) + established template-NLG mechanism. 0.50 novel-synthesis cap does not apply.

**Final: 0.75 - 0.15 = 0.60.**

**Failure modes and probability:**
- Frame-slot bundle cross-talk (frame_hd + role_slot pairs superpose destructively): P ~ 0.20. Mitigated by n_response_frames=20 << slot_dict_size=100, giving frame codebook lower density.
- Roundtrip decay from noise-budget shrinkage across bundle: P ~ 0.20. Mitigated by cleanup at n_dim=8192.
- ARM_M19_ROUNDTRIP fails because M1.9 v1 was tested against clean inputs, not against M1.10-composed bundles: P ~ 0.10. This is a composition-test risk - if roundtrip fails, that is a signal about M1.9 robustness under bundle noise, not necessarily an M1.10 bug.
- MIDDLE_BAND on partial cross-talk (frame solid, slot roundtrip partial): P ~ 0.25.

**Total P_CG after v1 iteration: 0.60.** Total P_MB or P_CG after v2 iteration on roundtrip root-cause: 0.75+.

---

## 6. Composability with M1.9 (they chain: M1.9 output -> M1.10 input)

M1.9 output shape (from sister design):
- `intent`: int (from IntentClassifier)
- `slots`: Dict[role, value_hd]
- `parse_hd`: bundled intent + role-bound slots
- `discourse_state`: enum

M1.10 input shape (proposed):
- `intent_hd`: HD (from M1.9 intent -> codebook lookup)
- `retrieved_facts`: Dict[role, filler_hd] (from M1.9 slots + M1.5/M1.6 retrieval augmentation)
- `discourse_state`: enum (drives frame selection - CLARIFICATION intent picks CLARIFY frame; STATEMENT picks ACKNOWLEDGE; Q_FACT picks ANSWER_FACT; etc.)

**Full cortex chain (M1.9 -> retrieval -> M1.10):**

```
token_sequence
  |
  v
[CharTrigramEncoder] --> input_hd
  |
  v
[M1.9 SemanticParser] --> {intent, slots, parse_hd, discourse_state}
  |
  v
[M1.3 NoiseChannel] --> parse_hd_noisy
  |
  v
[M1.6 chunked_attention_readout(parse_hd_noisy, ...)] OR [M1.5 STM read]
  |
  v
retrieved_facts (Dict[role, filler_hd])
  |
  v
[M1.4 apply_refuse] --> refuse flag (short-circuits to REFUSE frame if triggered)
  |
  v
[M1.8 ClarifyGate] --> route (short-circuits to CLARIFY frame if triggered)
  |
  v
[M1.10 ResponsePlanner(intent_hd, slots union retrieved_facts, discourse_state)]
  |     Step 1: select frame from response_frame_codebook via discourse_state + intent
  |     Step 2: unpack frame ROLE_SET
  |     Step 3: for each required role, bind response_role_key with slot_filler
  |     Step 4: bundle frame_hd + bound (role, slot) pairs --> response_hd
  |
  v
response_hd (M1.10 output; Stage 4 decode deferred)
```

**Key composability claims:**
- M1.9 slots (Dict[role, value_hd]) are DIRECTLY consumed by M1.10 as slot fillers - zero-copy composition.
- M1.9 discourse_state DIRECTLY drives M1.10 frame selection (FOLLOWUP -> continuation frame; CLARIFICATION -> clarify frame; NEW_TOPIC -> acknowledge frame).
- M1.9 unbind operation and M1.10 bind operation use the SAME role_key codebook (roles are shared) and the SAME bind algebra (HRR circular conv or BSC XOR). Symmetry is architectural, not accidental.
- The ARM_M19_ROUNDTRIP arm in the M1.10 cell IS a composition test: it validates M1.9-then-M1.10-then-M1.9 preserves the parse, which is the STRONGEST possible chain-grade evidence for the sister-pair.
- CortexResponse extension will need `m110_response_hd`, `m110_frame_id`, `m110_role_slot_map` fields (backwards-compat by default).

**Order-of-ops rationale (brain-grounded):**
- Parse-then-retrieve-then-plan mirrors ventral-stream comprehension (Wernicke/temporal) -> hippocampal retrieval -> prefrontal planning (dlPFC + Broca).
- Frame selection driven by discourse_state matches basal-ganglia schema selection (Ashby & Ennis 2006).
- Bind assembly in M1.10 mirrors Broca serial grammatical assembly (Sahin et al 2009).
- Fedorenko-Piantadosi separation of parse/reason/produce holds: M1.9 parses, retrieval + M1.4/M1.8 reasons/gates, M1.10 produces.

**When M1.10 lands, cortex.py forward() needs a modest patch:** after M1.4/M1.8 gating, invoke M1.10 with (intent_hd, slots union retrieved_facts, discourse_state) to produce response_hd. Extend CortexResponse with m110_* fields. Backwards-compat: if M1.10 disabled, forward() returns unchanged shape.

---

## Summary

- **Prior work check:** substrate-KB EMPTY on M1.10 concept (top cosine 0.45, all superseded=filtered; template-NLG at 0.30). Not rediscovery - genuine new design.
- **Recommended mechanism: (d) Hybrid frame-retrieval + role-slot binding.** Frame codebook (basal-ganglia analog) picks the response schema; role_keys bind with slot_fillers (M1.9 slots union retrieved facts); bundle to response_hd. Symmetric inverse of M1.9's unbind-then-cleanup.
- **Brain analog (plain-English):** Broca's area as mailroom clerk - retrieves pre-labeled box template (frame), stuffs labeled items (slots) into compartments, hands package to delivery guy (Stage 4 decoder, deferred). dlPFC holds intent active as top-level anchor; basal ganglia selects the schema; Broca assembles.
- **P_CG = 0.60** (deflated from 0.75 initial per lit-scan calibration; boosted 0.10 for M1.9 sister-symmetry algebraic guarantee; extension of CG primitives so 0.50 novel-synthesis cap does not apply).
- **Composition with M1.9 is tight:** M1.9 slots DIRECTLY feed M1.10 slot_fillers zero-copy; M1.9 discourse_state DIRECTLY drives M1.10 frame selection; SAME role_key codebook and SAME bind algebra used in both directions - symmetry is architectural.
- **Cell anchor:** `substrate_response_planner_frame_slot_composition_v1` with 5 arms including ARM_M19_ROUNDTRIP (STRONGEST mechanism proof - M1.9(M1.10(x)) recovers x) + ARM_SHUFFLED_RESPONSE_ROLE_KEYS sanity control; 3-seed smoke gate; HP frame-match >= 0.85 + roundtrip fidelity >= 0.80 + hybrid-over-template lift >= 0.30; sharded storage per role INHERITED from M1.9 (composition test).
- **Follow-ons filed:**
  - M1.10 v2: expand frame codebook to n=100 (approaches Reiter/Gatt-Krahmer 80-90% coverage regime).
  - M1.10 Stage 4: real-language response with open-vocab decoder head - deferred until Stage 3 v1 CG + Stage 4 language ingest infra.
  - Cortex.forward() patch to invoke M1.10 after M1.4/M1.8 gating - backwards-compat default.
  - M1.9 <-> M1.10 roundtrip becomes a permanent regression test for cortex integration.

**Dispatch decision:** author Stage 3 v1 cell next; hand off to hdi_exp_dev for cell authoring + pre-reg + smoke gate. Do NOT ship until substrate-KB concept-query re-run + Skunkworks SCHEMA-VET on the pre-reg + M1.9 v1 confirmed landing (roundtrip arm depends on M1.9 v1 being callable from the M1.10 cell).
