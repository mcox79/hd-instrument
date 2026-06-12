"""
exp_pp405_compositional_factor_disentanglement_cpu_v1.py -- PP-405 compositional factor disentanglement via resonator network.

Cycle 53 capability-portfolio build (research_to_exp_dev_CYCLE_53_RESONATOR_NETWORK_SCOPING..PP_405_PP_406). 1st of two capabilities
winning via the off-attractor mechanism `resonator_network_decoder` (existing substrate atom; Frady-Kent-Olshausen-Sommer 2020). If
PP-405 + PP-406 both win, the Tier-5 miner gets a RECURRING (n_caps=2) transition `greedy_unbind -> resonator_network_decoder` = the
4th novel recurring rule = Tier-5 fifth-appearance. Mechanism DISTINCT from P^k (positional) + TCM (temporal) + LEX_T (semantic
constant): ITERATIVE MULTI-FACTOR DECODING (disentangles a bound product into ALL its factors, not a single argmax).

Task: given a bound product B = bind(f_1, ..., f_K) of K factors (each drawn from its own codebook of M symbols), decode all K factors.
  Resonator: hold per-factor superposition estimates; iterate x_hat_i <- proj_i(B (*) conj(prod_{j!=i} x_hat_j)) until convergence;
             read out argmax per factor. (Frady-Sommer resonator dynamics for FHRR phasors.)
  Greedy-unbind baseline (fair, structurally limited): single cleanup of B against each codebook independently -- B carries no
             isolated signal for any one factor (it is the product of all), so greedy decoding is ~chance. This is the structural
             reason single-unbind cannot factor a multi-factor product; the resonator's iterative refinement is the lever.

Metric: joint accuracy (ALL K factors correct) + mean per-factor accuracy, resonator vs greedy, over a phase-noise sweep.
Pre-reg (Research): HP joint acc >= 0.65 + beats greedy by >= 0.15 every noise + distinct mechanism. MIDDLE lift >= 0.15 clean +
distinct. HARD_FAIL lift < 0.15 OR == greedy.

PACING (transparent, per PP-404 precedent + Research's explicit sanction): mechanism isolation is independent of the stalled Testbed
ingest; build proceeds, Tier-5 5th-appearance CLAIM stays gated on live confirmation.

--self-test + --smoke. Laptop-CPU. No LLM-judge. Deterministic seeds. Self-contained. D=4096.
"""
from __future__ import annotations
import argparse, json, sys, time, zlib
from pathlib import Path
import numpy as np

D = 4096
M = 12         # codebook size per factor
RESONATOR_ITERS = 50


def _fhrr(seed):
    rng = np.random.default_rng(seed)
    return np.exp(1j * rng.uniform(0, 2 * np.pi, D))


def _codebook(factor, trial):
    """(D, M) complex codebook for a factor: M candidate symbol vectors."""
    return np.stack([_fhrr(zlib.crc32(("cb:%d:%d:%d" % (trial, factor, m)).encode()) & 0x7fffffff) for m in range(M)], axis=1)


def _proj(vec, cb):
    """project a noisy factor estimate onto the codebook span (superposition cleanup); returns a unit-phasor-ish estimate."""
    sims = cb.conj().T @ vec            # (M,) complex similarities
    est = cb @ sims                     # weighted superposition
    m = np.abs(est); m[m < 1e-9] = 1.0
    return est / m                      # renormalize to phasor magnitudes


def _resonator(B, cbs, iters=RESONATOR_ITERS):
    """Iterative multi-factor decode. Returns list of argmax symbol indices per factor."""
    K = len(cbs)
    xh = [cb.mean(axis=1) for cb in cbs]              # init: codebook mean (uniform superposition)
    xh = [x / (np.abs(x) + 1e-9) for x in xh]
    prev = None
    for _ in range(iters):
        for i in range(K):
            others = np.ones(D, dtype=complex)
            for j in range(K):
                if j != i:
                    others = others * np.conj(xh[j])
            xh[i] = _proj(B * others, cbs[i])
        guess = tuple(int(np.argmax(np.real(cbs[i].conj().T @ (B * _others(xh, i))))) for i in range(K))
        if guess == prev:
            break
        prev = guess
    return list(prev if prev is not None else guess)


def _others(xh, i):
    o = np.ones(D, dtype=complex)
    for j in range(len(xh)):
        if j != i:
            o = o * np.conj(xh[j])
    return o


def _greedy(B, cbs):
    """Greedy single-cleanup: decode each factor by cleanup of the FULL product against its codebook (no iteration)."""
    return [int(np.argmax(np.real(cb.conj().T @ B))) for cb in cbs]


