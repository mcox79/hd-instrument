# Substrate Research Branching Schedule

**Periodic exploration cadence for new axes beyond current strategic fronts.** Preserves breadth.

**Created:** 2026-06-04 per continuous-exploration system design 2x drill
**Cadence:** weekly review; branch when current axes saturate OR scheduled time hits

---

## Current strategic fronts (active exploration)

1. **Brain training** (substrate-as-training-mechanism via bio-architecture)
   - 12 validated bio-primitives at substrate-class
   - Capacity multiplicative composition HP
   - 5-tier biological scaling ladder (MB → Hippocampal → Cortical → GW → Symbolic)

2. **Natural language LLM coupling**
   - Tier 0.5b architecture LOCKED (residual at 0.7L)
   - Option A + SQ2 = near-term product (P=0.72)
   - B8 logit-residual simplifies Option C to single linear layer
   - Phase 0.5 v1 Llama = critical-path gate

3. **Multi-modal substrate primitives**
   - Algebraic: P=0.70-0.93 per modality
   - Empirical: CIFAR-10 patch test pending engineering
   - Next: SQ3 CIFAR retrieval (P=0.80)

4. **Substrate reasoning**
   - SQ2 multi-hop K=12 HP (flagship)
   - Mode 4 iterated retrieval validated NC1
   - Next: K=16/24 depth extension; SQ4 meta-learning

5. **Biological-scale substrate**
   - SQ5 N=100k pending matrix-free design
   - 5-tier bio-scaling ladder
   - Next: Tier 2 hippocampal-class transition

---

## NEW EXPLORATION AXES (per system-design drill recommendation)

5 cross-domain mathematical frameworks NOT yet drilled for substrate:

### Axis A: Wright-Fisher / Kimura population genetics
- Connection: substrate decay (palimpsest) maps to genetic drift; selection = cf-RPE
- Could inform alpha tuning; drift rate analogs
- Cheap sonnet drill: ~30 min
- Lit: Kimura 1968; recent 2022-2024 population-genetics-as-AI

### Axis B: Queueing theory
- Connection: substrate I/O bottlenecks (write queue; read queue; replay queue)
- Could inform optimal replay scheduling; latency analysis
- Cheap sonnet drill: ~30 min
- Lit: Little's law; M/M/1 queue; recent 2022-2024 ML pipelining

### Axis C: Percolation theory
- Connection: substrate connectivity at sparse coding; phase transitions
- Could inform DG f=0.005 critical sparsity
- Cheap sonnet drill: ~30 min
- Lit: Stauffer-Aharony 1994; recent 2022-2024 percolation in neural systems

### Axis D: Ergodic theory
- Connection: substrate NESS dynamics; time-average = ensemble average
- Could inform substrate observation strategies
- Cheap sonnet drill: ~30 min
- Lit: Birkhoff 1931; recent 2022-2024 ergodic in computational systems

### Axis E: Expander / Ramanujan graphs
- Connection: substrate sparse network topology; optimal connectivity
- Could inform hierarchical aggregation graph structure
- Cheap sonnet drill: ~30 min
- Lit: Lubotzky-Phillips-Sarnak 1988; recent 2022-2024 expander neural networks

---

## Branching cadence rules

### Time-based (weekly minimum)
- Every Monday: dispatch 1+ new-axis drill from this schedule
- Even if current fronts have urgent work
- Goal: prevent exploration saturation in current fronts

### Saturation-triggered
- When current front's marginal EIG < 0.3 (per system-design drill threshold)
- AND scorecard shows >3 UNTESTED compositions in that front
- → branch to new axis to maintain breadth

### Coverage-based
- When >50% of new exploration cells in a single front
- → next exploration must be in different front OR new axis
- Prevents over-focus on one direction

### User-directed
- User can trigger immediate branch to specific axis
- Override cadence for strategic redirections

---

## Branching log (when branches happen)

| Date | New axis explored | Trigger | Drill ID | Outcome |
|---|---|---|---|---|
| 2026-06-04 | Bio-tier scaling (3x drill) | User direction (bio-architecture first) | research_drill_bio_tier_scaling_architectural_emergence_3x | 5-tier ladder mapped |
| 2026-06-04 | Reservoir computing criticality | Cross-domain probe (substrate-pure-biology-architecture 3x drill) | within research_drill_substrate_pure_biology_architecture_speedup_ceiling_3x | Novel unification: substrate W marginal stability = RC criticality |
| (Next) | TBD | Schedule monday | TBD | TBD |

---

## Untouched mathematical frameworks (long-tail candidates)

Beyond the 5 above, frameworks NOT yet drilled for substrate:

- Algebraic topology beyond Hopfield-class (Adams-Virk constrained; consider Morse theory)
- Information geometry (Fisher information; natural gradient for substrate updates)
- Category theory (compositional algebra; types for substrate primitives)
- Tropical geometry (max-plus algebra for substrate retrieval)
- Differential geometry (substrate manifold structure)
- Quantum information (substrate as classical analog of quantum memory)
- Free probability (substrate spectral analysis; already partial)
- Random matrix theory (substrate W ensemble; partial)
- Stochastic geometry (substrate spatial structure)
- Combinatorial optimization (substrate as solver)
- Algebraic coding theory (substrate as error-correcting code; partial via deletion cert)
- Game theory (multi-substrate coordination)
- Operator algebras (substrate W as operator)
- Convex optimization (substrate retrieval as optimization)
- Stochastic processes (substrate dynamics generalization)

Schedule periodic exploration of these. ~30 min sonnet per drill; cheap.

---

## Saturation detection metrics

For each current front, track:
- N_drills_landed in front
- Marginal EIG per drill (estimate from drill P_deflated and findings)
- N_UNTESTED_compositions in scorecard for primitives in this front
- N_empirical_anchors per capability

When EIG drops < 0.3 AND UNTESTED_compositions > 3: trigger branch.

---

## Update protocol

- Per Monday: dispatch 1+ scheduled drill
- Per branch event: log in branching log; update scorecard with new axis findings
- Per saturation detection: surface to user; recommend branch
- Per quarter: review long-tail candidates; promote to scheduled axes

**Total NEW axes scheduled: 5 (A through E)**
**Long-tail candidates: 15 mathematical frameworks**
**Branching cadence: weekly + saturation-triggered + user-directed**
