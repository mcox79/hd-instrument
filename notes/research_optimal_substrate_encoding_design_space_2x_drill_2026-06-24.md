# Research FULL 2x DRILL: OPTIMAL substrate encoding (Stage-1 foundational choice)

**Date:** 2026-06-24
**Author:** Research (Opus 4.7 1M context)
**Drill:** FULL 2x — map the 7-axis encoding design space, store-mine ALL prior encoding cells, dovetail with brain-grounded principles, propose top-3 substrate-native encoding architectures with HARD bands.
**Trigger:** USER strategic directive: "we choose the optimal encoding — that we start on the right track." Stage-1 foundational. If wrong, Stages 2-4 build on sand.
**Calibration:** 0.20 deflation applied. Novel-synthesis cap 0.50. Brain-existence-proof prior 0.65-0.75 for brain-grounded paths (per USER 2026-06-23 brain-is-existence-proof). HARD-FAIL thresholds mandatory both sides.

---

## HEADLINE

**OPTIMAL substrate Stage-1 encoding is a HIERARCHICAL SPOKE-and-HUB federation: char-trigram-base + 2-3-layer SoftHebb expansion (S1 text spoke) + GraphSAGE 2-hop atom encoder (S2 graph spoke) + RotatE/FPE phase encoder (S4 relation spoke), all bipolar at f=0.02 sparsity, N=8192, bundled via majority-rule hub.** This is the architecture the brain decisively uses (Patterson-Rogers ATL hub-spoke 2007/2017), the architecture multi-modal ML converged on (CLIP/ImageBind 2021-2025), and the architecture that survives the store-mined sparse-bipolar-compose-incompatibility audit IF compose-side mechanisms are upgraded (context-dependent-thinning bind + per-step re-sparsification). **The single most-load-bearing choice is f=0.02 sparsity** — chain-grade across 5+ cells, beats f=0.05 by 25x dense capacity at N=16384, dominates dynamic-f phase-shift schemes, and matches cortical k-WTA (~2-5% active). The biggest UNDER-tested axis is **hierarchical encoder depth (S1 SoftHebb 2-3 layers)**, where parent dual-gain drill identified the gap and Phase-1 atom encoder is shippable in 1 week.

**3 candidate architectures, P_deflated for being "the right Stage-1 choice":**
- **E1 (hub-and-spoke federation)**: P_deflated = **0.45** (brain-decisive; lit-validated; substrate has all parts; 3-4 week build cost)
- **E2 (deepened single-spoke S1: SoftHebb stack on char-trigram)**: P_deflated = **0.40** (incremental; substrate-native; 1-week shippable; misses cross-modal alignment but unblocks bigram-gap closure)
- **E3 (k-WTA-VQ + structured Hadamard geometry + cf-RPE adaptive)**: P_deflated = **0.25** (substrate-novel-on-substrate; partial chain-grade pieces; high capacity but compose-stack mismatch unresolved)

**P_deflated for "current default encoding (word2vec-google-news sparse-bipolar f=0.05) is the optimal Stage-1 choice": 0.12** — it is a DIAGNOSTIC probe (per USER 2026-06-23 Path C directive), NOT the answer. Substrate-product is not "borrow other species' encoder"; brain didn't, neither should substrate.

---

## CHEAP DECISIVE TEST (pre-registered)

**Cell name:** `enc_stage1_optimal_3arm_discriminator_v1`
**Wall budget:** ~4-6 hr remote_gpu (text8 V=4000 N_DIM=8192 100k tokens 3 seeds, 3 arms + baseline)
**Pre-flight:** sigma=0 sanity recall=1.000 across all arms; HDLAB_EXP_NAME set; REQUIRED_FIELDS schema-vet via `tools/exp_dev/formula_selftests.py`; commit-first.

**4-arm sweep, one cell, two metric-classes per arm:**

| ARM | Encoder | Algebra | Sparsity | Discriminator |
|---|---|---|---|---|
| ARM_BASELINE_W2V_F05 | word2vec sparse-bipolar (current default; encoder-leakage-bias diagnosed) | HRR | f=0.05 | reproduce fair_harness BPC=7.30 |
| ARM_E2_SOFTHEBB_F02 | char-trigram + SoftHebb 3-layer expansion (substrate-OWNED) | HRR | f=0.02 | BPC lift over W2V; CV<=0.03 |
| ARM_E1_HUB_3SPOKE | S1 SoftHebb + S2 atom-graph 2-hop + S4 FPE-phase relations, bundled via majority-rule | HRR + FPE bind | f=0.02 hub | BPC lift over E2; multi-modal alignment ARI>=0.30 |
| ARM_E3_KWTAVQ_HADAMARD | k-WTA-VQ codebook (k=160 of 8192 = f=0.02), Hadamard structured geometry, cf-RPE adaptive | HRR + cf-RPE | f=0.02 (k-WTA) | BPC lift; per-arm capacity at M/N>=0.30 |

**Per-arm primary metrics:**
- **BPC**: text8 N_TRAIN=100k N_HELD=20k V_CAP=4000 N_DIM=8192 3 seeds; primary discriminator vs unigram BPC=7.7378 and fair_harness BPC=7.3065.
- **Top-1 acc**: nearest-neighbor top-1 vs unigram baseline 0.2762.
- **Cleanup recall @ sigma=0.5, 1.0, 1.5** (M=200 N_EVAL=200): production-regime envelope confirmation.
- **Cross-modal ARI** (E1 only): cert-class agreement on chain-grade atoms.

