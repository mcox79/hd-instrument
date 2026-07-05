# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (synth/real/noorder recovered-index arrays hash-distinct)
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb/capacity-feasibility: envelope ceiling GEN_svo_1k=1.0 clean-iid is the analytic upper
#     bound; real correlated fillers can only reduce it (declared; discriminator reachable side)
# - baseline_in_band: noorder_ctrl (order destroyed) MUST collapse (< real_R16); real_R1 mid-band
# - discriminator survives scale: decode measured AT full N=8192 in BOTH smoke and full (same V,
#     fewer trials/seeds in smoke); noorder-collapse + synth-ceiling asserts fire in smoke
# - HARD_PASS strictly above floor (exact_ordered>=0.70 AND per_term>=envelope_ceiling-0.10)
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
#
# GENERATION DECODER ROUND-TRIP v1 (the substrate's "mouth")
# ==========================================================
# The clean INVERSE of the concept encoder: read a bound proposition HV back into an
# ORDERED surface token sequence, faithful-BY-CONSTRUCTION (every emitted token traces
# to one unbind op on a specific bound structure). Authorized by the factorization
# envelope GO verdict (MEASURED@data/exp_factorization_envelope_v1/metrics.json:
# GEN_svo_1k mean=1.000 F=2 V=1024 D=3 N=8192 R=16 -- the clean-iid UPPER BOUND).
#
# A proposition is a SUPERPOSITION of D bound TERMS; each term = bind(position_role, filler),
# exactly F=2 factors (the envelope HARD wall: F=3 cliffs 0.217, F=4 dead 0.000):
#     p = sum_{d=0..D-1}  pos_book[d] * lex[ toks[d] ]        (bipolar BSC, elementwise product)
# Position IS the role (2 factors), NOT an added 3rd factor. Order is CARRIED in the vector
# via position binding at encode (Stage B), not invented at decode.
#
# 3 stages (inverse of encode->reason->generate):
#   Stage A -- FACTOR:  full resonator recovers the D (position, filler) tuples via iterative
#              unbind + cleanup + real-valued explaining-away peel-off. High-energy lever =
#              RESTARTS parallel random inits (batched matmul). Reuses the VET'd envelope
#              resonator (experiments/exp_factorization_envelope_v1.py:resonate).
#   Stage B -- ORDER:   sort recovered tuples by recovered position index -> ordered sequence.
#   Stage C -- CLEANUP: codebook argmax per factor (the resonator's decode step). Same-slot
#              collisions are prevented BY CONSTRUCTION by PROTECTED/INDEX position binding
#              pos_book[k]=roll(base,k) (E3 permutation-indexed binding; the VET-confirmed
#              MM_STANDARD hub-rescue mechanism, CITED@exp_deep_reasoning_hub_robustness_v1
#              commit 5eb05b4e5 -- fully covers deg5-7 fillers).
#
# CLEAN-TEST DISCIPLINE (USER-locked): the deliverable arm uses REAL correlated concept fillers
# (real BGE concept vectors -> fixed random projection to N -> sign() -> bipolar, preserving the
# real cos-cone). Synthetic iid bipolar = the envelope ceiling (positive control). The gap
# between them is exactly the point: the clean-iid 1.0 is the ceiling; this cell measures the
# REALIZED round-trip on real correlated fillers (expect lower).
#
# NOTE on algebra: propositions are bound in bipolar BSC (elementwise product) per the committed
# wave14e/wave14b algebra, matching the envelope's Stage-A regime. The concept encoder is a sparse
# block code (GSBC); binding propositions directly in the sparse-block geometry is the v2 STRATEGIC
# path (memo section "STRATEGIC FLAG") and OUT OF SCOPE here -- this cell is the bipolar-BSC
# realization, the honest ceiling for THAT algebra.
#
# Sources (CITED@):
#  - data/exp_factorization_envelope_v1/metrics.json  (envelope GO; GEN_svo_1k=1.000 ceiling)
#  - experiments/exp_factorization_envelope_v1.py      (resonator + peel-off, reused)
#  - experiments/exp_deep_reasoning_hub_robustness_v1.py (protected/index binding, roles-known resonator)
#  - Resonator Networks 1&2, Frady/Kent/Olshausen/Sommer, Neural Computation 2020 (arxiv 1906.11684)
#
# ASCII-only. CPU default (task-mandated CPU probe; no LLM, no GPU). Read-only on substrate.
# Run: python experiments/exp_generation_decoder_roundtrip_v1.py [--self-test | --smoke]

