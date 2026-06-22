"""c_composition_storage_density_v1 -- COMPOUND storage-density cell.

USER 2026-06-22: 'How dense is storage now, how far can we push that?'

Substrate single-mechanism chain-grade at n8 (ConceptNet 100k facts, 67MB W matrix). Brain-drills
and cell-pipelines surfaced 4+ capacity-lifting mechanisms one by one. This cell stacks them
to measure the COMPOUND effect on storage density.

Mechanisms composed (5 arms):
  Arm 1 (BASELINE):     plain multi-value Hebbian (= n8 mechanism unchanged)
  Arm 2 (+ MODULAR):    Arm 1 + K=8 macrocolumn content-routed (m1 lineage)
  Arm 3 (+ WHITENING):  Arm 1 + ZCA whitening on encoded keys before Hebbian write (n10 lineage)
  Arm 4 (+ KWTA):       Arm 1 + k-WTA sparse readout (k=20 winners on recall scores; n4 lineage)
  Arm 5 (COMBINED):     Arm 1 + MODULAR + WHITENING + KWTA stacked

Synthetic-bipolar KG (no encoder; structural test only):
  - Random entity codebook (bipolar +-1)
  - Multi-value (each (s, p) -> 1-10 objects, mirrors n8 1-to-many fraction ~24%)
  - M_grid sweeps the capacity curve

Pre-reg HARD bands (per notes/c_composition_storage_density_v1_pre_reg_2026-06-22.md):
  Define M_fail(arm) = smallest M where setrecall_all < 0.95 for that arm.
  Compound lift L = M_fail(Arm 5) / M_fail(Arm 1).

  HARD_PASS:    L >= 5.0 AND substrate-only-decode preserved AND cv <= 0.10
                AND Arm 1 reproduces n8 chain-grade pattern at M=10k (sanity)
  HARD_FAIL:    L <= 1.5 (compound mechanisms don't compose)
  MIDDLE_BAND:  1.5 < L < 5.0 (partial; characterize which pair load-bears)

Discriminator regime (Fix #16): Arm 1 at M=10k MUST hit setrecall@10k >= 0.90 (n8 pattern).
If not, harness is broken.

CPU; ASCII; pure numpy; per-seed checkpoint.
"""
from __future__ import annotations
import sys, os, argparse, time, math, json
from pathlib import Path
from collections import defaultdict
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "c_composition_storage_density_v1"
_LLM_CALL_COUNTER = [0]  # pure numpy; substrate-only by construction

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()


def _detect_run_mode():
    """TODO #6 pattern: --smoke CLI > HDLAB_RUN_MODE env > HDLAB_EXP_NAME ends-with _smoke > full."""
    if _ARGS.smoke or _ARGS.self_test:
        return "smoke"
    env_mode = os.environ.get("HDLAB_RUN_MODE", "").lower()
    if env_mode in ("smoke", "full"):
        return env_mode
    exp_name = os.environ.get("HDLAB_EXP_NAME", "")
    if exp_name.lower().endswith("_smoke"):
        return "smoke"
    return "full"


RUN_MODE = _detect_run_mode()

# Config - fixed dimensions; mechanism arms vary
N_DIM = 4096                    # matches n8 baseline
V_C = 1024                      # entity codebook size (small slice; many M-shuffles per seed)
N_REL = 8                       # mirrors ConceptNet (n8 had 8 relation types)
MAX_OBJ_PER_KEY = 5             # multi-value cap (small to control eval set-size variance)
K_MOD = 8                       # modular macrocolumn count (m1 K=8 default)
M_TOP = 2                       # Top-m softmax over macrocolumn shards (m1 default)
KWTA_K = 20                     # k-WTA sparse readout: top-k winners
ZCA_EPS = 1e-3                  # ZCA shrinkage

