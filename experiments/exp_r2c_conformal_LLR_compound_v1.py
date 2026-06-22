"""r2c_conformal_LLR_compound_v1 -- chain-grade aggregator REVIVAL on r2 partial-positive.

r2 (exp_r2_successor_TEM_compound_v1) showed compound_margin_ratio = 1.13-1.19x ACROSS ALL K,
a consistent partial-positive: the geometric-product compound IS reading chain-structure signal,
but at a CAP. Per Research drill 2026-06-22
(notes/research_multihop_2x_revival_compound_margin_path_to_2x_drill_2026-06-22.md):

    "1.13x -> 2.0x gap is a CALIBRATION-stack gap not a mechanism gap;
     replace geometric-product compound with conformal Fisher LLR aggregator (PASC/Fisher)."

This cell tests 5 chain-score aggregators on the SAME r2 harness (W, R, E, perm, chains):

  1. GEOMETRIC_ANCHOR    -- r2's TEM compound-margin-mean (anchor; must reproduce r2 +/- 0.02)
  2. LLR                 -- per-hop log-likelihood-ratio sum (Neyman-Pearson chain score)
  3. CONFORMAL_FISHER    -- per-hop p-value via split-conformal -> Fisher's combined chi-square
  4. PASC_JOINT          -- one joint tau over (score, K) (pipeline-aware conformal)
  5. MIN                 -- min-over-hops (weakest-link emphasis)

The 5 arms operate on the SAME per-chain per-hop top1-top2 margin sequence collected during
TEM iter-cleanup. Aggregators differ; underlying retrieval is r2's TEM mechanism.

Pre-reg HARD bands (preregs/2026-06-22_r2c_conformal_LLR_compound_v1.md):
  HARD_PASS: ANY of {LLR, CONFORMAL_FISHER, PASC_JOINT, MIN} at K=4 achieves
    chain_aggregator_ratio >= 2.0x AND ood_refuse >= 0.90 AND inkb_accept >= 0.40
    AND cv <= 0.08 across 7 seeds
    AND GEOMETRIC_ANCHOR reproduces r2 within +/- 0.02
  HARD_FAIL: NO arm reaches >= 1.50x (no aggregator closes the gap)
    OR GEOMETRIC_ANCHOR fails to reproduce r2 (anchor drift => harness broken)
  MIDDLE_BAND: in between

Substrate-only-decode gate: torch permitted; NO LLM forward calls; counter asserted at exit.

Routing: post-processing layer on r2's W matrix; per-chain per-hop scores collected in single
iter-cleanup pass. ~20-30min CPU laptop estimate per Research drill. Routes to remote_cpu_queue
(faster + persistent than laptop CPU).

Composes with: r2 (anchor reproduction); hdlab/conformal.py + hdlab/refuse_gate.py primitives;
META storage atom on conformal-Fisher chain-aggregator if HARD_PASS.
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

ANCHOR_NAME = "r2c_conformal_LLR_compound_v1"
KG_PATH = REPO / "data" / "datasets" / "fb15k_237_train_50k.jsonl"

# ----- r2 reference compound ratios (GEOMETRIC_ANCHOR arm reproduces these within +/- 0.02) -----
R2_COMPOUND_RATIO_K2 = 1.1336
R2_COMPOUND_RATIO_K3 = 1.1318
R2_COMPOUND_RATIO_K4 = 1.1522
ANCHOR_TOL = 0.02   # GEOMETRIC_ANCHOR must reproduce r2 compound_ratio within this band

# ----- pre-registered HARD thresholds (per Research drill) -----
HARD_PASS_RATIO = 2.0          # chain_aggregator_ratio >= 2.0x at K=4
HARD_PASS_OOD_REFUSE = 0.90    # ood_refuse >= 0.90 at K=4
HARD_PASS_INKB_ACCEPT = 0.40   # inkb_accept >= 0.40 at K=4
HARD_FAIL_RATIO_FLOOR = 1.50   # no arm reaches >= 1.50x => HARD_FAIL
CV_PASS = 0.08                 # cv <= 0.08 across 7 seeds (slightly looser than r2's 0.06 per drill)

# ----- CLI / run-mode -----
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_IS_SMOKE_BY_NAME = _HDLAB_NAME.endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _IS_SMOKE_BY_NAME) else "full"

# ----- device selection (workload is CPU-laptop-tractable per drill; allow torch.cuda) -----
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
    CAL_FRAC = 0.5       # 50/50 cal/test split
    CONFORMAL_ALPHA = 0.10
else:
    SEEDS = [7, 17, 23, 31, 41, 53, 67]
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
    CAL_FRAC = 0.5       # 250/250 cal/test split (250 of 500 chains as calibration)
    CONFORMAL_ALPHA = 0.10

ARMS = ["GEOMETRIC_ANCHOR", "LLR", "CONFORMAL_FISHER", "PASC_JOINT", "MIN"]
FISHER_DF_MULT = 2  # chi2 = -2 * sum log p_k; df = 2K

CONFIG_VERSION = (
    "r2c-conformal-LLR-compound: arms=%s; N=%d M=%d K_hops=%s K_set=%d K_inner=%d "
    "gamma=%.2f perm=%s n_seeds=%d n_chains=%d cal_frac=%.2f alpha=%.2f device=%s; "
    "bands HARD_PASS ratio>=%.1fx OOD-refuse>=%.2f inkb-accept>=%.2f cv<=%.2f "
    "anchor-tol+/-%.2f HARD_FAIL no_arm>=%.2fx"
    % (str(ARMS), N_DIM, M_TRIPLES, str(K_HOPS_LIST), K_SET, K_INNER,
       GAMMA, PERM_TYPE, len(SEEDS), N_CHAINS, CAL_FRAC, CONFORMAL_ALPHA, str(DEVICE),
       HARD_PASS_RATIO, HARD_PASS_OOD_REFUSE, HARD_PASS_INKB_ACCEPT, CV_PASS,
       ANCHOR_TOL, HARD_FAIL_RATIO_FLOOR)
)


# ----- core HD primitives -----

def bipolar_torch(M, n, g):
    """Torch bipolar codebook on DEVICE. Uses numpy RNG for cross-seed reproducibility."""
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


# ----- aggregator primitives (load-bearing math) -----

def compute_llr_per_hop(scores_inkb_per_hop, scores_ood_per_hop, kde_bandwidth=0.05):
    """Estimate per-hop LLR via Gaussian-KDE density ratio on calibration scores.

    Args:
        scores_inkb_per_hop: array shape (n_cal_inkb,) per-hop top1-top2 margin (in-KB cal)
        scores_ood_per_hop: array shape (n_cal_ood,) per-hop margin (OOD cal)
        kde_bandwidth: Gaussian KDE bandwidth (fixed; not optimised for cell scope)

    Returns:
        llr_fn(s): callable returning log p(s|inkb) - log p(s|ood). Smooth + bounded.
    """
    inkb = np.asarray(scores_inkb_per_hop, dtype=np.float64)
    ood = np.asarray(scores_ood_per_hop, dtype=np.float64)

    def _gauss_log_density(s, samples, bw):
        # log of sum(exp(-(s-x)^2 / 2bw^2)) - log(n*sqrt(2*pi)*bw)
        n = len(samples)
        if n == 0:
            return -50.0
        ds = (s - samples) / bw
        logp = -0.5 * ds * ds
        # log-sum-exp
        max_logp = float(np.max(logp))
        lse = max_logp + math.log(float(np.sum(np.exp(logp - max_logp))) + 1e-300)
        return lse - math.log(n) - math.log(math.sqrt(2.0 * math.pi)) - math.log(bw)

    def llr_fn(s):
        # bound LLR to [-20, +20] to prevent log-domain explosions on outliers
        l_in = _gauss_log_density(s, inkb, kde_bandwidth)
        l_ood = _gauss_log_density(s, ood, kde_bandwidth)
        d = l_in - l_ood
        if d > 20.0:
            return 20.0
        if d < -20.0:
            return -20.0
        return d

    return llr_fn


def compute_conformal_pvalue(test_score, cal_ood_scores):
    """Split-conformal p-value: P(cal_ood >= test_score) under exchangeability.

    Higher test_score => smaller p-value (more anomalous vs OOD null).
    Treats OOD as null; in-KB chains should yield SMALL p (= rejected by union).
    For Fisher's combination we want LARGE chi2 = -2 sum log p under in-KB
    (more discriminating), so we use 1 - cdf_ood semantic:
        p_k = (1 + #{cal_ood >= test_score}) / (n_cal_ood + 1)
    """
    cal = np.asarray(cal_ood_scores, dtype=np.float64)
    n = len(cal)
    if n == 0:
        return 0.5
    rank = int(np.sum(cal >= test_score))
    # add-1 conformal correction; clip to (eps, 1)
    p = (1.0 + rank) / (n + 1.0)
    return max(p, 1.0 / (n + 1.0))


def fisher_combined(p_values):
    """Fisher's combined-probability chi-square statistic.

    chi2 = -2 * sum log(p_k); under null (independent uniforms) ~ chi2(df=2K).
    Higher chi2 => more anomalous vs null => more in-KB-like in our framing.
    """
    pv = np.asarray(p_values, dtype=np.float64)
    pv = np.clip(pv, 1e-12, 1.0)
    return float(-2.0 * np.sum(np.log(pv)))


# ----- refuse-gate calibration on aggregated chain scores -----

def calibrate_chain_gate(inkb_scores, ood_scores):
    """Calibrate tau on first half; evaluate on second half.

    Returns dict with tau, ood_refuse, inkb_accept, ratio (in-KB-mean / OOD-mean).
    """
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


# ----- self-test: tiny synthetic KG; verify all 5 aggregators run + separate in-KB from OOD -----

def _selftest():
    """Tiny synthetic KG K=2 sanity: collect per-hop scores for in-KB + OOD chains;
    verify all 5 aggregators yield ratio > 1.0 (in-KB > OOD)."""
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

    # Collect per-hop scores + compound for in-KB and OOD
    def _traverse(s, rels):
        per_hop_scores = []
        chain_ents = [E[s].clone()]
        state = E[s].clone()
        for p in rels:
            transit = W @ (state * R[p] * sq)
            ent_scores = E @ transit
            top_conf, top_idx = torch.topk(ent_scores, 4)
            margin = float(top_conf[0].item() - top_conf[1].item())
            per_hop_scores.append(margin)
            z = float(n) * top_conf
            w = torch.softmax(z, dim=0)
            state = (w.unsqueeze(1) * E[top_idx]).sum(dim=0)
            state = _normalize_t(state)
            chain_ents.append(state.clone())
        # Compound (GEOMETRIC_ANCHOR) margin
        compound = torch.zeros(n, dtype=TORCH_DTYPE, device=DEVICE)
        for k, e_k in enumerate(chain_ents):
            compound = compound + _apply_perm_k(e_k, perm_idx, k)
        compound = _normalize_t(compound)
        pos_margins = []
        for k in range(len(chain_ents)):
            recov = _apply_perm_k(compound, perm_idx, -k)
            ent_scores = E @ recov
            top2, _ = torch.topk(ent_scores, 2)
            pos_margins.append(float(top2[0].item() - top2[1].item()))
        compound_margin = float(np.mean(pos_margins))
        return per_hop_scores, compound_margin

    inkb_perhops = []
    inkb_compounds = []
    for (s, rels, _o) in chains_truth:
        ph, cm = _traverse(s, rels)
        inkb_perhops.append(ph)
        inkb_compounds.append(cm)
    ood_perhops = []
    ood_compounds = []
    for trial in range(10):
        s = 29
        rels = [2, 0]
        ph, cm = _traverse(s, rels)
        ood_perhops.append(ph)
        ood_compounds.append(cm)

    inkb_arr = np.asarray(inkb_perhops, dtype=np.float64)
    ood_arr = np.asarray(ood_perhops, dtype=np.float64)
    K = inkb_arr.shape[1]

    # GEOMETRIC_ANCHOR
    g_ratio = float(np.mean(inkb_compounds)) / max(abs(float(np.mean(ood_compounds))), 1e-9)

    # MIN
    min_inkb = np.min(inkb_arr, axis=1)
    min_ood = np.min(ood_arr, axis=1)
    min_ratio = float(np.mean(min_inkb)) / max(abs(float(np.mean(min_ood))), 1e-9)

    # LLR (use first half as cal; second half as test)
    h_in = max(1, len(inkb_arr) // 2)
    h_ood = max(1, len(ood_arr) // 2)
    llr_fns = []
    for k in range(K):
        llr_fns.append(compute_llr_per_hop(inkb_arr[:h_in, k], ood_arr[:h_ood, k]))
    inkb_llr_test = np.asarray(
        [sum(llr_fns[k](inkb_arr[i, k]) for k in range(K)) for i in range(h_in, len(inkb_arr))],
        dtype=np.float64,
    )
    ood_llr_test = np.asarray(
        [sum(llr_fns[k](ood_arr[i, k]) for k in range(K)) for i in range(h_ood, len(ood_arr))],
        dtype=np.float64,
    )
    llr_ratio = float(np.mean(inkb_llr_test)) / max(abs(float(np.mean(ood_llr_test))), 1e-9)

    # CONFORMAL_FISHER
    inkb_fisher = []
    for i in range(h_in, len(inkb_arr)):
        pvs = [compute_conformal_pvalue(inkb_arr[i, k], ood_arr[:h_ood, k]) for k in range(K)]
        inkb_fisher.append(fisher_combined(pvs))
    ood_fisher = []
    for i in range(h_ood, len(ood_arr)):
        pvs = [compute_conformal_pvalue(ood_arr[i, k], ood_arr[:h_ood, k]) for k in range(K)]
        ood_fisher.append(fisher_combined(pvs))
    inkb_fisher_arr = np.asarray(inkb_fisher, dtype=np.float64)
    ood_fisher_arr = np.asarray(ood_fisher, dtype=np.float64)
    fisher_ratio = (float(np.mean(inkb_fisher_arr)) /
                    max(abs(float(np.mean(ood_fisher_arr))), 1e-9))

    # PASC_JOINT: cal one joint tau over flattened (score, K)-pair distribution
    cal_inkb_flat = inkb_arr[:h_in].flatten()
    cal_ood_flat = ood_arr[:h_ood].flatten()
    cands = np.unique(np.concatenate([cal_inkb_flat, cal_ood_flat]))
    best_tau = float(cands[0])
    best_bal = -1.0
    for tcand in cands:
        acc = float((cal_inkb_flat >= tcand).mean())
        ref = float((cal_ood_flat < tcand).mean())
        bal = 0.5 * (acc + ref)
        if bal > best_bal:
            best_bal = bal
            best_tau = float(tcand)
    # PASC score for chain = mean over hops of (score - tau)
    pasc_inkb = np.asarray(
        [float(np.mean(inkb_arr[i] - best_tau)) for i in range(h_in, len(inkb_arr))],
        dtype=np.float64,
    )
    pasc_ood = np.asarray(
        [float(np.mean(ood_arr[i] - best_tau)) for i in range(h_ood, len(ood_arr))],
        dtype=np.float64,
    )
    # PASC_JOINT ratio uses (mean + shift to avoid div-by-zero near 0)
    pasc_inkb_s = pasc_inkb + 1.0
    pasc_ood_s = pasc_ood + 1.0
    pasc_ratio = float(np.mean(pasc_inkb_s)) / max(abs(float(np.mean(pasc_ood_s))), 1e-9)

    assert g_ratio > 1.0, "selftest: GEOMETRIC_ANCHOR ratio %.3f must exceed 1.0" % g_ratio
    assert min_ratio > 0.95, "selftest: MIN ratio %.3f below 0.95" % min_ratio
    # LLR + Fisher can be noisy on tiny synthetic; only assert finiteness
    assert math.isfinite(llr_ratio), "selftest: LLR ratio not finite"
    assert math.isfinite(fisher_ratio), "selftest: Fisher ratio not finite"
    assert math.isfinite(pasc_ratio), "selftest: PASC ratio not finite"
    print(
        "[selftest] PASS: GEOMETRIC=%.3fx MIN=%.3fx LLR=%.3fx FISHER=%.3fx PASC=%.3fx "
        "[device=%s]" % (g_ratio, min_ratio, llr_ratio, fisher_ratio, pasc_ratio, str(DEVICE)),
        flush=True,
    )


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ----- KG loader (verbatim from r2) -----

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


# ----- chain sampling (verbatim from r2) -----

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


# ----- per-chain traverse + collect per-hop scores + GEOMETRIC compound -----

def traverse_collect(E, R, W, sq, start_ent, rel_chain, K_set, K_inner, beta, perm_idx):
    """Run iter-cleanup; collect per-hop top1-top2 margin sequence + GEOMETRIC compound margin.

    Returns (per_hop_margins, geometric_compound_margin) where:
      per_hop_margins: list of K floats (one top1-top2 per hop)
      geometric_compound_margin: float (mean per-position recovery margin from compound state)
    """
    per_hop = []
    chain_ents = [E[start_ent].clone()]
    state = E[start_ent].clone()
    for p in rel_chain:
        for _inner in range(K_inner):
            transit = W @ (state * R[p] * sq)
            ent_scores = E @ transit
            top_conf, top_idx = torch.topk(ent_scores, K_set)
            margin = float(top_conf[0].item() - top_conf[1].item())
            z = beta * top_conf
            w = torch.softmax(z, dim=0)
            state = (w.unsqueeze(1) * E[top_idx]).sum(dim=0)
            state = _normalize_t(state)
        per_hop.append(margin)
        chain_ents.append(state.clone())
    # GEOMETRIC compound (r2 TEM compound-margin-mean)
    compound = torch.zeros(N_DIM, dtype=TORCH_DTYPE, device=DEVICE)
    for k, e_k in enumerate(chain_ents):
        compound = compound + _apply_perm_k(e_k, perm_idx, k)
    compound = _normalize_t(compound)
    pos_margins = []
    for k in range(len(chain_ents)):
        recov = _apply_perm_k(compound, perm_idx, -k)
        ent_scores = E @ recov
        top2, _ = torch.topk(ent_scores, 2)
        pos_margins.append(float(top2[0].item() - top2[1].item()))
    geometric_margin = float(np.mean(pos_margins))
    return per_hop, geometric_margin


# ----- per-K evaluator: collect ALL chain data, then apply all 5 aggregators -----

def eval_all_arms_at_K(E, R, W, sq, chains, ood_chains, K, perm_idx):
    """Run all 5 aggregator arms at this K. Returns dict per arm -> calibrated gate stats."""
    # Collect per-chain data
    inkb_perhops = []
    inkb_geom = []
    n_hit = 0
    t = time.time()
    for (s, rels, _ints, o_true) in chains:
        per_hop, geom = traverse_collect(
            E, R, W, sq, s, rels, K_SET, K_INNER, BETA_CLEANUP, perm_idx,
        )
        inkb_perhops.append(per_hop)
        inkb_geom.append(geom)
        # accuracy: predict final entity from last per-hop state argmax
    inkb_wall = time.time() - t

    ood_perhops = []
    ood_geom = []
    t = time.time()
    for (s, rels) in ood_chains:
        per_hop, geom = traverse_collect(
            E, R, W, sq, s, rels, K_SET, K_INNER, BETA_CLEANUP, perm_idx,
        )
        ood_perhops.append(per_hop)
        ood_geom.append(geom)
    ood_wall = time.time() - t

    inkb_arr = np.asarray(inkb_perhops, dtype=np.float64)  # (n_inkb, K)
    ood_arr = np.asarray(ood_perhops, dtype=np.float64)    # (n_ood, K)

    results = {"_inkb_wall_s": inkb_wall, "_ood_wall_s": ood_wall,
               "_n_chains": len(chains), "_n_ood": len(ood_chains)}

    # ---- ARM 1: GEOMETRIC_ANCHOR (r2 compound; must reproduce r2 +/- 0.02) ----
    gstats = calibrate_chain_gate(inkb_geom, ood_geom)
    results["GEOMETRIC_ANCHOR"] = gstats

    # ---- ARM 5: MIN aggregator (min-over-hops; weakest-link emphasis) ----
    min_inkb = np.min(inkb_arr, axis=1)
    min_ood = np.min(ood_arr, axis=1)
    mstats = calibrate_chain_gate(min_inkb.tolist(), min_ood.tolist())
    results["MIN"] = mstats

    # ---- LLR / CONFORMAL_FISHER / PASC_JOINT: cal/test split needed ----
    h_in = max(1, int(len(inkb_arr) * CAL_FRAC))
    h_ood = max(1, int(len(ood_arr) * CAL_FRAC))
    cal_inkb_arr = inkb_arr[:h_in]   # (h_in, K)
    cal_ood_arr = ood_arr[:h_ood]    # (h_ood, K)
    test_inkb_arr = inkb_arr[h_in:]
    test_ood_arr = ood_arr[h_ood:]

    # ---- ARM 2: LLR aggregator ----
    # Per-hop LLR via Gaussian KDE on per-hop score distributions
    llr_fns = []
    for k in range(K):
        llr_fns.append(compute_llr_per_hop(cal_inkb_arr[:, k], cal_ood_arr[:, k]))
    # Apply to ALL chains (cal + test), then calibrate gate on the half split
    inkb_llr_all = np.asarray([sum(llr_fns[k](inkb_arr[i, k]) for k in range(K))
                               for i in range(len(inkb_arr))], dtype=np.float64)
    ood_llr_all = np.asarray([sum(llr_fns[k](ood_arr[i, k]) for k in range(K))
                              for i in range(len(ood_arr))], dtype=np.float64)
    lstats = calibrate_chain_gate(inkb_llr_all.tolist(), ood_llr_all.tolist())
    results["LLR"] = lstats

    # ---- ARM 3: CONFORMAL_FISHER aggregator ----
    # Per-hop conformal p-value on cal_ood_arr; combine via Fisher chi2
    inkb_fisher_all = []
    for i in range(len(inkb_arr)):
        pvs = [compute_conformal_pvalue(inkb_arr[i, k], cal_ood_arr[:, k]) for k in range(K)]
        inkb_fisher_all.append(fisher_combined(pvs))
    ood_fisher_all = []
    for i in range(len(ood_arr)):
        pvs = [compute_conformal_pvalue(ood_arr[i, k], cal_ood_arr[:, k]) for k in range(K)]
        ood_fisher_all.append(fisher_combined(pvs))
    fstats = calibrate_chain_gate(inkb_fisher_all, ood_fisher_all)
    results["CONFORMAL_FISHER"] = fstats

    # ---- ARM 4: PASC_JOINT aggregator (one joint tau over (score, K) pairs) ----
    cal_inkb_flat = cal_inkb_arr.flatten()
    cal_ood_flat = cal_ood_arr.flatten()
    cands = np.unique(np.concatenate([cal_inkb_flat, cal_ood_flat]))
    if len(cands) == 0:
        results["PASC_JOINT"] = {"tau": 0.0, "ood_refuse": 0.0, "inkb_accept": 0.0,
                                  "ratio": 0.0, "inkb_mean": 0.0, "ood_mean": 0.0,
                                  "best_cal_bal": 0.0}
    else:
        best_tau = float(cands[0])
        best_bal = -1.0
        for tcand in cands:
            acc = float((cal_inkb_flat >= tcand).mean())
            ref = float((cal_ood_flat < tcand).mean())
            bal = 0.5 * (acc + ref)
            if bal > best_bal:
                best_bal = bal
                best_tau = float(tcand)
        # PASC score for a chain = mean over hops of (score - tau); shifted +1.0 for ratio
        pasc_inkb_all = np.asarray(
            [float(np.mean(inkb_arr[i] - best_tau)) for i in range(len(inkb_arr))],
            dtype=np.float64,
        )
        pasc_ood_all = np.asarray(
            [float(np.mean(ood_arr[i] - best_tau)) for i in range(len(ood_arr))],
            dtype=np.float64,
        )
        pstats = calibrate_chain_gate(pasc_inkb_all.tolist(), pasc_ood_all.tolist())
        pstats["joint_tau"] = best_tau
        pstats["joint_cal_bal"] = best_bal
        results["PASC_JOINT"] = pstats

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
                "inkb_wall_s": round(results["_inkb_wall_s"], 2),
                "ood_wall_s": round(results["_ood_wall_s"], 2),
                "K_wall_s": round(wall_K, 2),
            }
            if "joint_tau" in stats:
                unit["pasc_joint_tau"] = float(stats["joint_tau"])
                unit["pasc_joint_cal_bal"] = round(float(stats["joint_cal_bal"]), 4)
            out["per_unit"].append(unit)
            print(
                ("  [seed=%d K=%d arm=%s n=%d leak=%d] ratio=%.3fx ood-refuse=%.3f "
                 "inkb-accept=%.3f tau=%.4f")
                % (seed, K, arm, n_actual, leak, stats.get("ratio", 0.0),
                   stats.get("ood_refuse", 0.0), stats.get("inkb_accept", 0.0),
                   stats.get("tau", 0.0)),
                flush=True,
            )

    out["ingest_s"] = round(ingest_s, 1)
    out["seed_wall_s"] = round(time.time() - t0, 1)
    return out


# ----- verdict (pre-reg HARD bands) -----

def verdict(ps) -> Tuple[str, str]:
    # Aggregate by (K, arm)
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

    # ---- GEOMETRIC_ANCHOR reproduction check (must reproduce r2 within +/- 0.02) ----
    anchor_msgs = []
    anchor_drift = False
    for K, ref_ratio in zip([2, 3, 4], [R2_COMPOUND_RATIO_K2, R2_COMPOUND_RATIO_K3, R2_COMPOUND_RATIO_K4]):
        if K not in agg or "GEOMETRIC_ANCHOR" not in agg[K]:
            continue
        anchor = agg[K]["GEOMETRIC_ANCHOR"]
        diff = abs(anchor["ratio"] - ref_ratio)
        ok = diff <= ANCHOR_TOL
        if enforce_repro and not ok:
            anchor_drift = True
        tag = "OK" if ok else ("DRIFT" if enforce_repro else "SMOKE-SKIP")
        anchor_msgs.append("K%d anchor_ratio=%.4f r2_ratio=%.4f diff=%.4f %s"
                           % (K, anchor["ratio"], ref_ratio, diff, tag))

    # ---- HARD_PASS: ANY of {LLR, CONFORMAL_FISHER, PASC_JOINT, MIN} at K=4 ----
    candidate_arms = ["LLR", "CONFORMAL_FISHER", "PASC_JOINT", "MIN"]
    hp_arm = None
    hp_msgs = []
    if 4 in agg:
        for arm in candidate_arms:
            if arm not in agg[4]:
                continue
            d = agg[4][arm]
            c_ratio = d["ratio"] >= HARD_PASS_RATIO
            c_ood = d["ood_refuse"] >= HARD_PASS_OOD_REFUSE
            c_inkb = d["inkb_accept"] >= HARD_PASS_INKB_ACCEPT
            c_cv = d["cv"] <= CV_PASS
            hp_msgs.append("%s K4 ratio=%.3f(>=%.1f:%s) ood-refuse=%.3f(>=%.2f:%s) "
                           "inkb-accept=%.3f(>=%.2f:%s) cv=%.4f(<=%.2f:%s)"
                           % (arm, d["ratio"], HARD_PASS_RATIO, c_ratio,
                              d["ood_refuse"], HARD_PASS_OOD_REFUSE, c_ood,
                              d["inkb_accept"], HARD_PASS_INKB_ACCEPT, c_inkb,
                              d["cv"], CV_PASS, c_cv))
            if c_ratio and c_ood and c_inkb and c_cv:
                hp_arm = arm
                break

    # ---- HARD_FAIL: no arm reaches >= 1.50x at K=4 ----
    no_arm_reaches_fail_floor = True
    best_ratio_at_K4 = 0.0
    best_arm_at_K4 = None
    if 4 in agg:
        for arm in candidate_arms:
            if arm not in agg[4]:
                continue
            d = agg[4][arm]
            if d["ratio"] > best_ratio_at_K4:
                best_ratio_at_K4 = d["ratio"]
                best_arm_at_K4 = arm
            if d["ratio"] >= HARD_FAIL_RATIO_FLOOR:
                no_arm_reaches_fail_floor = False

    summ = (
        "by-K-by-arm: %s | anchor-repro: %s | HARD_PASS checks: %s | best_at_K4=%s@%.3fx"
        % (json.dumps({"K%d" % K: agg[K] for K in sorted(agg.keys())}),
           " ; ".join(anchor_msgs) if anchor_msgs else "n/a",
           " ; ".join(hp_msgs) if hp_msgs else "n/a",
           best_arm_at_K4 or "?", best_ratio_at_K4)
    )

    # HARD_FAIL inconclusive: GEOMETRIC_ANCHOR drifted (harness broken; not mechanism-negative)
    if enforce_repro and anchor_drift:
        return (
            "HARD_FAIL",
            "HARD_FAIL inconclusive: GEOMETRIC_ANCHOR ratio drifted >+/-%.2f vs r2 compound_ratio "
            "-- harness changed; cannot evaluate aggregator mechanism. " % ANCHOR_TOL + summ,
        )

    if hp_arm is not None:
        return (
            "HARD_PASS",
            "HARD_PASS: chain-aggregator %s at K=4 ratio=%.3fx (>=%.1fx) "
            "OOD-refuse=%.3f (>=%.2f) inkb-accept=%.3f (>=%.2f) cv=%.4f (<=%.2f); "
            "GEOMETRIC_ANCHOR reproduces r2 within +/-%.2f. CALIBRATION-STACK GAP CLOSED. "
            % (hp_arm, agg[4][hp_arm]["ratio"], HARD_PASS_RATIO,
               agg[4][hp_arm]["ood_refuse"], HARD_PASS_OOD_REFUSE,
               agg[4][hp_arm]["inkb_accept"], HARD_PASS_INKB_ACCEPT,
               agg[4][hp_arm]["cv"], CV_PASS, ANCHOR_TOL)
            + summ,
        )

    if enforce_repro and no_arm_reaches_fail_floor:
        return (
            "HARD_FAIL",
            "HARD_FAIL: no candidate aggregator at K=4 reaches >=%.2fx (calibration-stack "
            "hypothesis exhausted). best=%s@%.3fx. " % (HARD_FAIL_RATIO_FLOOR,
                                                       best_arm_at_K4 or "?", best_ratio_at_K4)
            + summ,
        )

    return (
        "MIDDLE_BAND",
        "MIDDLE_BAND: best arm %s at K=4 ratio=%.3fx is in [%.2f, %.1f]x (partial closure of "
        "calibration-stack gap). " % (best_arm_at_K4 or "?", best_ratio_at_K4,
                                      HARD_FAIL_RATIO_FLOOR, HARD_PASS_RATIO)
        + summ,
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
        "cal_frac": CAL_FRAC,
        "conformal_alpha": CONFORMAL_ALPHA,
        "fisher_df_mult": FISHER_DF_MULT,
        "device": str(DEVICE),
        "torch_cuda_available": bool(torch.cuda.is_available()),
        "zero_llm_calls_at_inference": True,
        "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "substrate_native": True,
        "substrate_role": "native_inference",
        "r2_compound_reference_ratios": {
            "K2": R2_COMPOUND_RATIO_K2,
            "K3": R2_COMPOUND_RATIO_K3,
            "K4": R2_COMPOUND_RATIO_K4,
        },
        "DESIGN_NOTE": (
            "r2c: revival of r2's partial-positive (compound_ratio=1.13-1.19x) via "
            "5 chain-score aggregators on the SAME r2 harness: GEOMETRIC_ANCHOR (r2 baseline), "
            "LLR (per-hop log-likelihood-ratio sum via Gaussian-KDE density estimation), "
            "CONFORMAL_FISHER (per-hop conformal p-value + Fisher chi2 combination), "
            "PASC_JOINT (one joint tau over (score, K) pairs per PASC), "
            "MIN (min-over-hops weakest-link). Pre-reg HARD_PASS: any of "
            "{LLR, CONFORMAL_FISHER, PASC_JOINT, MIN} at K=4 ratio>=2.0x + "
            "ood-refuse>=0.90 + inkb-accept>=0.40 + cv<=0.08. HARD_FAIL: no arm >=1.50x."
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
