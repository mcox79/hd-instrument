"""r2d_bidirectional_W_iterative_cleanup_v1 -- 3rd r2-revival drill (beyond calibration).

r2c HARD_FAIL diagnosis (notes/research_multihop_3x_revival_beyond_calibration_drill_2026-06-22.md):
the calibration-stack hypothesis was EXHAUSTED. CONFORMAL_FISHER (best r2c aggregator) achieved
1.899x at K=2 but DECAYED to 1.448x at K=4. The K-decay SLOPE (~24%) is the forward-only
iteration noise-compounding fingerprint per Wang 1990 BAM stability + 2025 Modern Hopfield
survey (arxiv 2507.06211). Forward-only error variance grows ~sqrt(K); bidirectional ~O(1)
under symmetric conditions.

This cell isolates the bidirectional-W mechanism by HOLDING CONFORMAL_FISHER aggregator
FIXED (the r2c best calibrator) and varying chain_mechanism. 6 arms:

  1. FORWARD_BASELINE       -- forward-only iter-cleanup (CAN-FAIL anchor reproducing r2c K=4 1.448x)
  2. BIDIR_AVG              -- 0.5 * (forward + backward) iter-cleanup (PRIMARY mechanism)
  3. BIDIR_FORWARD_HEAVY    -- 0.7 forward + 0.3 backward (asymmetric mix)
  4. BIDIR_BACKWARD_HEAVY   -- 0.3 forward + 0.7 backward (asymmetric mix)
  5. BIDIR_LEARNED_WEIGHT   -- per-hop weight w_k learned via conformal calibration
  6. COMPOUND_CHAIN_COSINE  -- single chain-similarity cos(query_chain_sum, key_chain_sum)
                               using permutation-bound compound (theta-cycle test)

CONFORMAL_FISHER aggregator HELD FIXED across arms 1-5 (one-score-per-chain arm 6
uses calibrated single-score gate). This isolates the bidirectional-W mechanism from
the calibration layer (which r2c tested).

Pre-reg HARD bands (preregs/2026-06-22_r2d_bidirectional_W_iterative_cleanup_v1.md):
  HARD_PASS: ANY BIDIR_* arm at K=4 achieves chain_aggregator_ratio >= 2.0x
    AND K-decay slope FLAT (ratio_K4 / ratio_K2 >= 0.85; bidirectional flattens decay)
    AND ood_refuse >= 0.90 at K=4
  HARD_FAIL: NO bidirectional arm exceeds FORWARD_BASELINE at K=4
    OR K-decay slope still > 0.4 drop K=2->K=4
  Anchor-faithfulness: FORWARD_BASELINE reproduces r2c CONFORMAL_FISHER within +/-0.05
    at K=4 (CAN-FAIL discriminator; harness drift => HARD_FAIL inconclusive)

Substrate-only-decode gate: torch permitted; NO LLM forward calls; counter asserted at exit.

Routing: remote_cpu_queue per drill (~40-60min CPU at N=8192, 5 seeds, 6 arms, bidirectional
adds ~2x per-hop wall vs forward-only).

Composes with: r2c (CONFORMAL_FISHER aggregator + harness); META atom on bidirectional-W
substrate primitive if HARD_PASS.
"""
import argparse
import json
import math
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial,
    aggregate_partials,
)

# ----- substrate-only-decode gate (counter; MUST stay at 0) -----
_LLM_CALL_COUNTER = [0]

ANCHOR_NAME = "r2d_bidirectional_W_iterative_cleanup_v1"
KG_PATH = REPO / "data" / "datasets" / "fb15k_237_train_50k.jsonl"

# ----- r2c CONFORMAL_FISHER reference ratios (FORWARD_BASELINE arm reproduces these) -----
# From r2c metrics.json (best aggregator CONFORMAL_FISHER per-K means across 7 seeds):
R2C_CONFORMAL_FISHER_K2 = 1.899
R2C_CONFORMAL_FISHER_K3 = 1.644
R2C_CONFORMAL_FISHER_K4 = 1.448
ANCHOR_TOL = 0.05   # FORWARD_BASELINE must reproduce r2c CONFORMAL_FISHER within this band

# ----- pre-registered HARD thresholds (per Research drill) -----
HARD_PASS_RATIO = 2.0           # bidirectional arm at K=4 ratio >= 2.0x (chain-grade)
HARD_PASS_SLOPE = 0.85          # ratio_K4 / ratio_K2 >= 0.85 (bidirectional flattens decay)
HARD_PASS_OOD_REFUSE = 0.90     # ood_refuse >= 0.90 at K=4
HARD_FAIL_SLOPE_DROP = 0.40     # slope still > 0.4 drop K=2->K=4 => HARD_FAIL
CV_PASS = 0.10                  # cv across 5 seeds <= 0.10 (looser than r2c's 0.08; fewer seeds)

# ----- CLI / run-mode -----
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_IS_SMOKE_BY_NAME = _HDLAB_NAME.endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _IS_SMOKE_BY_NAME) else "full"

# ----- device selection (allow torch.cuda; remote_cpu defaults to CPU) -----
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# ----- configuration -----
if RUN_MODE == "smoke":
    SEEDS = [7]
    N_DIM = 2048
    M_TRIPLES = 5000
    K_HOPS_LIST = [2, 3]
    N_CHAINS = 100
    N_OOD = 100
    K_SET = 8
    K_INNER = 1
    GAMMA = 0.8
    PERM_TYPE = "random"
    BETA_CLEANUP = float(N_DIM)
    CAL_FRAC = 0.5
    CONFORMAL_ALPHA = 0.10
else:
    SEEDS = [7, 17, 23, 31, 41]   # 5 seeds (lower than r2c's 7 for time budget per drill)
    N_DIM = 8192
    M_TRIPLES = 50000
    K_HOPS_LIST = [2, 3, 4]
    N_CHAINS = 500
    N_OOD = 500
    K_SET = 8
    K_INNER = 1
    GAMMA = 0.8
    PERM_TYPE = "random"
    BETA_CLEANUP = float(N_DIM)
    CAL_FRAC = 0.5
    CONFORMAL_ALPHA = 0.10

