---
owner_verdict:
---

# SUBMISSION — register-robust event detection (the reader drops events when the tagger misses the verb)

**Status: SOLVED (awaiting your verdict).** No live-substrate file was changed — everything is proved in
`experiments/` + `verification/` with a proposed default-off wire for the strategy session to land (board Q111).
Set `owner_verdict: DONE` above when you want strategy to integrate.

## In plain language
When the reader meets a real verb its word-tagger mislabels as a noun (common in old or unusual writing — "the lake
PRESENTS an unbroken sheet"), it emits no event and the whole "who did what to whom" for that clause vanishes silently.
A dictionary rule to rescue these floods the text with ~4 fake verbs per sentence. The brain doesn't look verbs up; it
**predicts** the verb slot from the sentence pattern, keeping a graded belief rather than a hard guess. I built a small,
transparent model that combines a few pattern clues the brain uses (how confident the tagger itself is, the surrounding
sentence frame, verb-like word endings, "every clause needs one verb"), trained only on modern text. It rescues about
**90% of the modern misses and 56–80% of the 150-year-old misses — having never seen old text — at under half a fake
verb per sentence** (a random rescuer does far worse, proving it's real). Then, pushing to the *exact* brain-faithful
design, I found the deeper fix: the tagger's belief was a hard max-margin score, not a real probability, so its "graded"
signal was degenerate. Retraining the same tagger with a probability objective (a CRF) gives a properly graded belief
that recovers the old-text misses at **81%** — a big step toward what a competent reader does (~100%).

## What we are submitting here (the parts)
1. **The result: SOLVED** — a register-robust, glass-box, self-supervised predicate detector that raises real-document
   event recall over the live floor, controlled false-verb rate, info-free twin losing, transfers modern→19c with zero
   19c labels. Full write-up + numbers: `SOLVED.md`.
2. **The bar-clearing detector** (`experiments/exp_register_predicate_detector_v1.py`) + its deployable static asset
   (`data/exp_register_predicate_detector_v1/predicate_detector_asset.json`).
3. **The exact brain-foundational upgrade** (`experiments/exp_register_predicate_crf_tagger_v1.py`) + the calibrated CRF
   tagger asset (`data/exp_register_predicate_crf_tagger_v1/crf_tagger.pkl`) — the recommended cue (SOLVED.md §4c).
4. **The rigor + understanding cells:** controls/ablation (`..._controls_v1`), the documented negative
   (`..._detector_v2`), the performance-vs-brain comparison (`..._brain_comparison_v1`), the mechanism ladder
   (`..._ideal_v1`), and the brain-mechanism drill (`BRAIN_MECHANISM_DRILL.md`).
5. **The witness** (`verification/test_register_predicate_detector.py`) — 12/12, recomputes every headline from the
   landed metrics, re-runs no cell.
6. **A proposed default-off wire** (SOLVED.md §6) for strategy to land under Q111 — NOT landed.

## Reverify (one command; re-runs no landed cell)
```
.venv/Scripts/python.exe verification/test_register_predicate_detector.py
```

## Paths to optimization (ordered; SOLVED.md §4c/§5/NEXT-STEPS have the detail)
- **A — land the detector default-off (this submission).** Ship the asset + a new `hdlab/predicate_detector.py`; wire an
  additive `predicate_recall` flag into the reader's event path. Additive-only ⇒ no regression on what it already gets
  right. **Recommended cue = the CRF calibrated posterior** (tied on modern, +0.22 on old text over the simpler version).
- **B — the deeper-fidelity build (named next problem, un-owned): a probability-trained, joint tagger+parser.** The one
  lever that would push old-text recovery from 0.81 toward a competent reader's ~1.0 AND fix the parser's register-brittle
  cue. The prototypes here prove each piece; the refinement this work bought is that it must be *likelihood*-trained, not
  max-margin.
- **C — the meaning hub (north-star P1) for the last residual.** The hardest ~33% of modern misses need top-down
  world-knowledge that no local model (or competent statistical reader) recovers — that's the meaning-hub program, not
  this problem.

## Questions
None blocking. One judgement call at landing: the false-verb-budget threshold is denser on old text than modern, so pick
one conservative threshold or calibrate per register — both are statistically clean; it's a recall-vs-false-verb dial.
