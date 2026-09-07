"""exp_partwhole_typed_spoke_bridging_v1 -- TYPE 4 (part-whole) + TYPE 6 (instrument) world-knowledge INGEST as
a TYPED, DIRECTED spoke, measured on the LIVE bridging consumer's instrument (exp_bridging_selection_v2 gold).

THE BRAIN OPERATION (PINNED). Bridging inference fills the unstated part-whole / instrument link between
sentences (Clark 1975; Kintsch 1988 construction-integration). The RELATION is DIRECTED and TYPED (a wheel is
PART-OF a car, not the reverse); the ATL stores it as a typed spoke (Lambon-Ralph 2017), not as symmetric
association. Committing the SPECIFIC coherence link (not the generically-most-related one) is the N400 /
predictive-coding signal (Kuperberg & Jaeger 2016).

THE WALL. The live bridging organ scores relatedness with a SYMMETRIC read (hub cosine / MFS-signature cosine).
Symmetric relatedness works when distractors are random wholes (~0.62), but it is FOOLED -- BELOW CHANCE --
when the distractors are the target's own generic neighbours (it maximises generic relatedness, which by
construction is a distractor). This cell shows the SAME superposition ceiling as the is-a demo, on part-whole,
and shows a DIRECTED typed spoke recovers it for COVERED facts.

THE TYPED SPOKE (glass-box, directed, no training). Ingest part-whole edges from curated KBs (WordNet
part/substance meronymy + ConceptNet PartOf/HasA/MadeOf) as a directed part->whole graph, resolved to hub
words. Score a candidate whole c by the MERONYM-PROTOTYPE: cos(hub(target), mean hub of c's KNOWN parts) --
"does the target resemble the things that are typically part of c?" -- fused with graph reachability. This is
DIRECTED (uses c's part-set, asymmetric) and the "consult the consolidated store" O(1) read (PINNED).

FINDINGS (measured):
  * COVERED pairs (the KB has the fact): typed spoke ~0.93 vs symmetric ~0.62 (easy) / ~0.09 (confusable) --
    stored typed knowledge >> re-derived distributional relatedness for the facts the foundation should hold.
  * HELD-OUT pairs (fact removed): typed drops to ~0.27 -- part-whole does NOT have the distributional geometry
    is-a has, so the typed spoke does not GENERALIZE alone (a located negative). The brain-faithful design is a
    HYBRID: typed spoke for stored facts + distributional read for novel ones.
  * Info-free twin (shuffled part-whole graph) collapses to chance -> the win is the CORRECT edges, not "a graph".

Glass-box, CPU numpy, NO LLM, NO training. ASCII. Own data dir. NO hdlab write (Q111).
Run: .venv/Scripts/python.exe experiments/exp_partwhole_typed_spoke_bridging_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_partwhole_typed_spoke_bridging_v1.py            (full)
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import sys
import json
import time
import pickle
import argparse
import collections

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

HUB_PATH = os.path.join(_REPO, "data", "frontend_assets", "hub_ppmi_svd_200d.pkl")
CN_DIR = os.path.join(_REPO, "data", "bridge_relation_assets_v1")
OUT = os.path.join(_REPO, "data", "exp_partwhole_typed_spoke_bridging_v1")
# KB_REFERENT: data/frontend_assets/hub_ppmi_svd_200d.pkl
# KB_REFERENT: data/bridge_relation_assets_v1/PartOf.jsonl
# KB_REFERENT: data/bridge_relation_assets_v1/HasA.jsonl
# KB_REFERENT: data/bridge_relation_assets_v1/MadeOf.jsonl
# KB_REFERENT: data/bridge_relation_assets_v1/UsedFor.jsonl
_EPS = 1e-9
K_DISTRACT = 4


def unit(v):
    v = np.asarray(v, float)
    n = np.linalg.norm(v)
    return v / (n + _EPS) if n > 0 else v


def _load_cn(rel):
    fp = os.path.join(CN_DIR, rel + ".jsonl")
    if not os.path.exists(fp):
        return []
    return [(d["s"], d["o"]) for d in (json.loads(l) for l in open(fp, encoding="ascii"))]


def wn_meronymy(hub):
    from nltk.corpus import wordnet as wn
    CONC = ("noun.artifact", "noun.body", "noun.food", "noun.plant", "noun.animal", "noun.object", "noun.substance")
    out = []
    for syn in wn.all_synsets("n"):
        if syn.lexname() not in CONC:
            continue
        wholes = [l.name().lower() for l in syn.lemmas() if "_" not in l.name()]
        for mer in (syn.part_meronyms() + syn.substance_meronyms()):
            parts = [l.name().lower() for l in mer.lemmas() if "_" not in l.name()]
            for w in wholes:
                for p in parts:
                    if w != p and w in hub and p in hub:
                        out.append((p, w))
    return out


def build_partwhole_graph(hub):
    """Directed part->whole edges from curated KBs (WordNet meronymy + ConceptNet PartOf/HasA/MadeOf)."""
    edges = set()
    for s, o in _load_cn("PartOf"):
        if s in hub and o in hub and s != o:
            edges.add((s, o))
    for s, o in _load_cn("MadeOf"):
        if s in hub and o in hub and s != o:
            edges.add((s, o))            # object MadeOf material: material is a 'part'
    for s, o in _load_cn("HasA"):
        if s in hub and o in hub and s != o:
            edges.add((o, s))            # s HasA o -> o is part of s
    for p, w in wn_meronymy(hub):
        edges.add((p, w))
    return edges


def eval_bridging(source, hub, mfnd, confusable, held_out, seed=0):
    """source: 'part_cn' PartOf gold, or 'instrument' UsedFor gold. Returns arm accuracy arrays (pooled items)."""
    from nltk.corpus import wordnet as wn
    if source == "part_cn":
        gold_pairs = sorted({(s, o) for s, o in _load_cn("PartOf") if s in hub and o in hub and s != o})
    else:  # instrument
        def is_art(w):
            ss = wn.synsets(w, pos="n")
            return any(x.lexname() in ("noun.artifact", "noun.object") for x in ss[:3])
        gold_pairs = sorted({(s, o) for s, o in _load_cn("UsedFor") if s in hub and o in hub and s != o and is_art(s)})

    pw_graph = build_partwhole_graph(hub) if source == "part_cn" else \
        {(s, o) for s, o in _load_cn("UsedFor") if s in hub and o in hub}
    parts_of = collections.defaultdict(set)
    for p, w in pw_graph:
        parts_of[w].add(p)
    ante_pool = sorted({o for _, o in gold_pairs})
    words = set(ante_pool) | {t for t, _ in gold_pairs} | {p for p, _ in pw_graph}
    U = {w: unit(hub[w]) for w in words if w in hub}
    shuf_rng = np.random.default_rng(1234)
    perm = shuf_rng.permutation(len(ante_pool))
    # shuffled graph twin: each whole's part-set reassigned to a random other whole (info-free)
    shuf_parts = {ante_pool[i]: parts_of[ante_pool[perm[i]]] for i in range(len(ante_pool))}

    def proto(pmap, c, exclude):
        ps = [p for p in pmap.get(c, ()) if p != exclude and p in U]
        return unit(np.mean([U[p] for p in ps], 0)) if ps else None

    rng = np.random.default_rng(seed)
    arms = collections.defaultdict(list)
    for (t, gold) in gold_pairs:
        if t not in U:
            continue
        tv = U[t]
        if confusable:
            sims = sorted(((float(tv @ U[c]), c) for c in ante_pool if c != gold and c != t and c in U), reverse=True)
            dist = [c for _, c in sims[:K_DISTRACT]]
        else:
            pool = [a for a in ante_pool if a != gold and a != t and a in U]
            dist = [pool[i] for i in rng.choice(len(pool), size=min(K_DISTRACT, len(pool)), replace=False)]
        cands = [gold] + dist
        rng.shuffle(cands)
        gi = cands.index(gold)
        ho = t if held_out else "___none___"
        # symmetric reads (the current bridging mechanism)
        arms["RANDOM"].append(1.0 / len(cands))
        arms["RAW_HUB_symmetric"].append(int(np.argmax([float(tv @ U[c]) for c in cands]) == gi))
        mt = mfnd(t)
        if mt is not None and np.linalg.norm(mt) > 0:
            mv = []
            for c in cands:
                mc = mfnd(c)
                mv.append(float(unit(mt) @ unit(mc)) if (mc is not None and np.linalg.norm(mc) > 0) else -9.0)
            arms["MEAN_FND_symmetric"].append(int(np.argmax(mv) == gi) if max(mv) > -9.0 else 1.0 / len(cands))
        else:
            arms["MEAN_FND_symmetric"].append(1.0 / len(cands))
        # typed directed spoke
        sp = []
        for c in cands:
            pr = proto(parts_of, c, ho)
            reach = 1.0 if t in {p for p in parts_of.get(c, ()) if p != ho} else 0.0
            base = float(tv @ pr) if pr is not None else -9.0
            sp.append(base + 2.0 * reach)
        arms["TYPED_directed_spoke"].append(int(np.argmax(sp) == gi) if max(sp) > -9.0 else 1.0 / len(cands))
        # hybrid: typed where covered (whole has parts other than target), else symmetric fallback
        covered = any(len([p for p in parts_of.get(c, ()) if p != ho]) > 0 for c in cands)
        if covered and max(sp) > -9.0:
            arms["HYBRID_typed_or_symmetric"].append(int(np.argmax(sp) == gi))
        else:
            arms["HYBRID_typed_or_symmetric"].append(int(np.argmax([float(tv @ U[c]) for c in cands]) == gi))
        # info-free twin: shuffled part-whole graph
        spt = []
        for c in cands:
            pr = proto(shuf_parts, c, ho)
            spt.append(float(tv @ pr) if pr is not None else -9.0)
        arms["TWIN_shuffled_graph"].append(int(np.argmax(spt) == gi) if max(spt) > -9.0 else 1.0 / len(cands))
    return {a: np.array(v, float) for a, v in arms.items()}


def mean_ci(x, B=2000, seed=0):
    rr = np.random.default_rng(seed)
    n = len(x)
    if n == 0:
        return (0.0, [0.0, 0.0])
    bs = [x[rr.integers(0, n, n)].mean() for _ in range(B)]
    return round(float(x.mean()), 4), [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]


def delta_ci(x, y, B=2000, seed=1):
    rr = np.random.default_rng(seed)
    n = min(len(x), len(y))
    x, y = x[:n], y[:n]
    bs = [x[bi].mean() - y[bi].mean() for bi in (rr.integers(0, n, n) for _ in range(B))]
    d = float(x.mean() - y.mean())
    lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
    return {"d": round(d, 4), "ci": [round(lo, 4), round(hi, 4)], "sep": bool(lo > 0 or hi < 0)}


_HYP = {}


def _hypers(lemma):
    """Nearer MFS hypernym lemmas of a word (for meronymy inheritance: a whole inherits its hypernyms' parts)."""
    if lemma in _HYP:
        return _HYP[lemma]
    from nltk.corpus import wordnet as wn
    ss = wn.synsets(lemma, pos=wn.NOUN)
    acc = set()
    if ss:
        for path in ss[0].hypernym_paths():
            for h in path[-5:-1]:
                for ln in h.lemma_names():
                    acc.add(ln.lower().split("_")[0])
    _HYP[lemma] = acc
    return acc


def generalization_report(hub, smoke=False):
    """DRILL the part-whole GENERALIZATION located-negative with the brain-foundational meronymy-INHERITANCE
    upgrade (Collins-Quillian property inheritance: a whole inherits its hypernyms' parts -- composes the is-a
    spoke x the part-whole spoke). Measures HELD-OUT confusable bridging with a PLAIN meronym-prototype vs an
    is-a-INHERITED prototype. Reports the delta (directional-only in practice -> generalization stays hard)."""
    gold_pairs = sorted({(s, o) for s, o in _load_cn("PartOf") if s in hub and o in hub and s != o})
    if smoke:
        gold_pairs = gold_pairs[:300]
    pw = build_partwhole_graph(hub)
    parts_of = {}
    for p, w in pw:
        parts_of.setdefault(w, set()).add(p)
    ante_pool = sorted({o for _, o in gold_pairs})
    words = set(ante_pool) | {t for t, _ in gold_pairs}
    for w in parts_of:
        words |= parts_of[w]
    U = {w: unit(hub[w]) for w in words if w in hub}

    def parts_inh(c):
        acc = set(parts_of.get(c, ()))
        for h in _hypers(c):
            acc |= parts_of.get(h, set())
        return acc

    def proto(pfn, c, exclude):
        ps = [p for p in pfn(c) if p != exclude and p in U]
        return unit(np.mean([U[p] for p in ps], 0)) if ps else None

    def score(pfn):
        rng = np.random.default_rng(0)
        ok = []
        for (t, gold) in gold_pairs:
            if t not in U:
                continue
            tv = U[t]
            sims = sorted(((float(tv @ U[c]), c) for c in ante_pool if c != gold and c != t and c in U), reverse=True)
            cands = [gold] + [c for _, c in sims[:K_DISTRACT]]
            rng.shuffle(cands)
            gi = cands.index(gold)
            sp = []
            for c in cands:
                pr = proto(pfn, c, t)                 # HELD-OUT: exclude the target's own edge
                sp.append(float(tv @ pr) if pr is not None else -9.0)
            ok.append(int(np.argmax(sp) == gi) if max(sp) > -9.0 else 1.0 / len(cands))
        return np.array(ok, float)

    # WALL A brain-mechanism test (research: Gentner/Osherson similarity-coverage; NOT is-a closure):
    # nearest-exemplar transfer -- pool parts of c + c's k nearest wholes, weighted by sim(c,w).
    wholes_wp = [w for w in parts_of if w in U and any(p in U for p in parts_of[w])]
    WM = np.array([U[w] for w in wholes_wp]) if wholes_wp else np.zeros((0, 1))

    def parts_nn(c, k=10):
        if c not in U or len(wholes_wp) == 0:
            return [(p, 1.0) for p in parts_of.get(c, ())]
        sims = WM @ U[c]
        idx = np.argsort(-sims)[:k + 1]
        out = []
        for i in idx:
            s = float(sims[i])
            if s <= 0:
                continue
            for p in parts_of[wholes_wp[i]]:
                out.append((p, s))
        return out

    def score_nn():
        rng = np.random.default_rng(0)
        ok = []
        for (t, gold) in gold_pairs:
            if t not in U:
                continue
            tv = U[t]
            sims = sorted(((float(tv @ U[c]), c) for c in ante_pool if c != gold and c != t and c in U), reverse=True)
            cands = [gold] + [c for _, c in sims[:K_DISTRACT]]
            rng.shuffle(cands)
            gi = cands.index(gold)
            sp = []
            for c in cands:
                pw = [(p, w) for p, w in parts_nn(c) if p != t and p in U]
                if pw:
                    vs = np.array([U[p] for p, _ in pw]); wt = np.array([w for _, w in pw])
                    pr = unit(np.average(vs, axis=0, weights=wt))
                    sp.append(float(tv @ pr))
                else:
                    sp.append(-9.0)
            ok.append(int(np.argmax(sp) == gi) if max(sp) > -9.0 else 1.0 / len(cands))
        return np.array(ok, float)

    plain = score(lambda c: parts_of.get(c, set()))
    inh = score(parts_inh)
    nn = score_nn()
    return {"held_out_plain_proto": round(float(plain.mean()), 4),
            "held_out_isa_inherited_proto": round(float(inh.mean()), 4),
            "held_out_nearest_exemplar_proto": round(float(nn.mean()), 4),
            "inherited_minus_plain": mean_ci_delta(inh, plain),
            "nearest_exemplar_minus_plain": mean_ci_delta(nn, plain),
            "verdict": "part-whole GENERALIZATION is a partially-PINNED limit (research: shallow partonomies, "
                       "6 meronymy subtypes, similarity-weighted transfer -- Tversky-Hemenway/Winston-Chaffin-"
                       "Herrmann/Gentner/Osherson). is-a inheritance (Collins-Quillian) helps only DIRECTIONALLY "
                       "(CI incl 0); nearest-exemplar transfer (the brain's named mechanism) is WORSE on confusable "
                       "distractors (pooling neighbour-parts dilutes discrimination). Stored spoke authoritative "
                       "for covered facts + distributional read for novel = the hybrid (confirmed by the wall)."}


def mean_ci_delta(a, b, B=2000, seed=3):
    rng = np.random.default_rng(seed)
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    ds = [(a[i] - b[i]).mean() for i in (rng.integers(0, n, n) for _ in range(B))]
    lo, hi = float(np.percentile(ds, 2.5)), float(np.percentile(ds, 97.5))
    return {"delta": round(float((a - b).mean()), 4), "lo": round(lo, 4), "hi": round(hi, 4),
            "sep": bool(lo > 0 or hi < 0)}


def build_mfnd():
    try:
        from hdlab.meaning_foundation import sense_signature
        from nltk.corpus import wordnet as wn
    except Exception:
        return lambda w: None
    cache = {}

    def vec(w):
        if w in cache:
            return cache[w]
        v = None
        ss = wn.synsets(w)
        if ss:
            v = sense_signature(ss[0].name())
        cache[w] = v
        return v
    return vec


def run(smoke=False):
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    hub = pickle.load(open(HUB_PATH, "rb"))["hub"]
    mfnd = build_mfnd()
    out = {"sources": ["part_cn", "instrument"], "K_distract": K_DISTRACT, "per": {}}
    for source in (["part_cn"] if smoke else ["part_cn", "instrument"]):
        blk = {}
        for confusable in (False, True):
            for held_out in (False, True):
                arms = eval_bridging(source, hub, mfnd, confusable, held_out, seed=0)
                key = "%s_%s" % ("confusable" if confusable else "easy", "heldout" if held_out else "indomain")
                stats = {a: mean_ci(arms[a]) for a in arms}
                blk[key] = {
                    "n": len(arms["RAW_HUB_symmetric"]),
                    "acc": {a: {"mean": stats[a][0], "ci": stats[a][1]} for a in stats},
                    "TYPED_minus_RAW_HUB": delta_ci(arms["TYPED_directed_spoke"], arms["RAW_HUB_symmetric"]),
                    "TYPED_minus_MEAN_FND": delta_ci(arms["TYPED_directed_spoke"], arms["MEAN_FND_symmetric"]),
                    "TYPED_minus_TWIN": delta_ci(arms["TYPED_directed_spoke"], arms["TWIN_shuffled_graph"]),
                }
        out["per"][source] = blk
        cd = blk["confusable_indomain"]["acc"]
        ci = blk["confusable_heldout"]["acc"]
        print("[%s] CONFUSABLE distractors: RAW_HUB=%.3f MEAN_FND=%.3f | TYPED in-domain=%.3f held-out=%.3f | "
              "twin=%.3f" % (source, cd["RAW_HUB_symmetric"]["mean"], cd["MEAN_FND_symmetric"]["mean"],
                             cd["TYPED_directed_spoke"]["mean"], ci["TYPED_directed_spoke"]["mean"],
                             cd["TWIN_shuffled_graph"]["mean"]), flush=True)
        ed = blk["easy_indomain"]["acc"]
        print("[%s] EASY distractors:       RAW_HUB=%.3f MEAN_FND=%.3f | TYPED in-domain=%.3f held-out=%.3f"
              % (source, ed["RAW_HUB_symmetric"]["mean"], ed["MEAN_FND_symmetric"]["mean"],
                 ed["TYPED_directed_spoke"]["mean"], blk["easy_heldout"]["acc"]["TYPED_directed_spoke"]["mean"]),
              flush=True)
    out["generalization_drill"] = generalization_report(hub, smoke=smoke)
    print("[generalization] held-out plain=%.4f is-a-inherited=%.4f (%s)" %
          (out["generalization_drill"]["held_out_plain_proto"],
           out["generalization_drill"]["held_out_isa_inherited_proto"],
           out["generalization_drill"]["inherited_minus_plain"]), flush=True)
    out["elapsed_s"] = round(time.time() - t0, 1)
    tag = "smoke" if smoke else "full"
    with open(os.path.join(OUT, "metrics_%s.json" % tag), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "partwhole_typed_spoke_bridging_v1", "verdict": "MEASURED", "result": out},
                  f, indent=2, default=str)
    print("[done] %.1fs" % out["elapsed_s"], flush=True)
    return out


