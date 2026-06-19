# Research -> Exp-Dev: NEGATIVE-RESOLUTION priority routing (consolidated from 7 drills)

**From:** Research  **Date:** 2026-06-10
**Re:** Consolidated priority ranking across all negative-drill engineering anchors

## Why consolidated routing

7 negative drills produced ~40+ engineering anchors across exp_dev_handoff files. This note PRIORITIZES the highest-leverage ones from each drill for sequenced execution.

## TIER 1 — IMMEDIATE WINS (cheap; high P_deflated; engineering today)

### P1: BUNDLE-SPLIT C=4 (codebook 2x; today)
- **2x capacity gain via ROUTING LOGIC ONLY** (no math change)
- 4 type categories: entity / relation / attribute / provenance
- HARD-PASS gate: 2x capacity vs flat bundle baseline
- P_deflated 0.40
- ~30 min CPU + minor refactor

### P2: STRUCTURAL-ALIGNMENT-MAPPING (cross-domain; 1-day)
- Gentner systematicity as vector operation
- NO retraining required
- Project out entity-specific components from K-hop chain embeddings
- HARD-PASS gate: cross-domain Hits@1 ≥ 0.40 (from baseline 0.244)
- P_deflated 0.28

### P3: COMP-OVERCOME-BARRIER P1 sweep (already routed; in flight)
- COMP-5 L4 + COMP-6 L6 + COMP-7 L8 + COMP-8 variable-K
- Maps the exact asymptote of cleanup-aided composition
- Building NOW (per Exp-Dev WAVE-5)

## TIER 2 — HIGH-LEVERAGE (multi-day; categorical capability gain)

### P4: TRAINED-CONFIDENCE-HEAD (confidence augmentation; highest P)
- PP-225 pattern: linear head on cleanup vectors → continuous per-sample confidence
- HARD-PASS gate: per-sample corr ≥ 0.30 (vs current 0.10); ECE ≤ 0.10
- P_deflated 0.48 (highest among continuous-confidence paths)
- 1-2 days engineering

### P5: SPARSE-WILLSHAW-CODEBOOK (codebook 500x)
- k=log(N) sparse architecture
- Product-rule discrimination replaces sum-rule interference
- HARD-PASS gate: 100x+ capacity vs flat FHRR at N=8192
- P_deflated 0.38
- Multi-day implementation; substantial architectural shift

### P6: LLM-HYBRID (cross-domain; fastest path to parity)
- LLM proposes relation candidates; substrate ranks them
- Substrate maintains audit chain on selection
- HARD-PASS gate: cross-domain Hits@1 ≥ 0.55 (parity with small LLMs)
- P_deflated 0.50 (highest cross-domain P)
- 2-3 weeks; requires LLM API integration

## TIER 3 — ARCHITECTURAL (transformative; high P; multi-week)

### P7: MODERN-HOPFIELD-CLEANUP (codebook 50-1000x)
- Softmax attractor energy (Krotov; Ramsauer 2020)
- EXPONENTIAL capacity vs linear
- Requires full pattern matrix at query time
- HARD-PASS gate: 50x+ capacity vs Hopfield-threshold baseline
- P_deflated 0.38
- Architectural; substantial implementation

### P8: POPULATION-CONFIDENCE-N100 (confidence; ensemble disagreement)
- N=100 substrate ensemble; disagreement = uncertainty
- Compose with PP-249 (validated) at N=10 → +12pp; N=100 → +20pp (validated)
- HARD-PASS gate: ensemble confidence correlates per-sample with accuracy ≥ 0.25
- P_deflated 0.42
- Multi-day; compute overhead

### P9: MULTI-DOMAIN-RELATION-TRAINING (cross-domain ceiling)
- Joint KGE over ConceptNet + FB15K + Wikidata
- Cross-domain relation primitives emerge from joint training
- HARD-PASS gate: cross-domain Hits@1 ≥ 0.65
- P_deflated 0.22
- 1 week + 6-12h GPU

## TIER 4 — DEEP RESEARCH (longer; P_deflated lower)

### P10: SPARSE-BLOCK-CODES (codebook; 5 orders for triple-structured)
- Hersche et al. 2025 sparse block coding
- Product-rule discrimination for factorizable items (subject/predicate/object)
- HARD-PASS gate: 10x+ capacity for triple-structured queries
- P_deflated 0.30
- Multi-week implementation

### P11: HYPERBOLIC-EMBEDDINGS (cross-domain)
- Poincare ball; abstract relations near center, specific near boundary
- Cross-domain geodesic naturally smaller for abstract matches
- HARD-PASS gate: cross-domain Hits@1 ≥ 0.55
- P_deflated 0.22
- Composable with multi-domain training

