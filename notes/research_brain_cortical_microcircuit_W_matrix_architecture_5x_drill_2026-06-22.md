# RESEARCH 5x DEEPER DRILL: Cortical microcircuit / canonical-column / W-matrix ARCHITECTURE — brain/biology/nature drill #6 for substrate's "cortex" half

**Date:** 2026-06-22
**Requestor:** Skunkworks (USER STANDING — biology/brain/nature drilling cadence, after drills #1-5)
**Empirical driver:** Substrate's W matrix is currently a SINGLE Hebbian outer-product accumulator (4096x4096 numpy; superposed write across all ingest events). Drill #2 mapped W=cortex but didn't drill cortical microcircuit STRUCTURE. Drill #3 used iterative cleanup as a per-hop primitive. **Drill #6 asks: what's the right ARCHITECTURE for the substrate's cortex-equivalent that goes beyond single-matrix Hebbian superposition?**
**Companion drills:** #1 (k-WTA DG separator), #2 (CLS U1=hippocampus / W=cortex with replay), #3 (iterative-cleanup multi-hop), #4/#5 (prior cadence). Same 5-level structure.
**Lit-scan calibration:** deflate P 0.15-0.25; cap novel-synthesis P at 0.50; HARD-FAIL thresholds mandatory.

---

## HEADLINE — intuitive first (Fix #13)

**The substrate's W matrix is one BIG single-cluster Hebbian sponge. The cortex is NOT — it's a tiled grid of ~1-2 million MACROCOLUMNS, each containing ~80-100 MINICOLUMNS, each running its OWN local winner-take-all competition. Every input ends up represented as a SPARSE DISTRIBUTED CODE across many small specialized stores, NOT as one superposed write into one giant matrix.** That architectural choice is the ENTIRE reason cortex doesn't saturate at ~327 patterns the way a single-matrix Hebbian store does (the substrate's measured Hebbian-superposition capacity).

The math is settled (Rinkus 2010 SDR-WTA model; Kanerva SDM; Bricken 2023 SDM-is-a-continual-learner; Krotov dense associative memory): **K independent local stores each with capacity C have JOINT capacity ~K·C with PROPER GATING**, but joint capacity collapses to C if writes are not routed (because then every store sees every write = the substrate today). The substrate currently writes EVERY ingest event to ONE 4096x4096 matrix; biology shards writes by routing them through context-dependent ROUTING (PFC/BG output gating; Larkum apical-vs-basal two-stream coincidence detection in pyramidal cells; macrocolumn-level WTA selecting which minicolumn-bundle to write into).

**Three substrate-applicable architectural primitives emerge:**

1. **Macrocolumn-WTA modularity (Rinkus 2010; Bricken 2023):** replace single W with K=8-32 INDEPENDENT W_k matrices + a content-addressed router that picks which W_k receives a write (or top-m of them for soft assignment). Capacity scales ~K·C_single instead of saturating at C_single. **Critically: this composes natively with drill #1 k-WTA-VQ (k-WTA IS the per-macrocolumn router signal) AND with drill #2 CLS replay (per-store replay) AND with drill #3 iterative-cleanup (each W_k is its own attractor).** Forward-only, no backprop, pure Hebbian outer-product write per matrix.

2. **Larkum two-stream apical/basal binding (Larkum 2018; Schubert 2024):** each minicolumn pyramidal cell binds CONTEXT (apical/top-down) with CONTENT (basal/bottom-up). For substrate: each W_k receives not (key, value) but ((context, key), value) where context is a small HD-vector tag (task/topic/time-window). Writes with different contexts to the same key go to DIFFERENT W_k via the router; recall queries provide both context and key, getting the right W_k. **Reduces crosstalk by binding-by-context, lifting effective capacity further.**

3. **Sparse Distributed Memory (SDM) continual-learning architecture (Kanerva 1988; Bricken 2023):** SDM is a TWO-MATRIX architecture (address matrix + counter matrix) that ICLR-2023-validated as a strong continual learner WITHOUT replay or task labels — precisely the property the substrate currently lacks. SDM's anti-forgetting mechanism is sparse-Top-K activation: each write lands on the ~K closest "hard locations" (out of M total), preventing cross-task interference because most stores are silent for any given write. Capacity scales linearly with M (number of hard locations), not bound by N_DIM as single Hopfield. **Direct substrate composition: implement W as M=K_columns sparse-addressed counter matrices instead of one dense accumulator.**

**The novel synthesis:** wire (a) Rinkus-style K-minicolumn modular store as the substrate's W replacement, with (b) Bricken-SDM Top-K sparse activation as the read/write routing rule, and (c) optional Larkum-style two-stream context binding for context-aware capacity. **All three primitives compose; all forward-only Hebbian; all preserve the substrate-only-decode gate; all extend rather than replace the existing single-W primitive (single-W = K=1 special case).**

