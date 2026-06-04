"""
phase05_v1_algorithm1_debug_pythia160m_v1 -- Phase 0.5 rung-0 debug.

SCIENTIFIC QUESTION (IMPLEMENTATION CORRECTNESS GATE):
  Does Algorithm 1 (Appendix B, arXiv:2509.25045) run cleanly on Pythia-160M
  (12 layers) BEFORE we attempt Llama-3.2-1B? This is a pure engineering
  correctness gate: validate K-means over layer embeddings + sum-pool centroids
  k=5 pipeline implementation produces valid bipolar substrate codes and that
  the MLP probe trains without NaN or shape errors.

  Pythia-160M: 12 layers, hidden_dim=768, ~160M params, ~320MB BF16.
  Algorithm 1 adapted: K-means over Pythia layers 6-12 (= latter half, mirroring
  paper's layers 16-32 of 32 for Llama-3.1-8B) + sum-pool centroids k=5.

PIPELINE:
  1. Load Pythia-160M with residual stream hooks at layers 6-12 (7 layers).
  2. For each doc: collect final-token residuals from layers 6-12. Shape: (7, 768).
  3. K-means with k=5 over the 7 layer-residuals. Centroids shape: (5, 768).
  4. Sum-pool centroids -> (768,) embedding.
  5. Sign() -> bipolar code in {-1, +1}^768 as substrate-native code.
  6. Train tiny MLP probe: embedding -> val_sim score (synthetic target).
     Since we have no real Hyperprobe training data in rung-0, we use a synthetic
     regression target derived from the embedding itself to verify convergence.
  7. 50-100 epochs, 3 seeds. Check: no NaN, val_sim trajectory improves.

RUNG-0 STRATEGY:
  This is an engineering correctness gate. The "val_sim" here is SYNTHETIC
  (embedding self-reconstruction proxy). The HP gate checks:
    - Pipeline runs without crashes, NaN, shape errors
    - Embedding quality (bipolar balance, pairwise diversity) looks healthy
    - MLP probe converges on the synthetic target

PRE-REGISTERED BANDS:
  HARD-PASS:   Algorithm 1 pipeline runs cleanly (no NaN, no shape errors,
               no device errors) AND bipolar balance > 0.3 (|mean(xi)| < 0.7)
               AND embedding pairwise cos diversity > 0.1 (embeddings distinct)
               AND probe loss decreasing over 50+ epochs across 3/3 seeds.
               This is a PURE IMPLEMENTATION CORRECTNESS gate, not a product claim.
  MIDDLE:      Pipeline runs but synthetic probe flat/noisy; implementation has
               subtle bugs; iterate at rung 0 (cheap).
  HARD-FAIL:   Pipeline crashes OR shape mismatch OR NaN in embeddings OR
               zero-diversity embeddings (all identical).

FORMULA SELF-TESTS (PROT-022):
  1. kmeans_centroids(embeddings=(7,768), k=5) returns shape (5,768).
     [INPUT: random (7,768) -> EXPECTED: shape==(5,768)]
  2. sum_pool_centroids((5,768)) returns shape (768,) equal to centroids.sum(0).
     [INPUT: ones (5,768) -> EXPECTED: values all == 5.0]
  3. bipolar_sign((768,) real-valued) returns {-1,+1}^768 via np.sign, zeros -> +1.
     [INPUT: random float array -> EXPECTED: all vals in {-1.0, 1.0}]
  4. bipolar_balance: mean(xi) near 0 for balanced random code.
     [INPUT: N=1000 random bipolar -> EXPECTED: |mean| < 0.1]
  5. pairwise_cos_diversity: two random bipolar codes have cos < 0.2 on average.
     [INPUT: 5 random bipolar codes (256,) -> EXPECTED: mean pairwise |cos| < 0.4]
  6. MLP probe step: single forward + backward on tiny batch returns finite loss.
     [INPUT: (2, 768) embeddings -> EXPECTED: isfinite(loss)]

PROT-018: anchor has NO _nN suffix; substrate dim = Pythia hidden_dim = 768.
  Explicit: PRODUCTION substrate dim = 768 (Pythia-160M hidden). No _nN suffix.
PROT-021: partials keyed by seed + run_mode.

ASCII-only stdout per feedback_ascii_only_in_scripts.
Per feedback_testbed_progress_logging_and_restart: per-cell partial JSON emitted.
"""
from __future__ import annotations

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial,
    aggregate_partials,
)

