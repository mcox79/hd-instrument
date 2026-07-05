# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (cb_gsbc vs dense_lex codebooks hash-distinct; sparse vs dense
#     composites hash-distinct; frame templates pairwise-distinct BIAS audit).
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb/capacity-feasibility: block-local sparse resonator is exact-by-construction on disjoint blocks
#     (per-block V-way argmax cleanup; no cross-slot interference within a frame -> each used block holds
#     exactly ONE filler). Frame-classification via occupancy is deterministic set-matching (no argmax-noise
#     floor). crlb_n_a declared: the decode has no superposition noise within a block; the correlation
#     stress is the cross-code overlap in the per-block cleanup (measured by known_frame_posctrl). CITED
#     proven ceiling: blocklocal_gsbc@V1024D3 exact=1.000, @V8192D26 exact=0.856 per_token=0.9945.
# - baseline_in_band: dense_ctrl frame_class MUST collapse toward chance (1/F); sparse_block frame_class is
#     occupancy-robust-by-construction and expected HIGH (this is the MECHANISM, made explicit + audited,
#     NOT a hidden saturation). The correlation-stressed discriminator that CAN fail is the DECODE (parse).
# - discriminator survives scale: decode measured AT full N=8192 in ALL modes (smoke reduces trials/seeds/F
#     only, never N and never the anchor V=1024). Discriminator gates FIRE in smoke:
#       (1) sparse_frame_class - dense_frame_class >= FRAME_GAP_MIN  (occupancy carries frame ONLY under
#           sparse-block geometry; dense collapses -> paired negative control fires);
#       (2) known_frame_posctrl decode >= POS_CTRL_DECODE_FLOOR  (Gate D: block-local decode reproduces the
#           cited ceiling AT the test regime bs=1024/k=20/V=1024).
# - HARD_PASS strictly above floor (frame_class >= 0.90 [HF 0.40], parse >= 0.75 [HF 0.15], cv <= 0.05).
# - HP_SCOPE: chain-grade HARD_PASS gates apply ONLY to sparse_block. dense_ctrl is a negative control
#     expected AT chance (exempt). known_frame_posctrl carries the POS_CTRL_DECODE_FLOOR gate only.
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
#
# FRAME-CLASSIFY-THEN-KNOWN-DECODE  --  first COMPREHENSION primitive (parse an UNKNOWN bound proposition
# into role-filler structure with NO external position cue given)  v1
# =================================================================================================
# Research: notes/research_frontier_drill_comprehension_parse_unknown_structure_2026-07-05.md
#           notes/research_comprehension_frame_classify_then_decode_experiment_proposal_2026-07-05.md
#
# GAP CLOSED: frame-UNKNOWN blind factorization has only ever been tried with the DENSE multiply-bind
# algebra -> exact_ordered = 0.000 twice
#   CITED@data/exp_generation_decoder_roundtrip_v1/metrics.json:arms.real_fullreso_hi.exact_ordered_mean = 0.000
#   CITED@data/exp_generation_decoder_gsbc_native_blocklocal_v1/metrics.json:arms['dense_gsbc_fullreso@V1024D3'].exact_ordered_mean = 0.000
# The frame-KNOWN block-local decode is a HARD_PASS ceiling (position handed in at decode)
#   CITED@data/exp_generation_decoder_gsbc_native_blocklocal_v1/metrics.json:arms['blocklocal_gsbc@V1024D3'].exact_ordered_mean = 1.000
#   CITED@...:arms['blocklocal_gsbc@V8192D26'].exact_ordered_mean = 0.856  per_token 0.9945 (real-at-scale)
# NEVER TESTED: can the FRAME be RECOVERED (which role went to which block) from the bound vector ALONE,
# on REAL correlated GSBC fillers, with the sparse-block geometry -- i.e. classify-then-decode comprehension.
#
# MECHANISM (brain-grounded; Helmholtz-machine recognition+generation split; Hickok-Poeppel dual-stream):
#   (1) FRAME-RECOGNITION step: a cheap NON-learned matched-filter over the per-block OCCUPANCY signature
#       (per-block L2 energy read directly off the bound vector). A "frame" = a distinct block-to-role
#       assignment (here: a distinct D-subset of B_TOTAL blocks; role d -> the d-th block of the subset).
#       Occupancy = which blocks carry energy. Predicted frame = argmax over F candidate templates of
#       (signature . template). This exposes STRUCTURE that the dense algebra ENTANGLES.
#   (2) GENERATION/DECODE step: feed the predicted frame into the ALREADY-PROVEN block-local decoder
#       (per-block argmax over the global GSBC codebook). This is the "mouth" reused as the synthesis half.
#
# WHY frame-classification is expected HIGH and is HONEST (not a hidden saturation): for these sparse
# codes each used block holds exactly ONE filler with k active +/-1 entries -> per-block energy = k
# (constant), independent of filler identity. So occupancy carries frame identity ROBUSTLY to real filler
# correlation. That is the FINDING (sparse-block makes structure inspectable), and it is PROVEN load-bearing
# by the live dense_ctrl negative control: bind the SAME real fillers with the DENSE algebra and per-block
# energy is ~uniform -> occupancy carries NO frame info -> frame_class collapses to chance. The
# correlation-stressed quantity that CAN fail is the DECODE: with V=1024 correlated GSBC codes projected to
# bs=1024 (k~20 active), cross-code overlap in the per-block cleanup could confound -> parse drops. That is
# the genuine risk (research MIDDLE/HARD-FAIL band). HARD-FAIL is reachable via decode collapse.
#
# METRIC (report SEPARATELY per Fix #28 -- never collapse to one aggregate):
#   frame_classification_accuracy = mean[ frame_pred == frame_true ]
#   conditional_decode_accuracy   = mean over {frame_pred==frame_true} of [ exact_ordered_decode == 1 ]
#   parse_accuracy (chained)      = mean[ frame_pred == frame_true AND exact_ordered_decode == 1 ]
#
# ARMS (PAIRED -- same propositions + same true frames across arms, per feedback_paired_trials_mandatory):
#   sparse_block         (PRIMARY, new): occupancy matched-filter classify + block-local decode.
#   dense_ctrl           (negative control, live): SAME fillers, DENSE binding; occupancy classify ONLY
#                        (decode collapse is CITED 0.000, not rerun). Expected frame_class ~ chance 1/F.
#   known_frame_posctrl  (positive control, Gate D): block-local decode with the TRUE frame given (no
#                        classification) -> reproduces the cited ceiling AT the test regime.
#
# Reuses (CITED@ / do NOT rerun the dense blind resonator or the known-frame ceiling -- those are on disk):
#   experiments/exp_generation_decoder_gsbc_native_blocklocal_v1.py  (native GSBC block-local decoder; pool)
#   experiments/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000.py  (block-local resonator ancestor)
#   data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz  (native GSBC filler pool; untracked -- SCP to
#       remote before FULL dispatch; queue_add does NOT auto-ship it)
#
# ASCII-only. CPU default (matched-filter classifier is not a trained net; no LLM, no GPU). Read-only.
# Run: python experiments/exp_frame_classify_then_known_decode_v1.py [--self-test | --smoke]
#      (bare / runner-injected HDLAB_RUN_MODE=full -> full)