# Per-M entity-pool sizing: keep V_proj cost proportional to M (n8 had ~ M/4 entities)
# n_ent_pool(M) = min(MAX_ENT_POOL, max(MIN_ENT_POOL, M * ENT_POOL_MULT))
MIN_ENT_POOL = 1000
MAX_ENT_POOL = 25000
ENT_POOL_MULT = 1.5             # roughly mirrors n8's ent-density (M=100k -> n_ent ~ 25k)

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    # v1 M_GRID: keeps discriminator at M=10k (Fix #16 sanity); defers M=100k+ to v2 per spawn prompt.
    M_GRID = [1000, 5000, 10000, 25000]
    N_EVAL = 300                # per-(arm, M) eval keys
else:
    # Smoke: 1 seed, 2 small M points; designed to complete in <8min (harness check + per-arm sanity)
    SEEDS = [1]
    M_GRID = [500, 2000]
    N_EVAL = 60

ARMS = ["baseline", "modular", "whitening", "kwta", "combined"]

# Pre-reg bands
SETRECALL_FLOOR = 0.95          # M_fail = smallest M where setrecall_all drops below this
HARD_PASS_LIFT = 5.0            # compound lift L >= this -> HARD_PASS
HARD_FAIL_LIFT = 1.5            # L <= this -> HARD_FAIL
DISCRIM_M = 10000               # sanity check: Arm 1 at this M
DISCRIM_RECALL = 0.90           # Arm 1 setrecall@DISCRIM_M floor (Fix #16)

CONFIG_VERSION = (
    "c_compose_v1: N_DIM=%d V_C=%d N_REL=%d M_grid=%s K_MOD=%d KWTA_K=%d ZCA_EPS=%.4f "
    "MAX_OBJ=%d N_EVAL=%d ENT_POOL_MULT=%.1f MIN_POOL=%d MAX_POOL=%d "
    "seeds=%s arms=%s SR_FLOOR=%.2f LIFT_PASS=%.1f LIFT_FAIL=%.1f"
) % (N_DIM, V_C, N_REL, M_GRID, K_MOD, KWTA_K, ZCA_EPS, MAX_OBJ_PER_KEY, N_EVAL,
     ENT_POOL_MULT, MIN_ENT_POOL, MAX_ENT_POOL,
     SEEDS, ARMS, SETRECALL_FLOOR, HARD_PASS_LIFT, HARD_FAIL_LIFT)


def _n_ent_pool_for_M(M: int) -> int:
    """Per-M entity-pool size: keeps V_proj + entity-codebook costs proportional to M."""
    return min(MAX_ENT_POOL, max(MIN_ENT_POOL, int(M * ENT_POOL_MULT)))


# ---------------------------------------------------------------------------
# Substrate primitives
# ---------------------------------------------------------------------------

def bipolar(n_vec: int, dim: int, rng: np.random.Generator) -> np.ndarray:
    """Synthetic bipolar +-1 / sqrt(dim) HVs."""
    X = (rng.integers(0, 2, size=(n_vec, dim)).astype(np.float32) * 2.0 - 1.0)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def make_synthetic_kg(M: int, n_ent_pool: int, n_rel: int, max_obj: int, rng: np.random.Generator):
    """Build a synthetic KG of M (s, p, o) triples grouped into (s, p) -> [o, o, ...] multi-value keys.

    Returns (triples list, keyobjs dict (s, p) -> sorted obj list, n_ent_used, n_rel_used).
    """
    keyobjs = defaultdict(set)
    triples = []
    tries = 0
    max_tries = M * 50
    while len(triples) < M and tries < max_tries:
        s = int(rng.integers(0, n_ent_pool))
        p = int(rng.integers(0, n_rel))
        # multi-value: 1 to max_obj objects per (s, p)
        k_obj = 1 + int(rng.integers(0, max_obj))
        for _ in range(k_obj):
            o = int(rng.integers(0, n_ent_pool))
            if o == s:
                continue
            if o in keyobjs[(s, p)]:
                continue
            keyobjs[(s, p)].add(o)
            triples.append((s, p, o))
            if len(triples) >= M:
                break
        tries += 1
    keyobjs_sorted = {k: sorted(v) for k, v in keyobjs.items()}
    n_ent_used = len({t[0] for t in triples} | {t[2] for t in triples})
    n_rel_used = len({t[1] for t in triples})
    return triples, keyobjs_sorted, n_ent_used, n_rel_used


