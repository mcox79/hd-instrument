"""STRUCTURED individuation for step-5 -- NO training. Represent each character by the reader's OWN
extracted, role-typed FACTS (its actions + attributes), the way the brain binds a mental file, instead
of a GloVe bag-of-context-words.

WHY (owner, 2026-09-03): four GloVe-context encodings (flat/cumulative/distinctive/learned-bilinear) all
converged at ~0.55 because a context CENTROID averages -- superposition WITHOUT structure -- which
destroys the role-bindings individuation needs, AND because we were RE-DERIVING a crude bag-of-words while
the reader ALREADY extracts each character's structured facts upstream and step-5 threw them away:
  - sm.entity_states : the copular is-a/attribute organ ("Ahab was a captain", "she was anxious") -- the
    HOLDER's individuating ATTRIBUTES (the landed organ from wire_the_referent_to_coref_linking's parent).
  - sm.events        : who-did-what (agent/patient/predicate) -- the character's ACTIONS.
This organ binds those upstream facts into a per-character profile (mental file / DRT referent; one-shot,
NO training) and resolves "she" by THEMATIC/ATTRIBUTE fit: which candidate's bound facts cohere with the
current clause. GloVe is used ONLY as the concept-similarity metric (a semantic-hub proxy), not as the
representation. Past-only (facts from sentences BEFORE the pronoun); glass-box; NO external LLM; NO training.

Compares, held-out: structure-only vs +context-bag (the old flat prior) vs +STRUCTURED-FACTS (this), with
shuffled-fact info-free twins, on the general + struct-dominated buckets.

Run: .venv/Scripts/python.exe experiments/exp_referent_coref_step5_structured_v1.py
"""
import math
import os
import random
import sys

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.situation_reader import SituationReader
from hdlab.coref import parse_litbank_conll, build_pronoun_targets
from hdlab.scene_segment import parse_conll_sentences
from hdlab.state_of_mind import compatible, PRONOUN_SCOPE
import experiments.exp_referent_coref_step5_ideal_v1 as I   # reuse: _docs,_animate,_content,load_glove,_centroid,train_condlogit,_boot,_acc_fn,_pick_centering,_oracle_struct

SEED = 20260903
FEATS = ("recency", "cb", "cb_recency", "freq", "subj_freq", "first", "parallel", "fan",
         "PRIOR_context", "PRIOR_facts")


def _facts_by_head(sm):
    """head(lower) -> list of (sent_idx, fact_word): the character's ACTIONS (event predicates where it is
    agent/patient) + ATTRIBUTES (copular state properties where it is holder). The reader's own extractions."""
    fb = {}
    for e in sm.events:
        pred = (e.predicate or "").lower()
        if not pred:
            continue
        for h in (e.agent, e.patient):
            h = (h or "").lower().strip()
            if h and h not in ("?", "none") and len(h) >= 2:
                fb.setdefault(h, []).append((e.sent_idx, pred))
    for s in sm.entity_states:
        prop = (s.property or "").lower()
        h = (s.holder or "").lower().strip()
        if prop and h and len(h) >= 2:
            fb.setdefault(h, []).append((s.sent_idx, prop))
    return fb


def collect(path, gaz, glove, reader):
    sm = reader.read(path)
    fb = _facts_by_head(sm)
    mentions, n_sents = parse_litbank_conll(path, name_gender_map=gaz)
    sents = parse_conll_sentences(path)
    cc = {}

    def csent(si):
        if si not in cc:
            cc[si] = I._content(sents[si]) if 0 <= si < len(sents) else set()
        return cc[si]

    targets = build_pronoun_targets(mentions)
    tgt = {t["target"]["midx"] for t in targets}
    ent = {}
    order = 0
    items = []
    for m in mentions:
        if m["is_pronoun"] and m["midx"] in tgt:
            sc = PRONOUN_SCOPE[m["head"]]
            cur = m["sent_idx"]
            pron_subj = (m.get("sent_role_rank", 99) == 0)
            clause_vec = I._centroid(csent(cur), glove)
            pool = [(cl, e) for cl, e in ent.items()
                    if e["animate"] and compatible(sc["gender"], sc["number"], e["gender"], e["number"])]
            if pool:
                rows, raws, gold_row = [], [], -1
                for i, (cl, e) in enumerate(pool):
                    subj_gap = (cur - e["last_subj_sent"]) if e["last_subj_sent"] >= 0 else 99
                    share = sum(1 for _c2, e2 in pool if abs(e2["last_order"] - e["last_order"]) <= 1)
                    # PRIOR_context = flat GloVe context centroid (the old, structure-destroying bag)
                    ev = e["gvec"]
                    coh_ctx = float(np.dot(ev, clause_vec)) if (ev is not None and clause_vec is not None) else 0.0
                    # PRIOR_facts = the entity's bound EXTRACTED FACTS (past-only), matched to the clause
                    fwords = [w for h in e["heads"] for (si, w) in fb.get(h, []) if si < cur]
                    fvec = I._centroid(fwords, glove)
                    coh_facts = float(np.dot(fvec, clause_vec)) if (fvec is not None and clause_vec is not None) else 0.0
                    rows.append([
                        -math.log(2 + (order - e["last_order"])), 1.0 if subj_gap <= 3 else 0.0,
                        -math.log(2 + subj_gap), math.log(1 + e["count"]), math.log(1 + e["subj_count"]),
                        -math.log(2 + (cur - e["first_sent"])), 1.0 if (pron_subj and subj_gap <= 3) else 0.0,
                        -math.log(1 + share), coh_ctx, coh_facts,
                    ])
                    raws.append((e["last_subj_sent"], e["last_order"], e["count"]))
                    if cl == m["cluster"]:
                        gold_row = i
                items.append({"X": np.array(rows, dtype=np.float64), "gold": gold_row,
                              "ncomp": len(pool), "raws": raws})
        if not m["is_pronoun"]:
            cl = m["cluster"]
            e = ent.get(cl)
            if e is None:
                e = {"count": 0, "subj_count": 0, "last_order": -1, "last_subj_sent": -10,
                     "first_sent": m["sent_idx"], "gender": m.get("gender"), "number": m.get("number"),
                     "animate": I._animate(m, gaz), "seen": set(), "gsum": np.zeros(300), "gvec": None,
                     "heads": set()}
                ent[cl] = e
            e["count"] += 1; e["last_order"] = order; e["heads"].add(m["head"].lower())
            for w in csent(m["sent_idx"]):
                if w not in e["seen"] and w in glove:
                    e["gsum"] = e["gsum"] + glove[w]; e["seen"].add(w)
            nrm = np.linalg.norm(e["gsum"])
            e["gvec"] = (e["gsum"] / nrm) if nrm > 1e-9 else None
            if e["gender"] is None and m.get("gender") is not None:
                e["gender"] = m["gender"]
            if m.get("sent_role_rank", 99) == 0:
                e["last_subj_sent"] = m["sent_idx"]; e["subj_count"] += 1
        order += 1
    return items


