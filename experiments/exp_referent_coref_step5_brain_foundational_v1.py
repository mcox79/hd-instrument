"""EXACT brain-foundational STEP-5 pronoun-antecedent selector.

Implements the pronoun-resolution architecture the literature actually specifies (the deltas from the
owner-DONE `who_has_what_needs_a_coherence_next_mention_prior_kehler_rohde` lit-scan, built here as the
prescribed-but-unbuilt two-stage form), NOT a flat weighted cue blend:

  BONDING (Garrod & Sanford 1989; fast, automatic) -- CENTERING (Grosz-Joshi-Weinstein 1995): resolve
    to the backward-looking center Cb (the most-recently-SUBJECT compatible entity) WHEN it uniquely
    and recently determines the referent. This is the fast path; on the easy cases it is the answer.
  RESOLUTION (slow, knowledge-driven) -- invoked ONLY when bonding under-determines (2+ centers, none
    recently/uniquely dominant = the Nref state). Here the COHERENCE next-mention PRIOR enters as a
    SEPARATE term (Kehler & Rohde 2013, full-text: P(ref|pron) proportional to P(pron|ref) x P(ref),
    NOT a bag-of-cues blend). Glass-box prior = content cohesion between the candidate's context and the
    pronoun's clause (Kintsch situation-model cohesion; the buildable proxy for the semantic channel).
  TWO-PASS control flow (Chow, Lewis & Phillips 2014): the prior is a SECOND pass triggered by first-pass
    (bonding) failure -- a gated hierarchy, which is what makes this genuinely different from one flat
    softmax (separately-normalized exponential terms would collapse to a flat blend; the GATE is the
    nonlinearity).
  GERNSBACHER (1989) asymmetric enhancement: resolving a pronoun to c makes c the realized center --
    enhance c's salience (and, as a subject pronoun, its Cb) as running state for the NEXT pronoun
    (read-modify-write, not passive decay).
  LEWIS-VASISHTH (2005) / BADECKER-STRAUB (2002) interference: a discrete competitor-count (fan)
    penalty in the resolution pass.

Everything is glass-box, symbolic, NO external LLM, NO gold seen at decision time. The SEMANTIC prior is
a deliberately-simple cohesion proxy: its ceiling is the rich per-entity individuation representation
(the priority-1 North Star), which this cell BOUNDS but does not build.

Controls: SHUFFLED-COHERENCE twin (permute the prior across candidates -> the forward signal, not the
machinery, must do the work); NO-REGRESSION on the easy 1-competitor cases; the interference signature.

Run: .venv/Scripts/python.exe experiments/exp_referent_coref_step5_brain_foundational_v1.py
"""
import json
import math
import os
import random
import sys

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
_STOP = frozenset(("the a an and or but of to in on at for with by from as it he she they we you i "
                   "his her their its my your our this that these those was were is are be been being "
                   "had has have do did does not no so then than there here what which who whom when "
                   "him them us me himself herself them then said say says one all any some more most "
                   "such very can could would should will shall may might must into out up down over "
                   "again about after before while because if though").split())


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


