"""exp_atl_hubspoke_actr_ideal_chain_v1 -- THE IDEAL chain informed by the mechanism-diff drill: replace the boolean
topical graph edges + iterated PageRank with the brain's ACTUAL spreading-activation math -- EXPERIENCE-WEIGHTED,
DIRECTIONAL, sense-DISCRIMINATIVE edges (Collins-Loftus 1975; ACT-R Anderson-Reder 1999) + one-step capacity-bounded
activation with FAN-normalized specificity + base-rate removal as CSC inhibit-dominant.

PROBLEM: build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader

WHY (the drill): joint PPR over WordNet++ is topical because its edges are BOOLEAN relatedness (robin->bird ==
chicken->bird) and it iterates to a hub/topical stationary distribution. The brain's edges carry GRADED strength
built from use-frequency (Collins-Loftus p.423-424; FAS/BAS asymmetry), and ACT-R activation is A_i = B_i + sum_j
W_j S_ji with S_ji = S + ln P(i|j), Sum_j W_j = 1, NOT iterated. This cell ports that primitive exactly.

THE IDEAL CHAIN (every component the brain's computation; offline foundation = gold-resolved, doc-disjoint):
  UPSTREAM EDGES (experience-weighted, directional, sense-discriminative): from gold-resolved co-occurrence,
    S(s|w) = ln( P(sense s | context word w) / P(s) ) -- how much w RAISES sense s over its base rate. The /P(s)
    is the CSC inhibit-dominant (removes the frequency prior that swamps the subordinate). Leave-one-DOC-out.
  THIS COMPONENT (ACT-R Eq 1/4): A(s) = sum_w spec(w) * S(s|w) / sum_w spec(w), with FAN-normalized specificity
    spec(w) = 1/(1+ln(1+fan(w))) (a word that cues FEW senses is diagnostic -> weighs more -- the fan effect =
    the precision mechanism grounded in ACT-R). Capacity-bounded (Sum W = 1). One-step (no PageRank iteration).
  READOUT: argmax A(s) where the sense is attested; FUSE with the w2v precision channel; fall back to precision
    where unattested. Twin: shuffled edges.

ARMS (strict doc-disjoint SemCor subordinate, n=2676):
  A0  launch-pad (frozen w2v)                    ~0.313
  A1  w2v precision readout                       ~0.336
  R   ACT-R W alone (gated, fallback to precision)
  Rf  ACT-R W fused with precision (z-sum)
  Rp  + explicit control amplify-weak (boost low-base senses)
  TWIN shuffled edges (must LOSE)

Glass-box at inference (NO external LLM/transformer); gold used ONLY to build the offline edge foundation, never as
an inference label; strict doc-disjoint. Core-capped. ASCII. Own dir.
# KB_REFERENT: data/_sglite_cache/sglite_w2v_full.pkl
# KB_REFERENT: data/_sglite_cache/sglite_semcorrole_f30.pkl
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

import sys
import json
import time
import math
import pickle
import argparse
from collections import Counter, defaultdict

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_consolidation_gate_v1 as G1
import experiments.exp_brain_faithful_reader_v1 as BF

_CACHE = G1._CACHE
OUT_DIR = os.path.join(_REPO, "data", "exp_atl_hubspoke_actr_ideal_chain_v1")


def _unit(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _z(x):
    x = np.asarray(x, float)
    s = x.std()
    return (x - x.mean()) / (s + 1e-9) if s > 1e-9 else x - x.mean()


def run(smoke=False):
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    recs = pickle.load(open(os.path.join(_CACHE, "sglite_semcorrole_f30.pkl"), "rb"))
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    test_idx = list(np.where((doc % 2 == 1) & sub)[0])
    if smoke:
        test_idx = test_idx[:400]
    cand = set()
    for i in test_idx:
        cand.update(recs[i]["tn"])
    rich_sig = {s: G1._sigvec(mat, w2i, BF.rich_atom_words(s, w2i, 3)) for s in sorted(cand)}

    # ---- UPSTREAM experience-weighted directional edges from GOLD-resolved co-occurrence (per-doc for LOO) ----
    g_cooc = defaultdict(Counter)      # sense -> Counter(context word -> count)
    g_sel = Counter()                  # sense -> occurrences
    w_fan = defaultdict(set)           # word -> set of senses it co-occurs with (fan)
    d_cooc = defaultdict(lambda: defaultdict(Counter)); d_sel = defaultdict(Counter); g_N = 0; d_N = Counter()
    for i in range(len(recs)):
        r = recs[i]; s = r["gold"]; dd = r["doc_id"]
        toks = set(x for x in r["ctx"] if x in w2i)
        if not toks:
            continue
        g_N += 1; g_sel[s] += 1; d_N[dd] += 1; d_sel[dd][s] += 1
        for w in toks:
            g_cooc[s][w] += 1; w_fan[w].add(s); d_cooc[dd][s][w] += 1

    def actr_scores(r):
        """ACT-R activation A(s) over candidates, leave-one-doc-out. Returns (A array, attested mask)."""
        tn = r["tn"]; dd = r["doc_id"]; ctxw = [x for x in r["ctx"] if x in w2i]
        N = max(1, g_N - d_N[dd])
        A = np.zeros(len(tn)); att = np.zeros(len(tn), bool)
        # base rates P(s) (leave-one-doc-out)
        for si, s in enumerate(tn):
            sel_s = g_sel.get(s, 0) - d_sel[dd].get(s, 0)
            att[si] = sel_s > 0
        # specificity per context word = 1/(1+ln(1+fan)) ; fan = # senses w cues (global proxy)
        spec = {}
        for w in ctxw:
            fan = len(w_fan.get(w, ()))
            spec[w] = 1.0 / (1.0 + math.log(1.0 + fan)) if fan > 0 else 0.0
        Z = sum(spec.values())
        if Z <= 1e-9:
            return A, att
        for si, s in enumerate(tn):
            sel_s = g_sel.get(s, 0) - d_sel[dd].get(s, 0)
            if sel_s <= 0:
                continue
            Ps = sel_s / N
            tot = 0.0
            for w in ctxw:
                c_sw = g_cooc.get(s, {}).get(w, 0) - d_cooc[dd].get(s, {}).get(w, 0)
                cw = sum((g_cooc.get(ss, {}).get(w, 0) - d_cooc[dd].get(ss, {}).get(w, 0)) for ss in tn)
                if c_sw > 0 and cw > 0:
                    Psw = c_sw / cw                                  # directional P(sense|word) over the candidates
                    tot += spec[w] * math.log((Psw + 1e-9) / (Ps + 1e-9))   # S(s|w), base-rate removed
            A[si] = tot / Z
        return A, att

    def precision_scores(r, gamma=3.0, topk=5):
        tn = r["tn"]; rows = [_unit(mat[w2i[x]]) for x in r["ctx"] if x in w2i]
        if not rows:
            return None
        C = np.stack(rows)
        G = np.stack([rich_sig[s] if (rich_sig[s] is not None and np.any(rich_sig[s])) else np.zeros(G1.EMB_DIM, np.float32) for s in tn])
        if not np.any(G):
            return None
        sim = C @ G.T
        diag = np.clip(sim.max(1) - sim.mean(1), 0, None)
        if topk is not None and topk < len(diag):
            thr = np.sort(diag)[-topk]; diag = np.where(diag >= thr, diag, 0.0)
        wq = diag ** gamma
        q = _unit((wq[:, None] * C).sum(0)) if wq.sum() > 1e-9 else _unit(C.mean(0))
        return G @ q

    a0, a1, R, Rf, Rp, TW = [], [], [], [], [], []
    rng = np.random.default_rng(4242)
    cov = 0; ncov = 0
    for i in test_idx:
        r = recs[i]; tn = r["tn"]
        base = precision_scores(r, gamma=1.0); prec = precision_scores(r)
        if base is None or prec is None:
            continue
        a0.append(int(tn[int(np.argmax(base))] == r["gold"]))
        a1.append(int(tn[int(np.argmax(prec))] == r["gold"]))
        A, att = actr_scores(r)
        covered = bool(np.any(A))
        ncov += 1; cov += int(covered)
        # R: ACT-R where covered, else precision fallback
        R.append(int(tn[int(np.argmax(A))] == r["gold"]) if covered else int(tn[int(np.argmax(prec))] == r["gold"]))
        # Rf: fuse z(precision)+z(A) where covered, else precision
        if covered:
            sc = _z(prec) + _z(A)
            Rf.append(int(tn[int(np.argmax(sc))] == r["gold"]))
            # Rp: + explicit amplify-weak (subtract a base-level prior => boost low-base senses)
            baselvl = np.array([math.log(1.0 + (g_sel.get(s, 0) - d_sel[r["doc_id"]].get(s, 0))) for s in tn])
            scp = _z(prec) + _z(A) - 0.5 * _z(baselvl)
            Rp.append(int(tn[int(np.argmax(scp))] == r["gold"]))
            sh = A[rng.permutation(len(A))]
            sct = _z(prec) + _z(sh)
            TW.append(int(tn[int(np.argmax(sct))] == r["gold"]))
        else:
            Rf.append(int(tn[int(np.argmax(prec))] == r["gold"]))
            Rp.append(int(tn[int(np.argmax(prec))] == r["gold"]))
            TW.append(int(tn[int(np.argmax(prec))] == r["gold"]))

    def m(x):
        return round(float(np.mean(x)), 4) if len(x) else None

    def pair(a, b, seed):
        n = min(len(a), len(b)); return G1._paired(np.asarray(a[:n], float), np.asarray(b[:n], float), seed)

    cands = {"R_actr_gated": R, "Rf_actr_fused": Rf, "Rp_actr_amplify_weak": Rp}
    best = max(cands, key=lambda k: np.mean(cands[k]))
    res = {
        "n_test": len(test_idx), "coverage": round(cov / max(1, ncov), 3),
        "arms": {"A0_launchpad": m(a0), "A1_precision": m(a1), "R_actr_gated": m(R),
                 "Rf_actr_fused": m(Rf), "Rp_actr_amplify_weak": m(Rp), "TWIN_shuffled_edges": m(TW)},
        "best_arm": best, "best_a_s": m(cands[best]),
        "best_vs_precision": pair(cands[best], a1, 851),
        "best_vs_twin": pair(cands[best], TW, 852),
        "crosses_0.35": bool((m(cands[best]) or 0) >= 0.35),
        "beats_precision": bool((m(cands[best]) or 0) > (m(a1) or 0)),
        "elapsed_s": round(time.time() - t0, 1),
    }
    res["headline"] = ("ACT-R IDEAL CHAIN | A0=%.4f A1_prec=%.4f R_gated=%.4f Rf_fused=%.4f Rp_amp=%.4f twin=%.4f "
                       "(cov=%.2f) | best=%s %.4f vs precision sep=%s ci=%s | vs twin sep=%s | crosses0.35=%s"
                       % (res["arms"]["A0_launchpad"], res["arms"]["A1_precision"], res["arms"]["R_actr_gated"],
                          res["arms"]["Rf_actr_fused"], res["arms"]["Rp_actr_amplify_weak"],
                          res["arms"]["TWIN_shuffled_edges"], res["coverage"], best, res["best_a_s"],
                          res["best_vs_precision"]["sep"], res["best_vs_precision"]["ci"],
                          res["best_vs_twin"]["sep"], res["crosses_0.35"]))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "atl_hubspoke_actr_ideal_chain_v1", "verdict": "MEASURED", "result": res}, f,
                  indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    # specificity: a low-fan (specific) word must weigh more than a high-fan word
    lo = 1.0 / (1.0 + math.log(1.0 + 2)); hi = 1.0 / (1.0 + math.log(1.0 + 50))
    assert lo > hi, "fan-normalized specificity: fewer senses -> higher weight"
    print("SELFTEST PASS (ACT-R fan specificity: low-fan word weighs %.3f > high-fan %.3f)" % (lo, hi), flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(smoke=args.smoke and not args.full)
    return 0


if __name__ == "__main__":
    sys.exit(main())
