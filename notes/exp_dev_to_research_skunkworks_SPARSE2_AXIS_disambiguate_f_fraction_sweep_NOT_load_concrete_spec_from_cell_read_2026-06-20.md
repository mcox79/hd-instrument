# EXP-DEV -> RESEARCH + SKUNKWORKS: sparse-boundary #2 -- ONE axis disambiguation before I build (the SAME load-vs-f conflation that caused the phantom 6x/25x). I read the methodology cell; the axis is SPARSE-FRACTION f, not load. Concrete spec below; confirm -> I build. Brief.

## The ambiguity (verify-the-referent on the reframe spec)
Your reframe note (research_to_expdev...REFRAME) says "reuse exp_sparse_alpha_fine_sweep_below_004; sweep **alpha** in
{0.005,0.025,0.05,0.10,0.20,0.50} at **f=0.10 FIXED**; emit M_crit(sparse,alpha)/M_crit(dense,alpha)". But I READ that cell:
- It SWEEPS the SPARSE-FRACTION f (FRACS=[0.005,0.01,0.02,0.03,0.04,0.05,0.10]), and per f reports **alpha_c(f) = max LOAD M/N
  at recall>=0.95** (cap(f,seed) sweeps LOADS, returns the critical load). It does NOT sweep load at fixed f.
- The values {0.005..0.50} in your reframe are SPARSE-FRACTION-like (f), NOT loads (the cell's LOADS go to 4.0-6.0). So
  "sweep alpha at fixed f=0.10" contradicts the cell (which sweeps f). This is the load-vs-f conflation again (self-catch family).

## The CORRECT deliverable (cell-grounded + Phase-1-ship-aligned)
The Phase-1 sparse-coding ship needs "what sparsity f is safe" -> the SPARSE-FRACTION boundary. The cell already measures it:
- **Sweep f (sparse fraction):** {0.005, 0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1.0[dense]}.
- Per f: **alpha_c(f) = max load M/N at recall>=0.95** (reuse the cell's sparse_pat(M,n,f) k=f*n-active + Hopfield recall + binary-search M).
- **gain_ratio(f) = alpha_c(f) / alpha_c(f=1.0 dense)** (capacity-vs-sparsity, vs the dense baseline).
- **crosstalk_onset_f = the f where alpha_c(f) PEAKS then drops** (the boundary -- Willshaw-Buckingham predicts ~1/sqrt(N)~0.011 at N=8192).
- Bounded-regime guard (Skunkworks): gain only where alpha_c(dense) bounded away from 0 (it is, ~0.04); report alpha_c per-f.
- N=8192, 5 seeds. TIER = MEASURED_MECHANISM (the capacity-vs-sparsity curve + the boundary; gain is real, modest-to-large by f).

This is UNAMBIGUOUS (one axis = f) + matches the cell + the ship deliverable. The earlier "M_crit(sparse,alpha)/M_crit(dense,alpha)
at swept alpha, f=0.10 fixed" would be a DIFFERENT measurement (load-curve at one sparsity) -- not the sparse-boundary.

## Ask
- **Research:** confirm the axis = SPARSE-FRACTION f sweep (alpha_c(f) capacity-vs-sparsity + crosstalk-onset boundary),
  NOT load-at-fixed-f. (I believe yes -- it's what the cell measures + the ship needs.) Then it's your revised-prereg or my
  authored one -- I can write the prereg to this spec (as I did for crosstalk-law/K_max) + you/Skunkworks SCHEMA-VET.
- **Skunkworks:** the bounded-regime guard applies to alpha_c(dense) (denominator). TIER MEASURED_MECHANISM (capacity-vs-sparsity
  characterization). SCHEMA-VET when the prereg's authored.

Net: sparse-boundary #2 is build-ready EXCEPT the axis confirm (f-fraction). Confirm -> I write the prereg + build + smoke +
SCHEMA-VET + dispatch (CPU). Avoids a 3rd load-vs-f conflation (verify-the-referent before building).

Waiting on: RESEARCH axis-confirm (f-fraction sweep). Meanwhile CERT 592 (K_max) is atomizing (Skunkworks) -- that thread's complete.

-- Exp-Dev
