"""exp_frame_sense_subordinate_recovery_v1 -- the FAIR test the owner's challenge demands: the brain beats MFS by
recovering the SUBORDINATE sense from CONTEXT. So measure, on the cases where per-lemma MFS is WRONG, whether the
mechanism recovers the gold -- and whether adding a CONTEXT cue (the brain's actual lever, omitted so far) helps.

Do NOT assume MFS is a wall. MFS is right only on the DOMINANT-sense cases; the brain's edge is the subordinate
cases. This cell isolates them:
  SUBORDINATE population = test items where gold_frame != per-lemma-MFS(train). MFS scores 0 there BY DEFINITION.
  Question: what fraction does each arm RECOVER? And on the FULL population, does an arm BEAT MFS (McNemar c>b)?

ARMS (binary confusion, curated + auto, same as the bakeoff):
  MFS          per-lemma most-frequent sense (the floor).
  DISAMBIG     construction + idiom + supersense-fit (the current winner).
  +GROUNDED    swap the supersense-count fit for a GROUNDED per-frame centroid fit (meaning-hub, more brain-faithful).
  +CONTEXT     add a distributional CONTEXT cue: the sentence's content words vote for each frame via their
               grounded similarity to that frame's object/subject centroid (reordered access -- context primes sense).

Reads cached v4 SemCor instances (they carry the full RealizedFrame + we re-derive context from the cached sent
is NOT stored, so CONTEXT uses the dobj/subject + any pobj already in the frame as a minimal context proxy).
Writes data/exp_frame_sense_subordinate_recovery_v1/. ASCII. NO hdlab writes.
"""
from __future__ import annotations
import json, math, os, pickle, sys, time
from collections import defaultdict
from datetime import datetime, timezone
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from experiments.frame_sense_disambiguator import FrameSenseDisambiguator, candidate_frames
from experiments.exp_frame_sense_confusion_pairs_v1 import MD_VERBS, PROP_VERBS, PROP, _FakeTok
from hdlab.grounded_similarity import grounded_vector as _GV

CACHE = os.path.join(REPO, "data", "exp_frame_sense_semcor_v1", "instances_v6.pkl")


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na > 0 and nb > 0 else 0.0


def build_grounded_centroids(insts):
    """frame -> centroid of grounded_vector(dobj) over training instances (>=8) with a typed object."""
    byf = defaultdict(list)
    for it in insts:
        if not it["train"]:
            continue
        d = it["rf"].dobj_head
        if d and it["rf"].dobj_types != {}:
            v = _GV(d)
            if v is not None:
                byf[it["gold_frame"]].append(np.asarray(v, float))
    return {f: np.mean(vs, 0) for f, vs in byf.items() if len(vs) >= 8}


def grounded_fit(cent, frame, obj):
    v = _GV(obj) if obj else None
    if v is None or frame not in cent:
        return 0.0
    return _cos(np.asarray(v, float), cent[frame])


def context_vote(cent, frame, rf):
    """CONTEXT cue proxy: the frame whose object-centroid best matches the realized argument words present in the
    cached frame (dobj + pobj + subject head). A minimal reordered-access signal from the local content words."""
    words = [w for w in (rf.dobj_head, rf.pobj_head) if w]
    if frame not in cent or not words:
        return 0.0
    sims = [grounded_fit(cent, frame, w) for w in words]
    return float(np.mean(sims)) if sims else 0.0


def zscore_over(cands, fn):
    vals = np.array([fn(c) for c in cands], float)
    if vals.std() < 1e-9:
        return {c: 0.0 for c in cands}
    z = (vals - vals.mean()) / (vals.std() + 1e-9)
    return {c: float(z[i]) for i, c in enumerate(cands)}


