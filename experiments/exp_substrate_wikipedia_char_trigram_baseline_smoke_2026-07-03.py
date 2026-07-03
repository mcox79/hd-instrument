"""exp_substrate_wikipedia_char_trigram_baseline_smoke_2026_07_03

USER-directed 2026-07-03: substrate-native Wikipedia retrieval floor-check.

Fork of the wikipedia_ingest infra (bge-large) with a SUBSTRATE-NATIVE surface
encoder in place of the borrowed bge transformer. bge is NEVER a substrate
primitive; this cell asks what a non-bge substrate ingest can do at real-corpus
scale using the simplest brain-analog surface reader available.

Arms:
  ARM_CHAR_TRIGRAM_WIKIPEDIA  -- hdlab.char_trigram_encoder.CharTrigramEncoder
                                 (bag-of-char-trigrams; VWFA-analog surface reader)
  ARM_RANDOM_BASELINE          -- random bipolar HDs (chance floor; per-seed)

Question: does a substrate-native surface encoder reach non-trivial
title->article retrieval on real Wikipedia, or does the task require
brain-analog composition (VWFA + ATL + Spoke 3 hippocampal consolidation)?

FRAMING DISCIPLINE (LOAD-BEARING):
- Substrate has no general knowledge ingested (feedback_substrate_knows_almost_
  nothing_no_general_knowledge_ingest_yet_USER_LOCKED_REPEATED_2026-07-02.md).
- Char-trigram bag is a MECHANISM PROBE, not a capability claim. HP here means
  "substrate-native surface encoder can partially retrieve real Wikipedia
  articles"; it does NOT mean the substrate understands Wikipedia
  (feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_corpus_is_
  supervised_regime_USER_LOCKED_2026-07-02.md).
- bge reference is a FLOOR-CHECK number, not a fair-contest target: if char-
  trigram alone approaches bge, the task is bag-favorable (title-word-overlap
  dominates) and doesn't need a fancy encoder; if it falls far short, brain-
  analog composition (VWFA + ATL + Spoke 3) is genuinely load-bearing.

PRIOR HP baseline (bge-large, 100K articles, 2026-06-19):
  recall@1=0.961 recall@5=0.992
    MEASURED@data/exp_wikipedia_ingest_100k_gpu_v1/metrics.json
  (Reference target only; do not run bge in this cell.)

Pre-reg: preregs/2026-07-03_substrate_wikipedia_char_trigram_baseline_smoke.md

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (META_RULE_AF)
- final_metrics_atomicity: tmp_replace (META_RULE_AH)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- baseline_in_band verified (META_RULE_AG; ARM_RANDOM_BASELINE r@5 ~ 5/N chance)
- discriminator survives scale: char-trigram encodes N=500 x 2048-dim in-process
- HP_SCOPE per-arm declaration (in verdict logic)
- cardinality_ok for arms cell (EXPECTED_N_UNITS = n_seeds x n_arms)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- all numbers in cell comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@ (META_RULE_AC)
- start_marker_written, crash_diagnostic_present, heartbeat_present (§13)

Scope: SMOKE-only cell. No FULL variant. USER-locked SMOKE-only-on-local_cpu
discipline (feedback_smoke_only_local_cpu_no_full_dispatches_USER_LOCKED_2026-07-01.md);
a FULL scale-up would be a separate cell filed after this floor-check reports.

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

ANCHOR_NAME = "substrate_wikipedia_char_trigram_baseline_smoke_2026_07_03"

# --- Config ---
DS_SMOKE = REPO / "data" / "datasets" / "wikipedia_smoke_500.jsonl"

# Substrate-native HD dimension. 2048 is enough headroom for 500-article
# discrimination at chance = 5/500 = 0.01; not so large that the smoke wall
# blows past the 180s queue_add SMOKE_TIMEOUT.
# THEORETICAL@ 500 articles at N_DIM=2048 stores 4.1 vecs per active-dim on average.
N_DIM = 2048

# Article corpus size. Local dataset has 500 rows; take all of them.
# MEASURED@ wc -l data/datasets/wikipedia_smoke_500.jsonl = 500.
N_ARTICLES = 500

# Article body char cap to keep encode fast + comparable across arms.
# HYPOTHESIZED@ 800 chars of lead text is >>title trigram overlap on average.
BODY_CHAR_CAP = 800

# Seeds. Char-trigram is deterministic across seeds by design (trigram hash
# codebook); random arm depends on seed. Running 3 seeds gives std for random
# arm and demonstrates char-trigram determinism (std ~ 0).
SEEDS = [11, 17, 23]

# HP band constants (per pre-reg).
HP_TRIGRAM_R5_FLOOR = 0.60
HF_TRIGRAM_R5_HARD_FLOOR = 0.30
# THEORETICAL@ chance recall@5 = 5/500 = 0.01. Random arm must land near this.
CHANCE_R5 = 5.0 / N_ARTICLES
# Random baseline sanity band: chance +/- 3x. Anything outside is an encoder bug.
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


# --- Deterministic in-code mini corpus for --self-test (no dataset dep) ---
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


# --- Data loading ---
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


# --- Retrieval metrics ---
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
def _selftest_mini_arms_differ() -> None:
    from hdlab.char_trigram_encoder import CharTrigramEncoder
    articles = _MINI_CORPUS
    n = len(articles)
    ct = CharTrigramEncoder(n_dim=1024)
    b_tri = np.stack([ct.encode(a["text"]) for a in articles], axis=0)
    t_tri = np.stack([ct.encode(a["title"]) for a in articles], axis=0)
    rng = np.random.default_rng(11)
    b_rand = (rng.integers(0, 2, size=(n, 1024)) * 2 - 1).astype(np.float32)
    t_rand = (rng.integers(0, 2, size=(n, 1024)) * 2 - 1).astype(np.float32)
    arms = {"trigram": b_tri, "random": b_rand}
    digests = _arms_differ_hash(arms)
    assert len(set(digests.values())) == len(arms), f"arms_differ failed: {digests}"
    for name, arr in [("b_tri", b_tri), ("t_tri", t_tri), ("b_rand", b_rand), ("t_rand", t_rand)]:
        n_nan = int(np.isnan(arr).sum())
        assert n_nan == 0, f"selftest NaN in {name}: n_nan={n_nan}"
    mt = _retrieval_metrics(b_tri, t_tri, seed=11)
    # Titles like "Alpha Star" have strong trigram overlap with their body text -> mini r@1 > 0.
    assert mt["recall_at_1"] >= 0.20, f"selftest trigram r@1={mt['recall_at_1']:.3f} < 0.20"
    mr = _retrieval_metrics(b_rand, t_rand, seed=11)
    # Random arm on N=5 mini corpus: r@5 must be 1.0 (all in top-5); r@1 is not stably bounded.
    assert mr["recall_at_5"] == 1.0, f"selftest random r@5 on N=5 corpus expected 1.0 got {mr['recall_at_5']}"
    print(f"[selftest mini_arms_differ] PASS -- digests={digests} "
          f"trigram r@1={mt['recall_at_1']:.3f} random r@1={mr['recall_at_1']:.3f}",
          flush=True)


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
    """Random bipolar HDs at N=200 x n_dim=2048 must give r@5 near 5/200 = 0.025 (band 0.0-0.10)."""
    n = 200
    n_dim = 2048
    rng = np.random.default_rng(17)
    b = (rng.integers(0, 2, size=(n, n_dim)) * 2 - 1).astype(np.float32)
    t = (rng.integers(0, 2, size=(n, n_dim)) * 2 - 1).astype(np.float32)
    m = _retrieval_metrics(b, t, seed=17)
    chance_expected = 5.0 / n
    # Random arm: r@5 must be in [0, chance_expected * 5] band.
    assert 0.0 <= m["recall_at_5"] <= chance_expected * 5, (
        f"random arm at N={n} r@5={m['recall_at_5']:.4f} outside "
        f"chance band [0, {chance_expected*5:.4f}] (chance={chance_expected:.4f})"
    )
    print(f"[selftest random_chance_at_scale] PASS -- r@5={m['recall_at_5']:.4f} "
          f"(chance={chance_expected:.4f})", flush=True)


def _selftest_arg_parse_default_is_smoke() -> None:
    # SMOKE-only cell: assert defaulting to 'smoke' when no flag is given prevents accidental FULL invocation.
    # We rebuild the parse in a subprocess-safe way -- call with mocked argv.
    old = sys.argv
    try:
        sys.argv = ["exp_substrate_wikipedia_char_trigram_baseline_smoke_2026-07-03"]
        mode = _parse_args()
        assert mode == "smoke", f"default mode should be 'smoke' not {mode!r}"
    finally:
        sys.argv = old
    print("[selftest arg_parse_default_is_smoke] PASS", flush=True)


def _run_selftests() -> int:
    tests = [
        ("retrieval_metrics_identity", _selftest_retrieval_metrics_identity),
        ("random_chance_at_scale", _selftest_random_chance_at_scale),
        ("mini_arms_differ", _selftest_mini_arms_differ),
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

    arm_defs = [
        ("ARM_CHAR_TRIGRAM_WIKIPEDIA", lambda: _encode_char_trigram(articles, seed)),
        ("ARM_RANDOM_BASELINE", lambda: _encode_random_baseline(articles, seed)),
    ]

    for arm_idx, (arm_name, encode_fn) in enumerate(arm_defs):
        _log(f"[seed {seed}] arm {arm_name} starting")
        arm_t0 = time.perf_counter()
        try:
            body_hds, title_hds, encoding_wall_s = encode_fn()
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
            _heartbeat(output_dir, arm_idx, len(arm_defs), time.perf_counter() - arm_t0,
                       {"arm": arm_name, "status": "failed", "failure_class": failure_class})
            continue
        n_nan = int(np.isnan(body_hds).sum()) + int(np.isnan(title_hds).sum())
        if n_nan > 0:
            per_arm[arm_name] = {
                "arm_name": arm_name,
                "failure_class": "NAN_IN_HDS",
                "failure_msg": f"n_nan={n_nan}",
                "encoding_wall_s": encoding_wall_s,
            }
            _log(f"[seed {seed}] arm {arm_name} NaN in HDs (n_nan={n_nan})")
            continue
        metrics = _retrieval_metrics(body_hds, title_hds, seed=seed)
        metrics.update({
            "arm_name": arm_name,
            "n_dim": int(body_hds.shape[1]),
            "encoding_wall_s": float(encoding_wall_s),
            "throughput_articles_per_sec": float(len(articles) / max(encoding_wall_s, 1e-6)),
        })
        per_arm[arm_name] = metrics
        per_arm_body_hds[arm_name] = body_hds
        _log(f"[seed {seed}] arm {arm_name} r@1={metrics['recall_at_1']:.3f} "
             f"r@5={metrics['recall_at_5']:.3f} r@10={metrics['recall_at_10']:.3f} "
             f"intra={metrics['intra_article_body_title_cos']:.3f} "
             f"inter={metrics['inter_article_title_body_cos']:.3f} "
             f"wall={encoding_wall_s:.2f}s "
             f"thr={metrics['throughput_articles_per_sec']:.1f}art/s")
        _heartbeat(output_dir, arm_idx, len(arm_defs), time.perf_counter() - arm_t0,
                   {"arm": arm_name, "recall_at_5": metrics["recall_at_5"]})

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
    arm_names = ["ARM_CHAR_TRIGRAM_WIKIPEDIA", "ARM_RANDOM_BASELINE"]
    out: Dict[str, Dict] = {}
    for arm in arm_names:
        r1s, r5s, r10s, walls, throughputs = [], [], [], [], []
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
    HP1 (char-trigram r@5 >= 0.60): LOAD_BEARING on ARM_CHAR_TRIGRAM_WIKIPEDIA
    HF1 (char-trigram r@5 < 0.30): substrate-native surface encoder alone insufficient
    HF2 (random r@5 out of chance band): implementation bug
    """
    tri = agg.get("ARM_CHAR_TRIGRAM_WIKIPEDIA", {}).get("recall_at_5_mean")
    rnd = agg.get("ARM_RANDOM_BASELINE", {}).get("recall_at_5_mean")

    if actual_n_units < expected_n_units:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                f"HARD_FAIL_CARDINALITY: expected {expected_n_units} unit-metrics but got {actual_n_units}; "
                f"one or more (seed, arm) units failed. See per-seed per_arm failure_class.")

    if tri is None or rnd is None:
        return ("HARD_FAIL_ARM_MISSING",
                f"HARD_FAIL: one or more arms have no r@5 metric: trigram={tri} random={rnd}")

    # HF2 first: baseline_in_band sanity (META_RULE_AG). If random arm is above the
    # chance band, the retrieval implementation is buggy and all r@5 numbers are
    # untrustworthy.
    if rnd > BASELINE_IN_BAND_R5_MAX:
        return ("HARD_FAIL_BASELINE_OUT_OF_BAND_META_RULE_AG",
                f"HF2 baseline_in_band failed: ARM_RANDOM_BASELINE r@5={rnd:.4f} > "
                f"{BASELINE_IN_BAND_R5_MAX:.4f} (chance={CHANCE_R5:.4f}). "
                f"Implementation bug in _retrieval_metrics or _encode_random_baseline. "
                f"trigram r@5={tri:.4f}")

    # HF1: char-trigram floor
    if tri < HF_TRIGRAM_R5_HARD_FLOOR:
        return ("HARD_FAIL_MECHANISM_INSUFFICIENT",
                f"HF1 char-trigram r@5={tri:.4f} < {HF_TRIGRAM_R5_HARD_FLOOR:.2f}. "
                f"Substrate-native surface encoder alone is insufficient for real-corpus "
                f"Wikipedia title-article retrieval; brain-analog composition "
                f"(VWFA + ATL + Spoke 3 hippocampal) is LOAD_BEARING. "
                f"random r@5={rnd:.4f} (chance={CHANCE_R5:.4f})")

    # HP: char-trigram floor cleared
    if tri >= HP_TRIGRAM_R5_FLOOR:
        return ("HARD_PASS",
                f"HARD_PASS: substrate-native char-trigram surface encoder reaches "
                f"r@5={tri:.4f} >= {HP_TRIGRAM_R5_FLOOR:.2f} on N={N_ARTICLES} real "
                f"Wikipedia articles at N_DIM={N_DIM}. HONEST SCOPE: title-body char-"
                f"trigram overlap dominates; does NOT grant substrate general-knowledge "
                f"of Wikipedia content. bge reference r@5=0.992 (100K MEASURED); "
                f"gap-to-bge={0.992 - tri:+.4f} indicates the residual capability "
                f"headroom that brain-analog composition (VWFA + ATL + Spoke 3) must "
                f"close. random r@5={rnd:.4f} (chance={CHANCE_R5:.4f})")

    # MIDDLE_BAND: between HF and HP floor
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: char-trigram r@5={tri:.4f} in [{HF_TRIGRAM_R5_HARD_FLOOR:.2f}, "
            f"{HP_TRIGRAM_R5_FLOOR:.2f}). Surface encoder gets partial signal but below CG "
            f"floor. Non-trivial title-body overlap exists but brain-analog composition "
            f"still needed. random r@5={rnd:.4f} (chance={CHANCE_R5:.4f})")


