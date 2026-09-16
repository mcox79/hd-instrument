"""test_no_stale_default_off_flag -- GENERALIZATION for pri 130 (dormant_capability_flags_audit...).

problem: dormant_capability_flags_audit_every_default_off_flag_its_reason_and_whether_the_reason_still_holds_flip_or_delete

WHAT THIS ENFORCES: every boolean capability flag of `SituationReader.__init__` that defaults OFF must carry
a machine-readable classification in the registry below (`CLASSIFICATION`), and the **STALE-REASON class must
be empty** -- a flag whose "why off" reason is 19c-only, a capped-board artifact, or "byte-identical pending a
measurement" is not allowed to sit unflipped once measured (pri 130's own checklist item 3/4).

HOW IT WORKS: it introspects the LIVE `SituationReader.__init__` signature (via `inspect.signature`, no
hdlab file is edited or duplicated) to find every boolean kwarg defaulting to `False`, and cross-checks that
set against `CLASSIFICATION` (built from the audit table, `flags_audit_table.md` -- SOT is this file, but the
table is the human-readable rendering of the same facts).

TODAY (against HEAD, before `default_flips_patch.diff` lands): this test is EXPECTED TO FAIL, naming the
flags still classified STALE-REASON (`agent_hybrid`, `agent_hybrid_construction`, `unified_referent`,
`entity_kb_resolver`, `graded_role_marginal`, `structural_do_recover`) -- that failure IS the audit's
finding, made into a can-fail gate. Once the diff flips a flag's default to True (or the flag is retagged
LIVE-REASON/DIAGNOSTIC with a fresh measured reason), remove it from `CLASSIFICATION`'s stale set (or
retag it) and the test passes again.

Two more checks, independent of the stale-class check:
  (a) every boolean False-default kwarg found by introspection has an ENTRY in `CLASSIFICATION` (nothing new
      can go unreviewed -- a brand-new default-off flag with no audit entry fails loudly, by name).
  (b) `commonnoun_situation_gate` (proven byte-identical dead code, RETIRED 2026-09-11) stays tagged
      DEAD_NOOP, not silently promoted to any other class, until it is actually deleted from the signature.

Run: .venv/Scripts/python.exe verification/test_no_stale_default_off_flag.py
"""
from __future__ import annotations
import inspect
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.situation_reader import SituationReader

# ---------------------------------------------------------------------------------------------------
# THE REGISTRY -- one entry per boolean flag that (as of this audit, pri 130, 2026-09-15) defaults OFF.
# classification in {"LIVE_REASON", "DIAGNOSTIC", "STAND_IN", "DEAD_NOOP", "IN_FLIGHT", "STALE_REASON"}.
# A flag that flips to default-ON (via default_flips_patch.diff) simply drops off this registry's
# "currently False" side automatically -- introspection will no longer find it among the False defaults,
# so it needs no manual removal here; only STALE_REASON entries need to shrink for the gate to pass.
# ---------------------------------------------------------------------------------------------------
CLASSIFICATION = {
    "causation_typed":              "STAND_IN",     # loads spaCy at inference -- not flippable under the BF bar
    "causation_foreground_gate":    "STAND_IN",     # dependent sub-flag of causation_typed
    "affect_structured_matcher":    "LIVE_REASON",  # OCC gold saturated ~0.94, no converse/antonym headroom (2026-09-07)
    "track_coherence":              "LIVE_REASON",  # +0.016 full-pop, NOT CI-sep; goal engine over-fires (2026-09-07)
    "graded_role_marginal":         "STALE_REASON", # already +0.0065 CI-sep who-did-what measured; "measure-first" gate is stale
    "structural_do_recover":        "STALE_REASON", # motivated by a 19c-specific count; register-general mechanism, never measured modern
    "agent_hybrid":                 "STALE_REASON", # explicit 19c-board reason; 19c banned from requirements since 2026-09-06
    "agent_hybrid_construction":    "STALE_REASON", # paired with agent_hybrid
    "entity_kb_resolver":           "STALE_REASON", # "board doesn't score common-noun" reason is stale since pri 122's board rewrite
    "commonnoun_situation_gate":    "DEAD_NOOP",    # proven byte-identical; online_entity_cluster overwrites it (RETIRED 2026-09-11)
    "commonnoun_type_license":      "LIVE_REASON",  # measured regression -0.0196 CI-sep, twin indistinguishable (2026-09-11)
    "unified_referent":             "STALE_REASON", # "flips on after first-hand verify" -- the verify already shows +0.106 CI-sep
    "pronoun_principle_b":          "IN_FLIGHT",    # pri 131's own active build, 2026-09-15 -- not this brief's to touch
}