from __future__ import annotations

import io
import json
import os
import platform
import sys
import time
import traceback
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)  # flush progress on newline (17. PRINT-PROGRESS)

torch.set_num_threads(8)
DEVICE = torch.device("cpu")

ANCHOR_NAME = "generation_decoder_roundtrip_v1"
REPO = Path(__file__).resolve().parents[1]

# Production dims (N=8192 == substrate compositional default == verified envelope regime).
# Anchor name intentionally omits a _n8192 suffix: PROT-018/019 are opt-in for sweep cells;
# this is a small-grid round-trip that runs in minutes, not a large-N battery needing 6h floor.
N_DIM = 8192
BGE_DIM = 1024
BGE_CACHE = REPO / "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz"

RESTARTS = 16          # high-energy parallel random restarts (redundancy lever; envelope decisive)
RESTARTS_LO = 1        # single-shot floor
MAX_ITER = 40          # resonator iterations per restart (early-stop on fixed point)
SEEDS = (7, 13, 19)

# MEASURED@data/exp_factorization_envelope_v1/metrics.json:results.GEN_svo_1k.mean = 1.000
ENVELOPE_CEILING = 1.0
# Pre-registered bands (memo notes/decoder_design_..._2026-07-05.md):
HP_EXACT_ORDERED = 0.70            # HARD_PASS floor for exact-ordered-sequence match
HP_PERTERM_TOL = 0.10             # per-term must be within 0.10 of envelope ceiling
HF_EXACT_ORDERED = 0.30            # HARD_FAIL ceiling for exact-ordered-sequence


# ============================================================
# Defensive error-checking helpers (13/16)
# ============================================================


def _out_dir() -> Path:
    """Output dir honors HDLAB_EXP_NAME (queue gate isolation for selftest/smoke)."""
    name = os.environ.get("HDLAB_EXP_NAME")
    if name:
        return REPO / f"data/exp_{name}"
    return REPO / f"data/exp_{ANCHOR_NAME}"


def _say(msg: str) -> None:
    print(msg, flush=True)


def _write_start_marker(output_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, output_dir / "_start_marker.json")


def _heartbeat(output_dir: Path, unit_idx: int, total_units: int, t0: float, extra=None) -> None:
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": unit_idx,
        "total_units": total_units,
        "elapsed_s": round(time.perf_counter() - t0, 2),
    }
    if extra:
        row["extra"] = extra
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_metrics_atomic(output_dir: Path, metrics: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, output_dir / "metrics.json")  # atomic (META_RULE_AH)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "anchor_name": ANCHOR_NAME,
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
    }
    _write_metrics_atomic(output_dir, diag)


# ============================================================
# Codebooks (bipolar BSC)
# ============================================================


def _bipolar(shape, gen: torch.Generator) -> torch.Tensor:
    raw = torch.rand(shape, generator=gen)
    return (2.0 * (raw > 0.5).float() - 1.0).to(DEVICE)


def make_positions(P: int, N: int, gen: torch.Generator) -> torch.Tensor:
    """Protected / index position codebook: pos[k] = roll(base, k). (P,N) bipolar.

    E3 permutation-indexed binding (roll) -- the VET-confirmed hub-rescue mechanism:
    D distinct slots get distinct roll powers so same-position collisions cannot occur.
    Rolls of one random bipolar base are near-orthogonal (cross-corr ~ 1/sqrt(N))."""
    base = _bipolar((N,), gen)
    return torch.stack([torch.roll(base, shifts=k) for k in range(P)], dim=0)


def make_synth_lexicon(V: int, N: int, gen: torch.Generator) -> torch.Tensor:
    """Clean iid bipolar lexicon = the envelope ceiling (positive control). (V,N)."""
    return _bipolar((V, N), gen)