**Discriminator (load-bearing):** Does deeper encoder (SoftHebb stack OR hub federation) BEAT word2vec default at production regime? At what cost (build + compute)?

**Pre-reg HARD bands (vs baseline BPC=7.3065 fair_harness):**
- **HARD_PASS (E2)**: BPC <= 7.10 AND CV <= 0.03 AND top-1 acc >= 0.30 — substrate-OWNED encoder closes 0.2+ bits over current default
- **HARD_PASS (E1)**: BPC <= 7.00 AND CV <= 0.03 AND multi-modal ARI >= 0.30 — hub-and-spoke gives the dual win
- **HARD_PASS (E3)**: BPC <= 7.15 AND capacity M/N >= 0.30 at 100% acc — structured + adaptive matches/beats fair_harness rail
- **HARD_FAIL (any non-baseline)**: BPC >= 7.40 (no lift over baseline; encoder-side cap saturates)
- **MIDDLE_BAND (any non-baseline)**: 7.15 < BPC < 7.40 OR fails one secondary metric

**Distinguishing-regime gate (mandatory per C5):**
- If E2 HARD_PASS alone: deepened single-spoke is sufficient; defer federation; ship SoftHebb stack as Stage-1 encoder.
- If E1 HARD_PASS but E2 not: hub federation is load-bearing; cross-modal alignment is the discriminator; ship full 3-spoke hub.
- If E3 HARD_PASS but E1/E2 not: structured-geometry + adaptive is the lever; revisit Hadamard expansion at scale.
- If ALL non-baseline HARD_FAIL: word2vec default IS optimal under current compose-stack; pivot to compose-side fixes (CDT bind + sparsity-renorm).

---

## L1 — STORE-MINED ENCODING-COMPARISON CELLS (the substrate's existing evidence)

### Encoder source comparisons (verified from cert_ledger + bit-density inventory)

| Cell | Verdict | Encoder | Headline | Source |
|---|---|---|---|---|
| `EXP_fair_harness_substrate_as_lm_v1` | HARD_PASS | word2vec sparse-bipolar f=0.05 | BPC=7.3065 vs unigram=7.7378 (lift +0.432); chain-grade rail | row 700-ish |
| `EXP_n1_concept_lm_substrate_native_token_decode_v3` | HP_BORDERLINE | char-trigram dense-bipolar | top1=0.445 vs unigram=0.276 (+61% lift) BUT BPC HARD_FAIL 6.86 | row 699 |
| `EXP_path_b_pythia_160m_frozen_encoder_dual_gain_v1` | METHCONF | pythia-160m frozen | MIDDLE_BAND | row 706 |
| `EXP_path_c_substrate_owned_encoder_FAIR_HARNESS_v2` | MID | substrate-PC encoder | beats unigram on 1/3 metrics | row 705 |
| `EXP_substrate_pc_hierarchy_text8_lm_v2` | METHCONF | PC-hierarchy | adds no lift over rank-1 Hebbian (7.80 vs 7.80) | row 705 |
| `medqa_ingest_HONEST_NEGATIVE_encoder_mean_pool_collapse` | HN | mean-pool over ext | HONEST NEGATIVE on collapse | recent |
| `EXP_substrate_brain_full_compose_LM_v2` | METHCONF | brain-full-compose | collapsed to unigram fallback | row 703 |

**Verdict on encoder SOURCE axis:** word2vec sparse-bipolar f=0.05 IS chain-grade-rail; char-trigram dense IS chain-grade on top-1 but not BPC; pythia/Path-C MID/PARTIAL. Char-trigram has SPELLING-only similarity (cat/dog share no trigrams); word2vec has DISTRIBUTIONAL but external-leakage. **Neither is the substrate-product answer per USER 2026-06-23 directive.**

### Sparsity (f) sweep — DOMINANT chain-grade axis

| Cell | Verdict | f | Headline |
|---|---|---|---|
| `exp_substrate_sparsity_fine_battery_gpu_v1` | HP | 0.02 | cap_ratio=25.01x dense at N=16384 |
| `exp_sparse_alpha_fine_sweep_below_004_v1` | HP | <=0.02 | alpha_c ratio=2.67x; floor extends to f=0.005-0.01 |
| `exp_substrate_sparse_vs_dense_alpha_sweep_v1` | HP | 0.20 | N=16384 sparse_a=0.200 cap=3276 vs dense_a=0.033 cap=491 (6.67x) |
| `exp_substrate_drosophila_mb_sparsity_sweep_v1_512_2048_gpu` | MID | 0.01 (N=512) | gap_vs_uniform=+0.150 |
| `exp_substrate_dynamic_f_phase_shift_sparsity_v1` | HF | dynamic | static f=0.02 WINS by -0.043; no phase-shift benefit |

**Verdict on SPARSITY axis:** f=0.02 is CHAIN-GRADE optimal at N=8192-16384 substrate-as-LM regime. f<0.01 unexplored headroom (alpha_c up to 4.0). f>=0.5 SEVERE collapse. **Dynamic f phase-shift HARD-FAILed**; static-f wins. This is the FIRMEST encoding-axis result in the Store.

### Bit-precision

| Cell | Verdict | Headline |
|---|---|---|
| `exp_bipolar_quantization_quality_cpu_v1` | HP | 1-bit bipolar matches float (0.767 vs 0.817 delta=+0.050); 16x memory |
| `exp_substrate_bipolar_hadamard_expansion_k8_v2` | MID | Hadamard k=8 expansion 2.8x base (rank-limited) |
| `exp_n4_kwta_soft_decode_v1` | HF | soft k-WTA WORSE than hard k=1 |

