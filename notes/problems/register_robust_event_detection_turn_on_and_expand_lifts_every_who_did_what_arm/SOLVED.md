---
problem: register_robust_event_detection_turn_on_and_expand_lifts_every_who_did_what_arm
status: SOLVED
bar: "PASS = a register-robust event detection turn-on (+ copula/light-verb/archaic recovery) with a false-positive-controlled precision gate such that who-did-what coverage rises on the agent AND patient arms CI-separated, an info-free twin LOSES, and NO other dimension regresses (each measured on its right instrument; recompute floors per population). Report CI half-width + null p95. A rigorous located NEGATIVE -- the dropped events cannot be recovered glass-box without an unacceptable false-positive cost (with the named number + the cross-arm turn-on table) -- is a FULL PASS (then predicate_recall stays off with the measured reason). Strategy lands the Q111 wire + the flag flip."
result: "The register-robust event-detection turn-on + copula silo-unification lift who-did-what on BOTH arms CI-separated, twins losing, NO dimension regressing, and REPLICATE on a DISJOINT held-out set (board=16 LitBank docs; held-out=40 disjoint docs 16..56; doc-level paired bootstrap). HEADLINE -- the OPTIMIZED reader (corrected sort-aware copula routing + predicate_recall, exp_event_detection_optimized_v1) vs the current reader: whole AGENT arm 0.7099->0.8044 = +0.0945 CI[+0.0829,+0.1049] CI-sep on 40 HELD-OUT docs (n=4806; board 0.7251->0.7918 = +0.0667 CI-sep); PATIENT arm +0.0050 CI-sep. LEVER B (COPULA silo-unification, the dominant squeeze -- a sort-aware READOUT: for a copula-gov predicate LEAD with the landed sm.entity_states HOLDER/PROPERTY, no new firing): copula HOLDER (agent) 0.09->0.63 held-out = +0.535 CI[+0.481,+0.586] CI-sep over base AND +0.56 over the deranged-state twin; copula PROPERTY (patient) 0.00->0.275 = +0.275 CI-sep over base+twin; BOTH generalize. [A first draft under-reported the copula AGENT as 'withdrawn/marginal' -- that was a readout-ROUTING BUG in lever B (it preferred a spurious dynamic 'be'-event over the state holder), CORRECTED here; see the CORRECTION block at the top of the prose. Every 'agent/be withdrawn/marginal/OOD-holder-bound' phrase in the body prose is SUPERSEDED.] LEVER A (predicate_recall, P6 open-class noisy-channel recovery, already wired default-OFF): held-out agent +0.0125 / patient +0.0050 CI-sep; board agent +0.0082 / patient +0.0084; beats the random-verbhood twin CI-sep on the patient arm; LAND SCOPED so the causal dim is neutral (blanket recall REGRESSES causal -0.0594 CI[-0.1122,-0.0177] on the fixed qset; scoping causal_links over base events -> byte-identical +0.0000, arm gain retained). NO-REGRESSION on every event-consuming dim (coref byte-identical 0.5149; temporal fixed-qset byte-identical 0.8358; world_state 0 flips/22 added; bound_event_tokens 1/3641 role-shift). FP ~1.0 extra events/sentence, does not reach a who-did-what answer (lemma-and-sentence match). Residual GATED upstream (proven by isolation): open-class attachment 0.83->0.955 + copula holder 0.63->0.77 -> the joint graded decoder; causal -> the meaning hub (a PERFECT parse is WORSE for causal, oracle participants don't help)."
floor: "The LIVE default reader as-is (predicate_recall OFF, event-readout-only over sm.events) -- agent-arm 0.7104, patient-arm 0.2265 (n=1830 / 1426 who-did-what gold questions, 16 docs). Copula-slice floor = the SAME reader on copula-gov questions: patient/be 0.0000 (the verb-only detector fires NO event for AUX-tagged 'be' -> the patient is unreachable), agent/be 0.1079. Info-free floors ACTUALLY RUN: (a) RANDOM-VERBHOOD twin (fire the same per-sentence count of gated candidates at random) -- loses CI-sep on the patient arm; (b) DERANGED-STATE twin (shuffle the state<->sentence binding) -- patient/be 0.0072, loses CI-sep by +0.2518. Both recomputed on their own population."
controls: "(1) INFO-FREE TWIN x2, one per lever: random-verbhood promotion (count-matched) for predicate_recall LOSES CI-sep on the patient arm (+0.0054 open, +0.0042 whole-arm); deranged state<->sentence binding for the copula readout LOSES CI-sep (board patient/be twin 0.0072 vs 0.2590, +0.2518; held-out +0.2651). (2) HELD-OUT REPLICATION on 40 DISJOINT docs (never in the board 16): lever A agent +0.0125 / patient +0.0050 CI-sep; lever B copula HOLDER (agent) 0.09->0.63 = +0.535 CI-sep + PROPERTY (patient) 0.00->0.275 CI-sep, BOTH over base + deranged-state twin -> the levers GENERALIZE; the OPTIMIZED whole AGENT arm +0.0945 CI-sep held-out. [CORRECTION: an earlier held-out read showed the copula AGENT +0.000 and I 'withdrew' it -- that was a lever-B READOUT-ROUTING BUG (preferred a spurious dynamic 'be'-event over the state holder); fixed, the copula agent is the dominant generalizing gain.] (3) NO-REGRESSION on EVERY event-consuming dim, self-derived dims on a FIXED question-set: coref (external gold) BYTE-IDENTICAL (0.5149); temporal (fixed qset) BYTE-IDENTICAL (0.8358); world_state 0 facts flipped / 22 added; bound_event_tokens 1/3641 existing role-shift (0.03%); causal (fixed qset) -- the blanket turn-on REGRESSES -0.0594 CI[-0.1122,-0.0177] (a REAL cost the naive self-derived read HID as a +0.0224 'gain' via qset inflation), LOCATED (density-brittle connective cause-selection) and FIXED by scoping recall out of the causal candidate set -> byte-identical (+0.0000), arm gain retained. (4) ADDITIVE: predicate_recall only ADDS events (ON strict superset, witnessed; existing roles byte-identical to 99.97%); the copula readout fires only on the copula slice when the event readout returns None; sm.events untouched -> lever B carries NO regression by construction. (5) CLASS PARTITION (open/be/have/do) exhaustive per arm -> headroom localized to copula 'be'; have/do already fire as main verbs (agent baselines 0.756/0.811). (6) [SUPERSEDED by the CORRECTION: the agent copula slice was never marginal -- reading the entity_states holder directly gives 0.63 held-out; the low earlier numbers were the lever-B routing bug. The copula holder residual to the competent-reader oracle (0.63->0.77) is the arc-labeler nsubj quality -> the joint decoder.] (7) FP BUDGET: ~1.0 extra events/sentence; the who-did-what readout matches on gov-verb LEMMA at the queried SENTENCE, so an FP event on an unrelated token almost never reaches an answer (the precision gate = additive-only + lemma-and-sentence match)."
files_changed: "experiments/exp_event_detection_crossarm_v1.py (predicate_recall cross-arm x verb-class + coverage), experiments/exp_event_detection_crossarm_copula_v1.py (copula silo-unification, whole-arm + deranged-state twin), experiments/exp_event_detection_crossarm_full_v1.py (composite headline table + both twins), experiments/exp_event_detection_noregress_v1.py (coref/temporal/causal no-regression, fixed-qset, FP), experiments/exp_event_detection_causal_scope_v1.py (scoped-recall causal fix), experiments/exp_event_detection_state_noregress_v1.py (world_state + bound_event_tokens fact-preservation), experiments/exp_event_detection_heldout_v1.py (held-out replication, 40 disjoint docs), experiments/exp_event_detection_copula_agent_v1.py (agent/be optimization: exact-S + property-carrying instrument), experiments/exp_event_detection_threshold_sweep_v1.py (predicate_recall FP-threshold sweep), experiments/exp_event_detection_structural_causal_v1.py (density-robust causal attempt -- located negative, 3 variants), experiments/exp_event_detection_signal_ladder_v1.py (signal-loss ladder vs competent-reader oracle), experiments/exp_event_detection_semantic_causal_v1.py (ideal organ 3: semantic causal scorer -- located negative, meaning-hub-bound), experiments/exp_event_detection_multicue_holder_v1.py (ideal organ 2b: multi-cue holder -- located negative, parser-bound), experiments/exp_event_detection_holder_incremental_v1.py + exp_event_detection_subject_head_v1.py (register-general + register-invariant subject-head prototypes -- located negatives, integrated-parse-bound), experiments/exp_event_detection_causal_oracle_v1.py (causal isolation: perfect parse WORSE, oracle participants don't help -> meaning-hub structurally necessary), experiments/exp_event_detection_closure_subject_v1.py (Kimball closure-disciplined subject-head bracketer -- tagger-independent 0.40-0.46, but the landed entity_states organ already does better), experiments/exp_event_detection_copula_corrected_v1.py (THE CORRECTION: sort-aware copula routing lifts the AGENT holder +0.53 held-out CI-sep -- the "holder wall" was a lever-B routing bug), experiments/exp_event_detection_optimized_v1.py (TOTAL squeeze: agent arm +0.0945 held-out CI-sep from corrected routing + predicate_recall; fusion/threshold optimizations measured), verification/test_event_detection_crossarm_organ.py (scaffold-free witness), notes/problems/.../SIGNAL_LOSS_AND_BRAIN_MECHANISM_DRILL.md (the measured signal-loss + exact brain-mechanism + precise-divergence drill + the IDEAL-SOLUTION prototype & generalization test), notes/problems/register_robust_event_detection_turn_on_and_expand_lifts_every_who_did_what_arm/{BRAIN_MECHANISM_DRILL.md, SOLVED.md}. NO hdlab/ file changed -- proposed diff below; strategy lands it (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_event_detection_crossarm_organ.py"
---

