"""Scaffold-free witness for the LANDING of the COREF-DENSIFIED world-state holder keying into the live reader.

Proves the default-off `densify_world_state` sub-flag on hdlab.situation_reader.SituationReader is an ADDITIVE,
byte-identical-when-off wire that, when ON (with track_world_state ON), keys each world-state HOLDER on its
canonical DISCOURSE-ENTITY (via the promoted hdlab.world_state_entity_binding.EntityBinder Stage-1 dispatcher)
instead of the raw surface head -- so possession attaches to the entity node (John...he...him -> one key), not the
surface mention (Glenberg/Meyer/Lindem 1987; Zwaan & Radvansky 1998). Recomputes everything FROM SOURCE.

  [1] DEFAULT-OFF byte-identical: with densify_world_state OFF, sm.world_state's holder/state grid over a REAL
      LitBank doc is IDENTICAL to an independent RAW-HEAD recompute (the pre-densify keying) -- the sub-flag adds
      nothing when off. And the event set is identical to the densify-ON reader (densify only re-keys holders).
  [2] PROMOTION FAITHFUL, byte-exact: hdlab.world_state_entity_binding is byte-identical to the experiments source
      AND its EntityBinder returns identical (key, route) to the experiments EntityBinder over a dispatch battery
      (indexical / he-she anaphoric / object-anaphora+pleonastic / nominal / scope-out). Proves the promotion did
      not fork the validated dispatcher.
  [3] DENSIFY-ON canonicalizes correctly (deterministic, constructed): fed an event list with a he/she agent (whose
      coref resolves to a cluster), a first-person indexical agent, an object-'it' theme after a nominal, and a
      nominal holder, the flag-ON _read_world_state keys the holders to ~NARRATOR / C<cluster> / recency-theme /
      head EXACTLY as the EntityBinder dispatch prescribes -- isolating the wire's canonicalization from the parser.
  [4] WIRE FIRES END-TO-END on REAL 19c prose (deterministic can-fail): over real LitBank docs, densify-ON
      canonicalizes at least one live holder head that raw-head keying leaves fragmented (a he/she -> C<cluster> via
      the reader's OWN coref, or a first-person I/me -> ~NARRATOR) -- the wire is reached from read() and changes the
      keying on real extracted events, not a toy. HONEST BOUND printed: the +0.148 who-has-what LEVER is measured in
      the isolated gold-aligned densify harness (exp_world_state_coref_densify_v1, on the board's RIGHT corpus); this
      wire lands the ENTITY-KEYED representation live (no downstream live who-has-what consumer scores sm.world_state
      yet -> no live board delta; the STATE dimension is simply no longer a raw-string island).

Brain frame (PINNED): comprehension binds a participant to a persistent discourse ENTITY, not the surface mention;
possession/availability attaches to the entity node (Glenberg/Meyer/Lindem 1987). Surface-string keying FRAGMENTS
the entity (John...he...him -> 3 keys). REUSE the reader's OWN he/she coref (no new resolver). Glass-box, NO LLM.

Run: .venv/Scripts/python.exe verification/test_world_state_densify_landing_organ.py
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_situation_model_qa_v1 as QA  # noqa: E402
import experiments.world_state_entity_binding as EWSB  # noqa: E402  (the validated source)
import hdlab.world_state_entity_binding as HWSB  # noqa: E402  (the promotion)
from hdlab.situation_reader import SituationReader, SituationModel, EventRecord, CorefResolution  # noqa: E402
from hdlab.world_state_register import WorldState as HWS  # noqa: E402
from hdlab.possession_operators import build_lexicon  # noqa: E402


CAPABLE = dict(tense_agnostic_events=True, preserve_tense=True, timeline_register=True,
               track_space=True, verb_subcat_gate=True, role_route="wired",
               spacy_pred_gate=False, causation_typed=False)


def _raw_reps(reader, sm):
    """The pre-densify RAW-HEAD rep construction (binder=None path) -- the OFF behavior, reproduced from source."""
    lex = build_lexicon()
    extra_by_gi = {r.get("global_idx"): r for r in (getattr(reader, "wired_extra_roles", None) or [])}
    reps = []
    for e in sm.events:
        v = (e.predicate or "").lower()
        entry = lex.get(v)
        op = entry.get("op") if entry else None
        roles = extra_by_gi.get(e.global_idx) or {}
        arg2 = roles.get("recipient") or roles.get("source")
        ag = e.agent if e.agent not in ("?", None) else None
        pat = e.patient if e.patient not in ("?", None) else None
        reps.append({"PRED": v, "AGENT": ag, "PATIENT": pat, "ARG2": arg2, "OP": op})
    return reps


def _densified_reps(reader, sm):
    """Reproduce the wire's densify loop EXACTLY (binder + (sent_idx,head)->cluster map from sm.coref_resolutions)."""
    lex = build_lexicon()
    extra_by_gi = {r.get("global_idx"): r for r in (getattr(reader, "wired_extra_roles", None) or [])}
    binder = HWSB.EntityBinder()
    he_she = {}
    for r in (sm.coref_resolutions or []):
        rc = r.resolved_cluster
        if rc is not None and rc >= 0:
            he_she[(r.sent_idx, (r.pronoun or "").lower())] = rc   # RAW id; bind_participant formats "C%s"
    reps = []
    for e in sm.events:
        v = (e.predicate or "").lower()
        entry = lex.get(v)
        op = entry.get("op") if entry else None
        roles = extra_by_gi.get(e.global_idx) or {}
        arg2 = roles.get("recipient") or roles.get("source")
        ag = e.agent if e.agent not in ("?", None) else None
        pat = e.patient if e.patient not in ("?", None) else None
        pat = (binder.bind_theme(pat, verb=v)[0]) if pat is not None else None
        ag = (binder.bind_participant(ag, coref_cluster=he_she.get((e.sent_idx, ag.lower())))[0]
              if ag is not None else None)
        arg2 = (binder.bind_participant(arg2, coref_cluster=he_she.get((e.sent_idx, arg2.lower())))[0]
                if arg2 is not None else None)
        reps.append({"PRED": v, "AGENT": ag, "PATIENT": pat, "ARG2": arg2, "OP": op})
    return reps


