# Pre-registration: evaluative-speech-act bridging inference (2026-08-06)

## Task / brief
Director's brief (2026-08-06, following `notes/audit_SYNTHESIS_semantic_meaning_barrier_2026-08-06.md`
+ `notes/audit_brain_composition_situationmodel_2026-08-06.md`): build the first increment of the
missing INFERENTIAL layer for the semantic-meaning barrier -- a Graesser Class-7 BACKWARD
causal-antecedent BRIDGING-INFERENCE path from an evaluative speech act ("you are a good boy") back
to a standing GOAL, for the case where the outcome clause shares ZERO verb/theme/thematic-role with
the goal clause (so no similarity/verb-typing/theme-match mechanism can ever bridge them).

## Prior-work check (substrate-KB, mandatory per exp_dev discipline)
`bash tools/substrate_query.sh "evaluative speech act bridging inference goal outcome praise
criticism causal antecedent Graesser class 7"` -> max cosine = 0.252 (meta::comprehension_frontier...
cert_ledger entry, a general "semantic relation inference is the frontier" note, not this specific
build). NONE at cosine>0.30. Genuinely novel increment, not a rediscovery.

## Mechanism (strict ADD, reuses owned organs, no new binding operator)
1. DETECT: `detect_evaluative_construction(sentence, roster)` -- a copula (is/are/was/were) followed
   within a small window by an evaluative adjective from a hand-supplied POS-blind valence lexicon
   (EVAL_POS / EVAL_NEG, same SUPPLY-schema pattern as `RESULT_VERB_CLASS` / `V2_OUTCOME_MET/_UNMET`
   in `hdlab/goal_typing.py`). Addressee resolved via (a) 2nd-person "you...Name" vocative (last
   roster name in the sentence) or (b) 3rd-person "Name is/was ADJ" (roster name immediately
   preceding the copula).
2. VALUE: POS -> praise, NEG -> criticism (lexicon lookup only, NOT verb-class typing).
3. BRIDGE: reuse `hdlab.goal_owner_select.GoalOutcomeRegister` (byte-identical, unmodified) --
   `bridge_outcome(entity, sentence, roster, register)` fires ONLY if the evaluative construction's
   addressee == `entity` AND `register.appraise(entity)["has_goal"]` is True (entity currently holds
   an open GOAL). POS+has_goal -> OUTCOME_MET; NEG+has_goal -> OUTCOME_UNMET. No match / no open
   goal -> abstain (None), never forces a bridge.
4. STRICT-ADD GATING: the harness tries LEXICAL verb-typing (`hdlab.goal_typing.type_goal_events`,
   unmodified production organ) on the outcome sentence FIRST; the bridge is only ever consulted
   when verb-typing produced NOTHING (the OUTCOME_NEVER_TYPED case). When verb-typing already fires,
   behavior is byte-identical to today's production path (bridge code never runs).

No production file (`hdlab/goal_typing.py`, `hdlab/goal_owner_select.py`) is modified -- this cell is
a self-contained harness that imports those modules read-only. Cert-gate (`verification/
run_certification.py`) is therefore NOT required for this increment (no production code touched).

## Instrument
Hand-authored bank, `experiments/data/evaluative_bridging_bank_v1.jsonl`, N=13 items, 4 categories:
- POS_MET (n=6, incl. `mg2_henry_bootblack` VERBATIM from `experiments/data/
  real_text_goal_owner_diagnostic_v1.jsonl`): goal clause + a later PRAISE evaluative outcome clause
  directed at the goal-holder, ZERO shared verb/theme/thematic-role between the two clauses (checked
  mechanically in self-test: content-token intersection, minus roster names and a closed-class
  stopword list, is empty).
- NEG_UNMET (n=3): same shape, CRITICISM instead of praise -- control (i), valence-correct.
- BYSTANDER (n=2): the evaluative sentence addresses a roster entity with NO open goal in this
  passage (a different entity holds the real goal but is not addressed) -- control (ii), the bridge
  must NOT fire on anyone (neither the addressed non-holder nor the un-addressed true holder).
- UNCHANGED (n=2): an ordinary verb-typed outcome (e.g. "won", "reached" -- literal V2_OUTCOME_MET
  hits) where verb-typing already succeeds -- control (iii), the bridge must never engage (harness
  records `source` per item; UNCHANGED items must show `source=="LEXICAL"`, never `"BRIDGE"`).

Arms: (a) BRIDGING (strict-add mechanism above) vs (b) LEXICAL-ONLY (production `type_goal_events`
verb-typing alone, no bridge step) -- (b) is expected to abstain on every POS_MET/NEG_UNMET item by
construction (zero lexical overlap).

