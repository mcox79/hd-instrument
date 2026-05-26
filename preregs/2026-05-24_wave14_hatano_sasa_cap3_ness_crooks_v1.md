# Pre-reg: Hatano-Sasa NESS audit-cert for Cap 3 streaming (v1)

**Date**: 2026-05-24
**Experiment**: wave14_hatano_sasa_cap3_ness_crooks_v1
**Script**: experiments/exp_wave14_hatano_sasa_cap3_ness_crooks_v1.py
**Cap-map axis**: Cap 3 (streaming-NESS) audit-certificate via fluctuation theorem
**Queue**: remote_cpu_queue (pure CPU; finite-temp Glauber sweep over 16 cells)

## Background and motivation

Cap 1 (Crooks forensic erase, ✅) carries an audit-cert via the Crooks
fluctuation-theorem inequality: ⟨e^(-W)⟩ ≥ e^(-ΔF) gives a verifiable
inequality on each erase event. Cap 3 (streaming-NESS, ✅) is established
by retrieval behavior under continuous writes (Cap 3 ✅ via three smoke
runs: `wave14_continuous_streaming_inference_v1_smoke` STREAMING_CONTINUOUS_PASS,
`wave14_streaming_NESS_eta_sweep_v1_smoke` NESS_BIMODAL_MIXED,
`wave14_streaming_noise_envelope_v1_smoke`) but lacks a fluctuation-theorem
style audit-cert. Hatano & Sasa (PRL 86:3463, 2001) extended Crooks to
non-equilibrium steady states (NESS) via the "excess heat" and
"housekeeping heat" decomposition, giving the integral identity

  ⟨exp(-W_ex)⟩ = 1

for trajectories of a Markov chain in NESS, where the excess work is

  W_ex(x_0 → x_T) = -[log π_ss(x_T) - log π_ss(x_0)]

(Hatano-Sasa 2001 eq. 12; Speck & Seifert 2005 discrete Markov form.)

Strategy's Research neighborhood recommendation #3 (cheapest CPU anchor,
~5-15 min) proposes testing whether Cap 3 streaming dynamics satisfies
this HS integral fluctuation theorem (HS-IFT). If it does, Cap 3 acquires
an audit-cert analogue of Cap 1's; Cap 1 + Cap 3 compose into a "full
audit-cert lifecycle" (HANDOFF-style composition per the lower-risk
composition class, NOT SCORE-style).

The earlier `wave14_hatano_sasa_ness_audit_v1` (smoke only) returned
`HATANO_SASA_NESS_CERT_PARTIAL`: HS identity = 1.0000 but
cross_basin_frac = 0 because deterministic Hopfield dynamics from
corrupted bipolar keys produced no basin transitions. This v1 fixes
that by (1) using the canonical auto-associative zero-diagonal Hebbian
Hopfield substrate, (2) running finite-temperature Glauber dynamics at
near-critical beta=1.5 so cross-basin events occur, and (3) tightening
the verdict bands per Strategy's spec ([0.95, 1.05] hard-pass, outside
[0.5, 2.0] hard-fail).

## Protocol

### Substrate (Cap 3 operating point)
- N = 2048
- M = 50 (alpha = M/N = 0.024, well within RS phase below alpha_c = 0.14)
- Auto-associative Hebbian: W = (1/N) Σ_μ p_μ p_μ^T, zero diagonal
- Bipolar patterns p_μ ∈ {±1}^N drawn uniformly

### Dynamics
- Finite-temperature Glauber updates: p(s_i=+1) = sigmoid(2β h_i) with h = W s
- beta = 1.5 (near critical; the Mattis-magnetization order parameter
  has T_c ≈ 1 in the SK/Hopfield limit, so beta=1.5 corresponds to a
  moderately-cold NESS with non-trivial basin-crossing rates)
- 60 Glauber steps per trajectory (sufficient relaxation for the
  empirical π_ss to be a meaningful sample of the steady distribution)

### Trajectory ensemble
- 4 noise levels × 4 seeds × 150 trajectories/cell = 2400 trajectories
- noise_levels = {0.30, 0.40, 0.50, 0.60} (bit-flip fraction applied to
  stored pattern before Glauber relaxation)
- seeds = {17, 23, 31, 41}
- Each cell yields one (hs_identity_val, cross_basin_frac) pair;
  aggregate over the 16 cells (>>3 required for HARD_PASS / HARD_FAIL)

### Hatano-Sasa decomposition
For each trajectory:
1. Identify start attractor: src_idx = pattern index used as seed
2. Identify end attractor: argmax cosine overlap of x_T with stored patterns
   (threshold 0.5; below threshold → spurious, trajectory excluded)
3. Estimate empirical π_ss as attractor-hit distribution over the M basins
4. Compute W_ex = -[log π_ss(x_T) - log π_ss(x_0)]
5. Aggregate ⟨exp(-W_ex)⟩ across valid trajectories

