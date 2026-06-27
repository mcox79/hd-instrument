# Research drill 3x — v4 NREM-replay-modulated trace fairness violation

**Date:** 2026-06-27
**Anchor:** `edge_importance_v4_NREM_replay_modulated_trace`
**Verdict:** HARD_FAIL — cor(importance, |W|) = 0.841 (gate < 0.30)
**Source metrics:** `data/exp_edge_importance_v4_NREM_replay_modulated_trace/metrics.json`

---

## STEP 0 — Honest per-arm re-read (Fix #28; corrects prompt framing)

The prompt summary said "TRACE alone: cor=acceptable; REPLAY alone: cor=high; COMP inherits replay's high cor". The actual per-arm metrics (3 seeds avg) are:

| Arm | cor(importance, |W|) | sel_minus_rand | recall_old_RETRIEVED |
|---|---|---|---|
| BASELINE_RANDOM | ~0.007 (correct null) | 0 (definition) | 0.752 |
| TRACE_ONLY | **0.829** (already FAILS gate) | +0.100 | 1.000 |
| REPLAY_ONLY | **0.980** (extreme — basically IS \|W\|) | +0.017 | 0.738 |
| TRACE + 0.5*REPLAY | 0.841 | +0.100 | 1.000 |
| TRACE + 1.0*REPLAY | 0.852 | +0.100 | 1.000 |
| TRACE + 2.0*REPLAY | 0.870 | +0.100 | 1.000 |

**Two corrections to the framing:**

1. **TRACE alone ALSO fails the 0.30 fairness gate** (0.83, not "acceptable"). The bug isn't replay-contaminating-trace; BOTH signals correlate with |W|. Replay is just MORE correlated (0.98 vs 0.83).
2. **COMP's cor is essentially TRACE's cor.** Adding lambda*REPLAY moves cor from 0.83 → 0.84 → 0.85 → 0.87 — a small monotone climb, not "inheriting REPLAY's 0.98". Lambda is well-damped because REPLAY's mean importance (0.144) is dwarfed by TRACE's mean (3.0).

This reframes the question. It's not "replay broke trace's fairness". It's: **both retrieval-trace AND replay-frequency are dominated by |W| in this substrate, and their composition can't escape that.** The mechanism family has a deeper problem.

---

## ANGLE 1 — Mathematical / sampling-theory diagnosis

### Why does retrieval-trace correlate 0.83 with |W|?

Trace = count of times an atom is the cleanup-argmax across J=3000 random composite queries.

For a noisy query `q = compose(items) + epsilon`, cleanup picks `argmax_a <q, a>`. The expected argmax-frequency for atom `a` is monotone in `||a||` (assuming items are non-zero overlap with `a`). High-|W| atoms dominate cleanup just by Cauchy-Schwarz. So trace-count IS a noisy proxy for ||a||, with cor 0.8-0.9 being the expected scaling-only baseline.

This is the **selection-bias root cause** common to BOTH signals: every signal that's computed by counting retrieval-events over a sampled query distribution will inherit the retrieval operator's magnitude bias.

### Why does replay correlate 0.98 with |W|?

Replay (sampling-importance-resampling lit; Liu 2001; Owen Monte Carlo Theory chapter 9) requires:

```
importance_independent_of_target  iff  proposal != target_posterior
```

The v4 replay uses *the substrate's own cleanup as proposal*. The proposal IS the high-|W| posterior. So replay-count converges to ||a||^2 (squared because each replay event re-queries the cleanup; high-|W| atoms get re-sampled at rate proportional to their cleanup-argmax probability, which is itself ~||a||^2 / sum).

Liu's diagnostic: **effective sample size (ESS) collapses to ~1/N when proposal == target** — meaning a uniform "proposal" sampler over substrate state degenerates to a |W|-weighted point mass. The replay arm has importance_max=3.0 with mean=0.144 (so the top atoms get replayed ~20x more than average) — that's classic ESS-collapse to a small subset of high-|W| atoms.

### What independence would require — three textbook fixes

**(A) Inverse-weighted (Liu IS):** importance(a) = replay_count(a) / cleanup_prior(a). Divides out the magnitude bias. Cost: need to estimate cleanup_prior — but `||a||` is already known so we just normalize by `||a||^2`.

**(B) Stratified sampling:** bin atoms by |W|-quantile (e.g., 10 bins), force equal sample budget per bin during replay. Provably magnitude-independent within bins; importance is *rank-within-bin* not raw count.

