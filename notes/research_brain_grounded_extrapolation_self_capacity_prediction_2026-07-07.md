# Research: brain-grounded mechanisms for out-of-range self-capacity prediction

Filed by: research (Sonnet, main synthesis) + 4 parallel Sonnet lit-scan sub-agents.
Trigger: director task -- "THE FRONTIER QUESTION: can the substrate predict its own capacity/operating-point
BEYOND its experienced range, not just interpolate within it?" Grounds in the CHAIN_GRADE VET'd result
(commit 775b5cd92 / VET afd8dd68): reasoning-depth survival law beats constant + nearest-lookup on
INTERPOLATION (LOO MAE 1.20 vs 4.70 vs 1.65) but loses to nearest-lookup on the ONE true EXTRAPOLATION
fold (fill=0.3516: law err 1.86 vs lookup 1.60).

## HEADLINE

**Ranked brain mechanisms (most to least likely to convert interpolation-win into extrapolation-win):
(1) model-based prospective simulation from a learned TRANSITION model [formal RL theorem + hippocampal
preplay evidence], (2) theory-derived mechanistic functional form [EVT/percolation-universality precedent],
(3) cerebellar forward models [mechanism real but evidence argues AGAINST far-extrapolation -- it is local,
distance-decaying generalization, a useful NEGATIVE prior], (4) metacognitive uncertainty [does not fix
the point-estimate; adds a trust-gate].** I additionally RAN a cheap decisive test on already-landed data
(no new compute): swapping the current law's assumed-occupancy input `phi(fill)` for the ALREADY-RECORDED
measured mechanism proxy `phi(collision_frac_emp)` improves overall LOO MAE (1.06 vs 1.20) and narrows the
extrapolation-fold gap (err 1.75 vs 1.86) but still does NOT beat nearest-lookup there (1.60) -- directionally
confirms the mechanistic-substitution hypothesis, insufficient alone. Disk-verified finding: the naive
occupancy proxy (`fill`) systematically diverges from the measured collision fraction, and the divergence
GROWS with fill (-0.3% at fill=0.053 -> -5.0% at fill=0.352) -- exactly the region where extrapolation
currently fails. This is the concrete, falsifiable next-step target.

## Cheap decisive test

**Already run on landed data (zero new compute, reused `data/exp_reasoning_depth_keyslots_sharding_v1/metrics.json`):**
recompute the existing LOO loop's law using `phi(mean_collision_frac_emp)` in place of `phi(fill)` as the
regression feature (both already present per-arm in the metrics; loop machinery unchanged). Result:

| law variant | overall LOO MAE | extrap fold (fill=0.3516) err |
|---|---|---|
| current (phi(fill), a+b affine) | 1.201 | 1.86 |
| **mechanistic substitution (phi(measured collision), same affine fit)** | **1.061** | **1.75** |
| nearest-lookup baseline | 1.650 | 1.60 |
| constant baseline | 4.702 | 8.0 (mean of all folds; extrap-fold const err not separately dominant) |

Both `phi(fill)` and `phi(collision_emp)` laws OVERSHOOT the true extrapolation-fold depth (predict 5.26 /
5.15 vs actual 3.40); lookup undershoots less (5.00 vs 3.40, err 1.60). This is the tell: usable depth falls
off FASTER at the highest fill than either affine-in-phi model captures -- consistent with an unmodeled
curvature/second-order collision-interaction term, not just an input-proxy bias. Swapping the proxy helps;
it doesn't fix the curvature. That is the target for the GPU-testable cell below.

**Next-tier cheap test (before GPU spend):** refit the SAME two candidate laws with a quadratic term in
phi-space (`a + b*phi + c*phi^2`) on existing data -- still zero new compute, tests whether curvature alone
(no new mechanism, no new data) already closes the gap on the single existing extrapolation fold. If yes,
GPU spend on new provisioning levels is justified with high prior. If no, the failure is likely a genuine
regime-shift (see HARD-FAIL band) and new held-out levels are needed to characterize it, not just fit better.

## Falsifiable predictions

**Proposed cell:** `exp_reasoning_depth_mechanistic_survival_law_extrapolation_v1` (extends
`experiments/exp_reasoning_depth_capacity_provisioning_monitor_loop_v1.py`, commit 775b5cd92; reuses ALL
loop/control machinery -- OBSERVE/LAW/PROPOSE/SCORE + both firing controls C1 scramble-law, C2 scramble-curve).

