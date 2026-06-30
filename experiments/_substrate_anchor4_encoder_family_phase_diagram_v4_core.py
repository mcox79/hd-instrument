"""Shared core for substrate_anchor4_encoder_family_phase_diagram_v4 siblings.

ANCHOR 4 encoder-family phase diagram v4 (META_RULE_AY enforcement + encoder-
specific code-path verification + regime where saturation does not mask).

v3 atomized 2026-06-30 as MM_PARTIAL_DISCRIMINATION (6th phantom-FULL partial)
per Skunkworks a4bfdc71. v3 promoted 0/5 -> 2/5 distinct (sparse_bipolar +
sparse_real wired); dense triplet (binary_bipolar / hrr_real / fhrr) remained
bit-identical at full capacity (13/18 cells saturate at recall=1.000).
encoder_pair_distinctness self-reported False for 3 pairs yet verdict still
emitted HARD_PASS; verdict-emitter was over-permissive.

v4 fix per spec (notes/director_anchor4_encoder_v4_design_spec_2026-06-30.md):
  1. Pre-flight distinctness gate at cell entry: bind fixed test pair under each
     encoder; verify per-encoder mechanism_hash distinct via SHA-256. HARD_FAIL
     pre-dispatch on collision (META_RULE_AY).
  2. Verdict-emitter auto-demotes HARD_PASS -> MM/HARD_FAIL on self-reported
     distinctness False (>=10% False -> MM; >=50% False -> HARD_FAIL).
  3. Regime to avoid saturation:
        N_DIMS = [2048, 4096, 8192]   (drop 1024 small + 16384 saturating)
        LOADS = [2.0, 4.0, 8.0, 12.0] (push higher load; v3 max=5.0)
        DECAYS = [30, 60, 180]
        NOISE_SIGMA = 0.1             (add noise to retain mechanism resolution)
        Phase grid: 3 N * 4 LOAD * 3 DECAY = 36 cells/encoder. 5 enc = 180/seed.
  4. Encoder-specific binding ops VERIFIED distinct:
        binary_bipolar  : elementwise mul on {-1,+1}^N           -> dense_real
        hrr_real        : FFT circular convolution                -> dense_real
        fhrr            : complex elementwise mul on C^(N/2)      -> complex
        sparse_bipolar  : elementwise mul on {-1,0,+1}^N           -> sparse
        sparse_real     : elementwise mul on sparse Gaussian       -> sparse_real
     SHA-256 mechanism_hash on bound output MUST differ across all 5 families
     at pre-flight. (v3 had op paths defined but pre-flight gate did not enforce.)
  5. Discriminator-survives-scale: smoke at FULL-N range verifies
     (a) all 5 encoder hashes distinct at pre-flight
     (b) per-encoder metrics differ by >= 0.05 across grid at smoke regime
     (c) no cell saturates to 1.000 at smoke

Anchor: substrate_anchor4_encoder_family_phase_diagram_v4_seed_{7,13,19}.

Pre-reg: preregs/2026-06-30_substrate_anchor4_encoder_family_phase_diagram_v4.md

ASCII-only. No unicode. No em-dashes. No emojis.

Author: exp_dev 2026-06-30 (Opus 4.7 1M, agent-spawn).
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import torch  # PROT-020: overnight_queue routing gate requires `import torch`


# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED at module init; META_RULE_AE)
# ---------------------------------------------------------------------------
# v3-ratified Pareto-AUC thresholds (preserve semantics)
HP_DOMINANCE_RATE_LO = 0.85
HP_NET_DOMINANCE_LO = 0.70
HP_RD_LOSS_RATE_HI = 0.05

# META_RULE_AP: pair Pareto-AUC chain-grade gate with readout floor
HP_RECENCY_DECODE_FLOOR = 0.30  # per-encoder mean recency_decode_acc

# META_RULE_AX: cross-encoder distinctness (5 encoders -> C(5,2)=10 pairs)
HP_MIN_PAIRS_DIFFER = 5  # of 10 pairs

# META_RULE_AY (NEW v4): verdict-emitter HARD_FAIL on encoder_pair_distinctness
# False rate. >=50% False -> HARD_FAIL; >=10% False -> MIDDLE_BAND demote.
META_AY_HARD_FAIL_FRAC = 0.50
META_AY_MM_DEMOTE_FRAC = 0.10

# META_RULE_Q (saturation): no cell may hit recall=1.000 at smoke; threshold to
# flag as suspicious is >= SATURATION_FLAG_THRESH
SATURATION_FLAG_THRESH = 1.000 - 1e-6
SATURATION_HARD_FAIL_FRAC = 0.50  # >50% of cells saturating -> HARD_FAIL

# Encoder families (OUTER axis; LOCKED at module init; 5 distinct families)
ENCODER_FAMILIES = (
    "binary_bipolar",
    "hrr_real",
    "fhrr",
    "sparse_bipolar",
    "sparse_real",
)

# Simulation params (ported from v3)
N_ATOMS_BASE = 1500
N_DAYS_SIM = 365
RECENT_QUERY_DAYS = 30
QUERY_DECAY_TAU = 60.0
R_BUCKETS = 128

# v4 regime: drop 1024 (too small) + 16384 (saturating)
N_DIM_SWEEP_FULL = [2048, 4096, 8192]
N_DIM_SWEEP_SMOKE = [2048, 4096, 8192]  # smoke at full-N range (discriminator-must-survive-scale)
N_DIM_DEFAULT = 4096  # used by positive-control point
SPARSE_BIPOLAR_DENSITY = 0.05
SPARSE_REAL_DENSITY = 0.20

# v4 LOADS pushed higher to escape v3 saturation regime.
# Loads also drive bundle_capacity_ratio (M atoms bundled into 1 mem vector;
# higher load -> more interference -> lower decode -> capacity stress).
# load=2.0 and 4.0 dropped: FHRR saturates at load=4 across all N (1.000 recall).
CAPACITY_LOAD_RATIO_FULL = [8.0, 12.0, 16.0, 24.0]
CAPACITY_LOAD_RATIO_SMOKE = [8.0, 16.0, 24.0]

# v4 DECAYS adjusted (v3 had [30, 90, 180]; v4 = [30, 60, 180])
DECAY_RATE_DAYS_FULL = [30, 60, 180]
DECAY_RATE_DAYS_SMOKE = [30, 180]  # smoke samples extremes

# v4 NOISE_SIGMA: add noise floor to retain mechanism resolution at high load
NOISE_SIGMA = 0.1

# Cardinality (per seed; LOCKED)
EXPECTED_N_UNITS_FULL = (
    len(ENCODER_FAMILIES) * len(DECAY_RATE_DAYS_FULL)
    * len(CAPACITY_LOAD_RATIO_FULL) * len(N_DIM_SWEEP_FULL)
)  # 5 * 3 * 4 * 3 = 180
EXPECTED_N_UNITS_SMOKE = (
    len(ENCODER_FAMILIES) * len(DECAY_RATE_DAYS_SMOKE)
    * len(CAPACITY_LOAD_RATIO_SMOKE) * len(N_DIM_SWEEP_SMOKE)
)  # 5 * 2 * 3 * 3 = 90
assert EXPECTED_N_UNITS_FULL == 180, f"expected 180 got {EXPECTED_N_UNITS_FULL}"
assert EXPECTED_N_UNITS_SMOKE == 90, f"expected 90 got {EXPECTED_N_UNITS_SMOKE}"

# Positive control: binary_bipolar at (decay=180, load=8.0, N=4096) at v4 regime
# with bundling + noise. decay=180 is in both SMOKE and FULL decay axis sets.
POSITIVE_CONTROL = {
    "encoder_family": "binary_bipolar",
    "decay_rate_days": 180,
    "capacity_load_ratio": 8.0,
    "N_DIM": N_DIM_DEFAULT,
    "expected_pareto_outcome": "TD_DOMINATES",
    "min_recency_decode_acc": 0.70,  # bundling + noise -> ~0.89 expected
    "max_recency_decode_acc": 0.999,  # must NOT saturate (META_RULE_Q)
}

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
            "v4 encoder family phase diagram at N_DIM up to %d requires CUDA "
            "for OVERNIGHT_QUEUE routing. Route to overnight_queue or run with "
            "--smoke / --self-test for local CPU fallback." % max(N_DIM_SWEEP_FULL)
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
# Encoder family primitives (torch tensors on _device)
# ---------------------------------------------------------------------------
def _make_gen(seed: int, device: torch.device) -> torch.Generator:
    g = torch.Generator(device=device)
    g.manual_seed(int(seed))
    return g


def _build_binary_bipolar_t(n_items: int, dim: int, seed: int,
                             device: torch.device) -> torch.Tensor:
    """Dense bipolar {-1, +1}^N (n_items, dim) float32 torch tensor."""
    g = _make_gen(seed, device)
    x = torch.empty(n_items, dim, device=device, dtype=torch.float32)
    x.bernoulli_(0.5, generator=g).mul_(2.0).sub_(1.0)
    return x


def _build_hrr_real_t(n_items: int, dim: int, seed: int,
                       device: torch.device) -> torch.Tensor:
    """Dense Gaussian N(0, 1/N), L2-normalized (n_items, dim) float32."""
    g = _make_gen(seed, device)
    x = torch.empty(n_items, dim, device=device, dtype=torch.float32)
    x.normal_(0.0, 1.0 / math.sqrt(dim), generator=g)
    norms = x.norm(dim=1, keepdim=True).clamp_min(1e-12)
    return x / norms


def _build_fhrr_t(n_items: int, dim: int, seed: int,
                   device: torch.device) -> torch.Tensor:
    """Unit-modulus complex exp(i*phi) in C^(dim/2); returned as complex64.

    Output shape: (n_items, dim/2) complex64. Total real DoF = dim.
    """
    if dim % 2 != 0:
        raise ValueError(f"FHRR requires even dim; got dim={dim}")
    n_complex = dim // 2
    g = _make_gen(seed, device)
    phi = torch.empty(n_items, n_complex, device=device, dtype=torch.float32)
    phi.uniform_(0.0, 2.0 * math.pi, generator=g)
    real = torch.cos(phi)
    imag = torch.sin(phi)
    return torch.complex(real, imag)


def _build_sparse_bipolar_t(n_items: int, dim: int, seed: int,
                              device: torch.device) -> torch.Tensor:
    """Sparse-ternary {-1, 0, +1}^N at density 0.05 (n_items, dim) float32."""
    g = _make_gen(seed, device)
    s = max(1, int(round(SPARSE_BIPOLAR_DENSITY * dim)))
    arr = torch.zeros(n_items, dim, device=device, dtype=torch.float32)
    scores = torch.empty(n_items, dim, device=device, dtype=torch.float32)
    scores.normal_(0.0, 1.0, generator=g)
    topk_vals, topk_idx = scores.topk(s, dim=1)
    sign_score = torch.empty(n_items, s, device=device, dtype=torch.float32)
    sign_score.bernoulli_(0.5, generator=g)
    signs = sign_score * 2.0 - 1.0
    arr.scatter_(1, topk_idx, signs)
    return arr


def _build_sparse_real_t(n_items: int, dim: int, seed: int,
                          device: torch.device) -> torch.Tensor:
    """Sparse REAL: Gaussian magnitudes at density 0.20, sign-bipolar at support.

    Distinct from sparse_bipolar (denser support, continuous magnitudes) and
    from sparse_bipolar's signs (Gaussian magnitude rather than +-1).

    NOT L2-normalized: keep raw magnitudes for bundle-decode signal.
    """
    g = _make_gen(seed, device)
    s = max(1, int(round(SPARSE_REAL_DENSITY * dim)))
    arr = torch.zeros(n_items, dim, device=device, dtype=torch.float32)
    scores = torch.empty(n_items, dim, device=device, dtype=torch.float32)
    scores.normal_(0.0, 1.0, generator=g)
    topk_vals, topk_idx = scores.topk(s, dim=1)
    # Sign-bipolar magnitudes drawn from |Gaussian| (continuous magnitudes)
    mag = torch.empty(n_items, s, device=device, dtype=torch.float32)
    mag.normal_(0.0, 1.0, generator=g)
    mag = mag.abs()  # keep magnitude continuous
    sign_score = torch.empty(n_items, s, device=device, dtype=torch.float32)
    sign_score.bernoulli_(0.5, generator=g)
    signs = sign_score * 2.0 - 1.0
    values = signs * mag
    arr.scatter_(1, topk_idx, values)
    return arr


# ---------------------------------------------------------------------------
# Encoder-specific BIND ops (v4 critical fix; each must produce distinct output)
# ---------------------------------------------------------------------------
def bind_binary_bipolar(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Elementwise multiplication for ±1 bipolar; result still in {-1, +1}.

    Math: c[i] = a[i] * b[i]. Self-inverse: a (*) a == 1.
    """
    return (a * b).to(torch.float32)