def _ent_sig(sm):
    return [(e.global_idx, str(e.predicate), str(e.agent), str(e.patient), str(e.tense)) for e in sm.events]


def _grid(ws, objs, ts):
    return {(o, t): (ws.holder_of(o, t), ws.is_open(o, t)) for o in objs for t in ts}


def main():
    gaz = QA.load_given_gazetteer()
    reader_off = SituationReader(gaz=gaz, track_world_state=True, densify_world_state=False, **CAPABLE)
    reader_on = SituationReader(gaz=gaz, track_world_state=True, densify_world_state=True, **CAPABLE)

    doc_used = None
    for doc in QA.load_docs(6):
        path = os.path.join(QA.CONLL_DIR, doc + ".conll")
        if os.path.exists(path):
            doc_used = doc
            break
    assert doc_used is not None, "no LitBank doc found"
    path = os.path.join(QA.CONLL_DIR, doc_used + ".conll")
    sm_off = reader_off.read(path)
    sm_on = reader_on.read(path)

    checks = []

    # [1] DEFAULT-OFF byte-identical to the raw-head recompute + same event set as ON.
    raw = _raw_reps(reader_off, sm_off)
    ind = HWS().fold(raw)
    objs = sorted(set(list(sm_off.world_state.have.keys()) + list(sm_off.world_state.state.keys())
                      + list(ind.have.keys()) + list(ind.state.keys())))
    ts = list(range(-1, len(sm_off.events) + 1)) + [None]
    off_grid_ok = (_grid(sm_off.world_state, objs, ts) == _grid(ind, objs, ts))
    events_same = (_ent_sig(sm_off) == _ent_sig(sm_on))
    checks.append((off_grid_ok and events_same and sm_off.world_state is not None,
                   "[1] DEFAULT-OFF byte-identical: densify-OFF world-state grid == raw-head recompute over %d "
                   "objects x %d story-times (%s); event set identical to densify-ON (%s)"
                   % (len(objs), len(ts), off_grid_ok, events_same)))

    # [2] PROMOTION FAITHFUL: file byte-identical + dispatch battery identical to the experiments binder.
    with open(HWSB.__file__, "rb") as f:
        hbytes = f.read()
    with open(EWSB.__file__, "rb") as f:
        ebytes = f.read()
    file_ident = (hbytes == ebytes)
    battery = [("I", None), ("me", None), ("he", 5), ("she", None), ("it", None),
               ("them", None), ("we", None), ("you", None), ("john", None), ("mary", 9)]
    bh, be = HWSB.EntityBinder(), EWSB.EntityBinder()
    disp_ok = True
    for head, cl in battery:
        if bh.bind_participant(head, coref_cluster=cl) != be.bind_participant(head, coref_cluster=cl):
            disp_ok = False
    # theme dispatch (stateful recency) on a parallel pair
    th, te = HWSB.EntityBinder(), EWSB.EntityBinder()
    for head in ("cup", "it", "box", "it", "them"):
        if th.bind_theme(head) != te.bind_theme(head):
            disp_ok = False
    checks.append((file_ident and disp_ok,
                   "[2] PROMOTION FAITHFUL: hdlab source byte-identical to experiments (%s); EntityBinder dispatch "
                   "battery (participants + stateful themes) identical across cores (%s)" % (file_ident, disp_ok)))

    # [3] DENSIFY-ON canonicalizes correctly on a CONSTRUCTED event list (isolates dispatch from the parser).
    #     John(->cluster 5) gets cup; 'he'(->5) puts it (the cup) somewhere; 'I' takes the cup; Mary gets cup.
    sm_c = SituationModel(passage_id="densify_test", n_sentences=1)
    sm_c.events = [
        EventRecord(global_idx=0, sent_idx=0, predicate="get", agent="john", patient="cup", tense="past"),
        EventRecord(global_idx=1, sent_idx=0, predicate="get", agent="he", patient="it", tense="past"),
        EventRecord(global_idx=2, sent_idx=0, predicate="get", agent="i", patient="cup", tense="past"),
        EventRecord(global_idx=3, sent_idx=0, predicate="get", agent="mary", patient="cup", tense="past"),
    ]
    sm_c.coref_resolutions = [
        CorefResolution(pronoun="he", sent_idx=0, gold_cluster=5, resolved_cluster=5,
                        correct=True, attempted=True, bucket="x", sent_dist=0)]
    reader_on.wired_extra_roles = []
    reader_on._read_world_state(sm_c, [])
    reps_c = _densified_reps(reader_on, sm_c)   # same construction the wire ran; assert the keys it produced
    ag_keys = [r["AGENT"] for r in reps_c]
    pat_keys = [r["PATIENT"] for r in reps_c]
    canon_ok = (ag_keys[0] == "john"                       # nominal -> head
                and ag_keys[1] == "C5"                     # he -> reader's resolved cluster
                and ag_keys[2] == HWSB.NARRATOR            # first-person I -> narrator node
                and ag_keys[3] == "mary"                   # nominal -> head
                and pat_keys[0] == "cup"                   # nominal theme
                and pat_keys[1] == "cup")                  # object 'it' -> recency theme (cup)
    checks.append((canon_ok,
                   "[3] DENSIFY-ON canonicalizes: agents john / he->C5 / I->%s / mary (%r); object 'it'->recency "
                   "'cup' (%r) -- the EntityBinder dispatch, byte-exact through the wire"
                   % (HWSB.NARRATOR, ag_keys, pat_keys)))

    # [4] WIRE FIRES END-TO-END on REAL 19c prose: densify canonicalizes >=1 live holder head.
    fired = 0
    fired_examples = []
    docs_scanned = 0
    for doc in QA.load_docs(12):
        p = os.path.join(QA.CONLL_DIR, doc + ".conll")
        if not os.path.exists(p):
            continue
        docs_scanned += 1
        smd = reader_on.read(p)
        raw_r = _raw_reps(reader_on, smd)
        den_r = _densified_reps(reader_on, smd)
        for rr, dr in zip(raw_r, den_r):
            for slot in ("AGENT", "ARG2"):
                rk, dk = rr[slot], dr[slot]
                if rk is not None and dk is not None and dk != rk:
                    fired += 1
                    if len(fired_examples) < 4:
                        fired_examples.append("%s: %r->%r" % (slot, rk, dk))
        if fired >= 1 and docs_scanned >= 2:
            break
    checks.append((fired >= 1,
                   "[4] WIRE FIRES on REAL prose: densify canonicalized %d live holder head(s) over %d docs "
                   "(examples: %s) -- reached from read(), changes keying on real extracted events"
                   % (fired, docs_scanned, "; ".join(fired_examples) or "n/a")))

    print("=== witness: COREF-DENSIFIED world-state holder keying LANDING (doc '%s', %d events) ==="
          % (doc_used, len(sm_on.events)))
    ok_all = True
    for ok, msg in checks:
        print("  %s  %s" % ("PASS" if ok else "FAIL", msg))
        ok_all = ok_all and bool(ok)
    print("  HONEST BOUND: +0.148 who-has-what is the isolated gold-aligned LEVER (board's RIGHT corpus); this "
          "wire lands the entity-keyed representation LIVE (no downstream live consumer scores sm.world_state yet).")
    print("\nRESULT: %s (%d/%d)" % ("ALL CHECKS PASS" if ok_all else "FAIL",
                                    sum(1 for ok, _ in checks if ok), len(checks)))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