_SEM_CACHE = {"sem": None}
_PROJ_CACHE = {}


def _load_sem() -> np.ndarray:
    """Load + cache the real concept BGE semantic matrix (1.3GB npz; load once per process)."""
    if _SEM_CACHE["sem"] is None:
        if not BGE_CACHE.exists():
            raise FileNotFoundError(f"BGE cache missing (local-only artifact): {BGE_CACHE}")
        _SEM_CACHE["sem"] = np.load(BGE_CACHE)["semantic"]  # (177899, BGE_DIM) float
    return _SEM_CACHE["sem"]


def _proj(bge_dim: int, N: int) -> np.ndarray:
    """Fixed (lexicon-independent) random Gaussian projection BGE_DIM->N, cached per (dim,N)."""
    key = (bge_dim, N)
    if key not in _PROJ_CACHE:
        proj_rng = np.random.default_rng(770077)                     # SAME projection every seed
        _PROJ_CACHE[key] = (proj_rng.standard_normal((bge_dim, N)).astype(np.float32)
                            / np.sqrt(bge_dim))
    return _PROJ_CACHE[key]


def make_real_lexicon(V: int, N: int, seed: int) -> torch.Tensor:
    """REAL correlated concept fillers: sample V real concept BGE vectors, fixed random
    projection BGE_DIM->N, sign() -> bipolar. Preserves the real cos-cone (correlated
    fillers = clean-test discipline). (V,N) bipolar."""
    sem = _load_sem()
    M = sem.shape[0]
    rng = np.random.default_rng(20260705 + seed)
    rows = rng.choice(M, size=V, replace=False)
    X = sem[rows].astype(np.float32)                                  # (V, BGE_DIM) real, correlated
    Pmat = _proj(sem.shape[1], N)
    Y = X @ Pmat                                                     # (V, N) real (JL-preserves inner products)
    B = np.where(Y >= 0.0, 1.0, -1.0).astype(np.float32)            # bipolar; sign preserves correlation
    return torch.from_numpy(B).to(DEVICE)


def mean_pair_cos(book: torch.Tensor, n_sample: int, gen: torch.Generator) -> float:
    """Mean pairwise cosine over a random sample of rows (correlation-cone diagnostic)."""
    V = book.shape[0]
    m = min(n_sample, V)
    idx = torch.randperm(V, generator=gen)[:m]
    B = book[idx]
    Bn = B / (B.norm(dim=1, keepdim=True) + 1e-12)
    S = Bn @ Bn.t()
    off = S[~torch.eye(m, dtype=torch.bool)]
    return float(off.mean().item())


# ============================================================
# Stage A resonator (reused from envelope; supports asymmetric factor codebooks)
# ============================================================


def resonate(residual: torch.Tensor, books, N: int, restarts: int, max_iter: int,
             gen: torch.Generator):
    """Factor ONE product-term (F=2: position x filler) out of a real-valued residual.

    books = [pos_book (P,N), lex_book (V,N)]. Batched over `restarts` random inits.
    Returns (best_tuple=(p_idx,f_idx), best_recon (N,), best_dot)."""
    F = len(books)
    est = [_bipolar((restarts, N), gen) for _ in range(F)]
    prev_sign = None
    for _ in range(max_iter):
        for i in range(F):
            other = torch.ones((restarts, N), device=DEVICE)
            for j in range(F):
                if j != i:
                    other = other * est[j]
            unbound = residual.unsqueeze(0) * other            # (restarts, N)
            scores = unbound @ books[i].t() / N                 # (restarts, V_i)
            recon = scores @ books[i]                           # (restarts, N)
            s = torch.sign(recon)
            est[i] = torch.where(s == 0, torch.ones_like(s), s)
        cur_sign = torch.cat(est, dim=1)
        if prev_sign is not None and torch.equal(cur_sign, prev_sign):
            break
        prev_sign = cur_sign
    idx = []
    for i in range(F):
        sims = est[i] @ books[i].t() / N
        idx.append(sims.argmax(dim=1))                          # (restarts,)
    idx = torch.stack(idx, dim=0)                               # (F, restarts)
    recon = torch.ones((restarts, N), device=DEVICE)
    for i in range(F):
        recon = recon * books[i][idx[i]]
    dots = (recon * residual.unsqueeze(0)).sum(dim=1)           # (restarts,)
    best = int(dots.argmax().item())
    best_tuple = (int(idx[0, best].item()), int(idx[1, best].item()))
    return best_tuple, recon[best], float(dots[best].item())


