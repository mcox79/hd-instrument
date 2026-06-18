"""ARCH-A Drosophila 2x2 ablation PRE-FLIGHT (Anchor 1; Director handoff 2026-06-18; laptop-CPU).

Orthogonalizes the prior DESIGN-INCOMPLETE ARCH-A closure into 2 axes:
  axis-1: fly-MB random-projection + top-k WTA expansion STAGE in {off, on}
  axis-2: READOUT in {linear, entmax(alpha=1.5)}
  4 cells: A1(off,linear) A2(off,entmax=C1-replication) A3(on,linear) A4(on,entmax)

TASK: sparse-pattern associative-memory recall@1. M K-sparse bipolar patterns in N dims; query = a stored pattern with
bit-corruption. One-step modern-Hopfield retrieval: cosine scores -> readout weights -> reconstruction r = sum_i w_i p_i ->
recall@1 = (argmax_i cosine(r, p_i) == true). The WEIGHTING (dense linear vs sparse entmax) changes r, hence recall (argmax
of w alone would NOT distinguish -- monotone; the reconstruction does). With expansion+WTA the SAME retrieval runs in the
sparse high-dim KC code (decorrelated -> lower crosstalk -> linear readout may suffice = the fly-MB canonical claim).

DISCIPLINE: COSINE-normalized scores (beta comparable across regimes; avoids raw-dot self-dominance). beta FIXED A PRIORI +
FROZEN across all cells (no per-cell tuning to the predicted table = no-Goodhart). Predictions are INTERPRETATION bands, not
targets. SYMMETRIC read (expansion may help OR be redundant; both honest). measured-bounds stated. Pre-reg:
preregs/2026-06-18_drosophila_2x2_ablation_preflight_DRAFT.md (PRED-1/PRED-2 floors; tighten-not-loosen).

HDLAB_RUN_MODE / --smoke / --self-test / --full. Laptop-CPU (no GPU). ASCII-only.
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

ALPHA = 1.5          # entmax sparsity (C1 setting)
BETA = 8.0           # FIXED A PRIORI (cosine-score regime); FROZEN across all cells (no-Goodhart)
WTA_FRAC = 0.05      # fly-MB KC sparsity (top ~5% active after expansion)
NOISE_FRAC = 0.30    # query bit-corruption fraction
EFFECT_FLOOR = 0.05  # a delta must exceed this to count as a real lift (else seed noise)


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


def make_patterns(M, N, K, g):
    """M K-sparse bipolar patterns (K active positions, +-1), in N dims."""
    P = np.zeros((M, N), dtype=np.float32)
    for i in range(M):
        idx = g.choice(N, size=K, replace=False)
        P[i, idx] = g.choice([-1.0, 1.0], size=K)
    return P


def corrupt(p, K, N, noise_frac, g):
    """Query = pattern with noise_frac of its active bits dropped + that many spurious active bits added."""
    q = p.copy()
    active = np.nonzero(p)[0]
    nflip = max(1, int(noise_frac * len(active)))
    drop = g.choice(active, size=min(nflip, len(active)), replace=False)
    q[drop] = 0.0
    inactive = np.nonzero(p == 0)[0]
    add = g.choice(inactive, size=min(nflip, len(inactive)), replace=False)
    q[add] = g.choice([-1.0, 1.0], size=len(add))
    return q


def _unit(X):
    return X / (np.linalg.norm(X, axis=-1, keepdims=True) + 1e-12)


def expand_wta(X, R, wta_frac):
    """fly-MB: random-project X (.,N)->(.,N_exp) then top-k WTA (keep top wta_frac active, binarize)."""
    E = X @ R.T                                    # (., N_exp)
    k = max(1, int(wta_frac * R.shape[0]))
    code = np.zeros_like(E)
    idx = np.argpartition(-E, k - 1, axis=1)[:, :k]
    np.put_along_axis(code, idx, 1.0, axis=1)      # binary KC code (active = 1)
    return code.astype(np.float32)


def recall_at_1(P, Q, true_idx, readout_mode):
    """One-step Hopfield retrieval; recall@1 = argmax_i cosine(reconstruction, p_i) == true. P,Q already in the working space."""
    Pn = _unit(P); Qn = _unit(Q)
    S = Qn @ Pn.T                                   # (nq, M) cosine scores
    if readout_mode == "linear":
        W = np.clip(S, 0.0, None)                   # relu (linear, non-exponential, NON-sparsifying -> keeps crosstalk)
        W = W / (W.sum(axis=1, keepdims=True) + 1e-12)
    elif readout_mode == "entmax":
        W = entmax_alpha(BETA * S, ALPHA)           # sparse -> rejects crosstalk
    else:
        raise ValueError(readout_mode)
    R = W @ P                                        # reconstruction (nq, dim)
    # re-nearest: which stored pattern is the reconstruction closest to?
    Rn = _unit(R)
    sim = Rn @ Pn.T                                  # (nq, M)
    pred = sim.argmax(axis=1)
    return float((pred == true_idx).mean())


def run_cell(expansion, readout_mode, N, M, K, n_exp, seeds):
    recalls = []
    for seed in seeds:
        g = _rng(seed)
        P = make_patterns(M, N, K, g)
        true_idx = np.arange(M)
        Q = np.stack([corrupt(P[i], K, N, NOISE_FRAC, g) for i in range(M)])   # one query per stored pattern
        if expansion:
            R = g.standard_normal((n_exp, N)).astype(np.float32)               # fixed random projection
            Pw = expand_wta(P, R, WTA_FRAC)
            Qw = expand_wta(Q, R, WTA_FRAC)
            recalls.append(recall_at_1(Pw, Qw, true_idx, readout_mode))
        else:
            recalls.append(recall_at_1(P, Q, true_idx, readout_mode))
    return float(np.mean(recalls)), float(np.std(recalls))


def run(fast=False):
    if fast:
        N, M, K, n_exp, seeds = 128, 40, 10, 512, [7]
    else:
        N, M, K, n_exp, seeds = 512, 200, 20, 4096, [7, 17, 23]
    cells = {
        "A1_baseline_linear": run_cell(False, "linear", N, M, K, n_exp, seeds),
        "A2_baseline_entmax": run_cell(False, "entmax", N, M, K, n_exp, seeds),
        "A3_expansion_linear": run_cell(True, "linear", N, M, K, n_exp, seeds),
        "A4_expansion_entmax": run_cell(True, "entmax", N, M, K, n_exp, seeds),
    }
    rc = {k: v[0] for k, v in cells.items()}
    A1, A2, A3, A4 = rc["A1_baseline_linear"], rc["A2_baseline_entmax"], rc["A3_expansion_linear"], rc["A4_expansion_entmax"]
    best = max(A1, A2, A3, A4)
    gap = best - A1
    # PRED-1: expansion is the lever
    expansion_lift = A3 - A1
    closes_frac = (expansion_lift / gap) if gap > EFFECT_FLOOR else 0.0
    pred1_hard_pass = (expansion_lift > EFFECT_FLOOR) and (closes_frac >= 0.60) and (A4 >= A3 - EFFECT_FLOOR)
    pred1_hard_fail = expansion_lift <= EFFECT_FLOOR
    pred1_middle = (not pred1_hard_pass) and (not pred1_hard_fail) and (A1 + EFFECT_FLOOR < A3 < A2)
    # PRED-2: linear-on-KC-code sufficient (WTA is the nonlinearity)
    entmax_on_expansion = A4 - A3
    pred2_hard_pass = abs(entmax_on_expansion) < EFFECT_FLOOR
    pred2_hard_fail = entmax_on_expansion > 0.10

    if pred1_hard_pass:
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS (PRED-1): the expansion+WTA STAGE is the Drosophila-class lever. expansion-lift A3-A1={expansion_lift:.3f} "
                f"(>{EFFECT_FLOOR}; closes {closes_frac*100:.0f}% of the A1->best gap) AND A4>=A3 (entmax-on-expansion additive/neutral). "
                f"-> Drosophila-class capability needs its OWN upstream expansion+WTA stage, DISTINCT from the entmax readout fix. "
                f"PRED-2 (WTA is the nonlinearity): |A4-A3|={entmax_on_expansion:+.3f} -> {'PASS (linear suffices on KC code)' if pred2_hard_pass else ('FAIL (entmax still helps with expansion)' if pred2_hard_fail else 'MIDDLE')}. "
                f"ARCH-A closure preserved cert-grade-but-DESIGN-INCOMPLETE; expansion+WTA = NEW cap_map row. Anchor 2 (full-N) GATED-GO.")
    elif pred1_hard_fail:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL (PRED-1): the expansion+WTA stage adds nothing (A3-A1={expansion_lift:.3f} <= {EFFECT_FLOOR}). "
                f"The Drosophila-class question is CLOSED as a substrate addition -- the entmax readout fix (A2={A2:.3f} vs A1={A1:.3f}) "
                f"was sufficient. Prior ARCH-A MIDDLE_BAND closure RATIFIED (honest-acceptance). Product-positive: cleaner story, no extra stage. No Anchor 2.")
    elif pred1_middle:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND (PRED-1): expansion helps (A3={A3:.3f} > A1+{EFFECT_FLOOR}) but readout helps more (A3 < A2={A2:.3f}). "
                f"expansion+WTA = marginal-not-load-bearing optional layer; honest-acceptance band. Anchor 2 not warranted on this signal.")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND (unclassified): A1={A1:.3f} A2={A2:.3f} A3={A3:.3f} A4={A4:.3f}; expansion-lift={expansion_lift:.3f}, "
                f"entmax-on-expansion={entmax_on_expansion:+.3f}. Does not cleanly meet PRED-1 PASS/FAIL; report as honest middle.")

    return {"verdict": verdict, "verdict_msg": vmsg, "recall_at_1": {k: round(v, 4) for k, v in rc.items()},
            "recall_std": {k: round(cells[k][1], 4) for k in cells}, "deltas": {
                "A2_minus_A1_entmax_readout_lift": round(A2 - A1, 4), "A3_minus_A1_expansion_lift": round(A3 - A1, 4),
                "A4_minus_A1_composed": round(A4 - A1, 4), "A4_minus_A3_entmax_on_expansion": round(A4 - A3, 4)},
            "pred1_hard_pass": pred1_hard_pass, "pred1_hard_fail": pred1_hard_fail, "pred2_hard_pass": pred2_hard_pass,
            "pred2_hard_fail": pred2_hard_fail, "config": {"N": N, "M": M, "K": K, "n_exp": n_exp, "seeds": seeds,
            "alpha": ALPHA, "beta_frozen": BETA, "wta_frac": WTA_FRAC, "noise_frac": NOISE_FRAC, "effect_floor": EFFECT_FLOOR},
            "measured_bounds": f"recall@1 envelope at N={N}/M={M}/K={K}/E_exp={n_exp}/wta={WTA_FRAC}/noise={NOISE_FRAC}/beta={BETA}(frozen); NOT fundamental",
            "branch_path": "smoke_2x2" if fast else "preflight_2x2_N512"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="tiny 2x2 wiring + recall check (laptop)")
    ap.add_argument("--self-test", action="store_true", help="PROT-020 fast wiring-check (<30s; writes NO metrics)")
    ap.add_argument("--full", action="store_true", help="pre-flight FULL (N=512, 3 seeds); laptop-CPU")
    args, _ = ap.parse_known_args()
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full").lower()
    self_test = getattr(args, "self_test", False)
    is_smoke = (args.smoke or self_test or run_mode == "smoke") and not getattr(args, "full", False)
    t0 = time.time(); run_started_utc = now_utc()

    if self_test:
        run(fast=True)
        print(f"[{ANCHOR}] --self-test wiring OK (2x2 harness runs); NO metrics written.")
        return 0

    r = run(fast=is_smoke)
    metrics = {"anchor_name": ANCHOR, "verdict": r["verdict"], "verdict_msg": r["verdict_msg"], "summary": r["verdict_msg"],
               "headline": r["verdict_msg"],
               **provenance_fields("smoke" if is_smoke else "full", r["branch_path"],
                                   "synthetic_2x2_ablation", run_started_utc),
               "recall_at_1": r["recall_at_1"], "recall_std": r["recall_std"], "deltas": r["deltas"],
               "pred1_hard_pass": r["pred1_hard_pass"], "pred1_hard_fail": r["pred1_hard_fail"],
               "pred2_hard_pass": r["pred2_hard_pass"], "pred2_hard_fail": r["pred2_hard_fail"],
               "config": r["config"], "measured_bounds": r["measured_bounds"],
               "recapture_of": "ARCH_A_Drosophila_MIDDLE_BAND (DESIGN-INCOMPLETE; conflated expansion-stage x readout axes)",
               "method_delta": "2x2 orthogonal ablation: fly-MB expansion+WTA stage {off,on} x readout {linear,entmax}; isolates whether Drosophila-class capability needs an upstream sparse-coding stage distinct from the entmax readout fix (C1)",
               "result": r, "elapsed_s": round(time.time() - t0, 2)}
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")

    print(f"[{ANCHOR}] run_mode={'smoke' if is_smoke else 'full'} branch={r['branch_path']} -> {r['verdict']}")
    print(f"  recall@1: {r['recall_at_1']}")
    print(f"  deltas: {r['deltas']}")
    print(f"  {r['verdict_msg']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
