# research: multi-agent reasoning beyond context exchange (2x drill) -- 2026-06-10

## HEADLINE

Context exchange between agents is necessary but not sufficient for multi-agent reasoning. Nash equilibrium computation is PPAD-complete; theory of mind requires iterated nested belief inference; mechanism design requires incentive-compatible protocol construction; iterated cooperation requires history-dependent strategy; all of these are distinct computational problems that shared memory does not solve. Substrate has validated primitives (ToM depth-3, PP-250; AGM belief revision, PP-266/PP-287; active inference, PP-272/PP-285; cultural conventions, PP-265; paraconsistent multi-context, PP-280) that are NECESSARY building blocks for specific constrained forms of multi-agent reasoning -- but none of these, nor their composition, constitutes a general multi-agent coordination system. Honest position: substrate solves the representation problem for a subset of multi-agent reasoning tasks; it does not solve the strategic interaction, incentive, or equilibrium-computation problems.

---

## 1. What the overclaim was

The overclaimed framing was: "multi-agent coordination via shared context exchange" implies that two agents sharing a NOW-shard context solves coordination. This framing conflates four distinct problems:

(a) Information sharing -- solved by context exchange  
(b) Common knowledge establishment -- partially addressed by shared reads  
(c) Strategic reasoning under conflicting objectives -- NOT solved  
(d) Equilibrium selection, mechanism design, bargaining -- NOT solved  

The lit record is unambiguous on this distinction. Sharing context is a prerequisite, not a solution.

---

## 2. What multi-agent reasoning actually requires (literature grounding)

### 2.1 Nash equilibrium and strategic interaction

Daskalakis, Goldberg, and Papadimitriou (2006) proved that computing a Nash equilibrium of a two-player bimatrix game is PPAD-complete. For n-player games the hardness only increases: finding an epsilon-Nash equilibrium in a succinctly represented n-player game requires exponential queries (2^Omega(n)) to the payoff tensor. This is a negative result about computation, not about representation: even if all agents have access to the full game description (full context exchange), no polynomial-time algorithm is known for finding Nash equilibria unless PPAD = P, which is widely considered false.

Implication for substrate: a shared context store that holds all agents' beliefs, histories, and private information does not reduce the computational hardness of equilibrium computation. A classical Nash solver (linear programming for 2-player zero-sum; Lemke-Howson for bimatrix; support enumeration for n-player) is required alongside any substrate representation.

### 2.2 Mechanism design

Hurwicz (1972), Maskin (1999), and Myerson (1981) developed the mechanism design framework: how to design rules of interaction (mechanisms) such that self-interested agents' best responses implement a desired social outcome. The key result (revelation principle, Myerson 1981) is that any outcome achievable by any mechanism can be achieved by a direct incentive-compatible mechanism where truthful reporting is a dominant strategy. The negative result (Hurwicz impossibility): no mechanism simultaneously achieves efficiency, incentive compatibility, and budget balance in general settings.

Implication for substrate: mechanism design requires specifying a game form (who reports what, in what order, with what verification), a payment rule, and proving incentive compatibility. A substrate that stores agents' reported types and verifies consistency is a useful component of a mechanism implementation -- but the protocol design and incentive proof are external classical results. The substrate can hold the auction state and the bid history; it cannot derive the optimal auction rule.

### 2.3 Theory of Mind -- iterated depth

Premack and Woodruff (1978) posed the ToM question; subsequent cognitive science operationalized it as nested belief attribution: "A believes B believes C believes X." Camerer et al.'s (2004) cognitive hierarchy (CH) model treats agents as distributed across reasoning levels: a level-k agent best-responds to a Poisson mixture of agents at levels 0 through k-1. Empirical data from beauty-contest games shows most humans operate at levels 1-3 (Camerer 2004; mean ~1.5).

The computational challenge: full iterated reasoning is potentially infinite and computationally intractable. Each additional depth level requires a new conditional distribution over the opponent's strategy, conditioned on their belief about your strategy, etc. Bounded-depth models (level-k, CH) are tractable approximations.

