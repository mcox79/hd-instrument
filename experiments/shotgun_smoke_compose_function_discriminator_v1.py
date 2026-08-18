"""
shotgun_smoke_compose_function_discriminator_v1 -- fast ablation of 5 compose-function variants.

PURPOSE: Information acquisition only. NOT a cert cell. NO queue ship.
GOAL: Identify which compose forms are LIVE (non-degenerate) vs DEAD (collapse to unigram BPC).

FIVE ARMS:
  ARM_MULTIPLICATIVE          -- gate = dopa * ACh * sero  (our 3-axis cell pattern)
  ARM_MULTIPLICATIVE_FLOOR01  -- gate = max(dopa*ACh*sero, 0.01)  (floor rescue?)
  ARM_MULTIPLICATIVE_FLOOR10  -- gate = max(dopa*ACh*sero, 0.10)  (larger floor)
  ARM_SIGMOID_ADDITIVE        -- gate = sigmoid(a*dopa + b*ACh + c*sero) (brain-canonical)
  ARM_LOG_ADDITIVE            -- gate = exp(log(dopa+eps)+log(ACh+eps)+log(sero+eps))  (log-space multiply)
  ARM_MAX_POOL                -- gate = max(dopa, ACh, sero)  (winner-take-all)

SMOKE CONFIG: N=256 dims, N_TRAIN=1000 tokens, 3 seeds. Pure numpy. <60s wall total.

PRE-REGISTERED BANDS (information-acquisition only; no cert):
  DEAD   -- BPC within 0.01 bits of unigram BPC (degenerate collapse; gate does nothing)
  LIVE   -- BPC differs from unigram by > 0.05 bits (gate modulates learning)
  DEGRADED -- BPC WORSE than no-modulator control (gate interferes)
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
import time
import json
import os

# ---- CONFIG ----
N_DIM = 256          # HD vector dimensionality
N_TRAIN = 1000       # tokens from text8 proxy (random bigrams; no actual text8 needed)
SEEDS = [42, 137, 999]
VOCAB = 256          # small vocab for speed
ALPHA = 1.0          # sigmoid weight for dopa
BETA = 1.0           # sigmoid weight for ACh
GAMMA = 1.0          # sigmoid weight for sero
EPS = 1e-6           # log-space epsilon

# ---- COMPOSE FUNCTIONS ----

def compose_multiplicative(dopa, ach, sero):
    """Pure product -- known to collapse when any modulator near 0."""
    return dopa * ach * sero

def compose_multiplicative_floor01(dopa, ach, sero):
    """Product with floor 0.01 -- does floor rescue collapse?"""
    return max(dopa * ach * sero, 0.01)

def compose_multiplicative_floor10(dopa, ach, sero):
    """Product with floor 0.10 -- larger floor."""
    return max(dopa * ach * sero, 0.10)

def compose_sigmoid_additive(dopa, ach, sero):
    """Brain-canonical: sigmoid of weighted sum (Pawlak-Kerr-Cheong)."""
    x = ALPHA * dopa + BETA * ach + GAMMA * sero
    return 1.0 / (1.0 + np.exp(-x))

def compose_log_additive(dopa, ach, sero):
    """Log-space multiply = exp(sum of logs). Mathematically equiv to multiply but avoids near-zero collapse."""
    return np.exp(np.log(dopa + EPS) + np.log(ach + EPS) + np.log(sero + EPS))

def compose_max_pool(dopa, ach, sero):
    """Winner-take-all: max of three modulators."""
    return max(dopa, ach, sero)

# No-modulator control
def compose_none(dopa, ach, sero):
    """Control: gate=1.0 always (pure Hebbian)."""
    return 1.0

# ---- HEBBIAN MEMORY ----

def run_arm(compose_fn, seed, n_dim=N_DIM, n_train=N_TRAIN, vocab=VOCAB):
    """
    Run one arm with given compose function.
    Returns dict: bpc, readout_entropy, gate_mean, gate_std, collapse_flag.
    """
    rng = np.random.default_rng(seed)

    # Random bipolar HD vectors for each token type
    codebook = rng.choice([-1.0, 1.0], size=(vocab, n_dim)).astype(np.float32)

    # Initialize weight matrix
    W = np.zeros((n_dim, n_dim), dtype=np.float32)

    # Generate random token sequence (proxy for text8 bigrams)
    tokens = rng.integers(0, vocab, size=n_train + 1)

    # Hebbian write with gated LR
    gate_vals = []
    for i in range(n_train):
        src = codebook[tokens[i]]
        tgt = codebook[tokens[i + 1]]

        # Modulators: random scalars in [0,1]
        dopa = float(rng.uniform(0.0, 1.0))
        ach  = float(rng.uniform(0.0, 1.0))
        sero = float(rng.uniform(0.0, 1.0))

        gate = compose_fn(dopa, ach, sero)
        gate_vals.append(gate)

        # Hebbian outer-product write (scaled by gate and 1/n_dim for stability)
        W += (gate / n_dim) * np.outer(tgt, src)

    # Readout: for each token predict next token via cosine similarity
    correct_log_probs = []
    entropies = []

    # Compute unigram distribution for BPC floor reference
    token_counts = np.bincount(tokens, minlength=vocab).astype(np.float64)
    token_probs = token_counts / token_counts.sum()
    unigram_bpc = -np.sum(token_probs * np.log2(np.maximum(token_probs, 1e-12)))

    for i in range(n_train):
        src = codebook[tokens[i]]
        predicted = W @ src  # shape (n_dim,)

        # Cosine similarity to all vocab vectors
        norms = np.linalg.norm(codebook, axis=1) + 1e-8
        pred_norm = np.linalg.norm(predicted) + 1e-8
        sims = (codebook @ predicted) / (norms * pred_norm)  # shape (vocab,)

        # Softmax at temperature T=0.5 (needed to avoid near-uniform)
        T = 0.5
        logits = sims / T
        logits -= logits.max()
        probs = np.exp(logits)
        probs /= probs.sum()

        tgt_idx = tokens[i + 1]
        log_prob = np.log2(np.maximum(probs[tgt_idx], 1e-12))
        correct_log_probs.append(log_prob)

        # Entropy of predicted distribution
        entropies.append(-np.sum(probs * np.log2(np.maximum(probs, 1e-12))))

    bpc = -np.mean(correct_log_probs)
    readout_entropy = np.mean(entropies)
    gate_mean = float(np.mean(gate_vals))
    gate_std  = float(np.std(gate_vals))

    # Degenerate-collapse flag: BPC within 0.01 bits of unigram entropy
    collapse_flag = abs(bpc - unigram_bpc) < 0.01

    return {
        "bpc": float(bpc),
        "unigram_bpc": float(unigram_bpc),
        "readout_entropy": float(readout_entropy),
        "gate_mean": gate_mean,
        "gate_std": gate_std,
        "collapse_flag": bool(collapse_flag),
        "bpc_vs_unigram_delta": float(bpc - unigram_bpc),
    }


# ---- INSTRUMENTATION SELF-TEST (mandatory per role contract) ----

def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    result = run_arm(compose_sigmoid_additive, seed=0, n_dim=32, n_train=50, vocab=16)
    assert result["bpc"] is not None and not np.isnan(result["bpc"]), "bpc is null"
    assert result["bpc"] > 0.0, f"bpc sentinel 0: {result['bpc']}"
    assert result["readout_entropy"] is not None and result["readout_entropy"] > 0.0, "readout_entropy sentinel"
    assert result["gate_mean"] is not None, "gate_mean null"
    assert result["unigram_bpc"] > 0.0, "unigram_bpc sentinel"
    assert "collapse_flag" in result, "collapse_flag missing"
    assert "bpc_vs_unigram_delta" in result, "bpc_vs_unigram_delta missing"
    print("[SELFTEST] PASS -- all metrics non-null at small scale")

_instrumentation_selftest()


# ---- MAIN SWEEP ----

ARMS = {
    "ARM_MULTIPLICATIVE":         compose_multiplicative,
    "ARM_MULTIPLICATIVE_FLOOR01": compose_multiplicative_floor01,
    "ARM_MULTIPLICATIVE_FLOOR10": compose_multiplicative_floor10,
    "ARM_SIGMOID_ADDITIVE":       compose_sigmoid_additive,
    "ARM_LOG_ADDITIVE":           compose_log_additive,
    "ARM_MAX_POOL":               compose_max_pool,
    "ARM_CONTROL_NO_MOD":         compose_none,
}

print(f"\n=== SHOTGUN SMOKE: compose-function discriminator ===")
print(f"N_DIM={N_DIM}  N_TRAIN={N_TRAIN}  SEEDS={SEEDS}  VOCAB={VOCAB}")
print(f"Arms: {list(ARMS.keys())}\n")

t_start = time.time()
results = {}

for arm_name, fn in ARMS.items():
    arm_results = []
    for seed in SEEDS:
        r = run_arm(fn, seed)
        arm_results.append(r)

    bpc_vals    = [r["bpc"] for r in arm_results]
    ent_vals    = [r["readout_entropy"] for r in arm_results]
    gate_means  = [r["gate_mean"] for r in arm_results]
    gate_stds   = [r["gate_std"] for r in arm_results]
    collapse    = any(r["collapse_flag"] for r in arm_results)
    deltas      = [r["bpc_vs_unigram_delta"] for r in arm_results]
    unigram_bpc = arm_results[0]["unigram_bpc"]

    results[arm_name] = {
        "bpc_mean":          float(np.mean(bpc_vals)),
        "bpc_std":           float(np.std(bpc_vals)),
        "readout_entropy_mean": float(np.mean(ent_vals)),
        "gate_mean_mean":    float(np.mean(gate_means)),
        "gate_std_mean":     float(np.mean(gate_stds)),
        "collapse_any_seed": collapse,
        "bpc_vs_unigram_mean": float(np.mean(deltas)),
        "unigram_bpc":       unigram_bpc,
    }

    status = "DEAD" if collapse else ("LIVE" if abs(np.mean(deltas)) > 0.05 else "MARGINAL")
    print(f"  {arm_name:35s}  BPC={np.mean(bpc_vals):.4f}  delta_vs_unigram={np.mean(deltas):+.4f}  "
          f"gate_mean={np.mean(gate_means):.3f}+-{np.mean(gate_stds):.3f}  "
          f"collapse={collapse}  STATUS={status}")

t_wall = time.time() - t_start
print(f"\nWall time: {t_wall:.1f}s")

# ---- SUSPICIOUS-RESULT GATE ----
bpc_vals_all = [results[a]["bpc_mean"] for a in results]
if len(set(round(v, 4) for v in bpc_vals_all)) == 1:
    print("\n[SUSPICIOUS] All arms produce identical BPC -- instrumentation suspect. BLOCKED.")
    sys.exit(1)

n_collapsed = sum(1 for a in results if results[a]["collapse_any_seed"])
print(f"\n[GATE] {n_collapsed}/{len(ARMS)} arms collapsed to unigram.")

# ---- PRINT RANKED SUMMARY ----
print("\n=== RANKED BY BPC (lower = better, more informative) ===")
ranked = sorted(results.items(), key=lambda x: x[1]["bpc_mean"])
for arm_name, r in ranked:
    live = "LIVE   " if not r["collapse_any_seed"] and abs(r["bpc_vs_unigram_mean"]) > 0.05 else \
           ("DEAD   " if r["collapse_any_seed"] else "MARGINAL")
    print(f"  {live}  {arm_name:35s}  BPC={r['bpc_mean']:.4f}  delta={r['bpc_vs_unigram_mean']:+.4f}  "
          f"readout_entropy={r['readout_entropy_mean']:.4f}")

# ---- SAVE METRICS ----
out_dir = "D:/AI/hd-instrument/data/shotgun_smoke_compose_function_discriminator_v1"
os.makedirs(out_dir, exist_ok=True)
metrics_path = os.path.join(out_dir, "metrics.json")
with open(metrics_path, "w") as f:
    json.dump({
        "arms": results,
        "config": {
            "N_DIM": N_DIM,
            "N_TRAIN": N_TRAIN,
            "SEEDS": SEEDS,
            "VOCAB": VOCAB,
        },
        "wall_s": t_wall,
        "purpose": "shotgun_smoke_information_acquisition_only",
    }, f, indent=2)

print(f"\nMetrics saved: {metrics_path}")
print("Done.")
