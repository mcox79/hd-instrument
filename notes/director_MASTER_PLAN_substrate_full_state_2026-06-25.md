# DIRECTOR MASTER PLAN — substrate full state at end of 2026-06-25

**Purpose:** record full understanding of the substrate-product plan + current state + open questions so context survives compaction. USER explicit ask: "make sure that our current understanding of the plan is fully baked, planned, and recorded."

**Date:** 2026-06-25 late-night (cell wave in flight)
**Cert state:** CERT 600 (yesterday 588; +12 today)
**Atoms:** 177,364 across math/meta/audit partitions
**Total spawn cycles today:** 15+ agents; 30+ cells dispatched

---

## SUBSTRATE-PRODUCT STORY (current best framing)

**"Auditable 2-hop declarative knowledge device with a working memory primitive, multi-axis refuse-gates, calibrated uncertainty, and a KG retrieval pipeline scaling to 10M facts. End-to-end audit-device pipeline operates at p95 < 0.2ms with zero LLM forward calls. Brain-aligned where the brain has the right answer; honest negative where it doesn't. Currently missing the cortical/consolidation half of the brain architecture; substrate has hippocampus + PFC equivalents but not cortex or sleep-replay yet."**

---

## CHAIN-GRADE PORTFOLIO (production-ready)

### Tier 1 — Base primitives
| Capability | Anchor / cell | Verdict | Envelope |
|---|---|---|---|
| Sparse-bipolar codebook | (foundational, cited everywhere) | CHAIN_GRADE | f ∈ [0.02, 0.05]; alpha_c(f) measured |
| Cleanup σ₀ ≥ 0.95 | (foundational; META rule) | CHAIN_GRADE | N ≥ 4096 for V ≤ 1000; N=8192 for V ≤ 4000 |
| HRR 2-hop binding | (foundational; many cells) | CHAIN_GRADE | depth ≤ 2 across N=8192 |
| Continual learning | a8_continual_writes + continual_kv_n32768_120_sessions | CHAIN_GRADE | 120 sessions retention=1.000 (drill upgraded from 200 cycles framing) |
| Working memory (multi-bank routing) | substrate_working_memory_multi_bank_routing_v1 (TODAY) | chain-grade-eligible | K=1024 via 32 banks × 32 items each |
| HRR permutation-indexed binding | substrate_permutation_binding_multiocc_v2_full | CHAIN_GRADE | multi-occurrence subset rescues FHRR same-role collision |

