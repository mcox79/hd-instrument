"""c_composition_storage_density_v2 -- COMPOUND storage-density cell (GPU).

USER 2026-06-22 + Director routing under Fix #22+#23: how dense is storage now,
and how far can we push it -- AT SCALE where baseline single-mechanism FAILS.

v1 (numpy/CPU; M_grid up to 25k) tripped Fix #16: smoke at M=2000 saw M_fail=2001
across ALL 5 arms (no arm failed at the tested cap = nothing to compound over =
discriminator-invalid). v2 sweeps a much wider M range so baseline DOES fail,
giving compound arms something to lift over. Routed to overnight_queue (GPU)
for matmul throughput at N=4096 across 6 M-points x 5 arms x 3 seeds = 90 cells.

Mechanisms composed (5 arms; same as v1):
  Arm 1 (BASELINE):     plain multi-value Hebbian (= n8 mechanism unchanged)
  Arm 2 (+ MODULAR):    Arm 1 + K=8 macrocolumn content-routed (m1 lineage)
  Arm 3 (+ WHITENING):  Arm 1 + ZCA whitening on encoded keys before Hebbian
  Arm 4 (+ KWTA):       Arm 1 + k-WTA sparse readout (k=20 winners; n4 lineage)
  Arm 5 (COMBINED):     Arm 1 + MODULAR + WHITENING + KWTA stacked

Synthetic-bipolar KG (no encoder; substrate-primitive isolation):
  - Random entity codebook (bipolar +-1)
  - Multi-value (each (s, p) -> 1-5 objects; mirrors n8 1-to-many fraction)
  - M_grid sweeps the capacity curve through-and-past baseline failure

Pre-reg HARD bands (per spawn-prompt 2026-06-22):
  Let M_star = smallest M in M_GRID where mean baseline setrecall < 0.50.

  HARD_PASS:   At M_star, combined setrecall >= 0.80 AND
               ratio combined/baseline >= 3.0x;
               cv <= 0.05 across seeds at M_star (combined arm);
               substrate-only-decode preserved (n_llm_calls == 0).

  HARD_FAIL:   Either (a) combined fails at same M_star as baseline
               (compound mechanisms don't compose), or
               (b) no M in M_GRID causes baseline to fail (smoke regime too
               small; same discriminator-invalid trap as v1).

  MIDDLE_BAND: Combined > baseline at M_star but ratio < 3.0x
               (partial composition; characterize load-bearing pair).

Substrate-only-decode gate: n_llm_calls = 0 (pure torch primitives; no LLM
forward calls anywhere in ingest, score, or verdict).

GPU (torch+cuda); ASCII; per-seed checkpoint; atexit synth-on-timeout (TODO #9).
"""
from __future__ import annotations
import sys, os, argparse, time, math, json, signal, atexit
from pathlib import Path
from collections import defaultdict
import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "c_composition_storage_density_v2"
_LLM_CALL_COUNTER = [0]  # substrate-only by construction; torch primitives only
_METRICS_WRITTEN = [False]

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

# TODO #6 resolution pattern: queue-entry name suffix is the only usable smoke signal
# (runner overrides HDLAB_RUN_MODE=full unconditionally on remote_cpu_queue).
_NAME_SAYS_SMOKE = "_smoke" in os.environ.get("HDLAB_EXP_NAME", "").lower()


def _detect_run_mode():
    """Detect run mode: --smoke flag > queue-entry-name _smoke suffix > HDLAB_RUN_MODE > full."""
    if _ARGS.smoke or _ARGS.self_test:
        return "smoke"
    if _NAME_SAYS_SMOKE:
        return "smoke"
    env_mode = os.environ.get("HDLAB_RUN_MODE", "").lower()
    if env_mode in ("smoke", "full"):
        return env_mode
    exp_name = os.environ.get("HDLAB_EXP_NAME", "")
    if exp_name.lower().endswith("_smoke"):
        return "smoke"
    return "full"


RUN_MODE = _detect_run_mode()
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
DTYPE = torch.float32

