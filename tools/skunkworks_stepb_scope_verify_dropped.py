"""SKUNKWORKS cert-owner SCOPE-RULING verification for STEP-B (A vs B).

Option B (finding-signal filter) DROPS classified notes that have NO marked finding-signal
(what_found OR citations OR ranked_candidates all empty). Before ruling B, the auditor must
VERIFY those dropped notes are genuinely requests/pointers, NOT real findings lost to a
header-mismatch in the marked-section parse (negativity-bias discipline: don't exclude on faith).

Imports the SHIPPED atomizer so classification + parse are IDENTICAL to what would APPLY.
Light compute (regex over note text) -> laptop OK per compute policy.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))

import atomize_research_findings as A  # noqa: E402

# Prose-finding indicators NOT requiring a markdown header (the recall gap B could miss).
RESULT_NUM = re.compile(r'(\d+(\.\d+)?\s*(x|%|pp)\b|->|\bRMSE\b|\bacc(uracy)?\s*[:=]|\brecall\b)', re.IGNORECASE)
RESULT_VERDICT = re.compile(r'\b(HARD_PASS|HARD_FAIL|PASS|FAIL|MIDDLE_BAND|CONFIRMED|REFUTED|VALIDATED)\b')
RESULT_VERB = re.compile(r'\b(we (found|find|observe|show)|results? (show|indicate)|demonstrat|confirms? that|the finding is|key result|conclusion[:])', re.IGNORECASE)
# Request/pointer indicators (legitimately droppable -- these are NOT findings).
REQUEST_LANG = re.compile(r'\b(probe|dispatch|please run|should run|request|anchor pointer|next-?step|TODO|propose|recommend running|hand-?off (to|request))', re.IGNORECASE)


def has_prose_finding(text: str) -> bool:
    body = text[:4000]
    hits = sum(bool(rx.search(body)) for rx in (RESULT_NUM, RESULT_VERDICT, RESULT_VERB))
    return hits >= 2  # at least two independent finding-signals in prose


def main():
    notes, dropped_cls = A.discover()
    with_signal, no_signal = [], []
    for p in notes:
        parsed = A.parse_note(p)
        sig = bool(parsed["what_found"] or parsed["ranked_candidates"] or parsed["citations"])
        (with_signal if sig else no_signal).append((p, parsed))

    print("=" * 88)
    print(f"classified (B-pool candidates): {len(notes)}   excluded-by-classify (bus/spec/state): {dropped_cls}")
    print(f"  WITH finding-signal (Option B keeps): {len(with_signal)}")
    print(f"  NO  finding-signal (Option B DROPS):  {len(no_signal)}   <- the set under audit")
    print("=" * 88)

    # Of the B-dropped set, how many actually carry a PROSE finding (header-mismatch false-negative)?
    prose_finding, pure_request, neither = [], [], []
    for p, parsed in no_signal:
        text = p.read_text(encoding="utf-8", errors="ignore")
        if has_prose_finding(text):
            prose_finding.append((p, text))
        elif REQUEST_LANG.search(text[:1500]):
            pure_request.append(p)
        else:
            neither.append(p)
    n = len(no_signal) or 1
    print(f"B-DROPPED breakdown ({len(no_signal)} notes):")
    print(f"  prose-finding present (potential FALSE-NEGATIVE for B): {len(prose_finding)}  ({100*len(prose_finding)//n}%)")
    print(f"  request/pointer language (legit drop):                  {len(pure_request)}  ({100*len(pure_request)//n}%)")
    print(f"  neither (bare headline only):                           {len(neither)}  ({100*len(neither)//n}%)")
    print("=" * 88)

    print("SAMPLE of B-dropped notes WITH prose-finding (the recall risk) -- up to 18:")
    for p, text in prose_finding[:18]:
        head = A.headline_of(text)[:88]
        # first prose line containing a result signal
        snip = ""
        for ln in text.splitlines():
            s = ln.strip()
            if len(s) > 30 and not s.startswith("#") and (RESULT_NUM.search(s) or RESULT_VERDICT.search(s) or RESULT_VERB.search(s)):
                snip = s[:150]
                break
        print(f"  [{p.name[:64]}]")
        print(f"     head: {head}")
        print(f"     snip: {snip}")

    print("=" * 88)
    print("STRIDE-SAMPLE of B-dropped 'neither' (bare) notes -- every 12th, up to 15:")
    for p in neither[::12][:15]:
        print(f"  {A.headline_of(p.read_text(encoding='utf-8', errors='ignore'))[:96]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
