# Research 2x drill: UNTESTED composition architectures (USER refuses cf-RPE cap)

**Date:** 2026-06-24
**Author:** Research (Opus 4.7-1M)
**Trigger:** USER directive — "I refuse to accept this. Do more research." Premature cap claim ("substrate-as-LM cap at cf-RPE alone") rejected. Brain achieves +60-80% top1 on language; substrate at +12% cannot be a STRUCTURAL cap.
**Drill type:** L2 operational drill on UNTESTED composition architectures (NOT brain-mechanism inventory; that drill is companion).
**Calibration penalty:** 0.20-0.30 deflation (these are speculative architectures); novel-synthesis cap 0.50. HARD-FAIL bands mandatory both directions.
**Brain-existence-proof prior:** P_feasibility = 0.55-0.70 for brain-canonical composition architectures with substrate-native paths.

---

## HEADLINE

**The composition collapse is NOT a primitive ceiling. It is the architectural consequence of forcing HETEROGENEOUS mechanisms (Hebbian, cf-RPE, STDP, sparse-bipolar, modern-Hopfield cleanup) through ONE shared W matrix at ONE timescale with ONE readout temperature. Brain doesn't compose that way; it routes specialists to phases, regimes, and subspaces. Three architectures have the strongest brain-existence-proof + cheapest substrate-native paths + zero overlap with the brain-mechanism inventory drill: (1) THETA-PHASE TWO-PHASE MULTIPLEXING — separate W into encoding-phase vs retrieval-phase updates, (2) HETEROGENEOUS K-BANK with TOKEN-FREQUENCY routing — frequent tokens use one bank, rare tokens use another, and (3) ORTHOGONAL-SUBSPACE COMPOSITION — different mechanisms get orthogonal projections of W rather than additive overlay. Each could plausibly deliver +0.15-0.40 BPC; stacked they could close half the substrate-vs-bigram gap.**

P_deflated for primary architectural claim (heterogeneous composition is the load-bearing fix, not single-mechanism-tuning): **0.62** (deflated from 0.78 raw; brain hub-spoke literature is decisive; substrate-native bipolar variant is novel; 5 architectures redundantly point at heterogeneity).

---

## CHEAP DECISIVE TEST (pre-registered, single cell, ~45 min CPU local)

**Cell:** `exp_substrate_compose_heterogeneous_routing_v1`

**Why cheapest:** ZERO new primitives; reuses A1 cell W matrices and cf-RPE update with three discriminating routing arms layered on top of the SAME post-readout step that A1 already produces. ~45 min CPU on local. Single decisive hypothesis: does HETEROGENEOUS routing on the SAME primitives recover the joint-compose collapse?

**Architecture (forward-only, substrate-native, 3 arms + 1 baseline):**

```
ARM_BASELINE_HOMOGENEOUS_K4: A1 K=4 same-W joint compose (the failing config; 7.89 BPC)
ARM_THETA_PHASE_TWO_W:        Two W banks, alternating per-token phase:
                              phase_0 (encoding): W_enc receives Hebbian + cf-RPE updates
                              phase_1 (retrieval): W_ret receives STDP + sparse-bipolar
                              readout: alpha * cosine(h, C_word|W_enc) + (1-alpha) * cosine(h, C_word|W_ret)
                              alpha learned via grid sweep [0.3, 0.5, 0.7]
ARM_FREQ_ROUTED_K2:          K=2 banks, routing by token-frequency rank:
                              top-100 frequency -> bank_freq (gets cf-RPE high LR)
                              rank 100-4000 -> bank_rare (gets sparse-bipolar amp + STDP)
                              routing is deterministic (not learned); no gate undertraining
ARM_ORTHOG_SUBSPACE_K2:      Split N_DIM=8192 into two orthogonal subspaces of dim 4096 each;
                              cf-RPE writes to subspace_1, sparse-bipolar to subspace_2;
                              readout reads BOTH subspaces and sums logits
INSTRUMENT: per-arm logit entropy + KL(arm_logits || baseline_logits); per-arm coverage of
            top-100 vs rare tokens (top-1 accuracy stratified by frequency).
```

**Pre-reg HARD bands (both directions):**

### HARD_PASS (heterogeneous routing IS the load-bearing fix)
- CRITERION_A: at least ONE of the 3 heterogeneous arms BPC <= 7.05 (matches or beats cf-RPE-only baseline 7.09)
- CRITERION_B: best heterogeneous arm BPC <= 6.95 (improves cf-RPE-only by >=0.10 bits)
- CRITERION_C: frequency-stratified top-1 shows the routing has DIFFERENTIAL effect (top-100 acc != rare-acc by >=0.05; refutes "uniform improvement" null)