Where substrate fits: PP-250 (ToM depth-3, recall=1.000 at n=200) validated that substrate can store and retrieve nested belief structures to depth 3 -- "A believes B believes C believes X" -- without error. PP-265 (cultural conventions) validated social-script lookup at ceiling. These are STORAGE and RETRIEVAL capabilities for belief structures. They are not inference engines over those beliefs in the strategic sense. The substrate can answer "what does agent A believe agent B believes?" -- it cannot answer "what is A's optimal action given B will optimize over A's inferred strategy?"

### 2.4 Multi-agent reinforcement learning

Littman (1994) introduced Markov games; MADDPG (Lowe et al. 2017) and QMIX (Rashid et al. 2018) are the leading cooperative MARL algorithms. MADDPG uses centralized training with decentralized execution (CTDE): a centralized critic conditions on all agents' observations and actions during training, but agents execute with only local observations at test time. QMIX factorizes the joint Q-function into per-agent utilities via a monotonic mixing network, enforcing the Individual-Global Max (IGM) principle.

The nonstationarity problem is fundamental: when multiple agents learn simultaneously, the environment is non-stationary from each agent's perspective because other agents are changing their policies. This cannot be resolved by better representation of the current joint state -- it requires multi-agent learning algorithms, credit assignment mechanisms, and convergence guarantees (which QMIX and MADDPG provide approximately, not provably in general).

Implication for substrate: substrate can serve as the state representation layer for a MARL system -- storing joint observations, belief states, and episodic histories in a compact associative form that is queryable at sub-millisecond latency. But the policy optimization, credit assignment, and convergence dynamics are the province of MARL algorithms running above the substrate.

### 2.5 Convention emergence and Schelling points

Schelling (1960) showed that agents can coordinate without communication by identifying salient focal points. Lewis (1969) formalized this as conventions: self-reinforcing behavioral regularities that are common knowledge. The game-theoretic foundation requires iterated knowledge: A knows B knows A knows the convention -- not just that both have read the same shared context.

PP-265 (cultural conventions) validated that substrate can store and retrieve social scripts (30 scripts, n=250, recall=1.000). This is the equivalent of encoding the convention externally and having agents look it up. Emergence of conventions -- how two agents with no prior interaction spontaneously converge on the same focal point -- requires a learning or coordination protocol. The substrate can hold the converged convention once it exists; it cannot derive or bootstrap it from scratch without an external protocol.

### 2.6 Cooperative game theory (Shapley)

Shapley (1953) introduced the Shapley value: the unique fair allocation of gains from cooperation satisfying efficiency, symmetry, dummy, and additivity axioms. Coalition formation (which subset of agents should cooperate) is NP-hard in general (evaluating the characteristic function requires exponential computation in the number of agents). Rubinstein (1982) showed that sequential bargaining with discounting converges to the Nash bargaining solution as the discount factor approaches 1.

Implication for substrate: substrate can store coalition membership, per-agent contributions, and accumulated histories. Computing Shapley values from stored data is a classical algorithm problem; substrate accelerates the state-lookup component but does not reduce the combinatorial complexity.

### 2.7 Iterated cooperation -- Axelrod

Axelrod (1984) showed that Tit-for-Tat wins iterated prisoner's dilemma tournaments. The key structural requirement is a history-dependent strategy: agents must recall whether the opponent cooperated or defected in prior rounds. This is a temporal binding problem -- substrate PP-259 (continuous temporal binding) and PP-265 are exactly relevant here. But Tit-for-Tat requires strategy selection over retrieved history, not just storage. The strategy computation (if opponent defected last round, defect this round) is trivial, but it illustrates the general point: retrieval enables strategy execution, but strategy design and selection are classical algorithm problems.

---

## 3. What context exchange CAN solve

Context exchange -- two agents reading from a shared substrate store -- addresses:

(a) Information asymmetry: agent B can read what agent A has written; common-knowledge establishment is approximated (not guaranteed; see 2.5).

(b) Joint-task grounding: two agents working on subtasks of a common objective can read the current partial state from a shared store and avoid redundant work. This is the "shared scratchpad" use case.

