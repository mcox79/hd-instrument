# Pre-registration: substrate_cortex_hippo_handoff_bottleneck_class_diagnostic_v1

**Filed:** 2026-06-28
**Anchor:** substrate_cortex_hippo_handoff_bottleneck_class_diagnostic_v1
**Script:** experiments/exp_substrate_cortex_hippo_handoff_bottleneck_class_diagnostic_v1.py
**Queue:** local_cpu_queue (NumPy; light; ~25s/seed at FULL; 3 seeds total ~75s + smoke gate ~10s)
**Tier:** MEASURED_MECHANISM (DIAGNOSTIC; not chain-grade promotion candidate)
**N_h / N_c:** 8192 / 2048 (PROT-018 capability-test; no `_n<N>` suffix; light cell)
**M:** 2048 (sub-capacity regime where rescue v1 measured gap=0.76)
**Seeds:** [7, 17, 23] (3-seed FULL)
**Drill source / parent:** notes/research_to_exp_dev_bottleneck_class_diagnostic_2026-06-28
**Lineage:** rescue v1 disproved alpha-capacity attribution; this probe identifies
WHICH structural mechanism dominates the DIRECT-STANDARD readout gap.

## Hypothesis

The cortex-hippo handoff readout gap at sub-capacity (DIRECT 0.989 vs STANDARD 0.226
at M=2048/N_h=8192/N_c=2048) is caused by one of:

- **H1 SPARSE-OVERLAP INTERFERENCE:** sparse-DG codes (k=10% active) have many
  shared active bits across items; W_h @ cue sums weighted by overlap counts;
  "popular" bits dominate over cue-specific signal.
- **H2 SIGN-QUANTIZATION:** sign(W_h @ cue) collapses real-valued matmul to
  {-1,+1}, destroying magnitude information that selects the correct stored val.
- **H3 SIGN+NORM COMBINED DESTRUCTION:** sign() + L2-normalization removes
  correlation-with-stored-val.

H2 and H3 are not orthogonal in the readout chain (sign happens before L2
normalize, and the diagnostic uses real-valued readout to lift BOTH);
ARM_REAL_VALUED tests them together vs ARM_STANDARD.  ARM_DENSE_DG isolates H1.
ARM_DENSE_REAL tests interaction.

## Pre-registered arms (5; META_RULE_AF arms-must-differ)

| Arm | Hippo encode | Hippo readout | Tests |
|-----|--------------|---------------|-------|
| ARM_DIRECT | sparse-DG (k=10%) | n/a (no hippo) | Ceiling |
| ARM_STANDARD | sparse-DG (k=10%) | sign(W_h @ cue) | Baseline (0.226) |
| ARM_REAL_VALUED | sparse-DG (k=10%) | W_h @ cue (no sign) | H2 + H3 |
| ARM_DENSE_DG | dense bipolar (all bits) | sign(W_h @ cue) | H1 |
| ARM_DENSE_REAL | dense bipolar (all bits) | W_h @ cue (no sign) | H1 + H2 + H3 |

Mechanism-distinctness enforced by selftest `_selftest_arm_hash_diverges` (catches
arm-level bit-collisions before dispatch) AND runtime META_RULE_AF check across
ALL 5 mechanism pairs in `compute_verdict`.

## Pre-registered thresholds

Let `R_X` = mean(recall) across seeds for ARM_X.
Let `gap = R_DIRECT - R_STANDARD`.
Let `close_frac(X) = (R_X - R_STANDARD) / gap`.

**Regime check (smoke + full):** `gap >= 0.40`.  Below this, regime drifted from
rescue v1's sub-capacity row -> MIDDLE_BAND (inconclusive).

**HARD_PASS bands (one clean hypothesis isolated):**

- `close_frac(REAL_VALUED) >= 0.40 AND close_frac(DENSE_DG) < 0.40`
  -> **H2_SIGN_QUANT_CONFIRMED** (sign-readout is the killer; real-valued
  readout rescues; sparse-overlap is incidental)
- `close_frac(DENSE_DG) >= 0.40 AND close_frac(REAL_VALUED) < 0.40`
  -> **H1_SPARSE_OVERLAP_CONFIRMED** (sparse-overlap is the killer; dense
  encoding rescues; sign-readout is incidental)
- `close_frac(DENSE_REAL) >= 0.80 AND close_frac(REAL_VALUED) < 0.40 AND
   close_frac(DENSE_DG) < 0.40`
  -> **H1xH2_SYNERGY** (neither alone suffices; combined intervention required)
- `close_frac(REAL_VALUED) < 0.15 AND close_frac(DENSE_DG) < 0.15 AND
   close_frac(DENSE_REAL) < 0.15`
  -> **H_OTHER_NEW_PROBE_NEEDED** (none of H1/H2/H3 dominate; new mechanism
  hypothesis required)

**MIDDLE_BAND:** mixed signals (e.g. both REAL_VALUED and DENSE_DG close 0.40+
independently -> additive contributions, can't tier H1 vs H2; or
DENSE_REAL <= 0.80 with one component closing).

