# Research: Phi-3 hidden-state → substrate codeword projection design (PP-8 Phase 2.5 Path 1a)

**Date**: 2026-06-01
**Filed by**: research (Opus synthesis of 4 parallel Sonnet sub-drills)
**Trigger**: PP-8 Phase 2.5 3-point convergence on val=0% (bypass / STE / soft-attention); testbed correctly diagnosed bottleneck as task design (random `key_text → codebook` mapping); Path 1a is principled redesign that derives key codewords from Phi-3 hidden states.
**Parent routing**: `notes/strategy_request_to_strategy_pp8_phase25_task_design_escalation_2026-06-01.md`
**Companion deliverable**: `notes/testbed_pp8_week2_phase25_soft_v1_2026-06-01.md`

---

## (a) HEADLINE

**SimHash-style random Gaussian projection followed by sign() is the recommended Path 1a v1.** Cosine-similarity-preserving (LSH guarantee from Goemans–Williamson 1995 / Charikar 2002), zero training cost, deterministic, drops cleanly into the existing pipeline at ~30 LOC. Calibrated **P(val > random with this projection alone) = 0.32 deflated** (raw P was ~0.50, deflated 0.18 for novel-synthesis penalty since no direct precedent maps "transformer hidden → Kerdock-coset codeword retrieval"). Recommended v1.5 add-on: **learned linear pre-projection (3072 → 4096) then sign() with STE** — calibrated **P=0.42 deflated** when added on top of the SimHash skeleton. P(at least ONE of the v1/v1.5/v2 stack achieves substantive val) = **0.55 deflated, capped at 0.50** per lit-scan calibration penalty.

**The dominant risk is NOT projection method — it is whether the toy task's val→target_token mapping still has random structure that breaks generalization even with semantically-aligned key codewords.** Path 1a only fixes the KEY side (text→codeword). The VAL side (codeword[val_idx] → random target_token) remains semantically arbitrary by construction. So Path 1a v1 must be **paired with a target-token redesign** (1a' below) to actually demonstrate held-out generalization. This is the cheap decisive test.

---

## (b) Cheap decisive test

**Test (~$2-3 H100 + 2-3h eng)**: Path 1c (no-holdout sanity) FIRST establishes baseline, THEN Path 1a v1+1a' on Phi-3-hidden-derived key codewords AND Phi-3-token-decodable val codewords.

**1a v1 mechanics** (recommended for first dispatch):

1. **Build key codebook from Phi-3 hidden states.**
   For each key index `k ∈ {0..M-1}`, generate key text `f"Key {k:04d}: "`, prefill Phi-3, take last-layer hidden state `h_k ∈ R^{3072}` (FP16 → FP32).
2. **Fixed random Gaussian projection R ∈ R^{3072 × 4096}** with entries `N(0, 1/sqrt(3072))`, seeded.
   `code_k = sign(R^T h_k) ∈ {-1, +1}^{4096}`.