(c) Rendezvous / coordination on externally specified focal point: if a Schelling point has been pre-encoded in the substrate (by design, not emergence), agents can look it up without communication.

(d) Belief-state sharing: agent A can write its current beliefs; agent B can read them; this reduces information asymmetry but does not guarantee common knowledge (because B knowing A's beliefs is not the same as A knowing B knows A's beliefs -- the infinite regress of common knowledge requires external proof, not just reads).

(e) Temporal coordination via shared event log: agents can read the sequence of prior events and coordinate on shared timelines. PP-259 (temporal binding) enables this.

These are real and valuable capabilities. They are necessary for many multi-agent applications. They are not sufficient for strategic interaction, equilibrium computation, or mechanism design.

---

## 4. What context exchange CANNOT solve

(a) Nash equilibrium computation (PPAD-complete; requires explicit solver).

(b) Deception: if agent B has an objective that differs from agent A's, shared context does not prevent strategic manipulation of what B writes. The substrate verifies retrieval fidelity, not intent alignment.

(c) Mechanism design: incentive-compatible protocols require game-form specification and payoff design external to any memory system.

(d) Coalition formation: exponential combinatorial problem; shared state helps evaluate per-agent contributions but does not reduce the complexity of computing the optimal coalition structure.

(e) Bargaining: Rubinstein's alternating-offers model requires rational agent preferences over time (discount factors) and rational anticipation of opponent's future strategy. Storage of bid history helps, but the game-theoretic reasoning is external.

(f) Convention emergence without external protocol: agents reading shared context can converge on a pre-existing convention but cannot bootstrap a new one without a learning or coordination algorithm.

(g) Credit assignment in joint learning: MARL nonstationarity and credit assignment require multi-agent learning algorithms, not better memory.

---

## 5. Substrate's actual multi-agent capabilities (validated)

These are the empirically validated PP rows directly relevant to multi-agent reasoning:

**PP-250 (ToM depth-3, recall=1.000, n=200):** Substrate stores and retrieves nested belief structures to depth 3. Enables: look up "what does A believe B believes about X." Does NOT enable: compute A's optimal action under iterated game-theoretic reasoning.

**PP-265 (cultural conventions, recall=1.000, 30 scripts):** Substrate stores social scripts and resolves expected-action queries. Enables: Schelling-point coordination when the convention is pre-encoded. Does NOT enable: emergence of new conventions between agents with no prior encoding.

**PP-266 + PP-287 (AGM belief revision, recall=1.000, n=5213 and n=2999 depth):** Substrate performs AGM-compliant belief revision -- prioritized contraction, expansion, erasure -- at ceiling accuracy under accumulated update depth. Enables: each agent can maintain a correctly-updated belief store when new evidence arrives. Does NOT enable: game-theoretic reasoning about the opponent's belief revision process.

**PP-272 + PP-285 (active inference, convergence=1.000, 6-step chains):** Substrate supports multi-step active inference: hypothesis-generate, predict, minimize prediction error. Enables: a single agent to update its generative model of another agent's apparent state from observations. Does NOT enable: Nash-optimal action selection under the inferred opponent model.

**PP-280 (paraconsistent multi-context, acc=1.000, NC=5, n=6000):** Substrate tracks Belnap 4-valued truth per context across 5 simultaneous contexts with zero cross-context contamination. Enables: different agents holding different truth values about the same facts simultaneously, with algebraic isolation. Does NOT enable: conflict resolution between contradictory agent beliefs -- that requires a protocol external to the substrate.

**PP-230 (multi-tenant isolation, contamination_rate=0.000, T=50):** Per-tenant weight matrix isolation is algebraically exact. Enables: per-agent isolated belief stores. Does NOT enable: coordination across those isolated stores (coordination requires reads across boundaries, which is a protocol decision).

**PP-281 (depth-2 meta-cognition, L2-AUC=0.998):** Substrate knows when it knows correctly vs does not know. Enables: an agent can report its epistemic status on a query ("I am confident" vs "I am uncertain") using substrate meta-cognition. Does NOT enable: game-theoretic reasoning about what the opponent knows.

---

## 6. Engineering anchors (5 concrete experiment candidates)