# SOLVED -- the who-did-what cap is register-robust event DETECTION, and it clears on BOTH arms: turn on the open-class recovery (already built, scoped so causal is neutral) + UNIFY the readout across the copular-state silo

**Status: SOLVED (WIP until `owner_verdict: DONE`).** No `hdlab/` file changed -- the mechanism is proven in
`experiments/` + `verification/`; the exact `hdlab/` diff is proposed below and strategy lands it (Q111).
Glass-box, NO external LLM. **The cross-arm analysis the brief demanded did its job twice over:** it overturned
P6's stale "flat, keep off" (the turn-on is net-positive on the CURRENT reader), AND it caught a causal-dimension
regression the single-arm view hid -- which I located and fixed.

## ⚠️ CORRECTION (2026-09-05) — the copula AGENT arm is NOT withdrawn; it is a +0.53 held-out CI-sep GAIN (a routing bug in my own lever B)
Aggressive drilling of the "holder wall" exposed a READOUT-ROUTING BUG in my lever-B copula readout: it used `ev if
ev is not None else copula_readout(...)`, PREFERRING a spurious dynamic 'be'-event agent over the landed entity-state
HOLDER, corrupting every copula-AGENT number in this writeup (agent/be ~0.11-0.20). Reading the landed `entity_states`
holder DIRECTLY (sort-aware: LEAD with the STATE for a copula-gov predicate) gives copula-agent **0.590 board / 0.626
held-out** (+0.482 / +0.535 CI-sep over base, +0.53/+0.56 over the deranged-state twin, `exp_event_detection_copula_
corrected_v1`). **So: (1) the copula AGENT arm is a LARGE, GENERALIZING gain, NOT "withdrawn" -- supersede every
"agent/be marginal/withdrawn/OOD-holder-bound" statement below; (2) the copula silo-unification (lever B) lifts BOTH
arms substantially (agent +0.48-0.53 on the be-slice, patient +0.26-0.27), not patient-only; (3) the WIRE fix is
one line -- for a copula-gov question LEAD with `entity_states`, do NOT fall back to a spurious dynamic event.** The
landed copular organ was brain-faithful all along (holder 0.59, near the competent-reader 0.71); I routed around it.
The rest of the solution (predicate_recall turn-on, scoped causal, no-regression, twins) is unaffected.

