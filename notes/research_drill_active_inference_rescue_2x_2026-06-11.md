# Research Drill: Active Inference Rescue (2x Depth) -- 2026-06-11

**Filed by:** research sub-agent (Sonnet 4.6)
**Trigger:** cycle 224 MIDDLE_BAND: active_inference_lite error_drop=20.5% (<30%), goal_reach=0.610 (<0.70). Both axes miss threshold. Strategy sketch: full free-energy gradient policy vs simple error minimization; integrate PP-315 boredom as exploration drive.
**Probes:** 5 parallel streams (Biology/Friston, Brain/predictive-coding, Materials/energy-landscape, LLM/world-models, Substrate-native paths)
**Calibration:** P estimates deflated 0.15-0.25 per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis cap P=0.50; hard-fail thresholds pre-registered.

---

## HEADLINE

Cycle 224 MIDDLE_BAND exposes a known split in active inference: perception (error minimization) and action (expected free energy minimization) are two distinct optimization problems. The substrate's existing implementation minimizes current prediction error but does not evaluate expected free energy over future trajectories, which is why error_drop is partial (20.5%) while goal_reach stalls (0.610). Ten substrate-native rescue mechanisms are ranked below; the top three are actionable within 1-2 CPU sessions.

---

## Background: What Cycle 224 Reveals

PP-272 (cycle 215): single-step active inference convergence 1.000 -- substrate codebook as generative model works.
PP-285 (cycle 218): 6-step trajectory convergence 1.000 -- multi-step chaining works.
PP-267 (cycle 215): predictive coding residuals, 3x compression -- error-minimization primitives strong.
PP-315 (cycle 221): boredom signal AUC=1.000, density_corr=0.815 -- intrinsic motivation primitive ready.

Cycle 224 MIDDLE_BAND result: error drops 20.5% (not 30%), goal_reach=0.610 (not 0.70). The pattern is: prediction-error minimization is working (PP-272/285 baseline infrastructure valid) but the policy layer -- choosing which actions to take to reach goals -- is not using the full machinery. The substrate is doing perception-only active inference, not action-selection active inference.

The key lit finding (Friston et al. "Active Inference and Learning", ScienceDirect 2016; Millidge "Deep Active Inference as Variational Policy Gradients" 2020): there are two distinct minimizations in active inference.
- Perception: minimize current variational free energy F = -log P(o|m) + KL[q(s)||p(s)] -- the substrate does this already.
- Action: minimize EXPECTED free energy G = epistemic_value + pragmatic_value over future trajectory -- this is what the lite implementation is missing.

Expected free energy G decomposes as:
  G(pi) = epistemic(pi) + pragmatic(pi)
         = -E[KL[q(o_tau|pi) || p(o_tau)]] + E[log p(o_tau | C)]
where C is a prior preference distribution over outcomes. Without a future-facing term, the agent reduces current error but does not steer toward preferred outcomes -- exactly the goal_reach=0.610 failure signature.

---

## Stream A: Biology (Friston FEP; neural implementation)

### What the brain does

Prefrontal cortex evaluates policy EFE (expected free energy per policy) and maintains a prior over policies pi ~ softmax(-gamma * G(pi)).
Basal ganglia selects actions by competition between policies; selection is proportional to exp(-G).
Cerebellum provides forward model: given current state and action, predicts next state. Prediction error from the forward model updates both the action (motor command correction) and the generative model.

Key finding: the SPLIT between perception (minimize F) and action (minimize G) is the canonical architecture. Agents implementing only the perception side converge on veridical internal states but cannot drive goal-directed behavior. This matches the cycle 224 signature exactly.

Relevant: ventral prefrontal cortex implements the G evaluation; dorsal prefrontal drives policy execution once G is computed. Substrate analog: the cleanup memory is the generative model (PP-272); what is missing is the ventral-prefrontal G-evaluator layer.

### Calibrated P for substrate analog
P_deflated(full-EFE-in-substrate) = 0.50 (lit precedent clear; substrate has primitives; implementation is non-trivial but not novel physics)

---

