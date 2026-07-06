"""exp_comprehension_order_recovery_exact_margin_v1

EXACT SELF-MARGIN test for a CAPABILITY (comprehension order-recovery): does the substrate
predict its OWN comprehension decode/order-recovery collapse boundary (the cliff at D=8 x V in the
landed comprehension-envelope cell) in closed form, via the SAME 64-pt Gauss-Hermite extreme-value
order statistic already CG'd for RNS decode margin, FHRR bundle capacity, and reasoning depth?

This is the TOP buildable pick of the capability-self-margin frontier map
(notes/research_capability_self_margin_frontier_map_2026-07-06.md, row 5, P_deflated=0.40 -- NOT
certain). It extends the exact-order-statistic family from CODEBOOKS + reasoning-depth to
COMPREHENSION. Base cell (measurement machinery reused VERBATIM):
exp_comprehension_envelope_superposition_vocab_v1 (FULL HARD_PASS, 60-row per_unit surface).

--------------------------------------------------------------------------------
THE TARGET (what actually collapses in the landed comprehension surface)
--------------------------------------------------------------------------------
MEASURED@data/exp_comprehension_envelope_superposition_vocab_v1/metrics.json:per_unit --
order_content_perrole stays >= 0.93 (barely cliffs); the real order-recovery COLLAPSE lives in
decode_part / superposition_survival, which fall from ~1.0 (D<=6) to 0.30-0.87 at D=8 as V grows.
Per-role decode p1 = decode_part^(1/D) is the FUNDAMENTAL per-role order statistic (the deep cliff
is its D-fold product). The prediction test is on p1 (apples-to-apples with the sibling per-hop /
per-slot margins); decode_part = p1^D is reported as the compounding-amplification diagnostic.

--------------------------------------------------------------------------------
THE MODELS (exact = the CG'd family; loose = the retained trivial control)
--------------------------------------------------------------------------------
Per role r, decode at its (true) block: the true filler self-correlates at score ~k; the V-1
same-partition distractors compete; the L-1 co-superposed OTHER-partition fillers add noise. From
the CODE GEOMETRY (the substrate's OWN geometry, measured NOT fit-to-accuracy) we get the score
moments (mu_s, sig_s) of the signal and (mu_d, sig_d) of a single distractor at load L=D/2.
  EXACT (the CG'd extreme-value order statistic, parameter-free given the measured moments):
    p1_exact(L,V) = E_{s~N(mu_s,sig_s)}[ Phi((s - mu_d)/sig_d)^(V-1) ]   (64-pt Gauss-Hermite)
    -- the true filler must beat the MAX of V-1 distractors (extreme value of V-1 draws).
  LOOSE (retained control): p1_loose(L,V) = E_s[ Phi((s - mu_d)/sig_d)^1 ] -- signal vs ONE typical
    distractor, V-INDEPENDENT (ignores the extreme-value-of-V amplification the exact model adds).

--------------------------------------------------------------------------------
OFF-DISK CHEAP DECISIVE PRE-CHECK (zero new trials, vs the landed 60-row surface) -- HONEST RESULT
--------------------------------------------------------------------------------
MEASURED@author off-disk (moments from geometry + landed decode_part; 8 non-saturated p1 cells):
  EXACT p1: mean_ratio 1.19, gm_ratio_err 1.18, max_ratio_err 1.47  (BIASED -- over-predicts collapse)
  LOOSE p1: mean_ratio 0.97, gm_ratio_err 1.03, max_ratio_err 1.09  (CLOSER, but V-blind)
  rel_improve = loose_gm_err / exact_gm_err = 0.87  (< 1.0 -> exact is NOT tighter than loose)
  decode_part (p1^D) exact ratio: gm 3.5x, MAX 18-22x  (D-fold compounding of the p1 over-prediction)
DIRECTION: the exact extreme-value order statistic OVER-predicts the comprehension decode cliff and
does NOT beat a trivial single-draw model on p1. ROOT CAUSE (MECHANISM): sparse block-local GSBC
distractor scores have a LIGHT (sub-Gaussian) upper tail (measured signal margin (mu_s-mu_d)/sig_d
~ 3.5 at D=8; a Gaussian max-of-1000 would sit at ~3.24 -> Gaussian model predicts p1 ~ 0.62, but
MEASURED p1 = 0.91), so the Gaussian order statistic over-counts the extreme value, and the error
compounds through the D=8 decode product. This is the SAME GSBC-heterogeneity that made the encoder
concept-Gram spectrum a POWER-LAW accept-boundary -- a convergent, mechanistically-named limit.

--------------------------------------------------------------------------------
PRE-REGISTERED BANDS (gated on the FUNDAMENTAL per-role quantity p1; non-saturated cells only)
--------------------------------------------------------------------------------
Ratio(r) = meas_p1 / pred_p1; ratio_err = max(r, 1/r). NON-SATURATED = meas_p1 in (0.55, 0.999)
(exclude the D<=4 self-correlation-saturated corners exactly as RNS/FHRR exclude their saturated
corners). Aggregate over seeds per (D,V,arm) op-point.
  HARD_PASS (H CONFIRMED -- comprehension order-recovery joins the exact self-margin family, CG-cand):
    - exact per-op ratio_err <= HP_RATIO_MAX (1.5) at ALL non-saturated cells, AND
    - exact aggregate mean-ratio in [HP_BIAS_LO, HP_BIAS_HI] = [0.80, 1.25] (unbiased), AND
    - exact TIGHTER than loose: rel_improve (loose_gm_err/exact_gm_err) >= REL_IMPROVE_MIN (1.5), AND
    - loose biased: loose aggregate mean-ratio outside [LOOSE_UNBIASED_LO, LOOSE_UNBIASED_HI]
      = [0.85, 1.18], AND
    - cross-seed CV of per-seed exact ratio_err <= HP_CV_MAX (0.15).
  HARD_FAIL / ACCEPT_BOUNDARY (H REFUTED -- comprehension order-recovery RESISTS exact self-margin;
    this is the off-disk-PREDICTED outcome, a LEGITIMATE, mechanistically-interpretable negative):
    - exact NOT tighter than loose: rel_improve < ACCEPT_REL_MAX (1.0) -- the extreme-value order
      statistic adds no value over a trivial single-draw model (the collapse is not governed by the
      extreme-value-of-V mechanism the order statistic encodes), OR
    - exact aggregate mean-ratio OUTSIDE [HF_BIAS_LO, HF_BIAS_HI] = [0.60, 1.70] (exact biased), OR
    - exact per-op ratio_err > HF_RATIO_MAX (2.0) at ANY non-saturated cell.
    ACCEPT_BOUNDARY is reported as verdict HARD_FAIL with verdict_msg tagged ACCEPT_BOUNDARY +
    the mechanism string, so downstream reads it as a scientific boundary, not a machinery failure.
  MIDDLE_BAND: exact tightens vs loose (1.0 <= rel_improve < 1.5) but misses a HARD_PASS sub-gate.

--------------------------------------------------------------------------------
CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified (AF): the EXACT prediction surface and the LOOSE prediction surface are
#   hash-distinct per unit (exact uses n_eff=V-1, loose n_eff=1 -> different arrays). Verified.
# - final_metrics_atomicity = tmp_replace (os.replace of metrics.json.tmp).
# - except SystemExit: raise BEFORE except Exception (no BaseException; grep-clean).
# - crlb / capacity-feasibility: this is a PREDICTION-MATCH test. Per-role decode chance = 1/V
#   (tiny); the measured p1 spans 0.91-1.0 (non-saturated cells at D>=6 high-V and D=8). The gated
#   quantity is a ratio, not an absolute accuracy floor. crlb_n_a: the discriminator is exact-vs-
#   loose ratio tightness, which has no Cramer-Rao noise floor. discriminator_reachability: MEASURED@
#   author off-disk (exact gm_err 1.18, loose gm_err 1.03, rel_improve 0.87) -- HP reachable in
#   PRINCIPLE (a light-tail-corrected model could pass) but the CG'd Gaussian order statistic as
#   pre-registered lands ACCEPT_BOUNDARY; both outcomes are pre-registered + interpretable.
# - baseline_in_band (AG): prediction-match test, not a difficulty baseline. Saturated (D<=4) cells
#   are EXCLUDED from ratio gates (declared), exactly as siblings exclude censored/saturated corners.
#   The loose arm is a live CONTROL; the exact arm is the MECHANISM under test.
# - discriminator survives scale: the cliff is at FULL N=8192, D=8 (never reduced). Smoke keeps the
#   FULL D grid at full N (D=8 present) so the collapse + the exact-vs-loose contrast FIRE in smoke.
# - HARD_PASS strictly above floor: HP_RATIO_MAX 1.5 + rel_improve >= 1.5 (deflated bars ABOVE the
#   MEASURED off-disk 1.18 / 0.87 retrospective -> HP is NOT reachable by the pre-registered Gaussian
#   model; this is honest, not rigged, because HARD_FAIL/ACCEPT_BOUNDARY is the pre-registered result).
# - HP_SCOPE per-arm: HARD_PASS ratio gates apply to the EXACT arm; the LOOSE arm carries only the
#   bias-direction gate (is loose biased?). No arm inherits the other's gates.
# - cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = seeds x D_grid x V_grid. Verdict gates on count.
# - per-unit failure-class instrumentation (META_RULE_J; no bare except).
# - calibration_check = default_ok_for_this_regime: the exact formula is parameter-free given the
#   geometry-measured moments (mu_s,sig_s,mu_d,sig_d) -- moments measured at a REFERENCE vocab V_REF
#   and EXTRAPOLATED across V, NOT fit to the accuracy surface. 64-pt GH matches RNS/FHRR/reasoning.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in prereg + comments.
# - progress_logging = line_buffered_stdout + print(flush=True). (smoke/self_test < 30min; FULL may
#   exceed 30min at 5 seeds -> heartbeat + flush satisfy the >= 1800s rule.)
# - start_marker + crash_diagnostic + heartbeat (defensive error checking).
# - positive_control (Gate D): the measurement machinery IS the landed comprehension cell's,
#   IMPORTED + reused VERBATIM (base.run_unit) at the SAME regime (N=8192, same GSBC pool, same
#   grid) -> no invocation/regime drift; the off-disk retrospective reproduces the landed surface.
#
# USER-LOCKED: monitor-not-control. The cell only REPORTS the exact-vs-measured comprehension cliff
#   prediction in its own metrics.json. It NEVER edits D, V, N, the base cell's config, or triggers a
#   rebuild -- a REPORTING refinement, never a config-changing action. NOT self-improvement. Brain-
#   grounding: HONESTLY a metacognitive error-monitoring signal by shared-math analogy (Nelson &
#   Narens 1990 monitor side), NOT a claim of task-level comprehension competence.
#
# Compute architecture: SEQUENTIAL-CPU (numpy matched-filter + block-argmax; the cell IS the
#   substrate comprehension primitive being re-measured -- bit-identical CPU reference exemption).
#   Storage: no_storage / no_composition beyond the base cell's superposition (synthetic clean GSBC
#   partitions). The prediction arms are numpy Gauss-Hermite quadrature (no GPU, no scipy, no torch,
#   no LLM). Requires the untracked GSBC pool npz (SCP before remote FULL; queue_add does NOT ship it).
#
# PROT-018: no _n<N> suffix (N is a fixed confirm axis, not the swept axis). NON-PARKED (synthetic
#   GSBC data only; no cert_ledger referent). ASCII-only; no unicode/emoji/em-dash. Author: exp_dev.
# Run: python experiments/exp_comprehension_order_recovery_exact_margin_v1.py [--self-test | --smoke]
#      (bare / runner-injected HDLAB_RUN_MODE=full -> full)
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
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)  # print-progress flush on newline

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Measurement machinery reused VERBATIM (Gate D positive-control at the SAME regime).
import experiments.exp_comprehension_envelope_superposition_vocab_v1 as base  # noqa: E402

ANCHOR_NAME = "comprehension_order_recovery_exact_margin_v1"

N_DIM = base.N_DIM             # 8192 (never reduced)
B_TOTAL = base.B_TOTAL         # 8
BS = N_DIM // B_TOTAL          # 1024

# ---- CLI + RUN_MODE (defaults to full; --smoke / --self-test flip; runner injects env) ----
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
_ENV_MODE = os.environ.get("HDLAB_RUN_MODE", "full").lower()
if _ARGS.self_test:
    RUN_MODE = "self_test"
elif _ARGS.smoke or _ENV_MODE == "smoke":
    RUN_MODE = "smoke"
else:
    RUN_MODE = "full"

# ---- grid + seeds per mode (D=8 always present: the cliff lives there; discriminator survives scale) ----
V_REF = 50                     # reference vocab where score moments are MEASURED then extrapolated
if RUN_MODE == "self_test":
    D_GRID = [2, 8]
    V_GRID = [50, 1000]
    SEEDS = [7]
    TRIALS = 40
    MOMENT_TRIALS = 40
elif RUN_MODE == "smoke":
    D_GRID = [2, 4, 6, 8]      # FULL D grid at full N=8192 (D=8 cliff must fire in smoke)
    V_GRID = [50, 250, 1000]   # reduced V grid (3 pts)
    SEEDS = [7, 13, 19]        # 3 seeds for cross-seed cv (RNS/FHRR smoke precedent)
    TRIALS = 60
    MOMENT_TRIALS = 60
else:  # full
    D_GRID = [2, 4, 6, 8]
    V_GRID = [50, 125, 250, 500, 1000]
    SEEDS = [7, 13, 19, 23, 29]   # >= 5 seeds (CG multi-seed precedent)
    TRIALS = 80
    MOMENT_TRIALS = 80

V_ROLE_MAX = max(V_GRID + [V_REF])
D_MAX = max(D_GRID)
EXPECTED_N_UNITS = len(SEEDS) * len(D_GRID) * len(V_GRID)

# ---- pre-registered bands (gated on per-role decode p1; non-saturated cells) ----
SAT_HI = 0.999                 # meas_p1 >= this -> saturated (excluded from ratio gates)
SAT_LO = 0.55                  # meas_p1 <= this -> below the useful band (excluded; none expected)
HP_RATIO_MAX = 1.5             # HARD_PASS: exact per-op ratio_err <= this at ALL non-saturated cells
HF_RATIO_MAX = 2.0             # HARD_FAIL: exact per-op ratio_err > this at ANY non-saturated cell
HP_BIAS_LO, HP_BIAS_HI = 0.80, 1.25     # HARD_PASS: exact aggregate mean-ratio unbiased band
HF_BIAS_LO, HF_BIAS_HI = 0.60, 1.70     # HARD_FAIL: exact aggregate mean-ratio outside -> biased
REL_IMPROVE_MIN = 1.50         # HARD_PASS: loose_gm_err / exact_gm_err >= this (exact genuinely tighter)
ACCEPT_REL_MAX = 1.00          # ACCEPT_BOUNDARY: rel_improve < this (exact no tighter than loose)
LOOSE_UNBIASED_LO, LOOSE_UNBIASED_HI = 0.85, 1.18   # loose "biased" iff mean-ratio OUTSIDE this
HP_CV_MAX = 0.15               # HARD_PASS: cross-seed CV of per-seed exact ratio_err <= this
MIN_NONSAT = {"smoke": 3, "full": 6, "self_test": 1}   # cardinality floor on non-saturated cells

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,B=%d,bs=%d,D=%s,V=%s,SEEDS=%s,TRIALS=%d,V_REF=%d,RUN_MODE=%s,"
    "pred=GH64_extreme_value_order_stat_vs_single_draw,measure=base.run_unit_VERBATIM,"
    "target=per_role_decode_p1=decode_part^(1/D)"
) % (ANCHOR_NAME, N_DIM, B_TOTAL, BS, "-".join(map(str, D_GRID)), "-".join(map(str, V_GRID)),
     "-".join(map(str, SEEDS)), TRIALS, V_REF, RUN_MODE)


# ============================================================
# Defensive error-checking helpers
# ============================================================
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _out_dir() -> Path:
    name = os.environ.get("HDLAB_EXP_NAME")
    return REPO / (f"data/exp_{name}" if name else f"data/exp_{ANCHOR_NAME}")


def _say(msg: str) -> None:
    print(msg, flush=True)


def _write_start_marker(out_dir: Path, run_mode: str, expected_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_units, "host": platform.node()}
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(str(tmp), str(out_dir / "_start_marker.json"))


def _heartbeat(out_dir: Path, unit_idx: int, total_units: int, t0: float,
               extra: Optional[Dict[str, Any]] = None) -> None:
    row = {"ts_iso": _now_iso(), "unit_idx": unit_idx, "total_units": total_units,
           "elapsed_s": round(time.perf_counter() - t0, 2)}
    if extra:
        row["extra"] = extra
    try:
        with open(out_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
    except OSError:
        pass


def _write_metrics_atomic(out_dir: Path, metrics: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(str(tmp), str(out_dir / "metrics.json"))


def _write_crash_metrics(out_dir: Path, exc: Exception) -> None:
    diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
            "pid": os.getpid(), "run_mode": RUN_MODE, "config_version": CONFIG_VERSION}
    _write_metrics_atomic(out_dir, diag)


def _digest(arr: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(arr, dtype=np.float64)).tobytes()).hexdigest()


# ============================================================
# Gauss-Hermite extreme-value order statistic (numpy-only; mirrors RNS v2 / FHRR v1 / reasoning-depth)
# ============================================================
_GH_N = 64
_GH_NODES, _GH_WEIGHTS = np.polynomial.hermite.hermgauss(_GH_N)
_INV_SQRT_PI = 1.0 / math.sqrt(math.pi)
_SQRT2 = math.sqrt(2.0)


def _logPhi(a: float) -> float:
    """Stable log standard-normal CDF. Phi(a) = 0.5*erfc(-a/sqrt2)."""
    v = 0.5 * math.erfc(-a / _SQRT2)
    return math.log(v) if v > 0.0 else -1e300


def p_win_extreme(mu_s: float, sig_s: float, mu_d: float, sig_d: float, n_comp: float) -> float:
    """P[ signal ~ N(mu_s, sig_s) beats the MAX of n_comp i.i.d. distractors ~ N(mu_d, sig_d) ]
    = E_{s~N(mu_s,sig_s)}[ Phi((s - mu_d)/sig_d)^n_comp ],  64-pt Gauss-Hermite.
    THEORETICAL@order-statistic (Hajek ECE361 L8 / Proakis Ch.4 M-ary family; David & Nagaraja
    Order Statistics -- max-of-n CDF Phi(x)^n). n_comp = V-1 (exact) or 1 (loose single-draw)."""
    if sig_d <= 0.0:
        sig_d = 1e-9
    acc = 0.0
    for zi, wi in zip(_GH_NODES, _GH_WEIGHTS):
        s = mu_s + sig_s * _SQRT2 * zi
        a = (s - mu_d) / sig_d
        lp = n_comp * _logPhi(a)
        acc += wi * (math.exp(lp) if lp > -700.0 else 0.0)
    return _INV_SQRT_PI * acc


# ============================================================
# Measure score moments from the code geometry (substrate's OWN geometry; NOT fit to accuracy)
# ============================================================
def measure_moments(seed: int, D: int, v_ref: int, cb_max: np.ndarray) -> Tuple[float, float, float, float]:
    """Estimate (mu_s, sig_s, mu_d, sig_d) at load L=D/2, reference vocab v_ref, from the code
    geometry: build L-filler superposition blocks and read out the true-filler self-correlation
    (signal) vs the same-partition distractor correlations (distractors). Reuses base._active_cb."""
    L = D // 2
    active_cb = base._active_cb(cb_max, D, v_ref, V_ROLE_MAX)   # (D*v_ref, bs)
    rng = np.random.default_rng(555 + seed + 17 * D)
    sig_scores: List[float] = []
    dist_scores: List[float] = []
    for _ in range(MOMENT_TRIALS):
        toks = [int(d * v_ref + rng.integers(0, v_ref)) for d in range(D)]
        roles = list(range(D))
        rng.shuffle(roles)
        a_roles = set(roles[:L])
        blk0 = np.zeros(BS, dtype=np.float32)
        blk1 = np.zeros(BS, dtype=np.float32)
        for d in range(D):
            (blk0 if d in a_roles else blk1)[:] += active_cb[toks[d]]
        for d in range(D):
            blk = blk0 if d in a_roles else blk1
            part = active_cb[d * v_ref:(d + 1) * v_ref]        # (v_ref, bs)
            scores = part @ blk                                 # (v_ref,)
            local = toks[d] - d * v_ref
            sig_scores.append(float(scores[local]))
            for i in range(v_ref):
                if i != local:
                    dist_scores.append(float(scores[i]))
    sig = np.asarray(sig_scores)
    dist = np.asarray(dist_scores)
    return float(sig.mean()), float(sig.std()), float(dist.mean()), float(dist.std())


# ============================================================
# One (seed, D, V) unit: fresh measurement (base.run_unit VERBATIM) + exact/loose p1 predictions
# ============================================================
def run_unit(seed: int, D: int, V: int, cb_max: np.ndarray,
             moments_D: Tuple[float, float, float, float]) -> Dict[str, Any]:
    r = base.run_unit(D, V, seed, TRIALS, cb_max, V_ROLE_MAX)   # fresh comprehension measurement
    decode_part = float(r["decode_part"])
    meas_p1 = decode_part ** (1.0 / D) if decode_part > 0.0 else 0.0
    mu_s, sig_s, mu_d, sig_d = moments_D
    p1_exact = p_win_extreme(mu_s, sig_s, mu_d, sig_d, float(V - 1))
    p1_loose = p_win_extreme(mu_s, sig_s, mu_d, sig_d, 1.0)
    dp_exact = p1_exact ** D
    dp_loose = p1_loose ** D
    saturated = bool(meas_p1 >= SAT_HI)
    below = bool(meas_p1 <= SAT_LO)
    ratio_exact = (meas_p1 / p1_exact) if p1_exact > 1e-9 else None
    ratio_loose = (meas_p1 / p1_loose) if p1_loose > 1e-9 else None
    return {
        "seed": seed, "D": D, "V_ROLE": V, "L": D // 2,
        "decode_part": round(decode_part, 4),
        "superposition_survival": round(float(r["superposition_survival"]), 4),
        "order_content_perrole": round(float(r["order_content_perrole"]), 4),
        "order_content_exact": round(float(r["order_content_exact"]), 4),
        "set_recognition": round(float(r["set_recognition"]), 4),
        "meas_p1": round(meas_p1, 5),
        "mu_s": round(mu_s, 3), "sig_s": round(sig_s, 3), "mu_d": round(mu_d, 3), "sig_d": round(sig_d, 3),
        "margin_std": round((mu_s - mu_d) / sig_d, 3) if sig_d > 0 else None,
        "p1_exact": round(p1_exact, 5), "p1_loose": round(p1_loose, 5),
        "decode_part_pred_exact": round(dp_exact, 5), "decode_part_pred_loose": round(dp_loose, 5),
        "ratio_exact_p1": (round(ratio_exact, 4) if ratio_exact is not None else None),
        "ratio_loose_p1": (round(ratio_loose, 4) if ratio_loose is not None else None),
        "ratio_exact_decode_part": (round(decode_part / dp_exact, 4) if dp_exact > 1e-9 else None),
        "saturated": saturated, "below_band": below,
    }


# ============================================================
# Aggregation + verdict
# ============================================================
def _ratio_err(r: Optional[float]) -> Optional[float]:
    if r is None or r <= 0:
        return None
    return max(r, 1.0 / r)


def _gm(errs: List[float]) -> Optional[float]:
    errs = [e for e in errs if e is not None and e > 0]
    return math.exp(float(np.mean([math.log(e) for e in errs]))) if errs else None


def _cv(xs: List[float]) -> Optional[float]:
    xs = [x for x in xs if x is not None]
    if len(xs) < 2:
        return None
    mu = float(np.mean(xs))
    return round(float(np.std(xs)) / abs(mu), 4) if abs(mu) > 1e-9 else None


def _agg_cells(per_unit: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Aggregate per (D,V) over seeds -> one op-point per cell."""
    cells: Dict[Tuple[int, int], List[Dict[str, Any]]] = {}
    for u in per_unit:
        cells.setdefault((u["D"], u["V_ROLE"]), []).append(u)
    out = []
    for (D, V), rows in sorted(cells.items()):
        meas_p1 = float(np.mean([r["meas_p1"] for r in rows]))
        p1e = float(np.mean([r["p1_exact"] for r in rows]))
        p1l = float(np.mean([r["p1_loose"] for r in rows]))
        dp = float(np.mean([r["decode_part"] for r in rows]))
        dpe = float(np.mean([r["decode_part_pred_exact"] for r in rows]))
        re = (meas_p1 / p1e) if p1e > 1e-9 else None
        rl = (meas_p1 / p1l) if p1l > 1e-9 else None
        seed_re = [_ratio_err(r["ratio_exact_p1"]) for r in rows]
        out.append({
            "D": D, "V_ROLE": V, "n_seeds": len(rows),
            "meas_p1": round(meas_p1, 5), "p1_exact": round(p1e, 5), "p1_loose": round(p1l, 5),
            "decode_part": round(dp, 4), "decode_part_pred_exact": round(dpe, 5),
            "ratio_exact_p1": (round(re, 4) if re is not None else None),
            "ratio_loose_p1": (round(rl, 4) if rl is not None else None),
            "ratio_err_exact": (round(_ratio_err(re), 4) if re else None),
            "ratio_err_loose": (round(_ratio_err(rl), 4) if rl else None),
            "ratio_exact_decode_part": (round(dp / dpe, 4) if dpe > 1e-9 else None),
            "saturated": bool(meas_p1 >= SAT_HI), "below_band": bool(meas_p1 <= SAT_LO),
            "per_seed_ratio_err_exact": [round(x, 4) for x in seed_re if x is not None],
        })
    return out


