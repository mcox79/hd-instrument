"""OPTIMIZATION of the register-general structure cue: eADM GRADED PRECISION-WEIGHTING + weight robustness +
prominence-vs-recency Centering. Baseline = the flat self-gating structure cue (exp_cmrole_agent_struct_v1,
which already MET the bar: +0.073 on the tie slice, twin loses, no canonical regression).

BRAIN QUESTION (eADM / Friston precision): syntax is a cue whose WEIGHT is its RELIABILITY in the current
input. The left-corner bind is reliable for EMBEDDED-clause subjects (nearest preceding = the embedded subject)
but UNRELIABLE for a MATRIX verb after a relative clause (it grabs the RC-internal nominal -- the "man who saw
the boy RAN -> boy" pop failure). A precision-faithful cue DOWN-weights where the bind is unreliable. Two
glass-box precision signals tested:
  precdist : precision = 1/(1 + k*(dist-1))   -- down-weight a DISTANT left-corner bind (DLT locality; a bind
             many tokens back is a weaker Now-or-Never commitment).
  precrel  : precision = 0.3 when a relativizer/subordinator sits between the bound subject and the verb (the
             matrix-verb-after-RC risk), else 1.0.
Also: struct_prom = replace the FAILED recency-Centering (Cb = immediately-previous subject) with grammatical
PROMINENCE (candidate was realized as a subject at any prior point) -- salience_binder's MEASURED finding is
that on hard ambiguous cases RECENCY is at chance and grammatical PROMINENCE carries.

Run: .venv/Scripts/python.exe experiments/exp_cmrole_agent_struct_opt_v1.py [--heldout] [--nboot 1000]
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
from hdlab.coref import parse_litbank_conll
from hdlab.scene_segment import parse_conll_sentences
from experiments.exp_cmrole_agent_board_v1 import (
    AGENT_W, _boot, _nominals_keep_pron, agent_supports, clause_bounds, NOMINATIVE_PRON,
)
from experiments.exp_cmrole_agent_readout_v1 import answer_instanced
from experiments.exp_cmrole_agent_struct_v1 import (
    StructAgentReader, incremental_subject_before, _questions_full, classify_slice, _REL, _SUB, STRUCT_W,
)

SEED = 20260904
OUT_DIR = os.path.join(_REPO, "data", "exp_cmrole_agent_struct_opt_v1")


def _precision(toks, up, subj_tok, v0, mode):
    """Per-event eADM precision in [0,1] scaling the structure cue weight. subj_tok None => 0 (self-gate)."""
    if subj_tok is None:
        return 0.0
    if mode == "flat":
        return 1.0
    if mode == "precdist":
        dist = abs(v0 - subj_tok)
        return 1.0 / (1.0 + 0.5 * max(0, dist - 1))
    if mode == "precrel":
        a, b = (subj_tok + 1, v0) if subj_tok < v0 else (v0 + 1, subj_tok)
        between = [t.lower() for t in toks[a:b]]
        return 0.3 if any(t in _REL or t in _SUB for t in between) else 1.0
    return 1.0


class StructOptReader(StructAgentReader):
    """Structure cue with graded per-event PRECISION weighting and/or PROMINENCE-Centering."""

    def __init__(self, *a, prec_mode="flat", prom=False, prom_w=1.5, **k):
        super().__init__(*a, struct=True, **k)
        self._prec_mode = prec_mode
        self._prom = prom
        self._prom_w = float(prom_w)
        self._subj_clusters = set()          # grammatical PROMINENCE: clusters ever realized as a subject

    def read(self, conll_path):
        self._subj_clusters = set()
        return super().read(conll_path)

    def _pick(self, toks, up, v0, acand, subj_before, agent_freq):
        cands = [(m["wtok_start"], m["head"], m.get("cluster"), m.get("wtok_end", m.get("wtok_start"))) for m in acand]
        if not cands:
            return "?", None
        base = [(p, h, cl) for (p, h, cl, _e) in cands]
        S = agent_supports(toks, up, v0, base, self._cm_gaz, agent_freq)
        subj_tok = subj_before[v0] if (subj_before is not None and 0 <= v0 < len(subj_before)) else None
        struct = []
        for (p, _h, _cl, e) in cands:
            hit = subj_tok is not None and (p == subj_tok or p <= subj_tok <= e)
            struct.append(1.0 if hit else 0.0)
        S["structure"] = struct
        if self._prom:
            S["prominence"] = [1.0 if cl in self._subj_clusters else 0.0 for (_p, _h, cl, _e) in cands]
        prec = _precision(toks, up, subj_tok, v0, self._prec_mode)
        w = dict(self._cm_weights)
        w["structure"] = STRUCT_W * prec
        if self._prom:
            w["prominence"] = self._prom_w
        A = net_activation(S, w)
        wi = int(np.argmax(A))
        return cands[wi][1], cands[wi][2]

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
        events, role_fillers, suppressed = [], [], []
        gidx = 0
        for si, toks in enumerate(sents):
            text = " ".join(toks)
            evs, _t = self._extract_events(text)
            noms = sent_noms[si] if si < len(sent_noms) else []
            anoms = agent_sent_noms[si] if si < len(agent_sent_noms) else []
            up = self._cached_tag(list(toks)) if (noms or anoms) else []
            subj_before = incremental_subject_before(list(toks), up) if anoms else None
            verb_lows = self.pred_gate_fn(text) if self.pred_gate_fn is not None else None
            for e in evs:
                agent, patient = _assign_roles(e.idx, noms, lemma=e.lemma, gate_intransitive=self.gate_intransitive)
                if anoms:
                    lo, hi = clause_bounds(toks, up, e.idx)
                    acand = [m for m in anoms if lo <= m["wtok_start"] < hi] or anoms
                    agent, agent_cl = self._pick(toks, up, e.idx, acand, subj_before, agent_freq)
                    if agent != "?" and agent_cl is not None:
                        self._subj_clusters.add(agent_cl)          # accrue grammatical prominence
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
    if arm == "struct_w1.5":
        return StructAgentReader(struct=True, struct_w=1.5, **common)
    if arm == "struct_w4.0":
        return StructAgentReader(struct=True, struct_w=4.0, **common)
    if arm == "prec_dist":
        return StructOptReader(prec_mode="precdist", **common)
    if arm == "prec_rel":
        return StructOptReader(prec_mode="precrel", **common)
    if arm == "prom":
        return StructOptReader(prec_mode="flat", prom=True, **common)
    raise ValueError(arm)


ARMS = ["base", "struct", "struct_w1.5", "struct_w4.0", "prec_dist", "prec_rel", "prom"]


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
    print("   %-14s %8s %8s %8s" % ("arm", "TIE", "CANON", "ALL"))
    for a in ARMS:
        print("   %-14s %8.4f %8.4f %8.4f" % (a, acc[a]["tie"], acc[a]["canon"], acc[a]["all"]))
    tests = {}
    for a in ARMS:
        if a == "base":
            continue
        dt = _boot(per[a]["tie"], per["base"]["tie"], nboot, SEED, doc_level=True)
        da = _boot(per[a]["all"], per["base"]["all"], nboot, SEED, doc_level=True)
        tests[a] = {"tie": dt, "all": da}
        print("   %-14s TIE d=%+.4f CI[%+.4f,%+.4f] sep=%-5s | ALL d=%+.4f CI[%+.4f,%+.4f] sep=%s"
              % (a, dt["delta"], dt["lo"], dt["hi"], dt["ci_sep"], da["delta"], da["lo"], da["hi"], da["ci_sep"]))
    # is any precision/prominence variant BETTER than flat struct on the tie slice?
    print("   -- vs flat struct (does graded precision / prominence add?) --")
    for a in ("struct_w1.5", "struct_w4.0", "prec_dist", "prec_rel", "prom"):
        d = _boot(per[a]["tie"], per["struct"]["tie"], nboot, SEED, doc_level=True)
        tests.setdefault(a, {})["vs_struct_tie"] = d
        print("   %-14s TIE(vs struct) d=%+.4f CI[%+.4f,%+.4f] sep=%s" % (a, d["delta"], d["lo"], d["hi"], d["ci_sep"]))
    return {"acc": acc, "tests": tests}


def run(heldout=False, nboot=1000):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    gaz = SITQA.load_given_gazetteer()
    wdw = {r["doc"]: r for r in json.load(open(SITQA.WDW_GOLD, encoding="utf-8"))}
    total = 40 if heldout else 16
    alldocs = SITQA.load_docs(total)
    tuned = [d for d in alldocs[:16] if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
    print("=" * 96)
    print("STRUCTURE-CUE OPTIMIZATION: eADM graded precision + weight robustness + prominence Centering")
    out = {"anchor_name": "cmrole_agent_struct_opt_v1", "tuned": _measure(tuned, gaz, wdw, nboot, "TUNED docs[0:16]")}
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


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--heldout", action="store_true")
    ap.add_argument("--nboot", type=int, default=1000)
    args = ap.parse_args()
    run(args.heldout, args.nboot)
