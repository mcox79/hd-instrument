# ROUTING -- Joint D+H brain-correct rung-1 redesign (multiplicative gating + cf-RPE)

**From:** Research session
**To:** Orchestrator (primary)
**Date:** 2026-06-04
**Type:** Empirical experiment / LLM-integration probe (Orchestrator routes to Testbed)

---

## Capability question

Can a brain-correct substrate-as-training-mechanism architecture (continuous float32 substrate + Hebbian core + cf rank-1 substitution as RPE + sparse multiplicative gating at p <= 1/K) train a tiny character-level LM at rung-1 scale where the as-shipped bipolar-additive-PCGrad design produced zero converged seeds?

## Pre-reg HP/MID/HF bands

**HARD-PASS (joint D+H + continuous float32 trains tiny LM):**
- >= 4/5 seeds converge to val_loss < 3.5 bits/char by step 500
- Mean gradient norm >= 0.80 * K=1-baseline norm (per Drill 1 prediction at p = 1/K = 0.125)
- Router entropy > log(2) bits (no gating saturation)
- Substrate alpha (capacity ratio) tracked across run; below alpha_c at all times
- No stale-cache failures (cf substitution always against freshly-computed v)

**MIDDLE:**
- 2-3 / 5 seeds converge
- Norm ratio 0.40-0.80 of K=1 baseline
- Router entropy in [0.5, log(2)]
- 1-2 capacity warnings or stale-cache events but not catastrophic

**HARD-FAIL:**
- Norm < 0.10 * K=1 baseline (gating collapse) OR
- 0-1 / 5 seeds converge OR
- Norm oscillation > 3x mean (instability) OR
- Capacity exceeds alpha_c at any time (substrate saturation)

## Resource

Local CPU runner (rung-1 scale; ~10k char-LM params; N=4096 substrate dim).

## Cost ceiling

$0 (CPU). Wall ~30-60 min per condition; 5 conditions x 5 seeds = ~3-4 hours total wall on single CPU runner.

## P_deflated

- Joint D+H + continuous float32 trains tiny LM at rung 1: **0.40-0.50** (additive synergy: Drill 1 P=0.38 sparse multiplicative + Drill 2 P=0.32-0.44 cf-RPE + continuous float32 fixes bipolar 97% MI loss)
- Conservative: 0.40 (apply additional lit-scan calibration penalty for novel architectural synthesis)
- Cap novel-synthesis at 0.50 per discipline

---

## What this is (plain language)

The five brain-inspired tiny-scale HFs (substrate-trained mini LM, curriculum, ICL, spectral monitor convergence-phase, 8-channel orchestration) all share underlying causes identified by 5 deep drills:

| Constraint | Drill | Fix |
|---|---|---|
| Hebbian PCA-only convergence | META 3x+ | cf rank-1 substitution as RPE (TD-analog) |
| No scalar objective | META 3x+ | cf-RPE delta IS the objective |
| 8-channel PCGrad cycle collapse | META 3x+ / C 3x | sparse multiplicative gating at p <= 1/K |
| Bipolar 97% MI loss per coord | Grouped 2x | continuous float32 substrate |

Two follow-up drills confirmed the joint architecture is algebraically clean:
- Drill (multiplicative gating 2x): sparse multiplicative at p <= 1/K dissolves PCGrad cycle by construction; K=1 baseline gradient norm equivalence
- Drill (cf-RPE 2x): cf rank-1 substitution provably gives conditional-probability supervised signal (TD-analog + predictive-coding equivalence)

The joint architecture is brain-correct: one core learning rule (Hebbian) modulated by sparse temporal cf-RPE signal. Matches biological neuromodulator gating pattern (BCM + Klampfl-Maass three-factor + MoE top-1 isomorphism).

---

## Experiment design (5 conditions, 5 seeds each)

**Anchor name:** `substrate_joint_dh_brain_correct_rung1_v1_n4096`

### Conditions

