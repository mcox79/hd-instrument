# Research Drill: Boredom/Attention Refinement 2x
# Scope: PP-325 BOREDOM-REAL gap (AUC 0.908, synthetic-to-real delta -0.092)
# Date: 2026-06-10

---

## HEADLINE

PP-325 BOREDOM-REAL gap (-0.092 AUC vs synthetic) is explained by at least four distinct mechanisms absent from synthetic training: (1) opportunity-cost temporal drift with non-linear onset (~30 min), (2) stretched-exponential novelty decay with half-life ~69 min, (3) dopamine-threshold bistability (the ADHD hyperfocus/boredom switch), and (4) cross-modal attention reallocation under sustained load. All four mechanisms are implementable as adversarial stream augmentations or temporal curriculum designs. Deflated P that all four compound into a deployable production solution: 0.38.

---

## Context: What PP-325 achieved and where it fell short

PP-325 achieved AUC=0.908 on synthetic boredom labels. The -0.092 gap to real-web-attention data is the primary refinement target. Synthetic data lacks:
- Temporal dynamics: synthetic labels treat each sample as i.i.d.; real boredom is a state that builds and decays over minutes to hours
- Adversarial novelty: real users encounter genuinely novel stimuli that reset the decay curve; synthetic datasets have no injection mechanism
- Cross-modal context: real boredom is influenced by competing signals (audio, visual, haptic) not present in unimodal synthetic training
- Population heterogeneity: ADHD users, age-related differences, and collective/social boredom effects all broaden the real distribution

---

## Stream A: Biology -- Habituation, Dopamine, Default Mode, ADHD

### Habituation mechanics
Habituation is not passive decay. It involves at least two distinct mechanisms operating in parallel:
- Short-term synaptic depression (STP): pre-synaptic resource depletion at timescale 100ms-10s; governs rapid stimulus repetition effects
- Anticipatory suppression: the brain learns to predict and pre-suppress the distractor, allocating resources away before the stimulus arrives (Frontiers Cognition 2025 review; PMC 12218333)
- These two mechanisms are additive and distinguishable by inter-stimulus interval (ISI): STP dominates at short ISI, predictive suppression dominates at longer ISI

The key implication for production detection: a boredom signal that uses only instantaneous prediction error will miss the anticipatory component. A system needs a history buffer of length sufficient to cover the STP+predictive window (estimated 1-30 seconds for STP recovery, minutes for predictive component).

### Dopamine and novelty gating
Dopamine is not purely reward-encoding; it is novelty-gated (eNeuro 2025, ENEURO.0358-25.2025). Novelty manipulations increase dopamine release and can reverse the directionality of cue-evoked responses. The mechanism: VTA dopamine neurons encode unsigned prediction error, and novelty increases their baseline firing rate independent of reward value.

The boredom signal arises when dopamine prediction error falls below a threshold: the default mode network (DMN) activates, redirecting cognitive resources internally (Neurosity, Springer 2016). This is the physiological substrate of the opportunity-cost model.

### ADHD as adversarial probe
ADHD represents a naturally-occurring perturbation of dopamine regulation that directly stresses boredom detection systems:
- Dopamine tonic/phasic imbalance: reduced tonic dopamine + preserved phasic response creates bistability -- extreme boredom on routine tasks, hyperfocus on novel high-reward tasks
- The ADHD attention state is NOT a continuous distribution around a single mode; it is bimodal (boredom-state / hyperfocus-state)
- Intra-individual response variability is elevated: latent brain state dynamics (PMC 8589642) show that the proportion of time in task-optimal vs non-optimal brain state predicts both variability and inattention
- Cross-modal: adults with ADHD show elevated auditory crossmodal activity in unimodal visual attention tasks (Frontiers Neuroscience 2023), meaning boredom in ADHD leaks across modalities differently than in neurotypical users

Production implication: a boredom classifier trained only on neurotypical sustained-attention data will fail on ADHD users. The feature distribution is genuinely bimodal, not just higher-variance. A mixture model or separate ADHD-conditioned pathway is needed.

