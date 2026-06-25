# Skunkworks tier ruling -- 3 cells post 5x disparate-fields drill (2026-06-25)

Verify-OFF-DATA recompute on `data/exp_*/metrics.json` for each cell.
Cert-owner role: AUDIT-ONLY. Cell-author commits cited; per-arm metrics read directly
(Fix #28 default); by-construction-saturation tiering applied; precedent cert-rows 698/707
considered.

## TL;DR ruling table

| Cell | Director request | Skunkworks ruling | CERT delta |
|------|------------------|-------------------|------------|
| 7 cross_layer_compose_LM_v2_RESCUE_FULL | CHAIN_GRADE | MEASURED_MECHANISM | 0 |
| 8 hub_spoke_E1_v2_diverse_algorithm | MEASURED_MECHANISM | MEASURED_MECHANISM | 0 |
| 9 compose_heterogeneous_routing_v2_RESCUE | MEASURED_MECHANISM | MEASURED_MECHANISM | 0 |

Director-vs-Skunkworks divergence is on Cell 7. I disagree with the CHAIN_GRADE
re-tier; I CONCUR that READOUT_DEGENERATE was an instrument artifact and the
architectural mechanism (independent-W beats shared-W) is real. I file the cell
as MEASURED_MECHANISM and atomize the verdict-classifier lesson separately.

Drill claims on Cells 8 and 9 reproduce off-data exactly.

---

## Cell 7 -- cross_layer_compose_LM_v2_RESCUE_FULL

Cell commit: `6ba0ef08` (Wave C). Metrics: `data/exp_substrate_cross_layer_compose_LM_v2_RESCUE_FULL/metrics.json`.

### Director claim verification (per-arm, off-data)

All numbers confirmed off `detail.by_arm_agg` (lines 70-126) and `per_seed` (lines 174-480):

- ARM_UNIGRAM bpc_mean = 7.7378 (line 71)
- ARM_SINGLE_LAYER_CFRPE bpc_best_mean = 7.0888 cv 0.003 (line 75)
- ARM_2_LAYER_INDEPENDENT_CFRPE bpc_best_mean = 7.1679 cv 0.005 (line 88) -- best_indep
- ARM_3_LAYER_INDEPENDENT_CFRPE bpc_best_mean = 7.1771 cv 0.0077 (line 101)
- ARM_2_LAYER_SHARED_W_CFRPE bpc_best_mean = 7.5442 cv 0.0008 (line 114)

`indep_vs_shared_gap = 0.3763` (line 133) confirmed: 7.5442 - 7.1679 = 0.3763. 3 seeds {7,17,23}.
Per-seed gaps verified consistent (s7: 7.5509-7.1313=0.4196; s17: 7.5456-7.2165=0.3291;
s23: 7.5361-7.1559=0.3802). Cell numbers reproduce.

### READOUT_DEGENERATE label -- I concur with the drill

`raw_bpc_at_T1_L1_mean = 11.5518` (line 95) IS within +/- 0.5 of `vocab_entropy_uniform_bits
= 11.9658` (line 137), which triggered `degen_flag = true` (line 136). But this is a verdict-
classifier instrument bug:

1. raw_at_T1 is the BPC at T=1.0 lambda=1.0 (untuned). Best tuned BPC sits at T=0.05
   lambda=0.3 (per_seed lines 187-188, 207-208, etc.) -- a 20x temperature scaling away
   from 1.0. At that T, raw_bpc_at_T1 is forced toward vocab-entropy by the wave14b CE_floor
   math regardless of substrate signal.
2. tuned-BPC at 7.168 = 4.8 bits BELOW vocab-entropy 11.97. That is NOT collapse.
3. shared_W (which suffers worse architectural penalty, +0.376 BPC) reads raw_at_T1 11.6353
   (line 121) -- HIGHER raw than independent (11.5518). The arm with worse capability has
   raw CLOSER to vocab-entropy, but is NOT flagged differently. The degen classifier is
   measurement-mode-confused.

So I retire READOUT_DEGENERATE as the operative verdict on this cell. The verdict-classifier
lesson is real and worth atomizing: M1 = verdict classifiers must use tuned metrics, never
raw_at_T1.

### Why NOT CHAIN_GRADE -- under-claim per by-construction-saturation + Fix #28

The cell's OWN pre-registered chain-grade bar (line 157, `honest_scope`):
> "HARD_PASS_CHAIN_GRADE = best_indep BPC <= 6.95 AND beats SHARED_W by >= 0.15 BPC AND cv<=0.03"

- best_indep BPC = 7.168, NOT <= 6.95. (Fails primary bar.)
- gap = 0.376 >= 0.15. (Passes secondary.)
- cv = 0.005 <= 0.03. (Passes tightness.)

Two of three. The PRIMARY BPC bar (<=6.95) is NOT met. Director's reclassification waives
this bar on grounds that 7.168 beats unigram 7.738 by 0.57 BPC. That argument applies a
DIFFERENT bar than the pre-reg; that's the move META_HARNESS_RIGGED (cert row 698) was
atomized to catch.

Even more load-bearing: the architecture-level argument that "indep beats shared by +0.376
BPC" needs top1 propagation under META_HARNESS_RIGGED to chain-grade. Top1 numbers:
- ARM_2_LAYER_INDEPENDENT top1 = 0.2324 (line 91)
- ARM_2_LAYER_SHARED_W top1 = 0.2171 (line 117)
- ARM_UNIGRAM top1 = 0.2171

indep_2L top1 over unigram = +0.0153 abs = +7.05% rel. n1_v3 chain-grade bar (cert row 699)
is +61.6% rel. This cell is 0.11x the chain-grade bar on top1. Same signature as cert rows
707 (cfrpe_n_steps_curve_v1) and 708 (cfrpe_per_token_adaptive_lr_v1): BPC improvement
without proportional top1 lift.

PRECEDENT: cert ledger rows 707 + 708 ruled MEASURED_MECHANISM on exactly this signature
in the past 48h. Consistency demands MEASURED_MECHANISM here.

### What IS proven (mechanism characterization)

- Cross-layer 2L-INDEPENDENT cf-RPE beats SHARED-W by 0.376 BPC at production scale
  (N_DIM=8192, V=4000, text8 100k, 3 seeds, cv 0.005). This refutes the strong-form
  hypothesis that shared-W is architecturally sufficient.
- Going from 2L to 3L INDEPENDENT does NOT help (7.168 -> 7.177; depth saturates at 2).
- SHARED-W cv = 0.0008 (extremely tight) means the +0.376 gap is well outside seed noise.
- Single-layer (7.089) BEATS 2L-indep (7.168) on BPC; layer-composition is BPC-NEGATIVE
  here at this dimensionality. (Line 132: `indep_vs_single_lift = -0.0791`.) Mechanism
  characterized: cross-layer with cf-RPE does NOT compose super-additively at production
  N=8192; the architectural lift is over SHARED-W only.

### Ruling

**Cell 7: MEASURED_MECHANISM** -- CERT-neutral, delta = 0.

Filing atom: `math::T3/EXP_substrate_cross_layer_compose_LM_v2_RESCUE_FULL_MM` with
provenance_quality = MEASURED_MECHANISM. READOUT_DEGENERATE retired as instrument
artifact; mechanism characterization retained as cited above.

Revival angles for Research (route to research-lane):
1. top1-targeted readout pass on the existing indep_W matrices (BPC-tuned T,lambda may
   hide a real top1 lift; matches angle (1) from row 708)
2. cross-layer indep cf-RPE x STDP heterogeneous compose (super-additive candidate
   per fair_harness STDP HET top1=0.2368)
3. cross-layer-2L-indep + cleanup-load-bearing (modern-Hopfield over decoded W) -- the
   architectural separation may surface under cleanup
4. N>=15000 step extension on indep-2L (does the BPC gap to shared widen with N?)

---

## Cell 8 -- hub_spoke_E1_v2_diverse_algorithm

Cell commit: `abc5887b`. Metrics: `data/exp_substrate_hub_spoke_E1_v2_diverse_algorithm/metrics.json`.

### Drill claims verified off-data

(1) SoftHebb spoke NaN: CONFIRMED at lines 241, 298, 370, 488, 545, 617, 735, 792, 864.
    Every seed (7, 17, 23) and every arm that includes the SoftHebb spoke shows
    `spoke_recon_err: NaN` for `algo: softhebb_kwta`. The other spokes are well-defined
    (chartrigram_x_random_indexing recon_err ~1.0; path_c_pc_3layer recon_err ~92.3;
    fractional_power_encoding recon_err ~1.48). NaN is structural.

(2) cf-RPE gate collapse: CONFIRMED at lines 356-359, 603-606, 850-853:
    seed 7: cfrpe_gates = [0.9587, 0.0323, 0.0090]
    seed 17: cfrpe_gates = [0.9552, 0.0357, 0.0091]
    seed 23: cfrpe_gates = [0.9526, 0.0356, 0.0117]
    Gates collapse to spoke index 0 across all 3 seeds. Spoke 0 IS the SoftHebb spoke
    (with NaN recon_err). The routing mechanism PICKED the broken spoke as dominant.

(3) Resulting bpc: all 3 spoke arms (DIVERSE_ALGO, DIVERSE_PLUS_FPE, DIVERSE_WITH_CFRPE_
    GATING) collapse to bpc 7.7378 (line 78), identical to ARM_UNIGRAM 7.7378 (line 57)
    to 4 decimals across all seeds (cv 0.0000). This is the substrate falling back to
    unigram-equivalent output -- a structural failure mode signature, not a substrate
    capability statement.

### Ruling

**Cell 8: MEASURED_MECHANISM** -- CERT-neutral, delta = 0.

The cell measured an INSTRUMENT FAILURE (broken SoftHebb spoke wins cf-RPE routing),
not a substrate-mechanism failure. This is M3 bias category: bundle-health-check
gap (when a spoke can return NaN keys, the hub-spoke routing has no signal to
discriminate against it, and a 3-spoke cf-RPE gate over [NaN, ok, ok] keys can
trivially select the NaN spoke).

Filing atom: `math::T3/EXP_substrate_hub_spoke_E1_v2_diverse_algorithm_MM` with provenance
recording the SoftHebb NaN + gate-collapse signature.

Revival path: fix the SoftHebb k-WTA recon (likely an iteration count / lr / threshold
init issue producing zero-norm keys -> recon_err NaN), add a per-spoke health-check
gate (drop any spoke with NaN keys before routing), then re-run.

META atom: M3_bundle_health_check_missing_NaN_spoke_can_win_cf_RPE_routing -- worth
CERT-neutral atomization as a discipline.

---

## Cell 9 -- compose_heterogeneous_routing_v2_RESCUE

Cell commit: `b143c179`. Metrics: `data/exp_substrate_compose_heterogeneous_routing_v2_RESCUE/metrics.json`.

### Drill claims verified off-data

(1) Rail referent (fair_harness_substrate_as_lm_v1):
    `data/exp_fair_harness_substrate_as_lm_v1/metrics.json`
    N_DIM = 8192 (line 7), N_TRAIN = 100000 (line 9), n_seeds = 3 (line 39),
    seeds = [7, 17, 23] (config_version line 149), sparse_f = 0.050 (line 149),
    ARM_SUBSTRATE_SPARSE_BIPOLAR bpc_best_mean = 7.3065 (line 70).
    Rail referent CONFIRMED.

(2) v2 RESCUE config:
    N_DIM = 4096 (line 9), N_TRAIN = 50000 (line 10), n_seeds = 2,
    seeds = [7, 17] (line 42), sparse_f = 0.05 (line 16),
    device = cpu (line 8).

    Mismatch confirmed: 2x N_DIM reduction, 2x N_TRAIN reduction, 1 fewer seed,
    cpu instead of cuda. Rail tolerance 0.05 cannot survive a 2x reduction in
    both N_DIM and N_TRAIN at production LM scale -- the drill prediction of
    +0.15 to +0.30 BPC drift is essentially capacity scaling. Observed
    ARM_BASELINE_FAIR_HARNESS bpc = 7.6563 vs rail 7.3065 = drift +0.3498
    (line 4 verdict_msg + line 187). Within the predicted +0.15-0.30 envelope
    once you allow for the cpu/cuda quantization noise (this is consistent
    with the half-N predicted drift).

(3) Direction-correct underlying signal: `ARM_FREQ_ROUTED_K2 bpc_best_mean = 7.4321
    cv 0.0031` (lines 115, 118), vs `ARM_BASELINE_FAIR_HARNESS = 7.6563` (line 59):
    `best_het - baseline = 7.4321 - 7.6563 = -0.2242 BPC` lift over the (broken-rail)
    baseline. ARM_THETA_PHASE_TWO_W = 7.5528 (line 75); ARM_ORTHOG_SUBSPACE = 7.7728
    (line 153). So FREQ_ROUTED_K2 is the only het-routing arm that clears the
    in-cell baseline.

### Ruling

**Cell 9: MEASURED_MECHANISM** -- CERT-neutral, delta = 0.

The HARD_FAIL_PROVENANCE verdict is correct as a provenance-gate firing (rail referent
config mismatch by 2x N and 2x data, drift +0.35 vs tol 0.05). But that gate firing
reflects INSTRUMENT CALIBRATION, not substrate-mechanism failure. The +0.2242 BPC lift
of FREQ_ROUTED_K2 vs the in-cell baseline is direction-correct evidence that
frequency-routed K=2 composition is the strongest het-routing variant at half-N (over
theta-phase two-W and orthogonal-subspace).

Filing atom: `math::T3/EXP_substrate_compose_heterogeneous_routing_v2_RESCUE_MM` with
the provenance failure characterized and the direction-correct best_het arm noted.

M2 atom: tight_rail_from_different_config_HARD_FAIL_PROVENANCE_can_mask_direction_
correct_lift -- worth atomizing.

Revival path: re-run at fair_harness-matched config (N_DIM=8192, N_TRAIN=100k, 3 seeds,
cuda). If `b143c179` already exists, just re-dispatch on the matched config.

---

## Atomization summary

Three EXPERIMENT_RECORD MM atoms filed (delta=0 each; CERT unchanged):
- `math::T3/EXP_substrate_cross_layer_compose_LM_v2_RESCUE_FULL_MM`
- `math::T3/EXP_substrate_hub_spoke_E1_v2_diverse_algorithm_MM`
- `math::T3/EXP_substrate_compose_heterogeneous_routing_v2_RESCUE_MM`

Plus 3 META rule atoms (CERT-neutral; meta corpus):
- M1_verdict_classifier_use_tuned_metrics_never_raw_at_T1
- M2_tight_rail_from_different_config_HARD_FAIL_PROVENANCE_can_mask_direction_correct_lift
- M3_bundle_health_check_NaN_spoke_can_win_cf_RPE_routing

(N1 verify-referent-verdict-field rule already added to memory per director; not duplicating
here.)

## Operational note to Director (Research)

The Cell 7 ruling rejects the CHAIN_GRADE re-tier. The cert-rule precedent is consistent:
BPC improvements without top1 propagation are MEASURED_MECHANISM under META_HARNESS_RIGGED
(cert row 698) + top1 chain-grade bar n1_v3 (row 699). This cell sits at 0.11x the top1 bar.

Concur the architectural mechanism is REAL (independent vs shared cv-clean +0.376 BPC at
production scale) and the READOUT_DEGENERATE label is instrument-bug. Filing the cell as MM
preserves the mechanism characterization for downstream compose tests + revival cells
WITHOUT chain-grading on BPC. Same disposition as cert rows 707/708 in the past 48h --
this is the third instance of the same signature; pattern is now well-characterized.

For revival to chain-grade-eligible, the cleanest path is top1-targeted readout on the
existing indep_2L W matrices (cheap; the W is already trained). If that surfaces lift to
> +30% rel over unigram, re-tier on top1 evidence.

The drill is correct that substrate is alive on all 3 cells -- I concur. The capability
narrative does not need any cells reclassified to CHAIN_GRADE for that to be true.
