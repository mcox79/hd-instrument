---
owner_verdict: DONE
---

════════════════════════════════════════════════════════════════════════════════════════════════════
SOLVER SUBMISSION — the_forward_prediction_organ_is_inert_wire_its_surprisal_into_a_live_decision   STATUS: SOLVED (WIP → owner DONE)
hdlab/ UNTOUCHED (strategy lands the diff, Q111). Both required gates MET with power + witness; the wall
decomposed AND built-across 7 ways to an evidence-forced terminus; brain-led (4 research drills). NO LLM/spaCy.
REVERIFY (recomputes every headline FROM SOURCE through the LIVE SituationReader.read()):
  .venv/Scripts/python.exe verification/test_forward_prediction_live_decision_organ.py   -> ALL 8 CHECKS PASS
  .venv/Scripts/python.exe tools/problem_ledger.py --check                               -> malformed/incomplete: 0
════════════════════════════════════════════════════════════════════════════════════════════════════
ASKED: hdlab/predictive_reader (the N400 forward-prediction organ — verb+role pre-activates the expected
  argument's grounded features; surprisal = -log P) was held-out-validated but a PURE INERT ISLAND (never
  computed on any live path). Compute it LIVE through read(), prove it is decision-relevant (predicts the
  reader's OWN who-did-what errors, shuffled twin losing), drive ONE brain-faithful decision that improves the
  reader — or enumerate why. (A rigorous negative is a full PASS.)

BRAIN METHOD (PINNED via 4 dispatched drills, not guessed): comprehension runs TWO dissociable streams — the
  N400 thematic-fit stream (surprisal; Hale/Levy/Michaelov) and the LIFG/semantic-P600 STRUCTURAL-conflict
  stream (Thompson-Schill; Van Herten & Kolk). Surprisal is a RISK FLAG not a verdict (OUR-INVENTION; closest
  pin = the P600 conflict monitor). The brain's most-evidenced ACTION is re-read/withhold, NOT auto-revise
  (revise-toward-plausible IS the good-enough error — Ferreira/Gibson). English who-did-what is WORD-ORDER
  dominant (MacWhinney Competition Model).

BUILT (all glass-box, in-substrate parse+coref, NO LLM): a live driver feeding predictive_reader on the reader's
  OWN patient bindings through read() (QA-SRL nominals auto-marked; role-capable reader). Population = QA-SRL v2
  dev+test patient items (MODERN text) + a 19c LitBank narrative slice.

RESULT — BAR MET (n=2606, through the LIVE read(), reader error-rate 0.40):
  * INFORMATIVE (PASS): live per-argument surprisal predicts the reader's OWN who-did-what errors AUC 0.651
    [0.630,0.672] CI-sep over chance; SHUFFLE-surprisal twin p95 0.519 (loses); point-biserial 0.263.
  * ACTIONABLE via surprisal-ABSTAIN (PASS): committed accuracy at 80% coverage 0.633 vs random-abstain twin
    0.598 -> margin +0.035 [+0.022,+0.050] CI-sep; committed acc rises 0.62->0.70 as coverage drops.
  * GRADED SIGNATURE (precision-weighting, CI-sep at power): surprisal->error AUC steeper for SHARP verbs —
    top-precision-tercile 0.684 vs bottom 0.628, +0.056 [+0.005,+0.110].
  * GENERALIZES to 19c LitBank narrative: AUC 0.624 [0.556,0.690] (n=311), twin p95 0.562 (loses) — the
    meaning-level prediction is not a modern-vocabulary artifact.

THE WALL — decomposed AND built-across (the ambitious RE-SELECT/revise decision FAILS; 7 probes converge):
  * Auto-revise fails: delta -0.002 [-0.009,+0.004]; even the non-canonical stratum (its strongest shot) +0.003
    [-0.010,+0.016]. Enumerated negative, then drilled to the mechanism.
  * ESTIMATOR class (drill 2): an EXEMPLAR store beats the prototype centroid +0.081 [+0.061,+0.102] CI-sep
    (0.364->0.445) — but still below the parse (0.596).
  * DIMENSIONALITY ruled out: a fair 1024-d distributional space (RI, 40k vocab) is WORSE than 12-d grounded;
    taxonomic (symmetric-pattern) beats topical (window) but none beats grounded or the parse.
  * AGENT-conditioning (drill 3): re-selection null (real ~ random-agent twin); the FLAG only directional
    (+0.008..0.015, not CI-sep) — agent-extraction noise hurts.
  * COMPETITION/CONFUSABILITY (drill 4 = LIFG/P600 retrieval interference): the brain-faithful confusability
    signal FAILS its gate (AUC 0.47 on the low-surprisal subset, below null, worse than the crude count).
  * DECISIVE TEST: the reader's wrong pick is NO more similar to the gold than a random competitor (0.221 vs
    0.229) => the errors are STRUCTURAL (wrong entity), NOT semantic near-twins — which is WHY every semantic
    signal fails.
  * PARSE-DISAGREEMENT (structural flag): FAILS in the OPPOSITE direction — disagree->20% error vs agree->44%.
    So the errors are SILENT POSITIONAL DEFAULTS: the reader is CONFIDENTLY wrong; NO self-consistency/
    plausibility signal can flag them. TERMINUS: the ~half of errors surprisal misses are parse-COVERAGE
    failures whose only lever is a BETTER PARSER (the p2 predictive parser).

