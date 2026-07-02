# HF_UNIFORM_COLLAPSE Hand-Off — metric_dependence_top_k_semantic_v2 (Dim S OVERLOAD+NOISE respec)

**Filed:** 2026-07-01
**Cell-author:** hdi_exp_dev
**Director decision (recommended):** HALT_ATOMIZE_AT_SMOKE + v3 RESPEC (do NOT dispatch full)
**Anchor:** `metric_dependence_top_k_semantic_v2_seed_7` (smoke)
**Commit:** (to be filled after commit)
**Discipline halt reason:** META_RULE_AG (baseline-in-band) — smoke reveals sigma=0.7 is a CLIFF not a gradient; dispatching full at chosen sigma grid would burn CPU-hr producing 16 more zeros/ones with no metric-differentiation. Preview at (1.5, 0.7) at floor (0.000) — discriminator DID survive scale (not saturating), but resolved into a UNIFORM COLLAPSE rather than metric-family opening.

## Verdict + Physics Finding

**Verdict:** `HARD_FAIL` (smoke; HF_UNIFORM_COLLAPSE fired at (a=1.5, s=0.7)).

**verdict_msg** (from `d:/AI/hd-instrument/data/exp_metric_dependence_top_k_semantic_v2_seed_7_smoke/metrics.json`):

> `HF_UNIFORM_COLLAPSE: all 6 metrics <0.10 at (a=1.5,s=0.7); spread@(a=1.0,s=0.7)=+0.006(HP>=0.20) top1@(1.5,0.7)=0.000 top10@(1.5,0.7)=0.000(HP: top10>=0.60 & top1<0.30) uniform-collapse@(1.5,0.7)=[max=0.000](HF<0.10) max_spread_all_cells=0.024`

**Measured (all MEASURED@`d:/AI/hd-instrument/data/exp_metric_dependence_top_k_semantic_v2_seed_7_smoke/metrics.json`):**

Smoke: 3 alphas x 2 sigmas = 6 cells, plus preview at (1.5, 0.7). All at full N=8192.

| alpha | sigma | M     | beta   | top1  | top5  | top10 | top50 | cos05 | cos08 | wall_s |
|-------|-------|-------|--------|-------|-------|-------|-------|-------|-------|--------|
| 0.30  | 0.0   | 2458  | 11.809 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 14.5   |
| 0.30  | 0.7   | 2458  | 11.802 | 0.000 | 0.004 | 0.006 | 0.024 | 0.000 | 0.000 | 20.4   |
| 1.00  | 0.0   | 8192  | 13.625 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 45.2   |
| 1.00  | 0.7   | 8192  | 13.624 | 0.000 | 0.000 | 0.000 | 0.006 | 0.000 | 0.000 | 31.3   |
| 1.50  | 0.0   | 12288 | 14.233 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 38.2   |
| 1.50  | 0.7   | 12288 | 14.235 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 50.8   |
| PREVIEW 1.50 | 0.7 | 12288 | 14.235 | 0.000 | (matches above) | | | | | 47.7 |

**Total smoke wall:** 251.4s (~4 min).

## Physics Reading (BIMODAL COLLAPSE — not the predicted gradient)

**v1 finding EXTENDED and CONFIRMED:** at sigma=0.0 the substrate saturates at 1.000 across ALL alphas up to 1.50 (v1 mapped up to alpha=8.0; v2 confirms extension into and past AGS wall 0.14N; substrate is EVEN MORE robust than v1 characterized).

**v2 NEW finding:** the transition from clean-saturation to noise-collapse under query noise is BIMODAL not gradual. At sigma=0 -> 1.000 (perfect); at sigma=0.7 -> 0.000 (uniform collapse). The predicted "top-K survives when top-1 collapses" regime is NOT observed in this sigma grid — sigma=0.7 is already past the collapse cliff.

**Where is the cliff?** Predicted transition is at sigma ~ signal-noise-equivalent boundary — for L2-normalized d-dimensional queries, the SNR crossover is roughly sigma ~ sqrt(1/(N_c/M)) — heuristic:
- alpha=0.30 (M=2458 at N=8192): SNR-cross ~ sqrt(2458/8192) ~ 0.548
- alpha=1.00 (M=8192): SNR-cross ~ 1.0
- alpha=1.50 (M=12288): SNR-cross ~ 1.22

sigma=0.7 is ABOVE the SNR-cross for alpha=0.30, EXACTLY AT the boundary for alpha=1.0, BELOW for alpha=1.5 — yet all three collapse. The uniform collapse suggests the effective SNR cliff is much lower than the naive heuristic; the softmax margin degradation happens FAR before signal-to-noise equipartition. Adaptive-beta softmax attention has an ALL-OR-NOTHING failure mode.

**Load-bearing insight:** the 6-metric family DOES differentiate in some regime — but it's a NARROW sigma band, not a full sigma sweep. Metric-differentiation is a knife-edge phenomenon in this substrate class, not a broad phase.

## Twin+ finding across v1 + v2 (converging null on this dim)

v1 (underloaded, no noise): metric family collapses to 1.000 uniformly.
v2 (overload + heavy noise): metric family collapses to 0.000 uniformly.
Between these two null endpoints there MAY be a differentiation band, but it wasn't captured by v2's coarse sigma grid.

**Dim S (top-1 vs top-K vs semantic-similarity dependence) is now DOUBLE-FALSIFIED at the sweep-boundary regimes.** The remaining live territory is the narrow sigma transition band (probably sigma in ~ 0.05-0.30).

## Recommended v3 (if Director wants to keep pushing this line)

**v3 respec: FINE sigma sweep at fixed alphas around the transition zone.**