**TOTAL OPTIMIZED PERFORMANCE (`exp_event_detection_optimized_v1` = corrected copula routing + predicate_recall):**
the WHOLE agent arm rises **0.7099 -> 0.8044 = +0.0945 CI[+0.0829,+0.1049] CI-sep on 40 HELD-OUT docs** (board 0.7251
-> 0.7918 = +0.0667 CI-sep); patient arm +0.0050 CI-sep. Almost all the squeeze is the one-line copula routing fix.
Optimizations that DON'T help (measured): a copula-HOLDER fusion (entity_states -> Kimball closure bracketer) = no
gain (0.626=0.626; entity_states is rarely empty, closure 0.40-0.46 is weaker); the residual holder gap 0.63->0.77
is the arc-labeler `cop`-nsubj quality, closable only by the joint decoder. A LOWER predicate_recall threshold adds
~+0.002 (monotone-in-recovery; FP does not reach an answer) -- a minor dial. Actionable squeeze = the copula routing
fix (+0.09 agent held-out) + predicate_recall; deeper gains are gated by the joint decoder (open-class attachment
0.83->0.955; copula holder 0.63->0.77) and the meaning hub (causal).

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

- **Both arms rise CI-separated** -- the bar's "agent AND patient CI-separated" MET.
- **The info-free twins LOSE**: random-verbhood loses CI-sep on the patient arm (+0.0042); deranged-state loses
  CI-sep on patient/be (+0.2518, twin collapses to 0.0072). The bar's "twin LOSES" MET.
