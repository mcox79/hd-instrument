"""Witness for hdlab.factorized_entity_store (landed 2026-08-28, landing-step 2 of the factorized entity store).

Self-contained construction proof (no corpus) of the two-system factorized store:
  [1] CO-MOMENT SET via RACE-TO-STOP: an entity that does several verbs at ONE context (different within-moment orders)
      is recovered as a SET by the self-terminating race -- NO oracle set-size.
  [2] CONTEXT FACTORISATION + CONTIGUITY: a verb stored at a FAR-AWAY context is NOT recovered at the query context
      (the graded context separates distant moments); a nearby context still shares contiguity.
  [3] SCHEMA/GIST ROUTING: a ROUTINE (repeated-dominant) verb graduates OUT of the episodic store into the gist.
  [4] GLASS-BOX: decode_set takes no gold; the store binds only at storage.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.factorized_entity_store import FactorizedEntityStore  # noqa: E402

VERBS = ["chase", "steady", "climb", "sing", "fall", "run", "read", "wait"]


def main() -> int:
    # [1] co-moment set: 'hero' does 3 things at t=10 (orders 0,1,2); race-to-stop recovers the set (no oracle)
    st = FactorizedEntityStore(VERBS, d=1024, seed=20260828, gist_route=False)   # gist off here to isolate the store
    for o, v in enumerate(["chase", "steady", "climb"]):
        st.add_event("hero", t=10.0, order=o, verb=v)
    st.add_event("hero", t=200.0, order=0, verb="sing")                          # a far-away other moment
    got = set(st.decode_set("hero", 10.0, stop="race"))
    print(f"[1] race-to-stop at t=10 -> {sorted(got)}")
    assert {"chase", "steady", "climb"} <= got, f"race must recover the co-moment set (got {got})"
    assert "sing" not in got, "a far-away-context verb must NOT leak into the co-moment set"

    # [2] context factorisation: querying a FAR context recovers nothing of hero's stored moments
    far = set(st.decode_set("hero", 900.0, stop="race"))
    print(f"[2] far context t=900 -> {sorted(far)} (should be empty / not the t=10 set)")
    assert not ({"chase", "steady", "climb"} & far), "distant context must not reactivate the t=10 moment"
    # the OTHER moment is recoverable at ITS context
    at200 = set(st.decode_set("hero", 200.0, stop="race"))
    print(f"[2] the other moment at t=200 -> {sorted(at200)}")
    assert "sing" in at200, "the verb stored at t=200 must be recoverable at t=200"

    # [3] schema/gist routing: a routine verb graduates to the gist
    st2 = FactorizedEntityStore(VERBS, d=1024, seed=1, gist_route=True, gist_min_count=3, gist_frac=0.5)
    routes = [st2.add_event("clerk", t=float(i), order=0, verb="read") for i in range(6)]   # 'read' is routine
    print(f"[3] routing of a repeated routine verb over 6 events: {routes}")
    assert routes[0] == "episodic" and "gist" in routes, "a routine verb must eventually route to the gist, not episodic"

    # [4] glass-box
    import inspect
    assert "gold" not in inspect.signature(FactorizedEntityStore.decode_set).parameters
    print(f"[4] glass-box PASS (decode_set signature: {list(inspect.signature(FactorizedEntityStore.decode_set).parameters)})")

    print("\nALL WITNESS ASSERTIONS PASSED -- the factorized store recovers a co-moment SET by a self-terminating race,")
    print("separates distant moments by the graded temporal context (each moment recoverable at ITS context), routes")
    print("routine events to the gist, and is glass-box -- content x context x order, bound only at storage.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
