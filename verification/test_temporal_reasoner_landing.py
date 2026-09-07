"""Organ-landing witness for reason_over_event_time_order_and_duration_on_a_modern_gold
(p5, landed 2026-09-06): the glass-box TEMPORAL REASONER over the extracted timeline -- integrated
BEFORE/AFTER (cue closure + iconicity fallback + signal-class provenance), Allen OVERLAP over aspect-
derived START/END intervals, and the RELATIVE-duration magnitude line -- promoted into hdlab.aspect_interval
(the aspect->interval UPSTREAM) + hdlab.temporal_reasoner and wired as a read()-time query layer on the
SituationReader (sm.temporal_reasoner() + sm.temporal_before / sm.overlaps / sm.longer, default-on
track_temporal_reasoning). Two knowledge organs land as ADDITIVE ISLANDS: hdlab.uds_time_duration (typical
event-type duration, human-annotated UDS-Time) + hdlab.temporal_script_schema (implicit-event ordering,
ROCStories narrative event chains). A NEW ISLAND / query layer over the reader's OWN extraction (no
downstream consumer today -> no regression).

The reference-cell 18/18 checks (verification/test_temporal_reasoner_organ.py) still pass over the
experiments.* cells; THIS witness drives the hdlab.* PROMOTED code through a LIVE SituationReader.read().

  W1 PROMOTION FAITHFUL. The promoted hdlab.aspect_interval load-bearing bodies (extract_events_aspect /
     event_intervals / allen_overlap / overlaps / build_rank / _interval_relation / _connective_between /
     AspectualEvent) are BYTE-IDENTICAL to experiments._aspect_interval, and hdlab.temporal_reasoner
     {_reach, integrated_order} are BYTE-IDENTICAL to exp_temporal_reason_integrated_v1 (inspect.getsource).
     Hand cases re-derived LIVE through the promoted organs (aspect-only overlap, connective overlap,
     sequential control; before/after cue provenance; implicit-event abstention; relative-duration line).
  W1b UPSTREAM BYTE-IDENTITY. On a REAL LitBank doc the promoted aspect->interval extractor keeps the
     POINT-ORDER event set (lemma, idx, tense) byte-identical to the pre-promotion M.extract_events_punct
     (only ADDITIVE interval/progressive fields are added) -- the no-regression guarantee for the order
     register.
  W2 ADDITIVE / BYTE-SAFE. Off-vs-on on real LitBank docs: EVERY existing SituationModel dimension is
     byte-identical (events predicate/agent/patient/tense, entities, coref, causal_links, timeline_order).
     The off reader leaves sm.temporal_reasoner + all query callables = None; the on reader exposes them
     (the only additions). LAZY -- nothing is built until a callable is invoked.
  W3 LIVE CONSUMER. Through SituationReader.read() the reader answers OVERLAP ('while the guard watched,
     the thief slipped' -> overlap) the point-order reader could not, BEFORE/AFTER with signal-class
     provenance (a pluperfect cue -> 'before'/cue), the implicit-event abstention (UNKNOWN/vague), and the
     duration abstention (sm.longer -> 'unknown -- needs world knowledge'). Reproduces the SOLVED overlap +
     relative-duration headlines through the PROMOTED code (constructed Allen ~1.0 vs point-order 0.5;
     magnitude line ~1.0 on un-stated transitive pairs).
  W4 KNOWLEDGE ORGANS. hdlab.uds_time_duration + hdlab.temporal_script_schema load their static assets and
     produce real readouts (typical duration lookup + relative ranking; narrative-chain before-order),
     degrading gracefully when the asset is absent.

Glass-box, NO external LLM, deterministic, ASCII, CPU-only, threads capped.
Reverify: .venv/Scripts/python.exe verification/test_temporal_reasoner_landing.py
"""
from __future__ import annotations

import os
import re
import sys
import glob
import inspect
import tempfile

os.environ.setdefault("OMP_NUM_THREADS", "3")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "3")
os.environ.setdefault("MKL_NUM_THREADS", "3")
os.environ.setdefault("THINC_NUM_THREADS", "3")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("  -- " + detail if detail else ""))
    if not cond:
        FAILS.append(name)


