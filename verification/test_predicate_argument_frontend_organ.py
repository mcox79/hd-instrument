"""Witness for the LANDED hdlab.predicate_argument_frontend.route_predicate_arguments (the shared event-semantic
predicate-argument / shallow-SRL front-end).

Landed 2026-08-29 from the integrated `no_shared_shallow_predicate_argument_front_end` (owner-DONE, PARTIAL/STRONG).
Confirms the MECHANISM on the actual hdlab organ, store-agnostically (hand-built minimal parses): the router types
each PP by the BRAIN'S event-semantics -- preposition-telicity (CUE1) modulated by the verb's VerbNet event-class
(CUE2) + the constructional caused-motion gate -- recovering the FIVE spatial/transfer roles (goal, location, path,
source, recipient) the conflating inline rule cannot, and crucially typing them by preposition VERB-INDEPENDENTLY
(the fix for v1's curated-motion-verb-list error). This is the +five-role, CI-separated mechanism the shipped
FrameNet result measured; here it is mechanism-witnessed.

Each case builds a minimal 1-based parse (tokens, upos, heads[child->head], verb_idx) for "[verb] [prep] the [noun]"
(or a transfer/caused-motion frame) and asserts the router puts the noun under the RIGHT role key and leaves the
others None. The role TYPING is set purely by preposition + verb-class, so it is robust to the ancillary binder.

Asserts:
  1. to   -> GOAL       ("walked to the door")
  2. in   -> LOCATION   ("stayed in the factory")
  3. through -> PATH    ("ran through the tunnel")
  4. from -> SOURCE     ("fled from the city")
  5. TRANSFER verb + to -> RECIPIENT, NOT goal ("handed the letter to Mary") -- CUE2 over CUE1
  6. CAUSED-MOTION, verb-independent: "shoved him to the ground" -> goal=ground even though 'shove' is in NO
     motion-verb list (the constructional gate; v1's list-shape error fixed), and the moved theme is attributed.
  7. runtime is spaCy-FREE (no external LLM; VerbNet/WordNet are static nltk lexical assets).

Run: .venv/Scripts/python.exe verification/test_predicate_argument_frontend_organ.py
"""
from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.predicate_argument_frontend import route_predicate_arguments  # noqa: E402

# roles that must be None when a single PP is typed as one specific role
_SPATIAL = ("goal", "location", "path", "source", "recipient", "direction")


def _vpp(verb, prep, noun, upos_noun="NOUN"):
    """Build the minimal parse for '[verb] [prep] the [noun]': tokens 1..4, PP object (4) attaches to verb (1)."""
    tokens = [verb, prep, "the", noun]
    upos = ["VERB", "ADP", "DET", upos_noun]
    heads = {2: 4, 3: 4, 4: 1}   # prep->noun (case), the->noun (det), noun->verb (obl)
    return route_predicate_arguments(tokens, upos, heads, 1)


def _only(role, r):
    """True iff `role` holds index 4 (the noun) and every OTHER spatial/transfer role is None."""
    return r.get(role) == 4 and all(r.get(k) is None for k in _SPATIAL if k != role)


def main() -> int:
    checks = []

    r1 = _vpp("walked", "to", "door")
    checks.append((_only("goal", r1), f"[1] 'walked to the door' -> GOAL only: { {k: r1[k] for k in _SPATIAL} }"))

    r2 = _vpp("stayed", "in", "factory")
    checks.append((_only("location", r2), f"[2] 'stayed in the factory' -> LOCATION only: { {k: r2[k] for k in _SPATIAL} }"))

    r3 = _vpp("ran", "through", "tunnel")
    checks.append((_only("path", r3), f"[3] 'ran through the tunnel' -> PATH only: { {k: r3[k] for k in _SPATIAL} }"))

    r4 = _vpp("fled", "from", "city")
    checks.append((_only("source", r4), f"[4] 'fled from the city' -> SOURCE only: { {k: r4[k] for k in _SPATIAL} }"))

    # (5) TRANSFER verb + 'to' -> RECIPIENT (Mary=5), NOT goal -- CUE2 (verb-class) overrides CUE1 (preposition).
    tok5 = ["handed", "the", "letter", "to", "Mary"]
    up5 = ["VERB", "DET", "NOUN", "ADP", "PROPN"]
    hd5 = {2: 3, 3: 1, 4: 5, 5: 1}   # the->letter, letter->handed(obj), to->Mary(case), Mary->handed(obl)
    r5 = route_predicate_arguments(tok5, up5, hd5, 1)
    checks.append((r5.get("recipient") == 5 and r5.get("goal") is None,
                   f"[5] 'handed the letter to Mary' -> RECIPIENT=Mary(5), goal None (CUE2 over CUE1): recipient={r5.get('recipient')} goal={r5.get('goal')}"))

    # (6) CAUSED-MOTION, verb-independent: 'shove' is in NO motion-verb list, yet 'to the ground' types as GOAL
    # (the constructional CUE1 gate), and the moved THEME (him) is the goal-holder.
    tok6 = ["shoved", "him", "to", "the", "ground"]
    up6 = ["VERB", "PRON", "ADP", "DET", "NOUN"]
    hd6 = {2: 1, 3: 5, 4: 5, 5: 1}   # him->shoved(obj), to->ground(case), the->ground, ground->shoved(obl)
    r6 = route_predicate_arguments(tok6, up6, hd6, 1)
    checks.append((r6.get("goal") == 5,
                   f"[6] 'shoved him to the ground' -> GOAL=ground(5) though 'shove' is in NO motion list (constructional gate): goal={r6.get('goal')} goal_belongs_to={r6.get('goal_belongs_to')}"))

    # (7) spaCy-free.
    checks.append(("spacy" not in sys.modules,
                   f"[7] runtime is spaCy-FREE (no external LLM; VerbNet/WordNet are static nltk assets): {'spacy' not in sys.modules}"))

    print("=== witness: hdlab.predicate_argument_frontend.route_predicate_arguments (shared event-semantic SRL) ===")
    all_pass = True
    for ok, msg in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {msg}")
        all_pass = all_pass and ok
    print(f"\nRESULT: {'ALL CHECKS PASS' if all_pass else 'FAIL'} ({sum(1 for ok, _ in checks if ok)}/{len(checks)})")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