CONTROLS: (1) shuffle-surprisal twin (R=500, p95 0.519). (2) random same-rate abstention twin (flat 0.60).
  (3) info-free random-adopt reanalysis twin. (4) non-canonical stratum (reanalysis' strongest shot). (5) LitBank
  corpus-age slice. (6) random-agent twin (isolates the agent signal). (7) shuffle-twin nulls on every probe.
  (8) reader's-own vs QA-SRL-gold agent. Every margin reports CI half-width + null p95.

KEY REALIZATIONS: (1) surprisal is a RISK FLAG, not a verdict — parse-as-truth==null; frame it honestly.
  (2) the drill-recommended ACTION (abstain/re-read) works; the good-enough action (auto-revise) fails — proving
  it wrong is the point. (3) DIAGNOSE a negative before labeling it: I first blamed "the coarse grounded space,"
  the decomposition caught that it's actually that ~half the errors are structural. (4) RULE OUT the cheap
  hypothesis: richer dimensions made it WORSE; the crude count beat the brain-faithful confusability — the fair
  test corrected the brain-faithful prediction. (5) the whole exploration CONVERGES: a two-stream account (N400
  thematic flag WORKS; LIFG/P600 structural errors are the parser's, not a flag's) — English who-did-what is
  structural, plausibility is a FLAG-ONLY tool.

AUDIT UPDATE (fold into BRAIN_FOUNDATIONAL_AUDIT.md §2b): predictive_reader is no longer inert-in-evidence —
  validated LIVE as an error-RISK flag + a working abstain decision (AUC 0.651 CI-sep, generalizes to 19c
  narrative), with precision-weighted diagnosticity. NEW PINNED-AND-MEASURED: two dissociable streams (N400
  thematic-fit flag + LIFG/P600 structural conflict); the reader binds STRUCTURALLY, so its residual errors are
  silent parse-coverage failures (parser-recall-bound), unflaggable by any plausibility/self-consistency signal.
  Correct the "island" line to "island in code; validated LIVE as a flag/abstain signal, proposed default-off wire."

PROPOSED hdlab CHANGE (Q111 — strategy lands): default-off `predict_surprisal` flag on SituationReader
  (byte-identical when off, the causation/timeline additive pattern). ON: read() computes per-argument surprisal
  among the sentence's candidate nominals via the promoted predictive_reader, exposes it as additive EventRecord
  metadata (patient_surprisal, precision), and an optional `surprisal_abstain_tau` marks the highest-surprisal
  bindings low_confidence (the validated decision). NO spaCy/LLM. First live node of the prediction-error
  hierarchy. Do NOT wire auto-revision (it fails). (adjacent bug to fix: hdlab/frame_induction.is_passive_real
  lacks an upper bound on range(lo, v_idx) -> IndexError on ~1/1300 sentences; one-line fix.)

FILES: experiments/_forward_prediction_live.py; experiments/exp_forward_prediction_live_decision_v1.py;
  verification/test_forward_prediction_live_decision_organ.py (8/8); 6 probe cells (reselector / richer_space /
  agent_conditioned_reselector / agent_conditioned_surprisal / flag_negative_diagnosis / two_factor_flag /
  confusability_flag / parse_disagreement_flag); data/forward_prediction_*/metrics.json; 4 research drills +
  SOLVED.md in the problem folder. hdlab/ UNTOUCHED.

TLDR: We had built the brain's "guess the next word's meaning and notice when it's wrong" machine and left it
  switched off. I switched it on: as the reader works out who-did-what on real (and 200-year-old) text, it now
  flags where the reader gets it wrong ~as well as the brain's N400 does, and holding back the flagged answers
  makes the reader measurably more accurate. Then I chased the more ambitious move — using it to FIX the answer —
  and it fails; I drilled that all the way down (4 literature drills, 7 experiments) and got a clean answer: the
  reader's remaining mistakes are STRUCTURAL — it confidently grabs the grammatically-default entity when it
  shouldn't — so no meaning-based or self-doubt signal can catch them; only a better sentence parser can. The
  forward-prediction organ's real job (flagging the implausible mistakes) works and is done; the structural half
  is the parser's, which was already the named next project. QUESTIONS: none. NEXT: land the default-off flag
  (fused verb+agent surprisal) + abstain; the p2 predictive parser is the sole remaining lever, filed separately.
════════════════════════════════════════════════════════════════════════════════════════════════════
