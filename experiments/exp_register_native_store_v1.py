"""exp_register_native_store_v1 -- THE DELIVERABLE: a no-gold, REGISTER-NATIVE selectional/event store
built OFFLINE from a genuinely DISJOINT domain-matched corpus recovers who-did-what over the out-of-domain
(simplewiki) store on the held-out QA-SRL science test.

PROBLEM (slug the_selectional_event_store_is_learned_from_the_wrong_domain_needs_a_register_native_corpus):
the parent problem's oracle-ladder dissection proved DOMAIN MATCH of the selectional corpus is the #1 lever
for who-did-what (+0.149), but it measured that with LEAVE-ONE-SENTENCE-OUT on the TEST corpus itself (a
probe, not a deployable result). This cell tests the DEPLOYABLE claim: build the store from a genuinely
DISJOINT corpus of the SAME DOMAIN (grade-school science) and prove it still recovers the domain lever.

WHY THIS IS THE TEST DOMAIN (verified on disk, not assumed): the QA population
(data/predict_revise_recall_v1/_population.json, corpus='qasrl') is grade-school EARTH/GENERAL SCIENCE
textbook prose -- top gold patients: soil, energy, water, minerals, earthquakes, crust, erosion,
precipitation, hypothesis, theory; top verbs: use/form/create/cause/contain/produce/release/measure. So a
DOMAIN-MATCHED disjoint corpus = grade-school SCIENCE expository prose that is NOT the test sentences.

DESIGN (isolate DOMAIN at a FIXED parser -- the ONLY thing that varies across arms is the corpus domain):
  SCIENCE  (in-domain, register-native)  ARC science corpus (data/corpora/arc, science_general) -- DISJOINT
  SIMPLEWIKI (out-of-domain baseline)    Simple English Wikipedia (the current store's domain)
  FICTION  (wrong-domain control)        classic novels (narrative_fiction) -- matched size, WRONG domain
  ALL THREE parsed with the SAME frontend UD parser (hdlab PosTagger/ArcParser/ArcLabeler), no gold roles,
  matched token budget. Extraction: verb->OBJ pairs (MARGINAL exemplar store) + (subj,verb,obj) triples
  (FHRR-BOUND joint event store, hdlab.binding; SEM/Franklin 2020; grounded-distributed GloVe fillers).

BAR (can-fail; CI-separated; twin + domain-scramble must lose):
  SCIENCE store BEATS SIMPLEWIKI store on held-out who-did-what CI-separated; VERB-SHUFFLED twin (fillers
  kept, verb keys permuted) LOSES; the WRONG-DOMAIN (fiction) store does NOT recover (the domain, not any
  corpus, does the work). Report CI half-width + null p95. Leakage guarded: the store corpus is a DIFFERENT
  SOURCE than the test, and we verify zero exact test-sentence overlap.

NO external LLM (GloVe = static offline asset; parser + binding = substrate organs). ASCII. Writes only to
its own data dir.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse, glob, json, re, sys, time
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_verbrole_exemplar_which_arg_v1 as V1  # STOP, _lem, load_pop, paired_delta, QA

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_register_native_store_v1")
_EPS = 1e-9
STRUCT = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|[0-9]+|[^\sA-Za-z0-9]")
OBJ = {"obj", "dobj", "nsubj:pass", "nsubjpass"}
SUBJ = {"nsubj", "obl:agent"}
D = 1024  # FHRR dim (OUR-INVENTION-UNDER-TEST; matches the parent + bound_event_backbone)

# ---- corpus registry: raw file globs per DOMAIN. All disjoint from the QA test sentences. ----
_C = os.path.join(_REPO, "data/corpora")
CORPORA = {
    "science":   [os.path.join(_C, "arc/ARC-V1-Feb2018-2/ARC_Corpus.txt")],
    "simplewiki": [os.path.join(_C, "simplewiki/simplewiki_clean_v1.txt")],
    "fiction":   [os.path.join(_C, "little_women/cleaned/little_women.clean.txt"),
                  os.path.join(_C, "tom_sawyer/cleaned/tom_sawyer.clean.txt"),
                  os.path.join(_C, "sherlock_holmes/cleaned/adventures.clean.txt"),
                  os.path.join(_C, "sherlock_holmes/cleaned/memoirs.clean.txt"),
                  os.path.join(_C, "anne_of_green_gables/cleaned/anne_of_green_gables.clean.txt"),
                  os.path.join(_C, "wizard_of_oz/cleaned/wizard_of_oz.clean.txt"),
                  os.path.join(_C, "little_women/cleaned/little_women.clean.txt")],
}


def _norm_sent(s):
    return re.sub(r"\s+", " ", s.strip().lower())


def clean_ok(s):
    """keep clean declarative prose sentences; drop headlines, citations, urls, list fragments."""
    s = s.strip()
    if not (30 <= len(s) <= 250):
        return False
    if "http" in s or "www." in s or "@" in s or "|" in s:
        return False
    letters = sum(c.isalpha() for c in s)
    if letters < 0.65 * len(s):
        return False
    if s[-1] not in ".!?":
        return False
    if sum(c.isdigit() for c in s) > 0.15 * len(s):
        return False
    return True


def iter_sentences(paths):
    for path in paths:
        if not os.path.exists(path):
            print("[warn] missing corpus file %s" % path, flush=True)
            continue
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                # strip WorldTree-style trailing "(TAG, UID: ...)" markers if present
                ln = re.sub(r"\s*\([A-Z]+, UID:[^)]*\)", "", ln)
                for piece in re.split(r"(?<=[.!?])\s+", ln):
                    if clean_ok(piece):
                        yield piece


def parse_corpus(name, max_tokens, test_norm_sents):
    """Parse a domain's raw text with the frontend UD parser; extract verb->OBJ pairs + (subj,verb,obj)
    triples (no gold). Cache {n_sent,n_tok,verb_obj,svo,n_leak}. Idempotent: reuse a cache with >= tokens."""
    os.makedirs(OUT_DIR, exist_ok=True)
    cache = os.path.join(OUT_DIR, "pairs_%s_%dtok.json" % (name, max_tokens))
    if os.path.exists(cache):
        d = json.load(open(cache))
        if d.get("n_tok", 0) >= max_tokens * 0.98:
            print("[parse] reuse %s (n_tok=%d)" % (cache, d["n_tok"]), flush=True)
            return d
    from hdlab.pos_tagger import PosTagger
    from hdlab.arc_parser import ArcParser
    from hdlab.arc_labeler import ArcLabeler
    from hdlab.reading_grounding_loop import normalize_lemma
    FE = os.path.join(_REPO, "data", "frontend_assets")
    tg = PosTagger.load(os.path.join(FE, "pos_tagger_ud_ewt_upos.json"))
    pr = ArcParser.load(os.path.join(FE, "arc_parser_richfeat_ud_ewt.npz"))
    lb = ArcLabeler.load(os.path.join(FE, "arc_labeler_hashed_ud_ewt.json"))
    verb_obj = []
    svo = []
    ntok = 0
    nsent = 0
    nleak = 0
    t0 = time.time()
    for sent in iter_sentences(CORPORA[name]):
        if ntok >= max_tokens:
            break
        if _norm_sent(sent) in test_norm_sents:      # leakage guard: never learn from a test sentence
            nleak += 1
            continue
        toks = STRUCT.findall(sent)
        if not toks or len(toks) > 80:
            continue
        try:
            pos = tg.tag(toks)
            heads = pr.parse(toks, pos).heads
            labs = lb.label(toks, pos, heads)
        except Exception:
            continue
        ntok += len(toks)
        nsent += 1
        n = len(toks)
        lem = [normalize_lemma(t) for t in toks]
        byv = defaultdict(lambda: {"s": None, "o": None})
        for i in range(1, n + 1):
            rel = labs.get(i)
            h = heads.get(i, 0)
            if not h or not (1 <= h <= n) or pos[h - 1] != "VERB":
                continue
            f = lem[i - 1]
            if f in V1.STOP or len(f) < 3:
                continue
            if rel in OBJ:
                byv[h]["o"] = f
            elif rel in SUBJ:
                byv[h]["s"] = f
        for h, dd in byv.items():
            verb = V1._lem(lem[h - 1])
            if len(verb) < 2:
                continue
            if dd["o"]:
                verb_obj.append((verb, dd["o"]))
            if dd["s"] and dd["o"]:
                svo.append((dd["s"], verb, dd["o"]))
        if nsent % 5000 == 0:
            print("[parse:%s] %d sent %d tok %.0fs (%d pairs)" % (name, nsent, ntok, time.time() - t0, len(verb_obj)), flush=True)
    out = {"name": name, "n_sent": nsent, "n_tok": ntok, "n_leak": nleak,
           "verb_obj": verb_obj, "svo": svo, "ts": datetime.now(timezone.utc).isoformat()}
    tmp = cache + ".tmp"
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh)
    os.replace(tmp, cache)
    print("[parse:%s] DONE %d sent %d tok %.0fs | %d verb_obj %d svo | leak=%d -> %s"
          % (name, nsent, ntok, time.time() - t0, len(verb_obj), len(svo), nleak, cache), flush=True)
    return out


# ------------------------------------------------------------------ GloVe (static offline asset)
def load_glove_union(vocab):
    """Vectors for the requested vocab from glove-wiki-gigaword-300 (static offline asset). Cache stores
    both the glove-COVERED words AND the full QUERIED vocab, so we can tell 'complete cache' from 'stale':
    rebuild only if a NEW word (never queried) is requested (OOV words legitimately absent from `words`)."""
    vocab = set(vocab)
    cache = os.path.join(OUT_DIR, "_glove_union.npz")
    if os.path.exists(cache):
        with np.load(cache, allow_pickle=True) as z:            # context-manager -> handle closed (Windows)
            words = list(z["words"]); V = np.asarray(z["vecs"])
            queried = set(z["queried"].tolist()) if "queried" in z.files else set(words)
        have = {w: V[i] for i, w in enumerate(words)}
        if vocab.issubset(queried):                             # every requested word already tried vs glove
            return have
        vocab = vocab | queried
    print("[glove] loading glove-wiki-gigaword-300 for %d words..." % len(vocab), flush=True)
    import gensim.downloader as api
    kv = api.load("glove-wiki-gigaword-300")
    words, vecs = [], []
    for w in sorted(vocab):
        if w in kv:
            v = np.asarray(kv[w], dtype=np.float64); nn = np.linalg.norm(v)
            if nn > _EPS:
                words.append(w); vecs.append(v / nn)
    V = np.stack(vecs)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(cache + ".tmp", "wb") as fh:
        np.savez(fh, words=np.array(words, dtype=object), vecs=V, queried=np.array(sorted(vocab), dtype=object))
    os.replace(cache + ".tmp", cache)
    print("[glove] cached %d words (queried %d)" % (len(words), len(vocab)), flush=True)
    return {w: V[i] for i, w in enumerate(words)}


# ------------------------------------------------------------------ stores
def build_marginal(pairs_d, gv, topk=150):
    """verb -> list of grounded OBJ filler vecs (count-ordered, top-K). The MARGINAL exemplar store."""
    byv = defaultdict(Counter)
    for v, o in pairs_d["verb_obj"]:
        byv[v][o] += 1
    store = {}
    for v, ctr in byv.items():
        exv = [gv[f] for f, _ in ctr.most_common(topk) if gv.get(f) is not None]
        if exv:
            store[v] = np.stack(exv)
    return store


def build_fhrr(pairs_d, gv, enc, A, P, topk=200):
    """verb -> [K,D] complex event tokens quantize(bind(A,enc(a))+bind(P,enc(p))). The FHRR joint store."""
    import torch
    import experiments.exp_fhrr_event_role_assignment_v1 as F
    from hdlab import binding
    byv = defaultdict(list)
    for s, v, o in pairs_d["svo"]:
        byv[v].append((s, o))
    store = {}
    for v, ps in byv.items():
        ps = [(a, p) for a, p in ps if gv.get(a) is not None and gv.get(p) is not None][:topk]
        if not ps:
            continue
        store[v] = torch.stack([F.quantize(binding.bind(A, enc(gv[a])) + binding.bind(P, enc(gv[p]))) for a, p in ps])
    return store


def verbshuffle(store, seed=17):
    """verb-shuffled twin: keep the filler sets, permute the verb keys (destroy verb->filler mapping)."""
    keys = sorted(store.keys())
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(keys))
    return {keys[i]: store[keys[perm[i]]] for i in range(len(keys))}


# ------------------------------------------------------------------ scoring on held-out QA
def anim(w):
    from hdlab.animacy_lexicon import lookup_animacy
    a = lookup_animacy(w)
    return isinstance(a, dict) and (a.get("animacy") == "animate" or a.get("category") in ("person", "animal"))


def knn(vec, exs, k=3):
    if exs is None or len(exs) == 0:
        return -1.0
    c = exs @ vec / (np.linalg.norm(exs, axis=1) * (np.linalg.norm(vec) + _EPS) + _EPS)
    c = np.sort(c)[::-1]
    return float(np.mean(c[:min(k, len(c))]))


def make_cands(gv):
    def cands(r):
        out = []
        for h, idx in zip(r["cand_heads"], r["cand_idx"]):
            if h in V1.STOP or len(h) < 3 or gv.get(h) is None:
                continue
            out.append((h, idx, gv[h]))
        return out
    return cands


def marginal_pick_fn(store, cands, k=3):
    def pick(r):
        C = cands(r); ex = store.get(V1._lem(r["verb"]))
        if len(C) < 2 or ex is None:
            return r.get("pos_pick")
        return max(((knn(v, ex, k), h) for h, _, v in C))[1]
    return pick


def fhrr_pick_fn(store, cands, enc, A, P):
    import torch
    import experiments.exp_fhrr_event_role_assignment_v1 as F
    from hdlab import binding
    ecache = {}

    def enc_c(h, v):
        if h not in ecache:
            ecache[h] = enc(v)
        return ecache[h]

    def pick(r):
        C = cands(r); toks = store.get(V1._lem(r["verb"]))
        if len(C) < 2 or toks is None:
            return r.get("pos_pick")
        n = len(C); pmarg = np.zeros(n)
        for ai in range(n):
            qa = binding.bind(A, enc_c(C[ai][0], C[ai][2]))
            for pi in range(n):
                if ai == pi:
                    continue
                q = F.quantize(qa + binding.bind(P, enc_c(C[pi][0], C[pi][2])))
                pmarg[pi] += max(0.0, F.recognition(q, toks))
        return C[int(np.argmax(pmarg))][0]
    return pick


def fhrr_and_pick_fn(store, cands, enc, A, P):
    """SOFT-AND (multiplicative) per-role kernel -- the brain-foundational conjunctive event code the
    audit names (a code that requires BOTH the agent AND the patient to match ONE stored event, not the
    additive FHRR cleanup that counts agent-match + patient-match and so UNDER-separates: the fan effect).
    score(patient p) = max_a max_token relu(agent_match(a,token)) * relu(patient_match(p,token)); argmax_p.
    agent_match / patient_match = per-role FHRR cleanup Re<conj(bind(ROLE,filler)), token>/D (~[filler==stored]).
    """
    import torch
    import experiments.exp_fhrr_event_role_assignment_v1 as F
    from hdlab import binding
    acache, pcache = {}, {}

    def qa(h, v):
        if h not in acache:
            acache[h] = binding.bind(A, enc(v))
        return acache[h]

    def qp(h, v):
        if h not in pcache:
            pcache[h] = binding.bind(P, enc(v))
        return pcache[h]

    def rolematch(qrole, toks):
        return (qrole.conj().unsqueeze(0) * toks).sum(dim=1).real / F.D  # [K] per stored token

    def pick(r):
        C = cands(r); toks = store.get(V1._lem(r["verb"]))
        if len(C) < 2 or toks is None:
            return r.get("pos_pick")
        n = len(C)
        am = [rolematch(qa(C[i][0], C[i][2]), toks).clamp(min=0.0) for i in range(n)]
        pm = [rolematch(qp(C[i][0], C[i][2]), toks).clamp(min=0.0) for i in range(n)]
        score = np.zeros(n)
        for pi in range(n):
            best = 0.0
            for ai in range(n):
                if ai == pi:
                    continue
                v = float((am[ai] * pm[pi]).max())  # soft-AND per token, then best-matching event
                if v > best:
                    best = v
            score[pi] = best
        return C[int(np.argmax(score))][0]
    return pick


def eval_all(tokens, nboot):
    import torch
    import experiments.exp_fhrr_event_role_assignment_v1 as F
    from hdlab.situation_model_accumulate import unit_phase_vec
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = V1.load_pop(V1.QA)
    test_norm = set(_norm_sent(r["sent"]) for r in rows)

    parsed = {name: parse_corpus(name, tokens, test_norm) for name in ("science", "simplewiki", "fiction")}

    # union vocab for glove: all store fillers + all candidate heads + gold heads
    vocab = set()
    for d in parsed.values():
        for v, o in d["verb_obj"]:
            vocab.add(o)
        for s, v, o in d["svo"]:
            vocab.add(s); vocab.add(o)
    for r in rows:
        vocab.update(h for h in r["cand_heads"] if len(h) >= 3)
        vocab.add(r["gold_head"])
    gv = load_glove_union(vocab)

    # ---- MARGINAL exemplar stores (the parent's +0.149 level) ----
    marg = {name: build_marginal(parsed[name], gv) for name in parsed}
    marg_shuf = verbshuffle(marg["science"])
    # ---- FHRR-bound joint event stores (the brain-foundational codec; SCIENCE + SIMPLEWIKI) ----
    enc = F.make_encoder()
    A = unit_phase_vec(D, torch.Generator().manual_seed(1)).to(torch.complex64)
    P = unit_phase_vec(D, torch.Generator().manual_seed(2)).to(torch.complex64)
    fhrr = {name: build_fhrr(parsed[name], gv, enc, A, P) for name in ("science", "simplewiki")}
    fhrr_shuf = verbshuffle(fhrr["science"])

    cands = make_cands(gv)
    marg_arms = {
        "SCIENCE_marg": marginal_pick_fn(marg["science"], cands),
        "SIMPLEWIKI_marg": marginal_pick_fn(marg["simplewiki"], cands),
        "FICTION_marg": marginal_pick_fn(marg["fiction"], cands),
        "SCIENCE_marg_VERBSHUF": marginal_pick_fn(marg_shuf, cands),
    }
    fhrr_arms = {
        "SCIENCE_fhrr": fhrr_pick_fn(fhrr["science"], cands, enc, A, P),
        "SIMPLEWIKI_fhrr": fhrr_pick_fn(fhrr["simplewiki"], cands, enc, A, P),
        "SCIENCE_fhrr_VERBSHUF": fhrr_pick_fn(fhrr_shuf, cands, enc, A, P),
        "SCIENCE_fhrrAND": fhrr_and_pick_fn(fhrr["science"], cands, enc, A, P),
        "SIMPLEWIKI_fhrrAND": fhrr_and_pick_fn(fhrr["simplewiki"], cands, enc, A, P),
    }

    results = {"config": {"tokens": tokens, "nboot": nboot, "D": D},
               "corpora": {n: {"n_sent": parsed[n]["n_sent"], "n_tok": parsed[n]["n_tok"],
                               "n_verb_obj": len(parsed[n]["verb_obj"]), "n_svo": len(parsed[n]["svo"]),
                               "n_leak": parsed[n]["n_leak"], "n_verbs_marg": len(marg[n]),
                               "n_verbs_fhrr": len(fhrr.get(n, {}))} for n in parsed}}

    def acc(fn, S):
        return round(sum(1 for r in S if fn(r) == r["gold_head"]) / len(S), 4) if S else 0.0

    for sname in ("passive", "noncanonical"):
        sub = [r for r in rows if r.get("voice") == "passive"] if sname == "passive" else [r for r in rows if r.get("noncanonical")]
        nonrev_full = [r for r in sub if len(cands(r)) >= 2 and sum(1 for h, _, _ in cands(r) if anim(h)) < 2]
        rec = {"n_slice": len(sub), "n_nonrev_full": len(nonrev_full)}

        # (A) MARGINAL, store-vs-store on BOTH-covered items (isolates filler quality at fixed verb coverage)
        def cov_marg(r):
            vl = V1._lem(r["verb"]); return vl in marg["science"] and vl in marg["simplewiki"]
        mrows = [r for r in nonrev_full if cov_marg(r)]
        rec["marginal"] = {
            "n": len(mrows), "acc": {a: acc(f, mrows) for a, f in marg_arms.items()},
            "SCIENCE_vs_SIMPLEWIKI": V1.paired_delta(mrows, marg_arms["SCIENCE_marg"], marg_arms["SIMPLEWIKI_marg"], nboot) if len(mrows) >= 20 else None,
            "SCIENCE_vs_VERBSHUF": V1.paired_delta(mrows, marg_arms["SCIENCE_marg"], marg_arms["SCIENCE_marg_VERBSHUF"], nboot) if len(mrows) >= 20 else None,
            "FICTION_vs_SIMPLEWIKI": V1.paired_delta(mrows, marg_arms["FICTION_marg"], marg_arms["SIMPLEWIKI_marg"], nboot) if len(mrows) >= 20 else None,
            "SCIENCE_vs_FICTION": V1.paired_delta(mrows, marg_arms["SCIENCE_marg"], marg_arms["FICTION_marg"], nboot) if len(mrows) >= 20 else None}

        # (B) FHRR-bound, store-vs-store on BOTH-covered items (the brain-foundational codec)
        def cov_fhrr(r):
            vl = V1._lem(r["verb"]); return vl in fhrr["science"] and vl in fhrr["simplewiki"]
        frows = [r for r in nonrev_full if cov_fhrr(r)]
        rec["fhrr"] = {
            "n": len(frows), "acc": {a: acc(f, frows) for a, f in fhrr_arms.items()},
            "SCIENCE_vs_SIMPLEWIKI": V1.paired_delta(frows, fhrr_arms["SCIENCE_fhrr"], fhrr_arms["SIMPLEWIKI_fhrr"], nboot) if len(frows) >= 20 else None,
            "SCIENCE_vs_VERBSHUF": V1.paired_delta(frows, fhrr_arms["SCIENCE_fhrr"], fhrr_arms["SCIENCE_fhrr_VERBSHUF"], nboot) if len(frows) >= 20 else None,
            "AND_SCIENCE_vs_SIMPLEWIKI": V1.paired_delta(frows, fhrr_arms["SCIENCE_fhrrAND"], fhrr_arms["SIMPLEWIKI_fhrrAND"], nboot) if len(frows) >= 20 else None,
            "AND_vs_ADDITIVE_science": V1.paired_delta(frows, fhrr_arms["SCIENCE_fhrrAND"], fhrr_arms["SCIENCE_fhrr"], nboot) if len(frows) >= 20 else None}

        # (C) DEPLOYMENT: full non-reversible slice, each store with position backoff (captures coverage too)
        rec["deployment_full"] = {
            "n": len(nonrev_full),
            "acc": {"SCIENCE_marg": acc(marg_arms["SCIENCE_marg"], nonrev_full),
                    "SIMPLEWIKI_marg": acc(marg_arms["SIMPLEWIKI_marg"], nonrev_full),
                    "SCIENCE_fhrr": acc(fhrr_arms["SCIENCE_fhrr"], nonrev_full),
                    "SIMPLEWIKI_fhrr": acc(fhrr_arms["SIMPLEWIKI_fhrr"], nonrev_full),
                    "POS": acc(lambda r: r.get("pos_pick"), nonrev_full)},
            "SCIENCE_vs_SIMPLEWIKI_marg": V1.paired_delta(nonrev_full, marg_arms["SCIENCE_marg"], marg_arms["SIMPLEWIKI_marg"], nboot) if len(nonrev_full) >= 20 else None,
            "SCIENCE_vs_SIMPLEWIKI_fhrr": V1.paired_delta(nonrev_full, fhrr_arms["SCIENCE_fhrr"], fhrr_arms["SIMPLEWIKI_fhrr"], nboot) if len(nonrev_full) >= 20 else None}

        results[sname] = rec
        print("\n=== QA/%s non-reversible ===" % sname, flush=True)
        print("  [MARGINAL both-covered n=%d]" % len(mrows), flush=True)
        for a in ("SIMPLEWIKI_marg", "FICTION_marg", "SCIENCE_marg_VERBSHUF", "SCIENCE_marg"):
            print("    %-24s acc=%.4f" % (a, rec["marginal"]["acc"][a]), flush=True)
        for lbl in ("SCIENCE_vs_SIMPLEWIKI", "SCIENCE_vs_VERBSHUF", "FICTION_vs_SIMPLEWIKI", "SCIENCE_vs_FICTION"):
            d = rec["marginal"][lbl]
            if d:
                print("      %-22s d=%+.4f CI[%+.4f,%+.4f] half=%.4f frac<=0=%.3f" %
                      (lbl, d["delta"], d["ci_lo"], d["ci_hi"], d["ci_half"], d["frac_le_0"]), flush=True)
        print("  [FHRR both-covered n=%d]" % len(frows), flush=True)
        for a in ("SIMPLEWIKI_fhrr", "SCIENCE_fhrr_VERBSHUF", "SCIENCE_fhrr", "SIMPLEWIKI_fhrrAND", "SCIENCE_fhrrAND"):
            print("    %-24s acc=%.4f" % (a, rec["fhrr"]["acc"][a]), flush=True)
        for lbl in ("SCIENCE_vs_SIMPLEWIKI", "SCIENCE_vs_VERBSHUF", "AND_SCIENCE_vs_SIMPLEWIKI", "AND_vs_ADDITIVE_science"):
            d = rec["fhrr"][lbl]
            if d:
                print("      %-24s d=%+.4f CI[%+.4f,%+.4f] half=%.4f frac<=0=%.3f" %
                      (lbl, d["delta"], d["ci_lo"], d["ci_hi"], d["ci_half"], d["frac_le_0"]), flush=True)
        dm = rec["deployment_full"]["SCIENCE_vs_SIMPLEWIKI_marg"]; df = rec["deployment_full"]["SCIENCE_vs_SIMPLEWIKI_fhrr"]
        acd = rec["deployment_full"]["acc"]
        if dm:
            print("  [DEPLOYMENT full n=%d POS=%.4f]" % (len(nonrev_full), acd["POS"]), flush=True)
            print("    marg  SCIENCE=%.4f SIMPLEWIKI=%.4f  d=%+.4f CI[%+.4f,%+.4f] frac<=0=%.3f"
                  % (acd["SCIENCE_marg"], acd["SIMPLEWIKI_marg"], dm["delta"], dm["ci_lo"], dm["ci_hi"], dm["frac_le_0"]), flush=True)
            print("    fhrr  SCIENCE=%.4f SIMPLEWIKI=%.4f  d=%+.4f CI[%+.4f,%+.4f] frac<=0=%.3f"
                  % (acd["SCIENCE_fhrr"], acd["SIMPLEWIKI_fhrr"], df["delta"], df["ci_lo"], df["ci_hi"], df["frac_le_0"]), flush=True)

    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "register_native_store_v1", "results": results,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("\n[done] %.0fs -> %s" % (time.time() - t0, os.path.join(OUT_DIR, "metrics.json")), flush=True)
    return results


def self_test():
    """tiny smoke: cleaning + extraction + marginal store + knn ranking on a synthetic pair set."""
    assert clean_ok("Earthquakes often trigger landslides in the mountains.")
    assert not clean_ok("http://x.y z")
    # synthetic marginal store: verb 'read' -> {book, letter}; a book-like vec must rank over a person-like
    gv = {"book": np.array([1.0, 0.0]), "letter": np.array([0.9, 0.1]), "man": np.array([0.0, 1.0])}
    d = {"verb_obj": [("read", "book"), ("read", "letter")], "svo": []}
    st = build_marginal(d, gv, topk=50)
    assert "read" in st
    fb = knn(gv["book"], st["read"], 1); fm = knn(gv["man"], st["read"], 1)
    assert fb > fm, "read-fit book %.3f must exceed man %.3f" % (fb, fm)
    print(json.dumps({"read_book_fit": round(fb, 3), "read_man_fit": round(fm, 3)}))
    print("SELF-TEST PASSED", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--parse-all", action="store_true", help="parse the 3 corpora to caches then stop")
    ap.add_argument("--parse", type=str, default=None, help="parse ONE corpus (science|simplewiki|fiction)")
    ap.add_argument("--eval", action="store_true")
    ap.add_argument("--tokens", type=int, default=1_500_000)
    ap.add_argument("--nboot", type=int, default=2000)
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.parse_all or args.parse:
        rows = V1.load_pop(V1.QA)
        test_norm = set(_norm_sent(r["sent"]) for r in rows)
        names = (args.parse,) if args.parse else ("science", "simplewiki", "fiction")
        for name in names:
            parse_corpus(name, args.tokens, test_norm)
        return
    # default: eval (parses on demand if caches absent)
    eval_all(args.tokens, args.nboot)


if __name__ == "__main__":
    main()
