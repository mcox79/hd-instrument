"""Encoder Migration Step 1b v3 - GLOBAL (landmark) RKD objective; the R1 rescue
for the full-scale HARD_FAIL diagnosed in
notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md.

THE PROBLEM v3 FIXES (do not re-litigate; see diagnosis note):
  The v2 RKD target is the IN-BATCH teacher cosine matrix x@x.T (512x512). Over
  160k+ concepts a batch of 512 samples ~0.32% of pairs; graded near-neighbor
  pairs (what spearman measures) co-occur in a batch ~1e-5/step, so graded
  geometry is NEVER supervised at scale. Proof it is the objective not the
  sparsifier: the DENSE_SIGN readout (NO sparsifier) ALSO collapsed 0.825(3k) ->
  0.368(178k); rkd converged to a 2.4x-higher floor with lr fully decayed (not
  under-training); 13x more teacher-draws/concept yet WORSE held generalization.

v3 delta over v2 (EXACTLY the objective; everything else preserved):
  1. OBJECTIVE = GLOBAL LANDMARK RKD. Replace the in-batch [batch x batch] RKD
     target with a [batch x L] target against a FIXED landmark/anchor frame of
     L (~4-8k) train concepts. Per step: match each batch concept's STUDENT-code
     cosine-to-landmarks against its TEACHER cosine-to-the-same-landmarks
     (l_rkd = mean( (s_n @ frame_n.T - Xbatch @ Xland.T)^2 )). Every concept gets
     a global L-dim coordinate frame EVERY step, independent of random in-batch
     co-occurrence. The landmark frame = the student's own landmark codes,
     refreshed (no_grad, detached) every REFRESH steps -- a cheap projection basis;
     the JL argument guarantees matching L>=~N_DIM landmark-cosine-profiles
     reproduces the teacher pairwise geometry, so near-neighbours (near-identical
     profiles) are transitively pulled together WITHOUT needing to co-occur.
  2. --objective {global,in_batch} selects the RKD target. in_batch reproduces the
     v2 objective EXACTLY, as the controlled baseline for the recovery discriminator.
  3. NEW run_mode 'mid' (~40k concepts, local CPU): trains GLOBAL + IN_BATCH_REF at
     matched config and reports the RECOVERY discriminator on the DENSE_SIGN readout
     first (the diagnosis-mandated validation gate) BEFORE any sparse re-check.
  4. Optional composed lever --cluster-frac (neighbor-clustered batches reusing the
     semi-hard mining) is available but DEFAULT 0.0 so the mid validation isolates
     the landmark-RKD effect cleanly.

Unchanged validated machinery (v2): MLP student (1024->2048 GELU ->4096), block
codes (K=128, L=32, 3.125% sparse), block-STE, SBC block-local circular
convolution algebra (roundtrip 1.000 self-test), semi-hard InfoNCE (NO
absolute-MSE), warmup+cosine LR, held-out semantic eval, defensive error-checking,
chunked+checkpointed mining/training. The MLP capacity + algebra path are NOT the
question here; the OBJECTIVE is.

Composition algebra (prereg field): SBC_block_local_circular_convolution. The
sparse block code is NOT a valid literal-FHRR atom; naive top-k + FHRR is retained
ONLY as the false-win comparison arm.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke/mid gate (sha256 over semantic-arm code matrices)
- final_metrics_atomicity: tmp_replace (write_metrics helper)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_floor_computed: r_max=0.901 at K=128 (THEORETICAL@ prereg; same regime v2)
- baseline_in_band: CHARPOS ret_agree@10 = 0.098 MEASURED@v1 smoke in (0.05,0.95)
- discriminator: the recovery discriminator (mid GLOBAL DENSE spearman >
  IN_BATCH DENSE spearman by a pre-reg margin) is run at INTERMEDIATE scale on
  local CPU, NOT deferred to FULL; this is the diagnosis-mandated validation.
- HARD_PASS strictly above floor per prereg bands (META_RULE_L)
- HP_SCOPE per-arm declared in prereg (gates on GLOBAL_BLOCK_K128 / recovery only)
- cardinality_ok: EXPECTED_N_UNITS declared per run_mode, counted from per_unit
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime (prereg evidence)
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

Prereg: preregs/2026-07-04_exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1.md
v2 cell: experiments/exp_encoder_migration_step1b_v2_mlp_distill_concept_encoder_v1_core.py

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
ANCHOR_NAME = "encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1"

_CACHE_DIR = _REPO / "data" / "substrate_index" / "cached_indices"
TEACHER_GLOB = "bge_large_v2_name_*.npz"

N_DIM_DEFAULT = 4096
K_BLOCKS_PRIMARY = 128          # L=32; sparsity 3.125% (prereg rationale)
K_BLOCKS_FULL_SWEEP = [128, 64]  # primary first; K64 report-only arm
SEED_DEFAULT = 7

# ---- v3 GLOBAL LANDMARK RKD objective config ------------------------------
OBJECTIVE_DEFAULT = "global"     # {global, in_batch}; global = the R1 fix
# Landmark/anchor frame: a FIXED set of train-concept indices. Random anchor
# frame (JL projection basis); L scaled by run mode. K-means centroids are a
# documented follow-up lever if random under-covers (prereg).
N_LANDMARKS_SMOKE = 1024
N_LANDMARKS_MID = 4096
N_LANDMARKS_FULL = 8192
# Frame refresh cadence: re-encode all landmark codes with the CURRENT student
# (no_grad, detached) every REFRESH steps. Frame is at most REFRESH steps stale
# (negligible vs total steps); amortizes the L-forward cost to ~0/step.
FRAME_REFRESH_SMOKE = 25
FRAME_REFRESH_MID = 50
FRAME_REFRESH_FULL = 100
# Optional composed lever (default off for clean landmark-RKD attribution):
# fraction of each batch built as seed+semi-hard-neighbour clusters so in-batch
# pairs ALSO cover graded structure. 0.0 = pure random batches.
CLUSTER_FRAC_DEFAULT = 0.0
CLUSTER_SIZE = 8                 # concepts per neighbour cluster when enabled

# v2 student architecture.
STUDENT_ARCH_PRIMARY = "mlp"    # MLP student is the v2 fix (REQUIRED for 0.85)
MLP_HIDDEN = 2048               # Linear(1024->2048) GELU Linear(2048->4096)

TAU_NCE = 0.07
LAM_NCE = 0.5
TAU_GUMBEL = 1.0
LR = 1e-3
WARMUP_STEPS = 400              # v2: linear warmup then cosine decay
SEMI_LO, SEMI_HI = 0.30, 0.60   # semi-hard teacher-cos band (drill Q4)
N_SEMI_CANDS = 64
N_NEG_PER_ANCHOR = 4
HELD_FRAC = 0.10

# v2 capacity-preview discriminator: MLP geometry-loss must beat LINEAR by >=10%
# on matched smoke data (option-C discriminator-preview arm). This is the
# mechanism-fires assertion for the "MLP has capacity a linear map lacks" claim.
CAPACITY_RKD_MAX_RATIO = 0.90

# Run-mode grids.
SMOKE_N_TRAIN, SMOKE_N_HELD = 3000, 800
SMOKE_STEPS, SMOKE_BATCH = 150, 192
SMOKE_J_GRID = [5, 20]
SMOKE_TRIALS = 50
SMOKE_CHARPOS_CAP = 2000
SMOKE_PAIR_SAMPLE = 250_000

FULL_STEPS, FULL_BATCH = 40_000, 512   # v2: batch 512 (was 1024); 40k steps for
#                                        sample-budget parity vs v1 (batch halved
#                                        + MLP needs more optimization; smoke showed
#                                        MLP under-trains at low steps: dense readout
#                                        0.825 but block code 0.645 at 150 steps)
FULL_J_GRID = [2, 5, 10, 20]
FULL_TRIALS = 200
FULL_CHARPOS_CAP = 5000
FULL_PAIR_SAMPLE = 500_000
FULL_HELD_CAP = 20_000

# run_mode 'mid' (~40k concepts, local CPU): the diagnosis-mandated INTERMEDIATE
# validation. Trains GLOBAL + IN_BATCH_REF at MATCHED config; reports the recovery
# discriminator on DENSE_SIGN first. Steps sized so DENSE geometry plateaus (dense
# geometry forms fast: v2 3k/150-step smoke already hit dense 0.825) while the
# in-batch baseline reaches its scale-limited plateau (~0.37-0.64 per diagnosis).
MID_STEPS, MID_BATCH = 1800, 512
MID_TRIALS = 60
MID_CHARPOS_CAP = 3000
MID_PAIR_SAMPLE = 400_000
MID_HELD_CAP = 5000
MID_J_GRID = [5]                 # algebra sanity only (objective does not touch it)
MID_DENSE_EVAL_EVERY = 300       # log DENSE-spearman trajectory during training

CKPT_EVERY_STEPS_FULL = 500
CKPT_EVERY_STEPS_MID = 300
CKPT_EVERY_STEPS_SMOKE = 50
# MINE_CHUNK is purely a batching axis over teacher rows: mining is
# shard-checkpointed (mine_*.npz) and each row's positive (argmax) + semi-hard
# candidates (uniform sample from the [SEMI_LO,SEMI_HI] band) are computed over
# the full V columns independent of chunk size. Reduced 2048->256 to cap the
# per-chunk [chunk,V] float32 materialization (sims/band/multinomial-weights)
# at ~0.5GB instead of ~4-6GB so mining fits a BOINC-shared 8GB GPU. Smaller
# chunks = more shards, no change to the semi-hard candidate semantics.
MINE_CHUNK = 256
CLEANUP_CHUNK = 16384

EXPECTED_N_UNITS_SMOKE = 22
EXPECTED_N_UNITS_FULL = 47
# mid: per objective {global,in_batch} x {BLOCK semantic, DENSE semantic} = 4
# semantic units + CHARPOS semantic (1) + RANDOM_BLOCK semantic (1)
# + keyed J5 for GLOBAL_BLOCK + RANDOM_BLOCK pos-ctrl + shuffled (3) = 9.
EXPECTED_N_UNITS_MID = 9

PREREG_BASELINE_ARMS = ["CHARPOS"]


def _artifact_dir(run_mode: str) -> Path:
    suffix = {"smoke": "_smoke", "mid": "_mid"}.get(run_mode, "")
    return _REPO / "data" / f"substrate_concept_encoder_v1b_v3global{suffix}"


def _warmup_for(steps: int) -> int:
    """Scale warmup to run length so smoke is not entirely inside warmup."""
    return min(WARMUP_STEPS, max(10, steps // 5))


def _lr_at(step: int, total: int, warmup: int, base_lr: float) -> float:
    """Linear warmup then cosine decay to ~0. step is 0-indexed global step."""
    if warmup > 0 and step < warmup:
        return base_lr * float(step + 1) / float(warmup)
    denom = max(1, total - warmup)
    prog = float(step - warmup) / float(denom)
    prog = min(1.0, max(0.0, prog))
    return 0.5 * base_lr * (1.0 + math.cos(math.pi * prog))


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
        del sims  # free [C,V] before materializing multinomial weights
        n_band = band.sum(dim=1)
        semi = torch.full((hi - lo, N_SEMI_CANDS), -1,
                          dtype=torch.long, device=device)
        ok = n_band > 0
        if ok.any():
            # band[ok] copies only the ok-rows (each with >=1 band member);
            # add the numerical-safety epsilon in place to avoid a second
            # [n_ok, V] temporary. Math is identical to band[ok] + 1e-12.
            band_ok = band[ok]
            band_ok.add_(1e-12)
            picks = torch.multinomial(
                band_ok, N_SEMI_CANDS, replacement=True)
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
            print(f"[step1b_v3] mine chunk {c + 1}/{n_chunks} "
                  f"({time.perf_counter() - t0:.1f}s)", flush=True)
    if (pos_all < 0).any():
        raise RuntimeError("mining left unfilled positive rows")
    return pos_all, semi_all


# ---------------------------------------------------------------------------
# Students (linear + MLP) + sparsifiers.
# ---------------------------------------------------------------------------

class _LinearStudent(torch.nn.Module):
    """v1 student: single linear map (capacity ceiling ~0.64 at full scale)."""

    def __init__(self, in_dim: int, out_dim: int):
        super().__init__()
        self.net = torch.nn.Linear(in_dim, out_dim, bias=False)
        self.out_dim = out_dim

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class _MLPStudent(torch.nn.Module):
    """v2 student: 1-hidden-layer MLP (the capacity fix for 0.85)."""

    def __init__(self, in_dim: int, hidden: int, out_dim: int):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(in_dim, hidden),
            torch.nn.GELU(),
            torch.nn.Linear(hidden, out_dim, bias=False),
        )
        self.out_dim = out_dim

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def _make_student(arch: str, in_dim: int, out_dim: int, device: str,
                  seed: int) -> torch.nn.Module:
    torch.manual_seed(seed)
    if arch == "mlp":
        s: torch.nn.Module = _MLPStudent(in_dim, MLP_HIDDEN, out_dim)
    elif arch == "linear":
        s = _LinearStudent(in_dim, out_dim)
    else:
        raise ValueError(f"unknown student arch {arch}")
    return s.to(device)


def _student_device(student: torch.nn.Module) -> torch.device:
    return next(student.parameters()).device


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
def _frame_codes_norm(student: torch.nn.Module, Xland_d: torch.Tensor,
                      kind: str, kb: int, blk_l: int, k_topk: int) -> torch.Tensor:
    """Normalized DETACHED landmark-code frame [L, N_DIM] for GLOBAL RKD.

    Encodes the landmark teacher embeddings with the CURRENT student (hard STE,
    no grad). Refreshed periodically during training; cheap projection basis.
    """
    z = student(Xland_d)
    s = _block_ste(z, kb, blk_l) if kind == "block" else _topk_ste(z, k_topk)
    s_n = s / (s.norm(dim=-1, keepdim=True) + 1e-8)
    return s_n.detach()


def _cluster_batch_idx(batch: int, cluster_frac: float, V: int,
                       pos_idx: torch.Tensor, semi_cands: torch.Tensor,
                       gen: torch.Generator) -> torch.Tensor:
    """Composed lever (default off): part of the batch = seed + semi-hard
    neighbours so in-batch pairs ALSO cover graded structure. Returns [batch]
    indices. cluster_frac=0.0 -> pure random batch (landmark-RKD-only test)."""
    if cluster_frac <= 0.0:
        return torch.randint(0, V, (batch,), generator=gen)
    n_cluster = int(round(batch * cluster_frac))
    n_random = batch - n_cluster
    parts = [torch.randint(0, V, (n_random,), generator=gen)]
    n_seeds = max(1, n_cluster // CLUSTER_SIZE)
    filled = 0
    for _ in range(n_seeds):
        seed_i = int(torch.randint(0, V, (1,), generator=gen))
        members = [seed_i, int(pos_idx[seed_i])]
        cand = semi_cands[seed_i]
        cand = cand[cand >= 0]
        if cand.numel() > 0:
            pick = cand[torch.randint(0, cand.numel(),
                                      (CLUSTER_SIZE - 2,), generator=gen)]
            members.extend(pick.tolist())
        take = members[:min(len(members), n_cluster - filled)]
        parts.append(torch.tensor(take, dtype=torch.long))
        filled += len(take)
        if filled >= n_cluster:
            break
    idx = torch.cat(parts)[:batch]
    if idx.numel() < batch:  # pad with random if clusters underfilled
        idx = torch.cat([idx, torch.randint(
            0, V, (batch - idx.numel(),), generator=gen)])
    return idx


@torch.no_grad()
def _encode_hard_block(student: torch.nn.Module, X: torch.Tensor, kb: int,
                       blk_l: int, batch: int = 8192) -> torch.Tensor:
    dev = _student_device(student)
    out = torch.zeros(X.shape[0], kb * blk_l, dtype=torch.float32)
    for lo in range(0, X.shape[0], batch):
        z = student(X[lo:lo + batch].to(dev)).reshape(-1, kb, blk_l)
        o = torch.zeros_like(z)
        idx = z.abs().argmax(dim=-1, keepdim=True)
        sgn = torch.sign(torch.gather(z, -1, idx))
        sgn[sgn == 0] = 1.0
        o.scatter_(-1, idx, sgn)
        out[lo:lo + batch] = o.reshape(-1, kb * blk_l).cpu()
    return out


@torch.no_grad()
def _encode_hard_topk(student: torch.nn.Module, X: torch.Tensor, k: int,
                      batch: int = 8192) -> torch.Tensor:
    dev = _student_device(student)
    n_dim = student.out_dim
    out = torch.zeros(X.shape[0], n_dim, dtype=torch.float32)
    for lo in range(0, X.shape[0], batch):
        z = student(X[lo:lo + batch].to(dev))
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
    arch: str,                    # "mlp" | "linear"
    kb: int, blk_l: int, k_topk: int,
    Xtr: torch.Tensor, pos_idx: torch.Tensor, semi_cands: torch.Tensor,
    steps: int, batch: int, warmup: int, seed: int, device: str,
    ckpt_path: Path, ckpt_every: int, output_dir: Path, t0: float,
    objective: str = "global",         # v3: {global, in_batch}
    land_idx: Optional[torch.Tensor] = None,   # train-concept landmark indices
    refresh_every: int = FRAME_REFRESH_FULL,
    cluster_frac: float = CLUSTER_FRAC_DEFAULT,
    dense_eval_fn=None,                # optional: student -> DENSE spearman float
    dense_eval_every: int = 0,
) -> Tuple[torch.nn.Module, Dict[str, float]]:
    out_dim = kb * blk_l
    student = _make_student(arch, Xtr.shape[1], out_dim, device, seed)
    opt = torch.optim.Adam(student.parameters(), lr=LR)
    gen = torch.Generator().manual_seed(seed)
    start_step = 0
    if ckpt_path.exists():
        try:
            ck = torch.load(str(ckpt_path), map_location=device)
            student.load_state_dict(ck["student"])
            opt.load_state_dict(ck["opt"])
            gen.set_state(ck["gen_state"])
            start_step = int(ck["step"])
            print(f"[step1b_v3] resume {arch}/{kind}/{objective} student at step "
                  f"{start_step}", flush=True)
        except (RuntimeError, KeyError, EOFError) as exc:
            print(f"[step1b_v3] WARN ckpt load failed ({type(exc).__name__}); "
                  f"retraining from scratch", flush=True)
            start_step = 0
    if objective not in ("global", "in_batch"):
        raise ValueError(f"unknown objective {objective}")
    V = Xtr.shape[0]
    Xd = Xtr.to(device)
    Xland_d = None
    if objective == "global":
        if land_idx is None or land_idx.numel() == 0:
            raise ValueError("global objective requires non-empty land_idx")
        Xland_d = Xd[land_idx.to(device)]          # [L, teacher_dim] fixed
    frame_n = None                                  # refreshed detached [L, N_DIM]
    loss_first = loss_last = None
    rkd_last = nce_last = lr_last = None
    dense_traj: List[Dict[str, float]] = []
    for step in range(start_step, steps):
        cur_lr = _lr_at(step, steps, warmup, LR)
        for g in opt.param_groups:
            g["lr"] = cur_lr
        bidx = _cluster_batch_idx(batch, cluster_frac, V, pos_idx, semi_cands, gen)
        x = Xd[bidx.to(device)]
        z = student(x)
        s = _block_ste(z, kb, blk_l) if kind == "block" else _topk_ste(z, k_topk)
        s_n = s / (s.norm(dim=-1, keepdim=True) + 1e-8)
        if objective == "global":
            # GLOBAL LANDMARK RKD: match code-vs-frame cosine to teacher-vs-land
            # cosine. Every batch concept supervised against L global coords.
            if frame_n is None or (step % refresh_every == 0):
                frame_n = _frame_codes_norm(
                    student, Xland_d, kind, kb, blk_l, k_topk)
            Tland = x @ Xland_d.T                    # [B, L] teacher cosine
            l_rkd = ((s_n @ frame_n.T - Tland) ** 2).mean()
        else:
            # in_batch (v2 objective, verbatim) = the controlled baseline
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
        zc = student(Xd[cand_idx.reshape(-1).to(device)])
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
                f"failure_class=NAN_LOSS: {arch}/{kind} student loss non-finite "
                f"at step {step} (l_rkd={float(l_rkd.detach())}, "
                f"l_nce={float(l_nce.detach())})")
        opt.zero_grad()
        loss.backward()
        opt.step()
        v_loss = float(loss.detach())
        v_rkd = float(l_rkd.detach())
        v_nce = float(l_nce.detach())
        if loss_first is None:
            loss_first = v_loss
        loss_last = v_loss
        rkd_last = v_rkd
        nce_last = v_nce
        lr_last = cur_lr
        if step % 100 == 0:
            print(f"[step1b_v3] {arch}/{kind}/{objective} step {step}/{steps} "
                  f"rkd={v_rkd:.4f} nce={v_nce:.4f} "
                  f"lr={cur_lr:.2e} ({time.perf_counter() - t0:.1f}s)",
                  flush=True)
            _emit_heartbeat(output_dir, step, steps,
                            time.perf_counter() - t0,
                            extra={"phase": f"train_{arch}_{kind}_{objective}",
                                   "loss": v_loss, "rkd": v_rkd})
        # DENSE-spearman trajectory (mid validation): shows recovery vs steps
        if (dense_eval_fn is not None and dense_eval_every > 0
                and step % dense_eval_every == 0):
            d_sp = float(dense_eval_fn(student))
            dense_traj.append({"step": step, "dense_spearman": d_sp,
                               "rkd": v_rkd})
            print(f"[step1b_v3] {objective} DENSE-traj step {step}: "
                  f"dense_spearman={d_sp:.4f} rkd={v_rkd:.4f}", flush=True)
        if (step + 1) % ckpt_every == 0 or (step + 1) == steps:
            tmp = ckpt_path.with_suffix(".tmp")
            torch.save({"student": student.state_dict(),
                        "opt": opt.state_dict(),
                        "gen_state": gen.get_state(), "step": step + 1},
                       str(tmp))
            os.replace(str(tmp), str(ckpt_path))
    return student, {
        "loss_first": loss_first if loss_first is not None else -1.0,
        "loss_last": loss_last if loss_last is not None else -1.0,
        "rkd_last": rkd_last if rkd_last is not None else -1.0,
        "nce_last": nce_last if nce_last is not None else -1.0,
        "lr_last": lr_last if lr_last is not None else -1.0,
        "arch": arch, "objective": objective,
        "dense_traj": dense_traj,
    }


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
def _dense_sign_codes(student: torch.nn.Module, X: torch.Tensor,
                      batch: int = 8192) -> torch.Tensor:
    dev = _student_device(student)
    n_dim = student.out_dim
    out = torch.zeros(X.shape[0], n_dim, dtype=torch.float32)
    for lo in range(0, X.shape[0], batch):
        z = student(X[lo:lo + batch].to(dev))
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
    """Un-keyed superposition of J codes -> per-item top-J recall (DIAGNOSTIC).

    v2 FIX 1: this raw-bundle recall is a REPORTED diagnostic, NOT a pass/fail
    gate. Semantic-correlation degrades raw superposition for all trained codes;
    decorrelation-by-key (the keyed path) not sparsity protects composition.
    """
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
# Verdict logic (v2: FIX-1 dual-gate = semantic + KEYED; bundle = diagnostic).
# ---------------------------------------------------------------------------

def _by_unit(per_unit: List[Dict], kind: str, arm: str,
             J: Optional[int] = None) -> Optional[Dict]:
    for u in per_unit:
        if u["kind"] == kind and u["arm"] == arm and (J is None or u.get("J") == J):
            return u
    return None


def _verdict(per_unit: List[Dict], run_mode: str, expected_units: int,
             j_grid: List[int],
             capacity_preview: Optional[Dict] = None) -> Tuple[str, str]:
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
    # --- integrity controls (unchanged from v1; unaffected by FIX 1) ---------
    if posc["acc_at1"] < 0.98:
        return ("HARD_FAIL",
                f"HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH: RANDOM_BLOCK "
                f"keyed J=5 {posc['acc_at1']:.3f} < 0.98 (SBC lossless prior)")
    if shuf["acc_at1"] > 0.05 or shuf["hit_any_member"] > 0.10:
        return ("HARD_FAIL",
                f"HARD_FAIL_SHUFFLED_KEY_LEAK: wrong-key cleanup "
                f"{shuf['acc_at1']:.3f}/{shuf['hit_any_member']:.3f}")
    a_val = sem["spearman_all"]
    b1 = keyed5["acc_at1"]
    b5 = bun5["recall_at_J"]
    d5u = _by_unit(per_unit, "bundle", "DENSE_SIGN", 5)
    d5 = d5u["recall_at_J"] if d5u else float("nan")

    if run_mode == "full":
        # dual-gate B (KEYED, non-negotiable): false-win gate FIRST -- keyed
        # roundtrip < 0.90 rejects regardless of semantic A (FIX-1 algebra gate).
        if b1 < 0.90:
            return ("HARD_FAIL",
                    f"FALSE_WIN_ALGEBRA: keyed_roundtrip J=5 {b1:.3f} < 0.90 "
                    f"(semantic A={a_val:.3f} irrelevant per FIX-1)")
        g_a = "HP" if a_val >= 0.85 else ("MB" if a_val >= 0.70 else "HF")
        g_b1 = "HP" if b1 >= 0.95 else "MB"
        if g_a == "HF":
            return ("HARD_FAIL",
                    f"G_A_SEMANTIC_FAIL: spearman {a_val:.3f} < 0.70 "
                    f"(keyed algebra B={b1:.3f} ok)")
        if g_a == "HP" and g_b1 == "HP":
            return ("HARD_PASS",
                    f"DUAL_GATE_PASS: spearman={a_val:.3f} keyed@J5={b1:.3f} "
                    f"[bundle@J5 diag {b5:.3f} vs dense {d5:.3f}] "
                    f"shuffled_ok pos_ctrl_ok")
        return ("MIDDLE_BAND",
                f"MB: G_A={g_a}({a_val:.3f}) G_B_keyed={g_b1}({b1:.3f}) "
                f"[bundle diag {b5:.3f} vs dense {d5:.3f}]")

    # --- smoke bands ---------------------------------------------------------
    gap = sem["ret_agree10"] - sem_cp["ret_agree10"]
    fails = []
    if a_val < 0.40:
        fails.append(f"S_A spearman {a_val:.3f} < 0.40")
    if gap < 0.10:
        fails.append(f"S_gap ret_agree10 gap {gap:.3f} < 0.10 "
                     f"(discriminator-did-not-fire META_RULE_K)")
    if b1 < 0.95:
        fails.append(f"S_B_keyed keyed J=5 {b1:.3f} < 0.95")
    # v2 capacity-preview discriminator (option-C: MLP must beat linear geometry)
    cap_ok = True
    cap_msg = "n/a"
    if capacity_preview is not None:
        mlp_rkd = capacity_preview.get("mlp_rkd_last", float("nan"))
        lin_rkd = capacity_preview.get("linear_rkd_last", float("nan"))
        cap_ok = bool(capacity_preview.get("mlp_breaks_linear_rkd", False))
        cap_msg = (f"mlp_rkd={mlp_rkd:.4f} lin_rkd={lin_rkd:.4f} "
                   f"ratio={capacity_preview.get('rkd_ratio', float('nan')):.3f}")
        if not cap_ok:
            fails.append(
                f"S_capacity MLP geometry-loss did not beat LINEAR by "
                f">= {int((1 - CAPACITY_RKD_MAX_RATIO) * 100)}% ({cap_msg})")
    if fails:
        return ("SMOKE_GATE_FAIL", "; ".join(fails))
    verdict = "HARD_PASS" if a_val >= 0.60 else "MIDDLE_BAND"
    return (verdict,
            f"SMOKE_{verdict}: spearman={a_val:.3f} gap={gap:.3f} "
            f"keyed@J5={b1:.3f} [capacity_preview {cap_msg}] "
            f"[bundle@J5 diag {b5:.3f} vs dense {d5:.3f}; naive_keyed@J20 diag "
            f"{(naive20['acc_at1'] if naive20 else float('nan')):.3f}] "
            f"shuffled_ok pos_ctrl_ok")


# ---------------------------------------------------------------------------
# Experiment driver.
# ---------------------------------------------------------------------------

def run_experiment(run_mode: str, seed: int, device_arg: str,
                   n_dim: int, teacher_cache_arg: Optional[str],
                   objective: str = OBJECTIVE_DEFAULT,
                   cluster_frac: float = CLUSTER_FRAC_DEFAULT) -> int:
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
        n_landmarks, refresh_every = N_LANDMARKS_SMOKE, FRAME_REFRESH_SMOKE
    else:
        steps, batch = FULL_STEPS, FULL_BATCH
        j_grid, n_trials = FULL_J_GRID, FULL_TRIALS
        charpos_cap, pair_sample = FULL_CHARPOS_CAP, FULL_PAIR_SAMPLE
        k_blocks_list = list(K_BLOCKS_FULL_SWEEP)
        expected_units = EXPECTED_N_UNITS_FULL
        ckpt_every = CKPT_EVERY_STEPS_FULL
        n_landmarks, refresh_every = N_LANDMARKS_FULL, FRAME_REFRESH_FULL
    warmup = _warmup_for(steps)

    _write_start_marker(out_dir, run_mode, expected_units)
    t0 = time.perf_counter()
    print(f"[step1b_v3] run_mode={run_mode} seed={seed} device={device} "
          f"n_dim={n_dim} k_blocks={k_blocks_list} arch={STUDENT_ARCH_PRIMARY} "
          f"batch={batch} warmup={warmup}", flush=True)

    cache_path = _resolve_teacher_cache(teacher_cache_arg)
    cache_bytes = cache_path.stat().st_size
    print(f"[step1b_v3] teacher cache: {cache_path.name} "
          f"({cache_bytes / 1e6:.1f} MB)", flush=True)
    X, ids = _load_teacher(cache_path)
    V_cache = X.shape[0]
    print(f"[step1b_v3] teacher: {V_cache} concepts x {X.shape[1]}d "
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
    print(f"[step1b_v3] split train={n_tr} held={n_he}", flush=True)

    pos_idx, semi_cands = _mine_teacher(
        Xtr, device, art_dir / "_mine_shards", out_dir, t0)
    semi_cov = float((semi_cands[:, 0] >= 0).float().mean())
    print(f"[step1b_v3] mining done; semi-hard coverage={semi_cov:.3f} "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    # --- landmark/anchor frame (GLOBAL objective) ---------------------------
    land_idx = None
    if objective == "global":
        n_land = min(n_landmarks, n_tr)
        g_land = torch.Generator().manual_seed(seed + 101)
        land_idx = torch.randperm(n_tr, generator=g_land)[:n_land]
        print(f"[step1b_v3] objective=global landmarks={n_land} "
              f"refresh_every={refresh_every} cluster_frac={cluster_frac}",
              flush=True)
    else:
        print(f"[step1b_v3] objective=in_batch (v2 baseline; no landmarks)",
              flush=True)

    # --- train MLP students (block K-sweep) ---------------------------------
    Xall = torch.cat([Xtr, Xhe])
    he_lo = n_tr  # held rows start at offset n_tr inside Xall/codes_all
    arm_codes: Dict[str, torch.Tensor] = {}
    train_diag: Dict[str, Dict] = {}
    for kb in k_blocks_list:
        blk_l = n_dim // kb
        if kb * blk_l != n_dim:
            raise ValueError(f"n_dim {n_dim} not divisible by k_blocks {kb}")
        arm = f"BLOCK_K{kb}"
        student, diag = _train_student(
            "block", STUDENT_ARCH_PRIMARY, kb, blk_l, kb, Xtr, pos_idx,
            semi_cands, steps, batch, warmup, seed, device,
            art_dir / f"_ckpt_block_K{kb}.pt", ckpt_every, out_dir, t0,
            objective=objective, land_idx=land_idx, refresh_every=refresh_every,
            cluster_frac=cluster_frac)
        arm_codes[arm] = _encode_hard_block(student, Xall, kb, blk_l)
        train_diag[arm] = diag
        if kb == K_BLOCKS_PRIMARY:
            arm_codes["DENSE_SIGN"] = _dense_sign_codes(student, Xall)
        # artifact write (int8 codes + student state_dict for novel-concept path)
        codes_i8 = arm_codes[arm].to(torch.int8).numpy()
        meta = {
            "n_dim": n_dim, "k_blocks": kb, "block_len": blk_l,
            "sparsity": kb / n_dim, "seed": seed, "steps": steps,
            "student_arch": STUDENT_ARCH_PRIMARY, "mlp_hidden": MLP_HIDDEN,
            "teacher_cache": cache_path.name,
            "teacher_cache_bytes": cache_bytes,
            "objective": "RKD + 0.5*InfoNCE(semi-hard [0.3,0.6]) warmup+cosine",
            "batch": batch, "warmup": warmup,
            "composition_algebra": "SBC_block_local_circular_convolution",
            "cell": ANCHOR_NAME, "run_mode": run_mode,
            "ts_iso": datetime.now(timezone.utc).isoformat(),
        }
        tmp_npz = art_dir / f"encoder_distilled_K{kb}.tmp.npz"
        np.savez(str(tmp_npz), codes=codes_i8,
                 train_idx=tr_idx.astype(np.int64),
                 held_idx=he_idx.astype(np.int64),
                 ids_json=np.array(json.dumps(names_tr + names_he)),
                 metadata=np.array(json.dumps(meta)))
        os.replace(str(tmp_npz), str(art_dir / f"encoder_distilled_K{kb}.npz"))
        tmp_pt = art_dir / f"_student_K{kb}.pt.tmp"
        torch.save({"state_dict": student.state_dict(),
                    "arch": STUDENT_ARCH_PRIMARY, "in_dim": Xtr.shape[1],
                    "hidden": MLP_HIDDEN, "out_dim": kb * blk_l},
                   str(tmp_pt))
        os.replace(str(tmp_pt), str(art_dir / f"_student_K{kb}.pt"))
        print(f"[step1b_v3] {arm} ({STUDENT_ARCH_PRIMARY}) trained + artifact "
              f"written ({time.perf_counter() - t0:.1f}s)", flush=True)

    # TOPK naive comparison student (MLP arch matched; ONLY sparsifier differs)
    W_topk_student, diag_topk = _train_student(
        "topk", STUDENT_ARCH_PRIMARY, K_BLOCKS_PRIMARY,
        n_dim // K_BLOCKS_PRIMARY, K_BLOCKS_PRIMARY,
        Xtr, pos_idx, semi_cands, steps, batch, warmup, seed, device,
        art_dir / "_ckpt_topk.pt", ckpt_every, out_dir, t0,
        objective=objective, land_idx=land_idx, refresh_every=refresh_every,
        cluster_frac=cluster_frac)
    arm_codes["TOPK_NAIVE"] = _encode_hard_topk(
        W_topk_student, Xall, K_BLOCKS_PRIMARY)
    train_diag["TOPK_NAIVE"] = diag_topk

    gen_ctrl = torch.Generator().manual_seed(seed + 1)
    arm_codes["RANDOM_BLOCK"] = _random_block_codes(
        Xall.shape[0], K_BLOCKS_PRIMARY, n_dim // K_BLOCKS_PRIMARY, gen_ctrl)

    # CHARPOS on capped subset (declared in prereg)
    n_cp_he = min(n_he, charpos_cap * 2 // 5)
    n_cp_tr = min(n_tr, charpos_cap - n_cp_he)
    cp_codes = _charpos_codes(names_tr[:n_cp_tr] + names_he[:n_cp_he],
                              n_dim, K_BLOCKS_PRIMARY)
    print(f"[step1b_v3] control arms built ({time.perf_counter() - t0:.1f}s)",
          flush=True)

    # --- v2 capacity-preview: LINEAR ref student on MATCHED smoke data --------
    capacity_preview: Optional[Dict] = None
    if run_mode == "smoke":
        lin_student, lin_diag = _train_student(
            "block", "linear", K_BLOCKS_PRIMARY, n_dim // K_BLOCKS_PRIMARY,
            K_BLOCKS_PRIMARY, Xtr, pos_idx, semi_cands, steps, batch, warmup,
            seed, device, art_dir / "_ckpt_linref.pt", ckpt_every, out_dir, t0,
            objective=objective, land_idx=land_idx, refresh_every=refresh_every,
            cluster_frac=cluster_frac)
        lin_codes = _encode_hard_block(
            lin_student, Xall, K_BLOCKS_PRIMARY, n_dim // K_BLOCKS_PRIMARY)
        lin_sem = _semantic_unit("LINEAR_REF", lin_codes[he_lo:], lin_codes,
                                 Xhe, Xall, he_lo, pair_sample, seed + 3)
        mlp_rkd = float(train_diag["BLOCK_K128"]["rkd_last"])
        lin_rkd = float(lin_diag["rkd_last"])
        ratio = mlp_rkd / lin_rkd if lin_rkd > 0 else float("nan")
        capacity_preview = {
            "mlp_rkd_last": mlp_rkd,
            "linear_rkd_last": lin_rkd,
            "rkd_ratio": ratio,
            "rkd_max_ratio_gate": CAPACITY_RKD_MAX_RATIO,
            "mlp_breaks_linear_rkd": bool(
                math.isfinite(ratio) and ratio <= CAPACITY_RKD_MAX_RATIO),
            "mlp_spearman_smoke": None,   # filled after primary semantic unit
            "linear_spearman_smoke": lin_sem["spearman_all"],
            "linear_ret_agree10": lin_sem["ret_agree10"],
            "note": ("smoke 3000-subset is easy so linear also scores high on "
                     "spearman; the geometry-loss (rkd) gap is the capacity "
                     "discriminator that survives to full 178K scale. The "
                     "0.64->0.85 semantic break itself is a FULL-GPU question."),
        }
        print(f"[step1b_v3] capacity_preview mlp_rkd={mlp_rkd:.4f} "
              f"lin_rkd={lin_rkd:.4f} ratio={ratio:.3f} "
              f"breaks={capacity_preview['mlp_breaks_linear_rkd']} "
              f"lin_spearman={lin_sem['spearman_all']:.4f}", flush=True)

    # --- META_RULE_AF arms-must-differ --------------------------------------
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

    # --- eval units ----------------------------------------------------------
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
            print(f"[step1b_v3] unit {len(per_unit)}/{total_planned} "
                  f"{u['unit']}: "
                  + json.dumps({k: round(v, 4) for k, v in u.items()
                                if isinstance(v, float)}), flush=True)
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append({"fn": getattr(fn, "__name__", "?"),
                              "failure_class": type(exc).__name__,
                              "msg": str(exc)[:300]})
            raise  # FAIL_LOUD; no silent continue (META_RULE_J)

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

    # backfill primary spearman into capacity_preview for the report
    sem_prim = _by_unit(per_unit, "semantic", "BLOCK_K128") or {}
    if capacity_preview is not None:
        capacity_preview["mlp_spearman_smoke"] = sem_prim.get("spearman_all")

    # --- verdict -------------------------------------------------------------
    verdict, verdict_msg = _verdict(per_unit, run_mode, expected_units, j_grid,
                                    capacity_preview=capacity_preview)
    elapsed = time.perf_counter() - t0
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
        "student_arch": STUDENT_ARCH_PRIMARY,
        "mlp_hidden": MLP_HIDDEN,
        "warmup_steps": warmup,
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
        "capacity_preview": capacity_preview,
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
        "dual_gate": "semantic_spearman + keyed_roundtrip (bundle=diagnostic)",
        "progress_logging": "print_flush_true",
        "primary_spearman": sem_prim.get("spearman_all"),
        "objective": objective,
        "n_landmarks": (int(land_idx.numel()) if land_idx is not None else 0),
        "refresh_every": refresh_every,
        "cluster_frac": cluster_frac,
        "dense_sign_spearman": (_by_unit(per_unit, "semantic", "DENSE_SIGN") or
                                {}).get("spearman_all"),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[step1b_v3] verdict={verdict} msg={verdict_msg} "
          f"elapsed={elapsed:.1f}s", flush=True)
    return 0


# ---------------------------------------------------------------------------
# Intermediate-scale (mid) validation: the diagnosis-mandated recovery gate.
# ---------------------------------------------------------------------------

@torch.no_grad()
def _dense_spearman_quick(student: torch.nn.Module, Xhe_sub: torch.Tensor,
                          n_pairs: int, seed: int) -> float:
    """Fast DENSE_SIGN spearman on a held subset (trajectory logging)."""
    codes = _dense_sign_codes(student, Xhe_sub)
    cn = codes / (codes.norm(dim=-1, keepdim=True) + 1e-8)
    n = Xhe_sub.shape[0]
    rng = np.random.default_rng(seed)
    i = torch.from_numpy(rng.integers(0, n, n_pairs))
    j = torch.from_numpy(rng.integers(0, n, n_pairs))
    keep = i != j
    i, j = i[keep], j[keep]
    tp = (Xhe_sub[i] * Xhe_sub[j]).sum(-1).numpy()
    sp = (cn[i] * cn[j]).sum(-1).numpy()
    return _spearman(sp, tp)


def _verdict_mid(per_unit: List[Dict], recovery: Dict,
                 expected_units: int) -> Tuple[str, str]:
    """Recovery discriminator on the DENSE readout (diagnosis-mandated gate).

    Bands (HYPOTHESIZED@prereg): the global objective RECOVERS if DENSE spearman
    reaches ~0.75+ (near the 3k-scale 0.825 and the 0.80 target) AND clearly beats
    the matched in-batch baseline (delta >= 0.15). Current in-batch gives DENSE
    ~0.37-0.64 at this scale (diagnosis MEASURED).
    """
    if len(per_unit) < expected_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"{len(per_unit)}/{expected_units} units")
    posc = _by_unit(per_unit, "keyed", "RANDOM_BLOCK", 5)
    shuf = _by_unit(per_unit, "shuffled_key", "GLOBAL_BLOCK_K128", 5)
    if posc is None or shuf is None:
        return ("HARD_FAIL", "HARD_FAIL_MISSING_GATE_UNITS")
    # integrity controls (algebra untouched by the objective; must hold)
    if posc["acc_at1"] < 0.98:
        return ("HARD_FAIL",
                f"HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH: RANDOM_BLOCK keyed "
                f"J=5 {posc['acc_at1']:.3f} < 0.98 (SBC lossless prior)")
    if shuf["acc_at1"] > 0.05 or shuf["hit_any_member"] > 0.10:
        return ("HARD_FAIL",
                f"HARD_FAIL_SHUFFLED_KEY_LEAK: {shuf['acc_at1']:.3f}")
    gd = recovery["global_dense_spearman"]
    ibd = recovery["inbatch_dense_spearman"]
    delta = recovery["recovery_delta_dense"]
    gb = recovery["global_block_spearman"]
    ibb = recovery["inbatch_block_spearman"]
    tail = (f"[global DENSE={gd:.4f} inbatch DENSE={ibd:.4f} delta={delta:.4f} "
            f"| global BLOCK={gb:.4f} inbatch BLOCK={ibb:.4f}]")
    if gd >= 0.75 and delta >= 0.15:
        return ("HARD_PASS", f"MID_RECOVERED: global objective recovers DENSE "
                             f"geometry at intermediate scale {tail}")
    if gd >= 0.64 and delta >= 0.05:
        return ("MIDDLE_BAND", f"MID_PARTIAL: DENSE improved but short of ~0.80 "
                              f"target {tail}")
    return ("HARD_FAIL", f"MID_NOT_RECOVERED: global objective did NOT recover "
                        f"DENSE at scale; do NOT proceed to FULL {tail}")


def run_midscale(seed: int, device_arg: str, n_dim: int,
                 teacher_cache_arg: Optional[str],
                 cluster_frac: float = CLUSTER_FRAC_DEFAULT) -> int:
    """Train GLOBAL + IN_BATCH_REF at ~40k concepts (local CPU); report the
    DENSE-recovery discriminator. This is the R1 validation gate BEFORE any FULL.
    """
    run_mode = "mid"
    anchor = f"{ANCHOR_NAME}_mid"
    out_dir = get_output_dir(anchor)
    art_dir = _artifact_dir(run_mode)
    art_dir.mkdir(parents=True, exist_ok=True)
    device = ("cuda" if torch.cuda.is_available() else "cpu") \
        if device_arg == "auto" else device_arg
    expected_units = EXPECTED_N_UNITS_MID
    steps, batch = MID_STEPS, MID_BATCH
    warmup = _warmup_for(steps)
    kb, blk_l = K_BLOCKS_PRIMARY, n_dim // K_BLOCKS_PRIMARY
    _write_start_marker(out_dir, run_mode, expected_units)
    t0 = time.perf_counter()
    print(f"[step1b_v3] MID run seed={seed} device={device} n_dim={n_dim} "
          f"steps={steps} batch={batch} cluster_frac={cluster_frac}", flush=True)

    cache_path = _resolve_teacher_cache(teacher_cache_arg)
    cache_bytes = cache_path.stat().st_size
    X, ids = _load_teacher(cache_path)
    V_cache = X.shape[0]
    print(f"[step1b_v3] MID teacher {cache_path.name}: {V_cache} concepts x "
          f"{X.shape[1]}d ({time.perf_counter() - t0:.1f}s)", flush=True)

    rng = np.random.default_rng(seed)
    perm = rng.permutation(V_cache)
    n_he = min(int(round(V_cache * HELD_FRAC)), MID_HELD_CAP)
    n_tr = V_cache - n_he
    tr_idx = perm[:n_tr]
    he_idx = perm[n_tr:n_tr + n_he]
    Xtr = X[torch.from_numpy(tr_idx.copy())].contiguous()
    Xhe = X[torch.from_numpy(he_idx.copy())].contiguous()
    names_he = [ids[i] for i in he_idx]
    print(f"[step1b_v3] MID split train={n_tr} held={n_he}", flush=True)

    pos_idx, semi_cands = _mine_teacher(
        Xtr, device, art_dir / "_mine_shards", out_dir, t0)
    semi_cov = float((semi_cands[:, 0] >= 0).float().mean())
    n_land = min(N_LANDMARKS_MID, n_tr)
    g_land = torch.Generator().manual_seed(seed + 101)
    land_idx = torch.randperm(n_tr, generator=g_land)[:n_land]
    print(f"[step1b_v3] MID mining done cov={semi_cov:.3f} landmarks={n_land} "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    # DENSE-trajectory eval closure (fast held-subset spearman)
    Xhe_sub = Xhe[:min(1500, n_he)].contiguous()

    def _deval(student: torch.nn.Module) -> float:
        return _dense_spearman_quick(student, Xhe_sub, 60_000, seed + 7)

    # --- train the two objectives at MATCHED config -------------------------
    students: Dict[str, torch.nn.Module] = {}
    train_diag: Dict[str, Dict] = {}
    for obj in ("global", "in_batch"):
        li = land_idx if obj == "global" else None
        st, diag = _train_student(
            "block", STUDENT_ARCH_PRIMARY, kb, blk_l, kb, Xtr, pos_idx,
            semi_cands, steps, batch, warmup, seed, device,
            art_dir / f"_ckpt_block_{obj}.pt", CKPT_EVERY_STEPS_MID, out_dir, t0,
            objective=obj, land_idx=li, refresh_every=FRAME_REFRESH_MID,
            cluster_frac=cluster_frac, dense_eval_fn=_deval,
            dense_eval_every=MID_DENSE_EVAL_EVERY)
        students[obj] = st
        train_diag[obj] = diag
        print(f"[step1b_v3] MID {obj} trained rkd_last={diag['rkd_last']:.4f} "
              f"({time.perf_counter() - t0:.1f}s)", flush=True)

    # --- encode held codes per arm (semantic eval within held set) ----------
    arm_codes: Dict[str, torch.Tensor] = {
        "GLOBAL_BLOCK_K128": _encode_hard_block(students["global"], Xhe, kb, blk_l),
        "GLOBAL_DENSE": _dense_sign_codes(students["global"], Xhe),
        "INBATCH_BLOCK_K128": _encode_hard_block(students["in_batch"], Xhe, kb, blk_l),
        "INBATCH_DENSE": _dense_sign_codes(students["in_batch"], Xhe),
    }
    gen_ctrl = torch.Generator().manual_seed(seed + 1)
    arm_codes["RANDOM_BLOCK"] = _random_block_codes(n_he, kb, blk_l, gen_ctrl)
    cp_cap = min(n_he, MID_CHARPOS_CAP)
    cp_codes = _charpos_codes(names_he[:cp_cap], n_dim, kb)

    # META_RULE_AF arms-differ
    digests = {}
    for name, c in list(arm_codes.items()) + [("CHARPOS", cp_codes)]:
        digests[name] = hashlib.sha256(
            c.to(torch.int8).numpy().tobytes()).hexdigest()
    for a in digests:
        for b in digests:
            if a < b and digests[a] == digests[b]:
                raise RuntimeError(
                    f"failure_class=META_RULE_AF_VIOLATION: {a}/{b} identical")

    # --- eval units ---------------------------------------------------------
    per_unit: List[Dict] = []
    unit_fail: List[Dict] = []
    gen_eval = torch.Generator().manual_seed(seed + 2)

    def _run_unit(fn, *a, **kw):
        try:
            u = fn(*a, **kw)
            per_unit.append(u)
            print(f"[step1b_v3] MID unit {len(per_unit)}/{expected_units} "
                  f"{u['unit']}: "
                  + json.dumps({k: round(v, 4) for k, v in u.items()
                                if isinstance(v, float)}), flush=True)
            _emit_heartbeat(out_dir, len(per_unit), expected_units,
                            time.perf_counter() - t0, extra={"unit": u["unit"]})
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append({"fn": getattr(fn, "__name__", "?"),
                              "failure_class": type(exc).__name__,
                              "msg": str(exc)[:300]})
            raise

    for arm in ["GLOBAL_BLOCK_K128", "GLOBAL_DENSE", "INBATCH_BLOCK_K128",
                "INBATCH_DENSE", "RANDOM_BLOCK"]:
        c = arm_codes[arm]
        _run_unit(_semantic_unit, arm, c, c, Xhe, Xhe, 0,
                  MID_PAIR_SAMPLE, seed + 3)
    cp_Xhe = Xhe[:cp_cap]
    _run_unit(_semantic_unit, "CHARPOS", cp_codes, cp_codes, cp_Xhe, cp_Xhe, 0,
              MID_PAIR_SAMPLE, seed + 3)
    # algebra sanity + integrity controls (objective does not touch SBC path)
    _run_unit(_keyed_unit, "GLOBAL_BLOCK_K128", "sbc",
              arm_codes["GLOBAL_BLOCK_K128"], kb, blk_l, 5, MID_TRIALS,
              gen_eval, device)
    _run_unit(_keyed_unit, "RANDOM_BLOCK", "sbc", arm_codes["RANDOM_BLOCK"],
              kb, blk_l, 5, MID_TRIALS, gen_eval, device)
    _run_unit(_keyed_unit, "GLOBAL_BLOCK_K128", "sbc",
              arm_codes["GLOBAL_BLOCK_K128"], kb, blk_l, 5, MID_TRIALS,
              gen_eval, device, shuffled_key=True)

    # --- recovery discriminator (the load-bearing result) -------------------
    def _sp(arm):
        u = _by_unit(per_unit, "semantic", arm)
        return float(u["spearman_all"]) if u else float("nan")
    recovery = {
        "global_dense_spearman": _sp("GLOBAL_DENSE"),
        "inbatch_dense_spearman": _sp("INBATCH_DENSE"),
        "global_block_spearman": _sp("GLOBAL_BLOCK_K128"),
        "inbatch_block_spearman": _sp("INBATCH_BLOCK_K128"),
        "charpos_spearman": _sp("CHARPOS"),
        "random_block_spearman": _sp("RANDOM_BLOCK"),
        "recovery_delta_dense": _sp("GLOBAL_DENSE") - _sp("INBATCH_DENSE"),
        "recovery_delta_block": _sp("GLOBAL_BLOCK_K128") - _sp("INBATCH_BLOCK_K128"),
        "global_rkd_last": float(train_diag["global"]["rkd_last"]),
        "inbatch_rkd_last": float(train_diag["in_batch"]["rkd_last"]),
        "global_dense_traj": train_diag["global"]["dense_traj"],
        "inbatch_dense_traj": train_diag["in_batch"]["dense_traj"],
    }
    verdict, verdict_msg = _verdict_mid(per_unit, recovery, expected_units)
    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "seed": int(seed), "device": device, "N": n_dim,
        "student_arch": STUDENT_ARCH_PRIMARY, "mlp_hidden": MLP_HIDDEN,
        "warmup_steps": warmup, "steps": steps, "batch": batch,
        "n_landmarks": n_land, "refresh_every": FRAME_REFRESH_MID,
        "cluster_frac": cluster_frac,
        "teacher_cache": cache_path.name, "teacher_cache_bytes": cache_bytes,
        "teacher_n_concepts": V_cache, "n_train": n_tr, "n_held": n_he,
        "semi_hard_coverage": semi_cov,
        "recovery": recovery, "train_diag": train_diag,
        "per_unit": per_unit, "unit_failures": unit_fail,
        "n_units": len(per_unit), "expected_n_units": expected_units,
        "cardinality_ok": len(per_unit) == expected_units,
        "arms_differ_verified": True, "arm_code_sha256": digests,
        "final_metrics_atomicity": "tmp_replace",
        "composition_algebra": "SBC_block_local_circular_convolution",
        "objective": "global+in_batch (matched-config recovery discriminator)",
        "progress_logging": "print_flush_true",
        "primary_spearman": recovery["global_dense_spearman"],
        "dense_sign_spearman": recovery["global_dense_spearman"],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[step1b_v3] MID verdict={verdict} msg={verdict_msg} "
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
    # LR schedule: warmup ramps up then cosine decays to ~0
    total, warm = 1000, 100
    assert _lr_at(0, total, warm, 1e-3) < _lr_at(warm - 1, total, warm, 1e-3), \
        "selftest: warmup not ramping"
    assert abs(_lr_at(warm - 1, total, warm, 1e-3) - 1e-3) < 1e-6, \
        "selftest: lr not at base at warmup end"
    assert _lr_at(total - 1, total, warm, 1e-3) < 1e-4, \
        "selftest: cosine did not decay to near zero"
    # block STE through a LINEAR student: exact 1-per-block sparsity + gradient
    lin = _make_student("linear", 64, n_dim, "cpu", 11)
    z = lin(X[:32])
    s = _block_ste(z, kb, blk_l)
    nnz = (s != 0).sum(dim=-1)
    assert bool((nnz == kb).all()), f"selftest: block nnz {nnz.unique()} != {kb}"
    per_block = (s.reshape(32, kb, blk_l) != 0).sum(-1)
    assert bool((per_block == 1).all()), "selftest: not 1-active-per-block"
    loss = (s ** 2).mean()
    loss.backward()
    glin = lin.net.weight.grad
    assert glin is not None and bool(torch.isfinite(glin).all()) and \
        float(glin.abs().sum()) > 0, "selftest: linear STE gradient dead"
    # block STE through an MLP student: gradient flows to BOTH layers
    mlp = _make_student("mlp", 64, n_dim, "cpu", 11)
    zm = mlp(X[:32])
    sm = _block_ste(zm, kb, blk_l)
    per_block_m = (sm.reshape(32, kb, blk_l) != 0).sum(-1)
    assert bool((per_block_m == 1).all()), "selftest: MLP not 1-active-per-block"
    (sm ** 2).mean().backward()
    g_in = mlp.net[0].weight.grad
    g_out = mlp.net[2].weight.grad
    for gname, g in [("mlp_in", g_in), ("mlp_out", g_out)]:
        assert g is not None and bool(torch.isfinite(g).all()) and \
            float(g.abs().sum()) > 0, f"selftest: MLP STE gradient dead at {gname}"
    # hard encode via student matches sparsity + int8-safe ternary values
    codes = _encode_hard_block(mlp, X, kb, blk_l)
    assert bool(((codes == 0) | (codes == 1) | (codes == -1)).all()), \
        "selftest: non-ternary code"
    assert int(codes.shape[1]) == n_dim, "selftest: encode wrong out dim"
    # v3 GLOBAL LANDMARK RKD: frame encode + global-RKD loss + gradient flow
    mlp2 = _make_student("mlp", 64, n_dim, "cpu", 13)
    land = torch.randint(0, v, (48,), generator=gen)
    Xland = X[land]
    frame_n = _frame_codes_norm(mlp2, Xland, "block", kb, blk_l, kb)
    assert frame_n.shape == (48, n_dim), "selftest: frame wrong shape"
    assert not frame_n.requires_grad, "selftest: frame not detached"
    per_block_f = (frame_n.reshape(48, kb, blk_l) != 0).sum(-1)
    assert bool((per_block_f == 1).all()), "selftest: frame not 1-per-block"
    xb = X[:24]
    zb2 = mlp2(xb)
    sb2 = _block_ste(zb2, kb, blk_l)
    sb2_n = sb2 / (sb2.norm(dim=-1, keepdim=True) + 1e-8)
    Tland = xb @ Xland.T
    l_glob = ((sb2_n @ frame_n.T - Tland) ** 2).mean()
    assert torch.isfinite(l_glob), "selftest: global RKD loss non-finite"
    l_glob.backward()
    assert mlp2.net[0].weight.grad is not None and \
        float(mlp2.net[0].weight.grad.abs().sum()) > 0, \
        "selftest: global RKD gradient dead"
    # cluster-batch builder: correct size, valid range, both frac 0 and 0.5
    posc_i = torch.randint(0, v, (v,), generator=gen)
    semic_i = torch.randint(0, v, (v, N_SEMI_CANDS), generator=gen)
    for cf in (0.0, 0.5):
        bi = _cluster_batch_idx(64, cf, v, posc_i, semic_i, gen)
        assert bi.numel() == 64, f"selftest: cluster batch size {bi.numel()}"
        assert int(bi.min()) >= 0 and int(bi.max()) < v, \
            "selftest: cluster batch idx OOR"
    # _train_student runs end-to-end for BOTH objectives (few steps, tmp ckpt)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        st_g, dg = _train_student(
            "block", "mlp", kb, blk_l, kb, X, posc_i, semic_i, 6, 16, 2, 11,
            "cpu", tdp / "ckpt_g.pt", 100, tdp, t0, objective="global",
            land_idx=land, refresh_every=2, cluster_frac=0.0)
        assert math.isfinite(dg["rkd_last"]) and dg["rkd_last"] >= 0, \
            "selftest: global train rkd bad"
        st_b, db = _train_student(
            "block", "mlp", kb, blk_l, kb, X, posc_i, semic_i, 6, 16, 2, 11,
            "cpu", tdp / "ckpt_b.pt", 100, tdp, t0, objective="in_batch")
        assert math.isfinite(db["rkd_last"]), "selftest: in_batch train rkd bad"
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
    print(f"[selftest] PASS (LR-sched + linear/MLP block-STE grads + GLOBAL "
          f"landmark-RKD grad + cluster-batch + both-objective train + SBC "
          f"roundtrip {u['acc_at1']:.2f} + shuffled {us['acc_at1']:.2f} + "
          f"fhrr {uf['acc_at1']:.2f}) elapsed={time.perf_counter() - t0:.2f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Entry.
# ---------------------------------------------------------------------------

def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=(
        "Encoder Migration Step 1b v3 -- GLOBAL (landmark) RKD objective; "
        "R1 rescue for the full-scale HARD_FAIL. mid = the recovery validation."))
    p.add_argument("--run-mode",
                   default=os.environ.get("HDLAB_RUN_MODE", "self_test"),
                   choices=["self_test", "smoke", "mid", "full"])
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--mid", action="store_true")
    p.add_argument("--full", action="store_true")
    p.add_argument("--seed", type=int, default=SEED_DEFAULT)
    p.add_argument("--device", default="auto",
                   choices=["auto", "cpu", "cuda"])
    p.add_argument("--n-dim", type=int, default=N_DIM_DEFAULT)
    p.add_argument("--objective", default=OBJECTIVE_DEFAULT,
                   choices=["global", "in_batch"],
                   help="RKD target for smoke/full (mid runs BOTH by design)")
    p.add_argument("--cluster-frac", type=float, default=CLUSTER_FRAC_DEFAULT,
                   help="fraction of each batch built as semi-hard clusters")
    p.add_argument("--teacher-cache", default=None,
                   help="explicit teacher npz path (default: largest match)")
    args, _ = p.parse_known_args(argv)
    if args.self_test:
        args.run_mode = "self_test"
    elif args.smoke:
        args.run_mode = "smoke"
    elif args.mid:
        args.run_mode = "mid"
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
    if args.run_mode == "mid":
        return run_midscale(args.seed, args.device, args.n_dim,
                            args.teacher_cache, cluster_frac=args.cluster_frac)
    return run_experiment(args.run_mode, args.seed, args.device,
                          args.n_dim, args.teacher_cache,
                          objective=args.objective,
                          cluster_frac=args.cluster_frac)


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
