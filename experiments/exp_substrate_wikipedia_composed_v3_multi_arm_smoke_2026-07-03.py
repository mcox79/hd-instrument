"""exp_substrate_wikipedia_composed_v3_multi_arm_smoke_2026_07_03

USER-directed 2026-07-03 (Skunkworks-recommended optimal-info probe):
substrate-native brain-analog composed encoder v3 vs single-stream references
on Wikipedia title -> body retrieval.

Tests 4 questions in one 5-arm cell:
  Q1 Does composition earn its keep on multi-token (V3 vs best-single)?
  Q2 Does VWFA earn its keep on multi-token (VWFA vs char-trigram baseline)?
  Q3 Does PPMI-alone reproduce cross-cell (0.906 sanity)?
  Q4 Does char-trigram reproduce cross-cell (0.854 sanity)?

Arms (5 arms x 3 seeds = 15 units):
  ARM_V3_COMPOSED_EQUAL_ALPHA         -- hdlab.composed_encoder_v3.ComposedEncoderV3
                                        (VWFA + PPMI equal-alpha, score-level late-combine)
                                        LOAD_BEARING
  ARM_VWFA_ALONE                      -- hdlab.vwfa.VWFAEncoder (multi-scale, HRR pos-bind)
                                        LOAD_BEARING (drill-5 multi-token prediction)
  ARM_PPMI_ALONE                      -- hdlab.ppmi_sparse_encoder.PPMISparseEncoder
                                        REGRESSION CHECK; must reproduce r@5 ~ 0.906 +/- 0.005
  ARM_CHAR_TRIGRAM_UNSUP_REFERENCE    -- hdlab.char_trigram_encoder.CharTrigramEncoder
                                        REGRESSION CHECK; must reproduce r@5 ~ 0.854 +/- 0.001
  ARM_RANDOM_BASELINE                 -- random bipolar HDs (chance floor)

FRAMING DISCIPLINE (LOAD-BEARING; USER-locked; 3 Fix#28 hits today):
- SUBSTRATE KNOWS ALMOST NOTHING; this is MECHANISM COMPOSITION on SUPERVISED corpus regime.
- Not "first-ever"; composition primitive already probed on WordNet -- this is task-class generalize.
- Not a "physics law"; smoke-scale mechanism CHARACTERIZATION.
- Discriminator-narrows-at-scale caveat applies (V2-A smoke +0.06 -> FULL +0.012).
- HF on composition = stronger structural finding across task classes; NOT rescue-required.

Reference constants (MEASURED@ 2026-07-03):
  PPMI_REFERENCE_R5           = 0.906
    MEASURED@ data/exp_substrate_wikipedia_ppmi_svd_baseline_smoke_2026_07_03/metrics.json
              :per_arm_aggregate.ARM_PPMI_SVD_WIKIPEDIA.recall_at_5_mean
    (commit b655b9fd3)
  CHAR_TRIGRAM_REFERENCE_R5   = 0.854
    MEASURED@ data/exp_substrate_wikipedia_char_trigram_baseline_smoke_2026_07_03/metrics.json
              :per_arm_aggregate.ARM_CHAR_TRIGRAM_WIKIPEDIA.recall_at_5_mean
    (commit 43ec44a50)
  RANDOM_CHANCE_R5             = 5/500 = 0.01 THEORETICAL@

HP bands (per pre-reg preregs/2026-07-03_substrate_wikipedia_composed_v3_multi_arm_smoke.md):
  HP1  ARM_V3_COMPOSED_EQUAL_ALPHA.r@5           >= 0.936   (ppmi_ref + 0.03; LOAD_BEARING)
  HP2  ARM_VWFA_ALONE.r@5                        >= 0.884   (trigram_ref + 0.03; LOAD_BEARING)
  HP3  ARM_PPMI_ALONE.r@5                        in [0.901, 0.911]  (ppmi_ref +/- 0.005)
  HP4  ARM_CHAR_TRIGRAM_UNSUP_REFERENCE.r@5      in [0.853, 0.855]  (trigram_ref +/- 0.001)
  HP5  ARM_RANDOM_BASELINE.r@5                   <= 0.05     (chance sanity)
  HF1  ARM_V3_COMPOSED_EQUAL_ALPHA.r@5           < max(vwfa, ppmi) - 0.01
       (composition strictly hurts across task classes; stronger structural)
  MB-C ARM_V3_COMPOSED_EQUAL_ALPHA.r@5 in [ppmi_arm, ppmi_arm + 0.03)
       (composition helps but by less than discriminator margin; V2-A precedent)

Pre-reg: preregs/2026-07-03_substrate_wikipedia_composed_v3_multi_arm_smoke.md

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (META_RULE_AF)
- final_metrics_atomicity: tmp_replace (META_RULE_AH)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- baseline_in_band verified (META_RULE_AG; ARM_RANDOM_BASELINE r@5 ~ chance)
- HP_SCOPE per-arm declaration (in verdict logic)
- cardinality_ok (EXPECTED_N_UNITS = 5 arms x 3 seeds = 15)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ (META_RULE_AC)
- start_marker_written, crash_diagnostic_present, heartbeat_present (Sec 13)
- progress_logging: print_flush_true + line_buffered stdout (Sec 17)

Scope: SMOKE-only cell. No FULL variant. USER-locked SMOKE-only-on-local_cpu.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import sys

# Line-buffered stdout so progress lines are visible during long runs.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_wikipedia_composed_v3_multi_arm_smoke_2026_07_03"

# --- Config (mirror ppmi + trigram cells verbatim) ---
DS_SMOKE = REPO / "data" / "datasets" / "wikipedia_smoke_500.jsonl"

# MEASURED@ wc -l data/datasets/wikipedia_smoke_500.jsonl = 500.
N_ARTICLES = 500

# THEORETICAL@ 2048-dim enough for 500-way discrimination at chance = 0.01.
N_DIM = 2048

# Body char cap; matches ppmi + char-trigram cells for apples-to-apples.
BODY_CHAR_CAP = 800

# Seeds -- MUST match ppmi + trigram cells for regression comparability.
SEEDS = [11, 17, 23]

# HP band constants (per pre-reg).
# MEASURED@ data/exp_substrate_wikipedia_ppmi_svd_baseline_smoke_2026_07_03/metrics.json
#   :per_arm_aggregate.ARM_PPMI_SVD_WIKIPEDIA.recall_at_5_mean = 0.906
PPMI_REFERENCE_R5 = 0.906
# MEASURED@ data/exp_substrate_wikipedia_char_trigram_baseline_smoke_2026_07_03/metrics.json
#   :per_arm_aggregate.ARM_CHAR_TRIGRAM_WIKIPEDIA.recall_at_5_mean = 0.854
CHAR_TRIGRAM_REFERENCE_R5 = 0.854

HP_MARGIN = 0.03
HP1_COMPOSED_R5_FLOOR = PPMI_REFERENCE_R5 + HP_MARGIN            # 0.936
HP2_VWFA_R5_FLOOR = CHAR_TRIGRAM_REFERENCE_R5 + HP_MARGIN        # 0.884
# Regression bands (deterministic-fit tolerance).
HP3_PPMI_TOL = 0.005
HP3_PPMI_R5_LO = PPMI_REFERENCE_R5 - HP3_PPMI_TOL                # 0.901
HP3_PPMI_R5_HI = PPMI_REFERENCE_R5 + HP3_PPMI_TOL                # 0.911
HP4_TRIGRAM_TOL = 0.001
HP4_TRIGRAM_R5_LO = CHAR_TRIGRAM_REFERENCE_R5 - HP4_TRIGRAM_TOL  # 0.853
HP4_TRIGRAM_R5_HI = CHAR_TRIGRAM_REFERENCE_R5 + HP4_TRIGRAM_TOL  # 0.855
# THEORETICAL@ chance recall@5 = 5/500 = 0.01.
CHANCE_R5 = 5.0 / N_ARTICLES
HP5_RANDOM_R5_MAX = 0.05

# HF1 margin -- how much composition must strictly hurt vs best-single to be HF-confirming.
HF1_COMPOSED_HURT_MARGIN = 0.01

ARM_NAMES = [
    "ARM_V3_COMPOSED_EQUAL_ALPHA",
    "ARM_VWFA_ALONE",
    "ARM_PPMI_ALONE",
    "ARM_CHAR_TRIGRAM_UNSUP_REFERENCE",
    "ARM_RANDOM_BASELINE",
]


# --- Args ---
def _parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run-mode",
                    default=os.environ.get("HDLAB_RUN_MODE", None),
                    choices=[None, "self_test", "smoke", "full"])
    args, _ = ap.parse_known_args()
    if args.self_test:
        return "self_test"
    if args.smoke:
        return "smoke"
    if args.run_mode is not None:
        return args.run_mode
    # SMOKE-only cell: default to smoke.
    return "smoke"


RUN_MODE = _parse_args()
IS_SMOKE = RUN_MODE == "smoke"
IS_SELFTEST = RUN_MODE == "self_test"


# --- Deterministic in-code mini corpus for --self-test ---
_MINI_CORPUS = [
    {"title": "Alpha Star", "text": "Alpha Star is a bright celestial object. Astronomers observe alpha star regularly."},
    {"title": "Beta River", "text": "Beta River flows through the valley. Its waters are clear. Beta river supports aquatic life."},
    {"title": "Gamma Mountain", "text": "Gamma Mountain rises above the plain. Climbers ascend gamma mountain each summer."},
    {"title": "Delta Forest", "text": "Delta Forest is an ancient woodland. Delta forest is a protected reserve."},
    {"title": "Epsilon Lake", "text": "Epsilon Lake is a freshwater body. Epsilon lake attracts many birds."},
]


# --- Progress + observability helpers ---
def _log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%SZ')}] {msg}", flush=True)


def _write_start_marker(output_dir: Path, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f, indent=2)
    os.replace(tmp, final)


def _heartbeat(output_dir: Path, unit_idx: int, total_units: int, elapsed_s: float, extra: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": unit_idx,
        "total_units": total_units,
        "elapsed_s": elapsed_s,
        "extra": extra,
    }
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# --- Data loading (BIT-IDENTICAL to ppmi + trigram cells) ---
def load_articles(n: int, path: Path) -> List[Dict[str, str]]:
    """Load n articles from a jsonl file. Each line: {'title': ..., 'text': ...}."""
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {path}. "
            f"For smoke expected: data/datasets/wikipedia_smoke_500.jsonl."
        )
    out: List[Dict[str, str]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = (r.get("title") or "").strip()
            x = (r.get("text") or "").strip()
            if t and x:
                out.append({"title": t, "text": x[:BODY_CHAR_CAP]})
            if len(out) >= n:
                break
    return out


def _unit_norm(x: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + eps)


# --- Retrieval metrics (BIT-IDENTICAL to ppmi + trigram cells) ---
def _retrieval_metrics(body_hds: np.ndarray, title_hds: np.ndarray, seed: int) -> Dict[str, float]:
    """recall@k, MRR, intra/inter cos, snr; cosine similarity title-i -> body-j."""
    b = _unit_norm(body_hds.astype(np.float32))
    t = _unit_norm(title_hds.astype(np.float32))
    n = b.shape[0]
    chunk = 256
    r1 = r5 = r10 = 0
    mrr_sum = 0.0
    intra_sum = 0.0
    for i in range(0, n, chunk):
        sims = t[i:i + chunk] @ b.T
        order = np.argsort(-sims, axis=1)
        for j in range(order.shape[0]):
            gi = i + j
            intra_sum += float(sims[j, gi])
            r1 += int(order[j, 0] == gi)
            if gi in order[j, :5]:
                r5 += 1
            if gi in order[j, :10]:
                r10 += 1
            rank_arr = np.where(order[j] == gi)[0]
            if rank_arr.size > 0:
                mrr_sum += 1.0 / float(rank_arr[0] + 1)
    r1 /= n
    r5 /= n
    r10 /= n
    mrr = mrr_sum / n
    intra = intra_sum / n

    rng = np.random.default_rng(int(seed) * 991 + 7)
    perm = rng.permutation(n)
    for i in range(n):
        if perm[i] == i:
            j = (i + 1) % n
            perm[i], perm[j] = perm[j], perm[i]
    inter = float(np.mean(np.sum(t * b[perm], axis=1)))
    snr = intra / max(abs(inter), 1e-6)
    return {
        "recall_at_1": float(r1),
        "recall_at_5": float(r5),
        "recall_at_10": float(r10),
        "mean_reciprocal_rank": float(mrr),
        "intra_article_body_title_cos": float(intra),
        "inter_article_title_body_cos": float(inter),
        "signal_to_noise_ratio": float(snr),
    }


# --- Arm implementations ---

def _encode_vwfa(articles: List[Dict[str, str]], seed: int) -> Tuple[np.ndarray, np.ndarray, float]:
    """VWFA-analog multi-scale HRR-position encoder (scales=(1,2,3,4)). Deterministic w.r.t. seed."""
    from hdlab.vwfa import VWFAEncoder
    _ = seed  # deterministic; captured only for caller-loop alignment.
    enc = VWFAEncoder(
        n_dim=N_DIM,
        scales=(1, 2, 3, 4),
        bind_position=True,
        max_pos=24,
        seed_prefix="VWFA_WIKIPEDIA_v1",
        sign_bundle=True,
    )
    n = len(articles)
    body_hds = np.zeros((n, N_DIM), dtype=np.float32)
    title_hds = np.zeros((n, N_DIM), dtype=np.float32)
    t0 = time.perf_counter()
    for i, a in enumerate(articles):
        body_hds[i] = enc.encode_sentence(a["text"])
        title_hds[i] = enc.encode_sentence(a["title"])
        if (i + 1) % max(1, n // 5) == 0:
            _log(f"  [vwfa] {i+1}/{n}")
    wall = time.perf_counter() - t0
    return body_hds, title_hds, wall


def _encode_ppmi(articles: List[Dict[str, str]], seed: int) -> Tuple[np.ndarray, np.ndarray, float, float, dict]:
    """PPMI/SVD encoder (identical hyperparams to standalone ppmi cell)."""
    from hdlab.ppmi_sparse_encoder import PPMISparseEncoder
    n = len(articles)
    bodies = [a["text"] for a in articles]
    labels = np.arange(n, dtype=np.int64)
    fit_t0 = time.perf_counter()
    enc = PPMISparseEncoder(
        n_dim=N_DIM,
        min_term_freq=2,
        smoothing=0.75,
        seed=int(seed),
    )
    enc.fit(bodies, labels)
    fit_wall = time.perf_counter() - fit_t0
    _log(f"  [ppmi] fit V={len(enc.term_to_idx)} effective_dim={enc.effective_n_dim} "
         f"fit_wall={fit_wall:.2f}s")
    encode_t0 = time.perf_counter()
    body_hds = np.zeros((n, N_DIM), dtype=np.float32)
    title_hds = np.zeros((n, N_DIM), dtype=np.float32)
    title_oov_count = 0
    for i, a in enumerate(articles):
        body_hds[i] = enc.encode(a["text"])
        th = enc.encode(a["title"])
        title_hds[i] = th
        if float(np.linalg.norm(th)) < 1e-8:
            title_oov_count += 1
        if (i + 1) % max(1, n // 5) == 0:
            _log(f"  [ppmi] encode {i+1}/{n}")
    encode_wall = time.perf_counter() - encode_t0
    diag = {
        "vocab_size": int(len(enc.term_to_idx)),
        "effective_n_dim": int(enc.effective_n_dim),
        "title_oov_count": int(title_oov_count),
        "title_oov_frac": float(title_oov_count) / max(1, n),
    }
    return body_hds, title_hds, encode_wall, fit_wall, diag


def _encode_char_trigram(articles: List[Dict[str, str]], seed: int) -> Tuple[np.ndarray, np.ndarray, float]:
    """Substrate-native char-trigram bag-of-HD encoder. Deterministic hash-codebook."""
    from hdlab.char_trigram_encoder import CharTrigramEncoder
    _ = seed  # deterministic
    enc = CharTrigramEncoder(n_dim=N_DIM)
    n = len(articles)
    body_hds = np.zeros((n, N_DIM), dtype=np.float32)
    title_hds = np.zeros((n, N_DIM), dtype=np.float32)
    t0 = time.perf_counter()
    for i, a in enumerate(articles):
        body_hds[i] = enc.encode(a["text"])
        title_hds[i] = enc.encode(a["title"])
        if (i + 1) % max(1, n // 5) == 0:
            _log(f"  [trigram] {i+1}/{n}")
    wall = time.perf_counter() - t0
    return body_hds, title_hds, wall


def _encode_random(articles: List[Dict[str, str]], seed: int) -> Tuple[np.ndarray, np.ndarray, float]:
    """Random bipolar HD codebook. Independent draws body + title -> chance retrieval."""
    n = len(articles)
    rng = np.random.default_rng(int(seed) * 977 + 3)
    t0 = time.perf_counter()
    body_hds = (rng.integers(0, 2, size=(n, N_DIM)) * 2 - 1).astype(np.float32)
    title_hds = (rng.integers(0, 2, size=(n, N_DIM)) * 2 - 1).astype(np.float32)
    wall = time.perf_counter() - t0
    return body_hds, title_hds, wall


def _run_composed_arm(
    articles: List[Dict[str, str]], seed: int
) -> Tuple[Dict[str, float], float, float, dict]:
    """Composed VWFA+PPMI equal-alpha via ComposedEncoderV3.retrieve_topk.

    Fits the encoder on bodies with labels=arange(N) (each body its own concept),
    then queries with each title -> per-title top-k concept indices; computes
    r@1, r@5, r@10, MRR against gold index i.

    Returns (metrics_dict, encode_wall, fit_wall, ppmi_diag). The metrics_dict
    contains recall_at_1/5/10 and mean_reciprocal_rank (intra/inter/snr are
    unavailable at proto-retrieval layer so those are omitted).
    """
    from hdlab.composed_encoder_v3 import ComposedEncoderV3
    n = len(articles)
    bodies = [a["text"] for a in articles]
    labels = np.arange(n, dtype=np.int64)

    fit_t0 = time.perf_counter()
    enc = ComposedEncoderV3(
        n_dim=N_DIM,
        alpha=0.5,
        beta=0.5,
        vwfa_kwargs={
            "scales": (1, 2, 3, 4),
            "bind_position": True,
            "max_pos": 24,
            "seed_prefix": "VWFA_WIKIPEDIA_v1",
            "sign_bundle": True,
        },
        ppmi_kwargs={
            "min_term_freq": 2,
            "smoothing": 0.75,
            "seed": int(seed),
        },
    )
    enc.fit(bodies, labels)
    fit_wall = time.perf_counter() - fit_t0
    _log(f"  [composed] fit V={len(enc.ppmi.term_to_idx)} n_concepts={enc.n_concepts} "
         f"fit_wall={fit_wall:.2f}s")

    encode_t0 = time.perf_counter()
    r1 = r5 = r10 = 0
    mrr_sum = 0.0
    intra_sum = 0.0  # cos of title-vs-gold-body under combined-score.
    # Compute combined score against ALL prototypes per title so we can also
    # report intra (score at gold index) as an SNR-adjacent diagnostic.
    for i, a in enumerate(articles):
        top = enc.retrieve_topk(a["title"], k=10)  # int64 top-10 concept indices
        gold = i
        # r@k
        top1 = int(top[0]) if top.size > 0 else -1
        r1 += int(top1 == gold)
        top5 = set(int(x) for x in top[:5])
        top10 = set(int(x) for x in top[:10])
        if gold in top5:
            r5 += 1
        if gold in top10:
            r10 += 1
        # MRR: find rank of gold in top-10; if not in top-10 -> 0.
        rank_arr = np.where(top == gold)[0]
        if rank_arr.size > 0:
            mrr_sum += 1.0 / float(rank_arr[0] + 1)
        if (i + 1) % max(1, n // 5) == 0:
            _log(f"  [composed] retrieve {i+1}/{n}")
    encode_wall = time.perf_counter() - encode_t0

    metrics = {
        "recall_at_1": float(r1) / n,
        "recall_at_5": float(r5) / n,
        "recall_at_10": float(r10) / n,
        "mean_reciprocal_rank": float(mrr_sum) / n,
    }
    ppmi_diag = {
        "vocab_size": int(len(enc.ppmi.term_to_idx)),
        "effective_n_dim": int(enc.ppmi.effective_n_dim),
        "n_concepts": int(enc.n_concepts),
        "alpha": float(enc.alpha),
        "beta": float(enc.beta),
    }
    return metrics, encode_wall, fit_wall, ppmi_diag


# --- Arms-differ hash (META_RULE_AF) ---
def _arms_differ_hash(arms_body_hds: Dict[str, np.ndarray]) -> Dict[str, str]:
    digests: Dict[str, str] = {}
    for name, arr in arms_body_hds.items():
        sig = arr[0, :200].astype(np.float32).tobytes()
        digests[name] = hashlib.sha256(sig).hexdigest()[:16]
    names = list(digests.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if digests[a] == digests[b]:
                raise RuntimeError(
                    f"META_RULE_AF VIOLATION arms_differ: {a!r} and {b!r} bit-identical "
                    f"first-article prefix (hash={digests[a]}). Arm-implementation bug."
                )
    return digests


# --- Selftests (--self-test path) ---
def _selftest_retrieval_metrics_identity() -> None:
    n = 20
    n_dim = 128
    rng = np.random.default_rng(11)
    x = rng.standard_normal((n, n_dim)).astype(np.float32)
    m = _retrieval_metrics(x, x, seed=11)
    assert m["recall_at_1"] == 1.0, f"identity r@1={m['recall_at_1']}"
    assert m["recall_at_5"] == 1.0
    assert m["mean_reciprocal_rank"] == 1.0
    print(f"[selftest retrieval_metrics_identity] PASS r1={m['recall_at_1']}", flush=True)


def _selftest_random_chance_at_scale() -> None:
    """Random bipolar HDs at N=200 x n_dim=2048 must give r@5 <= 5x chance."""
    n = 200
    n_dim = 2048
    rng = np.random.default_rng(17)
    b = (rng.integers(0, 2, size=(n, n_dim)) * 2 - 1).astype(np.float32)
    t = (rng.integers(0, 2, size=(n, n_dim)) * 2 - 1).astype(np.float32)
    m = _retrieval_metrics(b, t, seed=17)
    chance_expected = 5.0 / n
    assert 0.0 <= m["recall_at_5"] <= chance_expected * 5, (
        f"random arm at N={n} r@5={m['recall_at_5']:.4f} outside "
        f"chance band [0, {chance_expected*5:.4f}] (chance={chance_expected:.4f})"
    )
    print(f"[selftest random_chance_at_scale] PASS -- r@5={m['recall_at_5']:.4f} "
          f"(chance={chance_expected:.4f})", flush=True)


def _selftest_composed_v3_retrieves_on_mini() -> None:
    """ComposedEncoderV3 at n_dim=2048 alpha=0.5 beta=0.5 retrieves >= 4/5 on toy corpus."""
    from hdlab.composed_encoder_v3 import ComposedEncoderV3
    sentences = [
        "cat feline pet purr whiskers",
        "cat kitten meow claws",
        "dog canine bark loyal",
        "dog puppy leash walk",
        "airplane jet wing fly sky",
        "airplane pilot cockpit turbine",
        "rose flower red petal thorn",
        "rose bloom garden fragrance",
        "guitar string chord strum music",
        "guitar acoustic pluck song",
    ]
    labels = np.array([0, 0, 1, 1, 2, 2, 3, 3, 4, 4], dtype=np.int64)
    queries = [
        (0, "feline purr claws whiskers"),
        (1, "canine bark loyal puppy"),
        (2, "aircraft pilot wing turbine"),
        (3, "flower petal bloom garden"),
        (4, "chord string strum acoustic"),
    ]
    enc = ComposedEncoderV3(
        n_dim=2048, alpha=0.5, beta=0.5,
        vwfa_kwargs={"scales": (1, 2, 3, 4), "bind_position": True,
                     "seed_prefix": "SELFTEST_V3_MINI"},
        ppmi_kwargs={"min_term_freq": 1, "smoothing": 0.75, "seed": 11},
    )
    enc.fit(sentences, labels)
    correct = sum(1 for lbl, q in queries if enc.cosine_argmax(q) == lbl)
    assert correct >= 4, (
        f"composed_v3 mini retrieval r@1={correct}/5 < 4/5; module contract broken"
    )
    print(f"[selftest composed_v3_retrieves_on_mini] PASS r@1={correct}/5", flush=True)


def _selftest_arms_differ_mini() -> None:
    """All 5 encoder body HDs on a 5-atom mini corpus must hash-differ."""
    from hdlab.char_trigram_encoder import CharTrigramEncoder
    from hdlab.ppmi_sparse_encoder import PPMISparseEncoder
    from hdlab.vwfa import VWFAEncoder
    from hdlab.composed_encoder_v3 import ComposedEncoderV3
    articles = _MINI_CORPUS
    n = len(articles)
    bodies = [a["text"] for a in articles]
    labels = np.arange(n, dtype=np.int64)
    # VWFA
    vwfa_enc = VWFAEncoder(n_dim=1024, scales=(1, 2, 3, 4), bind_position=True,
                           seed_prefix="SELFTEST_V3_MINI")
    b_vwfa = np.stack([vwfa_enc.encode_sentence(x) for x in bodies], axis=0)
    # PPMI
    ppmi_enc = PPMISparseEncoder(n_dim=1024, min_term_freq=1, seed=11)
    ppmi_enc.fit(bodies, labels)
    b_ppmi = np.stack([ppmi_enc.encode(x) for x in bodies], axis=0)
    # Char-trigram
    ct = CharTrigramEncoder(n_dim=1024)
    b_tri = np.stack([ct.encode(x) for x in bodies], axis=0)
    # Random
    rng = np.random.default_rng(11)
    b_rand = (rng.integers(0, 2, size=(n, 1024)) * 2 - 1).astype(np.float32)
    # Composed: use proto-VWFA row 0 as its "body HD" for hash-differ purposes.
    comp_enc = ComposedEncoderV3(
        n_dim=1024, alpha=0.5, beta=0.5,
        vwfa_kwargs={"scales": (1, 2, 3, 4), "bind_position": True,
                     "seed_prefix": "SELFTEST_V3_MINI_COMP"},
        ppmi_kwargs={"min_term_freq": 1, "smoothing": 0.75, "seed": 11},
    )
    comp_enc.fit(bodies, labels)
    # Prototype rows are L2-normed float32 mean of body streams; use VWFA proto.
    assert comp_enc.protos_vwfa is not None
    b_composed_proxy = comp_enc.protos_vwfa.astype(np.float32)
    arms = {
        "vwfa": b_vwfa,
        "ppmi": b_ppmi,
        "trigram": b_tri,
        "random": b_rand,
        "composed_vwfa_proto": b_composed_proxy,
    }
    for name, arr in arms.items():
        n_nan = int(np.isnan(arr).sum())
        assert n_nan == 0, f"selftest NaN in {name}: n_nan={n_nan}"
    digests = _arms_differ_hash(arms)
    assert len(set(digests.values())) == 5, f"arms_differ failed: {digests}"
    print(f"[selftest arms_differ_mini] PASS -- digests={digests}", flush=True)


def _selftest_scale_sentinel_n8192() -> None:
    """ComposedEncoderV3 at n_dim=8192 fits + encodes + retrieves >= 3/5 on toy corpus."""
    from hdlab.composed_encoder_v3 import ComposedEncoderV3
    sentences = [
        "cat feline pet purr whiskers",
        "dog canine bark loyal",
        "airplane jet wing fly sky",
        "rose flower red petal thorn",
        "guitar string chord strum music",
    ]
    labels = np.array([0, 1, 2, 3, 4], dtype=np.int64)
    queries = [
        (0, "feline whiskers"),
        (1, "canine bark loyal"),
        (2, "jet wing fly"),
        (3, "flower petal"),
        (4, "chord string strum"),
    ]
    enc = ComposedEncoderV3(
        n_dim=8192, alpha=0.5, beta=0.5,
        vwfa_kwargs={"scales": (1, 2, 3, 4), "bind_position": True,
                     "seed_prefix": "SELFTEST_V3_BIG"},
        ppmi_kwargs={"min_term_freq": 1, "smoothing": 0.75, "seed": 17},
    )
    enc.fit(sentences, labels)
    streams = enc.encode_streams("cat pet")
    assert streams["vwfa"].shape == (8192,), (
        f"scale sentinel: vwfa stream shape {streams['vwfa'].shape} != (8192,)"
    )
    assert streams["ppmi"].shape == (8192,), (
        f"scale sentinel: ppmi stream shape {streams['ppmi'].shape} != (8192,)"
    )
    # Retrieval sanity at 8192.
    correct = sum(1 for lbl, q in queries if enc.cosine_argmax(q) == lbl)
    assert correct >= 3, (
        f"scale sentinel n_dim=8192 retrieval r@1={correct}/5 < 3/5"
    )
    print(f"[selftest scale_sentinel_n8192] PASS r@1={correct}/5", flush=True)


def _selftest_arg_parse_default_is_smoke() -> None:
    old = sys.argv
    try:
        sys.argv = ["exp_substrate_wikipedia_composed_v3_multi_arm_smoke_2026-07-03"]
        mode = _parse_args()
        assert mode == "smoke", f"default mode should be 'smoke' not {mode!r}"
    finally:
        sys.argv = old
    print("[selftest arg_parse_default_is_smoke] PASS", flush=True)


def _selftest_formula_identity_alpha1_equals_vwfa_only() -> None:
    """ComposedEncoderV3(alpha=1, beta=0).retrieve_topk == pure-VWFA argmax."""
    from hdlab.composed_encoder_v3 import ComposedEncoderV3
    sentences = [
        "cat feline pet purr whiskers",
        "dog canine bark loyal",
        "airplane jet wing fly sky",
        "rose flower red petal thorn",
        "guitar string chord strum music",
    ]
    labels = np.array([0, 1, 2, 3, 4], dtype=np.int64)
    enc = ComposedEncoderV3(
        n_dim=1024, alpha=1.0, beta=0.0,
        vwfa_kwargs={"scales": (1, 2, 3, 4), "bind_position": True,
                     "seed_prefix": "SELFTEST_V3_FI"},
        ppmi_kwargs={"min_term_freq": 1, "smoothing": 0.75, "seed": 11},
    )
    enc.fit(sentences, labels)
    # Pure-VWFA argmax against protos_vwfa via cosine.
    assert enc.protos_vwfa is not None
    for lbl, qtext in [(0, "feline purr"), (2, "jet pilot"), (3, "flower petal")]:
        top_composed = enc.retrieve_topk(qtext, k=3)
        # Pure VWFA computation: encode -> L2-norm -> cosine against protos_vwfa.
        vw = enc.vwfa.encode_sentence(qtext).astype(np.float32)
        vwn = float(np.linalg.norm(vw))
        if vwn > 1e-12:
            vw = vw / vwn
        pn = np.linalg.norm(enc.protos_vwfa, axis=1)
        pn_safe = np.where(pn < 1e-12, 1.0, pn)
        scores = (enc.protos_vwfa @ vw) / pn_safe
        scores = np.where(pn < 1e-12, -1e9, scores)
        pure_top = np.argsort(-scores)[:3].astype(np.int64)
        assert np.array_equal(top_composed, pure_top), (
            f"formula identity alpha=1,beta=0 diverges from pure VWFA argmax; "
            f"composed={top_composed.tolist()} pure={pure_top.tolist()} q={qtext!r}"
        )
    print("[selftest formula_identity_alpha1_equals_vwfa_only] PASS", flush=True)


def _run_selftests() -> int:
    tests = [
        ("retrieval_metrics_identity", _selftest_retrieval_metrics_identity),
        ("random_chance_at_scale", _selftest_random_chance_at_scale),
        ("composed_v3_retrieves_on_mini", _selftest_composed_v3_retrieves_on_mini),
        ("arms_differ_mini", _selftest_arms_differ_mini),
        ("scale_sentinel_n8192", _selftest_scale_sentinel_n8192),
        ("arg_parse_default_is_smoke", _selftest_arg_parse_default_is_smoke),
        ("formula_identity_alpha1_equals_vwfa_only", _selftest_formula_identity_alpha1_equals_vwfa_only),
    ]
    failed = []
    for name, fn in tests:
        try:
            fn()
        except AssertionError as e:
            failed.append((name, f"AssertionError: {e}"))
            print(f"[selftest {name}] FAIL: {e}", flush=True)
        except Exception as e:
            failed.append((name, f"{type(e).__name__}: {e}"))
            print(f"[selftest {name}] ERROR: {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()
    print(f"[selftest summary] {len(tests) - len(failed)}/{len(tests)} passed", flush=True)
    return 0 if not failed else 1


# --- Per-seed driver ---
def _run_one_seed(seed: int, articles: List[Dict[str, str]], output_dir: Path) -> Dict:
    _log(f"[seed {seed}] starting; n_articles={len(articles)}")
    per_arm: Dict[str, Dict] = {}
    per_arm_body_hds: Dict[str, np.ndarray] = {}

    def _record_arm_metrics(arm_name: str, metrics: Dict, encoding_wall_s: float,
                             fit_wall_s: float, extra: dict, arm_idx: int, arm_t0: float) -> None:
        metrics.update({
            "arm_name": arm_name,
            "n_dim": N_DIM,
            "encoding_wall_s": float(encoding_wall_s),
            "fit_wall_s": float(fit_wall_s),
            "throughput_articles_per_sec": float(len(articles) / max(encoding_wall_s, 1e-6)),
        })
        if extra:
            metrics.update(extra)
        per_arm[arm_name] = metrics
        _log(f"[seed {seed}] arm {arm_name} r@1={metrics.get('recall_at_1', -1):.3f} "
             f"r@5={metrics.get('recall_at_5', -1):.3f} r@10={metrics.get('recall_at_10', -1):.3f} "
             f"encode_wall={encoding_wall_s:.2f}s fit_wall={fit_wall_s:.2f}s")
        _heartbeat(output_dir, arm_idx, len(ARM_NAMES),
                   time.perf_counter() - arm_t0,
                   {"arm": arm_name, "recall_at_5": metrics.get("recall_at_5", -1)})

    def _run_body_title_arm(arm_name: str, encoder_fn, arm_idx: int) -> None:
        _log(f"[seed {seed}] arm {arm_name} starting")
        arm_t0 = time.perf_counter()
        try:
            result = encoder_fn()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            failure_class = type(e).__name__
            per_arm[arm_name] = {
                "arm_name": arm_name,
                "failure_class": failure_class,
                "failure_msg": str(e)[:500],
                "traceback": traceback.format_exc()[:2000],
            }
            _log(f"[seed {seed}] arm {arm_name} FAILED: {failure_class}: {e}")
            _heartbeat(output_dir, arm_idx, len(ARM_NAMES), time.perf_counter() - arm_t0,
                       {"arm": arm_name, "status": "failed", "failure_class": failure_class})
            return
        # Unpack: PPMI returns 5-tuple with fit_wall + diag; others return 3-tuple.
        if len(result) == 5:
            body_hds, title_hds, encoding_wall_s, fit_wall_s, arm_diag = result
        else:
            body_hds, title_hds, encoding_wall_s = result
            fit_wall_s = 0.0
            arm_diag = None
        n_nan = int(np.isnan(body_hds).sum()) + int(np.isnan(title_hds).sum())
        if n_nan > 0:
            per_arm[arm_name] = {
                "arm_name": arm_name,
                "failure_class": "NAN_IN_HDS",
                "failure_msg": f"n_nan={n_nan}",
                "encoding_wall_s": encoding_wall_s,
            }
            _log(f"[seed {seed}] arm {arm_name} NaN in HDs (n_nan={n_nan})")
            return
        metrics = _retrieval_metrics(body_hds, title_hds, seed=seed)
        per_arm_body_hds[arm_name] = body_hds
        extra = {}
        if arm_diag is not None:
            extra["encoder_diag"] = arm_diag
        _record_arm_metrics(arm_name, metrics, encoding_wall_s, fit_wall_s, extra,
                             arm_idx, arm_t0)

    def _run_composed_arm_wrapped(arm_idx: int) -> None:
        arm_name = "ARM_V3_COMPOSED_EQUAL_ALPHA"
        _log(f"[seed {seed}] arm {arm_name} starting")
        arm_t0 = time.perf_counter()
        try:
            metrics, encoding_wall_s, fit_wall_s, arm_diag = _run_composed_arm(articles, seed)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            failure_class = type(e).__name__
            per_arm[arm_name] = {
                "arm_name": arm_name,
                "failure_class": failure_class,
                "failure_msg": str(e)[:500],
                "traceback": traceback.format_exc()[:2000],
            }
            _log(f"[seed {seed}] arm {arm_name} FAILED: {failure_class}: {e}")
            _heartbeat(output_dir, arm_idx, len(ARM_NAMES), time.perf_counter() - arm_t0,
                       {"arm": arm_name, "status": "failed", "failure_class": failure_class})
            return
        # Composed retrieves at score-level so we do NOT store per-arm body HDs
        # (they live in two separate codebook namespaces). Skip arms_differ for
        # the composed arm; other arms cover the arms_differ contract.
        _record_arm_metrics(arm_name, metrics, encoding_wall_s, fit_wall_s,
                             {"encoder_diag": arm_diag}, arm_idx, arm_t0)

    # Run all 5 arms.
    _run_composed_arm_wrapped(0)
    _run_body_title_arm("ARM_VWFA_ALONE", lambda: _encode_vwfa(articles, seed), 1)
    _run_body_title_arm("ARM_PPMI_ALONE", lambda: _encode_ppmi(articles, seed), 2)
    _run_body_title_arm("ARM_CHAR_TRIGRAM_UNSUP_REFERENCE",
                        lambda: _encode_char_trigram(articles, seed), 3)
    _run_body_title_arm("ARM_RANDOM_BASELINE", lambda: _encode_random(articles, seed), 4)

    arms_differ_verified = False
    arms_differ_digests: Dict[str, str] = {}
    if len(per_arm_body_hds) >= 2:
        try:
            arms_differ_digests = _arms_differ_hash(per_arm_body_hds)
            arms_differ_verified = True
        except Exception as e:
            _log(f"[seed {seed}] ARMS_DIFFER_FAIL: {e}")
            arms_differ_verified = False
            arms_differ_digests = {"error": str(e)[:200]}

    return {
        "seed": int(seed),
        "n_articles": int(len(articles)),
        "per_arm": per_arm,
        "arms_differ_verified": bool(arms_differ_verified),
        "arms_differ_digests": arms_differ_digests,
    }


# --- Aggregation + verdict ---
def _aggregate(per_seed: List[Dict]) -> Dict:
    out: Dict[str, Dict] = {}
    for arm in ARM_NAMES:
        r1s, r5s, r10s, mrrs, walls, throughputs, fits = [], [], [], [], [], [], []
        n_failed = 0
        for ps in per_seed:
            arm_m = ps.get("per_arm", {}).get(arm, {})
            if "failure_class" in arm_m:
                n_failed += 1
                continue
            r1s.append(arm_m.get("recall_at_1", 0.0))
            r5s.append(arm_m.get("recall_at_5", 0.0))
            r10s.append(arm_m.get("recall_at_10", 0.0))
            mrrs.append(arm_m.get("mean_reciprocal_rank", 0.0))
            walls.append(arm_m.get("encoding_wall_s", 0.0))
            fits.append(arm_m.get("fit_wall_s", 0.0))
            throughputs.append(arm_m.get("throughput_articles_per_sec", 0.0))
        if r5s:
            out[arm] = {
                "n_seeds_succeeded": len(r5s),
                "n_seeds_failed": n_failed,
                "recall_at_1_mean": float(np.mean(r1s)),
                "recall_at_5_mean": float(np.mean(r5s)),
                "recall_at_5_std": float(np.std(r5s)),
                "recall_at_10_mean": float(np.mean(r10s)),
                "mean_reciprocal_rank_mean": float(np.mean(mrrs)),
                "encoding_wall_s_mean": float(np.mean(walls)),
                "fit_wall_s_mean": float(np.mean(fits)),
                "throughput_articles_per_sec_mean": float(np.mean(throughputs)),
            }
        else:
            out[arm] = {
                "n_seeds_succeeded": 0,
                "n_seeds_failed": n_failed,
                "recall_at_5_mean": None,
            }
    return out


def _verdict(agg: Dict, expected_n_units: int, actual_n_units: int) -> Tuple[str, str]:
    """5-arm multi-question verdict per pre-reg HP_SCOPE."""
    composed = agg.get("ARM_V3_COMPOSED_EQUAL_ALPHA", {}).get("recall_at_5_mean")
    vwfa = agg.get("ARM_VWFA_ALONE", {}).get("recall_at_5_mean")
    ppmi = agg.get("ARM_PPMI_ALONE", {}).get("recall_at_5_mean")
    tri = agg.get("ARM_CHAR_TRIGRAM_UNSUP_REFERENCE", {}).get("recall_at_5_mean")
    rnd = agg.get("ARM_RANDOM_BASELINE", {}).get("recall_at_5_mean")

    if actual_n_units < expected_n_units:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                f"HARD_FAIL_CARDINALITY: expected {expected_n_units} unit-metrics but got "
                f"{actual_n_units}; one or more (seed, arm) units failed. See per_arm failure_class.")

    if any(m is None for m in (composed, vwfa, ppmi, tri, rnd)):
        return ("HARD_FAIL_ARM_MISSING",
                f"HARD_FAIL: one or more arms have no r@5 metric: "
                f"composed={composed} vwfa={vwfa} ppmi={ppmi} trigram={tri} random={rnd}")

    # HF baseline sanity (META_RULE_AG chance-band)
    if rnd > HP5_RANDOM_R5_MAX:
        return ("HARD_FAIL_BASELINE_OUT_OF_BAND_META_RULE_AG",
                f"HP5 baseline_in_band failed: ARM_RANDOM_BASELINE r@5={rnd:.4f} > "
                f"{HP5_RANDOM_R5_MAX:.4f} (chance={CHANCE_R5:.4f}). Implementation bug in "
                f"_retrieval_metrics or _encode_random.")

    # HF regression PPMI (dispatch untrustworthy)
    if not (HP3_PPMI_R5_LO <= ppmi <= HP3_PPMI_R5_HI):
        return ("HARD_FAIL_PPMI_REGRESSION",
                f"HP3 PPMI regression failed: ARM_PPMI_ALONE r@5={ppmi:.4f} outside "
                f"[{HP3_PPMI_R5_LO:.4f}, {HP3_PPMI_R5_HI:.4f}] "
                f"(reference {PPMI_REFERENCE_R5:.3f} +/- {HP3_PPMI_TOL:.3f}). "
                f"Standalone PPMI cell diverges here; investigate cross-cell drift. "
                f"composed={composed:.4f} vwfa={vwfa:.4f} trigram={tri:.4f} random={rnd:.4f}")

    # HF regression char-trigram (dispatch untrustworthy)
    if not (HP4_TRIGRAM_R5_LO <= tri <= HP4_TRIGRAM_R5_HI):
        return ("HARD_FAIL_TRIGRAM_REGRESSION",
                f"HP4 char-trigram regression failed: ARM_CHAR_TRIGRAM_UNSUP_REFERENCE "
                f"r@5={tri:.4f} outside [{HP4_TRIGRAM_R5_LO:.4f}, {HP4_TRIGRAM_R5_HI:.4f}] "
                f"(reference {CHAR_TRIGRAM_REFERENCE_R5:.3f} +/- {HP4_TRIGRAM_TOL:.3f}). "
                f"Deterministic hash-codebook should reproduce cross-cell. "
                f"composed={composed:.4f} vwfa={vwfa:.4f} ppmi={ppmi:.4f} random={rnd:.4f}")

    best_single = max(vwfa, ppmi)

    # HF1: composition strictly hurts (structural finding across task classes)
    if composed < best_single - HF1_COMPOSED_HURT_MARGIN:
        return ("HARD_FAIL_COMPOSITION_HURTS_ACROSS_TASK_CLASSES",
                f"HF1 composition dilutes across task classes: ARM_V3_COMPOSED_EQUAL_ALPHA "
                f"r@5={composed:.4f} < max(vwfa={vwfa:.4f}, ppmi={ppmi:.4f}) - {HF1_COMPOSED_HURT_MARGIN:.3f} = "
                f"{best_single - HF1_COMPOSED_HURT_MARGIN:.4f}. Combined with WordNet dilution "
                f"finding (v3-composed WordNet SMOKE HF, commit cc1807726), this suggests "
                f"equal-alpha late-combine is task-class insufficient; asymmetric-strength streams "
                f"dilute. STRUCTURAL FINDING; NOT rescue-required. "
                f"trigram={tri:.4f} random={rnd:.4f} "
                f"composed - best_single = {composed - best_single:+.4f}")

    # HP1: composition earns keep by discriminator margin
    hp2_vwfa_pass = vwfa >= HP2_VWFA_R5_FLOOR
    hp1_composed_pass = composed >= HP1_COMPOSED_R5_FLOOR

    if hp1_composed_pass:
        return ("HARD_PASS",
                f"HARD_PASS: substrate-native brain-analog COMPOSITION earns its keep on multi-token "
                f"Wikipedia. ARM_V3_COMPOSED_EQUAL_ALPHA r@5={composed:.4f} >= {HP1_COMPOSED_R5_FLOOR:.4f} "
                f"= PPMI_ref ({PPMI_REFERENCE_R5:.3f}) + discriminator margin ({HP_MARGIN:.2f}). "
                f"Q1 YES: composed earns keep. Q2 vwfa r@5={vwfa:.4f} "
                f"({'YES' if hp2_vwfa_pass else 'NO'} HP2 floor={HP2_VWFA_R5_FLOOR:.4f}). "
                f"Q3 ppmi r@5={ppmi:.4f} in reg band [{HP3_PPMI_R5_LO:.4f}, {HP3_PPMI_R5_HI:.4f}] "
                f"(reproduce OK). Q4 trigram r@5={tri:.4f} in reg band "
                f"[{HP4_TRIGRAM_R5_LO:.4f}, {HP4_TRIGRAM_R5_HI:.4f}] (reproduce OK). "
                f"HONEST SCOPE: MECHANISM_LIFT on SUPERVISED corpus-as-labeled-partition regime; "
                f"NOT substrate general-knowledge of Wikipedia. Discriminator-narrows-at-scale "
                f"caveat: V2-A precedent smoke +0.06 -> FULL +0.012. random={rnd:.4f} "
                f"composed - best_single = {composed - best_single:+.4f}")

    # MIDDLE_BAND: composed >= best_single but under discriminator margin.
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: ARM_V3_COMPOSED_EQUAL_ALPHA r@5={composed:.4f} in "
            f"[best_single ({best_single:.4f}), HP1_floor ({HP1_COMPOSED_R5_FLOOR:.4f})). "
            f"Composition helps but by less than discriminator margin ({HP_MARGIN:.2f}). "
            f"V2-A precedent (smoke +0.06 -> FULL +0.012) suggests any smoke lift would "
            f"narrow at scale; MB here is the honest read. "
            f"Q2 vwfa r@5={vwfa:.4f} ({'HP2 PASS' if vwfa >= HP2_VWFA_R5_FLOOR else 'HP2 miss'} "
            f"floor={HP2_VWFA_R5_FLOOR:.4f}). "
            f"Q3 ppmi r@5={ppmi:.4f} (reg OK). Q4 trigram r@5={tri:.4f} (reg OK). "
            f"composed - best_single = {composed - best_single:+.4f} "
            f"random={rnd:.4f}")


# --- main ---
def main() -> int:
    if IS_SELFTEST:
        rc = _run_selftests()
        sys.exit(rc)

    output_dir = get_output_dir(ANCHOR_NAME)
    output_dir.mkdir(parents=True, exist_ok=True)

    expected_n_units = len(SEEDS) * len(ARM_NAMES)  # 3 x 5 = 15
    _write_start_marker(output_dir, expected_n_units)

    _log(f"[config] anchor={ANCHOR_NAME}")
    _log(f"[config] run_mode={RUN_MODE} n_articles={N_ARTICLES} seeds={SEEDS} n_dim={N_DIM}")
    _log(f"[config] arms={ARM_NAMES}")
    _log(f"[config] dataset_path={DS_SMOKE}")
    _log(f"[config] HP1_COMPOSED_R5_FLOOR={HP1_COMPOSED_R5_FLOOR:.4f} "
         f"HP2_VWFA_R5_FLOOR={HP2_VWFA_R5_FLOOR:.4f}")
    _log(f"[config] HP3_PPMI_R5_BAND=[{HP3_PPMI_R5_LO:.4f}, {HP3_PPMI_R5_HI:.4f}] "
         f"HP4_TRIGRAM_R5_BAND=[{HP4_TRIGRAM_R5_LO:.4f}, {HP4_TRIGRAM_R5_HI:.4f}]")

    if not DS_SMOKE.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DS_SMOKE}. Expected pre-existing "
            f"data/datasets/wikipedia_smoke_500.jsonl on local disk."
        )

    t0 = time.perf_counter()
    articles = load_articles(N_ARTICLES, DS_SMOKE)
    _log(f"[load] loaded {len(articles)} articles in {time.perf_counter() - t0:.2f}s")
    if len(articles) < N_ARTICLES:
        _log(f"[warn] loaded fewer articles than requested: {len(articles)} < {N_ARTICLES}")

    per_seed: List[Dict] = []
    for seed in SEEDS:
        seed_t0 = time.perf_counter()
        ps = _run_one_seed(seed, articles, output_dir)
        ps["seed_elapsed_s"] = float(time.perf_counter() - seed_t0)
        per_seed.append(ps)

    agg = _aggregate(per_seed)
    actual_n_units = sum(
        1
        for ps in per_seed
        for arm_m in ps.get("per_arm", {}).values()
        if "failure_class" not in arm_m
    )
    verdict, verdict_msg = _verdict(agg, expected_n_units, actual_n_units)
    _log(f"[VERDICT] {verdict}")
    _log(f"[VERDICT_MSG] {verdict_msg}")

    total_elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "seeds": SEEDS,
        "n_articles": len(articles),
        "n_articles_configured": N_ARTICLES,
        "n_dim": N_DIM,
        "body_char_cap": BODY_CHAR_CAP,
        "expected_n_units": expected_n_units,
        "actual_n_units": actual_n_units,
        "cardinality_ok": actual_n_units >= expected_n_units,
        "arms_differ_verified": all(ps.get("arms_differ_verified", False) for ps in per_seed),
        "ppmi_reference_r5_MEASURED": PPMI_REFERENCE_R5,
        "char_trigram_reference_r5_MEASURED": CHAR_TRIGRAM_REFERENCE_R5,
        "hp_margin": HP_MARGIN,
        "hp1_composed_r5_floor": HP1_COMPOSED_R5_FLOOR,
        "hp2_vwfa_r5_floor": HP2_VWFA_R5_FLOOR,
        "hp3_ppmi_r5_band": [HP3_PPMI_R5_LO, HP3_PPMI_R5_HI],
        "hp4_trigram_r5_band": [HP4_TRIGRAM_R5_LO, HP4_TRIGRAM_R5_HI],
        "hp5_random_r5_max": HP5_RANDOM_R5_MAX,
        "hf1_composed_hurt_margin": HF1_COMPOSED_HURT_MARGIN,
        "baseline_in_band_check": {
            "arm": "ARM_RANDOM_BASELINE",
            "chance_r5": CHANCE_R5,
            "band_max_r5": HP5_RANDOM_R5_MAX,
            "observed_r5_mean": agg.get("ARM_RANDOM_BASELINE", {}).get("recall_at_5_mean"),
            "in_band": (agg.get("ARM_RANDOM_BASELINE", {}).get("recall_at_5_mean") or 0.0) <= HP5_RANDOM_R5_MAX,
        },
        "final_metrics_atomicity": "tmp_replace",
        "hp_scope": {
            "HP1_LOAD_BEARING": ["ARM_V3_COMPOSED_EQUAL_ALPHA"],
            "HP2_LOAD_BEARING": ["ARM_VWFA_ALONE"],
            "HP3_REGRESSION_PPMI": ["ARM_PPMI_ALONE"],
            "HP4_REGRESSION_TRIGRAM": ["ARM_CHAR_TRIGRAM_UNSUP_REFERENCE"],
            "HP5_baseline_in_band": ["ARM_RANDOM_BASELINE"],
            "HF1_COMPOSITION_HURTS": ["ARM_V3_COMPOSED_EQUAL_ALPHA"],
        },
        "per_seed": per_seed,
        "per_arm_aggregate": agg,
        "elapsed_s": total_elapsed,
        "ts_iso_end": datetime.now(timezone.utc).isoformat(),
    }

    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)
    _log(f"[metrics] written to {final} (elapsed={total_elapsed:.2f}s)")

    write_metrics(output_dir, metrics)
    return 0


if __name__ == "__main__":
    _output_dir_for_crash = get_output_dir(ANCHOR_NAME)
    try:
        rc = main()
        sys.exit(rc or 0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_output_dir_for_crash, e)
        raise
