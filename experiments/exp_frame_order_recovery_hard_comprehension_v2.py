# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (occupancy_baseline order-pred vs content_frame order-pred are
#     hash-distinct per seed; role-partitioned codebook distinct from a random codebook; frame samples vary).
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb / capacity-feasibility: order recovery in the CLEAN single-filler regime is deterministic-1.0 by
#     self-correlation dominance (each role's exact filler self-correlates at k while any cross-partition
#     cone-neighbor scores < k) -- THEORETICAL. The correlation-stressed quantities that CAN fail are (a) the
#     DECODE at scale (cited cliff blocklocal_gsbc@V8192D26 exact_ordered=0.856 per_token=0.9945) and (b) the
#     SUPERPOSITION separation (2 co-located correlated fillers separated by partition-restricted argmax).
#     crlb_n_a declared: no closed-form noise floor for the assignment step; the decode ceiling is CITED.
# - baseline_in_band: occupancy_baseline ORDER-recovery MUST collapse to chance 1/D! (stressor bites). This is
#     a STRUCTURAL guarantee: per-block occupancy energy is provably INVARIANT to role-permutation within a
#     fixed occupied set (bias_audit proves energy(frame)==energy(role_swapped_frame) exactly).
# - discriminator survives scale: decode + order measured AT full N=8192 in ALL modes (smoke reduces trials
#     and seeds only, never N and never the block geometry). Discriminator gates FIRE in smoke.
# - HARD_PASS strictly above floor (order_content >= 0.75 [chance 0.167], superposition_survival >= 0.50,
#     decode_at_scale_cited >= 0.60; order_occupancy <= 0.32 near-chance BIAS gate; gap >= 0.45).
# - HP_SCOPE: chain-grade HARD_PASS gates apply ONLY to content_frame (the mechanism). occupancy_baseline is
#     a negative control expected AT chance on ORDER. decode_at_scale_posctrl carries ONLY the pos-ctrl floor.
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
#
# FRAME-ORDER-RECOVERY  --  hard-comprehension order-recovery from a superposition   v2
# =================================================================================================
# v2 = DECODE-REGIME FIX of v1's REGIME_POSCTRL_FAIL (the mechanism was SOUND; the positive control was
#      decoded in the WRONG block-size regime and floored below its own gate).
#
# WHAT v1 GOT RIGHT (UNCHANGED in v2 -- the order-recovery mechanism is sound):
#   content_frame ORDER recovery = 1.000  MEASURED@data/exp_frame_order_recovery_hard_comprehension_v1/metrics.json:arms.content_frame.order_recovery_mean
#   occupancy_baseline ORDER     = 0.192  MEASURED@.../v1/metrics.json:arms.occupancy_baseline.order_recovery_mean (chance 1/D!=0.167)
#   real-vs-control ORDER gap    = 0.808  (content recovers role->block ORDER that occupancy provably cannot)
#   SUPERPOSITION parse survival = 0.783  MEASURED@.../v1/metrics.json:arms.content_frame.superposition_survival_mean
#   partition-restricted decode  = 0.983  MEASURED@.../v1/metrics.json:arms.decode_at_scale_posctrl.partition_restricted_true_frame_mean
#   => the mechanism's OWN decode operating point (role-typed / partition-restricted) is ROBUST at scale.
#
# WHAT v1 GOT WRONG (the REGIME_POSCTRL_FAIL -- a test-harness bug, NOT a capability gap):
#   The full-codebook DECODE positive control (whose PURPOSE is to reproduce the CITED hard cliff
#   blocklocal_gsbc@V8192D26 exact_ordered=0.856) was measured in the ORDER-mechanism's block geometry:
#     v1 decoded the posctrl at bs = N_DIM // B_TOTAL = 8192 // 32 = 256  (k = round(0.02*256) = 5 active).
#   But the CITED cliff was measured at the cited cell's block size:
#     CITED@experiments/exp_generation_decoder_gsbc_native_blocklocal_v1.py:517  bs = N_DIM // D = 8192 // 26 = 315
#     (k = round(0.02*315) = 6 active), D disjoint blocks, full-codebook argmax  ->  exact_ordered = 0.856.
#   bs=256 is SMALLER + sparser than the cited bs=315: per-token decode margin drops (0.970 vs 0.994), and
#   compounded across D=26 the frame-exact decode COLLAPSES to ~0.48-0.52 with enormous seed variance.
#     v1 posctrl (bs=256): full_codebook_true_frame_mean = 0.525  per_seed=[0.575,0.25,0.75] (CV~0.5)
#       MEASURED@.../v1/metrics.json:arms.decode_at_scale_posctrl.full_codebook_true_frame_mean  -> < 0.60 floor -> FAIL
#   Diagnostic recompute (SAME fillers, 3 seeds, 40 trials, this cell's helpers):
#     bs=256 (v1 regime):  full_frame_exact mean=0.483 per_seed=[0.375,0.25,0.825]  per_token=0.970   MEASURED@scratch_diag
#     bs=315 (cited regime): full_frame_exact mean=0.867 per_seed=[0.9,0.875,0.825]  per_token=0.9949 MEASURED@scratch_diag
#     V=8192 bs=315 (cited exact): full_frame_exact mean=0.850 per_token=0.9936 (reproduces CITED 0.856/0.9945)
#
# THE v2 FIX (surgical; DECODE regime only; the order-recovery mechanism is UNTOUCHED):
#   The positive control now reproduces the cited cliff AT THE CITED REGIME: it decodes each true-frame filler
#   in its OWN disjoint block of size bs_cited = N_DIM // D (matching exp_generation_decoder..._blocklocal),
#   full-codebook argmax, using the SAME sampled GSBC concepts. Expected ~0.85 (>= 0.60 floor). The v1
#   razor-edge bs=N//B_TOTAL number is STILL REPORTED (cellbs_full_codebook_*, informational -- nothing
#   hidden) so the block-size sensitivity is documented, not buried. A pos-ctrl CV guard (<= 0.20) rejects a
#   razor-edge control (v1 bs=256 CV~0.5) from ever clearing the floor by seed luck.
#   The ORDER-recovery arms (content_frame vs occupancy_baseline), their B_TOTAL=32 / bs=256 geometry, the
#   partition-restricted decode the mechanism actually uses, and the gap discriminator are BIT-FOR-BIT the
#   v1 design.
#
# MECHANISM (brain-grounded; Helmholtz recognition+generation; thematic-role selectional restrictions):
#   content_frame: for each recognized-occupied block b and role r, score s[r][b] = max over v in role r's
#     vocab partition of corr(block_b_content, cb[v]); assign role r -> argmax_b s[r][b]; decode each role by
#     partition-restricted per-block argmax. Reads CONTENT-TYPE, which occupancy energy is blind to.
#   occupancy_baseline (negative control): recognize the SET, then -- having NO order info -- assign roles by a
#     random consistent permutation. ORDER-recovery collapses to 1/D! by construction.
#
# METRIC (report SEPARATELY per Fix #28 -- never collapse to one aggregate):
#   set_recognition_acc           = P[ recognized occupied SET == true SET ]              (both arms; ~1.0)
#   order_recovery_acc            = P[ recovered role->block ASSIGNMENT == true ]         (content vs occupancy)
#   superposition_survival        = P[ full parse (order AND all fillers) | >1 filler/block ] (content)
#   decode_at_scale_cited         = P[ full-codebook decode | true frame ] at bs=N//D (CITED-cliff posctrl)  <-- v2 GATE
#   decode_at_scale_cellbs        = P[ full-codebook decode | true frame ] at bs=N//B_TOTAL (razor-edge; info)
#   decode_at_scale_partition     = P[ partition-restricted decode | true frame ] (mechanism's actual decode)
#
# Reuses (native GSBC filler pool + block-local sparse construction; do NOT rerun the cited ceilings):
#   experiments/exp_generation_decoder_gsbc_native_blocklocal_v1.py  (native GSBC block-local decoder; bs=N//D)
#   data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz          (native GSBC filler pool; untracked --
#       SCP to remote before FULL dispatch; queue_add does NOT auto-ship it)
#
# ASCII-only. CPU default (matched-filter + block-argmax; numpy only; no LLM, no GPU). Read-only.
# Run: python experiments/exp_frame_order_recovery_hard_comprehension_v2.py [--self-test | --smoke]
#      (bare / runner-injected HDLAB_RUN_MODE=full -> full)

