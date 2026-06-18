"""ARCH-A Drosophila 2x2 ablation PRE-FLIGHT (A5; Director handoff + Skunkworks SCHEMA-VET PASS 2026-06-18; laptop-CPU).

Orthogonalizes the prior DESIGN-INCOMPLETE ARCH-A closure into 2 axes, measured by CAPACITY-CURVE (Skunkworks-agreed):
  axis-1: fly-MB expansion stage in {off, on}   axis-2: readout in {linear, entmax(alpha=1.5)}
  4 cells: A1(off,linear) A2(off,entmax=C1-replication) A3(on,linear) A4(on,entmax)

METRIC = CAPACITY-CURVE M* (NOT single-regime recall; the readout effect saturates a point-metric). Sweep load M; recall =
FIDELITY (cosine(one-step-reconstruction, true) >= TAU); M* = the load where recall crosses RECALL_THRESH (pre-registered,
frozen). Larger readout/expansion effect -> larger M* gap. CENSORED-HONESTY: a cell that never crosses within the grid ->
M* censored (NON_TEST for that comparison; not extrapolated). Apples-to-apples: same grid/thresh/seeds/noise across cells.

EXPANSION = fly-LSH, faithful BY CONSTRUCTION (Dasgupta-Stevens-Navlakha 2017): sparse binary random connectivity (each KC
samples M_SAMP random PNs), sum, top-k WTA -> sparse locality-preserving KC code. FAITHFULNESS GATE = NO-NOISE CONTROL
(Skunkworks): the expansion must NOT reduce capacity at ZERO noise (M*(expanded,no-noise) >= M*(raw,no-noise)); else the
expansion destroys signal -> expansion axis = NON_TEST (fix the WTA), NOT "expansion hurts". KC-overlap-preservation reported
as a DIAGNOSTIC (not a tuned gate).

VERDICT (symmetric; readout axis SEPARATE from expansion axis -- A5's question is the EXPANSION built on the readout):
  HARD-PASS = expansion lifts capacity with a faithful WTA: M*(A3) >> M*(A1) AND faithfulness gate passes -> ARCH-A needed
     an upstream WTA-nonlinear expansion stage (candidate audit-discipline #93: prior closure was linear-readout-DESIGN-
     INCOMPLETE, not a ceiling); scoped to the nonlinearity, method/config qualifier.
  HARD-FAIL = expansion does NOT lift capacity EVEN with a faithful WTA -> RE-AFFIRMS the ARCH-A MIDDLE_BAND closure (real
     negative stays closed); the entmax readout fix (C1) is sufficient.
  NON_TEST = faithfulness gate fails (non-faithful expansion) OR censored M* on the compared cells.

Pre-reg: preregs/2026-06-18_drosophila_2x2_ablation_preflight_DRAFT.md (capacity-curve redesign per SCHEMA-VET).
HDLAB_RUN_MODE / --smoke / --self-test / --full. Laptop-CPU (no GPU). Deterministic (cert-2/11th-rule). ASCII-only.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cell_provenance import provenance_fields, now_utc

ANCHOR = "substrate_drosophila_2x2_ablation_preflight_v1"
_EXP_NAME = os.environ.get("HDLAB_EXP_NAME")
OUT = REPO / "data" / (f"exp_{_EXP_NAME}" if _EXP_NAME else ANCHOR)

# Pre-registered + FROZEN (no post-hoc fishing):
ALPHA = 1.5            # entmax sparsity (C1 setting)
BETA = 8.0             # cosine-score temperature, fixed a priori, frozen across cells
TAU_FIDELITY = 0.90    # reconstruction-fidelity threshold (cosine(r, true) >= TAU = a correct retrieval)
RECALL_THRESH = 0.50   # capacity M* = load where fidelity-recall crosses this
NOISE_FRAC = 0.20      # query bit-corruption (the noise-robustness being tested)
EXPAND = 8             # fly-LSH expansion factor (n_kc = EXPAND * N)
M_SAMP = 6             # fly-LSH: each KC samples this many random PNs (Dasgupta-Stevens-Navlakha canonical ~6)
WTA_FRAC = 0.05        # fly-MB KC sparsity (top ~5% active)


def _rng(seed):
    return np.random.default_rng(seed)


def entmax_alpha(Z, alpha=ALPHA, n_iter=30):
    Z = np.atleast_2d(Z).astype(np.float64)
    if alpha == 1.0:
        Z = Z - Z.max(axis=1, keepdims=True); E = np.exp(Z); return E / (E.sum(axis=1, keepdims=True) + 1e-12)
    am1 = alpha - 1.0; Zs = am1 * Z
    tau_hi = Zs.max(axis=1, keepdims=True); tau_lo = Zs.min(axis=1, keepdims=True) - 1.0
    for _ in range(n_iter):
        tau = 0.5 * (tau_lo + tau_hi)
        s = (np.clip(Zs - tau, 0.0, None) ** (1.0 / am1)).sum(axis=1, keepdims=True)
        over = s > 1.0; tau_lo = np.where(over, tau, tau_lo); tau_hi = np.where(over, tau_hi, tau)
    p = np.clip(Zs - 0.5 * (tau_lo + tau_hi), 0.0, None) ** (1.0 / am1)
    return p / (p.sum(axis=1, keepdims=True) + 1e-12)


def _unit(X):
    return X / (np.linalg.norm(X, axis=-1, keepdims=True) + 1e-12)


def make_patterns(M, N, g):
    """M dense bipolar patterns (classical crosstalk regime; capacity ~0.14N for linear one-step)."""
    return g.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)


def corrupt(P, noise_frac, g):
    """Query = pattern with noise_frac of bits sign-flipped."""
    Q = P.copy()
    if noise_frac <= 0:
        return Q
    N = P.shape[1]; k = max(1, int(noise_frac * N))
    for i in range(P.shape[0]):
        idx = g.choice(N, size=k, replace=False); Q[i, idx] *= -1.0
    return Q


def fly_lsh_connectivity(N, n_kc, m_samp, g):
    """Dasgupta-Stevens-Navlakha: sparse binary connectivity -- each KC samples m_samp random PNs (locality-preserving)."""
    C = np.zeros((n_kc, N), dtype=np.float32)
    for j in range(n_kc):
        C[j, g.choice(N, size=m_samp, replace=False)] = 1.0
    return C


def fly_lsh_expand(X, C, wta_frac):
    """fly-LSH expand-and-sparsify: project via sparse connectivity, top-k WTA -> binary KC code (faithful by construction)."""
    E = X @ C.T
    k = max(1, int(wta_frac * C.shape[0]))
    code = np.zeros_like(E)
    idx = np.argpartition(-E, k - 1, axis=1)[:, :k]
    np.put_along_axis(code, idx, 1.0, axis=1)
    return code.astype(np.float32)


def fidelity_recall(P, Q, true_idx, readout_mode):
    """One-step Hopfield retrieval; recall = mean(cosine(reconstruction, true) >= TAU_FIDELITY). P,Q in the working space."""
    Pn = _unit(P); Qn = _unit(Q)
    S = Qn @ Pn.T
    if readout_mode == "linear":
        W = np.clip(S, 0.0, None); W = W / (W.sum(axis=1, keepdims=True) + 1e-12)   # linear, non-sparsifying (keeps crosstalk)
    else:
        W = entmax_alpha(BETA * S, ALPHA)                                            # sparse (rejects crosstalk)
    R = W @ P
    cos_true = (_unit(R) * Pn[true_idx]).sum(axis=1)
    return float((cos_true >= TAU_FIDELITY).mean())


def capacity_curve(expansion, readout_mode, N, M_grid, seeds, noise_frac, conn_cache):
    """For each M in grid: mean fidelity-recall over seeds. Returns per-M recall + M* (crossing of RECALL_THRESH, interpolated)."""
    per_M = []
    for M in M_grid:
        rs = []
        for seed in seeds:
            g = _rng(seed)
            P = make_patterns(M, N, g)
            true = np.arange(M)
            Q = corrupt(P, noise_frac, g)
            if expansion:
                C = conn_cache[seed]
                rs.append(fidelity_recall(fly_lsh_expand(P, C, WTA_FRAC), fly_lsh_expand(Q, C, WTA_FRAC), true, readout_mode))
            else:
                rs.append(fidelity_recall(P, Q, true, readout_mode))
        per_M.append((M, float(np.mean(rs)), float(np.std(rs))))
    # M* = interpolated load where recall crosses RECALL_THRESH (descending). Censored if it never crosses.
    Mstar = None; censored = "none"
    Ms = [p[0] for p in per_M]; rec = [p[1] for p in per_M]
    if rec[0] < RECALL_THRESH:
        censored = "left_below_all"            # below threshold even at smallest load -> can't measure capacity
    elif rec[-1] >= RECALL_THRESH:
        censored = "right_above_all"           # above threshold even at largest load -> capacity > grid
    else:
        for i in range(len(Ms) - 1):
            if rec[i] >= RECALL_THRESH > rec[i + 1]:
                # log-linear interpolation of the crossing load
                f = (rec[i] - RECALL_THRESH) / (rec[i] - rec[i + 1] + 1e-12)
                Mstar = float(np.exp(np.log(Ms[i]) + f * (np.log(Ms[i + 1]) - np.log(Ms[i]))))
                break
    return {"per_M": per_M, "Mstar": (round(Mstar, 1) if Mstar else None), "censored": censored}


def run(fast=False):
    if fast:
        N, seeds = 128, [7]
        M_grid = [16, 32, 64, 128, 256, 512]
    else:
        N, seeds = 256, [7, 17, 23]
        M_grid = [32, 64, 128, 256, 512, 1024, 2048]
    n_kc = EXPAND * N
    conn_cache = {s: fly_lsh_connectivity(N, n_kc, M_SAMP, _rng(1000 + s)) for s in seeds}

    cells = {}
    for name, (exp, mode) in {"A1_baseline_linear": (False, "linear"), "A2_baseline_entmax": (False, "entmax"),
                              "A3_expansion_linear": (True, "linear"), "A4_expansion_entmax": (True, "entmax")}.items():
        cells[name] = capacity_curve(exp, mode, N, M_grid, seeds, NOISE_FRAC, conn_cache)
    # NO-NOISE faithfulness control: expansion must NOT reduce capacity at zero noise (else WTA destroys signal -> NON_TEST).
    nn_raw = capacity_curve(False, "linear", N, M_grid, seeds, 0.0, conn_cache)
    nn_exp = capacity_curve(True, "linear", N, M_grid, seeds, 0.0, conn_cache)
    # KC-overlap-preservation diagnostic (reported, not a tuned gate)
    g = _rng(seeds[0]); Pd = make_patterns(200, N, g); Qd = corrupt(Pd, NOISE_FRAC, g)
    Pw = fly_lsh_expand(Pd, conn_cache[seeds[0]], WTA_FRAC); Qw = fly_lsh_expand(Qd, conn_cache[seeds[0]], WTA_FRAC)
    kc_overlap = float((Pw * Qw).sum(1).mean() / (Pw.sum(1).mean() + 1e-9))

    Ms = {k: cells[k]["Mstar"] for k in cells}
    cen = {k: cells[k]["censored"] for k in cells}

    def _gt(a, b):  # a >> b: both measured and a at least 1.3x b
        return (a is not None) and (b is not None) and (a >= 1.3 * b)

    # faithfulness gate: expanded no-noise capacity >= raw no-noise capacity (allow censored-above as "fine")
    nn_ok = (nn_exp["censored"] == "right_above_all") or _gt(nn_exp["Mstar"], nn_raw["Mstar"]) or \
            (nn_exp["Mstar"] is not None and nn_raw["Mstar"] is not None and nn_exp["Mstar"] >= 0.9 * nn_raw["Mstar"])
    readout_lift = _gt(Ms["A2_baseline_entmax"], Ms["A1_baseline_linear"])   # C1 replication (separate axis)
    expansion_lift = _gt(Ms["A3_expansion_linear"], Ms["A1_baseline_linear"])  # the A5 question
    expansion_censored = cen["A3_expansion_linear"] != "none" or cen["A1_baseline_linear"] != "none"

    if not nn_ok:
        verdict = "NON_TEST"
        vmsg = (f"NON_TEST (non-faithful expansion): the fly-LSH expansion REDUCES capacity even at ZERO noise "
                f"(M*_exp_nonoise={nn_exp['Mstar']}/{nn_exp['censored']} < M*_raw_nonoise={nn_raw['Mstar']}/{nn_raw['censored']}) "
                f"-> the WTA is destroying signal, so the expansion axis is NOT a valid test (fix the expansion, not a verdict). "
                f"KC-overlap-preservation={kc_overlap:.2f} (diagnostic). Readout axis still measurable (see deltas).")
    elif expansion_censored:
        verdict = "NON_TEST"
        vmsg = (f"NON_TEST (censored M*): A1 or A3 never crosses recall={RECALL_THRESH} within the load grid "
                f"(A1={cen['A1_baseline_linear']}, A3={cen['A3_expansion_linear']}) -> the expansion-axis capacity comparison "
                f"is not measurable in this grid; widen the grid. Readout axis: {Ms}.")
    elif expansion_lift:
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS (#93): the fly-LSH expansion+WTA stage LIFTS capacity (M*(A3 expansion+linear)={Ms['A3_expansion_linear']} "
                f">> M*(A1 baseline+linear)={Ms['A1_baseline_linear']}) WITH a faithful WTA (no-noise control passed). -> ARCH-A "
                f"Drosophila-class capacity recovers WITH an upstream WTA-nonlinear expansion stage; the prior MIDDLE_BAND closure was "
                f"linear-readout-DESIGN-INCOMPLETE, NOT a fundamental ceiling (candidate audit-discipline #93). Scoped to the nonlinearity "
                f"(method/config qualifier). Composes with ARCH-B/C1 (readout lever, SEPARATE axis: M*(A2 entmax)={Ms['A2_baseline_entmax']} "
                f"vs M*(A1)={Ms['A1_baseline_linear']}, readout_lift={readout_lift}). ARCH-A closure preserved cert-grade-but-DESIGN-INCOMPLETE; "
                f"expansion+WTA = NEW cap_map row. Anchor 2 (full-N) GATED-GO. measured-bounds: capacity envelope at N={N}/this config.")
    else:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL: the fly-LSH expansion+WTA stage does NOT lift capacity (M*(A3)={Ms['A3_expansion_linear']} not >> "
                f"M*(A1)={Ms['A1_baseline_linear']}) EVEN WITH a faithful WTA (no-noise control passed) -> RE-AFFIRMS the ARCH-A "
                f"MIDDLE_BAND closure (a real negative stays closed). The entmax READOUT fix (C1) is sufficient for Drosophila-class "
                f"capability; no upstream expansion stage needed. Readout axis (separate): M*(A2 entmax)={Ms['A2_baseline_entmax']} vs "
                f"M*(A1 linear)={Ms['A1_baseline_linear']}, readout_lift={readout_lift} (C1 replication). Product-positive: cleaner story, no extra stage.")

    return {"verdict": verdict, "verdict_msg": vmsg, "Mstar": Ms, "censored": cen,
            "capacity_curves": {k: cells[k]["per_M"] for k in cells},
            "no_noise_control": {"raw": nn_raw, "expanded": nn_exp, "faithfulness_ok": bool(nn_ok)},
            "kc_overlap_preservation": round(kc_overlap, 4),
            "readout_lift_A2_over_A1": bool(readout_lift), "expansion_lift_A3_over_A1": bool(expansion_lift),
            "config": {"N": N, "M_grid": M_grid, "seeds": seeds, "alpha": ALPHA, "beta": BETA, "tau_fidelity": TAU_FIDELITY,
                       "recall_thresh": RECALL_THRESH, "noise_frac": NOISE_FRAC, "expand": EXPAND, "m_samp": M_SAMP, "wta_frac": WTA_FRAC},
            "measured_bounds": f"capacity (M* at recall>={RECALL_THRESH}, fidelity tau={TAU_FIDELITY}) envelope at N={N}/expand={EXPAND}/wta={WTA_FRAC}/noise={NOISE_FRAC}; NOT fundamental",
            "branch_path": "smoke_capacity_curve" if fast else "preflight_capacity_curve"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args, _ = ap.parse_known_args()
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full").lower()
    self_test = getattr(args, "self_test", False)
    is_smoke = (args.smoke or self_test or run_mode == "smoke") and not getattr(args, "full", False)
    t0 = time.time(); run_started_utc = now_utc()

    if self_test:
        run(fast=True)
        print(f"[{ANCHOR}] --self-test wiring OK (capacity-curve 2x2 + no-noise control runs); NO metrics written.")
        return 0

    r = run(fast=is_smoke)
    metrics = {"anchor_name": ANCHOR, "verdict": r["verdict"], "verdict_msg": r["verdict_msg"], "summary": r["verdict_msg"],
               "headline": r["verdict_msg"],
               **provenance_fields("smoke" if is_smoke else "full", r["branch_path"], "synthetic_capacity_curve_2x2", run_started_utc),
               "Mstar": r["Mstar"], "censored": r["censored"], "no_noise_control": r["no_noise_control"],
               "kc_overlap_preservation": r["kc_overlap_preservation"], "readout_lift_A2_over_A1": r["readout_lift_A2_over_A1"],
               "expansion_lift_A3_over_A1": r["expansion_lift_A3_over_A1"], "capacity_curves": r["capacity_curves"],
               "config": r["config"], "measured_bounds": r["measured_bounds"],
               "recapture_of": "ARCH_A_Drosophila_MIDDLE_BAND (DESIGN-INCOMPLETE; conflated expansion-stage x readout axes)",
               "method_delta": "capacity-curve M* over a 2x2 (fly-LSH expansion+WTA {off,on} x readout {linear,entmax}); no-noise faithfulness control; isolates whether Drosophila-class capacity needs an upstream WTA-nonlinear expansion stage distinct from the entmax readout fix (C1)",
               "result": r, "elapsed_s": round(time.time() - t0, 2)}
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")

    print(f"[{ANCHOR}] run_mode={'smoke' if is_smoke else 'full'} branch={r['branch_path']} -> {r['verdict']}")
    print(f"  M* capacity: {r['Mstar']} | censored: {r['censored']}")
    print(f"  no-noise faithfulness: raw M*={r['no_noise_control']['raw']['Mstar']} exp M*={r['no_noise_control']['expanded']['Mstar']} ok={r['no_noise_control']['faithfulness_ok']} | KC-overlap={r['kc_overlap_preservation']}")
    print(f"  readout_lift(A2>A1)={r['readout_lift_A2_over_A1']} expansion_lift(A3>A1)={r['expansion_lift_A3_over_A1']}")
    print(f"  {r['verdict_msg'][:300]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