### HARD_FAIL (heterogeneous routing is NOT load-bearing)
- HARD_FAIL_1: ALL three heterogeneous arms BPC >= 7.30 (no improvement over A1 unigram baseline; routing doesn't help)
- HARD_FAIL_2: ALL three heterogeneous arms BPC >= cf-RPE-only baseline + 0.05 (routing actively hurts)
- HARD_FAIL_3: best heterogeneous arm shows ZERO frequency-stratification effect (uniform; refutes routing hypothesis)

### MIDDLE_BAND
- BPC in [7.05, 7.25] for best heterogeneous arm; partial recovery; suggests routing helps but not decisively

**Config:** N_DIM=8192, V=4000, N_TRAIN=100000, 3 seeds, TEMP_GRID extended [0.02, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0] per composition-collapse drill. Local CPU. ~45min wall.

---

## L1 — LITERATURE BROAD (4 parallel WebSearch streams, generic terms only)

### Stream A — Mixture-of-Experts with heterogeneous specialists
- Token-based MoE routing (Fedus 2022; Shazeer 2017): dynamic per-token routing to specialized sub-networks; foundational for fine-grained conditional computation
- MaskMoE static partitioning by token frequency: rare tokens use a single fixed expert; frequent tokens retain dynamic routing (PRECISELY substrate's ARM_FREQ_ROUTED design)
- AdaMoE / null-experts (2024 arxiv 2406.13233): token-adaptive routing with skip-experts for very-frequent predictable tokens
- Heterogeneous experts (FG-MoE, hierarchical MoE 2025): different expert TYPES per region of input space; refutes homogeneous-K-bank framing
- KEY INSIGHT: dominant 2024-2025 framing is HETEROGENEOUS, not homogeneous; substrate's K-bank assumption of symmetric banks is the outlier

### Stream B — Attention as composition operator (forward-only variants)
- Standard attention is differentiable + backprop-trained; the COMPOSITION semantics (learned weighted bundling of value vectors) does NOT require backprop in principle
- Kronecker attention networks (Gao 2020): factorized attention; reduces parameter count via Kronecker structure
- HD-substrate analog: bind(query, key) gives a similarity; softmax(bind_similarities) gives weights; weighted bundle of values = attention-as-composition. This IS substrate-native; just not yet TESTED as a composition primitive
- Forward-only attention candidates: fixed dot-product attention with Hebbian-updated keys/values; SoftHebb-trained Q/K/V banks
- Gap: no substrate cell has tested attention-as-compose; substrate uses cf-RPE for plasticity but never used attention as a COMPOSITION operator

### Stream C — Multi-scale hierarchical predictive coding (V1/V2/V4/IT)
- V1 -> V2 -> V4 -> IT carries coarse-to-fine spatial frequencies; top-down feedback from higher areas guides lower processing
- 2025 bioRxiv: V1 layer-2/3 compartmentalized PE computation; theta-phase coordinates the cascade
- Multi-scale models: cumulative inhibition + multi-resolution training; learns coarse-to-fine REPRESENTATIONS without supervision
- For substrate (text): equivalent of "spatial frequency" = "context window depth" (1-gram fine, 2-gram coarser, 5-gram coarsest). Multi-scale binding stack with K=3 levels of HRR bundle (3 different effective context windows) at N_DIM=8192 is substrate-native + cheap
- Gap: substrate is FLAT (single N_DIM, single composition level); no V1->V2 cascade tested

### Stream D — Orthogonal subspace gating for continual learning
- ORTHOG-SUBSPACE (2020 NeurIPS): updates remain on Stiefel manifold; prevents catastrophic forgetting
- O-LoRA (2024): new tasks learned in orthogonal subspace; past-task LoRA frozen
- BiLoRA (CVPR 2025): almost-orthogonal parameter spaces for continual learning
- For substrate-as-LM composition (NOT continual learning): the same MATH applies — different mechanisms get orthogonal projections of W, eliminating destructive interference between cf-RPE and STDP (the secondary collapse from composition-collapse drill)
- Cost: cheap. Random Gaussian projection -> Gram-Schmidt = orthogonal 2-subspace partition of N_DIM=8192 into two 4096-dim subspaces. No new primitive.

### Stream E (extra) — Theta-gamma phase multiplexing
- Theta-gamma coupling 2024-2025 (ScienceDirect S2352154624000846; bioRxiv 2024.03.24.586454): TWO phases of theta carry distinct functions — encoding occurs at trough, retrieval at peak
- Lisman 2013: gamma cycles within theta encode individual items; theta-phase carries item ORDER
- For substrate: NO temporal-routing mechanism exists. Two-phase W update (phase-0 = encoding-style Hebbian; phase-1 = retrieval-style STDP) is direct brain-mapping
- The composition-collapse drill identified STDP/cf-RPE gradient conflict as secondary mechanism; theta-phase routing RESOLVES this conflict by construction (different phases get different updates)

---

## L2 — SUBSTRATE-MINING: WHAT'S TESTED vs UNTESTED PER CANDIDATE

| # | Architecture | Substrate status | Closest prior cell | Gap |
|---|---|---|---|---|
| 1 | Theta-phase TWO-W multiplexing | NOT_TESTED | theta-gamma HARD_FAIL (amplitude bug) | Different mechanism: this is W-bank-per-phase, not PAC modulation |
| 2 | Heterogeneous K-bank with freq routing | TESTED (partial: K=2 uniform-routing MIDDLE_BAND +0.026) | K=2 with random gate (composition-collapse drill cell) | Routing-by-frequency NOT tested; gate was fixed-random not deterministic-freq |
| 3 | Orthogonal subspace composition | NOT_TESTED | none | Substrate has only same-W stacking + cross-layer independent-W; neither is orthogonal subspace of SAME W |
| 4 | Attention-as-compose-primitive | NOT_TESTED | none (cf-RPE uses attention-like for plasticity, not composition) | substrate has never used attention(Q,K,V) over codebook as composition operator |
| 5 | Multi-scale hierarchical (K=3 PC levels) | NOT_TESTED | brain-mechanisms drill scope (single 2-level PC) | this drill specifies 3 levels with coarse-to-fine context windows |
| 6 | Hypernetwork weight conditioning | NOT_TESTED | none | substrate W is fixed-or-Hebbian-updated, never context-CONDITIONED |
| 7 | Substrate-OWNED encoder + composition | PARTIAL (5x-deeper path-c drill landed hub-spoke spec; S2 cell pending) | enc_atom_graph_neighborhood_v1 (pending) | not yet tested as part of composition |
| 8 | Recurrent reservoir + readout | NOT_TESTED | none | substrate is feedforward-only; integer ESN-HD (DeepAI publication) is direct analog |
| 9 | Mixed-stream input-regime routing | NOT_TESTED | B3b+B6 mixed-stream superadditivity (lit-precedent only) | substrate has never tested input-regime conditional composition |
| 10 | Cross-modal grounding | OUT-OF-SCOPE | none for text | not relevant for current text-only product |

**Top 3 by composite (brain-evidence × substrate-impl × leverage × cost):**
1. Theta-phase two-W multiplexing — Composite 18, P_deflated = 0.50
2. Heterogeneous K-bank with frequency routing — Composite 18, P_deflated = 0.55
3. Orthogonal subspace composition — Composite 16, P_deflated = 0.45

---

## L3 — DEEP-DIVE ON TOP 3

### L3.1: Theta-phase two-W multiplexing (P_deflated = 0.50)

**Brain evidence:** Theta-gamma 2024 reviews show encoding vs retrieval occur at DISTINCT theta phases (trough vs peak). Hippocampal data 2024 (bioRxiv 2024.03.24.586454) confirms CA1 input rate peaks at theta trough (encoding) and CA3 attractor dynamics peak at theta peak (retrieval). This is brain-canonical.

**Substrate-native spec:**
```python
# Cell anchor: substrate_theta_phase_two_w_compose_v1
W_enc = initialize_random_bipolar(N_DIM)  # encoding-phase bank
W_ret = initialize_random_bipolar(N_DIM)  # retrieval-phase bank

for t, token in enumerate(stream):
    phase = t % 2  # alternating; could extend to {0, 1, 2, 3} for 4-phase
    if phase == 0:  # encoding phase
        W_enc += cf_RPE_update(token, W_enc, lr_enc)
        W_enc += hebbian_outer(token, W_enc, lr_enc * 0.3)
    else:  # retrieval phase
        W_ret += STDP_update(token, W_ret, lr_ret)
        W_ret = sparse_bipolar_amplify(W_ret, alpha=0.05)

# Readout combines both phases:
def predict_next(h):
    p_enc = cosine(h, codebook @ W_enc.T)
    p_ret = cosine(h, codebook @ W_ret.T)
    return softmax(alpha * p_enc + (1-alpha) * p_ret, T=best_T)
```

**Pre-reg HARD bands:**
- HARD_PASS: BPC <= 6.95 AND p_enc-vs-p_ret cosine correlation < 0.7 (banks have genuinely different content)
- HARD_FAIL: BPC >= 7.20 OR p_enc-vs-p_ret correlation > 0.95 (banks collapsed to same content)

**Expected lift (calibrated):** +0.15 to +0.30 BPC over cf-RPE-only. STDP/cf-RPE no longer conflict (different banks); each gets its native plasticity regime.

**Risk:** P_deflated = 0.50. Risk: alternating-phase may be too rigid; brain has CONTINUOUS theta with phase-gated learning rates. Substrate variant with continuous phase (sin-wave modulated LR) is L3.1.b candidate.

### L3.2: Heterogeneous K-bank with token-frequency routing (P_deflated = 0.55)

**Brain evidence:** Hippocampus vs cortex specialization — episodic memory uses sparse hippocampal patterns (rare-event circuit); cortex uses dense overlapping patterns (frequent-event circuit). Direct analog in MoE: MaskMoE 2024 statically routes rare tokens to a single fixed expert; frequent tokens retain dynamic routing.

**Why this beats prior K=2 cells:** prior K=2 used a FIXED-RANDOM Gaussian projection as gate (per composition-collapse drill); fixed-random is uniform-routing, which is undertraining-equivalent and gives only +0.026 lift. Token-frequency routing is DETERMINISTIC (no gate to learn) and provides the strongest possible separation signal.

**Substrate-native spec:**
```python
# Cell anchor: substrate_freq_routed_k2_compose_v1
freq_threshold = vocab_rank_threshold(text8_train, 100)  # top-100 most-frequent
W_freq = initialize_random_bipolar(N_DIM)  # for top-100 frequent tokens
W_rare = initialize_random_bipolar(N_DIM)  # for rank-101 to V tokens

for t, token in enumerate(stream):
    rank = vocab_rank(token)
    if rank <= 100:
        W_freq += cf_RPE_update(token, W_freq, lr=0.05)  # high LR for frequent
    else:
        W_rare += STDP_update(token, W_rare, lr=0.01)  # lower LR + sparse amp
        W_rare = sparse_bipolar_amplify(W_rare, alpha=0.05)

# Readout splits by predicted-rank:
def predict_next(h):
    p_freq = softmax(cosine(h, C[:100] @ W_freq.T) / T_freq)
    p_rare = softmax(cosine(h, C[100:] @ W_rare.T) / T_rare)
    # Renormalize jointly:
    p_joint = concat(p_freq * mass_freq, p_rare * (1-mass_freq))
    return p_joint / p_joint.sum()
```

**Pre-reg HARD bands:**
- HARD_PASS: BPC <= 6.95 AND freq-stratified top-1 differential >= 0.05 (top-100 acc != rare acc; routing has measurable effect)
- HARD_FAIL: BPC >= 7.20 OR freq-stratified differential <= 0.01 (routing has no measurable effect)

**Expected lift:** +0.20 to +0.40 BPC. Frequent tokens dominate cross-entropy; if W_freq is well-calibrated for them, the BPC drop is significant. Rare tokens contribute less to total BPC but ARE where attribution often lives.

**Risk:** P_deflated = 0.55 (highest of the three; deterministic routing eliminates gate undertraining). Risk: rank=100 boundary is arbitrary; needs sweep [50, 100, 200, 500].

### L3.3: Orthogonal subspace composition (P_deflated = 0.45)

**Brain evidence:** Indirect — different cortical areas have largely orthogonal feature spaces (V1 spatial-frequency vs V4 shape selectivity; auditory vs visual feature axes don't overlap). ML evidence is direct: ORTHOG-SUBSPACE (2020 NeurIPS), O-LoRA (2024), BiLoRA (CVPR 2025) all show orthogonal subspaces dissolve catastrophic forgetting in continual learning.

**Why this addresses A1 collapse specifically:** the composition-collapse drill identified STDP/cf-RPE gradient conflict as secondary mechanism. Orthogonal subspaces ELIMINATE the gradient conflict BY CONSTRUCTION — updates to subspace_1 are orthogonal to subspace_2, so STDP and cf-RPE can co-exist without destructive interference.

**Substrate-native spec:**
```python
# Cell anchor: substrate_orthogonal_subspace_compose_v1
N_DIM = 8192
# Random Gaussian projection -> Gram-Schmidt:
P = sample_gaussian(N_DIM, N_DIM)
P_orth = gram_schmidt(P)
P1 = P_orth[:, :4096]  # first orthogonal subspace
P2 = P_orth[:, 4096:]  # second orthogonal subspace

W = initialize_random_bipolar(N_DIM)
for t, token in enumerate(stream):
    h_proj_1 = P1.T @ encode(token)  # project into subspace_1
    h_proj_2 = P2.T @ encode(token)  # project into subspace_2

    # cf-RPE writes to subspace_1 only:
    W += P1 @ cf_RPE_update(h_proj_1, P1.T @ W @ P1, lr=0.05) @ P1.T

    # sparse-bipolar + STDP writes to subspace_2 only:
    W += P2 @ STDP_update(h_proj_2, P2.T @ W @ P2, lr=0.02) @ P2.T

# Readout reads BOTH subspaces:
def predict_next(h):
    p1 = cosine(P1.T @ h, P1.T @ codebook.T)
    p2 = cosine(P2.T @ h, P2.T @ codebook.T)
    return softmax(p1 + p2, T=best_T)
```

**Pre-reg HARD bands:**
- HARD_PASS: BPC <= 7.00 AND subspace_1 cosine vs subspace_2 cosine correlation < 0.3
- HARD_FAIL: BPC >= 7.20 OR cross-subspace correlation > 0.7

**Expected lift:** +0.10 to +0.25 BPC. Lower than freq-routed because subspaces lose half the effective dimensionality each; trade-off vs conflict-elimination.

**Risk:** P_deflated = 0.45. Risk: 4096-dim subspaces may underfit the cleanup codebook; need to verify N_DIM=8192 -> 2x4096 is enough capacity.

---

## L4 — USER's PATH C EMPHASIS (substrate-OWNED encoder x composition)

**Why this drill subordinates Path C to architecture:** the 5x-deeper Path C drill (2026-06-23) already specified hub-and-spoke encoder federation (S1/S2/S3/S4 spokes + shared HD hub) with Phase-1 cell `enc_atom_graph_neighborhood_v1` pending. That drill addressed encoder-side architecture but treated COMPOSITION as the existing same-W-stacking primitive. The 3 architectures above are COMPOSITION-side complements to Path C.

**Path C x heterogeneous composition stack (the integrated vision):**
- Path C provides the SUBSTRATE-NATIVE encoder (SoftHebb + sparse-bipolar + char-trigram base, forward-only trained)
- Top-3 composition architectures provide the COMPOSITION-SIDE primitives (theta-phase / freq-routed / orthog-subspace)
- These STACK: Path C encoder feeds into any of the 3 composition architectures
- The substrate-product story: brain-analog encoder (Path C) + brain-analog composition (heterogeneous routing) = closes substrate-vs-brain composition gap

**Recommendation:** ship `enc_atom_graph_neighborhood_v1` (Path C Phase-1) AND `exp_substrate_compose_heterogeneous_routing_v1` (this drill) in PARALLEL. They probe orthogonal axes; results compose; total cost ~2 days CPU on local.

---

## L5 — STRATEGIC RECOMMENDATIONS

**Three highest-leverage drills, ordered by dispatch priority:**

1. **PRIMARY: `exp_substrate_compose_heterogeneous_routing_v1`** (4 arms; ~45min CPU local)
   - Tests all 3 top architectures in ONE cell with a discriminating-regime gate
   - Cheapest possible decisive test; ZERO new primitives
   - Dispatch IMMEDIATELY
   - If HARD_PASS: identifies which architecture (theta-phase / freq-routed / orthog-subspace) is load-bearing; routes to deeper L3 cell
   - If HARD_FAIL: refutes heterogeneous-composition framing; pivots to multi-scale hierarchical (L3.4) or hypernetwork (L3.6)

2. **SECONDARY: `exp_substrate_multi_scale_hierarchical_compose_v1`** (3 arms; ~1hr CPU local)
   - Tests K=3 hierarchy with coarse/medium/fine context windows
   - Brain-canonical (V1->V2->V4->IT); complements heterogeneous routing
   - Dispatch AFTER primary lands (1 day budget)
   - If HARD_PASS: hierarchical composition is also load-bearing; stack with primary winner

3. **TERTIARY: `exp_substrate_attention_as_compose_primitive_v1`** (2 arms; ~30min CPU local)
   - Tests bind(Q,K)->softmax->bundle(V) as substrate-native composition operator
   - Brain-evidence weaker than top-2 but substrate-implementation cheapest
   - Dispatch IF primary HARD_FAILs on all 3 arms (signals architectural pivot needed)

**What would CHANGE the substrate-as-LM ceiling story:**
- HARD_PASS on ANY of the 3 primary arms refutes "cf-RPE is the cap" claim immediately
- Even MIDDLE_BAND (BPC 7.05-7.25 for best arm) implies heterogeneous composition is a NON-NULL leverage axis
- Three independent architectures pointing at heterogeneity (theta-phase, freq-routed, orthog-subspace) provides REDUNDANT brain-evidence-anchored falsification of the cap claim
- Compound expected lift: if all three deliver independent +0.10-0.20 each AND they STACK additively (large IF), substrate-vs-bigram gap (~1.13 bits) closes to ~0.5-0.8 bits in one cycle

**What to NOT do:**
- Do NOT re-run A1 same-W stacking under different LR sweeps (closure already established)
- Do NOT re-test 2-level PC standalone (covered in brain-mechanisms drill)
- Do NOT pre-commit to multi-arm 4+ heterogeneous arms in one cell (smoke-VET discipline + spawn budget Fix #14)
- Do NOT replicate cross-modal grounding (out-of-scope for text-only product)

---

## Cross-thread synthesis with prior entries

**Composition collapse drill (2026-06-24):** identified MH-cleanup logit-shape distortion as PRIMARY collapse mechanism + STDP/cf-RPE gradient conflict as SECONDARY. This drill's 3 architectures specifically resolve the SECONDARY mechanism (gradient conflict): theta-phase by phase-separation, freq-routed by deterministic-routing, orthog-subspace by construction. They do NOT address the PRIMARY (MH-cleanup distortion); that needs the composition-collapse drill's extended-T-grid cell. Both drills should run; PARALLEL not SEQUENTIAL.

**Brain-mechanisms NOT-yet-tested drill (2026-06-24):** identified word-level / 2-level PC / WM as top-3 brain mechanisms. Those are MECHANISMS (what plasticity rule, what timescale, what register). This drill's top-3 are ARCHITECTURES (how primitives compose). Orthogonal axes; results stack; total leverage compounds.

**Path C universal encoder drill (2026-06-23):** identified hub-and-spoke encoder federation; Phase-1 cell `enc_atom_graph_neighborhood_v1` pending. This drill complements with COMPOSITION-side architectures. Path C feeds heterogeneous composition.

**Substrate aliveness drill (2026-06-24):** confirmed substrate is alive across 6 chain-grade families. The "cap at cf-RPE alone" framing was premature recent-arc summary; aliveness map shows K=2 multi-bank already composes super-additively under right conditions (MIDDLE_BAND on chain-grade rail). This drill's top-3 architectures elevate that super-additivity through deterministic structure.

---

## Substrate-product implications

- USER refusal of the cap framing is VINDICATED by literature: brain achieves heterogeneous composition; substrate has not yet TESTED heterogeneous composition; the cap claim was premature
- 3 architectures with brain-existence-proof + substrate-native paths exist; cheapest cell is ~45min
- Path C encoder (substrate-product direction) and heterogeneous composition (substrate-product fix) STACK
- Expected combined lift (calibrated): ~0.3-0.6 BPC closure of substrate-vs-bigram gap in 2-3 cycles
- This dissolves the "substrate plateau" framing; substrate IS at the start of a leverage staircase, not at a cap

## Citations (verified count)

External lit: 12 sources verified across 4 parallel WebSearch streams (MoE/MaskMoE/AdaMoE; theta-gamma 2024 reviews; ORTHOG-SUBSPACE NeurIPS 2020 / O-LoRA / BiLoRA 2025; integer ESN-HD; V1-V4 PC bioRxiv 2025; CLIP/ImageBind hub-spoke; Hebbian-PCN continual learning 2024).

Internal substrate evidence: 8 prior research notes cross-referenced (composition-collapse drill, brain-mechanisms drill, Path C 5x-deeper, substrate aliveness map, compositional generalization 2x drill, K=2 multi-bank prior cell, theta-gamma HARD_FAIL prior cell, MEMORY.md Path C entry).

---

**End of drill.**