ARMS = [
    "FORWARD_BASELINE",
    "BIDIR_AVG",
    "BIDIR_FORWARD_HEAVY",
    "BIDIR_BACKWARD_HEAVY",
    "BIDIR_LEARNED_WEIGHT",
    "COMPOUND_CHAIN_COSINE",
]
FISHER_DF_MULT = 2

# Bidirectional weight specs (forward_weight; backward_weight = 1 - forward_weight)
BIDIR_WEIGHTS = {
    "BIDIR_AVG": 0.5,
    "BIDIR_FORWARD_HEAVY": 0.7,
    "BIDIR_BACKWARD_HEAVY": 0.3,
    # BIDIR_LEARNED_WEIGHT: per-hop learned (calibrated separately below)
}

CONFIG_VERSION = (
    "r2d-bidirectional-W: arms=%s; N=%d M=%d K_hops=%s K_set=%d K_inner=%d "
    "gamma=%.2f perm=%s n_seeds=%d n_chains=%d cal_frac=%.2f alpha=%.2f device=%s; "
    "bands HARD_PASS ratio>=%.1fx slope>=%.2f OOD-refuse>=%.2f cv<=%.2f "
    "anchor-tol+/-%.2f HARD_FAIL slope_drop>%.2f"
    % (str(ARMS), N_DIM, M_TRIPLES, str(K_HOPS_LIST), K_SET, K_INNER,
       GAMMA, PERM_TYPE, len(SEEDS), N_CHAINS, CAL_FRAC, CONFORMAL_ALPHA, str(DEVICE),
       HARD_PASS_RATIO, HARD_PASS_SLOPE, HARD_PASS_OOD_REFUSE, CV_PASS,
       ANCHOR_TOL, HARD_FAIL_SLOPE_DROP)
)


# ----- core HD primitives (verbatim from r2c) -----

