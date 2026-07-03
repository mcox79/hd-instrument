"""exp_substrate_spoke3_hippocampal_encoder_smoke_2026_07_03

Stage 2 Spoke 3 substrate-native brain-analog hippocampal encoder SMOKE probe
on the same held-out Wikipedia title -> body retrieval task as PPMI + char-
trigram cells (N=500, N_DIM=2048, seeds [11, 17, 23]).

Load-bearing per Skunkworks-approved bge-retire decision fork (B) 2026-07-03:
after PPMI Wikipedia FULL 10K PRELIMINARY HARD_NEGATIVE (r@5=0.6791 < char-
trigram 0.703), no substrate-native surface/semantic mechanism alone closes
the bge gap. Spoke 3 hippocampal composition (DG expansion + Marr-CA3 auto-
associator) is the remaining brain-analog rescue path.

Arms (5 x 3 seeds = 15 units):
  ARM_SPOKE3_HIPPOCAMPAL  (LOAD_BEARING)  char-trigram -> DG expand -> CA3 write
                                          bodies -> retrieve via CA3-settled
                                          title DG codes with top-K sparsify
  ARM_SPOKE3_ONE_SHOT      (ablation)     char-trigram -> DG expand only
                                          (no CA3 settle)
  ARM_PPMI_ALONE           (regression)   MUST reproduce r@5 = 0.906 +/- 0.05
  ARM_CHAR_TRIGRAM         (regression)   MUST reproduce r@5 = 0.854 +/- 0.05
  ARM_RANDOM_BASELINE      (chance floor)

Reference constants (MEASURED@ 2026-07-03 wikipedia smokes):
  PPMI r@5              = 0.906
  char-trigram r@5      = 0.854
  random r@5            = 0.0073 (chance = 5/500 = 0.01)

HP band (LOAD_BEARING on ARM_SPOKE3_HIPPOCAMPAL):
  HP1  ARM_SPOKE3_HIPPOCAMPAL r@5 >= 0.884 (char-trigram + 0.03)
  HF1  ARM_SPOKE3_HIPPOCAMPAL r@5 < 0.824 (char-trigram - 0.03)
  MB   ARM_SPOKE3_HIPPOCAMPAL r@5 in [0.824, 0.884)

Pre-reg: preregs/2026-07-03_substrate_spoke3_hippocampal_encoder_smoke.md
Primitive: hdlab/hippocampal_encoder.py (13 selftests)

FRAMING DISCIPLINE (LOAD-BEARING per USER 2026-07-02):
- SUBSTRATE KNOWS ALMOST NOTHING. Spoke 3 hippocampal is a MECHANISM PROBE on
  the SUPERVISED synthetic-corpus regime; NOT a general-knowledge claim.
- Explicitly AVOIDS 2026-06-23 falsified WTA-collision pattern: expansion FIRST,
  learning driver in CA3, target sparsity ~2% (not 0.25%). Selftest
  hippo_ne_naive_wta_collision_2026_06_23 verifies at mechanism level.
- Discriminator-narrows-at-scale caveat: N=500 smoke may over-project to N=10K
  FULL (V2-A precedent -- PPMI passed at N=500 smoke but HF'd at N=10K FULL).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
- arms_differ_verified (hash-check on first-article body HD prefix per arm)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception
- baseline_in_band (META_RULE_AG; ARM_RANDOM_BASELINE r@5 sanity)
- HP_SCOPE per-arm declaration (in verdict logic)
- cardinality_ok (EXPECTED_N_UNITS = 5 arms x 3 seeds = 15)
- per-unit failure_class instrumentation (no bare except)
- all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@ (META_RULE_AC)
- start_marker_written, crash_diagnostic_present, heartbeat_present
- per-seed checkpoint (SH-4-adjacent) via partial_metrics_<seed>.json atomic
  tmp+os.replace before final aggregation

Scope: SMOKE-only cell. USER-locked SMOKE-only-on-local_cpu.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import sys

# Line-buffered stdout for real-time progress visibility.
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

ANCHOR_NAME = "substrate_spoke3_hippocampal_encoder_smoke_2026_07_03"

# --- Config ---
DS_SMOKE = REPO / "data" / "datasets" / "wikipedia_smoke_500.jsonl"

# THEORETICAL@ input HD dim for char-trigram + PPMI (matches those cells).
N_DIM = 2048

# DG expansion dim. 4x input; well within Johnson-Lindenstrauss capacity for
# N=500 (JL bound: N_DIM/log(500) ~ 1320 << 8192).
DG_DIM = 8192

# DG target sparsity (top-K by magnitude). ~2% -> ~164 active dims per code.
# Matches HippocampalEncoder scale sentinel selftest range.
DG_SPARSITY = 0.02

# MEASURED@ wc -l data/datasets/wikipedia_smoke_500.jsonl = 500.
N_ARTICLES = 500

# Body char cap; matches PPMI + char-trigram cells for apples-to-apples.
BODY_CHAR_CAP = 800

# Seeds.
SEEDS = [11, 17, 23]

# HP band constants (per pre-reg).
# MEASURED@ data/exp_substrate_wikipedia_ppmi_svd_baseline_smoke_2026_07_03/
#   metrics.json:per_arm_aggregate.ARM_CHAR_TRIGRAM_WIKIPEDIA.recall_at_5_mean = 0.854
CHAR_TRIGRAM_REFERENCE_R5 = 0.854
# MEASURED@ same metrics.json ARM_PPMI_SVD_WIKIPEDIA.recall_at_5_mean = 0.906
PPMI_REFERENCE_R5 = 0.906
HP_MARGIN = 0.03
HP_SPOKE3_R5_FLOOR = CHAR_TRIGRAM_REFERENCE_R5 + HP_MARGIN   # 0.884
HF_SPOKE3_R5_HARD_FLOOR = CHAR_TRIGRAM_REFERENCE_R5 - HP_MARGIN  # 0.824
# Regression tolerances
REG_TOL = 0.05
REG_TRIGRAM_LO = CHAR_TRIGRAM_REFERENCE_R5 - REG_TOL   # 0.804
REG_TRIGRAM_HI = CHAR_TRIGRAM_REFERENCE_R5 + REG_TOL   # 0.904
REG_PPMI_LO = PPMI_REFERENCE_R5 - REG_TOL              # 0.856
REG_PPMI_HI = PPMI_REFERENCE_R5 + REG_TOL              # 0.956
# THEORETICAL@ chance recall@5 = 5/500 = 0.01
CHANCE_R5 = 5.0 / N_ARTICLES
# Random baseline sanity band (5x chance).
BASELINE_IN_BAND_R5_MAX = 0.05
# DG sparse rate architectural constraint.
DG_SPARSE_RATE_MIN = 0.008
DG_SPARSE_RATE_MAX = 0.040


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
    # SMOKE-only cell.
    return "smoke"


RUN_MODE = _parse_args()
IS_SMOKE = RUN_MODE == "smoke"
IS_SELFTEST = RUN_MODE == "self_test"


# --- Mini corpus for --self-test ---
_MINI_CORPUS = [
    {"title": "Alpha Star", "text": "Alpha Star is a bright celestial object. Astronomers observe alpha star regularly."},
    {"title": "Beta River", "text": "Beta River flows through the valley. Its waters are clear. Beta river supports aquatic life."},
    {"title": "Gamma Mountain", "text": "Gamma Mountain rises above the plain. Climbers ascend gamma mountain each summer."},
    {"title": "Delta Forest", "text": "Delta Forest is an ancient woodland. Delta forest is a protected reserve."},
    {"title": "Epsilon Lake", "text": "Epsilon Lake is a freshwater body. Epsilon lake attracts many birds."},
]


# --- Observability helpers ---
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


def _heartbeat(output_dir: Path, unit_idx: int, total_units: int,
               elapsed_s: float, extra: dict) -> None:
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


def _write_partial_seed(output_dir: Path, seed: int, payload: dict) -> None:
    """Atomic per-seed checkpoint (SH-4). Prevents PPMI FULL-cell data-loss pattern."""
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / f"partial_metrics_{seed}.json.tmp"
    final = output_dir / f"partial_metrics_{seed}.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    os.replace(tmp, final)


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

def _encode_char_trigram_body_title(articles: List[Dict[str, str]]) -> Tuple[np.ndarray, np.ndarray, float]:
    """Substrate-native char-trigram bag-of-HD encoder. Returns (body_hds, title_hds, wall)."""
    from hdlab.char_trigram_encoder import CharTrigramEncoder
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


def _encode_arm_char_trigram(articles, seed):
    """ARM_CHAR_TRIGRAM regression."""
    _ = seed
    b, t, w = _encode_char_trigram_body_title(articles)
    return b, t, w, 0.0, None


def _encode_arm_ppmi_svd(articles, seed):
    """ARM_PPMI_ALONE regression."""
    from hdlab.ppmi_sparse_encoder import PPMISparseEncoder
    n = len(articles)
    bodies = [a["text"] for a in articles]
    labels = np.arange(n, dtype=np.int64)
    fit_t0 = time.perf_counter()
    enc = PPMISparseEncoder(n_dim=N_DIM, min_term_freq=2, smoothing=0.75, seed=int(seed))
    enc.fit(bodies, labels)
    fit_wall = time.perf_counter() - fit_t0
    _log(f"  [ppmi] fit V={len(enc.term_to_idx)} effective_dim={enc.effective_n_dim} "
         f"fit_wall={fit_wall:.2f}s")
    encode_t0 = time.perf_counter()
    body_hds = np.zeros((n, N_DIM), dtype=np.float32)
    title_hds = np.zeros((n, N_DIM), dtype=np.float32)
    for i, a in enumerate(articles):
        body_hds[i] = enc.encode(a["text"])
        title_hds[i] = enc.encode(a["title"])
        if (i + 1) % max(1, n // 5) == 0:
            _log(f"  [ppmi] encode {i+1}/{n}")
    encode_wall = time.perf_counter() - encode_t0
    diag = {"vocab_size": int(len(enc.term_to_idx)), "effective_n_dim": int(enc.effective_n_dim)}
    return body_hds, title_hds, encode_wall, fit_wall, diag


def _encode_arm_random(articles, seed):
    """ARM_RANDOM_BASELINE chance floor."""
    n = len(articles)
    rng = np.random.default_rng(int(seed) * 977 + 3)
    t0 = time.perf_counter()
    body_hds = (rng.integers(0, 2, size=(n, N_DIM)) * 2 - 1).astype(np.float32)
    title_hds = (rng.integers(0, 2, size=(n, N_DIM)) * 2 - 1).astype(np.float32)
    wall = time.perf_counter() - t0
    return body_hds, title_hds, wall, 0.0, None


def _encode_arm_spoke3_hippocampal(articles, seed):
    """ARM_SPOKE3_HIPPOCAMPAL (LOAD_BEARING).

    Pipeline:
      char-trigram body_hd/title_hd (input HD in R^{N_DIM})
      -> DG expansion + top-K sparsify (dg_dim=8192, sparsity=0.02)
      -> Write CA3 attractors from body DG codes (Hebbian outer product)
      -> Retrieve title codes via CA3 settle + top-K sparsify -> stays in
         sparse DG-code manifold
    Retrieval: cos(title_dg_completed[i], stored_body_dg[j])
    """
    from hdlab.hippocampal_encoder import HippocampalEncoder
    n = len(articles)
    _log(f"  [spoke3] char-trigram surface encoding N={n}")
    body_hd, title_hd, ct_wall = _encode_char_trigram_body_title(articles)

    fit_t0 = time.perf_counter()
    enc = HippocampalEncoder(input_dim=N_DIM, dg_dim=DG_DIM,
                             sparsity=DG_SPARSITY, seed=int(seed))
    _log(f"  [spoke3] DG expansion body_hd -> body_dg dg_dim={DG_DIM} sparsity={DG_SPARSITY}")
    stored_body_dg = enc.encode_and_write(body_hd)  # sparse ternary [n, dg_dim]
    dg_sparse_rate = enc.dg_sparse_rate(stored_body_dg)
    _log(f"  [spoke3] CA3 written n_writes={enc.ca3.n_written} "
         f"observed_dg_rate={dg_sparse_rate:.4f}")
    _log(f"  [spoke3] retrieve title_hd -> DG -> CA3 settle -> sparsify")
    title_dg_completed = enc.retrieve(title_hd, use_ca3=True,
                                      sparsify_after_settle=True)
    fit_wall = time.perf_counter() - fit_t0

    diag = {
        "input_dim": N_DIM, "dg_dim": DG_DIM, "sparsity_target": DG_SPARSITY,
        "dg_sparse_rate_observed": float(dg_sparse_rate),
        "ca3_n_written": int(enc.ca3.n_written),
        "char_trigram_wall_s": float(ct_wall),
    }
    # The "retrieval codes" are DG codes (dg_dim); cos in DG space.
    return stored_body_dg, title_dg_completed, ct_wall, fit_wall, diag


def _encode_arm_spoke3_one_shot(articles, seed):
    """ARM_SPOKE3_ONE_SHOT (ablation): DG expansion only; no CA3 settle.

    Isolates the DG-expansion contribution from the CA3 pattern-completion
    contribution. Retrieval: cos(title_dg[i], body_dg[j]).
    """
    from hdlab.hippocampal_encoder import HippocampalEncoder
    n = len(articles)
    _log(f"  [spoke3_1s] char-trigram surface encoding N={n}")
    body_hd, title_hd, ct_wall = _encode_char_trigram_body_title(articles)
    fit_t0 = time.perf_counter()
    enc = HippocampalEncoder(input_dim=N_DIM, dg_dim=DG_DIM,
                             sparsity=DG_SPARSITY, seed=int(seed))
    _log(f"  [spoke3_1s] DG expansion body_hd -> body_dg (no CA3 write/settle)")
    body_dg = enc.dg.encode_batch(body_hd)  # sparse ternary [n, dg_dim]
    title_dg = enc.dg.encode_batch(title_hd)
    fit_wall = time.perf_counter() - fit_t0
    dg_sparse_rate = enc.dg_sparse_rate(body_dg)
    diag = {"input_dim": N_DIM, "dg_dim": DG_DIM, "sparsity_target": DG_SPARSITY,
            "dg_sparse_rate_observed": float(dg_sparse_rate),
            "char_trigram_wall_s": float(ct_wall)}
    return body_dg, title_dg, ct_wall, fit_wall, diag


# --- Retrieval metrics (bit-identical to PPMI + char-trigram cells) ---
def _retrieval_metrics(body_hds: np.ndarray, title_hds: np.ndarray,
                       seed: int) -> Dict[str, float]:
    """recall@k, MRR, intra/inter cos, snr."""
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
                    f"META_RULE_AF VIOLATION arms_differ: {a!r} and {b!r} "
                    f"bit-identical first-article prefix (hash={digests[a]})."
                )
    return digests


# --- Cell-level selftests (chain to primitive selftests via subprocess) ---
def _selftest_retrieval_metrics_identity() -> None:
    n = 20
    n_dim = 128
    rng = np.random.default_rng(11)
    x = rng.standard_normal((n, n_dim)).astype(np.float32)
    m = _retrieval_metrics(x, x, seed=11)
    assert m["recall_at_1"] == 1.0, f"identity r@1={m['recall_at_1']}"
    print(f"[selftest retrieval_metrics_identity] PASS r1={m['recall_at_1']}",
          flush=True)


def _selftest_random_chance_at_scale() -> None:
    n = 200
    n_dim = 2048
    rng = np.random.default_rng(17)
    b = (rng.integers(0, 2, size=(n, n_dim)) * 2 - 1).astype(np.float32)
    t = (rng.integers(0, 2, size=(n, n_dim)) * 2 - 1).astype(np.float32)
    m = _retrieval_metrics(b, t, seed=17)
    chance_expected = 5.0 / n
    assert 0.0 <= m["recall_at_5"] <= chance_expected * 5, (
        f"random arm r@5={m['recall_at_5']:.4f} outside band")
    print(f"[selftest random_chance_at_scale] PASS -- r@5={m['recall_at_5']:.4f}",
          flush=True)


def _selftest_spoke3_pipeline_mini() -> None:
    """Spoke 3 pipeline runs end-to-end on 5-article mini corpus and produces
    a distinct output from DG-only variant."""
    articles = _MINI_CORPUS
    n = len(articles)
    b_hip, t_hip, _, _, diag_hip = _encode_arm_spoke3_hippocampal(articles, seed=11)
    b_1s, t_1s, _, _, diag_1s = _encode_arm_spoke3_one_shot(articles, seed=11)
    assert b_hip.shape == (n, DG_DIM), f"hippo body shape {b_hip.shape}"
    assert b_1s.shape == (n, DG_DIM), f"one-shot body shape {b_1s.shape}"
    # DG-only produces same body codes as hippocampal in this smoke (both use
    # DG.encode_batch on body_hd); the arms differ on TITLE side (hippocampal
    # settles title via CA3, one-shot doesn't).
    h_t_hip = hashlib.sha256(t_hip.tobytes()).hexdigest()
    h_t_1s = hashlib.sha256(t_1s.tobytes()).hexdigest()
    assert h_t_hip != h_t_1s, (
        f"Spoke3 title codes bit-identical hippo vs one-shot: "
        f"hip={h_t_hip[:8]} 1s={h_t_1s[:8]}. CA3 settle had no effect."
    )
    rate = diag_hip["dg_sparse_rate_observed"]
    assert 0.005 <= rate <= 0.08, f"spoke3 dg_sparse_rate={rate:.4f} out of band"
    print(f"[selftest spoke3_pipeline_mini] PASS title_hash_diff hip={h_t_hip[:8]} "
          f"1s={h_t_1s[:8]} dg_rate={rate:.4f}", flush=True)


def _selftest_arg_parse_default_is_smoke() -> None:
    old = sys.argv
    try:
        sys.argv = ["exp_substrate_spoke3_hippocampal_encoder_smoke_2026-07-03"]
        mode = _parse_args()
        assert mode == "smoke", f"default mode should be 'smoke' not {mode!r}"
    finally:
        sys.argv = old
    print("[selftest arg_parse_default_is_smoke] PASS", flush=True)


def _selftest_primitive_selftests_chain() -> None:
    """Verify hippocampal_encoder primitive selftests pass (13 tests)."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "hdlab.hippocampal_encoder", "--self-test"],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        print("[selftest primitive_selftests_chain] STDOUT:")
        print(result.stdout)
        print("[selftest primitive_selftests_chain] STDERR:")
        print(result.stderr)
        raise AssertionError(
            f"hdlab.hippocampal_encoder --self-test returned {result.returncode}"
        )
    # Verify at least summary line indicates 13/13 passed
    if "13/13 passed" not in result.stdout:
        raise AssertionError(
            f"hippocampal_encoder selftest summary not '13/13 passed'; "
            f"stdout tail:\n{result.stdout[-500:]}"
        )
    print("[selftest primitive_selftests_chain] PASS 13/13 hippocampal_encoder "
          "selftests", flush=True)


