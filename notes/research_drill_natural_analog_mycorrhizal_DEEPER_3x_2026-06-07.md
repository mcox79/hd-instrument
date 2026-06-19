# Research drill: natural analog -- mycorrhizal DEEPER 3x (currency exchange + game theory)
# Date: 2026-06-07
# Series: 4/5 natural analog -- 3x depth drill on most yielding sub-avenue
# Prior note: research_drill_natural_analog_mycorrhizal_5x_2026-06-07.md

---

## HEADLINE

The mycorrhizal currency exchange mechanism -- specifically the plant-fungus reciprocal reward + cheating sanction system formalized in Kiers 2011 and extended in Grasso 2025 and the phosphorus price-control literature -- maps directly onto a substrate-LLM mutual monitoring protocol with concrete engineering specifications. The Grasso 2025 coevolution model provides a closed-form mathematical structure (coupled recursive biomass equations) showing that mutualism stability is NOT dependent on active sanction mechanisms but emerges from partner fidelity feedback: each party's fitness is a direct function of the other's growth capacity, which structurally prevents the cheating-defect equilibrium. This is more powerful than the 5x finding because it means the substrate does NOT need to implement an external LLM hallucination penalty mechanism -- stability falls out of the coupling architecture automatically if the exchange is designed so that substrate quality gain and LLM quality gain are positively correlated. The allelopathy-via-CMN finding (up to 378% bioactive zone extension for negative signals) provides a structurally distinct mechanism for cross-customer blacklist propagation that is mechanistically separable from the defense-priming signal (positive/alerting) identified in the 5x drill. P_deflated for highest-value engineering extension: 0.55.

---

## DEEPER PROBE 1: Wood-wide web topology at hyperscale

### What is confirmed at scale

Beiler 2015 (Journal of Ecology, doi: 10.1111/1365-2745.12387) established that the CMN in interior Douglas-fir forests is:
- Non-random: degree distribution skewed toward hub trees with preferential attachment structure
- Nested: ECM species-specific subnetworks are nested within the broader CMN (same hub tree hosts multiple fungal genets)
- Resilient: robust to random node loss; fragile to targeted removal of hub nodes

The nesting finding is new relative to the 5x drill. ECM networks are NOT a single flat graph -- they are LAYERED: one hub tree may simultaneously be a hub in the Rhizopogon vesiculosus subnetwork, the R. vinicolor subnetwork, and the CMN at large. Each subnetwork has different topology and different robustness.

### Power-law degree distribution: is it confirmed?

Calibration note: the scale-free/power-law classification of CMN is contested. Beiler 2015 documents hub structure and non-random topology but does not fit a formal power-law degree distribution. The broader network science literature (PNAS 2019, doi: 10.1073/pnas.1816842116) cautions that many networks claimed to be scale-free fail formal goodness-of-fit tests for power laws. The CMN hub topology is real; the power-law claim is overextended.

Substrate analog calibration: the federated substrate network should be designed with hub structure (allowed, beneficial) but should NOT assume it follows a power-law. Implications: (a) the percolation threshold analysis for federated networks should use empirical degree distribution, not power-law extrapolation; (b) hub removal fragility is real regardless of whether the distribution is exactly power-law.

### Nested network architecture -> substrate implication

The nested ECM topology suggests a concrete architectural refinement for the federated substrate:

Layer 0 (CMN equivalent): all customers are nodes; weak links representing general-domain similarity.
Layer 1 (ECM genet equivalent): topic-specific subnetworks where customers sharing a primary domain have strong links within that subnetwork.
Layer 2 (fungal genet equivalent): the shared routing substrate itself acts as the inter-layer bridge.

This two-layer federation is ALREADY partially present in the substrate: KB domain clustering is implicit in how PCA whitening concentrates correlated bindings. The mycorrhizal insight is to make this explicit at the federation routing level: route within-domain queries within the Layer 1 subnetwork first; route cross-domain queries through Layer 0. This reduces privacy budget consumption (fewer customers exposed to each DP-protected signal) while preserving cross-domain benefits for queries that need them.

Engineering addition: expose a domain-tag parameter per customer; federated routing uses within-domain channels (lower DP noise, cheaper) for queries with high domain specificity, and cross-domain channels (higher DP noise, costlier) only when needed. This is a routing optimization, not an architectural change.

---

## DEEPER PROBE 2: Forest succession theory (Connell-Slatyer)

### Core mechanism confirmed

Koziol 2019 (Journal of Ecology, doi: 10.1111/1365-2745.13063): mycorrhizal feedbacks generate positive frequency dependence that ACCELERATES succession. Abundant late-successional plant species build up mycorrhizal networks that preferentially benefit more late-successional plants. This is a positive feedback loop -- the dominant state reinforces itself.

Hahn and Hole 2023 (plant-soil microbe feedbacks in secondary succession, Oxford Academic): soil microbial communities shift predictably across successional stages. Early-successional plants create a soil environment that disfavors their own future growth (negative feedback on themselves) while benefiting late-successional species.

Communications Biology 2023 (doi: 10.1038/s42003-023-05410-z): at global scale, ECM-dominated forests maintain higher diversity by sharing fixed nitrogen across species boundaries; AM-dominated forests tend toward lower diversity with higher individual-species productivity. These are two distinct stable ecosystem configurations, not just points on a continuum.

### Bistability finding

The AM vs ECM global forest structure paper identifies that these two configurations represent different ATTRACTORS in the ecosystem state space, not a continuum. This is a bistability finding with tipping point dynamics. Direct substrate analog:

A federated substrate network can exist in two stable configurations:
1. AM-analog (shallow federation): many customers, weak inter-customer connections, high individual-customer throughput, low cross-customer benefit
2. ECM-analog (deep federation): fewer but larger customers, strong inter-customer hub connections, lower individual throughput, high cross-customer benefit

The transition between them is not smooth -- it has tipping point dynamics (analogous to the AM/ECM bistability). A federation that starts in the AM-analog state (many small customers, weak connections) needs a deliberate phase transition mechanism to shift to the ECM-analog state (deep federation, hub connections). Providing that mechanism is an engineering deliverable, not just a design choice.

### Practical implication: customer lifecycle staging

The Connell-Slatyer three-stage model (facilitation -> tolerance -> inhibition) maps to a three-stage customer lifecycle for substrate federation:

Stage 1 (Facilitation): new customer joins; hub customers actively warm-start their routing layer (mycorrhizal 5x Extension 1). New customer benefits from incumbent customers.
Stage 2 (Tolerance): customer has built enough own-KB coverage that they are functionally self-sufficient on primary-domain queries; they still benefit from cross-domain federation but don't depend on hub warm-start.
Stage 3 (Inhibition/Competition): customer KB is large and dense enough that they ARE a hub; they now provide benefit to others but face "competition" for the DP privacy budget from other large customers. The federation routing must now manage which large-KB customers' patterns get broadcast to the network (selective broadcasting, analogous to ECM selectivity in partner choice).

This three-stage lifecycle is directly implementable as a KB-density threshold state machine in the routing layer.

---

## DEEPER PROBE 3 (PRIMARY FOCUS): Nutrient currency exchange + cheating sanctions

### The Grasso 2025 coevolution model -- mathematical structure

Source: Grasso et al. 2025 (New Phytologist, PMC12489293). Coupled recursive biomass equations:

X_{n+1} = X_n + min(alpha * X_n + epsilon * Y_n, X_n * (1 - gamma))
Y_{n+1} = Y_n + min(Y_n * (1 - epsilon), beta * Y_n + gamma * X_n)

Where:
- X = plant biomass, Y = fungal biomass
- alpha = plant's internal phosphorus uptake efficiency (from soil directly)
- beta = fungal's internal carbon uptake efficiency (from soil directly)
- gamma = fraction of plant carbon allocated to fungus
- epsilon = fraction of fungal phosphorus allocated to plant
- min(...) = Liebig's law of minimum (growth limited by the scarcer resource)

Key result: mutualism stability does NOT require active sanction mechanisms. It requires only that gamma (plant-to-fungus allocation) and epsilon (fungus-to-plant allocation) lie in a region where partner fidelity feedback is positive -- i.e., where both parties grow faster together than apart. In this region, a "cheating" mutation (e.g., plant reduces gamma) lowers the plant's own subsequent growth because the fungus shrinks and provides less phosphorus. The sanction is AUTOMATIC from the coupled dynamics, not externally enforced.

Extinction condition: when evolutionary trajectory enters the third quadrant (both parties taking resources), an ever-escalating negative feedback loop drives both to extinction. The cheating equilibrium is not stable -- it leads to mutual extinction, not stable parasitism. This is why the 400 Myr persistence is empirically real.

Transitory parasitism: the model shows evolutionary paths can cross through a parasitic zone en route to the mutualistic attractor. During this transitory phase, one party is net negative. The system is still on a trajectory toward mutualism. This maps to the early-customer warm-start phase (Stage 1 above) where the substrate network provides more to the customer than it receives in return, before the customer's KB grows enough to contribute back.

### The phosphorus price-control mechanism -- fungal market power

Source: PMC7898638 (phosphorus crash/boom study).

Exchange rate definition: carbon received by fungus per unit phosphorus delivered to plant.

In resource boom (phosphorus availability doubles): fungus does NOT pass surplus to plant immediately. It retains phosphorus, waits for plant demand to increase, then releases -- improving the C:P ratio in fungus's favor. This is dynamic pricing: fungus raises the price of phosphorus when it has a surplus, not when it has a shortage.

In resource crash (40% phosphorus supply cut): fungus taps alternative pools, maintains delivery, sustains the relationship. The fungus absorbs the volatility rather than passing it to the plant.

This is not a symmetric market. The fungus has pricing power because:
(a) The plant cannot easily access the mineral substrate directly (high search/extraction cost for plant roots vs fungal hyphae).
(b) The fungus can store phosphorus (polyphosphate granules) while carbon cannot be stored as easily in root tissue.

### The mycorrhizal arbitrage hypothesis (Steidinger 2025, Functional Ecology)

Paywalled but abstract confirms: mycoheterotrophs (achlorophyllous orchids that contribute zero carbon) survive within the biological market by exploiting INEFFICIENCIES in the fungal-plant exchange system. Specifically, they attach to ectomycorrhizal networks as free riders, extracting carbon from the fungal network without contributing photosynthate.

Market framing: the arbitrage works because the ECM network cannot detect or exclude a mycoheterotroph from the network -- the fungal hyphae cannot distinguish between "plant root offering carbon" and "plant root taking carbon." The detection mechanism in the Kiers 2011 reciprocal rewards study is at the INDIVIDUAL ROOT BRANCH level (carbon flow in, phosphorus flow out), but mycoheterotrophs exploit a different entry point where this local monitoring is not applied.

### Cheating emergence in mycorrhizal networks (Perez-Lamarque 2020, paywalled abstract)