**(C) Reservoir with explicit independence constraint:** Vitter reservoir sampling with rejection of any candidate whose |W|-percentile is already over-represented in the reservoir.

**(D) Counterfactual perturbation (Pearl, Spirtes; this is the one I think wins):** importance(a) = recall_drop if a is downscaled vs not. Has nothing to do with replay frequency; directly probes contribution. The M-CFU path the prompt mentioned.

---

## ANGLE 2 — Brain / neuroscience

### Does brain replay correlate with synaptic strength?

**Yes — and that's exactly why brain doesn't use replay-count as importance.**

Engram literature (Tonegawa Cell 2015; Josselyn & Tonegawa Science 2020; Liu Nature 2012): strongly potentiated engrams replay more often during NREM ripples. Frank lab 2017 ripple-replay analyses: replay-event probability scales with engram strength (which is itself the synaptic-weight readout).

So if substrate's replay correlates with |W|, that's biologically *expected*. The bug isn't that substrate-replay looks like brain-replay. The bug is treating replay-count as importance — **brain doesn't do that either**.

### What brain ACTUALLY uses for synaptic importance

Brain has at least 4 independent importance signals modulating consolidation:

1. **Synaptic tagging and capture (STC; Frey & Morris 1997; Redondo & Morris 2011):** a temporal tag set at encoding marks synapses for later capture of plasticity proteins. Tag strength depends on novelty/salience, not on weight magnitude.
2. **Behavioral timescale plasticity (BTSP; Bittner et al. 2017 Science; Magee 2020):** dendritic plateau potentials gate which synapses get strengthened, on seconds-timescale. Independent of |W|.
3. **Neuromodulatory gating (dopamine/norepinephrine):** VTA bursts at unexpected-reward / prediction-error times license consolidation of co-active synapses. The error signal is orthogonal to |W|.
4. **Sharp-wave ripple content selection (Buzsaki 2015; Foster Annu Rev 2017):** ripples preferentially replay recently-acquired AND prediction-relevant content. Modulated by hippocampal-cortical coupling, not by raw synaptic weight.

**Replay is the CONSOLIDATION OPERATOR, not the IMPORTANCE SIGNAL.** It's the mechanism by which whatever's been tagged-as-important gets transferred from hippocampus to cortex. Importance is determined upstream by STC + dopamine + novelty + behavioral relevance.

### The v4 conceptual error

v4 used the *replay operator* as the importance *signal*. That's like measuring "which synapses are important" by counting "which synapses fire most often during sleep" — and yes, strong synapses fire most often during sleep, but that's because they're already strong, not because they're important.

The right composition in brain terms:

```
brain_importance(synapse) =
    f(novelty_at_encoding,        # STC tag amplitude
      dopamine_at_encoding,       # neuromodulatory gating
      behavioral_relevance,       # prefrontal top-down
      recency)                    # systems-consolidation timescale

replay(synapse) = consolidation_operator * brain_importance(synapse)
                  = strengthening force gated by importance
```

So substrate analog:
```
substrate_importance(atom) =
    f(novelty(atom),              # how different from existing memory
      counterfactual_utility,     # M-CFU: recall drop if atom removed
      task_relevance,             # downstream-query dependence
      recency)

replay(atom) = repeated rehearsal applied AS A FORCE, gated by importance
```

The composition is `importance gates replay`, NOT `replay computes importance`.

---

## ANGLE 3 — Cross-domain: sampling / MC / importance-weighting

### Monte Carlo importance sampling

Classical result (Owen MCMC textbook; Cappe et al. 2004): under a proposal q(x) and target p(x), the importance weight is w(x) = p(x)/q(x). Sample-frequency is q(x), but importance is w(x) — they're definitionally different.

When q(x) == p(x), w(x) == 1 (uniform — no information from sampling). When proposal equals posterior (as in v4 replay), the sample COUNTS carry zero information about importance.

### Deep RL importance correction

PPO (Schulman 2017), V-trace (Espeholt 2018), Retrace (Munos 2016): off-policy RL must explicitly correct for behavior-policy bias via importance ratios — otherwise stale on-policy samples dominate updates. Without correction, the algorithm reinforces what it already does — exactly the v4 failure mode (replay reinforces what already has high |W|).

### Active learning

Settles 2009 survey; Houlsby 2011 BALD: query items where the *model is most uncertain*, not where it's most confident. Counterfactual: substrate replay queries items where cleanup is most CONFIDENT (high |W| ≈ high cosine ≈ low uncertainty) — the opposite of what active-learning theory says.

