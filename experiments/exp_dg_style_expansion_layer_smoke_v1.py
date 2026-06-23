"""dg_style_expansion_layer_smoke_v1 -- substrate-native dentate-gyrus analog.

USER 2026-06-23 directional pushback on top-enabler concern 1.1:
"why don't we have an equivalent expansion layer?"

Brain DG: ~200k EC neurons -> ~1M DG granule cells (5x expansion); each granule
cell receives ~5 mossy-fiber inputs (K_sparse=5 -- cerebellar/DG fan-in
regime per Cayco-Gajic 2017 + Litwin-Kumar 2017); ~2-3% of DG cells fire
for any cue (sparse output). Net: similar inputs DECORRELATE via random
sparse projection + sparse output (canonical pattern separation; Marr 1971).

Tests whether sparse expansion projection (N=4096 -> N=16384) orthogonalizes
similar inputs the way brain DG does. Substrate CAN have an expansion layer
just hasn't been built; this cell is the first build.

4 arms (real WordSim353 words encoded via word2vec for clean external data):
  ARM_FLAT_N4096                 baseline; argmax in N=4096 (current substrate).
  ARM_DENSE_LIFT_N16384          lift via DENSE random gaussian projection
                                 W_dense [16384, 4096]; argmax in lifted space.
  ARM_DG_SPARSE_LIFT_N16384      lift via SPARSE projection W_DG [16384, 4096];
                                 K=5 nonzero bipolar entries per row (DG analog);
                                 argmax in lifted space.
  ARM_DG_SPARSE_LIFT_PLUS_KWTA   sparse lift + k-WTA top-2% output
                                 (full DG: sparse projection AND sparse output).

Metrics:
  (A) Cleanup recall@1 at each sigma per arm.
  (B) Pairwise orthogonality of encoded atom reps (mean abs cosine).
  (C) Effective dimensionality (participation ratio of singular spectrum).

Pre-reg HARD bands (preregs/2026-06-23_dg_style_expansion_layer_smoke_v1.md):
  HARD_PASS: ARM_DG_SPARSE_LIFT_PLUS_KWTA recall@sigma=1.5 >= 0.20
             AND mean_abs_cosine reduced by >= 30% vs ARM_FLAT_N4096.
  HARD_FAIL: ARM_DG arms recall@sigma=1.5 <= ARM_FLAT_N4096 + 0.02.
  MIDDLE_BAND: partial.

Sanity self-tests (block dispatch on FAIL):
  sigma=0 -> all arms recall=1.000.
  Identical-input duplicates -> identical hashes.
  W_DG shape (16384, 4096); each row K=5 nonzero entries in {-1, +1}.

CPU; numpy-only + gensim word2vec loader; ASCII; smoke ~10min wall.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial,
    aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "dg_style_expansion_layer_smoke_v1"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)
WORDSIM_CSV = REPO / "data" / "encoder_eval_benchmarks" / "wordsim353_combined.csv"
_LLM_CALL_COUNTER = [0]

# CLI
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_IS_SMOKE_BY_NAME = "_smoke" in _HDLAB_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _IS_SMOKE_BY_NAME) else os.environ.get("HDLAB_RUN_MODE", "smoke")

# Config (smoke == full for v1; this IS the smoke cell)
N_INPUT = 4096
N_EXPANDED = 16384
K_SPARSE = 5
PRETRAIN_DIM = 300
KWTA_FRAC = 0.02
M = 200
N_EVAL = 50
SIGMA_SWEEP = [0.0, 0.5, 1.0, 1.5, 2.0]
DISCRIMINATOR_SIGMA = 1.5
SEEDS = [7]

ARM_NAMES = [
    "ARM_FLAT_N4096",
    "ARM_DENSE_LIFT_N16384",
    "ARM_DG_SPARSE_LIFT_N16384",
    "ARM_DG_SPARSE_LIFT_PLUS_KWTA",
]

# Pre-reg bands
HP_RECALL = 0.20
HP_ORTHOGONALITY_REDUCTION = 0.30  # fraction reduction in mean_abs_cosine vs FLAT
HF_RECALL_GAP = 0.02
DISCRIMINATOR_SIGMA = 1.5

CONFIG_VERSION = (
    "dg_style_expansion_layer_smoke_v1; N_INPUT=%d N_EXPANDED=%d K_SPARSE=%d "
    "M=%d N_EVAL=%d KWTA_FRAC=%.3f sigmas=%s seeds=%s mode=%s; "
    "HP_recall>=%.2f HP_ortho_reduction>=%.2f HF_recall_gap<=%.3f"
) % (N_INPUT, N_EXPANDED, K_SPARSE, M, N_EVAL, KWTA_FRAC, SIGMA_SWEEP, SEEDS,
     RUN_MODE, HP_RECALL, HP_ORTHOGONALITY_REDUCTION, HF_RECALL_GAP)


# ============================================================================
# Vocabulary: load WordSim353 (real external words; no substrate label leak)
# ============================================================================

def load_wordsim_vocab(csv_path: Path, cap: int) -> List[str]:
    """Read WordSim353 pairs; return up to `cap` unique words (preserving order)."""
    if not csv_path.exists():
        raise FileNotFoundError("WordSim353 csv missing at %s" % csv_path)
    seen: Dict[str, None] = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # header
        for row in reader:
            if len(row) < 2:
                continue
            for w in (row[0].strip(), row[1].strip()):
                if w and w not in seen:
                    seen[w] = None
                    if len(seen) >= cap:
                        return list(seen.keys())
    return list(seen.keys())


# ============================================================================
# word2vec loader (gensim)
# ============================================================================

_GENSIM_KV_CACHE: Dict[str, object] = {}


def _load_w2v():
    """Load word2vec-google-news-300 (cached in-process)."""
    name = "word2vec-google-news-300"
    if name in _GENSIM_KV_CACHE:
        return _GENSIM_KV_CACHE[name]
    import gensim.downloader as gd
    try:
        gd.base_dir = GENSIM_CACHE_DIR
        gd.BASE_DIR = GENSIM_CACHE_DIR
    except Exception:
        pass
    kv = gd.load(name)
    _GENSIM_KV_CACHE[name] = kv
    return kv


def _embed_via_w2v(vocab: List[str], kv) -> Tuple[np.ndarray, int, int]:
    """Look up each vocab word in word2vec; zero-vector on OOV (rare for WordSim353)."""
    dim = kv.vector_size
    V = len(vocab)
    out = np.zeros((V, dim), dtype=np.float32)
    n_hit = 0
    n_miss = 0
    for i, w in enumerate(vocab):
        v = None
        if w in kv.key_to_index:
            v = kv[w]
        elif w.lower() in kv.key_to_index:
            v = kv[w.lower()]
        if v is None:
            n_miss += 1
        else:
            n_hit += 1
            out[i] = v.astype(np.float32)
    return out, n_hit, n_miss


def _gaussian_projection(out_dim: int, in_dim: int, seed: int) -> np.ndarray:
    """JL-scaled gaussian random projection P [out_dim, in_dim]."""
    rng = np.random.default_rng(seed * 991 + 73)
    P = rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))
    return P


def _l2_normalize(X, eps=1e-12):
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


# ============================================================================
# DG-style sparse projection (K nonzero bipolar entries per row)
# ============================================================================

def make_W_DG(n_expanded: int, n_input: int, k_sparse: int,
              seed: int) -> np.ndarray:
    """Sparse projection W_DG [n_expanded, n_input]; each row has exactly
    k_sparse nonzero entries at random positions, +/-1 bipolar.

    Cerebellar/DG fan-in regime (Cayco-Gajic 2017; Litwin-Kumar 2017).
    """
    rng = np.random.default_rng(seed * 1009 + 41)
    W = np.zeros((n_expanded, n_input), dtype=np.float32)
    for r in range(n_expanded):
        positions = rng.choice(n_input, size=k_sparse, replace=False)
        signs = rng.integers(0, 2, size=k_sparse).astype(np.float32) * 2.0 - 1.0
        W[r, positions] = signs
    return W


def kwta_top_frac(X: np.ndarray, frac: float) -> np.ndarray:
    """k-WTA: keep top `frac` of entries per row by magnitude; zero rest.
    Works on 1d or 2d; returns same-shape dense array (sparse pattern).
    """
    if X.ndim == 1:
        n = X.shape[0]
        k = max(1, int(round(frac * n)))
        if k >= n:
            return X.copy()
        idx_top = np.argpartition(np.abs(X), n - k)[n - k:]
        out = np.zeros_like(X)
        out[idx_top] = X[idx_top]
        return out
    # 2d row-wise
    M_rows, n = X.shape
    k = max(1, int(round(frac * n)))
    if k >= n:
        return X.copy()
    out = np.zeros_like(X)
    # vectorized argpartition per row
    idx_part = np.argpartition(np.abs(X), n - k, axis=1)[:, n - k:]
    rows = np.arange(M_rows)[:, None]
    out[rows, idx_part] = X[rows, idx_part]
    return out


# ============================================================================
# Per-arm encoding: vocab_embeddings_n_input [M, N_INPUT] -> arm_reps [M, dim]
# ============================================================================

def encode_for_arm(arm: str, X_in: np.ndarray, seed: int) -> np.ndarray:
    """Take [M, N_INPUT] dense bipolar-ish reps; project to arm's space.

    ARM_FLAT_N4096:                   identity (return X_in unchanged).
    ARM_DENSE_LIFT_N16384:            X_in @ W_dense.T  ([N_EXPANDED, N_INPUT])
    ARM_DG_SPARSE_LIFT_N16384:        X_in @ W_DG.T     (K=5 nonzero rows)
    ARM_DG_SPARSE_LIFT_PLUS_KWTA:     kwta(X_in @ W_DG.T, KWTA_FRAC)
    """
    if arm == "ARM_FLAT_N4096":
        return X_in.astype(np.float32, copy=True)
    if arm == "ARM_DENSE_LIFT_N16384":
        W_dense = _gaussian_projection(N_EXPANDED, N_INPUT, seed)
        return (X_in @ W_dense.T).astype(np.float32)
    # Sparse lift arms (shared W_DG within seed)
    W_DG = make_W_DG(N_EXPANDED, N_INPUT, K_SPARSE, seed)
    lifted = (X_in @ W_DG.T).astype(np.float32)
    if arm == "ARM_DG_SPARSE_LIFT_N16384":
        return lifted
    if arm == "ARM_DG_SPARSE_LIFT_PLUS_KWTA":
        return kwta_top_frac(lifted, KWTA_FRAC)
    raise ValueError("unknown arm: %s" % arm)


# ============================================================================
# Cleanup recall (argmax in arm's space; noise added in N_INPUT space then
# projected -- mimics noisy cue arriving at substrate and being lifted)
# ============================================================================

def cleanup_recall(arm: str, X_in: np.ndarray, arm_reps: np.ndarray,
                   sigma: float, n_eval: int, seed: int) -> float:
    """Sample n_eval atoms; add gaussian noise to their N_INPUT-space cue;
    re-project via the arm's encoding pipeline; argmax against arm_reps."""
    rng = np.random.default_rng(seed * 7919 + int(sigma * 1000) + hash(arm) % 9973)
    M_total = X_in.shape[0]
    n_eval = min(n_eval, M_total)
    idxs = rng.choice(M_total, size=n_eval, replace=False)
    cues_in = X_in[idxs].copy()
    if sigma > 0:
        noise = rng.normal(0.0, sigma, size=cues_in.shape).astype(np.float32)
        cues_in = cues_in + noise
    # Re-encode noisy cue through the same arm pipeline (deterministic per seed)
    cues_arm = encode_for_arm(arm, cues_in, seed)
    sims = cues_arm @ arm_reps.T
    preds = sims.argmax(axis=1)
    return float(np.sum(preds == idxs) / n_eval)


