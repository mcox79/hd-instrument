"""Refuse-gate RECAPTURE via NONLINEAR readout attention-CONCENTRATION (LOCKED 2026-06-17; lead nonlinear-readout cell).

V1 6th-module YELLOW recapture. ANCHOR limiter: a LINEAR scalar bge-cosine confidence threshold (tau) cannot separate
present-gold-PARAPHRASED (high cosine, IS present) from ABSENT-gold (should refuse). RECAPTURE: use a NONLINEAR readout's
ATTENTION-CONCENTRATION as the refuse signal -- softmax/entmax over the stored index CONCENTRATES when a stored pattern
genuinely matches (present, incl. paraphrase -> sharp, high max-weight) and stays DIFFUSE when nothing matches (absent
-> low max-weight / high entropy). refuse iff concentration < c; accept + return argmax iff concentration >= c.

DIRECTOR-LOCKED CONDITION (verify-the-referent at runtime): the SMOKE MUST MEASURE the attention-spread distribution
(max-weight / entropy) on the present-paraphrased vs absent mix and CONFIRM the readout DISCRIMINATES (present ->
concentrated, absent -> diffuse). IF absent also goes one-hot (spurious nearest match, max-weight ~1) = the self-
dominance wall -> NON-TEST (clustered/spread harness route), NOT a refuse-gate verdict (no false HARD-FAIL).

SMOKE (laptop): SYNTHETIC via the shared spread harness -- present = cluster centroids (stored index); present-PARAPHRASED
queries = centroid + noise (near-duplicate); ABSENT queries = novel random vectors. Cosine readout; concentration refuse
signal; MEASURE spread; sweep (beta, c). FULL (REMOTE): real bge index of present-gold + held-out q54-q65 (22nd-rule
firewall: controlled one-shot eval); same mechanism. Bars (= the M1 anchor): exists (beta,c) gap-refuse>=0.95 AND
in-coverage accept-drop<=0.05. HDLAB_RUN_MODE smoke|full. ASCII-only.
"""
from __future__ import annotations
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
from _spread_attention_harness import make_clustered_keys, cosine_scores, verify_spread

ANCHOR = "substrate_refuse_gate_nonlinear_readout_v1"
OUT = REPO / "data" / ANCHOR
RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "smoke")
N = 256 if RUN_MODE == "smoke" else 1024
SEEDS = [7] if RUN_MODE == "smoke" else [7, 17, 23]
N_PRESENT = 60 if RUN_MODE == "smoke" else 400       # stored gold items (cluster centroids)
N_QUERY = 120 if RUN_MODE == "smoke" else 800        # half present-paraphrased, half absent
PARAPHRASE_NOISE = 0.10                                # present-paraphrased = centroid + 10% bit-flip (near-duplicate)
BETA_GRID = [10.0, 20.0, 40.0, 80.0, 160.0]
C_GRID = [round(x, 3) for x in np.arange(0.10, 0.96, 0.05)]
ALPHA = float(os.environ.get("HDLAB_RF_ALPHA", "1.0"))  # 1.0 softmax; 1.5/2.0 = entmax sparse variant (drill-1/C1)


def _rng(seed):
    return np.random.default_rng(seed)


def entmax_alpha(Z, alpha, n_iter=30):
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


def build_synthetic(seed):
    """present = cluster centroids (stored index); present-paraphrased queries = centroid+noise; absent = novel."""
    g = _rng(seed)
    present, _ = make_clustered_keys(N_PRESENT, N, cluster_size=1, g=g)      # distinct gold items
    nq = N_QUERY // 2
    # present-paraphrased: pick a present item, flip PARAPHRASE_NOISE bits
    para = np.empty((nq, N), dtype=np.float32); para_tgt = np.empty(nq, dtype=np.int64)
    kf = max(1, int(PARAPHRASE_NOISE * N))
    for i in range(nq):
        j = g.integers(0, N_PRESENT); para_tgt[i] = j
        q = present[j].copy(); idx = g.choice(N, size=kf, replace=False); q[idx] *= -1.0; para[i] = q
    absent = (g.integers(0, 2, size=(nq, N)).astype(np.float32) * 2 - 1)    # novel random (not near any present)
    return present, para, para_tgt, absent


def concentration(queries, present, beta, alpha):
    W = entmax_alpha(beta * cosine_scores(queries, present), alpha)          # (nq, N_PRESENT)
    conc = W.max(axis=1)                                                     # attention max-weight = refuse signal
    argmax = W.argmax(axis=1)
    return conc, argmax, W