# Config - dimensions fixed; mechanism arms vary
N_DIM = 4096                    # matches v1 + n8 baseline
V_C_REL = 8                     # relation codebook size (mirrors n8 ConceptNet)
MAX_OBJ_PER_KEY = 5             # multi-value cap
K_MOD = 8                       # modular macrocolumn count (m1 default)
M_TOP = 2                       # Top-m softmax over macrocolumn shards
KWTA_K = 20                     # k-WTA sparse readout: top-k winners
ZCA_EPS = 1e-3                  # ZCA shrinkage

# Per-M entity-pool sizing: keep V_proj cost proportional to M
MIN_ENT_POOL = 1000
MAX_ENT_POOL = 200000           # raised from v1 to support M=500k (n_ent ~ 150k)
ENT_POOL_MULT = 1.5             # roughly mirrors n8's ent-density

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    # Wider M_grid per spawn prompt: sweeps through-and-past baseline failure
    M_GRID = [1000, 10000, 50000, 100000, 250000, 500000]
    N_EVAL = 300                # per-(arm, M) eval keys
else:
    # Smoke: 1 seed, 3 small M points (Fix #16 honoring -- includes a regime
    # where baseline is EXPECTED to fail at smoke so harness can be sanity-checked
    # without taking 6h). Designed to complete in <15min on GPU.
    SEEDS = [1]
    M_GRID = [1000, 10000, 50000]
    N_EVAL = 60

ARMS = ["baseline", "modular", "whitening", "kwta", "combined"]

# Pre-reg bands (NEW for v2; per spawn-prompt 2026-06-22)
BASELINE_FAIL_THRESHOLD = 0.50  # M_star = smallest M where mean baseline setrecall < this
HARD_PASS_COMBINED_FLOOR = 0.80 # combined setrecall must be >= this at M_star
HARD_PASS_RATIO = 3.0           # combined/baseline ratio at M_star must be >= this
MIDDLE_BAND_RATIO_FLOOR = 1.0   # ratio in (1.0, 3.0) = MIDDLE_BAND
CV_MAX = 0.05                   # cv across seeds at M_star (combined arm)
DISCRIM_M = 10000               # sanity: at this M, expect baseline to still mostly work
DISCRIM_BASELINE_FLOOR = 0.50   # if baseline at M=10k < this in FULL, harness suspicious

CONFIG_VERSION = (
    "c_compose_v2: N_DIM=%d V_C_REL=%d M_grid=%s K_MOD=%d KWTA_K=%d ZCA_EPS=%.4f "
    "MAX_OBJ=%d N_EVAL=%d ENT_POOL_MULT=%.1f MIN_POOL=%d MAX_POOL=%d "
    "seeds=%s arms=%s BASE_FAIL=%.2f PASS_FLOOR=%.2f PASS_RATIO=%.1f "
    "MM_RATIO_FLOOR=%.1f CV_MAX=%.2f device=%s mode=%s"
) % (N_DIM, V_C_REL, M_GRID, K_MOD, KWTA_K, ZCA_EPS, MAX_OBJ_PER_KEY, N_EVAL,
     ENT_POOL_MULT, MIN_ENT_POOL, MAX_ENT_POOL, SEEDS, ARMS,
     BASELINE_FAIL_THRESHOLD, HARD_PASS_COMBINED_FLOOR, HARD_PASS_RATIO,
     MIDDLE_BAND_RATIO_FLOOR, CV_MAX, str(DEVICE), RUN_MODE)


def _n_ent_pool_for_M(M: int) -> int:
    """Per-M entity-pool size: keeps codebook costs proportional to M."""
    return min(MAX_ENT_POOL, max(MIN_ENT_POOL, int(M * ENT_POOL_MULT)))


# ---------------------------------------------------------------------------
# Substrate primitives (torch)
# ---------------------------------------------------------------------------

def bipolar(n_vec: int, dim: int, generator: torch.Generator) -> torch.Tensor:
    """Synthetic bipolar +-1 / sqrt(dim) HVs on DEVICE (uses torch generator)."""
    X = torch.randint(0, 2, (n_vec, dim), generator=generator,
                      dtype=DTYPE, device=generator.device) * 2.0 - 1.0
    norms = torch.linalg.norm(X, dim=1, keepdim=True).clamp(min=1e-8)
    X = X / norms
    # If generator is on CPU, move output to DEVICE
    if generator.device != DEVICE:
        X = X.to(DEVICE)
    return X


