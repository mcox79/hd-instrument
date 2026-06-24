# Research 2x drill — Dopamine-modulated LR alternatives (post-HARD_FAIL revival)

**Date:** 2026-06-23
**Author:** research (Opus 4.7, 1M context)
**Trigger:** `substrate_meta_lr_dopamine_analog_v1` HARD_FAILed at BETA=1.0 multiplicative-positive per-token RPE-LR (Skunkworks VET); USER brain-existence-proof + standing 2x-revival-for-every-negative directive.
**Tested formula (failed):** `alpha_t = base_lr * (1 + beta * clamp(rpe_t / ema_rpe, 0, 5))` with BETA=1.0, ema_alpha=0.05
**Result:** ARM_PER_TOKEN_RPE_LR=7.0602 vs ARM_FIXED_LR=7.0642 (lift=+0.004 bits, cv=0.0046 — within noise)
**Calibration penalty applied:** Substrate is in CHARTED regime (extensive brain RPE-LR literature, plus prior duration-vs-magnitude finding in our Store). Standard 0.15 deflation; cap novel-synthesis P at 0.50.

---

## (a) HEADLINE

**Brain-canonical formula is DURATION not MAGNITUDE: extend the eligibility-trace window when RPE is high, rather than multiply per-token LR by RPE magnitude. Top rescue candidate is `alpha_t = base * inverse_variance_normalization(rpe_t)` (Pearce-Hall associability) combined with `tau_eligibility = base_tau * (1 + gamma * |rpe|)` (Gong/Coddington 2026 duration-extension via optogenetics-confirmed dopamine-duration mechanism). The BETA=1.0 multiplicative-positive formula tested is structurally OPPOSITE to brain — brain CONTRACTS confidence in surprising contexts via eligibility-trace EXTENSION + variance NORMALIZATION, not LR amplification at the surprising token.**

P_deflated (DURATION-vs-MAGNITUDE rescue lifts >= +0.05 bits): **0.50** (capped at novel-synthesis ceiling; brain literature unambiguous; our own prior research note 2026-05-24 ALREADY identified this; substrate has chain-grade cf-RPE baseline to build on)
P_deflated (Pearce-Hall inverse-variance lift): **0.40**
P_deflated (Behrens-volatility-tracked LR lift): **0.35**

---

## (b) Cheap decisive test

