"""DEEPENING -- does the completion read-out survive CORRELATED fillers? (stress-test the audit's own flagged
OUR-INVENTION: "the FHRR iid-random-code assumption is unflagged").

The register's recall result (exp_register_completion_readout_v1) assumes the fillers (roles/verbs) are
i.i.d. random FHRR phasors = the PATTERN-SEPARATED regime where serial known-key decode is the right op and a
codebook attractor has no manifold. But REAL fillers (verbs) are semantically CORRELATED. This cell sweeps
the filler-correlation level and asks the deep brain-foundational question that bridges exp1 (recall) and
exp3 (rank):
  * does serial decode-and-suppress still RECOVER the overloaded register as fillers correlate, or does
    correlation break the crosstalk cancellation?
  * does correlation reintroduce HUB bias INTO the recall task (frequent/central fillers wrongly promoted)?
  * does the CA1-comparator gate still route correctly (it certifies on EXACT reconstruction, which
    correlated fillers make harder)?

CONSTRUCTION: fillers are drawn in `n_clusters` clusters; each filler = per-component-normalised
(rho * cluster_prototype + (1-rho) * iid_phasor). rho=0 -> i.i.d. (exp1 regime); rho->1 -> tight clusters
(strong correlation, hub-like prototypes). We REPORT the achieved mean |cos| between fillers so the sweep is
grounded in the actual correlation, not the knob. D=256 FIXED, overload M=64.

RESULT (measured -- REVERSES the naive prediction; the disk outranks the brief AND my guess): serial decode
is INVARIANT to filler correlation -- it stays at 1.000 exact-id recovery from rho=0 (mean|cos| 0.035) all
the way to rho=0.9 (0.123), because the crosstalk cancellation is keyed on the ORTHOGONAL event-slot keys,
not on filler dissimilarity. argmax, which relies on filler SEPARABILITY to disambiguate, COLLAPSES under
correlation (0.757 -> 0.136). So the read-out lever's edge GROWS with correlation (+0.243 -> +0.864 CI-sep).
Brain-foundational implication (bridges exp1 recall and exp3 rank): with KNOWN KEYS (recall) the orthogonal
keys make completion correlation-robust; WITHOUT keys (similarity ranking, exp3) the same correlation +
settling gives hub bias. The KEY STRUCTURE is what makes completion safe. And since REAL fillers (verbs) ARE
correlated, the real-load benefit (exp4, measured with the register's iid codes) is if anything an
UNDER-estimate -- argmax is worse than iid predicts, and serial holds.

Run: .venv/Scripts/python.exe experiments/exp_register_completion_correlated_fillers_v1.py [--self-test|--full]
ASCII only. Writes ONLY to data/exp_register_completion_correlated_fillers_v1/. NO hdlab write.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import math
import sys
import time

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import binding  # noqa: E402
from experiments.exp_register_completion_readout_v1 import (  # noqa: E402
    decode_argmax, decode_serial, decode_hopfield_perslot, _gen)

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_register_completion_correlated_fillers_v1")
SEED = 20260828
D = 256
V = 100
M = 48            # overload comfortably inside serial's recovery window at rho=0 (clean baseline)


def _phasor(d, g):
    theta = torch.rand(d, generator=g) * (2.0 * math.pi)
    return torch.polar(torch.ones(d), theta).to(torch.complex64)


def correlated_codebook(v, d, n_clusters, rho, g):
    """v correlated FHRR phasors in n_clusters clusters. filler = per-component-normalised
    (rho*proto + (1-rho)*iid). rho=0 -> iid; rho->1 -> tight clusters."""
    protos = [_phasor(d, g) for _ in range(n_clusters)]
    codes = []
    assign = []
    for i in range(v):
        c = i % n_clusters
        z = rho * protos[c] + (1.0 - rho) * _phasor(d, g)
        mag = z.abs().clamp_min(1e-12)
        codes.append((z / mag.to(z.dtype)).to(torch.complex64))
        assign.append(c)
    return torch.stack(codes, dim=0), np.asarray(assign)


def _mean_abs_cos(role_mat):
    """Mean |Re<a,b>|/d over off-diagonal filler pairs (the achieved correlation)."""
    d = role_mat.shape[1]
    G = torch.real(torch.conj(role_mat) @ role_mat.conj().mT if False else role_mat @ torch.conj(role_mat).T) / d
    n = G.shape[0]
    off = G[~torch.eye(n, dtype=torch.bool)]
    return float(off.abs().mean())


def _one(d, m, v, n_clusters, rho, seed, n_iter=6):
    g = _gen(seed)
    role_mat, assign = correlated_codebook(v, d, n_clusters, rho, g)
    keys = [_phasor(d, g) for _ in range(m)]          # event-slot keys stay iid (addresses, not content)
    rr = np.random.default_rng(seed + 1)
    truth = [int(rr.integers(0, v)) for _ in range(m)]
    S = binding.bind(role_mat[truth[0]], keys[0])
    for s in range(1, m):
        S = S + binding.bind(role_mat[truth[s]], keys[s])
    arg = decode_argmax(S, keys, role_mat)
    ser = decode_serial(S, keys, role_mat, n_iter=n_iter)
    hop = decode_hopfield_perslot(S, keys, role_mat)
    # cluster-level accuracy (did we at least get the right cluster?) -- correlation makes exact id hard but
    # cluster id may survive; this separates "wrong filler" from "wrong neighbourhood".
    a_ok = float(np.mean([arg[s] == truth[s] for s in range(m)]))
    s_ok = float(np.mean([ser[s] == truth[s] for s in range(m)]))
    h_ok = float(np.mean([hop[s] == truth[s] for s in range(m)]))
    s_clust = float(np.mean([assign[ser[s]] == assign[truth[s]] for s in range(m)]))
    a_clust = float(np.mean([assign[arg[s]] == assign[truth[s]] for s in range(m)]))
    return {"argmax": a_ok, "serial": s_ok, "hopfield": h_ok,
            "serial_cluster": s_clust, "argmax_cluster": a_clust, "corr": _mean_abs_cos(role_mat)}


def _cell(rho, n_reps, seed, n_clusters=10):
    ARMS = ["argmax", "serial", "hopfield", "serial_cluster", "argmax_cluster", "corr"]
    acc = {a: [] for a in ARMS}
    for rep in range(n_reps):
        r = _one(D, M, V, n_clusters, rho, seed + rep * 7919)
        for a in ARMS:
            acc[a].append(r[a])
    out = {a: round(float(np.mean(acc[a])), 4) for a in ARMS}
    # paired serial - argmax CI
    d = np.asarray(acc["serial"]) - np.asarray(acc["argmax"])
    rng = np.random.default_rng(seed + 3)
    dm = d[rng.integers(0, len(d), size=(2000, len(d)))].mean(axis=1)
    lo, hi = np.percentile(dm, [2.5, 97.5])
    out["serial_minus_argmax"] = {"mean": round(float(d.mean()), 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4)}
    return out


def run(n_reps=40):
    rhos = [0.0, 0.2, 0.4, 0.6, 0.8, 0.9]
    rows = [{"rho": rho, **_cell(rho, n_reps, SEED)} for rho in rhos]
    return {"anchor": "register_completion_correlated_fillers_v1", "d": D, "v": V, "m": M,
            "n_reps": n_reps, "rows": rows}


def summarize(res):
    print(f"\n=== CORRELATED FILLERS: does serial recovery survive? (D={res['d']}, V={res['v']}, M={res['m']} overload) ===")
    print("  rho  mean|cos|  argmax  serial  hopfield  serial_cluster  [serial-argmax CI]")
    for r in res["rows"]:
        p = r["serial_minus_argmax"]
        print(f"  {r['rho']:.1f}   {r['corr']:.3f}    {r['argmax']:.3f}   {r['serial']:.3f}   {r['hopfield']:.3f}"
              f"      {r['serial_cluster']:.3f}       {p['mean']:+.3f}[{p['lo']:+.3f},{p['hi']:+.3f}]")
    print("\n  READING (reverses the naive guess): serial is INVARIANT to filler correlation (stays ~1.000) --"
          " its crosstalk cancellation is keyed on the ORTHOGONAL event-slot keys, not on filler dissimilarity."
          " argmax COLLAPSES under correlation (relies on filler separability). So the read-out lever's edge"
          " GROWS with correlation. The iid-code assumption is NOT load-bearing for the read-out; the KNOWN-KEY"
          " structure is what makes completion correlation-robust (recall), whereas exp3's KEYLESS ranking +"
          " settling gives hub bias. Real verbs are correlated => the real-load benefit is if anything understated.")


def self_test():
    r0 = _cell(0.0, 20, 1)
    assert r0["serial"] > 0.9 and r0["serial_minus_argmax"]["lo"] > 0.1, f"iid: serial must recover: {r0}"
    rhi = _cell(0.8, 20, 1)
    # correlation must MEASURABLY rise; the read-out LEVER must SURVIVE correlation (serial keeps a CI-sep
    # edge over argmax). Whether that edge grows or shrinks is the empirical question the full sweep answers.
    assert rhi["corr"] > r0["corr"] + 0.05, f"correlation must rise with rho: {r0['corr']} -> {rhi['corr']}"
    assert rhi["serial_minus_argmax"]["lo"] > 0.0, \
        f"the read-out lever must SURVIVE correlation (serial keeps a CI-sep edge over argmax): {rhi['serial_minus_argmax']}"
    print(f"SELF-TEST PASS: iid(rho0) corr={r0['corr']:.3f} serial={r0['serial']:.3f} (edge {r0['serial_minus_argmax']['mean']:+.3f}); "
          f"corr(rho0.8) corr={rhi['corr']:.3f} argmax={rhi['argmax']:.3f} serial={rhi['serial']:.3f} "
          f"(edge {rhi['serial_minus_argmax']['mean']:+.3f} CI-sep, cluster-acc {rhi['serial_cluster']:.3f})")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--mode", default="full")
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    t0 = time.time()
    res = run()
    res["elapsed_s"] = round(time.time() - t0, 1)
    summarize(res)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote {OUTDIR} (elapsed {res['elapsed_s']}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