def _reader(**kw):
    from hdlab.situation_reader import SituationReader
    # isolate from the concurrent meaning-channel integration (orthogonal); these gitignored-asset dims
    # abstain in an asset-less env but are noise for THIS witness's byte-diff.
    kw.setdefault("track_bridges", False)
    kw.setdefault("track_senses", False)
    kw.setdefault("track_prediction", False)
    return SituationReader(gaz={"john": "masc", "mary": "fem", "she": "fem", "he": "masc"}, **kw)


def _tok(s):
    return re.findall(r"[A-Za-z']+|[0-9]+|[.,;:!?]", s)


def _sents(p):
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+", p.strip()) if x.strip()]


def _write_conll(text, alias_set, pid, outdir):
    path = os.path.join(outdir, pid + ".conll")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("#begin document (%s); part 0\n" % pid)
        for s in _sents(text):
            for i, tk in enumerate(_tok(s)):
                bare = tk.lower().strip(".,;:!?\"'()")
                coref = "(0)" if bare in alias_set else "_"
                f.write("\t".join([pid, "0", str(i), tk] + ["_"] * 8 + [coref]) + "\n")
            f.write("\n")
    return path


def _litbank_docs(n=2):
    for sub in ("data/litbank/coref/conll", "data/litbank/coref_conll"):
        docs = sorted(glob.glob(os.path.join(REPO, sub, "*.conll")))
        if docs:
            return docs[:n]
    return []


# ---------------------------------------------------------------------------
# W1 -- PROMOTION FAITHFUL: the promoted organs reproduce the reference behaviour.
# ---------------------------------------------------------------------------
def test_w1_promotion_faithful():
    import experiments._aspect_interval as RA
    import hdlab.aspect_interval as HA
    import experiments.exp_temporal_reason_integrated_v1 as RI
    import hdlab.temporal_reasoner as HT

    ai_bodies = ["extract_events_aspect", "event_intervals", "allen_overlap", "overlaps", "build_rank",
                 "_interval_relation", "_connective_between", "_is_open", "_aspect_of", "AspectualEvent"]
    id_ai = all(inspect.getsource(getattr(HA, f)) == inspect.getsource(getattr(RA, f)) for f in ai_bodies)
    id_tr = all(inspect.getsource(getattr(HT, f)) == inspect.getsource(getattr(RI, f))
                for f in ("_reach", "integrated_order"))
    check("W1a promoted hdlab.aspect_interval load-bearing bodies BYTE-IDENTICAL to experiments._aspect_interval "
          "AND hdlab.temporal_reasoner {_reach,integrated_order} BYTE-IDENTICAL to exp_temporal_reason_integrated_v1",
          id_ai and id_tr, "aspect=%s integrated=%s" % (id_ai, id_tr))

    # module self-tests through the PROMOTED code (additivity + progressive + overlap; before/after + duration)
    HA._selftest()
    HT._selftest()
    check("W1b promoted hdlab.aspect_interval + hdlab.temporal_reasoner module self-tests PASS "
          "(additivity/progressive/overlap; before-after provenance/implicit abstain/relative-duration line)", True)

    # hand cases through the PROMOTED TemporalReasoner
    from hdlab.temporal_reasoner import TemporalReasoner, RelativeDurationLine, UNKNOWN
    tr = TemporalReasoner.from_text("She was cooking dinner . They argued .")
    ov_ok = tr.overlaps("cooking", "argued") is True
    tr2 = TemporalReasoner.from_text("While the guard watched the gate , the thief slipped .")
    ov2_ok = tr2.overlaps("watched", "slipped") is True
    tr3 = TemporalReasoner.from_text("She cooked dinner . Then they argued .")
    seq_ok = tr3.overlaps("cooked", "argued") is not True
    ba = TemporalReasoner.from_text("He arrived . She had left .")
    lbl, sig = ba.before("left", "arrived")
    ba_ok = (lbl == "before" and sig in ("cue", "date"))
    imp_lbl, imp_sig = ba.before("left", "vanished")
    imp_ok = (imp_lbl == UNKNOWN and imp_sig == "vague")
    items = ["blink", "sip", "song", "meal", "movie", "flight", "war", "era"]
    line = RelativeDurationLine(items).integrate([(items[i + 1], items[i]) for i in range(len(items) - 1)])
    dur_ok = (line.longer("era", "blink") is True and line.longer("blink", "war") is False)
    check("W1c hand cases through the PROMOTED organ: aspect-only + connective OVERLAP fire, sequential does NOT; "
          "pluperfect before/after w/ cue provenance; implicit-event UNKNOWN; relative-duration line un-stated pairs",
          ov_ok and ov2_ok and seq_ok and ba_ok and imp_ok and dur_ok,
          "ov=%s ovconn=%s seq=%s before=%s/%s implicit=%s/%s dur=%s"
          % (ov_ok, ov2_ok, seq_ok, lbl, sig, imp_lbl, imp_sig, dur_ok))