# ============================================================================
# Orthogonality + effective dimensionality
# ============================================================================

def pairwise_mean_abs_cosine(X: np.ndarray, max_pairs: int = 50_000,
                             rng_seed: int = 0) -> float:
    """Mean |cos| across atom pairs. Subsample if M*(M-1)/2 > max_pairs."""
    Xn = _l2_normalize(X.astype(np.float32))
    M_rows = Xn.shape[0]
    sims = Xn @ Xn.T  # [M, M]
    # take upper-triangle off-diagonal
    iu, ju = np.triu_indices(M_rows, k=1)
    vals = np.abs(sims[iu, ju])
    if vals.size > max_pairs:
        rng = np.random.default_rng(rng_seed)
        idx = rng.choice(vals.size, size=max_pairs, replace=False)
        vals = vals[idx]
    return float(np.mean(vals))


def participation_ratio(X: np.ndarray) -> float:
    """Effective dimensionality: (sum s_i)^2 / sum(s_i^2).
    Computed on centered rows. Higher = atoms span more dimensions."""
    Xc = X.astype(np.float32) - X.mean(axis=0, keepdims=True)
    # Avoid full SVD on huge matrices: use s from SVD of Xc (limited to min dim)
    # SciPy not assumed; use numpy linalg.svd compute_uv=False
    s = np.linalg.svd(Xc, compute_uv=False)
    if s.size == 0:
        return 0.0
    num = float(np.sum(s)) ** 2
    den = float(np.sum(s * s)) + 1e-12
    return num / den


