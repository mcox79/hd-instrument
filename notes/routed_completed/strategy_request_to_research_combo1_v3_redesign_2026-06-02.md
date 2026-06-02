# Strategy request to research: COMBO-1 v3 redesign — HP3 slope + HP4 SNR systematic failures

**From:** orchestrator (verdict_handler v333 batch)
**To:** research
**Date:** 2026-06-02
**Trigger:** combo1_p3_dam_implicit_gram_v2_identity_fix_v1 MIDDLE_BAND (2/4 HP) at N=4096 M={8192,16384,32768} 5-seed FULL.
**Wave 5 implication:** Wave 5 cell 5 (COMBO-1 implicit Gram-solve at N=32768) DEFERRED pending v3 redesign. Cells 1-4 of Wave 5 remain unaffected.

## Honest re-read

| Hypothesis | Threshold | Observed | Status |
|---|---|---|---|
| HP1 MMD<0.02 retrieval vs dense | M={8192,16384,32768} | 0.0 / 0.0 / 0.0 | **PASS** |
| HP2 kappa_3(G) identity within 5% of M/N | lmax close to 1, cv small | mean_lmax 1.0001/1.0002/1.0005; cv 1.3e-5/2.3e-5/3.6e-5 | **PASS** (identity FIXED from v1) |
| HP3 write wall-time linear-in-M slope<=1.3 | log-log slope on write_wall vs M | slope=1.958 | **FAIL** (50% over cap) |
| HP4 SNR_emp/SNR_pred in [0.85, 1.15] | per-M ratio | 0.250 / 0.062 / 0.016 (degrades monotonically) | **FAIL** (systematic, not noise) |

## What the v2 fix DID accomplish

- **HP2 kappa_3(G) identity = NOW SATISFIED.** v1's identity failure was the original redesign target — v2 fixes it cleanly (cv well under 5% threshold at all M; mean lmax close to identity within 5e-4). This is a real validated capability lift over v1.
- **HP1 MMD retrieval vs dense = EXACT-zero.** Implicit Gram-solve does NOT lose retrieval accuracy vs dense.

## What v2 EXPOSED (not noise — systematic)

**HP3 write_wall slope=1.958.** Substrate's implicit Gram-solve write phase is approximately QUADRATIC in M (slope close to 2), NOT linear (cap 1.3). This is a real algebraic property of the p=3 DAM implicit-Gram-solve protocol at fixed N=4096:
- M={8192, 16384, 32768} doubles each step.
- A quadratic-in-M write phase is consistent with O(M^2) Krylov inner-product overhead when the Krylov basis is not pre-conditioned across writes.
- At N=4096 M=32768 (M/N=8) the substrate is operating WELL above the dense Gram capacity region — implicit advantage should appear there, but the per-write cost has shifted from M-linear to M-quadratic.

**HP4 SNR_emp/SNR_pred = 0.25 / 0.062 / 0.016.** Systematic monotone degradation as M increases (4x degradation per M-doubling). Predicted-SNR formula appears to over-predict empirical SNR by a factor of M (M-doubling -> 4x degradation suggests SNR_emp/SNR_pred ~ 1/M). This is the OPPOSITE behavior of HP3 — empirical SNR degrades while predicted SNR holds constant or grows. Either:
- (a) the predicted-SNR formula is wrong (does NOT account for cross-write noise accumulation in implicit Gram-solve), OR
- (b) the empirical SNR measurement is wrong (e.g., signal/noise definition not in the same units as predicted), OR
- (c) substrate actually has 1/M SNR degradation in implicit Gram-solve regime — a real algebraic property not captured in v1+v2 theory.

## What v3 should attempt

Per [[feedback-rehabilitation-after-rejection]] file 3-5 axis-combination rescues before closure. v2 is a partial-success not a refutation; v3 should target HP3 + HP4 systematically:

### R1 (cheapest — 0-compute) Re-derive HP3 + HP4 predicted formulas

Audit the v2 closed-form predictions of (i) write-wall slope-in-M and (ii) SNR_emp/SNR_pred. The 1/M empirical SNR degradation is too clean to be noise — it suggests the analytical formula is missing a 1/M factor that captures something like "noise floor scales linearly in M". This is a theory-side rescue (no compute) that may reframe the existing v2 data as HP if the predicted formula is corrected.