# KB_REFERENT: data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz

from __future__ import annotations

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

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)  # 17. PRINT-PROGRESS flush on newline

DEVICE = "cpu"  # matched-filter + block-argmax; numpy only (no torch needed)

ANCHOR_NAME = "frame_order_recovery_hard_comprehension_v2"
REPO = Path(__file__).resolve().parents[1]

N_DIM = 8192          # substrate compositional default == cited regime (all modes; never reduced)
GSBC_DIM = 8192       # GSBC_EXPAND2X output dim
K_ACTIVE = 192        # GSBC_EXPAND2X global top-K (metadata)
F_SPARSE = 0.02       # block-local code sparsity fraction (proven-cell F_SPARSE=0.02)
POOL_PATH = REPO / "data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz"

BL_PROJ_SEED = 5000       # per-seed block-local GSBC projection base seed (matches cited cell)

SEEDS = (7, 13, 19, 23, 29)   # FULL: 5 seeds (v2 raises v1's 3 seeds for a robust cited-regime posctrl + gap)

# Pre-registered bands (HARD-PASS / HARD-FAIL). Default tier MIDDLE (let cert-owner tier up).
# HYPOTHESIZED@this-prereg unless a MEASURED@ tag is given; verified against smoke before FULL.
#   HARD-PASS: order_content >= 0.75 AND order_occupancy <= 0.32 AND gap >= 0.45 AND
#              superposition_survival >= 0.50 AND decode_at_scale_cited >= 0.60, cv <= 0.15, >= 5 seeds.
#   HARD-FAIL: order_content <= 0.25 (~chance -> occupancy-degeneracy confirmed; comprehension needs a
#              different mechanism).
#   MIDDLE:    set works (~1.0) but superposition_survival OR decode_at_scale_cited below the HP floor.
HP_ORDER = 0.75            # HARD_PASS: content_frame order-recovery (chance 1/D! = 0.167 at D=3)
HP_SUPERPOSE = 0.50        # HARD_PASS: content_frame superposition parse survival
HP_DECODE_SCALE = 0.60     # HARD_PASS: CITED-regime full-codebook decode at bs=N//D (cited 0.856)
HF_ORDER = 0.25            # HARD_FAIL: order-recovery no better than chance
ORDER_OCC_MAX = 0.32       # BIAS gate: occupancy order-recovery MUST be near chance 1/D!=0.167 (+0.15 margin)
ORDER_GAP_MIN = 0.45       # discriminator: content order-recovery - occupancy order-recovery must exceed
POS_CTRL_DECODE_FLOOR = 0.60  # Gate D: CITED-regime full-codebook decode reproduces the cited cliff (bs=N//D)
POS_CTRL_CV_MAX = 0.20     # Gate D stability guard: reject a razor-edge posctrl (v1 bs=256 had CV~0.5)
CV_MAX = 0.15              # HARD_PASS: cv of order_content across seeds

ARMS = ["content_frame", "occupancy_baseline"]

# Conditions: bs = N_DIM / B_TOTAL. "injective" = one filler per occupied block (order is a permutation of a
# D-subset). "superpose" = D roles into B_OCC < D occupied blocks (>1 filler per block).
CONDITIONS = {
    "order":     {"B_TOTAL": 8,  "D": 3,  "V_ROLE": 1024, "mode": "injective", "B_OCC": 3},
    "superpose": {"B_TOTAL": 8,  "D": 4,  "V_ROLE": 1024, "mode": "superpose", "B_OCC": 2},
    "scale":     {"B_TOTAL": 32, "D": 26, "V_ROLE": 300,  "mode": "injective", "B_OCC": 26},
}


