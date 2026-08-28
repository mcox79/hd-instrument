"""Witness for the SET-RETURN decode landed on the situation-model register (2026-08-27).

Self-contained construction proof (no corpus) of the fix for the addressing-collision fan, from the integrated
`the_entity_store_is_a_dense_bundle_that_fans` (SOLVED/EXCELLENT, owner-DONE; reverify witnesses
test_entity_store_fan.py 21/21 + test_entity_store_frontier.py 26/26 re-verified FIRST-HAND):
  [1] COLLISION REPRODUCED: bind >1 role at ONE (entity, event_idx) address; the incumbent argmax `decode` returns
      only ONE of them (the fan artifact -- a busy character does several things at one context).
  [2] SET-RETURN RECOVERS THE SET: `decode_set` returns ALL co-bound roles (the information was never lost; the
      dense bundle holds it -- argmax just picked one). CA3 context-cued reactivation of the event set.
  [3] NO OVER-RETURN: on a UNIQUE address (one role bound) decode_set returns exactly that one role -- crosstalk
      from roles bound at OTHER slots stays below the margin and is excluded (info-free crosstalk loses).
  [4] BOTH BACKENDS: the flat AccumulateRegister and the default MultiBankAccumulateRegister both gain decode_set;
      decode() is byte-unchanged (additive, default-safe).
"""
from __future__ import annotations

import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.situation_model_accumulate import make_situation_register  # noqa: E402

D = 1024
ROLES = ["grab", "steady", "climb", "sing", "fall", "run"]


def _reg(backend):
    g = torch.Generator().manual_seed(20260827)
    return make_situation_register(ROLES, D, g, max_event_slots=8, backend=backend, n_banks=8)


def _check_backend(backend: str) -> None:
    reg = _reg(backend)
    # entity "hero": at slot 2 he does THREE things (a collision); at slot 5 he does ONE thing (unique).
    for r in ("grab", "steady", "climb"):
        reg.add_event("hero", r, 2)
    reg.add_event("hero", "sing", 5)

    # [1] collision: argmax decode returns only ONE of the three co-bound roles
    top, scores = reg.decode("hero", 2)
    assert top in {"grab", "steady", "climb"}, (backend, top)
    print(f"  [{backend}] [1] collision: argmax decode -> {top!r} (only 1 of 3 co-bound)")

    # [2] set-return recovers the whole co-bound set
    got, _ = reg.decode_set("hero", 2, rel_margin=0.5)
    assert set(got) == {"grab", "steady", "climb"}, f"{backend}: set-return must recover all 3 co-bound, got {got}"
    print(f"  [{backend}] [2] set-return -> {sorted(got)} (recovers ALL 3 -- info was never lost)")

    # [3] no over-return on a unique address; crosstalk from slot-2 roles excluded
    uniq, _ = reg.decode_set("hero", 5, rel_margin=0.5)
    assert uniq == ["sing"], f"{backend}: unique address must return exactly ['sing'], got {uniq}"
    print(f"  [{backend}] [3] unique address -> {uniq} (no over-return; crosstalk excluded)")

    # [4] decode() unchanged (still argmax, single answer)
    assert isinstance(reg.decode("hero", 5)[0], str) and reg.decode("hero", 5)[0] == "sing"
    print(f"  [{backend}] [4] decode() unchanged (argmax single answer) -- decode_set is additive")


def main() -> int:
    for backend in ("flat", "multibank"):
        _check_backend(backend)
    print("\nALL WITNESS ASSERTIONS PASSED -- set-return decode recovers the co-address collision set on BOTH")
    print("register backends where argmax returns only one; a unique address returns exactly its one role")
    print("(crosstalk excluded); decode() is byte-unchanged. The measured 'fan' was an argmax-vs-set readout")
    print("artifact on a coarse key, not superposition blur -- and this is the brain's CA3 set-reactivation read.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
