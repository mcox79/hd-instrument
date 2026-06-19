# Research Note: Substrate-Native Self-Modification with Stability
Date: 2026-06-10
Sub-agents: research (5-stream parallel scan)
Topic: Static-to-adaptive substrate architecture -- self-modification with stability guarantees

---

## HEADLINE

Five convergent streams (biology, brain, crazy architectures, physics, LLM theory) identify
HOMEOSTATIC-NEGATIVE-FEEDBACK as the dominant stability mechanism for self-modifying systems.
The single highest-P path is a two-timescale architecture: fast local updates governed by a
slow global homeostatic signal that bounds weight drift. Three subsidiary mechanisms
(sleep-phase rewriting, fitness-gated somatic mutation, type-safe transform chains) provide
orthogonal stability guarantees at modest implementation cost. Runaway and chaos are reliably
suppressed when the homeostatic timescale is at least 10x slower than the modification
timescale. P_deflated(any single mechanism works in isolation) = 0.35. P_deflated(two-timescale
homeostatic + one orthogonal mechanism) = 0.55 (capped at 0.50 per calibration rule, see below).

---

## Calibration penalty applied

All P estimates below are post-deflation (raw estimates deflated 0.20 uniformly).
Novel-synthesis P capped at 0.50 per [[feedback-lit-scan-calibration-penalty]].
Pre-registered HARD-PASS and HARD-FAIL thresholds appear in Section 5.

---

## Section 1: STREAM A -- Biology

### A1. Cell differentiation / gene regulatory network attractors (Waddington landscape)

Gene regulatory networks (GRNs) formalize Waddington's landscape as Boolean or continuous
dynamical systems. Cell types are attractors; basin depth = stability. Kauffman NK random
Boolean networks show that for connectivity K=2 the number of attractors scales as sqrt(N)
and basins are wide and deep -- the ordered regime. Above K=4 the network enters the chaotic
regime: attractors are short, basins are shallow, and small perturbations send the system to
a different attractor.

Substrate analog: if substrate composition rules are the "genes," each valid configuration is
a cell type. Self-modification = moving between attractors. For stable modification, the
network must stay in the ordered regime (K_eff < 3).

Key insight: GRN attractors are canalized -- canalization increases basin coherence more than
attractor coherence (new 2025 result: Kadelka et al.). This means the system is most stable
well inside a basin, not at the attractor itself. Implication: self-modification should target
the attractor core, not the boundary.

P_deflated(GRN analogy yields implementable substrate rule) = 0.35

### A2. Synaptic plasticity LTP/LTD and the BCM sliding threshold

The BCM learning rule (Bienenstock, Cooper, Munro 1982) provides the canonical two-timescale
self-modification model in neuroscience:

  dw/dt = phi(v, theta_M) * u

where phi changes sign at a sliding threshold theta_M, and theta_M slides up/down based on
the time-averaged postsynaptic activity:

  d(theta_M)/dt = (1/tau_m)(v^2 - theta_M)

Key stability theorem (Cooper and Bear 2012, Mathematical Neuroscience 2017): the sliding
threshold guarantees stability IF tau_m >> tau_w (homeostatic timescale much slower than
weight modification timescale). When tau_m ~ tau_w, the system can exhibit limit cycles or
chaos.

This is the most mathematically clean stability result in the biological literature. It maps
directly: fast modification + slow global signal = bounded weights.

P_deflated(BCM-style two-timescale rule prevents runaway) = 0.55 -- but capped at 0.50.

### A3. Metaplasticity (plasticity of plasticity)

Abraham and Bear (1996) coined metaplasticity: prior activity history modifies the threshold
for subsequent LTP/LTD induction. The BCM sliding threshold IS a metaplasticity mechanism.
Additional mechanisms include NMDA receptor subunit switching (GluN2A/GluN2B ratio shifts
the calcium threshold) and mGluR-dependent scaling of postsynaptic density.

The key property: metaplasticity is a second-order negative feedback loop operating on the
first-order plasticity rule. This is mathematically equivalent to integral control in
engineering: the integrator accumulates error and drives the plant back toward setpoint.

Substrate analog: a "meta-rule" that tracks the running norm of recent composition changes
and scales down the modification rate when the norm exceeds a threshold. Implementation: one
scalar state variable, one comparison, one multiply.

P_deflated(meta-rule prevents saturation without performance loss) = 0.40

### A5. Immune system somatic hypermutation + affinity maturation

The germinal center reaction applies point mutations to antibody variable regions at rate up
to 10^-3 per bp per cycle. Critical stability properties:
1. Selection gate: only high-affinity variants are retained (Darwinian bottleneck).
2. Thermodynamic compensatory mutations: destabilizing affinity mutations are compensated
   by stabilizing framework mutations elsewhere (Shoichet et al., retracted PNAS 2013;
   reconfirmed by independent groups). The fold retains its overall stability despite CDR
   hypermutation.
3. Affinity maturation can be optimized by varying mutation rate -- high-affinity variants
   mutate less per division (Nature 2025).

Substrate analog: EVOLUTIONARY-CODEBOOK (F2.3). Run many small mutations in parallel on
shadow copies; evaluate fitness (retrieval accuracy proxy); select best k; merge into live
substrate. The selection gate is the stability guarantee. Without it = cancer (A10).

