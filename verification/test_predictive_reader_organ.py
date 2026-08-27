"""Witness for hdlab.predictive_reader.PredictiveReader (landed 2026-08-26).

Self-contained construction proof of the forward-prediction MECHANISM over the substrate's REAL
grounded space (no QA-SRL dependency): a verb whose training arguments share a grounded-feature
profile pre-activates a centroid that anticipates a HELD-OUT argument of that verb better than a
WRONG-VERB centroid does. This is the can-fail core (predictive beats the info-free wrong-verb
twin); the full REAL-corpus validation is the solver's verify_predictive_reader.py (8/8).

Can-fail: if the verb->centroid map carried no selectional-preference signal, the wrong-verb twin
would tie -- it does not. Also checks the surprisal is graded (-log P) and that PRECISION
discriminates a tight verb from a diffuse one (Friston constraint strength).
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.grounded_similarity import grounded_vector  # noqa: E402
from hdlab.predictive_reader import PredictiveReader  # noqa: E402

# Verb classes with DISTINCT expected-argument grounded-feature profiles (real concrete nouns).
CLASSES = {
    "eat":   ["apple", "bread", "cake", "meat", "cheese", "egg", "soup", "fruit", "corn", "rice"],
    "drive": ["car", "truck", "bus", "train", "wagon", "cart", "boat", "ship"],
    "read":  ["book", "letter", "note", "paper", "page", "story", "poem", "sign"],
}
ROLE = "patient"


def _covered(words):
    return [w for w in words if grounded_vector(w) is not None]


def main() -> int:
    rng = np.random.default_rng(7)

    covered = {v: _covered(ws) for v, ws in CLASSES.items()}
    for v, ws in covered.items():
        assert len(ws) >= 4, f"[witness] too few grounded-covered args for '{v}': {ws} (pick better words)"
    verbs = list(covered.keys())

    # Leave-one-out: for each (verb, held-out arg), fit on all OTHER args (all verbs), then score
    # the held-out arg under the RIGHT verb centroid vs a WRONG-verb centroid, among candidates
    # drawn one-per-class (so the classes must be separated for the right verb to win).
    pred_surp, twin_surp, correct = [], [], 0
    n_items = 0
    for vi, verb in enumerate(verbs):
        wrong_verb = verbs[(vi + 1) % len(verbs)]
        for held in covered[verb]:
            train = [(vv, ROLE, a) for vv in verbs for a in covered[vv] if not (vv == verb and a == held)]
            pr = PredictiveReader().fit(train)
            # candidates: the held-out true arg + one distractor from each OTHER class
            cands = [held]
            for ov in verbs:
                if ov == verb:
                    continue
                pool = [a for a in covered[ov] if a != held]
                if pool:
                    cands.append(pool[int(rng.integers(0, len(pool)))])
            s_pred = pr.surprisal(verb, ROLE, held, cands)
            s_twin = pr.surprisal(wrong_verb, ROLE, held, cands)
            if s_pred is None or s_twin is None:
                continue
            pred_surp.append(s_pred)
            twin_surp.append(s_twin)
            # acc@1: is the true arg the lowest-surprisal candidate under the RIGHT verb?
            cand_s = [pr.surprisal(verb, ROLE, c, cands) for c in cands]
            if all(x is not None for x in cand_s) and int(np.argmin(cand_s)) == cands.index(held):
                correct += 1
            n_items += 1

    assert n_items >= 12, f"[witness] too few test items ({n_items})"
    m_pred, m_twin = float(np.mean(pred_surp)), float(np.mean(twin_surp))
    acc = correct / n_items
    chance = 1.0 / (1 + (len(verbs) - 1))  # 1 / n_candidates

    print(f"[1] PREDICTIVE surprisal {m_pred:.3f} < WRONG-VERB twin {m_twin:.3f} "
          f"(margin {m_twin - m_pred:+.3f}) over n={n_items}")
    assert m_pred < m_twin - 0.05, "[witness] predictive did NOT beat the wrong-verb twin"

    print(f"[2] acc@1 (right verb picks the true arg) = {acc:.3f} vs chance {chance:.3f}")
    assert acc > chance + 0.10, "[witness] predictive acc@1 not above chance"

    # [3] PRECISION discriminates a tight verb (all edible) from a diffuse one (mixed args).
    tight = [("eat", ROLE, a) for a in covered["eat"]]
    diffuse_args = (covered["eat"][:2] + covered["drive"][:2] + covered["read"][:2])
    diffuse = [("misc", ROLE, a) for a in diffuse_args]
    pr2 = PredictiveReader().fit(tight + diffuse)
    p_tight = pr2.precision("eat", ROLE)
    p_diffuse = pr2.precision("misc", ROLE)
    print(f"[3] precision tight('eat')={p_tight:.3f} > diffuse('misc')={p_diffuse:.3f}")
    assert p_tight is not None and p_diffuse is not None and p_tight > p_diffuse + 0.02, \
        "[witness] precision did not discriminate tight vs diffuse selectional preference"

    # [4] default-safe: predict falls back to the base-rate role centroid for an unseen verb.
    assert pr2.predict("neverseenverb", ROLE) is not None, "[witness] role base-rate fallback missing"
    assert pr2.predict("eat", "neverseenrole") is None, "[witness] unseen role should be None"
    print("[4] base-rate fallback + unseen-role handling OK")

    print("\nALL WITNESS ASSERTIONS PASSED -- the forward predictor anticipates held-out args via the")
    print("verb-role selectional-preference centroid, beats the info-free wrong-verb twin, and its")
    print("precision tracks selectional-preference concentration (over the substrate's REAL grounded space).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