### Default mode and prospective memory
Alpha oscillations in parietal and parietooccipital cortex mediate boredom effects on prospective memory (PMC 9043245). When boredom is high, alpha increases in these regions, indicating internally-directed attention. This is measurable from EEG or predicted from behavioral markers.

Key finding: boredom-related alpha is NOT the same as fatigue-related alpha. Boredom alpha increases coherence within DMN; fatigue alpha increases diffusely. A detector that conflates these will have systematic false positive errors in fatigued users who are NOT bored.

---

## Stream B: Materials Science -- Hysteresis, Fatigue, Thermal Noise

### Hysteresis: attention state depends on history
Attention does not respond symmetrically to increasing vs decreasing stimulation. Vigilance decrement shows hysteresis: once performance drops in the first 30 minutes (steep phase), partial recovery is achievable with breaks but full recovery requires substantially longer rest than the decline took.

Concretely:
- Decline phase: ~30 minutes to reach the plateau (Mackworth 1948 confirmed by Frontiers Cognition 2025)
- Recovery with rest: partial in 5-10 minutes, full requires 20-60+ minutes depending on task intensity
- The asymmetry is hysteresis: a system that predicts attention from current stimulus intensity alone, without tracking the integral of prior load, will overestimate current capacity

For implementation: the boredom/attention state needs a cumulative load integral (think: heat accumulator in thermal systems) that charges during high-demand periods and discharges during rest. The discharge time constant is longer than the charge time constant -- this is the hysteresis property.

### Fatigue vs boredom: distinct dynamics
Signal detection theory separates vigilance decrement into two components (Frontiers Cognition 2024):
- d' (perceptual sensitivity): decreases with fatigue; represents sensory processing degradation
- beta/c (criterion): shifts with boredom/motivation; represents decision threshold change

A key discriminator: cognitive fatigue primarily affects d', boredom primarily affects criterion. They co-occur but have separable causes and interventions. A boredom classifier that does not separately model criterion shift will conflate these two distinct states.

### Thermal noise analogy for threshold uncertainty
At high noise levels, weak signals can be detected via stochastic resonance (thermal noise helps). Analogously: mild task variability or mild novelty injection can maintain boredom threshold above detection threshold even during extended sessions. The materials-physics analogy: thermal fluctuations prevent a system from getting trapped in a local minimum (hysteresis loop). Adding random variability to stimulus sequences is the computational equivalent of thermal annealing for attention maintenance.

---

## Stream C: LLM Theory -- Temperature, Curiosity RL, Novelty Rewards

### Temperature sampling as attention proxy
Temperature controls the entropy of the sampling distribution. High temperature = high exploration = high curiosity state. Low temperature = exploitation = engagement with known structure.

Key finding (arxiv 2602.13035, Feb 2026): a hierarchical RL framework (Introspective LLM) learns an adaptive temperature policy from the model's own internal hidden states. At each decoding step, the model selects temperature based on its current hidden state. This is directly analogous to biological arousal-modulated attention: the system's internal estimate of its own uncertainty/engagement determines how much exploration it does next.

Mapping to boredom detection:
- High entropy in the model's hidden state distribution = high curiosity / low boredom
- Collapsing hidden state entropy over time = increasing boredom / habituation
- A learned temperature scheduler that detects entropy collapse and injects exploration is a computational implementation of novelty injection

### RND and exploration bonus decay
Random Network Distillation (RND, Burda et al. 2019) assigns intrinsic rewards based on prediction error between a fixed random network and a trainable predictor. Key property: the rate of exploration bonus decay is NOT well-defined -- it depends on SGD learning dynamics (arxiv 2301.13616).

Random Distribution Distillation (RDD, arxiv 2505.11044) addresses this by decomposing the intrinsic reward into:
- A pseudo-count term (proper exploration decay)
- A discrepancy term (predictor convergence)

The pseudo-count term has the correct asymptotic: it decays proportionally to visit count, ensuring proper habituation. This is directly applicable to attention modeling: the attention weight on a stimulus should decay with a pseudo-count-like schedule, not a naive time-based decay.

