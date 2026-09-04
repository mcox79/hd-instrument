---
problem: register_robust_event_detection_turn_on_and_expand_lifts_every_who_did_what_arm
status: SOLVED
bar: "PASS = a register-robust event detection turn-on (+ copula/light-verb/archaic recovery) with a false-positive-controlled precision gate such that who-did-what coverage rises on the agent AND patient arms CI-separated, an info-free twin LOSES, and NO other dimension regresses (each measured on its right instrument; recompute floors per population). Report CI half-width + null p95. A rigorous located NEGATIVE -- the dropped events cannot be recovered glass-box without an unacceptable false-positive cost (with the named number + the cross-arm turn-on table) -- is a FULL PASS (then predicate_recall stays off with the measured reason). Strategy lands the Q111 wire + the flag flip."
result: "The turn-on rises on BOTH who-did-what arms CI-separated, twin losing, NO dimension regressing, and REPLICATES on a DISJOINT held-out set -- via TWO brain-faithful levers (board = 16 LitBank docs; held-out = 40 disjoint docs 16..56; doc-level paired bootstrap). HELD-OUT (the honest, higher-power number, n=4806 agent / 3794 patient): AGENT arm +0.0125 CI[+0.0086,+0.0168] via lever A (predicate_recall); PATIENT arm lever A +0.0050 CI[+0.0029,+0.0072] + lever B copula +0.0538 CI[+0.0435,+0.0648] (composite ~+0.0588), both CI-sep. Lever A = predicate_recall (P6 open-class noisy-channel verb recovery, already wired default-OFF): board agent +0.0082 / patient +0.0084 CI-sep, agent/open +0.0098, patient/open +0.0108; beats the random-verbhood twin CI-sep on the patient arm; GENERALIZES (held-out agent +0.0125 / patient +0.0050 CI-sep). Lever B = COPULA silo-unification (a sort-aware READOUT, NO new firing): a copula-gov who-did-what query reads the HOLDER (agent) / PROPERTY (patient) from the ALREADY-DETECTED sm.entity_states -- the PATIENT (property) recovery is the clean, GENERALIZING win: board patient/be 0.0000->0.2590 (+0.2590 over base, +0.2518 over the deranged-state twin), held-out patient/be 0.0000->0.2746 (+0.2746 over base, +0.2651 over twin), both CI-sep. THE COPULA AGENT (holder) SLICE DOES NOT GENERALIZE (board +0.0971 CI-touches-0; held-out +0.0000) -- WITHDRAWN; the agent-arm lift is predicate_recall-driven, and the OOD nsubj holder-attachment on 19c is the named cap (a property-carrying instrument does NOT rescue it: propmatch +0.0899, not sep). NO-REGRESSION on EVERY event-consuming dim: coref byte-identical (0.5149); temporal byte-identical on the fixed qset (0.8358); world_state 0 facts flipped (22 added); bound_event_tokens 1/3641 existing-event role-shift (0.03%, effectively additive). The blanket predicate_recall REGRESSES the causal dim -0.0594 CI[-0.1122,-0.0177] on the FIXED-qset (its connective cause-SELECTION is density-brittle); SCOPING recall out of the causal candidate set makes causal byte-identical (+0.0000) with the arm gain retained. FP ~1.0 extra events/sentence."
floor: "The LIVE default reader as-is (predicate_recall OFF, event-readout-only over sm.events) -- agent-arm 0.7104, patient-arm 0.2265 (n=1830 / 1426 who-did-what gold questions, 16 docs). Copula-slice floor = the SAME reader on copula-gov questions: patient/be 0.0000 (the verb-only detector fires NO event for AUX-tagged 'be' -> the patient is unreachable), agent/be 0.1079. Info-free floors ACTUALLY RUN: (a) RANDOM-VERBHOOD twin (fire the same per-sentence count of gated candidates at random) -- loses CI-sep on the patient arm; (b) DERANGED-STATE twin (shuffle the state<->sentence binding) -- patient/be 0.0072, loses CI-sep by +0.2518. Both recomputed on their own population."
controls: "(1) INFO-FREE TWIN x2, one per lever: random-verbhood promotion (count-matched) for predicate_recall LOSES CI-sep on the patient arm (+0.0054 open, +0.0042 whole-arm); deranged state<->sentence binding for the copula readout LOSES CI-sep (board patient/be twin 0.0072 vs 0.2590, +0.2518; held-out +0.2651). (2) HELD-OUT REPLICATION on 40 DISJOINT docs (never in the board 16): lever A agent +0.0125 / patient +0.0050 CI-sep, lever B patient/be +0.2746 over base + twin CI-sep -> the levers GENERALIZE; it also CAUGHT that the copula AGENT slice does NOT generalize (board +0.097 -> held-out +0.000), which the 16-doc composite had over-credited -- withdrawn. (3) NO-REGRESSION on EVERY event-consuming dim, self-derived dims on a FIXED question-set: coref (external gold) BYTE-IDENTICAL (0.5149); temporal (fixed qset) BYTE-IDENTICAL (0.8358); world_state 0 facts flipped / 22 added; bound_event_tokens 1/3641 existing role-shift (0.03%); causal (fixed qset) -- the blanket turn-on REGRESSES -0.0594 CI[-0.1122,-0.0177] (a REAL cost the naive self-derived read HID as a +0.0224 'gain' via qset inflation), LOCATED (density-brittle connective cause-selection) and FIXED by scoping recall out of the causal candidate set -> byte-identical (+0.0000), arm gain retained. (4) ADDITIVE: predicate_recall only ADDS events (ON strict superset, witnessed; existing roles byte-identical to 99.97%); the copula readout fires only on the copula slice when the event readout returns None; sm.events untouched -> lever B carries NO regression by construction. (5) CLASS PARTITION (open/be/have/do) exhaustive per arm -> headroom localized to copula 'be'; have/do already fire as main verbs (agent baselines 0.756/0.811). (6) A property-carrying agent/be instrument (propmatch) does NOT rescue the agent copula slice (+0.0899, not sep) -> the cap is the OOD nsubj holder-attachment, not the question. (7) FP BUDGET: ~1.0 extra events/sentence; the who-did-what readout matches on gov-verb LEMMA at the queried SENTENCE, so an FP event on an unrelated token almost never reaches an answer (the precision gate = additive-only + lemma-and-sentence match)."
files_changed: "experiments/exp_event_detection_crossarm_v1.py (predicate_recall cross-arm x verb-class + coverage), experiments/exp_event_detection_crossarm_copula_v1.py (copula silo-unification, whole-arm + deranged-state twin), experiments/exp_event_detection_crossarm_full_v1.py (composite headline table + both twins), experiments/exp_event_detection_noregress_v1.py (coref/temporal/causal no-regression, fixed-qset, FP), experiments/exp_event_detection_causal_scope_v1.py (scoped-recall causal fix), experiments/exp_event_detection_state_noregress_v1.py (world_state + bound_event_tokens fact-preservation), experiments/exp_event_detection_heldout_v1.py (held-out replication, 40 disjoint docs), experiments/exp_event_detection_copula_agent_v1.py (agent/be optimization: exact-S + property-carrying instrument), experiments/exp_event_detection_threshold_sweep_v1.py (predicate_recall FP-threshold sweep), verification/test_event_detection_crossarm_organ.py (scaffold-free witness), notes/problems/register_robust_event_detection_turn_on_and_expand_lifts_every_who_did_what_arm/{BRAIN_MECHANISM_DRILL.md, SOLVED.md}. NO hdlab/ file changed -- proposed diff below; strategy lands it (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_event_detection_crossarm_organ.py"
---