from __future__ import annotations

import hashlib
import itertools
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

ANCHOR_NAME = "frame_classify_then_known_decode_v1"
REPO = Path(__file__).resolve().parents[1]

N_DIM = 8192          # substrate compositional default == cited regime (all modes; never reduced)
GSBC_DIM = 8192       # GSBC_EXPAND2X output dim
K_ACTIVE = 192        # GSBC_EXPAND2X global top-K (metadata)
F_SPARSE = 0.02       # block-local code sparsity fraction (proven-cell F_SPARSE=0.02)
POOL_PATH = REPO / "data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz"

B_TOTAL = 8           # candidate block inventory (bs = N/B_TOTAL = 1024 clean; C(8,3)=56 distinct frames)
D_ROLES = 3           # roles per proposition (anchor D=3, matching cited anchor)
ANCHOR_V = 1024       # vocabulary (anchor V=1024, matching cited anchor; kept in smoke -- decode difficulty)

FRAME_SET_SEED = 424242   # fixed frame inventory (a stable "grammar"); content varies per trial-seed
BL_PROJ_SEED = 5000       # per-seed block-local GSBC projection base seed (matches cited cell)
DENSE_PROJ_SEED = 770077  # fixed GSBC_DIM->N projection for the dense negative-control fillers
POS_SEED = 1234           # dense position/role codebook seed

