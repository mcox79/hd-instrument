"""exp_goal_constraints_v1 -- MAKE THE AGENT, OBJECT AND TIME CONSTRAINTS BINDING IN THE GOAL REGISTER.

problem: the_goal_register_answers_why_with_another_agents_purpose_marks_a_goal_satisfied_by_verb_and_agent_
         alone_and_reads_future_goals_into_time_limited_prediction_make_agent_object_and_time_constraints_binding
         (pri 135; review findings R02/R03/R04 + appendix A11)

WHAT IS WRONG (reproduced on HEAD, in this cell's --fixtures arm):
  R02  why(action, agent) returned ANOTHER agent's purpose when the requested agent had none.  ALREADY FIXED
       at the pri 129 landing -- this cell keeps the regression fixture (and adds the missing LABEL on the
       same-agent fallback, so a consumer can tell a purpose from a fallback instead of assuming).
  R03  satisfaction compared the goal's PREDICATE and AGENT only: "buy bread" was closed by "bought a car",
       and a realization later in the goal's OWN sentence was never counted (strictly-later-sentence rule).
  R04  a t-limited prediction respected t for the passage context but read the FULL-document goal register:
       the forward projection at t=0 was conditioned on a goal stated at sentence 5.

THE BRAIN (the mechanism this cell measures; full citations in hdlab/goal_register.py's new section):
  a goal node is closed by an outcome that achieves its CONTENT -- same agent, same theme (Trabasso & van den
  Broek 1985 goal/outcome arcs; Zwaan & Radvansky 1998 intentionality index); the theme is an ENTITY (a file
  card -- Heim 1982; Kahneman & Treisman 1992), so identity is decided through the reader's OWN entity files
  first and by head lemma only as the fallback; order is (sentence, within-sentence position) because the
  reference time advances with every clause (Reichenbach 1947; van Dijk & Kintsch 1983); a query at time t
  reads the model AS OF t (Altmann & Kamide 1999); and where the theme cannot be observed the closure is
  recorded as agent+predicate-only with the ONLINE validity of that cue (Lutz & Radvansky 1997 graded status),
  never a silent equivalence.

ARMS (every scored arm: model vs the INCUMBENT rule as the floor vs an information-free twin, item- or
goal-paired bootstrap CI; populations are MODERN prose -- ROC Stories narrative + the authored OCC gold):
  A  FIXTURES        the four review fixtures as pass/fail witnesses (R02 unavailable / buy-bread not closed
                     by bought-milk / same-sentence later action counts / t-bounded prediction ignores future).
  B  CONTENT         goal-closure discrimination on REAL goals extracted from ROC Stories by the live reader:
                     each goal with a theme yields a MATCHING and a MISMATCHING outcome (gold by construction).
                     B1 lexical theme, B2 anaphoric theme ("it") -- B2 isolates the coref dependency (pri 131).
  C  ORDER           same-sentence realization AFTER the goal span (gold satisfied) paired with one BEFORE it
                     (gold active -- a goal cannot be closed before it is stated).
  D  TIME            prefix-invariance of the forward-prediction goal evidence on real ROC documents: the
                     evidence at t from the full document must equal the evidence at t from the prefix.
  E  NO-REGRESS      the authored satisfaction gold (witness W7) + the reinstatement gold (W8) + the ROC status
                     flip census + the DOWNSTREAM OCC-gold emotion read (n=50) with status_fn A/B.

LANDED-STATE DETECTION: every arm runs against the LIVE hdlab modules when the proposal has landed (detected
by hdlab.goal_register.closing_outcome existing); before landing it builds the proposed module IN MEMORY from
notes/problems/<slug>/goal_constraints_patch.diff (no git apply, no edit of hdlab/, no monkeypatch of the live
package).  The FLOOR is the incumbent rule RECOMPUTED IN THIS CELL, so the A/B survives landing.

GLASS-BOX: stdlib + numpy + hdlab. NO spaCy, NO nltk tagger, NO supervised parser, NO external LLM anywhere.
Writes ONLY to its own get_output_dir.

Run: .venv/Scripts/python.exe experiments/exp_goal_constraints_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_goal_constraints_v1.py --fixtures
     .venv/Scripts/python.exe experiments/exp_goal_constraints_v1.py --run [--n 400] [--boot 2000]
"""
from __future__ import annotations
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("PYTHONHASHSEED", "0")

import argparse
import copy
import importlib.util
import json
import re
import sys
import tempfile
import time
from collections import defaultdict
from datetime import datetime, timezone
from types import SimpleNamespace as N

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR = "goal_constraints_v1"
OUT_DIR = str(get_output_dir(ANCHOR))
SEED = 20260916
SLUG = ("the_goal_register_answers_why_with_another_agents_purpose_marks_a_goal_satisfied_by_verb_and_agent_"
        "alone_and_reads_future_goals_into_time_limited_prediction_make_agent_object_and_time_constraints_binding")
DIFF_PATH = os.path.join(_REPO, "notes", "problems", SLUG, "goal_constraints_patch.diff")
ROC = os.path.join(_REPO, "data", "corpora", "roc_stories", "train.jsonl")


# ===================================================================================================
# THE IMPLEMENTATION UNDER TEST -- the live modules when landed, else the proposal built from the diff
# ===================================================================================================
def _apply_unified(src_text, diff_text, rel):
    """Apply the hunks of `rel` from a unified diff to `src_text` (pure python; PRE-LANDING path only)."""
    lines = src_text.split("\n")
    hunks, active = [], False
    for ln in diff_text.split("\n"):
        if ln.endswith("\r"):
            ln = ln[:-1]      # the diff was taken over CRLF sources; the live source is read with \n endings
        if ln.startswith("--- a/"):
            active = (ln[6:] == rel)
            continue
        if ln.startswith("+++ b/") or ln.startswith("diff ") or ln.startswith("index ") or ln.startswith("\\"):
            continue
        if not active:
            continue
        if ln.startswith("@@"):
            hunks.append([ln, []])
            continue
        if hunks:
            hunks[-1][1].append(" " if ln == "" else ln)
    for head, body in reversed(hunks):
        m = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", head)
        start = int(m.group(1)) - 1
        n_old = int(m.group(2) or 1)
        n_new = int(m.group(4) or 1)
        old, new = [], []
        for l in body:                       # the declared counts END the hunk (a trailing blank is not a line)
            if len(old) >= n_old and len(new) >= n_new:
                break
            if l[:1] in (" ", "-"):
                old.append(l[1:])
            if l[:1] in (" ", "+"):
                new.append(l[1:])
        assert len(old) == n_old and len(new) == n_new, (head, len(old), len(new))
        if lines[start:start + len(old)] != old:
            found = None
            for off in range(1, 400):
                for s2 in (start - off, start + off):
                    if s2 >= 0 and lines[s2:s2 + len(old)] == old:
                        found = s2
                        break
                if found is not None:
                    break
            assert found is not None, ("hunk did not apply: %s" % head)
            start = found
        lines[start:start + len(old)] = new
    return "\n".join(lines)


