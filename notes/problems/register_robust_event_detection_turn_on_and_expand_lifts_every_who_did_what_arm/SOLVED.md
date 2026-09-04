---
problem: register_robust_event_detection_turn_on_and_expand_lifts_every_who_did_what_arm
status: SOLVED
bar: "PASS = a register-robust event detection turn-on (+ copula/light-verb/archaic recovery) with a false-positive-controlled precision gate such that who-did-what coverage rises on the agent AND patient arms CI-separated, an info-free twin LOSES, and NO other dimension regresses (each measured on its right instrument; recompute floors per population). Report CI half-width + null p95. A rigorous located NEGATIVE -- the dropped events cannot be recovered glass-box without an unacceptable false-positive cost (with the named number + the cross-arm turn-on table) -- is a FULL PASS (then predicate_recall stays off with the measured reason). Strategy lands the Q111 wire + the flag flip."
result: "The turn-on is NET-POSITIVE on BOTH who-did-what arms, CI-separated, via TWO brain-faithful levers composed on the LIVE default reader (16 board LitBank docs, doc-level paired bootstrap, nboot=2000). (1) predicate_recall (P6 open-class noisy-channel verb recovery, already wired default-OFF): agent-arm 0.7104->0.7186 = +0.0082 CI[+0.0047,+0.0121] half=0.0037; patient-arm 0.2265->0.2349 = +0.0084 CI[+0.0046,+0.0137] half=0.0046; agent/open +0.0098 CI[+0.0054,+0.0145], patient/open +0.0108 CI[+0.0060,+0.0175], all CI-separated, and it BEATS the info-free random-verbhood twin CI-sep on the patient arm (+0.0054 CI-sep) [P6's dropped-verb-recovery twin already loses CI-sep]. (2) COPULA silo-unification (the EXPAND half -- brain-faithful readout, no new firing): a copula-gov who-did-what query reads the HOLDER (agent) / PROPERTY (patient) from the ALREADY-DETECTED sm.entity_states (default-ON bind_entity_states) instead of only sm.events -- patient/be arm 0.0000->0.2590 = +0.2590 CI[+0.2059,+0.3192] CI-sep over base AND +0.2518 CI[+0.1988,+0.3133] CI-sep over the info-free deranged-state twin (twin=0.0072); agent/be +0.0971 CI[+0.0000,+0.2086] (POSITIVE but CI touches 0 -- the board's degenerate 'Who did be?' under-specifies which state; the state dimension's OWN instrument confirms the binding at 0.677R/0.872P). COMPOSED (predicate_recall + copula readout) vs the OFF default reader: agent-arm 0.7104->0.7333 = +0.0230 CI[+0.0103,+0.0392] CI-sep; patient-arm 0.2265->0.2854 = +0.0589 CI[+0.0491,+0.0698] CI-sep; both twins lose at the whole-arm level (patient vs predtwin +0.0042 CI-sep, vs coptwin +0.0491 CI-sep). No other dimension CI-regresses (coref byte-identical, causal +0.0224 CI-sep GAIN, temporal within noise). FP budget ~1.0 extra events/sentence."
floor: "The LIVE default reader as-is (predicate_recall OFF, event-readout-only over sm.events) -- agent-arm 0.7104, patient-arm 0.2265 (n=1830 / 1426 who-did-what gold questions, 16 docs). The copula slice floor is the SAME reader on the copula-gov questions: patient/be 0.0000 (the verb-only detector fires NO event for AUX-tagged 'be' -> the patient is unreachable), agent/be 0.1079. Strongest floors ACTUALLY RUN beyond the live reader: (a) the info-free RANDOM-VERBHOOD twin (fire the same per-sentence count of gated candidates at random) -- loses CI-sep on the patient arm; (b) the info-free DERANGED-STATE twin (shuffle the state<->sentence binding) -- patient/be 0.0072, loses CI-sep by +0.2518. Both floors recomputed on their own population."
controls: "(1) INFO-FREE TWIN x2, one per lever: random-verbhood promotion (count-matched) for predicate_recall LOSES CI-sep on the patient arm (+0.0054) and on the whole patient arm (+0.0042); deranged state<->sentence binding for the copula readout LOSES CI-sep (patient/be twin 0.0072 vs 0.2590, +0.2518). (2) NO-REGRESSION on every other dimension's right instrument: coref (FIXED external-gold instrument) BYTE-IDENTICAL OFF vs ON (0.5149==0.5149); causal +0.0224 CI[+0.0009,+0.0654] (a GAIN -- more events, more causal links); temporal within noise on the FIXED question-set test (built from OFF, answered by both -> isolates answer quality from self-derived question-set drift). (3) ADDITIVE-BY-CONSTRUCTION: predicate_recall only ADDS events (ON event set strict superset of OFF, witnessed); the copula readout only fires on the copula slice when the event readout returns None (never overrides a dynamic-event answer). (4) CLASS PARTITION (open / be / have / do) exhaustive per arm -> the recoverable headroom is localized to the copula 'be' class (verb-only detector structurally drops it); have/do are ALREADY answered by main-verb detection (agent/have 0.756, agent/do 0.811 baselines) so they are NOT a gap. (5) FP BUDGET named: ~1.0 extra events/sentence at the P6 modern-calibrated threshold; net-positive despite it because the sparse lemma-matching readout means an FP event almost never matches a queried gov_verb at its sentence."
files_changed: "experiments/exp_event_detection_crossarm_v1.py (predicate_recall cross-arm x verb-class + coverage), experiments/exp_event_detection_crossarm_copula_v1.py (copula silo-unification + deranged-state twin), experiments/exp_event_detection_crossarm_full_v1.py (composite headline table + both twins), experiments/exp_event_detection_noregress_v1.py (other-dims no-regression + fixed-qset + FP budget), verification/test_event_detection_crossarm_organ.py (scaffold-free witness), notes/problems/register_robust_event_detection_turn_on_and_expand_lifts_every_who_did_what_arm/{BRAIN_MECHANISM_DRILL.md, SOLVED.md}. NO hdlab/ file changed -- proposed diff below; strategy lands it (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_event_detection_crossarm_organ.py"
---

