"""exp_frame_sense_context2_v1 -- tests #2 (CROSS-SENTENCE discourse context) and #3a (COREF for anaphoric
objects) on the v6 cache, fair (matched train-MFS prior, context learned on TRAIN only, scored on TEST).

Single-sentence context recovered only ~40% of subordinate senses (measured ceiling). The brain's reordered
access uses the WHOLE prior discourse -- so a wider context window (ctx_wide = prior 2 sentences + current)
should recover more. And a pronoun object ('she left it') is uninformative until COREF resolves it -- so typing
the resolved antecedent should recover the object-type cue the disambiguator otherwise defers on.

ARMS (motion/prop x curated/auto): MFS | CTX (single sentence) | CTX_WIDE (cross-sentence) | CTX_WIDE+CONSTR
(the full combination) | CTX_WIDE+CONSTR+COREF (also resolve pronoun objects). Decisive metric: OVERRIDE
PRECISION c/(b+c) on the subordinate (MFS-wrong) cases. Writes data/exp_frame_sense_context2_v1/. ASCII. No hdlab.
"""
from __future__ import annotations
import copy, json, math, os, pickle, sys, time
from collections import defaultdict
from datetime import datetime, timezone
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from experiments.frame_sense_disambiguator import FrameSenseDisambiguator, verb_confusions, noun_frame_types
from experiments.exp_frame_sense_confusion_pairs_v1 import MD_VERBS, PROP_VERBS, PROP, _FakeTok
from experiments.exp_frame_sense_context_v1 import context_scores, mcnemar_p

CACHE = os.path.join(REPO, "data", "exp_frame_sense_semcor_v1", "instances_v6.pkl")
W = 3.0


def learn_ctx(train, field):
    wf = defaultdict(lambda: defaultdict(float)); ftot = defaultdict(float); vocab = set()
    for it in train:
        f = it["gold_frame"]
        for w in it.get(field, []):
            wf[f][w] += 1.0; ftot[f] += 1.0; vocab.add(w)
    return {"wf": {f: dict(d) for f, d in wf.items()}, "ftot": dict(ftot), "V": max(1, len(vocab))}


def coref_rf(it):
    """Return a copy of the RealizedFrame with a pronoun object replaced by its resolved antecedent's typing."""
    rf = it["rf"]
    if not it.get("dobj_coref") or (rf.dobj_types and rf.dobj_head):
        return rf
    rf2 = copy.copy(rf)
    rf2.dobj_head = it["dobj_coref"]
    rf2.dobj_types = noun_frame_types(it["dobj_coref"])
    return rf2


def eval_pop(insts, which, curated):
    tis = (lambda f: f == "motion") if which == "motion" else (lambda f: f in PROP)
    keyset = {"motion"} if which == "motion" else PROP
    fam = "md" if which == "motion" else "prop"
    if curated:
        verbs = MD_VERBS if which == "motion" else PROP_VERBS
        sub = [it for it in insts if it["lemma"] in verbs and (set(it["cands"]) & keyset)]
    else:
        sub = [it for it in insts if fam in verb_confusions(it["cands"]) and (set(it["cands"]) & keyset)]
    train = [it for it in sub if it["train"]]; test = [it for it in sub if not it["train"]]
    cpri = defaultdict(lambda: defaultdict(float))
    for it in train:
        cpri[it["lemma"]][it["gold_frame"]] += 1.0
    m_ctx = learn_ctx(train, "ctx"); m_wide = learn_ctx(train, "ctx_wide")
    dis = FrameSenseDisambiguator(nlp="cached", context_weight=W)

    def mfs(it):
        d = cpri.get(it["lemma"], {}); return tis(max(it["cands"], key=lambda c: d.get(c, 0.0))) if d else tis(it["cands"][0])
    arms = {k: [] for k in ("MFS", "CTX", "CTX_WIDE", "WIDE_CONSTR", "WIDE_CONSTR_COREF")}
    gold = []
    for it in test:
        gold.append(tis(it["gold_frame"])); cands = it["cands"]; pri = cpri.get(it["lemma"]) or None
        pa = {c: (pri or {}).get(c, 0.0) for c in cands}
        arms["MFS"].append(mfs(it))
        cz = context_scores(m_ctx, cands, it.get("ctx", []))
        wz = context_scores(m_wide, cands, it.get("ctx_wide", []))
        arms["CTX"].append(tis(max(cands, key=lambda c: pa[c] + W * cz[c])))
        arms["CTX_WIDE"].append(tis(max(cands, key=lambda c: pa[c] + W * wz[c])))
        v = dis.disambiguate_token(None, _FakeTok(it["lemma"]), cand=cands, frame_feats=it["rf"],
                                   joint=True, prior=pri, context_scores=wz)
        arms["WIDE_CONSTR"].append(tis(v.frame))
        vc = dis.disambiguate_token(None, _FakeTok(it["lemma"]), cand=cands, frame_feats=coref_rf(it),
                                    joint=True, prior=pri, context_scores=wz)
        arms["WIDE_CONSTR_COREF"].append(tis(vc.frame))
    gold = np.array(gold); mfsp = np.array(arms["MFS"]); subord = mfsp != gold
    out = {"n": len(gold), "n_subordinate": int(subord.sum())}
    for k in arms:
        p = np.array(arms[k])
        b = int(((mfsp == gold) & (p != gold)).sum()); c = int(((mfsp != gold) & (p == gold)).sum())
        out[k] = {"acc": round(float((p == gold).mean()), 3),
                  "subord_rec": round(float((p[subord] == gold[subord]).mean()) if subord.sum() else 0.0, 3),
                  "ovr_prec": round(c / (b + c), 3) if (b + c) else None, "b": b, "c": c,
                  "mcnemar_p": round(mcnemar_p(b, c), 4)}
    return out


def run():
    t0 = time.time()
    insts, _ = pickle.load(open(CACHE, "rb"))
    pops = {f"{w}_{'cur' if c else 'auto'}": eval_pop(insts, w, c)
            for w in ("motion", "prop") for c in (True, False)}
    return {"anchor_name": "frame_sense_context2_v1", "pops": pops,
            "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}


def main():
    od = os.path.join(REPO, "data", "exp_frame_sense_context2_v1"); os.makedirs(od, exist_ok=True)
    m = run()
    json.dump(m, open(os.path.join(od, "metrics.json.tmp"), "w", encoding="ascii"), indent=2)
    os.replace(os.path.join(od, "metrics.json.tmp"), os.path.join(od, "metrics.json"))
    print(f"=== frame_sense_context2_v1 {m['elapsed_s']}s (#2 cross-sentence + #3a coref) ===")
    for pop, r in m["pops"].items():
        print(f"\n[{pop}] n={r['n']} subord={r['n_subordinate']}")
        print(f"    {'arm':20s} {'acc':>6s} {'sub_rec':>8s} {'ovr_prec':>9s}  (b,c,p)")
        for k in ("MFS", "CTX", "CTX_WIDE", "WIDE_CONSTR", "WIDE_CONSTR_COREF"):
            a = r[k]
            beat = "  <== beats MFS" if (a["c"] > a["b"] and a["mcnemar_p"] < 0.05) else ""
            print(f"    {k:20s} {a['acc']:6.3f} {a['subord_rec']:8.3f} {str(a['ovr_prec']):>9s}  "
                  f"b={a['b']} c={a['c']} p={a['mcnemar_p']:.3f}{beat}")
    print("\nwrote", od)


if __name__ == "__main__":
    main()