def ingest_baseline(triples, n_ent_pool: int, n_rel: int, E: np.ndarray, R: np.ndarray,
                    sq: float, key_transform=None, batch: int = 5000) -> np.ndarray:
    """Multi-value Hebbian: W += outer(E[o_i], key_i) / N over all triples (chunked BLAS).

    key_transform: optional callable applied to the (B, N_DIM) key matrix BEFORE Hebbian.
    Used to inject whitening into the same code path without duplicating the ingest loop.
    """
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        if key_transform is not None:
            ks = key_transform(ks)
        W += (E[o_idx[b:b + batch]].T @ ks) / N_DIM
    return W


def fit_zca(keys: np.ndarray, eps: float = ZCA_EPS):
    """Fit ZCA whitening on a sample of keys. Returns (mean, W_zca) for transform.

    Substrate-native: pure numpy svd; no LLM forward call.
    """
    mean = keys.mean(axis=0)
    Kc = keys - mean
    cov = (Kc.T @ Kc) / max(len(keys), 1)
    U, S, _ = np.linalg.svd(cov)
    W_zca = U @ np.diag(1.0 / np.sqrt(S + eps)) @ U.T
    return mean.astype(np.float32), W_zca.astype(np.float32)


def apply_zca(keys: np.ndarray, mean: np.ndarray, W_zca: np.ndarray) -> np.ndarray:
    """Apply ZCA whitening to a key matrix."""
    return ((keys - mean) @ W_zca).astype(np.float32)


def kwta_topk(scores: np.ndarray, k: int) -> np.ndarray:
    """k-WTA sparse readout: keep top-k scores, zero the rest.

    Substrate-native: argmax / argpartition only; no LLM call.
    Returns same-shape array.
    """
    if k >= scores.shape[-1]:
        return scores
    out = np.zeros_like(scores)
    if scores.ndim == 1:
        idx = np.argpartition(scores, -k)[-k:]
        out[idx] = scores[idx]
    else:
        idx = np.argpartition(scores, -k, axis=-1)[..., -k:]
        np.put_along_axis(out, idx, np.take_along_axis(scores, idx, axis=-1), axis=-1)
    return out


# ---------------------------------------------------------------------------
# Modular K-macrocolumn (m1 lineage)
# ---------------------------------------------------------------------------

def _per_shard_dim(K: int, n_dim_total: int = N_DIM) -> int:
    """N_per such that K * N_per^2 ~= n_dim_total^2 (fixed parameter budget)."""
    total_p = n_dim_total * n_dim_total
    return max(1, int(round(math.sqrt(total_p / K))))


