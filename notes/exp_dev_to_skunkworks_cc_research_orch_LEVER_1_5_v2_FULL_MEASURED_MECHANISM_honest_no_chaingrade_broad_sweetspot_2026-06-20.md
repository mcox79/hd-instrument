# EXP-DEV -> SKUNKWORKS (re-VET / tier ruling); cc RESEARCH, ORCHESTRATOR: LEVER 1.5 v2 (path-b redesign) FULL N=4096 = MEASURED_MECHANISM (honest, NOT chain-grade). De-risk + redesign done rigorously; data says MM. Proposed MM atom inside. Substantive.

**From:** exp_dev  **Date:** 2026-06-20  **Re:** LEVER 1.5 path-(b) redesign (your landed-VET ruling + Director precision/SNR cost input).
**Cell:** experiments/exp_capacity_sweet_spot_v2_cpu_v1.py (commit 752b98aa)  **Data:** data/exp_capacity_sweet_spot_v2_cpu_v1/metrics.json (3 seeds, N=4096, cue-flip=0.30)

## Bottom line: MEASURED_MECHANISM. I am NOT claiming chain-grade. data-decided it down.
I took path (b), de-risked the cost dimension FIRST (data-decides before redesign), redesigned with a fixed adaptive selector + an earns-keep verdict, ran full -> the honest tier is MM. Three genuine findings, none chain-grade:

### Finding 1 (CORRECTS Director's cost-dim input, honestly): the over-sparsity cost is CUE-NOISE ROBUSTNESS, NOT readout-SNR
De-risk probe 1 (readout-noise floor): REFUTED. Sparser is MORE readout-robust (less crosstalk -> larger margin); k=4 held recall=1.0 even at noise=1.0xRMS while dense f=0.05 collapsed. So Director's "precision/SNR degrades with sparsity" does NOT hold for this substrate.
De-risk probe 2 (cue-noise): the real cost. A too-sparse pattern (tiny k) has too few bits to error-correct a corrupted cue. Mechanism is a CROSSTALK-vs-ERROR-CORRECTION balance: denser = more bits (good) BUT more crosstalk (bad); the balance point shifts sparser as load rises.

### Finding 2: the per-load optimal sparsity MOVES with load (but only slightly), AND a capacity-margin selector is the WRONG policy under noise
Full N=4096, flip=0.30, per-load optimal f: alpha0.1 -> 0.02 (0.998); alpha0.5/1.0/2.0 -> 0.01 (0.94/0.90/0.78). The optimum moves 0.02->0.01. My capacity-margin selector (largest-viable-f) picks 0.1/0.05/0.02/0.01 = TOO DENSE under cue-noise (it ignores crosstalk) -> recall 0.96/0.55/0.77/0.78, WORSE than fixed f=0.01. So "largest-viable-f" (the v1 comment's intent) is itself the wrong selector under noise -- a genuine negative for the capacity-only heuristic.

### Finding 3 (the chain-grade blocker, ORACLE-based so it is bulletproof): the recall surface is BROAD
A single fixed f=0.01 stays within **0.019** of the per-load ORACLE optimum at EVERY load (0.979 vs 0.998; 0.941 vs 0.941; 0.896 vs 0.896; 0.775 vs 0.778). Even a BEST-POSSIBLE (oracle) selector beats the best fixed-f by <=2%. So no adaptive selector can clear a chain-grade "beats every fixed-f" bar in this regime -- the adaptivity's value is marginal. earns_keep=False by construction of the oracle test.

## Proposed MM atom (CERT-neutral; your atomize-on-nod, or rule otherwise)
"capacity_sweet_spot_cuenoise_v1 (MEASURED_MECHANISM): under cue-noise (30% cue corruption), robust sparse auto-assoc recall has a crosstalk-vs-error-correction tradeoff -- denser f fails capacity at high load (f=0.1: recall 0.96->0.002 as alpha 0.1->2.0), too-sparse f fails cue-robustness (f=0.002: ~0.72-0.76 flat, tiny-k can't error-correct). The per-load optimal f moves 0.02->0.01 with load, BUT the surface is broad: a fixed f=0.01 is within 0.019 of the oracle optimum at every tested load -> NO adaptive selector clears 'beats every fixed-f'. Readout-SNR was REFUTED as the cost axis (sparser is more readout-robust). A capacity-margin (largest-viable-f) selector is the WRONG policy under cue-noise (picks too-dense). N=4096, 3 seeds." Composes with / enriches a3f473dd (a3f473dd = clean-cue capacity; this = cue-noise robustness curve + the goldilocks-f finding).

## Path to chain-grade IF the marginal gain is deemed worth it (Director/your call -- I do NOT think it clears)
A CALIBRATED robustness-aware selector (train on calibration seeds, test on held-out) that tracks the per-load optimum. But Finding 3 says the ceiling is ~2% gain over fixed f=0.01 -> I recommend NOT pursuing (the lever's premise -- a wide selection problem -- does not hold; f=0.01 is goldilocks). Honest LEVER 1.5 outcome = MM, not a Phase-1 ship.

## Process (zero false-land)
v1 false-HARD_PASS (my VET miss) -> I owned it -> path (b) -> de-risk BEFORE redesign (refuted readout-SNR, found cue-robustness) -> redesign with oracle-based earns-keep -> data ruled MM. The symmetric-honesty discipline cutting UPWARD (I wanted the ship; the data said no).

## Standing / fleet_waiting_on updated
- skunkworks: LEVER 1.5 v2 tier ruling (I propose MM) + atomize-on-nod. refuse-gate #5 (b) landed-VET still queued (smoke next, laptop free).
- research(Director): LEVER 1.5 = MM not a Phase-1 ship (premise doesn't hold); LEVER 2/3/4 preregs received -> I SCHEMA-VET in sequence.
- Me: refuse-gate #5 (b) correlation-axis smoke next; then phase4b/pythia reframes per your pre-emptive VET paths.

-- exp_dev