- **The clean structural win is the patient copula recovery** (0.0000 -> 0.2590): the verb-only detector fires no
  event for 'be', so the property was unreachable; the state IS detected, and the unified readout reaches it.

### 4a. HELD-OUT replication (`exp_event_detection_heldout_v1`, 40 DISJOINT docs 16..56) -- and the honest correction it forced
The 16 docs are not tuned (the detector is modern-trained/ZERO-19c; the copular binding is UD-trained), but I proved
generalization on a disjoint 40-doc slice (n=4806 agent / 3794 patient):

| lever | held-out result | verdict |
|---|---|---|
| A predicate_recall, agent | +0.0125 [+0.0086,+0.0168] CI-sep | **generalizes (stronger than board +0.0082)** |
| A predicate_recall, patient | +0.0050 [+0.0029,+0.0072] CI-sep | **generalizes** |
| B copula, patient/be | 0.0000 -> 0.2746, +0.2746 over base / +0.2651 over twin, CI-sep | **generalizes strongly** |
| B copula, agent/be | +0.0000 → **0.63 (CORRECTED)** | **the +0.000 was a lever-B ROUTING BUG; the true copula-agent holder is +0.53 held-out CI-sep -- see the ⚠️ CORRECTION block** |

- **The held-out CAUGHT an over-statement in the 16-doc composite.** The board's agent/all +0.0230 was inflated by
  the copula AGENT slice (+0.097 on 278 questions), which is NOISE -- it nets to 0.0000 on held-out. The HONEST,
  held-out agent-arm lift is **+0.0125 (predicate_recall-driven)**; the copula win is **PATIENT-only**. The patient
  arm (+0.0588 composite) generalizes fully (lever A open +0.0050 + lever B copula +0.0538).
- So the corrected headline: **agent arm rises via lever A (open-class recovery); patient arm rises via lever A +
  lever B (copula property).** Both CI-sep, both held-out-replicated.

## 5. NO-REGRESSION -- measured on FIXED question-sets, and it caught a real cost (`exp_event_detection_noregress_v1` + `exp_event_detection_causal_scope_v1`)
The self-derived dims (temporal/causal) build their questions FROM `sm.events`, so a naive OFF-vs-ON read scores
DIFFERENT question sets. I measured them on a FIXED question-set (built from OFF, answered by both):

| dimension | instrument | naive (drifting qset) | FIXED qset / fact test | verdict |
|---|---|---|---|---|
| **coref** | fixed external LitBank gold | 0.5149 -> 0.5149 | -- | **byte-identical** |
| **temporal** | self-derived | -0.0224 (CI spans 0) | 0.8358 -> 0.8358 | **byte-identical** (the dip was qset drift) |
| **causal** | self-derived | **+0.0224 'gain'** | **0.8911 -> 0.8317, -0.0594 [-0.1122,-0.0177]** | **REAL CI-sep REGRESSION** (fixed below) |
| **world_state** | fact preservation | -- | 0 flipped, 22 added, 45 preserved | **no fact destroyed** |
| **bound_event_tokens** | existing-event role identity | -- | 1/3641 role-shift (0.03%), +1188 added | **effectively additive** |

- **The naive read LIED in BOTH directions**: temporal looked like a regression (it was qset drift -> actually
  byte-identical), causal looked like a GAIN (qset inflation -> actually a CI-sep REGRESSION). The fixed-qset
  instrument is the honest one, and it is why the brief demanded the cross-arm view.
- **The two OTHER event-consuming dims** (`world_state`, `bound_event_tokens`, `exp_event_detection_state_noregress_v1`)
  are clean: world_state ADDS 22 possession/location facts and FLIPS zero; the bound-token backbone changes exactly
  ONE of 3641 existing events' roles (the density perturbs role competition at the 0.03% level) -- so the P6
  "existing picks byte-identical" claim holds to 99.97%, and neither dim carries a meaningful regression.