def modular_ingest(triples, E: np.ndarray, R: np.ndarray, sq: float, K: int,
                   rng: np.random.Generator, whitening_fit=None):
    """Modular K-macrocolumn Hebbian ingest with content-router top-m softmax.

    VECTORIZED: gather items routed to the same shard into a batch outer-product
    (~150x faster than per-item loop at M>=10k).

    whitening_fit: optional (mean, W_zca) tuple to whiten keys before shard projection.

    Returns (Ws list of (n_per, n_per) per shard, shard_projs (K, n_per, N_DIM),
             macrocol_keys_norm (K, N_DIM)).
    """
    n_per = _per_shard_dim(K)
    macrocol_keys = (rng.integers(0, 2, size=(K, N_DIM)).astype(np.float32) * 2.0 - 1.0)
    macrocol_keys_norm = macrocol_keys / (np.linalg.norm(macrocol_keys, axis=1, keepdims=True) + 1e-12)
    shard_projs = rng.standard_normal((K, n_per, N_DIM)).astype(np.float32) * (1.0 / math.sqrt(N_DIM))
    Ws = [np.zeros((n_per, n_per), dtype=np.float32) for _ in range(K)]

    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    m_eff = min(M_TOP, K)
    batch = 5000  # chunk to bound peak memory while keeping BLAS efficient
    for b in range(0, len(tr), batch):
        sb = s_idx[b:b + batch]; pb = p_idx[b:b + batch]; ob = o_idx[b:b + batch]
        keys = (E[sb] * R[pb] * sq).astype(np.float32)            # (B, N_DIM)
        vals = E[ob].astype(np.float32)                            # (B, N_DIM)
        if whitening_fit is not None:
            keys = apply_zca(keys, whitening_fit[0], whitening_fit[1])
        B = len(keys)
        # Content router: (B, K) similarity
        keys_norm = keys / (np.linalg.norm(keys, axis=1, keepdims=True) + 1e-12)
        sims = keys_norm @ macrocol_keys_norm.T                    # (B, K)
        # Vectorized top-m: argpartition along axis=-1 then softmax over top-m only
        if m_eff < K:
            top_idx = np.argpartition(-sims, m_eff - 1, axis=-1)[:, :m_eff]    # (B, m_eff)
        else:
            top_idx = np.broadcast_to(np.arange(K)[None, :], (B, K)).copy()
        top_sims = np.take_along_axis(sims, top_idx, axis=-1)                  # (B, m_eff)
        # softmax over top-m
        top_sims_n = top_sims - top_sims.max(axis=-1, keepdims=True)
        e_top = np.exp(top_sims_n); w_top = e_top / (e_top.sum(axis=-1, keepdims=True) + 1e-12)  # (B, m_eff)
        # For each (j in [0..m_eff)), accumulate the per-shard outer-products in batch
        # by gathering items routed to shard k_idx with weight w_top[:, j].
        for j in range(m_eff):
            k_for_items = top_idx[:, j]      # (B,) shard index per item for this top-m slot
            w_for_items = w_top[:, j]        # (B,) softmax weight per item
            # Per-shard batched outer-product accumulation
            for k_idx in range(K):
                mask = (k_for_items == k_idx)
                if not mask.any():
                    continue
                idxs = np.nonzero(mask)[0]
                # Project keys + vals into shard subspace (batched matmul)
                # shard_projs[k_idx]: (n_per, N_DIM)
                ks_sub = keys[idxs] @ shard_projs[k_idx].T            # (n_sel, n_per)
                vs_sub = vals[idxs] @ shard_projs[k_idx].T            # (n_sel, n_per)
                # Weighted outer-product accumulate: sum_n w_n * outer(v_n, k_n) = V.T @ diag(w) @ K
                # Equivalent vectorized: (V * w[:, None]).T @ K
                w_sel = w_for_items[idxs][:, None].astype(np.float32)
                Ws[k_idx] += (vs_sub * w_sel).T @ ks_sub / n_per
    return Ws, shard_projs, macrocol_keys_norm


def modular_score(sp_pairs, E: np.ndarray, R: np.ndarray, sq: float, Ws, shard_projs,
                  macrocol_keys_norm, n_ent_pool: int, whitening_fit=None):
    """Score (s, p) queries through modular shards; returns (n_q, n_ent_pool) score matrix
    via per-shard subspace cleanup + top-m weighted aggregation.
    """
    K = len(Ws)
    n_per = Ws[0].shape[0]
    m_eff = min(M_TOP, K)
    # Build per-shard projected entity codebook (one-time per call)
    V_proj = np.empty((K, n_ent_pool, n_per), dtype=np.float32)
    for k_idx in range(K):
        V_proj[k_idx] = E @ shard_projs[k_idx].T   # (n_ent_pool, n_per)
    V_proj_norm = V_proj / (np.linalg.norm(V_proj, axis=2, keepdims=True) + 1e-12)
    n_q = len(sp_pairs)
    scores_out = np.zeros((n_q, n_ent_pool), dtype=np.float32)
    for qi, (s, p) in enumerate(sp_pairs):
        key = (E[s] * R[p] * sq).astype(np.float32)
        if whitening_fit is not None:
            key = apply_zca(key[None, :], whitening_fit[0], whitening_fit[1])[0]
        key_n = key / (np.linalg.norm(key) + 1e-12)
        q_sims = key_n @ macrocol_keys_norm.T
        top_idx = np.argpartition(-q_sims, m_eff - 1)[:m_eff] if m_eff < K else np.arange(K)
        order = np.argsort(-q_sims[top_idx])
        top_idx = top_idx[order]
        top_sims = q_sims[top_idx]
        z = top_sims - top_sims.max()
        e = np.exp(z); w = e / (e.sum() + 1e-12)
        for j, k_idx in enumerate(top_idx):
            q_sub = shard_projs[k_idx] @ key
            recalled_sub = Ws[k_idx] @ q_sub
            r_norm = recalled_sub / (np.linalg.norm(recalled_sub) + 1e-12)
            scores_out[qi] += w[j] * (V_proj_norm[k_idx] @ r_norm)
    return scores_out