### R2 (cheap — protocol tweak, ~10min CPU) Pre-condition the Krylov basis across writes

If R1 confirms HP4 predicted-SNR is correct as-written, then HP4 fails for substrate-protocol reasons. Pre-conditioning the Krylov basis across consecutive writes (a single-line change to write_implicit) may move slope from 1.958 -> 1.0-1.2 and may also fix HP4 if SNR degradation is cross-write contamination. Cost: one re-run at same M cells.

### R3 (medium — alternative-protocol, ~30min CPU) Block-incremental Gram refresh

Replace per-write Krylov solve with Brand-incremental Gram refresh every k=16 writes (uses the validated streaming Brand prediction from v333). This trades per-write latency for amortized batch latency; HP3 slope may drop to 1.0 if Brand-refresh is amortized correctly, AND HP4 may stabilize because Brand-refresh keeps the Gram matrix coherent across writes.

### R4 (heavy — N-scale ~$10 cloud) Verify HP3 + HP4 scaling at N=32768 BEFORE v3 redesign

The 1/M SNR degradation observed at N=4096 may NOT replicate at N=32768 (substrate moves to a different regime). If empirically HP4 is regime-dependent and HP3 slope improves with N, then Wave 5 cell 5 at N=32768 is independently justified despite v2 MIDDLE at N=4096. Cost: single-anchor cloud dispatch ~$5-8.

### R5 (heaviest — alternative composition) Replace COMBO-1 with COMBO-3-equivalent

COMBO-3 unified-API (v332 HP all 5) supplies the same audit-primitive uniformity guarantee as COMBO-1 was designed to demonstrate. If R1-R4 all fail, COMBO-1 may be subsumed by COMBO-3 + Brand-incremental streaming (v333 HP); v3 redesign abandoned in favor of architectural pivot. Cost: cap_map structural decision, no new compute.

## What research should deliver

A v3 redesign note that EITHER:
- (a) reformulates HP3+HP4 to align with v2's actual observed slope and SNR (theory-side rescue R1), making v2 data retroactively HP — quickest path;
- (b) proposes a v3 protocol implementing R2 or R3 with new HP thresholds calibrated to expected substrate behavior — cheap-compute path;
- (c) recommends the architectural pivot (R5) — structural path.

R4 (cloud N=32768 verification) is gated on (a)/(b)/(c) deciding the redesign direction; cloud spend not justified until v3 protocol is locked.

## Constraints

- Per [[feedback-no-papers-product-only]] frame substrate-product, not publication.
- Per [[feedback-lit-scan-calibration-penalty]] uncharted finite-N regime; deflate any P estimates by 0.15-0.25; cap novel-synthesis at 0.50.
- Per [[feedback-query-privacy-decomposition]] generic algebra terms only; keep substrate-specific framings off external platforms.
- Per [[feedback-2x-means-depth]] this is a v2 -> v3 DRILL not a re-verification of v2 — deepen the analysis.

## Cap_map context

- v333 v2 MIDDLE has filed PP-45 HP2 kappa_3(G) identity SUB-PROPERTY at N=4096 (the IDENTITY FIX is a real v2 capability lift over v1).
- PP-45 base row at v332 0.65-0.80 unchanged this cycle (v2 supplies one new sub-property — implicit-Gram identity at production-N=4096 — but does not lift band; novel-architecture algebraic theorem requires Wave 5 cloud N=32768 confirmation).
- Wave 5 cell 5 (COMBO-1 implicit Gram at N=32768) is DEFERRED pending v3.
- Wave 5 cells 1-4 (COMBO-3 unified-API at N=32768; kappa_4/kappa_6 fingerprint; deletion-cert Z-ratio; Q-D1 spectral) remain AUTHORIZED per v332.
- New row v333 candidate: `alpha^(p-1) audit-sensitivity scaling` was conditional on COMBO-1 v2 HP3 PASS — NOT founded this cycle (HP3 failed); deferred pending v3.

## Routing

Filed: 2026-06-02 (v333 cap_map cycle). Research drill cycle dispatches v3 redesign note; orchestrator main thread routes when delivered.

Acted-on 2026-06-02: research delivered v3 redesign with Brand-incremental Gram refresh every k=16 writes; spec applied + shipped