SEEDS = (7, 13, 19)

# Pre-registered bands -- LIFTED VERBATIM from the research note (HARD-PASS / HARD-FAIL):
#   HARD-PASS: frame_classification_accuracy >= 0.90 (F=8-16) AND chained parse_accuracy >= 0.75,
#              cv <= 0.05, >= 3 seeds.
#   HARD-FAIL: frame_classification_accuracy <= 0.40 OR parse_accuracy <= 0.15.
# Default tier MIDDLE (let cert-owner tier up). HYPOTHESIZED@prereg -- verified against smoke before FULL.
HP_FRAME_CLASS = 0.90    # HARD_PASS: sparse_block frame-classification accuracy (F candidate frames)
HP_PARSE = 0.75          # HARD_PASS: sparse_block chained parse accuracy
HF_FRAME_CLASS = 0.40    # HARD_FAIL: frame-classification no better than useless
HF_PARSE = 0.15          # HARD_FAIL: parse no meaningfully better than the dense 0.000 floor
CV_MAX = 0.05            # HARD_PASS: cv of parse across seeds
POS_CTRL_DECODE_FLOOR = 0.90  # Gate D: known-frame block-local decode reproduces the cited ceiling at regime
FRAME_GAP_MIN = 0.50     # discriminator: sparse_frame_class - dense_frame_class must exceed this (fires)

ARMS = ["sparse_block", "dense_ctrl", "known_frame_posctrl"]


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
    return hashlib.sha256(np.ascontiguousarray(np.asarray(arr, dtype=np.float32)).tobytes()).hexdigest()


# ============================================================
# Native GSBC filler pool (bounded, pre-encoded offline; sparse cache) -- reused from the cited cell
# ============================================================


_POOL = {"nz_idx": None, "nz_val": None, "n": 0, "meta": None}


def _load_pool() -> dict:
    if _POOL["nz_idx"] is None:
        if not POOL_PATH.exists():
            raise FileNotFoundError(
                f"GSBC native filler pool missing: {POOL_PATH}. It is an untracked npz -- SCP it to the "
                f"remote (queue_add does NOT auto-ship it). Generated offline from the GSBC_EXPAND2X seed7 "
                f"FULL student (bounded 10000-concept probe).")
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


# ============================================================
# Block-local sparse codebook (GSBC-native; reused construction from the cited cell)
# ============================================================


def _blocklocal_codebook_gsbc(gsbc_codes: np.ndarray, bs: int, seed: int) -> np.ndarray:
    """Native GSBC filler codebook: project each concept's GSBC code GSBC_DIM->bs (JL-preserves the real
    cos-cone), keep top-(F_SPARSE*bs) magnitude, sign -> sparse bipolar (V, bs). GLOBAL codebook (one code
    per concept); the block (position) is applied at compose-time by writing into block b."""
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


def make_dense_bipolar_gsbc(rows: np.ndarray, N: int) -> np.ndarray:
    """Native GSBC concepts as DENSE bipolar (randproj GSBC_DIM->N, sign) -- carries the GSBC cone but with
    FULL support (the dense algebra). (V, N) bipolar float32. Used ONLY by the dense negative control."""
    gc = _gsbc_dense(rows)
    pr = np.random.default_rng(DENSE_PROJ_SEED)
    P = (pr.standard_normal((GSBC_DIM, N)).astype(np.float32) / np.sqrt(GSBC_DIM))
    B = np.where(gc @ P >= 0.0, 1.0, -1.0).astype(np.float32)
    del P
    return B


def make_positions(P: int, N: int, seed: int) -> np.ndarray:
    """Roll-indexed dense bipolar position/role codebook pos[k]=roll(base,k). (P, N) bipolar float32."""
    g = np.random.default_rng(seed)
    base = (g.integers(0, 2, size=N).astype(np.float32) * 2.0 - 1.0)
    return np.stack([np.roll(base, k) for k in range(P)], axis=0)


# ============================================================
# Frames + occupancy classifier + block-local decode
# ============================================================