1. **Derive a genuinely mechanistic law** (not a post-hoc empirical correction): candidate B is a per-hop
   transmission-coefficient / percolation-style compounding form, `p_hop = f(m_over_n, V/V_CHAIN)` derived in
   closed form from the substrate's actual bundling/superposition collision statistics (birthday-paradox-style
   collision probability over the real key/slot counts already in `metrics.json`: `N, V, V_CHAIN, m_over_n`),
   NOT an empirical 2-param affine fit to a collapsed scalar. `usable_depth* = argmax_D { p_hop(D)^D >= FLOOR }`
   composed over D hops, matching the mesoscopic-transport / percolation-critical-phenomena adjacency already
   flagged in the field-coverage map (Tier-1b, `mesoscopic-transport` and `percolation-critical-phenomena`,
   both anchored to the thermodynamics/semiconductor fruit-bearing fields) -- this lit-scan independently
   arrives at the SAME prescription via the brain/RL-theorem route. Cross-thread confirmation, not coincidence.
2. **Generate NEW provisioning levels beyond fill=0.3516** by re-running `exp_reasoning_depth_keyslots_sharding_v1`
   at additional `n_test`/`N` configs pushing fill to ~0.42, ~0.50, ~0.60 -- creating >=2 GENUINE held-out
   extrapolation folds (current design has exactly one, and it is also the top training point, which is a
   weak test of "beyond the range").
3. **Score:** on the NEW genuinely out-of-range folds, does the mechanistic law (candidate B, or the
   quadratic-in-phi refinement if the cheap next-tier test above confirms it) beat BOTH nearest-lookup AND
   the current empirical affine law?

**HARD-PASS:** mechanistic law MAE on all NEW extrapolation folds (fill > 0.3516) beats nearest-lookup by
>=20% AND beats the current empirical law, AND both firing controls (C1 scramble-law, C2 scramble-curve)
fire on the extended fold set, AND the model-based-RL theorem's precondition holds empirically (per-hop
collision statistics are approximately factored/reproducible across hops within a fold -- check via a
simple hop-to-hop autocorrelation test on collision_frac_emp, not assumed).

**HARD-FAIL:** mechanistic law does NOT beat nearest-lookup on the new extrapolation folds (same failure
mode persists even with the theoretically-correct functional form). This would be a DEEPER, more valuable
honest result than the current MIDDLE-ish caveat: it would show the extrapolation limit is a genuine
REGIME SHIFT at high fill (a percolation-style near-critical-point transition, where the substrate crosses
into a different collision regime not captured by ANY smooth pre-transition functional form) rather than a
fixable functional-form/proxy problem -- directly matching the ML lit-scan's documented failure mode
("a mechanistic form derived from one physical regime has no validity once the system crosses into a
different regime not represented in its governing equations"). A HARD-FAIL here is itself a publishable
substrate-physics finding: it would motivate hunting for the actual critical fill (analogous to a percolation
threshold) as a NEW measurable substrate constant, rather than continuing to refine the survival-law fit.

**MIDDLE:** mechanistic law improves over the current empirical law (as the cheap test above already shows
directionally) but still ties/loses to nearest-lookup at the highest-stress new folds -- informative partial
win; lookup remains the practical floor near the knee, and the honest scope caveat should be UPGRADED, not
resolved, until a genuine regime-shift model (percolation-critical framing) is tried.

## Cross-thread synthesis

Brain-mechanism ranking (deflated per lit-scan calibration penalty; each sub-agent's raw estimate then
deflated 0.15-0.25 here):

1. **Model-based prospective simulation (hippocampal-PFC preplay + model-based RL).** Neuroscience: place-cell
   sequences run forward through UNVISITED paths before/during choice (Pfeiffer & Foster 2013, *Nature*;
   Johnson & Redish 2007 vicarious-trial-and-error), read out by PFC to bias decisions; Daw/Dayan model-based
   vs model-free arbitration (Daw, Niv & Dayan 2005, *Nat Neurosci*); successor representation (Dayan 1993;
   Stachenfeld, Botvinick & Gershman 2017, *Nat Neurosci*). Formal RL-theory backbone: Young et al.
   (arXiv:2211.02222) prove learned-transition-model hypothesis classes generalize strictly tighter than
   direct value/cache learning UNDER FACTORED/STRUCTURED dynamics with a correctly-specified model -- this is
   the closest thing to an actual theorem for "why compose-from-a-model beats cache-from-instances outside
   the visited range." Sub-agent raw confidence 0.55 (blend of strong separate halves, weaker tight causal
   link between the neural finding and the RL theorem). Deflated: **0.35**. Directly maps to substrate action:
   derive the compositional per-hop transition function (candidate B above) instead of regressing a scalar.