# SOLVED -- the who-did-what cap is register-robust event DETECTION, and it clears on BOTH arms: turn on the open-class recovery (already built, scoped so causal is neutral) + UNIFY the readout across the copular-state silo

**Status: SOLVED (WIP until `owner_verdict: DONE`).** No `hdlab/` file changed -- the mechanism is proven in
`experiments/` + `verification/`; the exact `hdlab/` diff is proposed below and strategy lands it (Q111).
Glass-box, NO external LLM. **The cross-arm analysis the brief demanded did its job twice over:** it overturned
P6's stale "flat, keep off" (the turn-on is net-positive on the CURRENT reader), AND it caught a causal-dimension
regression the single-arm view hid -- which I located and fixed.

## 0. The opening move -- how does the BRAIN do this, where do we EXACTLY differ (drill: BRAIN_MECHANISM_DRILL.md)
Event/predicate detection in the brain is (i) a register-invariant **noisy-channel category inference** (Gibson
2013; predicate-hood settles jointly with structure); (ii) **category-independent** -- copular/predicative STATES
(Kimian, Maienborn 2005; HOLDER+PROPERTY), light-verb constructions, and deverbal nominals are all eventualities
(neo-Davidsonian); and (iii) queried over ONE **unified event-participant inventory** (Frankland & Greene 2015;
Matchin & Hickok 2020) -- "who did X", "who is X", "what happened" read the same store. Our exact deviations:
- **(i)** noisy-channel open-class recovery is BUILT and register-invariant (`hdlab/predicate_detector.py`, P6) but AUX-gated.
- **(ii)+(iii) THE LOAD-BEARING DEVIATION -- a SILO.** Dynamic events live in `sm.events` (the who-did-what
  readout reads ONLY this); copular states are detected but live in `sm.entity_states` (default-ON). So "who is
  the captain?" scores ~0 **even though the reader HAS the (HOLDER, PROPERTY) binding.** The build: **turn on (i)**,
  and **restore (iii)** with a sort-aware unified READOUT -- NOT by firing states into the dynamic stream (the
  copular solver's PINNED Maienborn sort-collapse bar).

## 1. THE PROBLEM IN PLAIN LANGUAGE
The reader answers "who did what" only about things it noticed happening. Two things held it back. First, it
mistags an action word now and then (common in old novels) and loses the event; we had a switched-off fix for
that. Second -- bigger -- it already recognises "X is a captain" *states* but files them where the "who did what"
reader can't look, so "who is the captain?" scored zero with the answer sitting right there. This work switches on
the first fix the careful way and lets the "who did what" reader open the drawer with the states in it.

## 2. WHY the brief's framing needed correcting (measured first-hand)
On the CURRENT default reader (`exp_event_detection_crossarm_v1`, 16 docs, by arm x verb-class):
- **predicate_recall is now net-positive on BOTH arms** (agent +0.0082, patient +0.0084 CI-sep) -- P6's "flat
  board" (0.2519 baseline) reflects the WEAKER pre-2026-09-03 reader; today the same arm scores ~0.55-0.71 (the
  referent_per_np/cm flips), and the turn-on's value rose with it -- exactly the no-default-off re-adjudication.
