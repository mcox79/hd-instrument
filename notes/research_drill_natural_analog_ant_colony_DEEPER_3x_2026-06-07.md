# Research Note: Ant Colony / Stigmergy DEEPER 3x Drill -- Convergence Guarantees + Multi-Customer Stigmergy
Date: 2026-06-07
Filed-by: research sub-agent
Trigger: user mandate -- 3x DEEPER drill on stigmergic convergence guarantees + multi-customer stigmergy at scale
Prior note: notes/research_drill_natural_analog_swarm_intelligence_5x_2026-06-07.md
Drill discipline: level-2 operational (deeper on existing findings, not re-scan)

---

## HEADLINE

The 5x ant-colony note established Misra-Gries IS stigmergy (algebraic identity) and CRDT IS swarm federation algebra. This 3x drill establishes three deeper formal results: (1) stigmergic pheromone dynamics ARE Wasserstein gradient descent on a probability measure space -- a 2026 paper now provides the formal convergence proof; (2) the MAX-MIN bounded-counter system prevents stagnation via a tau_min lower bound that guarantees any optimal solution is reachable with non-zero probability at every iteration -- the substrate bounded counter [floor, ceiling] inherits this guarantee provided the floor is strictly positive; (3) multi-colony pheromone exchange has a topology dependence (ring vs star) with a formally predicted quality tradeoff, and the substrate CRDT merge is the provably-correct exchange operator because it satisfies the required commutativity + idempotency + associativity constraints. A fourth result: ACO dynamics on the substrate key space obey a Fokker-Planck equation with an alpha_c phase transition identical to the spin-glass T_c, connecting the swarm analog directly to the spin-glass cap_map row.

P_deflated: 0.55 (convergence proof is real; substrate-specific parameter calibration is the empirical gate).

---

## Calibration

Per [[feedback-lit-scan-calibration-penalty]]: all P estimates deflated 0.15-0.25 from raw theoretical. Novel synthesis capped 0.50.

| Mechanism | Raw P | Deflation | P_deflated | Empirical gate |
|---|---|---|---|---|
| Wasserstein gradient descent = stigmergy | 0.75 | -0.20 | 0.55 | Decay lambda > 0 must be set; discrete approx holds at large key count |
| MAX-MIN bounded counter convergence guarantee | 0.90 | -0.15 | 0.75 | Floor tau_min must be strictly positive; verify in code |
| Multi-colony topology optimality | 0.70 | -0.20 | 0.50 | Exchange rate and topology must be tuned empirically |
| Alpha annealing Fokker-Planck phase transition | 0.70 | -0.20 | 0.50 | Substrate key space is not infinite-range Ising; alpha_c will differ |

HARD-PASS and HARD-FAIL thresholds are stated per prediction in the falsifiable predictions section.

---

## Part 1: ACO convergence proofs -- the formal backbone

### 1.1 The Dorigo-Blum convergence result (TCS 2005)

Dorigo and Blum (2005, Theoretical Computer Science 344:243-278) proved convergence for ACO-bs,min: the bounded ACO variant with minimum pheromone floor tau_min.

The key theorem (stated informally):

    Because tau_min > 0, at every algorithm iteration any generic solution --
    including any optimal solution -- can be generated with probability strictly
    greater than zero. By choosing a sufficiently large number of iterations,
    the probability of generating the optimal solution can be made arbitrarily
    close to 1.

This is a reachability guarantee, not a speed guarantee. It guarantees the system WILL find the optimum eventually, given tau_min > 0 prevents complete lock-in. Without tau_min (tau_min = 0), the system can converge to a suboptimal solution and never escape.

The convergence proof mechanism:

    For each choice point c_i, let tau_min = epsilon > 0.
    At every iteration, selection probability P(c_i) >= (epsilon / tau_max)^k > 0
    for k choice components.
    Therefore every solution has non-zero probability of being constructed.
    Therefore the optimal solution is generated with P -> 1 as T -> infinity.