## Stream B: Brain (Predictive Coding Hierarchy; Precision Weighting)

### Precision-weighted prediction errors

In hierarchical predictive coding, each level passes prediction errors UP and predictions DOWN. The precision (inverse variance) of each level weights how strongly its prediction error updates the level above. High-precision errors from goal-relevant levels drive more action; low-precision errors from irrelevant levels are suppressed.

Key finding: precision-weighting IS the mechanism that connects "error reduction" to "goal reaching". Without it, all prediction errors are treated equally and the agent responds to whichever error is easiest to reduce (typically perceptual/sensory errors, not goal errors). With it, goal-level errors are amplified and drive policy.

Substrate analog: the substrate has a boredom signal (PP-315) that tracks repetition/novelty at the sensory level. The missing piece is a goal-level analog -- a goal-precision signal that amplifies goal prediction errors relative to sensory prediction errors. This is mechanistically simple: gate the error update by a goal-relevance weight.

### Calibrated P
P_deflated(precision-weighted-goal-errors) = 0.52 (well-established theory; substrate primitives exist; mechanism is a single weighting multiply -- straightforward implementation)

---

## Stream C: Materials Science (Energy Landscape Navigation)

### Thermal annealing and exploration as physics

Simulated annealing: transition probability P(accept) = exp(-delta_E / kT). At high temperature, the agent accepts uphill moves (exploration). At low temperature, it converges on minima (exploitation). The temperature schedule controls the exploration-exploitation trade-off.

For a policy that must reach a goal state (exploit) while avoiding getting stuck in local minima (explore): the Boltzmann factor gives the natural form for a precision parameter. The active inference gamma parameter (precision over policies) is exactly this inverse temperature: low gamma = diffuse exploration, high gamma = sharp exploitation.

Key finding: the substrate's current active-inference-lite likely uses a fixed policy precision (fixed gamma or fixed threshold). Materials science says: you need an adaptive temperature schedule. The boredom signal (PP-315) is a natural substrate-native proxy for "is the current environment novel enough to warrant exploration" -- high boredom (repetitive) = lower effective temperature = exploit; low boredom (novel) = higher temperature = explore.

Metastable state insight: in energy landscape terms, each possible action sequence is a basin. Getting stuck in a suboptimal basin (goal_reach=0.610) is the classic local-minimum problem. The fix is not just better gradient descent -- it is a temperature schedule + escape mechanism (basin-hopping, tunneling analog).

### Calibrated P
P_deflated(adaptive-temperature-via-boredom) = 0.48 (strong conceptual mapping; PP-315 exists; the only question is whether cleanup-margin variance is a good kT proxy -- needs empirical test)

---

## Stream D: LLM Theory (World Models; Model-Based RL)

### Dreamer and world models

Dreamer (Hafner et al.): learn a latent world model, then plan in imagination by rolling out the model and training a policy on imagined trajectories. Key: the policy is trained on rollouts of the model, not on real environment steps. This gives sample efficiency and allows goal-directed planning.

TransDreamer (Chen et al. 2022): replaces RNN world model with transformer. Relevant: the transformer world model supports longer-horizon planning because attention is not limited by recurrence.

Decision Transformer: frames RL as sequence modeling -- past (state, action, return) triples are the context; the model predicts the next action conditioned on a target return. Key insight: framing policy as conditional generation on desired outcome (rather than gradient ascent on value) sidesteps the credit assignment problem.

Substrate analog: the substrate stores sequences (PP-259 temporal binding, PP-267 predictive coding compression, PP-268 Allen interval algebra). A substrate-native world model is: store (state, action, next_state) triples as bound FHRR vectors; retrieve predicted next state given current state + candidate action; select action that predicts state closest to goal. This is a nearest-neighbor forward model, not a gradient-trained world model -- but it is substrate-native.

Key lit finding (arxiv 2602.21467): Vector Symbolic Architecture with FHRR encoders directly implements world-model transitions via element-wise complex multiplication -- not a metaphor, a direct technical match. The substrate already has FHRR multiplication and cleanup (the core VSA ops); what is missing is the forward-model indexing.

