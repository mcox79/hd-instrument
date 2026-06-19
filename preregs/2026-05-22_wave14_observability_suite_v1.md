# Pre-reg: Wave 14 Substrate Observability Suite v1

**Filed:** 2026-05-22
**Source:** `strategy_request_to_exp_dev_observability_suite_v1_2026-05-22.md` (Strategy 14:25 EDT)
**Source:** `research_substrate_observability_deep_drill_2026-05-22.md` (Research 14:10 EDT)

## Question

When the substrate is loaded at α=M/N=0.15 (Hopfield critical-loading regime) and run as a Glauber Ising dynamical system, do two independent spin-glass diagnostic probes (Priority 1 + Priority 3 from Strategy's request) agree on the phase classification?

## Hypothesis

Substrate is empirically in RSB phase per Bet E ✅ Parisi P(q). Two new probes:
- Family I (C_ij eigvalsh): RSB ↔ >1 extensive eigenvalue in excess of W's structure
- Family II (P(h) histogram): FROZEN ↔ bimodal local-field histogram

H_certify: both families agree (cross-family certification standard from Entry 141).

## Pre-declared verdicts

- `OBS_SUITE_RSB_CERTIFIED` — C_ij excess > 1 AND P(h) bimodal/frozen agree on RSB phase.
- `OBS_SUITE_RS_CERTIFIED` — C_ij excess ≤ 1 AND P(h) unimodal narrow agree on RS phase.
- `OBS_SUITE_AMBIGUOUS` — probes disagree OR marginal counts.
- `OBS_SUITE_INCONCLUSIVE` — metric collection error.

## Method

1. Construct Hopfield W = (1/N) Σ_μ ξ_μ ξ_μ^T (zeroed diagonal) with M=⌈αN⌉ random bipolar patterns.
2. Run Glauber MC at β=2.0 for n_burn sweeps, then sample every sample_interval sweeps for n_sample configs.
3. **Probe C_ij**: time-average correlation C_ij = ⟨s_i s_j⟩ − ⟨s_i⟩⟨s_j⟩; compare extensive eigval count (λ/N > 0.1) of C vs W; report excess.
4. **Probe P(h)**: h = W s; aggregate across all samples × sites; bimodality coefficient b = (skew² + 1)/kurt; FROZEN if b > 0.555. Wipeout fraction = mean(|h| > 2σ).

## Acceptance thresholds

- 0.1 N relative-magnitude threshold for "extensive" eigval (per Sinova-Houdayer-Martin).
- 0.555 bimodality coefficient = canonical SAS threshold.
- 0.10 wipeout fraction = paramagnet cutoff.

## Config

- N=256 smoke, 4096 full.
- α=0.15, β=2.0.
- Full: n_burn=200 sweeps, n_sample=500 configs, sample_interval=50 sweeps.
- Single seed=17 (initial scan; multi-seed only if result depends on seed).

## Pre-declared interpretation

- **RSB_CERTIFIED**: substrate-physics characterization sharpens. cap_map promotion: "classical-Hopfield-class in RSB phase". Confirms Bet E ✅ via two new families.
- **RS_CERTIFIED**: substrate is NOT in RSB at α=0.15 / β=2.0. Re-examine Bet E methodology OR Strategy's "α=0.15 operating point" choice.
- **AMBIGUOUS**: need longer MC chain or third probe (Priority 2 = P(q) replica overlap, v2 follow-up).

## Not in scope

- Priority 2 P(q) replica overlap probe (requires PT MC, deferred to v2).
- Kerdock or non-random patterns (canonical Hopfield = random bipolar per Strategy spec).
- Multi-temperature sweep (single β=2.0).
- Multi-α sweep (single α=0.15 per Strategy spec).
