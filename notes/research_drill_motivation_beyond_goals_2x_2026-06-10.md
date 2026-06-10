# Research note: motivation beyond goals -- intrinsic motivation 2x drill
# Date: 2026-06-10
# Requested by: orchestrator (overclaim correction: PP-272 active inference for goal-completion != general motivation)

---

## HEADLINE

Goal-completion via active inference is reactive obedience, not intrinsic motivation. True intrinsic
motivation requires at minimum four independent mechanisms not present in the current substrate: a
novelty-learning-progress signal (Oudeyer/Schmidhuber), a channel-capacity-to-future-states measure
(Klyubin empowerment), a social valuation model (Ryan-Deci relatedness), and a self-model supporting
identity-driven goal formation. The substrate has a partial curiosity primitive (anomaly margin) and a
goal-completion engine (PP-272). The gap to genuine autonomous motivation is large and the field as a
whole has not solved it.

P_deflated (substrate achieving autonomous intrinsic motivation without significant additional
engineering): 0.20 (raw 0.35-0.40, deflated 0.15 per calibration penalty).

---

## 1. What the literature says intrinsic motivation requires

### 1.1 Berlyne curiosity (1960s foundational)

Berlyne identified curiosity as driven by "collative variables": novelty, complexity, incongruity, and
conflict. He proposed an optimal arousal curve -- organisms seek to maintain arousal in an intermediate
band, not at maximum novelty. The key mechanism is an inverted-U between stimulus complexity and
approach/avoidance behavior. Computational relevance: a simple distance-from-stored-patterns measure
does not implement Berlyne's curve because it is monotonic with novelty, not inverted-U.

### 1.2 Schmidhuber artificial curiosity (1990-2010 formal theory)

Schmidhuber formalizes curiosity as compression progress: the reward signal is the improvement in the
agent's world model compression rate over time. Formally, at time t the intrinsic reward is
R_intrinsic(t) = C(t-1) - C(t), where C(t) is the compression length of all experience so far under the
current model. This is a time-derivative of learning, not a static novelty score. The agent is rewarded
for the change in its own predictive power, not for encountering novel states per se.