def make_frames(B_total: int, D: int, F: int, seed: int = FRAME_SET_SEED):
    """F distinct block-to-role assignments. A frame = a distinct sorted D-subset of the B_total blocks;
    role d -> the d-th smallest block of the subset. Returns (frames list of D-tuples, templates (F,B_total)
    binary occupancy indicators)."""
    combos = list(itertools.combinations(range(B_total), D))
    if len(combos) < F:
        raise ValueError(f"C({B_total},{D})={len(combos)} < F={F}: not enough distinct frames")
    g = np.random.default_rng(seed)
    pick = sorted(g.choice(len(combos), size=F, replace=False).tolist())
    frames = [tuple(int(b) for b in combos[i]) for i in pick]
    templates = np.zeros((F, B_total), dtype=np.float64)
    for f, fr in enumerate(frames):
        for b in fr:
            templates[f, b] = 1.0
    return frames, templates


def _occupancy(comp: np.ndarray, bs: int, B_total: int) -> np.ndarray:
    """Per-block L2 energy signature read directly off the bound vector. (B_total,) float64."""
    sig = np.empty(B_total, dtype=np.float64)
    for b in range(B_total):
        seg = comp[b * bs:(b + 1) * bs]
        sig[b] = float(np.dot(seg, seg))
    return sig


def _classify_frame(sig: np.ndarray, templates: np.ndarray) -> int:
    """Non-learned matched filter: predicted frame = argmax_f (signature . template_f)."""
    return int(np.argmax(templates @ sig))


def _compose_sparse(toks, frame, cb: np.ndarray, bs: int, N: int) -> np.ndarray:
    comp = np.zeros(N, dtype=np.float32)
    for d, b in enumerate(frame):
        comp[b * bs:(b + 1) * bs] += cb[toks[d]]     # each used block holds exactly one filler (injection)
    return comp


def _decode_given_frame(comp: np.ndarray, frame, cb: np.ndarray, bs: int):
    """Block-local per-block argmax cleanup over the global codebook (position IS the block index)."""
    rec = []
    for d, b in enumerate(frame):
        seg = comp[b * bs:(b + 1) * bs]
        rec.append(int(np.argmax(cb @ seg)))
    return rec


def _compose_dense(toks, frame, dense_lex: np.ndarray, pos: np.ndarray) -> np.ndarray:
    N = pos.shape[1]
    comp = np.zeros(N, dtype=np.float32)
    for d, b in enumerate(frame):
        comp += pos[b] * dense_lex[toks[d]]           # dense role-filler bind (full support -> occupancy flat)
    return comp


def _sample_props(V: int, D: int, trials: int, seed: int):
    rng = np.random.default_rng(90000 + seed)
    props = [[int(x) for x in rng.choice(V, size=D, replace=False)] for _ in range(trials)]
    true_frames = [int(rng.integers(0, _F_FOR_SEED)) for _ in range(trials)]
    return props, true_frames


_F_FOR_SEED = None  # set per-run in run_all (F candidate count)


# ============================================================
# Per-seed arm execution (PAIRED: same props + true frames for all arms)
# ============================================================


def run_seed(seed: int, V: int, D: int, F: int, bs: int, trials: int,
             frames, templates) -> dict:
    props, true_frames = _sample_props(V, D, trials, seed)

    # codebooks
    samp = np.random.default_rng(91000 + seed).choice(_load_pool()["n"], size=V, replace=False)
    gc = _gsbc_dense(samp)
    cb_gsbc = _blocklocal_codebook_gsbc(gc, bs, seed)
    dense_lex = make_dense_bipolar_gsbc(samp, N_DIM)
    pos = make_positions(B_TOTAL, N_DIM, POS_SEED + seed)

    fc_hits = pc_hits = 0             # sparse_block: frame-class + chained parse
    cond_hits = cond_den = 0          # sparse_block: conditional decode (given frame correct)
    dfc_hits = 0                      # dense_ctrl: frame-class
    kf_hits = 0                       # known_frame_posctrl: decode with TRUE frame given
    samp_sparse_comp = samp_dense_comp = None

    for toks, tf in zip(props, true_frames):
        frame_true = frames[tf]

        # --- sparse_block (PRIMARY): occupancy classify + block-local decode ---
        comp_s = _compose_sparse(toks, frame_true, cb_gsbc, bs, N_DIM)
        if samp_sparse_comp is None:
            samp_sparse_comp = comp_s.copy()
        sig_s = _occupancy(comp_s, bs, B_TOTAL)
        pred = _classify_frame(sig_s, templates)
        fc_ok = (pred == tf)
        fc_hits += int(fc_ok)
        rec = _decode_given_frame(comp_s, frames[pred], cb_gsbc, bs)
        exact = (rec == list(toks))
        pc_hits += int(fc_ok and exact)
        if fc_ok:
            cond_den += 1
            cond_hits += int(exact)

        # --- dense_ctrl (negative control): SAME fillers, dense binding; occupancy classify only ---
        comp_d = _compose_dense(toks, frame_true, dense_lex, pos)
        if samp_dense_comp is None:
            samp_dense_comp = comp_d.copy()
        sig_d = _occupancy(comp_d, bs, B_TOTAL)
        dfc_hits += int(_classify_frame(sig_d, templates) == tf)

        # --- known_frame_posctrl (Gate D): block-local decode with TRUE frame given ---
        rec_kf = _decode_given_frame(comp_s, frame_true, cb_gsbc, bs)
        kf_hits += int(rec_kf == list(toks))

    n = float(trials)
    return {
        "frame_class": fc_hits / n,
        "parse": pc_hits / n,
        "cond_decode": (cond_hits / cond_den) if cond_den else 0.0,
        "cond_decode_den": cond_den,
        "dense_frame_class": dfc_hits / n,
        "posctrl_decode": kf_hits / n,
        "digests": {"cb_gsbc": _digest_arr(cb_gsbc), "dense_lex": _digest_arr(dense_lex),
                    "comp_sparse": _digest_arr(samp_sparse_comp), "comp_dense": _digest_arr(samp_dense_comp)},
    }


