"""THE FULLY BRAIN-FOUNDATIONAL CHAIN: brain-foundational UPSTREAM (Competition-Model role assignment,
exp_brain_upstream_role_v1) -> brain-foundational STEP-5 (role-typed FHRR person-file binder,
exp_referent_coref_step5_bound_v1). Both glass-box, NO training, pinned mechanisms.

Tests the owner's thesis -- "the ONLY way to overcome the wall is for EVERY component, upstream and the
binder, to be brain-foundational." Feeds the SAME faithful FHRR binder facts from three upstreams and
compares the bound individuation signal:
  READER-positional : the reader's who-did-what (agent=preverbal noun, patient=nearest post-verbal) -- NOT brain-faithful.
  COMPETITION-MODEL : word-order-dominant cue competition + animacy tie-break + passive flip + frame gate -- PINNED, brain-foundational, glass-box, no training.
  (spaCy oracle was the ceiling diagnostic in exp_referent_coref_step5_upstream_v1: bound weight -0.048 -> +0.188.)

If COMPETITION-MODEL upstream lifts the bound signal toward the oracle, the brain-foundational upstream
is the fix; whatever residual remains localizes the LAST non-faithful link (the world-knowledge prior).

Run: .venv/Scripts/python.exe experiments/exp_referent_coref_step5_chain_v1.py
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
from hdlab.pos_tagger import PosTagger
from hdlab.situation_reader import _FRONTEND_POS_ASSET
from hdlab.state_of_mind import compatible, PRONOUN_SCOPE
from hdlab.thematic_role_labeler import lemma_verb
import experiments.exp_referent_coref_step5_ideal_v1 as I
from experiments.exp_referent_coref_step5_bound_v1 import hrr_bind, hrr_unbind, ROLE
from experiments.exp_brain_upstream_role_v1 import cm_assign, positional_assign, _animate

SEED = 20260903
FEATS = ("recency", "cb", "cb_recency", "freq", "subj_freq", "first", "parallel", "fan",
         "PRIOR_context", "PRIOR_bound")
_NOMINAL = ("NOUN", "PROPN")
_PRONS = frozenset(("he", "she", "it", "they", "we", "i", "you", "him", "her", "them", "us"))


def _facts_and_clause(sents, tagger, assign):
    """Run the upstream role assigner over every sentence; return facts_by_head[lemma]->(sent,ROLE,verb)
    and clause_by_sent[si]->(verb_lemma, probe_ROLE) from a he/she pronoun's own assigned role."""
    fb, clause = {}, {}
    for si, toks in enumerate(sents):
        toks = list(toks); pos = tagger.tag(toks)
        noun_idxs = [i for i, u in enumerate(pos) if u in _NOMINAL or toks[i].lower() in _PRONS]
        for v_idx, u in enumerate(pos):
            if u != "VERB":
                continue
            v = lemma_verb(toks[v_idx])
            ag, pt = assign(toks, pos, v_idx, noun_idxs)
            if ag not in ("?", ""):
                fb.setdefault(ag, []).append((si, "AGENT", v))
                if ag in ("he", "she") and si not in clause:
                    clause[si] = (v, ROLE["AGENT"])
            if pt not in ("?", ""):
                fb.setdefault(pt, []).append((si, "PATIENT", v))
                if pt in ("he", "she") and si not in clause:
                    clause[si] = (v, ROLE["PATIENT"])
    return fb, clause


def collect(path, gaz, glove, tagger, assign):
    mentions, n_sents = parse_litbank_conll(path, name_gender_map=gaz)
    sents = parse_conll_sentences(path)
    fb, clause_by_sent = _facts_and_clause(sents, tagger, assign)
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


def _fit(train, test, n_boot):
    d = len(FEATS)
    allrows = np.vstack([it["X"] for it in train if len(it["X"])])
    mu = allrows.mean(0); sd = allrows.std(0); sd[sd == 0] = 1.0
    for it in train + test:
        it["X"] = (it["X"] - mu) / sd
    w = I.train_condlogit(train, d)
    acc = I._acc_fn(test, lambda it: int(np.argmax(it["X"] @ w)) == it["gold"])[0]
    rng = random.Random(SEED)
    sc = {"model": [int(np.argmax(it["X"] @ w) == it["gold"]) for it in test]}
    tw = []
    for it in test:
        X = it["X"].copy(); v = list(X[:, 9]); rng.shuffle(v); X[:, 9] = v
        tw.append(int(int(np.argmax(X @ w)) == it["gold"]))
    sc["twin"] = tw
    dB = I._boot(test, sc, "model", "twin", n_boot)
    fires = sum(1 for it in test for r in it["X"] if abs(r[-1]) > 1e-9)
    return w[FEATS.index("PRIOR_bound")], acc, dB, fires


def run(n_docs=100, n_boot=1000):
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    gaz = load_given_gazetteer()
    docs = I._docs(n_docs)
    glove = I.load_glove(docs)
    tagger = PosTagger.load(_FRONTEND_POS_ASSET)
    print("=" * 88)
    print("FULLY BRAIN-FOUNDATIONAL CHAIN: upstream role assigner -> faithful FHRR step-5 binder (held-out)")
    print("-" * 88)
    for name, assign in (("READER-positional", positional_assign), ("COMPETITION-MODEL", cm_assign)):
        tr, te = [], []
        for i, (_d, p) in enumerate(docs):
            (te if (i % 10 < 3) else tr).extend(collect(p, gaz, glove, tagger, assign))
        wgt, acc, dB, fires = _fit(tr, te, n_boot)
        print("  %-18s  bound-weight=%+.3f  acc=%.4f  bound-signal=%+.4f CI[%+.4f,%+.4f] sep=%s  (fires %d)"
              % (name, wgt, acc, dB["delta"], dB["lo"], dB["hi"], dB["ci_sep"], fires))
    print("-" * 88)
    print("  (spaCy oracle ceiling was bound-weight +0.188; reader-positional in bound_v1 was -0.048)")
    print("=" * 88)


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 100)