def bipolar_np(n_vec: int, dim: int, rng: np.random.Generator) -> torch.Tensor:
    """Pure-numpy seed + move to DEVICE (deterministic across cpu/gpu)."""
    X = (rng.integers(0, 2, size=(n_vec, dim)).astype(np.float32) * 2.0 - 1.0)
    X = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
    return torch.from_numpy(X).to(DEVICE)


def make_synthetic_kg(M: int, n_ent_pool: int, n_rel: int, max_obj: int,
                      rng: np.random.Generator):
    """Synthetic KG of M (s, p, o) triples grouped into (s, p) -> [o, ...]."""
    keyobjs = defaultdict(set)
    triples = []
    tries = 0
    max_tries = M * 50
    while len(triples) < M and tries < max_tries:
        s = int(rng.integers(0, n_ent_pool))
        p = int(rng.integers(0, n_rel))
        k_obj = 1 + int(rng.integers(0, max_obj))
        for _ in range(k_obj):
            o = int(rng.integers(0, n_ent_pool))
            if o == s or o in keyobjs[(s, p)]:
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


def ingest_baseline(triples, E: torch.Tensor, R: torch.Tensor, sq: float,
                    key_transform=None, batch: int = 8192) -> torch.Tensor:
    """Multi-value Hebbian on GPU: W += outer(E[o], key) / N over all triples.

    Chunked outer-product accumulation via batched matmul.
    key_transform: optional callable applied to (B, N_DIM) keys before Hebbian.
    """
    tr = torch.tensor(triples, dtype=torch.int64, device=DEVICE)
    s_idx = tr[:, 0]; p_idx = tr[:, 1]; o_idx = tr[:, 2]
    W = torch.zeros((N_DIM, N_DIM), dtype=DTYPE, device=DEVICE)
    n = len(triples)
    for b in range(0, n, batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]]) * sq
        if key_transform is not None:
            ks = key_transform(ks)
        # outer-product accumulate: W += (vals.T @ keys) / N_DIM
        W.addmm_(E[o_idx[b:b + batch]].T, ks, alpha=1.0 / N_DIM)
    return W


def fit_zca(keys: torch.Tensor, eps: float = ZCA_EPS):
    """Fit ZCA whitening on a sample of keys (torch.svd on GPU)."""
    mean = keys.mean(dim=0)
    Kc = keys - mean
    cov = (Kc.T @ Kc) / max(len(keys), 1)
    U, S, _ = torch.linalg.svd(cov)
    W_zca = (U @ torch.diag(1.0 / torch.sqrt(S + eps)) @ U.T).to(DTYPE)
    return mean.to(DTYPE), W_zca


def apply_zca(keys: torch.Tensor, mean: torch.Tensor, W_zca: torch.Tensor) -> torch.Tensor:
    """Apply ZCA whitening to a (B, N_DIM) key matrix."""
    return ((keys - mean) @ W_zca).to(DTYPE)


def kwta_topk(scores: torch.Tensor, k: int) -> torch.Tensor:
    """k-WTA sparse readout: keep top-k scores per row, zero the rest."""
    if k >= scores.shape[-1]:
        return scores
    out = torch.zeros_like(scores)
    if scores.dim() == 1:
        vals, idx = torch.topk(scores, k)
        out[idx] = vals
    else:
        vals, idx = torch.topk(scores, k, dim=-1)
        out.scatter_(-1, idx, vals)
    return out


# ---------------------------------------------------------------------------
# Modular K-macrocolumn (m1 lineage; torch)
# ---------------------------------------------------------------------------

def _per_shard_dim(K: int, n_dim_total: int = N_DIM) -> int:
    """N_per such that K * N_per^2 ~= n_dim_total^2 (fixed parameter budget)."""
    total_p = n_dim_total * n_dim_total
    return max(1, int(round(math.sqrt(total_p / K))))


