"""NEXT-LEVER TEST (owner push): does a THEMATIC-FIT / SELECTIONAL cue add over the structure cue on the
embedded-clause AGENT tie slice? The named lever (distributional thematic fit) is a MEASURED 19c negative
(exp_19c_distributional/reestimation/composition_thematic_fit_prototype_v1: DIST/C19 vs VERB-SHUFFLED twin
+0.008 / +0.012, CI includes 0) AND the tie residual is 89% character-vs-character (proper names carry no
selectional signature). This cell CONFIRMS first-hand on OUR exact slice with the cheapest brain-foundational
selectional cue: lexical AGENT-CAPABILITY (animacy_lexicon `agent_capable` -- Dowty proto-agent volition/
sentience; McRae generalized event knowledge at the lexical grain). Arm = structure cue + agentivity cue vs
structure cue; info-free twin shuffles the agentivity support.

Run: .venv/Scripts/python.exe experiments/exp_cmrole_agent_thematic_v1.py [--nboot 2000]
"""
from __future__ import annotations
import argparse, json, os, sys, time
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
from hdlab.animacy_lexicon import lookup_animacy
from experiments.exp_cmrole_agent_board_v1 import (
    AGENT_W, _boot, _nominals_keep_pron, agent_supports, clause_bounds, NOMINATIVE_PRON, _ANIM_PRON)
from experiments.exp_cmrole_agent_readout_v1 import answer_instanced
from experiments.exp_cmrole_agent_struct_v1 import (
    StructAgentReader, incremental_subject_before, _questions_full, classify_slice, STRUCT_W)

SEED = 20260904
OUT_DIR = os.path.join(_REPO, "data", "exp_cmrole_agent_thematic_v1")
AGENTIV_W = 1.5


def _agent_capable(head, tag):
    """Lexical agentivity (Dowty proto-agent): +1 agent-capable, -1 not, 0 unknown. Pronouns (he/she/they...)
    are agent-capable participants; 'it' is not. Glass-box lexical lookup."""
    if head in _ANIM_PRON:
        return 1.0
    if head == "it":
        return -1.0
    a = lookup_animacy(head, tag)
    if a is not None:
        return 1.0 if a.get("agent_capable") else -1.0
    return 0.0


def _pick(toks, up, v0, acand, subj_before, gaz, cmw, agent_freq, agentivity, twin_seed=None):
    cands = [(m["wtok_start"], m["head"], m.get("cluster"), m.get("wtok_end", m.get("wtok_start"))) for m in acand]
    if not cands:
        return "?", None
    base = [(p, h, cl) for (p, h, cl, _e) in cands]
    S = agent_supports(toks, up, v0, base, gaz, agent_freq)
    subj_tok = subj_before[v0] if (subj_before is not None and 0 <= v0 < len(subj_before)) else None
    S["structure"] = [1.0 if (subj_tok is not None and (p == subj_tok or p <= subj_tok <= e)) else 0.0
                      for (p, _h, _cl, e) in cands]
    if agentivity:
        ag = [_agent_capable(h.lower(), up[p] if p < len(up) else None) for (p, h, _cl, _e) in cands]
        if twin_seed is not None:
            rng = np.random.default_rng(twin_seed + v0 + len(cands))
            ag = list(np.asarray(ag, float)[rng.permutation(len(ag))])
        S["agentivity"] = ag
    A = net_activation(S, cmw)
    wi = int(np.argmax(A))
    return cands[wi][1], cands[wi][2]


