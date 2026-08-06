# Pre-reg: DID-IT-HAPPEN occurrence-gate wired into goal-congruence (occurrence-gate + recurrence channel
+ window-widening companion + 4 mandated subtlety cases)

**Filed by:** research (FORMALIZE-drill, spec + pre-reg only — see
`notes/research_did_it_happen_occurrence_gate_congruence_wiring_2026-08-06.md` for the full design,
brain->organ map, and code-verified findings this pre-reg is derived from).
**Status:** NOT YET BUILT. This document is the can-fail contract for whoever (exp_dev) builds it.
**Target files:** `hdlab/goal_typing.py` (`find_actual_state_candidates`, `congruence_decision`, new
`congruence_outcome_valence_windowed`), `hdlab/thematic_role_labeler.py` (`_IRREGULAR_LEMMA` participle
entries, optional/small).
**Eval:** `experiments/data/goal_bearing_modern_eval_v1.jsonl` (44 items: 36 `outcome_in_lexicon=false`
OOV + 8 `outcome_in_lexicon=true` controls).
**Harness precedent:** `verification/verify_grounded_word_acquisition_increment1b.py` (imports
`congruence_with_lexicon_fallback`, `congruence_decision`, `_verb_classes` directly from
`hdlab.goal_typing`; scores via `congruence_with_lexicon_fallback(r["text"])` per item against
`r["gold_outcome_polarity"]`). Reuse this harness shape (or extend it) rather than writing a new one.

## Reference baselines (measured, disk-verified, do not re-derive)

- empty-overlay floor: 0.1667 (6/36 OOV)
- majority-class floor (all-MET): 0.6389 (23/36 OOV)
- increment1b structural-vote acquisition + live congruence organ: 16/36 = 0.4444 (met_recall 14/23,
  unmet_recall 2/13) — `verification/verify_grounded_word_acquisition_increment1b.py`, commit-confirmed.
- combined dictionary+consequence word-learning tool (a DIFFERENT, layered acquisition mechanism, NOT
  what this pre-reg is testing): dict-only 0.2222, consequence-only 0.1944, combined 0.1944 — commit
  329f01733, BACKUP doc 2026-08-06 "COMBINED DICTIONARY+CONSEQUENCE" entry.
- **THIS PRE-REG'S OWN BASELINE (must be established by cell-author, first step, before any change):**
  run `congruence_with_lexicon_fallback` unmodified (no acquisition mechanism layered on, bare organ) over
  the full 36 OOV items and record whole-eval accuracy + the 15-item did-it-happen-primary subset accuracy.
  Hand-traced spot-check this cycle (15/15 did-it-happen-primary items only, NOT the full 36): 6/15 = 0.40
  correct on that subset (2 structurally correct, 1 correct-for-right-reason-once-fixed, 3 lexicon-luck —
  see design note for per-item detail). This number is NOT yet a full-harness run; re-derive it as Step 0.

## Step 0 (MANDATORY, before any code change): reproduce the baseline

Run the harness unmodified. Record: (a) full 36-item accuracy, (b) 15-item did-it-happen-primary subset
accuracy, (c) which of the 15 are correct and via what `detail["reason"]` (distinguish `congruence_decision`
structural correctness from `lexicon_predict` fallback luck — the `detail` dict's `reason` field already
carries this: `"abstain_fallback_to_lexicon"` vs a `congruence_decision`-native reason). This step exists
because 3 of the 6 currently-correct did-it-happen items are lexicon-fallback coincidences with NO
negation-scope logic behind them (`lexicon_predict`'s Tier-2 similarity scan has no `_verb_negated_before`
call either) — the build must not silently rely on this luck holding, and Step 0's per-item reason capture
is what makes Check 2 below possible.

## Check 1 — Occurrence-gate + recurrence channel (GAP-3 core mechanism)

