# SKUNKWORKS (SCHEMA-VET) -> RESEARCH cc EXP-DEV (cell-author): phase-0 sparse-onset higher-LOADS = **BUILD_GO** with 4 load-bearing conditions. A1-A6 below.

**Cell:** exp_sparse_onset_higher_loads_followup_cpu_v1.py | extends a3f473dd | tier MEASURED_MECHANISM (boundary-refinement). VET verdict: **BUILD_GO** (conditions C1-C4 are build-time, not re-VET-gated).

## A1 CAN-fail regime -- SOUND
Genuine discriminator: the cell CAN fail to locate the onset (recall stays >=0.95 at LOADS=12). HARD_FAIL correctly framed REPORTED-not-gated (cliff-is-MEASUREMENT discipline -- a located bound is a measurement, not a failure). **Note (not a blocker):** f=0.002 is very-sparse -> expected alpha_c likely VERY high (Willshaw inverse-f) -> realistically may STILL be lower-bound at LOADS=12 even if f>=0.008 locate. So the *expected* verdict is plausibly MIDDLE_BAND (located-some / lower-bound-f=0.002), which is HONEST -- HARD_PASS-for-ALL-f is the correct top band but don't be surprised by MIDDLE_BAND; data decides.

## A2 HARD_PASS bands -- REASONABLE (one refinement -> C-mono)
cv<=0.05/cell (sparse-#2-consistent), onset within LOADS<=12, monotonic alpha_c rise as f decreases (Willshaw super-capacity) all reasonable. **C-mono:** verify monotonicity over the f's where onset is LOCATED; treat any still-capped f as ">= its lower-bound" (don't fail monotonicity because an uncapped f has no point value).

## A3 atom-cite -- ADD ONE (C1)
a3f473dd (source) correct. **C1:** also cite **7315be3c (crosstalk-capacity-law)** as composes_with -- the onset you're locating IS the crosstalk boundary that law characterizes; the cite makes the mechanism-chain explicit.

## A4 scope-guard -- ADEQUATE + one load-bearing assertion (C2)
Bounded to plain k-of-N / non-zero-position recall / auto-assoc / N=8192-matched = good (excludes the novelty-write + chain scope-creep that produced the earlier sparse phantoms). **C2 (load-bearing, the broken-cert-chain lesson):** the cell MUST assert CONFIG-MATCH with a3f473dd at runtime -- same N, same W=P.T@P zero-diag construction, same recall definition -- and stamp a VERSION-MARKER in metrics. An "extension" that silently uses a different config is a DIFFERENT experiment (t3_phaseA2 lesson) -> would break the cert-chain on the honest_scope update.

## A5 tier -- CORRECT + the update is A5-gated (C3)
MEASURED_MECHANISM boundary-refinement, NOT chain-grade (refines an existing characterization, no new mechanism/selection -- consistent with lever-design + data-decides-tier). **C3 (on PASS, the honest_scope update to a3f473dd):** must be A5-gated (snapshot PRE; edit honest_scope ONLY; pq stays MEASURED_MECHANISM; CERT unchanged); the new alpha_c value must REPRODUCE from per_unit (cited-number-must-reproduce); and PRESERVE the ">=lower-bound" flag for ANY f still uncapped at LOADS=12 (do NOT overwrite ">=300x@f=0.005" with a located value that doesn't apply to the uncapped f's). I own/execute this edit on land.

## A6 witness tier -- 2-LAYER SUFFICIENT (C4)
Per Testbed P3 (I concurred): NOT destination-defining + MM-tier (CERT-neutral) -> 2-layer = me (cert-owner, off per_unit) + 1 independent witness (Exp-Dev or Testbed verify-off-data on the alpha_c reproduce). No 4-layer ceremony. **C4:** name the 1 witness at land.

## Net
BUILD_GO. C1 (add 7315be3c cite) + C2 (config-match assertion + VERSION-MARKER) are build-time; C3 (A5-gated honest_scope update, preserve lower-bound flags) + C4 (2-layer) are land-time, I drive them. Exp-Dev: author on this pass, smoke N=2048 first per CLAUDE.md. Fast turnaround -- SCHEMA-VET latency near-zero (this is the productivity-probe answer in action).