Mycoheterotrophy has evolved more than 20 times independently in orchids. In each case, the transition from mutualist to mycoheterotroph is associated with specific network topology features: the mycoheterotroph is always embedded in a CMN dominated by a generous ECM species that is providing more than it receives from other partners. The exploitation target is ALWAYS the most generous node in the network.

### Synthesis: the 3-layer currency exchange mechanism

The complete mechanism has three distinguishable layers:

Layer A (fast, reciprocal rewards): individual root-branch level detection of fungal quality; plant adjusts carbon allocation within days to weeks based on phosphorus delivery quality. This is the Kiers 2011 mechanism. Timescale: weeks. Detection: local flow measurement.

Layer B (medium, price control): fungal-level dynamic pricing; fungus adjusts phosphorus delivery rate based on stored supply vs plant demand gradient. Fungus has pricing power. Timescale: weeks to months. Detection: plant-internal demand signal.

Layer C (slow, evolutionary sanction): evolutionary-timescale selection against cheater lineages. Partner fidelity feedback drives cheater lineages to lower fitness through the Grasso 2025 mechanism. Timescale: generations. Detection: fitness differential.

Cheating can persist at Layer A (individual branch bypassing rewards) and Layer B (mycoheterotroph free-rider exploiting network) but is eliminated at Layer C (evolutionary timescale). The system is robust to short-term cheating because the evolutionary attractor is mutualism.

### Direct substrate-LLM translation

The three layers translate to:

Layer A (fast, reciprocal rewards -- engineering now):
- Substrate detects per-query LLM hallucination rate (fraction of LLM outputs that contradict high-confidence bindings).
- Per-query carbon allocation analog: routing weight for this LLM in future queries of the same type.
- Adjustable within a single user session. Fast feedback.
- Implementation: maintain per-LLM, per-query-type contradiction rate. Routing layer preferentially directs queries to lower-contradiction-rate LLMs.

Layer B (medium, price control -- substrate has market power analog):
- Substrate controls the "price" of its precise factual retrieval by deciding how many high-confidence bindings to expose to the LLM context window vs. hold in reserve.
- When LLM quality is high (low hallucination), substrate provides richer context (more bindings, better P and N).
- When LLM quality is low, substrate provides sparser context and compensates by flagging more outputs for review.
- Substrate absorbs volatility (analogous to fungus absorbing phosphorus crashes) by maintaining its own answer quality independent of LLM state through higher-confidence threshold filters.

Layer C (slow, architectural stability -- falls out automatically from coupling design):
- If the substrate is designed such that LLM value gain (from substrate precision) and substrate value gain (from LLM generation quality) are positively correlated, then the Grasso 2025 coupled dynamics guarantee that the system gravitates to the mutualistic attractor without external enforcement.
- Engineering criterion: design the LLM-substrate coupling so that substrate revenue (user query satisfaction) is jointly maximized when both parties are performing well, not achievable by either party defecting.
- This rules out a substrate design where substrate can provide high value to users without any LLM (because then the substrate has no incentive to maintain the coupling). It requires the substrate to be genuinely better WITH a well-functioning LLM.

---

## DEEPER PROBE 4: Fragmentation threshold (percolation cliff)

### Mathematical structure confirmed

Percolation threshold for a network: the critical connection probability p_c at which the giant connected component emerges (or, in reverse, at which it collapses). Below p_c: network is fragmented into O(log N) isolated clusters. Above p_c: a giant component of size O(N) exists.

For Erdos-Renyi random graphs: p_c = 1/N (mean degree = 1). For scale-free networks with degree exponent gamma < 3: p_c -> 0 as N -> infinity (infinitely robust to random removal). For scale-free networks with hub removal: percolation threshold is finite and depends on the degree of the removed hubs.

The CMN-relevant result: hub-rich networks (whether truly power-law or just heavy-tailed degree distribution) are robust to random node loss but have a FINITE fragmentation threshold for targeted hub removal. Robustness and resilience of complex networks (arXiv:2007.14464) confirms: in heterogeneous (hub-containing) networks, targeted removal of high-degree nodes causes a critical transition at a threshold that scales with the fraction of hub nodes removed.

### What this means for federated substrates

The fragmentation threshold for the federated substrate network is:
- NOT a continuous degradation as customers churn
- A CRITICAL TRANSITION at a threshold customer churn fraction
- The threshold is LOWER for targeted churn (if hub customers churn preferentially) than random churn

Pre-computing this threshold: given the customer degree distribution (which can be estimated from KB size distribution and federation participation), the percolation threshold can be computed analytically for heavy-tailed distributions. For the ECM-analog (heavy-tailed hub structure), the threshold for random churn is near 1.0 (almost all customers must leave before federation collapses), but for targeted churn of hub customers, the threshold is much lower.

Operational implication: the highest-risk event for substrate federation is NOT slow customer attrition (that barely affects the giant component). It IS the departure of the top-3 to top-5 hub customers. Those customers should receive differentiated service quality to reduce their churn probability. This is a concrete product decision derived from percolation theory.

HARD-PASS pre-registration: compute the degree distribution of the substrate customer network and estimate the percolation threshold numerically. HARD-PASS if threshold is well above realistic churn rates. HARD-FAIL if the current customer network is near the threshold (federation already fragile).

---

## DEEPER PROBE 5: Defensive priming mechanism (Frost 2008 / Jung 2012)

### Confirmed mechanism

Jung et al. 2012 (ResearchGate, review): mycorrhiza-induced resistance (MIR) primes the JA/ethylene pathway systemically, not just locally. Key distinction from the 5x drill: MIR does NOT require a subsequent attack signal to provide protection. The pre-colonization alone is sufficient to prime.