2. **Theory-derived mechanistic functional form (EVT/percolation/RG universality precedent).** Fisher-Tippett-
   Gnedenko + Pickands give an actual LIMIT THEOREM guaranteeing GPD/GEV tail shape is correct regardless of
   fitted parameters -- the strongest, most citable form of "mechanism beats black-box for extrapolation" in
   all of statistics. Renormalization-group universality (Wilson 1971) gives the analogous guarantee near a
   critical point. BUT the same lit-scan found the closely-analogous case (parametric SURVIVAL models --
   Weibull/log-logistic, the literal name-match to our "survival law") frequently LOSE to flexible splines in
   real extrapolation benchmarks (Latimer 2013 NICE DSU TSD14; Swedish Cancer Registry study), and PINNs show
   contested, regime-dependent extrapolation gains/failures (Raissi et al. 2019; 2025-26 benchmarks documenting
   sharp degradation beyond short horizons). Sub-agent raw confidence 0.55-0.6, CONTINGENT on correct
   abstraction level. Deflated, capped (novel-synthesis P<=0.50 per policy): **0.35**. This is essentially the
   same prescription as (1) in different notation -- reinforces rather than adds an independent mechanism.
3. **Cerebellar forward/inverse models (Marr-Albus-Ito, Kawato feedback-error-learning, Wolpert-Kawato-Miall
   MOSAIC).** Real, well-established mechanism -- but it is architecturally a LOCALLY-TUNED basis-function /
   mixture-of-experts regression (gated linear approximators over an expanded feature space), fit online by
   error-driven correction. Empirical generalization studies (force-field, saccadic, prism adaptation) show
   generalization DECAYING with distance from trained conditions (Parmar & Patton 2018: near-zero transfer by
   ~60 deg from trained direction) -- i.e. this is the biological analog of the CURRENT substrate law (a
   locally-fit affine correction), and the evidence argues it should NOT be expected to extrapolate far. Raw
   sub-agent confidence 0.25 for the "gives genuine out-of-range extrapolation" claim. Deflated: **0.10**.
   Value here is as a CAUTION / negative prior, not a build target: it predicts the CURRENT approach's
   extrapolation failure is expected, not a fixable bug in the affine-fit step itself.