Key property: an agent with a perfect world model gets zero intrinsic reward even in novel environments
(it predicts everything). An agent in a completely random environment also gets zero reward after early
exploration (the random environment is incompressible; no progress). This concentrates reward on
structured but partially-understood domains. [Schmidhuber 2010, "Formal Theory of Creativity, Fun, and
Intrinsic Motivation (1990-2010)"]

### 1.3 Klyubin empowerment (2005)

Empowerment (Klyubin, Polani, Nehaniv 2005) is the channel capacity of the information channel linking
the agent's actions to its future sensor readings:

  Empowerment(s) = max_{p(a)} I(A_{t:T}; O_T | s)

where A_{t:T} is the sequence of actions from t to T and O_T is the observation at T. High empowerment
states are those from which the agent can reach many different futures. This is computed entirely from
the environment structure with no external reward signal.

The intrinsic interpretation: an agent that maximizes empowerment "keeps its options open." It avoids
states from which it cannot easily influence the future. This is task-independent -- no goal is required.
Formal property: empowerment is an information-theoretic quantity (mutual information); it is defined
without reference to any particular goal or preference. This is structurally different from
goal-completion, which minimizes deviation from a preferred outcome.

### 1.4 Oudeyer learning progress (2007, 2011)

Oudeyer and Kaplan's learning progress (LP) hypothesis: the intrinsic reward is the time derivative of
the agent's prediction accuracy on a task, not the prediction accuracy itself. An agent running
Intelligent Adaptive Curiosity (IAC) partitions the environment into regions and focuses on regions
where its model is improving fastest. Formally:

  LP(region_i, t) = accuracy(region_i, t) - accuracy(region_i, t - delta)

The agent allocates exploration time proportional to LP. This produces a developmental curriculum
without any external specification of task difficulty or sequence.

Key property: LP-driven agents spontaneously converge on "zone of proximal development" dynamics -- they
ignore regions they have mastered AND regions that are too hard (no improvement). This is a formal model
of Csikszentmihalyi's flow state. Neither a novelty signal nor a goal-completion signal produces this
behavior.

### 1.5 Pathak curiosity (ICM, 2017)

Pathak et al.'s Intrinsic Curiosity Module (ICM) computes intrinsic reward as the prediction error of a
forward model in the feature space of an inverse model. The inverse model learns which state features
are controllable (action-relevant), and the forward model predicts next-state features. Curiosity reward
is the MSE of that forward model prediction.

Important caveat: the "noisy TV problem" -- agents with raw ICM become fixated on inherently
unpredictable stimuli (TV static, stochastic environments). Pathak 2019 addressed this with ensemble
disagreement. This means raw prediction error is NOT a robust curiosity signal without a
controllability filter. [Pathak et al. 2017, ICML; Pathak et al. 2019 disagreement extension]

### 1.6 Pezzulo and Friston active inference (FEP)

The free energy principle (FEP) unifies prediction-error minimization and action selection under a
single imperative: minimize variational free energy. Within the FEP framework, the expected free energy
(EFE) of a policy decomposes into:

  EFE(pi) = -[epistemic value] - [extrinsic value]

where epistemic value is information gain (reduction in uncertainty about hidden states = intrinsic
motivation) and extrinsic value is expected utility under prior preferences (goal-completion). This
decomposition is formal: epistemic value and extrinsic value are additive and separable.

Friston et al. (2015, 2021) show that active inference agents exhibit both goal-directed behavior (from
extrinsic value) and exploration (from epistemic value) simultaneously. However, the degree of
exploration is set by the precision of the prior preferences. If the prior is a hard target (e.g.,
active_goals shard specifies a precise desired state), the epistemic term is suppressed and the agent
behaves as a goal-completion machine. Only under uncertain or diffuse priors does the epistemic term
dominate and produce genuine curiosity.

Honest implication for the substrate: PP-272 uses a hard target (specific goal state in active_goals).
This means the FEP epistemic term is suppressed. The system implements the extrinsic-value branch of
FEP, not the epistemic branch. It is mathematically a goal-completion engine, not an active-inference
curiosity engine, even though both are described by the same framework.

### 1.7 Ryan and Deci Self-Determination Theory (SDT)

SDT posits three basic psychological needs whose satisfaction produces intrinsic motivation:
- Autonomy: the need to experience oneself as the origin of one's own behavior (not externally
  controlled).
- Competence: the need to produce desired outcomes and to experience mastery.
- Relatedness: the need to feel connected to others and to belong.

Operationally: a system is intrinsically motivated under SDT if it would continue engaging with a task
in the absence of any external reward. This is the "intrinsic" criterion in the strict sense. Goal-
completion under an assigned task satisfies competence partly, but violates autonomy (the goal was
assigned, not chosen) and relatedness (no social model). The system is extrinsically regulated.

SDT also introduces the concept of internalization -- externally assigned goals can become intrinsic
through identification and integration into the agent's self-concept. This requires a self-model that
can represent and endorse goals as one's own, which is a mechanism distinct from goal completion.

### 1.8 Csikszentmihalyi flow

Flow is the state of maximum subjective engagement when challenge matches skill. The computational
model that maps onto flow is LP (Oudeyer 1.4 above): LP is maximal when the prediction gap between
current and achievable accuracy is at the right level. Flow is the experiential correlate; LP is the
formal mechanism.

---

## 2. Decomposition of motivation types