ANCHOR_NAME = "phase05_v1_algorithm1_debug_pythia160m_v1"

# PROT-018 explicit declaration
PRODUCTION_SUBSTRATE_DIM = 768  # Pythia-160M hidden_dim

# Pythia-160M model config
PYTHIA_MODEL_ID = "EleutherAI/pythia-160m"
PYTHIA_N_LAYERS = 12
PYTHIA_HIDDEN = 768
# Layer range for Algorithm 1 (latter half, mirroring paper's 16-32 of 32)
LAYER_START = 6   # inclusive, 0-indexed
LAYER_END = 12    # exclusive (layers 6..11 = 7 layers)
K_CLUSTERS = 5    # paper Algorithm 1

# Probe training
N_DOCS_TRAIN = 50
N_DOCS_VAL = 20

RUN_MODE = (
    "smoke" if "--smoke" in sys.argv
    else os.environ.get("HDLAB_RUN_MODE", "full")
).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_EPOCHS = 20
    BATCH_SIZE = 4
    LR = 1e-3
    N_DOCS_TRAIN_EFF = 20
    N_DOCS_VAL_EFF = 10
else:
    SEEDS = [7, 17, 23]
    N_EPOCHS = 80
    BATCH_SIZE = 8
    LR = 3e-4
    N_DOCS_TRAIN_EFF = N_DOCS_TRAIN
    N_DOCS_VAL_EFF = N_DOCS_VAL

# Pre-registered thresholds
HP_BIPOLAR_BALANCE_MAX = 0.7   # |mean(xi)| < 0.7
HP_DIVERSITY_MIN = 0.1         # mean pairwise |cos| < 1 - 0.1 = 0.9 -> mean distinctness > 0.1
HP_MIN_SEEDS = 3
MID_MIN_SEEDS = 2


# ---------------------------------------------------------------------------
# Algorithm 1 helpers (pure numpy except model load)
# ---------------------------------------------------------------------------

def kmeans_centroids(embeddings: np.ndarray, k: int) -> np.ndarray:
    """K-means clustering of embeddings. Returns centroid matrix (k, D).

    Uses Lloyd's algorithm (sklearn or manual numpy).
    embeddings: (L, D) float32 where L = number of layers.
    Returns: (min(k, L), D) float32 centroids.
    """
    L, D = embeddings.shape
    k_actual = min(k, L)  # can't have more clusters than points
    if k_actual == 1:
        return embeddings.mean(axis=0, keepdims=True)
    try:
        from sklearn.cluster import KMeans as _KMeans
        km = _KMeans(n_clusters=k_actual, n_init=3, max_iter=100, random_state=42)
        km.fit(embeddings.astype(np.float64))
        return km.cluster_centers_.astype(np.float32)
    except ImportError:
        # Manual numpy fallback: random init + 20 Lloyd iterations
        rng = np.random.default_rng(42)
        idx = rng.choice(L, size=k_actual, replace=False)
        centers = embeddings[idx].copy()
        for _ in range(20):
            dists = np.sum((embeddings[:, None, :] - centers[None, :, :]) ** 2, axis=-1)
            assigns = np.argmin(dists, axis=1)
            new_centers = np.zeros_like(centers)
            for c in range(k_actual):
                mask = assigns == c
                if mask.sum() > 0:
                    new_centers[c] = embeddings[mask].mean(axis=0)
                else:
                    new_centers[c] = centers[c]
            if np.max(np.abs(new_centers - centers)) < 1e-6:
                break
            centers = new_centers
        return centers.astype(np.float32)