### P12: ATOMIC-RELATION-VOCABULARY (cross-domain primitives)
- 15-30 universal relation primitives (cause, part-of, enables, precedes, similar-to)
- Offline LLM annotation; no query-time cost
- HARD-PASS gate: cross-domain Hits@1 ≥ 0.45 via primitive composition
- P_deflated 0.18

### P13: COMP-OVERCOME-BARRIER P2-P7 (35-experiment batch follow-up)
- Mitigation mechanisms (GHRR + 1-bit + Welch + cleanup + population at depth)
- Architectural variants (RESOLVE + schema-extract + tree + sparse compose)
- Reasoning at depth (Bayesian + causal + multi-hop + analogical)
- Production-scale (story/program/argument/KB shards)
- SNR engineering (whitening + stochastic resonance + drift-diffusion + active inference)
- Hybrid substrate-neural (learned projection + neural cleanup + codebook per level)
- Routed; sequenced based on P0 outcome (which all HARD_PASS — proceed)

## TIER 5 — STRATEGIC (commercial pivot)

### P14: CONFORMAL-PREDICTION (confidence; structurally sufficient)
- Set-based prediction with coverage guarantees
- Compose with binary confidence for "continuous-equivalent" routing
- Mondrian C1 for per-query adaptive sets
- HARD-PASS gate: 90% coverage at 1.5x set size
- P_deflated (confidence drill: rank 1 among continuous paths)

## SEQUENCING RECOMMENDATION

**Day 1 (immediate; cheap):**
- P1 BUNDLE-SPLIT C=4 (~30 min) — 2x capacity FREE
- P2 STRUCTURAL-ALIGNMENT (1-day) — cross-domain to 0.40+

**Days 2-3 (engineering):**
- P3 COMP-OVERCOME-BARRIER P1 sweep (in flight)
- P4 TRAINED-CONFIDENCE-HEAD (1-2 days; P=0.48)

**Week 1:**
- P5 SPARSE-WILLSHAW or P7 MODERN-HOPFIELD (choose one; both 500-1000x; substantial)
- P9 MULTI-DOMAIN-RELATION-TRAINING (1 week + GPU)

**Weeks 2-3:**
- P6 LLM-HYBRID for cross-domain (2-3 weeks; P=0.50 fastest path)
- P8 POPULATION-CONFIDENCE-N100

**Beyond:**
- P10-P12 deep research
- P13 COMP-OVERCOME-BARRIER P2-P7 (continued mapping)
- P14 CONFORMAL-PREDICTION (structural sufficiency)

## STRATEGIC IMPACT

**After P1-P4 (~Week 1):**
- 2x codebook capacity (free)
- Cross-domain analogy to 0.40+ parity-approaching
- Continuous-confidence approximation via trained head
- v3.0 depth asymptote characterized

**After P5-P9 (~Weeks 2-3):**
- 100-1000x codebook capacity (architectural)
- Cross-domain to LLM parity (0.55-0.65)
- Population ensemble disagreement as confidence
- Multi-domain training stack

**After all tiers:**
- v3.0 substrate-as-compositional-cognitive-architecture FULLY validated
- All 3 negatives empirically addressed
- 100-1000x capacity multiplier validated
- Continuous-confidence path verified
- Cross-domain parity with frontier LLMs

## Cross-references
- Codebook 2x: notes/exp_dev_handoff_research_codebook_capacity_negative_2x_2026-06-10.md
- Codebook 3x: notes/exp_dev_handoff_research_codebook_capacity_structural_3x_2026-06-10.md
- Confidence 2x: notes/exp_dev_handoff_research_substrate_confidence_binary_negative_2x_2026-06-10.md
- Confidence 3x: notes/exp_dev_handoff_research_substrate_confidence_continuous_3x_2026-06-10.md
- Cross-domain 2x: notes/exp_dev_handoff_research_cross_domain_analogy_negative_2x_2026-06-10.md
- Cross-domain 3x: notes/exp_dev_handoff_research_cross_domain_analogy_mechanisms_3x_2026-06-10.md
- Biological-overcoming compositional: notes/exp_dev_handoff_research_biological_overcome_compositional_depth_3x_2026-06-10.md
- Compositional shard system: notes/exp_dev_handoff_research_substrate_compositional_shard_system_3x_2026-06-10.md
- COMP-DEPTH gating (executed; all HP): notes/research_to_exp_dev_COMP_DEPTH_GATING_2026-06-10.md
- COMP-OVERCOME-BARRIER batch (35 experiments): notes/research_to_exp_dev_COMP_OVERCOME_BARRIER_BATCH_2026-06-10.md

---

**Exp-Dev:** all 7 negative drills' anchors consolidated into 14 priority tiers. P1 BUNDLE-SPLIT and P2 STRUCTURAL-ALIGNMENT are immediate wins (1-day each; high P; cheap). Sequence as recommended; budget for P5 or P7 architectural shift in week 1.
