# exp_dev hand-off -- research: PP-58 isochoric ratio reframing (asymptotic ~4.1, BBP protocol, gate revision)

**Filed:** 2026-06-03 by research sub-agent.

**Trigger:** Research drill notes/research_drill_pp58_isochoric_ratio_reframing_deep_dive_2026-06-03.md delivered three concrete experiment candidates with measurable predictions and HARD-PASS/HARD-FAIL thresholds. BBP calibration test is the cheapest, highest-leverage anchor -- if BBP audit_crit confirmed at ~0.73, ratio gate can be revised to 4.0 and PP-58 advances from MIDDLE to HP-eligible.

**Pause state:** Check data/orchestrator_paused.flag before dispatch. Queue-refill is GATED.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile.

---

## Anchor candidates (rank-ordered; exp_dev picks from these)

### 1. BBP spectral-gap calibration -- audit_crit from eigenspectrum merging

- **Anchor pointer:** notes/research_drill_pp58_isochoric_ratio_reframing_deep_dive_2026-06-03.md, Sub-question (5) Alternative A and Cheap decisive test A.
- **Substrate-product reading:** The Baik-Ben Arous-Peche (BBP) formula predicts sigma_g_audit_crit = 1 - sqrt(alpha) - alpha, which at alpha=0.05 gives 0.726. This closely matches the empirical kappa_3-based audit_crit of 0.75 at N=16384. The BBP criterion measures when the M signal eigenvalues of W merge with the Marchenko-Pastur bulk -- an exact, N-independent, parameter-free threshold. Run W eigenspectrum at varied sigma_g; find the merging point. HARD-PASS: merging in [0.60, 0.85]. HARD-FAIL: merging outside [0.40, 1.0]. If confirmed: BBP protocol replaces kappa_3, gate revision to R>=4.0 is justified, and PP-58 advances from MIDDLE to HP-eligible at N=16384.
- **Tier hint:** Local CPU smoke. Pure spectral measurement (eigenvalue decomposition of W at each sigma_g). Very cheap -- no retrieval loop needed.
- **Why now:** This is the single cheapest test that could unlock PP-58 HP. It requires only W-matrix spectral analysis, not a full retrieval sweep.

### 2. NLO cap_crit multi-alpha survey

- **Anchor pointer:** notes/research_drill_pp58_isochoric_ratio_reframing_deep_dive_2026-06-03.md, Sub-question (2) and Cheap decisive test B.
- **Substrate-product reading:** The cap_crit formula sqrt(1/alpha-1) over-predicts by ~30% at alpha<=0.1 in a way that is N-stable. At alpha=0.2 it is exact. The correction is alpha-dependent with an unknown functional form. Sweeping alpha in {0.05, 0.10, 0.15, 0.20, 0.25, 0.30} at fixed N=8192 and measuring cap_crit would characterize the correction factor C_NLO(alpha). HARD-PASS: exact at alpha=0.2, 25-35% mis at alpha=0.05 -- confirming the alpha-dependent correction. HARD-FAIL: correction is alpha-independent (constant fractional error across alpha). If PASS: a formula for the NLO correction can be fitted, enabling per-alpha deployment contracts.
- **Tier hint:** Remote CPU (6 alpha values, N=8192, retrieval quality sweep). Moderate compute.
- **Why now:** The NLO correction affects all PP-58 product claims that cite cap_crit values. Getting a clean alpha-dependent formula is foundational for deployment specifications.

### 3. Ratio at N=32768 -- asymptotic confirmation

- **Anchor pointer:** notes/research_drill_pp58_isochoric_ratio_reframing_deep_dive_2026-06-03.md, Falsifiable predictions P2 and Follow-on Priority 3.
- **Substrate-product reading:** The N-scale trajectory shows ratio: 3.00 (N=8192) -> 4.00 (N=16384). The BBP asymptote predicts ratio=4.13 at N->infinity. Running N=32768 at alpha=0.05 tests whether the ratio continues to increase (toward 4.1) or plateau (confirming the BBP asymptote). HARD-PASS: ratio in [4.0, 5.0] at N=32768 (approaching BBP limit, not exceeding it). HARD-FAIL: ratio > 5.5 (diverging past BBP, suggesting audit_crit is still decreasing faster than expected) OR ratio < 3.5 (converging downward). If ratio lands in [4.0, 5.0] as predicted: PP-58 N=32768 HP gate met with original 4.0 revised gate, confirming the asymptote.
- **Tier hint:** Remote CPU or GPU (N=32768 is large; 5 seeds; one alpha). Long wall time.
- **Why now:** N=32768 is the extrapolated HP point for the ratio trajectory. Getting this data point closes the "is ratio diverging or plateauing?" question definitively.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_pp58_isochoric_ratio_reframing_deep_dive_2026-06-03.md
- Prior Arrhenius / isochoric drill: d:/AI/hd-instrument/notes/research_drill_arrhenius_paradox_substrate_deep_dive_2026-06-02.md
- PP-58 cap_map entries (cycles 22-25): d:/AI/hd-instrument/notes/substrate_capability_map.md (grep PP-58)
- Empirical data: ratio=3.0 (N=8192), ratio=4.0 (N=16384), cap_crit=3.0 N-stable, audit_crit=0.75 at N=16384
- BBP reference: Baik, Ben Arous, Peche 2005, Annals of Probability 33(5):1643-1697
- Status log: d:/AI/hd-instrument/data/orchestrator_status_log.jsonl (most recent research_delivery entry)

---

## Contract

exp_dev is dispatched with TASK + WHY + CONTRACT + AUTONOMY. exp_dev designs the experiment (N, seeds, queue, thresholds, anchor name). The handoff provides the WHY and the prediction structure. exp_dev does NOT receive inline numerical sweep grids or pre-committed cap_map decisions.

## Autonomy declaration

exp_dev decides: which of the 3 anchors to ship first (or batch), what N and seed count to use, whether smoke vs FULL, which queue tier (A/B/C), anchor names, and ETA. The rank ordering above is a suggestion; exp_dev may reorder based on current queue state and runner availability. Anchor 1 (BBP calibration) is the cheapest unlock path; exp_dev should evaluate whether it can batch anchors 1+2 in a single CPU dispatch.
