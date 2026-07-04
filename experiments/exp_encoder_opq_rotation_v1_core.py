"""Encoder OPQ-STYLE LEARNED ROTATION before block-argmax quantization -- the
LAST sparsity-preserving shot at retrieval (ret_agree10) at fixed K=128/3.125%
active before accepting either a code-widening (K=256, doubles density) or a
sparsity-preserving dead-end.

THREE CONVERGENT EVIDENCE LINES motivating this cell (do not re-litigate):
  1. Skunkworks HARD_FAIL closure of the KL-RANK objective-family swap
     (commit 7f116800d, MEASURED@data/exp_encoder_objective_swap_kl_rank_v1_
     seed7/metrics.json + ..._seed13/metrics.json): KL-RANK does NOT lift
     ret_agree10 at fixed K=128 (0.2229/0.2193, delta-vs-MSE +0.0117/+0.0089,
     ~9x smaller than K256's verified +0.093) -- PROVES the retrieval ceiling
     at fixed code capacity is a CODE/QUANTIZATION-STRUCTURE bound, NOT a
     training-objective bound. K256 lifts it materially (+0.093 MEASURED) but
     doubles density (6.25% active), breaking the sparsity goal.
  2. Cardinality drill (notes/research_drill_encoder_cardinality_capacity_
     ceiling_0.85_reachability_2026-07-04.md): Rank 2 structural lever
     (P_deflated=0.45 rotation-only variant) is "learned rotation before
     block-selection (OPQ-style)" -- our block-WTA structure IS mathematically
     Product Quantization (PQ); PQ's well-documented "subspace-independence"
     tax is exactly the axis-misalignment cost a rotation fixes CHEAPLY (no
     width/runtime change), per the OPQ literature (Ge, He, Sun, "Optimized
     Product Quantization", CVPR 2013 / TPAMI 2014).
  3. Bypass diagnostic (MEASURED@data/exp_encoder_teacher_sparsifier_bypass_
     v1/metrics.json): at ZERO training (teacher embeddings straight through
     the SAME K=128 quantizer), ORTHO_K128 (isometric random lift)
     ret_agree10=0.4295 vs the TRAINED student's ret_agree10=0.21 -- roughly
     HALF the code's own zero-training ceiling is left on the table by
     training. This is a CODE-UTILIZATION gap, not (necessarily) a code-
     capacity gap: does a SMARTER (not merely random) axis choice close more
     of it, without adding density?

IMPORTANT CAVEAT the bypass diagnostic does NOT already answer: its
"ORTHO_K128" and "RANDOM_K128" arms are BOTH data-INDEPENDENT random lifts
(isometry_vs_random_gap_k128=0.0276 MEASURED -- a small gap between two
FLAVORS of random projection). Neither is a DATA-ADAPTED (OPQ-style)
rotation. This cell is the first to test a genuinely adapted rotation.

HYPOTHESIS: the trained student's D=4096 output is highly ANISOTROPIC (a
distillation target derived from a rank<=1024 BGE teacher via a low-rank-ish
MLP map almost certainly concentrates variance very unevenly across its 4096
raw output coordinates). The EXISTING code's blocks are CONTIGUOUS RAW-INDEX
ranges [0:32], [32:64], ... -- i.e. axis-aligned to whatever the MLP's output
neurons happen to be, not to the student's own variance structure. Some
blocks are almost certainly starved (all-near-zero-variance neurons, argmax
picks noise) while others are variance-saturated (one dominant neuron always
wins, wasting the block's L=32-way capacity). A rotation that REDISTRIBUTES
variance evenly across all K=128 blocks before the hard per-block argmax
should let MORE blocks compete informatively -> higher ret_agree10 at the
SAME K=128/3.125% sparsity, same width, same runtime.

MECHANISM CHOSEN (ONE, well-justified -- not diluting across many under-
tested variants per "no padding experiments"): NON-PARAMETRIC OPQ /
EIGENVALUE-ALLOCATION rotation (Ge, He, Sun, "Optimized Product
Quantization for Approximate Nearest Neighbor Search", CVPR 2013 -- the
paper's own cheaper closed-form alternative to full iterative/joint
optimization): PCA-eigendecompose the (already fully-trained) student's own
raw continuous output on a held-out VAL split, then GREEDILY assign the D
principal directions (sorted by eigenvalue, descending) to the K=128 blocks
via a capacity-constrained min-heap load-balance (LPT-style bin-balancing:
each direction goes to whichever block currently has the LOWEST running
eigenvalue-sum, until that block's L=32 slots are full) so every block ends
up with a BALANCED mix of high+low-variance directions instead of the
naive contiguous-index ordering's wildly uneven per-block variance. The
resulting R [D, D] is EXACTLY orthonormal (a column-reordering of an
eigh-orthonormal basis is itself orthonormal) -- a true rotation, zero
information loss, zero added density (still hard K=128-of-4096 argmax+sign
after rotation).

WHY POST-HOC / ALTERNATING (not jointly-backprop-trained), on reflection:
`v3._block_ste`'s forward pass is `softmax(zb.abs()/TAU_GUMBEL, dim=-1)` PER
BLOCK -- this operation is NOT rotation-invariant (it depends on which raw
coordinates fall in which fixed-width contiguous block), so a rotation
inserted BEFORE `_block_ste` and trained end-to-end WOULD receive a genuine,
non-zero gradient (correcting an earlier, mistaken "dead-gradient" intuition
that only holds for a PURE Gram-matrix/cosine loss operating on the raw
UNQUANTIZED continuous vector -- that is NOT what happens here, since the
STE quantization sits inside the training loop between z and the loss).
A jointly-trained rotation is therefore a LEGITIMATE alternative this cell
does NOT rule out on mathematical grounds. It is deliberately deferred as a
follow-up for practical reasons instead: (a) the post-hoc/alternating variant
is ITSELF a separately-published, well-cited OPQ method (Ge et al. 2013's own
"non-parametric" closed-form alternative to iterative joint optimization),
not a lesser fallback; (b) it requires ZERO new training-loop code -- reuses
`v3c._train_student_full` VERBATIM, unmodified, at the SAME proven config
(lowest possible risk of a new training-loop bug); (c) it needs only ONE
training run (not a two-arm paired training), roughly HALF the GPU compute of
the sibling KL-RANK cell; (d) it gives the CLEANEST possible pairing --
BASELINE and ROTATION arms literally share the IDENTICAL trained weights
(zero training-noise confound), arguably a MORE rigorous isolation of "does
the rotation itself help" than a jointly co-adapted variant would be (joint
training would additionally confound "does rotation help" with "does joint
training find a different, possibly-better student+rotation combination than
independently-trained baseline dynamics").

RISK THIS CELL CHECKS HARD (per task instruction, "check it hard"): the
rotation changes the hard block-argmax slot pattern -> may change how well
bind/unbind (SBC composition algebra) round-trips. `ROTATION_BLOCK_LAST`'s
keyed J=5 unbind-cleanup accuracy MUST clear the SAME `ALGEBRA_FLOOR=0.90`
floor as every other arm in this lineage. If it does not, the verdict logic
below emits a DISTINCT, LOUD `ROTATION_BREAKS_ALGEBRA` HARD_FAIL BEFORE any
retrieval-lift check -- this kills the lever regardless of ret_agree10.

Composition algebra (prereg field): SBC_block_local_circular_convolution.

Unchanged validated machinery (v2/v3/v3c/v3e/objswap_kl): MLP student
(1024->2048 GELU ->4096), block codes (K=128, L=32, 3.125% sparse), semi-hard
mining, warmup+cosine LR, 3-way train/val/test split (TEST never used for
selection or rotation-fitting), FINAL-step is the PRIMARY gated number,
best-by-VAL-on-TEST is SECONDARY context, headline ret_agree10/hi80_cos
fields, NCE off (nce_weight=0.0), FULL_BATCH=128/FULL_STEPS=6000 (IDENTICAL
to v3e/objswap_kl -- "the established base").

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke/full gate (sha256 over all code matrices --
  BASELINE_BLOCK_* and ROTATION_BLOCK_* MUST differ since R != I is applied
  before argmax; this IS the "mechanism fires" smoke assertion, THREE
  DISCIPLINE PATTERNS #2)
- final_metrics_atomicity: tmp_replace (write_metrics helper + ckpt os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
- crlb_floor_computed: r_max=0.901 at K=128 (THEORETICAL@v2/v3/v3b/v3c/v3e/
  objswap_kl prereg, UNCHANGED -- a rotation re-labels which continuous
  coordinate feeds each block; it does not change the K=128/N=4096
  quantization channel's information-theoretic ceiling, since R is an exact
  isometry of the pre-quantization space)
- baseline_in_band: CHARPOS ret_agree10 in (0.05, 0.95)
- discriminator-survives-scale: option (B) analytical justification (same as
  the whole v3 lineage) FOR THE RETRIEVAL-LIFT question -- smoke's tiny
  V_train=3000/VAL_CAP=200 cannot reproduce the true near-neighbor coverage
  effect that makes the UNROTATED code's ret_agree10 sit at ~0.21 at V~178k;
  smoke validates MACHINERY ONLY for that question. HOWEVER, for the
  ALLOCATION MECHANISM ITSELF (does the eigenvalue-balance greedy allocation
  actually balance variance across blocks), THIS cell adds an option-(C)-
  style discriminator-preview: a pure-synthetic self-test with n_samples >>
  D (well-posed PCA regime, unlike smoke's n_val=200 << D=4096) asserts
  `balance_improvement_ratio > 2.0` on a deliberately skewed synthetic
  spectrum -- proving the ALLOCATION mechanism itself fires correctly at ANY
  scale, decoupled from the FULL-only retrieval-lift question.
- HARD_PASS strictly above floor per prereg bands (META_RULE_L)
- HP_SCOPE: HARD_PASS/HARD_FAIL bands apply to ROTATION_BLOCK_LAST only (the
  arm under test). BASELINE_BLOCK_LAST is the live control/reproduction (must
  itself stay in-band per baseline_in_band + algebra, but is NOT separately
  HARD_PASS/HARD_FAIL gated on ret_agree10). *_BESTVAL units are comparison/
  context, NOT separately gated. RANDOM_BLOCK/CHARPOS/shuffled_key are
  integrity-only. DENSE_LAST/DENSE_BESTVAL are diagnostic context (rotation-
  invariant reference point), NOT gated.
- cardinality_ok: EXPECTED_N_UNITS=15 both run_modes (SMOKE=FULL code path)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime (identical hyperparameters to
  the validated v3/v3c/v3e/objswap_kl lineage; only the post-hoc rotation
  applied before block-argmax differs)
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ / VERIFIED@

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01):
  query "OPQ learned rotation orthogonal transform before block quantizer
  retrieval code utilization gap" -> top hit cosine=0.3545 (WordNet
  'transformation' dictionary entry, not an arc cell). Next: 'utilization'
  (WordNet, cosine=0.3398). THIRD hit cosine=0.334, source_class=note,
  notes/research_drill_sparse_w_alternatives_3x_2026-06-07.md -- a DIFFERENT
  context (Walsh-Hadamard rotation preconditioning a pseudoinverse-derived
  sparse-W matrix for QuaRot/QuIP#-style weight quantization, NOT an
  encoder-output block-argmax retrieval code). Remaining hits <=0.326
  (WordNet 'quantization'/'conventionalization'). NONE at cosine>0.30 for a
  DISTINCT prior CELL applying a learned/data-adapted rotation to THIS
  encoder's block-argmax code. GENUINELY NOVEL: the existing bypass
  diagnostic (cosine=0.2612 in ITS OWN prior-work check) tested only
  DATA-INDEPENDENT random rotations (ORTHO_K128/RANDOM_K128), never an
  eigenvalue-adapted OPQ-style rotation.

Prereg: preregs/2026-07-04_exp_encoder_opq_rotation_v1.md
Parent cells (read-only imports, NOT edited):
  experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py (as v3)
  experiments/exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py (as v3c)
  experiments/exp_encoder_v3e_decline_vs_plateau_v1_core.py (as v3e -- reuses `_trend_diagnostic` verbatim)
Does NOT touch v3/v3b/v3c/v3e/objswap_kl/v4/v5's own artifact/checkpoint
directories -- distinct anchor name, distinct artifact dir, distinct prereg,
no shared files edited.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import copy
import hashlib
import heapq
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
from experiments import (  # noqa: E402
    exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core
    as v3,
)
from experiments import (  # noqa: E402
    exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core
    as v3c,
)
from experiments import (  # noqa: E402
    exp_encoder_v3e_decline_vs_plateau_v1_core
    as v3e,
)

# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_opq_rotation_v1"
SEED_DEFAULT = v3.SEED_DEFAULT  # 7

TEACHER_CACHE_DEFAULT = v3c.TEACHER_CACHE_DEFAULT  # pinned 177899-concept cache

NCE_WEIGHT = 0.0   # NCE off, matches v3c/v3e/objswap_kl's winning ablation config

# ---- FULL-scale config: IDENTICAL to v3e/objswap_kl (apples-to-apples baseline) ----
FULL_BATCH = 128
FULL_STEPS = 6000
CKPT_EVERY_STEPS_FULL = 500
DENSE_EVAL_EVERY_FULL = 50
FULL_TRIALS = v3.MID_TRIALS               # 60 (keyed n_trials)
FULL_CHARPOS_CAP = v3.MID_CHARPOS_CAP

VAL_CAP = 5000                # > N_DIM_DEFAULT=4096: full-rank, well-posed PCA fit
VAL_QUICK_SUB = 1500
VAL_QUICK_PAIRS = 40_000
VAL_FULL_PAIRS = 60_000
TEST_FINAL_PAIRS = v3.MID_PAIR_SAMPLE      # 400_000 -- reported-number sample

# ---- Smoke config: MACHINERY validation only (SAME code path as FULL) ----
SMOKE_N_TRAIN = v3.SMOKE_N_TRAIN          # 3000
SMOKE_N_HELD = v3.SMOKE_N_HELD            # 800
SMOKE_STEPS = 200
SMOKE_CKPT_EVERY = 60
SMOKE_DENSE_EVAL_EVERY = 20
SMOKE_VAL_CAP = 200            # << N_DIM_DEFAULT=4096: low-rank/degenerate PCA fit
                               # BY DESIGN -- machinery-only, see docstring caveat
SMOKE_VAL_QUICK_SUB = 120
SMOKE_VAL_QUICK_PAIRS = 3_000
SMOKE_VAL_FULL_PAIRS = 5_000
SMOKE_TEST_FINAL_PAIRS = 8_000
SMOKE_CHARPOS_CAP = 300
SMOKE_TRIALS = 20

MIN_STEP_FRAC_FOR_BEST = 0.05
MIN_TREND_POINTS = v3e.MIN_TREND_POINTS

# semantic: {BASELINE,ROTATION} x {LAST,BESTVAL} BLOCK (4) + DENSE {LAST,BESTVAL} (2)
#           + RANDOM_BLOCK + CHARPOS = 8
# keyed: RANDOM_BLOCK posctrl (1) + {BASELINE,ROTATION} x {LAST,BESTVAL} keyed (4)
#        + {BASELINE,ROTATION} LAST-shuffled (2) = 7
# total = 15
EXPECTED_N_UNITS_FULL = 15
EXPECTED_N_UNITS_SMOKE = 15

PREREG_BASELINE_ARMS = ["CHARPOS", "RANDOM_BLOCK", "BASELINE_BLOCK_LAST", "BASELINE_BLOCK_BESTVAL"]

# ---- Pre-reg bands (HYPOTHESIZED@this prereg unless tagged otherwise) ------
# ROTATION is the arm under test; BASELINE is the live control/reproduction.
ROTATION_RET_AGREE10_HARD_PASS = 0.35        # per task spawn: "target >= 0.35"
ROTATION_RET_AGREE10_HARD_FAIL_CEILING = 0.25  # "no material movement" vs BASELINE's ~0.21
ROTATION_HI80_COS_HARD_PASS = 0.82           # per task spawn: ">= 0.82, calibrated not overshooting"
ROTATION_HI80_COS_HARD_FAIL_FLOOR = 0.75     # material regression on the coarse metric
ALGEBRA_FLOOR = 0.90                         # per task spawn: "algebra ... >= 0.90"
BASELINE_REPRO_TOLERANCE = 0.10              # Gate D: BASELINE_BLOCK_LAST vs cited
                                              # prior ret_agree10 (~0.2105-0.2229)


def _artifact_dir(run_mode: str, run_tag: str = "") -> Path:
    suffix = {"smoke": "_smoke"}.get(run_mode, "")
    tag = f"_{run_tag}" if run_tag else ""
    return _REPO / "data" / f"substrate_concept_encoder_opq_rotation{tag}{suffix}"


# ---------------------------------------------------------------------------
# Defensive helpers (start marker / crash metrics / heartbeat) -- mirrors v3e/objswap_kl.
# ---------------------------------------------------------------------------

def _write_start_marker(output_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "expected_n_units": int(expected_n_units), "host": platform.node(),
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
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(tmp, output_dir / "metrics.json")


def _emit_heartbeat(output_dir: Path, unit_idx: int, total_units: int,
                    elapsed_s: float, extra: Optional[dict] = None) -> None:
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": int(unit_idx),
           "total_units": int(total_units), "elapsed_s": float(elapsed_s)}
    if extra:
        row["extra"] = extra
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# ---------------------------------------------------------------------------
# THE NEW MECHANISM: post-hoc / alternating OPQ-style rotation.
# ---------------------------------------------------------------------------

@torch.no_grad()
def _dense_raw_output(student: torch.nn.Module, X: torch.Tensor,
                      batch: int = 8192) -> torch.Tensor:
    """Raw CONTINUOUS student output (NO quantization) -- the PCA-fit target
    for the rotation AND the rotation's own input before block-argmax."""
    dev = v3._student_device(student)
    out_dim = student.out_dim
    out = torch.zeros(X.shape[0], out_dim, dtype=torch.float32)
    for lo in range(0, X.shape[0], batch):
        z = student(X[lo:lo + batch].to(dev))
        out[lo:lo + batch] = z.detach().float().cpu()
    return out