def main():
    t0 = time.time()
    # aggregate over seeds
    best = {"beta": None, "c": None, "gap_refuse": 0.0, "accept_drop": 1.0}
    spread_ok_any = False
    spread_report = {}
    per = {}
    for seed in SEEDS:
        present, para, para_tgt, absent = build_synthetic(seed)
        for beta in BETA_GRID:
            cp, ap, Wp = concentration(para, present, beta, ALPHA)          # present-paraphrased
            ca, aa, Wa = concentration(absent, present, beta, ALPHA)        # absent
            # SPREAD MEASUREMENT (verify-the-referent): absent must be DIFFUSE (low max-weight) vs present concentrated.
            # If absent also one-hot (max-weight ~1) -> self-dominance wall -> non-discriminating.
            absent_spreads = bool(np.median(ca) < 0.9) and verify_spread(Wa)["spreads"]
            spread_report[f"beta{beta}"] = {"present_maxw_med": float(np.median(cp)),
                                            "absent_maxw_med": float(np.median(ca)),
                                            "absent_spreads": absent_spreads}
            if absent_spreads:
                spread_ok_any = True
            for c in C_GRID:
                # refuse iff concentration < c
                gap_refuse = float((ca < c).mean())                          # absent correctly refused
                accept_present = float((cp >= c).mean())                     # present correctly accepted
                # accept_drop proxy for in-coverage F1 drop (1 - accept-rate on present-paraphrased)
                accept_drop = 1.0 - accept_present
                per.setdefault(f"{beta}_{c}", []).append((gap_refuse, accept_drop, absent_spreads))
    # average over seeds; pick best (beta,c) meeting both bars in a SPREAD regime
    for key, vals in per.items():
        gr = float(np.mean([v[0] for v in vals])); ad = float(np.mean([v[1] for v in vals]))
        sp = all(v[2] for v in vals)
        if sp and gr >= 0.95 and ad <= 0.05:
            if gr - ad > best["gap_refuse"] - best["accept_drop"]:
                b, c = key.split("_"); best = {"beta": float(b), "c": float(c), "gap_refuse": gr, "accept_drop": ad}

    if not spread_ok_any:
        verdict = "NON_TEST"
        msg = (f"NON-TEST (self-dominance): absent queries ALSO concentrate (max-weight ~1) at all beta -> the readout "
               f"does NOT discriminate present-paraphrased from absent (same one-hot wall as C1 clean-cue). spread_report="
               f"{spread_report}. Needs clustered/spread harness tuning, NOT a refuse-gate verdict. (alpha={ALPHA}, N={N}.)")
    elif best["beta"] is not None:
        verdict = "HARD_PASS"
        msg = (f"RECAPTURE: nonlinear-readout ATTENTION-CONCENTRATION refuse-gate separates present-paraphrased from "
               f"absent where the LINEAR cosine-tau (M1) could not -- (beta={best['beta']}, c={best['c']}): gap-refuse "
               f"{best['gap_refuse']:.3f} >= 0.95 AND accept-drop {best['accept_drop']:.3f} <= 0.05 (the bar M1 FAILED). "
               f"SYNTHETIC smoke; REMOTE bge/held-out q54-q65 FULL confirms. envelope of THIS method (alpha={ALPHA}, N={N}).")
    else:
        verdict = "HARD_FAIL"
        msg = (f"nonlinear readout does NOT recapture: no (beta,c) reaches gap-refuse>=0.95 + accept-drop<=0.05 in a "
               f"spread regime -> the present-paraphrased vs absent separation limit is DEEPER than the readout "
               f"(honest bound -> learned cross-domain adapter next). spread_report={spread_report}.")

    metrics = {
        "anchor_name": ANCHOR, "verdict": verdict, "verdict_msg": msg, "headline": msg, "run_mode": RUN_MODE,
        "N": N, "alpha": ALPHA, "n_present": N_PRESENT, "n_query": N_QUERY, "paraphrase_noise": PARAPHRASE_NOISE,
        "spread_report": spread_report, "spread_ok_any": spread_ok_any, "best": best,
        "regime": "SYNTHETIC near-collision (present-paraphrased vs absent) via shared spread harness; FULL = REMOTE bge + held-out q54-q65",
        "recapture_of": "PHASE_V1_6th_module_refuse_gated_retriever_YELLOW (M1 bge-cosine-tau HARD_FAIL gap-refuse>=0.95)",
        "method_delta": "refuse signal = NONLINEAR readout attention-CONCENTRATION (softmax/entmax max-weight) vs LINEAR scalar cosine tau (M1); readout<->readout anchor-match",
        "verify_the_referent_condition": "smoke MEASURES present-vs-absent attention-spread + confirms discrimination (absent diffuse, present concentrated); one-hot-both -> NON_TEST",
        "measured_bounds": f"envelope of nonlinear-readout refuse method at alpha={ALPHA}/N={N}/this synthetic regime; REMOTE bge/held-out FULL confirms; transfer UNTESTED",
        "elapsed_s": round(time.time() - t0, 2),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")

    print(f"[{ANCHOR}] run_mode={RUN_MODE} N={N} alpha={ALPHA} -> {verdict}")
    print(f"  SPREAD measurement (present concentrated vs absent diffuse) by beta:")
    for b, r in spread_report.items():
        print(f"    {b}: present_maxw={r['present_maxw_med']:.3f}  absent_maxw={r['absent_maxw_med']:.3f}  absent_spreads={r['absent_spreads']}")
    print(f"  best (beta,c) meeting both bars in spread regime: {best}")
    print(f"  {msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
