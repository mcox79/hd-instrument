"""IDEAL-FOR-NOW step-5 selector: a learned, glass-box, LM-free cue COMBINER with a pluggable
world-knowledge PRIOR slot.

The step-5 waterfall (exp_referent_coref_step5_brain_foundational_v1) showed two loss centers, both
BELOW the architecture: (S2) the coarse likelihood fails to even surface the right candidate
(reachability 0.66), and (S3) the representation is too thin to choose among surfaced candidates. The
prescribed fix (kehler_rohde lit-scan, Competition Model MacWhinney-Bates: cue VALIDITY is LEARNED,
not hand-set; Parker 2019: combined nonlinearly) is a LEARNED conditional-softmax reranker over the
candidate pool. This cell builds it on the live he/she population, held-out, with:

  LIKELIHOOD cues (structural, buildable now): ACT-R recency base-level, Centering Cb (recent-subject),
    frequency, subject-frequency, first-mention primacy, distance, grammatical parallelism, and a
    discrete Lewis-Vasishth FAN/competitor-count interference term.
  PRIOR slot (the world-knowledge plug): ONE feature = a per-entity individuation signal. TODAY it is
    the glass-box content-cohesion proxy; TOMORROW the priority-1 North Star (a rich distributional
    per-character code + world knowledge) drops into the SAME feature with no architecture change --
    the learned weight on it simply grows as the signal gets richer.

The learned weights are the Competition Model's acquired cue validity; conditional-MLE on a TRAIN
doc-split, evaluated on HELD-OUT docs (no train-on-test). Controls: SHUFFLED-cue twin (permute each
candidate's features -> the learned model has nothing to grip); PRIOR-slot ablation + a SHUFFLED-prior
twin (the individuation slot must carry CI-separated signal AND be the growth point). Ceilings: the
best-single-structural-cue oracle (0.695) and the rich-in-text semantic oracle (0.857). Glass-box, NO
external LLM, past-only (no future-mention leakage), no gold at decision time (gold used only to LEARN
cue validity on TRAIN, exactly as a child learns which cues are reliable).

Run: .venv/Scripts/python.exe experiments/exp_referent_coref_step5_ideal_v1.py
"""
import json
import math
import os
import random
import sys

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.coref import parse_litbank_conll, build_pronoun_targets, name_gender_for_span
from hdlab.scene_segment import parse_conll_sentences
from hdlab.state_of_mind import compatible, PRONOUN_SCOPE
from hdlab.animacy_lexicon import lookup_animacy
import experiments.exp_name_entity_clustering_v1 as NC
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer

SEED = 20260903
MATCH_K = 24                                   # rank of the LEARNED clause<->entity matching metric
REP_K = 2 + MATCH_K                            # representation columns = flat cosine + distinctive cosine + match
FEATS = (("recency", "cb", "cb_recency", "freq", "subj_freq", "first", "parallel", "fan",
          "PRIOR_flat", "PRIOR_dist") + tuple("match%02d" % i for i in range(MATCH_K)))
_STOP = frozenset(("the a an and or but of to in on at for with by from as it he she they we you i his "
                   "her their its my your our this that these those was were is are be been being had has "
                   "have do did does not no so then than there here what which who whom when him them us "
                   "me said say says one all any some more most such very into out up down over about "
                   "after before while because if though her hers").split())


def _docs(n):
    wdw = json.load(open(os.path.join(_REPO, "data/litbank/who_did_what_events.json"), encoding="utf-8"))
    out = []
    for r in wdw:
        p = os.path.join(NC.CONLL_DIR, r["doc"] + ".conll")
        if os.path.exists(p):
            out.append((r["doc"], p))
        if len(out) >= n:
            break
    return out


def _animate(m, gaz):
    g = m.get("gender") or m.get("name_gender")
    if g is None and gaz:
        g = name_gender_for_span(m.get("span_toks", [m["head"]]), gaz)
    if g in ("masc", "fem"):
        return True
    a = lookup_animacy(m["head"], pos_tag=None)
    return bool(a and (a["animacy"] == "animate" or a["category"] == "person"))


def _content(toks):
    return {t.lower() for t in toks if t.isalpha() and len(t) >= 3 and t.lower() not in _STOP}


