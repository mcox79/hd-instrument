# Research drill: Frustration-resolution mechanisms (3x depth) -- 2026-06-10

## HEADLINE

Spin-glass frustration at the 4% irreducible floor is NOT inherently irreducible: resolution
mechanisms from six independent fields (biology, neuroscience, materials science, LLM
theory, control theory, and substrate-native math) all converge on the same structural
insight -- frustration is resolved by META-LEVEL operations that break ergodicity,
change the framing of the conflict, or defer resolution to a different timescale. The
substrate currently applies only BG-analog (Boltzmann-gradient), which is a SAME-LEVEL
operation and cannot escape the frustration basin. P_deflated for any single mechanism
= 0.28-0.42; for a two-mechanism cascade = 0.48 (calibration penalty applied; cap at 0.50
for novel synthesis).

---

## BACKGROUND: The 4% irreducible problem

### The BG-analog result

The substrate's Boltzmann-gradient (BG) analog mechanism produces a 4% lift on conflicts
that are otherwise classified as "irreducible." Irreducible here means: no locally available
gradient in W-space points away from the conflicted state; the energy landscape is locally
flat or saddle-shaped around the frustrated minimum; argmax iteration converges to the same
basin regardless of initialization.

### Why 4% is not zero (and why that is the clue)

A BG mechanism at temperature T>0 samples from exp(-E/T) rather than hardmax. This gives
non-zero probability to states other than the local minimum, producing occasional escapes.
The 4% lift is exactly what you expect from Boltzmann sampling when the energy gap between
the frustrated minimum and the next basin is small relative to kT. This is NOT evidence
that BG is wrong -- it is evidence that the TEMPERATURE parameter is in the right ballpark
and the mechanism is working as designed. The correct framing is: "we are at the bottom of
a shallow frustration basin, BG samples uniformly around the bowl, and 4% of samples escape
to the correct basin."

The key implication: BG is a same-level (within-basin) operation. It can only escape by
lucky Boltzmann kicks. To reliably escape, the substrate needs a meta-level operation that
(a) detects frustration, (b) changes the representation or framing, and (c) re-presents the
problem to a resolver operating on a transformed landscape where the conflict is not
frustrated.

---

## STREAM A: BIOLOGY -- Multi-timescale deferral and reframing

### A.1 Behavioral deferral (sleep / delay / context-change)

Animals resolve conflicted states by NOT resolving them at the moment of conflict.
Three documented mechanisms:

(1) SLEEP CONSOLIDATION: Hippocampal replay during slow-wave sleep re-presents conflicts
to cortical circuits that have different synaptic time constants. The conflict that was
frustrated at the rapid (theta/gamma) timescale is re-evaluated at the slow (delta)
timescale where different convergence dynamics apply. The functional analog: a substrate
that defers conflicted queries to a slower, more expensive path with different effective
temperature or different binding field.

(2) TEMPORAL DISTANCING: Animals that fail to resolve a conflict under acute stress resolve
it after a period of inactivity. This is not magical -- the temporal gap allows unrelated
activity to shift the prior over states, so the re-presented conflict starts from a
different initialization. The functional analog: substrate inserts a stochastic perturbation
into W after a detected frustration event, then re-presents the query to a different
attractor basin.

(3) CONTEXT CHANGE (CUE RE-ENTRY): Animals trained on conflicting contingencies show
spontaneous recovery when placed in a different context. The context acts as a conditioning
variable that breaks the symmetry of the frustration basin -- the same stimulus is
ambiguous in context A but unambiguous in context B. The functional analog: the substrate
presents the conflicted query with a different binding field (different context hypervector),
effectively asking "resolve this conflict under the assumption that we are in context C."

### A.2 Cultural conventions (human-specific)

Humans resolve coordination conflicts (which side of the road to drive on, which bid price
to name) via shared cultural conventions. The convention is not derived from first
principles -- it is a pre-committed meta-level agreement that removes the conflict from the
resolution process entirely. No computation is needed: the convention IS the answer.

The substrate analog: a "frustration convention table" -- a lookup for known frustration
classes (detected structurally) that maps each class to a pre-committed resolution strategy.
This is not memorization -- it is a meta-cognitive module that recognizes the STRUCTURE of
a frustration basin and applies a resolution policy before entering the basin. Detected
via pattern P(frustration) = argmax_c sim(conflict_signature, convention_c).

### A.3 Planning and decomposition

Animals plan by decomposing a high-level goal into a sequence of sub-goals, each of which
is resolvable without the full conflicted state. The plan is generated at a meta-level that
has access to the goal structure but is not yet committed to any specific path through the
frustration basin.