def peel_decode(prop: torch.Tensor, pos_book, lex_book, D: int, restarts: int,
                max_iter: int, gen: torch.Generator):
    """Stage A: recover D (pos,filler) tuples by explaining-away peel-off.
    Returns list of (p_idx, f_idx, dot)."""
    residual = prop.clone()
    out = []
    for _ in range(D):
        tup, recon, dot = resonate(residual, [pos_book, lex_book], N_DIM, restarts, max_iter, gen)
        out.append((tup[0], tup[1], dot))
        residual = residual - recon                             # exact real-valued peel-off
    return out


def roles_known_decode(prop: torch.Tensor, pos_D, lex_book, D: int, n_iters: int):
    """ROBUSTNESS arm: positions KNOWN (the decoder owns its role vectors). Iterative
    explaining-away resonator (bipolar analog of the hub-rescue recover_iterative).
    Order = slot index (no sort needed). Returns filler idx per slot (list length D)."""
    V = lex_book.shape[0]
    # init: unbind each slot by its known position, cleanup filler
    est = torch.empty(D, dtype=torch.long, device=DEVICE)
    for d in range(D):
        q = prop * pos_D[d]
        est[d] = int((q @ lex_book.t() / N_DIM).argmax().item())
    for _ in range(n_iters):
        bound = pos_D * lex_book[est]                           # (D,N) reconstruct each slot
        total = bound.sum(0)                                    # (N,)
        new = est.clone()
        for d in range(D):
            resid = prop - (total - bound[d])                  # remove OTHER slots
            q = resid * pos_D[d]
            new[d] = int((q @ lex_book.t() / N_DIM).argmax().item())
        if torch.equal(new, est):
            break
        est = new
    return [int(x) for x in est.tolist()]


# ============================================================
# Encode + metrics
# ============================================================


def encode_prop(toks, pos_book, lex_book, shared_pos: bool = False) -> torch.Tensor:
    """Encode ordered token sequence -> bound proposition (bipolar BSC superposition).
    shared_pos=True binds EVERY slot to position 0 (destroys order = noorder control)."""
    D = len(toks)
    s = torch.zeros(N_DIM, device=DEVICE)
    for d, t in enumerate(toks):
        p = pos_book[0] if shared_pos else pos_book[d]
        s = s + p * lex_book[t]
    return s


def _multiset_match(recovered, truth) -> int:
    """Order-free multiplicity-aware match count."""
    pool = list(recovered)
    hits = 0
    for x in truth:
        if x in pool:
            pool.remove(x)
            hits += 1
    return hits


def score_tuples(recovered_tuples, toks):
    """recovered_tuples: list of (p,f,dot). toks: ordered truth fillers (position d -> toks[d]).
    Returns (per_term, exact_ordered, per_token_cleanup)."""
    D = len(toks)
    truth_tuples = [(d, toks[d]) for d in range(D)]
    rec_pf = [(p, f) for (p, f, _dot) in recovered_tuples]
    # 1. per-term recovery = order-free (pos,filler) tuple match (envelope-metric analog)
    per_term = _multiset_match(rec_pf, truth_tuples) / D
    # 2. exact ordered: place each recovered filler at its recovered position (max-dot wins ties)
    out = [-1] * D
    best_dot = [-1e30] * D
    for (p, f, dot) in recovered_tuples:
        if 0 <= p < D and dot > best_dot[p]:
            best_dot[p] = dot
            out[p] = f
    exact = 1.0 if out == list(toks) else 0.0
    # 3. per-token cleanup = order-free FILLER match (isolates Stage C; ignores position)
    per_token = _multiset_match([f for (_p, f, _d) in recovered_tuples], list(toks)) / D
    return per_term, exact, per_token


