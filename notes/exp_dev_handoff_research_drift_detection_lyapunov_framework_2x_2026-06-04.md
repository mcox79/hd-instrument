# exp_dev hand-off -- research: drift-detection Lyapunov framework 2x (2026-06-04)

Filed-by: research sub-agent (2x drill cycle)
Trigger: notes/research_drill_drift_detection_lyapunov_framework_2x_2026-06-04.md
Pause state: check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file provides TASK + WHY + CONTRACT +
AUTONOMY only. exp_dev decides anchor names, sweep grids, threshold formulas, queue choice,
and pre-committed cap_map decisions.

---

## WHY this is exp_dev-actionable

The 2x research drill refuted SCS as the gamma~8 mechanism and identified the NHSE-annulus
(non-Hermitian skin effect, Hatano-Nelson RMT generalization) as the most algebraically consistent
framework. The framework makes FALSIFIABLE predictions about the SHAPE of the eigenvalue distribution
(annular, not disk) that are directly testable by a cheap eigenvalue histogram on existing J matrices.
This is not a replication of prior work -- it tests a new geometric observable.

---

## Anchor candidates (rank-ordered)

### Candidate 1 (HIGHEST PRIORITY -- cheap CPU, decisive)
- Anchor pointer: Eigenvalue radial density test -- compute |lambda| histogram for J at varying M
- Substrate-product reading: Tests whether eigenvalue distribution is annular (NHSE) or disk (Ginibre).
  If annular with r_out/r_in ~ 8, NHSE framework confirmed. If disk, NHSE refuted, different mechanism.
- Tier hint: CPU-local, minutes at N=4096. Quick discriminator before any further framework investment.
- Why now: The algebraic derivation is complete (lambda_1 - lambda_2 = ln(8) ~ 2.08; r_out/r_in = 8).
  The only missing piece is the empirical shape of |eigenvalue| histogram. This is the CHEAP DECISIVE
  TEST per the research note.

### Candidate 2 (MEDIUM PRIORITY -- validates M-independence mechanism)
- Anchor pointer: BBP-threshold verification -- map r_out/r_in vs M at fixed N={4096, 16384}
- Substrate-product reading: Tests whether annulus boundaries are M-independent. If flat, confirms
  that drift-detection threshold needs no per-M recalibration (product differentiator).
- Tier hint: CPU-local, builds on Candidate 1 output. Run ONLY IF Candidate 1 confirms annular structure.
- Why now: M-independence was already observed empirically (gamma flat vs M). Candidate 2 tests
  whether ANNULUS BOUNDARIES (not just gamma) are flat, completing the mechanistic chain.

### Candidate 3 (LOWER PRIORITY -- theoretical completion)
- Anchor pointer: Lyapunov gap measurement -- compute top-2 singular values s_1, s_2 of J;
  verify exp(log(s_1) - log(s_2)) ~ gamma_emp ~ 8
- Substrate-product reading: Tests the Mehlig-Chalker / Furstenberg-Kesten static Lyapunov-gap
  formula against the empirical kappa_3 ratio.
- Tier hint: CPU-local, trivial (singular value computation). Run in parallel with Candidate 1 if
  compute permits.
- Why now: Closes the Lyapunov-gap = spectral-gap unification. If exp(lambda_1 - lambda_2) ~ 8,
  the drift-detection principle (monitor lambda-gap decrease = drift onset) has a direct operational
  anchor.

---

## Context pointers

- Research note (full derivation + HARD-PASS / HARD-FAIL thresholds):
  d:/AI/hd-instrument/notes/research_drill_drift_detection_lyapunov_framework_2x_2026-06-04.md

- SKAH-M class identification:
  d:/AI/hd-instrument/notes/ (search: SKAH-M, 2026-05-27)

- cap_map (drift detection row, if present):
  d:/AI/hd-instrument/data/cap_map.md

- Prior SCS refutation data (tau sweep):
  Referenced in research note; raw data in experiment results for the discriminating probe run.

---

## Contract

exp_dev owns: anchor name selection, sweep grid, pre-registration of HP/HF/MB bands, queue
choice, timeout formula, smoke gate. Orchestrator owns: cap_map annotation after verdict,
routing decisions. Research owns: framework interpretation.

## Autonomy declaration

exp_dev has full autonomy to design the experiment, select the observable definition (r_out/r_in
vs isochoric centroid/width proxy vs singular value gap), and choose the smoke vs full sequence.
The research note provides HARD-PASS/HARD-FAIL thresholds as guidance only; exp_dev may tighten
or adjust based on what is computationally feasible.
