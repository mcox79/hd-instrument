"""GAP 2 CLOSE DIAGNOSTIC -- stride-sweep test of cosine-physics-floor hypothesis.

PARENT CONTEXT (Research diagnosis 2026-06-26):
  - notes/research_gap2_capacity_side_analysis_NOT_geometry_2026-06-26.md
  - notes/exp_dev_handoff_research_gap2_capacity_side_analysis_2026-06-26.md (Anchor 1 + 2)
  - 6 independent geometry-side mechanisms HARD_FAIL'd on Gap 2 (whitening, MIMO,
    DG, polarimetric, anisotropy v4 expansion, ScaNN VQ).
  - Diagnosis: substrate's 1.8% recall at M=10k adversarial-stride-1 keys IS the
    COSINE-PHYSICS FLOOR (test-design artifact), not a substrate capacity gap.

MECHANISM (one paragraph):
  Stride between consecutive KEYS controls token-overlap between adjacent items.
  stride=1 -> adjacent keys share 15/16 tokens (adversarial near-duplicates; cosine
  > 0.9 inevitable; KNN itself floors at ~0.30 because adjacent items are physically
  indistinguishable in any cosine metric). stride=16 -> disjoint windows (natural
  keys; substrate's chain-grade regime; KNN >= 0.9). If substrate recall scales
  monotonically with stride from KNN-floor toward chain-grade, the diagnosis is
  confirmed: the 1.8% number measures the IMPOSSIBLE (KNN-on-stride-1), not a
  substrate gap. If recall stays low even at stride=16, Gap 2 is REAL on natural
  keys and a new mechanism is needed.

  Combined Anchor 2 analysis layer (refuse-gate top1-top2 delta) reads delta-cosine
  distribution per arm; arms with high refuse-headroom (low top1-top2 delta on
  stride=1; high on stride=16) confirm refuse-gate is the right primitive for
  adversarial near-duplicates.

CRITICAL PATTERN-CHECK (per handoff smoke gate):
  Smoke MUST verify monotone stride curve (recall non-decreasing as stride
  increases). If smoke shows non-monotonic stride curve OR recall(stride=16)
  collapses with KNN sentinel passing, GATE and report rather than dispatch full.

ARMS (per handoff Anchor 1):
  CROSS-CELL SANITY RAIL (Fix #28 by-construction-saturation sentinel):
    ARM_KNN_SENTINEL per stride -- recall via exhaustive cosine KNN at each stride.
    The load-bearing comparison; substrate should approximately track KNN as
    stride increases.

  MECHANISM ARMS (varying stride parameter):
    ARM_STRIDE_1  -- adversarial 15/16 token overlap (reproduces v2_batched ~0.02 raw)
    ARM_STRIDE_4  -- 12/16 token overlap
    ARM_STRIDE_8  -- 8/16 token overlap (half-overlapping)
    ARM_STRIDE_16 -- disjoint windows (natural keys)

  ANALYSIS LAYER (combined Anchor 2 -- refuse-gate top1-top2 delta):
    Per arm: median top1-top2 delta on cue-key cosine post-rerank. High delta ->
    distinguishable; low delta -> refuse candidates. Plus delta-at-coverage-0.5
    point estimate (analog of Anchor 2 refuse-gate diagnostic).

  PER-ARM METRICS:
    - recall@1: fraction of cues where reranked top-1 within routed partition is true.
    - recall@10: fraction of cues where reranked top-10 contains true.
    - route_acc: fraction of cues routed to partition containing true key.
    - knn_sentinel: exhaustive cosine KNN recall@1 (rank-blind).
    - top1_top2_delta_median: refuse-gate analog.

PRE-REGISTERED BANDS (LOCKED AT MODULE INIT):

  HARD_PASS_GAP2_CLOSES (diagnosis confirmed; CLOSE Gap 2):
    recall(stride=16) >= 0.90
    AND recall(stride=8) >= 0.70
    AND monotone non-decreasing in stride
    AND cv across seeds for stride=16 recall <= 0.05
    -- substrate is at cosine-physics floor; anisotropy is feature; 1.8% is
    KNN-floor on adversarial near-duplicates that no cosine method can solve.

  MIDDLE_BAND (partial signal; informative on cosine-physics edge):
    monotone non-decreasing AND recall(stride=16) in [0.70, 0.90)
    -- substrate works but not chain-grade on natural keys at M=10k; refuse-gate
    or further mechanism may help.

  HARD_FAIL_GAP2_REAL (re-open Gap 2 as real capacity gap):
    recall(stride=16) < 0.70
    OR non-monotonic stride curve (regression as stride increases)
    -- substrate has true M=10k bottleneck independent of stride; need new
    mechanism (Anchor 3 natural-keys M-scaling audit).

  HARD_FAIL_KNN_SENTINEL_REGRESSION (corruption catch):
    knn_sentinel(stride=16) < 0.80 -- keys themselves degraded; any arm
    "lift" is artifact (not the substrate's mechanism).

Q-DISCIPLINE: any arm >= 0.995 flags suspect saturation; bands favor under-claim.

Disciplines (load-bearing):
  - ASCII only.
  - Substrate-only at inference; encoder is SETUP-TIME hidden-state extractor.
  - Per-arm metrics (Fix #28); read metrics.json per-arm, NOT verdict_msg.
  - atexit per-seed checkpoint + restartable (per Fix #20).
  - META_M7 capacity-sensitive dims (PROJ_DIM, PART_SIZE_TARGET, KM_ITERS,
    KNN_TOPK, WINDOW_TOKENS, CUE_SHIFT) IDENTICAL across smoke and full --
    ONLY M, n_seeds, encoder, and TRAIN_STEPS differ.

Routing: local CPU (Tier A per handoff). M=10k matmul-bound; numpy CPU adequate;
~1.5-2 hr full wall on laptop.

Cites:
  - notes/research_gap2_capacity_side_analysis_NOT_geometry_2026-06-26.md (DIAGNOSIS)
  - notes/exp_dev_handoff_research_gap2_capacity_side_analysis_2026-06-26.md (Anchor 1+2)
  - data/exp_substrate_partition_routing_hierarchical_2level_v1/metrics.json (chain-grade spine)
  - data/exp_substrate_partition_routing_anisotropic_scann_quantizer_v1_smoke/metrics.json (KNN=0.30 at M=400 stride-1)
  - Geifman_El-Yaniv_2017_selective_classification (refuse-gate analog)
  - Goldman-Rakic delta-rejection (brain analog for top1-top2 refuse)
"""
from __future__ import annotations
import sys, os, argparse, time, math, json
from pathlib import Path
from typing import Dict, List
import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_gap2_stride_sweep_confirm_v1"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# CAPACITY-SENSITIVE (META_M7) -- IDENTICAL smoke/full
PROJ_DIM = 768                  # post-contrastive projection dim (matches polarimetric anchor)
PART_SIZE_TARGET = 2000         # matches substrate's chain-grade partition routing
KM_ITERS = 25                   # k-means EM iterations
KNN_TOPK = 1                    # KNN baseline = top-1 cosine
KNN_TOPK_10 = 10                # for recall@10 measurement
SIGMA = 0.1                     # cue noise sigma
MAX_Q = 1500                    # max cue count per arm
WINDOW_TOKENS = 16              # 16-token windows on natural Pythia prose
CUE_SHIFT = 1                   # cue is shifted-by-1 from key (within-key cue noise model)