def run():
    t0 = time.time()
    insts, _ = pickle.load(open(CACHE, "rb"))
    cent = build_grounded_centroids(insts)
    dis = FrameSenseDisambiguator(nlp="cached")                 # +BOTH default (idiom + supersense fit)
    out = {"grounded_frames": sorted(cent.keys()), "pops": {}}
    for which, verbs in (("motion", MD_VERBS), ("prop", PROP_VERBS)):
        target_is = (lambda f: f == "motion") if which == "motion" else (lambda f: f in PROP)
        for curated in (True, False):
            if curated:
                sub = [it for it in insts if it["lemma"] in verbs
                       and (set(it["cands"]) & ({"motion"} if which == "motion" else PROP))]
            else:
                from experiments.frame_sense_disambiguator import verb_confusions
                fam = "md" if which == "motion" else "prop"
                sub = [it for it in insts if fam in verb_confusions(it["cands"])
                       and (set(it["cands"]) & ({"motion"} if which == "motion" else PROP))]
            train = [it for it in sub if it["train"]]
            test = [it for it in sub if not it["train"]]
            # COARSE train prior per lemma (the SAME prior injected into the disambiguator AND used for the MFS
            # floor -> a clean one-variable test: the ONLY difference between DISAMBIG and MFS is the cues, not a
            # WordNet-vs-corpus prior mismatch).
            cpri = defaultdict(lambda: defaultdict(float))
            for it in train:
                cpri[it["lemma"]][it["gold_frame"]] += 1.0
            cpri = {lm: dict(d) for lm, d in cpri.items()}

            def mfs_pred(it):
                d = cpri.get(it["lemma"], {})
                if not d:
                    return target_is(it["cands"][0])
                return target_is(max(it["cands"], key=lambda c: d.get(c, 0.0)))

            rows = {"MFS": [], "DISAMBIG": [], "GROUNDED": [], "CONTEXT": []}
            gold = []
            for it in test:
                g = target_is(it["gold_frame"]); gold.append(g)
                cands = it["cands"]
                rows["MFS"].append(mfs_pred(it))
                pri = cpri.get(it["lemma"]) or None
                v = dis.disambiguate_token(None, _FakeTok(it["lemma"]), cand=cands, frame_feats=it["rf"],
                                           joint=True, prior=pri)
                rows["DISAMBIG"].append(target_is(v.frame))
                # GROUNDED: replace fit with grounded centroid fit; re-pick argmax among prior+constr+groundedfit
                gz = zscore_over(cands, lambda f: grounded_fit(cent, f, it["rf"].dobj_head))
                cz = zscore_over(cands, lambda f: context_vote(cent, f, it["rf"]))
                base = {c: v.p.get(c, 0.0) for c in cands}       # the +BOTH posterior as the base
                gpick = max(cands, key=lambda c: base[c] + 0.5 * gz[c])
                cpick = max(cands, key=lambda c: base[c] + 0.5 * cz[c])
                rows["GROUNDED"].append(target_is(gpick))
                rows["CONTEXT"].append(target_is(cpick))
            gold = np.array(gold)
            n = len(gold)
            # subordinate population: MFS wrong
            mfs = np.array(rows["MFS"])
            subord = mfs != gold
            res = {"n": n, "n_subordinate": int(subord.sum()), "pct_subordinate": float(subord.mean())}
            for arm in rows:
                p = np.array(rows[arm])
                acc = float((p == gold).mean())
                rec = float((p[subord] == gold[subord]).mean()) if subord.sum() else 0.0
                b = int(((mfs == gold) & (p != gold)).sum())     # MFS right, arm wrong
                c = int(((mfs != gold) & (p == gold)).sum())     # MFS wrong, arm right (recovery)
                nn = b + c
                pmc = min(1.0, sum(math.comb(nn, i) for i in range(min(b, c) + 1)) * 0.5 ** nn * 2) if nn else 1.0
                res[arm] = {"acc": round(acc, 3), "subord_recovery": round(rec, 3),
                            "mcnemar_b_mfsonly": b, "mcnemar_c_armonly": c, "mcnemar_p": round(pmc, 4)}
            out["pops"][f"{which}_{'curated' if curated else 'auto'}"] = res
    out["elapsed_s"] = round(time.time() - t0, 1)
    return out


def main():
    od = os.path.join(REPO, "data", "exp_frame_sense_subordinate_recovery_v1")
    os.makedirs(od, exist_ok=True)
    m = run()
    json.dump(m, open(os.path.join(od, "metrics.json.tmp"), "w", encoding="ascii"), indent=2)
    os.replace(os.path.join(od, "metrics.json.tmp"), os.path.join(od, "metrics.json"))
    print(f"=== subordinate_recovery {m['elapsed_s']}s  grounded_frames={len(m['grounded_frames'])} ===")
    for pop, r in m["pops"].items():
        print(f"\n[{pop}] n={r['n']}  subordinate(MFS-wrong)={r['n_subordinate']} ({r['pct_subordinate']:.2f})")
        print(f"    {'arm':10s} {'acc':>6s} {'sub_recovery':>13s}  McNemar(b=MFSonly,c=ARMonly,p)")
        for arm in ("MFS", "DISAMBIG", "GROUNDED", "CONTEXT"):
            a = r[arm]
            print(f"    {arm:10s} {a['acc']:6.3f} {a['subord_recovery']:13.3f}  b={a['mcnemar_b_mfsonly']} c={a['mcnemar_c_armonly']} p={a['mcnemar_p']:.3f}")
    print("\nwrote", od)


if __name__ == "__main__":
    main()
