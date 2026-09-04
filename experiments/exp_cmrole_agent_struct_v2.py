"""MORE BRAIN-FAITHFUL structure cue + UPSTREAM components (owner ask: prototype a more brain-faithful
component AND upstream components, show it exceeds).

The flat structure cue (exp_cmrole_agent_struct_v1) MET the bar (+0.073 tuned / +0.056 held-out on the tie
slice, twin loses, no canonical regression). Its #1 residual is the MATRIX-verb-after-relative-clause POP
failure: pure left-corner binds the RC-internal nominal ("the man who saw the boy RAN" -> boy), because it
lacks REVISION. Two upgrades, each a pinned brain mechanism, measured against flat struct:

  (A) MORE BRAIN-FAITHFUL PARSE -- RC-POP / reanalysis (rcpop). The brain builds structure incrementally and
      REANALYZES at clause boundaries (Frazier-Clifton; active-filler, Frazier 1987; garden-path recovery).
      A stack-based left-corner: a relativizer SAVES the matrix buffer (antecedent = the noun before it) and
      opens an RC-local buffer; at the RC's end (its verb consumed, or a comma) the matrix buffer is RESTORED
      so the MATRIX verb re-attaches the ANTECEDENT, not the RC-internal nominal. This is the pop the flat
      left-corner lacks. (The specialised filler-gap circuit -- the adjacent SOLVED relcl organ -- is the
      full version; this is the reader-side reuse of that operation as the structure cue.)

  (B) UPSTREAM animacy-lexicon coverage (animacy_fix). The animacy CUE mislabels COLLECTIVE-HUMAN nouns as
      inanimate (lookup_animacy: people/crowd->inanimate-abstract, everyone->None), flipping the cue AGAINST
      the true agent ("how many PEOPLE ... has stretched" -> people scored inanimate). A glass-box coverage
      patch restores their animacy. This is an UPSTREAM organ (hdlab.animacy_lexicon) fix, not this organ.

Baseline = the flat structure cue. Arms measured on the tie slice + canon + all, tuned + held-out, twin.

Run: .venv/Scripts/python.exe experiments/exp_cmrole_agent_struct_v2.py [--heldout] [--nboot 2000] [--selftest]
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_situation_model_qa_v1 as SITQA
from hdlab.graded_competition import net_activation
from hdlab.candidate_generator import NOMINAL
from hdlab.coref import parse_litbank_conll
from hdlab.scene_segment import parse_conll_sentences
from experiments.exp_cmrole_agent_board_v1 import (
    AGENT_W, _boot, _nominals_keep_pron, agent_supports, clause_bounds, NOMINATIVE_PRON, _is_animate,
)
from experiments.exp_cmrole_agent_readout_v1 import answer_instanced
from experiments.exp_cmrole_agent_struct_v1 import (
    StructAgentReader, incremental_subject_before, _questions_full, classify_slice, STRUCT_W, _REL,
)

SEED = 20260904
OUT_DIR = os.path.join(_REPO, "data", "exp_cmrole_agent_struct_v2")

_STRONG = frozenset((",", ";", ":", "--", "—", "(", ")"))
# COLLECTIVE-HUMAN nouns the animacy lexicon marks inanimate/abstract or misses (a coverage fix to the SAME
# animacy cue: a collective of persons is an animate, agent-capable participant in narrative prose).
COLLECTIVE_HUMAN = frozenset((
    "people", "peoples", "folk", "folks", "crowd", "crowds", "throng", "throngs", "multitude", "multitudes",
    "everyone", "everybody", "someone", "somebody", "anyone", "anybody", "others", "children", "gentry",
    "nobility", "mob", "mobs", "populace", "public", "crew", "crews", "humanity", "mankind", "womankind",
))


def _is_animate_fixed(head, tag, gaz) -> float:
    """_is_animate + a COLLECTIVE-HUMAN coverage patch (upstream animacy-lexicon fix)."""
    if head in COLLECTIVE_HUMAN:
        return 1.0
    return _is_animate(head, tag, gaz)


def incremental_subject_rcpop(toks, pos, buffer_n: int = 3):
    """Left-corner subject with RELATIVE-CLAUSE POP (reanalysis). subj[i] = the bound subject token for a verb
    at i, where a relativizer opens an RC (saving the matrix buffer, antecedent = the preceding nominal) and the
    RC closes at its verb-then-boundary so the MATRIX verb re-attaches the antecedent. Register-general, glass-
    box (reads only toks/UPOS + closed-class relativizers). Reduces to plain left-corner when no relativizer."""
    n = len(toks)
    out = [None] * n
    buf = []                      # current-level nominal buffer
    stack = []                    # saved matrix buffers (for the pop)
    in_rc = 0                     # nesting depth of open relative clauses
    rc_verb_seen = []            # per open RC: has its verb been consumed?
    low = [t.lower() for t in toks]
    for i in range(n):
        out[i] = buf[-1] if buf else None
        tag = pos[i] if i < len(pos) else None
        w = low[i]
        if w in _REL and buf:                       # enter an RC: save matrix context, seed with antecedent
            stack.append(list(buf))
            buf = [buf[-1]]                          # antecedent is the RC-local subject candidate (subj-relative)
            in_rc += 1
            rc_verb_seen.append(False)
            continue
        if tag == "VERB":
            if in_rc and not rc_verb_seen[-1]:
                rc_verb_seen[-1] = True              # this is the RC's own verb; stay in the RC to absorb its args
            elif in_rc and rc_verb_seen[-1]:         # a SECOND verb => the matrix verb: POP back to matrix
                buf = stack.pop(); in_rc -= 1; rc_verb_seen.pop()
                out[i] = buf[-1] if buf else None    # re-bind the matrix subject (the antecedent)
        elif w in _STRONG and in_rc and rc_verb_seen[-1]:
            buf = stack.pop(); in_rc -= 1; rc_verb_seen.pop()   # RC closes at a boundary after its verb
        if tag in NOMINAL:
            buf.append(i); buf = buf[-buffer_n:]
    return out


def _pick(toks, up, v0, acand, subj_before, cm_gaz, cmw, agent_freq, animacy_fix, struct_twin_seed=None):
    cands = [(m["wtok_start"], m["head"], m.get("cluster"), m.get("wtok_end", m.get("wtok_start"))) for m in acand]
    if not cands:
        return "?", None
    base = [(p, h, cl) for (p, h, cl, _e) in cands]
    S = agent_supports(toks, up, v0, base, cm_gaz, agent_freq)
    if animacy_fix:
        S["animacy"] = [_is_animate_fixed(h.lower(), up[p] if p < len(up) else None, cm_gaz)
                        for (p, h, _cl) in base]
    subj_tok = subj_before[v0] if (subj_before is not None and 0 <= v0 < len(subj_before)) else None
    struct = [1.0 if (subj_tok is not None and (p == subj_tok or p <= subj_tok <= e)) else 0.0
              for (p, _h, _cl, e) in cands]
    if struct_twin_seed is not None:
        rng = np.random.default_rng(struct_twin_seed + v0 + len(cands))
        struct = list(np.asarray(struct, float)[rng.permutation(len(struct))])
    S["structure"] = struct
    A = net_activation(S, cmw)
    wi = int(np.argmax(A))
    return cands[wi][1], cands[wi][2]


class StructV2Reader(StructAgentReader):
    """Structure cue with optional RC-POP parse and/or UPSTREAM animacy fix."""

    def __init__(self, *a, rcpop=False, animacy_fix=False, struct_twin_seed=None, **k):
        super().__init__(*a, struct=True, struct_twin_seed=struct_twin_seed, **k)
        self._rcpop = rcpop
        self._animacy_fix = animacy_fix

    def _read_events(self, sents, mentions, n_sents):
        from hdlab.situation_reader import (EventBundleCodec, ChunkedFocus, DEFAULT_ROLES, FOCUS_SEED,
                                            _sentence_nominals, _assign_roles, _assign_frame_primary_roles,
                                            _assign_affect, SuppressedPredicate, EventRecord)
        codec = EventBundleCodec(n_dim=self.focus_n_dim, roles=DEFAULT_ROLES, seed=FOCUS_SEED)
        focus = ChunkedFocus(codec, capacity=4, fanout=2, seed=FOCUS_SEED)
        sent_noms = _sentence_nominals(mentions, n_sents)
        coref_ment, _nc = parse_litbank_conll(self._cm_conll, name_gender_map=self.gaz)
        agent_sent_noms = _nominals_keep_pron(coref_ment, n_sents)
        agent_sent_noms = [[m for m in lst if (not m.get("is_pronoun")) or m["head"].lower() in NOMINATIVE_PRON]
                           for lst in agent_sent_noms]
        agent_freq = {}
        for m in coref_ment:
            agent_freq[m.get("cluster")] = agent_freq.get(m.get("cluster"), 0) + 1
        cmw = dict(self._cm_weights); cmw["structure"] = STRUCT_W
        events, role_fillers, suppressed = [], [], []
        gidx = 0
        for si, toks in enumerate(sents):
            text = " ".join(toks)
            evs, _t = self._extract_events(text)
            noms = sent_noms[si] if si < len(sent_noms) else []
            anoms = agent_sent_noms[si] if si < len(agent_sent_noms) else []
            up = self._cached_tag(list(toks)) if (noms or anoms) else []
            if anoms:
                subj_before = (incremental_subject_rcpop(list(toks), up) if self._rcpop
                               else incremental_subject_before(list(toks), up))
            else:
                subj_before = None
            verb_lows = self.pred_gate_fn(text) if self.pred_gate_fn is not None else None
            for e in evs:
                agent, patient = _assign_roles(e.idx, noms, lemma=e.lemma, gate_intransitive=self.gate_intransitive)
                if anoms:
                    lo, hi = clause_bounds(toks, up, e.idx)
                    acand = [m for m in anoms if lo <= m["wtok_start"] < hi] or anoms
                    agent, _cl = _pick(toks, up, e.idx, acand, subj_before, self._cm_gaz, cmw, agent_freq,
                                       self._animacy_fix, struct_twin_seed=self._struct_twin_seed)
                if verb_lows is not None and e.lemma not in verb_lows:
                    suppressed.append(SuppressedPredicate(sent_idx=si, predicate=e.lemma, tense=str(e.tense),
                                                          agent=agent, patient=patient))
                    continue
                rf = {"PRED": e.lemma, "AGENT": agent, "PATIENT": patient, "TENSE": str(e.tense)}
                vec = codec.encode_event(rf); focus.push(vec, gidx)
                subj_role, obj_role = _assign_frame_primary_roles(e.lemma, toks, e.idx, noms,
                                                                  gate_intransitive=self.gate_intransitive)
                affect = _assign_affect(patient, text)
                events.append(EventRecord(global_idx=gidx, sent_idx=si, predicate=e.lemma, agent=agent,
                                          patient=patient, tense=str(e.tense), subj_role=subj_role,
                                          obj_role=obj_role, affect=affect, pred_idx=e.idx))
                role_fillers.append(rf); gidx += 1
        return events, focus, codec, role_fillers, suppressed


def _reader(arm, gaz):
    common = dict(gaz=gaz, role_route="positional", referent_per_np=True, cm_weights=AGENT_W, cm_gaz=gaz,
                  agent_source="coref", include_pron_agents=True, clause_local=True, case_filter=True)
    if arm == "base":
        return StructAgentReader(**common)
    if arm == "struct":
        return StructAgentReader(struct=True, **common)
    if arm == "rcpop":
        return StructV2Reader(rcpop=True, **common)
    if arm == "animacy":
        return StructV2Reader(animacy_fix=True, **common)
    if arm == "rcpop_animacy":
        return StructV2Reader(rcpop=True, animacy_fix=True, **common)
    if arm == "twin_v2":
        return StructV2Reader(rcpop=True, animacy_fix=True, struct_twin_seed=SEED, **common)
    raise ValueError(arm)


ARMS = ["base", "struct", "rcpop", "animacy", "rcpop_animacy", "twin_v2"]


def _measure(docset, gaz, wdw, nboot, label):
    per = {a: {"tie": [], "canon": [], "all": []} for a in ARMS}
    for doc in docset:
        path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        sents = parse_conll_sentences(path)
        coref, ncoref = parse_litbank_conll(path, name_gender_map=gaz)
        per_sent_full = _nominals_keep_pron(coref, ncoref)
        per_sent_cf = [[m for m in lst if (not m.get("is_pronoun")) or m["head"].lower() in NOMINATIVE_PRON]
                       for lst in per_sent_full]
        qs = _questions_full(wdw[doc])
        labels = [classify_slice(q, sents, per_sent_cf, gaz) for q in qs]
        for a in ARMS:
            sm = _reader(a, gaz).read(path)
            b = {"tie": [], "canon": [], "all": []}
            for q, lab in zip(qs, labels):
                if not lab.get("valid"):
                    continue
                c = int(SITQA._match(answer_instanced(sm, q), q["gold"], "events"))
                b["all"].append(c); b["tie" if lab["tie"] else "canon"].append(c)
            for k in b:
                per[a][k].append(np.array(b[k], float))
    acc = {a: {k: float(np.concatenate(per[a][k]).mean()) for k in per[a]} for a in ARMS}
    print("\n[%s]" % label)
    print("   %-16s %8s %8s %8s" % ("arm", "TIE", "CANON", "ALL"))
    for a in ARMS:
        print("   %-16s %8.4f %8.4f %8.4f" % (a, acc[a]["tie"], acc[a]["canon"], acc[a]["all"]))
    tests = {}
    contrasts = [("rcpop - base (tie)", "rcpop", "base", "tie"),
                 ("animacy - base (tie)", "animacy", "base", "tie"),
                 ("rcpop_animacy - base (tie)", "rcpop_animacy", "base", "tie"),
                 ("rcpop_animacy - struct (does it EXCEED flat?)", "rcpop_animacy", "struct", "tie"),
                 ("rcpop_animacy - twin (info-free)", "rcpop_animacy", "twin_v2", "tie"),
                 ("rcpop_animacy - base (CANON no-regress)", "rcpop_animacy", "base", "canon"),
                 ("rcpop_animacy - base (ALL whole-arm)", "rcpop_animacy", "base", "all")]
    for lab, a, b, k in contrasts:
        d = _boot(per[a][k], per[b][k], nboot, SEED, doc_level=True)
        tests[lab] = d
        print("   %-46s d=%+.4f CI[%+.4f,%+.4f] sep=%s" % (lab, d["delta"], d["lo"], d["hi"], d["ci_sep"]))
    return {"acc": acc, "tests": tests}


def run(heldout=False, nboot=2000):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    gaz = SITQA.load_given_gazetteer()
    wdw = {r["doc"]: r for r in json.load(open(SITQA.WDW_GOLD, encoding="utf-8"))}
    total = 40 if heldout else 16
    alldocs = SITQA.load_docs(total)
    tuned = [d for d in alldocs[:16] if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
    print("=" * 96)
    print("MORE BRAIN-FAITHFUL structure cue (RC-POP) + UPSTREAM animacy fix")
    out = {"anchor_name": "cmrole_agent_struct_v2", "tuned": _measure(tuned, gaz, wdw, nboot, "TUNED docs[0:16]")}
    if heldout:
        held = [d for d in alldocs[16:40] if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
        out["held_out"] = _measure(held, gaz, wdw, nboot, "HELD-OUT docs[16:40]")
    print("=" * 96)
    out["elapsed_s"] = round(time.time() - t0, 1); out["ts_iso"] = datetime.now(timezone.utc).isoformat()
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2, default=str)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[done] %.0fs -> %s" % (time.time() - t0, os.path.join(OUT_DIR, "metrics.json")))
    return out


def selftest():
    ok = True
    cases = [
        ("the man who saw the boy ran .", "NOUN PRON VERB DET NOUN VERB PUNCT".replace("NOUN", "NOUN", 1)),
    ]
    # explicit canaries: rcpop should bind the MATRIX subject for the matrix verb
    canaries = [
        (["the", "man", "who", "saw", "the", "boy", "ran", "."],
         ["DET", "NOUN", "PRON", "VERB", "DET", "NOUN", "VERB", "PUNCT"], 6, 1),   # ran -> man(1)
        (["the", "man", "whom", "the", "boy", "saw", "ran", "."],
         ["DET", "NOUN", "PRON", "DET", "NOUN", "VERB", "VERB", "PUNCT"], 6, 1),   # ran -> man(1)
        (["boys", "who", "kept", "them", ",", "that", "chizzle", "engaged", "him"],
         ["NOUN", "PRON", "VERB", "PRON", "PUNCT", "SCONJ", "PROPN", "VERB", "PRON"], 7, 6),  # engaged -> chizzle(6)
    ]
    for toks, pos, vpos, want in canaries:
        sb = incremental_subject_rcpop(toks, pos)
        got = sb[vpos]
        print("  rcpop verb@%d '%s' -> subj tok %s ('%s') expect %s ('%s') %s"
              % (vpos, toks[vpos], got, toks[got] if got is not None else None, want, toks[want],
                 "OK" if got == want else "MISMATCH"))
        ok = ok and (got == want)
    # animacy fix
    print("  animacy_fix('people') =", _is_animate_fixed("people", "NOUN", None), "(expect 1.0)")
    ok = ok and _is_animate_fixed("people", "NOUN", None) == 1.0
    print("SELFTEST", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--heldout", action="store_true")
    ap.add_argument("--nboot", type=int, default=2000)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(0 if selftest() else 1)
    run(args.heldout, args.nboot)
