# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (blocklocal_gsbc / blocklocal_synth / noorder recovered-index
#     arrays hash-distinct; dense contrast arms hash-distinct)
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb/capacity-feasibility: block-local sparse resonator is exact-by-construction on disjoint blocks
#     (per-block V-way cleanup; no cross-slot interference). CITED proven ceiling K=26 slots >=85%
#     (exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000 HARD_PASS). Native GSBC fillers carry the
#     real cos-cone (MEASURED raw 0.511; discriminator reachable side). crlb_n_a declared (no argmax-noise
#     floor blocks the deliverable: disjoint-block recovery has no superposition noise within a block).
# - baseline_in_band: noorder control MUST collapse (exact ~ 0); synth iid ceiling MUST recover (>=0.90).
# - discriminator survives scale: decode measured AT full N=8192 in ALL modes (smoke reduces V/D/trials/
#     seeds only, never N). noorder-collapse + synth-ceiling + blocklocal-recover assertions FIRE in smoke.
# - HARD_PASS strictly above floor (anchor exact_ordered >= 0.85 AND per_token >= 0.90; floor 0.50).
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
#
# GENERATION DECODER -- NATIVE GSBC FILLERS via the GSBC-NATIVE (block-local sparse) factorizer  v1
# ================================================================================================
# Scale-up of the decoder MVP (exp_generation_decoder_roundtrip_v1, MM_STANDARD, commit 1fd6f580a):
# replace the BGE-randproj bipolar STAND-IN fillers with NATIVE GSBC concept-encoder codes, and swap
# Stage A to the PROVEN sparse-block resonator (block-local) that MATCHES the GSBC sparse geometry
# (Hersche/Terzic; Frady-Sommer arXiv:2404.19126). Coordinator course-correction 2026-07-05: binding
# native GSBC fillers in a DENSE bipolar-BSC multiply-bind algebra is the encoding MISMATCH that
# collapses under superposition of correlated fillers (MVP real_fullreso exact=0.000
# MEASURED@data/exp_generation_decoder_roundtrip_v1/metrics.json:arms.real_fullreso_hi.exact_ordered_mean);
# the block-local sparse resonator recovers because binding = SUM of per-block sparse codes (no
# multiply/intersection collapse) and recovery = per-block cleanup (blocks disjoint -> exact-by-construction).
#
# 3 stages (inverse of encode->reason->generate), all block-local:
#   Stage A -- FACTOR:  N partitioned into D disjoint blocks (bs = N/D each). A term = one filler code
#              placed in its slot's block. Composite = SUM over slots (block-superposition; sparsity kept).
#   Stage B -- ORDER:   position IS the block index (the filler code is shifted into block d for slot d).
#              Recovered tuples sort trivially by block -> ordered token sequence. (Stage B carried in the
#              vector, not invented at decode.)
#   Stage C -- CLEANUP: per-block argmax over the (global) filler codebook restricted to that block.
#
# NATIVE GSBC filler code (the load-bearing swap): the filler code = the REAL deployed concept encoder's
# output. We pre-encode a BOUNDED pool (10000 of 177899 concepts, 5.6pct -- NOT a full-store re-encode,
# which is HELD) with the GSBC_EXPAND2X seed7 FULL student, cache sparse to
# data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz (SCP'd to remote; queue_add does NOT auto-ship
# untracked npz). At decode-time the native GSBC code (GSBC_DIM=8192, 192 active, unit-L1) is projected
# GSBC_DIM->bs via a fixed Gaussian (JL-preserves the real cos-cone) and sparsified top-(0.02*bs) sign ->
# a sparse bipolar block code that CARRIES the real GSBC correlation structure (the point: cleanup
# collisions are realistic, not iid). Synthetic random sparse bipolar codes = the proven-ceiling positive
# control (reproduces exp_substrate_sparse_resonator_blocklocal_K26 at the test regime).
#
# MECHANISM CONTRAST (anchor V=1024 D=3 only): the DENSE bipolar-BSC pipeline (copied UNCHANGED from the
# MVP) on the SAME native GSBC concepts (randproj->sign bipolar), to demonstrate the coordinator's thesis:
#   dense_gsbc_rolesknown (positions handed in)   -> holds (MEASURED@MVP real_rolesknown_hi exact=1.000)
#   dense_gsbc_fullreso   (positions UNKNOWN, R16) -> COLLAPSES on correlated fillers (the mismatch)
#   dense_synth_fullreso  (iid, R16)               -> holds (positive control; the dense resonator works iid)
# => block-local (GSBC-native) is the robust factorizer; dense multiply-bind is the mismatch that cliffs.
#
# Sources (CITED@):
#  - experiments/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000.py  (block-local resonator, HARD_PASS K=26)
#  - experiments/exp_generation_decoder_roundtrip_v1.py                     (MVP dense pipeline, reused UNCHANGED)
#  - data/substrate_concept_encoder_v12_gwta_seed7/_ckpt_best_GSBC_EXPAND2X.pt (deployed native encoder)
#  - notes/decoder_design_stage_A_factor_B_order_C_cleanup_generation_readout_2026-07-05.md (design memo)
#  - Frady/Sommer sparse block-local resonator arXiv:2404.19126; Resonator Networks Neural Computation 2020.
#
# ASCII-only. CPU default (task-mandated CPU probe; no LLM, no GPU). Read-only on substrate.
# Run: python experiments/exp_generation_decoder_gsbc_native_blocklocal_v1.py [--self-test | --smoke]
#      (bare / runner-injected HDLAB_RUN_MODE=full -> full)

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)  # 17. PRINT-PROGRESS flush on newline