The substrate analog: PLAN-DECOMPOSITION. A conflicted query is decomposed into a sequence
of sub-queries, each constructed so that the sub-query is NOT frustrated (each sub-query
has a clear majority winner in the Hamming sense). The sub-queries are resolved in
sequence, and their partial outputs are bound together to produce a composite answer.
This works whenever the frustration is caused by simultaneous multi-constraint satisfaction
and the constraints can be factored into a sequential schedule.

---

## STREAM B: BRAIN -- Prefrontal meta-cognition and DMN reframing

### B.1 Prefrontal cortex as meta-cognitive monitor

PFC does not store memories or perform primary pattern matching. Its anatomical role is
to maintain task-set representations and apply inhibitory control over competing responses.
In the conflict literature (Botvinick et al. 2001, Cohen et al. 2000), anterior cingulate
cortex (ACC) detects response conflict (measured as Hopfield-like energy in competing
response units) and signals PFC to INCREASE CONTROL, which then biases the next evaluation
away from the conflicted response.

The key math: conflict detection is Sigma_i (a_i)^2 - (Sigma_i a_i)^2, where a_i are
response unit activations. This is the variance of the activation distribution -- high
variance = high conflict. PFC activation is proportional to detected conflict. This is an
explicit meta-cognitive signal that triggers a DIFFERENT PROCESSING REGIME for the
next evaluation.

Substrate analog: CONFLICT-MONITOR layer. Compute the activation variance over competing
attractor candidates at each retrieval. When variance exceeds threshold theta_c, trigger
a secondary retrieval pass with a modified temperature or different binding field rather
than committing the primary result.

### B.2 Default mode network and reframing

The DMN (default mode network) activates during rest and is suppressed during focused task
performance. Its functional role (Andrews-Hanna et al. 2014, Buckner et al. 2008) includes:
mental simulation, prospection, and self-referential processing. Crucially, the DMN
re-encodes episodic memories in terms of high-level schemas that REMOVE surface details
and retain structural relationships. A conflict that was unresolvable at the surface level
may not be conflicted at the schema level.

Substrate analog: SCHEMA-REFRAMING. Conflicted queries are projected to a lower-dimensional
subspace that captures only structural relationships (analogous to PCA-whitened codes with
fewer components). The reduced representation may not be frustrated even when the full
representation is. If the schema-level query is unambiguous, its answer is lifted back to
the full representation space via reconstruction.

### B.3 Sleep and offline consolidation: the math

Tononi et al. (2014, SHY hypothesis) propose that wakefulness increases synaptic strength
via potentiation, while sleep globally downscales synapses toward a baseline. The mechanism
selectively preserves strong (high-signal) connections and removes weak (noise) connections.

The relevance to frustration: frustrated attractors often exist because of weak conflicting
connections that are insufficient to establish a clear winner but sufficient to prevent
convergence. A global downscale operation (equivalent to re-normalizing W toward a
sparsified version) removes the weak conflicting connections and allows the strong
connections to dominate.

Substrate analog: PERIODIC W-PRUNING. After N retrieval cycles, apply a soft threshold to
W that zeros entries below epsilon_W. This is a synaptic homeostasis analog. Frustrated
attractors that depend on weak cross-connections will lose those connections; the attractor
basin will either resolve cleanly or cease to exist (which is the correct outcome if the
stored memory itself was noise-contaminated).

---

## STREAM C: MATERIALS SCIENCE -- Spin glass frustration resolution

### C.1 What frustration is in spin glasses

A frustrated spin glass has local constraints that cannot simultaneously be satisfied.
The canonical example: three spins on a triangle with antiferromagnetic couplings J_{ij}<0.
No configuration satisfies all three constraints simultaneously -- at least one pair must
be aligned. This is energetically penalized and cannot be removed by any local move.

The frustrated ground state is NOT unique: there is a degenerate manifold of states that
all achieve the same (minimal achievable) energy. The system does not "solve" the conflict
-- it lives in the conflict. The Parisi order parameter q(x) for a frustrated spin glass
is nonzero and x-dependent, reflecting the ultrametric hierarchy of metastable states.

### C.2 Resolution mechanism 1: Thermal annealing

Simulated annealing (Kirkpatrick et al. 1983) escapes frustrated minima by increasing T
(thermal noise), allowing the system to explore the landscape at lower resolution, then
slowly cooling to a final state. The critical insight: at high T, the energy landscape is
effectively smoothed and the frustration basins merge into broader, less-frustrated basins.
The system finds the global optimum at the coarse level, then the fine-grained details are
resolved as T decreases.

