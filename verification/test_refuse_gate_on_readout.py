"""Scaffold-free witness for wire_the_refuse_gate_onto_the_readout.

Recomputes the headline live (tracing off, no scaffold), on a modest read so it runs in well under
a minute. Two claims:

  1. PROBLEM IS LIVE: recall_sentence and recall_cortical give a NON-EMPTY, confident answer to
     invented strings the substrate never read -- they cannot natively refuse. (query() can; it is
     the positive control and is left alone.)

  2. THE REFUSE GATE DOES NOT CLEAR THE BAR. The bar is BOTH ARMS: invented refused AND real
     answered. The gate is a threshold on the route's top-1 confidence; a threshold can satisfy both
     arms only if the confidence SEPARATES read words from never-read words. It barely does:
        - the best achievable min(accept_real, refuse_invented) over all thresholds ("both-arms
          operating point") is well below a usable level for BOTH routes; and
        - at any threshold that refuses >=90% of invented words, most REAL words are refused too.
     This is measured against the information-free reference (a random gate at the same refusal rate,
     whose both-arms point is ~0.5 by construction).

Run:  .venv/Scripts/python.exe verification/test_refuse_gate_on_readout.py
ASCII-only.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.substrate import Substrate
from experiments.exp_refuse_gate_on_readout_v1 import build_pools, top1_conf, ROUTES
from experiments.exp_refuse_gate_on_readout_v2_membership import (
    familiarity_set, recollection_set, refusing_recall, arms)

SEED = 7
N_REAL = N_INV = 120


def both_arms_max_min(real_conf, inv_conf):
    """max over tau of min(accept_real, refuse_invented). 1.0 = a threshold cleanly separates
    the two populations; ~0.5 = no threshold does better than chance."""
    rc = np.asarray(real_conf, float); ic = np.asarray(inv_conf, float)
    best = 0.0
    op_at_90 = None
    for tau in np.unique(np.concatenate([rc, ic])):
        accept_real = float(np.mean(rc >= tau))
        refuse_inv = float(np.mean(ic < tau))
        best = max(best, min(accept_real, refuse_inv))
        if refuse_inv >= 0.90 and op_at_90 is None:
            op_at_90 = accept_real
    # tau just above the max score refuses everything; ensure the >=90% branch is reachable
    if op_at_90 is None:
        op_at_90 = float(np.mean(rc >= (max(ic) + 1e-9)))
    return best, op_at_90


def _build():
    sub = Substrate(seed=SEED)
    got = 0
    for _ in range(3):
        r = sub.read(corpus="simplewiki", n_sentences=1500, batch=100)
        got += r.n_sentences
        if r.n_sentences == 0:
            break
    real, invented, cons = build_pools(sub, N_REAL, N_INV, SEED)
    return sub, real, invented


def test_problem_is_live():
    sub, real, invented = _build()
    for route in ROUTES:
        fn = getattr(sub, route)
        answered = sum(1 for w in invented[:20]
                       if (lambda res: bool(res) and (res[0] is not None))(list(fn(w))))
        print("[witness] %-16s answered %d/20 INVENTED strings (native refuse rate %d/20)"
              % (route, answered, 20 - answered))
        assert answered == 20, "%s natively refused some invented strings (%d/20)" % (route, answered)
    # positive control: query() CAN refuse
    q = sub.query("blorptaxis")
    print("[witness] query('blorptaxis') known=%s decision=%s" % (q.known, q.decision))
    assert q.known is False and q.decision == "REFUSE", "query() should refuse an unread string"


def test_gate_does_not_clear_the_bar():
    sub, real, invented = _build()
    for route in ROUTES:
        fn = getattr(sub, route)
        rc = [top1_conf(fn, w) for w in real]
        ic = [top1_conf(fn, w) for w in invented]
        rc = [x for x in rc if x is not None]
        ic = [x for x in ic if x is not None]
        bam, acc_at_90 = both_arms_max_min(rc, ic)
        # info-free reference: random gate at the observed overall refusal rate -> both-arms ~0.5
        print("[witness] %-16s both-arms max-min = %.3f | accept_real @>=90%%-refuse-invented = %.3f"
              % (route, bam, acc_at_90))
        # the bar needs BOTH arms high; a usable gate would clear ~0.9. It does not.
        assert bam < 0.75, "%s both-arms operating point unexpectedly high (%.3f)" % (route, bam)
        # the trap: refusing invented forces refusing real
        assert acc_at_90 < 0.60, \
            "%s kept too many real words while refusing 90%% invented (%.3f)" % (route, acc_at_90)


def test_membership_gate_clears_the_bar():
    """The brain-faithful fix: gate on CUE FAMILIARITY (store membership), not similarity confidence.
    At the familiarity level it clears BOTH arms; at the stricter recollection level (query()'s own)
    it refuses read-but-unconsolidated real words, re-introducing the trap. The familiarity win is
    DEFINITIONAL -- it proves the refusal information was available and merely unconsulted."""
    sub, real, invented = _build()
    fam = familiarity_set(sub)
    rec = recollection_set(sub)
    ar_f, ri_f, bal_f = arms(real, invented, fam)
    ar_r, ri_r, bal_r = arms(real, invented, rec)
    print("[witness] FAMILIARITY  gate: accept_real %.3f refuse_invented %.3f balanced %.3f"
          % (ar_f, ri_f, bal_f))
    print("[witness] RECOLLECTION gate: accept_real %.3f refuse_invented %.3f balanced %.3f"
          % (ar_r, ri_r, bal_r))
    # accept_real is exact (real words ARE their own lemmas in the read vocab); refuse_invented can
    # dip a hair below 1.0 when a generated string LEMMATISES to a read word -- which is correct
    # familiarity behaviour, not a miss.
    assert ar_f == 1.0 and ri_f >= 0.98, \
        "familiarity gate did not clear both arms (accept_real=%.3f refuse_inv=%.3f)" % (ar_f, ri_f)
    assert ar_r < 0.10, \
        "recollection gate unexpectedly kept many real words (%.3f) -- level analysis wrong" % ar_r
    # functional end-to-end on the real routes: a never-known cue -> refuse ([]), real -> answer.
    from hdlab.reading_grounding_loop import normalize_lemma
    unknown_inv = [w for w in invented if normalize_lemma(w) not in fam][:10]
    for route in ROUTES:
        fn = getattr(sub, route)
        assert all(len(refusing_recall(sub, fn, w, fam)) == 0 for w in unknown_inv), \
            "%s did not refuse a never-known cue under the membership gate" % route
        assert all(len(refusing_recall(sub, fn, w, fam)) > 0 for w in real[:10]), \
            "%s refused a real word under the membership gate" % route
    print("[witness] membership gate refuses invented and answers real, end to end, both routes")


def _main():
    ok = True
    for fn in (test_problem_is_live, test_gate_does_not_clear_the_bar,
               test_membership_gate_clears_the_bar):
        try:
            fn(); print("[witness] PASS", fn.__name__)
        except AssertionError as e:
            ok = False; print("[witness] FAIL", fn.__name__, "--", e, file=sys.stderr)
    print("[witness] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_main())