# ============================================================
# Defensive error-checking helpers (13/16)
# ============================================================


def _out_dir() -> Path:
    name = os.environ.get("HDLAB_EXP_NAME")
    return REPO / (f"data/exp_{name}" if name else f"data/exp_{ANCHOR_NAME}")


def _say(msg: str) -> None:
    print(msg, flush=True)


def _write_start_marker(output_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, output_dir / "_start_marker.json")


def _heartbeat(output_dir: Path, unit_idx: int, total_units: int, t0: float, extra=None) -> None:
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": unit_idx,
        "total_units": total_units,
        "elapsed_s": round(time.perf_counter() - t0, 2),
    }
    if extra:
        row["extra"] = extra
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_metrics_atomic(output_dir: Path, metrics: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, output_dir / "metrics.json")  # atomic (META_RULE_AH)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "anchor_name": ANCHOR_NAME,
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
    }
    _write_metrics_atomic(output_dir, diag)


def _digest_arr(arr) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(arr, dtype=np.float64)).tobytes()).hexdigest()


# ============================================================
# Native GSBC filler pool (reused from the cited cell) + block-local codebook
# ============================================================


_POOL = {"nz_idx": None, "nz_val": None, "n": 0, "meta": None}


def _load_pool() -> dict:
    if _POOL["nz_idx"] is None:
        if not POOL_PATH.exists():
            raise FileNotFoundError(
                f"GSBC native filler pool missing: {POOL_PATH}. It is an untracked npz -- SCP it to the "
                f"remote (queue_add does NOT auto-ship it).")
        d = np.load(POOL_PATH)
        _POOL["nz_idx"] = d["nz_idx"].astype(np.int64)
        _POOL["nz_val"] = d["nz_val"].astype(np.float32)
        _POOL["n"] = int(_POOL["nz_idx"].shape[0])
        _POOL["meta"] = json.loads(str(d["meta_json"]))
    return _POOL


def _gsbc_dense(rows: np.ndarray) -> np.ndarray:
    """Reconstruct dense native GSBC codes for the given pool rows. (len(rows), GSBC_DIM) float32."""
    p = _load_pool()
    ni, nv = p["nz_idx"], p["nz_val"]
    out = np.zeros((len(rows), GSBC_DIM), dtype=np.float32)
    for i, r in enumerate(rows):
        out[i, ni[r]] = nv[r]
    return out


def _blocklocal_codebook_gsbc(gsbc_codes: np.ndarray, bs: int, seed: int) -> np.ndarray:
    """Native GSBC filler codebook: project each concept's GSBC code GSBC_DIM->bs (JL-preserves the real
    cos-cone), keep top-(F_SPARSE*bs) magnitude, sign -> sparse bipolar (V, bs). GLOBAL codebook."""
    V = gsbc_codes.shape[0]
    k = max(1, int(round(F_SPARSE * bs)))
    g = np.random.default_rng(BL_PROJ_SEED + seed)
    P = (g.standard_normal((GSBC_DIM, bs)).astype(np.float32) / np.sqrt(GSBC_DIM))
    Y = gsbc_codes @ P                                           # (V, bs) real, correlated (GSBC cone)
    idx = np.argpartition(-np.abs(Y), k - 1, axis=1)[:, :k]      # top-k magnitude per row
    cb = np.zeros((V, bs), dtype=np.float32)
    rows = np.arange(V)[:, None]
    cb[rows, idx] = np.where(Y[rows, idx] >= 0.0, 1.0, -1.0)
    return cb


# ============================================================
# Frame sampling (an ASSIGNMENT role -> block; SET and ORDER are separate DOF) + compose
# ============================================================


def _sample_props(cfg: dict, trials: int, seed: int):
    """Return (list of tok tuples, list of role2block tuples). Each role d draws a filler from its OWN
    disjoint vocab partition [d*V_ROLE, (d+1)*V_ROLE). role2block encodes SET (which blocks) AND ORDER
    (which role in which block); occupancy energy is invariant to the ORDER within a fixed SET."""
    D, V_ROLE, B_TOTAL, B_OCC = cfg["D"], cfg["V_ROLE"], cfg["B_TOTAL"], cfg["B_OCC"]
    rng = np.random.default_rng(90000 + seed)
    props, frames = [], []
    for _ in range(trials):
        toks = tuple(int(d * V_ROLE + rng.integers(0, V_ROLE)) for d in range(D))
        occ = sorted(int(b) for b in rng.choice(B_TOTAL, size=B_OCC, replace=False))  # the occupied SET
        if cfg["mode"] == "injective":            # D == B_OCC: a permutation assignment of the D-subset
            perm = rng.permutation(occ)
            role2block = tuple(int(b) for b in perm)
        else:                                     # superpose: D roles -> B_OCC blocks, every block used once+
            assign = list(occ) + [int(rng.choice(occ)) for _ in range(D - B_OCC)]
            rng.shuffle(assign)
            role2block = tuple(int(b) for b in assign)
        props.append(toks)
        frames.append(role2block)
    return props, frames


def _compose(toks, role2block, cb: np.ndarray, bs: int, B_TOTAL: int) -> np.ndarray:
    comp = np.zeros(B_TOTAL * bs, dtype=np.float32)
    for d, b in enumerate(role2block):
        comp[b * bs:(b + 1) * bs] += cb[toks[d]]     # superposed when two roles share a block (sum)
    return comp


def _block_energy(comp: np.ndarray, bs: int, B_TOTAL: int) -> np.ndarray:
    seg = comp.reshape(B_TOTAL, bs)
    return np.einsum("bd,bd->b", seg, seg)           # per-block L2 energy (B_TOTAL,)


# ============================================================
# content_frame mechanism + occupancy_baseline (PAIRED)
# ============================================================


