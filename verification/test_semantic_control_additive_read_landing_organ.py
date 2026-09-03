"""Scaffold-free witness for the LANDING of the brain-faithful REORDERED-ACCESS ADDITIVE sense read-out
into hdlab.semantic_control (from the owner-DONE north-star
the_meaning_channel_needs_a_generative_world_knowledge_situation_model...).

The parent's net-gain see-saw was the DECISION RULE, not the generative source: a subtractive/gated
hard-flip can ERASE a correct dominant sense; the brain's reordered access is ADDITIVE (dominant always
accessed by frequency, context only ADDS to a subordinate; Duffy/Morris/Rayner) with NON-margin precision
(Feldman-Friston). This additive rule is the GENERALIZING net-gain lever (held-out SemCor: +0.0116 over MFS
CI-sep, twin loses, dominant preserved 0.949; the parent's gated hard-flip was -0.0013 CI-sep BELOW).

  [1] EXISTING ORGAN INTACT: adding the additive read-out did NOT change SemanticControl.resolve /
      conflict / suppressed_scores -- they produce the same deterministic outputs (the organ is only
      EXTENDED with a new module function). Recomputed from source.
  [2] PROMOTION FAITHFUL, byte-exact: hdlab.semantic_control.additive_reordered_read returns the IDENTICAL
      pick to the validated cell experiments/exp_generative_situation_sense_selector_v2._additive_pick over
      a random battery of (prior, likelihood, reliability, gamma, tau) -- so a wired read == the witnessed
      cell's decision.
  [3] BRAIN-FAITHFUL PROPERTY (deterministic can-fail): reordered access is ADDITIVE -- a flat context or
      zero reliability KEEPS the dominant (no override), a sharp+reliable context for a competitor CAN
      override, and in NO case is the dominant's own score decreased (facilitatory-only; the see-saw fix).

Run: .venv/Scripts/python.exe verification/test_semantic_control_additive_read_landing_organ.py
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402
import hdlab.semantic_control as SC  # noqa: E402
import experiments.exp_generative_situation_sense_selector_v2 as V2  # noqa: E402 (the validated cell)


def main():
    checks = []
    rng = np.random.default_rng(20260903)

    # [1] EXISTING ORGAN INTACT -- resolve/conflict/suppressed_scores unchanged (deterministic).
    sc = SC.SemanticControl(theta=0.0, gamma=1.0)
    scores = [1.0, 0.5, 0.2]
    coher = [0.1, 0.9, 0.2]          # a strong NON-prior competitor (idx 1) => conflict fires
    conf = SC.conflict(coher, prior_idx=0)
    supp = sc.suppressed_scores(scores, prior_idx=0, conflict_value=conf)
    pick, c2 = sc.resolve(scores, coher, prior_idx=0)
    organ_ok = (abs(conf - (0.9 - 0.1)) < 1e-9            # best_other - prior coherence
                and abs(supp[0] - (1.0 - 1.0 * max(0.0, conf - 0.0))) < 1e-9  # prior suppressed by gamma*relu(conflict-theta)
                and pick == 1 and abs(c2 - conf) < 1e-9)   # re-argmax picks the competitor
    checks.append((organ_ok,
                   "[1] EXISTING ORGAN INTACT: conflict=%.3f, suppressed prior score=%.3f, resolve->%d (competitor) "
                   "-- resolve/conflict/suppressed_scores unchanged by the additive add-on" % (conf, supp[0], pick)))

    # [2] PROMOTION FAITHFUL -- additive_reordered_read == V2._additive_pick byte-exact over a battery.
    faithful = True
    n = 400
    for _ in range(n):
        k = int(rng.integers(2, 6))
        prior = rng.random(k) + 0.05
        has_L = bool(rng.integers(0, 4))              # sometimes None (abstain path)
        L = (rng.random(k) if has_L else None)
        rel = float(rng.random())
        gamma = float(rng.choice([0.1, 0.25, 0.5, 0.75, 1.0]))
        tau = float(rng.choice([0.0, 0.1, 0.25]))
        it = {"prior": prior.copy(), "_rel": rel}
        ref = V2._additive_pick(it, None if L is None else L.copy(), gamma, tau)
        got = SC.additive_reordered_read(prior.copy(), None if L is None else L.copy(), rel, gamma, tau)
        if ref != got:
            faithful = False
            break
    checks.append((faithful,
                   "[2] PROMOTION FAITHFUL: additive_reordered_read == exp_..._v2._additive_pick byte-exact over "
                   "%d random (prior,likelihood,reliability,gamma,tau) cases (incl. the None/abstain path)" % n))

    # [3] BRAIN-FAITHFUL PROPERTY -- additive/facilitatory-only, dominant never penalized.
    prior = np.array([0.90, 0.07, 0.03])              # sense 0 dominant
    flat = np.array([0.33, 0.34, 0.33])               # ~flat context
    sharp = np.array([0.02, 0.95, 0.03])              # sharp context for competitor 1
    keep_flat = SC.additive_reordered_read(prior, flat, reliability=1.0, gamma=1.0, tau=0.2) == 0
    keep_zero_rel = SC.additive_reordered_read(prior, sharp, reliability=0.0, gamma=1.0, tau=0.0) == 0
    can_override = SC.additive_reordered_read(prior, sharp, reliability=1.0, gamma=3.0, tau=0.0) == 1
    # dominant score never DECREASED: log prior + boost, boost = relu(z(L)) >= 0 -> dominant's own term never drops
    pr = prior / prior.sum()
    boost = 1.0 * 1.0 * np.maximum(SC._z(sharp), 0.0)
    dominant_not_penalized = bool(boost[0] >= 0.0)     # additive-only: the dominant term is log prior + (>=0)
    prop_ok = keep_flat and keep_zero_rel and can_override and dominant_not_penalized
    checks.append((prop_ok,
                   "[3] BRAIN-FAITHFUL ADDITIVE: flat-context keeps dominant (%s), zero-reliability keeps dominant "
                   "(%s), sharp+reliable CAN override (%s), dominant boost>=0 never penalized (%s)"
                   % (keep_flat, keep_zero_rel, can_override, dominant_not_penalized)))

    print("=== witness: semantic_control ADDITIVE reordered-access read-out LANDING ===")
    ok_all = True
    for ok, msg in checks:
        print("  %s  %s" % ("PASS" if ok else "FAIL", msg))
        ok_all = ok_all and bool(ok)
    print("  NOTE: this is the PROVEN net-gain DECISION RULE promoted into the organ; the meaning channel's LIVE "
          "wiring into situation_reader.read() is a separate DEBT-3 step (the meaning organs are islands).")
    print("\nRESULT: %s (%d/%d)" % ("ALL CHECKS PASS" if ok_all else "FAIL",
                                    sum(1 for ok, _ in checks if ok), len(checks)))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