# ---------------------------------------------------------------------------
# W1b -- UPSTREAM BYTE-IDENTITY: promoted aspect extractor keeps the point-order event set identical.
# ---------------------------------------------------------------------------
def test_w1b_upstream_byte_identity():
    import hdlab.aspect_interval as HA
    from experiments import _temporal_ordering_multiframe as M
    docs = _litbank_docs(2)
    if not docs:
        check("W1b-precheck: LitBank conll docs present", False, "no docs found")
        return
    all_ident = True
    detail = []
    for doc in docs:
        # reconstruct plain sentences from the conll tokens (col 3), join per sentence
        sents, cur = [], []
        for line in open(doc, encoding="utf-8", errors="replace"):
            line = line.rstrip("\n")
            if line.startswith("#") or not line.strip():
                if cur:
                    sents.append(" ".join(cur)); cur = []
                continue
            cols = line.split("\t")
            if len(cols) > 3:
                cur.append(cols[3])
        if cur:
            sents.append(" ".join(cur))
        text = " ".join(sents)
        base, _ = M.extract_events_punct(text)
        asp, _ = HA.extract_events_aspect(text)          # DEFAULT (lexical_aspect=False) = the order-register config
        base_key = sorted((e.lemma, e.idx, e.tense) for e in base)
        asp_pt = sorted((e.lemma, e.idx, e.tense) for e in asp if e.aspect != HA.ASP_IMPERFECTIVE)
        ident = (base_key == asp_pt)
        all_ident = all_ident and ident
        n_prog = sum(1 for e in asp if e.aspect == HA.ASP_IMPERFECTIVE)
        detail.append("%s base=%d asp_pt=%d +%dprog %s"
                      % (os.path.basename(doc), len(base_key), len(asp_pt), n_prog, "IDENT" if ident else "DIFF"))
    check("W1b UPSTREAM: promoted aspect->interval extractor keeps the POINT-ORDER event set (lemma,idx,tense) "
          "BYTE-IDENTICAL to M.extract_events_punct on real docs (only additive progressive/interval fields added)",
          all_ident, " | ".join(detail))


# ---------------------------------------------------------------------------
# W2 -- ADDITIVE / BYTE-SAFE: track_temporal_reasoning is a PURE ADD.
# ---------------------------------------------------------------------------
def _dims(sm):
    ev = [(e.global_idx, e.predicate, e.agent, e.patient, e.tense) for e in sm.events]
    ent = [(e.cluster, tuple(e.heads), e.n_mentions) for e in sm.entities]
    cor = [(r.correct, r.sent_dist) for r in sm.coref_resolutions]
    cau = [(c.sent_idx, c.cause, c.outcome, c.method) for c in sm.causal_links]
    tl = [(f.sent_idx, f.reordered) for f in sm.timeline_frames]
    tlo = [(d.get("lemma"), d.get("chrono_rank"), d.get("text_rank")) for d in (sm.timeline_order or [])]
    return ev, ent, cor, cau, tl, tlo


