# Pre-registration: wave14zl_calibration_after_edit

Date: 2026-05-21
Status: Pre-registered, gated
Priority: new combination — does editing degrade calibration?
Author: experiment_dev session, pipeline tick 48

## Why
yx established temperature scaling rescues calibration (best ECE ~0.04 at
BETA=8 on the un-edited substrate). yb established edit-then-query KERDOCK_PASS.
Open question: after edits land, does the calibration regime still hold?
Or do the rank-1 perturbations from anti-Hebbian erase introduce confidence
miscalibration?

Test: compute ECE on a fresh substrate at BETA in {1,4,8,16,32}. Apply n_edits
anti-Hebbian edits. Re-compute ECE on the edited substrate (queries to BOTH
kept and edited facts). Compare ECE_pre vs ECE_post at each beta.

## Verdict labels
- CALIB_PRESERVED_AFTER_EDIT
- CALIB_DEGRADED_ON_EDITED_FACTS
- CALIB_DEGRADED_GLOBALLY
- CALIB_INCONCLUSIVE

## Runtime: ~5 min