def modular_ingest(triples, E: torch.Tensor, R: torch.Tensor, sq: float, K: int,
                   rng: np.random.Generator, whitening_fit=None):
    """Modular K-macrocolumn Hebbian ingest with content-router top-m softmax."""
    n_per = _per_shard_dim(K)
    macrocol_keys_np = (rng.integers(0, 2, size=(K, N_DIM)).astype(np.float32) * 2.0 - 1.0)
    macrocol_keys = torch.from_numpy(macrocol_keys_np).to(DEVICE)
    macrocol_keys_norm = macrocol_keys / torch.linalg.norm(macrocol_keys, dim=1, keepdim=True).clamp(min=1e-12)
    shard_projs_np = rng.standard_normal((K, n_per, N_DIM)).astype(np.float32) * (1.0 / math.sqrt(N_DIM))
    shard_projs = torch.from_numpy(shard_projs_np).to(DEVICE)
    Ws = [torch.zeros((n_per, n_per), dtype=DTYPE, device=DEVICE) for _ in range(K)]

    tr = torch.tensor(triples, dtype=torch.int64, device=DEVICE)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    m_eff = min(M_TOP, K)
    batch = 8192
    n = len(triples)
    for b in range(0, n, batch):
        sb = s_idx[b:b + batch]; pb = p_idx[b:b + batch]; ob = o_idx[b:b + batch]
        keys = (E[sb] * R[pb]) * sq
        vals = E[ob]
        if whitening_fit is not None:
            keys = apply_zca(keys, whitening_fit[0], whitening_fit[1])
        keys_norm = keys / torch.linalg.norm(keys, dim=1, keepdim=True).clamp(min=1e-12)
        sims = keys_norm @ macrocol_keys_norm.T                       # (B, K)
        if m_eff < K:
            top_vals, top_idx = torch.topk(sims, m_eff, dim=-1)        # (B, m_eff)
        else:
            B_ = sims.shape[0]
            top_idx = torch.arange(K, device=DEVICE).unsqueeze(0).expand(B_, K).contiguous()
            top_vals = sims
        top_norm = top_vals - top_vals.max(dim=-1, keepdim=True).values
        e_top = torch.exp(top_norm); w_top = e_top / e_top.sum(dim=-1, keepdim=True).clamp(min=1e-12)
        for j in range(m_eff):
            k_for_items = top_idx[:, j]
            w_for_items = w_top[:, j]
            # Per-shard batched accumulation (gather-by-mask)
            for k_idx in range(K):
                mask = (k_for_items == k_idx)
                if not mask.any():
                    continue
                idxs = torch.nonzero(mask, as_tuple=True)[0]
                ks_sub = keys[idxs] @ shard_projs[k_idx].T               # (n_sel, n_per)
                vs_sub = vals[idxs] @ shard_projs[k_idx].T               # (n_sel, n_per)
                w_sel = w_for_items[idxs].unsqueeze(1).to(DTYPE)
                Ws[k_idx].addmm_((vs_sub * w_sel).T, ks_sub, alpha=1.0 / n_per)
    return Ws, shard_projs, macrocol_keys_norm


def modular_score(sp_pairs, E, R, sq, Ws, shard_projs, macrocol_keys_norm,
                  n_ent_pool: int, whitening_fit=None) -> torch.Tensor:
    """Score (s, p) queries through modular shards; returns (n_q, n_ent_pool)."""
    K = len(Ws)
    n_per = Ws[0].shape[0]
    m_eff = min(M_TOP, K)
    V_proj = torch.empty((K, n_ent_pool, n_per), dtype=DTYPE, device=DEVICE)
    for k_idx in range(K):
        V_proj[k_idx] = E @ shard_projs[k_idx].T
    V_proj_norm = V_proj / torch.linalg.norm(V_proj, dim=2, keepdim=True).clamp(min=1e-12)
    n_q = len(sp_pairs)
    scores_out = torch.zeros((n_q, n_ent_pool), dtype=DTYPE, device=DEVICE)
    # Vectorize across queries: build (n_q, N_DIM) key matrix once
    sp_tensor = torch.tensor(sp_pairs, dtype=torch.int64, device=DEVICE)
    s_t = sp_tensor[:, 0]; p_t = sp_tensor[:, 1]
    keys = (E[s_t] * R[p_t]) * sq
    if whitening_fit is not None:
        keys = apply_zca(keys, whitening_fit[0], whitening_fit[1])
    keys_norm = keys / torch.linalg.norm(keys, dim=1, keepdim=True).clamp(min=1e-12)
    sims = keys_norm @ macrocol_keys_norm.T  # (n_q, K)
    if m_eff < K:
        top_vals, top_idx = torch.topk(sims, m_eff, dim=-1)
    else:
        top_idx = torch.arange(K, device=DEVICE).unsqueeze(0).expand(n_q, K).contiguous()
        top_vals = sims
    top_norm = top_vals - top_vals.max(dim=-1, keepdim=True).values
    e_top = torch.exp(top_norm); w_top = e_top / e_top.sum(dim=-1, keepdim=True).clamp(min=1e-12)
    for j in range(m_eff):
        k_for_items = top_idx[:, j]   # (n_q,)
        w_for_items = w_top[:, j]     # (n_q,)
        for k_idx in range(K):
            mask = (k_for_items == k_idx)
            if not mask.any():
                continue
            qi = torch.nonzero(mask, as_tuple=True)[0]
            q_sub = keys[qi] @ shard_projs[k_idx].T               # (n_sel, n_per)
            recalled_sub = q_sub @ Ws[k_idx].T                    # (n_sel, n_per)
            r_norm = recalled_sub / torch.linalg.norm(recalled_sub, dim=1, keepdim=True).clamp(min=1e-12)
            partial = r_norm @ V_proj_norm[k_idx].T                # (n_sel, n_ent_pool)
            scores_out[qi] += w_for_items[qi].unsqueeze(1) * partial
    return scores_out


