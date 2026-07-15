# exp_dev hand-off -- research: ordinal magnitude coding + composition best-in-class

Filed-by: research sub-agent
Date: 2026-07-14
Trigger: notes/drill_ordinal_magnitude_coding_and_composition_bestinclass_2026-07-14.md
Urgency: MEDIUM -- both anchors are same-harness re-parameterizations of the already-run monotone-vs-modular
ordinal-conjunction test (metabolic-rate 191-animal cluster: modular 0.159 below chance -> monotone equal-wt 0.395
/ learned-wt 0.573), not new mechanism builds. Cheap, decision-relevant, and directly informs whether the encoding
gap (uniform bins) or the combination-rule gap (fixed weights) is the next-order lever.

---

## Pause state

Anchors below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (exact bin-edge formula, confidence-weighting formula, script structure) are to be
authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as
implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: log_compressed_thermometer_bins_ordinal_v1 (cheapest, run FIRST)

Anchor pointer: research note's "Cheap decisive test" section + ranked-shortlist rank 1 + Falsifiable Prediction 1.
Re-run the existing monotone-ordinal-conjunction test (the cell that produced modular 0.159 -> monotone equal-wt
0.395 / learned-wt 0.573 on the metabolic-rate/191-animal cluster) with ONE change: replace uniform-spaced
thermometer bin edges with log-spaced (or empirical-quantile / Weber-scaled) bin edges for the ordinal-level
encoding. Everything else (mechanism, split, FREQ_NULL baseline, must-fail controls ARB/SHUF, seeds) held IDENTICAL
to the already-run cell so the delta isolates the encoding-density question alone.
Substrate-product reading: every biological magnitude axis surveyed (parietal LIP summation coding, prefrontal
labeled-line coding, human IPS fMRI tuning) is log/power-law compressive, never linear-uniform -- this is the one
documented, concrete mismatch between the current crude code and every biological account found. Zero new
mechanism; pure re-parameterization of the bin-edge function.
Tier hint: local or remote_cpu_queue -- CPU-only, reuses the existing harness verbatim apart from the bin-edge
function; should be one of the cheapest cells available.
Why-now: directly closes the loop opened by the prior session's monotone-vs-modular finding (memory file
`project_reasoning_mechanism_improve_additive_map_construction_proof_encoding_lever_2026-07-14.md`, "NEW
NEXT-SESSION #1") by testing the next-order refinement (compression) before committing to the data-generation
follow-up that note also flagged.

Pre-reg bands:
  HARD-PASS: accuracy on the held-out novel-combination split improves by >=0.05 absolute over the current 0.573
  learned-weight baseline (i.e. >=0.62), with must-fail controls (ARB, SHUF) still firing at or below their
  already-measured levels (ARB ~-0.04, SHUF ~-0.06) -- confirms the lift is a genuine encoding improvement, not a
  control-leak artifact.
  MIDDLE-BAND: delta between +0.02 and +0.05 -- real but modest; report as a genuine but small refinement, not a
  headline win.
  HARD-FAIL: delta <0.02 in either direction -- means linear-uniform binning was NOT the active bottleneck; do not
  iterate further bin-edge variants if this fires, and redirect to Anchor 2 or to the data-generation follow-up.

### Anchor 2: reliability_weighted_additive_combination_ordinal_v1 (cheap, bundle alongside Anchor 1 if compute allows)

Anchor pointer: research note's ranked-shortlist rank 2 + Falsifiable Prediction 2. Replace the current fixed
learned non-negative per-constituent weights (`[0.18, 0.97, 44.5, 10.1]` on the metabolic-rate cluster) with
per-instance/per-constituent reliability-scaled weights (e.g. inverse-variance-style gain derived from each
constituent's own estimation noise/calibration variance), keeping the composition additive.
Substrate-product reading: the brain's actual default combiner for multiple magnitude cues is reliability-weighted
LINEAR averaging (Ernst & Banks 2002 Bayesian cue integration, implemented via divisive-normalization circuits) --
not a fixed global weight and not a multiplicative/nonlinear combiner. This keeps the additive backbone that the
ML lit-scan (Xu et al. 2021 extrapolation theory; NALU) also favors for generalizing to novel combinations, while
adding the one missing degree of freedom (per-cue confidence).
Tier hint: local or remote_cpu_queue -- same harness, same data, only the weighting-computation step changes.
Why-now: cheap enough to bundle with Anchor 1 in the same dispatch; resolves whether the fixed-weight combiner or
the raw encoding is the dominant remaining bottleneck via cheap dispatch rather than argument.

Pre-reg bands:
  HARD-PASS: closes >=30% of the CURRENT (learned-weight baseline) failure cases without introducing new failures
  elsewhere -- a net LOCALIZED improvement (check failure-case overlap with baseline directly), not just a global
  average bump.
  MIDDLE-BAND: improves the global average by >=0.02 but does not show clear localization to specific failure
  cases -- report as a real but diffuse gain, flag for follow-up on WHY it's diffuse.
  HARD-FAIL: failure-case overlap with baseline >=90% (no localized improvement) -- means the fixed-weight
  combiner was not the bottleneck; the gap is upstream in the per-constituent encoding, not the combination rule.

---

## Context pointers (file paths, not summaries)

- notes/drill_ordinal_magnitude_coding_and_composition_bestinclass_2026-07-14.md (this hand-off's trigger; full
  ranked shortlist, citations, cross-thread synthesis)
- Memory file (outside repo, session-local memory dir):
  `project_reasoning_mechanism_improve_additive_map_construction_proof_encoding_lever_2026-07-14.md` -- contains
  the exact prior-session numbers (modular 0.159 below chance; monotone equal-wt 0.395; monotone learned-wt 0.573;
  learned weights `[0.18,0.97,44.5,10.1]`; must-fail levels ARB -0.04, SHUF -0.06; "beats-freq margin MODEST
  +0.062, DATA-limited" caveat) that both anchors above hold fixed as the baseline to diff against.
  NOTE: the prior session's harness scripts (`monotonic_code_ordinal_conjunction.py`, `mono_data_vs_code_diag.py`)
  were session-scratchpad files and are NOT present in `d:/AI/hd-instrument/scratchpad/` at time of this hand-off
  -- exp_dev will need to regenerate the 191-animal metabolic-rate-cluster harness fresh (same cluster, same
  FREQ_NULL baseline, same ARB/SHUF must-fail construction) before diffing either anchor against it, rather than
  assuming the prior script is reusable as-is.
- notes/research_sr_compose_close_gap_to_additive_map_2026-07-14.md (sibling drill, independent convergence on
  "keep composition additive, fuse/weight rather than replace with a nonlinear combiner" -- same spirit, different
  mechanism)

---

## Contract section

exp_dev owns: regenerating the 191-animal metabolic-rate cluster harness (baseline reproduction first, THEN the
two diffs), pre-registration file, smoke gate, exact bin-edge / reliability-weighting formula, dispatch via
queue_add.sh, post-ship REMOTE VERIFY, self-test per formula-selftests. This hand-off does not prescribe
implementation details beyond the pre-reg bands above (per [[feedback-no-experiment-design-in-prompts]]).

## Autonomy declaration

Research does not decide dispatch tier, exact bin-edge formula, exact reliability-weighting formula, or code
structure -- those are exp_dev's authored decisions from this hand-off + the cited context. Research's role ends
at supplying the mechanism-level rationale (brain + ML lit), the falsifiable pre-reg bands, and pointers to the
exact prior numbers needed to build without re-deriving context from scratch.
