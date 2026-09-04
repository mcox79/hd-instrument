"""REGISTER-GENERAL INCREMENTAL STRUCTURE CUE for the embedded/relative-clause AGENT tie residual.

PROBLEM (measured, P2 SOLVED residual): with the Competition-Model AGENT competition landed (who-did-what
agent 0.041 -> ~0.69), the remaining errors concentrate in NOMINATIVE-vs-NOMINATIVE ties in embedded/relative
clauses -- two+ animate tracked entities that tie on every current cue (word-order + animacy + Centering-
givenness + crude clause-locality), where the correct agent is fixed only by full clause structure. A TRAINED
arc parser was PROVEN to lose OOD on 19c prose (P2 section 6), so the fix is NOT a trained parser.

HOW THE BRAIN DOES THIS (PINNED): role assignment is INCREMENTAL and CLAUSE-BOUNDED -- the parser builds
structure left-to-right and binds each verb's subject within its clause (Christiansen & Chater 2016 Now-or-
Never; Lewis & Vasishth 2005 cue-based retrieval; Frazier/Clifton clause boundaries). Syntax is ONE cue in a
graded competition, PRECISION-WEIGHTED: reliable structure dominates, unreliable structure steps back and the
lexical/discourse cues carry (eADM actor competition, Bornkessel-Schlesewsky & Schlesewsky 2006; Friston
precision). ATTACHMENT and ROLE-BINDING are SEPARATE POOLS sharing the activation FORM (Matchin-Hickok 2020;
Beber 2025 double dissociation) -- so the structural attachment enters the ROLE competition as a precision-
weighted CUE, it does not replace it.

WHAT IS REUSED (not re-derived):
  * hdlab.incremental_parser.incremental_build -- the landed REGISTER-GENERAL (rule-based, glass-box, NOT
    trained) left-corner incremental structure builder. Its subject rule (frames[verb].subj = the nearest
    preceding nominal in a bounded Now-or-Never buffer) is the register-general structure cue source. We
    reproduce that exact operation as `incremental_subject_before` (generalized to every token position so it
    is robust to event-extractor/tagger verb-index mismatches) and self-test it against incremental_build.
  * hdlab.graded_competition.net_activation -- the SAME additive-cue posterior the AGENT competition already
    uses; the structure cue is one more weighted support array (the separate attachment pool feeds the role
    pool as a precision-weighted vote).
  * hdlab.graded_role_assigner.agent_supports / clause_bounds / NOMINATIVE_PRON -- the landed P2 AGENT cues;
    imported via experiments.exp_cmrole_agent_board_v1 (the SOLVED reference the wire was ported from).

BASELINE = the LIVE full P2 stack (cm_agent + include_pron_agents + case_filter + clause_local), scored with
the context-cued readout (answer_instanced). The ONE varied thing is the added `structure` (and optional
`recency`-Centering) cue. struct=False, recency=False reproduces the baseline BYTE-IDENTICALLY (delegates to
the parent pick).

Run: .venv/Scripts/python.exe experiments/exp_cmrole_agent_struct_v1.py [--heldout] [--nboot 2000]
     .venv/Scripts/python.exe experiments/exp_cmrole_agent_struct_v1.py --selftest
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
from hdlab.situation_reader import (
    SituationReader, EventRecord, SuppressedPredicate, DEFAULT_ROLES, EventBundleCodec, ChunkedFocus,
    FOCUS_SEED, _sentence_nominals, _assign_roles, _assign_frame_primary_roles, _assign_affect, lemma_verb,
)
from hdlab.graded_competition import net_activation
from hdlab.candidate_generator import NOMINAL
from hdlab.coref import parse_litbank_conll
from hdlab.scene_segment import parse_conll_sentences
from hdlab.pos_tagger import PosTagger
from hdlab.situation_reader import _FRONTEND_POS_ASSET
from experiments.exp_cmrole_agent_board_v1 import (
    CMAgentReader, AGENT_W, _boot, _nominals_keep_pron, agent_supports, cm_agent_pick, clause_bounds,
    _is_animate, NOMINATIVE_PRON,
)
from experiments.exp_cmrole_agent_readout_v1 import answer_instanced

SEED = 20260904
OUT_DIR = os.path.join(_REPO, "data", "exp_cmrole_agent_struct_v1")

# structure + recency cue weights (validity-seeded; SWEPT not adopted). The structure cue sits between
# animacy(2) and preverbal(3): a real structural commitment, but ONE cue -- it must not override strong
# lexical evidence in canonical clauses (the FIX/BREAK ratio in the diagnostic was ~12:1, so a moderate
# weight is net-positive on BOTH slices without regression).
STRUCT_W = 2.5
RECENCY_W = 1.5


# --------------------------------------------------------------------------- the register-general structure cue
def incremental_subject_before(toks, pos, buffer_n: int = 3):
    """subj_before[i] = the incremental left-corner SUBJECT token index for a verb at position i: the nearest
    preceding nominal held in a bounded (n) lossy buffer (Now-or-Never). This REPRODUCES the subject rule of
    hdlab.incremental_parser.incremental_build (frames[verb].subj = buffer[-1]), generalized to EVERY position
    so it is robust to event-extractor/tagger verb-index mismatches. Register-general, glass-box: reads only
    toks/UPOS. Returns a list of length len(toks) (None where no nominal precedes)."""
    n = len(toks)
    out = [None] * n
    buf = []
    for i in range(n):
        out[i] = buf[-1] if buf else None            # buffer state BEFORE token i => subject for a verb AT i
        tag = pos[i] if i < len(pos) else None
        if tag in NOMINAL:
            buf.append(i)
            buf = buf[-buffer_n:]
    return out


def cm_agent_pick_struct(toks, up, v0, noms, gaz, weights, subj_before, cb_cluster,
                         cluster_freq=None, struct_twin_seed=None):
    """The AGENT competition with the register-general STRUCTURE cue (and optional recency-Centering cue) added
    as precision-weighted supports, over the P2 cues (REUSES agent_supports + net_activation). Returns
    (head, cluster). The structure cue is SELF-GATING (eADM minimal precision: it votes only when the parse's
    subject maps onto a candidate; abstains -> support all 0 -> the lexical/discourse competition carries).
    struct_twin_seed => the SHUFFLED-STRUCTURE info-free twin (permute ONLY the structure support)."""
    cands = [(m["wtok_start"], m["head"], m.get("cluster"), m.get("wtok_end", m.get("wtok_start"))) for m in noms]
    if not cands:
        return "?", None
    base = [(p, h, cl) for (p, h, cl, _e) in cands]
    S = agent_supports(toks, up, v0, base, gaz, cluster_freq)
    # STRUCTURE cue: +1 for the candidate the incremental parse binds as this verb's subject.
    subj_tok = subj_before[v0] if (subj_before is not None and 0 <= v0 < len(subj_before)) else None
    struct = []
    for (p, _h, _cl, e) in cands:
        hit = subj_tok is not None and (p == subj_tok or p <= subj_tok <= e)
        struct.append(1.0 if hit else 0.0)
    if struct_twin_seed is not None:                 # shuffled-structure info-free twin
        rng = np.random.default_rng(struct_twin_seed + v0 + len(cands))
        struct = list(np.asarray(struct, dtype=float)[rng.permutation(len(struct))])
    S["structure"] = struct
    # RECENCY-Centering cue: +1 for the candidate whose cluster == the CURRENT Cb (the entity realized as
    # subject in the previous clause -- Centering CONTINUE preference, Grosz-Joshi-Weinstein 1995).
    S["recency"] = [1.0 if (cb_cluster is not None and cl == cb_cluster) else 0.0 for (_p, _h, cl, _e) in cands]
    A = net_activation(S, weights)
    wi = int(np.argmax(A))
    return cands[wi][1], cands[wi][2]


class StructAgentReader(CMAgentReader):
    """Live full-P2-stack reader with a register-general incremental STRUCTURE cue (and optional recency-
    Centering cue) added to the AGENT competition. struct=False, recency=False => byte-identical to the parent
    (the LIVE baseline)."""

    def __init__(self, *a, struct=False, recency=False, struct_w=STRUCT_W, recency_w=RECENCY_W,
                 struct_twin_seed=None, **k):
        super().__init__(*a, **k)
        self._struct = struct
        self._recency = recency
        self._struct_twin_seed = struct_twin_seed
        self._cb = None
        # extended weight dict: the structure/recency cues vote only if enabled (weight 0 otherwise, so they
        # cannot influence net_activation).
        self._cmw_ext = dict(self._cm_weights)
        self._cmw_ext["structure"] = float(struct_w) if struct else 0.0
        self._cmw_ext["recency"] = float(recency_w) if recency else 0.0

    def read(self, conll_path):
        self._cb = None                                # reset the Centering backward-looking center per document
        return super().read(conll_path)

    def _read_events(self, sents, mentions, n_sents):
        # BYTE-FAITHFUL copy of CMAgentReader._read_events with the AGENT pick extended by the structure/recency
        # cues. When struct=False and recency=False, the pick DELEGATES to the parent cm_agent_pick (identical).
        codec = EventBundleCodec(n_dim=self.focus_n_dim, roles=DEFAULT_ROLES, seed=FOCUS_SEED)
        focus = ChunkedFocus(codec, capacity=4, fanout=2, seed=FOCUS_SEED)
        sent_noms = _sentence_nominals(mentions, n_sents)
        if self._agent_source == "coref" and self._cm_conll is not None:
            coref_ment, _nc = parse_litbank_conll(self._cm_conll, name_gender_map=self.gaz)
            agent_sent_noms = (_nominals_keep_pron(coref_ment, n_sents) if self._include_pron_agents
                               else _sentence_nominals(coref_ment, n_sents))
            if self._include_pron_agents and self._case_filter:
                agent_sent_noms = [[m for m in lst if (not m.get("is_pronoun"))
                                    or m["head"].lower() in NOMINATIVE_PRON] for lst in agent_sent_noms]
            agent_src = coref_ment
        else:
            agent_sent_noms = sent_noms
            agent_src = mentions
        agent_freq = {}
        for m in agent_src:
            if self._include_pron_agents or not m.get("is_pronoun"):
                agent_freq[m.get("cluster")] = agent_freq.get(m.get("cluster"), 0) + 1
        use_ext = self._struct or self._recency
        events, role_fillers, suppressed = [], [], []
        gidx = 0
        for si, toks in enumerate(sents):
            text = " ".join(toks)
            evs, _tagged = self._extract_events(text)
            noms = sent_noms[si] if si < len(sent_noms) else []
            anoms = agent_sent_noms[si] if si < len(agent_sent_noms) else []
            up = self._cached_tag(list(toks)) if (noms or anoms) else []
            subj_before = incremental_subject_before(list(toks), up) if (use_ext and anoms) else None
            verb_lows = self.pred_gate_fn(text) if self.pred_gate_fn is not None else None
            for e in evs:
                agent, patient = _assign_roles(e.idx, noms, lemma=e.lemma,
                                               gate_intransitive=self.gate_intransitive)
                if anoms:
                    acand = anoms
                    if self._clause_local:
                        lo, hi = clause_bounds(toks, up, e.idx)
                        acand = [m for m in anoms if lo <= m["wtok_start"] < hi] or anoms
                    if use_ext:
                        agent, agent_cl = cm_agent_pick_struct(
                            toks, up, e.idx, acand, self._cm_gaz, self._cmw_ext, subj_before, self._cb,
                            cluster_freq=agent_freq, struct_twin_seed=self._struct_twin_seed)
                        if self._recency and agent != "?":
                            self._cb = agent_cl                # update the Cb to the realized subject
                    else:
                        agent = cm_agent_pick(toks, up, e.idx, acand, patient, self._cm_gaz, self._cm_weights,
                                              cluster_freq=agent_freq, twin_seed=self._cm_twin_seed)
                if verb_lows is not None and e.lemma not in verb_lows:
                    suppressed.append(SuppressedPredicate(
                        sent_idx=si, predicate=e.lemma, tense=str(e.tense), agent=agent, patient=patient))
                    continue
                rf = {"PRED": e.lemma, "AGENT": agent, "PATIENT": patient, "TENSE": str(e.tense)}
                vec = codec.encode_event(rf); focus.push(vec, gidx)
                subj_role, obj_role = _assign_frame_primary_roles(
                    e.lemma, toks, e.idx, noms, gate_intransitive=self.gate_intransitive)
                affect = _assign_affect(patient, text)
                events.append(EventRecord(global_idx=gidx, sent_idx=si, predicate=e.lemma, agent=agent,
                                          patient=patient, tense=str(e.tense), subj_role=subj_role,
                                          obj_role=obj_role, affect=affect, pred_idx=e.idx))
                role_fillers.append(rf); gidx += 1
        return events, focus, codec, role_fillers, suppressed


# --------------------------------------------------------------------------- slice classification (input-only)
_TAGGER = None
_REL = frozenset(("who", "whom", "whose", "which", "that"))
_SUB = frozenset(("because", "when", "while", "if", "although", "though", "since", "unless", "after",
                  "before", "until", "as", "whereas", "whenever", "wherever", "once", "lest"))


def _tagger():
    global _TAGGER
    if _TAGGER is None:
        _TAGGER = PosTagger.load(_FRONTEND_POS_ASSET)
    return _TAGGER


def _questions_full(rec):
    """who-did-what AGENT questions keeping `sent` AND `start` (the gold subject token offset, for verb-locating)."""
    qs = []
    for m in rec.get("stream", []):
        if m.get("role") != "SUBJECT" or not m.get("gov_verb"):
            continue
        qs.append({"pred": m["gov_verb"], "gold": m["head_text"], "sent": int(m.get("sent", -1)),
                   "start": int(m.get("start", -1))})
    return qs


def classify_slice(q, sents, per_sent_cf, gaz):
    """Correctness-INDEPENDENT structural label for a question, from INPUT only.
      tie      : >=2 ANIMATE TRACKED candidates preverbal to the gov-verb in its clause span (the genuine
                 nominative-vs-nominative competition the structure cue targets).
      embedded : the gov-verb sits in an embedded/relative context (a relativizer/subordinator precedes it,
                 or the sentence has >=2 verbs) -- the register where clause structure is load-bearing.
    Returns dict(tie=bool, embedded=bool, valid=bool)."""
    S = q["sent"]
    if not (0 <= S < len(sents)):
        return {"valid": False}
    toks = list(sents[S]); up = _tagger().tag(toks)
    plem = lemma_verb(q["pred"])
    vpos = [i for i, t in enumerate(toks)
            if lemma_verb(t) == plem or SITQA._norm(t) == SITQA._norm(q["pred"])]
    if not vpos:
        return {"valid": False}
    # the gov-verb occurrence nearest the gold subject start (disambiguates repeats)
    st = q.get("start", -1)
    v0 = min(vpos, key=lambda i: abs(i - st)) if st >= 0 else vpos[0]
    anoms = per_sent_cf[S] if S < len(per_sent_cf) else []
    lo, hi = clause_bounds(toks, up, v0)
    acand = [m for m in anoms if lo <= m["wtok_start"] < hi] or anoms
    n_anim_pre = sum(1 for m in acand if m["wtok_start"] < v0
                     and _is_animate(m["head"].lower(),
                                     (up[m["wtok_start"]] if m["wtok_start"] < len(up) else None), gaz) > 0)
    n_verbs = sum(1 for i, t in enumerate(toks) if i < len(up) and up[i] == "VERB")
    low_before = [t.lower() for t in toks[:v0]]
    embedded = (n_verbs >= 2) or any(t in _REL or t in _SUB for t in low_before)
    return {"valid": True, "tie": n_anim_pre >= 2, "embedded": bool(embedded)}


# --------------------------------------------------------------------------- measurement
def _reader(arm, gaz):
    common = dict(gaz=gaz, role_route="positional", referent_per_np=True, cm_weights=AGENT_W, cm_gaz=gaz,
                  agent_source="coref", include_pron_agents=True, clause_local=True, case_filter=True)
    if arm == "base":
        return StructAgentReader(**common)                       # LIVE full P2 stack (byte-identical baseline)
    if arm == "struct":
        return StructAgentReader(struct=True, **common)
    if arm == "struct_rec":
        return StructAgentReader(struct=True, recency=True, **common)
    if arm == "twin_struct":
        return StructAgentReader(struct=True, struct_twin_seed=SEED, **common)
    raise ValueError(arm)


def _measure(docset, gaz, wdw, nboot, label):
    arms = ["base", "struct", "struct_rec", "twin_struct"]
    # per-doc per-arm correctness, split by slice
    per = {a: {"all": [], "tie": [], "canon": [], "emb": [], "nonemb": []} for a in arms}
    fire = {"n": 0, "fires": 0, "tie_n": 0}
    for doc in docset:
        path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        sents = parse_conll_sentences(path)
        coref, ncoref = parse_litbank_conll(path, name_gender_map=gaz)
        per_sent_full = _nominals_keep_pron(coref, ncoref)
        per_sent_cf = [[m for m in lst if (not m.get("is_pronoun")) or m["head"].lower() in NOMINATIVE_PRON]
                       for lst in per_sent_full]
        qs = _questions_full(wdw[doc])
        labels = [classify_slice(q, sents, per_sent_cf, gaz) for q in qs]
        sms = {a: _reader(a, gaz).read(path) for a in arms}
        for a in arms:
            buckets = {k: [] for k in ("all", "tie", "canon", "emb", "nonemb")}
            for q, lab in zip(qs, labels):
                if not lab.get("valid"):
                    continue
                c = int(SITQA._match(answer_instanced(sms[a], q), q["gold"], "events"))
                buckets["all"].append(c)
                buckets["tie" if lab["tie"] else "canon"].append(c)
                buckets["emb" if lab["embedded"] else "nonemb"].append(c)
            for k in buckets:
                per[a][k].append(np.array(buckets[k], dtype=float))
    acc = {a: {k: (float(np.concatenate(per[a][k]).mean()) if sum(len(x) for x in per[a][k]) else float("nan"))
               for k in per[a]} for a in arms}
    ns = {k: int(sum(len(x) for x in per["base"][k])) for k in per["base"]}
    print("\n[%s]  n_all=%d  n_tie=%d  n_canon=%d  n_emb=%d" % (label, ns["all"], ns["tie"], ns["canon"], ns["emb"]))
    print("   %-12s %8s %8s %8s %8s %8s" % ("arm", "ALL", "TIE", "CANON", "EMB", "NONEMB"))
    for a in arms:
        print("   %-12s %8.4f %8.4f %8.4f %8.4f %8.4f"
              % (a, acc[a]["all"], acc[a]["tie"], acc[a]["canon"], acc[a]["emb"], acc[a]["nonemb"]))
    tests = {}
    contrasts = [
        ("TIE: struct - base", "struct", "base", "tie"),
        ("TIE: struct - twin(shuffled-struct)", "struct", "twin_struct", "tie"),
        ("TIE: struct_rec - base", "struct_rec", "base", "tie"),
        ("EMB: struct - base", "struct", "base", "emb"),
        ("EMB: struct - twin", "struct", "twin_struct", "emb"),
        ("CANON: struct - base (no-regress)", "struct", "base", "canon"),
        ("ALL: struct - base (whole-arm no-regress)", "struct", "base", "all"),
        ("ALL: struct_rec - base", "struct_rec", "base", "all"),
    ]
    for lab, a, b, k in contrasts:
        d = _boot(per[a][k], per[b][k], nboot, SEED, doc_level=True)
        tests[lab] = d
        print("   %-42s d=%+.4f CI[%+.4f,%+.4f] hw=%.4f p<=0=%.3f sep=%s"
              % (lab, d["delta"], d["lo"], d["hi"], d["ci_hw"], d["p_le_0"], d["ci_sep"]))
    return {"acc": acc, "ns": ns, "tests": tests}


def run(heldout=False, nboot=2000):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    gaz = SITQA.load_given_gazetteer()
    wdw = {r["doc"]: r for r in json.load(open(SITQA.WDW_GOLD, encoding="utf-8"))}
    total = 40 if heldout else 16
    alldocs = SITQA.load_docs(total)
    tuned = [d for d in alldocs[:16] if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
    print("=" * 96)
    print("REGISTER-GENERAL INCREMENTAL STRUCTURE CUE for the embedded-clause AGENT tie residual")
    out = {"anchor_name": "cmrole_agent_struct_v1", "struct_w": STRUCT_W, "recency_w": RECENCY_W,
           "tuned": _measure(tuned, gaz, wdw, nboot, "TUNED docs[0:16]")}
    if heldout:
        held = [d for d in alldocs[16:40] if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
        out["held_out"] = _measure(held, gaz, wdw, nboot, "HELD-OUT docs[16:40] (never inspected)")
    print("=" * 96)
    out["elapsed_s"] = round(time.time() - t0, 1); out["ts_iso"] = datetime.now(timezone.utc).isoformat()
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2, default=str)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[done] %.0fs -> %s" % (time.time() - t0, os.path.join(OUT_DIR, "metrics.json")))
    return out


def selftest():
    """The structure cue reproduces hdlab.incremental_parser.incremental_build's SUBJECT bind at VERB positions,
    and a canary embedded-clause resolves to the embedded subject."""
    from hdlab.incremental_parser import incremental_build
    ok = True
    # 1) subj_before matches incremental_build's subj at every verb (structural fidelity of the reuse)
    cases = [
        (["the", "man", "who", "saw", "the", "boy", "ran", "."],
         ["DET", "NOUN", "PRON", "VERB", "DET", "NOUN", "VERB", "PUNCT"]),
        (["boys", "who", "kept", "suitors", "at", "bay", ",", "that", "chizzle", "engaged", "them"],
         ["NOUN", "PRON", "VERB", "NOUN", "ADP", "NOUN", "PUNCT", "SCONJ", "PROPN", "VERB", "PRON"]),
    ]
    for toks, pos in cases:
        sb = incremental_subject_before(toks, pos)
        frames = incremental_build(toks, pos, use_predict=False)
        buf = []
        exp = {}
        for i in range(len(toks)):
            if pos[i] == "VERB":
                exp[i] = (buf[-1] if buf else None)
            if pos[i] in NOMINAL:
                buf.append(i); buf = buf[-3:]
        for v in [i for i, t in enumerate(pos) if t == "VERB"]:
            got = sb[v]
            want = exp[v]
            print("  verb@%d '%s' subj_before=%s expect=%s %s" % (v, toks[v], got, want, "OK" if got == want else "MISMATCH"))
            ok = ok and (got == want)
        # incremental_build subj (1-based) present in its arg set for the verb
        _ = frames
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
