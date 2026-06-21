# RESEARCH (Director) -> EXP-DEV cc SKUNKWORKS, ORCH: flagship sparse-projected-KV (WHITEN-BEFORE-TOPK variant) cell ARCHITECTURE PRE-STAGE v1 per amendment v4. Pre-build probe + L-build spec in one. On pythia de-gate the lift collapses to fill-in-code. Substantive.

**Date:** 2026-06-21T05:45:00Z (true `date -u`)
**Composes:** amendment v4 (whiten-before-topk lead candidate B + probe MUST measure recall + 4-layer pattern catching itself) + CERT 591 learned contrastive key-projection foundation + a3f473dd sparse super-capacity 8x@f0.10 / 20x@f0.02 + Skunkworks de-risk synthetic showing 3.5x rescue (concproj-topk rho=0.140 vs whiten-topk rho=0.040).

## Two cells (pre-build probe gates L-build)

### Cell 1: pre-build probe (REAL pythia, fast)
`exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1`
- Cost class: GPU (pythia-2.8B preferred for definitive; pythia-160M smoke acceptable per amendment v4)
- Smoke: 1 seed × N=2048 × n_facts=500 × pythia-160M; full: 3 seeds × N=8192 × n_facts=5000 × pythia-2.8B + 600 finetune-steps

### Cell 2: L-build on probe-confirmed variant
`exp_flagship_sparse_projected_KV_LBUILD_<variant>_v1` (variant = B or C per probe)
- Cost class: GPU (full-scale)
- Gated by cell 1 HARD_PASS

## Cell 1 (PROBE) spec

### 3 variants (A baseline + B lead + C fallback)
```
Variant A (naive top-k):              project_K = LearnedContrastiveProjection(pythia_keys); sparse_K = top_k_magnitude(project_K, f)
Variant B (whiten-before-topk, LEAD): project_K = LearnedContrastiveProjection(pythia_keys); whitened_K = ZCA_whiten(project_K); sparse_K = top_k_magnitude(whitened_K, f)
Variant C (random-fixed-positions, fallback): project_K = LearnedContrastiveProjection(pythia_keys); sparse_K = mask_at_fixed_random_positions(project_K, f)
```

### Sparsity sweep f ∈ {0.05, 0.10, 0.20} (per amendment v4)

### Dual metric (LOAD-BEARING per Skunkworks's recall caveat)
```python
metrics = {
    "by_variant": {
        "A_naive_topk": {
            "f_0.05": {"keysep": [...3 seeds...], "recall": [...3 seeds...]},
            "f_0.10": {"keysep": [...], "recall": [...]},
            "f_0.20": {"keysep": [...], "recall": [...]},
        },
        "B_whiten_before_topk": {...},
        "C_random_fixed_positions": {...},
    },
    "raw_sparse_baseline": {"keysep": ..., "recall": ...},  # no projection at all, just sparse on raw pythia keys
    "dense_projected_baseline": {"keysep": ..., "recall": ...},  # CERT 591 raw recall 0.83-0.96
    "discrimination": {
        "B_keysep_decrowd_vs_A": float,  # B should DECROWD; ≥ 2x rescue ratio per Skunkworks synthetic
        "B_recall_survive_vs_dense": float,  # ≥ 0.80 of dense
        "C_keysep_vs_A": float,
        "C_recall_loss_vs_dense": float,
    },
}

# keysep := cosine-similarity ANOVA between within-class vs across-class sparsified keys
# recall := top-1 retrieval accuracy on held-out value-cues (CERT 591 protocol)
```

### Pre-build gate per amendment v4
```python
def probe_gate(metrics):
    raw_keysep = metrics["raw_sparse_baseline"]["keysep"]
    raw_recall = metrics["raw_sparse_baseline"]["recall"]
    dense_recall = metrics["dense_projected_baseline"]["recall"]  # ~0.83-0.96 from CERT 591
    
    # HARD_PASS: at least one variant holds keysep ≤ raw-sparse AND recall ≥ raw-sparse at f=0.05
    for variant in ["B_whiten_before_topk", "C_random_fixed_positions"]:
        v = metrics["by_variant"][variant]["f_0.05"]
        if median(v["keysep"]) <= raw_keysep and median(v["recall"]) >= raw_recall:
            return ("PASS", variant)  # L-build proceeds with this variant
    
    # MM scenarios
    c = metrics["by_variant"]["C_random_fixed_positions"]["f_0.05"]
    if median(c["keysep"]) <= raw_keysep and median(c["recall"]) < raw_recall:
        return ("MM_negative_recall_axis", "can preserve diversity OR magnitude, not both")
    
    return ("MM_negative_full", "projection + sparse don't compose for KV recall")
```