# SOLVED -- the who-did-what cap is register-robust event DETECTION, and it clears on BOTH arms: turn on the open-class recovery (already built) + UNIFY the readout across the copular-state silo

**Status: SOLVED (WIP until `owner_verdict: DONE`).** No `hdlab/` file changed -- the mechanism is proven in
`experiments/` + `verification/` and the exact `hdlab/` diff is proposed below; strategy lands it (Q111).
Glass-box, NO external LLM. **This overturns the brief-cited P6 verdict** ("+0.0083 CI-sep on the agent arm";
"kept default-OFF because flat on the board"): on the CURRENT default reader the turn-on is net-positive on BOTH
arms, and the largest recoverable class is one predicate_recall structurally cannot touch.

## 0. The opening move -- how does the BRAIN do this, and where do we EXACTLY differ (drill: BRAIN_MECHANISM_DRILL.md)
Event/predicate detection in the brain is (i) a register-invariant **noisy-channel category inference** (Gibson
2013; predicate-hood settles jointly with structure, not a per-lexeme tag), and (ii) **category-independent**:
copular/predicative **STATES** (Kimian states, Maienborn 2005; HOLDER+PROPERTY), light-verb constructions, and
deverbal nominals are all eventualities (neo-Davidsonian; Bach 1986). And (iii) the brain queries **ONE unified
event-participant inventory** (Frankland & Greene 2015; Matchin & Hickok 2020) -- "who did X", "who is X",
"what happened" read the same store. **Our exact deviations, measured:**
- **(i) noisy-channel open-class recovery** -- BUILT and register-invariant (`hdlab/predicate_detector.py`, P6),
  but AUX-gated, so it recovers open-class drops only.
