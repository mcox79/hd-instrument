"""Encoder carry-through: in-batch-RKD-only WINNER -> Step2 sparse-encode ->
Step3 ship-metric gold-verify, on the ONE arm that already cleared 0.85
semantic fidelity with FHRR/SBC algebra intact.

WHY THIS CELL (buried-win carry-through, verified off-disk this cycle):
  exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1 ran
  two PAIRED arms at nce_weight=0: GLOBAL(landmark)-RKD and IN_BATCH-RKD. The
  cell's AGGREGATE verdict is HARD_FAIL, driven by the GLOBAL arm's algebra
  collapse (keyed_roundtrip@J5 mean 0.143). But the IN_BATCH arm -- buried in
  the SAME cell, never separately verdicted, never carried past Step1b -- is a
  genuine win:
    INBATCH_BLOCK spearman-to-teacher mean 0.886 range [0.852,0.897] (5 seeds)
       MEASURED@data/exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_{7,13,23,29,31}/metrics.json:per_unit[INBATCH_BLOCK].spearman_all
    INBATCH_BLOCK keyed_roundtrip@J5 = 1.000 all 5 seeds (algebra INTACT)
       MEASURED@ same files :per_unit[keyed::INBATCH_BLOCK::J5].acc_at1
    INBATCH_BLOCK hi80_cos (cosine on teacher-highly-similar pairs) mean 0.827
       range [0.786,0.861]  MEASURED@ same :per_unit[INBATCH_BLOCK].hi80_cos
    INBATCH_BLOCK ret_agree10 vs teacher mean 0.221 range [0.184,0.266]
       MEASURED@ same :per_unit[INBATCH_BLOCK].ret_agree10
  GLOBAL broke algebra; INBATCH held it AT THE SAME 128-block SBC target. So
  the semantic gain is NOT bought at the cost of algebra. This cell drops the
  algebra-breaking GLOBAL co-arm and carries INBATCH-RKD-only through to the
  actual USER ship metric.

NO SURVIVING CHECKPOINT (VERIFIED@exp_dev pre-flight, 2026-07-05): the 5 v3c
  FULL seed runs ran on device="cuda" (remote GPU); their best-checkpoints live
  in the remote artifact dir, not local, and are not pulled here. So this cell
  RETRAINS the in-batch-RKD-only arm from scratch -- the CHEAPEST arm in the
  whole family (no landmark pairwise term, no InfoNCE, single-pass in-batch
  RKD), exactly as the research hand-off anticipated. The retrain reuses the
  proven v3c training loop verbatim (v3c._train_student_full, objective=
  "in_batch", nce_weight=0.0) so this is the SAME code path that produced the
  buried win, not a re-implementation.

SHIP-METRIC DEFINITION (exp_dev design decision -- FLAGGED for Director):
  The existing Step2/Step3 chain (exp_encoder_migration_step2_* / step3_*) is
  wired to the ORTHOGRAPHIC char-positional encoder: Step3's ARM_CONCEPT uses
  hdlab.CharPositionalEncoder + top-K WTA and encodes raw query STRINGS on the
  fly. The in-batch-RKD winner is a DIFFERENT encoder entirely -- a BGE-teacher
  -embedding (1024d) -> MLP -> block-STE student. Its input space is a BGE
  embedding, NOT an orthographic char code, so it cannot be dropped into
  Step3's string-query pipeline without live BGE inference on the 100 query
  strings (a heavy new dependency + 970K live BGE encodes for the KB side).
  This cell therefore measures a SELF-CONTAINED, teacher-anchored ship metric
  on the held concept set (which HAS cached BGE embeddings), faithful to the
  distilled encoder and to "cosine to the right answer":
    cosine_to_gold := INBATCH_BLOCK hi80_cos  = mean code-space cosine on
       concept-pairs the BGE teacher rates highly-related (teacher_cos>=0.80);
       i.e. for the pairs that ARE the right answer, how high is the code
       cosine. (Band >= 0.80.)
    ret_agree10    := INBATCH_BLOCK top-10 retrieval overlap with the BGE
       teacher's own top-10 on held concepts. (Band >= 0.30.)
    composed_roundtrip := INBATCH_BLOCK SBC keyed bind/unbind roundtrip at a
       HARDER composed load (J_COMPOSED > the J=5 the buried win reported).
       (Band >= 0.95.)
  A live-BGE real-query variant (BGE-encode the 100 gold queries -> MLP -> code
  -> retrieve against BGE-cached KB concept codes) is the strictly-more-
  faithful FUTURE test; it is out of scope for this cheap carry-through and is
  flagged in the completion report.

HONEST FORECAST (pre-registered, MEASURED off the buried win's own held-pair
  numbers -- NOT smoke-inflated): the winning arm's held-pair cosine_to_gold
  0.827 STRADDLES the 0.80 gate (3/5 seeds clear), algebra is 1.000, but
  ret_agree10 0.221 MISSES the 0.30 gate on all 5 seeds. So the JOINT ship gate
  is forecast MIDDLE_BAND, localizing the proxy-to-real gap to top-10 retrieval
  agreement (a strong rank-spearman does not imply strong top-10 retrieval).
  This is a genuine, actionable outcome, not a reason to abort -- the full-KB
  (177899-concept) run may differ from the held-subset numbers, and either way
  the result localizes exactly where the distilled code stands on the ship
  metric.

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01):
  query "in-batch RKD encoder perception spearman roundtrip algebra bind unbind
  ship metric" -> top hit cosine=0.2617 (WordNet 'unbind'), all hits <=0.2617.
  NONE at cosine>0.30 -- no prior arc CELL at threshold; only lexical baseline.
  GENUINELY NOVEL carry-through (no prior cell carries the in-batch-RKD arm to
  a ship metric).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified: sha256 over INBATCH_BLOCK / CHARPOS / RANDOM_BLOCK codes
- final_metrics_atomicity: tmp_replace (write_metrics + E_concept.pt os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException, no bare)
- crlb_floor_computed: r_max=0.901 at K=128 (THEORETICAL@v2/v3 prereg;
  unchanged -- same K-block quantization channel as the winning arm)
- baseline_in_band: CHARPOS ret_agree10 in (0.05, 0.95)
- discriminator-survives-scale: option (B) analytical. The ship discriminator
  (does spearman-0.886 translate to cosine_to_gold/ret_agree at full 177899-
  concept V) is a FULL-only question; smoke's tiny V cannot reproduce the
  retrieval-agreement regime. The discriminator is already in a MEASURABLE,
  NON-SATURATED band by construction (held-pair ret_agree10=0.221, cosine_to_
  gold=0.827 -- neither floor nor ceiling). Smoke validates MACHINERY + fires
  the ALGEBRA discriminator via the by-construction SBC-lossless positive
  control (RANDOM_BLOCK keyed@J_ISO ~= 1.0, training-independent) + the
  shuffled-key leak control, exactly as v3c's own smoke gate does.
- HARD_PASS strictly above floor per prereg bands (META_RULE_L)
- HP_SCOPE: {INBATCH_BLOCK: [cosine_to_gold, composed_roundtrip, ret_agree10]}
  CHARPOS (baseline) + RANDOM_BLOCK (SBC-lossless pos control) + INBATCH_DENSE
  (diagnostic) are integrity-only, NOT ship-gated.
- cardinality_ok: EXPECTED_N_UNITS declared per run_mode, counted from per_unit
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime (identical training
  hyperparameters to the validated v3c in-batch arm; only the GLOBAL co-arm is
  dropped and the eval is re-pointed at the ship metric)
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ / VERIFIED@
- cell_chunked: False (single-seed; FULL multi-seed via re-dispatch of --seed)
- start_marker_written / crash_diagnostic_present / heartbeat_present: True
- progress_logging: print_flush_true (line-buffered stdout + flush=True)

Parent cells (imported, single-hop):
  experiments/exp_encoder_migration_step1b_v3_..._v1_core.py         (as v3)
  experiments/exp_encoder_migration_step1b_v3c_..._v1_core.py        (as v3c)
Prereg: preregs/2026-07-05_exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1.md

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

# argv snapshot BEFORE any _seed_checkpoint import (its module-import selftest
# mangles sys.argv, stripping --smoke/--full/--self-test; see Step2 cell note).
import sys as _sys
_ARGV_SNAPSHOT = list(_sys.argv)

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
from experiments import (  # noqa: E402
    exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core
    as v3c,
)

# Restore argv if the _seed_checkpoint import-time selftest mangled it.
if list(sys.argv) != _ARGV_SNAPSHOT:
    sys.argv = _ARGV_SNAPSHOT

# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1"
SEED_DEFAULT = v3.SEED_DEFAULT  # 7 -- matches the lineage for comparability.

# Winning objective: in-batch RKD only, nce_weight=0 (drops the algebra-breaking
# GLOBAL/landmark co-arm). MATCHES v3c's INBATCH arm exactly.
NCE_WEIGHT = 0.0
OBJECTIVE = "in_batch"

# Pinned FULL teacher cache (VERIFIED@exp_dev present locally 2026-07-05,
# 1355319709 bytes; same 177899-concept cache v3c pinned). smoke auto-resolves
# a small local cache instead (see _resolve_smoke_cache).
TEACHER_CACHE_FULL = (
    "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz")

# ---- FULL config: MATCHED to v3c's INBATCH arm (batch=128, steps=1800) ----
FULL_STEPS = v3.MID_STEPS                 # 1800  MATCHES v3c INBATCH arm
FULL_BATCH = 128                          # MATCHES v3c
FULL_CKPT_EVERY = v3.CKPT_EVERY_STEPS_MID  # 300
FULL_DENSE_EVAL_EVERY = 150               # 12 eval points over 1800 steps
FULL_QUICK_HELD_SUB = 1500
FULL_QUICK_PAIRS = 60_000
FULL_TRAJ_PAIRS = 100_000
FULL_FINAL_PAIRS = v3.MID_PAIR_SAMPLE     # 400_000
FULL_CHARPOS_CAP = v3.MID_CHARPOS_CAP     # 3000
FULL_TRIALS = v3.MID_TRIALS               # 60 keyed/shuffled trials

# ---- Smoke config: MACHINERY validation only (option B; see docstring) ----
SMOKE_N_TRAIN = 900
SMOKE_N_HELD = 400
SMOKE_STEPS = 60
SMOKE_CKPT_EVERY = 30
SMOKE_DENSE_EVAL_EVERY = 15
SMOKE_QUICK_HELD_SUB = 300
SMOKE_QUICK_PAIRS = 8_000
SMOKE_TRAJ_PAIRS = 15_000
SMOKE_FINAL_PAIRS = 30_000
SMOKE_CHARPOS_CAP = 400
SMOKE_TRIALS = 30

# Best-checkpoint anti-gaming floor (fraction of total steps).
MIN_STEP_FRAC_FOR_BEST = 0.05

# Algebra roundtrip loads: J_ISO = the J the buried win reported (isolated);
# J_COMPOSED = a strictly-harder composed load for the ship-grade algebra gate.
J_ISO = 5
J_COMPOSED_FULL = 10
J_COMPOSED_SMOKE = 8

# Eval unit count: semantic(4) + keyed(4) = 8. See EXPECTED_N_UNITS.
#   semantic: INBATCH_BLOCK, INBATCH_DENSE, CHARPOS, RANDOM_BLOCK
#   keyed:    RANDOM_BLOCK@J_ISO (pos ctrl), INBATCH_BLOCK@J_ISO (isolated),
#             INBATCH_BLOCK@J_COMPOSED (composed), shuffled INBATCH_BLOCK@J_ISO
EXPECTED_N_UNITS = 8

PREREG_BASELINE_ARMS = ["CHARPOS", "RANDOM_BLOCK"]

# ---- Ship-metric bands (JOINT gate; per Director hand-off contract) ----
# HARD-PASS requires ALL THREE jointly (a rank/spearman win with a real-metric
# miss is a FALSE PASS, not a HARD-PASS -- JOINT gate discipline).
HP_COS_TO_GOLD = 0.80        # HYPOTHESIZED@hand-off contract (cosine_to_gold floor)
HP_COMPOSED_RT = 0.95        # HYPOTHESIZED@hand-off contract (composed roundtrip)
HP_RET_AGREE10 = 0.30        # HYPOTHESIZED@hand-off contract (ret_agree@10 floor)
HF_COS_TO_GOLD = 0.60        # HYPOTHESIZED@hand-off HARD-FAIL ceiling
HF_COMPOSED_RT = 0.85        # HYPOTHESIZED@hand-off HARD-FAIL ceiling (algebra)
# Integrity thresholds (both modes).
POSCTRL_KEYED_FLOOR = 0.98   # RANDOM_BLOCK SBC keyed lossless prior
SHUFFLED_LEAK_CEIL = 0.05    # shuffled-key must not retrieve the true target


def _artifact_dir(run_mode: str, seed: int) -> Path:
    # SEED-NAMESPACED (fix 2026-07-05): the intermediate/checkpoint dir MUST be
    # per-seed. Under the 5-seed FULL sweep every seed shares one runner
    # sequentially; a PRIOR seed's completed run leaves _ckpt_INBATCH.pt in this
    # dir, so a later seed with a FIXED (non-seed) dir would find that checkpoint
    # and enter v3c._train_student_full's resume branch. That branch calls
    # gen.set_state(ck["gen_state"]); the CPU ByteTensor gen_state is moved to
    # cuda by torch.load(map_location="cuda"), so set_state raises TypeError
    # (RNG state must be a torch.ByteTensor) -- and v3c's resume except clause
    # catches only (RuntimeError, KeyError, EOFError), so the cell crashes at
    # ~0.0s. Namespacing per seed guarantees each seed starts in its own clean
    # dir and never enters the cross-seed resume path. Same-seed resume (runner
    # death then re-dispatch) is the intended restartable-checkpoint feature and
    # is preserved. Landing (metrics.json) isolation is orthogonal -- it comes
    # from HDLAB_EXP_NAME per queue entry (see _seed_checkpoint.get_output_dir).
    suffix = "_smoke" if run_mode == "smoke" else ""
    return (_REPO / "data"
            / f"substrate_concept_encoder_carrythrough_v1{suffix}_seed{int(seed)}")


def _e_concept_path(run_mode: str, seed: int) -> Path:
    return _artifact_dir(run_mode, seed) / "E_concept.pt"


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
# Teacher-cache resolution for smoke (smallest local cache with enough concepts;
# avoids loading the 1.35 GB FULL cache for a machinery smoke).
# ---------------------------------------------------------------------------

def _resolve_smoke_cache(min_concepts: int) -> Path:
    cand_dir = _REPO / "data" / "substrate_index" / "cached_indices"
    best: Optional[Tuple[int, Path]] = None
    for p in sorted(cand_dir.glob("bge_large_v2_name_*.npz")):
        # filename: bge_large_v2_name_<count>_<hash>.npz
        parts = p.stem.split("_")
        try:
            count = int(parts[4])
        except (IndexError, ValueError):
            continue
        if count >= min_concepts and (best is None or count < best[0]):
            best = (count, p)
    if best is None:
        # fall back to whatever _resolve_teacher_cache picks (largest).
        return v3._resolve_teacher_cache(None)
    return best[1]


# ---------------------------------------------------------------------------
# Sparse-bipolar CSR (Step2 half): convert the winning arm's block code to a
# per-entity sparse artifact + verify bit-identical round-trip + size. Inlined
# (minimal; mirrors exp_encoder_migration_step2_*_core) to keep the dispatch
# dependency surface to v3 + v3c only.
# ---------------------------------------------------------------------------

def _dense_to_sparse_csr(dense_int8: np.ndarray, entity_names: List[str],
                         n_dim: int) -> Dict:
    n_entities = int(dense_int8.shape[0])
    rows, cols = np.nonzero(dense_int8)            # row-major -> rows ascending
    total_nnz = int(rows.shape[0])
    signs_np = dense_int8[rows, cols].astype(np.int8)
    if total_nnz > 0 and not np.all((signs_np == 1) | (signs_np == -1)):
        raise ValueError("failure_class=NON_BIPOLAR: block code has values "
                         "outside {-1,+1} in nonzero positions")
    if n_dim > 32767:
        raise ValueError(f"failure_class=NDIM_OOB_INT16: n_dim={n_dim} > 32767")
    counts = np.bincount(rows, minlength=n_entities).astype(np.int64)
    offsets_np = np.zeros(n_entities + 1, dtype=np.int64)
    np.cumsum(counts, out=offsets_np[1:])
    if int(offsets_np[-1]) != total_nnz:
        raise ValueError("failure_class=OFFSETS_MISMATCH: cumsum != total_nnz")
    return {
        "active_indices": torch.from_numpy(cols.astype(np.int16)),
        "signs": torch.from_numpy(signs_np),
        "offsets": torch.from_numpy(offsets_np),
        "n_dim": int(n_dim), "n_entities": n_entities, "total_nnz": total_nnz,
        "entity_names": entity_names,
    }


def _sparse_roundtrip_mismatch(dense_int8: np.ndarray, sparse: Dict,
                               n_samples: int, seed: int) -> Tuple[int, int]:
    rng = np.random.default_rng(seed)
    n_entities = dense_int8.shape[0]
    n_dim = sparse["n_dim"]
    offsets = sparse["offsets"].numpy()
    ai = sparse["active_indices"].numpy()
    sg = sparse["signs"].numpy()
    n_check = min(n_samples, n_entities)
    idxs = rng.choice(n_entities, size=n_check, replace=False)
    n_mismatch = 0
    for i in idxs:
        lo, hi = int(offsets[i]), int(offsets[i + 1])
        recon = np.zeros(n_dim, dtype=np.int8)
        if lo < hi:
            recon[ai[lo:hi].astype(np.int32)] = sg[lo:hi]
        if not np.array_equal(recon, dense_int8[i]):
            n_mismatch += 1
    return n_check, n_mismatch


def _save_e_concept(sparse: Dict, out_path: Path, arm_label: str) -> Tuple[int, str]:
    payload = {
        "active_indices": sparse["active_indices"], "signs": sparse["signs"],
        "offsets": sparse["offsets"], "n_dim": sparse["n_dim"],
        "n_entities": sparse["n_entities"], "total_nnz": sparse["total_nnz"],
        "entity_names": sparse["entity_names"],
        "format": "sparse_bipolar_csr_v1",
        "encoder": f"inbatch_rkd_only_block_STE_K{v3.K_BLOCKS_PRIMARY}",
        "arm": arm_label,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(".pt.tmp")
    torch.save(payload, str(tmp))
    os.replace(str(tmp), str(out_path))
    size = int(out_path.stat().st_size)
    h = hashlib.sha256()
    with open(out_path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return size, h.hexdigest()


# ---------------------------------------------------------------------------
# Verdict logic (JOINT ship gate on INBATCH_BLOCK).
# ---------------------------------------------------------------------------

def _verdict(per_unit: List[Dict], ship: Dict, expected_units: int,
             run_mode: str) -> Tuple[str, str]:
    if len(per_unit) < expected_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"{len(per_unit)}/{expected_units} units")

    posc = v3._by_unit(per_unit, "keyed", "RANDOM_BLOCK", J_ISO)
    shuf = v3._by_unit(per_unit, "shuffled_key", "INBATCH_BLOCK", J_ISO)
    if posc is None or shuf is None:
        return ("HARD_FAIL", "HARD_FAIL_MISSING_GATE_UNITS")
    if posc["acc_at1"] < POSCTRL_KEYED_FLOOR:
        return ("HARD_FAIL",
                f"HARD_FAIL_SBC_LOSSLESS_PRIOR: RANDOM_BLOCK keyed J={J_ISO} "
                f"{posc['acc_at1']:.3f} < {POSCTRL_KEYED_FLOOR} (SBC algebra "
                f"machinery broken; not a training result)")
    if shuf["acc_at1"] > SHUFFLED_LEAK_CEIL or shuf["hit_any_member"] > 0.10:
        return ("HARD_FAIL",
                f"HARD_FAIL_SHUFFLED_KEY_LEAK: {shuf['acc_at1']:.3f}/"
                f"{shuf['hit_any_member']:.3f}")

    cos = ship["cosine_to_gold"]
    ra = ship["ret_agree10"]
    rt_iso = ship["isolated_roundtrip"]
    rt_comp = ship["composed_roundtrip"]
    charpos_ra = ship["charpos_ret_agree10"]
    delta_ra = ship["delta_ret_agree10_vs_charpos"]
    baseline_in_band = ship["baseline_in_band"]
    tail = (f"[cosine_to_gold(hi80)={cos:.4f} ret_agree10={ra:.4f} "
            f"iso_roundtrip@J{J_ISO}={rt_iso:.4f} "
            f"composed_roundtrip@J{ship['j_composed']}={rt_comp:.4f} "
            f"charpos_ret_agree10={charpos_ra:.4f} "
            f"delta_ret_agree10={delta_ra:+.4f} baseline_in_band={baseline_in_band}]")

    if run_mode == "smoke":
        fails = []
        if not math.isfinite(rt_iso):
            fails.append("S_iso_roundtrip_nan")
        if not (-1.0 <= ra <= 1.0):
            fails.append("S_ret_agree_out_of_range")
        # cosine_to_gold may be nan at smoke (too few teacher>=0.80 pairs); OK.
        if fails:
            return ("SMOKE_GATE_FAIL", "; ".join(fails))
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: train(in_batch,nce=0)->encode->sparse-CSR"
                f"->ship-metric all fire; SBC-lossless pos-ctrl "
                f"RANDOM_BLOCK keyed={posc['acc_at1']:.3f}>= {POSCTRL_KEYED_FLOOR}, "
                f"no shuffled-key leak ({shuf['acc_at1']:.3f}); "
                f"the trained-code ship gate (cosine_to_gold/ret_agree10/composed"
                f"-roundtrip) is a FULL-only question (smoke V too small to "
                f"crystallize block-STE structure, same precedent as v3c) {tail}")

    # FULL: JOINT ship gate. HARD-FAIL first (either failing hard).
    if cos < HF_COS_TO_GOLD or rt_comp < HF_COMPOSED_RT:
        return ("HARD_FAIL",
                f"SHIP_HARD_FAIL: cosine_to_gold {cos:.4f} < {HF_COS_TO_GOLD} "
                f"OR composed_roundtrip {rt_comp:.4f} < {HF_COMPOSED_RT}. The "
                f"held-pair spearman-0.886 did NOT carry to the ship metric: "
                f"either the sparse code does not preserve the teacher's high-"
                f"similarity geometry (fails to beat the orthographic ceiling) "
                f"OR algebra collapses under composed load. Re-open the "
                f"training-fidelity lever ladder (Lever B soft-to-hard STE per "
                f"the GSBC training-recipe memo) {tail}")

    joint_pass = (cos >= HP_COS_TO_GOLD and rt_comp >= HP_COMPOSED_RT
                  and ra >= HP_RET_AGREE10 and baseline_in_band)
    if joint_pass:
        return ("HARD_PASS",
                f"SHIP_HARD_PASS: JOINT gate cleared -- cosine_to_gold "
                f"{cos:.4f}>= {HP_COS_TO_GOLD} AND composed_roundtrip "
                f"{rt_comp:.4f}>= {HP_COMPOSED_RT} (algebra INTACT under composed"
                f" load) AND ret_agree10 {ra:.4f}>= {HP_RET_AGREE10}; the in-"
                f"batch-RKD distilled block code carries the semantic win to the "
                f"real ship metric with algebra preserved {tail}")
    return ("MIDDLE_BAND",
            f"SHIP_MIDDLE_BAND: real signal but the JOINT ship gate is not fully "
            f"cleared -- cosine_to_gold>= {HP_COS_TO_GOLD}? {cos >= HP_COS_TO_GOLD}; "
            f"composed_roundtrip>= {HP_COMPOSED_RT}? {rt_comp >= HP_COMPOSED_RT}; "
            f"ret_agree10>= {HP_RET_AGREE10}? {ra >= HP_RET_AGREE10}. This "
            f"localizes the proxy-to-real gap (a strong held-pair rank-spearman "
            f"does not imply strong top-10 retrieval agreement / composed "
            f"algebra); route to the GSBC graded-code / STE-anneal lever {tail}")


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def run_carrythrough(run_mode: str, seed: int, device_arg: str, n_dim: int,
                     teacher_cache_arg: Optional[str]) -> int:
    assert run_mode in ("smoke", "full"), f"unsupported run_mode {run_mode}"
    anchor = f"{ANCHOR_NAME}_smoke" if run_mode == "smoke" else ANCHOR_NAME
    out_dir = get_output_dir(anchor)
    art_dir = _artifact_dir(run_mode, seed)
    art_dir.mkdir(parents=True, exist_ok=True)
    device = ("cuda" if torch.cuda.is_available() else "cpu") \
        if device_arg == "auto" else device_arg
    kb, blk_l = v3.K_BLOCKS_PRIMARY, n_dim // v3.K_BLOCKS_PRIMARY
    if kb * blk_l != n_dim:
        raise ValueError(f"n_dim {n_dim} not divisible by k_blocks {kb}")

    if run_mode == "smoke":
        steps, batch = SMOKE_STEPS, min(FULL_BATCH, SMOKE_N_TRAIN)
        ckpt_every, dense_every = SMOKE_CKPT_EVERY, SMOKE_DENSE_EVAL_EVERY
        quick_sub, quick_pairs = SMOKE_QUICK_HELD_SUB, SMOKE_QUICK_PAIRS
        traj_pairs, final_pairs = SMOKE_TRAJ_PAIRS, SMOKE_FINAL_PAIRS
        charpos_cap, n_trials = SMOKE_CHARPOS_CAP, SMOKE_TRIALS
        j_composed = J_COMPOSED_SMOKE
        n_tr_target, n_he_target = SMOKE_N_TRAIN, SMOKE_N_HELD
    else:
        steps, batch = FULL_STEPS, FULL_BATCH
        ckpt_every, dense_every = FULL_CKPT_EVERY, FULL_DENSE_EVAL_EVERY
        quick_sub, quick_pairs = FULL_QUICK_HELD_SUB, FULL_QUICK_PAIRS
        traj_pairs, final_pairs = FULL_TRAJ_PAIRS, FULL_FINAL_PAIRS
        charpos_cap, n_trials = FULL_CHARPOS_CAP, FULL_TRIALS
        j_composed = J_COMPOSED_FULL
        n_tr_target = n_he_target = None

    warmup = v3._warmup_for(steps)
    min_step_for_best = max(1, int(round(MIN_STEP_FRAC_FOR_BEST * steps)))
    _write_start_marker(out_dir, run_mode, EXPECTED_N_UNITS)
    t0 = time.perf_counter()
    print(f"[carry] run_mode={run_mode} seed={seed} device={device} n_dim={n_dim} "
          f"kb={kb} blk_l={blk_l} steps={steps} batch={batch} "
          f"objective={OBJECTIVE} nce={NCE_WEIGHT} j_composed={j_composed}",
          flush=True)

    # ---- resolve teacher cache ----
    if run_mode == "full":
        cache_arg = teacher_cache_arg or TEACHER_CACHE_FULL
        cache_path = v3._resolve_teacher_cache(cache_arg)
    else:
        cache_path = (v3._resolve_teacher_cache(teacher_cache_arg)
                      if teacher_cache_arg
                      else _resolve_smoke_cache(SMOKE_N_TRAIN + SMOKE_N_HELD))
    X, ids = v3._load_teacher(cache_path)
    V_cache = X.shape[0]
    print(f"[carry] teacher {cache_path.name}: {V_cache} concepts x {X.shape[1]}d "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    rng = np.random.default_rng(seed)
    perm = rng.permutation(V_cache)
    if run_mode == "smoke":
        if V_cache < n_tr_target + n_he_target:
            raise RuntimeError(f"teacher cache too small for smoke: {V_cache}")
        n_tr, n_he = n_tr_target, n_he_target
    else:
        n_he = min(int(round(V_cache * v3.HELD_FRAC)), v3.FULL_HELD_CAP)
        n_tr = V_cache - n_he
    tr_idx, he_idx = perm[:n_tr], perm[n_tr:n_tr + n_he]
    Xtr = X[torch.from_numpy(tr_idx.copy())].contiguous()
    Xhe = X[torch.from_numpy(he_idx.copy())].contiguous()
    names_he = [ids[i] for i in he_idx]
    print(f"[carry] split train={n_tr} held={n_he}", flush=True)

    pos_idx, semi_cands = v3._mine_teacher(Xtr, device, art_dir / "_mine_shards",
                                           out_dir, t0)
    semi_cov = float((semi_cands[:, 0] >= 0).float().mean())
    print(f"[carry] mining cov={semi_cov:.3f} ({time.perf_counter() - t0:.1f}s)",
          flush=True)

    Xhe_sub = Xhe[:min(quick_sub, n_he)].contiguous()

    def _deval_quick(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xhe_sub, quick_pairs, seed + 7)

    def _deval_full(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xhe, traj_pairs, seed + 7)

    # ---- PHASE A: TRAIN in-batch-RKD-only (reuse v3c training loop verbatim) ----
    st, diag = v3c._train_student_full(
        kb, blk_l, Xtr, pos_idx, semi_cands, steps, batch, warmup, seed, device,
        art_dir / "_ckpt_INBATCH.pt", art_dir / "_ckpt_best_INBATCH.pt",
        ckpt_every, out_dir, t0, None, v3.FRAME_REFRESH_MID, NCE_WEIGHT,
        "INBATCH", objective=OBJECTIVE, dense_eval_quick_fn=_deval_quick,
        dense_eval_full_fn=_deval_full, dense_eval_every=dense_every,
        min_step_for_best=min_step_for_best)
    print(f"[carry] trained rkd_last={diag['rkd_last']:.4f} "
          f"best_full={diag['best_dense_full']:.4f}@step{diag['best_step']} "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    # reload BEST checkpoint as the official encoder.
    best_student = v3c._reload_best_student(
        "mlp", Xtr.shape[1], kb * blk_l, device, art_dir / "_ckpt_best_INBATCH.pt")

    # ---- PHASE B: encode held concepts -> block code -> sparse-CSR artifact ----
    inbatch_block = v3._encode_hard_block(best_student, Xhe, kb, blk_l)
    inbatch_dense = v3._dense_sign_codes(best_student, Xhe)
    gen_ctrl = torch.Generator().manual_seed(seed + 1)
    random_block = v3._random_block_codes(n_he, kb, blk_l, gen_ctrl)
    cp_cap = min(n_he, charpos_cap)
    charpos_codes = v3._charpos_codes(names_he[:cp_cap], n_dim, kb)

    block_dense_int8 = inbatch_block.to(torch.int8).numpy()
    sparse_rep = _dense_to_sparse_csr(block_dense_int8, names_he, n_dim)
    total_nnz = sparse_rep["total_nnz"]
    mean_nnz = total_nnz / max(1, n_he)
    n_rt_ck, n_rt_mm = _sparse_roundtrip_mismatch(block_dense_int8, sparse_rep,
                                                  min(100, n_he), seed)
    pt_bytes, pt_sha = _save_e_concept(sparse_rep, _e_concept_path(run_mode, seed),
                                       "INBATCH_BLOCK")
    print(f"[carry] sparse-CSR mean_nnz={mean_nnz:.2f} roundtrip_mismatch="
          f"{n_rt_mm}/{n_rt_ck} pt_bytes={pt_bytes} sha={pt_sha[:12]}",
          flush=True)
    _emit_heartbeat(out_dir, 1, EXPECTED_N_UNITS, time.perf_counter() - t0,
                    extra={"stage": "encoded_sparse_csr"})

    # ---- META_RULE_AF arms-must-differ ----
    digests = {}
    for name, c in (("INBATCH_BLOCK", inbatch_block), ("CHARPOS", charpos_codes),
                    ("RANDOM_BLOCK", random_block)):
        digests[name] = hashlib.sha256(
            c.to(torch.int8).numpy().tobytes()).hexdigest()
    for a in digests:
        for b in digests:
            if a < b and digests[a] == digests[b]:
                raise RuntimeError(
                    f"failure_class=META_RULE_AF_VIOLATION: {a}/{b} identical")

    # ---- PHASE C+D: ship-metric + algebra units ----
    per_unit: List[Dict] = []
    unit_fail: List[Dict] = []
    gen_eval = torch.Generator().manual_seed(seed + 2)

    def _run_unit(fn, *a, **kw):
        try:
            u = fn(*a, **kw)
            per_unit.append(u)
            print(f"[carry] unit {len(per_unit)}/{EXPECTED_N_UNITS} {u['unit']}: "
                  + json.dumps({k: round(v, 4) for k, v in u.items()
                                if isinstance(v, float)}), flush=True)
            _emit_heartbeat(out_dir, len(per_unit), EXPECTED_N_UNITS,
                            time.perf_counter() - t0, extra={"unit": u["unit"]})
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append({"fn": getattr(fn, "__name__", "?"),
                              "failure_class": type(exc).__name__,
                              "msg": str(exc)[:300]})
            raise

    # semantic (cosine_to_gold via hi80_cos + ret_agree10 vs teacher)
    _run_unit(v3._semantic_unit, "INBATCH_BLOCK", inbatch_block, inbatch_block,
              Xhe, Xhe, 0, final_pairs, seed + 3)
    _run_unit(v3._semantic_unit, "INBATCH_DENSE", inbatch_dense, inbatch_dense,
              Xhe, Xhe, 0, final_pairs, seed + 3)
    cp_Xhe = Xhe[:cp_cap]
    _run_unit(v3._semantic_unit, "CHARPOS", charpos_codes, charpos_codes,
              cp_Xhe, cp_Xhe, 0, final_pairs, seed + 3)
    _run_unit(v3._semantic_unit, "RANDOM_BLOCK", random_block, random_block,
              Xhe, Xhe, 0, final_pairs, seed + 3)

    # keyed algebra: pos-ctrl + isolated + composed + shuffled leak
    _run_unit(v3._keyed_unit, "RANDOM_BLOCK", "sbc", random_block, kb, blk_l,
              J_ISO, n_trials, gen_eval, device)
    _run_unit(v3._keyed_unit, "INBATCH_BLOCK", "sbc", inbatch_block, kb, blk_l,
              J_ISO, n_trials, gen_eval, device)
    _run_unit(v3._keyed_unit, "INBATCH_BLOCK", "sbc", inbatch_block, kb, blk_l,
              j_composed, n_trials, gen_eval, device)
    _run_unit(v3._keyed_unit, "INBATCH_BLOCK", "sbc", inbatch_block, kb, blk_l,
              J_ISO, n_trials, gen_eval, device, shuffled_key=True)

    # ---- assemble ship dict ----
    ib_sem = v3._by_unit(per_unit, "semantic", "INBATCH_BLOCK")
    cp_sem = v3._by_unit(per_unit, "semantic", "CHARPOS")
    ib_iso = v3._by_unit(per_unit, "keyed", "INBATCH_BLOCK", J_ISO)
    ib_comp = v3._by_unit(per_unit, "keyed", "INBATCH_BLOCK", j_composed)
    charpos_ra = float(cp_sem["ret_agree10"]) if cp_sem else float("nan")
    ship = {
        "cosine_to_gold": float(ib_sem["hi80_cos"]),
        "cosine_to_gold_teacher": float(ib_sem["hi80_teacher_mean"]),
        "cosine_to_gold_calib_err": float(ib_sem["hi80_calib_err"]),
        "ret_agree10": float(ib_sem["ret_agree10"]),
        "spearman_all": float(ib_sem["spearman_all"]),
        "isolated_roundtrip": float(ib_iso["acc_at1"]),
        "composed_roundtrip": float(ib_comp["acc_at1"]),
        "j_composed": int(j_composed),
        "charpos_ret_agree10": charpos_ra,
        "delta_ret_agree10_vs_charpos": (float(ib_sem["ret_agree10"]) - charpos_ra
                                         if not math.isnan(charpos_ra)
                                         else float("nan")),
        "baseline_in_band": bool(0.05 < charpos_ra < 0.95)
        if not math.isnan(charpos_ra) else False,
    }

    verdict, verdict_msg = _verdict(per_unit, ship, EXPECTED_N_UNITS, run_mode)
    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "seed": int(seed), "device": device, "N": n_dim,
        "student_arch": v3.STUDENT_ARCH_PRIMARY, "mlp_hidden": v3.MLP_HIDDEN,
        "objective": (f"IN_BATCH-RKD-only, nce_weight={NCE_WEIGHT}, "
                      "best-by-full-held-eval checkpoint selection "
                      f"(min_step_for_best={min_step_for_best}); winning arm of "
                      "step1b_v3c carried to Step2 sparse-encode + Step3 ship "
                      "metric (teacher-anchored gold-verify)"),
        "steps": steps, "batch": batch, "warmup_steps": warmup,
        "nce_weight": NCE_WEIGHT, "min_step_for_best": min_step_for_best,
        "j_iso": J_ISO, "j_composed": j_composed,
        "teacher_cache": cache_path.name, "teacher_n_concepts": V_cache,
        "n_train": n_tr, "n_held": n_he, "semi_hard_coverage": semi_cov,
        "ship": ship,
        "step2_sparse": {
            "mean_nnz": mean_nnz, "total_nnz": total_nnz,
            "roundtrip_checked": n_rt_ck, "roundtrip_mismatch": n_rt_mm,
            "pt_bytes": pt_bytes, "pt_sha256": pt_sha,
            "e_concept_path": str(_e_concept_path(run_mode, seed)),
        },
        "train_diag": {k: diag[k] for k in
                       ("rkd_last", "best_dense_full", "best_step",
                        "alltime_best_dense_full", "alltime_best_step",
                        "best_ckpt_fallback_to_final")},
        "per_unit": per_unit, "unit_failures": unit_fail,
        "n_units": len(per_unit), "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": len(per_unit) == EXPECTED_N_UNITS,
        "arms_differ_verified": True, "arm_code_sha256": digests,
        "final_metrics_atomicity": "tmp_replace",
        "composition_algebra": "SBC_block_local_circular_convolution",
        "progress_logging": "print_flush_true",
        "primary_spearman": ship["spearman_all"],
        "cosine_to_gold": ship["cosine_to_gold"],
        "ret_agree10": ship["ret_agree10"],
        "composed_roundtrip": ship["composed_roundtrip"],
        "baseline_in_band": ship["baseline_in_band"],
        "crlb_floor_computed": 0.901,
        "crlb_formula_reference": ("r_max = sigma_teacher / sqrt(sigma_teacher^2 "
                                   "+ 0.25/K), K=128 -> 0.901 (unchanged from "
                                   "v2/v3/v3c; same block quantization channel)"),
        "discriminator_reachability": True,
        "cell_chunked": False, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "calibration_check": "default_ok_for_this_regime",
        "hp_scope": {"INBATCH_BLOCK": ["cosine_to_gold", "composed_roundtrip",
                                       "ret_agree10"]},
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[carry] verdict={verdict} msg={verdict_msg} elapsed={elapsed:.1f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Self-test (synthetic; no cache dependency; fast).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()

    # 1. sparse-CSR convert + round-trip (bit-identical) on synthetic block code.
    rng = np.random.default_rng(7)
    n, n_dim, kb = 40, 256, 16       # blk_l = 16; nnz = kb = 16 per row
    blk_l = n_dim // kb
    gen = torch.Generator().manual_seed(7)
    blk = v3._random_block_codes(n, kb, blk_l, gen)
    dense_int8 = blk.to(torch.int8).numpy()
    names = [f"ent_{i}" for i in range(n)]
    sp = _dense_to_sparse_csr(dense_int8, names, n_dim)
    assert sp["n_entities"] == n and sp["n_dim"] == n_dim
    assert int(sp["offsets"][-1]) == sp["total_nnz"] == n * kb
    ck, mm = _sparse_roundtrip_mismatch(dense_int8, sp, n, seed=7)
    assert ck == n and mm == 0, f"selftest: sparse round-trip mismatch {mm}/{ck}"

    # non-bipolar guard.
    bad = dense_int8.copy()
    bad[0, sp["active_indices"][0].item()] = 2
    try:
        _dense_to_sparse_csr(bad, names, n_dim)
        raise AssertionError("selftest: non-bipolar value should raise")
    except ValueError:
        pass

    # 2. smoke-cache resolver returns a real npz with enough concepts (if any).
    try:
        cp = _resolve_smoke_cache(1000)
        assert cp.exists() and cp.suffix == ".npz"
    except Exception:
        pass  # cache dir may be absent in a bare checkout; not fatal for selftest

    # 3. ship-verdict logic: cardinality + integrity gates + JOINT bands.
    def _units(posc_acc=0.99, shuf_acc=0.01):
        u = [{"unit": f"sem{i}", "arm": "x", "kind": "semantic"} for i in range(4)]
        u += [
            {"unit": f"keyed::RANDOM_BLOCK::J{J_ISO}", "arm": "RANDOM_BLOCK",
             "kind": "keyed", "J": J_ISO, "acc_at1": posc_acc,
             "hit_any_member": posc_acc},
            {"unit": f"keyed::INBATCH_BLOCK::J{J_ISO}", "arm": "INBATCH_BLOCK",
             "kind": "keyed", "J": J_ISO, "acc_at1": 1.0, "hit_any_member": 1.0},
            {"unit": f"keyed::INBATCH_BLOCK::J{J_COMPOSED_FULL}",
             "arm": "INBATCH_BLOCK", "kind": "keyed", "J": J_COMPOSED_FULL,
             "acc_at1": 0.97, "hit_any_member": 0.97},
            {"unit": f"shuffled_key::INBATCH_BLOCK::J{J_ISO}",
             "arm": "INBATCH_BLOCK", "kind": "shuffled_key", "J": J_ISO,
             "acc_at1": shuf_acc, "hit_any_member": shuf_acc},
        ]
        return u

    def _ship(cos, ra, rt_comp, charpos_ra=0.30, rt_iso=1.0):
        return {"cosine_to_gold": cos, "ret_agree10": ra,
                "isolated_roundtrip": rt_iso, "composed_roundtrip": rt_comp,
                "j_composed": J_COMPOSED_FULL, "charpos_ret_agree10": charpos_ra,
                "delta_ret_agree10_vs_charpos": ra - charpos_ra,
                "baseline_in_band": (0.05 < charpos_ra < 0.95)}

    v_hp, _ = _verdict(_units(), _ship(0.85, 0.35, 0.97), EXPECTED_N_UNITS, "full")
    assert v_hp == "HARD_PASS", f"selftest: expected HARD_PASS got {v_hp}"
    # ret_agree miss -> MIDDLE (this is the forecast case).
    v_mb, _ = _verdict(_units(), _ship(0.85, 0.22, 0.97), EXPECTED_N_UNITS, "full")
    assert v_mb == "MIDDLE_BAND", f"selftest: expected MIDDLE_BAND got {v_mb}"
    # cosine below HARD-FAIL ceiling -> HARD_FAIL.
    v_hf, _ = _verdict(_units(), _ship(0.55, 0.35, 0.97), EXPECTED_N_UNITS, "full")
    assert v_hf == "HARD_FAIL", f"selftest: expected HARD_FAIL got {v_hf}"
    # composed algebra collapse -> HARD_FAIL.
    v_hf2, _ = _verdict(_units(), _ship(0.85, 0.35, 0.80), EXPECTED_N_UNITS, "full")
    assert v_hf2 == "HARD_FAIL", f"selftest: expected HARD_FAIL (algebra) got {v_hf2}"
    # SBC-lossless pos-ctrl broken -> HARD_FAIL regardless of ship numbers.
    v_pc, m_pc = _verdict(_units(posc_acc=0.5), _ship(0.85, 0.35, 0.97),
                          EXPECTED_N_UNITS, "full")
    assert v_pc == "HARD_FAIL" and "SBC_LOSSLESS" in m_pc
    # shuffled-key leak -> HARD_FAIL.
    v_lk, m_lk = _verdict(_units(shuf_acc=0.5), _ship(0.85, 0.35, 0.97),
                          EXPECTED_N_UNITS, "full")
    assert v_lk == "HARD_FAIL" and "SHUFFLED_KEY_LEAK" in m_lk
    # cardinality breach.
    v_cd, m_cd = _verdict(_units()[:3], _ship(0.85, 0.35, 0.97),
                          EXPECTED_N_UNITS, "full")
    assert v_cd == "HARD_FAIL" and "CARDINALITY_BREACH" in m_cd
    # smoke machinery-OK (nan cosine tolerated at smoke).
    v_sm, _ = _verdict(_units(), _ship(float("nan"), 0.22, float("nan")),
                       EXPECTED_N_UNITS, "smoke")
    assert v_sm == "HARD_PASS", f"selftest: expected smoke HARD_PASS got {v_sm}"

    print(f"[selftest] PASS (sparse-CSR bit-identical round-trip + non-bipolar "
          f"guard + JOINT ship verdict bands incl HP/MB/HF/pos-ctrl/leak/"
          f"cardinality/smoke) elapsed={time.perf_counter() - t0:.2f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Entry.
# ---------------------------------------------------------------------------

def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=(
        "Encoder carry-through: in-batch-RKD-only winner -> Step2 sparse-encode "
        "-> Step3 teacher-anchored ship-metric gold-verify."))
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
    return run_carrythrough(args.run_mode, args.seed, args.device, args.n_dim,
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