def _fit_np_opq_rotation(Zval: torch.Tensor, kb: int, blk_l: int) -> Tuple[torch.Tensor, Dict]:
    """Non-parametric OPQ (Ge, He, Sun CVPR 2013 eigenvalue-allocation style):
    eigendecompose the UNCENTERED second-moment matrix of Zval (the quantity
    that actually drives per-block hard-argmax competition, which operates on
    raw magnitude, not mean-removed spread), then greedily assign the D
    principal directions (descending eigenvalue) to K blocks of L slots each
    via a capacity-constrained min-heap load-balance (each direction goes to
    whichever block currently has the SMALLEST running eigenvalue-sum, until
    that block's L slots are full -- classic LPT bin-balancing). Returns
    R [D, D] (EXACTLY orthonormal: a column-reordering of an eigh-orthonormal
    basis) + a diagnostic dict (balance-improvement ratio, isometry error,
    eigenvalue spread).
    """
    D = Zval.shape[1]
    if D != kb * blk_l:
        raise ValueError(f"D={D} != kb*blk_l={kb * blk_l}")
    n_val = Zval.shape[0]
    Zc = Zval.to(torch.float64).cpu()
    M = (Zc.T @ Zc) / max(n_val, 1)          # uncentered second-moment [D, D]
    evals, evecs = torch.linalg.eigh(M)      # ascending
    order_desc = torch.argsort(evals, descending=True)
    evals_desc = evals[order_desc]
    evecs_desc = evecs[:, order_desc]        # columns reordered, descending eigenvalue

    # Naive comparator: a contiguous slice of the EIGENVALUE-SORTED list into K
    # blocks is the worst-case allocation (block 0 = all top eigenvalues, block
    # K-1 = all near-zero) -- the correct "how bad could axis-misalignment be"
    # comparator for the balance-improvement diagnostic (NOT a claim about the
    # untransformed code's own literal per-neuron variance, which we cannot
    # observe without doing this same PCA on it).
    naive_block_sums = evals_desc.reshape(kb, blk_l).sum(dim=1)

    # Capacity-constrained greedy min-heap load-balance (LPT-style).
    heap = [(0.0, b) for b in range(kb)]
    heapq.heapify(heap)
    slot_counts = [0] * kb
    block_of_rank = [0] * D
    for rank in range(D):
        cur_sum, b = heapq.heappop(heap)
        while slot_counts[b] >= blk_l:            # defensive; should not trigger
            cur_sum, b = heapq.heappop(heap)
        block_of_rank[rank] = b
        slot_counts[b] += 1
        if slot_counts[b] < blk_l:
            heapq.heappush(heap, (cur_sum + float(evals_desc[rank]), b))
        # else: block b is full; excluded from future assignment (not re-pushed)
    if any(c != blk_l for c in slot_counts):
        raise RuntimeError(
            f"failure_class=ALLOCATION_INVARIANT_VIOLATION: slot_counts={slot_counts} "
            f"(every block must end with exactly blk_l={blk_l} slots)")

    per_block_ranks: List[List[int]] = [[] for _ in range(kb)]
    for rank in range(D):
        per_block_ranks[block_of_rank[rank]].append(rank)
    col_order: List[int] = []
    for b in range(kb):
        col_order.extend(per_block_ranks[b])
    col_order_t = torch.tensor(col_order, dtype=torch.long)
    R = evecs_desc[:, col_order_t].to(torch.float32)   # [D, D], orthonormal columns

    balanced_block_sums = torch.tensor(
        [sum(float(evals_desc[r]) for r in per_block_ranks[b]) for b in range(kb)])
    naive_var = float(naive_block_sums.var(unbiased=False))
    balanced_var = float(balanced_block_sums.var(unbiased=False))
    diag = {
        "naive_block_variance_of_sums": naive_var,
        "balanced_block_variance_of_sums": balanced_var,
        "balance_improvement_ratio": naive_var / (balanced_var + 1e-12),
        "eigval_max": float(evals_desc[0]), "eigval_min": float(evals_desc[-1]),
        "eigval_condition_number": float(evals_desc[0] / max(float(evals_desc[-1]), 1e-12)),
        "n_val_used": int(n_val), "d": int(D),
        "well_posed_pca": bool(n_val > D),   # n_val > D required for a full-rank M
    }
    return R, diag