def _recognize_set(energy: np.ndarray, B_OCC: int) -> list:
    """Top-B_OCC energy blocks == recognized occupied SET (the easy, occupancy-robust part)."""
    return sorted(int(b) for b in np.argpartition(-energy, B_OCC - 1)[:B_OCC])


def _content_order_and_decode(comp, cb, bs, D, V_ROLE, occ_blocks, part_argmax_only=True):
    """Role-typed matched filter. corr[j] = cb @ block_content(occ_blocks[j]). For role r, score over its
    partition; assign role r -> occ block with max partition-score; decode role r by partition-restricted
    argmax at its assigned block. Returns (order_pred tuple, tokens_pred tuple)."""
    segs = comp.reshape(-1, bs)[occ_blocks]                       # (n_occ, bs)
    corr = cb @ segs.T                                           # (V, n_occ)
    order_pred = [0] * D
    tok_pred = [0] * D
    for r in range(D):
        sl = slice(r * V_ROLE, (r + 1) * V_ROLE)
        part = corr[sl]                                         # (V_ROLE, n_occ)
        j = int(np.argmax(part.max(axis=0)))                   # occ-block index with best role-r evidence
        order_pred[r] = int(occ_blocks[j])
        tok_pred[r] = int(r * V_ROLE + int(np.argmax(part[:, j])))
    return tuple(order_pred), tuple(tok_pred)


def _decode_given_frame(comp, cb, bs, D, V_ROLE, role2block, full_codebook):
    """Block-local per-role decode GIVEN the true frame, in the ORDER-mechanism's own composition (bs=N//
    B_TOTAL). full_codebook=True -> argmax over the FULL global codebook (cross-partition confusable, razor-
    edge at this cell's small block size). full_codebook=False -> partition-restricted argmax (the decode the
    content mechanism actually uses; robust)."""
    tok_pred = [0] * D
    seg = comp.reshape(-1, bs)
    for d, b in enumerate(role2block):
        c = cb @ seg[b]                                        # (V,)
        if full_codebook:
            tok_pred[d] = int(np.argmax(c))
        else:
            sl = slice(d * V_ROLE, (d + 1) * V_ROLE)
            tok_pred[d] = int(d * V_ROLE + int(np.argmax(c[sl])))
    return tuple(tok_pred)


def _decode_cited_regime(toks, cb_cited, bs_cited, D):
    """POSITIVE CONTROL (v2 fix): reproduce the cited hard cliff at the CITED regime. Place each true-frame
    filler in its OWN disjoint block of size bs_cited = N_DIM // D (matching
    CITED@exp_generation_decoder_gsbc_native_blocklocal_v1:517 bs = N_DIM // D), full-codebook argmax per
    block. Returns predicted token tuple. This is the decode geometry the cited 0.856 was measured in --
    v1 mistakenly decoded the posctrl at the ORDER mechanism's bs = N_DIM // B_TOTAL = 256."""
    comp = np.zeros(D * bs_cited, dtype=np.float32)
    for d, t in enumerate(toks):
        comp[d * bs_cited:(d + 1) * bs_cited] += cb_cited[t]
    seg = comp.reshape(D, bs_cited)
    return tuple(int(np.argmax(cb_cited @ seg[d])) for d in range(D))


def run_condition(cname: str, cfg: dict, seed: int, trials: int) -> dict:
    D, V_ROLE, B_TOTAL, B_OCC = cfg["D"], cfg["V_ROLE"], cfg["B_TOTAL"], cfg["B_OCC"]
    bs = N_DIM // B_TOTAL
    bs_cited = N_DIM // D                # cited-cliff decode regime (posctrl); matches the cited cell's bs
    V = D * V_ROLE
    props, frames = _sample_props(cfg, trials, seed)

    samp = np.random.default_rng(91000 + seed).choice(_load_pool()["n"], size=V, replace=False)
    gc = _gsbc_dense(samp)
    cb = _blocklocal_codebook_gsbc(gc, bs, seed)              # ORDER mechanism codebook (bs = N//B_TOTAL)
    cb_cited = _blocklocal_codebook_gsbc(gc, bs_cited, seed)  # posctrl codebook (SAME concepts, bs = N//D)

    orng = np.random.default_rng(70000 + seed)  # occupancy random-assignment rng (its best guess sans order)

    set_hits = 0
    oc_hits = 0            # content_frame order-recovery
    op_hits = 0           # occupancy_baseline order-recovery
    parse_c = 0           # content parse (order AND all fillers)
    parse_o = 0           # occupancy parse
    dec_scale_full = 0    # full-codebook decode GIVEN true frame, at CELL bs=N//B_TOTAL (razor-edge; info)
    dec_scale_part = 0    # partition-restricted decode GIVEN true frame (mechanism's actual decode)
    dec_scale_cited = 0   # full-codebook decode GIVEN true frame, at CITED bs=N//D (posctrl; v2 GATE)
    op_digest = []
    oc_digest = []

    for toks, r2b in zip(props, frames):
        comp = _compose(toks, r2b, cb, bs, B_TOTAL)
        energy = _block_energy(comp, bs, B_TOTAL)
        true_set = sorted(set(r2b))
        rec_set = _recognize_set(energy, len(true_set))
        set_ok = (rec_set == true_set)
        set_hits += int(set_ok)

        # --- content_frame (PRIMARY): role-typed matched filter over recognized set ---
        c_order, c_tok = _content_order_and_decode(comp, cb, bs, D, V_ROLE, rec_set)
        oc_ok = (c_order == r2b)
        oc_hits += int(oc_ok)
        parse_c += int(oc_ok and c_tok == toks)
        oc_digest.append(c_order)

        # --- occupancy_baseline (negative control): recognize set, then random order assignment ---
        if cfg["mode"] == "injective":
            o_order = tuple(int(b) for b in orng.permutation(rec_set))
        else:  # respect recognized per-block load from energy; assign roles to blocks randomly within load
            k_bs = max(1, int(round(F_SPARSE * bs)))
            loads = [max(1, int(round(float(energy[b]) / k_bs))) for b in rec_set]
            slots = []
            for b, ld in zip(rec_set, loads):
                slots += [b] * ld
            while len(slots) < D:
                slots.append(int(orng.choice(rec_set)))
            slots = slots[:D]
            orng.shuffle(slots)
            o_order = tuple(int(b) for b in slots)
        op_ok = (o_order == r2b)
        op_hits += int(op_ok)
        o_tok = _decode_given_frame(comp, cb, bs, D, V_ROLE, o_order, full_codebook=False)
        parse_o += int(op_ok and o_tok == toks)
        op_digest.append(o_order)

        # --- decode-at-scale ceilings GIVEN the true frame (positive controls) ---
        t_full = _decode_given_frame(comp, cb, bs, D, V_ROLE, r2b, full_codebook=True)   # razor-edge (info)
        t_part = _decode_given_frame(comp, cb, bs, D, V_ROLE, r2b, full_codebook=False)  # mechanism decode
        t_cited = _decode_cited_regime(toks, cb_cited, bs_cited, D)                       # CITED posctrl (GATE)
        dec_scale_full += int(t_full == toks)
        dec_scale_part += int(t_part == toks)
        dec_scale_cited += int(t_cited == toks)

    n = float(trials)
    return {
        "condition": cname, "D": D, "V_ROLE": V_ROLE, "B_TOTAL": B_TOTAL, "bs": bs, "bs_cited": bs_cited,
        "B_OCC": B_OCC,
        "chance_order": (1.0 / math.factorial(D)) if cfg["mode"] == "injective" else None,
        "set_recognition": set_hits / n,
        "order_content": oc_hits / n,
        "order_occupancy": op_hits / n,
        "parse_content": parse_c / n,
        "parse_occupancy": parse_o / n,
        "decode_scale_full": dec_scale_full / n,        # cell bs=N//B_TOTAL (razor-edge; informational)
        "decode_scale_part": dec_scale_part / n,        # partition-restricted (mechanism's actual decode)
        "decode_scale_cited": dec_scale_cited / n,      # CITED bs=N//D (positive control; v2 GATE)
        "digest_content_order": _digest_arr(np.array([b for t in oc_digest for b in t], dtype=np.float64)),
        "digest_occupancy_order": _digest_arr(np.array([b for t in op_digest for b in t], dtype=np.float64)),
        "cb_digest": _digest_arr(cb),
    }