The substrate version: TEMPERATURE-CASCADE annealing. For frustrated queries, apply a
sequence of retrieval passes with DECREASING temperature (T_1 > T_2 > ... > T_k). Each
pass refines the previous answer rather than starting from scratch. At T_1, the query
projects to a coarse approximation (possibly unfrusted); at T_k, the coarse approximation
is refined into a specific candidate.

### C.3 Resolution mechanism 2: Quantum tunneling

At finite temperature, spin glass dynamics proceed by thermal activation over energy
barriers. At zero temperature, quantum tunneling provides an alternative: the system
quantum-mechanically tunnels through barriers rather than climbing over them. The
effective tunneling rate between frustrated states scales as exp(-S_tunneling), where
S_tunneling is the tunneling action (proportional to barrier width x barrier height^{1/2}).

For shallow, wide frustrated minima (which is the case at 4% residual conflict), tunneling
is exponentially suppressed. For NARROW barriers (metastable states separated by a thin
high-energy ridge), tunneling is efficient. The practical analog in classical systems is
"momentum-based" methods (ADAM, momentum SGD) that can cross shallow barriers by
accumulating gradient history.

Substrate analog: MOMENTUM-AUGMENTED retrieval. The substrate's attractor iteration is
currently pure gradient descent on the energy landscape. Adding a momentum term allows
the iteration to carry inertia from previous steps through shallow barriers. This is
equivalent to partial quantum annealing at zero temperature.

Math: x_{t+1} = argmax(W^T h_t + beta * (x_t - x_{t-1}))

where beta is a momentum coefficient. For beta=0, this is standard Hopfield iteration.
For 0 < beta < 1, the iteration carries partial memory of the previous direction.

### C.4 Resolution mechanism 3: Breaking ergodicity via replica symmetry breaking

In the 1-RSB Parisi framework, the spin glass state space fractures into disconnected
"valleys" (ergodic components). Within each valley, dynamics are ergodic; between valleys,
ergodicity is broken. The system selects one valley via spontaneous symmetry breaking.

The resolution mechanism: ERGODICITY BREAKING via external field. An infinitesimal external
field (the Parisi h-field) explicitly breaks the symmetry between valleys, directing the
system into the valley that is aligned with the field. This is not an energy gradient --
it is a symmetry-breaking bias that selects among otherwise degenerate frustrated states.

Substrate analog: CONTEXTUAL DISAMBIGUATION FIELD. When frustration is detected, apply an
external conditioning vector h_context to the energy function:

  E(x; h) = -x^T W x + lambda * x^T h_context

where h_context is derived from a high-level context (e.g., the user's prior query
sequence, or a schema-level representation of the expected answer domain). The context
breaks the symmetry between the frustrated degenerate states and selects the one that is
most consistent with context.

This is algebraically identical to Parisi's external field, but semantically driven: the
field is not random noise but a contextually meaningful conditioning signal.

### C.5 Resolution mechanism 4: Mode-coupling relaxation (MCT)

Mode-coupling theory (MCT) for structural glasses describes two relaxation regimes: the
fast beta-process (cage rattling, ps-ns timescales) and the slow alpha-process (structural
relaxation, ns-ms timescales). Frustration at the fast timescale is NOT frustration at
the slow timescale -- different modes couple at each scale.

Substrate analog: DUAL-TIMESCALE retrieval. The substrate's fast pass (single-step argmax)
corresponds to the beta-process. A slow pass (iterated refinement over many cycles) with
W updated between cycles corresponds to the alpha-process. Conflicts that are unresolvable
in the beta-process may resolve in the alpha-process as the slow modes equilibrate.

---

## STREAM D: LLM THEORY -- Meta-cognitive conflict resolution

### D.1 Chain-of-thought decomposition

LLM chain-of-thought (CoT, Wei et al. 2022) produces dramatic accuracy improvements on
conflicted multi-step reasoning by decomposing the problem into explicit intermediate steps.
The critical mechanism is NOT that CoT gives the model more computation -- it is that CoT
forces the model to produce explicit intermediate representations that BREAK the conflict.

A conflicted LLM prompt (e.g., "Is the capital of Australia Sydney?") produces a frustrated
activation pattern because both "yes" (high co-occurrence of Australia and Sydney) and "no"
(Sydney is not the capital) have strong direct associations. CoT breaks this by making the
model produce: "Australia's cities include Sydney (largest), Melbourne, and Canberra. The
capital is Canberra. So no." The intermediate step REMOVES the frustration by introducing
Canberra as an explicit mediating concept.

Substrate analog: MEDIATION-STEP insertion. When frustration is detected (rival candidates
with near-equal similarity to query), construct a mediation vector by binding query with
a "disambiguation relation" hypervector:

  mediator = bind(query, R_disambiguate)
  candidates = {c : sim(W^T mediator, c) > theta}

