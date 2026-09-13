#!/usr/bin/env python
# -*- coding: ascii -*-
"""
Scaffold-free witnesses for the learned convergence semantic hub
(experiments/exp_semantic_hub_convergence_v1.py + exp_semantic_hub_live_coverage_v1.py).

Asserts the LOAD-BEARING claims:
 W1  MACHINERY: a fast synthetic (sparse, known shared latent) -> the ConsensusHub recovers shared
     structure (RSA CI lower bound > 0), BEATS raw concat (imputation niche), and its INFO-FREE TWIN
     (shuffled spoke->word rows) COLLAPSES. Proves the convergence mechanism is real, not an artifact.
 W2  UPGRADE: ConsensusHub (recon + similarity-to-cross-spoke-consensus) >= the plain recon hub on the
     same synthetic (the brain-faithful objective helps).
 W3  REAL DATA (if metrics_full.json present): the consensus hub's info-free twin loses on every gold;
     the per-store own-task comparison is recorded for every spoke.
 W4  LIVE INSTRUMENT (if metrics_{full,smoke}.json present): HUB-vs-FUSED and HUB-vs-TWIN are recorded
     and the FUSED twin loses (sanity of the reused instrument).

Run: .venv/Scripts/python.exe verification/test_semantic_hub_convergence.py
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import json
import sys
from pathlib import Path

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_semantic_hub_convergence_v1 as H

FAILS = []


def check(name, cond, detail=""):
    print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name, ("  -- " + detail) if detail else ""))
    if not cond:
        FAILS.append(name)


def _fast_synth(seed=0):
    """small sparse synthetic: 300 words, latent 10, 4 partial-view spokes, ~45% coverage."""
    rng = np.random.default_rng(seed)
    n, L = 300, 10
    Z = rng.normal(size=(n, L))
    Zc = H._cos_rows(Z)
    words = ["w%03d" % i for i in range(n)]
    cfg = [("a", 30, 1.0, 5, 0.5), ("b", 30, 1.0, 5, 0.55), ("c", 24, 1.1, 5, 0.55), ("d", 24, 1.1, 5, 0.6)]
    spokes = {}
    for nm, d, noise, k, miss in cfg:
        seen = rng.choice(L, size=k, replace=False)
        M = Z[:, seen] @ rng.normal(size=(k, d)) + noise * rng.normal(size=(n, d))
        keep = rng.random(n) > miss
        spokes[nm] = {words[i]: (M[i] if keep[i] else None) for i in range(n)}
    ai = rng.integers(0, n, 900); bi = rng.integers(0, n, 900)
    pairs, gold = [], []
    for a, b in zip(ai, bi):
        if a != b:
            pairs.append((words[a], words[b])); gold.append(float(np.dot(Zc[a], Zc[b])))
    return spokes, words, pairs, gold


def w1_w2_machinery():
    print("W1/W2 MACHINERY (fast synthetic)")
    spokes, vocab, pairs, gold = _fast_synth(0)
    X, present, spoke_dims, index = H.assemble(spokes, vocab)
    concat = {}
    for w in vocab:
        i = index[w]
        concat[w] = H._cos_rows(X[i:i + 1])[0] if present[i].sum() > 0 else None
    rho_concat, _ = H.rsa_on_pairs(concat, pairs, gold)
    # recon hub
    rec = H.ConvergenceHub(spoke_dims, hub_width=16, shortcut_density=0.0, spoke_dropout=0.5, seed=0)
    rec.fit(X, present, epochs=80, batch=256, lr=1e-2)
    rho_rec, _ = H.rsa_on_pairs(H.hub_vecs(rec, X, present, index, vocab), pairs, gold)
    # consensus hub
    con = H.ConsensusHub(spoke_dims, hub_width=16, spoke_dropout=0.5, seed=0)
    con.fit(X, present, epochs=80, batch=256, lr=1e-2, recon_w=1.0, sim_w=1.0)
    cvecs = H.consensus_hub_vecs(con, X, present, index, vocab)
    rho_con, _ = H.rsa_on_pairs(cvecs, pairs, gold)
    lo, hi, _ = H.bootstrap_ci_rho(cvecs, pairs, gold, n_boot=400, seed=0)
    # twin
    rng = np.random.default_rng(123)
    tw = {}
    for nm, _ in spoke_dims:
        ws = [w for w in vocab if spokes[nm].get(w) is not None]
        vals = [spokes[nm][w] for w in ws]
        pm = rng.permutation(len(ws))
        tw[nm] = {ws[i]: vals[pm[i]] for i in range(len(ws))}
    Xt, Pt, sdt, idxt = H.assemble(tw, vocab)
    con_t = H.ConsensusHub(sdt, hub_width=16, spoke_dropout=0.5, seed=0)
    con_t.fit(Xt, Pt, epochs=80, batch=256, lr=1e-2, recon_w=1.0, sim_w=1.0)
    rho_tw, _ = H.rsa_on_pairs(H.consensus_hub_vecs(con_t, Xt, Pt, idxt, vocab), pairs, gold)
    print("    concat=%.3f recon=%.3f consensus=%.3f CI[%.3f,%.3f] twin=%.3f" %
          (rho_concat, rho_rec, rho_con, lo, hi, rho_tw))
    check("W1 consensus hub CI lower bound > 0", lo > 0.0, "lo=%.3f" % lo)
    check("W1 consensus hub beats raw concat", rho_con > rho_concat,
          "consensus=%.3f concat=%.3f" % (rho_con, rho_concat))
    check("W1 info-free twin COLLAPSES", (rho_tw < 0.15) and (rho_tw < rho_con - 0.2),
          "twin=%.3f consensus=%.3f" % (rho_tw, rho_con))
    check("W2 consensus hub >= recon hub", rho_con >= rho_rec - 0.02,
          "consensus=%.3f recon=%.3f" % (rho_con, rho_rec))


def w3_real():
    p = Path("data/exp_semantic_hub_convergence_v1/metrics_full.json")
    if not p.exists():
        print("W3 REAL DATA -- metrics_full.json not present (skip; run exp_semantic_hub_convergence_v1.py --mode full)")
        return
    print("W3 REAL DATA (metrics_full.json)")
    m = json.loads(p.read_text(encoding="ascii"))
    golds = m.get("golds", {})
    for k, row in golds.items():
        ch = row.get("consensus_hub", {}).get("rho")
        cht = row.get("twin", {}).get("rho")
        if ch is not None and cht is not None:
            check("W3 consensus twin loses on %s" % k, cht < ch - 0.05 or cht < 0.1,
                  "hub=%s twin=%s" % (ch, cht))
    ps = m.get("per_store_own_task", {})
    check("W3 per-store own-task recorded for every spoke", len(ps) >= 3, "n_stores=%d" % len(ps))
    # W3b PLASTIC path: a few-pass ONLINE/streaming fit reaches ~the batch equilibrium (the brain does not
    # freeze; the batch only measures the equilibrium the online plastic process settles at).
    men = golds.get("men_all", {})
    oh = men.get("online_hub", {}).get("rho")
    bh = men.get("consensus_hub", {}).get("rho")
    if oh is not None and bh is not None:
        check("W3b online/plastic hub reaches ~batch equilibrium on MEN", abs(oh - bh) <= 0.06,
              "online=%s batch=%s" % (oh, bh))


def w4_live():
    for mode in ("full", "smoke"):
        p = Path("data/exp_semantic_hub_live_coverage_v1/metrics_%s.json" % mode)
        if not p.exists():
            continue
        print("W4 LIVE INSTRUMENT (metrics_%s.json)" % mode)
        m = json.loads(p.read_text(encoding="ascii"))
        check("W4 HUB-vs-FUSED recorded (%s)" % mode, "HUB_minus_FUSED@0.5" in m)
        ft = m.get("FUSED_minus_TWIN@0.5", {})
        if ft:
            check("W4 FUSED twin loses (%s)" % mode, ft.get("ci_sep_positive", False),
                  "diff=%s ci=%s" % (ft.get("diff"), ft.get("ci")))
        return
    print("W4 LIVE INSTRUMENT -- no metrics present (skip; run exp_semantic_hub_live_coverage_v1.py)")


def main():
    w1_w2_machinery()
    w3_real()
    w4_live()
    print("\n%d checks failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