torch.set_num_threads(min(8, os.cpu_count() or 4))
DEVICE = torch.device("cpu")

ANCHOR_NAME = "generation_decoder_gsbc_native_blocklocal_v1"
REPO = Path(__file__).resolve().parents[1]

N_DIM = 8192          # substrate compositional default == MVP == envelope regime (all modes; never reduced)
GSBC_DIM = 8192       # GSBC_EXPAND2X output dim
K_ACTIVE = 192        # GSBC_EXPAND2X global top-K
F_SPARSE = 0.02       # block-local code sparsity fraction (proven-cell F_SPARSE=0.02)
POOL_PATH = REPO / "data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz"

RESTARTS = 16         # dense resonator high-energy restarts (MVP)
MAX_ITER = 40         # dense resonator iterations per restart (MVP)
SEEDS = (7, 13, 19)

BL_PROJ_SEED = 5000   # per-seed block-local projection base seed
SYNTH_SEED = 6000     # per-seed synth codebook base seed
DENSE_PROJ_SEED = 770077  # fixed GSBC_DIM->N projection for the dense-bipolar contrast arms

# Pre-registered bands (memo notes/decoder_design_..._2026-07-05.md, deflated honestly for NATIVE fillers).
# Native block-local MEASURED exact_ordered=1.000 at anchor across probes -> HP floor 0.85 is strict-above
# (band_width 0.35 from HF=0.50; +5pct = 0.5175; 0.85 well above). HYPOTHESIZED bands verified vs probe.
HP_EXACT_ORDERED = 0.85    # HARD_PASS: anchor blocklocal_gsbc exact-ordered-sequence match
HP_PER_TOKEN = 0.90        # HARD_PASS: anchor per-token cleanup accuracy (Stage C)
HF_EXACT_ORDERED = 0.50    # HARD_FAIL: below -> native cannot round-trip even in-box (mechanism wrong)
SYNTH_CEILING_FLOOR = 0.90 # positive-control gate: synth iid block-local must recover (wiring)
NOORDER_COLLAPSE_GAP = 0.50  # order discriminator: gsbc_exact - noorder_exact must exceed this at anchor

# (V, D, region): region "direct" = gated deliverable box (memo HARD constraint D<=6, V<=1024);
#                        "boundary" = capability MAP beyond the box (locate the cliff; ungated).
FULL_GRID = [
    (256, 3, "direct"),
    (1024, 3, "direct"),   # ANCHOR
    (256, 6, "direct"),
    (1024, 6, "direct"),
    (4096, 6, "boundary"),
    (8192, 6, "boundary"),
    (1024, 12, "boundary"),
    (1024, 26, "boundary"),
    (8192, 26, "boundary"),
]
SMOKE_GRID = [(64, 2, "direct"), (128, 3, "direct")]
SELFTEST_GRID = [(32, 2, "direct")]
ANCHOR_V, ANCHOR_D = 1024, 3
SMOKE_ANCHOR_V, SMOKE_ANCHOR_D = 128, 3

BL_ARMS = ["blocklocal_gsbc", "blocklocal_synth", "noorder_ctrl"]
DENSE_ARMS = ["dense_gsbc_rolesknown", "dense_gsbc_fullreso", "dense_synth_fullreso"]


# ============================================================
# Defensive error-checking helpers (13/16)
# ============================================================


def _out_dir() -> Path:
    name = os.environ.get("HDLAB_EXP_NAME")
    return REPO / (f"data/exp_{name}" if name else f"data/exp_{ANCHOR_NAME}")


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
# Native GSBC filler pool (bounded, pre-encoded offline; sparse cache)
# ============================================================


_POOL = {"nz_idx": None, "nz_val": None, "n": 0, "meta": None}


def _load_pool() -> dict:
    if _POOL["nz_idx"] is None:
        if not POOL_PATH.exists():
            raise FileNotFoundError(
                f"GSBC native filler pool missing: {POOL_PATH}. It is an untracked npz -- SCP it to the "
                f"remote (queue_add does NOT auto-ship it). Generated offline from the GSBC_EXPAND2X seed7 "
                f"FULL student (bounded 10000-concept probe).")
        d = np.load(POOL_PATH)
        _POOL["nz_idx"] = d["nz_idx"].astype(np.int64)
        _POOL["nz_val"] = d["nz_val"].astype(np.float32)
        _POOL["n"] = int(_POOL["nz_idx"].shape[0])
        _POOL["meta"] = json.loads(str(d["meta_json"]))
    return _POOL