# ============================================================
# BIAS audit: prove occupancy energy is INVARIANT to role-order (the stressor bites BY CONSTRUCTION)
# ============================================================


def bias_audit(seed: int = 7) -> dict:
    """Structural proof that per-block occupancy energy is degenerate for ORDER: compose a frame and its
    role-swapped variant (same SET, swapped ORDER) and verify per-block energy is bit-identical. Also
    verify vocab partitions are disjoint + non-empty."""
    cfg = CONDITIONS["order"]
    D, V_ROLE, B_TOTAL, B_OCC = cfg["D"], cfg["V_ROLE"], cfg["B_TOTAL"], cfg["B_OCC"]
    bs = N_DIM // B_TOTAL
    V = D * V_ROLE
    samp = np.random.default_rng(91000 + seed).choice(_load_pool()["n"], size=V, replace=False)
    cb = _blocklocal_codebook_gsbc(_gsbc_dense(samp), bs, seed)
    rng = np.random.default_rng(4242)
    toks = tuple(int(d * V_ROLE + rng.integers(0, V_ROLE)) for d in range(D))
    occ = sorted(int(b) for b in rng.choice(B_TOTAL, size=B_OCC, replace=False))
    fa = tuple(occ)                     # role d -> occ[d]
    fb = (occ[1], occ[0], occ[2])       # swap roles 0 and 1 (same SET, different ORDER)
    ea = _block_energy(_compose(toks, fa, cb, bs, B_TOTAL), bs, B_TOTAL)
    eb = _block_energy(_compose(toks, fb, cb, bs, B_TOTAL), bs, B_TOTAL)
    energy_invariant = bool(np.array_equal(ea, eb))          # occupancy CANNOT see the role swap
    frames_differ = (fa != fb)
    # partition disjointness (by construction contiguous, disjoint, non-empty)
    parts_ok = (V_ROLE >= 1) and (D >= 2)
    return {
        "energy_invariant_under_role_swap": energy_invariant,   # TRUE == occupancy degenerate for order
        "frames_differ_under_role_swap": bool(frames_differ),
        "partitions_disjoint_nonempty": bool(parts_ok),
        "chance_order_D3": round(1.0 / math.factorial(D), 4),
        "occupancy_degenerate_for_order": bool(energy_invariant and frames_differ),
    }


# ============================================================
# Config + verdict
# ============================================================


def get_config(mode: str):
    if mode == "selftest":
        return {"trials": 4, "seeds": (7,),
                "conds": {
                    "order":     {"B_TOTAL": 8,  "D": 3, "V_ROLE": 64, "mode": "injective", "B_OCC": 3},
                    "superpose": {"B_TOTAL": 8,  "D": 4, "V_ROLE": 64, "mode": "superpose", "B_OCC": 2},
                    "scale":     {"B_TOTAL": 32, "D": 6, "V_ROLE": 40, "mode": "injective", "B_OCC": 6}}}
    if mode == "smoke":
        return {"trials": 20, "seeds": (7,), "conds": CONDITIONS}     # full geometry (N, bs, D); fires discrim
    return {"trials": 40, "seeds": SEEDS, "conds": CONDITIONS}        # FULL: 5 seeds


def _cv(vals):
    a = np.asarray(vals, dtype=np.float64)
    m = float(a.mean())
    return float(a.std() / m) if m > 0.0 else float("inf")


