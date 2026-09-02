"""exp_parser_gap_decomp_v1 -- WHERE does the frontend->spaCy who-did-what gap live: POS, HEAD-ATTACHMENT,
or LABELING? (the crux disambiguation for the parser problem; owner: "fully disambiguate where we lose the
signal the entire way").

The parent measured arc_parser 0.515 < spaCy 0.588 (+0.073) on QA-SRL science who-did-what. BOTH used a
LABELED role rule (patient = a token labeled obj/nsubjpass and head==verb). This cell decomposes the +0.073
into three named components by crossing {frontend parse, spaCy parse} x {LABELED role rule, LABEL-FREE role
rule}. The LABEL-FREE rule recovers the patient from HEAD-ATTACHMENT + POS + VOICE only (no dep label): among
tokens whose head IS the verb and whose POS is nominal, pick by voice+position (passive -> pre-verbal filler;
active -> nearest post-verbal). Holding the role rule fixed and swapping the parse isolates HEAD-ATTACHMENT
(UAS) quality; holding the parse fixed and swapping the rule isolates the LABELER contribution.

  A0 POS            linear position (post-verbal -> patient)                         [floor]
  A1 FE_LABELED     frontend heads + arc_labeler labels (obj/nsubj:pass)             [= parent 0.515]
  A2 FE_LABELFREE   frontend heads + POS + voice, NO labels                          [A1-A2 = labeler effect]
  A3 SP_LABELFREE   spaCy heads + POS + voice, NO labels                             [A3-A2 = pure HEAD-ATTACH]
  A4 SP_LABELED     spaCy heads + spaCy dep labels (dobj/nsubjpass)                  [= parent 0.588; A4-A3 = spaCy label effect]
  A5 GOLD_ATTACH    oracle: gold patient IS a candidate -> pick it                   [upper bound]

Also: the substrate UAS ladder on UD-EWT test (richfeat / hashed / mst arc-factored parsers) + spaCy UAS on
the SAME gold tokens (pretokenized Doc), so the head-attachment component in who-did-what is anchored to a
measured UAS gap. Modern QA-science + 19c LitBank. spaCy = glass-box parser (NOT an LLM), diagnostic only.
ASCII. Writes only to its own dir. --self-test smoke-gates the role rules on a hand example.
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
if os.path.join(_REPO, "experiments") not in sys.path:
    sys.path.insert(0, os.path.join(_REPO, "experiments"))
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
from hdlab.animacy_lexicon import lookup_animacy

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_parser_gap_decomp_v1")
STRUCT = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|[0-9]+|[^\sA-Za-z0-9]")
FE_LAB = os.path.join(_REPO, "data", "frontend_assets")
NOUN = {"NOUN", "PROPN", "PRON"}
FE_OBJ = {"obj", "dobj", "nsubj:pass", "nsubjpass"}
SPACY_OBJ = {"dobj", "nsubjpass", "dobjpass"}


def anim(w):
    a = lookup_animacy(w)
    return isinstance(a, dict) and (a.get("animacy") == "animate" or a.get("category") in ("person", "animal"))


# ---------------------------------------------------------------------------------------------------
# Per-sentence parse -> for each verb lemma: {LABELED: set(patient forms), LABELFREE: set(head-attached
# nominal forms with voice/position tags}. We store, per verb lemma, dicts keyed by role rule.
# ---------------------------------------------------------------------------------------------------
def _voice_is_passive(toks_lower, vi):
    """crude voice: a be/aux + past participle-ish (-ed/-en) at the verb, or 'by' following. vi is 0-based."""
    lo = max(0, vi - 3)
    window = toks_lower[lo:vi]
    beforms = {"is", "are", "was", "were", "be", "been", "being", "am", "'s", "get", "gets", "got", "gotten"}
    return any(w in beforms for w in window)


def frontend_parses(sents):
    from hdlab.pos_tagger import PosTagger
    from hdlab.arc_parser import ArcParser
    from hdlab.arc_labeler import ArcLabeler
    from hdlab.reading_grounding_loop import normalize_lemma
    tg = PosTagger.load(os.path.join(FE_LAB, "pos_tagger_ud_ewt_upos.json"))
    pr = ArcParser.load(os.path.join(FE_LAB, "arc_parser_richfeat_ud_ewt.npz"))
    lb = ArcLabeler.load(os.path.join(FE_LAB, "arc_labeler_hashed_ud_ewt.json"))
    out = {}
    t0 = time.time()
    for k, sent in enumerate(sents):
        toks = STRUCT.findall(sent)
        labeled = defaultdict(set); labelfree = defaultdict(set)
        if toks and len(toks) <= 80:
            try:
                pos = tg.tag(toks); heads = pr.parse(toks, pos).heads; labs = lb.label(toks, pos, heads)
                lem = [normalize_lemma(t) for t in toks]; low = [t.lower() for t in toks]; N = len(toks)
                for i in range(1, N + 1):        # i is 1-based dep idx
                    h = heads.get(i, 0)
                    if not (1 <= h <= N and pos[h - 1] == "VERB"):
                        continue
                    vlem = V1._lem(lem[h - 1])
                    rel = labs.get(i)
                    if rel in FE_OBJ:
                        labeled[vlem].add(lem[i - 1]); labeled[vlem].add(low[i - 1])
                    if pos[i - 1] in NOUN:       # LABEL-FREE: any head-attached nominal
                        pas = _voice_is_passive(low, h - 1)
                        tag = ("PRE" if i < h else "POST")
                        labelfree[vlem].add((lem[i - 1], tag, pas))
                        labelfree[vlem].add((low[i - 1], tag, pas))
            except Exception:
                pass
        out[sent] = (dict(labeled), dict(labelfree))
        if (k + 1) % 1000 == 0:
            print("[frontend] %d/%d %.0fs" % (k + 1, len(sents), time.time() - t0), flush=True)
    return out


def spacy_parses(sents):
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    out = {}
    t0 = time.time()
    for k, doc in enumerate(nlp.pipe(sents, batch_size=64)):
        labeled = defaultdict(set); labelfree = defaultdict(set)
        for tok in doc:
            hd = tok.head
            if hd.pos_ != "VERB":
                continue
            vlem = V1._lem(hd.lemma_.lower())
            forms = {tok.lemma_.lower(), tok.text.lower()}
            if tok.dep_ in SPACY_OBJ:
                labeled[vlem] |= forms
            if tok.pos_ in NOUN:
                pas = (tok.dep_ == "nsubjpass") or any(c.dep_ == "auxpass" for c in hd.children)
                tag = ("PRE" if tok.i < hd.i else "POST")
                for f in forms:
                    labelfree[vlem].add((f, tag, pas))
        out[sents[k]] = (dict(labeled), dict(labelfree))
        if (k + 1) % 1000 == 0:
            print("[spacy] %d/%d %.0fs" % (k + 1, len(sents), time.time() - t0), flush=True)
    return out


def cands(r):
    return [(h, idx) for h, idx in zip(r["cand_heads"], r["cand_idx"]) if h not in V1.STOP and len(h) >= 3]


def in_set(h, s):
    return V1._lem(h) in s or h in s


def pick_labeled(r, parses):
    C = cands(r)
    if len(C) < 2:
        return r.get("pos_pick")
    objs = parses.get(r["sent"], ({}, {}))[0].get(V1._lem(r["verb"]), set())
    hits = [h for h, idx in C if in_set(h, objs)]
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        vi = r["verb_idx"]; post = [(idx, h) for h, idx in C if in_set(h, objs) and idx > vi]
        return min(post)[1] if post else hits[0]
    return r.get("pos_pick")


def pick_labelfree(r, parses):
    """patient from head-attached nominals + voice + position, NO dep labels."""
    C = cands(r)
    if len(C) < 2:
        return r.get("pos_pick")
    lf = parses.get(r["sent"], ({}, {}))[1].get(V1._lem(r["verb"]), set())
    if not lf:
        return r.get("pos_pick")
    # forms attached to the verb, with their (tag, passive) markers
    formtags = defaultdict(list)
    passive_any = False
    for (form, tag, pas) in lf:
        formtags[form].append((tag, pas))
        passive_any = passive_any or pas
    hitc = [(h, idx) for h, idx in C if (V1._lem(h) in formtags or h in formtags)]
    if not hitc:
        return r.get("pos_pick")
    if len(hitc) == 1:
        return hitc[0][0]
    vi = r["verb_idx"]
    if passive_any:
        # passive: patient is the PRE-verbal head-attached nominal (surface subject)
        pre = [(idx, h) for h, idx in hitc if idx < vi]
        if pre:
            return max(pre)[1]     # nearest pre-verbal
    post = [(idx, h) for h, idx in hitc if idx > vi]
    if post:
        return min(post)[1]        # nearest post-verbal = the object
    return hitc[0][0]


def pick_gold_attach(r, parses_fe, parses_sp):
    """oracle: if the gold patient is a candidate at all, pick it (upper bound on selection)."""
    C = cands(r)
    if len(C) < 2:
        return r.get("pos_pick")
    g = r["gold_head"]
    if any(h == g for h, idx in C):
        return g
    return r.get("pos_pick")


def measure_uas():
    """UAS of the substrate arc-factored parsers on UD-EWT test, + spaCy on the same gold tokens."""
    from _ud_loader import load_conllu
    from hdlab.pos_tagger import PosTagger
    from hdlab.arc_parser import ArcParser
    test = load_conllu("test")
    test = [s for s in test if 1 <= len(s) <= 50]
    tg = PosTagger.load(os.path.join(FE_LAB, "pos_tagger_ud_ewt_upos.json"))
    out = {}
    for name, fn in (("richfeat", "arc_parser_richfeat_ud_ewt.npz"),
                     ("hashed", "arc_parser_hashed_ud_ewt.npz"),
                     ("mst_retrain", "arc_parser_mst_retrain_ud_ewt.npz")):
        pr = ArcParser.load(os.path.join(FE_LAB, fn))
        # gold-POS UAS (isolates head-attachment from tagging)
        uas_g, c, t = pr.eval_uas(test)
        # predicted-POS UAS (the deployment condition: tagger feeds the parser)
        hitp = totp = 0
        for s in test:
            toks = [w for (_i, w, _p, _h, _d) in s]
            pos = tg.tag(toks)
            heads = pr.parse(toks, pos).heads
            for (i, w, p, h, d) in s:
                if h < 0 or h > len(s):
                    continue
                hitp += int(heads.get(i, -1) == h); totp += 1
        out[name] = {"uas_goldpos": round(uas_g, 4), "uas_predpos": round(hitp / totp, 4), "n_arcs": t}
        print("  [UAS] %-12s goldPOS=%.4f predPOS=%.4f (n=%d)" % (name, uas_g, hitp / totp, t), flush=True)
    # spaCy UAS on the same gold tokens (pretokenized) -- fair same-token comparison
    try:
        import spacy
        from spacy.tokens import Doc
        nlp = spacy.load("en_core_web_sm", disable=["ner"])
        hit = tot = 0
        for s in test:
            words = [w for (_i, w, _p, _h, _d) in s]
            doc = Doc(nlp.vocab, words=words)
            for name, proc in nlp.pipeline:
                doc = proc(doc)
            for k, (i, w, p, h, d) in enumerate(s):
                if h < 0 or h > len(s):
                    continue
                tok = doc[k]
                pred_head = 0 if tok.head.i == tok.i else tok.head.i + 1  # ROOT -> 0, else 1-based
                hit += int(pred_head == h); tot += 1
        out["spacy"] = {"uas_predpos": round(hit / tot, 4), "n_arcs": tot}
        print("  [UAS] %-12s               predPOS=%.4f (n=%d)" % ("spacy", hit / tot, tot), flush=True)
    except Exception as e:
        out["spacy"] = {"error": str(e)[:120]}
        print("  [UAS] spacy FAILED: %s" % str(e)[:120], flush=True)
    return out


def run_pop(pop_name, path, nboot):
    rows = V1.load_pop(path)
    sents = sorted({r["sent"] for r in rows})
    print("[%s] %d items, %d sentences" % (pop_name, len(rows), len(sents)), flush=True)
    fe = frontend_parses(sents)
    sp = spacy_parses(sents)

    def nonrev(r):
        return sum(1 for h, _ in cands(r) if anim(h)) < 2
    FULL = [r for r in rows if len(cands(r)) >= 2 and nonrev(r)]
    HARD = [r for r in FULL if (r.get("voice") == "passive" or r.get("noncanonical"))]
    arms = {
        "A0_POS": lambda r: r.get("pos_pick"),
        "A1_FE_LABELED": lambda r: pick_labeled(r, fe),
        "A2_FE_LABELFREE": lambda r: pick_labelfree(r, fe),
        "A3_SP_LABELFREE": lambda r: pick_labelfree(r, sp),
        "A4_SP_LABELED": lambda r: pick_labeled(r, sp),
        "A5_GOLD_ATTACH": lambda r: pick_gold_attach(r, fe, sp),
    }

    def acc(fn, S):
        return round(sum(1 for r in S if fn(r) == r["gold_head"]) / len(S), 4) if S else 0.0
    res = {"n_FULL": len(FULL), "n_HARD": len(HARD), "acc": {}, "deltas": {}}
    # decomposition deltas (on FULL)
    D = lambda a, b: {k: V1.paired_delta(FULL, arms[a], arms[b], nboot)[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")}
    for tag, S in (("FULL", FULL), ("HARD", HARD)):
        res["acc"][tag] = {a: acc(f, S) for a, f in arms.items()}
        print("\n=== %s / %s (n=%d) ===" % (pop_name, tag, len(S)), flush=True)
        for a in arms:
            print("  %-16s acc=%.4f" % (a, res["acc"][tag][a]), flush=True)
    res["deltas"] = {
        "TOTAL_gap  (A4-A1)": D("A4_SP_LABELED", "A1_FE_LABELED"),
        "HEADATTACH (A3-A2)": D("A3_SP_LABELFREE", "A2_FE_LABELFREE"),
        "FE_labeler (A1-A2)": D("A1_FE_LABELED", "A2_FE_LABELFREE"),
        "SP_labeler (A4-A3)": D("A4_SP_LABELED", "A3_SP_LABELFREE"),
        "FE_struct  (A1-A0)": D("A1_FE_LABELED", "A0_POS"),
    }
    print("  --- decomposition of the frontend->spaCy who-did-what gap (FULL) ---", flush=True)
    for lbl, d in res["deltas"].items():
        print("    %-20s d=%+.4f CI[%+.4f,%+.4f] frac<=0=%.3f" % (lbl, d["delta"], d["ci_lo"], d["ci_hi"], d["frac_le_0"]), flush=True)
    return res


def _selftest():
    # role-rule smoke: passive picks pre-verbal, active picks nearest post-verbal
    r = {"sent": "S", "verb": "eat", "verb_idx": 3, "gold_head": "apple",
         "cand_heads": ["dog", "apple"], "cand_idx": [1, 4], "pos_pick": "dog"}
    fe = {"S": ({}, {"eat": {("apple", "POST", False), ("dog", "PRE", False)}})}
    assert pick_labelfree(r, fe) == "apple", "active label-free should pick post-verbal object"
    r2 = dict(r, verb="chase", gold_head="dog", cand_idx=[1, 4])
    fe2 = {"S": ({}, {"chase": {("dog", "PRE", True), ("apple", "POST", True)}})}
    assert pick_labelfree(r2, fe2) == "dog", "passive label-free should pick pre-verbal filler"
    print("[selftest] PASS role rules", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nboot", type=int, default=2000)
    ap.add_argument("--pops", type=str, default="qa,litbank")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--no-uas", action="store_true")
    args = ap.parse_args()
    _selftest()
    if args.self_test:
        return
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    out = {"pops": {}}
    if not args.no_uas:
        print("\n=== UAS LADDER on UD-EWT test ===", flush=True)
        out["uas"] = measure_uas()
    pmap = {"qa": V1.QA, "litbank": V1.LB}
    for p in args.pops.split(","):
        out["pops"][p] = run_pop(p, pmap[p], args.nboot)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "parser_gap_decomp_v1", "results": out,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