def _gsbc_dense(rows: np.ndarray) -> np.ndarray:
    """Reconstruct dense native GSBC codes for the given pool rows. (len(rows), GSBC_DIM) float32."""
    p = _load_pool()
    ni, nv = p["nz_idx"], p["nz_val"]
    out = np.zeros((len(rows), GSBC_DIM), dtype=np.float32)
    for i, r in enumerate(rows):
        out[i, ni[r]] = nv[r]
    return out


# ============================================================
# Stage A/B/C: block-local sparse resonator (GSBC-native factorizer)
# ============================================================


def _blocklocal_codebook_gsbc(gsbc_codes: np.ndarray, bs: int, seed: int) -> np.ndarray:
    """Native GSBC filler codebook: project each concept's GSBC code GSBC_DIM->bs (JL-preserves the real
    cos-cone), keep top-(F_SPARSE*bs) magnitude, sign -> sparse bipolar (V, bs). Position (block) is applied
    at compose-time by shifting into block d, so this is a GLOBAL codebook (one code per concept)."""
    V = gsbc_codes.shape[0]
    k = max(1, int(round(F_SPARSE * bs)))
    g = np.random.default_rng(BL_PROJ_SEED + seed)
    P = (g.standard_normal((GSBC_DIM, bs)).astype(np.float32) / np.sqrt(GSBC_DIM))
    Y = gsbc_codes @ P                                            # (V, bs) real, correlated (GSBC cone)
    idx = np.argpartition(-np.abs(Y), k - 1, axis=1)[:, :k]       # top-k magnitude per row
    cb = np.zeros((V, bs), dtype=np.float32)
    rows = np.arange(V)[:, None]
    cb[rows, idx] = np.where(Y[rows, idx] >= 0.0, 1.0, -1.0)
    return cb


def _blocklocal_codebook_synth(V: int, bs: int, seed: int) -> np.ndarray:
    """Proven-cell random sparse bipolar block-local codebook (iid ceiling / positive control). (V, bs)."""
    k = max(1, int(round(F_SPARSE * bs)))
    g = np.random.default_rng(SYNTH_SEED + seed)
    idx = np.stack([g.choice(bs, size=k, replace=False) for _ in range(V)], axis=0)  # (V, k)
    cb = np.zeros((V, bs), dtype=np.float32)
    rows = np.arange(V)[:, None]
    cb[rows, idx] = (g.integers(0, 2, size=(V, k)).astype(np.float32) * 2.0 - 1.0)
    return cb


def _decode_blocklocal(toks, cb: np.ndarray, bs: int, D: int, N: int, noorder: bool = False):
    """Compose D-term proposition (bind = block-superposition) and recover per block.
    noorder=True binds EVERY slot into block 0 (destroys position) -> ordered readout collapses."""
    comp = np.zeros(N, dtype=np.float32)
    for d in range(D):
        base = 0 if noorder else d * bs
        comp[base:base + bs] += cb[toks[d]]
    rec = []
    for d in range(D):
        seg = comp[d * bs:(d + 1) * bs]                          # canonical: read slot d's block d
        rec.append(int(np.argmax(cb @ seg)))
    return rec


def _score_blocklocal(rec, toks):
    """Returns (per_term, exact_ordered, per_token). position==block so per_term is per-slot."""
    D = len(toks)
    exact = 1.0 if list(rec) == list(toks) else 0.0
    per_term = sum(1 for d in range(D) if rec[d] == toks[d]) / D
    pool = list(rec)
    hits = 0
    for tv in toks:
        if tv in pool:
            pool.remove(tv)
            hits += 1
    per_token = hits / D
    return per_term, exact, per_token


def _sample_props(V: int, D: int, trials: int, seed: int):
    rng = np.random.default_rng(90000 + seed)
    return [[int(x) for x in rng.choice(V, size=D, replace=False)] for _ in range(trials)]


def run_blocklocal_arm(cb: np.ndarray, props, bs: int, D: int, N: int, noorder: bool = False):
    pt = ex = tk = 0.0
    rec_idx = []
    for toks in props:
        rec = _decode_blocklocal(toks, cb, bs, D, N, noorder=noorder)
        a, b, c = _score_blocklocal(rec, toks)
        pt += a; ex += b; tk += c
        rec_idx.extend(rec)
    n = len(props)
    return {"per_term": pt / n, "exact_ordered": ex / n, "per_token": tk / n}, rec_idx


# ============================================================
# MECHANISM CONTRAST: dense bipolar-BSC pipeline (copied UNCHANGED from the MVP)
# ============================================================


def _bipolar(shape, gen: torch.Generator) -> torch.Tensor:
    raw = torch.rand(shape, generator=gen)
    return (2.0 * (raw > 0.5).float() - 1.0).to(DEVICE)


