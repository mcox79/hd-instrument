"""exp_wire_predarg_binder_live_reader_integration_v1 -- DEMONSTRATE the proposed diff IN the LIVE
`hdlab.situation_reader.SituationReader.read()` code path (not a standalone mirror), with NO regression.

The sibling cell exp_wire_predarg_binder_live_reader_v1 measured the mechanism in a faithful STANDALONE mirror
of the reader's role path (McGuffey gold). This cell closes the last integration gap for an EXCELLENT wiring
result: it subclasses the REAL SituationReader and routes its role assignment through parse ->
route_predicate_arguments (+ quotative inversion), running the ACTUAL read() pipeline end-to-end, and proves:
  (1) NO REGRESSION: with routing OFF the subclass is byte-identical to the stock reader; with routing ON the
      NON-role dimensions (entities / coref / timeline / causation / memory round-trip) are byte-identical --
      the diff touches ONLY role assignment, exactly as proposed.
  (2) The live role path is FIXED on the constructions the positional rule gets wrong: QUOTATIVE inversion
      ("... said John" -> John is the AGENT, not the object) and it EMITS richer roles (RECIPIENT) the
      agent/patient reader structurally cannot.
No tokenization mismatch: the parser is fed the reader's OWN token list (the same `toks` read() passes to
_read_events), so router indices align with the reader's mention positions.

hdlab/ UNTOUCHED -- this is a SUBCLASS in experiments/ that demonstrates the proposed hdlab/situation_reader
diff; strategy lands the real change (Q111). No external LLM (the invariant); nltk + numpy only.

Run: .venv/Scripts/python.exe experiments/exp_wire_predarg_binder_live_reader_integration_v1.py --self-test
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import hdlab.situation_reader as SR  # noqa: E402
from hdlab.situation_reader import (  # noqa: E402
    SituationReader, EventRecord, EventBundleCodec, ChunkedFocus, DEFAULT_ROLES,
    _sentence_nominals, _assign_roles, _assign_frame_primary_roles, _assign_affect,
    SuppressedPredicate, FOCUS_SEED, _write_temp_conll)
from hdlab.pos_tagger import PosTagger  # noqa: E402
from hdlab.arc_parser import ArcParser  # noqa: E402
from hdlab.predicate_argument_frontend import route_predicate_arguments  # noqa: E402
from hdlab.thematic_role_labeler import lemma_verb  # noqa: E402
from experiments.exp_wire_predarg_binder_live_reader_v1 import (  # noqa: E402
    _quotative_speaker, _is_speech_verb, _matrix_verbs, PREDARG_TO_GOLD)

POS_ASSET = os.path.join(REPO_ROOT, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
ARC_ASSET = os.path.join(REPO_ROOT, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")


_FRONTEND = {}


def _load_frontend():
    """Load the persisted UPOS tagger + arc parser ONCE per process (not per reader instance)."""
    if "t" not in _FRONTEND:
        _FRONTEND["t"] = PosTagger.load(POS_ASSET)
        _FRONTEND["p"] = ArcParser.load(ARC_ASSET)
    return _FRONTEND["t"], _FRONTEND["p"]


class WiredSituationReader(SituationReader):
    """SituationReader whose role assignment is routed through a real parse -> route_predicate_arguments
    (+ quotative inversion), demonstrating the proposed hdlab/situation_reader diff IN the live read() path.
    role_route='positional' (default) is byte-identical to the stock reader; role_route='wired' routes roles."""

    def __init__(self, *args, role_route="positional", **kw):
        super().__init__(*args, **kw)
        self.role_route = role_route
        self.wired_extra_roles = []           # demo artifact: [{global_idx, goal, recipient, ...}]
        if role_route == "wired":
            self._tagger, self._parser = _load_frontend()   # module-cached (load once, not per reader)

    def _router_roles(self, toks):
        """{verb_pos0: {pa_role: token_pos0}} from parse -> route_predicate_arguments (+ quotative), fed the
        reader's OWN tokens so indices align with mention wtok positions. Empty if the parse yields nothing."""
        if not toks or len(toks) > 120:
            return {}
        pos = self._tagger.tag(toks)
        heads = self._parser.parse(toks, pos).heads
        out = {}
        for v in _matrix_verbs(toks, pos, heads):
            # quotative=False: the WiredSituationReader applies its OWN mention-based quotative (the reader
            # lowercases tokens, so the router's capitalization-based speaker scan cannot fire here anyway);
            # disabled explicitly to keep this a faithful reproduction of the validated integration path.
            roles = route_predicate_arguments(toks, pos, heads, v, quotative=False)
            out[v - 1] = {k: (val - 1) for k, val in roles.items() if isinstance(val, int) and val}
        return out

    @staticmethod
    def _align_events_to_toks(evs, toks):
        """Map each event's predicate (surface e.lemma) to its `toks` index, greedy left-to-right (T's
        tokenization != `toks`, so e.idx cannot be trusted). None if no surface match remains."""
        low = [t.lower() for t in toks]
        used = set()
        out = []
        for e in evs:
            j = next((k for k in range(len(low)) if k not in used and low[k] == str(e.lemma).lower()), None)
            if j is not None:
                used.add(j)
            out.append(j)
        return out

    @staticmethod
    def _nom_head_at(noms, pos0):
        """The non-pronoun mention head at/covering token position pos0 (reader tracks only non-pronoun
        heads for roles), else the nearest within 1 token, else None."""
        for m in noms:
            if m["wtok_start"] == pos0:
                return m["head"]
        for m in noms:
            if abs(m["wtok_start"] - pos0) <= 1:
                return m["head"]
        return None

    def _read_events(self, sents, mentions, n_sents):
        """Copy of the stock _read_events with ONE change: when role_route='wired', agent/patient come from
        the parse -> router (mapped to the reader's mention heads), with the positional rule as the
        good-enough fallback; richer roles (goal/recipient/...) are collected as a demo artifact. Everything
        else (event extraction, encoding, focus, frame/affect metadata) is UNCHANGED."""
        if self.role_route != "wired":
            return super()._read_events(sents, mentions, n_sents)
        codec = EventBundleCodec(n_dim=self.focus_n_dim, roles=DEFAULT_ROLES, seed=FOCUS_SEED)
        focus = ChunkedFocus(codec, capacity=4, fanout=2, seed=FOCUS_SEED)
        sent_noms = _sentence_nominals(mentions, n_sents)
        events, role_fillers, suppressed = [], [], []
        self.wired_extra_roles = []
        gidx = 0
        for si, toks in enumerate(sents):
            text = " ".join(toks)
            evs, _tagged = SR.T.extract_events(text)
            noms = sent_noms[si] if si < len(sent_noms) else []
            rr = self._router_roles(list(toks))
            # T.extract_events uses a DIFFERENT tokenization than `toks` (e.idx is T-space, not toks-space);
            # align each event's predicate to its `toks` position by surface match (greedy L->R), so router
            # roles (keyed in toks-space, the same space as mention wtok_start) line up with the reader's event.
            toks_pos = self._align_events_to_toks(evs, toks)
            verb_lows = self.pred_gate_fn(text) if self.pred_gate_fn is not None else None
            for ei, e in enumerate(evs):
                # positional roles (the fallback + the OFF behavior), computed identically to the stock reader
                agent, patient = _assign_roles(e.idx, noms, lemma=e.lemma,
                                               gate_intransitive=self.gate_intransitive)
                extra = {}
                vp = toks_pos[ei]
                if vp is not None and _is_speech_verb(lemma_verb(e.lemma)):
                    # QUOTATIVE INVERSION, reader-native (case-independent): the reader's tokens are
                    # lowercased, so capitalization-based animacy fails -- use the MENTION structure instead.
                    # The speaker (AGENT) is the nearest postverbal tracked mention ("... said John"), else the
                    # nearest preverbal one; the quoted content is not a role filler.
                    post = [m for m in noms if m["wtok_start"] > vp]
                    pre = [m for m in noms if m["wtok_start"] < vp]
                    spk = post[0]["head"] if post else (pre[-1]["head"] if pre else None)
                    if spk is not None:
                        agent, patient = spk, "?"
                else:
                    vr = rr.get(vp) if vp is not None else None
                    if vr is not None:
                        a_head = self._nom_head_at(noms, vr["agent"]) if "agent" in vr else None
                        t_head = self._nom_head_at(noms, vr["theme"]) if "theme" in vr else None
                        if a_head is not None:
                            agent = a_head        # ROUTER agent (fixes passive/ditransitive), else positional
                        if t_head is not None:
                            patient = t_head
                        for pa in ("goal", "recipient", "source", "location", "path", "direction", "instrument"):
                            if pa in vr:
                                h = self._nom_head_at(noms, vr[pa])
                                if h is not None:
                                    extra[PREDARG_TO_GOLD.get(pa, pa)] = h
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
                                          obj_role=obj_role, affect=affect))
                role_fillers.append(rf)
                if extra:
                    self.wired_extra_roles.append({"global_idx": gidx, **extra})
                gidx += 1
        return events, focus, codec, role_fillers, suppressed


