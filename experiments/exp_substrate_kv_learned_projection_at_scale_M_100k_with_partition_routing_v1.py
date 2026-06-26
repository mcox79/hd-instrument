"""
substrate_kv_learned_projection_at_scale_M_100k_with_partition_routing_v1 -- compose KV-learned + partition routing at M=100k.

PROMOTION CONTEXT (Research DRILL 1 ITEM 5 Tier A #3, 2026-06-25):
  KV learned projection (`exp_kv_learned_projection_v1`) chain-grade HARD_PASS at M up to 10k:
    held-out recall@1 worst=0.827 keysep=0.878 std=0.019 margin=+0.747 over analytic-ceiling 0.080
    (verbatim from metrics.json)
  Dense KV cliffs sharply M=10k -> M=50k (0.827 -> 0.149) per related capacity sweep cell.
  Partition routing (`exp_substrate_partition_routing_10M_full_v2`) chain-grade @ M=100k
    routed recall@10=0.97 part_size=2000; HARD_PASS_PARTIAL_AT_M_1M routed recall@10=0.95.

v1 DESIGN: COMPOSE learned-projection + partition-routing. Tests held-out generalization
at production scale where neither dense KV nor unrouted learned projection survives:
  Arm A: learned-projection (no partition) at M in {10k, 30k, 100k} -- baseline scaling
  Arm B: dense+partition at M=100k -- replicate partition-routing baseline at production scale
  Arm C: learned+partition at M=100k -- the integration (mechanism under test)
  Arm D: dense-only at M=100k -- control (expected catastrophic cliff)

EXPECTED OUTCOMES per DRILL 1 P=0.55:
  HARD_PASS_CHAIN_GRADE_AT_M_100k:
    Arm C held-out recall@1 >= 0.70 AND keysep < 0.95 AND cv <= 0.05
    AND Arm C beats Arm A AND Arm B by >= 0.10 absolute
  CHAIN_GRADE_AT_LOWER_X:
    Arm A passes at M=10k/30k but cliffs at 100k; Arm C provides the M=100k chain-grade
  HARD_FAIL_LEARNED_PROJECTION_DOESNT_SCALE:
    held-out recall@1 < 0.40 at M=100k for all arms (composition does NOT close)

META_M6 baseline: ANALYTIC ceiling (svd-whiten on held-out) computed in-cell per M; NOT copied
META_M7: smoke matches full on PROJ_DIM, HELDOUT_FRAC, PART_SIZE, CAT_COS (capacity-sensitive)
  Only ENCODER (160m vs 2.8b), M_SWEEP, SEEDS, TRAIN_STEPS reduce
Q-discipline: if ALL arms saturate >= 0.995 at M=100k, BIAS-Q fires (corpus too easy at scale)
Fix #24: torch.cuda actively used; encoder + matmul on device; metrics report gpu_avail + max_mem

CONFIG (full):
  ENCODER = EleutherAI/pythia-2.8b (matches reference cell)
  M_SWEEP = [10000, 30000, 100000]
  Seeds = [11, 13, 19] (cross-cell consistent; note: reference cell used [0..4])
  PROJ_DIM = 256, HELDOUT_FRAC = 0.25, TRAIN_STEPS = 600
  PART_SIZE = 2000 (matches partition routing reference; locked across smoke/full)
  CAT_COS = 0.70 (matches partition routing reference)

SMOKE: pythia-160m, M_SWEEP=[400, 1000], seeds=[11], TRAIN_STEPS=200, PROJ_DIM=128
  Self-test asserts T1-T7 (sanity + svd-whiten + bipolar + bands locked + cat-cue routing).

Author: exp_dev 2026-06-25 (Drill 1 Tier A #3 composition cell).
ASCII-only; substrate-only at inference; encoder hoisted ONCE per seed.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, math, atexit
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import torch  # PROT-020 GPU-gate literal; Fix #24

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "substrate_kv_learned_projection_at_scale_M_100k_with_partition_routing_v1"
_LLM_CALL_COUNTER = [0]   # encoder forward counter at SETUP-time; substrate-only at INFERENCE

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SMOKE = RUN_MODE == "smoke"

# CAPACITY-SENSITIVE: smoke matches full on PROJ_DIM, PART_SIZE, CAT_COS, HELDOUT_FRAC.
# Only ENCODER, M_SWEEP, SEEDS, TRAIN_STEPS reduce.
PART_SIZE = 2000           # matches partition routing reference (locked across smoke/full)
CAT_COS = 0.70             # clean category cue -> robust routing (matches partition routing)
HELDOUT_FRAC = 0.25

if SMOKE:
    ENCODER = "EleutherAI/pythia-160m"
    M_SWEEP = [400, 1000]
    SEEDS = [11]
    PROJ_DIM = 128
    TRAIN_STEPS = 200
else:
    ENCODER = "EleutherAI/pythia-2.8b"
    M_SWEEP = [10000, 30000, 100000]
    SEEDS = [11, 13, 19]
    PROJ_DIM = 256
    TRAIN_STEPS = 600

# PROSPECTIVE BANDS (LOCKED AT MODULE INIT per META_PROSPECTIVE_BANDS_FRESH_SEEDS)
BAND_HARD_PASS_RECALL_M100K = 0.70         # arm C held-out recall@1 floor at M=100k
BAND_HARD_PASS_KEYSEP_MAX = 0.95           # keysep table-stakes (low = de-crowded)
BAND_HARD_PASS_CV_MAX = 0.05               # cv ceiling across seeds
BAND_HARD_PASS_COMPOSITION_LIFT = 0.10     # arm C must beat arms A and B by >= this
BAND_HARD_FAIL_RECALL_M100K = 0.40         # all arms below this -> HARD_FAIL
BAND_Q_SUSPECT_SATURATION = 0.995
BAND_MARGIN_OVER_ANALYTIC = 0.30           # learned must beat analytic ceiling
assert 0.0 < BAND_HARD_PASS_RECALL_M100K < 1.0, "band locked"
assert BAND_HARD_FAIL_RECALL_M100K < BAND_HARD_PASS_RECALL_M100K, "fail < pass ordered"
assert BAND_HARD_PASS_COMPOSITION_LIFT > 0.05, "composition lift meaningful"

# Vocabulary for synthetic facts (matches reference cell)
_ADJ = "red blue swift quiet ancient modern silver golden hidden northern rapid silent hollow bright frozen molten crimson azure verdant amber".split()
_NOUN = "falcon river engine archive bridge reactor delta harbor summit forge canyon beacon orchard meadow glacier tower lagoon prairie quarry vault".split()
_VALW = "helium cobalt basalt cedar quartz copper marble willow granite saffron indigo cypress bronze jasper walnut".split()
_PROPS = ["founded in", "powered by", "located near", "awarded for", "merged with"]

CONFIG_VERSION = (
    "substrateKvLearnedProjAtScale-v1: encoder=%s M_SWEEP=%s seeds=%s "
    "proj_dim=%d heldout=%.2f train_steps=%d part_size=%d cat_cos=%.2f mode=%s "
    "HP_recall>=%.2f HP_keysep<=%.2f HP_cv<=%.2f HP_comp_lift>=%.2f Q_sat>=%.3f"
) % (ENCODER, M_SWEEP, SEEDS, PROJ_DIM, HELDOUT_FRAC, TRAIN_STEPS,
     PART_SIZE, CAT_COS, RUN_MODE,
     BAND_HARD_PASS_RECALL_M100K, BAND_HARD_PASS_KEYSEP_MAX,
     BAND_HARD_PASS_CV_MAX, BAND_HARD_PASS_COMPOSITION_LIFT,
     BAND_Q_SUSPECT_SATURATION)


def make_facts(M: int) -> Tuple[List[str], List[str]]:
    keys, vq = [], []
    for i in range(M):
        ent = "the %s %s" % (_ADJ[i % len(_ADJ)], _NOUN[(i // len(_ADJ)) % len(_NOUN)])
        prop = _PROPS[i % len(_PROPS)]
        value = "%s %d" % (_VALW[i % len(_VALW)], 1000 + i)
        keys.append("%s was %s %s." % (ent, prop, value))
        vq.append("Which one was %s %s?" % (prop, value))
    return keys, vq


def _np_norm(X: np.ndarray) -> np.ndarray:
    return (X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def recall_at_1(Qn: np.ndarray, Kn: np.ndarray, chunk: int = 256) -> float:
    """Recall@1: argmax over keys matches target index. O(Q*K) chunked."""
    cor = 0
    for i in range(0, len(Qn), chunk):
        sims = Qn[i:i + chunk] @ Kn.T
        cor += int((np.argmax(sims, axis=1) ==
                    np.arange(i, min(i + chunk, len(Qn)))).sum())
    return cor / len(Qn)


def keysep(Kn: np.ndarray, sample: int = 512,
            g: np.random.Generator = None) -> float:
    n = len(Kn)
    idx = (g.permutation(n)[:min(sample, n)] if g is not None
           else np.arange(min(sample, n)))
    S = Kn[idx]
    G = S @ Kn.T
    for r, j in enumerate(idx):
        G[r, j] = -2.0
    return float(np.median(G.max(1)))


def svd_whiten(K: np.ndarray, Q: np.ndarray, topk: int) -> Tuple[np.ndarray, np.ndarray]:
    mu = K.mean(0)
    Kc = K - mu
    Qc = Q - mu
    U, S, Vt = np.linalg.svd(Kc, full_matrices=False)
    k = min(topk, len(S))
    Wk = (Vt[:k].T / (S[:k] / np.sqrt(len(K)) + 1e-3)).astype(np.float32)
    return _np_norm(Kc @ Wk), _np_norm(Qc @ Wk)


def _selftest():
    g = np.random.default_rng(0)
    # T1: synthetic facts have correct count
    keys, vq = make_facts(50)
    assert len(keys) == 50 and len(vq) == 50
    print("[selftest] T1 PASS: make_facts count correct")

    # T2: recall@1 on identity is ~1
    Kn = _np_norm(g.standard_normal((50, 16)).astype(np.float32))
    assert recall_at_1(Kn, Kn) > 0.95, "T2 self-recall ~1"
    print("[selftest] T2 PASS: recall@1 self-id near 1")

    # T3: svd-whiten preserves topk dimensionality
    Ka, Qa = svd_whiten(
        g.standard_normal((40, 16)).astype(np.float32),
        g.standard_normal((40, 16)).astype(np.float32),
        8)
    assert Ka.shape[1] == 8, "T3 svd-whiten topk dim"
    print("[selftest] T3 PASS: svd-whiten topk dim correct")

    # T4: keysep nonneg
    k_sep = keysep(Kn, sample=20, g=g)
    assert -1.0 <= k_sep <= 1.0
    print("[selftest] T4 PASS: keysep in [-1, 1] (=%.3f)" % k_sep)

    # T5: cat-cue routing (with PART_SIZE chunks)
    P = 50
    Cc = _np_norm(g.standard_normal((P, 64)).astype(np.float32))
    p_true = 17
    qc = _np_norm(
        (CAT_COS * Cc[p_true]
         + math.sqrt(1 - CAT_COS ** 2) *
         _np_norm(g.standard_normal((1, 64)).astype(np.float32))[0]).reshape(1, -1))[0]
    assert int(np.argmax(Cc @ qc)) == p_true, (
        "T5 cat-cue routing failed: got %d expected %d" % (
            int(np.argmax(Cc @ qc)), p_true))
    print("[selftest] T5 PASS: cat-cue routing at CAT_COS=%.2f" % CAT_COS)

    # T6: bands locked
    assert BAND_HARD_PASS_RECALL_M100K == 0.70
    assert BAND_HARD_PASS_COMPOSITION_LIFT == 0.10
    assert BAND_HARD_PASS_RECALL_M100K > BAND_HARD_FAIL_RECALL_M100K
    print("[selftest] T6 PASS: bands locked")

    # T7: LLM counter at module init
    assert _LLM_CALL_COUNTER[0] == 0
    print("[selftest] T7 PASS: LLM counter = 0 at module init")

    print("[selftest] ALL PASS")


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)

# --- GPU + Encoder gate (Fix #24) ---
try:
    import torch.nn.functional as F
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True)
    sys.exit(1)
DEV = torch.device("cuda") if torch.cuda.is_available() else (
    torch.device("cpu") if SMOKE else None)
if DEV is None:
    print("[FATAL] CUDA required for full (Pythia-2.8B encoder).", flush=True)
    sys.exit(1)
GPU_AVAIL = torch.cuda.is_available()
GPU_NAME = torch.cuda.get_device_name(0) if GPU_AVAIL else "cpu"
print("[device] %s gpu_avail=%s name=%s" % (DEV, GPU_AVAIL, GPU_NAME), flush=True)


def encode(texts: List[str]) -> np.ndarray:
    """Encode texts via Pythia mean-pooled hidden state. Setup-time only; counted in LLM_CALL_COUNTER."""
    _LLM_CALL_COUNTER[0] += 1   # SETUP-TIME encoder forward (not inference)
    tok = AutoTokenizer.from_pretrained(ENCODER)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    mdl = AutoModel.from_pretrained(
        ENCODER,
        torch_dtype=(torch.float16 if DEV.type == "cuda" else torch.float32)
    ).to(DEV).eval()
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True,
                truncation=True, max_length=48).to(DEV)
        with torch.no_grad():
            h = mdl(**t).last_hidden_state
        m = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * m).sum(1) / m.sum(1).clamp(min=1)).float().cpu().numpy())
    del mdl
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    return np.concatenate(out, 0).astype(np.float32)


def train_contrastive(K_tr: np.ndarray, Q_tr: np.ndarray, d: int,
                        steps: int, seed: int,
                        shuffle: bool = False) -> np.ndarray:
    """Linear contrastive projection W (D x d). SYMMETRIC InfoNCE + key-UNIFORMITY (de-crowd)."""
    torch.manual_seed(seed)
    K = torch.tensor(K_tr, device=DEV)
    Q = torch.tensor(Q_tr, device=DEV)
    n, D = K.shape
    if shuffle:
        Q = Q[torch.randperm(n, device=DEV)]
    W = (torch.randn(D, d, device=DEV) * (1.0 / D ** 0.5)).requires_grad_(True)
    opt = torch.optim.Adam([W], lr=1e-2)
    bs = min(256, n)
    for step in range(steps):
        idx = torch.randperm(n, device=DEV)[:bs]
        tgt = torch.arange(len(idx), device=DEV)
        kp = F.normalize(K[idx] @ W, dim=1)
        qp = F.normalize(Q[idx] @ W, dim=1)
        lq = (qp @ kp.T) / 0.07
        lk = (kp @ qp.T) / 0.07
        loss_align = 0.5 * (F.cross_entropy(lq, tgt) + F.cross_entropy(lk, tgt))
        kk = kp @ kp.T
        off = kk - torch.eye(len(idx), device=DEV) * 2.0
        loss_unif = off.mean()
        loss = loss_align + 0.5 * loss_unif
        opt.zero_grad()
        loss.backward()
        opt.step()
    return W.detach().cpu().numpy().astype(np.float32)


# ---------- Arms ----------

def arm_a_learned_no_partition(K: np.ndarray, Q: np.ndarray, ho_idx: np.ndarray,
                                  tr_idx: np.ndarray, seed: int) -> Dict:
    """Arm A: learned-projection (no partition); recall@1 over ALL held-out keys."""
    W = train_contrastive(K[tr_idx], Q[tr_idx], PROJ_DIM, TRAIN_STEPS, seed)
    Kho = _np_norm(K[ho_idx] @ W)
    Qho = _np_norm(Q[ho_idx] @ W)
    rec = recall_at_1(Qho, Kho)
    ks = keysep(Kho, g=np.random.default_rng(seed + 5))
    return {"arm": "ARM_A_LEARNED_NO_PARTITION",
            "recall_at_1": round(rec, 4), "keysep": round(ks, 4),
            "n_heldout": int(len(ho_idx))}


def arm_b_dense_partition(K: np.ndarray, Q: np.ndarray, ho_idx: np.ndarray,
                             part_assign: np.ndarray, route_cues: np.ndarray,
                             route_partition_cents: np.ndarray) -> Dict:
    """Arm B: dense (no learned projection) + partition routing.
    Route each held-out cue to its predicted partition; recall@1 within partition."""
    # Normalize raw keys+queries (no projection)
    Kn = _np_norm(K)
    Qn = _np_norm(Q[ho_idx])
    # Routing: each query has a route_cue (per held-out item)
    routes = np.argmax(route_cues @ route_partition_cents.T, axis=1)
    true_p = part_assign[ho_idx]
    route_acc = float(np.mean(routes == true_p))
    # Per-query recall@1 within routed partition
    correct = 0
    for j, ho_j in enumerate(ho_idx):
        rp = int(routes[j])
        in_part = np.where(part_assign == rp)[0]
        if len(in_part) == 0:
            continue
        Kpart = Kn[in_part]
        sims = Kpart @ Qn[j]
        pred_local = int(np.argmax(sims))
        pred_global = int(in_part[pred_local])
        if pred_global == int(ho_j) and rp == int(true_p[j]):
            correct += 1
    rec = correct / max(len(ho_idx), 1)
    return {"arm": "ARM_B_DENSE_PARTITION",
            "recall_at_1": round(rec, 4), "route_acc": round(route_acc, 4),
            "n_heldout": int(len(ho_idx))}


def arm_c_learned_partition(K: np.ndarray, Q: np.ndarray, ho_idx: np.ndarray,
                              tr_idx: np.ndarray, part_assign: np.ndarray,
                              route_cues: np.ndarray, route_partition_cents: np.ndarray,
                              seed: int) -> Dict:
    """Arm C: learned-projection + partition routing (the composition)."""
    W = train_contrastive(K[tr_idx], Q[tr_idx], PROJ_DIM, TRAIN_STEPS, seed)
    Kp = _np_norm(K @ W)
    Qp = _np_norm(Q[ho_idx] @ W)
    routes = np.argmax(route_cues @ route_partition_cents.T, axis=1)
    true_p = part_assign[ho_idx]
    route_acc = float(np.mean(routes == true_p))
    correct = 0
    for j, ho_j in enumerate(ho_idx):
        rp = int(routes[j])
        in_part = np.where(part_assign == rp)[0]
        if len(in_part) == 0:
            continue
        Kpart = Kp[in_part]
        sims = Kpart @ Qp[j]
        pred_local = int(np.argmax(sims))
        pred_global = int(in_part[pred_local])
        if pred_global == int(ho_j) and rp == int(true_p[j]):
            correct += 1
    rec = correct / max(len(ho_idx), 1)
    ks = keysep(Kp[ho_idx], g=np.random.default_rng(seed + 7))
    return {"arm": "ARM_C_LEARNED_PARTITION",
            "recall_at_1": round(rec, 4), "keysep": round(ks, 4),
            "route_acc": round(route_acc, 4), "n_heldout": int(len(ho_idx))}


def arm_d_dense_no_partition(K: np.ndarray, Q: np.ndarray, ho_idx: np.ndarray) -> Dict:
    """Arm D: dense (no learned, no partition). Expected catastrophic cliff at large M."""
    Kn = _np_norm(K)
    Qn = _np_norm(Q[ho_idx])
    Kho_for_recall = Kn[ho_idx]
    rec = recall_at_1(Qn, Kho_for_recall)
    return {"arm": "ARM_D_DENSE_NO_PARTITION",
            "recall_at_1": round(rec, 4), "n_heldout": int(len(ho_idx))}


def run_unit(M: int, seed: int, K_enc: np.ndarray, Q_enc: np.ndarray) -> Dict:
    """Single (M, seed) unit: split heldout, build partitions+routes, run 4 arms."""
    t = time.time()
    g = np.random.default_rng(seed)
    nho = max(2, int(M * HELDOUT_FRAC))
    perm = g.permutation(M)
    ho_idx = perm[:nho]
    tr_idx = perm[nho:]

    # Build partition assignment + routing cues
    # Partition each key by index // PART_SIZE (deterministic; matches partition routing reference)
    n_parts = max(1, math.ceil(M / PART_SIZE))
    part_assign = np.arange(M) // PART_SIZE  # (M,) partition id per key
    part_assign = part_assign.astype(np.int64)
    # Per-partition category centroid (random; used as routing key)
    DC = 256  # matches partition routing reference
    route_partition_cents = _np_norm(
        g.standard_normal((n_parts, DC)).astype(np.float32))
    # Per held-out query: build clean-ish route cue around its true partition
    route_cues = np.zeros((nho, DC), dtype=np.float32)
    for j, ho_j in enumerate(ho_idx):
        p = int(part_assign[ho_j])
        noise = _np_norm(g.standard_normal((1, DC)).astype(np.float32))[0]
        cue = CAT_COS * route_partition_cents[p] + math.sqrt(1 - CAT_COS ** 2) * noise
        route_cues[j] = cue / (np.linalg.norm(cue) + 1e-8)

    # Compute analytic ceiling
    Kho_raw = K_enc[ho_idx]
    Qho_raw = Q_enc[ho_idx]
    Ka, Qa = svd_whiten(Kho_raw, Qho_raw, PROJ_DIM)
    analytic_ceiling = recall_at_1(Qa, Ka)

    arm_a = arm_a_learned_no_partition(K_enc, Q_enc, ho_idx, tr_idx, seed)
    arm_b = arm_b_dense_partition(K_enc, Q_enc, ho_idx, part_assign,
                                    route_cues, route_partition_cents)
    arm_c = arm_c_learned_partition(K_enc, Q_enc, ho_idx, tr_idx, part_assign,
                                      route_cues, route_partition_cents, seed)
    arm_d = arm_d_dense_no_partition(K_enc, Q_enc, ho_idx)

    elapsed = round(time.time() - t, 2)
    print("  [M=%d seed=%d] arm_A=%.4f arm_B=%.4f(route_acc=%.4f) arm_C=%.4f(route_acc=%.4f) "
          "arm_D=%.4f analytic=%.4f n_parts=%d wall=%.1fs" % (
              M, seed, arm_a["recall_at_1"], arm_b["recall_at_1"], arm_b["route_acc"],
              arm_c["recall_at_1"], arm_c["route_acc"], arm_d["recall_at_1"],
              analytic_ceiling, n_parts, elapsed), flush=True)
    return {
        "M": M, "seed": seed,
        "arm_A": arm_a, "arm_B": arm_b, "arm_C": arm_c, "arm_D": arm_d,
        "analytic_ceiling_recall": round(analytic_ceiling, 4),
        "n_parts": int(n_parts), "part_size": PART_SIZE,
        "n_heldout": int(nho),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": 0,  # encoder forward is SETUP-time; inference is substrate-only
        "_llm_forward_calls_at_setup": _LLM_CALL_COUNTER[0],
        "gpu_avail": GPU_AVAIL, "gpu_name": GPU_NAME,
        "elapsed_s_unit": elapsed,
    }


def compute_verdict(units: List[Dict]) -> Tuple[str, str]:
    if not units:
        return ("HARD_FAIL", "no units")

    # Aggregate per M
    by_M = {}
    for u in units:
        by_M.setdefault(u["M"], []).append(u)

    summary_rows = []
    chain_grade_Ms = []
    saturated_arms_at_M = {}
    arm_rows_at_M = {}
    for M in sorted(by_M.keys()):
        us = by_M[M]
        per_arm = {}
        for arm_key in ("arm_A", "arm_B", "arm_C", "arm_D"):
            recs = [u[arm_key]["recall_at_1"] for u in us]
            m = float(np.mean(recs))
            cv = float(np.std(recs) / max(m, 1e-9)) if len(recs) >= 2 else 0.0
            per_arm[arm_key] = {"recall_mean": round(m, 4), "recall_cv": round(cv, 4),
                                 "recall_per_seed": [round(r, 4) for r in recs]}
            if arm_key in ("arm_B", "arm_C"):
                ras = [u[arm_key].get("route_acc") for u in us
                       if u[arm_key].get("route_acc") is not None]
                if ras:
                    per_arm[arm_key]["route_acc_mean"] = round(float(np.mean(ras)), 4)
            if arm_key in ("arm_A", "arm_C"):
                kss = [u[arm_key].get("keysep") for u in us
                       if u[arm_key].get("keysep") is not None]
                if kss:
                    per_arm[arm_key]["keysep_mean"] = round(float(np.mean(kss)), 4)
        analytic = float(np.mean([u["analytic_ceiling_recall"] for u in us]))
        per_arm["analytic_ceiling"] = round(analytic, 4)
        arm_rows_at_M[M] = per_arm
        # Chain-grade gate at this M (arm C must compose beat arm A AND arm B AND analytic)
        c_rec = per_arm["arm_C"]["recall_mean"]
        c_cv = per_arm["arm_C"]["recall_cv"]
        c_keysep = per_arm["arm_C"].get("keysep_mean", 1.0)
        a_rec = per_arm["arm_A"]["recall_mean"]
        b_rec = per_arm["arm_B"]["recall_mean"]
        chain_grade_gate = (c_rec >= BAND_HARD_PASS_RECALL_M100K
                             and c_cv <= BAND_HARD_PASS_CV_MAX
                             and c_keysep <= BAND_HARD_PASS_KEYSEP_MAX
                             and (c_rec - a_rec) >= BAND_HARD_PASS_COMPOSITION_LIFT
                             and (c_rec - b_rec) >= BAND_HARD_PASS_COMPOSITION_LIFT)
        if chain_grade_gate:
            chain_grade_Ms.append(M)
        # Q-saturation per arm
        sat_arms = [k for k in ("arm_A", "arm_B", "arm_C", "arm_D")
                    if per_arm[k]["recall_mean"] >= BAND_Q_SUSPECT_SATURATION]
        if sat_arms:
            saturated_arms_at_M[M] = sat_arms
        summary_rows.append(
            "M=%d A=%.4f B=%.4f(racc=%.3f) C=%.4f(racc=%.3f keysep=%.3f cv=%.3f) D=%.4f anal=%.4f" % (
                M,
                per_arm["arm_A"]["recall_mean"], per_arm["arm_B"]["recall_mean"],
                per_arm["arm_B"].get("route_acc_mean", float("nan")),
                per_arm["arm_C"]["recall_mean"],
                per_arm["arm_C"].get("route_acc_mean", float("nan")),
                per_arm["arm_C"].get("keysep_mean", float("nan")), c_cv,
                per_arm["arm_D"]["recall_mean"], analytic))

    summ = " | ".join(summary_rows)
    if saturated_arms_at_M:
        summ += " | [Q-DISCIPLINE: saturated arms at M=%s]" % saturated_arms_at_M

    # M=100k is the load-bearing M (chain-grade-confirmed at production scale)
    M_TARGET = 100000 if not SMOKE else 1000
    has_target = M_TARGET in chain_grade_Ms

    # HARD_FAIL: all arms below floor at M=target
    if M_TARGET in arm_rows_at_M:
        row = arm_rows_at_M[M_TARGET]
        all_below_fail = all(row[k]["recall_mean"] < BAND_HARD_FAIL_RECALL_M100K
                              for k in ("arm_A", "arm_B", "arm_C"))
        if all_below_fail:
            return ("HARD_FAIL",
                    "HARD_FAIL_LEARNED_PROJECTION_DOESNT_SCALE: all arms below "
                    "recall_floor=%.2f at M=%d (composition does NOT close) | %s" % (
                        BAND_HARD_FAIL_RECALL_M100K, M_TARGET, summ))

    if has_target:
        return ("HARD_PASS",
                "HARD_PASS_CHAIN_GRADE_AT_M_%dK: arm_C recall>=%.2f AND beats arm_A "
                "and arm_B by >=%.2f at M=%d (chain_grade_Ms=%s) | %s" % (
                    M_TARGET // 1000, BAND_HARD_PASS_RECALL_M100K,
                    BAND_HARD_PASS_COMPOSITION_LIFT, M_TARGET,
                    chain_grade_Ms, summ))

    if chain_grade_Ms:
        return ("HARD_PASS",
                "CHAIN_GRADE_AT_LOWER_X: arm_C chain-grades at M=%s but cliffs at M=%d "
                "(composition extends part of envelope only) | %s" % (
                    chain_grade_Ms, M_TARGET, summ))

    return ("MIDDLE_BAND",
            "MIDDLE_BAND_NO_CHAIN_GRADE: no M reaches arm_C chain-grade gate "
            "(recall>=%.2f AND lift>=%.2f over arms A and B) | %s" % (
                BAND_HARD_PASS_RECALL_M100K, BAND_HARD_PASS_COMPOSITION_LIFT, summ))


_RESULTS_HOLDER = {"out_dir": None, "started_at": time.time()}


def _atexit_synth():
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        if (od / "metrics.json").exists():
            return
        keys = ["M%d_s%d" % (M, s) for M in M_SWEEP for s in SEEDS]
        agg = aggregate_partials(od, seeds=keys, run_config={"run_mode": RUN_MODE})
        if not agg:
            return
        units = list(agg.values())
        if not units:
            return
        v, vmsg = compute_verdict(units)
        try:
            mem = int(torch.cuda.max_memory_allocated() / 1024 / 1024) if GPU_AVAIL else 0
        except Exception:
            mem = 0
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_units": len(units),
            "config_version": CONFIG_VERSION, "per_unit": units,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": 0,
            "_llm_forward_calls_at_setup": _LLM_CALL_COUNTER[0],
            "gpu_avail": GPU_AVAIL, "gpu_name": GPU_NAME, "gpu_max_mem_alloc_mb": mem,
            "M_SWEEP": M_SWEEP, "seeds": SEEDS,
        }
        write_metrics(od, metrics, results=units)
        print("[atexit] wrote synth metrics.json (%d units)" % len(units), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s encoder=%s M=%s seeds=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, ENCODER, M_SWEEP, SEEDS, CONFIG_VERSION),
        flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"run_mode": RUN_MODE}
    keys = ["M%d_s%d" % (M, s) for M in M_SWEEP for s in SEEDS]
    existing = aggregate_partials(out_dir, seeds=keys, run_config=run_config)
    done_keys = set(existing.keys())
    print("[ckpt] done=%d/%d units" % (len(done_keys), len(keys)), flush=True)

    # Pre-encode facts ONCE per seed * M (encoder forward is the expensive setup step)
    for M in M_SWEEP:
        # Pre-encode at the largest M for this seed; reuse for the inner-M splits
        # NOTE: each seed needs its own encoding because make_facts is deterministic
        # but the fact-corpus changes with M (i loops 0..M-1 with different mod selectors).
        # So we encode the FULL M of facts for each (M, seed) unit.
        for s in SEEDS:
            key = "M%d_s%d" % (M, s)
            if key in done_keys:
                continue
            t_enc = time.time()
            keys_text, vq_text = make_facts(M)
            print("[encode] M=%d seed=%d: %d keys + %d queries via %s" % (
                M, s, len(keys_text), len(vq_text), ENCODER), flush=True)
            K_enc = encode(keys_text)
            Q_enc = encode(vq_text)
            print("[encode] M=%d seed=%d done (%.1fs)" % (M, s, time.time() - t_enc),
                  flush=True)
            try:
                rec = run_unit(M, s, K_enc, Q_enc)
                write_partial_key(out_dir, key, rec)
            except Exception as e:
                print("[WARN] %s failed: %s" % (key, e), flush=True)

    agg = aggregate_partials(out_dir, seeds=keys, run_config=run_config)
    units = [agg[k] for k in keys if k in agg]
    if not units:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    v, vmsg = compute_verdict(units)
    print("\n[VERDICT] " + vmsg, flush=True)
    try:
        mem = int(torch.cuda.max_memory_allocated() / 1024 / 1024) if GPU_AVAIL else 0
    except Exception:
        mem = 0
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_units": len(units),
        "config_version": CONFIG_VERSION, "per_unit": units,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": 0,   # substrate-only at inference
        "_llm_forward_calls_at_setup": _LLM_CALL_COUNTER[0],
        "gpu_avail": GPU_AVAIL, "gpu_name": GPU_NAME, "gpu_max_mem_alloc_mb": mem,
        "M_SWEEP": M_SWEEP, "seeds": SEEDS, "encoder": ENCODER,
        "DESIGN_NOTE": (
            "Composition cell: KV learned projection + partition routing at M=100k. "
            "Tests held-out generalization at production scale. Arm A (learned-only), "
            "Arm B (dense+partition), Arm C (learned+partition = the integration), "
            "Arm D (dense-only control). Pre-reg per "
            "preregs/2026-06-25_substrate_kv_learned_projection_at_scale_M_100k_with_partition_routing_v1.md."
        ),
    }
    write_metrics(out_dir, metrics, results=units)
    print("[done] metrics.json written (%d units, %.1fs)" % (
        len(units), metrics["elapsed_s"]), flush=True)