Deflated P that RDD-style pseudo-count bonus maps cleanly onto a production boredom detector: 0.35. The mechanism is right but the embedding space and scale mismatch between RL state spaces and natural attention streams is non-trivial.

### Curiosity-driven RL from human feedback (CRLHF)
arxiv 2501.11463 introduces curiosity as an explicit dimension of RLHF. Key claim: users who are curious provide more reliable feedback signals; bored users provide noisier, more variable feedback. This creates a direct product loop: boredom detection enables active feedback quality filtering, which improves downstream model quality.

---

## Stream D: New Paths -- Real-Web-Attention, Adversarial Novelty, Temporal, Cross-Modal, Age, Collective

### Real-web-attention gap: what synthetic data misses
The -0.092 AUC gap is not random error -- it is systematic bias from three structural differences:

1. Temporal autocorrelation: real attention sequences have strong autocorrelation (boredom builds over minutes); synthetic samples are typically i.i.d. or have short context windows. A model trained on i.i.d. samples will underfit the temporal dynamics.

2. Novelty injection events: in real web engagement, users encounter genuinely novel content that creates step-function resets in the boredom curve. These are not present in synthetic datasets. A model trained without novelty-reset examples will not learn the recovery dynamics.

3. Multi-session effects: real users carry prior session fatigue into new sessions. Synthetic data treats each session as independent. This creates systematic underestimation of boredom in users who have been active earlier in the day.

### Adversarial novelty injection
The opportunity-cost model (Semantic Scholar; Wojtowicz & Chater) formalizes boredom as the accumulation of opportunity cost of foregoing exploration. Key prediction: novelty injection resets the opportunity cost accumulator when the injected novelty exceeds the current alternative-activity value threshold.

Adversarial novelty injection as training augmentation:
- During training, randomly insert high-novelty items at variable intervals (exponential inter-novelty intervals with mean ~15-30 min based on collective attention half-life data)
- Annotate these insertions as attention-reset events
- Train the model to predict post-injection attention trajectory separately from pre-injection trajectory
- This teaches the model the shape of recovery, not just decline

HARD-PASS threshold for this augmentation: AUC improvement >= 0.03 on held-out real-web data with verified novelty-injection events. HARD-FAIL: AUC regression >= 0.01 from adding augmentation (means augmentation is introducing noise, not signal).

### Long-duration fatigue: temporal dynamics beyond 30 minutes
The vigilance decrement literature (Frontiers Cognition 2025) finds:
- First 30 min: steep non-linear decline (most of the decrement happens here)
- 30-90 min: plateau phase with slower decline
- 90+ min: highly individual-specific; some show recovery, some show continued decline

This means the feature space for boredom detection must change structure across the session:
- 0-30 min: rate-of-change features dominate (how fast is engagement dropping)
- 30-90 min: absolute level features dominate (what is the sustained engagement floor)
- 90+ min: recovery marker features become relevant (are there micro-recovery bursts)

A single feature extractor covering all three phases will underfit each. Temporal segmentation with phase-specific feature weighting is predicted to outperform a single-phase approach.

### Cross-modal boredom
Adults with ADHD show elevated auditory crossmodal activity during visual attention tasks (Frontiers Neuroscience 2023, PMC 10495991). This is not just ADHD-specific: in neurotypical users under boredom conditions, cross-modal intrusion increases (internal speech, spontaneous auditory imagery). The DMN activation during boredom is multimodal by nature.

Production implication: a unimodal boredom detector (e.g., text engagement only) will miss cross-modal boredom signals. A user who is nominally reading but whose attention is drifting to audio stimuli in the environment will appear engaged by unimodal text features. Multimodal fusion (gaze + text engagement + audio context if available) should outperform unimodal.

Cheap test: compare boredom detection AUC on users in quiet vs noisy environments using only text engagement features. If cross-modal boredom is real, AUC should drop in noisy environments. Expected delta: -0.03 to -0.07.

### Temporal dynamics: stretched-exponential novelty decay
Wu and Huberman (PNAS 2007, PMC 2077036) established that collective novelty decay follows a stretched-exponential (Kohlrausch-Williams-Watts) law:

