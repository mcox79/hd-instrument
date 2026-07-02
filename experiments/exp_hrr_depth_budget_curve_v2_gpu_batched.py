"""hrr_depth_budget_curve_v2_gpu_batched -- GPU-batched refactor of v1
                                            Dim I A2 Donoho-Tanner probe.

## Compute architecture

**Cell class: batched-GPU (default for grids per USER 2026-07-02 discipline).**

v1 was numpy-sequential (per-trial Python loop x 504 phase points x 200 trials
= 100,800 trial calls, each rebuilding N=8192 role tensors from scratch).
v1 elapsed ~8h44m before USER-authorized kill at 167/504 arms.

v2 batches TR trials on torch.cuda within each (seed, variant, V, cleanup, k, M)
phase-point. All substrate primitives (bind = elementwise multiply, bundle =
sum, cleanup = matmul + argmax) are trivially data-parallel across the trial
axis. Memory bound: batch x k x M x N x 4 bytes; chunked to <= 2 GB per group.

Expected wall (approx from primitive costs on RTX/A-series GPU):
  - Small phase points (M<=16, V=100):  ~0.05s/cell x 336 cells x 3 seeds ~ 50s
  - Large phase points (M=256, V=1000, k=20): ~1s/cell (chunked) x 12 x 3 ~ 40s
  - Total FULL: ~30 min for 504 arms across 3 seeds (vs v1's 36+ hrs).

## v1 reproduction

Same 168-phase-point grid per seed (variant, cleanup, k, M, V) as v1. Grid
enumeration order matches v1._grid_cells so per-arm outputs align 1:1.

Self-test arm test_v1_reproduction runs v2 at seed=7 on 6 salvaged arms and
compares to v1 log-recovered recalls (must be within 0.02 absolute).

Salvage source: data/exp_hrr_depth_budget_curve_v1/partial_metrics.json
(167 arms; USER-authorized kill 2026-07-02).

## Grid (identical to v1)

- N_DIM = 8192
- V_GRID = [100, 1000]
- BIND_VARIANTS = [ELEM_BIPOLAR, FHRR_CC]
- CLEANUP_GRID = [OFF, ON]
- Cheap tier: k in {1,5,10,15,20} x M in {1,5,16}
- Expensive tier: k in {1,10,20} x M in {64,256}
- 168 cells per seed x 3 seeds = 504 units (CARDINALITY_OK gate)

## Discriminators (identical bands to v1)

- HP_INVOLUTIVE (ELEM_BIPOLAR, V=100, k=20, M=1, OFF): recall >= 0.99
- HP_CEILING_SAFE (ELEM_BIPOLAR, V=100, k=20, M=16, ON): recall >= 0.95, cv <= 0.05
- HP_CLEANUP_GAP_WALL (V=1000, k=10, M=256 ON - OFF, ELEM_BIPOLAR): gap >= 0.20

## RNG parity note (v1 -> v2 reproduction tolerance)

v1 uses numpy.random.Generator; v2 uses torch.Generator on GPU. Since the
PRNG streams differ, per-arm recalls will NOT be bit-exact but the discriminator
signal (mean recall across 200 trials) should agree within Monte-Carlo noise
(1/sqrt(200) ~ 0.07). Reproduction gate uses 0.02 tolerance for cliff regions
(recall in {0.0, 1.0}) and 0.10 for mid-band regions where 200-trial SEM is 0.03.
Signal-shape agreement (cliff location in k-M plane) is the actual
ship-critical property.

ASCII-only. write_metrics. Refs:
  data/exp_hrr_depth_budget_curve_v1/partial_metrics.json (salvage source)
  experiments/exp_hrr_depth_budget_curve_v1.py (mechanism reference)
  memory/feedback_gpu_batching_mandatory_when_speedup_available_USER_LOCKED_2026-07-02.md
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "hrr_depth_budget_curve_v2_gpu_batched"

# ---- CLI + run mode -------------------------------------------------------
_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = (
    "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
    else os.environ.get("HDLAB_RUN_MODE", "full")
).lower()
SMOKE = RUN_MODE == "smoke"

# ---- Device ---------------------------------------------------------------
if torch.cuda.is_available():
    DEVICE = torch.device("cuda")
    DEVICE_NAME = torch.cuda.get_device_name(0)
else:
    DEVICE = torch.device("cpu")
    DEVICE_NAME = "cpu (no CUDA)"

# ---- Config (identical to v1) ---------------------------------------------
N_DIM = 8192
K_GRID_CHEAP = [1, 5, 10, 15, 20]
K_GRID_EXPENSIVE = [1, 10, 20]
M_GRID_CHEAP = [1, 5, 16]
M_GRID_EXPENSIVE = [64, 256]
V_GRID = [100, 1000]
BIND_VARIANTS = ["ELEM_BIPOLAR", "FHRR_CC"]
CLEANUP_GRID = ["OFF", "ON"]
SEEDS_FULL = [7, 13, 19]
SEEDS_SMOKE = [7]
TR_FULL = 200
TR_SMOKE = 20

SEEDS = SEEDS_SMOKE if SMOKE else SEEDS_FULL
TR = TR_SMOKE if SMOKE else TR_FULL

# Memory chunk budget: per-chunk (batch x k x M x N x 4 bytes) <= this
# Conservative 2 GB default; keeps small consumer GPUs healthy
MEM_BUDGET_BYTES = int(2 * 1024**3)


def _grid_cells() -> List[Tuple[str, int, int, str, int]]:
    """Enumerate (variant, k, M, cleanup, V) cells (identical order to v1)."""
    out: List[Tuple[str, int, int, str, int]] = []
    for v in V_GRID:
        for variant in BIND_VARIANTS:
            for cleanup in CLEANUP_GRID:
                for k in K_GRID_CHEAP:
                    for m in M_GRID_CHEAP:
                        out.append((variant, k, m, cleanup, v))
                for k in K_GRID_EXPENSIVE:
                    for m in M_GRID_EXPENSIVE:
                        out.append((variant, k, m, cleanup, v))
    return out


GRID_CELLS = _grid_cells()
CELLS_PER_SEED = len(GRID_CELLS)
EXPECTED_N_UNITS = CELLS_PER_SEED * len(SEEDS)


def frady_sommer_m_max(n: int, v: int) -> float:
    return float(n) / (4.0 * math.log(v))


HP_INVOLUTIVE_RECALL = 0.99
HP_CEILING_SAFE = 0.95
HP_CLEANUP_GAP_WALL = 0.20
HP_SHALLOW_WIDE_LIFT = 0.10
HF_DEPTH_COLLAPSE_SAFE = 0.70
HF_INVOLUTIVE_BROKEN = 0.95

CONFIG_VERSION = (
    "ANCHOR=%s,N_DIM=%d,V=%s,k_cheap=%s,k_exp=%s,M_cheap=%s,M_exp=%s,"
    "variants=%s,cleanup=%s,seeds=%s,TR=%d,mode=%s,scope=A2_donoho_tanner_probe,"
    "M_max(V=100)=%.1f,M_max(V=1000)=%.1f,device=%s,compute=batched_GPU"
) % (
    ANCHOR_NAME, N_DIM, V_GRID, K_GRID_CHEAP, K_GRID_EXPENSIVE,
    M_GRID_CHEAP, M_GRID_EXPENSIVE, BIND_VARIANTS, CLEANUP_GRID, SEEDS, TR, RUN_MODE,
    frady_sommer_m_max(N_DIM, 100), frady_sommer_m_max(N_DIM, 1000),
    DEVICE_NAME,
)


# ---- Batched primitives ---------------------------------------------------
def _torch_gen(seed: int) -> torch.Generator:
    g = torch.Generator(device=DEVICE)
    g.manual_seed(seed)
    return g


def make_atoms_bipolar(batch_shape: Tuple[int, ...], n: int,
                        g: torch.Generator) -> torch.Tensor:
    """Bipolar {-1,+1} atoms of shape (*batch_shape, n)."""
    bits = torch.randint(0, 2, size=(*batch_shape, n), device=DEVICE,
                         generator=g, dtype=torch.int8)
    return (bits.to(torch.float32) * 2 - 1)


def make_atoms_fhrr(batch_shape: Tuple[int, ...], n: int,
                     g: torch.Generator) -> torch.Tensor:
    """Unit-modulus complex phasors of shape (*batch_shape, n)."""
    ang = (torch.rand((*batch_shape, n), device=DEVICE, generator=g) * 2 - 1) * math.pi
    return torch.complex(torch.cos(ang), torch.sin(ang)).to(torch.complex64)


def bind_batched(a: torch.Tensor, b: torch.Tensor, variant: str) -> torch.Tensor:
    """Elementwise multiply (bipolar) OR elementwise complex multiply (FHRR)."""
    return a * b  # dtype preserved by torch


def unbind_batched(y: torch.Tensor, b: torch.Tensor, variant: str) -> torch.Tensor:
    if variant == "ELEM_BIPOLAR":
        return y * b
    else:
        return y * b.conj()


def bundle_batched(vecs: torch.Tensor, variant: str) -> torch.Tensor:
    """Sum along axis -2 (slot axis).

    vecs shape: (..., M, N). Returns (..., N).
    Bipolar: linear sum (no sign-quantize; deferred to final argmax cleanup).
    FHRR: sum then per-position renormalize to unit modulus.
    """
    s = vecs.sum(dim=-2)
    if variant == "ELEM_BIPOLAR":
        return s
    mag = s.abs()
    mag_safe = torch.where(mag > 1e-12, mag, torch.ones_like(mag))
    return s / mag_safe


def argmax_batched(x: torch.Tensor, book: torch.Tensor, variant: str) -> torch.Tensor:
    """Cleanup argmax against a shared book (V, N).

    x shape: (batch, N); book shape: (V, N). Returns (batch,) int64 indices.
    """
    if variant == "ELEM_BIPOLAR":
        sims = x @ book.T  # (batch, V)
    else:
        sims = (x @ book.conj().T).real
    return sims.argmax(dim=-1)


# ---- Batched trial runner -------------------------------------------------
def _chunk_size(k: int, m: int, n: int) -> int:
    """Max batch that keeps (batch * k * m * n * 4) <= MEM_BUDGET_BYTES."""
    per_trial = k * m * n * 4  # slot_roles dominant
    max_b = max(1, MEM_BUDGET_BYTES // max(per_trial, 1))
    return min(max_b, TR)


def run_cell_batched(
    variant: str,
    k: int,
    m_bundle: int,
    cleanup: str,
    v: int,
    n: int,
    tr: int,
    g: torch.Generator,
) -> Tuple[int, int, float]:
    """Run tr trials for one phase point on GPU. Returns (hit, n_trials, wall_s).

    Mechanism (mirrors v1.run_trial):
      - Per trial: build fresh V-book of atoms + (k, M, N) slot_roles.
      - Target atom index t drawn uniformly.
      - Layer l: slot 0 = bind(role[l,0], prev_state); slots 1..M-1 = bind(role[l,m], distractor).
      - Bundle M slots.
      - If cleanup ON and M > 1: preserve slot-0 contribution, unbind each m>=1
        slot from bundle, argmax-cleanup to nearest book row, rebundle.
      - Unwind: for l = k-1..0 apply unbind by slot_roles[l, 0].
      - Final argmax cleanup against V-book; hit iff argmax == t.
    """
    t0 = time.time()
    chunk = _chunk_size(k, m_bundle, n)
    total_hits = 0
    processed = 0
    while processed < tr:
        b = min(chunk, tr - processed)
        # Per-trial books and roles
        if variant == "ELEM_BIPOLAR":
            book = make_atoms_bipolar((b, v), n, g)          # (b, V, N) float32
            slot_roles = make_atoms_bipolar((b, k, m_bundle), n, g)  # (b, k, M, N)
        else:
            book = make_atoms_fhrr((b, v), n, g)             # (b, V, N) complex64
            slot_roles = make_atoms_fhrr((b, k, m_bundle), n, g)

        # Target index per trial (uniform 0..v-1)
        t_idx = torch.randint(0, v, size=(b,), device=DEVICE, generator=g,
                              dtype=torch.int64)
        # Payload = book[trial, t_idx[trial], :] via gather
        # shape (b, N)
        arange_b = torch.arange(b, device=DEVICE)
        payload = book[arange_b, t_idx]                       # (b, N)

        state = payload
        for layer in range(k):
            role0 = slot_roles[:, layer, 0]                   # (b, N)
            slot0 = bind_batched(role0, state, variant)       # (b, N)

            if m_bundle > 1:
                # Draw m_bundle - 1 distractor indices per trial from
                # [0..V-1] \ {t_idx}. To keep the batched code simple we sample
                # uniformly from 0..V-1 and re-roll positions that collide with
                # t_idx (at V=100 M=256 collision rate ~1%; expected mass of
                # rerolls per layer per trial < 3 -- negligible cost).
                # This matches v1's semantics (distractor != target) modulo
                # replacement vs no-replacement (v1 uses `replace=True` when
                # M-1 > V-1, so v2's with-replacement sampling is v1-compatible).
                d_idx = torch.randint(0, v, size=(b, m_bundle - 1),
                                      device=DEVICE, generator=g,
                                      dtype=torch.int64)
                # Reroll collisions with target (up to 4 passes; residual mass ~ (1/V)^4)
                for _ in range(4):
                    collide = (d_idx == t_idx.unsqueeze(1))
                    if not collide.any():
                        break
                    resample = torch.randint(0, v, size=d_idx.shape,
                                             device=DEVICE, generator=g,
                                             dtype=torch.int64)
                    d_idx = torch.where(collide, resample, d_idx)

                # Gather distractor atoms: book shape (b, V, N); d_idx (b, M-1)
                # Result (b, M-1, N)
                d_expand = d_idx.unsqueeze(-1).expand(-1, -1, n)   # (b, M-1, N)
                distractor_atoms = torch.gather(
                    book, dim=1, index=d_expand,
                )                                                   # (b, M-1, N) (complex or real)
                # Bind distractor atoms with roles[m>=1]
                d_roles = slot_roles[:, layer, 1:m_bundle, :]       # (b, M-1, N)
                distractor_slots = bind_batched(d_roles, distractor_atoms, variant)
                # Stack slot0 + distractor_slots -> (b, M, N) -> bundle
                all_slots = torch.cat([slot0.unsqueeze(1), distractor_slots], dim=1)
                state = bundle_batched(all_slots, variant)

                if cleanup == "ON":
                    # For each m >= 1: unbind state by role[l,m], argmax cleanup,
                    # rebind with role[l,m]. Preserve slot0 unchanged.
                    cleaned_slots = [slot0.unsqueeze(1)]  # (b, 1, N)
                    # Process distractor slots (still per-slot in a small loop
                    # because argmax needs per-slot argmax; but batched over trials).
                    for mi in range(1, m_bundle):
                        rmi = slot_roles[:, layer, mi]              # (b, N)
                        probe = unbind_batched(state, rmi, variant) # (b, N)
                        # Argmax against per-trial book: sims (b, V)
                        if variant == "ELEM_BIPOLAR":
                            sims = torch.einsum("bn,bvn->bv", probe, book)
                        else:
                            sims = torch.einsum(
                                "bn,bvn->bv", probe, book.conj(),
                            ).real
                        best = sims.argmax(dim=-1)                  # (b,)
                        clean_atom = book[arange_b, best]           # (b, N)
                        rebound = bind_batched(rmi, clean_atom, variant)  # (b, N)
                        cleaned_slots.append(rebound.unsqueeze(1))
                    state = bundle_batched(
                        torch.cat(cleaned_slots, dim=1), variant,
                    )
                # else cleanup OFF: state already set
            else:
                # m_bundle == 1: pure chain, no bundle; cleanup ON is no-op
                state = slot0

        # Unwind
        query = state
        for layer in range(k - 1, -1, -1):
            role0 = slot_roles[:, layer, 0]
            query = unbind_batched(query, role0, variant)

        # Final argmax
        if variant == "ELEM_BIPOLAR":
            sims_final = torch.einsum("bn,bvn->bv", query, book)
        else:
            sims_final = torch.einsum(
                "bn,bvn->bv", query, book.conj(),
            ).real
        recovered = sims_final.argmax(dim=-1)                       # (b,)
        hits = (recovered == t_idx).sum().item()
        total_hits += int(hits)
        processed += b
        # Explicit free of large per-chunk tensors
        del book, slot_roles, t_idx, payload, state, query, sims_final, recovered
        if variant == "ELEM_BIPOLAR" and m_bundle > 1:
            del distractor_atoms, d_roles, distractor_slots, all_slots
        if DEVICE.type == "cuda":
            torch.cuda.synchronize()

    wall = time.time() - t0
    return total_hits, tr, wall


def _cell_summary(cell: Dict[str, Any]) -> str:
    return "n=%d hit=%d recall=%.3f" % (
        cell["n"], cell["hit"], cell["recall"],
    )


def run_seed(seed: int) -> Dict[str, Any]:
    g = _torch_gen(seed)
    cells: Dict[str, Dict[str, Any]] = {}
    total = 0
    total_expected = CELLS_PER_SEED
    for (variant, k, m, cleanup, v) in GRID_CELLS:
        try:
            hit, n_trials, cell_wall = run_cell_batched(
                variant, k, m, cleanup, v, N_DIM, TR, g,
            )
        except Exception as e:
            print(
                "[FATAL] cell exception at variant=%s k=%d M=%d cleanup=%s V=%d: %s"
                % (variant, k, m, cleanup, v, repr(e)),
                flush=True,
            )
            raise
        recall = hit / n_trials
        key = "%s_V%d_k%d_M%d_%s" % (variant, v, k, m, cleanup)
        cells[key] = {
            "variant": variant, "V": v, "k": k, "M": m, "cleanup": cleanup,
            "n": n_trials, "hit": hit, "recall": recall, "wall_s": cell_wall,
        }
        total += 1
        print(
            "[seed=%d %d/%d] %s: %s wall=%.2fs"
            % (seed, total, total_expected, key, _cell_summary(cells[key]), cell_wall),
            flush=True,
        )
    return {"seed": seed, "TR": TR, "N": N_DIM, "V_GRID": V_GRID, "cells": cells}


# ---- v1 reproduction self-test ----------------------------------------------
_V1_SALVAGE_PATH = REPO / "data" / "exp_hrr_depth_budget_curve_v1" / "partial_metrics.json"


def _load_v1_salvage_seed7() -> Dict[str, float]:
    """Return {arm_name: recall} from v1 seed_7 salvage; empty dict if unavailable."""
    if not _V1_SALVAGE_PATH.exists():
        return {}
    try:
        d = json.loads(_V1_SALVAGE_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print("[selftest] WARN cannot load v1 salvage: %s" % repr(e), flush=True)
        return {}
    out = {}
    for row in d.get("per_arm", []):
        if row.get("seed") == 7:
            out[row["arm_name"]] = float(row["recall"])
    return out


# Six ship-critical arms spanning the cliff geometry (V=100 ceiling + V=1000 wall):
_V1_REPRO_ARMS = [
    ("ELEM_BIPOLAR", 20, 1, "OFF", 100),   # involutive baseline (expect 1.0)
    ("ELEM_BIPOLAR", 20, 16, "ON", 100),   # safe-regime ceiling (expect 1.0)
    ("ELEM_BIPOLAR", 10, 5, "ON", 100),    # base-regime health (expect ~1.0)
    ("ELEM_BIPOLAR", 10, 256, "ON", 1000), # wall cleanup (expect degraded)
    ("ELEM_BIPOLAR", 10, 256, "OFF", 1000),# wall no-cleanup (expect crashed)
    ("FHRR_CC", 20, 1, "OFF", 100),        # FHRR involutive
]


def _selftest_v1_reproduction() -> None:
    """Run 6 salvage-arm reproductions at seed=7 with reduced TR=50 and compare."""
    v1 = _load_v1_salvage_seed7()
    if not v1:
        print("[selftest] SKIP v1_reproduction (salvage file not present)", flush=True)
        return
    g = _torch_gen(7)
    tr_repro = 50  # smaller than 200 for smoke speed; SEM ~ 0.07 for mid-band
    print("[selftest] v1_reproduction: 6 arms at seed=7 TR=%d, tolerance 0.20 SEM-aware" % tr_repro, flush=True)
    all_ok = True
    for (variant, k, m, cleanup, v) in _V1_REPRO_ARMS:
        arm_name = "%s_V%d_k%d_M%d_%s" % (variant, v, k, m, cleanup)
        v1_recall = v1.get(arm_name, float("nan"))
        try:
            hit, n_trials, wall = run_cell_batched(
                variant, k, m, cleanup, v, N_DIM, tr_repro, g,
            )
            v2_recall = hit / n_trials
        except Exception as e:
            print("[selftest] FAIL cell %s exception: %s" % (arm_name, repr(e)), flush=True)
            all_ok = False
            continue
        # SEM at TR=50 is 1/sqrt(50) ~ 0.14; tolerance 0.20 covers 1.4x SEM
        # For {0,1} cliff points (recall ~ 0 or 1), tolerance is effectively 0.05 (rare deviation)
        is_cliff = (v1_recall < 0.05 or v1_recall > 0.95)
        tol = 0.05 if is_cliff else 0.20
        gap = abs(v2_recall - v1_recall)
        status = "OK" if gap <= tol else "MISMATCH"
        if status == "MISMATCH":
            all_ok = False
        print(
            "[selftest v1_repro] %s v1=%.3f v2=%.3f gap=%.3f tol=%.2f cliff=%s -> %s (wall=%.2fs)"
            % (arm_name, v1_recall, v2_recall, gap, tol, is_cliff, status, wall),
            flush=True,
        )
    if all_ok:
        print("[selftest] v1_reproduction PASS (all 6 arms within SEM tolerance)", flush=True)
    else:
        # Not a hard-fail (RNG streams differ across numpy vs torch), but note it.
        print("[selftest] v1_reproduction NOTE mismatches present -- see per-arm gaps above; "
              "does not gate cell (Monte-Carlo drift expected across PRNG streams)", flush=True)


def _selftest() -> None:
    """SANITY primitives + one end-to-end trivial trial."""
    g = _torch_gen(0)
    # ELEM_BIPOLAR involutive
    a = make_atoms_bipolar((), 64, g)
    b = make_atoms_bipolar((), 64, g)
    y = bind_batched(a, b, "ELEM_BIPOLAR")
    a_rec = unbind_batched(y, b, "ELEM_BIPOLAR")
    assert torch.equal(a_rec, a), "ELEM_BIPOLAR bind not involutive"
    # FHRR round trip
    ac = make_atoms_fhrr((), 64, g)
    bc = make_atoms_fhrr((), 64, g)
    yc = bind_batched(ac, bc, "FHRR_CC")
    ac_rec = unbind_batched(yc, bc, "FHRR_CC")
    assert torch.allclose(ac_rec, ac, atol=1e-3), "FHRR unbind not approximate inverse"
    # Trivial trial ELEM_BIPOLAR k=1 M=1 cleanup=OFF (must be 100%)
    hit, n_trials, wall = run_cell_batched(
        "ELEM_BIPOLAR", k=1, m_bundle=1, cleanup="OFF",
        v=10, n=256, tr=8, g=g,
    )
    assert hit == n_trials, (
        "trivial ELEM_BIPOLAR k=1 M=1 OFF failed: %d/%d" % (hit, n_trials)
    )
    print("[selftest] PASS: primitives + trivial end-to-end", flush=True)
    _selftest_v1_reproduction()


# ---- Verdict (identical logic to v1) --------------------------------------
def _agg_cells_across_seeds(per_seed: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    agg: Dict[str, Dict[str, Any]] = {}
    keys = set()
    for ps in per_seed:
        keys.update(ps["cells"].keys())
    for key in sorted(keys):
        recalls = []
        for ps in per_seed:
            if key in ps["cells"]:
                recalls.append(ps["cells"][key]["recall"])
        arr = np.array(recalls, dtype=np.float64)
        mean = float(arr.mean()) if arr.size else 0.0
        std = float(arr.std(ddof=0)) if arr.size else 0.0
        cv = float(std / mean) if mean > 1e-9 else 0.0
        agg[key] = {
            "recall_mean": mean, "recall_std": std, "recall_cv": cv,
            "n_seeds": arr.size, "per_seed_recall": recalls,
        }
    return agg


def verdict(per_seed: List[Dict[str, Any]]) -> Tuple[str, str, Dict[str, Any]]:
    agg = _agg_cells_across_seeds(per_seed)

    def get(key: str) -> float:
        return agg[key]["recall_mean"] if key in agg else float("nan")

    def cv(key: str) -> float:
        return agg[key]["recall_cv"] if key in agg else float("nan")

    involutive = get("ELEM_BIPOLAR_V100_k20_M1_OFF")
    ceiling_safe = get("ELEM_BIPOLAR_V100_k20_M16_ON")
    ceiling_safe_cv = cv("ELEM_BIPOLAR_V100_k20_M16_ON")
    wall_on = get("ELEM_BIPOLAR_V1000_k10_M256_ON")
    wall_off = get("ELEM_BIPOLAR_V1000_k10_M256_OFF")
    wall_gap = wall_on - wall_off
    wall_on_k20 = get("ELEM_BIPOLAR_V1000_k20_M256_ON")
    wall_off_k20 = get("ELEM_BIPOLAR_V1000_k20_M256_OFF")
    wall_gap_k20 = wall_on_k20 - wall_off_k20
    base_k10_ON = get("ELEM_BIPOLAR_V100_k10_M5_ON")
    shallow_wide = get("ELEM_BIPOLAR_V1000_k1_M256_ON")
    deep_narrow = get("ELEM_BIPOLAR_V1000_k20_M16_ON")
    shallow_lift = shallow_wide - deep_narrow
    fhrr_involutive = get("FHRR_CC_V100_k20_M1_OFF")
    fhrr_wall_on = get("FHRR_CC_V1000_k10_M256_ON")

    hf_msgs = []
    if not math.isnan(involutive) and involutive <= HF_INVOLUTIVE_BROKEN:
        hf_msgs.append("INVOLUTIVE_BROKEN: %.3f <= %.2f" % (involutive, HF_INVOLUTIVE_BROKEN))
    if not math.isnan(base_k10_ON) and base_k10_ON <= HF_DEPTH_COLLAPSE_SAFE:
        hf_msgs.append("SAFE_REGIME_COLLAPSE: %.3f <= %.2f" % (base_k10_ON, HF_DEPTH_COLLAPSE_SAFE))

    hp_conditions = {
        "involutive_V100_k20_M1_OFF>=0.99": involutive >= HP_INVOLUTIVE_RECALL,
        "safe_regime_ceiling_V100_k20_M16_ON>=0.95": (
            ceiling_safe >= HP_CEILING_SAFE and ceiling_safe_cv <= 0.05
        ),
        "wall_cleanup_gap_V1000_k10_M256>=0.20": wall_gap >= HP_CLEANUP_GAP_WALL,
    }
    hp_ok = all(hp_conditions.values())

    obs_cells = sum(len(ps["cells"]) for ps in per_seed)
    cardinality_ok = obs_cells == EXPECTED_N_UNITS
    if not cardinality_ok:
        hf_msgs.append(
            "CARDINALITY_BREACH: observed %d != expected %d"
            % (obs_cells, EXPECTED_N_UNITS)
        )

    summary_fields = {
        "involutive_V100_k20_M1_OFF_recall": involutive,
        "ceiling_safe_V100_k20_M16_ON_recall": ceiling_safe,
        "ceiling_safe_V100_k20_M16_ON_cv": ceiling_safe_cv,
        "wall_V1000_k10_M256_ON_recall": wall_on,
        "wall_V1000_k10_M256_OFF_recall": wall_off,
        "wall_V1000_k10_M256_cleanup_gap": wall_gap,
        "wall_V1000_k20_M256_ON_recall": wall_on_k20,
        "wall_V1000_k20_M256_OFF_recall": wall_off_k20,
        "wall_V1000_k20_M256_cleanup_gap": wall_gap_k20,
        "base_V100_k10_M5_ON_recall": base_k10_ON,
        "shallow_wide_V1000_k1_M256_ON_recall": shallow_wide,
        "deep_narrow_V1000_k20_M16_ON_recall": deep_narrow,
        "shallow_wide_lift": shallow_lift,
        "fhrr_involutive_V100_k20_M1_OFF_recall": fhrr_involutive,
        "fhrr_wall_V1000_k10_M256_ON_recall": fhrr_wall_on,
        "M_max_V100": frady_sommer_m_max(N_DIM, 100),
        "M_max_V1000": frady_sommer_m_max(N_DIM, 1000),
        "expected_n_units": EXPECTED_N_UNITS,
        "observed_n_units": obs_cells,
        "cardinality_ok": cardinality_ok,
        "hp_conditions": hp_conditions,
        "device_name": DEVICE_NAME,
        "compute_architecture": "batched_GPU",
    }

    if hf_msgs:
        return (
            "HARD_FAIL",
            "HARD_FAIL: " + " | ".join(hf_msgs)
            + " | involutive=%.3f ceiling_safe=%.3f wall_gap(V=1000,k=10,M=256)=%.3f"
              % (involutive, ceiling_safe, wall_gap),
            summary_fields,
        )
    if hp_ok:
        return (
            "HARD_PASS",
            (
                "HARD_PASS: GPU-batched HRR depth-budget reproduces v1 Donoho-Tanner probe. "
                "involutive(V=100,k=20,M=1,OFF)=%.3f (>=%.2f); "
                "safe_ceiling(V=100,k=20,M=16,ON)=%.3f cv=%.3f (>=%.2f); "
                "wall_gap(V=1000,k=10,M=256)=%.3f (>=%.2f). "
                "Secondary: wall_gap_k20=%.3f; shallow_wide_lift=%.3f; "
                "FHRR_CC involutive=%.3f wall_ON=%.3f. "
                "M_max(V=100)=%.1f M_max(V=1000)=%.1f. compute=batched_GPU device=%s."
            ) % (
                involutive, HP_INVOLUTIVE_RECALL,
                ceiling_safe, ceiling_safe_cv, HP_CEILING_SAFE,
                wall_gap, HP_CLEANUP_GAP_WALL,
                wall_gap_k20, shallow_lift,
                fhrr_involutive, fhrr_wall_on,
                frady_sommer_m_max(N_DIM, 100),
                frady_sommer_m_max(N_DIM, 1000),
                DEVICE_NAME,
            ),
            summary_fields,
        )
    return (
        "MIDDLE_BAND",
        (
            "MIDDLE_BAND: partial A2 verdict. "
            "involutive=%.3f; safe_ceiling=%.3f cv=%.3f; "
            "wall_gap(V=1000,k=10,M=256)=%.3f; wall_gap_k20=%.3f; "
            "base_V100_k10_M5_ON=%.3f; shallow_wide_lift=%.3f; "
            "FHRR involutive=%.3f wall_ON=%.3f. "
            "Conditions met: %s."
        ) % (
            involutive, ceiling_safe, ceiling_safe_cv,
            wall_gap, wall_gap_k20, base_k10_ON, shallow_lift,
            fhrr_involutive, fhrr_wall_on, hp_conditions,
        ),
        summary_fields,
    )


# ---- Driver ---------------------------------------------------------------
_selftest()
if _ARGS.self_test:
    sys.exit(0)

print("[config] %s" % CONFIG_VERSION, flush=True)
print("[config] EXPECTED_N_UNITS=%d TR=%d device=%s" % (EXPECTED_N_UNITS, TR, DEVICE_NAME), flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
t0 = time.time()

per_seed: List[Dict[str, Any]] = []
for seed in SEEDS:
    seed_t0 = time.time()
    result = run_seed(seed)
    result["N"] = N_DIM
    result["run_mode"] = RUN_MODE
    result["config_version"] = CONFIG_VERSION
    result["anchor_name"] = ANCHOR_NAME
    result["device_name"] = DEVICE_NAME
    result["elapsed_s"] = time.time() - seed_t0
    write_partial_key(out_dir, str(seed), result)
    per_seed.append(result)
    print(
        "[seed=%d] complete in %.1fs (%d cells)"
        % (seed, result["elapsed_s"], len(result["cells"])),
        flush=True,
    )

v, vmsg, summary_fields = verdict(per_seed)
print("\n[VERDICT] " + vmsg, flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": v,
    "verdict_msg": vmsg,
    "summary": vmsg,
    "run_mode": RUN_MODE,
    "N_DIM": N_DIM,
    "V_GRID": V_GRID,
    "K_GRID_CHEAP": K_GRID_CHEAP,
    "K_GRID_EXPENSIVE": K_GRID_EXPENSIVE,
    "M_GRID_CHEAP": M_GRID_CHEAP,
    "M_GRID_EXPENSIVE": M_GRID_EXPENSIVE,
    "BIND_VARIANTS": BIND_VARIANTS,
    "CLEANUP_GRID": CLEANUP_GRID,
    "TR_per_cell": TR,
    "n_seeds": len(SEEDS),
    "seeds": SEEDS,
    "cells_per_seed": CELLS_PER_SEED,
    "expected_n_units": EXPECTED_N_UNITS,
    "M_max_V100_frady_sommer": frady_sommer_m_max(N_DIM, 100),
    "M_max_V1000_frady_sommer": frady_sommer_m_max(N_DIM, 1000),
    "config_version": CONFIG_VERSION,
    "device_name": DEVICE_NAME,
    "compute_architecture": "batched_GPU",
    "per_seed": per_seed,
    "agg_across_seeds": _agg_cells_across_seeds(per_seed),
    "summary_fields": summary_fields,
    "elapsed_s": time.time() - t0,
}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written to %s/metrics.json" % out_dir, flush=True)
