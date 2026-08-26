"""Scaffold-free witness for problem the_substrate_does_not_learn_or_update_by_prediction_error.

Reproduces the HEADLINE fast, from the experiment module's own functions, using the REAL hdlab
primitives (binding.bind/unbind, bundling.bundle) for the situation-model register. No file writes.

Asserts, with bootstrap CIs, at the headline cell (D=128, moderate within-event coherence noise=1.0),
tau rate-CALIBRATED on VAL seeds (by boundary count vs the event-length prior -- NOT the DV) and
evaluated on HELD-OUT TEST seeds:

  1. GUARD: bundle recency==0 (plain-sum branch); unbind(bind(v,r),r)==v (the register identity).
  2. TASK SOLVABLE: ORACLE (true boundaries) recovers near-ceiling; NO_SEG collapses -> the DV
     actually rewards correct segmentation.
  3. HEADLINE: the brain's N400 signal -- a GRADED forward prediction error against the RUNNING
     situation-model state -- beats EVERY floor CI-separated at a MATCHED boundary rate:
       RANDOM_ratematched (the killer control that dissociated the prior write-gate),
       FORM_NOVELTY (the KILLED whole-stream-anchor proxy, at ITS OWN rate-matched tau),
       FIXED_k, and PERMUTED_SURPRISE (the info-free twin).
  4. DISSOCIATION: the NAIVE ||Delta register|| (N400_modelupdate) TIES NO_SEG -- the raw
     state-update magnitude is the form-novelty trap; the CONTENT prediction error is what carries
     the signal. This localises the F5 fix.

Run:  .venv/Scripts/python.exe verification/verify_prediction_error_event_segmentation.py
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import experiments.exp_prediction_error_event_segmentation_v1 as X


def main() -> int:
    # 1. GUARD (also asserts recency==0 and the register identity)
    X._guard()
    print("[1] GUARD ok: bundle recency==0 (plain sum); unbind(bind(v,r),r)==v")

    D, noise = X.HEADLINE["D"], X.HEADLINE["noise"]
    cal = X.calibrate_taus(D, noise, X.VAL_SEEDS, 30)
    cell = X.eval_cell(D, noise, cal["taus"], X.TEST_SEEDS, 40)
    a = cell["arms"]

    def acc(name):
        return a[name]["acc"], a[name]["lo"], a[name]["hi"], a[name]["mean_n_boundaries"]

    n_acc, n_lo, n_hi, n_nb = acc("N400_content")
    o_acc = a["ORACLE_true_boundaries"]["acc"]
    ns_acc = a["NO_SEG"]["acc"]
    print(f"    taus (rate-calibrated on VAL): {cal['taus']}")
    print(f"[2] task solvable: ORACLE={o_acc:.3f} (near ceiling) vs NO_SEG={ns_acc:.3f} (collapses)")
    assert o_acc > 0.9, f"ORACLE not near ceiling ({o_acc:.3f}) -- task not solvable, DV suspect"
    assert ns_acc < 0.5, f"NO_SEG did not collapse ({ns_acc:.3f}) -- DV does not reward segmentation"

    print(f"[3] HEADLINE N400_content acc={n_acc:.3f} [{n_lo:.3f},{n_hi:.3f}] (nb={n_nb:.1f}/{X.GOLD_RATE:.0f} gold)")
    floors = ["RANDOM_ratematched", "FORM_NOVELTY", "FIXED_k", "PERMUTED_SURPRISE"]
    strongest = max(floors, key=lambda f: a[f]["hi"])
    for f in floors:
        fa, flo, fhi, fnb = acc(f) if f in ("RANDOM_ratematched", "FORM_NOVELTY", "PERMUTED_SURPRISE") \
            else (a[f]["acc"], a[f]["lo"], a[f]["hi"], a[f]["mean_n_boundaries"])
        star = "  <== strongest floor" if f == strongest else ""
        print(f"      vs {f:20s} acc={fa:.3f} [hi={fhi:.3f}] (nb={fnb:.1f}){star}")
        assert n_lo > fhi, f"N400_content NOT CI-separated above {f}: n_lo={n_lo:.3f} {f}_hi={fhi:.3f}"
    print(f"    -> N400_content lower-CI {n_lo:.3f} > every floor's upper-CI "
          f"(strongest = {strongest} @ {a[strongest]['hi']:.3f}), at a matched boundary rate")

    # 4. dissociation: naive ||Delta register|| ties NO_SEG
    mu_acc, mu_lo, mu_hi, mu_nb = acc("N400_modelupdate")
    ns_lo, ns_hi = a["NO_SEG"]["lo"], a["NO_SEG"]["hi"]
    ties = not (mu_lo > ns_hi or ns_lo > mu_hi)
    print(f"[4] N400_modelupdate acc={mu_acc:.3f} (nb={mu_nb:.1f}) vs NO_SEG {ns_acc:.3f} -> "
          f"{'TIE (raw ||Delta model|| is the form-novelty trap; CONTENT-PE carries it)' if ties else 'DIFFERENT'}")
    assert ties, "expected naive ||Delta register|| to tie NO_SEG (it should never fire)"

    print("\nPASS: prediction-error event-segmentation witness -- the brain's GRADED forward "
          "prediction error against the running situation-model state segments discourse and gets "
          "the right content into memory, CI-separated over every floor at a matched boundary rate; "
          "the naive ||Delta model|| does not. A missing, brain-faithful UPDATE signal, built.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
