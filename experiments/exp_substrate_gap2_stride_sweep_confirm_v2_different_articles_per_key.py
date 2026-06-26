"""GAP 2 CLOSE DIAGNOSTIC V2 -- different-articles-per-key reframe.

PARENT CONTEXT (v1 SMOKE-GATED 2026-06-26):
  - v1 (stride-sweep on same-region prose) SMOKE_HARD_FAIL_KNN_SENTINEL + non-
    monotonic. Smoke evidence: across all strides [1,4,8,16], substrate recall
    tracks KNN within +-0.01 (substrate IS at cosine-physics floor; diagnosis
    CONFIRMED) but the absolute curve peaks at stride=4 (recall=0.151) and
    DECREASES at stride=16 (recall=0.099). text8 boilerplate-rich Wikipedia
    has natural similarity ceiling on disjoint windows from same article so
    the stride trick CAN'T demonstrate chain-grade escape regardless of M.
  - Research Option 1 reframe: re-author with KEY CONSTRUCTION where EACH KEY
    comes from a DIFFERENT article (topically distant region of text8). This
    is how chain-grade ledger entries got built historically (fly-LSH chain-
    grade at M=10k used per-key independent topics).

DECISION NOTE:
  - notes/exp_dev_to_research_gap2_stride_sweep_SMOKE_GATED_nonmonotonic_2026-06-26.md
  - Research re-authoring authorization: REFRAME per Option 1.

MECHANISM (one paragraph):
  Each KEY is a 16-token window drawn from a RANDOM region of text8, with keys
  spaced TOPICALLY-DISTANT-APART (stride between key starts = 10000 words). This
  near-guarantees keys come from different Wikipedia articles. text8 has 17M
  words and average article ~few thousand words, so 10000-word stride between
  starts crosses article boundaries with high probability. Compare against
  ARM_SAME_ARTICLE_STRIDE_16 (v1's stride=16 from contiguous region) as a rail
  to expose article-boundary effect. KNN sentinel verifies the substrate-at-
  cosine-floor relationship is preserved by the new construction (sentinel
  should remain within 0.05 of substrate; if it diverges >0.05 the new
  construction itself is confounded -- GATE_AND_REPORT not full-dispatch).

  Goal: demonstrate substrate (at cosine-physics floor) achieves chain-grade
  >=0.90 at M=10k WITH proper key independence. If yes -> Gap 2 closes cleanly:
  substrate IS at cosine-physics optimum AND cosine-physics IS chain-grade-
  capable on properly-independent keys.

ARMS (per Research re-author spec):
  ARM_DIFFERENT_ARTICLES (the test):
    Each key = 16-token window from a different region of text8; key starts
    spaced KEY_STRIDE_WORDS=10000 apart -> different articles with high prob.

  ARM_SAME_ARTICLE_STRIDE_16 (the rail; v1's stride=16 baseline):
    Each key = 16-token window from CONTIGUOUS text8 region at stride=16 between
    key starts (disjoint windows from likely-same article).

  ARM_KNN_BASELINE (sentinel; should match ARM_DIFFERENT_ARTICLES within 0.05):
    Exhaustive cosine KNN recall@1 on ARM_DIFFERENT_ARTICLES keys; preserves
    the substrate-at-floor relationship verification.

  ANALYSIS LAYER (refuse-gate top1-top2 cosine delta):
    Per arm: median + p25/p75 delta on cue-key cosine post-rerank. Higher delta
    on ARM_DIFFERENT_ARTICLES expected -> independent keys mean clearer top-1
    separation; refuse-gate primitive corroborated.

  PER-ARM METRICS:
    - recall_at_1, recall_at_10, route_acc
    - knn_recall_at_1 (sentinel)
    - top1_top2_delta_median, _p25, _p75

PRE-REGISTERED BANDS (LOCKED AT MODULE INIT):

  HARD_PASS_GAP2_CLOSES (diagnosis confirmed; Gap 2 CLOSES):
    ARM_DIFFERENT_ARTICLES recall_at_1 >= 0.90
    AND ARM_DIFFERENT_ARTICLES beats ARM_SAME_ARTICLE_STRIDE_16 by >= 0.50
    AND substrate-vs-KNN delta within 0.05 (substrate-at-KNN-floor preserved)
    AND cv across seeds for ARM_DIFFERENT_ARTICLES recall <= 0.05
    -- substrate is at cosine-physics floor; cosine-physics IS chain-grade-
    capable when keys are properly independent. Anisotropy is feature. CLOSE
    Gap 2.

  HARD_PASS_PARTIAL (significant lift but below chain-grade):
    ARM_DIFFERENT_ARTICLES recall_at_1 in [0.70, 0.90)
    AND substrate-vs-KNN delta within 0.05
    -- substrate gains independent-keys lift but not chain-grade at M=10k;
    refuse-gate or further mechanism may help.

  MIDDLE_BAND (modest lift):
    ARM_DIFFERENT_ARTICLES recall_at_1 in [0.50, 0.70)
    AND substrate-vs-KNN delta within 0.05
    -- substrate gains some lift from independent keys but Gap 2 partial.

  HARD_FAIL_GAP2_REAL (Gap 2 is real even with independent keys):
    ARM_DIFFERENT_ARTICLES recall_at_1 < 0.50
    -- even with proper key independence, substrate can't chain-grade at M=10k.
    Gap 2 is a real capacity gap. Need new mechanism.

  HARD_FAIL_KNN_DIVERGENCE (test-bed confound; GATE; report differently):
    |ARM_DIFFERENT_ARTICLES recall_at_1 - ARM_KNN_BASELINE recall_at_1| > 0.05
    -- the different-articles construction broke the substrate-at-KNN-floor
    relationship (KNN sentinel diverged from substrate). NOT a Gap 2 verdict;
    the cell is the confound. Per smoke gate, GATE if smoke shows this; for
    full, mark as TEST-DESIGN_FAIL.

Q-DISCIPLINE: any arm >= 0.995 flags suspect saturation; bands favor under-claim.

Disciplines (load-bearing):
  - ASCII only.
  - Substrate-only at inference; encoder is SETUP-TIME hidden-state extractor.
  - Per-arm metrics (Fix #28); read metrics.json per-arm, NOT verdict_msg.
  - atexit per-seed checkpoint + restartable.
  - META_M7 capacity-sensitive dims (PROJ_DIM, PART_SIZE_TARGET, KM_ITERS,
    KNN_TOPK, WINDOW_TOKENS, CUE_SHIFT) IDENTICAL across smoke and full --
    ONLY M, n_seeds, encoder, and TRAIN_STEPS differ.
  - Smoke gate FIRST: if smoke shows substrate-vs-KNN delta > 0.05 in ARM_
    DIFFERENT_ARTICLES, GATE -- different-articles construction confounded.

Routing: local CPU (Tier A); ~1.5-2 hr full wall on laptop.

Cites:
  - exp_dev_to_research_gap2_stride_sweep_SMOKE_GATED_nonmonotonic_2026-06-26 (v1 gate)
  - research_gap2_capacity_side_analysis_NOT_geometry_2026-06-26 (diagnosis)
  - exp_dev_handoff_research_gap2_capacity_side_analysis_2026-06-26 (Anchor 1+2)
  - data/exp_substrate_partition_routing_hierarchical_2level_v1/metrics.json (chain-grade spine)
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

ANCHOR_NAME = "substrate_gap2_stride_sweep_confirm_v2_different_articles_per_key"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# CAPACITY-SENSITIVE (META_M7) -- IDENTICAL smoke/full
PROJ_DIM = 768                  # matches v1 + polarimetric anchor
PART_SIZE_TARGET = 2000         # matches substrate's chain-grade partition routing
KM_ITERS = 25                   # k-means EM iterations
KNN_TOPK = 1
KNN_TOPK_10 = 10
SIGMA = 0.1                     # cue noise sigma
MAX_Q = 1500                    # max cue count per arm
WINDOW_TOKENS = 16              # 16-token windows on natural Pythia prose
CUE_SHIFT = 1                   # cue is shifted-by-1 from key (within-key cue noise model)

# Key-construction parameter (v2 specific): word-distance between key starts in
# ARM_DIFFERENT_ARTICLES. 10000 words >> avg Wikipedia article (~few thousand),
# so adjacent keys near-certainly cross article boundaries.
KEY_STRIDE_WORDS_DIFFERENT_ARTICLES = 10000

# ARM_SAME_ARTICLE_STRIDE_16 (v1 rail): stride=16 between key starts (disjoint
# windows from contiguous region).
KEY_STRIDE_WORDS_SAME_ARTICLE = 16

ARM_NAMES = ["DIFFERENT_ARTICLES", "SAME_ARTICLE_STRIDE_16"]

# MODE-DEPENDENT
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
BAND_HP_DIFFART_RECALL = 0.90          # ARM_DIFFERENT_ARTICLES recall_at_1 floor for HARD_PASS
BAND_HP_BEATS_RAIL_DELTA = 0.50        # ARM_DIFF beats ARM_SAME by >= this
BAND_HP_PARTIAL_RECALL_LO = 0.70       # HP_PARTIAL range [0.70, 0.90)
BAND_MIDDLE_RECALL_LO = 0.50           # MIDDLE_BAND range [0.50, 0.70)
BAND_HF_REAL_RECALL = 0.50             # below this -> HARD_FAIL_GAP2_REAL
BAND_SUBSTRATE_KNN_DELTA = 0.05        # |substrate - knn| > this -> KNN_DIVERGENCE
BAND_CV_HP = 0.05                      # seed cv ceiling for HARD_PASS
BAND_Q_SATURATION = 0.995              # suspect saturation

# Band ordering assertions
assert 0.0 < BAND_HF_REAL_RECALL <= BAND_MIDDLE_RECALL_LO <= BAND_HP_PARTIAL_RECALL_LO <= BAND_HP_DIFFART_RECALL < 1.0, (
    "diffart recall band ordering"
)
assert 0.0 < BAND_HP_BEATS_RAIL_DELTA < 1.0, "beats-rail delta"
assert 0.0 < BAND_SUBSTRATE_KNN_DELTA < 0.5, "substrate-vs-knn divergence band"

CONFIG_VERSION = (
    "gap2_v2_different_articles_per_key (arms=%s; "
    "key_stride_diff_articles=%d_words key_stride_same_article=%d_words; prose=text8) | "
    "proj=%d part_target=%d km_iters=%d sigma=%.2f window=%dt cue_shift=%d | "
    "seeds=%s M=%d encoder=%s | CPU_numpy"
) % (
    ARM_NAMES,
    KEY_STRIDE_WORDS_DIFFERENT_ARTICLES, KEY_STRIDE_WORDS_SAME_ARTICLE,
    PROJ_DIM, PART_SIZE_TARGET, KM_ITERS, SIGMA, WINDOW_TOKENS, CUE_SHIFT,
    SEEDS, M, ENCODER,
)


# ---------- numerical helpers (unchanged from v1) ----------

def _np_norm(X):
    return (X / (np.linalg.norm(X, axis=-1, keepdims=True) + 1e-8)).astype(np.float32)


def _knn_topk_recall(K, cue, ytrue_idx, topk=1):
    """Cosine exhaustive KNN; recall@topk over normalized vectors.

    K: (M, D). cue: (Q, D). ytrue_idx: (Q,). Returns mean recall.
    """
    Kn = _np_norm(K)
    cn = _np_norm(cue)
    sim = cn @ Kn.T
    if topk == 1:
        idx = np.argmax(sim, axis=1)
        return float((idx == ytrue_idx).mean())
    topk_idx = np.argpartition(sim, -topk, axis=1)[:, -topk:]
    hits = np.any(topk_idx == ytrue_idx[:, None], axis=1)
    return float(hits.mean())


def _top1_top2_delta(K, cue, ytrue_idx):
    """Median + p25/p75 top1-top2 cosine delta across queries (refuse-gate primitive)."""
    Kn = _np_norm(K)
    cn = _np_norm(cue)
    sim = cn @ Kn.T
    part = np.argpartition(sim, -2, axis=1)[:, -2:]
    top_vals = np.take_along_axis(sim, part, axis=1)
    top_sorted = np.sort(top_vals, axis=1)
    delta = top_sorted[:, 1] - top_sorted[:, 0]
    return (float(np.median(delta)),
            float(np.percentile(delta, 25)),
            float(np.percentile(delta, 75)))


# ---------- ISOTROPIC k-means (unchanged from v1) ----------

def _kmeans_isotropic(K, n_parts, iters, seed):
    """Standard L2 k-means partition assignment.

    K: (M, D) normalized keys.
    Returns: centroids (n_parts, D), assign (M,), quant_err float.
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