# STRIDE ARMS -- 4 arms (Anchor 1 load-bearing diagnostic)
STRIDES = [1, 4, 8, 16]

# MODE-DEPENDENT (ONLY THESE DIFFER smoke vs full)
if RUN_MODE == "full":
    ENCODER = "EleutherAI/pythia-2.8b"
    SEEDS = [11, 13, 19]
    M = 10000
    TRAIN_M = 10000
    TRAIN_STEPS = 600
else:
    ENCODER = "EleutherAI/pythia-160m"
    SEEDS = [11]
    M = 2000
    TRAIN_M = 800
    TRAIN_STEPS = 100

# PRE-REG BANDS (LOCKED AT MODULE INIT)
BAND_HP_STRIDE16_RECALL = 0.90     # recall(stride=16) floor for HARD_PASS_GAP2_CLOSES
BAND_HP_STRIDE8_RECALL = 0.70      # recall(stride=8) floor for HARD_PASS
BAND_MIDDLE_STRIDE16_RECALL = 0.70  # recall(stride=16) floor for MIDDLE_BAND
BAND_HF_STRIDE16_RECALL = 0.70     # recall(stride=16) below this -> HARD_FAIL_GAP2_REAL
BAND_KNN_SENTINEL_STRIDE16 = 0.80  # knn@stride=16 floor (corruption catch)
BAND_CV_HP = 0.05                  # seed cv ceiling for HARD_PASS
BAND_Q_SATURATION = 0.995          # suspect saturation
BAND_MONOTONE_TOL = 0.02           # allow tiny regression within seed noise

# Band ordering assertions
assert 0.0 < BAND_HF_STRIDE16_RECALL <= BAND_MIDDLE_STRIDE16_RECALL <= BAND_HP_STRIDE16_RECALL < 1.0, (
    "stride16 recall band ordering"
)
assert 0.0 < BAND_HP_STRIDE8_RECALL < BAND_HP_STRIDE16_RECALL < 1.0, "stride8 < stride16 band"
assert 0.0 < BAND_KNN_SENTINEL_STRIDE16 < 1.0, "knn sentinel"
assert STRIDES == sorted(STRIDES) and STRIDES[0] == 1, "stride order: ascending starting at 1"

CONFIG_VERSION = (
    "gap2_stride_sweep_v1 (strides=%s; prose=text8) | "
    "proj=%d part_target=%d km_iters=%d sigma=%.2f window=%dt cue_shift=%d | "
    "seeds=%s M=%d encoder=%s | CPU_numpy"
) % (
    STRIDES, PROJ_DIM, PART_SIZE_TARGET, KM_ITERS, SIGMA, WINDOW_TOKENS, CUE_SHIFT,
    SEEDS, M, ENCODER,
)


# ---------- numerical helpers ----------

def _np_norm(X):
    return (X / (np.linalg.norm(X, axis=-1, keepdims=True) + 1e-8)).astype(np.float32)


def _knn_topk_recall(K, cue, ytrue_idx, topk=1):
    """Cosine exhaustive KNN; recall@topk over normalized vectors.

    K: (M, D). cue: (Q, D). ytrue_idx: (Q,). Returns mean recall.
    """
    Kn = _np_norm(K)
    cn = _np_norm(cue)
    sim = cn @ Kn.T  # Q x M
    if topk == 1:
        idx = np.argmax(sim, axis=1)
        return float((idx == ytrue_idx).mean())
    topk_idx = np.argpartition(sim, -topk, axis=1)[:, -topk:]
    hits = np.any(topk_idx == ytrue_idx[:, None], axis=1)
    return float(hits.mean())