def resolve_doc(path, gaz, params):
    """Online single pass: replay the mention stream, resolve each he/she target with the exact-brain
    two-pass selector + Gernsbacher enhancement, and score against gold. Returns per-target
    (correct, n_competitors). params selects ablations."""
    mentions, n_sents = parse_litbank_conll(path, name_gender_map=gaz)
    sents = parse_conll_sentences(path)
    content_cache = [None] * len(sents)

    def csent(si):
        if 0 <= si < len(sents):
            if content_cache[si] is None:
                content_cache[si] = _content(sents[si])
            return content_cache[si]
        return set()

    targets = build_pronoun_targets(mentions)
    tgt_midx = {t["target"]["midx"] for t in targets}
    ent = {}            # cluster -> dict(count,last_order,last_subj_sent,gender,number,animate,profile)
    order = 0
    recs = []
    diag = {"n_targets": 0, "gold_in_pool": 0, "bonded": 0, "bonded_correct": 0,
            "resolution": 0, "res_correct": 0, "reachable": 0, "oracle_amb": 0}
    rng = random.Random(params.get("shuffle_seed", 0))
    WIN = params["win"]; K = params["k"]
    use_prior = params["use_prior"]; use_fan = params["use_fan"]; shuffle = params["shuffle_prior"]
    gern = params["gernsbacher"]; cumulative = params.get("cumulative", False)

    for m in mentions:
        if m["is_pronoun"] and m["midx"] in tgt_midx:
            sc = PRONOUN_SCOPE[m["head"]]
            cur_sent = m["sent_idx"]
            pool = [(cl, e) for cl, e in ent.items()
                    if e["animate"] and compatible(sc["gender"], sc["number"], e["gender"], e["number"])]
            if pool:
                diag["n_targets"] += 1
                if any(cl == m["cluster"] for cl, _e in pool):
                    diag["gold_in_pool"] += 1
                # ---- PASS 1: BONDING (Centering Cb: most-recently-subject, recency tie-break) ----
                ranked = sorted(pool, key=lambda ce: (ce[1]["last_subj_sent"], ce[1]["last_order"]),
                                reverse=True)
                top = ranked[0]
                second = ranked[1] if len(ranked) > 1 else None
                bonded = None
                cb_unique = (second is None or top[1]["last_subj_sent"] > second[1]["last_subj_sent"])
                cb_recent = (cur_sent - top[1]["last_subj_sent"]) <= WIN and top[1]["last_subj_sent"] >= 0
                if cb_unique and cb_recent:
                    bonded = top[0]                                   # fast path commits
                # ---- PASS 2: RESOLUTION (ambiguous) -- coherence prior + interference ----
                if bonded is not None:
                    pick = bonded
                    diag["bonded"] += 1
                    diag["bonded_correct"] += int(pick == m["cluster"])
                else:
                    diag["resolution"] += 1
                    amb = ranked[:K] if K else ranked
                    pron_ctx = csent(cur_sent)
                    coh = {}
                    for cl, e in amb:
                        prof = e["profile"] if cumulative else (csent(e["last_sent"]) if e.get("last_sent") is not None else set())
                        coh[cl] = len(pron_ctx & prof)
                    amb_cls = {cl for cl, _e in amb}
                    if m["cluster"] in amb_cls:
                        diag["reachable"] += 1
                        if coh.get(m["cluster"], -1) == max(coh.values()) and max(coh.values()) > 0:
                            diag["oracle_amb"] += 1
                    if shuffle:                                       # info-free twin: scramble the prior
                        vals = list(coh.values()); rng.shuffle(vals)
                        coh = {cl: vals[i] for i, (cl, _e) in enumerate(amb)}
                    def score(ce):
                        cl, e = ce
                        s = -math.log(2 + (order - e["last_order"]))  # likelihood: recency (log base-level)
                        s += 0.5 * (1.0 if e["last_subj_sent"] >= 0 and (cur_sent - e["last_subj_sent"]) <= WIN + 2 else 0.0)
                        if use_prior:
                            s += params["w_prior"] * coh[cl]          # SEPARATE coherence prior term
                        if use_fan:                                   # Lewis-Vasishth fan: penalize shared-cue crowding
                            share = sum(1 for c2, e2 in amb if abs(e2["last_order"] - e["last_order"]) <= 1)
                            s -= 0.15 * math.log(share)
                        return s
                    pick = max(amb, key=score)[0]
                    diag["res_correct"] += int(pick == m["cluster"])
                recs.append((pick == m["cluster"], len(pool)))
                # ---- GERNSBACHER: the pronoun realizes the center -> enhance the resolved entity ----
                if gern and pick in ent:
                    ent[pick]["last_order"] = order
                    if m.get("sent_role_rank", 99) == 0:             # subject pronoun -> becomes the Cb
                        ent[pick]["last_subj_sent"] = cur_sent
        if not m["is_pronoun"]:
            cl = m["cluster"]
            e = ent.get(cl)
            if e is None:
                e = {"count": 0, "last_order": -1, "last_subj_sent": -10, "last_sent": None,
                     "gender": m.get("gender"), "number": m.get("number"), "animate": _animate(m, gaz),
                     "profile": set()}
                ent[cl] = e
            e["count"] += 1; e["last_order"] = order; e["last_sent"] = m["sent_idx"]
            e["profile"] |= csent(m["sent_idx"])            # cumulative per-entity individuation profile
            if e["gender"] is None and m.get("gender") is not None:
                e["gender"] = m["gender"]
            if m.get("sent_role_rank", 99) == 0:
                e["last_subj_sent"] = m["sent_idx"]
        order += 1
    return recs, diag


