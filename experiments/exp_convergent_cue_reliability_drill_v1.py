"""DEEPENING DRILL (fidelity, not a new deliverable): is the convergent-cue COMBINATION RULE near
its ceiling given these two cues, or is there headroom for a MORE brain-faithful PER-QUERY reliability
weighting? Ernst-Banks/Ma reliability is per-OBSERVATION -- each cue weighted by its OWN confidence on
THAT query -- but the headline uses a single global learned weight w. This drill tests explicit
per-query precision weighting and bounds the achievable gain with an oracle, to localize the wall.

Reads the CACHED 60-doc records (no re-extraction). Reports:
  * meaning-solo / entity-solo / headline RWW (context).
  * ORACLE_UNION = correct iff EITHER cue's argmax is v = the tightest ceiling for ANY one-answer
    selector between these two cues. headline-vs-oracle gap = how much the RULE leaves on the table.
  * entity-solo ON the meaning-solo-WRONG subset = the episodic RESCUE ceiling (bounded by store quality).
  * CONVERGENT_PQ = PER-QUERY precision-weighted read: joint(c) = conf_epi*z(epi)(c) + a*conf_sem*z(sem)(c),
    conf = 1 - normalized_entropy of that cue's posterior (its reliability on THIS query), a learned
    (CV, held-out) global code-scale ratio. This is the fuller Ernst-Banks form. Does it beat RWW?
  If PQ ~= RWW ~= oracle -> the rule is near-optimal and the wall is the DENSE episodic store (p2), not
  the combination. If PQ > RWW -> per-query reliability is a real further optimization.

Run: .venv/Scripts/python.exe experiments/exp_convergent_cue_reliability_drill_v1.py [--docs N]
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


def _conf(p):
    p = np.asarray(p, float); p = p / p.sum()
    k = len(p)
    if k <= 1:
        return 0.0
    h = -np.sum(p * np.log(p + 1e-12)) / np.log(k)   # normalized entropy in [0,1]
    return float(1.0 - h)                             # peakedness = reliability of this observation


def pick_pq(r, tau_e, tau_s, a):
    """Per-query precision-weighted convergent read (fuller Ernst-Banks): each cue's z-normalized shape
    weighted by its per-query confidence; a = learned global code-scale ratio (semantic vs episodic)."""
    z_sem = X._zn(r["sem"]); c_sem = _conf(X._softmax(np.asarray(r["sem"]) / tau_s))
    if r["epi"] is None:
        return int(np.argmax(z_sem))
    z_epi = X._zn(r["epi"]); c_epi = _conf(X._softmax(np.asarray(r["epi"]) / tau_e))
    return int(np.argmax(c_epi * z_epi + a * c_sem * z_sem))


def main():
    docs = 60
    if "--docs" in sys.argv:
        docs = int(sys.argv[sys.argv.index("--docs") + 1])
    recs = X.load_records(docs, rebuild=False)
    n = len(recs); tau_e = X._global_tau(recs, "epi"); tau_s = X._global_tau(recs, "sem")
    vi = [r["vi"] for r in recs]
    es = [X.pick_entity(r) for r in recs]
    ms = [X.pick_meaning(r) for r in recs]

    meaning_solo = np.mean([int(ms[i] == vi[i]) for i in range(n)])
    entity_solo = np.mean([int(es[i] == vi[i]) for i in range(n)])
    oracle_union = np.mean([int(es[i] == vi[i] or ms[i] == vi[i]) for i in range(n)])

    # headline RWW (learned w, held-out)
    W_GRID = [1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0, 24.0]
    held_w, chosen_w = X._cv(recs, W_GRID, lambda r, w: X.pick_convergent_rw(r, tau_e, tau_s, w))
    rww = np.mean([int(held_w[id(r)] == r["vi"]) for r in recs])

    # per-query precision-weighted (learned a, held-out)
    A_GRID = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0]
    held_a, chosen_a = X._cv(recs, A_GRID, lambda r, a: pick_pq(r, tau_e, tau_s, a))
    pq = np.mean([int(held_a[id(r)] == r["vi"]) for r in recs])

    # rescue ceilings on the meaning-solo-WRONG subset
    msw = [i for i in range(n) if ms[i] != vi[i]]
    es_on_msw = np.mean([int(es[i] == vi[i]) for i in msw]) if msw else float("nan")

    def paired_docs(pickA, pickB, seed):
        dd = {}
        for i, r in enumerate(recs):
            d = r["doc"]; dd.setdefault(d, [0, 0, 0])
            dd[d][0] += int(pickA(i)); dd[d][1] += int(pickB(i)); dd[d][2] += 1
        arr = np.array([dd[d] for d in sorted(dd)], float)
        rng = np.random.default_rng(seed); nd = len(arr); dl = []
        for _ in range(2000):
            s = arr[rng.integers(0, nd, nd)]
            dl.append(s[:, 0].sum() / max(s[:, 2].sum(), 1) - s[:, 1].sum() / max(s[:, 2].sum(), 1))
        lo, hi = float(np.percentile(dl, 2.5)), float(np.percentile(dl, 97.5))
        pt = arr[:, 0].sum() / arr[:, 2].sum() - arr[:, 1].sum() / arr[:, 2].sum()
        return {"delta": round(float(pt), 4), "ci": [round(lo, 4), round(hi, 4)],
                "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}

    print(f"=== reliability drill (n={n}) ===")
    print(f"  entity-solo            {entity_solo:.4f}")
    print(f"  meaning-solo           {meaning_solo:.4f}  <- strongest floor")
    print(f"  RWW (headline, w~{int(np.median(chosen_w))})     {rww:.4f}")
    print(f"  PQ per-query precision {pq:.4f}  (learned a per fold {chosen_a})")
    print(f"  ORACLE_UNION (ceiling) {oracle_union:.4f}  <- best any 1-answer selector between the 2 cues")
    print(f"\n  headline gap to oracle : {oracle_union - rww:+.4f}")
    print(f"  PQ gap to oracle       : {oracle_union - pq:+.4f}")
    print(f"  episodic RESCUE ceiling on meaning-solo-WRONG (n={len(msw)}): entity-solo there = {es_on_msw:.4f}")
    conv = [X.pick_convergent_rw(r, tau_e, tau_s, float(np.median(chosen_w))) for r in recs]
    rescued = np.mean([int(conv[i] == vi[i]) for i in msw]) if msw else float("nan")
    print(f"  convergent ACHIEVES on meaning-solo-WRONG        : {rescued:.4f}  "
          f"(of the {es_on_msw:.4f} reachable via episodic)")

    print("\n  --- is PER-QUERY reliability a real further optimization? ---")
    d_pq_rww = paired_docs(lambda i: held_a[id(recs[i])] == vi[i], lambda i: held_w[id(recs[i])] == vi[i], 7)
    print(f"  PQ - RWW (held-out, paired): {d_pq_rww}")
    d_rww_oracle = paired_docs(lambda i: held_w[id(recs[i])] == vi[i], lambda i: (es[i] == vi[i] or ms[i] == vi[i]), 8)
    print(f"  RWW - ORACLE (paired): {d_rww_oracle}  (BELOW expected; size = rule headroom)")

    # --- mechanistic confirmation: does the convergence gain TRACK episodic reliability? ---
    # (the compounding prediction: where the episodic read is more reliable, episodic contributes more
    #  and the gain over meaning-solo is larger -- validated WITHIN the current store, no p2 needed.)
    print("\n  --- convergence gain vs EPISODIC reliability (peakedness of p_epi), quartile bins ---")
    ce = [(_conf(X._softmax(np.asarray(r["epi"]) / tau_e)) if r["epi"] is not None else 0.0) for r in recs]
    conv_all = [X.pick_convergent_rw(r, tau_e, tau_s, float(np.median(chosen_w))) for r in recs]
    idx_sorted = sorted(range(n), key=lambda i: ce[i])
    qs = np.array_split(idx_sorted, 4)
    print("   bin  epi_conf   entity_solo  meaning_solo  convergent   gain(conv-mean)")
    for qi, q in enumerate(qs):
        q = list(q)
        eic = np.mean([ce[i] for i in q]); ent = np.mean([int(es[i] == vi[i]) for i in q])
        mea = np.mean([int(ms[i] == vi[i]) for i in q]); cnv = np.mean([int(conv_all[i] == vi[i]) for i in q])
        print(f"   Q{qi+1}   {eic:.3f}      {ent:.4f}       {mea:.4f}        {cnv:.4f}       {cnv-mea:+.4f}")
    print("   (prediction: gain rises with episodic reliability -> the weighting is genuinely reliability-driven)")

    print("\n  INTERPRETATION:")
    if d_pq_rww["band"] == "ABOVE":
        print("    PER-QUERY reliability weighting BEATS the global weight -> a real further optimization.")
    else:
        print("    PER-QUERY weighting does NOT beat the global weight -> global-tau softmax already")
        print("    captures per-query reliability (peakedness); the wall is the DENSE episodic STORE (p2),")
        print("    not the combination rule (convergent is near the union ceiling given these cues).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