r_t ~ exp(-0.4 * t^0.4)

where r_t is the novelty factor at time t (in hours). Key parameters:
- Half-life tau ~ 69 minutes (attention to a given item drops to 50%)
- r_t < 0.03 after ~3 hours (effectively zero engagement)
- The stretched exponent 0.4 < 1 indicates multiple underlying relaxation timescales (not a single-RC-circuit decay)

For a production boredom detector, this provides a principled temporal prior:
- Items should receive a novelty bonus that decays with this stretched-exponential schedule
- The bonus should reset (partially) when the user encounters a genuinely novel item
- The reset magnitude should be proportional to novelty distance from prior items (information-theoretic distance in embedding space)

Deflated P that this temporal prior improves real-web AUC: 0.32. The WW parameters were fit on Digg.com (2004-era news aggregator); generalizing to modern attention streams requires re-calibration.

### Age-dependent curiosity
Children show higher baseline novelty seeking (developmental curiosity); this declines monotonically through adolescence and levels in adulthood, with some recovery in older adults (information-seeking for health/meaning). The ADHD cross-section shows that the developmental trajectory is altered: novelty-seeking remains elevated but with lower boredom threshold (more easily bored AND more easily captured by novel stimuli).

Implementation: age as a moderator variable in boredom detection. Predicted effect: adding age as a feature should improve AUC by 0.01-0.03 depending on how age-diverse the real-web population is.

### Collective boredom: social synchronization effects
Wu and Huberman (2007) and EPJ B (2022, Springer) establish that collective attention to a novel item follows predictable decay dynamics. Social amplification can temporarily reverse individual boredom: seeing that many other users are engaged with an item triggers vicarious curiosity (social proof novelty reset).

Mechanism: collective attention signals act as exogenous novelty injection events from the user's perspective. A user who would otherwise be bored with an item can be re-engaged by social proof signals (comment counts, share rates, trending indicators).

Production implication: social engagement features (how many users are currently engaging) should be included in the boredom prediction feature set. This is a real-web-specific feature absent from synthetic datasets and may account for some of the -0.092 AUC gap.

---

## Stream E: Empirical Tests

### Cheap decisive test (pre-registered)

**Test E1: Temporal phase segmentation**
Split held-out real-web sessions into three phases: 0-30 min, 30-90 min, 90+ min. Train a phase-specific boredom classifier on each. Compare AUC against single-classifier baseline.
- HARD-PASS: mean AUC improvement across phases >= 0.02 (indicating temporal heterogeneity is real and learnable)
- HARD-FAIL: phase-specific AUC is worse than single classifier in >= 2 of 3 phases (indicating overfitting, not real structure)
- Cost: single data split + 3x training runs; estimated CPU hours < 2

**Test E2: Novelty-injection augmentation**
Add stretched-exponential decay temporal prior to training: novelty bonus decays as exp(-0.4*t^0.4) where t is time since item exposure. Compare AUC on real-web held-out.
- HARD-PASS: AUC improvement >= 0.03 (closing > 30% of the synthetic-real gap)
- HARD-FAIL: AUC regression >= 0.01 or loss of calibration (ECE worsens > 0.02)
- Cost: modification to data pipeline + 1 training run

**Test E3: ADHD population probe**
Separate the real-web test set by users with reported ADHD diagnosis vs not. Compute boredom detection AUC separately.
- HARD-PASS: AUC gap between ADHD and non-ADHD < 0.05 after adding ADHD-indicator feature or mixture model
- HARD-FAIL: AUC gap > 0.10 in both conditions (model is systematically failing on ADHD users)
- Cost: population metadata lookup + 2 inference passes

**Test E4: Cross-modal environment probe**
For real-web sessions with available ambient noise annotations (self-report or device sensor), compute AUC separately in quiet vs noisy conditions.
- HARD-PASS: AUC in quiet >= 0.92, gap quiet-vs-noisy < 0.03 (cross-modal noise is not a major confounder)
- HARD-FAIL: AUC in noisy < 0.85 (cross-modal boredom is a major unaddressed source of error)
- Cost: metadata filter + 2 inference passes; no retraining