def compute_verdict(per_unit: List[Dict[str, Any]], n_units: int) -> Tuple[str, str, Dict[str, Any]]:
    if n_units < EXPECTED_N_UNITS:
        return ("HARD_FAIL", "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d units" % (n_units, EXPECTED_N_UNITS),
                {"cardinality_ok": False})

    # arms-differ (AF): exact and loose prediction surfaces must be hash-distinct.
    ex_surf = np.array([u["p1_exact"] for u in per_unit], dtype=np.float64)
    lo_surf = np.array([u["p1_loose"] for u in per_unit], dtype=np.float64)
    arms_differ = _digest(ex_surf) != _digest(lo_surf)

    cells = _agg_cells(per_unit)
    nonsat = [c for c in cells if not c["saturated"] and not c["below_band"]]
    n_nonsat = len(nonsat)

    exact_ratios = [c["ratio_exact_p1"] for c in nonsat if c["ratio_exact_p1"] is not None]
    loose_ratios = [c["ratio_loose_p1"] for c in nonsat if c["ratio_loose_p1"] is not None]
    exact_errs = [c["ratio_err_exact"] for c in nonsat if c["ratio_err_exact"] is not None]
    loose_errs = [c["ratio_err_loose"] for c in nonsat if c["ratio_err_loose"] is not None]

    exact_mean_ratio = round(float(np.mean(exact_ratios)), 4) if exact_ratios else None
    loose_mean_ratio = round(float(np.mean(loose_ratios)), 4) if loose_ratios else None
    exact_gm = _gm(exact_errs)
    loose_gm = _gm(loose_errs)
    rel_improve = (loose_gm / exact_gm) if (exact_gm and loose_gm) else None
    max_exact_err = max(exact_errs) if exact_errs else None
    # cross-seed cv (pool per-cell per-seed exact ratio-err CVs)
    per_cell_cv = [_cv(c["per_seed_ratio_err_exact"]) for c in nonsat]
    per_cell_cv = [x for x in per_cell_cv if x is not None]
    agg_cv = round(float(np.mean(per_cell_cv)), 4) if per_cell_cv else None
    # decode_part compounding diagnostic
    dp_errs = [_ratio_err(c["ratio_exact_decode_part"]) for c in nonsat]
    dp_errs = [e for e in dp_errs if e is not None]
    dp_gm = _gm(dp_errs)
    dp_max = max(dp_errs) if dp_errs else None
    loose_biased = (loose_mean_ratio is not None
                    and not (LOOSE_UNBIASED_LO <= loose_mean_ratio <= LOOSE_UNBIASED_HI))

    extra = {
        "cardinality_ok": True, "n_units": n_units, "expected_n_units": EXPECTED_N_UNITS,
        "arms_differ_verified": bool(arms_differ),
        "n_cells": len(cells), "n_nonsaturated": n_nonsat,
        "exact_mean_ratio_p1": exact_mean_ratio, "loose_mean_ratio_p1": loose_mean_ratio,
        "exact_gm_ratio_err_p1": (round(exact_gm, 4) if exact_gm else None),
        "loose_gm_ratio_err_p1": (round(loose_gm, 4) if loose_gm else None),
        "rel_improve_loose_over_exact": (round(rel_improve, 4) if rel_improve else None),
        "max_exact_ratio_err_p1": (round(max_exact_err, 4) if max_exact_err else None),
        "aggregate_cross_seed_cv_exact": agg_cv, "loose_biased": bool(loose_biased),
        "decode_part_compounding_gm_ratio_err": (round(dp_gm, 4) if dp_gm else None),
        "decode_part_compounding_max_ratio_err": (round(dp_max, 4) if dp_max else None),
        "cells": cells,
        "bands": {"HP_RATIO_MAX": HP_RATIO_MAX, "HF_RATIO_MAX": HF_RATIO_MAX,
                  "HP_BIAS_LO": HP_BIAS_LO, "HP_BIAS_HI": HP_BIAS_HI,
                  "HF_BIAS_LO": HF_BIAS_LO, "HF_BIAS_HI": HF_BIAS_HI,
                  "REL_IMPROVE_MIN": REL_IMPROVE_MIN, "ACCEPT_REL_MAX": ACCEPT_REL_MAX,
                  "LOOSE_UNBIASED_LO": LOOSE_UNBIASED_LO, "LOOSE_UNBIASED_HI": LOOSE_UNBIASED_HI,
                  "HP_CV_MAX": HP_CV_MAX, "SAT_HI": SAT_HI, "SAT_LO": SAT_LO,
                  "MIN_NONSAT": MIN_NONSAT.get(RUN_MODE, 3)},
    }

    summ = ("units=%d/%d nonsat_cells=%d | EXACT p1 mean_ratio=%s gm_err=%s max_err=%s | LOOSE p1 "
            "mean_ratio=%s gm_err=%s biased=%s | rel_improve=%s cross_seed_cv=%s | decode_part(p1^D) "
            "compounding gm=%s max=%s | arms_differ=%s"
            % (n_units, EXPECTED_N_UNITS, n_nonsat, exact_mean_ratio, extra["exact_gm_ratio_err_p1"],
               extra["max_exact_ratio_err_p1"], loose_mean_ratio, extra["loose_gm_ratio_err_p1"],
               loose_biased, extra["rel_improve_loose_over_exact"], agg_cv,
               extra["decode_part_compounding_gm_ratio_err"], extra["decode_part_compounding_max_ratio_err"],
               arms_differ))

    if not arms_differ:
        return "HARD_FAIL", "HARD_FAIL_ARMS (exact and loose prediction surfaces bit-identical -- AF): " + summ, extra
    min_nonsat = MIN_NONSAT.get(RUN_MODE, 3)
    if n_nonsat < min_nonsat:
        return ("MIDDLE_BAND", "MIDDLE_BAND (insufficient non-saturated cells: %d < %d -- decode surface "
                "saturated; the cliff did not appear at this grid): " % (n_nonsat, min_nonsat) + summ, extra)
    if exact_mean_ratio is None or loose_mean_ratio is None or rel_improve is None:
        return "MIDDLE_BAND", "MIDDLE_BAND (ratios not computable): " + summ, extra

    # ---- ACCEPT_BOUNDARY / HARD_FAIL gates (the off-disk-PREDICTED honest negative) ----
    if rel_improve < ACCEPT_REL_MAX:
        return ("HARD_FAIL",
                ("ACCEPT_BOUNDARY: comprehension order-recovery RESISTS the exact Gauss-Hermite "
                 "extreme-value order statistic. The exact model is NOT tighter than a trivial single-draw "
                 "baseline (rel_improve=%.3f < %.2f) -- the decode collapse is NOT governed by the extreme-"
                 "value-of-V mechanism the order statistic encodes. MECHANISM: sparse block-local GSBC "
                 "distractor scores have a LIGHT (sub-Gaussian) upper tail, so the Gaussian order statistic "
                 "OVER-predicts the max (exact p1 mean_ratio=%s) and the error compounds through the D-fold "
                 "decode product (decode_part ratio up to %sx). Convergent with the encoder power-law accept-"
                 "boundary (GSBC-heterogeneity). This is a mechanistically-named boundary, NOT a machinery "
                 "failure: " % (rel_improve, ACCEPT_REL_MAX, exact_mean_ratio,
                                extra["decode_part_compounding_max_ratio_err"])) + summ, extra)
    if not (HF_BIAS_LO <= exact_mean_ratio <= HF_BIAS_HI):
        return ("HARD_FAIL",
                ("ACCEPT_BOUNDARY: exact aggregate mean-ratio=%.3f OUTSIDE [%.2f,%.2f] -- the extreme-value "
                 "order statistic is BIASED for comprehension order-recovery (sparse-GSBC light tail). "
                 % (exact_mean_ratio, HF_BIAS_LO, HF_BIAS_HI)) + summ, extra)
    if max_exact_err is not None and max_exact_err > HF_RATIO_MAX:
        return ("HARD_FAIL",
                ("ACCEPT_BOUNDARY: exact per-cell ratio-err %.3fx > %.2fx -- the order statistic breaks at "
                 "the deep corner (sparse-GSBC light tail). " % (max_exact_err, HF_RATIO_MAX)) + summ, extra)

    # ---- HARD_PASS gate (H confirmed -- comprehension joins the exact self-margin family) ----
    hp = (max_exact_err is not None and max_exact_err <= HP_RATIO_MAX
          and HP_BIAS_LO <= exact_mean_ratio <= HP_BIAS_HI
          and rel_improve >= REL_IMPROVE_MIN
          and loose_biased
          and (agg_cv is None or agg_cv <= HP_CV_MAX))
    if hp:
        return ("HARD_PASS",
                ("EXACT COMPREHENSION ORDER-RECOVERY SELF-MARGIN VALID (CG-candidate): the substrate predicts "
                 "its OWN comprehension decode cliff via the extreme-value order statistic. Exact p1 mean_ratio="
                 "%.3f (unbiased [%.2f,%.2f]); per-cell ratio-err <= %.2fx at ALL %d non-saturated cells; "
                 "cross-seed cv=%s. Loose single-draw control stays biased (mean_ratio=%.3f); exact is %sx "
                 "tighter (>= %.2f). Joins RNS/FHRR/reasoning-depth one level up (comprehension). "
                 % (exact_mean_ratio, HP_BIAS_LO, HP_BIAS_HI, HP_RATIO_MAX, n_nonsat, agg_cv,
                    loose_mean_ratio, extra["rel_improve_loose_over_exact"], REL_IMPROVE_MIN)) + summ, extra)

    return ("MIDDLE_BAND",
            ("MIDDLE_BAND: the exact order statistic tightens vs the single-draw control (rel_improve=%.3f in "
             "[%.2f,%.2f)) but misses a HARD_PASS sub-gate (max_err=%s vs %.2f / mean_ratio in [%.2f,%.2f] / "
             "loose_biased=%s / cv=%s vs %.2f). Partially predictive, not exact at every cell. "
             % (rel_improve, ACCEPT_REL_MAX, REL_IMPROVE_MIN, extra["max_exact_ratio_err_p1"], HP_RATIO_MAX,
                HP_BIAS_LO, HP_BIAS_HI, loose_biased, agg_cv, HP_CV_MAX)) + summ, extra)