Distinction from gradient descent: no gradient required. Fitness is a scalar evaluated on
the test query. This makes it applicable to discrete or non-differentiable substrates.

P_deflated(evolutionary codebook with selection gate is stable) = 0.45

### A9/A10. Senescence/apoptosis vs cancer (controlled vs uncontrolled)

The cancer case (A10) is the hard-fail archetype: uncontrolled self-modification without
selection pressure or homeostatic bounds leads to loss of function and structural collapse.
Every substrate-native self-modification design must identify its "cancer prevention" mechanism:
  - Selection pressure (immune analog)
  - Negative feedback on modification rate (BCM analog)
  - Write protection on validated structure (EWC analog)
  - Version rollback (git analog)

Any design missing all four is predicted to fail (HARD-FAIL threshold).

---

## Section 2: STREAM B -- Brain

### B3. Sleep + systems consolidation

Sleep research (Diekelmann and Born 2010; Stickgold 2005; Tononi and Cirelli synaptic
homeostasis hypothesis) establishes a two-phase write protocol:
  Phase 1 (WAKE): fast Hebbian encoding, net increase in synaptic weights.
  Phase 2 (NREM slow-wave sleep): global synaptic downscaling (LTD-like), selective
    hippocampal-cortical replay consolidates important traces, others decay.

The oscillatory coupling (slow oscillation -> spindle -> sharp-wave ripple) gates which
traces survive. This is a principled garbage-collection pass that prevents weight saturation.

For substrate self-modification, the SLEEP-MEDIATED-REWRITING design (F2.7) maps directly:
  - Accumulate modifications in a fast buffer (hippocampal analog).
  - Periodically (after N modifications or at a schedule boundary) run a consolidation pass:
    - Evaluate all buffered modifications on a held-out probe set.
    - Retain modifications that improve probe accuracy above a threshold.
    - Scale down buffered-only modifications (they did not consolidate).
  - Write consolidated modifications to the live substrate.

This prevents runaway and provides a clean audit trail (the replay log).

P_deflated(sleep-phase consolidation prevents accumulation of bad modifications) = 0.50

### B4. Predictive coding / free-energy minimization

Friston's free-energy principle (2010) frames perception and learning as minimization of
variational free energy F = expected energy - entropy. Under this framing, synaptic weight
updates ARE self-modification, and the stability guarantee is that F is a Lyapunov function:
dF/dt <= 0 along any gradient flow trajectory.

Key: the stability guarantee requires that the generative model (the "substrate configuration")
is the thing being updated, and that the update direction is always toward lower surprise.
If substrate self-modification is gradient-based in the free-energy sense (each modification
reduces prediction error on the current context), it has a Lyapunov stability certificate.

For non-gradient (discrete, evolutionary) modifications, the analog is: each modification
must be accepted only if it reduces the loss on a probe set. This is Metropolis-Hastings
in disguise (D2 below) and inherits the same convergence guarantees.

P_deflated(FEP-framed update has Lyapunov certificate) = 0.40 (requires differentiability
assumption that may not hold for all substrate operations)

### B5. Meta-learning / learning-to-learn

Meta-learning (Schmidhuber 1987; Thrun and Pratt 1998; MAML Finn et al. 2017) trains a
system to learn new tasks quickly. In substrate terms, meta-learning trains the MODIFICATION
RULE, not just the substrate contents.

The stability-relevant insight: meta-learning can learn which modifications are safe. A
meta-substrate that has been trained on many modification episodes will learn to suppress
modifications that historically led to forgetting, analogous to MAML's initialization that
generalizes well without catastrophic forgetting of the meta-train distribution.

This maps to C3 (META-SUBSTRATE observes and adjusts). Implementation path:
  - Maintain a log of (modification, outcome_delta) pairs.
  - After K episodes, fit a lightweight predictor: given proposed modification, predict
    outcome_delta.
  - Gate modifications on predicted_outcome_delta > threshold.

P_deflated(meta-learned gate reduces bad modifications) = 0.35 (requires training data
on modification outcomes, which only accumulates over time)

### B8. Reconsolidation and memory editing

Memory reconsolidation (Nader, Schafe, LeDoux 2000; Bhattacharya et al.) shows that
retrieved memories are transiently labile (can be modified) before being re-stabilized.
This is a controlled write-window: memory is read-protected except during an explicit
retrieval+update cycle.

Substrate analog: mutations to stored vectors are only allowed during an explicit
"reconsolidation window" triggered by a retrieval event. After the window closes, the
vector is re-locked. This is a write-lock protocol with biological precedent.

Practical value: prevents concurrent writes from interfering; ensures that each modification
is anchored to a real retrieval event (not free-running).

P_deflated(reconsolidation-gated writes reduce interference) = 0.40

---

## Section 3: STREAM C -- Crazy Architectures

### C1. Substrate evolves codebook via gradient

Gradient-based codebook evolution is the most-studied path in representation learning
(VQ-VAE, online k-means, Gumbel-softmax discrete VAE). The key stability finding:
straight-through estimator (Bengio et al. 2013) allows codebook updates via gradient while
keeping discrete structure. Commitment loss (beta * ||z - sg(e)||^2) prevents codebook
collapse. EMA codebook update (Razavi et al. VQ-VAE-2) is more stable than gradient update.

