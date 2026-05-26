# Pre-reg: Wave 14 muSR Kubo-Toyabe analog v1

**Filed:** 2026-05-22
**Source:** `research_materials_characterization_methods_2026-05-22.md` (Research Entry 140, 13:55 EDT) — top-recommended probe #3 (P=0.80).

## Question

When the substrate at α=0.15 is run as Glauber-MC dynamics, does its spin autocorrelation G(t) = ⟨s(0)·s(t)⟩/N follow the static Kubo-Toyabe Gaussian decay G(t) ~ exp(−Δ²t²/2), or stretched-exponential (dynamic regime)?

Research's hypothesis: substrate is a spin glass per Bet E ✅. Static random-Gaussian-field interpretation predicts Gaussian decay; dynamic averaging predicts stretched exponential (β < 2).

## Hypothesis

H_static: Gaussian fit r² ≥ 0.85 AND stretched-exp r² doesn't beat Gaussian by > 0.05. Substrate is in the static-Gaussian-field Kubo-Toyabe limit.

H_dynamic: stretched-exp r² − Gaussian r² > 0.05. Substrate has additional dynamic averaging (RSB-class slow modes contribute).

## Pre-declared verdicts

- `KUBO_STATIC` — Gaussian r² ≥ 0.85; stretched-exp doesn't significantly beat.
- `KUBO_DYNAMIC` — stretched-exp r² beats Gaussian r² by > 0.05; β < 2.
- `KUBO_MIXED` — neither fit clean.
- `KUBO_INCONCLUSIVE` — metric collection error.

## Method

1. Generate M=⌈αN⌉ random bipolar patterns; W = (patterns^T @ patterns) / N; zero diagonal.
2. For n_replicates trajectories: init random s; run Glauber MC at β_mc=2.0; record m(t)=⟨s(t)·s(0)⟩/N at each sweep t.
3. G(t) = average m(t) across replicates.
4. Fit Gaussian: log(G(t)/G(0)) = −½ Δ² t². Linear regression on (t², log(G/G(0))) → Δ and r².
5. Fit stretched: log(−log(G/G(0))) = β log(t) + const. Log-log linear regression → β and r².

## Acceptance thresholds

- 0.85 r² Gaussian = "clean static fit" per spin-glass NMR/muSR literature.
- 0.05 r² gap = "stretched-exp significantly better" threshold.

## Config

- N=256 smoke, 1024 full.
- α=0.15 (substrate operating point per Strategy observability suite spec).
- β_mc=2.0 (Glauber temperature).
- n_sweeps=30 full, 15 smoke.
- n_replicates=30 full, 10 smoke.
- seed=17.

## Pre-declared interpretation

- **STATIC**: substrate behaves as if local fields are static-Gaussian-distributed; consistent with paramagnetic-like or weak-glass dynamics. Δ_rms gives canonical disorder strength.
- **DYNAMIC**: substrate has additional dynamic averaging; β < 2 stretching is the RSB signature. Couples to Cugliandolo-Kurchan 1993 aging framework.
- **MIXED**: insufficient signal; longer MC chain needed.

## Substrate-product framing

Bet E ✅ Parisi P(q) already certified RSB phase at substrate's operating point. muSR analog is the **second-order time-domain** observable that should AGREE with P(q) RSB via stretched-exponential. Cross-family certification.

## Not in scope

- Multi-α sweep (single α=0.15).
- Multi-β_mc sweep (single β=2.0).
- Comparison vs analytic Kubo-Toyabe with known Δ (this is a substrate-self-characterization).
