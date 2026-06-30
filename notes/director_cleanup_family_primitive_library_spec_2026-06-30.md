# Cleanup primitive library spec — for Cell B Cleanup family × WM K-cliff

**Filed:** 2026-06-30 19:00 UTC
**Audience:** hdi_exp_dev (next cell-author)
**Motivation:** a2e6c3b4 deferred Cell B (Cleanup family × WM K-cliff) with rationale: needs 4 cleanup primitives from scratch + ~800-1200 LoC; risk of replicating v1/v2 phantom-degeneracy pattern. This doc spec'd the primitives so cell-author has a clean drop-in library.

---

## Library scope

New module: `hdlab/cleanup_family.py` (or extend `hdlab/iterative_attractor.py`).

**4 cleanup primitives + 1 baseline. All share the same signature.**

### Common signature

```python
def cleanup(
    query: np.ndarray,        # shape [D] or [batch, D] (HD vector(s) to clean)
    codebook: np.ndarray,     # shape [N, D] (N codes to clean toward)
    **params,                 # primitive-specific kwargs
) -> tuple[np.ndarray, dict]:
    """Returns (recovered_vector, diagnostics) where:
       recovered_vector has same shape as query (single HD or batch)
       diagnostics is a dict with at least: {
           'n_iterations': int,    # 0 for one-shot; >0 for iterative
           'converged': bool,
           'final_argmax_idx': int (or list for batch),
       }
    """
```

### Primitive 1: classical_hopfield

```python
def classical_hopfield(query, codebook, *, max_steps=8, sign_quantize=True):
    """Classical Hopfield (Hebb 1949 / Hopfield 1982): outer-product W matrix + sign update.
    
    Capacity ~0.14 N (Hopfield original); N = codebook D.
    Args:
      sign_quantize: if True, use sign(W @ s) per step (binary Hopfield);
                     if False, use W @ s (continuous; weaker but smoother).
    """
    # W = codebook.T @ codebook / N (outer-product Hebbian)
    # state = query (L2-normalized)
    # for step in range(max_steps):
    #   s_next = np.sign(W @ state) if sign_quantize else (W @ state)
    #   if ||s_next - state|| < tol: break
    #   state = s_next / ||s_next||
    # return state, diagnostics
```

### Primitive 2: modern_hopfield_continuous (Ramsauer 2021 dense Hopfield)

```python
def modern_hopfield_continuous(query, codebook, *, beta=8.0, max_steps=8):
    """Krotov-Hopfield 2016 / Ramsauer 2021 dense associative memory.
    
    Exponential capacity (~exp(D)); softmax-attention update rule.
    Equivalent to transformer attention with codebook as keys+values.
    """
    # state = query (L2-normalized)
    # for step in range(max_steps):
    #   scores = state @ codebook.T          # [N]
    #   weights = softmax(beta * scores)      # [N]
    #   s_next = weights @ codebook           # [D]
    #   if ||s_next - state|| < tol: break
    #   state = s_next / ||s_next||
    # return state, diagnostics
```

NB: existing `hdlab.iterative_attractor.iterative_cleanup` is functionally equivalent to this; can wrap/reuse.

### Primitive 3: k_NN_lookup

```python
def k_NN_lookup(query, codebook, *, k=1):
    """k-nearest-neighbor cleanup: one-shot top-k argmax + averaging.
    
    Strict baseline: no iteration; no attractor dynamics; pure retrieval.
    k=1 = argmax (the substrate's default behavior).
    k>1 = top-k averaged (smoother but loses identity).
    """
    # scores = query @ codebook.T               # [N]
    # topk_idx = scores.argsort()[-k:]          # top-k indices
    # recovered = codebook[topk_idx].mean(0)    # [D]
    # diagnostics = {'n_iterations': 0, 'converged': True, 'final_argmax_idx': int(topk_idx[-1])}
    # return recovered, diagnostics
```

### Primitive 4: iterative_attractor (existing)

Wrap `hdlab.iterative_attractor.iterative_cleanup` with the common signature.