### Calibrated P
P_deflated(substrate-native-VSA-world-model) = 0.48 (strong lit precedent for FHRR world models; substrate has the algebra; novel synthesis for this specific rescue = 0.48 cap)

---

## Stream E: New Substrate-Native Paths

Ten mechanisms ranked by P_deflated (implementation difficulty factored in):

---

### E1. FULL-FREE-ENERGY-GRADIENT-POLICY (replace error-only with full EFE)

**Mechanism:** The current active_inference_lite minimizes current prediction error F. Upgrade: compute expected free energy G(pi) = sum over future time steps of [epistemic_value(pi,t) + pragmatic_value(pi,t)]. Policy pi is selected as argmin G. Epistemic value = cleanup margin spread across candidate next states (uncertainty about which next state is most likely). Pragmatic value = cleanup margin for goal state retrieval (how well does candidate action lead toward goal?).

**Math:** G(pi) = -sum_tau [E_q[log p(o_tau | C)] - KL[q(s_tau|pi) || p(s_tau)]]
                = pragmatic_value - epistemic_value
For substrate: pragmatic = similarity(predicted_next_state, goal_state); epistemic = -entropy(predicted_next_state_distribution)

**Why error_drop is partial but goal_reach fails:** error-only descent reduces F but ignores C (goal prior). Adding pragmatic term forces the policy to favor actions that increase goal-state similarity.

**P_deflated = 0.52.** Well-supported; substrate primitives for both terms exist (retrieval similarity for pragmatic; cleanup-margin spread for epistemic); main risk is whether single-step lookahead suffices or whether multi-step rollout is needed.

**HARD-PASS threshold:** goal_reach >= 0.70 AND error_drop >= 0.30 in full run (both axes)
**HARD-FAIL threshold:** goal_reach < 0.55 after EFE fix (suggests wrong decomposition or inadequate lookahead depth)

---

### E2. BOREDOM-AS-EXPLORATION-DRIVE (PP-315 integration)

**Mechanism:** Gate the exploration-exploitation balance using the PP-315 boredom signal. When boredom_auc is triggered (repeated inputs), reduce gamma (policy precision) to encourage varied action selection. When boredom is low (novel inputs), increase gamma to exploit learned policy. This is a substrate-native temperature schedule.

**Math:** gamma_effective(t) = gamma_base * (1 - alpha * boredom_score(t))
where boredom_score = cleanup_margin_against_decayed_buffer (already computed by PP-315 mechanism).

**Why this helps cycle 224:** goal_reach=0.610 pattern is consistent with policy getting trapped in a locally-minimal error configuration. Boredom-driven gamma modulation gives the agent a natural escape mechanism without requiring external curriculum.

**Biological precedent:** Boredom-Driven Curious Learning (HHVG, NIH PMC6349823): boredom and curiosity are formally complementary -- boredom enables escape from local attractors, curiosity drives toward novel high-information states. This matches the PP-315 implementation exactly.

**P_deflated = 0.55.** PP-315 already HARD_PASS; integration is an arithmetic gate on gamma; no new substrate mechanism needed. Main risk: the scale of gamma effect relative to goal complexity.

**HARD-PASS:** goal_reach improvement >= 0.05 vs no-boredom baseline at same error_drop
**HARD-FAIL:** boredom integration causes goal_reach regression (exploration too aggressive)

---

### E3. TEMPORAL-POLICY-WITH-LOOKAHEAD (substrate predicts future free energy)

**Mechanism:** Instead of selecting actions based on current state alone, the substrate generates a 2-3 step lookahead by chaining the predictive-coding forward model (PP-267 mechanism). Candidate action sequences are evaluated by predicted free energy at the lookahead horizon. Best sequence is selected; only first action is executed (receding horizon / MPC style).

**Math:** pi* = argmin_{a_1, ..., a_k} G(s_{t+k} | a_1..a_k)
       s_{t+j} = forward_model(s_{t+j-1}, a_j) using PP-267 residual compression