# ---------------------------------------------------------------------------
# Eval
# ---------------------------------------------------------------------------

def baseline_score(sp_pairs, E, R, sq, W, whitening_fit=None) -> torch.Tensor:
    """Score (s, p) queries through monolithic W; returns (n_q, n_ent_pool)."""
    if not sp_pairs:
        return torch.zeros((0, E.shape[0]), dtype=DTYPE, device=DEVICE)
    sp_tensor = torch.tensor(sp_pairs, dtype=torch.int64, device=DEVICE)
    s_t = sp_tensor[:, 0]; p_t = sp_tensor[:, 1]
    keys = (E[s_t] * R[p_t]) * sq
    if whitening_fit is not None:
        keys = apply_zca(keys, whitening_fit[0], whitening_fit[1])
    # E @ (W @ keys.T) -> (n_ent, n_q); transpose to (n_q, n_ent)
    return (E @ (W @ keys.T)).T


def set_recall_at_k(score_matrix: torch.Tensor, sp_pairs, objs_list,
                    use_kwta: bool = False) -> float:
    """Multi-value set-recall@k: top-|obj| per query; intersect with truth."""
    if score_matrix.shape[0] == 0:
        return 0.0
    sm = score_matrix
    if use_kwta:
        sm = kwta_topk(sm, KWTA_K)
    tot = 0.0
    for j, ob in enumerate(objs_list):
        k = len(ob)
        row = sm[j]
        _, idx = torch.topk(row, k)
        topk = set(idx.cpu().tolist())
        tot += len(topk & set(ob)) / k
    return tot / max(len(objs_list), 1)


# ---------------------------------------------------------------------------
# Per-arm runner
# ---------------------------------------------------------------------------