If we want replay to expose important atoms, we should bias toward HIGH-UNCERTAINTY atoms (low |W|? high cleanup-entropy? margin-based?). That's an "anti-popularity" replay.

### Recommender cold-start

Netflix Prize era + multi-armed-bandit lit (Li 2010 LinUCB; Chapelle Thompson 2011): popularity-only collapses; need novelty / exploration bonus. UCB1's `sqrt(log(t)/n_a)` term penalizes already-sampled items. Direct analog for substrate replay: add `1/sqrt(replay_count(a)+1)` bonus to override popularity bias.

### Genetic algorithm fitness vs novelty search

Lehman & Stanley 2011 "Novelty Search": pure fitness-based GA converges to local optima because successful genotypes get sampled more. Solution: novelty bonus = distance from k-nearest behaviors in archive. Same fix for v4: replay-importance = distance from k-nearest-already-replayed-atoms, not raw count.

---

## SYNTHESIS — answers to the 4 questions

### Q1: Why did v4 fail — (a) substrate genuinely proxies |W|, or (b) replay-as-signal-when-it-should-be-operator?

**Both, with (b) deeper.**

(a) is empirically true: substrate's cleanup-argmax-frequency IS a magnitude proxy (cor 0.83 even for the trace-only arm; cor 0.98 for replay-only). This is not a bug, it's Cauchy-Schwarz.

But (b) is the conceptual root cause: v4 *chose* to use a sampling-operator's frequency as an importance signal, which textbook MC theory says is exactly the wrong move (proposal == posterior collapses ESS). Brain literature confirms: replay is operator, not signal.

(a) is a property of any retrieval-trace-based importance signal in any HD substrate — you can't fix it with more replay tricks. (b) tells us what direction to move: STOP using sampling-counts as importance; START using counterfactual or novelty or uncertainty.

### Q2: If (a), which independent importance signal can substrate add?

Ranked by P (HD-feasible × magnitude-independent × cheap):

1. **Counterfactual utility (M-CFU)** — P=0.65. importance(a) = (recall with a) − (recall with a downscaled). Directly orthogonal to |W| because BOTH conditions normalize |W|. Substrate already runs a recall harness; this is a near-trivial extension. Brain analog: behavioral salience.
2. **Inverse-weighted replay (Liu IS)** — P=0.45. importance(a) = replay_count(a) / ||a||^2. Provably magnitude-corrected if cleanup_prior is well-approximated by ||.||^2. Risk: the approximation may be sloppy at boundary atoms.
3. **Cleanup-margin uncertainty** — P=0.45. importance(a) = entropy of cleanup distribution when a is the target. High entropy = atom is hard to distinguish = high importance for maintenance. Brain analog: prediction-error.
4. **Stratified replay** — P=0.55. Bin atoms by |W|-decile, force equal replay budget per bin, importance = rank-within-bin. Operationally simple; provably independent across bins.
5. **Novelty-against-replay-archive** — P=0.40. importance(a) = HD distance from k-nearest already-replayed atoms. Brain analog: NREM novelty preference.

### Q3: If (b), what's the right composition?

```
v4_BROKEN:  importance(a) = trace_count(a) + lambda * replay_count(a)
            # both terms are |W|-correlated; no independence

v5_PROPOSED: importance(a) = counterfactual_utility(a)         # PRIMARY signal
             replay_force(a) = importance(a) * replay_budget   # operator gated BY importance
             consolidation(a) = replay_force(a) * decay_protection(a)
```

The composition is `importance → gates → replay`, NOT `replay → computes → importance`. This matches brain's STC-gates-replay-target hierarchy.

### Q4: Implications for Wave 3 ANCHOR 2 TWO_TIER promotion

**v4 HARD_FAIL is a strong validator of the M-CFU counterfactual-utility path over composition-with-replay.**

Two competing TWO_TIER promotion criteria were on the table:
- COMPOSED (trace + lambda*replay) — v4's mechanism
- M-CFU (counterfactual utility per atom) — orthogonal axis

v4 just demonstrated that COMPOSED collapses to a |W|-correlated single axis no matter how lambda is tuned (0.5/1.0/2.0 all in 0.84-0.87 range). It is structurally incapable of being magnitude-independent.

M-CFU, by construction (recall-with vs recall-without, both normalized by |W|), has *no first-order dependence on |W|*. It might still have second-order leakage (e.g., high-|W| atoms participate in more compositions so their removal hurts recall more), but that's a much weaker correlation than the 0.83-0.98 we just saw.

