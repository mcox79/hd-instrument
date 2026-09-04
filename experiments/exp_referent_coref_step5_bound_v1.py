"""BRAIN-FAITHFUL (role-typed, bound, NO-training) individuation for step-5 -- the mechanism the
2026-09-03 research probe pinned:
  BINDER   = hippocampal fast conjunctive binding + pattern completion == VSA/HRR bind+bundle+cleanup
             (the substrate's FHRR basis; hdlab.binding). Duff & Brown-Schmidt 2012 (FULL-TEXT) tie
             hippocampal relational binding causally to referential processing.
  RETRIEVER= cue-based content-addressable retrieval (Lewis & Vasishth 2005) -- ROLE-TYPED unbinding,
             graded similarity. The interference literature warns a FLAT similarity over pooled facts
             OVER-retrieves; role-typing the cue (probe the thematic slot the predicate demands, not a
             blended blob) is the fix -- which the four GloVe-centroid attempts violated by averaging.
  ACCESS   = animacy+agreement pre-filter (DRT-accessibility analogue).

Each character's mental file = bundle over its reader-extracted facts of bind(ROLE, GloVe(filler)):
{AGENT o pred} for verbs it did, {PATIENT o pred} for verbs done to it, {ATTR o property} for its
copular states (the landed copular organ). To resolve "she", probe the file at the pronoun's own role
with the clause predicate: score = cos( unbind(file, probe_role), GloVe(clause_predicate) ) -- "does
this character have a role-appropriate fact that fits what is happening now." GloVe supplies the
MEANING of each filler; HRR supplies the STRUCTURE (role binding) that averaging destroyed. Past-only;
glass-box; NO external LLM; NO training. (HRR bind/unbind = the hdlab.binding HRR path, inlined in
numpy for speed; the OPERATION is identical -- the proposed wire reuses hdlab.binding.)

The predicate-fit SELECTION step is honestly OUR-INVENTION on pinned primitives (the probe found no
work pinning it for pronouns; Kehler-Rohde warn a bare fit-score can be epiphenomenal of a next-mention
prior) -- so this measures whether the faithful bound mechanism carries CI-separated signal over its
info-free twin, i.e. whether the STRUCTURE (vs the averaged blob) recovers usable individuation.

Run: .venv/Scripts/python.exe experiments/exp_referent_coref_step5_bound_v1.py
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
import experiments.exp_referent_coref_step5_ideal_v1 as I

SEED = 20260903
FEATS = ("recency", "cb", "cb_recency", "freq", "subj_freq", "first", "parallel", "fan",
         "PRIOR_context", "PRIOR_bound")
_rng = np.random.default_rng(SEED)
ROLE = {r: (lambda v: v / np.linalg.norm(v))(_rng.standard_normal(300)) for r in ("AGENT", "PATIENT", "ATTR")}


def hrr_bind(a, b):
    return np.fft.irfft(np.fft.rfft(a) * np.fft.rfft(b), n=len(a))


def hrr_unbind(c, b):
    return np.fft.irfft(np.fft.rfft(c) * np.conj(np.fft.rfft(b)), n=len(c))


def _facts_roled(sm):
    """head(lower) -> list of (sent_idx, ROLE, filler_word) from the reader's OWN extractions."""
    fb = {}
    for e in sm.events:
        pred = (e.predicate or "").lower()
        if not pred:
            continue
        a = (e.agent or "").lower().strip()
        if a and a not in ("?", "none") and len(a) >= 2:
            fb.setdefault(a, []).append((e.sent_idx, "AGENT", pred))
        p = (e.patient or "").lower().strip()
        if p and p not in ("?", "none") and len(p) >= 2:
            fb.setdefault(p, []).append((e.sent_idx, "PATIENT", pred))
    for s in sm.entity_states:
        prop = (s.property or "").lower(); h = (s.holder or "").lower().strip()
        if prop and h and len(h) >= 2:
            fb.setdefault(h, []).append((s.sent_idx, "ATTR", prop))
    return fb


def _clause_pred(sm_events_by_sent, cur, glove):
    """The clause's predicate GloVe vector: the first GloVe-covered event predicate in the pronoun's sentence."""
    for e in sm_events_by_sent.get(cur, []):
        p = (e.predicate or "").lower()
        if p in glove:
            return glove[p]
    return None


