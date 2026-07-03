"""exp_substrate_wikipedia_ppmi_svd_baseline_smoke_2026_07_03

USER-directed 2026-07-03: substrate-native PPMI/SVD Wikipedia retrieval SMOKE
(parallel-probe to char-trigram HP r@5=0.854 MEASURED@ 2026-07-03).

Arms:
  ARM_PPMI_SVD_WIKIPEDIA        -- hdlab.ppmi_sparse_encoder.PPMISparseEncoder
                                    (ATL-hub analog; PPMI + SVD on body-as-labeled-corpus)
                                    LOAD_BEARING
  ARM_CHAR_TRIGRAM_WIKIPEDIA     -- hdlab.char_trigram_encoder.CharTrigramEncoder
                                    REGRESSION CHECK; must reproduce r@5 ~ 0.854
  ARM_RANDOM_BASELINE            -- random bipolar HDs (chance floor)

Question: does ATL-hub-analog PPMI/SVD alone BEAT the surface char-trigram bag
(r@5=0.854 MEASURED) on real Wikipedia title -> body retrieval?

FRAMING DISCIPLINE (LOAD-BEARING per USER 2026-07-02):
- Substrate has no general knowledge ingested. PPMI is a MECHANISM PROBE on
  SUPERVISED corpus-as-labeled-partition regime.
- HP here = "PPMI mechanism-lift on this SUPERVISED regime at this smoke scale."
  It does NOT mean "substrate understands Wikipedia."
- MECHANISM ANALOG != TASK ANALOG (feedback_mechanism_analog_is_not_task_analog...
  supervised_synthetic_corpus_is_supervised_regime_USER_LOCKED_2026-07-02.md).
- PPMI/SVD is ATL-hub analog for amodal semantic co-occurrence (Levy/Goldberg 2015).

Reference constants (MEASURED@ commit a71920bbf 2026-07-03):
  char_trigram_r5 = 0.854
  random_r5 = 0.0073 (chance = 5/500 = 0.01)

HP bands (per pre-reg):
  HP1  ARM_PPMI_SVD_WIKIPEDIA r@5 >= 0.884   (char_trigram + 0.03; LOAD_BEARING)
  HPreg ARM_CHAR_TRIGRAM_WIKIPEDIA r@5 in [0.804, 0.904]  (regression check)
  HF1  ARM_PPMI_SVD_WIKIPEDIA r@5 < 0.824    (PPMI loses to trigram)
  HF2  ARM_RANDOM_BASELINE r@5 > 0.05        (META_RULE_AG baseline_in_band)
  MB   ARM_PPMI_SVD_WIKIPEDIA r@5 in [0.824, 0.884)  (within +/- 0.03)

Pre-reg: preregs/2026-07-03_substrate_wikipedia_ppmi_svd_baseline_smoke.md

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (META_RULE_AF)
- final_metrics_atomicity: tmp_replace (META_RULE_AH)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- baseline_in_band verified (META_RULE_AG; ARM_RANDOM_BASELINE r@5 ~ chance)
- HP_SCOPE per-arm declaration (in verdict logic)
- cardinality_ok (EXPECTED_N_UNITS = n_seeds x n_arms = 9)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@ (META_RULE_AC)
- start_marker_written, crash_diagnostic_present, heartbeat_present (Sec 13)

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

ANCHOR_NAME = "substrate_wikipedia_ppmi_svd_baseline_smoke_2026_07_03"

# --- Config ---
DS_SMOKE = REPO / "data" / "datasets" / "wikipedia_smoke_500.jsonl"

# THEORETICAL@ 500 articles at N_DIM=2048; effective PPMI SVD dim <= min(V, C, n_dim)
# = min(V, 500, 2048) = 500, right-zero-padded to 2048.
N_DIM = 2048

# Article corpus size. MEASURED@ wc -l data/datasets/wikipedia_smoke_500.jsonl = 500.
N_ARTICLES = 500

# Body char cap; matches char-trigram cell for apples-to-apples.
BODY_CHAR_CAP = 800

# Seeds. PPMI fit + char-trigram are deterministic across seeds; only random
# arm depends on seed. Running 3 seeds for interface parity + random-arm std.
SEEDS = [11, 17, 23]

# HP band constants (per pre-reg).
# MEASURED@ data/exp_substrate_wikipedia_char_trigram_baseline_smoke_2026_07_03/
#   metrics.json:per_arm_aggregate.ARM_CHAR_TRIGRAM_WIKIPEDIA.recall_at_5_mean = 0.854
CHAR_TRIGRAM_REFERENCE_R5 = 0.854
HP_MARGIN = 0.03
HP_PPMI_R5_FLOOR = CHAR_TRIGRAM_REFERENCE_R5 + HP_MARGIN  # 0.884
HF_PPMI_R5_HARD_FLOOR = CHAR_TRIGRAM_REFERENCE_R5 - HP_MARGIN  # 0.824
# Regression check: trigram arm within +/- 0.05 of MEASURED reference.
REG_TRIGRAM_TOL = 0.05
REG_TRIGRAM_LO = CHAR_TRIGRAM_REFERENCE_R5 - REG_TRIGRAM_TOL  # 0.804
REG_TRIGRAM_HI = CHAR_TRIGRAM_REFERENCE_R5 + REG_TRIGRAM_TOL  # 0.904
# THEORETICAL@ chance recall@5 = 5/500 = 0.01.
CHANCE_R5 = 5.0 / N_ARTICLES
# Random baseline sanity band.
BASELINE_IN_BAND_R5_MAX = 0.05


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
    # SMOKE-only cell: default to smoke to prevent accidental "full" invocations.
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


# --- Data loading (BIT-IDENTICAL to char-trigram cell) ---
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


# --- Arm implementations ---

def _encode_ppmi_svd(articles: List[Dict[str, str]], seed: int) -> Tuple[np.ndarray, np.ndarray, float, float, dict]:
    """PPMI/SVD encoder fit on body-as-labeled-corpus, encode both body + title."""
    from hdlab.ppmi_sparse_encoder import PPMISparseEncoder
    n = len(articles)
    bodies = [a["text"] for a in articles]
    labels = np.arange(n, dtype=np.int64)  # concept_label = article index
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
    """Substrate-native char-trigram bag-of-HD encoder. Deterministic w.r.t. seed."""
    from hdlab.char_trigram_encoder import CharTrigramEncoder
    _ = seed  # deterministic; captured only for caller loop alignment
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


def _encode_random_baseline(articles: List[Dict[str, str]], seed: int) -> Tuple[np.ndarray, np.ndarray, float]:
    """Random bipolar HD codebook. Independent draws for body + title -> chance retrieval."""
    n = len(articles)
    rng = np.random.default_rng(int(seed) * 977 + 3)
    t0 = time.perf_counter()
    body_hds = (rng.integers(0, 2, size=(n, N_DIM)) * 2 - 1).astype(np.float32)
    title_hds = (rng.integers(0, 2, size=(n, N_DIM)) * 2 - 1).astype(np.float32)
    wall = time.perf_counter() - t0
    return body_hds, title_hds, wall


# --- Retrieval metrics (BIT-IDENTICAL to char-trigram cell) ---
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
    """Random bipolar HDs at N=200 x n_dim=2048 must give r@5 near 5/200 = 0.025."""
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


def _selftest_ppmi_encoder_fits_mini_corpus() -> None:
    """Fit PPMI encoder on 5-atom mini corpus; verify vocab + retrieval sanity."""
    from hdlab.ppmi_sparse_encoder import PPMISparseEncoder
    articles = _MINI_CORPUS
    n = len(articles)
    bodies = [a["text"] for a in articles]
    labels = np.arange(n, dtype=np.int64)
    enc = PPMISparseEncoder(n_dim=64, min_term_freq=1, seed=11)
    enc.fit(bodies, labels)
    assert enc.term_embeddings is not None, "PPMI fit produced no term_embeddings"
    assert enc.effective_n_dim <= n, f"effective_dim {enc.effective_n_dim} > n={n}"
    # Encode all bodies + titles.
    body_hds = np.zeros((n, 64), dtype=np.float32)
    title_hds = np.zeros((n, 64), dtype=np.float32)
    for i, a in enumerate(articles):
        body_hds[i] = enc.encode(a["text"])
        title_hds[i] = enc.encode(a["title"])
    # Titles like "Alpha Star" have trigram overlap with body ("alpha star" appears
    # in body text repeatedly); expect at least 3/5 titles find their body in top-3.
    m = _retrieval_metrics(body_hds, title_hds, seed=11)
    assert m["recall_at_5"] >= 0.6, (
        f"PPMI mini r@5={m['recall_at_5']:.3f} < 0.6; encoder may be broken on trivial corpus"
    )
    print(f"[selftest ppmi_encoder_fits_mini_corpus] PASS "
          f"V={len(enc.term_to_idx)} effective_dim={enc.effective_n_dim} "
          f"r@5={m['recall_at_5']:.3f}", flush=True)


def _selftest_arms_differ_mini() -> None:
    """PPMI + char-trigram + random body HDs on mini corpus must hash-differ."""
    from hdlab.char_trigram_encoder import CharTrigramEncoder
    from hdlab.ppmi_sparse_encoder import PPMISparseEncoder
    articles = _MINI_CORPUS
    n = len(articles)
    # PPMI
    ppmi_enc = PPMISparseEncoder(n_dim=1024, min_term_freq=1, seed=11)
    ppmi_enc.fit([a["text"] for a in articles], np.arange(n, dtype=np.int64))
    b_ppmi = np.stack([ppmi_enc.encode(a["text"]) for a in articles], axis=0)
    # Char-trigram
    ct = CharTrigramEncoder(n_dim=1024)
    b_tri = np.stack([ct.encode(a["text"]) for a in articles], axis=0)
    # Random
    rng = np.random.default_rng(11)
    b_rand = (rng.integers(0, 2, size=(n, 1024)) * 2 - 1).astype(np.float32)
    arms = {"ppmi": b_ppmi, "trigram": b_tri, "random": b_rand}
    for name, arr in arms.items():
        n_nan = int(np.isnan(arr).sum())
        assert n_nan == 0, f"selftest NaN in {name}: n_nan={n_nan}"
    digests = _arms_differ_hash(arms)
    assert len(set(digests.values())) == 3, f"arms_differ failed: {digests}"
    print(f"[selftest arms_differ_mini] PASS -- digests={digests}", flush=True)


def _selftest_arg_parse_default_is_smoke() -> None:
    old = sys.argv
    try:
        sys.argv = ["exp_substrate_wikipedia_ppmi_svd_baseline_smoke_2026-07-03"]
        mode = _parse_args()
        assert mode == "smoke", f"default mode should be 'smoke' not {mode!r}"
    finally:
        sys.argv = old
    print("[selftest arg_parse_default_is_smoke] PASS", flush=True)


def _run_selftests() -> int:
    tests = [
        ("retrieval_metrics_identity", _selftest_retrieval_metrics_identity),
        ("random_chance_at_scale", _selftest_random_chance_at_scale),
        ("ppmi_encoder_fits_mini_corpus", _selftest_ppmi_encoder_fits_mini_corpus),
        ("arms_differ_mini", _selftest_arms_differ_mini),
        ("arg_parse_default_is_smoke", _selftest_arg_parse_default_is_smoke),
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

    def _run_arm(arm_name: str, encoder_fn, arm_idx: int) -> None:
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
            _heartbeat(output_dir, arm_idx, 3, time.perf_counter() - arm_t0,
                       {"arm": arm_name, "status": "failed", "failure_class": failure_class})
            return
        # Result unpacking: PPMI returns (body, title, encode_wall, fit_wall, diag);
        # others return (body, title, wall).
        if len(result) == 5:
            body_hds, title_hds, encoding_wall_s, fit_wall_s, ppmi_diag = result
        else:
            body_hds, title_hds, encoding_wall_s = result
            fit_wall_s = 0.0
            ppmi_diag = None
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
        metrics.update({
            "arm_name": arm_name,
            "n_dim": int(body_hds.shape[1]),
            "encoding_wall_s": float(encoding_wall_s),
            "fit_wall_s": float(fit_wall_s),
            "throughput_articles_per_sec": float(len(articles) / max(encoding_wall_s, 1e-6)),
        })
        if ppmi_diag is not None:
            metrics["ppmi_diag"] = ppmi_diag
        per_arm[arm_name] = metrics
        per_arm_body_hds[arm_name] = body_hds
        _log(f"[seed {seed}] arm {arm_name} r@1={metrics['recall_at_1']:.3f} "
             f"r@5={metrics['recall_at_5']:.3f} r@10={metrics['recall_at_10']:.3f} "
             f"intra={metrics['intra_article_body_title_cos']:.3f} "
             f"inter={metrics['inter_article_title_body_cos']:.3f} "
             f"encode_wall={encoding_wall_s:.2f}s fit_wall={fit_wall_s:.2f}s")
        _heartbeat(output_dir, arm_idx, 3, time.perf_counter() - arm_t0,
                   {"arm": arm_name, "recall_at_5": metrics["recall_at_5"]})

    _run_arm("ARM_PPMI_SVD_WIKIPEDIA", lambda: _encode_ppmi_svd(articles, seed), 0)
    _run_arm("ARM_CHAR_TRIGRAM_WIKIPEDIA", lambda: _encode_char_trigram(articles, seed), 1)
    _run_arm("ARM_RANDOM_BASELINE", lambda: _encode_random_baseline(articles, seed), 2)

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
    arm_names = ["ARM_PPMI_SVD_WIKIPEDIA", "ARM_CHAR_TRIGRAM_WIKIPEDIA", "ARM_RANDOM_BASELINE"]
    out: Dict[str, Dict] = {}
    for arm in arm_names:
        r1s, r5s, r10s, walls, throughputs, fits = [], [], [], [], [], []
        n_failed = 0
        for ps in per_seed:
            arm_m = ps.get("per_arm", {}).get(arm, {})
            if "failure_class" in arm_m:
                n_failed += 1
                continue
            r1s.append(arm_m.get("recall_at_1", 0.0))
            r5s.append(arm_m.get("recall_at_5", 0.0))
            r10s.append(arm_m.get("recall_at_10", 0.0))
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
    """HP_SCOPE per pre-reg:
    HP1 (PPMI r@5 >= 0.884): LOAD_BEARING on ARM_PPMI_SVD_WIKIPEDIA
    HPreg (trigram r@5 in [0.804, 0.904]): REGRESSION on ARM_CHAR_TRIGRAM_WIKIPEDIA
    HF1 (PPMI r@5 < 0.824): PPMI-alone loses to surface bag
    HF2 (random out of chance band): implementation bug
    HFreg (trigram out of reg band): dispatch untrustworthy
    """
    ppmi = agg.get("ARM_PPMI_SVD_WIKIPEDIA", {}).get("recall_at_5_mean")
    tri = agg.get("ARM_CHAR_TRIGRAM_WIKIPEDIA", {}).get("recall_at_5_mean")
    rnd = agg.get("ARM_RANDOM_BASELINE", {}).get("recall_at_5_mean")

    if actual_n_units < expected_n_units:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                f"HARD_FAIL_CARDINALITY: expected {expected_n_units} unit-metrics but got {actual_n_units}; "
                f"one or more (seed, arm) units failed. See per-seed per_arm failure_class.")

    if ppmi is None or tri is None or rnd is None:
        return ("HARD_FAIL_ARM_MISSING",
                f"HARD_FAIL: one or more arms have no r@5 metric: ppmi={ppmi} trigram={tri} random={rnd}")

    # HF2: random arm sanity (META_RULE_AG baseline_in_band)
    if rnd > BASELINE_IN_BAND_R5_MAX:
        return ("HARD_FAIL_BASELINE_OUT_OF_BAND_META_RULE_AG",
                f"HF2 baseline_in_band failed: ARM_RANDOM_BASELINE r@5={rnd:.4f} > "
                f"{BASELINE_IN_BAND_R5_MAX:.4f} (chance={CHANCE_R5:.4f}). "
                f"Implementation bug in _retrieval_metrics or _encode_random_baseline. "
                f"ppmi r@5={ppmi:.4f} trigram r@5={tri:.4f}")

    # HFreg: regression check on trigram arm
    if not (REG_TRIGRAM_LO <= tri <= REG_TRIGRAM_HI):
        return ("HARD_FAIL_TRIGRAM_REGRESSION",
                f"HFreg regression failed: ARM_CHAR_TRIGRAM_WIKIPEDIA r@5={tri:.4f} outside "
                f"[{REG_TRIGRAM_LO:.3f}, {REG_TRIGRAM_HI:.3f}] "
                f"(MEASURED reference {CHAR_TRIGRAM_REFERENCE_R5:.3f}). "
                f"Dispatch untrustworthy; investigate cell drift vs char-trigram cell. "
                f"ppmi r@5={ppmi:.4f} random r@5={rnd:.4f}")

    # HF1: PPMI floor
    if ppmi < HF_PPMI_R5_HARD_FLOOR:
        return ("HARD_FAIL_MECHANISM_LOSES",
                f"HF1 ARM_PPMI_SVD_WIKIPEDIA r@5={ppmi:.4f} < {HF_PPMI_R5_HARD_FLOOR:.4f} "
                f"(char_trigram_ref {CHAR_TRIGRAM_REFERENCE_R5:.3f} - {HP_MARGIN:.2f}). "
                f"PPMI-alone LOSES to surface char-trigram bag on real Wikipedia "
                f"title-body retrieval at N=500. ATL-hub-analog semantics does NOT "
                f"add signal above VWFA-analog surface bag on this task class. "
                f"Signal: v3-composed VWFA+PPMI late-combine or Spoke 3 hippocampal "
                f"consolidation is LOAD_BEARING for substrate-native Wikipedia ingest. "
                f"trigram r@5={tri:.4f} random r@5={rnd:.4f}")

    # HP: PPMI beats char-trigram by margin
    if ppmi >= HP_PPMI_R5_FLOOR:
        return ("HARD_PASS",
                f"HARD_PASS: substrate-native ATL-hub-analog PPMI/SVD encoder reaches "
                f"r@5={ppmi:.4f} >= {HP_PPMI_R5_FLOOR:.4f} = char_trigram_ref "
                f"({CHAR_TRIGRAM_REFERENCE_R5:.3f}) + {HP_MARGIN:.2f} on N={N_ARTICLES} real "
                f"Wikipedia articles at N_DIM={N_DIM}. HONEST SCOPE: MECHANISM_LIFT on "
                f"SUPERVISED corpus-as-labeled-partition regime; does NOT grant substrate "
                f"general-knowledge of Wikipedia content. PPMI mechanism (Levy/Goldberg "
                f"2015 co-occurrence + SVD) adds signal ABOVE surface trigram bag on "
                f"multi-token real-corpus retrieval. trigram r@5={tri:.4f} (regression OK). "
                f"random r@5={rnd:.4f} (chance={CHANCE_R5:.4f}). "
                f"PPMI - trigram delta = {ppmi - tri:+.4f}")

    # MIDDLE_BAND
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: ARM_PPMI_SVD_WIKIPEDIA r@5={ppmi:.4f} in "
            f"[{HF_PPMI_R5_HARD_FLOOR:.4f}, {HP_PPMI_R5_FLOOR:.4f}). Within +/- {HP_MARGIN:.2f} "
            f"of char_trigram reference ({CHAR_TRIGRAM_REFERENCE_R5:.3f}). Neither clear lift "
            f"nor clear loss. At N=500 Wikipedia the surface bag already captures most of "
            f"the mechanism's headroom; composition may be genuinely needed for lift. "
            f"PPMI - trigram delta = {ppmi - tri:+.4f}. "
            f"trigram r@5={tri:.4f} (regression OK) random r@5={rnd:.4f} (chance={CHANCE_R5:.4f})")


# --- main ---
def main() -> int:
    if IS_SELFTEST:
        rc = _run_selftests()
        sys.exit(rc)

    output_dir = get_output_dir(ANCHOR_NAME)
    output_dir.mkdir(parents=True, exist_ok=True)

    expected_n_units = len(SEEDS) * 3  # 3 arms
    _write_start_marker(output_dir, expected_n_units)

    _log(f"[config] anchor={ANCHOR_NAME}")
    _log(f"[config] run_mode={RUN_MODE} n_articles={N_ARTICLES} seeds={SEEDS} n_dim={N_DIM}")
    _log(f"[config] dataset_path={DS_SMOKE}")
    _log(f"[config] HP_PPMI_R5_FLOOR={HP_PPMI_R5_FLOOR:.4f} "
         f"HF_PPMI_R5_HARD_FLOOR={HF_PPMI_R5_HARD_FLOOR:.4f} "
         f"(char_trigram_ref={CHAR_TRIGRAM_REFERENCE_R5:.3f} +/- {HP_MARGIN:.2f})")

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
        "char_trigram_reference_r5_MEASURED": CHAR_TRIGRAM_REFERENCE_R5,
        "hp_margin": HP_MARGIN,
        "hp_ppmi_r5_floor": HP_PPMI_R5_FLOOR,
        "hf_ppmi_r5_hard_floor": HF_PPMI_R5_HARD_FLOOR,
        "reg_trigram_band": [REG_TRIGRAM_LO, REG_TRIGRAM_HI],
        "baseline_in_band_check": {
            "arm": "ARM_RANDOM_BASELINE",
            "chance_r5": CHANCE_R5,
            "band_max_r5": BASELINE_IN_BAND_R5_MAX,
            "observed_r5_mean": agg.get("ARM_RANDOM_BASELINE", {}).get("recall_at_5_mean"),
            "in_band": (agg.get("ARM_RANDOM_BASELINE", {}).get("recall_at_5_mean") or 0.0) <= BASELINE_IN_BAND_R5_MAX,
        },
        "final_metrics_atomicity": "tmp_replace",
        "hp_scope": {
            "HP1_LOAD_BEARING": ["ARM_PPMI_SVD_WIKIPEDIA"],
            "HPreg_REGRESSION": ["ARM_CHAR_TRIGRAM_WIKIPEDIA"],
            "HF1_LOAD_BEARING": ["ARM_PPMI_SVD_WIKIPEDIA"],
            "HF2_baseline_in_band": ["ARM_RANDOM_BASELINE"],
            "HFreg_regression": ["ARM_CHAR_TRIGRAM_WIKIPEDIA"],
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