- **Arm A (K=1 baseline):** Pure Hebbian outer-product write on tiny char-LM; no modulation. Establishes baseline norm and val_loss trajectory.
- **Arm B (cf-RPE alone, no gating):** Hebbian + cf rank-1 substitution as supervised signal; no multiplicative gating; uses dense cf-RPE every step. Tests cf-RPE alone vs Hebbian.
- **Arm C (sparse multiplicative gating, no cf-RPE):** Hebbian + sparse multiplicative modulator at p=0.10 with K=8 random modulators (no semantic content). Tests gating mechanism without error signal.
- **Arm D (joint D+H, k=4 channels):** Hebbian + cf-RPE + sparse multiplicative gating at p=0.25, K=4 channels. Tests joint architecture at low K.
- **Arm E (joint D+H, K=8 channels):** Hebbian + cf-RPE + sparse multiplicative gating at p=0.125, K=8 channels. Full architecture at brain-analog channel count.

### Channels for Arms D and E

K=4 (Arm D): cf-RPE + capacity-ratio + drift (kappa_3) + activation-erank
K=8 (Arm E): above + 4 phasic event-triggered channels (deletion-cert, place-field-tag, anti-Hebbian-error, multi-bank-routing)

### Continuous float32 substrate

All arms use continuous float32 substrate (drop bipolar {+/-1}). Drill (Grouped 2x) identified bipolar 97% MI loss per coord as binding constraint.

### Three structural mitigations required

1. **No-cache cf:** always recompute stored value at the moment of cf substitution; no caching of v_old (FM-1 mitigation per cf-RPE drill)
2. **Capacity tracking:** monitor alpha = M / N at every step; early-stop if alpha > 0.9 * alpha_c (FM-4 mitigation per cf-RPE drill)
3. **Router entropy guard:** Shazeer 2017 noise injection on gating router; track entropy > log(2) bits; FiLM affine gating as fallback (gating saturation mitigation per Drill 1)

### Training details

- Model: 2-layer LSTM or tiny transformer, ~10k char-LM params
- Substrate: N=4096 continuous float32
- Corpus: char-level Shakespeare or simple synthetic
- Steps: 500-1000
- Seeds: 5 per condition
- Per-condition wall: ~30-60 min CPU
- Per-cell partial JSON output (per testbed-progress-logging discipline)

---

## Expected outcomes

### If HP (Arm D or E)

- First positive empirical evidence for substrate-as-training-mechanism at small scale
- Validates joint D+H brain-correct architecture
- Cap_map: NEW sub-property founding under "substrate-as-training-mechanism" capability candidate row
- Unlocks rung-2 (4-layer char-LM, ~100k params) escalation
- P_deflated of full architecture re-estimates upward

### If MIDDLE

- Architecture partially works; iterate at rung 1 with variant sweeps (different K, p, modulator subsets)
- $0 to iterate

### If HF

- Joint D+H architecture refuted at rung 1
- Falls back to Design B (DeltaNet-pattern substrate-retrieval + SGD readout; published precedent at 1.3B)
- Separate routing for Design B prototype follows

---

## Status check

- [ ] Has any joint D+H architecture script been engineered?
- [ ] Is testbed currently working on rung-1 brain-inspired scaffold?
- [ ] Does the continuous-float32 substrate require new infrastructure or extends existing scripts?

Expected: not yet engineered; testbed scaffold ready for the continuous-float32 substrate variant.

---

## Discipline declarations

- Per [[feedback-routings-address-orchestrator-not-testbed]]: orchestrator primary; routes to Testbed
- Per [[feedback-small-scale-first-methodology]]: rung 1 first; cloud is last validation pass
- Per [[feedback-plain-language-experiment-tracking]]: described by what it tests
- Per [[feedback-no-padding-experiments]]: 5 conditions discriminate K=1 baseline vs cf-RPE-alone vs gating-alone vs joint architecture
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: HP/MID/HF tied to drill predictions
- Per [[feedback-envelope-expansion-fail-bands]]: explicit HF thresholds (norm < 0.10, gating collapse, capacity overflow)
- Per [[feedback-rehabilitation-after-rejection]]: 5 rescue paths consolidated; joint D+H is the brain-correct rescue
- ASCII-only output enforced

PROT-018: anchor name `substrate_joint_dh_brain_correct_rung1_v1_n4096` with _n4096 suffix
PROT-021: source=local CPU, run_mode=full, n_seeds=5

---

**END.**

**Orchestrator:** route to Testbed for engineering. Estimated engineering: 6-10h for continuous-float32 substrate primitive + cf-RPE no-cache + multiplicative gating router + Arm A-E scaffolds. Dispatch when engineering complete.

**Research session:** holds for verdict; will ship capability-implication note per outcome.
