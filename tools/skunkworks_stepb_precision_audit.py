"""SKUNKWORKS re-VET precision audit for STEP-B prose-capture (the symmetric guard).

Recall is reported at 99% (1228/1229 populated). The risk that buys: did the prose-capture
inject PLAN/SPEC/REQUEST boilerplate into what_found for notes with no real finding? This audits
PRECISION across ALL 1229 (not just the content-rich alphabetical front the 50-sample shows):
for every populated what_found, does it actually contain a RESULT signal, or is it non-finding noise?

Imports the SHIPPED (enhanced) atomizer so the parse is identical to APPLY. Light compute -> laptop OK.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "tools"))
import atomize_research_findings as A  # noqa: E402

# A real finding signal inside the captured what_found.
RESULT = re.compile(
    r'(\d+(\.\d+)?\s*(x|%|pp|b)\b|->|=\s*\d|\w+@\d|\bRMSE\b|\brecall\b|'
    r'\b(HARD[_-]?PASS|HARD[_-]?FAIL|PASS|FAIL|MIDDLE_BAND|CONFIRMED|REFUTED|VALIDATED)\b|'
    r'\b(found|diagnos|root cause|mechanism|predicts?|stalls?|caused by|exposes)\b|P\()',
    re.IGNORECASE)
# Pure request/plan markers (if what_found is THESE with no RESULT -> leak).
REQ = re.compile(r'\b(please run|should run|will run|plan to|dispatch|TODO|next-?step|to run\b|recommend running)\b', re.IGNORECASE)


def main():
    notes, _ = A.discover()
    empty, signal, noleak_req, LEAK = 0, 0, 0, []
    for p in notes:
        wf = A.parse_note(p)["what_found"]
        if not wf:
            empty += 1
        elif RESULT.search(wf):
            signal += 1
        else:
            # populated but NO result signal -> precision risk
            LEAK.append((p.name, wf[:160]))
    print("=" * 90)
    print(f"classified: {len(notes)}")
    print(f"  what_found EMPTY:                     {empty}")
    print(f"  what_found has RESULT signal (good):  {signal}")
    print(f"  what_found POPULATED but NO signal:   {len(LEAK)}   <- precision risk (manufactured/noise)")
    print("=" * 90)
    if LEAK:
        print(f"PRECISION-RISK sample (populated-but-no-result-signal) -- up to 25 of {len(LEAK)}:")
        for name, wf in LEAK[:25]:
            req = " [REQUEST-LANG]" if REQ.search(wf) else ""
            print(f"  [{name[:60]}]{req}")
            print(f"     wf: {wf}")
    else:
        print("CLEAN: every populated what_found carries a result signal. Precision-guard holds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