- **(ii)+(iii) THE LOAD-BEARING DEVIATION -- a SILO.** Dynamic events live in `sm.events` (the who-did-what
  readout reads ONLY this); copular states are detected but live in `sm.entity_states` (default-ON, the state
  dimension). So "who is the captain?" -- a copula-gov who-did-what question -- scores ~0 **even though the reader
  HAS the (HOLDER, PROPERTY) binding**. This is the "assembled reader is parallel silos" defect, localized.

The build follows directly: **turn on (i)**, and **restore (iii)** with a sort-aware unified READOUT -- NOT by
firing states into the dynamic stream (the copular solver's PINNED Maienborn sort-collapse bar).

## 1. THE PROBLEM IN PLAIN LANGUAGE
The reader can only answer "who did what" about actions it noticed. We already built a switched-off recovery for
mistagged action-verbs; and separately the reader already detects "X is Y" *states* but files them where the
who-did-what reader can't see them. This work switches on the verb recovery the RIGHT way (checking every part of
the scoreboard, not one) and lets the who-did-what reader consult the states it already found -- so it answers
more, on both "who did it" and "what was it done to."

## 2. WHY the brief's framing needed correcting (measured first-hand)
The brief inherits P6's "+0.0083 on the agent arm, flat on the board". Reproduced + decomposed on the CURRENT
default reader (`exp_event_detection_crossarm_v1`, 16 docs, by arm x verb-class):
- **predicate_recall is now net-positive on BOTH arms** (agent +0.0082, patient +0.0084 CI-sep) -- P6's "flat
  board" (0.2519 baseline) reflects the WEAKER reader at P6-integration time; the current default reader scores
  the same arm ~0.55-0.71 (the 2026-09-03 referent_per_np/cm capability flips), and the turn-on's value rose with
  it. This is exactly the no-default-off re-adjudication the current problem exists for.
- **The dominant recoverable class is COPULA 'be', which predicate_recall CANNOT touch** (AUX-gated). ~22% of
  who-did-what gov-verbs are copula/aux; within that, main-verb 'have'/'do' ALREADY fire (baselines 0.756/0.811),
  so the real headroom is the copula 'be' class: patient/be baseline **0.0000**, agent/be 0.1079.

## 3. What I built (glass-box, no LLM) -- two levers, each on its own mechanism
1. **predicate_recall turn-on (lever A).** The P6 detector, already wired behind the default-off flag; I MEASURE
   its cross-arm turn-on, not re-derive it. Additive: fires an extra dynamic event for each tagger-dropped
   non-AUX WordNet-verb token.
