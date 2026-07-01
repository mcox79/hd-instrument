"""Shared core for substrate_seqbind_N_dim_scaling_law_v1 siblings.

USER 2026-07-01 overnight priority: verify chain-grade sequence-binding
K-cliff scales cleanly across N (axis B; first free-axis chain-grade attempt).

Design:
  - N_DIM_SWEEP = [2048, 4096, 8192, 16384, 32768]
  - K_SEQ_SWEEP = [50, 100, 200, 500, 1000, 2000, 4000]
  - 2 arms:
      SUBSTRATE : FHRR_FLAT_PHASE_32 sequence binding (composed CG primitive)
      RANDOM    : shuffle-item baseline (chance-level; META_RULE_BC control)
  - Encoder: FHRR complex64 (matches theta-gamma v2)
  - ITEM_VOCAB_SIZE=10000; NOISE_SIGMA=0.05 (matches CG regime)

Discriminator: linear scaling law K_cliff(N) = alpha * N
  HARD_PASS: log2-log2 fit R^2 >= 0.95 AND slope in [0.85, 1.15] AND
             cv-across-seeds on slope <= 0.10 AND positive-control passes
  MIDDLE_BAND: R^2 in [0.80, 0.95) OR slope in [0.70, 1.30) but not HARD_PASS
  HARD_FAIL: R^2 < 0.80 OR slope outside [0.70, 1.30]

positive-control (Gate D): K_cliff at N=8192 must lie in {500, 1000, 2000}
  (log2 window matching CG theta-gamma v2 K_cliff ~ 1000).

Reuses code paths from _substrate_theta_gamma_v2_FHRR_all_complex_core:
  - make_fhrr_codebook (unit-phase complex64)
  - _build_positions_flat (FHRR_FLAT_PHASE_32 codebook)
  - encode_fhrr_sequence + decode_fhrr_at_position
  - _add_noise_complex

Anchor: substrate_seqbind_N_dim_scaling_law_v1_seed_{7,13,19}

Pre-reg: preregs/2026-06-30_substrate_seqbind_N_dim_scaling_law_v1.md

ASCII-only. No unicode. No em-dashes. No emojis.

Author: exp_dev 2026-06-30 (Opus 4.7 1M, agent-spawn) N-scaling drill.
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import torch  # PROT-020: overnight_queue routing-gate requires `import torch`


# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED at module init; META_RULE_AE)
# ---------------------------------------------------------------------------
# 2 arms (META_RULE_AX outer axis; LOCKED)
ARMS = ("SUBSTRATE", "RANDOM")

# N dimensionality sweep (axis B; LOCKED)
N_DIM_SWEEP_FULL = (2048, 4096, 8192, 16384, 32768)
# smoke uses 3 lower N + 1 preview at max N (discriminator-must-survive-scale pattern C)
N_DIM_SWEEP_SMOKE = (2048, 4096, 8192, 32768)

# K_SEQ sweep (needed to LOCATE cliff; LOCKED)
K_SEQ_SWEEP_FULL = (50, 100, 200, 500, 1000, 2000, 4000)
K_SEQ_SWEEP_SMOKE = (200, 1000, 4000)  # 3-point smoke (still identifies cliff for preview)

# Regime (LOCKED; matches theta-gamma v2 FHRR CG for positive-control fidelity)
ITEM_VOCAB_SIZE = 10000
# POSITION_SLOTS must be >= max(K_SEQ) so each sequence slot gets a UNIQUE
# position code (no cyclic wrap collisions). At K > POSITION_SLOTS, multiple
# items share positions and the unbind step returns a mixture -> chance
# retrieval, hiding the true N-scaling law. Set to max K_SEQ + 1.
POSITION_SLOTS = 4096        # covers K up to 4000 (max K_SEQ) with headroom
NOISE_SIGMA = 0.05

# Queries per (N, K) point
N_QUERIES_PER_KN = 30
N_QUERIES_PER_KN_SMOKE = 10

# Cliff detection threshold
CLIFF_ACC_THRESHOLD = 0.5

# HARD_PASS bands (LOCKED; strictly above floor + 5% per META_RULE_L)
HP_R2_FLOOR = 0.95
HP_SLOPE_LOW = 0.85
HP_SLOPE_HIGH = 1.15
HP_SEED_SLOPE_CV_MAX = 0.10

# MIDDLE_BAND bands
MB_R2_FLOOR = 0.80
MB_SLOPE_LOW = 0.70
MB_SLOPE_HIGH = 1.30

# Positive-control tolerance (Gate D)
POSCTRL_N = 8192
POSCTRL_LOG2_K_CENTER = math.log2(1000.0)  # CG cited K_cliff at N=8192
POSCTRL_LOG2_TOL = 0.5  # +/- factor of 1.41 (K in {500, 1000, 2000})

# Cardinality (per seed; LOCKED)
EXPECTED_N_UNITS_FULL = len(ARMS) * len(N_DIM_SWEEP_FULL) * len(K_SEQ_SWEEP_FULL)  # 2*5*7=70
EXPECTED_N_UNITS_SMOKE = len(ARMS) * len(N_DIM_SWEEP_SMOKE) * len(K_SEQ_SWEEP_SMOKE)  # 2*4*3=24

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# Device setup
# ---------------------------------------------------------------------------
def _get_device(strict_gpu: bool = False) -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda:0")
    if strict_gpu:
        raise RuntimeError(
            "GPU_MANDATE_VIOLATED (PROT-020 / Fix #24): cuda.is_available()=False. "
            "seqbind N-scaling at N up to %d K up to %d requires CUDA for "
            "overnight_queue routing. Route to overnight_queue or run "
            "with --smoke / --self-test for local CPU fallback." % (
                max(N_DIM_SWEEP_FULL), max(K_SEQ_SWEEP_FULL))
        )
    return torch.device("cpu")


def get_backend_label() -> str:
    if torch.cuda.is_available():
        try:
            return "torch.cuda:" + torch.cuda.get_device_name(0)
        except Exception:
            return "torch.cuda"
    return "torch.cpu"


# ---------------------------------------------------------------------------
# FHRR codebook (unit-phase complex64)
# ---------------------------------------------------------------------------
def make_fhrr_codebook(
    n_items: int, n_dim: int, seed: int, device: torch.device,
) -> torch.Tensor:
    """Unit-phase complex codebook (n_items, n_dim) complex64.

    Each element is exp(i*phi) for phi ~ Uniform[0, 2*pi).
    """
    g = torch.Generator(device=device)
    g.manual_seed(int(seed))
    phi = torch.empty(n_items, n_dim, device=device, dtype=torch.float32)
    phi.uniform_(0.0, 2.0 * math.pi, generator=g)
    real = torch.cos(phi)
    imag = torch.sin(phi)
    return torch.complex(real, imag)


def _build_positions_flat(
    n_positions: int, n_dim: int, seed: int, device: torch.device,
) -> torch.Tensor:
    """Flat FHRR phase codebook: n_positions unit-phase codes."""
    return make_fhrr_codebook(n_positions, n_dim, seed + 7919, device)


def _add_noise_complex(hd: torch.Tensor, sigma: float,
                       gen: torch.Generator) -> torch.Tensor:
    """Add complex Gaussian noise (real + imag) at sigma magnitude."""
    if sigma <= 0:
        return hd
    real_noise = torch.empty(hd.shape, device=hd.device, dtype=torch.float32)
    real_noise.normal_(0.0, sigma, generator=gen)
    imag_noise = torch.empty(hd.shape, device=hd.device, dtype=torch.float32)
    imag_noise.normal_(0.0, sigma, generator=gen)
    return hd + torch.complex(real_noise, imag_noise)


# ---------------------------------------------------------------------------
# FHRR sequence bind ops
# ---------------------------------------------------------------------------
# Chunk size for vocab-dim decode (v1.1 OOM fix 2026-06-30).
# item_codebook has shape (ITEM_VOCAB_SIZE=10000, N_DIM up to 32768) complex64.
# Full matmul item_codebook.conj() @ candidate materializes a full
# ITEM_VOCAB_SIZE x N_DIM conjugate tensor (~2.44 GiB at N=32768 c64).
# Chunk over vocab rows (dim 0) so peak alloc = DECODE_VOCAB_CHUNK * N_DIM.
# At chunk=512, N=32768, c64 -> 128 MiB per chunk (fits with codebook + positions
# resident on 8 GiB GPU).
DECODE_VOCAB_CHUNK = 512

# Chunk size for K-dim encode (v1.2 OOM fix 2026-06-30).
# (item_codes * position_codes) materializes a full (K, N) c64 outer product
# BEFORE the .sum(dim=0). At K=4000 N=32768 c64 -> ~1 GiB just for that tensor
# (peak ~4 GiB after chained allocs on the CUDA autograd path). Chunk over K
# so we accumulate the sum incrementally. Sum is associative -> chunked math
# is exact (modulo complex64 float summation order, which is bit-stable within
# a single chunk order and empirically identical to direct at these scales).
# At chunk=256, N=32768, c64 -> 64 MiB per chunk.
ENCODE_K_CHUNK = 256


def encode_fhrr_sequence(
    item_codes: torch.Tensor, position_codes: torch.Tensor,
) -> torch.Tensor:
    """Bundle phase-bound items: sum(item[k] * position[k]) over k in K.

    v1.2: chunk over K to bound GPU peak allocation (was OOM at K=4000
    N=32768 on 8 GiB GPU because (item*position) materializes a full (K,N)
    complex64 tensor before .sum(dim=0)). Chunked math is exact-equivalent
    via associativity of sum: total = sum_chunks(sum_within_chunk(item*pos)).
    """
    K = item_codes.shape[0]
    # For small K or CPU, direct path (no chunk overhead).
    if K <= ENCODE_K_CHUNK or item_codes.device.type != "cuda":
        return (item_codes * position_codes).sum(dim=0)
    # Chunked path: allocate a running sum tensor, add per-chunk partial sums.
    N = item_codes.shape[1]
    running = torch.zeros(N, dtype=item_codes.dtype, device=item_codes.device)
    for start in range(0, K, ENCODE_K_CHUNK):
        stop = min(start + ENCODE_K_CHUNK, K)
        # Partial sum for this K-chunk: peak alloc = (stop-start) * N * 8 bytes
        partial = (item_codes[start:stop] * position_codes[start:stop]).sum(dim=0)
        running = running + partial
        del partial
    return running


def decode_fhrr_at_position(
    seq_hd: torch.Tensor, position_hd: torch.Tensor,
    item_codebook: torch.Tensor,
) -> int:
    """Recover argmax item index at a given position.

    v1.1: chunk over vocab rows to bound GPU peak allocation (was OOM at
    N=32768 on 8 GiB GPU because item_codebook.conj() @ candidate materializes
    a full (V, N) conjugate). Chunked math is exact-equivalent: score of item i
    is |<conj(codebook[i]), candidate>| regardless of chunking.
    """
    candidate = seq_hd * position_hd.conj()
    V = item_codebook.shape[0]
    # For small V or CPU, take the direct path (no chunk overhead).
    if V <= DECODE_VOCAB_CHUNK or item_codebook.device.type != "cuda":
        scores = (item_codebook.conj() @ candidate).abs()
        return int(scores.argmax().item())
    # Chunked path: iterate vocab rows, keep only per-chunk argmax + score.
    best_score = None
    best_idx = -1
    for start in range(0, V, DECODE_VOCAB_CHUNK):
        stop = min(start + DECODE_VOCAB_CHUNK, V)
        chunk = item_codebook[start:stop]  # view; (chunk, N)
        chunk_scores = (chunk.conj() @ candidate).abs()  # (chunk,) float32
        chunk_max_val, chunk_max_idx = chunk_scores.max(dim=0)
        cmv = float(chunk_max_val.item())
        if best_score is None or cmv > best_score:
            best_score = cmv
            best_idx = start + int(chunk_max_idx.item())
        del chunk_scores
    return best_idx


# ---------------------------------------------------------------------------
# Per-arm eval at (arm, N, K_SEQ) point
# ---------------------------------------------------------------------------
def eval_arm_at_point(
    arm: str, N_DIM: int, K_SEQ: int, n_queries: int, seed: int,
    device: torch.device, noise_sigma: float = NOISE_SIGMA,
) -> Dict[str, Any]:
    """Evaluate one (arm, N, K) grid point. Returns metrics dict."""
    t0 = time.time()

    # v1.1 OOM insurance: clear CUDA cache at the start of every point so
    # transient allocations from the previous point don't stack. Cheap
    # (microseconds) and lets us hit N=32768 K=500 within 8 GiB budget.
    # v1.2: reset peak-stats here so cuda_peak_gib reflects THIS point only.
    if device.type == "cuda":
        torch.cuda.empty_cache()
        try:
            torch.cuda.reset_peak_memory_stats(device)
        except Exception:
            pass

    # v1.2: track encode + decode peaks separately for OOM audit
    encode_peak_gib = None
    decode_peak_gib = None

    g_main = torch.Generator(device=device)
    g_main.manual_seed(int(seed) + 1000 * int(N_DIM // 1024) + int(K_SEQ))
    g_noise = torch.Generator(device=device)
    g_noise.manual_seed(int(seed) + 31337 + int(N_DIM) + int(K_SEQ))

    # Build vocab + positions (allocated once per point)
    item_codebook = make_fhrr_codebook(ITEM_VOCAB_SIZE, N_DIM, seed, device)
    positions = _build_positions_flat(POSITION_SLOTS, N_DIM, seed, device)

    n_correct = 0
    # Assert POSITION_SLOTS >= K_SEQ so each item has a UNIQUE position code
    # (no cyclic wrap collisions that would hide the true K-cliff)
    if K_SEQ > POSITION_SLOTS:
        raise ValueError(
            f"K_SEQ={K_SEQ} > POSITION_SLOTS={POSITION_SLOTS}; "
            f"unique-position invariant violated"
        )
    for _q in range(n_queries):
        # Random item assignment
        item_ids = torch.empty(K_SEQ, device=device, dtype=torch.long)
        item_ids.random_(0, ITEM_VOCAB_SIZE, generator=g_main)
        # Each item gets a UNIQUE position (no cyclic wrap; slot k -> position k)
        pos_assignment = torch.arange(K_SEQ, device=device)

        seq_item_codes = item_codebook[item_ids]
        seq_pos_codes = positions[pos_assignment]
        seq_hd = encode_fhrr_sequence(seq_item_codes, seq_pos_codes)
        # v1.2: capture encode-phase peak on the FIRST query (representative)
        if _q == 0 and device.type == "cuda":
            try:
                encode_peak_gib = round(
                    torch.cuda.max_memory_allocated(device) / (1024 ** 3), 3
                )
            except Exception:
                encode_peak_gib = None
        seq_hd_noisy = _add_noise_complex(seq_hd, noise_sigma, g_noise)

        # Query a random target slot
        target_slot = int(torch.randint(
            0, K_SEQ, (1,), device=device, generator=g_main).item())
        true_item = int(item_ids[target_slot].item())
        query_position = positions[int(pos_assignment[target_slot].item())]

        if arm == "SUBSTRATE":
            pred = decode_fhrr_at_position(
                seq_hd_noisy, query_position, item_codebook)
        elif arm == "RANDOM":
            # META_RULE_BC positive control (chance-level baseline):
            # decode a uniformly random item id from the vocab
            pred = int(torch.randint(
                0, ITEM_VOCAB_SIZE, (1,), device=device, generator=g_main).item())
        else:
            raise ValueError(f"unknown arm: {arm!r}")

        if pred == true_item:
            n_correct += 1

    acc = float(n_correct) / float(n_queries)
    elapsed = time.time() - t0

    # Report CUDA peak memory (v1.1 diagnostic for OOM audit; v1.2 splits into
    # encode-phase peak + full-point peak so we can attribute future OOMs)
    peak_gib = None
    if device.type == "cuda":
        try:
            peak_bytes = torch.cuda.max_memory_allocated(device)
            peak_gib = round(peak_bytes / (1024 ** 3), 3)
        except Exception:
            peak_gib = None
        # decode_peak = full-point peak (decode happens after encode); if
        # decode was smaller than encode, this still records the largest.
        decode_peak_gib = peak_gib

    # Free intermediates (crucial for N=32768 memory hygiene)
    del item_codebook, positions
    if device.type == "cuda":
        torch.cuda.empty_cache()
        try:
            torch.cuda.reset_peak_memory_stats(device)
        except Exception:
            pass

    return {
        "arm": arm,
        "N_DIM": int(N_DIM),
        "K_SEQ": int(K_SEQ),
        "n_queries": int(n_queries),
        "n_correct": int(n_correct),
        "retrieval_acc": round(acc, 4),
        "noise_sigma": float(noise_sigma),
        "wall_s": round(elapsed, 3),
        "cuda_peak_gib": peak_gib,
        "cuda_encode_peak_gib": encode_peak_gib,
        "cuda_decode_peak_gib": decode_peak_gib,
    }


# ---------------------------------------------------------------------------
# Cliff-K detection per (arm, N)
# ---------------------------------------------------------------------------
def find_cliff_K(arm_N_pts: List[Dict[str, Any]]) -> Tuple[int, float]:
    """Given points sorted by K (ascending), return (cliff_K, log2_cliff_K).

    Cliff: largest K where retrieval_acc >= CLIFF_ACC_THRESHOLD.
    If all below threshold: cliff_K=0, log2=-1.0.
    If all above threshold: cliff_K=max(K), log2=log2(max(K)) (but flag ceiling).
    """
    pts_sorted = sorted(arm_N_pts, key=lambda p: p["K_SEQ"])
    last_above_K = 0
    for p in pts_sorted:
        if p["retrieval_acc"] >= CLIFF_ACC_THRESHOLD:
            last_above_K = p["K_SEQ"]
    if last_above_K == 0:
        return 0, -1.0
    return last_above_K, round(math.log2(last_above_K), 4)


# ---------------------------------------------------------------------------
# Scaling-law linear fit (log2(K_cliff) vs log2(N))
# ---------------------------------------------------------------------------
def fit_scaling_law(N_vals: List[int], K_cliffs: List[int]) -> Dict[str, Any]:
    """Fit log2(K_cliff) = slope * log2(N) + intercept.

    Skips points where K_cliff <= 0 (no capacity).
    Returns slope, intercept, R^2, n_points_used.
    """
    xs, ys = [], []
    for N, K in zip(N_vals, K_cliffs):
        if K > 0:
            xs.append(math.log2(N))
            ys.append(math.log2(K))
    n = len(xs)
    if n < 3:
        return {
            "slope": None, "intercept": None, "r2": None,
            "n_points_used": n, "fit_ok": False,
            "reason": f"need >=3 valid points; got {n}",
        }
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    if den <= 0:
        return {
            "slope": None, "intercept": None, "r2": None,
            "n_points_used": n, "fit_ok": False,
            "reason": "zero variance in log2(N)",
        }
    slope = num / den
    intercept = my - slope * mx
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - my) ** 2 for y in ys)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return {
        "slope": round(slope, 4),
        "intercept": round(intercept, 4),
        "r2": round(r2, 4),
        "n_points_used": n,
        "fit_ok": True,
    }


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------
def selftest(seed: int, device: torch.device = None) -> Tuple[bool, str]:
    if device is None:
        device = _get_device(strict_gpu=False)
    msgs: List[str] = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 70:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 70"
    if EXPECTED_N_UNITS_SMOKE != 24:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 24"
    msgs.append(
        f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}"
    )

    # 2. FHRR unbind is canonical inverse (mechanism unit test at tiny N)
    n_dim_st = 256
    item = make_fhrr_codebook(1, n_dim_st, seed, device)[0]
    pos = make_fhrr_codebook(1, n_dim_st, seed + 100, device)[0]
    bound = item * pos
    recovered = bound * pos.conj()
    diff = (recovered - item).abs().max().item()
    if diff > 1e-3:
        return False, f"FHRR unbind self-inverse FAIL: max|diff|={diff:.6f}"
    msgs.append(f"fhrr_unbind_self_inverse_max_diff={diff:.2e}")

    # 3. Clean K=1 retrieval at tiny N recovers item
    cb_small = make_fhrr_codebook(100, n_dim_st, seed, device)
    pos_small = make_fhrr_codebook(POSITION_SLOTS, n_dim_st, seed + 1, device)
    item_ids = torch.tensor([7], device=device, dtype=torch.long)
    pos_assignment = torch.tensor([0], device=device, dtype=torch.long)
    seq_hd = encode_fhrr_sequence(cb_small[item_ids], pos_small[pos_assignment])
    pred = decode_fhrr_at_position(seq_hd, pos_small[0], cb_small)
    if pred != 7:
        return False, f"clean K=1 retrieval FAIL: expected 7 got {pred}"
    msgs.append("clean_K1_retrieval_pass")

    # 4. Arms distinctness at tiny N smoke regime.
    # K=8 chosen because it's below POSITION_SLOTS=32, so each item gets a
    # unique position code (no cyclic wrap collisions). At K<POSITION_SLOTS,
    # substrate cleanup should recover items reliably even at N=1024.
    pt_sub = eval_arm_at_point(
        "SUBSTRATE", N_DIM=1024, K_SEQ=8, n_queries=8,
        seed=seed, device=device, noise_sigma=0.0,
    )
    pt_rnd = eval_arm_at_point(
        "RANDOM", N_DIM=1024, K_SEQ=8, n_queries=8,
        seed=seed, device=device, noise_sigma=0.0,
    )
    if pt_sub["retrieval_acc"] < 0.5:
        return False, (
            f"SUBSTRATE clean K=8 N=1024 acc too low: "
            f"{pt_sub['retrieval_acc']}; mechanism broken"
        )
    if pt_rnd["retrieval_acc"] > 0.05:
        return False, (
            f"RANDOM baseline non-chance: acc={pt_rnd['retrieval_acc']}; "
            f"baseline broken"
        )
    msgs.append(
        f"arm_distinctness_pass sub_acc={pt_sub['retrieval_acc']} "
        f"rnd_acc={pt_rnd['retrieval_acc']}"
    )

    # 5. Chunked-decode equivalence (v1.1 OOM fix): assert chunked path returns
    # SAME argmax as full matmul. Force-test both on CPU (chunking is only
    # auto-applied on CUDA; here we drive an inlined chunked reference).
    n_dim_ce = 128
    V_ce = DECODE_VOCAB_CHUNK * 2 + 37  # force >=3 chunks with a tail
    cb_ce = make_fhrr_codebook(V_ce, n_dim_ce, seed + 555, device)
    pos_ce = make_fhrr_codebook(POSITION_SLOTS, n_dim_ce, seed + 556, device)
    tgt_id = 1234 % V_ce
    seq_ce = encode_fhrr_sequence(
        cb_ce[torch.tensor([tgt_id], device=device, dtype=torch.long)],
        pos_ce[torch.tensor([0], device=device, dtype=torch.long)],
    )
    # Direct reference (full matmul)
    candidate_ref = seq_ce * pos_ce[0].conj()
    scores_ref = (cb_ce.conj() @ candidate_ref).abs()
    ref_argmax = int(scores_ref.argmax().item())
    ref_topscore = float(scores_ref.max().item())
    # Inlined chunked reference (validates the chunked math independent of
    # the device-type dispatch inside decode_fhrr_at_position)
    best_score_c = None
    best_idx_c = -1
    for start in range(0, V_ce, DECODE_VOCAB_CHUNK):
        stop = min(start + DECODE_VOCAB_CHUNK, V_ce)
        chunk = cb_ce[start:stop]
        chunk_scores = (chunk.conj() @ candidate_ref).abs()
        cmv, cmi = chunk_scores.max(dim=0)
        if best_score_c is None or float(cmv.item()) > best_score_c:
            best_score_c = float(cmv.item())
            best_idx_c = start + int(cmi.item())
    if best_idx_c != ref_argmax:
        return False, (
            f"chunked_decode_mismatch: chunked={best_idx_c} "
            f"direct={ref_argmax} (V={V_ce} chunk={DECODE_VOCAB_CHUNK})"
        )
    if abs(best_score_c - ref_topscore) > 1e-4:
        return False, (
            f"chunked_decode_score_drift: chunked={best_score_c:.6f} "
            f"direct={ref_topscore:.6f}"
        )
    # Also verify the actual API dispatch is correct on this device
    got_argmax = decode_fhrr_at_position(seq_ce, pos_ce[0], cb_ce)
    if got_argmax != ref_argmax:
        return False, (
            f"decode_api_mismatch: got={got_argmax} direct={ref_argmax}"
        )
    msgs.append(
        f"chunked_decode_equivalence_pass V={V_ce} chunk={DECODE_VOCAB_CHUNK} "
        f"topscore={ref_topscore:.4f}"
    )

    # 5b. Chunked-encode equivalence (v1.2 OOM fix): sum is associative -> the
    # chunked K-accumulation must give the same complex vector as direct
    # (item * position).sum(dim=0). Force-test with an inlined chunked
    # reference at K > ENCODE_K_CHUNK on any device (CPU path skips chunking).
    n_dim_ee = 64
    K_ee = ENCODE_K_CHUNK * 3 + 17  # force 4 chunks with a tail
    cb_ee = make_fhrr_codebook(ITEM_VOCAB_SIZE, n_dim_ee, seed + 777, device)
    pos_ee = make_fhrr_codebook(POSITION_SLOTS, n_dim_ee, seed + 778, device)
    item_ids_ee = torch.arange(K_ee, device=device, dtype=torch.long) % ITEM_VOCAB_SIZE
    pos_ids_ee = torch.arange(K_ee, device=device, dtype=torch.long) % POSITION_SLOTS
    ic_ee = cb_ee[item_ids_ee]
    pc_ee = pos_ee[pos_ids_ee]
    # Direct reference
    seq_ref = (ic_ee * pc_ee).sum(dim=0)
    # Inlined chunked reference
    seq_chunk = torch.zeros(n_dim_ee, dtype=ic_ee.dtype, device=device)
    for start in range(0, K_ee, ENCODE_K_CHUNK):
        stop = min(start + ENCODE_K_CHUNK, K_ee)
        seq_chunk = seq_chunk + (ic_ee[start:stop] * pc_ee[start:stop]).sum(dim=0)
    max_diff = (seq_ref - seq_chunk).abs().max().item()
    if max_diff > 1e-3:
        return False, (
            f"chunked_encode_mismatch: max|diff|={max_diff:.6f} "
            f"(K={K_ee} chunk={ENCODE_K_CHUNK})"
        )
    # Verify the actual API dispatch is correct on this device
    seq_api = encode_fhrr_sequence(ic_ee, pc_ee)
    api_diff = (seq_ref - seq_api).abs().max().item()
    if api_diff > 1e-3:
        return False, (
            f"encode_api_mismatch: max|diff|={api_diff:.6f}"
        )
    msgs.append(
        f"chunked_encode_equivalence_pass K={K_ee} chunk={ENCODE_K_CHUNK} "
        f"max_diff={max_diff:.2e}"
    )

    # 6. Scaling-law fit sanity (synthetic K_cliff = 0.12 * N snapped to K_SEQ)
    N_test = list(N_DIM_SWEEP_FULL)
    K_synth = []
    for N in N_test:
        K_hyp = 0.12 * N
        K_snap = min(K_SEQ_SWEEP_FULL,
                     key=lambda k: abs(math.log2(k) - math.log2(K_hyp)))
        K_synth.append(K_snap)
    fit = fit_scaling_law(N_test, K_synth)
    if not fit["fit_ok"]:
        return False, f"scaling fit FAIL on synthetic: {fit.get('reason')}"
    if not (0.8 <= fit["slope"] <= 1.2):
        return False, (
            f"synthetic slope out of range: {fit['slope']} "
            f"(expected ~1.0 for alpha*N synthetic)"
        )
    if fit["r2"] < 0.90:
        return False, f"synthetic R2 too low: {fit['r2']} (expected >=0.90)"
    msgs.append(
        f"scaling_fit_synthetic_slope={fit['slope']} R2={fit['r2']} "
        f"n_pts={fit['n_points_used']}"
    )

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed_scaling_sweep(
    seed: int, run_mode: str, device: torch.device,
    heartbeat=None,
) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    n_sweep = N_DIM_SWEEP_SMOKE if is_smoke else N_DIM_SWEEP_FULL
    k_sweep = K_SEQ_SWEEP_SMOKE if is_smoke else K_SEQ_SWEEP_FULL
    n_queries = N_QUERIES_PER_KN_SMOKE if is_smoke else N_QUERIES_PER_KN
    expected_n = len(ARMS) * len(n_sweep) * len(k_sweep)

    print(
        f"[run_scaling_sweep] seed={seed} mode={run_mode} device={device} "
        f"arms={ARMS} N_sweep={n_sweep} K_sweep={k_sweep} "
        f"n_queries={n_queries} expected_n={expected_n}",
        flush=True,
    )

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()
    unit_idx = 0
    for arm in ARMS:
        for N_DIM in n_sweep:
            for K_SEQ in k_sweep:
                pt = eval_arm_at_point(
                    arm=arm, N_DIM=N_DIM, K_SEQ=K_SEQ,
                    n_queries=n_queries, seed=seed, device=device,
                    noise_sigma=NOISE_SIGMA,
                )
                phase_map.append(pt)
                unit_idx += 1
                print(
                    f"[pt] s={seed} arm={arm:<10} N={N_DIM:>6} K={K_SEQ:>5} "
                    f"acc={pt['retrieval_acc']:.3f} t={pt['wall_s']:.2f}s",
                    flush=True,
                )
                if heartbeat is not None:
                    heartbeat.tick(
                        unit_idx,
                        extra={"arm": arm, "N": N_DIM, "K": K_SEQ,
                               "acc": pt["retrieval_acc"]},
                    )

    elapsed = time.time() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    # Per-arm per-N cliff detection
    per_arm_per_N_summary: Dict[str, Dict[int, Dict[str, Any]]] = {}
    K_cliff_by_arm_N: Dict[str, Dict[int, int]] = {}
    log2_K_cliff_by_arm_N: Dict[str, Dict[int, float]] = {}
    for arm in ARMS:
        per_arm_per_N_summary[arm] = {}
        K_cliff_by_arm_N[arm] = {}
        log2_K_cliff_by_arm_N[arm] = {}
        for N_DIM in n_sweep:
            arm_N_pts = [
                p for p in phase_map
                if p["arm"] == arm and p["N_DIM"] == N_DIM
            ]
            cliff_K, log2_cliff = find_cliff_K(arm_N_pts)
            per_arm_per_N_summary[arm][N_DIM] = {
                "n_K_points": len(arm_N_pts),
                "K_values": [p["K_SEQ"] for p in sorted(arm_N_pts,
                                                       key=lambda p: p["K_SEQ"])],
                "accs": [p["retrieval_acc"] for p in sorted(arm_N_pts,
                                                           key=lambda p: p["K_SEQ"])],
                "cliff_K": cliff_K,
                "log2_cliff_K": log2_cliff,
                "max_acc": max([p["retrieval_acc"] for p in arm_N_pts],
                               default=0.0),
                "mean_acc": round(float(np.mean(
                    [p["retrieval_acc"] for p in arm_N_pts])), 4)
                    if arm_N_pts else 0.0,
            }
            K_cliff_by_arm_N[arm][N_DIM] = cliff_K
            log2_K_cliff_by_arm_N[arm][N_DIM] = log2_cliff

    # Scaling-law fit for SUBSTRATE arm
    substrate_Ns = list(n_sweep)
    substrate_cliffs = [K_cliff_by_arm_N["SUBSTRATE"][N] for N in substrate_Ns]
    substrate_fit = fit_scaling_law(substrate_Ns, substrate_cliffs)

    # Fit for RANDOM arm (expected to fail; K_cliff ~ 0)
    random_cliffs = [K_cliff_by_arm_N["RANDOM"][N] for N in substrate_Ns]
    random_fit = fit_scaling_law(substrate_Ns, random_cliffs)

    # Positive-control check (Gate D): K_cliff at N=8192 must be in {500, 1000, 2000}
    posctrl_pass = False
    posctrl_reason = ""
    if POSCTRL_N in K_cliff_by_arm_N["SUBSTRATE"]:
        posctrl_K = K_cliff_by_arm_N["SUBSTRATE"][POSCTRL_N]
        if posctrl_K > 0:
            posctrl_log2 = math.log2(posctrl_K)
            delta = abs(posctrl_log2 - POSCTRL_LOG2_K_CENTER)
            posctrl_pass = (delta <= POSCTRL_LOG2_TOL)
            posctrl_reason = (
                f"N={POSCTRL_N} K_cliff={posctrl_K} log2={posctrl_log2:.3f}; "
                f"CG center=log2(1000)={POSCTRL_LOG2_K_CENTER:.3f}; "
                f"|delta|={delta:.3f} tol={POSCTRL_LOG2_TOL}"
            )
        else:
            posctrl_reason = f"N={POSCTRL_N} K_cliff=0 (no capacity)"
    else:
        posctrl_reason = f"N={POSCTRL_N} not in sweep (smoke maybe skipped)"

    # META_RULE_AF arms-must-differ: hash the outcome payloads
    arm_outcome_hashes: Dict[str, str] = {}
    for arm in ARMS:
        arm_pts = sorted(
            [p for p in phase_map if p["arm"] == arm],
            key=lambda p: (p["N_DIM"], p["K_SEQ"]),
        )
        payload = json.dumps(
            [(p["N_DIM"], p["K_SEQ"], round(p["retrieval_acc"], 4))
             for p in arm_pts],
            sort_keys=True,
        ).encode("utf-8")
        arm_outcome_hashes[arm] = hashlib.sha256(payload).hexdigest()[:16]
    arms_differ = (
        arm_outcome_hashes["SUBSTRATE"] != arm_outcome_hashes["RANDOM"]
    )

    return {
        "seed": seed,
        "run_mode": run_mode,
        "arms": list(ARMS),
        "N_DIM_sweep": list(n_sweep),
        "K_SEQ_sweep": list(k_sweep),
        "n_queries_per_KN": n_queries,
        "ITEM_VOCAB_SIZE": ITEM_VOCAB_SIZE,
        "POSITION_SLOTS": POSITION_SLOTS,
        "NOISE_SIGMA": NOISE_SIGMA,
        "phase_map": phase_map,
        "per_arm_per_N_summary": per_arm_per_N_summary,
        "K_cliff_by_arm_N": {
            arm: {str(N): int(K) for N, K in d.items()}
            for arm, d in K_cliff_by_arm_N.items()
        },
        "log2_K_cliff_by_arm_N": {
            arm: {str(N): float(v) for N, v in d.items()}
            for arm, d in log2_K_cliff_by_arm_N.items()
        },
        "substrate_scaling_fit": substrate_fit,
        "random_scaling_fit": random_fit,
        "positive_control_pass": bool(posctrl_pass),
        "positive_control_reason": posctrl_reason,
        "arm_outcome_hashes": arm_outcome_hashes,
        "arms_differ_verified": bool(arms_differ),
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "elapsed_seed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Smoke gate predicate
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    phase_map = body.get("phase_map", [])
    expected_n = body.get("expected_n_units", 0)
    arms_differ = body.get("arms_differ_verified", False)
    substrate_fit = body.get("substrate_scaling_fit", {})
    K_cliff = body.get("K_cliff_by_arm_N", {})

    # 1. Cardinality
    if len(phase_map) != expected_n:
        return False, (
            f"cardinality_breach: expected {expected_n} got {len(phase_map)}"
        )

    # 2. META_RULE_AF arms-must-differ
    if not arms_differ:
        return False, "HARD_FAIL_ARMS_COLLIDE (META_RULE_AF): SUBSTRATE == RANDOM hash"

    # 3. Discriminator-fires: SUBSTRATE must show non-zero cliff at multiple N
    sub_cliffs = K_cliff.get("SUBSTRATE", {})
    nonzero_cliffs = sum(1 for k in sub_cliffs.values() if k > 0)
    if nonzero_cliffs < 3:
        return False, (
            f"HARD_FAIL_DISCRIMINATOR_DEAD: SUBSTRATE has only {nonzero_cliffs}/"
            f"{len(sub_cliffs)} non-zero K_cliffs; mechanism not firing"
        )

    # 4. Preview at largest N should have non-zero cliff
    # (DISCRIMINATOR-MUST-SURVIVE-SCALE pattern C)
    N_max = str(max(int(k) for k in sub_cliffs.keys()))
    if sub_cliffs.get(N_max, 0) <= 0:
        return False, (
            f"HARD_FAIL_SCALE_PREVIEW: N={N_max} K_cliff=0; scaling law breaks "
            f"at largest N; do NOT dispatch full"
        )

    # 5. RANDOM must be near-zero cliff (chance baseline sanity)
    rnd_cliffs = K_cliff.get("RANDOM", {})
    rnd_nonzero = sum(1 for k in rnd_cliffs.values() if k > 0)
    if rnd_nonzero > 1:  # allow noise at 1 N; more = broken baseline
        return False, (
            f"HARD_FAIL_BASELINE_ELEVATED (META_RULE_BC): RANDOM has "
            f"{rnd_nonzero} non-zero cliffs; baseline broken"
        )

    # 6. Preliminary fit sanity: slope should be positive (increasing K with N)
    slope = substrate_fit.get("slope")
    if slope is not None and slope <= 0:
        return False, (
            f"HARD_FAIL_NEGATIVE_SCALING: slope={slope} <= 0; K_cliff does not "
            f"grow with N"
        )

    return True, (
        f"smoke_gate_pass: cardinality={len(phase_map)} arms_differ=True "
        f"sub_nonzero_cliffs={nonzero_cliffs}/{len(sub_cliffs)} "
        f"N_max={N_max}_cliff={sub_cliffs.get(N_max, 0)} "
        f"rnd_nonzero={rnd_nonzero} slope~={slope}"
    )


# ---------------------------------------------------------------------------
# Verdict-emitter
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                          run_mode: str) -> Dict[str, Any]:
    if not per_seed:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": "HARD_FAIL_NO_SEEDS: empty per_seed",
            "summary": "HARD_FAIL_NO_SEEDS",
        }

    is_smoke = (run_mode == "smoke")
    seed_key = list(per_seed.keys())[0]
    body = per_seed[seed_key]

    common = {
        "phase_map": body.get("phase_map", []),
        "per_arm_per_N_summary": body.get("per_arm_per_N_summary", {}),
        "K_cliff_by_arm_N": body.get("K_cliff_by_arm_N", {}),
        "log2_K_cliff_by_arm_N": body.get("log2_K_cliff_by_arm_N", {}),
        "substrate_scaling_fit": body.get("substrate_scaling_fit", {}),
        "random_scaling_fit": body.get("random_scaling_fit", {}),
        "positive_control_pass": body.get("positive_control_pass", False),
        "positive_control_reason": body.get("positive_control_reason", ""),
        "arm_outcome_hashes": body.get("arm_outcome_hashes", {}),
        "arms_differ_verified": body.get("arms_differ_verified", False),
        "cardinality_ok": body.get("cardinality_ok", False),
        "expected_n_units": body.get("expected_n_units", 0),
        "observed_n_units": body.get("observed_n_units", 0),
        "N_DIM_sweep": body.get("N_DIM_sweep"),
        "K_SEQ_sweep": body.get("K_SEQ_sweep"),
        "ITEM_VOCAB_SIZE": body.get("ITEM_VOCAB_SIZE"),
        "POSITION_SLOTS": body.get("POSITION_SLOTS"),
        "NOISE_SIGMA": body.get("NOISE_SIGMA"),
    }

    if is_smoke:
        passed, reason = smoke_gate_predicate(body)
        verdict = "HARD_PASS" if passed else "HARD_FAIL"
        vmsg = (
            f"HARD_PASS_SMOKE_seqbind_N_scaling: {reason}"
            if passed
            else f"HARD_FAIL_SMOKE_seqbind_N_scaling: {reason}"
        )
        out = dict(common)
        out.update({
            "verdict": verdict,
            "verdict_msg": vmsg,
            "summary": vmsg,
            "smoke_gate_pass": passed,
            "smoke_gate_reason": reason,
        })
        return out

    # FULL verdict
    cardinality_ok = body.get("cardinality_ok", False)
    arms_differ = body.get("arms_differ_verified", False)
    posctrl_pass = body.get("positive_control_pass", False)
    posctrl_reason = body.get("positive_control_reason", "")
    fit = body.get("substrate_scaling_fit", {})
    slope = fit.get("slope")
    r2 = fit.get("r2")
    fit_ok = fit.get("fit_ok", False)

    if not cardinality_ok:
        verdict = "HARD_FAIL"
        vmsg = (
            f"HARD_FAIL_CARDINALITY_BREACH (META_RULE_H): "
            f"expected={body.get('expected_n_units')} "
            f"observed={body.get('observed_n_units')}"
        )
    elif not arms_differ:
        verdict = "HARD_FAIL"
        vmsg = "HARD_FAIL_ARMS_COLLIDE (META_RULE_AF): SUBSTRATE hash == RANDOM hash"
    elif not fit_ok:
        verdict = "HARD_FAIL"
        vmsg = (
            f"HARD_FAIL_SCALING_FIT_UNDEFINED: {fit.get('reason', 'no fit')}; "
            f"insufficient cliff points to characterize scaling"
        )
    elif not posctrl_pass:
        verdict = "HARD_FAIL"
        vmsg = (
            f"HARD_FAIL_POSITIVE_CONTROL_REGRESSION (Gate D): {posctrl_reason}"
        )
    elif (r2 >= HP_R2_FLOOR
          and HP_SLOPE_LOW <= slope <= HP_SLOPE_HIGH):
        verdict = "HARD_PASS"
        vmsg = (
            f"HARD_PASS_seqbind_N_dim_scaling_law: slope={slope:.3f} "
            f"in [{HP_SLOPE_LOW}, {HP_SLOPE_HIGH}]; R2={r2:.3f} >= {HP_R2_FLOOR}; "
            f"posctrl={posctrl_reason}; K_cliff_by_N=SUBSTRATE:{body.get('K_cliff_by_arm_N', {}).get('SUBSTRATE', {})}"
        )
    elif (r2 is not None and r2 >= MB_R2_FLOOR
          and slope is not None and MB_SLOPE_LOW <= slope <= MB_SLOPE_HIGH):
        verdict = "MIDDLE_BAND"
        vmsg = (
            f"MIDDLE_BAND_seqbind_scaling: slope={slope:.3f} "
            f"in [{MB_SLOPE_LOW}, {MB_SLOPE_HIGH}]; R2={r2:.3f} "
            f"in [{MB_R2_FLOOR}, {HP_R2_FLOOR}); posctrl={posctrl_reason}; "
            f"K_cliff_by_N=SUBSTRATE:{body.get('K_cliff_by_arm_N', {}).get('SUBSTRATE', {})}"
        )
    else:
        verdict = "HARD_FAIL"
        vmsg = (
            f"HARD_FAIL_SCALING_CEILING: slope={slope} R2={r2} outside "
            f"MB bands slope[{MB_SLOPE_LOW}, {MB_SLOPE_HIGH}] R2>={MB_R2_FLOOR}; "
            f"substrate does NOT scale linearly with N; posctrl={posctrl_reason}"
        )

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "ARMS", "N_DIM_SWEEP_FULL", "N_DIM_SWEEP_SMOKE",
    "K_SEQ_SWEEP_FULL", "K_SEQ_SWEEP_SMOKE",
    "ITEM_VOCAB_SIZE", "POSITION_SLOTS", "NOISE_SIGMA",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "REQUIRED_FIELDS", "CLIFF_ACC_THRESHOLD",
    "HP_R2_FLOOR", "HP_SLOPE_LOW", "HP_SLOPE_HIGH", "HP_SEED_SLOPE_CV_MAX",
    "MB_R2_FLOOR", "MB_SLOPE_LOW", "MB_SLOPE_HIGH",
    "POSCTRL_N", "POSCTRL_LOG2_K_CENTER", "POSCTRL_LOG2_TOL",
    "_get_device", "get_backend_label",
    "make_fhrr_codebook", "encode_fhrr_sequence", "decode_fhrr_at_position",
    "eval_arm_at_point", "find_cliff_K", "fit_scaling_law",
    "selftest", "run_one_seed_scaling_sweep",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