# ============================================================
# BIAS-13 / BIAS-S regime audit (frame-classifier signal is NON-degenerate)
# ============================================================


def bias_audit(frames, templates, F: int, B_total: int) -> dict:
    distinct = {tuple(int(x) for x in t.tolist()) for t in templates}
    n_distinct = len(distinct)
    min_ham = None
    for i in range(F):
        for j in range(i + 1, F):
            h = int(np.sum(templates[i] != templates[j]))
            min_ham = h if (min_ham is None or h < min_ham) else min_ham
    usage = templates.sum(axis=0)                      # per-block usage count across frames
    any_block_all = bool((usage >= F).any())           # a block used by ALL frames = uninformative-constant
    # per-block usage entropy (bits): 0 => degenerate/uniform-uninformative
    ent = 0.0
    for b in range(B_total):
        p = usage[b] / F
        if 0.0 < p < 1.0:
            ent += -(p * math.log2(p) + (1 - p) * math.log2(1 - p))
    non_degenerate = (n_distinct == F) and (min_ham is not None and min_ham >= 1) and (not any_block_all)
    return {
        "n_frames": F, "n_distinct_templates": n_distinct,
        "min_pairwise_template_hamming": min_ham,
        "block_usage_counts": [int(x) for x in usage.tolist()],
        "any_block_used_by_all_frames": any_block_all,
        "block_usage_entropy_bits": round(ent, 4),
        "non_degenerate": bool(non_degenerate),
    }


# ============================================================
# Config + verdict
# ============================================================


def get_config(mode: str):
    if mode == "selftest":
        return {"V": 64, "F": 8, "trials": 5, "seeds": (7,)}
    if mode == "smoke":
        return {"V": ANCHOR_V, "F": 8, "trials": 8, "seeds": (7,)}      # N + anchor V kept; fires discriminators
    return {"V": ANCHOR_V, "F": 16, "trials": 30, "seeds": SEEDS}       # FULL: F=16, 3 seeds


def _cv(vals):
    a = np.asarray(vals, dtype=np.float64)
    m = float(a.mean())
    if m <= 0.0:
        return float("inf")
    return float(a.std() / m)


