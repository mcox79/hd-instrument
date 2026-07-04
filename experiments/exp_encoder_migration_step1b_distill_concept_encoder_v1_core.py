"""Encoder Migration Step 1b - Dense-teacher (BGE) distillation into sparse
BLOCK-bipolar concept codes, dual-gated (semantic + algebra).

Redesign of Step 1 per the design-correctness drill (2026-07-04): the Step-1
orthographic objective has no semantic signal source capable of the 0.85
target. Step 1b distills cached BGE-large teacher geometry into a sparse
block code (K blocks, 1 signed active/block) via relational KD + InfoNCE with
semi-hard teacher-mined negatives, and gates EVERY result on BOTH semantic
fidelity (vs BGE-gold on held-out concepts) AND algebraic fidelity (SBC
block-local circular convolution keyed roundtrip + bundle-superposition) --
the false-win guard.

Composition algebra decision (prereg field): SBC_block_local_circular_
convolution. A k-sparse real code is NOT a valid literal-FHRR atom; the
naive top-k + FHRR path is retained ONLY as the false-win comparison arm
(probe MEASURED: 0.483 keyed roundtrip at J=20 vs BLOCK 1.000).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (sha256 over semantic-arm code matrices)
- final_metrics_atomicity: tmp_replace (write_metrics helper)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_floor_computed: r_max=0.901 at K=128 (formula in prereg;
  THEORETICAL@r_max = sigma_t/sqrt(sigma_t^2+0.25/K), sigma_t=0.0918 MEASURED)
- baseline_in_band: CHARPOS ret_agree@10 = 0.0655 MEASURED@probe in (0.05,0.95)
- discriminator survives scale: smoke at FULL N_DIM=4096 + K_BLOCKS=128;
  scale axes V + steps are monotone-helpful for G_A; G_B1 V-insensitive (SBC
  lossless); G_B2 bands set BELOW probe values for V growth
- HARD_PASS strictly above floor per prereg bands (META_RULE_L)
- HP_SCOPE per-arm declared in prereg (gates on BLOCK_K128 only)
- cardinality_ok: EXPECTED_N_UNITS smoke=22 full=47, counted from per_unit
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime (prereg evidence)
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

Prereg: preregs/2026-07-04_exp_encoder_migration_step1b_distill_concept_encoder_v1.md
Probe evidence: notes/cell_design_step1b_distill_feasibility_probe_2026-07-04.md

Source signature: teacher = BGE-large warm cache (prebuild_bge_index_cache_
gpu_v1); algebra = hdlab.binding bind/unbind (SBC block-local on [K,L]) +
hdlab.atoms make_atoms (FHRR keys for comparison arms); baseline encoder =
hdlab.char_positional_encoder (Step-1-style).

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
from hdlab.atoms import make_atoms  # noqa: E402
from hdlab.binding import bind, unbind  # noqa: E402
from hdlab.char_positional_encoder import CharPositionalEncoder  # noqa: E402

# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_migration_step1b_distill_concept_encoder_v1"

_CACHE_DIR = _REPO / "data" / "substrate_index" / "cached_indices"
TEACHER_GLOB = "bge_large_v2_name_*.npz"

N_DIM_DEFAULT = 4096
K_BLOCKS_PRIMARY = 128          # L=32; sparsity 3.125% (prereg rationale)
K_BLOCKS_FULL_SWEEP = [128, 64]  # primary first; K64 report-only arm
SEED_DEFAULT = 7
TAU_NCE = 0.07
LAM_NCE = 0.5
TAU_GUMBEL = 1.0
LR = 1e-3
SEMI_LO, SEMI_HI = 0.30, 0.60   # semi-hard teacher-cos band (drill Q4)
N_SEMI_CANDS = 64
N_NEG_PER_ANCHOR = 4
HELD_FRAC = 0.10

# Run-mode grids.
SMOKE_N_TRAIN, SMOKE_N_HELD = 3000, 800
SMOKE_STEPS, SMOKE_BATCH = 150, 192
SMOKE_J_GRID = [5, 20]
SMOKE_TRIALS = 50
SMOKE_CHARPOS_CAP = 2000
SMOKE_PAIR_SAMPLE = 250_000

FULL_STEPS, FULL_BATCH = 20_000, 1024
FULL_J_GRID = [2, 5, 10, 20]
FULL_TRIALS = 200
FULL_CHARPOS_CAP = 5000
FULL_PAIR_SAMPLE = 500_000
FULL_HELD_CAP = 20_000

CKPT_EVERY_STEPS_FULL = 500
CKPT_EVERY_STEPS_SMOKE = 50
MINE_CHUNK = 2048
CLEANUP_CHUNK = 16384

EXPECTED_N_UNITS_SMOKE = 22
EXPECTED_N_UNITS_FULL = 47

PREREG_BASELINE_ARMS = ["CHARPOS"]


def _artifact_dir(run_mode: str) -> Path:
    suffix = "_smoke" if run_mode == "smoke" else ""
    return _REPO / "data" / f"substrate_concept_encoder_v1b{suffix}"


# ---------------------------------------------------------------------------
# Defensive helpers (start marker / crash metrics / heartbeat).
# ---------------------------------------------------------------------------

def _write_start_marker(output_dir: Path, run_mode: str,
                        expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": int(expected_n_units),
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, output_dir / "_start_marker.json")


def _write_crash_metrics(output_dir: Path, exc: BaseException) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(tmp, output_dir / "metrics.json")


def _emit_heartbeat(output_dir: Path, unit_idx: int, total_units: int,
                    elapsed_s: float, extra: Optional[dict] = None) -> None:
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": int(unit_idx),
        "total_units": int(total_units),
        "elapsed_s": float(elapsed_s),
    }
    if extra:
        row["extra"] = extra
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# ---------------------------------------------------------------------------
# Teacher cache.
# ---------------------------------------------------------------------------

def _resolve_teacher_cache(explicit: Optional[str]) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.is_absolute():
            p = _REPO / p
        if not p.exists():
            raise FileNotFoundError(f"teacher cache not found: {p}")
        return p
    cands = sorted(_CACHE_DIR.glob(TEACHER_GLOB),
                   key=lambda p: p.stat().st_size, reverse=True)
    if not cands:
        raise FileNotFoundError(
            f"no teacher cache matching {TEACHER_GLOB} under {_CACHE_DIR}")
    return cands[0]


def _load_teacher(cache_path: Path) -> Tuple[torch.Tensor, List[str]]:
    d = np.load(str(cache_path), allow_pickle=False)
    if "semantic" not in d or "id_order_json" not in d:
        raise ValueError(f"teacher cache {cache_path.name} missing "
                         f"semantic/id_order_json keys: {list(d.keys())}")
    sem = d["semantic"]
    ids = json.loads(str(d["id_order_json"]))
    if sem.shape[0] != len(ids):
        raise ValueError(f"teacher cache row/id mismatch: {sem.shape[0]} "
                         f"vs {len(ids)}")
    if np.isnan(sem).any() or np.isinf(sem).any():
        raise ValueError("teacher cache contains NaN/Inf")
    return torch.from_numpy(np.ascontiguousarray(sem)), ids


# ---------------------------------------------------------------------------
# Mining (chunked + shard-checkpointed): top-1 positives + semi-hard cands.
# ---------------------------------------------------------------------------

def _mine_teacher(Xtr: torch.Tensor, device: str, shard_dir: Path,
                  output_dir: Path, t0: float) -> Tuple[torch.Tensor, torch.Tensor]:
    """Return (pos_idx [V], semi_cands [V, N_SEMI_CANDS] with -1 padding)."""
    V = Xtr.shape[0]
    n_chunks = (V + MINE_CHUNK - 1) // MINE_CHUNK
    shard_dir.mkdir(parents=True, exist_ok=True)
    Xd = Xtr.to(device)
    pos_all = torch.full((V,), -1, dtype=torch.long)
    semi_all = torch.full((V, N_SEMI_CANDS), -1, dtype=torch.long)
    for c in range(n_chunks):
        sp = shard_dir / f"mine_{c:05d}.npz"
        lo, hi = c * MINE_CHUNK, min((c + 1) * MINE_CHUNK, V)
        if sp.exists():
            d = np.load(str(sp), allow_pickle=False)
            pos_all[lo:hi] = torch.from_numpy(d["pos"].astype(np.int64))
            semi_all[lo:hi] = torch.from_numpy(d["semi"].astype(np.int64))
            continue
        sims = Xd[lo:hi] @ Xd.T  # [C, V]
        rows = torch.arange(hi - lo, device=device)
        sims[rows, torch.arange(lo, hi, device=device)] = -2.0
        pos = sims.argmax(dim=1)
        band = ((sims >= SEMI_LO) & (sims <= SEMI_HI)).float()
        n_band = band.sum(dim=1)
        semi = torch.full((hi - lo, N_SEMI_CANDS), -1,
                          dtype=torch.long, device=device)
        ok = n_band > 0
        if ok.any():
            picks = torch.multinomial(
                band[ok] + 1e-12, N_SEMI_CANDS, replacement=True)
            semi[ok] = picks
        pos_c = pos.cpu()
        semi_c = semi.cpu()
        pos_all[lo:hi] = pos_c
        semi_all[lo:hi] = semi_c
        tmp = shard_dir / f"mine_{c:05d}.tmp.npz"
        np.savez_compressed(tmp, pos=pos_c.numpy().astype(np.int32),
                            semi=semi_c.numpy().astype(np.int32))
        os.replace(tmp, sp)
        if c % 8 == 0:
            _emit_heartbeat(output_dir, c + 1, n_chunks,
                            time.perf_counter() - t0,
                            extra={"phase": "mine"})
            print(f"[step1b] mine chunk {c + 1}/{n_chunks} "
                  f"({time.perf_counter() - t0:.1f}s)", flush=True)
    if (pos_all < 0).any():
        raise RuntimeError("mining left unfilled positive rows")
    return pos_all, semi_all


# ---------------------------------------------------------------------------
# Students + sparsifiers.
# ---------------------------------------------------------------------------

def _block_ste(z: torch.Tensor, kb: int, blk_l: int) -> torch.Tensor:
    """Per-block argmax straight-through: hard one-hot*sign fwd, soft bwd."""
    B = z.shape[0]
    zb = z.reshape(B, kb, blk_l)
    p = torch.softmax(zb.abs() / TAU_GUMBEL, dim=-1)
    hard = torch.zeros_like(p)
    hard.scatter_(-1, p.argmax(dim=-1, keepdim=True), 1.0)
    h_st = hard + p - p.detach()
    sgn = torch.sign(zb)
    sgn = torch.where(sgn == 0, torch.ones_like(sgn), sgn)
    sgn_st = sgn + torch.tanh(zb) - torch.tanh(zb).detach()
    return (h_st * sgn_st).reshape(B, kb * blk_l)


def _topk_ste(z: torch.Tensor, k: int) -> torch.Tensor:
    """Unstructured top-k magnitude + sign, identity STE (naive comparison)."""
    mag = z.abs()
    thr = mag.topk(k, dim=-1).values[..., -1:]
    mask = (mag >= thr).float()
    sgn = torch.sign(z)
    sgn = torch.where(sgn == 0, torch.ones_like(sgn), sgn)
    return z + (sgn * mask - z).detach()


@torch.no_grad()
def _encode_hard_block(W: torch.nn.Linear, X: torch.Tensor, kb: int,
                       blk_l: int, batch: int = 8192) -> torch.Tensor:
    out = torch.zeros(X.shape[0], kb * blk_l, dtype=torch.float32)
    for lo in range(0, X.shape[0], batch):
        z = W(X[lo:lo + batch].to(W.weight.device)).reshape(-1, kb, blk_l)
        o = torch.zeros_like(z)
        idx = z.abs().argmax(dim=-1, keepdim=True)
        sgn = torch.sign(torch.gather(z, -1, idx))
        sgn[sgn == 0] = 1.0
        o.scatter_(-1, idx, sgn)
        out[lo:lo + batch] = o.reshape(-1, kb * blk_l).cpu()
    return out


@torch.no_grad()
def _encode_hard_topk(W: torch.nn.Linear, X: torch.Tensor, k: int,
                      batch: int = 8192) -> torch.Tensor:
    n_dim = W.weight.shape[0]
    out = torch.zeros(X.shape[0], n_dim, dtype=torch.float32)
    for lo in range(0, X.shape[0], batch):
        z = W(X[lo:lo + batch].to(W.weight.device))
        o = torch.zeros_like(z)
        topk = z.abs().topk(k, dim=-1).indices
        rows = torch.arange(z.shape[0], device=z.device).unsqueeze(1)
        sgn = torch.sign(z[rows, topk])
        sgn[sgn == 0] = 1.0
        o[rows, topk] = sgn
        out[lo:lo + batch] = o.cpu()
    return out


def _train_student(
    kind: str,                    # "block" | "topk"
    kb: int, blk_l: int, k_topk: int,
    Xtr: torch.Tensor, pos_idx: torch.Tensor, semi_cands: torch.Tensor,
    steps: int, batch: int, seed: int, device: str,
    ckpt_path: Path, ckpt_every: int, output_dir: Path, t0: float,
) -> Tuple[torch.nn.Linear, Dict[str, float]]:
    n_dim = kb * blk_l if kind == "block" else k_topk * 0 + int(kb * blk_l)
    torch.manual_seed(seed)
    W = torch.nn.Linear(Xtr.shape[1], n_dim, bias=False).to(device)
    opt = torch.optim.Adam(W.parameters(), lr=LR)
    gen = torch.Generator().manual_seed(seed)
    start_step = 0
    if ckpt_path.exists():
        try:
            ck = torch.load(str(ckpt_path), map_location=device)
            W.load_state_dict(ck["W"])
            opt.load_state_dict(ck["opt"])
            gen.set_state(ck["gen_state"])
            start_step = int(ck["step"])
            print(f"[step1b] resume {kind} student at step {start_step}",
                  flush=True)
        except (RuntimeError, KeyError, EOFError) as exc:
            print(f"[step1b] WARN ckpt load failed ({type(exc).__name__}); "
                  f"retraining from scratch", flush=True)
            start_step = 0
    V = Xtr.shape[0]
    Xd = Xtr.to(device)
    loss_first, loss_last = None, None
    for step in range(start_step, steps):
        bidx = torch.randint(0, V, (batch,), generator=gen)
        x = Xd[bidx.to(device)]
        z = W(x)
        s = _block_ste(z, kb, blk_l) if kind == "block" else _topk_ste(z, k_topk)
        s_n = s / (s.norm(dim=-1, keepdim=True) + 1e-8)
        T = x @ x.T
        off = ~torch.eye(batch, dtype=torch.bool, device=device)
        l_rkd = (((s_n @ s_n.T) - T)[off] ** 2).mean()
        # semi-hard negatives (vectorized; -1 padding falls back to random)
        p_ = pos_idx[bidx]
        cols = torch.randint(0, N_SEMI_CANDS, (batch, N_NEG_PER_ANCHOR),
                             generator=gen)
        negs = torch.gather(semi_cands[bidx], 1, cols)
        fallback = torch.randint(0, V, (batch, N_NEG_PER_ANCHOR),
                                 generator=gen)
        negs = torch.where(negs < 0, fallback, negs)
        cand_idx = torch.cat([p_.unsqueeze(1), negs], dim=1)  # [B, 1+neg]
        zc = W(Xd[cand_idx.reshape(-1).to(device)])
        sc = (_block_ste(zc, kb, blk_l) if kind == "block"
              else _topk_ste(zc, k_topk))
        sc = sc.reshape(batch, 1 + N_NEG_PER_ANCHOR, -1)
        sc_n = sc / (sc.norm(dim=-1, keepdim=True) + 1e-8)
        lg_h = torch.einsum("bd,bcd->bc", s_n, sc_n) / TAU_NCE
        lg_i = (s_n @ s_n.T / TAU_NCE).masked_fill(
            torch.eye(batch, dtype=torch.bool, device=device), -1e4)
        l_nce = torch.nn.functional.cross_entropy(
            torch.cat([lg_h, lg_i], dim=1),
            torch.zeros(batch, dtype=torch.long, device=device))
        loss = l_rkd + LAM_NCE * l_nce
        if not torch.isfinite(loss):
            raise RuntimeError(
                f"failure_class=NAN_LOSS: {kind} student loss non-finite at "
                f"step {step} (l_rkd={float(l_rkd)}, l_nce={float(l_nce)})")
        opt.zero_grad()
        loss.backward()
        opt.step()
        if loss_first is None:
            loss_first = float(loss)
        loss_last = float(loss)
        if step % 100 == 0:
            print(f"[step1b] {kind} step {step}/{steps} rkd={float(l_rkd):.4f} "
                  f"nce={float(l_nce):.4f} ({time.perf_counter() - t0:.1f}s)",
                  flush=True)
            _emit_heartbeat(output_dir, step, steps,
                            time.perf_counter() - t0,
                            extra={"phase": f"train_{kind}",
                                   "loss": float(loss)})
        if (step + 1) % ckpt_every == 0 or (step + 1) == steps:
            tmp = ckpt_path.with_suffix(".tmp")
            torch.save({"W": W.state_dict(), "opt": opt.state_dict(),
                        "gen_state": gen.get_state(), "step": step + 1},
                       str(tmp))
            os.replace(str(tmp), str(ckpt_path))
    return W, {"loss_first": loss_first if loss_first is not None else -1.0,
               "loss_last": loss_last if loss_last is not None else -1.0}


# ---------------------------------------------------------------------------
# Control arms.
# ---------------------------------------------------------------------------

def _charpos_codes(names: List[str], n_dim: int, k: int) -> torch.Tensor:
    enc = CharPositionalEncoder(n_dim=n_dim, max_pos=24,
                                seed_prefix="SPOKE1_S7")
    out = torch.zeros(len(names), n_dim, dtype=torch.float32)
    for i, nm in enumerate(names):
        txt = nm.replace("/", " ").replace("_", " ")
        acc = enc.encode_sentence(txt).astype(np.float32)
        if np.isnan(acc).any() or np.isinf(acc).any():
            raise RuntimeError(
                f"failure_class=NAN_CHARPOS: NaN/Inf at name idx {i}")
        mag = np.abs(acc)
        topk = np.argpartition(-mag, k)[:k]
        sgn = np.sign(acc[topk])
        sgn[sgn == 0] = 1
        out[i, torch.from_numpy(topk.astype(np.int64))] = \
            torch.from_numpy(sgn.astype(np.float32))
    return out


def _random_block_codes(n: int, kb: int, blk_l: int,
                        gen: torch.Generator) -> torch.Tensor:
    z = torch.zeros(n, kb, blk_l, dtype=torch.float32)
    idx = torch.randint(0, blk_l, (n, kb, 1), generator=gen)
    sgn = torch.randint(0, 2, (n, kb, 1), generator=gen).float() * 2 - 1
    z.scatter_(-1, idx, sgn)
    return z.reshape(n, kb * blk_l)


@torch.no_grad()
def _dense_sign_codes(W: torch.nn.Linear, X: torch.Tensor,
                      batch: int = 8192) -> torch.Tensor:
    n_dim = W.weight.shape[0]
    out = torch.zeros(X.shape[0], n_dim, dtype=torch.float32)
    for lo in range(0, X.shape[0], batch):
        z = W(X[lo:lo + batch].to(W.weight.device))
        s = torch.sign(z)
        s[s == 0] = 1.0
        out[lo:lo + batch] = s.cpu()
    return out


# ---------------------------------------------------------------------------
# Eval units.
# ---------------------------------------------------------------------------

def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra = np.argsort(np.argsort(a)).astype(np.float64)
    rb = np.argsort(np.argsort(b)).astype(np.float64)
    return float(np.corrcoef(ra, rb)[0, 1])


def _semantic_unit(arm: str, codes_he: torch.Tensor, codes_all: torch.Tensor,
                   Xhe: torch.Tensor, Xall: torch.Tensor, self_offset: int,
                   n_pairs: int, seed: int) -> Dict:
    """Semantic fidelity on held-out concepts vs teacher gold."""
    n_he = Xhe.shape[0]
    rng = np.random.default_rng(seed)
    i = torch.from_numpy(rng.integers(0, n_he, n_pairs))
    j = torch.from_numpy(rng.integers(0, n_he, n_pairs))
    keep = i != j
    i, j = i[keep], j[keep]
    tp = (Xhe[i] * Xhe[j]).sum(-1).numpy()
    cn = codes_he / (codes_he.norm(dim=-1, keepdim=True) + 1e-8)
    sp = (cn[i] * cn[j]).sum(-1).numpy()
    m8 = tp >= 0.80
    hi80_cos = float(sp[m8].mean()) if m8.sum() > 0 else float("nan")
    hi80_t = float(tp[m8].mean()) if m8.sum() > 0 else float("nan")
    # retrieval agreement @10 (chunked over held rows)
    ca = codes_all / (codes_all.norm(dim=-1, keepdim=True) + 1e-8)
    agree, chunk = 0.0, 1024
    for lo in range(0, n_he, chunk):
        hi = min(lo + chunk, n_he)
        rows = torch.arange(lo, hi)
        ts = Xhe[lo:hi] @ Xall.T
        ts[rows - lo, self_offset + rows] = -2.0
        t10 = ts.topk(10, dim=1).indices
        ss = cn[lo:hi] @ ca.T
        ss[rows - lo, self_offset + rows] = -2.0
        s10 = ss.topk(10, dim=1).indices
        for r in range(hi - lo):
            agree += len(set(t10[r].tolist()) & set(s10[r].tolist())) / 10.0
    return {
        "unit": f"semantic::{arm}", "arm": arm, "kind": "semantic",
        "spearman_all": _spearman(sp, tp),
        "pearson_all": float(np.corrcoef(sp, tp)[0, 1]),
        "hi80_cos": hi80_cos, "hi80_n": int(m8.sum()),
        "hi80_teacher_mean": hi80_t,
        "hi80_calib_err": (abs(hi80_cos - hi80_t)
                           if not math.isnan(hi80_cos) else float("nan")),
        "ret_agree10": agree / n_he,
        "n_pairs_sampled": int(len(tp)),
    }


def _chunked_cleanup_argmax(queries: torch.Tensor, codebook: torch.Tensor,
                            device: str) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Return (argmax idx, best sim, second-best sim) per query; cosine."""
    is_c = codebook.is_complex()
    qn = queries / (queries.abs().pow(2).sum(-1, keepdim=True).sqrt() + 1e-8) \
        if is_c else queries / (queries.norm(dim=-1, keepdim=True) + 1e-8)
    n_q = queries.shape[0]
    best = torch.full((n_q,), -2.0)
    second = torch.full((n_q,), -2.0)
    best_i = torch.zeros(n_q, dtype=torch.long)
    for lo in range(0, codebook.shape[0], CLEANUP_CHUNK):
        cb = codebook[lo:lo + CLEANUP_CHUNK].to(device)
        cbn = cb / (cb.abs().pow(2).sum(-1, keepdim=True).sqrt() + 1e-8) \
            if is_c else cb / (cb.norm(dim=-1, keepdim=True) + 1e-8)
        if is_c:
            sims = torch.real(qn.to(device) @ cbn.conj().T).cpu()
        else:
            sims = (qn.to(device) @ cbn.T).cpu()
        top2 = sims.topk(min(2, sims.shape[1]), dim=1)
        v1 = top2.values[:, 0]
        i1 = top2.indices[:, 0] + lo
        v2 = top2.values[:, 1] if sims.shape[1] > 1 else torch.full((n_q,), -2.0)
        upd = v1 > best
        second = torch.where(upd, torch.maximum(best, v2), torch.maximum(second, v1))
        best_i = torch.where(upd, i1, best_i)
        best = torch.where(upd, v1, best)
    return best_i, best, second


