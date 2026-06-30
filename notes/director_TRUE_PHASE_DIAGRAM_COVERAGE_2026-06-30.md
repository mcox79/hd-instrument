# TRUE phase diagram coverage — substrate operating space

**Last updated:** 2026-06-30 18:50 UTC
**Audience:** Director (post-compaction) + Skunkworks (audit reference) + USER (progress framing)
**Purpose:** Honest accounting of substrate operating space coverage. The "TRUE phase diagram" = component-axis substitution (outer) × parameter sweep within component (inner).

---

## Component-axis taxonomy (16 families)

Each axis family is a substrate-level choice the cell-author can vary. Most cells fix 13-15 axes and sweep 1-3. Cross-products are <5% explored.

| # | Axis | Primitives | Outer-axis CG cells | Inner-axis CG cells | Coverage |
|---|---|---|---|---|---|
| A | **Vector type (encoder)** | HRR-real / FHRR / BSC binary / sparse-binary / sparse-bipolar / GHRR / hex | ANCHOR 4 v3 (5 encoders × decay) pending VET | All chain-grade primitives default N_DIM=8192 | Outer ~70%; Inner ~50% (only 4 of 7 actually tested at FULL) |
| B | **N dimensionality** | 512 / 1024 / 2048 / 4096 / 8192 / 16384 / 32768 | None directly | All cells fixed N | Outer ~10%; Inner: dominantly N=8192 |
| C | **Sparsity** | 0.005 / 0.01 / 0.025 / 0.05 / 0.1 / 0.2 | None | Single value per cell | <5% |
| D | **Binding operation** | Hadamard / circular-conv / XOR / tensor-product / permutation / phase-add / block | Binding-op v1 PC MM (3-seed; 4 ops × N × corruption) | PC + capacity multi-bank use Hadamard | Outer ~30% (PC only); Inner extensive on default |
| E | **Bundle/superposition** | Sum / mean / majority / sparse-OR / centroid / per-exemplar Bayes / weighted | Schema family CG (4 schemas × 8 regimes) | Schema v4 capacity-stress CG | Outer ~60%; Inner CG |
| F | **Cleanup attractor** | Classical Hopfield / Modern Hopfield / iterative / soft / k-NN / WTA | PC cleanup family v1 MM (4 cleanups convergent) | PC v2.2 N-scaling law CG | Outer ~50% PC only; UNTESTED for WM, seqbind, capacity |
| G | **Routing / context-gating** | Random partition / learned-supervised / LSH / hierarchical / k-NN / softmax / partition-by-source / partition-oracle | WM routing family smoke HP, FULL VET pending | Multihop uses partition_oracle | Outer ~30%; Inner CG via partition-oracle |
| H | **Codebook structure** | Flat / banked / hierarchical bank / coarse-grain / per-context | Capacity multi-bank CG (B × K_per sweep); ANCHOR 3 coarse-grain CG; ANCHOR 1 partition-by-source CG | All CG at default | Outer ~60% (3 structures CG); Hierarchical UNTESTED |
| I | **Sequence encoding** | Positional shift / permutation / time-cells / gated-LSTM-like / context-modulated / hippocampal-replay | a43243de design pre-reg filed (DESIGN-ONLY; not authored) | Positional shift used everywhere | Outer ~0%; Inner CG at positional |
| J | **Order binding** | Cyclic shift / permutation / phase-rotation / learned-position | a43243de design pre-reg filed (DESIGN-ONLY; not authored); theta-gamma v1 HONEST_ABORT smoke | Cyclic shift used everywhere | Outer ~0%; Inner CG at cyclic |
| K | **Memory update rule** | Hebbian / SoftHebb / Willshaw / autoassociative / BCM-gain / STDP / replay-NREM | storage_update_rule_family v1 IN PROGRESS (4 rules × α × K seed_7 running 2026-06-30) | Hebbian default everywhere | Outer 0% → ~25% pending; Inner CG at Hebbian |
| L | **Eviction/forgetting** | Exponential / power-law / threshold / LRU / frequency-adaptive / CRISPR | ANCHOR 4 Pareto v2 CG (TD vs RD); ANCHOR 4 v3 pending VET (5 encoders × decay) | TD exponential default | Outer ~30%; Inner CG |
| M | **Refuse-gate adaptivity** | Fixed V_REL / Bayesian-CI / learned-logistic / percentile / cal-set-adaptive | Refuse-gate v1 MM (4 families × 4 regimes × 3 cal_sizes; 4/6 family pairs differ) | Fixed V_REL=256 CG | Outer ~50%; Inner CG |
| N | **Schema/abstraction** | Exemplar-Bayes / centroid HARDMAX / mixture HYBRID / prototype-distance / bagging / GRACEFUL | Schema family CG (4-way; HYBRID dominates EB in 10/12 regimes); Schema v4 capacity-stress CG (HARDMAX centroid noise-suppressing) | All CG | Outer ~70%; Inner CG |
| O | **Capacity allocation** | K_per × num_banks × α × N | Capacity multi-bank α-K CG (B={4,16,64} × K_per × α) | CG inner | Outer ~70% (single primitive family); Inner CG |
| P | **TWO_TIER generational** | STM-only / LTM-only / 2-tier / 3-tier / replay-driven | None directly; 2-tier CG | 2-tier CG | Outer ~25% (1 of 4); Inner CG |

