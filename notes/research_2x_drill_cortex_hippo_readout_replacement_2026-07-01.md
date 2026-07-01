# research 2x-drill — cortex-Hopfield as READOUT-REPLACEMENT (not compose)

**Filed:** 2026-07-01
**Trigger:** cell-author ade5bb72 smoke on `exp_cortex_hippo_dense_layer_M8192_v1_seed_7` HARD_FAILed with dense_gain=-0.740. Additive composition (HA_HC_DENSE=0.008) collapsed below Ha+Hc baseline (0.748). Cell-author then tested READOUT-REPLACEMENT variant: dense-Hopfield direct key→attn→val bypassing cortex-Hebbian, recall=1.000 at beta>=8 in M=512 smoke. This drill re-scopes Cell D from compose to REPLACE.
**Calibration:** novel-synthesis; deflate agent P by 0.15-0.25; cap novel-synthesis P at 0.50 per [[feedback-lit-scan-calibration-penalty]].
**Prior context:** `research_5x_drill_cortex_hippo_M8192_rescue_2026-07-01.md` (5x drill that recommended dense-Hopfield rescue; classified path as compose-with-Ha+Hc — empirically wrong).

## HEADLINE

Cross-domain literature unanimously supports READOUT-REPLACEMENT over additive composition: the transformer/Ramsauer 2021 paradigm IS key->attention->value direct retrieval, not "attention on top of Hebbian readout." The empirical Ha+Hc+DENSE collapse is exactly the predicted failure mode of composing a lossy bipolar readout with a soft attention query — the substrate readout ceiling (0.75) becomes the query ceiling, and dense-Hopfield metastable-state collision under noisy query drives collapse to 0.008. Recommended Cell D v2 is REPLACEMENT: cortex layer reads directly from a Hebbian write-side memory tape via product-key or dense-Hopfield attention. This IS the "cortex layer above substrate" M3 architecture — the read path is attention, the write path stays Hebbian. P_deflated (M=8192 chain-grade recall >= 0.90): **0.42**.

## Cheap decisive test

Author **Cell D v2**: `cortex_hippo_readout_replacement_M8192_v2`
- Substrate WRITES via Ha (Hebbian cross-term) into a memory tape (key_i, value_i) pairs; NO cortex-Hebbian read path
- Cortex READS via dense-Hopfield attention: query q → softmax(beta * q @ K^T) @ V → decoded value
- Compose Ha (write) with attention (read); DO NOT run cortex-Hebbian readout at all
- 5 arms:
  - (a) ARM_STANDARD (clean write, direct decode) — sanity ceiling
  - (b) ARM_HA_ONLY (Hebbian read, current baseline) — expect ~0.75 bipolar ceiling
  - (c) ARM_DENSE_REPLACE_beta_8 (attention read, beta=8) — hypothesis: >=0.90 at M=8192
  - (d) ARM_DENSE_REPLACE_beta_32 (attention read, beta=32) — sharpness sweep
  - (e) ARM_DENSE_REPLACE_beta_128 (attention read, beta=128) — saturation regime; check metastable collapse
- CARDINALITY_OK: M=8192, N_c=4096, K=200 K-banks (Hc partition still on write), 5 arms, 3 seeds
- **Smoke discipline:** smoke at M=512 first (proves cell RUNS), then M=8192 preview arm before full dispatch per [[feedback-discriminator-must-survive-scale-before-full-dispatch]]. The smoke result already exists from ade5bb72; v2 mainly needs the REPLACE arms wired.

Runtime estimate: ~2h remote_cpu (matmul-bound); consider remote_gpu route per [[feedback-gpu-underutilization-route-heavy-cells-via-orchestrator]].

## Falsifiable predictions

**HARD-PASS (READOUT-REPLACEMENT closes 49% remainder gap at chain-grade):**
- Arm (c) beta=8 achieves recall_cortex >= 0.90 at M=8192, N_c=4096 (crosses the 49% gap)
- Arm (c)/(d)/(e) monotone in beta over [8, 32]; recall >= 0.90 sustained; beta=128 may collapse to metastable states (expected per literature)
- Delta between arm (c) and arm (b) Ha-only baseline is >= 15 percentage points (attention read is discriminator, not scenery)

**HARD-FAIL (path closed):**
- Arm (c) recall < 0.60 at M=8192 → replacement doesn't survive scale; the M=512 smoke result was a low-M artifact and the substrate write side is what caps recall (not the read path)
- Arm (c)/(d)/(e) ALL collapse below 0.5 → dense-Hopfield attention saturates on bipolar-quantized keys under M=8192 load; falls back to path 2 (Product-Key Memory hierarchical decomposition)
- Delta between arm (c) and arm (b) < 5 percentage points → attention read is scenery, Hebbian was doing the work