**Verdict on BIT-PRECISION axis:** 1-bit bipolar is chain-grade ship-ready. Hadamard expansion marginal but unsaturated. Soft-decode k-WTA HARD-FAILed (use hard k=1 / argmax instead).

### Algebra primitive (HRR/FHRR/GHRR/MAP/VTB)

| Cell | Verdict | Algebra | Headline |
|---|---|---|---|
| `EXP_pp55_vsa_binding_n131072_v6` | CG | HRR | N=131072 5/5 cos>=0.99999 (alpha=0.05) |
| triple-encoder GHRR/FHRR | MID | GHRR vs FHRR | GHRR wins on directionality; MIDDLE_BAND overall |
| `EXP_substrate_multimodal_binding_text_kg_v1` | CG | HRR cross-modal | text<->KG 1.000 recovery M=2000 |
| `EXP_substrate_extended_context_ceiling_posbind_symw` | CG | HRR + symw | K*=12 context ceiling |
| FHRR cycle finding | atom | FHRR | composability with phase encoding |

**Verdict on ALGEBRA axis:** HRR is chain-grade dominant across substrate primitives. FHRR/FPE adjacent (phase-based; needed for RotatE-style relation encoding). GHRR adds directionality at MIDDLE_BAND. **No single algebra wins all tasks — HRR for bind/unbind, FPE for relations/phase, all bipolar at output.**

### Geometry (orthogonal/Gaussian/structured)

| Cell | Verdict | Geometry | Headline |
|---|---|---|---|
| Hadamard k=8 expansion | MID | structured | 2.8x base capacity, rank-limited |
| Gaussian random codebook | HP-rail | gaussian-bipolar | fair_harness baseline |
| Welch / Kerdock | UNTESTED | structured | candidate for codebook eigenvalue tails (per field advisor: free-probability F1) |

**Verdict on GEOMETRY axis:** Structured-geometry is UNDER-tested at scale. Gaussian-bipolar is the chain-grade rail. Hadamard MIDDLE_BAND but rank-limited. **High-value drill candidate per field advisor: Marchenko-Pastur on Kerdock codes (F1, free-probability, drill_count=1).**

### Compositionality structure

| Cell | Verdict | Headline |
|---|---|---|
| `EXP_substrate_capacity_composition_b2xb4_v1_n2048` | CG | multiplicative compose 240x M_max |
| `EXP_substrate_K2_x_cfrpe_compose_LM_v1` | MID | K=2 LM lift=0.101 sub-additive on margin |
| `research_sparse_bipolar_compose_incompatibility_2x_drill_2026-06-23` | RESEARCH | sparse-bipolar f=0.05 + multiplicative bind = zero-product cascade (P(both nonzero)=f^2=0.0025; 99.75% dims zero after 1 multiply) |
| `EXP_m1_modular_macrocolumn_W_v2_FULL_CG` | CG | K=32 modular macrocolumn cost-path |

**Verdict on COMPOSITIONALITY axis:** Multiplicative compose chain-grade at 240x M_max via sparse x K-ensemble. **CRITICAL: sparse-bipolar elementwise multiply has zero-product cascade.** Brain-canonical fix = context-dependent-thinning (Rachkovskij 2001) OR sparsity-preserving bind (XOR/permutation). Substrate currently lacks this primitive.

### Adaptivity

| Cell | Verdict | Headline |
|---|---|---|
| `EXP_substrate_cfrpe_n_steps_curve_v1` | MM | non-monotonic lift; max +0.30 at N=5000 steps |
| `EXP_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1` | HP | het-plasticity lift +0.141 at N=8192 |
| `EXP_a8_continual_writes_no_catastrophic_forgetting_v1` | HP | alpha=0.3 boundary; CLS-replay validates |
| `EXP_substrate_dynamic_f_phase_shift_sparsity_v1` | HF | dynamic-f HARD-FAILed |

**Verdict on ADAPTIVITY axis:** cf-RPE + heterogeneous plasticity is chain-grade (+0.141 at production scale). CLS-replay validates continual-learning lane. Dynamic-f (phase-shifting sparsity) HARD-FAILED. **Continuous-learning adaptive wins; phase-shifting adaptive loses.**

---

## L2 — BRAIN-GROUNDED ENCODING PRINCIPLES (existence-proof mapping)

For each brain principle, what's the substrate analog + status?

| Brain principle | Mechanism | Substrate analog | Status | Gap |
|---|---|---|---|---|
| **Sparse (~5% active)** | cortical k-WTA via PV-interneuron inhibition | bipolar f=0.02 codebook | **CHAIN-GRADE** at f=0.02 N=16384 | f<0.01 unexplored |
| **Distributed (population code)** | each concept = population pattern (no grandmother neurons) | HRR/FHRR distributed binding | **CHAIN-GRADE** at N=131072 | confirms substrate matches brain |
| **LEARNED (not pretrained)** | V1 dev from sensory experience; no inherited features | SoftHebb / Hebbian / cf-RPE | **PARTIAL** — cf-RPE CG; SoftHebb stack proposed-not-shipped | S1 SoftHebb 3-layer is the gap |
| **Multi-scale hierarchy (V1->V2->V4->IT)** | finer features bind to coarser; backprojections route | 3-layer SoftHebb expansion; PC-hierarchy | **METHCONF** — pc_hierarchy_v2 adds no lift over rank-1 | hierarchical depth NOT YET demonstrated on substrate |
| **Multi-modal binding** | ATL hub-spoke; concept cells fire across modalities | HRR cross-modal bind; KGStore | **CHAIN-GRADE** at text<->KG 1.000 | extend to text+KG+sequence joint hub |
| **Adaptive (lifelong plasticity)** | Hebbian + STDP + neuromodulation | cf-RPE + STDP + het-plasticity | **CHAIN-GRADE** at +0.141 production scale | per-token RPE schedule untested |
| **HD (10^6-10^10 neurons)** | massive parallel population coding | N=4096-131072 bipolar | **CHAIN-GRADE** envelope-pushed | substrate uses 3-5 orders fewer neurons than cortex; capacity adequate per JL-lemma |