# ============================================================
# Formula self-test (GH order statistic correctness + off-disk retrospective vs landed comprehension)
# ============================================================
def _formula_selftest() -> Tuple[bool, str]:
    # (a) Phi/logPhi correctness + monotone
    if abs(0.5 * math.erfc(0.0) - 0.5) > 1e-9:
        return False, "PHI_HALF_BROKEN"
    if not (_logPhi(1.0) > _logPhi(0.0) > _logPhi(-1.0)):
        return False, "LOGPHI_NOT_MONOTONE"
    # (b) large-margin signal wins ~ surely for any competitor count
    if p_win_extreme(30.0, 1.0, 0.0, 1.0, 1000.0) < 0.999:
        return False, "LARGE_MARGIN_NOT_WIN"
    # (c) monotone DECREASING in competitor count (more distractors -> lower win prob)
    prev = 2.0
    for n in (1.0, 10.0, 100.0, 1000.0):
        p = p_win_extreme(3.5, 3.9, 0.0, 4.8, n)
        if p > prev + 1e-9:
            return False, "PWIN_NOT_MONOTONE_IN_NCOMP n=%.0f p=%.4f prev=%.4f" % (n, p, prev)
        prev = p
    # (d) exact (n=V-1) <= loose (n=1) pointwise for V>1 (more competitors is harder)
    for V in (50, 250, 1000):
        pe = p_win_extreme(29.7, 3.9, 13.0, 4.8, float(V - 1))
        pl = p_win_extreme(29.7, 3.9, 13.0, 4.8, 1.0)
        if pe > pl + 1e-9:
            return False, "EXACT_ABOVE_LOOSE V=%d exact=%.4f loose=%.4f" % (V, pe, pl)
    return True, "FORMULA_SELFTEST_PASS"


