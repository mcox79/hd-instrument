---
owner_verdict: DONE
---

Problem: situation_model_has_no_tested_temporal_order_comprehension — done, ready for review (SOLVED).

DISK OUTRANKS THE BRIEF (say this first): the brief said "nothing composes tense into a
before/after model." False — the mechanism was already built (two HARD_PASS cells, 2026-07-24)
AND wired into situation_reader. So this was not a from-scratch build. What was genuinely
missing — and what I built + validated — is a QUERYABLE before/after register, tested on real
prose with a floor + info-free twin + CI + a coverage measurement, a REPRESENTATION decision,
and a downstream serve. Plus I fixed concrete live-wiring gaps.

VALIDATED (all --mode full; witness verification/test_temporal_order_register.py = 8/8):
- before/after: register 1.000 [1.000,1.000] vs the naive "telling order = event order" floor
  0.272 [0.194,0.349]; info-free twin loses (p95 0.602); past-perfect flashback positive
  control 1.000 vs 0.000. (Construction gold that ISOLATES the mechanism, like the SPACE organ.)
- Real prose: narration order is wrong on ~1 in 11 event pairs (8.7% base rate) → a LIVE
  signal, not a "narration suffices" negative. Hand-adjudicated 22 reorderings: 0 confident errors.
- Representation fork decided BY MEASUREMENT: the continuous magnitude line (reused
  transitive_ordering) reproduces the human distance-effect signature (margin slope +0.66) +
  a calibrated confidence, which the discrete toposort can't — but adds NO accuracy (I caught +
  removed a tiebreak-vs-truth confound). Verdict: keep discrete primary, layer continuous as a
  confidence read-out.
- Serve (wire-don't-island): temporal order constrains causal DIRECTION — on "The bridge
  collapsed. The flood had weakened it," 1.000 vs the order-agnostic default's 0.000.

WALL DRILLED THE BRAIN'S WAY: the real-prose cap is tense EXTRACTION, not ordering logic. The
fixed 3-token "had"-window misses inverted pluperfects ("had the paragraph originally stood…");
the brain binds "had" to its participle across the clause, so I built that. Quantified vs a
spaCy dependency reference: EVENT-pluperfect recall 0.911 → 0.941 (~6% residual — small). Key
reframe: 27% of real "had"-pluperfects are copular "had been X" = a prior-STATE channel we drop
(a different dimension, next-problem), which had inflated the apparent wall.

FOR STRATEGY — LAND (Q111, you own hdlab): promote experiments/_temporal_order_register.py →
hdlab/temporal_order_register.py; fix situation_reader._read_timeline to run whole-passage +
drop the "had"-only gate + apply the clause-pluperfect binder; point _read_causation at the
register for causal direction. This turns a built-but-under-firing organ into a live, queryable,
correctly-firing one.

NEXT PROBLEMS (evaluated + de-risked this session, ready to file):
1. CAUSATION via force dynamics (Talmy/Wolff CAUSE/ENABLE/PREVENT). Fully scoped
   (next_problem_scoping_causation_force_dynamics_2026-08-29.md) AND de-risked with a built probe
   (exp_causal_force_dynamics_probe_v1.py): 1.000 on the PREVENT killer vs placeholder 0.000, and
   1.000 on CAUSE-vs-ENABLE where a verb-shuffle twin is at chance. Reuses the TIME precedence gate;
   cautionary disk precedent = do-calculus routing already HARD_FAILed.
2. Per-entity resultant-STATE register for the dropped 27% "had been X" channel (feeds the ENTITY
   dimension; reuses the SPACE register's interval pattern).
(See adjacent_components_brain_fidelity_map_2026-08-29.md for the full 5-dimension map.)

REVERIFY: .venv/Scripts/python.exe verification/test_temporal_order_register.py   # 8/8
  then experiments/exp_temporal_order_before_after_v1.py --mode full   # HARD_PASS 1.000 vs 0.272
  and  experiments/exp_temporal_order_serves_causal_v1.py --mode full   # 1.000 vs 0.000
FILES: experiments/_temporal_order_register.py + exp_temporal_order_{before_after,distance_effect,
serves_causal,extraction_recall}_v1.py + exp_causal_force_dynamics_probe_v1.py;
verification/test_temporal_order_register.py; the problem folder's SOLVED.md + 4 notes. No hdlab/
touched (Q111); shared _temporal_ordering modules untouched.