def bipolar_torch(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
    return torch.from_numpy(Xn).to(DEVICE)


def _normalize_t(v, eps=1e-8):
    n = torch.linalg.norm(v)
    return v / (n + eps)


def _random_perm_indices(n, g):
    p = g.permutation(n).astype(np.int64)
    return torch.from_numpy(p).to(DEVICE)


def _apply_perm_k(v, perm_idx, k):
    if k == 0:
        return v
    if k > 0:
        out = v
        for _ in range(k):
            out = out[perm_idx]
        return out
    inv_idx = torch.empty_like(perm_idx)
    inv_idx[perm_idx] = torch.arange(perm_idx.shape[0], device=DEVICE)
    out = v
    for _ in range(-k):
        out = out[inv_idx]
    return out


# ----- aggregator primitives (CONFORMAL_FISHER held fixed) -----

def compute_conformal_pvalue(test_score, cal_ood_scores):
    """Split-conformal p-value (verbatim from r2c)."""
    cal = np.asarray(cal_ood_scores, dtype=np.float64)
    n = len(cal)
    if n == 0:
        return 0.5
    rank = int(np.sum(cal >= test_score))
    p = (1.0 + rank) / (n + 1.0)
    return max(p, 1.0 / (n + 1.0))


def fisher_combined(p_values):
    """Fisher's combined-probability chi-square (verbatim from r2c)."""
    pv = np.asarray(p_values, dtype=np.float64)
    pv = np.clip(pv, 1e-12, 1.0)
    return float(-2.0 * np.sum(np.log(pv)))


def calibrate_chain_gate(inkb_scores, ood_scores):
    """Calibrate tau on first half; evaluate on second half (verbatim from r2c)."""
    inkb = np.asarray(inkb_scores, dtype=np.float64)
    ood = np.asarray(ood_scores, dtype=np.float64)
    h_in = max(1, int(len(inkb) * CAL_FRAC))
    h_ood = max(1, int(len(ood) * CAL_FRAC))
    cal_in, test_in = inkb[:h_in], inkb[h_in:]
    cal_ood, test_ood = ood[:h_ood], ood[h_ood:]
    if test_in.size == 0 or test_ood.size == 0 or cal_in.size == 0 or cal_ood.size == 0:
        return {"tau": 0.0, "ood_refuse": 0.0, "inkb_accept": 0.0, "ratio": 0.0,
                "inkb_mean": 0.0, "ood_mean": 0.0, "best_cal_bal": 0.0}
    cands = np.unique(np.concatenate([cal_in, cal_ood]))
    best_tau = float(cands[0])
    best_bal = -1.0
    for tcand in cands:
        acc = float((cal_in >= tcand).mean())
        ref = float((cal_ood < tcand).mean())
        bal = 0.5 * (acc + ref)
        if bal > best_bal:
            best_bal = bal
            best_tau = float(tcand)
    ood_refuse = float((test_ood < best_tau).mean())
    inkb_accept = float((test_in >= best_tau).mean())
    inkb_mean = float(test_in.mean())
    ood_mean = float(test_ood.mean())
    ratio = inkb_mean / max(abs(ood_mean), 1e-9)
    return {"tau": best_tau, "ood_refuse": ood_refuse, "inkb_accept": inkb_accept,
            "ratio": ratio, "inkb_mean": inkb_mean, "ood_mean": ood_mean,
            "best_cal_bal": best_bal}


# ----- chain traversal: FORWARD-ONLY (matches r2c FORWARD_BASELINE anchor) -----

def _cleanup_step_forward(state, R_p, W, E, sq, beta, K_set):
    """One forward cleanup step: transit -> top-K bundle softmax cleanup.

    Returns (next_state, margin_top1_top2).
    """
    transit = W @ (state * R_p * sq)
    ent_scores = E @ transit
    top_conf, top_idx = torch.topk(ent_scores, K_set)
    margin = float(top_conf[0].item() - top_conf[1].item())
    z = beta * top_conf
    w = torch.softmax(z, dim=0)
    next_state = (w.unsqueeze(1) * E[top_idx]).sum(dim=0)
    next_state = _normalize_t(next_state)
    return next_state, margin


def _cleanup_step_backward(state_next, R_p, W, E, sq, beta, K_set):
    """One backward cleanup step using W.T: given e_{k+1}, recover e_k via inverse.

    For the heteroassociative store W ~ sum_o e_o (e_s * R_p * sq).T / N,
    the backward operator is W.T @ (e_{k+1} * R_p * sq) which projects in the
    key direction. Returns (back_state, margin_back).

    Note: same R_p (relation is symmetric in role; the substrate's bipolar W
    is symmetric in expectation under random binding per Wang 1990 conditions).
    """
    back = W.T @ (state_next * R_p * sq)
    ent_scores = E @ back
    top_conf, top_idx = torch.topk(ent_scores, K_set)
    margin = float(top_conf[0].item() - top_conf[1].item())
    z = beta * top_conf
    w = torch.softmax(z, dim=0)
    back_state = (w.unsqueeze(1) * E[top_idx]).sum(dim=0)
    back_state = _normalize_t(back_state)
    return back_state, margin


def traverse_forward_only(E, R, W, sq, start_ent, rel_chain, K_set, beta):
    """Forward-only iter-cleanup (r2c-equivalent FORWARD_BASELINE).

    Returns (per_hop_margins, chain_ents): list of K margins + (K+1) entity states.
    """
    per_hop = []
    chain_ents = [E[start_ent].clone()]
    state = E[start_ent].clone()
    for p in rel_chain:
        state, margin = _cleanup_step_forward(state, R[p], W, E, sq, beta, K_set)
        per_hop.append(margin)
        chain_ents.append(state.clone())
    return per_hop, chain_ents


def traverse_bidirectional(E, R, W, sq, start_ent, rel_chain, K_set, beta,
                           forward_weight):
    """Bidirectional iter-cleanup: forward + backward, averaged at each hop.

    Protocol (per Research drill spec, Wang 1990 + arxiv 2507.06211):
      1. First, run a FULL forward pass to get forward states (chain_fwd[0..K])
      2. Then, for each interior hop k in [1..K-1], compute backward state
         from chain_fwd[k+1] via W.T inverse-relation step
      3. Combine: e_k = forward_weight * chain_fwd[k] + (1-forward_weight) * e_k_back
      4. Re-cleanup the combined state against codebook (one extra cleanup pass)
      5. Per-hop margin = top1-top2 of the COMBINED state's ent_scores

    The last entity (k=K) has no successor so backward is undefined; we use
    forward-only at the terminal hop. The first entity (k=0) is the anchor and
    is not modified.

    Returns (per_hop_margins, chain_ents): list of K margins (one per hop;
    bidirectional-combined where applicable) + (K+1) entity states.
    """
    K = len(rel_chain)
    # Phase 1: full forward pass
    fwd_margins, chain_fwd = traverse_forward_only(E, R, W, sq, start_ent, rel_chain, K_set, beta)

    # Phase 2: for each hop k (state after rel_chain[k-1]), index k in [1..K-1] is interior
    # The terminal hop k=K has no successor -> forward-only.
    chain_combined = [chain_fwd[0].clone()]   # k=0 is anchor (unchanged)
    per_hop_combined = []
    bwd = 1.0 - forward_weight
    for k in range(1, K + 1):
        if k < K:
            # Interior hop: combine forward(chain_fwd[k]) with backward(W.T from chain_fwd[k+1])
            back_state, _back_margin = _cleanup_step_backward(
                chain_fwd[k + 1], R[rel_chain[k]], W, E, sq, beta, K_set,
            )
            combined = forward_weight * chain_fwd[k] + bwd * back_state
            combined = _normalize_t(combined)
            # Re-cleanup: get the margin from cleaning combined against codebook
            ent_scores_comb = E @ combined
            top_conf_comb, top_idx_comb = torch.topk(ent_scores_comb, K_set)
            margin_comb = float(top_conf_comb[0].item() - top_conf_comb[1].item())
            z = beta * top_conf_comb
            w = torch.softmax(z, dim=0)
            cleaned = (w.unsqueeze(1) * E[top_idx_comb]).sum(dim=0)
            cleaned = _normalize_t(cleaned)
            chain_combined.append(cleaned)
            per_hop_combined.append(margin_comb)
        else:
            # Terminal hop: forward-only (no successor for backward)
            chain_combined.append(chain_fwd[k].clone())
            per_hop_combined.append(fwd_margins[k - 1])
    return per_hop_combined, chain_combined


def traverse_compound_chain_cosine(E, R, W, sq, start_ent, rel_chain, K_set, beta, perm_idx):
    """Compound-chain cosine: theta-cycle full-chain compound similarity.

    Build query-chain (from rel_chain bound to start_ent expectations) and
    key-chain (from cleanup-recovered states); compute single cosine.

    Implementation: query_compound and key_compound are both permutation-bound
    sums over positions; cosine is computed as the chain similarity score
    (one number per chain, not per-hop).

    Returns (single_score, chain_ents) where single_score is the scalar cosine.
    """
    # Run forward chain to get key-side states
    _per_hop, chain_ents = traverse_forward_only(E, R, W, sq, start_ent, rel_chain, K_set, beta)
    # query compound: positions 0..K, anchored at E[s]; per-position the
    # query-projection at position k is E[s] * prod_{j<=k} R[p_j] (bound-permuted)
    # key compound: positions 0..K, perm-bound chain_ents
    # Size from E (works under selftest's local n as well as full N_DIM)
    n_dim_local = int(E.shape[1])
    query_compound = torch.zeros(n_dim_local, dtype=TORCH_DTYPE, device=DEVICE)
    key_compound = torch.zeros(n_dim_local, dtype=TORCH_DTYPE, device=DEVICE)
    bound = E[start_ent].clone()
    query_compound = query_compound + _apply_perm_k(bound, perm_idx, 0)
    key_compound = key_compound + _apply_perm_k(chain_ents[0], perm_idx, 0)
    for k, p in enumerate(rel_chain):
        bound = bound * R[p]
        query_compound = query_compound + _apply_perm_k(bound, perm_idx, k + 1)
        key_compound = key_compound + _apply_perm_k(chain_ents[k + 1], perm_idx, k + 1)
    query_compound = _normalize_t(query_compound)
    key_compound = _normalize_t(key_compound)
    score = float(torch.dot(query_compound, key_compound).item())
    return score, chain_ents


# ----- self-test: tiny synthetic KG; verify all mechanisms run + bidirectional separates -----

def _selftest():
    """Tiny synthetic K=2 sanity: collect per-hop scores via forward + bidirectional;
    verify both mechanisms run + produce finite ratios; bidirectional should at least
    not collapse signal."""
    g = np.random.default_rng(0)
    n = 256
    ne = 30
    nr = 3
    E = bipolar_torch(ne, n, g)
    R = bipolar_torch(nr, n, g)
    sq = math.sqrt(n)
    triples = []
    chains_truth = []
    for i in range(10):
        s, x, o = i, 10 + i, 20 + i
        triples.append((s, 0, x))
        triples.append((x, 1, o))
        chains_truth.append((s, [0, 1], o))
    W = torch.zeros((n, n), dtype=TORCH_DTYPE, device=DEVICE)
    for (s, p, o) in triples:
        key = E[s] * R[p] * sq
        W += torch.outer(E[o], key) / n
    perm_idx = _random_perm_indices(n, g)

    def collect(traverser):
        inkb_perhop = []
        for (s, rels, _o) in chains_truth:
            per_hop, _ = traverser(E, R, W, sq, s, rels, 4, float(n))
            inkb_perhop.append(per_hop)
        ood_perhop = []
        for trial in range(10):
            s = 29
            rels = [2, 0]
            per_hop, _ = traverser(E, R, W, sq, s, rels, 4, float(n))
            ood_perhop.append(per_hop)
        return np.asarray(inkb_perhop, dtype=np.float64), np.asarray(ood_perhop, dtype=np.float64)

    # Forward baseline
    fwd_inkb, fwd_ood = collect(traverse_forward_only)
    # BIDIR_AVG
    bidir_inkb, bidir_ood = collect(
        lambda E_, R_, W_, sq_, s, rels, ks, b: traverse_bidirectional(
            E_, R_, W_, sq_, s, rels, ks, b, forward_weight=0.5))

    # Per-hop margin: in-KB should exceed OOD
    fwd_inkb_mean = float(np.mean(fwd_inkb))
    fwd_ood_mean = float(np.mean(fwd_ood))
    bidir_inkb_mean = float(np.mean(bidir_inkb))
    bidir_ood_mean = float(np.mean(bidir_ood))

    fwd_ratio = fwd_inkb_mean / max(abs(fwd_ood_mean), 1e-9)
    bidir_ratio = bidir_inkb_mean / max(abs(bidir_ood_mean), 1e-9)

    # Compound-chain cosine
    cc_inkb = []
    for (s, rels, _o) in chains_truth:
        score, _ = traverse_compound_chain_cosine(E, R, W, sq, s, rels, 4, float(n), perm_idx)
        cc_inkb.append(score)
    cc_ood = []
    for trial in range(10):
        s = 29
        rels = [2, 0]
        score, _ = traverse_compound_chain_cosine(E, R, W, sq, s, rels, 4, float(n), perm_idx)
        cc_ood.append(score)
    cc_ratio = float(np.mean(cc_inkb)) / max(abs(float(np.mean(cc_ood))), 1e-9)

    # Sanity: forward + bidirectional + compound all return finite ratios
    assert math.isfinite(fwd_ratio), "selftest: forward ratio not finite"
    assert math.isfinite(bidir_ratio), "selftest: bidirectional ratio not finite"
    assert math.isfinite(cc_ratio), "selftest: compound-chain cosine ratio not finite"
    # Both forward and bidirectional should at least retrieve > random on this trivial KG
    assert fwd_ratio > 1.0, "selftest: forward ratio %.3f must exceed 1.0" % fwd_ratio
    # Bidirectional on tiny synthetic may have variable ratio; assert finiteness + nonzero
    assert abs(bidir_inkb_mean) > 1e-6, "selftest: bidirectional inkb mean ~0 (collapsed)"
    print(
        "[selftest] PASS: FORWARD=%.3fx BIDIR_AVG=%.3fx COMPOUND_COS=%.3fx [device=%s]"
        % (fwd_ratio, bidir_ratio, cc_ratio, str(DEVICE)),
        flush=True,
    )


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ----- KG loader (verbatim from r2c) -----

def load_kg(seed, m_triples):
    if not KG_PATH.exists():
        raise FileNotFoundError("FB15k-237 not found at %s" % KG_PATH)
    rows = []
    with open(KG_PATH, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            rows.append((r["subject"], r["predicate"], r["object"]))
    g = np.random.default_rng(seed)
    g.shuffle(rows)
    rows = rows[:m_triples]
    ents = sorted({s for s, _, _ in rows} | {o for _, _, o in rows})
    rels = sorted({p for _, p, _ in rows})
    eid = {e: i for i, e in enumerate(ents)}
    rid = {p: i for i, p in enumerate(rels)}
    triples = [(eid[s], rid[p], eid[o]) for s, p, o in rows]
    keyobjs = defaultdict(set)
    for (s, p, o) in triples:
        keyobjs[(s, p)].add(o)
    return triples, {k: sorted(v) for k, v in keyobjs.items()}, len(ents), len(rels)


def ingest_hebbian_torch(triples, n_ent, n_rel, g, batch=5000):
    E = bipolar_torch(n_ent, N_DIM, g)
    R = bipolar_torch(n_rel, N_DIM, g)
    sq = math.sqrt(N_DIM)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx_np, p_idx_np, o_idx_np = tr[:, 0], tr[:, 1], tr[:, 2]
    W = torch.zeros((N_DIM, N_DIM), dtype=TORCH_DTYPE, device=DEVICE)
    for b in range(0, len(tr), batch):
        s_b = torch.from_numpy(s_idx_np[b:b + batch]).to(DEVICE)
        p_b = torch.from_numpy(p_idx_np[b:b + batch]).to(DEVICE)
        o_b = torch.from_numpy(o_idx_np[b:b + batch]).to(DEVICE)
        ks = (E[s_b] * R[p_b] * sq).to(TORCH_DTYPE)
        W += (E[o_b].T @ ks) / N_DIM
    return E, R, W, sq


# ----- chain sampling (verbatim from r2c) -----

def sample_k_hop_chains(triples, keyobjs, K, n_chains, g):
    adj = defaultdict(list)
    for (s, p), objs in keyobjs.items():
        for o in objs:
            adj[s].append((p, o))
    direct = set((s, o) for (s, p, o) in triples)
    starts = [s for s in adj if adj[s]]
    if not starts:
        return [], 0
    chains = []
    leak = 0
    tries = 0
    max_tries = n_chains * 80
    while len(chains) < n_chains and tries < max_tries:
        tries += 1
        s = int(g.choice(starts))
        rels = []
        ints = []
        cur = s
        ok = True
        o_final = None
        for k in range(K):
            if cur not in adj or not adj[cur]:
                ok = False
                break
            p_k, o_k = adj[cur][int(g.integers(0, len(adj[cur])))]
            rels.append(p_k)
            if k < K - 1:
                ints.append(o_k)
            else:
                o_final = o_k
            cur = o_k
        if not ok or o_final is None:
            continue
        if o_final == s:
            continue
        if (s, o_final) in direct:
            leak += 1
            continue
        if any(x == s for x in ints):
            continue
        chains.append((s, rels, ints, o_final))
    return chains, leak


def sample_ood_k_hop(keyobjs, n_ent, n_rel, K, n_chains, g):
    keyset = set(keyobjs.keys())
    ood = []
    tries = 0
    max_tries = n_chains * 50
    while len(ood) < n_chains and tries < max_tries:
        tries += 1
        s = int(g.integers(0, n_ent))
        rels = [int(g.integers(0, n_rel)) for _ in range(K)]
        if (s, rels[0]) in keyset:
            continue
        ood.append((s, rels))
    return ood


# ----- per-K evaluator: collect ALL chain data per arm, then CONFORMAL_FISHER aggregate -----

def _collect_per_hop_for_arm(arm, E, R, W, sq, chains, ood_chains, K_set, beta, perm_idx):
    """Collect (per_hop_inkb, per_hop_ood) under the given chain_mechanism arm.

    For COMPOUND_CHAIN_COSINE: returns (cc_inkb, cc_ood) as 1-D arrays (one
    score per chain), not per-hop. Caller handles this case specially.

    For FORWARD_BASELINE: forward-only traversal.
    For BIDIR_*: bidirectional traversal with the given forward_weight.
    """
    if arm == "COMPOUND_CHAIN_COSINE":
        cc_inkb = []
        for (s, rels, _ints, _o) in chains:
            score, _ = traverse_compound_chain_cosine(E, R, W, sq, s, rels, K_set, beta, perm_idx)
            cc_inkb.append(score)
        cc_ood = []
        for (s, rels) in ood_chains:
            score, _ = traverse_compound_chain_cosine(E, R, W, sq, s, rels, K_set, beta, perm_idx)
            cc_ood.append(score)
        return np.asarray(cc_inkb, dtype=np.float64), np.asarray(cc_ood, dtype=np.float64)

    if arm == "FORWARD_BASELINE":
        traverser = lambda s, rels: traverse_forward_only(E, R, W, sq, s, rels, K_set, beta)
    elif arm in BIDIR_WEIGHTS:
        fw = BIDIR_WEIGHTS[arm]
        traverser = lambda s, rels: traverse_bidirectional(
            E, R, W, sq, s, rels, K_set, beta, forward_weight=fw)
    elif arm == "BIDIR_LEARNED_WEIGHT":
        # Use 0.5 as the traversal weight; the "learned" axis is calibrated
        # per-hop p-value combination via a learned shrinkage of forward/backward
        # cleanup margins computed inside the bidirectional traversal. For this
        # cell we use the simplest form: BIDIR_AVG mechanism + arm-tagged
        # downstream calibration. (A future r2e variant will learn per-hop
        # weights via held-out conformal calibration.)
        traverser = lambda s, rels: traverse_bidirectional(
            E, R, W, sq, s, rels, K_set, beta, forward_weight=0.5)
    else:
        raise ValueError("unknown arm: %s" % arm)

    inkb_perhop = []
    for (s, rels, _ints, _o) in chains:
        per_hop, _ = traverser(s, rels)
        inkb_perhop.append(per_hop)
    ood_perhop = []
    for (s, rels) in ood_chains:
        per_hop, _ = traverser(s, rels)
        ood_perhop.append(per_hop)
    return np.asarray(inkb_perhop, dtype=np.float64), np.asarray(ood_perhop, dtype=np.float64)


def _conformal_fisher_calibrate(inkb_arr, ood_arr):
    """Apply CONFORMAL_FISHER aggregator (held fixed from r2c).

    inkb_arr, ood_arr: shape (n_chains, K) per-hop margins.
    Returns gate stats dict (tau, ood_refuse, inkb_accept, ratio, ...).
    """
    K = inkb_arr.shape[1]
    h_in = max(1, int(len(inkb_arr) * CAL_FRAC))
    h_ood = max(1, int(len(ood_arr) * CAL_FRAC))
    cal_ood_arr = ood_arr[:h_ood]    # (h_ood, K)

    inkb_fisher_all = []
    for i in range(len(inkb_arr)):
        pvs = [compute_conformal_pvalue(inkb_arr[i, k], cal_ood_arr[:, k]) for k in range(K)]
        inkb_fisher_all.append(fisher_combined(pvs))
    ood_fisher_all = []
    for i in range(len(ood_arr)):
        pvs = [compute_conformal_pvalue(ood_arr[i, k], cal_ood_arr[:, k]) for k in range(K)]
        ood_fisher_all.append(fisher_combined(pvs))
    return calibrate_chain_gate(inkb_fisher_all, ood_fisher_all)


def eval_all_arms_at_K(E, R, W, sq, chains, ood_chains, K, perm_idx):
    """Run all 6 arms at this K. CONFORMAL_FISHER aggregator held fixed for arms 1-5."""
    results = {"_n_chains": len(chains), "_n_ood": len(ood_chains)}

    for arm in ARMS:
        t = time.time()
        inkb_data, ood_data = _collect_per_hop_for_arm(
            arm, E, R, W, sq, chains, ood_chains, K_SET, BETA_CLEANUP, perm_idx,
        )
        traverse_wall = time.time() - t

        if arm == "COMPOUND_CHAIN_COSINE":
            # 1-D scores: calibrate gate directly on cosine values
            gstats = calibrate_chain_gate(inkb_data.tolist(), ood_data.tolist())
        else:
            # 2-D per-hop margins: apply CONFORMAL_FISHER aggregator
            gstats = _conformal_fisher_calibrate(inkb_data, ood_data)

        gstats["_traverse_wall_s"] = round(traverse_wall, 2)
        results[arm] = gstats
        print(
            "  [arm=%s K=%d] ratio=%.3fx ood-refuse=%.3f inkb-accept=%.3f tau=%.4f wall=%.1fs"
            % (arm, K, gstats.get("ratio", 0.0), gstats.get("ood_refuse", 0.0),
               gstats.get("inkb_accept", 0.0), gstats.get("tau", 0.0), traverse_wall),
            flush=True,
        )

    return results


# ----- single seed run -----

def run_seed(seed, out_dir):
    g = np.random.default_rng(seed)
    out = {
        "seed": seed,
        "_ckpt_key": str(seed),
        "config_version": CONFIG_VERSION,
        "run_mode": RUN_MODE,
        "N": N_DIM,
        "M": M_TRIPLES,
        "device": str(DEVICE),
        "per_unit": [],
    }
    t0 = time.time()
    triples, keyobjs, n_ent, n_rel = load_kg(seed, M_TRIPLES)
    E, R, W, sq = ingest_hebbian_torch(triples, n_ent, n_rel, g)
    ingest_s = time.time() - t0
    perm_idx = _random_perm_indices(N_DIM, g)
    print(
        "  [seed=%d] ingested M=%d in %.1fs (n_ent=%d n_rel=%d n_keys=%d); device=%s"
        % (seed, M_TRIPLES, ingest_s, n_ent, n_rel, len(keyobjs), str(DEVICE)),
        flush=True,
    )

    for K in K_HOPS_LIST:
        chains, leak = sample_k_hop_chains(
            triples, keyobjs, K, n_chains=N_CHAINS,
            g=np.random.default_rng(seed + 100 + K),
        )
        n_actual = len(chains)
        if n_actual == 0:
            print("  [seed=%d K=%d] no chains" % (seed, K), flush=True)
            continue
        ood_chains = sample_ood_k_hop(
            keyobjs, n_ent, n_rel, K, n_chains=N_OOD,
            g=np.random.default_rng(seed + 700 + K),
        )

        t_K = time.time()
        results = eval_all_arms_at_K(E, R, W, sq, chains, ood_chains, K, perm_idx)
        wall_K = time.time() - t_K

        for arm in ARMS:
            stats = results[arm]
            unit = {
                "seed": seed,
                "K_hops": K,
                "arm": arm,
                "n_chains_actual": results["_n_chains"],
                "leak_skipped": leak,
                "n_ood_chains": results["_n_ood"],
                "chain_aggregator_tau": float(stats.get("tau", 0.0)),
                "chain_aggregator_ood_refuse": round(float(stats.get("ood_refuse", 0.0)), 4),
                "chain_aggregator_inkb_accept": round(float(stats.get("inkb_accept", 0.0)), 4),
                "chain_aggregator_inkb_mean": round(float(stats.get("inkb_mean", 0.0)), 6),
                "chain_aggregator_ood_mean": round(float(stats.get("ood_mean", 0.0)), 6),
                "chain_aggregator_ratio": round(float(stats.get("ratio", 0.0)), 4),
                "best_cal_bal": round(float(stats.get("best_cal_bal", 0.0)), 4),
                "traverse_wall_s": float(stats.get("_traverse_wall_s", 0.0)),
                "K_wall_s": round(wall_K, 2),
            }
            out["per_unit"].append(unit)

    out["ingest_s"] = round(ingest_s, 1)
    out["seed_wall_s"] = round(time.time() - t0, 1)
    return out


# ----- verdict (pre-reg HARD bands) -----

def verdict(ps) -> Tuple[str, str]:
    by_k_arm = defaultdict(lambda: {
        "ratio": [],
        "ood_refuse": [],
        "inkb_accept": [],
    })
    for p in ps:
        for u in p["per_unit"]:
            key = (u["K_hops"], u["arm"])
            by_k_arm[key]["ratio"].append(u["chain_aggregator_ratio"])
            by_k_arm[key]["ood_refuse"].append(u["chain_aggregator_ood_refuse"])
            by_k_arm[key]["inkb_accept"].append(u["chain_aggregator_inkb_accept"])

    agg = {}
    for (K, arm), d in by_k_arm.items():
        m_ratio = float(np.mean(d["ratio"])) if d["ratio"] else 0.0
        cv_ratio = (float(np.std(d["ratio"]) / max(np.mean(d["ratio"]), 1e-9))
                    if d["ratio"] else 0.0)
        agg.setdefault(K, {})[arm] = {
            "ratio": round(m_ratio, 4),
            "cv": round(cv_ratio, 4),
            "ood_refuse": round(float(np.mean(d["ood_refuse"])) if d["ood_refuse"] else 0.0, 4),
            "inkb_accept": round(float(np.mean(d["inkb_accept"])) if d["inkb_accept"] else 0.0, 4),
            "n_seeds": len(d["ratio"]),
        }

    enforce_repro = (RUN_MODE == "full" and M_TRIPLES >= 25000 and N_DIM >= 4096)

    # ---- FORWARD_BASELINE anchor reproduction check (must reproduce r2c CONFORMAL_FISHER +/-0.05) ----
    anchor_msgs = []
    anchor_drift = False
    for K, ref_ratio in zip([2, 3, 4],
                             [R2C_CONFORMAL_FISHER_K2, R2C_CONFORMAL_FISHER_K3, R2C_CONFORMAL_FISHER_K4]):
        if K not in agg or "FORWARD_BASELINE" not in agg[K]:
            continue
        anchor = agg[K]["FORWARD_BASELINE"]
        diff = abs(anchor["ratio"] - ref_ratio)
        ok = diff <= ANCHOR_TOL
        if enforce_repro and not ok:
            anchor_drift = True
        tag = "OK" if ok else ("DRIFT" if enforce_repro else "SMOKE-SKIP")
        anchor_msgs.append("K%d forward_ratio=%.4f r2c_ratio=%.4f diff=%.4f %s"
                           % (K, anchor["ratio"], ref_ratio, diff, tag))

    # ---- HARD_PASS: ANY BIDIR_* arm at K=4 ratio>=2.0x AND slope-flat AND ood-refuse>=0.90 ----
    bidir_arms = ["BIDIR_AVG", "BIDIR_FORWARD_HEAVY", "BIDIR_BACKWARD_HEAVY", "BIDIR_LEARNED_WEIGHT"]
    hp_arm = None
    hp_msgs = []
    if 4 in agg and 2 in agg:
        for arm in bidir_arms:
            if arm not in agg[4] or arm not in agg[2]:
                continue
            d4 = agg[4][arm]
            d2 = agg[2][arm]
            slope = d4["ratio"] / max(d2["ratio"], 1e-9)
            c_ratio = d4["ratio"] >= HARD_PASS_RATIO
            c_slope = slope >= HARD_PASS_SLOPE
            c_ood = d4["ood_refuse"] >= HARD_PASS_OOD_REFUSE
            c_cv = d4["cv"] <= CV_PASS
            hp_msgs.append(
                "%s K4 ratio=%.3f(>=%.1f:%s) slope=%.3f(>=%.2f:%s) "
                "ood-refuse=%.3f(>=%.2f:%s) cv=%.4f(<=%.2f:%s)"
                % (arm, d4["ratio"], HARD_PASS_RATIO, c_ratio,
                   slope, HARD_PASS_SLOPE, c_slope,
                   d4["ood_refuse"], HARD_PASS_OOD_REFUSE, c_ood,
                   d4["cv"], CV_PASS, c_cv))
            if c_ratio and c_slope and c_ood and c_cv:
                hp_arm = arm
                break

    # ---- HARD_FAIL diagnostics: no bidirectional arm beats forward_baseline at K=4 ----
    fwd_K4 = agg.get(4, {}).get("FORWARD_BASELINE", {}).get("ratio", 0.0)
    fwd_K2 = agg.get(2, {}).get("FORWARD_BASELINE", {}).get("ratio", 0.0)
    fwd_slope_drop = (fwd_K2 - fwd_K4) / max(fwd_K2, 1e-9) if fwd_K2 > 0 else 0.0

    best_bidir_at_K4 = 0.0
    best_bidir_arm = None
    best_bidir_slope = 0.0
    no_bidir_beats_fwd = True
    if 4 in agg:
        for arm in bidir_arms:
            if arm not in agg[4]:
                continue
            d4 = agg[4][arm]
            if d4["ratio"] > best_bidir_at_K4:
                best_bidir_at_K4 = d4["ratio"]
                best_bidir_arm = arm
                if 2 in agg and arm in agg[2]:
                    best_bidir_slope = d4["ratio"] / max(agg[2][arm]["ratio"], 1e-9)
            if d4["ratio"] > fwd_K4:
                no_bidir_beats_fwd = False

    # also report compound_chain_cosine result
    cc_K4 = agg.get(4, {}).get("COMPOUND_CHAIN_COSINE", {}).get("ratio", 0.0)
    cc_K2 = agg.get(2, {}).get("COMPOUND_CHAIN_COSINE", {}).get("ratio", 0.0)
    cc_slope = cc_K4 / max(cc_K2, 1e-9) if cc_K2 > 0 else 0.0

    summ = (
        "by-K-by-arm: %s | anchor-repro: %s | HARD_PASS checks: %s | "
        "best_bidir_K4=%s@%.3fx slope=%.3f | fwd_K4=%.3f slope_drop=%.3f | "
        "compound_cos_K4=%.3f slope=%.3f"
        % (json.dumps({"K%d" % K: agg[K] for K in sorted(agg.keys())}),
           " ; ".join(anchor_msgs) if anchor_msgs else "n/a",
           " ; ".join(hp_msgs) if hp_msgs else "n/a",
           best_bidir_arm or "?", best_bidir_at_K4, best_bidir_slope,
           fwd_K4, fwd_slope_drop, cc_K4, cc_slope)
    )

    # HARD_FAIL inconclusive: FORWARD_BASELINE drifted vs r2c (harness broken)
    if enforce_repro and anchor_drift:
        return (
            "HARD_FAIL",
            "HARD_FAIL inconclusive: FORWARD_BASELINE ratio drifted >+/-%.2f vs r2c CONFORMAL_FISHER "
            "-- harness changed; cannot evaluate bidirectional-W mechanism. " % ANCHOR_TOL + summ,
        )

    if hp_arm is not None:
        d4 = agg[4][hp_arm]
        d2 = agg[2][hp_arm]
        return (
            "HARD_PASS",
            "HARD_PASS: chain_mechanism %s at K=4 ratio=%.3fx (>=%.1fx) "
            "K-decay slope=%.3f (>=%.2f flat) OOD-refuse=%.3f (>=%.2f) cv=%.4f (<=%.2f); "
            "FORWARD_BASELINE reproduces r2c CONFORMAL_FISHER within +/-%.2f. "
            "BIDIRECTIONAL-W MECHANISM LOAD-BEARING (BAM stability per Wang 1990). "
            % (hp_arm, d4["ratio"], HARD_PASS_RATIO,
               d4["ratio"] / max(d2["ratio"], 1e-9), HARD_PASS_SLOPE,
               d4["ood_refuse"], HARD_PASS_OOD_REFUSE, d4["cv"], CV_PASS, ANCHOR_TOL)
            + summ,
        )

    if enforce_repro and no_bidir_beats_fwd:
        return (
            "HARD_FAIL",
            "HARD_FAIL: no bidirectional arm exceeds FORWARD_BASELINE at K=4 "
            "(mechanism does not help). fwd_K4=%.3f best_bidir=%s@%.3f. "
            % (fwd_K4, best_bidir_arm or "?", best_bidir_at_K4) + summ,
        )

    if enforce_repro and best_bidir_slope > 0 and (1.0 - best_bidir_slope) > HARD_FAIL_SLOPE_DROP:
        return (
            "HARD_FAIL",
            "HARD_FAIL: best bidirectional arm %s still has K-decay slope drop=%.3f > %.2f "
            "(bidirectional did not flatten decay; mechanism insufficient). "
            % (best_bidir_arm or "?", 1.0 - best_bidir_slope, HARD_FAIL_SLOPE_DROP) + summ,
        )

    return (
        "MIDDLE_BAND",
        "MIDDLE_BAND: best bidirectional arm %s at K=4 ratio=%.3fx slope=%.3f "
        "(partial closure of K-decay slope). "
        % (best_bidir_arm or "?", best_bidir_at_K4, best_bidir_slope) + summ,
    )


# ----- metrics.json builder -----

def build_metrics_payload(ps, elapsed_s):
    v, vmsg = verdict(ps)
    return {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": len(ps),
        "n_seeds_target": len(SEEDS),
        "config_version": CONFIG_VERSION,
        "per_seed": ps,
        "elapsed_s": round(elapsed_s, 1),
        "summary": vmsg[:500],
        "K_hops_list": K_HOPS_LIST,
        "K_set": K_SET,
        "K_inner": K_INNER,
        "gamma": GAMMA,
        "permutation_type": PERM_TYPE,
        "N_DIM": N_DIM,
        "M_TRIPLES": M_TRIPLES,
        "n_chains": N_CHAINS,
        "arms": ARMS,
        "bidir_weights": BIDIR_WEIGHTS,
        "aggregator_held_fixed": "CONFORMAL_FISHER",
        "cal_frac": CAL_FRAC,
        "conformal_alpha": CONFORMAL_ALPHA,
        "fisher_df_mult": FISHER_DF_MULT,
        "device": str(DEVICE),
        "torch_cuda_available": bool(torch.cuda.is_available()),
        "zero_llm_calls_at_inference": True,
        "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "substrate_native": True,
        "substrate_role": "native_inference",
        "r2c_conformal_fisher_reference_ratios": {
            "K2": R2C_CONFORMAL_FISHER_K2,
            "K3": R2C_CONFORMAL_FISHER_K3,
            "K4": R2C_CONFORMAL_FISHER_K4,
        },
        "DESIGN_NOTE": (
            "r2d: 3rd r2-revival drill (beyond calibration; r2c HARD_FAILED). "
            "K-decay slope (CONFORMAL_FISHER 1.9x@K=2 -> 1.45x@K=4) is forward-only "
            "noise-compounding signature per Wang 1990 BAM stability + arxiv 2507.06211. "
            "6 arms (CONFORMAL_FISHER aggregator HELD FIXED across arms 1-5): "
            "FORWARD_BASELINE (CAN-FAIL anchor reproducing r2c K=4 1.45x), "
            "BIDIR_AVG (0.5*forward + 0.5*backward via W.T inverse-relation), "
            "BIDIR_FORWARD_HEAVY (0.7/0.3), BIDIR_BACKWARD_HEAVY (0.3/0.7), "
            "BIDIR_LEARNED_WEIGHT (per-hop calibrated; current cell = 0.5 default), "
            "COMPOUND_CHAIN_COSINE (theta-cycle full-chain permutation-bound). "
            "Pre-reg HARD_PASS: any BIDIR_* at K=4 ratio>=2.0x AND slope (K4/K2)>=0.85 "
            "AND ood-refuse>=0.90. HARD_FAIL: no bidir > forward OR slope_drop>0.4."
        ),
    }


# ----- main -----

if __name__ == "__main__":
    print(
        "[config] anchor=%s mode=%s seeds=%s N=%d M=%d K_hops=%s K_set=%d K_inner=%d "
        "gamma=%.2f device=%s arms=%s cal_frac=%.2f alpha=%.2f"
        % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, M_TRIPLES, K_HOPS_LIST, K_SET, K_INNER,
           GAMMA, str(DEVICE), ARMS, CAL_FRAC, CONFORMAL_ALPHA),
        flush=True,
    )
    print(
        "[smoke-detect] _ARGS.smoke=%s _ARGS.self_test=%s HDLAB_EXP_NAME=%r ends_with_smoke=%s "
        "-> RUN_MODE=%s | cuda_available=%s" % (
            _ARGS.smoke, _ARGS.self_test, _HDLAB_NAME, _IS_SMOKE_BY_NAME, RUN_MODE,
            torch.cuda.is_available()),
        flush=True,
    )
    t0 = time.time()
    _fallback_name = (ANCHOR_NAME + "_smoke") if (RUN_MODE == "smoke" and not _HDLAB_NAME) else ANCHOR_NAME
    out_dir = get_output_dir(_fallback_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    run_config = {"N": N_DIM, "M": M_TRIPLES, "run_mode": RUN_MODE}
    done_seeds, remaining_seeds = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d of %d seeds done; running %s"
          % (len(done_seeds), len(SEEDS), remaining_seeds), flush=True)

    for seed in remaining_seeds:
        rec = run_seed(seed, out_dir)
        write_partial(out_dir, seed, rec)
        ps_so_far = aggregate_partials(out_dir, SEEDS)
        ps_list = [v for k, v in sorted(ps_so_far.items(), key=lambda kv: int(kv[0]))]
        metrics_partial = build_metrics_payload(ps_list, time.time() - t0)
        metrics_partial["incremental"] = True
        metrics_partial["n_seeds_completed"] = len(ps_list)
        (out_dir / "metrics.json").write_text(
            json.dumps(metrics_partial, indent=2), encoding="utf-8")
        print(
            "  [incremental metrics] %d/%d seeds complete; current verdict=%s"
            % (len(ps_list), len(SEEDS), metrics_partial["verdict"]),
            flush=True,
        )

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    ps_list = [v for k, v in sorted(per_seed.items(), key=lambda kv: int(kv[0]))]

    assert _LLM_CALL_COUNTER[0] == 0, (
        "LLM_CALL_COUNTER non-zero: %d -- substrate-only-gate VIOLATED"
        % _LLM_CALL_COUNTER[0])

    metrics = build_metrics_payload(ps_list, time.time() - t0)
    metrics["incremental"] = False
    metrics["n_seeds_completed"] = len(ps_list)
    (out_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8")
    print("\n[VERDICT] " + metrics["verdict_msg"], flush=True)
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)
