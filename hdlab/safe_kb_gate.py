"""Safe-KB familiarity gate -- make a broad/noisy entity knowledge-base SAFE to consult.

PROMOTED 2026-09-09 (Q111) from experiments/exp_namebridge_safe_kb_gate_v1.py::safe_kb_types (the reusable
project-wide deliverable of the owner-DONE `world_knowledge_common_noun_to_name_bridge_the_81_percent_residual`,
reverified 11/11 + 9/9). Self-contained: the ONLY dependency is the landed hdlab.typed_spokes is-a spoke (the
`_compatible` consistency check was `experiments._entity_type_spoke.TS.is_a`, and `TS` there IS `hdlab.typed_spokes`
-- repointed directly, behaviour-identical). NO experiments import, NO external LLM.

WHY (the safety theorem this proves): a static/broad entity KB looked up by name and asserted top-1 for every
match is HARMED under noise -- wrong-entity disambiguation (notable-but-wrong) pours in false type facts. The brain
does NOT do this: recognition memory is gated by FAMILIARITY (Bruce & Young 1986 IAC person-recognition; Yonelinas
2002 dual-process SDT criterion) -- a name's stored facts fire only when the current context CONFIRMS the
recognition, else the system ABSTAINS (a NIL/"I don't actually know who this is" response). Wrapping a KB lookup in
this gate converts an unsafe broad KB into a safe one: MEASURED (the source cell, noise-injection) an UNGATED KB is
harmed 0.607->0.399 while the GATED KB is PROTECTED at 0.601. So: wrap ANY KB lookup in `safe_kb_types` before
admitting its facts. PINNED (copy): the familiarity-gated confirm/abstain decision. OUR-INVENTION (swept): the
notability fallback threshold `tau_notability` (the criterion for the silent-context case).

USAGE:  admitted = safe_kb_types(raw_kb_types, discourse_types, notability)
  raw_kb_types    = the KB's asserted type set for the recognized name (may be noisy / wrong-entity).
  discourse_types = the entity's ONLINE who-is-who type set from the document (the recognition signal).
  notability      = a familiarity proxy for the SILENT case (no discourse types yet); >= tau -> trust, else abstain.
Returns the SAFE subset (possibly empty = ABSTAIN/NIL).
"""
from __future__ import annotations

__bf_status__ = "BF"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = "2026-09-09 name-bridge world-knowledge solver (safety theorem proven: ungated 0.607->0.399 harmed vs gated 0.601 protected under noise injection); strategy first-hand"
__bf_note__ = "Bruce-Young/IAC familiarity gate + Yonelinas dual-process SDT criterion: KB facts fire only when discourse CONFIRMS the recognition, else ABSTAIN (NIL); notability fallback (tau) swept, not adopted; is-a consistency via hdlab.typed_spokes"
__bf_corrections__ = []

import hdlab.typed_spokes as TS

TAU_NOTAB = 30   # OUR-INVENTION-UNDER-TEST: the familiarity criterion for the silent (no-discourse) case; sweep, don't adopt


def _compatible(a, b):
    """Type-consistency: identity OR an is-a relation either direction (hdlab.typed_spokes C5 spoke)."""
    if a == b:
        return True
    try:
        return bool(TS.is_a(a, b) or TS.is_a(b, a))
    except Exception:
        return False


def safe_kb_types(raw_kb_types, discourse_types, notability=0, tau_notability=TAU_NOTAB, consistent_fn=_compatible):
    """Make a broad/noisy KB SAFE: admit an entity's KB type facts ONLY when the DISCOURSE confirms them
    (Bruce-Young familiarity gate). discourse_types = the entity's online who-is-who type set. Returns the SAFE
    subset of raw_kb_types (possibly empty = ABSTAIN/NIL). Wrap this around any KB lookup."""
    if not raw_kb_types:
        return frozenset()
    if discourse_types:
        if any(consistent_fn(d, k) for d in discourse_types for k in raw_kb_types):
            return frozenset(raw_kb_types)          # discourse CONFIRMS the recognition -> facts fire
        return frozenset()                          # discourse present but DISAGREES -> wrong entity -> abstain
    return frozenset(raw_kb_types) if notability >= tau_notability else frozenset()   # silent -> familiarity gate


def _selftest() -> int:
    """The gate confirms/abstains/notability-falls-back correctly (byte-faithful to the source cell's self_test)."""
    fails = []
    cases = [
        (safe_kb_types(frozenset(["composer"]), {"composer"}, 0), frozenset(["composer"]), "exact confirm keeps"),
        (safe_kb_types(frozenset(["painter"]), {"artist"}, 0), frozenset(["painter"]), "is-a confirm keeps"),
        (safe_kb_types(frozenset(["album"]), {"person", "teacher"}, 500), frozenset(), "disagree abstains (even if notable)"),
        (safe_kb_types(frozenset(["country"]), set(), 100), frozenset(["country"]), "silent + notable keeps"),
        (safe_kb_types(frozenset(["country"]), set(), 1), frozenset(), "silent + obscure abstains"),
        (safe_kb_types(frozenset(), {"person"}, 500), frozenset(), "empty KB -> abstain"),
    ]
    for got, want, desc in cases:
        ok = got == want
        print("  %s %s (got=%s)" % ("PASS" if ok else "FAIL", desc, set(got)))
        if not ok:
            fails.append(desc)
    print("RESULT: %s" % ("PASS" if not fails else "FAIL (%s)" % "; ".join(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    import sys
    sys.exit(_selftest())