## Verdict criteria (hard-pass / middle / hard-fail bands)

**HARD PASS — `HATANO_SASA_CAP3_NESS_CROOKS_HARD_PASS`:**
- ⟨exp(-W_ex)⟩ ∈ [0.95, 1.05] aggregated across ≥ 3 valid cells
- cross_basin_frac ≥ 0.05 (non-vacuous: same-basin-only gives W_ex=0
  trivially; we require real basin-crossing evidence)
- → Cap 3 gains Hatano-Sasa NESS audit-cert annotation
- → Cap 1 + Cap 3 compose into HANDOFF-style "full audit-cert lifecycle"
  (Cap 1 audits erase events; Cap 3 audits steady-state writes)

**HARD FAIL — `HATANO_SASA_CAP3_NESS_CROOKS_HARD_FAIL`:**
- ⟨exp(-W_ex)⟩ outside [0.5, 2.0] across ≥ 3 valid cells
- → Substrate streaming dynamics breaks HS-IFT structurally
- → Informative-negative; substrate's NESS is non-canonical
  (either non-Markov or non-stationary π_ss); does not refute Cap 3 ✅
  itself, only refutes the HS-style audit-cert extension

**MIDDLE BAND — `HATANO_SASA_CAP3_NESS_CROOKS_MIDDLE_BAND`:**
- ⟨exp(-W_ex)⟩ ∈ [0.5, 2.0] but outside [0.95, 1.05], OR
- ⟨exp(-W_ex)⟩ in hard-pass band but cross_basin_frac < 0.05, OR
- n_valid_cells < 3
- → Partial cert; needs more data, longer Glauber chains, or theoretical
  adjustment

## Self-tests (per [[feedback-strategy-spec-formula-selftests]])

Verdict-band unit tests (14 cases): boundary tests at HARD_PASS_LOW=0.95,
HARD_PASS_HIGH=1.05, HARD_FAIL_LOW=0.5, HARD_FAIL_HIGH=2.0,
CROSS_BASIN_MIN=0.05, and n_valid_cells thresholds.

Hatano-Sasa formula self-tests (4 cells):
- **Cell 1 (Brownian uphill)**: starting at log π_ss = 0 (low U), ending at
  log π_ss = -1 (high U) gives W_ex = +1.0 (uphill against NESS measure).
- **Cell 2 (same-state)**: log π_start = log π_end → W_ex = 0.
- **Cell 3 (downhill)**: reverse of Cell 1 gives W_ex = -1.0.
- **Cell 4 (HS-IFT trivial identity)**: diagonal-only chain (no dynamics)
  satisfies ⟨exp(-W_ex)⟩ = 1.0 since W_ex = 0 along all trajectories.

Both test suites PASS locally (14/14 verdict + 4/4 formula cells).

## Expected outcome

HARD PASS at P ≈ 0.55. Reasoning:
- HS-IFT is a structural theorem for any Markov chain at NESS with
  stationary π_ss; finite-temp Glauber on a Hopfield W generically
  satisfies the theorem.
- Possible failure modes giving MIDDLE or FAIL:
  - Empirical π_ss has high statistical noise (M=50 basins with 150
    traj/cell = 3 hits/basin avg — coarse estimate)
  - Substrate's spurious-attractor side-channel breaks the M-basin
    Markov assumption
  - Cross-basin events too rare even at beta=1.5 / noise 0.5

Calibration penalty per [[feedback-lit-scan-calibration-penalty]]: this
is the first direct Hatano-Sasa test on the substrate; no published
precedent for HS-IFT on Hopfield-Glauber Cap 3. Apply 0.20 deflation to
naive P=0.75 → P ≈ 0.55.

## Substrate-product implication

If HARD PASS: substrate has a verified fluctuation-theorem audit-cert
for BOTH erase events (Cap 1, Crooks) AND steady-state writes
(Cap 3, Hatano-Sasa). Product positioning: "auditable memory with
fluctuation-theorem certificates across the full erase + write
lifecycle." This is a HANDOFF-style composition (Cap 1 audits the
erase, Cap 3 audits the write; they cover disjoint events) and so
carries lower composition risk than SCORE-style stackings.

If HARD FAIL: substrate's Cap 3 streaming has structure that breaks
canonical NESS; substrate is auditable for erase only, and the streaming
regime needs a different fluctuation-theorem framework (Seifert-Speck,
Sekimoto stochastic energetics, or a substrate-specific derivation).
Informative; does not refute Cap 3 ✅ itself.

## Resources

- Queue: `remote_cpu_queue` (pure CPU, no CUDA)
- Estimated runtime: 5-15 min (16 cells × ~30s/cell for Glauber relaxation)
- Timeout: 1800 s (3x safety margin)