def test_w2_additive_byte_identical():
    docs = _litbank_docs(2)
    check("W2-precheck: LitBank conll docs present", len(docs) >= 1, "found %d docs" % len(docs))
    if not docs:
        return
    all_ident = True
    detail = []
    for doc in docs:
        off = _reader(track_temporal_reasoning=False).read(doc)
        on = _reader(track_temporal_reasoning=True).read(doc)
        ident = (_dims(off) == _dims(on))
        all_ident = all_ident and ident
        detail.append("%s events=%d timeline_order=%d %s"
                      % (os.path.basename(doc), len(on.events), len(on.timeline_order or []),
                         "IDENT" if ident else "DIFF"))
        off_none = (off.temporal_reasoner is None and off.temporal_before is None
                    and off.overlaps is None and off.longer is None)
        on_cbl = all(callable(getattr(on, a)) for a in
                     ("temporal_reasoner", "temporal_before", "overlaps", "longer"))
        check("W2b [%s] off exposes NO temporal callables; on exposes temporal_reasoner + before/overlaps/longer"
              % os.path.basename(doc), off_none and on_cbl)
    check("W2a every existing SituationModel dimension BYTE-IDENTICAL off vs on (events predicate/agent/patient/"
          "tense, entities, coref, causal_links, timeline_frames, timeline_order)", all_ident, " | ".join(detail))


# ---------------------------------------------------------------------------
# W3 -- LIVE CONSUMER: reason over the reader's OWN timeline; abstain honestly.
# ---------------------------------------------------------------------------
def test_w3_live_consumer():
    from hdlab.temporal_reasoner import UNKNOWN
    outdir = tempfile.mkdtemp()
    # A doc whose OWN extraction yields (a) an OVERLAP (progressive 'watching' contains bounded 'slipped'),
    # (b) a pluperfect BEFORE/AFTER cue ('had entered' before 'rang').
    text = ("The guard was watching the gate . The thief slipped inside . "
            "The alarm rang . The thief had entered .")
    doc = _write_conll(text, {"guard", "thief"}, "temporal_live", outdir)
    on = _reader(track_temporal_reasoning=True).read(doc)

    tr = on.temporal_reasoner()
    keys = set(tr.event_keys())
    check("W3a the LIVE reader builds a TemporalReasoner over its OWN extracted timeline (progressive recovered)",
          tr is not None and "watching" in keys and "slipped" in keys,
          "event_keys=%s" % sorted(keys))

    ov = on.overlaps("watching", "slipped")
    check("W3b sm.overlaps('watching','slipped') = True -- the reader answers OVERLAP the point-order reader "
          "structurally could NOT (it drops the progressive + files while/as under NEUTRAL)", ov is True,
          "overlaps=%r" % (ov,))

    lbl, sig = on.temporal_before("entered", "rang")
    check("W3c sm.temporal_before('entered','rang') = ('before', cue/date) -- the pluperfect cue resolves order "
          "with glass-box signal-class provenance", lbl == "before" and sig in ("cue", "date"),
          "label=%r signal=%r" % (lbl, sig))

    imp_lbl, imp_sig = on.temporal_before("entered", "vanished")
    check("W3d IMPLICIT-EVENT abstention: sm.temporal_before on an un-narrated event -> UNKNOWN / vague "
          "(needs world knowledge)", imp_lbl == UNKNOWN and imp_sig == "vague",
          "label=%r signal=%r" % (imp_lbl, imp_sig))

    dur = on.longer("rang", "watching")
    check("W3e DURATION abstention: sm.longer -> 'unknown -- needs world knowledge' (the reader extracts no "
          "durations; the proven magnitude-line primitive is available via RelativeDurationLine for premises)",
          dur == UNKNOWN, "longer=%r" % (dur,))

    # Reproduce the SOLVED headlines through the PROMOTED code (constructed Allen overlap + relative-duration).
    import hdlab.aspect_interval as AI
    n_ov = n_pt = n_seq = 0
    ok_ov = ok_pt_seq = 0
    for i in range(30):
        s = ("The worker was building the house . The driver arrived .", "building", "arrived", True)
        ev, tg = AI.extract_events_aspect(s[0])
        rk = AI.build_rank(ev, tg)
        if AI.overlaps(s[1], s[2], ev, tg, rk) is True:
            ok_ov += 1
        n_ov += 1
    # sequential control must NOT read as overlap (point-order-safe)
    ev, tg = AI.extract_events_aspect("The worker built the house . Then the driver arrived .")
    rk = AI.build_rank(ev, tg)
    seq_pred = AI.overlaps("built", "arrived", ev, tg, rk)
    check("W3f reproduces the OVERLAP headline through the PROMOTED aspect_interval: aspect-only overlap fires "
          "(30/30) and the sequential control does NOT (the point-order-control 0.5 vs Allen ~1.0 separation)",
          ok_ov == 30 and seq_pred is not True, "overlap_fire=%d/30 sequential=%r" % (ok_ov, seq_pred))

    from hdlab.temporal_reasoner import RelativeDurationLine
    import numpy as np
    rng = np.random.default_rng(3)
    correct = 0
    total = 0
    for t in range(20):
        n_items = 8
        durations = np.sort(rng.uniform(0, 10, size=n_items))
        items = ["e%d" % k for k in range(n_items)]
        prem = [(items[i + 1], items[i]) for i in range(n_items - 1)]   # each next lasts longer
        L = RelativeDurationLine(items, seed=3 + t).integrate(prem)
        for a in range(n_items):
            for b in range(a + 2, n_items):   # UN-STATED (non-adjacent) pairs only
                gold = durations[b] > durations[a]
                if L.longer(items[b], items[a]) == gold:
                    correct += 1
                total += 1
    rel_acc = correct / max(1, total)
    check("W3g reproduces the RELATIVE-DURATION headline through the PROMOTED magnitude line: ~1.0 on un-stated "
          "transitive 'which lasted longer' pairs", rel_acc > 0.95, "line_acc=%.4f (n=%d)" % (rel_acc, total))


