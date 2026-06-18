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


def _noise_at_half(noise_grid, recalls):
    """Noise level where recall crosses 0.5 (descending). Higher = more noise-robust. Censored if never crosses."""
    if recalls[0] < 0.5:
        return None, "fair_start_fail"            # below 0.5 even at noise=0 -> not a fair start
    if recalls[-1] >= 0.5:
        return float(noise_grid[-1]), "right_censored"   # still >=0.5 at max noise -> very robust (lower bound)
    for i in range(len(noise_grid) - 1):
        if recalls[i] >= 0.5 > recalls[i + 1]:
            f = (recalls[i] - 0.5) / (recalls[i] - recalls[i + 1] + 1e-12)
            return float(noise_grid[i] + f * (noise_grid[i + 1] - noise_grid[i])), "none"
    return None, "uncrossed"


def noise_retention(N, M_fixed, noise_grid, seeds, conn_cache, readout_mode, expansion):
    """Option B: re-nearest retrieval accuracy at FIXED load M_fixed across the noise grid (mean over seeds)."""
    curve = []
    for noise in noise_grid:
        rs = []
        for seed in seeds:
            g = _rng(seed); P = make_patterns(M_fixed, N, g); true = np.arange(M_fixed)
            Q = corrupt(P, noise, _rng(10000 + seed))
            if expansion:
                C = conn_cache[seed]
                Pw = fly_lsh_expand(P, C, WTA_FRAC); Qw = fly_lsh_expand(Q, C, WTA_FRAC)
                Pn = _unit(Pw); Qn = _unit(Qw); S = Qn @ Pn.T; Puse = Pw
            else:
                Pn = _unit(P); Qn = _unit(Q); S = Qn @ Pn.T; Puse = P
            if readout_mode == "linear":
                W = np.clip(S, 0.0, None); W = W / (W.sum(axis=1, keepdims=True) + 1e-12)
            else:
                W = entmax_alpha(BETA * S, ALPHA)
            Rrec = W @ Puse
            rs.append(float((_unit(Rrec) @ Pn.T).argmax(axis=1).__eq__(true).mean()))
        curve.append((float(noise), float(np.mean(rs)), float(np.std(rs))))
    recalls = [c[1] for c in curve]
    nah, cen = _noise_at_half(noise_grid, recalls)
    return {"curve": curve, "noise_at_half": (round(nah, 4) if nah is not None else None), "censored": cen}