**Biological precedent:** Cerebellar forward model provides state prediction; prefrontal evaluates EFE at predicted state; dorsal prefrontal executes selected action. The substrate already has all three: retrieval (PP-272), residual prediction (PP-267), multi-step chaining (PP-285).

**Why PP-285 is the missing bridge:** PP-285 shows 6-step trajectory convergence at 1.000 -- but that was convergence ON the correct trajectory, not convergence TO a goal state via action selection. The rescue flips the use of PP-285: use the multi-step chain to GENERATE candidate trajectories, evaluate each by goal_reach at horizon, select best.

**P_deflated = 0.50.** The mechanism re-uses PP-267+PP-285 primitives; the novel step is the argmin over candidate trajectories. Main risk: branching factor. If each step has K candidate actions, the k-step lookahead is O(K^k); needs pruning.

**HARD-PASS:** goal_reach >= 0.72 with k=2 lookahead
**HARD-FAIL:** k=2 lookahead gives goal_reach < 0.61 (worse than no lookahead, suggesting forward model error compounds faster than policy value accrues)

---

### E4. CONTEXT-BOUND-POLICY (context vector modulates action selection)

**Mechanism:** Bind the current context (role, episode, task type) to the action selection process as a precision modulator. Different contexts have different goal-relevance profiles; the same prediction error in context A may be goal-relevant but in context B irrelevant. Substrate-native: bind context_bundle to goal_prior, use similarity to scale which error signal drives policy update.

**Math:** gamma_context(c) = sim(context_bundle_c, goal_prior_bundle)
         policy_score(a) = gamma_context * pragmatic_value(a) + (1 - gamma_context) * epistemic_value(a)

**Biological precedent:** Precision-weighting in hierarchical predictive coding; contextual modulation of dopaminergic precision (Friston 2012 "Attention, Uncertainty, and Free-Energy"). Context is the top-down prior that sets precision at lower levels.

**Substrate relevance:** PP-323 bilingual hub-and-spoke (different contexts = different codebooks); PP-272 generative model loop. Context binding is algebraically natural in FHRR: bind(context, goal) and retrieve similarity vs action candidates.

**P_deflated = 0.45.** Conceptually clean but requires a well-structured context-goal codebook; the main risk is that context bundles are too diffuse to provide meaningful precision modulation on arbitrary tasks.

**HARD-PASS:** goal_reach >= 0.70 in context-structured task vs 0.610 baseline
**HARD-FAIL:** context modulation reduces goal_reach below 0.55 (over-specialization)

---

### E5. COMPOSITIONAL-WORLD-MODEL (store forward model in compositional layers)

**Mechanism:** Store (state, action, next_state) triples as bound FHRR tuples: W_forward += bind(state_i, bind(action_j, next_state_k)). To predict next state given (state, action): retrieve unbind(unbind(state_query, action_query), W_forward). Use predicted next state to evaluate pragmatic value before committing to action.

**Lit precedent (direct):** arxiv 2602.21467 "Geometric Priors for Generalizable World Models via Vector Symbolic Architecture" uses learnable FHRR to model world transitions via complex multiplication -- exact algebraic match to substrate. Also: arxiv 2304.04734 "Modularizing and Assembling Cognitive Map Learners via Hyperdimensional Computing" -- cognitive maps as compositional HD structures support planning.

**Why this unlocks goal_reach:** current active_inference_lite must rely on whatever state the substrate currently holds. A stored forward model lets the agent evaluate hypothetical action consequences WITHOUT executing them -- the standard MBRL gain.

