"""exp_optimized_who_did_what_v1 -- FIX/OPTIMIZE every realizable bucket the signal-loss decomposition named
(owner: "can we fix/optimize the other things too?"). NO new parser -- only better USE of the two parsers we
have + the register-native store, each fix ablated so its contribution is measured.

BASELINE  = STRUCT: spaCy grammatical object (dobj/nsubjpass) -> patient, position backoff (0.588 FULL).
FIXES (stacked, each ablated):
  +UNION      object = spaCy-obj UNION frontend-UD-obj  (where one parser fails to attach, the other often
              succeeds -- addresses part of D 'attachment fail' + E 'verb not tagged'; headroom UNION>+0.076).
  +VOICE      on PASSIVE items also accept the verb's SUBJECT (nsubj) as patient (the decomposition found
              48/71 C-errors are passive patients mislabeled nsubj not nsubj:pass).
  +VTIE       voice-aware positional tiebreak: PASSIVE -> nearest PRE-verbal matched arg; ACTIVE -> nearest
              POST-verbal (the patient sits on opposite sides under the two voices).
  +STOREGATE  RELIABILITY GATE: when NO candidate matches a parsed object, fall back to the REGISTER-NATIVE
              STORE (0.308 on the parse-fail bucket) instead of linear position (0.145). The store is used
              ONLY here -- on parse-confident items it HURTS (decomposition), so it is gated OFF there.
Measured on modern QA-science FULL / HARD. spaCy + the substrate frontend are glass-box parsers (NOT LLMs).
Reuses exp_register_native_store_v1 + FHRR. ASCII. Own dir only.
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
import torch
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_register_native_store_v1 as E
import experiments.exp_fhrr_event_role_assignment_v1 as F
from hdlab import binding
from hdlab.situation_model_accumulate import unit_phase_vec
from hdlab.animacy_lexicon import lookup_animacy

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_optimized_who_did_what_v1")
STRUCT = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|[0-9]+|[^\sA-Za-z0-9]")


def anim(w):
    a = lookup_animacy(w)
    return isinstance(a, dict) and (a.get("animacy") == "animate" or a.get("category") in ("person", "animal"))


def spacy_parse(sents):
    """sent -> {verb_lemma: {'obj': set, 'subj': set}}."""
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    out = {}
    for k, doc in enumerate(nlp.pipe(sents, batch_size=64)):
        d = defaultdict(lambda: {"obj": set(), "subj": set()})
        for tok in doc:
            hd = tok.head
            if hd.pos_ == "VERB":
                vl = V1._lem(hd.lemma_.lower()); forms = {tok.lemma_.lower(), tok.text.lower()}
                if tok.dep_ in ("dobj", "nsubjpass"):
                    d[vl]["obj"] |= forms
                elif tok.dep_ == "nsubj":
                    d[vl]["subj"] |= forms
        out[sents[k]] = d
    return out


def frontend_parse(sents):
    from hdlab.pos_tagger import PosTagger
    from hdlab.arc_parser import ArcParser
    from hdlab.arc_labeler import ArcLabeler
    from hdlab.reading_grounding_loop import normalize_lemma
    FE = os.path.join(_REPO, "data", "frontend_assets")
    tg = PosTagger.load(os.path.join(FE, "pos_tagger_ud_ewt_upos.json"))
    pr = ArcParser.load(os.path.join(FE, "arc_parser_richfeat_ud_ewt.npz"))
    lb = ArcLabeler.load(os.path.join(FE, "arc_labeler_hashed_ud_ewt.json"))
    OBJ = {"obj", "dobj", "nsubj:pass", "nsubjpass"}
    out = {}; t0 = time.time()
    for k, sent in enumerate(sents):
        toks = STRUCT.findall(sent); d = defaultdict(lambda: {"obj": set(), "subj": set()})
        if toks and len(toks) <= 80:
            try:
                pos = tg.tag(toks); heads = pr.parse(toks, pos).heads; labs = lb.label(toks, pos, heads)
                lem = [normalize_lemma(t) for t in toks]; N = len(toks)
                for i in range(1, N + 1):
                    rel = labs.get(i); h = heads.get(i, 0)
                    if 1 <= h <= N and pos[h - 1] == "VERB":
                        vl = V1._lem(lem[h - 1])
                        if rel in OBJ:
                            d[vl]["obj"].add(lem[i - 1])
                        elif rel == "nsubj":
                            d[vl]["subj"].add(lem[i - 1])
            except Exception:
                pass
        out[sent] = d
        if (k + 1) % 1000 == 0:
            print("[frontend] %d/%d %.0fs" % (k + 1, len(sents), time.time() - t0), flush=True)
    return out


def cands(r):
    return [(h, idx) for h, idx in zip(r["cand_heads"], r["cand_idx"]) if h not in V1.STOP and len(h) >= 3]


def in_set(h, s):
    return V1._lem(h) in s or h in s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nboot", type=int, default=2000)
    ap.add_argument("--tokens", type=int, default=1_200_000)
    ap.add_argument("--pop", type=str, default="qa", help="qa | litbank (generalization)")
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    rows = V1.load_pop(V1.LB if args.pop == "litbank" else V1.QA)
    sents = sorted({r["sent"] for r in rows})
    print("[data] %d items, %d sentences" % (len(rows), len(sents)), flush=True)
    SP = spacy_parse(sents); FEp = frontend_parse(sents)

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

    def store_fallback(r):
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

    def objset(r, use_union, use_voice):
        vl = V1._lem(r["verb"])
        s = set(SP.get(r["sent"], {}).get(vl, {"obj": set()})["obj"])
        if use_union:
            s |= set(FEp.get(r["sent"], {}).get(vl, {"obj": set()})["obj"])
        if use_voice and r.get("voice") == "passive":
            s |= set(SP.get(r["sent"], {}).get(vl, {"subj": set()})["subj"])
            s |= set(FEp.get(r["sent"], {}).get(vl, {"subj": set()})["subj"])
        return s

    def tiebreak(hits, r):
        if len(hits) == 1:
            return hits[0][0]
        vi = r["verb_idx"]
        post = [(idx, h) for h, idx in hits if idx > vi]
        return (min(post)[1] if post else hits[0][0])

    def picker(use_union, use_voice, use_vtie, use_storegate):
        def pick(r):
            C = cands(r); s = objset(r, use_union, use_voice)
            hits = [(h, idx) for h, idx in C if in_set(h, s)]
            if len(hits) == 1:
                return hits[0][0]
            if len(hits) > 1:
                vi = r["verb_idx"]
                if use_vtie and r.get("voice") == "passive":       # passive patient = nearest PRE-verbal
                    pre = [(vi - idx, h) for h, idx in hits if idx < vi]
                    return (min(pre)[1] if pre else hits[0][0])
                post = [(idx, h) for h, idx in hits if idx > vi]    # active patient = nearest POST-verbal
                return (min(post)[1] if post else hits[0][0])
            return store_fallback(r) if use_storegate else r.get("pos_pick")
        return pick

    def one_parser_objset(r, which, use_voice):
        vl = V1._lem(r["verb"]); src = SP if which == "spacy" else FEp
        s = set(src.get(r["sent"], {}).get(vl, {"obj": set()})["obj"])
        if use_voice and r.get("voice") == "passive":
            s |= set(src.get(r["sent"], {}).get(vl, {"subj": set()})["subj"])
        return s

    def agreement_picker(defer_on_single):
        """AGREEMENT GATE (the negatives' signal = reliability-gate by PARSER AGREEMENT): if spaCy and the
        frontend parser AGREE on the object pick, trust it; if they DISAGREE (or, when defer_on_single, only
        one parser found it) that is low confidence -> defer to the register-native store."""
        def pick(r):
            C = cands(r)
            sp = [(h, idx) for h, idx in C if in_set(h, one_parser_objset(r, "spacy", True))]
            fe = [(h, idx) for h, idx in C if in_set(h, one_parser_objset(r, "frontend", True))]
            if sp and fe:
                p1, p2 = tiebreak(sp, r), tiebreak(fe, r)
                return p1 if p1 == p2 else store_fallback(r)      # agree -> trust; disagree -> store
            if sp or fe:
                return store_fallback(r) if defer_on_single else tiebreak(sp or fe, r)
            return store_fallback(r)                              # neither -> store
        return pick

    def nonrev(r):
        return sum(1 for h, _ in cands(r) if anim(h)) < 2
    FULL = [r for r in rows if len(cands(r)) >= 2 and nonrev(r)]
    HARD = [r for r in FULL if (r.get("voice") == "passive" or r.get("noncanonical"))]

    arms = [
        ("BASE STRUCT (spaCy obj, pos backoff)", picker(False, False, False, False)),
        ("+UNION (spaCy|frontend obj)", picker(True, False, False, False)),
        ("+VOICE (passive subj = patient)", picker(True, True, False, False)),
        ("+STOREGATE (store on parse-fail) = OPTIMIZED", picker(True, True, False, True)),
        ("AGREEMENT-GATE (store on parser DISAGREE)", agreement_picker(False)),
        ("AGREEMENT-GATE+ (store on disagree OR single-parser)", agreement_picker(True)),
        ("[ablation] +VTIE voice-aware tiebreak (HURTS)", picker(True, True, True, True)),
    ]
    base = arms[0][1]
    def acc(fn, S):
        return round(sum(1 for r in S if fn(r) == r["gold_head"]) / len(S), 4) if S else 0.0
    res = {"n_FULL": len(FULL), "n_HARD": len(HARD), "arms": {}}
    prev = None
    print("\n=== OPTIMIZED who-did-what (each fix stacked; delta = vs previous row) ===", flush=True)
    for name, fn in arms:
        aF = acc(fn, FULL); aH = acc(fn, HARD)
        dprev = V1.paired_delta(FULL, fn, prev, args.nboot) if prev is not None else None
        dbase = V1.paired_delta(FULL, fn, base, args.nboot)
        res["arms"][name] = {"FULL": aF, "HARD": aH,
                             "vs_prev_FULL": ({k: dprev[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")} if dprev else None),
                             "vs_BASE_FULL": {k: dbase[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")}}
        dp = ("d_prev %+.4f f<=0=%.2f" % (dprev["delta"], dprev["frac_le_0"])) if dprev else "(base)"
        print("  %-46s FULL=%.4f HARD=%.4f  %s  [vs BASE %+.4f]" % (name, aF, aH, dp, dbase["delta"]), flush=True)
        prev = fn

    out_name = "metrics.json" if args.pop == "qa" else ("metrics_%s.json" % args.pop)
    with open(os.path.join(OUT_DIR, out_name), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "optimized_who_did_what_v1", "pop": args.pop, "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