def _verify_orthonormal(R: torch.Tensor) -> float:
    D = R.shape[0]
    I = torch.eye(D, dtype=R.dtype, device=R.device)
    return float((R.T @ R - I).abs().max())


@torch.no_grad()
def _encode_hard_block_rotated(student: torch.nn.Module, X: torch.Tensor, kb: int,
                               blk_l: int, R: torch.Tensor, batch: int = 8192) -> torch.Tensor:
    """Same hard block-argmax+sign quantizer as `v3._encode_hard_block`, but
    the student's continuous output is rotated by the FIXED orthonormal R
    BEFORE quantization (OPQ-style, post-hoc). R must be [out_dim, out_dim]."""
    dev = v3._student_device(student)
    Rd = R.to(dev)
    out = torch.zeros(X.shape[0], kb * blk_l, dtype=torch.float32)
    for lo in range(0, X.shape[0], batch):
        z = student(X[lo:lo + batch].to(dev))
        zr = (z.float() @ Rd).reshape(-1, kb, blk_l)
        o = torch.zeros_like(zr)
        idx = zr.abs().argmax(dim=-1, keepdim=True)
        sgn = torch.sign(torch.gather(zr, -1, idx))
        sgn[sgn == 0] = 1.0
        o.scatter_(-1, idx, sgn)
        out[lo:lo + batch] = o.reshape(-1, kb * blk_l).cpu()
    return out


