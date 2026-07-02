# Design Discipline — Mandatory Saturation Check for Dim-X Sweep Cells

**Filed:** 2026-07-02 (session late)
**Trigger:** Sonnet dense-HF underloaded-saturation-theory 2x drill (`research_dense_hopfield_underloaded_saturation_theory_2x_drill_2026-07-02.md`)
**Root cause:** Twin HF cells today (Dim H distributional shape + Dim S metric dependence) both fell over onto ceiling saturation at α ≤ 0.30 because CLT washout at N=8192 gives dot-product std 0.011 vs margin 0.976 — discriminator cannot see distribution/metric variation.

## The Discipline

Every Dim-X sweep cell (where X is a substrate characteristic being probed at underloaded regime) must include a pre-file information-theoretic saturation check in the pre-reg **before** the cell is authored.

**Formula (computed in Python at pre-reg author time, cited as MEASURED@formula):**

```python
import math

# For each intended sweep point (alpha, f):
M = alpha * N
noise_frac = f            # bit-flip fraction (0.0 = clean query)
margin = (1 - 2 * noise_frac) - math.sqrt(2 * M * math.log(M)) / N

if margin > 0.10:
    # DISCRIMINATOR SATURATION WARNING
    raise ValueError(f"SATURATION at alpha={alpha}, f={f}, N={N}: margin={margin:.3f} > 0.10 threshold. Cell will vacuously saturate; add noise arm (f>=0.43) or supra-alpha arm (alpha>=0.88).")
```

**Threshold justification:** margin < 0.10 places the substrate in a regime where distribution/metric/architecture variations (perturbing dot products at std ~ 1/sqrt(N)) are visible above the retrieval margin. Above 0.10 the substrate is in structural saturation and any Dim-X probe will hit 1.000 vacuously.

## Remediation Options

If pre-reg's target regime shows margin > 0.10 at all intended points, cell-author MUST add one of:

### Option 1 (preferred — cheap): Noise arm
Add an arm at `f = 0.43-0.46` bit-flip noise (or FHRR gaussian σ = 0.35 equivalent). This:
- Runs on same CPU compute as clean arm
- Tests substrate in a regime where mechanism differences are visible (softmax margin dominance drops to ~0.14, below the 0.976 clean-query margin)
- Does not require GPU or scale change

### Option 2 (more work — decisive): Supra-α arm
Add an arm at `α = 0.88-0.92` (past classical AGS wall for clean substrate, into discriminating zone predicted by Sonnet drill). This:
- Tests actual operational wall (Hebbian+argmax at ρ=0 has wall ~ 0.85)
- Requires slightly larger M so more compute
- Directly complements Löwe correlated-key CG (which mapped α_c(ρ) for ρ > 0)

### Option 3 (rare): Close the angle
If the intended Dim-X probe simply doesn't discriminate for THIS substrate mechanism at ANY regime, close the angle as "HF_STRUCTURAL_BOUND — mechanism-class immune". This is what happened to Dim H v2 dense-Hopfield + Dim S v1 dense-Hopfield today.

## Why This Matters

Without this check, cell-authors ship Dim-X sweeps at default underloaded regime → discriminator saturates → HF_PROVEN_NEGATIVE atomization is legitimate but wasteful (~1 hr CPU per cell not counting sub-agent context). Discipline saves compute + generates FIRST-ORDER regime characterization (not just "substrate is invariant here" but "substrate operational wall is at α = 0.85").

## Convergent Findings

- **Correlated-key rho sweep v1 CG (Löwe 1998 α_c(ρ) ≈ 0.138(1-ρ²))** — mapped α_c on ρ axis; ρ=0 baseline stays at 1.000 through α=0.20 (matches CLT-washout theory)
- **Twin HF today** — Dim H + Dim S both hit ceiling because their probes are in the saturated regime
- **Sonnet dense-HF theory drill** — CLT washout root-cause + operational wall α ~ 0.85 for Hebbian+argmax substrate
- **Sparse-coding / compressed-sensing drill** — Donoho-Tanner phase boundary structurally isomorphic to substrate wall; AMP-analog cleanup gives operational discriminator

## Application to In-Flight Cells

**Dim H v3 Hebbian frequency-reinforce** — cell-author instructed to include full-N preview at Amit-Gutfreund wall M/N ∈ [0.10, 0.14]. Predicted Q1-Q4 gap in that regime; if the discipline check shows margin > 0.10 at all pre-reg points, cell-author must add noise arm before dispatch.

**Dim S v3 fine σ cliff bracket** — bracketing the transition zone at fine σ IS the noise arm approach. Explicitly compliant with discipline.

**Substrate operational wall α fine sweep v1** — new cell dispatched to CG the α ∈ [0.60, 0.95] × f ∈ [0.0, 0.43] regime for chain-grade substrate wall characterization.

**Adversarial key gap crossing v1** — PGD attack IS noise-in-adversarial-direction; naturally discriminating regime.

**Cross-axis discriminating arm v2** — Skunkworks-mandated discriminating arm at β=1.0 OR M≥32768 OR K≥4000. Complies via alternative discriminator (over-saturated regime).

## For Skunkworks/Testbed

If durability review confirms this is a load-bearing discipline (recommend YES), atomize into MEMORY.md as `feedback_mandatory_saturation_check_dim_x_sweep_cells_2026-07-02.md`. Alternative: encode into pre-reg author template so `preregs/_template_` includes the check as a MUST-COMPUTE field before pre-reg is filed.
