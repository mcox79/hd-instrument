# Research drill 3x: BCM slow-learning at chance (gap3_cls_two_tier_BCM HARD_FAIL 2026-06-27)

**Author:** research (Director)
**Date:** 2026-06-27
**Trigger:** `data/exp_gap3_cls_two_tier_BCM_slow_replay_v1/metrics.json` HARD_FAIL — BCM_SLOW + BCM_GENERATIVE_REPLAY both at chance (0.20 = 1/N_CAT=5); Hebbian baseline rec=1.000
**Lit-scan calibration penalty:** novel-synthesis P deflated by 0.20; cap at 0.50 per discipline
**Source files cross-checked:**
- `data/exp_gap3_cls_two_tier_BCM_slow_replay_v1/metrics.json` (empirical)
- `experiments/exp_gap3_cls_two_tier_BCM_slow_replay_v1.py` (cell code; lines 284-296 BCM update; lines 363-367 init)
- `preregs/2026-06-27_gap3_cls_two_tier_BCM_slow_replay_v1.md`

---

## VERIFY-THE-REFERENT FINDINGS (code-read forensics)

Before lit-scan synthesis, a code-read on the actual cell. Three load-bearing details:

**(1) ZERO-INIT W_schema (line 363):**
```python
W_schema = torch.zeros((N_CATEGORIES, N_DIM), dtype=torch.float32, device=_DEVICE)
```

**(2) ZERO-INIT theta_M_per_class (line 366):**
```python
theta_M_per_class = torch.zeros((N_CATEGORIES,), dtype=torch.float32, device=_DEVICE)
```

**(3) BCM update rule (lines 284-296):**
```python
def _bcm_update(W_row, x, theta_M, eta=ETA_SLOW):
    y = float((W_row * x).sum().item())
    dW = eta * x * y * (y - theta_M)
    W_new = W_row + dW
    alpha = 1.0 / THETA_M_WINDOW
    theta_new = (1 - alpha) * theta_M + alpha * (y * y)
    return W_new, theta_new
```

**Direct algebraic consequence:**
- Cycle 0: W=0, theta_M=0
- y = (W * x).sum() = 0 (because W=0)
- dW = eta * x * 0 * (0 - 0) = 0  ← weights do not update
- theta_new = (1 - 1/200) * 0 + (1/200) * 0 = 0  ← threshold does not update
- Cycle 1, 2, ..., 5000: same state. Forever.

**Diagnosis: BCM is on a fixed point at the origin (W=0, theta=0).** Every term in dW has y as a factor; y=0 makes dW=0. theta tracks y^2, also stays 0. The 0.20 = 1/N_CAT result is exactly chance because W_schema stays the zero matrix → cosine sim is degenerate (NaN/uniform) → argmax over equal scores picks category 0 (or whatever ties first), and `(W_schema/(norm+1e-9))` makes it numerical noise on the 1e-9 epsilon. Effectively random.

**Cell-author smoke-discipline gap:** smoke uses zero-init too (line 363 runs in smoke). The smoke pre-reg said "smoke fires discriminator: smoke uses N_DIM=2048 baseline+BCM with 500 replay cycles to check BCM-arm-rises-monotonically." But BCM doesn't rise at all — it sits at chance — and the smoke verdict apparently accepted that. META_RULE_K violation (smoke must FIRE discriminator).

**Hebbian works (rec=1.000) because:** Hebbian is `W_schema[c] += eta_slow * train_x[ep]` — pure additive accumulation; the x vector (bipolar +/-1, no y multiplier) directly drives growth from W=0. After 5000 cycles * 0.2 * 100 episodes = 100k accumulations at eta=1e-3, ||W|| is enormous and matches the true class prototype direction. NO degeneracy.

This is overwhelmingly the proximate cause. Lit-scan below provides the diagnostic framework.

---

## ANGLE 1 — MATHEMATICAL / BCM CONVERGENCE THEORY

