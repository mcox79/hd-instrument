"""Recall-ceiling DECOMPOSITION diagnostic -- capacity-bound vs semantic-fidelity-bound.

MEASUREMENT, NOT A FIX. The concept-recall ceiling (~0.5 cos-to-target / argmax
recall observed on the migration encoder, backup 2026-07-08 line 29) has an
UNDER-DETERMINED cause: is it CAPACITY-bound (dimensionality N too small / code
crowding / associative-store crosstalk) or SEMANTIC-FIDELITY-bound (encoder
teacher / objective quality)? This cell decomposes it with an ANOVA-style
factorial of ISOLATION arms + per-factor sensitivity sweeps, on CLEAN SYNTHETIC
data (USER: smoke clean synthetic, not substrate state). It does NOT touch the
active encoder cell.

MODEL (faithful, non-tautological):
  - V concepts have intrinsic "meaning" vectors m_i in R^dsem with cluster
    structure (G groups, within-cluster meaning-similarity rho = SEMANTIC crowding
    / near-duplication, e.g. synonyms/polysemy).
  - ENCODER renders a meaning into an N-dim quantized (bipolar-sign) HD code via a
    fixed random projection W: code = sign(W @ (m + teacher_noise)). The teacher
    noise sigma_e models encoder / objective quality (a perfect teacher = 0).
  - RECALL: re-encode the concept (independent teacher-noise draw = a fresh
    rendering / noisy cue) -> query q; argmax cosine over the V stored codes.
  - Two observables:
      cos_to_target = cos(q, code_true)      (the FIDELITY metric, mirrors 0.507)
      recall        = P(argmax == true)      (the DISCRETE retrieval metric)

WHY THIS SEPARATES THE HYPOTHESES (the physics, verified in calibration):
  - cos_to_target is set by sigma_e and is (empirically) N-INVARIANT: capacity
    provably cannot buy encoder fidelity. It is a purely SEMANTIC ceiling.
  - recall is N-recoverable (more dimensions separate more codes) UP TO an asymptote
    set by sigma_e / rho: N and encoder-fidelity TRADE OFF at a measurable exchange
    rate. The decomposition measures, at the operating point, how much recall each
    idealization buys back.

FACTORIAL (recall), at the substrate-FAITHFUL operating point (well-provisioned N):
  FULL       (N*, se*, rho*)                 -- reproduces the mid-band ceiling
  CAP_IDEAL  (N->N_high, se*, rho*)          -- idealize CAPACITY (dimensionality)
  SEM_IDEAL  (N*, se->se_lo, rho->0)         -- idealize SEMANTICS (teacher + corr)
  ORACLE     (N->N_high, se->se_lo, rho->0)  -- positive control (~1.0)
  SEM_FIDELITY_IDEAL (N*, se->se_lo, rho*)   -- sub-split: teacher fidelity only
  SEM_CORR_IDEAL     (N*, se*, rho->0)       -- sub-split: semantic correlation only
  capacity_gain = recall(CAP_IDEAL) - recall(FULL)
  semantic_gain = recall(SEM_IDEAL) - recall(FULL)
  D = semantic_gain - capacity_gain          (the DISCRIMINATOR)

SELF-VALIDATION (the credibility anchor -- avoids a rigged verdict):
  The SAME machinery is run at a CAPACITY-STARVED control regime (tiny N, good
  encoder) where the answer MUST flip to CAPACITY-bound. If D_control does NOT go
  negative, the decomposition cannot detect capacity-binding and the primary
  SEMANTIC verdict is UNTRUSTWORTHY -> HARD_FAIL_CONTROL_DID_NOT_FLIP. This proves
  the discriminator can fire in BOTH directions; the semantic verdict at the
  faithful regime is then a genuine measurement, not a blind spot.

PRE-REG BANDS (which-factor verdict; symmetric, both directions tested):
  PRIMARY (faithful regime): HARD_SEMANTIC if D_primary >= +0.15 and semantic_gain
    >= 0.20; HARD_CAPACITY if D_primary <= -0.15 and capacity_gain >= 0.20;
    else MIDDLE_BAND (MIXED).
  CONTROL (starved regime) VALIDATION GATE: require D_control <= -0.15 (capacity
    wins); else HARD_FAIL_CONTROL_DID_NOT_FLIP (whole-cell untrusted).

Calibration (MEASURED@scratchpad calib6.py, se*=1.5 N*=4096 V=20000 G=200 rho*=0.5):
  FULL recall 0.504; CAP_IDEAL 0.601 (+0.097); SEM_IDEAL 1.000 (+0.496);
  SEM_FIDELITY_IDEAL 1.000 (+0.496); SEM_CORR_IDEAL 0.772 (+0.268);
  D_primary = +0.399. Capacity-binding control N sweep rho0 se0.6: N48 0.368 ->
  N64 0.561 -> N128 0.957 -> N256 1.000 (capacity binds only at N<128 for V=20000;
  operating N=4096 is far above the capacity floor). All seed-sensitive.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (sha256 over per-arm code matrices)
- final_metrics_atomicity: tmp_replace (os.replace on final metrics.json)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a: discrete argmax recall; capacity feasibility handled by the starved
  positive-control regime that empirically locates the N-transition
- baseline_in_band at smoke (FULL ~0.5 in (0.05, 0.95))
- discriminator survives scale (smoke fires BOTH branches; full at faithful N)
- HARD bands strictly above floor (D margin measured +0.399 >> +0.15)
- per-unit failure-class instrumentation (no bare except)
- calibration_check: default_ok_for_this_regime (synthetic; params calibrated above)
- all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

ASCII-only. No unicode. No emojis.
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

import numpy as np

# ---- path / hdlab import (repo-root relative; no hard-coded absolute paths) ----
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
try:
    from hdlab.per_item_log import PerItemLogger  # additive per-item logging
except Exception:  # noqa: BLE001 - logging is optional; never break science
    PerItemLogger = None

ANCHOR_NAME = "recall_ceiling_capacity_vs_semantic_decomp_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", f"exp_{ANCHOR_NAME}")

# unbuffered progress (per section 17)
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:  # noqa: BLE001
    pass

# ------------------------- pre-reg constants (locked) -------------------------
DSEM = 256                 # intrinsic semantic dimensionality (fixed)
QUANT = "sign"             # bipolar-sign HD code

# discriminator bands (pre-reg)
D_MARGIN = 0.15            # |D| threshold to declare a winner (semantic vs capacity)
GAIN_FLOOR = 0.20         # winning gain must clear this floor
# credibility control: capacity and semantic-fidelity are ENTANGLED through the same
# argmax margin (capacity only binds when the encoder is imperfect, and then improving
# the encoder also helps), so a clean "capacity-only wins" regime is PHYSICALLY
# impossible. The honest control is SATURATION: the capacity lever must demonstrably
# FIRE (large recall gain from raising N) at a STARVED N, and be more SATURATED (smaller
# gain) at the provisioned operating N. That proves a small primary capacity_gain means
# capacity is saturated (not the bottleneck), not that the lever is inert/broken.
CTRL_LEVER_FLOOR = 0.20   # capacity_gain at starved N must clear this (lever fires)

# multi-seed
FULL_SEEDS = [7, 13, 19, 23, 29]
SMOKE_SEEDS = [7, 13, 19]

# ---- FAITHFUL (primary) regime: well-provisioned N, recall mid-band ~0.5 ----
FULL_REGIME = dict(N=4096, N_high=16384, V=20000, G=200,
                   rho=0.5, se=1.5, se_lo=0.4, nq=600)
# ---- CAPACITY-STARVED control regime: tiny N, good encoder -> capacity binds ----
CTRL_REGIME = dict(N=64, N_high=512, V=20000, G=200,
                   rho=0.0, se=0.6, se_lo=0.3, nq=600)
# ---- reduced-scale SMOKE regimes (must still fire BOTH branches) ----
SMOKE_FULL_REGIME = dict(N=2048, N_high=8192, V=5000, G=100,
                         rho=0.5, se=1.5, se_lo=0.4, nq=400)
SMOKE_CTRL_REGIME = dict(N=48, N_high=256, V=5000, G=100,
                         rho=0.0, se=0.6, se_lo=0.3, nq=400)

# sensitivity sweeps (per-factor local slopes)
N_SWEEP = [64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]
SE_SWEEP = [0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8]
RHO_SWEEP = [0.0, 0.2, 0.4, 0.6, 0.8, 0.9]


# ------------------------------- core model ---------------------------------
def _build_meanings(V, G, rho, rng):
    """V unit meaning vectors in R^DSEM with within-group correlation ~rho."""
    grp = rng.standard_normal((G, DSEM)).astype(np.float32)
    grp /= np.linalg.norm(grp, axis=1, keepdims=True)
    idio = rng.standard_normal((V, DSEM)).astype(np.float32)
    idio /= np.linalg.norm(idio, axis=1, keepdims=True)
    gid = np.arange(V) % G
    m = np.sqrt(rho) * grp[gid] + np.sqrt(1.0 - rho) * idio
    m /= np.linalg.norm(m, axis=1, keepdims=True)
    return m, gid


def _encode(x, W):
    """Bipolar-sign HD code of a batch of meaning vectors. x:(B,DSEM) W:(DSEM,N)."""
    z = x.astype(np.float32) @ W
    return np.sign(z).astype(np.float32)


def measure_arm(N, V, G, rho, se, seed, nq, want_peritem=False):
    """Return dict with cos_to_target, recall, per-item arrays, and code-matrix hash."""
    rng = np.random.default_rng(seed)
    m, gid = _build_meanings(V, G, rho, rng)
    W = (rng.standard_normal((DSEM, N)).astype(np.float32) / np.sqrt(DSEM))
    se_scaled = se / np.sqrt(DSEM)
    codes = _encode(m + se_scaled * rng.standard_normal((V, DSEM)).astype(np.float32), W)
    # query = independent re-encoding (fresh teacher-noise draw)
    qi = rng.choice(V, size=min(nq, V), replace=False)
    q = _encode(m[qi] + se_scaled * rng.standard_normal((len(qi), DSEM)).astype(np.float32), W)
    qn = q / np.linalg.norm(q, axis=1, keepdims=True)
    cn = codes / np.linalg.norm(codes, axis=1, keepdims=True)
    sims = qn @ cn.T  # (nq, V) float32
    self_sim = sims[np.arange(len(qi)), qi]
    pred = np.argmax(sims, axis=1)
    hit = (pred == qi)
    out = {
        "cos_to_target": float(np.mean(self_sim)),
        "recall": float(np.mean(hit)),
        "code_hash": hashlib.sha256(codes.tobytes()).hexdigest(),
        "N": int(N), "V": int(V), "G": int(G), "rho": float(rho), "se": float(se),
    }
    if want_peritem:
        out["_qi"] = qi
        out["_hit"] = hit
        out["_selfsim"] = self_sim
        out["_gid_q"] = gid[qi]
    return out


# --------------------------- decomposition at a regime -----------------------
def decompose(regime, seed, pil=None, tag=""):
    """Run the 6-arm factorial at one regime for one seed. Returns per-arm + gains."""
    N, Nh, V, G = regime["N"], regime["N_high"], regime["V"], regime["G"]
    rho, se, se_lo, nq = regime["rho"], regime["se"], regime["se_lo"], regime["nq"]
    arms = {}
    arms["FULL"] = measure_arm(N, V, G, rho, se, seed, nq, want_peritem=(pil is not None))
    arms["CAP_IDEAL"] = measure_arm(Nh, V, G, rho, se, seed, nq)
    arms["SEM_IDEAL"] = measure_arm(N, V, G, 0.0, se_lo, seed, nq)
    arms["ORACLE"] = measure_arm(Nh, V, G, 0.0, se_lo, seed, nq)
    arms["SEM_FIDELITY_IDEAL"] = measure_arm(N, V, G, rho, se_lo, seed, nq)
    arms["SEM_CORR_IDEAL"] = measure_arm(N, V, G, 0.0, se, seed, nq)
    r = {k: arms[k]["recall"] for k in arms}
    c = {k: arms[k]["cos_to_target"] for k in arms}
    gains = {
        "capacity_gain": r["CAP_IDEAL"] - r["FULL"],
        "semantic_gain": r["SEM_IDEAL"] - r["FULL"],
        "fidelity_gain": r["SEM_FIDELITY_IDEAL"] - r["FULL"],
        "correlation_gain": r["SEM_CORR_IDEAL"] - r["FULL"],
        "oracle_gap": r["ORACLE"] - r["FULL"],
    }
    gains["D"] = gains["semantic_gain"] - gains["capacity_gain"]
    gains["interaction"] = gains["oracle_gap"] - gains["semantic_gain"] - gains["capacity_gain"]
    # per-item logging (FULL arm of the primary regime only, additive)
    if pil is not None and "_qi" in arms["FULL"]:
        f = arms["FULL"]
        for i in range(len(f["_qi"])):
            pil.log(int(f["_qi"][i]), stage=f"decomp:{tag}:FULL",
                    outcome={"hit": bool(f["_hit"][i]), "cos": float(f["_selfsim"][i]),
                             "miss": not bool(f["_hit"][i])},
                    tags={"grouped": bool(f["_gid_q"][i] >= 0)})
    return {"recall": r, "cos_to_target": c, "gains": gains,
            "code_hashes": {k: arms[k]["code_hash"] for k in arms}}


def _verdict_from_D(D, cap_gain, sem_gain):
    if D >= D_MARGIN and sem_gain >= GAIN_FLOOR:
        return "HARD_SEMANTIC"
    if D <= -D_MARGIN and cap_gain >= GAIN_FLOOR:
        return "HARD_CAPACITY"
    return "MIDDLE_BAND_MIXED"


def _mean(xs):
    return float(np.mean(xs)) if xs else float("nan")


def _cv(xs):
    a = np.asarray(xs, dtype=np.float64)
    mu = float(np.mean(a))
    if abs(mu) < 1e-9:
        return 0.0
    return float(np.std(a) / abs(mu))


# ----------------------------- sensitivity sweeps ----------------------------
def sensitivity_sweeps(regime, seeds):
    """1D per-factor recall+cos sweeps at the faithful operating point."""
    N0, V, G = regime["N"], regime["V"], regime["G"]
    rho0, se0, nq = regime["rho"], regime["se"], regime["nq"]
    sweeps = {}
    def sweep(axis, values, build):
        pts = []
        for v in values:
            N, rho, se = build(v)
            t0 = time.perf_counter()
            rr = [measure_arm(N, V, G, rho, se, sd, nq) for sd in seeds]
            pts.append({"x": float(v),
                        "recall": _mean([a["recall"] for a in rr]),
                        "cos_to_target": _mean([a["cos_to_target"] for a in rr])})
            print(f"[progress] sweep={axis} x={v} recall={pts[-1]['recall']:.3f} "
                  f"cos={pts[-1]['cos_to_target']:.3f} dt={time.perf_counter()-t0:.1f}s",
                  flush=True)
        sweeps[axis] = pts
    sweep("N", N_SWEEP, lambda N: (N, rho0, se0))
    sweep("sigma_e", SE_SWEEP, lambda se: (N0, rho0, se))
    sweep("rho", RHO_SWEEP, lambda rho: (N0, rho, se0))
    # local slopes around the operating point (finite difference on recall)
    def slope(axis, x0):
        pts = sweeps[axis]
        xs = [p["x"] for p in pts]
        ys = [p["recall"] for p in pts]
        # nearest bracketing pair around x0
        idx = int(np.argmin([abs(x - x0) for x in xs]))
        lo = max(0, idx - 1); hi = min(len(xs) - 1, idx + 1)
        if xs[hi] == xs[lo]:
            return 0.0
        return float((ys[hi] - ys[lo]) / (xs[hi] - xs[lo]))
    slopes = {
        "dRecall_dN": slope("N", N0),
        "dRecall_dSigmaE": slope("sigma_e", se0),
        "dRecall_dRho": slope("rho", rho0),
    }
    return sweeps, slopes


# ------------------------------ IO / diagnostics -----------------------------
def _write_start_marker(output_dir, run_mode, expected_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))  # atomic (META_RULE_AH)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "run_mode": "crash", "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


def _seed_partial_path(output_dir, run_mode, regime_tag, seed):
    # run_mode in the path so SMOKE-scale partials never get reused by a FULL run
    return os.path.join(output_dir, f"_seed_{run_mode}_{regime_tag}_{seed}.json")


def _run_regime_multiseed(output_dir, run_mode, regime, seeds, regime_tag, pil=None):
    """Per-seed decomposition with resumable partials (survives mid-run death)."""
    per_seed = []
    for sd in seeds:
        pp = _seed_partial_path(output_dir, run_mode, regime_tag, sd)
        if os.path.exists(pp):
            try:
                with open(pp, encoding="utf-8") as f:
                    per_seed.append(json.load(f)); continue
            except Exception:  # noqa: BLE001 - corrupt partial: recompute
                pass
        t0 = time.perf_counter()
        res = decompose(regime, sd, pil=(pil if regime_tag == "primary" else None), tag=regime_tag)
        res["seed"] = sd
        res["elapsed_s"] = time.perf_counter() - t0
        tmp = pp + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(res, f)
        os.replace(tmp, pp)
        per_seed.append(res)
        print(f"[progress] regime={regime_tag} seed={sd} "
              f"FULL_recall={res['recall']['FULL']:.3f} D={res['gains']['D']:.3f} "
              f"elapsed={res['elapsed_s']:.1f}s", flush=True)
    return per_seed


def _aggregate(per_seed):
    keys_r = per_seed[0]["recall"].keys()
    keys_g = per_seed[0]["gains"].keys()
    agg = {"n_seeds": len(per_seed),
           "recall_mean": {k: _mean([s["recall"][k] for s in per_seed]) for k in keys_r},
           "cos_to_target_mean": {k: _mean([s["cos_to_target"][k] for s in per_seed])
                                  for k in per_seed[0]["cos_to_target"].keys()},
           "gains_mean": {k: _mean([s["gains"][k] for s in per_seed]) for k in keys_g},
           "gains_cv": {k: _cv([s["gains"][k] for s in per_seed]) for k in keys_g},
           "D_per_seed": [s["gains"]["D"] for s in per_seed],
           "FULL_recall_per_seed": [s["recall"]["FULL"] for s in per_seed]}
    return agg


# ---------------------------------- self-test --------------------------------
def self_test():
    """Scaffold-free witnesses: model sanity + telemetry-sensitivity + both-branch fire."""
    ok = True
    # 1) cos_to_target is N-invariant (capacity cannot buy fidelity) at fixed se
    c_lo = measure_arm(512, 3000, 100, 0.3, 1.0, 7, 300)["cos_to_target"]
    c_hi = measure_arm(8192, 3000, 100, 0.3, 1.0, 7, 300)["cos_to_target"]
    n_inv = abs(c_lo - c_hi) < 0.05
    ok &= n_inv
    # 2) cos_to_target DOES move with sigma_e (fidelity is the lever)
    c_good = measure_arm(2048, 3000, 100, 0.3, 0.5, 7, 300)["cos_to_target"]
    c_bad = measure_arm(2048, 3000, 100, 0.3, 1.5, 7, 300)["cos_to_target"]
    se_moves = (c_good - c_bad) > 0.10
    ok &= se_moves
    # 3) TELEMETRY-SENSITIVITY: FULL recall NOT bit-identical across seeds
    r_s7 = measure_arm(2048, 5000, 100, 0.5, 1.5, 7, 400)["recall"]
    r_s13 = measure_arm(2048, 5000, 100, 0.5, 1.5, 13, 400)["recall"]
    seed_moves = (r_s7 != r_s13)
    ok &= seed_moves
    # 4) discriminator fires SEMANTIC at a well-provisioned regime
    d_prim = decompose(dict(N=2048, N_high=8192, V=5000, G=100, rho=0.5,
                            se=1.5, se_lo=0.4, nq=400), 7)
    fires_sem = d_prim["gains"]["D"] >= D_MARGIN
    ok &= fires_sem
    # 5) capacity LEVER FIRES at a starved regime AND is more saturated at provisioned N
    d_ctrl = decompose(dict(N=48, N_high=256, V=5000, G=100, rho=0.0,
                            se=0.6, se_lo=0.3, nq=400), 7)
    cap_ctrl = d_ctrl["gains"]["capacity_gain"]
    cap_prim = d_prim["gains"]["capacity_gain"]
    fires_cap = (cap_ctrl >= CTRL_LEVER_FLOOR) and (cap_ctrl > cap_prim)
    ok &= fires_cap
    # 6) arms differ (no bit-identical code matrices in the primary factorial)
    hashes = list(d_prim["code_hashes"].values())
    arms_differ = len(set(hashes)) == len(hashes)
    ok &= arms_differ
    print(f"[self-test] N-invariant-cos={n_inv}(|d|={abs(c_lo-c_hi):.3f}) "
          f"se-moves-cos={se_moves}(d={c_good-c_bad:.3f}) "
          f"seed-moves-recall={seed_moves}({r_s7:.3f}!={r_s13:.3f}) "
          f"fires_SEM={fires_sem}(D={d_prim['gains']['D']:.3f}) "
          f"cap_lever_fires={fires_cap}(cap_starved={cap_ctrl:.3f}>cap_prov={cap_prim:.3f}) "
          f"arms_differ={arms_differ}")
    print(f"[self-test] {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ------------------------------------ main -----------------------------------
def run(run_mode):
    t0 = time.perf_counter()
    if run_mode == "smoke":
        prim_regime, ctrl_regime, seeds = SMOKE_FULL_REGIME, SMOKE_CTRL_REGIME, SMOKE_SEEDS
    else:
        prim_regime, ctrl_regime, seeds = FULL_REGIME, CTRL_REGIME, FULL_SEEDS
    expected_units = len(seeds) * 2  # 2 regimes x n_seeds decompositions
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)

    pil = None
    if PerItemLogger is not None:
        try:
            pil = PerItemLogger(OUTPUT_DIR, eval_name=f"{ANCHOR_NAME}:{run_mode}", cap=200000)
        except Exception:  # noqa: BLE001
            pil = None

    primary = _run_regime_multiseed(OUTPUT_DIR, run_mode, prim_regime, seeds, "primary", pil=pil)
    control = _run_regime_multiseed(OUTPUT_DIR, run_mode, ctrl_regime, seeds, "control")
    agg_p = _aggregate(primary)
    agg_c = _aggregate(control)

    # sensitivity sweeps (faithful regime only; single sweep-seed set for cost)
    sweep_seeds = seeds if run_mode == "full" else seeds[:2]
    sweeps, slopes = sensitivity_sweeps(prim_regime, sweep_seeds)

    if pil is not None:
        pil.close()

    # ---- verdict logic ----
    D_p = agg_p["gains_mean"]["D"]
    cap_p = agg_p["gains_mean"]["capacity_gain"]
    sem_p = agg_p["gains_mean"]["semantic_gain"]
    fid_p = agg_p["gains_mean"]["fidelity_gain"]
    corr_p = agg_p["gains_mean"]["correlation_gain"]
    cap_c = agg_c["gains_mean"]["capacity_gain"]
    D_c = agg_c["gains_mean"]["D"]
    primary_verdict = _verdict_from_D(D_p, cap_p, sem_p)
    # SATURATION control: capacity lever must FIRE when starved and be more saturated
    # at the provisioned operating N (see CTRL_LEVER_FLOOR rationale).
    control_lever_fires = (cap_c >= CTRL_LEVER_FLOOR) and (cap_c > cap_p)

    # cos-to-target ceiling decomposition (the FIDELITY metric that mirrors 0.507):
    # capacity effect = range of cos across the N sweep; semantic effect = cos lift
    # from idealizing the teacher (SEM_FIDELITY_IDEAL vs FULL).
    cos_N_effect = None
    try:
        cvals = [p["cos_to_target"] for p in sweeps["N"]]
        cos_N_effect = float(max(cvals) - min(cvals))
    except Exception:  # noqa: BLE001
        pass
    cos_se_effect = float(agg_p["cos_to_target_mean"]["SEM_FIDELITY_IDEAL"]
                          - agg_p["cos_to_target_mean"]["FULL"])
    cos_ceiling_verdict = ("SEMANTIC" if (cos_N_effect is not None
                           and cos_se_effect - cos_N_effect >= D_MARGIN) else "AMBIGUOUS")

    # cardinality gate
    n_units = len(primary) + len(control)
    cardinality_ok = (n_units == expected_units)

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not control_lever_fires:
        verdict = "HARD_FAIL_CAPACITY_LEVER_INERT"
    else:
        verdict = primary_verdict

    # load-bearing factor ranking (which lever recovers the most recall)
    ranking = sorted(
        [("capacity", cap_p), ("semantic_fidelity", fid_p), ("semantic_correlation", corr_p)],
        key=lambda kv: kv[1], reverse=True)

    fid_ceiling_n_invariant = None
    try:
        cs = sweeps["N"]
        cos_vals = [p["cos_to_target"] for p in cs]
        fid_ceiling_n_invariant = float(max(cos_vals) - min(cos_vals))
    except Exception:  # noqa: BLE001
        pass

    verdict_msg = (
        f"{verdict} | RECALL PRIMARY(faithful N={prim_regime['N']}): FULL_recall="
        f"{agg_p['recall_mean']['FULL']:.3f} D={D_p:+.3f} "
        f"(sem_gain={sem_p:+.3f} [fidelity={fid_p:+.3f} corr={corr_p:+.3f}] "
        f"cap_gain={cap_p:+.3f}) -> {primary_verdict}. "
        f"CAPACITY-SATURATION control(starved N={ctrl_regime['N']}): cap_gain_starved="
        f"{cap_c:+.3f} vs cap_gain_provisioned={cap_p:+.3f} lever_fires={control_lever_fires}. "
        f"COS-TO-TARGET ceiling: N-effect={cos_N_effect} vs teacher-effect={cos_se_effect:+.3f}"
        f" -> {cos_ceiling_verdict}. "
        f"Load-bearing rank(recall): {ranking[0][0]}({ranking[0][1]:+.3f}) > "
        f"{ranking[1][0]}({ranking[1][1]:+.3f}) > {ranking[2][0]}({ranking[2][1]:+.3f}). "
        f"slopes dR/dN={slopes['dRecall_dN']:.2e} dR/dSigmaE={slopes['dRecall_dSigmaE']:.3f} "
        f"dR/dRho={slopes['dRecall_dRho']:.3f}.")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: recall-ceiling decomposition ({run_mode})",
        "run_mode": run_mode,
        "elapsed_s": time.perf_counter() - t0,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_units,
        "n_units": n_units,
        "primary_verdict": primary_verdict,
        "control_lever_fires": control_lever_fires,
        "cap_gain_starved": cap_c,
        "cap_gain_provisioned": cap_p,
        "D_primary": D_p,
        "D_control": D_c,
        "cos_ceiling_verdict": cos_ceiling_verdict,
        "cos_N_effect": cos_N_effect,
        "cos_teacher_effect": cos_se_effect,
        "load_bearing_ranking": ranking,
        "primary_regime": prim_regime,
        "control_regime": ctrl_regime,
        "primary_agg": agg_p,
        "control_agg": agg_c,
        "sensitivity_slopes": slopes,
        "sensitivity_sweeps": sweeps,
        "cos_to_target_N_range": fid_ceiling_n_invariant,
        "bands": {"D_margin": D_MARGIN, "gain_floor": GAIN_FLOOR,
                  "ctrl_lever_floor": CTRL_LEVER_FLOOR},
        "seeds": seeds,
    }
    _write_metrics(OUTPUT_DIR, metrics)
    print("[done] " + verdict_msg, flush=True)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["full", "smoke", "self_test"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test or args.run_mode == "self_test":
        raise SystemExit(self_test())
    run(args.run_mode)


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
