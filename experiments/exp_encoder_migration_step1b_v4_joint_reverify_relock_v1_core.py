"""Encoder Migration Step 1b v4 -- JOINT REVERIFY + RELOCK: closes the
semantic-vs-keyed-algebra trade-off question the 2026-07-06 2x drill
(notes/research_encoder_nce_margin_tradeoff_2x_drill_2026-07-06.md) framed as
"no arm anywhere in this lineage has demonstrated BOTH goals at once."

EXP_DEV PRE-DISPATCH FINDING (2026-07-07, verified off-disk BEFORE authoring
this cell -- this changes the cell's job vs the drill's literal ask):
direct read of ALL 5 already-landed v3c FULL seeds
(data/exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_{7,13,23,29,31}/
metrics.json) shows the INBATCH-RKD-only arm (nce_weight=0, same MLP student,
same K=128 block-argmax SBC code) ALREADY jointly clears BOTH bars, 5/5 seeds:
  seed7:  INBATCH_BLOCK spearman=0.8969  keyed@J5 acc1=1.0000
  seed13: INBATCH_BLOCK spearman=0.8865  keyed@J5 acc1=1.0000
  seed23: INBATCH_BLOCK spearman=0.8522  keyed@J5 acc1=1.0000
  seed29: INBATCH_BLOCK spearman=0.8968  keyed@J5 acc1=1.0000
  seed31: INBATCH_BLOCK spearman=0.8963  keyed@J5 acc1=1.0000
MEASURED@data/exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_{N}/metrics.json:per_unit
(kind=semantic,arm=INBATCH_BLOCK / kind=keyed,arm=INBATCH_BLOCK,J=5).
This was MASKED from the v3c cell's own verdict (HARD_FAIL) because
_verdict_full_paired short-circuits on GLOBAL_BLOCK's keyed gate FIRST
(0.03-0.32, genuinely failing) before ever reaching the INBATCH_BLOCK keyed
gate (which passes) -- see exp_encoder_migration_step1b_v3c_full_paired_rkd_
only_dense_recovery_v1_core.py:599-607. The 2026-07-06 drill ALSO missed this:
it explicitly flagged INBATCH_BLOCK's keyed acc@1 as "never reached/reported
... Flag as inference, not an on-disk-verified number" and GUESSED (wrongly)
that it was "likely equally or more degraded" than GLOBAL's. The per_unit list
in the SAME landed metrics.json already contained the true (passing) number;
nobody had read past the verdict_msg's short-circuit.

ONE GAP remains before calling this a fully-verified HARD_PASS: the existing
v3c cell computed a shuffled_key NEGATIVE CONTROL only for GLOBAL_BLOCK, never
for INBATCH_BLOCK. Without it, a collapsed/degenerate code that returns the
same top-hit regardless of key could in principle produce a spurious acc@1=1.0
(the exact failure mode the shuffled_key control exists to catch). This cell's
PHASE 1 closes that gap: reload the already-existing, already-landed
_ckpt_best_INBATCH.pt (no retraining) and add the missing shuffled_key control
plus an independent dense/keyed reproduction (Gate D positive-control style).

PHASE 2 is the ORIGINALLY REQUESTED experiment, scoped to the arm that
genuinely still fails: GLOBAL-RKD-only's checkpoint (keyed@J5 0.03-0.32,
5/5 seeds) gets a SHORT terminal NCE-relock fine-tune (reload the existing
_ckpt_best_GLOBAL.pt, reintroduce nce_weight=0.5 -- the SAME weight v2/v3b
used, known to deliver keyed acc@1~1.0 given enough steps -- at a REDUCED LR
for a SHORT schedule, tracking both dense-spearman and keyed-roundtrip acc@1
at fine cadence so a re-collapse is caught, not laundered). This is the
literal recipe from research_encoder_nce_margin_tradeoff_2x_drill_2026-07-06.md
Rank-1 lever, with ONE budget correction: the drill's illustrative "5-10% of
a 40,000-step schedule" assumes v3's ORIGINAL FULL_STEPS=40000 config; the
ACTUAL checkpoint on disk was trained at v3c's matched-to-v3b 1800-step
config (v3.MID_STEPS), so the "25% of original = no longer short" HARD_FAIL
ceiling this cell uses is 450 steps (0.25 * 1800), NOT 2000-4000 steps.
THEORETICAL@drill's own falsifiable-prediction table, rescaled to the true
trained-schedule length (MEASURED@v3c metrics.json:steps=1800).

ZERO RETRAINING COST for the starting point of EITHER phase: both phases load
existing, already-landed, already-preserved checkpoints (v3c's docstring:
"Checkpoints are saved every CKPT_EVERY_STEPS_FULL (300) steps and PRESERVED
(not deleted post-run)"). VERIFIED@this cell's authoring session (2026-07-07,
ssh marsh@home Test-Path): _ckpt_best_{GLOBAL,INBATCH}.pt present for all 5
seeds at data/substrate_concept_encoder_v1b_v3c_full_paired_seed{N}/, sizes
~41.9MB, mtimes 2026-07-04 14:27-14:59 (matches the original v3c FULL run).

RESOURCE-RULE COMPLIANCE (USER, this cycle): FULL dispatch is REMOTE ONLY
(overnight_queue, GPU) -- both phases are cheap (Phase 1 is pure eval, no
training; Phase 2 trains at most RELOCK_STEPS_FULL=450 steps, versus the
ORIGINAL v3c cell's FULL 1800-step x 2-arm run which measured 182.1s wall on
GPU -- this cell's total budget is a small fraction of that, not a GPU-day).
Local smoke is a SELF-CONTAINED synthetic bootstrap (v3c's own tiny-synthetic-
data recipe, no external file dependency, no real-corpus/GPU-day cost) --
machinery-only per DISCRIMINATOR-MUST-SURVIVE-SCALE option (B), same
analytical-justification precedent already used twice in this lineage (v3 mid
prereg, v3b prereg): smoke's synthetic V cannot reproduce the real semantic/
algebra discriminator, it only proves checkpoint-load + relock-train + eval +
verdict machinery executes end-to-end.

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01):
  query "NCE curriculum sequenced contrastive loss margin decodability keyed
  algebra semantic tradeoff encoder" -> top hit cosine=0.249 ('ability to
  change sequence', WordNet), all other hits <=0.2412. NONE at cosine>0.30 --
  no prior SUBSTRATE-KB atom at this threshold (expected: this is a WordNet/
  note-prose lexical index, not a code-history index). The REAL prior-work
  check for this cell is the on-disk encoder-lineage re-derivation documented
  above (v3c 5-seed FULL + the GSBC lineage noted below), not the KB query.

ADJACENT-LINEAGE FLAG (surfaced to Director in this cell's dispatch report,
not litigated further here): a SEPARATE, LATER lineage
(exp_encoder_v11_gsbc_graded_sparse_v1, exp_encoder_v12_gsbc_gwta_expansion_v1,
exp_encoder_gsbc_gradedcode_retrieval_v1; all dated 2026-07-05, i.e. BEFORE
the 2026-07-06 drill) uses a DIFFERENT code family (graded Sparse-Block-Code +
circular-conv binding, FlyHash-style expansion) and ALSO lands HARD_PASS
verdicts jointly clearing retrieval (ret_agree10 0.31-0.68) and algebra
(keyed@J5=1.000, composed_roundtrip>=0.95) at the SAME full 177899-concept
scale (n_train=160109, same teacher cache). That lineage's own verdict_msg
flags "Next: density dial + full-M=177899 composition VET" as still open --
i.e. GSBC's win is at full TRAINING scale but not yet full COMPOSITION-VET
scale. This cell does NOT re-litigate GSBC; it only closes the SBC-block-code
question the drill and this dispatch's contract specifically asked about.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified: sha256 over all 4 code arms (INBATCH_BLOCK_REVERIFY,
  GLOBAL_BLOCK_START, GLOBAL_BLOCK_RELOCKED, RANDOM_BLOCK) at smoke+full gate
- final_metrics_atomicity: tmp_replace (write_metrics + relock ckpt os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException/bare except)
- crlb_floor_computed: r_max=0.901 at K=128 (unchanged code family; THEORETICAL,
  CITED@v2/v3/v3b/v3c prereg lineage)
- baseline_in_band (this cell's variant): GLOBAL_BLOCK_START keyed@J5 acc1 MUST
  be < 0.5 (the relock experiment is vacuous if the "before" state already
  passes -- MEASURED@v3c per-seed data shows 0.03-0.32, comfortably below)
- discriminator-survives-scale: option (B) analytical, same precedent as v3/v3b/v3c
- HP_SCOPE: {REVERIFY: [INBATCH_BLOCK dense>=0.82, keyed>=0.90, shuffled<=0.10]},
  {RELOCK: [GLOBAL_BLOCK dense-at-crossing>=0.70, keyed-at-crossing>=0.90,
  post-crossing stability, shuffled-at-final<=0.10]}
- cardinality_ok: EXPECTED_N_UNITS=9 (see per_unit list below), counted from per_unit
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime (identical hyperparameters
  inherited from the validated v3/v3b/v3c lineage; only the relock phase's
  nce_weight/lr/step-budget are new, pre-registered, principled changes)
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ / VERIFIED@

Prereg: preregs/2026-07-07_exp_encoder_migration_step1b_v4_joint_reverify_relock_v1.md
Parent cells:
  experiments/exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py
  experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py

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
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import torch

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
from experiments import (  # noqa: E402
    exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core
    as v3c,
)

v3 = v3c.v3  # the lower-level shared helper module v3c itself imports

# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_migration_step1b_v4_joint_reverify_relock_v1"
SEED_DEFAULT = v3.SEED_DEFAULT  # 7

# ---- Relock hyperparameters (Phase 2, GLOBAL arm only) ----
RELOCK_NCE_WEIGHT = 0.5   # MEASURED@v2/v3b: the constant weight known to
                          # deliver keyed acc@1~1.0 given enough steps.
RELOCK_LR_FULL = 2.0e-4  # HYPOTHESIZED@QAT lit (Krishnamoorthi arXiv:1806.08342):
                          # reduced LR (0.2x v3.LR=1e-3) for a short post-hoc
                          # fine-tune, avoids "catastrophic disruption."
RELOCK_STEPS_FULL = 450  # THEORETICAL: 0.25 * v3c's ACTUAL trained schedule
                          # (v3.MID_STEPS=1800), matching the drill's own
                          # "25% of original = no longer short" HARD_FAIL
                          # ceiling, rescaled from the drill's illustrative
                          # 40000-step assumption to the true 1800-step one.
RELOCK_EVAL_EVERY_FULL = 25  # 18 eval points over 450 steps.
RELOCK_WARMUP_FRAC = 0.10    # 45-step linear warmup (fresh optimizer state).
RELOCK_CKPT_EVERY_FULL = 100

# ---- Smoke (self-contained synthetic bootstrap; machinery-only) ----
SMOKE_N_DIM, SMOKE_KB, SMOKE_BLK_L, SMOKE_V_SYN = 256, 16, 16, 400
SMOKE_BOOTSTRAP_STEPS = 20
SMOKE_RELOCK_STEPS = 24
SMOKE_RELOCK_EVAL_EVERY = 6
SMOKE_RELOCK_WARMUP_FRAC = 0.20
SMOKE_RELOCK_LR = 5.0e-3
SMOKE_TRIALS = 30

# semantic(3: INBATCH_REVERIFY, GLOBAL_START, GLOBAL_RELOCKED)
# + keyed-real(4: INBATCH_REVERIFY, GLOBAL_START, GLOBAL_RELOCKED, RANDOM_BLOCK
#   calibration) + shuffled(2: INBATCH_REVERIFY, GLOBAL_RELOCKED) = 9.
# CAUGHT BY SMOKE (2026-07-07): an earlier draft declared 10 here (an
# arithmetic slip in the tally, not a missing unit) -- smoke's cardinality
# gate correctly HARD_FAILed 9/10 before any FULL dispatch. Fixed to the true
# count; self-test's own fake-unit fixtures already used 9 correctly the
# whole time (this constant was the only thing wrong).
EXPECTED_N_UNITS = 9

# Bands (PRIMARY gates).
REVERIFY_DENSE_FLOOR = 0.82     # HYPOTHESIZED@this dispatch's own contract
REVERIFY_KEYED_FLOOR = 0.90
REVERIFY_SHUFFLED_LEAK_CEILING = 0.10
RELOCK_HP_DENSE_FLOOR = 0.70     # HYPOTHESIZED@drill falsifiable-prediction table
RELOCK_HP_KEYED_FLOOR = 0.90
RELOCK_STABILITY_DROP_MARGIN = 0.05  # post-crossing keyed relapse tolerance
RELOCK_MB_KEYED_FLOOR = 0.70
RELOCK_MB_DENSE_FLOOR = 0.65
RELOCK_HF_DENSE_AT_CROSSING_FLOOR = 0.60


def _artifact_dir(run_mode: str, run_tag: str = "") -> Path:
    suffix = {"smoke": "_smoke"}.get(run_mode, "")
    tag = f"_{run_tag}" if run_tag else ""
    return _REPO / "data" / f"substrate_concept_encoder_v1b_v4_reverify_relock{tag}{suffix}"


# ---------------------------------------------------------------------------
# Defensive helpers (start marker / crash metrics / heartbeat) -- mirrors v3c.
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
# Relock training loop (Phase 2): loads an EXTERNAL init_state_dict (the
# already-landed v3c best-checkpoint), fine-tunes with nce_weight REINTRODUCED
# at a reduced LR for a short, monitored schedule. Adapted from v3c's
# _train_student_full inner loop but parameterized on LR (v3c hardcodes
# v3.LR) and warm-started from an external state dict (v3c always inits fresh
# or resumes its OWN {student,opt,gen_state,step} format, which the read-only
# source best-checkpoint does not have -- so this is a distinct function, not
# a monkeypatch of v3c's).
# ---------------------------------------------------------------------------

def _relock_lr_at(step: int, warmup: int, lr: float) -> float:
    if warmup <= 0:
        return lr
    return lr * min(1.0, (step + 1) / warmup)


def _run_relock(
    kb: int, blk_l: int, Xtr: torch.Tensor, pos_idx: torch.Tensor,
    semi_cands: torch.Tensor, init_state_dict: Dict, relock_steps: int,
    batch: int, warmup: int, seed: int, lr: float, nce_weight: float,
    device: str, land_idx: Optional[torch.Tensor], refresh_every: int,
    arm_label: str, objective: str, dense_eval_fn: Callable,
    keyed_eval_fn: Callable, eval_every: int, out_dir: Path, t0: float,
    relock_ckpt_path: Path, ckpt_every: int,
) -> Tuple[torch.nn.Module, List[Dict]]:
    """Returns (relocked_student, trajectory). trajectory[i] = {step,
    dense_full, keyed_acc1}. Includes step-0 (pre-relock) eval point."""
    if objective not in ("global", "in_batch"):
        raise ValueError(f"unknown objective {objective}")
    in_dim = Xtr.shape[1]
    out_dim = kb * blk_l
    student = v3._make_student("mlp", in_dim, out_dim, device, seed=0)
    opt = torch.optim.Adam(student.parameters(), lr=lr)
    gen = torch.Generator().manual_seed(seed + 5001)
    start_step = 0
    traj: List[Dict] = []
    if relock_ckpt_path.exists():
        try:
            ck = torch.load(str(relock_ckpt_path), map_location=device)
            student.load_state_dict(ck["student"])
            opt.load_state_dict(ck["opt"])
            gen.set_state(ck["gen_state"])
            start_step = int(ck["step"])
            traj = list(ck.get("traj", []))
            print(f"[v4_relock] resume {arm_label} at step {start_step}", flush=True)
        except (RuntimeError, KeyError, EOFError) as exc:
            print(f"[v4_relock] WARN relock-ckpt load failed "
                  f"({type(exc).__name__}); starting {arm_label} relock fresh "
                  f"from the ORIGINAL init_state_dict", flush=True)
            student.load_state_dict(init_state_dict)
            start_step = 0
            traj = []
    else:
        student.load_state_dict(init_state_dict)
    V = Xtr.shape[0]
    Xd = Xtr.to(device)
    Xland_d = None
    if objective == "global":
        if land_idx is None or land_idx.numel() == 0:
            raise ValueError(f"{arm_label}: global objective requires non-empty land_idx")
        Xland_d = Xd[land_idx.to(device)]
    frame_n = None

    if start_step == 0:
        d0 = float(dense_eval_fn(student))
        k0 = float(keyed_eval_fn(student))
        traj.append({"step": 0, "dense_full": d0, "keyed_acc1": k0})
        print(f"[v4_relock] {arm_label} PRE-RELOCK (step 0): dense={d0:.4f} "
              f"keyed_acc1={k0:.4f}", flush=True)

    for step in range(start_step, relock_steps):
        cur_lr = _relock_lr_at(step, warmup, lr)
        for g in opt.param_groups:
            g["lr"] = cur_lr
        bidx = v3._cluster_batch_idx(batch, 0.0, V, pos_idx, semi_cands, gen)
        x = Xd[bidx.to(device)]
        z = student(x)
        s = v3._block_ste(z, kb, blk_l)
        s_n = s / (s.norm(dim=-1, keepdim=True) + 1e-8)
        if objective == "global":
            if frame_n is None or (step % refresh_every == 0):
                frame_n = v3._frame_codes_norm(student, Xland_d, "block", kb, blk_l, kb)
            Tland = x @ Xland_d.T
            l_rkd = ((s_n @ frame_n.T - Tland) ** 2).mean()
        else:
            T = x @ x.T
            off = ~torch.eye(batch, dtype=torch.bool, device=device)
            l_rkd = (((s_n @ s_n.T) - T)[off] ** 2).mean()
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
                f"failure_class=NAN_LOSS: relock {arm_label} loss non-finite "
                f"at step {step} (l_rkd={float(l_rkd.detach())}, "
                f"l_nce={float(l_nce.detach())}, nce_w={nce_weight})")
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 50 == 0:
            print(f"[v4_relock] {arm_label} step {step}/{relock_steps} "
                  f"rkd={float(l_rkd.detach()):.4f} nce={float(l_nce.detach()):.4f} "
                  f"lr={cur_lr:.2e} ({time.perf_counter() - t0:.1f}s)", flush=True)
            _emit_heartbeat(out_dir, step, relock_steps, time.perf_counter() - t0,
                            extra={"phase": f"relock_{arm_label}",
                                   "loss": float(loss.detach())})
        if (step + 1) % eval_every == 0 or (step + 1) == relock_steps:
            d = float(dense_eval_fn(student))
            k = float(keyed_eval_fn(student))
            traj.append({"step": step + 1, "dense_full": d, "keyed_acc1": k})
            print(f"[v4_relock] {arm_label} RELOCK-traj step {step + 1}: "
                  f"dense={d:.4f} keyed_acc1={k:.4f}", flush=True)
        if (step + 1) % ckpt_every == 0 or (step + 1) == relock_steps:
            tmp = relock_ckpt_path.with_suffix(".tmp")
            torch.save({"student": student.state_dict(), "opt": opt.state_dict(),
                       "gen_state": gen.get_state(), "step": step + 1,
                       "traj": traj}, str(tmp))
            os.replace(str(tmp), str(relock_ckpt_path))
    return student, traj


def _analyze_relock_traj(traj: List[Dict]) -> Dict:
    """Find the first crossing step where keyed_acc1 >= RELOCK_HP_KEYED_FLOOR,
    and check post-crossing stability (no relapse > RELOCK_STABILITY_DROP_MARGIN
    from the crossing value through the end of the observed trajectory)."""
    crossing_step = None
    crossing_dense = None
    crossing_keyed = None
    for row in traj:
        if row["keyed_acc1"] >= RELOCK_HP_KEYED_FLOOR:
            crossing_step = row["step"]
            crossing_dense = row["dense_full"]
            crossing_keyed = row["keyed_acc1"]
            break
    stable = True
    if crossing_step is not None:
        for row in traj:
            if row["step"] > crossing_step:
                if row["keyed_acc1"] < (crossing_keyed - RELOCK_STABILITY_DROP_MARGIN):
                    stable = False
                    break
    max_keyed = max((r["keyed_acc1"] for r in traj), default=float("nan"))
    final_dense = traj[-1]["dense_full"] if traj else float("nan")
    final_keyed = traj[-1]["keyed_acc1"] if traj else float("nan")
    return {
        "crossing_step": crossing_step, "crossing_dense": crossing_dense,
        "crossing_keyed": crossing_keyed, "post_crossing_stable": stable,
        "max_keyed_acc1": max_keyed, "final_dense": final_dense,
        "final_keyed_acc1": final_keyed, "traj_len": len(traj),
    }


# ---------------------------------------------------------------------------
# Verdict logic.
# ---------------------------------------------------------------------------

def _verdict_v4(per_unit: List[Dict], relock_analysis: Dict, expected_units: int,
               run_mode: str) -> Tuple[str, str]:
    if len(per_unit) < expected_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"{len(per_unit)}/{expected_units} units")

    def _u(kind, arm, J=None):
        return v3._by_unit(per_unit, kind, arm, J)

    rblock_keyed = _u("keyed", "RANDOM_BLOCK", 5)
    if rblock_keyed is None:
        return ("HARD_FAIL", "HARD_FAIL_MISSING_GATE_UNITS")
    if rblock_keyed["acc_at1"] < 0.90:
        return ("HARD_FAIL",
                f"HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH: RANDOM_BLOCK keyed "
                f"J=5 {rblock_keyed['acc_at1']:.3f} < 0.90 (SBC lossless prior)")

    inb_sem = _u("semantic", "INBATCH_BLOCK_REVERIFY")
    inb_keyed = _u("keyed", "INBATCH_BLOCK_REVERIFY", 5)
    inb_shuf = _u("shuffled_key", "INBATCH_BLOCK_REVERIFY", 5)
    gl_start_sem = _u("semantic", "GLOBAL_BLOCK_START")
    gl_start_keyed = _u("keyed", "GLOBAL_BLOCK_START", 5)
    gl_relock_sem = _u("semantic", "GLOBAL_BLOCK_RELOCKED")
    gl_relock_keyed = _u("keyed", "GLOBAL_BLOCK_RELOCKED", 5)
    gl_relock_shuf = _u("shuffled_key", "GLOBAL_BLOCK_RELOCKED", 5)
    if None in (inb_sem, inb_keyed, inb_shuf, gl_start_sem, gl_start_keyed,
                gl_relock_sem, gl_relock_keyed, gl_relock_shuf):
        return ("HARD_FAIL", "HARD_FAIL_MISSING_GATE_UNITS")

    # Integrity gate: shuffled-key leak overrides everything (a code that
    # "decodes" regardless of key is not doing real algebra).
    if inb_shuf["acc_at1"] > REVERIFY_SHUFFLED_LEAK_CEILING:
        return ("HARD_FAIL",
                f"HARD_FAIL_SHUFFLED_KEY_LEAK_INBATCH: "
                f"{inb_shuf['acc_at1']:.3f} > {REVERIFY_SHUFFLED_LEAK_CEILING}")

    reverify_pass = (inb_sem["spearman_all"] >= REVERIFY_DENSE_FLOOR
                     and inb_keyed["acc_at1"] >= REVERIFY_KEYED_FLOOR
                     and inb_shuf["acc_at1"] <= REVERIFY_SHUFFLED_LEAK_CEILING)
    reverify_tail = (f"[REVERIFY INBATCH_BLOCK: dense={inb_sem['spearman_all']:.4f} "
                     f"keyed@J5={inb_keyed['acc_at1']:.4f} "
                     f"shuffled@J5={inb_shuf['acc_at1']:.4f}]")

    if run_mode == "smoke":
        fails = []
        if relock_analysis["traj_len"] < 2:
            fails.append("S_relock_traj_too_short")
        if not math.isfinite(inb_sem["spearman_all"]):
            fails.append("S_dense_nan")
        if fails:
            return ("SMOKE_GATE_FAIL", "; ".join(fails))
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: checkpoint-load + reverify-eval + relock-"
                f"train + keyed/shuffled eval all executed end-to-end on "
                f"synthetic data; verdict logic reachable. Real semantic/"
                f"algebra discriminator is a FULL-only question (synthetic V "
                f"cannot reproduce it, same precedent as v3/v3b/v3c). "
                f"{reverify_tail}")

    # baseline_in_band variant for this cell: the GLOBAL "before relock" state
    # MUST be a genuine failure (< 0.5), else the relock experiment is vacuous.
    if gl_start_keyed["acc_at1"] >= 0.5:
        return ("HARD_FAIL",
                f"HARD_FAIL_VACUOUS_RELOCK_TARGET: GLOBAL_BLOCK_START keyed@J5 "
                f"{gl_start_keyed['acc_at1']:.3f} >= 0.5 -- the pre-relock "
                f"checkpoint is not genuinely failing keyed algebra; relocking "
                f"it proves nothing. Re-verify the loaded checkpoint is the "
                f"correct one.")

    if gl_relock_shuf["acc_at1"] > REVERIFY_SHUFFLED_LEAK_CEILING:
        return ("HARD_FAIL",
                f"HARD_FAIL_SHUFFLED_KEY_LEAK_RELOCKED_GLOBAL: "
                f"{gl_relock_shuf['acc_at1']:.3f} > "
                f"{REVERIFY_SHUFFLED_LEAK_CEILING}")

    relock_pass = (
        relock_analysis["crossing_step"] is not None
        and relock_analysis["crossing_dense"] >= RELOCK_HP_DENSE_FLOOR
        and relock_analysis["post_crossing_stable"]
        and gl_relock_shuf["acc_at1"] <= REVERIFY_SHUFFLED_LEAK_CEILING)
    relock_tail = (
        f"[RELOCK GLOBAL_BLOCK: crossing_step={relock_analysis['crossing_step']} "
        f"crossing_dense={relock_analysis['crossing_dense']} "
        f"crossing_keyed={relock_analysis['crossing_keyed']} "
        f"stable={relock_analysis['post_crossing_stable']} "
        f"final_dense={relock_analysis['final_dense']:.4f} "
        f"final_keyed={relock_analysis['final_keyed_acc1']:.4f} "
        f"shuffled_final={gl_relock_shuf['acc_at1']:.4f}]")

    if reverify_pass:
        return ("HARD_PASS",
                f"ALREADY_JOINT_SOLVED_VIA_INBATCH: the INBATCH-RKD-only "
                f"(nce_weight=0) arm's ALREADY-LANDED best-checkpoint jointly "
                f"clears dense>={REVERIFY_DENSE_FLOOR}, keyed>="
                f"{REVERIFY_KEYED_FLOOR}, and the previously-missing "
                f"shuffled-key control confirms no leak "
                f"(<={REVERIFY_SHUFFLED_LEAK_CEILING}) -- the semantic-vs-"
                f"algebra trade-off this dispatch targets is ALREADY RESOLVED "
                f"by data landed 2026-07-04, masked only by the v3c cell's "
                f"own verdict short-circuit on GLOBAL_BLOCK. No new training "
                f"was required to reach this verdict (Phase 1 = pure eval on "
                f"an existing checkpoint). {reverify_tail} RELOCK secondary "
                f"finding on the separately-failing GLOBAL arm: "
                f"{'RECOVERED' if relock_pass else 'NOT recovered'} "
                f"{relock_tail}")

    if relock_pass:
        return ("HARD_PASS",
                f"RELOCK_RECOVERS_GLOBAL_JOINT: the short terminal NCE-relock "
                f"curriculum recovers keyed algebra on the previously-failing "
                f"GLOBAL arm while dense-spearman stays materially above the "
                f"v2 baseline and the recovery is stable post-crossing. "
                f"{relock_tail} (REVERIFY INBATCH result: "
                f"{'also passes' if reverify_pass else 'did NOT pass'} "
                f"{reverify_tail})")

    # Neither arm cleared the joint bar cleanly -- MIDDLE_BAND or HARD_FAIL
    # per the drill's own bands, applied to whichever arm got closer.
    relock_mb = (relock_analysis["crossing_step"] is not None
                and relock_analysis["max_keyed_acc1"] >= RELOCK_MB_KEYED_FLOOR
                and relock_analysis["final_dense"] >= RELOCK_MB_DENSE_FLOOR)
    reverify_mb = (inb_sem["spearman_all"] >= 0.70
                  and inb_keyed["acc_at1"] >= 0.70)
    if relock_mb or reverify_mb:
        return ("MIDDLE_BAND",
                f"PARTIAL_JOINT_RECOVERY: neither arm cleanly clears the full "
                f"joint bar but real partial signal exists. {reverify_tail} "
                f"{relock_tail}")

    return ("HARD_FAIL",
            f"JOINT_REQUIREMENT_NOT_MET_EITHER_ARM: REVERIFY did not confirm "
            f"an already-passing INBATCH arm AND the RELOCK curriculum did "
            f"not recover GLOBAL's algebra within the short budget "
            f"({RELOCK_STEPS_FULL} steps = 25pct of the true 1800-step "
            f"original schedule) -- per the drill's own HARD-FAIL band, this "
            f"means the recipe needs longer than 'short and monitored' to "
            f"work, reproducing the corruption dynamic it was designed to "
            f"avoid. {reverify_tail} {relock_tail}")


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def run_v4(run_mode: str, seed: int, device_arg: str, n_dim: int,
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

    _write_start_marker(out_dir, run_mode, EXPECTED_N_UNITS)
    t0 = time.perf_counter()
    print(f"[v4] run_mode={run_mode} seed={seed} device={device} "
          f"n_dim={n_dim} tag={run_tag!r}", flush=True)

    per_unit: List[Dict] = []
    unit_fail: List[Dict] = []
    expected_units = EXPECTED_N_UNITS

    def _run_unit(fn, *a, **kw):
        try:
            u = fn(*a, **kw)
            per_unit.append(u)
            print(f"[v4] unit {len(per_unit)}/{expected_units} {u['unit']}: "
                  + json.dumps({k: round(v, 4) for k, v in u.items()
                                if isinstance(v, float)}), flush=True)
            _emit_heartbeat(out_dir, len(per_unit), expected_units,
                            time.perf_counter() - t0, extra={"unit": u["unit"]})
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append({"fn": getattr(fn, "__name__", "?"),
                              "failure_class": type(exc).__name__,
                              "msg": str(exc)[:300]})
            raise

    if run_mode == "smoke":
        kb, blk_l = SMOKE_KB, SMOKE_BLK_L
        torch.manual_seed(seed + 900)
        Xall = torch.randn(SMOKE_V_SYN, 64)
        Xall = Xall / Xall.norm(dim=-1, keepdim=True)
        gen_data = torch.Generator().manual_seed(seed + 901)
        pos_idx = torch.randint(0, SMOKE_V_SYN, (SMOKE_V_SYN,), generator=gen_data)
        semi_cands = torch.randint(0, SMOKE_V_SYN, (SMOKE_V_SYN, v3.N_SEMI_CANDS),
                                   generator=gen_data)
        land_idx = torch.randperm(SMOKE_V_SYN, generator=gen_data)[:96]
        Xtr = Xall
        Xhe = Xall[:80]
        n_trials = SMOKE_TRIALS
        relock_steps, eval_every, warmup_frac, relock_lr = (
            SMOKE_RELOCK_STEPS, SMOKE_RELOCK_EVAL_EVERY,
            SMOKE_RELOCK_WARMUP_FRAC, SMOKE_RELOCK_LR)
        final_pairs = 3000

        def _dq(student):
            return v3._dense_spearman_quick(student, Xhe, 800, seed + 7)

        # Self-contained bootstrap: train tiny GLOBAL + INBATCH "existing"
        # checkpoints at nce=0 (mirrors v3c's own synthetic self-test recipe)
        # so this smoke never depends on any OTHER cell's artifact file.
        _, diag_g = v3c._train_student_full(
            kb, blk_l, Xtr, pos_idx, semi_cands, SMOKE_BOOTSTRAP_STEPS, 32, 4,
            seed + 11, "cpu", art_dir / "_boot_ckpt_g.pt",
            art_dir / "_boot_ckpt_best_g.pt", 100, out_dir, t0, land_idx, 4,
            0.0, "BOOT_GLOBAL", objective="global", dense_eval_quick_fn=_dq,
            dense_eval_full_fn=_dq, dense_eval_every=5, min_step_for_best=0)
        _, diag_i = v3c._train_student_full(
            kb, blk_l, Xtr, pos_idx, semi_cands, SMOKE_BOOTSTRAP_STEPS, 32, 4,
            seed + 11, "cpu", art_dir / "_boot_ckpt_i.pt",
            art_dir / "_boot_ckpt_best_i.pt", 100, out_dir, t0, None, 4,
            0.0, "BOOT_INBATCH", objective="in_batch", dense_eval_quick_fn=_dq,
            dense_eval_full_fn=_dq, dense_eval_every=5, min_step_for_best=0)
        ck_global = torch.load(str(art_dir / "_boot_ckpt_best_g.pt"), map_location="cpu")
        ck_inbatch = torch.load(str(art_dir / "_boot_ckpt_best_i.pt"), map_location="cpu")
        init_global = ck_global["student"]
        init_inbatch = ck_inbatch["student"]
        device = "cpu"
    else:
        kb, blk_l = v3.K_BLOCKS_PRIMARY, n_dim // v3.K_BLOCKS_PRIMARY
        if kb * blk_l != n_dim:
            raise ValueError(f"n_dim {n_dim} not divisible by k_blocks {kb}")
        effective_cache_arg = teacher_cache_arg or v3c.TEACHER_CACHE_DEFAULT
        cache_path = v3._resolve_teacher_cache(effective_cache_arg)
        cache_bytes = cache_path.stat().st_size
        X, ids = v3._load_teacher(cache_path)
        V_cache = X.shape[0]
        print(f"[v4] teacher {cache_path.name}: {V_cache} concepts x "
              f"{X.shape[1]}d ({time.perf_counter() - t0:.1f}s)", flush=True)
        rng = np.random.default_rng(seed)
        perm = rng.permutation(V_cache)
        n_he = min(int(round(V_cache * v3.HELD_FRAC)), v3.FULL_HELD_CAP)
        n_tr = V_cache - n_he
        tr_idx = perm[:n_tr]
        he_idx = perm[n_tr:n_tr + n_he]
        Xtr = X[torch.from_numpy(tr_idx.copy())].contiguous()
        Xhe = X[torch.from_numpy(he_idx.copy())].contiguous()
        print(f"[v4] split train={n_tr} held={n_he} (SAME seed/permutation "
              f"convention as v3c -> reproduces its exact held set)", flush=True)

        src_dir = v3c._artifact_dir("full", run_tag)
        ckpt_inbatch_path = src_dir / "_ckpt_best_INBATCH.pt"
        ckpt_global_path = src_dir / "_ckpt_best_GLOBAL.pt"
        if not ckpt_inbatch_path.exists() or not ckpt_global_path.exists():
            raise FileNotFoundError(
                f"expected v3c FULL best-checkpoints missing at {src_dir} "
                f"(inbatch_exists={ckpt_inbatch_path.exists()} "
                f"global_exists={ckpt_global_path.exists()}) -- cannot reuse-"
                f"checkpoint per the zero-retrain-cost premise; refusing to "
                f"silently fall back to training from scratch (that would "
                f"violate the SHORT-budget resource contract).")
        ck_global = torch.load(str(ckpt_global_path), map_location=device)
        ck_inbatch = torch.load(str(ckpt_inbatch_path), map_location=device)
        init_global = ck_global["student"]
        init_inbatch = ck_inbatch["student"]

        pos_idx, semi_cands = v3._mine_teacher(
            Xtr, device, art_dir / "_mine_shards", out_dir, t0)
        n_land_eff = min(v3c.N_LANDMARKS_FULL, n_tr)
        g_land = torch.Generator().manual_seed(seed + 101)
        land_idx = torch.randperm(n_tr, generator=g_land)[:n_land_eff]
        print(f"[v4] mining done landmarks={n_land_eff} "
              f"({time.perf_counter() - t0:.1f}s)", flush=True)

        n_trials = v3c.FULL_TRIALS
        relock_steps = RELOCK_STEPS_FULL
        eval_every = RELOCK_EVAL_EVERY_FULL
        warmup_frac = RELOCK_WARMUP_FRAC
        relock_lr = RELOCK_LR_FULL
        final_pairs = v3c.FULL_FINAL_PAIRS
        quick_sub = min(v3c.FULL_QUICK_HELD_SUB, n_he)
        Xhe_sub = Xhe[:quick_sub].contiguous()

        def _dq(student):
            return v3._dense_spearman_quick(student, Xhe_sub, v3c.FULL_QUICK_PAIRS, seed + 7)

    in_dim = Xtr.shape[1]
    out_dim = kb * blk_l

    def _keyed_eval(student, gen_local):
        codes = v3._encode_hard_block(student, Xhe, kb, blk_l)
        u = v3._keyed_unit("EVAL_TMP", "sbc", codes, kb, blk_l, 5, n_trials,
                          gen_local, device)
        return u["acc_at1"]

    gen_eval = torch.Generator().manual_seed(seed + 2)

    # ---- Phase 1: REVERIFY INBATCH (pure eval, no training) ----
    student_in = v3._make_student("mlp", in_dim, out_dim, device, seed=0)
    student_in.load_state_dict(init_inbatch)
    codes_inbatch = v3._encode_hard_block(student_in, Xhe, kb, blk_l)
    _run_unit(v3._semantic_unit, "INBATCH_BLOCK_REVERIFY", codes_inbatch,
              codes_inbatch, Xhe, Xhe, 0, final_pairs, seed + 3)
    _run_unit(v3._keyed_unit, "INBATCH_BLOCK_REVERIFY", "sbc", codes_inbatch,
              kb, blk_l, 5, n_trials, gen_eval, device)
    _run_unit(v3._keyed_unit, "INBATCH_BLOCK_REVERIFY", "sbc", codes_inbatch,
              kb, blk_l, 5, n_trials, gen_eval, device, shuffled_key=True)

    # ---- Phase 2a: GLOBAL "before relock" reproduction (pure eval) ----
    student_gl = v3._make_student("mlp", in_dim, out_dim, device, seed=0)
    student_gl.load_state_dict(init_global)
    codes_global_start = v3._encode_hard_block(student_gl, Xhe, kb, blk_l)
    _run_unit(v3._semantic_unit, "GLOBAL_BLOCK_START", codes_global_start,
              codes_global_start, Xhe, Xhe, 0, final_pairs, seed + 3)
    _run_unit(v3._keyed_unit, "GLOBAL_BLOCK_START", "sbc", codes_global_start,
              kb, blk_l, 5, n_trials, gen_eval, device)

    # ---- Phase 2b: RELOCK training on GLOBAL arm ----
    warmup_steps = max(1, int(round(warmup_frac * relock_steps)))

    def _keyed_eval_fixed(student):
        gen_local = torch.Generator().manual_seed(seed + 4001)
        return _keyed_eval(student, gen_local)

    student_relocked, relock_traj = _run_relock(
        kb, blk_l, Xtr, pos_idx, semi_cands, init_global, relock_steps,
        min(128, Xtr.shape[0]) if run_mode == "smoke" else 128, warmup_steps,
        seed, relock_lr, RELOCK_NCE_WEIGHT, device, land_idx,
        (4 if run_mode == "smoke" else v3c.FRAME_REFRESH_FULL),
        "GLOBAL_RELOCK", "global", _dq, _keyed_eval_fixed, eval_every, out_dir,
        t0, art_dir / "_relock_ckpt_GLOBAL.pt",
        (8 if run_mode == "smoke" else RELOCK_CKPT_EVERY_FULL))
    relock_analysis = _analyze_relock_traj(relock_traj)

    codes_global_relocked = v3._encode_hard_block(student_relocked, Xhe, kb, blk_l)
    _run_unit(v3._semantic_unit, "GLOBAL_BLOCK_RELOCKED", codes_global_relocked,
              codes_global_relocked, Xhe, Xhe, 0, final_pairs, seed + 3)
    _run_unit(v3._keyed_unit, "GLOBAL_BLOCK_RELOCKED", "sbc",
              codes_global_relocked, kb, blk_l, 5, n_trials, gen_eval, device)
    _run_unit(v3._keyed_unit, "GLOBAL_BLOCK_RELOCKED", "sbc",
              codes_global_relocked, kb, blk_l, 5, n_trials, gen_eval, device,
              shuffled_key=True)

    # ---- Calibration control ----
    gen_ctrl = torch.Generator().manual_seed(seed + 1)
    random_codes = v3._random_block_codes(Xhe.shape[0], kb, blk_l, gen_ctrl)
    _run_unit(v3._keyed_unit, "RANDOM_BLOCK", "sbc", random_codes, kb, blk_l,
              5, n_trials, gen_eval, device)

    # ---- META_RULE_AF arms-must-differ ----
    digests = {}
    for name, c in [("INBATCH_BLOCK_REVERIFY", codes_inbatch),
                    ("GLOBAL_BLOCK_START", codes_global_start),
                    ("GLOBAL_BLOCK_RELOCKED", codes_global_relocked),
                    ("RANDOM_BLOCK", random_codes)]:
        digests[name] = hashlib.sha256(c.to(torch.int8).numpy().tobytes()).hexdigest()
    for a in digests:
        for b in digests:
            if a < b and digests[a] == digests[b]:
                raise RuntimeError(
                    f"failure_class=META_RULE_AF_VIOLATION: {a}/{b} identical")

    verdict, verdict_msg = _verdict_v4(per_unit, relock_analysis, expected_units, run_mode)
    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "run_tag": run_tag, "seed": int(seed), "device": device, "N": n_dim,
        "relock_nce_weight": RELOCK_NCE_WEIGHT,
        "relock_lr": relock_lr, "relock_steps": relock_steps,
        "relock_eval_every": eval_every, "relock_warmup_steps": warmup_steps,
        "relock_traj": relock_traj, "relock_analysis": relock_analysis,
        "per_unit": per_unit, "unit_failures": unit_fail,
        "n_units": len(per_unit), "expected_n_units": expected_units,
        "cardinality_ok": len(per_unit) == expected_units,
        "arms_differ_verified": True, "arm_code_sha256": digests,
        "final_metrics_atomicity": "tmp_replace",
        "composition_algebra": "SBC_block_local_circular_convolution",
        "objective": ("PHASE1=pure-eval reverify of existing INBATCH-RKD-only "
                     "nce=0 best-checkpoint (adds missing shuffled-key control); "
                     "PHASE2=short terminal NCE-relock (nce_weight="
                     f"{RELOCK_NCE_WEIGHT}, lr={relock_lr}, steps={relock_steps}"
                     ") fine-tune of existing GLOBAL-RKD-only nce=0 best-"
                     "checkpoint"),
        "progress_logging": "print_flush_true",
        "baseline_in_band": bool(
            (v3._by_unit(per_unit, "keyed", "GLOBAL_BLOCK_START", 5) or
             {"acc_at1": 1.0})["acc_at1"] < 0.5),
        "crlb_floor_computed": 0.901,
        "crlb_formula_reference": ("r_max = sigma_teacher / sqrt(sigma_teacher^2 + "
                                   "0.25/K), K=128 -> 0.901 (unchanged from v2/v3/v3b/v3c)"),
        "discriminator_reachability": True,
        "cell_chunked": False, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "calibration_check": "default_ok_for_this_regime",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[v4] verdict={verdict} msg={verdict_msg} elapsed={elapsed:.1f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Self-test (synthetic; no cache dependency; fast).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()

    # 1. relock LR schedule.
    lr0 = _relock_lr_at(0, 10, 1e-3)
    lr9 = _relock_lr_at(9, 10, 1e-3)
    assert 0 < lr0 < lr9 <= 1e-3 + 1e-12

    # 2. trajectory analysis: crossing + stability detection.
    traj_stable = [
        {"step": 0, "dense_full": 0.9, "keyed_acc1": 0.1},
        {"step": 100, "dense_full": 0.8, "keyed_acc1": 0.5},
        {"step": 200, "dense_full": 0.75, "keyed_acc1": 0.95},
        {"step": 300, "dense_full": 0.73, "keyed_acc1": 0.93},
    ]
    a_stable = _analyze_relock_traj(traj_stable)
    assert a_stable["crossing_step"] == 200
    assert a_stable["post_crossing_stable"] is True

    traj_unstable = [
        {"step": 0, "dense_full": 0.9, "keyed_acc1": 0.1},
        {"step": 100, "dense_full": 0.8, "keyed_acc1": 0.95},
        {"step": 200, "dense_full": 0.6, "keyed_acc1": 0.5},
    ]
    a_unstable = _analyze_relock_traj(traj_unstable)
    assert a_unstable["crossing_step"] == 100
    assert a_unstable["post_crossing_stable"] is False

    traj_never = [
        {"step": 0, "dense_full": 0.9, "keyed_acc1": 0.1},
        {"step": 100, "dense_full": 0.8, "keyed_acc1": 0.3},
    ]
    a_never = _analyze_relock_traj(traj_never)
    assert a_never["crossing_step"] is None

    # 3. end-to-end tiny synthetic relock run: checkpoint load from an
    #    EXTERNAL state dict (not v3c's own resume format), training runs,
    #    trajectory has step-0 + subsequent points, arms differ.
    n_dim, kb, blk_l, v_syn = 256, 16, 16, 300
    torch.manual_seed(21)
    Xsyn = torch.randn(v_syn, 64)
    Xsyn = Xsyn / Xsyn.norm(dim=-1, keepdim=True)
    gen = torch.Generator().manual_seed(21)
    pos_syn = torch.randint(0, v_syn, (v_syn,), generator=gen)
    semi_syn = torch.randint(0, v_syn, (v_syn, v3.N_SEMI_CANDS), generator=gen)
    land_syn = torch.randperm(v_syn, generator=gen)[:64]
    Xhe_syn = Xsyn[:48]

    init_student = v3._make_student("mlp", 64, kb * blk_l, "cpu", seed=99)
    init_state = init_student.state_dict()

    def _dq(student):
        return v3._dense_spearman_quick(student, Xhe_syn, 400, 5)

    def _keyed(student):
        codes = v3._encode_hard_block(student, Xhe_syn, kb, blk_l)
        gl = torch.Generator().manual_seed(5)
        u = v3._keyed_unit("T", "sbc", codes, kb, blk_l, 5, 20, gl, "cpu")
        return u["acc_at1"]

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        student_out, traj = _run_relock(
            kb, blk_l, Xsyn, pos_syn, semi_syn, init_state, 10, 24, 2, 13,
            1e-3, 0.5, "cpu", land_syn, 3, "TEST_RELOCK", "global", _dq,
            _keyed, 3, tdp, t0, tdp / "relock_test.pt", 100)
        assert len(traj) >= 2
        assert traj[0]["step"] == 0
        assert math.isfinite(traj[0]["dense_full"])
        assert 0.0 <= traj[0]["keyed_acc1"] <= 1.0
        w_init = torch.cat([p.flatten() for p in init_student.parameters()])
        w_out = torch.cat([p.flatten() for p in student_out.parameters()])
        assert not torch.allclose(w_init, w_out, atol=1e-6), (
            "selftest: relock training produced no weight change "
            "(training loop is a no-op)")

        # in_batch objective (land_idx=None) must also run without error.
        _, traj_ib = _run_relock(
            kb, blk_l, Xsyn, pos_syn, semi_syn, init_state, 8, 24, 2, 13,
            1e-3, 0.5, "cpu", None, 3, "TEST_RELOCK_IB", "in_batch", _dq,
            _keyed, 4, tdp, t0, tdp / "relock_test_ib.pt", 100)
        assert len(traj_ib) >= 2

        # global objective without land_idx must raise.
        try:
            _run_relock(kb, blk_l, Xsyn, pos_syn, semi_syn, init_state, 3, 24,
                       1, 13, 1e-3, 0.5, "cpu", None, 3, "TEST_BAD", "global",
                       _dq, _keyed, 2, tdp, t0, tdp / "relock_bad.pt", 100)
            raise AssertionError("selftest: global objective without land_idx should raise")
        except ValueError:
            pass

        # resume: a second call with more steps must extend, not restart, the
        # trajectory (checkpoint/resume discipline).
        student_r1, traj_r1 = _run_relock(
            kb, blk_l, Xsyn, pos_syn, semi_syn, init_state, 4, 24, 1, 17,
            1e-3, 0.5, "cpu", land_syn, 3, "TEST_RESUME", "global", _dq,
            _keyed, 2, tdp, t0, tdp / "relock_resume.pt", 2)
        len_before = len(traj_r1)
        student_r2, traj_r2 = _run_relock(
            kb, blk_l, Xsyn, pos_syn, semi_syn, init_state, 8, 24, 1, 17,
            1e-3, 0.5, "cpu", land_syn, 3, "TEST_RESUME", "global", _dq,
            _keyed, 2, tdp, t0, tdp / "relock_resume.pt", 2)
        assert len(traj_r2) > len_before

    # 4. verdict logic: hit all bands + cardinality + integrity gates.
    def _fake_unit(kind, arm, **kw):
        d = {"unit": f"{kind}::{arm}", "arm": arm, "kind": kind}
        d.update(kw)
        return d

    def _fake_units(inb_dense, inb_keyed, inb_shuf, gl_start_keyed,
                    gl_relock_shuf=0.02, rblock_keyed=0.99):
        return [
            _fake_unit("semantic", "INBATCH_BLOCK_REVERIFY", spearman_all=inb_dense),
            _fake_unit("keyed", "INBATCH_BLOCK_REVERIFY", J=5, acc_at1=inb_keyed),
            _fake_unit("shuffled_key", "INBATCH_BLOCK_REVERIFY", J=5, acc_at1=inb_shuf),
            _fake_unit("semantic", "GLOBAL_BLOCK_START", spearman_all=0.85),
            _fake_unit("keyed", "GLOBAL_BLOCK_START", J=5, acc_at1=gl_start_keyed),
            _fake_unit("semantic", "GLOBAL_BLOCK_RELOCKED", spearman_all=0.75),
            _fake_unit("keyed", "GLOBAL_BLOCK_RELOCKED", J=5, acc_at1=0.92),
            _fake_unit("shuffled_key", "GLOBAL_BLOCK_RELOCKED", J=5, acc_at1=gl_relock_shuf),
            _fake_unit("keyed", "RANDOM_BLOCK", J=5, acc_at1=rblock_keyed),
        ]

    relock_analysis_pass = {
        "crossing_step": 200, "crossing_dense": 0.75, "crossing_keyed": 0.92,
        "post_crossing_stable": True, "max_keyed_acc1": 0.95,
        "final_dense": 0.74, "final_keyed_acc1": 0.93, "traj_len": 5,
    }
    units_already_solved = _fake_units(0.87, 1.0, 0.0, 0.15)
    v1, m1 = _verdict_v4(units_already_solved, relock_analysis_pass, 9, "full")
    assert v1 == "HARD_PASS" and "ALREADY_JOINT_SOLVED_VIA_INBATCH" in m1, (v1, m1)

    units_relock_only = _fake_units(0.30, 0.20, 0.02, 0.15)
    v2, m2 = _verdict_v4(units_relock_only, relock_analysis_pass, 9, "full")
    assert v2 == "HARD_PASS" and "RELOCK_RECOVERS_GLOBAL_JOINT" in m2, (v2, m2)

    units_leak = _fake_units(0.87, 1.0, 0.5, 0.15)
    v3_verdict, m3 = _verdict_v4(units_leak, relock_analysis_pass, 9, "full")
    assert v3_verdict == "HARD_FAIL" and "SHUFFLED_KEY_LEAK_INBATCH" in m3, (v3_verdict, m3)

    units_vacuous = _fake_units(0.30, 0.20, 0.02, 0.8)
    v4_verdict, m4 = _verdict_v4(units_vacuous, relock_analysis_pass, 9, "full")
    assert v4_verdict == "HARD_FAIL" and "VACUOUS_RELOCK_TARGET" in m4, (v4_verdict, m4)

    relock_analysis_fail = {
        "crossing_step": None, "crossing_dense": None, "crossing_keyed": None,
        "post_crossing_stable": True, "max_keyed_acc1": 0.4,
        "final_dense": 0.55, "final_keyed_acc1": 0.4, "traj_len": 5,
    }
    units_neither = _fake_units(0.30, 0.20, 0.02, 0.15)
    v5, m5 = _verdict_v4(units_neither, relock_analysis_fail, 9, "full")
    assert v5 == "HARD_FAIL" and "JOINT_REQUIREMENT_NOT_MET" in m5, (v5, m5)

    v_card, m_card = _verdict_v4(units_already_solved[:3], relock_analysis_pass, 9, "full")
    assert v_card == "HARD_FAIL" and "CARDINALITY_BREACH" in m_card

    print(f"[selftest] PASS (relock LR schedule + trajectory crossing/stability "
          f"analysis + end-to-end relock train on external checkpoint state + "
          f"in_batch objective + land_idx-required-for-global guard + resume + "
          f"weight-change assertion + verdict bands incl already-solved / "
          f"relock-recovers / leak / vacuous-target / neither / cardinality) "
          f"elapsed={time.perf_counter() - t0:.2f}s", flush=True)
    return 0


# ---------------------------------------------------------------------------
# Entry.
# ---------------------------------------------------------------------------

def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=(
        "Encoder Migration Step 1b v4 -- joint reverify (INBATCH, pure eval) "
        "+ short terminal NCE-relock curriculum (GLOBAL)."))
    p.add_argument("--run-mode", default=os.environ.get("HDLAB_RUN_MODE", "self_test"),
                   choices=["self_test", "smoke", "full"])
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--full", action="store_true")
    p.add_argument("--seed", type=int, default=SEED_DEFAULT)
    p.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    p.add_argument("--n-dim", type=int, default=v3.N_DIM_DEFAULT)
    p.add_argument("--teacher-cache", default=None)
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
    return run_v4(args.run_mode, args.seed, args.device, args.n_dim,
                 args.teacher_cache)


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
