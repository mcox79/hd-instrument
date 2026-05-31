# Pre-registration: substrate_state_compression_v3_n8192

**Date:** 2026-05-31
**Anchor:** substrate_state_compression_v3_n8192
**Queue:** remote_cpu_queue
**Script:** experiments/exp_substrate_state_compression_v3_n8192.py
**Cap-map row:** PP-2 Substrate state compression (first-foothold annotation added v295)
**Trigger:** v2 at N=4096 HARD_PASS'd c_quant/bits8: 4x compression + retrieval>=95% + KF-1/2/3 all PASS across 5 seeds

## Scientific question

Does c_quant/bits8 (the PP-2 first-foothold winner) still achieve:
  >= 4x compression AND retrieval >= 95% AND KF-1/KF-2/KF-3 all PASS
at N=8192 (cross-N validation)?

## Design choice: c_quant only

The task brief asks for cross-N validation of the foothold. The foothold IS
c_quant/bits8. Re-testing SVD and sparse approaches at N=8192 would answer
a different question (full re-mapping of the compression space at N=8192) at
3-4x more compute. The focused test (quant only) answers the strategic question
with minimal burn.

Bits tested: [4, 8, 16] -- bits8 is primary; 4 and 16 are context anchors
that confirm bits8 is not an outlier in the quant family.

## Pre-registered threshold bands

**HARD_PASS:** c_quant/bits8 achieves >= 4x compression AND retrieval >= 95%
  AND KF-1/KF-2/KF-3 all PASS in 4/5+ seeds at N=8192.
  Interpretation: PP-2 foothold is cross-N stable; confidence in compression
  as a shipping capability increases substantially.

**HARD_FAIL:** c_quant/bits8 KF preservation breaks (kfs_all_pass=False in
  4/5+ seeds) AND compression_ratio < 4x in 4/5+ seeds.
  Interpretation: foothold is N=4096-specific; compression has an N-dependent
  ceiling that needs further investigation.

**MIDDLE_BAND:** c_quant/bits8 holds compression >= 4x but retrieval degrades
  below 95% at N=8192, OR KFs partially preserved (some seeds pass, some fail).
  Interpretation: compression works but retrieval scaling is N-sensitive;
  annotate as "compression viable at N=4096, marginal at N=8192."

## N-suffix binding (PROT-018)

`_n8192` binds N = 8192. Production config: `N = 8192`, `N_FULL = 8192`.
Pre-ship audit confirms `grep -E "(N\s*=|n\s*=)\s*8192"` matches.

## Seed policy

5 seeds [7, 17, 23, 31, 41] per PROT-021 seed-checkpoint pattern.
Same 5-seed set as v2 for direct cross-seed comparison.

## Smoke result

Smoke at N=1024, M=256:
- seed=17: bits4 comp=8.00x retr=1.000 kfs=PASS
           bits8 comp=4.00x retr=1.000 kfs=PASS
           bits16 comp=2.00x retr=1.000 kfs=PASS
- Wall: 0.2s. Self-test PASS.
- bits8 at smoke: comp=4.00x, retrieval=1.000, all KFs PASS. Strong signal.

Note: smoke at N=1024 is well below the target N=8192. The smoke confirms
instrumentation health; the scientific question is at N=8192 where W is
64x larger and quantization noise may behave differently.

## Walk-back gate assessment

Smoke bits8 is at full HP criteria (comp=4.0x, retr=1.0, kfs=True). Effect
is strong at smoke scale; no walk-back doubling needed.

## Timeout estimate

Reference: v2 at N=4096 ran 5 seeds in 5.26s wall (confirmed from metrics.json).
v3 at N=8192: W matrix is 4x larger (N^2 ratio = 4), quant ops scale as O(W.nelement()).
Estimated full run: ~5.26s * 4 = ~21s.
Formula: ceil(1.5 * 21s) = 32s.

PROT-019 floor for _n8192 (>=8192): **21600s (6h)**. This is the binding floor.

**timeout_s = 21600**

(The PROT-019 floor dominates -- this is a fast CPU-only quant script that
will finish in <2 min, but the floor protects against unexpected overhead at
the remote machine.)

## Post-ship cap_map decision plan

- HARD_PASS -> PP-2 row promoted from "first-foothold" to "cross-N stable";
  confidence band raised; roadmap item flagged for product integration planning
- MIDDLE_BAND -> PP-2 row annotated "N-boundary between 4096 and 8192"; dispatch
  probe at finer N grid or investigate retrieval degradation mechanism
- HARD_FAIL -> PP-2 row demoted to "N=4096 specific finding"; rehabilitation
  probe at what breaks at larger N (KF or retrieval?); 2x research on quant
  scaling in associative memory
