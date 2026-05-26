# Pre-registration: wave14_glauber_kerdock_v1

**Date registered**: 2026-05-23
**Script**: experiments/exp_wave14_glauber_kerdock_v1.py
**Field-advisor candidate**: D1 Glauber dynamics on substrate codeword space (tier-1 semiconductor, anchor_yield=100%, score=5.0)
**Anchor**: D - Drift-diffusion to BP (Cap 3 + theorem anchor) - stochastic-dynamics adjacents
**Capability axis**: Cap 3 streaming-NESS extension to discrete codeword space (substrate-product capability map row)
**Framing**: substrate-product observability + cross-mechanism design-space coverage; NOT a paper claim

## Hypothesis

Single-spin heat-bath Glauber dynamics over the substrate's Kerdock-Hebbian
weight matrix W = (1/N) sum_mu xi_mu xi_mu^T (xi_mu = bipolar Kerdock
4-coset codeword) shows a substrate-characteristic bimodal stationary
P(q) distribution at low temperature, with peaks at q ~ 1 (retrieval mode)
and q ~ 0 (noise / paramagnetic mode). The transition temperature T_c is
the substrate-internal Hopfield retrieval threshold on Kerdock codewords.

This is structurally distinct from the spectral / free-probability probe
of Exp 1 (free cumulants on Kerdock spectrum) — Glauber dynamics is a
DYNAMICAL probe of the Hopfield landscape on Kerdock codewords, complementary
to the static SPECTRAL probe.

Brutal-honesty P estimates:
- P(low-T cells, beta >= 4, show bimodal_score >= 0.5 and abs_mean_q >= 0.3
  on majority of cells): **0.55** — Kerdock has Welch-bound-quasi-orthogonal
  codewords so individual rank-1 stored patterns should produce energy
  minima at q = +-1 and the symmetric mixed state at q = 0; Glauber should
  recover this classical Hopfield phenomenology
- P(temperature sweep reveals clean T_c crossover): **0.50**
- P(verdict = UNIMODAL — Glauber utterly fails on Kerdock): **0.15** —
  possible if Kerdock structure breaks single-spin ergodicity (likely
  rescue via cluster moves; would be a surprising finding)
- P(INCONCLUSIVE): **0.30**

The experiment is informative under all three verdicts; UNIMODAL would be
a substrate-novel surprise (suggesting Kerdock codewords are NOT recoverable
by single-spin Glauber, only by collective dynamics).

## Config (FULL)

- N = 1024 (Glauber sweep is O(N^2) per sweep; 5*5*5*300 sweeps * O(N^2)
  must stay under 1 hour on remote CPU)
- alpha_list = [0.25, 0.5, 1.0] (loading regimes below, at, above classical
  Hopfield critical alpha_c ~ 0.138 — we want to span the classical
  transition)
- beta_list = [0.5, 1.0, 2.0, 4.0, 8.0] (T = 2, 1, 0.5, 0.25, 0.125)
- n_seeds = 5 per (alpha, beta) cell
- n_burn = 100 sweeps; n_collect = 200 sweeps
- Init: target codeword with 30% bit-flips
- Total cells: 3 * 5 = 15; total chains: 15 * 5 = 75
- Per chain: 300 sweeps * O(N^2 / cache) numpy mat-vec on N=1024 ~= 300 *
  10 ms = 3 sec
- Total: ~225 sec wall; with overhead, ~5-10 min. Timeout = 3600 s.

## Predictions (falsifiable, with hard-fail thresholds)

For each (alpha, beta) cell, compute mean bimodal_score and abs_mean_q
across 5 seeds.

- **BIMODAL_KERDOCK**: at low-T cells (beta >= 4), at least half satisfy
  bimodal_score >= 0.5 AND abs_mean_q >= 0.30 (retrieval regime confirmed)
- **UNIMODAL_KERDOCK**: ALL cells have bimodal_score < 0.2 AND abs_mean_q
  < 0.15 (no retrieval found at any T)
- **INCONCLUSIVE**: mixed

Hard-fail / kill criteria:
- If verdict self-test (4 hand-crafted cases) fails: halt
- If smoke crashes due to Kerdock builder at N=256: try N=512 smoke; if
  still fails, file upstream-push to Strategy