def _acc(recs, lo=1, hi=99):
    sub = [c for c, nc in recs if lo <= nc <= hi]
    return (sum(sub) / len(sub)) if sub else float("nan"), len(sub)


def _boot(ra, rb, n_boot=1000, seed=SEED):
    """Doc-level bootstrap on pooled acc(a)-acc(b). ra/rb = list of per-doc [(correct,ncomp),...]."""
    rng = random.Random(seed); k = len(ra)

    def pooled(lst, sel):
        cc = sum(sum(c for c, _ in lst[i]) for i in sel); nn = sum(len(lst[i]) for i in sel)
        return cc / nn if nn else 0.0
    idx = list(range(k)); base = pooled(ra, idx) - pooled(rb, idx)
    ds = []
    for _ in range(n_boot):
        sel = [rng.randrange(k) for _ in range(k)]
        ds.append(pooled(ra, sel) - pooled(rb, sel))
    ds.sort()
    return {"delta": base, "lo": ds[int(0.025 * n_boot)], "hi": ds[int(0.975 * n_boot)],
            "ci_sep": ds[int(0.025 * n_boot)] > 0 or ds[int(0.975 * n_boot)] < 0}


BASE = dict(win=2, k=4, w_prior=0.6, gernsbacher=True, use_fan=True,
            use_prior=True, shuffle_prior=False, shuffle_seed=0)


def run(n_docs=100, n_boot=1000):
    gaz = load_given_gazetteer()
    docs = _docs(n_docs)
    arms = {
        "centering-only (bonding, no resolution)": {**BASE, "use_prior": False, "use_fan": False, "gernsbacher": False},
        "+ fan interference (no Gernsbacher)": {**BASE, "use_prior": False, "use_fan": True, "gernsbacher": False},
        "EXACT BRAIN (last-sent coherence prior)": {**BASE, "gernsbacher": False},
        "EXACT BRAIN (cumulative individuation prior)": {**BASE, "gernsbacher": False, "cumulative": True},
        "  twin: shuffled cumulative prior": {**BASE, "gernsbacher": False, "cumulative": True, "shuffle_prior": True},
    }
    per = {}; dgs = {}
    for name, prm in arms.items():
        rd = [resolve_doc(p, gaz, prm) for _d, p in docs]
        per[name] = [r for r, _d in rd]
        dgs[name] = [d for _r, d in rd]
    flat = {name: [r for doc in per[name] for r in doc] for name in arms}

    print("=" * 88)
    print("EXACT BRAIN-FOUNDATIONAL STEP-5 SELECTOR  (%d docs)" % len(docs))
    print("-" * 88)
    for name in arms:
        a_all, n_all = _acc(flat[name])
        a_hard, n_h = _acc(flat[name], lo=2)
        a_easy, n_e = _acc(flat[name], lo=1, hi=1)
        print("  %-42s ALL=%.4f  HARD(>=2)=%.4f  EASY(1)=%.4f" % (name, a_all, a_hard, a_easy))
    print("-" * 88)
    brain = "EXACT BRAIN (cumulative individuation prior)"
    cent = "centering-only (bonding, no resolution)"
    twin = "  twin: shuffled cumulative prior"
    for lbl, a, b in (("brain - centering-only", brain, cent),
                      ("brain - shuffled-twin ", brain, twin)):
        d = _boot(per[a], per[b], n_boot)
        print("  %s : %+.4f CI[%+.4f,%+.4f] ci_sep=%s" % (lbl, d["delta"], d["lo"], d["hi"], d["ci_sep"]))
    # reachability + oracle of the coherence prior (is the wall the ARCHITECTURE or the REPRESENTATION?)
    D = {k: sum(dd[k] for doc in dgs[brain] for dd in [doc]) for k in ("bonded", "resolution", "reachable", "oracle_amb")}
    res = max(1, D["resolution"])
    print("  two-pass: bonded(fast) %d | resolution(slow) %d ; of resolution: gold reachable %.3f, prior-oracle %.3f"
          % (D["bonded"], D["resolution"], D["reachable"] / res, D["oracle_amb"] / res))
    print("-" * 88)
    print("  INTERFERENCE (cumulative-prior brain acc by same-gender competitor count):")
    for lo, hi in ((1, 1), (2, 2), (3, 4), (5, 99)):
        a, n = _acc(flat[brain], lo, hi)
        if n:
            print("     %d%s competitors: n=%-5d acc=%.3f" %
                  (lo, "" if lo == hi else ("-%d" % hi if hi < 99 else "+"), n, a))
    print("=" * 88)
    return {name: _acc(flat[name])[0] for name in arms}