# ---------------------------------------------------------------------------
# Eval (set-recall@k for multi-value)
# ---------------------------------------------------------------------------

def baseline_score(sp_pairs, E: np.ndarray, R: np.ndarray, sq: float, W: np.ndarray,
                   whitening_fit=None) -> np.ndarray:
    """Score (s, p) queries through monolithic W; returns (n_q, n_ent_pool) score matrix."""
    if not sp_pairs:
        return np.zeros((0, E.shape[0]), dtype=np.float32)
    s = np.array([x[0] for x in sp_pairs])
    p = np.array([x[1] for x in sp_pairs])
    keys = (E[s] * R[p] * sq).astype(np.float32)
    if whitening_fit is not None:
        keys = apply_zca(keys, whitening_fit[0], whitening_fit[1])
    return (E @ (W @ keys.T)).T


def set_recall_at_k(score_matrix: np.ndarray, sp_pairs, objs_list, use_kwta: bool = False) -> float:
    """Multi-value set-recall@k: for each query, take top-|obj| from score row; intersect with truth."""
    if score_matrix.shape[0] == 0:
        return 0.0
    tot = 0.0
    for j, ob in enumerate(objs_list):
        k = len(ob)
        row = score_matrix[j]
        if use_kwta:
            row = kwta_topk(row, KWTA_K)
        topk = set(np.argpartition(row, -k)[-k:].tolist())
        tot += len(topk & set(ob)) / k
    return tot / max(len(objs_list), 1)


# ---------------------------------------------------------------------------
# Per-arm runner
# ---------------------------------------------------------------------------