def collect(path, gaz, glove, reader):
    sm = reader.read(path)
    fb = _facts_roled(sm)
    ev_by_sent = {}
    for e in sm.events:
        ev_by_sent.setdefault(e.sent_idx, []).append(e)
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
            probe = ROLE["AGENT"] if pron_subj else ROLE["PATIENT"]
            clause_vec = I._centroid(csent(cur), glove)
            clause_pred = _clause_pred(ev_by_sent, cur, glove)
            pool = [(cl, e) for cl, e in ent.items()
                    if e["animate"] and compatible(sc["gender"], sc["number"], e["gender"], e["number"])]
            if pool:
                rows, gold_row, raws = [], -1, []
                for i, (cl, e) in enumerate(pool):
                    subj_gap = (cur - e["last_subj_sent"]) if e["last_subj_sent"] >= 0 else 99
                    share = sum(1 for _c2, e2 in pool if abs(e2["last_order"] - e["last_order"]) <= 1)
                    ev = e["gvec"]
                    coh_ctx = float(np.dot(ev, clause_vec)) if (ev is not None and clause_vec is not None) else 0.0
                    # BOUND role-typed retrieval: build the entity's file (past-only), unbind the probe role,
                    # match to the clause predicate. NO averaging -- each fact keeps its role binding.
                    coh_bound = 0.0
                    if clause_pred is not None:
                        fvec = np.zeros(300)
                        got = False
                        for h in e["heads"]:
                            for (si, role, w) in fb.get(h, []):
                                if si < cur and w in glove:
                                    fvec = fvec + hrr_bind(ROLE[role], glove[w]); got = True
                        if got:
                            nn = np.linalg.norm(fvec)
                            if nn > 1e-9:
                                retr = hrr_unbind(fvec / nn, probe)
                                rn = np.linalg.norm(retr)
                                if rn > 1e-9:
                                    coh_bound = float(np.dot(retr / rn, clause_pred))
                    rows.append([
                        -math.log(2 + (order - e["last_order"])), 1.0 if subj_gap <= 3 else 0.0,
                        -math.log(2 + subj_gap), math.log(1 + e["count"]), math.log(1 + e["subj_count"]),
                        -math.log(2 + (cur - e["first_sent"])), 1.0 if (pron_subj and subj_gap <= 3) else 0.0,
                        -math.log(1 + share), coh_ctx, coh_bound,
                    ])
                    raws.append((e["last_subj_sent"], e["last_order"], e["count"]))
                    if cl == m["cluster"]:
                        gold_row = i
                items.append({"X": np.array(rows, dtype=np.float64), "gold": gold_row,
                              "ncomp": len(pool), "raws": raws})
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

    n_fire = sum(1 for it in test_items for r in it["X"] if abs(r[-1]) > 1e-9)   # how often the bound cue fires
    sc = {"model": [int(np.argmax(it["X"] @ w) == it["gold"]) for it in test_items],
          "centering": [int(I._pick_centering(it) == it["gold"]) for it in test_items]}
    print("=" * 86)
    print("BRAIN-FAITHFUL BOUND (role-typed FHRR) INDIVIDUATION  (held-out %d/%d ; bound cue fires on %d cand-rows)"
          % (len(train_items), len(test_items), n_fire))
    for name, wt in sorted(zip(FEATS, w), key=lambda z: -abs(z[1])):
        print("     %-14s % .3f" % (name, wt))
    print("-" * 86)

    def acc_drop(cols, lo=1, hi=99):
        n = c = 0
        for it in test_items:
            if not (lo <= it["ncomp"] <= hi):
                continue
            X = it["X"].copy(); X[:, cols] = 0.0
            n += 1; c += int(int(np.argmax(X @ w)) == it["gold"])
        return c / max(1, n)
    print("  centering-only                     ALL=%.4f" % I._acc_fn(test_items, lambda it: I._pick_centering(it) == it["gold"])[0])
    print("  structure-only (drop both priors)  ALL=%.4f  HARD=%.4f" % (acc_drop([8, 9]), acc_drop([8, 9], lo=2)))
    print("  + context only (drop bound)        ALL=%.4f  HARD=%.4f" % (acc_drop([9]), acc_drop([9], lo=2)))
    print("  + BOUND only (drop context)        ALL=%.4f  HARD=%.4f" % (acc_drop([8]), acc_drop([8], lo=2)))
    print("  FULL                               ALL=%.4f  HARD=%.4f" %
          (I._acc_fn(test_items, lambda it: int(np.argmax(it["X"] @ w)) == it["gold"])[0],
           I._acc_fn(test_items, lambda it: int(np.argmax(it["X"] @ w)) == it["gold"], lo=2)[0]))
    print("-" * 86)
    rng = random.Random(SEED); btw = []
    for it in test_items:
        X = it["X"].copy(); v = list(X[:, 9]); rng.shuffle(v); X[:, 9] = v
        btw.append(int(int(np.argmax(X @ w)) == it["gold"]))
    sc["bound_twin"] = btw
    dB = I._boot(test_items, sc, "model", "bound_twin", n_boot)
    print("  BOUND signal (model - shuffled-bound twin) : %+.4f CI[%+.4f,%+.4f] ci_sep=%s" % (dB["delta"], dB["lo"], dB["hi"], dB["ci_sep"]))
    print("=" * 86)


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 100)
