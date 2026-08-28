---
owner_verdict: DONE
---

SUBMISSION — SOLVER RESULT for problem: no_automatic_reliability_signal_reaches_the_source_oracle
STATUS: SOLVED  (by a DEEPER brain-foundational mechanism than the brief proposed — the brief's own
                 mechanism refuted, then the real bottleneck was localised and fixed)
LEDGER: python tools/problem_ledger.py --check  ->  malformed/incomplete: 0
INTEGRATION: a NEW hippocampal organ is PROPOSED, not landed (board Q111 — strategy lands it).

REVERIFY (three scaffold-free witnesses; each rebuilds from the live instrument, reads no artifact):
    .venv/Scripts/python.exe verification/test_dg_ca3_recollection_self_certifies.py        <- THE SOLUTION
    .venv/Scripts/python.exe verification/test_reliability_geometry_gate_diagnosis.py       <- brief's mechanism refuted
    .venv/Scripts/python.exe verification/test_pattern_separated_recollection_not_self_certifying.py

================================================================================
THE BAR (verbatim from PROBLEM.md §7)
================================================================================
"On the source-selection / recall task (same population and floor as the oracle 0.408 / counting 0.324):
a per-item reliability estimator derived from a source's OWN response geometry must beat the fixed-weight
blend AND plain counting CI-separated, moving toward the oracle, with the mandated info-free twin
(per-item reliability PERMUTED across items) LOSING CI-separated. HOW WE WOULD KNOW IT FAILED, and this
is a full PASS for the brief: the geometry signal is ALSO inert (permuted twin reproduces it) => per-item
reliability is not recoverable from our sources at this scale; recommend a fixed blend and name what a
recoverable signal would require."

The brief authorises solving it a DIFFERENT way. That is what happened: the OWN-RESPONSE-GEOMETRY route
refuted, and the REAL problem underneath it was solved with a mechanism of my choosing (the brain's).

================================================================================
THE ANSWER (recall instrument = the bar's population; n=5490; F_COUNT1 reproduces at 0.3242)
================================================================================
An AUTOMATIC per-item reliability signal that beats the counting floor CI-separated EXISTS. It is the
CA3 completion confidence of a dentate-gyrus PATTERN-SEPARATED episodic store. The chain:

  1. The brief's mechanism (read reliability off the EXISTING dense sources' output geometry) — REFUTED.
  2. Built the deeper brain mechanism (pattern-separated recollection). Word-overlap version — NOT
     self-certifying at ANY strictness. This LOCALISED the bottleneck: not the reliability signal, not
     the arbitration machinery — the EPISODIC STORE itself (no separable, completable traces).
  3. Rebuilt the store with the hippocampus's real circuit (DG separation + CA3 completion). Recollection
     now SELF-CERTIFIES and dual-process routing BEATS THE FLOOR. Bar met.

================================================================================
THE SOLUTION — DG/CA3 (exp_dg_ca3_recollection_gate_v1.py), full scale, TWO projection seeds
================================================================================
Mechanism (glass-box, no LLM): idf-weighted word vector -> fixed random EXPANSIVE projection -> k-WTA
(~2% active) = dentate-gyrus PATTERN SEPARATION (orthogonalises episodes sharing frequent words). Each
episode is one sparse code; a cue is encoded the same way and COMPLETED to the nearest stored code (CA3);
the completion overlap is an INTRINSIC confidence. Dual-process routing: trust recollection when it fires
confidently, else PMI familiarity. No estimator, no labels.

  scorer = lemma hit@1, held-out cues, n=5490.  floor F_COUNT1=0.3242 CI[0.3115,0.3366] (gate UB 0.3366).
  oracle ceiling = ORACLE_UNION 0.4091 CI[0.3962,0.4220] (reproduces the store SOLVED's 0.4082).

  firing cov | DG/CA3 precision when fired | familiarity same items | ROUTE acc | route-floor (CI)
     2%      |     0.936 / 0.955           |    0.518 / 0.418        |   0.333   | +0.008 [+0.006,+0.011]
     5%      |     0.938 / 0.934           |    0.533 / 0.493        |   0.344   | +0.020 [+0.017,+0.024]
    10%      |     0.891 / 0.893           |    0.483 / 0.485        |  *0.365*  | *+0.041 [+0.036,+0.046]*
    20%      |     0.539 / 0.533           |    0.341 / 0.353        |   0.364   | +0.040 [+0.034,+0.046]
   word-overlap (old), any cov: precision 0.07-0.16, BELOW familiarity, route < floor.

HEADLINE: dual-process route at 10% coverage = 0.3650, +0.0408 over the floor, CI [+0.0355,+0.0461] ->
clears the floor UPPER bound 0.3366 CI-separated, capturing ~half the oracle headroom (0.324 -> 0.365 ->
0.404). Recollection OVERALL is still weak (hit@1 0.179); the entire win is that its confidence is now
TRUSTWORTHY, so trusting it only when confident adds signal instead of noise.

CONTROLS (all bind, both projection seeds):
  - SELF-CERTIFICATION vs BASELINE: DG/CA3 top-5% precision 0.938/0.934 vs familiarity 0.533/0.493 on the
    SAME items; word-overlap recollection self-certifies at NONE -> the win is pattern separation, not
    recollection-in-general.
  - INFO-FREE TWIN (shuffle the firing flag across items) LOSES CI-separated: +0.028 [+0.024,+0.033] and
    +0.031 [+0.026,+0.036] -> the firing carries genuine per-item info, not item-difficulty base rate.
  - SCRAMBLE-CONTENT (cue from a deranged donor lemma) collapses confident precision 0.94 -> 0.00 -> the
    confidence is genuine cue<->target completion, NOT an artifact / leak.
  - ROBUSTNESS: two independent random DG projection seeds give the same result.
  - MECHANISM self-test PASSES (DG k-WTA drops episode overlap raw jaccard 0.77 -> 0.05; idf-weighted
    partial cue completes to the right episode 11 vs 0).
  - FLOOR reproduced to the digit; gated on its UPPER bound.

================================================================================
THE DIAGNOSIS THAT LED HERE (also landed, also witnessed)
================================================================================
A. BRIEF'S MECHANISM REFUTED (exp_reliability_geometry_gate_v1 / _meaning_v1):
   A learned NO-LEAK gate over own-response geometry (self-consistency [the pinned untried gain-variability
   signal], entropy, margin, participation-ratio, evidence) = ARB_ROUTE 0.3281 CI[0.3153,0.3403] — does
   NOT clear the floor UB CI-separated. Own-geometry reads the COMPETENT source's reliability (COUNT1
   entropy AUC 0.708, self-consistency 0.658; single-shot peak-z here is also 0.647) but NOT a weak
   source's rare unique wins (REC/MULT 0.40-0.65), which is where the oracle's reserve lives. On the
   comparable-source MEANING instrument the signal is fully INERT (arbiter 0.3000 vs its twin 0.3014;
   coverage predicts SEEN at 0.81 but which-source-wins at only 0.57).
B. BOTTLENECK LOCALISED (exp_pattern_separated_recollection_gate_v1):
   Word-overlap recollection is NOT self-certifying — at EVERY firing strictness (2%-100%) its
   precision-when-fired (0.05-0.12) is BELOW familiarity on the same items (0.22-0.34); its most confident
   2% are right 0.073 where familiarity is 0.264. So the weak source is a broken COMPLETER, not a broken
   reliability read-out. Root cause = the episodic store's lack of separable traces. (This is exactly the
   brief's "geometry inert" full-PASS-by-refutation on the read-out branch — but it pointed one level
   deeper, to the store, which is what got fixed.)