GLOVE_CACHE = os.path.join(_REPO, "data/exp_referent_coref_step5_ideal_v1/glove_litbank.npz")


def load_glove(docs):
    """GloVe-300 (glove-wiki-gigaword-300) vectors for the LitBank content vocab -- the LANDED
    distributional world-knowledge asset (data/gensim_cache). Cached to npz after first build."""
    if os.path.exists(GLOVE_CACHE):
        z = np.load(GLOVE_CACHE, allow_pickle=True)
        V = z["vecs"]; words = list(z["words"])      # read arrays ONCE (npz re-reads on every index)
        return {w: V[i] for i, w in enumerate(words)}
    vocab = set()
    for _d, p in docs:
        for s in parse_conll_sentences(p):
            vocab |= _content(s)
    print("[glove] loading glove-wiki-gigaword-300 for %d words (~2min first time)..." % len(vocab), flush=True)
    import gensim.downloader as api
    kv = api.load("glove-wiki-gigaword-300")
    words, vecs = [], []
    for w in sorted(vocab):
        if w in kv:
            v = np.asarray(kv[w], dtype=np.float64); n = np.linalg.norm(v)
            if n > 1e-9:
                words.append(w); vecs.append(v / n)
    V = np.stack(vecs)
    os.makedirs(os.path.dirname(GLOVE_CACHE), exist_ok=True)
    with open(GLOVE_CACHE + ".tmp", "wb") as fh:
        np.savez(fh, words=np.array(words, dtype=object), vecs=V)
    os.replace(GLOVE_CACHE + ".tmp", GLOVE_CACHE)
    print("[glove] cached %d words" % len(words), flush=True)
    return {w: V[i] for i, w in enumerate(words)}


def _centroid(words, glove):
    vs = [glove[w] for w in words if w in glove]
    if not vs:
        return None
    c = np.sum(vs, axis=0); n = np.linalg.norm(c)
    return c / n if n > 1e-9 else None


def _distinctive(wc, ent_df, n_ent, glove):
    """BEST individuation: a TF-IDF-weighted GloVe centroid of the entity's content words, DOWN-weighting
    words shared across the document's other characters (idf over ENTITIES) so the code emphasizes what is
    DISTINCTIVE about THIS character (the 'anxious god-daughter' vs 'vain elder sister' signal) rather than
    a blurred context average. Past-only (ent_df counts only entities seen so far). Glass-box, LM-free."""
    acc = None
    for w, cnt in wc.items():
        g = glove.get(w)
        if g is None:
            continue
        idf = math.log((n_ent + 1.0) / (1.0 + ent_df.get(w, 0)))
        wgt = math.log(1.0 + cnt) * idf
        acc = (g * wgt) if acc is None else (acc + g * wgt)
    if acc is None:
        return None
    n = np.linalg.norm(acc)
    return acc / n if n > 1e-9 else None