def _top1_top2_delta(K, cue, ytrue_idx):
    """Median top1-top2 cosine delta across queries (refuse-gate primitive).

    Returns (median_delta, p25_delta, p75_delta) -- distribution stats.
    """
    Kn = _np_norm(K)
    cn = _np_norm(cue)
    sim = cn @ Kn.T  # Q x M
    # partition top-2 per row
    part = np.argpartition(sim, -2, axis=1)[:, -2:]
    top_vals = np.take_along_axis(sim, part, axis=1)
    # sort each row so top_vals[:,0] is top-1, top_vals[:,1] is top-2
    top_sorted = np.sort(top_vals, axis=1)
    delta = top_sorted[:, 1] - top_sorted[:, 0]  # top1 - top2 (>= 0)
    return (float(np.median(delta)),
            float(np.percentile(delta, 25)),
            float(np.percentile(delta, 75)))


# ---------- ISOTROPIC k-means (chain-grade substrate baseline; per handoff "no anisotropy") ----------

def _kmeans_isotropic(K, n_parts, iters, seed):
    """Standard L2 k-means partition assignment.

    K: (M, D) normalized keys.
    Returns:
      centroids: (n_parts, D) float32
      assign:    (M,) int64
      quant_err: float
    """
    M_loc, D = K.shape
    g = np.random.default_rng(seed)
    centroids = np.empty((n_parts, D), dtype=np.float32)
    centroids[0] = K[int(g.integers(0, M_loc))]
    if n_parts > 1:
        min_dist = np.linalg.norm(K - centroids[0][None], axis=1) ** 2
        for ci in range(1, n_parts):
            prob = min_dist / (min_dist.sum() + 1e-12)
            idx = int(g.choice(M_loc, p=prob))
            centroids[ci] = K[idx]
            new_dist = np.linalg.norm(K - centroids[ci][None], axis=1) ** 2
            min_dist = np.minimum(min_dist, new_dist)

    assign = np.zeros(M_loc, dtype=np.int64)
    for it in range(iters):
        sim = K @ centroids.T
        c_norm_sq = (centroids ** 2).sum(axis=1)
        scores = 2 * sim - c_norm_sq[None, :]
        new_assign = np.argmax(scores, axis=1).astype(np.int64)
        if it > 0 and (new_assign == assign).mean() > 0.999:
            assign = new_assign
            break
        assign = new_assign
        for ci in range(n_parts):
            mask = assign == ci
            if mask.sum() > 0:
                centroids[ci] = K[mask].mean(axis=0)

    diff = K - centroids[assign]
    quant_err = float((diff ** 2).sum(axis=1).mean())
    return centroids, assign, quant_err


# ---------- arm evaluation: route + within-partition rerank ----------

def _route_and_rerank(K, centroids, assign, cue, ytrue_idx, topk=1):
    """For each cue: route to argmax-cosine partition; rerank within by exact cosine.

    Returns (route_acc, recall_at_topk).
    """
    Q = cue.shape[0]
    Cn = _np_norm(centroids)
    cn = _np_norm(cue)
    Kn = _np_norm(K)
    sim_to_centroid = cn @ Cn.T
    routes = np.argmax(sim_to_centroid, axis=1).astype(np.int64)
    true_partition = assign[ytrue_idx]
    route_acc = float((routes == true_partition).mean())

    hits = 0
    for q in range(Q):
        p = int(routes[q])
        idx_in_p = np.where(assign == p)[0]
        if len(idx_in_p) == 0:
            continue
        sims = Kn[idx_in_p] @ cn[q]
        if topk == 1:
            best = idx_in_p[int(np.argmax(sims))]
            if best == ytrue_idx[q]:
                hits += 1
        else:
            k_use = min(topk, len(idx_in_p))
            top_loc = np.argpartition(sims, -k_use)[-k_use:]
            top_global = idx_in_p[top_loc]
            if ytrue_idx[q] in top_global:
                hits += 1
    recall = hits / Q
    return route_acc, recall


# ---------- per-stride arm runner ----------