def _retrospective_offdisk() -> Tuple[Optional[bool], str, Dict[str, Any]]:
    """Zero-new-trials retrospective vs the landed comprehension surface. Reproduces the DIRECTION of
    the pre-registered off-disk finding: on non-saturated per-role decode cells, the exact extreme-
    value order statistic is BIASED / NOT tighter than the single-draw loose model (rel_improve <= 1),
    while the D-fold decode_part compounding amplifies the error to >> 1.5x. Skips gracefully if the
    landed metrics OR the GSBC pool are absent (remote)."""
    land = REPO / "data" / "exp_comprehension_envelope_superposition_vocab_v1" / "metrics.json"
    if not land.exists():
        return None, "RETRO_SKIP (landed comprehension metrics absent -- fresh measurement is primary)", {}
    if not base.POOL_PATH.exists():
        return None, "RETRO_SKIP (GSBC pool npz absent -- cannot rebuild geometry for moments)", {}
    try:
        d = json.loads(land.read_text(encoding="utf-8"))
        per = d["per_unit"]
    except (OSError, ValueError, KeyError) as e:
        return None, "RETRO_SKIP (landed metrics unreadable: %s)" % type(e).__name__, {}
    land_seeds = sorted({u["seed"] for u in per})
    land_D = sorted({u["D"] for u in per})
    land_V = sorted({u["V_ROLE"] for u in per})
    # moments per (seed, D)
    mom: Dict[Tuple[int, int], Tuple[float, float, float, float]] = {}
    for seed in land_seeds:
        cb = base._build_cbmax(seed, BS, max(land_V), max(land_D))
        for D in land_D:
            mom[(seed, D)] = measure_moments(seed, D, V_REF, cb)
    # per-cell exact/loose p1 ratios (seed-averaged), non-saturated only
    ex_r, lo_r, dp_r = [], [], []
    for D in land_D:
        mD = tuple(np.mean([mom[(s, D)] for s in land_seeds], axis=0))
        for V in land_V:
            rows = [u for u in per if u["D"] == D and u["V_ROLE"] == V]
            dp = float(np.mean([u["decode_part"] for u in rows]))
            mp1 = dp ** (1.0 / D) if dp > 0 else 0.0
            if not (SAT_LO < mp1 < SAT_HI):
                continue
            pe = p_win_extreme(mD[0], mD[1], mD[2], mD[3], float(V - 1))
            pl = p_win_extreme(mD[0], mD[1], mD[2], mD[3], 1.0)
            if pe > 1e-9:
                ex_r.append(mp1 / pe)
                dp_r.append(_ratio_err(dp / (pe ** D)))
            if pl > 1e-9:
                lo_r.append(mp1 / pl)
    if not ex_r:
        return None, "RETRO_SKIP (no non-saturated landed decode cells)", {}
    ex_gm = _gm([_ratio_err(r) for r in ex_r])
    lo_gm = _gm([_ratio_err(r) for r in lo_r])
    rel = (lo_gm / ex_gm) if (ex_gm and lo_gm) else None
    dp_max = max([x for x in dp_r if x is not None]) if dp_r else None
    info = {"retro_n_cells": len(ex_r), "retro_exact_mean_ratio": round(float(np.mean(ex_r)), 4),
            "retro_loose_mean_ratio": round(float(np.mean(lo_r)), 4),
            "retro_exact_gm_err": round(ex_gm, 4) if ex_gm else None,
            "retro_loose_gm_err": round(lo_gm, 4) if lo_gm else None,
            "retro_rel_improve": round(rel, 4) if rel else None,
            "retro_decode_part_max_ratio_err": round(dp_max, 4) if dp_max else None}
    # EXPECTED direction (pre-registered accept-boundary): exact NOT tighter than loose (rel <= ~1.1)
    # AND decode_part compounding blows up (>> 1.5x). Assert the DIRECTION reproduces.
    direction_ok = (rel is not None and rel <= 1.15 and dp_max is not None and dp_max >= 1.5)
    msg = ("RETRO n=%d exact_mean_ratio=%.3f (over-predicts) loose_mean_ratio=%.3f exact_gm=%.3f "
           "loose_gm=%.3f rel_improve=%.3f (<=~1 EXPECTED) decode_part_max_err=%.2fx -> %s"
           % (len(ex_r), info["retro_exact_mean_ratio"], info["retro_loose_mean_ratio"],
              ex_gm, lo_gm, rel, dp_max, "ACCEPT_BOUNDARY_DIRECTION_CONFIRMED" if direction_ok else "UNEXPECTED"))
    return direction_ok, msg, info