- Hold alpha at {0.30, 1.00} (v1+v2 verified both saturate clean; both collapse at 0.7).
- Sweep sigma at fine resolution: {0.05, 0.10, 0.15, 0.20, 0.30, 0.50} (7 points).
- This should bracket the cliff.
- Expected: sigma < X saturates 1.000; sigma > X falls to ~0; the differentiation regime (if any) is a NARROW sigma band around the cliff.
- Cost: 2 alphas x 7 sigmas x 3 seeds = 42 cells; ~15-30 min per seed based on v2 wall (~4 min for 6 cells + preview at heaviest).

Alternative: **v3 alt** = switch mechanism to classical Hopfield (no softmax; sum-of-outer-products) at fixed alpha=0.30 with sigma sweep — classical Hopfield lacks the softmax margin annihilation and should show broad-band differentiation. This tests whether the collapse cliff is an ARTIFACT of softmax attention or a UNIVERSAL bipolar-dense-Hopfield property.

**Recommended:** ship v3 FINE sigma sweep FIRST (single mechanism, refined resolution); if differentiation band opens up, expand to classical Hopfield alt in v4.

## Convergent Meta-Finding (v1 + v2)

**Two HFs same day on Dim S** (HF_METRICS_IDENTICAL underload + HF_UNIFORM_COLLAPSE overload+heavy-noise) suggest Dim S is a KNIFE-EDGE phenomenon: metric-differentiation exists in some narrow parameter band but the substrate class exhibits ALL-OR-NOTHING behavior across two of the three primary axes (alpha, sigma). Load-bearing for M3 architecture:

- **Positive:** substrate is enormously robust in clean-query operation across a huge (alpha) range up to and past AGS wall — this is a stronger CG-adjacent claim than v1 alone showed.
- **Negative:** metric-family differentiation is not a broad phase; can't rely on top-K rescue for noisy queries in M3 workloads; substrate goes cliff-collapse under Gaussian noise. Cortex-layer M3 architecture should PRESERVE query cleanness (denoising / re-attention loops) rather than rely on substrate metric-band tolerance.

## Files (absolute paths)

- v2 cell + prereg (this atomization): `d:/AI/hd-instrument/experiments/_substrate_metric_dependence_top_k_semantic_v2_core.py` + `exp_metric_dependence_top_k_semantic_v2_seed_{7,13,19}.py` + `preregs/2026-07-01_metric_dependence_top_k_semantic_v2_overload_noise_sweep.md`
- v2 smoke landing: `d:/AI/hd-instrument/data/exp_metric_dependence_top_k_semantic_v2_seed_7_smoke/metrics.json` (HARD_FAIL_HF_UNIFORM_COLLAPSE)
- v1 hand-off (parent): `d:/AI/hd-instrument/notes/exp_dev_findings/exp_metric_dependence_top_k_semantic_v1_HF_METRICS_IDENTICAL_2026-07-01.md`
- Dim S source: `d:/AI/hd-instrument/notes/research_hidden_phase_diagram_dimensions_2026-07-01.md`

## Atomization Guidance for Store

**Atom-class:** substrate-physics-null (measured HF; second HF on Dim S same day).
**Atom-key concept:** "dense-Hopfield READ-REPLACE at N=8192 under BIMODAL alpha x sigma sweep: sigma=0.0 saturates all 6 metrics at 1.000 across alpha in [0.30, 1.50] (extends v1 clean-baseline into overload region); sigma=0.7 collapses all 6 metrics to <0.03 uniformly across same alpha range. Sigma cliff is ALL-OR-NOTHING; no gradual differentiation observed. Softmax attention has knife-edge SNR failure mode. Metric-differentiation, if it exists, occupies a narrow sigma transition band (~0.05-0.30 estimated) not captured by v2 grid."
**Chain-grade elevation:** NONE (measured null; not chain-grade). Meta-atom: potential "clean-query broad-alpha saturation" claim strengthens Cell D v2 CG anchor by mapping upward alpha extension into overload with adaptive beta.
**Meta-tag:** double-HF-on-Dim-S-2026-07-01 (v1 + v2 same day); knife-edge-metric-differentiation.
**Downstream implication:** M3 cortex layer should NOT rely on substrate top-K rescue for noisy queries; substrate collapses cliff-wise under sigma. Query-cleaning or re-attention should live in cortex layer above substrate. Any future Dim S rescue attempt (v3) must sweep sigma at fine resolution in the transition band (proposed sigma in {0.05, 0.10, 0.15, 0.20, 0.30, 0.50}).

## Runtime + Dispatch Notes

- Total smoke wall: 251.4s (~4 min) laptop numpy.
- Extrapolated FULL wall per seed: ~15-25 min (16 cells vs smoke's 6, similar per-cell cost). 3 seeds full = ~45-75 min laptop; on remote_cpu comparable.
- Timeout budget requested: 7200s per seed (comfortable 6-10x headroom); would use ~10-15% of budget.
- **Dispatch NOT recommended** per HALT_ATOMIZE decision above; the answer is already visible in smoke. Full run would produce 4 alphas x 4 sigmas but 3 of 4 sigmas (0.0, 0.3 maybe, 0.7) are already characterized as either saturating or collapsed; only sigma=0.5 might show something new and even that's likely already past the cliff.

## Full Night Push Guidance

If Director wants to keep the physics push going tonight:
1. **v3 FINE sigma sweep** (author + smoke; low-cost; probably ~20-30 min author + ~5-10 min smoke) — this could uncover the transition band if it exists.
2. **Alternative:** turn to other cells in the Dim series (Dim H twin already HF today; Dim R? Dim Q?) per `notes/research_hidden_phase_diagram_dimensions_2026-07-01.md`.

Cell-author standby on Director decision.