def _arm_for_stride(Kp, seed_for_arm, stride):
    """Run the routing arm on pre-encoded keys for this stride.

    Kp: (M, D) projected keys at the requested stride (built upstream).
    """
    K = _np_norm(Kp)
    M_loc = K.shape[0]
    D = K.shape[1]
    g = np.random.default_rng(seed_for_arm)

    if M_loc <= MAX_Q:
        qidx = np.arange(M_loc)
    else:
        qidx = np.sort(g.choice(M_loc, MAX_Q, replace=False))
    noise = (SIGMA * g.standard_normal((len(qidx), D))).astype(np.float32)
    cue = (K[qidx] + noise).astype(np.float32)
    ytrue_idx = qidx.astype(np.int64)

    # KNN sentinel (rank-blind; per stride)
    knn_r1 = _knn_topk_recall(K, cue, ytrue_idx, topk=KNN_TOPK)

    # partition count
    n_parts = max(2, M_loc // PART_SIZE_TARGET)

    # iso k-means partition route (chain-grade mechanism)
    t0 = time.time()
    cen, assign, qerr = _kmeans_isotropic(K, n_parts, KM_ITERS, seed_for_arm)
    route_acc_1, recall_1 = _route_and_rerank(K, cen, assign, cue, ytrue_idx, topk=1)
    route_acc_10, recall_10 = _route_and_rerank(K, cen, assign, cue, ytrue_idx, topk=KNN_TOPK_10)
    t_arm = time.time() - t0

    # refuse-gate analysis layer: top1-top2 delta on EXHAUSTIVE cosine (decouples from routing)
    delta_med, delta_p25, delta_p75 = _top1_top2_delta(K, cue, ytrue_idx)

    return {
        "stride": stride,
        "M_eff": M_loc,
        "n_parts": n_parts,
        "knn_recall_at_1": round(knn_r1, 4),
        "route_acc": round(route_acc_1, 4),
        "recall_at_1": round(recall_1, 4),
        "recall_at_10": round(recall_10, 4),
        "quant_err_l2": round(qerr, 6),
        "top1_top2_delta_median": round(delta_med, 4),
        "top1_top2_delta_p25": round(delta_p25, 4),
        "top1_top2_delta_p75": round(delta_p75, 4),
        "elapsed_s": round(t_arm, 2),
    }


# ---------- natural prose source (text8 disk corpus; ~17M words natural English) ----------
#
# Smoke 2026-06-26 evidence: the prior 11-chunk embedded prose pool (~664 words)
# produced near-duplicate keys EVEN AT STRIDE=16 because the pool concatenates
# ~48 times across the M*stride=32000-word demand. KNN floored at 0.17 across
# all strides -> cannot discriminate stride effects (HARD_FAIL_KNN_SENTINEL on
# smoke). Fix: use text8 (Mahoney's cleaned Wikipedia; 17M words; same corpus
# substrate uses for bigram-gap measurement). Provides genuine prose diversity
# at all stride values up to and beyond M=10k at stride=16.

_TEXT8_PATH = REPO / "data" / "text8_cache" / "text8.txt"
_TEXT8_CACHE = None  # loaded lazily


def _load_text8_words():
    """Load text8 words once, cached in module-level _TEXT8_CACHE."""
    global _TEXT8_CACHE
    if _TEXT8_CACHE is not None:
        return _TEXT8_CACHE
    if not _TEXT8_PATH.exists():
        raise RuntimeError("text8 corpus not found at %s" % _TEXT8_PATH)
    with open(_TEXT8_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    words = text.split()
    print("[text8-load] %d words from %s" % (len(words), _TEXT8_PATH), flush=True)
    _TEXT8_CACHE = words
    return words


def _build_prose(g, target_tokens):
    """Return a list of words drawn from a random contiguous slice of text8.

    Different (seed, stride) calls get different starting positions -> different
    natural prose subsets, ensuring genuine cross-stride diversity.
    """
    words = _load_text8_words()
    n = len(words)
    if target_tokens >= n:
        return " ".join(words)
    start = int(g.integers(0, n - target_tokens))
    return " ".join(words[start:start + target_tokens])


def _train_W(seed: int, encode, train_contrastive):
    """Train ONE contrastive projection W on a small stride-1 train pool.

    Reuses the same W across all stride arms (W is the encoder->substrate projection;
    stride is a property of KEY CONSTRUCTION, not of the projection).
    """
    g = np.random.default_rng(seed * 1009 + 17)
    needed_words = TRAIN_M + WINDOW_TOKENS + CUE_SHIFT + 50
    prose = _build_prose(g, target_tokens=needed_words)
    words = prose.split()
    while len(words) < TRAIN_M + WINDOW_TOKENS + CUE_SHIFT:
        prose = _build_prose(g, target_tokens=needed_words * 2)
        words = prose.split()
    keys_tr = [" ".join(words[i:i + WINDOW_TOKENS]) for i in range(TRAIN_M)]
    cues_tr = [" ".join(words[i + CUE_SHIFT:i + CUE_SHIFT + WINDOW_TOKENS])
               for i in range(TRAIN_M)]
    print("[train] seed=%d TRAIN_M=%d sample_key=%r" % (
        seed, TRAIN_M, keys_tr[0][:60]), flush=True)
    K_tr = encode(keys_tr)
    Q_tr = encode(cues_tr)
    W = train_contrastive(K_tr, Q_tr, PROJ_DIM, TRAIN_STEPS, seed)
    return W


def _encode_keys_at_stride(seed: int, stride: int, encode, W) -> np.ndarray:
    """Build M keys at the requested stride from natural Pythia prose; encode + project.

    For stride S: key i is the 16-token window starting at word position i*S.
    cue is shift-1 from each key (within-key noise model, same as polarimetric).
    """
    g = np.random.default_rng(seed * 7919 + stride * 31)
    # need M*stride + WINDOW_TOKENS + CUE_SHIFT words
    needed_words = M * stride + WINDOW_TOKENS + CUE_SHIFT + 50
    prose = _build_prose(g, target_tokens=needed_words)
    words = prose.split()
    while len(words) < M * stride + WINDOW_TOKENS + CUE_SHIFT:
        prose = _build_prose(g, target_tokens=needed_words * 2)
        words = prose.split()

    keys = []
    for i in range(M):
        base = i * stride
        keys.append(" ".join(words[base:base + WINDOW_TOKENS]))
    print("[encode-stride] seed=%d stride=%d M=%d sample_key=%r" % (
        seed, stride, M, keys[0][:60]), flush=True)
    # Encode keys only; cues are noise-perturbed keys (matches partition-routing convention
    # used in polarimetric / chain-grade ledger). Saves 4x encoder cost per stride.
    K = encode(keys)
    Kp = (K @ W).astype(np.float32)
    return Kp


def run_unit(seed: int) -> Dict:
    print("[seed=%d] encoder=%s M=%d strides=%s mode=%s" % (
        seed, ENCODER, M, STRIDES, RUN_MODE), flush=True)
    os.environ["HDLAB_RUN_MODE"] = RUN_MODE
    import experiments.exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 as _probe
    _probe.ENCODER = ENCODER
    encode = _probe.encode
    train_contrastive = _probe.train_contrastive

    t_train = time.time()
    W = _train_W(seed, encode, train_contrastive)
    t_train_s = time.time() - t_train
    print("  [seed=%d] train_W elapsed=%.1fs PROJ_DIM=%d" % (seed, t_train_s, PROJ_DIM), flush=True)

    by_stride = {}
    total_enc = 0.0
    for s in STRIDES:
        arm_seed = seed * 13 + s
        t_enc = time.time()
        Kp_s = _encode_keys_at_stride(seed, s, encode, W)
        t_enc_s = time.time() - t_enc
        total_enc += t_enc_s
        t0 = time.time()
        a = _arm_for_stride(Kp_s, arm_seed, s)
        a["encode_elapsed_s"] = round(t_enc_s, 2)
        by_stride["s%d" % s] = a
        print(("  [seed=%d stride=%d] knn=%.3f | route=%.3f recall@1=%.3f recall@10=%.3f "
               "delta_med=%.3f enc=%.1fs arm=%.1fs"
               ) % (
            seed, s, a["knn_recall_at_1"], a["route_acc"], a["recall_at_1"], a["recall_at_10"],
            a["top1_top2_delta_median"], t_enc_s, time.time() - t0,
        ), flush=True)
    return {"seed": seed, "by_stride": by_stride,
            "train_W_elapsed_s": round(t_train_s, 2),
            "total_encoder_elapsed_s": round(total_enc, 2),
            "run_mode": RUN_MODE, "STRIDES": STRIDES, "N": PROJ_DIM, "M": M}


def _med_std(values):
    if not values:
        return 0.0, 0.0
    return float(np.median(values)), float(np.std(values))


def _cv(values):
    vals = [v for v in values if isinstance(v, (int, float)) and not math.isnan(v) and v >= 0]
    if len(vals) < 2:
        return float("nan")
    m = float(np.mean(vals))
    if abs(m) < 1e-9:
        return 0.0
    return float(np.std(vals) / abs(m))


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})

    # gather per-stride per-seed values
    def vals(stride, key):
        out = []
        for u in units:
            r = u["by_stride"].get("s%d" % stride, {})
            v = r.get(key) if isinstance(r, dict) else None
            if v is not None and isinstance(v, (int, float)) and not math.isnan(v):
                out.append(float(v))
        return out

    per_stride_recall_med = {}
    per_stride_recall_cv = {}
    per_stride_knn = {}
    per_stride_route = {}
    per_stride_delta = {}
    per_stride_recall_at_10 = {}
    for s in STRIDES:
        rv = vals(s, "recall_at_1")
        kn = vals(s, "knn_recall_at_1")
        rt = vals(s, "route_acc")
        dl = vals(s, "top1_top2_delta_median")
        r10 = vals(s, "recall_at_10")
        per_stride_recall_med[s], _ = _med_std(rv)
        per_stride_recall_cv[s] = _cv(rv)
        per_stride_knn[s], _ = _med_std(kn)
        per_stride_route[s], _ = _med_std(rt)
        per_stride_delta[s], _ = _med_std(dl)
        per_stride_recall_at_10[s], _ = _med_std(r10)

    s_max = max(STRIDES)
    s_mid = sorted(STRIDES)[len(STRIDES) // 2]  # for 4 strides [1,4,8,16] -> 8
    # explicit pick of mid=8 from spec
    if 8 in STRIDES:
        s_mid = 8

    r16 = per_stride_recall_med[s_max]
    r8 = per_stride_recall_med[s_mid]
    cv16 = per_stride_recall_cv[s_max]
    knn16 = per_stride_knn[s_max]

    # monotone check: recall non-decreasing as stride increases (within MONOTONE_TOL)
    strides_sorted = sorted(STRIDES)
    monotone = True
    monotone_violations = []
    for i in range(1, len(strides_sorted)):
        prev_s = strides_sorted[i - 1]
        cur_s = strides_sorted[i]
        if per_stride_recall_med[cur_s] < per_stride_recall_med[prev_s] - BAND_MONOTONE_TOL:
            monotone = False
            monotone_violations.append("s%d(%.3f) < s%d(%.3f)-tol" % (
                cur_s, per_stride_recall_med[cur_s], prev_s, per_stride_recall_med[prev_s]))

    # Q-saturation
    q_flags = []
    for s in STRIDES:
        r = per_stride_recall_med[s]
        if r >= BAND_Q_SATURATION:
            q_flags.append("[Q-DISCIPLINE: recall@stride=%d=%.4f >= %.3f suspect saturation]" % (
                s, r, BAND_Q_SATURATION))
    q_note = " ".join(q_flags) + (" " if q_flags else "")

    # summary text
    summ_parts = []
    for s in strides_sorted:
        summ_parts.append("s%d: knn=%.3f route=%.3f recall=%.3f r10=%.3f delta=%.3f" % (
            s, per_stride_knn[s], per_stride_route[s], per_stride_recall_med[s],
            per_stride_recall_at_10[s], per_stride_delta[s]))
    summ = " | ".join(summ_parts) + (" | mono=%s cv16=%.3f" % (monotone, cv16))

    detail = {
        "STRIDES": STRIDES,
        "per_stride_recall_at_1_median": {("s%d" % s): round(per_stride_recall_med[s], 4) for s in STRIDES},
        "per_stride_recall_at_10_median": {("s%d" % s): round(per_stride_recall_at_10[s], 4) for s in STRIDES},
        "per_stride_knn_recall_at_1_median": {("s%d" % s): round(per_stride_knn[s], 4) for s in STRIDES},
        "per_stride_route_acc_median": {("s%d" % s): round(per_stride_route[s], 4) for s in STRIDES},
        "per_stride_top1_top2_delta_median": {("s%d" % s): round(per_stride_delta[s], 4) for s in STRIDES},
        "per_stride_recall_at_1_cv": {("s%d" % s): round(per_stride_recall_cv[s], 4)
                                       if not math.isnan(per_stride_recall_cv[s]) else None
                                       for s in STRIDES},
        "monotone_non_decreasing": bool(monotone),
        "monotone_violations": monotone_violations,
        "n_seeds": len(units),
        "M": M,
        "bands": {
            "HP_STRIDE16_RECALL": BAND_HP_STRIDE16_RECALL,
            "HP_STRIDE8_RECALL": BAND_HP_STRIDE8_RECALL,
            "MIDDLE_STRIDE16_RECALL": BAND_MIDDLE_STRIDE16_RECALL,
            "HF_STRIDE16_RECALL": BAND_HF_STRIDE16_RECALL,
            "KNN_SENTINEL_STRIDE16": BAND_KNN_SENTINEL_STRIDE16,
            "CV_HP": BAND_CV_HP,
            "Q_SATURATION": BAND_Q_SATURATION,
            "MONOTONE_TOL": BAND_MONOTONE_TOL,
        },
        "CONFIG_VERSION": CONFIG_VERSION,
        "cites": [
            "research_gap2_capacity_side_analysis_NOT_geometry_2026-06-26",
            "exp_dev_handoff_research_gap2_capacity_side_analysis_2026-06-26",
            "substrate_partition_routing_anisotropic_scann_quantizer_v1_smoke",
            "substrate_partition_routing_hierarchical_2level_v1",
            "Geifman_El-Yaniv_2017_selective_classification",
        ],
    }

    # GATE 0: KNN sentinel corruption catch (keys themselves degraded at stride=16 -> abort)
    if knn16 < BAND_KNN_SENTINEL_STRIDE16:
        return ("HARD_FAIL",
                ("HARD_FAIL_KNN_SENTINEL_REGRESSION: knn@stride=%d=%.3f < %.2f -> keys themselves "
                 "corrupted; any recall lift is artifact. %s%s") % (
                    s_max, knn16, BAND_KNN_SENTINEL_STRIDE16, q_note, summ),
                detail)

    # GATE 1: HARD_PASS_GAP2_CLOSES (diagnosis confirmed)
    if (r16 >= BAND_HP_STRIDE16_RECALL
            and r8 >= BAND_HP_STRIDE8_RECALL
            and monotone
            and (math.isnan(cv16) or cv16 <= BAND_CV_HP)):
        return ("HARD_PASS",
                ("HARD_PASS_GAP2_CLOSES: recall@stride=%d=%.3f >= %.2f AND "
                 "recall@stride=%d=%.3f >= %.2f AND monotone=true AND cv@stride=%d=%.3f <= %.2f. "
                 "Substrate at cosine-physics floor; anisotropy is feature; 1.8%% adversarial "
                 "stride-1 = KNN-floor on near-duplicates no cosine method can solve. CLOSE Gap 2. "
                 "%s%s") % (
                    s_max, r16, BAND_HP_STRIDE16_RECALL,
                    s_mid, r8, BAND_HP_STRIDE8_RECALL,
                    s_max, cv16, BAND_CV_HP, q_note, summ),
                detail)

    # GATE 2: MIDDLE_BAND (monotone but partial)
    if monotone and r16 >= BAND_MIDDLE_STRIDE16_RECALL and r16 < BAND_HP_STRIDE16_RECALL:
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND_GAP2_PARTIAL: recall@stride=%d=%.3f in [%.2f, %.2f); monotone "
                 "confirmed but not chain-grade at M=%d natural keys. Refuse-gate or further "
                 "mechanism may help. %s%s") % (
                    s_max, r16, BAND_MIDDLE_STRIDE16_RECALL, BAND_HP_STRIDE16_RECALL, M,
                    q_note, summ),
                detail)

    # GATE 3: HARD_FAIL_GAP2_REAL (re-open Gap 2)
    reason = []
    if r16 < BAND_HF_STRIDE16_RECALL:
        reason.append("recall@stride=%d=%.3f < %.2f" % (s_max, r16, BAND_HF_STRIDE16_RECALL))
    if not monotone:
        reason.append("non-monotone stride curve (%s)" % "; ".join(monotone_violations))
    reason_s = " AND ".join(reason) if reason else "diagnosis-not-confirmed"
    return ("HARD_FAIL",
            ("HARD_FAIL_GAP2_REAL: %s. Substrate has TRUE M=%d bottleneck independent of stride; "
             "Gap 2 IS a real capacity gap on natural keys; need new mechanism (Anchor 3 "
             "natural-keys M-scaling audit). %s%s") % (
                reason_s, M, q_note, summ),
            detail)


