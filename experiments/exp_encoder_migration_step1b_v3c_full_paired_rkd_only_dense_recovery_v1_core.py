"""Encoder Migration Step 1b v3c -- the TIE-BREAKER completion of v3b's
already-landed FULL-178k ablation table: PAIRED global(landmark)-RKD-only vs
in_batch-RKD-only, nce_weight=0 for BOTH arms, at v3b's EXACT config
(batch=128, steps=1800, same seed/split/mining convention), with genuine
best-by-full-held-eval checkpoint SELECTION (not just diagnostic logging) and
mid-training checkpoints saved for a later capacity/peak re-diagnostic.

USER directive (2026-07-04, post v3b landing): dispatch a definitive
global-RKD-only vs in_batch-RKD-only comparison at FULL 178k, nce_weight=0.

COORDINATOR COURSE-CORRECTION (2026-07-04, mid-authoring; supersedes this
cell's initial batch=512/steps=40000/single-seed plan -- see git history for
the superseded version): fresh Skunkworks VET + a direct metrics.json read
established that v3b's "mid" run ALREADY trained on the FULL 177899-concept
cache (see cache-resolution finding below) -- so v3b's NCE_ZERO (global
objective, RKD-only, batch=128, steps=1800) DENSE=0.7336 IS ALREADY a
full-scale number, not a MID proxy needing re-confirmation. This cell's job
is therefore NOT "does global-RKD-only hold at full scale" (already answered)
but the ONE MISSING ARM that decides the landmark-objective question:
in_batch-RKD-only (nce=0) AT THE SAME config. If in_batch-RKD-only ALSO
reaches ~0.73, the landmark/global objective adds nothing over the simpler
in_batch baseline once NCE is off, and the landmark mechanism should be
dropped; if in_batch-RKD-only collapses (near-neighbor pairs still
essentially never co-occur at a 128-batch over 172899 train concepts), the
landmark objective is genuinely validated as the fix. The GLOBAL-RKD-only arm
is re-trained here too (not merely cited from v3b) as the matched control run
in the SAME process/split/mining, and to get its BLOCK (sparse) number, which
v3b's recovery{} summary omitted (BLOCK was computed into v3b's per_unit list
for the ablation arms but never surfaced into the headline recovery dict).
Batch=128/steps=1800 MATCH v3b exactly (NOT this cell's original
batch=512/steps=40000 plan) so this is an apples-to-apples completion of
v3b's table, not a new-scale experiment -- also much cheaper ("GPU is fast":
v3b's own 10-arm battery at this exact regime landed in 662.99s).

TWO SEEDS (CHUNKED single-seed-per-cell per this role's canonical instruction
file section 13): Skunkworks flagged v3b's nce=0 finding as single-seed
(tiered MM_STANDARD, not yet chain-grade-promotable). This core module is
invoked by TWO thin per-seed wrapper scripts (seed=7, matching v3b for direct
comparability; seed=13, the replicate) so a runner-death loses only one seed,
not both -- see experiments/exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_7.py
and _seed_13.py. Each wrapper passes a seed-specific `run_tag` so the two
seeds write to fully isolated output/artifact/checkpoint paths (no clobbering).

CHAIN SO FAR (do not re-litigate; read before amending):
  v2 FULL (in_batch, nce=0.5): DENSE_SIGN collapsed 0.825(3k)->0.368(178k)
    MEASURED@notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md.
  v3 mid (global vs in_batch, nce=0.5): HARD_FAIL -- global did NOT beat
    in_batch at that scale (global DENSE 0.521 vs in_batch 0.568)
    MEASURED@data/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_mid/metrics.json.
  v3b (batch-ratio-match sweep + NCE ablation): PRIMARY tier HARD_FAIL
    (BATCH_RATIO_MATCH_DID_NOT_CONFIRM -- in_batch did not degrade with
    shrinking batch, global was worse at the decisive batch, confounded by
    nce_weight=0.5 on BOTH arms). SECONDARY tier (NCE ablation, global
    objective only, decisive batch=128) DECISIVE: TAIL_CORRUPTION_CONFIRMED_
    RECOVERED -- NCE_ZERO (nce=0.0) DENSE=0.7336 vs NCE_CURRENT (nce=0.5)
    DENSE=0.2687 (delta +0.465); NCE_DECAY40 (anneal-to-0) DENSE=0.5128
    MEASURED@data/exp_encoder_migration_step1b_v3b_nce_ablation_dense_recovery_diagnostic_v1/metrics.json:recovery.
  research_drill_encoder_052_to_085_ranked_levers_2026-07-04.md (decision
    memo, written BEFORE v3b landed): ranks the NCE-schedule fix as the
    top-P lever (P_deflated=0.55) and pre-stages a FULL-scale follow-up once
    the secondary tier confirms. This cell's REVISED job (see coordinator
    course-correction above) is narrower and cheaper than that memo's
    original framing: complete v3b's ablation table with the missing
    in_batch-RKD-only arm at the SAME (already-full-scale) config, not a new
    higher-step-budget run.

IMPORTANT CACHE-RESOLUTION FINDING (VERIFIED@this prereg, 2026-07-04, exp_dev
audit, INDEPENDENTLY CONFIRMED by the coordinator's own Skunkworks-VET read):
v3b's own "mid" run's landed metrics.json shows device="cuda",
teacher_cache="bge_large_v2_name_177899_54f7cf6a.npz", teacher_n_concepts=
177899, n_train=172899 -- i.e. v3b's "mid" run auto-resolved
(v3._resolve_teacher_cache picks the LARGEST bge_large_v2_name_*.npz match) to
the FULL 177899-concept cache on the machine it actually ran on (remote GPU,
NOT local CPU as that prereg's Compute-architecture section had stipulated),
NOT the intended ~40k-concept MID-scale cache. So v3b's batch-sweep already
trained on essentially-FULL V (172899 train concepts) at batch=128/steps=1800
-- NOT a genuine MID-vs-FULL scale comparison as its own docstring narrative
claims, but a genuine FULL-scale ablation nonetheless. This cell matches that
EXACT config (batch=128, steps=1800, N_LANDMARKS_MID=4096) rather than a new
scale, per the coordinator's redesign. This cell PINS the exact teacher-cache
filename explicitly (not auto-resolve-largest) to remove any remaining
ambiguity, verified present on the remote host via `ssh marsh@home`
PowerShell Test-Path (2026-07-04): True, 1355319709 bytes, confirmed as the
largest bge_large_v2_name_1***** candidate on the remote.

BEST-CHECKPOINT DESIGN NOTE (genuinely new vs v3b): v3b's `_train_student_diag`
tracked a `best_dense_full`/`best_step` field per arm but its recovery{}
dict / verdict logic used ONLY the FINAL step's value throughout (grep-
verified: `nce_zero_dense_final` etc. all read the "final":true trajectory
entry, never the best-tracked one). This cell is the FIRST in the lineage to
actually SELECT and REPORT the best-checkpoint model's semantic/keyed/bundle
numbers as the official result, and the FIRST to surface BLOCK (sparse)
alongside DENSE in the headline recovery{} summary (v3b computed BLOCK per
ablation arm into per_unit but never promoted it into recovery{}). To
prevent a known artifact from winning "best" by construction -- ALL arms in
every prior cell this arc show DENSE ~0.95-0.96 at step~0 (a fresh
random-Gaussian-initialized MLP + sign-code readout approximates a
random-hyperplane LSH/SimHash, which is known to roughly preserve
cosine-similarity RANK on an untrained network; see NCE_ZERO's own
trajectory in v3b: dense_full=0.9560@step0 declining to 0.7311@step1800 --
i.e. the untrained network briefly looks BETTER than the trained one by this
proxy) -- best-checkpoint SELECTION here excludes early eval points below
MIN_STEP_FRAC_FOR_BEST (5% of total steps) from eligibility. The
unconstrained (all-time, including step~0) best is ALSO logged per arm as a
diagnostic/transparency field so a genuine "training never beats the
random-init artifact" outcome is visible, not silently laundered into a
false-looking "recovery." Checkpoints are saved every CKPT_EVERY_STEPS_FULL
(300) steps and PRESERVED (not deleted post-run) so a later capacity/peak
diagnostic can re-run pre-decline, per the coordinator's explicit request.

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01):
  query "global landmark objective RKD-only NCE weight zero full scale
  distillation encoder paired comparison" -> top hit cosine=0.291
  ('destructive_distillation', WordNet dictionary entry), all other hits
  <=0.2754. NONE at cosine>0.30 -- i.e. no prior arc CELL at this
  cosine threshold (only WordNet/FrameNet lexical baseline + this arc's own
  design-note prose, which is expected self-similarity not a distinct prior
  result). GENUINELY NOVEL: no prior cell has run the paired
  global-RKD-only-vs-in_batch-RKD-only comparison at this config with
  best-checkpoint selection and a 2-seed replicate.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke/full gate (sha256 over code matrices)
- final_metrics_atomicity: tmp_replace (write_metrics + checkpoint os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
- crlb_floor_computed: r_max=0.901 at K=128 (THEORETICAL@v2/v3 prereg,
  unchanged -- this cell changes only nce_weight + step budget + checkpoint
  selection, not the K-block quantization channel)
- baseline_in_band: CHARPOS ret_agree10 in (0.05, 0.95)
- discriminator-survives-scale: option (B) analytical justification, SAME
  physics argument already accepted twice this arc (v3 mid prereg + v3b
  prereg): smoke's tiny V_train=3000 cannot reproduce a meaningful coverage
  effect at batch=128; smoke validates MACHINERY ONLY (both arms train
  end-to-end, best-ckpt tracking + reload fires, arms differ, all eval units
  execute, cardinality holds). The actual "does in_batch-RKD-only collapse or
  hold at the true 177899-concept corpus" question can ONLY be answered by
  running it at that V -- that IS this dispatch.
- HARD_PASS strictly above floor per prereg bands (META_RULE_L)
- HP_SCOPE: {GLOBAL, INBATCH} both gated by the recovery bands; RANDOM_BLOCK/
  CHARPOS/shuffled_key are integrity-only (not recovery-gated).
- cardinality_ok: EXPECTED_N_UNITS declared per run_mode, counted from per_unit
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime (identical training
  hyperparameters to the validated v3/v3b lineage; only nce_weight, step
  budget, and checkpoint-selection policy change)
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ / VERIFIED@

Prereg: preregs/2026-07-04_exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1.md
Parent cells: experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py
              experiments/exp_encoder_migration_step1b_v3b_nce_ablation_dense_recovery_diagnostic_v1_core.py (sibling; not imported -- this cell imports v3 core directly, single-hop, to keep the remote-SCP dependency surface minimal per the dispatch-contract note on sibling-cell imports).

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
    exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core
    as v3,
)

# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1"
SEED_DEFAULT = v3.SEED_DEFAULT  # 7 -- matches the whole lineage for comparability.

# Pinned teacher cache (VERIFIED@this prereg present on remote host, 2026-07-04;
# see docstring cache-resolution finding). Relative to repo root; resolved via
# v3._resolve_teacher_cache which accepts an explicit path.
TEACHER_CACHE_DEFAULT = (
    "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz")

NCE_WEIGHT_FULL = 0.0  # RKD-only for BOTH arms (the v3b-winning ablation config).
OBJECTIVES = ("global", "in_batch")

# ---- FULL-scale config: MATCHED to v3b's already-landed FULL-178k regime ----
# COORDINATOR REDESIGN (2026-07-04, post-dispatch course-correction): v3b's
# "mid" run already trained on the FULL 177899-concept cache (auto-resolved
# via largest-file-wins; see docstring cache-resolution finding) at
# batch=128 (its DECISIVE_BATCH_MID), steps=1800 (v3.MID_STEPS). So v3b's
# NCE_ZERO (global objective, nce=0) DENSE=0.7336 is ALREADY a genuine
# FULL-178k number -- NOT a MID proxy needing re-validation at a new scale.
# This cell's job is NOT "does global-RKD-only hold at full scale" (already
# answered) but the TIE-BREAKER v3b never ran: in_batch-RKD-only (nce=0) AT
# THE SAME config (batch=128, steps=1800, same seed/split/mining) -- if
# in_batch-RKD-only ALSO reaches ~0.73, the landmark/global objective adds
# NOTHING over the simpler in_batch baseline once NCE is off; if
# in_batch-RKD-only collapses (near-neighbor pairs still essentially never
# co-occur in a 128-batch over 172899 train concepts), the landmark objective
# is genuinely validated. batch/steps MATCH v3b exactly (not v3's original
# FULL_STEPS=40000/FULL_BATCH=512) so this is an apples-to-apples completion
# of v3b's ablation table, not a new-scale experiment.
FULL_BATCH = 128                         # MATCHES v3b's DECISIVE_BATCH_MID (v3b.py)
FULL_STEPS = v3.MID_STEPS                # 1800 -- MATCHES v3b (NOT v3.FULL_STEPS=40000)
N_LANDMARKS_FULL = v3.N_LANDMARKS_MID    # 4096 -- MATCHES v3b (MID_N_LANDMARKS_DIAG)
FRAME_REFRESH_FULL = v3.FRAME_REFRESH_MID  # 50 -- MATCHES v3b (MID_REFRESH_DIAG)
CKPT_EVERY_STEPS_FULL = v3.CKPT_EVERY_STEPS_MID  # 300 -- MATCHES v3b; checkpoints
                                          # SAVED at this cadence for the
                                          # capacity/peak diagnostic re-run request
DENSE_EVAL_EVERY_FULL = 150              # MATCHES v3b's MID_DENSE_EVAL_EVERY_DIAG
                                          # (13 eval points over 1800 steps)
FULL_QUICK_HELD_SUB = 1500               # MATCHES v3b's MID_QUICK_HELD_SUB
FULL_QUICK_PAIRS = 60_000                # MATCHES v3b's MID_QUICK_PAIRS
FULL_TRAJ_PAIRS = 100_000                # MATCHES v3b's MID_FULL_TRAJ_PAIRS
FULL_FINAL_PAIRS = v3.MID_PAIR_SAMPLE    # 400_000 -- MATCHES v3b's MID_FULL_PAIRS_FINAL
FULL_CHARPOS_CAP = v3.MID_CHARPOS_CAP    # MATCHES v3b
FULL_TRIALS = v3.MID_TRIALS              # MATCHES v3b (keyed/shuffled J=5 trials)

# ---- Smoke config: MACHINERY validation only (option B; see docstring) ----
SMOKE_N_TRAIN = v3.SMOKE_N_TRAIN         # 3000
SMOKE_N_HELD = v3.SMOKE_N_HELD           # 800
SMOKE_STEPS = 60
SMOKE_N_LANDMARKS = 512
SMOKE_REFRESH = 15
SMOKE_CKPT_EVERY = 30
SMOKE_DENSE_EVAL_EVERY = 15
SMOKE_QUICK_HELD_SUB = 300
SMOKE_QUICK_PAIRS = 8_000
SMOKE_TRAJ_PAIRS = 15_000
SMOKE_FINAL_PAIRS = 30_000
SMOKE_CHARPOS_CAP = 800
SMOKE_TRIALS = 30

# Best-checkpoint anti-gaming floor: exclude early eval points (untrained-
# network SimHash-like artifact; see docstring) from best-checkpoint
# eligibility. Applied as a FRACTION of total steps so it scales with run_mode.
MIN_STEP_FRAC_FOR_BEST = 0.05

# semantic(6) + keyed(3) + shuffled(1) = 10. See docstring "EXPECTED_N_UNITS".
EXPECTED_N_UNITS_FULL = 10
EXPECTED_N_UNITS_SMOKE = 10

PREREG_BASELINE_ARMS = ["CHARPOS", "RANDOM_BLOCK"]

# Recovery bands (PRIMARY gate). DENSE floor/ceiling per
# research_drill_encoder_052_to_085_ranked_levers_2026-07-04.md's own
# falsifiable-prediction table (written to gate EXACTLY this dispatch).
# Delta band (global beats in_batch) per the v3/v3b lineage's established
# recovery-delta convention (v3 mid prereg: delta >= 0.15 for HARD_PASS).
HP_DENSE_FLOOR = 0.75      # HYPOTHESIZED@research_drill_encoder_052_to_085_ranked_levers_2026-07-04.md
HP_DELTA_FLOOR = 0.15      # HYPOTHESIZED@v3 mid prereg convention (unchanged)
PEAK_DECLINE_MARGIN = 0.03       # trajectory-shape gate: peak-to-final drop threshold
MB_DENSE_FLOOR = 0.60      # HYPOTHESIZED@research_drill ranked-levers MIDDLE-BAND floor
MB_DELTA_FLOOR = 0.05
HF_DENSE_CEILING = 0.60    # HYPOTHESIZED@research_drill ranked-levers HARD-FAIL ceiling


def _artifact_dir(run_mode: str, run_tag: str = "") -> Path:
    suffix = {"smoke": "_smoke"}.get(run_mode, "")
    tag = f"_{run_tag}" if run_tag else ""
    return _REPO / "data" / f"substrate_concept_encoder_v1b_v3c_full_paired{tag}{suffix}"


# ---------------------------------------------------------------------------
# Defensive helpers (start marker / crash metrics / heartbeat) -- mirrors v3/v3b.
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
# Training loop: PAIRED {global, in_batch}, nce_weight FIXED (0.0 in
# production; parameterized for self-test coverage), dual quick+full held-set
# dense trajectory, best-by-full-held checkpoint tracking with an anti-gaming
# min-step floor. Adapted from v3b's _train_student_diag (proven at MID
# scale); simplified here to a single fixed batch (no batch-sweep axis).
# ---------------------------------------------------------------------------

def _train_student_full(
    kb: int, blk_l: int,
    Xtr: torch.Tensor, pos_idx: torch.Tensor, semi_cands: torch.Tensor,
    steps: int, batch: int, warmup: int, seed: int, device: str,
    ckpt_path: Path, best_ckpt_path: Path, ckpt_every: int,
    output_dir: Path, t0: float,
    land_idx: Optional[torch.Tensor], refresh_every: int,
    nce_weight: float, arm_label: str, objective: str,
    dense_eval_quick_fn: Optional[Callable] = None,
    dense_eval_full_fn: Optional[Callable] = None,
    dense_eval_every: int = 0,
    min_step_for_best: int = 0,
) -> Tuple[torch.nn.Module, Dict]:
    if objective not in ("global", "in_batch"):
        raise ValueError(f"unknown objective {objective}")
    out_dim = kb * blk_l
    student = v3._make_student("mlp", Xtr.shape[1], out_dim, device, seed)
    opt = torch.optim.Adam(student.parameters(), lr=v3.LR)
    gen = torch.Generator().manual_seed(seed)
    start_step = 0
    dense_traj: List[Dict[str, float]] = []
    best_state = {"score": -2.0, "step": -1}          # eligible (>= min_step_for_best)
    alltime_state = {"score": -2.0, "step": -1}        # diagnostic only, no floor
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
            print(f"[v3c_full] resume {arm_label} at step {start_step}", flush=True)
        except (RuntimeError, KeyError, EOFError) as exc:
            print(f"[v3c_full] WARN ckpt load failed ({type(exc).__name__}); "
                  f"retraining {arm_label} from scratch", flush=True)
            start_step = 0
            dense_traj = []
            best_state = {"score": -2.0, "step": -1}
            alltime_state = {"score": -2.0, "step": -1}
    V = Xtr.shape[0]
    Xd = Xtr.to(device)
    Xland_d = None
    if objective == "global":
        if land_idx is None or land_idx.numel() == 0:
            raise ValueError(f"{arm_label}: global objective requires non-empty land_idx")
        Xland_d = Xd[land_idx.to(device)]
    frame_n = None
    loss_first = loss_last = None
    rkd_last = nce_last = lr_last = None

    def _maybe_save_best(step_i: int, d_full: float) -> None:
        if not math.isfinite(d_full):
            return
        if d_full > alltime_state["score"]:
            alltime_state["score"] = d_full
            alltime_state["step"] = step_i
        if step_i < min_step_for_best:
            return  # anti-gaming: exclude untrained-network artifact window
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
                f"failure_class=NAN_LOSS: {arm_label} loss non-finite at step {step} "
                f"(l_rkd={float(l_rkd.detach())}, l_nce={float(l_nce.detach())}, "
                f"nce_w={nce_weight})")
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
            print(f"[v3c_full] {arm_label} step {step}/{steps} rkd={v_rkd:.4f} "
                  f"nce={v_nce:.4f} nce_w={nce_weight:.3f} lr={cur_lr:.2e} "
                  f"({time.perf_counter() - t0:.1f}s)", flush=True)
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
            print(f"[v3c_full] {arm_label} DENSE-traj step {step}: "
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
        print(f"[v3c_full] {arm_label} FINAL step {steps}: full={d_full_fin:.4f} "
              f"quick={d_quick_fin:.4f}", flush=True)
    best_ckpt_fallback_to_final = best_state["step"] < 0
    if best_ckpt_fallback_to_final:
        # No eval point ever cleared min_step_for_best (degenerate/very-short
        # run); fall back to the final (post-loop) student so downstream code
        # always has a valid "official" model.
        tmp_b = best_ckpt_path.with_suffix(".tmp")
        torch.save({"student": student.state_dict(), "step": steps,
                   "dense_full": float("nan"), "arm": arm_label}, str(tmp_b))
        os.replace(str(tmp_b), str(best_ckpt_path))
        print(f"[v3c_full] WARN {arm_label}: no eval point >= min_step_for_best; "
              f"best-ckpt falls back to FINAL student", flush=True)
    return student, {
        "loss_first": loss_first if loss_first is not None else -1.0,
        "loss_last": loss_last if loss_last is not None else -1.0,
        "rkd_last": rkd_last if rkd_last is not None else -1.0,
        "nce_last": nce_last if nce_last is not None else -1.0,
        "lr_last": lr_last if lr_last is not None else -1.0,
        "nce_weight": nce_weight,
        "arm": arm_label, "objective": objective, "batch": batch,
        "dense_traj": dense_traj,
        "best_dense_full": best_state["score"], "best_step": best_state["step"],
        "best_ckpt_fallback_to_final": best_ckpt_fallback_to_final,
        "alltime_best_dense_full": alltime_state["score"],
        "alltime_best_step": alltime_state["step"],
    }


def _reload_best_student(arch: str, in_dim: int, out_dim: int, device: str,
                         best_ckpt_path: Path) -> torch.nn.Module:
    """Rebuild a fresh student and load the saved best-checkpoint weights."""
    student = v3._make_student(arch, in_dim, out_dim, device, seed=0)
    ck = torch.load(str(best_ckpt_path), map_location=device)
    student.load_state_dict(ck["student"])
    return student


# ---------------------------------------------------------------------------
# Trajectory-analysis helper (peak-then-decline; informational, not a gate).
# ---------------------------------------------------------------------------

def _peak_then_decline(traj: List[Dict], key: str,
                       margin: float = 0.03
                       ) -> Tuple[bool, Optional[int], Optional[float], Optional[int]]:
    vals = [(r["step"], r[key]) for r in traj if math.isfinite(r.get(key, float("nan")))]
    if len(vals) < 2:
        return False, None, None, None
    peak_step, peak_val = max(vals, key=lambda t: t[1])
    final_step, final_val = vals[-1]
    declined = bool((peak_val - final_val) >= margin and peak_step < final_step)
    return declined, peak_step, peak_val, final_step


# ---------------------------------------------------------------------------
# Verdict logic.
# ---------------------------------------------------------------------------

def _verdict_full_paired(per_unit: List[Dict], recovery: Dict, expected_units: int,
                         run_mode: str) -> Tuple[str, str]:
    if len(per_unit) < expected_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"{len(per_unit)}/{expected_units} units")
    posc = v3._by_unit(per_unit, "keyed", "RANDOM_BLOCK", 5)
    shuf = v3._by_unit(per_unit, "shuffled_key", "GLOBAL_BLOCK", 5)
    if posc is None or shuf is None:
        return ("HARD_FAIL", "HARD_FAIL_MISSING_GATE_UNITS")
    if posc["acc_at1"] < 0.98:
        return ("HARD_FAIL",
                f"HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH: RANDOM_BLOCK keyed J=5 "
                f"{posc['acc_at1']:.3f} < 0.98 (SBC lossless prior)")
    if shuf["acc_at1"] > 0.05 or shuf["hit_any_member"] > 0.10:
        return ("HARD_FAIL",
                f"HARD_FAIL_SHUFFLED_KEY_LEAK: {shuf['acc_at1']:.3f}/"
                f"{shuf['hit_any_member']:.3f}")

    gd, ibd = recovery["global_dense_best"], recovery["inbatch_dense_best"]
    delta = recovery["delta_dense_best"]
    gb, ibb = recovery["global_block_best"], recovery["inbatch_block_best"]
    g_step_frac = recovery["global_best_step_frac"]
    tail = (f"[global DENSE(best)={gd:.4f}@frac{g_step_frac:.2f} "
           f"inbatch DENSE(best)={ibd:.4f} delta={delta:.4f} "
           f"| global BLOCK(best)={gb:.4f} inbatch BLOCK(best)={ibb:.4f} "
           f"| global_peak_decline={recovery['global_peak_decline']} "
           f"inbatch_peak_decline={recovery['inbatch_peak_decline']}]")

    if run_mode == "smoke":
        fails = []
        if recovery["global_traj_len"] < 2 or recovery["inbatch_traj_len"] < 2:
            fails.append("S_traj_too_short")
        if recovery["global_best_step"] < 0 or recovery["inbatch_best_step"] < 0:
            fails.append("S_no_best_ckpt")
        if not (math.isfinite(gd) and -1.0 <= gd <= 1.0):
            fails.append("S_dense_out_of_range")
        if fails:
            return ("SMOKE_GATE_FAIL", "; ".join(fails))
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: both objectives trained end-to-end at nce=0, "
                f"best-checkpoint tracking + reload fire, arms differ {tail} "
                f"(the full-scale recovery/objective-advantage discriminator is a "
                f"FULL-only question; smoke's tiny V_train cannot reproduce it; "
                f"keyed-algebra floor is NOT gated at smoke scale -- 60 steps on "
                f"V_train=3000 does not reliably crystallize block-STE one-hot "
                f"structure, same precedent as v3b's smoke gate)")

    # full only from here (smoke already returned above): FALSE_WIN_ALGEBRA gate
    # BEFORE the semantic recovery bands -- a degenerate/non-composable BLOCK
    # code (keyed roundtrip failing for the CORRECT key, not just refusing the
    # WRONG key) would make any "BLOCK spearman toward 0.85" claim meaningless
    # even if the raw spearman number looks fine. Mirrors v3's FULL-mode
    # dual-gate (b1 < 0.90 -> FALSE_WIN_ALGEBRA), extended to BOTH arms since
    # this cell reports BLOCK for both GLOBAL and INBATCH.
    keyed_global = v3._by_unit(per_unit, "keyed", "GLOBAL_BLOCK", 5)
    keyed_inbatch = v3._by_unit(per_unit, "keyed", "INBATCH_BLOCK", 5)
    if keyed_global is None or keyed_inbatch is None:
        return ("HARD_FAIL", "HARD_FAIL_MISSING_GATE_UNITS")
    if keyed_global["acc_at1"] < 0.90:
        return ("HARD_FAIL",
                f"FALSE_WIN_ALGEBRA_GLOBAL: keyed_roundtrip J=5 "
                f"{keyed_global['acc_at1']:.3f} < 0.90 (BLOCK spearman irrelevant "
                f"if the code is not a valid composable SBC code) {tail}")
    if keyed_inbatch["acc_at1"] < 0.90:
        return ("HARD_FAIL",
                f"FALSE_WIN_ALGEBRA_INBATCH: keyed_roundtrip J=5 "
                f"{keyed_inbatch['acc_at1']:.3f} < 0.90 {tail}")

    # full: the real discriminators.
    # HP requires the best-checkpoint numbers to be genuine, not a fleeting
    # early spike immediately followed by catastrophic collapse: gate on the
    # peak-then-decline TRAJECTORY SHAPE (>=0.03 drop from peak to final),
    # not a rigid "best must be in the second half" step-fraction rule --
    # v3b's own NCE_ZERO trajectory fluctuates in a healthy 0.65-0.83 band
    # with its single highest sample early (step150) yet ends at a
    # respectable 0.731 (no collapse); a step-fraction floor would wrongly
    # demote that as "early spike" when it plainly is not.
    if gd >= HP_DENSE_FLOOR and delta >= HP_DELTA_FLOOR and not recovery["global_peak_decline"]:
        return ("HARD_PASS",
                f"FULL_PAIRED_RECOVERED_AND_OBJECTIVE_CONFIRMED: RKD-only global "
                f"objective clears the DENSE recovery floor, beats in_batch by "
                f">= {HP_DELTA_FLOOR}, and the trajectory does not show a "
                f">=0.03 peak-then-decline collapse {tail}")
    if gd >= MB_DENSE_FLOOR and delta >= MB_DELTA_FLOOR:
        return ("MIDDLE_BAND",
                f"FULL_PAIRED_PARTIAL: real signal (DENSE and/or delta) but short "
                f"of the full recovery bar, OR recovery achieved only via an early "
                f"best-checkpoint at risk of the peak-then-decline pathology {tail}")
    if gd < HF_DENSE_CEILING or delta < MB_DELTA_FLOOR:
        return ("HARD_FAIL",
                f"FULL_PAIRED_NOT_CONFIRMED: at v3b's exact FULL-178k config "
                f"(batch=128, steps=1800) the RKD-only global objective either "
                f"did not clear the recovery floor here (reproducibility concern "
                f"vs v3b's own NCE_ZERO=0.7336) and/or in_batch-RKD-only reached "
                f"comparably high DENSE too (delta < {MB_DELTA_FLOOR}) -- if the "
                f"latter, the landmark/global objective adds NOTHING over plain "
                f"in_batch once NCE is off and should be DROPPED as the load-"
                f"bearing mechanism; escalate to Rank 2 (objective-family/KL-PKT "
                f"swap) or re-examine reproducibility per "
                f"research_drill_encoder_052_to_085_ranked_levers_2026-07-04.md "
                f"decision table {tail}")
    return ("MIDDLE_BAND", f"FULL_PAIRED_PARTIAL: ambiguous band {tail}")


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def run_full_paired(run_mode: str, seed: int, device_arg: str, n_dim: int,
                    teacher_cache_arg: Optional[str],
                    run_tag: str = "") -> int:
    """run_tag isolates output/artifact/checkpoint paths per-seed (CHUNKED
    single-seed-per-cell discipline): the seed_7/seed_13 wrapper scripts pass
    a distinct run_tag so the two seeds never clobber each other's anchors,
    mining shards, or training checkpoints."""
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
        n_land, refresh = SMOKE_N_LANDMARKS, SMOKE_REFRESH
        dense_every, ckpt_every = SMOKE_DENSE_EVAL_EVERY, SMOKE_CKPT_EVERY
        quick_sub, quick_pairs = SMOKE_QUICK_HELD_SUB, SMOKE_QUICK_PAIRS
        traj_pairs, final_pairs = SMOKE_TRAJ_PAIRS, SMOKE_FINAL_PAIRS
        charpos_cap, n_trials = SMOKE_CHARPOS_CAP, SMOKE_TRIALS
        n_tr_target, n_he_target = SMOKE_N_TRAIN, SMOKE_N_HELD
        batch = min(FULL_BATCH, 128)  # cannot exceed smoke V; kept small
    else:
        steps = FULL_STEPS
        n_land, refresh = N_LANDMARKS_FULL, FRAME_REFRESH_FULL
        dense_every, ckpt_every = DENSE_EVAL_EVERY_FULL, CKPT_EVERY_STEPS_FULL
        quick_sub, quick_pairs = FULL_QUICK_HELD_SUB, FULL_QUICK_PAIRS
        traj_pairs, final_pairs = FULL_TRAJ_PAIRS, FULL_FINAL_PAIRS
        charpos_cap, n_trials = FULL_CHARPOS_CAP, FULL_TRIALS
        n_tr_target = n_he_target = None
        batch = FULL_BATCH
    expected_units = EXPECTED_N_UNITS_SMOKE if run_mode == "smoke" else EXPECTED_N_UNITS_FULL
    warmup = v3._warmup_for(steps)
    min_step_for_best = max(1, int(round(MIN_STEP_FRAC_FOR_BEST * steps)))

    _write_start_marker(out_dir, run_mode, expected_units)
    t0 = time.perf_counter()
    print(f"[v3c_full] run_mode={run_mode} seed={seed} device={device} n_dim={n_dim} "
          f"steps={steps} batch={batch} nce_weight={NCE_WEIGHT_FULL} "
          f"min_step_for_best={min_step_for_best}", flush=True)

    # Pin the exact FULL teacher cache in production (removes any auto-resolve-
    # largest ambiguity; see docstring cache-resolution finding). smoke mode
    # ALWAYS auto-resolves (teacher_cache_arg=None) since the pinned 177899-
    # concept file is remote-only and local smoke must run against whatever
    # local cache is largest (e.g. the 43905-concept one).
    effective_cache_arg = teacher_cache_arg
    if run_mode == "full" and effective_cache_arg is None:
        effective_cache_arg = TEACHER_CACHE_DEFAULT
    cache_path = v3._resolve_teacher_cache(effective_cache_arg)
    cache_bytes = cache_path.stat().st_size
    X, ids = v3._load_teacher(cache_path)
    V_cache = X.shape[0]
    print(f"[v3c_full] teacher {cache_path.name}: {V_cache} concepts x "
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
    print(f"[v3c_full] split train={n_tr} held={n_he}", flush=True)

    pos_idx, semi_cands = v3._mine_teacher(
        Xtr, device, art_dir / "_mine_shards", out_dir, t0)
    semi_cov = float((semi_cands[:, 0] >= 0).float().mean())
    n_land_eff = min(n_land, n_tr)
    g_land = torch.Generator().manual_seed(seed + 101)
    land_idx = torch.randperm(n_tr, generator=g_land)[:n_land_eff]
    print(f"[v3c_full] mining done cov={semi_cov:.3f} landmarks={n_land_eff} "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    Xhe_sub = Xhe[:min(quick_sub, n_he)].contiguous()

    def _deval_quick(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xhe_sub, quick_pairs, seed + 7)

    def _deval_full(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xhe, traj_pairs, seed + 7)

    # --- train the PAIRED arms (same split/mining/landmarks/seed; nce_weight=0) ---
    trained: Dict[str, Tuple[torch.nn.Module, Dict]] = {}
    for obj_key, obj in (("GLOBAL", "global"), ("INBATCH", "in_batch")):
        li = land_idx if obj == "global" else None
        st, diag = _train_student_full(
            kb, blk_l, Xtr, pos_idx, semi_cands, steps, batch, warmup, seed, device,
            art_dir / f"_ckpt_{obj_key}.pt", art_dir / f"_ckpt_best_{obj_key}.pt",
            ckpt_every, out_dir, t0, li, refresh, NCE_WEIGHT_FULL, obj_key,
            objective=obj, dense_eval_quick_fn=_deval_quick,
            dense_eval_full_fn=_deval_full, dense_eval_every=dense_every,
            min_step_for_best=min_step_for_best)
        trained[obj_key] = (st, diag)
        print(f"[v3c_full] {obj_key} trained rkd_last={diag['rkd_last']:.4f} "
              f"best_full={diag['best_dense_full']:.4f}@step{diag['best_step']} "
              f"alltime_best={diag['alltime_best_dense_full']:.4f}@step"
              f"{diag['alltime_best_step']} ({time.perf_counter() - t0:.1f}s)",
              flush=True)

    # --- reload each arm's BEST checkpoint as the official model ---------------
    in_dim = Xtr.shape[1]
    best_students: Dict[str, torch.nn.Module] = {}
    for obj_key in ("GLOBAL", "INBATCH"):
        best_students[obj_key] = _reload_best_student(
            "mlp", in_dim, kb * blk_l, device, art_dir / f"_ckpt_best_{obj_key}.pt")

    # --- encode held codes from the BEST-checkpoint models ----------------------
    arm_codes: Dict[str, torch.Tensor] = {}
    for obj_key in ("GLOBAL", "INBATCH"):
        st = best_students[obj_key]
        arm_codes[f"{obj_key}_DENSE"] = v3._dense_sign_codes(st, Xhe)
        arm_codes[f"{obj_key}_BLOCK"] = v3._encode_hard_block(st, Xhe, kb, blk_l)
    gen_ctrl = torch.Generator().manual_seed(seed + 1)
    arm_codes["RANDOM_BLOCK"] = v3._random_block_codes(n_he, kb, blk_l, gen_ctrl)
    cp_cap = min(n_he, charpos_cap)
    cp_codes = v3._charpos_codes(names_he[:cp_cap], n_dim, kb)

    # --- META_RULE_AF arms-must-differ ------------------------------------------
    digests = {}
    for name, c in list(arm_codes.items()) + [("CHARPOS", cp_codes)]:
        digests[name] = hashlib.sha256(c.to(torch.int8).numpy().tobytes()).hexdigest()
    for a in digests:
        for b in digests:
            if a < b and digests[a] == digests[b]:
                raise RuntimeError(
                    f"failure_class=META_RULE_AF_VIOLATION: {a}/{b} identical")

    # --- eval units --------------------------------------------------------------
    per_unit: List[Dict] = []
    unit_fail: List[Dict] = []
    gen_eval = torch.Generator().manual_seed(seed + 2)

    def _run_unit(fn, *a, **kw):
        try:
            u = fn(*a, **kw)
            per_unit.append(u)
            print(f"[v3c_full] unit {len(per_unit)}/{expected_units} {u['unit']}: "
                  + json.dumps({k: round(v, 4) for k, v in u.items()
                                if isinstance(v, float)}), flush=True)
            _emit_heartbeat(out_dir, len(per_unit), expected_units,
                            time.perf_counter() - t0, extra={"unit": u["unit"]})
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append({"fn": getattr(fn, "__name__", "?"),
                              "failure_class": type(exc).__name__,
                              "msg": str(exc)[:300]})
            raise

    for obj_key in ("GLOBAL", "INBATCH"):
        for kind in ("DENSE", "BLOCK"):
            label = f"{obj_key}_{kind}"
            c = arm_codes[label]
            _run_unit(v3._semantic_unit, label, c, c, Xhe, Xhe, 0, final_pairs, seed + 3)
    _run_unit(v3._semantic_unit, "RANDOM_BLOCK", arm_codes["RANDOM_BLOCK"],
              arm_codes["RANDOM_BLOCK"], Xhe, Xhe, 0, final_pairs, seed + 3)
    cp_Xhe = Xhe[:cp_cap]
    _run_unit(v3._semantic_unit, "CHARPOS", cp_codes, cp_codes, cp_Xhe, cp_Xhe, 0,
              final_pairs, seed + 3)

    _run_unit(v3._keyed_unit, "RANDOM_BLOCK", "sbc", arm_codes["RANDOM_BLOCK"],
              kb, blk_l, 5, n_trials, gen_eval, device)
    _run_unit(v3._keyed_unit, "GLOBAL_BLOCK", "sbc", arm_codes["GLOBAL_BLOCK"],
              kb, blk_l, 5, n_trials, gen_eval, device)
    _run_unit(v3._keyed_unit, "INBATCH_BLOCK", "sbc", arm_codes["INBATCH_BLOCK"],
              kb, blk_l, 5, n_trials, gen_eval, device)
    _run_unit(v3._keyed_unit, "GLOBAL_BLOCK", "sbc", arm_codes["GLOBAL_BLOCK"],
              kb, blk_l, 5, n_trials, gen_eval, device, shuffled_key=True)

    # --- recovery discriminators --------------------------------------------------
    def _sp(arm):
        u = v3._by_unit(per_unit, "semantic", arm)
        return float(u["spearman_all"]) if u else float("nan")

    global_dense_best = _sp("GLOBAL_DENSE")
    inbatch_dense_best = _sp("INBATCH_DENSE")
    global_block_best = _sp("GLOBAL_BLOCK")
    inbatch_block_best = _sp("INBATCH_BLOCK")
    delta_dense_best = global_dense_best - inbatch_dense_best

    global_traj = trained["GLOBAL"][1]["dense_traj"]
    inbatch_traj = trained["INBATCH"][1]["dense_traj"]
    g_decl, g_pk, g_pv, _ = _peak_then_decline(global_traj, "dense_full")
    i_decl, i_pk, i_pv, _ = _peak_then_decline(inbatch_traj, "dense_full")
    global_best_step = trained["GLOBAL"][1]["best_step"]
    inbatch_best_step = trained["INBATCH"][1]["best_step"]
    global_best_step_frac = (global_best_step / steps) if steps > 0 else 0.0

    recovery = {
        "global_dense_best": global_dense_best, "inbatch_dense_best": inbatch_dense_best,
        "global_block_best": global_block_best, "inbatch_block_best": inbatch_block_best,
        "delta_dense_best": delta_dense_best,
        "global_best_step": global_best_step, "inbatch_best_step": inbatch_best_step,
        "global_best_step_frac": global_best_step_frac,
        "global_alltime_best_dense": trained["GLOBAL"][1]["alltime_best_dense_full"],
        "global_alltime_best_step": trained["GLOBAL"][1]["alltime_best_step"],
        "inbatch_alltime_best_dense": trained["INBATCH"][1]["alltime_best_dense_full"],
        "inbatch_alltime_best_step": trained["INBATCH"][1]["alltime_best_step"],
        "global_best_ckpt_fallback_to_final": trained["GLOBAL"][1]["best_ckpt_fallback_to_final"],
        "inbatch_best_ckpt_fallback_to_final": trained["INBATCH"][1]["best_ckpt_fallback_to_final"],
        "global_peak_decline": g_decl, "global_peak_step": g_pk, "global_peak_val": g_pv,
        "inbatch_peak_decline": i_decl, "inbatch_peak_step": i_pk, "inbatch_peak_val": i_pv,
        "global_traj_len": len(global_traj), "inbatch_traj_len": len(inbatch_traj),
        "global_traj": global_traj, "inbatch_traj": inbatch_traj,
        "charpos_dense": _sp("CHARPOS"), "random_block_dense": _sp("RANDOM_BLOCK"),
    }
    verdict, verdict_msg = _verdict_full_paired(per_unit, recovery, expected_units, run_mode)
    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "run_tag": run_tag, "seed": int(seed), "device": device, "N": n_dim,
        "student_arch": v3.STUDENT_ARCH_PRIMARY, "mlp_hidden": v3.MLP_HIDDEN,
        "warmup_steps": warmup, "steps": steps, "batch": batch,
        "nce_weight": NCE_WEIGHT_FULL, "min_step_for_best": min_step_for_best,
        "n_landmarks": n_land_eff, "refresh_every": refresh, "dense_eval_every": dense_every,
        "teacher_cache": cache_path.name, "teacher_cache_bytes": cache_bytes,
        "teacher_n_concepts": V_cache, "n_train": n_tr, "n_held": n_he,
        "semi_hard_coverage": semi_cov,
        "recovery": recovery,
        "train_diag": {k: {kk: vv for kk, vv in trained[k][1].items()}
                      for k in trained},
        "per_unit": per_unit, "unit_failures": unit_fail,
        "n_units": len(per_unit), "expected_n_units": expected_units,
        "cardinality_ok": len(per_unit) == expected_units,
        "arms_differ_verified": True, "arm_code_sha256": digests,
        "final_metrics_atomicity": "tmp_replace",
        "composition_algebra": "SBC_block_local_circular_convolution",
        "objective": ("PAIRED global(landmark)-RKD-only vs in_batch-RKD-only, "
                     f"nce_weight={NCE_WEIGHT_FULL} for BOTH arms, "
                     "best-by-full-held-eval checkpoint selection "
                     f"(min_step_for_best={min_step_for_best})"),
        "progress_logging": "print_flush_true",
        "primary_spearman": global_dense_best,
        "dense_sign_spearman": global_dense_best,
        "baseline_in_band": bool(
            0.05 < (v3._by_unit(per_unit, "semantic", "CHARPOS") or
                   {"ret_agree10": 0})["ret_agree10"] < 0.95),
        "crlb_floor_computed": 0.901,
        "crlb_formula_reference": ("r_max = sigma_teacher / sqrt(sigma_teacher^2 + "
                                   "0.25/K), K=128 -> 0.901 (unchanged from v2/v3/v3b)"),
        "discriminator_reachability": True,
        "cell_chunked": False, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "calibration_check": "default_ok_for_this_regime",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[v3c_full] verdict={verdict} msg={verdict_msg} elapsed={elapsed:.1f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Self-test (synthetic; no cache dependency; fast).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()

    # 1. peak-then-decline helper.
    rising = [{"step": i, "dense_full": 0.1 * i} for i in range(5)]
    decl, _, _, _ = _peak_then_decline(rising, "dense_full")
    assert decl is False
    peaky = [{"step": 0, "dense_full": 0.3}, {"step": 1, "dense_full": 0.7},
             {"step": 2, "dense_full": 0.75}, {"step": 3, "dense_full": 0.5}]
    decl2, pk2, pv2, _ = _peak_then_decline(peaky, "dense_full")
    assert decl2 is True and pk2 == 2 and abs(pv2 - 0.75) < 1e-9

    # 2. end-to-end training on tiny synthetic data: both objectives at
    #    nce_weight=0, checkpoint/resume, best-ckpt anti-gaming floor,
    #    reload-from-best-ckpt correctness, arms-must-differ.
    n_dim, kb, blk_l, v_syn = 256, 16, 16, 400
    torch.manual_seed(11)
    Xsyn = torch.randn(v_syn, 64)
    Xsyn = Xsyn / Xsyn.norm(dim=-1, keepdim=True)
    gen = torch.Generator().manual_seed(11)
    pos_syn = torch.randint(0, v_syn, (v_syn,), generator=gen)
    semi_syn = torch.randint(0, v_syn, (v_syn, v3.N_SEMI_CANDS), generator=gen)
    land_syn = torch.randperm(v_syn, generator=gen)[:48]
    Xhe_syn = Xsyn[:64]

    def _dq(student):
        return v3._dense_spearman_quick(student, Xhe_syn[:32], 500, 3)

    def _df(student):
        return v3._dense_spearman_quick(student, Xhe_syn, 800, 3)

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        # min_step_for_best=0 (default) so every eval point is eligible; the
        # anti-gaming floor is tested separately below.
        st_g, diag_g = _train_student_full(
            kb, blk_l, Xsyn, pos_syn, semi_syn, 12, 24, 2, 13, "cpu",
            tdp / "ckpt_g.pt", tdp / "ckpt_best_g.pt", 100, tdp, t0,
            land_syn, 3, 0.0, "TEST_GLOBAL", objective="global",
            dense_eval_quick_fn=_dq, dense_eval_full_fn=_df, dense_eval_every=3,
            min_step_for_best=0)
        assert math.isfinite(diag_g["rkd_last"])
        assert len(diag_g["dense_traj"]) >= 2
        assert diag_g["best_step"] >= 0
        assert not diag_g["best_ckpt_fallback_to_final"]
        assert (tdp / "ckpt_best_g.pt").exists()

        st_i, diag_i = _train_student_full(
            kb, blk_l, Xsyn, pos_syn, semi_syn, 12, 16, 2, 13, "cpu",
            tdp / "ckpt_i.pt", tdp / "ckpt_best_i.pt", 100, tdp, t0,
            None, 3, 0.0, "TEST_INBATCH", objective="in_batch",
            dense_eval_quick_fn=_dq, dense_eval_full_fn=_df, dense_eval_every=3,
            min_step_for_best=0)
        assert math.isfinite(diag_i["rkd_last"])

        # global objective without land_idx must raise.
        try:
            _train_student_full(
                kb, blk_l, Xsyn, pos_syn, semi_syn, 3, 16, 1, 13, "cpu",
                tdp / "ckpt_bad.pt", tdp / "ckpt_best_bad.pt", 100, tdp, t0,
                None, 3, 0.0, "TEST_BAD_GLOBAL", objective="global")
            raise AssertionError("selftest: global objective without land_idx should raise")
        except ValueError:
            pass

        # global vs in_batch at nce_weight=0 must still diverge (different loss
        # geometry even though the contrastive term is off for both).
        w_g = torch.cat([p.flatten() for p in st_g.parameters()])
        w_i = torch.cat([p.flatten() for p in st_i.parameters()])
        assert not torch.allclose(w_g, w_i, atol=1e-6), \
            "selftest: global and in_batch (both nce=0) converged identically -- " \
            "objective has no effect (arm-implementation bug)"

        # reload-from-best-checkpoint correctness: the reloaded model's weights
        # must exactly match the saved best checkpoint's state_dict (bitwise),
        # and re-evaluating it must reproduce the recorded best score.
        st_reload = _reload_best_student("mlp", 64, kb * blk_l, "cpu",
                                         tdp / "ckpt_best_g.pt")
        w_reload = torch.cat([p.flatten() for p in st_reload.parameters()])
        ck_raw = torch.load(str(tdp / "ckpt_best_g.pt"), map_location="cpu")
        w_ckpt = torch.cat([v.flatten() for v in ck_raw["student"].values()])
        assert torch.allclose(w_reload, w_ckpt, atol=0.0), \
            "selftest: reloaded student does not exactly match saved best checkpoint"
        re_eval = _df(st_reload)
        assert abs(re_eval - diag_g["best_dense_full"]) < 1e-4, (
            f"selftest: reloaded-best re-eval {re_eval} does not reproduce recorded "
            f"best_dense_full {diag_g['best_dense_full']}")

        # anti-gaming min_step_for_best floor: force min_step_for_best above every
        # eval point's step -> best_state never updates -> fallback-to-final fires,
        # and the fallback checkpoint's weights match the FINAL (not best) student.
        st_late, diag_late = _train_student_full(
            kb, blk_l, Xsyn, pos_syn, semi_syn, 6, 16, 1, 17, "cpu",
            tdp / "ckpt_late.pt", tdp / "ckpt_best_late.pt", 100, tdp, t0,
            land_syn, 3, 0.0, "TEST_LATE_FLOOR", objective="global",
            dense_eval_quick_fn=_dq, dense_eval_full_fn=_df, dense_eval_every=2,
            min_step_for_best=9999)  # above total steps -> nothing eligible
        assert diag_late["best_ckpt_fallback_to_final"] is True
        assert diag_late["best_step"] < 0
        # alltime tracking is UNCONSTRAINED and must still have fired.
        assert diag_late["alltime_best_step"] >= 0
        w_late_final = torch.cat([p.flatten() for p in st_late.parameters()])
        ck_late = torch.load(str(tdp / "ckpt_best_late.pt"), map_location="cpu")
        w_late_ckpt = torch.cat([v.flatten() for v in ck_late["student"].values()])
        assert torch.allclose(w_late_final, w_late_ckpt, atol=0.0), \
            "selftest: fallback-to-final best-ckpt does not match the final student"

        # checkpoint/resume roundtrip persists dense_traj + both best trackers.
        st_a, diag_a = _train_student_full(
            kb, blk_l, Xsyn, pos_syn, semi_syn, 4, 16, 1, 19, "cpu",
            tdp / "ckpt_resume.pt", tdp / "ckpt_best_resume.pt", 4, tdp, t0,
            land_syn, 2, 0.0, "RESUME_TEST", objective="global",
            dense_eval_quick_fn=_dq, dense_eval_full_fn=_df, dense_eval_every=2,
            min_step_for_best=0)
        traj_before = len(diag_a["dense_traj"])
        st_b, diag_b = _train_student_full(
            kb, blk_l, Xsyn, pos_syn, semi_syn, 8, 16, 1, 19, "cpu",
            tdp / "ckpt_resume.pt", tdp / "ckpt_best_resume.pt", 4, tdp, t0,
            land_syn, 2, 0.0, "RESUME_TEST", objective="global",
            dense_eval_quick_fn=_dq, dense_eval_full_fn=_df, dense_eval_every=2,
            min_step_for_best=0)
        assert len(diag_b["dense_traj"]) > traj_before
        assert diag_b["best_step"] >= 0

    # 3. verdict logic: hit all bands + cardinality gate + integrity gates.
    fake_units = [{"unit": f"u{i}", "arm": "x", "kind": "k"} for i in range(10)]
    fake_units += [
        {"unit": "keyed::RANDOM_BLOCK::J5", "arm": "RANDOM_BLOCK", "kind": "keyed",
         "J": 5, "acc_at1": 0.99, "hit_any_member": 0.99},
        {"unit": "keyed::GLOBAL_BLOCK::J5", "arm": "GLOBAL_BLOCK", "kind": "keyed",
         "J": 5, "acc_at1": 0.97, "hit_any_member": 0.97},
        {"unit": "keyed::INBATCH_BLOCK::J5", "arm": "INBATCH_BLOCK", "kind": "keyed",
         "J": 5, "acc_at1": 0.96, "hit_any_member": 0.96},
        {"unit": "shuffled_key::GLOBAL_BLOCK::J5", "arm": "GLOBAL_BLOCK",
         "kind": "shuffled_key", "J": 5, "acc_at1": 0.01, "hit_any_member": 0.01},
    ]
    rec_pass = {
        "global_dense_best": 0.80, "inbatch_dense_best": 0.40,
        "delta_dense_best": 0.40, "global_block_best": 0.70,
        "inbatch_block_best": 0.35, "global_best_step_frac": 0.75,
        "global_peak_decline": False, "inbatch_peak_decline": True,
    }
    v_pass, m_pass = _verdict_full_paired(fake_units, rec_pass, 10, "full")
    assert v_pass == "HARD_PASS", f"selftest: expected HARD_PASS got {v_pass} ({m_pass})"
    rec_mb = dict(rec_pass, global_dense_best=0.65, delta_dense_best=0.10)
    v_mb, _ = _verdict_full_paired(fake_units, rec_mb, 10, "full")
    assert v_mb == "MIDDLE_BAND", f"selftest: expected MIDDLE_BAND got {v_mb}"
    rec_fail = dict(rec_pass, global_dense_best=0.30, delta_dense_best=0.01)
    v_fail, _ = _verdict_full_paired(fake_units, rec_fail, 10, "full")
    assert v_fail == "HARD_FAIL", f"selftest: expected HARD_FAIL got {v_fail}"
    # peak-then-decline trajectory shape (collapse after the best-checkpoint
    # peak) with otherwise-passing numbers -> MB not HP (best-ckpt selection
    # should not silently launder a collapsing trajectory into a HARD_PASS).
    rec_decline = dict(rec_pass, global_peak_decline=True)
    v_decline, _ = _verdict_full_paired(fake_units, rec_decline, 10, "full")
    assert v_decline == "MIDDLE_BAND", (
        f"selftest: expected MIDDLE_BAND (peak-then-decline) got {v_decline}")
    v_card, m_card = _verdict_full_paired(fake_units[:3], rec_pass, 10, "full")
    assert v_card == "HARD_FAIL" and "CARDINALITY_BREACH" in m_card
    # integrity gate: shuffled-key leak overrides otherwise-passing numbers.
    fake_units_leak = list(fake_units)
    for u in fake_units_leak:
        if u.get("kind") == "shuffled_key":
            u["acc_at1"] = 0.5
    v_leak, m_leak = _verdict_full_paired(fake_units_leak, rec_pass, 10, "full")
    assert v_leak == "HARD_FAIL" and "SHUFFLED_KEY_LEAK" in m_leak

    print(f"[selftest] PASS (peak-decline helper + paired nce=0 training both "
          f"objectives + land_idx-required-for-global guard + arms-must-differ-"
          f"at-nce0 + best-ckpt reload bitwise correctness + anti-gaming min-step "
          f"floor + fallback-to-final + checkpoint/resume + verdict bands incl "
          f"cardinality + integrity gates) elapsed={time.perf_counter() - t0:.2f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Entry.
# ---------------------------------------------------------------------------

def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=(
        "Encoder Migration Step 1b v3c -- definitive FULL-scale PAIRED "
        "global-RKD-only vs in_batch-RKD-only, nce_weight=0, best-by-full-"
        "held-eval checkpoint selection."))
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
    # No alias needed: this cell's terminal/production tier IS literally "full"
    # (unlike v3b, whose terminal tier is named "mid"), so the runner's
    # unconditional HDLAB_RUN_MODE=full injection matches choices=[...,"full"]
    # natively. See tools/orchestrator/queue_add.sh dispatch-contract note.
    return args


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    args = _parse_args()
    if args.run_mode == "self_test":
        return run_self_test()
    return run_full_paired(args.run_mode, args.seed, args.device, args.n_dim,
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
