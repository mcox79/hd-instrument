# Research -> Exp-Dev: 8 DEEPER drills CONSOLIDATED AUTHORIZE

**From:** Research  **Date:** 2026-06-07 ~22:15  **Re:** Per user audit "did you route all
identified experiments + develop into viable experiments?" — filing consolidated AUTHORIZE
for all 8 DEEPER drill extensions NOT yet covered by dedicated AUTHORIZE notes.

Already routed (NOT repeating): resonator PRIORITY 0; 3 substrate-native multi-hop paths
(resonator + streaming betweenness + multi-scale SR); OAS critical seeding mitigation;
overnight batch 15 anchors; multi-hop RESCUE 4 paths.

## PRIORITY 0 (correctness gates; ship-immediately; zero-cost)

### Anchor 0.1: TAU-MIN-FLOOR-AUDIT (correctness gate)
- Source: Ant Colony DEEPER 3x
- Substrate-product reading: Dorigo-Blum 2005 theorem requires Misra-Gries counter floor
  strictly > 0 for convergence. If substrate MG decay can reach exactly 0, the cycle 175
  ant-colony-decay 83x HP convergence guarantee is BROKEN. One-line fix: min_count = 1.
- Tier: LOCAL CPU AUDIT (1 hr)
- HARD-PASS: substrate MG counter floor always >= 1 in code; cycle 175 result holds
- HARD-FAIL: counter can reach 0; immediate one-line patch required

### Anchor 0.2: Variable cosine threshold dorsal-ventral (zero-cost ship-immediately)
- Source: Hippocampal DEEPER 3x
- Substrate-product reading: substrate already has cosine threshold; add tunable parameter;
  threshold=0.85 = dorsal (precise; few results); threshold=0.65 = ventral (exploratory;
  more results); zero code changes, just config exposure
- Tier: LOCAL CPU SMOKE (2-3 hr; no code change)
- HARD-PASS: threshold=0.85 hits >= 95% precision@1; threshold=0.65 expands result set >= 2x
- Customer pitch: "dial substrate from precise to exploratory at zero cost"

### Anchor 0.3: Imagination-mode noise injection (one-line change)
- Source: Hippocampal DEEPER 3x
- Substrate-product reading: hippocampus uses same W matrix for retrieval AND imagination via
  noise injection on query; substrate adds noise to query vector, gets candidate
  "imagined" facts; one-line change
- Tier: LOCAL CPU SMOKE (1-2 hr)
- HARD-PASS: noise-injected queries return semantically-related but non-exact-match candidates >= 70%

## PRIORITY 1 (high-value engineering)

### Anchor 1.1: Two-tier confidence (retrieval vs adversarial) + age-weighted decay
- Source: Immune DEEPER 3x (OAS mitigation deepening)
- Substrate-product reading: separate c_retrieval (undecayed) from c_adversarial (age-weighted
  alpha=0.95/defrag); seeded bindings keep retrieval quality but lose competitive advantage
  in contradiction ranking; 2025 eLife mechanism
- Tier: LOCAL CPU (3-4 hr)
- HARD-PASS: customer-overlay bindings win conflict competitions >= 90% with mitigation vs <= 50% without

### Anchor 1.2: Burial-depth invariant for load-bearing bindings
- Source: Immune DEEPER 3x (bnAb biology)
- Substrate-product reading: bindings present in >= 90% of concept paraphrase variants are
  load-bearing; EXEMPT from decay; reconciles OAS mitigation with cross-variant generalization
- Tier: LOCAL CPU (2-3 hr)
- HARD-PASS: load-bearing detection accuracy >= 95%; protected bindings survive decay cycles

### Anchor 1.3: int8 lossless storage (Modern Hopfield)
- Source: Modern Hopfield DEEPER 5x (synaptic-noise formula proof)
- Substrate-product reading: int8 vs bf16 substrate storage; 4x memory savings; lossless per
  synaptic-noise analysis at production noise level; combines with cycle 175 fp16=bf16 HP
- Tier: LOCAL CPU (2-3 hr)
- HARD-PASS: int8 substrate retains >= 95% recall vs bf16 at production noise

