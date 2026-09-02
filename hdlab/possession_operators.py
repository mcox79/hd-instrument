"""possession_operators -- derive the world-state register's TRANSFER OPERATORS from a resource we
ALREADY HAVE (FrameNet), instead of a hand-authored verb list. This is the "use what we have + brain-
foundational" rebuild of the operator layer for situation_model_has_no_mutable_world_state_register.

PROMOTED VERBATIM (2026-09-01, Q111) from experiments/possession_operators.py -- the FrameNet-derived
operator+role lexicon the world-state register runs off. The lexicon is a STATIC OFFLINE asset built once
and cached at data/possession_operators_v1/lexicon.json (loaded from cache at inference -- no nltk /
FrameNet needed in the live reader). Wired behind the reader's default-off `track_world_state` flag.

BRAIN FRAME:
  PINNED (the COMPUTATION, shared): possession-transfer is a caused-change-of-possession CONSTRUCTION
    (Goldberg 1995; Pinker 1989 give/get verb classes) whose semantics is a FrameNet FRAME with roles
    Donor/Recipient/Theme (Fillmore frame semantics = the brain's event-role structure; Baker/Fillmore
    FrameNet). The STRIPS effect (~have(donor,theme) & have(recipient,theme)) is the frame's meaning.
  FROM-RESOURCE (the PARAMETER, language-specific, we GET not invent): which verbs evoke which transfer
    frame, and each frame's role inventory -- read directly from FrameNet (nltk). The recipient/source
    ROLE is a frame element (Recipient/Goal/Source/Donor), so it comes for free -- fixing the recipient
    gap at the resource level, not by a bespoke dative rule.
  LEARNED (see experiments/exp_world_state_learn_operators_v1.py): a verb NOT covered by FrameNet has its
    operator INDUCED from observed possession transitions (usage-based construction acquisition; the
    consequence_learning_loop template). The FrameNet map is the inherited SEED; learning is the growth.

FRAME -> OPERATOR is the one principled mapping authored here (frame semantics -> STRIPS possession
effect); verb membership + role inventory are pulled from FrameNet. op classes:
  GIVE  : donor loses theme, recipient gains it  (Giving, Sending, Delivery, Supply, Transfer,
          Commerce_sell [seller->buyer goods], Lending [lender->borrower]).
  GET   : agent gains theme (optionally from a source)  (Getting, Receiving, Taking, Commerce_buy,
          Borrowing).
  LOSE  : agent/source loses theme  (Removing).

Glass-box, NO external LLM. FrameNet is a STATIC OFFLINE asset (admissible foundation); the lexicon is
built once and cached. ASCII only.
"""
from __future__ import annotations

import json
import os
from typing import Dict, Optional

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, "data", "possession_operators_v1", "lexicon.json")

# FRAME -> (op_class, role_slots): which FrameNet frame elements fill giver / recipient / theme / source.
# The op_class is the frame's possession-change semantics (PINNED). The FE names are FrameNet's.
FRAME_OPS = {
    # GIVE-type: giver loses, recipient gains
    "Giving":       ("GIVE", {"giver": ["Donor"], "recipient": ["Recipient"], "theme": ["Theme"]}),
    "Sending":      ("GIVE", {"giver": ["Sender"], "recipient": ["Recipient", "Goal"], "theme": ["Theme"]}),
    "Delivery":     ("GIVE", {"giver": ["Deliverer"], "recipient": ["Recipient", "Goal"], "theme": ["Theme"]}),
    "Supply":       ("GIVE", {"giver": ["Supplier"], "recipient": ["Recipient"], "theme": ["Theme"]}),
    "Transfer":     ("GIVE", {"giver": ["Donor", "Transferors"], "recipient": ["Recipient"], "theme": ["Theme"]}),
    "Commerce_sell":("GIVE", {"giver": ["Seller"], "recipient": ["Buyer"], "theme": ["Goods"]}),
    "Lending":      ("GIVE", {"giver": ["Lender"], "recipient": ["Borrower"], "theme": ["Theme"]}),
    # GET-type: agent gains (optionally from a source)
    "Getting":      ("GET", {"getter": ["Recipient"], "source": ["Source", "Donor"], "theme": ["Theme"]}),
    "Receiving":    ("GET", {"getter": ["Recipient"], "source": ["Donor"], "theme": ["Theme"]}),
    "Taking":       ("GET", {"getter": ["Agent"], "source": ["Source"], "theme": ["Theme"]}),
    "Commerce_buy": ("GET", {"getter": ["Buyer"], "source": ["Seller"], "theme": ["Goods"]}),
    "Borrowing":    ("GET", {"getter": ["Borrower"], "source": ["Lender"], "theme": ["Theme"]}),
    # LOSE/REMOVE-type: agent/source loses theme
    "Removing":     ("LOSE", {"loser": ["Agent", "Source"], "theme": ["Theme"]}),
}
# priority when a verb sits in multiple transfer frames (marked/specific first): GIVE > GET > LOSE
OP_PRIORITY = {"GIVE": 3, "GET": 2, "LOSE": 1}