The mediation step asks: "what is the disambiguation-relation of this query?" which may
have a clear winner even when the original query does not.

### D.2 Tool use and external grounding

LLM tool use (Mialon et al. 2023, Schick et al. 2023) resolves conflicts by delegating
to external ground truth rather than trying to resolve the conflict internally. When the
model detects uncertainty (high entropy over next tokens), it generates a tool call to
retrieve authoritative information.

Substrate analog: EXTERNAL-ANCHOR retrieval. When internal retrieval produces a frustrated
result (two candidates with similarity gap < delta_thresh), trigger a secondary retrieval
from a different (less compressed) representation of the KB. The secondary retrieval uses
an explicit lookup on structured metadata rather than associative retrieval, which is
not subject to the same frustration mechanism.

### D.3 Constitutional AI and constraint satisfaction

Constitutional AI (Bai et al. 2022, Anthropic) resolves conflicts between competing
principles (be helpful vs. be safe) via a hierarchical constraint system where one principle
explicitly dominates another. This is NOT general optimization -- it is a pre-committed
ordering of constraints that removes the conflict structurally.

Substrate analog: CONSTRAINT HIERARCHY in energy function. Rewrite the energy function as:

  E(x) = alpha_1 * E_primary(x) + alpha_2 * E_secondary(x) + alpha_3 * E_tertiary(x)

where alpha_1 >> alpha_2 >> alpha_3. Primary constraints are never violated for secondary
satisfaction. This lexicographic ordering prevents the energy function from being frustrated
across constraint levels -- frustration can only occur WITHIN a level.

### D.4 Backtracking and plan revision

LLMs with search (Yao et al. 2023, Tree of Thoughts) use explicit backtracking: when a
reasoning path leads to a conflict, the model returns to an earlier branch point and
selects a different path. This is a meta-level operation -- the model knows it is searching
a tree of possibilities and uses the detected conflict as a signal to revise the plan.

Substrate analog: DEAD-END DETECTION with backtrack. If retrieval produces a frustrated
result on path P (e.g., multi-hop retrieval x1 -> x2 -> conflict), backtrack to x1 and
try a different intermediate node x2'. The backtrack requires: (a) tracking the retrieval
path (not currently stored), (b) a divergence criterion to detect dead ends, (c) a
branching mechanism at each hop to generate alternative intermediates.

### D.5 Meta-prompting and self-reflection

Meta-prompting (Suzgun and Kalai 2024) uses an outer-loop prompt that explicitly
represents the task type, selects an appropriate problem-solving strategy, then applies
that strategy. The key insight: different problem types have different optimal strategies;
meta-prompting identifies the type FIRST and applies the matched strategy.

Substrate analog: FRUSTRATION-CLASS ROUTING. A lightweight classifier detects the
structural class of a frustrated query (e.g., multi-constraint, near-duplicate candidates,
chain-conflict) and routes it to the resolution strategy matched to that class. This is
a meta-level dispatch table -- not computation of the answer, but selection of the
computation policy.

---

## STREAM E: SUBSTRATE-NATIVE MECHANISMS (CRAZY)

Ten substrate-native mechanisms for irreducible-conflict resolution, derived by applying
the above frameworks algebraically to the substrate's existing representational primitives
(hypervectors, Hopfield W, binding/unbinding, similarity retrieval, cap_map operations).

### E.1 SUBSTRATE-DELAY-RESOLUTION

**Mechanism**: Insert a deliberate deferral step when frustration is detected. The system
does not attempt to resolve the conflict in the current retrieval pass. Instead, it stores
the conflicted state as a "pending" hypervector, executes unrelated retrievals to shift
the W statistics, then re-presents the pending query after k steps.

**Math**: Let x_frustrated be the attractor state at the frustrated minimum.
  store: pending[t] = x_frustrated
  after k steps: re-query = W^T pending[t]
  The re-query is now computed against a W that has been updated by k subsequent operations,
  which shifts the effective energy landscape. If any of those operations are correlated
  with the pending conflict, the W shift may resolve it.

**Pre-reg**: HARD-PASS if frustration rate reduces by >= 15% vs. no-delay baseline with
k=10 steps. HARD-FAIL if reduction < 5%.

### E.2 META-COGNITIVE-RECURSION

**Mechanism**: The substrate applies itself recursively to its own conflict state. The
first-order retrieval produces a conflicted result x_1. A second-order retrieval asks:
"what is the meta-representation of this conflict?" using a reserved meta-retrieval
register:

  x_meta = W_meta^T bind(x_1, R_meta)

