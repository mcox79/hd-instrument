"""hrr_depth_budget_curve_v1 -- depth-budget envelope for HRR bind chains
                                 with Frady-Sommer-crossing M x V phase probe (A2 scope).

Closes 2026-06-23 research drill open item (notes/research_drill_hrr_capacity_vs_depth_2026-06-23.md).
A1 smoke at V=100 M<=16 hit ceiling (all recall=1.000 for ELEM_BIPOLAR); A2 scope extends
into the genuine noise regime by pushing M_bundle up to Frady-Sommer M_max crossover for
each V_CLEANUP, producing a depth-vs-noise phase curve isomorphic to Donoho-Tanner L1-recovery.

Frady-Sommer 2018 (openreview 6tazBqPem3) capacity: M_max = N / (4 * log V)
  V=100,  N=8192 -> M_max = 8192/(4*4.605) = 444.7  -> M in {16, 64, 256} straddles regime
  V=1000, N=8192 -> M_max = 8192/(4*6.908) = 296.4  -> M=256 sits right at wall (M/M_max~0.86)

Grid TWO_TIER (per V, per variant, per cleanup):
  Cheap tier   (M in {1, 5, 16}, well below M_max):     k in {1, 5, 10, 15, 20} = 5 depths
  Expensive tier (M in {64, 256}, at / crossing M_max):  k in {1, 10, 20}       = 3 depths
    -> 5*3 + 3*2 = 21 (k, M) points per (V, variant, cleanup)

  Total per seed: 21 * 2 V * 2 variants * 2 cleanup = 168 cells
  Full: 3 seeds * 168 = 504 units (CARDINALITY_OK gate).

Protocol per (k, M, variant, cleanup, V, seed) -- distinct-slot-role m4_nested pattern:
  1. Build cleanup memory book of V random atoms + M_bundle distinct slot_roles per layer.
  2. Layer l: state = bundle([bind(slot_roles[l,0], prev_state)] +
                              [bind(slot_roles[l,m], distractor_m) for m in 1..M-1]).
  3. If cleanup=ON and M>1: preserve slot-0 wrapped-state; for slots m>=1, unbind by
     slot_roles[l,m], argmax against book, rebind (denoise distractor superposition
     while preserving recursive chain-carrier). For M=1: no-op (nothing to denoise).
  4. Unwind: for l=k-1..0 apply unbind by slot_roles[l,0].
  5. Final cleanup against V. Correct iff argmax == t.

Substrate wall prediction (per research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x_2026-06-04.md):
  Substrate operates in dense-bipolar regime (f=1.0); the M-bundle superposition
  in HRR is structurally equivalent to K-sparse L1-recovery under Donoho-Tanner phase
  boundary at K/M ~ 0.20 +/- 0.03 with M/N ~ 0.14. For substrate: expected substantial
  degradation at (M/N > 0.03) x (V >= few hundred). At M=256, V=1000 we sit near the
  known wall -> cleanup-ON minus cleanup-OFF gap becomes non-trivial (AMP-like denoise
  regime; predicted 0.2-0.5 lift for ELEM_BIPOLAR).

Discriminators (A2 scope):
  Primary A involutive baseline (HP): recall@1 >= 0.99 at k=20, M=1, cleanup=OFF, ELEM_BIPOLAR
                                       (positive control; drill involutive prediction).
  Primary B ceiling-holds-below-wall (HP): recall@1 >= 0.95 at k=20, M=16, cleanup=ON,
                                            V=100, ELEM_BIPOLAR (safe regime).
  Primary C cleanup-gap-in-noise-regime (HP): recall@1(M=256,V=1000,ON) - recall@1(M=256,V=1000,OFF)
                                               >= 0.20 at k=10, ELEM_BIPOLAR (Donoho-Tanner
                                               / AMP compensation active near wall).
  Secondary shallow-wide-vs-deep-narrow (HP): recall@1(k=1, M=256, V=1000, ON) >=
                                               recall@1(k=20, M=16, V=1000, ON) + 0.10.
  Tertiary  wall-crossing (report): identify (k, M, V) frontier where recall drops below 0.70.

  HARD_FAIL depth-collapse-safe-regime: recall@1(k=10, M=5, ON, V=100, ELEM_BIPOLAR) <= 0.70
                                        (base regime broken -- impl bug).
  HARD_FAIL involutive-broken: recall@1(k=20, M=1, OFF, ELEM_BIPOLAR) <= 0.95.

Regime-aware verdict logic (per Director A2 directive):
  Cleanup-OFF ceiling at M < M_max = N/(4 log V) is EXPECTED not failure.
  Cleanup-gap discriminator applies at M >= M_max/2 only. Ceiling below crossover is
  a positive substrate finding (no cleanup infrastructure needed in safe regime),
  not a MIDDLE_BAND.

CARDINALITY_OK: expected_n_units = 3 seeds * 168 = 504; hard-fail if breach.

No silent except. Selftest asserts bind involutive + FHRR round-trip + top-1 cleanup +
trivial-trial end-to-end.

ASCII-only. write_metrics. Refs:
  notes/research_drill_hrr_capacity_vs_depth_2026-06-23.md (drill design; A1 spec)
  notes/research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x_2026-06-04.md
    (Donoho-Tanner wall; substrate K/M ~ 0.20 +- 0.03 at M/N=0.14; AMP analog)
  data/exp_m4_nested/metrics.json (prior; d1-d5 100/100/100/100/97 at N=1024 FHRR)
  data/exp_nesting_depth_cpu_v1/metrics.json (prior smoke; d4=d8=1.0 at N=2048 FHRR)
  data/exp_hrr_depth_budget_sparse_bipolar_v2/metrics.json
    (W-free Hopfield direct recall; sparse f-sweep at N=4096; does NOT cover
     M_bundle x V grid; complementary paradigm)
  data/exp_hrr_depth_budget_curve_v1_smoke/metrics.json (A1 smoke; ceiling at M<=16)
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import math
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "hrr_depth_budget_curve_v1"

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

# ---- Config (A2 scope; Donoho-Tanner / Frady-Sommer M_max crossover probe) ----
N_DIM = 8192

# TWO_TIER grid: cheap tier fills k densely at low-M; expensive tier fills k
# sparsely at high-M near Frady-Sommer M_max = N/(4 log V).
#   V=100:  M_max ~ 445 -> M in {64, 256} well below crossover
#   V=1000: M_max ~ 297 -> M=256 sits at ~0.86*M_max (wall regime)
K_GRID_CHEAP = [1, 5, 10, 15, 20]
K_GRID_EXPENSIVE = [1, 10, 20]
M_GRID_CHEAP = [1, 5, 16]        # below M_max/10 for both V values
M_GRID_EXPENSIVE = [64, 256]     # from mid-fraction to M_max wall
V_GRID = [100, 1000]
BIND_VARIANTS = ["ELEM_BIPOLAR", "FHRR_CC"]
CLEANUP_GRID = ["OFF", "ON"]
SEEDS_FULL = [7, 13, 19]
SEEDS_SMOKE = [7]
TR_FULL = 200
TR_SMOKE = 20

SEEDS = SEEDS_SMOKE if SMOKE else SEEDS_FULL
TR = TR_SMOKE if SMOKE else TR_FULL


def _grid_cells() -> List[Tuple[str, int, int, str, int]]:
    """Enumerate (variant, k, M, cleanup, V) cells across TWO_TIER x V x variant x cleanup."""
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
    """Frady-Sommer 2018 capacity: M_max = N / (4 log V)."""
    return float(n) / (4.0 * math.log(v))


# Pre-reg discriminator bands (A2 scope)
HP_INVOLUTIVE_RECALL = 0.99  # k=20, M=1, OFF, V=100, ELEM_BIPOLAR
HP_CEILING_SAFE = 0.95       # k=20, M=16, ON, V=100, ELEM_BIPOLAR (safe regime holds)
HP_CLEANUP_GAP_WALL = 0.20   # k=10, M=256, V=1000, ELEM_BIPOLAR: ON - OFF (AMP compensation)
HP_SHALLOW_WIDE_LIFT = 0.10  # k=1 M=256 V=1000 ON - k=20 M=16 V=1000 ON

HF_DEPTH_COLLAPSE_SAFE = 0.70  # k=10, M=5, ON, V=100, ELEM_BIPOLAR (impl bug if collapse)
HF_INVOLUTIVE_BROKEN = 0.95    # k=20, M=1, OFF, V=100, ELEM_BIPOLAR
HF_CLEANUP_NOT_LOAD = 0.05     # cleanup gap at wall regime below this = not load-bearing

# Regime-aware ceiling policy (per Director A2 directive):
# Cleanup-gap discriminator applies ONLY at M >= M_max/2 (past crossover). Below the
# crossover the OFF baseline is at ceiling by construction and ON cannot lift.
# HP evaluated at (M=256, V=1000) which is 0.86 * M_max (crossover regime).

CONFIG_VERSION = (
    "ANCHOR=%s,N_DIM=%d,V=%s,k_cheap=%s,k_exp=%s,M_cheap=%s,M_exp=%s,"
    "variants=%s,cleanup=%s,seeds=%s,TR=%d,mode=%s,scope=A2_donoho_tanner_probe,"
    "M_max(V=100)=%.1f,M_max(V=1000)=%.1f"
) % (
    ANCHOR_NAME, N_DIM, V_GRID, K_GRID_CHEAP, K_GRID_EXPENSIVE,
    M_GRID_CHEAP, M_GRID_EXPENSIVE, BIND_VARIANTS, CLEANUP_GRID, SEEDS, TR, RUN_MODE,
    frady_sommer_m_max(N_DIM, 100), frady_sommer_m_max(N_DIM, 1000),
)


# ---- Primitives -----------------------------------------------------------
def make_atom_bipolar(n: int, g: np.random.Generator) -> np.ndarray:
    """Bipolar {-1,+1}^n atom."""
    return (g.integers(0, 2, size=n, dtype=np.int8) * 2 - 1).astype(np.float32)


def make_atom_fhrr(n: int, g: np.random.Generator) -> np.ndarray:
    """Unit-modulus complex phasor atom (FHRR)."""
    ang = (g.random(n) * 2 - 1) * math.pi
    return np.exp(1j * ang).astype(np.complex64)


def bind_bipolar(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Element-wise multiply on bipolar {-1,+1} -> bipolar; involutive."""
    return (a * b).astype(np.float32)