def classify(mode, audit, sparse_fc, sparse_parse, sparse_cond, dense_fc, posctrl, n_units, exp_units):
    if n_units < exp_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: {n_units}/{exp_units} units")
    fc_m = float(np.mean(sparse_fc))
    parse_m = float(np.mean(sparse_parse))
    cond_m = float(np.mean(sparse_cond))
    dense_m = float(np.mean(dense_fc))
    pc_m = float(np.mean(posctrl))
    gap = fc_m - dense_m
    diag = (f"sparse_block frame_class={fc_m:.3f} parse={parse_m:.3f} cond_decode={cond_m:.3f}; "
            f"dense_ctrl frame_class={dense_m:.3f} (chance~{1.0/audit['n_frames']:.3f}); gap={gap:.3f}; "
            f"known_frame_posctrl decode={pc_m:.3f}; CITED dense blind decode=0.000 "
            f"(data/exp_generation_decoder_gsbc_native_blocklocal_v1:dense_gsbc_fullreso@V1024D3)")

    # BIAS audit hard gate (all modes)
    if not audit["non_degenerate"]:
        return ("BLOCK_DISPATCH_BIAS_DEGENERATE",
                f"frame templates degenerate (n_distinct={audit['n_distinct_templates']}/{audit['n_frames']}, "
                f"min_ham={audit['min_pairwise_template_hamming']}, block_used_by_all="
                f"{audit['any_block_used_by_all_frames']}): occupancy signal is not a valid classifier basis. {diag}")

    # Gate D: known-frame decode reproduces the cited ceiling at the test regime (all modes)
    if pc_m < POS_CTRL_DECODE_FLOOR:
        return ("REGIME_POSCTRL_FAIL",
                f"known_frame_posctrl decode={pc_m:.3f} < {POS_CTRL_DECODE_FLOOR}: block-local decode does NOT "
                f"reproduce the cited ceiling at bs={N_DIM // B_TOTAL}/V={ANCHOR_V} regime; bump bs (fewer blocks) "
                f"before trusting the classify-then-decode result. {diag}")

    # Discriminator FIRES: occupancy carries frame ONLY under sparse-block geometry (paired negative control)
    if gap < FRAME_GAP_MIN:
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"sparse-vs-dense frame_class gap={gap:.3f} < {FRAME_GAP_MIN}: occupancy did not discriminate "
                f"frames beyond the dense control -> frame signal not attributable to sparse-block geometry. {diag}")

    if mode == "smoke":
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: classify-then-decode runs end-to-end AT N={N_DIM} V={ANCHOR_V}; "
                f"known_frame_posctrl reproduces the ceiling ({pc_m:.3f}); the sparse-vs-dense frame_class "
                f"discriminator fires (gap={gap:.3f}); BIAS audit non-degenerate. The pre-registered "
                f"comprehension band is FULL-only (canonical = remote multi-seed landing). {diag}")

    # --- FULL pre-registered bands (research note, verbatim) ---
    parse_cv = _cv(sparse_parse)
    if fc_m >= HP_FRAME_CLASS and parse_m >= HP_PARSE and parse_cv <= CV_MAX:
        return ("HARD_PASS",
                f"COMPREHENSION OPENS: frame_classification={fc_m:.3f} (>= {HP_FRAME_CLASS}) AND chained "
                f"parse_accuracy={parse_m:.3f} (>= {HP_PARSE}), parse_cv={parse_cv:.3f} (<= {CV_MAX}) over "
                f"{len(sparse_parse)} seeds, on REAL correlated GSBC fillers with NO position cue. This BEATS "
                f"the dense blind-factorization 0.000 (CITED) by parse={parse_m:.3f}. Frame recovery survives "
                f"real filler correlation via the sparse-block occupancy signature (dense_ctrl collapses to "
                f"{dense_m:.3f}); decode holds conditional on the recovered frame. {diag}")
    if fc_m <= HF_FRAME_CLASS or parse_m <= HF_PARSE:
        return ("HARD_FAIL",
                f"comprehension wall: frame_class={fc_m:.3f} (HF<= {HF_FRAME_CLASS}) OR parse={parse_m:.3f} "
                f"(HF<= {HF_PARSE}) -> real-filler correlation confounds the {'frame signal' if fc_m <= HF_FRAME_CLASS else 'conditional decode'}. {diag}")
    return ("MIDDLE_BAND",
            f"partial comprehension: frame_class={fc_m:.3f}, parse={parse_m:.3f} in "
            f"({HF_PARSE},{HP_PARSE}) OR cv over band. Error-propagation / decode-under-correlation is the "
            f"boundary; informative but not chain-grade. {diag}")


# ============================================================
# Driver
# ============================================================