### Lit confirmation (web search 2026-06-27)
- **Scholarpedia BCM:** "synaptic weights were initialized randomly (normal distribution with zero mean) in computational implementations" — note: zero MEAN with non-zero VARIANCE; substrate cell used pure zeros.
- **Yger-Harris 2013 (Weight dependence in BCM, Journal of Computational Neuroscience):** "initial weights can be set as an unequal mix of two fixed points, w(t=0) = (1−ε)w1* + εw2*, so the dynamics is prone to converge to the desired fixed point" — explicit acknowledgment that BCM has multiple fixed points and init must break symmetry.
- **Bio-protocol selectivity-with-BCM:** weights init "randomly between 0.10 and 0.12" — small but non-zero positive.
- **Slowdown of BCM plasticity with many synapses (Lim-Cohen 2019, J Comput Neurosci):** convergence slows EXPONENTIALLY in N_DIM. At N_DIM=8192 this is a separate concern even with non-zero init (5000 cycles may be far below the convergence horizon).

### BCM fixed-point structure
BCM dynamics in continuous form:
  dW/dt = eta * x * y * (y - theta)
  d(theta)/dt = (1/tau) * (y^2 - theta)
  where y = W . x

Fixed points (dW/dt = 0):
  (a) y = 0 (orthogonality fixed point — DEGENERATE, achieved by W=0 OR W orthogonal to x)
  (b) y = theta (selectivity fixed point — DESIRED)

The ZERO fixed point is unstable in the GENERIC stochastic-input setting (any input noise drives small y > 0 → growth) — BUT only if W has even tiny non-zero component along some x direction. With W EXACTLY zero AND deterministic float arithmetic, no perturbation ever arises. The substrate cell hit this exact degenerate case.

The DESIRED fixed point (selectivity) requires:
- W to have positive overlap with at least one stimulus class
- theta to track E[y^2] over a window short enough to react but long enough to estimate
- eta small enough for stability, large enough for convergence in finite cycles
- input statistics quasi-stationary (BCM proof requires this)

### Substrate-specific failure modes (ranked)