def _keyed_unit(arm: str, algebra: str, codes_all: torch.Tensor, kb: int,
                blk_l: int, J: int, n_trials: int, gen: torch.Generator,
                device: str, shuffled_key: bool = False) -> Dict:
    """bind(key_j, code_j) sum over J -> unbind key_q -> cleanup@1."""
    V, n_dim = codes_all.shape
    queries = []
    targets = []
    members = []
    for _ in range(n_trials):
        fi = torch.randint(0, V, (J,), generator=gen)
        if algebra == "sbc":
            keys = _random_block_codes(J, kb, blk_l, gen).reshape(J, kb, blk_l)
            bundle = torch.zeros(kb, blk_l)
            for j in range(J):
                bundle = bundle + bind(keys[j],
                                       codes_all[fi[j]].reshape(kb, blk_l))
            qj = int(torch.randint(0, J, (1,), generator=gen))
            key_q = (_random_block_codes(1, kb, blk_l, gen).reshape(kb, blk_l)
                     if shuffled_key else keys[qj])
            u = unbind(bundle, key_q).reshape(n_dim)
        elif algebra == "fhrr":
            keys = make_atoms(J, n_dim, torch.complex64, gen)
            cc = codes_all[fi].to(torch.complex64)
            bundle = torch.zeros(n_dim, dtype=torch.complex64)
            for j in range(J):
                bundle = bundle + bind(keys[j], cc[j])
            qj = int(torch.randint(0, J, (1,), generator=gen))
            key_q = (make_atoms(1, n_dim, torch.complex64, gen)[0]
                     if shuffled_key else keys[qj])
            u = unbind(bundle, key_q)
        else:
            raise ValueError(f"unknown algebra {algebra}")
        queries.append(u)
        targets.append(int(fi[qj]))
        members.append(fi.tolist())
    Q = torch.stack(queries)
    cb = codes_all.to(torch.complex64) if algebra == "fhrr" else codes_all
    pred, best, second = _chunked_cleanup_argmax(Q, cb, device)
    tgt = torch.tensor(targets)
    acc = float((pred == tgt).float().mean())
    hit_any = float(np.mean([int(int(pred[t]) in members[t])
                             for t in range(n_trials)]))
    unit_name = ("shuffled_key" if shuffled_key else "keyed")
    return {
        "unit": f"{unit_name}::{arm}::J{J}", "arm": arm, "kind": unit_name,
        "J": J, "algebra": algebra, "acc_at1": acc,
        "hit_any_member": hit_any,
        "snr_margin_mean": float((best - second).mean()),
        "n_trials": n_trials,
    }