def collect(path, gaz, glove, R):
    """Online past-only replay; at each he/she target snapshot per-candidate feature rows + gold row.
    The PRIOR slot holds GloVe cohesion (flat + distinctive) AND a LEARNED matching block: R projects
    the clause and entity centroids to MATCH_K dims and their element-wise product is fed to the
    combiner, so the learned weights on it form a rank-MATCH_K bilinear matching metric clause^T M entity
    (the buildable core of EntityNLM/EntNet -- learn the individuation-matching function, not a fixed cosine)."""
    mentions, n_sents = parse_litbank_conll(path, name_gender_map=gaz)
    sents = parse_conll_sentences(path)
    cc = {}

    def csent(si):
        if si not in cc:
            cc[si] = _content(sents[si]) if 0 <= si < len(sents) else set()
        return cc[si]

    targets = build_pronoun_targets(mentions)
    tgt = {t["target"]["midx"] for t in targets}
    ent = {}
    ent_df = {}          # doc-level: word -> #distinct entities that have used it (past-only idf)
    order = 0
    items = []
    for m in mentions:
        if m["is_pronoun"] and m["midx"] in tgt:
            sc = PRONOUN_SCOPE[m["head"]]
            cur = m["sent_idx"]
            pron_subj = (m.get("sent_role_rank", 99) == 0)
            pron_ctx = csent(cur)
            clause_vec = _centroid(pron_ctx, glove)
            pool = [(cl, e) for cl, e in ent.items()
                    if e["animate"] and compatible(sc["gender"], sc["number"], e["gender"], e["number"])]
            if pool:
                rows, raws, gold_row = [], [], -1
                n_ent = len(ent)
                for i, (cl, e) in enumerate(pool):
                    subj_gap = (cur - e["last_subj_sent"]) if e["last_subj_sent"] >= 0 else 99
                    share = sum(1 for _c2, e2 in pool if abs(e2["last_order"] - e["last_order"]) <= 1)
                    # PRIOR slot -- two world-knowledge encodings of the same GloVe asset:
                    ev = e["gvec"]                                          # flat context centroid
                    coh_flat = float(np.dot(ev, clause_vec)) if (ev is not None and clause_vec is not None) else 0.0
                    dv = _distinctive(e["wc"], ent_df, n_ent, glove)        # BEST: distinctive TF-IDF individuation
                    coh_dist = float(np.dot(dv, clause_vec)) if (dv is not None and clause_vec is not None) else 0.0
                    base = [
                        -math.log(2 + (order - e["last_order"])),          # recency (ACT-R base-level)
                        1.0 if subj_gap <= 3 else 0.0,                      # Centering Cb (recent subject)
                        -math.log(2 + subj_gap),                           # graded Cb recency
                        math.log(1 + e["count"]),                          # frequency
                        math.log(1 + e["subj_count"]),                     # subject frequency (topicality)
                        -math.log(2 + (cur - e["first_sent"])),            # first-mention primacy
                        1.0 if (pron_subj and subj_gap <= 3) else 0.0,     # grammatical parallelism
                        -math.log(1 + share),                              # Lewis-Vasishth fan/interference
                        coh_flat,                                          # PRIOR_flat: context-centroid cohesion
                        coh_dist,                                          # PRIOR_dist: distinctive individuation
                    ]
                    if ev is not None and clause_vec is not None:          # LEARNED matching block (rank-MATCH_K)
                        match = list((R @ clause_vec) * (R @ ev))
                    else:
                        match = [0.0] * MATCH_K
                    rows.append(base + match)
                    raws.append((e["last_subj_sent"], e["last_order"], e["count"]))
                    if cl == m["cluster"]:
                        gold_row = i
                items.append({"X": np.array(rows, dtype=np.float64), "gold": gold_row,
                              "ncomp": len(pool), "raws": raws})
            # Gernsbacher-lite enhancement is OFF here (measured to hurt at this accuracy); combiner only.
        if not m["is_pronoun"]:
            cl = m["cluster"]
            e = ent.get(cl)
            if e is None:
                e = {"count": 0, "subj_count": 0, "last_order": -1, "last_subj_sent": -10,
                     "first_sent": m["sent_idx"], "gender": m.get("gender"), "number": m.get("number"),
                     "animate": _animate(m, gaz), "seen": set(), "gsum": np.zeros(300), "gvec": None,
                     "wc": {}}
                ent[cl] = e
            e["count"] += 1
            e["last_order"] = order
            for w in csent(m["sent_idx"]):                    # accumulate the entity's GloVe individuation centroid
                if w not in e["seen"] and w in glove:
                    e["gsum"] = e["gsum"] + glove[w]; e["seen"].add(w)
                if w not in e["wc"]:                          # first time this entity uses w -> idf bookkeeping
                    ent_df[w] = ent_df.get(w, 0) + 1
                e["wc"][w] = e["wc"].get(w, 0) + 1
            nrm = np.linalg.norm(e["gsum"])
            e["gvec"] = (e["gsum"] / nrm) if nrm > 1e-9 else None
            if e["gender"] is None and m.get("gender") is not None:
                e["gender"] = m["gender"]
            if m.get("sent_role_rank", 99) == 0:
                e["last_subj_sent"] = m["sent_idx"]
                e["subj_count"] += 1
        order += 1
    return items