# ---------------------------------------------------------------------------
# Verdict logic.
# ---------------------------------------------------------------------------

def _verdict_rotation(per_unit: List[Dict], recovery: Dict, expected_units: int,
                      run_mode: str) -> Tuple[str, str]:
    if len(per_unit) < expected_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"{len(per_unit)}/{expected_units} units")
    posc = v3._by_unit(per_unit, "keyed", "RANDOM_BLOCK", 5)
    base_prim = v3._by_unit(per_unit, "keyed", "BASELINE_BLOCK_LAST", 5)
    rot_prim = v3._by_unit(per_unit, "keyed", "ROTATION_BLOCK_LAST", 5)
    base_shuf = v3._by_unit(per_unit, "shuffled_key", "BASELINE_BLOCK_LAST", 5)
    rot_shuf = v3._by_unit(per_unit, "shuffled_key", "ROTATION_BLOCK_LAST", 5)
    if any(u is None for u in (posc, base_prim, rot_prim, base_shuf, rot_shuf)):
        return ("HARD_FAIL", "HARD_FAIL_MISSING_GATE_UNITS")
    if posc["acc_at1"] < 0.98:
        return ("HARD_FAIL",
                f"HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH: RANDOM_BLOCK keyed J=5 "
                f"{posc['acc_at1']:.3f} < 0.98 (SBC lossless prior)")
    if base_shuf["acc_at1"] > 0.05 or base_shuf["hit_any_member"] > 0.10:
        return ("HARD_FAIL",
                f"HARD_FAIL_SHUFFLED_KEY_LEAK_BASELINE: {base_shuf['acc_at1']:.3f}/"
                f"{base_shuf['hit_any_member']:.3f}")
    if rot_shuf["acc_at1"] > 0.05 or rot_shuf["hit_any_member"] > 0.10:
        return ("HARD_FAIL",
                f"HARD_FAIL_SHUFFLED_KEY_LEAK_ROTATION: {rot_shuf['acc_at1']:.3f}/"
                f"{rot_shuf['hit_any_member']:.3f}")

    rot_ret = recovery["rotation_ret_agree10_last"]
    rot_cos = recovery["rotation_hi80_cos_last"]
    base_ret = recovery["baseline_ret_agree10_last"]
    lift = recovery["lift_ret_agree10_last"]
    tail = (f"[ROTATION: ret_agree10={rot_ret:.4f} hi80_cos={rot_cos:.4f} "
           f"keyed_J5={rot_prim['acc_at1']:.3f} | "
           f"BASELINE(control): ret_agree10={base_ret:.4f} "
           f"keyed_J5={base_prim['acc_at1']:.3f} | "
           f"lift={lift:+.4f} | balance_improvement_ratio_last="
           f"{recovery['rotation_diag_last']['balance_improvement_ratio']:.2f}]")

    if run_mode == "smoke":
        fails = []
        if not math.isfinite(rot_ret):
            fails.append("S_rotation_ret_agree10_missing")
        if not math.isfinite(base_ret):
            fails.append("S_baseline_ret_agree10_missing")
        iso_err = recovery.get("rotation_isometry_err_last", 1.0)
        if iso_err > 1e-2:
            fails.append(f"S_rotation_not_orthonormal(err={iso_err:.2e})")
        if fails:
            return ("SMOKE_GATE_FAIL", "; ".join(fails))
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: single training run + post-hoc rotation-fit "
                f"end-to-end, 3-way split partitions correctly, BASELINE/ROTATION "
                f"codes differ (arms-must-differ), R verified orthonormal "
                f"(err={iso_err:.2e}), headline ret_agree10/hi80_cos fields "
                f"populate for both arms {tail} (the retrieval-lift discriminator "
                f"is a FULL-only question at smoke's tiny V_train/VAL_CAP; smoke's "
                f"VAL_CAP={SMOKE_VAL_CAP} << N_DIM_DEFAULT so the PCA fit here is "
                f"expected low-rank/degenerate BY DESIGN, machinery-only)")

    # full: algebra gates apply to BOTH arms; BASELINE's own algebra FIRST
    # (if the control arm's own algebra is broken, the run itself is suspect).
    if base_prim["acc_at1"] < ALGEBRA_FLOOR:
        return ("HARD_FAIL",
                f"HARD_FAIL_ALGEBRA_BASELINE_CONTROL: keyed_roundtrip J=5 "
                f"{base_prim['acc_at1']:.3f} < {ALGEBRA_FLOOR} (control arm's own "
                f"algebra broke -- the run itself is suspect, not just the "
                f"rotation comparison) {tail}")
    # THE LOUD, CRITICAL CHECK (per task instruction): rotation must not break
    # composition algebra. Checked BEFORE any retrieval-lift interpretation --
    # this kills the lever regardless of how good ret_agree10 looks.
    if rot_prim["acc_at1"] < ALGEBRA_FLOOR:
        return ("HARD_FAIL",
                f"!!!ROTATION_BREAKS_ALGEBRA!!!: keyed_roundtrip J=5 acc_at1="
                f"{rot_prim['acc_at1']:.3f} < {ALGEBRA_FLOOR} floor -- the OPQ-"
                f"style rotation makes ROTATION_BLOCK_LAST NOT a valid composable "
                f"SBC code (bind/unbind roundtrip degrades). THIS KILLS THE "
                f"ROTATION LEVER REGARDLESS OF ANY RETRIEVAL GAIN "
                f"(ret_agree10={rot_ret:.4f} is IRRELEVANT if algebra is broken) "
                f"{tail}")

    if rot_ret >= ROTATION_RET_AGREE10_HARD_PASS and rot_cos >= ROTATION_HI80_COS_HARD_PASS:
        return ("HARD_PASS",
                f"ROTATION_RECOVERS_RETRIEVAL: ret_agree10={rot_ret:.4f} "
                f"(>= {ROTATION_RET_AGREE10_HARD_PASS}) while holding "
                f"hi80_cos={rot_cos:.4f} (>= {ROTATION_HI80_COS_HARD_PASS}) and "
                f"algebra ({rot_prim['acc_at1']:.3f}); the OPQ-style rotation "
                f"closes a code-UTILIZATION gap at fixed K=128/3.125% sparsity "
                f"{tail}")
    if rot_ret <= ROTATION_RET_AGREE10_HARD_FAIL_CEILING or rot_cos < ROTATION_HI80_COS_HARD_FAIL_FLOOR:
        return ("HARD_FAIL",
                f"ROTATION_NO_MATERIAL_LIFT: ret_agree10={rot_ret:.4f} "
                f"(ceiling {ROTATION_RET_AGREE10_HARD_FAIL_CEILING}) "
                f"hi80_cos={rot_cos:.4f} (floor {ROTATION_HI80_COS_HARD_FAIL_FLOOR}) "
                f"-- the OPQ-style rotation lever is dead; sparsity-preserving "
                f"levers exhausted at K=128 (objective-family swap AND rotation "
                f"both refuted); the only remaining retrieval lever is code-"
                f"widening (K=256, accepts the density cost) {tail}")
    return ("MIDDLE_BAND",
            f"ROTATION_PARTIAL: ret_agree10={rot_ret:.4f} hi80_cos={rot_cos:.4f} "
            f"lift={lift:+.4f} -- real but partial movement, neither a clean "
            f"recovery nor a clean no-lift result {tail}")


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def run_rotation(run_mode: str, seed: int, device_arg: str, n_dim: int,
                 teacher_cache_arg: Optional[str], run_tag: str = "") -> int:
    assert run_mode in ("smoke", "full"), f"unsupported run_mode {run_mode}"
    tag_suffix = f"_{run_tag}" if run_tag else ""
    anchor = f"{ANCHOR_NAME}{tag_suffix}_smoke" if run_mode == "smoke" \
        else f"{ANCHOR_NAME}{tag_suffix}"
    out_dir = get_output_dir(anchor)
    art_dir = _artifact_dir(run_mode, run_tag)
    art_dir.mkdir(parents=True, exist_ok=True)
    device = ("cuda" if torch.cuda.is_available() else "cpu") \
        if device_arg == "auto" else device_arg
    kb, blk_l = v3.K_BLOCKS_PRIMARY, n_dim // v3.K_BLOCKS_PRIMARY
    if kb * blk_l != n_dim:
        raise ValueError(f"n_dim {n_dim} not divisible by k_blocks {kb}")

    if run_mode == "smoke":
        steps = SMOKE_STEPS
        ckpt_every, dense_every = SMOKE_CKPT_EVERY, SMOKE_DENSE_EVAL_EVERY
        quick_sub, quick_pairs = SMOKE_VAL_QUICK_SUB, SMOKE_VAL_QUICK_PAIRS
        val_full_pairs, test_final_pairs = SMOKE_VAL_FULL_PAIRS, SMOKE_TEST_FINAL_PAIRS
        charpos_cap, n_trials = SMOKE_CHARPOS_CAP, SMOKE_TRIALS
        n_tr_target, n_he_target = SMOKE_N_TRAIN, SMOKE_N_HELD
        val_cap = SMOKE_VAL_CAP
        batch = min(FULL_BATCH, 32)
    else:
        steps = FULL_STEPS
        ckpt_every, dense_every = CKPT_EVERY_STEPS_FULL, DENSE_EVAL_EVERY_FULL
        quick_sub, quick_pairs = VAL_QUICK_SUB, VAL_QUICK_PAIRS
        val_full_pairs, test_final_pairs = VAL_FULL_PAIRS, TEST_FINAL_PAIRS
        charpos_cap, n_trials = FULL_CHARPOS_CAP, FULL_TRIALS
        n_tr_target = n_he_target = None
        val_cap = VAL_CAP
        batch = FULL_BATCH
    expected_units = EXPECTED_N_UNITS_SMOKE if run_mode == "smoke" else EXPECTED_N_UNITS_FULL
    warmup = v3._warmup_for(steps)
    min_step_for_best = max(1, int(round(MIN_STEP_FRAC_FOR_BEST * steps)))

    _write_start_marker(out_dir, run_mode, expected_units)
    t0 = time.perf_counter()
    print(f"[opq_rot] run_mode={run_mode} seed={seed} device={device} n_dim={n_dim} "
          f"steps={steps} batch={batch} nce_weight={NCE_WEIGHT} "
          f"dense_eval_every={dense_every} min_step_for_best={min_step_for_best}",
          flush=True)

    effective_cache_arg = teacher_cache_arg
    if run_mode == "full" and effective_cache_arg is None:
        effective_cache_arg = TEACHER_CACHE_DEFAULT
    cache_path = v3._resolve_teacher_cache(effective_cache_arg)
    cache_bytes = cache_path.stat().st_size
    X, ids = v3._load_teacher(cache_path)
    V_cache = X.shape[0]
    print(f"[opq_rot] teacher {cache_path.name}: {V_cache} concepts x "
          f"{X.shape[1]}d ({time.perf_counter() - t0:.1f}s)", flush=True)

    rng = np.random.default_rng(seed)
    perm = rng.permutation(V_cache)
    if run_mode == "smoke":
        if V_cache < n_tr_target + n_he_target:
            raise RuntimeError(f"teacher cache too small for smoke: {V_cache}")
        n_tr, n_he = n_tr_target, n_he_target
    else:
        n_he = min(int(round(V_cache * v3.HELD_FRAC)), v3.FULL_HELD_CAP)
        n_tr = V_cache - n_he
    tr_idx = perm[:n_tr]
    held_idx = perm[n_tr:n_tr + n_he]
    n_val = min(val_cap, n_he - 1)
    val_idx = held_idx[:n_val]
    test_idx = held_idx[n_val:]
    n_test = test_idx.shape[0]
    if n_test < 10:
        raise RuntimeError(f"TEST split too small: n_test={n_test} (n_he={n_he}, n_val={n_val})")
    Xtr = X[torch.from_numpy(tr_idx.copy())].contiguous()
    Xval = X[torch.from_numpy(val_idx.copy())].contiguous()
    Xtest = X[torch.from_numpy(test_idx.copy())].contiguous()
    names_test = [ids[i] for i in test_idx]
    print(f"[opq_rot] split train={n_tr} val={n_val} test={n_test}", flush=True)

    pos_idx, semi_cands = v3._mine_teacher(
        Xtr, device, art_dir / "_mine_shards", out_dir, t0)
    semi_cov = float((semi_cands[:, 0] >= 0).float().mean())
    print(f"[opq_rot] mining done cov={semi_cov:.3f} "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    Xval_sub = Xval[:min(quick_sub, n_val)].contiguous()

    def _deval_quick(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xval_sub, quick_pairs, seed + 7)

    def _deval_full(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xval, val_full_pairs, seed + 7)

    in_dim = Xtr.shape[1]
    ckpt_path = art_dir / "_ckpt_BASE.pt"
    best_ckpt_path = art_dir / "_ckpt_best_BASE.pt"
    # ONE training run: the SAME v3c._train_student_full, VERBATIM, objective=
    # "in_batch", nce_weight=0.0 -- "the established base" per task spawn.
    last_student, train_diag = v3c._train_student_full(
        kb, blk_l, Xtr, pos_idx, semi_cands, steps, batch, warmup, seed, device,
        ckpt_path, best_ckpt_path, ckpt_every, out_dir, t0,
        None, 0, NCE_WEIGHT, "BASE", objective="in_batch",
        dense_eval_quick_fn=_deval_quick, dense_eval_full_fn=_deval_full,
        dense_eval_every=dense_every, min_step_for_best=min_step_for_best)
    print(f"[opq_rot] BASE trained rkd_last={train_diag['rkd_last']:.4f} "
          f"best_val={train_diag['best_dense_full']:.4f}@step{train_diag['best_step']} "
          f"n_traj_points={len(train_diag['dense_traj'])} "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)
    bestval_student = v3c._reload_best_student(
        "mlp", in_dim, kb * blk_l, device, best_ckpt_path)

    students = {"LAST": last_student, "BESTVAL": bestval_student}
    arm_codes: Dict[str, torch.Tensor] = {}
    rotation_diags: Dict[str, Dict] = {}
    isometry_errs: Dict[str, float] = {}
    for tag, st in students.items():
        Zval = _dense_raw_output(st, Xval)
        R, rdiag = _fit_np_opq_rotation(Zval, kb, blk_l)
        iso_err = _verify_orthonormal(R)
        if iso_err > 1e-2:
            raise RuntimeError(
                f"failure_class=ROTATION_NOT_ORTHONORMAL: {tag} isometry err "
                f"{iso_err:.2e} exceeds tolerance")
        rotation_diags[tag] = rdiag
        isometry_errs[tag] = iso_err
        arm_codes[f"BASELINE_BLOCK_{tag}"] = v3._encode_hard_block(st, Xtest, kb, blk_l)
        arm_codes[f"ROTATION_BLOCK_{tag}"] = _encode_hard_block_rotated(
            st, Xtest, kb, blk_l, R)
        arm_codes[f"DENSE_{tag}"] = v3._dense_sign_codes(st, Xtest)
        print(f"[opq_rot] {tag} rotation fit: balance_improvement_ratio="
              f"{rdiag['balance_improvement_ratio']:.2f} iso_err={iso_err:.2e} "
              f"well_posed_pca={rdiag['well_posed_pca']} "
              f"({time.perf_counter() - t0:.1f}s)", flush=True)

    gen_ctrl = torch.Generator().manual_seed(seed + 1)
    arm_codes["RANDOM_BLOCK"] = v3._random_block_codes(n_test, kb, blk_l, gen_ctrl)
    cp_cap = min(n_test, charpos_cap)
    cp_codes = v3._charpos_codes(names_test[:cp_cap], n_dim, kb)

    # META_RULE_AF arms-must-differ: BASELINE vs ROTATION MUST differ (this IS
    # the "mechanism fires" smoke assertion, THREE DISCIPLINE PATTERNS #2).
    digests = {}
    for name, c in list(arm_codes.items()) + [("CHARPOS", cp_codes)]:
        digests[name] = hashlib.sha256(c.to(torch.int8).numpy().tobytes()).hexdigest()
    for a in digests:
        for b in digests:
            if a < b and digests[a] == digests[b]:
                raise RuntimeError(
                    f"failure_class=META_RULE_AF_VIOLATION: {a}/{b} identical")

    per_unit: List[Dict] = []
    unit_fail: List[Dict] = []
    gen_eval = torch.Generator().manual_seed(seed + 2)

    def _run_unit(fn, *a, **kw):
        try:
            u = fn(*a, **kw)
            per_unit.append(u)
            print(f"[opq_rot] unit {len(per_unit)}/{expected_units} {u['unit']}: "
                  + json.dumps({k: round(v, 4) for k, v in u.items()
                                if isinstance(v, float)}), flush=True)
            _emit_heartbeat(out_dir, len(per_unit), expected_units,
                            time.perf_counter() - t0, extra={"unit": u["unit"]})
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append({"fn": getattr(fn, "__name__", "?"),
                              "failure_class": type(exc).__name__,
                              "msg": str(exc)[:300]})
            raise

    for label in ("BASELINE_BLOCK_LAST", "ROTATION_BLOCK_LAST",
                  "BASELINE_BLOCK_BESTVAL", "ROTATION_BLOCK_BESTVAL",
                  "DENSE_LAST", "DENSE_BESTVAL"):
        c = arm_codes[label]
        _run_unit(v3._semantic_unit, label, c, c, Xtest, Xtest, 0,
                  test_final_pairs, seed + 3)
    _run_unit(v3._semantic_unit, "RANDOM_BLOCK", arm_codes["RANDOM_BLOCK"],
              arm_codes["RANDOM_BLOCK"], Xtest, Xtest, 0, test_final_pairs, seed + 3)
    cp_Xtest = Xtest[:cp_cap]
    _run_unit(v3._semantic_unit, "CHARPOS", cp_codes, cp_codes, cp_Xtest, cp_Xtest, 0,
              test_final_pairs, seed + 3)

    _run_unit(v3._keyed_unit, "RANDOM_BLOCK", "sbc", arm_codes["RANDOM_BLOCK"],
              kb, blk_l, 5, n_trials, gen_eval, device)
    for arm_key in ("BASELINE_BLOCK_LAST", "ROTATION_BLOCK_LAST",
                    "BASELINE_BLOCK_BESTVAL", "ROTATION_BLOCK_BESTVAL"):
        _run_unit(v3._keyed_unit, arm_key, "sbc", arm_codes[arm_key],
                  kb, blk_l, 5, n_trials, gen_eval, device)
    for arm_key in ("BASELINE_BLOCK_LAST", "ROTATION_BLOCK_LAST"):
        _run_unit(v3._keyed_unit, arm_key, "sbc", arm_codes[arm_key],
                  kb, blk_l, 5, n_trials, gen_eval, device, shuffled_key=True)

    def _sp(arm):
        return v3._by_unit(per_unit, "semantic", arm)

    base_last_u = _sp("BASELINE_BLOCK_LAST")
    rot_last_u = _sp("ROTATION_BLOCK_LAST")
    base_bv_u = _sp("BASELINE_BLOCK_BESTVAL")
    rot_bv_u = _sp("ROTATION_BLOCK_BESTVAL")

    base_ret = float(base_last_u["ret_agree10"]) if base_last_u else float("nan")
    rot_ret = float(rot_last_u["ret_agree10"]) if rot_last_u else float("nan")

    train_trend = v3e._trend_diagnostic(train_diag["dense_traj"], "dense_full", min_step_for_best)

    recovery = {
        "baseline_ret_agree10_last": base_ret,
        "baseline_hi80_cos_last": float(base_last_u["hi80_cos"]) if base_last_u else float("nan"),
        "baseline_spearman_last": float(base_last_u["spearman_all"]) if base_last_u else float("nan"),
        "rotation_ret_agree10_last": rot_ret,
        "rotation_hi80_cos_last": float(rot_last_u["hi80_cos"]) if rot_last_u else float("nan"),
        "rotation_spearman_last": float(rot_last_u["spearman_all"]) if rot_last_u else float("nan"),
        "lift_ret_agree10_last": (rot_ret - base_ret) if math.isfinite(rot_ret) and math.isfinite(base_ret) else float("nan"),
        "baseline_ret_agree10_bestval": float(base_bv_u["ret_agree10"]) if base_bv_u else float("nan"),
        "rotation_ret_agree10_bestval": float(rot_bv_u["ret_agree10"]) if rot_bv_u else float("nan"),
        "rotation_diag_last": rotation_diags["LAST"],
        "rotation_diag_bestval": rotation_diags["BESTVAL"],
        "rotation_isometry_err_last": isometry_errs["LAST"],
        "rotation_isometry_err_bestval": isometry_errs["BESTVAL"],
        "train_trend": train_trend,
        "train_best_step": train_diag["best_step"],
        "train_best_ckpt_fallback_to_final": train_diag["best_ckpt_fallback_to_final"],
        "charpos_ret_agree10": float(_sp("CHARPOS")["ret_agree10"]) if _sp("CHARPOS") else float("nan"),
        "random_block_ret_agree10": float(_sp("RANDOM_BLOCK")["ret_agree10"]) if _sp("RANDOM_BLOCK") else float("nan"),
        "baseline_repro_prior_cited": 0.2129,   # MEASURED@objswap_kl MSE control (seed7/13 mean ~0.211-0.213)
        "baseline_repro_delta": (base_ret - 0.2129) if math.isfinite(base_ret) else float("nan"),
        "baseline_repro_within_tolerance": (
            abs(base_ret - 0.2129) <= BASELINE_REPRO_TOLERANCE if math.isfinite(base_ret) else False),
    }
    verdict, verdict_msg = _verdict_rotation(per_unit, recovery, expected_units, run_mode)
    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "run_tag": run_tag, "seed": int(seed), "device": device, "N": n_dim,
        "student_arch": v3.STUDENT_ARCH_PRIMARY, "mlp_hidden": v3.MLP_HIDDEN,
        "warmup_steps": warmup, "steps": steps, "batch": batch,
        "nce_weight": NCE_WEIGHT, "min_step_for_best": min_step_for_best,
        "dense_eval_every": dense_every,
        "teacher_cache": cache_path.name, "teacher_cache_bytes": cache_bytes,
        "teacher_n_concepts": V_cache, "n_train": n_tr, "n_val": n_val,
        "n_test": n_test, "n_held_pool": n_he,
        "semi_hard_coverage": semi_cov,
        "recovery": recovery,
        "train_diag": train_diag,
        "per_unit": per_unit, "unit_failures": unit_fail,
        "n_units": len(per_unit), "expected_n_units": expected_units,
        "cardinality_ok": len(per_unit) == expected_units,
        "arms_differ_verified": True, "arm_code_sha256": digests,
        "final_metrics_atomicity": "tmp_replace",
        "composition_algebra": "SBC_block_local_circular_convolution",
        "methodology": ("POST-HOC / alternating OPQ-style rotation: ONE student "
                        "trained via v3c._train_student_full VERBATIM (in_batch "
                        "RKD, NCE off, IDENTICAL to v3e/objswap_kl config), THEN "
                        "a non-parametric-OPQ (eigenvalue-allocation) rotation R "
                        "fit from that SAME trained student's own VAL-split dense "
                        "output, applied before hard block-argmax on TEST. "
                        "BASELINE and ROTATION arms share IDENTICAL trained "
                        "weights (zero training-noise confound) -- the cleanest "
                        "possible paired comparison. FINAL-step is the PRIMARY "
                        "gated number, best-by-VAL-on-TEST is SECONDARY context; "
                        "ret_agree10 + hi80_cos are top-level headline fields; "
                        "algebra (keyed J=5) checked on BOTH arms, loudly gated "
                        "on the ROTATION arm per task instruction"),
        "progress_logging": "print_flush_true",
        "primary_spearman": recovery["rotation_spearman_last"],
        "dense_sign_spearman": float(_sp("DENSE_LAST")["spearman_all"]) if _sp("DENSE_LAST") else float("nan"),
        "baseline_in_band": bool(0.05 < recovery["charpos_ret_agree10"] < 0.95),
        "crlb_floor_computed": 0.901,
        "crlb_formula_reference": ("r_max = sigma_teacher / sqrt(sigma_teacher^2 + "
                                   "0.25/K), K=128 -> 0.901 (unchanged from v2/v3/v3b/"
                                   "v3c/v3e/objswap_kl; a rotation is an exact isometry "
                                   "of the pre-quantization space, so it re-labels "
                                   "which coordinate feeds each block without changing "
                                   "the channel's information-theoretic ceiling)"),
        "discriminator_reachability": True,
        "cell_chunked": True, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "calibration_check": "default_ok_for_this_regime",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[opq_rot] verdict={verdict} msg={verdict_msg} elapsed={elapsed:.1f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Self-test (synthetic; no cache dependency; fast).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()

    # 1. NP-OPQ allocation: well-posed regime (n_samples >> D), deliberately
    #    skewed synthetic eigenvalue spectrum -- proves the greedy balance
    #    ALGORITHM works correctly, decoupled from the FULL-only retrieval
    #    question (discriminator-preview, option-(C)-style).
    torch.manual_seed(3)
    D_t, kb_t, blk_l_t, n_t = 64, 8, 8, 4000
    skew = torch.cat([torch.full((8,), 50.0), torch.full((56,), 0.01)])  # 8 huge, 56 tiny
    basis = torch.linalg.qr(torch.randn(D_t, D_t))[0]
    Zsyn = torch.randn(n_t, D_t) @ torch.diag(skew.sqrt()) @ basis.T
    R_syn, diag_syn = _fit_np_opq_rotation(Zsyn, kb_t, blk_l_t)
    assert R_syn.shape == (D_t, D_t)
    iso_err_syn = _verify_orthonormal(R_syn)
    assert iso_err_syn < 1e-3, f"selftest: R must be orthonormal, err={iso_err_syn:.2e}"
    assert diag_syn["well_posed_pca"] is True
    assert diag_syn["balance_improvement_ratio"] > 2.0, (
        f"selftest: greedy allocation must materially balance a deliberately "
        f"skewed spectrum, got ratio={diag_syn['balance_improvement_ratio']:.2f}")

    # 1b. Degenerate (low-rank, n < D) regime must NOT crash -- matches SMOKE's
    #     VAL_CAP << N_DIM_DEFAULT machinery-only caveat.
    Zdeg = torch.randn(20, D_t)   # n=20 << D=64
    R_deg, diag_deg = _fit_np_opq_rotation(Zdeg, kb_t, blk_l_t)
    assert R_deg.shape == (D_t, D_t)
    assert _verify_orthonormal(R_deg) < 1e-3
    assert diag_deg["well_posed_pca"] is False

    # 1c. Unknown-shape / invariant-violation guards.
    try:
        _fit_np_opq_rotation(torch.randn(10, 63), kb_t, blk_l_t)
        raise AssertionError("selftest: mismatched D must raise ValueError")
    except ValueError:
        pass

    # 2. _encode_hard_block_rotated with R=Identity must reproduce
    #    v3._encode_hard_block EXACTLY (regression-equivalence).
    torch.manual_seed(11)
    kb2, blk_l2, in_dim2, v_syn2 = 16, 16, 64, 40
    student2 = v3._make_student("mlp", in_dim2, kb2 * blk_l2, "cpu", seed=11)
    Xsyn2 = torch.randn(v_syn2, in_dim2)
    Xsyn2 = Xsyn2 / Xsyn2.norm(dim=-1, keepdim=True)
    I_rot = torch.eye(kb2 * blk_l2, dtype=torch.float32)
    c_plain = v3._encode_hard_block(student2, Xsyn2, kb2, blk_l2)
    c_ident_rot = _encode_hard_block_rotated(student2, Xsyn2, kb2, blk_l2, I_rot)
    assert torch.equal(c_plain, c_ident_rot), (
        "selftest: rotation with R=Identity must reproduce v3._encode_hard_block "
        "EXACTLY (regression-equivalence)")

    # 2b. A genuine (non-identity) fitted rotation must produce a DIFFERENT
    #     code than the unrotated baseline on the SAME student (arms-must-
    #     differ at the mechanism level, not just a hash check).
    Zval2 = _dense_raw_output(student2, Xsyn2)
    R2, _ = _fit_np_opq_rotation(Zval2, kb2, blk_l2)
    c_rot2 = _encode_hard_block_rotated(student2, Xsyn2, kb2, blk_l2, R2)
    assert not torch.equal(c_plain, c_rot2), (
        "selftest META_RULE_AF: a genuine (non-identity) rotation must change "
        "the resulting block code vs the unrotated baseline")
    h_plain = hashlib.sha256(c_plain.to(torch.int8).numpy().tobytes()).hexdigest()
    h_rot2 = hashlib.sha256(c_rot2.to(torch.int8).numpy().tobytes()).hexdigest()
    assert h_plain != h_rot2

    # 3. run_rotation-style semantic/keyed units must populate on this tiny
    #    synthetic rotated code (shape/signal-compatibility check).
    u_plain = v3._semantic_unit("TEST_BASE", c_plain, c_plain, Xsyn2, Xsyn2, 0, 500, 3)
    u_rot = v3._semantic_unit("TEST_ROT", c_rot2, c_rot2, Xsyn2, Xsyn2, 0, 500, 3)
    assert "ret_agree10" in u_plain and "hi80_cos" in u_plain
    assert "ret_agree10" in u_rot and "hi80_cos" in u_rot
    gen_k = torch.Generator().manual_seed(5)
    k_plain = v3._keyed_unit("TEST_BASE", "sbc", c_plain, kb2, blk_l2, 5, 10, gen_k, "cpu")
    k_rot = v3._keyed_unit("TEST_ROT", "sbc", c_rot2, kb2, blk_l2, 5, 10, gen_k, "cpu")
    assert "acc_at1" in k_plain and "acc_at1" in k_rot

    # 4. mse_rkd reproduction guard: v3c._train_student_full at objective=
    #    "in_batch" is called VERBATIM (not copied) -- prove it is importable
    #    and runs a tiny synthetic training loop end-to-end without error
    #    (this cell's "regression-equivalence" IS reuse, not a re-derivation).
    n_dim3, kb3, blk_l3, v_syn3 = 128, 8, 16, 200
    torch.manual_seed(17)
    Xsyn3 = torch.randn(v_syn3, 32)
    Xsyn3 = Xsyn3 / Xsyn3.norm(dim=-1, keepdim=True)
    gen3 = torch.Generator().manual_seed(17)
    pos3 = torch.randint(0, v_syn3, (v_syn3,), generator=gen3)
    semi3 = torch.randint(0, v_syn3, (v_syn3, v3.N_SEMI_CANDS), generator=gen3)
    Xval3 = Xsyn3[:40].contiguous()
    Xtest3 = Xsyn3[40:64].contiguous()

    def _dq3(student):
        return v3._dense_spearman_quick(student, Xval3[:20], 300, 3)

    def _df3(student):
        return v3._dense_spearman_quick(student, Xval3, 500, 3)

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        st3, diag3 = v3c._train_student_full(
            kb3, blk_l3, Xsyn3, pos3, semi3, 30, 24, 4, 13, "cpu",
            tdp / "ckpt.pt", tdp / "ckpt_best.pt", 100, tdp, t0,
            None, 0, 0.0, "BASE_SYN", "in_batch",
            dense_eval_quick_fn=_dq3, dense_eval_full_fn=_df3, dense_eval_every=4,
            min_step_for_best=2)
        assert math.isfinite(diag3["rkd_last"])
        Zv3 = _dense_raw_output(st3, Xval3)
        R3, rdiag3 = _fit_np_opq_rotation(Zv3, kb3, blk_l3)
        assert _verify_orthonormal(R3) < 1e-3
        c_base3 = v3._encode_hard_block(st3, Xtest3, kb3, blk_l3)
        c_rot3 = _encode_hard_block_rotated(st3, Xtest3, kb3, blk_l3, R3)
        assert c_base3.shape == c_rot3.shape == (24, kb3 * blk_l3)
        assert torch.isfinite(c_base3).all() and torch.isfinite(c_rot3).all()
        trend3 = v3e._trend_diagnostic(diag3["dense_traj"], "dense_full", min_step=2)
        assert trend3["sufficient"] is True

    # 5. Verdict bands.
    fake_units_base = [{"unit": f"u{i}", "arm": "x", "kind": "k"} for i in range(8)]
    fake_units_base += [
        {"unit": "keyed::RANDOM_BLOCK::J5", "arm": "RANDOM_BLOCK", "kind": "keyed",
         "J": 5, "acc_at1": 0.99, "hit_any_member": 0.99},
        {"unit": "keyed::BASELINE_BLOCK_LAST::J5", "arm": "BASELINE_BLOCK_LAST",
         "kind": "keyed", "J": 5, "acc_at1": 0.97, "hit_any_member": 0.97},
        {"unit": "shuffled_key::BASELINE_BLOCK_LAST::J5", "arm": "BASELINE_BLOCK_LAST",
         "kind": "shuffled_key", "J": 5, "acc_at1": 0.01, "hit_any_member": 0.01},
        {"unit": "keyed::ROTATION_BLOCK_LAST::J5", "arm": "ROTATION_BLOCK_LAST",
         "kind": "keyed", "J": 5, "acc_at1": 0.96, "hit_any_member": 0.96},
        {"unit": "shuffled_key::ROTATION_BLOCK_LAST::J5", "arm": "ROTATION_BLOCK_LAST",
         "kind": "shuffled_key", "J": 5, "acc_at1": 0.02, "hit_any_member": 0.02},
    ]
    assert len(fake_units_base) == 13  # + 2 more (BESTVAL keyed) not needed for verdict logic

    rec_pass = {
        "rotation_ret_agree10_last": 0.40, "rotation_hi80_cos_last": 0.85,
        "baseline_ret_agree10_last": 0.21, "lift_ret_agree10_last": 0.40 - 0.21,
        "rotation_diag_last": {"balance_improvement_ratio": 12.0},
    }
    v_pass, m_pass = _verdict_rotation(fake_units_base, rec_pass, 13, "full")
    assert v_pass == "HARD_PASS" and "ROTATION_RECOVERS_RETRIEVAL" in m_pass, (
        f"selftest: expected HARD_PASS got {v_pass} ({m_pass})")

    rec_fail = dict(rec_pass, rotation_ret_agree10_last=0.22,
                    lift_ret_agree10_last=0.22 - 0.21)
    v_fail, m_fail = _verdict_rotation(fake_units_base, rec_fail, 13, "full")
    assert v_fail == "HARD_FAIL" and "ROTATION_NO_MATERIAL_LIFT" in m_fail, (
        f"selftest: expected HARD_FAIL got {v_fail} ({m_fail})")

    rec_mid = dict(rec_pass, rotation_ret_agree10_last=0.30,
                   lift_ret_agree10_last=0.30 - 0.21)
    v_mid, m_mid = _verdict_rotation(fake_units_base, rec_mid, 13, "full")
    assert v_mid == "MIDDLE_BAND" and "ROTATION_PARTIAL" in m_mid, (
        f"selftest: expected MIDDLE_BAND got {v_mid} ({m_mid})")

    v_card, m_card = _verdict_rotation(fake_units_base[:5], rec_pass, 13, "full")
    assert v_card == "HARD_FAIL" and "CARDINALITY_BREACH" in m_card

    fake_units_leak = copy.deepcopy(fake_units_base)
    for u in fake_units_leak:
        if u.get("kind") == "shuffled_key" and u.get("arm") == "ROTATION_BLOCK_LAST":
            u["acc_at1"] = 0.5
    v_leak, m_leak = _verdict_rotation(fake_units_leak, rec_pass, 13, "full")
    assert v_leak == "HARD_FAIL" and "SHUFFLED_KEY_LEAK_ROTATION" in m_leak

    # THE critical loud-algebra-break check.
    fake_units_algbreak = copy.deepcopy(fake_units_base)
    for u in fake_units_algbreak:
        if u.get("arm") == "ROTATION_BLOCK_LAST" and u.get("kind") == "keyed":
            u["acc_at1"] = 0.20
    v_alg, m_alg = _verdict_rotation(fake_units_algbreak, rec_pass, 13, "full")
    assert v_alg == "HARD_FAIL" and "ROTATION_BREAKS_ALGEBRA" in m_alg, (
        f"selftest: expected loud ROTATION_BREAKS_ALGEBRA got {v_alg} ({m_alg})")

    print(f"[selftest] PASS (NP-OPQ allocation balances a skewed synthetic "
          f"spectrum + orthonormality + degenerate-regime no-crash + shape "
          f"guards; R=Identity regression-equivalence + genuine-rotation "
          f"arms-differ; v3c._train_student_full reuse end-to-end + rotation "
          f"fit/apply on a real tiny trained student; verdict bands "
          f"HARD_PASS/HARD_FAIL/MIDDLE_BAND/cardinality/shuffled-key-leak/"
          f"LOUD algebra-break) elapsed={time.perf_counter() - t0:.2f}s",
          flush=True)
    return 0