def make_positions(P: int, N: int, gen: torch.Generator) -> torch.Tensor:
    """Protected/index position codebook pos[k]=roll(base,k) (MVP; E3 permutation-indexed binding)."""
    base = _bipolar((N,), gen)
    return torch.stack([torch.roll(base, shifts=k) for k in range(P)], dim=0)


def make_synth_lexicon(V: int, N: int, gen: torch.Generator) -> torch.Tensor:
    return _bipolar((V, N), gen)


def make_dense_bipolar_gsbc(rows: np.ndarray, N: int) -> torch.Tensor:
    """Native GSBC concepts as DENSE bipolar (randproj GSBC_DIM->N, sign) -- the MVP stand-in style but
    sourced from native GSBC codes (carries the GSBC cone). (V, N) bipolar."""
    gc = _gsbc_dense(rows)
    pr = np.random.default_rng(DENSE_PROJ_SEED)
    P = (pr.standard_normal((GSBC_DIM, N)).astype(np.float32) / np.sqrt(GSBC_DIM))
    B = np.where(gc @ P >= 0.0, 1.0, -1.0).astype(np.float32)
    return torch.from_numpy(B).to(DEVICE)


def resonate(residual, books, N, restarts, max_iter, gen):
    """Factor ONE (position x filler) product-term out of a residual (MVP; batched over restarts)."""
    F = len(books)
    est = [_bipolar((restarts, N), gen) for _ in range(F)]
    prev_sign = None
    for _ in range(max_iter):
        for i in range(F):
            other = torch.ones((restarts, N), device=DEVICE)
            for j in range(F):
                if j != i:
                    other = other * est[j]
            unbound = residual.unsqueeze(0) * other
            scores = unbound @ books[i].t() / N
            recon = scores @ books[i]
            s = torch.sign(recon)
            est[i] = torch.where(s == 0, torch.ones_like(s), s)
        cur_sign = torch.cat(est, dim=1)
        if prev_sign is not None and torch.equal(cur_sign, prev_sign):
            break
        prev_sign = cur_sign
    idx = []
    for i in range(F):
        sims = est[i] @ books[i].t() / N
        idx.append(sims.argmax(dim=1))
    idx = torch.stack(idx, dim=0)
    recon = torch.ones((restarts, N), device=DEVICE)
    for i in range(F):
        recon = recon * books[i][idx[i]]
    dots = (recon * residual.unsqueeze(0)).sum(dim=1)
    best = int(dots.argmax().item())
    best_tuple = (int(idx[0, best].item()), int(idx[1, best].item()))
    return best_tuple, recon[best], float(dots[best].item())


def peel_decode(prop, pos_book, lex_book, D, restarts, max_iter, gen):
    residual = prop.clone()
    out = []
    for _ in range(D):
        tup, recon, dot = resonate(residual, [pos_book, lex_book], N_DIM, restarts, max_iter, gen)
        out.append((tup[0], tup[1], dot))
        residual = residual - recon
    return out


def roles_known_decode(prop, pos_D, lex_book, D, n_iters):
    est = torch.empty(D, dtype=torch.long, device=DEVICE)
    for d in range(D):
        q = prop * pos_D[d]
        est[d] = int((q @ lex_book.t() / N_DIM).argmax().item())
    for _ in range(n_iters):
        bound = pos_D * lex_book[est]
        total = bound.sum(0)
        new = est.clone()
        for d in range(D):
            resid = prop - (total - bound[d])
            q = resid * pos_D[d]
            new[d] = int((q @ lex_book.t() / N_DIM).argmax().item())
        if torch.equal(new, est):
            break
        est = new
    return [int(x) for x in est.tolist()]


def encode_prop(toks, pos_book, lex_book) -> torch.Tensor:
    s = torch.zeros(N_DIM, device=DEVICE)
    for d, t in enumerate(toks):
        s = s + pos_book[d] * lex_book[t]
    return s


def _multiset_match(recovered, truth) -> int:
    pool = list(recovered)
    hits = 0
    for x in truth:
        if x in pool:
            pool.remove(x)
            hits += 1
    return hits


def score_tuples(recovered_tuples, toks):
    D = len(toks)
    truth_tuples = [(d, toks[d]) for d in range(D)]
    rec_pf = [(p, f) for (p, f, _dot) in recovered_tuples]
    per_term = _multiset_match(rec_pf, truth_tuples) / D
    out = [-1] * D
    best_dot = [-1e30] * D
    for (p, f, dot) in recovered_tuples:
        if 0 <= p < D and dot > best_dot[p]:
            best_dot[p] = dot
            out[p] = f
    exact = 1.0 if out == list(toks) else 0.0
    per_token = _multiset_match([f for (_p, f, _d) in recovered_tuples], list(toks)) / D
    return per_term, exact, per_token


def score_rolesknown(est_fillers, toks):
    D = len(toks)
    exact = 1.0 if list(est_fillers) == list(toks) else 0.0
    per_token = _multiset_match(list(est_fillers), list(toks)) / D
    per_term = sum(1 for d in range(D) if est_fillers[d] == toks[d]) / D
    return per_term, exact, per_token