def score_rolesknown(est_fillers, toks):
    """est_fillers: filler idx per slot (order = slot). Returns (per_term, exact, per_token)."""
    D = len(toks)
    exact = 1.0 if list(est_fillers) == list(toks) else 0.0
    per_token = _multiset_match(list(est_fillers), list(toks)) / D
    per_term = sum(1 for d in range(D) if est_fillers[d] == toks[d]) / D  # position known -> per-slot
    return per_term, exact, per_token


# ============================================================
# Arm runners
# ============================================================


def sample_props(V: int, D: int, trials: int, seed: int):
    """Sample `trials` propositions, each D DISTINCT filler indices (S/V/O)."""
    rng = np.random.default_rng(90000 + seed)
    props = []
    for _ in range(trials):
        props.append([int(x) for x in rng.choice(V, size=D, replace=False)])
    return props


def run_full_arm(lex_book, pos_book, props, D, restarts, max_iter, gen, shared_pos=False):
    """Full-resonator arm over a fixed set of propositions (paired across arms)."""
    pt = ex = tk = 0.0
    rec_idx = []
    for toks in props:
        prop = encode_prop(toks, pos_book, lex_book, shared_pos=shared_pos)
        tuples = peel_decode(prop, pos_book, lex_book, D, restarts, max_iter, gen)
        a, b, c = score_tuples(tuples, toks)
        pt += a; ex += b; tk += c
        rec_idx.extend([f for (_p, f, _d) in tuples])
    n = len(props)
    return {"per_term": pt / n, "exact_ordered": ex / n, "per_token": tk / n}, rec_idx


def run_rolesknown_arm(lex_book, pos_book, props, D, n_iters, shared_pos=False):
    """Roles-known arm (positions KNOWN; the memo-mandated hub-rescue mechanism) over the
    same propositions. n_iters=0 => single-shot (init cleanup only, no explaining-away)."""
    pt = ex = tk = 0.0
    rec_idx = []
    pos_D = pos_book[:D]
    for toks in props:
        prop = encode_prop(toks, pos_book, lex_book, shared_pos=shared_pos)
        est = roles_known_decode(prop, pos_D, lex_book, D, n_iters)
        a, b, c = score_rolesknown(est, toks)
        pt += a; ex += b; tk += c
        rec_idx.extend(est)
    n = len(props)
    return {"per_term": pt / n, "exact_ordered": ex / n, "per_token": tk / n}, rec_idx


# ============================================================
# Config
# ============================================================


def get_config(mode: str):
    """mode: 'selftest' | 'smoke' | 'full'. SMOKE==FULL code path; smaller V/trials/seeds.
    All modes decode AT full N=8192 (discriminator-survives-scale: never smoke at reduced N)."""
    if mode == "selftest":
        return {"V": 128, "D": 3, "trials": 3, "seeds": (7,), "n_iters": 4}
    if mode == "smoke":
        return {"V": 256, "D": 3, "trials": 5, "seeds": (7,), "n_iters": 5}
    # full: memo config F=2 V=1024 D=3 N=8192, 3 seeds
    return {"V": 1024, "D": 3, "trials": 30, "seeds": SEEDS, "n_iters": 6}


ARMS = ["synth_rolesknown", "real_rolesknown_hi", "real_rolesknown_lo", "noorder_ctrl",
        "synth_fullreso_hi", "real_fullreso_hi"]