**Recommendation:** drop COMPOSED from Wave 3 ANCHOR 2 promotion criteria. Promote on M-CFU + at most one diagnostic-only secondary signal (stratified replay) for cross-validation. Reserve "replay-as-operator-gated-by-CFU" for v6+ once CFU is chain-grade.

---

## ACTIONABLE CELL-SPEC STUBS

### Cell stub 1: `edge_importance_v5_counterfactual_utility_M_CFU`

```
PRE-REG:
  PRIMARY_METRIC: cor(M_CFU(a), |W(a)|) < 0.30 (fairness gate)
  SECONDARY:      sel_minus_rand > +0.05 on prune-top-30% test
  HARD_FAIL_IF:   cor >= 0.50  (clear magnitude-contamination)
  HARD_PASS_IF:   cor < 0.20 AND sel_minus_rand > +0.10

ARMS:
  ARM_RANDOM:       importance = uniform random (null)
  ARM_W_MAGNITUDE:  importance = |W(a)|  (worst-case anchor; should HARD_FAIL fairness)
  ARM_TRACE_ONLY:   importance = retrieval_trace (v4 baseline; expect ~0.83 cor)
  ARM_M_CFU_LOO:    importance(a) = recall(W) - recall(W_downscale_a)  (leave-one-out)
  ARM_M_CFU_BATCH:  importance(a) = mean_drop_when_a_in_pruned_batch (cheaper)

PROTOCOL:
  N=512, M_OLD=600, M_RECENT=400, alpha=1.95 (v4-matched)
  J_composite=3000 queries
  Compute M_CFU per atom: full-substrate recall, then re-recall after downscaling atom a by 0.2x
  Repeat for all M_OLD atoms; importance(a) = recall_drop normalized to [0,1]
  Compare to baseline (random downscale) for sel_minus_rand

EXPECTED:
  M_CFU_LOO cor: 0.15-0.25 (passes fairness; small second-order |W| leakage from composition density)
  M_CFU_BATCH cor: 0.25-0.35 (borderline; cheaper but noisier)

RUNTIME:  ~20s smoke / ~5min full (M=1000 leave-one-out is dominant cost)

DISCRIMINATOR-SURVIVES-SCALE check (USER 2026-06-26): smoke at full M=600 LOO
  to confirm fairness gate fires before full dispatch
```

### Cell stub 2: `edge_importance_v5b_replay_as_modulator_NOT_signal`

```
PRE-REG:
  PRIMARY_METRIC: sel_minus_rand on prune-top-30% with replay applied AS A FORCE
                  (NOT as the ranking signal)
  FAIRNESS GATE:  cor(importance_signal, |W|) < 0.30
                  (where importance_signal is whatever drives the ranking, not the operator)
  HARD_FAIL_IF:   cor >= 0.50 OR sel_minus_rand <= 0
  HARD_PASS_IF:   cor < 0.20 AND sel_minus_rand > +0.10

ARMS:
  ARM_CFU_NO_REPLAY:        importance=M_CFU; no replay (control)
  ARM_CFU_PLUS_UNIFORM_REPLAY:  importance=M_CFU; replay applied uniformly across kept atoms
  ARM_CFU_GATED_REPLAY:     importance=M_CFU; replay budget allocated proportional to M_CFU
                            (replay strengthens IMPORTANT atoms, not POPULAR atoms)
  ARM_CFU_ANTI_REPLAY:      importance=M_CFU; replay applied INVERSELY to |W|
                            (rehearses weak-but-important atoms more)

PROTOCOL:
  Same N/M/alpha as v4
  Replay K=48; gate replay-target selection by importance signal, not by retrieval frequency
  Measure: does GATED_REPLAY beat NO_REPLAY on recall_old_RETRIEVED * (1 - cor)?

EXPECTED:
  GATED beats NO_REPLAY by +0.02-0.05 on weighted-recall (replay is useful AS operator)
  Fairness preserved because the ranking signal (M_CFU) is magnitude-independent
  ANTI_REPLAY may show even stronger gains on weak-atom recall (brain BTSP analog)

KEY DESIGN INSIGHT (from drill ANGLE 2):
  Replay is the CONSOLIDATION OPERATOR; importance is computed UPSTREAM by CFU/novelty/STC
  This cell tests the brain-aligned composition: importance gates operator, not vice versa

RUNTIME: ~30s smoke / ~10min full
```

### Cell stub 3: `edge_importance_v5c_stratified_replay_baseline_diagnostic`