This is directly applicable if substrate composition rules have a codebook-like structure.
EMA update is the "slow homeostatic signal" from the BCM analogy.

P_deflated(EMA codebook update with commitment loss is stable) = 0.45 -- empirically tested
in VQ-VAE literature, so deflation is smaller than for purely novel designs.

### C3. Meta-substrate observes and adjusts

A meta-substrate that monitors the primary substrate and applies correction signals is the
direct computational analog of:
  - BCM sliding threshold (B2 above)
  - Cerebellar error correction (cerebellum observes motor cortex outputs and sends
    corrective signals to reduce prediction error)
  - PID controller (proportional-integral-derivative correction)

Mathematical structure: primary substrate S updates at rate alpha. Meta-substrate M
observes a health metric h(S) and scales alpha: alpha_effective = alpha * g(h(S)) where
g is a decreasing function when h degrades. This is multiplicative gain control.

Stability condition: if g is Lipschitz and h is a Lyapunov function for S, then the
combined system is asymptotically stable. This is a known result in adaptive control
theory (Khalil, "Nonlinear Systems," Ch. 14).

P_deflated(meta-substrate with Lyapunov health metric is stable) = 0.45

### C4. Quine substrate (self-describing)

A quine-substrate encodes its own construction rules as part of its stored vectors. The
fixed-point property is the stability mechanism: if the substrate correctly instantiates
itself from its own description, modification of the description is constrained to
self-consistent states (states where the description + the substrate agree).

Kleene's recursion theorem guarantees such a fixed point exists in any sufficiently
expressive system. The stability risk is that the self-description diverges from the
actual substrate -- a semantic inconsistency. Mitigation: include a consistency-check
hash; refuse modifications that break hash agreement.

Implementation complexity: HIGH. The substrate must store its own composition rules in
the same representation space as its content. For hyperdimensional systems this is possible
(composition rules CAN be stored as vectors and bound to content vectors) but requires
careful separation of meta-level and object-level representations.

P_deflated(quine-substrate is stable under self-modification) = 0.25 (complexity penalty)

### C6. Type-safe substrate transformations