1. **W_schema = 0 → y = 0 → dW = 0** [PRIMARY]; explains 100% of observed chance behavior.
2. **theta_M = 0 init** [SECONDARY, masked by #1]; even if W had tiny init, theta_M starting at 0 with EWMA window=200 means early dW = eta * x * y * y (since theta=0, the (y-theta) factor is y), which is the COVARIANCE/Hebbian-quadratic limit — would grow weights super-linearly but NOT establish selectivity until theta catches up.
3. **theta_window=200 vs N_REPLAY=5000:** ratio is reasonable (25 windows of estimation across the run); not the dominant failure.
4. **eta_slow=1e-3 with bipolar +/-1 inputs at N_DIM=8192:** if W had non-zero init w_init, then y = w_init . x ~ w_init * sqrt(N_DIM) * O(1) by random-walk. With w_init=0.01, y ~ 0.9. Then dW ~ 1e-3 * x * 0.9 * (0.9 - theta). For theta to track, need ~200 cycles. Reasonable scale.
5. **BCM convergence-slowdown at large N (Lim-Cohen):** at N_DIM=8192, BCM convergence is empirically slow; 5000 cycles may be marginal. Lower-bound concern but not primary.

### Verdict on Angle 1
**Root cause is #1 (zero-init at degenerate fixed point), enabled by #2 (zero-init theta).** The other concerns matter for a RESCUED cell but are not the proximate failure. P(rescue with non-zero init alone) = 0.60. P(also need theta init + eta tuning) = 0.25 additional. P(also need cycle-count increase) = 0.10 additional. Combined P(rescue with all four) = 0.50 (capped per lit-scan calibration; novel-synthesis ceiling).

---

## ANGLE 2 — BRAIN / NEUROSCIENCE (BCM in vivo)

### Lit summary
- **BCM successful predictions in vivo:** V1 receptive field formation in cats (Cooper-Bear 2010 review); monocular deprivation shift; orientation selectivity.
- **BCM in hippocampus:** less direct; hippocampus uses STC (synaptic tagging-capture), BTSP (behavioral timescale plasticity), STDP variants. BCM is more a cortical V1-specific model.
- **BCM requires SLOW input statistics:** cat visual experience is naturalistic scenes over hours; even fast OR is over many seconds. The substrate is firing 100k replay events in ~6 sec of wall time — that's 5 orders of magnitude faster than the brain's BCM regime.
- **Brain initialization (the implicit answer):** there is NO zero-init in brain. Cortical pyramidal cells have thousands of pre-existing synapses with non-zero (mostly weak but distributed) weights from spontaneous activity in development. Thalamic input establishes COARSE retinotopic tuning before BCM-style refinement kicks in. BCM is a SECOND-stage refinement rule, not a from-scratch learner.

### Brain-grounded implications for substrate

The substrate cell tried to use BCM as a from-scratch learning rule (zero-init). Brain doesn't do this. Brain's BCM operates on a pre-tuned substrate from thalamic input + spontaneous activity. The substrate equivalent would be:

**Required pre-conditions for substrate BCM:**
1. **W_schema pre-init from Hebbian step.** Run a few hundred Hebbian writes first to establish coarse tuning, THEN switch to BCM for selectivity refinement. This mimics thalamic-then-cortical sequencing.
2. **Spontaneous-activity init.** Initialize W_schema with small random bipolar at scale ~0.01-0.1, mimicking pre-experience cortical connectivity (random sparse positive distribution).
3. **theta_M warm-up.** Run a few hundred cycles of pure Hebbian (no BCM term) to let theta_M track a meaningful y^2 baseline before letting it gate the BCM term.

### Brain-grounded SUBSTITUTE rules (if substrate truly can't host BCM)

1. **Oja rule:** `dW = eta * (x * y - y^2 * W)`. Also has W=0 fixed point but it's UNSTABLE under stochastic input (random perturbation grows). Oja converges to first principal component — IS a brain-grounded rule (Foldiak, Linsker, Sanger).
2. **Generalized Hebbian Algorithm (GHA / Sanger 1989):** extracts multiple principal components via sequential Oja-with-deflation. Brain-grounded (proposed for V1 simple cells).
3. **Foldiak's competitive learning + anti-Hebbian inhibition:** sparse coding; brain-grounded for V1 sparse representations.
4. **Triplet-STDP (Pfister-Gerstner 2006):** reduces to BCM in mean-field limit; spiking variant. Triplet-STDP can implement BCM-like selectivity without the degenerate zero fixed point because spike-timing breaks symmetry.
5. **Hopfield consolidation (Whittington-Behrens 2024 family):** energy-based slow consolidation; chain-grade primitive in substrate already (cert atom 588 generation, NREM replay).

### Verdict on Angle 2
Substrate CAN host BCM provided pre-conditions are met (warm Hebbian + non-zero init + theta warm-up). Brain doesn't run BCM from zero either — substrate cell was set up for a regime the brain never operates in. P(BCM works with brain-grounded init pipeline) = 0.55.

If BCM still fails after init fix, Oja rule is the cleanest brain-grounded substitute (P=0.55 it works in substrate substrate). Hopfield consolidation is the most substrate-native (already cert-graded primitive on chain). P(substrate has a brain-grounded slow-learning rule that DOES work) = 0.80 conditional on willingness to try Oja / GHA / Hopfield-consolidation pathway.

---

## ANGLE 3 — CROSS-DOMAIN (learning rate scheduling, normalization)

### Adam / RMSProp / Adagrad parallel
Adam normalizes gradient by running second moment estimate — essentially theta_M but applied to GRADIENT not POSTSYNAPTIC ACTIVITY. Adam mitigates BCM's failure mode (degenerate W=0) because gradient is computed from loss not from activity * activity, and loss has external structure (labels) that breaks symmetry.

**BCM doesn't have this advantage.** BCM is purely activity-driven — no external label signal. The symmetry-breaking has to come from INIT or from input STRUCTURE (which substrate's bipolar inputs do have, but only if y is non-zero to expose it).

### Batch normalization parallel
BN forces zero-mean unit-variance per layer activation — this is what theta_M tries to do in BCM. BN is a stable trainable parameter pair (gamma, beta) computed across batch; BCM's theta_M is a single sliding average. BN works because (a) gradient flows through the normalization; (b) gamma/beta are learnable; (c) init is non-degenerate (gamma=1, beta=0 doesn't kill activations).

**Implication for substrate:** BCM with theta_M init at SMALL POSITIVE VALUE (not zero) — say theta_init = 0.5 — would behave more like BN warmup. The (y - theta) term then has a non-trivial sign-breaking even on first cycle.