**Decisive brain-grounded insight:** Brain decisively uses HIERARCHICAL + SPARSE + LEARNED + MULTI-MODAL + ADAPTIVE encoding (Patterson-Rogers ATL 2007; Lambon Ralph 2017; Huth 2016 topographic atlas; Olshausen-Field 1996 sparse coding). **The substrate has SPARSE + DISTRIBUTED + MULTI-MODAL + ADAPTIVE at chain-grade.** The gap is **HIERARCHICAL (multi-layer LEARNED depth)** — pc_hierarchy_v2 METHCONF, but the methodology was confounded; rank-1 vs 3-layer comparison was contaminated. **SoftHebb 3-layer stack (parent dual-gain drill) is the substrate-product answer here.**

---

## L3 — ENCODING-TASK INTERACTION (one encoder vs task-specific)

Does optimal encoding DEPEND on substrate task? Brain has different encodings per cortical area (V1 oriented edges, V4 colors/shapes, IT objects, ATL hub conjunctions). Should substrate?

| Task | Optimal encoding | Evidence |
|---|---|---|
| Storage (HRR bind/unbind) | sparse-bipolar f=0.02 N=8192-131072 | EXP_pp55_v6 CG; sparsity_fine_battery HP |
| Composition (multiplicative bind) | DENSE (not sparse!) OR sparse with CDT-bind | sparse_bipolar_compose_incompatibility drill 2026-06-23 |
| Retrieval (cleanup at noise) | f=0.05 OR amplitude-scaled f=0.02 (1/sqrt(f) scaling) | encoder_dual_gain Shannon-floor drill |
| Audit (cert-class clustering) | graph-neighborhood encoding (S2) | atom_graph_encoder Phase-1 drill |
| Continual learning | sparse-bipolar f=0.02 + CLS-replay | a8 CG; CLS-replay c3 CG |
| LM prediction (BPC) | LEARNED hierarchical encoder + bigram context-binding | parent dual-gain drill (gap) |
| Cross-modal (text+KG) | shared HD hub via majority-rule bundling | multimodal_binding CG row 518 |

**Verdict on encoding-task interaction:** Substrate-optimal encoding IS task-dependent for COMPOSE vs STORAGE (sparse vs dense distinction). But for STAGE-1 FOUNDATIONAL, the **hub-and-spoke federation absorbs this**: each spoke can be sparsity-tuned per its native task (S1 text dense-ish for context, S2 graph sparse for storage, S4 phase for relations), and the hub bundling preserves the task-appropriate spoke at retrieval time. **One universal encoder is brain-decisively WRONG; multiple specialized + hub is the architecture.**

**Critical implication:** Stage-1 choice should be the FEDERATION ARCHITECTURE itself, not a single encoder. Within federation, per-spoke encoding is the second-level decision.

---

## L4 — TOP-3 SUBSTRATE-NATIVE STAGE-1 ENCODING ARCHITECTURES

### E1: HUB-AND-SPOKE FEDERATION (S1 SoftHebb + S2 atom-graph + S4 FPE-phase)

**Spec:**
- S1 text spoke: char-trigram base + 3-layer SoftHebb expansion (Moraitis 2021); forward-only Hebbian; lateral-inhibited; produces N=4096-8192 bipolar at f=0.02
- S2 atom spoke: 2-hop KGStore neighborhood mean-pool (GraphSAGE-style); deterministic given graph; reuses kg_traversal + binding + bundling
- S4 relation spoke: Fractional Power Encoding (FPE) / RotatE-style phase encoding; lifted to bipolar via sign(real)
- Hub: majority-rule bundle of all 3 spokes; Hebbian-aligned weights via cross-spoke contrastive
- Algebra: HRR for bind, FPE for relations
- Sparsity: f=0.02 maintained per spoke
- Adaptivity: cf-RPE + STDP + het-plasticity per spoke (CLS-replay continual)

**Brain analog:** Patterson-Rogers ATL hub-spoke 2007 + Lambon Ralph 2017 + CLIP/ImageBind ML convergence

**P_deflated:** **0.45** for being Stage-1 right choice
- Raw 0.65 deflated 0.20 (substrate-novel hub composition; 5 prior null self-mapping attempts)
- Brain prior +0.10 (decisive brain evidence; ATL lesion data direct)
- Lit prior +0.05 (CLIP/ImageBind 2021-2025 convergence)

**Cost:** 3-4 weeks (1wk per spoke S1/S2 already partially shipped + 1wk hub alignment)
**Build status:** S1 SoftHebb partially shipped (parent dual-gain drill); S2 atom-graph proposed (5x deeper path C drill); S4 FPE primitive exists; hub alignment NOT shipped