**MIDDLE_BAND (0.60 <= recall(c) < 0.90):**
- Partial rescue; MM_PARTIAL classification; queue beta-sweep + M-sweep drill to find exact saturation crossover

## Per-question findings

### Q1 — Cross-domain lit precedent for READOUT-REPLACEMENT

**Product-Key Memory (Lample 2019; Meta Memory Layers at Scale 2024):**
- Exactly the target architecture: query → product-key decomposition into 2 sub-key sets, exact nearest-neighbor over full O(sqrt(M)) key space, value lookup — memory scales to 1B parameters with negligible compute overhead
- Read path is EXCLUSIVELY attention-based (softmax over top-K matched sub-keys); write path is gradient-updatable memory tape
- Explicit design choice: read path REPLACES not composes with any prior lookup mechanism
- Direct M3 precedent for cortex-side dense retrieval

**Modern Hopfield / Ramsauer 2021 "Hopfield Networks is All You Need":**
- Transformer attention IS one step of Hopfield fixed-point iteration
- "Query = state pattern", "Keys = stored patterns", "Values = output". This is inherently a REPLACEMENT architecture — the attention IS the retrieval
- No published architecture composes Hopfield attention as a corrective layer on top of another readout; every dense-Hopfield paper treats it as the retrieval path

**Hebbian Memory-Augmented (Engram Neural Network, arxiv/2507.21474):**
- Explicit design: input + prior hidden + retrieved memory + Hebbian trace are COMPOSED at update time
- Critically, "retrieved memory" is the ATTENTION-DRIVEN retrieval, not a Hebbian readout — Hebbian is the WRITE plasticity, attention is the READ path
- Confirms the substrate direction: Hebbian for write plasticity, attention for read

**Hippocampal Indexing Theory (Teyler-DiScenna; Reassessment Authorea 2024):**
- Hippocampus stores pointers/indices; cortex holds the content; retrieval is INDEX->CONTENT via a direct content-addressable lookup
- Bio parallel: substrate is the write-side index (Ha Hebbian trace) + Hc partitioning; cortex-side attention is the read-side content lookup
- Bio does NOT compose two readouts — cortex reads directly from index
- This is the STRUCTURAL PRECEDENT for READOUT-REPLACEMENT