def classify(mode, audit, agg, n_units, exp_units):
    if n_units < exp_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: {n_units}/{exp_units} units")

    order_c = agg["order"]["order_content_mean"]
    order_o = agg["order"]["order_occupancy_mean"]
    set_c = agg["order"]["set_recognition_mean"]
    gap = order_c - order_o
    superpose = agg["superpose"]["parse_content_mean"]
    dec_cited = agg["scale"]["decode_scale_cited_mean"]        # v2 GATE (bs=N//D, cited-cliff reproduction)
    dec_cited_cv = agg["scale"]["decode_scale_cited_cv"]
    dec_cellbs = agg["scale"]["decode_scale_full_mean"]        # v1 razor-edge (bs=N//B_TOTAL); informational
    dec_part = agg["scale"]["decode_scale_part_mean"]          # mechanism's actual decode
    order_cv = agg["order"]["order_content_cv"]
    chance = agg["order"]["chance_order"]

    diag = (f"set_recognition={set_c:.3f}; ORDER content={order_c:.3f} vs occupancy={order_o:.3f} "
            f"(chance 1/D!={chance:.3f}); gap={gap:.3f}; SUPERPOSITION parse={superpose:.3f}; "
            f"DECODE@scale cited-regime(bs=N//D,true-frame)={dec_cited:.3f} cv={dec_cited_cv:.3f} "
            f"(cited V8192D26=0.856); cellbs(bs=N//B_TOTAL) razor-edge={dec_cellbs:.3f}; "
            f"partition-restricted(mechanism)={dec_part:.3f}; scale content parse="
            f"{agg['scale']['parse_content_mean']:.3f}")

    # BIAS: occupancy energy must be provably invariant to role-order (stressor bites by construction)
    if not audit["occupancy_degenerate_for_order"]:
        return ("BLOCK_DISPATCH_BIAS_DEGENERATE",
                f"occupancy energy NOT invariant to role swap (energy_invariant="
                f"{audit['energy_invariant_under_role_swap']}): the ORDER stressor does not bite. {diag}")

    # BIAS: occupancy order-recovery must be near chance (empirical confirmation the stressor bites)
    if order_o > ORDER_OCC_MAX:
        return ("BLOCK_DISPATCH_BIAS_OCC_NOT_AT_CHANCE",
                f"occupancy_baseline order-recovery={order_o:.3f} > {ORDER_OCC_MAX} (chance {chance:.3f}): "
                f"occupancy is recovering order it should not -> degenerate test. {diag}")

    # Gate D: CITED-regime full-codebook decode reproduces the cited hard cliff at bs=N//D (all modes)
    if dec_cited < POS_CTRL_DECODE_FLOOR:
        return ("REGIME_POSCTRL_FAIL",
                f"decode_at_scale cited-regime(bs=N//D)={dec_cited:.3f} < {POS_CTRL_DECODE_FLOOR}: block-local "
                f"decode does NOT reproduce the cited cliff at the cited regime; fix decode before trusting "
                f"order. {diag}")
    # Gate D stability: reject a razor-edge posctrl (v1 bs=256 CV~0.5 cleared only by seed luck)
    if dec_cited_cv > POS_CTRL_CV_MAX:
        return ("REGIME_POSCTRL_UNSTABLE",
                f"decode_at_scale cited-regime cv={dec_cited_cv:.3f} > {POS_CTRL_CV_MAX}: posctrl is razor-edge "
                f"(seed-luck dependent), not a stable cliff reproduction. {diag}")

    # Discriminator FIRES: content recovers order that occupancy cannot (paired)
    if gap < ORDER_GAP_MIN:
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"order content-vs-occupancy gap={gap:.3f} < {ORDER_GAP_MIN}: content did not out-recover "
                f"occupancy on ORDER -> order signal not attributable to the content mechanism. {diag}")

    if mode == "smoke":
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: order+superposition+scale run end-to-end AT N={N_DIM}; the content-vs-"
                f"occupancy ORDER discriminator fires (gap={gap:.3f}); occupancy is at chance ({order_o:.3f}); "
                f"the CITED-regime decode reproduces the cited cliff ({dec_cited:.3f} at bs=N//D); BIAS proves "
                f"occupancy order-degeneracy. The pre-registered comprehension band is FULL-only "
                f"(canonical = remote multi-seed). {diag}")

    # --- FULL pre-registered bands ---
    if order_c <= HF_ORDER:
        return ("HARD_FAIL",
                f"comprehension wall: order_content={order_c:.3f} (HF<= {HF_ORDER}, chance {chance:.3f}) -> "
                f"occupancy-degeneracy CONFIRMED and the content mechanism cannot beat it; comprehension of "
                f"ORDER needs a different mechanism than role-typed matched filtering. {diag}")
    if (order_c >= HP_ORDER and order_o <= ORDER_OCC_MAX and gap >= ORDER_GAP_MIN
            and superpose >= HP_SUPERPOSE and dec_cited >= HP_DECODE_SCALE and order_cv <= CV_MAX):
        return ("HARD_PASS",
                f"COMPREHENSION HOLDS AT THE HARD REGIME: role->block ORDER recovered at {order_c:.3f} "
                f"(>> chance {chance:.3f}; occupancy stuck at {order_o:.3f}); full parse SURVIVES "
                f"SUPERPOSITION at {superpose:.3f} (>= {HP_SUPERPOSE}); DECODE holds at the cited scale regime "
                f"{dec_cited:.3f} (>= {HP_DECODE_SCALE}; cited cliff 0.856). Occupancy is provably order-blind; "
                f"content-conditioned role typing recovers the permutation on REAL correlated GSBC fillers. {diag}")
    return ("MIDDLE_BAND",
            f"partial comprehension: SET recognized ({set_c:.3f}) and ORDER clearly above chance "
            f"({order_c:.3f} vs occupancy {order_o:.3f}), but superposition_survival={superpose:.3f} "
            f"(HP {HP_SUPERPOSE}) and/or decode_at_scale_cited={dec_cited:.3f} (HP {HP_DECODE_SCALE}) below "
            f"floor: order works, superposition/scale partial. {diag}")


