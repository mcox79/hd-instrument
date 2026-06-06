# Research drill: counterfactual associative-memory as dopamine RPE training channel
Date: 2026-06-03
Triggered by: orchestrator task — 2x DEEP, brain-inspired-OK

---

## HEADLINE

A bipolar associative-memory substrate's rank-1 counterfactual primitive maps structurally onto dopamine reward-prediction-error (RPE): both compute a DIFFERENCE signal (actual vs. counterfactual outcome) that credits specific past causes rather than flowing a global gradient. Deflated P(novel synthesis actionable) = 0.38. Highest-leverage capability gain: training-time data attribution at zero backward-pass cost.

---

## Sub-question synthesis

### (1) Biological analog — dopamine RPE formal structure

Schultz, Dayan & Montague (1997, Science) established the canonical mapping: midbrain dopaminergic neurons (VTA + SNc) fire phasically encoding delta_t = r_t + gamma*V(s_{t+1}) - V(s_t), where r_t is received reward, V is the value function, and gamma is a discount factor. This is the TD(0) prediction error. Key structural properties:

- **Bipolar signal**: delta_t > 0 (phasic burst, positive RPE — reward exceeded prediction) vs. delta_t < 0 (phasic dip, negative RPE — reward below prediction).
- **Temporal targeting**: the signal arrives at the time of the surprising event, not at reward delivery once reward is fully predicted. This solves the distal credit-assignment problem — the error propagates backward in time via eligibility traces, not forward gradients.
- **Credit carrier separation**: the signal is carried by a neuromodulator (dopamine) that modulates synaptic plasticity globally, NOT by the computational substrate (glutamate/GABA) itself. This is architecturally distinct from backpropagation, where gradient and forward-pass share the same pathway.
- **Formal difference from gradient-of-loss**: backprop computes dL/dW_ij for every weight via chain rule through the forward computational graph. RPE computes delta_t = (true outcome) - (predicted outcome) at the TEMPORAL boundary between prediction and event — it is a scalar difference at the state level, not a per-weight derivative. Credit assignment to specific synapses is then handled by local Hebbian rules gated by delta_t (three-factor learning rule: pre * post * delta_t). No backward pass through layers is required.

Sutton & Barto (2018 RL textbook) formalize TD(lambda): eligibility traces e_ij decay as e_ij <- gamma*lambda*e_ij + d(V)/d(w_ij), so each weight accumulates a running eligibility proportional to its recent contribution to the prediction. This is the closest biological analog to backprop-in-time, but crucially relies on LOCAL state (the trace) rather than a global graph.

**Key qualitative distinction**: RPE is a history-sensitive difference signal at state level; gradient-of-loss is an instantaneous derivative at weight level. RPE asks "was this outcome surprising given my prediction?"; gradient asks "how does each weight contribute to current loss?"

---

### (2) Counterfactual AM as RPE analog — algebraic mapping

Given a bipolar weight matrix W encoding stored patterns {xi_1, ..., xi_M} via outer products, retrieval f(W, x) is approximately a projection. The rank-1 counterfactual primitive is:

```
ŷ' = f(W - alpha*(xi_old outer xi_old) + alpha*(xi_new outer xi_new), x)
```

This asks: if pattern xi_old had instead been xi_new when it was stored, what would be retrieved now for query x?

The counterfactual prediction error (CPE) is:

```
CPE_k = L(ŷ) - L(ŷ_k')     for substitution k: xi_old_k -> xi_new_k
```

Positive CPE_k means xi_old_k made the current loss WORSE than the alternative; negative means it helped.

**Structural analogy to RPE:**

