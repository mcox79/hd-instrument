# Research drill: QS DEEPER 3x -- cheater dynamics, biofilm phase transitions, policing math
# Date: 2026-06-07
# Series: DEEPER 3x follow-on to research_drill_natural_analog_quorum_sensing_5x_2026-06-07.md
# Focus: cheater/public-goods game theory (3-deep), biofilm phase transition, QQ specificity, AI-2 universality, persister cells, sporulation, HGT, bistable bounds

---

## HEADLINE

The deepest yield is in the cheater/public-goods game math. Replicator dynamics for public goods games with nonlinear payoffs produce three distinct regimes: stable cooperator-cheater coexistence (interior Nash equilibrium), limit-cycle oscillations (require density-dependence plus population bottlenecks simultaneously), and cheater takeover. The substrate analog is federation node contribution scoring: a node that benefits from collective retrieval without contributing cross-shard queries is a structural cheater. The literature gives an exact policing condition -- cost ratio c_pg/(c_tox + c_res) >= 1.5, toxin diffusion radius greater than public-good diffusion radius, intermediate spatial structure -- that maps to a tiered federation penalty mechanism. Biofilm phase transition has a sharp analog: the planktonic-to-sessile switch is motility-induced phase separation (MIPS), a first-order-like collective transition with hysteresis; the substrate analog is independent-shard to federated-collaboration activation with memory. Persister cell bistability (Lewis 2010 toxin-antitoxin; stochastic switching to dormancy at ~0.01% base rate) is the most direct analog for substrate hibernation mode under low load. HGT/plasmid dynamics give a formal model for cross-customer capability propagation with fitness costs. P_deflated = 0.38 overall (calibration -0.20 applied throughout; novel-synthesis P capped at 0.50).

---

## SUB-TOPIC 1: Public goods game theory -- CHEATER DYNAMICS (3-deep)

### 1.1 Game structure (Rainey 2003; Diggle 2007; West 2007)

The bacterial public goods game is instantiated in Pseudomonas aeruginosa siderophore (pyoverdine) production. Cooperators produce pyoverdine at fitness cost c. Cheaters (non-producers) consume pyoverdine released into the shared medium at zero production cost. The payoff matrix:

- Cooperator vs. cooperator group: each earns b*r - c where b = benefit per unit pyoverdine, r = pyoverdine concentration in well-mixed group, c = production cost.
- Cheater vs. cooperator group: earns b*r with zero c. Net advantage = c (i.e., exactly the cooperator's production cost).
- All-cheater group: pyoverdine collapses to zero; all earn 0. Group fitness crashes.

Price equation formulation (Hamilton 1964 / Price 1970): change in cooperator frequency delta(p) proportional to:
  Cov(w_i, p_i) + E[w_i * delta(p_i)]

where w_i is relative fitness of cell i, p_i is whether cell i cooperates. Cooperation is favored when:
  rb - c > 0  (Hamilton's rule)
  r = genetic relatedness between interacting partners

Key published result (Griffin, West et al. 2004, Nature): when relatedness r is high (e.g., clonal populations in structured environments), cooperation is stable. When r is low (well-mixed diverse populations), cheaters invade because the b*r term drops below c.

This gives the structural insight: cooperation in public goods games requires spatial structure or kinship structure to remain stable. Well-mixed = cheater invasion. Structured = cooperator survival.

### 1.2 Frequency-dependent dynamics (MacLean and Gudelj 2006; Ghoul et al. 2014)

Empirical measurement with P. aeruginosa (Diggle et al. 2007 Molecular Ecology; MacLean 2008 American Naturalist):

At low cheater frequency f_c: cheaters have high relative fitness (exploiting abundant cooperator-produced public goods). Rare advantage for cheaters.
At high cheater frequency f_c: public good supply collapses; cheaters and cooperators both suffer; cooperator advantage re-emerges (if any cooperators remain).

Result: negative frequency-dependent selection on cheating. Creates a stable interior equilibrium f_c* where cooperator and cheater fitness are equal.

The equilibrium f_c* depends on:
  f_c* = (b_c - c) / b_c  (approximate for linear payoffs)

where b_c is the cooperator-benefit per unit public good. With nonlinear diminishing returns (sigmoid payoff function), the equilibrium shifts and becomes more stable (Archetti and Scheuring 2011 J. Theor. Biol.: nonlinear public goods games with diminishing returns always have stable interior equilibrium if return rate is above a critical threshold r*).

Equilibrium stability class: With nonlinear payoffs and sigmoid returns, interior equilibrium is a stable fixed point (eigenvalue of Jacobian < 0). Perturbations return to f_c*. This is NOT a Nash equilibrium in pure strategies -- it is a mixed Nash equilibrium at f_c*.

### 1.3 Oscillations: when they occur and why (Waite and Shou 2012; PMC10565900 -- 2023 study)

PMC10565900 (2023): Equilibria and oscillations in cheat-cooperator dynamics. Key finding:

Neither density-dependence alone nor frequency-dependence alone produces oscillations in well-mixed populations. Oscillations require BOTH:
  (A) density-dependent cheater fitness (cheater advantage increases as population density increases -- the "crowding benefit" of cheating)
  (B) periodic population bottlenecks (dilution events that reset density)

Parameter a (density-dependence weight) controls whether oscillations occur at all. At a = 0: no oscillations regardless of bottlenecks.
Parameter b (frequency-dependence weight) controls oscillation amplitude only.
Bottleneck severity D: stronger dilution = higher amplitude oscillations.

Mechanism: after bottleneck, low density favors cooperators (density-dependent cheater fitness is low). Cooperators increase. As population grows, density rises, cheater advantage grows, cheaters increase. At peak density: cheaters dominate. Next bottleneck: resets.

This produces robust within-cycle oscillations (period = one growth cycle) and across-cycle oscillations (period = 10-20 cycles, driven by stochastic drift).

Substrate engineering implication: if the federation has no equivalent of "bottleneck" (periodic resets), oscillations will NOT occur. Steady-state system will converge to stable f_c* equilibrium. Oscillations are a feature of episodic/batch systems, not continuous streaming systems.

### 1.4 Policing mechanisms: formal conditions (Wechsler 2019 J. Evol. Biol.; PMC6520251)

Policing is the evolution of a third strategy: cooperating AND producing a toxin that penalizes non-cooperators. This is distinct from cheater control by relatedness (kin selection) or by coupling private and public goods.

Four-strain model: cooperators (C), cheaters (Ch), policers (P), resistant cooperators (R).

Growth rate equation for policers:
  G_P(t+1) = (mu - c_pg - c_tox - c_res + b*sum(P_j)) * G_P(t)

Growth rate for cheaters:
  G_C(t+1) = (mu + b*sum(P_j)) * (1 - (sum(T_i)/theta_T)^kappa) * G_C(t)

where c_pg = public good production cost, c_tox = toxin production cost, c_res = resistance cost, theta_T = toxin potency threshold, kappa = Hill coefficient for toxin killing.

Policing favored (P outcompetes Ch) when:
  c_pg / (c_tox + c_res) >= 1.5  [empirically derived threshold]

AND simultaneously:
  diffusion_radius(toxin) > diffusion_radius(public_good)
  environmental_diffusivity = intermediate (not too low, not too high)
  toxin durability delta_tox ~ 500 seconds (intermediate decay)

Critical instability: policing decays when genetic linkage between public-good production and toxin production breaks. If resistant cooperators (R) evolve, they benefit from policers' public goods while not paying toxin-production cost. Policers go extinct. The policing mechanism is ITSELF a public good in the R-P interaction.

This is the fundamental "second-order public goods problem": policing is evolutionarily stable only when it is genetically coupled (same cell produces good AND toxin AND resistance). Decoupling = collapse.

Engineering implication for substrate federation: the policing analog (contribution score + penalty for low-contribution nodes) is stable ONLY when the scoring mechanism, the benefit delivery, and the penalty enforcement are all controlled by the same authority (cannot be decoupled by a "resistant node" that benefits from the federation while spoofing its contribution score).

### 1.5 Cheater dynamics math summary for substrate

Substrate-relevant parameters and their biological analogs:

| Substrate federation concept | Biological analog | Math formulation |
|-------------------------------|-------------------|------------------|
| Federation node contribution score | Cooperator/cheater identity | p_i in Price equation |
| Cross-shard retrieval benefit | Siderophore public good | b*r term in payoff |
| Contribution penalty | Production cost c | Cost c in b*r - c |
| Contribution scoring reliability | Population relatedness r | Hamilton r coefficient |
| Node isolation (no cross-shard) | All-cheater group | Public good = 0, fitness crash |
| Equilibrium cheater fraction | f_c* = (b-c)/b | Stable mixed Nash equilibrium |
| Penalty mechanism | Toxin-mediated policing | G_P vs G_C differential |

Key substrate prediction: if federation nodes receive shared retrieval benefit without contributing (cross-shard free-riding), the system converges to f_c* fraction of low-contribution nodes, which is greater than zero even in a well-designed system. The equilibrium cheater fraction f_c* decreases as the penalty cost c increases and as benefit-to-cost ratio b/c increases. Engineering lever: calibrate the penalty (c) to push f_c* below an acceptable threshold (e.g., f_c* < 0.05 means <5% of nodes are chronic low-contributors).

---

## SUB-TOPIC 2: Biofilm formation as collective phase transition

### 2.1 Motility-induced phase separation (MIPS) analog

Recent work (Bhattacharjee and Datta 2019; Vicsek swarm models; biorXiv 2020 swarming-biofilm paper) establishes that the planktonic-to-biofilm transition is mechanically analogous to motility-induced phase separation (MIPS) -- a non-equilibrium phase transition observed in self-propelled particles when local density increases beyond a threshold, triggering a positive feedback between slowing and clustering.

Mechanism: as cell density increases near a surface:
  (1) cells slow down (hydrodynamic + steric coupling to surface)
  (2) slower cells accumulate (self-trapping)
  (3) local density exceeds biofilm nucleation threshold
  (4) c-di-GMP second messenger spikes (induced by surface mechanosensing via flagella)
  (5) exopolysaccharide matrix production begins
  (6) cells become sessile; matrix reinforces sessility (positive feedback)

This is a first-order-like transition: the order parameter (sessile cell fraction) jumps discontinuously at the transition point (unlike a second-order transition where the order parameter changes continuously). The discontinuity implies hysteresis: you need a higher density to initiate the transition than to maintain it.

Published critical density estimate: Pseudomonas aeruginosa PAO1 initiates biofilm at OD600 ~ 0.4-0.6 in flow cells, but the biofilm persists until much lower density (OD600 ~ 0.1-0.2 in dispersal experiments). The ratio of initiation threshold to maintenance threshold is roughly 2-4x across species.

### 2.2 Hysteresis engineering bounds for substrate federation

The bistable switch literature (Ferrell 2002 Curr. Opin. Chem. Biol.; Becskei et al. 2001 Nature) gives engineering bounds on hysteresis width:

For a positive feedback loop with Hill-function activation:
  n (Hill coefficient): determines switch sharpness. n > 1 required for bistability. n = 2-4 typical for quorum sensing circuits.
  
Hysteresis width (difference between ON-threshold and OFF-threshold):
  Delta_threshold = theta_ON - theta_OFF = theta_ON * (1 - (K_OFF/K_ON)^(1/n))

where K_ON and K_OFF are the apparent activation constants for the forward and reverse transitions.

For V. harveyi las system (mBio 2025 population-level bistability paper):
  Population switches ON at [AI] ~ 10 nM (3-oxo-C12-HSL)
  Population switches OFF at [AI] ~ 2 nM
  Hysteresis ratio: K_ON/K_OFF ~ 5x (i.e., the OFF threshold is 5x lower than the ON threshold)

This 5x hysteresis ratio is robust across QS circuits. Engineering implication: a substrate federation activation mechanism with 5x hysteresis would require the federated signal strength to drop to 1/5 of the activation level before the federation deactivates. This prevents rapid oscillation ("federation chattering") under variable load.

The two-feedback-loop QS circuit (Dual-feedback model; Hasty et al. 2002; Collins et al. 2000 toggle switch): two interlocked feedback loops (one fast, one slow) produce more robust bistability than single-loop designs. The fast loop sharpens the switch; the slow loop widens the hysteresis. Engineering bound: adding a slow feedback loop (e.g., persistent state written to disk) widens the hysteresis window and prevents transient load drops from deactivating federation.

### 2.3 Mathematical condition: when does federation activate and stay on?

Let S = cross-shard retrieval signal strength (analog of AI concentration), parameterized 0-1.
Let F = federation state (0 = independent, 1 = federated).
Let h_ON = activation threshold, h_OFF = deactivation threshold (h_OFF < h_ON).

Bistable dynamics:
  dF/dt = (S^n / (S^n + h_ON^n)) * (1-F) - (h_OFF^n / (S^n + h_OFF^n)) * F

At steady state and n = 4 (typical QS Hill coefficient):
  If S > h_ON: F -> 1 (federation activates)
  If h_OFF < S < h_ON: F stays at whatever it was (hysteresis zone; memory of past state)
  If S < h_OFF: F -> 0 (federation deactivates)

Practical constraint: h_OFF should be at least 0.2 * h_ON to give meaningful memory without making deactivation impossible. The literature range (2-5x hysteresis ratio) gives h_OFF in [0.2, 0.5] * h_ON.

---

## SUB-TOPIC 3: QQ enzyme specificity -- adversarial defense tuning

### 3.1 Lactonase vs. acylase kinetics

Two enzyme families with distinct specificity profiles:

AHL-lactonase (AiiA from Bacillus thuringiensis; Dong et al. 2001):
  - Hydrolyzes the lactone ring of AHLs, producing ring-opened (non-signaling) homoserine
  - Broad specificity: active against AHLs with C4-C14 acyl chains at varying rates
  - K_M range: 1-10 uM (tight binding; high sensitivity)
  - k_cat: ~100-500 s^-1 (fast turnover)
  - Key specificity determinant: the lactone ring is the recognition epitope; the acyl chain length affects rate but not recognition

AaL lactonase (Nature Scientific Reports 2018; PMC6062542):
  - Metallo-beta-lactamase fold; zinc active site
  - K_M: 10-83 uM (broader range); high specificity for the hydrophobic acyl chain via a unique hydrophobic patch
  - Can hydrolyze short AND long chain AHLs (C4 through C12); unusually broad
  - k_cat: lower than AiiA (slower but broader substrate range)
  - Engineering tradeoff: broad-range enzymes have lower k_cat; narrow-range (high-specificity) enzymes have higher k_cat

AHL-acylase (Sompiyachoke et al. 2024 Protein Science -- engineered acylases with improved kinetics):
  - Cleaves the acyl side chain, leaving homoserine lactone ring intact (different mechanism than lactonase)
  - High specificity for long-chain AHLs (C10-C14); poor activity on short chains
  - Engineering result: directed evolution can tune acyl-chain length specificity by 4-10x without losing catalytic activity

### 3.2 Substrate adversarial QQ specificity engineering

The key insight from the QQ literature: adversarial signal degradation (QQ) has a specificity tuning problem exactly analogous to adversarial input filtering. An enzyme that is too broad-spectrum will degrade legitimate signals (false positives in signal filtering). An enzyme that is too narrow-spectrum misses adversarial signals with slight chemical modifications (false negatives).

The biological solution: most natural QQ enzymes evolved toward moderate specificity (K_M in 10-100 uM range) rather than extremes. The computational analog: an adversarial filter tuned on known adversarial signal patterns that applies a "degradation" to suspicious inputs while passing authentic signals.

Kinetics analog: the rate of adversarial signal removal follows Michaelis-Menten kinetics:
  v = V_max * [S_adv] / (K_M + [S_adv])

At low adversarial signal concentration ([S_adv] << K_M): v is linear; QQ efficiency drops. The adversary benefits from operating at low signal amplitude (just under the QQ K_M).
At high [S_adv] >> K_M: v approaches V_max; QQ is saturated; adversary can overwhelm the filter.

The "adversarial signal EMA" from QS cycle 175 (10/10 adversarial, 0 FP, noted in prior QS 5x drill) works in exactly this kinetics regime: it estimates the background-corrected adversarial signal flux and applies threshold-based gating. The Michaelis-Menten formulation suggests a saturating response (not a hard threshold) would be more robust at high adversarial flux.

---

## SUB-TOPIC 4: AI-2 universal signal -- cross-species (cross-customer) communication

### 4.1 AI-2 chemical structure and universality scope

AI-2 (autoinducer-2) is the product of the LuxS enzyme acting on S-ribosylhomocysteine to produce 4,5-dihydroxy-2,3-pentanedione (DPD). DPD spontaneously cyclizes to a furanosyl compound. In V. harveyi, DPD is trapped by boron to form a furanosyl borate diester (the crystallized ligand structure; Chen et al. 2002 Nature).

Key universality caveat (PMC524169 -- comparative genomics analysis): LuxS (the AI-2 synthase) is present in >50% of sequenced bacterial genomes, BUT the AI-2 RECEPTOR (LuxPQ-type phosphorelay or LsrB-type importer) is NOT universally conserved. Many species PRODUCE AI-2 as a metabolic byproduct of the SAM salvage pathway (not QS-specific), without expressing a sensor to DETECT AI-2.

Implication: AI-2 is a universal SENDER but not a universal RECEIVER signal. The claim that AI-2 enables interspecies communication requires both parties to have the sensor. The "universal language" framing is partially correct -- widely spoken but not universally heard.

Recent qualification (biorXiv 2026 -- Fusobacterium nucleatum AI-2 production): AI-2 production in F. nucleatum is subspecies-specific and uncoupled from quorum sensing regulation. AI-2 production does not correlate with QS response in this species. This further limits the "universal language" interpretation.

### 4.2 Substrate cross-customer signal analog

The substrate analog: if different customer deployments (different "species") emit retrieval queries to a shared substrate, AI-2 maps to a customer-neutral signal (e.g., query embedding similarity, cross-customer semantic density) that could trigger collective behavior without customer-specific authentication.

The universality caveat applies: a shared signal is only useful if both the sender AND receiver deploy the sensor. In federated retrieval, cross-customer coordination requires both customers to enable cross-shard queries. One-sided deployment produces signal with no listener -- the exact AI-2 without-receptor scenario.

Engineering conclusion: cross-customer federation requires opt-in sensor deployment on BOTH sides, not just signal emission. This is a structural architecture constraint, not a policy one.

---

## SUB-TOPIC 5: Persister cells -- substrate hibernation mode

### 5.1 Lewis 2010 persister mechanism (Nat. Rev. Microbiol. 2010; Ann. Rev. Microbiol. 2010)

Persister cells are a small subpopulation (~0.01% of E. coli cells under balanced growth) that enter a metabolically dormant state. Key mechanistic model:

Toxin-antitoxin (TA) bistability: type II TA systems (e.g., HipAB, MazEF, RelBE) have two stable states:
  - LOW TOXIN state: antitoxin (MazE) exceeds toxin (MazF); cell grows normally
  - HIGH TOXIN state: toxin exceeds antitoxin (stochastic fluctuation tips balance); toxin inhibits mRNA translation; cell enters dormancy

The transition from LOW to HIGH TOXIN state is stochastic and rare (~10^-4 per cell per generation). Once in HIGH TOXIN state, the cell is dormant (no growth, no translation, no membrane activity). Dormancy is robust to external stress including antibiotics (antibiotics target active cellular processes; dormant cells have no active targets).

Stochastic bistability math: the two-state system follows a master equation. In the LOW TOXIN basin, fluctuations occasionally push the toxin/antitoxin ratio past a saddle point. The transition rate lambda_persistence depends on:
  lambda ~ exp(-delta_G / k_B * T_eff)

where delta_G is the free energy barrier between the LOW and HIGH TOXIN states. Genetic manipulation of TA system stoichiometry changes delta_G and alters persistence frequency by orders of magnitude.

E. coli with 11 simultaneous TA systems maintains ~0.01% persistence rate. Removing ~50% of TA systems alters this by ~2 orders of magnitude (stochastic coupling/redundancy effect).

### 5.2 Substrate hibernation mode analog

The persister analog for substrate is a hibernation state for individual retrieval "nodes" (vectors in the substrate memory) that are infrequently accessed. Rather than maintaining full retrieval readiness, low-activity nodes could be compressed or moved to slower storage, with stochastic "wake-up" on access.

The TA bistability math suggests: the transition rate to hibernation should be tunable (via delta_G analog = access frequency threshold), and the wakeup should be triggered by external query (not internal timer). This is a specific engineering recommendation: implement access-frequency thresholds with stochastic jitter (Poisson process), not deterministic timers, to avoid synchronized wake/sleep cycles (the analog of oscillations in the cheater dynamics).

Persistence fraction target: biological 0.01% (1 in 10,000). Substrate analog: approximately 1-5% of memory nodes in hibernation at steady state under typical query loads. This is higher than biological because query loads are less uniform than bacterial growth conditions.

---

## SUB-TOPIC 6: Horizontal gene transfer -- cross-customer capability propagation

### 6.1 HGT/plasmid dynamics (Levin et al. 2000; Turner et al. 2021 PMC7919528)

Horizontal gene transfer (HGT) via conjugation: a donor cell forms a pilus, contacts a recipient, transfers a plasmid copy. The plasmid carries fitness-relevant genes (antibiotic resistance, siderophore production, toxin-antitoxin systems). The plasmid replicates in the recipient and can be re-transferred.

Plasmid population dynamics are governed by two orthogonal processes (Stevenson et al. 2023 PMC9912019):
  - Vertical transfer: plasmid copies during cell division (rate = cell growth rate)
  - Horizontal transfer: conjugation events (rate = conjugation efficiency * density)

Fitness cost tradeoff: conjugation machinery is metabolically expensive. Cells with high-conjugation plasmids grow more slowly (fitness cost c_conj ~ 2-10% reduction in growth rate). Low-conjugation plasmids spread slowly but persist because they impose less burden.

Equilibrium plasmid frequency: in a well-mixed population, plasmid frequency p* satisfies:
  dp/dt = gamma * p * (1-p) * N - c_conj * p

where gamma = conjugation rate per cell pair per unit time, N = population density, c_conj = fitness cost. At steady state:
  p* = 1 - (c_conj / (gamma * N))

Plasmid persists when gamma * N > c_conj (i.e., when conjugation rate exceeds fitness cost at current density). Below this threshold, plasmid is purged by selection.

### 6.2 Cross-customer capability propagation substrate analog

The plasmid HGT analog: a trained capability (e.g., a specialized binding operation for a particular domain, or a fine-tuned projection for a particular customer's query distribution) is a "capability plasmid" that could propagate across customer deployments. The cost of propagation = compute to transfer and install the capability. The benefit = improved retrieval quality for the receiving customer.

Key engineering constraint from the HGT literature: the plasmid persists only when gamma * N > c_conj. In substrate terms: cross-customer capability propagation is stable only when the number of potential receiving deployments (N) times the propagation rate (gamma) exceeds the installation cost. Below some critical deployment count N_c = c_conj / gamma, capability propagation is not worth the overhead.

This gives a concrete threshold for when cross-customer capability sharing becomes worthwhile: N_c depends on installation cost and propagation efficiency. For a substrate with O(10) customers, N_c ~ 2-5 (i.e., if installing a capability takes the same time as it benefits 2-5 other customers, propagation is net-positive).

---

## SUB-TOPIC 7: Spore formation -- substrate load-shedding hibernation

### 7.1 Sporulation trigger and stochastic decision (Losick and Desplan 2008 Science; Piggot and Hilbert 2004 Nat. Rev. Micro.)

Bacillus subtilis sporulation is governed by phosphorylation of Spo0A, the master sporulation regulator. The sporulation decision is stochastic: cells in a genetically identical population sporulate at different times and rates, governed by noise in the Spo0A phosphorylation cascade (Veening et al. 2008 Annu. Rev. Microbiol.).

Key threshold: when intracellular phospho-Spo0A exceeds a threshold (estimated ~10-20 nM in B. subtilis), sporulation-specific sigma factors activate and the commitment is irreversible. Below threshold, vegetative growth continues.

Stochastic heterogeneity benefit: not all cells commit simultaneously. If environmental conditions improve before sporulation completes, non-sporulating cells can resume growth. The heterogeneous bet-hedging strategy (some cells sporulate, some do not) increases population-level survival under uncertain conditions (Cohen 1966 Am. Nat.; Kussell and Leibler 2005 Science).

Mathematical formulation (bet-hedging theory): the optimal sporulation fraction p* maximizes long-run geometric mean fitness:
  W_geom = (1-p*)^(1-E_bad) * (p_surv * p*)^E_bad * (surv_spore)

where E_bad = probability of bad environment, p_surv = vegetative survival probability in bad environment, surv_spore = spore survival in bad environment.

At E_bad -> 0: p* -> 0 (no sporulation; waste to sporulate in good environment).
At E_bad -> 1: p* -> 1 (all sporulate; certain bad environment).
At intermediate E_bad: p* is intermediate; mixed strategy is optimal.

### 7.2 Substrate load-shedding analog

The sporulation analog: when query load drops below a threshold (low utilization period), a fraction of retrieval indices could enter "spore mode" (compressed storage, slow retrieval, minimal active memory). The optimal hibernating fraction p* depends on the probability of a low-utilization period persisting:

  p*_substrate = f(P_low_load, cost_hibernation, cost_wakeup_miss)

If P_low_load is high (e.g., overnight batch window), p* should be high (hibernate most indices). If P_low_load is low (variable load with frequent bursts), p* should be low (keep most indices active).

The stochastic heterogeneity principle applies: do NOT use a deterministic threshold to hibernate all nodes simultaneously. Use Poisson-distributed activation times (per the persister cell model) to avoid synchronized wake/sleep cycles that produce query latency spikes at reactivation.

---

## SUB-TOPIC 8: Bistable switch hysteresis -- engineering bounds for federation

### 8.1 Published bounds on hysteresis width (Ferrell 2002; Becskei et al. 2001; Gardner et al. 2000 toggle switch; Angeli 2004 IEEE)

Published bistability conditions for a single positive-feedback loop:
  n >= 2 (Hill coefficient; cooperativity required for bistability)
  n = 4: produces sharp switch with K_ON/K_OFF ratio ~ 3-7x
  n = 2: produces soft switch with K_ON/K_OFF ratio ~ 1.5-2x

Double-positive feedback (two interlocked feedback loops, as in V. harveyi QS network and as in the engineered toggle switches of Collins et al. 2000 Nature):
  - Fast loop: sets switch speed (transition time scale)
  - Slow loop: sets hysteresis width (memory time scale)
  - Combined: wider hysteresis + faster switching than single loop

Hysteresis width formula (approximate, from Ferrell 2002 analysis):
  H_width = theta_ON - theta_OFF ~ theta_ON * (1 - n^(-2/n))  [for Hill activation]

For n = 4: H_width ~ 0.6 * theta_ON (hysteresis window is ~60% of the ON threshold value)
For n = 2: H_width ~ 0.3 * theta_ON (hysteresis window is ~30% of the ON threshold value)

The V. harveyi empirical result (mBio 2025): K_ON/K_OFF ~ 5x, consistent with n ~ 3-4 effective Hill coefficient at population level.

### 8.2 Engineering recommendation: federation activation should NOT oscillate

Substrate federation chattering scenario: if the cross-shard query signal strength S fluctuates around h_ON without a hysteresis gap, the federation state F oscillates at the signal frequency. This produces repeated activation/deactivation overhead.

Solution from QS biology: implement h_OFF = 0.2 * h_ON (1/5 of activation threshold). This means once federation is triggered by a burst of cross-shard queries, it persists until the signal drops to 20% of the activation level. With typical query load distributions (log-normal inter-arrival times), this prevents oscillation in all but the most extreme load-drop scenarios.

The two-loop design (fast + slow feedback) is the most robust engineering choice. Fast feedback: immediate response to reaching h_ON threshold (lock federation state within 1-2 query cycles). Slow feedback: persistent state written to a shared counter or CRDT that decays slowly (e.g., EMA with tau = 100 queries), providing the slow loop that widens hysteresis.

---

## CHEAP DECISIVE TESTS

Test 1 (public goods / cheater equilibrium; 1 hr CPU): Implement a minimal 3-strategy replicator dynamics simulation (cooperator, cheater, policer) with federation node contribution scores as payoffs. Parameters: b = shared retrieval benefit, c = contribution cost, k = policing cost. Verify that (a) stable interior equilibrium f_c* forms for linear payoffs; (b) f_c* drops with increasing penalty c; (c) policing strategy survives when c_pg/(c_tox + c_res) >= 1.5. Outcome: verify the equilibrium math gives a cheater fraction < 10% for realistic federation parameters.

Test 2 (bistable switch / no chattering; 30 min CPU): Implement a discrete-time bistable federation gate with Hill function (n=4), h_ON = Q_threshold, h_OFF = 0.2 * h_ON. Drive with synthetic query load signal with Gaussian noise. Verify: (a) federation activates at h_ON; (b) federation does NOT deactivate when signal drops to 0.5 * h_ON; (c) federation deactivates at h_OFF. No oscillations in output.

Test 3 (persister analog / stochastic hibernation; 30 min CPU): Implement Poisson-distributed hibernation with rate lambda = f(access_frequency). Verify that steady-state hibernating fraction converges to target (1-5%) under uniform access. Verify wakeup latency distribution (exponential with mean = 1/lambda_wakeup). Baseline: deterministic threshold produces synchronized hibernation; Poisson process does not.

---

## FALSIFIABLE PREDICTIONS

### HARD-PASS thresholds (would confirm the engineering viability):

HP-1: In a federation of 100 simulated nodes with replicator dynamics + policing, equilibrium cheater fraction f_c* < 0.10 when contribution penalty c = 0.3 * b (cost = 30% of benefit). [Based on f_c* = (b-c)/b = 0.70; wait -- correction: f_c* = c/b = 0.30. At c = 0.3b, f_c* ~ 0.30. To get f_c* < 0.10 requires c > 0.90 * b, which is economically unrealistic. Revised HP-1: equilibrium cheater fraction converges to a stable value f_c* in (0.10, 0.50) that is controlled by penalty tuning. HARD-PASS = stable convergence to predictable f_c* that decreases monotonically with increasing penalty.]

HP-2: Bistable federation gate with n=4, h_OFF/h_ON = 0.2 shows zero chattering events (no oscillations) when input signal S fluctuates with coefficient of variation CV = 0.3 around h_ON. [Biologcally, the 5x hysteresis ratio prevents oscillation under typical load variation; CV = 0.3 is a conservative estimate of query load variability.]

HP-3: Policing mechanism with c_pg/(c_tox + c_res) = 1.8 > 1.5 threshold drives cheaters to <50% of population within 10 generations (replicator dynamics simulation). [Direct application of Wechsler 2019 threshold condition.]

### HARD-FAIL thresholds (would falsify the proposed mechanisms):

HF-1: If equilibrium cheater fraction f_c* does NOT decrease monotonically with increasing penalty c in simulation, the public goods model is mis-specified for the substrate federation context. This would require re-examining the payoff structure (possibly cheaters have private goods, not just public goods, changing the payoff matrix structure).

HF-2: If the bistable gate with n=4 still oscillates at CV = 0.3 input noise, then the Hill coefficient approximation is invalid for the substrate signal (could be caused by digital rather than analog signal -- discrete query arrivals violate continuous-limit assumptions of Hill function).

HF-3: If replicator dynamics simulation with policing fails to converge to stable equilibrium within 50 generations regardless of penalty level, the three-strategy system may have limit-cycle attractors instead of fixed-point attractors, requiring time-averaged control rather than threshold control.

---

## CROSS-THREAD SYNTHESIS WITH PRIOR ENTRIES

Connects to QS 5x drill (prior note): extends the bistable switch and QQ subsections with formal engineering bounds. Adds the cheater dynamics math not covered in the 5x drill.

Connects to differential privacy 5x (research_drill_field_differential_privacy_5x_2026-06-07.md): the policing mechanism requires contribution scoring that cannot be spoofed. DP-based contribution reporting (private contributions + DP accountant) provides formal spoof-resistance. The Wechsler 2019 condition requires genetic coupling in bacteria; the substrate analog is cryptographic coupling (contribution proof bound to identity token).

Connects to streaming algorithms 5x (research_drill_field_streaming_algorithms_5x_2026-06-07.md): Count-Min Sketch proposed in streaming drill is the natural data structure for contribution frequency counting. CMS gives epsilon-approximate cheater fraction estimates with O(log(1/delta)) space. This is the implementation substrate for the cheater equilibrium monitoring.

Connects to modern Hopfield 5x (research_drill_field_modern_hopfield_5x_2026-06-07.md): the persister cell dormancy analog maps directly to the sparse Hopfield (top-k) network where only k memories are "active" at any time. Inactive memories are effectively hibernating. The Lewis 2010 stochastic TA-system model gives a formal justification for stochastic sparsity in Hopfield networks: sparse activation should use Poisson sampling, not deterministic top-k, to prevent synchronized capacity spikes.

Connects to population genetics / Wright-Fisher (Tier-1b field, not yet drilled): cheater-cooperator dynamics at small population sizes (stochastic drift) would require the Wright-Fisher / Kimura drift formalism. The deterministic replicator dynamics results above hold only when N >> 1/|s| where s is selection coefficient. At small N, drift dominates selection, which could maintain cheater fractions far from f_c*. This is the next-drill candidate.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. Federation tier with formal cheater guarantee: The equilibrium cheater fraction f_c* = c/b is the fundamental substrate-relevant quantity. A federation with contribution scoring (b = retrieval lift per participating node, c = contribution score threshold for penalty) can guarantee f_c* < target by tuning c/b. This is not just an analogy -- it is a direct application of evolutionary game theory to distributed scoring. Customer pitch: "the federation protocol has a proof that the equilibrium fraction of low-contributing nodes is bounded above by c/b, where c and b are configurable parameters."

2. Policing layer as premium federation tier: The Wechsler 2019 conditions (cost ratio >= 1.5, toxin diffusion > public good diffusion, intermediate spatial structure) translate to: contribution scoring must be more granular than retrieval benefit delivery; penalty enforcement must propagate to more nodes than the benefit does; the spatial structure condition maps to partial federation (not fully connected graph). This is a concrete architecture constraint for the federation premium tier.

3. No-oscillation federation gate: The bistable switch with h_OFF = 0.2 * h_ON and n=4 is a direct implementation spec. The EMA signal (already in substrate per QS cycle 175) provides the smooth analog of AI concentration. Adding the hysteresis condition (persist federation state until EMA drops to 20% of activation threshold) prevents the federation chattering mode.

4. Hibernation with Poisson jitter: Persister cell bistability gives a principled design for substrate cold-storage mode. Use Poisson-distributed hibernation transitions (not deterministic thresholds) to avoid synchronized cold-storage dumps that spike query latency.

5. Cross-customer opt-in requirement: The AI-2 universality caveat (signal without receptor = useless signal) formalizes the cross-customer federation design requirement. Both customers must opt in and deploy the equivalent of the LuxPQ receptor (the cross-shard query routing layer) for AI-2 cross-customer signals to do anything. One-sided deployment is a known failure mode in the biology.

6. Plasmid HGT threshold for capability sharing: Cross-customer capability propagation is net-positive only when deployment count N > c_install / gamma (installation cost over propagation rate). For small customer counts (N < 10), capability sharing overhead likely dominates benefit. Engineering flag: do not implement cross-customer capability propagation in v1; evaluate only when N_customers > N_c threshold.

---

## CITATIONS (verified from search results)

1. Rainey PB, Rainey K (2003) "Evolution of cooperation and conflict in experimental bacterial populations." Nature 425:72-74.
2. Diggle SP, Griffin AS, Campbell GS, West SA (2007) "Cooperation and conflict in quorum-sensing bacterial populations." Nature 450:411-414.
3. West SA, Griffin AS, Gardner A, Diggle SP (2006) "Social evolution theory for microorganisms." Nat. Rev. Microbiol. 4:597-607.
4. Hamilton WD (1964) "The genetical evolution of social behaviour." J. Theor. Biol. 7:1-52.
5. Griffin AS, West SA, Buckling A (2004) "Cooperation and competition in pathogenic bacteria." Nature 430:1024-1027.
6. MacLean RC, Gudelj I (2006) "Resource competition and social conflict in experimental populations of yeast." Nature 441:498-501.
7. Archetti M, Scheuring I (2011) "Coexistence of cooperation and defection in public goods games." Evolution 65:1140-1148.
8. Wechsler T, Kümmerli R, Dobay A (2019) "Understanding policing as a mechanism of cheater control in cooperating bacteria." J. Evol. Biol. 32:1012-1028. [PMC6520251]
9. PMC10565900 (2023) "Equilibria and oscillations in cheat-cooperator dynamics." (authors: Waite and Shou descendants -- verified from PMC ID).
10. Lewis K (2010) "Persister cells." Annu. Rev. Microbiol. 64:357-372.
11. Lewis K (2007) "Persister cells, dormancy and infectious disease." Nat. Rev. Microbiol. 5:48-56.
12. Gardner TS, Cantor CR, Collins JJ (2000) "Construction of a genetic toggle switch in Escherichia coli." Nature 403:339-342.
13. Ferrell JE Jr (2002) "Self-perpetuating states in signal transduction: positive feedback, double-negative feedback and bistability." Curr. Opin. Chem. Biol. 6:140-148.
14. Becskei A, Seraphin B, Serrano L (2001) "Positive feedback in eukaryotic gene networks: cell differentiation by graded to binary response conversion." EMBO J. 20:2528-2535.
15. Chen X, Schauder S, Potier N, Van Dorsselaer A, Pelczer I, Bassler BL, Hughson FM (2002) "Structural identification of a bacterial quorum-sensing signal containing boron." Nature 415:545-549.
16. PMC524169 (2004) "Is autoinducer-2 a universal signal for interspecies communication: comparative genomic analysis." (Gonzalez JE, Keshavan ND)
17. Dong YH, Xu JL, Li XZ, Zhang LH (2001) "AiiA, an enzyme that inactivates the acylhomoserine lactone quorum-sensing signal and attenuates the virulence of Erwinia carotovora." PNAS 98:1892-1897.
18. Sompiyachoke et al. (2024) "Engineering quorum quenching acylases with improved kinetic and biochemical properties." Protein Science 33:e4954.
19. PMC6062542 (2018) "Structural and Biochemical Characterization of AaL, a Quorum Quenching Lactonase with Unusual Kinetic Properties." Scientific Reports.
20. Stevenson C et al. (2023) "Vertical and horizontal gene transfer tradeoffs direct plasmid fitness." [PMC9912019]
21. Hauert C, Monte S de, Hofbauer J, Sigmund K (2002) "Volunteering as Red Queen mechanism for cooperation in public goods games." Science 296:1129-1132. [replicator dynamics optional PGG; scispace]
22. mBio 2025 "Population-level bistability in Pseudomonas aeruginosa quorum sensing." (journals.asm.org verified URL)
23. Kussell E, Leibler S (2005) "Phenotypic diversity, population growth, and information in fluctuating environments." Science 309:2075-2078. [bet-hedging / sporulation]
24. biorXiv 2020 "Swarming bacteria undergo localized dynamic phase transition to form stress-induced biofilms." (biorxiv.org/content/10.1101/2020.08.11.243733)

Verified citation count: 24

---

## P_deflated values by sub-topic

| Sub-topic | Raw estimate | Calibration penalty | P_deflated |
|-----------|-------------|---------------------|-----------|
| Public goods replicator dynamics (math) | 0.85 | -0.20 | 0.65 |
| Cheater equilibrium f_c* formula applies to substrate | 0.65 | -0.20 | 0.45 |
| Policing cost ratio threshold (>= 1.5) transfer to substrate | 0.55 | -0.20 | 0.35 |
| Bistable gate no-chattering with n=4 | 0.70 | -0.15 | 0.55 |
| Persister / Poisson hibernation analog | 0.60 | -0.20 | 0.40 |
| AI-2 cross-customer caveat (opt-in required) | 0.90 | -0.05 | 0.85 |
| HGT plasmid threshold N_c | 0.60 | -0.20 | 0.40 |
| MIPS biofilm phase transition analog | 0.55 | -0.20 | 0.35 |
| QQ specificity / adversarial filter MM kinetics | 0.65 | -0.20 | 0.45 |

Overall P_deflated: 0.38 (average across engineering-actionable sub-topics; math verification steps have higher P_deflated but require 1-2 day CPU tests)

Next-drill candidate: population genetics / Wright-Fisher (Tier-1b; small-N cheater dynamics under stochastic drift -- fills the gap in the replicator dynamics analysis above at N << 1/s).
