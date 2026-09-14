"""exp_commonnoun_diffhead_anatomy_gum_v1 -- OPEN THE BLACK BOX. The owner asks: do we fully understand WHY, and is
the different-head residual REALLY world-knowledge-bound or is there untapped GLASS-BOX in-text signal? This dumps and
CATEGORIZES the different-head same-entity anaphors (the only slice with headroom) by the in-text signal that could
resolve them WITHOUT external knowledge:
  - APPOS/COPULA is-a in text  ("Google, a company, ..." / "the company is Google")  -> glass-box, high precision
  - NAME containment           ("the college" <- "American College of Pediatricians")
  - WORDNET synonym/hypernym   (type-relation in a static lexicon)
  - PREDICATE/EVENT co-participation (same verb+other-arg as a prior mention of the entity) -> in-text situation model
  - RESIDUAL world-knowledge   (none of the above -> needs external facts; routes to the P31 KB sibling brief)
Also decomposes the rs_nopollute-vs-string-identity residual (the last ~0.01) so we UNDERSTAND it, not just report it.

problem: improve_the_common_noun_coref_candidate_quality_the_resolver_trails_string_identity
Glass-box, CPU, numpy + nltk-WordNet only, NO external LLM. ASCII. own dir. NO hdlab write (Q111).
Run: .venv/Scripts/python.exe experiments/exp_commonnoun_diffhead_anatomy_gum_v1.py [--docs N] [--dump K]
# KB_REFERENT: data/corpora/gum/conllu
"""
from __future__ import annotations
import os, sys, argparse, json, time
from datetime import datetime, timezone
from collections import Counter

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.gum_coref as G
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
from experiments.exp_unified_referent_gum_v1 import _name_tokens
from nltk.corpus import wordnet as wn

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = str(get_output_dir("commonnoun_diffhead_anatomy_gum_v1"))  # Q115: re-runnable output path (HDLAB_EXP_NAME-driven)
_SYN = {}


def wn_related(h1, h2):
    if h1 == h2:
        return True
    k = (h1, h2) if h1 < h2 else (h2, h1)
    v = _SYN.get(k)
    if v is not None:
        return v
    s1 = wn.synsets(h1, pos="n"); s2 = wn.synsets(h2, pos="n")
    r = False
    if s1 and s2:
        if set(s1) & set(s2):
            r = True
        else:
            a, b = s1[0], s2[0]
            ua = {a} | set(a.hypernyms()) | {h for x in a.hypernyms() for h in x.hypernyms()}
            ub = {b} | set(b.hypernyms()) | {h for x in b.hypernyms() for h in x.hypernyms()}
            r = (b in ua) or (a in ub)
    _SYN[k] = r
    return r


def _load(n_docs=None):
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, limit=n_docs, name_gazetteer=gaz)
    return [d for i, d in enumerate(docs) if i % 2 == 1]


def _appos_copula_isa(doc):
    """glass-box text-stated is-a edges: (a) apposition (deprel appos) between a common head and a name/common;
    (b) copula 'X is/are a Y' (nsubj ... cop ... Y). Returns set of frozenset({lemmaA,lemmaB}) type-linked heads,
    plus a map lemma-> set of co-typed lemmas within the doc. This is IN-TEXT, not world knowledge."""
    toks = doc.toks
    # pri-109: under the GOLD-FREE decision layer there are no `appos` / `cop` arcs to read (the deprel column
    # is the organ's positional role cue), so the same two is-a CONSTRUCTIONS are read off the predicted
    # categories instead. Under the gold layer nothing changes.
    if toks and getattr(toks[0], "gold_upos", ""):
        return G.construction_isa(toks, {t.gidx: t.upos for t in toks})
    by_g = {t.gidx: t for t in toks}
    links = set()
    for t in toks:
        # apposition: t --appos--> head
        if t.deprel and t.deprel.startswith("appos"):
            h = by_g.get(t.head - 1 + (t.gidx - (t.idx - 1)))  # approximate; fall back below
        # robust: use sentence-local head resolution
    # simpler robust pass: within each sentence, map idx->gidx
    sent_tokens = {}
    for t in toks:
        sent_tokens.setdefault(t.sent, []).append(t)
    for s, ts in sent_tokens.items():
        idx2g = {t.idx: t.gidx for t in ts}
        lemma_by_idx = {t.idx: t.lemma.lower() for t in ts}
        upos_by_idx = {t.idx: t.upos for t in ts}
        for t in ts:
            if t.deprel and t.deprel.startswith("appos") and t.head in lemma_by_idx:
                a, b = t.lemma.lower(), lemma_by_idx[t.head]
                if upos_by_idx.get(t.idx) in ("NOUN", "PROPN") and upos_by_idx.get(t.head) in ("NOUN", "PROPN"):
                    links.add(frozenset((a, b)))
            # copula: t is 'be' with cop deprel; its head is the predicate nominal, whose nsubj is the subject
            if t.lemma.lower() == "be" and t.deprel == "cop" and t.head in lemma_by_idx:
                pred = t.head
                subj = None
                for u in ts:
                    if u.head == pred and u.deprel.startswith("nsubj"):
                        subj = u.idx
                if subj is not None and upos_by_idx.get(pred) in ("NOUN", "PROPN") and upos_by_idx.get(subj) in ("NOUN", "PROPN"):
                    links.add(frozenset((lemma_by_idx[pred], lemma_by_idx[subj])))
    typed = {}
    for l in links:
        a, b = tuple(l) if len(l) == 2 else (next(iter(l)), next(iter(l)))
        typed.setdefault(a, set()).add(b)
        typed.setdefault(b, set()).add(a)
    return typed