def run_arm(arm: str, triples, keyobjs, E, R, sq, n_ent_pool, n_rel_used, n_eval, rng_eval):
    """Run a single arm; return setrecall + diagnostics."""
    keys_items = list(keyobjs.items())
    idx_eval = rng_eval.permutation(len(keys_items))[:min(n_eval, len(keys_items))]
    sp_eval = [keys_items[i][0] for i in idx_eval]
    objs_eval = [keys_items[i][1] for i in idx_eval]
    out = {"arm": arm}

    whitening_fit = None
    if arm in ("whitening", "combined"):
        n_fit = min(5000, len(triples))
        tr_fit = torch.tensor(triples[:n_fit], dtype=torch.int64, device=DEVICE)
        keys_fit = (E[tr_fit[:, 0]] * R[tr_fit[:, 1]]) * sq
        t0 = time.time()
        mean, W_zca = fit_zca(keys_fit)
        out["zca_fit_s"] = round(time.time() - t0, 2)
        whitening_fit = (mean, W_zca)

    if arm in ("baseline", "whitening", "kwta"):
        t0 = time.time()
        if whitening_fit is not None:
            kt = lambda ks: apply_zca(ks, whitening_fit[0], whitening_fit[1])
        else:
            kt = None
        W = ingest_baseline(triples, E, R, sq, key_transform=kt)
        out["ingest_s"] = round(time.time() - t0, 2)
        t0 = time.time()
        S = baseline_score(sp_eval, E, R, sq, W, whitening_fit=whitening_fit)
        out["score_s"] = round(time.time() - t0, 2)
        use_kwta = (arm == "kwta")
        sr_all = set_recall_at_k(S, sp_eval, objs_eval, use_kwta=use_kwta)
        del W
    elif arm in ("modular", "combined"):
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
        del Ws, shard_projs, macrocol_keys_norm
    else:
        raise ValueError("unknown arm: %s" % arm)

    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()
    out["setrecall_all"] = round(float(sr_all), 4)
    out["n_eval"] = len(sp_eval)
    return out


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest():
    """Mechanism unit-tests on torch primitives."""
    g = torch.Generator(device="cpu"); g.manual_seed(0)
    # ZCA roundtrip
    K_fit = torch.randn(1000, 64, generator=g, dtype=DTYPE).to(DEVICE)
    mean, W = fit_zca(K_fit, eps=1e-5)
    K_w = apply_zca(K_fit, mean, W)
    cov_w = (K_w.T @ K_w) / len(K_w)
    off_diag = cov_w - torch.diag(torch.diag(cov_w))
    assert off_diag.abs().mean().item() < 0.05, "ZCA off-diag too high"
    # kwta
    scores = torch.tensor([0.1, 0.5, 0.9, 0.3, 0.7], dtype=DTYPE, device=DEVICE)
    out = kwta_topk(scores, 2)
    assert (out > 0).sum().item() == 2, "kwta should keep exactly 2"
    assert out[2].item() > 0 and out[4].item() > 0, "kwta should keep top-2 (idx 2, 4)"
    # Tiny synthetic KG + baseline Hebbian sanity
    n_dim = 256
    rng = np.random.default_rng(0)
    E_s = bipolar_np(50, n_dim, rng); R_s = bipolar_np(4, n_dim, rng)
    sq_s = math.sqrt(n_dim)
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
    tr = torch.tensor(triples_s, dtype=torch.int64, device=DEVICE)
    W_st = torch.zeros((n_dim, n_dim), dtype=DTYPE, device=DEVICE)
    for b in range(0, len(tr), 5000):
        ks = (E_s[tr[b:b + 5000, 0]] * R_s[tr[b:b + 5000, 1]]) * sq_s
        W_st.addmm_(E_s[tr[b:b + 5000, 2]].T, ks, alpha=1.0 / n_dim)
    hit, tot = 0, 0
    for (s, p), objs in keyobjs_s.items():
        key = E_s[s] * R_s[p] * sq_s
        scores = E_s @ (W_st @ key)
        k = len(objs)
        _, idx = torch.topk(scores, k)
        topk = set(idx.cpu().tolist())
        hit += len(topk & set(objs)); tot += k
    assert hit / tot >= 0.85, "baseline Hebbian set-recall too low: %.2f" % (hit / tot)
    print("[selftest] PASS: ZCA-decorr ok, kwta ok, baseline-Hebbian set-recall=%.2f device=%s" %
          (hit / tot, str(DEVICE)), flush=True)


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
    R = bipolar_np(V_C_REL, N_DIM, rng)
    sq = math.sqrt(N_DIM)
    for M in M_GRID:
        n_ent_pool = _n_ent_pool_for_M(M)
        rng_E = np.random.default_rng(seed * 100 + M // 1000)
        E = bipolar_np(n_ent_pool, N_DIM, rng_E)
        rng_kg = np.random.default_rng(seed * 1000 + M)
        triples, keyobjs, n_ent_used, n_rel_used = make_synthetic_kg(
            M, n_ent_pool, V_C_REL, MAX_OBJ_PER_KEY, rng_kg)
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
        # Free E (per-M codebook); modular shard tensors freed inside run_arm
        del E
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
    return out


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def _mean_arm_at_M(arm: str, M: int, ps) -> float:
    vals = []
    for p in ps:
        cell = p.get("by_M", {}).get("M%d" % M, {}).get("arms", {}).get(arm)
        if cell is not None and cell.get("setrecall_all") is not None:
            vals.append(cell["setrecall_all"])
    if not vals:
        return None
    return float(np.mean(vals))


def _find_m_star(ps):
    """M_star = smallest M in M_GRID where mean baseline setrecall < BASELINE_FAIL_THRESHOLD."""
    for M in M_GRID:
        mean_sr = _mean_arm_at_M("baseline", M, ps)
        if mean_sr is not None and mean_sr < BASELINE_FAIL_THRESHOLD:
            return M, mean_sr
    return None, None


def verdict(ps):
    """v2 bands per spawn-prompt 2026-06-22."""
    m_star, baseline_at_star = _find_m_star(ps)

    # Discriminator-invalid trap (v1's failure mode): no baseline-fail in the grid
    if m_star is None:
        # Build per-arm setrecall-at-largest-M summary for diagnostic
        largest = max(M_GRID)
        diag = {arm: _mean_arm_at_M(arm, largest, ps) for arm in ARMS}
        return ("HARD_FAIL",
                "HARD_FAIL (DISCRIMINATOR_INVALID): baseline never failed in M_grid=%s "
                "(min mean setrecall = %.3f at M=%d). Compound mechanisms have nothing to lift "
                "over. Re-scope to larger M. setrecall@M%d per arm: %s" % (
                    M_GRID, min(v for v in diag.values() if v is not None) if diag else -1.0,
                    largest, largest, diag))

    combined_at_star = _mean_arm_at_M("combined", m_star, ps)
    if combined_at_star is None:
        return ("HARD_FAIL",
                "HARD_FAIL (DATA_MISSING): no combined-arm data at M_star=%d" % m_star)
    ratio = combined_at_star / max(baseline_at_star, 1e-9)

    # cv at M_star (combined arm) across seeds
    combined_vals = []
    for p in ps:
        c = p.get("by_M", {}).get("M%d" % m_star, {}).get("arms", {}).get("combined", {})
        v = c.get("setrecall_all")
        if v is not None:
            combined_vals.append(v)
    if not combined_vals:
        cv = 1.0
    else:
        cv = float(np.std(combined_vals) / max(np.mean(combined_vals), 1e-9))

    # Per-arm setrecall at M_star (for diagnostic in summary)
    per_arm_at_star = {arm: _mean_arm_at_M(arm, m_star, ps) for arm in ARMS}

    # Discriminator sanity at DISCRIM_M (if in grid): baseline should not crater catastrophically
    discrim_baseline = _mean_arm_at_M("baseline", DISCRIM_M, ps) if DISCRIM_M in M_GRID else None

    summ_parts = [
        "M_star=%d (baseline fell below %.2f -> %.3f)" % (m_star, BASELINE_FAIL_THRESHOLD, baseline_at_star),
        "combined@M_star=%.3f (need>=%.2f)" % (combined_at_star, HARD_PASS_COMBINED_FLOOR),
        "ratio=%.2fx (need>=%.1fx)" % (ratio, HARD_PASS_RATIO),
        "cv=%.3f (need<=%.2f)" % (cv, CV_MAX),
        "per_arm@M_star=%s" % {a: (None if per_arm_at_star[a] is None else round(per_arm_at_star[a], 3)) for a in ARMS},
    ]
    if discrim_baseline is not None:
        summ_parts.append("discrim_baseline@M%d=%.3f" % (DISCRIM_M, discrim_baseline))
    summ = " | ".join(summ_parts)

    if (combined_at_star >= HARD_PASS_COMBINED_FLOOR
            and ratio >= HARD_PASS_RATIO
            and cv <= CV_MAX
            and _LLM_CALL_COUNTER[0] == 0):
        return ("HARD_PASS",
                "HARD_PASS: at M_star=%d, combined setrecall=%.3f >= %.2f AND ratio=%.2fx >= %.1fx; "
                "substrate-only-decode preserved (n_llm=%d); cv=%.3f <= %.2f. " % (
                    m_star, combined_at_star, HARD_PASS_COMBINED_FLOOR, ratio, HARD_PASS_RATIO,
                    _LLM_CALL_COUNTER[0], cv, CV_MAX) + summ)

    if ratio <= MIDDLE_BAND_RATIO_FLOOR:
        return ("HARD_FAIL",
                "HARD_FAIL: at M_star=%d, combined/baseline ratio=%.2fx <= %.1fx; compound mechanisms "
                "do NOT compose. " % (m_star, ratio, MIDDLE_BAND_RATIO_FLOOR) + summ)

    return ("MIDDLE_BAND",
            "MIDDLE_BAND: at M_star=%d, partial composition; combined=%.3f ratio=%.2fx in "
            "(%.1fx, %.1fx). " % (m_star, combined_at_star, ratio, MIDDLE_BAND_RATIO_FLOOR,
                                  HARD_PASS_RATIO) + summ)


# ---------------------------------------------------------------------------
# Atexit synthesize-on-timeout pattern (TODO #9 from pipeline template)
# ---------------------------------------------------------------------------

_T0_GLOBAL = [None]
_OUT_DIR_GLOBAL = [None]
_SEEDS_GLOBAL = [None]


def _synthesize_on_exit():
    """If main path didn't write metrics.json (timeout SIGKILL or crash), synthesize
    from per-seed partials so cert-owner has valid data to verify-off."""
    if _METRICS_WRITTEN[0]:
        return
    if _OUT_DIR_GLOBAL[0] is None or _SEEDS_GLOBAL[0] is None:
        return
    try:
        out_dir = _OUT_DIR_GLOBAL[0]
        seeds = _SEEDS_GLOBAL[0]
        existing = aggregate_partials(out_dir, seeds, run_config={"N": N_DIM, "run_mode": RUN_MODE})
        ps_recovered = list(existing.values())
        if not ps_recovered:
            return
        v, vmsg = verdict(ps_recovered)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": v,
            "verdict_msg": "[TIMEOUT_PARTIAL_n%d/%d] " % (len(ps_recovered), len(seeds)) + vmsg,
            "summary": vmsg,
            "run_mode": RUN_MODE,
            "n_seeds": len(ps_recovered),
            "n_seeds_planned": len(seeds),
            "config_version": CONFIG_VERSION,
            "per_seed": ps_recovered,
            "elapsed_s": round(time.time() - _T0_GLOBAL[0], 1) if _T0_GLOBAL[0] else None,
            "zero_llm_calls_at_inference": (_LLM_CALL_COUNTER[0] == 0),
            "n_llm_calls": _LLM_CALL_COUNTER[0],
            "TIMEOUT_PARTIAL": True,
            "DESIGN_NOTE": "Synthesized from per-seed partials by atexit handler (timeout/SIGKILL recovery).",
        }
        write_metrics(out_dir, metrics, results=ps_recovered)
        _METRICS_WRITTEN[0] = True
        print("[atexit] synthesized metrics.json from %d partial seeds" % len(ps_recovered), flush=True)
    except Exception as e:
        print("[atexit] synthesize failed: %s" % e, flush=True)


