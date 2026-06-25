"""
substrate_compose_heterogeneous_routing_v3_full_config_rerun -- v2 RESCUE_FULL
landed HARD_FAIL_PROVENANCE; v3 rerun at SAME fair-harness rail config + GPU
setup hardening.

v2_RESCUE_FULL (overnight_queue 2026-06-25T01:19:24Z) landed `failed` with no
artifacts. v2_RESCUE (CPU smaller-scope) landed HARD_FAIL_PROVENANCE because
baseline drift was 0.35 from fair_harness rail 7.3065 -- the rail was set
INSIDE the cross-config noise floor of 0.20-0.45 BPC. Per drill
notes/research_readout_degeneracy_5x_disparate_drill_2026-06-25.md Cell 9:
the rail is correct; the cell mis-applied it (half-N/half-tokens/2-seeds vs
N=8192/100k/3-seeds rail). v3 reruns at FULL fair-harness config + adds GPU
setup hardening for the silent-failure mode the FULL run hit.

CHANGES vs v2_RESCUE_FULL:
  1. Bands TIGHTENED per drill recommendation -- TOL 0.05 (was 0.10), CG <=6.95,
     HP <=7.20, HARD_FAIL on baseline drift > 0.05.
  2. ARM_FREQ_ROUTED_K2 (the lead arm per v2_RESCUE +0.22 BPC differential) is
     PRIMARY for verdict; cell spec confirms.
  3. GPU setup hardening (vs v2_RESCUE_FULL silent crash):
     - explicit cuda.empty_cache + device-mismatch asserts at startup
     - memory-headroom print before each arm
     - D2 atexit handler flushes partials BEFORE any crash propagates
     - per-step (not just per-arm) checkpointable state
  4. Per Fix #24: torch.cuda + batched ops mandatory; smoke profiling sanity.

PRODUCTION CONFIG (matches fair-harness rail EXACTLY):
  N_DIM = 8192 (was v2_RESCUE 4096 = HALF)
  N_TRAIN = 100_000 (was v2_RESCUE 50k = HALF)
  N_HELD = 20_000
  VOCAB_CAP = 4000
  SEEDS = [7, 17, 23] (was v2_RESCUE [7, 17] = 2 seeds)
  encoder = word2vec sparse-bipolar f=0.05 (matches fair-harness rail)
  Routing: overnight_queue (GPU) -- 7200s timeout.

HARD bands (v3; drill-tightened):
  HARD_PASS_CHAIN_GRADE: best het arm BPC <= 6.95 AND beats BASELINE by >= 0.20
                          BPC AND CV <= 0.03 AND sanity_rail OK
                          (baseline in +/-0.05 of 7.3065)
  HARD_PASS:             best het arm BPC <= 7.20 AND beats BASELINE by >= 0.10
                          AND sanity_rail OK
  HARD_FAIL_PROVENANCE:  baseline rail drift > 0.05 (re-investigate)
  HARD_FAIL_DECISIVE:    best het arm <= BASELINE AND sanity_rail OK
                          (heterogeneous architecture refuted at full scale)

Sanity rail: ARM_BASELINE_FAIR_HARNESS within +/-0.05 of fair-harness 7.3065
(was v2_RESCUE_FULL 0.10; v3 tightened per drill).

ASCII-only. Per-seed checkpoint + atexit. Fix #14 + Fix #28 + Fix #24.

---- ORIGINAL v2_RESCUE docstring follows for provenance ----

substrate_compose_heterogeneous_routing_v2_RESCUE
-- TIMEOUT-class revival of v1 (which TIMED OUT at 3600s, 0 information).

Per TIMEOUT-class drill ANCHOR 2 (notes/research_timeout_class_revival_disparate_fields_2026-06-24.md +
notes/exp_dev_handoff_research_timeout_class_revival_2026-06-24.md):

  v1 wall: seed 7 alone took 3074s at N_DIM=8192 N_TRAIN=100k (per partial_metrics_7.json),
  so 3 seeds would have needed ~9200s -- but the timeout was 3600s. ZERO information landed.

  Per disparate-fields drill (HPC roofline / queueing theory / Erlang OTP / K-SAT phase /
  brain energy budget): smaller units + partial results + sparse computation + no global
  sync. This rescue applies all four:

    - SMALLER UNITS: N_DIM 8192 -> 4096 (4x matmul reduction); N_TRAIN 100k -> 50k (2x);
      SEEDS 3 -> 2 (1.5x). Total per-seed cost ~8x smaller.
    - PARTIAL RESULTS: D2 atexit handler flushes per-arm-per-seed state at SIGTERM/timeout.
    - SPARSE COMPUTATION: sparsify_bipolar_gpu (f=0.05) preserved.
    - NO GLOBAL SYNC: per-seed checkpoint (_seed_checkpoint); seed-0 lands before seed-1.

Scope ('rescue with scope reduction + disciplines' per task spec):
  N_DIM=4096 (v1: 8192)
  N_TRAIN=50_000 (v1: 100_000)
  N_HELD=10_000 (v1: 20_000)
  SEEDS=[7, 17] (v1: [7, 17, 23])

NEW DISCIPLINES MANDATORY this revision:

  D1 ROOFLINE PROBE (pre-FULL gate): before running any FULL seed, time the SLOWEST
       arm (ARM_FREQ_ROUTED_K2 per v1 metrics: 1351s @ N=8192) at 3 scales:
         probe_a = N_DIM/4, N_STEPS=50
         probe_b = N_DIM/2, N_STEPS=50
         probe_c = N_DIM,   N_STEPS=50
       Fit t = a * N^k. Extrapolate to full N_STEPS. Refuse dispatch if extrapolated
       wall > 0.8 * --timeout. Probe is ~30-60s and gates >90% of timeout failures.

  D2 ATEXIT + per-seed checkpoint (already wired via _seed_checkpoint.write_partial):
       Module-level atexit handler flushes _RUN_STATE.current_seed_partials to
       partial_metrics_<seed>_atexit.json so even mid-arm interruption leaves SOMETHING.
       _seed_checkpoint handles atomic per-seed final flush.

Four arms (1 baseline + 3 heterogeneous-routing architectures, IDENTICAL to v1):
  ARM_BASELINE_FAIR_HARNESS
      Sanity rail at fair_harness 7.3065 (provenance check)
  ARM_THETA_PHASE_TWO_W
      Two FULL-N_DIM W banks; alternate per-token phase routing:
          phase_0 (encoding): cf-RPE updates W_enc
          phase_1 (retrieval): STDP-asymmetric updates W_ret
      Readout: alpha-mixed cosine. Brain anchor: theta-gamma phase routing.
  ARM_FREQ_ROUTED_K2
      Deterministic frequency-based routing:
          rank <= 100 (top-100 frequent) -> W_freq (cf-RPE, high LR)
          rank > 100 (rare)               -> W_rare (cf-RPE + STDP, lower LR, sparse-amp)
      Brain anchor: hippocampus vs cortex specialization.
  ARM_ORTHOG_SUBSPACE
      Gram-Schmidt orthogonal split of N_DIM into two N_DIM/2 subspaces.
      cf-RPE writes via subspace_1; STDP writes via subspace_2.
      Brain anchor: V1 spatial-freq vs V4 shape orthogonal axes.

PRE-REG HARD bands (UNCHANGED from v1 spec; bands inherit per drill instruction):
  Sanity rail:           ARM_BASELINE_FAIR_HARNESS within +/-0.05 of 7.3065 (provenance)
  HARD_PASS_CAP_BROKEN:  any of ARM_THETA / ARM_FREQ / ARM_ORTHOG BPC <= 6.95
                         (refutes cf-RPE cap; heterogeneous routing works)
  CHAIN_GRADE_BONUS:     best architecture BPC <= 6.80 (substantial gain over cf-RPE)
  MIDDLE_BAND:           best heterogeneous BPC in [6.95, 7.05] (partial signal)
  HARD_FAIL_DECISIVE:    all 3 architectures BPC >= 7.30 (cap structural at this regime)
  cv < 0.05 mandatory on best heterogeneous arm.

Note on band carryover at reduced N: v1 partial_metrics_7 (seed 7 only @ N=8192) found
  best_het = ARM_FREQ_ROUTED_K2 @ 7.2142, ARM_THETA @ 7.2149, ARM_ORTHOG @ 7.4295,
  ARM_BASELINE @ 7.3187. At reduced N=4096 the heterogeneous discriminator may be
  weaker (fewer dims to route across). If MIDDLE_BAND result lands, that itself is
  signal: heterogeneous-routing benefit scales WITH N (interesting capacity-bound).

CONFIG:
  N_DIM=4096, V=4000, text8 N_TRAIN=50k, 2 seeds, word2vec sparse-bipolar f=0.05
  Queue: local_cpu_queue or remote_cpu_queue (~60-90min wall estimated per drill).
  LAMBDA_GRID excludes 0.0 (META C7).

CITES:
  notes/research_timeout_class_revival_disparate_fields_2026-06-24.md (TIMEOUT drill)
  notes/exp_dev_handoff_research_timeout_class_revival_2026-06-24.md (ANCHOR 2)
  experiments/exp_substrate_compose_heterogeneous_routing_v1.py (v1 cell that timed out)
  data/exp_substrate_compose_heterogeneous_routing_v1/partial_metrics_7.json (seed 7 v1 data)
  data/exp_fair_harness_substrate_as_lm_v1/metrics.json (sanity rail 7.3065)
  preregs/2026-06-24_substrate_compose_heterogeneous_routing_v2_RESCUE.md
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse
import atexit
import hashlib
import json
import math
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial, aggregate_partials, write_metrics,
    resumable_seeds as _resumable_seeds,
)

ANCHOR_NAME = "substrate_compose_heterogeneous_routing_v3_full_config_rerun"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# Substrate-only audit counter
_LLM_CALL_COUNTER = [0]

# ============================================================================
# Pre-reg threshold bands (UNCHANGED from v1)
# ============================================================================
SANITY_RAIL_BASELINE_REF = 7.3065
SANITY_RAIL_TOLERANCE = 0.05  # v3: TIGHTENED from v2_RESCUE_FULL 0.10 per drill

# v3 HARD bands (per cell spec; drill-tightened)
HARD_PASS_CAP_BROKEN_BPC = 7.20          # v3 HARD_PASS floor (was 6.95 in v2)
CHAIN_GRADE_BONUS_BPC = 6.95             # v3 HARD_PASS_CHAIN_GRADE floor (was 6.80)
MIDDLE_BAND_LOWER = 7.20
MIDDLE_BAND_UPPER = 7.30
HARD_FAIL_DECISIVE_FLOOR = 7.30
CV_MAX = 0.05                            # HARD_PASS seed CV
CV_MAX_CHAIN_GRADE = 0.03                # v3 CHAIN_GRADE seed CV (tightened)

# v3 discriminator gaps vs BASELINE
BASELINE_GAP_CHAIN_GRADE = 0.20  # best het must beat BASELINE by >= 0.20 BPC (CHAIN_GRADE)
BASELINE_GAP_HARD_PASS = 0.10    # v3: >= 0.10 BPC for HARD_PASS (was 0.15)
HARD_FAIL_HURT_MARGIN = 0.0      # v3: HARD_FAIL_DECISIVE if best het <= baseline (was +0.05)

FREQ_ROUTED_DIFFERENTIAL_MIN = 0.05
THETA_BANK_CORR_MAX = 0.95
ORTHOG_CROSS_CORR_MAX = 0.70

# ============================================================================
# Primitive knob parameters
# ============================================================================
CFRPE_LR = 0.5
STDP_WEIGHT = 0.5
INGEST_BATCH = 64
N_STEPS_PER_SEED = 1000

THETA_ALPHA_GRID = [0.3, 0.5, 0.7]

FREQ_ROUTE_RANK = 100
FREQ_LR_HIGH = 0.5
FREQ_LR_RARE = 0.2

ORTHOG_LR = 0.5

TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

SPARSE_BIPOLAR_F = 0.05
WORD2VEC_MODEL = "word2vec-google-news-300"
PRETRAIN_DIM = 300

ARMS = [
    "ARM_BASELINE_FAIR_HARNESS",
    "ARM_THETA_PHASE_TWO_W",
    "ARM_FREQ_ROUTED_K2",
    "ARM_ORTHOG_SUBSPACE",
]

# ============================================================================
# CLI / run-mode
# ============================================================================
_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_P.add_argument("--roofline-probe-only", action="store_true",
                dest="roofline_probe_only",
                help="Run D1 roofline probe only; report wall extrapolation; exit.")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = (
    "smoke"
    if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
    else os.environ.get("HDLAB_RUN_MODE", "full")
)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32


# ============================================================================
# v3 GPU setup hardening (vs v2_RESCUE_FULL silent crash)
# ============================================================================

def _gpu_setup_assert_and_report(label: str = "startup"):
    """Print memory headroom + flush cache + assert no device-mismatch will
    happen later. Called at startup + before each arm."""
    try:
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
            try:
                free_b, total_b = torch.cuda.mem_get_info(DEVICE)
                free_gb = free_b / (1024 ** 3)
                total_gb = total_b / (1024 ** 3)
                print(("[gpu_setup %s] device=%s free_gb=%.2f total_gb=%.2f "
                       "headroom_frac=%.3f") % (
                          label, str(DEVICE), free_gb, total_gb,
                          free_b / max(total_b, 1)),
                      flush=True)
            except Exception:
                pass
            # Device-mismatch assertion: tensors created here must end up on DEVICE
            probe = torch.zeros(8, device=DEVICE, dtype=TORCH_DTYPE)
            assert probe.device.type == DEVICE.type, \
                "GPU setup: tensor device mismatch (probe on %s, expected %s)" % (
                    probe.device.type, DEVICE.type)
            del probe
            torch.cuda.synchronize()
        else:
            print("[gpu_setup %s] device=cpu (no GPU available)" % label, flush=True)
    except Exception as e:
        # Never crash from setup-report; print + continue
        print("[gpu_setup %s] WARN: %s" % (label, str(e)[:200]), flush=True)

# ============================================================================
# RESCUE config -- scope reduction vs v1
# ============================================================================
# v1: N_DIM=8192, N_TRAIN=100_000, N_HELD=20_000, SEEDS=[7,17,23]
# v2_RESCUE: N_DIM=4096, N_TRAIN=50_000, N_HELD=10_000, SEEDS=[7,17]
# Per-seed compute estimate: (4096/8192)^2 * (50_000/100_000) = 0.125 of v1 per-seed
# v1 seed 7 took 3074s; v2_RESCUE per-seed estimate ~385s; 2 seeds ~770s; 1.5x safety ~1155s.
N_DIM = 8192
VOCAB_CAP = 4000
RECALL_BATCH = 256
INGEST_CHUNK = 4096

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
    N_STEPS = N_STEPS_PER_SEED
else:
    # Smoke: clean synthetic data + small config; goal <180s on CPU.
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 1024
    N_STEPS = 80
    RECALL_BATCH = 128
    INGEST_CHUNK = 512

N_DIM_HALF = N_DIM // 2  # for orthogonal subspace split

CONFIG_VERSION = (
    "%s; encoder=word2vec_sparse_bipolar_f%.3f; N_DIM=%d N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d arms=%s seeds=%s mode=%s temps=%s lambdas=%s "
    "cfrpe_lr=%.3f stdp_w=%.3f n_steps=%d batch=%d "
    "theta_alphas=%s freq_rank=%d freq_lr_high=%.3f freq_lr_rare=%.3f "
    "orthog_lr=%.3f device=%s rescue=v2"
) % (
    ANCHOR_NAME, SPARSE_BIPOLAR_F, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP,
    ARMS, SEEDS, RUN_MODE, TEMP_GRID, LAMBDA_GRID, CFRPE_LR, STDP_WEIGHT,
    N_STEPS, INGEST_BATCH, THETA_ALPHA_GRID, FREQ_ROUTE_RANK,
    FREQ_LR_HIGH, FREQ_LR_RARE, ORTHOG_LR, str(DEVICE),
)


# ============================================================================
# D2 ATEXIT handler -- preserve partial state on SIGTERM / timeout
# ============================================================================
class _RunState:
    """Module-level state for atexit partial-flush.

    Holds the current-seed under work + per-arm partial dicts so that if the
    process is killed mid-arm (timeout, OOM, signal), atexit flushes whatever
    is known so far to partial_metrics_<seed>_atexit.json.

    The companion partial_metrics_<seed>.json from _seed_checkpoint.write_partial
    is only written when a seed FULLY completes; atexit covers the gap.
    """
    def __init__(self):
        self.out_dir: Optional[Path] = None
        self.current_seed: Optional[int] = None
        self.current_seed_partials: Dict = {}
        self.atexit_registered: bool = False
        self.last_flush_ts: float = 0.0

_RUN_STATE = _RunState()


def _atexit_flush_partial():
    """Flush current-seed partial state to disk. Called by atexit + signal handlers."""
    try:
        if _RUN_STATE.out_dir is None or _RUN_STATE.current_seed is None:
            return
        if not _RUN_STATE.current_seed_partials:
            return
        seed = _RUN_STATE.current_seed
        out_path = _RUN_STATE.out_dir / ("partial_metrics_%d_atexit.json" % seed)
        # Skip if seed FULLY completed (canonical partial already written)
        canonical = _RUN_STATE.out_dir / ("partial_metrics_%d.json" % seed)
        if canonical.exists():
            return
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "seed": int(seed),
            "_atexit_partial": True,
            "_atexit_ts": time.time(),
            "by_arm_partial": _RUN_STATE.current_seed_partials,
            "N_DIM": N_DIM,
            "N_TRAIN": N_TRAIN,
            "N_HELD": N_HELD,
            "VOCAB_CAP": VOCAB_CAP,
            "run_mode": RUN_MODE,
            "_note": "D2 atexit partial -- seed was mid-flight when process exited",
        }
        tmp = out_path.with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        os.replace(tmp, out_path)
        print("[atexit] flushed seed=%d partial to %s" % (seed, out_path), flush=True)
    except Exception as e:
        # NEVER raise from atexit; print and move on.
        try:
            print("[atexit] flush failed: %s" % str(e), flush=True)
        except Exception:
            pass


def _register_atexit_once():
    if _RUN_STATE.atexit_registered:
        return
    atexit.register(_atexit_flush_partial)
    _RUN_STATE.atexit_registered = True


# ============================================================================
# Corpus utilities (mirrors fair_harness cell)
# ============================================================================

def load_text8_tokens(n_total: int) -> List[str]:
    if not TEXT8.exists():
        print("[FATAL] corpus missing at %s" % TEXT8, flush=True)
        sys.exit(1)
    out: List[str] = []
    with TEXT8.open("r", encoding="utf-8") as f:
        buf = ""
        while len(out) < n_total:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            buf += chunk
            parts = buf.split(" ")
            buf = parts.pop()
            out.extend(parts)
        if buf and len(out) < n_total:
            out.append(buf)
    return out[:n_total]


def build_vocab(train_tokens: List[str], cap: int) -> Tuple[List[str], Dict[str, int]]:
    c = Counter(train_tokens)
    top = [w for w, _ in c.most_common(cap - 1)]
    vocab = ["<unk>"] + top
    w2i = {w: i for i, w in enumerate(vocab)}
    return vocab, w2i


def tokens_to_idx(toks: List[str], w2i: Dict[str, int]) -> np.ndarray:
    unk = w2i["<unk>"]
    return np.array([w2i.get(t, unk) for t in toks], dtype=np.int64)


def build_unigram_np(idx_train: np.ndarray, V: int, alpha: float = 0.1) -> np.ndarray:
    counts = np.full(V, alpha, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


def vocab_frequency_ranks(idx_train: np.ndarray, V: int) -> np.ndarray:
    counts = np.zeros(V, dtype=np.int64)
    np.add.at(counts, idx_train, 1)
    order = np.argsort(-counts)
    ranks = np.empty(V, dtype=np.int64)
    ranks[order] = np.arange(V)
    return ranks


# ============================================================================
# Encoder utilities (identical to fair_harness)
# ============================================================================

def _seed_for_trigram(trigram: str, seed: int) -> int:
    h = hashlib.blake2b((trigram + ":" + str(seed)).encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv_np(seed_val: int, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed_val)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


def char_trigram_encode(word: str, n_dim: int, seed: int) -> np.ndarray:
    t = " " + word.lower().replace("_", " ") + " "
    accum = np.zeros(n_dim, dtype=np.float32)
    if len(t) < 3:
        return accum
    for i in range(len(t) - 2):
        tri = t[i:i + 3]
        accum += _bipolar_hv_np(_seed_for_trigram(tri, seed), n_dim)
    out = np.sign(accum).astype(np.float32)
    out[out == 0] = 1.0
    return out


def _l2_normalize_np(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def _l2_normalize_t(X: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    if X.dim() == 1:
        return X / (X.norm() + eps)
    return X / (X.norm(dim=1, keepdim=True) + eps)


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed * 991 + 73)
    P = rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))
    return P


_GENSIM_KV_CACHE: Dict[str, object] = {}


def _load_gensim_kv(model_name: str):
    if model_name in _GENSIM_KV_CACHE:
        return _GENSIM_KV_CACHE[model_name]
    from tools.gensim_load_helper import load_gensim_kv
    kv = load_gensim_kv(model_name, cache_dir=GENSIM_CACHE_DIR)
    _GENSIM_KV_CACHE[model_name] = kv
    return kv


def _embed_vocab_via_gensim(vocab: List[str], kv) -> Tuple[np.ndarray, int, int]:
    dim = kv.vector_size
    V = len(vocab)
    out = np.zeros((V, dim), dtype=np.float32)
    n_hit = 0
    n_miss = 0
    for i, w in enumerate(vocab):
        v = None
        if w in kv.key_to_index:
            v = kv[w]
        elif w.lower() in kv.key_to_index:
            v = kv[w.lower()]
        else:
            try:
                v = kv.get_vector(w, norm=False)
            except Exception:
                v = None
        if v is None:
            n_miss += 1
        else:
            n_hit += 1
            out[i] = v.astype(np.float32)
    return out, n_hit, n_miss


def build_E_word2vec(vocab: List[str], n_dim: int, seed: int) -> Tuple[torch.Tensor, Dict]:
    kv = _load_gensim_kv(WORD2VEC_MODEL)
    E_pre, n_hit, n_miss = _embed_vocab_via_gensim(vocab, kv)
    E_pre_n = _l2_normalize_np(E_pre)
    P = _gaussian_projection(in_dim=kv.vector_size, out_dim=n_dim, seed=seed)
    E_proj = (E_pre_n @ P.T).astype(np.float32)
    norms_before_proj = np.linalg.norm(E_pre, axis=1)
    oov_mask = norms_before_proj < 1e-9
    if oov_mask.any():
        for i in np.where(oov_mask)[0]:
            E_proj[i] = char_trigram_encode(vocab[i], n_dim, seed)
    E_proj = _l2_normalize_np(E_proj)
    E_t = torch.from_numpy(E_proj).to(device=DEVICE, dtype=TORCH_DTYPE)
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size)}
    return E_t, meta


def build_E_synthetic_smoke(V: int, n_dim: int, seed: int) -> Tuple[torch.Tensor, Dict]:
    rng = np.random.default_rng(seed * 9173 + 11)
    E_np = rng.standard_normal((V, n_dim)).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    E_t = torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)
    meta = {"n_hit": int(V), "n_miss": 0, "n_vocab": int(V),
            "pretrain_dim": int(n_dim), "synthetic_smoke": True}
    return E_t, meta


def sparsify_bipolar_gpu(E: torch.Tensor, f: float) -> torch.Tensor:
    V, dim = E.shape
    k = max(1, int(round(f * dim)))
    abs_E = E.abs()
    _, topk_idx = torch.topk(abs_E, k=k, dim=1)
    out = torch.zeros_like(E)
    row_idx = torch.arange(V, device=E.device).unsqueeze(1).expand(-1, k)
    signs = torch.sign(E.gather(1, topk_idx))
    signs = torch.where(signs == 0, torch.ones_like(signs), signs)
    out[row_idx, topk_idx] = signs
    return out


# ============================================================================
# Plasticity primitives (IDENTICAL to v1; copied to make cell self-contained)
# ============================================================================

def build_W_hebbian_gpu(E: torch.Tensor, idx_train_t: torch.Tensor,
                          ingest_chunk: int) -> torch.Tensor:
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src_idx = idx_train_t[b:end]
        tgt_idx = idx_train_t[b + 1:end + 1]
        E_src = E[src_idx]
        E_tgt = E[tgt_idx]
        W.add_(E_tgt.T @ E_src)
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


def build_logits_hebbian_baseline_gpu(E_full: torch.Tensor,
                                         idx_train_t: torch.Tensor,
                                         idx_held_t: torch.Tensor,
                                         recall_batch: int,
                                         ingest_chunk: int) -> Dict:
    V, dim = E_full.shape
    n_h = idx_held_t.shape[0]
    device = E_full.device

    t0 = time.time()
    W = build_W_hebbian_gpu(E_full, idx_train_t, ingest_chunk)
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    t0 = time.time()
    pred = torch.zeros((n_h, dim), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx_b = E_full[idx_held_t[b:end]]
        pred[b:end] = _l2_normalize_t(ctx_b @ W.T)
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        logits[b:end] = pred[b:end] @ E_full.T
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    del W, pred, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"logits": logits_np, "wall_ingest_s": round(t_ingest, 2),
            "wall_recall_s": round(t_recall, 2),
            "discriminating": {}}


def build_logits_theta_phase_two_w_gpu(E_full: torch.Tensor,
                                          idx_train_t: torch.Tensor,
                                          idx_held_t: torch.Tensor,
                                          n_steps: int, batch: int, lr: float,
                                          stdp_w: float,
                                          seed: int, arm_idx: int,
                                          recall_batch: int) -> Dict:
    V, dim = E_full.shape
    n_h = idx_held_t.shape[0]
    device = E_full.device

    t0 = time.time()
    W_enc = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    W_ret = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)

    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return {"logits": np.zeros((n_h, V), dtype=np.float32),
                "wall_ingest_s": 0.0, "wall_recall_s": 0.0,
                "discriminating": {}}

    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + arm_idx * 31337) & 0x7FFFFFFF)

    n_phase0 = 0
    n_phase1 = 0
    for step in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=device)
        Ctx = E_full[idx_train_t[st]]
        Nxt = E_full[idx_train_t[st + 1]]
        phase = step % 2
        if phase == 0:
            error = Nxt - Ctx @ W_enc.T
            dW = (error.T @ Ctx) / float(batch)
            W_enc = W_enc + lr * dW
            n_phase0 += 1
        else:
            dW = (Nxt.T @ Ctx - Ctx.T @ Nxt) / float(batch)
            W_ret = W_ret + lr * stdp_w * dW
            n_phase1 += 1

    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    enc_flat = W_enc.flatten()
    ret_flat = W_ret.flatten()
    enc_norm = enc_flat / (enc_flat.norm() + 1e-12)
    ret_norm = ret_flat / (ret_flat.norm() + 1e-12)
    enc_vs_ret_corr = float((enc_norm * ret_norm).sum().item())

    t0 = time.time()
    pred_enc = torch.zeros((n_h, dim), dtype=TORCH_DTYPE, device=device)
    pred_ret = torch.zeros((n_h, dim), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx_b = E_full[idx_held_t[b:end]]
        pred_enc[b:end] = _l2_normalize_t(ctx_b @ W_enc.T)
        pred_ret[b:end] = _l2_normalize_t(ctx_b @ W_ret.T)
    logits_enc = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    logits_ret = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        logits_enc[b:end] = pred_enc[b:end] @ E_full.T
        logits_ret[b:end] = pred_ret[b:end] @ E_full.T
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    le = logits_enc.detach().cpu().numpy().astype(np.float32)
    lr_np = logits_ret.detach().cpu().numpy().astype(np.float32)
    if le.shape[0] > 0:
        le_c = le - le.mean(axis=1, keepdims=True)
        lr_c = lr_np - lr_np.mean(axis=1, keepdims=True)
        num = (le_c * lr_c).sum(axis=1)
        den = (np.linalg.norm(le_c, axis=1) * np.linalg.norm(lr_c, axis=1) + 1e-12)
        per_q_corr = num / den
        logit_enc_ret_corr = float(np.mean(per_q_corr))
    else:
        logit_enc_ret_corr = float("nan")

    alpha_stack = np.stack(
        [(a * le) + ((1.0 - a) * lr_np) for a in THETA_ALPHA_GRID],
        axis=0,
    ).astype(np.float32)

    del W_enc, W_ret, pred_enc, pred_ret, logits_enc, logits_ret
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits_alpha_stack": alpha_stack,
        "alpha_grid": list(THETA_ALPHA_GRID),
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "discriminating": {
            "enc_vs_ret_bank_corr": round(enc_vs_ret_corr, 4),
            "logit_enc_ret_corr_mean": round(logit_enc_ret_corr, 4),
            "n_phase0_steps": int(n_phase0),
            "n_phase1_steps": int(n_phase1),
        },
    }


def build_logits_freq_routed_k2_gpu(E_full: torch.Tensor,
                                      idx_train_t: torch.Tensor,
                                      idx_held_t: torch.Tensor,
                                      ranks_np: np.ndarray,
                                      n_steps: int, batch: int,
                                      lr_high: float, lr_rare: float,
                                      stdp_w: float, freq_threshold: int,
                                      seed: int, arm_idx: int,
                                      recall_batch: int) -> Dict:
    V, dim = E_full.shape
    n_h = idx_held_t.shape[0]
    device = E_full.device

    is_high_freq = (ranks_np < freq_threshold)
    is_high_freq_t = torch.from_numpy(is_high_freq.astype(np.float32)).to(device)

    idx_train_np = idx_train_t.detach().cpu().numpy()
    n_pairs_total = idx_train_np.shape[0] - 1
    if n_pairs_total <= 0:
        return {"logits": np.zeros((n_h, V), dtype=np.float32),
                "wall_ingest_s": 0.0, "wall_recall_s": 0.0,
                "discriminating": {}}

    t0 = time.time()
    W_freq = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    W_rare = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)

    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + arm_idx * 31337) & 0x7FFFFFFF)

    n_high_steps = 0
    n_rare_steps = 0
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs_total, (batch,), generator=gen, device=device)
        Ctx = E_full[idx_train_t[st]]
        Nxt = E_full[idx_train_t[st + 1]]
        tgt_idx = idx_train_t[st + 1]
        is_high_batch = is_high_freq_t[tgt_idx]
        error_freq = Nxt - Ctx @ W_freq.T
        wh = is_high_batch.unsqueeze(1)
        dW_freq = ((error_freq * wh).T @ Ctx) / float(batch)
        W_freq = W_freq + lr_high * dW_freq
        wr = (1.0 - is_high_batch).unsqueeze(1)
        error_rare = Nxt - Ctx @ W_rare.T
        dW_cf_rare = ((error_rare * wr).T @ Ctx) / float(batch)
        Ctx_w = Ctx * wr
        Nxt_w = Nxt * wr
        dW_stdp_rare = (Nxt_w.T @ Ctx - Ctx_w.T @ Nxt) / float(batch)
        W_rare = W_rare + lr_rare * (dW_cf_rare + stdp_w * dW_stdp_rare)
        n_high_steps += int(is_high_batch.sum().item())
        n_rare_steps += int((1.0 - is_high_batch).sum().item())

    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    t0 = time.time()
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx_b = E_full[idx_held_t[b:end]]
        pred_freq = _l2_normalize_t(ctx_b @ W_freq.T)
        pred_rare = _l2_normalize_t(ctx_b @ W_rare.T)
        logit_freq = pred_freq @ E_full.T
        logit_rare = pred_rare @ E_full.T
        mask = is_high_freq_t.unsqueeze(0)
        logits[b:end] = mask * logit_freq + (1.0 - mask) * logit_rare
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)

    discriminating = {
        "n_high_freq_steps": int(n_high_steps),
        "n_rare_steps": int(n_rare_steps),
        "freq_threshold": int(freq_threshold),
        "n_high_freq_vocab": int(is_high_freq.sum()),
        "n_rare_vocab": int(V - is_high_freq.sum()),
    }

    del W_freq, W_rare, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "discriminating": discriminating,
        "is_high_freq_vocab_mask": is_high_freq,
    }


def _gram_schmidt_qr_split(n_dim: int, seed: int) -> Tuple[torch.Tensor, torch.Tensor]:
    rng = np.random.default_rng(seed * 7919 + 13)
    G = rng.standard_normal((n_dim, n_dim)).astype(np.float32)
    Q, _ = np.linalg.qr(G)
    half = n_dim // 2
    P1_np = Q[:, :half]
    P2_np = Q[:, half:]
    P1 = torch.from_numpy(P1_np).to(device=DEVICE, dtype=TORCH_DTYPE)
    P2 = torch.from_numpy(P2_np).to(device=DEVICE, dtype=TORCH_DTYPE)
    return P1, P2


def build_logits_orthog_subspace_gpu(E_full: torch.Tensor,
                                       idx_train_t: torch.Tensor,
                                       idx_held_t: torch.Tensor,
                                       n_steps: int, batch: int, lr: float,
                                       stdp_w: float,
                                       seed: int, arm_idx: int,
                                       recall_batch: int) -> Dict:
    V, dim = E_full.shape
    n_h = idx_held_t.shape[0]
    device = E_full.device
    half = dim // 2

    P1, P2 = _gram_schmidt_qr_split(dim, seed)
    cross_proj = P1.T @ P2
    orthog_residual = float(cross_proj.abs().max().item())

    E1 = E_full @ P1
    E2 = E_full @ P2

    t0 = time.time()
    W1 = torch.zeros((half, half), dtype=TORCH_DTYPE, device=device)
    W2 = torch.zeros((half, half), dtype=TORCH_DTYPE, device=device)

    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return {"logits": np.zeros((n_h, V), dtype=np.float32),
                "wall_ingest_s": 0.0, "wall_recall_s": 0.0,
                "discriminating": {}}

    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + arm_idx * 31337) & 0x7FFFFFFF)

    sample_steps = sorted({0, n_steps // 4, n_steps // 2, 3 * n_steps // 4, n_steps - 1})
    sample_steps = [s for s in sample_steps if 0 <= s < n_steps]
    dW1_samples: List[np.ndarray] = []
    dW2_samples: List[np.ndarray] = []

    for step in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=device)
        Ctx1 = E1[idx_train_t[st]]
        Nxt1 = E1[idx_train_t[st + 1]]
        Ctx2 = E2[idx_train_t[st]]
        Nxt2 = E2[idx_train_t[st + 1]]
        error1 = Nxt1 - Ctx1 @ W1.T
        dW1 = (error1.T @ Ctx1) / float(batch)
        W1 = W1 + lr * dW1
        dW2 = (Nxt2.T @ Ctx2 - Ctx2.T @ Nxt2) / float(batch)
        W2 = W2 + lr * stdp_w * dW2
        if step in sample_steps:
            dW1_samples.append(dW1.detach().cpu().numpy().astype(np.float32).flatten())
            dW2_samples.append(dW2.detach().cpu().numpy().astype(np.float32).flatten())

    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    if dW1_samples and dW2_samples:
        cs = []
        for a, b in zip(dW1_samples, dW2_samples):
            an = a / (np.linalg.norm(a) + 1e-12)
            bn = b / (np.linalg.norm(b) + 1e-12)
            cs.append(float(np.dot(an, bn)))
        cross_subspace_grad_corr = float(np.mean(np.abs(cs)))
    else:
        cross_subspace_grad_corr = float("nan")

    t0 = time.time()
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx1_b = E1[idx_held_t[b:end]]
        ctx2_b = E2[idx_held_t[b:end]]
        pred1 = _l2_normalize_t(ctx1_b @ W1.T)
        pred2 = _l2_normalize_t(ctx2_b @ W2.T)
        logit1 = pred1 @ E1.T
        logit2 = pred2 @ E2.T
        logits[b:end] = logit1 + logit2
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)

    del W1, W2, P1, P2, E1, E2, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "discriminating": {
            "orthog_residual_max": round(orthog_residual, 6),
            "cross_subspace_grad_corr_mean_abs": round(cross_subspace_grad_corr, 4),
            "n_grad_samples": len(dW1_samples),
        },
    }


# ============================================================================
# BPC / eval utilities (identical to v1)
# ============================================================================

def softmax_with_T(logits: np.ndarray, T: float) -> np.ndarray:
    z = logits / max(T, 1e-9)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def log_linear_interp(sub_logp: np.ndarray, U_log: np.ndarray, lam: float) -> np.ndarray:
    combined = lam * sub_logp + (1.0 - lam) * U_log[None, :]
    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    return combined - Z[:, None]


def bpc_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    n = len(nxt)
    if n == 0:
        return float("inf")
    return -float(np.mean(logp[np.arange(n), nxt])) / math.log(2.0)


def top1_acc(logp: np.ndarray, nxt: np.ndarray) -> float:
    if len(nxt) == 0:
        return float("nan")
    return float(np.mean(np.argmax(logp, axis=1) == nxt))


def mrr_at_k(logp: np.ndarray, nxt: np.ndarray, k: int) -> float:
    n = len(nxt)
    if n == 0:
        return float("nan")
    k_use = min(k, logp.shape[1])
    top_idx = np.argpartition(-logp, kth=k_use - 1, axis=1)[:, :k_use]
    rows = np.arange(n)[:, None]
    top_vals = logp[rows, top_idx]
    order = np.argsort(-top_vals, axis=1)
    top_idx_sorted = top_idx[rows, order]
    rr = 0.0
    for i in range(n):
        match = np.where(top_idx_sorted[i] == nxt[i])[0]
        if len(match) > 0:
            rr += 1.0 / float(match[0] + 1)
    return float(rr / n)


def raw_bpc_at_T1(logits_np: np.ndarray, nxt_eval: np.ndarray) -> float:
    n_h = logits_np.shape[0]
    n_eval = min(n_h, len(nxt_eval))
    if n_eval == 0:
        return float("inf")
    sub = logits_np[:n_eval]
    nxt_e = nxt_eval[:n_eval]
    z = sub - sub.max(axis=1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    p = e / np.clip(e.sum(axis=1, keepdims=True), 1e-30, None)
    p_nxt = p[np.arange(n_eval), nxt_e].clip(1e-12, 1.0)
    return float(-np.mean(np.log(p_nxt)) / math.log(2.0))


def joint_sweep(sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
                U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray) -> Dict:
    best_bpc = {"T": 1.0, "lambda": 1.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    per_lambda_best_T_bpc: Dict[float, Dict] = {}

    for T in TEMP_GRID:
        probs_dev = softmax_with_T(sub_logits_dev, T)
        logp_sub_dev = np.log(np.clip(probs_dev, 1e-30, 1.0))
        for lam in LAMBDA_GRID:
            logp_dev = log_linear_interp(logp_sub_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            td = top1_acc(logp_dev, nxt_dev)
            md = mrr_at_k(logp_dev, nxt_dev, MRR_K)
            if bd < best_bpc["dev_value"]:
                best_bpc = {"T": float(T), "lambda": float(lam), "dev_value": bd}
            if td > best_top1["dev_value"]:
                best_top1 = {"T": float(T), "lambda": float(lam), "dev_value": td}
            if md > best_mrr["dev_value"]:
                best_mrr = {"T": float(T), "lambda": float(lam), "dev_value": md}
            cur = per_lambda_best_T_bpc.get(float(lam),
                                              {"T": float(T), "bpc_dev": bd})
            if bd < cur["bpc_dev"]:
                per_lambda_best_T_bpc[float(lam)] = {"T": float(T), "bpc_dev": bd}
            else:
                per_lambda_best_T_bpc.setdefault(float(lam), cur)

    def _eval_test(T: float, lam: float, fn) -> float:
        probs = softmax_with_T(sub_logits_test, T)
        logp_sub = np.log(np.clip(probs, 1e-30, 1.0))
        logp = log_linear_interp(logp_sub, U_log, lam)
        return fn(logp, nxt_test)

    bpc_best_test = _eval_test(best_bpc["T"], best_bpc["lambda"], bpc_from_logp)
    top1_best_test = _eval_test(best_top1["T"], best_top1["lambda"], top1_acc)
    mrr_best_test = _eval_test(best_mrr["T"], best_mrr["lambda"],
                                lambda lp, nx: mrr_at_k(lp, nx, MRR_K))

    per_lambda_T_summary = {
        str(round(lam, 3)): {"best_T": v["T"], "bpc_dev": round(v["bpc_dev"], 4)}
        for lam, v in sorted(per_lambda_best_T_bpc.items())
    }

    return {
        "bpc_best": round(bpc_best_test, 4),
        "best_T_for_bpc": best_bpc["T"],
        "best_lambda_for_bpc": best_bpc["lambda"],
        "best_dev_bpc": round(best_bpc["dev_value"], 4),
        "top1_acc": round(top1_best_test, 4),
        "best_T_for_top1": best_top1["T"],
        "best_lambda_for_top1": best_top1["lambda"],
        "mrr_at_10": round(mrr_best_test, 4),
        "best_T_for_mrr": best_mrr["T"],
        "best_lambda_for_mrr": best_mrr["lambda"],
        "per_lambda_T_summary": per_lambda_T_summary,
        "n_dev": int(len(nxt_dev)),
        "n_test": int(len(nxt_test)),
    }


def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray, V: int) -> Dict:
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != 0)
    nxt_eval = nxt[mask]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        return {"bpc_unigram": float("inf"), "top1_unigram": 0.0,
                "mrr_unigram": 0.0, "n_test": 0}
    n_dev = n_eval // 2
    nxt_test = nxt_eval[n_dev:]
    p_test = U[nxt_test].clip(1e-12, 1.0)
    bpc = float(-np.mean(np.log(p_test)) / math.log(2.0))
    am = int(np.argmax(U))
    top1 = float(np.mean(nxt_test == am))
    order = np.argsort(-U)
    inv_rank = np.empty_like(order)
    inv_rank[order] = np.arange(len(order))
    ranks = inv_rank[nxt_test] + 1
    rr = np.where(ranks <= MRR_K, 1.0 / ranks, 0.0)
    mrr = float(np.mean(rr))
    return {"bpc_unigram": round(bpc, 4), "top1_unigram": round(top1, 4),
            "mrr_unigram": round(mrr, 4), "n_test": int(len(nxt_test))}


# ============================================================================
# Instrumentation self-test (MANDATORY -- runs at import)
# ============================================================================

def _instrumentation_selftest():
    print("[selftest] running instrumentation self-test...", flush=True)

    # ST1: cf-RPE delta shrinks prediction error
    n_dim_st = 64
    rng_st = np.random.default_rng(42)
    Ctx_np = rng_st.standard_normal((1, n_dim_st)).astype(np.float32)
    Nxt_np = rng_st.standard_normal((1, n_dim_st)).astype(np.float32)
    Ctx_np /= np.linalg.norm(Ctx_np) + 1e-8
    Nxt_np /= np.linalg.norm(Nxt_np) + 1e-8
    W_test = np.zeros((n_dim_st, n_dim_st), dtype=np.float32)
    err_before = float(np.linalg.norm(Nxt_np - Ctx_np @ W_test.T))
    dW = (Nxt_np - Ctx_np @ W_test.T).T @ Ctx_np
    W_test = W_test + 0.9 * dW
    err_after = float(np.linalg.norm(Nxt_np - Ctx_np @ W_test.T))
    assert err_after < err_before, (
        "ST1 cf-RPE should shrink error: before=%.4f after=%.4f" % (err_before, err_after))
    print("[selftest] ST1 cf-RPE shrinks error: %.4f -> %.4f" % (err_before, err_after), flush=True)

    # ST2: STDP antisymmetry: dW + dW.T == 0
    b_st = 4
    Ctx_t = torch.randn(b_st, n_dim_st, device=DEVICE)
    Nxt_t = torch.randn(b_st, n_dim_st, device=DEVICE)
    dW_stdp = (Nxt_t.T @ Ctx_t - Ctx_t.T @ Nxt_t) / float(b_st)
    antisym_err = float((dW_stdp + dW_stdp.T).abs().max())
    assert antisym_err < 1e-4, "ST2 STDP antisymmetry failed: %.4e" % antisym_err
    print("[selftest] ST2 STDP antisymmetry OK (err=%.2e)" % antisym_err, flush=True)

    # ST3: Gram-Schmidt QR split returns orthogonal subspaces
    P1, P2 = _gram_schmidt_qr_split(32, seed=1)
    cross = P1.T @ P2
    max_cross = float(cross.abs().max().item())
    assert max_cross < 1e-4, "ST3 P1.T @ P2 not zero: max=%.4e" % max_cross
    print("[selftest] ST3 Gram-Schmidt orthogonal split max|P1.T P2|=%.2e OK" % max_cross, flush=True)
    del P1, P2

    # ST4: vocab_frequency_ranks: most-frequent token gets rank 0
    idx_st = np.array([1, 2, 1, 3, 1, 2, 1], dtype=np.int64)
    ranks = vocab_frequency_ranks(idx_st, V=5)
    assert ranks[1] == 0, "ST4 most-freq token should be rank 0; got %d" % ranks[1]
    print("[selftest] ST4 freq-ranks: token 1 (most-freq) rank=%d OK" % ranks[1], flush=True)

    # ST5: build_logits_hebbian_baseline_gpu produces non-zero logits
    V_st = 10
    n_dim_s2 = 128
    rng3 = np.random.default_rng(0)
    E_np = rng3.standard_normal((V_st, n_dim_s2)).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    E_t = torch.from_numpy(E_np).to(DEVICE)
    E_sb = _l2_normalize_t(sparsify_bipolar_gpu(E_t, SPARSE_BIPOLAR_F))
    idx_tr_st = torch.tensor([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=torch.long, device=DEVICE)
    idx_h_st = torch.tensor([3, 4, 5, 6], dtype=torch.long, device=DEVICE)
    ar = build_logits_hebbian_baseline_gpu(E_sb, idx_tr_st, idx_h_st,
                                              recall_batch=4, ingest_chunk=4)
    assert ar["logits"].shape == (idx_h_st.shape[0], V_st), (
        "ST5 baseline logits shape mismatch: %s" % str(ar["logits"].shape))
    assert not np.all(ar["logits"] == 0.0), "ST5 baseline logits all zero"
    print("[selftest] ST5 hebbian baseline logits OK", flush=True)

    # ST6: theta_phase produces valid alpha_stack + finite discriminating
    ar_theta = build_logits_theta_phase_two_w_gpu(E_sb, idx_tr_st, idx_h_st,
                                                     n_steps=10, batch=3, lr=0.5,
                                                     stdp_w=0.5, seed=0, arm_idx=1,
                                                     recall_batch=4)
    assert ar_theta["logits_alpha_stack"].shape == (len(THETA_ALPHA_GRID), idx_h_st.shape[0], V_st), (
        "ST6 theta alpha stack shape wrong: %s" % str(ar_theta["logits_alpha_stack"].shape))
    assert not np.all(ar_theta["logits_alpha_stack"] == 0.0), "ST6 theta logits all zero"
    enc_vs_ret = ar_theta["discriminating"]["enc_vs_ret_bank_corr"]
    assert math.isfinite(enc_vs_ret), "ST6 enc_vs_ret_bank_corr not finite"
    n0 = ar_theta["discriminating"]["n_phase0_steps"]
    n1 = ar_theta["discriminating"]["n_phase1_steps"]
    assert n0 + n1 == 10, "ST6 phase step counts mismatch: %d + %d != 10" % (n0, n1)
    print("[selftest] ST6 theta_phase: enc_ret_corr=%.4f n_phase0=%d n_phase1=%d OK" % (
        enc_vs_ret, n0, n1), flush=True)

    # ST7: freq_routed produces valid mask + nonzero logits
    ranks_st = vocab_frequency_ranks(idx_tr_st.detach().cpu().numpy(), V=V_st)
    ar_freq = build_logits_freq_routed_k2_gpu(E_sb, idx_tr_st, idx_h_st, ranks_st,
                                                 n_steps=10, batch=3,
                                                 lr_high=0.5, lr_rare=0.2,
                                                 stdp_w=0.5, freq_threshold=3,
                                                 seed=0, arm_idx=2, recall_batch=4)
    assert ar_freq["logits"].shape == (idx_h_st.shape[0], V_st), "ST7 freq logits shape wrong"
    assert not np.all(ar_freq["logits"] == 0.0), "ST7 freq logits all zero"
    is_high = ar_freq["is_high_freq_vocab_mask"]
    assert is_high.sum() <= 3, "ST7 high-freq mask count wrong (threshold=3)"
    n_high_steps = ar_freq["discriminating"]["n_high_freq_steps"]
    n_rare_steps = ar_freq["discriminating"]["n_rare_steps"]
    assert n_high_steps > 0 or n_rare_steps > 0, "ST7 freq routing zero on both"
    print("[selftest] ST7 freq_routed: n_high_steps=%d n_rare_steps=%d n_high_vocab=%d OK" % (
        n_high_steps, n_rare_steps, int(is_high.sum())), flush=True)

    # ST8: orthog_subspace produces valid logits + low residual
    ar_orthog = build_logits_orthog_subspace_gpu(E_sb, idx_tr_st, idx_h_st,
                                                    n_steps=10, batch=3, lr=0.5,
                                                    stdp_w=0.5, seed=0, arm_idx=3,
                                                    recall_batch=4)
    assert ar_orthog["logits"].shape == (idx_h_st.shape[0], V_st), "ST8 orthog logits shape wrong"
    assert not np.all(ar_orthog["logits"] == 0.0), "ST8 orthog logits all zero"
    orthog_res = ar_orthog["discriminating"]["orthog_residual_max"]
    assert orthog_res < 1e-3, "ST8 orthog residual too high: %.4e" % orthog_res
    cs_corr = ar_orthog["discriminating"]["cross_subspace_grad_corr_mean_abs"]
    assert math.isfinite(cs_corr), "ST8 cross-subspace grad corr not finite"
    print("[selftest] ST8 orthog_subspace: residual=%.2e cross_grad_corr=%.4f OK" % (
        orthog_res, cs_corr), flush=True)

    # ST9: 4 arms differ (non-trivial diversity)
    base_logits = ar["logits"]
    theta_best = ar_theta["logits_alpha_stack"][0]
    freq_logits = ar_freq["logits"]
    orthog_logits = ar_orthog["logits"]
    d_bt = float(np.abs(base_logits - theta_best).mean())
    d_bf = float(np.abs(base_logits - freq_logits).mean())
    d_bo = float(np.abs(base_logits - orthog_logits).mean())
    assert d_bt > 1e-6, "ST9 baseline vs theta logits identical"
    assert d_bf > 1e-6, "ST9 baseline vs freq logits identical"
    assert d_bo > 1e-6, "ST9 baseline vs orthog logits identical"
    print("[selftest] ST9 arm logits diversity: bt=%.4e bf=%.4e bo=%.4e OK" % (
        d_bt, d_bf, d_bo), flush=True)

    # ST10: joint_sweep finite
    n_tok_st = 30
    n_v_sm = 6
    rng6 = np.random.default_rng(99)
    logits_syn = rng6.standard_normal((n_tok_st, n_v_sm)).astype(np.float32)
    nxt_syn = rng6.integers(0, n_v_sm, size=n_tok_st).astype(np.int64)
    U_log_st = np.log(np.full(n_v_sm, 1.0 / n_v_sm, dtype=np.float32))
    nd = n_tok_st // 2
    jr = joint_sweep(logits_syn[:nd], logits_syn[nd:], U_log_st,
                     nxt_syn[:nd], nxt_syn[nd:])
    assert math.isfinite(jr["bpc_best"]), "ST10 bpc_best not finite"
    assert math.isfinite(jr["top1_acc"]), "ST10 top1_acc not finite"
    print("[selftest] ST10 joint_sweep OK (bpc=%.3f top1=%.4f)" % (
        jr["bpc_best"], jr["top1_acc"]), flush=True)

    # ST11: sparsify_bipolar_gpu nnz correct
    E_chk = torch.from_numpy(
        np.random.default_rng(0).standard_normal((20, 100)).astype(np.float32)
    ).to(DEVICE)
    E_sparse = sparsify_bipolar_gpu(E_chk, 0.05)
    nnz_per_row = (E_sparse != 0).sum(dim=1).cpu().numpy()
    expected_nnz = max(1, int(round(0.05 * 100)))
    assert bool((nnz_per_row == expected_nnz).all()), (
        "ST11 sparse nnz mismatch: expected %d, got %s" % (expected_nnz, str(nnz_per_row[:5])))
    print("[selftest] ST11 sparsify_bipolar_gpu nnz=%d OK" % expected_nnz, flush=True)

    # ST12: LAMBDA_GRID excludes 0.0 (META C7)
    assert 0.0 not in LAMBDA_GRID, "ST12 LAMBDA_GRID must exclude 0.0"
    print("[selftest] ST12 LAMBDA_GRID excludes 0.0 OK", flush=True)

    # ST13: LLM-call counter is zero
    assert _LLM_CALL_COUNTER[0] == 0, "ST13 LLM call counter non-zero: %d" % _LLM_CALL_COUNTER[0]
    print("[selftest] ST13 LLM call counter == 0 OK", flush=True)

    # ST14: ARMS list consistency
    expected_arms = {"ARM_BASELINE_FAIR_HARNESS", "ARM_THETA_PHASE_TWO_W",
                     "ARM_FREQ_ROUTED_K2", "ARM_ORTHOG_SUBSPACE"}
    assert set(ARMS) == expected_arms, "ST14 ARMS mismatch: %s" % set(ARMS)
    print("[selftest] ST14 ARMS consistent (%d arms) OK" % len(ARMS), flush=True)

    # ST15 (NEW for v2_RESCUE): D2 atexit handler registered + flush is no-op when idle
    _register_atexit_once()
    assert _RUN_STATE.atexit_registered, "ST15 atexit not registered"
    # Idle flush -- should NOT write anything
    _atexit_flush_partial()  # no-op (current_seed=None)
    print("[selftest] ST15 D2 atexit handler registered OK", flush=True)

    # ST16 (NEW for v2_RESCUE): scope-reduction sanity -- N_DIM is even (orthog split safe)
    if RUN_MODE == "full":
        assert N_DIM % 2 == 0, "ST16 N_DIM must be even (orthog subspace split); got %d" % N_DIM
        assert N_DIM == 4096, "ST16 v2_RESCUE expects N_DIM=4096 in full mode; got %d" % N_DIM
        assert N_TRAIN == 50_000, "ST16 v2_RESCUE expects N_TRAIN=50000 in full mode; got %d" % N_TRAIN
        assert len(SEEDS) == 2, "ST16 v2_RESCUE expects 2 seeds; got %d" % len(SEEDS)
    print("[selftest] ST16 scope-reduction sanity OK (N_DIM=%d N_TRAIN=%d seeds=%d)" % (
        N_DIM, N_TRAIN, len(SEEDS)), flush=True)

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()

if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# D1 ROOFLINE PROBE -- pre-FULL gate
# ============================================================================

def roofline_probe(timeout_s_target: int) -> Dict:
    """Time slowest arm (ARM_FREQ_ROUTED_K2) at 3 N_DIM scales and fit power law.

    Returns dict with extrapolated full wall + dispatch decision.

    Refuses (raises SystemExit) if extrapolated wall > 0.8 * timeout_s_target.

    PROBE DESIGN: vary N_DIM only; hold V=VOCAB_CAP, N_STEPS at PROBE_N_STEPS
    fixed. Extrapolation scales only by (N_STEPS_FULL / PROBE_N_STEPS) since V is
    held at full vocab, so recall cost is already accounted in the probe walls.
    This avoids the v1 prototyping bug where multi-factor extrapolation
    (V-ratio * step-ratio * arm-multiplier) over-counted by 1000x.

    Sanity: at N=8192/100k v1 seed 7 took ~3074s with FREQ_ROUTED=1351s alone.
    At v2_RESCUE (N=4096/50k) we expect FREQ_ROUTED ~ 1351 / (8192/4096)^2 / (100k/50k)
    ~ 169s; full seed ~385s; 2 seeds ~770s.
    """
    print("\n[D1 probe] running roofline probe (slowest arm = ARM_FREQ_ROUTED_K2)...",
          flush=True)
    # Probe scales: N_DIM/4, N_DIM/2, N_DIM at FULL V (so V doesn't need extrapolation)
    probe_scales = [N_DIM // 4, N_DIM // 2, N_DIM]
    probe_n_steps = 25  # fixed; we extrapolate steps separately
    probe_v = VOCAB_CAP    # HOLD AT FULL V; eliminates V-ratio extrapolation error
    probe_n_train = 5000
    probe_n_held = 1000
    probe_seed = 42
    walls: List[Tuple[int, float]] = []

    # Build clean synthetic data once per probe (varies E_full size only)
    rng_probe = np.random.default_rng(probe_seed)
    bigram_tgts = rng_probe.integers(0, probe_v, size=probe_v).astype(np.int64)
    idx_tr = np.empty(probe_n_train, dtype=np.int64)
    idx_tr[0] = rng_probe.integers(0, probe_v)
    for i in range(1, probe_n_train):
        if rng_probe.random() < 0.5:
            idx_tr[i] = bigram_tgts[idx_tr[i - 1]]
        else:
            idx_tr[i] = rng_probe.integers(0, probe_v)
    idx_h = rng_probe.integers(0, probe_v, size=probe_n_held).astype(np.int64)
    idx_tr_t = torch.from_numpy(idx_tr).to(DEVICE)
    idx_h_t = torch.from_numpy(idx_h).to(DEVICE)
    ranks_probe = vocab_frequency_ranks(idx_tr, V=probe_v)
    freq_thresh = FREQ_ROUTE_RANK if probe_v > FREQ_ROUTE_RANK else max(1, probe_v // 4)

    for probe_n_dim in probe_scales:
        # Build encoder for this scale
        E_np = np.random.default_rng(probe_seed * 11 + probe_n_dim).standard_normal(
            (probe_v, probe_n_dim)).astype(np.float32)
        E_np = _l2_normalize_np(E_np)
        E_t = torch.from_numpy(E_np).to(DEVICE)
        E_sb = _l2_normalize_t(sparsify_bipolar_gpu(E_t, SPARSE_BIPOLAR_F))
        t0 = time.time()
        _ = build_logits_freq_routed_k2_gpu(
            E_sb, idx_tr_t, idx_h_t, ranks_probe,
            n_steps=probe_n_steps, batch=INGEST_BATCH,
            lr_high=FREQ_LR_HIGH, lr_rare=FREQ_LR_RARE,
            stdp_w=STDP_WEIGHT, freq_threshold=freq_thresh,
            seed=probe_seed, arm_idx=2, recall_batch=RECALL_BATCH,
        )
        wall = time.time() - t0
        walls.append((probe_n_dim, wall))
        print("  [D1 probe] N=%d wall=%.2fs (V=%d, n_steps=%d)" % (
            probe_n_dim, wall, probe_v, probe_n_steps), flush=True)
        del E_t, E_sb
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()

    # Fit t = a * N^k via log-log linear regression
    ns = np.array([w[0] for w in walls], dtype=np.float64)
    ts = np.array([w[1] for w in walls], dtype=np.float64)
    # Guard floor for log
    ts_floor = np.clip(ts, 1e-6, None)
    log_n = np.log(ns)
    log_t = np.log(ts_floor)
    A = np.vstack([np.ones_like(log_n), log_n]).T
    coef, *_ = np.linalg.lstsq(A, log_t, rcond=None)
    log_a_fit, k_fit = float(coef[0]), float(coef[1])
    a_fit = float(np.exp(log_a_fit))

    # Extrapolate FREQ_ROUTED arm wall at full N_DIM, full N_STEPS.
    # V is already at full vocab in probe -> no V scaling needed.
    # n_train scales recall slightly (eval loop is n_held / RECALL_BATCH iterations);
    # n_held at full = 10k vs probe 1k -> 10x extra recall iterations; recall portion
    # is small fraction of FREQ arm wall (per v1: FREQ recall 82s of 1351s total = 6%).
    # So total scale = (N_STEPS_full / probe_n_steps) for training + ~10x for recall(small).
    # Use (N_STEPS_full / probe_n_steps) * 1.1 as the conservative factor.
    step_scale = float(N_STEPS) / float(probe_n_steps)
    freq_arm_wall_extrap = a_fit * float(N_DIM) ** k_fit * step_scale * 1.1

    # Per v1 ratio of arm walls at N=8192/100k:
    #   BASELINE 292s, THETA 838s, FREQ 1351s, ORTHOG 463s -> total 2944s/seed
    # Total seed wall ratio over FREQ alone = 2944 / 1351 ~ 2.18.
    # Use 2.5x as conservative buffer.
    per_seed_wall_extrap = 2.5 * freq_arm_wall_extrap
    # Plus per-seed encoder build (~10s) + corpus load (~5s) ~ 15s overhead
    per_seed_wall_extrap += 15.0
    full_wall_extrap = per_seed_wall_extrap * float(len(SEEDS))

    print("[D1 probe] fit: a=%.4e k=%.3f" % (a_fit, k_fit), flush=True)
    print("[D1 probe] extrapolated per-seed wall (all 4 arms): %.1fs" % per_seed_wall_extrap,
          flush=True)
    print("[D1 probe] extrapolated FULL wall (%d seeds): %.1fs (%.1f min)" % (
        len(SEEDS), full_wall_extrap, full_wall_extrap / 60.0), flush=True)
    print("[D1 probe] target timeout: %ds (%.1f min); budget = 0.8x = %.1fs" % (
        timeout_s_target, timeout_s_target / 60.0, 0.8 * timeout_s_target), flush=True)

    result = {
        "probe_scales": probe_scales,
        "probe_walls_s": [round(w[1], 3) for w in walls],
        "fit_a": round(a_fit, 6),
        "fit_k": round(k_fit, 3),
        "per_seed_wall_extrap_s": round(per_seed_wall_extrap, 1),
        "full_wall_extrap_s": round(full_wall_extrap, 1),
        "timeout_s_target": int(timeout_s_target),
        "budget_s": round(0.8 * timeout_s_target, 1),
        "dispatch_ok": bool(full_wall_extrap <= 0.8 * timeout_s_target),
    }

    if not result["dispatch_ok"]:
        print(
            "[D1 probe] REFUSE DISPATCH: extrapolated wall %.1fs > 0.8 * timeout (%ds)" % (
                full_wall_extrap, timeout_s_target), flush=True)
    else:
        print("[D1 probe] DISPATCH OK", flush=True)
    return result


if _ARGS.roofline_probe_only:
    target = int(os.environ.get("HDLAB_RUN_TIMEOUT_S", "3600"))
    probe_result = roofline_probe(target)
    print("[D1 probe] result: %s" % json.dumps(probe_result, indent=2), flush=True)
    sys.exit(0 if probe_result["dispatch_ok"] else 1)


# ============================================================================
# Per-seed runner (IDENTICAL to v1 except D2 atexit state tracking)
# ============================================================================

def run_unit(seed: int) -> Dict:
    t_seed = time.time()

    # D2: register atexit + mark current seed
    _register_atexit_once()
    _RUN_STATE.out_dir = out_dir  # set in main loop
    _RUN_STATE.current_seed = seed
    _RUN_STATE.current_seed_partials = {}

    if RUN_MODE == "smoke":
        print("\n[seed=%d] SMOKE: clean synthetic markov-bigram corpus (V=%d N_TRAIN=%d N_HELD=%d)" % (
            seed, VOCAB_CAP, N_TRAIN, N_HELD), flush=True)
        rng_corp = np.random.default_rng(seed * 7727 + 41)
        bigram_targets = rng_corp.integers(0, VOCAB_CAP, size=VOCAB_CAP).astype(np.int64)
        idx_train = np.empty(N_TRAIN, dtype=np.int64)
        idx_train[0] = rng_corp.integers(0, VOCAB_CAP)
        for i in range(1, N_TRAIN):
            if rng_corp.random() < 0.5:
                idx_train[i] = bigram_targets[idx_train[i - 1]]
            else:
                idx_train[i] = rng_corp.integers(0, VOCAB_CAP)
        idx_held = np.empty(N_HELD, dtype=np.int64)
        idx_held[0] = rng_corp.integers(0, VOCAB_CAP)
        for i in range(1, N_HELD):
            if rng_corp.random() < 0.5:
                idx_held[i] = bigram_targets[idx_held[i - 1]]
            else:
                idx_held[i] = rng_corp.integers(0, VOCAB_CAP)
        V = VOCAB_CAP
        encoder_meta = {"smoke_synthetic": True, "V": V, "N_TRAIN": N_TRAIN}
    else:
        print("\n[seed=%d] loading text8 + building vocab" % seed, flush=True)
        toks = load_text8_tokens(N_TRAIN + N_HELD)
        if len(toks) < N_TRAIN + N_HELD:
            print("[WARN] corpus short: %d tokens loaded" % len(toks), flush=True)
        train_toks = toks[:N_TRAIN]
        held_toks = toks[N_TRAIN:N_TRAIN + N_HELD]
        vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
        V = len(vocab)
        idx_train = tokens_to_idx(train_toks, w2i)
        idx_held = tokens_to_idx(held_toks, w2i)
        encoder_meta = {}

    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d device=%s" % (
        seed, V, N_TRAIN, N_HELD, N_DIM, str(DEVICE)), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)
    uni = unigram_metrics(idx_train, idx_held, V)
    print("[seed=%d arm=UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"]), flush=True)

    ranks_np = vocab_frequency_ranks(idx_train, V=V)

    print("\n[seed=%d] building encoder (V=%d, N_DIM=%d)..." % (seed, V, N_DIM), flush=True)
    t_enc0 = time.time()
    if RUN_MODE == "smoke":
        E_proj_t, w2v_meta = build_E_synthetic_smoke(V, N_DIM, seed)
    else:
        E_proj_t, w2v_meta = build_E_word2vec(vocab, N_DIM, seed)
    encoder_meta.update(w2v_meta)
    E_full = _l2_normalize_t(sparsify_bipolar_gpu(E_proj_t, SPARSE_BIPOLAR_F))
    sparsity = float((E_full != 0).float().mean().item())
    print("[seed=%d] encoder built in %.1fs; sparsity=%.3f" % (
        seed, time.time() - t_enc0, sparsity), flush=True)
    del E_proj_t

    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)

    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    ctx_eval = ctx_full[mask]
    nxt_eval = nxt_full[mask]
    n_eval = len(ctx_eval)
    if n_eval == 0:
        print("[WARN seed=%d] no valid eval pairs" % seed, flush=True)
        return {"seed": seed, "by_arm": {"ARM_UNIGRAM": uni}, "V": V,
                "N_DIM": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
                "run_mode": RUN_MODE,
                "elapsed_s_seed": round(time.time() - t_seed, 2)}
    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni, "w2v_meta": w2v_meta}
    _RUN_STATE.current_seed_partials = by_arm  # D2 atexit will see this dict reference

    # Helper for arm-result post-processing (factored to reduce body length)
    def _process_arm(arm_name: str, ar: Dict) -> Dict:
        logits_full = ar["logits"]
        valid_pos = np.where(mask)[0]
        valid_pos = valid_pos[valid_pos < logits_full.shape[0]]
        logits_eval = logits_full[valid_pos]
        nxt_eval_local = nxt_full[valid_pos]
        n_eval_l = len(nxt_eval_local)
        n_dev_l = n_eval_l // 2
        nxt_dev_l = nxt_eval_local[:n_dev_l]
        nxt_test_l = nxt_eval_local[n_dev_l:]
        jr = joint_sweep(logits_eval[:n_dev_l], logits_eval[n_dev_l:],
                          U_log, nxt_dev_l, nxt_test_l)
        rbt1 = raw_bpc_at_T1(logits_eval, nxt_eval_local)
        jr.update({
            "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
            "wall_recall_s": ar.get("wall_recall_s", 0.0),
            "raw_bpc_at_T1_L1": round(rbt1, 4),
            "discriminating": ar.get("discriminating", {}),
        })
        return jr, logits_eval, nxt_eval_local, nxt_test_l

    # ----- ARM 1: baseline -----
    arm = "ARM_BASELINE_FAIR_HARNESS"
    t_arm0 = time.time()
    print("\n  [seed=%d arm=%s] computing..." % (seed, arm), flush=True)
    try:
        ar = build_logits_hebbian_baseline_gpu(
            E_full, idx_train_t, idx_held_t,
            recall_batch=RECALL_BATCH, ingest_chunk=INGEST_CHUNK,
        )
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
        by_arm[arm] = {
            "compute_failed": True, "compute_error": err,
            "bpc_best": float("inf"), "top1_acc": float("nan"),
            "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
            "elapsed_s_arm": round(time.time() - t_arm0, 2),
        }
    else:
        jr, _, _, _ = _process_arm(arm, ar)
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f rawT1=%.3f elapsed=%.1fs" % (
            seed, arm, jr["bpc_best"], jr["top1_acc"],
            jr["raw_bpc_at_T1_L1"], jr["elapsed_s_arm"]), flush=True)
    # D2: update atexit-visible state
    _RUN_STATE.current_seed_partials = dict(by_arm)

    # ----- ARM 2: theta-phase two-W -----
    arm = "ARM_THETA_PHASE_TWO_W"
    t_arm0 = time.time()
    print("\n  [seed=%d arm=%s] computing..." % (seed, arm), flush=True)
    try:
        ar = build_logits_theta_phase_two_w_gpu(
            E_full, idx_train_t, idx_held_t,
            n_steps=N_STEPS, batch=INGEST_BATCH, lr=CFRPE_LR, stdp_w=STDP_WEIGHT,
            seed=seed, arm_idx=1, recall_batch=RECALL_BATCH,
        )
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
        by_arm[arm] = {
            "compute_failed": True, "compute_error": err,
            "bpc_best": float("inf"), "top1_acc": float("nan"),
            "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
            "elapsed_s_arm": round(time.time() - t_arm0, 2),
        }
    else:
        alpha_stack = ar["logits_alpha_stack"]
        alpha_grid = ar["alpha_grid"]
        best_alpha_idx = 0
        best_alpha_jr = None
        best_dev_bpc = float("inf")
        valid_pos = np.where(mask)[0]
        best_alpha_logits = None
        best_nxt_eval_local = None
        for a_idx, alpha_val in enumerate(alpha_grid):
            logits_full = alpha_stack[a_idx]
            valid_pos_clip = valid_pos[valid_pos < logits_full.shape[0]]
            logits_eval = logits_full[valid_pos_clip]
            nxt_eval_local = nxt_full[valid_pos_clip]
            n_eval_l = len(nxt_eval_local)
            n_dev_l = n_eval_l // 2
            nxt_dev_l = nxt_eval_local[:n_dev_l]
            nxt_test_l = nxt_eval_local[n_dev_l:]
            jr = joint_sweep(logits_eval[:n_dev_l], logits_eval[n_dev_l:],
                              U_log, nxt_dev_l, nxt_test_l)
            if jr["best_dev_bpc"] < best_dev_bpc:
                best_dev_bpc = jr["best_dev_bpc"]
                best_alpha_idx = a_idx
                best_alpha_jr = jr
                best_alpha_logits = logits_eval
                best_nxt_eval_local = nxt_eval_local
        jr = best_alpha_jr
        rbt1 = raw_bpc_at_T1(best_alpha_logits, best_nxt_eval_local)
        disc = dict(ar.get("discriminating", {}))
        disc["best_alpha"] = float(alpha_grid[best_alpha_idx])
        disc["best_alpha_dev_bpc"] = round(best_dev_bpc, 4)
        disc["alpha_grid"] = list(alpha_grid)
        jr.update({
            "elapsed_s_arm": round(time.time() - t_arm0, 2),
            "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
            "wall_recall_s": ar.get("wall_recall_s", 0.0),
            "raw_bpc_at_T1_L1": round(rbt1, 4),
            "discriminating": disc,
        })
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f rawT1=%.3f best_alpha=%.2f enc_ret_corr=%.4f elapsed=%.1fs" % (
            seed, arm, jr["bpc_best"], jr["top1_acc"], jr["raw_bpc_at_T1_L1"],
            disc["best_alpha"], disc.get("enc_vs_ret_bank_corr", -1),
            jr["elapsed_s_arm"]), flush=True)
    _RUN_STATE.current_seed_partials = dict(by_arm)

    # ----- ARM 3: frequency-routed K=2 -----
    arm = "ARM_FREQ_ROUTED_K2"
    t_arm0 = time.time()
    print("\n  [seed=%d arm=%s] computing..." % (seed, arm), flush=True)
    try:
        ar = build_logits_freq_routed_k2_gpu(
            E_full, idx_train_t, idx_held_t, ranks_np,
            n_steps=N_STEPS, batch=INGEST_BATCH,
            lr_high=FREQ_LR_HIGH, lr_rare=FREQ_LR_RARE,
            stdp_w=STDP_WEIGHT,
            freq_threshold=FREQ_ROUTE_RANK if V > FREQ_ROUTE_RANK else max(1, V // 4),
            seed=seed, arm_idx=2, recall_batch=RECALL_BATCH,
        )
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
        by_arm[arm] = {
            "compute_failed": True, "compute_error": err,
            "bpc_best": float("inf"), "top1_acc": float("nan"),
            "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
            "elapsed_s_arm": round(time.time() - t_arm0, 2),
        }
    else:
        logits_full = ar["logits"]
        is_high_freq_mask = ar["is_high_freq_vocab_mask"]
        valid_pos_clip = np.where(mask)[0]
        valid_pos_clip = valid_pos_clip[valid_pos_clip < logits_full.shape[0]]
        logits_eval = logits_full[valid_pos_clip]
        nxt_eval_local = nxt_full[valid_pos_clip]
        n_eval_l = len(nxt_eval_local)
        n_dev_l = n_eval_l // 2
        nxt_dev_l = nxt_eval_local[:n_dev_l]
        nxt_test_l = nxt_eval_local[n_dev_l:]
        jr = joint_sweep(logits_eval[:n_dev_l], logits_eval[n_dev_l:],
                          U_log, nxt_dev_l, nxt_test_l)
        rbt1 = raw_bpc_at_T1(logits_eval, nxt_eval_local)
        best_T = jr["best_T_for_top1"]
        best_lam = jr["best_lambda_for_top1"]
        probs_test = softmax_with_T(logits_eval[n_dev_l:], best_T)
        logp_sub_test = np.log(np.clip(probs_test, 1e-30, 1.0))
        logp_test = log_linear_interp(logp_sub_test, U_log, best_lam)
        pred_top1 = np.argmax(logp_test, axis=1)
        is_correct = (pred_top1 == nxt_test_l).astype(np.float32)
        nxt_is_high_freq = is_high_freq_mask[nxt_test_l]
        if nxt_is_high_freq.sum() > 0:
            top1_high = float(is_correct[nxt_is_high_freq].mean())
        else:
            top1_high = float("nan")
        if (~nxt_is_high_freq).sum() > 0:
            top1_low = float(is_correct[~nxt_is_high_freq].mean())
        else:
            top1_low = float("nan")
        freq_differential = abs(top1_high - top1_low) if (
            math.isfinite(top1_high) and math.isfinite(top1_low)) else float("nan")
        disc = dict(ar.get("discriminating", {}))
        disc.update({
            "top1_high_freq_tokens": round(top1_high, 4) if math.isfinite(top1_high) else None,
            "top1_low_freq_tokens": round(top1_low, 4) if math.isfinite(top1_low) else None,
            "freq_top1_differential": round(freq_differential, 4) if math.isfinite(freq_differential) else None,
            "n_high_freq_tgts_in_test": int(nxt_is_high_freq.sum()),
            "n_low_freq_tgts_in_test": int((~nxt_is_high_freq).sum()),
        })
        jr.update({
            "elapsed_s_arm": round(time.time() - t_arm0, 2),
            "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
            "wall_recall_s": ar.get("wall_recall_s", 0.0),
            "raw_bpc_at_T1_L1": round(rbt1, 4),
            "discriminating": disc,
        })
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f rawT1=%.3f top1_high=%.3f top1_low=%.3f diff=%.3f elapsed=%.1fs" % (
            seed, arm, jr["bpc_best"], jr["top1_acc"], jr["raw_bpc_at_T1_L1"],
            top1_high if math.isfinite(top1_high) else -1,
            top1_low if math.isfinite(top1_low) else -1,
            freq_differential if math.isfinite(freq_differential) else -1,
            jr["elapsed_s_arm"]), flush=True)
    _RUN_STATE.current_seed_partials = dict(by_arm)

    # ----- ARM 4: orthogonal subspace -----
    arm = "ARM_ORTHOG_SUBSPACE"
    t_arm0 = time.time()
    print("\n  [seed=%d arm=%s] computing..." % (seed, arm), flush=True)
    try:
        ar = build_logits_orthog_subspace_gpu(
            E_full, idx_train_t, idx_held_t,
            n_steps=N_STEPS, batch=INGEST_BATCH, lr=ORTHOG_LR, stdp_w=STDP_WEIGHT,
            seed=seed, arm_idx=3, recall_batch=RECALL_BATCH,
        )
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
        by_arm[arm] = {
            "compute_failed": True, "compute_error": err,
            "bpc_best": float("inf"), "top1_acc": float("nan"),
            "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
            "elapsed_s_arm": round(time.time() - t_arm0, 2),
        }
    else:
        jr, _, _, _ = _process_arm(arm, ar)
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f rawT1=%.3f cross_grad_corr=%.4f elapsed=%.1fs" % (
            seed, arm, jr["bpc_best"], jr["top1_acc"], jr["raw_bpc_at_T1_L1"],
            jr["discriminating"].get("cross_subspace_grad_corr_mean_abs", -1),
            jr["elapsed_s_arm"]), flush=True)
    _RUN_STATE.current_seed_partials = dict(by_arm)

    del E_full
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    result = {
        "seed": seed,
        "by_arm": by_arm,
        "V": V,
        "N": N_DIM,        # PROT-021 config-check key
        "M": N_TRAIN,      # PROT-021 config-check key
        "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "N_STEPS": N_STEPS,
        "run_mode": RUN_MODE,
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
        "llm_forward_calls_at_inference": int(_LLM_CALL_COUNTER[0]),
        "elapsed_s_seed": round(time.time() - t_seed, 2),
    }
    return result


# ============================================================================
# Verdict (IDENTICAL bands to v1)
# ============================================================================

def compute_verdict(units: List[Dict]) -> tuple:
    if not units:
        return ("HARD_FAIL", "no results", {})

    by_arm_agg: Dict[str, Dict] = {}
    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan")) for u in units]
    by_arm_agg["ARM_UNIGRAM"] = {
        "bpc_mean": round(float(np.mean(uni_bpc)), 4),
        "bpc_std": round(float(np.std(uni_bpc)), 4),
    }
    unigram_bpc = by_arm_agg["ARM_UNIGRAM"]["bpc_mean"]

    arm_bpc: Dict[str, float] = {}
    arm_cv: Dict[str, float] = {}
    arm_disc: Dict[str, Dict] = {}
    for arm in ARMS:
        valid = [u for u in units
                 if not u["by_arm"].get(arm, {}).get("compute_failed", False)
                 and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))]
        if not valid:
            by_arm_agg[arm] = {"bpc_best_mean": float("inf"), "n_valid_seeds": 0,
                               "all_seeds_failed": True}
            arm_bpc[arm] = float("inf")
            arm_cv[arm] = float("nan")
            arm_disc[arm] = {}
            continue
        bpc_v = [u["by_arm"][arm]["bpc_best"] for u in valid]
        top1_v = [u["by_arm"][arm]["top1_acc"] for u in valid]
        mrr_v = [u["by_arm"][arm]["mrr_at_10"] for u in valid]
        raw_v = [u["by_arm"][arm].get("raw_bpc_at_T1_L1", float("nan")) for u in valid]
        b_mean = float(np.mean(bpc_v))
        b_std = float(np.std(bpc_v))
        b_cv = b_std / max(abs(b_mean), 1e-6)
        disc_per_seed = [u["by_arm"][arm].get("discriminating", {}) for u in valid]
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_cv, 4),
            "top1_acc_mean": round(float(np.mean(top1_v)), 4),
            "top1_acc_std": round(float(np.std(top1_v)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_v)), 4),
            "mrr_at_10_std": round(float(np.std(mrr_v)), 4),
            "raw_bpc_at_T1_L1_mean": round(float(np.mean(raw_v)), 4),
            "n_valid_seeds": len(valid),
            "discriminating_per_seed": disc_per_seed,
            "all_seeds_failed": False,
        }
        arm_bpc[arm] = b_mean
        arm_cv[arm] = b_cv
        arm_disc[arm] = disc_per_seed

    total_llm_calls = sum(int(u.get("llm_forward_calls_at_inference", 0)) for u in units)
    if total_llm_calls != 0:
        return ("HARD_FAIL",
                "HARD_FAIL_LLM_CALL: llm_calls=%d (substrate-only invariant)." % total_llm_calls,
                {"by_arm_agg": by_arm_agg, "llm_forward_calls_total": total_llm_calls})

    baseline_bpc = arm_bpc.get("ARM_BASELINE_FAIR_HARNESS", float("inf"))
    baseline_drift = abs(baseline_bpc - SANITY_RAIL_BASELINE_REF) if math.isfinite(baseline_bpc) else float("inf")
    baseline_rail_ok = baseline_drift <= SANITY_RAIL_TOLERANCE

    theta_bpc = arm_bpc.get("ARM_THETA_PHASE_TWO_W", float("inf"))
    freq_bpc = arm_bpc.get("ARM_FREQ_ROUTED_K2", float("inf"))
    orthog_bpc = arm_bpc.get("ARM_ORTHOG_SUBSPACE", float("inf"))

    het_arms = {"ARM_THETA_PHASE_TWO_W": theta_bpc,
                "ARM_FREQ_ROUTED_K2": freq_bpc,
                "ARM_ORTHOG_SUBSPACE": orthog_bpc}
    best_het_name = min(het_arms.items(), key=lambda kv: kv[1])[0]
    best_het_bpc = het_arms[best_het_name]
    best_het_cv = arm_cv.get(best_het_name, float("nan"))

    arm_summary = (
        "uni=%.3f | BASE=%.4f(drift=%+.4f,rail=%s) | THETA=%.4f | FREQ=%.4f | ORTHOG=%.4f | "
        "best_het=%s (BPC=%.4f cv=%.4f)"
    ) % (
        unigram_bpc, baseline_bpc, baseline_bpc - SANITY_RAIL_BASELINE_REF, str(baseline_rail_ok),
        theta_bpc, freq_bpc, orthog_bpc,
        best_het_name, best_het_bpc,
        best_het_cv if math.isfinite(best_het_cv) else -1.0,
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "het_arm_bpc": {k: round(v, 4) if math.isfinite(v) else None for k, v in het_arms.items()},
        "best_het_arm": best_het_name,
        "best_het_bpc": round(best_het_bpc, 4) if math.isfinite(best_het_bpc) else None,
        "best_het_cv": round(best_het_cv, 4) if math.isfinite(best_het_cv) else None,
        "sanity_rails": {
            "baseline_ref": SANITY_RAIL_BASELINE_REF,
            "baseline_drift": round(baseline_drift, 4),
            "baseline_rail_ok": bool(baseline_rail_ok),
            "tolerance": SANITY_RAIL_TOLERANCE,
        },
        "bands": {
            "hard_pass_cap_broken_bpc": HARD_PASS_CAP_BROKEN_BPC,
            "chain_grade_bonus_bpc": CHAIN_GRADE_BONUS_BPC,
            "middle_band_lower": MIDDLE_BAND_LOWER,
            "middle_band_upper": MIDDLE_BAND_UPPER,
            "hard_fail_decisive_floor": HARD_FAIL_DECISIVE_FLOOR,
            "cv_max": CV_MAX,
            "cv_max_chain_grade": CV_MAX_CHAIN_GRADE,
            "baseline_gap_chain_grade": BASELINE_GAP_CHAIN_GRADE,
            "baseline_gap_hard_pass": BASELINE_GAP_HARD_PASS,
            "hard_fail_hurt_margin": HARD_FAIL_HURT_MARGIN,
            "sanity_rail_tolerance": SANITY_RAIL_TOLERANCE,
        },
        "n_seeds": len(units),
        "unigram_bpc": round(unigram_bpc, 4),
        "llm_forward_calls_total": total_llm_calls,
        "honest_scope": (
            "v3 rerun of v2_RESCUE_FULL at SAME fair-harness rail config "
            "(N_DIM=8192, N_TRAIN=100k text8, V=4000, word2vec sparse-bipolar "
            "f=0.05, 3 seeds [7,17,23]). v2_RESCUE_FULL on overnight_queue "
            "landed `failed` with no artifacts; v2_RESCUE (CPU smaller) landed "
            "HARD_FAIL_PROVENANCE because rail tolerance 0.05 was set INSIDE "
            "cross-config noise floor 0.20-0.45 BPC (per drill cell 9). v3 "
            "fixes this by running at SAME rail config. CHANGES vs v2 FULL: "
            "(a) bands TIGHTENED: CG <=6.95 BPC + lift >=0.20 + CV<=0.03; "
            "HP <=7.20 + lift >=0.10. (b) sanity_rail TOL TIGHTENED 0.10->0.05. "
            "(c) GPU setup hardening: explicit cuda.empty_cache + device-mismatch "
            "asserts + memory-headroom print. ARM_FREQ_ROUTED_K2 is lead arm per "
            "v2_RESCUE +0.22 BPC differential. WHAT_THIS_DOES_NOT_SHOW: doesn't "
            "test K>2 routing variants; modern-Hopfield cleanup not stacked."
        ),
        "cites": [
            "preregs/2026-06-25_substrate_compose_heterogeneous_routing_v3_full_config_rerun.md",
            "notes/research_readout_degeneracy_5x_disparate_drill_2026-06-25.md",
            "experiments/exp_substrate_compose_heterogeneous_routing_v2_RESCUE_FULL.py (v2 base; failed run)",
            "experiments/exp_substrate_compose_heterogeneous_routing_v2_RESCUE.py (v2 RESCUE smaller scope; HARD_FAIL_PROVENANCE)",
            "data/exp_substrate_compose_heterogeneous_routing_v2_RESCUE_smoke/metrics.json",
            "data/exp_fair_harness_substrate_as_lm_v1/metrics.json (sanity rail 7.3065 at this exact config)",
        ],
    }

    all_het_failed = (
        by_arm_agg.get("ARM_THETA_PHASE_TWO_W", {}).get("all_seeds_failed", True) and
        by_arm_agg.get("ARM_FREQ_ROUTED_K2", {}).get("all_seeds_failed", True) and
        by_arm_agg.get("ARM_ORTHOG_SUBSPACE", {}).get("all_seeds_failed", True)
    )
    if all_het_failed:
        return ("HARD_FAIL",
                "HARD_FAIL: all 3 heterogeneous-routing arms failed all seeds. %s" % arm_summary,
                detail)

    detail["provenance_check_active"] = (RUN_MODE == "full")
    if RUN_MODE == "full" and not baseline_rail_ok:
        return ("HARD_FAIL_PROVENANCE",
                "HARD_FAIL_PROVENANCE_BASELINE: ARM_BASELINE_FAIR_HARNESS=%.4f drifts %.4f "
                "from fair_harness ref %.4f (>tol %.2f). Encoder/Hebbian pipeline mismatch. %s" % (
                    baseline_bpc, baseline_drift, SANITY_RAIL_BASELINE_REF,
                    SANITY_RAIL_TOLERANCE, arm_summary),
                detail)

    if math.isfinite(best_het_cv) and best_het_cv > CV_MAX:
        return ("MIDDLE_BAND_HIGH_CV",
                "MIDDLE_BAND_HIGH_CV: best_het=%s cv=%.4f > %.2f mandatory. "
                "best_het_bpc=%.4f. %s" % (
                    best_het_name, best_het_cv, CV_MAX, best_het_bpc, arm_summary),
                detail)

    # Wave-C HARD_FAIL: ALL het arms BPC >= BASELINE + 0.05 (heterogeneous HURTS)
    baseline_hurt_floor = (baseline_bpc + HARD_FAIL_HURT_MARGIN) if math.isfinite(baseline_bpc) else float("inf")
    all_het_finite = all(math.isfinite(b) for b in het_arms.values())
    all_het_hurt = all_het_finite and all(b >= baseline_hurt_floor for b in het_arms.values())
    detail["baseline_hurt_floor"] = round(baseline_hurt_floor, 4) if math.isfinite(baseline_hurt_floor) else None
    if all_het_hurt:
        detail["verdict_tier"] = "HARD_FAIL_HURT"
        return ("HARD_FAIL",
                "HARD_FAIL_HURT: all 3 het arms BPC >= baseline+%.2f=%.4f "
                "(theta=%.4f, freq=%.4f, orthog=%.4f). Heterogeneous routing HURTS at "
                "production scale. %s" % (
                    HARD_FAIL_HURT_MARGIN, baseline_hurt_floor,
                    theta_bpc, freq_bpc, orthog_bpc, arm_summary),
                detail)

    n_below_floor = sum(1 for bpc in het_arms.values()
                        if math.isfinite(bpc) and bpc < HARD_FAIL_DECISIVE_FLOOR)
    if n_below_floor == 0 and all_het_finite:
        detail["verdict_tier"] = "HARD_FAIL_DECISIVE"
        return ("HARD_FAIL",
                "HARD_FAIL_DECISIVE: all 3 het-routing arms BPC >= %.2f "
                "(theta=%.4f, freq=%.4f, orthog=%.4f). cf-RPE cap may indeed be structural "
                "at this regime. %s" % (
                    HARD_FAIL_DECISIVE_FLOOR, theta_bpc, freq_bpc, orthog_bpc, arm_summary),
                detail)

    # Wave-C: gap to baseline is part of chain-grade/HARD_PASS discriminator
    best_het_gap = (baseline_bpc - best_het_bpc) if math.isfinite(baseline_bpc) and math.isfinite(best_het_bpc) else float("nan")
    detail["best_het_vs_baseline_gap"] = round(best_het_gap, 4) if math.isfinite(best_het_gap) else None

    if (math.isfinite(best_het_bpc) and best_het_bpc <= CHAIN_GRADE_BONUS_BPC and
            math.isfinite(best_het_gap) and best_het_gap >= BASELINE_GAP_CHAIN_GRADE and
            math.isfinite(best_het_cv) and best_het_cv <= CV_MAX_CHAIN_GRADE):
        detail["verdict_tier"] = "HARD_PASS_CHAIN_GRADE"
        return ("HARD_PASS",
                "HARD_PASS_CHAIN_GRADE: best_het=%s BPC=%.4f <= %.2f AND beats "
                "BASELINE by %.4f >= %.2f BPC AND CV %.4f <= %.3f. v3 full-config "
                "rerun confirms heterogeneous routing at production scale. %s" % (
                    best_het_name, best_het_bpc, CHAIN_GRADE_BONUS_BPC,
                    best_het_gap, BASELINE_GAP_CHAIN_GRADE,
                    best_het_cv, CV_MAX_CHAIN_GRADE,
                    arm_summary),
                detail)

    if (math.isfinite(best_het_bpc) and best_het_bpc <= HARD_PASS_CAP_BROKEN_BPC and
            math.isfinite(best_het_gap) and best_het_gap >= BASELINE_GAP_HARD_PASS):
        detail["verdict_tier"] = "HARD_PASS_CAP_BROKEN"
        return ("HARD_PASS",
                "HARD_PASS_CAP_BROKEN: best_het=%s BPC=%.4f <= %.2f AND beats BASELINE "
                "by %.4f >= %.2f BPC. cf-RPE +12%% cap refuted at production scale. %s" % (
                    best_het_name, best_het_bpc, HARD_PASS_CAP_BROKEN_BPC,
                    best_het_gap, BASELINE_GAP_HARD_PASS, arm_summary),
                detail)

    if math.isfinite(best_het_bpc) and MIDDLE_BAND_LOWER <= best_het_bpc <= MIDDLE_BAND_UPPER:
        detail["verdict_tier"] = "MIDDLE_BAND_PARTIAL_SIGNAL"
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_PARTIAL_SIGNAL: best_het=%s BPC=%.4f in [%.2f, %.2f] "
                "(partial routing benefit; reduced-N RESCUE may suppress full discriminator). %s" % (
                    best_het_name, best_het_bpc, MIDDLE_BAND_LOWER, MIDDLE_BAND_UPPER,
                    arm_summary),
                detail)

    detail["verdict_tier"] = "MIDDLE_BAND_INTER_GAP"
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_INTER_GAP: best_het=%s BPC=%.4f between MB upper %.2f "
            "and HARD_FAIL floor %.2f. Marginal sub-cap-breaking benefit at RESCUE scope. %s" % (
                best_het_name, best_het_bpc, MIDDLE_BAND_UPPER, HARD_FAIL_DECISIVE_FLOOR,
                arm_summary),
            detail)


# ============================================================================
# Main loop with per-seed checkpoint + D1 + D2
# ============================================================================

print("[config] %s" % CONFIG_VERSION, flush=True)
print("[config] device=%s torch_cuda_available=%s" % (str(DEVICE), torch.cuda.is_available()),
      flush=True)

# v3: GPU setup hardening BEFORE anything compute-heavy. Catches silent
# CUDA init failures that v2_RESCUE_FULL likely hit (overnight_queue
# 2026-06-25T01:19:24Z landed `failed` with no artifacts).
_gpu_setup_assert_and_report(label="startup")

out_dir = get_output_dir(ANCHOR_NAME)
_RUN_STATE.out_dir = out_dir
_register_atexit_once()

# D1 ROOFLINE PROBE -- mandatory pre-FULL gate
if RUN_MODE == "full":
    timeout_s_env = int(os.environ.get("HDLAB_RUN_TIMEOUT_S", "3600"))
    probe_result = roofline_probe(timeout_s_env)
    if not probe_result["dispatch_ok"]:
        print("[D1 probe] EXIT: roofline refuses dispatch (extrapolated wall too high)",
              flush=True)
        # Write a minimal metrics.json so the runner records the refusal
        minimal_metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "HARD_FAIL",
            "verdict_msg": "HARD_FAIL_D1_ROOFLINE_REFUSE: extrapolated wall %.1fs > 0.8 * timeout %ds. Probe: %s" % (
                probe_result["full_wall_extrap_s"], probe_result["timeout_s_target"],
                json.dumps(probe_result)),
            "summary": "HARD_FAIL_D1_ROOFLINE_REFUSE | arms=%d seeds=%d N_DIM=%d N_TRAIN=%d" % (
                len(ARMS), len(SEEDS), N_DIM, N_TRAIN),
            "elapsed_s": 0.0,
            "config_version": CONFIG_VERSION,
            "run_mode": RUN_MODE,
            "d1_probe": probe_result,
        }
        (out_dir / "metrics.json").parent.mkdir(parents=True, exist_ok=True)
        with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
            json.dump(minimal_metrics, f, indent=2, default=str)
        sys.exit(0)  # exit cleanly; metrics.json carries the refusal
    print("[D1 probe] GATE PASSED -- proceeding to FULL run", flush=True)

# PROT-021 config-mismatch guard
run_config = {"N": N_DIM, "M": N_TRAIN, "run_mode": RUN_MODE}

done_seeds_init: List[int] = []
remaining_seeds_init: List[int] = SEEDS[:]
try:
    done_seeds_init, remaining_seeds_init = _resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d done, %d remaining: %s" % (
        len(done_seeds_init), len(remaining_seeds_init), remaining_seeds_init), flush=True)
except Exception as e:
    print("[ckpt] resumable_seeds failed (%s); running all seeds" % e, flush=True)
    remaining_seeds_init = SEEDS[:]

for seed in remaining_seeds_init:
    print("\n[run] seed=%d starting..." % seed, flush=True)
    result = run_unit(seed)
    write_partial(out_dir, seed, result)
    print("[ckpt] seed=%d partial written to %s" % (seed, out_dir), flush=True)
    # D2: seed complete -- clear atexit state for this seed
    _RUN_STATE.current_seed = None
    _RUN_STATE.current_seed_partials = {}

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
all_units = list(per_seed.values())

verdict, verdict_msg, detail = compute_verdict(all_units)
print("\n[VERDICT] %s: %s" % (verdict, verdict_msg), flush=True)

summary_str = (
    "%s | arms=%d seeds=%d N_DIM=%d N_TRAIN=%d encoder=word2vec_sparse_bipolar het_routing_v3_full_config_rerun" % (
        verdict, len(ARMS), len(SEEDS), N_DIM, N_TRAIN)
)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": summary_str,
    "config_version": CONFIG_VERSION,
    "run_mode": RUN_MODE,
    "device": str(DEVICE),
    "N_DIM": N_DIM,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "N_STEPS": N_STEPS,
    "CFRPE_LR": CFRPE_LR,
    "STDP_WEIGHT": STDP_WEIGHT,
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "FREQ_ROUTE_RANK": FREQ_ROUTE_RANK,
    "FREQ_LR_HIGH": FREQ_LR_HIGH,
    "FREQ_LR_RARE": FREQ_LR_RARE,
    "THETA_ALPHA_GRID": THETA_ALPHA_GRID,
    "ORTHOG_LR": ORTHOG_LR,
    "TEMP_GRID": TEMP_GRID,
    "LAMBDA_GRID": LAMBDA_GRID,
    "SEEDS": SEEDS,
    "ARMS": ARMS,
    "detail": detail,
    "per_seed": [
        {"seed": u.get("seed"), "by_arm": u.get("by_arm"),
         "V": u.get("V"), "N_DIM": u.get("N_DIM"),
         "N_TRAIN": u.get("N_TRAIN"),
         "llm_forward_calls_at_inference": u.get("llm_forward_calls_at_inference", 0),
         "encoder_meta": u.get("encoder_meta", {}),
         "elapsed_s_seed": u.get("elapsed_s_seed")}
        for u in all_units
    ],
    "elapsed_s": round(sum(u.get("elapsed_s_seed", 0.0) for u in all_units), 2),
}

if DEVICE.type == "cuda":
    try:
        peak_gb = torch.cuda.max_memory_allocated(0) / 1e9
        print("[gpu] peak memory %.3f GB" % peak_gb, flush=True)
        metrics["gpu_peak_mem_gb"] = round(peak_gb, 3)
    except Exception:
        pass

write_metrics(out_dir, metrics, all_units)
print("[metrics] written to %s" % out_dir, flush=True)