# ============================================================================
# Self-tests (block dispatch on failure)
# ============================================================================

def _selftest():
    # 1) W_DG shape and K-sparsity
    W = make_W_DG(64, 32, 5, seed=0)
    assert W.shape == (64, 32), "W_DG shape mismatch: %s" % (W.shape,)
    for r in range(W.shape[0]):
        nz = np.nonzero(W[r])[0]
        assert nz.size == 5, "row %d has %d nonzero (expected 5)" % (r, nz.size)
        vals = W[r, nz]
        assert set(vals.tolist()).issubset({-1.0, 1.0}), "non-bipolar value in row %d" % r

    # 2) kwta keeps top frac
    x = np.array([0.1, 0.9, 0.5, 0.05, 0.7], dtype=np.float32)
    out = kwta_top_frac(x, 0.4)  # keep top 2 of 5
    nz = np.nonzero(out)[0]
    assert nz.size == 2 and set(nz.tolist()) == {1, 4}, "kwta wrong: nz=%s" % nz.tolist()

    # 3) sigma=0 endpoint per arm: recall == 1.000
    # use small synthetic X_in (no w2v) for fast selftest
    rng = np.random.default_rng(0)
    X_test = (rng.integers(0, 2, size=(20, N_INPUT)) * 2 - 1).astype(np.float32)
    X_test = _l2_normalize(X_test)
    for arm in ARM_NAMES:
        reps = encode_for_arm(arm, X_test, seed=0)
        r = cleanup_recall(arm, X_test, reps, sigma=0.0, n_eval=10, seed=0)
        assert r == 1.0, "[selftest] arm=%s sigma=0 recall=%.3f (expected 1.000)" % (arm, r)

    # 4) Determinism: identical input -> identical output for fixed seed
    a = encode_for_arm("ARM_DG_SPARSE_LIFT_N16384", X_test[:3], seed=0)
    b = encode_for_arm("ARM_DG_SPARSE_LIFT_N16384", X_test[:3], seed=0)
    assert np.array_equal(a, b), "[selftest] non-deterministic encoding for fixed seed"

    # 5) kWTA produces sparse output: fraction nonzero ~= KWTA_FRAC
    lifted_test = encode_for_arm("ARM_DG_SPARSE_LIFT_N16384", X_test[:5], seed=0)
    sparse_out = kwta_top_frac(lifted_test, KWTA_FRAC)
    frac_nz = float(np.mean(np.abs(sparse_out) > 0))
    expected = KWTA_FRAC
    assert abs(frac_nz - expected) < 0.02, "[selftest] kWTA frac=%.4f expected~%.4f" % (frac_nz, expected)

    print("[selftest] PASS: W_DG shape+K-sparsity + kwta + sigma=0-endpoint(4 arms) + "
          "determinism + kWTA-output-sparsity", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Main run
# ============================================================================

def run_one_seed(seed: int) -> dict:
    t0 = time.time()
    print("[%s] seed=%d start: loading word2vec + WordSim353 vocab"
          % (ANCHOR_NAME, seed), flush=True)

    # Load vocab + word2vec embeddings
    vocab = load_wordsim_vocab(WORDSIM_CSV, cap=M)
    if len(vocab) < M:
        print("[%s] WARN: vocab size %d < requested M=%d; running with %d"
              % (ANCHOR_NAME, len(vocab), M, len(vocab)), flush=True)
    M_eff = len(vocab)
    kv = _load_w2v()
    emb_300, n_hit, n_miss = _embed_via_w2v(vocab, kv)
    print("[%s] seed=%d w2v lookup: %d hit / %d miss"
          % (ANCHOR_NAME, seed, n_hit, n_miss), flush=True)

    # Project 300d -> N_INPUT=4096 via per-seed gaussian projection
    P_300_to_input = _gaussian_projection(N_INPUT, PRETRAIN_DIM, seed)
    X_input_raw = emb_300 @ P_300_to_input.T  # [M_eff, N_INPUT]
    # L2-normalize so noise sigma has consistent semantics across atoms
    X_input = _l2_normalize(X_input_raw)
    print("[%s] seed=%d X_input shape=%s norm=%.3f"
          % (ANCHOR_NAME, seed, X_input.shape,
             float(np.linalg.norm(X_input[0]))), flush=True)

    # Per-arm metrics
    arm_results: Dict[str, dict] = {}
    for arm in ARM_NAMES:
        arm_t0 = time.time()
        print("[%s] seed=%d arm=%s encoding"
              % (ANCHOR_NAME, seed, arm), flush=True)
        reps = encode_for_arm(arm, X_input, seed)
        # Free intermediate memory hint for dense arm (W_dense is 16384*4096*4=256MB)
        encode_elapsed = time.time() - arm_t0

        # (A) Cleanup recall sweep
        recall_by_sigma: Dict[str, float] = {}
        for sigma in SIGMA_SWEEP:
            r = cleanup_recall(arm, X_input, reps, sigma, N_EVAL, seed)
            recall_by_sigma["sigma_%.1f" % sigma] = float(r)

        # (B) Pairwise orthogonality
        mac = pairwise_mean_abs_cosine(reps, rng_seed=seed)

        # (C) Effective dimensionality (participation ratio of singular spectrum)
        # cap M for SVD cost: use full M_eff (200 atoms; SVD is fast even at 16384 dim)
        pr = participation_ratio(reps)

        arm_elapsed = time.time() - arm_t0
        arm_results[arm] = {
            "recall_by_sigma": recall_by_sigma,
            "recall_at_disc_sigma": recall_by_sigma["sigma_%.1f" % DISCRIMINATOR_SIGMA],
            "mean_abs_cosine": float(mac),
            "participation_ratio": float(pr),
            "rep_dim": int(reps.shape[1]),
            "encode_elapsed_s": float(encode_elapsed),
            "arm_elapsed_s": float(arm_elapsed),
        }
        print(
            "[%s] seed=%d arm=%s done: rep_dim=%d recall@s%.1f=%.3f mac=%.4f "
            "PR=%.1f (%.1fs)"
            % (ANCHOR_NAME, seed, arm, reps.shape[1], DISCRIMINATOR_SIGMA,
               recall_by_sigma["sigma_%.1f" % DISCRIMINATOR_SIGMA], mac, pr, arm_elapsed),
            flush=True,
        )
        # explicit free of reps before next arm to keep peak memory low
        del reps

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_INPUT,
        "M": M_eff,
        "run_mode": RUN_MODE,
        "vocab_size": M_eff,
        "w2v_hit": int(n_hit),
        "w2v_miss": int(n_miss),
        "arms": arm_results,
        "elapsed_s": float(elapsed),
    }


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("[%s] start mode=%s seeds=%s N_INPUT=%d N_EXPANDED=%d K_SPARSE=%d M=%d arms=%d"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_INPUT, N_EXPANDED, K_SPARSE, M, len(ARM_NAMES)),
          flush=True)

    run_config = {"N": N_INPUT, "M": M, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[%s] ckpt: %d done; running %d"
          % (ANCHOR_NAME, len(done), len(remaining)), flush=True)

    for seed in remaining:
        result = run_one_seed(seed)
        write_partial(out_dir, seed, result)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)

    # Aggregate across seeds: per-arm mean recall@disc_sigma + mac + PR
    per_arm_summary: Dict[str, dict] = {}
    for arm in ARM_NAMES:
        recalls = [per_seed[str(s)]["arms"][arm]["recall_at_disc_sigma"] for s in SEEDS]
        macs = [per_seed[str(s)]["arms"][arm]["mean_abs_cosine"] for s in SEEDS]
        prs = [per_seed[str(s)]["arms"][arm]["participation_ratio"] for s in SEEDS]
        per_arm_summary[arm] = {
            "recall_at_disc_sigma_mean": float(np.mean(recalls)),
            "recall_at_disc_sigma_std": float(np.std(recalls)),
            "mean_abs_cosine_mean": float(np.mean(macs)),
            "participation_ratio_mean": float(np.mean(prs)),
            "rep_dim": int(per_seed[str(SEEDS[0])]["arms"][arm]["rep_dim"]),
        }

    flat = per_arm_summary["ARM_FLAT_N4096"]
    dg_sparse = per_arm_summary["ARM_DG_SPARSE_LIFT_N16384"]
    dg_kwta = per_arm_summary["ARM_DG_SPARSE_LIFT_PLUS_KWTA"]

    # HP gates
    hp_recall_ok = dg_kwta["recall_at_disc_sigma_mean"] >= HP_RECALL
    # mac reduction = (flat_mac - dg_kwta_mac) / flat_mac
    flat_mac = max(flat["mean_abs_cosine_mean"], 1e-9)
    mac_reduction = (flat_mac - dg_kwta["mean_abs_cosine_mean"]) / flat_mac
    hp_ortho_ok = mac_reduction >= HP_ORTHOGONALITY_REDUCTION

    # HF gates
    hf_recall_dg_sparse = (dg_sparse["recall_at_disc_sigma_mean"]
                           <= flat["recall_at_disc_sigma_mean"] + HF_RECALL_GAP)
    hf_recall_dg_kwta = (dg_kwta["recall_at_disc_sigma_mean"]
                         <= flat["recall_at_disc_sigma_mean"] + HF_RECALL_GAP)
    hf_recall = hf_recall_dg_sparse and hf_recall_dg_kwta

    # Endpoint sanity: sigma=0 recall=1.000 for ALL arms across ALL seeds
    endpoint_ok = True
    for arm in ARM_NAMES:
        rs = [per_seed[str(s)]["arms"][arm]["recall_by_sigma"]["sigma_0.0"] for s in SEEDS]
        if not all(r == 1.0 for r in rs):
            endpoint_ok = False

    if not endpoint_ok:
        verdict = "HARD_FAIL"
        verdict_extra = "_ENDPOINT_VIOLATION"
    elif hp_recall_ok and hp_ortho_ok:
        verdict = "HARD_PASS"
        verdict_extra = ""
    elif hf_recall:
        verdict = "HARD_FAIL"
        verdict_extra = ""
    else:
        verdict = "MIDDLE_BAND"
        verdict_extra = ""

    elapsed_s = float(sum(per_seed[str(s)]["elapsed_s"] for s in SEEDS))

    verdict_msg = (
        "%s%s_%s_%dseeds_NIN%d_NEXP%d_K%d_M%d_"
        "FLAT_recall%.3f_mac%.4f_PR%.1f_"
        "DENSE_recall%.3f_mac%.4f_PR%.1f_"
        "DGSP_recall%.3f_mac%.4f_PR%.1f_"
        "DGKWTA_recall%.3f_mac%.4f_PR%.1f_"
        "mac_reduction=%.3f_HPrecall=%s_HPortho=%s_endpoint=%s_elapsed_%.1fs"
    ) % (
        verdict, verdict_extra, RUN_MODE.upper(), len(SEEDS),
        N_INPUT, N_EXPANDED, K_SPARSE, M,
        flat["recall_at_disc_sigma_mean"], flat["mean_abs_cosine_mean"], flat["participation_ratio_mean"],
        per_arm_summary["ARM_DENSE_LIFT_N16384"]["recall_at_disc_sigma_mean"],
        per_arm_summary["ARM_DENSE_LIFT_N16384"]["mean_abs_cosine_mean"],
        per_arm_summary["ARM_DENSE_LIFT_N16384"]["participation_ratio_mean"],
        dg_sparse["recall_at_disc_sigma_mean"], dg_sparse["mean_abs_cosine_mean"], dg_sparse["participation_ratio_mean"],
        dg_kwta["recall_at_disc_sigma_mean"], dg_kwta["mean_abs_cosine_mean"], dg_kwta["participation_ratio_mean"],
        mac_reduction, hp_recall_ok, hp_ortho_ok, endpoint_ok, elapsed_s,
    )

    summary = {
        "anchor": ANCHOR_NAME,
        "config_version": CONFIG_VERSION,
        "run_mode": RUN_MODE,
        "seeds": SEEDS,
        "N_INPUT": N_INPUT,
        "N_EXPANDED": N_EXPANDED,
        "K_SPARSE": K_SPARSE,
        "M": M,
        "N_EVAL": N_EVAL,
        "KWTA_FRAC": KWTA_FRAC,
        "SIGMA_SWEEP": SIGMA_SWEEP,
        "DISCRIMINATOR_SIGMA": DISCRIMINATOR_SIGMA,
        "arms": per_arm_summary,
        "hp_gates": {
            "hp_recall_ok": hp_recall_ok,
            "hp_ortho_ok": hp_ortho_ok,
            "endpoint_ok": endpoint_ok,
            "hp_recall_floor": HP_RECALL,
            "hp_orthogonality_reduction_floor": HP_ORTHOGONALITY_REDUCTION,
            "mac_reduction_actual": float(mac_reduction),
        },
        "hf_gates": {
            "hf_recall_dg_sparse": hf_recall_dg_sparse,
            "hf_recall_dg_kwta": hf_recall_dg_kwta,
            "hf_recall_gap": HF_RECALL_GAP,
        },
    }

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed_s,
        "n_llm_calls": _LLM_CALL_COUNTER[0],
        "summary": summary,
        "per_seed": per_seed,
    }

    write_metrics(out_dir, metrics)
    print("[%s] %s" % (ANCHOR_NAME, verdict_msg), flush=True)


if __name__ == "__main__":
    main()
