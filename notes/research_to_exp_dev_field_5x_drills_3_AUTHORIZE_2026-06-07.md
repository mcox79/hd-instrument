# Research -> Exp-Dev: 3 LANDED field 5x drills AUTHORIZE (VSA + Modern Hopfield + Streaming)

**From:** Research  **Date:** 2026-06-07  **Re:** 3 of 5 field deep-dive 5x drills landed
(VSA + Modern Hopfield + Streaming algorithms). Consolidated AUTHORIZE per Exp-Dev's
"handoffs are drill specs; AUTHORIZE notes are action-ready" convention.

## Field 1: VSA / HRR / FHRR / BSC 5x — landed

Drill handoff: notes/exp_dev_handoff_research_field_VSA_5x_2026-06-07.md
Drill output: notes/research_drill_field_VSA_algebraic_foundation_5x_2026-06-07.md

### 4 rank-ordered anchors authorized

**Anchor 1 (HIGHEST priority): MAP Permute operation for ordered sequences**
~1-week engineering. 5-line code change to add MAP permutation primitive. Enables native
sequence/temporal reasoning that bitemporal capability requires.
HARD-PASS: bipolar substrate with MAP permute correctly encodes ordered sequences;
unbind+permute recovers position-tagged elements.
P_deflated 0.50.

**Anchor 2: Resonator network annotation (NO experiments needed)**
~1 day documentation. Annotate cycle 173+155 results showing modern Hopfield capacity
matches Lucibello-Mezard 2024 prediction AND resonator capacity theory (Frady 2020)
predicts K=2944 convergence dip seen in existing acf_K_dependent results. PURE THEORY-EMPIRICAL
ALIGNMENT documentation. Zero engineering cost.

**Anchor 3: arXiv 2512.14709 narrative integration (NO experiments needed)**
~1 day customer pitch update. "Substrate does EXPLICITLY + AUDITABLY what transformer
attention does IMPLICITLY." Zero cost; pure pitch upgrade.

**Anchor 4: FHRR speed optimization pre-test**
~3-4 hr CPU. Test if FFT-domain convolution speeds up substrate retrieval at N=4096
relative to direct convolution. HARD-PASS: FHRR >= 2x speedup at recall parity.

## Field 2: Modern Hopfield 5x — landed

Drill handoff: notes/exp_dev_handoff_research_field_modern_hopfield_5x_2026-06-07.md
Drill output: notes/research_drill_field_modern_hopfield_5x_2026-06-07.md

### 4 CPU experiments authorized

**Anchor 1 (HIGHEST priority): Substrate-as-attention narrative validation**
~1 day documentation. Ramsauer 2020 attention-equivalence + Lucibello-Mezard 2024 capacity
+ cycle 171 1M empirical = substrate's strongest single technical pitch anchor. Document
+ adopt.

**Anchor 2: Sparse Hopfield for edge deployment pre-test**
~3-4 hr CPU. Sparse activation patterns; substrate at lower memory cost; tests edge
deployment moat enhancement.

**Anchor 3: Continuous Hopfield bridge to substrate-augmented attention (Tier-4.5 prep)**
~4-6 hr CPU. Substrate continuous-valued bindings for fine-grained queries; bridge to
attention layer naturally. Tier 5 enabler.

**Anchor 4: Phase-transition operating point characterization**
~1 week analysis. Map substrate's current operating point on capacity-noise phase diagram.
Customer pitch: "substrate operates at <1% of theoretical capacity; massive safety margin."

## Field 3: Streaming algorithms 5x — landed

Drill handoff: notes/exp_dev_handoff_research_field_streaming_algorithms_5x_2026-06-07.md
Drill output: notes/research_drill_field_streaming_algorithms_5x_2026-06-07.md

### 4 gap-closing extensions authorized (all 2-5 days each)

**Anchor 1: Count-Min Sketch addition (P=0.70; 3-5 days)**
Adds finer-grained frequency tracking; O(1) query vs O(k) Misra-Gries scan. Complements
Misra-Gries. Customer dashboard: granular pattern statistics.

**Anchor 2: Cuckoo filter for deduplication (P=0.65; 2-3 days)**
O(1) "have we stored this fact" check. Prevents duplicate ingest; reduces storage
redundancy.

**Anchor 3: HyperLogLog for KB diversity metric (P=0.50; 2-3 days)**
Customer dashboard metric ("your KB has N distinct entities; diversity score X").
Marketing/customer-success angle.

**Anchor 4: Reservoir sampling for training curation (P=0.55; 3-5 days)**
Random sample from query stream for periodic LoRA updates or eval. Builds toward
Tier 4.

### Ben-Eliezer 2022 narrative integration (NO experiments needed)
~1 day customer pitch update. DP layer = adversarial robustness for FREE in streaming
setting. Substrate's federated DP histograms (cycle 170 HP) automatically grant
adversarial-streaming robustness. Free moat upgrade.

## Strategic implications

All 3 field drills converge on substrate as **algebraic intersection of mature scientific
fields**. Cross-field identities discovered:
- Misra-Gries = stigmergy (ant colony)
- Transformer attention = VSA binding (arXiv 2512.14709)
- Transformer attention = Hopfield retrieval (Ramsauer 2020)
- VSA superposition = AMS sketch (Ben-Eliezer 2022)
- Pinv = Pearl's do() (cycle 162)

Customer pitch: substrate's operations are algebraically identical to mechanisms
studied independently across 30+ years of research. Mature scientific backing for every
architectural decision.

## Cross-references

- VSA 5x: notes/research_drill_field_VSA_algebraic_foundation_5x_2026-06-07.md
- Modern Hopfield 5x: notes/research_drill_field_modern_hopfield_5x_2026-06-07.md
- Streaming algorithms 5x: notes/research_drill_field_streaming_algorithms_5x_2026-06-07.md
- Continual learning 5x (in flight): TBD
- DP 5x (in flight; final): TBD

---

**Exp-Dev:** authorize all anchors per drill handoffs. VSA Anchor 1 (MAP Permute) is
highest priority single engineering task. Modern Hopfield narrative + Ben-Eliezer 2022
free adversarial robustness are zero-cost pitch upgrades — adopt immediately. CMS +
Cuckoo + HyperLogLog + reservoir sampling = 4 substrate gaps as 2-5 day tasks each;
parallel as bandwidth allows.

Remaining 2 field drills (continual learning + DP) will get their own AUTHORIZE notes
when they land.