### Baseline: no_cleanup

```python
def no_cleanup(query, codebook):
    """Return query unchanged; diagnostics report nothing happened. Strict baseline."""
    return query, {'n_iterations': 0, 'converged': True, 'final_argmax_idx': -1}
```

---

## Cell B: Cleanup family × WM K-cliff phase diagram

### Hypothesis
Cleanup family CONVERGED at PC (4 families MB; cleanup choice family-invariant at PC scale per a009a44a MM atom). WM is a DIFFERENT regime — higher K, multi-bank routing, sequence-binding-adjacent. Possibly cleanup family discriminates here.

### Cell design

```python
# 4 cleanup primitives + 1 no_cleanup baseline (5 arms total)
ARMS = [
    "no_cleanup",
    "classical_hopfield",
    "modern_hopfield_continuous",
    "iterative_attractor",
    "k_NN_lookup",
]

# K-sweep (the WM capacity primitive)
K_PER_BANK_SWEEP = [50, 100, 250, 500, 1000]

# Fixed axes (META_RULE_AW seed-config-identical)
NUM_BANKS = 16
N_DIM = 8192
SEEDS = [7, 13, 19]
```

### Discriminator

- HARD_PASS: at least 3 of 5 arms produce DISTINCT K_cliff localizations (≥ 0.3 log2 separation)
- MIDDLE_BAND: at least 2 of 5 distinct
- HARD_FAIL: all 5 cleanup arms converge to identical K_cliff (cleanup choice family-invariant at WM scale too)

### Discipline gates (mandatory)

- META_RULE_AX: per-arm mechanism_hash distinct + per-K per-arm metric distinct
- META_RULE_AY (proposed today by Skunkworks after ANCHOR 4 v3 dense-triplet phantom): if cell-author's self-reported distinctness check returns False → HARD_FAIL automatically (verdict logic must NOT emit HARD_PASS when distinctness fails)
- META_RULE_AW: identical config across seeds
- META_RULE_Q: suspect-1.000 check at saturating K regime
- CARDINALITY_OK: 4 × 5 K × 3 seeds = 60 grid points; declared in pre-reg

### Smoke gate (DISCRIMINATOR-MUST-SURVIVE-SCALE)

At smoke regime (N=2048, K=100/250), at least 3 of 5 cleanup arms produce DISTINCT K_cliff predictions. If <3 distinct → BLOCK_DISPATCH (regime too easy or primitive bug).

### Queue + timeout

- Queue: overnight_queue (GPU; multi-bank matmul-bound) — note that v2 modern Hopfield can be made GPU via torch.cuda for the softmax-attention update
- Timeout: 7200s/seed
- ~2-3 hours full run per seed

### Helper modules SCP'd before queue_add

- `_substrate_cleanup_family_wm_kcliff_v1_core.py` (cell helper)
- `hdlab/cleanup_family.py` (already on remote after push)

---

## Effort estimate

- `hdlab/cleanup_family.py`: ~150 LoC (3 new primitives + 1 wrapper + tests)
- Cell file (_core + seed entries): ~400 LoC
- Pre-reg: ~80 lines
- Total ~600 LoC (lower than a2e6c3b4's 800-1200 estimate because we reuse existing iterative_attractor + write thin wrappers around standard mechanisms)

---

## How to use this spec

hdi_exp_dev spawn prompt should include:
1. Read this spec end-to-end first
2. Implement `hdlab/cleanup_family.py` with the 5 functions
3. Smoke test each primitive independently (just verify they return finite arrays + diagnostics)
4. Author the cell with the 5-arm + K-sweep design
5. Apply META_RULE_AY (verdict HARD_FAIL on self-reported distinctness False)
6. Smoke at full-N (or analytical justification)
7. SCP helper + dispatch via Orchestrator to overnight_queue (GPU)

Composes with `feedback_no_hallucinated_numbers_verify_on_disk` + `feedback_use_peek_arm_metrics_before_framing` + the META_RULE_Q suspect-1.000 check.