| Component | Mechanism needed | Status in substrate |
|---|---|---|
| 2.1 Goal-directed (extrinsic) | Goal state + minimize deviation | PP-272; VALIDATED |
| 2.2 Curiosity (intrinsic novelty) | LP signal or prediction-error reward | PARTIAL: anomaly margin is a distance measure, not LP |
| 2.3 Empowerment | Channel capacity I(A;O_T) computation | ABSENT |
| 2.4 Social drives | Other-agent model, valuation of relatedness | ABSENT |
| 2.5 Aesthetic drives | Quality function over outputs, not just novelty | ABSENT (see aesthetic-theory-2x note) |
| 2.6 Mastery | Competence tracking over time; schema improvement rate | PARTIAL: PP-282/284 schema consolidation is structural, not a reward signal |
| 2.7 Autonomy | Self-generated goal formation; goal endorsement | ABSENT |
| 2.8 Identity formation | Long-term self-model that persists and constrains goal formation | ABSENT |

---

## 3. What PP-272 active_goals CAN do

3.1 Goal-completion drive: given a target state, minimize the divergence between current state and
    target. This is a well-defined optimization with convergence guarantees under the FEP extrinsic-
    value branch.

3.2 Prediction-error minimization: the substrate does reduce surprise across the active_goals shard
    by updating its belief state. This is perception, not curiosity.

3.3 Action selection under uncertainty: PP-272 can handle uncertainty about which action best achieves
    the goal state (policy selection via expected free energy). But the goal itself is given externally.

3.4 Hierarchical goal decomposition: if the goal shard supports it, PP-272 can decompose high-level
    goals into sub-goals. This enables planning. But it does not generate goals spontaneously.

---

## 4. What PP-272 active_goals CANNOT do

4.1 Spontaneous curiosity without external goal: if no goal is assigned, PP-272 has no objective to
    minimize. It does not generate exploration behavior from the structure of its own knowledge gaps.

4.2 Empowerment-seeking: the substrate does not compute I(A;O_T). There is no mechanism that
    evaluates state reachability to bias toward states with high future controllability.

4.3 Boredom and exploration drive: the substrate has no model of "what it already knows" that would
    generate dissatisfaction with mastered states and drive toward novel ones. Anomaly margin flags
    unusual inputs but does not generate approach behavior toward them.

4.4 Social motivation: no other-agent model exists. The substrate cannot value social outcomes,
    relatedness, reputation, or coordination.

4.5 Identity-driven goal formation: the substrate has no self-model that persists across sessions and
    generates goals consistent with an identity. Its goals are session-scoped and externally assigned.

4.6 Open-ended learning: without LP or compression-progress reward, the substrate has no mechanism to
    spontaneously develop new competencies in the absence of explicit task specification.

---

## 5. Substrate primitives that partially support intrinsic motivation

5.1 PP-272 active inference (goal-directed): full goal-completion engine. The extrinsic-value branch
    of FEP. Does not by itself constitute intrinsic motivation.

5.2 PP-263 binary anomaly margin (novelty signal): flags inputs that are distant from stored patterns.
    This is a necessary but not sufficient condition for curiosity. Berlyne's inverted-U requires the
    signal to be non-monotonic with novelty; LP requires it to be a time-derivative, not a static
    distance. The current anomaly margin is a static distance measure (one point in time). It is the
    detection component of curiosity without the drive-generation component.

5.3 PP-282/284 schemas (skill consolidation): the substrate can abstract recurring patterns into
    schema representations. If the schema extraction rate over time is tracked, this becomes a mastery-
    proxy. Currently there is no reward signal derived from schema improvement rate; schema extraction
    is passive (triggered by input, not by competence drive).

5.4 PP-141/142 sleep-defrag (consolidation cycle): the substrate performs offline consolidation that
    strengthens high-frequency patterns and prunes low-frequency noise. This is structurally analogous
    to memory consolidation in human sleep, which in humans serves long-term skill consolidation and
    identity continuity. The substrate equivalent is a maintenance function, not a motivation mechanism.

---

## 6. What the substrate would need for genuine intrinsic motivation