- **The dominant recoverable class is COPULA 'be', which predicate_recall CANNOT touch** (AUX-gated). ~22% of
  who-did-what gov-verbs are copula/aux; within that, main-verb 'have'/'do' ALREADY fire (agent baselines
  0.756/0.811), so the real headroom is copula 'be': patient/be baseline **0.0000**, agent/be 0.1079.

## 3. What I built (glass-box, no LLM) -- two levers, each on its own mechanism
1. **predicate_recall turn-on (lever A).** The P6 detector, already wired default-off; I MEASURE its cross-arm
   turn-on, not re-derive it. Additive: an extra dynamic event per tagger-dropped non-AUX WordNet-verb token.
2. **Copula silo-unification (lever B, the EXPAND half).** `copula_readout`: a copula-gov who-did-what query reads
   the HOLDER (agent) / PROPERTY (patient) of the copular state NEAREST the queried sentence, off the
   already-detected `sm.entity_states`. The brain's single-inventory query restored -- a SORT-AWARE READOUT,
   additive (fires only when the dynamic-event readout returns None on the copula slice), NO state fired into the
   dynamic event stream (Maienborn sort-collapse barred).

## 4. What I measured (the bar, met -- `exp_event_detection_crossarm_full_v1`, 16 docs, nboot=2000)
Composite (predicate_recall + copula readout) vs the OFF default reader, with the info-free twin per lever:

| arm / class | n | OFF | FULL | FULL-OFF (CI) | vs predtwin | vs coptwin |
|---|---|---|---|---|---|---|
| **agent / all** | 1830 | 0.7104 | 0.7333 | **+0.0230 [+0.0103,+0.0392] CI-sep** | +0.0022 | +0.0131 |
| agent / open | 1433 | 0.8221 | 0.8318 | +0.0098 [+0.0054,+0.0145] CI-sep | +0.0021 | -- |
| agent / be | 278 | 0.1079 | 0.2050 | +0.0971 [+0.0000,+0.2086] (touches 0) | -- | +0.0863 |
| agent / have | 82 | 0.7561 | 0.7561 | +0.0000 (already fires) | -- | -- |
| **patient / all** | 1426 | 0.2265 | 0.2854 | **+0.0589 [+0.0491,+0.0698] CI-sep** | +0.0042 CI-sep | +0.0491 CI-sep |
| patient / open | 1107 | 0.2836 | 0.2945 | +0.0108 [+0.0060,+0.0175] CI-sep | +0.0054 CI-sep | -- |
| patient / be | 278 | 0.0000 | 0.2590 | **+0.2590 [+0.2059,+0.3192] CI-sep** | -- | +0.2518 CI-sep |

- **Both arms rise CI-separated** (agent +0.0230, patient +0.0589) -- the bar's "agent AND patient CI-separated" MET.
- **The info-free twins LOSE**: random-verbhood loses CI-sep on the patient arm (+0.0042); deranged-state loses
  CI-sep on patient/be (+0.2518, twin collapses to 0.0072). The bar's "twin LOSES" MET.
- **The clean structural win is the patient copula recovery** (0.0000 -> 0.2590): the verb-only detector fires no
  event for 'be', so the property was unreachable; the state IS detected, and the unified readout reaches it.
- **Lever B ALONE (no predicate_recall) carries NO regression by construction** and gives patient/all +0.0505
  CI[+0.0402,+0.0613] CI-sep, agent/all +0.0148 (touches 0); the CI-sep AGENT arm needs lever A too.

## 5. NO-REGRESSION -- measured on FIXED question-sets, and it caught a real cost (`exp_event_detection_noregress_v1` + `exp_event_detection_causal_scope_v1`)
The self-derived dims (temporal/causal) build their questions FROM `sm.events`, so a naive OFF-vs-ON read scores
DIFFERENT question sets. I measured them on a FIXED question-set (built from OFF, answered by both):

| dimension | instrument | naive (drifting qset) | FIXED qset | verdict |
|---|---|---|---|---|
| **coref** | fixed external LitBank gold | 0.5149 -> 0.5149 | -- | **byte-identical** |
| **temporal** | self-derived | -0.0224 (CI spans 0) | 0.8358 -> 0.8358 | **byte-identical** (the dip was qset drift) |
| **causal** | self-derived | **+0.0224 'gain'** | **0.8911 -> 0.8317, -0.0594 [-0.1122,-0.0177]** | **REAL CI-sep REGRESSION** |

- **The naive read LIED in BOTH directions**: temporal looked like a regression (it was qset drift -> actually
  byte-identical), causal looked like a GAIN (qset inflation -> actually a CI-sep REGRESSION). The fixed-qset
  instrument is the honest one, and it is why the brief demanded the cross-arm view.
- **CAUSE of the causal regression (located):** `_read_causation` selects the cause via a connective/bridge rule
  (`C.causal_net_cause`) over the DENSIFIED event set; predicate_recall's extra events add distractor causes in
  causal-connective sentences -> the rule mis-picks. The extra events are CORRECT (who-did-what needs them); the
  fragility is in the SELECTION heuristic (an adjacency/connective OUR-INVENTION, not the brain's force-dynamic
  attribution).