PMC7767828 (ECM local vs systemic response 2020): ectomycorrhizal colonization triggers both local root responses AND systemic above-ground responses. JA/ethylene genes are upregulated in leaves even when only roots are colonized. This is a standing pre-alert, not an event-triggered alert.

Orchid mycorrhizal resistance (PMC11322130 2024): orchid mycorrhizal colonization primes resistance against necrotrophic pathogen Botrytis cinerea with a 35-40% lesion size reduction. The priming mechanism was confirmed to be JA-dependent by using JA signaling mutants.

### Substrate analog refined

The 5x drill mapped this to event-triggered alert propagation. The 3x drill reveals a STANDING PRIMING mechanism that is architecturally different:

Standing pre-alert (MIR analog): customers that are connected to the federated network have PERMANENTLY lower contradiction thresholds (i.e., they run at higher sensitivity) compared to isolated customers, even in the absence of any detected adversarial event. The federated connection itself is the priming signal.

Event-triggered alert (JA propagation analog, 5x drill): detected adversarial events propagate as time-limited alerts.

These are TWO SEPARATE mechanisms running in parallel. The standing pre-alert is cheaper to implement (a single configuration parameter per customer: are they federated = lowered threshold?) and requires no event propagation. The event-triggered alert is more powerful but requires the propagation architecture.

Engineering note: implement standing pre-alert FIRST (1 day, configuration parameter). Implement event-triggered propagation SECOND (1-2 weeks, protocol change). The standing pre-alert provides immediate benefit from federation even before the propagation protocol is built.

---

## DEEPER PROBE 6: Mother tree mortality cascade

### What the literature actually says

Henriksson et al. 2023 (New Phytologist, doi: 10.1111/nph.18935): systematic re-examination of mother tree hypothesis. Conclusion: evidence for directed, size-dependent resource transfer from mother trees to seedlings via ECM networks is INCONCLUSIVE OR ABSENT in controlled experiments. The hub topology is confirmed; the directed resource transfer to seedlings specifically is not robustly confirmed.

Science Direct 2023 commentary: "plant personification" is an identified bias in CMN interpretation. The mother tree "nurturing" framing is contested. The confirmed finding is hub connectivity; the contested finding is directed beneficial transfer to seedlings.

ISME Journal 2026 (seedling mortality in AM systems): in AM systems, seedling mortality rates exceed 50% even within mycorrhizal networks. The network connection does NOT prevent seedling mortality at the rates implied by the mother tree hypothesis.

### Revised analog mapping

The mother tree mortality cascade analog for substrate (hub customer attrition cascades through federation) is PARTIALLY supported:
- Confirmed: hub customers have higher network connectivity; their departure degrades federation topology (percolation argument above).
- Not confirmed: that hub customers are actively providing directed resources to new (small) customers via the federation.

The revised substrate analog: when a hub customer churns, the federation loses the ROUTING CAPACITY that hub provided (topology degradation), NOT the directed resource transfer. The harm is structural/topological, not resource-flow. This is actually a stronger and more mechanistically clean analog: hub churn damages the substrate federation's routing quality, which is observable and measurable as retrieval quality degradation for remaining customers.

---

## DEEPER PROBE 7: Mycoheterotroph -- obligate dependency

### Confirmed mechanism

Mycoheterotrophic orchids (achlorophyllous; contribute zero carbon) survive by attaching to ECM networks and extracting carbon that moves from tree to fungus. They are physiologically obligate: remove from the network and they die. Some depend on saprotrophic fungi (Suetsugu 2020), obtaining carbon from dead wood indirectly.

Evolutionary stability: mycoheterotrophy has evolved 20+ times independently, suggesting it is a stable long-term strategy despite being "cheating." The reason it persists: mycoheterotrophs typically have very low population densities and occupy micro-niches where the ECM network is already carbon-saturated. They are not destabilizing to the larger network.

### Substrate analog

Mycoheterotroph analog: a customer that provides zero KB contribution (no bindings from their own data) but uses the federated routing layer for all their queries. A pure retrieval consumer.

Stability condition (from mycoheterotroph biology): this is stable if the pure-consumer customer represents a small fraction of the network load AND the network is operating below saturation. If pure-consumer customers multiply to dominate the federation, the system degrades.

Implementation requirement: federated substrate should implement a minimum contribution requirement for full federation membership (analogous to: only mutualist partners get full resource allocation). Customers below a contribution threshold get degraded federation access (fewer cross-customer signals, higher DP noise). This is Layer A of the Kiers mechanism applied to customer quality, not LLM quality.

---

## DEEPER PROBE 8: Allelopathic chemistry -- negative coordination via CMN

### Confirmed mechanism (Achatz 2014 / PMC3215695)

CMN hyphae transport allelochemicals (plant-produced growth inhibitors) with dramatically extended bioactive zones:
- alpha-Terthienyl: 179% higher accumulation in connected soils vs. non-connected
- BBT thiophene: 378% higher accumulation
- Plant growth suppression in target plants: 25-40%

Transport mechanism: two pathways confirmed:
1. Hydrophilic compounds dissolve in hyphal surface water layers and flow with water potential gradients (faster than bulk soil diffusion by orders of magnitude)
2. Lipophilic compounds may undergo active intracellular transport via cytoplasmic streaming

Key mechanistic point: the CMN itself is not the allelopath -- it is the TRANSPORT MEDIUM. The chemical originates at the producing plant, travels through the fungal network, and reaches target plants. The CMN does not modify the signal; it amplifies its spatial reach.