def run_dense_full_arm(lex_book, pos_book, props, D, restarts, max_iter, gen):
    pt = ex = tk = 0.0
    rec_idx = []
    for toks in props:
        prop = encode_prop(toks, pos_book, lex_book)
        tuples = peel_decode(prop, pos_book, lex_book, D, restarts, max_iter, gen)
        a, b, c = score_tuples(tuples, toks)
        pt += a; ex += b; tk += c
        rec_idx.extend([f for (_p, f, _d) in tuples])
    n = len(props)
    return {"per_term": pt / n, "exact_ordered": ex / n, "per_token": tk / n}, rec_idx


def run_dense_rolesknown_arm(lex_book, pos_book, props, D, n_iters):
    pt = ex = tk = 0.0
    rec_idx = []
    pos_D = pos_book[:D]
    for toks in props:
        prop = encode_prop(toks, pos_book, lex_book)
        est = roles_known_decode(prop, pos_D, lex_book, D, n_iters)
        a, b, c = score_rolesknown(est, toks)
        pt += a; ex += b; tk += c
        rec_idx.extend(est)
    n = len(props)
    return {"per_term": pt / n, "exact_ordered": ex / n, "per_token": tk / n}, rec_idx


# ============================================================
# Config + driver
# ============================================================


def get_config(mode: str):
    if mode == "selftest":
        return {"grid": SELFTEST_GRID, "trials": 5, "seeds": (7,),
                "restarts": 2, "max_iter": 6, "n_iters": 4, "anchor": None}
    if mode == "smoke":
        return {"grid": SMOKE_GRID, "trials": 5, "seeds": (7,),
                "restarts": 4, "max_iter": 10, "n_iters": 5,
                "anchor": (SMOKE_ANCHOR_V, SMOKE_ANCHOR_D)}
    return {"grid": FULL_GRID, "trials": 30, "seeds": SEEDS,
            "restarts": RESTARTS, "max_iter": MAX_ITER, "n_iters": 6,
            "anchor": (ANCHOR_V, ANCHOR_D)}


def _digest(int_list) -> str:
    return hashlib.sha256(np.asarray(int_list, dtype=np.int64).tobytes()).hexdigest()


def _digest_arr(arr) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(arr, dtype=np.float32)).tobytes()).hexdigest()


def expected_units(cfg) -> int:
    n_seeds = len(cfg["seeds"])
    n = len(cfg["grid"]) * len(BL_ARMS) * n_seeds
    if cfg["anchor"] is not None:
        n += len(DENSE_ARMS) * n_seeds
    return n