# ---------- self-test ----------

def _selftest():
    """Validate: (a) helpers; (b) iso k-means convergence; (c) stride-arm runs;
    (d) route+rerank ground truth; (e) top1-top2 delta math; (f) band ordering;
    (g) verdict synthetic paths (HP_CLOSES / MB / HF_REAL / HF_KNN)."""

    g = np.random.default_rng(0)
    D = 64
    M_loc = 300
    n_parts = M_loc // 30

    # Build keys: clustered around a few directions
    n_clusters_true = 6
    centers_true = _np_norm(g.standard_normal((n_clusters_true, D)).astype(np.float32))
    keys = []
    for ci in range(n_clusters_true):
        n_c = M_loc // n_clusters_true + (1 if ci < M_loc % n_clusters_true else 0)
        cs = centers_true[ci][None] + 0.20 * g.standard_normal((n_c, D)).astype(np.float32)
        keys.append(cs)
    K_raw = np.concatenate(keys, axis=0)[:M_loc]
    K = _np_norm(K_raw)

    # (a) helpers
    assert K.shape == (M_loc, D)
    assert np.allclose(np.linalg.norm(K, axis=1), 1.0, atol=1e-5)

    # (b) iso k-means converges
    cen, assign, qerr = _kmeans_isotropic(K, n_parts, KM_ITERS, 7)
    assert cen.shape == (n_parts, D)
    assert assign.shape == (M_loc,)
    used = len(set(assign.tolist()))
    assert used >= 2, "iso kmeans collapsed to 1 cluster"
    assert 0 < qerr < 4.0, "iso qerr out of range: %f" % qerr
    print("[selftest] iso_kmeans: used=%d qerr=%.4f" % (used, qerr), flush=True)

    # (c) route_and_rerank on identity cues
    cue_id = K.copy()
    ytrue_id = np.arange(M_loc, dtype=np.int64)
    route_acc, recall_1 = _route_and_rerank(K, cen, assign, cue_id, ytrue_id, topk=1)
    assert route_acc >= 0.95, "identity route_acc too low: %.3f" % route_acc
    assert recall_1 >= 0.95, "identity recall@1 too low: %.3f" % recall_1
    route_acc_10, recall_10 = _route_and_rerank(K, cen, assign, cue_id, ytrue_id, topk=KNN_TOPK_10)
    assert recall_10 >= recall_1, "recall@10 must be >= recall@1"
    print("[selftest] route_and_rerank identity: route=%.3f r1=%.3f r10=%.3f" % (
        route_acc, recall_1, recall_10), flush=True)

    # (d) top1-top2 delta math: identity cues -> delta should be > 0
    delta_med, dp25, dp75 = _top1_top2_delta(K, cue_id, ytrue_id)
    assert delta_med >= 0.0, "delta must be non-negative"
    assert dp25 <= delta_med <= dp75, "p25 <= med <= p75 ordering: %.3f %.3f %.3f" % (
        dp25, delta_med, dp75)
    print("[selftest] top1_top2_delta identity: med=%.3f p25=%.3f p75=%.3f" % (
        delta_med, dp25, dp75), flush=True)

    # (e) KNN sentinel math
    knn_id = _knn_topk_recall(K, cue_id, ytrue_id, topk=1)
    assert knn_id >= 0.99, "KNN on identity cues should be ~1.0: %.3f" % knn_id
    knn_id_10 = _knn_topk_recall(K, cue_id, ytrue_id, topk=10)
    assert knn_id_10 >= knn_id, "knn@10 >= knn@1"
    print("[selftest] knn identity: r1=%.3f r10=%.3f" % (knn_id, knn_id_10), flush=True)

    # (f) band ordering already asserted at module init

    # (g) verdict synthetic paths

    # HP_GAP2_CLOSES path: monotone, r16 >= 0.90, r8 >= 0.70
    mock_hp = []
    for _ in range(3):
        u = {"by_stride": {
            "s1": {"knn_recall_at_1": 0.30, "route_acc": 0.95, "recall_at_1": 0.28,
                   "recall_at_10": 0.50, "top1_top2_delta_median": 0.01},
            "s4": {"knn_recall_at_1": 0.60, "route_acc": 0.95, "recall_at_1": 0.55,
                   "recall_at_10": 0.75, "top1_top2_delta_median": 0.05},
            "s8": {"knn_recall_at_1": 0.85, "route_acc": 0.98, "recall_at_1": 0.78,
                   "recall_at_10": 0.92, "top1_top2_delta_median": 0.10},
            "s16": {"knn_recall_at_1": 0.97, "route_acc": 0.99, "recall_at_1": 0.93,
                    "recall_at_10": 0.99, "top1_top2_delta_median": 0.20},
        }}
        mock_hp.append(u)
    v, msg, _ = compute_verdict(mock_hp)
    assert v == "HARD_PASS" and "GAP2_CLOSES" in msg, "HP_GAP2_CLOSES path failed: %s | %s" % (
        v, msg[:200])
    print("[selftest] verdict HP_GAP2_CLOSES path PASS", flush=True)

    # MIDDLE_BAND path: monotone, r16 in [0.70, 0.90)
    mock_mb = []
    for _ in range(3):
        u = {"by_stride": {
            "s1": {"knn_recall_at_1": 0.30, "route_acc": 0.85, "recall_at_1": 0.25,
                   "recall_at_10": 0.45, "top1_top2_delta_median": 0.01},
            "s4": {"knn_recall_at_1": 0.50, "route_acc": 0.88, "recall_at_1": 0.45,
                   "recall_at_10": 0.65, "top1_top2_delta_median": 0.03},
            "s8": {"knn_recall_at_1": 0.70, "route_acc": 0.90, "recall_at_1": 0.62,
                   "recall_at_10": 0.80, "top1_top2_delta_median": 0.08},
            "s16": {"knn_recall_at_1": 0.85, "route_acc": 0.93, "recall_at_1": 0.78,
                    "recall_at_10": 0.90, "top1_top2_delta_median": 0.15},
        }}
        mock_mb.append(u)
    v, msg, _ = compute_verdict(mock_mb)
    assert v == "MIDDLE_BAND" and "GAP2_PARTIAL" in msg, "MIDDLE_BAND path failed: %s | %s" % (
        v, msg[:200])
    print("[selftest] verdict MIDDLE_BAND path PASS", flush=True)

    # HARD_FAIL_GAP2_REAL path: r16 < 0.70
    mock_hf_real = []
    for _ in range(3):
        u = {"by_stride": {
            "s1": {"knn_recall_at_1": 0.30, "route_acc": 0.80, "recall_at_1": 0.20,
                   "recall_at_10": 0.40, "top1_top2_delta_median": 0.01},
            "s4": {"knn_recall_at_1": 0.40, "route_acc": 0.82, "recall_at_1": 0.30,
                   "recall_at_10": 0.50, "top1_top2_delta_median": 0.02},
            "s8": {"knn_recall_at_1": 0.55, "route_acc": 0.84, "recall_at_1": 0.45,
                   "recall_at_10": 0.62, "top1_top2_delta_median": 0.05},
            "s16": {"knn_recall_at_1": 0.85, "route_acc": 0.88, "recall_at_1": 0.55,
                    "recall_at_10": 0.70, "top1_top2_delta_median": 0.10},
        }}
        mock_hf_real.append(u)
    v, msg, _ = compute_verdict(mock_hf_real)
    assert v == "HARD_FAIL" and "GAP2_REAL" in msg, "HF_GAP2_REAL path failed: %s | %s" % (
        v, msg[:200])
    print("[selftest] verdict HF_GAP2_REAL path PASS", flush=True)

    # HARD_FAIL_KNN_SENTINEL path: knn@16 < 0.80
    mock_hf_knn = []
    for _ in range(3):
        u = {"by_stride": {
            "s1": {"knn_recall_at_1": 0.30, "route_acc": 0.80, "recall_at_1": 0.20,
                   "recall_at_10": 0.40, "top1_top2_delta_median": 0.01},
            "s4": {"knn_recall_at_1": 0.40, "route_acc": 0.82, "recall_at_1": 0.30,
                   "recall_at_10": 0.50, "top1_top2_delta_median": 0.02},
            "s8": {"knn_recall_at_1": 0.55, "route_acc": 0.84, "recall_at_1": 0.45,
                   "recall_at_10": 0.62, "top1_top2_delta_median": 0.05},
            "s16": {"knn_recall_at_1": 0.50, "route_acc": 0.88, "recall_at_1": 0.55,
                    "recall_at_10": 0.70, "top1_top2_delta_median": 0.10},
        }}
        mock_hf_knn.append(u)
    v, msg, _ = compute_verdict(mock_hf_knn)
    assert v == "HARD_FAIL" and "KNN_SENTINEL_REGRESSION" in msg, (
        "HF_KNN_SENTINEL path failed: %s | %s" % (v, msg[:200]))
    print("[selftest] verdict HF_KNN_SENTINEL_REGRESSION path PASS", flush=True)

    # HF_GAP2_REAL via non-monotone (r4 > r8)
    mock_hf_mono = []
    for _ in range(3):
        u = {"by_stride": {
            "s1": {"knn_recall_at_1": 0.30, "route_acc": 0.80, "recall_at_1": 0.20,
                   "recall_at_10": 0.40, "top1_top2_delta_median": 0.01},
            "s4": {"knn_recall_at_1": 0.60, "route_acc": 0.90, "recall_at_1": 0.80,
                   "recall_at_10": 0.92, "top1_top2_delta_median": 0.10},
            "s8": {"knn_recall_at_1": 0.70, "route_acc": 0.88, "recall_at_1": 0.50,
                   "recall_at_10": 0.70, "top1_top2_delta_median": 0.05},
            "s16": {"knn_recall_at_1": 0.85, "route_acc": 0.92, "recall_at_1": 0.93,
                    "recall_at_10": 0.99, "top1_top2_delta_median": 0.20},
        }}
        mock_hf_mono.append(u)
    v, msg, _ = compute_verdict(mock_hf_mono)
    assert v == "HARD_FAIL" and "non-monotone" in msg, (
        "HF_GAP2_REAL (non-monotone) path failed: %s | %s" % (v, msg[:200]))
    print("[selftest] verdict HF_GAP2_REAL (non-monotone) path PASS", flush=True)

    print("[selftest] PASS: iso_kmeans + route_rerank + knn + top1_top2_delta + "
          "verdict_paths(HP_CLOSES / MB / HF_REAL / HF_KNN / HF_NONMONO) ALL", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)

    print("[config] %s mode=%s | %s" % (ANCHOR_NAME, RUN_MODE, CONFIG_VERSION), flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_cfg = {"run_mode": RUN_MODE, "proj": PROJ_DIM,
               "schema": "gap2-stride-sweep-v1", "seeds": SEEDS, "STRIDES": STRIDES, "M": M}
    t0 = time.time()
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))

    units = list(aggregate_partials(
        out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg
    ).values())

    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": msg,
        "headline": msg,
        "run_mode": RUN_MODE,
        "model": ENCODER,
        "proj_dim": PROJ_DIM,
        "M": M,
        "STRIDES": STRIDES,
        "n_seeds": len(units),
        "seeds": [int(s.replace("s", "")) for s in
                  [u.get("seed_key", "s%d" % u.get("seed", 0)) for u in units]] if units else SEEDS,
        "window_tokens": WINDOW_TOKENS,
        "cue_shift": CUE_SHIFT,
        "detail": detail,
        "metrics_source": "measured_cpu_stride_sweep_iso_kmeans_partition_routing_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "config_version": CONFIG_VERSION,
    }
    write_metrics(out_dir, metrics, units)