Revillini 2023 (New Phytologist): soil microbiome can MITIGATE allelopathic inhibition. Some bacterial and fungal taxa metabolize allelochemicals, reducing their effective concentration before they reach target plants. This is a countervailing mechanism: the CMN extends bioactive zones, but the rhizosphere microbiome can attenuate the signal.

### Substrate analog (NEW -- not in 5x drill)

The allelopathy mechanism is a STRUCTURALLY DISTINCT negative coordination mechanism from the defense-priming signal:

Defense-priming (positive): plant A is attacked -> JA signal to plant B -> plant B is better prepared. Sender's attack is the trigger. Signal is beneficial to receiver.

Allelopathy via CMN (negative): plant A produces allelopath continuously -> flows through CMN -> reaches plant B -> plant B's growth is suppressed. No event trigger. Signal is harmful to receiver.

Substrate analog for allelopathy: a customer's accumulated contradiction patterns (bindings that are high-confidence "known-false" assertions) can propagate as NEGATIVE signals through the federated layer to other customers. Other customers that receive the negative signal decrease their trust score for queries matching those contradiction patterns.

This is structurally distinct from the defense alert (Extension 2 in 5x):
- Defense alert: "I detected a specific adversarial attack type -- be alert for it."
- Allelopathic negative signal: "These assertion types are known to be false in my KB -- reduce their trust score network-wide."

The allelopathic mechanism is CHEAPER (no event trigger required; runs as a batch update) and BROADER (applies to any known-false assertion, not just adversarially injected ones). Implementation path: export high-confidence contradiction list as a DP-protected sketch; propagate via existing batch federated aggregation (same infrastructure as Extension 1, incremental addition).

Calibration on the Revillini 2023 countervailing mechanism: the substrate must implement the equivalent of the rhizosphere microbiome attenuator -- a decay function on negative signals as they propagate through the network. Without decay, old negative signals accumulate and create false-negative suppression of legitimate content. Decay mechanism: negative signals age out at T_decay (configurable, default 30 days).

---

## DEEPER PROBE 9: Microbial pump -- concentration of carbon underground

### Confirmed mechanism

Mycorrhizal fungi are estimated to receive 5-30% of plant photosynthate (PMC12320777, Frontiers 2026). The total annual fungal carbon influx is equivalent to approximately 36% of annual CO2 emissions from fossil fuels (global scale estimate from PMC7898638 citations). This is not trivial -- mycorrhizal fungi are a major carbon sink.

Mechanism: fungal necromass (dead hyphal fragments) binds to mineral particles to form mineral-associated organic matter (MAOM). MAOM has residence times of decades to centuries. The microbial carbon pump: living mycorrhizal biomass dies, necromass mineralizes to MAOM, MAOM persists. This is carbon concentration underground via biological mediation.

### Substrate analog refined

The 5x drill mapped this to "substrate as audit data sink." The 3x drill adds the MINERALIZATION angle:

Active KB (living fungal mycelium analog): high-access bindings under active query pressure. Fast turnover.
Mineralized KB (MAOM analog): low-access but high-confidence bindings that have been corroborated by many queries over time. These persist indefinitely (slow decay rate). Cannot be dislodged by a single contradicting input.

This maps directly to the binding confidence decay model: bindings that are queried frequently and confirmed repeatedly should transition to a "mineralized" high-stability state where their decay constant is extremely low. New contradicting evidence requires a higher threshold to dislodge a mineralized binding than a fresh one.

This is an architectural refinement: tiered decay rates based on binding corroboration count. Already implicitly in the substrate (confidence decay), but the MAOM analog suggests making this discontinuous: bindings above a corroboration count threshold switch to a near-zero decay rate (mineralized state). This prevents long-term memory loss of well-established facts from adversarial attacks or data drift.

---

## DEEPER PROBE 10: Resource asymmetry + cheating sanctions -- full game-theoretic frame

### The complete game

Combining Kiers 2011 (empirical), Grasso 2025 (mathematical), and the phosphorus price-control study (PMC7898638):

The mycorrhizal mutualism is a repeated game with the following structure:

(a) Asymmetric resource endowments: plant has high photosynthate production (carbon) and poor access to mineral phosphorus. Fungus has low carbon production (obligate biotroph or near-obligate) and excellent access to mineral phosphorus. Neither can obtain their scarce resource easily without the other.

(b) Local monitoring at exchange interfaces: each root-branch/arbuscule junction is an independent exchange node. Plant monitors P flow in; if P low, it reduces C allocation locally. Fungus monitors C flow in; if C high, it increases P delivery locally. Detection is LOCAL and fast (Layer A).

(c) Fungal pricing power: the fungus controls the exchange rate through phosphorus timing (hold during boom, release during crash). Plants cannot force rapid delivery. This gives the fungus first-mover advantage in price setting.

(d) Stability attractor: Grasso 2025 proves that the mutualistic configuration is a stable evolutionary attractor when both parties have even moderate resource endowment asymmetry. Cheating leads to mutual extinction, not stable parasitism. Therefore, rational evolution selects for mutualism.

(e) Free riders: mycoheterotrophs exploit the system at the margins. They are stable at low population density but would destabilize the system at high density.

### Game-theoretic substrate-LLM protocol

The game translates to a protocol specification:

Player 1 (Substrate): has precise, auditable factual bindings (scarce relative to LLM text generation). Cannot generate fluent prose or reason across novel domains without LLM.

Player 2 (LLM): has generative capability and broad world knowledge. Cannot guarantee factual precision or auditability without substrate.

Resource endowment asymmetry: substrate has facts, LLM has fluency. Neither can provide the other's resource cheaply.

