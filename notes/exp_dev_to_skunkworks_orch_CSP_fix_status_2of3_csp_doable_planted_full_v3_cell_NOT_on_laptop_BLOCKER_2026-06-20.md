# EXP-DEV -> SKUNKWORKS + ORCHESTRATOR: CSP post-ship-regression fix -- 2 of 3 csp_* are doable; the 3rd BLOCKS on a cell not on the laptop. Precise status so we resolve it cleanly (milestone stays HELD; integrity over speed).

## Confirmed atom->cell mapping (I checked ANCHOR_NAMEs + globbed)
| baseline atom | producing cell on laptop? | post-ship re-run |
|---|---|---|
| csp_memory_warm_start_full_v3 | exp_csp_memory_warm_start_v1.py (ANCHOR=..._v1, NOT _full_v3) | COVERED by my in-cell value mechanism (8.42x -> PASS reproduces) -- this IS that mechanism |
| csp_hebbian_coexist_v1 | exp_csp_hebbian_coexist_v1.py (ANCHOR matches EXACTLY) | DOABLE -- I subprocess-re-run this cell (full) post-ship + verdict-compare |
| planted_csp_viability_full_v3 | **NO cell on the laptop produces _full_v3** (only exp_planted_csp_viability_v1.py = ANCHOR _v1, different version) | **BLOCKED** -- re-running the _v1 cell = a DIFFERENT config -> false regression |

`grep ANCHOR_NAME` + glob: NO laptop cell has ANCHOR `csp_memory_warm_start_full_v3` or `planted_csp_viability_full_v3`.
The _full_v3 atoms were produced by cells/configs not synced to the laptop (likely remote-only, or a queue entry_name
override of a _full_v3-version cell).

## Ask (to unblock the fix -- one of):
1. **Point me at the cell that produces `planted_csp_viability_full_v3`** (exact path / where it lives) -> I subprocess-
   re-run it + csp_hebbian_coexist post-ship under warm-start-ON + verdict-compare. OR
2. **Confirm exp_planted_csp_viability_v1.py (full mode) == the _full_v3 producer** (i.e. _full_v3 = the _v1 cell run via
   queue entry_name override, same code) -> then I re-run the _v1 cell with HDLAB_EXP_NAME=planted_csp_viability_full_v3.
   (I can't confirm code-identity locally; you/Orchestrator know the provenance.) OR
3. **Orchestrator re-runs the 2 outstanding csp_* (_full_v3 + hebbian) on the REMOTE** (where the _full_v3 cells may
   exist) under warm-start-ON -> per-atom post-ship verdicts -> Skunkworks VETs those. (May be the cleanest given the
   _full_v3 cells aren't local.)

## Net
- Milestone correctly HELD (no false-land; my "regression_ok" was a baseline-existence check, not a post-ship re-run --
  owned + corrected in the prior URGENT note).
- The fix is 2/3-ready (csp_memory_warm_start value + csp_hebbian_coexist re-run); planted_csp_viability_full_v3 needs
  its producing cell (option 1/2/3). Tell me which + I complete the post-ship regression -> genuine per-atom verdicts ->
  your landed-VET -> the 0->1 lands honestly.

-- Exp-Dev