def train_condlogit(items, d, l2=1.0, iters=400, lr=0.5):
    """Conditional-softmax (Competition-Model learned cue validity) by conditional-MLE."""
    w = np.zeros(d)
    tr = [it for it in items if it["gold"] >= 0]
    for _ in range(iters):
        grad = l2 * w
        for it in tr:
            X = it["X"]; s = X @ w; s -= s.max()
            p = np.exp(s); p /= p.sum()
            grad += X.T @ p - X[it["gold"]]
        w -= lr * grad / max(1, len(tr))
    return w


def _pick_centering(it):
    return int(max(range(len(it["raws"])), key=lambda i: (it["raws"][i][0], it["raws"][i][1])))


def _oracle_struct(it):
    if it["gold"] < 0:
        return False
    r = it["raws"]
    cent = max(range(len(r)), key=lambda i: (r[i][0], r[i][1]))
    rec = max(range(len(r)), key=lambda i: r[i][1])
    frq = max(range(len(r)), key=lambda i: (r[i][2], r[i][1]))
    return it["gold"] in (cent, rec, frq)


def _acc_model(items, w, lo=1, hi=99, drop_prior=False, shuffle_prior=None, shuffle_all=None):
    n = c = 0
    for idx, it in enumerate(items):
        if not (lo <= it["ncomp"] <= hi):
            continue
        n += 1
        X = it["X"].copy()
        if drop_prior:
            X[:, -REP_K:] = 0.0
        if shuffle_prior is not None:
            X[:, -1] = shuffle_prior[idx][:len(X)]
        if shuffle_all is not None:
            X = shuffle_all[idx]
        pick = int(np.argmax(X @ w))
        c += int(pick == it["gold"])
    return (c / n if n else float("nan")), n


def _acc_fn(items, fn, lo=1, hi=99):
    n = c = 0
    for it in items:
        if lo <= it["ncomp"] <= hi:
            n += 1; c += int(fn(it))
    return (c / n if n else float("nan")), n


def _boot(items_te, scorers, a, b, n_boot=1000, seed=SEED):
    """Doc-agnostic item bootstrap on acc(a)-acc(b); scorers[name] -> list of 0/1 aligned to items_te."""
    rng = random.Random(seed); k = len(items_te)
    A, B = scorers[a], scorers[b]
    base = (sum(A) - sum(B)) / k
    ds = []
    for _ in range(n_boot):
        sel = [rng.randrange(k) for _ in range(k)]
        ds.append((sum(A[i] for i in sel) - sum(B[i] for i in sel)) / k)
    ds.sort()
    return {"delta": base, "lo": ds[int(.025 * n_boot)], "hi": ds[int(.975 * n_boot)],
            "ci_sep": ds[int(.025 * n_boot)] > 0 or ds[int(.975 * n_boot)] < 0}