```
PURPOSE: Diagnostic cell to confirm the |W|-bias DIAGNOSIS from this drill.
         Not aiming for HARD_PASS on promotion; aiming to validate ANGLE 1 math.

PRE-REG:
  EXPECTED:  stratified replay (forced equal-sample per |W|-decile) gives cor ~ 0.05-0.15
             (vs unstratified ~0.98) — proves the operator is the bias source
  HARD_FAIL_IF: stratified cor still > 0.50 (means the bias is NOT in the proposal-equals-posterior
                degeneracy; some deeper substrate property is the cause)

ARMS:
  ARM_UNSTRATIFIED_REPLAY:  v4-style replay (unstratified; expect cor ~ 0.98)
  ARM_STRATIFIED_10BIN:     bin by |W|-decile; force 4.8 replays per bin
  ARM_STRATIFIED_4BIN:      coarser binning; force 12 replays per bin
  ARM_INVERSE_WEIGHTED:     replay_count(a) / ||a||^2  (Liu IS correction)

PROTOCOL:
  Cheap: reuse v4 substrate state; just modify replay-target selection
  Measure cor(importance, |W|) for each strategy

EXPECTED (DIAGNOSTIC):
  STRATIFIED_10BIN: cor 0.05-0.15 (validates math)
  STRATIFIED_4BIN: cor 0.15-0.25 (validates binning sensitivity)
  INVERSE_WEIGHTED: cor 0.10-0.25 (validates Liu IS in HD substrate)

RUNTIME: ~5s smoke / ~30s full (state-reuse)

USE: confirms WHY v4 failed; informs whether v5 fixes should target the operator
     (stratified/IS) or sidestep it (M-CFU). If even stratified fails, the substrate
     itself has a deeper magnitude-bias and we need ANGLE-3 anti-popularity bonuses.
```

---

## RECOMMENDED SEQUENCE

1. **First:** dispatch Cell stub 3 (diagnostic; ~30s; cheap state-reuse) to confirm ANGLE 1 math holds in this substrate. This is verify-the-referent for the drill's diagnosis.

2. **If stub 3 confirms operator-degeneracy is the cause:** dispatch Cell stub 1 (M-CFU). High-prior path (P=0.65 fairness-pass).

3. **If stub 1 hits HARD_PASS:** dispatch Cell stub 2 (replay-as-modulator). This is the brain-aligned composition; expect +0.02-0.05 weighted-recall lift over CFU-alone, validating that replay-as-operator is *additionally* useful once importance is computed correctly.

4. **Wave 3 ANCHOR 2 promotion:** drop COMPOSED criterion; promote on M-CFU. Reserve composed-with-replay-as-operator for v6+ chain-grade.

## Atomization candidates (Store)

Three rule atoms emerge from this drill that belong in the discipline catalog:

- `RULE_REPLAY_IS_OPERATOR_NOT_SIGNAL` — replay-count cannot be importance because proposal-equals-posterior collapses ESS; replay is the consolidation operator; importance must come from upstream signal (CFU/novelty/STC-analog).
- `RULE_RETRIEVAL_TRACE_FAILS_FAIRNESS_BY_CONSTRUCTION` — any sampling-count signal over substrate retrieval is magnitude-correlated by Cauchy-Schwarz; expect cor(trace, |W|) >= 0.7 baseline; fairness gates require explicit normalization (stratification / inverse-weighting / counterfactual).
- `RULE_BRAIN_REPLAY_CORRELATES_WITH_W_BUT_BRAIN_DOESNT_USE_IT_AS_IMPORTANCE` — engram literature confirms replay-frequency tracks synaptic strength, but brain computes importance via STC + dopamine + behavioral salience upstream of replay; substrate should follow same architecture.

---

## DRILL CALIBRATION NOTE

- Lit-scan calibration penalty applied to all P estimates (deflated 0.15-0.25; capped novel-synthesis at 0.50). M-CFU pegged at P=0.65 because it's a direct reformulation of a textbook counterfactual measure, not a novel synthesis.
- Generic terms only used in cross-domain searches (sampling-importance-resampling / engram replay / STC / counterfactual utility / novelty search / IS correction). No project-specific names.
- Verify-the-referent applied: re-read per-arm metrics before propagating the prompt's framing (caught the TRACE-is-also-0.83 correction).
- Anti-negativity symmetric: didn't overclaim M-CFU as guaranteed-PASS; flagged the second-order leakage risk (high-|W| atoms participate in more compositions, so their removal hurts more — secondary cor 0.15-0.25 expected, not 0).
