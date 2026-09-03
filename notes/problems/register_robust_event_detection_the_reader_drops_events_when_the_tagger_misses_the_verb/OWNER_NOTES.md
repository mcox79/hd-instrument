---
owner_verdict: DONE
---

SOLVED — register_robust_event_detection_the_reader_drops_events_when_the_tagger_misses_the_verb (opus 4.8 solver)

Full write-up: notes/problems/register_robust_event_detection_the_reader_drops_events_when_the_tagger_misses_the_verb/
  {SOLVED.md, OWNER_NOTES.md, BRAIN_MECHANISM_DRILL.md}
Reverify (re-runs no landed cell): .venv/Scripts/python.exe verification/test_register_predicate_detector.py   # 12/12

RESULT: a register-robust, glass-box, self-supervised PREDICATE detector — a learned noisy-channel combiner over
register-invariant cues (tagger verb-margin as likelihood × frame/morphology/one-verb-per-clause competition as prior),
trained on MODERN auto-labels, NO LLM. Recovers tagger-dropped real verbs (the whole class of silently-lost events)
@ FP<=0.5 false-verbs/sent, info-free twin losing CI-separated:
  MODERN (UD-EWT test, 5-fold CV)      0.899   Δvs-twin +0.333 CI[+0.21,+0.46]
  19c TRANSFER (LitBank, 0 19c labels) 0.5625  Δvs-twin +0.539 CI[+0.44,+0.64]
Crosses the parent's structure-only modern wall (0.16 → 0.899). No-regression by construction (additive-only:
promotes only dropped tokens; existing detections byte-identical). Heuristic baseline was 3.72 false-verbs/sent.

EXACT brain-foundational architecture, prototyped (SOLVED.md §4c): the mechanism-diff is max-margin-vs-graded (drill,
PINNED). Retraining the SAME tagger with a likelihood objective (a CRF; same features/data) gives a CALIBRATED posterior
that recovers 19c at 0.806 (vs 0.582 max-margin), modern 0.955 — +0.224 of the fidelity gap closed with one principled
cue; argmax recall tied (0.954 vs 0.956). Joint parse-coherence helps modern (→0.966) but is register-brittle on 19c
(parser also modern-trained). Performance-vs-brain (spaCy oracle, reference-only): a competent reader recovers ~100% of
the 19c drops (fidelity gap, recoverable), and ~33% of MODERN drops are the genuine ceiling (needs top-down meaning).

LAND (strategy, Q111, default-off, witnessed):
  1. Ship asset(s): data/exp_register_predicate_detector_v1/predicate_detector_asset.json (+ the calibrated CRF tagger
     data/exp_register_predicate_crf_tagger_v1/crf_tagger.pkl — the RECOMMENDED cue, §4c).
  2. New organ hdlab/predicate_detector.py (promote experiments/exp_register_predicate_detector_v1 feats + the asset;
     recommended category cue = logit(CRF P(VERB))).
  3. Wire an ADDITIVE `predicate_recall` flag into situation_reader's tense_agnostic event path (default OFF =
     byte-identical); calibrate the false-verb-budget threshold per register. Fold the AUDIT UPDATE into
     BRAIN_FOUNDATIONAL_AUDIT.md §2b.
  DO NOT land: a heuristic verbhood override (refuted, 3.72 FP) or the parent's structure-only post-hoc override
  (0.16 modern). v2 morphological-gate + imperative cue are a documented NEGATIVE (don't land).

NEXT PROBLEMS (not this one): (B) a LIKELIHOOD-trained, JOINT-DECODED tagger+parser (Bohnet-Nivre 2012 with a CRF
objective — the refinement this work bought over the parent's §0i) — the lever that pushes 19c past 0.806 toward ~1.0
AND fixes the parser's register-brittle cue. (C) the meaning hub (north-star P1) for the ~33% modern semantic ceiling.