def run_all(mode: str, output_dir: Path, t0: float):
    global _F_FOR_SEED
    cfg = get_config(mode)
    V, F, trials, seeds = cfg["V"], cfg["F"], cfg["trials"], cfg["seeds"]
    _F_FOR_SEED = F
    bs = N_DIM // B_TOTAL
    frames, templates = make_frames(B_TOTAL, D_ROLES, F)
    audit = bias_audit(frames, templates, F, B_TOTAL)

    per_unit = []          # cardinality ledger: one record per (seed, arm)
    seed_digests = {}
    total_units = len(seeds) * len(ARMS)
    unit = 0
    for seed in seeds:
        r = run_seed(seed, V, D_ROLES, F, bs, trials, frames, templates)
        seed_digests[str(seed)] = r["digests"]
        for arm in ARMS:
            unit += 1
            if arm == "sparse_block":
                rec = {"frame_class": round(r["frame_class"], 4), "parse": round(r["parse"], 4),
                       "cond_decode": round(r["cond_decode"], 4), "cond_decode_den": r["cond_decode_den"]}
            elif arm == "dense_ctrl":
                rec = {"frame_class": round(r["dense_frame_class"], 4)}
            else:  # known_frame_posctrl
                rec = {"decode": round(r["posctrl_decode"], 4)}
            per_unit.append({"seed": seed, "arm": arm, **rec})
        _heartbeat(output_dir, unit, total_units, t0,
                   extra={"seed": seed, "sparse_frame_class": round(r["frame_class"], 3),
                          "sparse_parse": round(r["parse"], 3), "dense_frame_class": round(r["dense_frame_class"], 3),
                          "posctrl_decode": round(r["posctrl_decode"], 3)})
        _say(f"  [seed {seed}] sparse_block frame_class={r['frame_class']:.3f} parse={r['parse']:.3f} "
             f"cond_decode={r['cond_decode']:.3f} | dense_ctrl frame_class={r['dense_frame_class']:.3f} "
             f"| known_frame_posctrl decode={r['posctrl_decode']:.3f}")
    return cfg, audit, frames, templates, per_unit, seed_digests, total_units


def _collect(per_unit, arm, key):
    return [u[key] for u in per_unit if u["arm"] == arm]