# ============================================================
# Driver
# ============================================================


def run_all(mode: str, output_dir: Path, t0: float):
    cfg = get_config(mode)
    trials, seeds, conds = cfg["trials"], cfg["seeds"], cfg["conds"]
    per_unit = []                                  # cardinality ledger: one record per (seed, condition)
    total_units = len(seeds) * len(conds)
    unit = 0
    for seed in seeds:
        for cname, ccfg in conds.items():
            r = run_condition(cname, ccfg, seed, trials)
            per_unit.append({"seed": seed, **r})
            unit += 1
            _heartbeat(output_dir, unit, total_units, t0,
                       extra={"seed": seed, "cond": cname, "order_content": round(r["order_content"], 3),
                              "order_occupancy": round(r["order_occupancy"], 3),
                              "parse_content": round(r["parse_content"], 3),
                              "decode_scale_cited": round(r["decode_scale_cited"], 3),
                              "decode_scale_cellbs": round(r["decode_scale_full"], 3)})
            _say(f"  [seed {seed}][{cname}] set={r['set_recognition']:.3f} "
                 f"order_content={r['order_content']:.3f} order_occupancy={r['order_occupancy']:.3f} "
                 f"parse_content={r['parse_content']:.3f} decode_cited={r['decode_scale_cited']:.3f} "
                 f"decode_cellbs={r['decode_scale_full']:.3f} decode_part={r['decode_scale_part']:.3f}")
    return cfg, per_unit, total_units


def _agg(per_unit, cname):
    rows = [u for u in per_unit if u["condition"] == cname]
    def col(k):
        return [u[k] for u in rows]
    return {
        "set_recognition_mean": round(float(np.mean(col("set_recognition"))), 4),
        "set_recognition_per_seed": [round(x, 4) for x in col("set_recognition")],
        "order_content_mean": round(float(np.mean(col("order_content"))), 4),
        "order_content_per_seed": [round(x, 4) for x in col("order_content")],
        "order_content_cv": round(_cv(col("order_content")), 4) if len(rows) > 1 else 0.0,
        "order_occupancy_mean": round(float(np.mean(col("order_occupancy"))), 4),
        "order_occupancy_per_seed": [round(x, 4) for x in col("order_occupancy")],
        "parse_content_mean": round(float(np.mean(col("parse_content"))), 4),
        "parse_content_per_seed": [round(x, 4) for x in col("parse_content")],
        "parse_occupancy_mean": round(float(np.mean(col("parse_occupancy"))), 4),
        "decode_scale_full_mean": round(float(np.mean(col("decode_scale_full"))), 4),
        "decode_scale_full_per_seed": [round(x, 4) for x in col("decode_scale_full")],
        "decode_scale_part_mean": round(float(np.mean(col("decode_scale_part"))), 4),
        "decode_scale_cited_mean": round(float(np.mean(col("decode_scale_cited"))), 4),
        "decode_scale_cited_per_seed": [round(x, 4) for x in col("decode_scale_cited")],
        "decode_scale_cited_cv": round(_cv(col("decode_scale_cited")), 4) if len(rows) > 1 else 0.0,
        "bs_cited": rows[0]["bs_cited"],
        "chance_order": rows[0]["chance_order"],
    }