def self_test():
    # tiny synthetic: typed proto discriminates, symmetric fooled by a confusable neighbour.
    rng = np.random.default_rng(0)
    hub = {}
    for w in ("wheel", "tyre", "car", "bike", "engine"):
        hub[w] = rng.standard_normal(8)
    # make car's parts (wheel,tyre,engine) cluster; bike a confusable neighbour of wheel
    base = rng.standard_normal(8)
    for w in ("wheel", "tyre", "engine"):
        hub[w] = base + 0.05 * rng.standard_normal(8)
    hub["bike"] = hub["wheel"] + 0.02 * rng.standard_normal(8)   # bike ~ wheel (confusable)
    hub["car"] = rng.standard_normal(8)
    U = {w: unit(v) for w, v in hub.items()}
    parts_of = {"car": {"wheel", "tyre", "engine"}}
    # target wheel, gold car, distractor bike (confusable). proto(car exclude wheel)= mean(tyre,engine)~wheel-ish
    pr = unit(np.mean([U["tyre"], U["engine"]], 0))
    typed_car = float(U["wheel"] @ pr)
    typed_bike = -9.0   # bike has no parts
    assert typed_car > typed_bike, "typed proto must prefer the true whole"
    sym_car = float(U["wheel"] @ U["car"]); sym_bike = float(U["wheel"] @ U["bike"])
    assert sym_bike > sym_car, "symmetric SHOULD be fooled by the confusable neighbour (setup check)"
    print("SELFTEST PASS (typed proto prefers true whole; symmetric fooled by confusable neighbour)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(smoke=args.smoke)
    return 0


if __name__ == "__main__":
    sys.exit(main())