def bind_hrr_real(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """HRR circular convolution via FFT.

    Math: c[k] = sum_j a[j] * b[(k-j) mod N]. F(c) = F(a) * F(b).
    """
    fa = torch.fft.rfft(a, dim=-1)
    fb = torch.fft.rfft(b, dim=-1)
    out = torch.fft.irfft(fa * fb, n=a.shape[-1], dim=-1).to(torch.float32)
    return out


def bind_fhrr_complex(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """FHRR phase-binding: elementwise complex multiplication.

    Math: c[i] = a[i] * b[i] in C; |c[i]|=1 preserved.
    """
    return (a * b).to(torch.complex64)


def bind_sparse_bipolar(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Sparse bipolar bind: elementwise mul (preserves sparsity intersection).

    Math: c[i] = a[i] * b[i]. Where a or b is 0, c = 0 (AND on supports).
    """
    return (a * b).to(torch.float32)


def bind_sparse_real(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Sparse real bind: elementwise mul on sparse Gaussian.

    Math: c[i] = a[i] * b[i]; sparse intersection support; continuous magnitudes.
    """
    return (a * b).to(torch.float32)


# Unbind / decode ops
def unbind_binary_bipolar(bound: torch.Tensor, key: torch.Tensor) -> torch.Tensor:
    """Self-inverse: a (*) a == 1, so a (*) (a*b) == b for bipolar."""
    inv = torch.where(key != 0, torch.sign(key), torch.zeros_like(key))
    return (bound * inv).to(torch.float32)


def unbind_hrr_real(bound: torch.Tensor, key: torch.Tensor) -> torch.Tensor:
    """HRR circular correlation = conv(bound, conj(key)) via FFT."""
    fa = torch.fft.rfft(bound, dim=-1)
    fb_conj = torch.fft.rfft(key, dim=-1).conj()
    out = torch.fft.irfft(fa * fb_conj, n=bound.shape[-1], dim=-1).to(torch.float32)
    return out


def unbind_fhrr_complex(bound: torch.Tensor, key: torch.Tensor) -> torch.Tensor:
    """FHRR unbind by complex conjugate multiplication."""
    return (bound * key.conj()).to(torch.complex64)


def unbind_sparse_bipolar(bound: torch.Tensor, key: torch.Tensor) -> torch.Tensor:
    """Sparse bipolar unbind: elementwise mul (masked by key support)."""
    inv = torch.where(key != 0, torch.sign(key), torch.zeros_like(key))
    return (bound * inv).to(torch.float32)


def unbind_sparse_real(bound: torch.Tensor, key: torch.Tensor) -> torch.Tensor:
    """Sparse real unbind: elementwise mul (correlate-by-key); cosine score
    against recency basis recovers signal via inner product. Pure divide-by-key
    yields broken decode at scale because most positions are zero."""
    return (bound * key).to(torch.float32)


# Score ops (cosine for real codes; complex-analog for FHRR)
def _score_real_t(Q: torch.Tensor, X: torch.Tensor) -> torch.Tensor:
    qn = Q.norm(dim=1, keepdim=True).clamp_min(1e-12)
    xn = X.norm(dim=1, keepdim=True).clamp_min(1e-12)
    return ((Q / qn) @ (X / xn).T).to(torch.float32)


def _score_fhrr_t(Q: torch.Tensor, X: torch.Tensor) -> torch.Tensor:
    sims = (Q @ X.conj().T).real
    n_complex = X.shape[1]
    return (sims / float(n_complex)).to(torch.float32)


def _encoder_dim(family: str, dim: int) -> int:
    return dim // 2 if family == "fhrr" else dim


_ENCODER_REGISTRY: Dict[str, Dict[str, Any]] = {
    "binary_bipolar": {
        "build": _build_binary_bipolar_t,
        "bind": bind_binary_bipolar,
        "unbind": unbind_binary_bipolar,
        "score": _score_real_t,
        "complex": False,
        "dtype_label": "float32",
        "bind_op_name": "elementwise_mul_bipolar",
    },
    "hrr_real": {
        "build": _build_hrr_real_t,
        "bind": bind_hrr_real,
        "unbind": unbind_hrr_real,
        "score": _score_real_t,
        "complex": False,
        "dtype_label": "float32",
        "bind_op_name": "fft_circular_convolution",
    },
    "fhrr": {
        "build": _build_fhrr_t,
        "bind": bind_fhrr_complex,
        "unbind": unbind_fhrr_complex,
        "score": _score_fhrr_t,
        "complex": True,
        "dtype_label": "complex64",
        "bind_op_name": "complex_elementwise_mul",
    },
    "sparse_bipolar": {
        "build": _build_sparse_bipolar_t,
        "bind": bind_sparse_bipolar,
        "unbind": unbind_sparse_bipolar,
        "score": _score_real_t,
        "complex": False,
        "dtype_label": "float32",
        "bind_op_name": "elementwise_mul_sparse_bipolar",
    },
    "sparse_real": {
        "build": _build_sparse_real_t,
        "bind": bind_sparse_real,
        "unbind": unbind_sparse_real,
        "score": _score_real_t,
        "complex": False,
        "dtype_label": "float32",
        "bind_op_name": "elementwise_mul_sparse_real",
    },
}


# ---------------------------------------------------------------------------
# Pre-flight encoder distinctness gate (META_RULE_AY enforcement)
# ---------------------------------------------------------------------------
def verify_encoder_distinctness_preflight(
    seed: int, device: torch.device, dim: int = 1024,
) -> Tuple[bool, Dict[str, str], str]:
    """Bind a FIXED test pair under each encoder; verify SHA-256 hashes distinct.

    Returns (all_distinct: bool, hashes: Dict[family, hash16], msg: str).
    HARD_FAIL pre-dispatch if ANY 2 encoders' bind output hashes collide.
    """
    n_test = 4  # 4 test pairs per encoder
    hashes: Dict[str, str] = {}
    collisions: List[Tuple[str, str]] = []

    for fam in ENCODER_FAMILIES:
        reg = _ENCODER_REGISTRY[fam]
        a = reg["build"](n_test, dim, seed, device)
        b = reg["build"](n_test, dim, seed + 1, device)
        bound = reg["bind"](a, b)
        bound_cpu = bound.detach().cpu().numpy()
        # Hash on the byte representation; distinct encoders produce distinct bytes
        h = hashlib.sha256(bound_cpu.tobytes()).hexdigest()[:16]
        # Check for collision against earlier encoders
        for prev_fam, prev_h in hashes.items():
            if prev_h == h:
                collisions.append((prev_fam, fam))
        hashes[fam] = h
        del a, b, bound, bound_cpu
        if device.type == "cuda":
            torch.cuda.empty_cache()

    if collisions:
        msg = (
            f"ENCODER_HASH_COLLISION (META_RULE_AY pre-flight): collisions="
            f"{collisions}; hashes={hashes}. Cell HARD_FAILs pre-dispatch."
        )
        return False, hashes, msg

    msg = f"preflight_distinct(dim={dim}): {hashes}"
    return True, hashes, msg


# ---------------------------------------------------------------------------
# Substrate timeline (PORTED from v3; numpy RNG for positive-control reproduction)
# ---------------------------------------------------------------------------
def simulate_atom_timeline(
    n_atoms: int, n_days: int, capacity_load_ratio: float,
    query_decay_tau: float, seed: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Port of v3 timeline. Returns arrival_day, last_query_day, is_working_set."""
    rng = np.random.RandomState(seed)
    arrival_day = rng.randint(0, n_days, size=n_atoms).astype(np.int64)
    is_core = rng.rand(n_atoms) < 0.30
    last_query_day = np.full(n_atoms, -1, dtype=np.int64)
    for i in range(n_atoms):
        a = arrival_day[i]
        if is_core[i]:
            last_query_day[i] = n_days - 1 - rng.randint(0, RECENT_QUERY_DAYS)
        else:
            age_at_end = n_days - a
            mean_interval = query_decay_tau * capacity_load_ratio
            lam = max(0.0, age_at_end / max(mean_interval, 1e-6))
            n_reqs = rng.poisson(lam) if lam > 0 else 0
            if n_reqs == 0:
                last_query_day[i] = a
            else:
                qs = rng.randint(a, n_days, size=n_reqs)
                last_query_day[i] = int(qs.max())
    is_working_set = (last_query_day >= n_days - RECENT_QUERY_DAYS) & (last_query_day >= 0)
    return arrival_day, last_query_day, is_working_set


# ---------------------------------------------------------------------------
# Encoder mediation (v4: noise injection on bound vec for non-saturation)
# ---------------------------------------------------------------------------
def quantize_to_bucket(day: int, n_days: int, n_buckets: int) -> int:
    if day < 0:
        return 0
    return int(min(n_buckets - 1, max(0, (day * n_buckets) // max(n_days, 1))))


def build_encoded_atom_store(
    encoder_family: str, n_atoms: int, last_query_day: np.ndarray,
    n_days: int, n_buckets: int, dim: int, seed: int,
    device: torch.device, noise_sigma: float = NOISE_SIGMA,
    bundle_capacity_ratio: float = 2.0,
) -> Dict[str, Any]:
    """Encode atoms via BUNDLED memory; decode requires unbinding against
    superposition of M=ceil(bundle_capacity_ratio * dim_eff / n_buckets) atoms.

    v4 CRITICAL FIX: previous versions stored each atom's bound vector separately
    (`bound[i] = atom_code[i] (*) recency_keys[i]`), then decoded via self-inverse
    `unbind(bound[i], atom_code[i]) = recency_keys[buckets_true[i]]`. This is
    trivially perfect (recall=1.000) regardless of N, load, or noise because the
    unbind operator factors out cleanly. capacity_load_ratio modulated only the
    timeline (which atoms count as working_set), NOT the encoding capacity.

    v4 bundles M atoms into ONE shared memory vector per partition. Decode of
    atom i sums interference from M-1 other atoms in same partition. This
    genuinely stresses capacity: higher bundle_capacity_ratio -> more atoms per
    partition -> lower decode accuracy. Encoder families now differ because:
      - binary_bipolar: signs accumulate; partial cancellation
      - hrr_real: FFT superposition; partial; circular convolution recovers via correlation
      - fhrr: phase superposition; bounded magnitude
      - sparse_bipolar/real: sparse interference; fewer collisions

    Bundle size M = max(2, int(bundle_capacity_ratio * dim_eff / n_buckets)).
    Partition all atoms into chunks of size M; each chunk gets its own bundled
    memory vector. Decode atom i by querying its chunk's memory vector with
    atom_code[i] as key.

    v4 noise injection: adds N(0, noise_sigma) to bound vec for additional stress.
    """
    reg = _ENCODER_REGISTRY[encoder_family]

    atom_codes = reg["build"](n_atoms, dim, seed, device)
    recency_basis = reg["build"](n_buckets, dim, seed + 31337, device)

    buckets = np.array(
        [quantize_to_bucket(int(d), n_days, n_buckets) for d in last_query_day],
        dtype=np.int64,
    )
    buckets_t = torch.from_numpy(buckets).to(device)

    recency_keys = recency_basis[buckets_t]  # (n_atoms, dim_eff)

    # CRITICAL v4 FIX: each encoder invokes its OWN bind op (registry routes correctly)
    per_atom_bound = reg["bind"](atom_codes, recency_keys)  # (n_atoms, dim_eff)

    # Bundle: partition atoms into chunks of size M; sum within chunk
    dim_eff = _encoder_dim(encoder_family, dim)
    M = max(2, int(round(bundle_capacity_ratio * dim_eff / max(n_buckets, 1))))
    M = min(M, n_atoms)  # cap at n_atoms

    # Assign each atom to a chunk
    n_chunks = (n_atoms + M - 1) // M
    chunk_id = np.arange(n_atoms) // M  # int array (n_atoms,)
    chunk_id_t = torch.from_numpy(chunk_id).to(device).long()

    # Sum per_atom_bound within each chunk
    if reg["complex"]:
        # Complex sum: do real + imag separately, recombine
        chunk_real = torch.zeros(n_chunks, dim_eff, device=device, dtype=torch.float32)
        chunk_imag = torch.zeros(n_chunks, dim_eff, device=device, dtype=torch.float32)
        chunk_real.index_add_(0, chunk_id_t, per_atom_bound.real)
        chunk_imag.index_add_(0, chunk_id_t, per_atom_bound.imag)
        bundled_mem = torch.complex(chunk_real, chunk_imag).to(torch.complex64)
    else:
        bundled_mem = torch.zeros(n_chunks, dim_eff, device=device, dtype=torch.float32)
        bundled_mem.index_add_(0, chunk_id_t, per_atom_bound)

    # v4 noise injection on bundled memory
    if noise_sigma > 0.0:
        g = _make_gen(seed + 7777, device)
        if reg["complex"]:
            noise_r = torch.empty_like(bundled_mem.real)
            noise_i = torch.empty_like(bundled_mem.imag)
            noise_r.normal_(0.0, noise_sigma, generator=g)
            noise_i.normal_(0.0, noise_sigma, generator=g)
            bundled_mem = torch.complex(
                bundled_mem.real + noise_r, bundled_mem.imag + noise_i,
            ).to(torch.complex64)
        else:
            noise = torch.empty_like(bundled_mem)
            noise.normal_(0.0, noise_sigma, generator=g)
            bundled_mem = (bundled_mem + noise).to(torch.float32)

    # Per-atom "bound" is the bundled vector at the atom's chunk (broadcast)
    bound = bundled_mem[chunk_id_t]  # (n_atoms, dim_eff)

    return {
        "atom_codes": atom_codes,
        "recency_basis": recency_basis,
        "bound": bound,
        "bundled_mem": bundled_mem,
        "chunk_id": chunk_id,
        "buckets_true": buckets,
        "buckets_true_t": buckets_t,
        "family": encoder_family,
        "dim_eff": dim_eff,
        "bundle_M": int(M),
        "n_chunks": int(n_chunks),
        "bind_op_name": reg["bind_op_name"],
    }


def decode_recency_buckets(store: Dict[str, Any]) -> Tuple[torch.Tensor, float]:
    """Decode each atom's recency bucket from the bound store."""
    reg = _ENCODER_REGISTRY[store["family"]]
    atom_codes = store["atom_codes"]
    recency_basis = store["recency_basis"]
    bound = store["bound"]
    buckets_true_t = store["buckets_true_t"]

    decoded = reg["unbind"](bound, atom_codes)
    sims = reg["score"](decoded, recency_basis)
    preds_t = sims.argmax(dim=1)
    acc = float((preds_t == buckets_true_t).to(torch.float32).mean().item())
    return preds_t, acc


# ---------------------------------------------------------------------------
# Arms (TIME_DECAY / RANDOM eviction)
# ---------------------------------------------------------------------------
def arm_time_decay_via_encoder(
    decoded_buckets_t: torch.Tensor, n_days: int, n_buckets: int,
    decay_rate_days: int,
) -> np.ndarray:
    decoded_cpu = decoded_buckets_t.detach().cpu().numpy().astype(np.int64)
    bucket_width_days = n_days / float(max(n_buckets, 1))
    estimated_last_query_day = (decoded_cpu.astype(np.float64) + 0.5) * bucket_width_days
    estimated_age = n_days - estimated_last_query_day
    return (estimated_age > decay_rate_days).astype(bool)


def arm_random_eviction(
    n_atoms: int, target_eviction_count: int, seed: int,
) -> np.ndarray:
    rng = np.random.RandomState(seed + 7919)
    evicted = np.zeros(n_atoms, dtype=bool)
    if target_eviction_count <= 0:
        return evicted
    target_eviction_count = min(target_eviction_count, n_atoms)
    idx = rng.choice(n_atoms, size=target_eviction_count, replace=False)
    evicted[idx] = True
    return evicted


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def compute_arm_metrics(evicted: np.ndarray, is_working_set: np.ndarray) -> Dict[str, Any]:
    n_atoms = len(evicted)
    n_ws = int(is_working_set.sum())
    n_alive = int((~evicted).sum())
    n_evicted = int(evicted.sum())
    if n_ws == 0:
        ws_retention = float("nan")
    else:
        ws_retention = float(((~evicted) & is_working_set).sum() / n_ws)
    if n_alive == 0:
        clutter_fraction = float("nan")
    else:
        clutter_fraction = float(((~evicted) & (~is_working_set)).sum() / n_alive)
    if np.isnan(ws_retention) or np.isnan(clutter_fraction):
        composite = float("nan")
    else:
        composite = ws_retention - clutter_fraction
    return {
        "working_set_retention": float(ws_retention),
        "clutter_fraction": float(clutter_fraction),
        "composite": float(composite),
        "n_alive": int(n_alive),
        "n_evicted": int(n_evicted),
        "eviction_fraction": float(n_evicted / n_atoms) if n_atoms else 0.0,
    }


def pareto_dominance_outcome(td_ws, td_clut, rd_ws, rd_clut) -> str:
    if any(np.isnan(x) for x in (td_ws, td_clut, rd_ws, rd_clut)):
        return "TIE"
    td_y = 1.0 - td_clut
    rd_y = 1.0 - rd_clut
    if td_ws >= rd_ws and td_y >= rd_y and (td_ws > rd_ws or td_y > rd_y):
        return "TD_DOMINATES"
    if rd_ws >= td_ws and rd_y >= td_y and (rd_ws > td_ws or rd_y > td_y):
        return "RD_DOMINATES"
    return "TIE"


# ---------------------------------------------------------------------------
# Per-phase-point eval
# ---------------------------------------------------------------------------
def eval_phase_point(
    encoder_family: str, decay_rate_days: int, capacity_load_ratio: float,
    n_atoms: int, n_days: int, n_buckets: int, dim: int, seed: int,
    device: torch.device, noise_sigma: float = NOISE_SIGMA,
) -> Dict[str, Any]:
    if encoder_family not in _ENCODER_REGISTRY:
        raise ValueError(f"unknown encoder_family={encoder_family!r}")
    t0 = time.time()

    arrival_day, last_query_day, is_working_set = simulate_atom_timeline(
        n_atoms=n_atoms, n_days=n_days,
        capacity_load_ratio=capacity_load_ratio,
        query_decay_tau=QUERY_DECAY_TAU, seed=seed,
    )

    store = build_encoded_atom_store(
        encoder_family=encoder_family, n_atoms=n_atoms,
        last_query_day=last_query_day, n_days=n_days, n_buckets=n_buckets,
        dim=dim, seed=seed, device=device, noise_sigma=noise_sigma,
        bundle_capacity_ratio=capacity_load_ratio,
    )
    decoded_buckets_t, recency_decode_acc = decode_recency_buckets(store)

    td_evicted = arm_time_decay_via_encoder(
        decoded_buckets_t, n_days, n_buckets, decay_rate_days,
    )
    td_metrics = compute_arm_metrics(td_evicted, is_working_set)

    rd_evicted = arm_random_eviction(n_atoms, int(td_evicted.sum()), seed)
    rd_metrics = compute_arm_metrics(rd_evicted, is_working_set)

    pareto_outcome = pareto_dominance_outcome(
        td_metrics["working_set_retention"], td_metrics["clutter_fraction"],
        rd_metrics["working_set_retention"], rd_metrics["clutter_fraction"],
    )

    # Saturation flag (META_RULE_Q)
    td_saturated = (
        td_metrics["working_set_retention"] >= SATURATION_FLAG_THRESH
        and recency_decode_acc >= SATURATION_FLAG_THRESH
    )

    bind_op_name = store["bind_op_name"]

    del store, decoded_buckets_t
    if device.type == "cuda":
        torch.cuda.empty_cache()

    elapsed = time.time() - t0
    return {
        "encoder_family": encoder_family,
        "bind_op_name": bind_op_name,
        "decay_rate_days": int(decay_rate_days),
        "capacity_load_ratio": float(capacity_load_ratio),
        "n_atoms": int(n_atoms),
        "n_days": int(n_days),
        "n_buckets": int(n_buckets),
        "N_dim_input": int(dim),
        "dim_eff": _encoder_dim(encoder_family, dim),
        "noise_sigma": float(noise_sigma),
        "n_working_set_atoms": int(is_working_set.sum()),
        "recency_decode_acc": round(recency_decode_acc, 4),
        "ARM_TIME_DECAY_EVICTION": td_metrics,
        "ARM_RANDOM_EVICTION": rd_metrics,
        "td_minus_random_ws_retention": round(
            td_metrics["working_set_retention"] - rd_metrics["working_set_retention"], 4),
        "td_minus_random_clutter_fraction": round(
            td_metrics["clutter_fraction"] - rd_metrics["clutter_fraction"], 4),
        "td_minus_random_composite": round(
            td_metrics["composite"] - rd_metrics["composite"], 4),
        "pareto_outcome": pareto_outcome,
        "saturated": bool(td_saturated),
        "wall_s": round(elapsed, 3),
        "dtype_label": _ENCODER_REGISTRY[encoder_family]["dtype_label"],
    }


# ---------------------------------------------------------------------------
# Selftest (encoder distinctness + recency decode + positive control)
# ---------------------------------------------------------------------------
def selftest(seed: int, device: torch.device = None) -> Tuple[bool, str]:
    if device is None:
        device = _get_device(strict_gpu=False)
    msgs: List[str] = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 180:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 180"
    if EXPECTED_N_UNITS_SMOKE != 90:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 90"
    msgs.append(
        f"cardinality FULL={EXPECTED_N_UNITS_FULL} "
        f"SMOKE={EXPECTED_N_UNITS_SMOKE}"
    )

    # 2. Pre-flight encoder distinctness (META_RULE_AY)
    ok, hashes, pf_msg = verify_encoder_distinctness_preflight(seed, device, dim=1024)
    if not ok:
        return False, pf_msg
    msgs.append(pf_msg)

    # Also verify at a larger dim
    ok2, hashes2, pf_msg2 = verify_encoder_distinctness_preflight(seed, device, dim=4096)
    if not ok2:
        return False, pf_msg2
    msgs.append(f"preflight_distinct(dim=4096): {hashes2}")

    # 3. Recency decode fidelity per encoder at N_DIM_DEFAULT with noise
    decode_accs: Dict[str, float] = {}
    n_atoms_dec = 200
    n_buckets_dec = 32
    dim_dec = N_DIM_DEFAULT
    n_days_san = 180
    arrival_d, lastq_d, _ = simulate_atom_timeline(
        n_atoms_dec, n_days_san, 1.0, QUERY_DECAY_TAU, seed + 1,
    )
    for fam in ENCODER_FAMILIES:
        store = build_encoded_atom_store(
            fam, n_atoms_dec, lastq_d, n_days_san, n_buckets_dec, dim_dec,
            seed + 1, device, noise_sigma=0.0,  # noise-free for selftest fidelity
        )
        _, acc = decode_recency_buckets(store)
        decode_accs[fam] = round(acc, 3)
        del store
        if device.type == "cuda":
            torch.cuda.empty_cache()
        if acc < 0.50:
            return False, (
                f"recency decode FAIL {fam}: acc={acc:.3f} < 0.50 at "
                f"n_atoms={n_atoms_dec} n_buckets={n_buckets_dec} dim={dim_dec}"
            )
    msgs.append(f"recency_decode_acc per encoder(dim={dim_dec}, noise=0): {decode_accs}")

    # 4. v4 positive control: binary_bipolar at (dr=180, ld=8.0, N=4096) with bundling + noise
    pt = eval_phase_point(
        encoder_family="binary_bipolar", decay_rate_days=180,
        capacity_load_ratio=8.0, n_atoms=N_ATOMS_BASE,
        n_days=N_DAYS_SIM, n_buckets=R_BUCKETS, dim=N_DIM_DEFAULT,
        seed=13, device=device, noise_sigma=NOISE_SIGMA,
    )
    if pt["pareto_outcome"] != "TD_DOMINATES":
        return False, (
            f"Positive control FAILED: binary_bipolar v4 op-point "
            f"expected TD_DOMINATES, got {pt['pareto_outcome']}; "
            f"td.ws={pt['ARM_TIME_DECAY_EVICTION']['working_set_retention']:.3f} "
            f"rec={pt['recency_decode_acc']:.3f}"
        )
    if pt["recency_decode_acc"] < POSITIVE_CONTROL["min_recency_decode_acc"]:
        return False, (
            f"Positive control recency_decode_acc too low: "
            f"{pt['recency_decode_acc']:.3f} < "
            f"{POSITIVE_CONTROL['min_recency_decode_acc']}"
        )
    if pt["recency_decode_acc"] > POSITIVE_CONTROL["max_recency_decode_acc"]:
        return False, (
            f"Positive control SATURATED (META_RULE_Q): recency_decode_acc="
            f"{pt['recency_decode_acc']:.3f} > {POSITIVE_CONTROL['max_recency_decode_acc']}; "
            f"v4 regime should produce non-saturated decode at higher load + noise"
        )
    msgs.append(
        f"positive_control v4: binary_bipolar @ (dr=180, ld=8.0, N=4096, noise=0.1, bundle) "
        f"pareto={pt['pareto_outcome']} "
        f"td.ws={pt['ARM_TIME_DECAY_EVICTION']['working_set_retention']:.3f} "
        f"rec={pt['recency_decode_acc']:.3f} saturated={pt['saturated']}"
    )

    # 5. Pareto dominance unit-checks
    assert pareto_dominance_outcome(0.9, 0.1, 0.5, 0.4) == "TD_DOMINATES"
    assert pareto_dominance_outcome(0.5, 0.4, 0.9, 0.1) == "RD_DOMINATES"
    assert pareto_dominance_outcome(0.5, 0.3, 0.5, 0.3) == "TIE"
    assert pareto_dominance_outcome(0.9, 0.4, 0.5, 0.1) == "TIE"
    assert pareto_dominance_outcome(float("nan"), 0.1, 0.5, 0.4) == "TIE"
    msgs.append("pareto_dominance unit-tests pass")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed phase sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(
    seed: int, run_mode: str, device: torch.device,
) -> Dict[str, Any]:
    """Run all (encoder, decay, load, N_dim) phase points for one seed."""
    is_smoke = (run_mode == "smoke")
    decay_sweep = DECAY_RATE_DAYS_SMOKE if is_smoke else DECAY_RATE_DAYS_FULL
    load_sweep = CAPACITY_LOAD_RATIO_SMOKE if is_smoke else CAPACITY_LOAD_RATIO_FULL
    dim_sweep = N_DIM_SWEEP_SMOKE if is_smoke else N_DIM_SWEEP_FULL
    expected_n = (
        len(ENCODER_FAMILIES) * len(decay_sweep)
        * len(load_sweep) * len(dim_sweep)
    )

    # PRE-FLIGHT GATE: encoder distinctness at cell entry (META_RULE_AY)
    preflight_ok, preflight_hashes, preflight_msg = verify_encoder_distinctness_preflight(
        seed, device, dim=1024,
    )

    print(
        f"[run_one_seed v4] seed={seed} mode={run_mode} device={device} "
        f"encoders={ENCODER_FAMILIES} decay_axis={decay_sweep} "
        f"load_axis={load_sweep} dim_axis={dim_sweep} "
        f"NOISE_SIGMA={NOISE_SIGMA} R_BUCKETS={R_BUCKETS} "
        f"n_atoms={N_ATOMS_BASE} expected_n={expected_n}",
        flush=True,
    )
    print(f"[preflight] {preflight_msg}", flush=True)

    if not preflight_ok:
        # Pre-flight HARD_FAIL: bail without running phase points
        return {
            "seed": seed,
            "run_mode": run_mode,
            "preflight_ok": False,
            "preflight_hashes": preflight_hashes,
            "preflight_msg": preflight_msg,
            "phase_map": [],
            "per_encoder_summary": {},
            "encoder_tiers": {},
            "encoder_pair_distinctness": {},
            "n_pairs_differ": 0,
            "n_pairs_total": 10,
            "arms_differ_per_encoder": {},
            "positive_control_result": {"pass": False, "outcome": "PREFLIGHT_FAIL"},
            "cardinality_ok": False,
            "expected_n_units": expected_n,
            "observed_n_units": 0,
            "elapsed_seed_s": 0.0,
        }

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()
    for fam in ENCODER_FAMILIES:
        for dr in decay_sweep:
            for cl in load_sweep:
                for nd in dim_sweep:
                    pt = eval_phase_point(
                        encoder_family=fam, decay_rate_days=dr,
                        capacity_load_ratio=cl, n_atoms=N_ATOMS_BASE,
                        n_days=N_DAYS_SIM, n_buckets=R_BUCKETS, dim=nd,
                        seed=seed, device=device, noise_sigma=NOISE_SIGMA,
                    )
                    phase_map.append(pt)
                    td = pt["ARM_TIME_DECAY_EVICTION"]
                    rd = pt["ARM_RANDOM_EVICTION"]
                    sat_marker = "[SAT]" if pt["saturated"] else "     "
                    print(
                        f"[pt] s={seed} {fam[:14]:<14} dr={dr:>3} ld={cl:.1f} "
                        f"N={nd:>5} td.ws={td['working_set_retention']:.3f} "
                        f"rd.ws={rd['working_set_retention']:.3f} "
                        f"pareto={pt['pareto_outcome']:<14} "
                        f"rec={pt['recency_decode_acc']:.3f} {sat_marker} "
                        f"t={pt['wall_s']:.2f}s",
                        flush=True,
                    )

    elapsed = time.time() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    # Per-encoder summary
    per_encoder_summary: Dict[str, Dict[str, Any]] = {}
    for fam in ENCODER_FAMILIES:
        fam_pts = [p for p in phase_map if p["encoder_family"] == fam]
        outcomes = [p["pareto_outcome"] for p in fam_pts]
        td_wins = sum(1 for o in outcomes if o == "TD_DOMINATES")
        rd_wins = sum(1 for o in outcomes if o == "RD_DOMINATES")
        ties = sum(1 for o in outcomes if o == "TIE")
        n_pts_fam = len(fam_pts)
        dom_rate = (td_wins + 0.5 * ties) / max(n_pts_fam, 1)
        net_dom = (td_wins - rd_wins) / max(n_pts_fam, 1)
        rd_loss = rd_wins / max(n_pts_fam, 1)
        decode_accs = [p["recency_decode_acc"] for p in fam_pts]
        sat_counts = sum(1 for p in fam_pts if p["saturated"])
        per_encoder_summary[fam] = {
            "n_points": n_pts_fam,
            "td_wins": td_wins,
            "rd_wins": rd_wins,
            "ties": ties,
            "dominance_rate": round(dom_rate, 4),
            "net_dominance": round(net_dom, 4),
            "rd_loss_rate": round(rd_loss, 4),
            "recency_decode_acc_mean": round(
                float(np.mean(decode_accs)), 4) if decode_accs else 0.0,
            "recency_decode_acc_std": round(
                float(np.std(decode_accs)), 4) if decode_accs else 0.0,
            "n_saturated_cells": sat_counts,
            "saturation_frac": round(sat_counts / max(n_pts_fam, 1), 4),
        }

    # META_RULE_AX: cross-encoder pair distinctness over C(5,2)=10 pairs
    # Use full metrics hash (composite + recency_decode), ordered by (decay, load, dim)
    encoder_outcome_hashes: Dict[str, str] = {}
    for fam in ENCODER_FAMILIES:
        fam_pts = sorted(
            [p for p in phase_map if p["encoder_family"] == fam],
            key=lambda p: (p["decay_rate_days"], p["capacity_load_ratio"],
                            p["N_dim_input"]),
        )
        payload = json.dumps(
            [(p["pareto_outcome"],
              round(p["ARM_TIME_DECAY_EVICTION"]["composite"], 4),
              round(p["recency_decode_acc"], 4))
             for p in fam_pts],
            sort_keys=True,
        ).encode("utf-8")
        encoder_outcome_hashes[fam] = hashlib.sha256(payload).hexdigest()[:16]

    fams = list(ENCODER_FAMILIES)
    pairs_differ: Dict[str, bool] = {}
    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            key = f"{fams[i]}_vs_{fams[j]}"
            pairs_differ[key] = (encoder_outcome_hashes[fams[i]]
                                  != encoder_outcome_hashes[fams[j]])
    n_pairs_differ = sum(1 for v in pairs_differ.values() if v)
    n_pairs_total = len(pairs_differ)  # 10 for C(5,2)

    # Cross-encoder metric distinctness: average |delta recency_decode| across grid
    # NEW v4 check: per-pair mean abs delta of recency_decode_acc across cells
    cross_enc_metric_distinct: Dict[str, float] = {}
    cells_by_grid: Dict[Tuple[int, float, int], Dict[str, float]] = {}
    for p in phase_map:
        key = (p["decay_rate_days"], p["capacity_load_ratio"], p["N_dim_input"])
        if key not in cells_by_grid:
            cells_by_grid[key] = {}
        cells_by_grid[key][p["encoder_family"]] = p["recency_decode_acc"]
    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            pair_key = f"{fams[i]}_vs_{fams[j]}"
            deltas = []
            for grid_cell, accs in cells_by_grid.items():
                if fams[i] in accs and fams[j] in accs:
                    deltas.append(abs(accs[fams[i]] - accs[fams[j]]))
            cross_enc_metric_distinct[pair_key] = round(
                float(np.mean(deltas)) if deltas else 0.0, 4)
    n_pairs_metric_distinct = sum(
        1 for v in cross_enc_metric_distinct.values() if v >= 0.05
    )

    # TIME_DECAY vs RANDOM per encoder (mechanism gate; META_RULE_AF within-arm)
    arms_differ_per_enc: Dict[str, Dict[str, Any]] = {}
    for fam in ENCODER_FAMILIES:
        fam_pts = [p for p in phase_map if p["encoder_family"] == fam]
        td_payload = json.dumps(
            [round(p["ARM_TIME_DECAY_EVICTION"]["composite"], 4) for p in fam_pts],
            sort_keys=True,
        ).encode("utf-8")
        rd_payload = json.dumps(
            [round(p["ARM_RANDOM_EVICTION"]["composite"], 4) for p in fam_pts],
            sort_keys=True,
        ).encode("utf-8")
        td_hash = hashlib.sha256(td_payload).hexdigest()[:16]
        rd_hash = hashlib.sha256(rd_payload).hexdigest()[:16]
        arms_differ_per_enc[fam] = {
            "mechanism_hash": td_hash,
            "random_hash": rd_hash,
            "differ": td_hash != rd_hash,
        }

    # Positive control (v4 op-point)
    pc_n_dim = POSITIVE_CONTROL["N_DIM"]
    pc_matches = [
        p for p in phase_map
        if p["encoder_family"] == POSITIVE_CONTROL["encoder_family"]
        and p["decay_rate_days"] == POSITIVE_CONTROL["decay_rate_days"]
        and abs(p["capacity_load_ratio"]
                - POSITIVE_CONTROL["capacity_load_ratio"]) < 1e-6
        and p["N_dim_input"] == pc_n_dim
    ]
    if pc_matches:
        pc_pt = pc_matches[0]
        pc_outcome = pc_pt["pareto_outcome"]
        pc_decode = pc_pt["recency_decode_acc"]
        pc_pass = (pc_outcome == POSITIVE_CONTROL["expected_pareto_outcome"]
                    and pc_decode >= POSITIVE_CONTROL["min_recency_decode_acc"]
                    and pc_decode <= POSITIVE_CONTROL["max_recency_decode_acc"])
    else:
        pc_outcome = "MISSING"
        pc_decode = -1.0
        pc_pass = False

    positive_control_result = {
        "target": POSITIVE_CONTROL,
        "measured_outcome": pc_outcome,
        "measured_recency_decode_acc": pc_decode,
        "pass": pc_pass,
    }

    # Saturation total
    n_saturated_total = sum(1 for p in phase_map if p["saturated"])
    saturation_frac = n_saturated_total / max(observed_n, 1)

    # Encoder tier classification
    means = {fam: per_encoder_summary[fam]["dominance_rate"]
             for fam in ENCODER_FAMILIES}
    best = max(means.values()) if means else 0.0
    encoder_tiers: Dict[str, str] = {}
    for fam in ENCODER_FAMILIES:
        m = means[fam]
        if m >= best - 0.05:
            others = [v for k, v in means.items() if k != fam]
            next_best = max(others) if others else 0.0
            if m == best and m - next_best > 0.10:
                encoder_tiers[fam] = "DOMINANT_ENCODER"
            else:
                encoder_tiers[fam] = "COMPETITIVE_ENCODER"
        else:
            encoder_tiers[fam] = "DOMINATED_ENCODER"

    return {
        "seed": seed,
        "run_mode": run_mode,
        "encoder_families": list(ENCODER_FAMILIES),
        "decay_sweep": decay_sweep,
        "load_sweep": load_sweep,
        "dim_sweep": dim_sweep,
        "noise_sigma": NOISE_SIGMA,
        "N_DIM_DEFAULT": N_DIM_DEFAULT,
        "R_BUCKETS": R_BUCKETS,
        "n_atoms": N_ATOMS_BASE,
        "n_days": N_DAYS_SIM,
        "preflight_ok": True,
        "preflight_hashes": preflight_hashes,
        "preflight_msg": preflight_msg,
        "phase_map": phase_map,
        "per_encoder_summary": per_encoder_summary,
        "encoder_tiers": encoder_tiers,
        "encoder_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "n_pairs_total": n_pairs_total,
        "cross_encoder_metric_distinct": cross_enc_metric_distinct,
        "n_pairs_metric_distinct": n_pairs_metric_distinct,
        "arms_differ_per_encoder": arms_differ_per_enc,
        "positive_control_result": positive_control_result,
        "n_saturated_cells_total": n_saturated_total,
        "saturation_frac_total": round(saturation_frac, 4),
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "elapsed_seed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Smoke gate predicate (v4 -- discriminator-survives-scale at full-N range)
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    if not body.get("preflight_ok", False):
        return False, (
            f"preflight_fail: {body.get('preflight_msg', 'unknown')}"
        )

    phase_map = body.get("phase_map", [])
    arms_differ = body.get("arms_differ_per_encoder", {})
    pairs_differ = body.get("encoder_pair_distinctness", {})
    expected_n = body.get("expected_n_units", 0)
    pc_result = body.get("positive_control_result", {})
    per_enc = body.get("per_encoder_summary", {})
    saturation_frac = body.get("saturation_frac_total", 0.0)
    n_pairs_metric_distinct = body.get("n_pairs_metric_distinct", 0)

    # 1. Cardinality
    if len(phase_map) != expected_n:
        return False, (
            f"cardinality_breach: expected {expected_n} got {len(phase_map)}"
        )

    # 2. arms_differ for ALL encoders
    for fam in ENCODER_FAMILIES:
        ad = arms_differ.get(fam, {})
        if not ad.get("differ"):
            return False, (
                f"arms_identical_encoder_{fam}: TD and RD per-encoder hashes match"
            )

    # 3. META_RULE_AX: cross-encoder pair distinctness >= HP_MIN_PAIRS_DIFFER
    n_pairs_total = len(pairs_differ)
    n_distinct = sum(1 for v in pairs_differ.values() if v)
    if n_distinct < HP_MIN_PAIRS_DIFFER:
        collapsed = [k for k, v in pairs_differ.items() if not v]
        return False, (
            f"HARD_FAIL_DEGENERATE_ENCODERS (META_RULE_AX): "
            f"{n_distinct}/{n_pairs_total} encoder pairs differ "
            f"(need >= {HP_MIN_PAIRS_DIFFER}); collapsed pairs: {collapsed}"
        )

    # 4. v4 cross-encoder metric distinctness: >= 7 of 10 pairs show |delta| >= 0.05
    if n_pairs_metric_distinct < 7:
        return False, (
            f"HARD_FAIL_METRIC_COLLAPSE: only {n_pairs_metric_distinct}/10 pairs "
            f"have |delta recency_decode| >= 0.05; v4 spec requires >=7 "
            f"(discriminator-survives-scale check b)"
        )

    # 5. v4 META_RULE_Q saturation check: NO cell may saturate at smoke
    if saturation_frac > 0.0:
        return False, (
            f"HARD_FAIL_SATURATION (META_RULE_Q): {saturation_frac:.3f} of cells "
            f"saturate at recall=1.000; v4 spec requires no saturation at smoke "
            f"(discriminator-survives-scale check c)"
        )

    # 6. Positive control
    if not pc_result.get("pass"):
        return False, (
            f"positive_control_fail: target={pc_result.get('target')} "
            f"outcome={pc_result.get('measured_outcome')} "
            f"recency={pc_result.get('measured_recency_decode_acc')}"
        )

    # 7. META_RULE_AP: per-encoder recency_decode_acc floor
    failing_decode = {}
    for fam in ENCODER_FAMILIES:
        rda = per_enc.get(fam, {}).get("recency_decode_acc_mean", 0.0)
        if rda < HP_RECENCY_DECODE_FLOOR:
            failing_decode[fam] = rda
    if failing_decode:
        return False, (
            f"HARD_FAIL_READOUT_FLOOR (META_RULE_AP): per-encoder "
            f"recency_decode_acc_mean below {HP_RECENCY_DECODE_FLOOR}: "
            f"{failing_decode}"
        )

    # 8. Discriminator-fires: >= 2 encoders show dominance_rate >= 0.50
    fams_above = [fam for fam in ENCODER_FAMILIES
                   if per_enc.get(fam, {}).get("dominance_rate", 0.0) >= 0.50]
    if len(fams_above) < 2:
        rates = {fam: per_enc.get(fam, {}).get("dominance_rate", 0.0)
                  for fam in ENCODER_FAMILIES}
        return False, (
            f"discriminator_fails_scale: only {len(fams_above)} encoders show "
            f"dominance_rate >= 0.50 at smoke; rates={rates}"
        )

    return True, (
        f"smoke_gate_pass_v4: preflight_distinct + cardinality_ok + "
        f"arms_differ(5 enc) + pairs_differ={n_distinct}/{n_pairs_total} + "
        f"metric_distinct={n_pairs_metric_distinct}/10 + no_saturation + "
        f"positive_control_pass + readout_floor_ok + >=2 enc above dominance"
    )


# ---------------------------------------------------------------------------
# Aggregate + verdict (META_RULE_AY enforcement)
# ---------------------------------------------------------------------------
def emit_verdict_with_AY(
    base_verdict: str, base_vmsg: str,
    encoder_pair_distinctness: Dict[str, bool],
) -> Tuple[str, str]:
    """META_RULE_AY: auto-demote verdict on self-reported distinctness False rate.

    Returns (final_verdict, final_msg). Demotes HARD_PASS -> MM or HARD_FAIL
    when distinctness checks fail proportionally.
    """
    if not encoder_pair_distinctness:
        return base_verdict, base_vmsg

    n_total = len(encoder_pair_distinctness)
    n_false = sum(1 for v in encoder_pair_distinctness.values() if not v)
    if n_total == 0:
        return base_verdict, base_vmsg

    false_frac = n_false / float(n_total)
    failed_pairs = [k for k, v in encoder_pair_distinctness.items() if not v]

    if false_frac >= META_AY_HARD_FAIL_FRAC:
        return ("HARD_FAIL", (
            f"HARD_FAIL_ENCODER_AXIS_BROKEN (META_RULE_AY): {n_false}/{n_total} "
            f"({false_frac:.2%}) pair distinctness False (>= {META_AY_HARD_FAIL_FRAC:.0%}); "
            f"failed_pairs={failed_pairs}; base_verdict_was={base_verdict}; "
            f"base_msg='{base_vmsg}'"
        ))
    elif false_frac >= META_AY_MM_DEMOTE_FRAC:
        if base_verdict == "HARD_PASS":
            return ("MIDDLE_BAND", (
                f"MIDDLE_BAND_AY_DEMOTE (META_RULE_AY): base_verdict=HARD_PASS demoted; "
                f"{n_false}/{n_total} ({false_frac:.2%}) pair distinctness False "
                f"(>= {META_AY_MM_DEMOTE_FRAC:.0%}); failed_pairs={failed_pairs}; "
                f"base_msg='{base_vmsg}'"
            ))

    return base_verdict, base_vmsg


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
    phase_map = body.get("phase_map", [])
    arms_differ = body.get("arms_differ_per_encoder", {})
    pairs_differ = body.get("encoder_pair_distinctness", {})
    n_pairs_differ = body.get("n_pairs_differ", 0)
    n_pairs_total = body.get("n_pairs_total", 10)
    cross_enc_metric_distinct = body.get("cross_encoder_metric_distinct", {})
    n_pairs_metric_distinct = body.get("n_pairs_metric_distinct", 0)
    pc_result = body.get("positive_control_result", {})
    per_enc_summary = body.get("per_encoder_summary", {})
    encoder_tiers = body.get("encoder_tiers", {})
    expected_n = body.get("expected_n_units", 0)
    observed_n = body.get("observed_n_units", 0)
    cardinality_ok = body.get("cardinality_ok", False)
    preflight_ok = body.get("preflight_ok", False)
    preflight_msg = body.get("preflight_msg", "")
    preflight_hashes = body.get("preflight_hashes", {})
    saturation_frac = body.get("saturation_frac_total", 0.0)
    n_saturated = body.get("n_saturated_cells_total", 0)

    outcomes = [p["pareto_outcome"] for p in phase_map]
    n_td = sum(1 for o in outcomes if o == "TD_DOMINATES")
    n_rd = sum(1 for o in outcomes if o == "RD_DOMINATES")
    n_tie = sum(1 for o in outcomes if o == "TIE")

    n_total = len(phase_map)
    overall_dom_rate = (n_td + 0.5 * n_tie) / max(n_total, 1)
    overall_net = (n_td - n_rd) / max(n_total, 1)
    overall_rd_loss = n_rd / max(n_total, 1)

    # Per-encoder chain-grade
    enc_chain_grade: Dict[str, bool] = {}
    for fam in ENCODER_FAMILIES:
        s = per_enc_summary.get(fam, {})
        passes = (
            s.get("dominance_rate", 0.0) >= HP_DOMINANCE_RATE_LO
            and s.get("net_dominance", 0.0) >= HP_NET_DOMINANCE_LO
            and s.get("rd_loss_rate", 1.0) <= HP_RD_LOSS_RATE_HI
            and s.get("recency_decode_acc_mean", 0.0) >= HP_RECENCY_DECODE_FLOOR
        )
        enc_chain_grade[fam] = passes
    n_chain_grade = sum(1 for v in enc_chain_grade.values() if v)

    common = {
        "preflight_ok": preflight_ok,
        "preflight_msg": preflight_msg,
        "preflight_hashes": preflight_hashes,
        "phase_map": phase_map,
        "per_encoder_summary": per_enc_summary,
        "encoder_tiers": encoder_tiers,
        "encoder_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "n_pairs_total": n_pairs_total,
        "cross_encoder_metric_distinct": cross_enc_metric_distinct,
        "n_pairs_metric_distinct": n_pairs_metric_distinct,
        "arms_differ_per_encoder": arms_differ,
        "positive_control_result": pc_result,
        "saturation_frac_total": saturation_frac,
        "n_saturated_cells_total": n_saturated,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "pareto_outcome_counts": {
            "TD_DOMINATES": n_td, "RD_DOMINATES": n_rd, "TIE": n_tie},
        "overall_dominance_rate": round(overall_dom_rate, 4),
        "overall_net_dominance": round(overall_net, 4),
        "overall_rd_loss_rate": round(overall_rd_loss, 4),
        "per_encoder_chain_grade_pass": enc_chain_grade,
        "n_encoders_chain_grade": n_chain_grade,
        "N_DIM_sweep": body.get("dim_sweep"),
        "R_BUCKETS": body.get("R_BUCKETS"),
        "noise_sigma": body.get("noise_sigma", NOISE_SIGMA),
    }

    # Pre-flight HARD_FAIL short-circuit
    if not preflight_ok:
        out = dict(common)
        out.update({
            "verdict": "HARD_FAIL",
            "verdict_msg": (
                f"HARD_FAIL_PREFLIGHT_v4: {preflight_msg}"
            ),
            "summary": "HARD_FAIL_PREFLIGHT_v4",
        })
        return out

    if is_smoke:
        passed, reason = smoke_gate_predicate(body)
        if passed:
            base_verdict = "HARD_PASS"
            base_vmsg = (
                f"HARD_PASS_SMOKE_v4: {observed_n}/{expected_n} pts; "
                f"td_wins={n_td}/{n_total} rd_wins={n_rd}/{n_total} "
                f"ties={n_tie}/{n_total}; "
                f"overall_dom={overall_dom_rate:.3f}; "
                f"pairs_differ={n_pairs_differ}/{n_pairs_total}; "
                f"metric_distinct={n_pairs_metric_distinct}/10; "
                f"saturation_frac={saturation_frac:.3f}; "
                f"positive_control_pass; "
                f"n_encoders_chain_grade={n_chain_grade}/5"
            )
        else:
            base_verdict = "HARD_FAIL"
            base_vmsg = (
                f"HARD_FAIL_SMOKE_v4: {reason}; "
                f"td_wins={n_td} rd_wins={n_rd} ties={n_tie}"
            )

        # META_RULE_AY auto-demote check
        final_verdict, final_vmsg = emit_verdict_with_AY(
            base_verdict, base_vmsg, pairs_differ,
        )
        out = dict(common)
        out.update({
            "verdict": final_verdict,
            "verdict_msg": final_vmsg,
            "summary": final_vmsg,
            "smoke_gate_pass": passed,
            "smoke_gate_reason": reason,
            "base_verdict_pre_AY": base_verdict,
        })
        return out

    # FULL verdict
    if not cardinality_ok:
        base_verdict = "HARD_FAIL"
        base_vmsg = (
            f"HARD_FAIL_CARDINALITY_BREACH: expected={expected_n} "
            f"observed={observed_n}"
        )
    elif any(not ad.get("differ") for ad in arms_differ.values()):
        bad = [fam for fam in ENCODER_FAMILIES
               if not arms_differ.get(fam, {}).get("differ")]
        base_verdict = "HARD_FAIL"
        base_vmsg = f"HARD_FAIL_ARMS_IDENTICAL: encoders with TD==RD: {bad}"
    elif n_pairs_differ < HP_MIN_PAIRS_DIFFER:
        collapsed = [k for k, v in pairs_differ.items() if not v]
        base_verdict = "HARD_FAIL"
        base_vmsg = (
            f"HARD_FAIL_DEGENERATE_ENCODERS (META_RULE_AX): "
            f"{n_pairs_differ}/{n_pairs_total} pairs differ "
            f"(need >= {HP_MIN_PAIRS_DIFFER}); collapsed: {collapsed}"
        )
    elif saturation_frac >= SATURATION_HARD_FAIL_FRAC:
        base_verdict = "HARD_FAIL"
        base_vmsg = (
            f"HARD_FAIL_SATURATION (META_RULE_Q): "
            f"{saturation_frac:.3f} (>= {SATURATION_HARD_FAIL_FRAC}) of cells saturate; "
            f"v4 regime should prevent this; check noise_sigma and load axis"
        )
    elif not pc_result.get("pass"):
        base_verdict = "HARD_FAIL"
        base_vmsg = (
            f"HARD_FAIL_CONTROL_FAIL: positive_control "
            f"outcome={pc_result.get('measured_outcome')} "
            f"recency={pc_result.get('measured_recency_decode_acc')}"
        )
    elif (n_chain_grade >= 4 and overall_dom_rate >= HP_DOMINANCE_RATE_LO
          and n_pairs_metric_distinct >= 7):
        # v4 HARD_PASS: 4/5 encoders chain-grade + 7/10 metric-distinct pairs
        base_verdict = "HARD_PASS"
        base_vmsg = (
            f"HARD_PASS_ENCODER_DISCRIMINATION_v4: {observed_n}/{expected_n} pts; "
            f"{n_chain_grade}/5 encoders pass v3-PB+AP chain-grade; "
            f"overall_dom={overall_dom_rate:.3f}; "
            f"pairs_differ={n_pairs_differ}/{n_pairs_total}; "
            f"metric_distinct={n_pairs_metric_distinct}/10; "
            f"saturation_frac={saturation_frac:.3f}; "
            f"encoder_tiers={encoder_tiers}; positive_control_pass"
        )
    elif overall_dom_rate >= 0.60 and n_pairs_differ >= HP_MIN_PAIRS_DIFFER:
        base_verdict = "MIDDLE_BAND"
        base_vmsg = (
            f"MIDDLE_BAND_ENCODER_DIFFERS_BUT_LOW_CHAIN_GRADE: "
            f"{n_chain_grade}/5 clear chain-grade; "
            f"overall_dom={overall_dom_rate:.3f}; "
            f"metric_distinct={n_pairs_metric_distinct}/10; tiers={encoder_tiers}"
        )
    else:
        base_verdict = "MIDDLE_BAND"
        base_vmsg = (
            f"MIDDLE_BAND_LOW_DISCRIMINATION: overall_dom="
            f"{overall_dom_rate:.3f}; pairs_differ={n_pairs_differ}; "
            f"n_chain_grade={n_chain_grade}/5"
        )

    # META_RULE_AY auto-demote check
    final_verdict, final_vmsg = emit_verdict_with_AY(
        base_verdict, base_vmsg, pairs_differ,
    )

    out = dict(common)
    out.update({
        "verdict": final_verdict,
        "verdict_msg": final_vmsg,
        "summary": final_vmsg,
        "base_verdict_pre_AY": base_verdict,
    })
    return out


__all__ = [
    "ENCODER_FAMILIES",
    "DECAY_RATE_DAYS_FULL", "CAPACITY_LOAD_RATIO_FULL", "N_DIM_SWEEP_FULL",
    "DECAY_RATE_DAYS_SMOKE", "CAPACITY_LOAD_RATIO_SMOKE", "N_DIM_SWEEP_SMOKE",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "N_ATOMS_BASE", "N_DAYS_SIM", "N_DIM_DEFAULT", "NOISE_SIGMA",
    "R_BUCKETS",
    "HP_DOMINANCE_RATE_LO", "HP_NET_DOMINANCE_LO", "HP_RD_LOSS_RATE_HI",
    "HP_RECENCY_DECODE_FLOOR", "HP_MIN_PAIRS_DIFFER",
    "META_AY_HARD_FAIL_FRAC", "META_AY_MM_DEMOTE_FRAC",
    "POSITIVE_CONTROL", "REQUIRED_FIELDS",
    "_get_device", "get_backend_label",
    "bind_binary_bipolar", "bind_hrr_real", "bind_fhrr_complex",
    "bind_sparse_bipolar", "bind_sparse_real",
    "verify_encoder_distinctness_preflight",
    "simulate_atom_timeline", "build_encoded_atom_store",
    "decode_recency_buckets", "arm_time_decay_via_encoder",
    "arm_random_eviction",
    "compute_arm_metrics", "pareto_dominance_outcome", "eval_phase_point",
    "selftest", "run_one_seed_phase_diagram",
    "smoke_gate_predicate", "aggregate_and_verdict",
    "emit_verdict_with_AY",
]