def _lemmatize_lu(lu_name: str) -> Optional[str]:
    base = lu_name.rsplit(".", 1)[0].strip().lower()
    if " " in base:
        head = base.split()[0]
        return head if head.isalpha() else None
    return base if base.isalpha() else None


def build_lexicon(use_cache: bool = True) -> Dict[str, dict]:
    """verb -> {op, frame, roles:{slot:[FE,...]}} derived from FrameNet transfer frames. Cached offline."""
    if use_cache and os.path.exists(CACHE):
        with open(CACHE, "r", encoding="utf-8") as f:
            return json.load(f)
    from nltk.corpus import framenet as fn  # local import (heavy; FrameNet is the static asset)
    lex: Dict[str, dict] = {}
    for frame, (op, roles) in FRAME_OPS.items():
        try:
            fr = fn.frame_by_name(frame)
        except Exception:
            continue
        present = set(fr.FE.keys())
        roles_present = {slot: [fe for fe in fes if fe in present] for slot, fes in roles.items()}
        for lu in fr.lexUnit.keys():
            if not lu.endswith(".v"):
                continue
            v = _lemmatize_lu(lu)
            if not v:
                continue
            cur = lex.get(v)
            if cur is None or OP_PRIORITY[op] > OP_PRIORITY[cur["op"]]:
                lex[v] = {"op": op, "frame": frame, "roles": roles_present}
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    tmp = CACHE + ".tmp"
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(lex, f, indent=1, sort_keys=True)
    os.replace(tmp, CACHE)
    return lex


def self_test() -> int:
    lex = build_lexicon(use_cache=False)
    checks = [
        ("give", "GIVE"), ("hand", "GIVE"), ("donate", "GIVE"), ("bequeath", "GIVE"),
        ("send", "GIVE"), ("sell", "GIVE"), ("lend", "GIVE"), ("supply", "GIVE"),
        ("get", "GET"), ("receive", "GET"), ("obtain", "GET"), ("acquire", "GET"),
        ("buy", "GET"), ("borrow", "GET"), ("take", "GET"),
    ]
    ok = True
    for v, exp in checks:
        got = lex.get(v, {}).get("op")
        good = got == exp
        ok = ok and good
        print("  [%s] %-10s -> %-5s (expect %s) frame=%s" %
              ("OK" if good else "FAIL", v, got, exp, lex.get(v, {}).get("frame")), flush=True)
    # recipient role must be recoverable for a canonical give verb (the gap the hand-lexicon left)
    give = lex.get("give", {})
    has_recip = bool(give.get("roles", {}).get("recipient"))
    print("  [%s] 'give' carries a RECIPIENT role from FrameNet: %s" %
          ("OK" if has_recip else "FAIL", give.get("roles", {}).get("recipient")), flush=True)
    ok = ok and has_recip
    print("  lexicon size = %d verbs across %d transfer frames" %
          (len(lex), len({v["frame"] for v in lex.values()})), flush=True)
    print("[self-test] " + ("ALL OK" if ok else "FAILED"), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    sys.exit(self_test())