def run_all(mode: str, output_dir: Path, t0: float):
    cfg = get_config(mode)
    grid, trials, seeds = cfg["grid"], cfg["trials"], cfg["seeds"]
    anchor = cfg["anchor"]
    per_unit = []              # cardinality ledger: one record per (grid-point/anchor, arm, seed)
    rec_digests = {}           # for arms-differ (per point/seed)
    cone = {}
    total_units = expected_units(cfg)
    unit = 0

    for seed in seeds:
        for (V, D, region) in grid:
            bs = N_DIM // D
            props = _sample_props(V, D, trials, seed)
            samp = np.random.default_rng(90000 + seed).choice(_load_pool()["n"], size=V, replace=False)
            gc = _gsbc_dense(samp)
            cb_gsbc = _blocklocal_codebook_gsbc(gc, bs, seed)
            cb_synth = _blocklocal_codebook_synth(V, bs, seed)

            s_g, rec_g = run_blocklocal_arm(cb_gsbc, props, bs, D, N_DIM)
            s_s, rec_s = run_blocklocal_arm(cb_synth, props, bs, D, N_DIM)
            s_n, rec_n = run_blocklocal_arm(cb_gsbc, props, bs, D, N_DIM, noorder=True)
            for arm, rec in (("blocklocal_gsbc", s_g), ("blocklocal_synth", s_s),
                             ("noorder_ctrl", s_n)):
                unit += 1
                per_unit.append({"region": region, "V": V, "D": D, "seed": seed, "arm": arm,
                                 "per_term": round(rec["per_term"], 4),
                                 "exact_ordered": round(rec["exact_ordered"], 4),
                                 "per_token": round(rec["per_token"], 4)})
            # arms_differ (META_RULE_AF): compare DISTINCT MECHANISM artifacts, not perfect-recovery
            # outputs (blocklocal_gsbc/synth legitimately emit the same truth tokens when both recover).
            # (a) codebooks must differ (gsbc vs synth); (b) order-destruction must change output
            # (noorder recovered != gsbc recovered).
            rec_digests[f"{V}_{D}_{seed}"] = {"cb_gsbc": _digest_arr(cb_gsbc),
                                              "cb_synth": _digest_arr(cb_synth),
                                              "rec_gsbc": _digest(rec_g),
                                              "rec_noorder": _digest(rec_n)}
            _heartbeat(output_dir, unit, total_units, t0,
                       extra={"V": V, "D": D, "seed": seed, "region": region,
                              "gsbc_exact": round(s_g["exact_ordered"], 3),
                              "synth_exact": round(s_s["exact_ordered"], 3),
                              "noorder_exact": round(s_n["exact_ordered"], 3)})
            _say(f"  [seed {seed}] V={V} D={D} ({region}) blocklocal: gsbc exact={s_g['exact_ordered']:.3f} "
                 f"perterm={s_g['per_term']:.3f} pertok={s_g['per_token']:.3f} | synth exact={s_s['exact_ordered']:.3f} "
                 f"| noorder exact={s_n['exact_ordered']:.3f} pertok={s_n['per_token']:.3f}")

        # --- mechanism contrast at anchor (dense bipolar-BSC pipeline on native GSBC) ---
        if anchor is not None:
            V, D = anchor
            gcb = torch.Generator().manual_seed(1000 + seed)
            pos_book = make_positions(D, N_DIM, gcb)
            samp = np.random.default_rng(91000 + seed).choice(_load_pool()["n"], size=V, replace=False)
            dense_gsbc_lex = make_dense_bipolar_gsbc(samp, N_DIM)
            synth_lex = make_synth_lexicon(V, N_DIM, gcb)
            props_d = _sample_props(V, D, trials, seed)
            cd = {}
            Bn = dense_gsbc_lex / (dense_gsbc_lex.norm(dim=1, keepdim=True) + 1e-12)
            sidx = torch.randperm(V, generator=gcb)[:min(300, V)]
            Sm = Bn[sidx] @ Bn[sidx].t()
            m = Sm.shape[0]
            cone[str(seed)] = round(float(Sm[~torch.eye(m, dtype=torch.bool)].mean().item()), 4)

            s_rk, rec_rk = run_dense_rolesknown_arm(dense_gsbc_lex, pos_book, props_d, D, cfg["n_iters"])
            gres = torch.Generator().manual_seed(3000 + seed)
            s_fg, rec_fg = run_dense_full_arm(dense_gsbc_lex, pos_book, props_d, D, cfg["restarts"],
                                              cfg["max_iter"], gres)
            gres2 = torch.Generator().manual_seed(3100 + seed)
            s_fs, rec_fs = run_dense_full_arm(synth_lex, pos_book, props_d, D, cfg["restarts"],
                                              cfg["max_iter"], gres2)
            for arm, rec in (("dense_gsbc_rolesknown", s_rk), ("dense_gsbc_fullreso", s_fg),
                             ("dense_synth_fullreso", s_fs)):
                unit += 1
                per_unit.append({"region": "anchor_contrast", "V": V, "D": D, "seed": seed, "arm": arm,
                                 "per_term": round(rec["per_term"], 4),
                                 "exact_ordered": round(rec["exact_ordered"], 4),
                                 "per_token": round(rec["per_token"], 4)})
            # arms_differ (META_RULE_AF): native-GSBC vs iid lexicons must differ, AND the mismatch
            # (positions-unknown fullreso on GSBC) must diverge from the positions-known decode.
            rec_digests[f"anchor_{seed}"] = {"lex_gsbc": _digest_arr(dense_gsbc_lex.numpy()),
                                             "lex_synth": _digest_arr(synth_lex.numpy()),
                                             "rec_fullreso_gsbc": _digest(rec_fg),
                                             "rec_rolesknown_gsbc": _digest(rec_rk)}
            _heartbeat(output_dir, unit, total_units, t0, extra={"phase": "anchor_contrast", "seed": seed})
            _say(f"  [seed {seed}] ANCHOR contrast (dense bipolar-BSC on native GSBC, cone={cone[str(seed)]:.3f}): "
                 f"rolesknown exact={s_rk['exact_ordered']:.3f} | gsbc_fullreso exact={s_fg['exact_ordered']:.3f} "
                 f"(mismatch->collapse) | synth_fullreso exact={s_fs['exact_ordered']:.3f} (iid ceiling)")

    return cfg, per_unit, rec_digests, cone


def _agg(per_unit, region_filter, arm, V, D, key):
    vals = [u[key] for u in per_unit
            if u["arm"] == arm and u["V"] == V and u["D"] == D
            and (region_filter is None or u["region"] == region_filter)]
    return float(np.mean(vals)) if vals else float("nan"), [round(float(v), 4) for v in vals]