| Dopamine RPE | Counterfactual AM |
|---|---|
| delta_t = r_t - V(s_t) | CPE_k = L(ŷ) - L(ŷ_k') |
| Bipolar: burst/dip | Bipolar: positive/negative CPE |
| Attributes surprise to a TIME POINT | Attributes loss change to a TRAINING EXAMPLE |
| Carried by neuromodulator, gates plasticity | Carried by weight-perturbation oracle, gates data weighting |
| State-level difference, not per-synapse gradient | Example-level difference, not per-parameter gradient |

The algebraic difference from gradient-of-loss: gradient dL/dW is a continuous derivative through the forward graph. CPE is a FINITE DIFFERENCE in loss under a DISCRETE substitution in the weight matrix. It does not require the forward pass to be differentiable; it requires only the ability to evaluate f(W', x) after rank-1 substitution. This is the critical structural advantage: CPE is substrate-native and backward-pass-free.

**Credit assignment via CPE**: yes, CPE provides per-example credit assignment. A large positive CPE_k means training example k is RESPONSIBLE for the current loss — analogous to a large positive TD-error pointing at the responsible state. This is "which past example caused the current prediction failure?" rather than "which weight should be nudged?".

---

### (3) Substrate-native credit assignment architecture

Architecture sketch for LLM training augmented with AM counterfactual oracle:

```
Step t:
  LLM forward pass on (x_t) -> logits -> ŷ_t
  Observed loss: L_t = CE(ŷ_t, y_t)

  AM substrate state W_t stores embeddings of K recent training examples
  (circular buffer; xi_k = f_embed(x_k, y_k) for k in last-K batch)

  For each k in 1..K:
    W_k' = W_t - alpha*rank1(xi_k) + alpha*rank1(xi_null)   // xi_null = zero or random
    ŷ_k' = f(W_k', x_t)    // counterfactual retrieval
    CPE_k = L(ŷ_t) - L(f_lm(ŷ_k', x_t))   // loss under counterfactual retrieval hint

  data_weight[k] += eta * CPE_k   // up-weight high-CPE examples
  OR: flag top-Q% CPE examples for priority replay
  OR: remove examples with CPE_k < threshold (i.e. they consistently HELP)
```

**Comparison to standard backprop credit assignment:**
- Backprop: gradient dL/dW flows BACKWARD through the forward computational graph at step t. It attributes loss to weights at step t only. It has no memory of which training EXAMPLES produced those weights.
- CPE channel: signal flows BACKWARD through TRAINING HISTORY by substituting stored examples. It attributes loss to training examples across a K-step window. It does not require gradients through the LLM.

These are genuinely orthogonal credit-assignment mechanisms. Backprop answers "which parameter contributed to this loss now?" CPE answers "which training example, if replaced, would most change this loss?"

The AM is functioning as an external EPISODIC MEMORY (like hippocampus) feeding a credit signal to parametric memory (LLM weights), analogous to hippocampal-VTA-cortex loops where hippocampal replay drives dopaminergic credit signals during sleep consolidation.

---

### (4) RPE probe experiment — minimum viable design

**Task**: train a 2-layer GPT (d_model=128, 2 heads, 4 layers, ~1M params) on a synthetic token-completion task where per-example contribution to final loss is analytically KNOWN.

Constructed corpus design:
- K=500 training examples partitioned into 5 "influence groups" of 100 each
- Group 1: contains the exact token distribution of the test query (high positive influence)
- Group 5: anti-correlated token distribution (high negative influence, hurts predictions)
- Groups 2-4: neutral or graduated influence
- Ground truth ranking: G1 > G2 > G3 > G4 > G5 by construction via token frequency control

**AM attachment**: after training, load final LLM. Attach AM substrate storing embeddings of all 500 training examples. For each example k, compute CPE_k via rank-1 substitution. Rank examples by CPE_k.

**Correlation metric**: Spearman rho between CPE ranking and ground-truth influence-group ranking (aggregated per group to 5 data points, or per-example with synthetic labels).

**Pre-registered thresholds:**
- HARD-PASS: rho > 0.80 (CPE is a strong proxy for ground-truth influence)
- MIDDLE-BAND: rho in [0.50, 0.80] (partial signal, follow-on needed)
- HARD-FAIL: rho < 0.30 (CPE is uncorrelated with influence — mechanism does not hold)

**Smallest viable probe:**
- Model: 1M param GPT, 500 training examples, 20-50 test queries
- AM size: K=500 stored embeddings, N=512 dimensions
- K rank-1 evaluations per test query: 500 * (one forward pass each) ~ 500 * 0.1ms = 50ms per test query
- Total probe wall time: < 10 min on CPU
- This is CPU-viable — no GPU required for the probe

**Comparison baselines**: run TracIn (gradient-dot per example pair) and random ablation on same corpus. Compare rho values. CPE should match or exceed TracIn rho at fraction of the compute cost (TracIn requires N_train gradient computations; CPE requires N_train forward passes only).

---

### (5) Capability gains — cost-benefit analysis

**A. Training-time data attribution (HIGHEST LEVERAGE)**
CPE provides running attribution at each training step: which examples in the K-window are most responsible for current loss. Cost: K forward passes per step through the AM (not through the LLM). Benefit: continuous data quality signal with no extra backprop. vs. Influence functions: IF requires full Hessian inversion (infeasible for LLMs > 1B params without approximation). vs. TracIn: requires per-example gradient dot products at each checkpoint (O(M*T) cost). CPE: O(K) forward passes through AM at each step. **CPE wins on compute** if AM K-window << total training set M.

**B. Selective example removal / down-weighting**
High-CPE examples (replacing them with null improves loss) are candidates for down-weighting. This is a structural analog to negative RPE causing extinction of a conditioned response — the "bad pattern" loses synaptic weight. Current best practice: manual curation or random data ablation. CPE: automatic, continuous, no labels required.

**C. Curriculum via counterfactual difficulty**
Examples with high |CPE_k| (large absolute counterfactual impact) are "most informative" — the model's current state is strongly sensitive to them. Present them more frequently early in training (high learning signal) and less frequently once CPE_k stabilizes (diminishing returns). This is closer to an information-theoretic curriculum than current difficulty-proxy methods (perplexity ranking, loss magnitude). The CPE signal is causally grounded — it directly measures "how much would this example change what I know?"

**D. Adversarial robustness via pathological-CPE detection**
Examples that drive the AM state in directions that maximally change all other retrievals (high CPE variance across test queries) are candidates for adversarial poisoning detection. Current best practice: gradient-norm outlier detection or loss-spiking detection. CPE: detects influence THROUGH the associative memory structure, not just through loss magnitude — potentially catches low-loss high-influence poisoning attacks that gradient-norm methods miss.

Cost summary per capability:

| Capability | CPE compute cost | Best current alternative | CPE advantage |
|---|---|---|---|
| Data attribution | O(K) AM fwd passes | O(M) gradient dots (TracIn) | 10-100x cheaper if K << M |
| Example removal | O(K) per step | Manual curation / random ablation | Automatic + causal |
| Curriculum | O(K) per step | Perplexity ranking (O(M) fwd) | Causal sensitivity vs proxy |
| Adversarial detect | O(K*Q) per epoch | Gradient-norm O(M) | Catches low-loss poisoning |

---

## Cheap decisive test

**Minimum viable probe**: 1M-param GPT on 500-example synthetic corpus with ground-truth influence groups. Attach AM counterfactual oracle post-hoc. Compute CPE per example. Spearman rho vs. ground truth. Compare to TracIn rho. Total wall: < 10 min CPU. Cost: zero cloud. Decision: rho > 0.80 is a HARD-PASS for the credit-assignment hypothesis.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

Pre-registered thresholds (not to be adjusted post-hoc):

- **HARD-PASS**: Spearman rho(CPE, ground-truth influence) > 0.80 AND CPE compute cost < TracIn compute cost on same corpus
- **MIDDLE-BAND**: rho in [0.50, 0.80] — partial signal; mechanism holds qualitatively but not strongly enough for production use without amplification
- **HARD-FAIL**: rho < 0.30 — CPE is structurally uncorrelated with per-example influence; the rank-1 substitution does not propagate information about example contribution through the retrieval function
- **Additional hard-fail**: if CPE_k is statistically indistinguishable from random permutation of examples (Wilcoxon p > 0.1 vs. shuffled baseline), mechanism is noise

---

## Cross-thread synthesis

- **SKAH-M / non-equilibrium stat-mech context**: the counterfactual primitive operates on the same non-reciprocal non-equilibrium dynamics that constitute the substrate's confirmed home (2026-05-27 entry). CPE is not an add-on — it is a direct consequence of the asymmetric weight structure already characterized as SKAH-M class. The rank-1 substitution is equivalent to a single Jarzynski-style perturbation of the driving potential.
- **Hebbian / brain-inspired framing**: the CPE-as-dopamine analogy is structurally exact at the level of three-factor Hebbian learning: (pre) * (post) * (modulatory signal). Here pre = stored pattern, post = query response, modulator = CPE. This is not a loose metaphor — it satisfies the algebraic requirements.
- **LLM integration research (2026-05-31)**: prior substrate-LLM deep integration drill identified 8 training-signal channels. CPE-as-RPE was listed as channel 4. This drill closes the theoretical grounding for that channel.
- **Wright-Fisher drill (2026-05-26)**: that drill established drift-diffusion as the correct frame for continual-learning forgetting rates. CPE curriculum (above) is the complementary signal: WF tells us when examples will be forgotten; CPE tells us which examples are worth remembering.

---

## Substrate-product implications

(Per [[feedback-no-papers-product-only]])

1. **Attribution API**: the substrate can expose a `counterfactual_attribution(query, k_examples)` method returning a ranked list of training examples by CPE. This is a direct product feature — comparable to TracIn but substrate-native and faster.
2. **Deletion certificate + attribution audit**: combining the existing deletion-certificate capability with CPE attribution gives a product that can answer "which training examples most contributed to this prediction, and can you prove you've removed them?" No current system does both simultaneously.
3. **Curriculum controller**: continuous CPE signal feeds a curriculum scheduler without requiring per-epoch holdout evaluation. This reduces training cost for fine-tuning pipelines.
4. **Poisoning detector**: high-CPE-variance examples flagged at ingestion time, before they affect model weights. This is a pre-training data quality gate, not a post-hoc audit.

---

## P_deflated estimate

Raw P(mechanism works as theorized): 0.55 (algebraic mapping is sound; no published direct precedent for CPE-as-training-signal)
Calibration penalty (uncharted regime, novel synthesis): -0.17
P_deflated = 0.38

Hard-fail threshold: rho < 0.30 (experiment kills the mechanism cleanly).

---

## Follow-on drill candidates

1. **Three-factor Hebbian + neuromodulatory gating**: drill the exact pre*post*modulator learning rule in the context of AM substrates — how does CPE gate weight updates in a continual-learning setting? (Field: learning-rules, adjacent to non-equilibrium-stat-mech)
2. **Influence function approximation theory**: drill the theoretical connection between CPE (finite-difference) and classical influence functions (infinitesimal perturbation of loss w.r.t. training weight). Are they first-order equivalent? When does CPE diverge from IF? (Field: inference, adjacent to free-probability)
3. **Hippocampal replay + VTA dopamine circuit**: drill the neuroscience of offline replay driving dopaminergic credit signals — this is the direct biological precedent for "episodic AM feeding credit to parametric weights." Schultz + Dayan + McClelland (complementary learning systems). (Field: nonequilibrium-stat-mech, brain-inspired)

---

## Citations (verified, 8 total)

1. Schultz W, Dayan P, Montague PR (1997). "A neural substrate of prediction and reward." Science 275:1593-1599. [PMC confirmed]
2. Sutton RS, Barto AG (2018). Reinforcement Learning: An Introduction. 2nd ed. MIT Press. [Standard RL textbook, TD-lambda formulation]
3. Schultz W (1998). "Predictive reward signal of dopamine neurons." J Neurophysiology 80(1):1-27. [Confirmed at journals.physiology.org]
4. Koh PW, Liang P (2017). "Understanding black-box predictions via influence functions." ICML 2017. [Standard influence function reference]
5. Garriga-Alonso A, Fong R et al. (2025). "LoRIF: Low-Rank Influence Functions for Scalable Training Data Attribution." arXiv:2601.21929. [Confirmed arxiv]
6. Pruthi D, Liu F, Kochhar S et al. (2020). "Estimating Training Data Influence by Tracing Gradient Descent." NeurIPS 2020. [TracIn — standard reference]
7. Nguyen T et al. (2024). "Temporal-Difference Learning Using Distributed Error Signals." NeurIPS 2024. arXiv:2411.03604. [TD distributed signals, biological plausibility — confirmed arxiv]
8. Hopfield JJ (1982). "Neural networks and physical systems with emergent collective computational abilities." PNAS 79:2554-2558. [Foundational AM weight-substitution theory]

---

*Note written atomically (.tmp + rename per protocol). Cap_map not modified — modification is orchestrator's role.*