atexit.register(_synthesize_on_exit)


def _sigterm_handler(signum, frame):
    _synthesize_on_exit()
    sys.exit(143)


try:
    signal.signal(signal.SIGTERM, _sigterm_handler)
except (ValueError, OSError):
    # SIGTERM may not be settable in non-main thread or some platforms
    pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s M_grid=%s N_DIM=%d device=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, M_GRID, N_DIM, str(DEVICE), CONFIG_VERSION), flush=True)
    if RUN_MODE == "full" and DEVICE.type != "cuda":
        print("[warn] full mode without CUDA -- this run will be SLOW; recommend GPU runner", flush=True)
    t0 = time.time()
    _T0_GLOBAL[0] = t0
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _OUT_DIR_GLOBAL[0] = out_dir
    _SEEDS_GLOBAL[0] = SEEDS

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
        "device": str(DEVICE),
        "DESIGN_NOTE": (
            "Compound storage-density v2 (GPU): 5 arms (baseline / +modular / +whitening / "
            "+kwta / combined) x M_grid=%s x %d seeds. Synthetic-bipolar KG (no encoder). "
            "HARD_PASS = at M_star (smallest M where baseline setrecall<%.2f): combined>=%.2f "
            "AND ratio>=%.1fx AND cv<=%.2f AND substrate-only-decode (n_llm=0). "
            "Fixes v1's discriminator-invalid trap (M=2000 too small) by extending M_grid."
        ) % (M_GRID, len(SEEDS), BASELINE_FAIL_THRESHOLD, HARD_PASS_COMBINED_FLOOR,
             HARD_PASS_RATIO, CV_MAX),
    }
    write_metrics(out_dir, metrics, results=ps)
    _METRICS_WRITTEN[0] = True
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)