---

## Component sweep coverage 2026-06-30 EOD

**CG outer-axis (family substitution) cells this session:**
- Schema family ✓ (axis N; 4 schemas × 8 regimes)
- Schema v4 capacity-stress ✓ (axis E centroid pooling; HARDMAX vs EB)
- ANCHOR 4 Pareto-AUC v2 ✓ (axis L; TD vs RD)
- Capacity multi-bank α-K v2 ✓ (axis O; B × K_per cliff)

**Outer-axis cells IN FLIGHT/PENDING VET:**
- ANCHOR 4 encoder v3 (axis A × L; 5 encoders × 12-pt grid) — VET in flight a4bfdc71 (potential 9th CG)
- Compartmentalized cortex K-banks v2 (axis H; 5 K values × N_c per bank) — dispatch in flight a3bafe51 (potential 9th CG)
- storage_update_rule_family (axis K; 4 update rules × 4 α) — seed_7 running on remote_cpu
- Refuse-gate v1 (axis M; 4 families × 4 regimes × 3 cal_sizes) — atomized MM
- Binding-op v1 PC (axis D; 4 ops × N × corruption) — atomized MM

**Outer-axis cells DESIGN-ONLY filed (need authoring):**
- Sequence encoding family (axis I) — a43243de design pre-reg
- Order binding family (axis J) — a43243de design pre-reg

**Outer-axis cells UNTESTED:**
- Cleanup family for WM (axis F at WM scale; PC version is convergent MB) — Cell B deferred by a2e6c3b4 (~800-1200 LoC; needs Research drill for primitive library spec)
- Cleanup family for sequence binding (axis F at seqbind scale)
- Sparsity sweep × encoder cross-product (axis A × C)
- N-dimensionality cross-product with anything (axis B)
- Routing geometry 2nd family at chain-grade scale (axis G; smoke HP via routing_geometry; full needs regime amend)
- TWO_TIER 3-tier variant (axis P)

---

## True coverage estimate

**Inner-axis (parameter sweep within fixed primitive):** ~70-80% on the 12 chain-grade primitives. Dense at default N=8192.

**Outer-axis (family substitution within axis family):** 6 of 16 CG (E, H, L, N, O — outer at least one family compared at chain-grade). +3 IN FLIGHT (A, D, K). +2 design-only (I, J). +5 untouched (B, C, F-WM, G-2nd-family, P).

**Cross-product (axis × axis × axis):** <5%. Nearly all cells fix 13 axes and sweep 1-3.

**Overall TRUE phase diagram coverage estimate:**
- Pre-2026-06-29: ~25%
- 2026-06-29 (end of overnight): ~35-40% (5 outer-axis CG promotions)
- 2026-06-30 ~18:50 UTC: ~40-45% (+ANCHOR 4 v3 pending VET / Cell C v2 pending dispatch / storage_update_rule running / 3 RIPE 2x-drills in flight)

**If all 4 in-flight CG candidates land (ANCHOR 4 v3 + Cell C v2 + storage_update_rule + Cell A v2 SWR multipass VET):** ~50% coverage. **CERT 634 → potentially 638** in this session.

---

## Highest-priority gaps for next program cycle

**Substrate-only (no cortex required):**
1. **Cleanup family × WM K-cliff** — needs cleanup primitive library spec FIRST (Research drill). 4 cleanups × K × num_banks. Cell B deferred by a2e6c3b4 for this reason.
2. **Sequence encoding family for sequence binding** — Stage 1 primitive only tested at positional shift; 4 alternatives untested. a43243de design pre-reg.
3. **Order binding family** — completely untouched at chain-grade (cyclic shift only). a43243de design pre-reg.
4. **Sparsity × encoder cross-product for PC** — META_RULE_AO claims regime-conditional; cross-product confirms.
5. **N-dimensionality sweep as a free axis** — currently always fixed.
6. **Routing geometry 2nd family at chain-grade** — random partition + partition-oracle CG; LSH / k-NN / hierarchical UNTESTED.

**Multi-structure-bio (defer to M3 cortex layer):**
- TOM Sally-Anne 2nd-order, TOM 3rd+, Hypothesis-gen pipeline composition, Self-explanation richness
- Long-narrative Q2 coref (closed; cortex required)
- Barrier 1 hint derivation (5 drills HF; cortex required)
- Hierarchical planning (substrate-native closed)
- 4-primitive brain-composition (substrate-native closed)
- CLS handoff at M=8192 (49% remainder; hippo v2 Ha+Hc rescue path in development)

---

## How to use this doc

- Director: reference for prioritizing next-batch dispatch + cell-author scope.
- Skunkworks: reference for "is this cell genuinely new vs same-axis recapitulation."
- USER: progress framing — coverage is moving but the operating space is genuinely large (~16 axis families × ~5-8 primitives each × continuous inner-axis parameters).

Update cadence: every major batch of CG promotions or session-end EOD.