# ============================================================
# Driver
# ============================================================
def run_all(out_dir: Path, t0: float) -> List[Dict[str, Any]]:
    per_unit: List[Dict[str, Any]] = []
    total = len(SEEDS) * len(D_GRID) * len(V_GRID)
    unit = 0
    for seed in SEEDS:
        cb_max = base._build_cbmax(seed, BS, V_ROLE_MAX, D_MAX)   # one geometry build per seed
        moments = {D: measure_moments(seed, D, V_REF, cb_max) for D in D_GRID}
        _say("  [seed %d] cb_max + moments built" % seed)
        for D in D_GRID:
            for V in V_GRID:
                r = run_unit(seed, D, V, cb_max, moments[D])
                per_unit.append(r)
                unit += 1
                _heartbeat(out_dir, unit, total, t0,
                           extra={"seed": seed, "D": D, "V": V, "meas_p1": r["meas_p1"],
                                  "p1_exact": r["p1_exact"], "ratio_exact_p1": r["ratio_exact_p1"]})
                _say("    [seed %d D=%d V=%d L=%d] decode_part=%.3f meas_p1=%.4f | p1_exact=%.4f "
                     "p1_loose=%.4f | r_exact=%s r_loose=%s%s"
                     % (seed, D, V, D // 2, r["decode_part"], r["meas_p1"], r["p1_exact"], r["p1_loose"],
                        r["ratio_exact_p1"], r["ratio_loose_p1"], " [SAT]" if r["saturated"] else ""))
    return per_unit


