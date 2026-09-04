"""IS THE UPSTREAM THE BOTTLENECK? Feed the brain-faithful role-typed FHRR step-5 binder CLEAN facts
from a competent-reader parse (spaCy, reference-only diagnostic oracle) instead of the reader's
POSITIONAL who-did-what (agent='streets', patient='?'), and measure whether the bound individuation
signal comes alive.

EVALUATION (owner, 2026-09-03): the reader's upstream role assignment (_assign_roles) is PURELY
POSITIONAL -- "AGENT = subject-position noun, PATIENT = nearest post-verbal noun" -- which is NOT the
brain's mechanism (thematic-role CUE INTEGRATION: word order + animacy + voice + verb argument
structure; the Competition Model, MacWhinney-Bates). So the facts the step-5 binder consumed were
noisy, and the "world-knowledge prior is required" conclusion was premature UNTIL we test clean input.

This cell holds the faithful step-5 mechanism FIXED (role-typed FHRR bind + cue-based unbinding,
hdlab.binding HRR path; GloVe fillers; NO training) and swaps ONLY the upstream fact source to a clean
spaCy dependency parse (nsubj->AGENT o verb, dobj/dative/attr/oprd/pobj->PATIENT o verb, acomp/amod->
ATTR o adj; the pronoun's own nsubj/dobj gives the clause predicate + probe role). spaCy = the
project's competent-reader diagnostic oracle (reference-only; NOT shipped at inference). If the bound
signal CI-separates with clean upstream, the upstream -- not the step-5 mechanism -- was the bottleneck,
and the brain-faithful buildable fix is thematic-fit role assignment (hdlab.thematic_role_labeler).

Run: .venv/Scripts/python.exe experiments/exp_referent_coref_step5_upstream_v1.py
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

from hdlab.coref import parse_litbank_conll, build_pronoun_targets
from hdlab.scene_segment import parse_conll_sentences
from hdlab.state_of_mind import compatible, PRONOUN_SCOPE
import experiments.exp_referent_coref_step5_ideal_v1 as I
from experiments.exp_referent_coref_step5_bound_v1 import hrr_bind, hrr_unbind, ROLE

SEED = 20260903
FEATS = ("recency", "cb", "cb_recency", "freq", "subj_freq", "first", "parallel", "fan",
         "PRIOR_context", "PRIOR_bound")
_OBJ = frozenset(("dobj", "dative", "attr", "oprd", "pobj"))
_PRON = frozenset(("he", "she", "him", "her", "himself", "herself"))


def parse_doc(sents, nlp):
    """spaCy clean upstream: facts_by_head[lemma] -> [(sent_idx, ROLE, filler)] and clause_by_sent[si]
    -> (pred_lemma, probe_role) from the he/she pronoun's own syntactic role."""
    fb, clause = {}, {}
    strs = [" ".join(s) for s in sents]
    for si, doc in enumerate(nlp.pipe(strs, disable=["ner"])):
        for t in doc:
            if t.pos_ == "VERB":
                v = t.lemma_.lower()
                for c in t.children:
                    cl = c.lemma_.lower()
                    if c.dep_ in ("nsubj", "nsubjpass"):
                        (fb.setdefault(cl, []).append((si, "AGENT", v)))
                        if c.text.lower() in _PRON and si not in clause:
                            clause[si] = (v, ROLE["AGENT"])
                    elif c.dep_ in _OBJ:
                        (fb.setdefault(cl, []).append((si, "PATIENT", v)))
                        if c.text.lower() in _PRON and si not in clause:
                            clause[si] = (v, ROLE["PATIENT"])
            if t.dep_ in ("acomp", "amod") and t.pos_ == "ADJ":
                head = t.head.lemma_.lower()
                fb.setdefault(head, []).append((si, "ATTR", t.lemma_.lower()))
    return fb, clause