def unbind_bipolar(y: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Element-wise multiply on bipolar; own inverse."""
    return (y * b).astype(np.float32)


def bind_fhrr_cc(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """FHRR circular convolution via elementwise complex multiply on unit-modulus phasors.

    Note: on unit-modulus complex vectors, elementwise multiply is Plate's CC in frequency
    domain (phase addition). Unbind is conjugate multiply. This is the substrate FHRR
    variant used by exp_m4_nested; represents Plate's original binding operator.
    """
    return (a * b).astype(np.complex64)


def unbind_fhrr_cc(y: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Conjugate multiply (approximate inverse for FHRR CC)."""
    return (y * b.conj()).astype(np.complex64)


def sign_quantize_bipolar(x: np.ndarray) -> np.ndarray:
    """Sign-quantize a real vector back to bipolar {-1,+1}; ties -> +1."""
    out = np.where(x >= 0, 1.0, -1.0).astype(np.float32)
    return out


def bundle_norm_bipolar(vecs: List[np.ndarray]) -> np.ndarray:
    """Bundle by SUM (linear superposition, NOT sign-quantized).

    Per Frady-Sommer 2018 capacity analysis, sign-quantize-at-bundle drops
    ~30-40% target signal per layer; correct HRR/BSC bundling is linear
    superposition, with sign-quantize applied only at final CLEANUP against
    a codebook (argmax dot-product). Bind-with-a-real-valued-vector remains
    correct because element-wise multiply distributes over sum.
    """
    return np.sum(np.stack(vecs, axis=0), axis=0).astype(np.float32)


def bundle_norm_fhrr(vecs: List[np.ndarray]) -> np.ndarray:
    """Bundle by sum then renormalize to unit modulus per-position."""
    s = np.sum(np.stack(vecs, axis=0), axis=0)
    mag = np.abs(s)
    # Avoid div-by-zero: positions with zero sum reset to angle 0 (magnitude 1)
    mag_safe = np.where(mag > 1e-12, mag, 1.0)
    out = (s / mag_safe).astype(np.complex64)
    # Zero-sum positions become (1+0j); rare but bounded
    return out


def cleanup_bipolar(x: np.ndarray, book: np.ndarray) -> np.ndarray:
    """Nearest-neighbor cleanup against bipolar codebook rows; returns closest atom vector."""
    # book shape (V, N); x shape (N,)
    sims = book @ x  # (V,)
    idx = int(np.argmax(sims))
    return book[idx].copy()


def cleanup_fhrr(x: np.ndarray, book: np.ndarray) -> np.ndarray:
    """Nearest-neighbor cleanup on complex codebook via Re(book @ x*).conj sim."""
    # book shape (V, N) complex; x shape (N,) complex; sim = Re(book @ x.conj())
    sims = (book @ x.conj()).real  # (V,)
    idx = int(np.argmax(sims))
    return book[idx].copy()


def argmax_bipolar(x: np.ndarray, book: np.ndarray) -> int:
    sims = book @ x
    return int(np.argmax(sims))


def argmax_fhrr(x: np.ndarray, book: np.ndarray) -> int:
    sims = (book @ x.conj()).real
    return int(np.argmax(sims))


# ---- Trial ----------------------------------------------------------------
def run_trial(
    variant: str,
    k: int,
    m_bundle: int,
    cleanup: str,
    n: int,
    v: int,
    g: np.random.Generator,
) -> bool:
    """Run one (variant, k, M, cleanup) trial. Returns True iff argmax cleanup recovers target.

    Semantics: at each layer l, we build a M-slot structure where slot 0 carries the
    "chain continuation" (the prev-layer state) and slots 1..M-1 carry M-1 distractor
    atoms. Each slot has its own DISTINCT role vector (slot_roles[l, m]) so that
    unbinding by slot_roles[l, 0] selects only the chain-continuation branch. This
    mirrors m4_nested's agent_role/patient_role pattern (100% recall at d=1-5, N=1024).
    """
    # Build vocab + roles
    if variant == "ELEM_BIPOLAR":
        book = np.stack([make_atom_bipolar(n, g) for _ in range(v)], axis=0)
        slot_roles = np.stack(
            [make_atom_bipolar(n, g) for _ in range(k * m_bundle)], axis=0,
        ).reshape(k, m_bundle, n)
        bind = bind_bipolar
        unbind = unbind_bipolar
        bundle = bundle_norm_bipolar
        argmax_fn = argmax_bipolar
    elif variant == "FHRR_CC":
        book = np.stack([make_atom_fhrr(n, g) for _ in range(v)], axis=0)
        slot_roles = np.stack(
            [make_atom_fhrr(n, g) for _ in range(k * m_bundle)], axis=0,
        ).reshape(k, m_bundle, n)
        bind = bind_fhrr_cc
        unbind = unbind_fhrr_cc
        bundle = bundle_norm_fhrr
        argmax_fn = argmax_fhrr
    else:
        raise ValueError("unknown variant: " + variant)

    # Pick target leaf
    t_idx = int(g.integers(0, v))
    payload = book[t_idx].copy()

    # Nest k layers. Layer l: slot 0 = bind(slot_roles[l, 0], prev_state);
    # slots 1..M-1 = bind(slot_roles[l, m], distractor_m). Bundle all M slots.
    state = payload
    for layer in range(k):
        slot_items = [bind(slot_roles[layer, 0], state)]
        if m_bundle > 1:
            distractor_pool = [i for i in range(v) if i != t_idx]
            # If M-1 > pool, sample with replacement (drill semantics allows repeated
            # distractors — bundle slots are physical carriers, duplicate atoms per
            # layer is a valid load). At V=100, M=256: 255 slots draw from 99 atoms
            # with replacement — reproduces the Frady-Sommer M >> V wall regime.
            replace = (m_bundle - 1) > len(distractor_pool)
            d_idx = g.choice(
                len(distractor_pool), size=m_bundle - 1, replace=replace,
            )
            for m in range(1, m_bundle):
                d_atom = book[distractor_pool[int(d_idx[m - 1])]]
                slot_items.append(bind(slot_roles[layer, m], d_atom))
            state = bundle(slot_items)
        else:
            # Pure chain: single slot, no bundle
            state = slot_items[0]

        if cleanup == "ON" and m_bundle > 1:
            # Per-layer cleanup (drill L2.1 approximation): apply cleanup ONLY to
            # distractor slots m>=1 (which hold codebook atoms). Slot 0 carries the
            # nested chain-continuation state (bind(...bind(...target))) and is NOT
            # a codebook atom -- projecting it onto book would corrupt the chain.
            # This denoises the distractor superposition while preserving the
            # recursive chain-carrier signal. Complexity O((M-1) * V * N) per layer.
            # Reconstruct the slot-0 contribution by subtracting distractor slots,
            # cleaning distractors, then re-summing. Requires SUM bundle (linear).
            #
            # Formulation: since bundle = sum, state = slot0_bind + sum_{m>=1} slot_m_bind.
            # Extract distractor superposition: for each m>=1, unbind by slot_roles[l,m]
            # to get atom candidate + slot_0_bind*slot_roles[l,m]^-1 crosstalk. Cleanup
            # the atom via top-1 argmax. Then reconstruct: cleaned_state = slot0_bind +
            # sum_{m>=1} bind(slot_roles[l,m], cleaned_atom_m). But we don't have direct
            # access to slot0_bind post-bundle. Approximation: rebuild the whole bundle
            # from CLEANED distractor atoms + the original slot0 wrapped-state.
            # We already have `slot_items[0]` cached from the bundling step above.
            cleaned_slots = [slot_items[0]]  # preserve chain-continuation slot
            for m in range(1, m_bundle):
                probe = unbind(state, slot_roles[layer, m])
                if variant == "ELEM_BIPOLAR":
                    sims = book @ probe
                else:
                    sims = (book @ probe.conj()).real
                atom_idx = int(np.argmax(sims))
                cleaned_slots.append(bind(slot_roles[layer, m], book[atom_idx]))
            state = bundle(cleaned_slots)
        elif cleanup == "ON" and m_bundle == 1:
            # M=1: cleanup is a no-op on pure chain (nothing to denoise beyond
            # the perfect involutive carry). Preserves state unchanged so the
            # cleanup-ON grid remains directly comparable to cleanup-OFF at M=1.
            pass

    # Unwind: walk down slot-0 chain (unbind by slot_roles[l, 0] in reverse layer order)
    query = state
    for layer in range(k - 1, -1, -1):
        query = unbind(query, slot_roles[layer, 0])

    # Final cleanup + verify
    recovered = argmax_fn(query, book)
    return recovered == t_idx


def _cell_summary(cell: Dict[str, Any]) -> str:
    return "n=%d hit=%d recall=%.3f" % (
        cell["n"], cell["hit"], cell["recall"],
    )


def run_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    cells: Dict[str, Dict[str, Any]] = {}
    total = 0
    total_expected = CELLS_PER_SEED
    for (variant, k, m, cleanup, v) in GRID_CELLS:
        t_cell = time.time()
        hit = 0
        for _ in range(TR):
            try:
                ok = run_trial(variant, k, m, cleanup, N_DIM, v, g)
            except Exception as e:
                # No silent except; record error and re-raise
                print(
                    "[FATAL] trial exception at variant=%s k=%d M=%d cleanup=%s V=%d: %s"
                    % (variant, k, m, cleanup, v, repr(e)),
                    flush=True,
                )
                raise
            if ok:
                hit += 1
        recall = hit / TR
        cell_wall = time.time() - t_cell
        key = "%s_V%d_k%d_M%d_%s" % (variant, v, k, m, cleanup)
        cells[key] = {
            "variant": variant, "V": v, "k": k, "M": m, "cleanup": cleanup,
            "n": TR, "hit": hit, "recall": recall, "wall_s": cell_wall,
        }
        total += 1
        print(
            "[seed=%d %d/%d] %s: %s wall=%.1fs"
            % (seed, total, total_expected, key, _cell_summary(cells[key]), cell_wall),
            flush=True,
        )
    return {"seed": seed, "TR": TR, "N": N_DIM, "V_GRID": V_GRID, "cells": cells}


def _selftest() -> None:
    """SANITY: bind involutive on ELEM_BIPOLAR; unbind approximate inverse on FHRR_CC."""
    g = np.random.default_rng(0)
    # ELEM_BIPOLAR involutive
    a = make_atom_bipolar(64, g)
    b = make_atom_bipolar(64, g)
    y = bind_bipolar(a, b)
    a_rec = unbind_bipolar(y, b)
    assert np.array_equal(a_rec, a), "ELEM_BIPOLAR bind not involutive: %s" % (
        (a_rec == a).mean(),
    )
    # FHRR_CC round-trip on unit modulus
    ac = make_atom_fhrr(64, g)
    bc = make_atom_fhrr(64, g)
    yc = bind_fhrr_cc(ac, bc)
    ac_rec = unbind_fhrr_cc(yc, bc)
    assert np.allclose(ac_rec, ac, atol=1e-3), "FHRR_CC unbind not approximate inverse"
    # Cleanup returns book row
    book_b = np.stack([make_atom_bipolar(64, g) for _ in range(5)], axis=0)
    x = book_b[2] + 0.1 * make_atom_bipolar(64, g)
    cx = cleanup_bipolar(x, book_b)
    assert np.array_equal(cx, book_b[2]), "cleanup_bipolar did not recover argmax row"
    # One end-to-end trial at tiny scale must succeed for ELEM_BIPOLAR k=1 M=1 cleanup=OFF
    ok = run_trial("ELEM_BIPOLAR", k=1, m_bundle=1, cleanup="OFF", n=256, v=10, g=g)
    assert ok, "trivial k=1 M=1 cleanup=OFF trial failed on ELEM_BIPOLAR (broken involutive)"
    print("[selftest] PASS: hrr_depth_budget_curve_v1", flush=True)


# ---- Verdict --------------------------------------------------------------
def _agg_cells_across_seeds(per_seed: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Average recall per (variant, k, M, cleanup) key across seeds; also cv."""
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

    # A2 discriminators
    involutive = get("ELEM_BIPOLAR_V100_k20_M1_OFF")   # positive control
    ceiling_safe = get("ELEM_BIPOLAR_V100_k20_M16_ON")  # safe regime holds
    ceiling_safe_cv = cv("ELEM_BIPOLAR_V100_k20_M16_ON")

    # Wall-regime cleanup gap (A2 Donoho-Tanner probe):
    # M=256, V=1000 sits at 0.86 * M_max (Frady-Sommer wall).
    # k=10 is the mid-depth probe (both k=1 and k=20 available too).
    wall_on   = get("ELEM_BIPOLAR_V1000_k10_M256_ON")
    wall_off  = get("ELEM_BIPOLAR_V1000_k10_M256_OFF")
    wall_gap  = wall_on - wall_off

    wall_on_k20  = get("ELEM_BIPOLAR_V1000_k20_M256_ON")
    wall_off_k20 = get("ELEM_BIPOLAR_V1000_k20_M256_OFF")
    wall_gap_k20 = wall_on_k20 - wall_off_k20

    # Base-regime depth-collapse check (should hold at safe M/V)
    base_k10_ON = get("ELEM_BIPOLAR_V100_k10_M5_ON")

    # Shallow-wide vs deep-narrow at V=1000 (near-wall)
    shallow_wide = get("ELEM_BIPOLAR_V1000_k1_M256_ON")
    deep_narrow  = get("ELEM_BIPOLAR_V1000_k20_M16_ON")
    shallow_lift = shallow_wide - deep_narrow

    # FHRR_CC secondary discriminator (Plate-CC norm-decay comparison)
    fhrr_involutive = get("FHRR_CC_V100_k20_M1_OFF")
    fhrr_wall_on    = get("FHRR_CC_V1000_k10_M256_ON")

    # HARD_FAIL checks (base-regime health only; wall-regime failures are informative
    # not disqualifying per Director's regime-aware directive)
    hf_msgs = []
    if not math.isnan(involutive) and involutive <= HF_INVOLUTIVE_BROKEN:
        hf_msgs.append(
            "INVOLUTIVE_BROKEN: ELEM_BIPOLAR V=100 k=20 M=1 OFF recall=%.3f <= %.2f "
            "(bind not depth-lossless -- impl bug or sign-quantize collision)"
            % (involutive, HF_INVOLUTIVE_BROKEN)
        )
    if not math.isnan(base_k10_ON) and base_k10_ON <= HF_DEPTH_COLLAPSE_SAFE:
        hf_msgs.append(
            "SAFE_REGIME_COLLAPSE: ELEM_BIPOLAR V=100 k=10 M=5 ON recall=%.3f <= %.2f "
            "(base regime broken; below-wall config should ceiling-hold)"
            % (base_k10_ON, HF_DEPTH_COLLAPSE_SAFE)
        )

    # HARD_PASS conditions (regime-aware per Director A2 directive)
    hp_conditions = {
        "involutive_V100_k20_M1_OFF>=0.99": involutive >= HP_INVOLUTIVE_RECALL,
        "safe_regime_ceiling_V100_k20_M16_ON>=0.95": (
            ceiling_safe >= HP_CEILING_SAFE and ceiling_safe_cv <= 0.05
        ),
        "wall_cleanup_gap_V1000_k10_M256>=0.20": wall_gap >= HP_CLEANUP_GAP_WALL,
    }
    hp_ok = all(hp_conditions.values())

    # Cardinality sanity
    obs_cells = sum(len(ps["cells"]) for ps in per_seed)
    cardinality_ok = obs_cells == EXPECTED_N_UNITS
    if not cardinality_ok:
        hf_msgs.append(
            "CARDINALITY_BREACH: observed %d units != expected %d"
            % (obs_cells, EXPECTED_N_UNITS)
        )

    summary_fields = {
        # positive controls
        "involutive_V100_k20_M1_OFF_recall": involutive,
        "ceiling_safe_V100_k20_M16_ON_recall": ceiling_safe,
        "ceiling_safe_V100_k20_M16_ON_cv": ceiling_safe_cv,
        # wall-regime discriminators (Donoho-Tanner probe)
        "wall_V1000_k10_M256_ON_recall": wall_on,
        "wall_V1000_k10_M256_OFF_recall": wall_off,
        "wall_V1000_k10_M256_cleanup_gap": wall_gap,
        "wall_V1000_k20_M256_ON_recall": wall_on_k20,
        "wall_V1000_k20_M256_OFF_recall": wall_off_k20,
        "wall_V1000_k20_M256_cleanup_gap": wall_gap_k20,
        # base regime + shallow-wide + FHRR comparison
        "base_V100_k10_M5_ON_recall": base_k10_ON,
        "shallow_wide_V1000_k1_M256_ON_recall": shallow_wide,
        "deep_narrow_V1000_k20_M16_ON_recall": deep_narrow,
        "shallow_wide_lift": shallow_lift,
        "fhrr_involutive_V100_k20_M1_OFF_recall": fhrr_involutive,
        "fhrr_wall_V1000_k10_M256_ON_recall": fhrr_wall_on,
        # Frady-Sommer references
        "M_max_V100": frady_sommer_m_max(N_DIM, 100),
        "M_max_V1000": frady_sommer_m_max(N_DIM, 1000),
        # cardinality
        "expected_n_units": EXPECTED_N_UNITS,
        "observed_n_units": obs_cells,
        "cardinality_ok": cardinality_ok,
        "hp_conditions": hp_conditions,
    }

    if hf_msgs:
        return (
            "HARD_FAIL",
            "HARD_FAIL: " + " | ".join(hf_msgs)
            + (" | involutive=%.3f ceiling_safe=%.3f wall_gap(V=1000,k=10,M=256)=%.3f"
               % (involutive, ceiling_safe, wall_gap)),
            summary_fields,
        )
    if hp_ok:
        return (
            "HARD_PASS",
            (
                "HARD_PASS: substrate HRR depth-budget spans safe regime AND cleanup "
                "actively compensates at Donoho-Tanner wall. "
                "involutive(V=100,k=20,M=1,OFF)=%.3f (>=%.2f); "
                "safe_ceiling(V=100,k=20,M=16,ON)=%.3f cv=%.3f (>=%.2f); "
                "wall_gap(V=1000,k=10,M=256)=%.3f (>=%.2f). "
                "Secondary: wall_gap_k20=%.3f; shallow_wide_lift=%.3f; "
                "FHRR_CC involutive=%.3f wall_ON=%.3f. "
                "M_max(V=100)=%.1f M_max(V=1000)=%.1f."
            ) % (
                involutive, HP_INVOLUTIVE_RECALL,
                ceiling_safe, ceiling_safe_cv, HP_CEILING_SAFE,
                wall_gap, HP_CLEANUP_GAP_WALL,
                wall_gap_k20, shallow_lift,
                fhrr_involutive, fhrr_wall_on,
                frady_sommer_m_max(N_DIM, 100),
                frady_sommer_m_max(N_DIM, 1000),
            ),
            summary_fields,
        )

    # MIDDLE_BAND
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
print("[config] EXPECTED_N_UNITS=%d TR=%d" % (EXPECTED_N_UNITS, TR), flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
t0 = time.time()

run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
per_seed: List[Dict[str, Any]] = []
for seed in SEEDS:
    seed_t0 = time.time()
    result = run_seed(seed)
    result["N"] = N_DIM
    result["run_mode"] = RUN_MODE
    result["config_version"] = CONFIG_VERSION
    result["anchor_name"] = ANCHOR_NAME
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
    "per_seed": per_seed,
    "agg_across_seeds": _agg_cells_across_seeds(per_seed),
    "summary_fields": summary_fields,
    "elapsed_s": time.time() - t0,
}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written to %s/metrics.json" % out_dir, flush=True)