# ------------------------------------------------------------------------------------------------
# ================================================================================================
# AT-SCALE lift THROUGH the live read() class: convert the 57 McGuffey passages to CoNLL, run stock vs
# WiredSituationReader.read(), and score role accuracy on the reader's ACTUAL EventRecords -- so the lift
# magnitude ORIGINATES in the live SituationReader class, not a standalone mirror.
# ================================================================================================
import re as _re  # noqa: E402
import numpy as _np  # noqa: E402
from experiments.exp_wire_organs_endtoend_v1 import (  # noqa: E402
    load_gold as _load_mcguffey, _passage_aliases as _aliases)
from experiments.exp_wire_predarg_binder_live_reader_v1 import fam as _fam  # noqa: E402
from hdlab.coref import load_name_gender as _load_ng  # noqa: E402


def _tok_clause(text):
    """Whitespace + punctuation-separated tokens (punct as its own token), matching the reader's CoNLL cols."""
    return [t for t in _re.findall(r"[A-Za-z']+|[^\sA-Za-z']", text) if t.strip()]


def mcguffey_conll_rows(passage):
    """Convert a McGuffey passage (clauses + entity chains) to CoNLL rows for _write_temp_conll, marking each
    entity mention head token with its cluster id. Returns (rows, cid_by_entity)."""
    ents = list(passage["entities"].keys())
    cid = {e: i for i, e in enumerate(ents)}
    rows = []
    for ci, clause in enumerate(passage["clauses"]):
        toks = _tok_clause(clause)
        coref = ["_"] * len(toks)
        low = [t.lower() for t in toks]
        # mark each entity's mention head at this clause (first unused matching token)
        for e in ents:
            for m in passage["entities"][e]:
                if m["clause"] != ci:
                    continue
                mtoks = [w.lower().strip(".,'\"") for w in str(m["mention"]).split() if w.strip()]
                head = mtoks[-1] if mtoks else None
                if head is None:
                    continue
                for k in range(len(low)):
                    if low[k] == head and coref[k] == "_":
                        coref[k] = f"({cid[e]})"
                        break
        for w, (t, c) in enumerate(zip(toks, coref)):
            rows.append((ci, w, t, c))
    return rows, cid