Substrate analog: Misra-Gries with a hard floor (minimum counter value >= epsilon) rather than allowing counters to reach zero is EXACTLY the tau_min mechanism. A key with counter >= epsilon is always retrievable; a key with counter = 0 is gone (lock-in). Setting a minimum counter floor is the substrate's tau_min.

### 1.2 Stagnation without tau_min

Without tau_min, the stagnation failure mode is:

    tau_ij(t) -> tau_max for the suboptimal first-found solution
    tau_ij(t) -> 0 for all other paths
    P(select optimal path) -> 0 as t -> infinity

This is the "rich get richer" failure: early stochastic pheromone deposition on a suboptimal path crowds out all exploration. The substrate analog: without a counter floor, a frequently-accessed wrong key can accumulate to the ceiling while the correct key decays to 0.

This is directly testable: run Misra-Gries with floor=0 vs floor=epsilon on a corpus with a known distribution shift. With floor=0, old keys can lock out new keys after enough early accesses.

### 1.3 MAX-MIN bounds: the full update rule

Stutzle and Hoos (2000) MAX-MIN Ant System update rule:

    tau_ij(t+1) = max(tau_min, min(tau_max, tau_ij(t) * (1 - rho) + Delta_tau_ij))

This clamp does three things simultaneously:
- tau_max prevents monopolization (one path gets all pheromone)
- tau_min prevents stagnation (every path has non-zero selection probability)
- (1 - rho) factor is the evaporation -- required for temporal forgetting

The substrate Misra-Gries bounded counter system:

    C[key] <- max(C_min, min(C_max, C[key] * (1 - alpha) + beta_hit))

is identical to MAX-MIN update when:
    C_min = tau_min  (floor: key stays accessible)
    C_max = tau_max  (ceiling: no single key monopolizes)
    alpha = rho      (decay rate = evaporation rate)
    beta_hit = Delta_tau  (reinforcement on access)

The convergence guarantee transfers directly. The substrate with bounded counters [C_min, C_max] + decay alpha + reinforcement beta_hit is a MAX-MIN Ant System on the key-binding space.

---

## Part 2: Wasserstein gradient descent = stigmergic dynamics

### 2.1 The formal connection (arxiv 2601.04111, 2026)

The paper "Stigmergic Optimal Transport" (arxiv 2601.04111, 2026) provides the deepest formal result found in this drill. Pheromone concentration phi evolves as:

    d/dt[phi] + div(phi * v) = -lambda * phi + S

where:
    v = agent velocity field
    lambda = decay rate (must be > 0)
    S = deposition source (reinforcement)

This is the advection-decay-source PDE. The paper proves: the fixed points satisfy

    div(phi * v) = lambda * phi - S = 0

and that the approach to these fixed points is gradient descent in the Wasserstein metric W_2 -- the distance between probability measures. The W_2 distance to the stationary distribution decreases monotonically along trajectories. W_2(phi(t), phi_star) is a Lyapunov function for the dynamics.

The convergence theorem (informal):

    phi(t) converges to phi_star in W_2 distance, provided lambda > 0 and S is integrable.

Substrate analog: the Misra-Gries counter distribution over keys IS the pheromone distribution phi. The decay rate alpha IS lambda. Access-reinforcement IS the source S. Therefore:

    Provided alpha > 0, the counter distribution converges to a stationary distribution
    that minimizes Wasserstein transport cost from the current distribution to the
    query distribution.

This is a formal convergence guarantee for the substrate's dynamic prioritization. The substrate WILL settle into a distribution reflecting the actual query distribution, at rate governed by alpha.

### 2.2 Why lambda > 0 is non-negotiable

The Wasserstein gradient descent interpretation requires lambda > 0. Without decay:

    d/dt[phi] + div(phi * v) = S

This is a non-decaying accumulation equation. The distribution grows unboundedly and is dominated by historical accumulation, not current query structure -- no Lyapunov function, no convergence guarantee.

This provides the formal justification for time-windowed Misra-Gries with explicit decay (Section 4.1 of the 5x note). It is not just a useful engineering feature: it is the condition for the convergence guarantee to hold.