where W_meta is a separate weight matrix trained on conflict patterns and R_meta is a
"meta" binding vector. The meta-representation x_meta is in a space where conflicts
map to distinct meta-attractors, each associated with a resolution strategy.

**Math**: This is a 2-layer Hopfield network with a bottleneck: the bottom layer runs
standard retrieval; the top layer is a smaller Hopfield net trained on representations
of conflict states and their correct resolutions. The top layer breaks frustrations that
the bottom layer cannot.

**Pre-reg**: HARD-PASS if adding W_meta (N x N/4, N/4 meta-dimensions) achieves
frustration resolution rate >= 0.60. HARD-FAIL if < 0.30.

### E.3 CULTURAL-CONVENTION-FALLBACK

**Mechanism**: Pre-register a set of canonical conflict signatures and their conventional
resolutions. When a detected frustration matches a canonical signature (sim > 0.85 to
a stored pattern), apply the convention without further computation.

**Math**: Build a convention codebook C = {(s_i, r_i)} where s_i is a frustrated-state
signature and r_i is the resolution hypervector. At retrieval:
  if max_i sim(x_frustrated, s_i) > 0.85:
    output = r_i*
  else:
    escalate to deeper mechanism

This is a substrate-level "constitution" -- a pre-committed table of answers to known-hard
questions that removes them from the dynamic computation.

**Pre-reg**: HARD-PASS if convention lookup reduces retrieval latency for known-frustrated
queries by >= 80% while maintaining correctness >= 0.95. HARD-FAIL if correctness < 0.90.

### E.4 STOCHASTIC-TUNNELING

**Mechanism**: Implement classical stochastic tunneling (Wenzel and Hamacher 1999) via
energy transformation: replace E(x) with E_tunnel(x) = 1 - exp(-gamma * E(x)). This
flattens the landscape around high-energy barriers, allowing Boltzmann sampling to cross
them without requiring a very high temperature globally. The tunneling parameter gamma
controls the degree of flattening.

**Math**:
  Standard BG: P(x) ~ exp(-E(x)/T)
  Tunneling BG: P(x) ~ exp(-E_tunnel(x)/T) = exp(-(1-exp(-gamma*E(x)))/T)

  For E(x) >> 1/gamma: E_tunnel -> 1, barriers are flattened to the ceiling.
  For E(x) << 1/gamma: E_tunnel ~ gamma*E(x), original landscape preserved.

  Setting gamma = 1/(E_barrier), the barrier is flattened to ~0.63 of its original height,
  allowing Boltzmann sampling to cross it at much lower T than the original.

**Pre-reg**: HARD-PASS if stochastic tunneling with gamma=1/(E_typical barrier) achieves
>= 25% frustration escape rate vs. 4% baseline. HARD-FAIL if < 10%.

### E.5 FRAMING-TRANSFORMATION

**Mechanism**: Apply a learned linear transformation T: R^N -> R^N to the query
hypervector before retrieval. The transformation T is trained to map frustrated query
representations to their resolved representation (i.e., T maps the frustrated attractor
to the basin of the correct answer). This is not a general whitening -- it is a learned
conflict-specific "framing transformation."

**Math**: T is a rectangular projection P (N x k, k << N) followed by expansion P^T.
The projection removes the frustration-inducing components of the query (the dimensions
that activate conflicting attractors equally) while preserving the components that
distinguish the correct answer.

  x_resolved = P^T P x_frustrated = P^+ P x_frustrated

where P is learned via a small number of labeled frustration examples.

**Pre-reg**: HARD-PASS if T reduces frustration rate by >= 20% with k = N/8 projection
rank. HARD-FAIL if reduction < 8% at any k.

### E.6 DREAMING-CONFLICT-RESOLUTION

**Mechanism**: Implement an offline consolidation pass (analogous to sleep) where the
substrate replays recently conflicted queries against a SPARSIFIED version of W. The
sparsification (zero all W entries below epsilon_sparse) is the SHY analog. During the
offline pass, conflicts that depend on weak connections are forced to resolve using only
strong connections. The resolved answers from the offline pass are used to update a
"consolidated memory" register.

**Math**:
  W_sparse = W * (|W| > epsilon_sparse)    [elementwise sparsification]
  x_resolved = hopfield_iterate(x_conflicted, W_sparse)
  if x_resolved != x_conflicted:
    update: resolved_memory[x_conflicted] = x_resolved

**Pre-reg**: HARD-PASS if offline consolidation resolves >= 40% of previously frustrated
queries using epsilon_sparse = median(|W|). HARD-FAIL if < 15%.

### E.7 PLAN-DECOMPOSITION