### Tier 2 — Architecture
| Capability | Anchor / cell | Verdict | Envelope |
|---|---|---|---|
| Stage 2 FREQ_ROUTED_DEEPER | substrate_compose_freq_routing_v5_DEFINITIVE | **CHAIN_GRADE_DEFINITIVE** | N ∈ [4096, 8192]; +0.148 BPC over baseline |
| MULTIPLICATIVE composition lever | multiplicative_composition_lever_v1 | MM (Skunkworks demoted; substrate's REAL claim is "fixed f=0.01 is provably-within-0.019-of-oracle EVERYWHERE") | high-fabrication loads |
| Multi-bank routing for KG | substrate_partition_routing_10M_full_v2 | **CHAIN_GRADE @ M=1M** | single-level; partition_size=2000 |
| Hierarchical 2-level partition routing | substrate_partition_routing_hierarchical_2level_v1 | **CHAIN_GRADE @ M=10M** | 2LEVEL=0.978 |

### Tier 3 — Applications
| Capability | Anchor / cell | Verdict | Envelope |
|---|---|---|---|
| Intent classifier | a1_substrate_intent_classifier_v1 | CHAIN_GRADE | acc=0.754 at 50 intents; p95=0.54ms |
| Templated response | a2_substrate_templated_response_v1 | CHAIN_GRADE | ≤100 templates |
| Audit-relation refuse-gate | substrate_refuse_gate_near_domain_v2 | CHAIN_GRADE | V_REL ≤ ~50 at N=8192 |
| Graph-health refuse | refuse_gate_5_graph_health_cpu_v1 | CHAIN_GRADE | reads substrate state |
| CSP uncertainty quantification | csp_first_ship_v1 | CHAIN_GRADE | 8.42× speedup |
| Dense projected KV at scale | dense_projected_KV_envelope_v1 | CHAIN_GRADE | M ≤ 10k recall ≥ 0.80; cliff at M=50k for (d=768, σ=0.1) |
| Sparse projected KV variant B | flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 | CHAIN_GRADE | f=0.02; whiten-before-topk |
| **Stage 3 integrated audit-device pipeline** | substrate_stage3_integrated_audit_device_demo_v2_production_scale_GPU (TODAY) | **CHAIN_GRADE_PRODUCTION_SCALE** | V_C_IN ≤ 2000, V_REL ≤ 50, M_KV ≤ 10k; p95 < 0.2ms; all 4 categories at 1.000 |
| NESS graph traversal | kmax_ness_envelope_corrected_v1 | CHAIN_GRADE | alpha ∈ [0.3, 0.7]; per-hop correct-next-node |
| KV learned projection | kv_learned_projection_v1 | CHAIN_GRADE | recall ≥ 0.70 held-out |

### Tier 4 — Architectural principles (META rules in cert)
- **Principle O** (basis-vs-use-case labels) — CHAIN_GRADE_DEFINITIVE
- **Mu-Viswanath anisotropy bound** — empirically confirmed via Wave D capacity-tight regime
- **META_PROSPECTIVE_BANDS_FRESH_SEEDS** — bands locked at module init + previously unseen seeds eliminates retrofit confound
- **META_CROSS_N_REPLICATION_AS_DEFINITIVE_UPGRADE_CRITERION** — second-N reproduces rules out N-specific fluke
- **META_M2_tight_rail_from_different_config** — referent-match rail discipline
- **META_M5_chain_construction_must_match** — chain-construction match
- **META_M6_NAIVE_baseline_must_be_derived_not_copied** — derivation provenance
- **META_M7_smoke_must_match_full_along_capacity_sensitive_dimensions** — TODAY's atomization; 3-cell evidence for smoke-vs-full sign-flip
- **META_BARRIER_1_QUADRUPLE_NEGATIVE** — 4 substrate-native multi-hop closure attempts REFUTED at random-bipolar isotropic regime
- **Per-arm metrics (Fix #28)** — read verdict per-arm; default UNDER-claim; let Skunkworks tier UP

---

## REFUTED / CLOSED (we tried; doesn't work at production rigor)

| Capability | Why refuted | Implication |
|---|---|---|
| Multi-hop QA beyond 2 hops (consolidation) | Compound atoms pollute library; cleanup wrong shortcuts | Per-hop cleanup is the ceiling |
| Multi-hop QA (pointer-chain) | Geometric error compounding | 70% per step → noise by hop 5 |
| Multi-hop QA (WM-scaffold) | WM holds clean intermediates but doesn't UPGRADE bad retrievals | Need primitive change |
| Multi-hop QA (CSP-gated) | Threshold too aggressive; 41% abort rate | Need diff approach |
| Multi-hop QA (parallel-vote v1) | Regime artifact (smoke W bindings 8× smaller than full); identical cleanup primitive to other 4 | META_M7 caught it |
| Wave D biology-native encoder | Capacity-dependent phase: helps at V=200 (rich), HURTS at V=10000 (tight); Mu-Viswanath confirmed | No encoder upgrade needed; random-bipolar correct at production |
| Frequency-multiplexed WM on shared W | FDM intermod (4-cell evidence: Cell 2 v4 + Cell 6 v3 + Cell 2 v6 + Cell Y) | Multi-bank decomposition is the answer |
| SEGREGATED dual-W brain analog | Brain analog doesn't transport (Cell 2 v6 MIDDLE_BAND honest negative) | Stage 2 stays at 2 chain-grade mechanisms |
| Foldiak axis-flip biology | Axis-flip bug; deferred since Wave D negative anyway | No need |
| Heterogeneous-routing composition | Failed at v1; SEGREGATED also failed | Need different mechanism |
| Whitening rescue of anisotropy | Recovery only +0.020; rotation doesn't add rank | Whitening is wrong fix |

---

## THE FOUR LOAD-BEARING GAPS (in priority order)

### GAP 1: Multi-hop QA beyond 2 hops

**Barrier:** per-hop cleanup at production scale gives ~70% accuracy. 5 hops × 70% = 17% noise. All 5 attempts (consolidation, pointer-chain, WM-scaffold, CSP-gated, parallel-vote) use IDENTICAL per-hop cleanup primitive — bit-identical per-step accuracy sequences [0.69, 0.485, 0.31, 0.205, 0.145].

**5x revival drill recommended 3 angles:**
1. Compose today's wins (fly-LSH + multi-bank + partition routing per hop) — P=0.45
2. PFC chunked 2-hop decomposition — P=0.45 STRONGEST brain prior
3. Bidirectional meet-in-middle — P=0.40

**3-cell revival batch dispatched (per drill recommendation):** RUNNING on local CPU. Cell A (PFC chunked) seed 7 partial showed only +0.055 lift; tracking HARD_FAIL.

**Additional cells dispatched per USER insight:**
- Beam-search multi-hop with WM-held candidate set + CSP pruning (different from all 6 prior attempts; maintains top-K candidates per hop, not top-1)
- USER quote: "with our PFC we should be able to do the brain analog easily no? We're not going to live with the ceiling"

### GAP 2: Anisotropy on real-data Pythia keys

**Barrier:** real items live in a narrow cone of code space; dense memory designed for spread items collapses to 1.8% recall.

**Bypass paths (work; don't solve):**
- Partition routing (Cell 1 + Cell E today; chain-grade to M=10M)
- KV learned projection (chain-grade held-out)

**Solve attempts:**
- Whitening: HARD_FAIL (+0.020 recovery)
- Fly-LSH sparse expansion: MM tier (Skunkworks demoted from chain-grade-candidate)
- v3 M=100k adversarial discriminator OOM'd today (partial showed AB_CONTROL=0.240 may beat LSH 0.189; un-verified)
- v2 batched (in flight; will give verified discrimination)

**USER insight on expansion ratio:** "if you have a cone - why can't you project the origin into the 'middle' of that cone and blow out all the parts to a bigger space?" — exactly the cerebellar mechanism. We tested at 8× expansion; brain cerebellum uses 7,000,000×. Cell Z (fly-LSH expansion ratio sweep 8x → 4096x) dispatched.

### GAP 3: Compositional generalization (combine facts to make NEW facts)

**Barrier:** capability suite scored 0.00 on heldout compositions (vs 0.05 chance). Substrate stores facts perfectly but doesn't COMBINE them into novel facts.

**Brain layer analog accounting:**
- Hippocampus (substrate W) ✓
- PFC (multi-bank WM) ✓ today
- **Cortex (slow semantic schema layer) MISSING** — substrate has no automatic feature-extraction across atoms; no compression of "1000 dog-episodes" into "mammals are warm-blooded"

**Cell C dispatched (TODAY):** substrate_cortical_schema_extraction_compositional_generalization_v1 — periodic batch scans atoms.jsonl + extracts schemas from shared capability/feature clusters + tests on heldout compositional queries.

### GAP 4: Long-term continual operation (5000+ cycles with repair)

**Barrier:** chain-grade at 200 cycles with forget=0.006. At production cadence (years of continual ingest), might compound or might stay linear. No repair mechanism if it does compound.

**Brain layer/process analog accounting:**
- Hippocampus (substrate W) ✓
- Cortex MISSING (same as Gap 3)
- NREM sharp-wave ripple replay MISSING — no offline pass that re-writes random subsets of old atoms
- REM synaptic homeostasis MISSING — no global downscaling primitive
- DMN consolidation MISSING

**Cells A + B dispatched (TODAY):**
- Cell A: substrate_continual_NREM_replay_v1 (periodic random-subset rewrites; brain NREM ripple analog)
- Cell B: substrate_synaptic_homeostasis_global_downscale_v1 (global W downscaling; Tononi REM-homeostasis analog)

---

## WHAT'S IN FLIGHT (10 cells + 2 exp_dev spawns active)

| Cell | Status | Tests |
|---|---|---|
| Cell X v2 META_M6 (multi-hop revival #5) | local CPU running | parallel-vote at matched regime |
| Cell A PFC chunked 2-hop (multi-hop revival #6) | local CPU running | PFC analog — decompose into 2-hop sub-queries |
| Cell B compose fly-LSH + multi-bank + partition (multi-hop revival #7) | local CPU queued | composition of 3 chain-grade wins |
| Cell C bidirectional meet-in-middle (multi-hop revival #8) | local CPU queued | forward + backward halves depth |
| Cell X beam-search multi-hop (NEW; USER insight) | local CPU queued | top-K candidates + CSP pruning |
| Cell Z fly-LSH expansion sweep (NEW; USER insight) | GPU queued | 8x → 4096x expansion ratios |
| Anisotropy v2 batched (M=100k discriminator) | GPU queued (4.5h) | fly-LSH vs Charikar vs AB_CONTROL |
| KV learned projection at scale | GPU running | M=100k with partition routing |
| Refuse-gate V_REL extension | local CPU queued | V_REL = {16, 32, 64, 128, 256, 512} |
| NESS alpha-high extension | local CPU queued | alpha = {0.8, 0.85, 0.9, 0.95} |
| Multi-bank WM K-extension adversarial | local CPU queued | K = {1024, 2048, 4096} + adversarial feature-overlap |
| META v4 self-discovered corpus | local CPU queued | 28 substrate-own equivalence groups |
| Cell A NREM replay (NEW; Gap 4) | (being authored) | brain sharp-wave ripple analog |
| Cell B synaptic homeostasis (NEW; Gap 4) | (being authored) | brain REM downscale analog |
| Cell C cortical schema extraction (NEW; Gap 3+4) | (being authored) | brain cortical schema analog |
| Cell B intent classifier | local CPU running | scaling 100 → 1000 intents |

---

## DECISION FRAMEWORK FOR LANDINGS

### Multi-hop revival (Gap 1)
- IF any of 8 attempts chain-grades → Barrier 1 has a real path; 2-hop ceiling lifts
- IF all 8 HARD_FAIL → 2-hop ceiling is substrate-product permanent at random-bipolar isotropic regime; external orchestration is the honest answer

### Anisotropy (Gap 2)
- IF v2 batched shows fly-LSH ≥ AB_CONTROL by ≥ 0.10 at M=100k → fly-LSH IS the mechanism; chain-grade-confirmed
- IF AB_CONTROL ≥ fly-LSH → fly-LSH was over-claim; partition routing + KV learned projection are the substrate-product anisotropy answers (not actual solve)
- IF expansion ratio sweep shows monotonic lift up to 4096x → cerebellar mechanism real but needs more dimensionality than we tested

### Schema extraction (Gap 3)
- IF Cell C schema arms score ≥ 0.50 on heldout compositions → cortex equivalent works; compositional generalization closes
- IF HARD_FAIL → substrate's atom-level structure isn't extractable into compositional schemas; deeper rework needed

### NREM replay + homeostasis (Gap 4)
- IF Cell A replay arm maintains forget ≤ 0.05 at 5000 cycles + baseline cliffs → sleep-replay analog works; continual extends indefinitely
- IF Cell B homeostasis prevents saturation → REM downscaling analog works
- Together: substrate gains brain-equivalent continual memory architecture

---

## SUBSTRATE BRAIN-LAYER MAP (current state)

| Brain region | Substrate analog | Status |
|---|---|---|
| Hippocampus (episodic storage) | W matrix + sparse-bipolar + CRISPR append-only | ✅ CHAIN-GRADE |
| Hippocampus (DG pattern separation) | sparse-bipolar f=0.02 + WTA cleanup | ✅ CHAIN-GRADE (implicit) |
| Cerebellum (sparse fan-in expansion) | fly-LSH arm | ⏳ MM; testing at brain-scale expansion ratios |
| PFC (working memory) | Multi-bank WM routing | ✅ CHAIN-GRADE (today) |
| Cortex (slow semantic) | **MISSING** — schema-extraction layer being built now | 🔨 IN FLIGHT (Cell C) |
| Cortex (CSP uncertainty) | csp_first_ship | ✅ CHAIN-GRADE |
| NREM sharp-wave ripple replay | **MISSING** — periodic random-subset rewrite being built | 🔨 IN FLIGHT (Cell A) |
| REM synaptic homeostasis | **MISSING** — global W downscaling being built | 🔨 IN FLIGHT (Cell B) |
| DMN consolidation | **MISSING** | ⏳ NOT YET |
| Basal ganglia (reward weighting) | NOT IN SCOPE | — |
| Thalamus (relay) | NOT IN SCOPE | — |

---

## KEY DISCIPLINE OBSERVATIONS

### Director Fix #28 violations today: 18+
Pattern: I see striking single-arm numbers and frame as findings; Skunkworks reads per-arm + verify-off-data and demotes. Today's catches:
- Anisotropy v2 chain-grade-candidate → MM (corpus too easy at M=10k)
- Cell D WM cleanup MIDDLE_BAND → HARD_FAIL (K-ceiling claim refuted)
- Cell X v1 "Cell X cleanup better" → regime artifact (identical primitive; smoke W 8× smaller)
- Capability re-audit Q-discipline (3 inflated chain-grade claims demoted by Skunkworks)
- "Anisotropy SOLVED" framing → premature; corpus saturation; LSH attribution un-verified
- META v3 1.000 perfect → likely by-construction (v4 self-discovered tests real claim)

**Operational discipline now codified:** META_M7 (smoke must match full along EVERY capacity-sensitive dimension) atomized today as 4th rail-discipline rule. Cert architecture catching every over-claim.

### Skunkworks rulings pending (next batch)
- META v3 (likely MM by-construction)
- Cell Y' multi-bank routing (likely chain-grade pending Q-discipline)
- Cell Y v1 corrected mechanism (HARD_FAIL_INTERMOD)
- Cell X v2 META_M6 (mode B determined)
- All cells from beam-search + expansion-sweep + 4-cell envelope batch + 3-cell brain-consolidation batch when they land

---

## SUBSTRATE-PRODUCT MASTER PLAN

### Where we are (end of 2026-06-25)
- Audit-device CHAIN_GRADE at production V (V_C_IN=2000, V_REL=50, M_KV=10k, p95 < 0.2ms)
- KG retrieval CHAIN_GRADE at M=10M via hierarchical routing
- WM CHAIN_GRADE at K=1024 via multi-bank routing
- All architectural decompositions today succeeded (KG, WM, fly-LSH)
- Multi-hop QA STILL OPEN (8 attempts in flight when all land)
- Anisotropy MECHANISM unclear (fly-LSH may be over-claim; expansion sweep tests if cerebellar-scale helps)
- Brain-consolidation primitives BEING BUILT (NREM + REM + cortex)

### Substrate-product positioning at this point
**Shippable today as:** "Auditable 2-hop declarative knowledge device with calibrated uncertainty, 3 chain-grade refuse mechanisms, working memory (1024 slots; ~140× brain's 7±2), KG retrieval to 10M facts via hierarchical routing, integrated audit pipeline at p95 < 0.2ms. Zero LLM forward calls."

**Pending the in-flight wave:** multi-hop revival path identified or definitively closed; anisotropy mechanism confirmed or honest-negative; compositional generalization enabled or capped; continual operation extended to 5000+ cycles.

### Strategic decisions to revisit when wave lands
1. If multi-hop revival lands: substrate-product gains real multi-hop reasoning; Stage 4 LM-equivalence deferral revisitable
2. If anisotropy fly-LSH dies at adversarial: substrate-product anisotropy story becomes "bypass via partition routing; no actual solve"
3. If Gap 3 cortex schema extraction works: substrate gains true compositional generalization (HUGE for higher cognition)
4. If Gap 4 NREM + homeostasis works: substrate gains continual operation indefinitely (production deployment for systems with continuous ingest)

### Standing user authorizations
- Full auto active
- Spawn budget Fix #14 (≤ 3 concurrent) flexible per user direct instruction
- Skunkworks tier-rule batch when ready
- Default UNDER-claim per Fix #28

### What we'd do next (after wave lands)
1. Skunkworks tier-rule comprehensive next batch (10+ pending cells)
2. Decide multi-hop path (revival succeeded → productionize; refuted → close + position external orchestration)
3. Decide anisotropy path (fly-LSH worked → atomize; failed → close + position bypass-only)
4. If Cell C schema-extraction works → integrate into substrate-product Stage 3
5. If Cell A + B work → spawn long-running continual cell at 10000+ cycles
6. Begin substrate-product Stage 3 application scale-up if all gates above pass

---

## RECORD OF TODAY'S MAJOR FINDINGS (chronological highlights)

- Principle O CHAIN_GRADE_DEFINITIVE
- Stage 2 FREQ_ROUTED_DEEPER CHAIN_GRADE_DEFINITIVE
- Cell A v1 integrated audit-device CHAIN_GRADE (V=600)
- Cell A v2 GPU integrated audit-device CHAIN_GRADE_PRODUCTION_SCALE (V=2000)
- Cell 1 partition routing CHAIN_GRADE @ M=1M
- Cell E hierarchical 2-level CHAIN_GRADE @ M=10M
- Cell 4 permutation-indexed binding CHAIN_GRADE
- Anisotropy rescue v2 fly-LSH MM (not chain-grade-candidate per Skunkworks)
- Wave D V=10000 closure: biology arms NEGATIVE at production V (Mu-Viswanath confirmed)
- Multi-hop 4-for-4 refuted (consolidation, pointer-chain, WM-scaffold, CSP-gated, parallel-vote regime artifact)
- WM multi-bank routing chain-grade-eligible K=1024
- META v3 HARD_PASS 1.000 (by-construction; v4 self-discovered tests real claim)
- META_M7 atomized as 4th rail-discipline meta rule
- META_BARRIER_1_QUADRUPLE_NEGATIVE atomized
- Audit tool `tools/audit_smoke_only_cells.py` shipped (229 strategic backlog cells flagged)
- User intuition arc: multi-bank WM (worked), frequency multiplexing (failed twice; 4-cell evidence pattern), sleep-replay-for-continual (cells being built now), cone-expansion-at-bigger-scale (cells testing now), PFC-as-beam-search-not-top-1 (cells testing now)
- CERT 588 → 600 (+12 today)

---

## PENDING FROM USER (open questions for next interaction)

1. After wave lands: decide if multi-hop revival path or accept 2-hop ceiling permanent
2. After anisotropy v2 batched + expansion-sweep land: decide if substrate-product positioning includes anisotropy "solved" or "bypassed only"
3. After Cell C schema-extraction lands: decide if substrate gains compositional generalization or stays at chain-grade-2-hop
4. After Cell A + B continual-consolidation land: decide if substrate-product extends to long-term continuous operation
5. USER may want to start substrate-product Stage 3 application productionization (chain-grade audit-device deployment) regardless of remaining gaps

— Research (Director), end-of-day 2026-06-25
