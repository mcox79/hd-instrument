# exp_dev hand-off — research: did-it-happen occurrence-gate wired into goal-congruence

**Filed-by:** research (FORMALIZE-drill: code-level spec + pre-reg, read `hdlab/goal_typing.py` end to
end this cycle, no build/run performed), 2026-08-06.
**Trigger:** `notes/research_did_it_happen_occurrence_gate_congruence_wiring_2026-08-06.md` — full design,
brain->organ map, code-verified findings (including 2 previously-undocumented architectural gaps found by
reading the code, not assumed) live there. This file is the pointer-only hand-off; do not re-derive the
reasoning here, read the cited note. Supersedes/sharpens
`notes/exp_dev_handoff_research_goal_bearing_eval_driver_decomposition_2026-08-06.md` anchor 1 — that
hand-off pointed at "wire did-it-happen into the congruence organ" at the strategy level; this hand-off is
the concrete code-level design for exactly that wiring, produced by actually reading the consumer function.
**Pause state:** `data/orchestrator_paused.flag` absent at filing time (NOT PAUSED) — re-check at pickup
time before shipping anything to remote/GPU queues.

Per [[feedback-no-experiment-design-in-prompts]]: no inline pre-reg, thresholds, or cell code below beyond
what is already pre-registered in `preregs/2026-08-06_did_it_happen_occurrence_gate_v1.md` — the cell-
author owns translating the design into runnable code, smoke gate, and dispatch.

## Why this hand-off exists

The cited research note designs the exact wiring point (`find_actual_state_candidates` gains a `negated`
flag via reusing `_verb_negated_before` verbatim; `congruence_decision` gains a 3-line occurrence-gate flip
on `_class_relation`'s output; a new `RECURRENCE_MATCH` sentinel lets class-registry-OOV verbs become
candidates when lemma-identical to the desired verb) and pre-registers can-fail bands for it. It ALSO found,
by disk-running the harness against all 15 did-it-happen-primary eval items (not just reading the eval
text), that a fixed single-last-sentence outcome window (`congruence_outcome_valence`'s `sents[-1]`) blocks
5-6 of those 15 items independent of negation logic — a previously-undocumented gap of comparable size to
the core mechanism, double-blocking 2 of the task's 4 mandated subtlety cases. This materially narrows the
realistic reachable of the core mechanism alone (2-4/15 new, not the 8/36 estimated in the prior driver-
decomposition note) and makes window-widening a REQUIRED companion, not an optional polish.

## Anchor candidates (rank-ordered)

1. **[Primary, build first, cheapest, most concrete] Occurrence-gate + goal-verb-recurrence channel
   (Check 1 in the pre-reg).**
   - Anchor pointer: research note "Design — the occurrence-gate (core, GAP-3)" section + pre-reg Check 1.
   - Substrate-product reading: a 2-part strict-ADD to `find_actual_state_candidates`/`congruence_decision`
     — reuses `_verb_negated_before` (already built, commit c2f88ea91) verbatim on the outcome side, where
     it has never been called; adds one new one-element sentinel (`RECURRENCE_MATCH`) structurally
     identical in kind to the existing `ACQUIRED_REALIZED`/`ACQUIRED_BLOCKED` Tier-3 pattern. No new
     parsing, no new taxonomy.
   - Tier hint: low novel-synthesis risk on the MECHANISM (both reused pieces are proven); the risk is in
     the recurrence channel's light-verb guard (must reuse the 8-item `NOISE` list already in
     `verify_grounded_word_acquisition_increment1b.py` as the anti-drift-leak gate — that exact failure
     class was caught once already this same day on a different mechanism).
   - Why now: this is the correctly-scoped, concrete implementation of the strategy-level anchor already
     handed off; ready to build directly from the pre-reg's exact code sketch.
   - HARD-PASS / HARD-FAIL bars: pre-registered in `preregs/2026-08-06_did_it_happen_occurrence_gate_v1.md`
     Check 1 + Check 2 (luck-to-reasoning verification) + Check 3 (the 4 mandated subtlety cases,
     individually reported, 2 pre-registered to still fail here and require anchor 2).

2. **[Secondary, comparable size, REQUIRED companion not optional] Outcome-window widening
   (Check 4 in the pre-reg).**
   - Anchor pointer: research note "Design — outcome-window widening (companion, GAP-1...)" + pre-reg
     Check 4.
   - Substrate-product reading: `congruence_outcome_valence_windowed` — a candidate-nonempty backward scan
     over the last `max_window=4` sentences, byte-identical fallback to today's behavior whenever
     `sents[-1]` already yields a candidate (so it cannot regress the common case by construction). Fixes
     the newly-found gap that blocks `race_davey_wiffle` and `onestop_limal_dating` (2 of the task's 4
     mandated subtlety cases) regardless of how good anchor 1's negation logic is.
   - Tier hint: named, unruled-out regression risk (an earlier, coincidentally-class-related clause could
     outcompete the true final one) — pre-reg Check 4 requires a FULL 44-item non-regression sweep (not
     just the 36 OOV subset), because this changes outcome-sentence selection for every item including the
     8 in-lexicon controls.
   - Why now: sequenced immediately after anchor 1 (not deferred) because it is comparably sized and 2 of
     the 4 mandated subtlety cases cannot pass without it — building anchor 1 alone and calling the
     did-it-happen work "done" would be an honest-scope violation per the research note.