def _eval_at_noise(n_trials, seed0, noise, k_lo=3, k_hi=5):
    res_joint = res_fac = grd_joint = grd_fac = tot = totf = 0
    for t in range(n_trials):
        rng = np.random.default_rng(seed0 + t * 733)
        K = int(rng.integers(k_lo, k_hi + 1))
        cbs = [_codebook(i, t) for i in range(K)]
        gold = [int(rng.integers(0, M)) for i in range(K)]
        B = np.ones(D, dtype=complex)
        for i in range(K):
            B = B * cbs[i][:, gold[i]]
        if noise > 0:
            B = B * np.exp(1j * noise * rng.standard_normal(D))
        r = _resonator(B, cbs)
        g = _greedy(B, cbs)
        res_joint += int(r == gold); grd_joint += int(g == gold)
        res_fac += sum(int(r[i] == gold[i]) for i in range(K))
        grd_fac += sum(int(g[i] == gold[i]) for i in range(K))
        tot += 1; totf += K
    return {"res_joint": res_joint / tot, "grd_joint": grd_joint / tot,
            "res_fac": res_fac / totf, "grd_fac": grd_fac / totf}


def run(n_trials=60, seed0=531, verbose=True):
    rows = []
    for noise in (0.0, 0.8, 1.6, 2.4):
        r = _eval_at_noise(n_trials, seed0, noise)
        rows.append({"noise": noise, "res_joint": round(r["res_joint"], 4), "grd_joint": round(r["grd_joint"], 4),
                     "res_fac": round(r["res_fac"], 4), "grd_fac": round(r["grd_fac"], 4),
                     "lift": round(r["res_joint"] - r["grd_joint"], 4)})
    if verbose:
        print("=== PP-405 compositional factor disentanglement (resonator vs greedy-unbind) ===")
        print("trials:", n_trials, "| K=3-5 factors | M=%d symbols/codebook | D:" % M, D)
        print("%-7s %-22s %-22s %-10s" % ("noise", "resonator joint/fac", "greedy joint/fac", "joint-lift"))
        for r in rows:
            print("%-7.1f %-22s %-22s %+0.4f" % (r["noise"], "%.4f / %.4f" % (r["res_joint"], r["res_fac"]),
                                                 "%.4f / %.4f" % (r["grd_joint"], r["grd_fac"]), r["lift"]))
    clean, noisy = rows[0], rows[-1]
    persists = all(r["lift"] >= 0.15 for r in rows)
    distinct_and_winning = clean["lift"] >= 0.15
    if clean["res_joint"] >= 0.65 and persists:
        verdict = "PASS"
        msg = ("PP-405 HP: resonator joint-decode %.4f >=0.65 AND beats greedy-unbind by >=0.15 every noise -> resonator_network_decoder validated robust; with PP-406 triggers Tier-5 5th-appearance (greedy_unbind -> resonator_network_decoder). CLAIM gated on live confirm." % clean["res_joint"])
    elif distinct_and_winning:
        verdict = "MIDDLE"
        msg = ("PP-405 MIDDLE -- resonator joint-decode %.4f beats greedy-unbind %.4f by +%0.4f clean (greedy structurally fails to factor a multi-factor product; resonator iteratively disentangles all K). Distinct iterative-decoding mechanism. Lift %+0.4f at noise %.1f%s." % (clean["res_joint"], clean["grd_joint"], clean["lift"], noisy["lift"], noisy["noise"], "" if persists else " (noise-fragile)"))
    else:
        verdict = "HARD_FAIL"
        msg = ("PP-405 resonator shows no advantage over greedy-unbind (clean lift %+0.4f < 0.15) -- honest negative." % clean["lift"])
    return {"verdict": verdict, "verdict_msg": msg, "summary": {"D": D, "M": M, "rows": rows, "distinct_and_winning": distinct_and_winning}}


def _self_test():
    # resonator decodes a clean 3-factor product exactly; greedy does not
    t = 0; cbs = [_codebook(i, t) for i in range(3)]
    gold = [2, 7, 5]
    B = cbs[0][:, 2] * cbs[1][:, 7] * cbs[2][:, 5]
    assert _resonator(B, cbs) == gold, _resonator(B, cbs)
    g = _greedy(B, cbs)
    assert g != gold, g  # greedy single-cleanup cannot factor the product
    print("[self-test] PASS: resonator decodes 3-factor product exactly %s; greedy fails %s" % (gold, g))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--n", type=int, default=60)
    args = ap.parse_args()
    t0 = time.time()
    if args.self_test:
        _self_test(); sys.exit(0)
    res = run(n_trials=args.n, verbose=True)
    res["elapsed_s"] = round(time.time() - t0, 2)
    print()
    print("VERDICT:", res["verdict"], "--", res["verdict_msg"])
    if args.smoke:
        Path("metrics.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
        print("[smoke] wrote metrics.json")
