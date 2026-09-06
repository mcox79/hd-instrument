"""LANDING WITNESS for the FORWARD-EVENT-PREDICTION organ (hdlab/generalized_event_knowledge.py) + its
live read()-time wire into hdlab/situation_reader.py (sm.predict_next_event / sm.forward_prediction).
Self-contained, ASCII, deterministic, capped threads. Proves the LANDED organ -- not the experiment cells --
carries the validated capability, that the wire is a PURE ADD (every existing situation-model dimension
byte-identical off vs on), and that the capability is now LIVE through a real read().

  W1  PROMOTION FAITHFUL: the promoted hdlab.generalized_event_knowledge reproduces the reference forward-
      predictor result on Story Cloze (val, from the pinned local corpus -- NO HF network): the forward GEK
      projection beats the majority-continuation floor CI-separated (~0.578-0.592 vs 0.514), the cross-context
      info-free twin COLLAPSES to chance (~0.49), and a calibrated precision (1 - normalized entropy) earns
      RISING selective accuracy on the most-confident quartile.
  W2  ADDITIVE / BYTE-SAFE: a live read of a couple of docs with track_prediction ON is byte-identical to OFF
      on every existing SituationModel dimension; the readout is lazy (sm.forward_prediction stays None until
      invoked), and OFF is the pre-landing reader (no sm.predict_next_event bound).
  W3  LIVE CONSUMER: sm.predict_next_event(...) returns a forward prediction + calibrated precision through the
      LIVE reader on a sample (the capability is now live), and ABSTAINS cleanly (returns None, never raises)
      when the store asset is absent.

Run: .venv/Scripts/python.exe verification/test_forward_projection_landing.py
"""
import json
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

import hdlab.generalized_event_knowledge as GEK
from hdlab.generalized_event_knowledge import GEKProjector, lemmatize, available
from hdlab.graded_competition import graded_pick
from hdlab.situation_reader import SituationReader, _write_temp_conll

P = 0


def check(name, cond, detail=""):
    global P
    assert cond, "FAIL %s -- %s" % (name, detail)
    P += 1
    print("  ok  %s  %s" % (name, detail))


def _boot_ci(x, B=2000, seed=0):
    x = np.asarray(x, float); rr = np.random.default_rng(seed)
    bs = np.array([x[rr.integers(0, len(x), len(x))].mean() for _ in range(B)])
    return float(x.mean()), (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))


def _boot_margin_lo(a, b, B=2000, seed=1):
    a = np.asarray(a, float); b = np.asarray(b, float); n = len(a); rr = np.random.default_rng(seed)
    bs = np.array([a[i].mean() - b[i].mean() for i in (rr.integers(0, n, n) for _ in range(B))])
    return float(a.mean() - b.mean()), float(np.percentile(bs, 2.5))


print("=" * 92)
print("LANDING WITNESS: forward-event-prediction organ + the live sm.predict_next_event read()-time consumer")
print("=" * 92)

check("W0-asset", available(),
      "hdlab.generalized_event_knowledge loads the frozen forward-transition store (%s)" % GEK.GEK_ASSET)

# --------------------------------------------------------------------------- W1: promotion faithful
org = GEKProjector()
rows = []
with open(os.path.join(_REPO, "data/corpora/story_cloze/validation.jsonl"), encoding="utf-8") as fh:
    for line in fh:
        rows.append(json.loads(line))
n = len(rows)
items = []
for r in rows:
    ctx = []
    for j in range(1, 5):
        ctx += lemmatize(r["input_sentence_%d" % j])
    items.append((ctx, lemmatize(r["sentence_quiz1"]), lemmatize(r["sentence_quiz2"]),
                  int(r["answer_right_ending"])))


def _precision(s1, s2):
    return 1.0 - float(graded_pick({"cue": [s1, s2]}, {"cue": 1.0}, gain=2.0)["entropy"])


fwd_c, fwd_p, twin_c = [], [], []
for k, (ctx, e1, e2, g) in enumerate(items):
    s1, s2 = org.score(ctx, e1), org.score(ctx, e2)
    fwd_c.append(int((1 if s1 >= s2 else 2) == g))
    fwd_p.append(_precision(s1, s2))
    tctx = items[(k + 971) % n][0]                       # cross-context: a different story's context
    t1, t2 = org.score(tctx, e1), org.score(tctx, e2)
    twin_c.append(int((1 if t1 >= t2 else 2) == g))