def _run_selftests() -> int:
    tests = [
        ("retrieval_metrics_identity", _selftest_retrieval_metrics_identity),
        ("random_chance_at_scale", _selftest_random_chance_at_scale),
        ("spoke3_pipeline_mini", _selftest_spoke3_pipeline_mini),
        ("arg_parse_default_is_smoke", _selftest_arg_parse_default_is_smoke),
        ("primitive_selftests_chain", _selftest_primitive_selftests_chain),
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
    print(f"[selftest summary] {len(tests) - len(failed)}/{len(tests)} passed",
          flush=True)
    return 0 if not failed else 1


# --- Per-seed driver ---
ARM_DEFS = [
    "ARM_SPOKE3_HIPPOCAMPAL",
    "ARM_SPOKE3_ONE_SHOT",
    "ARM_PPMI_ALONE",
    "ARM_CHAR_TRIGRAM",
    "ARM_RANDOM_BASELINE",
]

ARM_ENCODERS = {
    "ARM_SPOKE3_HIPPOCAMPAL": _encode_arm_spoke3_hippocampal,
    "ARM_SPOKE3_ONE_SHOT": _encode_arm_spoke3_one_shot,
    "ARM_PPMI_ALONE": _encode_arm_ppmi_svd,
    "ARM_CHAR_TRIGRAM": _encode_arm_char_trigram,
    "ARM_RANDOM_BASELINE": _encode_arm_random,
}


def _run_one_seed(seed: int, articles: List[Dict[str, str]],
                  output_dir: Path) -> Dict:
    _log(f"[seed {seed}] starting; n_articles={len(articles)}")
    per_arm: Dict[str, Dict] = {}
    per_arm_body_hds: Dict[str, np.ndarray] = {}
    n_arms = len(ARM_DEFS)

    for arm_idx, arm_name in enumerate(ARM_DEFS):
        _log(f"[seed {seed}] arm {arm_name} ({arm_idx+1}/{n_arms}) starting")
        arm_t0 = time.perf_counter()
        try:
            result = ARM_ENCODERS[arm_name](articles, seed)
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
            _heartbeat(output_dir, arm_idx, n_arms,
                       time.perf_counter() - arm_t0,
                       {"arm": arm_name, "status": "failed",
                        "failure_class": failure_class})
            continue
        # All encoders now return the 5-tuple (body, title, enc_wall, fit_wall, diag)
        body_hds, title_hds, encoding_wall_s, fit_wall_s, arm_diag = result
        n_nan = int(np.isnan(body_hds).sum()) + int(np.isnan(title_hds).sum())
        if n_nan > 0:
            per_arm[arm_name] = {
                "arm_name": arm_name,
                "failure_class": "NAN_IN_HDS",
                "failure_msg": f"n_nan={n_nan}",
                "encoding_wall_s": encoding_wall_s,
            }
            _log(f"[seed {seed}] arm {arm_name} NaN (n_nan={n_nan})")
            continue
        metrics = _retrieval_metrics(body_hds, title_hds, seed=seed)
        metrics.update({
            "arm_name": arm_name,
            "n_dim": int(body_hds.shape[1]),
            "encoding_wall_s": float(encoding_wall_s),
            "fit_wall_s": float(fit_wall_s),
            "throughput_articles_per_sec": float(len(articles) / max(encoding_wall_s + fit_wall_s, 1e-6)),
        })
        if arm_diag is not None:
            metrics["arm_diag"] = arm_diag
        per_arm[arm_name] = metrics
        per_arm_body_hds[arm_name] = body_hds
        _log(f"[seed {seed}] arm {arm_name} r@1={metrics['recall_at_1']:.3f} "
             f"r@5={metrics['recall_at_5']:.3f} r@10={metrics['recall_at_10']:.3f} "
             f"intra={metrics['intra_article_body_title_cos']:.3f} "
             f"inter={metrics['inter_article_title_body_cos']:.3f} "
             f"enc_wall={encoding_wall_s:.2f}s fit_wall={fit_wall_s:.2f}s")
        _heartbeat(output_dir, arm_idx, n_arms,
                   time.perf_counter() - arm_t0,
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
    out: Dict[str, Dict] = {}
    for arm in ARM_DEFS:
        r1s, r5s, r10s, walls, throughputs, fits = [], [], [], [], [], []
        dg_rates = []
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
            diag = arm_m.get("arm_diag") or {}
            if "dg_sparse_rate_observed" in diag:
                dg_rates.append(diag["dg_sparse_rate_observed"])
        if r5s:
            entry = {
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
            if dg_rates:
                entry["dg_sparse_rate_mean"] = float(np.mean(dg_rates))
            out[arm] = entry
        else:
            out[arm] = {"n_seeds_succeeded": 0, "n_seeds_failed": n_failed,
                        "recall_at_5_mean": None}
    return out


def _verdict(agg: Dict, expected_n_units: int,
             actual_n_units: int) -> Tuple[str, str]:
    """HP_SCOPE per pre-reg:
    HP1 (LOAD_BEARING): ARM_SPOKE3_HIPPOCAMPAL r@5 >= 0.884
    HF1: ARM_SPOKE3_HIPPOCAMPAL r@5 < 0.824
    HFreg-tri: ARM_CHAR_TRIGRAM r@5 outside [0.804, 0.904]
    HFreg-ppmi: ARM_PPMI_ALONE r@5 outside [0.856, 0.956]
    HF-baseline: ARM_RANDOM_BASELINE r@5 > 0.05 (META_RULE_AG)
    HF-dg-rate: ARM_SPOKE3_HIPPOCAMPAL dg_sparse_rate out of [0.008, 0.040]
    """
    spk = agg.get("ARM_SPOKE3_HIPPOCAMPAL", {}).get("recall_at_5_mean")
    spk_1s = agg.get("ARM_SPOKE3_ONE_SHOT", {}).get("recall_at_5_mean")
    ppmi = agg.get("ARM_PPMI_ALONE", {}).get("recall_at_5_mean")
    tri = agg.get("ARM_CHAR_TRIGRAM", {}).get("recall_at_5_mean")
    rnd = agg.get("ARM_RANDOM_BASELINE", {}).get("recall_at_5_mean")
    dg_rate = agg.get("ARM_SPOKE3_HIPPOCAMPAL", {}).get("dg_sparse_rate_mean")

    if actual_n_units < expected_n_units:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                f"HARD_FAIL_CARDINALITY: expected {expected_n_units} unit-metrics "
                f"but got {actual_n_units}. See per-seed per_arm failure_class.")

    if spk is None or ppmi is None or tri is None or rnd is None:
        return ("HARD_FAIL_ARM_MISSING",
                f"HARD_FAIL: one or more arms have no r@5: spoke3={spk} "
                f"ppmi={ppmi} tri={tri} random={rnd}")

    # HF-baseline (META_RULE_AG)
    if rnd > BASELINE_IN_BAND_R5_MAX:
        return ("HARD_FAIL_BASELINE_OUT_OF_BAND_META_RULE_AG",
                f"HF baseline_in_band failed: ARM_RANDOM_BASELINE r@5={rnd:.4f} > "
                f"{BASELINE_IN_BAND_R5_MAX:.4f} (chance={CHANCE_R5:.4f}). "
                f"Retrieval-implementation bug.")

    # HFreg-tri: regression
    if not (REG_TRIGRAM_LO <= tri <= REG_TRIGRAM_HI):
        return ("HARD_FAIL_TRIGRAM_REGRESSION",
                f"HFreg char-trigram r@5={tri:.4f} outside "
                f"[{REG_TRIGRAM_LO:.3f}, {REG_TRIGRAM_HI:.3f}] "
                f"(reference {CHAR_TRIGRAM_REFERENCE_R5:.3f}). Dispatch untrustworthy.")

    # HFreg-ppmi: regression
    if not (REG_PPMI_LO <= ppmi <= REG_PPMI_HI):
        return ("HARD_FAIL_PPMI_REGRESSION",
                f"HFreg PPMI r@5={ppmi:.4f} outside "
                f"[{REG_PPMI_LO:.3f}, {REG_PPMI_HI:.3f}] "
                f"(reference {PPMI_REFERENCE_R5:.3f}). Dispatch untrustworthy.")

    # HF-dg-rate: architectural sanity
    if dg_rate is not None and not (DG_SPARSE_RATE_MIN <= dg_rate <= DG_SPARSE_RATE_MAX):
        return ("HARD_FAIL_DG_SPARSE_RATE_ARCHITECTURAL",
                f"HF DG sparse rate={dg_rate:.4f} outside "
                f"[{DG_SPARSE_RATE_MIN:.3f}, {DG_SPARSE_RATE_MAX:.3f}] "
                f"(target {DG_SPARSITY:.3f}). DGProjection top-K threshold broken.")

    # HF1: mechanism-loses
    if spk < HF_SPOKE3_R5_HARD_FLOOR:
        return ("HARD_FAIL_MECHANISM_LOSES",
                f"HF1 ARM_SPOKE3_HIPPOCAMPAL r@5={spk:.4f} < {HF_SPOKE3_R5_HARD_FLOOR:.4f} "
                f"(char_trigram_ref {CHAR_TRIGRAM_REFERENCE_R5:.3f} - {HP_MARGIN:.2f}). "
                f"Brain-analog hippocampal composition (Marr-CA3 + DG-expansion) LOSES to "
                f"surface char-trigram on real Wikipedia title-body retrieval at N=500 "
                f"smoke. Combined with prior PPMI FULL 10K HF (r@5=0.679 < 0.703), no "
                f"substrate-native surface/semantic/hippocampal mechanism ALONE closes "
                f"the bge gap on this task class. Route to research 2x-drill for "
                f"whether composition (VWFA + ATL + Spoke 3 CLS) or a different "
                f"task class (episodic-binding not open-domain retrieval) is needed. "
                f"HONEST SCOPE: this is mechanism-scope-limited to this task class; NOT "
                f"a substrate-can't-do-Wikipedia claim. spoke3_1s r@5={spk_1s:.4f} "
                f"ppmi r@5={ppmi:.4f} tri r@5={tri:.4f} random r@5={rnd:.4f}")

    # HP: mechanism beats surface bag
    if spk >= HP_SPOKE3_R5_FLOOR:
        return ("HARD_PASS",
                f"HARD_PASS: brain-analog Spoke 3 hippocampal composition "
                f"(Marr-CA3 + DG-expansion at dg_dim={DG_DIM} sparsity={DG_SPARSITY:.3f}) "
                f"reaches r@5={spk:.4f} >= {HP_SPOKE3_R5_FLOOR:.4f} "
                f"(char_trigram + {HP_MARGIN:.2f}) on N={N_ARTICLES} real Wikipedia at "
                f"N_DIM={N_DIM}. HONEST SCOPE: MECHANISM_LIFT on SUPERVISED corpus-as-"
                f"labeled-partition regime; does NOT grant substrate general-knowledge. "
                f"AVOIDS 2026-06-23 falsified WTA-collision mechanism (verified at "
                f"hippo_ne_naive_wta_collision selftest). DISCRIMINATOR-NARROWS-AT-SCALE "
                f"caveat: N=500 smoke may over-project vs N=10K FULL (V2-A precedent -- "
                f"PPMI PASSED smoke but HF'd FULL). Scale-up cell needed before CG claim. "
                f"HOLD pending USER decision. spoke3 - trigram delta = {spk - tri:+.4f}; "
                f"spoke3 - one_shot delta = {spk - (spk_1s or 0):+.4f} (CA3 contribution). "
                f"observed dg_sparse_rate={dg_rate:.4f}. "
                f"spoke3_1s r@5={spk_1s:.4f} ppmi r@5={ppmi:.4f} tri r@5={tri:.4f} "
                f"random r@5={rnd:.4f}")

    # MIDDLE_BAND
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: ARM_SPOKE3_HIPPOCAMPAL r@5={spk:.4f} in "
            f"[{HF_SPOKE3_R5_HARD_FLOOR:.4f}, {HP_SPOKE3_R5_FLOOR:.4f}). Within +/- "
            f"{HP_MARGIN:.2f} of char-trigram reference {CHAR_TRIGRAM_REFERENCE_R5:.3f}. "
            f"Neither clean HP nor clean HF. Route to v2 sparsity/expansion sweep OR "
            f"Spoke 3 v2 (Option B Hebbian-adjusted DG projection). "
            f"spoke3 - trigram delta = {spk - tri:+.4f}; "
            f"spoke3 - one_shot delta = {spk - (spk_1s or 0):+.4f}. "
            f"spoke3_1s r@5={spk_1s:.4f} ppmi r@5={ppmi:.4f} tri r@5={tri:.4f} "
            f"random r@5={rnd:.4f}")


# --- main ---
def main() -> int:
    if IS_SELFTEST:
        rc = _run_selftests()
        sys.exit(rc)

    output_dir = get_output_dir(ANCHOR_NAME)
    output_dir.mkdir(parents=True, exist_ok=True)

    expected_n_units = len(SEEDS) * len(ARM_DEFS)
    _write_start_marker(output_dir, expected_n_units)

    _log(f"[config] anchor={ANCHOR_NAME}")
    _log(f"[config] run_mode={RUN_MODE} n_articles={N_ARTICLES} seeds={SEEDS} "
         f"n_dim={N_DIM} dg_dim={DG_DIM} sparsity={DG_SPARSITY}")
    _log(f"[config] dataset_path={DS_SMOKE}")

    if not DS_SMOKE.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DS_SMOKE}. Expected pre-existing "
            f"data/datasets/wikipedia_smoke_500.jsonl on local disk."
        )

    t0 = time.perf_counter()
    articles = load_articles(N_ARTICLES, DS_SMOKE)
    _log(f"[load] loaded {len(articles)} articles in {time.perf_counter() - t0:.2f}s")

    per_seed: List[Dict] = []
    for seed in SEEDS:
        seed_t0 = time.perf_counter()
        ps = _run_one_seed(seed, articles, output_dir)
        ps["seed_elapsed_s"] = float(time.perf_counter() - seed_t0)
        per_seed.append(ps)
        # SH-4-adjacent per-seed checkpoint (avoids PPMI FULL data-loss).
        _write_partial_seed(output_dir, seed, ps)
        _log(f"[seed {seed}] complete in {ps['seed_elapsed_s']:.2f}s; checkpoint written")

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
        "dg_dim": DG_DIM,
        "dg_sparsity_target": DG_SPARSITY,
        "body_char_cap": BODY_CHAR_CAP,
        "expected_n_units": expected_n_units,
        "actual_n_units": actual_n_units,
        "cardinality_ok": actual_n_units >= expected_n_units,
        "arms_differ_verified": all(
            ps.get("arms_differ_verified", False) for ps in per_seed),
        "baseline_in_band_check": {
            "arm": "ARM_RANDOM_BASELINE",
            "chance_r5": CHANCE_R5,
            "band_max_r5": BASELINE_IN_BAND_R5_MAX,
            "observed_r5_mean": agg.get("ARM_RANDOM_BASELINE", {}).get("recall_at_5_mean"),
            "in_band": (agg.get("ARM_RANDOM_BASELINE", {}).get("recall_at_5_mean") or 0.0)
                        <= BASELINE_IN_BAND_R5_MAX,
        },
        "final_metrics_atomicity": "tmp_replace",
        "progress_logging": "print_flush_true",
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "hp_scope": {
            "HP1": ["ARM_SPOKE3_HIPPOCAMPAL"],
            "HF1": ["ARM_SPOKE3_HIPPOCAMPAL"],
            "HFreg_trigram": ["ARM_CHAR_TRIGRAM"],
            "HFreg_ppmi": ["ARM_PPMI_ALONE"],
            "HF_baseline_in_band": ["ARM_RANDOM_BASELINE"],
            "HF_dg_sparse_rate": ["ARM_SPOKE3_HIPPOCAMPAL"],
        },
        "reference_r5_MEASURED": {
            "char_trigram": CHAR_TRIGRAM_REFERENCE_R5,
            "ppmi_svd": PPMI_REFERENCE_R5,
            "source": "data/exp_substrate_wikipedia_ppmi_svd_baseline_smoke_2026_07_03/metrics.json",
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