---

## Falsifiable Predictions (HARD-PASS + HARD-FAIL)

| Prediction | HARD-PASS | HARD-FAIL | Mechanism |
|---|---|---|---|
| Temporal phase segmentation improves AUC | +0.02 mean across phases | Worse in >=2/3 phases | Non-linear vigilance decrement structure |
| Stretched-exponential novelty prior improves real-web AUC | +0.03 AUC | AUC regression >=0.01 | KWW decay from Wu-Huberman |
| ADHD subpopulation has bimodal boredom distribution | Mixture model AUC gap <0.05 | Gap >0.10 both conditions | Dopamine tonic/phasic bistability |
| Social engagement features reduce synthetic-real gap | +0.01 AUC on real-web only | No improvement AND new train-test leakage | Collective novelty reset mechanism |
| d' and criterion shift are separable in feature space | SDT decomposition identifies 2 factors with factor loadings >0.6 | Single-factor solution fits as well (p>0.1) | SDT theory of vigilance |

---

## Cross-Thread Synthesis

### Connection to continual learning findings
The boredom/habituation literature maps onto the continual learning forgetting literature (research_drill_continual_learning_revival_3x_2026-06-10.md). Both involve temporal decay of active states: in continual learning, stored representations decay without replay; in boredom, attentional representations decay without novelty injection. The replay mechanism in continual learning is structurally analogous to novelty injection in boredom: both reset a decay accumulator at the cost of temporarily interrupting normal processing.

### Connection to compositional depth findings
The compositional depth research (research_drill_substrate_compositional_shard_system_3x_2026-06-10.md) revealed that per-level cascading cleanup crosses capability cliffs. The ADHD hysteresis finding maps onto this: the attention system also has a cliff-like transition (boredom-state to hyperfocus-state) that is triggered by dopamine threshold crossing, not continuous degradation. Both systems exhibit state-space bistability with hysteresis.

### Connection to KB scaling and dual CLS
The dual CLS lift findings (research_drill_dual_cls_lift_2x_2026-06-10.md) suggest that two-stream architectures capture distinct signal types. The d'-vs-criterion decomposition from SDT vigilance theory provides independent motivation for a two-stream boredom architecture: one stream for perceptual sensitivity change, one stream for decision criterion shift.

---

## Substrate-Product Implications

1. **Temporal curriculum for training PP-325 successor**: training data should be organized as temporal sessions (not i.i.d. samples) with explicit phase labels (0-30 min / 30-90 min / 90+ min). This requires session-aware data loading, not a flat shuffle.

2. **Novelty injection as active probe**: during deployment, the product can deliberately insert high-novelty items at intervals predicted to exceed the user's current boredom threshold. The injection schedule should follow a stretched-exponential spacing (not uniform), since the decay is faster early and slower late.

3. **ADHD-aware feature design**: the product should not assume a Gaussian attention distribution. A mixture model or bimodal classifier is needed for population-level reliability. The simplest implementation: separate classifiers for high-variance users (detected by intra-session response variability) and low-variance users.

4. **d' vs criterion as separate product signals**: criterion shift (boredom-induced disengagement) responds to novelty injection; d' shift (fatigue-induced sensitivity loss) responds to rest. The product should distinguish these to serve the right intervention (inject novelty vs suggest break).

5. **Social proof features**: include collective engagement signals (trending indicators, social proof) in the real-time feature set. These act as exogenous novelty resets and are absent from synthetic training data -- their absence is likely a direct contributor to the -0.092 AUC gap.

6. **Hysteresis-aware state machine**: the attention model should maintain a cumulative load integral (charge faster during high-demand tasks, discharge slower during rest). This models the asymmetric recovery property confirmed across vigilance, fatigue, and materials-physics analogues.

---

## Calibration Notes

All P estimates below are after mandatory deflation of 0.15-0.25 from raw lit-scan estimates.