def _load_from_source(src_text, modname, filename, as_file=None):
    """Execute the proposed source as a module. The compiled code carries the REAL hdlab filename (`as_file`)
    so every path the module derives from __file__ -- the frontend asset paths, the repo root -- resolves
    exactly as it will once the diff lands; the copy written under the cell's own output directory is for
    reading, not for importing."""
    path = os.path.join(OUT_DIR, "_prelanding", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(src_text)
    virt = as_file or path
    spec = importlib.util.spec_from_loader(modname, loader=None, origin=virt)
    mod = importlib.util.module_from_spec(spec)
    mod.__file__ = virt
    sys.modules[modname] = mod
    exec(compile(src_text, virt, "exec"), mod.__dict__)
    return mod


_IMPL = {}


def load_impl(need_reader=False):
    """(goal_register module under test, landed?) -- and when need_reader, also the situation_reader module."""
    key = "reader" if need_reader else "gr"
    if key in _IMPL:
        return _IMPL[key]
    import hdlab.goal_register as GR_live
    landed = hasattr(GR_live, "closing_outcome") and hasattr(GR_live, "content_verdict")
    if landed:
        GR = GR_live
        SR = None
        if need_reader:
            import hdlab.situation_reader as SRmod
            SR = SRmod
    else:
        assert os.path.exists(DIFF_PATH), ("pre-landing path needs the proposed diff: %s" % DIFF_PATH)
        diff = open(DIFF_PATH, encoding="utf-8").read()
        gr_src = _apply_unified(open(os.path.join(_REPO, "hdlab", "goal_register.py"), encoding="utf-8").read(),
                                diff, "hdlab/goal_register.py")
        GR = _load_from_source(gr_src, "hdlab_goal_register_pri135", "goal_register_pri135.py",
                               as_file=os.path.join(_REPO, "hdlab", "goal_register.py"))
        SR = None
        if need_reader:
            sr_src = _apply_unified(open(os.path.join(_REPO, "hdlab", "situation_reader.py"), encoding="utf-8").read(),
                                    diff, "hdlab/situation_reader.py")
            SR = _load_from_source(sr_src, "hdlab_situation_reader_pri135", "situation_reader_pri135.py",
                                   as_file=os.path.join(_REPO, "hdlab", "situation_reader.py"))
    out = (GR, SR, landed) if need_reader else (GR, landed)
    _IMPL[key] = out
    return out


# ===================================================================================================
# THE FLOOR -- the incumbent rule, recomputed here so the A/B survives landing
# ===================================================================================================
def floor_status(goals, events, norm):
    """THE INCUMBENT SATISFACTION RULE (the strongest floor: it is what the tree shipped): a goal is
    satisfied iff some event in a STRICTLY LATER SENTENCE has the same predicate lemma and the same agent.
    The goal's OBJECT is ignored and a realization inside the goal's own sentence is invisible."""
    ev = [(getattr(e, "sent_idx", 0), norm(str(getattr(e, "predicate", "") or "")),
           str(getattr(e, "agent", "") or "").lower()) for e in events]
    out = []
    for g in goals:
        if getattr(g, "negated", False):
            out.append("failed")
            continue
        ah = norm(str(g.goal_head or ""))
        ga = (g.agent_canonical or g.agent or "").lower()
        ok = any(si > g.sent_idx and pl == ah and (ea == ga or ga in ("?", "")) for (si, pl, ea) in ev)
        out.append("satisfied" if ok else "active")
    return out


def _inc_thwarted(g, ah, ga, ev, stexts, GR):
    """The INCUMBENT thwart branch, reproduced: the same three cues, each requiring a STRICTLY LATER
    SENTENCE (the rule the tree ships). The lexicons are the organ's own data tables, read from it."""
    for (si, pl, ea) in ev:
        if si > g.sent_idx and (ea == ga or ga in ("?", "")) and (
                pl in GR.FAILURE_VERBS or GR._norm_pred(pl) in GR.FAILURE_VERBS):
            return True
    if stexts is None:
        return False
    goal_obj = {t for t in GR._tokset(getattr(g, "goal_text", "") or "") if t != ah and len(t) > 2}
    for si in range(g.sent_idx + 1, len(stexts)):
        ts = set(GR._tokset(stexts[si]))
        if ah in ts and (ts & GR._THWART_NEG):
            return True
        if goal_obj and (goal_obj & ts) and (ts & GR.ADVERSE_RESULTANT):
            return True
    return False


def floor_status_thwart(goals, events, GR, sents=None, canon=None):
    """THE STRONGEST FLOOR: hdlab.goal_register.track_status_thwart EXACTLY AS THE TREE SHIPS IT -- the
    agent-canonicalised, irregular-past satisfaction match on a STRICTLY LATER SENTENCE (the goal's object
    and the event's polarity ignored), then the thwart branch, also strictly-later-sentence. Reproduced in
    the cell so the A/B against the proposal survives landing. The FAILURE/ADVERSE/NEG lexicons and the
    lemma normalisers are read from the organ (data tables my change does not touch)."""
    def _agent(surface, si):
        s_ = str(surface or "").lower()
        if canon is not None:
            try:
                c = canon(surface, si)
            except Exception:
                c = None
            if c:
                return str(c).lower()
        return s_
    ev = [(getattr(e, "sent_idx", 0), GR._norm_pred(getattr(e, "predicate", "") or ""),
           _agent(getattr(e, "agent", ""), getattr(e, "sent_idx", 0))) for e in events]
    stexts = [" ".join(str(t) for t in toks) for toks in sents] if sents is not None else None
    out = []
    for g in goals:
        if getattr(g, "negated", False):
            out.append("failed")
            continue
        ah = GR._norm_pred(g.goal_head)
        ga = _agent(g.agent_canonical or g.agent or "", getattr(g, "sent_idx", 0))
        realized = any(si > g.sent_idx and pl == ah and (ea == ga or ga in ("?", ""))
                       for (si, pl, ea) in ev)
        if realized:
            out.append("satisfied")
            continue
        out.append("failed" if _inc_thwarted(g, ah, ga, ev, stexts, GR) else "active")
    return out


def floor_goal_evidence(goals_all, events_all, wants_fn):
    """THE INCUMBENT _goal_lemmas: the agent population comes from the WHOLE event list and each agent's
    goal from the WHOLE-document register -- no t anywhere (the reproduced R04 leak)."""
    agents = sorted({str(getattr(e, "agent", "")).lower() for e in events_all
                     if str(getattr(e, "agent", "")).lower() not in ("?", "", "none")})
    spans = []
    for ag in agents:
        g = wants_fn(ag)
        gt = (getattr(g, "goal_text", None) or "") if g is not None else ""
        if gt:
            spans.append(gt)
    return spans


# ===================================================================================================
# ARM A -- THE FOUR REVIEW FIXTURES (A11's controlled inputs; these become the witness)
# ===================================================================================================
def _ev(sent, pos, pred, agent, patient=None, pol=1, gidx=0):
    return N(sent_idx=sent, pred_idx=pos, global_idx=gidx, predicate=pred, agent=agent,
             patient=patient, polarity=pol)


def fixtures(GR):
    """The four fixtures, run against whichever implementation is handed in. Returns a list of
    {name, got, want, ok} -- ALL must be ok for the proposal; on the unpatched tree F2/F3/F4 fail (that is
    the reproduction), which is exactly what the witness asserts flips at landing."""
    out = []

    def add(name, got, want):
        out.append({"name": name, "got": got, "want": want, "ok": got == want})

    def q(fn):
        """Evaluate a probe; an API the tree does not have yet is reported as UNSUPPORTED, not a crash (the
        same fixture file runs against the unpatched tree, where it must FAIL rather than error)."""
        try:
            return fn()
        except (TypeError, AttributeError, IndexError) as e:
            return "UNSUPPORTED:%s" % type(e).__name__

    # F1 (R02): an agent-constrained purpose query never returns another agent's purpose.
    bob = GR.Goal(agent="bob", goal_head="eat", goal_text="eat dinner", kind="purpose_marked",
                  source_verb="work", sent_idx=0, verb_tok=1, to_tok=2)
    reg = GR.GoalRegister([bob])
    add("F1a why(work,bob) is bob purpose", q(lambda: getattr(reg.why("work", "bob"), "agent", None)), "bob")
    add("F1b why(work,alice) is not bob purpose",
        q(lambda: getattr(reg.why("work", "alice"), "agent", None)), None)

    # F2 (R03 content): "buy bread" is NOT closed by buying a car, and IS closed by buying bread.
    def mk_goal():
        return GR.Goal(agent="alice", goal_head="buy", goal_text="buy bread", kind="desire",
                       source_verb="want", sent_idx=0, verb_tok=1, to_tok=2)

    for patient, want in (("bread", "satisfied"), ("car", "active")):
        g = mk_goal()
        add("F2 track_status: buy bread + bought %s -> %s" % (patient, want),
            q(lambda: (GR.track_status([g], [_ev(1, 1, "buy", "alice", patient)]), g.status)[1]), want)
        g2 = mk_goal()
        add("F2 track_status_thwart: buy bread + bought %s -> %s" % (patient, want),
            q(lambda: (GR.track_status_thwart([g2], [_ev(1, 1, "buy", "alice", patient)],
                                              sents=[["plain"], ["plain"]]), g2.status)[1]), want)

    # F3 (R03 order): a realization LATER IN THE GOAL'S OWN SENTENCE counts.
    g = mk_goal()
    add("F3 track_status: same-sentence later buy bread -> satisfied",
        q(lambda: (GR.track_status([g], [_ev(0, 7, "buy", "alice", "bread")]), g.status)[1]), "satisfied")
    g2 = mk_goal()
    add("F3 track_status_thwart: same-sentence later buy bread -> satisfied",
        q(lambda: (GR.track_status_thwart([g2], [_ev(0, 7, "buy", "alice", "bread")],
                                          sents=[["plain"], ["plain"]]), g2.status)[1]), "satisfied")
    # ... and an event BEFORE the goal is stated cannot close it (the can-fail half of the same fixture)
    g3 = mk_goal()
    g3.sent_idx, g3.verb_tok, g3.to_tok = 0, 6, 7
    add("F3b an outcome BEFORE the goal span does not close it",
        q(lambda: (GR.track_status([g3], [_ev(0, 1, "buy", "alice", "bread")]), g3.status)[1]), "active")

    # F4 (R04 time): a t-bounded query reads only goals stated at or before t.
    future = GR.Goal(agent="alice", goal_head="buy", goal_text="buy yacht", kind="desire",
                     source_verb="want", sent_idx=5, verb_tok=1, to_tok=2)
    reg2 = GR.GoalRegister([future])
    add("F4a wants(alice, t=0) with a goal stated at s5", q(lambda: reg2.wants("alice", 0)), None)
    add("F4b wants(alice) unbounded still sees it", q(lambda: getattr(reg2.wants("alice"), "goal_text", None)), "buy yacht")
    # the status at t: a goal closed at s3 is still ACTIVE at t=1
    g4 = GR.Goal(agent="alice", goal_head="buy", goal_text="buy bread", kind="desire", source_verb="want",
                 sent_idx=0, verb_tok=1, to_tok=2)
    GR.track_status([g4], [_ev(3, 1, "buy", "alice", "bread")])
    reg3 = GR.GoalRegister([g4])
    add("F4c status at t=1 of a goal closed at s3", q(lambda: reg3.status_of(g4, 1)), "active")
    add("F4d status at t=3 of a goal closed at s3", q(lambda: reg3.status_of(g4, 3)), "satisfied")
    add("F4e achieved(t=1) of a goal closed at s3", q(lambda: reg3.achieved("alice", "buy", 1)), "active")
    # D01 polarity: a NEGATED outcome does not close the goal
    g5 = mk_goal()
    add("F5 a negated outcome (she did not buy the bread) does not close the goal",
        q(lambda: (GR.track_status([g5], [_ev(1, 1, "buy", "alice", "bread", pol=-1)]), g5.status)[1]), "active")
    # the LABELLED fallback: the same-agent fallback is reported as a fallback, not as a purpose
    add("F6 why() provenance labels the same-agent fallback",
        q(lambda: reg.why("swim", "bob", with_provenance=True)[1]), "same_agent_current_goal_fallback")
    add("F6b why() provenance says unavailable for an agent with nothing",
        q(lambda: reg.why("swim", "zoe", with_provenance=True)[1]), "unavailable")

    # F7 (the OCC-gold regression this brief located and repaired): an identity DIFFERENCE that rests on a
    # PRONOUN is not evidence. The measured case: the entity files resolved "she finally won IT" to
    # "weekend", so the goal's own "championship" read as a DIFFERENT thing and a plain realization was
    # vetoed. Two independently NAMED themes still veto (F2 above).
    def _canon_weekend(surface, si):
        return {"championship": "championship", "it": "weekend"}.get(str(surface).lower())

    def mk_win():
        return GR.Goal(agent="maya", goal_head="win", goal_text="win the championship", kind="desire",
                       source_verb="want", sent_idx=0, verb_tok=1, to_tok=2)
    g7 = mk_win()
    add("F7 an anaphoric theme the files resolve elsewhere does NOT veto the closure",
        q(lambda: (GR.track_status([g7], [_ev(1, 4, "win", "maya", "it")], canon=_canon_weekend),
                   g7.status)[1]), "satisfied")
    add("F7b ... and the record SAYS the identity was unconfirmed, never a match",
        q(lambda: g7.status_evidence), "anaphoric_theme_identity_unconfirmed")

    # F8 (precision-weighted veto): a conflicting theme read off an arc the reader does not trust is not
    # evidence; the same conflict on a trusted arc still vetoes. The measured case: "he crossed the line and
    # finished" binds `line` as the patient of `finished` with conf 0.27.
    g8a, g8b = mk_win(), mk_win()
    ev_lo = _ev(1, 4, "win", "maya", "lottery")
    ev_lo.patient_conf = 0.27
    ev_hi = _ev(1, 4, "win", "maya", "lottery")
    ev_hi.patient_conf = 0.92
    add("F8 a conflicting theme on a LOW-precision arc does not veto",
        q(lambda: (GR.track_status([g8a], [ev_lo]), g8a.status)[1]), "satisfied")
    add("F8b the same conflict on a TRUSTED arc still vetoes",
        q(lambda: (GR.track_status([g8b], [ev_hi]), g8b.status)[1]), "active")
    return out


def fixtures_on_live():
    """The same fixtures against the LIVE hdlab modules (whatever the tree currently is)."""
    import hdlab.goal_register as GR
    return fixtures(GR)


# ===================================================================================================
# THE CORPUS -- real modern narrative prose (ROC Stories) read by the LIVE reader
# ===================================================================================================
def _roc_passages(n):
    out = []
    with open(ROC, encoding="utf-8") as f:
        for line in f:
            if len(out) >= n:
                break
            r = json.loads(line)
            sents = [r.get("sentence%d" % i, "") for i in range(1, 6)]
            text = " ".join(s for s in sents if s)
            first = (sents[0].split() or ["X"])[0].strip(".,")
            if first and first[0].isupper():
                out.append({"id": r.get("storyid", "roc%d" % len(out)), "char": first, "text": text})
    return out


def read_corpus(n, force=False):
    """Read n ROC passages with the LIVE reader (track_goals) ONCE and cache the extracted goal/event
    records. Extraction is UNCHANGED by the proposal, so the same records serve every arm and both sides of
    every A/B."""
    cache = os.path.join(OUT_DIR, "roc_records_v2_n%d.json" % n)
    if os.path.exists(cache) and not force:
        with open(cache, encoding="utf-8") as f:
            return json.load(f)
    from hdlab.situation_reader import SituationReader
    from experiments._tom_chain import split_sents, tokenize
    from experiments._occ_probe import write_conll
    import hdlab.goal_register as GRlive
    t0 = time.time()
    passages = _roc_passages(n)
    reader = SituationReader(track_goals=True, track_affect=True)
    tmp = tempfile.mkdtemp(prefix="p135_roc_")
    recs = []
    for p in passages:
        cp = write_conll(p["text"], p["char"], tmp, p["id"])
        sm = reader.read(cp)
        reg = getattr(sm, "goal_register", None)
        goals = list(getattr(reg, "goals", []) or [])
        sents = [tokenize(s) for s in split_sents(p["text"])]
        canon, _names = GRlive.make_canonicalizer(sm)
        cmap = {}

        def _probe(surface, si):
            if not surface:
                return
            k = "%s|%d" % (str(surface).lower(), si)
            if k not in cmap:
                try:
                    cmap[k] = canon(surface, si)
                except Exception:
                    cmap[k] = None
        events = []
        for e in sm.events:
            events.append({"sent_idx": e.sent_idx, "pred_idx": e.pred_idx, "predicate": str(e.predicate),
                           "agent": str(e.agent), "patient": str(e.patient), "polarity": e.polarity,
                           # the reader's OWN calibrated reliability of the arc the patient was read off
                           # (Friston precision) -- the graded signal the goal closure used to throw away
                           "patient_conf": getattr(e, "patient_conf", None)})
            _probe(e.patient, e.sent_idx)
            _probe(e.agent, e.sent_idx)
        # LEVER 2 (measured before it is landed): the theme the ARGUMENT-STRUCTURE ORGAN binds for each
        # goal, computed from the reader's OWN parse of the goal's sentence (the same call the landed form
        # makes inside extract_goals).
        GRimpl, _lnd = load_impl()
        pos_by_sent = {}
        heads_by_sent = {}

        def _organ_theme_for(g):
            if not hasattr(GRimpl, "organ_theme"):
                return None
            si = g.sent_idx
            if si >= len(sents) or g.to_tok is None or g.to_tok < 0:
                return None
            if si not in pos_by_sent:
                try:
                    pos_by_sent[si] = reader._cached_tag(list(sents[si]))
                    heads_by_sent[si] = reader._cached_parse_heads(list(sents[si]), pos_by_sent[si])
                except Exception:
                    pos_by_sent[si], heads_by_sent[si] = None, None
            if heads_by_sent.get(si) is None:
                return None
            try:
                return GRimpl.organ_theme(list(sents[si]), list(pos_by_sent[si]), heads_by_sent[si], g.to_tok + 1)
            except Exception:
                return None
        grecs = []
        for g in goals:
            grecs.append({"organ_theme": _organ_theme_for(g),
                          "agent": g.agent, "agent_canonical": g.agent_canonical, "goal_head": g.goal_head,
                          "goal_text": g.goal_text, "kind": g.kind, "source_verb": g.source_verb,
                          "sent_idx": g.sent_idx, "verb_tok": g.verb_tok, "to_tok": g.to_tok,
                          "negated": bool(g.negated), "status_live": g.status})
            for w in str(g.goal_text or "").split():
                _probe(w.strip(".,;:!?\"'").lower(), g.sent_idx)
        recs.append({"id": p["id"], "char": p["char"], "n_sents": len(sents),
                     "sents": [[str(t) for t in s] for s in sents],
                     "goals": grecs, "events": events, "canon": cmap})
        del sm
    with open(cache, "w", encoding="utf-8") as f:
        json.dump({"n_passages": len(recs), "elapsed_s": round(time.time() - t0, 1), "records": recs}, f)
    print("[corpus] %d ROC passages, %d goals, %.1fs -> %s"
          % (len(recs), sum(len(r["goals"]) for r in recs), time.time() - t0, cache), flush=True)
    with open(cache, encoding="utf-8") as f:
        return json.load(f)


def _mk_goals(GR, grecs, theme_source="organ"):
    """theme_source: 'span' = the head-final reading of the goal span (the fallback rung); 'organ' = the
    theme the argument-structure organ bound at extraction (lever 2), falling back to the span when the
    organ bound nothing."""
    out = []
    for r in grecs:
        g = GR.Goal(agent=r["agent"], goal_head=r["goal_head"], goal_text=r["goal_text"], kind=r["kind"],
                    source_verb=r["source_verb"], sent_idx=r["sent_idx"], verb_tok=r["verb_tok"],
                    to_tok=r["to_tok"], negated=r["negated"])
        g.agent_canonical = r["agent_canonical"]
        ot = r.get("organ_theme")
        if theme_source == "organ" and ot:
            _lk = getattr(GR, "_lemma_noun", GR._lemma)
            span_toks = {_lk(t) for t in str(r["goal_text"] or "").lower().split()}
            if _lk(ot) in span_toks:                 # the landed span bound (the cache is refreshed by
                                                     # --refresh-themes whenever the organ rule changes)
                try:
                    g.goal_object, g.object_source = ot, "argument_structure_organ"
                except Exception:
                    pass
        out.append(g)
    return out


def _mk_events(erecs, precision=True):
    """precision=False ABLATES the theme-precision signal (patient_conf -> None), which is exactly the
    'without lever 1' arm: a conflicting theme then vetoes the closure unconditionally."""
    out = []
    for e in erecs:
        ev = _ev(e["sent_idx"], e["pred_idx"], e["predicate"], e["agent"], e["patient"], e["polarity"])
        ev.patient_conf = e.get("patient_conf") if precision else None
        out.append(ev)
    return out


def _canon_fn(cmap):
    def canon(surface, si):
        return cmap.get("%s|%d" % (str(surface).lower(), int(si)))
    return canon


# ===================================================================================================
# BOOTSTRAP (paired over items, clustered by goal)
# ===================================================================================================
def _paired_boot(ok_a, ok_b, clusters, B, seed):
    """Paired cluster bootstrap of mean(a) - mean(b). clusters = a cluster id per item."""
    ids = sorted(set(clusters))
    by = defaultdict(list)
    for i, c in enumerate(clusters):
        by[c].append(i)
    a = np.asarray(ok_a, float)
    b = np.asarray(ok_b, float)
    if not ids:
        return [None, None, None]
    rng = np.random.default_rng(seed)
    nC = len(ids)
    diffs = np.empty(B)
    for k in range(B):
        pick = rng.integers(0, nC, nC)
        idx = [i for j in pick for i in by[ids[j]]]
        diffs[k] = a[idx].mean() - b[idx].mean()
    diffs.sort()
    return [round(float(a.mean() - b.mean()), 4), round(float(diffs[int(0.025 * B)]), 4),
            round(float(diffs[int(0.975 * B)]), 4)]


# ===================================================================================================
# ARM B -- CONTENT: goal-closure discrimination on real goals (gold by construction)
# ===================================================================================================
def arm_content(GR, recs, seed=SEED, B=2000, anaphoric=False, theme_source="organ"):
    """For every REAL goal that states a theme, build the MATCHING outcome (gold satisfied) and a
    MISMATCHING outcome whose theme is another goal's theme (gold active). model = the proposal;
    floor = the incumbent predicate+agent rule; twin = the proposal with the outcome THEMES PERMUTED across
    items (information-free: the themes no longer belong to their goals)."""
    rng = np.random.default_rng(seed)
    pool = []
    for r in recs["records"]:
        for gr_ in r["goals"]:
            g = _mk_goals(GR, [gr_], theme_source)[0]
            if getattr(g, "negated", False):
                continue
            obj = GR.goal_object(g)
            if not obj:
                continue
            pool.append((r, gr_, obj))
    themes = [o for (_r, _g, o) in pool]
    items = []
    for i, (r, gr_, obj) in enumerate(pool):
        # a foreign theme with a DIFFERENT lemma (else the "mismatch" would not be one)
        alt = None
        for _try in range(50):
            cand = themes[int(rng.integers(0, len(themes)))]
            if GR._lemma_noun(cand) != GR._lemma_noun(obj):
                alt = cand
                break
        if alt is None:
            continue
        pos_theme = "it" if anaphoric else obj
        items.append({"cluster": "%s#%d" % (r["id"], i), "rec": r, "grec": gr_,
                      "theme": pos_theme, "gold": "satisfied", "obj": obj})
        items.append({"cluster": "%s#%d" % (r["id"], i), "rec": r, "grec": gr_,
                      "theme": alt, "gold": "active", "obj": obj})
    ok_m, ok_f, ok_t, clusters, ev_hist = [], [], [], [], defaultdict(int)
    perm = list(rng.permutation(len(items)))
    for k, it in enumerate(items):
        r = it["rec"]
        g = _mk_goals(GR, [it["grec"]], theme_source)[0]
        canon = _canon_fn(r["canon"])
        out = _ev(g.sent_idx + 1, 1, g.goal_head, (g.agent_canonical or g.agent), it["theme"])
        GR.track_status([g], [out], canon=canon)
        ok_m.append(int(g.status == it["gold"]))
        ev_hist[str(g.status_evidence)] += 1
        gf = _mk_goals(GR, [it["grec"]], theme_source)[0]
        ok_f.append(int(floor_status([gf], [out], GR._lemma)[0] == it["gold"]))
        # info-free twin: the outcome theme is drawn from a PERMUTED item (the binding is destroyed)
        gt = _mk_goals(GR, [it["grec"]], theme_source)[0]
        out_t = _ev(g.sent_idx + 1, 1, g.goal_head, (g.agent_canonical or g.agent), items[perm[k]]["theme"])
        GR.track_status([gt], [out_t], canon=canon)
        ok_t.append(int(gt.status == it["gold"]))
        clusters.append(it["cluster"])
    n = len(items)
    res = {"n_items": n, "n_goals_with_theme": len(pool),
           "model_acc": round(float(np.mean(ok_m)), 4) if n else None,
           "floor_incumbent_acc": round(float(np.mean(ok_f)), 4) if n else None,
           "twin_permuted_theme_acc": round(float(np.mean(ok_t)), 4) if n else None,
           "model_minus_floor": _paired_boot(ok_m, ok_f, clusters, B, seed + 1) if n else None,
           "model_minus_twin": _paired_boot(ok_m, ok_t, clusters, B, seed + 2) if n else None,
           "evidence_histogram": dict(ev_hist),
           "population": ("REAL goals extracted by the live reader from ROC Stories; each goal contributes a "
                          "matching and a mismatching outcome, gold by construction%s")
                         % (" (the matching theme is the ANAPHOR 'it', so only the entity files can decide)"
                            if anaphoric else "")}
    res["ci_sep_over_floor"] = bool(res["model_minus_floor"] and res["model_minus_floor"][1] > 0)
    res["ci_sep_over_twin"] = bool(res["model_minus_twin"] and res["model_minus_twin"][1] > 0)
    return res


# ===================================================================================================
# ARM C -- ORDER: within-sentence realization
# ===================================================================================================
def arm_order(GR, recs, seed=SEED, B=2000):
    """For every REAL goal: an outcome in the SAME sentence AFTER the goal span (gold satisfied) paired with
    one BEFORE the goal is stated (gold active). The incumbent cannot see either (strictly-later sentence),
    so it scores the base rate; the twin permutes the position across items."""
    rng = np.random.default_rng(seed + 5)
    ok_m, ok_f, ok_t, clusters = [], [], [], []
    pool = [(r, gr_) for r in recs["records"] for gr_ in r["goals"] if not gr_["negated"]]
    positions = []
    for r, gr_ in pool:
        g = _mk_goals(GR, [gr_])[0]
        positions.append((GR.goal_span_end(g) + 1, max(0, min(g.verb_tok, g.to_tok) - 1)))
    for i, (r, gr_) in enumerate(pool):
        canon = _canon_fn(r["canon"])
        after_pos, before_pos = positions[i]
        j = int(rng.integers(0, len(positions)))
        for (pos, gold, tw_pos) in ((after_pos, "satisfied", positions[j][0]),
                                    (before_pos, "active", positions[j][1])):
            g = _mk_goals(GR, [gr_])[0]
            theme = GR.goal_object(g)
            out = _ev(g.sent_idx, pos, g.goal_head, (g.agent_canonical or g.agent), theme)
            GR.track_status([g], [out], canon=canon)
            ok_m.append(int(g.status == gold))
            gf = _mk_goals(GR, [gr_])[0]
            ok_f.append(int(floor_status([gf], [out], GR._lemma)[0] == gold))
            gt = _mk_goals(GR, [gr_])[0]
            out_t = _ev(g.sent_idx, tw_pos, g.goal_head, (g.agent_canonical or g.agent), theme)
            GR.track_status([gt], [out_t], canon=canon)
            ok_t.append(int(gt.status == gold))
            clusters.append("%s#%d" % (r["id"], i))
    n = len(ok_m)
    res = {"n_items": n, "n_goals": len(pool),
           "model_acc": round(float(np.mean(ok_m)), 4) if n else None,
           "floor_incumbent_acc": round(float(np.mean(ok_f)), 4) if n else None,
           "twin_permuted_position_acc": round(float(np.mean(ok_t)), 4) if n else None,
           "model_minus_floor": _paired_boot(ok_m, ok_f, clusters, B, seed + 6) if n else None,
           "model_minus_twin": _paired_boot(ok_m, ok_t, clusters, B, seed + 7) if n else None,
           "population": "REAL goals from ROC Stories; an outcome after the goal span vs before it, same sentence"}
    res["ci_sep_over_floor"] = bool(res["model_minus_floor"] and res["model_minus_floor"][1] > 0)
    res["ci_sep_over_twin"] = bool(res["model_minus_twin"] and res["model_minus_twin"][1] > 0)
    return res


# ===================================================================================================
# ARM D -- TIME: prefix-invariance of the forward-prediction goal evidence
# ===================================================================================================
class _Recorder:
    """A projector that records the closure's INPUTS (the review's probe): no scoring, no store asset."""

    def available(self):
        return True

    def project(self, context, goals, candidates, gain=2.0):
        return N(context=list(context), goals=list(goals), candidates=None)


def arm_time(GR, SR, recs, cap=None):
    """For every ROC document and every t, the goal evidence the prediction closure is given must be the
    SAME whether the reader holds the whole document or only the prefix 0..t. model = the t-threaded
    closure; floor = the incumbent closure (no t in the goal read)."""
    leaks_model = leaks_floor = trials = docs_with_future_goal = 0
    examples = []
    for r in recs["records"][:cap]:
        goals_all = _mk_goals(GR, r["goals"])
        events_all = _mk_events(r["events"])
        canon = _canon_fn(r["canon"])
        if not goals_all:
            continue
        GR.track_status(goals_all, events_all, canon=canon)
        reg_full = GR.GoalRegister(goals_all)
        sents = [list(s) for s in r["sents"]]
        for t in range(r["n_sents"]):
            if not any(g.sent_idx > t for g in goals_all):
                continue
            docs_with_future_goal += 1
            # the PREFIX model: the reader that has only read sentences 0..t
            gp = _mk_goals(GR, [x for x in r["goals"] if x["sent_idx"] <= t])
            ep = [e for e in events_all if e.sent_idx <= t]
            GR.track_status(gp, ep, canon=canon)
            reg_pre = GR.GoalRegister(gp)
            sm_full = N(events=events_all, wants=reg_full.wants, forward_prediction=None)
            sm_pre = N(events=ep, wants=reg_pre.wants, forward_prediction=None)
            SR.SituationReader._read_prediction(N(_gek_org=_Recorder()), sm_full, sents)
            SR.SituationReader._read_prediction(N(_gek_org=_Recorder()), sm_pre, sents[:t + 1])
            full = sm_full.predict_next_event(["a", "b"], t=t)
            pre = sm_pre.predict_next_event(["a", "b"], t=t)
            same_model = (full.goals == pre.goals)
            f_full = floor_goal_evidence(goals_all, events_all, reg_full.wants)
            f_pre = floor_goal_evidence(gp, ep, reg_pre.wants)
            same_floor = (f_full == f_pre)
            trials += 1
            leaks_model += int(not same_model)
            leaks_floor += int(not same_floor)
            if not same_floor and len(examples) < 5:
                examples.append({"doc": r["id"], "t": t, "floor_full": f_full, "floor_prefix": f_pre,
                                 "model_full": full.goals, "model_prefix": pre.goals})
    return {"n_trials": trials,
            "model_leaks": leaks_model, "floor_incumbent_leaks": leaks_floor,
            "model_leak_rate": round(leaks_model / trials, 4) if trials else None,
            "floor_leak_rate": round(leaks_floor / trials, 4) if trials else None,
            "examples": examples,
            "population": ("every (ROC document, t) for which a goal is stated AFTER t -- the only trials on "
                           "which the leak can show; the check is an IDENTITY (prefix-invariance), not an "
                           "accuracy, so it is reported as a rate with its count, not with a CI")}


# ===================================================================================================
# ARM E -- NO-REGRESS
# ===================================================================================================
def _tagger():
    from hdlab.pos_tagger import PosTagger
    if not hasattr(_tagger, "_tg"):
        _tagger._tg = PosTagger.load(os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json"))
    return _tagger._tg


def arm_authored(GR, seed=SEED, n_twin=200):
    """The two AUTHORED goal golds the landed witness asserts (test_goal_register.py W7 + W8), recomputed
    under the proposal: the satisfaction gold (active/satisfied/failed) and the Suh-Trabasso reinstatement
    gold. These are the no-regress populations for the goal organ itself."""
    from experiments.exp_goal_register_qa_v1 import _SAT_GOLD, _REINSTATE_GOLD

    class _Ev:
        def __init__(self, pred, agent, si):
            self.predicate, self.agent, self.sent_idx = pred, agent, si
            self.global_idx, self.pred_idx, self.patient, self.polarity = si, None, None, None

    n = m_ok = f_ok = 0
    by_status = defaultdict(lambda: [0, 0])
    for toks, agent, ghead, laters, gold in _SAT_GOLD:
        pos = _tagger().tag(list(toks))
        goals = GR.extract_goals([toks], [pos])
        for g in goals:
            g.agent_canonical = agent
        events = [_Ev(p, a, si) for (p, a, si) in laters]
        GR.track_status(goals, events)
        got = GR.GoalRegister(goals).achieved(agent, ghead)
        n += 1
        m_ok += int(got == gold)
        f_ok += int(gold == "active")
        by_status[gold][0] += 1
        by_status[gold][1] += int(got == gold)
    sat = {"n": n, "model_acc": round(m_ok / n, 4) if n else None,
           "floor_always_active_acc": round(f_ok / n, 4) if n else None,
           "by_status": {k: {"n": v[0], "ok": v[1]} for k, v in by_status.items()},
           "witness_bar_model_acc_ge_0.9": bool(n and (m_ok / n) >= 0.9)}

    nr = r_ok = fl_ok = 0
    built = []
    for sup_s, sub_s, agent, sup_h, sub_h, laters in _REINSTATE_GOLD:
        sents = [sup_s, sub_s]
        pos = [_tagger().tag(list(s)) for s in sents]
        goals = GR.extract_goals(sents, pos)
        for g in goals:
            g.agent_canonical = agent
        events = [_Ev(p, a, si) for (p, a, si) in laters]
        GR.track_status(goals, events)
        reg = GR.GoalRegister(goals)
        mg = reg.wants(agent)
        nr += 1
        r_ok += int(mg is not None and GR._lemma(mg.goal_head) == GR._lemma(sup_h))
        recent = reg.goals_of(agent)[0] if reg.goals_of(agent) else None
        fl_ok += int(recent is not None and GR._lemma(recent.goal_head) == GR._lemma(sup_h))
        built.append((goals, agent, sup_h))
    twin = []
    for k in range(n_twin):
        rng = np.random.default_rng(seed + 1 + k)
        ok = 0
        for goals, agent, sup_h in built:
            tg = [copy.copy(g) for g in goals]
            st = [g.status for g in tg]
            rng.shuffle(st)
            for g, s in zip(tg, st):
                g.status = s
            tw = GR.GoalRegister(tg).wants(agent)
            ok += int(tw is not None and GR._lemma(tw.goal_head) == GR._lemma(sup_h))
        twin.append(ok / max(1, nr))
    twin.sort()
    rei = {"n": nr, "model_reinstatement_acc": round(r_ok / nr, 4) if nr else None,
           "floor_recency_acc": round(fl_ok / nr, 4) if nr else None,
           "twin_status_shuffle_p95": round(float(twin[int(0.95 * len(twin))]), 4) if twin else None,
           "witness_bar_model_ge_0.9_floor_le_0.1": bool(nr and (r_ok / nr) >= 0.9 and (fl_ok / nr) <= 0.1)}
    return {"authored_satisfaction_W7": sat, "authored_reinstatement_W8": rei}


def arm_flip_census(GR, recs):
    """The REAL-TEXT frequency of the defect: on ROC prose, how many goal statuses and how many wants()
    answers does the proposal change, in which direction, and with what evidence."""
    flips = defaultdict(int)
    flips_nothwart = defaultdict(int)
    ev_hist = defaultdict(int)
    wants_changed = wants_added = wants_removed = wants_swapped = 0
    n_goals = n_with_theme = n_decidable = 0
    examples = []
    stats = GR.ContentMatchAccrual()
    for r in recs["records"]:
        goals_m = _mk_goals(GR, r["goals"])
        goals_f = _mk_goals(GR, r["goals"])
        events = _mk_events(r["events"])
        canon = _canon_fn(r["canon"])
        if not goals_m:
            continue
        GR.track_status_thwart(goals_m, events, sents=[list(s) for s in r["sents"]], canon=canon, stats=stats)
        floors = floor_status_thwart(goals_f, events, GR, sents=[list(s) for s in r["sents"]], canon=canon)
        floors_nothwart = floor_status(goals_f, events, GR._norm_pred)
        for g, fs in zip(goals_m, floors):
            n_goals += 1
            if GR.goal_object(g):
                n_with_theme += 1
            if g.status_evidence in ("entity_identity", "head_lemma"):
                n_decidable += 1
            ev_hist[str(g.status_evidence)] += 1
            if g.status != fs:
                flips["%s->%s" % (fs, g.status)] += 1
                if len(examples) < 16:
                    examples.append({"doc": r["id"], "goal": g.goal_text, "agent": g.agent_canonical,
                                     "floor": fs, "model": g.status, "evidence": g.status_evidence,
                                     "theme": GR.goal_object(g)})
        for g, fs in zip(goals_m, floors_nothwart):
            if g.status != fs:
                flips_nothwart["%s->%s" % (fs, g.status)] += 1
        # wants() effect per agent
        for g, fs in zip(goals_f, floors):
            g.status = fs
        reg_m, reg_f = GR.GoalRegister(goals_m), GR.GoalRegister(goals_f)
        for ag in set(reg_m.agents()) | set(reg_f.agents()):
            wm, wf = reg_m.wants(ag), reg_f.wants(ag)
            hm = getattr(wm, "goal_text", None)
            hf = getattr(wf, "goal_text", None)
            if hm != hf:
                wants_changed += 1
                if hf is None:
                    wants_added += 1
                elif hm is None:
                    wants_removed += 1
                else:
                    wants_swapped += 1
    return {"n_goals": n_goals, "n_goals_stating_a_theme": n_with_theme,
            "n_closures_decided_on_an_observed_theme": n_decidable,
            "status_flips_vs_incumbent": dict(flips),
            "status_flips_vs_satisfaction_only_floor": dict(flips_nothwart),
            "evidence_histogram": dict(ev_hist),
            "wants_answers_changed": wants_changed, "wants_added": wants_added,
            "wants_removed": wants_removed, "wants_swapped": wants_swapped,
            "content_accrual": stats.as_dict(), "examples": examples,
            "population": "every goal the live reader extracted from the ROC passages read"}


def _inject_organ_themes(GR, reader, sm, sents):
    """Set each live goal THEME from the ARGUMENT-STRUCTURE ORGAN exactly as the landed extractor does (so
    the downstream arm can be measured before the extractor change lands). Returns how many were bound."""
    if not hasattr(GR, "organ_theme"):
        return 0
    reg = getattr(sm, "goal_register", None)
    bound = 0
    for g in list(getattr(reg, "goals", []) or []):
        si = getattr(g, "sent_idx", 0)
        if si >= len(sents) or g.to_tok is None or g.to_tok < 0:
            continue
        try:
            pos = reader._cached_tag(list(sents[si]))
            heads = reader._cached_parse_heads(list(sents[si]), pos)
            th = GR.organ_theme(list(sents[si]), list(pos), heads, g.to_tok + 1, GR.goal_span_end(g))
        except Exception:
            th = None
        if th:
            g.goal_object, g.object_source = th, "argument_structure_organ"
            bound += 1
    return bound


_TWIN_MARGINAL = ["active", "satisfied", "failed"]      # replaced by the model's own marginal at run time


def arm_occ_gold(GR, cap=None, theme_source="organ"):
    """THE DOWNSTREAM CONSUMER: hdlab.occ_appraisal.infer_emotion reads the goal STATUS as its desirability.
    Same reads, THREE status functions -- the incumbent rule (floor), the proposal, and the proposal with the
    theme-PRECISION signal ablated (lever 1 removed) -- scored against the authored OCC gold (n=50)."""
    from experiments._occ_probe import load_gold, write_conll, _protagonist_canon
    from experiments._tom_chain import split_sents, tokenize
    from hdlab.situation_reader import SituationReader
    import hdlab.occ_appraisal as OCC

    def _floor_status_fn(goals, events, sents=None, canon=None):
        """THE STRONGEST FLOOR: the incumbent track_status_thwart, thwart branch included."""
        import hdlab.goal_register as GRlive
        for g, st in zip(goals, floor_status_thwart(goals, events, GRlive, sents=sents, canon=canon)):
            g.status = st
        return goals

    def _sat_only_floor_fn(goals, events, sents=None, canon=None):
        """The weaker satisfaction-only floor (no thwart branch), kept as an informational reference."""
        import hdlab.goal_register as GRlive
        for g, st in zip(goals, floor_status(goals, events, GRlive._norm_pred)):
            g.status = st
        return goals

    marginal = []
    twin_rng = np.random.default_rng(SEED + 99)

    def _twin_status_fn(goals, events, sents=None, canon=None):
        """INFO-FREE TWIN: every goal gets a status DRAWN from the model's OWN status marginal on this very
        population (so the desirability keeps its base rates exactly) with no relation to this passage --
        the shape is preserved and the binding is destroyed. Run in a second pass, after the marginal is
        measured in the first."""
        marg = marginal or ["active"]
        for g in goals:
            g.status = marg[int(twin_rng.integers(0, len(marg)))]
        return goals

    def _record_marginal(goals, events, sents=None, canon=None):
        GR.track_status_thwart(goals, events, sents=sents, canon=canon)
        marginal.extend(g.status for g in goals)
        return goals

    def _noprec_status_fn(goals, events, sents=None, canon=None):
        evs = []
        for e in events:
            e2 = copy.copy(e)
            try:
                e2.patient_conf = None
            except Exception:
                pass
            evs.append(e2)
        return GR.track_status_thwart(goals, evs, sents=sents, canon=canon)

    gold = load_gold()[:cap]
    reader = SituationReader(track_goals=True, track_affect=True)
    tmp = tempfile.mkdtemp(prefix="p135_occ_")
    # the OPT-IN theme-compatibility arm (the brief's "or a COMPATIBLE one from the reader's files"): the
    # structured relational store decides whether two different words name the same thing. It is NOT the
    # shipped default (it reads WordNet/ConceptNet at inference), so it is measured here as a lead.
    _matcher = None
    try:
        from hdlab.structured_matcher import StructuredMatcher
        _matcher = StructuredMatcher(use_valence=False)
    except Exception as _e:
        print("[occ] structured matcher unavailable: %s" % _e, flush=True)

    def _compat_status_fn(goals, events, sents=None, canon=None):
        return GR.track_status_thwart(goals, events, sents=sents, canon=canon, matcher=_matcher)

    names = ("floor", "model", "model_no_precision", "floor_satisfaction_only", "twin",
             "model_with_compatibility")
    ok = {k: 0 for k in names}
    abst = {k: 0 for k in names}
    per_item = {k: [] for k in names}
    n = n_bound = 0
    changed = []
    for it in gold:
        cp = write_conll(it["text"], it["char"], tmp, it["id"])
        sm = reader.read(cp)
        sents = [tokenize(s) for s in split_sents(it["text"])]
        if theme_source == "organ":
            n_bound += _inject_organ_themes(GR, reader, sm, sents)
        canon = _protagonist_canon(sm, it["char"])
        res = {}
        arms = [("floor", _floor_status_fn), ("model", _record_marginal),
                ("model_no_precision", _noprec_status_fn),
                ("floor_satisfaction_only", _sat_only_floor_fn)]
        if _matcher is not None:
            arms.append(("model_with_compatibility", _compat_status_fn))
        for name, fn in arms:
            e = OCC.infer_emotion(sm, it["char"], sents=sents, status_fn=fn, canon=canon)
            res[name] = getattr(e, "occ_type", None)
        n += 1
        for k in names:
            if k == "twin" or k not in res:
                continue
            ok[k] += int(res[k] == it["type"])
            abst[k] += int(res[k] is None)
            per_item[k].append(int(res[k] == it["type"]))
        if res["model"] != res["floor"]:
            changed.append({"id": it["id"], "gold": it["type"], "floor": res["floor"], "model": res["model"],
                            "model_no_precision": res["model_no_precision"]})
        del sm
    # SECOND PASS -- the info-free twin, now that the model's own status marginal is known
    for it in gold:
        cp = write_conll(it["text"], it["char"], tmp, it["id"])
        sm = reader.read(cp)
        sents = [tokenize(s) for s in split_sents(it["text"])]
        canon = _protagonist_canon(sm, it["char"])
        e = OCC.infer_emotion(sm, it["char"], sents=sents, status_fn=_twin_status_fn, canon=canon)
        got = getattr(e, "occ_type", None)
        ok["twin"] += int(got == it["type"])
        abst["twin"] += int(got is None)
        per_item["twin"].append(int(got == it["type"]))
        del sm
    out = {"n": n, "goal_themes_bound_by_the_organ": n_bound, "theme_source": theme_source,
           "answers_changed": changed, "model_status_marginal": dict(
               (v, marginal.count(v)) for v in sorted(set(marginal))),
           "population": "the authored OCC appraisal gold (n=50), read by the LIVE reader; only the goal "
                         "STATUS function differs between the arms"}
    for k in names:
        if not per_item[k]:
            continue
        out[("floor_incumbent_acc" if k == "floor" else k + "_acc")] = round(ok[k] / n, 4) if n else None
        out[k + "_abstains"] = abst[k]
    if per_item["model_with_compatibility"]:
        out["compatibility_minus_model"] = _paired_boot(per_item["model_with_compatibility"],
                                                        per_item["model"], cl_ := [str(i) for i in range(n)],
                                                        2000, SEED + 33)
        out["compatibility_minus_floor"] = _paired_boot(per_item["model_with_compatibility"],
                                                        per_item["floor"], cl_, 2000, SEED + 34)
    cl = [str(i) for i in range(n)]
    out["model_minus_floor"] = _paired_boot(per_item["model"], per_item["floor"], cl, 2000, SEED + 31)
    out["model_minus_twin"] = _paired_boot(per_item["model"], per_item["twin"], cl, 2000, SEED + 32)
    out["ci_sep_over_floor"] = bool(out["model_minus_floor"][1] is not None and out["model_minus_floor"][1] > 0)
    out["ci_sep_over_twin"] = bool(out["model_minus_twin"][1] is not None and out["model_minus_twin"][1] > 0)
    return out


# ===================================================================================================
# PHASE 4 -- THE QUALITY PUSH: the two levers the signal-loss trace named
# ===================================================================================================
def arm_lever_theme_source(GR, recs, seed=SEED, B=2000):
    """LEVER 2 -- the goal THEME from the ARGUMENT-STRUCTURE ORGAN (the same organ that binds every event's
    patient) instead of a head-final regex over the goal span. Coverage + agreement on real goals, and the
    B1 content-discrimination accuracy under each theme source (same items, same floor, same twin)."""
    n = organ = agree = disagree = organ_only = 0
    diffs = []
    for r in recs["records"]:
        for gr_ in r["goals"]:
            g_span = _mk_goals(GR, [gr_], "span")[0]
            span_theme = GR.goal_object(g_span)
            g_org = _mk_goals(GR, [gr_], "organ")[0]
            ot = getattr(g_org, "goal_object", None) if getattr(g_org, "object_source", None) == \
                "argument_structure_organ" else None
            n += 1
            if ot:
                organ += 1
                if span_theme is None:
                    organ_only += 1
                elif GR._lemma_noun(ot) == GR._lemma_noun(span_theme):
                    agree += 1
                else:
                    disagree += 1
                    if len(diffs) < 12:
                        diffs.append({"goal": gr_["goal_text"], "span": span_theme, "organ": ot})
    a_span = arm_content(GR, recs, seed=seed, B=B, theme_source="span")
    a_org = arm_content(GR, recs, seed=seed, B=B, theme_source="organ")
    return {"n_goals": n, "organ_bound_a_theme": organ, "organ_coverage": round(organ / n, 4) if n else None,
            "agree_with_span_head": agree, "disagree": disagree, "organ_only": organ_only,
            "disagreement_examples": diffs,
            "B1_span_theme_acc": a_span["model_acc"], "B1_organ_theme_acc": a_org["model_acc"],
            "B1_organ_minus_span": (round(a_org["model_acc"] - a_span["model_acc"], 4)
                                    if (a_org["model_acc"] is not None and a_span["model_acc"] is not None)
                                    else None),
            "B1_span_n_items": a_span["n_items"], "B1_organ_n_items": a_org["n_items"],
            "B1_span_full": a_span, "B1_organ_full": a_org,
            "note": "the organ theme is injected on the goal record exactly as the landed extractor sets it; "
                    "the span reading is the fallback rung. Both arms score the SAME construction."}


def arm_lever_precision(GR, recs):
    """LEVER 1 -- a CONFLICTING theme vetoes the closure only to the extent the reader trusts the arc it was
    read off (EventRecord.patient_conf, the precision the goal closure was throwing away). The A/B is run by
    ABLATING the signal (patient_conf -> None), not by changing the code."""
    out = {}
    for name, prec in (("with_precision", True), ("without_precision", False)):
        flips = defaultdict(int)
        stats = GR.ContentMatchAccrual()
        n_sat = n_act = n_low = 0
        for r in recs["records"]:
            goals = _mk_goals(GR, r["goals"], "organ")
            events = _mk_events(r["events"], precision=prec)
            if not goals:
                continue
            canon = _canon_fn(r["canon"])
            GR.track_status_thwart(goals, events, sents=[list(s) for s in r["sents"]], canon=canon, stats=stats)
            floors = floor_status(_mk_goals(GR, r["goals"], "organ"), events, GR._norm_pred)
            for g, fs in zip(goals, floors):
                n_sat += int(g.status == "satisfied")
                n_act += int(g.status == "active")
                n_low += int(g.status_evidence == "low_precision_theme_conflict")
                if g.status != fs:
                    flips["%s->%s" % (fs, g.status)] += 1
        out[name] = {"satisfied": n_sat, "active": n_act, "flips_vs_incumbent": dict(flips),
                     "closures_restored_by_precision": n_low, "accrual": stats.as_dict()}
    return out


def arm_candidate_decomposition(GR, recs):
    """THE ARITHMETIC CEILING ON THE CONTENT CHANNEL (the oracle-ceiling probe before any limit is written).
    Over EVERY (goal, candidate outcome) pair that passes predicate + agent + order -- i.e. every closure the
    INCUMBENT would make -- why was the theme decidable or not, and WHICH RUNG owns each residual bucket?"""
    buckets = defaultdict(int)
    owner = {"decided_entity_identity": "this organ (the theme is an entity in the reader files)",
             "decided_head_lemma": "this organ (the theme lemmas are comparable)",
             "goal_states_no_theme": "goal extraction (the construction states no object)",
             "outcome_theme_unobserved": "the who-did-what PATIENT rung (no patient bound on the outcome)",
             "pronoun_theme_unresolved": "the entity files / coref clustering (pri 131, pri 136)"}
    n_pairs = n_goals = 0
    for r in recs["records"]:
        goals = _mk_goals(GR, r["goals"])
        events = _mk_events(r["events"])
        canon = _canon_fn(r["canon"])

        def _agent(surface, si):
            c = canon(surface, si)
            return str(c).lower() if c else str(surface or "").lower()
        for g in goals:
            n_goals += 1
            if getattr(g, "negated", False):
                continue
            ah = GR._norm_pred(g.goal_head)
            ga = _agent(g.agent_canonical or g.agent or "", g.sent_idx)
            gobj = GR.goal_object(g)
            for e in events:
                pl = GR._norm_pred(getattr(e, "predicate", "") or "")
                ea = _agent(getattr(e, "agent", ""), e.sent_idx)
                if not pl or pl != ah:
                    continue
                if not (ea == ga or ga in ("?", "")):
                    continue
                if not GR.outcome_is_after(g, e.sent_idx, e.pred_idx):
                    continue
                n_pairs += 1
                th = GR.event_object(e)
                verdict, how = GR.content_verdict(gobj, th, canon, g.sent_idx, e.sent_idx)
                if verdict == GR.CONTENT_UNKNOWN:
                    key = {"goal_states_no_object": "goal_states_no_theme",
                           "outcome_theme_unobserved": "outcome_theme_unobserved",
                           "unresolved_pronoun_theme": "pronoun_theme_unresolved"}.get(how, how)
                else:
                    key = "decided_" + how
                buckets[key] += 1
    dec = buckets.get("decided_entity_identity", 0) + buckets.get("decided_head_lemma", 0)
    return {"n_goals": n_goals, "n_incumbent_closure_candidates": n_pairs,
            "buckets": dict(buckets),
            "decidable_share": round(dec / n_pairs, 4) if n_pairs else None,
            "rung_that_owns_each_residual": owner,
            "note": "the ceiling on the CONTENT constraint: a closure whose theme is unobservable can only be "
                    "graded, never adjudicated, so the residual buckets name the upstream rung to repair next"}


# ===================================================================================================
# PHASE 7 (B) -- CONDITION THE VETO ON THE COREFERENCE PICK'S OWN CONFIDENCE
# ===================================================================================================
# Today a theme-identity DIFFERENCE that rests on a pronoun never vetoes, because the antecedent is a graded
# competition this organ cannot re-run. pri 131 landed the competition itself on the record
# (`CorefResolution.candidates` = ((entity id, activation), ...) strongest first, plus `abstain_reason`), so
# the smallest read that could make the veto conditional is: let the difference veto WHEN THE PICK IS
# CONFIDENT. p_top = softmax over the candidate activations (the competition's own posterior), MAP threshold
# -- no tuned constant. This arm MEASURES that read before anything is shipped.
def _pick_confidence(sm):
    """{(pronoun_lower, sent_idx) -> (p_top, margin_nats, abstain_reason)} from the reader's OWN pick."""
    out = {}
    for r in getattr(sm, "coref_resolutions", []) or []:
        cands = list(getattr(r, "candidates", ()) or ())
        acts = [float(a) for (_e, a) in cands if a is not None]
        if not acts:
            continue
        m = max(acts)
        ex = [pow(2.718281828459045, a - m) for a in acts]
        p_top = ex[acts.index(m)] / sum(ex) if sum(ex) else None
        srt = sorted(acts, reverse=True)
        margin = (srt[0] - srt[1]) if len(srt) > 1 else float("inf")
        key = (str(r.pronoun).lower(), int(r.sent_idx))
        prev = out.get(key)
        if prev is None or (p_top or 0) > (prev[0] or 0):
            out[key] = (p_top, margin, getattr(r, "abstain_reason", None))
    return out


def arm_coref_confidence(GR, cap=None):
    """On the OCC gold (the population that carries the cost): every time the theme test reaches the
    ANAPHORIC-IDENTITY branch, what is the coreference pick's own confidence, and would letting a CONFIDENT
    pick veto have been right? Gold is the OCC type, so each flip is scoreable."""
    from experiments._occ_probe import load_gold, write_conll, _protagonist_canon
    from experiments._tom_chain import split_sents, tokenize
    from hdlab.situation_reader import SituationReader
    gold = load_gold()[:cap]
    reader = SituationReader(track_goals=True, track_affect=True)
    tmp = tempfile.mkdtemp(prefix="p135_cc_")
    firings, rows = 0, []
    n_conf = 0
    for it in gold:
        cp = write_conll(it["text"], it["char"], tmp, it["id"])
        sm = reader.read(cp)
        sents = [tokenize(s) for s in split_sents(it["text"])]
        _inject_organ_themes(GR, reader, sm, sents)
        canon = _protagonist_canon(sm, it["char"])
        conf = _pick_confidence(sm)
        goals = list(getattr(getattr(sm, "goal_register", None), "goals", []) or [])
        events = list(getattr(sm, "events", []) or [])
        ev = GR._ev_tuples(events, GR._norm_pred)
        for g in goals:
            gobj = GR.goal_object(g)
            ah = GR._norm_pred(g.goal_head)
            ga = str(g.agent_canonical or g.agent or "").lower()
            for row in ev:
                si, pos, pl, ea, th, pol = row[0], row[1], row[2], row[3], row[4], row[5]
                if not pl or pl != ah or not GR.outcome_is_after(g, si, pos):
                    continue
                verdict, how = GR.content_verdict(gobj, th, canon, g.sent_idx, si)
                if how != "anaphoric_theme_identity_unconfirmed":
                    continue
                firings += 1
                pron = th if th in GR.PRONOUNS else gobj
                p_top, margin, abst = conf.get((str(pron).lower(), int(si)), (None, None, None))
                if p_top is not None and p_top > 0.5:
                    n_conf += 1
                rows.append({"id": it["id"], "gold": it["type"], "goal": g.goal_text, "goal_theme": gobj,
                             "outcome_theme": th, "pronoun": pron, "p_top": (round(p_top, 4) if p_top else None),
                             "margin_nats": (round(margin, 4) if margin not in (None, float("inf")) else None),
                             "abstain_reason": abst,
                             "would_veto_if_confident": bool(p_top is not None and p_top > 0.5)})
        del sm
    return {"n_anaphoric_branch_firings": firings, "n_with_a_confident_pick": n_conf,
            "rows": rows,
            "note": "a firing is a closure the theme test can only ABSTAIN on today. If the pick's own "
                    "confidence licensed the veto, every row with would_veto_if_confident=True would be "
                    "BLOCKED instead of closed -- score those against the gold column."}


# ===================================================================================================
# THE AUDIT (checklist item 3): every identity/time-constrained query audited for silent broadening
# ===================================================================================================
AUDIT = [
    {"site": "hdlab/goal_register.py:why", "pattern": "filtered cands or all cands",
     "verdict": "FIXED at the pri 129 landing; fixture F1 keeps it, and the same-agent fallback is now "
                "LABELLED (why(..., with_provenance=True))"},
    {"site": "hdlab/goal_register.py:track_status / track_status_thwart", "pattern": "predicate+agent only",
     "verdict": "FIXED here: content + (sentence, position) + polarity, with the evidence recorded"},
    {"site": "hdlab/situation_reader.py:_read_prediction/_goal_lemmas", "pattern": "t ignored for goals",
     "verdict": "FIXED here: t threads through the agent population and every goal read"},
    {"site": "hdlab/situation_reader.py:_read_tom_action/_desired_value", "pattern": "untimed wants() while "
                                                                                    "accepting t for belief",
     "verdict": "FIXED here: the desire is read AS OF t"},
    {"site": "hdlab/situation_reader.py:sm.wants/why/achieved", "pattern": "no time parameter at all",
     "verdict": "FIXED here: every goal closure accepts t"},
    {"site": "hdlab/goal_hierarchy_graph.py:_apply_status:266", "pattern": "a SECOND copy of the "
                                                                          "predicate+agent+strictly-later rule",
     "verdict": "REPORTED, not fixed here: the graph re-derives satisfaction instead of calling the register's "
                "closure predicate. Measured in this cell (arm F) and handed to strategy as a one-call "
                "consolidation (hdlab/goal_hierarchy_graph.py is outside this brief's write list)"},
    {"site": "hdlab/coref.py:543 'legal = inside or cands'", "pattern": "filter-or-all",
     "verdict": "NOT the same defect class and NOT this solver's file (pri 136 holds it): it broadens a "
                "STRUCTURAL legality filter when it empties, it does not drop a constraint the question "
                "states. Reported for the record."},
    {"site": "hdlab/graded_role_assigner.py:176,195 / hdlab/relcl_resolver.py:152", "pattern": "filter-or-all",
     "verdict": "NOT an identity constraint (an NP-head type filter that falls back when it empties); "
                "graded_role_assigner is pri 134's file. Reported, not touched."},
]


# ===================================================================================================
# ARM F -- the second copy of the satisfaction rule (goal_hierarchy_graph)
# ===================================================================================================
def arm_graph_copy(GR, recs):
    """THE SECOND COPY OF THE RULE, measured the way the READER actually wires it (the first version of this
    arm handed `build_goal_graph` FRESH, UNTRACKED goals and then compared their default 'active' against the
    register -- an instrument error that reported 32 of 212 disagreements where the live wire has none).

    `_apply_status` PREFERS the flat register's status for every node whose key matches a goal head, so the
    GOAL nodes agree by construction (row 1 is the control on this instrument). The second copy is the
    ACTION-node branch: a bare action node -- the matrix action of a purpose construction -- gets
    `predicate + agent + strictly-later SENTENCE`, with no irregular-past normalisation, no within-sentence
    order and no polarity. Those nodes feed `open_superordinate` -> `sm.reinstated_goal`. Row 2 recomputes
    each action node through the register's own `closing_outcome` and counts what changes."""
    from hdlab.goal_hierarchy_graph import build_goal_graph
    import hdlab.goal_register as GRlive
    disagree = same = 0
    act_total = act_changed = act_sat = 0
    cons_total = cons_changed = 0
    act_by = defaultdict(int)
    examples, act_examples, cons_examples = [], [], []
    for r in recs["records"]:
        goals = _mk_goals(GR, r["goals"])
        events = _mk_events(r["events"])
        canon = _canon_fn(r["canon"])
        if not goals:
            continue
        sents = [list(x) for x in r["sents"]]
        GR.track_status_thwart(goals, events, sents=sents, canon=canon)
        # the reader hands the graph THE SAME TRACKED GOAL OBJECTS
        gg = build_goal_graph(goals, causal_links=None, events=events, link_open_stack=True, sents=sents)
        heads = set()
        for g in goals:
            key = "%s::%s" % ((g.agent_canonical or g.agent or "?").lower(), GRlive._lemma(g.goal_head))
            heads.add(key)
            nd = gg.nodes.get(key)
            if nd is None:
                continue
            if nd.status != g.status:
                disagree += 1
                if len(examples) < 8:
                    examples.append({"doc": r["id"], "goal": g.goal_text, "register": g.status,
                                     "graph": nd.status, "evidence": g.status_evidence})
            else:
                same += 1
        # ---- the consumer of those statuses, BEFORE the consolidation ----
        before = {ag: gg.open_superordinate(ag) for ag in gg.agents()}
        # ---- the ACTION nodes: the branch that really is a second copy ----
        ev = GR._ev_tuples(events, GR._norm_pred)
        for key, nd in gg.nodes.items():
            if key in heads:
                continue
            act_total += 1
            act_sat += int(nd.status == "satisfied")
            pseudo = GR.Goal(agent=nd.agent, goal_head=nd.head, goal_text=nd.text, kind="action",
                             source_verb=nd.head, sent_idx=nd.sent_idx, verb_tok=nd.verb_tok,
                             to_tok=nd.verb_tok)
            pseudo.agent_canonical = nd.agent
            hit = GR.closing_outcome(pseudo, nd.agent, GR._norm_pred(nd.head), ev, canon=canon)
            new = "satisfied" if hit is not None else "active"
            if new != nd.status:
                act_changed += 1
                act_by["%s->%s" % (nd.status, new)] += 1
                if len(act_examples) < 10:
                    act_examples.append({"doc": r["id"], "action": nd.text, "agent": nd.agent,
                                         "graph": nd.status, "consolidated": new,
                                         "evidence": (hit[2] if hit else None)})
            nd.status = new                      # apply the consolidation in place, then re-ask the consumer
        after = {ag: gg.open_superordinate(ag) for ag in gg.agents()}
        for ag in before:
            cons_total += 1
            if before[ag] != after.get(ag):
                cons_changed += 1
                if len(cons_examples) < 10:
                    cons_examples.append({"doc": r["id"], "agent": ag, "reinstated_before": before[ag],
                                          "reinstated_after": after.get(ag)})
    return {"n_goal_nodes_compared": same + disagree, "goal_nodes_agree": same,
            "goal_nodes_disagree": disagree,
            "goal_node_disagree_rate": round(disagree / (same + disagree), 4) if (same + disagree) else None,
            "n_action_nodes": act_total, "action_nodes_satisfied_by_the_graph": act_sat,
            "action_nodes_changed_by_consolidation": act_changed,
            "action_node_changes": dict(act_by), "action_examples": act_examples,
            "consumer_reinstated_goal_queries": cons_total,
            "consumer_reinstated_goal_changed": cons_changed,
            "consumer_examples": cons_examples,
            "goal_node_examples": examples,
            "note": "row 1 is the CONTROL (the graph copies the register's status for goal nodes, so it must "
                    "be 0); row 2 is the real second copy -- the action-node branch, which feeds "
                    "open_superordinate -> sm.reinstated_goal"}


# ===================================================================================================
# RUN
# ===================================================================================================
def run(n=400, boot=2000, seed=SEED, occ_cap=None, time_cap=None):
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    GR, SR, landed = load_impl(need_reader=True)
    res = {"anchor": ANCHOR, "landed": landed, "seed": seed, "n_passages_requested": n,
           "utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    res["A_fixtures"] = {"impl_under_test": fixtures(GR), "live_tree": fixtures_on_live()}
    res["A_fixtures"]["all_green_under_test"] = all(c["ok"] for c in res["A_fixtures"]["impl_under_test"])
    res["A_fixtures"]["live_tree_green"] = all(c["ok"] for c in res["A_fixtures"]["live_tree"])
    recs = read_corpus(n)
    res["corpus"] = {"n_passages": recs["n_passages"], "read_s": recs["elapsed_s"],
                     "n_goals": sum(len(r["goals"]) for r in recs["records"]),
                     "n_events": sum(len(r["events"]) for r in recs["records"])}
    print("[arm B] content discrimination ...", flush=True)
    res["B1_content_lexical"] = arm_content(GR, recs, seed=seed, B=boot, anaphoric=False)
    res["B2_content_anaphoric"] = arm_content(GR, recs, seed=seed, B=boot, anaphoric=True)
    print("[arm C] within-sentence order ...", flush=True)
    res["C_order"] = arm_order(GR, recs, seed=seed, B=boot)
    print("[arm D] prefix invariance ...", flush=True)
    res["D_time_prefix_invariance"] = arm_time(GR, SR, recs, cap=time_cap)
    print("[arm E] no-regress ...", flush=True)
    res["E_authored_goldens"] = arm_authored(GR, seed=seed)
    res["E_flip_census"] = arm_flip_census(GR, recs)
    res["E_occ_gold_downstream"] = arm_occ_gold(GR, cap=occ_cap)
    print("[arm F] the second copy of the rule ...", flush=True)
    res["F_graph_second_copy"] = arm_graph_copy(GR, recs)
    print("[arm G] the closure-candidate decomposition (the arithmetic ceiling) ...", flush=True)
    res["G_candidate_decomposition"] = arm_candidate_decomposition(GR, recs)
    res["audit_checklist_3"] = AUDIT
    res["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, default=str)
    _print(res)
    return res


def _print(r):
    print("\n=== exp_goal_constraints_v1 (landed=%s) ===" % r["landed"])
    f = r["A_fixtures"]
    print("A fixtures: under-test %d/%d green | live tree %d/%d green" % (
        sum(c["ok"] for c in f["impl_under_test"]), len(f["impl_under_test"]),
        sum(c["ok"] for c in f["live_tree"]), len(f["live_tree"])))
    for c in f["impl_under_test"]:
        if not c["ok"]:
            print("   FAIL(under test) %s: got %r want %r" % (c["name"], c["got"], c["want"]))
    for key in ("B1_content_lexical", "B2_content_anaphoric", "C_order"):
        a = r[key]
        print("%-22s n=%-5s model %-7s floor %-7s twin %-7s  m-f %s sep=%s  m-t %s sep=%s" % (
            key, a["n_items"], a["model_acc"], a["floor_incumbent_acc"],
            a.get("twin_permuted_theme_acc", a.get("twin_permuted_position_acc")),
            a["model_minus_floor"], a["ci_sep_over_floor"], a["model_minus_twin"], a["ci_sep_over_twin"]))
    d = r["D_time_prefix_invariance"]
    print("D prefix-invariance : trials=%s  model leaks %s (%s)  incumbent leaks %s (%s)" % (
        d["n_trials"], d["model_leaks"], d["model_leak_rate"], d["floor_incumbent_leaks"], d["floor_leak_rate"]))
    e = r["E_authored_goldens"]
    print("E W7 satisfaction   : model %s floor %s (bar>=0.9 %s)" % (
        e["authored_satisfaction_W7"]["model_acc"], e["authored_satisfaction_W7"]["floor_always_active_acc"],
        e["authored_satisfaction_W7"]["witness_bar_model_acc_ge_0.9"]))
    print("E W8 reinstatement  : model %s floor %s twin_p95 %s (bar %s)" % (
        e["authored_reinstatement_W8"]["model_reinstatement_acc"],
        e["authored_reinstatement_W8"]["floor_recency_acc"],
        e["authored_reinstatement_W8"]["twin_status_shuffle_p95"],
        e["authored_reinstatement_W8"]["witness_bar_model_ge_0.9_floor_le_0.1"]))
    c = r["E_flip_census"]
    print("E flip census       : goals=%s themed=%s theme-decided=%s flips=%s wants changed=%s (add %s / rm %s / swap %s)"
          % (c["n_goals"], c["n_goals_stating_a_theme"], c["n_closures_decided_on_an_observed_theme"],
             c["status_flips_vs_incumbent"], c["wants_answers_changed"], c["wants_added"], c["wants_removed"],
             c["wants_swapped"]))
    o = r["E_occ_gold_downstream"]
    print("E OCC gold (n=%s)   : model %s  incumbent %s  (answers changed %d)" % (
        o["n"], o["model_acc"], o["floor_incumbent_acc"], len(o["answers_changed"])))
    g = r["F_graph_second_copy"]
    print("F second copy       : goal nodes %s compared / %s disagree (control) | action nodes %s, %s satisfied by "
          "the graph, %s change under the register's closure %s | reinstated_goal answers %s of %s change"
          % (g["n_goal_nodes_compared"], g["goal_nodes_disagree"], g["n_action_nodes"],
             g["action_nodes_satisfied_by_the_graph"], g["action_nodes_changed_by_consolidation"],
             g["action_node_changes"], g["consumer_reinstated_goal_changed"],
             g["consumer_reinstated_goal_queries"]))
    d = r.get("G_candidate_decomposition") or {}
    print("G candidates        : %s incumbent closures, decidable share %s, buckets %s"
          % (d.get("n_incumbent_closure_candidates"), d.get("decidable_share"), d.get("buckets")))
    print("elapsed %.1fs -> %s" % (r["elapsed_s"], os.path.join(OUT_DIR, "metrics.json")))


def run_levers(n=200, boot=2000, seed=SEED, occ_cap=None, out="metrics_levers.json"):
    """PHASE 4 -- the quality push, measured the same way as the core arms."""
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    GR, landed = load_impl()
    recs = read_corpus(n)
    res = {"anchor": ANCHOR, "landed": landed, "seed": seed, "phase": "quality_push",
           "utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "corpus": {"n_passages": recs["n_passages"],
                      "n_goals": sum(len(r["goals"]) for r in recs["records"])}}
    print("[lever 2] theme source ...", flush=True)
    res["L2_theme_from_argument_structure_organ"] = arm_lever_theme_source(GR, recs, seed=seed, B=boot)
    print("[lever 1] precision-weighted content veto ...", flush=True)
    res["L1_precision_weighted_veto"] = arm_lever_precision(GR, recs)
    print("[downstream] OCC gold with both levers ...", flush=True)
    res["L_occ_gold_three_arms"] = arm_occ_gold(GR, cap=occ_cap, theme_source="organ")
    res["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT_DIR, out), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, default=str)
    L2 = res["L2_theme_from_argument_structure_organ"]
    print("\nL2 organ theme : coverage %s of %s goals | agree %s disagree %s organ-only %s | B1 span %s -> organ %s (%s)"
          % (L2["organ_bound_a_theme"], L2["n_goals"], L2["agree_with_span_head"], L2["disagree"],
             L2["organ_only"], L2["B1_span_theme_acc"], L2["B1_organ_theme_acc"], L2["B1_organ_minus_span"]))
    L1 = res["L1_precision_weighted_veto"]
    for k in ("with_precision", "without_precision"):
        print("L1 %-18s satisfied %s active %s flips %s restored %s" % (
            k, L1[k]["satisfied"], L1[k]["active"], L1[k]["flips_vs_incumbent"],
            L1[k]["closures_restored_by_precision"]))
    o = res["L_occ_gold_three_arms"]
    print("OCC gold n=%s : incumbent %s | model %s | model without precision %s (themes bound %s)"
          % (o["n"], o["floor_incumbent_acc"], o["model_acc"], o["model_no_precision_acc"],
             o["goal_themes_bound_by_the_organ"]))
    print("elapsed %.1fs -> %s" % (res["elapsed_s"], os.path.join(OUT_DIR, out)))
    return res


# ===================================================================================================
# PRE-LANDING VERIFIER -- run the goal organ's OWN downstream witnesses against the PROPOSED modules,
# injected under their real hdlab names, i.e. against exactly the tree shape strategy will land.
# ===================================================================================================
WITNESSES = ["verification/test_goal_register_constraints_are_binding.py",
             "verification/test_goal_register_landing_organ.py",
             "verification/test_occ_appraisal_landing.py",
             "verification/test_tom_chain_landing.py",
             "verification/test_goal_hierarchy_landing.py",
             "verification/test_forward_projection_landing.py"]

_BOOTSTRAP = """
import importlib.util, os, runpy, sys
PRE = os.environ["HDLAB_PRI135_PRELANDING"]
REPO = os.environ["HDLAB_PRI135_REPO"]
if REPO not in sys.path:
    sys.path.insert(0, REPO)


def _load(name, path, real):
    src = open(path, encoding="utf-8").read()
    spec = importlib.util.spec_from_loader(name, loader=None, origin=real)
    m = importlib.util.module_from_spec(spec)
    m.__file__ = real            # the module derives its asset paths from __file__: use the REAL hdlab path
    sys.modules[name] = m
    exec(compile(src, real, "exec"), m.__dict__)
    return m


import hdlab
hdlab.goal_register = _load("hdlab.goal_register", os.path.join(PRE, "goal_register_pri135.py"),
                            os.path.join(REPO, "hdlab", "goal_register.py"))
hdlab.situation_reader = _load("hdlab.situation_reader", os.path.join(PRE, "situation_reader_pri135.py"),
                               os.path.join(REPO, "hdlab", "situation_reader.py"))
print("[pri135] PROPOSED hdlab.goal_register + hdlab.situation_reader injected under their real names",
      flush=True)
runpy.run_path(sys.argv[1], run_name="__main__")
"""


def verify_landed(witnesses=None, timeout=1800):
    """Each witness in its OWN process, with the proposal injected as hdlab.goal_register /
    hdlab.situation_reader. When the proposal has landed the injection is a no-op (the files ARE hdlab), so
    this mode is meaningful both before and after landing."""
    import subprocess
    GR, SR, landed = load_impl(need_reader=True)
    pre = os.path.join(OUT_DIR, "_prelanding")
    boot = os.path.join(pre, "_inject_pri135.py")
    os.makedirs(pre, exist_ok=True)
    with open(boot, "w", encoding="utf-8", newline="\n") as f:
        f.write(_BOOTSTRAP)
    env = dict(os.environ)
    env.update({"HDLAB_PRI135_PRELANDING": pre, "HDLAB_PRI135_REPO": _REPO,
                "OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2", "MKL_NUM_THREADS": "2",
                "PYTHONHASHSEED": "0"})
    rows = []
    for w in (witnesses or WITNESSES):
        path = os.path.join(_REPO, w.replace("/", os.sep))
        if not os.path.exists(path):
            rows.append({"witness": w, "exit": None, "verdict": "MISSING"})
            continue
        t0 = time.time()
        if landed:
            cmd = [sys.executable, "-B", path]
        else:
            cmd = [sys.executable, "-B", boot, path]
        try:
            pr = subprocess.run(cmd, cwd=_REPO, env=env, capture_output=True, text=True, timeout=timeout)
            code, tail = pr.returncode, (pr.stdout + pr.stderr)[-1200:]
        except subprocess.TimeoutExpired:
            code, tail = None, "TIMEOUT after %ds" % timeout
        rows.append({"witness": w, "exit": code, "elapsed_s": round(time.time() - t0, 1),
                     "verdict": ("PASS" if code == 0 else ("TIMEOUT" if code is None else "FAIL")),
                     "tail": tail})
        print("  %-62s %-7s %5.1fs" % (w, rows[-1]["verdict"], rows[-1]["elapsed_s"]), flush=True)
    out = {"landed": landed, "injected": (not landed), "witnesses": rows,
           "all_pass": all(r["verdict"] == "PASS" for r in rows)}
    with open(os.path.join(OUT_DIR, "metrics_verify_landed.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str)
    print("verify-landed: %s" % ("ALL PASS" if out["all_pass"] else "FAILURES PRESENT"))
    for r in rows:
        if r["verdict"] != "PASS":
            print("--- %s ---\n%s" % (r["witness"], r.get("tail", "")))
    return out


def refresh_themes(n=400):
    """Recompute the cached per-goal ARGUMENT-STRUCTURE theme with the current implementation, by re-tagging
    and re-parsing ONLY the goal-bearing sentences through the reader's own organs. The alternative is a full
    corpus re-read; this keeps the A/B on exactly the same reads."""
    from hdlab.situation_reader import SituationReader
    GR, landed = load_impl()
    cache = os.path.join(OUT_DIR, "roc_records_v2_n%d.json" % n)
    with open(cache, encoding="utf-8") as f:
        blob = json.load(f)
    rdr = SituationReader(track_goals=True)
    t0 = time.time()
    changed = bound = total = 0
    for r in blob["records"]:
        sents = [list(x) for x in r["sents"]]
        for gr_ in r["goals"]:
            total += 1
            si, to = gr_["sent_idx"], gr_["to_tok"]
            th = None
            if 0 <= si < len(sents) and to is not None and to >= 0 and hasattr(GR, "organ_theme"):
                g = _mk_goals(GR, [gr_], "span")[0]
                try:
                    pos = rdr._cached_tag(list(sents[si]))
                    heads = rdr._cached_parse_heads(list(sents[si]), pos)
                    th = GR.organ_theme(list(sents[si]), list(pos), heads, to + 1, GR.goal_span_end(g))
                except Exception:
                    th = None
            bound += int(bool(th))
            if th != gr_.get("organ_theme"):
                changed += 1
            gr_["organ_theme"] = th
    with open(cache, "w", encoding="utf-8") as f:
        json.dump(blob, f)
    print("[refresh-themes] %d goals, %d bound by the organ, %d changed, %.1fs" % (
        total, bound, changed, time.time() - t0))
    return {"n_goals": total, "organ_bound": bound, "changed": changed}


def self_test():
    """Fast, no corpus: the fixtures under the implementation under test + the authored goldens."""
    GR, landed = load_impl()
    fx = fixtures(GR)
    bad = [c for c in fx if not c["ok"]]
    print("[self-test] landed=%s  fixtures %d/%d green" % (landed, len(fx) - len(bad), len(fx)))
    for c in bad:
        print("   FAIL %s: got %r want %r" % (c["name"], c["got"], c["want"]))
    a = arm_authored(GR, n_twin=20)
    print("[self-test] W7 satisfaction %s (floor %s) | W8 reinstatement %s (floor %s)" % (
        a["authored_satisfaction_W7"]["model_acc"], a["authored_satisfaction_W7"]["floor_always_active_acc"],
        a["authored_reinstatement_W8"]["model_reinstatement_acc"],
        a["authored_reinstatement_W8"]["floor_recency_acc"]))
    assert not bad, "fixtures must be green under the implementation under test"
    assert a["authored_satisfaction_W7"]["witness_bar_model_acc_ge_0.9"], a["authored_satisfaction_W7"]
    assert a["authored_reinstatement_W8"]["witness_bar_model_ge_0.9_floor_le_0.1"], a["authored_reinstatement_W8"]
    print("[self-test] PASS")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--levers", action="store_true")
    ap.add_argument("--verify-landed", action="store_true")
    ap.add_argument("--refresh-themes", action="store_true")
    ap.add_argument("--coref-conf", action="store_true")
    ap.add_argument("--witness", action="append", default=None)
    ap.add_argument("--out", default="metrics_levers.json")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--fixtures", action="store_true")
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--occ-cap", type=int, default=None)
    ap.add_argument("--time-cap", type=int, default=None)
    a = ap.parse_args()
    if a.fixtures:
        GR, landed = load_impl()
        for tag, rows in (("UNDER TEST", fixtures(GR)), ("LIVE TREE", fixtures_on_live())):
            print("--- %s (landed=%s) ---" % (tag, landed))
            for c in rows:
                print("  %-4s %-62s got=%r want=%r" % ("ok" if c["ok"] else "FAIL", c["name"], c["got"], c["want"]))
        return 0
    if a.self_test:
        self_test()
        return 0
    if a.coref_conf:
        GR, landed = load_impl()
        res = arm_coref_confidence(GR, cap=a.occ_cap)
        with open(os.path.join(OUT_DIR, "metrics_coref_confidence.json"), "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2, default=str)
        print("anaphoric-branch firings %s; with a CONFIDENT pick %s" % (
            res["n_anaphoric_branch_firings"], res["n_with_a_confident_pick"]))
        for r_ in res["rows"]:
            print("  %-7s gold=%-14s goal_theme=%-12r outcome=%-8r pron=%-6r p_top=%-6s margin=%-6s veto=%s"
                  % (r_["id"], r_["gold"], r_["goal_theme"], r_["outcome_theme"], r_["pronoun"],
                     r_["p_top"], r_["margin_nats"], r_["would_veto_if_confident"]))
        return 0
    if a.refresh_themes:
        refresh_themes(n=a.n)
        return 0
    if a.verify_landed:
        verify_landed(witnesses=a.witness)
        return 0
    if a.levers:
        run_levers(n=a.n, boot=a.boot, occ_cap=a.occ_cap, out=a.out)
        return 0
    if a.run:
        run(n=a.n, boot=a.boot, occ_cap=a.occ_cap, time_cap=a.time_cap)
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