**Mechanism**: Decompose a frustrated query into a sequence of sub-queries, each
targeted at a single constraint. The output of each sub-query is used as a conditioning
vector for the next sub-query. The decomposition schedule is learned from examples or
derived analytically from the conflict structure.

**Math**: Let q = query, c_1...c_k = constraints that conflict in q.
  Decomposed schedule:
    x_1 = retrieve(q | c_1 satisfied)        [partial query conditioned on c_1]
    x_2 = retrieve(x_1 | c_2 satisfied)      [extend x_1 with c_2]
    ...
    x_k = retrieve(x_{k-1} | c_k satisfied)  [final answer satisfying all constraints]

  Each step is a Hopfield retrieval with the query augmented by a constraint-satisfaction
  binding: q_i = bind(q, R_{c_i}) to enforce constraint c_i.

  Algebraic property: if constraints c_1...c_k are approximately independent given q,
  then x_k = Bigotimes_{i=1}^k R_{c_i} * q produces a non-frustrated answer.

**Pre-reg**: HARD-PASS if decomposed retrieval achieves correctness >= 0.75 on
3-constraint frustrated queries where standard retrieval scores 0.50. HARD-FAIL if < 0.60.

### E.8 RECURSIVE-SUBGOAL

**Mechanism**: When the full query is frustrated, generate a SUBGOAL hypervector by
projecting the query onto its most-constrained dimension and constructing a simpler query
that is guaranteed to have a unique attractor. Retrieve the subgoal answer, then use it
to construct a refined query that is closer to the full query but no longer frustrated.

**Math**: This is a recursive-halving approach to constraint satisfaction.
  level = 0: subgoal_0 = project(q, dim_most_constrained)
  level = 1: subgoal_1 = extend(subgoal_0_answer, q - project(q, dim_most_constrained))
  ...
  Convergence when sim(q_level, q_full) > 1 - epsilon

  At each level, the query is guaranteed non-frustrated by construction (it only includes
  constraints that were satisfied at the previous level plus one new constraint).

**Pre-reg**: HARD-PASS if recursive-subgoal achieves correctness >= 0.70 at depth 3.
HARD-FAIL if depth-3 correctness < 0.55.

### E.9 SYMMETRY-BREAKING-INJECTION

**Mechanism**: When frustration is detected, inject a small random symmetry-breaking
perturbation epsilon_SB into the query hypervector, THEN apply BG. The perturbation has
the same role as Parisi's external field: it differentiates the degenerate ground states.
The key is that the perturbation is NOT pure noise -- it is drawn from a distribution
conditioned on the high-level context (schema, prior query, domain).

**Math**:
  x_perturbed = q + epsilon_SB * h_context   [h_context: unit context hypervector]
  x_resolved = hopfield_iterate(x_perturbed, W, T_low)

  The context h_context breaks the Z_2 symmetry of the frustrated basin, making one
  degenerate ground state lower energy than the other. The BG sampling then reliably
  finds the lower-energy state (which is the contextually correct answer).

  For h_context orthogonal to the frustration axis: zero effect (correct no-op).
  For h_context aligned with the frustration axis: direct resolution.

**Pre-reg**: HARD-PASS if context-conditioned perturbation achieves >= 30% frustration
resolution where BG alone achieves 4%. HARD-FAIL if < 10%.

### E.10 ATTRACTOR-LANDSCAPE-SURGERY

**Mechanism**: Detect frustrated attractor pairs (a_1, a_2 with near-equal similarity to
query q) and surgically modify W to increase the energy gap between them. This is NOT
Hebbian learning of the correct answer -- it is anti-Hebbian removal of the incorrect
competitor.

**Math**:
  Given frustrated pair (a_1, a_2) and ground-truth correct a_1:
  W_update = W - alpha * a_2 * a_2^T   [suppress the competing attractor basin]

  This reduces the capacity for a_2 as an attractor while preserving all other stored
  patterns (to first order). The energy at a_2 increases relative to a_1, resolving the
  frustration.

  The risk: a_2 may be needed for other queries. Surgery requires scoped modification:
  W_update = W - alpha * a_2 * a_2^T + alpha * a_2_safe * a_2_safe^T
  where a_2_safe = project(a_2, complement(q)) -- the part of a_2 unrelated to q.

**Pre-reg**: HARD-PASS if attractor surgery resolves >= 50% of targeted frustrated
pairs without reducing recall on non-targeted queries by > 5%.
HARD-FAIL if non-targeted recall degrades by > 10%.

---

## CHEAP DECISIVE TEST

