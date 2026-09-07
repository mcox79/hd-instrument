"""exp_isa_spoke_commonnoun_coref_gum_v1 -- BUILD ACROSS THE COMMON-NOUN COREF WALL with the admissible
offline-gated WORLD-KNOWLEDGE typed spoke (is-a + part-whole/synonym), on GUM (modern, independent of WordNet).

THE WALL (located + quantified by exp_commonnoun_wall_gum_v1, REUSED + CREDITED, NOT redone): on GUM, unified
common-noun resolution does not beat blind head-identity; anaphoric common-noun mentions decompose into
same_head 0.647 (blind resolves), name_bridge 0.101 (in-text is-a covers only 0.191; 0.809 "needs WORLD
KNOWLEDGE -- the no-LLM limit"), variant 0.252 (720 cases: different-head common antecedents -- "the paintings ...
the collection", "a dog ... the animal" -- also need world knowledge). That cell restricted itself to IN-TEXT
is-a (no world knowledge) and left the remainder as the no-LLM limit.

THE BRIEF'S POINT: OFFLINE-gated world knowledge in the frozen typed store is ADMISSIBLE and brain-foundational
(systems consolidation), NOT the barred inference-time LLM. So the typed is-a/part-whole SPOKE (this problem's
deliverable) is exactly the admissible world-knowledge the wall cell said was needed but out of scope. Here we
add a WK-spoke resolution path to the SAME instrument and measure whether it links the variant/world-knowledge
common-noun anaphora that blind head-identity and in-text is-a cannot.

THE BRAIN OPERATION (PINNED). Coreference by a common-noun anaphor to a lexically-different antecedent uses
semantic-memory type knowledge: "the animal" resumes "a dog" because dog IS-A animal; "the collection" resumes
"the paintings" via a whole/member relation (Sanford-Garrod scenario binding; Lambon-Ralph ATL typed spokes).
This is DIRECTED/TYPED knowledge a symmetric relatedness read approximates poorly.

ARMS (per-doc hit/tot over anaphoric common-noun mentions; select an antecedent eid):
  BLIND        most-recent prior SAME-HEAD common referent (the prior floor 0.6119; == the reader today)
  RECENCY_WK   BLIND, else most-recent prior common referent of ANY head (recency-only, no knowledge)
  SYM_REL      BLIND, else prior common referent whose head is most DISTRIBUTIONALLY similar (hub cosine) --
               the symmetric-relatedness baseline (generic relatedness, not typed)
  WK_SPOKE     BLIND, else most-recent prior common referent whose head is IS-A / PART-WHOLE / SYNONYM related to
               the anaphor head via the typed spoke (WordNet MFS closure both directions + meronymy + synonymy)
  TWIN         WK_SPOKE on a SHUFFLED is-a/part-whole graph (info-free; must collapse toward RECENCY_WK)
Metric = pred_eid == gold eid; item bootstrap CI; reported on ALL anaphoric-common and on the VARIANT subset.
Glass-box, NO external LLM (WordNet + hub). ASCII. Own data dir. NO hdlab write (Q111).
Run: .venv/Scripts/python.exe experiments/exp_isa_spoke_commonnoun_coref_gum_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_isa_spoke_commonnoun_coref_gum_v1.py            (full)
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

import sys
import json
import time
import pickle
import argparse
import random

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.gum_coref as G
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer

OUT_DIR = os.path.join(_REPO, "data", "exp_isa_spoke_commonnoun_coref_gum_v1")
HUB_PATH = os.path.join(_REPO, "data", "frontend_assets", "hub_ppmi_svd_200d.pkl")
# KB_REFERENT: data/frontend_assets/hub_ppmi_svd_200d.pkl

# -------------------------------------------------------------- the typed WORLD-KNOWLEDGE spoke (lemma level)
_ANC = {}
_MERO = {}
_SYN = {}


def _wn():
    from nltk.corpus import wordnet as wn
    return wn


def _anc(lemma):
    """MFS hypernym closure (synset-name set) -- the directed is-a spoke."""
    if lemma in _ANC:
        return _ANC[lemma]
    ss = _wn().synsets(lemma, pos=_wn().NOUN)
    acc = set()
    if ss:
        acc.add(ss[0].name())
        for path in ss[0].hypernym_paths():
            for h in path:
                acc.add(h.name())
    _ANC[lemma] = acc
    return acc


def _synset_names(lemma):
    return {s.name() for s in _wn().synsets(lemma, pos=_wn().NOUN)}


def _mero_holo(lemma):
    """MFS part/member/substance meronyms + holonyms (synset-name set) -- the part-whole spoke."""
    if lemma in _MERO:
        return _MERO[lemma]
    ss = _wn().synsets(lemma, pos=_wn().NOUN)
    acc = set()
    if ss:
        s = ss[0]
        for rel in (s.part_meronyms(), s.substance_meronyms(), s.member_meronyms(),
                    s.part_holonyms(), s.substance_holonyms(), s.member_holonyms()):
            for x in rel:
                acc.add(x.name())
    _MERO[lemma] = acc
    return acc


def wk_related(h_ana, h_ante, anc_fn=_anc, mero_fn=_mero_holo):
    """Typed-spoke relation between an anaphor head and a candidate antecedent head. True if:
    is-a (either direction, via MFS hypernym closure), synonym (shared synset), or part-whole/member."""
    if h_ana == h_ante:
        return False                    # same head is BLIND's job, not the WK spoke's
    a_syn = _synset_names(h_ana)
    b_syn = _synset_names(h_ante)
    if a_syn & b_syn:
        return True                     # synonym / shared sense
    # is-a either direction: antecedent's MFS is an ancestor of anaphor, or vice versa
    if (b_syn & anc_fn(h_ana)) or (a_syn & anc_fn(h_ante)):
        return True
    # part-whole / member either direction
    if (b_syn & mero_fn(h_ana)) or (a_syn & mero_fn(h_ante)):
        return True
    return False


def build_shuffled_spoke(heads, seed=0):
    """Info-free twin: remap each head's closure+meronyms to a RANDOM other head's (destroys correct relations)."""
    heads = sorted(heads)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(heads))
    anc_map = {heads[i]: _anc(heads[perm[i]]) for i in range(len(heads))}
    mero_map = {heads[i]: _mero_holo(heads[perm[i]]) for i in range(len(heads))}
    return (lambda l: anc_map.get(l, set())), (lambda l: mero_map.get(l, set()))


# -------------------------------------------------------------- resolution over one doc
def resolve(doc, mode, hub=None, anc_fn=_anc, mero_fn=_mero_holo):
    """Per-doc (hit, tot, variant_hit, variant_tot) over anaphoric common-noun mentions.
    mode in {'blind','recency_wk','sym_rel','wk_spoke','twin'}."""
    gold_first = {}
    for m in doc.mentions:
        gold_first.setdefault(m.eid, m.order)
    head_ref = {}          # head lemma -> (order, eid) most recent common mention with that head
    prior_common = []      # list of (order, eid, lemma_head) all prior common referents (recency order)
    hit = tot = vhit = vtot = 0
    for m in doc.mentions:
        if m.mtype == "common":
            is_ana = gold_first[m.eid] < m.order
            if is_ana:
                same_head = m.lemma_head in head_ref
                pred = head_ref[m.lemma_head][1] if same_head else None
                if pred is None and mode != "blind":
                    cands = [(o, e, lh) for (o, e, lh) in prior_common if lh != m.lemma_head]
                    if cands:
                        if mode == "recency_wk":
                            pred = max(cands, key=lambda x: x[0])[1]
                        elif mode == "sym_rel" and hub is not None:
                            hv = hub.get(m.lemma_head)
                            if hv is not None:
                                best = None
                                for o, e, lh in cands:
                                    cv = hub.get(lh)
                                    if cv is None:
                                        continue
                                    s = float(hv @ cv)
                                    if best is None or s > best[0]:
                                        best = (s, e)
                                pred = best[1] if best else None
                        elif mode in ("wk_spoke", "twin"):
                            rel = [(o, e) for (o, e, lh) in cands
                                   if wk_related(m.lemma_head, lh, anc_fn=anc_fn, mero_fn=mero_fn)]
                            if rel:
                                pred = max(rel, key=lambda x: x[0])[1]
                hit += int(pred == m.eid)
                tot += 1
                if not same_head:      # the VARIANT/world-knowledge subset (blind cannot resolve)
                    vhit += int(pred == m.eid)
                    vtot += 1
            head_ref[m.lemma_head] = (m.order, m.eid)
            prior_common.append((m.order, m.eid, m.lemma_head))
    return hit, tot, vhit, vtot


def _unit(v):
    v = np.asarray(v, float)
    n = np.linalg.norm(v)
    return v / (n + 1e-9) if n > 0 else v


# -------------------------------------------------------------- OPTIMIZATION probes (located negatives)
_WUP = {}


def _wup(a, b):
    """Wu-Palmer taxonomic similarity of the MFS noun synsets (graded closeness), memoized."""
    if a == b:
        return 1.0
    key = (a, b) if a < b else (b, a)
    if key in _WUP:
        return _WUP[key]
    sa = _wn().synsets(a, pos=_wn().NOUN); sb = _wn().synsets(b, pos=_wn().NOUN)
    v = 0.0
    if sa and sb:
        w = sa[0].wup_similarity(sb[0])
        v = float(w) if w else 0.0
    _WUP[key] = v
    return v


def _load_cn_pairs():
    """Undirected ConceptNet relation set between lemmas (part-whole family) for the broadened-filter probe."""
    rel = set()
    cndir = os.path.join(_REPO, "data", "bridge_relation_assets_v1")
    for r in ("PartOf", "HasA", "UsedFor", "MadeOf"):
        fp = os.path.join(cndir, r + ".jsonl")
        if os.path.exists(fp):
            for ln in open(fp, encoding="ascii"):
                d = json.loads(ln)
                rel.add((d["s"], d["o"])); rel.add((d["o"], d["s"]))
    return rel


_ANCU = {}
_MEROU = {}


def _ancU(l):
    if l in _ANCU:
        return _ANCU[l]
    acc = set()
    for s in _wn().synsets(l, pos=_wn().NOUN):
        acc.add(s.name())
        for p in s.hypernym_paths():
            for h in p:
                acc.add(h.name())
    _ANCU[l] = acc
    return acc


def _meroU(l):
    if l in _MEROU:
        return _MEROU[l]
    acc = set()
    for s in _wn().synsets(l, pos=_wn().NOUN):
        for rel in (s.part_meronyms(), s.substance_meronyms(), s.member_meronyms(),
                    s.part_holonyms(), s.substance_holonyms(), s.member_holonyms()):
            for x in rel:
                acc.add(x.name())
    _MEROU[l] = acc
    return acc


def union_related(a, b):
    """RAW-UNION (unresolved lemma-string key) relatedness: is-a/part-whole/synonym over ALL senses (the
    twin of the MFS-resolved wk_related; over-generates cross-sense links -- the raw-string guard)."""
    if a == b:
        return False
    asyn = {s.name() for s in _wn().synsets(a, pos=_wn().NOUN)}
    bsyn = {s.name() for s in _wn().synsets(b, pos=_wn().NOUN)}
    if asyn & bsyn:
        return True
    if (bsyn & _ancU(a)) or (asyn & _ancU(b)):
        return True
    if (bsyn & _meroU(a)) or (asyn & _meroU(b)):
        return True
    return False


def optimization_report(test):
    """UPGRADE / drill attempts on the validated binary recency+is-a-filter, reported honestly:
    (1) GRADED closeness: among recency-compatible candidates, pick the taxonomically CLOSEST (Wu-Palmer).
    (2) BROADENED licensing: add ConceptNet part-whole relations to the WordNet is-a/part-whole filter.
    (3) RESOLUTION drill (the brief's raw-string guard on a CONTEXT-SENSITIVE consumer): MFS-RESOLVED filter
        vs RAW-UNION (all-senses) filter -- does sense resolution matter in coref?
    Neither (1)(2) beats the binary WordNet filter; (3) is directional only -> recency-primary binary-license
    is at its knee, and the raw-string over-generation cost is small in a recency-dominated consumer."""
    cn = _load_cn_pairs()

    def _score_rel(relfn):
        corr = []
        for doc in test:
            gf = {}
            for m in doc.mentions:
                gf.setdefault(m.eid, m.order)
            hr = {}; prior = []
            for m in doc.mentions:
                if m.mtype == "common":
                    if gf[m.eid] < m.order:
                        same = m.lemma_head in hr
                        pred = hr[m.lemma_head][1] if same else None
                        if pred is None:
                            cands = [(o, e, lh) for o, e, lh in prior if lh != m.lemma_head]
                            rel = [(o, e) for o, e, lh in cands if relfn(m.lemma_head, lh)]
                            if rel:
                                pred = max(rel, key=lambda x: x[0])[1]
                            elif cands:
                                pred = max(cands, key=lambda x: x[0])[1]
                        corr.append(int(pred == m.eid))
                    hr[m.lemma_head] = (m.order, m.eid); prior.append((m.order, m.eid, m.lemma_head))
        return np.array(corr, float)

    def _score(pick_graded, broad):
        corr = []
        for doc in test:
            gf = {}
            for m in doc.mentions:
                gf.setdefault(m.eid, m.order)
            hr = {}; prior = []
            for m in doc.mentions:
                if m.mtype == "common":
                    if gf[m.eid] < m.order:
                        same = m.lemma_head in hr
                        pred = hr[m.lemma_head][1] if same else None
                        if pred is None:
                            cands = [(o, e, lh) for o, e, lh in prior if lh != m.lemma_head]
                            rel = [(o, e, lh) for o, e, lh in cands
                                   if wk_related(m.lemma_head, lh)
                                   or (broad and ((m.lemma_head, lh) in cn))]
                            if rel:
                                if pick_graded:
                                    pred = max(rel, key=lambda x: _wup(m.lemma_head, x[2]))[1]
                                else:
                                    pred = max(rel, key=lambda x: x[0])[1]
                            elif cands:
                                pred = max(cands, key=lambda x: x[0])[1]
                        corr.append(int(pred == m.eid))
                    hr[m.lemma_head] = (m.order, m.eid); prior.append((m.order, m.eid, m.lemma_head))
        return np.array(corr, float)

    binv = _score(False, False)
    grd = _score(True, False)
    brd = _score(False, True)
    res_mfs = _score_rel(wk_related)          # MFS-resolved filter (the resolution drill)
    res_uni = _score_rel(union_related)       # raw-union (unresolved) filter
    return {"binary_wordnet_filter": round(float(binv.mean()), 4),
            "graded_closest": round(float(grd.mean()), 4),
            "broadened_conceptnet": round(float(brd.mean()), 4),
            "resolution_MFS_resolved": round(float(res_mfs.mean()), 4),
            "resolution_RAW_union": round(float(res_uni.mean()), 4),
            "graded_minus_binary": boot_delta(grd, binv),
            "broad_minus_binary": boot_delta(brd, binv),
            "resolved_minus_union": boot_delta(res_mfs, res_uni),
            "verdict": "LOCATED NEGATIVE: neither upgrade beats the binary WordNet is-a/part-whole filter "
                       "(recency-primary + binary type-license is at its knee); the raw-string guard is "
                       "directional only in coref (resolved-union small, CI incl 0 -- recency absorbs the "
                       "over-generation). Remaining headroom (name_bridge common->proper-name) needs an "
                       "ENTITY-TYPE KB (Wikidata P31), not on disk."}


def boot_delta(a, b, B=2000, seed=1):
    """paired per-item delta over pooled 0/1 items (a,b aligned)."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    n = len(a)
    rng = np.random.default_rng(seed)
    ds = [(a[i] - b[i]).mean() for i in (rng.integers(0, n, n) for _ in range(B))]
    lo, hi = float(np.percentile(ds, 2.5)), float(np.percentile(ds, 97.5))
    return {"delta": round(float((a - b).mean()), 4), "lo": round(lo, 4), "hi": round(hi, 4),
            "sep": bool(lo > 0 or hi < 0)}


def _item_vectors(docs, mode, hub=None, anc_fn=_anc, mero_fn=_mero_holo):
    """Per-anaphoric-common-mention 0/1 correctness vector + a variant-mask, pooled across docs (aligned across modes)."""
    correct = []
    variant = []
    for doc in docs:
        gold_first = {}
        for m in doc.mentions:
            gold_first.setdefault(m.eid, m.order)
        head_ref = {}
        prior_common = []
        for m in doc.mentions:
            if m.mtype == "common":
                is_ana = gold_first[m.eid] < m.order
                if is_ana:
                    same_head = m.lemma_head in head_ref
                    pred = head_ref[m.lemma_head][1] if same_head else None
                    if pred is None and mode != "blind":
                        cands = [(o, e, lh) for (o, e, lh) in prior_common if lh != m.lemma_head]
                        if cands:
                            if mode == "recency_wk":
                                pred = max(cands, key=lambda x: x[0])[1]
                            elif mode == "sym_rel" and hub is not None:
                                hv = hub.get(m.lemma_head)
                                best = None
                                if hv is not None:
                                    for o, e, lh in cands:
                                        cv = hub.get(lh)
                                        if cv is None:
                                            continue
                                        s = float(hv @ cv)
                                        if best is None or s > best[0]:
                                            best = (s, e)
                                pred = best[1] if best else None
                            elif mode in ("wk_spoke", "twin"):
                                rel = [(o, e) for (o, e, lh) in cands
                                       if wk_related(m.lemma_head, lh, anc_fn=anc_fn, mero_fn=mero_fn)]
                                if rel:
                                    pred = max(rel, key=lambda x: x[0])[1]
                            elif mode == "recency_isa":
                                # brain-faithful: recency-ranked, TYPE-LICENSED. Prefer the most-recent
                                # is-a/part-whole-compatible antecedent; fall back to pure recency if none.
                                rel = [(o, e) for (o, e, lh) in cands
                                       if wk_related(m.lemma_head, lh, anc_fn=anc_fn, mero_fn=mero_fn)]
                                if rel:
                                    pred = max(rel, key=lambda x: x[0])[1]
                                else:
                                    pred = max(cands, key=lambda x: x[0])[1]
                    correct.append(int(pred == m.eid))
                    variant.append(0 if same_head else 1)
                head_ref[m.lemma_head] = (m.order, m.eid)
                prior_common.append((m.order, m.eid, m.lemma_head))
    return np.array(correct, float), np.array(variant, int)


def run(n_docs=None, smoke=False):
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, limit=(60 if smoke else n_docs), name_gazetteer=gaz)
    test = [d for i, d in enumerate(docs) if i % 2 == 1]      # SAME split as the wall cell
    # unit-normalized hub for the sym_rel baseline
    hubraw = pickle.load(open(HUB_PATH, "rb"))["hub"]
    hub = {w: _unit(v) for w, v in hubraw.items()}
    # shuffled twin over the head vocabulary
    heads = sorted({m.lemma_head for d in test for m in d.mentions if m.mtype == "common"})
    sh_anc, sh_mero = build_shuffled_spoke(heads, seed=0)

    modes = {}
    modes["blind"] = _item_vectors(test, "blind")
    modes["recency_wk"] = _item_vectors(test, "recency_wk")
    modes["sym_rel"] = _item_vectors(test, "sym_rel", hub=hub)
    modes["wk_spoke"] = _item_vectors(test, "wk_spoke")
    modes["recency_isa"] = _item_vectors(test, "recency_isa")
    modes["recency_isa_twin"] = _item_vectors(test, "recency_isa", anc_fn=sh_anc, mero_fn=sh_mero)
    modes["twin"] = _item_vectors(test, "twin", anc_fn=sh_anc, mero_fn=sh_mero)

    corr = {k: v[0] for k, v in modes.items()}
    variant = modes["blind"][1]
    n = len(corr["blind"])
    vmask = variant == 1

    def acc(a, mask=None):
        x = a[mask] if mask is not None else a
        return round(float(x.mean()), 4), int(len(x))

    res = {
        "gold": "GUM OntoGUM coref TEST split (modern, independent of WordNet); anaphoric common-noun mentions",
        "n_anaphoric_common": n, "n_variant": int(vmask.sum()),
        "all": {k: acc(corr[k])[0] for k in corr},
        "variant_subset": {k: acc(corr[k], vmask)[0] for k in corr},
        "margins_all": {
            "wk_spoke_minus_blind": boot_delta(corr["wk_spoke"], corr["blind"]),
            "wk_spoke_minus_recency": boot_delta(corr["wk_spoke"], corr["recency_wk"]),
            "wk_spoke_minus_sym_rel": boot_delta(corr["wk_spoke"], corr["sym_rel"]),
            "wk_spoke_minus_twin": boot_delta(corr["wk_spoke"], corr["twin"]),
            "recency_isa_minus_recency": boot_delta(corr["recency_isa"], corr["recency_wk"]),
            "recency_isa_minus_shuffled_filter_twin": boot_delta(corr["recency_isa"], corr["recency_isa_twin"]),
        },
        "margins_variant": {
            "wk_spoke_minus_recency": boot_delta(corr["wk_spoke"][vmask], corr["recency_wk"][vmask]),
            "wk_spoke_minus_sym_rel": boot_delta(corr["wk_spoke"][vmask], corr["sym_rel"][vmask]),
            "wk_spoke_minus_twin": boot_delta(corr["wk_spoke"][vmask], corr["twin"][vmask]),
        },
        "optimization_attempts": optimization_report(test),
        "elapsed_s": round(time.time() - t0, 1),
    }
    res["headline"] = (
        "COMMON-NOUN COREF (GUM test, n=%d anaphoric-common; variant n=%d). ALL: blind=%.4f recency=%.4f "
        "sym_rel=%.4f WK_SPOKE=%.4f twin=%.4f | WK-blind=%s CIsep=%s ; WK-recency=%s ; WK-twin(loses)=%s. "
        "VARIANT subset: recency=%.4f sym_rel=%.4f WK_SPOKE=%.4f twin=%.4f | WK-recency CIsep=%s WK-twin CIsep=%s"
        % (n, int(vmask.sum()), res["all"]["blind"], res["all"]["recency_wk"], res["all"]["sym_rel"],
           res["all"]["wk_spoke"], res["all"]["twin"], res["margins_all"]["wk_spoke_minus_blind"]["delta"],
           res["margins_all"]["wk_spoke_minus_blind"]["sep"], res["margins_all"]["wk_spoke_minus_recency"]["delta"],
           res["margins_all"]["wk_spoke_minus_twin"]["delta"], res["variant_subset"]["recency_wk"],
           res["variant_subset"]["sym_rel"], res["variant_subset"]["wk_spoke"], res["variant_subset"]["twin"],
           res["margins_variant"]["wk_spoke_minus_recency"]["sep"], res["margins_variant"]["wk_spoke_minus_twin"]["sep"]))
    tag = "smoke" if smoke else "full"
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % tag), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "isa_spoke_commonnoun_coref_gum_v1", "verdict": "MEASURED", "result": res},
                  f, indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    # wk_related: is-a either direction, synonym, part-whole; NOT same head; NOT unrelated.
    assert wk_related("animal", "dog"), "hypernym anaphor <- hyponym antecedent (dog is-a animal)"
    assert wk_related("dog", "animal"), "is-a either direction"
    assert not wk_related("dog", "dog"), "same head is BLIND's job"
    assert not wk_related("dog", "democracy"), "unrelated must be False"
    assert wk_related("car", "vehicle"), "car is-a vehicle"
    print("SELFTEST PASS (wk_related: is-a both directions, same-head excluded, unrelated rejected)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(n_docs=args.n, smoke=args.smoke)
    return 0


if __name__ == "__main__":
    sys.exit(main())