fwd_c = np.array(fwd_c, float); fwd_p = np.array(fwd_p, float); twin_c = np.array(twin_c, float)
from collections import Counter
labels = [it[3] for it in items]
maj = Counter(labels).most_common(1)[0][0]
maj_c = np.array([int(l == maj) for l in labels], float)

fwd_acc, fwd_cis = _boot_ci(fwd_c)
maj_acc, _ = _boot_ci(maj_c)
mdiff, mlo = _boot_margin_lo(fwd_c, maj_c)
check("W1-beats-majority-CI-sep", n == 1871 and mlo > 0.0 and 0.575 <= fwd_acc <= 0.605,
      "forward GEK=%.4f [%.4f,%.4f] vs majority=%.4f ; margin=%+.4f (95%% lo=%+.4f > 0)"
      % (fwd_acc, fwd_cis[0], fwd_cis[1], maj_acc, mdiff, mlo))

twin_acc, twin_ci = _boot_ci(twin_c)
check("W1-cross-context-twin-collapses", twin_acc < 0.52 and (fwd_acc - twin_acc) > 0.06,
      "twin=%.4f [%.4f,%.4f] vs mechanism=%.4f (info-free loses -> the projection USES this story)"
      % (twin_acc, twin_ci[0], twin_ci[1], fwd_acc))

order = np.argsort(-fwd_p)
sel_all = float(fwd_c.mean())
q = max(1, int(round(0.25 * n)))
sel_q = float(fwd_c[order[:q]].mean())
half = max(1, int(round(0.5 * n)))
sel_h = float(fwd_c[order[:half]].mean())
check("W1-precision-selective-rises", sel_q > sel_all + 0.01 and sel_h >= sel_all,
      "selective acc @100%%=%.4f -> @50%%=%.4f -> @25%%=%.4f (calibrated precision defers correctly)"
      % (sel_all, sel_h, sel_q))

# --------------------------------------------------------------------------- W2: additive / byte-safe
def _dim_signature(sm):
    """Canonical serialization of every LOAD-BEARING situation-model dimension EXCEPT the new prediction one."""
    return {
        "entities": [tuple(e.heads) for e in sm.entities],
        "events": [(e.predicate, e.agent, e.patient, e.tense, e.subj_role, e.obj_role, e.affect)
                   for e in sm.events],
        "coref": [(r.pronoun, r.sent_idx, r.resolved_cluster, r.correct) for r in sm.coref_resolutions],
        "causal": [(c.sent_idx, c.cause, c.outcome, c.method) for c in sm.causal_links],
        "timeline_order": list(sm.timeline_order),
        "suppressed": [(s.sent_idx, s.predicate) for s in sm.suppressed_predicates],
        "entity_states": [(s.holder, s.property, s.htype) for s in sm.entity_states],
        "bridges": list(sm.bridges), "senses": list(sm.senses),
        "scalars": (sm.n_targets, sm.n_xsent_targets, sm.coref_acc, sm.coref_xsent_acc,
                    bool(sm.locations is not None), bool(sm.world_state is not None),
                    bool(sm.goal_register is not None), bool(sm.affect_register is not None),
                    callable(getattr(sm, "wants", None)), callable(getattr(sm, "bridge", None))),
    }


doc = [["The", "sailor", "loved", "his", "ship", "."],
       ["He", "repaired", "the", "hull", "after", "the", "storm", "."],
       ["The", "captain", "feared", "the", "reef", "."]]
_rows = [(si, wi, tok, "-") for si, toks in enumerate(doc) for wi, tok in enumerate(toks)]
_path = _write_temp_conll(_rows)
try:
    sm_on = SituationReader().read(_path)                          # track_prediction ON (default)
    sm_off = SituationReader(track_prediction=False).read(_path)   # the pre-landing reader
finally:
    os.remove(_path)

sig_on, sig_off = _dim_signature(sm_on), _dim_signature(sm_off)
mismatch = [k for k in sig_on if sig_on[k] != sig_off[k]]
check("W2-additive-byte-identical", not mismatch,
      "all %d existing dimensions byte-identical ON vs OFF (mismatches: %s)" % (len(sig_on), mismatch or "none"))