**4-arm CPU smoke @ N=512/V=300/N_TRAIN=2k (the meta-LR cell's own smoke regime, total ~10min wall):**
1. `ARM_FIXED_LR` (control — exact ARM_FIXED_LR from v1)
2. `ARM_DURATION_LR` — extend eligibility-trace window on high RPE; lr is FIXED, but each high-RPE token's update propagates to next K steps where K = `K_base * (1 + gamma * normalized_rpe)`
3. `ARM_PEARCE_HALL_LR` — `alpha_t = base * |rpe_t - mean_rpe| / ema_rpe_abs`; classic associability rule (high LR when surprise > baseline)
4. `ARM_INVERSE_LR` — `alpha_t = base / (1 + beta * clamp(rpe_t / ema_rpe, 0, 5))`; multiplicative-INVERSE (high RPE -> LOW LR, cautious update)

**Decision rule (smoke):** any arm beats ARM_FIXED_LR by >= +0.03 bits at smoke scale -> promote that formula to N=8192 full. If ALL <= +0.01, no full-scale dispatch; file dopamine-modulated-LR as substrate-irrelevant.

---

## (c) Falsifiable predictions

### HARD-PASS thresholds (full run N=8192)
- `ARM_DURATION_LR` lift vs ARM_FIXED_LR >= +0.10 bits AND vs prior PER_TOKEN_RPE_LR >= +0.10 bits (this confirms USER duration-vs-magnitude intuition AND brain-canonical Gong/Coddington 2026 result transfers to substrate).
- `ARM_PEARCE_HALL_LR` lift vs ARM_FIXED_LR >= +0.07 bits (matches Mathys 2021 PLOS-CB simple-volatility-model gain over fixed-LR in their behavioral fits).
- `ARM_INVERSE_LR` lift vs ARM_FIXED_LR >= +0.05 bits (Yu-Dayan unexpected-uncertainty SUPPRESSES learning per Cell 2005; brain caution effect).
- cv across 3 seeds < 0.05 for any HARD_PASS-claiming arm (matches the v1 cv standard).

### HARD-FAIL thresholds
- `ARM_DURATION_LR` within +/-0.02 bits of ARM_FIXED_LR -> duration mechanism HARD_FAIL at substrate; the brain-mapping was vibes-only; close the "dopamine-LR is load-bearing" hypothesis for substrate-LM.
- `ARM_PEARCE_HALL_LR` within +/-0.02 -> associability HARD_FAIL; the Pearce-Hall mechanism does NOT compose with cf-RPE delta-rule at production scale.
- `ARM_INVERSE_LR` within +/-0.02 -> caution-on-high-RPE HARD_FAIL; suggests substrate's LM regime has no benefit from learning-rate damping (which would itself be a non-trivial finding — brain caution does NOT transfer).
- ALL 3 arms within +/-0.02 -> meta-LR-via-RPE is fundamentally not load-bearing for cf-RPE delta-rule at substrate N=8192/V=4000 regime; close the cap_map row "dopamine-LR-modulation" as TIER_3_CLOSED.

### MIDDLE_BAND (one-shot pivot)
- Any arm in +0.03 to HARD_PASS bar -> rescue cell with extended N_TRAIN (200k vs 100k) to test whether the marginal lift becomes load-bearing at more data; OR couple with TAU_NEG=10 STDP (per cross-thread synthesis below).

---

## (d) Per-formula analysis

### FORMULA 1 — DURATION extension (brain-canonical; USER intuition)

**Brain literature:** Gong/Martell/Dudman/Coddington 2026 (*Science*, DOI 10.1126/science.aeb0813) — REWARD MAGNITUDE acts via dopamine-signal DURATION, not via dopamine-spike MAGNITUDE. Optogenetic extension of standard-magnitude dopamine pulses recovers the same accelerated learning as 10x larger rewards. Three measured components: (1) per-trial LR INCREASE, (2) day-to-day consolidation, (3) sustained engagement.

**This is already in our Store as research_dopamine_article_drill_2026-05-24.md.** The v1 meta-LR cell IGNORED this finding and tested MAGNITUDE instead — that is the diagnosable error.

**Substrate-native formula:**
```
For each token t with cf-RPE rpe_t:
  delta_W_t = lr * (target_t - W @ src_t) * outer(target_t, src_t)
  W += delta_W_t                                               # immediate update
  # Eligibility-trace extension:
  duration_t = base_duration * (1 + gamma * clamp(rpe_t / ema_rpe, 0, 5))
  # Apply attenuated update to next ceil(duration_t) tokens:
  for k in range(1, ceil(duration_t)):
    W += lr * exp(-k / duration_t) * delta_W_t                 # exponential decay
```

This preserves the v1 BASE_LR but extends the WINDOW. ∫(lr * decay) over [0, duration_t] stays constant per-token under the right normalization — i.e. it is NOT a magnitude amplification but a TIME-EXTENSION of credit assignment.

**Why v1 BETA=1.0 multiplicative-positive failed where this might lift:** v1's formula CONCENTRATES additional gradient at the surprising token. Brain disperses it FORWARD in time (and BACKWARD via retrograde dopamine modulation per Brzosko-Paulsen 2017). The substrate cf-RPE delta-rule already has Hebbian co-firing as the "what to update"; what's missing is the "extended credit window" mechanism. P_deflated = 0.50 (CAPPED novel-synthesis; brain unambiguous; substrate has chain-grade cf-RPE to build on; cheap to test).

### FORMULA 2 — INVERSE-multiplicative (Yu-Dayan caution; opposite of v1)

**Brain literature:** Yu & Dayan 2005 (*Neuron*; PMID 15944135) — UNEXPECTED uncertainty (high RPE-variance) signals via NOREPINEPHRINE, and the resulting effect is to SUPPRESS learning until context-stability re-established. Computational interpretation: when delta is large AND unpredicted, brain's optimal-inference is to DAMP the per-token update (variance-weighted Kalman gain decreases under high observation noise; classic precision-weighting).

**Substrate-native formula:**
```
alpha_t = base_lr / (1 + beta * clamp(rpe_t / ema_rpe, 0, 5))
```

**Why this might lift where v1 failed:** v1 amplifies updates ON high-RPE tokens, which COMPOUNDS gradient noise. cf-RPE rule is itself a delta-rule; on noisy targets, the delta will be large precisely when src->target is ambiguous (rare context, polysemy, OOV-adjacent). Multiplying LR by RPE in that regime concentrates updates on the WRONG examples (the ones with no robust signal). Inverse-multiplicative would put the LR on the EASY-confident tokens where the gradient is reliable. P_deflated = 0.35 (no direct brain-formula precedent for inverse-LR on RPE; brain uses ACh/NE not dopamine for this; but mechanistically clean).

### FORMULA 3 — PEARCE-HALL associability (variance-normalized)

**Brain literature:** Pearce & Hall 1980 (and Mathys et al 2020 *PLOS-CB* "Simple model for learning in volatile environments") — associability `a(t+1) = b * |delta(t)| + (1-b) * a(t)`. LR is the ASSOCIABILITY itself, which is the EMA of absolute prediction error. High when CS is unpredictable; low when CS reliably predicts outcome. Mathys 2020 shows this is mathematically equivalent to the Behrens 2007 hierarchical-Bayesian volatility-tracked LR.

**Substrate-native formula:**
```
a_t = b * abs(rpe_t / norm_factor) + (1 - b) * a_{t-1}     # b ~ 0.1
alpha_t = a_t * base_lr_scale                              # multiplicative scale of base
```

**Why this might lift:** v1's normalization `rpe_t / ema_rpe` does NOT give variance; it gives RATIO. Pearce-Hall is variance-tracking. In a regime where RPE distribution has fat tails (which substrate-LM almost certainly does — Zipfian word freq + sparse-bipolar encoding), variance-tracking adapts the LR to the CHANGING noise floor, not the instantaneous noise. P_deflated = 0.40 (well-validated brain mechanism; clean math; substrate-native via EMA-tracking already proven in cf-RPE rule).

### FORMULA 4 — SIGMOIDAL-Schultz (saturation)

**Brain literature:** Schultz 1997/2016 (DCNS) — dopamine response saturates at upper bound. Modeled as `phi(x) = sigmoid((x - baseline) / sigma)`. Frontiers Comput Neurosci 2022 ADHD model uses this form explicitly. Tonic-dopamine 2025 *Nature Comms* — sigmoidal dose-occupancy of D1/D2 receptors creates asymmetric LR (positive RPEs lift LR LESS than negative RPEs lift LR, because D2 has higher affinity).

**Substrate-native formula:**
```
alpha_t = base_lr * sigmoid((rpe_t - baseline_rpe) / sigma_rpe)
       with baseline_rpe = EMA(rpe), sigma_rpe = EMA(|rpe - baseline|)
```

**Why this differs from v1:** v1 was LINEAR-in-RPE within [0, 5] clamp. Sigmoid is BOUNDED at top, COMPRESSES high-RPE outliers (which v1's clamp also does, but linearly within window). Mechanistically, sigmoid says "extreme surprises don't drive proportionally larger learning" — saturation. v1's near-linear within clamp says they DO drive proportional learning. Brain canonically saturates. P_deflated = 0.30 (similar to v1 but BOUNDED; modest improvement expected; may not clear +0.05 bar).

### FORMULA 5 — TD-error GATED (threshold)

**Brain literature:** STDP gating per Fremaux & Gerstner 2016 (*Frontiers in Neural Circuits*) — three-factor learning rules require ELIGIBILITY TRACE * MODULATOR; if modulator is BELOW threshold, no plasticity. Gates suppress noise updates. Mahesh-Hutchinson 2019 (arXiv 1911.00307) "error-gated three-factor learning rules" — synaptic plasticity is gated by precision (inverse uncertainty).

**Substrate-native formula:**
```
alpha_t = base_lr if abs(rpe_t) > threshold else 0
threshold = c * sigma(rpe_t over recent window)
```

**Why this might lift OR fail in interesting way:** GATING means MOST tokens don't update. This reduces noise (good) but also reduces effective N_TRAIN (bad). The trade-off depends on what fraction of tokens have informative gradients. For text8 LM at V=4000, Zipfian common tokens have low RPE (predictable); rare tokens have high RPE (informative). GATED rule would focus updates on the rare tokens — which is EXACTLY the regime where Hebbian co-firing has fewest co-occurrences to leverage. May suffer from sample-starvation on informative-but-rare. P_deflated = 0.25 (sample-efficiency tradeoff unclear; brain has dense co-firing so gating is OK there; substrate may not).

### FORMULA 6 — DOYA 2002 ACh-control (acetylcholine NOT dopamine)

**Brain literature:** Doya 2002 (*Neural Networks*) — in his 4-neuromodulator mapping, ACh controls LR (not dopamine). Dopamine controls TD-error magnitude itself. Doya's framework: `alpha = phi_ACh(state)` where ACh is environment-stability-dependent, NOT prediction-error-dependent.

**Substrate-native formula:**
```
alpha_t = base_lr * sigmoid((stability_signal - baseline) / sigma)
stability_signal = -EMA(|rpe_t|)   # negative variance proxy
```

**Why this is structurally different from all the above:** v1 + Formulas 1-5 all use RPE to modulate LR. Doya argues LR is modulated by a SEPARATE neuromodulator (ACh) tracking environmental stability — orthogonal to the cf-RPE channel. This is the most direct brain-existence-proof for "what v1 did wrong": v1 used the WRONG neuromodulator analog. P_deflated = 0.35 (Doya's mapping is influential but simplified; testing it as substrate-native requires a SECOND state-variable beyond RPE).

---

## (e) Cross-thread synthesis

### Compose with cf-RPE chain-grade (already validated)
The v1 baseline ARM_FIXED_LR achieved BPC=7.0642 vs the prior chain-grade ARM_CFRPE_ONLY=7.1052. The v1 baseline is ~0.04 bits BETTER than prior chain-grade reference — this is real (v1 used N_TRAIN=100k vs prior's N_TRAIN may have been smaller). Confirms cf-RPE delta-rule is the right anchor. ALL rescue cells in this note keep ARM_FIXED_LR with cf-RPE base_lr=0.5 unchanged.

### Compose with N_STEPS sensitivity (asymptote curve in flight)
If `exp_substrate_cfrpe_n_steps_curve_v1.py` shows BPC continues falling past N_TRAIN=100k (not yet asymptoted), then meta-LR rescue cells should run at the asymptote-N to avoid confounding LR-modulation lift with under-training. Recommend coordinating: dispatch meta-LR-rescue at SAME N_TRAIN as N_STEPS curve's first-stable point. If asymptote is at N_TRAIN=200k, run rescues at 200k.

### Compose with TAU_NEG=10 STDP (in flight)
**KEY INSIGHT — STDP window timing IS the brain's eligibility-trace duration mechanism.** Brzosko-Paulsen 2017 (*eLife*, DOI 10.7554/eLife.27756) shows dopamine BROADENS the STDP timing window for LTP into the post-before-pre regime — i.e. dopamine = eligibility-trace-window-extender, EXACTLY matching the Gong/Coddington 2026 magnitude-via-duration finding at the synaptic level.

This means the duration-extension rescue (Formula 1) AND the TAU_NEG=10 STDP cell are testing the SAME brain mechanism via different substrate mechanisms. If both lift, they should COMPOSE multiplicatively (3-way synergy with cf-RPE, like the validated cfrpe x STDP superadditive cell). If duration-extension lifts but TAU_NEG=10 doesn't (or vice versa), the brain analog tells us which substrate mechanism better captures dopamine-broadened-eligibility.

**Recommend:** after TAU_NEG=10 lands, immediately run a `cfrpe x stdp x duration_lr` 3-way composition cell at the dominant TAU_NEG setting.

### Anti-pattern audit — what v1 got wrong
1. **Used MAGNITUDE not DURATION.** Our own Store (2026-05-24 dopamine article drill) explicitly diagnosed this as the load-bearing dimension. v1 wasn't authored against that note.
2. **Used MULTIPLICATIVE-POSITIVE (compound errors).** Brain literature is split between INVERSE (Yu-Dayan caution) and SATURATING (Schultz sigmoid). NO brain mechanism unambiguously supports unbounded multiplicative-positive.
3. **EMA timescale too short (ema_alpha=0.05 -> ~20 step).** Brain timescales are ~10s -> at 1 token/0.05s reading rate ~ 200 tokens, NOT 20. The EMA was tracking transient fluctuations not stable noise floor.
4. **NO comparison to brain-canonical alternatives.** Cell tested ONE formula; cell-author should have tested formula-bank.

---

## (f) Substrate-product implications

### If DURATION rescue HARD_PASSES
- Opens substrate-product capability: **"context-extension learning rule"** — substrate LM can learn from rare/surprising tokens by propagating updates forward in time, mimicking biological credit-assignment-window-extension. This is a genuine substrate-product story for capability that GPT/Llama LACK (their gradient credit-assignment is timestep-local within a batch).
- Cap_map: open new sub-row "Meta-LR duration-mode" under cf-RPE chain.
- Composition: 3-way `cfrpe x stdp x duration` if TAU_NEG=10 also lifts.

### If PEARCE-HALL rescue HARD_PASSES
- Opens "**variance-tracked LR**" substrate primitive — adaptive without RPE-magnitude coupling.
- More robust than DURATION for noisy domains (TBD: multi-domain KG portfolio).

### If ALL rescues HARD_FAIL
- Strong evidence "meta-LR via RPE is not load-bearing for cf-RPE delta-rule in substrate-LM regime."
- Close the cap_map row.
- Pivot: meta-learning gap (CLAIM 8 from brain-to-LM audit) needs DIFFERENT mechanism — e.g. fast-slow-weights (which has separate exp_dev cell in flight per fleet).

### If DURATION HARD_FAILS but INVERSE HARD_PASSES
- USER intuition refuted at substrate; brain mechanism transferred wrong direction.
- Substrate caution-on-noise pattern matches Yu-Dayan ACh/NE not dopamine — re-frame as "uncertainty-modulated LR" not "dopamine-modulated LR."

---

## Citations (verified count: 9)

1. Schultz W. 2016 — "Dopamine reward prediction error coding." *Dialogues Clin Neurosci* 18(1):23-32. PMID 27069377. https://pmc.ncbi.nlm.nih.gov/articles/PMC4826767/
2. Yu AJ & Dayan P. 2005 — "Uncertainty, neuromodulation, and attention." *Neuron* 46(4):681-92. PMID 15944135. https://pubmed.ncbi.nlm.nih.gov/15944135/
3. Brzosko Z, Zannone S, Schultz W, Clopath C, Paulsen O. 2017 — "Sequential neuromodulation of Hebbian plasticity offers a mechanism for effective reward-based navigation." *eLife* 6:e27756. DOI 10.7554/eLife.27756. https://elifesciences.org/articles/27756v1
4. Doya K. 2002 — "Metalearning and neuromodulation." *Neural Networks* 15(4-6):495-506. https://people.sissa.it/~ale/EvolNeurComp/2022/II_Doya_2002.pdf
5. Fremaux N & Gerstner W. 2016 — "Neuromodulated Spike-Timing-Dependent Plasticity, and Theory of Three-Factor Learning Rules." *Front Neural Circuits* 9:85. https://www.frontiersin.org/journals/neural-circuits/articles/10.3389/fncir.2015.00085/full
6. Behrens TE et al. 2007 — "Learning the value of information in an uncertain world." *Nat Neurosci* 10(9):1214-21. (cited via Mathys 2021 review)
7. Mathys C et al. 2020 — "A simple model for learning in volatile environments." *PLOS Comput Biol*. https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1007963
8. Gong R, Martell J, Dudman J, Coddington L. 2026 — "Mesolimbic dopamine ramps reflect environmental timescales / reward-timescale controls dopaminergic learning rate." *Science* DOI 10.1126/science.aeb0813 (per prior research_dopamine_article_drill_2026-05-24.md). Cross-reference: https://elifesciences.org/reviewed-preprints/98666v1
9. Pawlak V, Wickens JR, Kirkwood A, Kerr JN. 2010 — "Timing is not Everything: Neuromodulation Opens the STDP Gate." *Front Synaptic Neurosci* 2:146. (cross-validated via Frontiers Neuromodulation of STDP 2019 review at https://www.cell.com/neuron/pdf/S0896-6273(19)30494-5.pdf)

Plus our own Store: `notes/research_dopamine_article_drill_2026-05-24.md` (already identified DURATION as load-bearing — meta-LR v1 IGNORED this prior finding).

---

## Self-discipline check

- [x] Generic math terms only in external queries (no substrate-novel mechanism names off-platform; queries were "Schultz dopamine sigmoidal", "Pearce-Hall associability", etc.)
- [x] Lit-scan calibration penalty: 0.15 deflation applied; novel-synthesis cap at 0.50 enforced (DURATION P=0.50 max, others <=0.40).
- [x] Hard-fail thresholds explicit per formula.
- [x] Did NOT pre-judge adjacent methods — analyzed 6 formula families, only 1 was tested in v1.
- [x] Cross-thread synthesis with cf-RPE chain-grade, N_STEPS curve, TAU_NEG=10 (3 in-flight threads).
- [x] Substrate-product implications per HARD_PASS / HARD_FAIL paths.
