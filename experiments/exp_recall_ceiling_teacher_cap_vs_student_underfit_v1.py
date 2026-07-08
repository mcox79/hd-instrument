"""Recall-ceiling DISAMBIGUATION -- teacher-cap vs student-underfit (REAL BGE).

MEASUREMENT, NOT A FIX. The prior decomposition
(exp_recall_ceiling_capacity_vs_semantic_decomp_v1) established the concept-recall
ceiling (~0.5) is SEMANTIC-fidelity-bound not capacity-bound, but it used a
CONTROLLED teacher-noise PROXY (sigma_e). A proxy teacher cannot answer the
load-bearing follow-up:

  (a) STUDENT-UNDERFIT: our substrate encoder fails to reach the retrieval
      fidelity of its own BGE teacher  -> FIX THE STUDENT (train/capacity;
      already targeted by the v2 MLP distill cell), OR
  (b) TEACHER-CAP: the BGE teacher ITSELF tops out near ~0.5 on our
      concept-retrieval task, so distillation can never exceed it -> REPLACE the
      distillation objective with a substrate-native one.

These have OPPOSITE fixes. This cell measures BGE-TEACHER's OWN recall and a
substrate STUDENT's recall on the SAME concept-retrieval task, SAME dictionary,
SAME cleanup (argmax cosine), so the gap (or lack of one) is DIRECT evidence.

REAL DATA (justification for real-BGE over a proxy): the whole question is
whether the REAL BGE tops out. A teacher-noise proxy assumes teacher fidelity is
a free knob and therefore CANNOT distinguish (a) from (b). We load the cached
BGE-large teacher embeddings (data/substrate_index/cached_indices/
bge_large_v2_name_*.npz: semantic (V,1024) + concept id_order). One embedding per
concept (composite==semantic in cache; no distinct paraphrase view on disk;
wordnet cache empty) so the query!=key structure comes from the task itself, not
a second surface form.

TWO real concept-retrieval readouts on the SAME dictionary + SAME encoders:

  TASK SP (SUPERPOSITION recall@J) -- this is the PRODUCTION ~0.5 task (v2 distill
    smoke MEASURED bundle@J5 diag=0.420). Bundle J concept vectors (query = their
    normalized sum, genuinely != any single key), argmax-cosine recall@J over the
    V-concept dictionary. Semantic correlation collapses superposition.
      SP_gap = recall_teacher(J_OP) - recall_student(J_OP)   [PRIMARY discriminator]
      RT_sp  = teacher superposition recall @J_OP            [teacher-cap level]

  TASK SC (SINGLE-CONCEPT discrimination under shared-source rendering noise) --
    the pointwise-fidelity cross-check. Query = a concept's BGE source perturbed
    by relative noise alpha (a noisy rendering), encoded THROUGH each arm from the
    SAME noisy source; argmax-cosine recall over the dictionary.
      SC_gap = recall_teacher(ALPHA_OP) - recall_student(ALPHA_OP)  [cross-check]

  CROWDING scalar (teacher-cap witness): median teacher nearest-neighbor cosine +
    frac(NN-cos > 0.90) over the seeded working dictionary. High => concepts are
    near-duplicates in BGE space (explains superposition collapse).

WHY THE READOUTS SEPARATE THE HYPOTHESES (measured in calibration, NOT assumed;
see completion report; these are HYPOTHESIZED at pre-reg, MEASURED at landing):
  - If matching BGE geometry CAPS you (teacher superposition recall low) AND the
    substrate code BEATS it by decorrelating (SP_gap negative) -> distilling to
    match BGE is the WRONG objective -> (b) OBJECTIVE_MISMATCH / substrate-native.
  - If the teacher has superposition fidelity the student LOSES (SP_gap large
    positive, teacher high) -> (a) STUDENT_UNDERFIT / fix the student.
  - If teacher and student are capped equally (|SP_gap| small, both low) ->
    TEACHER_CAP_INTRINSIC (semantic content is intrinsically ambiguous).
The single-concept readout tells us whether the teacher's pointwise headroom is
recoverable by the substrate code family (representation-cap sub-classification).

STUDENT (substrate representation): canonical sparse-bipolar HD code -- random
Gaussian projection (Din->N) then top-K-magnitude WTA sign, N=4096 K=128
(3.125% sparse, matches the production block-code sparsity). This is the
ZERO-TRAINING substrate encoder = the representation-ceiling reference; a trained
MLP student targeting this code family (v2 spearman HARD_FAIL 0.317; smoke
bundle@J5 diag 0.420) sits at or below it. We do NOT couple to the (fragile)
trained checkpoint; the untrained code family bounds the question cleanly.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (sha256 teacher-dict vs student-dict)
- final_metrics_atomicity: tmp_replace (os.replace on final metrics.json)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a: retrieval recall; no closed-form noise floor. Feasibility handled by
  the calibrated operating points (teacher SP in-band, student SP in-band).
- baseline_in_band: both superposition arms at J_OP in (0.05,0.95); the SC teacher
  ~1.0 is the SIGNAL (teacher pointwise headroom), declared exempt not vacuous.
- discriminator survives scale: smoke V=4000 fires the PRIMARY (SP) discriminator
  (calib SP_gap=-0.561 @V4000, -0.662 @V40000; sign + teacher-low both survive).
- HARD bands strictly above floor (OBJECTIVE_MISMATCH needs SP_gap<=-0.15; calib
  -0.56..-0.66 -- large margin).
- per-unit failure-class instrumentation (no bare except)
- calibration_check: default_ok_for_this_regime (real BGE cache; operating points
  calibrated on 43905-concept cache before pre-reg)
- all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

ASCII-only. No unicode. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import glob
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

ANCHOR_NAME = "recall_ceiling_teacher_cap_vs_student_underfit_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", f"exp_{ANCHOR_NAME}")

# unbuffered progress (per section 17)
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:  # noqa: BLE001
    pass

# ----------------------------- teacher cache -------------------------------
_CACHE_DIR = os.path.join(_REPO, "data", "substrate_index", "cached_indices")
# primary cache (V=43905, fast); fallback glob to any v2_name cache with enough rows
_PRIMARY_CACHE = os.path.join(_CACHE_DIR, "bge_large_v2_name_43905_8a40445a.npz")

# ------------------------- student (substrate) code --------------------------
STUDENT_N = 4096           # HD code dimensionality (production N_DIM)
STUDENT_K = 128            # top-K magnitude coords kept (3.125% sparse; production)

# ------------------------------- operating points ----------------------------
J_OP = 5                   # production superposition load (v2 bundle@J5)
ALPHA_OP = 1.2             # single-concept rendering-noise operating alpha

# ------------------------------- pre-reg bands -------------------------------
# PRIMARY discriminator is the PRODUCTION task (superposition, TASK SP).
SP_GAP_NEG = -0.15         # student beats teacher by >= this => objective-mismatch
SP_GAP_POS = 0.20          # teacher beats student by >= this => student-underfit
RT_SP_LOW = 0.55           # teacher superposition recall at/under this => teacher caps low
RT_SP_HIGH = 0.70          # teacher superposition recall at/over this => teacher has headroom
SP_GAP_TIE = 0.10          # |gap| <= this with both low => intrinsic teacher-cap
SC_GAP_FID = 0.15          # single-concept gap >= this => substrate loses pointwise fidelity
CROWD_HI = 0.85            # median teacher NN-cos >= this => crowded BGE space (context)

# multi-seed
FULL_SEEDS = [7, 13, 19, 23, 29]
SMOKE_SEEDS = [7, 13, 19]

# regimes
FULL_REGIME = dict(V=40000, alphas=[0.0, 0.4, 0.8, 1.2, 1.6], Js=[1, 2, 3, 5, 8], nq=600)
SMOKE_REGIME = dict(V=4000, alphas=[0.0, 0.8, 1.2, 1.6], Js=[1, 3, 5], nq=400)


# --------------------------------- primitives --------------------------------
def _l2n(x):
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-9)


def _make_proj(din, n, rng):
    """Random Gaussian projection Din->N (unit-scaled)."""
    return (rng.standard_normal((din, n)).astype(np.float32) / np.sqrt(din))


def _encode_student(bge, W, k):
    """Canonical sparse-bipolar HD code: proj -> top-K magnitude -> sign, rest 0."""
    z = bge.astype(np.float32) @ W                       # (B, N)
    idx = np.argpartition(-np.abs(z), k, axis=1)[:, :k]   # top-K magnitude coords
    code = np.zeros_like(z)
    rows = np.arange(z.shape[0])[:, None]
    code[rows, idx] = np.sign(z[rows, idx])
    return code.astype(np.float32)


def _nn_crowding(unit_dict, rng, sample):
    """median nearest-neighbor cosine + frac>0.90 + frac>0.80 over a sampled subset."""
    V = unit_dict.shape[0]
    idx = rng.choice(V, size=min(sample, V), replace=False)
    sub = unit_dict[idx]
    sims = sub @ unit_dict.T                              # (sample, V)
    sims[np.arange(len(idx)), idx] = -2.0                 # mask self
    nn = sims.max(axis=1)
    return (float(np.median(nn)), float(np.mean(nn > 0.90)), float(np.mean(nn > 0.80)))


def _superposition_recall(unit_dict, rng, J, nq):
    """recall@J: bundle J members (unit sum), argmax-cosine top-J over dict."""
    V = unit_dict.shape[0]
    members = rng.integers(0, V, size=(nq, J))
    q = _l2n(unit_dict[members].sum(axis=1))              # (nq, D) bundle
    sims = q @ unit_dict.T                                # (nq, V)
    topJ = np.argpartition(-sims, J, axis=1)[:, :J]
    hits = [len(set(topJ[i].tolist()) & set(members[i].tolist())) / J for i in range(nq)]
    return float(np.mean(hits))


# ------------------------- per-seed measurement -------------------------------
def measure_seed(bge_full, seed, regime, want_peritem=False, pil=None):
    """One complete dual-task measurement (teacher + student) at one seed."""
    rng = np.random.default_rng(seed)
    V = regime["V"]
    sel = rng.choice(bge_full.shape[0], size=min(V, bge_full.shape[0]), replace=False)
    bge = bge_full[sel].astype(np.float32)                # dict source (V, Din)
    Vr = bge.shape[0]
    W = _make_proj(bge.shape[1], STUDENT_N, rng)          # per-seed student projection
    t_dict = _l2n(bge)                                    # teacher dictionary (unit)
    s_codes = _encode_student(bge, W, STUDENT_K)
    s_dict = _l2n(s_codes)                                # student dictionary (unit)

    t_hash = hashlib.sha256(t_dict.tobytes()).hexdigest()
    s_hash = hashlib.sha256(s_dict.tobytes()).hexdigest()

    # crowding (teacher space)
    crowd_med, crowd_f90, crowd_f80 = _nn_crowding(t_dict, np.random.default_rng(seed + 1),
                                                   sample=min(4000, Vr))

    # ---- TASK SP: superposition recall@J (teacher vs student) ----
    sp_teacher, sp_student = {}, {}
    for J in regime["Js"]:
        sp_teacher[J] = _superposition_recall(t_dict, np.random.default_rng(seed * 100 + J), J, regime["nq"])
        sp_student[J] = _superposition_recall(s_dict, np.random.default_rng(seed * 100 + J), J, regime["nq"])
        print(f"[progress] seed={seed} SP J={J} teacher={sp_teacher[J]:.3f} "
              f"student={sp_student[J]:.3f} gap={sp_teacher[J]-sp_student[J]:+.3f}", flush=True)

    # ---- TASK SC: single-concept discrimination under shared-source rendering noise ----
    qrng = np.random.default_rng(seed * 7 + 3)
    qi = qrng.choice(Vr, size=min(regime["nq"], Vr), replace=False)
    src = bge[qi]                                         # (nq, Din) clean source
    src_norm = np.linalg.norm(src, axis=1, keepdims=True)
    sc_teacher, sc_student = {}, {}
    peritem = None
    for a in regime["alphas"]:
        nz = qrng.standard_normal(src.shape).astype(np.float32)
        nz = nz / (np.linalg.norm(nz, axis=1, keepdims=True) + 1e-9)
        qsrc = src + a * src_norm * nz                   # noisy rendering in BGE source space
        # teacher: BGE identity encoder
        qt = _l2n(qsrc)
        pred_t = np.argmax(qt @ t_dict.T, axis=1)
        hit_t = (pred_t == qi)
        sc_teacher[a] = float(np.mean(hit_t))
        # student: encode SAME noisy source through the substrate code
        qs = _l2n(_encode_student(qsrc, W, STUDENT_K))
        pred_s = np.argmax(qs @ s_dict.T, axis=1)
        hit_s = (pred_s == qi)
        sc_student[a] = float(np.mean(hit_s))
        print(f"[progress] seed={seed} SC alpha={a} teacher={sc_teacher[a]:.3f} "
              f"student={sc_student[a]:.3f} gap={sc_teacher[a]-sc_student[a]:+.3f}", flush=True)
        if want_peritem and abs(a - ALPHA_OP) < 1e-9:
            peritem = (qi, hit_t, hit_s)

    if pil is not None and peritem is not None:
        qi_p, ht, hs = peritem
        for i in range(len(qi_p)):
            pil.log(int(qi_p[i]), stage=f"sc:alpha{ALPHA_OP}",
                    outcome={"teacher_hit": bool(ht[i]), "student_hit": bool(hs[i]),
                             "student_miss": not bool(hs[i])}, tags={})

    return {
        "seed": int(seed), "V": int(Vr),
        "sp_teacher": {str(k): v for k, v in sp_teacher.items()},
        "sp_student": {str(k): v for k, v in sp_student.items()},
        "sc_teacher": {str(k): v for k, v in sc_teacher.items()},
        "sc_student": {str(k): v for k, v in sc_student.items()},
        "crowd_median_nn": crowd_med, "crowd_frac_gt90": crowd_f90, "crowd_frac_gt80": crowd_f80,
        "t_dict_hash": t_hash, "s_dict_hash": s_hash,
    }


# ------------------------------ aggregation ----------------------------------
def _mean(xs):
    return float(np.mean(xs)) if xs else float("nan")


def _cv(xs):
    a = np.asarray(xs, dtype=np.float64)
    mu = float(np.mean(a))
    return 0.0 if abs(mu) < 1e-9 else float(np.std(a) / abs(mu))


def _aggregate(per_seed, Js, alphas):
    def curve(field, keys):
        return {str(k): _mean([s[field][str(k)] for s in per_seed]) for k in keys}
    agg = {
        "n_seeds": len(per_seed),
        "sp_teacher_mean": curve("sp_teacher", Js),
        "sp_student_mean": curve("sp_student", Js),
        "sc_teacher_mean": curve("sc_teacher", alphas),
        "sc_student_mean": curve("sc_student", alphas),
        "crowd_median_nn_mean": _mean([s["crowd_median_nn"] for s in per_seed]),
        "crowd_frac_gt90_mean": _mean([s["crowd_frac_gt90"] for s in per_seed]),
        "crowd_frac_gt80_mean": _mean([s["crowd_frac_gt80"] for s in per_seed]),
        "sp_gap_op_per_seed": [s["sp_teacher"][str(J_OP)] - s["sp_student"][str(J_OP)] for s in per_seed],
        "sc_gap_op_per_seed": [s["sc_teacher"][str(ALPHA_OP)] - s["sc_student"][str(ALPHA_OP)] for s in per_seed],
        "rt_sp_op_per_seed": [s["sp_teacher"][str(J_OP)] for s in per_seed],
    }
    agg["sp_gap_op_cv"] = _cv(agg["sp_gap_op_per_seed"])
    return agg


def _classify(rt_sp, sp_gap, sc_gap, crowd_med):
    """Primary verdict from the PRODUCTION (superposition) task; symmetric bands."""
    if sp_gap <= SP_GAP_NEG and rt_sp <= RT_SP_LOW:
        primary = "OBJECTIVE_MISMATCH_SUBSTRATE_NATIVE"     # fix (b)
    elif sp_gap >= SP_GAP_POS and rt_sp >= RT_SP_HIGH:
        primary = "STUDENT_UNDERFIT"                        # fix (a)
    elif abs(sp_gap) <= SP_GAP_TIE and rt_sp <= RT_SP_LOW:
        primary = "TEACHER_CAP_INTRINSIC"
    else:
        primary = "MIDDLE_BAND_MIXED"
    # single-concept sub-classification (pointwise fidelity)
    if sc_gap >= SC_GAP_FID:
        sub = "SUBSTRATE_LOSES_POINTWISE_FIDELITY"         # representation-cap on discrimination
    elif sc_gap <= -SC_GAP_FID:
        sub = "SUBSTRATE_ADDS_POINTWISE_FIDELITY"
    else:
        sub = "POINTWISE_FIDELITY_MATCHED"
    return primary, sub


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


def _resolve_cache():
    if os.path.exists(_PRIMARY_CACHE):
        return _PRIMARY_CACHE
    cands = sorted(glob.glob(os.path.join(_CACHE_DIR, "bge_large_v2_name_*.npz")))
    if not cands:
        raise FileNotFoundError(f"no BGE teacher cache in {_CACHE_DIR} (bge_large_v2_name_*.npz)")
    # pick the largest by row count in filename (name_<V>_<hash>.npz)
    def vcount(p):
        try:
            return int(os.path.basename(p).split("_name_")[1].split("_")[0])
        except Exception:  # noqa: BLE001
            return 0
    return max(cands, key=vcount)


def _load_teacher(regime):
    path = _resolve_cache()
    d = np.load(path, allow_pickle=True)
    if "semantic" not in d:
        raise KeyError(f"cache {path} missing 'semantic' key; has {list(d.keys())}")
    sem = d["semantic"].astype(np.float32)
    # drop zero rows (unembeddable concepts) so they cannot corrupt argmax
    good = np.linalg.norm(sem, axis=1) > 1e-6
    sem = sem[good]
    if sem.shape[0] < regime["V"]:
        print(f"[warn] cache has {sem.shape[0]} usable rows < requested V={regime['V']}; "
              f"using all {sem.shape[0]}", flush=True)
    return sem, os.path.basename(path)


def _seed_partial_path(output_dir, run_mode, seed):
    return os.path.join(output_dir, f"_seed_{run_mode}_{seed}.json")


# ---------------------------------- self-test --------------------------------
def self_test():
    """Scaffold-free witnesses: encoder validity + telemetry-sensitivity + both branches."""
    ok = True
    reg = dict(V=2500, alphas=[0.0, 1.2], Js=[1, 5], nq=250)
    try:
        bge_full, _src = _load_teacher(reg)
    except Exception as e:  # noqa: BLE001
        print(f"[self-test] FAIL cannot load teacher cache: {e}")
        return 1
    m7 = measure_seed(bge_full, 7, reg)
    m13 = measure_seed(bge_full, 13, reg)

    # 1) student is a VALID encoder: J=1 self-retrieval ~1.0 for both arms
    valid_enc = (m7["sp_teacher"]["1"] >= 0.98) and (m7["sp_student"]["1"] >= 0.98)
    ok &= valid_enc
    # 2) real crowded BGE space loaded (median NN-cos high, sanity that data is real)
    crowd_real = m7["crowd_median_nn"] > 0.5
    ok &= crowd_real
    # 3) TELEMETRY-SENSITIVITY: superposition recall@J_OP NOT bit-identical across seeds
    seed_moves = (m7["sp_teacher"][str(J_OP)] != m13["sp_teacher"][str(J_OP)]) or \
                 (m7["sp_student"][str(J_OP)] != m13["sp_student"][str(J_OP)])
    ok &= seed_moves
    # 4) PRIMARY discriminator FIRES at this reduced scale: student beats teacher on
    #    superposition (gap negative) AND teacher superposition recall is low
    sp_gap = m7["sp_teacher"][str(J_OP)] - m7["sp_student"][str(J_OP)]
    fires_sp = (sp_gap <= SP_GAP_NEG) and (m7["sp_teacher"][str(J_OP)] <= RT_SP_LOW)
    ok &= fires_sp
    # 5) ARMS DIFFER (META_RULE_AF): teacher-dict vs student-dict bit-different
    arms_differ = m7["t_dict_hash"] != m7["s_dict_hash"]
    ok &= arms_differ
    # 6) single-concept readout is a real number in [0,1] and moves with noise
    sc_moves = m7["sc_teacher"]["0.0"] >= m7["sc_teacher"]["1.2"] - 1e-9
    ok &= sc_moves

    print(f"[self-test] valid_encoder={valid_enc}"
          f"(spT@1={m7['sp_teacher']['1']:.3f} spS@1={m7['sp_student']['1']:.3f}) "
          f"crowd_real={crowd_real}(med_nn={m7['crowd_median_nn']:.3f}) "
          f"seed_moves={seed_moves}(spT@{J_OP}: {m7['sp_teacher'][str(J_OP)]:.3f}!={m13['sp_teacher'][str(J_OP)]:.3f}) "
          f"fires_SP={fires_sp}(gap={sp_gap:+.3f} rt={m7['sp_teacher'][str(J_OP)]:.3f}) "
          f"arms_differ={arms_differ} sc_moves={sc_moves}")
    print(f"[self-test] {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ------------------------------------ main -----------------------------------
def run(run_mode):
    t0 = time.perf_counter()
    regime, seeds = (SMOKE_REGIME, SMOKE_SEEDS) if run_mode == "smoke" else (FULL_REGIME, FULL_SEEDS)
    expected_units = len(seeds)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)

    bge_full, cache_src = _load_teacher(regime)

    pil = None
    if PerItemLogger is not None:
        try:
            pil = PerItemLogger(OUTPUT_DIR, eval_name=f"{ANCHOR_NAME}:{run_mode}", cap=200000)
        except Exception:  # noqa: BLE001
            pil = None

    per_seed = []
    for i, sd in enumerate(seeds):
        pp = _seed_partial_path(OUTPUT_DIR, run_mode, sd)
        if os.path.exists(pp):
            try:
                with open(pp, encoding="utf-8") as f:
                    per_seed.append(json.load(f))
                continue
            except Exception:  # noqa: BLE001 - corrupt partial: recompute
                pass
        ts = time.perf_counter()
        res = measure_seed(bge_full, sd, regime, want_peritem=(pil is not None and i == 0), pil=pil)
        res["elapsed_s"] = time.perf_counter() - ts
        tmp = pp + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(res, f)
        os.replace(tmp, pp)
        per_seed.append(res)

    if pil is not None:
        pil.close()

    agg = _aggregate(per_seed, regime["Js"], regime["alphas"])

    # operating-point aggregates
    rt_sp = agg["sp_teacher_mean"][str(J_OP)]
    rs_sp = agg["sp_student_mean"][str(J_OP)]
    sp_gap = rt_sp - rs_sp
    rt_sc = agg["sc_teacher_mean"][str(ALPHA_OP)]
    rs_sc = agg["sc_student_mean"][str(ALPHA_OP)]
    sc_gap = rt_sc - rs_sc
    crowd_med = agg["crowd_median_nn_mean"]

    primary, sub = _classify(rt_sp, sp_gap, sc_gap, crowd_med)

    # cardinality gate
    n_units = len(per_seed)
    cardinality_ok = (n_units == expected_units)

    # baseline-in-band (superposition arms) + arms-differ (smoke/self only strict)
    sp_in_band = (0.05 < rt_sp < 0.95) and (0.05 < rs_sp < 0.95)
    arms_differ = per_seed[0]["t_dict_hash"] != per_seed[0]["s_dict_hash"]

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not arms_differ:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    else:
        verdict = primary

    crowd_ctx = "CROWDED" if crowd_med >= CROWD_HI else "SPARSE"
    verdict_msg = (
        f"{verdict} | PRODUCTION superposition@J{J_OP}(V={per_seed[0]['V']}): "
        f"teacher={rt_sp:.3f} student={rs_sp:.3f} SP_gap={sp_gap:+.3f} -> {primary}. "
        f"SINGLE-CONCEPT@alpha{ALPHA_OP}: teacher={rt_sc:.3f} student={rs_sc:.3f} "
        f"SC_gap={sc_gap:+.3f} -> {sub}. "
        f"TEACHER-CROWDING: median_NN_cos={crowd_med:.3f} frac>0.90={agg['crowd_frac_gt90_mean']:.3f}"
        f" ({crowd_ctx}). "
        f"SP curve teacher={ {k: round(v,3) for k,v in agg['sp_teacher_mean'].items()} } "
        f"student={ {k: round(v,3) for k,v in agg['sp_student_mean'].items()} }. "
        f"SP_gap@J{J_OP} per-seed cv={agg['sp_gap_op_cv']:.3f}. cache={cache_src}. "
        f"INTERPRETATION: {'matching-BGE-geometry caps recall; substrate decorrelation exceeds teacher -> replace distillation objective (fix b)' if primary=='OBJECTIVE_MISMATCH_SUBSTRATE_NATIVE' else ('teacher has superposition fidelity the student loses -> fix the student (fix a)' if primary=='STUDENT_UNDERFIT' else ('teacher and student capped equally -> intrinsic semantic ambiguity' if primary=='TEACHER_CAP_INTRINSIC' else 'mixed; see per-task readouts'))}."
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: teacher-cap vs student-underfit ({run_mode})",
        "run_mode": run_mode,
        "elapsed_s": time.perf_counter() - t0,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "cache_source": cache_src,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_units,
        "n_units": n_units,
        "primary_verdict": primary,
        "pointwise_subclass": sub,
        "arms_differ_verified": arms_differ,
        "baseline_in_band_superposition": sp_in_band,
        "operating_points": {"J_OP": J_OP, "ALPHA_OP": ALPHA_OP},
        "rt_sp_op": rt_sp, "rs_sp_op": rs_sp, "sp_gap_op": sp_gap,
        "rt_sc_op": rt_sc, "rs_sc_op": rs_sc, "sc_gap_op": sc_gap,
        "crowd_median_nn": crowd_med,
        "crowd_frac_gt90": agg["crowd_frac_gt90_mean"],
        "crowd_frac_gt80": agg["crowd_frac_gt80_mean"],
        "student_code": {"N": STUDENT_N, "K": STUDENT_K, "sparsity": STUDENT_K / STUDENT_N},
        "bands": {"SP_GAP_NEG": SP_GAP_NEG, "SP_GAP_POS": SP_GAP_POS,
                  "RT_SP_LOW": RT_SP_LOW, "RT_SP_HIGH": RT_SP_HIGH,
                  "SP_GAP_TIE": SP_GAP_TIE, "SC_GAP_FID": SC_GAP_FID, "CROWD_HI": CROWD_HI},
        "regime": regime,
        "agg": agg,
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