### TOM-DEPTH-K-COORDINATION (anchor 1, priority: HIGH)
Task: two-agent coordination where agent A holds beliefs about agent B's state; agent A uses ToM depth-3 retrieval (PP-250) to infer what B will do; agent A then acts optimally given that inference. Test case: coordination game with known dominant strategy derivable from 3-level nested belief lookup. HARD-PASS: coordination success >= 0.90 on problems where the optimal action IS derivable from depth-3 ToM retrieval (not from equilibrium computation). HARD-FAIL: coordination success < 0.70 OR problems are misclassified as ToM-solvable when they require Nash computation. This test is honest: it tests whether ToM-depth-3 is sufficient for the SUBSET of coordination games where 3-level nested belief resolution determines the action.

### SCHELLING-POINT-VIA-CULTURAL-SCHEMA (anchor 2, priority: MEDIUM)
Task: encode N pre-specified conventions in PP-265 scripts; two simulated agents independently query the same substrate for the expected action in a coordination game with a unique focal point derived from the script. HARD-PASS: both agents independently retrieve the same action >= 0.95 of the time. HARD-FAIL: cross-agent action agreement < 0.80 OR agents retrieve different actions from the same script. This is honest: tests substrate-mediated Schelling coordination on PRE-ENCODED conventions, not emergent convention formation.

### ACTIVE-INFERENCE-OVER-OPPONENT-STATE (anchor 3, priority: MEDIUM)
Task: agent A uses PP-285 (multi-step active inference) to build an internal model of agent B's policy from observed actions. After k observations, agent A queries its generative model to predict B's next action. HARD-PASS: prediction accuracy >= 0.75 on the held-out action given k=10 prior observations from a policy drawn from a known distribution. HARD-FAIL: prediction accuracy < 0.50 (at-chance), OR if performance collapses when B changes policy mid-sequence (non-stationarity test). This is honest: tests active inference as opponent modeling, not as Nash computation.