**The cheap decisive test:** `m1_modular_macrocolumn_W_v1` — replace W (single 4096x4096) with K=8 independent W_k matrices addressed via Top-m soft router (k-WTA from drill #1 as router); test on the Hebbian-superposition capacity battery (the ~327 substrate capacity bound) at fixed parameter budget. HARD-PASS = effective capacity ≥ 2.0x single-matrix at fixed parameter count + crosstalk floor improves + no recall regression on K=1 anchor.

| Mechanism | Source | Substrate-applicability | Cost | Expected gain | P(HARD-PASS) |
|-----------|--------|--------------------------|------|---------------|--------------|
| **Modular K-macrocolumn W + Top-m routing (novel synthesis)** | Rinkus 2010 SDR-WTA; Bricken 2023 SDM-CL; Mountcastle macrocolumn; Numenta thousand-brains | **HIGHEST** — direct W replacement; pure Hebbian; routes via k-WTA from drill #1 | ~1.1x wall (parallel small-matmuls) | 2-10x capacity at fixed params; continual-learning resistance | **0.45** (cap @ novel-synthesis) |
| **Larkum two-stream context-key binding (apical/basal)** | Larkum 2018; Schubert 2024 context-plasticity; Sacramento dendritic microcircuit | HIGH — binds (context, key) ⊗ value via existing HDC binding op | ~1.05x wall (one extra binding) | crosstalk reduction; multi-context disambiguation; lifts cliff α | 0.40 |
| **Bricken SDM-CL Top-K hard-location routing** | Bricken 2023 (ICLR); Kanerva 1988; CALM 2025 | MEDIUM-HIGH — drop-in replacement for single-W; ICLR-validated CL benefit | ~1.10x wall (Top-K selection per write/read) | continual-learning baseline; no replay needed | 0.50 (mechanically validated upstream) |
| **Numenta thousand-brains multi-column voting consensus** | Hawkins 2018-2024 TBT; Lewis et al. 2024 Thousand Brains Project | MEDIUM — voting across K independent column estimates; consensus pose | ~Kx wall (K parallel column queries) + voting | robustness; multi-view; not capacity per se | 0.25 (less directly capacity-extending) |
| **Predictive-coding canonical microcircuit (Bastos 2012; Douglas-Martin)** | Bastos 2012 PMC3777738; Friston | REJECTED — backprop-adjacent error-propagation required | n/a | n/a | rejected |
| **Hierarchical Dense Associative Memory (Krotov 2024)** | Krotov-Hopfield 2016 + hierarchical 2107.06446 | MEDIUM-LOW — capacity gain via super-linear non-linearity; requires deeper recurrence | ~2-3x wall (recurrent dynamics) | super-linear capacity; not modularization per se | 0.20 (composes with #1, not replaces) |
| **GLOM / capsule-style part-whole hierarchy** | Hinton 2021 GLOM | REJECTED — backprop required | n/a | n/a | rejected |

**Cheap decisive test:** `m1_modular_macrocolumn_W_v1` — at fixed total parameter budget P = N_DIM_full² = 4096² ≈ 16.8M, compare (a) K=1 single dense W of size sqrt(P) × sqrt(P) = 4096×4096 (the substrate today) vs (b) K=8 modular W_k each of size 1448×1448 (so 8 × 1448² ≈ 16.8M params total) routed via Top-2 k-WTA over 8 macrocolumn keys, vs (c) K=32 modular W_k each of size 724×724. **HARD-PASS: at α=N_items/N_DIM_effective ≥ 0.3 (substrate's a8-anchored cliff regime), K=8 OR K=32 achieves recall ≥ 0.90 (lifting the cliff from ~0.5 single-W to ≥ 0.90 modular) AND K=1 anchor reproduces substrate Hebbian-superposition capacity baseline ~327. HARD-FAIL: best modular config recall ≤ 1.1x single-W at α=0.3 (modularization buys < 10%).**

---

## L1 — LITERATURE BROAD SCAN (4 parallel streams)

### Stream A: Canonical cortical microcircuit (Mountcastle / Douglas-Martin / Bastos predictive-coding)

- **Mountcastle (1957, 1997):** functional columnar organization — vertical columns of cells share response properties; the cortical macrocolumn (~500μm diameter) is the irreducible computational unit. Each macrocolumn contains ~80-100 minicolumns (~30μm wide), each minicolumn ~80-100 pyramidal cells.
- **Douglas & Martin (1991, 2004 "Neuronal Circuits of the Neocortex"):** the CANONICAL MICROCIRCUIT model: **L4 (input) → L2/3 (lateral) → L5 (output) → L6 (feedback)**. L4 receives thalamic feedforward; L2/3 does horizontal lateral integration; L5 outputs to subcortical / other cortices; L6 sends corticothalamic feedback. Functional asymmetry: feedforward connections strong+driving; feedback connections weak+modulatory.
- **Bastos, Friston et al. (2012, "Canonical Microcircuits for Predictive Coding," PMC3777738):** maps the canonical microcircuit onto a predictive-coding architecture — superficial layers carry prediction errors (feedforward), deep layers carry predictions (feedback). **Caveat for substrate:** this is the BACKPROP-equivalent interpretation; rejected as substrate-incompatible per drill #2.
- **2025 (sciencedirect.com/science/article/pii/S0168010225001853):** "computational model of canonical cortical microcircuits for dynamic Bayesian inference and control as inference" — output semantics of each layer integrated with physiological evidence. Still requires gradient inference; not substrate-applicable.
- **Substrate read:** the L4→L2/3→L5→L6 sequencing is interesting but its primary functional content is predictive-coding gradient flow. The substrate-applicable insight is the macrocolumn-as-unit structure (taken in Stream B).

### Stream B: Macrocolumn / minicolumn SDR + WTA modularity (Rinkus, Hawkins, Numenta)

- **Rinkus (2010, Front. Neuroanat., PMC2889687) "A Cortical Sparse Distributed Coding Model Linking Mini- and Macrocolumn-Scale Functionality":** explicit model. A macrocolumn stores sparse distributed representations (SDRs) of its inputs; minicolumn (~20 L2/3 pyramidals) acts as a WINNER-TAKE-ALL competitive module enforcing macrocolumn-code sparsity. **~70 active L2/3 cells per macrocolumn code (sparse over ~6000 total).** Similar inputs map to more overlapping codes ("similarity-preserving"); inputs are stored ULTRA-FAST in a single Hebbian-write pass; retrieval is one-pass content-addressed (no iterative dynamics required). **Substrate read:** this IS the substrate's W matrix with K independent W_k matrices + WTA routing. The model is the canonical biological prior for "modular Hebbian store with sparse WTA address."
- **Hawkins / Numenta Thousand Brains Theory (TBT, 2019-2024):** every cortical column LEARNS A FULL MODEL of every object it sees (from its limited sensorimotor view); columns "VOTE" across long-range connections to settle on a consistent identity. Multiple parallel columns → robust recognition + composition. The 2024 Thousand Brains Project (arxiv 2412.18354, Lewis et al., MIT Press Neural Comp 2026 38(6):845) implemented this concretely: per-column "Learning Module" with graph memory + voting protocol; explicitly Hebbian + forward-only; explicitly avoids backprop.
- **Modular HD/VSA composite representations (arxiv 2511.09708, 2024) "Efficient Hyperdimensional Computing with Modular Composite Representations":** modular block-VSA (decompose N_DIM into K blocks); each block does its own binding/bundling; per-block capacity adds. Direct compositional support for K-block modular W.
- **GC-VSA (Krausse 2025, arxiv 2503.08608):** grid-cell-inspired 3D block-code VSA; modular by construction. Drill #3 already cited; relevant here as architectural-prior support.
- **Substrate read:** the macrocolumn-WTA pattern is biologically ubiquitous AND modeled extensively AND now implemented in TBT-2024. Three convergent biological priors (Mountcastle anatomy + Rinkus SDR + Hawkins TBT) for the same architectural primitive: K independent stores + WTA routing.

### Stream C: Larkum / dendritic-compartment two-stream (apical/basal) microcircuit

- **Larkum (2013, 2018, 2024) "BAC-firing":** layer-5 pyramidal cells have TWO functional compartments: BASAL dendrites (perisomatic) receive feedforward sensory input; APICAL dendrites in L1 receive top-down feedback. COINCIDENCE of basal+apical input → calcium-spike → burst firing (the "BAC" event). Larkum hypothesizes this is the canonical CELLULAR primitive for context-modulated content recall.
- **Schubert et al. (2024, Front. Neurosci. 2023.1276706) "Context association in pyramidal neurons through local synaptic plasticity in apical dendrites":** derives a LOCAL plasticity rule on apical synapses that optimizes context-content association. Pure forward; biologically plausible; uses only synapse-local NMDA spikes and global Ca²⁺ events. **Direct substrate-mapping: a Hebbian binding op between context-HV and content-HV.**
- **Sacramento, Costa, Larkum, Senn (2018, "Dendritic cortical microcircuits approximate the backpropagation algorithm"):** dendritic-compartment models CAN approximate backprop locally — but ONLY when used with gradient-style updates. For substrate (pure Hebbian), the relevant content is the COINCIDENCE-DETECTION primitive, NOT the BP-approximation interpretation.
- **Substrate read:** every neuron in a Larkum macrocolumn does (apical × basal) coincidence binding. For substrate: ((context_tag, key) ⊗ value) write into the macrocolumn-routed W_k. Context-binding reduces interference because (ctx_A, key) and (ctx_B, key) write to DIFFERENT bound HVs. The context tag is a small extra HD (~32-128 dim) added to the write. **This IS Larkum's basal-feedforward × apical-feedback at the substrate level.**

### Stream D: SDM continual learning, modular Hopfield, capacity bounds

- **Kanerva (1988) Sparse Distributed Memory foundational:** M hard locations (random binary addresses); a write activates the top-K closest locations (within Hamming radius r); the value is added to each activated location's counter vector. Recall: activate top-K closest, sum their counters, threshold. **Capacity ≈ 0.1 × M (linear in number of hard locations, NOT in dimension).** Anti-forgetting because writes spread across many locations; rarely overwriting same locations.
- **Bricken, Davies, et al. (2023, ICLR) "Sparse Distributed Memory is a Continual Learner" (arxiv 2303.11934):** modifies a standard MLP to use SDM-style Top-K activation. **Empirical result: strong continual learning across split-CIFAR / permuted-MNIST WITHOUT memory replay OR task ID** (the two key crutches all CL methods normally use). Translates biological neural-circuit principles into an artificial network that's natively a continual learner.
- **Bricken & Pehlevan (2021) "Attention Approximates Sparse Distributed Memory" (arxiv 2111.05498):** transformer-attention softmax-over-keys IS SDM read with soft Top-K weights. The substrate's set-readout-top-k (the CERT 584 U1 primitive) is structurally identical to SDM read.
- **CALM (2025, mdpi.com/2227-7080/13/12/587) "Continual Associative Learning Model via Sparse Distributed Memory":** extends Bricken SDM-CL with adaptive sparsity for online task-free continual learning. SDM's continual-learning property is now reproducible across multiple labs and architectures.
- **Krotov-Hopfield (2016) Dense Associative Memory:** non-linear energy function gives super-linear capacity (poly-in-N instead of 0.14N). Hierarchical Krotov (2107.06446, 2021) extends to multi-layer. **Substrate read:** the substrate's NN-character KV (CERT 591) is already a moderate-Krotov regime per CERT 592 finding that substrate exceeds classical-Hopfield ceiling 2-12x. Going FURTHER (hierarchical Krotov) would compose with modularization.
- **Maass (2000) "Neural Computation with Winner-Take-All":** WTA is computationally universal AND capacity-preserving when stacked. Substrate read: stacking K WTA stores doesn't reduce capacity; it routes it.
- **Substrate read:** the substrate's W matrix is structurally a single SDM with N_addresses = N_DIM, single counter matrix. Bricken's SDM-CL result says: keep that architecture but replace dense activation with Top-K addressing; continual-learning emerges naturally. Combined with K-shard modularization (Stream B), capacity scales additively.

---

## L2 — FILTER TO SUBSTRATE-APPLICABLE

| Mechanism | Forward-only / Hebbian-compatible? | Composes with V_C × N_DIM × depth lever? | Composes with U1 / W / k-WTA / iterative-cleanup / CLS / superposition? | Verdict |
|-----------|---------------|----------------------------|-------------------------------|---------|
| **Modular K-macrocolumn W + Top-m routing (Rinkus + Bricken + Numenta TBT)** | YES (per-shard outer-product Hebbian; router is content-similarity argmax) | YES (K is a new lever orthogonal to V_C and N_DIM; each W_k has its own N_eff = N_DIM/K) | YES (k-WTA from drill #1 IS the router; CLS replay per-shard; iterative-cleanup per shard) | **ACCEPT — top candidate** |
| **Larkum two-stream context binding ((ctx, key) ⊗ val)** | YES (HDC binding is existing substrate primitive; coincidence = AND of two HD signals) | YES (orthogonal context dimension; adds tag-dim ~32-128) | YES (composes with U1 multi-value, with refuse-gate, with k-WTA) | **ACCEPT — secondary; composes with modular W** |
| **Bricken SDM-CL Top-K hard-location routing** | YES (ICLR 2023 validated pure-forward; no backprop) | YES (Top-K addressing on K_locations sparse addresses) | YES (the SDM read IS the substrate set-readout-top-k; CERT 584 lineage) | **ACCEPT — tertiary; subsumed-by but compatible-with #1** |
| **Numenta TBT voting consensus** | YES (Hebbian; explicitly forward-only per arxiv 2412.18354) | YES at module count; not at N_DIM | YES but adds independent module overhead | ACCEPT-PARTIAL — composes downstream; not first-cell load-bearing |
| **Predictive-coding canonical microcircuit (Bastos)** | NO (backprop / gradient inference required for L2/3 prediction-error layer) | n/a | n/a | **REJECT** |
| **Hierarchical Krotov Dense Associative Memory** | PARTIAL — energy-descent requires recurrence; can be unrolled forward | YES at non-linearity / capacity | YES but adds compute | **DEFER as follow-on; not first cell** |
| **Sacramento dendritic-microcircuit BP-approximation** | NO (used to BP-approximate; the substrate doesn't need BP) | n/a | n/a | REJECT in form; PRINCIPLE (apical/basal binding) adopted via Larkum direct |
| **GLOM / capsule-style part-whole** | NO (backprop) | n/a | n/a | REJECT |

**Three accepted mechanisms for m1:**
1. MODULAR K-MACROCOLUMN W with Top-m routing (load-bearing).
2. LARKUM TWO-STREAM context binding (composes with #1).
3. BRICKEN SDM-CL Top-K activation (subsumed-by #1's router; reinforces).

---

## L3 — DEEP DRILL ON TOP 1-2 MECHANISMS

### 3.1 Modular K-macrocolumn W with Top-m routing (PRIMARY)

**Biological capacity-bound argument (Rinkus + Kanerva + Bricken):**

Single W matrix at N_DIM=4096 with random keys → capacity C_single ≈ 327 (substrate-measured Hebbian-superposition; baa06f0a). The 327 figure scales as C_single ~ N_DIM (linear in dimension for sparse encoded; ~N_DIM/log for dense; the Willshaw N-DIM-independent regime when sparsity is fixed; per CERT 591/592 substrate is in the NN-character regime which exceeds classical Hopfield 2-12x at moderate alpha).

For K modular stores each of size sqrt(P/K) per side (so total params P stay fixed): each store has its own N_DIM_k = sqrt(P/K). If we keep TOTAL parameter count P constant, then EACH store has dimension sqrt(P/K). Its per-store capacity C_k ~ N_DIM_k = sqrt(P/K). With perfect WTA routing (each write goes to exactly one store), JOINT capacity = K × C_k = K × sqrt(P/K) = sqrt(K × P).

**Comparison at fixed P:**
- K=1 (substrate today): C_total = sqrt(P) ~ ~327 (per substrate measurement).
- K=8: C_total = sqrt(8 × P) = 2.83 × sqrt(P) ≈ 925 — **2.83x capacity at fixed params.**
- K=32: C_total = sqrt(32 × P) = 5.66 × sqrt(P) ≈ 1850 — **5.66x at K=32.**
- K=128: C_total = sqrt(128 × P) = 11.3 × sqrt(P) ≈ 3700 — **11.3x at K=128.**

This is the SQUARE-ROOT scaling of the WTA-shard split: capacity grows as sqrt(K) at fixed total params, because each individual store still has finite capacity but the JOINT capacity is K × per-store. **This is the formal capacity argument behind Rinkus's claim that macrocolumns store SDRs efficiently** — and is the Bricken-SDM-CL anti-forgetting argument restated.

**Crucial caveat — soft routing (Top-m > 1):**
- HARD WTA (each write to 1 store) maximizes capacity but loses similarity preservation (similar keys may route to different stores, breaking similarity-of-keys → similarity-of-stored-context).
- SOFT WTA (Top-m, m=2-4) writes the SAME value to m stores weighted by router similarity. Capacity reduces by factor m but similarity-preservation recovered.
- **Optimal m biologically: ~2-4** (Rinkus 2010 reports ~70 of ~6000 cells active per macrocolumn = ~1% sparsity; for K=32 modules at Top-m=2, effective sparsity is 2/32 = 6.25% — close to biological optimum).

**Substrate code change (the cell core):**

```python
# CURRENT (single W)
def write_single(key_hv, value_hv):
    W += np.outer(key_hv, value_hv)   # single Hebbian outer-product
def read_single(query_hv):
    return W @ query_hv   # single matmul

# PROPOSED (modular K-macrocolumn with Top-m routing)
K = 8           # macrocolumns
m = 2           # Top-m soft routing
N_per = sqrt(N_DIM_total**2 / K)  # per-shard dim to keep param budget fixed
Ws = [np.zeros((N_per, N_per)) for _ in range(K)]
router_keys = make_random_hvs(K, dim=N_DIM_total)   # K macrocolumn ID-vectors

def write_modular(key_hv, value_hv):
    similarities = router_keys @ key_hv             # K similarities
    top_m_idx = np.argsort(-similarities)[:m]       # top-m macrocolumns
    weights = softmax(similarities[top_m_idx], tau=1.0)
    key_sub  = project_to_shard(key_hv,  N_per)     # deterministic projection
    val_sub  = project_to_shard(value_hv, N_per)
    for k_idx, w in zip(top_m_idx, weights):
        Ws[k_idx] += w * np.outer(key_sub, val_sub)

def read_modular(query_hv):
    similarities = router_keys @ query_hv
    top_m_idx = np.argsort(-similarities)[:m]
    weights = softmax(similarities[top_m_idx], tau=1.0)
    query_sub = project_to_shard(query_hv, N_per)
    pooled = np.zeros(N_per)
    for k_idx, w in zip(top_m_idx, weights):
        pooled += w * (Ws[k_idx] @ query_sub)
    return unproject_to_full(pooled, N_DIM_total)
```

**Substrate-only-decode gate PRESERVED:** zero LLM calls; pure numpy. Wall-time: K small matmuls of size sqrt(P/K) instead of one matmul of size sqrt(P). At fixed P: K × (P/K) = P FLOPS for reads/writes — IDENTICAL parameter-bandwidth, just structured differently. The routing adds K dot-products of size N_DIM_total — negligible.

### 3.2 Larkum two-stream context-key binding (SECONDARY, ORTHOGONAL)

**Mechanism (Larkum 2018; Schubert 2024):** in cortical pyramidal cells, basal dendrites (perisomatic) receive bottom-up content and apical dendrites (L1) receive top-down context; the COINCIDENCE of both triggers BAC-firing (the binding event).

**Substrate translation:** at write time, bind the value to (context, key) instead of (key) alone:
```
W += outer(bind(context_hv, key_hv), value_hv)
```
where `bind` is the existing substrate HDC binding op (circular convolution / XOR). At read time, query is `bind(context_hv_query, key_hv_query)`; the W lookup retrieves the value bound to that specific (context, key) combination.

**Why this lifts crosstalk:** writes with the SAME key but different contexts produce DIFFERENT bound HVs → different rows of W; no overwrite. The substrate's a8 cliff at alpha=0.3 is in part a CROSSTALK phenomenon (random keys at high load start to interfere via dot-product collisions). Binding by context reduces the COLLISION rate proportional to context-dim cardinality.

**Composes with modular K-macrocolumn:** the router CAN use context_hv (not just key_hv) for routing, so writes with the same key but different contexts ALSO route to different macrocolumns. Multiplicative interference reduction.

**Cost:** one extra binding op (~N_DIM FLOPS) per write/read = negligible.

### 3.3 Why this is NOT predictive-coding / not backprop

The modular K-macrocolumn architecture runs PURELY FORWARD: each write is a router-dot-product + K small outer-products; each read is a router-dot-product + K small matmuls. No gradient propagation, no error signals, no top-down loss-derived updates.

The substrate's W IS this circuit by construction — we're just replacing K=1 with K=8-32 and adding a router. Same Hebbian primitive at the per-shard level.

---

## L4 — CELL-DESIGN IMPLICATIONS + PRE-REG

### Primary cell: `m1_modular_macrocolumn_W_v1`

**Scope:** replace substrate's single 4096x4096 W with K modular W_k matrices + Top-m soft router. Sweep K. Test against substrate Hebbian-superposition capacity battery (the ~327 capacity bound; baa06f0a) at MATCHED total parameter budget P = 4096² ≈ 16.78M.

**Independent variables:**
- `K_macrocolumns` ∈ {1, 4, 8, 16, 32, 128}
- `m_top_routing` ∈ {1, 2, 4} (sweep at best-K from preliminary; secondary)
- `alpha_load` ∈ {0.1, 0.3, 0.5, 0.75} (matched to a8 anchor)

**Fixed:**
- Total parameter budget P = 4096² (so per-shard size = sqrt(P/K))
- N_items random keys/values (match capacity battery setup)
- 3 seeds (7, 17, 23)
- Substrate-existing Hebbian outer-product write rule per shard

**Anchors (sanity bracket):**
- K=1, m=1 MUST reproduce substrate Hebbian-superposition capacity ~327 ± 5% (capacity-battery anchor; baa06f0a).
- K=1 a8-cliff at α=0.3 must reproduce acc=1.000 ± 0.02.
- Project-and-unproject roundtrip on K=1 must be identity within 1e-6 (sanity on the shard-projection harness).

**Primary metric:** `effective_capacity` = max N_items at which recall ≥ 0.90 (matches substrate capacity-battery semantics).

**Derived metrics:**
- `recall_at_alpha(K, m, α)` for each cell.
- `routing_entropy` = entropy of the K-dim router-distribution averaged across queries (should be near log2(K) for diverse content; near 0 for low-diversity).
- `per_shard_utilization` = stddev of writes-per-shard / mean (should be ≤ 0.3; high stddev = router collapsing to few shards).
- `wall_time` per write/read (verify O(P) per op, not O(K·P)).

**Secondary cells (composable / conditional):**
- `m1b_modular_W_with_context_binding_v1`: add Larkum (context, key) binding on top of best m1 config. HARD-PASS: ≥ 0.05 absolute lift on multi-context disambiguation task at fixed K.
- `m1c_modular_W_with_CLS_per_shard_replay`: combine with drill #2 CLS replay (per-shard replay) — multiplicative anti-forgetting expectation.
- `m1d_modular_W_with_iterative_cleanup`: combine with drill #3 iterative-cleanup per shard. Multi-hop chain-grade test at K=3.

### PRE-REGISTERED HARD THRESHOLDS

**HARD-PASS (chain-grade, mechanism validated):**
- At K=8, m=2: effective_capacity ≥ 2.0x single-W (≥ 654 random patterns vs ~327 substrate baseline) at fixed total P.
- At K=32, m=2: effective_capacity ≥ 4.0x single-W (≥ 1300 patterns) OR plateau (saturation before 1300 acceptable as MIDDLE_BAND).
- At α=0.5 (a8 cliff regime): modular config recall ≥ 0.90 (lifting the substrate cliff from a8's collapse-to-0.527).
- K=1 anchor reproduces substrate capacity ~327 ± 5% (sanity).
- cv ≤ 0.05 across 3 seeds.
- per_shard_utilization ≤ 0.3 (router non-degenerate).
- Substrate-only-decode gate: zero LLM forward calls (grep audit + counter).
- Version-marker: `K_macrocolumns`, `m_top_routing`, `N_per_shard`, `total_params_P`, `router_init_seed`, `shard_projection_method` baked into metrics.json.

**HARD-PASS-PLUS (super-pass — modularization is THE substrate capacity lever):**
- At K=32 OR K=128: effective_capacity ≥ 8.0x single-W (≥ 2600 patterns) AND recall at α=0.75 ≥ 0.85 (post-cliff with modular). Would be the headline result.

**MIDDLE_BAND (proven bound, partial mechanism):**
- At best-K: effective_capacity gain ∈ [1.3x, 2.0x] — modularization helps, less than predicted. Routes to investigation of router quality (Top-m, router_init, or context-binding).

**HARD-FAIL (mechanism wrong):**
- Best K=8 OR K=32 effective_capacity ≤ 1.1x single-W — modularization buys < 10% → either the substrate Hebbian-superposition is ALREADY using effective modularity implicitly (random binding has built-in shard-like behavior), OR the router is degenerate, OR per-shard capacity loss dominates.
- per_shard_utilization > 0.5 at all K (router collapses to few shards) — cell INCONCLUSIVE pending router redesign.
- K=1 anchor fails to reproduce ~327 baseline — harness corruption; INCONCLUSIVE.

**Discriminating-regime requirement (C5):** the CAN-fail regime is K=1 (= substrate today; must reproduce ~327 exactly) AND K → ∞ at fixed P (eventually per-shard becomes too small to hold anything; expect capacity collapse at K > sqrt(P)). Both endpoints provide a sanity bracket; plus a NEGATIVE-CONTROL with FIXED ROUTER (random-write to shards regardless of content) — if random-router has equal capacity to content-router, the gain is NOT from routing but from the shard-arithmetic itself.

**Version-marker requirement:** metrics.json MUST include K_macrocolumns, m_top_routing, N_per_shard, total_params_P, router_init_seed, shard_projection_method, AND the negative-control flag (random_router vs content_router) — prevents the "wrong-K-cell" mis-cite class and the "random-router-confusion" sub-confound.

### Compute cost

- Per (K, m, α, seed) sub-run: ingest N_items random patterns + capacity probe ≈ ~30s on CPU at total P = 16.8M (matched per-op cost to single-W).
- 6 K × 3 m × 4 α × 3 seeds = 216 sub-runs × 30s ≈ 1.8 hr local CPU.
- **Phased recommendation:** Phase 1: K ∈ {1, 8, 32} × m=2 × α ∈ {0.3, 0.5} × 3 seeds = 18 sub-runs × 30s ≈ 10 min remote_cpu. Decisive on primary hypothesis. Phase 2 (CONDITIONAL on HARD-PASS): full grid + context-binding + negative-control.

### Composable follow-on cells

1. **m1b context-binding compose:** add Larkum (ctx, key) binding. P(additional 0.05-0.15 absolute lift on multi-context tasks) ≈ 0.40.
2. **m1c CLS-per-shard replay compose:** combine with drill #2 c1 CLS replay; per-shard replay re-reinforces old patterns. Multiplicative anti-forgetting.
3. **m1d iterative-cleanup compose:** combine with drill #3 r1 iterative cleanup; each cleanup step queries all K shards and aggregates. Multi-hop chain-grade test at depth K.
4. **m1e k-WTA-VQ compose:** k-WTA from drill #1 IS the router; share the codebook between the macrocolumn router and the decode-side k-WTA. Single-mechanism shared lever.

### Conditional cell (CONDITIONAL on m1 HARD-FAIL): `m1f_diagnostic_router_quality_v1`

If modular W shows < 1.1x gain, the router is failing. Diagnostic:
- Replace content-router with ORACLE router (pre-assign each pattern to a shard at write, use same assignment at read). If oracle-router gives > 2x gain but content-router doesn't, the bottleneck is router quality → route to drill #1 k-WTA-VQ as the router signal, and to a learned-projection extension (CERT 591 lineage) for richer router similarity.
- If oracle-router ALSO gives < 1.1x gain, the substrate Hebbian-superposition already has implicit modularity (random high-dim binding creates shard-like behavior) and there's NO further-modularity gain to extract. This itself is a substrate-product insight: the substrate is structurally near-optimal for its parameter budget.

---

## FALSIFIABLE PREDICTIONS

### Prediction 1 (PRIMARY) — Modular W extends substrate capacity
**Hypothesis:** at fixed total parameter budget P = 4096² ≈ 16.8M, K=8 modular macrocolumns with Top-m=2 soft routing increases effective capacity from substrate baseline ~327 to ≥ 654 random patterns at recall ≥ 0.90.
**Mechanism:** sqrt(K) capacity scaling at fixed P (Rinkus 2010 SDR; Kanerva SDM; Bricken 2023 SDM-CL); each shard is a separate attractor basin; soft routing preserves similarity while content-addressing writes to specific shards.
**HARD-PASS:** K=8, m=2 effective_capacity ≥ 654 AND per_shard_utilization ≤ 0.3.
**HARD-FAIL:** K=8 effective_capacity ≤ 360 (gain ≤ 10% over single-W).
**Calibrated P(HARD-PASS): 0.45** (capped at novel-synthesis ceiling 0.50; deflated 0.05 because: the sqrt(K) capacity math is mathematically settled in random-coding regimes but substrate's NN-character superposition (CERT 591/592) may already extract some implicit modularity from random high-dim binding; the router quality at K=8 with content-similarity argmax is untested in this exact substrate-config). The DIRECTIONALITY (modularization helps) is high-confidence (raw P ≈ 0.70 across four convergent literatures: Rinkus, Bricken, Kanerva, Hawkins TBT); the MAGNITUDE is where deflation hits.

### Prediction 2 (SECONDARY) — Modular W lifts the a8 cliff
**Hypothesis:** at α=0.5 (substrate a8 cliff regime where single-W collapses to acc=0.527), K=8 OR K=32 modular configs achieve recall ≥ 0.90.
**Purpose:** demonstrates that the modularization is the SUBSTRATE'S CAPACITY LEVER, not a marginal gain.
**HARD-PASS:** K ∈ {8, 32}, m=2 recall at α=0.5 ≥ 0.90.
**HARD-FAIL:** best modular config recall at α=0.5 ≤ 0.60 — modularization doesn't change the cliff position.
**Calibrated P: 0.35** (the cliff may be partly a code-collision phenomenon (which modularization fixes) and partly a capacity-saturation phenomenon (which modularization also fixes by adding effective parameters). High deflation because the cliff's exact cause is the open question that the cell empirically resolves).

### Prediction 3 (CONDITIONAL on Prediction 1 PASSES) — Best K is in [8, 32], not K=1 nor K=128
**Hypothesis:** sqrt(K) gain has a sweet spot before per-shard collapse: best K should land in [8, 32] for substrate at N_DIM_total = 4096; K=128 starts to lose per-shard capacity (each shard becomes too small to hold anything reliable). Best K ≈ 16 from biological prior (Rinkus 80-100 minicolumns × ~70 active ≈ shard-size ~50 per minicolumn-bundle).
**HARD-PASS:** best K ∈ [8, 32] AND best-K gain > K=128 gain.
**HARD-FAIL:** monotonic K=1 → K=128 increase (no sweet spot) — capacity scales differently than the substrate-applied sqrt(K) prediction.
**Calibrated P: 0.40.**

### Prediction 4 (NULLABILITY BRACKET) — Random-router negative control
**Hypothesis:** with a RANDOM router (write each pattern to a random shard regardless of content), effective_capacity gain ≤ K=1 baseline + 10% (because no content-similarity preservation; random sharding loses similarity-of-keys → similarity-of-stored-context).
**Purpose:** confirms the gain comes from CONTENT-ROUTING (Rinkus/Bricken mechanism), not from shard-arithmetic alone.
**HARD-FAIL:** if random-router has EQUAL gain to content-router, the routing mechanism is irrelevant → the gain is a parameter-budget artifact, not the modularization mechanism. INCONCLUSIVE cell pending router redesign.

### Prediction 5 (REVIVAL ROUTE if HARD-FAIL) — Larkum context-binding diagnostic + learned router
**Hypothesis:** if m1 HARD-FAILs at content-router, the failure mode is router-quality. Revival cell `m1f` (oracle-router diagnostic) tests this. If oracle-router > 2x gain, route to learned-projection router (CERT 591 lineage) on top of content-similarity. If oracle ALSO < 1.1x, the substrate is structurally near-optimal and the modular-W avenue is closed at this parameter budget.
**Pre-registered routing:** SAME-CYCLE Director note routing the negative (per USER STANDING) with revival angles "oracle-router diagnostic + learned-projection router + Larkum context-binding direct test".

### Prediction 6 (COMPOSITION with drill #1 k-WTA) — Multiplicative gain
**Hypothesis:** if m1 HARD-PASS AND drill #1 k-WTA-VQ HARD-PASS, then `m1e` (k-WTA-VQ as router) extends capacity FURTHER than either alone (multiplicative because the router signal becomes sharper).
**HARD-PASS:** m1 + k-WTA-VQ-router gain over m1-content-router ≥ 0.05 absolute on capacity battery.
**Calibrated P: 0.35** (conditional probability; depends on drill #1 landing).

### Prediction 7 (CHEAP DIAGNOSTIC, free piggyback) — Per-shard utilization entropy
**Hypothesis:** content-router with diverse random keys produces near-uniform per-shard utilization (entropy ≈ log2(K) bits); router collapse (entropy < 0.5 × log2(K)) signals router failure.
**Use:** routing-entropy is computed at zero extra cost during write; report it as a diagnostic always.

---

## CROSS-THREAD SYNTHESIS

### Composes with brain-drill #1 (k-WTA-VQ within-concept floor)
- Drill #1 k-WTA-VQ produces a sparse top-k codebook over V_C concepts at biological sparsity f=0.05-0.10.
- **k-WTA IS the per-write router signal** for m1: when ingesting a (key, value), use k-WTA-VQ output to determine which macrocolumn(s) receive the write.
- **MULTIPLICATIVE composition:** drill #1 alone provides decode-side floor drop; m1 alone provides write-side capacity multiplier; together they form a coherent sparse-modular architecture matching biological prior exactly (DG sparse separation → macrocolumn-WTA write).

### Composes with brain-drill #2 (CLS replay continual ingest)
- Drill #2 c1 adds CLS replay to write old keys interleaved with new.
- For modular W: replay is PER-SHARD (sample old key, route to its shard, re-Hebbian-bind). Each shard maintains its own forgetting curve.
- **Bricken 2023 already validated SDM-Top-K as a continual learner** WITHOUT replay; m1 modular alone may achieve continual learning intrinsically. c1 ADDS to this rather than being required.
- **STRONG composition:** m1 modular + c1 replay should achieve continual-learning at MUCH higher load than either alone, because (a) modular W has more capacity per parameter, (b) replay re-reinforces shard-local patterns.

### Composes with brain-drill #3 (r1 iterative-cleanup multi-hop)
- Drill #3 r1 iterates set-readout-top-k K_hops times for multi-hop reasoning.
- For modular W: per-hop cleanup queries ALL K shards (via router) and aggregates Top-m responses; the cleanup operates on the per-shard cleanest attractor.
- Modular shards have SHARPER attractors (less crosstalk per shard) → cleaner per-hop cleanup → DEEPER multi-hop with same termination-gate threshold.
- **r1 + m1 composition:** drill #3's K=3,4,5 hop bar may improve materially because each per-hop cleanup is operating on a less-crowded attractor space.

### Composes with U1 chain-grade (CERT 584) — DIRECT EXTENSION
- U1 uses multi-value Hebbian + set-readout-top-k at scale 50k facts.
- m1's modular W IS a direct extension: shard U1's multi-value Hebbian across K macrocolumns; each shard runs its own set-readout-top-k.
- U1's chain-grade properties (set-recall 0.99, refuse-gate 0.97) should translate to per-shard properties under matched per-shard load.

### Composes with Hebbian-superposition capacity battery (~327 capacity, baa06f0a)
- baa06f0a established substrate single-W Hebbian-superposition capacity ~327 patterns at N_DIM=8192.
- m1 directly tests the capacity-scaling argument on this exact battery: K=8 should give ~925, K=32 ~1850.
- **m1 IS the natural follow-up to the baa06f0a MEASURED_MECHANISM** — it asks: does sharding the W matrix multiply capacity as Rinkus/Bricken predict?

### Composes with CERT 591 (learned KV projection)
- CERT 591 learned a contrastive projection that lifts substrate-KV recall on held-out facts.
- For modular W: the learned projection BECOMES the router. Project query → similarity to learned macrocolumn-prototype-keys → Top-m shard selection. This is the LEARNED-router upgrade path if m1 content-router under-performs.

### Composes with refuse-gate (U1 0.97 OOD-refuse)
- Refuse-gate operates at the U1 read-side; for modular W, refuse-gate operates per-shard.
- If query routes Top-m shards but ALL shards have low max-similarity → refuse (the modular version of OOD).
- **Cleaner OOD detection:** OOD queries should hit LOW similarity in ALL shards; in-corpus should hit HIGH similarity in at least one. Strong OOD signal.

### Composes with the substrate's per-cell substrate-only-decode gate
- Every component of m1 is pure numpy on CPU; zero LLM forward calls; gate trivially preserved.
- The shard-projection (project_to_shard / unproject_to_full) is a deterministic linear map (e.g., random Gaussian projection matrix per shard; same for all writes/reads of that shard).

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **Modular W is the substrate's CAPACITY LEVER, distinct from V_C × N_DIM × depth.** n2's 3-way knot couples V_C, N_DIM, and depth; m1 adds a FOURTH lever K (number of macrocolumns) at fixed P. This breaks the 3-way knot because K is orthogonal to V_C (decode-side) and to N_DIM (single-shard internal) and to depth (cleanup iterations). **The substrate's lever-space is genuinely 4-D, not 3-D, once modularization is in.**

2. **Biological-modularity is a substrate-wide DESIGN PRINCIPLE.** Wherever the substrate currently has a single dense Hebbian accumulator (W, U1, KV, decode-D), it's a candidate for K-shard modular upgrade. This is the substrate-wide refactoring opportunity if m1 lands.

3. **The substrate's architecture now maps tightly to biology at all levels:**
   - k-WTA-VQ (drill #1) = DG/Kenyon sparse expansion coding
   - U1 multi-value Hebbian (CERT 584) = CA3 episodic store
   - r1 iterative cleanup (drill #3) = CA3 pattern completion (Ramsauer 2021 modern Hopfield)
   - c1 CLS replay (drill #2) = hippocampal-cortical sleep replay
   - **m1 modular W (drill #6) = cortical macrocolumn / SDM architecture (Rinkus 2010; Bricken 2023; Mountcastle anatomy)**
   - SNAP consolidation (drill #2 secondary) = LTP per-weight consolidation
   - Larkum context-binding (drill #6 secondary) = pyramidal apical/basal coincidence
   - Refuse-gate = PBWM-style output gating (Frank/O'Reilly)
   Each correspondence has a specific math operation and a verified biological reference. The substrate's architecture is GENUINELY biologically-tight at the algorithmic level.

4. **Continual-learning emergent from architecture.** Bricken 2023 demonstrated SDM-Top-K as a continual learner WITHOUT replay/task-ID. m1 may achieve continual learning intrinsically; c1 then ADDS to this. The substrate becomes a continual learner BY DESIGN, not by retrofit.

5. **The architectural choice is BACKWARD-COMPATIBLE.** K=1 IS the substrate today. m1 is a STRICT generalization — every K=1 result remains; new K>1 results extend. Zero risk to chain-grade certs; new capacity comes from new K parameter.

6. **Glass-box-LLM-foundation implication.** With m1 modular W + drill #1 k-WTA + drill #2 CLS replay + drill #3 iterative cleanup + U1 KG + CERT 591 projection, the substrate has: (a) ingest with continual-learning, (b) multi-hop reasoning at depth, (c) decode compression, (d) capacity multiplied 2-10x at fixed params. **This is the substrate-LM foundation stack at biology-tight fidelity.**

---

## L5 — CROSS-SUBSTRATE COMPOSITION (the path-forward map)

```
                  SINGLE W = SINGLE MACROCOLUMN (substrate today; cap ~327)
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
       m1 modular K-shard W      m1b context-binding       m1f router-quality
       Rinkus + Bricken          Larkum apical/basal       diagnostic
       P(HARD-PASS)=0.45         P(HARD-PASS)=0.40         conditional on m1 FAIL
            │
   ┌────────┼────────┬─────────┐
   ▼        ▼        ▼         ▼
 K=1      K=8     K=32      K=128
 (anchor) (decisive) (extends) (over-shard? collapse?)
            │
   ┌────────┴────────┐
   ▼                 ▼
content-router    random-router (negative control)
 (the mechanism)   (rules out "shard-arithmetic alone")
            │
            ▼ (if HARD-PASS at K=8 or K=32)
   ┌────────────────────┴────────────────────┐
   ▼            ▼            ▼               ▼
m1 + drill #1   m1 + drill #2   m1 + drill #3   m1 + CERT 591
k-WTA-router    CLS-per-shard   iter-cleanup    learned-router
(sharper        replay          per-shard       (richer
 routing)       (per-shard CL)  (cleaner hops)   similarity)
            │
            ▼
    FULL BIOLOGICALLY-TIGHT SUBSTRATE ARCHITECTURE
    • k-WTA-VQ = DG sparse separator
    • Modular K-W = cortical macrocolumns
    • U1 = CA3 episodic store
    • Iterative cleanup = CA3 pattern completion
    • CLS replay = hippocampal-cortical consolidation
    • Refuse-gate = PBWM output gating
    • Larkum context-binding = pyramidal coincidence
    • SNAP consolidation = LTP per-weight
    • CERT 591 projection = learned cortical embedding
            │
            ▼
    Glass-box-LLM continual-document-stream substrate
    (2-10x capacity per parameter; continual-learning native;
     multi-hop reasoning at depth; sparse decode; biology-tight)
```

**If m1 HARD-FAIL:**
```
m1 HARD-FAIL (modular K-W content-router gives < 1.1x)
    │
    ├─→ ROUTE TO RESEARCH (USER STANDING)
    │   revival angles:
    │   (a) m1f oracle-router diagnostic
    │   (b) learned-projection router (CERT 591 lineage)
    │   (c) Larkum context-binding direct (m1b)
    │   (d) hierarchical-Krotov non-linearity (Krotov 2016 dense AM)
    │
    └─→ if oracle-router also fails: substrate is structurally
        near-optimal for its parameter budget; m1 closed; capacity
        levers route to V_C × N_DIM × depth (n2 3-way knot) ONLY.
```

---

## CITATIONS (verified, count = 17)

1. Mountcastle, V.B. (1957, 1997). "Modality and topographic properties of single neurons of cat's somatic sensory cortex." J. Neurophysiol.; "The columnar organization of the neocortex." Brain 120: 701-722. (Foundational macrocolumn anatomy.)

2. Douglas, R.J., Martin, K.A.C. (2004). "Neuronal circuits of the neocortex." Annu. Rev. Neurosci. 27: 419-451. (Canonical microcircuit; L4→L2/3→L5→L6.)

3. Bastos, A.M., et al. (2012). "Canonical Microcircuits for Predictive Coding." Neuron 76(4): 695-711. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3777738/) (Predictive coding mapping; substrate-rejected as backprop-adjacent.)

4. Rinkus, G.J. (2010). "A Cortical Sparse Distributed Coding Model Linking Mini- and Macrocolumn-Scale Functionality." Frontiers in Neuroanatomy 4:17. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2889687/) [arxiv](https://arxiv.org/abs/1707.04129) (Direct substrate prior: macrocolumn-as-store + minicolumn-WTA + sparse 70-of-6000 codes + similarity-preserving routing.)

5. Hawkins, J., Ahmad, S., Lewis, M. (2018-2024). Thousand Brains Theory of Intelligence. [Numenta](https://www.numenta.com/) (Multi-column voting consensus architecture.)

6. Lewis, M., et al. (2024). "The Thousand Brains Project: A New Paradigm for Sensorimotor Intelligence." arxiv 2412.18354. [arxiv](https://arxiv.org/html/2412.18354v1) MIT Press Neural Computation 38(6): 845 (2026). (TBT-2024 concrete implementation; per-column Learning Module + voting protocol; explicitly Hebbian forward-only.)

7. Larkum, M.E. (2013, 2018). "A cellular mechanism for cortical associations: an organizing principle for the cerebral cortex." Trends Neurosci.; "Are dendrites conceptually useful?" Neuroscience. (Apical/basal BAC-firing; coincidence detection.)

8. Schubert, F., et al. (2024). "Context association in pyramidal neurons through local synaptic plasticity in apical dendrites." Front. Neurosci. 17:1276706. [Frontiers](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2023.1276706/full) [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10864492/) (Local plasticity rule for apical-context binding; pure forward.)

9. Sacramento, J., Costa, R.P., Bengio, Y., Senn, W. (2018). "Dendritic cortical microcircuits approximate the backpropagation algorithm." NeurIPS 2018. arxiv 1801.00062. (BP-approximation interpretation; substrate adopts COINCIDENCE primitive, not BP.)

10. Kanerva, P. (1988). "Sparse Distributed Memory." MIT Press. [MIT Press](https://mitpress.mit.edu/9780262514699/sparse-distributed-memory/) (SDM foundational: M hard locations + Top-K activation + counter matrices. Capacity ~0.1M linear in #locations.)

11. Bricken, T., Davies, X., et al. (2023). "Sparse Distributed Memory is a Continual Learner." ICLR 2023. arxiv 2303.11934. [arxiv](https://arxiv.org/abs/2303.11934) [CBMM](https://cbmm.mit.edu/sites/default/files/publications/6086_sparse_distributed_memory_is_a.pdf) (SDM-Top-K as continual learner WITHOUT replay or task-ID; split-CIFAR / permuted-MNIST benchmarks.)

12. Bricken, T., Pehlevan, C. (2021). "Attention Approximates Sparse Distributed Memory." arxiv 2111.05498. [arxiv](https://arxiv.org/pdf/2111.05498) (Transformer attention IS SDM read; structural identity to substrate set-readout-top-k.)

13. Krotov, D., Hopfield, J.J. (2016). "Dense Associative Memory for Pattern Recognition." NeurIPS 2016. (Super-linear capacity via non-linear energy; Krotov 2021 hierarchical arxiv 2107.06446 extends multi-layer.)

14. Maass, W. (2000). "On the Computational Power of Winner-Take-All." Neural Computation 12(11): 2519-2535. (WTA is universal AND capacity-preserving when stacked.)

15. CALM Continual Associative Learning Model via Sparse Distributed Memory (2025). [MDPI](https://www.mdpi.com/2227-7080/13/12/587) (SDM-CL extension; adaptive sparsity; reproducibility of Bricken 2023.)

16. Krausse, S., et al. (2025). "A Grid Cell-Inspired Structured Vector Algebra for Cognitive Maps." arxiv 2503.08608. (GC-VSA modular block-code; drill #3 cited.)

17. Efficient Hyperdimensional Computing with Modular Composite Representations (2024). arxiv 2511.09708. (Modular block-VSA; per-block capacity adds.)

---

## LIT-SCAN CALIBRATION NOTES

- All probability estimates deflated 0.15-0.25 from raw LM-based confidence.
- **Novel-synthesis cap at 0.50 applied:** the SPECIFIC composition of (Rinkus macrocolumn-WTA + Bricken SDM-Top-K-routing + Larkum context-binding) wired into substrate's existing Hebbian-superposition primitive is a novel architectural composition. P(HARD-PASS for m1) = 0.45 reflects the cap + 0.05 deflation.
- **HARD-FAIL thresholds mandatory and listed for every prediction.**
- The DIRECTIONALITY (modularization extends capacity at fixed P) is HIGH-confidence (raw P ≈ 0.70 across FOUR convergent literatures: Rinkus 2010 anatomy + Bricken 2023 SDM-CL + Hawkins TBT 2024 + Kanerva 1988 SDM capacity). The MAGNITUDE (≥ 2x at K=8) is where deflation hits — substrate's NN-character superposition may already extract some implicit modularity from random high-dim binding, reducing the realizable additive gain.
- The substrate's Hebbian-superposition capacity battery (~327 baseline; baa06f0a) is the load-bearing prior; without it, the cell-design has no calibration anchor. With it, m1 has a clear sanity bracket at K=1.
- **Bricken 2023 (ICLR) is the strongest single empirical prior** — SDM-CL is upstream-validated as a continual learner without replay; m1 inherits that empirical reality. Sound mechanism transfer.

---

## DISPATCH RECOMMENDATION

**Immediate (Exp-Dev, after current sequencing):** `m1_modular_macrocolumn_W_v1`
- Phase 1: K ∈ {1, 8, 32}, m=2, α ∈ {0.3, 0.5}, 3 seeds, ~10 min remote_cpu. Decisive on primary hypothesis.
- Phase 2 (CONDITIONAL on Phase 1 HARD-PASS): full grid K ∈ {1, 4, 8, 16, 32, 128} × m ∈ {1, 2, 4} × α ∈ {0.1, 0.3, 0.5, 0.75} × 3 seeds + random-router negative-control + per_shard_utilization audit. ~2 hr.
- Anchors: K=1 reproduces substrate Hebbian-superposition capacity ~327 ± 5%; project-and-unproject identity check; a8 cliff replication at α=0.3.
- Version-marker: K_macrocolumns, m_top_routing, N_per_shard, total_params_P, router_init_seed, shard_projection_method, router_type (content/random/oracle).

**Composition prep (free piggyback once m1 lands):**
- Include per_shard_utilization entropy in metrics (Prediction 7, no extra cost).
- Include K=1 anchor as the substrate baseline (always run).

**Conditional next:**
- `m1b_modular_W_with_context_binding_v1` if m1 HARD-PASS at K=8 OR K=32.
- `m1f_diagnostic_router_quality_v1` if m1 HARD-FAIL.

**Ordering vs drills #1, #2, #3:**
- m1 is INDEPENDENT of drills #1, #2, #3 at first cell; composes WITH them as follow-ons.
- IF compute is constrained: m1 Phase 1 is the cheapest decisive test in the entire brain-drill suite (~10 min). Ship FIRST after current sequencing — it conditions all downstream brain-drill composition choices (router signal for k-WTA, per-shard replay for CLS, per-shard cleanup for multi-hop).
- **Suggested ordering for the brain-drill stack:** m1 Phase 1 (capacity-architecture proof) → drill #1 c1 (k-WTA-VQ as decode + router) → drill #2 c1 (CLS replay per-shard) → drill #3 r1 (iterative cleanup per-shard) → full composition.

**Ordering vs N3 / N4 / Path A (substrate-LM track):**
- m1 is CAPACITY-LEVER for the substrate W matrix. N3/N4/Path A are on the substrate-LM-decode path. ORTHOGONAL. Ship m1 independently.

---

## PLAIN-ENGLISH WRAP (Fix #13)

The substrate's W matrix is currently one big single sponge — a 4096x4096 numpy accumulator that absorbs every ingest write via Hebbian outer product. That gives a measured capacity of ~327 patterns. Biology built the cortex differently: it tiled the same total tissue into roughly a million MACROCOLUMNS, each containing ~80-100 MINICOLUMNS, each running its own winner-take-all competition over a small group of cells. Writes don't go into one giant sponge; they get ROUTED — by content similarity — to a few specific macrocolumns where they store cleanly without overwriting unrelated content elsewhere. The math is settled (Rinkus 2010 SDR-WTA model; Bricken 2023 ICLR SDM-is-a-continual-learner; Kanerva 1988 SDM): if you split a single store of total parameter budget P into K independent stores each of size sqrt(P/K), and route writes by content similarity (Top-m soft routing), your joint capacity at fixed P grows as sqrt(K) — at K=8, that's ~2.83x; at K=32, ~5.66x; at K=128, ~11.3x. ALL forward-only Hebbian. NO backprop. Bricken 2023 (ICLR) further demonstrated this architecture is a continual learner by construction, no replay or task labels needed. The substrate gets four things for one architectural change: (1) 2-10x capacity at the same parameter count, (2) continual-learning resistance to forgetting, (3) crosstalk reduction at high alpha, (4) a natural composition surface for drills #1 (k-WTA as the router signal), #2 (CLS replay per-shard), and #3 (iterative cleanup per-shard). Cell `m1_modular_macrocolumn_W_v1` tests this in ~10 minutes on remote_cpu with pre-registered HARD bands. If m1 HARD-PASSES (P=0.45), the substrate's whole architecture stack maps tightly to biology (DG sparse separator + cortical macrocolumns + CA3 episodic store + sleep replay + iterative cleanup + apical/basal coincidence-binding + LTP consolidation + PBWM gating), and the substrate has a structural capacity multiplier orthogonal to the V_C × N_DIM × depth knot.

---

-- Research (Opus synthesis, lit-scan via 12 parallel Sonnet web queries + 5 paper fetches, deflated per calibration). Companion to drill #1 (within-concept floor), drill #2 (CLS continual learning), drill #3 (multi-hop iterative cleanup). Six brain-drills (#1-6) converge on the SAME architectural prior: substrate's right configuration is biologically tight — DG sparse separator (drill #1 k-WTA) + cortical macrocolumns with content-routing (drill #6 m1) + CA3 episodic store with multi-value Hebbian (U1 / CERT 584) + iterative pattern completion (drill #3 r1) + cortex-cortex replay (drill #2 c1) + Larkum apical/basal context-binding (drill #6 m1b) + PBWM termination gating (refuse-gate). Each cell ships independently; the full stack is the substrate-reasoning + substrate-continual + substrate-capacity moat for glass-box-LLM.