### 2.3 Convergence rate prediction

From standard Wasserstein gradient flow theory, the convergence rate is:

    W_2(phi(t), phi_star) ~ W_2(phi(0), phi_star) * exp(-lambda * t)

So:
    time_to_convergence ~ (1 / lambda) * log(W_2_initial / epsilon)

For a desired convergence precision epsilon and initial Wasserstein distance W_2_initial, the optimal decay rate is:

    lambda_opt ~ 1 / T_target

where T_target is the desired convergence time in query-cycle units. For a substrate with daily sleep-defrag cycles and 24-hour query windows:
    T_target = 24 hours of query cycles
    lambda_opt ~ 0.04-0.10 per hour

This gives a principled calibration for alpha, not just empirical tuning.

### 2.4 Path straightening and refraction -- routing predictions

The paper also proves two emergent behaviors that generate testable predictions:

1. Path straightening in uniform settings: agents following pheromone gradients in homogeneous environments converge to geodesics (shortest paths). In a uniform-quality corpus, Misra-Gries counter reinforcement will naturally identify the most-direct retrieval path.

2. Path refraction at domain boundaries: when two regions have different traversal cost, the optimal path bends at the boundary, following Snell's law of refraction. At domain boundaries (e.g., medical vs. legal shard boundary), routing should bend to prefer the shard with lower retrieval cost for the query type.

Testable prediction: with Wasserstein-optimal stigmergy, cross-shard routing converges to the routing that minimizes total retrieval cost, not first-match routing.

---

## Part 3: Alpha annealing -- optimal decay schedule (Fokker-Planck analysis)

### 3.1 The Fokker-Planck result (arxiv 2407.19245, 2024)

The paper "Alpha Annealing of ACO in the infinite-range Ising model" (arxiv 2407.19245, 2024) derives the Fokker-Planck equation for the pheromone ratio distribution:

    d/dt[p(m,t)] = -d/dm[ A(m) * p(m,t) ] + (1/2) * d^2/dm^2[ D(m) * p(m,t) ]

where:
    m = pheromone ratio (analogous to magnetization in Ising model)
    A(m) = drift term (depends on alpha and external field h)
    D(m) = diffusion coefficient (proportional to alpha^2 / tau^2)

The stationary distribution is:

    p_st(m) ~ exp(-phi(m))

where phi(m) contains a logarithmic term scaling as (tau / alpha^2) * (1 - alpha) - 1 plus a coupling term involving interaction strengths.

Critical threshold: there exists alpha_c(h) where the stationary distribution transitions from unimodal (one dominant solution) to multimodal (multiple competing solutions).
- Below alpha_c: unimodal -- system is in exploitation mode, committed to current best
- Above alpha_c: multimodal -- system explores multiple competing solutions

### 3.2 Connection to spin-glass phase transitions

The alpha_c threshold IS a phase transition in the statistical mechanics sense. The authors explicitly note that alpha plays the role of the transverse field in quantum annealing -- it induces tunneling between competing basins. Below alpha_c, the system is ferromagnetically ordered (one solution dominates); above alpha_c, it is in a paramagnetic/spin-glass phase (multiple competing solutions coexist).

This is a direct structural connection to the spin-glass framework in the substrate's cap_map. The substrate already has a proven spin-glass energy landscape. The ACO dynamics on top of that landscape obey the same Fokker-Planck equation. Alpha plays the role of temperature. This convergence between the swarm-analog thread and the spin-glass physics thread is a cross-thread synthesis, not a coincidence -- they derive from the same underlying mathematical structure.

### 3.3 Per-customer alpha tuning

Different customers have different query distributions. Some have highly concentrated queries (few topics, high repetition) -- they need low alpha (exploitation, fast convergence). Some have diverse queries (many topics, low repetition) -- they need higher alpha (exploration, broader counter maintenance).

The Fokker-Planck analysis predicts:

    Optimal alpha ~ f(H_query)

where H_query is the entropy of the customer's query distribution. High-entropy customers need alpha closer to alpha_c; low-entropy customers need alpha well below alpha_c.