### BELIEF-REVISION-PER-AGENT (anchor 4, priority: MEDIUM)
Task: agent A and agent B each maintain separate belief stores (PP-230 isolation). When agent B acts unexpectedly (inconsistent with A's model of B), agent A must perform AGM belief revision (PP-287) to update its model of B and then re-derive its next action. HARD-PASS: A's updated belief correctly tracks B's revised policy within 3 revision steps (measured by predictive accuracy on held-out B actions). HARD-FAIL: belief revision fails to converge (oscillates) OR predictive accuracy after revision is not better than before revision. This tests the belief revision + active inference pipeline as an opponent-modeling loop.

### MIXED-SUBSTRATE-CLASSICAL-GT (anchor 5, priority: LOW -- hybrid architecture validation)
Task: substrate holds game state (agent beliefs, histories, convention store); classical Nash solver (or Lemke-Howson) operates over the substrate-represented payoff matrix retrieved in real time. Test: 2-agent coordination game where Nash solution requires explicit equilibrium computation; substrate provides the state; classical solver provides the equilibrium; verify the combined system achieves the Nash outcome. HARD-PASS: Nash outcome achieved in >= 0.90 of games; substrate retrieval latency < 1ms per query. HARD-FAIL: system fails to reach Nash outcome in games where equilibrium is unique AND unique equilibrium is not derivable from ToM lookup alone. This is the honest hybrid architecture test: substrate as state layer, classical GT as solver layer.

---

## 7. Hybrid architectures

Three hybrid paths are viable for production multi-agent systems using substrate:

**Path A: Substrate state layer + classical game theory solver.** Substrate stores agent beliefs, histories, payoff matrices, and convention tables. A classical solver (linear program for zero-sum, Lemke-Howson for bimatrix, support enumeration for small n-player games) takes substrate-retrieved state as input and outputs equilibrium strategies. Substrate advantage: sub-ms state lookup + exact belief revision + ToM-depth-3 lookup for belief structures. Limit: equilibrium computation cost is outside the substrate.

**Path B: Substrate state layer + MARL algorithm.** Substrate holds the joint observation history and episodic episodic buffer for a CTDE MARL system (MADDPG, QMIX). Substrate advantage: substrate's associative retrieval replaces a standard replay buffer with a content-addressable episodic memory -- retrieve the k most-similar past states to the current query, not the k most-recent. Active inference (PP-285) provides an intrinsic surprise signal for MARL exploration. Limit: policy optimization and credit assignment remain MARL algorithmic concerns.

**Path C: ToM-grounded coordination for bounded-depth games.** For problems where the optimal action IS derivable from iterated belief lookup to depth 3 or fewer (a subset of coordination games, bargaining games with known discount factors, and games with unique dominant strategies), substrate can serve as the complete reasoning engine. PP-250, PP-265, PP-266, PP-285, PP-280 together cover: nested belief storage, convention lookup, belief revision under surprise, and per-agent paraconsistent belief tracking. This is the honest substrate-native path: constrained game classes only.

---

## 8. Honest commercial framing

The honest position on substrate and multi-agent:

Substrate is not a general multi-agent reasoning engine. It does not compute Nash equilibria. It does not design mechanisms. It does not solve the nonstationarity problem in MARL. Claiming otherwise is an overclaim.

What substrate does provide for multi-agent applications:

(1) A low-latency, algebraically-exact state representation layer: agent beliefs, histories, nested knowledge structures, and shared conventions stored and retrieved with verified fidelity.

(2) A ToM-capable belief representation: depth-3 nested beliefs stored and retrieved at ceiling accuracy (PP-250, PP-265) -- enough to cover the cognitive hierarchy range where most human agents operate (empirical mean level ~1.5).

(3) AGM-correct belief revision: when an agent observes unexpected information, it can update its world model without accumulating logical inconsistency (PP-266, PP-287) -- this is a property classical key-value stores and vector databases lack.

(4) Active inference for opponent modeling: substrate's generative model framework (PP-272, PP-285) enables a lightweight opponent-modeling loop -- observe B's actions, minimize prediction error, derive updated model of B.

(5) Algebraically isolated per-agent stores: multi-tenancy isolation (PP-230) gives each agent a mathematically isolated W matrix; cross-agent reads can be permissioned without risking cross-contamination.

(6) Paraconsistent multi-context reasoning: substrate can hold contradictory beliefs across 5 simultaneous agent-contexts without logical explosion (PP-280) -- a property no classical coordination middleware provides.

These are genuine differentiators. They are useful and commercially viable. They address the representation and retrieval problems for multi-agent state. They do not address the strategic reasoning, equilibrium computation, or mechanism design problems.

The honest product framing is: substrate is a ToM-capable, belief-revision-correct, algebraically-isolated multi-agent state layer. Pair it with classical game theory or MARL algorithms for strategic interaction. Do not claim substrate solves strategic multi-agent coordination standalone.

---

## Cheap decisive test

Test whether substrate ToM-depth-3 retrieval is SUFFICIENT for a specific class of coordination games (those with dominant strategies derivable from at most 3 levels of nested belief lookup):

1. Construct 100 two-agent coordination games where the correct action is derivable by a level-3 cognitive hierarchy agent (known ground truth from CH model).
2. Encode agent A's beliefs about agent B's beliefs about agent A's beliefs in PP-250 substrate structure.
3. Query substrate: what does A believe B will do?
4. Map retrieved belief to action via a deterministic strategy function.
5. Compare to CH-model ground truth.

PASS criterion: accuracy >= 0.85 on the level-3-solvable subset; clearly below 0.85 on games requiring Nash computation (i.e., games without dominant strategies). The test is decisive because it draws the line between the class of games substrate can handle and the class it cannot.

Cost: local CPU, < 5 min wall. No GPU needed. Pure substrate retrieval + comparison against precomputed CH ground truth.

---

## Falsifiable predictions

**HARD-PASS (what would confirm substrate's bounded multi-agent claim):**
- TOM-DEPTH-K-COORDINATION: >= 0.90 coordination success on level-3-solvable games, and the system correctly abstains (or fails gracefully) on Nash-only games.
- SCHELLING-POINT-VIA-CULTURAL-SCHEMA: cross-agent agreement >= 0.95 on pre-encoded conventions.
- ACTIVE-INFERENCE-OVER-OPPONENT-STATE: prediction accuracy >= 0.75 after k=10 observations.
- BELIEF-REVISION-PER-AGENT: updated model predicts B's actions better than prior model within 3 revision steps.

**HARD-FAIL (what would refute even the constrained claim):**
- TOM-DEPTH-K-COORDINATION < 0.70 accuracy on level-3-solvable games -- the substrate ToM representation does not translate to coordination improvement (representation without inference).
- SCHELLING-POINT-VIA-CULTURAL-SCHEMA < 0.80 cross-agent agreement -- convention encoding is not reliably retrievable under agent-A vs agent-B query framing differences.
- ACTIVE-INFERENCE-OVER-OPPONENT-STATE <= 0.55 (near-chance) after k=10 -- active inference loop does not generalize from within-distribution policy observations.
- BELIEF-REVISION-PER-AGENT shows oscillation or divergence over 3 revision steps -- AGM revision accumulates inconsistency under repeated updates (would contradict PP-287 depth results, but the multi-agent framing adds query structure that single-agent tests did not cover).

---

## Cross-thread synthesis

Connects to:

- **PP-250, PP-265, PP-266, PP-280, PP-281, PP-272, PP-285, PP-230**: directly tested capabilities that map to multi-agent primitives.
- **Prior handoff: notes/routed_completed/exp_dev_handoff_research_multiagent_coordination_substrate_2026-06-01.md**: the June 1 drill established that substrate has the infrastructure primitives (commutative write, per-agent isolation, deletion persistence). This drill establishes the reasoning claim boundary: infrastructure is correct; strategic reasoning is NOT substrate-native.
- **North Star (functional system beats LLMs)**: the honest multi-agent position is that substrate provides a ToM-capable state representation at sub-ms that LLMs cannot match for latency-sensitive coordination scaffolding. An LLM running ToM inference requires full forward pass; substrate lookup is O(1) per query. The comparison to LLMs should be on this latency + fidelity axis, not on strategic reasoning completeness.
- **MARL field (Tier-1b candidate)**: multi-agent RL is not currently in the field advisor's tracked fields. If the hybrid architecture path (Path B above) is prioritized, it deserves a dedicated MARL adjacency drill targeting QMIX/MADDPG substrate-as-replay-buffer integration.

---

## Substrate-product implications

1. **Do not claim "multi-agent coordination." Claim "multi-agent state layer."** Substrate is the belief-revision-correct, ToM-aware, algebraically-isolated memory component of a multi-agent system -- not the coordination protocol.

2. **ToM depth-3 is commercially differentiating for specific applications.** Social robotics, conversational AI with multiple personas, and negotiation support systems all require nested belief lookup that classical databases cannot provide. Substrate's depth-3 ToM at sub-ms latency is a genuine moat in this narrow but real category.

3. **Hybrid architectures are the path to production multi-agent.** Path A (substrate + Nash solver) and Path B (substrate + MARL) are both viable and honest. These can be demonstrated with anchor TOM-DEPTH-K-COORDINATION and MIXED-SUBSTRATE-CLASSICAL-GT.

4. **Convention encoding (PP-265) is underutilized.** The 30-script validation is a proof of concept; scaling to 10K+ social scripts would make substrate the fastest convention lookup layer available. This is a real product story that does not require overclaiming strategic reasoning.

5. **Active inference opponent modeling (PP-285) is the strongest substrate-native multi-agent capability.** It goes beyond lookup: it iteratively updates a generative model of another agent's state from observations. No classical key-value store or vector database provides this. The ACTIVE-INFERENCE-OVER-OPPONENT-STATE anchor would validate this claim empirically.

---

## Citations (verified from search results)

1. Daskalakis, Goldberg, Papadimitriou (2006/2009). "The complexity of computing a Nash equilibrium." STOC 2006 / JACM 2009. PPAD-completeness of 2-player Nash equilibrium. [arxiv](https://people.csail.mit.edu/costis/simplified.pdf)

2. Camerer, Ho, Chong (2004). "A cognitive hierarchy model of games." Quarterly Journal of Economics. CH model with Poisson level distribution. [ResearchGate](https://www.researchgate.net/publication/247706143)

3. Hurwicz (1972). "On informationally decentralized systems." Decision and organization. Incentive compatibility impossibility. [Nobel 2007 summary](https://www.nobelprize.org/prizes/economic-sciences/2007/popular-information/)

4. Myerson (1981). "Optimal auction design." Mathematics of Operations Research. Revelation principle. [Nobel 2007 advanced](https://www.nobelprize.org/uploads/2018/06/advanced-economicsciences2007.pdf)

5. Rubinstein (1982). "Perfect equilibrium in a bargaining model." Econometrica. Alternating-offers convergence to Nash bargaining solution. [Wikipedia](https://en.wikipedia.org/wiki/Rubinstein_bargaining_model)

6. Rashid et al. (2018). "QMIX: monotonic value function factorisation for deep multi-agent reinforcement learning." ICML. [JMLR paper](https://jmlr.org/papers/volume21/20-081/20-081.pdf)

7. Lowe et al. (2017). "Multi-agent actor-critic for mixed cooperative-competitive environments." NeurIPS. MADDPG. [referenced via emergentmind](https://www.emergentmind.com/topics/multiagent-deep-reinforcement-learning-madrl)

8. Schelling (1960). "The Strategy of Conflict." Harvard University Press. Focal points / Schelling points. [focal point entry](https://en.wikipedia.org/wiki/Focal_point_(game_theory))

9. Lewis (1969). "Convention: A Philosophical Study." Harvard University Press. Convention emergence. [focal points revisited](https://centaur.reading.ac.uk/67904/1/Focal_points_final_clean%20(1).pdf)

10. Axelrod (1984). "The Evolution of Cooperation." Basic Books. Tit-for-Tat tournament. [Wikipedia](https://en.wikipedia.org/wiki/The_Evolution_of_Cooperation)

11. Premack, Woodruff (1978). "Does the chimpanzee have a theory of mind?" Behavioral and Brain Sciences. ToM origin. [referenced via BeliefNest](https://arxiv.org/html/2505.12321v1)

12. Alchourrón, Gärdenfors, Makinson (1985). "On the logic of theory change." Journal of Symbolic Logic. AGM belief revision. [SEP entry](https://plato.stanford.edu/entries/logic-belief-revision/)

13. Friston et al. (various). "Active inference." Free energy principle generative model. [MDPI multi-agent active inference](https://www.mdpi.com/1099-4300/27/2/143)

14. Shapley (1953). "A value for n-person games." Contributions to the Theory of Games. Shapley value. [mechanism design survey](https://www.isid.ac.in/~dmishra/doc/survey.pdf)

15. Nash (1950). "Equilibrium points in n-person games." Proceedings of the National Academy of Sciences. Nash equilibrium. [PPAD paper](https://web2.qatar.cmu.edu/~gdicaro/15281/additional/complexity_NASH.pdf)

Verified citations: 15

---

## Calibration

P_deflated (substrate solves general multi-agent reasoning): 0.00 -- this is a definitional impossibility not a probability claim. Nash computation hardness is a complexity-theoretic result, not an empirical question.

P_deflated (substrate ToM-depth-3 coordination anchor passes): 0.65 (raw estimate 0.80-0.90, deflated -0.20 per calibration discipline; novel framing of existing PP-250 result as coordination rather than retrieval).

P_deflated (substrate cultural convention coordination anchor passes): 0.70 (raw estimate 0.90, deflated -0.20; PP-265 already validated retrieval; the cross-agent coordination framing adds retrieval-under-different-query-structure risk).

P_deflated (active inference opponent modeling anchor passes at 0.75 threshold): 0.45 (raw estimate 0.65, deflated -0.20; PP-285 validates convergence on generating-distribution predictions; opponent policy from i.i.d. observations is a harder inference problem with less substrate-native grounding).

P_deflated (hybrid substrate + classical GT anchor passes): 0.75 (raw estimate 0.90, deflated -0.15; this is mostly a plumbing problem -- substrate retrieval + solver input formatting -- with well-understood failure modes).