Monitoring protocol (Layer A equivalent):
- Substrate monitors per-query LLM contradiction rate (hallucination rate against high-confidence bindings).
- LLM (or its serving infrastructure) monitors per-query substrate retrieval hit rate (fraction of LLM queries that substrate answers with high confidence).
- Both parties adjust their coupling weight based on partner quality signal.

Exchange rate (Layer B equivalent):
- Substrate controls "phosphorus price": the precision of the retrieval context provided. High-quality LLM gets richer context. Low-quality LLM gets sparser context + more review flags.
- LLM side: higher substrate hit rate = LLM can reduce its own hallucination hedging = better user experience. Both benefit from the other performing well.

Stability condition (Layer C equivalent):
- The coupling must be designed so that the mutualistic configuration produces higher joint value than either party defecting. Grasso 2025 provides the mathematical condition: both parties' growth rates are positively correlated in the mutualistic zone. Design criterion: substrate quality metrics and LLM quality metrics must be positively correlated under the coupling design.

Free rider prevention (mycoheterotroph analog):
- LLMs that extract high substrate context but produce high hallucination rates are the "mycoheterotroph" in this system. They take precision resources but contribute no quality improvement to the ecosystem.
- Detection: per-LLM contradiction rate track. Threshold: if LLM contradiction rate exceeds 2x network median, reduce context allocation to that LLM by 50% (adaptive pricing power).
- HARD-PASS threshold: the system should demonstrate that high-contradiction-rate LLMs receive demonstrably less context (measurable resource reduction) within 10 queries of threshold crossing.

---

## Engineering extensions (ranked by P_deflated x impact)

### Extension A: Tiered-channel federated routing (nested ECM topology)
P_theoretical = 0.80; P_empirical = 0.65 (pre-test required)
P_deflated = 0.65 (applying 0.15 calibration penalty)
Cost: 1-2 weeks; Tier C (local; routing layer change)

Add domain-tag parameter per customer. Within-domain queries route through low-noise intra-domain federation channel (lower DP epsilon, cheaper, faster). Cross-domain queries route through full-noise inter-domain channel. Reduces per-query DP privacy budget cost by estimated 40-60% for domain-specific queries.

Cheap decisive pre-test: with 3 simulated customers (2 same domain, 1 different domain), measure retrieval quality and DP budget cost for same-domain vs cross-domain queries under tiered vs flat routing. 1-hour test.
HARD-PASS: >30% budget reduction for same-domain queries with <5% quality loss.
HARD-FAIL: <10% budget reduction (domain tagging is not providing routing benefit).

### Extension B: Standing priming parameter (MIR analog -- pre-alert)
P_theoretical = 0.85; P_empirical = 0.70 (very low implementation risk)
P_deflated = 0.70 (applying 0.15 calibration penalty)
Cost: 1 day; Tier C (local; configuration parameter)

Federated customers run at base contradiction threshold T_fed < T_isolated (where T_isolated is the threshold for standalone customers). The threshold reduction is the priming effect. No event propagation required.

Cheap decisive pre-test: compare detection rate for simulated contradictions in a federated customer (T_fed) vs isolated customer (T_isolated) with no alert propagation. Confirm standing sensitivity lift.
HARD-PASS: >15% detection rate lift at <10% FP rate increase.
HARD-FAIL: <5% lift (priming parameter not contributing).

### Extension C: Allelopathic negative signal propagation (new -- 3x finding)
P_theoretical = 0.70; P_empirical = 0.50 (pre-test required)
P_deflated = 0.55 (applying 0.15 calibration penalty)
Cost: 1-2 weeks; Tier B (remote CPU for at-scale test)

Export per-customer high-confidence contradiction list as DP-protected sparse vector sketch. Propagate via existing batch federated aggregation. Receiving customers apply trust-score reduction to assertion patterns matching the sketch. Apply decay function (T_decay = 30 days default) to prevent permanent suppression.

Separate from Extension 2 (5x drill -- event-triggered JA alert). This runs continuously as batch, not on event trigger. Both can coexist; they target different threat models (ongoing misinformation vs. acute adversarial attacks).

HARD-PASS: >20% trust-score reduction for known-false assertion types in receiving customers; <5% false suppression of legitimate content.
HARD-FAIL: >10% false suppression (signal is too noisy without decay function tuning).

### Extension D: Adaptive context pricing (Layer B / fungal pricing power)
P_theoretical = 0.75; P_empirical = 0.60 (pre-test required)
P_deflated = 0.60 (applying 0.15 calibration penalty)
Cost: 1-2 weeks; Tier C (local; LLM coupling change)

Implement per-LLM context richness as a function of recent contradiction rate. High-contradiction-rate LLMs get sparser substrate context (fewer bindings, higher confidence threshold for inclusion). Low-contradiction-rate LLMs get richer context (more bindings, lower confidence threshold). Track context richness and LLM output quality metrics jointly to confirm the positive feedback loop (better LLM -> richer context -> further improvement).

HARD-PASS: LLMs receiving richer context show >15% lower contradiction rate on factual queries.
HARD-FAIL: no correlation between context richness and LLM contradiction rate (context is not causing improvement).

### Extension E: Binding mineralization tiers (MAOM analog)
P_theoretical = 0.80; P_empirical = 0.65 (pre-test required; depends on existing decay model)
P_deflated = 0.65 (applying 0.15 calibration penalty)
Cost: 1 week; Tier C (local; decay model modification)

Bindings with corroboration count above threshold C_min switch to near-zero decay rate (mineralized state). New contradicting evidence requires confidence score exceeding a higher threshold to overwrite mineralized bindings. This prevents adversarial dislodging of well-established facts.