class ThematicReader(StructAgentReader):
    def __init__(self, *a, agentivity=False, agentiv_twin=None, **k):
        super().__init__(*a, struct=True, **k)
        self._agentivity = agentivity
        self._agentiv_twin = agentiv_twin

    def _read_events(self, sents, mentions, n_sents):
        from hdlab.situation_reader import (EventBundleCodec, ChunkedFocus, DEFAULT_ROLES, FOCUS_SEED,
                                            _sentence_nominals, _assign_roles, _assign_frame_primary_roles,
                                            _assign_affect, SuppressedPredicate, EventRecord)
        codec = EventBundleCodec(n_dim=self.focus_n_dim, roles=DEFAULT_ROLES, seed=FOCUS_SEED)
        focus = ChunkedFocus(codec, capacity=4, fanout=2, seed=FOCUS_SEED)
        sent_noms = _sentence_nominals(mentions, n_sents)
        coref_ment, _nc = parse_litbank_conll(self._cm_conll, name_gender_map=self.gaz)
        asn = _nominals_keep_pron(coref_ment, n_sents)
        asn = [[m for m in lst if (not m.get("is_pronoun")) or m["head"].lower() in NOMINATIVE_PRON] for lst in asn]
        agent_freq = {}
        for m in coref_ment:
            agent_freq[m.get("cluster")] = agent_freq.get(m.get("cluster"), 0) + 1
        cmw = dict(self._cm_weights); cmw["structure"] = STRUCT_W
        if self._agentivity:
            cmw["agentivity"] = AGENTIV_W
        events, role_fillers, suppressed, gidx = [], [], [], 0
        for si, toks in enumerate(sents):
            text = " ".join(toks)
            evs, _t = self._extract_events(text)
            noms = sent_noms[si] if si < len(sent_noms) else []
            anoms = asn[si] if si < len(asn) else []
            up = self._cached_tag(list(toks)) if (noms or anoms) else []
            subj_before = incremental_subject_before(list(toks), up) if anoms else None
            verb_lows = self.pred_gate_fn(text) if self.pred_gate_fn is not None else None
            for e in evs:
                agent, patient = _assign_roles(e.idx, noms, lemma=e.lemma, gate_intransitive=self.gate_intransitive)
                if anoms:
                    lo, hi = clause_bounds(toks, up, e.idx)
                    acand = [m for m in anoms if lo <= m["wtok_start"] < hi] or anoms
                    agent, _cl = _pick(toks, up, e.idx, acand, subj_before, self._cm_gaz, cmw, agent_freq,
                                       self._agentivity, twin_seed=self._agentiv_twin)
                if verb_lows is not None and e.lemma not in verb_lows:
                    suppressed.append(SuppressedPredicate(sent_idx=si, predicate=e.lemma, tense=str(e.tense),
                                                          agent=agent, patient=patient))
                    continue
                rf = {"PRED": e.lemma, "AGENT": agent, "PATIENT": patient, "TENSE": str(e.tense)}
                vec = codec.encode_event(rf); focus.push(vec, gidx)
                sr, orl = _assign_frame_primary_roles(e.lemma, toks, e.idx, noms, gate_intransitive=self.gate_intransitive)
                events.append(EventRecord(global_idx=gidx, sent_idx=si, predicate=e.lemma, agent=agent,
                                          patient=patient, tense=str(e.tense), subj_role=sr, obj_role=orl,
                                          affect=_assign_affect(patient, text), pred_idx=e.idx))
                role_fillers.append(rf); gidx += 1
        return events, focus, codec, role_fillers, suppressed


def _reader(arm, gaz):
    common = dict(gaz=gaz, role_route="positional", referent_per_np=True, cm_weights=AGENT_W, cm_gaz=gaz,
                  agent_source="coref", include_pron_agents=True, clause_local=True, case_filter=True)
    if arm == "struct":
        return StructAgentReader(struct=True, **common)
    if arm == "struct_agentiv":
        return ThematicReader(agentivity=True, **common)
    if arm == "twin_agentiv":
        return ThematicReader(agentivity=True, agentiv_twin=SEED, **common)
    raise ValueError(arm)


def run(nboot=2000):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    gaz = SITQA.load_given_gazetteer()
    wdw = {r["doc"]: r for r in json.load(open(SITQA.WDW_GOLD, encoding="utf-8"))}
    docs = [d for d in SITQA.load_docs(16) if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
    arms = ["struct", "struct_agentiv", "twin_agentiv"]
    per = {a: {"tie": [], "all": []} for a in arms}
    for doc in docs:
        path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        sents = parse_conll_sentences(path)
        coref, ncoref = parse_litbank_conll(path, name_gender_map=gaz)
        psf = _nominals_keep_pron(coref, ncoref)
        pcf = [[m for m in lst if (not m.get("is_pronoun")) or m["head"].lower() in NOMINATIVE_PRON] for lst in psf]
        qs = _questions_full(wdw[doc]); labels = [classify_slice(q, sents, pcf, gaz) for q in qs]
        for a in arms:
            sm = _reader(a, gaz).read(path)
            b = {"tie": [], "all": []}
            for q, lab in zip(qs, labels):
                if not lab.get("valid"):
                    continue
                c = int(SITQA._match(answer_instanced(sm, q), q["gold"], "events"))
                b["all"].append(c)
                if lab["tie"]:
                    b["tie"].append(c)
            for k in b:
                per[a][k].append(np.array(b[k], float))
    acc = {a: {k: float(np.concatenate(per[a][k]).mean()) for k in per[a]} for a in arms}
    print("=" * 88)
    print("THEMATIC-FIT / AGENTIVITY next-lever test (tie slice)")
    for a in arms:
        print("   %-16s tie=%.4f all=%.4f" % (a, acc[a]["tie"], acc[a]["all"]))
    out = {"acc": acc, "tests": {}}
    for lab, a, b in [("agentiv - struct (does it add?)", "struct_agentiv", "struct"),
                      ("agentiv - twin (beats info-free?)", "struct_agentiv", "twin_agentiv")]:
        d = _boot(per[a]["tie"], per[b]["tie"], nboot, SEED, doc_level=True)
        out["tests"][lab] = d
        print("   %-36s tie d=%+.4f CI[%+.4f,%+.4f] sep=%s" % (lab, d["delta"], d["lo"], d["hi"], d["ci_sep"]))
    print("=" * 88)
    out.update({"elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()})
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2, default=str)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[done] %.0fs" % (time.time() - t0))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--nboot", type=int, default=2000)
    run(ap.parse_args().nboot)