def waterfall(n_docs=100):
    """The exact step-5 signal-loss chain, measured stage by stage."""
    gaz = load_given_gazetteer()
    docs = _docs(n_docs)
    D = {k: 0 for k in ("n_targets", "gold_in_pool", "bonded", "bonded_correct",
                        "resolution", "res_correct", "reachable", "oracle_amb")}
    for _d, p in docs:
        _r, dg = resolve_doc(p, gaz, {**BASE, "gernsbacher": False, "cumulative": True})
        for k in D:
            D[k] += dg[k]
    N = D["n_targets"]
    correct = D["bonded_correct"] + D["res_correct"]
    print("=" * 84)
    print("STEP-5 SIGNAL-LOSS WATERFALL  (%d docs, n=%d he/she targets with a candidate pool)" % (len(docs), N))
    print("-" * 84)
    print("  ORACLE (answer exists)                         1.000")
    print("  S1  gold entity IS in the tracked pool         %.3f   (steps 1-4 residual: %d/%d miss)"
          % (D["gold_in_pool"] / N, N - D["gold_in_pool"], N))
    print("  --- the pronoun then routes two ways ---")
    print("  BONDING (fast, Centering Cb)  fires on %.0f%% of targets, acc = %.3f"
          % (100 * D["bonded"] / N, D["bonded_correct"] / max(1, D["bonded"])))
    print("  RESOLUTION (slow)             fires on %.0f%% of targets, acc = %.3f"
          % (100 * D["resolution"] / N, D["res_correct"] / max(1, D["resolution"])))
    print("     S2  gold REACHABLE (in top-K by likelihood)  %.3f   <- likelihood/ranking loss"
          % (D["reachable"] / max(1, D["resolution"])))
    print("     S3  prior PICKS gold | reachable             %.3f   <- REPRESENTATION loss (content-BOW)"
          % (D["oracle_amb"] / max(1, D["reachable"])))
    print("-" * 84)
    print("  END-TO-END step-5 accuracy                     %.3f" % (correct / N))
    print("  ---- reference ceilings ----")
    print("  structural oracle (best structural cue/item)   0.695   (Tier-1 combiner headroom)")
    print("  semantic oracle (rich in-text, kehler_rohde)   0.857   (Tier-2 representation headroom)")
    print("  competent human reader (approx)                ~0.90")
    print("=" * 84)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "waterfall":
        waterfall(int(sys.argv[2]) if len(sys.argv) > 2 else 100)
    else:
        run(int(sys.argv[1]) if len(sys.argv) > 1 else 100)