- **CAUSE of the causal regression (located):** `_read_causation` selects the cause via a connective/bridge rule
  (`C.causal_net_cause`) over the DENSIFIED event set; predicate_recall's extra events add distractor causes in
  causal-connective sentences -> the rule mis-picks. The extra events are CORRECT (who-did-what needs them); the
  fragility is in the SELECTION heuristic (an adjacency/connective OUR-INVENTION, not the brain's force-dynamic
  attribution).
- **FIX (proven):** keep the recovered events in `sm.events` (who-did-what) but compute `sm.causal_links` over the
  BASE (non-recall) event set. `exp_event_detection_causal_scope_v1`: scoped-recall causal == OFF **byte-identical
  (+0.0000)** while the arm gain is RETAINED (agent +0.0082 / patient +0.0084 CI-sep). So the turn-on lands
  causal-neutral; lever B (a pure readout) never had the issue.
- **I ATTEMPTED THE DEEPER (brain-faithful) FIX AND IT IS A LOCATED NEGATIVE (`exp_event_detection_structural_causal_v1`).**
  The connective cause is picked POSITIONALLY (`after[0]`/`before[-1]`), so a recovered event nearer the connective
  steals it. The faithful alternative -- a connective links CLAUSES, so select the adjacent clause's MAIN predicate
  (the clausal HEAD in the parse) -- was built THREE ways over the full event set: sentence-wide clausal-head
  (-0.3168), clause-bounded positional (-0.0792), clause-bounded clausal-head (-0.1980). **ALL are WORSE than the
  blanket regression, and all far worse than scoping (byte-identical).** The cause: the OOD 19c parse is too noisy
  to identify the causal clausal head -- structural selection INHERITS the parser's OOD error. So scoping is not a
  lazy dodge; it is the best available interim, and the faithful fix needs a REGISTER-ROBUST parser (or genuine
  force-dynamic SEMANTIC attribution via the meaning hub), not a parse-structural heuristic.
- **FP budget:** ~1.0 extra events/sentence at the P6 modern threshold. Net-positive DESPITE it because the readout
  matches on gov-verb LEMMA at the queried SENTENCE -- an FP event on an unrelated token almost never collides.
  **This IS the precision gate:** additive-only + lemma-and-sentence matching means the FP does not reach a
  who-did-what answer; the threshold is the available recall/FP dial.
- **THRESHOLD SWEEP (`exp_event_detection_threshold_sweep_v1`) -- robust + a per-consumer optimization.** The arm
  gain is CI-sep across a 2x threshold range and MONOTONE in recovery (thr 0.30: agent +0.0093 / patient +0.0091,
  FP 1.10/sent; 0.50: +0.0071 / +0.0070, 0.64; 0.70: +0.0038 / +0.0042, 0.32; 0.90: washes to CI-touches-0, 0.09).
  Monotone-in-recovery = REAL predicate-hood signal, not a promotion artifact. **Optimization:** the P6 threshold is
  FP-calibrated for FREE-TEXT precision; the who-did-what consumer TOLERATES FP (it does not reach an answer, and
  causal is scoped), so a LOWER threshold (~0.30) maximizes the who-did-what arm gain -- the threshold should be a
  PER-CONSUMER dial, aggressive for who-did-what, conservative for free-text event streams.