Control (iv) SCRAMBLE: a fixed-seed cyclic shift (offset=1, asserted zero-fixed-points) reassigns
each POS_MET/NEG_UNMET item's GOAL register to a DIFFERENT item's register before bridging; all 9
item names are distinct, so a shuffled register never has an open goal for the real addressee ->
bridging is predicted to collapse to 0/9.

## Bands (declared before running)
- `zero_overlap_bridging_acc` = accuracy of arm (a) on the 9 POS_MET+NEG_UNMET items (exact dict
  match: bridge binds MET/UNMET to the gold goal-holder and nobody else), incl. mg2 correct.
- `lexical_only_acc` = accuracy of arm (b) on the same 9 items (predicted ~0.0, cannot bridge).
- `gap` = zero_overlap_bridging_acc - lexical_only_acc.
- `valence_pos_acc` = fraction of the 6 POS_MET items bridging to MET (not UNMET).
- `valence_neg_acc` = fraction of the 3 NEG_UNMET items bridging to UNMET (not MET).
- `bystander_no_bridge_acc` = fraction of the 2 BYSTANDER items where arm (a) binds NOBODY.
- `unchanged_control_acc` = fraction of the 2 UNCHANGED items where arm (a) == arm (b) (both correct)
  AND `source=="LEXICAL"` (bridge never engaged).
- `scramble_acc` = arm (a) accuracy on the 9 POS_MET+NEG_UNMET items under the offset-1 scramble.

**HARD-PASS**: `zero_overlap_bridging_acc >= 0.85` (incl. mg2 item specifically correct) AND
`gap >= 0.50` AND `valence_pos_acc == 1.0` AND `valence_neg_acc == 1.0` AND
`bystander_no_bridge_acc == 1.0` AND `unchanged_control_acc == 1.0` AND `scramble_acc <= 0.15`.

**HARD-FAIL**: `zero_overlap_bridging_acc < 0.85` OR `gap < 0.25` OR `bystander_no_bridge_acc < 1.0`
(over-fires: binds wrong entity) OR `unchanged_control_acc < 1.0` (over-fires: fires on non-evaluative
/ hijacks a working lexical case) OR `valence_pos_acc < 1.0` OR `valence_neg_acc < 1.0` (wrong
valence) OR `scramble_acc > 0.15` (mechanism secretly keys off surface praise/criticism words alone,
not the goal-content link -- the exact failure mode the scramble exists to catch).

Anything strictly between the two bands (partial numeric shortfall, no over-fire) -> `MIDDLE_BAND`.

## Compute architecture
(a)/(b)/(c) classification: (b) sequential-CPU with justification -- this is a rule-based, N=13-item
hand-authored bank scored with FHRR decode over d=1024, effectively instantaneous (no matmul-heavy
sweep, no batching candidate). 3 seeds x 13 items completes in well under 1 second.

## crlb / discriminator-reachability
`crlb_n/a`: no swept capacity claim; FHRR decode of <=8 bound event-slots at d=1024 is far below any
capacity ceiling (the appraisal-sim / goal_owner_select self-tests already establish decode fidelity
> 0.99 at this scale). The discriminator here is a boolean construction-detector + registry lookup,
not a noise-limited decode.

## Cardinality / determinism
`EXPECTED_N_ITEMS=13` (6 POS_MET + 3 NEG_UNMET + 2 BYSTANDER + 2 UNCHANGED). `SEEDS=[0,1,2]`
(EXPECTED_N_SEEDS=3) -- deterministic given seed (FHRR decode margins at this scale are not
seed-sensitive; multi-seed run is a determinism/robustness check, not expected to move any verdict).
`deterministic_seeding: true` (fixed integer seeds; scramble permutation is a fixed cyclic shift, not
`hash()`-derived -- PROT-023/F.5 compliant).

## Cell-template mandates
- arms_differ_verified: bridging vs lexical-only arm outputs differ (bridging arm binds all 9
  POS_MET/NEG_UNMET items, lexical-only arm binds none) -- checked in self-test.
- final_metrics_atomicity: tmp_replace.
- except SystemExit: raise BEFORE except Exception (no BaseException).
- per-unit failure-class instrumentation: no bare except anywhere in the cell.
- cell_chunked: true (per-seed unit via tools/exp_checkpoint.py).
- HP_SCOPE: HARD-PASS/HARD-FAIL bands above apply to the aggregate (all-seeds-agree) verdict only;
  per-seed cardinality gate (META_RULE_H) is a separate, prior check.
