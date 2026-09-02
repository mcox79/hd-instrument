"""exp_error_decomposition_v1 -- WHERE EXACTLY is who-did-what signal lost? (owner: "disambiguate this problem
aggressively -- where, exactly, are you losing signal").

Partitions the held-out QA-science non-reversible items by the RELATION of the gold patient to its verb in the
(spaCy) parse, and reports per-partition accuracy of POS / STRUCT / STRUCT+SEL so every point of the 0.59
STRUCT score is attributed to a named failure mode:

  A  gold IS the verb's OBJECT (dobj/nsubjpass)     -- STRUCT should get it; loss here = SELECTION among
                                                        multiple parsed objects (the store's job).
  B  gold is ANOTHER verb argument (pobj/dative/...) -- RICH-reachable (measured tiny 2.4%).
  C  gold is a dependent of the verb with a NON-ARG relation (nsubj[voice error]/conj/nmod/appos/...)
                                                     -- parser LABEL/voice error.
  D  gold is NOT a dependent of the verb at all      -- parser ATTACHMENT error (or gold not an argument).
  E  the VERB was not found as a VERB in the parse   -- POS-tagging error.
For C/D/E we also report POS accuracy: if position STILL gets it, the info is present and the PARSER lost it
(fixable by a better parser); if position also fails, it is genuinely hard.

Also: on partition A, how many items have >1 parsed object (a real WHICH-is-patient choice) and does the
register-native store recover them. spaCy = a glass-box parser (NOT an LLM). ASCII. Own dir only.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
from collections import defaultdict, Counter
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import torch
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_register_native_store_v1 as E
import experiments.exp_fhrr_event_role_assignment_v1 as F
from hdlab import binding
from hdlab.situation_model_accumulate import unit_phase_vec
from hdlab.animacy_lexicon import lookup_animacy

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_error_decomposition_v1")
OBJ = {"dobj", "nsubjpass"}
OTHER_ARG = {"pobj_of_verb", "dative", "oprd", "attr", "iobj", "obl"}


def anim(w):
    a = lookup_animacy(w)
    return isinstance(a, dict) and (a.get("animacy") == "animate" or a.get("category") in ("person", "animal"))


def parse_full(sents):
    """sent -> ({verb_lemma: {relation: set(forms)}}, set(verb_lemmas), {verb_lemma: [obj forms]})."""
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    out = {}
    t0 = time.time()
    for k, doc in enumerate(nlp.pipe(sents, batch_size=64)):
        rels = defaultdict(lambda: defaultdict(set)); verbs = set()
        for tok in doc:
            if tok.pos_ == "VERB":
                verbs.add(V1._lem(tok.lemma_.lower()))
            hd = tok.head
            forms = {tok.lemma_.lower(), tok.text.lower()}
            if hd.pos_ == "VERB":
                rels[V1._lem(hd.lemma_.lower())][tok.dep_] |= forms
            if tok.dep_ == "pobj" and hd.dep_ == "prep" and hd.head.pos_ == "VERB":
                rels[V1._lem(hd.head.lemma_.lower())]["pobj_of_verb"] |= forms
        out[sents[k]] = ({v: dict(d) for v, d in rels.items()}, verbs)
        if (k + 1) % 1000 == 0:
            print("[spacy] %d/%d %.0fs" % (k + 1, len(sents), time.time() - t0), flush=True)
    return out


def cands(r):
    return [(h, idx) for h, idx in zip(r["cand_heads"], r["cand_idx"]) if h not in V1.STOP and len(h) >= 3]


def in_set(h, s):
    return V1._lem(h) in s or h in s


def gold_relation(r, P):
    """return (class, relation_label) of the gold patient to its verb in the parse."""
    rels, verbs = P.get(r["sent"], ({}, set()))
    vl = V1._lem(r["verb"]); g = r["gold_head"]
    if vl not in verbs and vl not in rels:
        return "E_verb_not_found", None
    rd = rels.get(vl, {})
    grel = None
    for rel, forms in rd.items():
        if in_set(g, forms):
            grel = rel; break
    if grel is None:
        return "D_gold_not_verb_dep", None
    if grel in OBJ:
        return "A_gold_is_object", grel
    if grel in OTHER_ARG:
        return "B_gold_other_arg", grel
    return "C_gold_nonarg_rel", grel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", type=int, default=1_200_000)
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    rows = V1.load_pop(V1.QA)
    sents = sorted({r["sent"] for r in rows})
    print("[data] %d items, %d sentences" % (len(rows), len(sents)), flush=True)
    P = parse_full(sents)

    parsed = E.parse_corpus("science", args.tokens, set())
    vocab = set()
    for a, v, o in parsed["svo"]:
        vocab.add(a); vocab.add(o)
    for r in rows:
        vocab.update(h for h in r["cand_heads"] if len(h) >= 3)
    gv = E.load_glove_union(vocab)
    enc = F.make_encoder()
    A = unit_phase_vec(E.D, torch.Generator().manual_seed(1)).to(torch.complex64)
    Pk = unit_phase_vec(E.D, torch.Generator().manual_seed(2)).to(torch.complex64)
    fhrr = E.build_fhrr(parsed, gv, enc, A, Pk)
    ecache = {}
    def enc_c(h):
        if h not in ecache:
            ecache[h] = enc(gv[h])
        return ecache[h]

    def struct_pick(r):
        rels = P.get(r["sent"], ({}, set()))[0].get(V1._lem(r["verb"]), {})
        objs = set()
        for rel in OBJ:
            objs |= rels.get(rel, set())
        C = cands(r); hits = [h for h, idx in C if in_set(h, objs)]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            vi = r["verb_idx"]; post = [(idx, h) for h, idx in C if in_set(h, objs) and idx > vi]
            return min(post)[1] if post else hits[0]
        return r.get("pos_pick")

    def sel_pick_all(r):
        """the store picks among ALL candidates (agent-marginalized FHRR) -- no parser."""
        toks = fhrr.get(V1._lem(r["verb"])); C = [(h, idx) for h, idx in cands(r) if gv.get(h) is not None]
        if toks is None or len(C) < 2:
            return r.get("pos_pick")
        best = None; bs = -1e9
        for h, idx in C:
            s = 0.0
            for a, aidx in C:
                if a == h:
                    continue
                q = F.quantize(binding.bind(A, enc_c(a)) + binding.bind(Pk, enc_c(h)))
                s += max(0.0, F.recognition(q, toks))
            if s > bs:
                bs = s; best = h
        return best

    def struct_sel_pick(r):
        """STRUCT, but when the parser finds >1 object, the store disambiguates."""
        rels = P.get(r["sent"], ({}, set()))[0].get(V1._lem(r["verb"]), {})
        objs = set()
        for rel in OBJ:
            objs |= rels.get(rel, set())
        C = cands(r); hits = [h for h, idx in C if in_set(h, objs)]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            toks = fhrr.get(V1._lem(r["verb"]))
            if toks is None:
                vi = r["verb_idx"]; post = [(idx, h) for h, idx in C if in_set(h, objs) and idx > vi]
                return min(post)[1] if post else hits[0]
            allc = [(h, idx) for h, idx in cands(r) if gv.get(h) is not None]
            best = None; bs = -1e9
            for h in hits:
                if gv.get(h) is None:
                    continue
                s = 0.0
                for a, aidx in allc:
                    if a == h:
                        continue
                    q = F.quantize(binding.bind(A, enc_c(a)) + binding.bind(Pk, enc_c(h)))
                    s += max(0.0, F.recognition(q, toks))
                if s > bs:
                    bs = s; best = h
            return best or hits[0]
        return r.get("pos_pick")

    def nonrev(r):
        return sum(1 for h, _ in cands(r) if anim(h)) < 2
    FULL = [r for r in rows if len(cands(r)) >= 2 and nonrev(r)]
    n = len(FULL)

    # classify every item
    buckets = defaultdict(list); relcount = Counter()
    for r in FULL:
        cls, rel = gold_relation(r, P)
        buckets[cls].append(r)
        if cls == "C_gold_nonarg_rel":
            relcount[rel] += 1

    def acc(fn, S):
        return sum(1 for r in S if fn(r) == r["gold_head"]) / len(S) if S else 0.0

    print("\n=== SIGNAL-LOSS DECOMPOSITION (FULL non-reversible n=%d) ===" % n, flush=True)
    print("  %-26s %6s %6s | POS   STRUCT STR+SEL SEL_all  what it is / what would fix it" % ("partition", "count", "share"), flush=True)
    order = ["A_gold_is_object", "B_gold_other_arg", "C_gold_nonarg_rel", "D_gold_not_verb_dep", "E_verb_not_found"]
    fix = {"A_gold_is_object": "SELECTION among parsed objects (the store)",
           "B_gold_other_arg": "richer extraction (tiny)",
           "C_gold_nonarg_rel": "parser LABEL/voice error -> better parser",
           "D_gold_not_verb_dep": "parser ATTACHMENT error -> better parser",
           "E_verb_not_found": "POS-tagging error -> better tagger"}
    out = {"n": n, "partitions": {}}
    for cls in order:
        S = buckets.get(cls, [])
        if not S:
            continue
        aP = acc(lambda r: r.get("pos_pick"), S); aS = acc(struct_pick, S)
        aSS = acc(struct_sel_pick, S); aA = acc(sel_pick_all, S)
        out["partitions"][cls] = {"count": len(S), "share": round(len(S) / n, 3),
                                  "POS": round(aP, 3), "STRUCT": round(aS, 3), "STRUCT_SEL": round(aSS, 3), "SEL_all": round(aA, 3)}
        print("  %-26s %6d %5.1f%% | %.3f %.3f  %.3f   %.3f   %s"
              % (cls, len(S), 100 * len(S) / n, aP, aS, aSS, aA, fix[cls]), flush=True)

    # partition A: how many have a real WHICH-object choice, and does the store recover it?
    Abkt = buckets["A_gold_is_object"]
    multi = []
    for r in Abkt:
        rels = P.get(r["sent"], ({}, set()))[0].get(V1._lem(r["verb"]), {})
        objs = set()
        for rel in OBJ:
            objs |= rels.get(rel, set())
        if sum(1 for h, idx in cands(r) if in_set(h, objs)) > 1:
            multi.append(r)
    print("\n  [A] %d/%d gold-is-object items have >1 parsed object (a real WHICH choice):" % (len(multi), len(Abkt)), flush=True)
    if multi:
        print("      STRUCT %.3f  STRUCT+SEL %.3f  (the store's disambiguation headroom on A)"
              % (acc(struct_pick, multi), acc(struct_sel_pick, multi)), flush=True)
    print("\n  [C] gold-attached-with-nonarg-relation breakdown:", dict(relcount.most_common(8)), flush=True)
    out["A_multi_object"] = {"n_multi": len(multi), "n_A": len(Abkt),
                             "STRUCT": round(acc(struct_pick, multi), 3), "STRUCT_SEL": round(acc(struct_sel_pick, multi), 3)}
    out["C_relations"] = dict(relcount.most_common())

    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "error_decomposition_v1", "results": out,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