**Build:** `_verb_negated_before` reused verbatim on every `find_actual_state_candidates` candidate
(`negated` key added); occurrence-gate flip in `congruence_decision` (`relation = "opposed" if relation ==
"same" else "same"` when `actual["negated"]` and `relation is not None`); recurrence channel
(`RECURRENCE_MATCH` sentinel, `desired_verb_lemma` threaded into `find_actual_state_candidates`, guarded
by a closed light-verb stop-list reusing the `GOAL_ASPECT_SEED_LEMMAS` neighborhood — `be`, `do`, `have`,
`say`, `get` excluded at minimum).

- **HARD-PASS:** net new-correct >= 2 on the 15-item did-it-happen-primary subset relative to Step 0's
  baseline, AND zero regressions on Step 0's already-correct items (the 3 lexicon-luck items must either
  stay correct — ideally now via a `congruence_decision`-native reason, not the lexicon fallback — or the
  regression is reported honestly, not hidden), AND `race_chen_situps` / `onestop_carle_madeinfrance`
  (the 2 in-lexicon numeric-threshold items, both already documented HARD-FAILs for any verb/occurrence-
  only lever) remain correctly UNMET — i.e. the recurrence channel must not be fooled by their surface-
  positive verbs into flipping them to MET.
- **HARD-FAIL:** any regression on a Step-0-correct item, OR the recurrence channel produces a wrong
  MET/UNMET on ANY of the 8 `NOISE` light-verb sentences already defined in
  `verification/verify_grounded_word_acquisition_increment1b.py` (`walked`, `sat`, `spoke`, `turned`,
  `answered`, `asked`, `stood`, `carried` — reuse that exact list as the anti-drift-leak gate), OR net
  new-correct is 0 on the 15-item subset.

## Check 2 — Replace-luck-with-reasoning verification (specific, not covered by Check 1's aggregate count)

For the 3 items identified this cycle as currently-correct-via-lexicon-fallback-luck
(`agg_gilbert_pond_rescue_friendship_plea`, `agg_anne_pudding_sauce_mouse`, `race_german_dog`) and the
1 fragile-luck item (`woz_scarecrow_brains`): report, per item, whether the post-change verdict comes from
`congruence_decision` (structural, earned) or still falls through to `lexicon_predict` (luck, unearned).
**HARD-PASS-adjacent (informational, not a blocking gate):** >= 2 of these 4 flip from luck to earned.
**Flag (not a hard-fail, but must be reported):** if any of the 4 flip from correct-luck to WRONG once the
occurrence-gate is live (would mean the new negation logic is actively worse than doing nothing on that
specific construction — investigate before shipping, do not silently accept a net-positive aggregate that
hides a specific regression).

## Check 3 — The 4 mandated subtlety cases (explicit, individually reported, not folded into the aggregate)

1. `race_davey_wiffle` (EXCEPTION-SCOPE): **pre-registered to FAIL under Check 1 alone** (GAP-1-blocked,
   `sents[-1]` has no candidate at all) — passing this WITHOUT window-widening (Check 4) would be
   suspicious and must be investigated, not celebrated.
2. `agg_anne_avery_scholarship_gilbert_medal_ch36` (FALSE-NEGATIVE OVERRIDE): **pre-registered as OUT OF
   SCOPE for this pre-reg** — confirmed this cycle to be a non-cross-sentence-issue (the false negative
   sentence is safely in `goal_sentences`, never reaches `find_actual_state_candidates`); its current wrong
   answer (`AMBIGUOUS`) traces to a `lexicon_predict` ambiguity unrelated to did-it-happen. Report its
   post-change verdict for completeness but do not count a flip either way toward Check 1's pass/fail.
3. `onestop_hunt_crowdfunding` (MULTI-ATTEMPT, easy half): **pre-registered to PASS under Check 1 alone**
   (recurrence channel, `sents[-1]` literally contains `"made"`, OOV of `CLASS_REGISTRY`). If this does NOT
   flip to correct under Check 1, the recurrence channel's guard is mis-specified — investigate before
   shipping.
4. `onestop_limal_dating` (MULTI-ATTEMPT, hard half) and `race_davey_wiffle` again: **pre-registered to
   FAIL under Check 1 alone**, same as #1 — both are GAP-1-blocked.