4. **Metacognitive confidence/uncertainty (Kepecs & Mainen; Fleming & Lau; Yu & Dayan LC-NE "unexpected
   uncertainty").** Real, dissociable brain confidence computation exists, and separately a more CATEGORICAL
   novelty/surprise alarm (LC-NE) for genuinely novel situations. ML parallel (deep ensembles, MC-dropout,
   conformal prediction) is on firmer ground: uncertainty demonstrably widens OOD and enables abstention/
   trust-gating EVEN WHEN it does nothing for point-estimate accuracy. Raw confidence 0.55 for the general
   design principle, only 0.25-0.3 for the brain showing smoothly-graded (vs binary-alarm) widening. Deflated:
   **0.30** for "worth adding a confidence band," but explicitly NOT claimed to fix extrapolation accuracy --
   complementary second-stage addition (a trust-gate: "flag when NOT to trust the extrapolated proposal"),
   layered on top of (1)/(2), not a substitute for deriving the correct functional form.

Synthesis with prior entries: this closes the loop flagged in `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-08.md`
("extrapolation-superiority is UNPROVEN = the next frontier") with a concrete, disk-verified partial result
(mechanistic-proxy substitution improves but does not resolve) plus a specific next mechanism (percolation/
transmission-coefficient compounding) that is independently corroborated by BOTH the brain/RL-theorem lit-scan
AND the pre-existing physics-field-coverage map's Tier-1b `mesoscopic-transport`/`percolation-critical-phenomena`
adjacencies (`tools/orchestrator/research_field_advisor.py` output, this cycle: both fields anchored to the
fruit-bearing thermodynamics/semiconductor parents, previously flagged for the unrelated multi-hop d=25 cliff
and capacity-cliff work -- same mathematical machinery now shown relevant here too).

## Substrate-product implications

- If HARD-PASS: the substrate gains a genuinely predictive (not just interpolative) self-capacity model --
  product-relevant as "tell the user the safe operating envelope BEFORE they hit it," including regions never
  directly measured. This is a stronger self-improvement claim than the current VET'd result.
- If HARD-FAIL: still valuable -- it converts an open scope-caveat into a characterized, honest limit (a
  measurable "critical fill" threshold), which is itself a new self-observable substrate constant, and tells
  the product to treat nearest-lookup as the safe extrapolation fallback beyond that threshold rather than
  trusting any smooth law.
- Either outcome: the confidence/trust-gate addition (rank 4) is cheap to add regardless (reuses existing
  bootstrap machinery already in `control1_scramble_law`) and gives the product a legitimate "low-confidence,
  falling back to lookup" mode near/beyond the observed range -- independent of whether the point-estimate
  problem itself gets solved.

## Citations (verified count)

Delivered via 4 parallel Sonnet lit-scan sub-agents using WebSearch/WebFetch with generic math/neuroscience
terms only (no substrate-specific terms sent off-platform, per query-privacy discipline). Citations as
reported by each sub-agent (author/year, not independently re-fetched by this synthesis step -- standard
lit-scan calibration discipline applies, hence the deflation above):

- Cerebellar forward models (7 citations): Marr 1969; Albus 1971; Kawato et al. 1987; Wolpert & Kawato 1998;
  Haruno, Wolpert & Kawato 2001; Shadmehr & Mussa-Ivaldi 1994; Parmar & Patton 2018; Herzfeld/Shadmehr 2023-25.
- Metacognition/uncertainty (6 citations): Kepecs, Uchida, Zariwala & Mainen 2008 *Nature*; Fleming & Lau 2014;
  Fleming & Daw 2017; Lak et al. 2015 *Neuron*; Yu & Dayan 2005 *Neuron*; Gal & Ghahramani 2016 / Lakshminarayanan et al. 2017.
- Prospective coding/model-based RL (7 citations): Pfeiffer & Foster 2013 *Nature*; Johnson & Redish 2007;
  Daw, Niv & Dayan 2005 *Nat Neurosci*; Dayan 1993; Stachenfeld, Botvinick & Gershman 2017; Mattar & Daw 2018;
  Young et al. arXiv:2211.02222; *Cell* 2023 generative-replay MEG paper.
- Mechanistic-vs-empirical extrapolation (9 citations, 3 with fetched URLs): Fisher & Tippett 1928 / Gnedenko
  1943; Pickands 1975; Coles 2001; arXiv:2605.01909; Latimer 2013 NICE DSU TSD14; PMC10988990; PMC6900572;
  Wilson 1971 RG theory; Raissi, Perdikaris & Karniadakis 2019 + arXiv:2508.21559 / arXiv:2507.12659 PINN
  benchmarks.

Total: **29 citations across 4 independent lit-scans**, plus 1 disk-verified quantitative finding computed
directly in this synthesis pass (no citation needed -- recomputed from `data/exp_reasoning_depth_keyslots_sharding_v1/metrics.json`,
reproducible by re-running the printed python snippet against that file).

P_deflated (headline claim: "a properly-derived mechanistic per-hop compounding law will resolve the
extrapolation gap") = **0.30** (capped per novel-synthesis policy; the cheap test's directional confirmation
supports proceeding, but the curvature-mismatch finding means the SPECIFIC candidate B form is unverified,
not just its general category).

Next-drill candidate (field-advisor-informed): `percolation-critical-phenomena` / `mesoscopic-transport`
(Tier-1b, both 100% anchor-yield via thermodynamics/semiconductor parents) -- drill the specific question
"does the reasoning-depth capacity cliff sit near a percolation-style critical fill, and does universality-
class scaling (mean-field vs the substrate's actual dimensionality) predict the curvature-mismatch observed
at fill=0.28-0.35?" This is the natural adjacency-cascade follow-up (Trigger C) from this delivery.