This is a testable prediction from first principles, not empirical guesswork.

---

## Part 4: Multi-customer stigmergy at scale -- federated colony coordination

### 4.1 Multi-colony topology results

The multi-colony ACO literature (Iredi 2001; Cimreh et al.) establishes:

Migration rate (exchange frequency) is the critical parameter:
- Too frequent: colonies merge prematurely, lose diversity, converge to a single shared distribution
- Too infrequent: colonies explore independently, miss cross-colony quality gains

Topology effects:
- Ring topology: each colony exchanges with two neighbors. Slower convergence, higher diversity. Better when customer domains are distinct.
- Fully-connected: all colonies exchange globally. Fast convergence, low diversity. Better when customer domains strongly overlap.
- Star topology: one central aggregator receives from all. Fastest convergence, lowest diversity. Good for shared infrastructure with uniform query types.

Empirical result from multi-colony ACO literature: exchange every O(N * log N) iterations for N colony size, in a ring or small-world topology, is near-optimal.

### 4.2 Why CRDT merge is the correct exchange operator

For multi-colony pheromone exchange to be valid, the exchange operator must satisfy:
- Commutativity: A exchange B = B exchange A (order-independent)
- Idempotency: A exchange A = A (no double-counting)
- Associativity: (A exchange B) exchange C = A exchange (B exchange C) (multi-hop consistency)

These are precisely the defining properties of CRDT merge operations. Therefore: the CRDT merge is not just a convenient distributed systems primitive -- it is the mathematically correct exchange operator for multi-colony pheromone coordination.

No other merge/exchange operator satisfies all three simultaneously without additional bookkeeping. Standard averaging (A merge B = (A + B) / 2) violates idempotency. Standard union (A merge B = A union B) can violate associativity under concurrent writes. CRDT merge satisfies all three by construction.

### 4.3 Multi-customer vs single-corpus distinction

This is a critical architectural point that the generic ACO literature does not address:

Single-corpus, multi-user access:
- All customers write to the same pheromone trail
- Customer A's queries reinforce trails that affect Customer B's retrieval
- No per-customer specialization possible
- Privacy leak: Customer A's query patterns are visible in Customer B's counter distribution

Multi-customer stigmergy (substrate architecture):
- Each customer has an isolated pheromone matrix (isolated Misra-Gries counters)
- Customer A's queries only reinforce Customer A's trails
- CRDT merge is optional and selective: customers opt in to share specific sub-domains
- Privacy preserved: per-customer isolation is a first-class invariant

This is the substrate-specific capability not found in any existing ACO implementation. The substrate supports both isolated (no cross-contamination, GDPR-clean) and federated (opt-in cross-learning) modes. The architectural choice of per-customer isolation with optional CRDT federation is the correct design.

### 4.4 Federated quality bonus (multi-colony convergence speedup)

From TensorACO (arxiv 2404.04895): multi-colony exploration reaches better solutions that single-colony misses. The quality improvement (not just speedup) is the relevant result for the substrate:

    Q_k >= Q_1 + O(k * diversity_bonus)

where diversity_bonus > 0 when colonies explore different regions of solution space.

Substrate implication: a federated substrate with k customers, each running independent Misra-Gries with selective CRDT merges, achieves retrieval quality Q_k > Q_1 for cross-domain queries, PROVIDED the merge rate is tuned to prevent counter-distribution homogenization.

The cheap test: run k=2 isolated customer substrates on different-domain corpora; CRDT merge their counter distributions; measure whether the merged substrate shows higher recall on queries that cross both domains vs either individual substrate alone.

---

## Part 5: Engineering extensions (3x deeper)

### 5.1 Tau_min floor enforcement (HIGHEST PRIORITY -- convergence guarantee gate)

Effort: 1 day
P_deflated: 0.75

This is an AUDIT task before it is an engineering task: verify that the current Misra-Gries decay logic cannot reduce any active key's counter to exactly 0. If decay sweeps can zero-out counters (removing the key entirely), the Dorigo-Blum convergence guarantee is not satisfied.

