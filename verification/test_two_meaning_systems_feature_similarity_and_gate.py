"""Scaffold-free witness for slug the_substrate_has_one_meaning_system_where_the_brain_has_two.

HEADLINE (recomputed here from the STATIC grounding asset, no corpus, no scaffold):
  BAR #1 -- the FEATURE-SIMILARITY system is built brain-faithfully. Distinctive-feature weighting
  (WHITEN away the dominant shared axis = the ATL's privilege-distinctive-features operation) beats the
  RAW grounded cosine on the SIMILARITY axis (SimLex-999 + SimVerb-test3000), CI-separated (paired
  bootstrap), with the info-free twin (shuffled grounding rows) LOSING and the concreteness floor
  cleared. This is the load-bearing, corpus-free part of bar #1 (the head-to-head vs the associative
  co-occurrence rep, and the semantic-control gate result, need the corpus -> checked by re-running the
  cells; their landed verdicts are asserted here for consistency).

Run: .venv/Scripts/python.exe verification/test_two_meaning_systems_feature_similarity_and_gate.py
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys

import numpy as np
from scipy.stats import spearmanr

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import grounded_similarity as GS
from hdlab.reading_grounding_loop import normalize_lemma

N_BOOT = 2000
SEED = 20260826


def _load(path, i1, i2, isc, sep):
    rows = []
    with open(os.path.join(REPO_ROOT, path), encoding="utf-8") as f:
        f.readline()
        for line in f:
            p = line.rstrip("\n").split(sep)
            if len(p) <= max(i1, i2, isc):
                continue
            try:
                rows.append((p[i1].strip().lower(), p[i2].strip().lower(), float(p[isc])))
            except ValueError:
                continue
    return rows


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na > 1e-12 and nb > 1e-12 else np.nan


def _rho(x, y):
    return float(spearmanr(x, y).statistic)


def main():
    tbl = GS._table()
    gwords = sorted(tbl.keys())
    gidx = {w: i for i, w in enumerate(gwords)}
    Xg = np.stack([tbl[w].numpy() for w in gwords]).astype(np.float64)

    simlex = _load("data/encoder_eval_benchmarks/simlex999.txt", 0, 1, 3, "\t")
    simverb = _load("data/encoder_eval_benchmarks/simverb3500_test3000.txt", 0, 1, 3, "\t")
    bench_vocab = {w for pr in (simlex, simverb) for a, b, _s in pr for w in (a, b)}

    # distinctive-feature transform (whiten), fit GOLD-BLIND + VOCAB-DISJOINT (exclude benchmark words)
    fit_mask = np.array([w not in bench_vocab for w in gwords])
    mu = Xg[fit_mask].mean(0)
    Xc = Xg[fit_mask] - mu
    ev, evec = np.linalg.eigh((Xc.T @ Xc) / len(Xc))
    o = np.argsort(ev)[::-1]
    ev, evec = ev[o], evec[:, o]
    Wt = evec * (1.0 / np.sqrt(ev + 1e-8))[None, :]     # k_drop=0, whiten=True

    def gvec(w):
        i = gidx.get(w) if gidx.get(w) is not None else gidx.get(normalize_lemma(w))
        return None if i is None else Xg[i]
    def raw(w):
        v = gvec(w); return v
    def dfw(w):
        v = gvec(w); return None if v is None else (v - mu) @ Wt

    rng = np.random.default_rng(SEED)
    perm = rng.permutation(len(gwords))
    Xsh = Xg[perm]
    def twin(w):
        i = gidx.get(w) if gidx.get(w) is not None else gidx.get(normalize_lemma(w))
        return None if i is None else (Xsh[i] - mu) @ Wt

    for name, pairs in (("SimLex-999", simlex), ("SimVerb-test", simverb)):
        cov = [(a, b, s) for a, b, s in pairs if dfw(a) is not None and dfw(b) is not None]
        cr_dfw = np.array([_cos(dfw(a), dfw(b)) for a, b, s in cov])
        cr_raw = np.array([_cos(raw(a), raw(b)) for a, b, s in cov])
        cr_tw = np.array([_cos(twin(a), twin(b)) for a, b, s in cov])
        conc = np.array([raw(a)[11] + raw(b)[11] for a, b, s in cov])
        gold = np.array([s for a, b, s in cov])
        r_dfw, r_raw = _rho(cr_dfw, gold), _rho(cr_raw, gold)
        r_tw, r_conc = _rho(cr_tw, gold), _rho(conc, gold)

        # paired bootstrap: rho(DFW) - rho(RAW)
        n = len(gold)
        diffs = np.empty(N_BOOT)
        rb = np.random.default_rng(SEED + 1)
        for i in range(N_BOOT):
            idx = rb.integers(0, n, n)
            diffs[i] = _rho(cr_dfw[idx], gold[idx]) - _rho(cr_raw[idx], gold[idx])
        lo = float(np.percentile(diffs, 2.5))

        print("[%s] n=%d  DFW=%.4f RAW=%.4f (d=%.4f CI_lo=%.4f)  twin=%.4f  conc=%.4f"
              % (name, n, r_dfw, r_raw, r_dfw - r_raw, lo, r_tw, r_conc))

        assert r_dfw > r_raw, "%s: distinctive-feature weighting must beat RAW grounding" % name
        assert lo > 0, "%s: DFW>RAW must be CI-separated (paired bootstrap ci_lo=%.4f)" % (name, lo)
        assert abs(r_tw) < 0.10 and r_dfw > abs(r_tw) + 0.10, (
            "%s: info-free twin must LOSE (twin=%.4f, DFW=%.4f)" % (name, r_tw, r_dfw))
        assert r_dfw > r_conc + 0.10, (
            "%s: DFW must clear the concreteness floor (DFW=%.4f conc=%.4f)" % (name, r_dfw, r_conc))

    # ---- assert the landed corpus-dependent verdicts are consistent (re-run cells to reproduce) ----
    def _verdict(path):
        with open(os.path.join(REPO_ROOT, path), encoding="utf-8") as f:
            return json.load(f)
    feat = _verdict("data/exp_feature_similarity_system_v1/metrics.json")
    assert feat["verdict"] == "FEATURE_SIMILARITY_SYSTEM_BEATS_ASSOCIATIVE_ON_SIMILARITY", feat["verdict"]
    for bn in ("SimLex999_sim", "SimVerb_test"):
        b = feat["report"][bn]["boot_DFW_minus_ASSOC"]
        assert b["ci_lo"] > 0, "%s: feature system must beat associative CI-sep (ci_lo=%.4f)" % (bn, b["ci_lo"])
    strong = _verdict("data/exp_semantic_control_strongassoc_gate_v1/metrics.json")
    assert strong["verdict"] == "EVEN_WITH_STRONG_ASSOC_BETTER_FUSED_THAN_SWITCHED", strong["verdict"]
    # the fixed blend must beat the task-gate (fusion > switching) with a strong associative system
    assert strong["gate_minus_fixed_blend"]["ci_hi"] < 0, (
        "strong-assoc: fixed blend must beat the task-gate CI-sep (gate-fixed ci_hi=%.4f)"
        % strong["gate_minus_fixed_blend"]["ci_hi"])
    # finer drill: linear whitening is the faithful op at this fidelity (nonlinear does not add)
    dfm = _verdict("data/exp_distinctive_feature_mechanism_v1/metrics.json")
    assert dfm["verdict"] == "LINEAR_WHITENING_IS_SUFFICIENT_NONLINEAR_DOES_NOT_ADD", dfm["verdict"]

    print("\nALL WITNESS ASSERTIONS PASSED")
    print("  bar #1: distinctive-feature-weighted grounding beats raw grounding AND the associative rep")
    print("          on SIMILARITY, CI-separated, info-free twin losing, floors cleared.")
    print("  bar #2: the task-switch gate does NOT beat a fixed blend (even with a strong associative")
    print("          system) -> the two systems are better FUSED than SWITCHED.")


if __name__ == "__main__":
    main()
