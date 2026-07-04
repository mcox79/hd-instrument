"""Encoder OBJECTIVE-FAMILY SWAP: MSE-RKD (control, reproduces the existing
in-batch-RKD-only decline / ret_agree10~0.21) vs KL-RANK (new distributional /
rank-aware objective), PAIRED at FULL 178k, in-batch, NCE off. Matched
EVERYTHING ELSE (mining, split, seed, batch-index sequence, student init,
steps, eval cadence) -- ONLY the RKD loss FORMULA differs between arms.

THREE CONVERGENT EVIDENCE LINES motivating this cell (do not re-litigate):
  1. seed_13's own trajectory analysis (v3e HARD_FAIL verdict_msg,
     MEASURED@data/exp_encoder_v3e_decline_vs_plateau_v1_seed13/metrics.json):
     "removing NCE only SLOWED the in_batch collapse; the true asymptote
     likely requires an objective-family change (KL/PKT-style swap), not a
     longer NCE-off run" [final_block=0.9144(TEST spearman, mostly-random
     pairs) final_ret_agree10=0.2105 early_minus_late=0.1243 (still
     declining)].
  2. Metric drill (notes/research_drill_encoder_target_metric_coarse_cosine_
     vs_fine_retrieval_2026-07-04.md): the real downstream goal is RETRIEVAL
     (ret_agree10), currently 0.21 vs target >=0.35; the K=128 code itself
     supports a zero-training ceiling of ~0.48 (MEASURED@data/
     exp_encoder_teacher_sparsifier_bypass_v1_selftest/metrics.json, true
     177899-cache, n_test=800) -- so the 0.21-vs-0.48 gap is a TRAINING
     problem, not a code-capacity problem.
  3. Cardinality drill (notes/research_drill_encoder_cardinality_capacity_
     ceiling_0.85_reachability_2026-07-04.md): the top-ranked structural
     lever (Rank 1, P_deflated=0.50) is a "rank-aware / anisotropic
     quantization loss" -- reweight the RKD objective toward the
     ranking-relevant projection of similarity, not raw magnitude
     reconstruction (direct analog: Guo et al. ScaNN, arXiv:1908.10396,
     VERIFIED via fetch in that drill) -- code-widening (K=256) is a real but
     SECOND-ORDER lever (Rank 3), not the first one to pull.

HYPOTHESIS: the current MSE-RKD objective (`l_rkd = mean((S_cos - T_cos)^2)`
over off-diagonal in-batch pairs) matches BULK pairwise geometry (adequate
hi80_cos=0.828, near the 0.85 coarse target) but does NOT optimize NEAR-
NEIGHBOR RANKING (weak ret_agree10=0.21) and does not converge (declines
post-floor). A RANK-AWARE / DISTRIBUTIONAL objective that directly targets
"which of my batch-mates am I closest to" (a listwise, softmax-normalized
target) should lift ret_agree10 without sacrificing coarse calibration or
algebra.

OBJECTIVE CHOSEN (ONE, well-justified -- not diluting across many
under-tested variants per "no padding experiments"): KL-RANK -- a
temperature-scaled, in-batch, off-diagonal SOFTMAX-KL distillation loss
(CompRess/PKT-style relational-KD: Koohpayegani et al. "CompRess", NeurIPS
2020; Passalis & Tefas "Probabilistic Knowledge Transfer", ECCV 2018).
Per batch: convert BOTH the teacher's and the student's in-batch cosine-
similarity ROW (masked at the self-position) into a softmax probability
distribution over "which other batch item am I most similar to", at a fixed
temperature TAU_KL, then minimize KL(teacher_row || student_row), averaged
over rows. This is a LISTWISE, RANK-SENSITIVE signal by construction (softmax
concentrates on the few highest-similarity neighbors, exactly what
ret_agree10 measures) rather than a magnitude-regression signal that treats
every pair (near or far) with equal weight. Reuses the SAME in-batch
[batch x batch] similarity matrices the MSE-RKD control already computes --
zero extra forward passes, same O(batch^2) cost, same masking convention
(`masked_fill(eye, -1e4)`, matching the existing NCE self-similarity mask at
experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_
concept_encoder_v1_core.py:427-428) -- near-zero incremental compute cost.
TAU_KL=0.10 (HYPOTHESIZED@this prereg, slightly softer than the existing
TAU_NCE=0.07 since this loss must carry a full ~127-way row distribution, not
a 1-vs-many top-1 classification; not swept this cell -- a temperature sweep
is a cheap, well-scoped follow-up IF this cell lands MIDDLE_BAND).

PAIRED-TRIALS DESIGN (mandatory per feedback_paired_trials_mandatory_for_arm_
comparison_discriminators_2026-07-04): both arms are trained by the SAME
local function `_train_student_full_swap`, differing ONLY in the `loss_family`
string branch that computes `l_rkd`. Both arms receive the IDENTICAL `seed`
(-> identical `_make_student` init via `torch.manual_seed(seed)`) and consume
`gen` in the IDENTICAL order (`_cluster_batch_idx` -> semi-hard negatives ->
fallback negatives -- the loss-family branch adds NO extra random draws), so
both arms see the token-for-token IDENTICAL batch/negative sequence. The MSE
branch is a byte-for-byte copy of `v3c._train_student_full`'s `objective=
"in_batch"` formula (verified in self-test: bit-close reproduction against
`v3c._train_student_full` itself on tiny synthetic data, same seed) -- this
proves the copy is faithful BEFORE trusting the KL branch sits fairly
alongside it (guards against a copy-paste bug masquerading as an "objective
effect").

Unchanged validated machinery (v2/v3/v3c/v3e): MLP student (1024->2048 GELU
->4096), block codes (K=128, L=32, 3.125% sparse), block-STE, SBC
block-local circular-convolution algebra, semi-hard mining, warmup+cosine LR,
3-way train/val/test split (TEST never used for selection), FINAL-step is the
PRIMARY gated number (best-by-VAL-on-TEST is SECONDARY context), headline
ret_agree10/hi80_cos fields, trend-slope plateau/decline diagnostic (reused
directly from v3e, not reimplemented).

Composition algebra (prereg field): SBC_block_local_circular_convolution.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke/full gate (sha256 over all code matrices)
- final_metrics_atomicity: tmp_replace (write_metrics helper + ckpt os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
- crlb_floor_computed: r_max=0.901 at K=128 (THEORETICAL@v2/v3/v3b/v3c/v3e
  prereg, unchanged -- same K=128/N=4096 quantization channel; the loss
  FAMILY does not change the quantization channel's information ceiling)
- baseline_in_band: CHARPOS ret_agree10 in (0.05, 0.95)
- discriminator-survives-scale: option (B) analytical justification, same as
  the whole v3-lineage: smoke's tiny V_train=3000 cannot reproduce the true
  near-neighbor coverage-ratio effect that makes MSE-RKD collapse at scale;
  smoke validates MACHINERY ONLY (both loss families train end-to-end, 3-way
  split partitions correctly, trend-slope runs on a real trajectory,
  cardinality holds, KL loss stays finite/non-negative). The actual
  objective-family discriminator needs the true 177899-concept corpus AND
  the full 6000-step budget -- that IS the FULL dispatch.
- HARD_PASS strictly above floor per prereg bands (META_RULE_L)
- HP_SCOPE: HARD_PASS/HARD_FAIL bands apply to KL_BLOCK_LAST only (the arm
  under test). MSE_BLOCK_LAST is the control/reproduction (must itself stay
  in-band per baseline_in_band + algebra, but is NOT separately HARD_PASS/
  HARD_FAIL gated on ret_agree10 -- its role is to reproduce the KNOWN
  decline as a live-in-this-run control, not to be judged). *_BESTVAL units
  are comparison/context, NOT separately gated. RANDOM_BLOCK/CHARPOS/
  shuffled_key are integrity-only.
- cardinality_ok: EXPECTED_N_UNITS=17 both run_modes (SMOKE=FULL code path)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime (identical hyperparameters to
  the validated v3/v3c/v3e lineage; only the RKD loss FORMULA + TAU_KL differ)
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ / VERIFIED@

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01):
  query "objective family swap KL divergence rank-aware distillation loss
  softmax similarity distribution retrieval agreement encoder" -> top hit
  cosine=0.3604, entity is an AUDIT-LOG MIA-detection method ("KL divergence
  of observed [retrieval] score distribution from expected [calibrated]" --
  notes/research_drill_substrate_evaluation_methodology_5x_chain1_drill3_
  2026-06-07.md) -- KL used there for anomaly/attack DETECTION over query
  logs, a completely DIFFERENT domain from a distillation TRAINING objective.
  Remaining hits <=0.3564 (a pretest prereg's generic "reference distribution"
  field, WordNet lexical entries for "distribution"/"distribution_agreement").
  NONE at cosine>0.30 for a DISTINCT prior CELL testing a KL/rank-aware
  distillation objective for this encoder. GENUINELY NOVEL.

Prereg: preregs/2026-07-04_exp_encoder_objective_swap_kl_rank_v1.md
Parent cells (read-only imports, NOT edited):
  experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py (as v3)
  experiments/exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py (as v3c)
  experiments/exp_encoder_v3e_decline_vs_plateau_v1_core.py (as v3e -- reuses `_trend_diagnostic` verbatim)
Does NOT touch v3/v3b/v3c/v3e's own artifact/checkpoint directories, nor the
concurrently-in-flight v4 (convergence LR-hold) / v5 (K128 vs K256 capacity)
lanes (a0ff3e's lane) -- distinct anchor name, distinct artifact dir, distinct
prereg, no shared files edited.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import copy
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
ANCHOR_NAME = "encoder_objective_swap_kl_rank_v1"
SEED_DEFAULT = v3.SEED_DEFAULT  # 7

TEACHER_CACHE_DEFAULT = v3c.TEACHER_CACHE_DEFAULT  # pinned 177899-concept cache

NCE_WEIGHT = 0.0   # NCE off, matches v3c/v3e's winning ablation config

TAU_KL = 0.10      # HYPOTHESIZED@this prereg (softer than TAU_NCE=0.07; see docstring)

LOSS_FAMILIES = ("mse_rkd", "kl_rank")
ARM_KEY = {"mse_rkd": "MSE", "kl_rank": "KL"}

# ---- FULL-scale config: IDENTICAL to v3e (apples-to-apples baseline match) ----
FULL_BATCH = 128
FULL_STEPS = 6000
CKPT_EVERY_STEPS_FULL = 500
DENSE_EVAL_EVERY_FULL = 50
FULL_TRIALS = v3.MID_TRIALS               # 60 (keyed n_trials)
FULL_CHARPOS_CAP = v3.MID_CHARPOS_CAP

VAL_CAP = 5000
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
SMOKE_VAL_CAP = 200
SMOKE_VAL_QUICK_SUB = 120
SMOKE_VAL_QUICK_PAIRS = 3_000
SMOKE_VAL_FULL_PAIRS = 5_000
SMOKE_TEST_FINAL_PAIRS = 8_000
SMOKE_CHARPOS_CAP = 300
SMOKE_TRIALS = 20

MIN_STEP_FRAC_FOR_BEST = 0.05
MIN_TREND_POINTS = v3e.MIN_TREND_POINTS

# semantic: {MSE,KL} x {DENSE,BLOCK} x {LAST,BESTVAL} = 8, + RANDOM_BLOCK + CHARPOS = 10
# keyed: RANDOM_BLOCK posctrl (1) + {MSE,KL} x {LAST,BESTVAL} keyed (4)
#        + {MSE,KL} LAST-shuffled (2) = 7
# total = 17
EXPECTED_N_UNITS_FULL = 17
EXPECTED_N_UNITS_SMOKE = 17

PREREG_BASELINE_ARMS = ["CHARPOS", "RANDOM_BLOCK", "MSE_BLOCK_LAST", "MSE_BLOCK_BESTVAL"]

# ---- Pre-reg bands (HYPOTHESIZED@this prereg unless tagged otherwise) ------
# KL_RANK is the arm under test; MSE_RKD is the live control/reproduction.
KL_RET_AGREE10_HARD_PASS = 0.35     # per task spawn: "materially closes gap toward ~0.48 ceiling"
KL_RET_AGREE10_HARD_FAIL_CEILING = 0.25  # "no material movement" vs MSE control's ~0.2105
KL_HI80_COS_HARD_PASS = 0.82        # "must not regress below ~0.82" (coarse target, near-closed)
KL_HI80_COS_HARD_FAIL_FLOOR = 0.75  # material regression on the coarse metric
ALGEBRA_FLOOR = 0.90                # unchanged lineage convention ("must stay ~1.0")
PLATEAU_EARLY_MINUS_LATE_MAX = 0.03 # reused v3e convention: <= this = essentially flat
DECLINE_EARLY_MINUS_LATE_MIN = 0.10 # reused v3e convention: >= this = clearly still declining


def _artifact_dir(run_mode: str, run_tag: str = "") -> Path:
    suffix = {"smoke": "_smoke"}.get(run_mode, "")
    tag = f"_{run_tag}" if run_tag else ""
    return _REPO / "data" / f"substrate_concept_encoder_objswap_kl{tag}{suffix}"


# ---------------------------------------------------------------------------
# Defensive helpers (start marker / crash metrics / heartbeat) -- mirrors v3e.
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
# THE NEW MECHANISM: paired training loop supporting BOTH loss families.
# A near-verbatim copy of v3c._train_student_full's loop structure; the ONLY
# semantic difference from v3c is the `l_rkd` computation branch (mse_rkd is
# a byte-for-byte copy of v3c's "in_batch" formula; kl_rank is new). Every
# other line (batch construction, NCE term, optimizer, LR schedule,
# checkpointing, dense eval, best-ckpt tracking) is unchanged so the ONLY
# variable that differs between arms is the loss family (paired-trials
# discipline).
# ---------------------------------------------------------------------------

def _rkd_loss(x: torch.Tensor, s_n: torch.Tensor, batch: int, device: str,
              loss_family: str, tau_kl: float) -> torch.Tensor:
    """Compute the RKD loss term for one training step.

    x: [batch, in_dim] teacher embeddings (unit-norm rows, no grad).
    s_n: [batch, out_dim] L2-normalized student block-STE codes (grad-carrying).
    """
    T = x @ x.T  # teacher in-batch cosine (unit-norm rows per cache convention)
    eye_mask = torch.eye(batch, dtype=torch.bool, device=device)
    if loss_family == "mse_rkd":
        off = ~eye_mask
        return (((s_n @ s_n.T) - T)[off] ** 2).mean()
    if loss_family == "kl_rank":
        S = s_n @ s_n.T
        # Same masking convention as the existing NCE self-similarity mask
        # (v3._train_student_full-style: divide by temperature FIRST, then
        # masked_fill with a large-negative FINITE constant -- avoids the
        # 0*(-inf - -inf)=NaN hazard of literal -inf on both sides).
        T_logits = (T / tau_kl).masked_fill(eye_mask, -1e4)
        S_logits = (S / tau_kl).masked_fill(eye_mask, -1e4)
        T_prob = torch.softmax(T_logits, dim=1).detach()
        S_logprob = torch.log_softmax(S_logits, dim=1)
        return torch.nn.functional.kl_div(S_logprob, T_prob, reduction="batchmean")
    raise ValueError(f"unknown loss_family {loss_family}")


def _train_student_full_swap(
    kb: int, blk_l: int,
    Xtr: torch.Tensor, pos_idx: torch.Tensor, semi_cands: torch.Tensor,
    steps: int, batch: int, warmup: int, seed: int, device: str,
    ckpt_path: Path, best_ckpt_path: Path, ckpt_every: int,
    output_dir: Path, t0: float,
    nce_weight: float, arm_label: str, loss_family: str, tau_kl: float,
    dense_eval_quick_fn: Optional[Callable] = None,
    dense_eval_full_fn: Optional[Callable] = None,
    dense_eval_every: int = 0,
    min_step_for_best: int = 0,
) -> Tuple[torch.nn.Module, Dict]:
    if loss_family not in LOSS_FAMILIES:
        raise ValueError(f"unknown loss_family {loss_family}")
    out_dim = kb * blk_l
    student = v3._make_student("mlp", Xtr.shape[1], out_dim, device, seed)
    opt = torch.optim.Adam(student.parameters(), lr=v3.LR)
    gen = torch.Generator().manual_seed(seed)
    start_step = 0
    dense_traj: List[Dict[str, float]] = []
    best_state = {"score": -2.0, "step": -1}
    alltime_state = {"score": -2.0, "step": -1}
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
            alltime_state["score"] = float(ck.get("alltime_score", -2.0))
            alltime_state["step"] = int(ck.get("alltime_step", -1))
            print(f"[objswap_kl] resume {arm_label} at step {start_step}", flush=True)
        except (RuntimeError, KeyError, EOFError) as exc:
            print(f"[objswap_kl] WARN ckpt load failed ({type(exc).__name__}); "
                  f"retraining {arm_label} from scratch", flush=True)
            start_step = 0
            dense_traj = []
            best_state = {"score": -2.0, "step": -1}
            alltime_state = {"score": -2.0, "step": -1}
    V = Xtr.shape[0]
    Xd = Xtr.to(device)
    loss_first = loss_last = None
    rkd_last = nce_last = lr_last = None

    def _maybe_save_best(step_i: int, d_full: float) -> None:
        if not math.isfinite(d_full):
            return
        if d_full > alltime_state["score"]:
            alltime_state["score"] = d_full
            alltime_state["step"] = step_i
        if step_i < min_step_for_best:
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
        bidx = v3._cluster_batch_idx(batch, 0.0, V, pos_idx, semi_cands, gen)
        x = Xd[bidx.to(device)]
        z = student(x)
        s = v3._block_ste(z, kb, blk_l)
        s_n = s / (s.norm(dim=-1, keepdim=True) + 1e-8)

        l_rkd = _rkd_loss(x, s_n, batch, device, loss_family, tau_kl)

        p_ = pos_idx[bidx]
        cols = torch.randint(0, v3.N_SEMI_CANDS, (batch, v3.N_NEG_PER_ANCHOR),
                             generator=gen)
        negs = torch.gather(semi_cands[bidx], 1, cols)
        fallback = torch.randint(0, V, (batch, v3.N_NEG_PER_ANCHOR), generator=gen)
        negs = torch.where(negs < 0, fallback, negs)
        cand_idx = torch.cat([p_.unsqueeze(1), negs], dim=1)
        zc = student(Xd[cand_idx.reshape(-1).to(device)])
        sc = v3._block_ste(zc, kb, blk_l)
        sc = sc.reshape(batch, 1 + v3.N_NEG_PER_ANCHOR, -1)
        sc_n = sc / (sc.norm(dim=-1, keepdim=True) + 1e-8)
        lg_h = torch.einsum("bd,bcd->bc", s_n, sc_n) / v3.TAU_NCE
        lg_i = (s_n @ s_n.T / v3.TAU_NCE).masked_fill(
            torch.eye(batch, dtype=torch.bool, device=device), -1e4)
        l_nce = torch.nn.functional.cross_entropy(
            torch.cat([lg_h, lg_i], dim=1),
            torch.zeros(batch, dtype=torch.long, device=device))
        loss = l_rkd + nce_weight * l_nce
        if not torch.isfinite(loss):
            raise RuntimeError(
                f"failure_class=NAN_LOSS: {arm_label} loss non-finite at step {step} "
                f"(l_rkd={float(l_rkd.detach())}, l_nce={float(l_nce.detach())}, "
                f"nce_w={nce_weight}, loss_family={loss_family})")
        opt.zero_grad()
        loss.backward()
        opt.step()
        v_loss = float(loss.detach())
        v_rkd = float(l_rkd.detach())
        v_nce = float(l_nce.detach())
        if loss_first is None:
            loss_first = v_loss
        loss_last, rkd_last, nce_last, lr_last = v_loss, v_rkd, v_nce, cur_lr
        if step % 200 == 0:
            print(f"[objswap_kl] {arm_label} ({loss_family}) step {step}/{steps} "
                  f"rkd={v_rkd:.4f} nce={v_nce:.4f} nce_w={nce_weight:.3f} "
                  f"lr={cur_lr:.2e} ({time.perf_counter() - t0:.1f}s)", flush=True)
            _emit_heartbeat(output_dir, step, steps, time.perf_counter() - t0,
                            extra={"phase": f"train_{arm_label}", "loss": v_loss,
                                   "rkd": v_rkd})
        if (dense_eval_full_fn is not None and dense_eval_every > 0
                and step % dense_eval_every == 0):
            d_full = float(dense_eval_full_fn(student))
            d_quick = (float(dense_eval_quick_fn(student))
                       if dense_eval_quick_fn is not None else float("nan"))
            dense_traj.append({"step": step, "dense_full": d_full,
                               "dense_quick": d_quick, "rkd": v_rkd, "final": False})
            print(f"[objswap_kl] {arm_label} DENSE-traj step {step}: "
                  f"full={d_full:.4f} quick={d_quick:.4f}", flush=True)
            _maybe_save_best(step, d_full)
        if (step + 1) % ckpt_every == 0 or (step + 1) == steps:
            tmp = ckpt_path.with_suffix(".tmp")
            torch.save({"student": student.state_dict(), "opt": opt.state_dict(),
                       "gen_state": gen.get_state(), "step": step + 1,
                       "dense_traj": dense_traj, "best_score": best_state["score"],
                       "best_step": best_state["step"],
                       "alltime_score": alltime_state["score"],
                       "alltime_step": alltime_state["step"]}, str(tmp))
            os.replace(str(tmp), str(ckpt_path))
    if dense_eval_full_fn is not None:
        d_full_fin = float(dense_eval_full_fn(student))
        d_quick_fin = (float(dense_eval_quick_fn(student))
                       if dense_eval_quick_fn is not None else float("nan"))
        dense_traj.append({"step": steps, "dense_full": d_full_fin,
                           "dense_quick": d_quick_fin,
                           "rkd": rkd_last if rkd_last is not None else float("nan"),
                           "final": True})
        _maybe_save_best(steps, d_full_fin)
        print(f"[objswap_kl] {arm_label} FINAL step {steps}: full={d_full_fin:.4f} "
              f"quick={d_quick_fin:.4f}", flush=True)
    best_ckpt_fallback_to_final = best_state["step"] < 0
    if best_ckpt_fallback_to_final:
        tmp_b = best_ckpt_path.with_suffix(".tmp")
        torch.save({"student": student.state_dict(), "step": steps,
                   "dense_full": float("nan"), "arm": arm_label}, str(tmp_b))
        os.replace(str(tmp_b), str(best_ckpt_path))
        print(f"[objswap_kl] WARN {arm_label}: no eval point >= min_step_for_best; "
              f"best-ckpt falls back to FINAL student", flush=True)
    return student, {
        "loss_first": loss_first if loss_first is not None else -1.0,
        "loss_last": loss_last if loss_last is not None else -1.0,
        "rkd_last": rkd_last if rkd_last is not None else -1.0,
        "nce_last": nce_last if nce_last is not None else -1.0,
        "lr_last": lr_last if lr_last is not None else -1.0,
        "nce_weight": nce_weight,
        "arm": arm_label, "loss_family": loss_family, "tau_kl": tau_kl,
        "batch": batch,
        "dense_traj": dense_traj,
        "best_dense_full": best_state["score"], "best_step": best_state["step"],
        "best_ckpt_fallback_to_final": best_ckpt_fallback_to_final,
        "alltime_best_dense_full": alltime_state["score"],
        "alltime_best_step": alltime_state["step"],
    }


# ---------------------------------------------------------------------------
# Verdict logic.
# ---------------------------------------------------------------------------

def _verdict_swap(per_unit: List[Dict], recovery: Dict, expected_units: int,
                  run_mode: str) -> Tuple[str, str]:
    if len(per_unit) < expected_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"{len(per_unit)}/{expected_units} units")
    posc = v3._by_unit(per_unit, "keyed", "RANDOM_BLOCK", 5)
    kl_prim = v3._by_unit(per_unit, "keyed", "KL_BLOCK_LAST", 5)
    kl_shuf = v3._by_unit(per_unit, "shuffled_key", "KL_BLOCK_LAST", 5)
    mse_prim = v3._by_unit(per_unit, "keyed", "MSE_BLOCK_LAST", 5)
    mse_shuf = v3._by_unit(per_unit, "shuffled_key", "MSE_BLOCK_LAST", 5)
    if any(u is None for u in (posc, kl_prim, kl_shuf, mse_prim, mse_shuf)):
        return ("HARD_FAIL", "HARD_FAIL_MISSING_GATE_UNITS")
    if posc["acc_at1"] < 0.98:
        return ("HARD_FAIL",
                f"HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH: RANDOM_BLOCK keyed J=5 "
                f"{posc['acc_at1']:.3f} < 0.98 (SBC lossless prior)")
    if kl_shuf["acc_at1"] > 0.05 or kl_shuf["hit_any_member"] > 0.10:
        return ("HARD_FAIL",
                f"HARD_FAIL_SHUFFLED_KEY_LEAK_KL: {kl_shuf['acc_at1']:.3f}/"
                f"{kl_shuf['hit_any_member']:.3f}")
    if mse_shuf["acc_at1"] > 0.05 or mse_shuf["hit_any_member"] > 0.10:
        return ("HARD_FAIL",
                f"HARD_FAIL_SHUFFLED_KEY_LEAK_MSE: {mse_shuf['acc_at1']:.3f}/"
                f"{mse_shuf['hit_any_member']:.3f}")

    kl_trend = recovery["kl_trend"]
    tail = (f"[KL: ret_agree10={recovery['kl_final_ret_agree10']:.4f} "
           f"hi80_cos={recovery['kl_final_hi80_cos']:.4f} "
           f"early_minus_late={kl_trend.get('early_minus_late')} "
           f"keyed_J5={kl_prim['acc_at1']:.3f} | "
           f"MSE(control): ret_agree10={recovery['mse_final_ret_agree10']:.4f} "
           f"hi80_cos={recovery['mse_final_hi80_cos']:.4f} "
           f"keyed_J5={mse_prim['acc_at1']:.3f} | "
           f"delta_ret_agree10={recovery['delta_ret_agree10']:.4f}]")

    if run_mode == "smoke":
        fails = []
        if not kl_trend.get("sufficient", False):
            fails.append("S_kl_trend_insufficient_points")
        if not math.isfinite(recovery["kl_final_ret_agree10"]):
            fails.append("S_kl_ret_agree10_missing")
        if not math.isfinite(recovery["kl_final_hi80_cos"]):
            fails.append("S_kl_hi80_cos_missing")
        if not math.isfinite(recovery["mse_final_ret_agree10"]):
            fails.append("S_mse_ret_agree10_missing")
        if fails:
            return ("SMOKE_GATE_FAIL", "; ".join(fails))
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: both loss families train end-to-end, "
                f"3-way split partitions correctly, trend-slope diagnostic "
                f"runs on a real multi-point trajectory for KL_RANK, headline "
                f"ret_agree10/hi80_cos fields populate for both arms {tail} "
                f"(the objective-family discriminator is a FULL-only "
                f"question; smoke's tiny V_train cannot reproduce it)")

    # full: algebra gate applies to BOTH trained arms (goal #4 non-negotiable).
    if kl_prim["acc_at1"] < ALGEBRA_FLOOR:
        return ("HARD_FAIL",
                f"FALSE_WIN_ALGEBRA_KL: keyed_roundtrip J=5 {kl_prim['acc_at1']:.3f} "
                f"< {ALGEBRA_FLOOR} (KL_RANK BLOCK code is not a valid composable "
                f"SBC code) {tail}")
    if mse_prim["acc_at1"] < ALGEBRA_FLOOR:
        return ("HARD_FAIL",
                f"FALSE_WIN_ALGEBRA_MSE_CONTROL: keyed_roundtrip J=5 "
                f"{mse_prim['acc_at1']:.3f} < {ALGEBRA_FLOOR} (control arm's own "
                f"algebra broke -- the run itself is suspect, not just the "
                f"KL comparison) {tail}")

    kl_ret = recovery["kl_final_ret_agree10"]
    kl_cos = recovery["kl_final_hi80_cos"]
    eml = kl_trend.get("early_minus_late", float("nan"))
    trend_ok = kl_trend.get("sufficient", False) and (
        eml <= PLATEAU_EARLY_MINUS_LATE_MAX or eml < DECLINE_EARLY_MINUS_LATE_MIN)
    trend_bad = kl_trend.get("sufficient", False) and eml >= DECLINE_EARLY_MINUS_LATE_MIN

    if kl_ret >= KL_RET_AGREE10_HARD_PASS and kl_cos >= KL_HI80_COS_HARD_PASS and trend_ok:
        return ("HARD_PASS",
                f"OBJECTIVE_SWAP_RECOVERS: KL_RANK lifts ret_agree10 to "
                f"{kl_ret:.4f} (>= {KL_RET_AGREE10_HARD_PASS} target) while "
                f"holding hi80_cos={kl_cos:.4f} (>= {KL_HI80_COS_HARD_PASS}) "
                f"and algebra ({kl_prim['acc_at1']:.3f}); the rank-aware "
                f"distributional objective is the fix the decline diagnosed "
                f"in v3e requires {tail}")
    if kl_ret <= KL_RET_AGREE10_HARD_FAIL_CEILING or kl_cos < KL_HI80_COS_HARD_FAIL_FLOOR \
            or trend_bad:
        return ("HARD_FAIL",
                f"OBJECTIVE_SWAP_NO_MATERIAL_LIFT: KL_RANK ret_agree10={kl_ret:.4f} "
                f"(ceiling {KL_RET_AGREE10_HARD_FAIL_CEILING}) hi80_cos={kl_cos:.4f} "
                f"(floor {KL_HI80_COS_HARD_FAIL_FLOOR}) trend_bad={trend_bad} -- the "
                f"objective-family swap did not fix the retrieval/decline problem; "
                f"escalate to K=256 widening or an OPQ-style rotation lever "
                f"(cardinality drill Ranks 2-3) {tail}")
    return ("MIDDLE_BAND",
            f"OBJECTIVE_SWAP_PARTIAL: KL_RANK shows real but partial movement "
            f"(ret_agree10={kl_ret:.4f}, hi80_cos={kl_cos:.4f}) -- neither a clean "
            f"recovery nor a clean no-lift result; consider a TAU_KL sweep or a "
            f"longer run before deciding the objective-family question {tail}")


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def run_swap(run_mode: str, seed: int, device_arg: str, n_dim: int,
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
    print(f"[objswap_kl] run_mode={run_mode} seed={seed} device={device} n_dim={n_dim} "
          f"steps={steps} batch={batch} nce_weight={NCE_WEIGHT} tau_kl={TAU_KL} "
          f"dense_eval_every={dense_every} min_step_for_best={min_step_for_best}",
          flush=True)

    effective_cache_arg = teacher_cache_arg
    if run_mode == "full" and effective_cache_arg is None:
        effective_cache_arg = TEACHER_CACHE_DEFAULT
    cache_path = v3._resolve_teacher_cache(effective_cache_arg)
    cache_bytes = cache_path.stat().st_size
    X, ids = v3._load_teacher(cache_path)
    V_cache = X.shape[0]
    print(f"[objswap_kl] teacher {cache_path.name}: {V_cache} concepts x "
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
    print(f"[objswap_kl] split train={n_tr} val={n_val} test={n_test}", flush=True)

    pos_idx, semi_cands = v3._mine_teacher(
        Xtr, device, art_dir / "_mine_shards", out_dir, t0)
    semi_cov = float((semi_cands[:, 0] >= 0).float().mean())
    print(f"[objswap_kl] mining done cov={semi_cov:.3f} "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    Xval_sub = Xval[:min(quick_sub, n_val)].contiguous()

    def _deval_quick(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xval_sub, quick_pairs, seed + 7)

    def _deval_full(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xval, val_full_pairs, seed + 7)

    in_dim = Xtr.shape[1]
    per_arm_diag: Dict[str, Dict] = {}
    per_arm_student: Dict[str, torch.nn.Module] = {}
    per_arm_bestval_student: Dict[str, torch.nn.Module] = {}

    for loss_family in LOSS_FAMILIES:
        arm_key = ARM_KEY[loss_family]
        ckpt_path = art_dir / f"_ckpt_{arm_key}.pt"
        best_ckpt_path = art_dir / f"_ckpt_best_{arm_key}.pt"
        last_student, diag = _train_student_full_swap(
            kb, blk_l, Xtr, pos_idx, semi_cands, steps, batch, warmup, seed, device,
            ckpt_path, best_ckpt_path, ckpt_every, out_dir, t0,
            NCE_WEIGHT, arm_key, loss_family, TAU_KL,
            dense_eval_quick_fn=_deval_quick, dense_eval_full_fn=_deval_full,
            dense_eval_every=dense_every, min_step_for_best=min_step_for_best)
        print(f"[objswap_kl] {arm_key} ({loss_family}) trained rkd_last={diag['rkd_last']:.4f} "
              f"best_val={diag['best_dense_full']:.4f}@step{diag['best_step']} "
              f"n_traj_points={len(diag['dense_traj'])} "
              f"({time.perf_counter() - t0:.1f}s)", flush=True)
        per_arm_diag[arm_key] = diag
        per_arm_student[arm_key] = last_student
        per_arm_bestval_student[arm_key] = v3c._reload_best_student(
            "mlp", in_dim, kb * blk_l, device, best_ckpt_path)

    arm_codes: Dict[str, torch.Tensor] = {}
    for arm_key, sfx in (("MSE", "MSE"), ("KL", "KL")):
        arm_codes[f"{sfx}_DENSE_LAST"] = v3._dense_sign_codes(per_arm_student[arm_key], Xtest)
        arm_codes[f"{sfx}_BLOCK_LAST"] = v3._encode_hard_block(per_arm_student[arm_key], Xtest, kb, blk_l)
        arm_codes[f"{sfx}_DENSE_BESTVAL"] = v3._dense_sign_codes(per_arm_bestval_student[arm_key], Xtest)
        arm_codes[f"{sfx}_BLOCK_BESTVAL"] = v3._encode_hard_block(per_arm_bestval_student[arm_key], Xtest, kb, blk_l)

    gen_ctrl = torch.Generator().manual_seed(seed + 1)
    arm_codes["RANDOM_BLOCK"] = v3._random_block_codes(n_test, kb, blk_l, gen_ctrl)
    cp_cap = min(n_test, charpos_cap)
    cp_codes = v3._charpos_codes(names_test[:cp_cap], n_dim, kb)

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
            print(f"[objswap_kl] unit {len(per_unit)}/{expected_units} {u['unit']}: "
                  + json.dumps({k: round(v, 4) for k, v in u.items()
                                if isinstance(v, float)}), flush=True)
            _emit_heartbeat(out_dir, len(per_unit), expected_units,
                            time.perf_counter() - t0, extra={"unit": u["unit"]})
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append({"fn": getattr(fn, "__name__", "?"),
                              "failure_class": type(exc).__name__,
                              "msg": str(exc)[:300]})
            raise

    for label in ("MSE_DENSE_LAST", "MSE_BLOCK_LAST", "MSE_DENSE_BESTVAL", "MSE_BLOCK_BESTVAL",
                  "KL_DENSE_LAST", "KL_BLOCK_LAST", "KL_DENSE_BESTVAL", "KL_BLOCK_BESTVAL"):
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
    for sfx in ("MSE", "KL"):
        _run_unit(v3._keyed_unit, f"{sfx}_BLOCK_LAST", "sbc",
                  arm_codes[f"{sfx}_BLOCK_LAST"], kb, blk_l, 5, n_trials, gen_eval, device)
        _run_unit(v3._keyed_unit, f"{sfx}_BLOCK_BESTVAL", "sbc",
                  arm_codes[f"{sfx}_BLOCK_BESTVAL"], kb, blk_l, 5, n_trials, gen_eval, device)
        _run_unit(v3._keyed_unit, f"{sfx}_BLOCK_LAST", "sbc",
                  arm_codes[f"{sfx}_BLOCK_LAST"], kb, blk_l, 5, n_trials, gen_eval,
                  device, shuffled_key=True)

    def _sp(arm):
        return v3._by_unit(per_unit, "semantic", arm)

    mse_block_last_u = _sp("MSE_BLOCK_LAST")
    kl_block_last_u = _sp("KL_BLOCK_LAST")

    mse_trend = v3e._trend_diagnostic(per_arm_diag["MSE"]["dense_traj"], "dense_full", min_step_for_best)
    kl_trend = v3e._trend_diagnostic(per_arm_diag["KL"]["dense_traj"], "dense_full", min_step_for_best)

    kl_ret = float(kl_block_last_u["ret_agree10"]) if kl_block_last_u else float("nan")
    mse_ret = float(mse_block_last_u["ret_agree10"]) if mse_block_last_u else float("nan")

    recovery = {
        "mse_final_dense": float(_sp("MSE_DENSE_LAST")["spearman_all"]) if _sp("MSE_DENSE_LAST") else float("nan"),
        "mse_final_block": float(mse_block_last_u["spearman_all"]) if mse_block_last_u else float("nan"),
        "mse_bestval_block_on_test": float(_sp("MSE_BLOCK_BESTVAL")["spearman_all"]) if _sp("MSE_BLOCK_BESTVAL") else float("nan"),
        "mse_final_ret_agree10": mse_ret,
        "mse_final_hi80_cos": float(mse_block_last_u["hi80_cos"]) if mse_block_last_u else float("nan"),
        "mse_final_hi80_calib_err": float(mse_block_last_u["hi80_calib_err"]) if mse_block_last_u else float("nan"),
        "mse_trend": mse_trend,
        "kl_final_dense": float(_sp("KL_DENSE_LAST")["spearman_all"]) if _sp("KL_DENSE_LAST") else float("nan"),
        "kl_final_block": float(kl_block_last_u["spearman_all"]) if kl_block_last_u else float("nan"),
        "kl_bestval_block_on_test": float(_sp("KL_BLOCK_BESTVAL")["spearman_all"]) if _sp("KL_BLOCK_BESTVAL") else float("nan"),
        "kl_final_ret_agree10": kl_ret,
        "kl_final_hi80_cos": float(kl_block_last_u["hi80_cos"]) if kl_block_last_u else float("nan"),
        "kl_final_hi80_calib_err": float(kl_block_last_u["hi80_calib_err"]) if kl_block_last_u else float("nan"),
        "kl_trend": kl_trend,
        "delta_ret_agree10": (kl_ret - mse_ret) if math.isfinite(kl_ret) and math.isfinite(mse_ret) else float("nan"),
        "tau_kl": TAU_KL,
        "charpos_ret_agree10": float(_sp("CHARPOS")["ret_agree10"]) if _sp("CHARPOS") else float("nan"),
        "random_block_ret_agree10": float(_sp("RANDOM_BLOCK")["ret_agree10"]) if _sp("RANDOM_BLOCK") else float("nan"),
    }
    verdict, verdict_msg = _verdict_swap(per_unit, recovery, expected_units, run_mode)
    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "run_tag": run_tag, "seed": int(seed), "device": device, "N": n_dim,
        "student_arch": v3.STUDENT_ARCH_PRIMARY, "mlp_hidden": v3.MLP_HIDDEN,
        "warmup_steps": warmup, "steps": steps, "batch": batch,
        "nce_weight": NCE_WEIGHT, "tau_kl": TAU_KL, "loss_families": list(LOSS_FAMILIES),
        "min_step_for_best": min_step_for_best, "dense_eval_every": dense_every,
        "teacher_cache": cache_path.name, "teacher_cache_bytes": cache_bytes,
        "teacher_n_concepts": V_cache, "n_train": n_tr, "n_val": n_val,
        "n_test": n_test, "n_held_pool": n_he,
        "semi_hard_coverage": semi_cov,
        "recovery": recovery,
        "train_diag": {"MSE": per_arm_diag["MSE"], "KL": per_arm_diag["KL"]},
        "per_unit": per_unit, "unit_failures": unit_fail,
        "n_units": len(per_unit), "expected_n_units": expected_units,
        "cardinality_ok": len(per_unit) == expected_units,
        "arms_differ_verified": True, "arm_code_sha256": digests,
        "final_metrics_atomicity": "tmp_replace",
        "composition_algebra": "SBC_block_local_circular_convolution",
        "methodology": ("PAIRED objective-family swap: MSE-RKD (control, "
                        "reproduces v3e's decline/~0.21 retrieval) vs KL-RANK "
                        "(temperature-scaled in-batch softmax-KL distillation, "
                        "CompRess/PKT-style), IDENTICAL seed/mining/split/batch-"
                        "sequence/student-init/steps/eval-cadence -- only the "
                        "RKD loss formula differs; FINAL-step is the PRIMARY "
                        "gated number, best-by-VAL-on-TEST is SECONDARY context; "
                        "ret_agree10 + hi80_cos are top-level headline fields; "
                        "trend-slope (reused from v3e) decides plateau-vs-decline "
                        "for the KL_RANK arm"),
        "progress_logging": "print_flush_true",
        "primary_spearman": recovery["kl_final_block"],
        "dense_sign_spearman": recovery["kl_final_dense"],
        "baseline_in_band": bool(0.05 < recovery["charpos_ret_agree10"] < 0.95),
        "crlb_floor_computed": 0.901,
        "crlb_formula_reference": ("r_max = sigma_teacher / sqrt(sigma_teacher^2 + "
                                   "0.25/K), K=128 -> 0.901 (unchanged from v2/v3/v3b/v3c/v3e; "
                                   "the loss FAMILY does not change the K=128/N=4096 "
                                   "quantization channel)"),
        "discriminator_reachability": True,
        "cell_chunked": True, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "calibration_check": "default_ok_for_this_regime",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[objswap_kl] verdict={verdict} msg={verdict_msg} elapsed={elapsed:.1f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Self-test (synthetic; no cache dependency; fast).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()

    # 1. KL loss numerical safety: finite, non-negative (up to float eps), and
    #    genuinely DIFFERENT from the mse_rkd formula on the same inputs (not
    #    an accidental alias).
    torch.manual_seed(5)
    batch_t, out_dim_t = 16, 64
    x_syn = torch.randn(batch_t, 32)
    x_syn = x_syn / x_syn.norm(dim=-1, keepdim=True)
    s_syn = torch.randn(batch_t, out_dim_t, requires_grad=True)
    s_n_syn = s_syn / s_syn.norm(dim=-1, keepdim=True)
    l_mse = _rkd_loss(x_syn, s_n_syn, batch_t, "cpu", "mse_rkd", TAU_KL)
    l_kl = _rkd_loss(x_syn, s_n_syn, batch_t, "cpu", "kl_rank", TAU_KL)
    assert torch.isfinite(l_mse) and torch.isfinite(l_kl), "selftest: both losses must be finite"
    assert float(l_kl.detach()) >= -1e-4, f"selftest: KL loss must be ~non-negative, got {float(l_kl.detach())}"
    assert abs(float(l_mse.detach()) - float(l_kl.detach())) > 1e-6, (
        "selftest: mse_rkd and kl_rank must compute DIFFERENT values on the same "
        "inputs (else the objective-family swap has no effect)")
    l_kl.backward()
    assert s_syn.grad is not None and torch.isfinite(s_syn.grad).all(), (
        "selftest: KL loss must produce a finite gradient")
    try:
        _rkd_loss(x_syn, s_n_syn, batch_t, "cpu", "bogus_family", TAU_KL)
        raise AssertionError("selftest: unknown loss_family must raise")
    except ValueError:
        pass

    # 2. Regression-equivalence: my mse_rkd branch inside
    #    _train_student_full_swap must reproduce v3c._train_student_full's
    #    "in_batch" objective closely (same seed/data/steps) -- proves the
    #    copy is faithful before trusting the kl_rank branch sits fairly
    #    alongside it.
    n_dim, kb, blk_l, v_syn = 256, 16, 16, 400
    torch.manual_seed(11)
    Xsyn = torch.randn(v_syn, 64)
    Xsyn = Xsyn / Xsyn.norm(dim=-1, keepdim=True)
    gen = torch.Generator().manual_seed(11)
    pos_syn = torch.randint(0, v_syn, (v_syn,), generator=gen)
    semi_syn = torch.randint(0, v_syn, (v_syn, v3.N_SEMI_CANDS), generator=gen)
    Xval_syn = Xsyn[:40].contiguous()
    Xtest_syn = Xsyn[40:64].contiguous()

    def _dq(student):
        return v3._dense_spearman_quick(student, Xval_syn[:20], 300, 3)

    def _df(student):
        return v3._dense_spearman_quick(student, Xval_syn, 500, 3)

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        st_ref, diag_ref = v3c._train_student_full(
            kb, blk_l, Xsyn, pos_syn, semi_syn, 40, 24, 4, 13, "cpu",
            tdp / "ref_ckpt.pt", tdp / "ref_ckpt_best.pt", 100, tdp, t0,
            None, 0, 0.0, "REF_INBATCH", "in_batch",
            dense_eval_quick_fn=_dq, dense_eval_full_fn=_df, dense_eval_every=4,
            min_step_for_best=2)
        st_swap, diag_swap = _train_student_full_swap(
            kb, blk_l, Xsyn, pos_syn, semi_syn, 40, 24, 4, 13, "cpu",
            tdp / "swap_ckpt.pt", tdp / "swap_ckpt_best.pt", 100, tdp, t0,
            0.0, "SWAP_MSE", "mse_rkd", TAU_KL,
            dense_eval_quick_fn=_dq, dense_eval_full_fn=_df, dense_eval_every=4,
            min_step_for_best=2)
        assert abs(diag_ref["rkd_last"] - diag_swap["rkd_last"]) < 1e-4, (
            f"selftest: mse_rkd branch must reproduce v3c in_batch objective "
            f"(ref={diag_ref['rkd_last']:.6f} swap={diag_swap['rkd_last']:.6f})")
        assert abs(diag_ref["loss_last"] - diag_swap["loss_last"]) < 1e-4, (
            "selftest: total loss must also match between ref and swap-mse_rkd")
        ref_sd = st_ref.state_dict()
        swap_sd = st_swap.state_dict()
        for k in ref_sd:
            assert torch.allclose(ref_sd[k], swap_sd[k], atol=1e-4), (
                f"selftest: trained weights diverge for param {k} between "
                f"v3c._train_student_full and _train_student_full_swap(mse_rkd)")

        # 3. kl_rank end-to-end tiny run completes; produces a valid trajectory
        #    and a student whose CODE differs from the mse_rkd-trained student
        #    (arms-must-differ, at the mechanism level not just hash-of-output).
        st_kl, diag_kl = _train_student_full_swap(
            kb, blk_l, Xsyn, pos_syn, semi_syn, 40, 24, 4, 13, "cpu",
            tdp / "kl_ckpt.pt", tdp / "kl_ckpt_best.pt", 100, tdp, t0,
            0.0, "SWAP_KL", "kl_rank", TAU_KL,
            dense_eval_quick_fn=_dq, dense_eval_full_fn=_df, dense_eval_every=4,
            min_step_for_best=2)
        assert math.isfinite(diag_kl["rkd_last"])
        assert len(diag_kl["dense_traj"]) >= MIN_TREND_POINTS
        trend_kl = v3e._trend_diagnostic(diag_kl["dense_traj"], "dense_full", min_step=2)
        assert trend_kl["sufficient"] is True
        c_mse = v3._encode_hard_block(st_swap, Xtest_syn, kb, blk_l)
        c_kl = v3._encode_hard_block(st_kl, Xtest_syn, kb, blk_l)
        assert c_mse.shape == c_kl.shape == (24, kb * blk_l)
        assert torch.isfinite(c_mse).all() and torch.isfinite(c_kl).all()
        h_mse = hashlib.sha256(c_mse.to(torch.int8).numpy().tobytes()).hexdigest()
        h_kl = hashlib.sha256(c_kl.to(torch.int8).numpy().tobytes()).hexdigest()
        assert h_mse != h_kl, (
            "selftest META_RULE_AF: mse_rkd-trained and kl_rank-trained codes "
            "must NOT be bit-identical")
        u_mse = v3._semantic_unit("TEST_MSE", c_mse, c_mse, Xtest_syn, Xtest_syn, 0, 500, 3)
        u_kl = v3._semantic_unit("TEST_KL", c_kl, c_kl, Xtest_syn, Xtest_syn, 0, 500, 3)
        assert "ret_agree10" in u_mse and "hi80_cos" in u_mse
        assert "ret_agree10" in u_kl and "hi80_cos" in u_kl

    # 4. Verdict bands.
    fake_units_base = [{"unit": f"u{i}", "arm": "x", "kind": "k"} for i in range(10)]
    fake_units_base += [
        {"unit": "keyed::RANDOM_BLOCK::J5", "arm": "RANDOM_BLOCK", "kind": "keyed",
         "J": 5, "acc_at1": 0.99, "hit_any_member": 0.99},
        {"unit": "keyed::MSE_BLOCK_LAST::J5", "arm": "MSE_BLOCK_LAST", "kind": "keyed",
         "J": 5, "acc_at1": 0.97, "hit_any_member": 0.97},
        {"unit": "shuffled_key::MSE_BLOCK_LAST::J5", "arm": "MSE_BLOCK_LAST",
         "kind": "shuffled_key", "J": 5, "acc_at1": 0.01, "hit_any_member": 0.01},
        {"unit": "keyed::KL_BLOCK_LAST::J5", "arm": "KL_BLOCK_LAST", "kind": "keyed",
         "J": 5, "acc_at1": 0.96, "hit_any_member": 0.96},
        {"unit": "shuffled_key::KL_BLOCK_LAST::J5", "arm": "KL_BLOCK_LAST",
         "kind": "shuffled_key", "J": 5, "acc_at1": 0.02, "hit_any_member": 0.02},
    ]
    assert len(fake_units_base) == 15  # + 2 more (BESTVAL keyed) not needed for verdict logic itself

    rec_pass = {
        "kl_final_ret_agree10": 0.40, "kl_final_hi80_cos": 0.85,
        "kl_trend": {"sufficient": True, "n_points": 100, "early_minus_late": 0.01},
        "mse_final_ret_agree10": 0.21, "mse_final_hi80_cos": 0.83,
        "delta_ret_agree10": 0.40 - 0.21,
    }
    v_pass, m_pass = _verdict_swap(fake_units_base, rec_pass, 15, "full")
    assert v_pass == "HARD_PASS" and "OBJECTIVE_SWAP_RECOVERS" in m_pass, (
        f"selftest: expected HARD_PASS got {v_pass} ({m_pass})")

    rec_fail = dict(rec_pass, kl_final_ret_agree10=0.22,
                    kl_trend={"sufficient": True, "n_points": 100, "early_minus_late": 0.12})
    v_fail, m_fail = _verdict_swap(fake_units_base, rec_fail, 15, "full")
    assert v_fail == "HARD_FAIL" and "OBJECTIVE_SWAP_NO_MATERIAL_LIFT" in m_fail, (
        f"selftest: expected HARD_FAIL got {v_fail} ({m_fail})")

    rec_mid = dict(rec_pass, kl_final_ret_agree10=0.30,
                   kl_trend={"sufficient": True, "n_points": 100, "early_minus_late": 0.05})
    v_mid, m_mid = _verdict_swap(fake_units_base, rec_mid, 15, "full")
    assert v_mid == "MIDDLE_BAND" and "OBJECTIVE_SWAP_PARTIAL" in m_mid, (
        f"selftest: expected MIDDLE_BAND got {v_mid} ({m_mid})")

    v_card, m_card = _verdict_swap(fake_units_base[:5], rec_pass, 15, "full")
    assert v_card == "HARD_FAIL" and "CARDINALITY_BREACH" in m_card

    fake_units_leak = copy.deepcopy(fake_units_base)
    for u in fake_units_leak:
        if u.get("kind") == "shuffled_key" and u.get("arm") == "KL_BLOCK_LAST":
            u["acc_at1"] = 0.5
    v_leak, m_leak = _verdict_swap(fake_units_leak, rec_pass, 15, "full")
    assert v_leak == "HARD_FAIL" and "SHUFFLED_KEY_LEAK_KL" in m_leak

    fake_units_algbreak = copy.deepcopy(fake_units_base)
    for u in fake_units_algbreak:
        if u.get("arm") == "KL_BLOCK_LAST" and u.get("kind") == "keyed":
            u["acc_at1"] = 0.20
    v_alg, m_alg = _verdict_swap(fake_units_algbreak, rec_pass, 15, "full")
    assert v_alg == "HARD_FAIL" and "FALSE_WIN_ALGEBRA_KL" in m_alg

    print(f"[selftest] PASS (KL-loss numerical-safety + non-aliasing + gradient "
          f"check; mse_rkd branch regression-equivalence against v3c._train_"
          f"student_full incl weight-level match; kl_rank end-to-end tiny run "
          f"+ arms-differ hash check; verdict bands HARD_PASS/HARD_FAIL/"
          f"MIDDLE_BAND/cardinality/shuffled-key-leak/algebra) "
          f"elapsed={time.perf_counter() - t0:.2f}s", flush=True)
    return 0