**TrueNorth / neuromorphic key-value:** search returned less direct evidence (TrueNorth is limited by low-precision synapses ±0,±1,±2 — dense-Hopfield's exp(<x,W>) is not natural on hardware). But the memristor/PCM in-memory dot-product literature (arxiv Sebastian 2020) supports high-dim bipolar keys + parallel similarity — exactly the substrate + attention combo.

**Conclusion:** all four literatures point to REPLACE-not-COMPOSE. The additive-composition failure at ade5bb72 was predicted by the field — nobody in modern-Hopfield / MAM lit composes attention on top of a Hebbian readout.

**Citations verified this drill:** 8 (Lample 2019 NeurIPS; Meta arxiv/2412.09764 Memory Layers at Scale; Ramsauer 2021 ICLR; Engram arxiv/2507.21474; Reassessment Hippocampal Index Theory Authorea 2024; MAM systematic review arxiv/2508.10824; Sebastian 2020 Nature Nanotech; TrueNorth Open Neuromorphic 2024).

### Q2 — Does recall=1.000 hold at M=8192 (14x above Amit)?

**Theoretical:**
- Amit classical bound 0.138N is a LINEAR-CAPACITY floor; dense-Hopfield capacity is EXPONENTIAL: 2^(αN) with α~0.14 (Ramsauer 2021; Demircigil 2017; Provably Optimal Capacity arxiv/2410.23126 Lucibello-Mezard 2024)
- For N_c=4096: theoretical retrievable patterns ~ 2^573 — M=8192 is well within the exponential regime
- Recent tight bound: modern-Hopfield capacity equals spherical-code capacity (arxiv/2410.23126) — capacity is set by minimum key separation angle, not by M/N ratio
- **BUT bipolar keys reduce effective code-book:** the spherical-code capacity applies to continuous keys on the sphere; bipolar keys sit at 2^N corners of the hypercube. Effective capacity is still exponential but with smaller α (roughly α_bipolar ~ 0.14 * (1 - b^2) per Feature-Correlation arxiv/2508.01395; b=0 for balanced bipolar keeps capacity high)

**Empirical M=8192 prediction:**
- If keys are drawn i.i.d. balanced-bipolar (b=0), α_effective~0.14 → retrievable patterns ~ 2^573 → M=8192 recall should hold near 1.0 for sufficient beta
- If keys are CORRELATED (real substrate has Ha cross-term structure imposing correlation), effective capacity drops. Feature-correlation arxiv/2508.01395 shows correlated keys reduce capacity by (1 - overlap)^2 factor; if key overlap ~ 0.3, effective M_cap ~ 4900 at N_c=4096 → M=8192 sits at 1.7x saturation — recall degrades but should still exceed 0.75 bipolar-readout ceiling
- **Key uncertainty:** the M=512 smoke used clean keys with likely low overlap. At M=8192, keys may exhibit greater overlap from Ha write side, degrading capacity. HARD-FAIL criterion (c) < 0.60 is calibrated for this risk.

### Q3 — Composability with Ha as substrate-side write while cortex reads via attention

**Two-tier structural pattern (transformer paradigm):**
- Ha = write-time Hebbian plasticity (memory encoding); this IS the "learned weights" in transformer terms
- Cortex attention = read-time content-addressable lookup
- These are ORTHOGONAL: write path shapes the (K, V) tape; read path queries it
- This is the natural composition — additive composition of two READ paths is the anti-pattern

**Substrate-specific detail:**
- Ha cross-term populates the (key, value) storage matrix M_ij with pattern outer-products (Hebbian rule); attention softmax(beta * q @ K^T) @ V then reads
- Hc K-bank compartmentalization can gate WHICH partition of the tape attention reads over (routing) — this is a hierarchical MoE-style read (Meta Memory Layers at Scale precedent)
- Composition guidance: Ha writes, Hc routes, attention reads. NO Hebbian direct readout in the read path.

### Q4 — Failure modes at M -> 64K -> 256K

**Softmax saturation (Scalable-Softmax arxiv/2501.19399):**
- Max attention probability decays as context grows; at M=256K, max(softmax) can be O(1/sqrt(M)) even for the true match
- Mitigation: use log-scaled beta (beta scales with log M) or use SSMax scalable-softmax replacement
- At M=64K, standard softmax likely still recovers with beta~30-50; at M=256K, may need SSMax

**Metastable-state collision (Temperature-Dependent Phase Transition arxiv/2311.18434):**
- At high M with clustered keys, metastable states form that mix multiple stored patterns; attention converges to the metastable mix, not the true target
- Mitigation: high beta separates basins BUT loses gradient (vanishing Jacobian); for pure recall (no training), high beta is safe
- HARD-FAIL signature: recall(c) at beta=8 much lower than at beta=32 → beta needs to scale with M
- HARD-FAIL signature: recall(c) plateaus around 0.5 → mixed-metastable regime

**Key correlation from repeated writes:**
- Substrate Ha writes accumulate cross-terms; later writes are correlated with earlier ones through the shared M_ij matrix
- Feature-correlation reduces α_effective; at M -> 64K, this compounds
- Mitigation: sparse-write (Hc partition + write-locality) or orthogonal-encoder pre-processing on keys

**Bipolar quantization noise on keys:**
- Bipolar keys quantize continuous target to {±1}^N; each key has ~sqrt(N) bits of noise
- For N_c=4096, quantization noise is ~64 bits; at M=64K, ~16-bit key resolution matters and quantization noise dominates
- **This is likely the ultimate scaling wall.** Continuous-valued keys (float32) would push much farther; bipolar substrate-native encoding has structural ceiling

**Rank-ordered failure at M sweeps:**
1. M=8192 (target, 2x N_c): likely OK if key overlap low, beta>=8
2. M=32K (8x): softmax needs beta-scaling
3. M=64K (16x): softmax + correlation both binding; SSMax recommended
4. M=256K (64x): bipolar quantization dominant; requires continuous-valued key path or product-key hierarchical decomposition (Lample 2019 sqrt-M scaling)

### Q5 — Is "replace vs compose" a general M3-cortex-layer discipline?

**Yes — this is a load-bearing M3 architectural principle.** Cross-domain generalization:

**Principle: cortex-layer readouts REPLACE substrate readouts; substrate provides WRITE plasticity + STATE, not read decisions.**

Concrete instances beyond Cell D:
- **Semantic concept learner (5/6 arms chain-grade):** current architecture has a downstream classifier read; per this principle, that classifier should read the substrate STATE (H+C+K tensors), not a substrate-decoded prediction
- **WM multi-bank K=4096:** working-memory readout should be cortex-attention over the bank state, not bipolar-decoded per-bank
- **Refuse-gate V_REL=256:** the gate decision is cortex-side; substrate provides the V_REL comparison state, cortex layer reads it directly rather than composing on top of a substrate-native decision
- **Intent classifier n=100:** classifier reads substrate state directly (transformer-style), not composed on Hebbian-decoded intent
- **Multi-hop depth-15 at 0.808:** the 19.2% remainder gap likely has the same READOUT-REPLACEMENT rescue path — cortex attention over the graph state, not composing over Hebbian graph-decode

**Substrate-side design implication:** substrate must expose STATE (H, C, K, V_REL, banks) as (K, V) tape for cortex attention; substrate does NOT need to ship its own decoded prediction. This is a big simplification of the substrate interface — it produces state, not answers.

**Meta-drill result:** this is Trigger C adjacency-cascade (new adjacency edge: "cortex-side read path IS transformer attention" generalizes across all cortex-layer M3 designs). Should queue a follow-up drill: **"Which substrate mechanisms currently ship read-side decisions vs state?"** — audit likely surfaces 3-5 more READOUT-REPLACEMENT rescue candidates.

**Product-side framing (per [[feedback-no-papers-product-only]]):** M3 = "substrate does memory + write plasticity + state maintenance; cortex above does attention-based read + planning + language". This is the transformer paradigm applied to the substrate; substrate is a differentiable memory tape with structured writes.

## Cross-thread synthesis

**Consistent with prior:**
- `research_5x_drill_cortex_hippo_M8192_rescue_2026-07-01.md` — correctly identified dense-Hopfield as rescue; INCORRECTLY assumed additive composition
- `project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28` — cortex layer above substrate; this drill supplies the READ mechanism (attention) + composition rule (REPLACE)
- `project_M3_cortex_layer_must_inject_stochastic_noise_at_boundary_2026-06-30` — orthogonal: noise-injection is a separate concern at the boundary; READOUT-REPLACEMENT is about the read path structure
- `feedback-substrate-doesnt-know-anything-stop-testing-against-language` — reinforces: substrate provides state, cortex builds meaning by reading state via attention

**Deprecates:**
- The composition-arm design in v1 Cell D (`cortex_hippo_dense_layer_M8192_v1`) — the HA_HC_DENSE arm is refuted; drop from v2
- The 5x-drill's Rank-1 P_deflated=0.45 was for compose variant; REPLACE variant P_deflated=0.42 (similar, but the mechanism is different)

**New adjacency edges surfaced:**
- READOUT-REPLACEMENT as a general M3 discipline (Q5 above)
- Bipolar quantization as the M=64K-256K scaling wall (Q4)
- Product-Key Memory hierarchical decomposition as the M>>64K path (Lample 2019 sqrt-M)

## Substrate-product implications

- **M3 architecture:** Cortex layer = transformer-style attention read over substrate state (K, V tape produced by Hebbian writes). NOT a Hebbian-decoded output feeding cortex.
- **Substrate interface simplification:** substrate exposes (H, C, K, V_REL, banks) as (K, V) memory tape. No per-mechanism decoded output required for cortex consumption. This removes 5+ readout modules from the substrate boundary.
- **Product framing:** "substrate = differentiable memory tape + write plasticity; cortex layer = attention-based read + planning". Clean glass-box interface for M3.
- **Product feature enabled:** if Cell D v2 HARD_PASSes, M3 demo becomes "conversational memory task at M=8192 with cortex-side attention". Aligns cleanly with USER M3 target.
- **Product feature threatened:** if v2 HARD_FAILs (all beta arms), the substrate write side is capping recall — falls back to Product-Key Memory hierarchical decomposition (Cell E) or CLS slow-consolidation (Cell F). BOTH still validate the READ-REPLACE discipline.

## Ranked design table (Cell D v2 + fallbacks)

| Rank | Cell | Mechanism | P_deflated (CG at M=8192) | M3 payoff | Total |
|---|---|---|---|---|---|
| 1 | **D v2 dense-Hopfield READ-REPLACE** | Ha writes; attention reads directly; NO Hebbian read | 0.42 | HIGH (direct M3 fit) | 1.26 |
| 2 | **E Product-Key Memory READ-REPLACE** | Ha writes; PKM sqrt(M) attention read; hierarchical | 0.38 | HIGH (M3 scaling primitive; M>>64K) | 1.14 |
| 3 | **D v2 Hc-gated attention (MoE-style)** | Hc routes to K-partition; attention reads within partition | 0.36 | MEDIUM-HIGH (compatible with substrate Hc) | 0.90 |
| 4 | **F CLS slow-consolidation multi-cycle** | Iterated replay; slow cortex LTP-analog updates | 0.28 | MEDIUM (multi-arc instrument) | 0.56 |

Caps: novel-synthesis P at 0.50 applied (READOUT-REPLACEMENT is a novel substrate integration).

## Next cell to author

**Cell D v2: `cortex_hippo_readout_replacement_M8192_v2`** per Cheap Decisive Test above.
- Substrate anchor: cortex_hippo family; mechanism-class: cortex-side attention read over Hebbian-written (K, V) tape
- Author via `hdi_exp_dev` spawn with smoke-at-full-N discipline
- Include ARM_DENSE_REPLACE_beta_SWEEP at M=8192 preview arm in smoke (fix ade5bb72's missing preview arm — got ERROR "unknown arm: ARM_HA_HC_DENSE_FULL_N_PREVIEW", indicating the switch statement missed that arm name)
- CARDINALITY_OK pre-reg: 5 arms x 3 seeds = 15 units; declare EXPECTED_N_UNITS=15 + HARD_FAIL_CARDINALITY_BREACH if <15 land

**If D v2 HARD_FAILs at M=8192:** author **Cell E: `cortex_hippo_PKM_M8192_v1`** using Product-Key Memory. Falls back to path 2.

**Regardless of D v2 outcome:** queue a follow-up drill on **substrate-mechanism audit for READOUT-REPLACEMENT candidates** (semantic learner, WM banks, refuse-gate, intent classifier, multi-hop) — the meta-principle applies broadly per Q5.

## Citations (verified count: 18)

**New this drill (8):**
1. Lample et al. (2019) — "Large Memory Layers with Product Keys" — NeurIPS 2019 / arxiv/1907.05242.
2. Meta AI (2024) — "Memory Layers at Scale" — arxiv/2412.09764.
3. Ramsauer et al. (2021) — "Hopfield Networks is All You Need" — ICLR 2021.
4. Engram Neural Networks (2025) — "Hebbian Memory-Augmented Recurrent Networks" — arxiv/2507.21474.
5. Reassessment of Hippocampal Index Theory (2024) — Authorea doi 10.22541/au.176442317.74625166.
6. Memory-Augmented Transformers Systematic Review (2025) — arxiv/2508.10824.
7. Provably Optimal Memory Capacity for Modern Hopfield Models (2024) — arxiv/2410.23126.
8. Effects of Feature Correlations on Associative Memory Capacity (2025) — arxiv/2508.01395.

**Reinforced from prior (10):**
9. Krotov, Hopfield (2016) — Dense associative memory — arxiv/1606.01164.
10. Demircigil et al. (2017) — On a model of associative memory with huge storage capacity.
11. Scalable-Softmax Is Superior for Attention (2025) — arxiv/2501.19399.
12. Temperature-Dependent Phase Transition in Modern Hopfield Networks (2024) — arxiv/2311.18434.
13. Sparse Modern Hopfield Model (2024) — arxiv/2309.12673.
14. Hopfield-Fenchel-Young Networks — JMLR 26/24-1961 (2025).
15. Sebastian et al. (2020) — Memory devices and applications — Nature Nanotech.
16. TrueNorth deep-dive — Open Neuromorphic (2024).
17. McClelland, Kumaran, Hassabis (2016) — CLS updated — TICS.
18. Uniform Memory Retrieval with Larger Capacity for Modern Hopfield Models — arxiv/2404.03827.

---

**HEADLINE (repeat):** Cortex-Hopfield as READOUT-REPLACEMENT (not compose) is unanimously supported by cross-domain lit (transformer/Ramsauer, PKM/Lample, hippocampal-indexing, Engram MAM). Cell D v2 = Ha writes + attention reads DIRECTLY; NO Hebbian read composed on top. Recall=1.000 at M=512 smoke should extend to M=8192 with beta>=8 IF key overlap remains bounded (P_deflated 0.42). READ-REPLACE is a general M3 discipline applying to semantic learner, WM banks, refuse-gate, intent classifier, multi-hop.

**P_deflated (top option):** 0.42.

**Next-drill candidate:** substrate-mechanism audit for READOUT-REPLACEMENT candidates across all chain-grade capabilities (Trigger C adjacency-cascade; 24h queue).