def _run(mode: str) -> int:
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    cfg = get_config(mode)
    exp_units = len(cfg["seeds"]) * len(ARMS)
    _write_start_marker(output_dir, mode, exp_units)
    _say(f"[{ANCHOR_NAME}] mode={mode} N={N_DIM} B_TOTAL={B_TOTAL} bs={N_DIM // B_TOTAL} D={D_ROLES} "
         f"V={cfg['V']} F={cfg['F']} trials={cfg['trials']} seeds={cfg['seeds']} expected_units={exp_units}")

    cfg, audit, frames, templates, per_unit, seed_digests, total_units = run_all(mode, output_dir, t0)
    _say(f"[{ANCHOR_NAME}] BIAS audit: {audit}")

    # arms_differ (META_RULE_AF): sparse codebook vs dense lexicon must differ; sparse composite vs dense
    # composite must differ; frame templates pairwise-distinct (in bias_audit).
    arms_differ_ok = True
    for sd in seed_digests.values():
        if sd["cb_gsbc"] == sd["dense_lex"]:
            arms_differ_ok = False
        if sd["comp_sparse"] == sd["comp_dense"]:
            arms_differ_ok = False
    if audit["n_distinct_templates"] != cfg["F"]:
        arms_differ_ok = False
    if not arms_differ_ok:
        raise AssertionError("META_RULE_AF VIOLATION: sparse/dense arm artifacts bit-identical OR frame "
                             "templates not all distinct")

    sparse_fc = _collect(per_unit, "sparse_block", "frame_class")
    sparse_parse = _collect(per_unit, "sparse_block", "parse")
    sparse_cond = _collect(per_unit, "sparse_block", "cond_decode")
    dense_fc = _collect(per_unit, "dense_ctrl", "frame_class")
    posctrl = _collect(per_unit, "known_frame_posctrl", "decode")

    verdict, vmsg = classify(mode, audit, sparse_fc, sparse_parse, sparse_cond, dense_fc, posctrl,
                             len(per_unit), exp_units)
    elapsed = time.perf_counter() - t0

    arms = {
        "sparse_block": {
            "frame_class_mean": round(float(np.mean(sparse_fc)), 4), "frame_class_per_seed": sparse_fc,
            "parse_mean": round(float(np.mean(sparse_parse)), 4), "parse_per_seed": sparse_parse,
            "parse_cv": round(_cv(sparse_parse), 4) if len(sparse_parse) > 1 else None,
            "cond_decode_mean": round(float(np.mean(sparse_cond)), 4), "cond_decode_per_seed": sparse_cond,
        },
        "dense_ctrl": {
            "frame_class_mean": round(float(np.mean(dense_fc)), 4), "frame_class_per_seed": dense_fc,
            "chance": round(1.0 / cfg["F"], 4),
            "decode_CITED": 0.000,  # dense blind decode collapse (do NOT rerun)
        },
        "known_frame_posctrl": {
            "decode_mean": round(float(np.mean(posctrl)), 4), "decode_per_seed": posctrl,
        },
    }

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: frame-classify-then-known-decode comprehension primitive ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": len(cfg["seeds"]),
        "n_units": len(per_unit),
        "expected_n_units": exp_units,
        "cardinality_ok": len(per_unit) >= exp_units,
        "arms_differ_verified": arms_differ_ok,
        "config": {
            "N": N_DIM, "GSBC_DIM": GSBC_DIM, "K_ACTIVE": K_ACTIVE, "F_SPARSE": F_SPARSE,
            "B_TOTAL": B_TOTAL, "bs": N_DIM // B_TOTAL, "D_ROLES": D_ROLES, "V": cfg["V"], "F": cfg["F"],
            "trials": cfg["trials"], "seeds": list(cfg["seeds"]),
            "classifier": "matched_filter_occupancy_L2_nonlearned",
            "frame_def": "distinct_sorted_D_subset_of_B_TOTAL_blocks_role_d_to_dth_block",
            "algebra_sparse": "block_superposition_sum", "algebra_dense_ctrl": "dense_multiply_bind",
            "native_filler": "GSBC_EXPAND2X_seed7_FULL_projected_sparse_bipolar", "pool_meta": _load_pool()["meta"],
        },
        "arms": arms,
        "per_unit": per_unit,
        "bias_audit": audit,
        "frames": [list(fr) for fr in frames],
        "bands": {"HP_frame_class": HP_FRAME_CLASS, "HP_parse": HP_PARSE, "HF_frame_class": HF_FRAME_CLASS,
                  "HF_parse": HF_PARSE, "cv_max": CV_MAX, "pos_ctrl_decode_floor": POS_CTRL_DECODE_FLOOR,
                  "frame_gap_min": FRAME_GAP_MIN},
        "hp_scope": {"sparse_block": ["HP_frame_class", "HP_parse", "cv_max"],
                     "dense_ctrl": ["negative_control_expected_at_chance"],
                     "known_frame_posctrl": ["pos_ctrl_decode_floor"]},
        "cited_baselines": {
            "dense_blind_decode_0": "data/exp_generation_decoder_gsbc_native_blocklocal_v1:dense_gsbc_fullreso@V1024D3=0.000",
            "dense_blind_roundtrip_0": "data/exp_generation_decoder_roundtrip_v1:real_fullreso_hi=0.000",
            "known_frame_ceiling": "data/exp_generation_decoder_gsbc_native_blocklocal_v1:blocklocal_gsbc@V1024D3=1.000,@V8192D26=0.856",
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
    global _F_FOR_SEED
    cfg = get_config("selftest")
    _F_FOR_SEED = cfg["F"]
    bs = N_DIM // B_TOTAL
    frames, templates = make_frames(B_TOTAL, D_ROLES, cfg["F"])
    audit = bias_audit(frames, templates, cfg["F"], B_TOTAL)
    r = run_seed(7, cfg["V"], D_ROLES, cfg["F"], bs, cfg["trials"], frames, templates)
    # invariants: (a) BIAS audit non-degenerate; (b) sparse occupancy classifies frames perfectly
    # (correlation-independent); (c) known-frame decode recovers; (d) dense occupancy collapses (< sparse).
    ok = (audit["non_degenerate"]
          and r["frame_class"] >= 0.99
          and r["posctrl_decode"] >= 0.90
          and (r["frame_class"] - r["dense_frame_class"]) >= 0.30)
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: non_degen={audit['non_degenerate']} "
         f"sparse_frame_class={r['frame_class']:.3f} dense_frame_class={r['dense_frame_class']:.3f} "
         f"posctrl_decode={r['posctrl_decode']:.3f} parse={r['parse']:.3f} [{time.perf_counter()-t0:.1f}s]")
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