def _reader_role_by_ec(reader, sm, passage):
    """From the reader's ACTUAL output, build {(entity, clause): set(role_family)} by mapping each event's
    agent/patient (and the wired extra roles) head-string back to a tracked entity via the passage aliases."""
    alias, _g = _aliases(passage)

    def head_to_entity(head):
        if not head or head == "?":
            return None
        h = str(head).lower().strip(".,'\"")
        for e, toks in alias.items():
            if h in toks:
                return e
        return None
    by_ec = {}
    by_ent = {}
    extra = {x["global_idx"]: x for x in getattr(reader, "wired_extra_roles", [])}
    for ev in sm.events:
        ci = ev.sent_idx
        for head, fam_role in ((ev.agent, "AGENT"), (ev.patient, "OBJECT")):
            e = head_to_entity(head)
            if e is not None:
                by_ec.setdefault((e, ci), set()).add(fam_role)
                by_ent.setdefault(e, []).append((ci, fam_role))
        xr = extra.get(ev.global_idx, {})
        for rk, rv in xr.items():
            if rk == "global_idx":
                continue
            e = head_to_entity(rv)
            if e is not None:
                by_ec.setdefault((e, ci), set()).add(_fam(rk))
                by_ent.setdefault(e, []).append((ci, _fam(rk)))
    return by_ec, by_ent


def _score_reader(reader_cls, passages, gaz, **kw):
    """Run reader_cls.read() on each McGuffey-as-CoNLL passage; per-passage (correct, total) role accuracy on
    the reader's ACTUAL events (family grain), with the same fallback as the standalone scorer."""
    gm = "AGENT"
    rows = []
    for p in passages:
        conll_rows, _cid = mcguffey_conll_rows(p)
        path = _write_temp_conll(conll_rows)
        try:
            rdr = reader_cls(gaz=gaz, **kw)
            sm = rdr.read(path)
        finally:
            os.remove(path)
        by_ec, by_ent = _reader_role_by_ec(rdr, sm, p)
        c = n = 0
        for q in p.get("target_queries", []):
            e, qc, g = q["entity"], q["query_clause"], _fam(q["gold_role"])
            if (e, qc) in by_ec:
                ok = g in by_ec[(e, qc)]
            elif by_ent.get(e):
                ok = g == max(by_ent[e], key=lambda x: x[0])[1]
            else:
                ok = (g == gm)
            n += 1; c += int(ok)
        rows.append((c, n))
    return _np.array(rows, float)


