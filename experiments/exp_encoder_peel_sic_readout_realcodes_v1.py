"""Confidence-ordered peel/SIC readout on REAL two-head encoder STORE codes -- THE transfer test.

QUESTION (2026-07-08). On CLEAN synthetic near-orthogonal FHRR codes we proved the additive
superposition capacity wall is BEATABLE by a CONFIDENCE-ORDERED peel/SIC readout (matching
pursuit: global-argmax -> deflate the resolved codeword from the running residual -> repeat):
FLAT_PEEL ~1.0 at high J where flat-argmax cratered (exp_bundling_slot_peel_sic_v1, commit
c2f65e53d; theta-gamma SLOTTING was UNNECESSARY -- cancellation was the load-bearing half). The
open question: does that SAME readout fix the REAL two-head encoder STORE head, whose
superposition recall collapses (flat-argmax) SP 0.99@J3 -> 0.75@J5 -> 0.20@J8 at V=40000
(exp_encoder_twohead_decoupled_store_retrieval_v1, commit b2e26cd86, FULL HARD_FAIL). That
collapse is an ENCODER-EMBEDDING-GEOMETRY (correlation-law) artifact, NOT reproduced by clean
codes -- so whether confidence-ordered peel/SIC TRANSFERS from clean synthetic to REAL correlated
encoder codes is genuinely UNKNOWN and is the whole point of this cell.

WHAT THIS CELL TESTS. Source REAL store codes from the two-head module (reuse its _train_arm /
_make_forward / _encode_wta VERBATIM -- Gate D positive control: the store dictionary is produced
by the exact trained architecture that hit the wall). Then run a decisive multi-arm bundle-readout
comparison on those real WTA store codes, sweeping bundle size J:
  READOUT ARMS (PAIRED per trial -- identical member sets across all 3 arms):
    A. FLAT_ARGMAX    -- l2-normalized bundle sum, argmax-cosine top-J over the dict. THE current
                         failing readout == the two-head cell's _superposition_recall VERBATIM.
                         The negative control that MUST fail at high J (else smoke is saturation-
                         vacuous -> raise V/J).
    B. FLAT_PEEL_UNIT -- confidence-ordered greedy SIC / matching pursuit: global argmax -> DEFLATE
                         book[argmax] (UNIT weight: residual -= dict[ih]) from the running residual
                         -> repeat J times, never repick. EXACT transfer of the clean-code cell's
                         FLAT_PEEL readout (unit-weight deflation is principled here: the bundle is a
                         sum of unit-norm codes, each true member contributes weight exactly 1).
                         [HEADLINE CANDIDATE FIX]
    C. FLAT_PEEL_PROJ -- same greedy SIC but PROJECTION-weight deflation (residual -= (dict[ih].residual)
                         dict[ih]), classic matching pursuit. Tests whether correlated real codes need
                         magnitude-aware deflation (mechanism refinement) or the unit step suffices.
  Confidence-ordering is intrinsic to flat greedy MP (each round resolves the GLOBAL argmax = the
  most-confident codeword first); there is no separable "fixed-order" flat ablation (that ablation
  required SLOTS and was already settled in the clean-code cell: SLOT_PEEL_POWER >> SLOT_PEEL_FIXED).
  This cell's job is the TRANSFER question, not re-deriving the ordering dissociation.

  STORE SOURCES (each provides a real WTA store dict per seed):
    twohead_shared    the collapsing HEADLINE real code (shared trunk -> VICReg store head). PRIMARY.
    singlehead_native the strongest decorrelated single code (VICReg-only). breadth.
    native_untrained  random projection of BGE + WTA (free). breadth / correlation contrast.
  Bands are defined on the twohead_shared HEADLINE source; the other two are reported enrichment.

  Metric per (source,arm,J) = SET RECALL = mean over nq queries of
     |predicted top-J set intersect true member set| / J,  members sampled EXACTLY as the two-head
     _superposition_recall (rng.integers(0,V,(nq,J)), with replacement) so numbers are directly
     comparable to the cited 0.20@J8 collapse.

PILOT CALIBRATION (MEASURED@scratchpad this session; drives the bands, re-measured on disk by FULL):
  - twohead_shared store, SMOKE V=1500 N=2048: FLAT_ARGMAX 0.999@J3 0.974@J5 0.874@J8 0.696@J12;
    FLAT_PEEL_UNIT ~1.000 throughout (lift +0.30 @J12).  MEASURED@scratchpad/pilot_twohead_source.py
  - twohead_shared PREVIEW V=8000 N=2048: FLAT_ARGMAX 0.826@J8 0.565@J12; PEEL_UNIT ~0.997 (lift
    +0.43 @J12) -- lift GROWS with V/crowding.  MEASURED@scratchpad/pilot_twohead_source.py
  - native/vicreg V<=8000: PEEL_UNIT >= PEEL_PROJ at high J (unit-weight deflation is the correct
    step for a sum of unit codes; proj over-subtracts correlated energy).  MEASURED@scratchpad/pilot_peel_realcodes.py
  At production V=40000 both readouts degrade more (higher first-pick error under crowding) -- the
  FULL re-measures whether the large clean-code lift survives real-code crowding. HYPOTHESIZED bands
  below carry that headroom.

PRE-REG BANDS (HEADLINE source = twohead_shared; strictly-above-floor per META_RULE_L):
  DISCRIMINATOR-FIRES (META_RULE_AG): FLAT_ARGMAX at the DEEP J must have collapsed (<= 0.70) --
    else the regime is too easy, verdict = MIDDLE_BAND (raise J / V). At V=40000 argmax@J8 ~0.20.
  HARD_PASS (peel/SIC TRANSFERS -- bundling wall beaten on REAL codes): at the deep J (FULL J=8),
    best_peel = max(PEEL_UNIT, PEEL_PROJ) satisfies ALL of:
      lift    : best_peel - FLAT_ARGMAX >= 0.20
      abs     : best_peel               >= 0.60
      cv      : cv(best_peel) over seeds <= 0.15
    AND the lift PERSISTS at the max J (FULL J=12): best_peel - FLAT_ARGMAX >= 0.20.
  HARD_FAIL (peel does NOT transfer -> the real collapse is GEOMETRY not readout-order; honest+
    important negative): best_peel - FLAT_ARGMAX <= 0.05 at EVERY J in the high-J set (>=8).
  MIDDLE_BAND: a real but sub-bar lift (0.05 < lift < 0.20, or abs < 0.60, or lift does not persist
    to max J) -- ordering/deflation refinement may sharpen it; report to Research.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (3 readout arms -> distinct winner sets where argmax fails)
# - final_metrics_atomicity: tmp_replace (write_metrics / os.replace) + per-seed partials + resume
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: set-recall has no closed-form noise floor; feasibility from MEASURED pilot bands
#   (argmax floor ~0.20 known; peel headroom ~0.99 at V<=8k) -> PEEL_ABS_HP 0.60 reachable.
# - discriminator survives scale: SMOKE fires (argmax collapses at high J at smoke V; peel lifts) AND
#   the lift is an architectural readout property that GROWS with V (pilot V1500->V8000) -> option A+B.
# - baseline_in_band: FLAT_ARGMAX (the in-band control) 0.05 < recall < 0.95 at the deep J.
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds (one per-seed unit; each unit sweeps sources x J).
# - PAIRED trials: identical member sets across all 3 readout arms per (seed,source,J).
# - progress_logging: print_flush_true + _heartbeat.jsonl.
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (see docstring).
ASCII-only. No unicode. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

try:
    sys.stdout.reconfigure(line_buffering=True)  # unbuffered progress (section 17)
except Exception:  # noqa: BLE001
    pass

from experiments._seed_checkpoint import (
    get_output_dir, write_metrics, resumable_seeds, write_partial, aggregate_partials,
    assert_discriminator_fires, VacuousSmokeError,
)
# Source the REAL two-head STORE head from the exact cell that hit the wall (Gate D).
from experiments.exp_encoder_twohead_decoupled_store_retrieval_v1 import (
    _load_teacher, _train_arm, _make_forward, _encode_wta, _l2n, _resolve_device,
    ARMS as _TWOHEAD_ARMS,
)

ANCHOR_NAME = "encoder_peel_sic_readout_realcodes_v1"

RUN_MODE = "full"  # overridden in main() from argv; default full is the most defensive (section 16)

# ---- readout arms (the comparison) ----
READOUT_ARMS = ["FLAT_ARGMAX", "FLAT_PEEL_UNIT", "FLAT_PEEL_PROJ"]
PEEL_ARMS = ["FLAT_PEEL_UNIT", "FLAT_PEEL_PROJ"]

# ---- store sources (real code providers) ----
SOURCES = ["twohead_shared", "singlehead_native", "native_untrained"]
HEADLINE_SOURCE = "twohead_shared"

# ---- bands (HEADLINE source; HYPOTHESIZED@this prereg from pilot calibration) ----
ARGMAX_COLLAPSE_HI = 0.70   # discriminator-fires: FLAT_ARGMAX@deepJ must be <= this on headline
PEEL_LIFT_HP = 0.20         # best_peel - FLAT_ARGMAX at deepJ (and persist at maxJ)
PEEL_ABS_HP = 0.60          # best_peel absolute at deepJ
NO_TRANSFER_HI = 0.05       # HARD_FAIL if lift <= this at EVERY high J
CV_MAX = 0.15

# ---- regimes ----
# FULL: production V=40000 N=4096 (the two-head FULL regime); trained arms via _train_arm.
# SMOKE: reduced V/N/iters/B but SAME code path + high J so FLAT_ARGMAX collapses (discriminator
#        fires) -- SMOKE=FULL branch parity (META_RULE candidate). deep/max J chosen per regime so
#        the negative control has clearly cratered at the smoke's smaller V.
FULL_REGIME = dict(N=4096, H=512, V=40000, iters=800, B=8192, lr=1e-3, nq=600,
                   Js=[3, 5, 8, 12], deep_j=8, max_j=12)
SMOKE_REGIME = dict(N=2048, H=512, V=4000, iters=150, B=1024, lr=1e-3, nq=250,
                    Js=[5, 8, 12, 16], deep_j=12, max_j=16)
SELFTEST_REGIME = dict(N=1024, H=512, V=800, iters=60, B=400, lr=1e-3, nq=120,
                       Js=[8, 16], deep_j=16, max_j=16)

FULL_SEEDS = [7, 13, 19, 23, 29]
SMOKE_SEEDS = [7, 13]
SELFTEST_SEEDS = [7]

OUTPUT_DIR = get_output_dir(ANCHOR_NAME)


# ============================ readout decoders (torch, batched) ==============
def _to_t(x, device):
    import torch
    return torch.from_numpy(np.ascontiguousarray(x, dtype=np.float32)).to(device)


def _decode_argmax(bundle, dictT, J):
    """l2-normalized bundle, argmax-cosine top-J. bundle:(nq,N) dictT:(N,V) -> (nq,J) long."""
    import torch
    b = bundle / (bundle.norm(dim=1, keepdim=True) + 1e-9)   # match two-head _superposition_recall
    sims = b @ dictT
    return torch.topk(sims, J, dim=1).indices


def _decode_peel(bundle, dct, dictT, J, mode):
    """Confidence-ordered greedy SIC. dct:(V,N) unit-norm. mode: 'unit' | 'proj'. -> (nq,J) long."""
    import torch
    nq, V = bundle.shape[0], dct.shape[0]
    resid = bundle.clone()
    preds = torch.full((nq, J), -1, dtype=torch.long, device=bundle.device)
    picked = torch.zeros((nq, V), dtype=torch.bool, device=bundle.device)
    ar = torch.arange(nq, device=bundle.device)
    neg = torch.finfo(bundle.dtype).min
    for r in range(J):
        sims = resid @ dictT
        sims = sims.masked_fill(picked, neg)
        ih = torch.argmax(sims, dim=1)                        # global argmax = most-confident (order)
        preds[:, r] = ih
        picked[ar, ih] = True
        chosen = dct[ih]                                      # (nq,N) resolved codewords
        if mode == "unit":
            resid = resid - chosen                            # unit-weight deflation (clean-cell exact)
        else:
            coeff = (resid * chosen).sum(dim=1, keepdim=True)
            resid = resid - coeff * chosen                    # projection-weight (matching pursuit)
    return preds


def _decode(arm, bundle, dct, dictT, J):
    if arm == "FLAT_ARGMAX":
        return _decode_argmax(bundle, dictT, J)
    if arm == "FLAT_PEEL_UNIT":
        return _decode_peel(bundle, dct, dictT, J, "unit")
    if arm == "FLAT_PEEL_PROJ":
        return _decode_peel(bundle, dct, dictT, J, "proj")
    raise ValueError(f"unknown readout arm {arm!r}")


def _set_recall(preds_np, members_np, J):
    """Mean over queries of |pred set intersect member set| / J (members with replacement)."""
    nq = preds_np.shape[0]
    tot = 0.0
    for i in range(nq):
        tot += len(set(preds_np[i].tolist()) & set(members_np[i].tolist())) / J
    return tot / nq


# ============================ real store-code sourcing =======================
def _build_store_dict(source, bge, t_unit, seed, regime, device):
    """Return (dct_np (V,N) unit-norm WTA store dict, train_loss or None) for a real code source."""
    N = regime["N"]
    k = max(1, N // 32)                                       # 3.125% sparsity (production)
    if source == "native_untrained":
        gnp = np.random.default_rng(seed * 1000 + 7)
        Din = bge.shape[1]
        Wt = gnp.standard_normal((Din, N)).astype(np.float32) / np.sqrt(Din)
        z = bge @ Wt
        loss = None
    else:
        arm = next(a for a in _TWOHEAD_ARMS if a["name"] == source)
        np_params, loss = _train_arm(bge, t_unit, arm, seed, regime, device)
        store_fwd, _ret_fwd = _make_forward(arm, np_params, device)
        z = store_fwd(bge)                                    # store-head code (V,N)
    dct = _l2n(_encode_wta(z, k))                             # unit-norm WTA block code
    return dct.astype(np.float32), (None if loss is None else float(loss))


# ============================ per-seed measurement ===========================
def measure_seed(bge_full, t_unit_full, seed, regime, device):
    import torch
    rng = np.random.default_rng(seed)
    V, N = regime["V"], regime["N"]
    sel = rng.choice(bge_full.shape[0], size=min(V, bge_full.shape[0]), replace=False)
    bge = bge_full[sel].astype(np.float32)
    t_unit = t_unit_full[sel].astype(np.float32)
    Vr = bge.shape[0]
    Js = regime["Js"]

    src_res = {}
    for source in SOURCES:
        dct_np, train_loss = _build_store_dict(source, bge, t_unit, seed, regime, device)
        dct = _to_t(dct_np, device)                          # (V,N) on device
        dictT = dct.t().contiguous()                         # (N,V)
        recall = {a: {} for a in READOUT_ARMS}
        # PAIRED: identical member sets across all 3 readout arms per J.
        for J in Js:
            mrng = np.random.default_rng(seed * 100 + J)
            members = mrng.integers(0, Vr, size=(regime["nq"], J))     # with replacement (two-head parity)
            bundle = _to_t(dct_np[members].sum(axis=1), device)        # raw sum of unit codes (nq,N)
            for arm in READOUT_ARMS:
                preds = _decode(arm, bundle, dct, dictT, J).cpu().numpy()
                recall[arm][str(J)] = _set_recall(preds, members, J)
        # arm-winner hash at the deep J for arms-differ (headline-ish crowding)
        dj = regime["deep_j"]
        mrng = np.random.default_rng(seed * 100 + dj)
        members = mrng.integers(0, Vr, size=(regime["nq"], dj))
        bundle = _to_t(dct_np[members].sum(axis=1), device)
        hashes = {}
        for arm in READOUT_ARMS:
            preds = _decode(arm, bundle, dct, dictT, dj).cpu().numpy()
            hashes[arm] = hashlib.sha256(np.sort(preds, axis=1).tobytes()).hexdigest()
        src_res[source] = {"recall": recall, "arm_hashes": hashes, "train_loss": train_loss,
                           "store_dict_hash": hashlib.sha256(dct_np.tobytes()).hexdigest()}
        argx = recall["FLAT_ARGMAX"]
        pu = recall["FLAT_PEEL_UNIT"]
        print(f"[progress] seed={seed} source={source} "
              + " ".join(f"J{J}(AX={argx[str(J)]:.3f},PU={pu[str(J)]:.3f})" for J in Js), flush=True)
        del dct, dictT
        if device != "cpu":
            torch.cuda.empty_cache()
    return {"seed": int(seed), "V": int(Vr), "N": int(N), "sources": src_res}


# ============================ aggregation / verdict ==========================
def _mean(xs):
    xs = [v for v in xs if v is not None]
    return float(np.mean(xs)) if xs else None


def _cv(xs):
    a = np.asarray([v for v in xs if v is not None], dtype=np.float64)
    if a.size == 0:
        return 0.0
    mu = float(np.mean(a))
    return 0.0 if abs(mu) < 1e-9 else float(np.std(a) / abs(mu))


def _aggregate(per_seed, regime):
    Js = regime["Js"]
    agg = {"n_seeds": len(per_seed), "sources": {}}
    for source in SOURCES:
        arms = {}
        for arm in READOUT_ARMS:
            arms[arm] = {str(J): _mean([s["sources"][source]["recall"][arm][str(J)]
                                        for s in per_seed]) for J in Js}
        # best-peel per-J mean + per-seed cv at deep J
        best_peel = {}
        for J in Js:
            best_peel[str(J)] = max(arms["FLAT_PEEL_UNIT"][str(J)], arms["FLAT_PEEL_PROJ"][str(J)])
        dj = str(regime["deep_j"])
        # which peel arm wins at deep J (per-seed for cv)
        pu_dj = [s["sources"][source]["recall"]["FLAT_PEEL_UNIT"][dj] for s in per_seed]
        pp_dj = [s["sources"][source]["recall"]["FLAT_PEEL_PROJ"][dj] for s in per_seed]
        best_arm = "FLAT_PEEL_UNIT" if _mean(pu_dj) >= _mean(pp_dj) else "FLAT_PEEL_PROJ"
        best_dj_per_seed = pu_dj if best_arm == "FLAT_PEEL_UNIT" else pp_dj
        agg["sources"][source] = {"arms": arms, "best_peel": best_peel,
                                  "best_peel_arm_deepj": best_arm,
                                  "best_peel_deepj_cv": _cv(best_dj_per_seed),
                                  "best_peel_deepj_per_seed": best_dj_per_seed}
    return agg


def _classify(agg, regime):
    Js, dj, mj = regime["Js"], regime["deep_j"], regime["max_j"]
    high_js = [J for J in Js if J >= 8]
    H = agg["sources"][HEADLINE_SOURCE]
    ax = H["arms"]["FLAT_ARGMAX"]
    bp = H["best_peel"]

    argmax_deep = ax[str(dj)]
    lift_deep = bp[str(dj)] - argmax_deep
    lift_max = bp[str(mj)] - ax[str(mj)]
    peel_abs_deep = bp[str(dj)]
    cv_deep = H["best_peel_deepj_cv"]

    discriminator_fires = bool(argmax_deep <= ARGMAX_COLLAPSE_HI)
    ever_lifts = any((bp[str(J)] - ax[str(J)]) > NO_TRANSFER_HI for J in high_js)

    hp = bool(lift_deep >= PEEL_LIFT_HP and peel_abs_deep >= PEEL_ABS_HP
              and cv_deep <= CV_MAX and lift_max >= PEEL_LIFT_HP)

    cls = {
        "headline_source": HEADLINE_SOURCE,
        "deep_j": dj, "max_j": mj,
        "argmax_deep": argmax_deep, "peel_best_deep": peel_abs_deep,
        "lift_deep": lift_deep, "lift_max": lift_max,
        "peel_best_arm_deepj": H["best_peel_arm_deepj"], "cv_deep": cv_deep,
        "discriminator_fires": discriminator_fires, "ever_lifts": bool(ever_lifts),
        "lifts_per_J": {str(J): (bp[str(J)] - ax[str(J)]) for J in Js},
        "bands": {"ARGMAX_COLLAPSE_HI": ARGMAX_COLLAPSE_HI, "PEEL_LIFT_HP": PEEL_LIFT_HP,
                  "PEEL_ABS_HP": PEEL_ABS_HP, "NO_TRANSFER_HI": NO_TRANSFER_HI, "CV_MAX": CV_MAX},
    }
    if not discriminator_fires:
        cls["verdict"] = "MIDDLE_BAND_VACUOUS_DISCRIMINATOR"
    elif not ever_lifts:
        cls["verdict"] = "HARD_FAIL_PEEL_DOES_NOT_TRANSFER_GEOMETRY_NOT_READOUT"
    elif hp:
        cls["verdict"] = "HARD_PASS_PEEL_SIC_TRANSFERS_TO_REAL_CODES"
    else:
        cls["verdict"] = "MIDDLE_BAND_PARTIAL_LIFT"
    return cls


# ============================ IO / diagnostics ===============================
def _write_start_marker(output_dir, run_mode, expected_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_units, "host": platform.node()}
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, output_dir / "_start_marker.json")


def _heartbeat(output_dir, unit_idx, total_units, t0, extra):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total_units, "elapsed_s": time.perf_counter() - t0}
    row.update(extra)
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "run_mode": RUN_MODE, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, output_dir / "metrics.json")


# ============================ self-test ======================================
def self_test():
    """Scaffold-free witnesses: readout validity, telemetry-sensitivity, arms-differ, discriminator."""
    ok = True
    reg, device = SELFTEST_REGIME, "cpu"
    try:
        bge_full, t_unit_full, _src = _load_teacher(reg)
    except Exception as e:  # noqa: BLE001
        print(f"[self-test] FAIL cannot load teacher cache: {e}")
        return 1
    m = measure_seed(bge_full, t_unit_full, 7, reg, device)
    H = m["sources"][HEADLINE_SOURCE]["recall"]
    dj = str(reg["deep_j"])

    # 1) VALID READOUT: at the deep J, peel does NOT UNDERPERFORM argmax on real codes (transfer sanity)
    peel_ge_argmax = (max(H["FLAT_PEEL_UNIT"][dj], H["FLAT_PEEL_PROJ"][dj]) >= H["FLAT_ARGMAX"][dj] - 1e-9)
    ok &= peel_ge_argmax
    # 2) DISCRIMINATOR FIRES (saturation-vacuous guard): the negative control FLAT_ARGMAX must have
    #    COLLAPSED (<= ARGMAX_COLLAPSE_HI) at the deep J (else nothing to fix -> vacuous smoke).
    control_passed = bool(H["FLAT_ARGMAX"][dj] > ARGMAX_COLLAPSE_HI)
    try:
        assert_discriminator_fires(control_passed, control_name="FLAT_ARGMAX",
                                   headline_name="argmax_collapsed<=%.2f" % ARGMAX_COLLAPSE_HI,
                                   run_mode="self_test",
                                   extra=f"argmax@J{reg['deep_j']}={H['FLAT_ARGMAX'][dj]:.3f}")
        disc_ok = True
    except VacuousSmokeError as ve:
        disc_ok = False
        print(f"[self-test] VACUOUS: {ve}")
    ok &= disc_ok
    # 3) TELEMETRY-SENSITIVITY: two seeds move the headline discriminator (not analytically pinned)
    m13 = measure_seed(bge_full, t_unit_full, 13, reg, device)
    H13 = m13["sources"][HEADLINE_SOURCE]["recall"]
    moves = (H["FLAT_PEEL_UNIT"][dj] != H13["FLAT_PEEL_UNIT"][dj]) or \
            (H["FLAT_ARGMAX"][dj] != H13["FLAT_ARGMAX"][dj])
    ok &= moves
    # 4) ARMS DIFFER (META_RULE_AF): the 3 readout arms are NOT bit-identical at the deep J on headline
    hashes = m["sources"][HEADLINE_SOURCE]["arm_hashes"]
    arms_differ = len(set(hashes.values())) >= 2
    ok &= arms_differ
    # 5) SOURCES DIFFER: the store dicts from the 3 sources are distinct
    src_hashes = [m["sources"][s]["store_dict_hash"] for s in SOURCES]
    sources_differ = len(set(src_hashes)) == len(src_hashes)
    ok &= sources_differ

    print(f"[self-test] peel_ge_argmax={peel_ge_argmax}(AX@J{reg['deep_j']}={H['FLAT_ARGMAX'][dj]:.3f} "
          f"PU={H['FLAT_PEEL_UNIT'][dj]:.3f} PP={H['FLAT_PEEL_PROJ'][dj]:.3f}) disc_fires={disc_ok} "
          f"telemetry_moves={moves} arms_differ={arms_differ} sources_differ={sources_differ}")
    print(f"[self-test] {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ============================ run ============================================
def run(run_mode, device_want):
    global RUN_MODE
    RUN_MODE = run_mode
    t0 = time.perf_counter()
    if run_mode == "smoke":
        regime, seeds = SMOKE_REGIME, SMOKE_SEEDS
    else:
        regime, seeds = FULL_REGIME, FULL_SEEDS
    device = _resolve_device(device_want)
    expected_units = len(seeds)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    print(f"[start] anchor={ANCHOR_NAME} run_mode={run_mode} device={device} seeds={seeds} "
          f"regime={regime}", flush=True)

    bge_full, t_unit_full, cache_src = _load_teacher(regime)
    run_config = {"V": regime["V"], "N": regime["N"], "run_mode": run_mode}
    done, remaining = resumable_seeds(seeds, OUTPUT_DIR, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(seeds)} seeds done; running {remaining}", flush=True)

    for i, sd in enumerate(remaining):
        ts = time.perf_counter()
        res = measure_seed(bge_full, t_unit_full, sd, regime, device)
        res["elapsed_s"] = time.perf_counter() - ts
        res["run_mode"] = run_mode
        write_partial(OUTPUT_DIR, sd, res)
        _heartbeat(OUTPUT_DIR, len(done) + i + 1, expected_units, t0,
                   {"seed": sd, "elapsed_s": res["elapsed_s"]})
        print(f"[seed-done] seed={sd} elapsed={res['elapsed_s']:.1f}s", flush=True)

    per_seed = list(aggregate_partials(OUTPUT_DIR, seeds, run_config=run_config).values())
    n_units = len(per_seed)
    cardinality_ok = (n_units == expected_units)

    agg = _aggregate(per_seed, regime)
    cls = _classify(agg, regime)

    # in-band control check (META_RULE_AG): FLAT_ARGMAX at deep J on headline in (0.05, 0.95)
    H = agg["sources"][HEADLINE_SOURCE]["arms"]
    argmax_deep = H["FLAT_ARGMAX"][str(regime["deep_j"])]
    baseline_in_band = bool(0.05 < argmax_deep < 0.95)

    # arms-differ across the 3 readouts at deep J on headline (first seed)
    hd = per_seed[0]["sources"][HEADLINE_SOURCE]["arm_hashes"]
    arms_differ = len(set(hd.values())) >= 2

    # SMOKE discriminator gate (saturation-vacuous): the negative control FLAT_ARGMAX must have
    # COLLAPSED (<= ARGMAX_COLLAPSE_HI) at the deep J -- same condition _classify uses. If argmax
    # stayed high, the regime is too easy and peel cannot be exercised -> raise V/J. (Aligned with
    # discriminator_fires so smoke and FULL gate identically.)
    if run_mode == "smoke":
        control_passed = bool(argmax_deep > ARGMAX_COLLAPSE_HI)
        assert_discriminator_fires(control_passed, control_name="FLAT_ARGMAX",
                                   headline_name="argmax_collapsed<=%.2f" % ARGMAX_COLLAPSE_HI,
                                   run_mode=run_mode,
                                   extra=f"argmax@J{regime['deep_j']}={argmax_deep:.3f}")

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not arms_differ:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    else:
        verdict = cls["verdict"]

    # per-source one-liners for the message
    src_str = ""
    for s in SOURCES:
        a = agg["sources"][s]["arms"]
        bp = agg["sources"][s]["best_peel"]
        dj, mj = str(regime["deep_j"]), str(regime["max_j"])
        src_str += (f" | {s}: AX@J{dj}={a['FLAT_ARGMAX'][dj]:.3f} best_peel@J{dj}={bp[dj]:.3f} "
                    f"(lift={bp[dj]-a['FLAT_ARGMAX'][dj]:+.3f}) @J{mj} lift="
                    f"{bp[mj]-a['FLAT_ARGMAX'][mj]:+.3f}")

    verdict_msg = (
        f"{verdict} | TRANSFER TEST: does the CLEAN-code confidence-ordered peel/SIC readout fix the "
        f"REAL two-head STORE head collapse? HEADLINE source={HEADLINE_SOURCE} deep_J={regime['deep_j']}: "
        f"FLAT_ARGMAX={cls['argmax_deep']:.3f} (collapsed<={ARGMAX_COLLAPSE_HI}:{cls['discriminator_fires']}) "
        f"-> best_peel={cls['peel_best_deep']:.3f} ({cls['peel_best_arm_deepj']}) lift={cls['lift_deep']:+.3f} "
        f"(HP needs >=+{PEEL_LIFT_HP} AND abs>={PEEL_ABS_HP} AND cv<={CV_MAX}; cv={cls['cv_deep']:.3f}); "
        f"lift persists @J{regime['max_j']}={cls['lift_max']:+.3f}. ever_lifts={cls['ever_lifts']}. "
        f"cache={cache_src}." + src_str + " INTERPRETATION: "
        + ("confidence-ordered peel/SIC TRANSFERS from clean synthetic codes to REAL correlated "
           "encoder store codes -> the two-head superposition-recall wall is a READOUT limit, beatable "
           "by matching-pursuit deflation; the store head does NOT need re-training, only a better readout."
           if verdict == "HARD_PASS_PEEL_SIC_TRANSFERS_TO_REAL_CODES" else
           ("peel/SIC gives NO material lift on real codes -> the two-head collapse is an ENCODER-"
            "EMBEDDING-GEOMETRY (correlation-law) artifact, NOT a readout-order problem; a better "
            "readout cannot rescue it -> the fix must be in the STORE-CODE GEOMETRY (decorrelation/"
            "training), an honest and important negative."
            if verdict == "HARD_FAIL_PEEL_DOES_NOT_TRANSFER_GEOMETRY_NOT_READOUT" else
            ("peel/SIC lifts real-code recall but does not clear the full HARD_PASS bar (lift/abs/"
             "persistence) -> a real but partial readout gain; deflation/ordering refinement (proj vs "
             "unit, adaptive stopping) may sharpen it. Report to Research."
             if verdict.startswith("MIDDLE_BAND") else
             "cardinality/arms-differ structural failure; see verdict tag."))))

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": f"{verdict}: peel/SIC readout transfer to real two-head store codes ({run_mode})",
        "run_mode": run_mode, "device": device,
        "elapsed_s": time.perf_counter() - t0,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "cache_source": cache_src,
        "cardinality_ok": cardinality_ok, "expected_n_units": expected_units, "n_units": n_units,
        "arms_differ_verified": bool(arms_differ), "baseline_in_band": baseline_in_band,
        "classification": cls, "agg": agg,
        "regime": regime, "seeds": seeds,
        "readout_arms": READOUT_ARMS, "sources": SOURCES, "headline_source": HEADLINE_SOURCE,
        "bands": {"ARGMAX_COLLAPSE_HI": ARGMAX_COLLAPSE_HI, "PEEL_LIFT_HP": PEEL_LIFT_HP,
                  "PEEL_ABS_HP": PEEL_ABS_HP, "NO_TRANSFER_HI": NO_TRANSFER_HI, "CV_MAX": CV_MAX},
    }
    write_metrics(OUTPUT_DIR, metrics, per_seed)
    print("[done] " + verdict_msg, flush=True)
    print(f"[metrics] -> {OUTPUT_DIR / 'metrics.json'}", flush=True)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["full", "smoke", "self_test"], default="full")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _ = ap.parse_known_args()
    if args.self_test or args.run_mode == "self_test":
        raise SystemExit(self_test())
    mode = "smoke" if (args.smoke or args.run_mode == "smoke") else "full"
    run(mode, args.device)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