================================================================================
BRAIN-FOUNDATIONAL LABELLING
================================================================================
PINNED: dual-process recognition (Yonelinas; Diana/Yonelinas/Ranganath); Complementary Learning Systems
(McClelland 1995; O'Reilly); dentate-gyrus pattern separation + CA3 attractor completion (Treves-Rolls;
Yassa-Stark); reliability-weighted cue combination (Ernst-Banks; Ma; Kording). The COMPUTATION (DG
orthogonalisation + CA3 completion) is copied exactly.
OUR-INVENTION-UNDER-TEST: (a) that per-item reliability read from EXISTING dense sources' output geometry
reaches the oracle — REFUTED. (b) that a DG(k-WTA)+CA3 completer's confidence self-certifies and clears
the floor — CONFIRMED. Parameters SWEPT/reported not adopted: DG dim D=2048, sparsity k~2%, one-step
completion, fixed random projection (all flagged as tunable, not claimed optimal).

================================================================================
KEY REALIZATIONS (the enabling moves)
================================================================================
1. When a reliability SIGNAL is missing, first check whether the thing it would certify actually works.
   Building the mechanism (not just naming it) revealed the weak source is a broken COMPLETER — there was
   nothing reliable to certify. No arbitration-side cleverness could have reached this.
2. COPY THE BRAIN'S COMPUTATION EXACTLY. Word-overlap (the convenient tool) never self-certifies; the SAME
   episodes read through DG separation + CA3 completion (the brain's operation) self-certify at 0.94 and
   beat the floor. Only the representation changed — from convenient to brain-faithful.
3. SCOPE EVERY NUMBER TO ITS POPULATION — a witness caught me comparing a recall-instrument AUC (0.71) to
   a meaning-instrument refuted peak-z (0.49) as if within-population. Recomputing on the same population
   dissolved a false headline. No number crosses instruments.
4. The INFO-FREE TWIN and the SCRAMBLE control, not the AUC, told the truth at each stage (they killed a
   plausible-looking geometry signal on the meaning instrument, and they certified the DG/CA3 win).

================================================================================
WHAT I DID NOT ESTABLISH (withdraw first if wrong)
================================================================================
- The DG/CA3 route captures ~HALF the oracle headroom (0.365 vs 0.404), NOT the full oracle. I claim
  "the automatic signal exists / beats the floor CI-separated", not "reaches the oracle".
- The win is coverage-limited (~10-20% of items — those whose held-out cue closely matches a stored
  episode). More episodic reading should raise coverage (CLS synthetic control jumps to 0.89 with a clean
  trace); I did NOT run larger corpora here.
- The DG/CA3 store is a PROPOSED organ, not landed. One-step CA3 (nearest code), fixed random projection —
  I withdraw "this exact implementation is optimal" before the core claim that pattern separation makes
  recollection self-certifying.

================================================================================
FOR THE STRATEGY SESSION (you own hdlab + integration, board Q111)
================================================================================
1. Re-verify the three witnesses above (the solution one prints route 0.3650 > floor UB 0.3366,
   self-cert 0.938 vs 0.533, scramble -> 0.00).
2. INTEGRATE the DG/CA3 episodic completer as a NEW hippocampal organ: DG expansive random projection +
   k-WTA(~2%) over idf-weighted episode/cue vectors -> CA3 nearest-code completion (overlap = confidence)
   -> intrinsic dual-process gating (recollection when confident, else PMI familiarity). This ANSWERS
   board Q118 ("where does a selection signal come from WITHOUT labels"): it is CA3 completion confidence.
3. SCALE WITH READING. The headroom captured grows with episodic coverage; this is the SAME episodic tier
   the reader_meaning_channel / CLS three-tier design needs, so read-more pays twice. This is the lever
   for higher performance — NOT a better gate.
4. Record the closures: (a) per-item reliability from own-response geometry does NOT reach the oracle
   (real-but-insufficient on recall, inert on meaning) — do not re-open; (b) word-overlap recollection is
   not self-certifying — the bottleneck was the store, now fixed. My earlier "external evidence estimator"
   proposal is SUBSUMED by CA3 completion (a match-to-store evidence signal, done the brain's way).
5. LABEL CALL (the only soft point): I filed SOLVED because an automatic signal that clears the bar now
   exists and reproduces with all controls binding. A reviewer preferring "clears the bar but not yet
   full-oracle / not yet integrated" could file STRONG-but-open. Numbers and controls are unambiguous.

FILES
  experiments/exp_reliability_geometry_gate_v1.py          (brief's mechanism, recall — refuted)
  experiments/exp_reliability_geometry_gate_meaning_v1.py  (brief's mechanism, meaning — inert)
  experiments/exp_pattern_separated_recollection_gate_v1.py(word-overlap recollection — not self-certifying)
  experiments/exp_dg_ca3_recollection_gate_v1.py           (THE SOLUTION — DG separation + CA3 completion)
  verification/test_dg_ca3_recollection_self_certifies.py                  (solution witness)
  verification/test_reliability_geometry_gate_diagnosis.py                 (diagnosis witness)
  verification/test_pattern_separated_recollection_not_self_certifying.py  (diagnosis witness)
  data/exp_reliability_geometry_gate_v1|_meaning_v1|_pattern_separated_recollection_gate_v1|_dg_ca3_recollection_gate_v1/metrics.json

DO NOT QUOTE / CAUTIONS
  - Do NOT quote the DG/CA3 route (0.365) as reaching the oracle — it captures ~half the headroom.
  - Do NOT quote DG/CA3 recollection's OVERALL hit@1 (0.179) as a capability — it is a weak read-out; the
    win is its CONFIDENCE, used for routing.
  - No number crosses the recall and meaning instruments (refuted peak-z 0.49 is meaning-only; recall
    peak-z is 0.65).
  - The oracle (0.4091) SEES the answers — it proves headroom, not an achievable capability.

================================================================================
PLAIN-LANGUAGE TLDR
================================================================================
The system couldn't tell which of its memory sources to trust on a given question. It looked like a
missing "trust" signal. The real problem was deeper: its memory-recall channel was broken — it was
confidently wrong. We fixed it by building memory the way the hippocampus does: spread each memory into a
sparse, distinctive pattern so similar memories stop blurring together, then let a partial clue snap onto
the closest stored memory. Now recall is trustworthy — when it answers confidently it's right about 94% of
the time (vs ~50% for plain word-counting on those same questions), and a system that trusts recall only
when it's confident beats plain word-counting for the first time, closing about half the gap to a cheating
oracle. Same data, same task — the only change was building the memory the brain's way instead of the
convenient way. The path to more: read much more (so more questions have a distinctive stored memory to
recall), not a cleverer trust-signal.

QUESTIONS: none (one soft label call noted above).
NEXT STEPS: integrate the DG/CA3 organ; scale episodic reading to push coverage past 20%; optionally
iterate CA3 (multi-step attractor) and a learned DG projection for higher per-item precision.