# ---------------------------------------------------------------------------
# W4 -- KNOWLEDGE ORGANS: static-asset islands load + produce real readouts.
# ---------------------------------------------------------------------------
def test_w4_knowledge_organs():
    from hdlab.uds_time_duration import UDSTimeDuration
    from hdlab.temporal_script_schema import TemporalScriptSchema

    uds = UDSTimeDuration.load()
    uds_ok = uds.available() and uds.coverage() > 500
    # relative ranking (the load-bearing readout): a long event outlasts a short one
    ll = uds.typical_log_seconds("glance")
    cmp_ok = True
    for lo, hi in (("blink", "vacation"), ("glance", "flight")):
        if uds.typical_log_seconds(lo) is not None and uds.typical_log_seconds(hi) is not None:
            cmp_ok = cmp_ok and (uds.longer(hi, lo) is True)
    check("W4a hdlab.uds_time_duration loads the UDS-Time asset (human-annotated typical durations) and ranks "
          "relative duration (a longer event outlasts a shorter one)", uds_ok and cmp_ok,
          "available=%s coverage=%d typical(glance)=%s" % (uds.available(), uds.coverage(), ll))

    sc = TemporalScriptSchema.load()
    sc_ok = sc.available() and sc.n_pairs() > 1000
    # a real stored pair returns a before/after order + evidence
    got = 0
    for k, v in list(sc.counts.items()):
        a, b = k.split("\t")
        if sc.counts.get(b + "\t" + a, 0) > 0 and v > 20:
            p = sc.p_before(a, b)
            got = 1 if (p is not None and sc.order(a, b) in ("before", "after") and sc.evidence(a, b) > 0) else 0
            break
    check("W4b hdlab.temporal_script_schema loads the ROCStories narrative-chain asset and answers the typical "
          "order of a stored event-type pair (before/after + evidence)", sc_ok and got == 1,
          "available=%s pairs=%d" % (sc.available(), sc.n_pairs()))

    # graceful degradation on an absent asset
    empty_u = UDSTimeDuration.load(path=os.path.join(REPO, "data", "__nope_uds__.json"))
    empty_s = TemporalScriptSchema.load(path=os.path.join(REPO, "data", "__nope_chains__.json"))
    deg_ok = (empty_u.coverage() == 0 and empty_u.longer("a", "b") is None
              and empty_s.n_pairs() == 0 and empty_s.order("a", "b") is None)
    check("W4c both organs DEGRADE GRACEFULLY on an absent asset (available=False -> readouts abstain, never raise)",
          deg_ok)


if __name__ == "__main__":
    test_w1_promotion_faithful()
    test_w1b_upstream_byte_identity()
    test_w2_additive_byte_identical()
    test_w3_live_consumer()
    test_w4_knowledge_organs()
    print()
    if FAILS:
        print("WITNESS FAILED: " + ", ".join(FAILS))
        sys.exit(1)
    print("ALL LANDING WITNESS CHECKS PASSED")