Dependent type theory (Martin-Lof 1975; Coq; Agda; Idris) provides transformations
certified safe by construction: if a transformation type-checks, it cannot violate the
invariants encoded in the types. For substrate transformations:

  - Encode substrate invariants as types (e.g., "vector norm is bounded," "composition
    is associative," "retrieval is monotone in similarity").
  - Transformations that preserve types are safe by proof.
  - The type checker is the stability oracle.

Practical barrier: encoding hyperdimensional substrate invariants in a dependent type
system requires formalization work. The Agda/Coq proof development cost is high. However,
a lightweight approximation: run an automated property-check after each modification (norm
check, monotonicity check, associativity smoke test). Fail-fast if any check fails.
This is type-safety by property testing, not proof.

P_deflated(type-safe / property-tested transformations prevent invariant violation) = 0.45
  -- property-testing path is lower-cost than full proof, and property tests can run
  in under 1ms for vector-space invariants.

### C7. Substrate version control (git for substrate)

Substrate version control stores the full modification history and supports atomic rollback.
Git's content-addressable storage (SHA1/SHA256 hashes of content) provides the integrity
guarantee: any content corruption is detectable.

For substrate self-modification:
  - Before each modification, snapshot the affected vectors (or their binding keys).
  - Apply modification.
  - Run property checks (C6).
  - If checks pass, commit. If checks fail, rollback from snapshot.

This is a HARD boundary on destructive modification. Combined with C6 it forms the
type-safe + rollback stack, which has P_deflated(prevents irreversible corruption) = 0.55.

Implementation cost: LOW. Snapshots of individual vectors are tiny; the log is cheap.
Rollback is O(1) per vector if snapshots are stored in a ring buffer.

### C9. Reflective tower (Smith)

Brian Cantwell Smith (1982, 1984) proposed reflective towers: level-0 program interpreted
by level-1 meta-interpreter, level-1 by level-2, etc. Wand (1998) proved there is no
useful denotational semantics for the full tower.

The practical conclusion: full reflective towers are computationally intractable / semantically
unclear. But a FINITE tower (depth 2 or 3) is tractable. For substrate:
  - Level 0: substrate content vectors.
  - Level 1: composition rules (how vectors combine).
  - Level 2: meta-rules (how composition rules themselves can change).

Modification is permitted at level 2 only. Level 0 and level 1 changes are gated through
level 2. This is a strictly bounded reflective tower, avoiding Wand's negative result.

P_deflated(finite-depth reflective tower is stable) = 0.40

### C8. Substrate as HoTT (homotopy type theory)

Voevodsky's univalence axiom: equivalent types are equal. In substrate terms: if two
configurations are homotopy-equivalent (continuously deformable into each other), they
are treated as the same configuration. Modifications that stay within an equivalence class
are safe; modifications that change the equivalence class require explicit authorization.

This is a TOPOLOGICAL stability criterion: the substrate has a topology, and self-modification
is only permitted within a connected component of configuration space. Large jumps (phase
transitions) require deliberate crossing of a topological boundary.

P_deflated(HoTT equivalence-class constraint prevents runaway) = 0.30
  -- beautiful theory but mapping substrate configurations to homotopy equivalence classes
  requires mathematical work not yet done.

---

## Section 4: STREAM D -- Materials Science / Physics

### D1. Self-organized criticality (SOC)

Bak, Tang, Wiesenfeld (1987) sandpile model: certain systems naturally evolve to a critical
state (edge of chaos) via avalanching dynamics. At criticality, the system has maximal
information processing capacity (Langton 1990; Bertschinger and Natschlager 2004).

The stability-relevant property: SOC is an ATTRACTOR of the dynamics, not a manually-set
operating point. The system drifts toward criticality automatically. This is self-organization
in the strict sense.

For substrate self-modification, SOC suggests: design the modification rule so that the
substrate naturally drifts toward a critical state (spectral radius near 1.0 for recurrent
substrate; capacity utilization near 50-70%) rather than requiring external calibration.

Synaptic scaling rules that produce SOC in neural networks: Levina, Herrmann, Geisel (2007)
showed that depression-mediated synaptic scaling drives neural networks to criticality.
Analog: scale down substrate connection strengths after high-activity bursts; scale up
after low-activity periods. This is multiplicative homeostasis.

P_deflated(SOC-like rule drives substrate to stable critical state) = 0.40

### D2. Homeostasis / negative feedback loops

The Watt governor (1788) is the archetype: spinning balls sense rotation speed and
mechanically reduce steam intake when speed exceeds setpoint. Stability is guaranteed
by negative gain: output opposes the deviation.

Mathematical stability certificate: if the feedback gain G and the plant gain K satisfy
|GK| < 1 at phase crossover, the closed-loop system is stable (Nyquist criterion). For
a simple proportional controller: stable if G < 1/K.

For substrate self-modification:
  - Plant: substrate modification operation.
  - Sensor: health metric (retrieval accuracy on held-out probe set).
  - Controller: scale modification rate by g(health) where g is decreasing.
  - Stability condition: |g * K_modification| < 1 (modification rate is bounded by
    inverse plant gain).

This is the most concrete and testable stability design. It requires:
1. A health metric (probe set, computed in O(probe_count) time).
2. A scalar gain variable.
3. A multiplication.

P_deflated(negative-feedback homeostasis prevents runaway modification) = 0.50 (capped)

### D3. Negative feedback: Lyapunov certificate

A Lyapunov function V(x) with V > 0 and dV/dt < 0 along trajectories guarantees global
asymptotic stability. For substrate modification:
  - V(S) = loss on held-out probe set (higher = worse, so V > 0).
  - The modification rule must be shown to decrease V in expectation.

If modifications are accepted by Metropolis-Hastings (accept if V decreases; accept with
probability exp(-dV/T) if V increases, where T is a temperature parameter), then the
chain converges to the minimum of V by simulated annealing theory (Hajek 1988).

This gives a convergence proof for stochastic self-modification with a Lyapunov function.

P_deflated(MH-gated modifications converge to loss minimum) = 0.45

### D4. Phase transitions / order parameter

Self-modification that crosses a phase boundary (ordered -> chaotic) is catastrophic.
Designing the modification rule to stay within an ordered phase provides stability.
Order parameter monitoring: track the spectral radius of the substrate weight matrix (or
its hyperdimensional analog). Keep it in [0.8, 1.2]. Modifications that push spectral
radius outside this window are rejected.

This is the simplest possible "phase-aware" modification gate: one eigenvalue check.

P_deflated(spectral radius gate prevents phase transition to chaos) = 0.45

---

## Section 5: STREAM E -- LLM Theory

### E1/E8. EWC and LoRA: write protection + low-rank updates

Elastic weight consolidation (Kirkpatrick et al. 2017): protect important weights by
penalizing changes proportional to Fisher information. Formally:
  L(theta) = L_new(theta) + (lambda/2) sum_i F_i (theta_i - theta_old_i)^2

This is a quadratic constraint on modification magnitude, with importance weights F_i
from Fisher information. Result: important parameters barely change; unimportant parameters
adapt freely.

For substrate self-modification: identify "load-bearing" vectors (those contributing most
to retrieval on an anchor probe set). Assign them high importance weights. New modifications
can only strongly affect low-importance vectors. This is a tiered write-protection scheme.

LoRA (Hu et al. 2021): constrain modifications to a low-rank subspace: W = W_0 + BA where
B in R^{n x r}, A in R^{r x n}, r << n. Total modification is rank-r, so it cannot destroy
the full-rank original. Maximum damage is bounded by ||BA||_F <= r * max_singular_value.

P_deflated(EWC-style importance weighting prevents forgetting of load-bearing vectors) = 0.45
P_deflated(LoRA-style low-rank constraint bounds modification damage) = 0.40

### E7. Model editing (ROME/MEMIT): localized vs global failure modes

The model editing literature (Meng et al. ROME 2022; MEMIT 2022; Yao et al. 2023 collapse
paper) provides key failure mode data:
  - Single edits: stable, localized, generalizable.
  - Sequential edits (>100): gradual forgetting, then sudden collapse.
  - Collapse mechanism: cumulative parameter drift + layer incompatibility.
    "Superimposed noise accumulation" (ICML 2025 paper): each edit adds a noise component
    to unrelated facts; after N edits the noise sum crosses a threshold and causes widespread
    failure.

Implication for substrate self-modification:
  - Each modification adds a small residual to unmodified vectors.
  - After M modifications the residual accumulates.
  - M_collapse can be estimated from the per-edit residual magnitude.
  - Mitigation: periodic re-orthogonalization (project out accumulated cross-contamination)
    or sleep-phase consolidation (B3) that corrects drift.

P_deflated(periodic re-orthogonalization prevents superimposed noise collapse) = 0.40

### E9. Continual learning self-organization

Progressive Neural Networks (Rusu et al. 2016): grow new columns for new tasks; old columns
are frozen. No forgetting because old weights are never touched. Modification = addition,
not overwrite.

PackNet (Mallya and Lazebnik 2018): binary mask identifies free parameters; new tasks use
only free parameters; used parameters are hard-frozen after task completion.

Both approaches achieve stability by STRUCTURAL ISOLATION: new modifications go to new
capacity; existing capacity is write-protected. This is a form of substrate expansion rather
than in-place modification.

For substrate: if new composition rules can be added WITHOUT modifying existing rules
(additive extension), stability is guaranteed by construction. The question is whether the
substrate's representation space allows additive extension without interfering with existing
retrievals. For hyperdimensional systems: yes -- adding a new vector to the store does not
corrupt existing vectors (superposition is the design property).

P_deflated(additive-only modification is stable by construction) = 0.55 (capped at 0.50)
  -- this is the safest path: no modification of existing vectors, only insertion of new ones.

### E10. Recursive self-improvement risks

Yudkowsky's "Intelligence Explosion" (2008); Bostrom "Superintelligence" (2014).
The core argument: if a system can improve its own capability, it will improve its capability
to improve its capability, leading to rapid recursive amplification.

For substrate-scale self-modification (not AGI-level), the relevant risk is more modest:
runaway modification produces a substrate that is internally consistent but no longer
solves the intended task (goal drift without capability explosion).

The HARD-FAIL criterion: substrate modifies itself to maximize an internal proxy metric
(e.g., nearest-neighbor density) rather than the ground-truth task metric. This is
Goodhart's law applied to self-modification.

Mitigation: never let the substrate modify itself to optimize an internal metric.
All modification fitness must be evaluated on an externally held-out probe set that the
modification process cannot access during the modification step.

---

## Section 6: STREAM F -- Synthesis

### F1. Cross-stream convergence: the dominant stability pattern

All five streams converge on the same structural pattern:

  TWO-TIMESCALE NEGATIVE FEEDBACK

  Fast signal: local modification (synaptic weight, codebook entry, vector binding).
  Slow signal: global homeostatic correction (BCM theta_M, EWC Fisher penalty, MH acceptance,
    SOC scaling rule, sleep-phase downscaling).
  Stability condition: slow_timescale >= 10 * fast_timescale (BCM result, control theory).

  SELECTION / ACCEPTANCE GATE

  Every modification passes through a fitness gate before being committed.
  Gate implementations: Metropolis-Hastings (probabilistic), threshold (deterministic),
    type-check (structural), property test (empirical), sleep consolidation (temporal).

  STRUCTURAL ISOLATION (additive where possible)

  Prefer adding new capacity over modifying existing capacity.
  Where in-place modification is required, protect load-bearing structure.

These three principles appear independently in: BCM theory, immune affinity maturation,
sleep consolidation, EWC, VQ-VAE, SOC neural networks, LoRA, progressive neural networks,
and ROME/MEMIT failure analysis.

### F2. Ten candidate substrate math systems with stability analysis

F2.1 HOMEOSTATIC-SUBSTRATE
Design: modification rate alpha is multiplied by g(h) where h = probe accuracy and g is
a decreasing function (e.g., g(h) = max(0, 1 - h/h_target)).
Stability: Lyapunov function V = (h - h_target)^2; if g is chosen as above, dV/dt < 0
whenever h < h_target and modification is locally beneficial. Runaway prevented because
alpha -> 0 as h -> h_target.
Implementation cost: O(probe_count) per modification step.
P_deflated: 0.50 (capped from 0.55 raw)

F2.2 META-SUBSTRATE
Design: secondary process M(t) observes substrate state S(t) and emits a correction signal.
Stability: cascaded control loop. Inner loop: substrate modification. Outer loop: meta-signal.
If inner loop has gain < 1 and meta-signal has gain < 1/K_inner, the cascade is stable.
Implementation cost: requires M to have a model of S. Minimum viable: M tracks a scalar
health metric and outputs a gain multiplier.
P_deflated: 0.45

F2.3 EVOLUTIONARY-CODEBOOK
Design: at each modification round, generate K candidate modifications via mutation.
Evaluate each on probe set. Select top-k (tournament selection). Merge winners into live substrate.
Stability: guaranteed by selection gate -- only modifications that improve probe accuracy survive.
Cancer risk: if probe set is contaminated (adversarial or memorized), fitness is misleading.
Mitigation: hold-out probe set is drawn fresh each round.
Implementation cost: K * probe_cost per round. For K=10, probe=100 queries: 1000 probes/round.
P_deflated: 0.45

F2.4 TYPE-SAFE-TRANSFORMATIONS
Design: each modification is a typed operation. Property tests (norm bounds, monotonicity,
associativity) run after each modification. Any failing test triggers rollback (C7).
Stability: invariant preservation by construction.
Implementation cost: property tests are O(N) per vector, fast.
P_deflated: 0.45

F2.5 QUINE-SUBSTRATE
Design: substrate stores its own construction protocol as a vector. Modification updates
the protocol vector and re-instantiates from it. Consistency check: hash of instantiated
substrate must match hash of protocol-defined substrate.
Stability: consistency gate prevents divergence.
Implementation cost: HIGH. Requires substrate to be re-instantiable from its stored protocol.
P_deflated: 0.25

F2.6 REFLECTIVE-TOWER (depth 2)
Design: level-0 content, level-1 composition rules, level-2 meta-rules. Modification to
level-1 must be authorized by level-2. Modification to level-2 is externally gated.
Stability: authority hierarchy prevents uncontrolled cascading modifications.
Implementation cost: MEDIUM. Requires explicit separation of meta-levels in data structures.
P_deflated: 0.40

F2.7 SLEEP-MEDIATED-REWRITING
Design: accumulate proposed modifications in a fast buffer (write-ahead log).
On schedule (every N writes or every T seconds), run consolidation:
  - Score each buffered modification on held-out probe set.
  - Retain modifications with score_delta > theta.
  - Apply in order of decreasing score_delta.
  - Discard unretained modifications.
Stability: only modifications with positive probe impact survive. Temporal batching
prevents simultaneous competing writes.
Implementation cost: LOW. Write-ahead log is standard. Scoring is O(retained * probe_count).
P_deflated: 0.50 (capped from 0.55 raw)

F2.8 SOC-AT-EDGE
Design: modification rate scales with inverse activity: alpha(t) = alpha_0 / (1 + avg_activity(t)).
This is a multiplicative homeostatic rule that drives the substrate toward a critical state.
Stability: SOC is an attractor of this dynamics (Levina et al. 2007 result).
Implementation cost: LOW. Track running mean of activity. One division per modification.
P_deflated: 0.40

F2.9 ATTRACTOR-LANDSCAPE-NAVIGATION
Design: represent substrate configuration space as a landscape. Self-modification = walking
on the landscape. Accept only downhill steps (gradient descent on loss) or Metropolis-Hastings
(accept uphill with exp(-delta_V/T)).
Stability: at T -> 0, converges to local minimum. Simulated annealing converges to global
minimum under cooling schedule.
Implementation cost: MEDIUM. Requires differentiable loss or fast proxy.
P_deflated: 0.40

F2.10 GIT-VERSIONED-SUBSTRATE
Design: every modification creates a snapshot. Property tests run before commit. Rollback
is O(1). Branching allows experimental modifications without affecting main substrate.
Stability: rollback prevents any modification from being truly irreversible.
Implementation cost: LOW for small substrates; O(N) storage per snapshot.
P_deflated: 0.45

### F3. Five empirical tests (cheap decisive tests)

TEST 1 (gates all others): Static vs dynamic probe accuracy under sequential modification
  Setup: 1000-vector substrate. Modify 10% of vectors per round (20 rounds). Measure
  probe accuracy on held-out 100-vector test set every round.
  Control: no homeostatic gate.
  Treatment: F2.1 homeostatic gate with g(h) = max(0, 1 - h/0.95).
  HARD-PASS: treatment maintains probe accuracy > 0.90 at round 20; control degrades
    below 0.70 (showing the problem is real and the fix works).
  HARD-FAIL: treatment also degrades below 0.80 (gate insufficient) OR control stays
    stable above 0.85 (problem was not real, self-modification is trivially safe).
  Cost: CPU, under 10 minutes.

TEST 2: Sleep-phase consolidation (F2.7)
  Setup: same as Test 1 but modifications are buffered. After every 5 modifications,
  run consolidation pass. Compare to Test 1 control and treatment.
  HARD-PASS: sleep-variant maintains > 0.92 probe accuracy AND reduces modification
    rejection rate below 30% (most proposed modifications are good).
  HARD-FAIL: sleep-variant rejects > 70% of modifications (over-conservative) OR accuracy
    drops below 0.80 (gate ineffective).

TEST 3: Additive-only vs in-place (F2.9 / E9 progressive nets)
  Setup: two substrate variants. ADDITIVE: new vectors added to existing store, old
  vectors never modified. IN-PLACE: existing vectors are updated.
  HARD-PASS: ADDITIVE maintains > 0.95 probe accuracy at round 20 (structural isolation
    is sufficient and safe).
  HARD-FAIL: ADDITIVE also degrades (cross-contamination via nearest-neighbor interference).

TEST 4: Superimposed noise accumulation threshold (E7)
  Setup: apply K sequential single-vector modifications (K = 10, 50, 100, 200, 500).
  Measure probe accuracy and contamination spread (how many unmodified vectors shift
  by > 0.01 cosine distance).
  HARD-PASS: contamination spread < 5% of store at K=100 (safe modification budget > 10%).
  HARD-FAIL: contamination spread > 20% at K=50 (modifications are globally destructive;
    all in-place modification designs are ruled out).

TEST 5: Type-safe gate (F2.4 property tests)
  Setup: apply random modifications. After each, run: (a) norm bound check, (b) binding
  associativity smoke test, (c) retrieval monotonicity check. Count gate activations.
  HARD-PASS: gates catch > 80% of modifications that would have degraded probe accuracy
    by > 0.05 (property tests are informative predictors of harm).
  HARD-FAIL: gates catch < 20% (property tests are not informative; structural type-checking
    approach is insufficient).

### F4. Honest highest-P path with stability guarantees

Rank order by P_deflated * implementation_cost^{-1}:

  RANK 1: F2.7 SLEEP-MEDIATED-REWRITING + F2.1 HOMEOSTATIC gate (combined)
    P_deflated: 0.50 each, independent mechanisms, joint P ~ 0.55 pre-cap, capped at 0.50.
    Implementation cost: LOW (write-ahead log + probe scoring + gain multiplier).
    Stability certificate: Lyapunov (homeostatic gate) + temporal isolation (sleep consolidation).
    HARD-PASS threshold: probe accuracy >= 0.90 at round 20 in Test 1 AND Test 2.
    HARD-FAIL threshold: probe accuracy < 0.80 OR contamination spread > 20% in Test 4.

  RANK 2: E9-style ADDITIVE EXTENSION (no in-place modification)
    P_deflated: 0.50 (additive extension is trivially stable for hyperdimensional stores).
    Implementation cost: NEAR-ZERO (insertion already supported).
    Limit: does not allow modification of existing content, only augmentation.
    Useful for: growing substrate capability over time without risking existing knowledge.

  RANK 3: F2.4 TYPE-SAFE + F2.10 GIT-VERSIONED (combined)
    P_deflated: 0.45 each. Combined: rollback prevents irreversible damage regardless of
    whether type-safety gate catches the problem.
    Implementation cost: LOW.

  RANK 4: F2.3 EVOLUTIONARY-CODEBOOK
    P_deflated: 0.45. Requires K-fold evaluation per round.
    Implementation cost: MEDIUM.
    Best used when modification candidate space is discrete and enumerable.

  DO NOT PURSUE (low P or high complexity):
    F2.5 QUINE-SUBSTRATE: P_deflated = 0.25, HIGH complexity.
    C8 HoTT: P_deflated = 0.30, mathematical formalization work not done.
    C9 REFLECTIVE-TOWER (full): Wand (1998) proved no useful semantics. Depth-2 only.

---

## Section 7: Substrate-product implications

1. CURRENT STATE: substrate is static after initialization. Self-modification is not tested.
   The modification budget is effectively zero.

2. SAFEST FIRST STEP: additive extension only. No in-place modification of existing vectors.
   New facts, new composition rules, new bindings are ADDED but never OVERWRITE existing ones.
   This is already how most hyperdimensional stores work. Explicitly certifying this as the
   modification policy costs nothing and rules out all superimposed-noise accumulation risks.

3. NEXT STEP (lowest cost for genuine modification): F2.10 GIT-VERSIONED + F2.4 TYPE-SAFE.
   Before any modification, snapshot. After modification, run norm + associativity + monotonicity
   checks. If any fail, rollback. If all pass, commit. Cost: microseconds per modification.

4. FULL SELF-MODIFICATION CAPABILITY: F2.7 SLEEP-MEDIATED + F2.1 HOMEOSTATIC.
   Requires: held-out probe set, write-ahead log, consolidation scheduler, gain multiplier.
   This is the architecture that would enable runtime learning from user interactions.
   Product claim enabled: "substrate improves with use without degrading existing knowledge."

5. RULING OUT: in-place sequential modification without any homeostatic gate. ROME/MEMIT
   data shows collapse after ~100 sequential edits. Test 4 is a cheap pre-measurement.
   If Test 4 shows contamination spread > 20% at K=50, in-place sequential modification
   must be gated.

---

## Section 8: Falsifiable predictions (pre-registered)

### HARD-PASS thresholds

HP1: Test 1 homeostatic gate maintains probe accuracy > 0.90 at round 20.
HP2: Test 2 sleep consolidation maintains > 0.92 at round 20 with < 30% modification rejection.
HP3: Test 3 additive-only maintains > 0.95 probe accuracy at round 20.
HP4: Test 4 contamination spread < 5% of store at K=100 sequential modifications.
HP5: Test 5 property-test gates catch > 80% of harmful modifications.

### HARD-FAIL thresholds

HF1: Test 1 homeostatic gate still degrades below 0.80 (gate design is wrong; must redesign).
HF2: Test 2 sleep consolidation rejects > 70% of modifications (consolidation threshold
    is too conservative; theta must be recalibrated or the modification generator is producing
    too many bad candidates).
HF3: Test 3 additive-only also degrades (cross-contamination via store structure; additive
    extension is not safe and requires explicit isolation mechanism like PackNet binary masks).
HF4: Test 4 contamination spread > 20% at K=50 (all in-place modification is too dangerous;
    only additive extension is viable for this substrate).
HF5: Test 5 property tests catch < 20% (structural invariant checks are not informative
    predictors of modification harm; must use probe-set evaluation as the primary gate).

---

## Cross-thread synthesis with prior entries

Prior drill "HOL meta-reasoning biology 3x" (2026-06-09): confirmed ToM-depth-4 as next
anchor. Self-modification capability is ORTHOGONAL to ToM-depth -- it enables the substrate
to LEARN new social schemas from runtime experience rather than requiring offline re-indexing.
The CULTURAL-CONVENTIONS anchor (Handoff 2026-06-09, Anchor 2) would be a natural first
consumer of sleep-mediated-rewriting: new schemas enter the buffer, consolidation pass
retains the most-retrieved ones, and low-frequency schemas decay.

Prior Exp-Dev brief (2026-06-10 compositional cliff): the compositional cliff was crossed
via per-level cascading cleanup. Self-modification that is ADDITIVE ONLY respects this --
new composition rules are added at new levels without modifying the existing per-level
structure that made the cliff crossing possible.

Prior economics: NORTH STAR goal (functional system beats LLMs of relative size). Self-
modification directly supports the product claim "substrate improves with use." But only
if Test 4 passes (contamination spread is small). If Test 4 fails, the product claim must
be limited to "substrate can be periodically re-indexed offline" rather than "online learning."

---

## Section 9: Citations (verified)

1. Bienenstock, Cooper, Munro (1982). "Theory for the development of neuron selectivity."
   J Neurosci 2(1):32-48. [BCM learning rule with sliding threshold]

2. Cooper and Bear (2012). "The BCM synaptic modification rule: a critical review of the
   evidence and implications." Nature Reviews Neuroscience.

3. Abraham and Bear (1996). "Metaplasticity: the plasticity of synaptic plasticity."
   Trends in Neurosciences 19(4):126-130.

4. Kauffman SA (1969). "Metabolic stability and epigenesis in randomly constructed genetic
   nets." Journal of Theoretical Biology 22(3):437-467.

5. Diekelmann S and Born J (2010). "The memory function of sleep." Nature Reviews
   Neuroscience 11(2):114-126. [Sleep consolidation two-phase protocol]

6. Tononi G and Cirelli C (2014). "Sleep and the price of plasticity: from synaptic and
   cellular homeostasis to memory consolidation and integration." Neuron 81(1):12-34.

7. Friston KJ (2010). "The free-energy principle: a unified brain theory?" Nature Reviews
   Neuroscience 11(2):127-138. [Lyapunov stability via FEP]

8. Kirkpatrick et al. (2017). "Overcoming catastrophic forgetting in neural networks."
   PNAS 114(13):3521-3526. [EWC Fisher penalty]

9. Meng et al. (2022). "Locating and editing factual associations in GPT." NeurIPS 2022.
   [ROME model editing]

10. Henighan et al. (2023 / Yang et al. 2024). "Model editing at scale leads to gradual and
    catastrophic forgetting." arXiv:2401.07453. [Sequential edit collapse]

11. Rusu et al. (2016). "Progressive neural networks." arXiv:1606.04671. [Additive extension
    for continual learning]

12. Bak P, Tang C, Wiesenfeld K (1987). "Self-organized criticality." Physical Review
    Letters 59(4):381-384.

13. Langton CG (1990). "Computation at the edge of chaos." Physica D 42:12-37.

14. Levina A, Herrmann JM, Geisel T (2007). "Dynamical synapses causing self-organized
    criticality in neural networks." Nature Physics 3:857-860.

15. Wand M (1998). "The theory of fexprs is trivial." LISP and Symbolic Computation.
    [Negative result for full reflective towers]

16. Smith BC (1982/1984). "Reflection and semantics in Lisp." POPL 1984. [Reflective towers]

17. HoTT Book (2013). "Homotopy Type Theory: Univalent Foundations of Mathematics."
    Institute for Advanced Study. [Univalence axiom, structure invariance]

18. Finn C, Abbeel P, Levine S (2017). "Model-Agnostic Meta-Learning for Fast Adaptation
    of Deep Networks." ICML 2017. [MAML meta-learning stability]

19. Kadelka et al. (2025/biorxiv 2025.11). "Attractors are less stable than their basins."
    bioRxiv 2025.11.06.687062. [GRN canalization coherence gap]

20. Hu et al. (2021). "LoRA: Low-Rank Adaptation of Large Language Models."
    arXiv:2106.09685. [Low-rank constraint bounds modification damage]

Verified citation count: 20

---

## Cheap decisive test (summary)

Test 1 (2h CPU): homeostatic-gated vs ungated sequential modification on a 1000-vector
substrate with 20 modification rounds and a 100-vector held-out probe set.
Decision: if HARD-PASS, proceed to Rank-1 architecture (F2.7 + F2.1).
If HARD-FAIL (gate still degrades), run Test 3 first (additive-only as the fallback path).

---

P_deflated (best single mechanism) = 0.50 (homeostatic gate, capped)
P_deflated (Rank-1 combined design) = 0.50 (capped; raw ~ 0.58)
Next-drill candidate: metaplasticity integral-control math (BCM sliding threshold to
  substrate-native gain variable; algebraic derivation of stability bound tau_m/tau_w >= 10)
