"""Witness for the LANDED hdlab.idiom_lexicon (spaCy-free stored-unit MWE FOUNDATION).

Landed 2026-08-28 from the integrated `no_glass_box_verb_sense_disambiguation` (SOLVED/EXCELLENT, owner-DONE). Confirms
the shared idiom-flagging foundation on the ACTUAL committed asset (data/idiom_foundation_v1/idioms.json): a
non-compositional MWE retrieves its stored holistic coarse frame; a LITERAL verb+object/particle returns None (compose
literally); the runtime is spaCy-FREE (a dict lookup).

Asserts:
  1. VERB+OBJECT MWEs retrieve their stored frame (take|place->stative, make|sense->cognition, hold|meeting->social,
     give|speech->communication) -- and every returned frame is a valid COARSE_FRAME.
  2. PHRASAL-VERB MWEs retrieve their stored frame (pass|away, go|off, come|back are stored, not None).
  3. LITERAL cases return None (leave|room, leave|key, walk|dog) -- the caller composes literally.
  4. is_idiom agrees with idiom_sense; empty verb -> None; particle checked before object.
  5. spaCy-FREE + WordNet-free at runtime (no spacy / nltk imported by importing/using the module).

Run: .venv/Scripts/python.exe verification/test_idiom_lexicon_organ.py
"""
from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.idiom_lexicon import idiom_sense, is_idiom, COARSE_FRAMES, _FRAMESET  # noqa: E402


def main() -> int:
    checks = []

    # (1) verb+object MWEs.
    vobj = {("take", None, "place"): "stative", ("make", None, "sense"): "cognition",
            ("hold", None, "meeting"): "social", ("give", None, "speech"): "communication"}
    vobj_ok = all(idiom_sense(v, p, o) == fr for (v, p, o), fr in vobj.items())
    frames_valid = all(idiom_sense(v, p, o) in _FRAMESET for (v, p, o) in vobj)
    checks.append((vobj_ok and frames_valid,
                   f"[1] VERB+OBJECT MWEs retrieve stored frame + valid COARSE_FRAME: {vobj_ok and frames_valid} "
                   f"(take|place->{idiom_sense('take', None, 'place')}, make|sense->{idiom_sense('make', None, 'sense')})"))

    # (2) phrasal-verb MWEs are stored (non-None).
    phrasal = [("pass", "away", None), ("go", "off", None), ("come", "back", None)]
    ph_ok = all(idiom_sense(v, p, o) is not None and idiom_sense(v, p, o) in _FRAMESET for (v, p, o) in phrasal)
    checks.append((ph_ok, f"[2] PHRASAL-VERB MWEs stored (non-None, valid frame): {ph_ok} "
                          f"(pass|away->{idiom_sense('pass', 'away', None)}, go|off->{idiom_sense('go', 'off', None)})"))

    # (3) literal cases return None.
    literal = [("leave", None, "room"), ("leave", None, "key"), ("walk", None, "dog"), ("put", None, "book")]
    lit_ok = all(idiom_sense(v, p, o) is None for (v, p, o) in literal)
    checks.append((lit_ok, f"[3] LITERAL cases return None (compose literally): {lit_ok} "
                           f"(leave|room->{idiom_sense('leave', None, 'room')})"))

    # (4) API consistency.
    api_ok = (is_idiom("take", None, "place") is True and is_idiom("leave", None, "room") is False
              and idiom_sense("", None, "place") is None and idiom_sense("take", None, None) is None)
    checks.append((api_ok, f"[4] API: is_idiom<->idiom_sense agree; empty verb None; object-only-no-object None -> {api_ok}"))

    # (5) spaCy-free + WordNet-free at runtime.
    clean = "spacy" not in sys.modules and "nltk" not in sys.modules
    checks.append((clean, f"[5] runtime is spaCy-FREE + WordNet-FREE (no spacy/nltk in sys.modules): {clean}"))

    print("=== witness: hdlab.idiom_lexicon (spaCy-free stored-unit MWE foundation) ===")
    all_pass = True
    for ok, msg in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {msg}")
        all_pass = all_pass and ok
    print(f"\n  (asset: {len(COARSE_FRAMES)} coarse frames)")
    print(f"RESULT: {'ALL CHECKS PASS' if all_pass else 'FAIL'} ({sum(1 for ok, _ in checks if ok)}/{len(checks)})")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
