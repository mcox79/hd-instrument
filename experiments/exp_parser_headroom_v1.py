"""exp_parser_headroom_v1 -- IS THE PARSER THE BOTTLENECK? Diagnostic headroom test for who-did-what role
assignment (owner: "is there a parser that could be causing lower scores?").

The brain-faithful integration showed the STRUCTURAL cue (patient = the verb's grammatical OBJECT / PASSIVE
SUBJECT, from a real parse) is the who-did-what lever, and it beats linear position. But that used the
substrate's OWN frontend UD parser (ArcParser, ~UAS 0.85-0.90). This asks: does a DIFFERENT, independently-
trained statistical parser (spaCy en_core_web_sm) -- a proxy for "a better parser" -- assign roles BETTER?
If spaCy-STRUCT beats frontend-STRUCT CI-separated, the PARSER ACCURACY is the live bottleneck and improving
it is the lever (the parent p5 audit + the situation_model submission both name the parser as the highest-
compounding front-end lever).

ARMS (patient = candidate matched to the parser's object/passive-subject of the target verb; else backoff to
position):
  POS            linear position (post-verbal -> patient) -- the wired reader's role_route='positional'
  FRONTEND       the substrate's UD parser (ArcParser + ArcLabeler): rel in {obj, nsubj:pass}
  SPACY          spaCy en_core_web_sm parser: dep in {dobj, nsubjpass}   (a DIFFERENT, stronger-ish parser)
  UNION          patient found by EITHER parser (an upper-ish bound on parser coverage)
Reports accuracy + SPACY_vs_FRONTEND and FRONTEND_vs_POS on modern QA-science and 19c LitBank (generalization).
spaCy is a glass-box statistical parser (NOT an LLM); this is a DIAGNOSTIC headroom measurement, not a wired
reader component. ASCII. Writes only to its own dir.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, re, sys, time
from collections import defaultdict
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
from hdlab.animacy_lexicon import lookup_animacy

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_parser_headroom_v1")
STRUCT = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|[0-9]+|[^\sA-Za-z0-9]")
FE_OBJ = {"obj", "dobj", "nsubj:pass", "nsubjpass"}
SPACY_OBJ = {"dobj", "nsubjpass", "dobjpass"}


def anim(w):
    a = lookup_animacy(w)
    return isinstance(a, dict) and (a.get("animacy") == "animate" or a.get("category") in ("person", "animal"))


# ---------------- frontend UD parser: sentence -> {verb_lemma: set(patient_lemmas)} ----------------
def frontend_patients(sents):
    from hdlab.pos_tagger import PosTagger
    from hdlab.arc_parser import ArcParser
    from hdlab.arc_labeler import ArcLabeler
    from hdlab.reading_grounding_loop import normalize_lemma
    FE = os.path.join(_REPO, "data", "frontend_assets")
    tg = PosTagger.load(os.path.join(FE, "pos_tagger_ud_ewt_upos.json"))
    pr = ArcParser.load(os.path.join(FE, "arc_parser_richfeat_ud_ewt.npz"))
    lb = ArcLabeler.load(os.path.join(FE, "arc_labeler_hashed_ud_ewt.json"))
    out = {}
    t0 = time.time()
    for k, sent in enumerate(sents):
        toks = STRUCT.findall(sent)
        d = defaultdict(set)
        if toks and len(toks) <= 80:
            try:
                pos = tg.tag(toks); heads = pr.parse(toks, pos).heads; labs = lb.label(toks, pos, heads)
                lem = [normalize_lemma(t) for t in toks]; N = len(toks)
                for i in range(1, N + 1):
                    rel = labs.get(i); h = heads.get(i, 0)
                    if rel in FE_OBJ and 1 <= h <= N and pos[h - 1] == "VERB":
                        d[V1._lem(lem[h - 1])].add(lem[i - 1])
            except Exception:
                pass
        out[sent] = d
        if (k + 1) % 1000 == 0:
            print("[frontend] %d/%d %.0fs" % (k + 1, len(sents), time.time() - t0), flush=True)
    return out


# ---------------- spaCy parser: sentence -> {verb_lemma: set(patient_lemmas)} ----------------
def spacy_patients(sents):
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    out = {}
    t0 = time.time()
    for k, doc in enumerate(nlp.pipe(sents, batch_size=64)):
        d = defaultdict(set)
        for tok in doc:
            if tok.dep_ in SPACY_OBJ and tok.head.pos_ == "VERB":
                d[V1._lem(tok.head.lemma_.lower())].add(tok.lemma_.lower())
                d[V1._lem(tok.head.lemma_.lower())].add(tok.text.lower())
        out[sents[k]] = d
        if (k + 1) % 1000 == 0:
            print("[spacy] %d/%d %.0fs" % (k + 1, len(sents), time.time() - t0), flush=True)
    return out


def cands(r):
    return [(h, idx) for h, idx in zip(r["cand_heads"], r["cand_idx"]) if h not in V1.STOP and len(h) >= 3]


def struct_pick(r, patients_by_sent):
    C = cands(r)
    if len(C) < 2:
        return r.get("pos_pick")
    pats = patients_by_sent.get(r["sent"], {}).get(V1._lem(r["verb"]), set())
    hits = [h for h, idx in C if V1._lem(h) in pats or h in pats]
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:                      # parser found several objects -> nearest post-verbal, else first
        vi = r["verb_idx"]
        post = [(idx, h) for h, idx in C if (V1._lem(h) in pats or h in pats) and idx > vi]
        return (min(post)[1] if post else hits[0])
    return r.get("pos_pick")               # parser found no object -> backoff to position


def union_pick(r, fe, sp):
    C = cands(r)
    if len(C) < 2:
        return r.get("pos_pick")
    pf = fe.get(r["sent"], {}).get(V1._lem(r["verb"]), set())
    ps = sp.get(r["sent"], {}).get(V1._lem(r["verb"]), set())
    pats = pf | ps
    hits = [h for h, idx in C if V1._lem(h) in pats or h in pats]
    if hits:
        vi = r["verb_idx"]
        post = [(idx, h) for h, idx in C if (V1._lem(h) in pats or h in pats) and idx > vi]
        return (min(post)[1] if post else hits[0])
    return r.get("pos_pick")


def run(pop_name, path, nboot):
    rows = V1.load_pop(path)
    sents = sorted({r["sent"] for r in rows})
    print("[%s] %d items, %d unique sentences" % (pop_name, len(rows), len(sents)), flush=True)
    fe = frontend_patients(sents)
    sp = spacy_patients(sents)

    def nonrev(r):
        return sum(1 for h, _ in cands(r) if anim(h)) < 2
    FULL = [r for r in rows if len(cands(r)) >= 2 and nonrev(r)]
    HARD = [r for r in FULL if (r.get("voice") == "passive" or r.get("noncanonical"))]
    arms = {
        "POS": lambda r: r.get("pos_pick"),
        "FRONTEND": lambda r: struct_pick(r, fe),
        "SPACY": lambda r: struct_pick(r, sp),
        "UNION": lambda r: union_pick(r, fe, sp),
    }
    def acc(fn, S):
        return round(sum(1 for r in S if fn(r) == r["gold_head"]) / len(S), 4) if S else 0.0
    res = {"n_FULL": len(FULL), "n_HARD": len(HARD), "acc": {}, "deltas": {}}
    for tag, S in (("FULL", FULL), ("HARD", HARD)):
        res["acc"][tag] = {a: acc(f, S) for a, f in arms.items()}
        res["deltas"][tag] = {
            "SPACY_vs_FRONTEND": {k: V1.paired_delta(S, arms["SPACY"], arms["FRONTEND"], nboot)[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")},
            "FRONTEND_vs_POS": {k: V1.paired_delta(S, arms["FRONTEND"], arms["POS"], nboot)[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")},
            "UNION_vs_FRONTEND": {k: V1.paired_delta(S, arms["UNION"], arms["FRONTEND"], nboot)[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")},
        }
        print("\n=== %s / %s (n=%d) ===" % (pop_name, tag, len(S)), flush=True)
        for a in ("POS", "FRONTEND", "SPACY", "UNION"):
            print("  %-9s acc=%.4f" % (a, res["acc"][tag][a]), flush=True)
        for lbl, d in res["deltas"][tag].items():
            print("    %-20s d=%+.4f CI[%+.4f,%+.4f] frac<=0=%.3f" % (lbl, d["delta"], d["ci_lo"], d["ci_hi"], d["frac_le_0"]), flush=True)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nboot", type=int, default=2000)
    ap.add_argument("--pops", type=str, default="qa,litbank")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    pmap = {"qa": V1.QA, "litbank": V1.LB}
    out = {}
    for p in args.pops.split(","):
        out[p] = run(p, pmap[p], args.nboot)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "parser_headroom_v1", "results": out,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