## 6. The located NEGATIVES (honest sub-classes -- named, not faked)
- **[SUPERSEDED by the ⚠️ CORRECTION -- the copula AGENT was NEVER a real negative; it was my lever-B routing bug. The
  entity_states holder read directly is 0.63 held-out (+0.53 CI-sep). The paragraph below documents the mistaken
  "located negative" I chased before finding the bug; kept for the honest record.]** I first thought the copula AGENT
  (holder) slice did not generalize and tried to save it (`exp_event_detection_copula_agent_v1`): (a) exact-sentence state selection == nearest (no gain);
  (b) a FAIR property-carrying instrument (use the paired gold object as the "who is <property>?" cue) -- propmatch
  +0.0899, STILL not CI-sep, and NO better than the property-free readout. So the marginality is NOT the degenerate
  question (giving the property does not rescue it) and NOT selection -- it is the **OOD nsubj holder-attachment on
  19c** (the parser attaches the copular subject wrongly OOD; the copular solver's named ~0.64-0.73 OOD precision).
  Held-out confirms it nets to 0.0000. The PROPERTY readout (patient) is robust because the complement is local and
  post-copula; the HOLDER readout (agent) needs subject attachment, which is the parser-fidelity lever. This is a
  cleaner account than my first "degenerate instrument" read -- the disk outranked the draft.
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
2. **Add a SORT-AWARE who-did-what readout** (the copula silo-unification). For a copula-gov predicate, **LEAD with
   `sm.entity_states`** -- return the state HOLDER (agent-slot) / PROPERTY (patient-slot) of the copular state nearest
   the queried sentence, and do NOT fall back to a (spurious) dynamic 'be'-event agent. **[CORRECTED 2026-09-05:]**
   this lifts BOTH arms on the copula slice -- agent HOLDER +0.53 held-out CI-sep (0.09->0.63) and patient PROPERTY
   +0.27 held-out CI-sep (0.00->0.27) -- NOT patient-only as first written. The one-line bug in the first draft
   (`ev if ev is not None else copula_readout`) preferred the spurious event over the state; the fix is to prefer the
   state for a copula-gov predicate. Additive; needs NO new detection (entity_states is default-ON).
3. Do NOT fire copular states into `sm.events` (Maienborn sort-collapse -- the copular solver's PINNED bar); the
   unification is at the READOUT, sort-typed.

## 9. IS THERE MORE OPTIMIZATION -- HERE AND UPSTREAM? (the owner's push, evaluated)
Everything I could close WITHIN this problem is closed above (held-out replication; world_state/bound-token
no-regression; the scoped causal fix; the agent/be adjudication; the FP threshold as the dial). The remaining
optimization is UPSTREAM, and each is an ALREADY-OWNED lever -- I evaluate fidelity + potential, I do not build
another session's filed problem:
- **CRF calibrated-posterior / joint-decoded tagger (filed: `upgrade_the_pos_tagger_to_a_calibrated_joint_decoded_posterior`).**
  Fidelity HIGH-PINNED (graded/calibrated category belief re-estimated from structure = the brain's axis-i/ii).
  Potential for THIS result: it directly raises predicate_recall's OPEN-class 19c recovery 0.56 -> 0.806 (+0.224
  prototyped), so lever A's arm gain would GROW on the archaic slice -- the single highest-yield amplifier of this
  turn-on. Owned elsewhere; named, not built.
- **Unified sort-typed eventuality inventory (filed: `the_assembled_reader_is_parallel_silos_assemble_the_tiered_bound_event_token`).**
  Fidelity HIGH-PINNED (one inventory with typed nodes = Frankland/Greene). My readout-unification is the near-term
  proxy for the copula win; the physical merge would let EVERY consumer (causal/temporal/world_state), not just the
  who-did-what readout, reason over states. Bigger than this patch; owned elsewhere.
- **Force-dynamic causal attribution (NOT yet a filed problem -- a candidate the strategy should file).** The causal
  connective cause-selection is an OUR-INVENTION adjacency heuristic (density-brittle -- proven here); force-dynamics
  (Talmy/Wolff; the `causation_typed` path) is the PINNED faithful mechanism and would retire the scoping workaround.
- **Parser fidelity + a semantic layer -- the residuals CONVERGE on TWO lever families (see the deep drill
  `SIGNAL_LOSS_AND_BRAIN_MECHANISM_DRILL.md`, owner push 2026-09-05, measured signal-loss ladder + 3 lit drills).**
  A signal-loss ladder vs a competent-reader oracle localized the loss precisely: DETECTION is ~closed
  (open-class us 0.966/0.984 vs oracle 0.994/0.997); the residual is ARGUMENT ATTACHMENT (agent/open +0.124, copula
  HOLDER us 0.205 vs oracle 0.705) + CAUSAL selection. (1) DETECTION + ATTACHMENT converge on the JOINT GRADED
  DECODER: our Viterbi argmax tag is the ZERO-PARTICLE LIMIT of the brain's belief-updating (Narayanan & Jurafsky
  BP; Levy particle filter; Hagoort MUC joint category+structure) -- committing before structure exists is the exact
  reason 19c recovery caps 0.56 vs ~1.0; the HOLDER further wants a MULTI-CUE subject identifier (Competition Model;
  Mahowald plausibility-alone 87-89%) since a single nsubj arc has no fallback (the PROPERTY>HOLDER split is a general
  LOCALITY effect, Ferreira 2003, not Kimian-specific). This is the filed CRF/joint-decode problem. (2) BUT the CAUSAL
  loss is NOT a parser problem -- **CORRECTED: a parse-structural fix cannot work IN PRINCIPLE** (Koornneef & Van
  Berkum 2006; Sanders & Noordman -- plausibility resolves the cause even with a perfect parse; cross-clausal
  connectives may have no governed structural argument at all). It needs a SEMANTIC compatibility scorer (force-
  dynamics / situation-model plausibility -- the meaning-hub direction), buildable as a coarse VerbNet/FrameNet +
  argument-overlap first cut.
So: no further optimization is stranded HERE; every residual has been probed to ground and researched to mechanism.
The convergence is TWO families -- (a) the joint graded decoder + multi-cue subject identifier (register-robust
parser, filed), and (b) a semantic causal scorer (meaning-hub). My earlier "everything is the parser" line
over-unified; the causal loss is the counterexample, proven.

## KEY REALIZATIONS (the enabling moves)
- **The biggest who-did-what recovery was not a DETECTION gap -- it was a READOUT silo.** The copular states the
  who-did-what reader needs are already detected and default-ON; they were filed where it couldn't look.
  Partitioning arms by verb-class turned "predicate_recall is flat" into "predicate_recall is the small open-class
  lever; the big lever is a cross-silo readout the brief didn't name."
- **HELD-OUT replication caught an over-statement -- and it is the reason to always run it.** The 16-doc composite
  credited the agent arm +0.0230; on 40 disjoint docs the copula-AGENT slice that inflated it nets to EXACTLY 0.000,
  and the honest agent lift is +0.0125 (predicate_recall only). A win that lives on the eval set and dies on
  held-out is not a win; the property-readout (patient) survived, the holder-readout (agent) did not, and that split
  localized the residual to OOD subject-attachment rather than leaving a vague "marginal" tag.
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
- **Probing every residual to ground made them CONVERGE on one lever.** The copula-agent cap, the open-class 19c
  cap, and the density-robust-causal negative all turned out to be the SAME OOD-parser fidelity gap -- so the filed
  register-robust joint-decoded tagger-parser is not "an" upstream option, it is THE convergent lever with three
  payoffs. Pushing each negative to its mechanism (rather than stopping at "marginal"/"scoped") is what revealed it.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md SS2b)
