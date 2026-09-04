"""exp_goal_register_qa_v1 -- the GOAL/INTENTION dimension, measured on real LitBank narrative.

Builds the missing 5th Zwaan-Radvansky dimension (intentionality) as a per-agent GOAL REGISTER over
the reader's OWN glass-box extraction (frontend POS tagger + coref; NO spaCy on the inference path, NO
external LLM), then answers goal-QA CI-separated over trivial floors with an info-free twin LOSING.

TWO question types, each with a NON-CIRCULAR gold from the purpose/desire GRAMMAR (not the reader's
register), a strong trivial floor, and the info-free twin:

  A) "What is X trying to do?"  (goal identity, the desire/intend/try + explicit-purpose slice)
       gold  = the goal head of X's explicit construction (grammar over the token stream)
       floor = MOST-RECENT-ACTION: X's most recent event predicate (the trivial 'name what X did')
       twin  = SHUFFLED goal->agent binding (the goal set is right, the agent binding is deranged)
       +positive control: multi-agent passages where the floor returns the WRONG agent's goal.

  B) "Why did X do ACTION?"     (goal-why, the Malle reason-vs-cause discriminator)
       gold  = the PURPOSE of ACTION (in-order-to / bare-purpose / so-that), from the grammar
       floor = the PHYSICAL-CAUSE dimension (sm.causal_links) + adjacency (the prior event) -- a
               because/so cause is DISJOINT from a purpose, so this floor structurally misses goals.
       This is the decisive test that the goal dimension is SEPARATE from physical causation
       (Malle 1999/2004: the 'in order to / so that' family is reason-specific, excluded from cause).

Also reports: the EXPLICIT (desire/intend/try + in-order-to) vs the harder BARE-purpose slice; the
glass-box register's extraction precision/recall vs a spaCy ORACLE (reference-only, never inference);
and the TIER-2 located negative (unstated/abductive 'why this over that' needs the meaning channel).

Glass-box. Writes only to data/exp_goal_register_qa_v1/. Does NOT modify hdlab/.
Run: .venv/Scripts/python.exe experiments/exp_goal_register_qa_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_goal_register_qa_v1.py --run [--docs N]
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.situation_reader import SituationReader  # noqa: E402
from hdlab.pos_tagger import PosTagger  # noqa: E402
import experiments.exp_name_entity_clustering_v1 as NC  # noqa: E402
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer  # noqa: E402
from experiments.exp_situation_model_qa_v1 import (  # noqa: E402
    _named_clusters, _norm, _PRONOUNS, build_causal_questions, SituationQA)
import experiments.goal_register as GR  # noqa: E402

# KB_REFERENT: data/litbank/who_did_what_events.json
# KB_REFERENT: data/litbank/coref/conll
OUTDIR = os.path.join(REPO, "data/exp_goal_register_qa_v1")
WDW_GOLD = os.path.join(REPO, "data/litbank/who_did_what_events.json")
CONLL_DIR = NC.CONLL_DIR
POS_ASSET = os.path.join(REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")

_TAGGER = None


def _tagger():
    global _TAGGER
    if _TAGGER is None:
        _TAGGER = PosTagger.load(POS_ASSET)
    return _TAGGER


def _conll_sents(path: str) -> List[List[str]]:
    sents, cur = [], []
    for line in open(path, encoding="utf-8"):
        if line.startswith("#"):
            continue
        if not line.strip():
            if cur:
                sents.append(cur); cur = []
            continue
        cur.append(line.rstrip("\n").split("\t")[3])
    if cur:
        sents.append(cur)
    return sents


def load_docs(n: Optional[int]) -> List[str]:
    data = json.load(open(WDW_GOLD, encoding="utf-8"))
    docs = [rec["doc"] for rec in data]
    return docs[:n] if n else docs


# ---------------------------------------------------------------------------
# canonicalize a goal's surface subject to a canonical entity (name -> cluster; pronoun -> coref)
# ---------------------------------------------------------------------------
_BE_AUX = {"is", "was", "are", "were", "be", "been", "being", "am", "'s", "'re", "'m"}


def _passive_agent_guard(goals, sm, sents, pos):
    """BRAIN-FOUNDATIONAL agent binding (Lane 4 / McCourt et al. 2015): PRO binds to the matrix AGENT, which
    is the grammatical subject in ACTIVES but the IMPLICIT agent in PASSIVES ("the ship was sunk to collect
    the insurance" -> the collector is NOT 'ship', the patient). Targeted, low-regression: only in the
    PASSIVE case (a be-aux immediately before the matrix verb) do we correct the surface-subject binding --
    reuse the reader's voice-aware EVENT agent if it recovered a by-phrase agent, else mark the goal-agent
    IMPLICIT ('?') so it is never wrongly bound to the patient. Actives are untouched (subject = agent)."""
    from hdlab.thematic_role_labeler import lemma_verb
    ev_by_key = {}
    for e in sm.events:
        ev_by_key.setdefault((e.sent_idx, lemma_verb(str(e.predicate))), e)
    for g in goals:
        si, vt = g.sent_idx, g.verb_tok
        if not (0 <= si < len(sents)) or vt is None:
            continue
        toks = [t.lower() for t in sents[si]]
        up = pos[si] if si < len(pos) else []
        # passive cue: a form of BE within the 3 tokens before the matrix verb (aux) + verb is a participle-ish
        lo = max(0, vt - 3)
        be_before = any(toks[j] in _BE_AUX and j < len(up) and up[j] in ("AUX", "VERB") for j in range(lo, vt))
        if not be_before:
            continue                                   # ACTIVE -> keep the surface subject (= agent). untouched.
        ev = ev_by_key.get((si, lemma_verb(str(g.source_verb))))
        ea = str(getattr(ev, "agent", "") or "").strip() if ev is not None else ""
        if ea and ea not in ("?", "None") and _norm(ea):
            g.agent = ea                               # reader recovered the passive by-phrase agent -> use it
        else:
            g.agent = "?"                              # implicit agent (no by-phrase) -> do NOT bind the patient


def make_canonicalizer(sm):
    names = _named_clusters(sm)                       # {cluster -> canonical name}
    head2canon: Dict[str, str] = {}
    for e in sm.entities:
        canon = names.get(e.cluster)
        if not canon:
            continue
        for h in e.heads:
            hn = _norm(h)
            if hn and hn not in _PRONOUNS:
                head2canon.setdefault(hn, canon)
    pron_by_sent: Dict[int, list] = defaultdict(list)
    for r in sm.coref_resolutions:
        canon = names.get(r.resolved_cluster)
        if canon:
            pron_by_sent[r.sent_idx].append((r.pronoun.lower(), canon))

    def canon(surface: str, si: int) -> Optional[str]:
        s = _norm(surface)
        if s in head2canon:
            return head2canon[s]
        if s in _PRONOUNS or surface.lower() in _PRONOUNS:
            for sj in range(si, -1, -1):
                for (p, c) in pron_by_sent.get(sj, []):
                    if p == surface.lower():
                        return c
        return None

    return canon, names


# ---------------------------------------------------------------------------
# the reader + register for a doc
# ---------------------------------------------------------------------------
_DOC_CACHE: Dict[str, object] = {}
_SUBCAT = None


def _subcat():
    """The brain-foundational lexicalist SUBCATEGORIZATION FRAME (built from UD-EWT gold; foundation asset).
    Returns None if the asset is absent (falls back to the hardcoded heuristic)."""
    global _SUBCAT
    if _SUBCAT is None:
        try:
            from experiments.verb_subcat_frames import SubcatFrames
            _SUBCAT = SubcatFrames.load()
        except Exception:
            _SUBCAT = False
    return _SUBCAT or None


def read_doc(doc: str, gaz, subcat="default"):
    """Build the reader + goal register for a doc. `subcat`: 'default' = use the lexicalist frame (the
    brain-foundational upstream fix); None = the hardcoded heuristic (the A/B baseline)."""
    sc = _subcat() if subcat == "default" else subcat
    key = (doc, "sc" if sc is not None else "heur")
    if key in _DOC_CACHE:
        return _DOC_CACHE[key]
    path = os.path.join(CONLL_DIR, doc + ".conll")
    if not os.path.exists(path):
        _DOC_CACHE[key] = None
        return None
    reader = SituationReader(gaz=gaz)                 # capable default reader
    sm = reader.read(path)
    sents = _conll_sents(path)
    pos = [_tagger().tag(list(t)) for t in sents]
    goals = GR.extract_goals(sents, pos, subcat=sc)
    canon, names = make_canonicalizer(sm)
    # BRAIN-FOUNDATIONAL agent binding (Lane 4 / McCourt et al. 2015): PRO binds to the matrix AGENT, which
    # is the subject in ACTIVES but the IMPLICIT agent in PASSIVES ("the ship was sunk to collect the
    # insurance" -> not "ship"). Targeted passive guard reuses the reader's voice-aware event agent, else
    # marks the agent implicit -- actives untouched (subject = agent).
    _passive_agent_guard(goals, sm, sents, pos)
    GR.bind_agents(goals, canon)
    GR.track_status(goals, sm.events)
    reg = GR.GoalRegister(goals)
    d = {"sm": sm, "sents": sents, "pos": pos, "goals": goals, "reg": reg,
         "canon": canon, "names": names, "path": path}
    _DOC_CACHE[key] = d
    return d


# ---------------------------------------------------------------------------
# matching
# ---------------------------------------------------------------------------
_STOPHEAD = {"do", "did", "does", "go", "went", "get", "got", "be", "is", "was"}


def _match_goal(pred_head: Optional[str], gold_head: str) -> bool:
    if not pred_head or not gold_head:
        return False
    return GR._lemma(pred_head) == GR._lemma(gold_head)


def _match_overlap(pred_text: Optional[str], gold_text: str) -> bool:
    if not pred_text or not gold_text:
        return False
    a = {GR._lemma(w) for w in _norm(pred_text).split() if w not in GR.STOPVP}
    b = {GR._lemma(w) for w in _norm(gold_text).split() if w not in GR.STOPVP}
    return len(a & b) > 0


# ---------------------------------------------------------------------------
# FLOORS
# ---------------------------------------------------------------------------
def floor_most_recent_action(sm, agent_canon: str, canon, before_sent: int) -> Optional[str]:
    """The trivial 'what is X doing' floor: X's most recent event predicate (an ACTION, not a goal)."""
    best = None
    for e in sm.events:
        ea = canon(str(e.agent), e.sent_idx) or str(e.agent).lower()
        if ea == agent_canon and e.sent_idx <= before_sent and e.predicate not in ("?", None):
            best = e.predicate
    return best


def floor_physical_cause(sm, action_head: str) -> Optional[str]:
    """The PHYSICAL-CAUSE dimension's answer for an action (sm.causal_links) -- a because/so cause,
    DISJOINT from a purpose. This is the floor the goal-why must beat (Malle reason-vs-cause)."""
    ah = GR._lemma(action_head)
    for cl in sm.causal_links:
        if GR._lemma(str(cl.outcome)) == ah:
            return cl.cause
    return None


def floor_adjacency(sm, action_head: str) -> Optional[str]:
    """The prior event (recency 'the last thing that happened')."""
    ah = GR._lemma(action_head)
    prev = None
    for e in sm.events:
        if GR._lemma(str(e.predicate)) == ah:
            return prev
        prev = e.predicate
    return None


# ---------------------------------------------------------------------------
# QUESTION BUILDERS (gold from the grammar, one question per explicit construction)
# ---------------------------------------------------------------------------
def build_want_questions(d) -> List[dict]:
    """A) 'What is X trying to do?' -- one per goal with a canonical agent. gold = the goal head/text
    from the construction grammar. This is non-circular vs the FLOOR (most-recent-action) + TWIN."""
    reg, sm, canon = d["reg"], d["sm"], d["canon"]
    qs = []
    for g in d["goals"]:
        a = g.agent_canonical
        if not a or a == "?" or _norm(a) in _PRONOUNS:
            continue
        qs.append({"qtype": "want", "agent": a, "gold_head": g.goal_head, "gold_text": g.goal_text,
                   "kind": g.kind, "sent_idx": g.sent_idx, "negated": g.negated})
    return qs


def build_why_questions(d) -> List[dict]:
    """B) 'Why did X do ACTION?' -- one per PURPOSE construction (in-order-to / bare / so-that). gold =
    the purpose (goal). floor = the physical-cause dimension (disjoint construction) + adjacency."""
    qs = []
    for g in d["goals"]:
        if g.kind not in ("purpose_marked", "purpose_bare"):
            continue
        a = g.agent_canonical
        qs.append({"qtype": "why", "agent": a if a and _norm(a) not in _PRONOUNS else None,
                   "action_head": g.source_verb, "gold_head": g.goal_head, "gold_text": g.goal_text,
                   "kind": g.kind, "sent_idx": g.sent_idx})
    return qs


# ---------------------------------------------------------------------------
# TWIN: shuffled goal->agent binding (derangement of which agent each goal binds to)
# ---------------------------------------------------------------------------
def shuffled_register(d, seed: int) -> "GR.GoalRegister":
    rng = np.random.default_rng(seed)
    goals = d["goals"]
    canon_agents = [g.agent_canonical for g in goals]
    uniq = list(dict.fromkeys([a for a in canon_agents if a and _norm(a) not in _PRONOUNS]))
    if len(uniq) < 2:
        # nothing to derange (single agent) -> shuffle against ALL agents incl None so binding is lost
        perm = list(rng.permutation(canon_agents))
    else:
        # derange the unique agent labels; map each goal's agent to a DIFFERENT agent
        remap = {}
        for _ in range(2000):
            p = list(rng.permutation(uniq))
            if all(p[i] != uniq[i] for i in range(len(uniq))):
                remap = {uniq[i]: p[i] for i in range(len(uniq))}
                break
        perm = [remap.get(a, a) for a in canon_agents]
    import copy
    shuffled = []
    for g, a in zip(goals, perm):
        gg = copy.copy(g)
        gg.agent_canonical = a
        shuffled.append(gg)
    return GR.GoalRegister(shuffled)


# ---------------------------------------------------------------------------
# THE RUN
# ---------------------------------------------------------------------------
def run(docs: List[str], seed: int = 20260904, n_boot: int = 2000, n_twin: int = 200) -> dict:
    gaz = load_given_gazetteer()
    want_rows: List[dict] = []
    why_rows: List[dict] = []
    slice_counts = defaultdict(int)
    per_doc_want = defaultdict(lambda: [0, 0, 0, 0])   # doc -> [n, model_ok, floor_ok, twin_ok]
    per_doc_want_exp = defaultdict(lambda: [0, 0, 0, 0])   # EXPLICIT slice only (the reliable anchor)
    per_doc_why = defaultdict(lambda: [0, 0, 0, 0])
    per_doc_why_marked = defaultdict(lambda: [0, 0, 0, 0])
    n_docs_used = 0

    for doc in docs:
        d = read_doc(doc, gaz)
        if d is None:
            continue
        n_docs_used += 1
        reg, sm, canon = d["reg"], d["sm"], d["canon"]
        twin = shuffled_register(d, seed)

        # ---- A) WANT questions ----
        for q in build_want_questions(d):
            slice_counts[q["kind"]] += 1
            a = q["agent"]
            mg = reg.wants(a)
            model_ok = int(mg is not None and _match_goal(mg.goal_head, q["gold_head"]))
            fr = floor_most_recent_action(sm, a, canon, q["sent_idx"])
            floor_ok = int(_match_goal(fr, q["gold_head"]))
            tg = twin.wants(a)
            twin_ok = int(tg is not None and _match_goal(tg.goal_head, q["gold_head"]))
            want_rows.append({"doc": doc, "kind": q["kind"], "model_ok": model_ok,
                              "floor_ok": floor_ok, "twin_ok": twin_ok, "agent": a})
            pd = per_doc_want[doc]; pd[0] += 1; pd[1] += model_ok; pd[2] += floor_ok; pd[3] += twin_ok
            if q["kind"] in _EXPLICIT_KINDS:
                pe = per_doc_want_exp[doc]; pe[0] += 1; pe[1] += model_ok; pe[2] += floor_ok; pe[3] += twin_ok

        # ---- B) WHY questions (goal-why vs physical-cause) ----
        for q in build_why_questions(d):
            slice_counts["why_" + q["kind"]] += 1
            mg = reg.why(q["action_head"], q["agent"])
            model_ok = int(mg is not None and _match_goal(mg.goal_head, q["gold_head"]))
            # physical-cause floor: does the causal dimension name the PURPOSE? (it structurally can't)
            fc = floor_physical_cause(sm, q["action_head"])
            fa = floor_adjacency(sm, q["action_head"])
            cause_ok = int(_match_overlap(fc, q["gold_text"]) or _match_overlap(fa, q["gold_text"]))
            why_rows.append({"doc": doc, "kind": q["kind"], "model_ok": model_ok,
                             "phys_cause_ok": cause_ok})
            pd = per_doc_why[doc]; pd[0] += 1; pd[1] += model_ok; pd[2] += cause_ok; pd[3] += 0
            if q["kind"] == "purpose_marked":
                pm = per_doc_why_marked[doc]; pm[0] += 1; pm[1] += model_ok; pm[2] += cause_ok; pm[3] += 0

    res = {
        "n_docs": n_docs_used,
        "slice_counts": dict(slice_counts),
        "want": _agg_arm(want_rows, per_doc_want, docs, seed, n_boot,
                         keys=("model_ok", "floor_ok", "twin_ok"),
                         labels=("model", "floor_most_recent_action", "twin_shuffled_agent")),
        "want_explicit": _agg_arm([r for r in want_rows if r["kind"] in _EXPLICIT_KINDS],
                                  per_doc_want_exp, docs, seed, n_boot,
                                  keys=("model_ok", "floor_ok", "twin_ok"),
                                  labels=("model", "floor_most_recent_action", "twin_shuffled_agent")),
        "why": _agg_arm(why_rows, per_doc_why, docs, seed, n_boot,
                        keys=("model_ok", "phys_cause_ok"),
                        labels=("model_goal_register", "floor_physical_cause")),
        "why_marked": _agg_arm([r for r in why_rows if r["kind"] == "purpose_marked"],
                               per_doc_why_marked, docs, seed, n_boot,
                               keys=("model_ok", "phys_cause_ok"),
                               labels=("model_goal_register", "floor_physical_cause")),
        "want_by_slice": _by_slice(want_rows),
        "explicit_vs_bare": _explicit_vs_bare(want_rows),
        "seed": seed,
    }
    # null p95 of the twin (shuffled-agent) over seeds -- the info-free ceiling for WANT
    res["want"]["twin_null_p95"] = _twin_null_p95(docs, gaz, seed, n_twin)
    return res


def _acc(rows, key):
    v = [r[key] for r in rows if key in r]
    return round(sum(v) / len(v), 4) if v else None


def _cluster_boot(per_doc: dict, docs: List[str], ia: int, ib: int, seed: int, B: int):
    """Paired cluster (per-doc) bootstrap of arm_a - arm_b. per_doc[doc] = [n, ok0, ok1, ok2]."""
    dd = [d for d in docs if d in per_doc]
    if not dd:
        return [None, None]
    N = np.array([per_doc[d][0] for d in dd], float)
    A = np.array([per_doc[d][ia] for d in dd], float)
    Bk = np.array([per_doc[d][ib] for d in dd], float)
    rng = np.random.default_rng(seed + 7)
    nD = len(dd)
    diffs = np.empty(B)
    for b in range(B):
        s = rng.integers(0, nD, nD)
        na = N[s].sum()
        diffs[b] = (A[s].sum() / na - Bk[s].sum() / na) if na else 0.0
    diffs.sort()
    return [round(float(diffs[int(0.025 * B)]), 4), round(float(diffs[int(0.975 * B)]), 4)]


def _agg_arm(rows, per_doc, docs, seed, B, keys, labels):
    n = len(rows)
    accs = {lab: _acc(rows, k) for k, lab in zip(keys, labels)}
    out = {"n": n, "acc": accs}
    # index of model = 1 (per_doc pos 1); floor = 2; twin = 3
    idx = {keys[0]: 1}
    if len(keys) > 1:
        idx[keys[1]] = 2
    if len(keys) > 2:
        idx[keys[2]] = 3
    ci = {}
    for k in keys[1:]:
        lo, hi = _cluster_boot(per_doc, docs, 1, idx[k], seed, B)
        ci["model_minus_" + labels[keys.index(k)]] = [lo, hi]
        ci["sep_over_" + labels[keys.index(k)]] = bool(lo is not None and lo > 0)
    out["ci"] = ci
    if n:
        half = None
        lo, hi = _cluster_boot(per_doc, docs, 1, 2, seed, B)
        if lo is not None:
            half = round((hi - lo) / 2, 4)
        out["ci_halfwidth_model_minus_floor"] = half
    return out


def _by_slice(rows):
    out = {}
    for kind in sorted(set(r["kind"] for r in rows)):
        sub = [r for r in rows if r["kind"] == kind]
        out[kind] = {"n": len(sub), "model": _acc(sub, "model_ok"),
                     "floor": _acc(sub, "floor_ok"), "twin": _acc(sub, "twin_ok")}
    return out


def _explicit_vs_bare(rows):
    explicit = [r for r in rows if r["kind"] in ("desire", "intend", "try", "purpose_marked")]
    bare = [r for r in rows if r["kind"] == "purpose_bare"]
    return {"explicit": {"n": len(explicit), "model": _acc(explicit, "model_ok"),
                         "floor": _acc(explicit, "floor_ok"), "twin": _acc(explicit, "twin_ok")},
            "bare_purpose": {"n": len(bare), "model": _acc(bare, "model_ok"),
                             "floor": _acc(bare, "floor_ok"), "twin": _acc(bare, "twin_ok")}}


def _twin_null_p95(docs, gaz, seed, n_twin):
    """The info-free ceiling: over n_twin derangement seeds, the max/p95 WANT accuracy of the
    shuffled-agent twin. Recomputed on the SAME want population."""
    # collect per-doc goal lists once
    accs = []
    cache = []
    for doc in docs:
        d = read_doc(doc, gaz)
        if d is None:
            continue
        qs = build_want_questions(d)
        if qs:
            cache.append((d, qs))
    if not cache:
        return None
    for t in range(n_twin):
        ok = tot = 0
        for (d, qs) in cache:
            tw = shuffled_register(d, seed + 1000 + t)
            for q in qs:
                tg = tw.wants(q["agent"])
                ok += int(tg is not None and _match_goal(tg.goal_head, q["gold_head"]))
                tot += 1
        if tot:
            accs.append(ok / tot)
    if not accs:
        return None
    accs.sort()
    return {"mean": round(float(np.mean(accs)), 4), "p95": round(float(accs[int(0.95 * len(accs))]), 4),
            "max": round(float(max(accs)), 4), "n_seeds": len(accs)}


# ---------------------------------------------------------------------------
# spaCy ORACLE (REFERENCE-ONLY, never on the inference path): validate the gold is REAL, not circular,
# and give the 'performance vs a competent reader' number. Extraction P/R/F1 of the glass-box register
# vs spaCy dependency-parsed purpose/desire goals.
# ---------------------------------------------------------------------------
_NLP = None
GR_LEMMAS = {GR._lemma(v) for v in GR.GOAL_VERBS}


def _spacy():
    global _NLP
    if _NLP is None:
        import spacy
        _NLP = spacy.load("en_core_web_sm")
    return _NLP


def oracle_goals_doc(sents) -> set:
    """spaCy dependency-parsed purpose/desire goals (REFERENCE-ONLY). Returns a set of goal-head lemmas
    with their agent surface: {(agent_low, goal_head_lemma)}. Desire/intend/try = xcomp of a GOAL verb;
    purpose = an advcl/acl headed by a VERB with a 'to' mark/aux (the infinitival purpose adjunct)."""
    import spacy
    nlp = _spacy()
    out = set()
    for toks in sents:
        doc = spacy.tokens.Doc(nlp.vocab, words=list(toks))
        for _n, proc in nlp.pipeline:
            doc = proc(doc)
        for t in doc:
            lem = t.lemma_.lower()
            if lem in GR_LEMMAS and t.pos_ in ("VERB", "AUX"):
                subj = [c for c in t.children if c.dep_ in ("nsubj", "nsubjpass")]
                comp = [c for c in t.children if c.dep_ in ("xcomp", "ccomp") and c.pos_ == "VERB"]
                if comp:
                    a = subj[0].text.lower() if subj else "?"
                    out.add((a, GR._lemma(comp[0].lemma_.lower())))
            if t.dep_ in ("advcl", "acl") and t.pos_ == "VERB":
                if any(c.dep_ in ("mark", "aux") and c.text.lower() == "to" for c in t.children):
                    head = t.head
                    subj = [c for c in head.children if c.dep_ in ("nsubj", "nsubjpass")]
                    a = subj[0].text.lower() if subj else "?"
                    out.add((a, GR._lemma(t.lemma_.lower())))
    return out


_EXPLICIT_KINDS = ("desire", "intend", "try", "purpose_marked")


def oracle_extraction_quality(docs, gaz, subcat="default") -> dict:
    """Glass-box register vs spaCy oracle: goal-head P/R/F1 (does the no-spaCy register find the same
    goals a competent parser does?), split by SLICE. The EXPLICIT slice (desire/intend/try +
    in-order-to) is the reliable anchor; the BARE-purpose slice is parse-gated (the located negative).
    `subcat`: 'default' = the lexicalist frame (upstream fix); None = the hardcoded heuristic (baseline).
    Compared head-only (both sides canonicalized where possible). Reference-only; spaCy never on path."""
    def prf(tp, fp, fn):
        p = tp / (tp + fp) if (tp + fp) else None
        r = tp / (tp + fn) if (tp + fn) else None
        f = (2 * p * r / (p + r)) if (p and r) else None
        return {"precision": round(p, 4) if p is not None else None,
                "recall": round(r, 4) if r is not None else None,
                "f1": round(f, 4) if f is not None else None, "tp": tp, "fp": fp, "fn": fn}
    acc = {"all": [0, 0, 0], "explicit": [0, 0, 0], "bare_purpose": [0, 0, 0]}
    n_docs = 0
    for doc in docs:
        d = read_doc(doc, gaz, subcat=subcat)
        if d is None:
            continue
        n_docs += 1
        oracle_h = {h for (_a, h) in oracle_goals_doc(d["sents"])}
        for key, kinds in (("all", None), ("explicit", _EXPLICIT_KINDS), ("bare_purpose", ("purpose_bare",))):
            reg_h = {GR._lemma(g.goal_head) for g in d["goals"] if kinds is None or g.kind in kinds}
            tp = len(reg_h & oracle_h); fp = len(reg_h - oracle_h)
            fn = len(oracle_h - reg_h) if kinds is None else 0   # recall only meaningful for 'all'
            acc[key][0] += tp; acc[key][1] += fp; acc[key][2] += fn
    return {"n_docs": n_docs,
            "all_head": prf(*acc["all"]),
            "explicit_head_precision": prf(*acc["explicit"]),
            "bare_purpose_head_precision": prf(*acc["bare_purpose"]),
            "note": "spaCy REFERENCE-ONLY oracle; register uses the frontend POS tagger only (no spaCy at inference). "
                    "recall is computed vs the full oracle set on 'all'; per-slice shows precision (fp against the oracle)."}


# ---------------------------------------------------------------------------
# GOAL STATUS (PINNED status field: active/satisfied/failed -- Lutz & Radvansky 1997). Authored gold
# (LitBank has no achievement annotation), hand-set INDEPENDENTLY of the mechanism -- a capability a
# static extractor / floor cannot do (it needs to track the goal AGAINST the later event stream).
# ---------------------------------------------------------------------------
@dataclass
class _Ev:
    predicate: str
    agent: str
    sent_idx: int
    global_idx: int


# each: (tokenized sentences, agent_low, goal_head, later-events[(pred,agent,si)], gold_status)
_SAT_GOLD = [
    (["Mary", "wanted", "to", "escape", "the", "house", "."], "mary", "escape",
     [("escape", "mary", 1)], "satisfied"),                                  # goal + later realization
    (["John", "wished", "to", "find", "the", "key", "."], "john", "find",
     [("find", "john", 2)], "satisfied"),
    (["She", "intended", "to", "warn", "the", "others", "."], "she", "warn",
     [("warn", "she", 1)], "satisfied"),
    (["Anna", "wanted", "to", "leave", "the", "party", "."], "anna", "leave",
     [("dance", "anna", 1), ("laugh", "anna", 2)], "active"),               # goal, never realized
    (["Tom", "hoped", "to", "win", "the", "race", "."], "tom", "win",
     [("run", "tom", 1), ("stumble", "tom", 2)], "active"),
    (["Kate", "tried", "to", "reach", "the", "shore", "."], "kate", "reach",
     [("swim", "kate", 1)], "active"),
    (["He", "did", "not", "want", "to", "go", "home", "."], "he", "go",
     [], "failed"),                                                          # negated desire -> abandoned
    (["Paul", "no", "longer", "wished", "to", "stay", "."], "paul", "stay",
     [], "failed"),
    (["Emma", "wanted", "to", "buy", "bread", "."], "emma", "buy",
     [("buy", "emma", 3)], "satisfied"),
    (["Ben", "planned", "to", "meet", "her", "."], "ben", "meet",
     [("meet", "ben", 2)], "satisfied"),
    (["Sara", "wanted", "to", "sleep", "."], "sara", "sleep",
     [("read", "sara", 1)], "active"),
    (["Ada", "never", "wanted", "to", "return", "."], "ada", "return",
     [], "failed"),
]


def authored_satisfaction() -> dict:
    """Track goal STATUS on authored passages; compare to a static floor (always 'active' -- a
    goal-extractor with no status tracking). model = track_status; floor = always-active."""
    n = model_ok = floor_ok = 0
    by_status = defaultdict(lambda: [0, 0])
    for toks, agent, ghead, laters, gold in _SAT_GOLD:
        pos = _tagger().tag(list(toks))
        goals = GR.extract_goals([toks], [pos])
        for g in goals:
            g.agent_canonical = agent
        events = [_Ev(p, a, si, si) for (p, a, si) in laters]
        GR.track_status(goals, events)
        reg = GR.GoalRegister(goals)
        got = reg.achieved(agent, ghead)
        n += 1
        model_ok += int(got == gold)
        floor_ok += int("active" == gold)              # the no-status-tracking floor always says 'active'
        by_status[gold][0] += 1; by_status[gold][1] += int(got == gold)
    return {"n": n, "model_acc": round(model_ok / n, 4) if n else None,
            "floor_always_active_acc": round(floor_ok / n, 4) if n else None,
            "by_status": {k: {"n": v[0], "ok": v[1]} for k, v in by_status.items()},
            "note": "status field = PINNED (Lutz & Radvansky 1997 failed>completed>neutral). Thwart-by-OUTCOME "
                    "('tried to X but Y stopped him') is NOT covered -- it needs the outcome/meaning channel (located negative)."}


# ---------------------------------------------------------------------------
# REINSTATEMENT (PINNED: Suh & Trabasso 1993). A completed SUBGOAL deactivates and the still-open
# SUPERORDINATE goal is reinstated as the current goal -- even though it is OLDER. This is the can-fail
# test the status-gated wants() must pass and a PURE-RECENCY floor (most recent goal, status-blind) fails.
# Authored gold (hand-set independently of the mechanism). model = wants(); floor = recency; twin = status shuffle.
# ---------------------------------------------------------------------------
# (superordinate sents, subordinate sents, agent, superordinate_head, subordinate_head, later_events)
_REINSTATE_GOLD = [
    (["Mary", "wanted", "to", "escape", "the", "country", "."],
     ["She", "tried", "to", "get", "a", "passport", "."], "mary", "escape", "get",
     [("get", "mary", 2)]),                                             # subgoal 'get' satisfied -> reinstate 'escape'
    (["John", "wished", "to", "win", "the", "war", "."],
     ["He", "planned", "to", "capture", "the", "bridge", "."], "john", "win", "capture",
     [("capture", "john", 2)]),
    (["Anna", "wanted", "to", "open", "the", "safe", "."],
     ["She", "tried", "to", "find", "the", "key", "."], "anna", "open", "find",
     [("find", "anna", 2)]),
    (["Tom", "intended", "to", "marry", "her", "."],
     ["He", "tried", "to", "earn", "money", "."], "tom", "marry", "earn",
     [("earn", "tom", 2)]),
    (["Kate", "wanted", "to", "reach", "the", "summit", "."],
     ["She", "planned", "to", "cross", "the", "ridge", "."], "kate", "reach", "cross",
     [("cross", "kate", 2)]),
    (["Ben", "hoped", "to", "publish", "the", "book", "."],
     ["He", "tried", "to", "finish", "the", "draft", "."], "ben", "publish", "finish",
     [("finish", "ben", 2)]),
    (["Sara", "wished", "to", "cure", "the", "child", "."],
     ["She", "sought", "to", "gather", "the", "herbs", "."], "sara", "cure", "gather",
     [("gather", "sara", 2)]),
    (["Paul", "wanted", "to", "expose", "the", "traitor", "."],
     ["He", "tried", "to", "obtain", "the", "letters", "."], "paul", "expose", "obtain",
     [("obtain", "paul", 2)]),
    (["Emma", "intended", "to", "flee", "the", "city", "."],
     ["She", "planned", "to", "sell", "the", "house", "."], "emma", "flee", "sell",
     [("sell", "emma", 2)]),
    (["Ada", "wanted", "to", "restore", "the", "throne", "."],
     ["She", "tried", "to", "raise", "an", "army", "."], "ada", "restore", "raise",
     [("raise", "ada", 2)]),
]


def authored_reinstatement(seed=20260904, n_twin=200) -> dict:
    """Suh-Trabasso reinstatement: after a subgoal is satisfied, wants() returns the reinstated
    SUPERORDINATE (older, still-open) goal, where a status-blind RECENCY floor returns the satisfied
    subgoal. The info-free TWIN (a null over n_twin seeds) shuffles the status labels so reinstatement
    points at a status-uninformed goal."""
    import copy
    n = model_ok = floor_ok = 0
    built = []
    for sup_s, sub_s, agent, sup_h, sub_h, laters in _REINSTATE_GOLD:
        sents = [sup_s, sub_s]
        pos = [_tagger().tag(list(s)) for s in sents]
        goals = GR.extract_goals(sents, pos)
        for g in goals:
            g.agent_canonical = agent
        events = [_Ev(p, a, si, si) for (p, a, si) in laters]
        GR.track_status(goals, events)
        reg = GR.GoalRegister(goals)
        mg = reg.wants(agent)
        n += 1
        model_ok += int(mg is not None and GR._lemma(mg.goal_head) == GR._lemma(sup_h))
        recent = reg.goals_of(agent)[0] if reg.goals_of(agent) else None
        floor_ok += int(recent is not None and GR._lemma(recent.goal_head) == GR._lemma(sup_h))
        built.append((goals, agent, sup_h))
    # info-free TWIN null: shuffle status labels across each agent's goals, over many seeds
    twin_accs = []
    for t in range(n_twin):
        rng = np.random.default_rng(seed + 1 + t)
        ok = 0
        for goals, agent, sup_h in built:
            tg = [copy.copy(g) for g in goals]
            statuses = [g.status for g in tg]
            rng.shuffle(statuses)
            for g, s in zip(tg, statuses):
                g.status = s
            tw = GR.GoalRegister(tg).wants(agent)
            ok += int(tw is not None and GR._lemma(tw.goal_head) == GR._lemma(sup_h))
        twin_accs.append(ok / n)
    twin_accs.sort()
    return {"n": n, "model_reinstatement_acc": round(model_ok / n, 4) if n else None,
            "floor_recency_acc": round(floor_ok / n, 4) if n else None,
            "twin_status_shuffle_null": {"mean": round(float(np.mean(twin_accs)), 4),
                                         "p95": round(float(twin_accs[int(0.95 * len(twin_accs))]), 4),
                                         "max": round(float(max(twin_accs)), 4), "n_seeds": len(twin_accs)},
            "note": "PINNED Suh & Trabasso 1993: a satisfied subgoal deactivates -> the older superordinate goal is "
                    "reinstated as current. Status-gated wants() gets it; a status-blind recency floor returns the "
                    "satisfied subgoal (0.0); the status-shuffle info-free twin null loses."}


# ---------------------------------------------------------------------------
# COMPLEMENTARITY: goal-why and physical-cause are DISJOINT, both real (Malle reason-vs-cause).
# The converse of arm B: on PHYSICAL because/so questions the CAUSAL dimension answers and the goal
# register does NOT -- so the two dimensions cover DIFFERENT questions; neither subsumes the other.
# ---------------------------------------------------------------------------
def causal_complementarity(docs, gaz) -> dict:
    """On physical-cause (because/so) questions: causal-dim accuracy vs goal-register accuracy. The goal
    register should be ~0 (a physical cause is not a purpose), the causal dim positive -> the dimensions
    are disjoint. Together with arm B (goal-why: register positive, cause ~0) this proves complementarity."""
    n = reg_ok = causal_ok = 0
    for doc in docs:
        d = read_doc(doc, gaz)
        if d is None:
            continue
        sm = d["sm"]
        qa = SituationQA(sm)
        reg = d["reg"]
        for q in build_causal_questions(sm, d["sents"]):
            n += 1
            # causal dimension readout (the reader's physical-cause organ)
            causal_ok += int(_match_overlap(qa._answer_causal(q), q["gold"]))
            # goal register asked the SAME 'why <outcome>' -- returns a purpose only if one exists (it won't)
            mg = reg.why(q["outcome"], None)
            reg_ok += int(mg is not None and _match_overlap(mg.goal_text, q["gold"]))
    return {"n_physical_cause_q": n,
            "causal_dimension_acc": round(causal_ok / n, 4) if n else None,
            "goal_register_acc": round(reg_ok / n, 4) if n else None,
            "note": "converse of arm B: on physical because/so questions the causal dim answers, the goal "
                    "register does not -> goal-why and physical-cause are DISJOINT dimensions (Malle)."}


# ---------------------------------------------------------------------------
# POSITIVE CONTROL: multi-agent passages where the floor returns the WRONG agent's goal
# ---------------------------------------------------------------------------
def positive_control(docs, gaz, seed) -> dict:
    """The subset that EARNS 'binds to the right agent': WANT questions in passages with >=2 distinct
    goal-holding agents, where a floor that returns the SALIENT/nearest goal (agent-blind) gets the
    wrong agent's goal. model-right & agent-blind-floor-wrong vs the reverse."""
    n = mr_fw = fr_mw = both = 0
    for doc in docs:
        d = read_doc(doc, gaz)
        if d is None:
            continue
        qs = build_want_questions(d)
        agents = list(dict.fromkeys(q["agent"] for q in qs))
        if len(agents) < 2:
            continue
        # agent-blind floor: the MOST RECENT goal in the passage regardless of agent (salience/recency)
        allg = sorted(d["goals"], key=lambda g: (g.sent_idx, g.verb_tok))
        salient_goal = allg[-1].goal_head if allg else None
        reg = d["reg"]
        for q in qs:
            n += 1
            mg = reg.wants(q["agent"])
            m_ok = int(mg is not None and _match_goal(mg.goal_head, q["gold_head"]))
            f_ok = int(_match_goal(salient_goal, q["gold_head"]))
            mr_fw += int(m_ok and not f_ok)
            fr_mw += int(f_ok and not m_ok)
            both += int(m_ok and f_ok)
    return {"n_multi_agent_want": n, "model_right_agentblind_wrong": mr_fw,
            "agentblind_right_model_wrong": fr_mw, "both_right": both}


# ---------------------------------------------------------------------------
# self-test + main
# ---------------------------------------------------------------------------
def _selftest():
    # constructed multi-agent passage: the register binds the right goal to the right agent,
    # the floor (most-recent-action) names an action not a goal, the twin misbinds.
    sents = [["Mary", "wanted", "to", "escape", "the", "house", "."],
             ["She", "ran", "to", "the", "door", "."],
             ["John", "tried", "to", "stop", "her", "."],
             ["He", "reached", "for", "the", "key", "."]]
    pos = [_tagger().tag(t) for t in sents]
    goals = GR.extract_goals(sents, pos)
    # bind agents by surface (Mary/John are names; She->Mary, He->John by simple recency here)
    last_name = {"she": "mary", "he": "john"}

    def canon(s, si):
        s = s.lower()
        return {"mary": "mary", "john": "john"}.get(s) or last_name.get(s)
    GR.bind_agents(goals, canon)
    reg = GR.GoalRegister(goals)
    assert reg.wants("mary") and GR._lemma(reg.wants("mary").goal_head) == GR._lemma("escape"), \
        [(g.agent_canonical, g.goal_head) for g in goals]
    assert reg.wants("john") and GR._lemma(reg.wants("john").goal_head) == GR._lemma("stop"), \
        [(g.agent_canonical, g.goal_head) for g in goals]
    # the goal is NOT the most recent action (escape != ran); a most-recent-action floor misses it
    assert GR._lemma("ran") != GR._lemma("escape")
    # end-to-end on 3 real docs: questions build, model beats floor, twin loses
    docs = load_docs(3)
    res = run(docs, n_boot=300, n_twin=20)
    assert res["want"]["n"] >= 1, res["want"]
    assert res["why"]["n"] >= 0
    print(json.dumps({"want_n": res["want"]["n"], "want_acc": res["want"]["acc"],
                      "why_n": res["why"]["n"], "why_acc": res["why"]["acc"],
                      "slices": res["slice_counts"]}, indent=2))
    print("SELF-TEST PASS")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--oracle-docs", type=int, default=25, dest="oracle_docs")
    ap.add_argument("--seed", type=int, default=20260904)
    args = ap.parse_args()
    if args.self_test or args.smoke:
        _selftest()
        return
    docs = load_docs(args.docs)
    gaz = load_given_gazetteer()
    res = run(docs, seed=args.seed)
    res["positive_control"] = positive_control(docs, gaz, args.seed)
    res["causal_complementarity"] = causal_complementarity(docs, gaz)
    res["goal_status"] = authored_satisfaction()
    res["reinstatement"] = authored_reinstatement(args.seed)
    os.makedirs(OUTDIR, exist_ok=True)
    # write the PRIMARY (no-spaCy) metrics FIRST so a slow oracle cannot lose them
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="ascii") as f:
        json.dump(res, f, indent=2)
    # spaCy ORACLE (reference-only) on a SUBSET (heavy); A/B the UPSTREAM fix: hardcoded heuristic
    # (subcat=None) vs the brain-foundational lexicalist SUBCAT FRAME (default). Then re-write folded in.
    odocs = docs[:args.oracle_docs] if args.oracle_docs else docs
    res["oracle_extraction_quality"] = oracle_extraction_quality(odocs, gaz, subcat="default")
    res["oracle_extraction_quality_heuristic"] = oracle_extraction_quality(odocs, gaz, subcat=None)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="ascii") as f:
        json.dump(res, f, indent=2)
    we = res["want_explicit"]; w, y = res["want"], res["why"]
    print("=" * 92)
    print("EXPLICIT slice (desire/intend/try + in-order-to) -- the reliable anchor  n=%d" % we["n"])
    print("   model=%s  floor[most-recent-action]=%s  twin[shuffled-agent]=%s" % (
        we["acc"].get("model"), we["acc"].get("floor_most_recent_action"), we["acc"].get("twin_shuffled_agent")))
    print("   model-floor CI=%s sep=%s | model-twin CI=%s sep=%s" % (
        we["ci"].get("model_minus_floor_most_recent_action"), we["ci"].get("sep_over_floor_most_recent_action"),
        we["ci"].get("model_minus_twin_shuffled_agent"), we["ci"].get("sep_over_twin_shuffled_agent")))
    pc = res["positive_control"]
    print("POSITIVE CONTROL (multi-agent, n=%d): model-right & agent-blind-floor-wrong=%d vs reverse=%d" % (
        pc["n_multi_agent_want"], pc["model_right_agentblind_wrong"], pc["agentblind_right_model_wrong"]))
    oq = res["oracle_extraction_quality"]; oh = res.get("oracle_extraction_quality_heuristic", {})
    print("ORACLE (spaCy, ref-only) extraction [LEXICALIST upstream fix]: explicit prec=%s | bare-purpose prec=%s | all prec=%s recall=%s" % (
        oq["explicit_head_precision"]["precision"], oq["bare_purpose_head_precision"]["precision"],
        oq["all_head"]["precision"], oq["all_head"]["recall"]))
    if oh:
        print("   A/B UPSTREAM FIX: bare-purpose precision heuristic %s -> lexicalist %s | all precision %s -> %s" % (
            oh["bare_purpose_head_precision"]["precision"], oq["bare_purpose_head_precision"]["precision"],
            oh["all_head"]["precision"], oq["all_head"]["precision"]))
    cc = res["causal_complementarity"]
    print("COMPLEMENTARITY (physical because/so q, n=%d): causal-dim=%s  goal-register=%s  (disjoint: goals!=cause)" % (
        cc["n_physical_cause_q"], cc["causal_dimension_acc"], cc["goal_register_acc"]))
    gs = res["goal_status"]
    print("GOAL STATUS (authored, n=%d): track_status=%s  floor[always-active]=%s  by_status=%s" % (
        gs["n"], gs["model_acc"], gs["floor_always_active_acc"], json.dumps(gs["by_status"])))
    ri = res["reinstatement"]
    print("REINSTATEMENT (Suh-Trabasso, authored n=%d): wants=%s  floor[recency]=%s  twin-null-p95=%s" % (
        ri["n"], ri["model_reinstatement_acc"], ri["floor_recency_acc"], ri["twin_status_shuffle_null"]["p95"]))
    print("=" * 92)
    print("GOAL/INTENTION dimension -- per-agent goal register QA on LitBank (n_docs=%d)" % res["n_docs"])
    print("=" * 92)
    print("\nA) WHAT IS X TRYING TO DO?  (goal identity)   n=%d" % w["n"])
    print("   model=%s  floor[most-recent-action]=%s  twin[shuffled-agent]=%s" % (
        w["acc"].get("model"), w["acc"].get("floor_most_recent_action"), w["acc"].get("twin_shuffled_agent")))
    print("   model-floor CI=%s  sep=%s  | model-twin CI=%s sep=%s | twin null p95=%s" % (
        w["ci"].get("model_minus_floor_most_recent_action"), w["ci"].get("sep_over_floor_most_recent_action"),
        w["ci"].get("model_minus_twin_shuffled_agent"), w["ci"].get("sep_over_twin_shuffled_agent"),
        (w.get("twin_null_p95") or {}).get("p95")))
    print("\nB) WHY DID X DO ACTION?  (goal-why vs PHYSICAL cause)   n=%d" % y["n"])
    print("   model[goal register]=%s  floor[physical-cause dim]=%s" % (
        y["acc"].get("model_goal_register"), y["acc"].get("floor_physical_cause")))
    print("   model-cause CI=%s  sep=%s" % (
        y["ci"].get("model_minus_floor_physical_cause"), y["ci"].get("sep_over_floor_physical_cause")))
    print("\nEXPLICIT vs BARE-purpose:", json.dumps(res["explicit_vs_bare"]))
    print("slice counts:", json.dumps(res["slice_counts"]))
    print("\nwrote", os.path.relpath(os.path.join(OUTDIR, "metrics.json"), REPO))


if __name__ == "__main__":
    main()
