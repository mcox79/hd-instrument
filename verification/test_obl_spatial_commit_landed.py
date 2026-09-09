"""LANDING WITNESS -- OPT-A/OPT-C from build_the_obl_spatial_defer_consumer (owner-DONE 2026-09-08).

Landed (strategy, Q111): hdlab.joint_relation_frontend.parse_sentence now also caches the exact single-root
Matrix-Tree marginals (OPT-C, one inverse/read reused) and hdlab.joint_relation_frontend.commit_spatial_ground_heads
RE-ATTACHES each spatial-preposition GROUND nominal to the marginal-argmax over the brain-faithful candidate set
(OPT-A -- McRae/Spivey normalized-recurrence COMMIT to the globally-normalized posterior, not the local MAP-tree head,
not the refuted defer). Wired in situation_reader._read_spatial_reasoning (default-on `spatial_obl_commit`), scoped so
temporal's heads stay byte-identical.

W1  want_marginals=True does NOT change heads (the shared-path no-regress: temporal/spatial share parse_sentence).
W2  commit_spatial_ground_heads returns a NEW dict, never mutates its input, and is a NO-OP when marginals absent.
W3  live reader: events/timeline/causal are BYTE-IDENTICAL with the commit ON vs OFF (the commit only feeds the
    SpatialModel); the spatial reasoner is exercised.
W4  (guarded on UD-EWT) the committed ground attachment BEATS the live exact-MAP decode CI-separated on spatial obl.

Run: .venv/Scripts/python.exe verification/test_obl_spatial_commit_landed.py
"""
import os
import sys
import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import hdlab.joint_relation_frontend as JF
from hdlab.arc_parser import ArcParser

_ARC = os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
_CORPUS = [
    "The soldier walked into the office .".split(),
    "He put the rifle on the table near the window .".split(),
    "She waited in the hall by the door .".split(),
    "They travelled from the village to the city through the forest .".split(),
    "A painting of the mountains hung above the fireplace in the hall .".split(),
]
_fail = []


def _ck(cond, msg):
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond:
        _fail.append(msg)


def w1_head_invariance():
    ap = ArcParser.load(_ARC)
    diff = 0
    for toks in _CORPUS:
        pos = ap_tag(ap, toks)
        h0 = dict(ap.parse(toks, pos, decode="exact", want_marginals=False).heads)
        h1 = dict(ap.parse(toks, pos, decode="exact", want_marginals=True).heads)
        diff += int(h0 != h1)
    _ck(diff == 0, "W1 want_marginals=True leaves heads byte-identical (diff=%d, must be 0)" % diff)


def ap_tag(ap, toks):
    t, _p = JF._frontend()
    return t.tag(list(toks))


def w2_commit_purity():
    toks = _CORPUS[0]
    up, hd = JF.parse_sentence(toks)
    hd_snapshot = dict(hd)
    hd_c = JF.commit_spatial_ground_heads(toks, up, hd)
    _ck(hd == hd_snapshot, "W2 commit does NOT mutate the input heads dict")
    _ck(hd_c is not hd, "W2 commit returns a NEW dict")
    # no-op when marginals absent
    fake = ["z%d" % i for i in range(200)]  # > 160 -> parse_sentence stores {} marginals
    up2, hd2 = JF.parse_sentence(fake)
    _ck(JF.commit_spatial_ground_heads(fake, up2, hd2) == hd2, "W2 no-op (returns input) when marginals unavailable")


def w3_reader_noregress():
    from hdlab.situation_reader import SituationReader, _write_temp_conll
    rows = []
    for si, s in enumerate(_CORPUS, 1):
        for wi, w in enumerate(s, 1):
            rows.append((si, wi, w, "-"))
    path = _write_temp_conll(rows)
    r_on = SituationReader(); r_on.spatial_obl_commit = True
    r_off = SituationReader(); r_off.spatial_obl_commit = False
    a = r_on.read(path); b = r_off.read(path)

    def ev(sm):
        return [(getattr(e, "pred", None), getattr(e, "sent_idx", None)) for e in (getattr(sm, "events", []) or [])]

    def tl(sm):
        return [(f.sent_idx, tuple(f.chrono_order)) for f in (getattr(sm, "timeline_frames", []) or [])]

    def ca(sm):
        return [(l.sent_idx, l.cause, l.outcome) for l in (getattr(sm, "causal_links", []) or [])]

    _ck(ev(a) == ev(b), "W3 events byte-identical ON vs OFF (n=%d)" % len(ev(a)))
    _ck(tl(a) == tl(b), "W3 timeline byte-identical ON vs OFF")
    _ck(ca(a) == ca(b), "W3 causal byte-identical ON vs OFF")
    sr = getattr(a, "spatial_reasoner", None)
    _ck(callable(sr) and sr() is not None, "W3 spatial reasoner exercised")


def w4_accuracy():
    try:
        import experiments.exp_obl_spatial_integrator_throughput_v1 as INT
        from experiments.exp_typed_selpref_ppattach_v1 import load, TEST
    except Exception as e:
        print("  SKIP W4 (UD-EWT loader unavailable: %s)" % e)
        return
    te = [s for s in load(TEST) if 2 <= len(s) <= 60]
    e_ok = []; c_ok = []
    for s in te:
        toks = [t[1] for t in s]; n = len(s)
        if n < 2:
            continue
        gold = {t[0]: t[4] for t in s}; grel = {t[0]: t[5].split(":")[0] for t in s}
        up, hd = JF.parse_sentence(toks)
        hd_c = JF.commit_spatial_ground_heads(toks, up, hd)
        for t in s:
            c = t[0]
            if grel.get(c) not in INT.OBL_RELS or t[3] not in INT.NOMINAL:
                continue
            if INT._prep_of(s, c) not in INT.SPATIAL_PREP:
                continue
            gh = gold.get(c)
            if gh is None:
                continue
            e_ok.append(int(hd.get(c, 0) == gh)); c_ok.append(int(hd_c.get(c, 0) == gh))
    e = np.array(e_ok); c = np.array(c_ok)
    rng = np.random.default_rng(17); d = c - e; idx = rng.integers(0, len(d), (4000, len(d)))
    lo, hi = np.percentile(d[idx].mean(1), [2.5, 97.5])
    print("  [read] exact-MAP=%.4f commit=%.4f delta=%+.4f CI[%.4f,%.4f] n=%d" %
          (e.mean(), c.mean(), float(d.mean()), lo, hi, len(e)))
    _ck(lo > 0, "W4 committed ground attachment beats live exact-MAP CI-separated on UD-EWT spatial obl")


if __name__ == "__main__":
    w1_head_invariance()
    w2_commit_purity()
    w3_reader_noregress()
    w4_accuracy()
    print("\nRESULT: %s" % ("PASS" if not _fail else "FAIL (%d)" % len(_fail)))
    sys.exit(1 if _fail else 0)
