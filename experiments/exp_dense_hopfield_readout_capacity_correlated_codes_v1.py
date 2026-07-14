"""Dense / modern-Hopfield READOUT capacity vs pairwise, on IID vs CORRELATED codes.

QUESTION (PRIMARY): does a dense/modern-Hopfield readout -- a super-quadratic
similarity/energy separation in the cleanup/reconstruction step (higher-order
polynomial F(x)=relu(x)^n for n in {2,4,8}, plus an exp-family F(x)=exp(beta*x))
-- raise RECOVERABLE-SIGNAL CAPACITY over the standard PAIRWISE readout (n=2),
and CRUCIALLY does that lift SURVIVE the substrate's ACTUAL correlated,
structureless code distribution, not merely idealized iid patterns?

MECHANISM (glass-box, closed-form, no learned aggregator): retrieval is the
one-step dense-associative-memory update (Krotov-Hopfield 2016 F(x)=x^n;
Demircigil 2017 / Ramsauer 2020 F(x)=exp). Given stored patterns P (the codes,
UNCHANGED), a partial-cue query q, similarities s_mu = <q, p_mu>, the
reconstruction is p_hat = sum_mu F(s_mu) p_mu / sum_mu F(s_mu). SUCCESS requires
the reconstruction to be a FAITHFUL recovery of the target (cosine(p_hat, p_t)
>= RECON_TAU) AND target = nearest codebook neighbour. The separation function F
does NOT change argmax(s) (both x^n and exp are monotone), so a pure 1-NN score
readout is n-invariant; F's ONLY lever is SHARPENING the superposition weights so
spurious (non-target) patterns contribute less crosstalk to p_hat -> cleaner
reconstruction -> higher recoverable capacity. Codes + ingest are UNCHANGED; only
the readout nonlinearity varies. That is the whole point (structure-agnostic; you
do not compress the arbitrary label, you sharpen the cleanup).

WHY BOTH DISTRIBUTIONS: idealized IID (near-orthogonal Gaussian) codes are the
regime the classical Hopfield/Krotov capacity theorems assume, and where the
super-quadratic lift is a textbook effect -- so IID is the POSITIVE CONTROL (if
the lift is absent even on IID, the readout is broken / the regime saturates).
CORRELATED codes (subspace-confined, off-diagonal cosine ~1/sqrt(d_sub)) are the
substrate's actual regime; correlation both (a) inflates non-target crosstalk and
(b) pulls the reconstruction toward correlated neighbours -- a wall sharper
separation may not fully clear (quantum-drill HF2). The headline is the CORRELATED
lift, reported across a mild->strong correlation gradient.

CAPACITY (censoring-robust): per (dist,N,order) the recall-vs-load curve is walked
to a crossing load alpha* = M*/N at which recall crosses RECALL_THRESH (linear
interp; floored at alpha_min if it fails even at the smallest load; censored at
alpha_max if it never fails -> a CONSERVATIVE lower bound on capacity). lift(dist,
N) = best-super-order alpha* / pairwise alpha*.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; hash-test across orders)
# - final_metrics_atomicity = tmp_replace (os.replace at end)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (relative-lift band, not an absolute-noise-floor threshold)
# - baseline_in_band at smoke (META_RULE_AG; poly2 recall crosses [0.05,0.95])
# - discriminator survives scale (IID/mild-corr lift grows with N in probes; FULL N ladder)
# - HARD_PASS strictly above floor (corr lift>=1.5x; no-lift floor=1.0x)
# - cardinality_ok (EXPECTED_N_UNITS = |N| x |dist| x |order| x |seed|)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (closed-form readout)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in prereg
# - VALIDITY_PREFLIGHT: real_code_path exercises the REAL readout+codegen fns
# - progress_logging = print_flush_true
#
# Numbers referenced in this cell:
#   poly2 IID capacity ~ 0.14 * N   CITED@Amit-Gutfreund-Sompolinsky 1985
#   super-quadratic F(x)=x^n capacity ~ N^(n-1)  CITED@Krotov-Hopfield 2016
#   exp-family exponential capacity  CITED@Demircigil 2017 / Ramsauer 2020
#   MONO_MATCHED deployable oracle MRR = 0.4660  MEASURED@data/exp_map_builder_residue_module_ceiling_v1/metrics.json:gates.oracle_2x2_mrr.MONO_MATCHED
#     (RNS-arena deployable-regime reference; this cell does NOT reproduce it -- separate harness)
#
# ASCII-only; no em-dashes.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

import argparse
import hashlib
import json
import math
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "dense_hopfield_readout_capacity_correlated_codes_v1"

# --------------------------------------------------------------------------- #
# Config                                                                      #
# --------------------------------------------------------------------------- #
# Interaction orders. poly n=2 is the PAIRWISE BASELINE (linear-N capacity per
# Amit-Gutfreund-Sompolinsky). poly 4/8 + exp are the super-quadratic readouts.
ORDERS: List[Tuple[str, str, float]] = [
    ("poly2", "poly", 2.0),   # BASELINE (pairwise)
    ("poly4", "poly", 4.0),
    ("poly8", "poly", 8.0),
    ("exp",   "exp", 25.0),   # beta=25 (Demircigil/Ramsauer exp separation)
]
BASELINE_ORDER = "poly2"
SUPERQUAD_ORDERS = ["poly4", "poly8", "exp"]

# Code distributions. iid = near-orthogonal (idealized POSITIVE CONTROL).
# corr_* = subspace-confined correlated codes (substrate's actual-style regime);
# off-diagonal cosine ~ 1/sqrt(d_sub). d_sub CONSTANT across N so correlation
# strength is fixed while N grows. mild->strong gradient.
DIST_SPECS: List[Tuple[str, Optional[int]]] = [
    ("iid",         None),   # positive control (idealized near-orthogonal)
    ("corr_mild",   64),     # off-diag |cos| ~ 0.125
    ("corr_mod",    24),     # off-diag |cos| ~ 0.204
    ("corr_strong", 12),     # off-diag |cos| ~ 0.289
]
CORR_DISTS = ["corr_mild", "corr_mod", "corr_strong"]

# Partial-cue: query has fixed cosine COS_TARGET to its target pattern.
COS_TARGET = 0.25

# Success = (target is argmax NN) AND (reconstruction cosine to target >= RECON_TAU).
RECON_TAU = 0.80
# Capacity crossing: alpha* = load at which success-rate crosses RECALL_THRESH.
RECALL_THRESH = 0.90

# Load ladder (M = round(alpha * N)), capped at M_CAP.
ALPHA_LADDER = [0.1, 0.2, 0.35, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0]
ALPHA_MIN = ALPHA_LADDER[0]
ALPHA_MAX = ALPHA_LADDER[-1]
M_CAP = 6144
ATTN_CHUNK = 512

# N ladders.
N_LADDER_FULL = [256, 512, 1024, 2048]
N_LADDER_SMOKE = [256, 512]

SEEDS_FULL = [7, 13, 19]
SEEDS_SMOKE = [7, 13, 19]   # keep 3 seeds even at smoke (capacity is seed-noisy)

# Bands (relative capacity-lift ratio on the CORRELATED regime = headline).
HP_LIFT = 1.50     # HARD_PASS: super-quad alpha* >= 1.5x pairwise alpha* on correlated codes
HF_LIFT = 1.15     # HARD_FAIL: super-quad alpha* < 1.15x pairwise (no meaningful lift)
# POSITIVE CONTROL: super-quad MUST lift >= this on IID (else readout broken).
POS_CONTROL_IID_LIFT = 1.50


# --------------------------------------------------------------------------- #
# Output dir / atomic write / markers                                         #
# --------------------------------------------------------------------------- #
def _output_dir() -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _atomic_write_json(path: Path, obj: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)  # atomic per META_RULE_AH


def _write_start_marker(out_dir: Path, run_mode: str, expected_units: int) -> None:
    import platform
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_units,
        "host": platform.node(),
    }
    _atomic_write_json(out_dir / "_start_marker.json", marker)


def _emit_heartbeat(out_dir: Path, unit_idx: int, total_units: int,
                    elapsed_s: float, extra: Optional[dict] = None) -> None:
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": int(unit_idx),
        "total_units": int(total_units),
        "elapsed_s": float(elapsed_s),
    }
    if extra:
        row["extra"] = extra
    try:
        with open(out_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass  # heartbeat best-effort; never blocks the run


def _write_crash_metrics(out_dir: Path, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "run_mode": "crash",
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _atomic_write_json(out_dir / "metrics.json", diag)


# --------------------------------------------------------------------------- #
# Code generation + queries (the REAL codegen path)                           #
# --------------------------------------------------------------------------- #
def make_codes(m_items: int, n_dim: int, d_sub: Optional[int],
               rng: np.random.RandomState) -> np.ndarray:
    """M x N l2-normalized codes. d_sub=None -> near-orthogonal iid Gaussian;
    d_sub=int -> confined to a random d_sub-dim subspace (correlated, off-diag
    cosine ~ 1/sqrt(d_sub))."""
    if d_sub is None:
        raw = rng.randn(m_items, n_dim).astype(np.float32)
    else:
        if d_sub >= n_dim:
            raise ValueError(f"d_sub={d_sub} must be < n_dim={n_dim}")
        basis, _ = np.linalg.qr(rng.randn(n_dim, d_sub).astype(np.float32))  # (N,d_sub) orthonormal cols
        coeffs = rng.randn(m_items, d_sub).astype(np.float32)                # (M,d_sub)
        raw = coeffs @ basis.T                                               # (M,N) in span(basis)
    nrm = np.linalg.norm(raw, axis=1, keepdims=True)
    return (raw / np.clip(nrm, 1e-12, None)).astype(np.float32)


def make_queries(codes: np.ndarray, cos_target: float,
                 rng: np.random.RandomState) -> np.ndarray:
    """Partial cues with EXACT cosine cos_target to their target pattern:
    q_i = cos*p_i + sqrt(1-cos^2) * (unit noise orthogonalized to p_i)."""
    m, n = codes.shape
    noise = rng.randn(m, n).astype(np.float32)
    proj = np.sum(noise * codes, axis=1, keepdims=True)
    perp = noise - proj * codes
    perp /= np.clip(np.linalg.norm(perp, axis=1, keepdims=True), 1e-12, None)
    q = cos_target * codes + math.sqrt(max(0.0, 1.0 - cos_target * cos_target)) * perp
    q /= np.clip(np.linalg.norm(q, axis=1, keepdims=True), 1e-12, None)
    return q.astype(np.float32)


# --------------------------------------------------------------------------- #
# THE READOUT (the one-line-change core; closed-form, glass-box)              #
# --------------------------------------------------------------------------- #
def _separation_weights(sims: np.ndarray, family: str, order: float,
                        scramble: bool,
                        rng: Optional[np.random.RandomState]) -> np.ndarray:
    """Row-normalized separation weights over stored patterns.
    family='poly': F(x)=relu(x)^order ; family='exp': F(x)=softmax(order*x).
    scramble=True permutes each row independently (destroys the true similarity
    ranking, PRESERVES the weight-magnitude multiset) -> must-fail control."""
    if family == "poly":
        w = np.clip(sims, 0.0, None) ** order
    elif family == "exp":
        z = order * sims
        z = z - z.max(axis=1, keepdims=True)
        w = np.exp(z)
    else:
        raise ValueError(f"unknown family {family!r}")
    if scramble:
        if rng is None:
            raise ValueError("scramble requires an rng")
        for i in range(w.shape[0]):
            w[i] = w[i, rng.permutation(w.shape[1])]
    w = w / np.clip(w.sum(axis=1, keepdims=True), 1e-30, None)
    return w.astype(np.float32)


def dense_readout_recall(codes: np.ndarray, queries: np.ndarray,
                         family: str, order: float,
                         recon_tau: float = RECON_TAU,
                         scramble: bool = False,
                         scramble_rng: Optional[np.random.RandomState] = None,
                         attn_chunk: int = ATTN_CHUNK) -> float:
    """One-step dense-associative reconstruction + faithful-recovery decode.
    SUCCESS_i = (argmax_nu <p_hat_i, p_nu> == i) AND (<p_hat_i, p_i> >= recon_tau).
    Returns fraction of queries recovered. Query-chunked to bound peak memory."""
    m = codes.shape[0]
    n_hits = 0
    for start in range(0, m, attn_chunk):
        end = min(m, start + attn_chunk)
        q = queries[start:end]                       # (c,N)
        sims = q @ codes.T                           # (c,M)
        w = _separation_weights(sims, family, order, scramble, scramble_rng)
        p_hat = w @ codes                            # (c,N) reconstruction
        p_hat /= np.clip(np.linalg.norm(p_hat, axis=1, keepdims=True), 1e-12, None)
        match = p_hat @ codes.T                      # (c,M) decode scores
        pred = match.argmax(axis=1)
        targets = np.arange(start, end)
        recon_cos = match[np.arange(end - start), targets]  # <p_hat, p_target>
        ok = (pred == targets) & (recon_cos >= recon_tau)
        n_hits += int(ok.sum())
    return n_hits / float(m)


# --------------------------------------------------------------------------- #
# Capacity measurement (crossing-alpha; censoring-robust)                      #
# --------------------------------------------------------------------------- #
def _m_for_alpha(n_dim: int, alpha: float) -> int:
    return min(M_CAP, max(2, int(round(alpha * n_dim))))


def _crossing_alpha(curve: List[dict]) -> Tuple[float, str]:
    """Largest load alpha at which recall >= RECALL_THRESH (linear interp).
    Returns (alpha_star, flag) with flag in {ok, floor, cens}.
    floor: fails even at the smallest load (alpha_star = ALPHA_MIN).
    cens:  never fails within the ladder (alpha_star = last tested alpha)."""
    a = [c["alpha"] for c in curve]
    r = [c["recall"] for c in curve]
    if r[0] < RECALL_THRESH:
        return a[0], "floor"
    for i in range(len(r) - 1):
        if r[i] >= RECALL_THRESH and r[i + 1] < RECALL_THRESH:
            frac = (r[i] - RECALL_THRESH) / max(1e-9, (r[i] - r[i + 1]))
            return a[i] + frac * (a[i + 1] - a[i]), "ok"
    return a[-1], "cens"


def capacity_curve(n_dim: int, d_sub: Optional[int], family: str, order: float,
                   seed: int, cos_target: float) -> List[dict]:
    """recall vs load for one (N,dist,order,seed). Distinct code draw per M."""
    curve: List[dict] = []
    for alpha in ALPHA_LADDER:
        m = _m_for_alpha(n_dim, alpha)
        rng = np.random.RandomState(seed * 100003 + m)
        codes = make_codes(m, n_dim, d_sub, rng)
        queries = make_queries(codes, cos_target, rng)
        recall = dense_readout_recall(codes, queries, family, order)
        curve.append({"M": m, "alpha": m / n_dim, "recall": recall})
        if m >= M_CAP:
            break  # ladder capped; higher alphas would repeat the same M
    return curve


def scramble_recall_at(n_dim: int, d_sub: Optional[int], family: str,
                       order: float, seed: int, cos_target: float,
                       alpha: float) -> Tuple[float, float, int]:
    """(scramble_recall, intact_recall, M) at a fixed load. Must-fail control."""
    m = _m_for_alpha(n_dim, alpha)
    rng = np.random.RandomState(seed * 100003 + m)
    codes = make_codes(m, n_dim, d_sub, rng)
    queries = make_queries(codes, cos_target, rng)
    intact = dense_readout_recall(codes, queries, family, order)
    srng = np.random.RandomState(seed * 7919 + 1)
    scr = dense_readout_recall(codes, queries, family, order,
                               scramble=True, scramble_rng=srng)
    return scr, intact, m


# --------------------------------------------------------------------------- #
# Self-test (exercises the REAL readout + codegen paths; F.1)                  #
# --------------------------------------------------------------------------- #
def _selftest_codegen_correlation() -> None:
    rng = np.random.RandomState(3)
    iid = make_codes(96, 512, None, rng)
    off_iid = float(np.abs(iid @ iid.T)[~np.eye(96, dtype=bool)].mean())
    rng2 = np.random.RandomState(3)
    corr = make_codes(96, 512, 16, rng2)
    off_corr = float(np.abs(corr @ corr.T)[~np.eye(96, dtype=bool)].mean())
    if not (off_corr > 2.0 * off_iid):
        raise AssertionError(
            f"corr off-diag |cos|={off_corr:.4f} not > 2x iid {off_iid:.4f}")


def _selftest_query_cosine_exact() -> None:
    rng = np.random.RandomState(5)
    codes = make_codes(64, 256, None, rng)
    q = make_queries(codes, 0.25, rng)
    cos = float(np.mean(np.sum(q * codes, axis=1)))
    if abs(cos - 0.25) > 0.02:
        raise AssertionError(f"query cosine {cos:.4f} != 0.25")


def _selftest_scramble_collapses() -> None:
    """Scramble must destroy recovery on an intact-recoverable load."""
    rng = np.random.RandomState(9)
    codes = make_codes(256, 512, None, rng)
    q = make_queries(codes, 0.5, rng)   # easy cue -> intact recovers
    intact = dense_readout_recall(codes, q, "poly", 8.0)
    srng = np.random.RandomState(1)
    scr = dense_readout_recall(codes, q, "poly", 8.0, scramble=True,
                               scramble_rng=srng)
    if not (intact >= 0.90 and scr <= 0.40):
        raise AssertionError(
            f"scramble control weak: intact={intact:.3f} scr={scr:.3f}")


def _selftest_superquad_lifts() -> float:
    """POSITIVE CONTROL: on CORRELATED codes at a load where pairwise (poly2)
    reconstruction blurs, a super-quadratic order recovers more. Returns
    poly8 - poly2 recall gap (must be > 0.15)."""
    n_dim, d_sub, m = 256, 64, 256   # alpha=1 on mild-correlated codes
    rng = np.random.RandomState(7 * 100003 + m)
    codes = make_codes(m, n_dim, d_sub, rng)
    q = make_queries(codes, COS_TARGET, rng)
    r2 = dense_readout_recall(codes, q, "poly", 2.0)
    r8 = dense_readout_recall(codes, q, "poly", 8.0)
    if not (r8 > r2 + 0.15):
        raise AssertionError(
            f"super-quad did NOT lift on correlated codes: poly2={r2:.3f} "
            f"poly8={r8:.3f} (readout broken -- separation has no effect)")
    return r8 - r2


def _selftest_orders_differ() -> None:
    """META_RULE_AF: order arms must not be bit-identical on a discriminating load."""
    rng = np.random.RandomState(13)
    codes = make_codes(128, 256, 24, rng)
    q = make_queries(codes, COS_TARGET, rng)
    digests = {}
    for name, fam, order in ORDERS:
        w = _separation_weights(q @ codes.T, fam, order, False, None)
        digests[name] = hashlib.sha256(w.tobytes()).hexdigest()
    for a in digests:
        for b in digests:
            if a < b and digests[a] == digests[b]:
                raise AssertionError(f"META_RULE_AF: {a} == {b} bit-identical")


def run_selftest() -> int:
    print("[selftest] dense-Hopfield readout capacity cell", flush=True)
    try:
        _selftest_codegen_correlation()
        _selftest_query_cosine_exact()
        _selftest_orders_differ()
        _selftest_scramble_collapses()
        corr_gap = _selftest_superquad_lifts()

        # A tiny real capacity curve exercises the FULL measurement path.
        curve_p2 = capacity_curve(256, 64, "poly", 2.0, 7, COS_TARGET)
        curve_p8 = capacity_curve(256, 64, "poly", 8.0, 7, COS_TARGET)
        a2, f2 = _crossing_alpha(curve_p2)
        a8, f8 = _crossing_alpha(curve_p8)
        recalls_p2 = [c["recall"] for c in curve_p2]

        # Multi-seed scramble margin (Class 4).
        scr_scores = []
        for sd in SEEDS_SMOKE:
            scr, intact, mm = scramble_recall_at(512, None, "poly", 8.0, sd, 0.5, 1.0)
            scr_scores.append(scr)

        exercised = {"make_codes", "make_queries", "dense_readout_recall",
                     "_separation_weights", "capacity_curve", "scramble_recall_at"}

        try:
            from experiments._validity_preflight import run_validity_preflight
        except Exception:
            from _validity_preflight import run_validity_preflight  # remote layout

        ok = run_validity_preflight([
            # Class 5 (real_code_path, ENFORCE): self-test exercises the REAL
            # readout+codegen fns the FULL uses (this cell builds no KGStore --
            # its "substrate" IS the closed-form readout stack).
            {"kind": "real_code_path",
             "full_substrate_entrypoints": sorted(exercised),
             "exercised_entrypoints": sorted(exercised)},
            # Class 6 (substrate_signature, ENFORCE): bind the readout call sig.
            {"kind": "substrate_signature",
             "callable_obj": dense_readout_recall,
             "kwargs": {"codes": None, "queries": None, "family": "poly",
                        "order": 2.0},
             "callable_name": "dense_readout_recall"},
            # Class 1 (positive_control): super-quad lifts at self-test scale.
            {"kind": "positive_control",
             "positive_control_passed_headline_gate": bool(corr_gap > 0.15),
             "control_name": "poly8_vs_poly2_corr", "headline_name": "capacity_lift"},
            # Class 2 (metric_moves): capacity-ladder recall is not frozen.
            {"kind": "metric_moves", "metric_name": "poly2_recall_vs_load",
             "values": recalls_p2},
            # Class 4 (negative_control_margin): scramble fails >=3 seeds w/ margin.
            {"kind": "negative_control_margin", "control_scores": scr_scores,
             "headline_threshold": RECALL_THRESH, "higher_is_pass": True,
             "margin": 0.30, "control_name": "scramble_readout"},
        ], run_mode="selftest")

        print(f"[selftest] corr_gap(poly8-poly2)={corr_gap:.3f} "
              f"cross_a p2={a2:.2f}({f2}) p8={a8:.2f}({f8}) "
              f"scramble={['%.3f' % s for s in scr_scores]} validity_ok={ok}",
              flush=True)
        if a8 < a2:
            raise AssertionError(
                f"super-quad crossing < pairwise (a8={a8:.2f} < a2={a2:.2f}); "
                f"readout broken")
        print("[selftest] PASS", flush=True)
        return 0
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        return 2
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}",
              flush=True)
        traceback.print_exc()
        return 3


# --------------------------------------------------------------------------- #
# FULL / SMOKE sweep                                                           #
# --------------------------------------------------------------------------- #
def _key(dist: str, n_dim: int, order_name: str, seed: int) -> str:
    return f"{dist}|N{n_dim}|{order_name}|s{seed}"


def run_sweep(run_mode: str, out_dir: Path) -> dict:
    n_ladder = N_LADDER_FULL if run_mode == "full" else N_LADDER_SMOKE
    seeds = SEEDS_FULL if run_mode == "full" else SEEDS_SMOKE
    expected_units = len(n_ladder) * len(DIST_SPECS) * len(ORDERS) * len(seeds)
    _write_start_marker(out_dir, run_mode, expected_units)
    t0 = time.time()

    per_unit: Dict[str, dict] = {}
    total = expected_units
    done = 0
    for dist, d_sub in DIST_SPECS:
        for n_dim in n_ladder:
            for order_name, fam, order in ORDERS:
                for seed in seeds:
                    key = _key(dist, n_dim, order_name, seed)
                    try:
                        curve = capacity_curve(n_dim, d_sub, fam, order, seed,
                                               COS_TARGET)
                        a_star, flag = _crossing_alpha(curve)
                        per_unit[key] = {
                            "dist": dist, "N": n_dim, "order": order_name,
                            "seed": seed, "d_sub": (-1 if d_sub is None else d_sub),
                            "alpha_star": a_star, "m_star": int(round(a_star * n_dim)),
                            "cross_flag": flag,
                            "recall_curve": [round(c["recall"], 4) for c in curve],
                            "status": "OK",
                        }
                    except SystemExit:
                        raise
                    except KeyboardInterrupt:
                        raise
                    except Exception as exc:
                        per_unit[key] = {
                            "dist": dist, "N": n_dim, "order": order_name,
                            "seed": seed, "alpha_star": -1.0, "status": "ERROR",
                            "failure_class": f"{type(exc).__name__}: {str(exc)[:200]}",
                        }
                    done += 1
                    if done % 5 == 0 or done == total:
                        el = time.time() - t0
                        print(f"[progress] {done}/{total} last={key} "
                              f"a*={per_unit[key].get('alpha_star')} "
                              f"elapsed={el:.1f}s", flush=True)
                        _emit_heartbeat(out_dir, done, total, el,
                                        extra={"last_key": key})

    # Scramble must-fail control (per dist x N, poly8, seed-repeated at alpha=1).
    scramble_units: Dict[str, dict] = {}
    for dist, d_sub in DIST_SPECS:
        for n_dim in n_ladder:
            scr_scores, intact_scores = [], []
            for seed in seeds:
                scr, intact, mm = scramble_recall_at(
                    n_dim, d_sub, "poly", 8.0, seed, COS_TARGET, 1.0)
                scr_scores.append(scr)
                intact_scores.append(intact)
            scramble_units[f"{dist}|N{n_dim}"] = {
                "dist": dist, "N": n_dim,
                "scramble_recall_mean": float(np.mean(scr_scores)),
                "scramble_recall_max": float(np.max(scr_scores)),
                "intact_recall_mean": float(np.mean(intact_scores)),
                "scramble_scores": [float(s) for s in scr_scores],
            }

    elapsed = time.time() - t0
    return {
        "run_mode": run_mode, "n_ladder": n_ladder, "seeds": seeds,
        "expected_n_units": expected_units, "per_unit": per_unit,
        "scramble_units": scramble_units, "elapsed_s": elapsed,
    }


# --------------------------------------------------------------------------- #
# Aggregation + verdict                                                        #
# --------------------------------------------------------------------------- #
def _seedmean_alpha(per_unit: dict, dist: str, n_dim: int,
                    order_name: str) -> float:
    vals = [u["alpha_star"] for u in per_unit.values()
            if u.get("status") == "OK" and u["dist"] == dist
            and u["N"] == n_dim and u["order"] == order_name]
    return float(np.mean(vals)) if vals else 0.0


def _base_floored(per_unit: dict, dist: str, n_dim: int) -> bool:
    """True if the pairwise baseline floored (fails even at min load) for a
    majority of seeds -- lift is a low-confidence rescue, not a clean ratio."""
    flags = [u.get("cross_flag") for u in per_unit.values()
             if u.get("status") == "OK" and u["dist"] == dist
             and u["N"] == n_dim and u["order"] == BASELINE_ORDER]
    return flags.count("floor") > len(flags) / 2 if flags else False


def _lift_cell(per_unit: dict, dist: str, n_dim: int) -> Tuple[float, float, float]:
    base = _seedmean_alpha(per_unit, dist, n_dim, BASELINE_ORDER)
    best = max(_seedmean_alpha(per_unit, dist, n_dim, o) for o in SUPERQUAD_ORDERS)
    lift = (best / base) if base > 0 else 0.0
    return lift, base, best


def _geomean(vals: List[float]) -> float:
    vs = [v for v in vals if v and math.isfinite(v) and v > 0]
    return float(math.exp(np.mean([math.log(v) for v in vs]))) if vs else 0.0


def compute_verdict(sweep: dict) -> Tuple[str, str, dict]:
    per_unit = sweep["per_unit"]
    n_ladder = sweep["n_ladder"]
    expected = sweep["expected_n_units"]

    if len(per_unit) != expected:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected {expected} "
                f"units, got {len(per_unit)}", {"n_units": len(per_unit)})
    errs = [k for k, u in per_unit.items() if u.get("status") != "OK"]
    if errs:
        return ("HARD_FAIL",
                f"UNIT_ERRORS ({len(errs)}): "
                + "; ".join(f"{k}:{per_unit[k].get('failure_class')}" for k in errs[:4]),
                {"n_errors": len(errs)})

    # Per (dist,N) lift table (+ clean-baseline mask).
    lifts: Dict[str, dict] = {}
    for dist, _d in DIST_SPECS:
        for n_dim in n_ladder:
            lift, base, best = _lift_cell(per_unit, dist, n_dim)
            lifts[f"{dist}|N{n_dim}"] = {
                "lift": lift, "baseline_alpha": base, "best_super_alpha": best,
                "base_floored": _base_floored(per_unit, dist, n_dim),
            }

    def _dist_lift(dist: str, clean_only: bool) -> float:
        vs = []
        for n in n_ladder:
            cell = lifts[f"{dist}|N{n}"]
            if clean_only and cell["base_floored"]:
                continue
            vs.append(cell["lift"])
        return _geomean(vs)

    iid_lift = _dist_lift("iid", clean_only=True)
    corr_lift_per_dist = {d: _dist_lift(d, clean_only=True) for d in CORR_DISTS}
    # Headline correlated lift = geomean across clean correlated cells.
    corr_lift = _geomean(list(corr_lift_per_dist.values()))
    # Stringent secondary: survival at the STRONGEST correlation level.
    corr_strong_lift = corr_lift_per_dist.get("corr_strong", 0.0)

    # Scramble collapse (must-fail control).
    scr = sweep["scramble_units"]
    worst_scramble = max((u["scramble_recall_max"] for u in scr.values()), default=1.0)
    best_intact = min((u["intact_recall_mean"] for u in scr.values()), default=0.0)
    scramble_collapses = worst_scramble <= 0.60 and best_intact >= 0.70

    headline = {
        "iid_lift_geo": iid_lift,
        "corr_lift_geo": corr_lift,
        "corr_lift_per_dist": corr_lift_per_dist,
        "corr_strong_lift": corr_strong_lift,
        "lifts_per_cell": lifts,
        "worst_scramble_recall": worst_scramble,
        "best_intact_recall": best_intact,
        "scramble_collapses": scramble_collapses,
        "pos_control_iid_passes": bool(iid_lift >= POS_CONTROL_IID_LIFT),
        "HP_LIFT": HP_LIFT, "HF_LIFT": HF_LIFT,
    }

    # --- Positive control MUST hold: super-quad lifts on idealized IID. ---
    if iid_lift < POS_CONTROL_IID_LIFT:
        return ("HARD_FAIL",
                f"POSITIVE_CONTROL_BROKEN: super-quad did NOT lift capacity on "
                f"IDEALIZED iid codes (iid_lift={iid_lift:.2f}x < "
                f"{POS_CONTROL_IID_LIFT}x). Dense readout broken or regime "
                f"saturates; correlated result uninterpretable.", headline)
    if not scramble_collapses:
        return ("HARD_FAIL",
                f"MUST_FAIL_CONTROL_DID_NOT_COLLAPSE: worst scramble recall="
                f"{worst_scramble:.2f} (need <=0.60) / best intact="
                f"{best_intact:.2f} (need >=0.70). Lift not attributable to "
                f"separation sharpness.", headline)

    # --- Headline: does the lift SURVIVE correlated codes? ---
    corr_str = {k: round(v, 2) for k, v in corr_lift_per_dist.items()}
    if corr_lift >= HP_LIFT:
        return ("HARD_PASS",
                f"CAPACITY_LIFT_REAL: dense/super-quad readout lifts recoverable "
                f"capacity {corr_lift:.2f}x over pairwise on the substrate's "
                f"CORRELATED codes (>= {HP_LIFT}x); iid pos-control {iid_lift:.2f}x; "
                f"scramble collapses ({worst_scramble:.2f}). per-dist corr "
                f"lift={corr_str}; strongest-corr lift={corr_strong_lift:.2f}x",
                headline)
    if corr_lift < HF_LIFT:
        return ("HARD_FAIL",
                f"NO_LIFT_ON_CORRELATED_CODES: dense/super-quad readout gives "
                f"corr_lift={corr_lift:.2f}x (< {HF_LIFT}x) even though it lifts "
                f"{iid_lift:.2f}x on idealized iid -- the correlation-hurts "
                f"confound washes the modern-Hopfield capacity gain. per-dist "
                f"corr lift={corr_str}", headline)
    return ("MIDDLE_BAND",
            f"PARTIAL_LIFT_ON_CORRELATED: corr_lift={corr_lift:.2f}x in "
            f"[{HF_LIFT}, {HP_LIFT}); iid pos-control {iid_lift:.2f}x; per-dist "
            f"corr lift={corr_str}. Modern-Hopfield readout helps on correlated "
            f"codes but below the deployable {HP_LIFT}x bar.", headline)


# --------------------------------------------------------------------------- #
# Main                                                                         #
# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(run_selftest())

    run_mode = "smoke" if args.smoke else "full"
    out_dir = _output_dir()

    sweep = run_sweep(run_mode, out_dir)
    verdict, verdict_msg, headline = compute_verdict(sweep)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"[{run_mode}] {verdict}: {verdict_msg[:200]}",
        "elapsed_s": sweep["elapsed_s"],
        "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {
            "orders": [o[0] for o in ORDERS], "baseline_order": BASELINE_ORDER,
            "dist_specs": [{"dist": d, "d_sub": s} for d, s in DIST_SPECS],
            "cos_target": COS_TARGET, "recon_tau": RECON_TAU,
            "recall_thresh": RECALL_THRESH, "alpha_ladder": ALPHA_LADDER,
            "m_cap": M_CAP, "n_ladder": sweep["n_ladder"], "seeds": sweep["seeds"],
            "hp_lift": HP_LIFT, "hf_lift": HF_LIFT,
            "pos_control_iid_lift": POS_CONTROL_IID_LIFT,
        },
        "headline": headline,
        "expected_n_units": sweep["expected_n_units"],
        "n_units": len(sweep["per_unit"]),
        "cardinality_ok": len(sweep["per_unit"]) == sweep["expected_n_units"],
        "per_unit": sweep["per_unit"],
        "scramble_units": sweep["scramble_units"],
    }
    _atomic_write_json(out_dir / "metrics.json", metrics)
    print(f"[done] {verdict} :: {verdict_msg}", flush=True)
    print(f"[done] metrics -> {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    _out = _output_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
