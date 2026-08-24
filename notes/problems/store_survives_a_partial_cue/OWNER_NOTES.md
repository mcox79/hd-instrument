---
owner_verdict: DONE
---

SUBMISSION — problem: store_survives_a_partial_cue — status: REFUTED (first-class)

WHAT WAS ASKED
"Our store can recite but cannot recognise." Ask memory with the exact stored words and it answers
almost perfectly (0.9954); ask with only SOME of those words — all real reading ever gives — and it
collapses (0.1399), losing to plain word-counting (0.3242). The brief: design a better STORE whose
read-out survives a partial cue and beats counting on held-out text.

THE ANSWER — a better store FORMAT is not the fix. Refuted, and relocated.
I built the strongest brain-faithful stores I could, on the refuted cell's IDENTICAL live-path
instrument (so the floor reproduces at 0.3242 by construction). Grounded in how the brain recognises:
dual-process theory (fast cortical FAMILIARITY + episodic hippocampal RECOLLECTION) and predictive
coding (cortex computes a calibrated posterior). NONE beats counting:

  F_COUNT1  (PMI familiarity — the floor, reproduced) ... 0.3242  CI[0.3115, 0.3366]
  NB_LOGODDS (Bernoulli posterior) ..................... 0.0022
  NB_MULT   (multinomial likelihood) .................. 0.0486
  REC_EXPLICIT (explicit hippocampal recollection) ... 0.1619   (recites 0.9122 exact-key!)
  FAM_REC   (linear CLS dual-process) ................. 0.2066
  CONF_GATED (selective/confidence-gated control) ..... 0.2461   ← best store arm, still BELOW floor
  ORACLE_UNION (best-of-three per item) — CEILING ..... 0.4082   +0.0840 CI[+0.077, +0.091]
  controls: INFO_FREE 0.0000 (loses), SCRAMBLE 0.0000 (chance), self-retrieval 2AFC 0.9767 (works)
  n = 5,490 anchor lemmas, one held-out query each, lemma-weighted hit@1, live reading path.

THE TWO FINDINGS THAT MAKE THIS PRODUCTIVE
1. COUNTING ALREADY IS THE BRAIN'S FAMILIARITY SIGNAL. F_COUNT1 = PMI = log[P(w|L)/P(w)]; the
   corpus-baseline term it subtracts is exactly the informativeness weighting a calibrated posterior
   needs. The NB variants that DROP that term collapse — so there is no better first-order
   familiarity read-out to build. Store format is not the lever (this is now the 3rd format shown
   losing: superposition, addressing, and this).
2. THE COLLAPSE IS NOT AN INFORMATION CAP. A per-item oracle that picks the best of three methods
   reaches 0.4082, +0.084 CI-SEPARATED above the floor. The signal to beat counting IS in the store —
   recollection is right on a real subset where familiarity fails. What's missing is a CONTROL that
   knows WHEN to trust recollection; no UNSUPERVISED gate I built finds those moments.

DIAGNOSIS: the recite/recognise gap is a missing CONTROL NETWORK, not a bad store — the same
conclusion as reader_meaning_channel. Two independent problems now point at the same missing piece.

PROPOSED hdlab CHANGE (not landed — Q111): do NOT swap the store format. If a recognition read-out
is wired, it should compute the explicit PMI familiarity (= F_COUNT1). The real missing organ is a
learned recollection-gating CONTROL (over familiarity-confidence + recollection-confidence + cue-
length) plus an explicit episodic recollector (REC_EXPLICIT; not ca3_completer — its completion
regime never occurs here).

WHAT I DID NOT ESTABLISH / WOULD WITHDRAW FIRST
Did NOT build a LEARNED gate, so I have not shown the 0.084 reserve is unreachable — only that no
unfitted read-out reaches it. Most-exposed claim: "PMI is the ceiling of first-order familiarity"
(rests on the NB variants losing); I withdraw that before the missing-control diagnosis.

NEXT STEP (for a new brief): a LEARNED recollection-gating control — train on the profile/exact-key
split, apply to held-out, info-free twin must still lose. Same bar (0.3366); ceiling is the 0.4082
oracle union. If it clears, the gap is a solved control problem; if not even a learned gate clears
it, the information-cap reading becomes airtight.

FILES / REVERIFY
experiments/exp_recognition_store_calibrated_familiarity_recollection_v1.py
verification/test_recognition_store_calibrated_familiarity_recollection.py
notes/problems/store_survives_a_partial_cue/SOLVED.md
reverify:  .venv/Scripts/python.exe verification/test_recognition_store_calibrated_familiarity_recollection.py
  (scaffold-free witness: recomputes every number from the saved population with its own bootstrap;
   6/6 checks pass — floor reproduces, no arm clears, controls bind, oracle-union ceiling, recite/
   recognise gap. Ledger: malformed/incomplete: 0.)