def run_all(mode: str, output_dir: Path, t0: float):
    cfg = get_config(mode)
    output_dir.mkdir(parents=True, exist_ok=True)  # heartbeat/start-marker target (selftest path skips _write_start_marker)
    V, D, trials, seeds, n_iters = cfg["V"], cfg["D"], cfg["trials"], cfg["seeds"], cfg["n_iters"]
    P = D  # position vocabulary = D slots

    per_seed = {a: [] for a in ARMS}
    rec_digests = {}
    cone = {}
    total_units = len(seeds) * len(ARMS)
    unit = 0
    for seed in seeds:
        gcb = torch.Generator().manual_seed(1000 + seed)
        pos_book = make_positions(P, N_DIM, gcb)
        synth_lex = make_synth_lexicon(V, N_DIM, gcb)
        real_lex = make_real_lexicon(V, N_DIM, seed)
        gd = torch.Generator().manual_seed(2000 + seed)
        cone[str(seed)] = {"real_mean_pair_cos": round(mean_pair_cos(real_lex, 400, gd), 4),
                           "synth_mean_pair_cos": round(mean_pair_cos(synth_lex, 400, gd), 4)}
        # SAME propositions for every arm at this seed -> PAIRED trials
        props = sample_props(V, D, trials, seed)
        rec = {}

        # --- PRIMARY: roles-known decoder (positions known; hub-rescue protected/index mechanism) ---
        s, rec["synth_rolesknown"] = run_rolesknown_arm(synth_lex, pos_book, props, D, n_iters)
        per_seed["synth_rolesknown"].append(s); unit += 1
        _heartbeat(output_dir, unit, total_units, t0, extra={"arm": "synth_rolesknown", "seed": seed})

        s, rec["real_rolesknown_hi"] = run_rolesknown_arm(real_lex, pos_book, props, D, n_iters)
        per_seed["real_rolesknown_hi"].append(s); unit += 1
        _heartbeat(output_dir, unit, total_units, t0, extra={"arm": "real_rolesknown_hi", "seed": seed})

        s, rec["real_rolesknown_lo"] = run_rolesknown_arm(real_lex, pos_book, props, D, 0)  # single-shot
        per_seed["real_rolesknown_lo"].append(s); unit += 1
        _heartbeat(output_dir, unit, total_units, t0, extra={"arm": "real_rolesknown_lo", "seed": seed})

        s, rec["noorder_ctrl"] = run_rolesknown_arm(real_lex, pos_book, props, D, n_iters, shared_pos=True)
        per_seed["noorder_ctrl"].append(s); unit += 1
        _heartbeat(output_dir, unit, total_units, t0, extra={"arm": "noorder_ctrl", "seed": seed})

        # --- SECONDARY: full resonator (positions ALSO recovered; Stage-A envelope-analog) ---
        gres = torch.Generator().manual_seed(3000 + seed)
        s, rec["synth_fullreso_hi"] = run_full_arm(synth_lex, pos_book, props, D, RESTARTS, MAX_ITER, gres)
        per_seed["synth_fullreso_hi"].append(s); unit += 1
        _heartbeat(output_dir, unit, total_units, t0, extra={"arm": "synth_fullreso_hi", "seed": seed})

        gres = torch.Generator().manual_seed(3100 + seed)
        s, rec["real_fullreso_hi"] = run_full_arm(real_lex, pos_book, props, D, RESTARTS, MAX_ITER, gres)
        per_seed["real_fullreso_hi"].append(s); unit += 1
        _heartbeat(output_dir, unit, total_units, t0, extra={"arm": "real_fullreso_hi", "seed": seed})

        rec_digests[str(seed)] = {a: _digest(rec[a]) for a in ARMS}
        rkh = per_seed["real_rolesknown_hi"][-1]
        rfh = per_seed["real_fullreso_hi"][-1]
        _say(f"  [seed {seed}] roles-known real: exact={rkh['exact_ordered']:.3f} "
             f"perterm={rkh['per_term']:.3f} pertok={rkh['per_token']:.3f} | "
             f"lo(single-shot)={per_seed['real_rolesknown_lo'][-1]['exact_ordered']:.3f} | "
             f"noorder={per_seed['noorder_ctrl'][-1]['exact_ordered']:.3f} | "
             f"full-reso real={rfh['exact_ordered']:.3f} synth={per_seed['synth_fullreso_hi'][-1]['exact_ordered']:.3f} | "
             f"cone_real={cone[str(seed)]['real_mean_pair_cos']:.3f}")

    def agg(arm, key):
        vals = [d[key] for d in per_seed[arm]]
        return float(np.mean(vals)), [round(float(v), 4) for v in vals]

    summary = {}
    for a in ARMS:
        pt_m, pt_v = agg(a, "per_term")
        ex_m, ex_v = agg(a, "exact_ordered")
        tk_m, tk_v = agg(a, "per_token")
        summary[a] = {
            "per_term_mean": round(pt_m, 4), "per_term_per_seed": pt_v,
            "exact_ordered_mean": round(ex_m, 4), "exact_ordered_per_seed": ex_v,
            "per_token_mean": round(tk_m, 4), "per_token_per_seed": tk_v,
        }
    return cfg, summary, rec_digests, cone