def run_scale(n_boot=2000, seed=0):
    """The honest close: the role lift measured THROUGH the live SituationReader.read() class at scale."""
    gaz = dict(_load_ng())
    passages = _load_mcguffey()
    stock = _score_reader(SituationReader, passages, gaz)
    wired = _score_reader(WiredSituationReader, passages, gaz, role_route="wired")

    def acc_ci(A, sd):
        acc = A[:, 0].sum() / max(A[:, 1].sum(), 1)
        r = _np.random.default_rng(sd); nd = len(A); b = []
        for _ in range(n_boot):
            idx = r.integers(0, nd, nd); b.append(A[idx, 0].sum() / max(A[idx, 1].sum(), 1))
        lo, hi = _np.percentile(b, [2.5, 97.5])
        return {"acc": round(float(acc), 4), "ci": [round(float(lo), 4), round(float(hi), 4)],
                "n": int(A[:, 1].sum())}
    r = _np.random.default_rng(seed + 9); nd = len(stock); boots = []
    for _ in range(n_boot):
        idx = r.integers(0, nd, nd)
        da = wired[idx, 0].sum() / max(wired[idx, 1].sum(), 1)
        db = stock[idx, 0].sum() / max(stock[idx, 1].sum(), 1)
        boots.append(da - db)
    boots = _np.array(boots); lo, hi = _np.percentile(boots, [2.5, 97.5])
    delta = wired[:, 0].sum() / max(wired[:, 1].sum(), 1) - stock[:, 0].sum() / max(stock[:, 1].sum(), 1)
    return {"stock_positional": acc_ci(stock, seed + 1), "wired": acc_ci(wired, seed + 2),
            "wired_minus_stock": {"delta": round(float(delta), 4), "ci": [round(float(lo), 4), round(float(hi), 4)],
                                  "half_width": round(float(hi - lo) / 2, 4),
                                  "null_p95": round(float(_np.percentile(_np.abs(boots - boots.mean()), 95)), 4),
                                  "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")},
            "note": "role accuracy THROUGH the live SituationReader.read() class (57 McGuffey passages as CoNLL); "
                    "absolute level is capped by the reader's event-extraction recall (~0.32), so the LIFT is the "
                    "result, measured in the live class."}


def _dims(sm):
    """The NON-role dimensions the wiring must leave byte-identical."""
    return {
        "n_sentences": sm.n_sentences,
        "entities": [(e.cluster, tuple(e.heads), tuple(e.sent_indices), e.n_mentions, e.is_person)
                     for e in sm.entities],
        "coref": [(r.pronoun, r.sent_idx, r.resolved_cluster, r.correct) for r in sm.coref_resolutions],
        "timeline": [(f.sent_idx, tuple(f.chrono_order), f.reordered) for f in sm.timeline_frames],
        "causal": [(l.sent_idx, l.cause, l.outcome, l.method) for l in sm.causal_links],
        "memory_roundtrip": round(sm.memory_roundtrip.get("roundtrip_rate", 0.0), 6),
        "n_events": len(sm.events),
    }


