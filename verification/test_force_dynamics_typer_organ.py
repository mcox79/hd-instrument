"""Witness for the LANDED hdlab.force_dynamics_typer (the Wolff/Talmy CAUSE/ENABLE/PREVENT causal typer).

Landed 2026-08-29 verbatim from the integrated `causation_has_no_force_dynamic_typing` (owner-DONE, SOLVED/EXCELLENT).
Confirms the store-agnostic scoring CORE: the Wolff truth-table types a causal relation from the verb's force class +
the outcome's endstate polarity, and — crucially — represents a PREVENTED endstate (an outcome that never happens),
which a connective/adjacency placeholder structurally cannot. (The shipped result: 0.929 vs the placeholder 0.190, PREVENT
killer 0.900 vs 0.000, force-class-shuffle twin loses; here the mechanism is witnessed store-agnostically.)

Asserts:
  1. TRUTH-TABLE (hand-built lexicon, no FrameNet needed): CAUSE verb + endstate-reached -> CAUSE, else NO_CAUSATION;
     ENABLE verb + reached -> ENABLE; PREVENT verb + NOT-reached -> PREVENT (the prevented endstate), reached -> NO_CAUSATION
     (the prevention failed); an unknown verb -> SEQUENTIAL (not a causal link).
  2. ENDSTATE DETECTOR: a plain outcome reads REACHED; a negation/failure cue ("not", "spared", "dry") flips it to NOT-reached.
  3. PREVENT KILLER end-to-end: "save"/"protect" + a negated outcome -> PREVENT (only force dynamics types a never-happened endstate).
  4. LEXICON builds from the committed cache (no FrameNet parse at runtime) and types known force verbs.
  5. spaCy-FREE at runtime.

Run: .venv/Scripts/python.exe verification/test_force_dynamics_typer_organ.py
"""
from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.force_dynamics_typer import (  # noqa: E402
    force_dynamic_type, detect_endstate_reached, build_force_lexicon)


def main() -> int:
    checks = []
    lex = {"shatter": "CAUSE", "allow": "ENABLE", "prevent": "PREVENT"}

    # (1) truth-table.
    tt = [
        (force_dynamic_type("shatter", True, lex) == "CAUSE", "CAUSE verb + reached -> CAUSE"),
        (force_dynamic_type("shatter", False, lex) == "NO_CAUSATION", "CAUSE verb + NOT reached -> NO_CAUSATION"),
        (force_dynamic_type("allow", True, lex) == "ENABLE", "ENABLE verb + reached -> ENABLE"),
        (force_dynamic_type("prevent", False, lex) == "PREVENT", "PREVENT verb + NOT reached -> PREVENT (prevented endstate)"),
        (force_dynamic_type("prevent", True, lex) == "NO_CAUSATION", "PREVENT verb + reached -> NO_CAUSATION (prevention failed)"),
        (force_dynamic_type("wander", True, lex) == "SEQUENTIAL", "unknown verb -> SEQUENTIAL (not a causal link)"),
    ]
    checks.append((all(ok for ok, _ in tt), f"[1] Wolff truth-table: {sum(ok for ok,_ in tt)}/{len(tt)} " +
                   ("all correct" if all(ok for ok, _ in tt) else "FAIL: " + "; ".join(m for ok, m in tt if not ok))))

    # (2) endstate detector.
    ed = [
        (detect_endstate_reached(["the", "village", "flooded"]) is True, "plain outcome -> reached"),
        (detect_endstate_reached(["the", "village", "was", "not", "flooded"]) is False, "'not' -> NOT reached"),
        (detect_endstate_reached(["the", "town", "stayed", "dry"]) is False, "'dry' (failure cue) -> NOT reached"),
    ]
    checks.append((all(ok for ok, _ in ed), f"[2] endstate detector: {sum(ok for ok,_ in ed)}/{len(ed)} correct"))

    # (3) PREVENT killer end-to-end (needs the real lexicon for save/protect).
    lex_full = build_force_lexicon()
    reached = detect_endstate_reached(["the", "child", "was", "spared"])            # 'spared' -> False
    killer = force_dynamic_type("save", reached, lex_full)
    checks.append((reached is False and killer == "PREVENT",
                   f"[3] PREVENT KILLER: 'save ... spared' -> endstate NOT reached ({reached}) + PREVENT ({killer})"))

    # (4) lexicon builds from the committed cache + types known force verbs.
    ok_lex = (isinstance(lex_full, dict) and len(lex_full) > 100
              and lex_full.get("save") == "PREVENT" and lex_full.get("protect") == "PREVENT"
              and lex_full.get("free") == "ENABLE")
    checks.append((ok_lex, f"[4] lexicon builds ({len(lex_full)} verbs): save/protect->PREVENT, free->ENABLE = {ok_lex}"))

    # (5) spaCy-free.
    checks.append(("spacy" not in sys.modules,
                   f"[5] runtime is spaCy-FREE (FrameNet is a static nltk asset, cached): {'spacy' not in sys.modules}"))

    print("=== witness: hdlab.force_dynamics_typer (Wolff CAUSE/ENABLE/PREVENT causal typer) ===")
    all_pass = True
    for ok, msg in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {msg}")
        all_pass = all_pass and ok
    print(f"\nRESULT: {'ALL CHECKS PASS' if all_pass else 'FAIL'} ({sum(1 for ok, _ in checks if ok)}/{len(checks)})")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