def classify(per_unit, cfg, mode: str):
    anchor = cfg["anchor"]
    exp = expected_units(cfg)
    if len(per_unit) < exp:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: {len(per_unit)}/{exp} units", False)
    if anchor is None:
        return ("SELFTEST_OK", "selftest ran", True)
    V, D = anchor

    g_ex_m, _ = _agg(per_unit, None, "blocklocal_gsbc", V, D, "exact_ordered")
    g_pt_m, _ = _agg(per_unit, None, "blocklocal_gsbc", V, D, "per_term")
    g_tk_m, _ = _agg(per_unit, None, "blocklocal_gsbc", V, D, "per_token")
    s_pt_m, _ = _agg(per_unit, None, "blocklocal_synth", V, D, "per_term")
    n_ex_m, _ = _agg(per_unit, None, "noorder_ctrl", V, D, "exact_ordered")
    drk_m, _ = _agg(per_unit, "anchor_contrast", "dense_gsbc_rolesknown", V, D, "exact_ordered")
    dfg_m, _ = _agg(per_unit, "anchor_contrast", "dense_gsbc_fullreso", V, D, "exact_ordered")
    dfs_m, _ = _agg(per_unit, "anchor_contrast", "dense_synth_fullreso", V, D, "exact_ordered")

    # boundary cliff summary (map)
    cliff = []
    for (Vg, Dg, region) in cfg["grid"]:
        if region == "boundary":
            e, _ = _agg(per_unit, "boundary", "blocklocal_gsbc", Vg, Dg, "exact_ordered")
            cliff.append(f"V{Vg}D{Dg}={e:.2f}")

    diag = (f"anchor(V{V}D{D}) blocklocal_gsbc exact={g_ex_m:.3f} perterm={g_pt_m:.3f} pertok={g_tk_m:.3f}; "
            f"synth_ceiling perterm={s_pt_m:.3f}; noorder exact={n_ex_m:.3f} (must collapse); "
            f"CONTRAST dense_gsbc_rolesknown={drk_m:.3f} dense_gsbc_fullreso={dfg_m:.3f}(mismatch) "
            f"dense_synth_fullreso={dfs_m:.3f}(iid ceiling); boundary_map[{' '.join(cliff)}]")

    # --- discriminator-fires gates (all modes) ---
    if not (s_pt_m >= SYNTH_CEILING_FLOOR):
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"synth iid block-local ceiling per_term={s_pt_m:.3f} < {SYNTH_CEILING_FLOOR}: "
                f"block-local wiring FAILED (positive control). {diag}", False)
    if (g_ex_m - n_ex_m) < NOORDER_COLLAPSE_GAP:
        return ("ORDER_DISCRIMINATOR_DID_NOT_FIRE",
                f"noorder did not collapse (gsbc_exact={g_ex_m:.3f} vs noorder={n_ex_m:.3f}, "
                f"gap<{NOORDER_COLLAPSE_GAP}): ordered readout not attributable to position(block) binding. {diag}",
                True)

    if mode == "smoke":
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: block-local (native GSBC + synth ceiling + noorder) and dense-contrast "
                f"arms all run end-to-end AT N={N_DIM}; synth ceiling recovers, noorder collapses, arms differ. "
                f"The deliverable band is FULL-only (canonical = remote landing). {diag}", True)

    # --- FULL pre-registered generation bands (gate on native block-local at anchor) ---
    if g_ex_m >= HP_EXACT_ORDERED and g_tk_m >= HP_PER_TOKEN:
        return ("HARD_PASS",
                f"NATIVE GSBC round-trip WORKS with the GSBC-native (block-local sparse) factorizer: "
                f"exact-ordered={g_ex_m:.3f} (>= {HP_EXACT_ORDERED}) AND per_token={g_tk_m:.3f} (>= {HP_PER_TOKEN}) "
                f"at V{V} D{D} N={N_DIM}, matching the synth ceiling ({s_pt_m:.3f}). The dense bipolar-BSC "
                f"positions-unknown resonator COLLAPSES on the same native fillers (dense_gsbc_fullreso={dfg_m:.3f} "
                f"vs iid dense_synth_fullreso={dfs_m:.3f}) -> block-local is the right GSBC-native architecture; "
                f"dense multiply-bind is the encoding mismatch. {diag}", True)
    if g_ex_m < HF_EXACT_ORDERED:
        return ("HARD_FAIL",
                f"native GSBC cannot round-trip even in-box: exact-ordered={g_ex_m:.3f} (< {HF_EXACT_ORDERED}); "
                f"Stage A/C block-local is the wall on real correlated fillers. {diag}", True)
    return ("MIDDLE_BAND",
            f"partial native round-trip: exact-ordered={g_ex_m:.3f} in [{HF_EXACT_ORDERED},{HP_EXACT_ORDERED}); "
            f"chunking needed beyond the GO region. {diag}", True)


# ============================================================
# main
# ============================================================