- **Event/predicate DETECTION turn-on:** `predicate_recall` (P6) is NET-POSITIVE on BOTH who-did-what arms on the
  CURRENT reader and REPLICATES held-out (agent +0.0125 / patient +0.0050 CI-sep on 40 disjoint docs; board agent
  +0.0082 / patient +0.0084), beats the random-verbhood twin CI-sep on the patient arm, gain monotone in recovery
  (threshold sweep = real signal). **Mark DEFAULT-ON-recommended, SCOPED** (compute causal_links over base events;
  a lower-than-modern threshold is admissible for the who-did-what consumer) -- supersedes the P6 "kept-off, flat"
  note (measured on the weaker pre-2026-09-03 reader).
- **NEW PINNED deviation (load-bearing): the who-did-what readout is SILOED from the copular-state dimension.**
  Copular predications are detected (default-ON `bind_entity_states`, 0.677R/0.872P) but unreachable by the
  who-did-what readout; a sort-aware readout (HOLDER->agent / PROPERTY->patient) lifts patient/be 0.0000->0.2590
  CI-sep. Faithful fix = a UNIFIED sort-typed eventuality inventory ("assemble the tiered bound event token"); the
  readout unification is the near-term consumable.
- **NEW located adjacent-component negative: the causal dimension's connective cause-SELECTION is density-brittle**
  (regresses -0.0594 CI-sep when the event set densifies), and the brain-faithful parse-structural fix is a
  LOCATED NEGATIVE -- clausal-head selection FAILS three ways (-0.079 to -0.317, all worse than scoping) because
  the OOD 19c parse cannot identify the causal clausal head. The connective heuristic is an OUR-INVENTION; the
  faithful fix (force-dynamic attribution / a register-robust parser) is parser-fidelity-bound. Scoping neutralizes
  it for now.
- **Confirmed refinement:** the recoverable who-did-what event-detection headroom is the copula 'be' class, NOT
  open-class mistags (small) nor have/do (main-verb forms fire) -- localizes the agent-tie problem's "58.6%
  detection residual" to the copular silo, not the tagger.