def _run(mode: str) -> int:
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    cfg = get_config(mode)
    exp_units = len(cfg["seeds"]) * len(cfg["conds"])
    _write_start_marker(output_dir, mode, exp_units)
    _say(f"[{ANCHOR_NAME}] mode={mode} N={N_DIM} trials={cfg['trials']} seeds={cfg['seeds']} "
         f"conditions={list(cfg['conds'].keys())} expected_units={exp_units}")

    audit = bias_audit()
    _say(f"[{ANCHOR_NAME}] BIAS audit: {audit}")

    cfg, per_unit, total_units = run_all(mode, output_dir, t0)
    agg = {c: _agg(per_unit, c) for c in cfg["conds"].keys()}

    # arms_differ (META_RULE_AF): content order-pred vs occupancy order-pred must be hash-distinct per unit.
    arms_differ_ok = True
    for u in per_unit:
        if u["digest_content_order"] == u["digest_occupancy_order"]:
            arms_differ_ok = False
    if not arms_differ_ok:
        raise AssertionError("META_RULE_AF VIOLATION: content and occupancy order-predictions bit-identical")

    verdict, vmsg = classify(mode, audit, agg, len(per_unit), exp_units)
    elapsed = time.perf_counter() - t0

    arms = {
        "content_frame": {
            "order_recovery_mean": agg["order"]["order_content_mean"],
            "order_recovery_per_seed": agg["order"]["order_content_per_seed"],
            "order_recovery_cv": agg["order"]["order_content_cv"],
            "superposition_survival_mean": agg["superpose"]["parse_content_mean"],
            "superposition_survival_per_seed": agg["superpose"]["parse_content_per_seed"],
            "decode_at_scale_parse_mean": agg["scale"]["parse_content_mean"],
            "set_recognition_mean": agg["order"]["set_recognition_mean"],
        },
        "occupancy_baseline": {
            "order_recovery_mean": agg["order"]["order_occupancy_mean"],
            "order_recovery_per_seed": agg["order"]["order_occupancy_per_seed"],
            "chance_order": agg["order"]["chance_order"],
            "superposition_parse_mean": agg["superpose"]["parse_occupancy_mean"],
            "set_recognition_mean": agg["order"]["set_recognition_mean"],
        },
        "decode_at_scale_posctrl": {
            # v2 GATE: cited-regime reproduction (bs = N//D), the geometry the cited 0.856 was measured in
            "cited_regime_true_frame_mean": agg["scale"]["decode_scale_cited_mean"],
            "cited_regime_true_frame_per_seed": agg["scale"]["decode_scale_cited_per_seed"],
            "cited_regime_true_frame_cv": agg["scale"]["decode_scale_cited_cv"],
            "cited_regime_bs": agg["scale"]["bs_cited"],
            # INFORMATIONAL: the v1 razor-edge number at the ORDER-mechanism's own block size (bs = N//B_TOTAL)
            "cellbs_full_codebook_true_frame_mean": agg["scale"]["decode_scale_full_mean"],
            "cellbs_full_codebook_true_frame_per_seed": agg["scale"]["decode_scale_full_per_seed"],
            "cellbs_bs": N_DIM // CONDITIONS["scale"]["B_TOTAL"],
            # mechanism's actual decode operating point (partition-restricted; robust)
            "partition_restricted_true_frame_mean": agg["scale"]["decode_scale_part_mean"],
            "cited_V8192D26_exact_ordered": 0.856,
        },
    }

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: frame ORDER-recovery hard comprehension v2 (decode-regime posctrl fix) ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": len(cfg["seeds"]),
        "n_units": len(per_unit),
        "expected_n_units": exp_units,
        "cardinality_ok": len(per_unit) >= exp_units,
        "arms_differ_verified": arms_differ_ok,
        "config": {
            "N": N_DIM, "GSBC_DIM": GSBC_DIM, "K_ACTIVE": K_ACTIVE, "F_SPARSE": F_SPARSE,
            "trials": cfg["trials"], "seeds": list(cfg["seeds"]), "conditions": cfg["conds"],
            "classifier": "role_typed_matched_filter_over_partition_restricted_correlation",
            "frame_def": "assignment_role_to_block_set_and_order_are_separate_DOF",
            "posctrl_decode_regime": "cited_bs_N_over_D_disjoint_blocks_full_codebook_argmax",
            "native_filler": "GSBC_EXPAND2X_seed7_FULL_projected_sparse_bipolar", "pool_meta": _load_pool()["meta"],
        },
        "arms": arms,
        "per_condition": agg,
        "per_unit": per_unit,
        "bias_audit": audit,
        "bands": {"HP_order": HP_ORDER, "HP_superpose": HP_SUPERPOSE, "HP_decode_scale": HP_DECODE_SCALE,
                  "HF_order": HF_ORDER, "order_occ_max": ORDER_OCC_MAX, "order_gap_min": ORDER_GAP_MIN,
                  "pos_ctrl_decode_floor": POS_CTRL_DECODE_FLOOR, "pos_ctrl_cv_max": POS_CTRL_CV_MAX,
                  "cv_max": CV_MAX},
        "hp_scope": {"content_frame": ["HP_order", "HP_superpose", "HP_decode_scale", "order_gap_min", "cv_max"],
                     "occupancy_baseline": ["order_occ_max_near_chance_BIAS_gate"],
                     "decode_at_scale_posctrl": ["pos_ctrl_decode_floor", "pos_ctrl_cv_max"]},
        "cited_baselines": {
            "prior_trivial_set_only": "data/exp_frame_classify_then_known_decode_v1:sparse_block.parse_mean=1.0 (SET only)",
            "decode_hard_cliff": "data/exp_generation_decoder_gsbc_native_blocklocal_v1:blocklocal_gsbc@V8192D26=0.856 (bs=N//D)",
            "v1_posctrl_regime_fail": "data/exp_frame_order_recovery_hard_comprehension_v1:decode 0.525 at bs=N//B_TOTAL=256 (wrong regime)",
        },
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
    }
    _write_metrics_atomic(output_dir, metrics)
    written = json.load(open(output_dir / "metrics.json"))
    assert written["run_mode"] == mode, f"RUN_MODE_MISMATCH {written['run_mode']} != {mode}"

    _say(f"\n[{ANCHOR_NAME}] {verdict}: {vmsg}")
    _say(f"[{ANCHOR_NAME}] metrics -> {output_dir / 'metrics.json'}  elapsed={elapsed:.1f}s")
    return 0


def _run_selftest() -> int:
    t0 = time.perf_counter()
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    cfg = get_config("selftest")
    audit = bias_audit()
    conds = cfg["conds"]
    order_r = run_condition("order", conds["order"], 7, cfg["trials"])
    sup_r = run_condition("superpose", conds["superpose"], 7, cfg["trials"])
    scale_r = run_condition("scale", conds["scale"], 7, cfg["trials"])
    gap = order_r["order_content"] - order_r["order_occupancy"]
    # invariants: (a) occupancy order-degeneracy proven; (b) content recovers order (self-corr dominance);
    # (c) occupancy near chance; (d) gap large; (e) set recognized; (f) CITED-regime scale decode works.
    ok = (audit["occupancy_degenerate_for_order"]
          and order_r["order_content"] >= 0.90
          and order_r["order_occupancy"] <= (order_r["chance_order"] + 0.30)
          and gap >= 0.40
          and order_r["set_recognition"] >= 0.99
          and scale_r["decode_scale_cited"] >= 0.50)
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: degenerate_for_order="
         f"{audit['occupancy_degenerate_for_order']} order_content={order_r['order_content']:.3f} "
         f"order_occupancy={order_r['order_occupancy']:.3f} gap={gap:.3f} set={order_r['set_recognition']:.3f} "
         f"superpose_parse={sup_r['parse_content']:.3f} decode_cited={scale_r['decode_scale_cited']:.3f} "
         f"decode_cellbs={scale_r['decode_scale_full']:.3f} [{time.perf_counter()-t0:.1f}s]")
    return 0 if ok else 1


def main() -> int:
    if "--self-test" in sys.argv:
        return _run_selftest()
    mode = "smoke" if "--smoke" in sys.argv else \
        ("smoke" if os.environ.get("HDLAB_RUN_MODE", "").lower() == "smoke" else "full")
    return _run(mode)


if __name__ == "__main__":
    _od = None
    try:
        _od = _out_dir()
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        if _od is not None:
            _write_crash_metrics(_od, e)
        raise