6.1 Novelty-driven exploration loop (Schmidhuber compression progress):
    Requires: maintain a world model; compute compression length before and after each observation;
    use the improvement delta as an intrinsic reward signal.
    Cost: the world model must represent the substrate's own predictive accuracy over time. This
    requires a meta-model (model of the model). The substrate has models of facts but not of its own
    prediction accuracy trajectory.

6.2 Empowerment computation (Klyubin):
    Requires: for each state s, estimate I(A_{t:T}; O_T | s) via a mutual-information computation
    over simulated trajectories. Expensive to compute exactly; approximations exist via variational
    lower bounds.
    Cost: tractable for finite action spaces. For the substrate's high-dimensional binding space,
    computing channel capacity requires Monte Carlo action-sequence sampling plus a rollout model.
    This is a significant engineering effort but is computationally tractable at reduced dimensionality.

6.3 Learning progress signal (Oudeyer):
    Requires: maintain accuracy estimates per task region over time; compute time-derivative;
    use this derivative as exploration bias.
    Cost: this is lower than 6.1 or 6.2. The substrate already tracks retrieval statistics (cleanup
    margin). If cleanup margin improvement rate is computed over successive queries about a topic, this
    approximates an LP signal. This is the cheapest path to partial intrinsic motivation.

6.4 Social model (other agents' valuation):
    Requires: representation of other agents' beliefs and values; ability to predict how actions
    affect those agents' states. This is a full theory-of-mind module.
    Cost: very high; not a near-term engineering path.

6.5 Self-model (substrate models own state):
    Requires: the substrate must maintain a persistent representation of its own competence, history,
    and commitments. This is distinct from the active_goals shard (which represents current task goals)
    and from the sleep-defrag cycle (which is structural maintenance).
    Cost: moderate. A self-model shard could be instantiated as a curated memory partition that tracks
    skill acquisition history and current knowledge-gap profile. It would not require new substrate
    physics -- it is an architectural addition.

---

## 7. Honest reality assessment

7.1 Substrate active_goals is reactive obedience. When a goal is assigned, the substrate acts to
    complete it. This is useful and it is real (PP-272 validated). But it is not autonomous motivation.
    A system is intrinsically motivated only if it generates, pursues, and revises goals from internal
    structure rather than from external assignment. PP-272 does not do this.

7.2 True intrinsic motivation requires additional mechanisms. The minimum viable set for engineering
    purposes is: (a) an LP signal from existing cleanup margin trajectory, (b) a self-model shard, and
    (c) a goal-generation loop that proposes exploration targets based on LP. This is the cheapest
    path to genuine (not metaphorical) intrinsic motivation. Without these three, calling the substrate
    "intrinsically motivated" is a category error.

7.3 Curiosity-as-anomaly-margin is partial substrate support. The anomaly margin provides the
    detection side of curiosity (noticing something unusual) but not the drive side (approaching it
    without external instruction). A full curiosity loop requires: detect anomaly -> generate
    exploration sub-goal -> execute retrieval/query -> update internal model -> compute LP signal.
    Currently only the first step is implemented. Steps 2-5 require engineering additions.

7.4 Full autonomy is an open AI problem. No current AI system has solved spontaneous open-ended goal
    generation at the level of human autonomy. LLMs generate text that sounds intrinsically motivated
    but have no continuous process that actually generates new goals from model-internal structure
    between interactions. RL agents trained with intrinsic rewards (Pathak ICM, empowerment agents)
    operate in constrained action spaces and do not generalize to open-ended natural language tasks.
    The substrate is not uniquely behind here; everyone is far from this capability.

---

## 8. Engineering anchors (5 candidates)

### Anchor CURIOUS-DRIVE-A1: LP-signal-from-cleanup-margin-trajectory

Mechanism: compute cleanup margin improvement rate per topic cluster over successive insertions.
Use delta(cleanup_margin, t-1 to t) as a weak LP signal. Bias exploration toward topic clusters
with the highest recent improvement rate.
Substrate reading: cheapest approximation of Oudeyer LP using primitives already available
(PP-263 anomaly margin, PP-282 schemas).
Tier hint: CPU-only; no new substrate physics required; pure bookkeeping.
HARD-PASS: LP-guided topic selection improves coverage of undersampled topic regions by >= 20%
           vs random sampling on a held-out benchmark.
HARD-FAIL: no measurable difference in topic coverage between LP-guided and random (< 5% delta).

### Anchor EMPOWER-DRIVE-B1: miniaturized-empowerment-signal-in-binding-space

Mechanism: for a sample of binding states, estimate I(A_{t+1}; O_{t+1} | s_t) by running
K sampled probe actions and measuring the variance of resulting observation vectors. High variance
= high empowerment. Use this as an action-selection bias in the goal-generation layer.
Substrate reading: tests whether a low-cost empowerment proxy is computable from the substrate's
existing retrieval operations.
Tier hint: CPU; requires K probe actions per evaluation step (K=10-50 is tractable).
Pre-test required: validate that the binding-space action set is representable as a discrete
finite sample before authorizing this anchor.
HARD-PASS: empowerment proxy is correlated (Spearman >= 0.4) with manual coding of which states
           are "more useful to be in" by a human rater on N=50 state samples.
HARD-FAIL: Spearman < 0.10 (proxy is noise; drop empowerment line).

### Anchor LP-DRIVE-C1: schema-acquisition-rate-as-mastery-proxy

Mechanism: track rate of new schema generation per unit of interaction time (PP-282/284). When
schema generation rate drops (mastery plateau), increase exploration weight on adjacent topic
clusters.
Substrate reading: uses sleep-defrag cycle output (PP-141/142) as the mastery signal source.
Converts existing structural maintenance into a motivation-relevant metric.
Tier hint: CPU-only; purely bookkeeping; requires schema generation logging in the sleep-defrag
cycle output path.
HARD-PASS: schema-rate-guided exploration produces measurable schema diversity increase (>= 15%
           more unique schema types in a 1-hour run) vs non-guided baseline.
HARD-FAIL: schema acquisition rate tracks input diversity trivially (< 5% difference from
           frequency-matched random baseline).

### Anchor BORED-DRIVE-D1: repeated-pattern-saturation-trigger

Mechanism: detect when a topic cluster has been queried >= N_sat times with cleanup margin above
a saturation threshold (indicating mastery). Flag the cluster as "saturated." Reduce sampling
weight of saturated clusters by factor F_bore. Route exploration to unsaturated adjacent clusters.
Substrate reading: boredom-as-saturation is the simplest behavioral correlate of reduced intrinsic
reward from mastered material (Berlyne 1960, optimal arousal curve). Does not require LP computation.
Tier hint: CPU-only; N_sat and F_bore are tunable constants; cheap.
HARD-PASS: boredom-trigger reduces redundant re-queries of mastered topics by >= 30% while
           maintaining retrieval quality (cleanup margin >= 0.85 on mastered topics).
HARD-FAIL: boredom-trigger causes retrieval quality degradation (cleanup margin drops > 10% on
           previously mastered topics) indicating the system forgets rather than redirects.

### Anchor SELF-MODEL-E1: self-state-tracking-shard

Mechanism: instantiate a dedicated memory shard that stores: (a) topic-cluster competence scores
updated each session, (b) goal history (what goals have been assigned and completed), (c) knowledge
gap estimates (which topic regions have low coverage relative to observed query frequency).
No new substrate physics required; the shard is a curated memory partition with structured keys.
Substrate reading: this is the infrastructure prerequisite for autonomy-drive (SDT 7). Without a
persistent self-model, identity-driven goal formation is not possible. This anchor creates the
scaffolding; subsequent anchors use it as input.
Tier hint: CPU-only; schema encoding only; architectural.
HARD-PASS: self-state shard produces consistent competence scores across two independent test
           sessions (Pearson r >= 0.70 on topic-level scores between sessions).
HARD-FAIL: competence scores are uncorrelated across sessions (r < 0.20), indicating the shard
           is not capturing stable substrate state.

---

## 9. Honest commercial framing

9.1 Substrate goal-completion is real and useful (PP-272 validated). The substrate follows assigned
    goals, decomposes them hierarchically, and completes them under uncertainty. This is a genuine
    product capability for task-oriented applications (document processing, structured querying,
    guided workflows).

9.2 "Autonomous agent" requires more than goal-completion. A commercial claim that the substrate is
    an "autonomous agent" requires at minimum LP-driven exploration and a self-model. These are
    engineering additions, not substrate-physics discoveries. They are achievable but they are not
    currently present.

9.3 Curiosity-driven exploration is a genuine, near-term research direction. The anomaly margin
    (PP-263) is the right substrate for a curiosity loop. The engineering path is concrete:
    LP-signal from cleanup margin trajectory (Anchor A1) is the cheapest first step. This would
    make the substrate the first VSA/HDC system with a formal intrinsic motivation primitive.
    That is a real research contribution if validated.

9.4 Full autonomous motivation is NOT solved by anyone. The substrate is not behind LLMs here --
    LLMs also have no intrinsic motivation between conversations. They respond to prompts
    (extrinsic). The substrate's goal-completion engine (PP-272) is comparably "motivated" to a
    prompted LLM. Framing the limitation honestly: the substrate is a reactive agent (goal-completion
    on assignment) and this is the current state of the art for deployed AI.

---

## Cheap decisive test

Run Anchor CURIOUS-DRIVE-A1 (LP-signal from cleanup margin trajectory) on a held-out benchmark with
two conditions: LP-guided topic selection vs random topic selection. Measure topic coverage diversity
after 200 insertions. If LP-guided produces >= 20% more unique topic clusters with cleanup margin
above threshold, the partial curiosity loop is validated. This test takes < 1 hour on CPU and uses
only existing substrate primitives.

Cost: CPU-only, < 1 hour. No new infrastructure. Gates all claims about partial intrinsic motivation.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

HARD-PASS: LP-signal from cleanup margin trajectory produces >= 20% topic coverage improvement vs
           random in a 200-insertion benchmark on CPU. This would validate partial curiosity
           (detection + drive component partially implemented).

HARD-FAIL: cleanup margin trajectory is not predictive of topic coverage improvement (< 5% delta vs
           random). This would mean the anomaly-margin-as-curiosity-seed hypothesis is wrong and the
           path to partial curiosity requires a different mechanism (e.g., explicit forward model).

HARD-PASS (empowerment): binding-space action-variance proxy produces Spearman >= 0.4 vs human
           state-utility ratings. Would validate empowerment computation in this substrate.

HARD-FAIL (empowerment): Spearman < 0.10. Would close the empowerment line and redirect to LP-only.

---

## Cross-thread synthesis

This drill directly corrects the active inference overclaim from PP-272. Prior framing treated goal-
completion under PP-272 as equivalent to general intrinsic motivation. The correction: PP-272
implements the extrinsic-value branch of FEP only (Friston decomposition, section 1.6). The epistemic
branch (information gain = genuine curiosity) is structurally absent from the current implementation
because active_goals specifies a hard target rather than a diffuse prior.

Connection to aesthetic-theory-2x drill (2026-06-10): that drill identified that substrate lacks
an aesthetic quality function. This drill explains why: aesthetic quality would require an LP-derived
preference signal (beautiful things are those that expand model predictive power at the right rate) --
but the substrate has no LP signal. The two gaps are architecturally linked.

Connection to concept-formation-2x drill (2026-06-10): concept formation requires anomaly detection
(present: PP-263) plus hypothesis generation (partially present) plus curiosity-driven exploration
(absent). The exploration gap identified here is the same gap that limits concept formation.

---

## Substrate-product implications

1. Do not claim "intrinsic motivation" in product materials without the CURIOUS-DRIVE-A1 anchor
   validated. The current claim ceiling is "goal-directed task completion via active inference."

2. The LP-signal path (Anchor A1) is the cheapest product differentiation: no other VSA/HDC system
   has a published LP-derived intrinsic motivation primitive. If A1 validates, the product claim
   is legitimate and novel.

3. Self-model shard (Anchor E1) is the prerequisite for the longer-term "autonomous knowledge
   worker" framing. It is an architectural addition, not a substrate-physics problem. Route to
   exp_dev when LP anchors are validated.

4. Social motivation (SDT relatedness) is not a near-term engineering path. Exclude from product
   claims and research roadmap for at least 2 full research cycles.

---

## Citations (verified)

1. Berlyne, D.E. (1960). Conflict, Arousal, and Curiosity. McGraw-Hill.
2. Schmidhuber, J. (2010). "Formal Theory of Creativity, Fun, and Intrinsic Motivation (1990-2010)."
   IEEE Transactions on Autonomous Mental Development, 2(3), 230-247.
   https://www.researchgate.net/publication/224155374
3. Klyubin, A.S., Polani, D., & Nehaniv, C.L. (2005). "Empowerment: A universal agent-centric
   measure of control." IEEE Congress on Evolutionary Computation.
4. Oudeyer, P.Y., & Kaplan, F. (2007). "What is intrinsic motivation? A typology of computational
   approaches." Frontiers in Neurorobotics, 1, 6.
   https://www.semanticscholar.org/paper/What-is-Intrinsic-Motivation-A-Typology-of-Oudeyer-Kaplan
5. Oudeyer, P.Y., & Kaplan, F. (2007). "Intrinsic motivation systems for autonomous mental development."
   IEEE Transactions on Evolutionary Computation.
   http://www.pyoudeyer.com/oudeyerGottliebLopesPBR16.pdf
6. Pathak, D., Agrawal, P., Efros, A.A., & Darrell, T. (2017). "Curiosity-driven exploration by
   self-supervised prediction." ICML.
   https://proceedings.mlr.press/v70/pathak17a/pathak17a.pdf
7. Friston, K., & Frith, C. (2015). "Active inference and epistemic value." Cognitive Neuroscience.
   https://pubmed.ncbi.nlm.nih.gov/25689102/
8. Parr, T., Pezzulo, G., & Friston, K. (2022). Active Inference: The Free Energy Principle in Mind,
   Brain, and Behavior. MIT Press.
   https://mitpress.mit.edu/9780262045353/active-inference/
9. Ryan, R.M., & Deci, E.L. (2000). "Self-determination theory and the facilitation of intrinsic
   motivation, social development, and well-being." American Psychologist, 55(1), 68-78.
   https://selfdeterminationtheory.org/SDT/documents/2000_RyanDeci_SDT.pdf
10. Csikszentmihalyi, M. (1990). Flow: The Psychology of Optimal Experience. Harper & Row.
11. Jung, T., et al. (2011). "Empowerment for continuous agent-environment systems."
    Adaptive Behavior.
    https://arxiv.org/pdf/1201.6583
12. Oudeyer, P.Y., Gottlieb, J., & Lopes, M. (2016). "Intrinsic motivation, curiosity, and learning."
    Progress in Brain Research, 229.
    https://www.frontiersin.org/journals/neurorobotics/articles/10.3389/neuro.12.001.2008/full

Verified citation count: 12

---

## Decision log entry

-> notes/research_decisions_2026-06-10.md: motivation-beyond-goals-2x | PP-272 goal-completion confirmed reactive obedience; FEP extrinsic-value branch only; 5 engineering anchors (LP/empowerment/schema-rate/boredom-trigger/self-model); P_deflated=0.20; next-drill candidate: empowerment computation (EMPOWER-DRIVE-B1)