def collect(path, gaz, glove, nlp):
    mentions, n_sents = parse_litbank_conll(path, name_gender_map=gaz)
    sents = parse_conll_sentences(path)
    fb, clause_by_sent = parse_doc(sents, nlp)
    cc = {}

    def csent(si):
        if si not in cc:
            cc[si] = I._content(sents[si]) if 0 <= si < len(sents) else set()
        return cc[si]

    targets = build_pronoun_targets(mentions)
    tgt = {t["target"]["midx"] for t in targets}
    ent, order, items = {}, 0, []
    for m in mentions:
        if m["is_pronoun"] and m["midx"] in tgt:
            sc = PRONOUN_SCOPE[m["head"]]; cur = m["sent_idx"]
            pron_subj = (m.get("sent_role_rank", 99) == 0)
            clause_vec = I._centroid(csent(cur), glove)
            cp = clause_by_sent.get(cur)
            clause_pred = glove.get(cp[0]) if (cp and cp[0] in glove) else None
            probe = cp[1] if cp else (ROLE["AGENT"] if pron_subj else ROLE["PATIENT"])
            pool = [(cl, e) for cl, e in ent.items()
                    if e["animate"] and compatible(sc["gender"], sc["number"], e["gender"], e["number"])]
            if pool:
                rows, gold_row = [], -1
                for i, (cl, e) in enumerate(pool):
                    subj_gap = (cur - e["last_subj_sent"]) if e["last_subj_sent"] >= 0 else 99
                    share = sum(1 for _c2, e2 in pool if abs(e2["last_order"] - e["last_order"]) <= 1)
                    ev = e["gvec"]
                    coh_ctx = float(np.dot(ev, clause_vec)) if (ev is not None and clause_vec is not None) else 0.0
                    coh_bound = 0.0
                    if clause_pred is not None:
                        fvec, got = np.zeros(300), False
                        for h in e["heads"]:
                            for (si, role, wd) in fb.get(h, []):
                                if si < cur and wd in glove:
                                    fvec = fvec + hrr_bind(ROLE[role], glove[wd]); got = True
                        if got:
                            nn = np.linalg.norm(fvec)
                            if nn > 1e-9:
                                retr = hrr_unbind(fvec / nn, probe); rn = np.linalg.norm(retr)
                                if rn > 1e-9:
                                    coh_bound = float(np.dot(retr / rn, clause_pred))
                    rows.append([
                        -math.log(2 + (order - e["last_order"])), 1.0 if subj_gap <= 3 else 0.0,
                        -math.log(2 + subj_gap), math.log(1 + e["count"]), math.log(1 + e["subj_count"]),
                        -math.log(2 + (cur - e["first_sent"])), 1.0 if (pron_subj and subj_gap <= 3) else 0.0,
                        -math.log(1 + share), coh_ctx, coh_bound,
                    ])
                    if cl == m["cluster"]:
                        gold_row = i
                items.append({"X": np.array(rows, dtype=np.float64), "gold": gold_row, "ncomp": len(pool)})
        if not m["is_pronoun"]:
            cl = m["cluster"]; e = ent.get(cl)
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
            nrm = np.linalg.norm(e["gsum"]); e["gvec"] = (e["gsum"] / nrm) if nrm > 1e-9 else None
            if e["gender"] is None and m.get("gender") is not None:
                e["gender"] = m["gender"]
            if m.get("sent_role_rank", 99) == 0:
                e["last_subj_sent"] = m["sent_idx"]; e["subj_count"] += 1
        order += 1
    return items


def run(n_docs=100, n_boot=1000):
    import spacy
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    gaz = load_given_gazetteer()
    docs = I._docs(n_docs)
    glove = I.load_glove(docs)
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    train_items, test_items = [], []
    for i, (_d, p) in enumerate(docs):
        (test_items if (i % 10 < 3) else train_items).extend(collect(p, gaz, glove, nlp))
    d = len(FEATS)
    allrows = np.vstack([it["X"] for it in train_items if len(it["X"])])
    mu = allrows.mean(0); sd = allrows.std(0); sd[sd == 0] = 1.0
    for it in train_items + test_items:
        it["X"] = (it["X"] - mu) / sd
    w = I.train_condlogit(train_items, d)
    n_fire = sum(1 for it in test_items for r in it["X"] if abs(r[-1]) > 1e-9)
    sc = {"model": [int(np.argmax(it["X"] @ w) == it["gold"]) for it in test_items]}
    print("=" * 88)
    print("CLEAN-UPSTREAM (spaCy) FEEDING THE FAITHFUL BOUND BINDER  (held-out %d/%d ; bound fires %d rows)"
          % (len(train_items), len(test_items), n_fire))
    for name, wt in sorted(zip(FEATS, w), key=lambda z: -abs(z[1])):
        print("     %-14s % .3f" % (name, wt))

    def acc_drop(cols, lo=1, hi=99):
        n = c = 0
        for it in test_items:
            if not (lo <= it["ncomp"] <= hi):
                continue
            X = it["X"].copy(); X[:, cols] = 0.0
            n += 1; c += int(int(np.argmax(X @ w)) == it["gold"])
        return c / max(1, n)
    print("-" * 88)
    print("  structure-only (drop priors)   ALL=%.4f  HARD=%.4f" % (acc_drop([8, 9]), acc_drop([8, 9], lo=2)))
    print("  + context only (drop bound)    ALL=%.4f  HARD=%.4f" % (acc_drop([9]), acc_drop([9], lo=2)))
    print("  + CLEAN BOUND only (drop ctx)  ALL=%.4f  HARD=%.4f" % (acc_drop([8]), acc_drop([8], lo=2)))
    print("  FULL                           ALL=%.4f  HARD=%.4f" %
          (I._acc_fn(test_items, lambda it: int(np.argmax(it["X"] @ w)) == it["gold"])[0],
           I._acc_fn(test_items, lambda it: int(np.argmax(it["X"] @ w)) == it["gold"], lo=2)[0]))
    rng = random.Random(SEED); btw = []
    for it in test_items:
        X = it["X"].copy(); v = list(X[:, 9]); rng.shuffle(v); X[:, 9] = v
        btw.append(int(int(np.argmax(X @ w)) == it["gold"]))
    sc["bound_twin"] = btw
    dB = I._boot(test_items, sc, "model", "bound_twin", n_boot)
    print("-" * 88)
    print("  CLEAN-BOUND signal (model - shuffled-bound twin) : %+.4f CI[%+.4f,%+.4f] ci_sep=%s"
          % (dB["delta"], dB["lo"], dB["hi"], dB["ci_sep"]))
    print("  (reader-upstream bound was -0.001, NOT CI-sep -- so a CLEAN-BOUND win localizes the bottleneck UPSTREAM)")
    print("=" * 88)


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 100)