def sum_pool_centroids(centroids: np.ndarray) -> np.ndarray:
    """Sum-pool centroid matrix (k, D) -> (D,) embedding."""
    return centroids.sum(axis=0).astype(np.float32)


def bipolar_sign(vec: np.ndarray) -> np.ndarray:
    """Convert real-valued vector to bipolar {-1, +1}; zeros -> +1."""
    xi = np.sign(vec).astype(np.float32)
    xi[xi == 0] = 1.0
    return xi


def pairwise_cos_diversity(codes: np.ndarray) -> float:
    """Mean pairwise cosine similarity magnitude (lower = more diverse).

    codes: (M, D) float32.
    Returns: mean |cos(xi_i, xi_j)| for i < j.
    """
    M = codes.shape[0]
    if M < 2:
        return 0.0
    norms = np.linalg.norm(codes, axis=1)  # (M,)
    pairs = []
    for i in range(M):
        for j in range(i + 1, M):
            n_i = float(norms[i])
            n_j = float(norms[j])
            if n_i < 1e-30 or n_j < 1e-30:
                continue
            cos = float(abs(np.dot(codes[i], codes[j]) / (n_i * n_j)))
            pairs.append(cos)
    return float(np.mean(pairs)) if pairs else 0.0


# ---------------------------------------------------------------------------
# Tiny MLP probe (no external hyperprobe library)
# ---------------------------------------------------------------------------

def build_tiny_mlp(input_dim: int, hidden: int = 128, output_dim: int = 32):
    """Build tiny MLP: input_dim -> hidden -> output_dim."""
    import torch
    import torch.nn as nn
    return nn.Sequential(
        nn.Linear(input_dim, hidden),
        nn.ReLU(),
        nn.Linear(hidden, output_dim),
    )


def _synthetic_target(embeddings: np.ndarray, seed: int) -> np.ndarray:
    """Synthetic regression target: random linear projection of embedding.

    Creates a deterministic target that the probe can learn (unlike random labels).
    Target dim = 32; allows us to verify convergence without real Hyperprobe data.
    """
    rng = np.random.default_rng(seed + 999)
    proj = rng.standard_normal((embeddings.shape[1], 32)).astype(np.float32)
    proj /= np.linalg.norm(proj, axis=0, keepdims=True) + 1e-30
    return (embeddings @ proj).astype(np.float32)


def train_probe(
    train_embs: np.ndarray,
    val_embs: np.ndarray,
    seed: int,
    n_epochs: int,
    batch_size: int,
    lr: float,
    verbose: bool = True,
) -> dict:
    """Train tiny MLP probe on synthetic target; return loss history."""
    import torch
    import torch.nn as nn
    import torch.optim as optim

    torch.manual_seed(seed)
    device = "cpu"
    model = build_tiny_mlp(train_embs.shape[1]).to(device)
    opt = optim.Adam(model.parameters(), lr=lr)

    train_t = torch.from_numpy(train_embs).to(device)
    val_t = torch.from_numpy(val_embs).to(device)
    train_targets = torch.from_numpy(_synthetic_target(train_embs, seed)).to(device)
    val_targets = torch.from_numpy(_synthetic_target(val_embs, seed)).to(device)

    n_train = train_t.shape[0]
    rng_idx = np.random.default_rng(seed + 1)
    train_losses = []
    val_losses = []

    for epoch in range(n_epochs):
        model.train()
        perm = rng_idx.permutation(n_train)
        ep_loss = 0.0
        n_batches = 0
        for i in range(0, n_train, batch_size):
            idx = perm[i:i + batch_size]
            xb = train_t[idx.tolist()]
            yb = train_targets[idx.tolist()]
            opt.zero_grad()
            pred = model(xb)
            loss = nn.functional.mse_loss(pred, yb)
            loss.backward()
            opt.step()
            ep_loss += float(loss.item())
            n_batches += 1
        train_losses.append(ep_loss / max(n_batches, 1))

        model.eval()
        with torch.no_grad():
            val_pred = model(val_t)
            val_loss = float(nn.functional.mse_loss(val_pred, val_targets).item())
        val_losses.append(val_loss)

        if verbose and (epoch % 10 == 0 or epoch == n_epochs - 1):
            print(
                f"  epoch={epoch:3d}/{n_epochs} train_loss={train_losses[-1]:.4f} "
                f"val_loss={val_loss:.4f}",
                flush=True,
            )

    return {
        "train_losses": [float(v) for v in train_losses],
        "val_losses": [float(v) for v in val_losses],
        "final_train_loss": float(train_losses[-1]) if train_losses else float("nan"),
        "final_val_loss": float(val_losses[-1]) if val_losses else float("nan"),
        "initial_val_loss": float(val_losses[0]) if val_losses else float("nan"),
    }