# ---------- arm evaluation: route + within-partition rerank (unchanged from v1) ----------

def _route_and_rerank(K, centroids, assign, cue, ytrue_idx, topk=1):
    """For each cue: route to argmax-cosine partition; rerank within by exact cosine."""
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


# ---------- per-arm runner ----------

def _arm_eval(Kp, seed_for_arm, arm_label):
    """Run the routing arm on pre-encoded keys.

    Kp: (M, D) projected keys (built upstream by arm-specific key construction).
    Returns full arm metrics dict.
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

    # KNN sentinel
    knn_r1 = _knn_topk_recall(K, cue, ytrue_idx, topk=KNN_TOPK)

    n_parts = max(2, M_loc // PART_SIZE_TARGET)

    t0 = time.time()
    cen, assign, qerr = _kmeans_isotropic(K, n_parts, KM_ITERS, seed_for_arm)
    route_acc_1, recall_1 = _route_and_rerank(K, cen, assign, cue, ytrue_idx, topk=1)
    route_acc_10, recall_10 = _route_and_rerank(K, cen, assign, cue, ytrue_idx, topk=KNN_TOPK_10)
    t_arm = time.time() - t0

    delta_med, delta_p25, delta_p75 = _top1_top2_delta(K, cue, ytrue_idx)

    return {
        "arm": arm_label,
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

_TEXT8_PATH = REPO / "data" / "text8_cache" / "text8.txt"
_TEXT8_CACHE = None


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


# ---------- KEY CONSTRUCTION (the v2 reframe) ----------

def _build_keys_different_articles(seed: int, n_keys: int) -> List[str]:
    """Build n_keys 16-token windows, each from a TOPICALLY-DISTANT region of text8.

    Strategy: draw n_keys random start positions from text8, spaced by at least
    KEY_STRIDE_WORDS_DIFFERENT_ARTICLES apart. With text8's 17M words and
    Wikipedia avg article ~few thousand words, 10000-word spacing near-guarantees
    each key comes from a different article.

    Implementation: pick non-overlapping intervals of width WINDOW_TOKENS+CUE_SHIFT
    spaced by KEY_STRIDE_WORDS apart; randomize order.
    """
    words = _load_text8_words()
    g = np.random.default_rng(seed * 100003 + 7)
    n_words = len(words)
    needed_span = n_keys * KEY_STRIDE_WORDS_DIFFERENT_ARTICLES + WINDOW_TOKENS + CUE_SHIFT + 50
    if needed_span > n_words:
        # downsize stride if M is too large for corpus
        max_stride = (n_words - WINDOW_TOKENS - CUE_SHIFT - 50) // max(n_keys, 1)
        if max_stride < WINDOW_TOKENS * 4:
            raise RuntimeError(
                "text8 too small for n_keys=%d at stride>=4*WINDOW; have %d words" % (
                    n_keys, n_words))
        stride_use = max_stride
        print("[diff-articles] WARNING: stride downsized %d -> %d (corpus limit)" % (
            KEY_STRIDE_WORDS_DIFFERENT_ARTICLES, stride_use), flush=True)
    else:
        stride_use = KEY_STRIDE_WORDS_DIFFERENT_ARTICLES

    # pick a random base offset so we don't always start from word 0
    max_base = n_words - n_keys * stride_use - WINDOW_TOKENS - CUE_SHIFT
    base_off = int(g.integers(0, max(max_base, 1)))
    # add small jitter per key so positions aren't exact multiples
    jitter_max = max(1, stride_use // 8)
    starts = []
    for i in range(n_keys):
        jitter = int(g.integers(0, jitter_max))
        s = base_off + i * stride_use + jitter
        # clamp safety
        if s + WINDOW_TOKENS + CUE_SHIFT > n_words:
            s = n_words - WINDOW_TOKENS - CUE_SHIFT - 1
        starts.append(s)
    # shuffle ORDER so that ytrue_idx position isn't correlated with corpus order
    starts_arr = np.asarray(starts, dtype=np.int64)
    perm = g.permutation(n_keys)
    starts_arr = starts_arr[perm]

    keys = []
    for s in starts_arr:
        keys.append(" ".join(words[int(s):int(s) + WINDOW_TOKENS]))
    return keys


def _build_keys_same_article(seed: int, n_keys: int) -> List[str]:
    """v1's stride=16 rail: contiguous text8 region, disjoint 16-token windows.

    Strategy: pick ONE random contiguous block of text8; take consecutive 16-token
    windows at stride=KEY_STRIDE_WORDS_SAME_ARTICLE=16 (disjoint windows from
    likely-same article).
    """
    words = _load_text8_words()
    g = np.random.default_rng(seed * 200003 + 13)
    n_words = len(words)
    needed = n_keys * KEY_STRIDE_WORDS_SAME_ARTICLE + WINDOW_TOKENS + CUE_SHIFT + 50
    if needed > n_words:
        raise RuntimeError("text8 too small for same-article construction at n_keys=%d" % n_keys)
    base = int(g.integers(0, n_words - needed))

    keys = []
    for i in range(n_keys):
        s = base + i * KEY_STRIDE_WORDS_SAME_ARTICLE
        keys.append(" ".join(words[s:s + WINDOW_TOKENS]))
    return keys


def _train_W(seed: int, encode, train_contrastive):
    """Train ONE contrastive projection W (reused across both arms).

    Train pool is a contiguous text8 block (W is encoder->substrate projection;
    arm is a property of EVAL-TIME KEY CONSTRUCTION, not of training).
    """
    g = np.random.default_rng(seed * 1009 + 17)
    words = _load_text8_words()
    needed = TRAIN_M + WINDOW_TOKENS + CUE_SHIFT + 50
    if needed >= len(words):
        raise RuntimeError("text8 too small for TRAIN_M=%d" % TRAIN_M)
    start = int(g.integers(0, len(words) - needed))
    block = words[start:start + needed]

    keys_tr = [" ".join(block[i:i + WINDOW_TOKENS]) for i in range(TRAIN_M)]
    cues_tr = [" ".join(block[i + CUE_SHIFT:i + CUE_SHIFT + WINDOW_TOKENS])
               for i in range(TRAIN_M)]
    print("[train] seed=%d TRAIN_M=%d sample_key=%r" % (
        seed, TRAIN_M, keys_tr[0][:60]), flush=True)
    K_tr = encode(keys_tr)
    Q_tr = encode(cues_tr)
    W = train_contrastive(K_tr, Q_tr, PROJ_DIM, TRAIN_STEPS, seed)
    return W


def _encode_keys_for_arm(seed: int, arm_label: str, encode, W) -> np.ndarray:
    """Build keys for the given arm, encode + project."""
    if arm_label == "DIFFERENT_ARTICLES":
        keys = _build_keys_different_articles(seed, M)
    elif arm_label == "SAME_ARTICLE_STRIDE_16":
        keys = _build_keys_same_article(seed, M)
    else:
        raise ValueError("unknown arm: %s" % arm_label)
    print("[encode-arm] seed=%d arm=%s M=%d sample_key=%r" % (
        seed, arm_label, M, keys[0][:60]), flush=True)
    K = encode(keys)
    Kp = (K @ W).astype(np.float32)
    return Kp


def run_unit(seed: int) -> Dict:
    print("[seed=%d] encoder=%s M=%d arms=%s mode=%s" % (
        seed, ENCODER, M, ARM_NAMES, RUN_MODE), flush=True)
    os.environ["HDLAB_RUN_MODE"] = RUN_MODE
    import experiments.exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 as _probe
    _probe.ENCODER = ENCODER
    encode = _probe.encode
    train_contrastive = _probe.train_contrastive

    t_train = time.time()
    W = _train_W(seed, encode, train_contrastive)
    t_train_s = time.time() - t_train
    print("  [seed=%d] train_W elapsed=%.1fs PROJ_DIM=%d" % (seed, t_train_s, PROJ_DIM), flush=True)

    by_arm = {}
    total_enc = 0.0
    for arm_label in ARM_NAMES:
        arm_seed = seed * 13 + abs(hash(arm_label)) % 997
        t_enc = time.time()
        Kp = _encode_keys_for_arm(seed, arm_label, encode, W)
        t_enc_s = time.time() - t_enc
        total_enc += t_enc_s
        t0 = time.time()
        a = _arm_eval(Kp, arm_seed, arm_label)
        a["encode_elapsed_s"] = round(t_enc_s, 2)
        by_arm[arm_label] = a
        print(("  [seed=%d arm=%s] knn=%.3f | route=%.3f recall@1=%.3f recall@10=%.3f "
               "delta_med=%.3f enc=%.1fs arm=%.1fs"
               ) % (
            seed, arm_label, a["knn_recall_at_1"], a["route_acc"], a["recall_at_1"], a["recall_at_10"],
            a["top1_top2_delta_median"], t_enc_s, time.time() - t0,
        ), flush=True)
    return {"seed": seed, "by_arm": by_arm,
            "train_W_elapsed_s": round(t_train_s, 2),
            "total_encoder_elapsed_s": round(total_enc, 2),
            "run_mode": RUN_MODE, "ARM_NAMES": ARM_NAMES, "N": PROJ_DIM, "M": M}


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

    def arm_vals(arm, key):
        out = []
        for u in units:
            r = u["by_arm"].get(arm, {})
            v = r.get(key) if isinstance(r, dict) else None
            if v is not None and isinstance(v, (int, float)) and not math.isnan(v):
                out.append(float(v))
        return out

    diffart_r1 = arm_vals("DIFFERENT_ARTICLES", "recall_at_1")
    diffart_knn = arm_vals("DIFFERENT_ARTICLES", "knn_recall_at_1")
    diffart_r10 = arm_vals("DIFFERENT_ARTICLES", "recall_at_10")
    diffart_route = arm_vals("DIFFERENT_ARTICLES", "route_acc")
    diffart_delta = arm_vals("DIFFERENT_ARTICLES", "top1_top2_delta_median")

    same_r1 = arm_vals("SAME_ARTICLE_STRIDE_16", "recall_at_1")
    same_knn = arm_vals("SAME_ARTICLE_STRIDE_16", "knn_recall_at_1")
    same_r10 = arm_vals("SAME_ARTICLE_STRIDE_16", "recall_at_10")
    same_route = arm_vals("SAME_ARTICLE_STRIDE_16", "route_acc")
    same_delta = arm_vals("SAME_ARTICLE_STRIDE_16", "top1_top2_delta_median")

    diff_r1_med, _ = _med_std(diffart_r1)
    diff_knn_med, _ = _med_std(diffart_knn)
    diff_r10_med, _ = _med_std(diffart_r10)
    diff_route_med, _ = _med_std(diffart_route)
    diff_delta_med, _ = _med_std(diffart_delta)
    diff_r1_cv = _cv(diffart_r1)

    same_r1_med, _ = _med_std(same_r1)
    same_knn_med, _ = _med_std(same_knn)
    same_r10_med, _ = _med_std(same_r10)
    same_route_med, _ = _med_std(same_route)
    same_delta_med, _ = _med_std(same_delta)

    # KNN-divergence sentinel: |substrate - knn| within band
    substrate_vs_knn_delta = abs(diff_r1_med - diff_knn_med)
    same_substrate_vs_knn_delta = abs(same_r1_med - same_knn_med)

    # Q-saturation
    q_flags = []
    for arm, rv in [("DIFFERENT_ARTICLES", diff_r1_med), ("SAME_ARTICLE_STRIDE_16", same_r1_med)]:
        if rv >= BAND_Q_SATURATION:
            q_flags.append("[Q-DISCIPLINE: %s recall=%.4f >= %.3f suspect saturation]" % (
                arm, rv, BAND_Q_SATURATION))
    q_note = " ".join(q_flags) + (" " if q_flags else "")

    beats_rail = diff_r1_med - same_r1_med

    summ = (
        "DIFF_ART: knn=%.3f route=%.3f r1=%.3f r10=%.3f delta=%.3f | "
        "SAME_ART: knn=%.3f route=%.3f r1=%.3f r10=%.3f delta=%.3f | "
        "beats_rail=%.3f sub_vs_knn(diff)=%.3f sub_vs_knn(same)=%.3f cv(diff)=%.3f"
    ) % (
        diff_knn_med, diff_route_med, diff_r1_med, diff_r10_med, diff_delta_med,
        same_knn_med, same_route_med, same_r1_med, same_r10_med, same_delta_med,
        beats_rail, substrate_vs_knn_delta, same_substrate_vs_knn_delta, diff_r1_cv,
    )

    detail = {
        "ARM_NAMES": ARM_NAMES,
        "per_arm_recall_at_1_median": {
            "DIFFERENT_ARTICLES": round(diff_r1_med, 4),
            "SAME_ARTICLE_STRIDE_16": round(same_r1_med, 4),
        },
        "per_arm_recall_at_10_median": {
            "DIFFERENT_ARTICLES": round(diff_r10_med, 4),
            "SAME_ARTICLE_STRIDE_16": round(same_r10_med, 4),
        },
        "per_arm_knn_recall_at_1_median": {
            "DIFFERENT_ARTICLES": round(diff_knn_med, 4),
            "SAME_ARTICLE_STRIDE_16": round(same_knn_med, 4),
        },
        "per_arm_route_acc_median": {
            "DIFFERENT_ARTICLES": round(diff_route_med, 4),
            "SAME_ARTICLE_STRIDE_16": round(same_route_med, 4),
        },
        "per_arm_top1_top2_delta_median": {
            "DIFFERENT_ARTICLES": round(diff_delta_med, 4),
            "SAME_ARTICLE_STRIDE_16": round(same_delta_med, 4),
        },
        "per_arm_recall_at_1_cv": {
            "DIFFERENT_ARTICLES": round(diff_r1_cv, 4) if not math.isnan(diff_r1_cv) else None,
        },
        "beats_rail_delta": round(beats_rail, 4),
        "substrate_vs_knn_delta_diffart": round(substrate_vs_knn_delta, 4),
        "substrate_vs_knn_delta_samearticle": round(same_substrate_vs_knn_delta, 4),
        "n_seeds": len(units),
        "M": M,
        "bands": {
            "HP_DIFFART_RECALL": BAND_HP_DIFFART_RECALL,
            "HP_BEATS_RAIL_DELTA": BAND_HP_BEATS_RAIL_DELTA,
            "HP_PARTIAL_RECALL_LO": BAND_HP_PARTIAL_RECALL_LO,
            "MIDDLE_RECALL_LO": BAND_MIDDLE_RECALL_LO,
            "HF_REAL_RECALL": BAND_HF_REAL_RECALL,
            "SUBSTRATE_KNN_DELTA": BAND_SUBSTRATE_KNN_DELTA,
            "CV_HP": BAND_CV_HP,
            "Q_SATURATION": BAND_Q_SATURATION,
        },
        "CONFIG_VERSION": CONFIG_VERSION,
        "cites": [
            "exp_dev_to_research_gap2_stride_sweep_SMOKE_GATED_nonmonotonic_2026-06-26",
            "research_gap2_capacity_side_analysis_NOT_geometry_2026-06-26",
            "exp_dev_handoff_research_gap2_capacity_side_analysis_2026-06-26",
            "substrate_partition_routing_hierarchical_2level_v1",
            "Geifman_El-Yaniv_2017_selective_classification",
        ],
    }

    # GATE 0: KNN divergence (test-bed confound). If substrate diverged from KNN by
    # more than the band on the DIFFERENT_ARTICLES arm, the new construction broke
    # the substrate-at-floor relationship; cell IS the confound.
    if substrate_vs_knn_delta > BAND_SUBSTRATE_KNN_DELTA:
        return ("HARD_FAIL",
                ("HARD_FAIL_KNN_DIVERGENCE: |substrate(%.3f) - knn(%.3f)|=%.3f > %.2f on "
                 "DIFFERENT_ARTICLES arm. The new key construction broke the substrate-at-"
                 "cosine-floor relationship; cell is the confound, NOT Gap 2 verdict. Mark "
                 "as TEST-DESIGN_FAIL; route back to Research. %s%s") % (
                    diff_r1_med, diff_knn_med, substrate_vs_knn_delta,
                    BAND_SUBSTRATE_KNN_DELTA, q_note, summ),
                detail)

    # GATE 1: HARD_PASS_GAP2_CLOSES
    if (diff_r1_med >= BAND_HP_DIFFART_RECALL
            and beats_rail >= BAND_HP_BEATS_RAIL_DELTA
            and (math.isnan(diff_r1_cv) or diff_r1_cv <= BAND_CV_HP)):
        return ("HARD_PASS",
                ("HARD_PASS_GAP2_CLOSES: DIFF_ARTICLES recall_at_1=%.3f >= %.2f AND "
                 "beats SAME_ARTICLE rail by %.3f >= %.2f AND substrate-at-KNN-floor "
                 "preserved (|delta|=%.3f <= %.2f) AND cv=%.3f <= %.2f. Substrate IS at "
                 "cosine-physics floor AND cosine-physics IS chain-grade-capable on "
                 "properly-independent keys. CLOSE Gap 2. %s%s") % (
                    diff_r1_med, BAND_HP_DIFFART_RECALL,
                    beats_rail, BAND_HP_BEATS_RAIL_DELTA,
                    substrate_vs_knn_delta, BAND_SUBSTRATE_KNN_DELTA,
                    diff_r1_cv, BAND_CV_HP, q_note, summ),
                detail)

    # GATE 2: HARD_PASS_PARTIAL [0.70, 0.90)
    if diff_r1_med >= BAND_HP_PARTIAL_RECALL_LO and diff_r1_med < BAND_HP_DIFFART_RECALL:
        return ("HARD_PASS",
                ("HARD_PASS_PARTIAL: DIFF_ARTICLES recall_at_1=%.3f in [%.2f, %.2f); "
                 "significant lift from key independence but not chain-grade at M=%d. "
                 "Refuse-gate or further mechanism may help. %s%s") % (
                    diff_r1_med, BAND_HP_PARTIAL_RECALL_LO, BAND_HP_DIFFART_RECALL, M,
                    q_note, summ),
                detail)

    # GATE 3: MIDDLE_BAND [0.50, 0.70)
    if diff_r1_med >= BAND_MIDDLE_RECALL_LO and diff_r1_med < BAND_HP_PARTIAL_RECALL_LO:
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND_GAP2_MODEST: DIFF_ARTICLES recall_at_1=%.3f in [%.2f, %.2f); "
                 "modest lift from key independence. Gap 2 partial. %s%s") % (
                    diff_r1_med, BAND_MIDDLE_RECALL_LO, BAND_HP_PARTIAL_RECALL_LO,
                    q_note, summ),
                detail)

    # GATE 4: HARD_FAIL_GAP2_REAL
    return ("HARD_FAIL",
            ("HARD_FAIL_GAP2_REAL: DIFF_ARTICLES recall_at_1=%.3f < %.2f even with proper "
             "key independence. Gap 2 is a REAL capacity gap at M=%d; need new mechanism "
             "(Anchor 3 natural-keys M-scaling audit). %s%s") % (
                diff_r1_med, BAND_HF_REAL_RECALL, M, q_note, summ),
            detail)


# ---------- self-test ----------

def _selftest():
    """Validate: helpers; iso k-means convergence; arm runs; route+rerank ground truth;
    top1-top2 delta math; band ordering; verdict synthetic paths (HP_CLOSES / HP_PARTIAL /
    MIDDLE / HF_REAL / HF_KNN_DIVERGENCE)."""

    g = np.random.default_rng(0)
    D = 64
    M_loc = 300
    n_parts = M_loc // 30

    n_clusters_true = 6
    centers_true = _np_norm(g.standard_normal((n_clusters_true, D)).astype(np.float32))
    keys = []
    for ci in range(n_clusters_true):
        n_c = M_loc // n_clusters_true + (1 if ci < M_loc % n_clusters_true else 0)
        cs = centers_true[ci][None] + 0.20 * g.standard_normal((n_c, D)).astype(np.float32)
        keys.append(cs)
    K_raw = np.concatenate(keys, axis=0)[:M_loc]
    K = _np_norm(K_raw)

    assert K.shape == (M_loc, D)
    assert np.allclose(np.linalg.norm(K, axis=1), 1.0, atol=1e-5)

    cen, assign, qerr = _kmeans_isotropic(K, n_parts, KM_ITERS, 7)
    assert cen.shape == (n_parts, D)
    used = len(set(assign.tolist()))
    assert used >= 2, "iso kmeans collapsed"
    assert 0 < qerr < 4.0, "iso qerr out of range: %f" % qerr
    print("[selftest] iso_kmeans: used=%d qerr=%.4f" % (used, qerr), flush=True)

    cue_id = K.copy()
    ytrue_id = np.arange(M_loc, dtype=np.int64)
    route_acc, recall_1 = _route_and_rerank(K, cen, assign, cue_id, ytrue_id, topk=1)
    assert route_acc >= 0.95, "identity route_acc too low: %.3f" % route_acc
    assert recall_1 >= 0.95, "identity recall@1 too low: %.3f" % recall_1
    _, recall_10 = _route_and_rerank(K, cen, assign, cue_id, ytrue_id, topk=KNN_TOPK_10)
    assert recall_10 >= recall_1, "recall@10 >= recall@1"
    print("[selftest] route_and_rerank identity: route=%.3f r1=%.3f r10=%.3f" % (
        route_acc, recall_1, recall_10), flush=True)

    delta_med, dp25, dp75 = _top1_top2_delta(K, cue_id, ytrue_id)
    assert delta_med >= 0.0
    assert dp25 <= delta_med <= dp75, "p25 <= med <= p75"
    print("[selftest] top1_top2_delta identity: med=%.3f p25=%.3f p75=%.3f" % (
        delta_med, dp25, dp75), flush=True)

    knn_id = _knn_topk_recall(K, cue_id, ytrue_id, topk=1)
    assert knn_id >= 0.99, "KNN identity ~1.0: %.3f" % knn_id
    print("[selftest] knn identity: r1=%.3f" % knn_id, flush=True)

    # Verdict paths
    # HP_CLOSES: diff_r1=0.93, beats_rail=0.50+, substrate=knn within 0.05, cv low
    mock_hp_closes = []
    for _ in range(3):
        u = {"by_arm": {
            "DIFFERENT_ARTICLES": {"knn_recall_at_1": 0.95, "route_acc": 0.95, "recall_at_1": 0.93,
                                   "recall_at_10": 0.99, "top1_top2_delta_median": 0.25},
            "SAME_ARTICLE_STRIDE_16": {"knn_recall_at_1": 0.20, "route_acc": 0.90, "recall_at_1": 0.18,
                                       "recall_at_10": 0.35, "top1_top2_delta_median": 0.02},
        }}
        mock_hp_closes.append(u)
    v, msg, _ = compute_verdict(mock_hp_closes)
    assert v == "HARD_PASS" and "GAP2_CLOSES" in msg, "HP_CLOSES failed: %s | %s" % (v, msg[:200])
    print("[selftest] verdict HP_GAP2_CLOSES path PASS", flush=True)

    # HP_PARTIAL: diff_r1=0.80, in [0.70, 0.90), substrate~knn
    mock_hp_partial = []
    for _ in range(3):
        u = {"by_arm": {
            "DIFFERENT_ARTICLES": {"knn_recall_at_1": 0.82, "route_acc": 0.85, "recall_at_1": 0.80,
                                   "recall_at_10": 0.92, "top1_top2_delta_median": 0.15},
            "SAME_ARTICLE_STRIDE_16": {"knn_recall_at_1": 0.20, "route_acc": 0.88, "recall_at_1": 0.18,
                                       "recall_at_10": 0.35, "top1_top2_delta_median": 0.02},
        }}
        mock_hp_partial.append(u)
    v, msg, _ = compute_verdict(mock_hp_partial)
    assert v == "HARD_PASS" and "PARTIAL" in msg, "HP_PARTIAL failed: %s | %s" % (v, msg[:200])
    print("[selftest] verdict HP_PARTIAL path PASS", flush=True)

    # MIDDLE: diff_r1=0.60, in [0.50, 0.70)
    mock_mb = []
    for _ in range(3):
        u = {"by_arm": {
            "DIFFERENT_ARTICLES": {"knn_recall_at_1": 0.62, "route_acc": 0.80, "recall_at_1": 0.60,
                                   "recall_at_10": 0.80, "top1_top2_delta_median": 0.10},
            "SAME_ARTICLE_STRIDE_16": {"knn_recall_at_1": 0.18, "route_acc": 0.83, "recall_at_1": 0.16,
                                       "recall_at_10": 0.30, "top1_top2_delta_median": 0.02},
        }}
        mock_mb.append(u)
    v, msg, _ = compute_verdict(mock_mb)
    assert v == "MIDDLE_BAND" and "MODEST" in msg, "MIDDLE failed: %s | %s" % (v, msg[:200])
    print("[selftest] verdict MIDDLE_BAND path PASS", flush=True)

    # HF_REAL: diff_r1=0.30, below 0.50, substrate=knn within 0.05
    mock_hf_real = []
    for _ in range(3):
        u = {"by_arm": {
            "DIFFERENT_ARTICLES": {"knn_recall_at_1": 0.31, "route_acc": 0.75, "recall_at_1": 0.30,
                                   "recall_at_10": 0.55, "top1_top2_delta_median": 0.05},
            "SAME_ARTICLE_STRIDE_16": {"knn_recall_at_1": 0.15, "route_acc": 0.80, "recall_at_1": 0.13,
                                       "recall_at_10": 0.25, "top1_top2_delta_median": 0.02},
        }}
        mock_hf_real.append(u)
    v, msg, _ = compute_verdict(mock_hf_real)
    assert v == "HARD_FAIL" and "GAP2_REAL" in msg, "HF_REAL failed: %s | %s" % (v, msg[:200])
    print("[selftest] verdict HF_GAP2_REAL path PASS", flush=True)

    # HF_KNN_DIVERGENCE: substrate=0.50, knn=0.95 (delta=0.45 >> 0.05)
    mock_hf_knn = []
    for _ in range(3):
        u = {"by_arm": {
            "DIFFERENT_ARTICLES": {"knn_recall_at_1": 0.95, "route_acc": 0.60, "recall_at_1": 0.50,
                                   "recall_at_10": 0.70, "top1_top2_delta_median": 0.10},
            "SAME_ARTICLE_STRIDE_16": {"knn_recall_at_1": 0.20, "route_acc": 0.85, "recall_at_1": 0.18,
                                       "recall_at_10": 0.35, "top1_top2_delta_median": 0.02},
        }}
        mock_hf_knn.append(u)
    v, msg, _ = compute_verdict(mock_hf_knn)
    assert v == "HARD_FAIL" and "KNN_DIVERGENCE" in msg, "HF_KNN_DIVERGENCE failed: %s | %s" % (
        v, msg[:200])
    print("[selftest] verdict HF_KNN_DIVERGENCE path PASS", flush=True)

    print("[selftest] PASS: helpers + iso_kmeans + route_rerank + knn + top1_top2_delta + "
          "verdict_paths(HP_CLOSES / HP_PARTIAL / MIDDLE / HF_REAL / HF_KNN_DIV) ALL", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)

    print("[config] %s mode=%s | %s" % (ANCHOR_NAME, RUN_MODE, CONFIG_VERSION), flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_cfg = {"run_mode": RUN_MODE, "proj": PROJ_DIM,
               "schema": "gap2-v2-different-articles-per-key",
               "seeds": SEEDS, "ARM_NAMES": ARM_NAMES, "M": M,
               "key_stride_diff_articles": KEY_STRIDE_WORDS_DIFFERENT_ARTICLES,
               "key_stride_same_article": KEY_STRIDE_WORDS_SAME_ARTICLE}
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
        "ARM_NAMES": ARM_NAMES,
        "n_seeds": len(units),
        "seeds": [int(s.replace("s", "")) for s in
                  [u.get("seed_key", "s%d" % u.get("seed", 0)) for u in units]] if units else SEEDS,
        "window_tokens": WINDOW_TOKENS,
        "cue_shift": CUE_SHIFT,
        "detail": detail,
        "metrics_source": "measured_cpu_v2_different_articles_per_key_iso_kmeans_partition_routing_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "config_version": CONFIG_VERSION,
    }
    write_metrics(out_dir, metrics, units)
