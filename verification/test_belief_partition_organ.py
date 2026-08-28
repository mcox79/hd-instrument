"""Witness for hdlab.belief_partition (landed 2026-08-28).

Self-contained construction proof of the per-agent false-belief mechanism on the substrate's own FHRR organs
(no corpus): a classic Sally-Anne partition over a location vocabulary.
  [1] FALSE BELIEF: an agent who did NOT observe the move keeps the STALE initial binding (belief=initial != reality=final)
      -- the ToM signature. A shared-reality read (belief := reality) would be WRONG here.
  [2] TRUE BELIEF: an agent who OBSERVED updates (belief=final=reality) -- the can-fail control (belief tracks KNOWLEDGE).
  [3] TWO-AGENT DIVERGENCE: one agent false (initial), one true (final) in the SAME scene -> separate per-agent banks.
  [4] INFO-FREE TWIN: with the observation flag RANDOMISED, false-belief accuracy falls to ~chance -> the real observation
      signal (not the partition machinery alone) carries the win.
  [5] REALITY intact + glass-box: the world bank always decodes the truth; the query takes NO gold.
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.belief_partition import BeliefPartition, believed_location  # noqa: E402

LOCS = ["the basket", "the box", "the drawer", "the red cupboard", "the toy chest"]
# (agent, object, initial, final) false-belief scenarios: the agent is AWAY when the object moves.
SCENARIOS = [
    ("Sally", "the marble", "the basket", "the box"),
    ("Tom", "the ball", "the drawer", "the toy chest"),
    ("Ana", "the letter", "the red cupboard", "the basket"),
    ("Ben", "the coin", "the box", "the drawer"),
    ("Mia", "the ring", "the toy chest", "the red cupboard"),
]


def main() -> int:
    # [1] false belief: agent did NOT observe -> stale initial; reality = final
    bp = BeliefPartition()
    fb_ok = shared_reality_wrong = 0
    for ag, obj, ini, fin in SCENARIOS:
        bp.set_reality(obj, fin)
        bp.form_belief(ag, obj, ini, fin, observed=False)
        belief = bp.belief(ag, obj, LOCS)
        reality = bp.reality(obj, LOCS)
        fb_ok += int(belief == ini and reality == fin and belief != reality)
        shared_reality_wrong += int(reality != ini)   # a shared-reality reader would answer `reality` for the belief -> wrong
    n = len(SCENARIOS)
    print(f"[1] false belief (n={n}): stale-initial belief != reality  {fb_ok}/{n}; shared-reality would err {shared_reality_wrong}/{n}")
    assert fb_ok == n, f"false belief must be the STALE initial, distinct from reality ({fb_ok}/{n})"
    assert shared_reality_wrong == n, "the shared-reality floor must be wrong on every false-belief item"

    # [2] true belief: agent OBSERVED -> updates to final = reality
    bp2 = BeliefPartition()
    tb_ok = 0
    for ag, obj, ini, fin in SCENARIOS:
        bp2.set_reality(obj, fin)
        bp2.form_belief(ag, obj, ini, fin, observed=True)
        tb_ok += int(bp2.belief(ag, obj, LOCS) == fin == bp2.reality(obj, LOCS))
    print(f"[2] true belief (observed) (n={n}): belief == final == reality  {tb_ok}/{n}")
    assert tb_ok == n, f"an observer's belief must update to the final location ({tb_ok}/{n})"

    # [3] two-agent divergence in one scene: A false, B true -> separate banks
    bp3 = BeliefPartition()
    ag, obj, ini, fin = "Sally", "the marble", "the basket", "the box"
    bp3.set_reality(obj, fin)
    bp3.form_belief("Sally", obj, ini, fin, observed=False)   # away -> false
    bp3.form_belief("Anne", obj, ini, fin, observed=True)     # moved it -> true
    a, b = bp3.belief("Sally", obj, LOCS), bp3.belief("Anne", obj, LOCS)
    print(f"[3] divergence: Sally(false)->{a!r}  Anne(true)->{b!r}")
    assert a == ini and b == fin and a != b, "two agents must hold divergent beliefs from separate banks"

    # [4] info-free twin: randomise the observation flag -> false-belief acc ~chance (not systematically stale-initial)
    rng = np.random.default_rng(20260828)
    twin_ok = 0
    trials = 200
    for _ in range(trials):
        bt = BeliefPartition()
        ag, obj, ini, fin = SCENARIOS[int(rng.integers(0, n))]
        bt.form_belief(ag, obj, ini, fin, observed=bool(rng.integers(0, 2)))   # RANDOM observation
        twin_ok += int(bt.belief(ag, obj, LOCS) == ini)   # false-belief truth is `ini`
    twin_acc = twin_ok / trials
    print(f"[4] info-free twin (random observation): false-belief acc {twin_acc:.3f} (must be ~0.5, << the mechanism's 1.0)")
    assert twin_acc < 0.75, f"the random-observation twin must lose to the real mechanism ({twin_acc:.3f})"

    # [5] glass-box: the knowledge gate is explicit; the query takes no gold
    import inspect
    assert believed_location(True, "a", "b") == "b" and believed_location(False, "a", "b") == "a"
    params = list(inspect.signature(BeliefPartition.belief).parameters)
    assert "gold" not in params and "truth" not in params, params
    print(f"[5] glass-box PASS: believed_location gate explicit; belief() takes no gold ({params})")

    print("\nALL WITNESS ASSERTIONS PASSED -- the per-agent belief partition holds a STALE (false) belief for an agent")
    print("who did not observe a change, updates for an observer, keeps two agents' beliefs separate, loses under a")
    print("randomised observation signal, and never corrupts the reality bank -- on the substrate's own FHRR organs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