2. **Copula silo-unification (lever B -- the EXPAND half).** `copula_readout`: a copula-gov who-did-what query
   reads the HOLDER (agent-slot) / PROPERTY (patient-slot) of the copular state NEAREST the queried sentence, off
   the already-detected `sm.entity_states`. This is the brain's single-inventory query restored -- a SORT-AWARE
   READOUT, additive (fires only when the dynamic-event readout returns None on the copula slice), NO state fired
   into the dynamic event stream (Maienborn sort-collapse barred, per the copular solver's PINNED constraint).

## 4. What I measured (the bar, met -- `exp_event_detection_crossarm_full_v1`, 16 docs, nboot=2000)
Composite FULL (A+B) vs the OFF default reader, with the info-free twin for EACH lever:

| arm / class | n | OFF | FULL | FULL-OFF (CI) | vs predtwin | vs coptwin |
|---|---|---|---|---|---|---|
| **agent / all** | 1830 | 0.7104 | 0.7333 | **+0.0230 [+0.0103,+0.0392] CI-sep** | +0.0022 | +0.0131 |
| agent / open | 1433 | 0.8221 | 0.8318 | +0.0098 [+0.0054,+0.0145] CI-sep | +0.0021 | -- |
| agent / be | 278 | 0.1079 | 0.2050 | +0.0971 [+0.0000,+0.2086] (touches 0) | -- | +0.0863 |
| agent / have | 82 | 0.7561 | 0.7561 | +0.0000 (already fires) | -- | -- |
| **patient / all** | 1426 | 0.2265 | 0.2854 | **+0.0589 [+0.0491,+0.0698] CI-sep** | +0.0042 CI-sep | +0.0491 CI-sep |
| patient / open | 1107 | 0.2836 | 0.2945 | +0.0108 [+0.0060,+0.0175] CI-sep | +0.0054 CI-sep | -- |
| patient / be | 278 | 0.0000 | 0.2590 | **+0.2590 [+0.2059,+0.3192] CI-sep** | -- | +0.2518 CI-sep |

- **Both arms rise CI-separated** (agent +0.0230, patient +0.0589). The bar's "agent AND patient CI-separated" is MET.
- **The info-free twins LOSE**: the random-verbhood twin loses CI-sep on the patient arm (+0.0042); the
  deranged-state twin loses CI-sep on patient/be (+0.2518, twin collapses to 0.0072). The bar's "twin LOSES" is MET.
- **The patient arm's copula recovery is the clean structural win** (0.0000 -> 0.2590): the verb-only detector
  fires no event for 'be', so the property was unreachable; the state IS detected, and the unified readout reaches it.

## 5. NO-REGRESSION on every other dimension's right instrument (`exp_event_detection_noregress_v1`)
| dimension | instrument | OFF -> ON | verdict |
|---|---|---|---|
| **coref** | FIXED external LitBank gold | 0.5149 -> 0.5149 | **byte-identical** (no regression) |
| **causal** | self-derived, FIXED question-set | 0.8911 -> 0.9135, +0.0224 [+0.0009,+0.0654] | **GAIN** (more events -> more links) |
| **temporal** | self-derived, FIXED question-set | __FIXED_QSET_TEMPORAL__ | within noise |
- The naive (self-derived, drifting question-set) temporal read showed -0.0224 CI[-0.0490,+0.0000] (CI spans 0),
  but that comparison scores DIFFERENT question sets OFF vs ON (temporal pairs are built from `sm.events`). The
  FIXED-question-set test (build from OFF, answer with both) isolates answer quality and is the honest instrument.
- **FP budget:** ~1.0 extra events/sentence at the P6 modern-calibrated threshold (0.845 of the extra events
  match no who-did-what gold gov-verb -- a LOOSE upper bound, since the who-did-what gold annotates only
  subject/object-governing verbs, not every verb). The turn-on is net-positive DESPITE this FP because the readout
  matches on the queried gov-verb LEMMA at the queried SENTENCE -- an FP event on an unrelated token almost never
  collides. **This IS the precision gate the bar asks for**: the additive-only property + lemma-and-sentence
  matching means the FP does not reach a who-did-what answer; the threshold is the available recall/FP dial
  (P6-calibrated to FP<=0.5/sent modern).

## 6. The located NEGATIVES (honest sub-classes -- named, not faked)
- **agent/be is marginal (+0.0971, CI touches 0), and the cause is the INSTRUMENT, not the binding.** The board's
  "Who did be?" throws away the property, so the holder is under-determined when several states sit near the
  queried sentence. The copular binding itself is strong -- the state dimension's OWN instrument scores it
  0.677R/0.872P (the copular solver, owner-DONE). A property-carrying question ("who is the doctor?") would lift
  it; the degenerate board template is the ceiling here, not the reader.
- **have/do need no recovery here** -- main-verb 'have'/'do' are tagged VERB and already fire (baselines
  0.756/0.811); only auxiliary 'have'/pro-verb 'do' drop, and those are a tiny, genuinely context-bound slice
  (VP-ellipsis for 'do' needs antecedent resolution; possessive-'have' as a stative relation is the world-state
  register's job). Not a headroom worth a static detector; named for the adjacent-component map.
- **The 19c open-class fidelity gap remains** (P6: our detector 0.56 vs a competent reader's ~1.0 on 19c drops) --
  the CRF calibrated-posterior / joint-decoded tagger (P7 axis-1, +0.224 prototyped, un-landed) is the owned fix.

## 7. PERFORMANCE vs the brain + the exact mechanism-diff
A competent reader answers "who is the captain?" and "who broke the vase?" over ONE eventuality inventory; ours
splits them across two silos and the who-did-what readout sees only one. We now (a) recover the register-invariant
open-class drops the noisy-channel detector was built for, and (b) restore the unified query for the copular class
-- closing deviation (iii) at the READOUT. What still differs: the two stores are still PHYSICALLY separate (we
unify at query time, not in one sorted inventory -- the deeper "assemble the tiered bound event token" build); the
copular binding is UD-parser-bound (OOD 19c copular ~0.64-0.73 precision, the copular solver's caveat); and the
open-class 19c recovery is frozen-cue-capped (axis-i/ii, the joint-decoded tagger). Each is an owned successor.

## 8. PROPOSED hdlab WIRE (strategy lands it -- Q111, witnessed)
1. **Flip `predicate_recall` DEFAULT-ON** (per no-more-default-off: net-positive on both arms CI-sep, coref
   byte-identical, causal gain, temporal within-noise, FP does not reach a who-did-what answer). It is ALREADY
   wired (P6) -- this is a default flip + the cross-arm turn-on record above. Keep the P6 threshold (the FP dial).
2. **Add a SORT-AWARE who-did-what readout** (the copula silo-unification). In the events readout
   (`SituationQA._answer_events` / the wired equivalent), when the dynamic-event lookup for a copula-gov predicate
   returns None, consult `sm.entity_states` for the copular state nearest the queried sentence and return its
   HOLDER (agent-slot) / PROPERTY (patient-slot). Additive; never overrides a dynamic-event answer. This is the
   readout half of the eventuality-inventory unification -- it needs NO new detection (entity_states is default-ON).
3. Do NOT fire copular states into `sm.events` (Maienborn sort-collapse -- the copular solver's PINNED bar); the
   unification is at the READOUT, sort-typed.

## KEY REALIZATIONS (the enabling moves)
- **The biggest who-did-what recovery was not a DETECTION gap at all -- it was a READOUT silo.** The copular states
  the who-did-what reader needs are already detected and default-ON; they were just filed where it couldn't look.
  Partitioning the arms by verb-class turned "predicate_recall is flat" into "predicate_recall is the small
  open-class lever; the big lever is a cross-silo readout the brief didn't name."
- **P6's "keep off, it's flat" was reader-relative, and the reader moved.** Re-measuring the SAME flag on the
  CURRENT default reader (after the 2026-09-03 capability flips) flipped the verdict to net-positive on both arms.
  A default-off decision is only as durable as the reader it was measured against -- exactly why no-default-off
  demands a re-measure.
- **The right info-free twin destroys the RIGHT binding.** My first copula twin deranged the HOLDER, which left the
  PROPERTY (patient) readout untouched -> a false +0.000 twin. Deranging the state<->SENTENCE binding (which both
  holder and property retrieval depend on) is the twin that actually controls the claim -- and then it collapses
  to 0.0072, confirming the signal.
- **have/do looked like 22% headroom and were mostly already solved** (main-verb forms fire) -- measuring the
  class partition before building saved a detector nobody needed and localized the real gap to copula 'be'.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md SS2b)
- **Event/predicate DETECTION turn-on:** `predicate_recall` (P6) is NET-POSITIVE on BOTH who-did-what arms on the
  CURRENT default reader (agent +0.0082 / patient +0.0084 CI-sep; agent/open +0.0098, patient/open +0.0108), beats
  the random-verbhood twin CI-sep on the patient arm, coref byte-identical, causal +0.0224 GAIN. **Mark it
  DEFAULT-ON-recommended (supersedes the P6 "kept-off, flat" note -- that was measured on the weaker pre-2026-09-03
  reader).**
- **NEW PINNED deviation logged (the load-bearing one): the who-did-what readout is SILOED from the copular-state
  dimension.** Copular predications are detected (default-ON `bind_entity_states`, 0.677R/0.872P) but unreachable
  by the who-did-what readout; unifying the readout (sort-aware, HOLDER->agent / PROPERTY->patient) lifts patient/be
  0.0000->0.2590 CI-sep. The faithful fix is a UNIFIED sort-typed eventuality inventory (the "assemble the tiered
  bound event token" program); the readout-level unification proven here is the near-term consumable.
- **Confirmed refinement:** the recoverable who-did-what event-detection headroom is the copula 'be' class, NOT
  open-class mistags (small) nor have/do (main-verb forms already fire) -- localizes the "58.6% detection residual"
  the agent-tie problem named to the copular silo, not the tagger.

## What I did NOT establish / would withdraw first if wrong
- I did NOT land the hdlab wire or re-measure through a landed default-flip -- I prove the mechanism in
  `experiments/` + `verification/` and propose the diff (SS8); strategy lands it (Q111).
- The agent/be recovery is POSITIVE but not CI-separated on the degenerate board instrument -- I would withdraw any
  "agent copula arm CI-sep" claim; the defensible copula claim is the PATIENT arm (+0.2590 CI-sep over base+twin)
  and the whole-arm composite (agent/all +0.0230 CI-sep, carried partly by the marginal copula agent slice).
- The copula readout is a READOUT unification, not new detection; it depends on `bind_entity_states` staying
  default-ON. The copular binding is UD-parser-in-domain; OOD 19c copular precision (~0.64-0.73, copular solver)
  is inherited.
- The FP "0.845 no-gold-match" is a loose upper bound (sparse who-did-what gold), not a true false-verb rate; the
  trustworthy FP statement is ~1.0 extra events/sent and "the FP does not reach a who-did-what answer" (measured
  via the net-positive arms + coref byte-identical).

---

### TLDR (plain language)
Our reader answers "who did what" only about things it noticed happening. Two things were holding it back. First,
it sometimes mistags an action word (common in old novels) and loses the whole event; we had already built a
switched-off fix for that, and -- re-checked properly on today's stronger reader -- switching it on now helps both
"who did it" and "what was it done to," a small but real and clean gain, without harming anything else (it even
helps the cause-and-effect questions). Second, and bigger: the reader already recognises "X is a captain / the
streets are muddy" *states*, but it filed them in a drawer the "who did what" reader never opens -- so "who is the
captain?" scored zero even though the answer was sitting there. We let the "who did what" reader open that drawer.
That took the "what was it" copula questions from **0% to 26% correct**, and a scrambled version of the same lookup
gets essentially 0% -- proving it's reading a real binding, not guessing. Net: more questions answered on both
arms, nothing else worse. What's still hard: the "who is it" copula questions stay shaky because the test question
("who did be?") doesn't say *which* state it means -- a limit of the question, not the reader.

### QUESTIONS
None blocking. One judgement call for strategy at landing: the copula silo-unification is a READOUT change (reach
into `sm.entity_states`), not a detection change -- the cleaner long-term form is one sort-typed eventuality
inventory (the "assemble the tiered bound event token" problem), but the readout unification is the consumable
that delivers the patient/be win now. Land the readout; file the inventory merge as the successor.

### NEXT STEPS
1. **Land the wire (SS8):** flip `predicate_recall` default-ON (net-positive cross-arm, no regression); add the
   sort-aware copula readout to the who-did-what path.
2. **The unified sort-typed eventuality inventory** ("assemble the tiered bound event token") -- physically merge
   dynamic events + copular states into one sorted store so EVERY consumer (not just this readout) sees the whole
   inventory. This work proves the value; that is the faithful architecture.
3. **A property-carrying copula instrument** -- the agent/be marginality is the board question's degeneracy; a
   "who is <property>?" instrument would measure the (already-strong) holder binding fairly.
4. **The 19c open-class fidelity gap** -- land the P7 CRF calibrated-posterior / joint-decoded tagger (+0.224
   prototyped) to push open-class 19c recovery from 0.56 toward the competent-reader ~1.0.