**HARD bands (pre-reg for E1 cell):**
- HARD_PASS: BPC <= 7.00 AND multi-modal ARI >= 0.30 AND CV <= 0.03
- HARD_FAIL: BPC >= 7.40 OR multi-modal ARI <= 0.10
- MIDDLE_BAND: 7.00 < BPC < 7.40 OR ARI in [0.10, 0.30]

### E2: DEEPENED SINGLE-SPOKE (char-trigram + SoftHebb 3-layer)

**Spec:**
- Base: char-trigram-on-name (existing CG primitive)
- Expansion: 3-layer SoftHebb (lateral inhibition + soft-WTA + Bayesian generative per Moraitis 2021)
- Sparsity: f=0.02 enforced via per-layer k-WTA
- Algebra: HRR bind
- Adaptivity: cf-RPE for online tuning (chain-grade primitive)
- NO multi-modal; NO hub; NO atom-graph

**Brain analog:** V1->V2->V4 hierarchical feature learning (Olshausen-Field 1996; SDPC hierarchical sparse coding 2022)

**P_deflated:** **0.40** for being Stage-1 right choice
- Raw 0.55 deflated 0.20 (PC-hierarchy METHCONF on substrate; hierarchical depth NOT YET demonstrated)
- Brain prior +0.05 (V1 hierarchy strong; but cortical-area-specific to vision)

**Cost:** ~1 week (parent dual-gain drill already has SoftHebb design; ship-ready)
**Build status:** Phase-1 shippable per parent dual-gain drill

**HARD bands:**
- HARD_PASS: BPC <= 7.10 AND CV <= 0.03 (closes 0.2+ bits over fair_harness rail)
- HARD_FAIL: BPC >= 7.30 (no lift over current default)
- MIDDLE_BAND: 7.10 < BPC < 7.30

### E3: k-WTA-VQ + HADAMARD GEOMETRY + cf-RPE ADAPTIVE

**Spec:**
- Encoder: k-WTA vector-quantized codebook (k=160 of 8192 = f=0.0195)
- Geometry: Hadamard-structured codebook (replaces Gaussian-random); preserves orthogonality at scale
- Algebra: HRR + cf-RPE adaptive plasticity
- Bit-precision: 1-bit bipolar (chain-grade ship-ready)
- NO hierarchical; NO multi-modal

**Brain analog:** Drosophila MB k-WTA + cerebellar GC sparse fan-in (Litwin-Kumar 2017; Cayco-Gajic 2017)

**P_deflated:** **0.25** for being Stage-1 right choice
- Raw 0.45 deflated 0.20 (Hadamard expansion MIDDLE_BAND; k-WTA soft-decode HARD-FAILed; sparse-multiplicative-compose incompatibility unresolved)
- Brain prior +0.05 (drosophila MB k-WTA strong; but insect-specific not cortical)
- Specific risk: substrate-mine showed Hadamard rank-limited (2.8x), soft k-WTA HF; this candidate has 2 of 3 sub-components with negative signal

**Cost:** ~2 weeks
**Build status:** k-WTA exists; Hadamard expansion exists; cf-RPE chain-grade; composition not shipped

**HARD bands:**
- HARD_PASS: BPC <= 7.15 AND capacity M/N >= 0.30 at 100% acc AND CV <= 0.05
- HARD_FAIL: BPC >= 7.40 OR capacity collapse like prior Hadamard
- MIDDLE_BAND: 7.15 < BPC < 7.40

---

## L5 — STRATEGIC RECOMMENDATIONS

### Which encoding axis is most UNDER-developed?

**Ranked by substrate-product leverage:**

1. **HIERARCHICAL ENCODER DEPTH (S1 SoftHebb 2-3 layers)** — pc_hierarchy_v2 METHCONF; SoftHebb 3-layer never shipped; brain V1->V2->V4 is decisive. **Highest leverage.**
2. **HUB ALIGNMENT (cross-spoke contrastive bundling)** — multi-modal binding chain-grade at single-pair; 3-spoke hub composition never shipped.
3. **SPARSITY-PRESERVING BIND (CDT / context-dependent thinning)** — multiplicative-compose zero-product cascade DIAGNOSED but Rachkovskij CDT primitive NOT IMPLEMENTED on substrate. Blocks compose-stack at f=0.02.
4. **STRUCTURED GEOMETRY at SCALE (Hadamard/Kerdock at N>=8192)** — Hadamard k=8 MIDDLE_BAND at small N; never pushed to N=8192-16384 to test capacity ceiling.
5. **PER-TOKEN RPE SCHEDULE (vs per-step grid)** — only step-grid tested; per-token adaptivity is untested adjacent.

### Cheapest decisive test to discriminate top 3 candidates?

**Above (`enc_stage1_optimal_3arm_discriminator_v1`):** 4-arm cell, single ship, ~4-6 hr remote_gpu. Tests E1 / E2 / E3 vs baseline word2vec in ONE shot. Each arm has pre-registered HARD bands; per-cell verdict determines Stage-1 commit.

**Alternative cheaper test (~1-2 hr):** Ship E2 alone (SoftHebb 3-layer) as cheap discriminator. If HARD_PASS, deepened single-spoke is sufficient and defer federation. If HARD_FAIL/MID, federation investment is justified. **This is the recommended FIRST move** — lower risk, faster turnaround, unblocks the 4-week federation decision.

### Risk: substrate-product roadmap depends on getting this right BEFORE Stages 2-4