def run(n_docs=100, n_boot=1000):
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    gaz = load_given_gazetteer()
    docs = I._docs(n_docs)
    glove = I.load_glove(docs)
    reader = SituationReader(gaz=gaz)
    train_items, test_items = [], []
    for i, (_d, p) in enumerate(docs):
        (test_items if (i % 10 < 3) else train_items).extend(collect(p, gaz, glove, reader))
    d = len(FEATS)
    allrows = np.vstack([it["X"] for it in train_items if len(it["X"])])
    mu = allrows.mean(0); sd = allrows.std(0); sd[sd == 0] = 1.0
    for it in train_items + test_items:
        it["X"] = (it["X"] - mu) / sd
    w = I.train_condlogit(train_items, d)

    model_hit = [int(np.argmax(it["X"] @ w) == it["gold"]) for it in test_items]
    cent_hit = [int(I._pick_centering(it) == it["gold"]) for it in test_items]
    sc = {"model": model_hit, "centering": cent_hit}

    print("=" * 86)
    print("STRUCTURED (upstream-fed) INDIVIDUATION  (held-out: %d train / %d test)" % (len(train_items), len(test_items)))
    for name, wt in sorted(zip(FEATS, w), key=lambda z: -abs(z[1])):
        print("     %-14s % .3f" % (name, wt))
    print("-" * 86)

    def acc_drop(items, cols, lo=1, hi=99):
        n = c = 0
        for it in items:
            if not (lo <= it["ncomp"] <= hi):
                continue
            X = it["X"].copy(); X[:, cols] = 0.0
            n += 1; c += int(int(np.argmax(X @ w)) == it["gold"])
        return c / max(1, n)
    print("  centering-only                 ALL=%.4f" % I._acc_fn(test_items, lambda it: I._pick_centering(it) == it["gold"])[0])
    print("  structure-only (drop both priors)  ALL=%.4f  HARD=%.4f" % (acc_drop(test_items, [8, 9]), acc_drop(test_items, [8, 9], lo=2)))
    print("  + context bag only (drop facts)    ALL=%.4f  HARD=%.4f" % (acc_drop(test_items, [9]), acc_drop(test_items, [9], lo=2)))
    print("  + STRUCTURED FACTS only (drop ctx) ALL=%.4f  HARD=%.4f" % (acc_drop(test_items, [8]), acc_drop(test_items, [8], lo=2)))
    print("  FULL (context + facts)             ALL=%.4f  HARD=%.4f" %
          (I._acc_fn(test_items, lambda it: int(np.argmax(it["X"] @ w)) == it["gold"])[0],
           I._acc_fn(test_items, lambda it: int(np.argmax(it["X"] @ w)) == it["gold"], lo=2)[0]))
    print("-" * 86)
    # shuffled-FACTS info-free twin (isolate the structured-facts signal)
    rng = random.Random(SEED); ftw = []
    for it in test_items:
        X = it["X"].copy(); v = list(X[:, 9]); rng.shuffle(v); X[:, 9] = v
        ftw.append(int(int(np.argmax(X @ w)) == it["gold"]))
    sc["facts_twin"] = ftw
    dF = I._boot(test_items, sc, "model", "facts_twin", n_boot)
    dC = I._boot(test_items, sc, "model", "centering", n_boot)
    print("  FACTS signal (model - shuffled-facts twin) : %+.4f CI[%+.4f,%+.4f] ci_sep=%s" % (dF["delta"], dF["lo"], dF["hi"], dF["ci_sep"]))
    print("  FULL - centering-only                      : %+.4f CI[%+.4f,%+.4f] ci_sep=%s" % (dC["delta"], dC["lo"], dC["hi"], dC["ci_sep"]))
    print("  ceilings: structural-oracle 0.695 | semantic-oracle 0.857 | human ~0.90")
    print("=" * 86)


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 100)
