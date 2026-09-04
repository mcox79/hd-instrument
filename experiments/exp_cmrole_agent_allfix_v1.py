"""FIX-EVERY-LOSS composition (owner push): prototype the remaining untested levers and compose all
net-positive fixes over the structure cue, measured end-to-end on the board who-did-what AGENT arm.

Residual buckets (diag_residual / diag_readout_bucket) and the lever for each:
  detection@S (copula/light verb)  -> predicate_recall  (EXISTING organ, +0.0083 CI-sep whole-arm; done)
  animacy bug (people/crowd)       -> animacy_fix       (collective-human coverage; marginal; done)
  matrix-after-RC pop / matrix-vs-embedded -> GATED RC-POP: apply RC-pop reanalysis ONLY on UNAMBIGUOUS
     relativizers (who/whom/whose/which) -- NOT "that" (complementizer/demonstrative) which made the ungated
     RC-pop over-fire (-0.0126). The brain gates reanalysis; this is the gated version.
  possessive-of-gerund (his furnishing) -> GERUND-POSSESSIVE: keep a possessive pronoun as an agent candidate
     when it immediately governs a gerund (VBG) -- the gerund's subject (a case-filter exception).
  coref miss / character-vs-character -> NOT fixable in this organ (coref recall / genuine ambiguity); reported.

Arms compose the fixes cumulatively so each increment is visible.
Run: .venv/Scripts/python.exe experiments/exp_cmrole_agent_allfix_v1.py [--heldout] [--nboot 2000] [--selftest]
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
from experiments.exp_cmrole_agent_board_v1 import AGENT_W, _boot, _nominals_keep_pron, agent_supports, clause_bounds, NOMINATIVE_PRON
from experiments.exp_cmrole_agent_readout_v1 import answer_instanced
from experiments.exp_cmrole_agent_struct_v1 import StructAgentReader, _questions_full, classify_slice, STRUCT_W
from experiments.exp_cmrole_agent_struct_v2 import _is_animate_fixed

SEED = 20260904
OUT_DIR = os.path.join(_REPO, "data", "exp_cmrole_agent_allfix_v1")

_REL_STRICT = frozenset(("who", "whom", "whose", "which"))   # UNAMBIGUOUS relativizers (gated RC-pop; NO "that")
_STRONG = frozenset((",", ";", ":", "--", "—", "(", ")"))
_POSS_PRON = frozenset(("his", "her", "their", "its", "my", "your", "our", "whose"))


def incremental_subject_rcpop_gated(toks, pos, buffer_n=3):
    """RC-POP reanalysis GATED to unambiguous relativizers (who/whom/whose/which). "that" does NOT trigger a pop
    (it is a complementizer/demonstrative far more often than a relativizer in 19c prose -- the source of the
    ungated version's over-firing). Reduces to plain left-corner everywhere else."""
    n = len(toks)
    out = [None] * n
    buf, stack, in_rc, rc_verb = [], [], 0, []
    low = [t.lower() for t in toks]
    for i in range(n):
        out[i] = buf[-1] if buf else None
        tag = pos[i] if i < len(pos) else None
        w = low[i]
        if w in _REL_STRICT and buf:
            stack.append(list(buf)); buf = [buf[-1]]; in_rc += 1; rc_verb.append(False); continue
        if tag == "VERB":
            if in_rc and not rc_verb[-1]:
                rc_verb[-1] = True
            elif in_rc and rc_verb[-1]:
                buf = stack.pop(); in_rc -= 1; rc_verb.pop(); out[i] = buf[-1] if buf else None
        elif w in _STRONG and in_rc and rc_verb[-1]:
            buf = stack.pop(); in_rc -= 1; rc_verb.pop()
        if tag in NOMINAL:
            buf.append(i); buf = buf[-buffer_n:]
    return out


def incremental_subject_flat(toks, pos, buffer_n=3):
    n = len(toks); out = [None] * n; buf = []
    for i in range(n):
        out[i] = buf[-1] if buf else None
        if (pos[i] if i < len(pos) else None) in NOMINAL:
            buf.append(i); buf = buf[-buffer_n:]
    return out


class AllFixReader(StructAgentReader):
    def __init__(self, *a, animacy_fix=False, gated_rcpop=False, gerund_poss=False, **k):
        super().__init__(*a, struct=True, **k)
        self._animacy_fix = animacy_fix
        self._gated_rcpop = gated_rcpop
        self._gerund_poss = gerund_poss

    def _keep_pron(self, m, toks, up):
        """case_filter with the GERUND-POSSESSIVE exception: keep a possessive pronoun if it governs a gerund."""
        if not m.get("is_pronoun"):
            return True
        h = m["head"].lower()
        if h in NOMINATIVE_PRON:
            return True
        if self._gerund_poss and h in _POSS_PRON:
            p = m["wtok_start"]
            nxt = up[p + 1] if p + 1 < len(up) else None
            nxtw = toks[p + 1].lower() if p + 1 < len(toks) else ""
            if nxt == "VERB" or nxtw.endswith("ing"):     # possessive + gerund -> the gerund's subject
                return True
        return False

    def _read_events(self, sents, mentions, n_sents):
        from hdlab.situation_reader import (EventBundleCodec, ChunkedFocus, DEFAULT_ROLES, FOCUS_SEED,
                                            _sentence_nominals, _assign_roles, _assign_frame_primary_roles,
                                            _assign_affect, SuppressedPredicate, EventRecord)
        codec = EventBundleCodec(n_dim=self.focus_n_dim, roles=DEFAULT_ROLES, seed=FOCUS_SEED)
        focus = ChunkedFocus(codec, capacity=4, fanout=2, seed=FOCUS_SEED)
        sent_noms = _sentence_nominals(mentions, n_sents)
        coref_ment, _nc = parse_litbank_conll(self._cm_conll, name_gender_map=self.gaz)
        asn_all = _nominals_keep_pron(coref_ment, n_sents)
        agent_freq = {}
        for m in coref_ment:
            agent_freq[m.get("cluster")] = agent_freq.get(m.get("cluster"), 0) + 1
        cmw = dict(self._cm_weights); cmw["structure"] = STRUCT_W
        events, role_fillers, suppressed, gidx = [], [], [], 0
        for si, toks in enumerate(sents):
            text = " ".join(toks)
            evs, _t = self._extract_events(text)
            noms = sent_noms[si] if si < len(sent_noms) else []
            raw = asn_all[si] if si < len(asn_all) else []
            up = self._cached_tag(list(toks)) if (noms or raw) else []
            anoms = [m for m in raw if self._keep_pron(m, toks, up)]
            subj_before = ((incremental_subject_rcpop_gated(list(toks), up) if self._gated_rcpop
                            else incremental_subject_flat(list(toks), up)) if anoms else None)
            verb_lows = self.pred_gate_fn(text) if self.pred_gate_fn is not None else None
            for e in evs:
                agent, patient = _assign_roles(e.idx, noms, lemma=e.lemma, gate_intransitive=self.gate_intransitive)
                if anoms:
                    lo, hi = clause_bounds(toks, up, e.idx)
                    acand = [m for m in anoms if lo <= m["wtok_start"] < hi] or anoms
                    agent, _cl = self._pick(toks, up, e.idx, acand, subj_before, agent_freq, cmw)
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

    def _pick(self, toks, up, v0, acand, subj_before, agent_freq, cmw):
        cands = [(m["wtok_start"], m["head"], m.get("cluster"), m.get("wtok_end", m.get("wtok_start"))) for m in acand]
        if not cands:
            return "?", None
        base = [(p, h, cl) for (p, h, cl, _e) in cands]
        S = agent_supports(toks, up, v0, base, self._cm_gaz, agent_freq)
        if self._animacy_fix:
            S["animacy"] = [_is_animate_fixed(h.lower(), up[p] if p < len(up) else None, self._cm_gaz)
                            for (p, h, _cl) in base]
        subj_tok = subj_before[v0] if (subj_before is not None and 0 <= v0 < len(subj_before)) else None
        S["structure"] = [1.0 if (subj_tok is not None and (p == subj_tok or p <= subj_tok <= e)) else 0.0
                          for (p, _h, _cl, e) in cands]
        A = net_activation(S, cmw)
        wi = int(np.argmax(A))
        return cands[wi][1], cands[wi][2]


def _reader(arm, gaz):
    common = dict(gaz=gaz, role_route="positional", referent_per_np=True, cm_weights=AGENT_W, cm_gaz=gaz,
                  agent_source="coref", include_pron_agents=True, clause_local=True, case_filter=True)
    if arm == "struct":
        return StructAgentReader(struct=True, **common)
    if arm == "gated_rcpop":
        return AllFixReader(gated_rcpop=True, **common)
    if arm == "gerund_poss":
        return AllFixReader(gerund_poss=True, **common)
    if arm == "predrec":
        return AllFixReader(predicate_recall=True, **common)
    if arm == "ALL":     # every net-positive-or-neutral fix composed (predrec + animacy + gated_rcpop + gerund_poss)
        return AllFixReader(predicate_recall=True, animacy_fix=True, gated_rcpop=True, gerund_poss=True, **common)
    raise ValueError(arm)


ARMS = ["struct", "gated_rcpop", "gerund_poss", "predrec", "ALL"]


def _measure(docset, gaz, wdw, nboot, label):
    per = {a: {"tie": [], "canon": [], "all": []} for a in ARMS}
    for doc in docset:
        path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        sents = parse_conll_sentences(path)
        coref, ncoref = parse_litbank_conll(path, name_gender_map=gaz)
        psf = _nominals_keep_pron(coref, ncoref)
        pcf = [[m for m in lst if (not m.get("is_pronoun")) or m["head"].lower() in NOMINATIVE_PRON] for lst in psf]
        qs = _questions_full(wdw[doc]); labels = [classify_slice(q, sents, pcf, gaz) for q in qs]
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
        if a == "struct":
            continue
        for k in ("tie", "all"):
            d = _boot(per[a][k], per["struct"][k], nboot, SEED, doc_level=True)
            tests["%s-%s" % (a, k)] = d
            print("   %-14s %-5s d=%+.4f CI[%+.4f,%+.4f] sep=%s" % (a, k, d["delta"], d["lo"], d["hi"], d["ci_sep"]))
    return {"acc": acc, "tests": tests}


def run(heldout=False, nboot=2000):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    gaz = SITQA.load_given_gazetteer()
    wdw = {r["doc"]: r for r in json.load(open(SITQA.WDW_GOLD, encoding="utf-8"))}
    total = 40 if heldout else 16
    alld = SITQA.load_docs(total)
    tuned = [d for d in alld[:16] if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
    print("=" * 92); print("FIX-EVERY-LOSS composition over the structure cue")
    out = {"anchor_name": "cmrole_agent_allfix_v1", "tuned": _measure(tuned, gaz, wdw, nboot, "TUNED docs[0:16]")}
    if heldout:
        held = [d for d in alld[16:40] if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
        out["held_out"] = _measure(held, gaz, wdw, nboot, "HELD-OUT docs[16:40]")
    print("=" * 92)
    out.update({"elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()})
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2, default=str)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[done] %.0fs" % (time.time() - t0)); return out


def selftest():
    ok = True
    # gated RC-pop: who/whom/which trigger the pop; "that" does NOT
    t1 = ["the", "man", "who", "saw", "the", "boy", "ran", "."]
    p1 = ["DET", "NOUN", "PRON", "VERB", "DET", "NOUN", "VERB", "PUNCT"]
    g = incremental_subject_rcpop_gated(t1, p1)
    print("  gated RC-pop 'ran' ->", g[6], "(expect 1=man)"); ok = ok and g[6] == 1
    t2 = ["i", "think", "that", "chizzle", "engaged", "him"]
    p2 = ["PRON", "VERB", "SCONJ", "PROPN", "VERB", "PRON"]
    g2 = incremental_subject_rcpop_gated(t2, p2)
    print("  gated RC-pop 'engaged' (that-clause, no pop) ->", g2[4], "(expect 3=chizzle)"); ok = ok and g2[4] == 3
    print("SELFTEST", "PASS" if ok else "FAIL"); return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--heldout", action="store_true"); ap.add_argument("--nboot", type=int, default=2000)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    run(a.heldout, a.nboot)