def run_arm(arm: str, triples, keyobjs, E, R, sq, n_ent_pool, n_rel_used, n_eval, rng_eval):
    """Run a single arm; return setrecall_all + diagnostics."""
    keys_items = list(keyobjs.items())
    idx_eval = rng_eval.permutation(len(keys_items))[:min(n_eval, len(keys_items))]
    sp_eval = [keys_items[i][0] for i in idx_eval]
    objs_eval = [keys_items[i][1] for i in idx_eval]
    out = {"arm": arm}

    # Optional whitening fit (only the arms that use it)
    whitening_fit = None
    if arm in ("whitening", "combined"):
        # Fit ZCA on a sample of keys (use a subset of triples for fit; size capped)
        n_fit = min(5000, len(triples))
        tr_fit = np.asarray(triples[:n_fit], dtype=np.int64)
        keys_fit = (E[tr_fit[:, 0]] * R[tr_fit[:, 1]] * sq).astype(np.float32)
        t0 = time.time()
        mean, W_zca = fit_zca(keys_fit)
        out["zca_fit_s"] = round(time.time() - t0, 2)
        whitening_fit = (mean, W_zca)

    if arm in ("baseline", "whitening", "kwta"):
        # Monolithic Hebbian W (with optional whitening on key transform)
        t0 = time.time()
        if whitening_fit is not None:
            kt = lambda ks: apply_zca(ks, whitening_fit[0], whitening_fit[1])
        else:
            kt = None
        W = ingest_baseline(triples, n_ent_pool, n_rel_used, E, R, sq, key_transform=kt)
        out["ingest_s"] = round(time.time() - t0, 2)
        # Score
        t0 = time.time()
        S = baseline_score(sp_eval, E, R, sq, W, whitening_fit=whitening_fit)
        out["score_s"] = round(time.time() - t0, 2)
        use_kwta = (arm == "kwta")
        sr_all = set_recall_at_k(S, sp_eval, objs_eval, use_kwta=use_kwta)
    elif arm in ("modular", "combined"):
        # Modular shards (combined also uses whitening + kWTA)
        t0 = time.time()
        rng_mod = np.random.default_rng(7777)
        Ws, shard_projs, macrocol_keys_norm = modular_ingest(
            triples, E, R, sq, K_MOD, rng_mod, whitening_fit=whitening_fit)
        out["ingest_s"] = round(time.time() - t0, 2)
        out["n_per_shard"] = Ws[0].shape[0]
        t0 = time.time()
        S = modular_score(sp_eval, E, R, sq, Ws, shard_projs, macrocol_keys_norm,
                          n_ent_pool, whitening_fit=whitening_fit)
        out["score_s"] = round(time.time() - t0, 2)
        use_kwta = (arm == "combined")
        sr_all = set_recall_at_k(S, sp_eval, objs_eval, use_kwta=use_kwta)
    else:
        raise ValueError("unknown arm: %s" % arm)

    out["setrecall_all"] = round(float(sr_all), 4)
    out["n_eval"] = len(sp_eval)
    return out


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest():
    """Mechanism unit-tests: ZCA roundtrip + kwta + tiny modular sanity."""
    g = np.random.default_rng(0)
    # ZCA: fit + apply -> decorrelated cov ~ identity
    K_fit = g.standard_normal((1000, 64)).astype(np.float32)
    mean, W = fit_zca(K_fit, eps=1e-5)
    K_w = apply_zca(K_fit, mean, W)
    cov_w = (K_w.T @ K_w) / len(K_w)
    off_diag = cov_w - np.diag(np.diag(cov_w))
    assert np.abs(off_diag).mean() < 0.05, "ZCA off-diag too high"
    # kwta: top-k preserved, rest zero
    scores = np.array([0.1, 0.5, 0.9, 0.3, 0.7], dtype=np.float32)
    out = kwta_topk(scores, 2)
    assert (out > 0).sum() == 2, "kwta should keep exactly 2"
    assert out[2] > 0 and out[4] > 0, "kwta should keep top-2 (idx 2, 4)"
    # Tiny synthetic KG + baseline Hebbian sanity
    n_dim = 256
    rng = np.random.default_rng(0)
    E_s = bipolar(50, n_dim, rng); R_s = bipolar(4, n_dim, rng); sq = math.sqrt(n_dim)
    triples_s = []
    keyobjs_s = defaultdict(set)
    for i in range(20):
        s = i; p = int(rng.integers(0, 4))
        for _ in range(1 + int(rng.integers(0, 3))):
            o = int(rng.integers(0, 50))
            if o != s and o not in keyobjs_s[(s, p)]:
                keyobjs_s[(s, p)].add(o)
                triples_s.append((s, p, o))
    keyobjs_s = {k: sorted(v) for k, v in keyobjs_s.items()}
    # Baseline arm sanity at small scale
    tr = np.asarray(triples_s, dtype=np.int64)
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), 5000):
        ks = (E_s[tr[b:b + 5000, 0]] * R_s[tr[b:b + 5000, 1]] * sq).astype(np.float32)
        W += (E_s[tr[b:b + 5000, 2]].T @ ks) / n_dim
    hit, tot = 0, 0
    for (s, p), objs in keyobjs_s.items():
        key = E_s[s] * R_s[p] * sq
        scores = E_s @ (W @ key)
        k = len(objs)
        topk = set(np.argpartition(scores, -k)[-k:].tolist())
        hit += len(topk & set(objs)); tot += k
    assert hit / tot >= 0.85, "baseline Hebbian set-recall too low: %.2f" % (hit / tot)
    print("[selftest] PASS: ZCA-decorr ok, kwta ok, baseline-Hebbian set-recall=%.2f" %
          (hit / tot), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Per-seed runner
# ---------------------------------------------------------------------------

def run_seed(seed: int):
    """One seed: full M_GRID x ARMS sweep with per-M entity-pool sizing."""
    out = {"seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "config_version": CONFIG_VERSION,
           "by_M": {}}
    rng = np.random.default_rng(seed)
    R = bipolar(N_REL, N_DIM, rng)
    sq = math.sqrt(N_DIM)
    for M in M_GRID:
        n_ent_pool = _n_ent_pool_for_M(M)
        # Per-M entity codebook (deterministic from seed + M)
        rng_E = np.random.default_rng(seed * 100 + M // 1000)
        E = bipolar(n_ent_pool, N_DIM, rng_E)
        rng_kg = np.random.default_rng(seed * 1000 + M)
        triples, keyobjs, n_ent_used, n_rel_used = make_synthetic_kg(
            M, n_ent_pool, N_REL, MAX_OBJ_PER_KEY, rng_kg)
        per_arm = {}
        for arm in ARMS:
            t_arm = time.time()
            arm_out = run_arm(arm, triples, keyobjs, E, R, sq, n_ent_pool, n_rel_used,
                              N_EVAL, np.random.default_rng(seed * 3000 + hash(arm) % 100000))
            arm_out["wall_s"] = round(time.time() - t_arm, 2)
            arm_out["n_ent_pool"] = n_ent_pool
            per_arm[arm] = arm_out
            print("  [seed=%d M=%d arm=%-10s pool=%d] setrecall_all=%.4f wall=%.1fs" % (
                seed, M, arm, n_ent_pool, arm_out["setrecall_all"], arm_out["wall_s"]), flush=True)
        out["by_M"]["M%d" % M] = {
            "M": M, "n_triples": len(triples), "n_keys": len(keyobjs),
            "n_ent_used": n_ent_used, "n_rel_used": n_rel_used, "n_ent_pool": n_ent_pool,
            "arms": per_arm,
        }
    return out


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def _m_fail(arm: str, ps) -> int:
    """Smallest M where mean setrecall_all across seeds drops below SETRECALL_FLOOR.
    Returns max(M_GRID) + 1 sentinel if arm never fails in the tested grid (== beyond).
    """
    for M in M_GRID:
        vals = []
        for p in ps:
            cell = p.get("by_M", {}).get("M%d" % M, {}).get("arms", {}).get(arm)
            if cell is not None and cell.get("setrecall_all") is not None:
                vals.append(cell["setrecall_all"])
        if not vals:
            continue
        mean_sr = float(np.mean(vals))
        if mean_sr < SETRECALL_FLOOR:
            return M
    return max(M_GRID) + 1


def verdict(ps):
    """Compute compound lift L = M_fail(combined) / M_fail(baseline)."""
    m_fail = {arm: _m_fail(arm, ps) for arm in ARMS}
    L = m_fail["combined"] / max(m_fail["baseline"], 1)

    # cv across seeds at the largest M, combined arm
    largest = max(M_GRID)
    combined_at_largest = [
        p.get("by_M", {}).get("M%d" % largest, {}).get("arms", {}).get("combined", {})
        .get("setrecall_all")
        for p in ps
    ]
    combined_at_largest = [v for v in combined_at_largest if v is not None]
    cv = (float(np.std(combined_at_largest) / max(np.mean(combined_at_largest), 1e-9))
          if combined_at_largest else 1.0)

    # Discriminator regime sanity: Arm 1 at DISCRIM_M
    discrim_vals = [
        p.get("by_M", {}).get("M%d" % DISCRIM_M, {}).get("arms", {}).get("baseline", {})
        .get("setrecall_all")
        for p in ps
    ]
    discrim_vals = [v for v in discrim_vals if v is not None]
    if discrim_vals:
        discrim_mean = float(np.mean(discrim_vals))
    else:
        discrim_mean = None

    summ_parts = ["M_fail per arm: %s" % {a: m_fail[a] for a in ARMS},
                  "L=%.2f (combined/baseline)" % L,
                  "cv@combined,M%d=%.3f" % (largest, cv)]
    if discrim_mean is not None and DISCRIM_M in M_GRID:
        summ_parts.append("discrim_baseline@M%d=%.3f (need>=%.2f)" % (
            DISCRIM_M, discrim_mean, DISCRIM_RECALL))
    summ = " | ".join(summ_parts)

    # Discriminator gate: if Arm 1 at DISCRIM_M fails the sanity floor AND we're in FULL,
    # harness is broken (per Fix #16). Surface as HARD_HALT-equivalent (HARD_FAIL with
    # explicit harness-broken flag).
    if (discrim_mean is not None and DISCRIM_M in M_GRID and discrim_mean < DISCRIM_RECALL
            and RUN_MODE == "full"):
        return ("HARD_FAIL",
                "HARD_FAIL (HARNESS_BROKEN): baseline at M=%d setrecall=%.3f < %.2f sanity floor. " % (
                    DISCRIM_M, discrim_mean, DISCRIM_RECALL) + summ)

    if L >= HARD_PASS_LIFT and cv <= 0.10:
        return ("HARD_PASS",
                "HARD_PASS: compound mechanism lift L=%.2f >= %.1fx; substrate-only-decode "
                "preserved (n_llm=%d); cv=%.3f <= 0.10. " % (L, HARD_PASS_LIFT,
                                                              _LLM_CALL_COUNTER[0], cv) + summ)
    if L <= HARD_FAIL_LIFT:
        return ("HARD_FAIL",
                "HARD_FAIL: compound mechanism lift L=%.2f <= %.1fx; mechanisms do NOT compose "
                "(simple-compounding hypothesis ruled out). " % (L, HARD_FAIL_LIFT) + summ)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: partial compound lift L=%.2f in (%.1f, %.1f); characterize "
            "which mechanism pair is load-bearing. " % (L, HARD_FAIL_LIFT, HARD_PASS_LIFT) + summ)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s M_grid=%s N_DIM=%d K_MOD=%d KWTA_K=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, M_GRID, N_DIM, K_MOD, KWTA_K, CONFIG_VERSION), flush=True)
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Per-seed checkpoint resume (PROT-021 with run_config guard)
    run_cfg = {"N": N_DIM, "run_mode": RUN_MODE}
    ps = []
    for s in SEEDS:
        existing = aggregate_partials(out_dir, [s], run_config=run_cfg)
        if str(s) in existing:
            print("  [seed=%d] RESUME from checkpoint" % s, flush=True)
            ps.append(existing[str(s)]); continue
        rec = run_seed(s)
        write_partial_key(out_dir, s, rec)
        ps.append(rec)

    v, vmsg = verdict(ps)
    print("\n[VERDICT] " + vmsg, flush=True)

    # Build top-level metrics dict
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "summary": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "config_version": CONFIG_VERSION,
        "per_seed": ps,
        "elapsed_s": round(time.time() - t0, 1),
        "zero_llm_calls_at_inference": (_LLM_CALL_COUNTER[0] == 0),
        "n_llm_calls": _LLM_CALL_COUNTER[0],
        "DESIGN_NOTE": (
            "Compound storage-density test: 5 arms (baseline / +modular / +whitening / +kwta / "
            "combined) x M_grid sweep. Synthetic-bipolar KG (no encoder). HARD_PASS = "
            "M_fail(combined) >= 5.0x M_fail(baseline). Fix #16 discriminator regime: "
            "baseline at M=10k must reproduce n8 chain-grade pattern (setrecall >= 0.90)."
        ),
    }
    write_metrics(out_dir, metrics, results=ps)
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)