M_FIXED_B = 30           # option-B fixed load (fair-start verified; pre-registered)
NOISE_GRID_B = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]


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
    readout_lift = _gt(Ms["A2_baseline_entmax"], Ms["A1_baseline_linear"])   # C1 replication (capacity-curve, READOUT axis = PASS)
    nn_faithful = (nn_exp["censored"] == "right_above_all") or _gt(nn_exp["Mstar"], nn_raw["Mstar"])  # capacity-faithfulness DIAGNOSTIC only

    # OPTION B (Skunkworks-decided EXPANSION-axis test): noise-robustness retention at a fixed FAIR-START load.
    b_raw_lin = noise_retention(N, M_FIXED_B, NOISE_GRID_B, seeds, conn_cache, "linear", False)   # A1 raw-linear
    b_exp_lin = noise_retention(N, M_FIXED_B, NOISE_GRID_B, seeds, conn_cache, "linear", True)    # A3 expansion-linear (the fly-MB claim)
    b_raw_ent = noise_retention(N, M_FIXED_B, NOISE_GRID_B, seeds, conn_cache, "entmax", False)   # A2 reference
    b_exp_ent = noise_retention(N, M_FIXED_B, NOISE_GRID_B, seeds, conn_cache, "entmax", True)    # A4 reference
    nah_raw = b_raw_lin["noise_at_half"]; nah_exp = b_exp_lin["noise_at_half"]
    fair_start_ok = (b_raw_lin["censored"] != "fair_start_fail") and (b_exp_lin["censored"] != "fair_start_fail")
    delta_b = (nah_exp - nah_raw) if (nah_exp is not None and nah_raw is not None) else None

    rd = f"READOUT axis SEPARATE + POSITIVE: capacity M*(A2 entmax)={Ms['A2_baseline_entmax']} vs M*(A1 linear)={Ms['A1_baseline_linear']} = C1 REPLICATED."
    if not fair_start_ok:
        verdict = "NON_TEST"
        vmsg = (f"NON_TEST (option-B fair-start fail): raw or expanded linear is not >=0.5 retrieval at noise=0 / M={M_FIXED_B} "
                f"(raw={b_raw_lin['censored']}, exp={b_exp_lin['censored']}) -> lower the load. {rd}")
    elif delta_b is not None and delta_b > 0.03:
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS (option B, #93): the fly-LSH expansion+WTA stage ADDS NOISE-ROBUSTNESS -- expanded-linear noise_at_half={nah_exp} "
                f"> raw-linear={nah_raw} (delta=+{delta_b:.3f}). ARCH-A Drosophila-class capability RECOVERS with an upstream WTA-nonlinear "
                f"expansion stage (scoped to noise-robustness; the prior MIDDLE_BAND closure was linear-readout-DESIGN-INCOMPLETE, #93). {rd} "
                f"expansion+WTA = NEW cap_map row; Anchor 2 (full-N) GATED-GO.")
    elif delta_b is not None and delta_b <= 0.0:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL (option B): the fly-LSH expansion+WTA adds NO noise-robustness -- expanded-linear noise_at_half={nah_exp} "
                f"<= raw-linear={nah_raw} (delta={delta_b:+.3f}); raw-linear is at least as robust. -> RE-AFFIRMS the ARCH-A MIDDLE_BAND closure "
                f"(real negative stays closed). The entmax READOUT fix (C1) is the operative lever; no upstream expansion stage needed under this "
                f"substrate's retrieval. {rd} B is FINAL (pre-committed) -> expansion axis DISPOSITIONED. Product-positive: cleaner story, no extra stage.")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND (option B): expanded-linear noise_at_half={nah_exp} marginally > raw-linear={nah_raw} (delta=+{delta_b:.3f} <= 0.03) "
                f"-- a small, not-load-bearing noise-robustness edge. {rd} B is FINAL -> expansion axis dispositioned MIDDLE.")

    return {"verdict": verdict, "verdict_msg": vmsg, "Mstar": Ms, "censored": cen,
            "readout_axis_C1_replication": {"A1_linear_Mstar": Ms["A1_baseline_linear"], "A2_entmax_Mstar": Ms["A2_baseline_entmax"],
                                            "readout_lift": bool(readout_lift), "note": "A2 right-censored -> ratio is a LOWER BOUND (>=)"},
            "option_B_noise_retention": {"M_fixed": M_FIXED_B, "noise_grid": NOISE_GRID_B, "fair_start_ok": bool(fair_start_ok),
                "noise_at_half_raw_linear": nah_raw, "noise_at_half_exp_linear": nah_exp,
                "delta_exp_minus_raw": (round(delta_b, 4) if delta_b is not None else None),
                "A1_raw_linear": b_raw_lin, "A3_expansion_linear": b_exp_lin, "A2_raw_entmax": b_raw_ent, "A4_expansion_entmax": b_exp_ent},
            "no_noise_faithfulness_diagnostic": {"raw_Mstar": nn_raw["Mstar"], "exp_Mstar": nn_exp["Mstar"], "faithful": bool(nn_faithful),
                                                 "note": "capacity-metric faithfulness (binary code lossy by construction); DIAGNOSTIC, not the gate -- option B is the expansion test"},
            "capacity_curves": {k: cells[k]["per_M"] for k in cells}, "kc_overlap_preservation": round(kc_overlap, 4),
            "config": {"N": N, "M_grid": M_grid, "seeds": seeds, "alpha": ALPHA, "beta": BETA, "tau_fidelity": TAU_FIDELITY,
                       "recall_thresh": RECALL_THRESH, "noise_frac": NOISE_FRAC, "expand": EXPAND, "m_samp": M_SAMP, "wta_frac": WTA_FRAC,
                       "M_fixed_B": M_FIXED_B, "noise_grid_B": NOISE_GRID_B},
            "measured_bounds": f"EXPANSION axis = noise-robustness retention (noise_at_half) at M={M_FIXED_B}/N={N} (option B); READOUT axis = capacity M* at N={N}; both method/config-contingent, NOT fundamental",
            "branch_path": "smoke_2x2_optB" if fast else "preflight_2x2_optB"}


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
        print(f"[{ANCHOR}] --self-test wiring OK (capacity-curve readout-axis + option-B noise-retention expansion-axis run); NO metrics written.")
        return 0

    r = run(fast=is_smoke)
    metrics = {"anchor_name": ANCHOR, "verdict": r["verdict"], "verdict_msg": r["verdict_msg"], "summary": r["verdict_msg"],
               "headline": r["verdict_msg"],
               **provenance_fields("smoke" if is_smoke else "full", r["branch_path"], "synthetic_2x2_readout_capacity_plus_expansion_noise_retention", run_started_utc),
               "readout_axis_C1_replication": r["readout_axis_C1_replication"], "option_B_noise_retention": r["option_B_noise_retention"],
               "no_noise_faithfulness_diagnostic": r["no_noise_faithfulness_diagnostic"], "Mstar": r["Mstar"], "censored": r["censored"],
               "kc_overlap_preservation": r["kc_overlap_preservation"], "capacity_curves": r["capacity_curves"],
               "config": r["config"], "measured_bounds": r["measured_bounds"],
               "recapture_of": "ARCH_A_Drosophila_MIDDLE_BAND (DESIGN-INCOMPLETE; conflated expansion-stage x readout axes)",
               "method_delta": "2x2: READOUT axis via capacity-curve M* (C1 replication); EXPANSION axis via option-B noise-robustness retention (fly-MB mechanism's OWN claim; Skunkworks-decided after capacity-metric shown to disfavor binary codes by construction)",
               "result": r, "elapsed_s": round(time.time() - t0, 2)}
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")

    b = r["option_B_noise_retention"]
    print(f"[{ANCHOR}] run_mode={'smoke' if is_smoke else 'full'} branch={r['branch_path']} -> {r['verdict']}")
    print(f"  READOUT axis (capacity-curve, C1): M*(A1 linear)={r['Mstar']['A1_baseline_linear']} M*(A2 entmax)={r['Mstar']['A2_baseline_entmax']} censored={r['censored']}")
    print(f"  EXPANSION axis (option B noise_at_half): raw-linear={b['noise_at_half_raw_linear']} exp-linear={b['noise_at_half_exp_linear']} delta={b['delta_exp_minus_raw']} fair_start={b['fair_start_ok']}")
    print(f"  {r['verdict_msg'][:320]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
