"""Encoder v6 -- K=128 annealed-STE gradient-FIDELITY (lever B, PRIMARY) vs
hard-STE control, with a capacity secondary arm and a FREE train-loss capacity
diagnostic. Closes the trained-vs-code-ceiling retrieval gap at fixed 2%-sparse.

THE FINDING THIS CELL PROBES (verified from disk, not summarized):
  MEASURED@data/exp_encoder_teacher_sparsifier_bypass_v1/metrics.json:
    /recovery/ortho_k128_ret_agree10 = 0.4295278  (CODE CEILING at K128 --
      teacher vectors through the SAME block sparsifier, ZERO training error)
    /recovery/random_k128_ret_agree10 = 0.4248791  (ortho-vs-random +0.0047 ->
      OPQ rotation is DEAD for retrieval)
  MEASURED@data/exp_encoder_v3e_decline_vs_plateau_v1_seed7/metrics.json:
    trained student (hard block-argmax STE, hidden=2048) K128 final
    ret_agree10 = 0.2112, final hi80_cos = 0.8320.
  The TRAINED student captures ~0.2112/0.4295 = 49% of its OWN code's retrieval
  capacity. Target 0.35 is BELOW the 0.4295 ceiling -> a TRAINING-FIDELITY gap
  at fixed 2% sparsity. Loss-family swap REFUTED (+0.01); dense readout WORSE;
  OPQ rotation ~0. Live levers ranked by a 4-field-convergent research drill
  (notes/research_drill_sparse_distill_fidelity_lever_ladder_2026-07-04.md):
  B (discrete-gradient fidelity) > A (capacity) > C (schedule) > D (data).

LEVER B (PRIMARY, this cell). The forward is a per-block argmax (one +-1 per
32-wide block). The HARD straight-through estimator copies the upstream gradient
straight through the non-differentiable argmax -- a BIASED estimator whose
backward ignores that the winner could flip, so gradient to the NEAR-WINNER
logits (exactly the ones deciding fine near-neighbor rank, i.e. ret_agree10) is
starved/mis-signed. This is the reported #1 reason a trained model UNDERUSES an
available discrete code (PQ/deep-hashing/VQ/neural-compression all report the
train-soft/test-hard mismatch). FIX: per-block TEMPERATURE-ANNEALED softmax
assignment (tau HIGH->LOW so the soft forward converges to the hard argmax the
eval uses) + a soft/hard CONSISTENCY term (central-loss style) so the soft-trained
geometry survives the hard snap. Brain-grounded: cortical k-WTA uses graded
homeostatic gain, not a fixed hard threshold.

ARMS (PAIRED nested ablation; same seed/data/split/objective/LR/steps; ONLY the
listed lever changes between adjacent arms):
  HARD_STE        ste=hard   width=2048  -- control == v3e config (Gate-D posctrl)
  ANNEAL_STE      ste=anneal width=2048  -- +B (lever B ISOLATED vs HARD_STE)
  ANNEAL_STE_W2X  ste=anneal width=4096  -- +B+A (capacity ON TOP of B)
  PRIMARY discriminator: delta_B = ANNEAL_STE.ret - HARD_STE.ret (lever B).
  SECONDARY: delta_A_given_B = ANNEAL_STE_W2X.ret - ANNEAL_STE.ret.

FREE CAPACITY DIAGNOSTIC (coordinator ask, 2026-07-04). Every arm logs its
student's TRAIN-LOSS (in-batch RKD) trajectory alongside ret_agree10. If
HARD_STE train-loss is already FLOORED while ret_agree10 sits at ~0.20, that
KILLS the capacity hypothesis for FREE (the student fits the objective but the
HARD code loses the ranking -> it is the ESTIMATOR, not capacity). Reported as
`capacity_hypothesis_diagnostic`; no separate run needed.

WHY ONE TRAINER FOR ALL ARMS. At nce_weight=0 (the v3e/v5 winning config) the
NCE term contributes ZERO gradient in v3c._train_student_full (loss = l_rkd +
0*l_nce). So this cell uses ONE local trainer `_train_student_v6(ste_mode,...)`
whose ste_mode="hard" path reproduces the exact in-batch-RKD hard-STE baseline
(Gate-D band [0.15,0.28] around v3e's 0.2112) and whose ste_mode="anneal" path
swaps ONLY the STE + adds the consistency term. This makes HARD_STE and
ANNEAL_STE bit-paired to EACH OTHER (identical RNG/objective/LR), so delta_B is
a clean estimate of the estimator effect, and every arm logs train-loss
uniformly. v3._make_student / v3._block_ste / v3._encode_hard_block / v3._lr_at /
v3._semantic_unit / v3._keyed_unit are reused VERBATIM (read-only imports).

Longer cosine schedule (folds in lever C as B's delivery vehicle, HELD CONSTANT
across arms so C is not confounded with B): STEPS=8000 for all arms.

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01):
  query "encoder retrieval training fidelity student capacity MLP width depth
  K128 sparse ste gradient anneal" -> top cosine=0.2744 (wordnet noise) + a
  PQ-capacity note (0.27); NONE at cosine>0.30. The research drill's own
  concept-query (distill dense->sparse STE fidelity) also found NONE at >0.30
  for THIS concept (student-underuses-a-sufficient-code). GENUINELY NOVEL.

METHODOLOGY (LOCKED for all encoder cells): FINAL-step (not best-ckpt) is the
primary gated number; headline = ret_agree10 + hi80_cos; keyed@J5 SBC algebra is
an integrity control. Disjoint held/test pairs; exclude step-0; PAIRED
same-seed/data/split across arms; determinism pinned; torch.__version__
recorded. CANONICAL = the REMOTE-QUEUE OFFICIAL landing, NOT local smoke. 2
SEEDS: this core runs ONE seed; sibling _seed_7 / _seed_13 wrappers cover the
pair (CHUNKED single-seed-per-cell).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke/full gate (sha256 over each arm's code)
- final_metrics_atomicity: tmp_replace (write_metrics + atomic ckpt saves)
- except SystemExit: raise BEFORE except Exception (no BaseException/bare)
- crlb/capacity-feasibility: ret_agree10 ceiling at K128 is 0.4295
  (MEASURED@bypass); max attainable B-lift = 0.4295-0.2112 = 0.2183, HARD_PASS
  delta 0.05 far inside -> reachable. crlb_n_a declared (no sigma CRLB for
  ret_agree10); spearman r_max(128)=0.901 recorded for context.
- baseline_in_band: CHARPOS ret in (0.05,0.95); Gate-D HARD_STE in [0.15,0.28]
- discriminator-survives-scale: option (B) analytical (whole v3e/v5 lineage):
  smoke's tiny V_train=3000 cannot reproduce the near-neighbor coverage that
  drives ret_agree10, so smoke is a MACHINERY gate only (all STE arms train
  end-to-end, codes differ, integrity gates fire, cardinality holds; the
  annealed vs hard STE branches BOTH execute). The B-lift discriminator is
  FULL-only; the REMOTE-QUEUE OFFICIAL landing is canonical.
- HARD_PASS strictly above floor per prereg bands (META_RULE_L)
- HP_SCOPE: delta_B band applies to {HARD_STE,ANNEAL_STE}_BLOCK_LAST;
  delta_A_given_B to {ANNEAL_STE,ANNEAL_STE_W2X}; DENSE_*/*_BESTVAL context;
  RANDOM_BLOCK/CHARPOS/shuffled_key integrity-only.
- cardinality_ok: EXPECTED_N_UNITS=28 both run modes (SMOKE=FULL code path)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime (hyperparameters identical to
  the validated v3e/v5 lineage except the STE + width axes)
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

Prereg: preregs/2026-07-04_exp_encoder_v6_annealed_ste_fidelity_k128_v1.md
Parent cell (read-only import, NOT edited):
  experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py
Does NOT touch v3/v3c/v3e/v5's own artifact/checkpoint/output directories.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import random
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

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

# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_v6_annealed_ste_fidelity_k128_v1"
SEED_DEFAULT = v3.SEED_DEFAULT  # 7

# Pinned 177899-concept FULL corpus (canonical; matches v3c/v5). Present on the
# remote GPU box; NOT present locally (local has the 43905 half-corpus), so smoke
# passes None -> _resolve_teacher_cache picks the largest LOCAL cache.
TEACHER_CACHE_DEFAULT = (
    "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz")

OBJECTIVE = "in_batch"  # RKD-only, nce_weight=0 (matches v3e/v5 winning config)

# K held FIXED at 128 (3.125% active) for ALL arms. The axes are STE + width.
KB = 128
BLK_L = 32   # KB * BLK_L = 4096 = N_DIM

# arm_name -> (ste_mode, mlp_hidden). Nested ablation: control -> +B -> +B+A.
STE_ARMS = {
    "HARD_STE": ("hard", 2048),        # control == v3e config
    "ANNEAL_STE": ("anneal", 2048),    # +B (lever B isolated)
    "ANNEAL_STE_W2X": ("anneal", 4096),  # +B+A (capacity on top of B)
}
CONTROL_ARM = "HARD_STE"
B_ARM = "ANNEAL_STE"            # primary B comparison vs CONTROL_ARM
A_ON_B_ARM = "ANNEAL_STE_W2X"  # secondary A-given-B comparison vs B_ARM

# ---- Annealed-STE hyperparameters (lever B; literature-grounded defaults) ----
TAU_HI = 2.0          # soft early (gradient to near-winners)
TAU_LO = 0.1          # near-hard late (converges to argmax eval uses)
ANNEAL_FRAC = 0.8     # anneal over first 80% of steps, hold TAU_LO for last 20%
CONS_WEIGHT = 0.5     # soft/hard consistency weight (central-loss style)

# ---- FULL-scale config: MATCHES v3e/v5 except STE/width; LONGER schedule ----
FULL_BATCH = 128
FULL_STEPS = 8000     # longer than v3e's 6000 (lever C as B's delivery vehicle;
                      # HELD CONSTANT across arms so C is not confounded with B)
CKPT_EVERY_STEPS_FULL = 500
DENSE_EVAL_EVERY_FULL = 400
FULL_TRIALS = v3.MID_TRIALS
FULL_CHARPOS_CAP = v3.MID_CHARPOS_CAP

VAL_QUICK_SUB = 1500
VAL_QUICK_PAIRS = 40_000
VAL_FULL_PAIRS = 60_000
TEST_FINAL_PAIRS = v3.MID_PAIR_SAMPLE  # 400_000

# ---- Smoke config: MACHINERY validation only (SAME code path as FULL) ----
SMOKE_N_TRAIN = v3.SMOKE_N_TRAIN    # 3000
SMOKE_N_HELD = v3.SMOKE_N_HELD      # 800
SMOKE_STEPS = 200
SMOKE_CKPT_EVERY = 60
SMOKE_DENSE_EVAL_EVERY = 40
SMOKE_VAL_QUICK_SUB = 120
SMOKE_VAL_QUICK_PAIRS = 3_000
SMOKE_VAL_FULL_PAIRS = 5_000
SMOKE_TEST_FINAL_PAIRS = 8_000
SMOKE_CHARPOS_CAP = 300
SMOKE_TRIALS = 20
# Smoke uses narrower widths to keep the machinery gate fast while exercising
# the SAME per-arm hard/anneal STE branches at distinct settings.
SMOKE_STE_ARMS = {
    "HARD_STE": ("hard", 256),
    "ANNEAL_STE": ("anneal", 256),
    "ANNEAL_STE_W2X": ("anneal", 512),
}

MIN_STEP_FRAC_FOR_BEST = 0.05

# 3 arms x (semantic 4: DENSE/BLOCK x LAST/BESTVAL + semantic RANDOM_BLOCK(1) +
# keyed RANDOM_BLOCK(1) + keyed BLOCK_LAST(1) + keyed BLOCK_BESTVAL(1) +
# shuffled-LAST(1)) = 3 x 9 = 27, + shared CHARPOS semantic(1) = 28.
EXPECTED_N_UNITS_FULL = 28
EXPECTED_N_UNITS_SMOKE = 28

PREREG_BASELINE_ARMS = ["CHARPOS", "RANDOM_BLOCK"]
ALGEBRA_FLOOR = 0.90

# ---- Lever-B lift bands (HYPOTHESIZED@this prereg; research drill: B-alone
#      +0.06 to +0.10) ----
DELTA_B_HARD_PASS_MIN = 0.05     # delta_B >= 0.05 -> annealed STE is the lever
DELTA_B_HARD_FAIL_MAX = 0.02     # delta_B <= 0.02 -> STE-bias hypothesis refuted
DELTA_HI80_COS_REGRESSION_FLOOR = -0.02  # must not regress coarse cosine
BASELINE_RET_LO = 0.15           # Gate-D band around v3e MEASURED 0.2112
BASELINE_RET_HI = 0.28
CODE_CEILING_RET_K128 = 0.4295278  # MEASURED@bypass ortho_k128_ret_agree10


def _crlb_sigma_teacher(k_anchor: int, r_anchor: float) -> float:
    return math.sqrt((r_anchor ** 2 * 0.25 / k_anchor) / (1 - r_anchor ** 2))


CRLB_SIGMA_TEACHER = _crlb_sigma_teacher(128, 0.901)


def _crlb_r_max(k: int) -> float:
    return CRLB_SIGMA_TEACHER / math.sqrt(CRLB_SIGMA_TEACHER ** 2 + 0.25 / k)


def _artifact_dir(run_mode: str, run_tag: str = "") -> Path:
    suffix = {"smoke": "_smoke"}.get(run_mode, "")
    tag = f"_{run_tag}" if run_tag else ""
    return _REPO / "data" / f"substrate_concept_encoder_v6_annealste{tag}{suffix}"


# ---------------------------------------------------------------------------
# Annealed soft-block STE (lever B).
# ---------------------------------------------------------------------------

def _tau_at(step: int, steps: int, anneal_frac: float, tau_hi: float,
            tau_lo: float) -> float:
    """Cosine anneal tau_hi -> tau_lo over the first anneal_frac of steps, then
    hold tau_lo. tau(0)=tau_hi (soft); tau(anneal_end)=tau_lo (near-hard)."""
    anneal_steps = max(1, int(round(anneal_frac * steps)))
    if step >= anneal_steps:
        return tau_lo
    frac = step / anneal_steps
    return tau_lo + 0.5 * (tau_hi - tau_lo) * (1.0 + math.cos(math.pi * frac))


def _anneal_soft_block(z: torch.Tensor, kb: int, blk_l: int,
                       tau: float) -> torch.Tensor:
    """Per-block temperature-annealed SOFT signed code [B, kb*blk_l].

    a = softmax(|z|/tau) over each 32-wide block (soft one-hot); signed by
    sign(z). As tau->0, a->one-hot at argmax(|z|) so this converges to the
    hard block code (v3._encode_hard_block) the eval uses. Fully differentiable
    (no STE bias): gradient flows to ALL block entries weighted by softmax, so
    near-winner logits are NOT starved.
    """
    B = z.shape[0]
    zb = z.reshape(B, kb, blk_l)
    a = torch.softmax(zb.abs() / tau, dim=-1)
    sgn = torch.sign(zb)
    sgn = torch.where(sgn == 0, torch.ones_like(sgn), sgn)
    return (a * sgn).reshape(B, kb * blk_l)


# ---------------------------------------------------------------------------
# Determinism pinning (identical to v5/v4).
# ---------------------------------------------------------------------------

def _pin_determinism(seed: int) -> Dict:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    det_ok = True
    det_err = ""
    try:
        torch.use_deterministic_algorithms(True, warn_only=True)
    except TypeError:
        try:
            torch.use_deterministic_algorithms(True)
        except Exception as exc:  # pragma: no cover -- environment-dependent
            det_ok, det_err = False, f"{type(exc).__name__}: {exc}"
    except Exception as exc:  # pragma: no cover -- environment-dependent
        det_ok, det_err = False, f"{type(exc).__name__}: {exc}"
    n_threads = min(8, os.cpu_count() or 4)
    try:
        torch.set_num_threads(n_threads)
    except RuntimeError:
        pass
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        pass
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    return {
        "torch_version": torch.__version__,
        "cuda_available": bool(torch.cuda.is_available()),
        "num_threads_requested": n_threads,
        "deterministic_algorithms_set": det_ok,
        "deterministic_algorithms_error": det_err,
        "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
    }


# ---------------------------------------------------------------------------
# Defensive helpers (start marker / crash metrics / heartbeat).
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
# Trainer (ONE trainer, ste_mode-parameterized; nce_weight=0 -> NCE dropped).
# ---------------------------------------------------------------------------

def _train_loss_floored(rkd_traj: List[Dict]) -> Tuple[bool, float]:
    """Given the per-eval rkd (train-loss) trajectory, return (floored, frac).

    frac = fraction of total descent achieved by the halfway eval point.
    floored = last-quarter descent < 5% of total descent (loss flat at the end).
    """
    pts = [(r["step"], r["rkd"]) for r in rkd_traj if math.isfinite(r.get("rkd", float("nan")))]
    if len(pts) < 3:
        return False, float("nan")
    pts.sort()
    rkd_first = pts[0][1]
    rkd_last = pts[-1][1]
    total = rkd_first - rkd_last
    if total <= 1e-9:
        return True, 1.0  # never descended (or already floored)
    half_i = len(pts) // 2
    q3_i = (3 * len(pts)) // 4
    frac_by_half = (rkd_first - pts[half_i][1]) / total
    last_quarter = (pts[q3_i][1] - rkd_last) / total
    return bool(last_quarter < 0.05), float(frac_by_half)


def _train_student_v6(
    ste_mode: str, width: int, kb: int, blk_l: int, Xtr: torch.Tensor,
    steps: int, batch: int, warmup: int, seed: int, device: str,
    ckpt_path: Path, best_ckpt_path: Path, ckpt_every: int, output_dir: Path,
    t0: float, dense_eval_quick_fn: Optional[Callable],
    dense_eval_full_fn: Optional[Callable], dense_eval_every: int,
    min_step_for_best: int, tau_hi: float, tau_lo: float, anneal_frac: float,
    cons_weight: float, arm_label: str,
) -> Tuple[torch.nn.Module, Dict]:
    """In-batch RKD trainer. ste_mode in {hard, anneal}. Reuses v3 primitives.

    hard:  loss = in_batch_RKD(normalize(v3._block_ste(z)))   == v3e baseline.
    anneal: s_soft = normalize(_anneal_soft_block(z, tau(step)));
            s_hard = normalize(v3._block_ste(z));
            loss = in_batch_RKD(s_soft) + cons_weight * MSE(s_soft, s_hard.detach()).
    Eval always uses the HARD code (v3._encode_hard_block), so the annealed
    arm's benefit must manifest in the HARD code's retrieval.
    """
    if ste_mode not in ("hard", "anneal"):
        raise ValueError(f"unknown ste_mode {ste_mode}")
    orig_hidden = v3.MLP_HIDDEN
    v3.MLP_HIDDEN = width
    try:
        student = v3._make_student("mlp", Xtr.shape[1], kb * blk_l, device, seed)
    finally:
        v3.MLP_HIDDEN = orig_hidden
    actual_hidden = int(student.net[0].out_features)
    if actual_hidden != width:
        raise RuntimeError(
            f"failure_class=WIDTH_MONKEYPATCH_FAILED: {arm_label} built student "
            f"hidden={actual_hidden} != requested width={width}")
    opt = torch.optim.Adam(student.parameters(), lr=v3.LR)
    gen = torch.Generator().manual_seed(seed)
    V = Xtr.shape[0]
    Xd = Xtr.to(device)
    start_step = 0
    dense_traj: List[Dict] = []
    best_state = {"score": -2.0, "step": -1}
    if ckpt_path.exists():
        try:
            ck = torch.load(str(ckpt_path), map_location=device)
            student.load_state_dict(ck["student"])
            opt.load_state_dict(ck["opt"])
            gen.set_state(ck["gen_state"])
            start_step = int(ck["step"])
            dense_traj = list(ck.get("dense_traj", []))
            best_state["score"] = float(ck.get("best_score", -2.0))
            best_state["step"] = int(ck.get("best_step", -1))
            print(f"[v6_ste] resume {arm_label} at step {start_step}", flush=True)
        except (RuntimeError, KeyError, EOFError) as exc:
            print(f"[v6_ste] WARN {arm_label} ckpt load failed ({type(exc).__name__}); "
                  f"retraining from scratch", flush=True)
            start_step = 0
            dense_traj = []
            best_state = {"score": -2.0, "step": -1}

    off = ~torch.eye(batch, dtype=torch.bool, device=device)
    loss_first = loss_last = rkd_last = cons_last = tau_last = None

    def _maybe_save_best(step_i: int, d_full: float) -> None:
        if not math.isfinite(d_full) or step_i < min_step_for_best:
            return
        if d_full > best_state["score"]:
            best_state["score"] = d_full
            best_state["step"] = step_i
            tmp_b = best_ckpt_path.with_suffix(".tmp")
            torch.save({"student": student.state_dict(), "step": step_i,
                        "dense_full": d_full, "arm": arm_label}, str(tmp_b))
            os.replace(str(tmp_b), str(best_ckpt_path))

    for step in range(start_step, steps):
        cur_lr = v3._lr_at(step, steps, warmup, v3.LR)
        for g in opt.param_groups:
            g["lr"] = cur_lr
        bidx = torch.randint(0, V, (batch,), generator=gen)
        x = Xd[bidx.to(device)]
        z = student(x)
        T = x @ x.T
        if ste_mode == "hard":
            s = v3._block_ste(z, kb, blk_l)
            s_n = s / (s.norm(dim=-1, keepdim=True) + 1e-8)
            l_rkd = (((s_n @ s_n.T) - T)[off] ** 2).mean()
            l_cons = torch.zeros((), device=device)
            tau = float("nan")
        else:
            tau = _tau_at(step, steps, anneal_frac, tau_hi, tau_lo)
            s_soft = _anneal_soft_block(z, kb, blk_l, tau)
            s_soft_n = s_soft / (s_soft.norm(dim=-1, keepdim=True) + 1e-8)
            s_hard = v3._block_ste(z, kb, blk_l)
            s_hard_n = s_hard / (s_hard.norm(dim=-1, keepdim=True) + 1e-8)
            l_rkd = (((s_soft_n @ s_soft_n.T) - T)[off] ** 2).mean()
            l_cons = ((s_soft_n - s_hard_n.detach()) ** 2).mean()
        loss = l_rkd + cons_weight * l_cons
        if not torch.isfinite(loss):
            raise RuntimeError(
                f"failure_class=NAN_LOSS: {arm_label} loss non-finite at step {step} "
                f"(l_rkd={float(l_rkd.detach())}, l_cons={float(l_cons.detach())}, "
                f"tau={tau})")
        opt.zero_grad()
        loss.backward()
        opt.step()
        v_loss = float(loss.detach())
        v_rkd = float(l_rkd.detach())
        v_cons = float(l_cons.detach())
        if loss_first is None:
            loss_first = v_loss
        loss_last, rkd_last, cons_last, tau_last = v_loss, v_rkd, v_cons, tau
        if step % 200 == 0:
            print(f"[v6_ste] {arm_label} step {step}/{steps} rkd={v_rkd:.4f} "
                  f"cons={v_cons:.4f} tau={tau if math.isfinite(tau) else -1:.3f} "
                  f"lr={cur_lr:.2e} ({time.perf_counter() - t0:.1f}s)", flush=True)
            _emit_heartbeat(output_dir, step, steps, time.perf_counter() - t0,
                            extra={"phase": f"train_{arm_label}", "rkd": v_rkd,
                                   "cons": v_cons})
        if (dense_eval_full_fn is not None and dense_eval_every > 0
                and step % dense_eval_every == 0):
            d_full = float(dense_eval_full_fn(student))
            d_quick = (float(dense_eval_quick_fn(student))
                       if dense_eval_quick_fn is not None else float("nan"))
            dense_traj.append({"step": step, "dense_full": d_full,
                               "dense_quick": d_quick, "rkd": v_rkd,
                               "tau": tau, "final": False})
            print(f"[v6_ste] {arm_label} DENSE-traj step {step}: full={d_full:.4f} "
                  f"quick={d_quick:.4f} rkd={v_rkd:.4f}", flush=True)
            _maybe_save_best(step, d_full)
        if (step + 1) % ckpt_every == 0 or (step + 1) == steps:
            tmp = ckpt_path.with_suffix(".tmp")
            torch.save({"student": student.state_dict(), "opt": opt.state_dict(),
                        "gen_state": gen.get_state(), "step": step + 1,
                        "dense_traj": dense_traj, "best_score": best_state["score"],
                        "best_step": best_state["step"]}, str(tmp))
            os.replace(str(tmp), str(ckpt_path))
    if dense_eval_full_fn is not None:
        d_full_fin = float(dense_eval_full_fn(student))
        d_quick_fin = (float(dense_eval_quick_fn(student))
                       if dense_eval_quick_fn is not None else float("nan"))
        dense_traj.append({"step": steps, "dense_full": d_full_fin,
                           "dense_quick": d_quick_fin,
                           "rkd": rkd_last if rkd_last is not None else float("nan"),
                           "tau": tau_last, "final": True})
        _maybe_save_best(steps, d_full_fin)
        print(f"[v6_ste] {arm_label} FINAL step {steps}: full={d_full_fin:.4f}",
              flush=True)
    best_ckpt_fallback_to_final = best_state["step"] < 0
    if best_ckpt_fallback_to_final:
        tmp_b = best_ckpt_path.with_suffix(".tmp")
        torch.save({"student": student.state_dict(), "step": steps,
                    "dense_full": float("nan"), "arm": arm_label}, str(tmp_b))
        os.replace(str(tmp_b), str(best_ckpt_path))
        print(f"[v6_ste] WARN {arm_label}: no eval >= min_step_for_best; "
              f"best-ckpt falls back to FINAL", flush=True)
    floored, frac_half = _train_loss_floored(dense_traj)
    return student, {
        "loss_first": loss_first if loss_first is not None else -1.0,
        "loss_last": loss_last if loss_last is not None else -1.0,
        "rkd_last": rkd_last if rkd_last is not None else -1.0,
        "cons_last": cons_last if cons_last is not None else -1.0,
        "tau_last": tau_last if tau_last is not None else float("nan"),
        "ste_mode": ste_mode, "mlp_hidden": width,
        "arm": arm_label, "objective": OBJECTIVE, "batch": batch,
        "dense_traj": dense_traj,
        "train_loss_floored": floored,
        "train_loss_descent_frac_by_half": frac_half,
        "best_dense_full": best_state["score"], "best_step": best_state["step"],
        "best_ckpt_fallback_to_final": best_ckpt_fallback_to_final,
    }


def _reload_best_v6(width: int, in_dim: int, out_dim: int, device: str,
                    best_ckpt_path: Path) -> torch.nn.Module:
    orig_hidden = v3.MLP_HIDDEN
    v3.MLP_HIDDEN = width
    try:
        student = v3._make_student("mlp", in_dim, out_dim, device, seed=0)
    finally:
        v3.MLP_HIDDEN = orig_hidden
    ck = torch.load(str(best_ckpt_path), map_location=device)
    student.load_state_dict(ck["student"])
    return student


# ---------------------------------------------------------------------------
# Verdict logic.
# ---------------------------------------------------------------------------

def _verdict_ste(per_unit: List[Dict], recovery: Dict, arm_names: List[str],
                 control_arm: str, b_arm: str, a_on_b_arm: str,
                 expected_units: int, run_mode: str) -> Tuple[str, str]:
    if len(per_unit) < expected_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"{len(per_unit)}/{expected_units} units")
    for arm in arm_names:
        posc = v3._by_unit(per_unit, "keyed", f"{arm}_RANDOM_BLOCK", 5)
        if posc is None or posc["acc_at1"] < 0.98:
            return ("HARD_FAIL",
                    f"HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH: {arm} RANDOM_BLOCK "
                    f"keyed J=5 {posc['acc_at1'] if posc else None} < 0.98")
        shuf = v3._by_unit(per_unit, "shuffled_key", f"{arm}_BLOCK_LAST", 5)
        if shuf is None:
            return ("HARD_FAIL", f"HARD_FAIL_MISSING_GATE_UNITS: {arm} shuffled_key")
        if shuf["acc_at1"] > 0.05 or shuf["hit_any_member"] > 0.10:
            return ("HARD_FAIL",
                    f"HARD_FAIL_SHUFFLED_KEY_LEAK: {arm} "
                    f"{shuf['acc_at1']:.3f}/{shuf['hit_any_member']:.3f}")
        prim = v3._by_unit(per_unit, "keyed", f"{arm}_BLOCK_LAST", 5)
        if prim is None:
            return ("HARD_FAIL", f"HARD_FAIL_MISSING_GATE_UNITS: {arm} keyed LAST")
        if prim["acc_at1"] < ALGEBRA_FLOOR:
            return ("HARD_FAIL",
                    f"FALSE_WIN_ALGEBRA_LAST_STEP_{arm}: keyed_roundtrip J=5 "
                    f"{prim['acc_at1']:.3f} < {ALGEBRA_FLOOR}")

    ctrl = recovery[control_arm]["final"]
    b = recovery[b_arm]["final"]
    a = recovery[a_on_b_arm]["final"]
    delta_b = b["ret_agree10"] - ctrl["ret_agree10"]
    delta_b_hi80 = b["hi80_cos"] - ctrl["hi80_cos"]
    delta_a_given_b = a["ret_agree10"] - b["ret_agree10"]
    diag = recovery[control_arm].get("train_loss_floored")
    cap_diag = ("train_loss_floored_at_low_ret->capacity_NOT_bottleneck(favors_B)"
                if diag else "train_loss_not_floored->capacity_may_matter")
    tail = (f"[HARD_STE ret={ctrl['ret_agree10']:.4f} hi80={ctrl['hi80_cos']:.4f} "
            f"floored={diag}] [ANNEAL_STE ret={b['ret_agree10']:.4f} "
            f"hi80={b['hi80_cos']:.4f}] [ANNEAL_W2X ret={a['ret_agree10']:.4f}] "
            f"delta_B={delta_b:.4f} delta_A|B={delta_a_given_b:.4f} "
            f"code_ceiling={CODE_CEILING_RET_K128:.4f} cap_diag={cap_diag}")

    if run_mode == "smoke":
        for arm in arm_names:
            if not math.isfinite(recovery[arm]["final"]["ret_agree10"]):
                return ("SMOKE_GATE_FAIL", f"S_ret_agree10_missing_{arm}")
            if not math.isfinite(recovery[arm]["final"]["hi80_cos"]):
                return ("SMOKE_GATE_FAIL", f"S_hi80_cos_missing_{arm}")
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: all {len(arm_names)} STE arms (hard + 2 annealed) "
                f"train end-to-end with differing codes, per-arm RANDOM_BLOCK/algebra/"
                f"shuffled-key checks fire, cardinality holds; both hard and anneal STE "
                f"branches executed {tail} (the B-lift discriminator is a FULL-only "
                f"question; smoke's tiny V_train cannot reproduce it -- REMOTE-QUEUE "
                f"OFFICIAL LANDING is canonical, this local smoke is a machinery gate)")

    # ---- FULL verdict ----
    if not (BASELINE_RET_LO <= ctrl["ret_agree10"] <= BASELINE_RET_HI):
        return ("HARD_FAIL",
                f"HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH: control {control_arm} final "
                f"ret_agree10 {ctrl['ret_agree10']:.4f} outside v3e-reproduction band "
                f"[{BASELINE_RET_LO},{BASELINE_RET_HI}] -- hard-STE baseline drifted "
                f"from v3e; B comparison not trustworthy {tail}")
    if delta_b_hi80 < DELTA_HI80_COS_REGRESSION_FLOOR:
        return ("HARD_FAIL",
                f"ANNEAL_REGRESSES_CALIBRATION: hi80_cos delta {delta_b_hi80:.4f} < "
                f"{DELTA_HI80_COS_REGRESSION_FLOOR} -- annealed STE costs semantic "
                f"calibration {tail}")
    if delta_b >= DELTA_B_HARD_PASS_MIN:
        return ("HARD_PASS",
                f"LEVER_B_ANNEALED_STE_LIFTS_RETRIEVAL: delta_B {delta_b:.4f} >= "
                f"{DELTA_B_HARD_PASS_MIN} with no calibration regression -- the annealed "
                f"soft-to-hard STE closes part of the 0.21->0.43 gap; the hard-STE "
                f"gradient bias WAS the bottleneck. delta_A|B={delta_a_given_b:.4f} "
                f"(capacity ON TOP of B). Next: tau-schedule sweep + B+A+C stack for "
                f"0.35 {tail}")
    if delta_b <= DELTA_B_HARD_FAIL_MAX:
        return ("HARD_FAIL",
                f"LEVER_B_DEAD_STE_BIAS_NOT_THE_GAP: delta_B {delta_b:.4f} <= "
                f"{DELTA_B_HARD_FAIL_MAX} -- annealed STE does NOT lift retrieval; the "
                f"discrete-gradient-bias hypothesis is REFUTED at K128. The gap is "
                f"structural (k-WTA rank-preservation ceiling) or elsewhere; "
                f"capacity_diag={cap_diag} {tail}")
    return ("MIDDLE_BAND",
            f"LEVER_B_MARGINAL_LIFT: delta_B {delta_b:.4f} between "
            f"{DELTA_B_HARD_FAIL_MAX} and {DELTA_B_HARD_PASS_MIN} -- a real but small "
            f"estimator effect; needs a tau-schedule sweep or the 2nd seed {tail}")


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def run_ste_sweep(run_mode: str, seed: int, device_arg: str, n_dim: int,
                  teacher_cache_arg: Optional[str], run_tag: str = "") -> int:
    assert run_mode in ("smoke", "full"), f"unsupported run_mode {run_mode}"
    if KB * BLK_L != n_dim:
        raise ValueError(f"n_dim {n_dim} != KB*BLK_L {KB*BLK_L}")
    det_info = _pin_determinism(seed)
    tag_suffix = f"_{run_tag}" if run_tag else ""
    anchor = f"{ANCHOR_NAME}{tag_suffix}_smoke" if run_mode == "smoke" \
        else f"{ANCHOR_NAME}{tag_suffix}"
    out_dir = get_output_dir(anchor)
    art_dir = _artifact_dir(run_mode, run_tag)
    art_dir.mkdir(parents=True, exist_ok=True)
    device = ("cuda" if torch.cuda.is_available() else "cpu") \
        if device_arg == "auto" else device_arg

    ste_arms = SMOKE_STE_ARMS if run_mode == "smoke" else STE_ARMS
    arm_names = list(ste_arms.keys())

    if run_mode == "smoke":
        steps = SMOKE_STEPS
        ckpt_every, dense_every = SMOKE_CKPT_EVERY, SMOKE_DENSE_EVAL_EVERY
        quick_sub, quick_pairs = SMOKE_VAL_QUICK_SUB, SMOKE_VAL_QUICK_PAIRS
        val_full_pairs, test_final_pairs = SMOKE_VAL_FULL_PAIRS, SMOKE_TEST_FINAL_PAIRS
        charpos_cap, n_trials = SMOKE_CHARPOS_CAP, SMOKE_TRIALS
        n_tr_target, n_he_target = SMOKE_N_TRAIN, SMOKE_N_HELD
        batch = min(FULL_BATCH, 32)
    else:
        steps = FULL_STEPS
        ckpt_every, dense_every = CKPT_EVERY_STEPS_FULL, DENSE_EVAL_EVERY_FULL
        quick_sub, quick_pairs = VAL_QUICK_SUB, VAL_QUICK_PAIRS
        val_full_pairs, test_final_pairs = VAL_FULL_PAIRS, TEST_FINAL_PAIRS
        charpos_cap, n_trials = FULL_CHARPOS_CAP, FULL_TRIALS
        n_tr_target = n_he_target = None
        batch = FULL_BATCH
    expected_units = EXPECTED_N_UNITS_SMOKE if run_mode == "smoke" else EXPECTED_N_UNITS_FULL
    warmup = v3._warmup_for(steps)
    min_step_for_best = max(1, int(round(MIN_STEP_FRAC_FOR_BEST * steps)))

    _write_start_marker(out_dir, run_mode, expected_units)
    t0 = time.perf_counter()
    print(f"[v6_ste] run_mode={run_mode} seed={seed} device={device} n_dim={n_dim} "
          f"KB={KB} blk_l={BLK_L} arms={ste_arms} steps={steps} batch={batch} "
          f"tau={TAU_HI}->{TAU_LO}@{ANNEAL_FRAC} cons_w={CONS_WEIGHT} "
          f"torch={det_info['torch_version']} "
          f"deterministic_ok={det_info['deterministic_algorithms_set']}", flush=True)

    effective_cache_arg = teacher_cache_arg
    if run_mode == "full" and effective_cache_arg is None:
        effective_cache_arg = TEACHER_CACHE_DEFAULT  # pinned 177899 canonical corpus
    cache_path = v3._resolve_teacher_cache(effective_cache_arg)
    cache_bytes = cache_path.stat().st_size
    X, ids = v3._load_teacher(cache_path)
    V_cache = X.shape[0]
    print(f"[v6_ste] teacher {cache_path.name}: {V_cache} concepts x "
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
    he_idx = perm[n_tr:n_tr + n_he]
    Xtr = X[torch.from_numpy(tr_idx.copy())].contiguous()
    Xhe = X[torch.from_numpy(he_idx.copy())].contiguous()
    names_he = [ids[i] for i in he_idx]
    print(f"[v6_ste] split train={n_tr} held={n_he}", flush=True)

    Xhe_sub = Xhe[:min(quick_sub, n_he)].contiguous()

    def _deval_quick(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xhe_sub, quick_pairs, seed + 7)

    def _deval_full(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xhe, val_full_pairs, seed + 7)

    arm_diag: Dict[str, Dict] = {}
    arm_codes: Dict[str, torch.Tensor] = {}
    for arm, (ste_mode, width) in ste_arms.items():
        ckpt_path = art_dir / f"_ckpt_{arm}.pt"
        best_ckpt_path = art_dir / f"_ckpt_best_{arm}.pt"
        last_student, diag = _train_student_v6(
            ste_mode, width, KB, BLK_L, Xtr, steps, batch, warmup, seed, device,
            ckpt_path, best_ckpt_path, ckpt_every, out_dir, t0,
            _deval_quick, _deval_full, dense_every, min_step_for_best,
            TAU_HI, TAU_LO, ANNEAL_FRAC, CONS_WEIGHT, arm)
        bestval_student = _reload_best_v6(width, Xtr.shape[1], KB * BLK_L, device,
                                          best_ckpt_path)
        arm_diag[arm] = diag
        arm_codes[f"{arm}_DENSE_LAST"] = v3._dense_sign_codes(last_student, Xhe)
        arm_codes[f"{arm}_BLOCK_LAST"] = v3._encode_hard_block(last_student, Xhe, KB, BLK_L)
        arm_codes[f"{arm}_DENSE_BESTVAL"] = v3._dense_sign_codes(bestval_student, Xhe)
        arm_codes[f"{arm}_BLOCK_BESTVAL"] = v3._encode_hard_block(bestval_student, Xhe, KB, BLK_L)
        gen_ctrl = torch.Generator().manual_seed(seed + 1 + width + hash(ste_mode) % 997)
        arm_codes[f"{arm}_RANDOM_BLOCK"] = v3._random_block_codes(n_he, KB, BLK_L, gen_ctrl)
        print(f"[v6_ste] {arm} (ste={ste_mode} hidden={width}) trained "
              f"rkd_last={diag['rkd_last']:.4f} cons_last={diag['cons_last']:.4f} "
              f"floored={diag['train_loss_floored']} "
              f"best_val={diag['best_dense_full']:.4f}@step{diag['best_step']} "
              f"({time.perf_counter() - t0:.1f}s)", flush=True)

    cp_cap = min(n_he, charpos_cap)
    cp_codes = v3._charpos_codes(names_he[:cp_cap], n_dim, v3.K_BLOCKS_PRIMARY)

    digests = {}
    for name, c in list(arm_codes.items()) + [("CHARPOS", cp_codes)]:
        digests[name] = hashlib.sha256(c.to(torch.int8).numpy().tobytes()).hexdigest()

    def _is_last_bestval_pair(a: str, b: str) -> bool:
        # LAST vs BESTVAL of the SAME arm+kind legitimately coincide when the
        # best-val eval point IS the final step (best-ckpt == last student).
        # This is an expected identity, not an arm-implementation bug; cross-arm
        # and cross-kind collisions still raise META_RULE_AF_VIOLATION.
        return a != b and a.replace("_BESTVAL", "_LAST") == b.replace("_BESTVAL", "_LAST")

    af_exempted: List[List[str]] = []
    for aa in digests:
        for bb in digests:
            if aa < bb and digests[aa] == digests[bb]:
                if _is_last_bestval_pair(aa, bb):
                    af_exempted.append([aa, bb])
                    continue
                raise RuntimeError(
                    f"failure_class=META_RULE_AF_VIOLATION: {aa}/{bb} identical")

    per_unit: List[Dict] = []
    unit_fail: List[Dict] = []
    gen_eval = torch.Generator().manual_seed(seed + 2)

    def _run_unit(fn, *a, **kw):
        try:
            u = fn(*a, **kw)
            per_unit.append(u)
            print(f"[v6_ste] unit {len(per_unit)}/{expected_units} {u['unit']}: "
                  + json.dumps({k: round(v, 4) for k, v in u.items()
                                if isinstance(v, float)}), flush=True)
            _emit_heartbeat(out_dir, len(per_unit), expected_units,
                            time.perf_counter() - t0, extra={"unit": u["unit"]})
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append({"fn": getattr(fn, "__name__", "?"),
                              "failure_class": type(exc).__name__,
                              "msg": str(exc)[:300]})
            raise

    for arm in arm_names:
        for label in (f"{arm}_DENSE_LAST", f"{arm}_BLOCK_LAST",
                      f"{arm}_DENSE_BESTVAL", f"{arm}_BLOCK_BESTVAL"):
            c = arm_codes[label]
            _run_unit(v3._semantic_unit, label, c, c, Xhe, Xhe, 0,
                      test_final_pairs, seed + 3)
        _run_unit(v3._semantic_unit, f"{arm}_RANDOM_BLOCK", arm_codes[f"{arm}_RANDOM_BLOCK"],
                  arm_codes[f"{arm}_RANDOM_BLOCK"], Xhe, Xhe, 0, test_final_pairs, seed + 3)
    cp_Xhe = Xhe[:cp_cap]
    _run_unit(v3._semantic_unit, "CHARPOS", cp_codes, cp_codes, cp_Xhe, cp_Xhe, 0,
              test_final_pairs, seed + 3)

    for arm in arm_names:
        _run_unit(v3._keyed_unit, f"{arm}_RANDOM_BLOCK", "sbc", arm_codes[f"{arm}_RANDOM_BLOCK"],
                  KB, BLK_L, 5, n_trials, gen_eval, device)
        _run_unit(v3._keyed_unit, f"{arm}_BLOCK_LAST", "sbc",
                  arm_codes[f"{arm}_BLOCK_LAST"], KB, BLK_L, 5, n_trials, gen_eval, device)
        _run_unit(v3._keyed_unit, f"{arm}_BLOCK_BESTVAL", "sbc",
                  arm_codes[f"{arm}_BLOCK_BESTVAL"], KB, BLK_L, 5, n_trials, gen_eval, device)
        _run_unit(v3._keyed_unit, f"{arm}_BLOCK_LAST", "sbc",
                  arm_codes[f"{arm}_BLOCK_LAST"], KB, BLK_L, 5, n_trials, gen_eval,
                  device, shuffled_key=True)

    def _sem_summary(arm: str, kind: str) -> Dict:
        u = v3._by_unit(per_unit, "semantic", f"{arm}_{kind}")
        if u is None:
            return {"spearman_all": float("nan"), "ret_agree10": float("nan"),
                    "hi80_cos": float("nan"), "hi80_calib_err": float("nan")}
        return {"spearman_all": u["spearman_all"], "ret_agree10": u["ret_agree10"],
                "hi80_cos": u["hi80_cos"], "hi80_calib_err": u["hi80_calib_err"]}

    recovery = {arm: {
        "ste_mode": ste_arms[arm][0], "mlp_hidden": ste_arms[arm][1],
        "kb": KB, "blk_l": BLK_L, "sparsity": KB / n_dim,
        "final": _sem_summary(arm, "BLOCK_LAST"),
        "bestval_on_test": _sem_summary(arm, "BLOCK_BESTVAL"),
        "final_dense": _sem_summary(arm, "DENSE_LAST"),
        "bestval_dense_on_test": _sem_summary(arm, "DENSE_BESTVAL"),
        "rkd_last": arm_diag[arm]["rkd_last"],
        "cons_last": arm_diag[arm]["cons_last"],
        "tau_last": arm_diag[arm]["tau_last"],
        "train_loss_floored": arm_diag[arm]["train_loss_floored"],
        "train_loss_descent_frac_by_half": arm_diag[arm]["train_loss_descent_frac_by_half"],
        "rkd_traj": [{"step": r["step"], "rkd": r["rkd"], "dense_full": r["dense_full"]}
                     for r in arm_diag[arm]["dense_traj"]],
        "best_step": arm_diag[arm]["best_step"],
        "best_ckpt_fallback_to_final": arm_diag[arm]["best_ckpt_fallback_to_final"],
        "crlb_r_max": _crlb_r_max(KB),
    } for arm in arm_names}

    verdict, verdict_msg = _verdict_ste(
        per_unit, recovery, arm_names, CONTROL_ARM if CONTROL_ARM in recovery else arm_names[0],
        B_ARM if B_ARM in recovery else arm_names[1],
        A_ON_B_ARM if A_ON_B_ARM in recovery else arm_names[2],
        expected_units, run_mode)
    elapsed = time.perf_counter() - t0

    # Free capacity diagnostic surfaced explicitly.
    ctrl_floored = recovery.get(CONTROL_ARM, recovery[arm_names[0]])["train_loss_floored"]
    ctrl_ret = recovery.get(CONTROL_ARM, recovery[arm_names[0]])["final"]["ret_agree10"]
    capacity_hypothesis_diagnostic = (
        "train_loss_floored_while_ret_low->capacity_NOT_bottleneck_favors_B"
        if (ctrl_floored and math.isfinite(ctrl_ret) and ctrl_ret < 0.30)
        else "train_loss_not_floored_or_ret_high->capacity_may_matter")

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "run_tag": run_tag, "seed": int(seed), "device": device, "N": n_dim,
        "student_arch": "mlp", "ste_arms": {k: list(v) for k, v in ste_arms.items()},
        "control_arm": CONTROL_ARM, "b_arm": B_ARM, "a_on_b_arm": A_ON_B_ARM,
        "kb": KB, "blk_l": BLK_L, "sparsity": KB / n_dim,
        "tau_hi": TAU_HI, "tau_lo": TAU_LO, "anneal_frac": ANNEAL_FRAC,
        "cons_weight": CONS_WEIGHT,
        "warmup_steps": warmup, "steps": steps, "batch": batch,
        "nce_weight": 0.0, "objective": OBJECTIVE, "lr_schedule": "cosine_longer_8000",
        "min_step_for_best": min_step_for_best, "dense_eval_every": dense_every,
        "teacher_cache": cache_path.name, "teacher_cache_bytes": cache_bytes,
        "teacher_n_concepts": V_cache, "n_train": n_tr, "n_held_pool": n_he,
        "recovery": recovery,
        "capacity_hypothesis_diagnostic": capacity_hypothesis_diagnostic,
        "code_ceiling_ret_agree10_k128": CODE_CEILING_RET_K128,
        "code_ceiling_source": ("MEASURED@data/exp_encoder_teacher_sparsifier_bypass_v1/"
                                "metrics.json:/recovery/ortho_k128_ret_agree10"),
        "determinism": det_info,
        "canonical_source": "remote_queue_official_landing_only; local_smoke_is_gate_only",
        "per_unit": per_unit, "unit_failures": unit_fail,
        "n_units": len(per_unit), "expected_n_units": expected_units,
        "cardinality_ok": len(per_unit) == expected_units,
        "arms_differ_verified": True, "arm_code_sha256": digests,
        "arms_differ_exempted": af_exempted,
        "final_metrics_atomicity": "tmp_replace",
        "composition_algebra": "SBC_block_local_circular_convolution",
        "methodology": ("PAIRED nested-ablation at FIXED K=128 (3.125% active): "
                        "HARD_STE control (== v3e) -> ANNEAL_STE (+lever B, "
                        "temperature-annealed soft-to-hard block STE + soft/hard "
                        "consistency) -> ANNEAL_STE_W2X (+lever A capacity on top of "
                        "B). ONE trainer (nce_weight=0 -> NCE dropped) so arms are "
                        "bit-paired to each other. FINAL-step ret_agree10 delta_B "
                        "(ANNEAL-HARD) is the PRIMARY gated comparison; the control "
                        "== v3e config is a Gate-D positive control that must "
                        "reproduce v3e's ~0.21. Every arm logs its TRAIN-LOSS (RKD) "
                        "trajectory -> free capacity diagnostic (if HARD_STE "
                        "train-loss floored while ret ~0.20, capacity is NOT the "
                        "bottleneck). LR schedule held constant (8000 steps) across "
                        "arms so lever C is not confounded with B."),
        "sequenced_next_cell": ("IF LEVER_B lifts: tau-schedule sweep + EMA + full "
                                "B+A+C stack for 0.35. IF LEVER_B_DEAD: the 0.43 "
                                "ceiling is structural (k-WTA rank cap); accept ~0.30 "
                                "sparsity-honest fallback per encoder goals."),
        "storage_strategy": ("no_composition; single-hop retrieval-agreement is the "
                             "metric; keyed-J5 SBC is a fixed integrity control (bounded "
                             "5-item bundle, not a chain)"),
        "compute_architecture": ("batched-GPU: student forward/backward + annealed soft "
                                 "block are batched matmul/elementwise on cuda (device "
                                 "auto->cuda on the GPU box); eval samples pairs batched"),
        "progress_logging": "print_flush_true",
        "baseline_in_band": bool(0.05 < v3._by_unit(
            per_unit, "semantic", "CHARPOS")["ret_agree10"] < 0.95),
        "crlb_floor_computed": {"K128_spearman_r_max": _crlb_r_max(128)},
        "crlb_formula_reference": ("ret_agree10 discriminator reachability uses the "
                                   "EMPIRICAL K128 code ceiling 0.4295 (MEASURED@bypass): "
                                   "max attainable B-lift = 0.4295-0.2112 = 0.2183 >> "
                                   "HARD_PASS delta_B 0.05 -> reachable."),
        "crlb_n_a": ("ret_agree10 has no closed-form sigma CRLB; reachability via "
                     "empirical code ceiling per META_RULE #9"),
        "discriminator_reachability": True,
        "cell_chunked": True, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "calibration_check": "default_ok_for_this_regime",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[v6_ste] verdict={verdict} msg={verdict_msg} elapsed={elapsed:.1f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Self-test (synthetic; no cache dependency; fast).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()

    # 1. tau schedule: tau(0)=tau_hi, tau(anneal_end)=tau_lo, held after.
    assert abs(_tau_at(0, 100, 0.8, 2.0, 0.1) - 2.0) < 1e-6, "tau(0) should be tau_hi"
    assert abs(_tau_at(80, 100, 0.8, 2.0, 0.1) - 0.1) < 1e-6, "tau(anneal_end)=tau_lo"
    assert abs(_tau_at(99, 100, 0.8, 2.0, 0.1) - 0.1) < 1e-6, "tau held at tau_lo after"
    mid = _tau_at(40, 100, 0.8, 2.0, 0.1)
    assert 0.1 < mid < 2.0, f"tau mid should be between lo and hi, got {mid}"

    # 2. anneal soft block -> hard block as tau->0 (per-block argmax + sign).
    torch.manual_seed(3)
    z = torch.randn(4, 8 * 4)  # kb=8, blk_l=4
    soft_hot = _anneal_soft_block(z, 8, 4, 0.001)  # near-hard
    zb = z.reshape(4, 8, 4)
    argmax_idx = zb.abs().argmax(dim=-1)
    soft_hb = soft_hot.reshape(4, 8, 4)
    picked = soft_hb.abs().argmax(dim=-1)
    assert torch.equal(picked, argmax_idx), (
        "near-zero-tau anneal soft-block must select the argmax per block")
    # sign agreement at the picked entries
    sel_sign = torch.sign(torch.gather(zb, -1, argmax_idx.unsqueeze(-1)).squeeze(-1))
    soft_sign = torch.sign(torch.gather(soft_hb, -1, picked.unsqueeze(-1)).squeeze(-1))
    assert torch.equal(soft_sign[sel_sign != 0], sel_sign[sel_sign != 0]), \
        "anneal soft-block sign must match sign(z) at the winner"

    # 3. train-loss-floored detector.
    floored, frac = _train_loss_floored(
        [{"step": s, "rkd": r} for s, r in
         [(0, 1.0), (1, 0.5), (2, 0.2), (3, 0.11), (4, 0.105), (5, 0.10)]])
    assert floored, f"expected floored=True for a plateaued loss, got {floored}"
    not_floored, _ = _train_loss_floored(
        [{"step": s, "rkd": r} for s, r in
         [(0, 1.0), (1, 0.8), (2, 0.6), (3, 0.4), (4, 0.2), (5, 0.05)]])
    assert not not_floored, "expected floored=False for a still-descending loss"

    # 4. verdict bands: cardinality / algebra / regression / B-lift / B-dead /
    #    marginal / Gate-D.
    arms = ["HARD_STE", "ANNEAL_STE", "ANNEAL_STE_W2X"]

    def _fake_units(alg=1.0, shuf=0.01):
        units = [{"unit": "u0", "arm": "x", "kind": "k"}]
        for arm in arms:
            units += [
                {"unit": f"keyed::{arm}_RANDOM_BLOCK::J5", "arm": f"{arm}_RANDOM_BLOCK",
                 "kind": "keyed", "J": 5, "acc_at1": 0.99, "hit_any_member": 0.99},
                {"unit": f"keyed::{arm}_BLOCK_LAST::J5", "arm": f"{arm}_BLOCK_LAST",
                 "kind": "keyed", "J": 5, "acc_at1": alg, "hit_any_member": alg},
                {"unit": f"keyed::{arm}_BLOCK_BESTVAL::J5", "arm": f"{arm}_BLOCK_BESTVAL",
                 "kind": "keyed", "J": 5, "acc_at1": alg, "hit_any_member": alg},
                {"unit": f"shuffled_key::{arm}_BLOCK_LAST::J5", "arm": f"{arm}_BLOCK_LAST",
                 "kind": "shuffled_key", "J": 5, "acc_at1": shuf, "hit_any_member": shuf},
            ]
        return units

    def _rec(rets, hi80s=None, floored=True):
        hi80s = hi80s or {a: 0.83 for a in arms}
        return {a: {"ste_mode": "hard" if a == "HARD_STE" else "anneal",
                    "mlp_hidden": 4096 if a == "ANNEAL_STE_W2X" else 2048,
                    "train_loss_floored": floored,
                    "final": {"spearman_all": 0.83, "ret_agree10": rets[a],
                              "hi80_cos": hi80s[a], "hi80_calib_err": 0.4}}
                for a in arms}

    def _pad(units, n=28):
        u = list(units)
        while len(u) < n:
            u.append({"unit": f"pad{len(u)}", "arm": "pad", "kind": "pad"})
        return u

    v_pass, m_pass = _verdict_ste(
        _pad(_fake_units()), _rec({"HARD_STE": 0.21, "ANNEAL_STE": 0.28, "ANNEAL_STE_W2X": 0.31}),
        arms, "HARD_STE", "ANNEAL_STE", "ANNEAL_STE_W2X", 28, "full")
    assert v_pass == "HARD_PASS" and "LEVER_B_ANNEALED_STE_LIFTS_RETRIEVAL" in m_pass, \
        f"selftest: expected B-lift HARD_PASS got {v_pass} ({m_pass})"

    v_dead, m_dead = _verdict_ste(
        _pad(_fake_units()), _rec({"HARD_STE": 0.21, "ANNEAL_STE": 0.22, "ANNEAL_STE_W2X": 0.23}),
        arms, "HARD_STE", "ANNEAL_STE", "ANNEAL_STE_W2X", 28, "full")
    assert v_dead == "HARD_FAIL" and "LEVER_B_DEAD_STE_BIAS_NOT_THE_GAP" in m_dead, \
        f"selftest: expected B-dead HARD_FAIL got {v_dead} ({m_dead})"

    v_marg, m_marg = _verdict_ste(
        _pad(_fake_units()), _rec({"HARD_STE": 0.21, "ANNEAL_STE": 0.24, "ANNEAL_STE_W2X": 0.26}),
        arms, "HARD_STE", "ANNEAL_STE", "ANNEAL_STE_W2X", 28, "full")
    assert v_marg == "MIDDLE_BAND" and "LEVER_B_MARGINAL_LIFT" in m_marg, \
        f"selftest: expected marginal MIDDLE_BAND got {v_marg} ({m_marg})"

    v_reg, m_reg = _verdict_ste(
        _pad(_fake_units()),
        _rec({"HARD_STE": 0.21, "ANNEAL_STE": 0.28, "ANNEAL_STE_W2X": 0.31},
             hi80s={"HARD_STE": 0.83, "ANNEAL_STE": 0.79, "ANNEAL_STE_W2X": 0.80}),
        arms, "HARD_STE", "ANNEAL_STE", "ANNEAL_STE_W2X", 28, "full")
    assert v_reg == "HARD_FAIL" and "ANNEAL_REGRESSES_CALIBRATION" in m_reg, \
        f"selftest: expected calibration-regression HARD_FAIL got {v_reg} ({m_reg})"

    v_gd, m_gd = _verdict_ste(
        _pad(_fake_units()), _rec({"HARD_STE": 0.05, "ANNEAL_STE": 0.12, "ANNEAL_STE_W2X": 0.14}),
        arms, "HARD_STE", "ANNEAL_STE", "ANNEAL_STE_W2X", 28, "full")
    assert v_gd == "HARD_FAIL" and "REGIME_OR_INVOCATION_MISMATCH" in m_gd, \
        f"selftest: expected Gate-D control-out-of-band HARD_FAIL got {v_gd} ({m_gd})"

    v_alg, m_alg = _verdict_ste(
        _pad(_fake_units(alg=0.20)),
        _rec({"HARD_STE": 0.21, "ANNEAL_STE": 0.28, "ANNEAL_STE_W2X": 0.31}),
        arms, "HARD_STE", "ANNEAL_STE", "ANNEAL_STE_W2X", 28, "full")
    assert v_alg == "HARD_FAIL" and "FALSE_WIN_ALGEBRA" in m_alg, \
        f"selftest: expected algebra-break HARD_FAIL got {v_alg} ({m_alg})"

    v_card, m_card = _verdict_ste(
        _fake_units()[:5], _rec({"HARD_STE": 0.21, "ANNEAL_STE": 0.28, "ANNEAL_STE_W2X": 0.31}),
        arms, "HARD_STE", "ANNEAL_STE", "ANNEAL_STE_W2X", 28, "full")
    assert v_card == "HARD_FAIL" and "CARDINALITY_BREACH" in m_card

    v_smk, m_smk = _verdict_ste(
        _pad(_fake_units()), _rec({"HARD_STE": 0.21, "ANNEAL_STE": 0.22, "ANNEAL_STE_W2X": 0.23}),
        arms, "HARD_STE", "ANNEAL_STE", "ANNEAL_STE_W2X", 28, "smoke")
    assert v_smk == "HARD_PASS" and "SMOKE_MACHINERY_OK" in m_smk, \
        f"selftest: expected SMOKE_MACHINERY_OK got {v_smk} ({m_smk})"

    # 5. reachability.
    assert (CODE_CEILING_RET_K128 - 0.2112) > DELTA_B_HARD_PASS_MIN, \
        "selftest: HARD_PASS delta_B not reachable within code-ceiling gap"

    # 6. tiny end-to-end: BOTH ste_modes train + produce DISTINCT hard codes
    #    (ARMS-MUST-DIFFER on the STE axis) via the ONE trainer.
    n_dim, v_syn = 256, 400
    torch.manual_seed(11)
    Xsyn = torch.randn(v_syn, 64)
    Xsyn = Xsyn / Xsyn.norm(dim=-1, keepdim=True)
    Xval_syn = Xsyn[:40].contiguous()
    Xtest_syn = Xsyn[40:64].contiguous()
    kb_syn, blk_syn = 16, 16

    def _dq(student):
        return v3._dense_spearman_quick(student, Xval_syn[:20], 300, 3)

    def _df(student):
        return v3._dense_spearman_quick(student, Xval_syn, 500, 3)

    import tempfile
    code_by_mode = {}
    orig = v3.MLP_HIDDEN
    try:
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            for arm, (ste_mode, width) in (("Hh", ("hard", 32)), ("Aa", ("anneal", 32))):
                st_last, diag_st = _train_student_v6(
                    ste_mode, width, kb_syn, blk_syn, Xsyn, 40, 24, 4, 13, "cpu",
                    tdp / f"ckpt_{arm}.pt", tdp / f"ckpt_best_{arm}.pt", 100, tdp, t0,
                    _dq, _df, 8, 2, TAU_HI, TAU_LO, ANNEAL_FRAC, CONS_WEIGHT, arm)
                assert int(st_last.net[0].out_features) == width
                assert math.isfinite(diag_st["rkd_last"])
                assert diag_st["ste_mode"] == ste_mode
                if ste_mode == "anneal":
                    assert math.isfinite(diag_st["cons_last"]) and diag_st["cons_last"] >= 0.0
                c_last = v3._encode_hard_block(st_last, Xtest_syn, kb_syn, blk_syn)
                assert c_last.shape == (24, kb_syn * blk_syn)
                assert torch.isfinite(c_last).all()
                code_by_mode[arm] = hashlib.sha256(
                    c_last.to(torch.int8).numpy().tobytes()).hexdigest()
                st_best = _reload_best_v6(width, 64, kb_syn * blk_syn, "cpu",
                                          tdp / f"ckpt_best_{arm}.pt")
                assert int(st_best.net[0].out_features) == width
                u = v3._semantic_unit(arm, c_last, c_last, Xtest_syn, Xtest_syn, 0, 500, 3)
                assert "ret_agree10" in u and "hi80_cos" in u
    finally:
        v3.MLP_HIDDEN = orig
    assert code_by_mode["Hh"] != code_by_mode["Aa"], \
        "selftest: hard vs anneal STE produced identical hard codes (AF)"
    assert v3.MLP_HIDDEN == orig, "selftest: MLP_HIDDEN not restored"

    # 7. determinism idempotence.
    d1 = _pin_determinism(7)
    d2 = _pin_determinism(7)
    assert d1["torch_version"] == d2["torch_version"]

    print(f"[selftest] PASS (tau schedule hi->lo->hold + anneal-soft-block->argmax as "
          f"tau->0 + sign match + train-loss-floored detector + B-lift/B-dead/marginal/"
          f"calibration-regression/Gate-D/algebra/cardinality/smoke verdict bands + "
          f"reachability + ONE trainer at hard&anneal STE -> distinct hard codes + "
          f"best-reload + MLP_HIDDEN restored + determinism) "
          f"elapsed={time.perf_counter() - t0:.2f}s", flush=True)
    return 0