def _bundle_unit(arm: str, codes_all: torch.Tensor, J: int, n_trials: int,
                 gen: torch.Generator, device: str) -> Dict:
    """Un-keyed superposition of J codes -> per-item top-J recall."""
    V = codes_all.shape[0]
    cn = codes_all / (codes_all.norm(dim=-1, keepdim=True) + 1e-8)
    rec = 0.0
    bundles = []
    fis = []
    for _ in range(n_trials):
        fi = torch.randint(0, V, (J,), generator=gen)
        fis.append(fi)
        bundles.append(cn[fi].sum(0))
    Q = torch.stack(bundles)
    qn = Q / (Q.norm(dim=-1, keepdim=True) + 1e-8)
    # chunked top-J over codebook
    n_q = Q.shape[0]
    all_vals = torch.full((n_q, J), -2.0)
    all_idx = torch.zeros(n_q, J, dtype=torch.long)
    for lo in range(0, V, CLEANUP_CHUNK):
        cb = cn[lo:lo + CLEANUP_CHUNK].to(device)
        sims = (qn.to(device) @ cb.T).cpu()
        merged_v = torch.cat([all_vals, sims], dim=1)
        merged_i = torch.cat(
            [all_idx, torch.arange(lo, min(lo + CLEANUP_CHUNK, V))
             .unsqueeze(0).expand(n_q, -1)], dim=1)
        top = merged_v.topk(J, dim=1)
        all_vals = top.values
        all_idx = torch.gather(merged_i, 1, top.indices)
    for t in range(n_trials):
        rec += len(set(all_idx[t].tolist()) & set(fis[t].tolist())) / J
    return {
        "unit": f"bundle::{arm}::J{J}", "arm": arm, "kind": "bundle",
        "J": J, "recall_at_J": rec / n_trials, "n_trials": n_trials,
    }