STALE = {"STALE_REASON"}


def _false_default_bool_kwargs():
    sig = inspect.signature(SituationReader.__init__)
    out = []
    for name, p in sig.parameters.items():
        if p.kind != inspect.Parameter.KEYWORD_ONLY:
            continue
        if p.default is False and isinstance(p.default, bool):
            out.append(name)
    return sorted(out)


def selftest():
    found = _false_default_bool_kwargs()
    print("[T1] %d boolean False-default kwargs found by introspection: %s" % (len(found), found))

    # (a) every found flag must be registered -- an unreviewed new default-off flag fails BY NAME.
    unregistered = [f for f in found if f not in CLASSIFICATION]
    assert not unregistered, (
        "[T1 FAIL] new default-off boolean flag(s) with no audit entry: %s -- classify them in "
        "CLASSIFICATION (flags_audit_table.md) before they can ship silently." % unregistered)
    print("[T1] PASS: every default-off boolean flag is registered.")

    # (b) every registered flag that introspection still finds False must have a KNOWN classification tag.
    bad_tag = [f for f in found if CLASSIFICATION.get(f) not in
               ("LIVE_REASON", "DIAGNOSTIC", "STAND_IN", "DEAD_NOOP", "IN_FLIGHT", "STALE_REASON")]
    assert not bad_tag, "[T2 FAIL] unrecognized classification tag(s): %s" % bad_tag
    print("[T2] PASS: every default-off flag carries a recognized machine-readable tag.")

    # (c) THE GATE: the STALE_REASON class must be empty among flags STILL default-off.
    stale_now = [f for f in found if CLASSIFICATION.get(f) in STALE]
    if stale_now:
        print("[T3] FAIL (expected until default_flips_patch.diff lands): STALE-REASON flags still "
              "default-off: %s" % stale_now)
        print("     Each one's measured product-board effect is in SOLVED.md section 3. Flip its default to True "
              "(or re-tag it LIVE_REASON/DIAGNOSTIC with a fresh dated, numbered reason) to close this gate.")
    assert not stale_now, (
        "[T3 FAIL] STALE-REASON default-off flags remain: %s -- see notes/problems/"
        "dormant_capability_flags_audit_.../SOLVED.md and default_flips_patch.diff" % stale_now)
    print("[T3] PASS: the STALE-REASON class is empty.")

    # (d) commonnoun_situation_gate stays DEAD_NOOP until it is actually deleted from the signature.
    if "commonnoun_situation_gate" in found:
        assert CLASSIFICATION.get("commonnoun_situation_gate") == "DEAD_NOOP", (
            "[T4 FAIL] commonnoun_situation_gate is present and default-off but not tagged DEAD_NOOP -- "
            "it was proven byte-identical dead code (RETIRED 2026-09-11); re-verify before retagging it live.")
        print("[T4] PASS (informational): commonnoun_situation_gate is still present, tagged DEAD_NOOP "
              "(prune-list candidate, not a flip).")
    else:
        print("[T4] PASS: commonnoun_situation_gate has been removed from the signature (pruned).")

    print("SELF-TEST PASS: 4/4 (T3 is the live gate; see the printed note if it failed).")


if __name__ == "__main__":
    selftest()