def _run(mode: str) -> int:
    out_dir = _out_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    _write_start_marker(out_dir, mode, EXPECTED_N_UNITS)
    _say("[%s] mode=%s N=%d B=%d bs=%d D_grid=%s V_grid=%s seeds=%s trials=%d V_REF=%d expected_units=%d"
         % (ANCHOR_NAME, mode, N_DIM, B_TOTAL, BS, D_GRID, V_GRID, SEEDS, TRIALS, V_REF, EXPECTED_N_UNITS))

    ok_f, msg_f = _formula_selftest()
    if not ok_f:
        raise AssertionError("FORMULA_SELFTEST_FAIL: " + msg_f)
    _say("[formula] " + msg_f)
    retro_ok, retro_msg, retro_info = _retrospective_offdisk()
    _say("[retro] " + retro_msg)

    per_unit = run_all(out_dir, t0)
    verdict, vmsg, extra = compute_verdict(per_unit, len(per_unit))
    extra["formula_selftest"] = msg_f
    extra["retrospective_offdisk"] = retro_msg
    extra["retrospective_info"] = retro_info
    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg,
        "summary": "%s: comprehension order-recovery EXACT self-margin (extreme-value order statistic) (%s)"
                   % (verdict, mode),
        "run_mode": mode, "elapsed_s": round(elapsed, 2),
        "n_seeds": len(SEEDS), "n_units": len(per_unit), "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": len(per_unit) >= EXPECTED_N_UNITS,
        "arms_differ_verified": extra.get("arms_differ_verified", False),
        "config_version": CONFIG_VERSION,
        "config": {"N": N_DIM, "B_TOTAL": B_TOTAL, "bs": BS, "D_grid": D_GRID, "V_grid": V_GRID,
                   "seeds": SEEDS, "trials": TRIALS, "V_REF": V_REF,
                   "predictor": "GH64_extreme_value_order_statistic",
                   "loose": "single_draw_n_comp=1_V_independent",
                   "measurement": "base.run_unit_VERBATIM (exp_comprehension_envelope_superposition_vocab_v1)",
                   "target": "per_role_decode_p1 = decode_part^(1/D)",
                   "kb_referent_declared": False},
        "hp_scope": {"exact": ["ratio_err<=HP_RATIO_MAX", "mean_ratio_unbiased", "rel_improve>=1.5", "cv<=0.15"],
                     "loose": ["loose_biased_direction_gate_only"]},
        "extra": extra, "per_unit": per_unit,
        "ts_iso": _now_iso(), "pid": os.getpid(), "host": platform.node(),
    }
    _write_metrics_atomic(out_dir, metrics)
    written = json.load(open(out_dir / "metrics.json"))
    assert written["run_mode"] == mode, "RUN_MODE_MISMATCH %s != %s" % (written["run_mode"], mode)

    _say("\n[%s] %s: %s" % (ANCHOR_NAME, verdict, vmsg))
    _say("[%s] metrics -> %s  elapsed=%.1fs" % (ANCHOR_NAME, out_dir / "metrics.json", elapsed))
    return 0