def self_test():
    gaz = {"john": "masc", "mary": "fem", "harry": "masc", "boatman": "masc", "beggar": "masc"}

    # (1) NO REGRESSION on the stock reader's own end-to-end self-test doc: non-role dims byte-identical,
    #     event count unchanged (routing ON vs the stock reader).
    rows = [
        (0, 0, "John", "(0)"), (0, 1, "saw", "_"), (0, 2, "Mary", "(1)"), (0, 3, ".", "_"),
        (1, 0, "He", "(0)"), (1, 1, "had", "_"), (1, 2, "finished", "_"),
        (1, 3, "before", "_"), (1, 4, "she", "(1)"), (1, 5, "arrived", "_"), (1, 6, ".", "_"),
        (2, 0, "She", "(1)"), (2, 1, "cried", "_"), (2, 2, "because", "_"),
        (2, 3, "he", "(0)"), (2, 4, "left", "_"), (2, 5, ".", "_"),
    ]
    path = _write_temp_conll(rows)
    try:
        stock = SituationReader(gaz=gaz).read(path)
        wired = WiredSituationReader(gaz=gaz, role_route="wired").read(path)
        off = WiredSituationReader(gaz=gaz, role_route="positional").read(path)
    finally:
        os.remove(path)
    assert _dims(off) == _dims(stock), "role_route=positional must be BYTE-IDENTICAL to the stock reader"
    ds, dw = _dims(stock), _dims(wired)
    for k in ("n_sentences", "entities", "coref", "timeline", "causal", "memory_roundtrip"):
        assert ds[k] == dw[k], f"wiring must leave NON-role dim {k} byte-identical: {ds[k]} != {dw[k]}"
    assert dw["n_events"] == ds["n_events"], f"event recall must be unchanged: {dw['n_events']} vs {ds['n_events']}"

    # (2) QUOTATIVE inversion FIXED in the live path: "<quote> said John ." -- John is the AGENT (speaker),
    #     not the object. The stock positional rule brands the postverbal speaker the patient.
    rows_q = [
        (0, 0, "Mary", "(0)"), (0, 1, "cried", "_"), (0, 2, ".", "_"),
        (1, 0, "Yes", "_"), (1, 1, ",", "_"), (1, 2, "said", "_"), (1, 3, "John", "(1)"), (1, 4, ".", "_"),
    ]
    path = _write_temp_conll(rows_q)
    try:
        stock_q = SituationReader(gaz=gaz).read(path)
        wired_q = WiredSituationReader(gaz=gaz, role_route="wired").read(path)
    finally:
        os.remove(path)
    say_stock = [e for e in stock_q.events if e.predicate == "said"]
    say_wired = [e for e in wired_q.events if e.predicate == "said"]
    assert say_wired, f"'said' event must be extracted: {[e.predicate for e in wired_q.events]}"
    assert say_wired[0].agent.lower() == "john", (
        f"WIRED must bind the postverbal speaker John as AGENT, got agent={say_wired[0].agent!r}")
    # the stock positional reader does NOT get John as the agent (quotative inversion is the diff's win)
    stock_wrong = (not say_stock) or say_stock[0].agent.lower() != "john"
    assert stock_wrong, (f"the positional reader should MIS-assign the quotative speaker (it is the diff's "
                         f"win); got stock agent={say_stock[0].agent!r}")

    # (3) richer role EMITTED in the live path: a ditransitive -> RECIPIENT (the agent/patient reader cannot).
    rows_d = [
        (0, 0, "Mary", "(0)"), (0, 1, "gave", "_"), (0, 2, "the", "_"), (0, 3, "book", "(1)"),
        (0, 4, "to", "_"), (0, 5, "John", "(2)"), (0, 6, ".", "_"),
    ]
    path = _write_temp_conll(rows_d)
    try:
        rdr_d = WiredSituationReader(gaz=gaz, role_route="wired")
        rdr_d.read(path)
    finally:
        os.remove(path)
    recips = [x for x in rdr_d.wired_extra_roles if str(x.get("recipient", "")).lower() == "john"]
    assert recips, (f"WIRED must emit RECIPIENT=John for the ditransitive (a role the agent/patient reader "
                    f"cannot); extra_roles={rdr_d.wired_extra_roles}")

    print("SELF-TEST PASS (live read() path): role_route=positional byte-identical to stock; wiring leaves "
          "entities/coref/timeline/causal/memory byte-identical + event recall unchanged; QUOTATIVE speaker "
          "John bound as AGENT where the stock reader fails; RECIPIENT emitted for a ditransitive.")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--scale", action="store_true", help="measure the role lift THROUGH the live read() at scale")
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.scale:
        import json
        res = run_scale(n_boot=args.n_boot)
        outdir = os.path.join(REPO_ROOT, "data/exp_wire_predarg_binder_live_reader_integration_v1")
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "metrics_scale.json"), "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
        s, w, d = res["stock_positional"], res["wired"], res["wired_minus_stock"]
        print(f"role accuracy THROUGH the live SituationReader.read() (57 McGuffey passages as CoNLL, n={s['n']}):")
        print(f"  stock/positional {s['acc']:.3f} [{s['ci'][0]:.3f},{s['ci'][1]:.3f}]")
        print(f"  wired            {w['acc']:.3f} [{w['ci'][0]:.3f},{w['ci'][1]:.3f}]")
        print(f"  wired - stock    {d['delta']:+.3f} [{d['ci'][0]:+.3f},{d['ci'][1]:+.3f}] null_p95={d['null_p95']:.3f} {d['band']}")
        return
    print("use --self-test | --scale")


if __name__ == "__main__":
    main()