3. **[Tertiary, design-level only, do not build yet] Owner-attribution companion, deep integration option.**
   - Anchor pointer: research note "Owner-attribution companion (7/15 need it...)" section, option (b).
   - Substrate-product reading: reuse `hdlab/goal_owner_select.py`'s `select_outcome_owner` /
     `directed_goal_outcome_score` (the purpose-built directed, non-symmetric coherence-score organ) as a
     Tier-4 referent-link check inside `congruence_decision`, rather than a shallower coref-chain hack —
     the brain-faithful answer per
     [[feedback_for_every_mechanism_ask_which_brain_structure_and_does_it_share_existing_processes_USER_2026-08-03]].
   - Tier hint: requires threading a `roster` argument through 3 functions (`congruence_decision`,
     `find_actual_state_candidates`, the top-level entry point) — a real signature change, not a pure
     strict-ADD. NOT scoped for this cycle's build.
   - Why now: not yet — explicitly deferred until anchors 1-2 are built and measured STANDALONE, so the
     owner-attribution companion's own marginal lift can be isolated (the 3 levers have real overlap — 3 of
     the window-gap items also need owner-attribution — and are not simply additive; measuring them
     compounded would confound which lever did what).

## Context pointers (file paths, not summaries — read these, don't re-derive)

- `notes/research_did_it_happen_occurrence_gate_congruence_wiring_2026-08-06.md` — full design, exact code
  sketches for both anchors, the empirical 15-item table (which items are already correct today and why,
  distinguishing structural correctness from lexicon-fallback luck), brain->organ citations.
- `preregs/2026-08-06_did_it_happen_occurrence_gate_v1.md` — formal can-fail bands, Step 0 baseline
  reproduction requirement, Check 1-5 (occurrence-gate, luck-verification, 4-subtlety-cases individually,
  window-widening, non-circularity/eval-passage-exclusion).
- `hdlab/goal_typing.py` — target file. Read `find_actual_state_candidates` (line ~853),
  `congruence_decision` (line ~878), `congruence_outcome_valence` (line ~935), `_verb_negated_before`
  (line ~390, reuse verbatim), the Tier-3 `ACQUIRED_POLE_SENTINEL` pattern (line ~601, structural precedent
  for the new `RECURRENCE_MATCH` sentinel) before writing any code.
- `hdlab/thematic_role_labeler.py::lemma_verb`/`_IRREGULAR_LEMMA` (line ~160) — has no past-participle rule
  (GAP-4, non-blocking for this cycle's targeted items, but will matter once window-widening surfaces more
  participle-form recurrence candidates).
- `verification/verify_grounded_word_acquisition_increment1b.py` — the existing harness shape to reuse/
  extend (imports `congruence_with_lexicon_fallback`/`congruence_decision` directly), and the source of the
  8-item `NOISE` light-verb anti-drift-leak gate list to reuse verbatim in Check 1's guard.
- `experiments/data/goal_bearing_modern_eval_v1.jsonl` — the eval (44 items).

## Contract section

- Cell-author owns: exact code diff, exact light-verb stop-list composition (reuse the `NOISE` list first,
  extend only if a specific false-positive is observed and reported), smoke gate, dispatch, Step 0 baseline
  reproduction (MANDATORY first action per the pre-reg — do not skip).
- Must report per-item pass/fail against the SAME 15-item did-it-happen-primary subset AND the 4 mandated
  subtlety cases individually (id-for-id, per pre-reg Check 3), not an aggregate accuracy number alone.
- Must run Check 2 (luck-to-reasoning verification) on the 4 specifically-named currently-correct-via-luck
  items — a silent luck-to-wrong flip inside a net-positive aggregate must be surfaced, not hidden.
- Must NOT build anchor 3 (owner-attribution) in this cycle — explicitly deferred per the pre-reg's
  Non-goals section.
- Must run Check 5 (non-circularity) if development touches the 5 source novels directly.
- HARD-PASS/HARD-FAIL bars are pre-registered in `preregs/2026-08-06_did_it_happen_occurrence_gate_v1.md`
  — do not loosen without flagging the deviation explicitly in the shipped pre-reg.

## Autonomy declaration

Research does not prescribe the exact light-verb stop-list beyond "reuse the existing 8-item `NOISE` list
first," the exact `max_window` tuning beyond the pre-registered default of 4 (report if any target item
needs more), or exact code layout within `goal_typing.py`. Cell-author has full autonomy over
implementation detail, subject to the falsifiable predictions and HARD-PASS/HARD-FAIL bars pre-registered
in `preregs/2026-08-06_did_it_happen_occurrence_gate_v1.md`, and subject to the "wire, don't island"
constraint (both anchors are signal-additions/window-widenings of the existing congruence organ, not new
parallel mechanisms).
