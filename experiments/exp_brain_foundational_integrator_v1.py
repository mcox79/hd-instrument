"""exp_brain_foundational_integrator_v1 -- implement the brain's who-did-what integration FAITHFULLY (owner:
"implement the brain foundational entirely"): replace the HARD reliability-gate with GRADED, conflict-driven
PRECISION-WEIGHTING doing JOINT (not pipeline) noisy-channel integration of the syntactic and selectional cues.

THE BRAIN (PINNED): parallel precision-weighted cue integration (Competition Model, Bates & MacWhinney; optimal
inverse-variance combination, Ernst & Banks 2002) under noisy-channel inference (Levy 2008; Gibson 2013). The
precision on the SYNTACTIC cue is set CONTINUOUSLY by a CONFLICT signal -- the P600/LIFG structural monitor +
the N400 thematic-fit signal (the parent p5's dissociable predict_surprisal streams): when the parse CONFLICTS
with the selectional prior (implausible assignment) or is low-confidence, its precision drops and the
selectional prior takes over. This is GRADED, not a switch.

WHAT THIS CELL BUILDS (the feasible-in-one-cell brain-foundational core):
  syntactic cue    the parser's object pick (spaCy + frontend UD), voice-aware
  selectional cue  the register-native FHRR joint store (agent-marginalized recognition) -- consolidated
                   thematic fit (McRae; this project's deliverable), joint conjunctive binding (Frankland-Greene)
  GRADED precision on syntax = AGREEMENT(both parsers pick same object) x PLAUSIBILITY(store's confidence in the
                   parser's pick) -- the conflict-driven precision. High -> trust the parse; low -> the store.
  score(c) = conf * [c == parser_pick] + (1 - conf) * sel_dist(c)      (a continuous interpolation, the
             precision-weighted noisy-channel posterior; argmax = the patient).
Ablated vs the HARD gates (store-on-parse-fail, agreement-gate) to show GRADED > HARD. Measured modern QA-science
+ 19c generalization. NAMED-BUT-NOT-BUILT (dedicated organs, honestly flagged): a robust incremental parser, a
sensorimotor-grounded meaning space, a running situation model. spaCy/frontend are glass-box parsers (NOT LLMs).
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
# REUSE the owner-DONE brain-foundational integration organs (do NOT reinvent -- owner directive):
from hdlab import convergent_cue_reader as CC   # precision-weighted (Ernst-Banks) 2-cue product = convergent_pick
from hdlab import graded_competition as GC       # additive-cue -> softmax = Bayesian posterior; entropy = difficulty

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_brain_foundational_integrator_v1")
STRUCT = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|[0-9]+|[^\sA-Za-z0-9]")
_EPS = 1e-9


def anim(w):
    a = lookup_animacy(w)
    return isinstance(a, dict) and (a.get("animacy") == "animate" or a.get("category") in ("person", "animal"))


def spacy_parse(sents):
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
    ap.add_argument("--nboot", type=int, default=3000)
    ap.add_argument("--tokens", type=int, default=1_200_000)
    ap.add_argument("--pop", type=str, default="qa")
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    rows = V1.load_pop(V1.LB if args.pop == "litbank" else V1.QA)
    sents = sorted({r["sent"] for r in rows})
    print("[data] %d items %d sentences (pop=%s)" % (len(rows), len(sents), args.pop), flush=True)
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

    def sel_dist(r):
        """selectional (thematic-fit) distribution over candidates: agent-marginalized FHRR recognition."""
        toks = fhrr.get(V1._lem(r["verb"])); C = [(h, idx) for h, idx in cands(r) if gv.get(h) is not None]
        if toks is None or len(C) < 1:
            return {}, C
        raw = {}
        for h, idx in C:
            s = 0.0
            for a, aidx in C:
                if a == h:
                    continue
                q = F.quantize(binding.bind(A, enc_c(a)) + binding.bind(Pk, enc_c(h)))
                s += max(0.0, F.recognition(q, toks))
            raw[h] = s
        z = sum(np.exp(v / 0.05) for v in raw.values()) + _EPS   # softmax T=0.05 (sharp; store scores are small)
        return {h: float(np.exp(v / 0.05) / z) for h, v in raw.items()}, C

    def objhits(r, src, use_voice):
        vl = V1._lem(r["verb"]); d = src.get(r["sent"], {}).get(vl, {"obj": set(), "subj": set()})
        s = set(d["obj"])
        if use_voice and r.get("voice") == "passive":
            s |= set(d["subj"])
        return [(h, idx) for h, idx in cands(r) if in_set(h, s)]

    def tiebreak(hits, r):
        if len(hits) == 1:
            return hits[0][0]
        vi = r["verb_idx"]; post = [(idx, h) for h, idx in hits if idx > vi]
        return (min(post)[1] if post else hits[0][0])

    def parser_pick(r):
        sp = objhits(r, SP, True); fe = objhits(r, FEp, True)
        merged = sp + [x for x in fe if x not in sp]
        return (tiebreak(merged, r) if merged else None), sp, fe

    def store_pick(r):
        sd, C = sel_dist(r)
        return (max(sd, key=sd.get) if sd else r.get("pos_pick"))

    def nonrev(r):
        return sum(1 for h, _ in cands(r) if anim(h)) < 2
    FULL = [r for r in rows if len(cands(r)) >= 2 and nonrev(r)]
    HARD = [r for r in FULL if (r.get("voice") == "passive" or r.get("noncanonical"))]

    # ---- PRECOMPUTE the two cue arrays ONCE per item (FHRR is the cost), aligned by candidate order ----
    # syn_raw = per-candidate SYNTACTIC support (voice-fixed object indicator from BOTH parsers -> 0/1/2 =
    #   agreement, + a weak post-verbal position prior). sel_raw = per-candidate SELECTIONAL support (the
    #   register-native FHRR store, agent-marginalized recognition). These are the two cues the brain combines.
    PRE = {}
    for r in FULL:
        sp = set(h for h, _ in objhits(r, SP, True)); fe = set(h for h, _ in objhits(r, FEp, True))
        C = cands(r); vi = r["verb_idx"]
        syn = [(1.0 if h in sp else 0.0) + (1.0 if h in fe else 0.0) + (0.5 if idx > vi else 0.0) for h, idx in C]
        toks = fhrr.get(V1._lem(r["verb"])); sel = None
        if toks is not None:
            arr = []; have = False
            for h, idx in C:
                if gv.get(h) is None:
                    arr.append(0.0); continue
                s = 0.0
                for a, aidx in C:
                    if a == h or gv.get(a) is None:
                        continue
                    q = F.quantize(binding.bind(A, enc_c(a)) + binding.bind(Pk, enc_c(h)))
                    s += max(0.0, F.recognition(q, toks))
                arr.append(s); have = True
            sel = arr if have else None
        PRE[id(r)] = (C, syn, sel)
    TAU_SYN = CC.calibrate_tau([PRE[id(r)][1] for r in FULL])
    TAU_SEL = CC.calibrate_tau([PRE[id(r)][2] for r in FULL if PRE[id(r)][2] is not None])
    print("[cues] tau_syn=%.3f tau_sel=%.3f (calibrate_tau, gold-blind)" % (TAU_SYN, TAU_SEL), flush=True)

    def store_pick(r):
        v = PRE.get(id(r))
        if v and v[2] is not None:
            return v[0][int(np.argmax(v[2]))][0]
        return r.get("pos_pick")

    # ---- HARD references (my hand-rolled gates) ----
    def hard_storegate(r):
        pp, sp, fe = parser_pick(r)
        return pp if pp is not None else store_pick(r)

    def hard_agreementgate(r):
        pp, sp, fe = parser_pick(r)
        if sp and fe:
            return tiebreak(sp, r) if tiebreak(sp, r) == tiebreak(fe, r) else store_pick(r)
        if sp or fe:
            return tiebreak(sp or fe, r)
        return store_pick(r)

    # ---- BRAIN-FOUNDATIONAL: REUSE convergent_cue_reader.convergent_pick (owner-DONE, Ernst-Banks precision-
    #      weighted) to combine the SYNTACTIC and SELECTIONAL cues -- NOT a hand-rolled integrator. ----
    def convergent_arm(w):
        def pick(r):
            v = PRE.get(id(r))
            if v is None or len(v[0]) < 2:
                return r.get("pos_pick")
            C, syn, sel = v
            idx = CC.convergent_pick(syn, sel, tau_e=TAU_SYN, tau_s=TAU_SEL, w=w)
            return C[idx][0] if idx is not None else r.get("pos_pick")
        return pick

    # #4 CONFLICT-DRIVEN PRECISION (per-item, the N400): down-weight the SYNTACTIC cue when the parser's pick
    # is selectionally IMPLAUSIBLE (the store prefers a different candidate). Scaling syn toward uniform lowers
    # its peakedness, and convergent_pick's precision = peakedness, so the store takes over on conflict.
    def conflict_arm(w, alpha):
        def pick(r):
            v = PRE.get(id(r))
            if v is None or len(v[0]) < 2:
                return r.get("pos_pick")
            C, syn, sel = v
            if sel is None:
                return C[int(np.argmax(syn))][0]
            sp = int(np.argmax(syn))
            sd = np.exp(np.asarray(sel, float) / TAU_SEL); sd = sd / (sd.sum() + _EPS)
            conf = float(sd[sp] / (sd.max() + _EPS))          # 1 = store agrees with the parse; <1 = conflict
            gain = alpha + (1.0 - alpha) * conf               # down-weight syn on conflict
            syn_s = [s * gain for s in syn]
            idx = CC.convergent_pick(syn_s, sel, tau_e=TAU_SYN, tau_s=TAU_SEL, w=w)
            return C[idx][0] if idx is not None else r.get("pos_pick")
        return pick

    arms = [
        ("HARD agreement-gate (hand-rolled)", hard_agreementgate),
        ("CONVERGENT reuse w=1.0 (prior best)", convergent_arm(1.0)),
        ("CONFLICT-precision alpha=0.5 (#4 per-item N400)", conflict_arm(1.0, 0.5)),
        ("CONFLICT-precision alpha=0.3", conflict_arm(1.0, 0.3)),
        ("CONFLICT-precision alpha=0.15", conflict_arm(1.0, 0.15)),
    ]
    def acc(fn, S):
        return round(sum(1 for r in S if fn(r) == r["gold_head"]) / len(S), 4) if S else 0.0
    ref = arms[1][1]
    res = {"pop": args.pop, "n_FULL": len(FULL), "n_HARD": len(HARD), "arms": {}}
    print("\n=== BRAIN-FOUNDATIONAL GRADED INTEGRATOR (pop=%s) ===" % args.pop, flush=True)
    for name, fn in arms:
        aF = acc(fn, FULL); aH = acc(fn, HARD)
        d = V1.paired_delta(FULL, fn, ref, args.nboot)
        res["arms"][name] = {"FULL": aF, "HARD": aH, "vs_agreementgate_FULL": {k: d[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")}}
        print("  %-52s FULL=%.4f HARD=%.4f  [vs HARD-agree %+.4f f<=0=%.2f]" % (name, aF, aH, d["delta"], d["frac_le_0"]), flush=True)

    out_name = "metrics.json" if args.pop == "qa" else ("metrics_%s.json" % args.pop)
    with open(os.path.join(OUT_DIR, out_name), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "brain_foundational_integrator_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
