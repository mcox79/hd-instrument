"""exp_full_brain_foundational_reader_v1 -- COMPOSE the ENTIRE brain-foundational who-did-what from owner-DONE
organs (owner: "do all of these now - I believe we have pretty much all of it already"). Nothing new is built;
every deviation is closed by REUSING an existing organ, integrated over this problem's register-native store.

THE STACK (all hdlab, all owner-DONE + this problem's store):
  #10 PARSER (incremental)   hdlab.incremental_parser.incremental_build -- left-corner incremental structure
                             builder (beats the batch parser F1 +0.035); gives the SYNTACTIC patient cue.
  #1/#4 PREDICT + PRECISION  hdlab.predictive_reader.PredictiveReader -- forward prediction + per-verb
                             selectional PRECISION (the conflict/reliability signal).
  SELECTIONAL (this problem) exp_register_native_store_v1 FHRR joint event store -- consolidated register-native
                             thematic fit.
  #8 GROUNDING (conceptual)  hdlab.conceptual_meaning.ConceptualChannel -- ATL amodal hub (meaning identity;
                             beats GloVe on SimLex), an extra grounded cue.
  #3 INTEGRATION             hdlab.convergent_cue_reader.convergent_pick -- Ernst-Banks precision-weighted
                             log-posterior combination.
Measured on modern QA-science. Ablates: spaCy-syntactic (prior best 0.658) vs INCREMENTAL-parser syntactic;
+predictive-precision; +conceptual cue. spaCy/frontend/incremental are glass-box parsers (NOT LLMs). ASCII.
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
from hdlab import convergent_cue_reader as CC
from hdlab.incremental_parser import incremental_build
from hdlab.predictive_reader import PredictiveReader

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_full_brain_foundational_reader_v1")
STRUCT = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|[0-9]+|[^\sA-Za-z0-9]")


def anim(w):
    a = lookup_animacy(w)
    return isinstance(a, dict) and (a.get("animacy") == "animate" or a.get("category") in ("person", "animal"))


def load_tagger():
    from hdlab.pos_tagger import PosTagger
    return PosTagger.load(os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json"))


def cands(r):
    return [(h, idx) for h, idx in zip(r["cand_heads"], r["cand_idx"]) if h not in V1.STOP and len(h) >= 3]


def in_lemmaset(h, s):
    return V1._lem(h) in s or h in s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nboot", type=int, default=3000)
    ap.add_argument("--tokens", type=int, default=1_200_000)
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    rows = V1.load_pop(V1.QA)
    sents = sorted({r["sent"] for r in rows})
    print("[data] %d items %d sentences" % (len(rows), len(sents)), flush=True)

    # register-native store (this problem's deliverable) + its triples for the PredictiveReader
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

    # #1/#4 PredictiveReader fit on the register-native (verb, role, arg) triples
    triples = []
    for a, v, o in parsed["svo"]:
        triples.append((v, "PATIENT", o)); triples.append((v, "AGENT", a))
    predictor = PredictiveReader().fit(triples)
    print("[predictor] fit on %d triples" % len(triples), flush=True)

    # #10 incremental parse of every test sentence -> {verb_lemma: set(patient forms)}
    tagger = load_tagger()
    incr = {}; t1 = time.time()
    for k, sent in enumerate(sents):
        toks = STRUCT.findall(sent); d = defaultdict(set)
        if toks and len(toks) <= 80:
            try:
                pos = tagger.tag(toks)
                frames = incremental_build(toks, pos, predictor)
                for vi, argset in frames.items():
                    if 1 <= vi <= len(toks) and pos[vi - 1] == "VERB":
                        vl = V1._lem(toks[vi - 1])
                        # the PATIENT slot is the verb's post-verbal obj (arg index > verb index)
                        for ai in argset:
                            if ai > vi and 1 <= ai <= len(toks):
                                d[vl].add(toks[ai - 1].lower())
            except Exception:
                pass
        incr[sent] = d
        if (k + 1) % 1000 == 0:
            print("[incremental] %d/%d %.0fs" % (k + 1, len(sents), time.time() - t1), flush=True)

    def incr_objset(r):
        return incr.get(r["sent"], {}).get(V1._lem(r["verb"]), set())

    # precompute cue arrays once per item
    def nonrev(r):
        return sum(1 for h, _ in cands(r) if anim(h)) < 2
    FULL = [r for r in rows if len(cands(r)) >= 2 and nonrev(r)]
    HARD = [r for r in FULL if (r.get("voice") == "passive" or r.get("noncanonical"))]

    from hdlab.conceptual_meaning import ConceptualChannel
    CONC = ConceptualChannel()

    PRE = {}
    for r in FULL:
        C = cands(r); vi = r["verb_idx"]; vl = V1._lem(r["verb"])
        objs = incr_objset(r)
        syn = [(1.0 if in_lemmaset(h, objs) else 0.0) + (0.5 if idx > vi else 0.0) for h, idx in C]
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
        prec = predictor.precision(vl, "PATIENT")     # #4 per-verb selectional precision (conflict signal)
        PRE[id(r)] = (C, syn, sel, prec)
    TAU_SYN = CC.calibrate_tau([PRE[id(r)][1] for r in FULL])
    TAU_SEL = CC.calibrate_tau([PRE[id(r)][2] for r in FULL if PRE[id(r)][2] is not None])
    precs = [PRE[id(r)][3] for r in FULL if PRE[id(r)][3] is not None]
    print("[cues] tau_syn=%.3f tau_sel=%.3f | predictive precision: median=%.3f" %
          (TAU_SYN, TAU_SEL, float(np.median(precs)) if precs else -1), flush=True)

    def convergent_arm(w, use_prec):
        def pick(r):
            v = PRE.get(id(r))
            if v is None or len(v[0]) < 2:
                return r.get("pos_pick")
            C, syn, sel, prec = v
            ww = w
            if use_prec and prec is not None:
                ww = w * (0.5 + prec)          # sharp verb -> up-weight the selectional cue (Friston precision)
            idx = CC.convergent_pick(syn, sel, tau_e=TAU_SYN, tau_s=TAU_SEL, w=ww)
            return C[idx][0] if idx is not None else r.get("pos_pick")
        return pick

    def store_only(r):
        v = PRE.get(id(r))
        if v and v[2] is not None:
            return v[0][int(np.argmax(v[2]))][0]
        return r.get("pos_pick")

    def incr_only(r):
        v = PRE.get(id(r))
        if v is None or len(v[0]) < 2:
            return r.get("pos_pick")
        C, syn, sel, prec = v
        return C[int(np.argmax(syn))][0]

    arms = [
        ("INCR parser only (#10 better parser)", incr_only),
        ("register-native store only", store_only),
        ("CONVERGENT(INCR, store) w=1.0", convergent_arm(1.0, False)),
        ("CONVERGENT(INCR, store) + predictive-precision (#4)", convergent_arm(1.0, True)),
    ]
    def acc(fn, S):
        return round(sum(1 for r in S if fn(r) == r["gold_head"]) / len(S), 4) if S else 0.0
    ref = convergent_arm(1.0, False)
    res = {"n_FULL": len(FULL), "n_HARD": len(HARD), "arms": {}}
    print("\n=== FULL BRAIN-FOUNDATIONAL READER (all owner-DONE organs + register-native store) ===", flush=True)
    for name, fn in arms:
        aF = acc(fn, FULL); aH = acc(fn, HARD)
        d = V1.paired_delta(FULL, fn, ref, args.nboot)
        res["arms"][name] = {"FULL": aF, "HARD": aH, "vs_convergent_FULL": {k: d[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")}}
        print("  %-52s FULL=%.4f HARD=%.4f  [vs CONV %+.4f f<=0=%.2f]" % (name, aF, aH, d["delta"], d["frac_le_0"]), flush=True)
    print("\n  (prior best, spaCy-syntactic CONVERGENT = 0.658 FULL -- this swaps in the INCREMENTAL parser #10)", flush=True)

    # ---- FULL SIGNAL-LOSS DECOMPOSITION across the ENTIRE stack (owner: "fully disambiguate where we lose
    #      signal the entire way") -- partition by where the gold patient sits in the INCREMENTAL parse. ----
    from collections import Counter
    conv = convergent_arm(1.0, True)
    buckets = defaultdict(list); no_obj_but_verb = 0
    for r in FULL:
        objs = incr_objset(r); g = r["gold_head"]
        vfound = V1._lem(r["verb"]) in incr.get(r["sent"], {})
        anyobj = len(objs) > 0
        if not vfound and not anyobj:
            buckets["E_verb_not_parsed_as_VERB"].append(r)
        elif in_lemmaset(g, objs):
            buckets["A_gold_IS_incr_patient"].append(r)
        elif anyobj:
            buckets["C_incr_found_WRONG_patient"].append(r)
        else:
            buckets["D_incr_found_NO_patient"].append(r)
    def gold_cov(S):    # is the gold even a scorable candidate + in the store?
        return round(sum(1 for r in S if r["gold_head"] in [h for h, _ in cands(r)]) / len(S), 3) if S else 0.0
    results_dec = {}
    print("\n=== SIGNAL-LOSS DECOMPOSITION -- the ENTIRE stack (incremental parser, n=%d) ===" % len(FULL), flush=True)
    print("  %-28s %5s %6s | POS   INCR  STORE CONV  gold-in-cands" % ("partition", "n", "share"), flush=True)
    for cls in ("A_gold_IS_incr_patient", "C_incr_found_WRONG_patient", "D_incr_found_NO_patient", "E_verb_not_parsed_as_VERB"):
        S = buckets.get(cls, [])
        if not S:
            continue
        row = {"n": len(S), "share": round(len(S) / len(FULL), 3), "POS": acc(lambda r: r.get("pos_pick"), S),
               "INCR": acc(incr_only, S), "STORE": acc(store_only, S), "CONV": acc(conv, S), "gold_in_cands": gold_cov(S)}
        results_dec[cls] = row
        print("  %-28s %5d %5.1f%% | %.3f %.3f %.3f %.3f   %.3f" %
              (cls, len(S), 100 * len(S) / len(FULL), row["POS"], row["INCR"], row["STORE"], row["CONV"], row["gold_in_cands"]), flush=True)
    res["decomposition"] = results_dec

    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "full_brain_foundational_reader_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