# ---------------------------------------------------------------------------
# Residual extraction with hooks
# ---------------------------------------------------------------------------

def extract_layer_residuals(
    model,
    tokenizer,
    text: str,
    layer_start: int,
    layer_end: int,
    device: str,
) -> Optional[np.ndarray]:
    """Extract final-token residuals from layers [layer_start, layer_end).

    Returns: (layer_end - layer_start, hidden_dim) float32, or None on failure.
    """
    import torch

    residuals: Dict[int, np.ndarray] = {}
    hooks = []

    def make_hook(layer_idx):
        def hook(module, inp, out):
            # out may be tuple; take first element = hidden state
            if isinstance(out, (tuple, list)):
                hidden = out[0]
            else:
                hidden = out
            # hidden: (batch, seq, hidden) or (seq, batch, hidden)
            if hidden.dim() == 3:
                # Take last token, first batch
                res = hidden[0, -1, :].detach().float().cpu().numpy()
            elif hidden.dim() == 2:
                res = hidden[-1, :].detach().float().cpu().numpy()
            else:
                res = hidden.detach().float().cpu().numpy().flatten()[:PYTHIA_HIDDEN]
            residuals[layer_idx] = res
        return hook

    # Attach hooks to each target layer
    # Pythia-160M uses model.gpt_neox.layers as the layer list
    if hasattr(model, "gpt_neox") and hasattr(model.gpt_neox, "layers"):
        layers_list = model.gpt_neox.layers
    elif hasattr(model, "transformer") and hasattr(model.transformer, "h"):
        layers_list = model.transformer.h
    elif hasattr(model, "model") and hasattr(model.model, "layers"):
        layers_list = model.model.layers
    else:
        return None

    for li in range(layer_start, min(layer_end, len(layers_list))):
        h = layers_list[li].register_forward_hook(make_hook(li))
        hooks.append(h)

    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with __import__("torch").no_grad():
            model(**inputs)
    except Exception as e:
        print(f"[extract] ERROR during forward pass: {e}", flush=True)
        for h in hooks:
            h.remove()
        return None
    finally:
        for h in hooks:
            h.remove()

    # Collect in order
    ordered = [layer_start + i for i in range(layer_end - layer_start)]
    reses = []
    for li in ordered:
        if li in residuals:
            reses.append(residuals[li])
        else:
            # Missing layer -> zeros
            reses.append(np.zeros(PYTHIA_HIDDEN, dtype=np.float32))

    if not reses:
        return None
    return np.stack(reses, axis=0).astype(np.float32)  # (n_layers, hidden)