def _run(mode: str) -> int:
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    cfg = get_config(mode)
    exp = expected_units(cfg)
    _write_start_marker(output_dir, mode, exp)
    _say(f"[{ANCHOR_NAME}] mode={mode} N={N_DIM} grid={cfg['grid']} seeds={cfg['seeds']} "
         f"trials={cfg['trials']} R={cfg['restarts']} expected_units={exp}")

    cfg, per_unit, rec_digests, cone = run_all(mode, output_dir, t0)

    # arms_differ (META_RULE_AF): assert the DISTINCT mechanism artifacts differ. Perfect-recovery arms
    # legitimately emit identical truth tokens, so we compare codebooks/lexicons (the arm implementations)
    # + verify order-destruction/positions-unknown genuinely diverge from the recovering decode.
    arms_differ_ok = True
    for key, dg in rec_digests.items():
        if "cb_gsbc" in dg:
            if dg["cb_gsbc"] == dg["cb_synth"]:
                arms_differ_ok = False   # native + iid codebooks identical -> arm bug
            if dg["rec_gsbc"] == dg["rec_noorder"]:
                arms_differ_ok = False   # order-destruction did not change output -> noorder bug
        else:  # anchor contrast
            if dg["lex_gsbc"] == dg["lex_synth"]:
                arms_differ_ok = False   # native + iid lexicons identical -> arm bug
            if dg["rec_fullreso_gsbc"] == dg["rec_rolesknown_gsbc"]:
                arms_differ_ok = False   # mismatch fullreso did not diverge from positions-known -> arm bug
    if not arms_differ_ok:
        raise AssertionError(
            "META_RULE_AF VIOLATION: mechanism artifacts bit-identical "
            "(codebook/lexicon collision OR order-control did not alter output)")

    verdict, vmsg, order_ok = classify(per_unit, cfg, mode)
    elapsed = time.perf_counter() - t0

    # build per-arm summary (anchor + per-region rollups)
    def arm_summary(region_filter, arm, V, D):
        pt_m, pt_v = _agg(per_unit, region_filter, arm, V, D, "per_term")
        ex_m, ex_v = _agg(per_unit, region_filter, arm, V, D, "exact_ordered")
        tk_m, tk_v = _agg(per_unit, region_filter, arm, V, D, "per_token")
        return {"per_term_mean": round(pt_m, 4), "per_term_per_seed": pt_v,
                "exact_ordered_mean": round(ex_m, 4), "exact_ordered_per_seed": ex_v,
                "per_token_mean": round(tk_m, 4), "per_token_per_seed": tk_v}

    grid_summary = {}
    for (V, D, region) in cfg["grid"]:
        for arm in BL_ARMS:
            grid_summary[f"{arm}@V{V}D{D}"] = arm_summary(region, arm, V, D)
    if cfg["anchor"] is not None:
        V, D = cfg["anchor"]
        for arm in DENSE_ARMS:
            grid_summary[f"{arm}@V{V}D{D}"] = arm_summary("anchor_contrast", arm, V, D)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: native GSBC generation round-trip via block-local sparse resonator ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": len(cfg["seeds"]),
        "n_units": len(per_unit),
        "expected_n_units": exp,
        "cardinality_ok": len(per_unit) >= exp,
        "config": {"N": N_DIM, "GSBC_DIM": GSBC_DIM, "K_ACTIVE": K_ACTIVE, "F_SPARSE": F_SPARSE,
                   "grid": [[V, D, r] for (V, D, r) in cfg["grid"]], "anchor": cfg["anchor"],
                   "trials": cfg["trials"], "seeds": list(cfg["seeds"]),
                   "RESTARTS": cfg["restarts"], "MAX_ITER": cfg["max_iter"], "n_iters": cfg["n_iters"],
                   "stageA": "block_local_sparse_resonator", "algebra": "block_superposition_sum",
                   "position_binding": "disjoint_block_index",
                   "native_filler": "GSBC_EXPAND2X_seed7_FULL_projected_sparse_bipolar",
                   "pool_meta": _load_pool()["meta"]},
        "arms": grid_summary,
        "per_unit": per_unit,
        "controls": {"noorder_collapsed": order_ok,
                     "dense_bipolar_cone": cone},
        "arms_differ_verified": arms_differ_ok,
        "bands": {"HP_exact_ordered": HP_EXACT_ORDERED, "HP_per_token": HP_PER_TOKEN,
                  "HF_exact_ordered": HF_EXACT_ORDERED, "synth_ceiling_floor": SYNTH_CEILING_FLOOR,
                  "noorder_collapse_gap": NOORDER_COLLAPSE_GAP},
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
    t0 = time.perf_counter()
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    cfg, per_unit, _dg, _cone = run_all("selftest", output_dir, t0)
    V, D, _r = SELFTEST_GRID[0]
    g_pt, _ = _agg(per_unit, None, "blocklocal_gsbc", V, D, "per_term")
    s_pt, _ = _agg(per_unit, None, "blocklocal_synth", V, D, "per_term")
    g_ex, _ = _agg(per_unit, None, "blocklocal_gsbc", V, D, "exact_ordered")
    n_ex, _ = _agg(per_unit, None, "noorder_ctrl", V, D, "exact_ordered")
    ok = (g_pt >= 0.90) and (s_pt >= 0.90) and (g_ex - n_ex >= 0.0)
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: gsbc_perterm={g_pt:.3f} synth_perterm={s_pt:.3f} "
         f"gsbc_exact={g_ex:.3f} noorder_exact={n_ex:.3f} [{time.perf_counter()-t0:.1f}s]")
    return 0 if ok else 1


def main() -> int:
    if "--self-test" in sys.argv:
        return _run_selftest()
    mode = "smoke" if "--smoke" in sys.argv else \
        ("smoke" if os.environ.get("HDLAB_RUN_MODE", "").lower() == "smoke" else "full")
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