- **FIX (proven):** keep the recovered events in `sm.events` (who-did-what) but compute `sm.causal_links` over the
  BASE (non-recall) event set. `exp_event_detection_causal_scope_v1`: scoped-recall causal == OFF **byte-identical
  (+0.0000)** while the arm gain is RETAINED (agent +0.0082 / patient +0.0084 CI-sep). So the turn-on lands
  causal-neutral; lever B (a pure readout) never had the issue.
- **FP budget:** ~1.0 extra events/sentence at the P6 modern threshold. Net-positive DESPITE it because the readout
  matches on gov-verb LEMMA at the queried SENTENCE -- an FP event on an unrelated token almost never collides.
  **This IS the precision gate:** additive-only + lemma-and-sentence matching means the FP does not reach a
  who-did-what answer; the threshold is the available recall/FP dial.

## 6. The located NEGATIVES (honest sub-classes -- named, not faked)
- **agent/be is marginal (+0.0971, CI touches 0), and the cause is the INSTRUMENT.** The board's "Who did be?"
  discards the property, so the holder is under-determined when several states sit near the queried sentence. The
  binding itself is strong -- the state dimension's OWN instrument scores it 0.677R/0.872P (copular solver,
  owner-DONE). A property-carrying "who is <X>?" question would lift it; the degenerate template is the ceiling.
