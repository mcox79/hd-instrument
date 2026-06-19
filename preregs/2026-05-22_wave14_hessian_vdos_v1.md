# Pre-reg: Wave 14 Hessian VDOS v1

**Filed:** 2026-05-22
**Source:** `research_materials_characterization_methods_2026-05-22.md` (Research Entry 140, 13:55 EDT) — top-recommended cheap probe #1.

## Question

At α=M/N=0.15 (substrate operating point), does the substrate's Hopfield W matrix have soft-mode density consistent with RSB-class flat directions?

Research's hypothesis: substrate is empirically in RSB phase (Bet E ✅). Soft-mode density (eigenvalues near 0) is the direct VDOS analog from materials science.

## Hypothesis

H_softmodes: fraction of |eigvals| ≤ 0.01·λ_max ≥ 0.20 (substantial flat-direction density) at α=0.15 N=4096. Consistent with RSB.

H_sharp: fraction < 0.05 (substrate W is sharp/non-degenerate). Paramagnet- or ferromagnet-like.

## Pre-declared verdicts

- `VDOS_SOFTMODES_RSB` — soft-mode fraction ≥ 0.20.
- `VDOS_SHARP` — soft-mode fraction < 0.05.
- `VDOS_INTERMEDIATE` — 0.05 ≤ fraction < 0.20.
- `VDOS_INCONCLUSIVE` — metric collection error.

## Method

For each (N, α) pair:
1. Generate M=⌈αN⌉ random bipolar patterns.
2. Build W = (patterns^T @ patterns) / N; zero diagonal.
3. `eigvals = torch.linalg.eigvalsh(W)`.
4. λ_max = max |eigval|; soft threshold = 0.01·λ_max.
5. soft_mode_fraction = mean(|eigvals| ≤ soft threshold).

Canonical run for verdict: largest N at α=0.15.

## Acceptance thresholds

- 0.20 RSB threshold matches Research Entry 140 soft-mode interpretation.
- 0.05 sharp threshold = "negligible flat directions".

## Config

- N_grid full: [1024, 2048, 4096].
- α_grid full: [0.05, 0.15, 0.30, 0.50].
- soft_threshold_rel=0.01.
- Single seed=17.
- Smoke: N=[256, 512], α=[0.15].

## Pre-declared interpretation

- **RSB**: substrate W's soft modes confirm RSB phase via VDOS. New observability primitive: cross-check vs C_ij eigvals (Observability Suite v1) for cross-family certification.
- **SHARP**: substrate W is non-degenerate — contradicts Bet E ✅ RSB finding. Audit Bet E methodology OR investigate α-dependence.
- **INTERMEDIATE**: substrate sits between regimes. Map full VDOS shape vs α to identify transition.

## Cost

eigvalsh(W) at N=4096: ~1-3 seconds. Full sweep: <30 seconds. Cheapest substrate-physics probe per Research.

## Not in scope

- Comparison vs Wigner / Marchenko-Pastur baseline (separate experiment if needed).
- α > 0.50.
- Non-Hopfield W (Hebbian only).