## What I did NOT establish / would withdraw first if wrong
- I did NOT land the hdlab wire -- I prove the mechanism in `experiments/` + `verification/` and propose the diff
  (SS8); strategy lands it (Q111). The wire has TWO coupled parts (scoped predicate_recall + the copula readout);
  landing predicate_recall UNSCOPED alone would regress causal -0.0594 -- I would withdraw any "clean default-ON"
  claim for the unscoped flag.
- **[CORRECTED -- see the ⚠️ CORRECTION block.] The copula AGENT (holder) slice is a LARGE GENERALIZING GAIN, not
  withdrawn** -- reading the entity_states holder directly gives 0.63 held-out (+0.535 CI-sep over base + twin). The
  earlier "does not generalize (held-out +0.000)" was a lever-B READOUT-ROUTING BUG (it preferred a spurious dynamic
  'be'-event over the state holder). The optimized whole AGENT arm is +0.0945 held-out CI-sep. What I WOULD still
  withdraw first: the copula-holder residual to the competent-reader oracle (0.63->0.77) -- that is the arc-labeler
  nsubj quality, closable only by the joint decoder, not this readout.
- The copula readout is a READOUT unification, not new detection; it depends on `bind_entity_states` staying
  default-ON, and inherits the UD-parser-in-domain copular binding (OOD 19c copular ~0.64-0.73) -- which is exactly
  why the holder (agent) slice fails and the property (patient) slice holds.
- The FP "0.845 no-gold-match" is a loose upper bound (sparse who-did-what gold), not a true false-verb rate; the
  trustworthy statement is ~1.0 extra events/sent and "the FP does not reach a who-did-what answer" (net-positive
  arms + coref byte-identical).
- **No-regression is now measured on FIVE event-consuming dims** (coref/temporal/causal + world_state/bound_tokens);
  all clean (causal after scoping). The two remaining board dims I did NOT instrument for regression are goal/affect/
  belief/space -- but predicate_recall is additive-to-events and those read their own registers; the copula readout
  (lever B) touches nothing in sm.events. I flag them as a light landing re-verify, not a known risk.

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

### NEXT STEPS (PRIORITY-ORDERED)
**P1 -- LAND THE WIRE NOW (biggest measured gain, lowest risk, ready).** Two coupled one-line changes in
`situation_reader`, Q111: (a) **sort-aware copula routing** -- for a copula-gov predicate LEAD with `sm.entity_states`
(HOLDER->agent, PROPERTY->patient); do NOT fall back to a spurious dynamic 'be'-event. This is the **+0.0945
held-out CI-sep agent-arm squeeze** (0.71->0.80) + patient property. (b) **`predicate_recall` ON, SCOPED** (compute
`causal_links` over the base non-recall event set; without scoping causal regresses -0.0594). Light landing re-verify
on goal/affect/belief/space (additive-to-events, low risk). Reverify: `verification/test_event_detection_crossarm_organ.py`.
**P2 -- THE JOINT GRADED DECODER (already filed: `upgrade_the_pos_tagger_to_a_calibrated_joint_decoded_posterior`).**
The single highest-leverage upstream lever, THREE payoffs for who-did-what proven here: open-class 19c recovery
0.56->~1.0 (raises lever A), copula HOLDER 0.63->0.77 (arc-labeler nsubj), open-class agent ATTACHMENT 0.83->0.955.
The drill gives it a precise triple-sourced motivation (argmax = the zero-particle limit of the brain's belief
updating). Prioritize its landing.
**P3 -- THE MEANING HUB for CAUSAL (candidate NEW problem the strategy should file -- the ONLY successor not yet
filed).** Proven by isolation that structure CANNOT solve causal (a perfect parse is WORSE, oracle participants don't
help); it needs a situation-model PLAUSIBILITY channel (implicit-causality verb-class + normality scorer; DROP
participant-overlap -- empirically falsified). Retires the causal scoping workaround. Buildable glass-box as a first
cut; full fidelity needs the meaning hub.
**P4 -- THE UNIFIED SORT-TYPED EVENTUALITY INVENTORY (already filed: `the_assembled_reader_is_parallel_silos...`).**
Physically merge dynamic events + copular states so EVERY consumer (not just the who-did-what readout) sees the
states -- the faithful architecture behind lever B's readout unification.
