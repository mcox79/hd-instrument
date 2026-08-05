# Pre-reg: maintained_affect_narrative_irony_probe_v1

## Question
Does adding a per-entity MAINTAINED-AFFECT trajectory (built by scanning a WIDE prior-narrative
window for entity-tagged paragraphs and scoring each with the SAME reused blind-valence lexicon)
recover the narrative-only irony items that arm_c (blind lexicon + local +-2-line tone/negation
context, `exp_grounded_appraisal_transfer_to_text_v1.py`) MISSED?

## Corrected premise (code-read, 2026-08-05)
`hdlab/situation_reader.py` SituationModel has entities/coref/events/timeline/causal_links but NO
per-entity affect/valence state. `SituationModel.read()` also requires a CoNLL-parsed mention
stream (`parse_litbank_conll`) which does not exist for raw .clean.txt novel corpora at probe
scope. Full situation_reader coref reuse is therefore NOT feasible within this probe's budget;
this probe uses a declared SIMPLIFICATION -- literal entity-name-variant string match per
paragraph (a Centering-lite backward search: same "compatible antecedent, most recent block"
principle, without the full mention-stream/gender-number machinery) -- and documents this as a
scope caveat, not silently substitutes it as "the coref reuse."

## Discriminating set (identified from data/exp_grounded_appraisal_transfer_to_text_v1/metrics.json,
commit fddde7e22, arm_c_correct field, consistent across all 5 seeds since arm_c's hypothesis is
seed-independent)
- NARRATIVE-ONLY MISSED (arm_c wrong, target): grapp_irony_002 (Oz fake-courage), grapp_irony_003
  (Tom whitewash false-cheer), grapp_irony_005 (Tom fake-deathbed)
- LOCAL-CUE items arm_c already got right: grapp_irony_001 (Jo/Amy), grapp_irony_004 (Oz/heart)
- SINCERE controls (false-positive check): grapp_sincere_001..005

## Mechanism
1. Reuse `exp_grounded_appraisal_transfer_to_text_v1.fit_arm_c_hypothesis()` (fitted once,
   deterministic, disjoint synthetic training grid) + `.resolve_valence_context()` for the
   arm_c-equivalent local prediction (surface span + its own already-used +-2-line window).
2. NEW: for each item's declared agent (AGENT_FOR_ITEM, a GIVEN speaker-identity table of the
   SAME tier as the pre-existing IRONY_AGENT_TARGET / MULTI_CAND_ORACLE_TRUE_SLOT tables in the
   parent cell -- factual WHO-is-speaking, never the valence/intent answer), scan corpus
   paragraphs in the window `[surface_start-400, surface_start-3]` (strictly BEFORE arm_c's own
   local window -- no overlap, no supporting_span line_range read at all). Any paragraph
   containing a name-variant of the agent gets scored with the REUSED (unchanged)
   `resolve_valence_blind` over the whole paragraph. Non-NA scores form the trajectory.
3. `maintained_state` = most frequent non-NA class in the trajectory (most-recent tie-break);
   NA if trajectory empty.
4. Incongruity override: if arm_c's local class != HARM and maintained_state == HARM, override to
   HARM (predict NEG). ASYMMETRIC by design -- a symmetric HELP-override branch was tried during
   smoke and found to actively damage already-correct local-cue predictions (unrelated HELP-toned
   prior paragraphs flipping grapp_irony_001/004 from correct NEG to wrong POS); removed rather
   than kept, since the pre-registered hypothesis under test is specifically "narrative-established
   negative affect exposes a false-positive-positive surface reading," not the reverse. Otherwise
   pass through arm_c's own local class unchanged.
5. Score against TRUE_LABEL = NEG for every irony item (all 5 are true-negative per gold), POS for
   every sincere item (all 5 are true-positive per gold) -- same class scheme the parent cell uses
   (cong_arm_c HURT<->NEG, HELP/NEUTRAL<->POS).

## Contamination
Never reads `true_intent_valence` / `surface_valence` / `supporting_span` fields. `AGENT_FOR_ITEM`
values are read off the surface_span's own text (e.g. "answered Oz" is literally inside
grapp_irony_002's surface_span) or well-known chapter-scene identity, never off supporting_span or
the answer fields -- declared explicitly per item in the cell's contamination log.

## Pre-registered bands (declared BEFORE running)
- PROVEN: recovers >= 2/3 of {irony_002, irony_003, irony_005} (i.e. flips arm_c's wrong pred to
  correct) AND 0 new false positives on the 5 sincere items (maintained-affect-pred must stay POS
  on all 5 sincere items).
- NULL: recovers 0 or 1 of the 3 narrative-missed items, or flips >=1 sincere item to NEG (FP).
- MIDDLE: recovers exactly 1-2 with 0 FP (partial, report per-item mechanism read regardless).
- Any miss on the narrative-only set is drilled per-item: coref-scope failure (agent name/variant
  not found within window) vs valence-reader failure (paragraph found, entity-tagged, but
  resolve_valence_blind's lexicon lacks the mood/dread words used in that passage, e.g.
  "melancholy"/"hollow"/"burden" are NOT in HARM_WORDS) vs genuinely goal-level (not
  valence-level) incongruity.

## Compute architecture
(c) sequential-CPU, justified: n=10 items, 10 corpus-paragraph scans over <=400-line windows on
4 already-cached in-memory novel texts. Wall time < 5s. No sweep axis, no seeds, no GPU benefit.

## Cell-template mandates
- arms_differ_verified: hash-compare arm_c-local-pred vector vs maintained-affect-pred vector;
  MUST differ on at least the narrative-missed set for the probe to have fired at all.
- final_metrics_atomicity: tmp_replace
- except SystemExit/KeyboardInterrupt: raise; except Exception: write crash metrics + raise (no
  bare except, no except BaseException)
- cardinality_ok: n/a (no sweep axis; fixed 10-item eval declared as EXPECTED_N_ITEMS=10)
- calibration_check: default_ok_for_this_regime (HARM_WORDS/HELP_WORDS lexicon reused verbatim,
  unchanged, from exp_situated_goal_structure_valence_v1; window=400 lines is a single fixed
  constant chosen to bound the max observed supporting-evidence distance (~131 lines) with margin,
  NOT tuned per-item to hit each item's answer location)
- progress_logging: n/a (elapsed < 30s, no timeout_s >= 1800)
- run_mode: single deterministic full pass; no smoke/full split needed (n=10, <5s)

## Downstream if PROVEN
Wire the maintained-affect-trajectory dimension into `hdlab/situation_reader.py` as an ADDITIVE
per-`TrackedEntity` field (not modifying entities/events schema), landed as a follow-up cell -- not
done in this probe per the CONTRACT's "do not modify situation_reader unless minimal + additive"
instruction; this probe stays standalone.