- P(temporal phase segmentation gives +0.02 AUC) = 0.52 (strong theoretical support, but real-web data may not have long enough sessions)
- P(KWW novelty prior gives +0.03 AUC) = 0.32 (mechanism clear, WW parameters need re-calibration for modern streams)
- P(ADHD mixture model closes gap by 50%) = 0.28 (strong mechanism, depends on ADHD prevalence and labeling in real-web data)
- P(all four mechanisms compound into +0.07+ AUC closing the full gap) = 0.38 (high mechanism plausibility, compounding is uncertain)
- P_cap_novel_synthesis = 0.38 (capped at 0.50 per calibration rule; four distinct mechanisms, each with individual uncertainty)

---

## Citations (verified)

1. Wu F, Huberman BA. Novelty and collective attention. PNAS 2007. https://www.pnas.org/doi/10.1073/pnas.0704916104 (PMC 2077036)
2. EPJ B 2022. Collective attention dynamic induced by novelty decay. https://link.springer.com/article/10.1140/epjb/s10051-022-00385-y
3. Frontiers Cognition 2025. Understanding vigilance and its decrement. https://www.frontiersin.org/journals/cognition/articles/10.3389/fcogn.2025.1617561/full
4. Frontiers Cognition 2024. Beyond detection rate: vigilance decrement using SDT. https://www.frontiersin.org/journals/cognition/articles/10.3389/fcogn.2024.1505046/full
5. eNeuro 2025. Novelty influences dopamine responses. https://www.eneuro.org/content/12/12/ENEURO.0358-25.2025
6. PMC 12218333. Anticipatory and reactive mechanisms of habituation to visual distractors. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12218333/
7. PMC 9043245. Alpha oscillations in parietal cortex explaining boredom and prospective memory. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9043245/
8. PMC 8589642. Latent brain state dynamics distinguish behavioral variability and inattention. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8589642/
9. PMC 10495991. Electrophysiological evidence for increased auditory crossmodal activity in adult ADHD. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10495991/
10. PMC 9342605. Mechanistic model of ADHD as dopamine phasic/tonic imbalance. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9342605/
11. PMC 3856320. Opportunity cost model of subjective effort and task performance. https://pmc.ncbi.nlm.nih.gov/articles/PMC3856320/
12. Semantic Scholar. Boredom and Flow: Opportunity Cost Theory. https://www.semanticscholar.org/paper/Boredom-and-Flow:-An-Opportunity-Cost-Theory-of-Wojtowicz-Chater/e556ea564856b8bd0c1a6fffd61b1178545b0ea2
13. bioRxiv 2020. Temporal Dynamics of Opportunity Costs. https://www.biorxiv.org/content/10.1101/2020.09.08.287276v2.full
14. PMC 7844088. Signal Detection Theory to understand cognitive fatigue. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7844088/
15. Gershman 2024. Habituation as optimal filtering. https://gershmanlab.com/pubs/Gershman24_habituation.pdf
16. arxiv 2602.13035. Introspective LLM: learning temperature policy from internal states. https://arxiv.org/abs/2602.13035
17. arxiv 2505.11044. Random Distribution Distillation. https://arxiv.org/html/2505.11044v1
18. arxiv 2301.13616. Anti-Exploration by RND. https://arxiv.org/pdf/2301.13616
19. OpenAI RND blog. Reinforcement learning with prediction-based rewards. https://openai.com/index/reinforcement-learning-with-prediction-based-rewards/
20. arxiv 2501.11463. Curiosity-Driven RL from Human Feedback. https://arxiv.org/pdf/2501.11463
21. Springer 2016. Boredom, sustained attention and the default mode network. https://link.springer.com/article/10.1007/s00221-016-4617-5
22. PMC 10513058. Boredom, attentional bias, and internet addiction. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10513058/

Verified count: 22 citations.

---

## Next-Drill Candidates

1. SDT d'-vs-criterion separation in embedding space (field: signal-detection / psychophysics) -- directly actionable as feature design decision
2. Pseudo-count novelty bonus decay schedules applied to attention modeling (field: curiosity-RL) -- maps RDD formalism onto production feature
3. Collective novelty decay re-calibration for modern platforms (field: network-science) -- WW parameters are 20 years old; need re-estimation