### Self-organizing maps (Kohonen)
SOM converges from random init via competitive learning + neighborhood function. Brain-grounded for cortical map formation. SOM does NOT have the BCM degeneracy because winner-take-all selects ONE neuron per stimulus → that neuron's W is updated regardless of activity level (the update is `W += eta * (x - W)` not multiplicative in y).

**SOM-style substrate slow-learning rule:**
```
For each replay sample x with label c:
    W_schema[c] += eta * (x - W_schema[c])  # tracking moving average toward x
```
This is robust, never degenerates, and is effectively what Hebbian baseline approximates (without the explicit subtraction). Brain-grounded (cortical maps).

### Boltzmann learning
Requires temperature schedule. Substrate-native temperature is implicit in cleanup-iteration depth. Not directly applicable as drop-in BCM replacement.

### Verdict on Angle 3
Cross-domain analogues all suggest: (a) explicit normalization helps but needs non-degenerate init; (b) WINNER-TAKE-ALL competitive learning (SOM, sparse coding) sidesteps BCM's degeneracy entirely; (c) Adam-style adaptive learning rate isn't applicable without a loss gradient. P(SOM-style works in substrate as drop-in slow rule) = 0.65 (this is essentially what Hebbian already does, just with an explicit decay term).

---

## SYNTHESIS ANSWERS

**Q1 — ROOT CAUSE: is BCM-at-chance because (a) theta_window=200 too long? (b) zero-init W too small? (c) eta wrong? (d) substrate dynamics fundamentally incompatible?**

**Answer:** (b) dominantly, with (a) and theta-init as enablers. NOT (d) — substrate is mathematically capable of hosting BCM. Specifically:
- W = 0 → y = 0 → dW = 0 (algebraically exact, every cycle, every seed). This is the entire failure.
- theta_M = 0 init compounds because even if W had perturbation, the (y-theta) factor would be all y (no selectivity gating until theta catches up).
- theta_window=200 with N_REPLAY=5000 is fine (25 windows of estimation), not a primary issue.
- eta=1e-3 with bipolar +/-1 at N_DIM=8192 is fine IF W is non-zero (expected y ~ sqrt(N_DIM) * w_init).

**Q2 — Best chance of rescue: which combination most likely to make substrate BCM work?**

