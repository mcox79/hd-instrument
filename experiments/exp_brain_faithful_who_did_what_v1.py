"""exp_brain_faithful_who_did_what_v1 -- build the brain's who-did-what mechanism EXACTLY (the 7 deviations
from exp_register_native_store_v1's brain-comparison), integrate them, and ABLATE each so we MEASURE which
mechanism actually raises the score (owner: "make this match the brain 1-7 ... this is how we get higher
scores"). The register-native store proved the DOMAIN signal lives in JOINT event structure; this cell asks
whether copying the REST of the brain's who-did-what operation raises accuracy toward the human ~0.83.

THE 7 BRAIN MECHANISMS (each an ablatable toggle):
  #1 JOINT NOISY-CHANNEL   parse is soft EVIDENCE, not a hard commit; cues integrated, parse down-weighted when
                           unreliable (Gibson 2013; Levy 2008; McRae 1998).
  #2 PARALLEL MULTI-CUE    word-order + selectional + animacy integrated in parallel, PRECISION-weighted,
                           construction-conditional (Competition Model, Bates & MacWhinney; Ernst & Banks 2002).
  #3 CLS (episodic+semantic) hippocampal EPISODIC FHRR retrieval + neocortical GENERATIVE generalization
                           (GroundedDistMult), UNCERTAINTY-gated arbitration (McClelland 1995; Lee/O'Doherty 2014).
  #4 ONLINE ADAPTATION     the generative store learns by prediction error over its reading (N400; Rabovsky 2018)
                           -- reported as a learning curve.
  #5 GROUNDED FILLERS      fillers grounded in the substrate's sensorimotor space (hdlab.grounded_similarity),
                           vs the distributional GloVe stand-in (ATL hub-and-spoke; Lambon Ralph).
  #6 PREDICT / PRE-ACTIVATE the cue is the verb+agent PRE-ACTIVATING the expected filler (Altmann & Kamide 1999),
                           not list-matching -- scored as predicted activation.
  #7 SITUATION-CONDITIONING the patient expectation is conditioned on the AGENT jointly (Bicknell 2010); the
                           full discourse-prominence variant (Wall B; graded_coref_pick) needs coref chains and
                           is validated on the LitBank animate slice (parent +0.156), N/A on inanimate QA-science.

Integration (#1,#2): log P(patient=j) = sum_cue precision_cue * log softmax(cue_j), precision = 1 - normalized
entropy of the cue (Ernst & Banks inverse-variance weighting), the POSITION cue's precision multiplied by a
construction-conditional beta that COLLAPSES on non-canonical order. Marginalize the joint (agent,patient) over
the agent; patient = argmax_j.

Reuses the register-native 1.2M SCIENCE store (exp_register_native_store_v1) + the FHRR codec (hdlab.binding) +
GroundedDistMult (exp_generative_event_model_v1) + hdlab.grounded_similarity + hdlab.animacy_lexicon. NO external
LLM. ASCII. Writes only to its own data dir.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse, json, math, sys, time
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
from experiments.exp_generative_event_model_v1 import GroundedDistMult
from hdlab import binding
from hdlab.situation_model_accumulate import unit_phase_vec
from hdlab.animacy_lexicon import lookup_animacy

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_brain_faithful_who_did_what_v1")
_EPS = 1e-9
TOK = 1_200_000
BETA_NONCANON = 0.15   # Competition Model: word-order cue precision COLLAPSES on non-canonical order (swept)


def make_enc(dim, seed=17):
    """grounded/distributional filler (dim-d) -> FHRR unit-phase hypervector (dim-agnostic version of
    F.make_encoder, so #5's grounded 12-d fillers get their OWN encoder, not the 300-d GloVe one)."""
    g = torch.Generator().manual_seed(seed)
    W = torch.randn(F.D, dim, generator=g, dtype=torch.float64) * 0.30

    def enc(gvec):
        x = torch.from_numpy(np.asarray(gvec, dtype=np.float64))
        x = x / (x.norm() + _EPS)
        return torch.exp(1j * (W @ x)).to(torch.complex64)
    return enc


def anim(w):
    a = lookup_animacy(w)
    return isinstance(a, dict) and (a.get("animacy") == "animate" or a.get("category") in ("person", "animal"))


def _grounded(w, _c={}):
    if w not in _c:
        from hdlab.grounded_similarity import grounded_vector
        v = grounded_vector(w)
        _c[w] = None if v is None else np.asarray(v, dtype=np.float64).reshape(-1)
    return _c[w]


# ------------------------------------------------------------------ cue distributions (per candidate j = patient)
def _softmax(x, T=1.0):
    x = np.asarray(x, dtype=np.float64) / max(T, _EPS)
    x = x - x.max()
    e = np.exp(x)
    return e / (e.sum() + _EPS)


def _precision(p):
    """cue reliability = 1 - normalized entropy (peaked cue -> high precision; flat -> ~0)."""
    p = np.asarray(p, dtype=np.float64) + _EPS
    H = -(p * np.log(p)).sum()
    Hmax = math.log(len(p))
    return float(1.0 - H / (Hmax + _EPS)) if len(p) > 1 else 0.0


def pos_scores(C, vi):
    """word-order cue: patient tends POST-verbal in canonical order. Per-candidate patient score."""
    return np.array([1.0 if idx > vi else 0.0 for _, idx, _ in C], dtype=np.float64)


def anim_scores(C):
    """animacy cue: the patient of a non-reversible event tends INANIMATE (agent animate)."""
    return np.array([0.0 if anim(h) else 1.0 for h, _, _ in C], dtype=np.float64)


def fhrr_patient_scores(C, toks, enc_c, A, P, soft_and=False):
    """episodic FHRR (#core,#6): pre-activation of patient j = sum over agent i of event recognition(a_i,v,p_j)."""
    n = len(C)
    s = np.zeros(n)
    if toks is None:
        return s
    if not soft_and:
        for ai in range(n):
            qa = binding.bind(A, enc_c(C[ai][0], C[ai][2]))
            for pj in range(n):
                if ai == pj:
                    continue
                q = F.quantize(qa + binding.bind(P, enc_c(C[pj][0], C[pj][2])))
                s[pj] += max(0.0, F.recognition(q, toks))
    else:
        am = [((binding.bind(A, enc_c(C[i][0], C[i][2]))).conj().unsqueeze(0) * toks).sum(1).real.clamp(min=0) / F.D for i in range(n)]
        pm = [((binding.bind(P, enc_c(C[i][0], C[i][2]))).conj().unsqueeze(0) * toks).sum(1).real.clamp(min=0) / F.D for i in range(n)]
        for pj in range(n):
            best = 0.0
            for ai in range(n):
                if ai == pj:
                    continue
                v = float((am[ai] * pm[pj]).max())
                if v > best:
                    best = v
            s[pj] = best
    return s


def gen_patient_scores(C, vl, vidx, model, Gmap):
    """neocortical generative (#3): GroundedDistMult pre-activation, marginalized over agent. Generalizes to
    unseen (agent,verb,patient) combinations."""
    n = len(C)
    s = np.zeros(n)
    vi = vidx.get(vl)
    if vi is None:
        return s
    with torch.no_grad():
        rv = model.R(torch.tensor(vi))
        embs = []
        for h, _, gvec in C:
            g = Gmap.get(h)
            embs.append(model.emb(torch.from_numpy(g.astype(np.float32)).unsqueeze(0))[0] if g is not None else None)
        for pj in range(n):
            if embs[pj] is None:
                continue
            best = 0.0
            for ai in range(n):
                if ai == pj or embs[ai] is None:
                    continue
                sc = float((embs[ai] * rv * embs[pj]).sum())
                if sc > best:
                    best = sc
            s[pj] = best
    return s


# ------------------------------------------------------------------ #PARSER: structural role cue (the lever)
_PARSER = None
_PARSE_CACHE = {}


def _load_parser():
    global _PARSER
    if _PARSER is None:
        from hdlab.pos_tagger import PosTagger
        from hdlab.arc_parser import ArcParser
        from hdlab.arc_labeler import ArcLabeler
        FE = os.path.join(_REPO, "data", "frontend_assets")
        _PARSER = (PosTagger.load(os.path.join(FE, "pos_tagger_ud_ewt_upos.json")),
                   ArcParser.load(os.path.join(FE, "arc_parser_richfeat_ud_ewt.npz")),
                   ArcLabeler.load(os.path.join(FE, "arc_labeler_hashed_ud_ewt.json")))
    return _PARSER


def struct_patient_scores(r, C):
    """PARSER cue (the lever): patient = the verb's grammatical OBJECT (obj/dobj) or PASSIVE SUBJECT
    (nsubj:pass), from a real frontend UD parse -- grammatical function + voice -> thematic role, NOT linear
    position. This is what the wired reader's role_route='positional' does NOT do."""
    from hdlab.reading_grounding_loop import normalize_lemma
    sent = r["sent"]
    if sent not in _PARSE_CACHE:
        tg, pr, lb = _load_parser()
        toks = E.STRUCT.findall(sent)
        try:
            pos = tg.tag(toks); heads = pr.parse(toks, pos).heads; labs = lb.label(toks, pos, heads)
            lem = [normalize_lemma(t) for t in toks]
            _PARSE_CACHE[sent] = (toks, heads, labs, pos, lem)
        except Exception:
            _PARSE_CACHE[sent] = None
    parsed = _PARSE_CACHE[sent]
    n = len(C); s = np.zeros(n)
    if parsed is None:
        return s
    toks, heads, labs, pos, lem = parsed
    vl = V1._lem(r["verb"]); N = len(toks)
    patients = set()
    for i in range(1, N + 1):
        rel = labs.get(i); h = heads.get(i, 0)
        if rel in E.OBJ and 1 <= h <= N and pos[h - 1] == "VERB" and V1._lem(lem[h - 1]) == vl:
            patients.add(lem[i - 1])
    for j, (h, idx, g) in enumerate(C):
        if V1._lem(h) in patients or h in patients:
            s[j] = 1.0
    return s


# ------------------------------------------------------------------ the integrated brain-faithful scorer
def make_scorer(cfg, spaces, A, P):
    """Returns pick(r) using the cues enabled in cfg (a set of mechanism tags). Precision-weighted
    noisy-channel integration, construction-conditional word-order weight, agent-marginalized. `spaces` maps
    'glove'/'grounded' -> {gv, enc, fhrr, model, vidx, Gmap}; #5 selects the grounded filler space."""
    sp = spaces["grounded" if "grounded" in cfg else "glove"]
    fhrr_store, vidx, model, Gmap, enc = sp["fhrr"], sp["vidx"], sp["model"], sp["Gmap"], sp["enc"]
    ecache = {}

    def enc_c(h, gvec):
        if h not in ecache:
            ecache[h] = enc(gvec)
        return ecache[h]

    def pick(r):
        C = _cands(r, cfg)
        if len(C) < 2:
            return r.get("pos_pick")
        vl = V1._lem(r["verb"]); vi = r["verb_idx"]
        cues = []            # list of (precision_weight, logprob_array)
        # #2 word-order cue, #1 construction-conditional collapse
        if "pos" in cfg:
            ps = pos_scores(C, vi)
            dist = _softmax(ps, T=0.5)
            beta = BETA_NONCANON if (r.get("voice") == "passive" or r.get("noncanonical")) else 1.0
            cues.append((_precision(dist) * beta, np.log(dist + _EPS)))
        # PARSER structural cue (the lever): grammatical object / passive-subject -> patient
        if "struct" in cfg:
            ss = struct_patient_scores(r, C)
            if ss.any():
                dist = _softmax(ss, T=0.3)
                cues.append((_precision(dist), np.log(dist + _EPS)))
        # #core selectional/episodic FHRR (#5 grounded fillers if 'grounded' in cfg; #6 pre-activation; #7 agent-cond)
        if "sel" in cfg:
            toks = fhrr_store.get(vl)
            fs = fhrr_patient_scores(C, toks, enc_c, A, P, soft_and=("softand" in cfg))
            if fs.any():
                dist = _softmax(fs, T=0.05)
                cues.append((_precision(dist), np.log(dist + _EPS)))
        # #3 neocortical generative
        if "gen" in cfg:
            gs = gen_patient_scores(C, vl, vidx, model, Gmap)
            if gs.any():
                dist = _softmax(gs, T=0.5)
                cues.append((_precision(dist), np.log(dist + _EPS)))
        # #2 animacy cue
        if "anim" in cfg:
            as_ = anim_scores(C)
            if 0 < as_.sum() < len(C):    # informative only if candidates differ in animacy
                dist = _softmax(as_, T=0.5)
                cues.append((_precision(dist) * 0.5, np.log(dist + _EPS)))
        if not cues:
            return r.get("pos_pick")
        # #1 precision-weighted noisy-channel integration (log-space product)
        total = np.zeros(len(C))
        for w, lp in cues:
            total = total + w * lp
        return C[int(np.argmax(total))][0]

    return pick


def _cands(r, cfg):
    """candidate (head, idx, filler_vec); filler space = grounded-12d (#5) or GloVe-300 (default)."""
    out = []
    for h, idx in zip(r["cand_heads"], r["cand_idx"]):
        if h in V1.STOP or len(h) < 3:
            continue
        if "grounded" in cfg:
            g = _grounded(h)
        else:
            g = _GV.get(h)
        if g is None:
            continue
        out.append((h, idx, g))
    return out


# module-level handles set in main (kept simple; single-process cell)
_GV = {}


def train_generative(parsed, gv, d_grounded=300, epochs=8, k=64):
    """#3/#4: GroundedDistMult over the SCIENCE (a,v,p) triples, prediction-error trained. Returns (model,
    vidx, Gmap, learning_curve). Gmap = word -> d_grounded grounded/glove vec (the projection input)."""
    torch.manual_seed(0)
    trips_raw = [(a, v, p) for a, v, p in parsed["svo"] if gv.get(a) is not None and gv.get(p) is not None]
    verbs = sorted({v for _, v, _ in trips_raw}); vidx = {v: i for i, v in enumerate(verbs)}
    words = sorted({w for a, _, p in trips_raw for w in (a, p)})
    widx = {w: i for i, w in enumerate(words)}
    G = torch.from_numpy(np.stack([np.asarray(gv[w], dtype=np.float64) for w in words]).astype(np.float32))
    trips = [(widx[a], vidx[v], widx[p]) for a, v, p in trips_raw]
    rng = np.random.default_rng(0); rng.shuffle(trips)
    ntest = max(500, len(trips) // 10); test, train = trips[:ntest], trips[ntest:]
    ppool = sorted({p for _, _, p in train}); pp = np.array(ppool)
    model = GroundedDistMult(len(verbs), d_grounded, k)
    opt = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=1e-5)
    bs = 512; order = np.arange(len(train)); curve = []

    def hit1(sample=1000, ncor=50):
        model.eval()
        idx = rng.integers(0, len(test), size=min(sample, len(test))); h = 0; n = 0
        with torch.no_grad():
            Pp = model.emb(G[pp])
            for j in idx:
                a, v, p = test[j]
                ea = model.emb(G[a].unsqueeze(0))[0]; rv = model.R(torch.tensor(v))
                cand = list(rng.integers(0, len(ppool), size=ncor))
                sc = ((ea * rv).unsqueeze(0) * Pp[cand]).sum(-1)
                sg = ((ea * rv) * model.emb(G[p].unsqueeze(0))[0]).sum()
                h += int((sc > sg).sum() == 0); n += 1
        return h / max(n, 1)

    for ep in range(epochs):
        model.train(); rng.shuffle(order)
        for i in range(0, len(order), bs):
            bt = [train[j] for j in order[i:i + bs]]
            ga = G[[a for a, _, _ in bt]]; vi = torch.tensor([v for _, v, _ in bt]); gp = G[[p for _, _, p in bt]]
            neg = G[[pp[k] for k in rng.integers(0, len(ppool), size=len(bt))]]
            loss = torch.nn.functional.softplus(model.score(ga, vi, neg) - model.score(ga, vi, gp)).mean()
            opt.zero_grad(); loss.backward(); opt.step()
        curve.append({"epoch": ep, "heldout_hit1": round(hit1(), 4)})
    Gmap = {w: gv[w] for w in gv}
    return model, vidx, Gmap, curve


def evaluate(rows, scorer, pop):
    return round(sum(1 for r in pop if scorer(r) == r["gold_head"]) / len(pop), 4) if pop else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", type=int, default=TOK)
    ap.add_argument("--nboot", type=int, default=2000)
    ap.add_argument("--epochs", type=int, default=8)
    ap.add_argument("--pop", type=str, default="qa", help="qa (modern science) | litbank (19c fiction) -- generalization")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    global _GV

    parsed = E.parse_corpus("science", args.tokens, set())  # reuse the register-native SCIENCE cache
    rows = V1.load_pop(V1.LB if args.pop == "litbank" else V1.QA)
    vocab = set()
    for a, v, o in parsed["svo"]:
        vocab.add(a); vocab.add(o)
    for v, o in parsed["verb_obj"]:
        vocab.add(o)
    for r in rows:
        vocab.update(h for h in r["cand_heads"] if len(h) >= 3)
        vocab.add(r["gold_head"])
    _GV = E.load_glove_union(vocab)

    A = unit_phase_vec(E.D, torch.Generator().manual_seed(1)).to(torch.complex64)
    P = unit_phase_vec(E.D, torch.Generator().manual_seed(2)).to(torch.complex64)
    epochs = 2 if args.smoke else args.epochs

    # --- SPACE 1: GloVe-300 distributional fillers (the working stand-in) ---
    enc300 = make_enc(300)
    fhrr_g = E.build_fhrr(parsed, _GV, enc300, A, P)
    model_g, vidx_g, Gmap_g, curve = train_generative(parsed, _GV, d_grounded=300, epochs=epochs)
    print("[store] glove fhrr verbs=%d | gen curve hit@1: %s" % (len(fhrr_g), [c["heldout_hit1"] for c in curve]), flush=True)

    # --- SPACE 2: grounded-12d sensorimotor fillers (#5 -- the substrate's ATL space) ---
    grnd = {}
    for w in (set(v for v in _GV)):   # only words we have any vec for; grounded may cover fewer
        gr = _grounded(w)
        if gr is not None:
            grnd[w] = gr
    enc12 = make_enc(12)
    fhrr_r = E.build_fhrr(parsed, grnd, enc12, A, P)
    model_r, vidx_r, Gmap_r, curve_r = train_generative(parsed, grnd, d_grounded=12, epochs=epochs)
    print("[store] grounded-12d fhrr verbs=%d (cov %d words)" % (len(fhrr_r), len(grnd)), flush=True)

    spaces = {
        "glove": {"gv": _GV, "enc": enc300, "fhrr": fhrr_g, "model": model_g, "vidx": vidx_g, "Gmap": Gmap_g},
        "grounded": {"gv": grnd, "enc": enc12, "fhrr": fhrr_r, "model": model_r, "vidx": vidx_r, "Gmap": Gmap_r},
    }

    # populations: HARD (non-canonical/passive, non-reversible) and FULL (all non-reversible)
    def cnd(r):
        return [(h, idx) for h, idx in zip(r["cand_heads"], r["cand_idx"]) if h not in V1.STOP and len(h) >= 3 and _GV.get(h) is not None]
    def nonrev(r):
        return sum(1 for h, _ in cnd(r) if anim(h)) < 2
    def posambig(r):
        # word-order genuinely UNINFORMATIVE: all glove-covered candidates on the SAME side of the verb
        vi = r["verb_idx"]; sides = set(1 if idx > vi else 0 for _, idx in cnd(r))
        return len(sides) == 1
    FULL = [r for r in rows if len(cnd(r)) >= 2 and nonrev(r)]
    HARD = [r for r in FULL if (r.get("voice") == "passive" or r.get("noncanonical"))]
    PAMB = [r for r in FULL if posambig(r)]      # the subset where SELECTIONAL must carry it (position flat)
    if args.smoke:
        HARD = HARD[:120]; FULL = FULL[:120]; PAMB = PAMB[:120]
    print("[pop] HARD n=%d  FULL n=%d  POS-AMBIG n=%d" % (len(HARD), len(FULL), len(PAMB)), flush=True)

    # ablation ladder: each config is a set of mechanism tags
    CONFIGS = [
        ("POS_only (linear position)", {"pos"}),
        ("STRUCT_only (PARSER: gram-role+voice)", {"struct"}),
        ("SEL_only(episodic joint)", {"sel"}),
        ("GEN_only(generative)", {"gen"}),
        ("POS+SEL (#1,#2 noisy-channel)", {"pos", "sel"}),
        ("STRUCT+SEL (parser + selectional)", {"struct", "sel"}),
        ("STRUCT+SEL+ANIM", {"struct", "sel", "anim"}),
        ("ALL-with-STRUCT (parser replaces pos)", {"struct", "sel", "gen", "anim", "softand"}),
        ("ALL (#1,2,3,7 + softAND #core)", {"pos", "sel", "gen", "anim", "softand"}),
        ("ALL + grounded-12d (#5)", {"pos", "sel", "gen", "anim", "softand", "grounded"}),
    ]
    pos_pick = lambda r: r.get("pos_pick")
    results = {"config": {"tokens": args.tokens, "epochs": args.epochs, "beta_noncanon": BETA_NONCANON},
               "gen_learning_curve_glove": curve, "gen_learning_curve_grounded": curve_r,
               "n_HARD": len(HARD), "n_FULL": len(FULL), "n_POSAMBIG": len(PAMB), "arms": {}}
    for name, cfg in CONFIGS:
        sc = make_scorer(cfg, spaces, A, P)
        aH = evaluate(rows, sc, HARD); aF = evaluate(rows, sc, FULL); aP = evaluate(rows, sc, PAMB)
        dH = V1.paired_delta(HARD, sc, pos_pick, args.nboot)
        dF = V1.paired_delta(FULL, sc, pos_pick, args.nboot)
        results["arms"][name] = {"HARD_acc": aH, "FULL_acc": aF, "POSAMBIG_acc": aP,
                                 "HARD_vs_POS": {k: dH[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")},
                                 "FULL_vs_POS": {k: dF[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")}}
        print("  %-34s HARD=%.4f  FULL=%.4f  POS-AMBIG=%.4f" % (name, aH, aF, aP), flush=True)

    # load-bearing ablations -- THE decisive one is STRUCT (parser) vs POS (linear position): is the PARSER the lever?
    selsc = make_scorer({"sel"}, spaces, A, P)
    possc = make_scorer({"pos"}, spaces, A, P)
    structsc = make_scorer({"struct"}, spaces, A, P)
    struct_sel = make_scorer({"struct", "sel"}, spaces, A, P)
    print("\n--- decisive comparisons ---", flush=True)
    for tag, pop in (("HARD", HARD), ("FULL", FULL), ("POSAMBIG", PAMB)):
        results["STRUCT_vs_POS_" + tag] = {k: V1.paired_delta(pop, structsc, possc, args.nboot)[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")}
        results["SEL_vs_POS_" + tag] = {k: V1.paired_delta(pop, selsc, possc, args.nboot)[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")}
        results["STRUCTSEL_vs_STRUCT_" + tag] = {k: V1.paired_delta(pop, struct_sel, structsc, args.nboot)[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")}
        st = results["STRUCT_vs_POS_" + tag]; sp = results["SEL_vs_POS_" + tag]; ss = results["STRUCTSEL_vs_STRUCT_" + tag]
        print("  [%s] STRUCT_vs_POS d=%+.4f f<=0=%.2f | SEL_vs_POS d=%+.4f f<=0=%.2f | STRUCT+SEL_vs_STRUCT d=%+.4f f<=0=%.2f"
              % (tag, st["delta"], st["frac_le_0"], sp["delta"], sp["frac_le_0"], ss["delta"], ss["frac_le_0"]), flush=True)

    out_name = "metrics.json" if args.pop == "qa" else ("metrics_%s.json" % args.pop)
    tmp = os.path.join(OUT_DIR, out_name + ".tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "brain_faithful_who_did_what_v1", "pop": args.pop, "results": results,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, out_name))
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