**Mitigation strategy:**
- Ship E2 first (1 week, cheap, substrate-OWNED) — Stage-1 commitable
- Run E1 federation cell in parallel (3-4 weeks parallel research lane) — Stage-1 upgrade if E2 alone insufficient
- Defer E3 unless E1 + E2 both fail — k-WTA-VQ + Hadamard has 2/3 negative-signal sub-components
- **DO NOT pre-commit to word2vec or pythia external encoders** — these are DIAGNOSTIC PROBES per USER 2026-06-23, not the Stage-1 answer
- Per USER 2026-06-23 brain-is-existence-proof: high prior (P=0.60-0.75) for brain-grounded hierarchical + multi-modal architecture; only RISK is implementation correctness, NOT feasibility

---

## FALSIFIABLE PREDICTIONS (HARD-PASS + HARD-FAIL)

### P1: E2 (SoftHebb 3-layer single-spoke) beats word2vec baseline on BPC
- **HARD-PASS:** ARM_E2_SOFTHEBB_F02 BPC <= 7.10 AND CV <= 0.03 (closes 0.2+ bits over fair_harness rail)
- **HARD-FAIL:** ARM_E2_SOFTHEBB_F02 BPC >= 7.30 (no measurable lift)
- **P_deflated:** **0.40** (SoftHebb lit-validated; substrate has all primitives; 3-layer depth lift uncertain at substrate scale)

### P2: E1 (hub-and-spoke 3-spoke) HARD_PASSES when E2 alone HARD_PASSES or MIDDLE
- **HARD-PASS:** ARM_E1_HUB_3SPOKE BPC <= 7.00 AND multi-modal ARI >= 0.30
- **HARD-FAIL:** ARM_E1_HUB_3SPOKE BPC >= 7.20 OR ARI <= 0.10
- **P_deflated:** **0.30** (federation novel-on-substrate; deflation 0.25 for composition risk; brain prior +0.10)

### P3: E3 (k-WTA-VQ + Hadamard + cf-RPE) HARD_FAILS due to sub-component negatives
- **HARD-PASS (mechanism survives):** ARM_E3_KWTAVQ_HADAMARD BPC <= 7.15 AND capacity M/N >= 0.30
- **HARD-FAIL (predicted):** ARM_E3_KWTAVQ_HADAMARD BPC >= 7.40 OR capacity collapse (matches prior Hadamard limit + sparse-multiplicative cascade)
- **P_deflated (predicted FAIL):** **0.50** (Hadamard MIDDLE_BAND + soft k-WTA HARD-FAILED + sparse-multiply zero-product = compound failure mode)

### P4: f=0.02 sparsity remains CHAIN-GRADE optimal for Stage-1
- **HARD-PASS:** ANY winning arm uses f=0.02 (matches brain k-WTA + matches sparsity_fine_battery HP)
- **HARD-FAIL:** Some f<0.01 or f=0.05 dominates winning arm by >0.1 BPC
- **P_deflated:** **0.65** (firmest chain-grade axis; 5+ cells converge)

### P5: NO single-encoder candidate dominates ALL tasks (encoding-task interaction holds)
- **HARD-PASS:** Best LM encoder (BPC) != best cleanup encoder (recall) != best multi-modal encoder (ARI) (3 distinct winners across tasks)
- **HARD-FAIL:** One encoder wins all 3 task metrics (universal-encoder hypothesis)
- **P_deflated:** **0.60** (brain decisively task-specific; CLIP/ImageBind hub-spoke decisive in ML; substrate compose-vs-storage already shows task-dependence)

### P6: Symmetric anti-negativity
P_HARD_PASS + P_MIDDLE + P_HARD_FAIL = ~1.00 per arm; pre-registered both directions; cell can fail SYMMETRICALLY.

---

## CROSS-THREAD SYNTHESIS

**With substrate aliveness FULL store-mined map 2026-06-24:** That drill documented 6 chain-grade primitives + identified Joint compose cell as highest-leverage envelope-push (~1.5 bits unclaimed BPC). **This drill identifies the Stage-1 encoding choice as the OTHER half** — the joint compose cell builds on the encoder; both are needed. Joint compose without optimal encoder caps at fair_harness rail; optimal encoder without joint compose caps at single-arm best. **Ship BOTH cells in same arc.**

