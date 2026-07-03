# INFORMAL_DIAGNOSTIC MM_TENTATIVE: H2 mechanism degeneracy at non-saturated SHARDED FHRR

Atom ID: `INFORMAL_DIAGNOSTIC_PROBES_H2_MECHANISM_DEGENERACY_HOLDS_AT_NON_SATURATED_SHARDED_FHRR_TENTATIVE_2026-07-03`

Tier: MM_TENTATIVE (informal cell-author diagnostic; not prereg-gated; requires
Probe 6 v2 SMOKE + FULL replication to promote to MM_STANDARD)

Filed by: exp_dev 2026-07-03 (Opus 4.7 agent-spawn, cell author for Probe 6)
Origin: Probe 6 v1 HARD_FAIL_SMOKE bracketing diagnostic (informal probes
outside prereg-registered SMOKE grid, characterizing SHARDED-storage cliff).

## Claim

At every non-saturated SHARDED-rule-storage FHRR chain composition regime
tested informally (N=512, M=6400 at corr=[0.85, 0.90], F ∈ {1, 4, 8, 16}),
the 3 non-Hebbian cleanup mechanisms (modern_hopfield, iterative_cosine,
soft_energy_attractor) produced IDENTICAL per-arm accuracy. This is
preliminary evidence for **H2 mechanism degeneracy holds at non-saturated
SHARDED regime** (mechanism axis is structurally degenerate, not just a
saturation artifact as Probe 3 was accused of).

## Cited measurements (exp_dev bracketing probe, no prereg registration)

| Regime | 3-mech accs | Delta |
|---|---|---|
| N=512 M=3200 corr=0.85 F=16 | [0.8667, 0.8667, 0.8667] | 0.00 |
| N=512 M=6400 corr=0.90 F=1  | [0.0000, 0.0000, 0.0000] | 0.00 |
| N=512 M=6400 corr=0.90 F=4  | [0.1000, 0.1000, 0.1000] | 0.00 |
| N=512 M=6400 corr=0.90 F=8  | [0.0667, 0.0667, 0.0667] | 0.00 |
| N=512 M=6400 corr=0.90 F=16 | [0.1000, 0.1000, 0.1000] | 0.00 |
| N=1024 M=6400 corr=0.90 F=16 | [0.6000, 0.6000, 0.6000] | 0.00 |

## COUNTER-EVIDENCE (v2 SMOKE, prereg-registered)

Probe 6 v2 SMOKE at N=512 M=6400 corr=0.85 (nearer the cliff than most bracket
probes above) shows mechanism DIVERGENCE:

| Regime | modern_hopfield | iterative_cosine | soft_energy_attractor | Delta |
|---|---|---|---|---|
| N=512 M=6400 corr=0.85 F=1  | 0.8500 | 0.7500 | 0.6500 | 0.20 |
| N=512 M=6400 corr=0.85 F=16 | 0.6750 | 0.6250 | 0.8250 | 0.20 |

max_per_F_mech_var_in_band = 0.20 (>= 0.10 threshold for H1). Mech-ranking
crossover across F: at F=1 modern_hopfield leads; at F=16 soft_energy leads.

## Honest interpretation (methodology reset)

Informal probe H2-evidence was at extreme regimes (corr=0.90 mostly, all past
the cliff at N=512). v2 SMOKE at corr=0.85 (mid-band cliff) shows mechanism
DIVERGENCE and ranking CROSSOVER — this is H1+H3 evidence, NOT H2.

Revised MM_TENTATIVE reads:

> Mechanism degeneracy in SHARDED FHRR chain composition may be regime-dependent:
> at FAR-from-cliff (all-saturated or all-broken) regimes, mechanism degeneracy
> holds. At NEAR-cliff (mid-band mean_acc ~0.7) regimes, mechanism divergence
> and ranking crossover appear. This suggests TOPOLOGY (F) IS a moderator of
> CLEANUP_MECHANISM at the specific band around the SHARDED-storage cliff.

## Promotion criteria to MM_STANDARD

Probe 6 v2 FULL (217 pts x 3 seeds; N ∈ {512, 2048} x corr ∈ {0.70, 0.85, 0.90}
x M x F) must show:

- Consistent mech-variance pattern across in-band cells (in_band_frac >= 30%)
- Cross-seed CV < 0.10 on per-cell accs
- Formal F_x_cleanup_max_abs_deviation_in_band + max_per_F_mech_variance_in_band
  computed per aggregate_and_verdict()

If v2 FULL reports HARD_PASS_H1_TOPOLOGY_MODERATES_WHEN_NON_SATURATED, then
this MM_TENTATIVE atom SUPERSEDES to that CG landing.

If v2 FULL reports HARD_PASS_H2_MECHANISM_DEGENERACY_HOLDS_AT_NON_SATURATED
(i.e., mech-variance stays < 0.05 across full grid), then the informal probe's
extreme-regime evidence was correct and v2 SMOKE was a lucky-band artifact.

## Skunkworks handoff

Skunkworks landed-VET should audit this note against v2 SMOKE metrics.json
and Probe 6 v2 FULL when landed. Do NOT formalize as CG atom until v2 FULL
is landed and Skunkworks-VETed.
