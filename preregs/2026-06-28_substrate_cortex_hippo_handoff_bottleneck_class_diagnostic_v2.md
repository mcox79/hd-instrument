# Pre-registration: substrate_cortex_hippo_handoff_bottleneck_class_diagnostic_v2

**Filed:** 2026-06-28
**Anchor:** substrate_cortex_hippo_handoff_bottleneck_class_diagnostic_v2
**Script:** experiments/exp_substrate_cortex_hippo_handoff_bottleneck_class_diagnostic_v2.py
**Queue:** remote_cpu_queue (NumPy; per USER routing — cpu_runner_0 IDLE)
**Tier:** MEASURED_MECHANISM (DIAGNOSTIC; not chain-grade promotion candidate)
**N_h / N_c:** 8192 / 2048
**M:** 2048 (sub-capacity regime; alpha_simple=0.25; v1's measured gap=0.766)
**Seeds:** [7, 17, 23] (3-seed FULL)
**Drill source / parent:** v1 diagnostic (commit 8a84607c) HARD_PASS tag=H_OTHER_NEW_PROBE_NEEDED
**Lineage:** v1 refuted H1 (sparse-overlap), H2 (sign-quant), H3 (sign+norm).
This v2 probes the 3 candidate mechanisms cell-author flagged in the v1 H_OTHER
bucket.

## Hypothesis space

v1 measured at M=2048/N_h=8192/N_c=2048:
- R_DIRECT=0.985  R_STANDARD=0.219  gap=+0.766
- R_REAL_VALUED=0.225 (closeFrac=+0.008)  -> H2 REFUTED (bit-equivalent)
- R_DENSE_DG=0.065    (closeFrac=-0.201)  -> H1 REFUTED (worse than baseline)
- R_DENSE_REAL=0.069  (closeFrac=-0.197)  -> H3 REFUTED via H2

Remaining H_OTHER candidates:

- **Ha HEBBIAN-CROSS-TERM INTERFERENCE.**  W_h = sum_i vals_h[i] @ keys_h[i].T
  superposes all 2048 items into one (N_h, N_h) matrix.  Even with sparse keys,
  bits that fire across many items dominate the readout sum.  Tests by
  REPLACING the Hebbian outer-product write with per-item explicit lookup
  (argmax-cosine in sparse-DG space; equivalent to a perfect content-addressable
  memory for the hippo READ path), leaving everything else identical to
  STANDARD.

- **Hb L2-NORM COLLAPSE ON READ-BACK.**  L2-normalize on vals_react_h @ P_hc.T
  forces every reconstructed vector to unit length BEFORE writing to cortex;
  if vals_react_h is weak/noisy, L2-norm amplifies noise (denominator small)
  and erases the magnitude correlation with the stored val.  Tests by skipping
  the read-back L2-norm only.

- **Hc CORTEX HEBBIAN WRITE-SATURATION.**  Cortex receives noisy vals_react_h
  via vals_c_react and Hebbian-superposes them; the cortex itself may be the
  failure site.  Tests by writing CLEAN vals_c (real cortex-projection of the
  stored val) into W_cortex instead of vals_c_react.

## Pre-registered arms (5; META_RULE_AF arms-must-differ)

| Arm | Hippo readout | Cortex write target | Tests |
|-----|---------------|---------------------|-------|
| ARM_DIRECT | n/a (no hippo) | vals_c[perm] (clean) | Ceiling |
| ARM_STANDARD | sign(W_h @ cue) + L2 | vals_c_react (noisy + normed) | Baseline (v1 reproduced: 0.219) |
| ARM_NO_HEBBIAN_CROSSTERM | argmax-key + vals_h[lookup] + L2 | vals_c_react (normed) | Ha |
| ARM_NO_L2_NORM | sign(W_h @ cue), NO L2 | vals_c_react (raw) | Hb |
| ARM_CLEAN_VALS_TO_CORTEX | sign(W_h @ cue) + L2 (paid but unused) | vals_c[perm] (clean) | Hc |

Mechanism-distinctness enforced by:
- `_selftest_arm_hash_diverges` (pre-dispatch self-test catches bit-collisions
  across the 4 mechanism arms; ARM_DIRECT and ARM_CLEAN_VALS_TO_CORTEX are
  expected to collide in selftest because both feed vals_c[perm] -- excluded
  from the distinctness check by design)
- `_selftest_no_hebbian_crossterm_isolation` (verifies argmax-lookup actually
  self-matches at small scale; otherwise Ha can't be isolated)
- Runtime META_RULE_AF check across the 6 mechanism pairs in `compute_verdict`.

## Pre-registered thresholds

Let `R_X` = mean(recall) across seeds for ARM_X.
Let `gap = R_DIRECT - R_STANDARD`.
Let `close_frac(X) = (R_X - R_STANDARD) / gap`.

**Regime check (smoke + full):** `gap >= 0.40`.  Below this, regime drifted ->
MIDDLE_BAND.

**HARD_PASS bands:**

- `close_frac(NO_HEBBIAN_CROSSTERM) >= 0.40` -> **Ha_HEBBIAN_CROSSTERM_CONFIRMED**
  (mechanism class for Stage 2 NREM closure rescue path: bound-capacity
  associative-memory write -- per-key explicit storage, replay-mediated
  re-superposition with coarse-grain eviction).
- `close_frac(NO_L2_NORM) >= 0.40` -> **Hb_L2_NORM_COLLAPSE_CONFIRMED**
  (rescue: drop normalize on weak signals; signal-strength gate).
- `close_frac(CLEAN_VALS_TO_CORTEX) >= 0.40` -> **Hc_CORTEX_WRITE_SATURATION_CONFIRMED**
  (rescue: bound cortex writes by hippo-readout quality; SNR gate).
- Multiple confirmed -> **additive H_OTHER class** (still HARD_PASS;
  further isolation cell required to separate which dominates).
- `all three closeFrac < 0.15` -> **H_DEEPER_OTHER_NEW_PROBE_NEEDED**
  (informative null result; new probe candidates would be:
   training-signal-quality / projection-rank-collapse / pre-cortex SNR floor).

**MIDDLE_BAND:** any single closeFrac in [0.15, 0.40) without others reaching
0.40 -- partial / mixed signal that doesn't cleanly isolate a mechanism class.

**HARD_FAIL:**
- META_RULE_AF violation (any two distinct mechanism arms produce bit-identical
  arm_hash across all seeds)
- Cardinality breach (n_arms != 5 or n_seeds != 3)
- Any arm error

## Pre-flight: smoke verdict + per-arm

To be filled at smoke time before dispatch. (Filled below by cell-author after
smoke gate; full results land in metrics.json.)

SMOKE regime: M=512, N_h=2048, N_c=512, 1 seed.  Same alpha_simple=0.25 as FULL.

Per v1's observation, the M=512 smoke understates the saturation gap (v1 smoke
gap was 0.40 vs full 0.77).  The smoke's load-bearing job here is:
1. Confirm the cell RUNS (no exceptions, no shape errors)
2. Confirm 4 mechanism arms produce distinct arm_hash values (META_RULE_AF
   pre-dispatch check; the selftest already covers this but smoke is end-to-end)
3. Confirm STANDARD reproduces "much less than DIRECT" (sanity)

The full-N preview (seed=7 alone at FULL regime) is the load-bearing
discriminator decision input -- if at full preview the gap is near v1's 0.77
AND no rescue arm closes >= 0.40 of it, that's the H_DEEPER_OTHER hard signal.

## Fairness disciplines (load-bearing)

- W_hippo (hippo Hebbian) and W_cortex (cortex Hebbian) are different matrices,
  different shapes (anatomical separation)
- Same projection matrices `P_in` and `P_hc` across all arms within a seed
- Same sparse-DG encoding for keys_h / vals_h across all arms (only mechanism
  arms differ in read/write path)
- Same single replay pass (N_replay_per_item=1)
- Same deterministic permutation seeded by `seed + 17`
- ARM_CLEAN_VALS_TO_CORTEX still PAYS the hippo-readout compute cost (the
  sign() result is computed but discarded) -- maintains arm_hash distinctness
  and ensures CLEAN doesn't accidentally bypass the entire pipeline

## Expected per-arm recall (smoke prior; informs interpretation)

These are calibration anchors for "smoke is in the right regime":

- R_DIRECT ~ 0.95-0.99 (v1 measured 0.985 at full)
- R_STANDARD ~ 0.20-0.25 (v1 measured 0.219 at full)
- R_NO_HEBBIAN_CROSSTERM: unknown; if Ha confirmed, ~0.6-0.95 (could match
  DIRECT if the cross-term superposition is the ENTIRE story); if not,
  STANDARD-ish.
- R_NO_L2_NORM: unknown; if Hb confirmed, ~0.4-0.7; else STANDARD-ish.
- R_CLEAN_VALS_TO_CORTEX: unknown; if Hc confirmed, ~0.5-0.95 (could match
  DIRECT if cortex write is the entire story); else STANDARD-ish.

Note: if NO_HEBBIAN_CROSSTERM reaches DIRECT (~0.985), that strongly suggests
Ha is the FULL story (the Hebbian-superposition write IS the bottleneck);
this would be a chain-grade-style isolation result and motivate immediate
Stage 2 rescue cell.

## Cap-map rows (proposed; landed-VET decides actual tier)

- "Cortex-hippo handoff bottleneck class -- H_OTHER refinement"
- Whichever H_OTHER candidate confirms feeds into the Stage 2 NREM closure
  rescue cell design.

## Coordination

- Cell-author: exp_dev (this dispatch)
- Landed-VET: skunkworks (audit-only)
- Routing: **remote_cpu_queue** (per USER directive; cpu_runner_0 IDLE).
  NumPy backend; ~30-60s/seed at FULL (v1 measured 25s/seed but Ha arm pays
  extra (M, M)=8 GB-equivalent argmax which adds ~10-20s); 3 seeds total
  ~3-5 min plus checkpoint sync overhead.
- Push gate: hd_metrics_sync (cell+prereg committed to local main; sync
  daemon pushes; remote runner picks up by name).

## Dispatch destination + timeout

- Queue: remote_cpu_queue
- timeout_s: 1800 (30 min; ~6x measured ceiling per seed * 3 seeds + 2x scale
  margin for the (M,M) argmax on the Ha arm; well below PROT-021 14400s
  long-timeout-checkpoint floor)
- No PROT-018 suffix (`_n<N>` not in anchor name)
- No PROT-019 floor (N_h=8192 but `_n8192` not in anchor)
- Pre-flight smoke gate runs locally before queue_add (queue_add.py enforces)
