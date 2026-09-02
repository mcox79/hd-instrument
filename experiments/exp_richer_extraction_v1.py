"""exp_richer_extraction_v1 -- PROTOTYPE a richer role extraction for who-did-what, following the
`situation_model_has_no_mutable_world_state_register` template (owner: "use what they did as an example of
how to prototype a parser that would benefit you too").

THEIR MOVE (that worked): the stock extractor returned only subject/object; they extracted the role the rule
IGNORED (the recipient PP) off the EXISTING parse -> recipient recovery 0 -> 0.33, "no new parser, just the
frame role + the existing parse." MY blind spot is identical: the STRUCT cue reads only the DIRECT OBJECT /
passive subject as the patient, and BACKS OFF to position whenever the patient is realized as a PP-object or
oblique ("sprayed paint ON the wall", dative shift, "the truck was loaded WITH hay").

THIS CELL:
 1. DIAGNOSTIC (the ceiling of richer extraction): for each held-out who-did-what item, WHERE does the gold
    patient sit in the parse? -- the verb's OBJECT (STRUCT already gets it), an OBLIQUE / PP-object of the verb
    (RICH extraction would get it), some OTHER argument, or NOT a verb argument at all (parse failure).
 2. ARMS: POS ; STRUCT (obj/passive-subj only) ; RICH (obj + oblique/PP-object + dative) ; RICH+SEL (when RICH
    yields >1 candidate, disambiguate with THIS project's register-native selectional store -- the parser
    finds the ARGUMENTS, the store picks WHICH is the patient). Driven by spaCy en_core_web_sm (the better
    parser from the headroom test) on modern QA-science.
 3. Reports accuracy on FULL / HARD + RICH_vs_STRUCT and RICHSEL_vs_RICH CI-separated.

spaCy is a glass-box statistical parser (NOT an LLM). Reuses the register-native store (exp_register_native_
store_v1) + FHRR codec. ASCII. Writes only to its own dir.
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
OUT_DIR = get_output_dir("exp_richer_extraction_v1")


def anim(w):
    a = lookup_animacy(w)
    return isinstance(a, dict) and (a.get("animacy") == "animate" or a.get("category") in ("person", "animal"))


def extract(sents):
    """spaCy parse -> {sent: {verb_lemma: {'obj': set, 'rich': set}}}. obj = direct object / passive subject;
    rich = obj + oblique/PP-object + dative + object-predicate (the roles the obj-only rule ignores)."""
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    out = {}
    t0 = time.time()
    for k, doc in enumerate(nlp.pipe(sents, batch_size=64)):
        d = defaultdict(lambda: {"obj": set(), "rich": set()})
        for tok in doc:
            hd = tok.head
            # direct object / passive subject / dative / object-predicate directly under a verb
            if hd.pos_ == "VERB":
                vl = V1._lem(hd.lemma_.lower())
                forms = {tok.lemma_.lower(), tok.text.lower()}
                if tok.dep_ in ("dobj", "nsubjpass"):
                    d[vl]["obj"] |= forms; d[vl]["rich"] |= forms
                elif tok.dep_ in ("dative", "oprd", "attr", "iobj"):
                    d[vl]["rich"] |= forms
            # PP-object: verb -> prep -> pobj  (the oblique/PP theme the obj-rule misses)
            if tok.dep_ == "pobj" and hd.dep_ == "prep" and hd.head.pos_ == "VERB":
                vl = V1._lem(hd.head.lemma_.lower())
                d[vl]["rich"] |= {tok.lemma_.lower(), tok.text.lower()}
        out[sents[k]] = d
        if (k + 1) % 1000 == 0:
            print("[spacy] %d/%d %.0fs" % (k + 1, len(sents), time.time() - t0), flush=True)
    return out


def cands(r, gv=None):
    out = []
    for h, idx in zip(r["cand_heads"], r["cand_idx"]):
        if h in V1.STOP or len(h) < 3:
            continue
        if gv is not None and gv.get(h) is None:
            continue
        out.append((h, idx))
    return out


def in_set(h, s):
    return V1._lem(h) in s or h in s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nboot", type=int, default=2000)
    ap.add_argument("--tokens", type=int, default=1_200_000)
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)

    rows = V1.load_pop(V1.QA)
    sents = sorted({r["sent"] for r in rows})
    print("[data] %d items, %d sentences" % (len(rows), len(sents)), flush=True)
    P = extract(sents)

    # register-native selectional store (this project's deliverable) for the RICH+SEL disambiguation
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

    def verb_sets(r):
        return P.get(r["sent"], {}).get(V1._lem(r["verb"]), {"obj": set(), "rich": set()})

    def sel_among(r, cand_heads):
        """pick among cand_heads by FHRR selectional recognition against the verb's stored events (agent-marg)."""
        toks = fhrr.get(V1._lem(r["verb"]))
        C = [(h, idx) for h, idx in cands(r) if h in cand_heads and gv.get(h) is not None]
        if toks is None or len(C) < 1:
            return cand_heads[0] if cand_heads else None
        if len(C) == 1:
            return C[0][0]
        allc = [(h, idx) for h, idx in cands(r) if gv.get(h) is not None]
        best = None; bs = -1e9
        for h, idx in C:
            s = 0.0
            for a, aidx in allc:
                if a == h:
                    continue
                q = F.quantize(binding.bind(A, enc_c(a)) + binding.bind(Pk, enc_c(h)))
                s += max(0.0, F.recognition(q, toks))
            if s > bs:
                bs = s; best = h
        return best

    # ---- arms ----
    def pos_pick(r):
        return r.get("pos_pick")

    def struct_pick(r):
        vs = verb_sets(r); C = cands(r)
        hits = [h for h, idx in C if in_set(h, vs["obj"])]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            vi = r["verb_idx"]; post = [(idx, h) for h, idx in C if in_set(h, vs["obj"]) and idx > vi]
            return min(post)[1] if post else hits[0]
        return r.get("pos_pick")

    def rich_pick(r):
        vs = verb_sets(r); C = cands(r)
        hits = [h for h, idx in C if in_set(h, vs["rich"])]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            vi = r["verb_idx"]; post = [(idx, h) for h, idx in C if in_set(h, vs["rich"]) and idx > vi]
            return min(post)[1] if post else hits[0]
        return r.get("pos_pick")

    def richsel_pick(r):
        vs = verb_sets(r); C = cands(r)
        hits = [h for h, idx in C if in_set(h, vs["rich"])]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            return sel_among(r, hits)          # parser found the arguments; the store picks which is patient
        return r.get("pos_pick")

    # ---- populations ----
    def nonrev(r):
        return sum(1 for h, _ in cands(r) if anim(h)) < 2
    FULL = [r for r in rows if len(cands(r)) >= 2 and nonrev(r)]
    HARD = [r for r in FULL if (r.get("voice") == "passive" or r.get("noncanonical"))]

    # ---- DIAGNOSTIC: where does the gold patient sit in the parse? ----
    diag = Counter()
    for r in FULL:
        vs = verb_sets(r); g = r["gold_head"]
        if in_set(g, vs["obj"]):
            diag["gold_is_OBJECT (STRUCT gets it)"] += 1
        elif in_set(g, vs["rich"]):
            diag["gold_is_OBLIQUE/PP (RICH gets it)"] += 1
        else:
            diag["gold_NOT_a_verb_arg (parse miss / accuracy)"] += 1
    nF = len(FULL)
    print("\n=== DIAGNOSTIC: where is the gold patient (FULL n=%d) ===" % nF, flush=True)
    for k, v in diag.most_common():
        print("  %-45s %4d (%.1f%%)" % (k, v, 100 * v / nF), flush=True)

    # ---- accuracy ----
    arms = {"POS": pos_pick, "STRUCT (obj only)": struct_pick, "RICH (obj+oblique/PP)": rich_pick,
            "RICH+SEL (store disambiguates)": richsel_pick}
    def acc(fn, S):
        return round(sum(1 for r in S if fn(r) == r["gold_head"]) / len(S), 4) if S else 0.0
    res = {"diag": dict(diag), "n_FULL": len(FULL), "n_HARD": len(HARD), "acc": {}, "deltas": {}}
    for tag, S in (("FULL", FULL), ("HARD", HARD)):
        res["acc"][tag] = {a: acc(f, S) for a, f in arms.items()}
        res["deltas"][tag] = {
            "RICH_vs_STRUCT": {k: V1.paired_delta(S, rich_pick, struct_pick, args.nboot)[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")},
            "RICHSEL_vs_RICH": {k: V1.paired_delta(S, richsel_pick, rich_pick, args.nboot)[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")},
            "RICHSEL_vs_STRUCT": {k: V1.paired_delta(S, richsel_pick, struct_pick, args.nboot)[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")},
        }
        print("\n=== QA/%s (n=%d) ===" % (tag, len(S)), flush=True)
        for a in ("POS", "STRUCT (obj only)", "RICH (obj+oblique/PP)", "RICH+SEL (store disambiguates)"):
            print("  %-34s acc=%.4f" % (a, res["acc"][tag][a]), flush=True)
        for lbl, d in res["deltas"][tag].items():
            print("    %-20s d=%+.4f CI[%+.4f,%+.4f] frac<=0=%.3f" % (lbl, d["delta"], d["ci_lo"], d["ci_hi"], d["frac_le_0"]), flush=True)

    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "richer_extraction_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