**For fastest signal**: E.4 STOCHASTIC-TUNNELING is the cheapest decisive test.
It requires only replacing E(x) with E_tunnel(x) in the BG sampling step -- no new
infrastructure, no new matrices, no training. The parameter gamma can be set analytically
from the observed energy barrier height (which is already measurable from the existing
BG 4% baseline). Run on the exact same frustrated-query benchmark as the 4% baseline.
Expected runtime: < 30 min CPU.

**Verdict criterion**: If tunneling escape rate > 10% (vs. 4% baseline), mechanism is
viable. If tunneling escape rate > 25%, stochastic tunneling alone is sufficient.
If < 10%, escalate to E.3 (cultural-convention-fallback, highest ceiling, requires
pre-registration of conflict signatures).

---

## FALSIFIABLE PREDICTIONS

### HARD-PASS thresholds (any one of these = strong signal)

1. E.4 STOCHASTIC-TUNNELING: frustration escape rate >= 25% on existing benchmark
2. E.9 SYMMETRY-BREAKING-INJECTION: context-conditioned resolution >= 30%
3. E.7 PLAN-DECOMPOSITION: 3-constraint correctness >= 0.75 vs. 0.50 baseline
4. E.2 META-COGNITIVE-RECURSION: W_meta achieves >= 0.60 resolution rate
5. E.6 DREAMING (offline consolidation): >= 40% of frustrated queries resolve offline

### HARD-FAIL thresholds (any of these = close that path)

1. E.4: escape rate < 10% -- tunneling not viable (barriers too wide / landscape wrong)
2. E.9: < 10% -- context field orthogonal to frustration axis (frustration not symmetry-breaking)
3. E.7: < 0.60 -- constraints not decomposable (frustration is entangled, not factored)
4. E.3: correctness < 0.90 -- convention table not reliable enough
5. Any mechanism: improvement < 5% -- mechanism has no foothold; close and move to next

---

## CROSS-THREAD SYNTHESIS

### Connection to spin-glass field (83% yield, 6 drills)

This drill opens THREE new angles in the spin-glass field that are not yet drilled:
- 1-RSB Parisi step (E1 from field advisor): directly relevant to ergodicity-breaking (E.10)
- Cavity method (E3): gives exact energy landscape description for substrate's W
- MCT slow-dynamics (structural-glasses-MCT, new Tier-1b field): alpha/beta relaxation =
  DUAL-TIMESCALE retrieval (E.6 / C.5 above)

### Connection to empowerment (prior drill 2026-06-10)

The CONTEXTUAL DISAMBIGUATION FIELD (E.9) is algebraically identical to the context
vector h_context in the empowerment bridge. The same "conditioning by context" mechanism
applies to both: for empowerment, context selects the action-value direction; for
frustration, context selects the degenerate ground state. A single implementation serves
both use cases.

### Connection to plan decomposition (LLM literature)

The PLAN-DECOMPOSITION mechanism (E.7) is the substrate-native implementation of CoT.
The "bind(q, R_{c_i})" operation is the substrate version of generating an explicit
intermediate reasoning step. The algebraic independence condition (constraints approximately
independent given q) is the substrate version of the "chain decomposability" condition
that makes CoT work.

### Connection to free-probability field (100% yield, 1 drill)

FRAMING-TRANSFORMATION (E.5) involves projecting to a k-dimensional subspace and back.
This is a deterministic rank-k approximation. Free-probability theory (Marchenko-Pastur,
R-transform) gives the exact distribution of eigenvalues of W^T W in the large-N limit,
which determines the optimal rank k for the projection. This is an unexplored connection
that makes E.5 analytically tractable.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **Frustration rate is a product quality metric.** If the product claims to resolve
   conflicts, the 4% residual frustration rate is a stated limitation. The mechanisms in
   this note give a concrete product roadmap from 4% toward sub-1%.

2. **STOCHASTIC-TUNNELING is zero-infrastructure.** It can be shipped as a parameter
   change in the BG sampling step. If it achieves >= 25% escape rate, the product benefit
   is immediate and requires no new model training or architecture change.

3. **CONFLICT-MONITOR + SYMMETRY-BREAKING-INJECTION (B.1 + E.9)** can be combined into
   a single "frustration mode" that is triggered by variance threshold. This is a
   product feature: "if the substrate detects a conflict, it automatically applies context-
   conditioned disambiguation." User experience: fewer wrong answers on ambiguous queries.

4. **DREAMING (E.6)** is a product-level offline maintenance operation. Run it after each
   KB import or during low-traffic periods. It improves freshness of the resolved-memory
   register without user-visible latency.

5. **PLAN-DECOMPOSITION (E.7)** enables multi-constraint queries that current architecture
   cannot answer reliably. This directly addresses the multi-hop retrieval failure mode
   (project status: MULTI-HOP REVIVE PRIORITY per memory).