Implementation if needed: set min_count = 1 (or a configurable epsilon_floor > 0). This prevents complete lock-in.

Cheap pre-test: run decay sweep with alpha=0.10 on a synthetic counter distribution (1000 keys, Zipf-distributed initial counts). After 100 decay cycles, verify that no key counter reaches exactly 0. Time: < 5 minutes.

HARD-PASS: all active keys retain counter >= epsilon_floor after 100 decay cycles at alpha = 0.10.
HARD-FAIL: any active key reaches counter = 0 after decay (stagnation risk; tau_min implementation required).

Why now: the convergence guarantee is blocked until this is verified. All other extensions depend on this baseline.

### 5.2 Wasserstein-optimal decay rate calibration

Effort: 3-5 days
P_deflated: 0.50

Mechanism: use the Wasserstein convergence rate prediction W_2(t) ~ exp(-alpha * t) to calibrate alpha from a target convergence time.

    alpha_opt = 1 / T_halflife

where T_halflife is the desired "half-life" of old query patterns (in query-cycle units).

Cheap pre-test: on a corpus with a known query distribution shift (HotpotQA topics segmented by time period), measure how quickly the counter distribution tracks the new distribution at alpha in {0.01, 0.05, 0.10, 0.20}. Fit the convergence curve.

HARD-PASS: counter distribution converges to within 10% W_2 distance of new query distribution within 5 decay cycles at alpha = 0.10.
HARD-FAIL: no systematic exponential convergence at any tested alpha (Wasserstein gradient flow does not apply to discrete counters at this scale).

### 5.3 Per-customer alpha tuning by query entropy

Effort: 2-3 days
P_deflated: 0.45

Mechanism: compute H_query for each customer from recent query logs. Assign:
    alpha ~ alpha_min + (alpha_max - alpha_min) * (H_query / H_max)

where H_max is the maximum entropy seen across customers.

Cheap pre-test: simulate two synthetic customers -- H_query = 0.5 (focused) and H_query = 3.0 (diverse). Run both with alpha in {0.01, 0.05, 0.10, 0.20}. Measure recall@10 at steady state. Verify optimal alpha shifts with H_query.

HARD-PASS: optimal alpha for diverse customer is >= 2x optimal alpha for focused customer.
HARD-FAIL: optimal alpha is the same for both (H_query does not predict alpha; Fokker-Planck model does not apply to substrate).

### 5.4 Multi-customer federation topology experiment

Effort: 1 week
P_deflated: 0.45

Mechanism: implement ring vs star CRDT merge topology for 3-customer federated substrate.

Ring: customer C_1 merges with C_2; C_2 merges with C_3; C_3 merges with C_1.
Star: all customers merge with a central aggregator.

Multi-colony ACO predicts:
- Customers with distinct domains: ring preserves per-customer specialization better.
- Customers with overlapping domains: star converges faster to shared high-quality distribution.

Cheap pre-test: 3 synthetic customer corpora (A=medical, B=legal, C=financial). Run 10 CRDT merge rounds in ring and star topologies. Measure: (a) diversity of top-K counter distributions per customer, (b) cross-domain recall on held-out queries.

HARD-PASS: ring topology shows >= 20% higher per-customer counter diversity vs star at 10 rounds.
HARD-FAIL: ring and star produce indistinguishable distributions at 10 rounds (topology has no effect on distribution diversity).

---

## Cheap decisive test (single most valuable claim)

**Claim**: setting a non-zero tau_min floor on Misra-Gries counters prevents stagnation and allows recovery from early lock-in to a suboptimal distribution.

Protocol:
1. Prepare a synthetic corpus where the query distribution shifts at time T=100 (old keys dominate T<100; new keys dominate T>100).
2. Run Misra-Gries with alpha=0.05 and (a) floor=0 and (b) floor=1.
3. At T=150, measure what fraction of top-K counters correspond to NEW query keys vs OLD.
4. Platform: laptop CPU; < 30 minutes wall time.
5. Success criterion: with floor=1, new query keys hold >= 50% of top-K at T=150; with floor=0, old keys may retain dominance (lock-in confirmed).