### Anchor 1.4: Wasserstein alpha calibration (per-customer Misra-Gries decay)
- Source: Ant Colony DEEPER 3x (arxiv 2601.04111 formal proof)
- Substrate-product reading: alpha = 1/T_halflife from Wasserstein gradient descent theorem;
  customer-tunable from query distribution entropy; auto-calibration
- Tier: LOCAL CPU (1-2 hr; algebraic + simulation)
- HARD-PASS: auto-calibrated alpha gives 80%+ optimal drift detection across 5 simulated
  customer profiles

### Anchor 1.5: Smooth Binary Mechanism (DP continual release)
- Source: Streaming/DP DEEPER 5x
- Substrate-product reading: 285x continual privacy budget savings for substrate's
  continual release of count/sum statistics; arxiv 2306.09666; integrate with Google
  dp_accounting
- Tier: LOCAL CPU (2-3 hr)
- HARD-PASS: substrate continual release at T=1000 rounds achieves 285x lower epsilon
  than naive composition

### Anchor 1.6: LARS-VSA rule storage validation
- Source: VSA NeSy DEEPER 5x (LARS-VSA 2024)
- Substrate-product reading: substrate stores rules as bipolar bundles with auditable
  unbind-chain application; 17x memory efficiency + 25x attention speedup reported
- Tier: LOCAL CPU (3-4 hr)
- HARD-PASS: substrate as rule engine matches LARS-VSA 17x memory + 25x speed at recall parity

## PRIORITY 2 (medium-value extensions)

### Anchor 2.1: Sparse Vector Technique (SVT) for dashboard
- Source: Streaming/DP DEEPER 5x
- Tier: LOCAL CPU (~2 hr); 50x epsilon savings for dashboard queries above threshold

### Anchor 2.2: Mergeable Misra-Gries for federation
- Source: Streaming/DP DEEPER 5x
- Tier: LOCAL CPU (~2 hr); federation aggregation primitive

### Anchor 2.3: DP-CMS adversarial robustness
- Source: Streaming/DP DEEPER 5x
- Tier: LOCAL CPU (~2 hr); zero space cost adversarial-robust CMS

### Anchor 2.4: Two-speed adversarial memory (trained innate immunity)
- Source: Immune DEEPER 3x
- Tier: LOCAL CPU (~3 hr); day-1 vs day-7 TPR improvement claim; zero labeled training

### Anchor 2.5: Jerne anti-idiotype coherence signal
- Source: Immune DEEPER 3x
- Tier: LOCAL CPU (~3 hr); network consistency prior on adversarial alerts; P_deflated=0.25 speculative

### Anchor 2.6: Allelopathic CMN trust-reduction
- Source: Mycorrhizal DEEPER 3x
- Tier: LOCAL CPU (~2 hr); network-wide trust-reduction protocol for known-false assertions

### Anchor 2.7: Grasso 2025 coupling design simulation
- Source: Mycorrhizal DEEPER 3x
- Tier: LOCAL CPU (~30 min Python simulation); substrate-LLM mutualism stability validation
- HARD-PASS: simulated coupling reaches mutualistic equilibrium without enforcement

### Anchor 2.8: Standing pre-alert (MIR analog)
- Source: Mycorrhizal DEEPER 3x
- Tier: LOCAL CPU (~1 hr); architecturally separate from event-triggered alert

### Anchor 2.9: Two-layer federated routing (within/cross domain DP)
- Source: Mycorrhizal DEEPER 3x
- Tier: LOCAL CPU (~3 hr); within-domain low-DP-noise + cross-domain high-DP-noise; 40-60% privacy budget reduction

### Anchor 2.10: Replicator dynamics cheater equilibrium validation
- Source: QS DEEPER 3x
- Tier: LOCAL CPU (~2 hr); f_c* = c/b stable mixed Nash; penalty-controlled federation

### Anchor 2.11: Bistable gate n=4 h_OFF=0.2*h_ON
- Source: QS DEEPER 3x
- Tier: LOCAL CPU (~2 hr); federation activation hysteresis; prevents chattering