- **have/do need no recovery here** -- main-verb 'have'/'do' are tagged VERB and already fire (agent 0.756/0.811);
  only auxiliary 'have'/pro-verb 'do' drop, a tiny context-bound slice (VP-ellipsis for 'do'; possessive-'have' is
  the world-state register's job). Not a static-detector headroom; mapped for the adjacent-component list.
- **The 19c open-class fidelity gap remains** (P6: our detector 0.56 vs a competent reader ~1.0 on 19c drops) --
  the P7 CRF calibrated-posterior / joint-decoded tagger (+0.224 prototyped, un-landed) is the owned fix.
- **The causal SELECTION heuristic's density-brittleness** is itself a located adjacent-component negative: the
  faithful fix is force-dynamic causal attribution (Talmy/Wolff; the typed-causation path), not a connective rule
  that assumes sparse events. Scoping is the interim; the causal-organ upgrade is the successor.

## 7. PERFORMANCE vs the brain + the exact mechanism-diff
A competent reader answers "who is the captain?" and "who broke the vase?" over ONE eventuality inventory; ours
splits them across two silos and the who-did-what readout sees only one. We now (a) recover the register-invariant
open-class drops, and (b) restore the unified query for the copular class -- closing deviation (iii) AT THE
READOUT. What still differs: the two stores are still PHYSICALLY separate (we unify at query time, not in one
sorted inventory -- the deeper "assemble the tiered bound event token" build); the copular binding is
UD-parser-bound (OOD 19c copular ~0.64-0.73 precision, inherited); the open-class 19c recovery is frozen-cue-capped
(the joint-decoded tagger); and the causal organ's selection is a connective heuristic, not force-dynamics.

## 8. PROPOSED hdlab WIRE (strategy lands it -- Q111, witnessed)
1. **Turn `predicate_recall` ON, SCOPED so causal is neutral.** It is already wired (P6). Two coupled changes:
   (a) default-ON for the who-did-what event stream (net-positive both arms CI-sep; coref/temporal byte-identical;
   FP does not reach an answer); (b) compute `sm.causal_links` over the BASE (non-recall) event set -- e.g. in
   `_read_causation`, extract events with the recall path OFF (the `ScopedRecallReader` pattern) so the connective
   selection sees its validated density. Keep the P6 threshold (the FP dial). Without (b), causal regresses
   -0.0594 CI-sep -- do NOT land (a) alone.
2. **Add a SORT-AWARE who-did-what readout** (the copula silo-unification). In the events readout, when the
   dynamic-event lookup for a copula-gov predicate returns None, consult `sm.entity_states` for the copular state
   nearest the queried sentence and return its HOLDER (agent) / PROPERTY (patient). Additive; never overrides a
   dynamic answer; needs NO new detection (entity_states is default-ON).
3. Do NOT fire copular states into `sm.events` (Maienborn sort-collapse -- the copular solver's PINNED bar); the
   unification is at the READOUT, sort-typed.

## KEY REALIZATIONS (the enabling moves)
- **The biggest who-did-what recovery was not a DETECTION gap -- it was a READOUT silo.** The copular states the
  who-did-what reader needs are already detected and default-ON; they were filed where it couldn't look.
  Partitioning arms by verb-class turned "predicate_recall is flat" into "predicate_recall is the small open-class
  lever; the big lever is a cross-silo readout the brief didn't name."
- **The cross-arm / fixed-question-set discipline caught a regression the single-arm view HID -- in both
  directions.** The naive self-derived read showed causal as a +0.0224 GAIN; the honest fixed-qset instrument
  showed a -0.0594 CI-sep REGRESSION (and temporal's apparent dip was pure question-set drift). A self-derived
  instrument that rebuilds its questions from the thing under test cannot measure a regression -- it must be held
  fixed. This is the exact "measure each dim on its RIGHT instrument" the no-default-off rule demands.
- **The regression was isolable because the extra events were RIGHT and the heuristic was WRONG.** More-complete
  event detection broke a causal SELECTION rule that assumed sparse events; the fix routes the recovered events to
  who-did-what while sparing the causal candidate set -- who-did-what gain retained, causal byte-identical.
- **The right info-free twin destroys the RIGHT binding.** My first copula twin deranged the HOLDER, leaving the
  PROPERTY (patient) readout untouched -> a false +0.000 twin. Deranging the state<->SENTENCE binding (which both
  holder and property retrieval depend on) collapses it to 0.0072 -- the twin that actually controls the claim.
- **have/do looked like 22% headroom and were mostly already solved** (main-verb forms fire) -- measuring the class
  partition BEFORE building saved a detector nobody needed and localized the real gap to copula 'be'.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md SS2b)
- **Event/predicate DETECTION turn-on:** `predicate_recall` (P6) is NET-POSITIVE on BOTH who-did-what arms on the
  CURRENT reader (agent +0.0082 / patient +0.0084 CI-sep; agent/open +0.0098, patient/open +0.0108), beats the
  random-verbhood twin CI-sep on the patient arm. **Mark DEFAULT-ON-recommended, SCOPED** (compute causal_links
  over base events) -- supersedes the P6 "kept-off, flat" note (measured on the weaker pre-2026-09-03 reader).
- **NEW PINNED deviation (load-bearing): the who-did-what readout is SILOED from the copular-state dimension.**
  Copular predications are detected (default-ON `bind_entity_states`, 0.677R/0.872P) but unreachable by the
  who-did-what readout; a sort-aware readout (HOLDER->agent / PROPERTY->patient) lifts patient/be 0.0000->0.2590
  CI-sep. Faithful fix = a UNIFIED sort-typed eventuality inventory ("assemble the tiered bound event token"); the
  readout unification is the near-term consumable.
- **NEW located adjacent-component negative: the causal dimension's connective cause-SELECTION is density-brittle**
  (regresses -0.0594 CI-sep when the event set densifies). It is an adjacency/connective OUR-INVENTION, not
  force-dynamic attribution (Talmy/Wolff) -- the faithful upgrade. Scoping neutralizes it for now.
- **Confirmed refinement:** the recoverable who-did-what event-detection headroom is the copula 'be' class, NOT
  open-class mistags (small) nor have/do (main-verb forms fire) -- localizes the agent-tie problem's "58.6%
  detection residual" to the copular silo, not the tagger.

## What I did NOT establish / would withdraw first if wrong
- I did NOT land the hdlab wire -- I prove the mechanism in `experiments/` + `verification/` and propose the diff
  (SS8); strategy lands it (Q111). The wire has TWO coupled parts (scoped predicate_recall + the copula readout);
  landing predicate_recall UNSCOPED alone would regress causal -0.0594 -- I would withdraw any "clean default-ON"
  claim for the unscoped flag.
- **agent/be recovery is POSITIVE but not CI-separated** on the degenerate board instrument -- I withdraw any
  "agent copula arm CI-sep" claim; the defensible copula claim is the PATIENT arm (+0.2590 CI-sep over base+twin)
  and the whole-arm composite (agent/all +0.0230 CI-sep, carried partly by the marginal copula agent slice).
- The copula readout is a READOUT unification, not new detection; it depends on `bind_entity_states` staying
  default-ON, and inherits the UD-parser-in-domain copular binding (OOD 19c copular ~0.64-0.73).
- The FP "0.845 no-gold-match" is a loose upper bound (sparse who-did-what gold), not a true false-verb rate; the
  trustworthy statement is ~1.0 extra events/sent and "the FP does not reach a who-did-what answer" (measured via
  the net-positive arms + coref byte-identical).
- **No-regression was measured on the three externally-instrumented board dims (coref/temporal/causal).** Two other
  dims also consume the event stream (`world_state`, `bound_event_tokens`); the copula readout (lever B) cannot
  touch them by construction (it never adds an event), but predicate_recall's extra events could -- I did NOT
  separately measure those two, and flag them for the strategy's landing re-verify (the same fixed-instrument test;
  if either shows the causal-style density sensitivity, scope recall out of it too). Lever B is universally safe;
  lever A's landing carries this one open check beyond causal.

---

### TLDR (plain language)
Our reader answers "who did what" only about things it noticed happening. Two things held it back. First, it
sometimes mistags an action word (common in old novels) and loses the whole event; we had a switched-off fix, and
-- re-checked on today's stronger reader -- switching it on helps both "who did it" and "what was it done to," a
small clean gain. But checking EVERY part of the scoreboard (not just one) caught a catch: the extra events
confused the cause-and-effect questions, because that part of the reader assumed events are sparse. The fix was
simple -- feed the recovered events to the "who did what" reader but not to the cause-and-effect one -- and it
removes the harm completely while keeping the gain. Second, and bigger: the reader already recognises "X is a
captain / the streets are muddy" *states*, but filed them in a drawer the "who did what" reader never opened -- so
"who is the captain?" scored zero with the answer sitting there. We let it open that drawer. That took the "what
was it" copula questions from **0% to 26% correct**, and a scrambled version gets essentially 0% -- proving it
reads a real binding, not a guess. Net: more answered on both arms, and nothing else worse.

### QUESTIONS
None blocking. One judgement call for strategy at landing: the copula silo-unification is a READOUT change (reach
into `sm.entity_states`), not a detection change -- the cleaner long-term form is ONE sort-typed eventuality
inventory (the "assemble the tiered bound event token" problem), but the readout unification is the consumable that
delivers the patient/be win now. And predicate_recall must land SCOPED (causal over base events) or not at all.

### NEXT STEPS
1. **Land the wire (SS8):** turn `predicate_recall` ON scoped (causal over base events); add the sort-aware copula
   readout to the who-did-what path.
2. **The unified sort-typed eventuality inventory** ("assemble the tiered bound event token") -- physically merge
   dynamic events + copular states into one sorted store so EVERY consumer sees the whole inventory.
3. **Force-dynamic causal attribution** -- replace the density-brittle connective cause-selection with the typed
   force-dynamic path so causal is robust to a complete event set (retires the scoping workaround).
4. **The 19c open-class fidelity gap** -- land the P7 CRF calibrated-posterior / joint-decoded tagger (+0.224
   prototyped) to push open-class 19c recovery from 0.56 toward ~1.0.
5. **A property-carrying copula instrument** -- to measure the (already-strong) holder binding fairly on the agent side.