check("W2-lazy-forward_prediction-None", sm_on.forward_prediction is None,
      "sm.forward_prediction is None until predict_next_event is invoked (zero read-time cost)")
check("W2-off-is-pre-landing", (not callable(getattr(sm_off, "predict_next_event", None)))
      and sm_off.forward_prediction is None,
      "track_prediction=False -> no sm.predict_next_event bound (== the pre-landing reader)")
check("W2-on-adds-only-prediction", callable(getattr(sm_on, "predict_next_event", None)),
      "track_prediction=True adds ONLY sm.predict_next_event (a pure additive read-only projection)")

# --------------------------------------------------------------------------- W3: live consumer
# Use a real Story Cloze item through the LIVE reader: build the 4-sentence context doc, then ask the reader to
# forward-project which of the two candidate endings comes next. Proves the capability is live end-to-end.
r0 = rows[0]
ctx_doc = [_toks for _toks in
           [str(r0["input_sentence_%d" % j]).replace(".", " .").split() for j in range(1, 5)]]
_rows3 = [(si, wi, tok, "-") for si, toks in enumerate(ctx_doc) for wi, tok in enumerate(toks)]
_p3 = _write_temp_conll(_rows3)
try:
    sm3 = SituationReader().read(_p3)
finally:
    os.remove(_p3)

cands = [r0["sentence_quiz1"], r0["sentence_quiz2"]]
fp = sm3.predict_next_event(candidates=cands)
check("W3-live-discrimination", fp is not None and fp.picked in (0, 1) and 0.0 <= fp.precision <= 1.0
      and abs(sum(fp.distribution) - 1.0) < 1e-6 and sm3.forward_prediction is fp,
      "sm.predict_next_event([e1,e2]) -> picked=%s precision=%.3f dist=%s cue=%s (forward projection is LIVE)"
      % (None if fp is None else fp.picked, -1 if fp is None else fp.precision,
         None if fp is None else [round(x, 3) for x in fp.distribution],
         None if fp is None else fp.cue_scores))
# WIRE FAITHFUL: the live projection's pick == the promoted organ's own direct-score pick on this context
# (proves the read()-time wire routes context+candidates to the store faithfully). NOTE: on THIS canonical
# item the mechanism (correctly, per the SOLVED) prefers the topically-similar WRONG ending "He joined a gang"
# -- it repeats "gang" from the context, the documented topically-matched-wrong-ending case the pure-association
# GEK cue is fooled by; a per-item correctness anchor would be testing a KNOWN located-negative failure, so we
# assert wire-faithfulness (the aggregate 0.593 accuracy is W1) rather than a per-item outcome.
_g1, _g2 = org.score(items[0][0], items[0][1]), org.score(items[0][0], items[0][2])
_raw_pick = 0 if _g1 >= _g2 else 1
check("W3-live-wire-faithful", fp is not None and fp.picked == _raw_pick,
      "live pick=%d == promoted-organ direct-score pick=%d (gek %.2f vs %.2f; item 0 is the documented "
      "topically-similar wrong-ending case)" % (fp.picked, _raw_pick, _g1, _g2))

# generative mode (no candidates) -> top-k forward-expected content, calibrated precision
fpg = sm3.predict_next_event()
check("W3-live-generative", fpg is not None and len(fpg.expected) >= 1 and 0.0 <= fpg.precision <= 1.0,
      "sm.predict_next_event() -> top forward-expected content %s (precision=%.3f)"
      % ([w for w, _ in fpg.expected[:5]], fpg.precision))

# ABSTAIN CLEANLY when the store asset is absent -- simulate by forcing the missing-store path (then restore)
_saved_store, _saved_missing = GEK._STORE, GEK._STORE_MISSING
GEK._STORE, GEK._STORE_MISSING = None, True
try:
    _p4 = _write_temp_conll(_rows3)
    try:
        sm4 = SituationReader().read(_p4)
    finally:
        os.remove(_p4)
    fp_absent = sm4.predict_next_event(candidates=cands)
    check("W3-abstains-when-asset-absent", fp_absent is None and sm4.forward_prediction is None,
          "with the store asset absent, sm.predict_next_event returns None (abstains cleanly, never raises)")
finally:
    GEK._STORE, GEK._STORE_MISSING = _saved_store, _saved_missing

print("=" * 92)
print("LANDING WITNESS PASS: %d/%d" % (P, P))
print("=" * 92)