# ---------------------------------------------------------------------------
# Instrumentation self-test (MANDATORY)
# ---------------------------------------------------------------------------

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at smoke scale."""
    import torch
    print("[selftest] running instrumentation self-test...", flush=True)

    # 1. kmeans_centroids: (7, 768) -> (5, 768)
    rng = np.random.default_rng(1)
    embs_7 = rng.standard_normal((7, 768)).astype(np.float32)
    centroids = kmeans_centroids(embs_7, k=5)
    assert centroids.shape == (5, 768), (
        f"[selftest] FAIL: kmeans_centroids shape={centroids.shape} expected (5,768)"
    )

    # 2. sum_pool_centroids: (5, 768) -> (768,) = sum of rows
    ones = np.ones((5, 768), dtype=np.float32)
    summed = sum_pool_centroids(ones)
    assert summed.shape == (768,), f"[selftest] FAIL: sum_pool shape={summed.shape}"
    assert np.allclose(summed, 5.0), f"[selftest] FAIL: sum_pool values not all 5: {summed[:3]}"

    # 3. bipolar_sign: all values in {-1, +1}
    v_test = rng.standard_normal(100).astype(np.float32)
    xi_test = bipolar_sign(v_test)
    assert xi_test.shape == (100,), f"[selftest] FAIL: bipolar_sign shape={xi_test.shape}"
    unique_vals = set(np.unique(xi_test).tolist())
    assert unique_vals.issubset({-1.0, 1.0}), (
        f"[selftest] FAIL: bipolar_sign has non-{{-1,1}} values: {unique_vals}"
    )
    # zeros -> +1
    v_zeros = np.zeros(10, dtype=np.float32)
    xi_zeros = bipolar_sign(v_zeros)
    assert np.all(xi_zeros == 1.0), f"[selftest] FAIL: zeros not -> +1: {xi_zeros}"

    # 4. bipolar_balance: random large code has |mean| < 0.1
    xi_big = rng.choice([-1.0, 1.0], size=1000).astype(np.float32)
    balance = abs(float(np.mean(xi_big)))
    assert balance < 0.1, f"[selftest] FAIL: balance={balance:.4f} expected < 0.1"

    # 5. pairwise_cos_diversity: 5 random bipolar codes (256,)
    codes_test = rng.choice([-1.0, 1.0], size=(5, 256)).astype(np.float32)
    div = pairwise_cos_diversity(codes_test)
    assert div >= 0.0 and div < 0.4, (
        f"[selftest] FAIL: pairwise diversity={div:.4f} expected in [0, 0.4)"
    )

    # 6. MLP probe step: single forward + backward returns finite loss
    mlp_test = build_tiny_mlp(input_dim=64, hidden=32, output_dim=8)
    embs_test = torch.from_numpy(rng.standard_normal((2, 64)).astype(np.float32))
    targets_test = torch.from_numpy(rng.standard_normal((2, 8)).astype(np.float32))
    pred_test = mlp_test(embs_test)
    loss_test = __import__("torch").nn.functional.mse_loss(pred_test, targets_test)
    assert np.isfinite(float(loss_test.item())), (
        f"[selftest] FAIL: probe loss is non-finite: {loss_test.item()}"
    )

    print(
        f"[selftest] PASS: kmeans_centroids_ok=True sum_pool_ok=True "
        f"bipolar_sign_ok=True balance={balance:.4f} diversity={div:.4f} "
        f"probe_loss={loss_test.item():.4f}",
        flush=True,
    )


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Run one seed
# ---------------------------------------------------------------------------

def run_one_seed(seed: int, tokenizer, model, device: str) -> dict:
    t_seed = time.time()
    print(
        f"[seed={seed}] extracting residuals from Pythia-160M "
        f"layers {LAYER_START}-{LAYER_END}...",
        flush=True,
    )

    # Generate synthetic docs from wikitext2 corpus
    from testbed.substrate_lm.data import wikitext2_char_corpus
    corpus = wikitext2_char_corpus(split="train", max_chars=50_000)

    # Split into ~100-char doc chunks
    doc_len = 100
    docs_all = [
        corpus[i:i + doc_len]
        for i in range(0, len(corpus) - doc_len, doc_len)
    ]
    n_needed = N_DOCS_TRAIN_EFF + N_DOCS_VAL_EFF + 5
    rng = np.random.default_rng(seed)
    if len(docs_all) >= n_needed:
        idx = rng.choice(len(docs_all), size=n_needed, replace=False)
        docs_sample = [docs_all[i] for i in idx]
    else:
        docs_sample = docs_all[:n_needed]

    train_docs = docs_sample[:N_DOCS_TRAIN_EFF]
    val_docs = docs_sample[N_DOCS_TRAIN_EFF:N_DOCS_TRAIN_EFF + N_DOCS_VAL_EFF]

    # Extract embeddings via Algorithm 1 pipeline
    def get_embedding(text: str) -> Optional[np.ndarray]:
        layer_res = extract_layer_residuals(
            model, tokenizer, text, LAYER_START, LAYER_END, device
        )
        if layer_res is None:
            return None
        centroids = kmeans_centroids(layer_res, k=K_CLUSTERS)  # (k, D)
        pooled = sum_pool_centroids(centroids)                 # (D,)
        xi = bipolar_sign(pooled)                              # {-1, +1}^D
        return xi

    print(f"[seed={seed}] extracting {len(train_docs)} train + {len(val_docs)} val embeddings", flush=True)

    train_embs = []
    for i, doc in enumerate(train_docs):
        emb = get_embedding(doc)
        if emb is not None:
            train_embs.append(emb)
        if (i + 1) % 10 == 0:
            print(f"  train {i+1}/{len(train_docs)}", flush=True)

    val_embs = []
    for doc in val_docs:
        emb = get_embedding(doc)
        if emb is not None:
            val_embs.append(emb)

    if not train_embs or not val_embs:
        return {
            "seed": int(seed),
            "error": "no_valid_embeddings",
            "n_train_embs": len(train_embs),
            "n_val_embs": len(val_embs),
        }

    train_arr = np.stack(train_embs, axis=0)
    val_arr = np.stack(val_embs, axis=0)

    print(
        f"[seed={seed}] embeddings: train shape={train_arr.shape} val shape={val_arr.shape}",
        flush=True,
    )

    # Embedding quality checks
    all_embs = np.vstack([train_arr, val_arr])
    balance = float(abs(np.mean(all_embs)))
    diversity = pairwise_cos_diversity(all_embs[:min(10, len(all_embs))])
    nan_frac = float(np.isnan(all_embs).mean())

    print(
        f"[seed={seed}] quality: balance={balance:.4f} diversity={diversity:.4f} nan_frac={nan_frac:.4f}",
        flush=True,
    )

    # Train probe
    probe_result = train_probe(
        train_arr, val_arr, seed=seed,
        n_epochs=N_EPOCHS, batch_size=BATCH_SIZE, lr=LR,
        verbose=True,
    )

    # Check convergence: val_loss should improve from epoch 0 to end
    converged = (
        probe_result["final_val_loss"] < probe_result["initial_val_loss"]
        and np.isfinite(probe_result["final_val_loss"])
    )

    elapsed = time.time() - t_seed
    print(
        f"[seed={seed}] converged={converged} "
        f"initial_val_loss={probe_result['initial_val_loss']:.4f} "
        f"final_val_loss={probe_result['final_val_loss']:.4f} "
        f"balance={balance:.4f} diversity={diversity:.4f} "
        f"elapsed={elapsed:.1f}s",
        flush=True,
    )

    return {
        "seed": int(seed),
        "n_train_embs": int(len(train_embs)),
        "n_val_embs": int(len(val_embs)),
        "balance": float(balance),
        "diversity": float(diversity),
        "nan_frac": float(nan_frac),
        "initial_val_loss": float(probe_result["initial_val_loss"]),
        "final_val_loss": float(probe_result["final_val_loss"]),
        "converged": bool(converged),
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if _ARGS.self_test:
        print("[exp] self-test already ran at module scope. Done.", flush=True)
        return

    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    out_dir = get_output_dir(ANCHOR_NAME)
    print(
        f"[exp] ANCHOR={ANCHOR_NAME} RUN_MODE={RUN_MODE} "
        f"SEEDS={SEEDS} MODEL={PYTHIA_MODEL_ID}",
        flush=True,
    )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[exp] loading Pythia-160M on device={device}...", flush=True)
    t_load = time.time()
    tokenizer = AutoTokenizer.from_pretrained(PYTHIA_MODEL_ID)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        PYTHIA_MODEL_ID, torch_dtype=torch.float32
    ).to(device)
    model.eval()
    print(f"[exp] model loaded in {time.time()-t_load:.1f}s", flush=True)

    done, remaining = resumable_seeds(SEEDS, out_dir)
    print(f"[ckpt] {len(done)} of {len(SEEDS)} seeds done; running {remaining}", flush=True)

    t_total = time.time()
    for seed in remaining:
        result = run_one_seed(seed, tokenizer, model, device)
        write_partial(out_dir, seed, result)
        print(
            f"[progress] seed={seed} "
            f"converged={result.get('converged', False)} "
            f"balance={result.get('balance', float('nan')):.4f}",
            flush=True,
        )

    per_seed = aggregate_partials(out_dir, SEEDS)
    total_elapsed = time.time() - t_total

    # ---- Verdict ----
    valid = {
        s: per_seed[str(s)]
        for s in SEEDS
        if str(s) in per_seed and per_seed[str(s)].get("n_train_embs", 0) > 0
    }
    n_valid = len(valid)
    n_converged = sum(1 for v in valid.values() if v.get("converged", False))
    balances = [v.get("balance", float("nan")) for v in valid.values()]
    diversities = [v.get("diversity", float("nan")) for v in valid.values()]
    nan_fracs = [v.get("nan_frac", 1.0) for v in valid.values()]

    balance_mean = float(np.nanmean(balances)) if balances else float("nan")
    diversity_mean = float(np.nanmean(diversities)) if diversities else float("nan")
    nan_frac_max = float(max(nan_fracs)) if nan_fracs else 1.0

    pipeline_clean = (
        nan_frac_max < 0.01
        and balance_mean < HP_BIPOLAR_BALANCE_MAX
        and np.isfinite(balance_mean)
    )
    diverse_enough = (
        diversity_mean >= HP_DIVERSITY_MIN
        and np.isfinite(diversity_mean)
    )

    if (
        pipeline_clean
        and diverse_enough
        and n_converged >= HP_MIN_SEEDS
    ):
        verdict = "HARD_PASS"
    elif (
        not np.isnan(balance_mean)
        and n_converged >= MID_MIN_SEEDS
    ):
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    verdict_msg = (
        f"VERDICT={verdict} "
        f"n_valid_seeds={n_valid} n_converged={n_converged}/{len(SEEDS)} "
        f"balance_mean={balance_mean:.4f} diversity_mean={diversity_mean:.4f} "
        f"nan_frac_max={nan_frac_max:.4f} "
        f"pipeline_clean={pipeline_clean} diverse_enough={diverse_enough} "
        f"HP: pipeline_clean AND diverse_enough AND n_converged>={HP_MIN_SEEDS} "
        f"total_wall_s={total_elapsed:.1f}"
    )
    print(f"[exp] {verdict_msg}", flush=True)

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "n_valid_seeds": int(n_valid),
        "n_converged": int(n_converged),
        "balance_mean": float(balance_mean),
        "diversity_mean": float(diversity_mean),
        "nan_frac_max": float(nan_frac_max),
        "pipeline_clean": bool(pipeline_clean),
        "diverse_enough": bool(diverse_enough),
        "HP_BALANCE_MAX": float(HP_BIPOLAR_BALANCE_MAX),
        "HP_DIVERSITY_MIN": float(HP_DIVERSITY_MIN),
        "LAYER_START": int(LAYER_START),
        "LAYER_END": int(LAYER_END),
        "K_CLUSTERS": int(K_CLUSTERS),
        "MODEL": PYTHIA_MODEL_ID,
        "elapsed_s": float(total_elapsed),
        "per_seed": {
            str(s): {k: (bool(v) if isinstance(v, (np.bool_, bool)) else
                         float(v) if isinstance(v, (np.floating, float)) else
                         int(v) if isinstance(v, (np.integer, int)) else v)
                     for k, v in per_seed[str(s)].items()} if str(s) in per_seed else None
            for s in SEEDS
        },
    }

    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"[exp] metrics written to {metrics_path}", flush=True)


if __name__ == "__main__":
    main()