3. **Replace `codebook[key_idx]` with these derived codes**. The val codewords stay Kerdock for now (this is the v1 minimal change).
4. **Replace val_to_token random map**: val_idx → target_token uses a semantic anchor — e.g., the **most-likely Phi-3 next-token at the val text**, or a deterministic hash of val text restricted to single-token alphabetic vocab (this is 1a', the val-side fix).
5. **Train**: identical Phase 2.5 soft-attention pipeline. Val eval: 1000 held-out keys.

**HARD-PASS gate**: val top-1 ≥ **3.0%** (≈30× random 0.098%) on held-out keys after same training budget as Phase 2.5 soft. This is the "substrate retains generalization" signal.

**HARD-FAIL gate**: val top-1 < **0.3%** (≈3× random; statistical noise floor on N=1000 val). Confirms the problem is NOT key-side projection but val-side or LLM-side bottleneck. Triggers Path 2 (move to multi-hop Phase 3) or Path 3 (defer).

**MIDDLE-BAND** (0.3% < val < 3.0%): provides signal that projection helps but doesn't close the gap; routes to 1a v1.5 (add learned linear pre-projection W_proj before sign).

---

## (c) Falsifiable predictions

### Prediction P1 (SimHash JL bound; established lit)

Under fixed random Gaussian projection R ∈ R^{d × N} with d=3072, N=4096:
- **Angle preservation**: P(sign(R^T h_a) agrees with sign(R^T h_b) per bit) = `1 − θ(h_a, h_b)/π` (Charikar 2002 / Goemans–Williamson hyperplane rounding).
- **Hamming distance signal**: For two Phi-3 hidden states with cosine similarity 0.5, expected normalized Hamming distance ≈ 0.33; for two unrelated hiddens (cosine ≈ 0), expected Hamming ≈ 0.5.

**HARD-PASS prediction**: training key `f"Key {k:04d}"` and held-out key `f"Key {k+1:04d}"` produce hidden states with cosine similarity in Phi-3 of **≥ 0.4** (consistent number-format prior). Their derived codes have expected Hamming overlap of `≥ 0.61`. Substrate cleanup via dot-product `bipolar_query @ codebook.T` returns the held-out key's codeword in argmax position with probability `≥ 0.10` per a single retrieval (vs. 1/M = 0.0244% random).

**HARD-FAIL prediction**: if Phi-3 hidden states for `f"Key {k:04d}"` across distinct k have pairwise cosine **uniformly > 0.95** (degenerate format-dominated regime), then derived codes all collapse to a small region of bipolar space; cleanup degenerates to random argmax over codebook entries; val accuracy stays at random.

### Prediction P2 (val-side bottleneck; novel)

Path 1a v1 with key-side projection ONLY (val codewords still Kerdock, val→token still random) achieves val top-1 < 1.0% with **P ≥ 0.65 deflated** (the val-token map's random construction breaks generalization regardless of key-side improvements).

**HARD-PASS test**: dispatch v1 with key-only fix; observe val top-1. If > 3.0%, prediction P2 was wrong, both sides matter less than expected. If < 0.5%, P2 confirmed — must add 1a' val-side fix.

### Prediction P3 (1a v2 architectural escalation; calibrated)

Learned linear pre-projection `W_proj ∈ R^{3072 × 4096}` trained jointly with bridge, then sign() with STE, raises P(substantive val) to **0.42 deflated** (~+0.10 over fixed Gaussian). Tradeoff: ~2h additional eng, ~$1-2 additional H100, risk of overfitting to training keys (held-out val could SUFFER if the projection learns key-specific features rather than semantic ones).

**HARD-FAIL gate for v2**: if v2 val < v1 val on held-out keys (overfitting confirmed), revert to v1.

### Prediction P4 (algebraic-structure preservation; established lit)

**Distinguishability**: Phi-3 hidden states for distinct keys produce distinct (Hamming distance > 1900 / 4096 ≈ 0.46) bipolar codes with probability **≥ 0.95** under SimHash, conditional on hidden-state cosine < 0.95. Confirmed by Charikar 2002 LSH theorem.

**Binding closure** (NB: substrate uses W-matrix Hebbian binding, NOT XOR — re-confirmed by reading `experiments/_metric_battery.py:make_substrate`): bipolar codes derived from Phi-3 hidden states are statistically equivalent to random bipolar codes for the purposes of Hebbian outer-product storage W = Σ v_i k_i^T (codes are approximately mean-zero per bit; concentration of measure applies). No closure failure expected.

**Cleanup tolerance**: nearest-codeword argmax retrieval scales as Hamming margin ≈ √N for random bipolar, ≈ N(1−2θ/π) for SimHash-derived codes with controlled angle θ. As long as Phi-3 hiddens have moderate cosine spread (cos ∈ [0.2, 0.9]), cleanup margin stays above thermal noise floor.

---

## (d) Cross-thread synthesis

### Connects to prior research

- **R(2026-06-01 capabilities expansion round 1)** — Free-probability drill produced K_max(α) ≈ log(1/α)/(2√α) for spectral-gap retrieval depth. With derived codes from Phi-3, the effective α (load ratio M/N) doesn't change at first order, but the codeword spectral statistics MIGHT shift (Phi-3-derived codes are not Marchenko-Pastur — they inherit Phi-3 hidden-state's spectral structure). For PP-8 Path 1a sizing, recommend M=4096 keys at N=4096 (α=1; same as existing); do NOT scale aggressively until v1 is validated.
- **R(2026-06-01 round 2 9-drill)** — Per-tenant W gives mathematical zero cross-tenant leakage. Path 1a derived codes do NOT change this property: W is still per-tenant; the codes are just semantically aligned. Confirms Path 1a does not interfere with the substrate's killer-feature roadmap.
- **R(2026-05-21 free-probability seed drill)** — Established Marchenko-Pastur applies to substrate W; this remains valid post-1a because W's structure (Hebbian outer-product of bipolar vectors) is preserved under SimHash-derived codes (codes are still ±1 bipolar, just non-uniform sampling of bipolar space).
- **R(2026-05-27 SKAH-M class confirmation)** — Substrate is SKAH-M (non-reciprocal Hopfield + spatial-correlated DAM + saddle-hierarchy DAM). Derived codes change the "spatial correlation" prior — Phi-3-derived codes have non-trivial pairwise correlation structure that could enhance OR degrade SKAH-M dynamics. v1 dispatch will provide first empirical signal.
- **Bet B 4-stage smoke (2026-05-27)** — Compositional CL evidence at N=1024 (pre-PROT-018). Path 1a does not directly inform Bet B but the val-side fix (using semantic target tokens) is exactly the framing CL benchmarks use; success could open shared infrastructure.

### Lit-precedent (verified)

1. **Goemans–Williamson hyperplane rounding** (1995) — `sign(R^T x)` agreement probability = `1 − θ/π`. The mathematical foundation for SimHash.
2. **Charikar 2002 SimHash** — LSH for cosine similarity via random Gaussian projection + sign. Direct precedent for v1.
3. **Quantized Random Projections / Li et al. NeurIPS 2016** — formal MLE for cosine recovery from b-bit quantized projections; supports v1 with explicit error bounds.
4. **TransHash 2021** (arxiv 2105.01823) — first transformer-based deep hashing. Demonstrates STE + transformer hidden → binary code is trainable end-to-end. Direct precedent for v2 (learned projection variant).
5. **Differentiable Optimized Product Quantization (WWW 2023)** — Gumbel-softmax through codebook assignment. Precedent for v3 alternative.

### Lit-gap (what is novel synthesis)

- **No direct precedent** maps "transformer hidden state → Kerdock-coset codeword for Hebbian heteroassociative retrieval." All deep-hashing lit targets cosine-similarity retrieval (vector search), NOT relation-graph retrieval through a binding matrix. This is why P_deflated penalty applied at 0.18 (deflate to 0.32 for v1, 0.42 for v2). 
- **Kerdock vs random bipolar**: substrate uses Kerdock-4-coset codebook for guaranteed pairwise correlation properties (free-probability load-bearing). v1 REPLACES key codewords with SimHash codes, losing Kerdock structure for keys but preserving it for vals. The mixed-codebook impact on Path D depth=5 retrieval is unstudied — flag for future drill if v1 succeeds.

---

## (e) Substrate-product implications (per [[feedback-no-papers-product-only]])

Per [[feedback-substrate-value-framing-matured-2026-05-26]]: framing is "which killer features does this unblock?" not "is the science novel?"

### Killer features Path 1a unlocks IF v1 hard-passes:

1. **LLM-integrated retrieval as a deployable substrate feature** (killer feature: substrate-as-3rd-memory-type). Without semantically-aligned key codewords, LLM can't drive substrate retrieval naturally. Path 1a v1 is the minimal architectural piece to make this real.
2. **Auditable memory queried by LLM** (killer features: deletion certificate + per-fact retention policy). User-facing flow becomes: "Show me everything you remember about X" → LLM emits text → bridge encodes → substrate retrieves → results returned WITH audit certificate. v1 is the wiring.
3. **Compositionality audit API** (killer feature 2). If LLM can produce key codewords via the hidden-state projection, the composition LLM-produces → substrate-binds → substrate-retrieves becomes the API surface for compositional audit. v1 unblocks this.

### Killer features Path 1a does NOT unlock:

- **Per-tenant W isolation** (already independent of Path 1a — W is per-tenant regardless of codeword construction).
- **Cert-chain replay / disaster recovery** (independent — replay is at W and atom-registry level, not codeword level).
- **Drift detection** (independent).

### Strategic priority

Per [[feedback-substrate-value-framing-matured-2026-05-26]] window analysis: plumbing/SDK is the rate-limiter. Path 1a v1 is **plumbing-level work, not theory** — small implementation, fast iteration. Recommend dispatching v1 in parallel with testbed's Path 1c sanity check. If Path 1c HARD-PASSES (architecture sound), 1a v1 follows immediately with the val-side fix bundled in.

If 1a v1 HARD-FAILS, the strategic implication is: **the toy task abstraction is empirically insufficient for PP-8's claim**, and we should pivot to Phase 3 (multi-hop retrieval) which doesn't need this specific architecture. Cap_map PP-8 stays 0.55-0.65 with the empirical caveat.

If 1a v1 HARD-PASSES (val ≥ 3%), **cap_map PP-8 lifts to 0.60-0.75** and the "LLM-driven substrate retrieval" killer-feature roadmap unblocks for Week 3+ build.

---

## (f) Implementation sketch (~50-100 LOC pseudocode)

Add to `testbed/llm_integration/phase2_toy_dataset_gen.py` and `phase2_qlora_train.py`:

```python
# === Path 1a v1: Phi-3-hidden-derived key codebook + semantic val target ===
# Filed in research_pp8_phi3_hidden_codeword_design_2026-06-01.md
# Add CLI flag --derived-key-codebook + --semantic-val-target

import torch
from transformers import AutoModel

def build_derived_key_codebook(
    key_texts: list[str],
    phi3_model_name: str,
    N: int = 4096,
    seed: int = 17,
    device: torch.device = torch.device("cuda"),
) -> torch.Tensor:
    """Build M x N bipolar codebook from Phi-3 hidden states via SimHash.
    
    Returns: codebook (M, N) in {-1, +1}.
    """
    # 1. Load Phi-3, get d_model = 3072
    model = AutoModel.from_pretrained(phi3_model_name, torch_dtype=torch.float16)
    model.to(device).eval()
    d_model = model.config.hidden_size  # 3072 for Phi-3-mini
    tokenizer = AutoTokenizer.from_pretrained(phi3_model_name)
    
    # 2. Fixed random Gaussian projection R in R^{d_model x N}
    gen = torch.Generator(device=device).manual_seed(seed)
    R = torch.randn(d_model, N, generator=gen, device=device, dtype=torch.float32)
    R = R / (d_model ** 0.5)  # standard JL normalization
    
    # 3. Per key text: prefill, take last-layer hidden state, project, sign
    codes = []
    with torch.no_grad():
        for batch_start in range(0, len(key_texts), 32):
            batch = key_texts[batch_start:batch_start+32]
            tok = tokenizer(batch, return_tensors="pt", padding=True).to(device)
            out = model(**tok, output_hidden_states=True)
            # Take last non-pad token's last-layer hidden
            last_hidden = out.hidden_states[-1]  # (B, T, d_model)
            last_idx = tok.attention_mask.sum(dim=1) - 1  # (B,)
            h = last_hidden[torch.arange(len(batch)), last_idx]  # (B, d_model)
            h = h.float()
            # Project + sign
            proj = h @ R  # (B, N)
            bipolar = torch.sign(proj)
            bipolar[bipolar == 0] = 1.0  # tie-break
            codes.append(bipolar.cpu())
    
    codebook = torch.cat(codes, dim=0)  # (M, N) bipolar
    return codebook.to(device)


def build_semantic_val_target_map(
    val_texts: list[str],
    val_idx_values: list[int],
    phi3_model_name: str,
    pool_size: int = 1024,
    seed: int = 19,
) -> dict[int, int]:
    """val_idx -> target_token via Phi-3 next-token prediction (deterministic).
    
    For each distinct val_idx, take val_text = f"Val {val_idx:04d}: ", prefill,
    pick the most-likely next-token from the alphabetic pool. Replaces the
    random val_to_token map in v1.
    """
    # ... (similar pipeline to above; output deterministic semantic mapping)
    pass


# === Wiring change in phase2_qlora_train.py ===
# Replace:
#   codebook, W, key_idx, val_idx, relation = build_shared(...)
# With:
if args.derived_key_codebook:
    key_texts = [f"Key {k:04d}: " for k in range(M_SUBSTRATE)]
    key_codes = build_derived_key_codebook(key_texts, PHI3_MODEL, N, seed, device)
    # Re-build W with derived key codes (vals stay Kerdock or also derive)
    codebook_keys = key_codes
    codebook_vals, W = build_W_with_mixed_codebook(
        codebook_keys, codebook_vals_kerdock, key_idx, val_idx, relation, seed,
    )
else:
    codebook, W, key_idx, val_idx, relation = build_shared(...)


# === Forward pass (unchanged from Phase 2.5 soft) ===
# soft_query = readout(phi3_last_hidden)
# retrieved = soft_query @ keys_codebook.T -> attn -> attn @ vals_codebook
# bridge(retrieved) -> prefix -> Phi-3 -> CE
# 
# Gradient flow:
#   soft_query <- readout <- phi3_hidden (frozen up to LoRA layers)
#   Now soft_query has gradient signal pulling it toward Phi-3 hidden's
#   own projection space (because keys_codebook is itself sign-projected
#   from Phi-3 hidden states of training keys). This is the alignment
#   that should unlock held-out generalization.
```

**LOC estimate**: ~70 LOC for v1, ~120 LOC for v1.5 (add learned W_proj layer + STE). All within the existing training script structure.

**v2 variant** (learned linear pre-projection with STE):

```python
class LearnedKeyProjection(nn.Module):
    def __init__(self, d_model=3072, N=4096):
        super().__init__()
        self.W_proj = nn.Linear(d_model, N, bias=False)
        # Init from random Gaussian (SimHash starting point)
        nn.init.normal_(self.W_proj.weight, std=1.0 / (d_model ** 0.5))
    
    def forward(self, h):
        # h: (B, d_model)
        proj = self.W_proj(h)  # (B, N) continuous
        # STE: forward sign, backward identity
        bipolar = torch.sign(proj)
        bipolar = proj + (bipolar - proj).detach()  # STE
        return bipolar
```

Joint train: `W_proj` parameters alongside readout + bridge + LoRA. Pre-train W_proj on the 4096 training keys' Phi-3 hidden states to match the fixed SimHash codes as a warm-start, OR random-init and let joint training find the projection.

---

## Recommendation rank

| Rank | Method | P_deflated (substantive val) | Eng cost | Train cost | Notes |
|---|---|---|---|---|---|
| **1** | **SimHash (fixed random Gaussian + sign)** — v1 | **0.32** | ~70 LOC, 2h | ~$2-3 H100 | Direct precedent (Charikar 2002); zero pre-training; preserves angle |
| 2 | **v1 + semantic val target map** — v1' | **0.42** | +20 LOC, 1h | same | Adds val-side semantic anchor; addresses Prediction P2 |
| 3 | Learned linear projection W_proj + STE — v2 | 0.42 | ~120 LOC, 4h | +$1-2 | Direct precedent (TransHash); overfitting risk on held-out |
| 4 | Hadamard/Walsh structured projection — v1-Walsh | 0.28 | ~80 LOC, 3h | same | Same JL guarantee, cheaper compute, less popular in lit |
| 5 | Product Quantization w/ learned codebook | 0.20 | ~200 LOC, 8h | +$3-5 | Differentiable PQ exists but breaks bipolar substrate structure entirely; recommend NOT for v1 |
| 6 | Gumbel-softmax through sign() | 0.18 | ~100 LOC, 5h | +$2-3 | Direct differentiability through discrete; brittleness in published lit |

**Recommended dispatch sequence**:

1. **Path 1c first** (testbed already authorized) — establishes architecture-soundness baseline at ~$1-2.
2. **Path 1a v1 + v1' (combined)** — single dispatch with both key-side SimHash AND semantic val target. Expected cost: **~$2-3 H100 + 3h eng + 1 dataset regen**. Joint test of two interventions.
3. **If v1/v1' HARD-PASSES**: cap_map PP-8 lifts; move to Week 3+ with this architecture as foundation.
4. **If v1/v1' MIDDLE**: escalate to v2 (learned projection); single additional dispatch ~$2 + 4h eng.
5. **If v1/v1' HARD-FAILS**: PP-8 toy task is empirically inadequate; pivot to Phase 3 (multi-hop) or Path 3 (defer).

---

## (f) Citations (verified count: 6)

1. Charikar, M. (2002). "Similarity Estimation Techniques from Rounding Algorithms." STOC. (SimHash foundational)
2. Goemans, M. & Williamson, D. (1995). "Improved Approximation Algorithms for Maximum Cut and Satisfiability Problems Using Semidefinite Programming." J. ACM. (hyperplane rounding angle bound)
3. Li, P., Mitzenmacher, M., & Slawski, M. (2016). "Quantized Random Projections and Non-Linear Estimation of Cosine Similarity." NeurIPS. arxiv 1610.06978
4. Chen, Y. et al. (2021). "TransHash: Transformer-based Hamming Hashing for Efficient Image Retrieval." arxiv 2105.01823
5. Wang, Z. et al. (2023). "Differentiable Optimized Product Quantization and Beyond." WWW.
6. Kanerva, P. (2009). "Hyperdimensional Computing: An Introduction to Computing in Distributed Representation with High-Dimensional Random Vectors." Cognitive Computation. (VSA / HDC foundation; XOR/multiplication binding)

Lit-scan also touched: Deep Class-Wise Hashing (Zhe et al. 2018); LARS-VSA (arxiv 2405.14436); HDC survey (arxiv 2111.06077); Codebook-softened PQ (Klein & Wolf 2022). These provide context but are not direct precedent.

---

## Calibration notes (per [[feedback-lit-scan-calibration-penalty]])

- Raw P for SimHash v1: ~0.50 (well-established LSH math; high confidence on angle preservation).
- Deflation: −0.18 because (i) no published precedent for "transformer hidden → Kerdock-mixed substrate → relation-graph retrieval via Hebbian W", (ii) Phi-3 hidden states for "Key 0001" vs "Key 0002" may have undesirable degeneracy (format token dominance), (iii) val-side mapping interaction with projection-derived keys is unstudied.
- Final P_deflated for v1: **0.32**. With v1' (semantic val) added: **0.42**.
- Hard-pass / hard-fail thresholds pre-registered above per [[feedback-envelope-expansion-fail-bands]].

Novel-synthesis cap: 0.50 per policy. P=0.42 is below cap. No further capping needed.

---

## Sub-drill provenance

- Sub-drill 1 (WebSearch): JL random projection + sign quantization angle preservation. Yielded Charikar 2002 + Li et al. NeurIPS 2016 MLE bound. **YIELD: HIGH (direct precedent for v1)**.
- Sub-drill 2 (WebSearch): Learning-to-hash transformer hidden states + STE deep hashing. Yielded TransHash 2021 + Deep Class-Wise Hashing 2018. **YIELD: MEDIUM (direct precedent for v2 but image-retrieval setting differs from substrate-retrieval setting)**.
- Sub-drill 3 (WebSearch): PQ codes language model embeddings learned codebook differentiable. Yielded Differentiable PQ WWW 2023 + Hyperbolic PQ. **YIELD: LOW for v1 path (PQ breaks bipolar substrate); MEDIUM as alternative if v1/v2 fail**.
- Sub-drill 4 (WebSearch): VSA / HDC bipolar codeword derived from neural network embedding. Yielded Kanerva 2009 + LARS-VSA + HDC survey. **YIELD: HIGH (confirms binding closure under derived bipolar; no XOR mismatch since substrate uses W matrix not XOR)**.

---

## Closing

Substrate-side audit confirmed: codebook is Kerdock-4-coset (NOT random bipolar); binding is W matrix Hebbian (NOT XOR); cleanup is dot-product argmax. Path 1a v1 (SimHash key codebook) is compatible with this algebra — keys move from Kerdock space to random-Gaussian-sign space, but Hebbian outer-product and dot-product cleanup work identically on any bipolar code. The risk is loss of Kerdock pairwise-correlation guarantee on keys; mixed-codebook (keys derived, vals Kerdock) interaction is unstudied and worth a follow-up drill if v1 succeeds.

**Recommendation to strategy**: Dispatch testbed Path 1c first (already authorized), then Path 1a v1+v1' as a single 3h eng + ~$2-3 H100 task. Pre-committed cap_map decisions: HARD-PASS lifts PP-8 to 0.60-0.75; HARD-FAIL keeps 0.55-0.65 with empirical caveat + routes to Phase 3 or defer.


---

Acted-on 2026-06-01: superseded by v1+v1 bundle authorization + Round 4 D1-1 frozen-random control results


Acted-on 2026-06-01: superseded by Round 4 D1-1 frozen-random control proving M1-dominance