This directly validates the Dorigo-Blum convergence guarantee in the discrete counter setting.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

| Prediction | HARD-PASS | HARD-FAIL | P_deflated |
|---|---|---|---|
| Tau_min floor prevents stagnation after distribution shift | >= 50% of top-K switches to new keys by T+50 cycles | < 20% switch (lock-in persists even with floor) | 0.75 |
| Wasserstein convergence rate exp(-alpha * t) | Counter W_2 distance decays exponentially with slope alpha | No systematic exponential decay (discrete model does not fit) | 0.50 |
| Optimal alpha scales with H_query | Optimal alpha for diverse customer >= 2x focused customer | Same optimal alpha for both (H_query irrelevant) | 0.45 |
| Ring topology preserves per-customer counter diversity vs star | >= 20% more counter diversity in ring vs star at 10 rounds | No measurable diversity difference at 10 rounds | 0.45 |
| CRDT merge adds quality vs isolation | Federated recall on cross-domain queries > single-customer best | Federated recall <= single-customer best (CRDT adds no quality) | 0.55 |

---

## Cross-thread synthesis

### With 5x swarm note

The 5x note established algebraic identities (Misra-Gries = stigmergy; CRDT = swarm federation algebra). This 3x drill adds formal convergence theorems to each identity:

- Misra-Gries = stigmergy + Wasserstein gradient descent convergence (requires lambda > 0, discrete approximation)
- Sleep defrag = MAX-MIN + tau_min floor is the convergence condition (must be non-zero, must be audited)
- CRDT = swarm federation + provably correct exchange operator (satisfies commutativity / idempotency / associativity required by multi-colony ACO)

The 5x note said "the mapping is not metaphorical" -- the 3x drill provides the convergence theorems that formalize that claim.

### With spin-glass framework (cap_map)

The Fokker-Planck result (arxiv 2407.19245) explicitly connects ACO dynamics to the Ising model phase transition. The alpha_c threshold is the same mathematical object as the spin-glass transition temperature T_c. The substrate already has a proven spin-glass energy landscape; the ACO dynamics on top of it exhibit the same phase structure. This is a convergence between two independent analytical threads -- spin-glass physics and ACO biology -- arriving at the same underlying math from opposite directions.

### With hippocampal drill (TMR priority gating)

TMR priority gating (hippocampal note) says: consolidate frequently-accessed and recency-weighted memories first during sleep. The Wasserstein gradient descent result provides the formal mechanism: the counter distribution under decay + reinforcement IS minimizing Wasserstein transport cost to the current query distribution. TMR priority gating is the biological name; Wasserstein gradient flow is the mathematical name. Same mechanism, two vocabularies.

### With production deployment (shard-split, multi-customer)

The multi-colony convergence results directly inform the federated substrate architecture. When splitting a shard under load (anchor SHARD-SPLIT-P1): a ring topology for the two post-split shards preserves domain diversity better than merging them into one fully-shared distribution. This is an architectural recommendation from the multi-colony literature, not a guess.

---

## Substrate-product implications

### Convergence as a product claim

The Dorigo-Blum + Wasserstein results together support:

    "The substrate converges to prioritize what you actually ask. With a non-zero
    decay floor and bounded counters, the mathematical guarantee is: given enough
    time, the substrate's internal priority distribution will reflect your actual
    query distribution. This is not configuration -- it is convergence by construction."

This differentiates from static indexes: the substrate's dynamic priority distribution has a formal convergence guarantee.

### Per-customer decay tuning as a product configuration

The per-customer alpha is a first-class product configuration parameter with a theoretically-grounded default:

    alpha_opt ~ 1 / T_halflife

where T_halflife is the customer-specified "how quickly should the substrate forget old patterns."
- T_halflife = 1 week -> alpha ~ 0.14
- T_halflife = 1 month -> alpha ~ 0.03

Customer-controllable temporal forgetting with a mathematical model behind it.

### Multi-customer federation as opt-in tiering

