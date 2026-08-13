"""exp_readout_fix_v1 -- implement the THREE measured read-out defects' fixes and ABLATE them.

Pre-reg: preregs/2026-08-12_readout_fix_v1.md (filed BEFORE any run).
Upstream: exp_context_vector_signal_v1 (commits 79c7521cd / 59479cf82). Its HARNESS is REUSED, not
rebuilt: this cell imports that cell's pass-cache loader, arm construction, eligible-anchor view,
flip-count / cluster-bootstrap / CI / concentration helpers, and re-scores its OWN cached encounter
set, so every number is directly comparable to flip REAL 0.782962.

THE DEFECT IS THE READ-OUT, NOT THE ENCODER (all MEASURED@data/exp_context_vector_signal_v1/
metrics.json):
  FIX 1  magnitude gate is blind: informative_rate REAL 0.416687 vs SCRAMBLE_SENT 0.416808
         (enrichment 1.0000x); mean best cos 0.311343 vs 0.311344. Replaced by a FIELD-RELATIVE
         gate (z_top or margin) whose threshold is a QUANTILE OF A MEASURED DISTRIBUTION.
  FIX 2  frequency-biased pool: trace_sum_separation -0.063775 (a lemma's OWN summed contexts
         clear SENSE_MATCH_THRESH LESS often than scrambled ones). Per-anchor background
         standardization (hubness correction).
  FIX 3  growing anchor space: fixed-space flip 0.782962 -> segment-snapshot 0.856881 (+0.0739).
         ConceptSpace.freeze() -> one stable field per verification episode.

SCOPE, STATED IN THE CELL ITSELF: this measures READ-OUT STABILITY (flip rate, gate selectivity,
projected confirm rate). It measures NOTHING about grounding QUALITY or whether any anchor means
anything. A better read-out is not better meanings. PBV is NOT re-run; the confirm rate is a
PROJECTION of the exact Library.flag state machine over re-scored encounters (prereg sec 7).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; sha256 over each condition's argmax vector)
# - final_metrics_atomicity: tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
# - crlb_n/a declared in prereg sec 11 (paired difference of rates, not an estimator vs a floor)
# - baseline_in_band: BASE flip_all 0.7830 is inside (0.05, 0.95) (META_RULE_AG)
# - discriminator survives scale: runs the SAME FULL 8282-encounter population the baseline used
# - HARD bands pre-committed in prereg sec 8; non-failable bands NAMED and REMOVED (prereg sec 8)
# - cardinality_ok: EXPECTED_N_UNITS = 4 FIXED*2 arms + 8 GROWING*2 arms = 24
# - per-unit failure-class instrumentation: no bare except; crash -> CELL_CRASHED metrics
# - calibration_check: adaptive_with_discriminator_gate (thresholds derived on a SELECTION half;
#   discriminator re-verified on the EVALUATION half)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - real_code_path: self_test runs the UPSTREAM cell's own self_test (real organs) + constructs
#   ConceptSpace/FrozenAnchorSpace/ReadoutConfig and calls the ORGAN canonicalize_fast
# - substrate_signature: every substrate call bound against inspect.signature, base kwargs only
# - deterministic seeding: fixed ints + hashlib only; no builtin hash(), no list(set())

ASCII-only.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)          # progress_logging: print_flush_true

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.closed_class_lexicon import is_eligible_meaning
from hdlab.grounding_acquisition_loop import (
    PBV_ABANDON_STRENGTH, PBV_GAMMA, PBV_INIT_STRENGTH, pbv_update_strength,
)
from hdlab.hd_fact_store import HDFactStore
from hdlab.reading_grounding_loop import (
    KNOWN_RELATION, MEANING_RELATION, PBV_INFORMATIVE_MIN, SENSE_MATCH_THRESH,
    ConceptSpace, FrozenAnchorSpace, ReadingLoopState, ReadoutConfig,
    canonicalize_fast, checkpoint, make_pbv_fns, process_sentence, seed_known_words,
)

from experiments._cell_heartbeat import emit_heartbeat
from experiments.exp_reading_grounding_loop_cycle1_v1 import SCHEMA_THRESH_FULL, repo_path
# ---- HARNESS REUSE (prereg sec 3): every one of these is the upstream cell's own code ----------
from experiments.exp_context_vector_signal_v1 import (
    ARMS as UP_ARMS,
    N_BOOTSTRAP,
    _agreement,
    _atomic_json,
    _boot_indices,
    _concentration,
    _eligible_anchor_view,
    _flip_rate_ci,
    _per_lemma_flip_counts,
    _seed_from,
    build_arm_contexts,
    load_pass_cache,
    self_test as upstream_self_test,
)

ANCHOR_NAME = "readout_fix_v1"
UPSTREAM_ANCHOR = "context_vector_signal_v1"
PRIMARY_NULL = "SCRAMBLE_SENT"
ARMS = ("REAL", PRIMARY_NULL)

# (name, f1, f2, f3) -- the 2^3 ablation matrix (prereg sec 5).
CONDITIONS: Tuple[Tuple[str, int, int, int], ...] = (
    ("BASE", 0, 0, 0), ("F1", 1, 0, 0), ("F2", 0, 1, 0), ("F3", 0, 0, 1),
    ("F1F2", 1, 1, 0), ("F1F3", 1, 0, 1), ("F2F3", 0, 1, 1), ("ALL", 1, 1, 1),
)
REGIMES = ("FIXED", "GROWING")
EXPECTED_N_UNITS = 4 * len(ARMS) + 8 * len(ARMS)         # 24 (prereg sec 5)
BLOCK = 1024

# ---- pre-registered bands (prereg sec 8; frozen before any run) ---------------------------------
FPR_ALPHA = 0.05                 # G-FPR: null admission fixed by construction
PRIMARY_DROP_HARD = 0.15         # ALL vs BASE gated-flip reduction for HARD_PASS
PRIMARY_DROP_MIDDLE = 0.05
RCTRL_MARGIN_HARD = 0.10         # ALL must beat the retention-matched random subset by this much
RCTRL_MARGIN_MIDDLE = 0.02
LOO_LOAD_BEARING = 0.05          # leave-one-out degradation that makes a fix load-bearing
ALONE_NOT_JUSTIFIED = 0.02
F1_SELECTIVE_MAX = 0.20          # null admission at matched real retention (legacy = 0.4168)
F1_BLIND_MIN = 0.35
F1_ENRICH_MIN = 0.15             # G-FPR real retention at null 0.05
F1_ENRICH_FAIL = 0.075
F2_HELPS_MIN = 0.05              # flip_all drop
F2_NULL_MAX = 0.02
F3_HELPS_MIN = 0.05              # GROWING-regime flip drop (ceiling 0.0739, prereg sec 8)
CONFIRM_CLEARS = 0.20
CONFIRM_MOVES = 0.1206           # observed 0.100561 + 0.02
COLLAPSE_TOP1 = 0.10             # 6.7x the measured baseline top1_share 0.014851
COLLAPSE_MIN_DISTINCT = 100
CALIB_ARM_DELTA_MAX = 0.05       # F2 background near-invariance under the null permutation
PBV_OBSERVED_CONFIRM_RATE = 0.100561   # MEASURED@data/exp_pbv_hypothesis_v1_smoke/metrics.json:
                                        # arms.B_PBV.trajectory (788 / (788 + 7048))
PROJECTION_TOL = 0.05
BASELINE_REPRO_TOL = 1e-6


# =============================================================== harness plumbing
def _output_dir(run_mode: str) -> str:
    return repo_path(f"data/exp_{ANCHOR_NAME}" + ("_smoke" if run_mode == "smoke" else ""))


def _upstream_dir(run_mode: str) -> str:
    return repo_path(f"data/exp_{UPSTREAM_ANCHOR}" + ("_smoke" if run_mode == "smoke" else ""))


def _write_start_marker(output_dir: str, run_mode: str) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": EXPECTED_N_UNITS, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir: str, exc: BaseException) -> None:
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}",
            "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    _atomic_json(os.path.join(output_dir, "metrics.json"), diag)


def _sel_half(lemma: str) -> bool:
    """Deterministic 50/50 SELECTION vs EVALUATION split of lemmas. sha256 only -- never the
    builtin salted hasher, which is per-process randomized (PROT-023 / F.5)."""
    return (int.from_bytes(hashlib.sha256(("split|" + lemma).encode("utf-8")).digest()[:8],
                           "big") % 2) == 0


# =============================================================== field scoring
def _score_group(ctx: np.ndarray, self_local: np.ndarray, mat: np.ndarray, norms: np.ndarray,
                 ctr: Optional[np.ndarray], scl: Optional[np.ndarray]) -> Dict[str, np.ndarray]:
    """Batched equivalent of the ORGAN's canonicalize_fast with a ReadoutConfig, over one anchor
    field. Returns per-row: best anchor index (LOCAL, -1 = no scannable anchor), RAW best cosine,
    z_top and margin over the calibrated field (raw field when ctr/scl are None).

    The self-anchor is excluded exactly as the organ excludes it (`keep[idx]=False`), by setting it
    to NaN before every statistic -- so mean/sd/second-best are computed over the SAME field the
    organ scans, not over a field that still contains the target."""
    n = ctx.shape[0]
    out = {"idx": np.full(n, -1, dtype=np.int64), "cos": np.zeros(n), "z": np.zeros(n),
           "margin": np.zeros(n)}
    for s in range(0, n, BLOCK):
        e = min(s + BLOCK, n)
        X = ctx[s:e]
        xn = np.linalg.norm(X, axis=1)
        sims = (X @ mat.T) / np.outer(np.maximum(xn, 1e-12), norms)
        cal = sims if ctr is None else (sims - ctr[None, :]) / scl[None, :]
        cal = np.array(cal, dtype=np.float64, copy=True)
        rows = np.flatnonzero(self_local[s:e] >= 0)
        if rows.size:
            cal[rows, self_local[s:e][rows]] = np.nan
        best = np.nanargmax(cal, axis=1)
        ar = np.arange(e - s)
        out["idx"][s:e] = best
        out["cos"][s:e] = sims[ar, best]
        mu = np.nanmean(cal, axis=1)
        sd = np.nanstd(cal, axis=1)
        out["z"][s:e] = np.where(sd < 1e-12, 0.0, (cal[ar, best] - mu) / np.maximum(sd, 1e-12))
        filled = np.where(np.isnan(cal), -np.inf, cal)
        part = np.partition(filled, -2, axis=1)
        out["margin"][s:e] = part[:, -1] - part[:, -2]
        zero = xn < 1e-9
        for k in ("idx",):
            out[k][s:e][zero] = -1
        for k in ("cos", "z", "margin"):
            out[k][s:e][zero] = 0.0
    return out


class FieldSet:
    """Per-encounter read-out of one (space-assignment, arm, f2) combination, in GLOBAL anchor ids."""

    def __init__(self, idx: np.ndarray, cos: np.ndarray, z: np.ndarray, margin: np.ndarray) -> None:
        self.idx, self.cos, self.z, self.margin = idx, cos, z, margin

    def stat(self, name: str) -> np.ndarray:
        return self.z if name == "z_top" else self.margin


def compute_field(mats_arm: np.ndarray, target_lemmas: Sequence[str], groups: List[dict],
                  global_pos: Dict[str, int],
                  background: Optional[Dict[str, Tuple[float, float]]]) -> FieldSet:
    """Score every encounter against its assigned anchor field, mapping the winner into the GLOBAL
    anchor index space so that adjacent encounters assigned to different snapshots still compare
    like-for-like (the upstream cell's own space-drift convention)."""
    n = mats_arm.shape[0]
    idx = np.full(n, -1, dtype=np.int64)
    cos = np.zeros(n)
    z = np.zeros(n)
    margin = np.zeros(n)
    for g in groups:
        rows = g["rows"]
        anchors, mat, norms = g["anchors"], g["mat"], g["norms"]
        pos = g["pos"]
        self_local = np.array([pos.get(target_lemmas[r], -1) for r in rows], dtype=np.int64)
        ctr = scl = None
        if background is not None:
            ctr = np.array([background.get(a, (0.0, 1.0))[0] for a in anchors], dtype=np.float64)
            scl = np.array([max(background.get(a, (0.0, 1.0))[1], 1e-6) for a in anchors],
                           dtype=np.float64)
        r = _score_group(mats_arm[rows], self_local, mat, norms, ctr, scl)
        gid = np.array([global_pos.get(anchors[int(j)], -2) if j >= 0 else -1
                        for j in r["idx"].tolist()], dtype=np.int64)
        idx[rows] = gid
        cos[rows] = r["cos"]
        z[rows] = r["z"]
        margin[rows] = r["margin"]
    return FieldSet(idx, cos, z, margin)


# =============================================================== statistics
def _auc(pos: np.ndarray, neg: np.ndarray) -> float:
    """Mann-Whitney AUC: P(stat(REAL) > stat(NULL)) with ties at 0.5. 0.5 = the statistic is as
    blind as the magnitude gate; 1.0 = perfect separation."""
    allv = np.concatenate([pos, neg])
    order = np.argsort(allv, kind="stable")
    ranks = np.empty(len(allv), dtype=np.float64)
    ranks[order] = np.arange(1, len(allv) + 1, dtype=np.float64)
    sv = allv[order]
    i = 0
    while i < len(sv):                       # average ranks within tie groups
        j = i
        while j + 1 < len(sv) and sv[j + 1] == sv[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = np.mean(ranks[order[i:j + 1]])
        i = j + 1
    r_pos = ranks[:len(pos)].sum()
    return float((r_pos - len(pos) * (len(pos) + 1) / 2.0) / (len(pos) * len(neg)))


def _gated_flip_counts(lemma_ids: np.ndarray, argmax: np.ndarray, retained: np.ndarray,
                       n_lemmas: int) -> Tuple[np.ndarray, np.ndarray]:
    """Flip counts over adjacent RETAINED encounters (what the verifier actually sees). Encounters
    are grouped by lemma and ordered within lemma, so filtering preserves both."""
    keep = np.flatnonzero(retained)
    if keep.size == 0:
        return np.zeros(n_lemmas), np.zeros(n_lemmas)
    return _per_lemma_flip_counts(lemma_ids[keep], argmax[keep], n_lemmas)


def _paired_delta(fA: np.ndarray, pA: np.ndarray, fB: np.ndarray, pB: np.ndarray,
                  boot: np.ndarray) -> dict:
    """B minus A, bootstrapped on the SAME resampled lemma sets (the upstream paired convention)."""
    _a, _ca, dA = _flip_rate_ci(fA, pA, boot)
    _b, _cb, dB = _flip_rate_ci(fB, pB, boot)
    diff = dB - dA
    pt = (fB.sum() / pB.sum() if pB.sum() > 0 else float("nan")) - \
         (fA.sum() / pA.sum() if pA.sum() > 0 else float("nan"))
    return {"delta_point": round(float(pt), 6),
            "delta_ci95": [round(float(np.nanpercentile(diff, 2.5)), 6),
                           round(float(np.nanpercentile(diff, 97.5)), 6)],
            "frac_above_zero": round(float(np.nanmean(diff > 0)), 6)}


def pbv_project(objs: np.ndarray, retained: np.ndarray, lemma_ids: np.ndarray,
                n_lemmas: int) -> dict:
    """PROJECT the confirm/disconfirm ledger of the EXACT Library.flag PBV state machine
    (hdlab/grounding_acquisition_loop.py:286-321) over these re-scored encounters. NOT a PBV run:
    no Library, no store, no grounding -- only the propose/verify/abandon accounting, using the
    ORGAN's own `pbv_update_strength` so the update rule cannot drift from the substrate's."""
    h = {}
    s = {}
    n_conf = n_dis = n_prop = n_aband = 0
    for r in range(objs.shape[0]):
        if not retained[r]:
            continue                                   # UNINFORMATIVE: no verdict (organ returns None)
        li = int(lemma_ids[r])
        obj = int(objs[r])
        if li not in h:
            h[li] = obj
            s[li] = PBV_INIT_STRENGTH                   # PROPOSE
            n_prop += 1
            continue
        if obj == h[li]:
            n_conf += 1
            s[li] = pbv_update_strength(s[li], True, PBV_GAMMA)
            continue
        n_dis += 1
        s[li] = pbv_update_strength(s[li], False, PBV_GAMMA)
        if s[li] <= PBV_ABANDON_STRENGTH:               # ABANDON + REPROPOSE from THIS encounter
            n_aband += 1
            h[li] = obj
            s[li] = PBV_INIT_STRENGTH
    tot = n_conf + n_dis
    return {"n_propose": n_prop, "n_confirm": n_conf, "n_disconfirm": n_dis,
            "n_abandon": n_aband, "n_verdicts": tot,
            "confirm_rate_projected": round(n_conf / tot, 6) if tot else None,
            "n_lemmas_with_hypothesis": len(h)}


# =============================================================== main measurement
def measure(run_mode: str, output_dir: str) -> dict:
    up_dir = _upstream_dir(run_mode)
    cached = load_pass_cache(up_dir)
    if cached is None:
        raise AssertionError(
            f"upstream pass cache missing at {up_dir} -- this cell REUSES the "
            f"exp_{UPSTREAM_ANCHOR} harness and cannot run without it")
    space, snaps, encounters, meta = cached
    up_metrics_path = os.path.join(up_dir, "metrics.json")
    with open(up_metrics_path, encoding="utf-8") as f:
        up = json.load(f)
    ref_flip = float(up["per_encounter"]["REAL"]["flip_rate"])
    ref_informative = float(up["per_encounter"]["REAL"]["informative_rate"])
    print(f"[info] upstream cache: {len(encounters)} encounters, ref flip={ref_flip:.6f}, "
          f"ref informative={ref_informative:.6f}", flush=True)

    mats, arm_info = build_arm_contexts(encounters)
    keep = arm_info["keep_index"]
    kept = [encounters[i] for i in keep]
    lemma_list = sorted({e["lemma"] for e in kept})
    lemma_pos = {l: i for i, l in enumerate(lemma_list)}
    lemma_ids = np.array([lemma_pos[e["lemma"]] for e in kept], dtype=np.int64)
    target_lemmas = [e["lemma"] for e in kept]
    n_lemmas = len(lemma_list)
    n_enc = len(kept)

    anchors_all, mat_all = space.anchor_matrix()
    anchors, amat, anorms = _eligible_anchor_view(list(anchors_all), mat_all)
    global_pos = {a: i for i, a in enumerate(anchors)}
    n_zero_norm_eligible = int(sum(1 for a in anchors_all
                                   if is_eligible_meaning(a)
                                   and np.linalg.norm(mat_all[list(anchors_all).index(a)]) < 1e-9)) \
        if len(anchors_all) < 4000 else -1
    print(f"[info] anchors total={len(anchors_all)} eligible={len(anchors)} "
          f"zero_norm_eligible={n_zero_norm_eligible}", flush=True)

    # ---- space assignments -----------------------------------------------------------------
    fixed_group = [{"rows": np.arange(n_enc), "anchors": anchors, "mat": amat, "norms": anorms,
                    "pos": global_pos}]
    seg_of_enc = [e["segment"] for e in kept]
    first_seg_of_lemma: Dict[str, str] = {}
    for e in kept:
        first_seg_of_lemma.setdefault(e["lemma"], e["segment"])
    snap_views = {}
    for seg, (sanch, smat) in snaps.items():
        sa, sm, sn = _eligible_anchor_view(list(sanch), smat)
        if sa:
            snap_views[seg] = {"anchors": sa, "mat": sm, "norms": sn,
                               "pos": {a: i for i, a in enumerate(sa)}}

    def _groups_by(seg_per_enc: Sequence[str]) -> List[dict]:
        out = []
        for seg, view in snap_views.items():
            rows = np.flatnonzero(np.array([s == seg for s in seg_per_enc]))
            if rows.size:
                out.append({"rows": rows, **view})
        return out

    grow_enc_groups = _groups_by(seg_of_enc)                                    # F3 OFF
    grow_epi_groups = _groups_by([first_seg_of_lemma[e["lemma"]] for e in kept])  # F3 ON
    assignments = {"fixed": fixed_group, "grow_enc": grow_enc_groups, "grow_epi": grow_epi_groups}

    # ---- SELECTION / EVALUATION split ---------------------------------------------------------
    sel_lemma = np.array([_sel_half(l) for l in lemma_list], dtype=bool)
    sel_enc = sel_lemma[lemma_ids]
    eva_enc = ~sel_enc
    print(f"[info] split: SEL {int(sel_enc.sum())} enc / EVA {int(eva_enc.sum())} enc", flush=True)

    # ---- FIX 2 background (per-anchor mean/sd of cos over SELECTION-half REAL contexts) --------
    def _background(ctx: np.ndarray, rows: np.ndarray) -> Dict[str, Tuple[float, float]]:
        acc_n = 0
        s1 = np.zeros(len(anchors))
        s2 = np.zeros(len(anchors))
        for s in range(0, rows.size, BLOCK):
            blk = rows[s:s + BLOCK]
            X = ctx[blk]
            xn = np.maximum(np.linalg.norm(X, axis=1), 1e-12)
            sims = (X @ amat.T) / np.outer(xn, anorms)
            s1 += sims.sum(axis=0)
            s2 += (sims ** 2).sum(axis=0)
            acc_n += blk.size
        mu = s1 / acc_n
        var = np.maximum(s2 / acc_n - mu ** 2, 0.0)
        return {a: (float(mu[i]), float(np.sqrt(var[i]))) for i, a in enumerate(anchors)}

    sel_rows = np.flatnonzero(sel_enc)
    background = _background(mats["REAL"], sel_rows)
    background_null = _background(mats[PRIMARY_NULL], sel_rows)
    calib_delta_mu = max(abs(background[a][0] - background_null[a][0]) for a in anchors)
    calib_delta_sd = max(abs(background[a][1] - background_null[a][1]) for a in anchors)
    hub_rank = sorted(anchors, key=lambda a: -background[a][0])[:10]
    print(f"[info] F2 background: arm delta mu={calib_delta_mu:.5f} sd={calib_delta_sd:.5f}; "
          f"top hubs={hub_rank[:5]}", flush=True)

    # ---- all needed fields ---------------------------------------------------------------------
    fields: Dict[Tuple[str, str, int], FieldSet] = {}
    t0 = time.time()
    todo = [("fixed", a, f2) for a in ARMS for f2 in (0, 1)]
    if snap_views:
        todo += [(asg, a, f2) for asg in ("grow_enc", "grow_epi") for a in ARMS for f2 in (0, 1)]
    for k, (asg, arm, f2) in enumerate(todo):
        fields[(asg, arm, f2)] = compute_field(mats[arm], target_lemmas, assignments[asg],
                                               global_pos, background if f2 else None)
        emit_heartbeat(output_dir, unit_idx=k, total_units=len(todo), elapsed_s=time.time() - t0)
        print(f"[progress] field {asg}/{arm}/f2={f2} done ({k + 1}/{len(todo)}) "
              f"elapsed={time.time() - t0:.1f}s", flush=True)

    # ---- BASELINE REPRODUCTION GATE (harness gate, zero verdict weight) ------------------------
    boot = _boot_indices(n_lemmas, N_BOOTSTRAP, _seed_from("bootstrap"))
    base = fields[("fixed", "REAL", 0)]
    bf, bp = _per_lemma_flip_counts(lemma_ids, base.idx, n_lemmas)
    base_flip, base_ci, _ = _flip_rate_ci(bf, bp, boot)
    legacy_retention = float(np.mean(base.cos >= PBV_INFORMATIVE_MIN))
    baseline_repro = abs(base_flip - ref_flip) <= BASELINE_REPRO_TOL
    print(f"[gate] baseline reproduce: {base_flip:.6f} vs upstream {ref_flip:.6f} -> "
          f"{baseline_repro}; legacy retention={legacy_retention:.6f}", flush=True)

    # ---- FIX 1: statistic form + thresholds, DERIVED on the SELECTION half ----------------------
    stat_auc = {}
    for name in ("z_top", "margin"):
        stat_auc[name] = round(_auc(fields[("fixed", "REAL", 0)].stat(name)[sel_rows],
                                    fields[("fixed", PRIMARY_NULL, 0)].stat(name)[sel_rows]), 6)
    stat_auc["legacy_cos"] = round(_auc(fields[("fixed", "REAL", 0)].cos[sel_rows],
                                        fields[("fixed", PRIMARY_NULL, 0)].cos[sel_rows]), 6)
    stat_name = "z_top" if stat_auc["z_top"] >= stat_auc["margin"] else "margin"
    print(f"[info] statistic AUCs (SEL half) {stat_auc} -> chosen {stat_name}", flush=True)

    # AMENDMENT C3 (bug fix, disclosed): the G-MATCH threshold matches the retention of the LEGACY
    # gate IN THE SAME REGIME AND CALIBRATION, not the FIXED regime's. Matching every assignment to
    # the fixed regime's 0.4167 made the GROWING F1 arms retain 1.0 at smoke -- a broken comparison,
    # not a result. AMENDMENT C4: BOTH statistic forms are carried through to the FULL results
    # instead of selecting one, because the selection criterion (AUC) came back at chance for both
    # at smoke; a coin-flip selection must not be hidden behind a single reported number.
    thresholds: Dict[Tuple[str, int, str], dict] = {}
    legacy_ret_by: Dict[Tuple[str, int], float] = {}
    for asg in assignments:
        if not assignments[asg]:
            continue
        for f2 in (0, 1):
            lr = float(np.mean(fields[(asg, "REAL", f2)].cos >= PBV_INFORMATIVE_MIN))
            legacy_ret_by[(asg, f2)] = lr
            for st in ("z_top", "margin"):
                fr = fields[(asg, "REAL", f2)].stat(st)[sel_rows]
                fn = fields[(asg, PRIMARY_NULL, f2)].stat(st)[sel_rows]
                thresholds[(asg, f2, st)] = {
                    "g_match": float(np.quantile(fr, max(0.0, 1.0 - lr))),  # retention-matched
                    "g_fpr": float(np.quantile(fn, 1.0 - FPR_ALPHA)),       # null admission 0.05
                    "legacy_retention_here": round(lr, 6)}

    # ---- conditions -----------------------------------------------------------------------------
    def _assignment_for(regime: str, f3: int) -> str:
        if regime == "FIXED":
            return "fixed"
        return "grow_epi" if f3 else "grow_enc"

    def _retained(fs: FieldSet, f1: int, asg: str, f2: int, variant: str,
                  st: Optional[str] = None) -> np.ndarray:
        if not f1:
            return fs.cos >= PBV_INFORMATIVE_MIN
        return fs.stat(st or stat_name) >= thresholds[(asg, f2, st or stat_name)][variant]

    def _gate_variants(f1: int) -> List[Tuple[str, str, str]]:
        """(label, statistic, threshold-variant) actually evaluated for a condition."""
        if not f1:
            return [("legacy_cos", stat_name, "g_match")]      # statistic unused when f1 == 0
        return [(f"{st}|{v}", st, v) for st in ("z_top", "margin") for v in ("g_match", "g_fpr")]

    results: Dict[str, dict] = {}
    per_lemma_counts: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}
    n_units = 0
    for regime in REGIMES:
        if regime == "GROWING" and not snap_views:
            continue
        for (cname, f1, f2, f3) in CONDITIONS:
            if regime == "FIXED" and f3:
                continue                        # prereg sec 8 removed band #2: no-op by construction
            asg = _assignment_for(regime, f3)
            for arm in ARMS:
                fs = fields[(asg, arm, f2)]
                key = f"{regime}|{cname}|{arm}"
                row: Dict[str, object] = {"regime": regime, "condition": cname, "arm": arm,
                                          "f1": f1, "f2": f2, "f3": f3, "assignment": asg}
                fl, pr = _per_lemma_flip_counts(lemma_ids, fs.idx, n_lemmas)
                fa, cia, _ = _flip_rate_ci(fl, pr, boot)
                row["flip_all"] = round(fa, 6)
                row["flip_all_ci95"] = [round(cia[0], 6), round(cia[1], 6)]
                row["n_pairs_all"] = int(pr.sum())
                variants = {}
                headline = f"{stat_name}|g_match" if f1 else "legacy_cos"
                for label, st, variant in _gate_variants(f1):
                    ret = _retained(fs, f1, asg, f2, variant, st)
                    gf, gp = _gated_flip_counts(lemma_ids, fs.idx, ret, n_lemmas)
                    gfr, gci, _ = _flip_rate_ci(gf, gp, boot)
                    gf_e, gp_e = _gated_flip_counts(lemma_ids[eva_enc], fs.idx[eva_enc],
                                                    ret[eva_enc], n_lemmas)
                    v = {"retention": round(float(np.mean(ret)), 6),
                         "flip_gated": round(gfr, 6) if gp.sum() > 0 else None,
                         "flip_gated_ci95": ([round(gci[0], 6), round(gci[1], 6)]
                                             if gp.sum() > 0 else None),
                         "n_pairs_gated": int(gp.sum()),
                         "retention_eva_half": round(float(np.mean(ret[eva_enc])), 6),
                         "flip_gated_eva_half": (round(float(gf_e.sum() / gp_e.sum()), 6)
                                                 if gp_e.sum() > 0 else None),
                         "pbv": pbv_project(fs.idx, ret, lemma_ids, n_lemmas)}
                    variants[label] = v
                    if label == headline:
                        per_lemma_counts[key] = (gf, gp)
                        row.update({"retention": v["retention"], "flip_gated": v["flip_gated"],
                                    "flip_gated_ci95": v["flip_gated_ci95"],
                                    "n_pairs_gated": v["n_pairs_gated"],
                                    "retention_eva_half": v["retention_eva_half"],
                                    "flip_gated_eva_half": v["flip_gated_eva_half"],
                                    "pbv": v["pbv"]})
                row["headline_gate"] = headline
                row["gate_variants"] = variants
                if f1:
                    row["retention_gfpr"] = variants[f"{stat_name}|g_fpr"]["retention"]
                row["concentration"] = _concentration(fs.idx)
                row["argmax_digest"] = hashlib.sha256(fs.idx.tobytes()).hexdigest()[:16]
                row["mean_best_cos"] = round(float(np.mean(fs.cos)), 6)
                results[key] = row
                n_units += 1
        print(f"[progress] regime={regime} done, units={n_units} "
              f"elapsed={time.time() - t0:.1f}s", flush=True)

    # ---- R-CTRL: retention-matched RANDOM subset on the BASE argmax (prereg sec 8, removed #3) --
    rctrl = {}
    for regime in REGIMES:
        if regime == "GROWING" and not snap_views:
            continue
        asg = "fixed" if regime == "FIXED" else "grow_enc"
        fs = fields[(asg, "REAL", 0)]
        bundle = f"{regime}|ALL|REAL" if f"{regime}|ALL|REAL" in results else f"{regime}|F1F2|REAL"
        target_n = int(round(float(results[bundle]["retention"]) * n_enc))
        rng = np.random.default_rng(_seed_from(f"rctrl_{regime}"))
        pick = rng.permutation(n_enc)[:target_n]
        ret = np.zeros(n_enc, dtype=bool)
        ret[pick] = True
        gf, gp = _gated_flip_counts(lemma_ids, fs.idx, ret, n_lemmas)
        gfr, gci, _ = _flip_rate_ci(gf, gp, boot)
        per_lemma_counts[f"{regime}|R-CTRL|REAL"] = (gf, gp)
        rctrl[regime] = {"retention": round(float(np.mean(ret)), 6),
                         "flip_gated": round(gfr, 6), "n_pairs_gated": int(gp.sum()),
                         "flip_gated_ci95": [round(gci[0], 6), round(gci[1], 6)],
                         "pbv": pbv_project(fs.idx, ret, lemma_ids, n_lemmas)}

    # ---- paired deltas: ALL vs BASE, leave-one-out, and vs R-CTRL -------------------------------
    def _delta(a_key: str, b_key: str) -> dict:
        fA, pA = per_lemma_counts[a_key]
        fB, pB = per_lemma_counts[b_key]
        return _paired_delta(fA, pA, fB, pB, boot)

    deltas = {}
    for regime in REGIMES:
        if regime == "GROWING" and not snap_views:
            continue
        avail = [c for (c, _f1, _f2, f3) in CONDITIONS if not (regime == "FIXED" and f3)]
        for cname in avail:
            if cname == "BASE":
                continue
            deltas[f"{regime}|{cname}_vs_BASE"] = _delta(f"{regime}|BASE|REAL",
                                                         f"{regime}|{cname}|REAL")
        # leave-one-out: the regime's BUNDLE minus one fix. FIXED's bundle is F1F2 (F3 is a no-op
        # there), GROWING's is ALL. delta_point > 0 means REMOVING the fix made the flip rate WORSE.
        bundle_c = "ALL" if "ALL" in avail else "F1F2"
        loo_map = ({"F1": "F2F3", "F2": "F1F3", "F3": "F1F2"} if bundle_c == "ALL"
                   else {"F1": "F2", "F2": "F1"})
        for missing, loo in loo_map.items():
            if loo in avail:
                deltas[f"{regime}|LOO_drop_{missing}"] = _delta(f"{regime}|{bundle_c}|REAL",
                                                                f"{regime}|{loo}|REAL")
        deltas[f"{regime}|BUNDLE_vs_RCTRL"] = _delta(f"{regime}|R-CTRL|REAL",
                                                     f"{regime}|{bundle_c}|REAL")
        deltas[f"{regime}|bundle_condition"] = {"bundle": bundle_c}

    # ---- trace-sum separation under F2 (FIX 2's own measured pathology) -------------------------
    ts_sep = {}
    for f2 in (0, 1):
        row = {}
        for arm in ARMS:
            sums = np.zeros((n_lemmas, mats[arm].shape[1]))
            np.add.at(sums, lemma_ids, mats[arm])
            sig = np.sign(sums)
            sig[sig == 0] = 1.0
            sig[np.all(sums == 0, axis=1)] = 0.0
            self_local = np.array([global_pos.get(l, -1) for l in lemma_list], dtype=np.int64)
            ctr = scl = None
            if f2:
                ctr = np.array([background[a][0] for a in anchors])
                scl = np.array([max(background[a][1], 1e-6) for a in anchors])
            r = _score_group(sig, self_local, amat, anorms, ctr, scl)
            row[arm] = round(float(np.mean(r["cos"] >= SENSE_MATCH_THRESH)), 6)
        ts_sep[f"f2={f2}"] = {"real": row["REAL"], "null": row[PRIMARY_NULL],
                              "separation": round(row["REAL"] - row[PRIMARY_NULL], 6)}
    print(f"[info] trace-sum separation {ts_sep}", flush=True)

    # ---- READ-OUT FIDELITY vs the ORGAN, per condition family (real_code_path, F.1) -------------
    fid_rng = np.random.default_rng(_seed_from("fidelity"))
    sample = fid_rng.choice(n_enc, size=min(200, n_enc), replace=False)
    elig_full = np.array([is_eligible_meaning(a) for a in anchors_all], dtype=bool)
    n_fid_mismatch = 0
    fid_checked = 0
    for (f1, f2) in ((0, 0), (0, 1), (1, 0), (1, 1)):
        rc = ReadoutConfig(anchor_background=background if f2 else None,
                           margin_z_min=(thresholds[("fixed", f2, stat_name)]["g_match"]
                                         if f1 else None),
                           margin_stat=stat_name)
        fs = fields[("fixed", "REAL", f2)]
        ret = _retained(fs, f1, "fixed", f2, "g_match")
        for i in sample.tolist():
            obj, cos = canonicalize_fast(target_lemmas[i], mats["REAL"][i], space,
                                         thresh=PBV_INFORMATIVE_MIN, eligible_mask=elig_full,
                                         readout=rc if (f1 or f2) else None)
            mine_anchor = anchors[int(fs.idx[i])] if fs.idx[i] >= 0 else target_lemmas[i]
            mine = mine_anchor if ret[i] else target_lemmas[i]
            if not f1 and not f2:
                mine = mine_anchor if fs.cos[i] >= PBV_INFORMATIVE_MIN else target_lemmas[i]
            if mine != obj or abs(float(fs.cos[i]) - float(cos)) > 1e-9:
                n_fid_mismatch += 1
            fid_checked += 1
    print(f"[gate] readout fidelity vs organ: {n_fid_mismatch}/{fid_checked} mismatches",
          flush=True)

    # ---- FROZEN-SPACE fidelity (FIX 3 through the ORGAN, growing regime) ------------------------
    n_freeze_mismatch = 0
    if snap_views:
        seg0 = sorted(snap_views)[0]
        sanch, smat = snaps[seg0]
        fspace = FrozenAnchorSpace(list(sanch), smat)
        smask = np.array([is_eligible_meaning(a) for a in sanch], dtype=bool)
        sv = snap_views[seg0]
        rows = [i for i in sample.tolist() if seg_of_enc[i] == seg0][:50]
        for i in rows:
            obj, _c = canonicalize_fast(target_lemmas[i], mats["REAL"][i], fspace,
                                        thresh=PBV_INFORMATIVE_MIN, eligible_mask=smask)
            r = _score_group(mats["REAL"][[i]], np.array([sv["pos"].get(target_lemmas[i], -1)]),
                             sv["mat"], sv["norms"], None, None)
            mine = sv["anchors"][int(r["idx"][0])] if r["idx"][0] >= 0 else target_lemmas[i]
            mine = mine if r["cos"][0] >= PBV_INFORMATIVE_MIN else target_lemmas[i]
            if mine != obj:
                n_freeze_mismatch += 1

    # ---- AMENDMENT C2 (disclosed; applied after SMOKE, before FULL) -----------------------------
    # The pre-registered META_RULE_AF check ("every condition's argmax digest must be distinct")
    # is MIS-SPECIFIED for this cell and fired at smoke on exactly the pairs the pre-reg had ALREADY
    # declared identical by construction (prereg sec 8, removed band #1: an F1 gate SELECTS
    # encounters, it cannot move an argmax). Amended to the two checks that can actually fail:
    #   (a) conditions differing in F2 or F3 -- the argmax-CHANGING fixes -- must have DISTINCT
    #       argmax digests (the real bit-identical-arm bug this rule exists to catch);
    #   (b) an F1-only pair must be BIT-IDENTICAL (positive invariant: if turning the gate on moved
    #       an argmax, the gate is doing something it must not do).
    # `prereg_literal_arms_differ` records the unamended outcome so the amendment cannot hide it.
    digests = {k: v["argmax_digest"] for k, v in results.items() if v["arm"] == "REAL"}
    distinct_digests = len(set(digests.values()))
    argmax_key = {}
    for k, v in results.items():
        if v["arm"] != "REAL":
            continue
        argmax_key[(v["regime"], v["f2"], v["f3"])] = argmax_key.get((v["regime"], v["f2"], v["f3"]), [])
        argmax_key[(v["regime"], v["f2"], v["f3"])].append(k)
    f1_invariant_violations = []
    for grp, keys in argmax_key.items():
        ds = {results[k]["argmax_digest"] for k in keys}
        if len(ds) != 1:
            f1_invariant_violations.append({"group": str(grp), "keys": keys})
    argmax_changing_digests = {grp: results[keys[0]]["argmax_digest"]
                               for grp, keys in argmax_key.items()}
    per_regime = {}
    for (reg, f2, f3), dg in argmax_changing_digests.items():
        per_regime.setdefault(reg, []).append(dg)
    f2f3_collisions = {reg: len(v) - len(set(v)) for reg, v in per_regime.items()}
    arms_differ_amended = (not f1_invariant_violations
                           and all(c == 0 for c in f2f3_collisions.values()))

    return {
        "conditions": results, "rctrl": rctrl, "deltas": deltas,
        "fix1": {"stat_chosen": stat_name, "stat_auc_selection_half": stat_auc,
                 "both_stats_reported": True,          # AMENDMENT C4
                 "thresholds": {f"{k[0]}|f2={k[1]}|{k[2]}": {kk: round(vv, 6)
                                                             for kk, vv in v.items()}
                                for k, v in thresholds.items()},
                 "legacy_retention_real": round(legacy_retention, 6),
                 "legacy_retention_null": round(
                     float(np.mean(fields[("fixed", PRIMARY_NULL, 0)].cos >= PBV_INFORMATIVE_MIN)),
                     6)},
        "fix2": {"background_arm_delta_mu_max": round(calib_delta_mu, 6),
                 "background_arm_delta_sd_max": round(calib_delta_sd, 6),
                 "top_hub_anchors_by_background_mean": hub_rank,
                 "trace_sum_separation": ts_sep},
        "argmax_agreement_BASE_vs_ALL": _agreement(
            fields[("fixed", "REAL", 0)].idx, fields[("fixed", "REAL", 1)].idx),
        "config": {"run_mode": run_mode, "upstream_metrics": up_metrics_path,
                   "upstream_ref_flip": ref_flip, "n_encounters": n_enc, "n_lemmas": n_lemmas,
                   "n_anchors_eligible": len(anchors), "n_segment_snapshots": len(snap_views),
                   "n_bootstrap": N_BOOTSTRAP, "informative_min": PBV_INFORMATIVE_MIN,
                   "sense_match_thresh": SENSE_MATCH_THRESH, "fpr_alpha": FPR_ALPHA,
                   "pbv_gamma": PBV_GAMMA, "pbv_init_strength": PBV_INIT_STRENGTH,
                   "pbv_abandon_strength": PBV_ABANDON_STRENGTH,
                   "sel_encounters": int(sel_enc.sum()), "eva_encounters": int(eva_enc.sum())},
        "integrity": {"verified_baseline_reproduces": bool(baseline_repro),
                      "baseline_flip_measured": round(base_flip, 6),
                      "baseline_flip_ci95": [round(base_ci[0], 6), round(base_ci[1], 6)],
                      "baseline_flip_upstream": ref_flip,
                      "growing_baseline_flip_measured": (
                          results["GROWING|BASE|REAL"]["flip_all"]
                          if "GROWING|BASE|REAL" in results else None),
                      "growing_baseline_flip_upstream": (
                          up.get("space_drift", {}).get("REAL", {}).get("snapshot_space_flip_rate")),
                      "prereg_literal_arms_differ_all_distinct": bool(
                          distinct_digests == len(digests)),
                      "f1_gate_moved_an_argmax": f1_invariant_violations,
                      "f2f3_digest_collisions_per_regime": f2f3_collisions,
                      "readout_fidelity_mismatches": n_fid_mismatch,
                      "readout_fidelity_checked": fid_checked,
                      "frozen_space_fidelity_mismatches": n_freeze_mismatch,
                      "f2_calibration_arm_delta_max": round(max(calib_delta_mu, calib_delta_sd), 6),
                      "n_units": n_units, "expected_n_units": EXPECTED_N_UNITS,
                      "cardinality_ok": n_units == EXPECTED_N_UNITS,
                      "arms_differ_verified": bool(arms_differ_amended),
                      "arms_differ_exempted": ["F1-only pairs (a gate cannot move an argmax; "
                                               "prereg sec 8 removed band #1) -- asserted IDENTICAL "
                                               "instead, which is the failable direction"],
                      "n_distinct_condition_digests": distinct_digests,
                      "n_condition_digests": len(digests),
                      "no_leak_violations": arm_info["no_leak_violations"],
                      "n_encounters_scored": arm_info["n_encounters_scored"],
                      "zero_norm_eligible_anchors": n_zero_norm_eligible},
    }


# =============================================================== verdict
def finalize(res: dict, backward_compat: dict) -> dict:
    integ = res["integrity"]
    C = res["conditions"]
    D = res["deltas"]
    blockers = []
    if not integ["verified_baseline_reproduces"]:
        blockers.append("BASELINE_REPRODUCTION_FAIL")
    if integ["readout_fidelity_mismatches"] != 0:
        blockers.append("READOUT_FIDELITY_FAIL")
    if integ["frozen_space_fidelity_mismatches"] != 0:
        blockers.append("FROZEN_SPACE_FIDELITY_FAIL")
    if integ["f2_calibration_arm_delta_max"] > CALIB_ARM_DELTA_MAX:
        blockers.append("F2_CALIBRATION_ARM_ASYMMETRY")
    if not integ["cardinality_ok"]:
        blockers.append("CARDINALITY_BREACH_META_RULE_H")
    if not integ["arms_differ_verified"]:
        blockers.append("META_RULE_AF_CONDITIONS_IDENTICAL")
    if integ["no_leak_violations"] != 0:
        blockers.append("NO_LEAK_VIOLATION")
    if not backward_compat.get("backward_compat_ok"):
        blockers.append("BACKWARD_COMPAT_FAIL")

    # ---- degenerate-collapse guard (can fail; refuses a win, never grants one) ------------------
    # AMENDMENT C1 (disclosed; applied after SMOKE, before FULL). The pre-registered guard was an
    # ABSOLUTE threshold (top1_share >= 0.10) calibrated on the FIXED regime's baseline
    # (top1_share 0.014851). At smoke it fired on the GROWING regime's own BASELINE
    # (top1_share 0.340853) and therefore on all eight GROWING conditions -- a guard that flags the
    # baseline cannot separate a fix-induced collapse from the regime's intrinsic concentration,
    # i.e. it can only fire vacuously (same defect class as the upstream cell's A1 ceiling guard,
    # and the F.4 "guard must fire against a NON-floor baseline" rule). Amended to a guard RELATIVE
    # TO EACH REGIME'S OWN BASELINE: a condition collapses iff its top1_share is >= 3x its regime's
    # BASE top1_share AND >= the absolute 0.10 edge, or it keeps < 1/3 of BASE's distinct argmaxes.
    # `prereg_literal_degenerate_collapse` records the unamended outcome.
    collapsed = []
    literal_collapsed = []
    for k, row in C.items():
        if row["arm"] != "REAL":
            continue
        con = row["concentration"]
        if con["top1_share"] >= COLLAPSE_TOP1 or con["n_distinct_argmax"] < COLLAPSE_MIN_DISTINCT:
            literal_collapsed.append(k)
        base_con = C.get(f"{row['regime']}|BASE|REAL", {}).get("concentration")
        if not base_con:
            continue
        rel_top1 = (con["top1_share"] >= max(COLLAPSE_TOP1, 3.0 * base_con["top1_share"]))
        rel_dist = (con["n_distinct_argmax"] < max(COLLAPSE_MIN_DISTINCT,
                                                   0.34 * base_con["n_distinct_argmax"]))
        if rel_top1 or rel_dist:
            collapsed.append(k)

    def g(key: str, field: str):
        return C[key][field] if key in C else None

    out: Dict[str, object] = {}
    # ---- PRIMARY: FIXED regime, ALL vs BASE on the operative (gated) flip rate ------------------
    base_g = g("FIXED|BASE|REAL", "flip_gated")
    rc = res["rctrl"].get("FIXED", {})
    # FIXED regime has no ALL (F3 is a no-op there): the FIXED-regime bundle is F1F2.
    all_key = "FIXED|ALL|REAL" if "FIXED|ALL|REAL" in C else "FIXED|F1F2|REAL"
    all_g = C[all_key]["flip_gated"]
    dd = D.get("FIXED|F1F2_vs_BASE")
    rctrl_margin = None
    if rc and all_g is not None and rc.get("flip_gated") is not None:
        rctrl_margin = round(rc["flip_gated"] - all_g, 6)
    drop = round(base_g - all_g, 6) if (base_g is not None and all_g is not None) else None
    ci_excl = bool(dd and (dd["delta_ci95"][1] < 0.0 or dd["delta_ci95"][0] > 0.0))
    if blockers:
        primary = "VOID"
    elif drop is None:
        primary = "VOID_NO_GATED_PAIRS"
    elif drop >= PRIMARY_DROP_HARD and ci_excl and (rctrl_margin or 0) >= RCTRL_MARGIN_HARD:
        primary = "READOUT_FIX_WORKS"
    elif drop >= PRIMARY_DROP_MIDDLE and (rctrl_margin or 0) >= RCTRL_MARGIN_MIDDLE:
        primary = "READOUT_FIX_PARTIAL"
    elif drop >= PRIMARY_DROP_HARD and not ci_excl:
        primary = "READOUT_FIX_PARTIAL"
    else:
        primary = "READOUT_FIX_INEFFECTIVE"

    # ---- per-fix attribution -------------------------------------------------------------------
    attribution = {}
    for fix, alone_key, loo_key in (("F1", "F1", "LOO_drop_F1"), ("F2", "F2", "LOO_drop_F2"),
                                    ("F3", "F3", "LOO_drop_F3")):
        # F1 / F2 are attributed in the FIXED regime (the one directly comparable to the 0.782962
        # baseline); F3 only exists in GROWING.
        regime = "GROWING" if fix == "F3" else "FIXED"
        alone = D.get(f"{regime}|{alone_key}_vs_BASE")
        loo = D.get(f"{regime}|{loo_key}")
        # KEY NAME FIX (2026-08-12, landed-VET sec 6): this block was emitted as
        # `leave_one_out_GROWING` for EVERY fix, but F1/F2 are attributed in FIXED (see `regime`
        # above), so the name misattributed the regime for 2 of the 3 fixes. The VALUES were always
        # correct and `regime_for_attribution` always disambiguated -- this is a mislabel, not a
        # mis-value -- but any consumer keying on the name would read FIXED numbers as GROWING.
        # The key is now regime-neutral; the regime is read from `regime_for_attribution`.
        rec: Dict[str, object] = {"regime_for_attribution": regime,
                                  "alone_vs_BASE": alone, "leave_one_out": loo}
        alone_eff = -(alone["delta_point"]) if alone else None       # positive = flip went DOWN
        loo_eff = (loo["delta_point"]) if loo else None              # positive = removing it hurt
        rec["alone_effect_flip_reduction"] = round(alone_eff, 6) if alone_eff is not None else None
        rec["leave_one_out_degradation"] = round(loo_eff, 6) if loo_eff is not None else None
        loo_ci_excl = bool(loo and loo["delta_ci95"][0] > 0.0)
        if loo_eff is not None and loo_eff >= LOO_LOAD_BEARING and loo_ci_excl:
            rec["status"] = "LOAD_BEARING"
        elif (alone_eff is not None and alone_eff < ALONE_NOT_JUSTIFIED
              and not loo_ci_excl):
            rec["status"] = "NOT_JUSTIFIED"
        else:
            rec["status"] = "INCONCLUSIVE"
        attribution[fix] = rec

    # F1-specific bands (the flip_all column is NOT evidence for F1 -- prereg sec 8 removed #1)
    f1_null_admission = g("FIXED|F1|" + PRIMARY_NULL, "retention")
    f1_real_retention = g("FIXED|F1|REAL", "retention")
    f1_real_ret_fpr = g("FIXED|F1|REAL", "retention_gfpr")
    if f1_null_admission is None:
        f1_verdict = "VOID"
    elif f1_null_admission <= F1_SELECTIVE_MAX:
        f1_verdict = "F1_SELECTIVE"
    elif f1_null_admission >= F1_BLIND_MIN:
        f1_verdict = "F1_BLIND"
    else:
        f1_verdict = "F1_MIDDLE"
    f1_enrich = ("F1_ENRICHED" if (f1_real_ret_fpr or 0) >= F1_ENRICH_MIN
                 else "F1_BLIND_FPR" if (f1_real_ret_fpr or 0) <= F1_ENRICH_FAIL else "F1_MIDDLE_FPR")

    # F2-specific
    f2_flip_all_drop = None
    if "FIXED|F2|REAL" in C:
        f2_flip_all_drop = round(C["FIXED|BASE|REAL"]["flip_all"] - C["FIXED|F2|REAL"]["flip_all"], 6)
    ts_after = res["fix2"]["trace_sum_separation"]["f2=1"]["separation"]
    if f2_flip_all_drop is None:
        f2_verdict = "VOID"
    elif f2_flip_all_drop >= F2_HELPS_MIN and ts_after >= 0.0:
        f2_verdict = "F2_HELPS"
    elif abs(f2_flip_all_drop) < F2_NULL_MAX:
        f2_verdict = "F2_NULL"
    else:
        f2_verdict = "F2_MIDDLE"

    # F3-specific (GROWING only; ceiling 0.0739 stated in prereg sec 8)
    f3_drop = None
    if "GROWING|BASE|REAL" in C and "GROWING|F3|REAL" in C:
        f3_drop = round(C["GROWING|BASE|REAL"]["flip_all"] - C["GROWING|F3|REAL"]["flip_all"], 6)
    f3_verdict = ("VOID" if f3_drop is None else
                  "F3_HELPS" if f3_drop >= F3_HELPS_MIN else
                  "F3_NULL" if abs(f3_drop) < F2_NULL_MAX else "F3_MIDDLE")

    # ---- SECONDARY: projected confirm rate ------------------------------------------------------
    base_conf = C["FIXED|BASE|REAL"]["pbv"]["confirm_rate_projected"]
    all_conf = C[all_key]["pbv"]["confirm_rate_projected"]
    projection_calibrated = (base_conf is not None
                             and abs(base_conf - PBV_OBSERVED_CONFIRM_RATE) <= PROJECTION_TOL)
    if all_conf is None:
        secondary = "VOID"
    elif not projection_calibrated:
        secondary = "CONFIRM_RATE_RELATIVE_ONLY"
    elif all_conf > CONFIRM_CLEARS:
        secondary = "CONFIRM_RATE_CLEARS_GATE"
    elif all_conf > CONFIRM_MOVES:
        secondary = "CONFIRM_RATE_MOVES"
    else:
        secondary = "CONFIRM_RATE_FLAT"

    verdict = ("HARD_FAIL" if blockers else
               "HARD_PASS" if primary == "READOUT_FIX_WORKS" else
               "MIDDLE_BAND" if primary == "READOUT_FIX_PARTIAL" else "HARD_FAIL")
    msg = (f"primary={primary} gated-flip BASE={base_g} -> {all_key.split('|')[1]}={all_g} "
           f"(drop={drop}, CI_excludes_0={ci_excl}, R-CTRL margin={rctrl_margin}) | "
           f"{f1_verdict}/{f1_enrich} null_admission={f1_null_admission} at real_retention="
           f"{f1_real_retention} (legacy null admission "
           f"{res['fix1']['legacy_retention_null']}) | {f2_verdict} flip_all drop={f2_flip_all_drop} "
           f"ts_sep {res['fix2']['trace_sum_separation']['f2=0']['separation']} -> {ts_after} | "
           f"{f3_verdict} growing drop={f3_drop} | secondary={secondary} confirm "
           f"{base_conf} -> {all_conf} (observed {PBV_OBSERVED_CONFIRM_RATE}) | "
           f"load_bearing={[k for k, v in attribution.items() if v['status'] == 'LOAD_BEARING']}")
    if collapsed:
        msg = f"DEGENERATE_COLLAPSE in {collapsed} (improvement REFUSED) | " + msg
        if verdict == "HARD_PASS":
            verdict = "MIDDLE_BAND"
    if blockers:
        msg = "BLOCKED: " + ",".join(blockers) + " | " + msg

    out.update({
        "verdict": verdict, "verdict_msg": msg, "summary": msg[:300],
        "primary_verdict": primary, "secondary_verdict": secondary,
        "fix_verdicts": {"F1_selectivity": f1_verdict, "F1_enrichment_gfpr": f1_enrich,
                         "F2": f2_verdict, "F3": f3_verdict},
        "attribution": attribution,
        "primary_numbers": {"base_flip_gated": base_g, "bundle_key": all_key,
                            "bundle_flip_gated": all_g, "drop": drop,
                            "paired_delta": dd, "rctrl_margin": rctrl_margin,
                            "rctrl": rc},
        "confirm_rate": {"baseline_projected": base_conf, "bundle_projected": all_conf,
                         "observed_pbv": PBV_OBSERVED_CONFIRM_RATE,
                         "projection_calibrated": projection_calibrated},
        "degenerate_collapse": collapsed,
        "prereg_literal_degenerate_collapse": literal_collapsed,
        "amendments": [
            "C1 collapse guard: the pre-registered ABSOLUTE top1_share >= 0.10 edge (calibrated on "
            "the FIXED baseline 0.014851) fired on the GROWING regime's own BASELINE at smoke, so "
            "it could only fire vacuously there; amended to a guard relative to each regime's own "
            "BASE. prereg_literal_degenerate_collapse records the unamended outcome.",
            "C2 arms-differ: the pre-registered 'all condition digests distinct' check fired at "
            "smoke on exactly the F1-only pairs the pre-reg had already declared identical by "
            "construction; amended to (a) F2/F3-differing conditions must differ, (b) F1-only pairs "
            "must be identical. prereg_literal_arms_differ_all_distinct records the unamended one.",
            "C3 threshold bug fix: the retention-matched F1 threshold now matches the legacy "
            "retention OF THE SAME regime and calibration (matching everything to the FIXED "
            "regime's made the GROWING F1 arms retain 1.000 at smoke -- a broken comparison).",
            "C4 statistic selection: BOTH z_top and margin are carried through to the reported "
            "results instead of selecting one by AUC, because both AUCs came back at chance at "
            "smoke; the AUC-chosen form is still the headline but the other is fully reported."],
        "blockers": blockers,
        "backward_compat": backward_compat,
        "bands": {"primary_drop_hard": PRIMARY_DROP_HARD, "primary_drop_middle": PRIMARY_DROP_MIDDLE,
                  "rctrl_margin_hard": RCTRL_MARGIN_HARD, "loo_load_bearing": LOO_LOAD_BEARING,
                  "alone_not_justified": ALONE_NOT_JUSTIFIED, "f1_selective_max": F1_SELECTIVE_MAX,
                  "f1_blind_min": F1_BLIND_MIN, "f1_enrich_min": F1_ENRICH_MIN,
                  "f2_helps_min": F2_HELPS_MIN, "f3_helps_min": F3_HELPS_MIN,
                  "confirm_clears": CONFIRM_CLEARS, "confirm_moves": CONFIRM_MOVES,
                  "collapse_top1": COLLAPSE_TOP1},
        "cannot_fail_declared_and_removed": [
            "F1's effect on flip_all is EXACTLY 0 by construction (a gate selects encounters, it "
            "does not move an argmax) -- excluded from F1's verdict, which rests on null admission "
            "at matched retention, flip_gated, and the projected confirm rate",
            "F3 in the FIXED regime is a no-op by construction -- not run, not reported",
            "'gated flip < ungated flip' cannot fail informatively (subsetting alone changes the "
            "pair population) -- replaced by the retention-matched R-CTRL random subset",
            "verified_baseline_reproduces is a HARNESS gate: it can only BLOCK, zero verdict weight"],
        "scope": ("READ-OUT STABILITY ONLY. Nothing here measures grounding QUALITY or whether any "
                  "anchor means anything; a better read-out is not better meanings. PBV was NOT "
                  "re-run -- the confirm rate is a PROJECTION of the Library.flag state machine "
                  "over re-scored encounters. WIRE STATUS: VET_PENDING."),
    })
    out.update(res)
    return out


# =============================================================== backward compatibility
def check_backward_compat(space: Optional[ConceptSpace] = None) -> dict:
    """BLOCKING gate (prereg sec 9): readout=None must be the pre-existing path, an existing
    foundation snapshot must still load, and an inactive ReadoutConfig must be a no-op."""
    rng = np.random.default_rng(_seed_from("compat"))
    sp = ConceptSpace(d=64)
    for name in ("alpha", "beta", "gamma", "delta", "also", "people"):
        sp.observe(name, rng.choice([-1.0, 1.0], size=64))
    n_same = 0
    for _ in range(200):
        x = rng.choice([-1.0, 1.0], size=64)
        a = canonicalize_fast("zzz", x, sp, thresh=0.30)
        b = canonicalize_fast("zzz", x, sp, thresh=0.30, readout=None)
        c = canonicalize_fast("zzz", x, sp, thresh=0.30, readout=ReadoutConfig())
        if a == b == c:
            n_same += 1
    # an existing foundation snapshot must still load
    snap = repo_path("data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl")
    n_rows = 0
    snap_ok = os.path.exists(snap)
    if snap_ok:
        with open(snap, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    json.loads(line)
                    n_rows += 1
    space_ok = True
    if space is not None:
        anchors, mat = space.anchor_matrix()
        space_ok = len(anchors) > 0 and mat.shape[0] == len(anchors)
    return {"readout_none_identical_n": n_same, "readout_none_identical_ok": n_same == 200,
            "foundation_snapshot_loaded": snap_ok, "foundation_snapshot_rows": n_rows,
            "cached_concept_space_rebuilds": space_ok,
            "backward_compat_ok": bool(n_same == 200 and snap_ok and n_rows > 0 and space_ok)}


# =============================================================== self-test
def self_test() -> dict:
    """Real substrate code path at tiny N (F.1) + live-signature binding (F.2) + the two things
    this cell adds that could silently be wrong: the ReadoutConfig semantics and the PBV
    projection's agreement with the ORGAN's own state machine."""
    exercised = set()

    for name, obj, kwargs in (
        ("canonicalize_fast", canonicalize_fast,
         {"new_lemma": "", "new_raw_sum": None, "space": None, "thresh": 0.3,
          "eligible_mask": None, "readout": None}),
        ("make_pbv_fns", make_pbv_fns, {"state": None, "readout": None, "freeze_episode": True}),
        ("ConceptSpace.freeze", ConceptSpace.freeze, {"self": None}),
        ("HDFactStore", HDFactStore, {"n_dim": 64, "seed": 1}),
        ("pbv_update_strength", pbv_update_strength, {"strength": 0.5, "confirmed": True}),
        ("process_sentence", process_sentence,
         {"state": None, "sentence": "", "episode_id": "", "pass_idx": 0}),
    ):
        inspect.signature(obj).bind_partial(**kwargs)
        exercised.add(name)

    # (1) the UPSTREAM harness must still be intact -- it is this cell's measurement apparatus
    up = upstream_self_test()
    assert up["selftest_ok"], "upstream harness self-test failed; measurement is not comparable"
    exercised.add("upstream_harness")

    # (2) real organs at tiny N
    store = HDFactStore(n_dim=256, seed=11,
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                              MEANING_RELATION: "FUNCTIONAL"}, use_index=True)
    state = ReadingLoopState(store=store)
    seed_known_words(state, ["water", "plant", "animal", "light", "food", "grow"],
                     source="selftest_seed")
    sents = ["the photosynthesis needs water and light to grow",
             "a plant uses photosynthesis with light and water",
             "the photosynthesis in a plant makes food from light",
             "an animal eats food that a plant made",
             "water and light drive photosynthesis in every plant"]
    for ci in range(2):
        for i, s in enumerate(sents):
            process_sentence(state, s, f"st_{ci}_{i}", pass_idx=ci)
        checkpoint(state, pass_idx=ci, source_tag="selftest", schema_thresh=SCHEMA_THRESH_FULL)
    assert state.space.anchors(), "self-test built an EMPTY ConceptSpace"
    exercised.update({"ReadingLoopState", "seed_known_words", "process_sentence", "checkpoint"})

    # (3) FIX 3: a frozen view must NOT track later growth, and must read like the live space did
    frozen = state.space.freeze()
    n_before = len(frozen.anchors())
    state.space.observe("zzz_new_anchor", np.ones(256))
    assert len(frozen.anchors()) == n_before, "FrozenAnchorSpace tracked a later mutation"
    assert len(state.space.anchors()) == n_before + 1, "live space did not grow"
    assert not hasattr(frozen, "observe"), "FrozenAnchorSpace must not expose a mutator"
    exercised.update({"ConceptSpace.freeze", "FrozenAnchorSpace"})

    # (4) FIX 1 / FIX 2 semantics through the ORGAN
    anchors_all, mat_all = frozen.anchor_matrix()
    emask = np.array([is_eligible_meaning(a) for a in anchors_all], dtype=bool)
    rng_p = np.random.default_rng(_seed_from("selftest_probe"))
    probe = rng_p.choice([-1.0, 1.0], size=256)                # NOT an anchor row (see below)
    hi = ReadoutConfig(margin_z_min=1e9)                       # nothing can stand that far out
    lo = ReadoutConfig(margin_z_min=-1e9)                      # everything passes
    o_hi, _ = canonicalize_fast("zzz", probe, frozen, thresh=0.30, eligible_mask=emask, readout=hi)
    o_lo, _ = canonicalize_fast("zzz", probe, frozen, thresh=0.30, eligible_mask=emask, readout=lo)
    assert o_hi == "zzz", "FIX 1 gate did not refuse at an unreachable threshold"
    assert o_lo != "zzz", "FIX 1 gate refused everything at a threshold nothing can fail"
    for stat in ("z_top", "margin"):
        canonicalize_fast("zzz", probe, frozen, thresh=0.30, eligible_mask=emask,
                          readout=ReadoutConfig(margin_z_min=0.0, margin_stat=stat))
    # FIX 2 must move the argmax in BOTH directions: crush the uncalibrated winner (a "hub" that
    # scores high against everything) and promote a specific loser. The probe is random, not an
    # anchor row -- crushing an anchor the probe IS would be a broken fixture, not a fixed read-out.
    w0, _c0 = canonicalize_fast("zzz", probe, frozen, thresh=-2.0, eligible_mask=emask)
    o_crush, _ = canonicalize_fast("zzz", probe, frozen, thresh=-2.0, eligible_mask=emask,
                                   readout=ReadoutConfig(anchor_background={w0: (0.99, 0.001)}))
    assert o_crush != w0, f"FIX 2 calibration did not penalise the hub anchor {w0!r}"
    loser = next(a for a, ok in zip(anchors_all, emask) if ok and a != w0)
    o_promo, _ = canonicalize_fast("zzz", probe, frozen, thresh=-2.0, eligible_mask=emask,
                                   readout=ReadoutConfig(anchor_background={loser: (-5.0, 0.001)}))
    assert o_promo == loser, f"FIX 2 calibration did not promote {loser!r} (got {o_promo!r})"
    exercised.update({"ReadoutConfig", "canonicalize_fast"})

    # (5) the batched scorer must equal the ORGAN under the SAME ReadoutConfig
    anchors, amat, anorms = _eligible_anchor_view(list(anchors_all), mat_all)
    pos = {a: i for i, a in enumerate(anchors)}
    rc = ReadoutConfig(anchor_background={a: (0.05, 0.2) for a in anchors[:5]},
                       margin_z_min=0.5, margin_stat="z_top")
    ctr = np.array([rc.anchor_background.get(a, (0.0, 1.0))[0] for a in anchors])
    scl = np.array([max(rc.anchor_background.get(a, (0.0, 1.0))[1], 1e-6) for a in anchors])
    rng = np.random.default_rng(_seed_from("selftest_equiv"))
    X = rng.choice([-1.0, 1.0], size=(25, 256))
    r = _score_group(X, np.full(25, -1, dtype=np.int64), amat, anorms, ctr, scl)
    for i in range(25):
        obj, cos = canonicalize_fast("zzz_absent", X[i], frozen, thresh=0.30,
                                     eligible_mask=emask, readout=rc)
        mine = anchors[int(r["idx"][i])] if r["z"][i] >= 0.5 else "zzz_absent"
        assert mine == obj, f"batched scorer disagrees with the organ at row {i}: {mine} vs {obj}"
        assert abs(float(r["cos"][i]) - float(cos)) < 1e-9, "cosine disagreement"
    exercised.add("batched_equals_organ")

    # (6) the PBV projection must match the ORGAN's own state machine on a fixture
    #     A A B A: propose A, confirm A (0.75), disconfirm (0.375), confirm? -> here obj A again.
    objs = np.array([0, 0, 1, 0, 1, 1, 1], dtype=np.int64)
    ret = np.ones(7, dtype=bool)
    li = np.zeros(7, dtype=np.int64)
    proj = pbv_project(objs, ret, li, 1)
    assert proj["n_propose"] == 1 and proj["n_confirm"] + proj["n_disconfirm"] == 6, proj
    s = PBV_INIT_STRENGTH
    exp_c = exp_d = exp_a = 0
    h = None
    for o in objs.tolist():
        if h is None:
            h = o
            continue
        if o == h:
            exp_c += 1
            s = pbv_update_strength(s, True, PBV_GAMMA)
        else:
            exp_d += 1
            s = pbv_update_strength(s, False, PBV_GAMMA)
            if s <= PBV_ABANDON_STRENGTH:
                exp_a += 1
                h = o
                s = PBV_INIT_STRENGTH
    assert (proj["n_confirm"], proj["n_disconfirm"], proj["n_abandon"]) == (exp_c, exp_d, exp_a), proj
    # an UNRETAINED encounter must produce no verdict at all (Medina 2011 uninformative)
    proj2 = pbv_project(objs, np.zeros(7, dtype=bool), li, 1)
    assert proj2["n_verdicts"] == 0 and proj2["n_propose"] == 0, proj2
    exercised.add("pbv_projection")

    # (7) AUC sanity: identical distributions -> 0.5; separated -> 1.0
    a1 = np.arange(100.0)
    assert abs(_auc(a1, a1.copy()) - 0.5) < 1e-9, "AUC of identical samples must be 0.5"
    assert _auc(a1 + 1000.0, a1) == 1.0, "AUC of fully separated samples must be 1.0"

    # (8) backward compatibility
    bc = check_backward_compat()
    assert bc["backward_compat_ok"], f"backward compatibility BROKEN: {bc}"
    exercised.add("backward_compat")

    # (9) source scan (F.5 / PROT-023 / META_RULE_J)
    scanmark = "SCAN" + "MARK"
    banned = ["list(" + "set(", "hash(", "except " + "BaseException", "except" + ":"]  # SCANMARK
    with open(os.path.abspath(__file__), encoding="utf-8") as f:
        lines = f.read().splitlines()
    for bad in banned:
        offenders = [ln for ln in lines
                     if bad in ln and scanmark not in ln and not ln.lstrip().startswith("#")
                     and "hashlib" not in ln]
        assert not offenders, f"F.5/META_RULE_J: forbidden construct {bad!r}: {offenders[:2]}"

    return {"real_code_path_exercised": sorted(exercised), "backward_compat": bc,
            "upstream_selftest_encounters": up["n_encounters_selftest"], "selftest_ok": True}


# =============================================================== main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full", "self_test"], default="full")
    ap.add_argument("--self-test", action="store_true", dest="self_test_flag")
    args = ap.parse_args()
    run_mode = "self_test" if args.self_test_flag else args.mode

    if run_mode == "self_test":
        st = self_test()
        print(json.dumps({k: v for k, v in st.items() if k != "backward_compat"}, indent=2),
              flush=True)
        sys.exit(0)

    output_dir = _output_dir(run_mode)
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, run_mode)
    t0 = time.time()
    st = self_test()
    res = measure(run_mode, output_dir)
    cached = load_pass_cache(_upstream_dir(run_mode))
    bc = check_backward_compat(cached[0] if cached else None)
    out = finalize(res, bc)
    out.update({"anchor_name": ANCHOR_NAME, "run_mode": run_mode,
                "elapsed_s": round(time.time() - t0, 2),
                "ts_iso": datetime.now(timezone.utc).isoformat(),
                "prereg": "preregs/2026-08-12_readout_fix_v1.md",
                "self_test": st, "wire_status": "VET_PENDING"})
    _atomic_json(os.path.join(output_dir, "metrics.json"), out)
    print(json.dumps({k: out[k] for k in ("verdict", "verdict_msg", "primary_verdict",
                                          "secondary_verdict", "fix_verdicts", "blockers",
                                          "degenerate_collapse", "elapsed_s")}, indent=2),
          flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _e:                       # NOT BaseException
        for _m in ("smoke", "full"):
            _d = _output_dir(_m)
            if os.path.isdir(_d):
                _write_crash_metrics(_d, _e)
        raise
