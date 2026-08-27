"""Witness for hdlab.semantic_control (landed 2026-08-27).

Self-contained construction proof of the LIFG/pMTG semantic-control MECHANISM (no meaning-infra
dependency): on synthetic sense-selection items where the frequency-DOMINANT candidate is
sometimes wrong (a competitor fits the context better), the gold-blind CONFLICT signal detects
"the prior is wrong", and conflict-gated GRADED suppression of the prior flips the answer to the
context-appropriate competitor on the OVERRIDE items -- WITHOUT false-firing on the DOMINANT
items. Can-fail: an info-free shuffled-conflict twin must NOT improve, and the trigger's AUC must
beat its shuffled twin. The full-corpus validation is the solver's test_context_override_frequency.py.
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.semantic_control import SemanticControl, conflict  # noqa: E402


def _auc(scores, labels):
    scores = np.asarray(scores, dtype=np.float64)
    labels = np.asarray(labels, dtype=np.int64)
    pos = scores[labels == 1]
    neg = scores[labels == 0]
    if pos.size == 0 or neg.size == 0:
        return 0.5
    # rank-based AUC
    order = np.argsort(np.concatenate([pos, neg]), kind="mergesort")
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(1, order.size + 1)
    r_pos = ranks[: pos.size].sum()
    return float((r_pos - pos.size * (pos.size + 1) / 2.0) / (pos.size * neg.size))


def main() -> int:
    rng = np.random.default_rng(7)
    N, K, PRIOR = 600, 4, 0
    FREQ_BOOST = 0.8  # the prior's frequency-prior advantage in the base read-out (must let it swamp uncontrolled)
    GAMMA = 1.5

    base_scores, coherences, true_idx, is_override = [], [], [], []
    for i in range(N):
        override = bool(rng.integers(0, 2))
        coh = rng.uniform(0.20, 0.35, size=K)  # baseline context-coherence
        if override:
            comp = int(rng.integers(1, K))          # a non-prior competitor fits best
            coh[comp] = rng.uniform(0.70, 0.90)
            coh[PRIOR] = rng.uniform(0.15, 0.30)    # the prior does NOT fit
            gold = comp
        else:
            coh[PRIOR] = rng.uniform(0.70, 0.90)    # the prior fits (dominant is correct)
            gold = PRIOR
        # base read-out = context coherence + the prior's frequency boost (so uncontrolled argmax
        # picks the prior even when a competitor coheres better -- "the prior swamps")
        sc = coh.copy()
        sc[PRIOR] += FREQ_BOOST
        base_scores.append(sc); coherences.append(coh); true_idx.append(gold)
        is_override.append(1 if override else 0)

    base_scores = np.array(base_scores); coherences = np.array(coherences)
    true_idx = np.array(true_idx); is_override = np.array(is_override)
    ov = is_override == 1
    dom = is_override == 0

    # [1] the gold-blind conflict predicts "the prior is wrong" (override), beating a shuffled twin
    confs = np.array([conflict(coherences[i], PRIOR) for i in range(N)])
    perm = rng.permutation(N)
    confs_tw = np.array([conflict(coherences[perm[i]], PRIOR) for i in range(N)])
    auc = _auc(confs, is_override); auc_tw = _auc(confs_tw, is_override)
    print(f"[1] conflict predicts override: AUC={auc:.3f} vs shuffled-twin {auc_tw:.3f}")
    assert auc > auc_tw + 0.15 and auc > 0.75, "[witness] conflict trigger does not beat its twin"

    # calibrate theta on the conflict distribution. The operating point is POPULATION-dependent:
    # the validated headline is the 80th pct on the real 63%-dominant SemCor population; this synthetic
    # is ~50/50 override/dominant, so the cluster boundary is the median.
    sc_ctrl = SemanticControl(gamma=GAMMA).calibrate(confs, quantile=0.50)

    # [2] uncontrolled (argmax of the base read-out) vs conflict-gated suppression
    uncontrolled = np.array([int(np.argmax(base_scores[i])) for i in range(N)])
    controlled = np.array([sc_ctrl.resolve(base_scores[i], coherences[i], PRIOR)[0] for i in range(N)])
    acc_un_ov = float((uncontrolled[ov] == true_idx[ov]).mean())
    acc_ct_ov = float((controlled[ov] == true_idx[ov]).mean())
    acc_un_dom = float((uncontrolled[dom] == true_idx[dom]).mean())
    acc_ct_dom = float((controlled[dom] == true_idx[dom]).mean())
    print(f"[2] OVERRIDE acc: uncontrolled {acc_un_ov:.3f} -> controlled {acc_ct_ov:.3f} "
          f"(+{acc_ct_ov - acc_un_ov:.3f}); DOMINANT acc {acc_un_dom:.3f} -> {acc_ct_dom:.3f}")
    assert acc_ct_ov > acc_un_ov + 0.10, "[witness] semantic control did not lift the override cases"
    assert acc_ct_dom >= acc_un_dom - 0.02, "[witness] semantic control false-fired on the dominant cases"

    # [3] info-free twin: suppress on a SHUFFLED conflict -> must NOT lift the override cases
    twin = SemanticControl(theta=sc_ctrl.theta, gamma=GAMMA)
    controlled_tw = np.array([int(np.argmax(twin.suppressed_scores(base_scores[i], PRIOR, confs_tw[i])))
                              for i in range(N)])
    acc_tw_ov = float((controlled_tw[ov] == true_idx[ov]).mean())
    print(f"[3] info-free shuffled-conflict twin OVERRIDE acc {acc_tw_ov:.3f} (must not beat controlled {acc_ct_ov:.3f})")
    assert acc_tw_ov < acc_ct_ov - 0.05, "[witness] a shuffled-conflict twin lifted the cases -> the gain is not the real trigger"

    # [4] default-safe: an UNCALIBRATED controller is exactly argmax(base scores) -- no behaviour change
    noop = SemanticControl()  # theta None
    same = all(noop.resolve(base_scores[i], coherences[i], PRIOR)[0] == int(np.argmax(base_scores[i]))
               for i in range(N))
    print(f"[4] default-safe: uncalibrated controller == argmax(scores) for all items: {same}")
    assert same, "[witness] uncalibrated semantic control changed behaviour (not default-safe)"

    print("\nALL WITNESS ASSERTIONS PASSED -- the gold-blind conflict trigger detects when the prior is")
    print("wrong (AUC >> shuffled twin), conflict-gated graded suppression flips the OVERRIDE cases to the")
    print("context-appropriate competitor without false-firing on the dominant cases, an info-free twin does")
    print("not, and an uncalibrated controller is a byte-safe no-op.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