def _digest(int_list) -> str:
    import hashlib
    return hashlib.sha256(np.asarray(int_list, dtype=np.int64).tobytes()).hexdigest()


# ============================================================
# Verdict
# ============================================================


def classify(summary: dict, mode: str):
    # PRIMARY deliverable = roles-known decoder on real correlated fillers (memo-mandated
    # hub-rescue protected/index mechanism). Full resonator arms are a secondary finding.
    synth_pt = summary["synth_rolesknown"]["per_term_mean"]
    real_ex = summary["real_rolesknown_hi"]["exact_ordered_mean"]
    real_pt = summary["real_rolesknown_hi"]["per_term_mean"]
    real_lo_ex = summary["real_rolesknown_lo"]["exact_ordered_mean"]
    noorder_ex = summary["noorder_ctrl"]["exact_ordered_mean"]
    fr_synth = summary["synth_fullreso_hi"]["per_term_mean"]
    fr_real = summary["real_fullreso_hi"]["per_term_mean"]

    diag = (f"roles-known: synth_ceiling_perterm={synth_pt:.3f}; real exact={real_ex:.3f} "
            f"perterm={real_pt:.3f}; real single-shot exact={real_lo_ex:.3f}; noorder exact={noorder_ex:.3f} "
            f"(must collapse) | full-resonator perterm synth={fr_synth:.3f} real={fr_real:.3f}")

    # --- discriminator-fires gates (apply in all modes) ---
    # (a) roles-known wiring correct: synth iid ceiling recovers (>=0.90 per-slot)
    if synth_pt < 0.90:
        return "DISCRIMINATOR_DID_NOT_FIRE", (
            f"synth-iid roles-known ceiling per_term={synth_pt:.3f} < 0.90: decoder wiring FAILED "
            f"(positive control). {diag}"), False
    # (b) order mechanism real: destroying position (noorder) must collapse exact-ordered below
    #     the real arm (position binding is load-bearing for ordered readout).
    if (real_ex - noorder_ex) < 0.20:
        return "ORDER_DISCRIMINATOR_DID_NOT_FIRE", (
            f"noorder control did not collapse (real_exact={real_ex:.3f} vs noorder={noorder_ex:.3f}, "
            f"gap<0.20): ordered readout not attributable to position binding. {diag}"), True

    # --- pre-registered generation bands (memo) ---
    perterm_ok = real_pt >= (ENVELOPE_CEILING - HP_PERTERM_TOL)   # within 0.10 of ceiling
    if real_ex >= HP_EXACT_ORDERED and perterm_ok:
        return "HARD_PASS", (
            f"generation round-trip WORKS on real correlated fillers: exact-ordered={real_ex:.3f} "
            f"(>= {HP_EXACT_ORDERED}) AND per_term={real_pt:.3f} (>= ceiling {ENVELOPE_CEILING}-{HP_PERTERM_TOL}). "
            f"NOTE full-resonator(positions-unknown) collapses on correlated fillers "
            f"(real perterm={fr_real:.3f} vs synth {fr_synth:.3f}) -> known-position decode is the "
            f"right architecture; positions-unknown factorization is v2 (sparse-block resonator). {diag}"), True
    if real_ex < HF_EXACT_ORDERED:
        return "HARD_FAIL", (
            f"decoder cannot round-trip even S/V/O: exact-ordered={real_ex:.3f} (< {HF_EXACT_ORDERED}); "
            f"Stage A or C is the wall on real correlated fillers. {diag}"), True
    return "MIDDLE_BAND", (
        f"partial round-trip: exact-ordered={real_ex:.3f} in [{HF_EXACT_ORDERED},{HP_EXACT_ORDERED}); "
        f"chunking wrapper needed for propositions beyond the GO region. {diag}"), True


# ============================================================
# main
# ============================================================