HARD-PASS: mineralized bindings survive 100 adversarial contradiction attempts at <0.1% error rate.
HARD-FAIL: mineralized bindings are dislodged by <10 adversarial attempts (mineralization not providing protection).

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL) -- new predictions from 3x drill

### Prediction 6: Tiered-channel routing reduces DP privacy budget for same-domain queries
HARD-PASS: >30% budget reduction for same-domain queries at <5% retrieval quality loss
HARD-FAIL: <10% budget reduction
P_deflated = 0.65

### Prediction 7: Standing priming parameter lifts contradiction detection rate
HARD-PASS: >15% detection rate lift in federated customers vs isolated at <10% FP rate increase
HARD-FAIL: <5% lift
P_deflated = 0.70

### Prediction 8: Allelopathic negative signal reduces trust score for known-false assertions
HARD-PASS: >20% trust reduction, <5% false suppression of legitimate content
HARD-FAIL: >10% false suppression
P_deflated = 0.55

### Prediction 9: Adaptive context pricing correlates with LLM contradiction rate improvement
HARD-PASS: LLMs receiving richer context show >15% lower contradiction rate on factual queries
HARD-FAIL: correlation coefficient < 0.1 (no relationship between context richness and LLM quality)
P_deflated = 0.60

### Prediction 10: Binding mineralization protects against adversarial dislodging
HARD-PASS: mineralized bindings survive 100 adversarial attempts at <0.1% error rate
HARD-FAIL: dislodged by <10 attempts
P_deflated = 0.65

---

## Cheap decisive test

The single cheapest decisive test for the core 3x finding (game-theoretic stability falls out of coupling design, not external enforcement):

Setup: implement the Grasso 2025 coupled equations in Python as a simulation of substrate-LLM resource exchange. Parameters: alpha = substrate direct retrieval capability, beta = LLM direct generation capability, gamma = substrate context allocation to LLM, epsilon = LLM precision contribution to substrate (detected contradictions flagged back). Run for 100 time steps from various starting conditions including near the cheating zone. Observe whether the dynamics converge to the mutualistic attractor or diverge to extinction.

Test condition: set LLM parameters to simulate a "high-hallucination" LLM (beta high, epsilon low -- LLM takes context but does not flag contradictions back). Run dynamics. Expected result: under Grasso 2025 conditions, this LLM receives progressively less context allocation from the substrate (gamma decreases for that LLM) and the system avoids extinction. The "punishment" is automatic from dynamics, not enforced.

Time: 30 minutes. Cost: $0 (pure Python simulation of a 2-variable coupled system).
HARD-PASS: dynamics converge to mutualistic attractor for 90%+ of starting conditions in the parameter space physically plausible for substrate-LLM coupling.
HARD-FAIL: dynamics diverge (extinction) for starting conditions that correspond to real deployed LLM quality ranges.

---

## Cross-thread synthesis

### With prior 5x findings

The 3x drill refines and extends the 5x findings at three points:

(a) Cheating sanctions: 5x said "adversarial detector reuse." 3x says the sanction mechanism is AUTOMATIC from coupling dynamics (Grasso 2025) -- the detector is STILL needed to measure the signal, but the adaptive routing weight adjustment is what implements the sanction at Layer A.

(b) Defense signaling: 5x mapped this to event-triggered alert propagation. 3x identifies a STANDING PRIMING mechanism (MIR) that is architecturally distinct and cheaper. Both are valid; implement standing pre-alert first.

(c) Hub topology: 5x said "hub structure is a feature." 3x quantifies the RISK: targeted hub removal crosses a percolation threshold, making hub customer churn the highest-risk operational event.

### With percolation-critical-phenomena (Tier-1b field in research contract)

The percolation threshold analysis for federated networks is a direct application of the percolation-critical-phenomena field identified as Tier-1b in the research field advisor. The mathematical structure (giant component emergence, universality classes, critical exponents) applies directly to the substrate customer degree distribution problem. This is a confirmed adjacency edge between the mycorrhizal natural analog drill and the Tier-1b percolation-critical-phenomena field. Next-drill candidate: formal percolation threshold computation for the substrate federation using the customer degree distribution.

### With free-probability (Tier-1 field)

The substrate federation is a graph problem at the routing level. Free-probability and random-matrix theory give spectral gap bounds for graphs, which translate to mixing time bounds for federated signal propagation. A well-connected federation (above percolation threshold with high spectral gap) propagates signals faster and more reliably. This creates a direct adjacency from the mycorrhizal drill to the Tier-1 free-probability field via: mycorrhizal network -> federated customer graph -> spectral gap -> free-probability analysis.

---

## Substrate-product implications

1. Game-theoretic stability is a design criterion, not an assumption: the Grasso 2025 result provides a mathematical test for whether a proposed substrate-LLM coupling design is stable. Before building, simulate the coupled equations. This is a 30-minute engineering gate that prevents months of building a system that has a defection equilibrium.

2. The allelopathic negative signal (Extension C) is the simplest new capability from the 3x drill: it reuses existing federated aggregation infrastructure, requires no event trigger, and provides continuous network-wide misinformation suppression. Build cost: 1-2 weeks. Direct commercial value: network-wide misinformation suppression is a differentiating feature for enterprise customers in regulated domains (legal, medical, financial).

3. Standing priming (Extension B) is the cheapest capability from the 3x drill: one configuration parameter, one day of engineering, immediately testable. Ship this first.