# ---------------------------------------------------------------------------
# Verdict logic.
# ---------------------------------------------------------------------------

def _by_unit(per_unit: List[Dict], kind: str, arm: str,
             J: Optional[int] = None) -> Optional[Dict]:
    for u in per_unit:
        if u["kind"] == kind and u["arm"] == arm and (J is None or u.get("J") == J):
            return u
    return None


def _verdict(per_unit: List[Dict], run_mode: str, expected_units: int,
             j_grid: List[int]) -> Tuple[str, str]:
    if len(per_unit) < expected_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"{len(per_unit)}/{expected_units} units")
    prim = "BLOCK_K128"
    sem = _by_unit(per_unit, "semantic", prim)
    sem_cp = _by_unit(per_unit, "semantic", "CHARPOS")
    keyed5 = _by_unit(per_unit, "keyed", prim, 5)
    bun5 = _by_unit(per_unit, "bundle", prim, 5)
    shuf = _by_unit(per_unit, "shuffled_key", prim, 5)
    posc = _by_unit(per_unit, "keyed", "RANDOM_BLOCK", 5)
    naive20 = _by_unit(per_unit, "keyed", "TOPK_NAIVE", 20)
    if not all([sem, sem_cp, keyed5, bun5, shuf, posc]):
        return ("HARD_FAIL", "HARD_FAIL_MISSING_GATE_UNITS")
    # controls first
    if posc["acc_at1"] < 0.98:
        return ("HARD_FAIL",
                f"HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH: RANDOM_BLOCK "
                f"keyed J=5 {posc['acc_at1']:.3f} < 0.98 (SBC lossless prior)")
    if shuf["acc_at1"] > 0.05 or shuf["hit_any_member"] > 0.10:
        return ("HARD_FAIL",
                f"HARD_FAIL_SHUFFLED_KEY_LEAK: wrong-key cleanup "
                f"{shuf['acc_at1']:.3f}/{shuf['hit_any_member']:.3f}")
    # bundle dominance vs dense at every J
    for J in j_grid:
        b = _by_unit(per_unit, "bundle", prim, J)
        dd = _by_unit(per_unit, "bundle", "DENSE_SIGN", J)
        if b is None or dd is None:
            return ("HARD_FAIL", f"HARD_FAIL_MISSING_BUNDLE_UNITS_J{J}")
        if b["recall_at_J"] < dd["recall_at_J"] - 1e-9:
            return ("HARD_FAIL",
                    f"HARD_FAIL_SPARSITY_NOT_PROTECTING: bundle J={J} "
                    f"BLOCK {b['recall_at_J']:.3f} < DENSE {dd['recall_at_J']:.3f}")
    a_val = sem["spearman_all"]
    b1 = keyed5["acc_at1"]
    b5 = bun5["recall_at_J"]
    d5 = _by_unit(per_unit, "bundle", "DENSE_SIGN", 5)["recall_at_J"]
    if run_mode == "full":
        # false-win gate FIRST (drill Q5): B1 < 0.90 rejects regardless of A
        if b1 < 0.90:
            return ("HARD_FAIL",
                    f"FALSE_WIN_ALGEBRA: keyed_roundtrip J=5 {b1:.3f} < 0.90 "
                    f"(semantic A={a_val:.3f} irrelevant per prereg)")
        g_a = "HP" if a_val >= 0.85 else ("MB" if a_val >= 0.70 else "HF")
        g_b1 = "HP" if b1 >= 0.95 else "MB"
        g_b2 = "PASS" if (b5 >= 0.55 and b5 >= d5 + 0.03) else "MB"
        if g_a == "HF":
            return ("HARD_FAIL",
                    f"G_A_SEMANTIC_FAIL: spearman {a_val:.3f} < 0.70 "
                    f"(algebra B1={b1:.3f})")
        if g_a == "HP" and g_b1 == "HP" and g_b2 == "PASS":
            return ("HARD_PASS",
                    f"DUAL_GATE_PASS: spearman={a_val:.3f} keyed@J5={b1:.3f} "
                    f"bundle@J5={b5:.3f} (dense {d5:.3f}) shuffled_ok pos_ctrl_ok")
        return ("MIDDLE_BAND",
                f"MB: G_A={g_a}({a_val:.3f}) G_B1={g_b1}({b1:.3f}) "
                f"G_B2={g_b2}({b5:.3f} vs dense {d5:.3f})")
    # smoke bands
    gap = sem["ret_agree10"] - sem_cp["ret_agree10"]
    if naive20 is None:
        return ("HARD_FAIL", "HARD_FAIL_MISSING_NAIVE_DEMO_UNIT")
    fails = []
    if a_val < 0.40:
        fails.append(f"S_A spearman {a_val:.3f} < 0.40")
    if gap < 0.10:
        fails.append(f"S_gap ret_agree10 gap {gap:.3f} < 0.10 "
                     f"(discriminator-did-not-fire META_RULE_K)")
    if b1 < 0.95:
        fails.append(f"S_B1 keyed J=5 {b1:.3f} < 0.95")
    if b5 < 0.50:
        fails.append(f"S_B2 bundle J=5 {b5:.3f} < 0.50")
    if naive20["acc_at1"] > 0.80:
        fails.append(f"S_falsewin_demo TOPK_NAIVE keyed J=20 "
                     f"{naive20['acc_at1']:.3f} > 0.80 (demo did not fire)")
    if fails:
        return ("SMOKE_GATE_FAIL", "; ".join(fails))
    verdict = "HARD_PASS" if a_val >= 0.60 else "MIDDLE_BAND"
    return (verdict,
            f"SMOKE_{verdict}: spearman={a_val:.3f} gap={gap:.3f} "
            f"keyed@J5={b1:.3f} bundle@J5={b5:.3f} "
            f"naive_demo@J20={naive20['acc_at1']:.3f} shuffled_ok pos_ctrl_ok")