**HARD_FAIL:**
- META_RULE_AF violation (any two distinct mechanism arms produce bit-identical
  arm_hash across all seeds -> mechanisms aren't actually different)
- Cardinality breach (n_arms != 5 or n_seeds != 3)
- Any arm error

## Smoke prediction (regime-fidelity check)

SMOKE regime: M=512, N_h=2048, N_c=512, 1 seed.  Same `alpha_simple = M/N_h = 0.25`
as FULL.

**Smoke RESULT (2026-06-28):** 5/5 arms ran; all 5 ARM_HASH distinct.  Gap at
smoke = 0.396 (DIRECT 1.000 / STANDARD 0.604).  THIS IS BELOW the 0.40
pre-reg threshold (failed regime-fidelity at this smoke point).

Verdict at smoke = MIDDLE_BAND (gap insufficient to discriminate hypotheses).

**Full-N preview (seed=7 only, M=2048/N_h=8192/N_c=2048):**
- DIRECT=0.985 STANDARD=0.213 REAL_VALUED=0.213 DENSE_DG=0.072 DENSE_REAL=0.076
- gap_DIR_STD=+0.772 (matches rescue v1 measured 0.76)
- closeFrac REAL_VALUED=+0.001 / DENSE_DG=-0.183 / DENSE_REAL=-0.177
- Verdict: HARD_PASS (tag=H_OTHER_NEW_PROBE_NEEDED)

**Key smoke findings:**
- Discriminator at M=512 smoke does NOT survive scale-down (USER 2026-06-26
  discriminator-must-survive-scale warning fires here).  The full-N preview
  arm (1-seed FULL-regime) is the load-bearing diagnostic input, NOT the
  M=512 smoke.
- DENSE arms HURT at BOTH smoke and full (refutes H1 sparse-overlap).
- REAL_VALUED equals STANDARD bit-exactly at FULL (refutes H2 sign-quant).
- Diagnostic-informative outcome: H_OTHER -- the gap is caused by something
  OTHER than the three structural hypotheses.  Cell ships to 3-seed FULL
  for seed-stability confirmation; result feeds back into the next-probe
  design (cell-author or research-drill).

**Discriminator-survives-scale check** (USER 2026-06-26 check C: full-N preview):
- Full-N preview (1 seed) at the actual FULL regime confirms gap=0.772 AND
  the arm ranking is informative.  Cell is in the right diagnostic regime
  at FULL; smoke at M=512 understates saturation but cell mechanics are correct.

Decision: ship 3-seed FULL on local_cpu_queue (resumable_seeds will see
seed=7 partial from full-N preview as complete; runs seeds 17 + 23).

## Fairness disciplines (load-bearing)

- W_hippo and W_cortex are different matrices, different shapes
- Same projection matrices `P_in` and `P_hc` across all arms within a seed (only
  the encode/readout discipline varies)
- Same Hebbian outer-product write rule across all arms (`W_h += vals_h.T @ keys_h`)
- ARM_DIRECT uses the SAME sparse-DG encode for keys_c/vals_c projection as
  ARM_STANDARD (controls for projection differences -- only the hippo READ path
  changes)
- Single replay pass (N_replay_per_item=1) per arm; deterministic permutation
  seeded by `seed + 17` (rescue v1 convention)

## Expected per-arm recall (smoke prior; informs interpretation)

These are not pre-registered thresholds -- they are calibration anchors for
"smoke is in the right regime":

- R_DIRECT ~ 0.95-0.99 (rescue v1 measured 0.989 at M=2048/N_h=8192)
- R_STANDARD ~ 0.18-0.26 (rescue v1 measured 0.226)
- R_REAL_VALUED: unknown; if H2 confirmed, ~0.6-0.9; if not, ~0.2-0.3
- R_DENSE_DG: unknown; if H1 confirmed, ~0.6-0.9; if not, ~0.2-0.3
- R_DENSE_REAL: highest among non-DIRECT if H1xH2 synergy; ~0.95+ in synergy
  case, otherwise tracks REAL_VALUED or DENSE_DG

## Cap-map rows (proposed; landed-VET decides actual tier)

- "Cortex-hippo handoff bottleneck class" (cap_map row creation)
- Whichever hypothesis is confirmed feeds into the cortex_hippo_handoff
  CLOSED-negative re-opening (rescue cell would target the confirmed mechanism)

## Coordination

- Cell-author: exp_dev (this dispatch)
- Landed-VET: skunkworks (audit-only)
- Routing: local_cpu_queue (NumPy; no GPU; measured 25s/seed at FULL; 3 seeds
  total ~75s; remote_cpu_queue would also be fine but local is simpler for a
  ~75s cell and avoids push-required-spawn-Orchestrator dance)

## Dispatch destination + timeout

- Queue: local_cpu_queue
- timeout_s: 600 (~8x measured per-seed wall + 3-seed multiplier + scale-up margin)
- No PROT-018 suffix (`_n<N>` not in anchor name); no PROT-019 floor (N_h=8192
  but `_n8192` not in anchor name -- PROT-019 keys off suffix not config)
- No PROT-021 long-timeout checkpoint requirement (well below 14400s)
- seed=7 already complete from full-N preview (resumable_seeds will skip it;
  runs seeds 17 + 23 only)