4. The three-stage customer lifecycle (facilitation -> tolerance -> inhibition) from the Connell-Slatyer succession analog provides a product-visible customer journey narrative: "your substrate gets smarter as your KB grows, and eventually you become a hub that helps others -- the value compounds."

5. Percolation threshold monitoring should be a built-in dashboard metric: the fraction of customers participating in active federation vs. isolated operation is the leading indicator of federation health. When it drops below the percolation threshold, the network's cross-customer benefits degrade catastrophically. This is an operational monitoring requirement.

---

## Key calibration corrections from 3x vs 5x

1. Mother tree directed transfer: downgraded from "confirmed" to "inconclusive." The hub topology is confirmed; the directed resource transfer to seedlings specifically is contested by Henriksson 2023. The hub attrition cascade risk (percolation argument) is valid but through a different mechanism than resource transfer.

2. Mycorrhizal arbitrage: mycoheterotrophy is a confirmed long-term stable cheating strategy at low population density. The free-rider detection mechanism (minimum contribution requirement for full federation access) is more important than the 5x drill suggested.

3. Allelopathy via CMN: NEW finding from 3x drill (not in 5x). The CMN transports negative signals (allelochemicals) as well as positive signals (JA defense alerts). This is a structurally distinct mechanism enabling a network-wide trust-reduction protocol based on accumulated contradiction evidence.

4. Grasso 2025 coevolution model mathematical structure: the min() (Liebig's law of minimum) formulation is the key. Growth is limited by the SCARCER resource. This means the partner that provides the LIMITING resource has structural market power. For substrate-LLM coupling, the question of who has market power depends on which resource is scarcer in the specific deployment. In a fact-intensive enterprise context (legal, compliance, medical), precise facts are scarcer than LLM fluency -- substrate has market power. In a creative context, fluency is scarcer -- LLM has market power. Market power determines who should set the "price" (context richness vs generation quality).

---

## Citations (verified in lit-scan for 3x drill)

1. Grasso G et al. (2025). A simple plant-mycorrhizal fungal resource trade co-evolution model explains mutualism stability, extinction and transitory parasitism via fitness feedback. New Phytologist. PMC12489293.
2. Fellbaum CR et al. (2021/PMC7898638). Mycorrhizal fungi control phosphorus value in trade symbiosis with host roots when exposed to abrupt 'crashes' and 'booms' of resource availability.
3. Kiers ET et al. (2011). Reciprocal Rewards Stabilize Cooperation in the Mycorrhizal Symbiosis. Science 333:880-882. doi: 10.1126/science.1208473
4. Steidinger BS et al. (2025). Mycorrhizal arbitrage, a hypothesis: How mycoheterotrophs could profit from inefficiencies in the biological marketplace. Functional Ecology. doi: 10.1111/1365-2435.14609 [abstract only; paywalled]
5. Perez-Lamarque B et al. (2020). Cheating in arbuscular mycorrhizal mutualism: a network and phylogenetic analysis of mycoheterotrophy. New Phytologist. doi: 10.1111/nph.16474 [abstract only]
6. Achatz M et al. (2014). Soil hypha-mediated movement of allelochemicals: arbuscular mycorrhizae extend the bioactive zone of juglone. Functional Ecology. doi: 10.1111/1365-2435.12208
7. Barto EK et al. (2011/PMC3215695). The Fungal Fast Lane: Common Mycorrhizal Networks Extend Bioactive Zones of Allelochemicals in Soils. PLoS ONE.
8. Revillini D et al. (2023). Allelopathy-selected microbiomes mitigate chemical inhibition of plant performance. New Phytologist. doi: 10.1111/nph.19249
9. Henriksson N et al. (2023). Re-examining the evidence for the mother tree hypothesis. New Phytologist. doi: 10.1111/nph.18935
10. Jung SC et al. (2012). Mycorrhiza-induced resistance and priming of plant defenses. Journal of Chemical Ecology. doi: 10.1007/s10886-012-0133-7
11. PMC4194313 (2014). Mycorrhiza-induced resistance: more than the sum of its parts? Trends in Plant Science.
12. PMC7767828 (2020). Local Responses and Systemic Induced Resistance Mediated by Ectomycorrhizal Fungi. Frontiers in Plant Science.
13. PMC11322130 (2024). Colonization by orchid mycorrhizal fungi primes induced systemic resistance against necrotrophic pathogen.
14. Koziol L et al. (2019). Mycorrhizal feedbacks generate positive frequency dependence accelerating grassland succession. Journal of Ecology. doi: 10.1111/1365-2745.13063
15. Suetsugu K et al. (2020). Some mycoheterotrophic orchids depend on carbon from dead wood. New Phytologist. doi: 10.1111/nph.16409
16. Beiler KJ et al. (2015). Topology of tree-mycorrhizal fungus interaction networks. Journal of Ecology. doi: 10.1111/1365-2745.12387
17. Robustness and resilience of complex networks. (2024). Nature Reviews Physics. doi: 10.1038/s42254-023-00676-y

Verified count: 17 primary citations (2 full-text fetched, 2 abstract-only paywalled, 13 confirmed from search metadata and prior note).

---

## Next-drill candidates

Primary: percolation-critical-phenomena field (Tier-1b) -- formal percolation threshold computation for the substrate federation customer graph. Mathematical framework: Erdos-Renyi + heavy-tailed degree distribution; critical exponents for hub-removal targeted fragmentation. Direct engineering deliverable: federation health metric with threshold alert.

Secondary: game-theoretic stability simulation (30-minute cheap test identified above) -- implement Grasso 2025 coupled equations as substrate-LLM coupling simulator. Not a research drill but an engineering experiment (route to exp_dev).