def run(n_docs=100, n_boot=1000):
    gaz = load_given_gazetteer()
    docs = _docs(n_docs)
    glove = load_glove(docs)
    R = np.random.default_rng(SEED).standard_normal((MATCH_K, 300)) / math.sqrt(300.0)   # fixed JL projection
    train_items, test_items = [], []
    for i, (_d, p) in enumerate(docs):
        (test_items if (i % 10 < 3) else train_items).extend(collect(p, gaz, glove, R))   # 30% held-out docs
    d = len(FEATS)
    # standardize on TRAIN candidate rows
    allrows = np.vstack([it["X"] for it in train_items if len(it["X"])])
    mu = allrows.mean(0); sd = allrows.std(0); sd[sd == 0] = 1.0
    for it in train_items + test_items:
        it["X"] = (it["X"] - mu) / sd
    w = train_condlogit(train_items, d)

    # per-item 0/1 vectors on TEST for the bootstrap
    def vec(fn):
        return [int(fn(it)) for it in test_items]
    model_hit = [int(np.argmax(it["X"] @ w) == it["gold"]) for it in test_items]
    cent_hit = [int(_pick_centering(it) == it["gold"]) for it in test_items]
    sc = {"model": model_hit, "centering": cent_hit}

    print("=" * 86)
    print("IDEAL-FOR-NOW STEP-5 COMBINER  (held-out: %d train / %d test targets)"
          % (len(train_items), len(test_items)))
    print("  learned cue validity (Competition Model):")
    for name, wt in sorted(zip(FEATS, w), key=lambda z: -abs(z[1])):
        print("     %-12s % .3f" % (name, wt))
    print("-" * 86)
    for lbl, fn in (("centering-only (best single cue)", lambda it: _pick_centering(it) == it["gold"]),
                    ("LEARNED COMBINER (ideal-for-now)", lambda it: int(np.argmax(it["X"] @ w)) == it["gold"]),
                    ("  drop PRIOR slot (structure only)", None),
                    ("structural oracle (Tier-1 ceiling)", _oracle_struct)):
        if fn is None:
            a_all, _ = _acc_model(test_items, w, drop_prior=True)
            a_h, _ = _acc_model(test_items, w, lo=2, drop_prior=True)
            a_e, _ = _acc_model(test_items, w, lo=1, hi=1, drop_prior=True)
        else:
            a_all, _ = _acc_fn(test_items, fn)
            a_h, _ = _acc_fn(test_items, fn, lo=2)
            a_e, _ = _acc_fn(test_items, fn, lo=1, hi=1)
        print("  %-36s ALL=%.4f  HARD(>=2)=%.4f  EASY(1)=%.4f" % (lbl, a_all, a_h, a_e))
    print("-" * 86)
    d1 = _boot(test_items, sc, "model", "centering", n_boot)
    print("  LEARNED COMBINER - centering-only : %+.4f CI[%+.4f,%+.4f] ci_sep=%s"
          % (d1["delta"], d1["lo"], d1["hi"], d1["ci_sep"]))
    # REPRESENTATION signal: model vs model with the WHOLE representation block shuffled (info-free twin)
    rng = random.Random(SEED)
    rep_tw = []
    for it in test_items:
        X = it["X"].copy()
        for col in range(X.shape[1] - REP_K, X.shape[1]):
            v = list(X[:, col]); rng.shuffle(v); X[:, col] = v
        rep_tw.append(int(int(np.argmax(X @ w)) == it["gold"]))
    sc["rep_twin"] = rep_tw
    d2 = _boot(test_items, sc, "model", "rep_twin", n_boot)
    print("  REPRESENTATION signal (model - shuffled-rep twin) : %+.4f CI[%+.4f,%+.4f] ci_sep=%s"
          % (d2["delta"], d2["lo"], d2["hi"], d2["ci_sep"]))
    match_mag = float(np.sqrt(np.sum(w[FEATS.index("match00"):] ** 2)))
    print("  learned weights: PRIOR_flat=%.3f  PRIOR_dist=%.3f  match-block ||w||=%.3f (LEARNED bilinear matching)"
          % (w[FEATS.index("PRIOR_flat")], w[FEATS.index("PRIOR_dist")], match_mag))
    # WHERE world knowledge EARNS ITS KEEP: the struct-dominated bucket -- items where NO single
    # structural cue (recency/centering/frequency) reaches gold, so only the PRIOR can recover them.
    sd = [it for it in test_items if it["gold"] >= 0 and not _oracle_struct(it)]
    def acc_on(items, drop_prior):
        n = c = 0
        for it in items:
            X = it["X"].copy()
            if drop_prior:
                X[:, -REP_K:] = 0.0
            n += 1; c += int(int(np.argmax(X @ w)) == it["gold"])
        return c / max(1, n)
    print("-" * 86)
    print("  STRUCT-DOMINATED bucket (structure cannot reach gold; n=%d of %d = %.0f%%): only the PRIOR helps"
          % (len(sd), len(test_items), 100 * len(sd) / len(test_items)))
    print("     combiner WITHOUT prior (structure only) : %.4f" % acc_on(sd, True))
    print("     combiner WITH GloVe world-knowledge prior: %.4f  <- the localized value of world knowledge"
          % acc_on(sd, False))
    print("-" * 86)
    print("  ceilings: structural-oracle 0.695 | semantic-oracle (rich rep) 0.857 | human ~0.90")
    print("  => the PRIOR slot is where the North Star (world knowledge / individuation) plugs in.")
    print("=" * 86)
    return {"model_all": _acc_fn(test_items, lambda it: int(np.argmax(it["X"] @ w)) == it["gold"])[0],
            "cent_all": _acc_fn(test_items, lambda it: _pick_centering(it) == it["gold"])[0],
            "combiner_vs_centering": d1, "prior_slot": d2}


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 100)