Ranked combinations (P = probability of HARD_PASS in next cell, lit-scan-calibrated):
1. **Random bipolar init at scale 0.01-0.1 + theta_init=0.5 + 200-cycle pure-Hebbian warm-up + BCM phase:** P=0.50 (cap)
2. **Hebbian-pre-train (~500 cycles) → BCM-refine (~4500 cycles):** P=0.45
3. **Random bipolar init alone (no Hebbian warmup, no theta init):** P=0.30
4. **Just non-zero W init (uniform 0.01 +/- noise), keep theta=0:** P=0.20
5. **Increase N_REPLAY to 50000, keep zero-init:** P=0.02 (won't escape fixed point)

**Q3 — If substrate fundamentally can't host BCM, what's the brain-grounded SUBSTITUTE?**

In order of brain-grounding strength + substrate-fit:
1. **Oja rule** (already brain-grounded for V1; tiny init suffices to escape W=0 instability under stochastic input). P(works in substrate) = 0.55.
2. **SOM-style moving-average update** (cortical map formation; sidesteps degeneracy entirely). P(works) = 0.65. ESSENTIALLY EQUIVALENT to Hebbian which already lands rec=1.000 — so this is "Hebbian with decay term," basically the cell's current winning arm. NOT a new mechanism, just a re-framing.
3. **Hopfield consolidation** (substrate-native cert-graded primitive 588). P(works) = 0.60.
4. **Triplet-STDP** (BCM in mean-field limit; rate-only substrate would need to simulate spike-timing). P(works) = 0.30 (would need spike-timing substrate features that don't exist yet).
5. **Generalized Hebbian Algorithm (GHA/Sanger):** extracts multi-component features. P(works) = 0.50.

**Q4 — Implications: is Stage 3 cortical schema extraction blocked on BCM, or can we route around?**

NOT blocked. Routes:
- **Path A (BCM rescue):** Fix init + theta + warmup; one re-dispatch cycle. Cost: ~2-6 CPU-hr (similar to original).
- **Path B (Oja substitute):** Brain-grounded; minor code change (different dW formula); same overall harness. Cost: ~2-6 CPU-hr.
- **Path C (Hopfield consolidation):** Use already-cert-graded substrate primitive (atom 588). Lowest dev cost. Cost: ~1-3 CPU-hr (primitive already exists).
- **Path D (acknowledge Hebbian wins, move on):** Hebbian baseline rec=1.000 IS the schema extraction in this regime. BCM was supposed to provide SELECTIVITY (one-pattern-per-neuron) which the prototype-match readout doesn't actually test. Re-design the discriminator instead: test on AMBIGUOUS inputs where selectivity matters, not category-rec which Hebbian aces.

**Recommendation:** Pursue Path A AND Path C in parallel (Path A as the "BCM-the-brain-rule actually works in substrate" affirmative answer; Path C as the substrate-native fallback). Path D should be a separate cell-design discussion — selectivity discriminator vs prototype-rec discriminator is a legitimate Stage 3 question independent of BCM.

---

## CELL-SPEC STUBS (3 alternatives)

### STUB 1 — BCM-v2 with init + theta + warmup fix (Path A, primary rescue)

```
ANCHOR: gap3_cls_two_tier_BCM_v2_init_fix_2026-06-27
CHANGES vs v1:
  W_schema init: torch.empty(...).normal_(mean=0.0, std=0.01)  # non-zero variance
  theta_M_per_class init: torch.full((N_CAT,), 0.5)  # warm threshold
  Phase 1 (cycles 0-499): Hebbian-only warm-up
      W_schema[c] += ETA_SLOW_WARM * train_x[ep]  # eta_warm=1e-2
  Phase 2 (cycles 500-4999): BCM as in v1
ARMS (4):
  ARM_BASELINE_SINGLE_W (rail check; rec must replicate ~1.0)
  ARM_BCM_V2_FULL (init + theta + warmup)
  ARM_BCM_V2_INIT_ONLY (random init, theta=0, no warmup) — ablation
  ARM_BCM_V2_WARMUP_ONLY (zero init, theta=0, Hebbian warmup phase) — ablation
PRE-REG BANDS: HP_FLOOR=0.70 (same as v1); HP_LIFT_OVER_BASELINE=0.18;
  HP_BCM_OVER_HEBB=0.10; CV<=0.08; selectivity discriminator added:
  best_BCM_arm must show neuron-selectivity profile (one row dominates per category;
  Shannon entropy of normalized W_schema row activities < 0.5 * uniform).
SMOKE: full-N preview arm (USER discriminator-survives-scale rule);
  smoke must observe y > 0 within 10 cycles for BCM_V2_FULL arm
  (FAIL smoke if y stays at 0 after init).
COST: ~6 CPU-hr full; remote_cpu_queue.
```

### STUB 2 — Oja rule substitute (Path B, brain-grounded alternative)

```
ANCHOR: gap3_cls_two_tier_OJA_slow_replay_v1_2026-06-27
RULE: dW = eta * (x * y - y^2 * W)  # Oja 1982
INIT: W_schema random bipolar at scale 0.01 (Oja's W=0 unstable, escapes via input noise)
ARMS (4):
  ARM_BASELINE_SINGLE_W (rail)
  ARM_TWO_TIER_HEBBIAN_SLOW (control; rec=1.000 expected)
  ARM_TWO_TIER_OJA_SLOW (primary mechanism)
  ARM_TWO_TIER_GHA_SLOW (Generalized Hebbian; multi-component variant)
PRE-REG: same envelope as v1; Oja lift over Hebbian gated at 0.05 (modest;
  Oja's value is PCA-extraction not classification per se).
DISCRIMINATOR: principal-component cosine — W_schema rows should align with
  top-N_CAT principal components of train_x covariance.
COST: ~4 CPU-hr.
```

### STUB 3 — Hopfield consolidation substrate-native (Path C, lowest dev cost)

```
ANCHOR: gap3_cls_two_tier_HOPFIELD_CONSOLIDATION_v1_2026-06-27
USE: hdlab.continual.replay_cycle (atom 588 cert-graded) for slow consolidation
RULE: modern Hopfield update with energy-min step on each replay sample
  E(W, x) = -sum_c log sum_i exp(beta * (W[c] . x_i))
  dW = -eta * gradient of E (analytical; cf. atom 587 generation cell)
INIT: W_schema = mean-of-class-instances after Hebbian warmup
ARMS (4):
  ARM_BASELINE_SINGLE_W
  ARM_HEBBIAN_SLOW_CONTROL
  ARM_HOPFIELD_CONSOLIDATION (primary)
  ARM_HOPFIELD_CONSOLIDATION_WITH_REPLAY (consolidation + chain-grade NREM replay)
PRE-REG: substrate-native primitive; HP_FLOOR=0.70; LIFT_OVER_HEBBIAN=0.05
  (Hopfield's value is COMPRESSION + ROBUSTNESS not raw accuracy).
DISCRIMINATOR: rec on AMBIGUOUS held-out (50/50 between two categories) —
  Hopfield-consolidated should show graded confidence vs Hebbian one-hot.
COST: ~2 CPU-hr (primitive already exists).
```

---

## NEXT-ACTION RECOMMENDATION (Director-call)

1. **Spawn hdi_exp_dev** with priority on STUB 1 (BCM-v2 init fix) as the affirmative test of "does BCM actually work in substrate when properly initialized?" — answers the brain-grounded mechanism question directly.
2. **In parallel queue STUB 3 (Hopfield consolidation)** as the substrate-native fallback — if BCM-v2 also fails, this is the lowest-cost path to Stage 3 schema-extraction chain-grade.
3. **Defer STUB 2 (Oja)** — Oja IS brain-grounded but its value-add over Hebbian in the CURRENT prototype-rec discriminator is marginal; queue it only if STUB 1 + STUB 3 both inconclusive.
4. **Open a separate research thread on SELECTIVITY DISCRIMINATOR DESIGN** — Hebbian rec=1.000 means the current discriminator doesn't test what BCM is supposed to provide (one-pattern-per-neuron selectivity). Stage 3 cortical schema extraction may need a different readout (per-row sparsity / per-category activation entropy / generalization-to-NOVEL-categories) than prototype-rec.

**META_RULE_J (no silent except) recap:** The cell DID record the BCM failure correctly (n_failures=0 because no exceptions; heldout_acc=0.2 IS the recorded result). Failure was discriminator-design (BCM at chance is "successful execution at degenerate fixed point") not silent-except. META_RULE_K (smoke fires discriminator) IS the violated rule — smoke should have caught BCM stuck at chance before full dispatch. Worth atomizing: "BCM-style multiplicative-y rules require non-zero W init OR smoke-must-fire-discriminator on y>0 within N cycles."

---

## SOURCES (web search 2026-06-27)

- [Scholarpedia BCM theory](http://www.scholarpedia.org/article/BCM_theory)
- [Talk:BCM theory - Scholarpedia](http://www.scholarpedia.org/article/Talk:BCM_theory)
- [Weight dependence in BCM (Yger-Harris 2022, J Comput Neurosci)](https://link.springer.com/article/10.1007/s10827-022-00824-w)
- [Slowdown of BCM plasticity with many synapses (Lim-Cohen 2019, J Comput Neurosci)](https://link.springer.com/article/10.1007/s10827-019-00715-7)
- [Selectivity with the BCM rule (Bio-protocol)](https://bio-protocol.org/exchange/minidetail?id=3079082&type=30)
- [Generalized BCM rule for spiking neurons (Toyoizumi et al 2005, PNAS)](https://www.pnas.org/doi/10.1073/pnas.0500495102)
- [Toward generalized BCM rule via triplet-STDP (Nature Comm 2020)](https://www.nature.com/articles/s41467-020-15158-3)
- [Oja's rule (Wikipedia)](https://en.wikipedia.org/wiki/Oja's_rule)
- [Generalized Hebbian algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Generalized_Hebbian_algorithm)
- [Error-Gated Hebbian Rule (Isomura-Toyoizumi 2018, Sci Rep)](https://www.nature.com/articles/s41598-018-20082-0)
- [Nonlinear Hebbian as unifying principle in RF formation (Brito-Gerstner 2016, arXiv)](https://arxiv.org/pdf/1601.00701)