5. `race_german_dog` (FINAL-STATE READING): **pre-registered to remain UNMET** (already correct via luck
   today; post-change it should be correct via the occurrence-gate's negation detection on `"never came
   back"` instead — a Check-2-style luck-to-earned flip, not new lift).

A naive first-negation-wins whole-sentence scanner (NOT what Check 1 builds, but the strawman the task asks
to falsify) is pre-registered to fail cases #1 and #4 even with perfect negation logic, because those two
are blocked by the SENTENCE-WINDOW gap, not a negation-scope-parsing gap — this distinction is the single
most important falsifiable claim in this pre-reg and must be reported explicitly, not folded into an
aggregate accuracy number.

## Check 4 — Window-widening companion (GAP-1, separate build, separate gate — build AFTER Check 1 lands)

**Build:** `congruence_outcome_valence_windowed` (candidate-nonempty backward scan, `max_window=4`,
byte-identical fallback to today's behavior whenever `sents[-1]` already has a candidate).

- **HARD-PASS:** recovers >= 3 of the 5 GAP-1-identified items (`lw_laurie_flower_table_amy`,
  `agg_anne_mrs_barry_forgiveness`, `woz_dorothy_kansas_wish`, `race_davey_wiffle`, `onestop_limal_dating`)
  when combined with Check 1's occurrence-gate, AND zero regressions across the **FULL 44-item eval**
  (all 8 in-lexicon controls included — window-widening changes outcome-sentence selection for every item,
  not just the 36 OOV, so the non-regression sweep must be eval-wide, not subset-restricted).
- **HARD-FAIL:** any item correct under `sents[-1]`-only selection becomes wrong once backward-stepping is
  enabled (an earlier, coincidentally-class-related clause outcompeting the true final clause — the named
  risk in the design note), OR fewer than 2 of the 5 targeted items are recovered, OR `max_window=4` proves
  insufficient for any targeted item (report the actual sentence-index distance needed per item; if any
  item needs `k>4`, that is a finding to report, not silently absorbed by raising the constant).

## Check 5 — Non-circularity / eval-passage exclusion

Per the standing discipline already applied to the sibling `consequence_learning_loop` pre-reg this same
day: if any part of this build's development/debugging touches `little_women`, `anne_of_green_gables`,
`tom_sawyer`, `wizard_of_oz`, or `alice_in_wonderland` corpus text directly (e.g. hand-tuning the recurrence
stop-list against observed failures), verify via `line_citation` spans that no eval item's exact passage
was used as a tuning example. 34/44 eval items are drawn from these same corpora (verified same day) — this
is a real leakage risk for a hand-guarded stop-list, not a hypothetical.

## Deflated P (per lit-scan calibration discipline, [[feedback-lit-scan-calibration-penalty]])

- Check 1 (occurrence-gate + recurrence): P_deflated = 0.35 (mechanism is code-verified correct in shape;
  deflated because the full-36 eval-wide number is not yet measured, only a 15-item hand-trace).
- Check 4 (window-widening): P_deflated = 0.25 (real, named, unruled-out regression risk).
- Check 3 items #1/#4 (exception-scope, hard multi-attempt): P_deflated = 0.20 standalone under Check 1
  (pre-registered to need Check 4 as a hard prerequisite — do not expect a surprise pass).
- Owner-attribution companion (design-level only, not gated by this pre-reg): no P assigned here — deferred
  to its own future FORMALIZE pass once Checks 1 and 4 are measured standalone, per the design note's
  Honest Scope (three levers are not simply additive; must isolate marginal lift per lever, not assume).

## Non-goals (explicit, to prevent scope creep at build time)

- Does NOT build GAP-2 (find_desired_state first-match-wins fix) — flagged in the design note as a
  separate, symmetric, cheap follow-up, not in this pre-reg's build scope.
- Does NOT build GAP-4 (past-participle lemma table entries) as a blocking prerequisite — note it if it
  affects any Check-1/Check-4 item's outcome, but do not treat its absence as a Check failure unless a
  specific targeted item requires it (currently: none of the 15 do, since `woz_scarecrow_brains` is
  GAP-1-blocked regardless).
- Does NOT build owner-attribution (a) or (b) — design-level only per the task's explicit lighter-detail
  ask for that companion.