def _run(mode: str) -> int:
    output_dir = _out_dir()
    t0 = time.perf_counter()
    cfg = get_config(mode)
    expected_n_units = len(cfg["seeds"]) * len(ARMS)
    _write_start_marker(output_dir, mode, expected_n_units)
    _say(f"[{ANCHOR_NAME}] mode={mode} N={N_DIM} V={cfg['V']} D={cfg['D']} "
         f"trials={cfg['trials']} seeds={cfg['seeds']} R={RESTARTS} iters={MAX_ITER}")

    cfg, summary, rec_digests, cone = run_all(mode, output_dir, t0)

    # arms_differ (META_RULE_AF): arms that should produce distinct recoveries must be bit-distinct.
    arms_differ_ok = True
    for sd, dg in rec_digests.items():
        core = [dg["real_rolesknown_hi"], dg["noorder_ctrl"], dg["real_fullreso_hi"]]
        if len(set(core)) != len(core):
            arms_differ_ok = False
    if not arms_differ_ok:
        raise AssertionError("META_RULE_AF VIOLATION: rolesknown/noorder/fullreso recovered arrays bit-identical")

    verdict, vmsg, order_ok = classify(summary, mode)
    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: substrate-native generation decoder round-trip ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": len(cfg["seeds"]),
        "config": {"N": N_DIM, "V": cfg["V"], "D": cfg["D"], "F": 2, "trials": cfg["trials"],
                   "seeds": list(cfg["seeds"]), "RESTARTS": RESTARTS, "RESTARTS_LO": RESTARTS_LO,
                   "MAX_ITER": MAX_ITER, "n_iters": cfg["n_iters"],
                   "algebra": "bipolar_BSC_elementwise_product",
                   "position_binding": "protected_index_roll_E3",
                   "real_lexicon": "BGE_concept_randproj_sign_bipolar"},
        "arms": summary,
        "controls": {"noorder_collapsed": order_ok,
                     "envelope_ceiling_GEN_svo_1k": ENVELOPE_CEILING},
        "correlation_cone": cone,
        "arms_differ_verified": arms_differ_ok,
        "recovered_digests": rec_digests,
        "bands": {"HP_exact_ordered": HP_EXACT_ORDERED, "HP_perterm_within": HP_PERTERM_TOL,
                  "HF_exact_ordered": HF_EXACT_ORDERED},
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
    }
    _write_metrics_atomic(output_dir, metrics)
    written = json.load(open(output_dir / "metrics.json"))
    assert written["run_mode"] == mode, f"RUN_MODE_MISMATCH {written['run_mode']} != {mode}"

    _say(f"\n[{ANCHOR_NAME}] {verdict}: {vmsg}")
    _say(f"[{ANCHOR_NAME}] metrics -> {output_dir / 'metrics.json'}  elapsed={elapsed:.1f}s")
    return 0


def _run_selftest() -> int:
    """Fast correctness gate for queue_add step-3 (180s cap). Writes NOTHING to canonical
    paths beyond the isolated HDLAB_EXP_NAME=<name>_selftest dir; asserts synth ceiling
    recovers and the order-control collapses. Returns 0 pass / 1 fail."""
    t0 = time.perf_counter()
    output_dir = _out_dir()
    _cfg, summary, _dg, _cone = run_all("selftest", output_dir, t0)
    synth_pt = summary["synth_rolesknown"]["per_term_mean"]
    real_ex = summary["real_rolesknown_hi"]["exact_ordered_mean"]
    noorder_ex = summary["noorder_ctrl"]["exact_ordered_mean"]
    ok = (synth_pt >= 0.90) and (real_ex - noorder_ex >= 0.0)   # ceiling recovers; order helps (>=)
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: synth_perterm={synth_pt:.3f} "
         f"(>=0.90) real_exact={real_ex:.3f} noorder_exact={noorder_ex:.3f} "
         f"[{time.perf_counter()-t0:.1f}s]")
    return 0 if ok else 1


def main() -> int:
    if "--self-test" in sys.argv:
        return _run_selftest()
    mode = "smoke" if "--smoke" in sys.argv else "full"
    return _run(mode)


if __name__ == "__main__":
    _od = None
    try:
        _od = _out_dir()
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        if _od is not None:
            _write_crash_metrics(_od, e)
        raise