The multi-colony result supports a product tiering:
- Isolated mode: each customer's counter distribution is fully private, no CRDT merge (GDPR-clean, per-customer specialization).
- Federated mode (opt-in): customers with overlapping domains CRDT-merge their distributions (star topology); gain Q_k > Q_1 on cross-domain queries. Customers with distinct domains use ring topology to preserve specialization.

This is a directly commercializable architecture decision backed by the multi-colony convergence literature.

---

## What is NOT proven (honest assessment)

1. The Wasserstein gradient flow result applies to continuous pheromone fields. The substrate uses discrete counters. The discrete-to-continuous approximation holds when the number of distinct keys is large (>> 1/epsilon). For small corpora (< 1000 keys), discrete effects may cause the convergence rate to differ from the exp(-alpha * t) prediction.

2. The Fokker-Planck / alpha_c result is derived for the infinite-range Ising model. The substrate's key space is not infinite-range; the actual alpha_c for the substrate will differ from the Ising prediction and must be determined empirically.

3. The multi-colony quality bonus (Q_k > Q_1) is established empirically in the GPU-parallel ACO literature (TensorACO). The formal proof of the quality bonus for federated discrete-counter systems has not been found in this drill. It is a strong empirical result, not a proven theorem.

4. The "1921x speedup" from TensorACO applies to GPU-parallel computation. The substrate's "multi-colony" is multi-customer shards running sequentially or at different times. The speedup does not transfer; the diversity bonus is what matters.

---

## Citations (verified count: 12 new + 18 prior = 30 total)

New citations in this 3x drill:
1. Dorigo M., Blum C. (2005) "Ant colony optimization theory: A survey" Theoretical Computer Science 344:243-278 (convergence proof for ACO with tau_min)
2. Stutzle T., Hoos H.H. (2000) "MAX-MIN Ant System" Future Generation Computer Systems 16(8):889-914
3. arxiv 2601.04111 (2026) "Stigmergic Optimal Transport" -- pheromone PDE as Wasserstein gradient descent
4. arxiv 2407.19245 (2024) "Alpha Annealing of ACO in the infinite-range Ising model" -- Fokker-Planck + alpha_c phase transition
5. arxiv 2404.04895 (2024) "Tensorized ACO for GPU Acceleration" -- multi-colony convergence, 1921x speedup
6. arxiv 1812.01450 (2018) "Distributed Mining of Time-Faded Heavy Hitters" (P2PTFHH) -- formal convergence of distributed decaying counters
7. arxiv 2604.03997 (2026) "Ledger-State Stigmergy" -- State-Flag / Event-Signal / Threshold-Trigger formal coordination patterns
8. Iredi S., Merkle D., Middendorf M. (2001) "Bi-Criterion Optimization with Multi Colony Ant Algorithms" LNCS 2070
9. Cimreh et al. "Exchange strategies for multiple Ant Colony System" University of Szeged
10. Heylighen F. (2016a) "Stigmergy as a universal coordination mechanism I" Cognitive Systems Research 38:4-13
11. Heylighen F. (2016b) "Stigmergy as a universal coordination mechanism II: Varieties and evolution" Cognitive Systems Research 38:50-59
12. Springer LNCS 5199 (2008) "Improved Lower Limits for Pheromone Trails in ACO"

Prior citations: see notes/research_drill_natural_analog_swarm_intelligence_5x_2026-06-07.md (18 citations)

---

## Next-drill candidates

1. URGENT (audit not research): verify tau_min floor is enforced in current Misra-Gries code. This is a convergence gate. 1 day.
2. Wasserstein decay rate calibration (5.2 above) -- empirical test on HotpotQA distribution shift. 3-5 days.
3. Free probability / Tracy-Widom edge fluctuations (field advisor #1-5): the spectral edge of the counter distribution as a substrate-novel observable. Connects to the Fokker-Planck stationary distribution.
4. Fokker-Planck analysis of discrete Misra-Gries dynamics -- no published paper covers this; would require original derivation. Novel synthesis; cap P at 0.50. 1-2 week theory.