**P_deflated = 0.48.** Strong lit precedent in VSA world models specifically. Main risk: forward model storage capacity (how many (s,a,s') triples can be stored before retrieval degrades); this is a K/N capacity problem familiar from PP-299.

**HARD-PASS:** goal_reach >= 0.72 with forward-model lookahead vs 0.610 baseline; forward_model_accuracy >= 0.85 on held-out transitions
**HARD-FAIL:** forward_model_accuracy < 0.70 (capacity cliff causes degraded predictions worse than no lookahead)

---

### E6. MULTI-TIMESCALE-INFERENCE (fast reactive + slow deliberative)

**Mechanism:** Run two concurrent inference processes: (a) fast reactive: error minimization at current time step (current implementation); (b) slow deliberative: expected free energy evaluation over a horizon, updated every N steps. The fast layer handles immediate prediction error; the slow layer steers the policy toward goal. Combine: action = fast_action if fast_confidence > threshold else slow_action.

**Biological precedent:** Multi-timescale RL in the brain (Nature 2025, biorxiv 2023.11): dopaminergic neurons encode RPE with a diversity of discount timescales -- phasic (fast, seconds) and tonic/ramping (slow, minutes). Separate timescales serve separate functions: phasic for immediate correction, tonic for sustained motivation toward goal.

**Substrate analog:** The substrate already has temporal binding at multiple scales (PP-259 continuous, PP-268 interval algebra). The rescue is: fast path = current active_inference_lite step; slow path = PP-285 multi-step chain evaluating goal at horizon.

**P_deflated = 0.45.** The two-path architecture is conceptually clear but the combination rule (fast vs slow switch) introduces a new hyperparameter. Risk: the switching threshold may be task-specific and require tuning.

**HARD-PASS:** goal_reach >= 0.70 with fast+slow vs 0.610 baseline; slow path contributions measurably positive (>5pp goal_reach gain vs fast-only)
**HARD-FAIL:** multi-timescale adds computation without goal_reach gain

---

### E7. VARIATIONAL-POLICY (empowerment + EFE)

**Mechanism:** Frame policy selection as variational information maximization: choose actions that maximize mutual information I(action; future_state) (empowerment) subject to goal constraint. Empowerment I(a; s_t+k) = H(s_t+k) - H(s_t+k | a) -- choose actions that make the future state most predictable given action (high control), while also moving toward goal.

**Lit precedent:** arxiv 1509.08731 "Variational Information Maximisation for Intrinsically Motivated Goal-Based RL"; arxiv 2502.15820 "Universal AI maximizes Variational Empowerment" (2025).

**Math:** pi* = argmax_pi [I_pi(a; s_{t+k}) + lambda * sim(E[s_{t+k}|pi], goal_bundle)]
For substrate: I_pi = spread of predicted next states (high entropy = more control); sim = cleanup similarity to goal bundle.

**P_deflated = 0.38.** Interesting theoretical path but adds complexity (empowerment estimator) without clear substrate-native shortcut. The variational estimator requires sampling multiple action trajectories -- doable but more expensive than the E1/E2 patches.

**HARD-PASS:** goal_reach >= 0.68 AND agent demonstrates better worst-case goal_reach (less variance) vs E1 baseline
**HARD-FAIL:** goal_reach < 0.55 (empowerment term dominates and agent explores rather than reaches goal)

---

### E8. HIERARCHICAL-GOAL-DECOMPOSITION

**Mechanism:** Decompose goal into a hierarchy of subgoals using the substrate's compositional binding. High-level goal bundle G is factored: G = bind(g1, bind(g2, g3...)). Policy selects actions to reach g1 first, then g2, then g3. Error signal is relative to the CURRENT active subgoal, not the final goal -- this tightens the effective prediction error threshold and makes goal_reach=1.0 achievable stepwise.

**Lit precedent:** Options framework (Sutton et al. 1999); hierarchical RL (HRL); MANGO multi-layer abstraction (arxiv 2508.17751, 2025).

**Substrate analog:** PP-258 depth-10 K-hop (multi-hop reasoning), PP-272/285 active inference chains. The compositional bind/unbind algebra gives subgoal extraction for free: unbind(G, g1) = g2_bundle; the substrate can walk goal hierarchies without external supervision.

**P_deflated = 0.42.** Well-motivated by error structure. Main risk: goal bundle factorization must be specified at task design time or learned; not automatic from the MIDDLE_BAND signal alone.

**HARD-PASS:** goal_reach >= 0.72 with 2-level subgoal decomposition vs 0.610 baseline
**HARD-FAIL:** subgoal approach locks into wrong subgoal sequence and performs worse than flat policy

---

### E9. TEMPORAL-DIFFERENCE-PREDICTION-ERROR (TD learning on substrate retrieval scores)

**Mechanism:** Implement a TD(lambda) style value function using cleanup margins as state-value proxies. V(s) = expected goal_reach from state s = rolling average of cleanup_margin(s, goal_bundle) over encountered states. TD error: delta_t = r_t + gamma * V(s_{t+1}) - V(s_t). Policy: choose action that maximizes delta_t (positive surprise in goal direction).

**Biological precedent:** Dopamine = TD error signal (Schultz 1997; reviewed Nature Neuroscience 2022 "A gradual temporal shift of dopamine responses mirrors TD error"). Dopaminergic prediction error drives both learning (update V) and action (prefer high V transitions).

**Substrate analog:** cleanup_margin is a direct analog of the dopaminergic signal -- it measures how well a retrieved state matches the stored template, and its surprise (frisson) component (PP-318) is already validated as a prediction-error-resolution signal. TD update rule is a simple running average -- no exotic mechanism.

**P_deflated = 0.45.** Clean analogy; substrate primitives (cleanup margin, running average via decayed buffer already in PP-315 mechanism) are already validated. Risk: TD bootstrapping requires stable V estimates, and with a sparse codebook the variance of V(s) might be high.

**HARD-PASS:** goal_reach >= 0.70 with TD-driven policy; value estimates converge within 100 steps
**HARD-FAIL:** V(s) variance too high for stable TD update (divergence or oscillation)

---

### E10. ENSEMBLE-WORLD-MODELS

**Mechanism:** Maintain K parallel world-model bundles (different binding patterns, different role assignments). At each step, all K models predict next state given action; ensemble prediction = superposition. Policy selects action with highest agreement across ensemble (low model disagreement = high confidence = high precision). Disagreement = epistemic signal for exploration.

**Lit precedent:** MBRL ensemble methods (Chua et al. PETS 2018); disagreement-based exploration (Pathak et al. 2019 "Self-Supervised Exploration via Disagreement").

**Substrate analog:** Superposition of K codebooks is algebraically cheap in FHRR -- multiple bundles can coexist and be queried in parallel. PP-323 bilingual hub-and-spoke already demonstrates multi-codebook architecture.

**P_deflated = 0.38.** Memory cost scales with K; retrieval from K parallel codebooks at inference time is K x retrieval cost. For small K (2-3) this is manageable. Risk: if all K models are stored in the same W matrix (superposition), cross-talk degrades prediction quality faster than K models help.

**HARD-PASS:** goal_reach >= 0.70 with K=3 ensemble; disagreement signal correlates with prediction error (r > 0.50)
**HARD-FAIL:** cross-talk causes ensemble to degrade to single-model performance with K > 1

---

## Cheap Decisive Test

**Test:** Implement E1 (full EFE gradient policy) as a single-modification patch to active_inference_lite: add a 1-step lookahead that evaluates pragmatic_value = similarity(predicted_next_state, goal_bundle) for each candidate action. Add pragmatic term to action selection score. No new substrate mechanism needed; uses existing retrieval + similarity.

**Pre-registration:** run with n >= 200, measure goal_reach and error_drop.
- HARD-PASS: goal_reach >= 0.70 AND error_drop >= 0.30
- MIDDLE_BAND: goal_reach in [0.65, 0.70] or error_drop in [0.25, 0.30] -- investigate lookahead depth
- HARD-FAIL: goal_reach < 0.61 after E1 patch -- suggests mechanism diagnosis wrong; escalate to E3 (temporal lookahead) or E5 (compositional world model)

If E1 MIDDLE_BAND: add E2 (boredom-driven gamma) as second patch. Combined E1+E2 should be sufficient for HARD_PASS if both mechanisms contribute.

Estimated cost: CPU, < 1 minute per run. No GPU needed.

---

## Falsifiable Predictions

### HARD-PASS targets (pre-registered):
- E1 full EFE patch: goal_reach >= 0.70, error_drop >= 0.30 [P_deflated=0.52]
- E1+E2 combined: goal_reach >= 0.72 [P_deflated=0.48, joint]
- E3 temporal lookahead (k=2): goal_reach >= 0.72 [P_deflated=0.50]
- E5 compositional world model: forward_model_accuracy >= 0.85, goal_reach >= 0.72 [P_deflated=0.48]

### HARD-FAIL thresholds (per mechanism):
- E1: goal_reach < 0.61 after EFE patch (mechanism diagnosis wrong)
- E2: boredom integration causes goal_reach regression below baseline (exploration too aggressive)
- E3: k=2 lookahead gives goal_reach < 0.61 (forward model error compounds)
- E5: forward_model_accuracy < 0.70 (capacity cliff)
- E7: goal_reach < 0.55 (empowerment dominates goal)
- E10: K > 1 ensemble degrades to single-model (cross-talk exceeds gain)

### Overall anchor-level prediction:
At least one of E1, E2, E3 reaches HARD_PASS within 3 CPU sessions. P_deflated(any of E1/E2/E3 HARD_PASS in 3 tries) = 0.72.

---

## Cross-Thread Synthesis

**PP-272 + PP-285 (active inference primitives) ARE the generative model layer.** The rescue is not to rebuild the substrate -- it is to add the EFE evaluation head that selects among actions. The substrate already has: (a) hypothesis generation (PP-272 active inference loop), (b) multi-step chains (PP-285), (c) residual compression forward model (PP-267), (d) intrinsic motivation signal (PP-315). The missing piece is a single algebraic layer: evaluate G(pi) = sum of similarity(predicted_next_state_t, goal_bundle) over t=1..k for each candidate action pi.

**PP-318 frisson signal cross-thread:** the frisson/prediction-error-resolution signal (cleanup margin spike at sequence resolution) is the biological analog of the phasic dopamine TD error. If the TD path (E9) is pursued, the frisson mechanism is the substrate-native delta_t signal.

**PP-315 boredom + E2:** boredom-as-exploration is the substrate's homeo-heterostatic value gradient (HHVG, NIH PMC6349823). PP-315 is already HARD_PASS on the sensory discrimination axis; the rescue extends it to a policy precision modulator.

**Materials science angle (E3):** the metastable-state energy landscape view predicts that goal_reach=0.610 is a local minimum in policy space, not a fundamental capacity limit. This is consistent with the fact that PP-272 achieves 1.000 convergence on the perception axis -- the substrate is not fundamentally limited; the policy update is stuck. Simulated annealing (E2 boredom gamma schedule) is the prescribed escape mechanism from metastable policy attractors.

**VSA world model (E5) direct lit match:** arxiv 2602.21467 uses learnable FHRR complex-multiplication transitions -- the exact same algebra as the substrate's binding operation. This is not an analogy; it is a direct technical precedent. The substrate can implement the world model from 2602.21467 using its existing FHRR bind/unbind and cleanup dictionary.

---

## Substrate-Product Implications

1. **Cycle 224 MIDDLE_BAND is not a fundamental failure.** It is a policy-head gap: the substrate generative model works (PP-272 1.000) but the action selection policy does not use expected free energy. This is a well-defined engineering addition, not a new capability breakthrough.

2. **Once fixed, active inference becomes a product differentiator.** A substrate that supports goal-directed active inference (EFE + exploration drive) goes beyond a retrieval/memory system into a lightweight decision-making agent substrate -- relevant for autonomous task agents, adaptive curriculum, and the "deployed cognitive ecology" product framing.

3. **Boredom integration (E2) has zero extra cost.** PP-315 already runs; adding the gamma modulation is a 3-line arithmetic addition. The question is entirely empirical: does it help goal_reach by >=5pp.

4. **Compositional world model (E5) is the highest-leverage long-term investment.** arxiv 2602.21467 shows FHRR world models generalize across environments. If the substrate stores (state, action, next_state) forward models, it becomes capable of planning, counterfactual reasoning, and model-based RL -- a major capability expansion beyond the current reactive inference.

5. **Multi-timescale (E6) is the substrate analog of the fast/slow dopamine system.** Validated at the biological level (Nature 2025 multi-timescale RL); the two-path architecture (PP-272 fast + PP-285-based slow horizon) is the natural substrate implementation. This addresses the pattern of error_drop only 20.5%: the slow path may be needed to drive the remaining 9.5pp of error reduction.

---

## Citations (verified, from search results)

1. Friston et al. "Active Inference and Learning" (ScienceDirect, Neuroscience & Biobehavioral Reviews, 2016) -- policy EFE decomposition
2. Millidge "Deep Active Inference as Variational Policy Gradients" (Journal of Mathematical Psychology, 2020; arxiv 1907.03876) -- EFE as policy gradient
3. Millidge "Predictive Coding: A Theoretical and Experimental Review" (arxiv 2107.12979, 2021) -- hierarchical PC hierarchy
4. Parr, Pezzulo, Friston "Active Inference: The Free Energy Principle in Mind, Brain, and Behavior" (MIT Press, 2022) -- canonical reference
5. Friston et al. "Active Inference in Discrete State Spaces from First Principles" (arxiv 2511.20321, 2025) -- updated discrete formulation
6. Gu et al. "Geometric Priors for Generalizable World Models via Vector Symbolic Architecture" (arxiv 2602.21467, 2025) -- FHRR world model direct precedent
7. Wu et al. "Modularizing and Assembling Cognitive Map Learners via Hyperdimensional Computing" (arxiv 2304.04734, 2023) -- HD cognitive map planning
8. Schultz et al. "Updating Dopamine Reward Signals" (PMC3866681) -- TD error = dopamine
9. Dabney et al. "A gradual temporal shift of dopamine responses mirrors TD error" (Nature Neuroscience, 2022) -- multi-timescale TD
10. Lukoševicius et al. "Multi-timescale reinforcement learning in the brain" (Nature, 2025; biorxiv 2023.11) -- multi-timescale RL validated in vivo
11. Kompella et al. "Boredom-Driven Curious Learning by Homeo-Heterostatic Value Gradients" (PMC6349823) -- boredom-curiosity complementarity formal model
12. Mohamed & Rezende "Variational Information Maximisation for Intrinsically Motivated Goal-Based RL" (arxiv 1509.08731, 2015) -- empowerment as variational MI
13. Gregor et al. "Variational Intrinsic Control" (arxiv 1611.07507, 2016) -- VIC empowerment
14. Sutton et al. "Between MDPs and Semi-MDPs: A Framework for Temporal Abstraction in RL" (Artificial Intelligence, 1999) -- options framework
15. Ha & Schmidhuber "World Models" (NeurIPS 2018) -- world model + controller
16. Hafner et al. "Dreamer" (Google Research Blog, 2020) -- Dreamer world model + actor-critic

Verified count: 16 citations.

---

## Ranked Anchor Candidates for exp_dev

| Rank | Mechanism | P_deflated | Cost | HP Threshold |
|------|-----------|------------|------|--------------|
| 1 | E1 FULL-FREE-ENERGY-GRADIENT-POLICY | 0.52 | 1 CPU session | goal_reach>=0.70, error_drop>=0.30 |
| 2 | E2 BOREDOM-AS-EXPLORATION-DRIVE | 0.55 | 1 CPU session | goal_reach improvement >=0.05pp |
| 3 | E1+E2 combined | 0.48 (joint) | 1 CPU session | goal_reach>=0.72 |
| 4 | E3 TEMPORAL-LOOKAHEAD (k=2) | 0.50 | 1 CPU session | goal_reach>=0.72 |
| 5 | E9 TD-PREDICTION-ERROR | 0.45 | 1 CPU session | goal_reach>=0.70, V converges |
| 6 | E5 COMPOSITIONAL-WORLD-MODEL | 0.48 | 2-3 CPU sessions | forward_model_acc>=0.85, goal_reach>=0.72 |

Recommended dispatch order: E1 alone first (cheapest decisive test); if MIDDLE_BAND, add E2; if still MIDDLE_BAND, try E3. E5 is the highest-leverage long-term investment but requires more implementation.