### Anchor 2.12: Persister Poisson hibernation
- Source: QS DEEPER 3x
- Tier: LOCAL CPU (~2 hr); prevents synchronized latency spikes

### Anchor 2.13: K=12 diffusion trajectory noise budget validation
- Source: Modern Hopfield DEEPER 5x
- Tier: LOCAL CPU (~2 hr); substrate K-hop = 12-step diffusion with 8% noise/hop budget

### Anchor 2.14: NeurIPS 2025 MHA hidden-state attention-equivalence
- Source: Modern Hopfield DEEPER 5x
- Tier: LOCAL CPU (~1 day analysis); tighter mathematical bound for substrate-as-attention pitch

### Anchor 2.15: Synthesis mode (domain-crossover query)
- Source: Hippocampal DEEPER 3x
- Tier: LOCAL CPU (~3-5 days); finds bridges in customer's own KB

### Anchor 2.16: Replay index for counterfactual do() ordered sequences
- Source: Hippocampal DEEPER 3x
- Tier: LOCAL CPU (~3-4 days); extends cycle 175 Wish 1 HP to sequence counterfactuals

### Anchor 2.17: Priority-weighted replay gate
- Source: Hippocampal DEEPER 3x
- Tier: LOCAL CPU (~3 days); high-value bindings strengthened via replay frequency

### Anchor 2.18: Differentiable VSA (encoder-substrate joint gradient)
- Source: VSA NeSy DEEPER 5x
- Tier: LOCAL CPU (~3-4 days); P_deflated=0.22 lowest confidence; needs Pythia-scale pre-test

### Anchor 2.19: LLM-proposes / substrate-verifies architecture
- Source: VSA NeSy DEEPER 5x (arXiv 2512.14709 enabler)
- Tier: LOCAL CPU (~3-4 days); attention = VSA binding identity exploited for verification layer

## PRIORITY 3 (lower-value or research-stage)

### Anchor 3.1: Percolation K-hop cliff universality class
- Sources: Modern Hopfield DEEPER + Mycorrhizal DEEPER (multiple drills flag this)
- Tier: research drill required (NOT empirical); next-drill candidate per multiple sources

### Anchor 3.2: Wright-Fisher small-N stochastic drift in cheater dynamics
- Source: QS DEEPER 3x; next-drill candidate
- Tier: research drill required

### Anchor 3.3: Neuromorphic substrate (Loihi / TrueNorth)
- Source: VSA NeSy DEEPER 5x
- Tier: hardware-dependent; not local CPU testable

## Summary

Total NEW anchors authorized in this consolidated routing: 27
- Priority 0 (ship immediate): 3
- Priority 1 (high-value engineering): 6
- Priority 2 (medium-value extensions): 19
- Priority 3 (research/hardware-dependent): 3

Combined with prior routings (overnight batch 15 + multi-hop RESCUE 4 + 3-NATIVE-PATHS 3 +
resonator PRIORITY 0 + OAS critical 1), total today: ~50 action-ready anchors filed.

## Cross-references

- All 8 DEEPER drill files in notes/research_drill_field_*_DEEPER_*_2026-06-07.md and
  notes/research_drill_natural_analog_*_DEEPER_*_2026-06-07.md
- Drill-agent-filed handoffs in notes/exp_dev_handoff_research_*_DEEPER_*_2026-06-07.md
- Existing AUTHORIZEs: notes/research_to_exp_dev_*_2026-06-07.md
- Overnight batch: notes/exp_dev_handoff_research_overnight_2026-06-07_batch.md

---

**Exp-Dev:** authorize all anchors per priority order. Anchor 0.1 (TAU-MIN-FLOOR-AUDIT)
is a SUBSTRATE CORRECTNESS gate — 1 hr to confirm cycle 175 ant-colony-decay HP
convergence guarantee holds. Anchors 0.2 + 0.3 are zero-cost / one-line ships
immediately. Priority 1 anchors are highest-yield engineering. Priority 2 anchors are
medium-value extensions; pick best per queue capacity. Priority 3 require research
drills first.
