# Coverage-wall decomposition: 2b ceiling + the real unlock is REFERENT-based / enablement did-it-happen (Director probes, disk-verified)

**Filed:** 2026-08-06 by Director during the full-auto #5 push, BEFORE the 2b agent returned — a
pre-VET prediction + root-cause probe of the 18 OUTCOME_NEVER_TYPED items on
experiments/data/goal_bearing_modern_eval_v1.jsonl. All read-only, disk-computed with the exact
helpers build_candidate_role_seq / congruence use. Purpose: predict 2b's ceiling to VET the agent's
number against, and pin the REAL mechanism the coverage unlock needs.

## FINDINGS (measured)
1. **2b (widen the owner-path type_goal_events + Tier-3 bridge scan across the passage) recovers only
   4/18** — predicted, disk-simulated. HARD-PASS bar was >=6, so 2b-as-window-widen lands PARTIAL
   (MIDDLE_BAND), not HARD-PASS. The 4 recoverable (gold owner correctly types): agg_anne_picnic_wish,
   ts_becky_anatomy_confession, ts_tom_sugar_theft, race_davey_wiffle. Real strict-ADD gain, bank as
   PARTIAL, NOT wasted.
2. **The other 14 are unreachable by BOTH current typing engines.** The polarity path
   (congruence_with_lexicon_fallback, which HAS the did-it-happen occurrence-gate/recurrence/windowing)
   ALSO abstains on 13/14 (types only onestop_limal_dating). So "unify the owner + polarity paths"
   would add only ~+1 — NOT the fix either.
3. **ROOT CAUSE (probed, not assumed): the goal IS recognized for 12/14** (find_desired_state fires),
   **but every desired-state has `classes: set()`** — the goal verb (get/give/make/find/see/do/have,
   OOV or light) yields NO result-class, so congruence_decision has nothing to compare the outcome
   against. AND the outcome uses a DIFFERENT verb than the goal (wish->carry, get->make, want->give),
   so the recurrence channel (same-verb) does not fire either. Neither class-comparison nor
   same-verb-recurrence has any signal. Several referents are also wrong (woz_dorothy referent='is' =
   the ECM copula bug; lw_jo referent='trying'; race_chen referent='now') — the "4 remaining
   did-it-happen items" (A3), on the critical path.

## THE REAL UNLOCK (brain-foundational): REFERENT/TARGET-STATE did-it-happen + enablement inference
The met/unmet for these 14 is recoverable RELATIONALLY (Phase 1) but needs signal types we have not
built — did-it-happen keyed on the goal's TARGET/REFERENT and its realization, not on the goal's VERB:
- **Referent-realization:** did the goal's target state get realized (possibly via a different verb)?
  (needs A3 referent fixes first — gated).
- **Enablement / granting inference:** another agent's action achieves the goal ("Silver Shoes will
  carry you [home]" grants Dorothy's wish; Oz gives the heart/brains/courage) = cross-character, borders
  on 2d.
- **Dispersed affect-reaction bridging:** the reaction is in a non-final sentence and/or on a different
  character (Mrs. Allan's "peculiar expression" -> Anne's cake spoiled).
- **Threshold-achievement:** race_chen "can now do 35" vs "needed 35" = numeric target met.
Several of these blur into a little world-knowledge (granting, cross-char reaction) but INTEGRATION is
still the binding FIRST constraint (cannot attempt without integrating). This SHARPENS Phase 1's
"29/31 integration" — the integration required is INFERENCE-heavy, not just windowing.

## REVISED INCREMENT SEQUENCE (supersedes the spec's generic 2c ordering)
- **2b (land, PARTIAL +4):** window-widen owner-path outcome typing. Real, strict-ADD, bank. (agent in
  flight.)
- **A3 (promote onto the critical path, not just cleanup):** fix referent extraction (ECM copula
  'wish IS to get', gerund/function-word referents) + the 2 goal-recognition misses (matthew/decide,
  anne_hair/mean). Referent-based did-it-happen NEEDS correct referents.
- **2c-extended (the substantive coverage unlock):** did-it-happen keyed on TARGET/REFERENT realization
  + enablement/granting + dispersed affect-reaction + threshold. This is where the 13 live. Several
  signal types are new; build each can-fail, reuse the occurrence-gate/bridge machinery, extend don't
  replace.
- **2d (cross-character links):** overlaps enablement/granting above; the relabeling-probe HARD-PASS
  (9/9 pre-validated).
- **Phase 3 grounding residual:** the small tail (spoil/flee-class) after the above.

## HONESTY
This does NOT weaken the #5-keystone thesis — it sharpens the mechanism: the coverage unlock is
referent/target-based did-it-happen + enablement inference (a richer integration), gated on the A3
referent fixes. 2b is a modest-but-real first brick. The heavy lifting is 2c-extended. Brain: this is
exactly the DMN reading the outcome off an integrated model where the goal's TARGET (not its verb) is
tracked and its realization detected — ACC expectancy-check on the goal's referent-state.