# --- main ---
def main() -> int:
    if IS_SELFTEST:
        rc = _run_selftests()
        sys.exit(rc)

    output_dir = get_output_dir(ANCHOR_NAME)
    output_dir.mkdir(parents=True, exist_ok=True)

    expected_n_units = len(SEEDS) * 2  # 2 arms
    _write_start_marker(output_dir, expected_n_units)

    _log(f"[config] anchor={ANCHOR_NAME}")
    _log(f"[config] run_mode={RUN_MODE} n_articles={N_ARTICLES} seeds={SEEDS} n_dim={N_DIM}")
    _log(f"[config] dataset_path={DS_SMOKE}")

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
        "baseline_in_band_check": {
            "arm": "ARM_RANDOM_BASELINE",
            "chance_r5": CHANCE_R5,
            "band_max_r5": BASELINE_IN_BAND_R5_MAX,
            "observed_r5_mean": agg.get("ARM_RANDOM_BASELINE", {}).get("recall_at_5_mean"),
            "in_band": (agg.get("ARM_RANDOM_BASELINE", {}).get("recall_at_5_mean") or 0.0) <= BASELINE_IN_BAND_R5_MAX,
        },
        "final_metrics_atomicity": "tmp_replace",
        "hp_scope": {
            "HP1": ["ARM_CHAR_TRIGRAM_WIKIPEDIA"],
            "HF1": ["ARM_CHAR_TRIGRAM_WIKIPEDIA"],
            "HF2_baseline_in_band": ["ARM_RANDOM_BASELINE"],
        },
        "bge_reference_r5_at_100k_MEASURED": 0.992,
        "bge_reference_source": "data/exp_wikipedia_ingest_100k_gpu_v1/metrics.json (2026-06-19)",
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