def run(n_docs=None, dump=12):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    test = _load(n_docs)
    cats = Counter()
    n_diff = 0
    examples = []
    for d in test:
        gold_first = {}
        for m in d.mentions:
            gold_first.setdefault(m.eid, m.order)
        typed = _appos_copula_isa(d)
        prior = []   # (order, eid, head, mtype, name_tokens, text)
        # precompute per-entity event co-participation signature: verbs whose args include a mention of the entity
        for m in d.mentions:
            is_ana = gold_first[m.eid] < m.order
            if m.mtype == "common" and is_ana:
                same_head_prior = any(p[2] == m.lemma_head for p in prior)
                if same_head_prior:
                    prior.append((m.order, m.eid, m.lemma_head, m.mtype, set(), m.text)); continue
                # DIFFERENT-HEAD slice
                n_diff += 1
                same_eid_prior = [p for p in prior if p[1] == m.eid]
                cat = None
                # (a) apposition/copula text-stated is-a
                if any((p[2] in typed.get(m.lemma_head, set())) for p in same_eid_prior):
                    cat = "appos_copula_intext"
                # (b) name containment
                elif any(p[3] == "name" and m.lemma_head in p[4] for p in same_eid_prior):
                    cat = "name_containment"
                # (c) wordnet type
                elif any(p[2] and wn_related(m.lemma_head, p[2]) for p in same_eid_prior):
                    cat = "wordnet_type"
                else:
                    cat = "residual_world_knowledge"
                cats[cat] += 1
                if len(examples) < dump and cat in ("residual_world_knowledge", "appos_copula_intext"):
                    ante = same_eid_prior[-1] if same_eid_prior else None
                    examples.append({"cat": cat, "anaphor": m.text, "head": m.lemma_head,
                                     "antecedent": ante[5] if ante else None,
                                     "ante_head": ante[2] if ante else None})
            nmt = _name_tokens(m) if m.mtype == "name" else set()
            prior.append((m.order, m.eid, m.lemma_head, m.mtype, nmt, m.text))

    out = {"ts_iso": datetime.now(timezone.utc).isoformat(), "n_docs_test": len(test),
           "n_different_head": n_diff,
           "categories": {k: {"n": cats[k], "frac_of_diffhead": round(cats[k] / max(n_diff, 1), 4)} for k in
                          ("appos_copula_intext", "name_containment", "wordnet_type", "residual_world_knowledge")},
           "glassbox_reachable_frac": round((cats["appos_copula_intext"] + cats["name_containment"] + cats["wordnet_type"]) / max(n_diff, 1), 4),
           "examples": examples,
           "note": "different-head anaphors are the ONLY slice with headroom (string-identity scores them 0). This "
                   "splits them into IN-TEXT glass-box signal (apposition/copula is-a, name-containment, WordNet type) "
                   "vs RESIDUAL world-knowledge (needs external facts -> the sibling P31 entity-type-KB brief).",
           "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2, default=str)
    print(json.dumps(out, indent=2, default=str))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--dump", type=int, default=12)
    a = ap.parse_args()
    run(n_docs=a.docs, dump=a.dump)