- If high-T cell (beta=0.5) shows bimodal_score > 0.6: indicates a bug
  (high-T should be paramagnetic, q concentrated at 0); halt and investigate

## Runtime / queue routing

- Pure numpy (no CUDA imports). Long-running (~5-10 min).
- Routes to **remote_cpu_queue** per Rule 2: pure CPU, >5 min, benefits
  from remote machine's persistent CPU runner; GPU is reserved for the
  free-cumulants experiment.
- Timeout = 3600 s (6x headroom)

## Smoke result (pre-registration gate)

Smoke config: N=1024 (forced by Kerdock builder PRIMITIVE_POLY registry:
only t=5 -> N=1024 and t=6 -> N=4096 supported), alpha=0.5 (M=512), beta in
{1.0, 4.0}, n_seeds=2, n_burn=30, n_collect=50. Runtime: ~30 sec.

Note on dynamics: original prereg said "single-spin sequential Glauber";
updated to **synchronous heat-bath parallel update** because sequential
Python loop at N=1024 is impractical. Synchronous Peretto 1984 dynamics
shares equilibrium phase structure with sequential Glauber for symmetric
diag-zero W (Bolle 1991, Hertz-Krogh-Palmer 1991 Ch. 4). May exhibit
period-2 cycles at zero T; harmless for stationary P(q) statistics.

Result (2026-05-23 ~18:43):
- Self-test 4/4 PASS
- beta=1.0 (high T): mean_q ~ 0.07, bimodal_score = 0.0 (paramagnetic;
  expected)
- beta=4.0 (low T): mean_q ~ 0.19, bimodal_score = 0.0
  -> abs_mean_q RISES with beta (good — substrate trends toward target)
  -> but bimodal_score still 0 at smoke; SMALL chain (50 samples) gives
     coarse histogram; FULL with n_collect=400 should give finer resolution
- Smoke verdict: GLAUBER_INCONCLUSIVE (expected at this small-N high-alpha
  short-chain config; alpha=0.5 is near AGS critical loading where bimodal
  retrieval is marginal even in classical theory)
- metrics.json: data/exp_wave14_glauber_kerdock_v1_smoke/metrics.json

Smoke does NOT predict FULL: the FULL config spans alpha=[0.25, 0.5, 1.0]
across beta=[0.5, 1.0, 2.0, 4.0, 8.0] with 4x longer chains; alpha=0.25
cell sits well below AGS critical loading where bimodal retrieval should
be cleanly observed if the substrate supports finite-T Hopfield phase.

## Failure modes / escalation

- If N=256 smoke crashes on Kerdock build: fall back to N=512; document.
- If smoke runtime > 2 min: re-estimate FULL timeout; halt before FULL if
  estimate exceeds 1 hour.
- If verdict on FULL is UNIMODAL (no retrieval found): notable substrate-
  novel finding — single-spin Glauber on Kerdock-Hebbian W is dynamically
  insufficient. Followup probes: cluster moves (Wolff/Swendsen-Wang), or
  zero-T initialization at target codeword (test stability rather than
  recovery).

## Linkage to Exp 1 (free cumulants) and to AMP_SE_DIVERGES

This is a cross-mechanism probe in the design-space subtree rooted at
AMP_SE_DIVERGES:

  AMP_SE_DIVERGES (Kerdock outside AMP universality)
    -> Spectral mechanism: Exp 1 (free cumulants kappa_n vs MP)
    -> Dynamical mechanism: Exp 2 (Glauber P(q) on Kerdock-Hebbian)

If both fire (DIVERGE + BIMODAL): converged substrate-novel observability
across spectral + dynamical axes; the Kerdock codebook is rich enough to
host both finite-T retrieval and non-MP higher cumulants. Substrate-product
implication: capability map gains a "Glauber retrieval envelope" row.

If Exp 1 MATCH + Exp 2 BIMODAL: Glauber retrieval works despite MP-like
free cumulants -> non-spectral mechanism for finite-T retrieval; followup
probe IPR.

If Exp 1 DIVERGE + Exp 2 UNIMODAL: spectral richness without dynamical
accessibility; followup probe cluster Monte Carlo.

If Exp 1 MATCH + Exp 2 UNIMODAL: AMP_SE_DIVERGES is mechanism unclear;
followup probe should look at noise model or measurement-process artifacts.