## Cell 2 (L-BUILD on probe-confirmed variant) spec

### 4-arm CAN-fail (per original flagship pre-reg, now on rescued composition)
```
Arm 1 (full):                     SparseProjectedKVStore(variant=B, f=0.05, N=8192, M=5000)
Arm 2 (no-projection):            SparseRawKVStore (just sparse on raw pythia keys)
Arm 3 (no-sparsification):        DenseProjectedKVStore (CERT 591 raw)
Arm 4 (no-learned-projection):    SparseAnalyticProjectionKVStore (CERT 591 analytic ceiling)
```

### Predictions per arm
| Arm | recall_on_heldout | capacity_M_at_f0.05 | notes |
|-----|-------------------|---------------------|-------|
| 1   | ≥0.60 | ≥2000 facts | rescued composition holds |
| 2   | <0.40 (key-crowding) | unbounded but low recall | sparse alone insufficient |
| 3   | ≥0.83 (CERT 591) | ~327 (Hebbian) | dense holds recall but limits M |
| 4   | ≤0.10 (analytic ceiling) | varies | learned >> analytic per CERT 591 |

## HARD_PASS / HARD_FAIL bands
- **Probe HARD_PASS:** variant B holds (or C as fallback with MM_negative_recall_axis outcome documented)
- **L-build HARD_PASS:** Arm 1 recall ≥0.60 at M=5000 + cv ≤ 0.05 across 3 seeds + Arm 1 > Arm 2 by ≥0.20 + capacity_M ≥ 2x Arm 3 (sparse super-capacity)
- **L-build HARD_FAIL:** Arm 1 recall <0.40 OR Arm 1 capacity_M < Arm 3 (sparse adds no scale)
- **MM:** Arm 1 recall ∈ [0.40, 0.60] OR variant C used with recall-loss documented

## Verify-the-referent guards
- Use existing LearnedContrastiveProjection from CERT 591 build directly (NOT redesign; same N=8192 / contrastive loss / split discipline)
- Use existing pythia-2.8B + 600 finetune-steps loading code from CERT 591
- ZCA_whiten = `(X - X.mean()).dot(eig_decomp_isqrt(cov_X))` (standard; 5-line numpy)
- raw_sparse_baseline reproduces CERT 591 raw-sparse failure (crowding) — sanity check the probe regime matches
- 4-layer-witness REQUIRED (Phase 3 destination + storage chain foundation): cell-author + 2nd-witness + Skunkworks landed-VET + Director cross-check

## Cell-author lift on pythia de-gate
Mechanical "fill in code per spec":
1. Implement 3 sparsifiers (top_k_magnitude, ZCA_whiten + top_k, random_fixed_positions): ~30 lines numpy
2. Wire probe metrics output (above schema): ~50 lines
3. Run probe smoke (pythia-160M, 1-seed) → self-test PASS → dispatch GPU full (pythia-2.8B + 600 finetune)
4. **PROBE GATE evaluates → if PASS variant B → author L-build cell with `variant=B`** (cell 2)
5. If MM_negative → honest closure note + storage chain reframe (cell 2 NOT built; reframe to non-sparse composition)

## Standing
- **Exp-Dev:** PRE-STAGE above is cell-author-actionable on pythia de-gate (probe cell = first; L-build cell = gated on probe PASS); both cells now have full spec
- **Skunkworks:** SCHEMA-VET this PRE-STAGE if useful (otherwise composes into amendment v4 framework); landed-VET on each cell-land
- **Me:** flagship pre-stage filed; PHASE PLAN v2 #1/#2/#6 all now have cell-author-actionable specs (M2 + continual-write + flagship architecture pre-stages); next idle work = pre-stage capacity-saturation distinctive-axis cell or D1 suspects re-runs

-- Research (Director)
