"""exp_parser_register_adaptation_v1 -- PARSER REGISTER-ADAPTATION prototype (owner-directed build). The
19c wall's residual blocker: the modern parser mis-extracts objects on non-canonical archaic syntax, so
the E-step's syntactic cue is unreliable and the EM store-learning plateaus. The brain ADAPTS its parser
to an unfamiliar register by ERROR-BASED structural learning (Chang, Dell & Bock 2006; Fine et al. 2013),
and the error signal comes from the SELECTIONAL PRIOR (constraint-based comprehension, MacDonald 1994):
when the parser attaches a selectionally-IMPLAUSIBLE object, that mismatch is the prediction error that
re-tunes the attachment model -- the knowledge<->parse virtuous cycle.

WHAT IS ADAPTED: a glass-box object-ATTACHMENT model P_attach(candidate = object of verb) = sigmoid(w . f),
features f = [post-verbal, -distance, nearest-post-verbal, animacy, concreteness, definiteness, bias].
Initialized position-dominant (the MODERN parser's bias). NO gold roles in training. Adapted by SELF-
TRAINING on 19c: the joint posterior q(c) ~ P_attach(c) * P_sel(c | store) is the soft pseudo-label; the
scorer is retrained toward q (so a selectionally-plausible but PRE-verbal object teaches the scorer that
19c fronts/passivizes objects), and the store is rebuilt from the adapted extractions. Iterate.

MEASURED ACROSS ADAPTATION ROUNDS (gold used for EVAL ONLY, never training):
  (a) PARSE-QUALITY curve: does P_attach's object-detection (rank gold object first) improve on the
      non-canonical 19c slice as it adapts?
  (b) STORE-RECOVERY curve: does the resulting store's which-argument accuracy on the ambiguous slice
      rise -- beat its verb-shuffled twin, approach/beat the holistic prior?
Honest prior (from _drill_19c_canonical_build): reliable extraction recovers the verb-KEYING signal (beats
twin) but the 19c holistic-parity ceiling is DENSITY + animate patients (Wall B). This build tests whether
adaptation moves parse-quality and store-recovery, and localizes the residual. NO external LLM. ASCII.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, math, sys, time
from collections import Counter, defaultdict
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
from hdlab.animacy_lexicon import lookup_animacy

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_parser_register_adaptation_v1")
_EPS = 1e-9
DEF = {"the", "this", "that", "these", "those", "his", "her", "its", "their", "my", "your", "our"}


def _sig(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


def _animacy_inanim(w):
    try:
        an = lookup_animacy(w)
    except Exception:
        an = None
    if isinstance(an, dict):
        return 0.0 if (an.get("animacy") == "animate" or an.get("category") in ("person", "animal")) else 1.0
    return 0.5


def features(r):
    """per-candidate attachment features (grounded content candidates only). Returns (list_of(h,idx,g,feat))."""
    vi = r["verb_idx"]
    toks = r["sent"].split(" ")
    post = sorted([ci for ci in r["cand_idx"] if ci > vi])
    nearest_post = post[0] if post else None
    out = []
    for h, idx in zip(r["cand_heads"], r["cand_idx"]):
        if h in V1.STOP or len(h) < 3:
            continue
        g = V1._grounded(h)
        if g is None:
            continue
        conc = float(np.asarray(g).reshape(-1)[-1])
        det = 1.0 if (0 <= idx - 1 < len(toks) and toks[idx - 1].lower().strip(".,;:'\"") in DEF) else 0.0
        feat = np.array([
            1.0 if idx > vi else 0.0,                     # post-verbal
            -min(abs(idx - vi), 12) / 12.0,               # -distance (normalized)
            1.0 if idx == nearest_post else 0.0,          # nearest post-verbal
            _animacy_inanim(h),                            # inanimate -> object-like
            max(-2.0, min(2.0, conc)) / 2.0,              # concreteness
            det,                                           # definiteness
            1.0,                                           # bias
        ], dtype=np.float64)
        out.append((h, idx, g, feat))
    return out


def p_attach(cands, w):
    if not cands:
        return np.array([])
    F = np.stack([f for _, _, _, f in cands])
    z = F @ w
    z = z - z.max()
    e = np.exp(z)
    return e / (e.sum() + _EPS)  # softmax over candidates (which is THE object)


def exemplar_fit(g, ex, knn=3):
    if not ex or g is None:
        return 0.0
    cs = sorted((V1._cos(g, ev) for _, ev in ex), reverse=True)
    return float(np.mean(cs[:min(knn, len(cs))]))


def p_sel(cands, store, verb):
    ex = store.get(verb)
    if not ex:
        return np.ones(len(cands)) / max(1, len(cands))
    s = np.array([exemplar_fit(g, ex) for _, _, g, _ in cands])
    s = s / 0.3
    s = s - s.max()
    e = np.exp(s)
    return e / (e.sum() + _EPS)


def build_store(rows_feats, q_by_item):
    soft = defaultdict(Counter)
    for (verb, cands), q in zip(rows_feats, q_by_item):
        for (h, _, _, _), qi in zip(cands, q):
            soft[verb][h] += float(qi)
    store = {}
    for v, c in soft.items():
        items = []
        for f, wt in sorted(c.items(), key=lambda kv: -kv[1]):
            g = V1._grounded(f)
            if g is not None:
                items.append((float(wt), g))
            if len(items) >= 50:
                break
        if items:
            store[v] = items
    return store


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=5)
    ap.add_argument("--seed", choices=["modern","canonical"], default="modern")
    ap.add_argument("--lr", type=float, default=0.5)
    ap.add_argument("--nboot", type=int, default=2000)
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args()
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)

    modern_store, holistic = V1.build_store(topk=50)
    modern_arms = V1.make_arms(modern_store, holistic, 3)

    rows = V1.load_pop(V1.LB)
    # precompute per-item features + verb; keep gold for EVAL only
    items = []
    for r in rows:
        cands = features(r)
        if not cands:
            continue
        items.append({"verb": V1._lem(r["verb"]), "cands": cands, "gold": r["gold_head"], "r": r})
    print("[data] %d 19c items with grounded candidates" % len(items), flush=True)

    # position-dominant init (the modern parser bias): weight post-verbal + nearest + distance
    w = np.array([1.5, 1.0, 1.5, 0.2, 0.2, 0.0, 0.0], dtype=np.float64)

    # ambiguous eval slice + gold-object eval on non-canonical
    v = lambda r: r["verb_idx"]
    npost = lambda r: sum(1 for ci in r["cand_idx"] if ci > v(r))
    amb_items = [it for it in items if (it["r"].get("voice") == "passive" or it["r"].get("noncanonical")
                                         or (npost(it["r"]) == 0 and len(it["r"]["cand_heads"]) >= 2))]
    noncanon_items = [it for it in items if (it["r"].get("voice") == "passive" or it["r"].get("noncanonical"))]

    # SEED: 'modern' (register-mismatched) or 'canonical' (reliable 19c extraction -- the best-case seed:
    # a store bootstrapped from canonical 19c sentences where position identifies the object correctly).
    if args.seed == "canonical":
        canon = [it for it in items if it["r"].get("voice") == "active" and not it["r"].get("noncanonical")]
        q_canon = []
        for it in canon:
            pa = p_attach(it["cands"], w)  # position-dominant init on RELIABLE canonical sentences
            q_canon.append(pa)
        store = build_store([(it["verb"], it["cands"]) for it in canon], q_canon)
        print("[seed] canonical-built store: %d verbs" % len(store), flush=True)
    else:
        store = dict(modern_store)
    history = []
    rows_feats = [(it["verb"], it["cands"]) for it in items]
    for rd in range(args.rounds):
        # E-step: joint posterior per item
        q_all = []
        for it in items:
            pa = p_attach(it["cands"], w)
            ps = p_sel(it["cands"], store, it["verb"])
            q = pa * ps
            q = q / (q.sum() + _EPS)
            q_all.append(q)
        # M-step (store): rebuild from q
        store = build_store(rows_feats, q_all)
        # M-step (parser): gradient step of the attachment softmax toward q (cross-entropy soft target)
        grad = np.zeros_like(w)
        for it, q in zip(items, q_all):
            F = np.stack([f for _, _, _, f in it["cands"]])
            pa = p_attach(it["cands"], w)
            grad += F.T @ (q - pa)          # softmax CE gradient toward soft target q
        w = w + args.lr * grad / max(1, len(items))

        # EVAL (gold-only): parse-quality = P_attach ranks gold object first on non-canonical
        def attach_hits(sub):
            hit = 0
            for it in sub:
                pa = p_attach(it["cands"], w)
                pick = it["cands"][int(np.argmax(pa))][0]
                hit += int(pick == it["gold"])
            return hit / len(sub) if sub else 0.0
        parse_q = attach_hits(noncanon_items)

        # store-recovery on ambiguous slice
        keys = sorted(store); perm = np.random.default_rng(41).permutation(len(keys))
        shuf = {keys[i]: keys[perm[i]] for i in range(len(keys))}
        def store_pick(it, shuffled=False):
            src = shuf.get(it["verb"], it["verb"]) if shuffled else it["verb"]
            ex = store.get(src)
            if not ex:
                return None
            best, bs = None, -1e9
            for h, idx, g, _ in it["cands"]:
                s = exemplar_fit(g, ex)
                if s > bs:
                    bs, best = s, h
            return best
        cov = [it for it in amb_items if it["verb"] in store]
        def acc(fn):
            return sum(1 for it in cov if fn(it) == it["gold"]) / len(cov) if cov else 0.0
        a_store = acc(lambda it: store_pick(it, False)); a_shuf = acc(lambda it: store_pick(it, True))
        a_hol = sum(1 for it in cov if modern_arms["HOLISTIC_CENTROID"](it["r"]) == it["gold"]) / len(cov)
        rec = {"round": rd, "parse_quality_noncanon": round(parse_q, 4), "n_cov": len(cov),
               "store_acc": round(a_store, 4), "twin_acc": round(a_shuf, 4), "holistic_acc": round(a_hol, 4),
               "w": [round(float(x), 3) for x in w]}
        history.append(rec)
        print("[round %d] parse_q(noncanon)=%.4f | store=%.4f twin=%.4f holistic=%.4f | w=%s"
              % (rd, parse_q, a_store, a_shuf, a_hol, rec["w"]), flush=True)

    out = {"anchor_name": "parser_register_adaptation_v1", "config": {"rounds": args.rounds, "lr": args.lr},
           "history": history, "elapsed_s": round(time.time() - t0, 1),
           "ts_iso": datetime.now(timezone.utc).isoformat()}
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(out, f, indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
