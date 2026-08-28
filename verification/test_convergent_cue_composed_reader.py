"""Scaffold-free witness for `compose_the_reader_by_convergent_cue_not_independent_conjunction`.

Reproduces the headline from the CACHED 60-doc records (data/exp_convergent_cue_composed_reader_v1/
records_60.json, built by the experiment) using the experiment's OWN readout functions -- no metric
crosses harnesses. Asserts the brain-faithful convergent-cue claim and every control that makes it
real:

  1. The reliability-weighted convergent read (learned w, HELD-OUT) BEATS meaning-solo, the STRONGEST
     floor, CI-separated (paired bootstrap over docs, lo > 0).  [it also trivially beats the brief's
     independent-AND straw floor and entity-solo.]
  2. Info-free MEANING twin (shuffled semantic cue) LOSES -> the gain is top-down semantic support.
  3. Info-free EPISODIC twin (shuffled episodic cue) does NOT beat meaning-solo -> the win is REAL
     convergence (needs the actual episodic evidence), not meaning-solo relabeled.
  4. The convergent read BEATS the FUSED one-pool store -> separated pools combined at read > fusion.
  5. The DOUBLE DISSOCIATION is preserved: lesion meaning -> entity-solo (nonzero); lesion entity ->
     meaning-solo (nonzero). Neither collapses.

Run:  .venv/Scripts/python.exe verification/test_convergent_cue_composed_reader.py
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))

import experiments.exp_convergent_cue_composed_reader_v1 as X  # noqa: E402


def main():
    recs = X.load_records(60, rebuild=False)
    assert len(recs) > 2000, f"expected the 60-doc records; got n={len(recs)} (run the experiment first)"
    tau_e = X._global_tau(recs, "epi"); tau_s = X._global_tau(recs, "sem"); tau_f = X._global_tau(recs, "fep")

    W_GRID = [1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0, 24.0]
    held_w, chosen_w = X._cv(recs, W_GRID, lambda r, w: X.pick_convergent_rw(r, tau_e, tau_s, w))
    w_med = float(np.median(chosen_w))

    def held_pairs(held):
        dd = {}
        for r in recs:
            d = r["doc"]; dd.setdefault(d, [0, 0])
            dd[d][0] += int(held[id(r)] == r["vi"]); dd[d][1] += 1
        return np.array([dd[d] for d in sorted(dd)], float)

    def rng_perm(r, salt):
        return list(np.random.default_rng(hash((r["doc"], r["vi"], salt)) % 2**31).permutation(r[
            "sem" if salt == 1 else "epi"]))

    HEAD = held_pairs(held_w)
    MEAN = X.per_doc_pairs(recs, X.pick_meaning)
    ENT = X.per_doc_pairs(recs, lambda r: X.pick_entity(r) if X.pick_entity(r) is not None else -1)
    AND = X.per_doc_pairs(recs, lambda r: r["vi"] if (X.pick_entity(r) == r["vi"] and X.pick_meaning(r) == r["vi"]) else -1)
    TWM = X.per_doc_pairs(recs, lambda r: X.pick_convergent_rw({**r, "sem": rng_perm(r, 1)}, tau_e, tau_s, w_med))
    TWE = X.per_doc_pairs(recs, lambda r: X.pick_convergent_rw({**r, "epi": (None if r["epi"] is None else rng_perm(r, 2))}, tau_e, tau_s, w_med))
    FUS = X.per_doc_pairs(recs, lambda r: X.pick_fused(r, tau_f, tau_s))

    def acc(p): return float(p[:, 0].sum() / max(p[:, 1].sum(), 1))
    checks = []

    d = X.paired(HEAD, MEAN, 101)
    checks.append(("convergent BEATS meaning-solo (strongest floor) CI-sep", d["band"] == "ABOVE", d))
    d = X.paired(HEAD, AND, 102)
    checks.append(("convergent BEATS independent-AND (brief floor) CI-sep", d["band"] == "ABOVE", d))
    d = X.paired(HEAD, ENT, 103)
    checks.append(("convergent BEATS entity-solo CI-sep", d["band"] == "ABOVE", d))
    d = X.paired(HEAD, TWM, 104)
    checks.append(("convergent BEATS shuffled-MEANING twin CI-sep", d["band"] == "ABOVE", d))
    d = X.paired(TWE, MEAN, 105)
    checks.append(("shuffled-EPISODIC twin does NOT beat meaning-solo (win is real convergence)", d["band"] != "ABOVE", d))
    d = X.paired(HEAD, FUS, 106)
    checks.append(("convergent BEATS fused one-pool store CI-sep", d["band"] == "ABOVE", d))
    checks.append((f"double dissociation: lesion-meaning=entity-solo {acc(ENT):.4f}>0 AND lesion-entity=meaning-solo {acc(MEAN):.4f}>0",
                   acc(ENT) > 0.0 and acc(MEAN) > 0.0, {"entity_solo": round(acc(ENT), 4), "meaning_solo": round(acc(MEAN), 4)}))

    print(f"records n={len(recs)}  w(median held-out)={w_med}")
    print(f"  meaning_solo {acc(MEAN):.4f}  entity_solo {acc(ENT):.4f}  AND {acc(AND):.4f}  "
          f"FUSED {acc(FUS):.4f}  CONVERGENT {acc(HEAD):.4f}")
    ok = True
    for name, passed, detail in checks:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}\n         {detail}")
        ok = ok and passed
    print("\n" + ("ALL CHECKS PASS -- convergent-cue composition beats the strongest floor, twins lose, "
                  "fused loses, dissociation preserved" if ok else "WITNESS FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