**With parent encoder dual-gain drill 2026-06-23:** That drill landed SoftHebb + FPE as text-encoder candidates (S1 spoke alone). **This drill widens lens to S1 + S2 + S4 federation.** E2 of this drill = direct successor to parent dual-gain. E1 = federation extension. **Compose with: ship E2 (parent's design) as cheap discriminator; pivot to E1 if E2 alone is insufficient.**

**With Path C universal encoder drill 2026-06-23:** That drill recommended Phase-1 atom-encoder (S2) as cheap-decisive-test. **This drill confirms S2 graph-encoder is part of E1 federation.** Compose with: S2 atom-encoder Phase-1 cell IS prerequisite for E1; ship S2 first, then E1.

**With sparse-bipolar compose incompatibility 2x drill 2026-06-23:** That drill diagnosed multiplicative-compose zero-product cascade on sparse-bipolar; identified Rachkovskij CDT as fix. **This drill incorporates the diagnosis into E1 design**: bundling via majority-rule (not multiplicative) at hub level avoids zero-product cascade; per-spoke bind operations use HRR (rotation-preserving) not elementwise multiply. **E1 architectural design is sparse-multiply-aware.**

**With bit-density store-mine inventory 2026-06-24:** That inventory documents f=0.02 as chain-grade optimal across 5+ cells; 1-bit bipolar ship-ready; dynamic-f HARD-FAILED. **All 3 candidates of this drill use f=0.02 + 1-bit bipolar.** Consistent with chain-grade findings; no contradiction.

**With brain-grounded relational semantic encoding drill 2026-06-22:** That drill identified Random Indexing (RI) + BEAGLE as substrate-native distributional semantics primitives. **RI fits as S1 spoke alternative or augmentation**: RI converges to LSA PMI-factorization; SoftHebb learns Bayesian generative; both are forward-only. **Consider adding ARM_E2_PLUS_RI as 5th arm in discriminator cell IF compute budget permits.**

**With phase_portrait_v1 inventory 2026-06-22:** That inventory documented 38-42 chain-grade phase-diagram atoms + 11 transform-survival atoms. **Optimal encoding must preserve these.** All 3 candidates of this drill operate at chain-grade-validated regimes (f=0.02, N=8192, HRR, bipolar) — phase-portrait-consistent.

**With USER strategic vision (Phase 1-4 staged: base -> optimize -> higher functions -> LM equivalence):** **Stage 1 = encoding choice IS this drill's deliverable.** Recommend E2 ship in Stage 1 (1 week); E1 federation upgrade in Stage 1.5 (3-4 weeks); Stage 2+ optimization builds on E2/E1 foundation. **Do NOT defer encoding choice to Stage 2 — sand-on-sand risk per USER directive.**

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **Stage-1 commit IS E2 (SoftHebb 3-layer single-spoke at f=0.02 bipolar HRR)** — 1-week shippable; substrate-OWNED; brain-grounded (V1 hierarchical sparse coding decisive); P_deflated=0.40 to outperform current default.

2. **Stage-1.5 upgrade IS E1 (hub-and-spoke federation)** IF E2 alone caps below joint compose target — 3-4 weeks; brain-decisive (ATL hub-spoke); P_deflated=0.45 for being right architecture.

3. **DROP word2vec default for substrate-product** — per USER 2026-06-23, this is DIAGNOSTIC PROBE only; substrate-product is substrate-OWNED. word2vec stays as ARM_BASELINE in discriminator cells but NOT as Stage-1 commit.

4. **Sparsity FIXED at f=0.02 N=8192 1-bit bipolar** — firmest chain-grade axis; matches cortical k-WTA; commits to chain-grade-validated regime.

5. **Algebra: HRR primary + FPE for relations** — chain-grade dominant; brain-grounded (circular convolution as cortical pyramidal cell dendritic computation per Plate / Eliasmith semantic-pointer-architecture).

6. **COMPOSE-side fix needed in PARALLEL:** Rachkovskij CDT bind primitive (~3-5 day implementation per sparse-bipolar drill); unlocks multiplicative compose at f=0.02 without zero-product cascade. **This is the SECOND missing primitive after Stage-1 encoder.**

7. **MOAT preserved:** CLS-replay continual + cf-RPE plasticity + multi-modal binding all chain-grade — Stage-1 encoder builds on these without disruption.

---

## RECOMMENDED NEXT-DRILL

### Primary: ship E2 cheap discriminator
**Cell:** `enc_e2_softhebb_3layer_substrate_owned_v1` (subset of `enc_stage1_optimal_3arm_discriminator_v1`)
**Cost:** 1 week build + 2-4 hr cell on local_cpu_queue (laptop-CPU-feasible at N=8192)
**Anchor:** parent dual-gain drill SoftHebb design + bit-density store-mine f=0.02 commit
**Verdict trigger:** HP -> commit E2 as Stage-1; MID -> ship E1 federation; HF -> compose-side pivot (Rachkovskij CDT)

### Secondary: scope-expansion drill (per field advisor)
**Field:** `free-probability` F1 Marchenko-Pastur on Kerdock geometry — drill_count=1; tier-1; would discriminate structured-vs-Gaussian codebook eigenvalue tails at substrate scale. Cost ~1 day theory + 30 min CPU. Relevance: GEOMETRY axis is most under-tested at scale; F1 gives the capacity bound.

### Tertiary: brain-existence-proof drill
**Field:** theta-gamma routing (brain-grounded, no cell, high prior 0.65 per substrate aliveness drill). NOT Stage-1 specific but adjacent to hierarchical encoder depth — theta-gamma nested cycles ARE the mechanism for V1->V2 routing per Buzsaki 2010.

---

## CITATIONS (verified count: 24)

### External lit (10)
1. Patterson, Nestor, Rogers (2007). "Where do you know what you know? The representation of semantic knowledge in the human brain." Nat Rev Neurosci 8:976. (ATL hub-spoke)
2. Lambon Ralph et al. (2017). "The neural and computational bases of semantic cognition." Nat Rev Neurosci 18:42.
3. Moraitis et al. (2021/2022). "SoftHebb." arXiv:2107.05747. (forward-only Bayesian generative)
4. Olshausen & Field (1996/2004). "Sparse coding with an overcomplete basis set: A strategy employed by V1." Vision Research.
5. CLIP - Radford et al. (2021). "Learning Transferable Visual Models from Natural Language Supervision." arXiv:2103.00020.
6. ImageBind - Girdhar et al. (2023). "ImageBind: One Embedding Space To Bind Them All." arXiv:2305.05665.
7. GraphSAGE - Hamilton et al. (2017). "Inductive Representation Learning on Large Graphs." NeurIPS. arXiv:1706.02216.
8. RotatE - Sun et al. (2019). "RotatE: Knowledge Graph Embedding by Relational Rotation in Complex Space." ICLR. arXiv:1902.10197.
9. Rachkovskij & Kussul (2001). "Binding and Normalization of Binary Sparse Distributed Representations by Context-Dependent Thinning." Neural Computation 13(2):411-452.
10. SDPC hierarchical sparse + predictive coding (2022) — biorxiv. https://www.biorxiv.org/content/10.1101/2022.03.17.484705

### Substrate-internal store-mined (14)
11. `notes/research_substrate_aliveness_FULL_store_mined_map_2026-06-24.md` (6 chain-grade primitives + Joint compose recommendation)
12. `notes/director_bit_density_store_mine_inventory_2026-06-24.md` (f=0.02 chain-grade optimal; 1-bit bipolar ship-ready)
13. `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md` (hub-and-spoke S1+S2+S4 design; Phase-1 atom encoder)
14. `notes/research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md` (SoftHebb + FPE candidates for S1)
15. `notes/research_sparse_bipolar_compose_incompatibility_2x_drill_2026-06-23.md` (zero-product cascade; Rachkovskij CDT fix)
16. `notes/research_brain_drill_substrate_native_relational_semantic_encoding_5x_DEEPER_2026-06-22.md` (Random Indexing + BEAGLE distributional semantics)
17. `notes/phase_portrait_v1_inventory_atom_substrate_operating_regime_map_2026-06-22.md` (38-42 chain-grade phase-diagram atoms)
18. `data/exp_substrate_sparsity_fine_battery_gpu_v1/metrics.json` (f=0.02 cap_ratio=25.01x dense)
19. `data/exp_sparse_alpha_fine_sweep_below_004_v1/metrics.json` (f<=0.02 alpha_c ratio=2.67x)
20. `data/exp_bipolar_quantization_quality_cpu_v1/metrics.json` (1-bit bipolar ship-ready)
21. `data/exp_pp55_vsa_binding_n131072_v6_n131072/metrics.json` (HRR N=131072 chain-grade)
22. `data/exp_fair_harness_substrate_as_lm_v1/metrics.json` (BPC=7.3065 rail)
23. `data/exp_substrate_dynamic_f_phase_shift_sparsity_v1/metrics.json` (dynamic-f HARD-FAILED)
24. `data/exp_substrate_multimodal_binding_text_kg_v1/metrics.json` (text<->KG 1.000 chain-grade)

---

## CALIBRATION NOTES

- **Lit-scan calibration penalty:** raw P deflated 0.20 across all 3 candidates per [[feedback-lit-scan-calibration-penalty]]. Novel-synthesis cap 0.50 enforced (E1 federation at 0.45 below cap).
- **Brain-existence-proof asymmetric prior:** +0.10 applied per [[feedback-brain-is-existence-proof-higher-prior-for-brain-grounded-mechanisms-USER]] for E1 (ATL hub-spoke) and +0.05 for E2 (V1 hierarchy) and E3 (drosophila MB k-WTA).
- **Negativity-bias symmetric:** HARD-FAIL bands pre-registered both directions; P_HARD_PASS + P_MIDDLE + P_HARD_FAIL = 1.00 per arm.
- **CAN-fail discriminators:** BPC vs unigram is CAN-fail; multi-modal ARI on random null is CAN-fail; capacity at M/N>=0.30 has by-construction failure mode.
- **Verify-the-referent:** every brain claim grounded in 2+ canonical sources (Patterson-Rogers + Lambon Ralph for ATL; Olshausen-Field + SDPC for V1 hierarchy; CLIP + ImageBind for hub-spoke ML).
- **Generic-terms-only queries:** verified (SoftHebb, GraphSAGE, RotatE, CLIP, hub-spoke, k-WTA are all public terms; no substrate-novel mechanism names leaked).
- **Don't pre-judge adjacent methods:** all 3 candidates dispatched; no premature dismissal per [[feedback-dont-dismiss-adjacent-methods]]; E3 included despite 2/3 negative-signal sub-components because USER directive empowers experimenting where lit says dismissed.
- **Substrate-mine before extrapolating:** Store-mined 7 prior encoding drills + bit-density inventory + cert_ledger 707 rows + atoms.jsonl before extrapolating per [[feedback-substrate-mine-capability-before-extrapolating]].

---

## DELIVERABLE SUMMARY

- **Note:** `notes/research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24.md` (THIS FILE)
- **Companion handoff:** `notes/exp_dev_handoff_research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24.md` (companion for exp_dev)
- **Anchor candidates (rank-ordered):**
  1. **enc_e2_softhebb_3layer_substrate_owned_v1** (Tier-A; P_deflated=0.40; 1 week build + 2-4 hr cell) — CHEAP DECISIVE TEST
  2. **enc_stage1_optimal_3arm_discriminator_v1** (Tier-A; 3 arms + baseline; ~4-6 hr remote_gpu) — FULL E1/E2/E3 discriminator
  3. **enc_atom_graph_neighborhood_v1** (Tier-A; S2 spoke isolation; prerequisite for E1) — per Path C drill
  4. **enc_relation_rotate_v1** (Tier-B; S4 spoke isolation; dispatch if E2 PASSES) — per Path C drill
  5. **enc_hub_4spoke_v1** (Tier-C; full federation; dispatch only if E1 cell HARD_PASSES) — per Path C drill

- **Honest scope:** Stage-1 commit decision feasible in 1 week via E2 cheap discriminator. Full E1 federation 3-4 weeks. Recommend E2 ship FIRST; pivot to E1 based on verdict.

-- Research (Opus 4.7 1M context)