def _run_selftest() -> int:
    t0 = time.perf_counter()
    ok_f, msg_f = _formula_selftest()
    assert ok_f, "FORMULA_SELFTEST_FAIL: " + msg_f
    retro_ok, retro_msg, _info = _retrospective_offdisk()
    # A tiny geometry-measure sanity: moments computable + ordered (mu_s > mu_d, sig_d > 0).
    cb = base._build_cbmax(7, BS, max(V_GRID + [V_REF]), max(D_GRID))
    mu_s, sig_s, mu_d, sig_d = measure_moments(7, 8, V_REF, cb)
    geom_ok = (mu_s > mu_d > 0 and sig_d > 0)
    # A tiny end-to-end unit.
    r = run_unit(7, 8, 1000, cb, (mu_s, sig_s, mu_d, sig_d))
    unit_ok = (0.0 <= r["meas_p1"] <= 1.0 and r["p1_exact"] <= r["p1_loose"] + 1e-9)
    ok = ok_f and geom_ok and unit_ok and (retro_ok is not False)
    _say("[%s] SELFTEST %s: formula=%s | geom(D8) mu_s=%.2f mu_d=%.2f sig_d=%.2f ok=%s | "
         "unit(D8V1000) meas_p1=%.4f p1_exact=%.4f p1_loose=%.4f ok=%s | %s [%.1fs]"
         % (ANCHOR_NAME, "PASS" if ok else "FAIL", msg_f, mu_s, mu_d, sig_d, geom_ok,
            r["meas_p1"], r["p1_exact"], r["p1_loose"], unit_ok, retro_msg, time.perf_counter() - t0))
    return 0 if ok else 1


def main() -> int:
    if RUN_MODE == "self_test":
        return _run_selftest()
    return _run(RUN_MODE)


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