6. **CONVENTION TABLE (E.3)** is a product feature for high-stakes domains (medical,
   legal) where ambiguity must be resolved by authority, not by energy landscape dynamics.

---

## P ESTIMATES (deflated per calibration penalty)

| Mechanism | Raw P (theoretical) | Deflation | P_deflated | Status |
|---|---|---|---|---|
| E.4 Stochastic tunneling | 0.65 | -0.20 | 0.45 | CANDIDATE |
| E.9 Symmetry-breaking | 0.60 | -0.20 | 0.40 | CANDIDATE |
| E.7 Plan decomposition | 0.55 | -0.20 | 0.35 | CANDIDATE |
| E.3 Convention fallback | 0.70 | -0.20 | 0.50 | CANDIDATE (cap) |
| E.6 Dreaming | 0.50 | -0.20 | 0.30 | CANDIDATE |
| E.2 Meta-cognitive recursion | 0.45 | -0.20 | 0.25 | SPECULATIVE |
| E.10 Attractor surgery | 0.55 | -0.20 | 0.35 | CANDIDATE |
| E.8 Recursive subgoal | 0.50 | -0.20 | 0.30 | SPECULATIVE |
| E.5 Framing transformation | 0.55 | -0.20 | 0.35 | CANDIDATE |
| E.1 Delay resolution | 0.40 | -0.20 | 0.20 | LOW PRIORITY |

P_deflated for two-mechanism cascade (best pair: E.4 + E.9): 0.48 (capped at 0.50).

---

## CITATIONS

1. Kirkpatrick S, Gelatt CD, Vecchi MP. "Optimization by simulated annealing." Science 220(4598):671-680 (1983).
2. Botvinick MM, Braver TS, Barch DM, Carter CS, Cohen JD. "Conflict monitoring and cognitive control." Psychol Rev 108(3):624-652 (2001).
3. Tononi G, Cirelli C. "Sleep and the price of plasticity." Neuron 81(1):12-34 (2014). [SHY hypothesis]
4. Parisi G. "Order parameter for spin-glasses." Phys Rev Lett 50(24):1946 (1983). [RSB / order parameter]
5. Wenzel W, Hamacher K. "Stochastic tunneling approach for global minimization of complex potential energy landscapes." Phys Rev Lett 82(15):3003 (1999).
6. Wei J et al. "Chain-of-thought prompting elicits reasoning in large language models." NeurIPS 2022.
7. Yao S et al. "Tree of thoughts: deliberate problem solving with large language models." NeurIPS 2023.
8. Bai Y et al. "Constitutional AI: harmlessness from AI feedback." arXiv:2212.06950 (2022).
9. Salge C, Glackin C, Polani D. "Empowerment -- an introduction." arXiv:1310.1863 (2014).
10. Andrews-Hanna JR. "The brain's default network and its adaptive role in internal mentation." Neuroscientist 18(3):251-270 (2012).
11. Buckner RL, Andrews-Hanna JR, Schacter DL. "The brain's default network." Ann NY Acad Sci 1124:1-38 (2008).
12. Cohen JD et al. "Anterior cingulate and prefrontal cortex: who's in control?" Nature Neurosci 3(5):421-423 (2000).
13. Suzgun M, Kalai AT. "Meta-prompting: enhancing language models with task-agnostic scaffolding." arXiv:2401.12954 (2024).
14. Mialon G et al. "Augmented language models: a survey." arXiv:2302.07842 (2023).
15. Schick T et al. "Toolformer: language models can teach themselves to use tools." NeurIPS 2023.
16. Gotze F, Tikhomirov A. "Rate of convergence in probability to the Marchenko-Pastur law." Bernoulli 10(3):503-548 (2004). [free-probability: relevance to E.5]
17. Gotze F, Tikhomirov A (above) also applies to Tracy-Widom edge; see Anderson GW, Guionnet A, Zeitouni O. "Introduction to Random Matrices." Cambridge UP (2010).
18. Gothoskar N et al. "3DP3: 3D scene perception via probabilistic programs." NeurIPS 2021. [recursive subgoal/decomposition analog]

Total verified citations: 18 (all peer-reviewed or major arXiv preprints with known authorship).

---

## NEXT-DRILL CANDIDATE

**Stochastic tunneling + free-probability (E.4 + F2)**: The energy barrier distribution
for substrate W is needed to set gamma analytically. This requires Tracy-Widom edge
fluctuation analysis of W eigenvalues -- a free-probability calculation that has NOT been
drilled (F2 from field advisor, score=5.0, count=0). Combined drill would make E.4
analytically grounded rather than heuristically parameterized.
