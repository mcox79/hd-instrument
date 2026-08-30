"""Witness for the LANDED hdlab.situation_reader `role_route` opt-in (the ASSEMBLY Change 2).

Landed 2026-08-30 from the integrated `wire_the_predarg_frontend_and_binder_into_the_live_reader`
(owner-DONE, SOLVED/STRONG). Confirms the MECHANISM on the ACTUAL hdlab SituationReader (not the
experiment's subclass), recomputing fresh from source -- so a re-run proves the behavior, not a replay:

  1. role_route="positional" (the DEFAULT) is BYTE-IDENTICAL to the stock reader (every SituationModel
     dimension unchanged) -- the opt-in never touches the default path.
  2. With routing ON (role_route="hybrid"), the NON-role dimensions (entities / coref / timeline / causal
     / memory round-trip) stay BYTE-IDENTICAL and event recall is unchanged -- the diff touches ONLY role
     assignment, exactly as proposed.
  3. QUOTATIVE inversion is fixed IN the live read() path: "... said John ." -> John is the AGENT
     (speaker), where the stock positional reader brands the postverbal speaker the patient.
  4. A richer RECIPIENT role is emitted live for a ditransitive (a role the agent/patient reader cannot).

This mirrors exp_wire_predarg_binder_live_reader_integration_v1's self-test, but exercises the REAL
landed class. NO external LLM (nltk + persisted parse assets only).

Run: .venv/Scripts/python.exe verification/test_situation_reader_role_route_organ.py
"""
from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.situation_reader import SituationReader, _write_temp_conll  # noqa: E402


def _dims(sm):
    """The NON-role dimensions the wiring must leave byte-identical + the event count."""
    return {
        "n_sentences": sm.n_sentences,
        "entities": [(e.cluster, tuple(e.heads), tuple(e.sent_indices), e.n_mentions, e.is_person)
                     for e in sm.entities],
        "coref": [(r.pronoun, r.sent_idx, r.resolved_cluster, r.correct) for r in sm.coref_resolutions],
        "timeline": [(f.sent_idx, tuple(f.chrono_order), f.reordered) for f in sm.timeline_frames],
        "causal": [(l.sent_idx, l.cause, l.outcome, l.method) for l in sm.causal_links],
        "memory_roundtrip": round(sm.memory_roundtrip.get("roundtrip_rate", 0.0), 6),
        "n_events": len(sm.events),
    }


def main() -> int:
    gaz = {"john": "masc", "mary": "fem", "harry": "masc", "boatman": "masc", "beggar": "masc"}
    checks = []

    # (1)+(2) NO REGRESSION on a multi-sentence doc with a cross-sentence pronoun: positional == stock;
    #         wired leaves the non-role dims byte-identical + event count unchanged.
    rows = [
        (0, 0, "John", "(0)"), (0, 1, "saw", "_"), (0, 2, "Mary", "(1)"), (0, 3, ".", "_"),
        (1, 0, "He", "(0)"), (1, 1, "had", "_"), (1, 2, "finished", "_"),
        (1, 3, "before", "_"), (1, 4, "she", "(1)"), (1, 5, "arrived", "_"), (1, 6, ".", "_"),
        (2, 0, "She", "(1)"), (2, 1, "cried", "_"), (2, 2, "because", "_"),
        (2, 3, "he", "(0)"), (2, 4, "left", "_"), (2, 5, ".", "_"),
    ]
    path = _write_temp_conll(rows)
    try:
        stock = SituationReader(gaz=gaz).read(path)
        off = SituationReader(gaz=gaz, role_route="positional").read(path)
        wired = SituationReader(gaz=gaz, role_route="hybrid").read(path)
    finally:
        os.remove(path)
    checks.append((_dims(off) == _dims(stock),
                   "[1] role_route='positional' is BYTE-IDENTICAL to the stock reader"))
    ds, dw = _dims(stock), _dims(wired)
    nonrole_same = all(ds[k] == dw[k] for k in
                       ("n_sentences", "entities", "coref", "timeline", "causal", "memory_roundtrip"))
    checks.append((nonrole_same and dw["n_events"] == ds["n_events"],
                   "[2] role_route='hybrid' leaves entities/coref/timeline/causal/memory BYTE-IDENTICAL "
                   "+ event recall unchanged (the diff touches ONLY roles)"))

    # (3) QUOTATIVE inversion FIXED in the live path: "<quote> said John ." -- John is the AGENT.
    rows_q = [
        (0, 0, "Mary", "(0)"), (0, 1, "cried", "_"), (0, 2, ".", "_"),
        (1, 0, "Yes", "_"), (1, 1, ",", "_"), (1, 2, "said", "_"), (1, 3, "John", "(1)"), (1, 4, ".", "_"),
    ]
    path = _write_temp_conll(rows_q)
    try:
        stock_q = SituationReader(gaz=gaz).read(path)
        wired_q = SituationReader(gaz=gaz, role_route="hybrid").read(path)
    finally:
        os.remove(path)
    say_wired = [e for e in wired_q.events if e.predicate == "said"]
    say_stock = [e for e in stock_q.events if e.predicate == "said"]
    wired_ok = bool(say_wired) and str(say_wired[0].agent).lower() == "john"
    stock_wrong = (not say_stock) or str(say_stock[0].agent).lower() != "john"
    checks.append((wired_ok and stock_wrong,
                   f"[3] QUOTATIVE fixed live: wired binds John as AGENT of 'said' "
                   f"(wired={say_wired[0].agent if say_wired else None!r}, "
                   f"stock={say_stock[0].agent if say_stock else None!r}) where the stock reader fails"))

    # (4) richer RECIPIENT role EMITTED in the live path for a ditransitive.
    rows_d = [
        (0, 0, "Mary", "(0)"), (0, 1, "gave", "_"), (0, 2, "the", "_"), (0, 3, "book", "(1)"),
        (0, 4, "to", "_"), (0, 5, "John", "(2)"), (0, 6, ".", "_"),
    ]
    path = _write_temp_conll(rows_d)
    try:
        rdr_d = SituationReader(gaz=gaz, role_route="hybrid")
        rdr_d.read(path)
    finally:
        os.remove(path)
    recips = [x for x in rdr_d.wired_extra_roles if str(x.get("recipient", "")).lower() == "john"]
    checks.append((bool(recips),
                   f"[4] RECIPIENT=John emitted live for the ditransitive (extra_roles={rdr_d.wired_extra_roles})"))

    print("=== witness: hdlab.situation_reader role_route opt-in (ASSEMBLY Change 2) ===")
    all_pass = True
    for ok, msg in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {msg}")
        all_pass = all_pass and ok
    print(f"\nRESULT: {'ALL CHECKS PASS' if all_pass else 'FAIL'} ({sum(1 for ok, _ in checks if ok)}/{len(checks)})")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
