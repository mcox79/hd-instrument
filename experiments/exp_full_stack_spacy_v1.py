"""exp_full_stack_spacy_v1 -- the FULL brain-foundational stack on the BETTER parser (owner: "what if you use
all the brain-foundational ones AND the better parser you used before?"). Prior best was spaCy-syntactic +
register-native store via convergent_cue_reader = 0.658. This ADDS the organs not yet stacked on spaCy:
`conceptual_meaning` (ATL taxonomic identity cue #8) as a THIRD cue, and `predictive_reader` precision (#4),
combined by the convergent Bayesian rule (sum of precision-weighted log-posteriors -- the 3-cue extension of
convergent_pick).

CUES (all owner-DONE organs + this problem's store):
  SYN   spaCy en_core_web_sm grammatical object / passive-subject (the better parser)   -> per-candidate
  SEL   register-native FHRR joint event store (associative/distributional thematic fit) -> per-candidate
  CONC  conceptual_meaning.ConceptualChannel: candidate's TAXONOMIC similarity to the verb's stored patients
        (ATL identity; complementary to SEL's associative fit)                           -> per-candidate
  precision refinement: predictive_reader.precision(verb, PATIENT) up-weights SEL/CONC for sharp verbs.
Integration: argmax_c [ log softmax(SYN/tau) + wS*log softmax(SEL/tau) + wC*log softmax(CONC/tau) ] (Bayes /
convergent). Measured on modern QA-science FULL/HARD. Glass-box parsers, no LLM. ASCII.
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
from hdlab import convergent_cue_reader as CC
from hdlab.conceptual_meaning import ConceptualChannel
from hdlab.predictive_reader import PredictiveReader

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_full_stack_spacy_v1")
_EPS = 1e-9


def anim(w):
    a = lookup_animacy(w)
    return isinstance(a, dict) and (a.get("animacy") == "animate" or a.get("category") in ("person", "animal"))


def spacy_obj(sents):
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


def cands(r):
    return [(h, idx) for h, idx in zip(r["cand_heads"], r["cand_idx"]) if h not in V1.STOP and len(h) >= 3]


def in_set(h, s):
    return V1._lem(h) in s or h in s


def _sm(x, tau):
    x = np.asarray(x, float) / max(tau, _EPS); x = x - x.max()
    e = np.exp(x); return e / (e.sum() + _EPS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nboot", type=int, default=3000)
    ap.add_argument("--tokens", type=int, default=1_200_000)
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    rows = V1.load_pop(V1.QA)
    sents = sorted({r["sent"] for r in rows})
    print("[data] %d items %d sentences" % (len(rows), len(sents)), flush=True)
    SP = spacy_obj(sents)

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

    # verb -> top stored patients (for the CONCEPTUAL taxonomic cue) + PredictiveReader
    byv = defaultdict(Counter)
    for v, o in parsed["verb_obj"]:
        byv[v][o] += 1
    verb_pats = {v: [p for p, _ in c.most_common(30)] for v, c in byv.items()}
    predictor = PredictiveReader().fit([(v, "PATIENT", o) for v, o in parsed["verb_obj"]])
    CONC = ConceptualChannel()
    cvec = {}
    def conc_vec(w):
        if w not in cvec:
            cvec[w] = CONC.vec(w, "N")
        return cvec[w]
    def conc_sim(a, b):
        from hdlab.conceptual_meaning import _sparse_cos
        va, vb = conc_vec(a), conc_vec(b)
        s = _sparse_cos(va, vb) if (va is not None and vb is not None) else None
        return 0.0 if s is None else float(s)

    def objset(r):
        vl = V1._lem(r["verb"]); d = SP.get(r["sent"], {}).get(vl, {"obj": set(), "subj": set()})
        s = set(d["obj"])
        if r.get("voice") == "passive":
            s |= set(d["subj"])
        return s

    def nonrev(r):
        return sum(1 for h, _ in cands(r) if anim(h)) < 2
    FULL = [r for r in rows if len(cands(r)) >= 2 and nonrev(r)]
    HARD = [r for r in FULL if (r.get("voice") == "passive" or r.get("noncanonical"))]

    # precompute the three cue arrays per item
    PRE = {}
    for r in FULL:
        C = cands(r); vi = r["verb_idx"]; vl = V1._lem(r["verb"])
        objs = objset(r)
        syn = [(1.0 if in_set(h, objs) else 0.0) + (0.5 if idx > vi else 0.0) for h, idx in C]
        toks = fhrr.get(vl); sel = None
        if toks is not None:
            arr = []; have = False
            for h, idx in C:
                if gv.get(h) is None:
                    arr.append(0.0); continue
                s = 0.0
                for a2, aidx in C:
                    if a2 == h or gv.get(a2) is None:
                        continue
                    q = F.quantize(binding.bind(A, enc_c(a2)) + binding.bind(Pk, enc_c(h)))
                    s += max(0.0, F.recognition(q, toks))
                arr.append(s); have = True
            sel = arr if have else None
        pats = verb_pats.get(vl, [])
        conc = None
        if pats:
            conc = [max((conc_sim(h, p) for p in pats), default=0.0) for h, idx in C]
            if not any(conc):
                conc = None
        prec = predictor.precision(vl, "PATIENT")
        PRE[id(r)] = (C, syn, sel, conc, prec)
    TAU_SYN = CC.calibrate_tau([PRE[id(r)][1] for r in FULL])
    TAU_SEL = CC.calibrate_tau([PRE[id(r)][2] for r in FULL if PRE[id(r)][2] is not None])
    TAU_CON = CC.calibrate_tau([PRE[id(r)][3] for r in FULL if PRE[id(r)][3] is not None])
    nconc = sum(1 for r in FULL if PRE[id(r)][3] is not None)
    print("[cues] tau_syn=%.3f tau_sel=%.3f tau_con=%.3f | conceptual covers %d/%d items" %
          (TAU_SYN, TAU_SEL, TAU_CON, nconc, len(FULL)), flush=True)

    def pick3(wS, wC, use_prec):
        def pick(r):
            v = PRE.get(id(r))
            if v is None or len(v[0]) < 2:
                return r.get("pos_pick")
            C, syn, sel, conc, prec = v
            lp = np.log(_sm(syn, TAU_SYN) + 1e-12)
            ws, wc = wS, wC
            if use_prec and prec is not None:
                f = 0.5 + prec; ws *= f; wc *= f       # sharp verb -> up-weight selectional/taxonomic
            if sel is not None:
                lp = lp + ws * np.log(_sm(sel, TAU_SEL) + 1e-12)
            if conc is not None:
                lp = lp + wc * np.log(_sm(conc, TAU_CON) + 1e-12)
            return C[int(np.argmax(lp))][0]
        return pick

    def acc(fn, S):
        return round(sum(1 for r in S if fn(r) == r["gold_head"]) / len(S), 4) if S else 0.0
    ref = pick3(1.0, 0.0, False)   # syn+sel only (= prior best 0.658)
    arms = [
        ("2-cue syn+SEL (prior best 0.658)", pick3(1.0, 0.0, False)),
        ("3-cue syn+SEL+CONC (wC=1.0)", pick3(1.0, 1.0, False)),
        ("3-cue syn+SEL+CONC (wC=0.5)", pick3(1.0, 0.5, False)),
        ("3-cue + predictive precision (#4)", pick3(1.0, 0.5, True)),
        ("syn+CONC only (no store)", pick3(0.0, 1.0, False)),
    ]
    res = {"n_FULL": len(FULL), "n_HARD": len(HARD), "n_conc_cov": nconc, "arms": {}}
    print("\n=== FULL STACK on the BETTER parser (spaCy) + all brain-foundational cues ===", flush=True)
    for name, fn in arms:
        aF = acc(fn, FULL); aH = acc(fn, HARD)
        d = V1.paired_delta(FULL, fn, ref, args.nboot)
        res["arms"][name] = {"FULL": aF, "HARD": aH, "vs_2cue_FULL": {k: d[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")}}
        print("  %-40s FULL=%.4f HARD=%.4f  [vs 2-cue %+.4f f<=0=%.2f]" % (name, aF, aH, d["delta"], d["frac_le_0"]), flush=True)

    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "full_stack_spacy_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
