"""Pre-dispatch verify-the-referent gate.

Self-eval finding 2026-06-22: I burned cell-author spawns on cells whose smoke had
ALREADY landed HARD_FAIL today (HumanEval) or whose mechanism was already empirically
falsified by an adjacent cell (modern_hopfield_xl after substrate-mining would have
predicted no-cliff). A 30-second check before any cell-author spawn would have caught
both. This tool is that check.

Usage:
    python tools/predispatch_check.py <anchor_name_or_keywords>

Reports:
    - Any matching recent landings (last 30d) and their verdicts
    - Any matching atoms in the substrate (cert_status)
    - HOLD-or-PROCEED recommendation based on whether prior evidence is strong enough
      to predict the outcome

Banked discipline (this is the "Fix #26 pre-dispatch verify-the-referent gate"; see
feedback_fix26_*.md).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LANDINGS = REPO / "data" / "recent_landings.jsonl"
LEDGER = REPO / "data" / "substrate_index" / "meta" / "cert_ledger.jsonl"
ATOMS = REPO / "data" / "substrate_index" / "math" / "atoms.jsonl"
LOOKBACK_DAYS = 30


def _load_jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    out = []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def _matches(text: str, kws: list[str]) -> bool:
    t = text.lower()
    return any(kw.lower() in t for kw in kws)


def check(keywords: list[str], lookback_days: int = LOOKBACK_DAYS) -> dict:
    """Return dict with matching landings, atoms, and a recommendation."""
    cutoff = time.time() - lookback_days * 86400
    landings = _load_jsonl(LANDINGS)
    matching_landings = []
    for L in landings:
        cell = str(L.get("cell", ""))
        verdict = str(L.get("verdict", ""))
        if not _matches(cell, keywords) and not _matches(verdict, keywords):
            continue
        ts = L.get("ts", "")
        try:
            t_epoch = time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))
            if t_epoch < cutoff:
                continue
        except (ValueError, TypeError):
            pass
        matching_landings.append(L)

    matching_atoms = []
    if ATOMS.exists():
        for a in _load_jsonl(ATOMS):
            name = str(a.get("name", a.get("anchor", "")))
            verdict = str(a.get("verdict", ""))
            if _matches(name, keywords) or _matches(verdict, keywords):
                matching_atoms.append({
                    "name": name[:80],
                    "cert_status": a.get("cert_status", "?"),
                    "tier": a.get("tier", "?"),
                })

    n_hard_fail = sum(1 for L in matching_landings if "HARD_FAIL" in L.get("verdict", ""))
    n_hard_pass = sum(1 for L in matching_landings if "HARD_PASS" in L.get("verdict", ""))
    n_middle = sum(1 for L in matching_landings if "MIDDLE_BAND" in L.get("verdict", ""))
    n_chain_grade = sum(1 for a in matching_atoms if "chain_grade" in str(a.get("cert_status", "")))

    rec = "PROCEED"
    why = []
    if n_hard_fail >= 2 and n_hard_pass == 0:
        rec = "HOLD"
        why.append(f"{n_hard_fail} prior HARD_FAIL with zero HARD_PASS in {lookback_days}d window")
    if n_hard_fail >= 1 and n_hard_pass == 0 and any(L.get("elapsed_s", 0) > 600 for L in matching_landings):
        rec = "HOLD"
        why.append("prior HARD_FAIL at >10min wall (substantial compute already invested)")
    if n_chain_grade >= 1:
        why.append(f"{n_chain_grade} chain-grade atom(s) already exist — verify-the-referent: is this distinct?")

    return {
        "keywords": keywords,
        "lookback_days": lookback_days,
        "n_matching_landings": len(matching_landings),
        "n_hard_fail": n_hard_fail,
        "n_hard_pass": n_hard_pass,
        "n_middle_band": n_middle,
        "n_matching_atoms": len(matching_atoms),
        "n_chain_grade_atoms": n_chain_grade,
        "recent_landings": matching_landings[-5:],
        "atoms_sample": matching_atoms[:5],
        "recommendation": rec,
        "why": why,
    }


def main():
    p = argparse.ArgumentParser(description="Pre-dispatch verify-the-referent gate")
    p.add_argument("keywords", nargs="+", help="anchor name or keywords to search for")
    p.add_argument("--lookback", type=int, default=LOOKBACK_DAYS,
                   help=f"days of landings to consider (default {LOOKBACK_DAYS})")
    args = p.parse_args()
    r = check(args.keywords, args.lookback)
    print(f"[predispatch_check] keywords={r['keywords']} lookback={r['lookback_days']}d")
    print(f"  matching landings: {r['n_matching_landings']} (HARD_FAIL={r['n_hard_fail']}, "
          f"HARD_PASS={r['n_hard_pass']}, MIDDLE={r['n_middle_band']})")
    print(f"  matching atoms: {r['n_matching_atoms']} (chain_grade={r['n_chain_grade_atoms']})")
    if r["recent_landings"]:
        print("  recent landings:")
        for L in r["recent_landings"]:
            print(f"    {L.get('ts','?')[:19]} {str(L.get('cell','?'))[:55]:<55} "
                  f"{L.get('verdict','?')[:40]}")
    if r["atoms_sample"]:
        print("  matching atoms:")
        for a in r["atoms_sample"]:
            print(f"    {a['name']:<60} cert_status={a['cert_status']} tier={a['tier']}")
    print(f"  RECOMMENDATION: {r['recommendation']}")
    if r["why"]:
        for w in r["why"]:
            print(f"    - {w}")
    return 0 if r["recommendation"] == "PROCEED" else 1


if __name__ == "__main__":
    sys.exit(main())