# ---------------------------------------------------------------------------
# Experiment driver.
# ---------------------------------------------------------------------------

def run_experiment(run_mode: str, seed: int, device_arg: str,
                   n_dim: int, teacher_cache_arg: Optional[str]) -> int:
    anchor = f"{ANCHOR_NAME}_smoke" if run_mode == "smoke" else ANCHOR_NAME
    out_dir = get_output_dir(anchor)
    art_dir = _artifact_dir(run_mode)
    art_dir.mkdir(parents=True, exist_ok=True)
    device = ("cuda" if torch.cuda.is_available() else "cpu") \
        if device_arg == "auto" else device_arg
    if run_mode == "smoke":
        steps, batch = SMOKE_STEPS, SMOKE_BATCH
        j_grid, n_trials = SMOKE_J_GRID, SMOKE_TRIALS
        charpos_cap, pair_sample = SMOKE_CHARPOS_CAP, SMOKE_PAIR_SAMPLE
        k_blocks_list = [K_BLOCKS_PRIMARY]
        expected_units = EXPECTED_N_UNITS_SMOKE
        ckpt_every = CKPT_EVERY_STEPS_SMOKE
    else:
        steps, batch = FULL_STEPS, FULL_BATCH
        j_grid, n_trials = FULL_J_GRID, FULL_TRIALS
        charpos_cap, pair_sample = FULL_CHARPOS_CAP, FULL_PAIR_SAMPLE
        k_blocks_list = list(K_BLOCKS_FULL_SWEEP)
        expected_units = EXPECTED_N_UNITS_FULL
        ckpt_every = CKPT_EVERY_STEPS_FULL

    _write_start_marker(out_dir, run_mode, expected_units)
    t0 = time.perf_counter()
    print(f"[step1b] run_mode={run_mode} seed={seed} device={device} "
          f"n_dim={n_dim} k_blocks={k_blocks_list}", flush=True)

    cache_path = _resolve_teacher_cache(teacher_cache_arg)
    cache_bytes = cache_path.stat().st_size
    print(f"[step1b] teacher cache: {cache_path.name} "
          f"({cache_bytes / 1e6:.1f} MB)", flush=True)
    X, ids = _load_teacher(cache_path)
    V_cache = X.shape[0]
    print(f"[step1b] teacher: {V_cache} concepts x {X.shape[1]}d "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    rng = np.random.default_rng(seed)
    perm = rng.permutation(V_cache)
    if run_mode == "smoke":
        n_tr, n_he = SMOKE_N_TRAIN, SMOKE_N_HELD
        if V_cache < n_tr + n_he:
            raise RuntimeError(f"teacher cache too small: {V_cache}")
    else:
        n_he = min(int(round(V_cache * HELD_FRAC)), FULL_HELD_CAP)
        n_tr = V_cache - n_he
    tr_idx = perm[:n_tr]
    he_idx = perm[n_tr:n_tr + n_he]
    Xtr = X[torch.from_numpy(tr_idx.copy())].contiguous()
    Xhe = X[torch.from_numpy(he_idx.copy())].contiguous()
    names_tr = [ids[i] for i in tr_idx]
    names_he = [ids[i] for i in he_idx]
    print(f"[step1b] split train={n_tr} held={n_he}", flush=True)

    pos_idx, semi_cands = _mine_teacher(
        Xtr, device, art_dir / "_mine_shards", out_dir, t0)
    semi_cov = float((semi_cands[:, 0] >= 0).float().mean())
    print(f"[step1b] mining done; semi-hard coverage={semi_cov:.3f} "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    # --- train students -------------------------------------------------
    Xall = torch.cat([Xtr, Xhe])
    arm_codes: Dict[str, torch.Tensor] = {}
    train_diag: Dict[str, Dict] = {}
    for kb in k_blocks_list:
        blk_l = n_dim // kb
        if kb * blk_l != n_dim:
            raise ValueError(f"n_dim {n_dim} not divisible by k_blocks {kb}")
        arm = f"BLOCK_K{kb}"
        W, diag = _train_student(
            "block", kb, blk_l, kb, Xtr, pos_idx, semi_cands,
            steps, batch, seed, device,
            art_dir / f"_ckpt_block_K{kb}.pt", ckpt_every, out_dir, t0)
        arm_codes[arm] = _encode_hard_block(W, Xall, kb, blk_l)
        train_diag[arm] = diag
        if kb == K_BLOCKS_PRIMARY:
            arm_codes["DENSE_SIGN"] = _dense_sign_codes(W, Xall)
            W_primary = W
        # artifact write (int8 codes for the cache concepts + W)
        codes_i8 = arm_codes[arm].to(torch.int8).numpy()
        meta = {
            "n_dim": n_dim, "k_blocks": kb, "block_len": blk_l,
            "sparsity": kb / n_dim, "seed": seed, "steps": steps,
            "teacher_cache": cache_path.name,
            "teacher_cache_bytes": cache_bytes,
            "objective": "RKD + 0.5*InfoNCE(semi-hard [0.3,0.6])",
            "composition_algebra": "SBC_block_local_circular_convolution",
            "cell": ANCHOR_NAME, "run_mode": run_mode,
            "ts_iso": datetime.now(timezone.utc).isoformat(),
        }
        tmp_npz = art_dir / f"encoder_distilled_K{kb}.tmp.npz"
        np.savez(str(tmp_npz), codes=codes_i8,
                 W=W.weight.detach().cpu().numpy(),
                 train_idx=tr_idx.astype(np.int64),
                 held_idx=he_idx.astype(np.int64),
                 ids_json=np.array(json.dumps(names_tr + names_he)),
                 metadata=np.array(json.dumps(meta)))
        os.replace(str(tmp_npz), str(art_dir / f"encoder_distilled_K{kb}.npz"))
        print(f"[step1b] {arm} trained + artifact written "
              f"({time.perf_counter() - t0:.1f}s)", flush=True)

    # TOPK naive comparison student (k = K_BLOCKS_PRIMARY active dims)
    W_topk, diag_topk = _train_student(
        "topk", K_BLOCKS_PRIMARY, n_dim // K_BLOCKS_PRIMARY, K_BLOCKS_PRIMARY,
        Xtr, pos_idx, semi_cands, steps, batch, seed, device,
        art_dir / "_ckpt_topk.pt", ckpt_every, out_dir, t0)
    arm_codes["TOPK_NAIVE"] = _encode_hard_topk(W_topk, Xall, K_BLOCKS_PRIMARY)
    train_diag["TOPK_NAIVE"] = diag_topk

    gen_ctrl = torch.Generator().manual_seed(seed + 1)
    arm_codes["RANDOM_BLOCK"] = _random_block_codes(
        Xall.shape[0], K_BLOCKS_PRIMARY, n_dim // K_BLOCKS_PRIMARY, gen_ctrl)

    # CHARPOS on capped subset (declared in prereg)
    n_cp_he = min(n_he, charpos_cap * 2 // 5)
    n_cp_tr = min(n_tr, charpos_cap - n_cp_he)
    cp_codes = _charpos_codes(names_tr[:n_cp_tr] + names_he[:n_cp_he],
                              n_dim, K_BLOCKS_PRIMARY)
    print(f"[step1b] control arms built ({time.perf_counter() - t0:.1f}s)",
          flush=True)

    # --- META_RULE_AF arms-must-differ ----------------------------------
    digests = {}
    for name, c in list(arm_codes.items()) + [("CHARPOS", cp_codes)]:
        digests[name] = hashlib.sha256(
            c.to(torch.int8).numpy().tobytes()).hexdigest()
    pairs = [(a, b) for a in digests for b in digests if a < b]
    for a, b in pairs:
        if digests[a] == digests[b]:
            raise RuntimeError(
                f"failure_class=META_RULE_AF_VIOLATION: arms {a}/{b} "
                f"bit-identical hash={digests[a]}")

    # --- eval units ------------------------------------------------------
    per_unit: List[Dict] = []
    unit_fail: List[Dict] = []
    total_planned = expected_units
    gen_eval = torch.Generator().manual_seed(seed + 2)

    def _run_unit(fn, *a, **kw):
        try:
            u = fn(*a, **kw)
            per_unit.append(u)
            _emit_heartbeat(out_dir, len(per_unit), total_planned,
                            time.perf_counter() - t0,
                            extra={"unit": u["unit"]})
            print(f"[step1b] unit {len(per_unit)}/{total_planned} "
                  f"{u['unit']}: "
                  + json.dumps({k: round(v, 4) for k, v in u.items()
                                if isinstance(v, float)}), flush=True)
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append({"fn": getattr(fn, "__name__", "?"),
                              "failure_class": type(exc).__name__,
                              "msg": str(exc)[:300]})
            raise  # FAIL_LOUD; no silent continue (META_RULE_J)

    he_lo = n_tr  # held rows start at offset n_tr inside Xall/codes_all
    sem_arms = [(a, arm_codes[a]) for a in
                ([f"BLOCK_K{kb}" for kb in k_blocks_list]
                 + ["TOPK_NAIVE", "RANDOM_BLOCK", "DENSE_SIGN"])]
    for arm, call in sem_arms:
        _run_unit(_semantic_unit, arm, call[he_lo:], call, Xhe, Xall, he_lo,
                  pair_sample, seed + 3)
    # CHARPOS semantic on its own capped subset
    cp_he = cp_codes[n_cp_tr:]
    cp_Xhe = Xhe[:n_cp_he]
    cp_Xall = torch.cat([Xtr[:n_cp_tr], cp_Xhe])
    _run_unit(_semantic_unit, "CHARPOS", cp_he, cp_codes, cp_Xhe, cp_Xall,
              n_cp_tr, pair_sample, seed + 3)

    blk_l_primary = n_dim // K_BLOCKS_PRIMARY
    algebra_arms = [(f"BLOCK_K{kb}", "sbc", kb) for kb in k_blocks_list] + [
        ("TOPK_NAIVE", "fhrr", K_BLOCKS_PRIMARY),
        ("RANDOM_BLOCK", "sbc", K_BLOCKS_PRIMARY),
        ("DENSE_SIGN", "fhrr", K_BLOCKS_PRIMARY),
    ]
    for arm, alg, kb in algebra_arms:
        for J in j_grid:
            _run_unit(_keyed_unit, arm, alg, arm_codes[arm], kb,
                      n_dim // kb, J, n_trials, gen_eval, device)
    _run_unit(_keyed_unit, "BLOCK_K128", "sbc", arm_codes["BLOCK_K128"],
              K_BLOCKS_PRIMARY, blk_l_primary, 5, n_trials, gen_eval, device,
              shuffled_key=True)
    for arm, alg, kb in algebra_arms:
        for J in j_grid:
            _run_unit(_bundle_unit, arm, arm_codes[arm], J, n_trials,
                      gen_eval, device)

    # --- verdict ---------------------------------------------------------
    verdict, verdict_msg = _verdict(per_unit, run_mode, expected_units, j_grid)
    elapsed = time.perf_counter() - t0
    sem_prim = _by_unit(per_unit, "semantic", "BLOCK_K128") or {}
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "elapsed_s": float(elapsed),
        "run_mode": run_mode,
        "anchor_name": anchor,
        "seed": int(seed),
        "device": device,
        "N": n_dim,
        "k_blocks_list": k_blocks_list,
        "k_blocks_primary": K_BLOCKS_PRIMARY,
        "sparsity_primary": K_BLOCKS_PRIMARY / n_dim,
        "teacher_cache": cache_path.name,
        "teacher_cache_bytes": cache_bytes,
        "teacher_n_concepts": V_cache,
        "n_train": n_tr, "n_held": n_he,
        "steps": steps, "batch": batch,
        "j_grid": j_grid, "n_trials": n_trials,
        "semi_hard_coverage": semi_cov,
        "train_diag": train_diag,
        "per_unit": per_unit,
        "unit_failures": unit_fail,
        "n_units": len(per_unit),
        "expected_n_units": expected_units,
        "cardinality_ok": len(per_unit) == expected_units,
        "arms_differ_verified": True,
        "arm_code_sha256": digests,
        "final_metrics_atomicity": "tmp_replace",
        "baseline_in_band": bool(
            0.05 < (_by_unit(per_unit, "semantic", "CHARPOS") or
                    {"ret_agree10": 0})["ret_agree10"] < 0.95),
        "composition_algebra": "SBC_block_local_circular_convolution",
        "progress_logging": "print_flush_true",
        "primary_spearman": sem_prim.get("spearman_all"),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[step1b] verdict={verdict} msg={verdict_msg} "
          f"elapsed={elapsed:.1f}s", flush=True)
    return 0


# ---------------------------------------------------------------------------
# Self-test (synthetic teacher; no cache dependency; fast).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()
    n_dim, kb, blk_l, v = 256, 16, 16, 400
    torch.manual_seed(11)
    X = torch.randn(v, 64)
    X = X / X.norm(dim=-1, keepdim=True)
    gen = torch.Generator().manual_seed(11)
    # block STE: exact 1-per-block sparsity + gradient flows
    W = torch.nn.Linear(64, n_dim, bias=False)
    z = W(X[:32])
    s = _block_ste(z, kb, blk_l)
    nnz = (s != 0).sum(dim=-1)
    assert bool((nnz == kb).all()), f"selftest: block nnz {nnz.unique()} != {kb}"
    per_block = (s.reshape(32, kb, blk_l) != 0).sum(-1)
    assert bool((per_block == 1).all()), "selftest: not 1-active-per-block"
    loss = (s ** 2).mean()
    loss.backward()
    g = W.weight.grad
    assert g is not None and bool(torch.isfinite(g).all()) and \
        float(g.abs().sum()) > 0, "selftest: STE gradient dead"
    # hard encode matches sparsity + int8-safe values
    codes = _encode_hard_block(W, X, kb, blk_l)
    assert bool(((codes == 0) | (codes == 1) | (codes == -1)).all()), \
        "selftest: non-ternary code"
    # SBC keyed roundtrip on random block codes (lossless prior, small regime)
    rb = _random_block_codes(v, kb, blk_l, gen)
    u = _keyed_unit("RB", "sbc", rb, kb, blk_l, 2, 20, gen, "cpu")
    assert u["acc_at1"] >= 0.90, f"selftest: SBC keyed J=2 {u['acc_at1']}"
    us = _keyed_unit("RB", "sbc", rb, kb, blk_l, 2, 20, gen, "cpu",
                     shuffled_key=True)
    assert us["acc_at1"] <= 0.20, f"selftest: shuffled-key leak {us['acc_at1']}"
    # bundle unit runs + in [0,1]
    ub = _bundle_unit("RB", rb, 2, 20, gen, "cpu")
    assert 0.0 <= ub["recall_at_J"] <= 1.0, "selftest: bundle recall OOB"
    # FHRR path smoke (dense sign codes are valid phasors)
    dn = torch.sign(torch.randn(v, n_dim, generator=gen))
    dn[dn == 0] = 1.0
    uf = _keyed_unit("DN", "fhrr", dn, kb, blk_l, 2, 20, gen, "cpu")
    assert uf["acc_at1"] >= 0.90, f"selftest: FHRR dense J=2 {uf['acc_at1']}"
    # spearman helper sanity
    a = np.arange(100).astype(np.float64)
    assert abs(_spearman(a, a) - 1.0) < 1e-9, "selftest: spearman broken"
    print(f"[selftest] PASS (block-STE + SBC roundtrip {u['acc_at1']:.2f} + "
          f"shuffled {us['acc_at1']:.2f} + fhrr {uf['acc_at1']:.2f}) "
          f"elapsed={time.perf_counter() - t0:.2f}s", flush=True)
    return 0


# ---------------------------------------------------------------------------
# Entry.
# ---------------------------------------------------------------------------

def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=(
        "Encoder Migration Step 1b -- BGE distillation into sparse block "
        "codes, dual-gated (semantic + algebra)"))
    p.add_argument("--run-mode",
                   default=os.environ.get("HDLAB_RUN_MODE", "self_test"),
                   choices=["self_test", "smoke", "full"])
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--full", action="store_true")
    p.add_argument("--seed", type=int, default=SEED_DEFAULT)
    p.add_argument("--device", default="auto",
                   choices=["auto", "cpu", "cuda"])
    p.add_argument("--n-dim", type=int, default=N_DIM_DEFAULT)
    p.add_argument("--teacher-cache", default=None,
                   help="explicit teacher npz path (default: largest match)")
    args, _ = p.parse_known_args(argv)
    if args.self_test:
        args.run_mode = "self_test"
    elif args.smoke:
        args.run_mode = "smoke"
    elif args.full:
        args.run_mode = "full"
    return args


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    args = _parse_args()
    if args.run_mode == "self_test":
        return run_self_test()
    return run_experiment(args.run_mode, args.seed, args.device,
                          args.n_dim, args.teacher_cache)


if __name__ == "__main__":
    _fallback_out = get_output_dir(ANCHOR_NAME)
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException per META_RULE section 8
        try:
            _write_crash_metrics(_fallback_out, exc)
        except Exception:
            pass  # crash-writer failure is not fatal
        raise
