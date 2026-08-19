"""MINE MIDDLE_BAND FOR THE ATTEMPT AND THE SIGNAL -- NOT FOR THE VERDICT.

OWNER, 2026-08-18, and the brief is the whole point: *"mine the middle band. it's worth it.
understanding what it was trying and the signal may be very important for the harder to obtain
capabilities."*

WHY THIS POPULATION AND NOT HARD_PASS. **Building the vetting queue from HARD_PASS SELECTED FOR
OVER-CLAIMING.** Two cells were found on 2026-08-18 whose HONEST tier was MIDDLE_BAND while an
over-claimed sibling took HARD_PASS -- and of 30 HARD_PASS cells vetted across five passes, ONE
survived. MIDDLE_BAND is where the honest self-assessments went. 117 meaning-relevant MIDDLE_BAND
cells had never been read by anyone.

WHAT THIS EXTRACTS, AND THE ORDERING IS DELIBERATE:
  1. WHAT IT WAS TRYING  -- the docstring headline and the mechanism words in it.
  2. WHAT SIGNAL IT SAW  -- the numeric deltas, correlations and rates in its own metrics, and
                            whether it carried a CI, a null, a floor or a scramble.
  3. WHAT IT SAID ABOUT ITSELF -- `honest_limitations`, `caveat`, `why_middle_band` and similar
                            self-assessment fields. THIS POPULATION IS SELECTED FOR HAVING THEM.
The VERDICT is recorded last and carries no weight. A MIDDLE_BAND verdict is not evidence the
attempt was wrong; it is usually evidence the author was honest about power or scope.

WHAT IT IS NOT. It is not a vetting pass and it does not bless anything. Nothing it surfaces may
be cited as a result -- `tools/vetting_ledger.py --cite` still governs that, and it still refuses
every cell in here. This produces a READ LIST ranked by how much MECHANISM is in the cell.

USAGE
  python tools/middle_band_miner.py                 # ranked digest
  python tools/middle_band_miner.py --n 25          # deeper
  python tools/middle_band_miner.py --json
  python tools/middle_band_miner.py --self-test
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(REPO, "data")

MIDDLE = re.compile(r"MIDDLE[_ ]?BAND", re.I)

# Substrate-physics cells are excluded: capacity, scaling laws, binding algebra, Hopfield limits.
# They are real work and they are not what "meaning-relevant" means.
PHYSICS = re.compile(
    r"capacity|scaling_law|hopfield|binding_operator|bundle_load|crosstalk|d_sweep|dimension_sweep|"
    r"fhrr_|hrr_|vsa_algebra|codebook_size", re.I)

MEANING = re.compile(
    r"meaning|semantic|word|lexic|concept|definition|ground|comprehen|read|sense|role|frame|"
    r"coref|infer|relation|analog|categor|taxonom|thematic|substitut|paradigmatic", re.I)

# Self-assessment fields. THIS POPULATION IS SELECTED FOR HAVING THEM -- that is the thesis.
SELF_ASSESS_KEYS = ("honest_limitations", "limitations", "caveat", "caveats", "why_middle_band",
                    "middle_band_reason", "honest_scope", "scope", "known_issues",
                    "what_would_settle_it", "next_step", "interpretation")

EVIDENCE = {
    "ci": re.compile(r"ci_low|ci_lo|ci_hi|conf_int|half_width|bootstrap", re.I),
    "null": re.compile(r"permutation|perm_p|null_dist|shuffle_null|p_value|binomtest", re.I),
    "floor": re.compile(r"floor|baseline|chance|majority", re.I),
    "scramble": re.compile(r"scramble|scrambled", re.I),
    "heldout": re.compile(r"held_?out|heldout|test_split|generaliz", re.I),
}

MECHANISM = re.compile(
    r"learn|update rule|write rule|error|gradient|delta|predict|gate|attractor|complete|"
    r"consolidat|replay|induc|bootstrap|transfer|compos", re.I)


def _num_signals(obj, out: List[float], depth: int = 0) -> None:
    """Every finite number in the metrics, so 'what signal did it see' is read from DATA."""
    if depth > 6:
        return
    if isinstance(obj, dict):
        for v in obj.values():
            _num_signals(v, out, depth + 1)
    elif isinstance(obj, list):
        for v in obj[:200]:
            _num_signals(v, out, depth + 1)
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        try:
            f = float(obj)
            if f == f and abs(f) < 1e12:
                out.append(f)
        except (TypeError, ValueError):
            pass


def scan_cell(d: str) -> Optional[Dict]:
    mp = os.path.join(d, "metrics.json")
    if not os.path.isfile(mp):
        return None
    try:
        with open(mp, "r", encoding="utf-8", errors="replace") as fh:
            m = json.load(fh)
    except (OSError, json.JSONDecodeError, ValueError):
        return None
    blob = json.dumps(m, default=str)
    if not MIDDLE.search(blob):
        return None
    name = os.path.basename(d)
    if PHYSICS.search(name):
        return None
    if not MEANING.search(name + " " + blob[:4000]):
        return None

    self_assess = {}
    if isinstance(m, dict):
        for k in SELF_ASSESS_KEYS:
            if k in m and m[k]:
                self_assess[k] = str(m[k])[:500]

    ev = {k: bool(p.search(blob)) for k, p in EVIDENCE.items()}
    nums: List[float] = []
    _num_signals(m, nums)
    interesting = [n for n in nums if 0.0 < abs(n) < 1.0]

    src = os.path.join(REPO, "experiments", name + ".py")
    head = ""
    if os.path.isfile(src):
        try:
            with open(src, "r", encoding="utf-8", errors="replace") as fh:
                txt = fh.read(4000)
            mm = re.search(r'"""(.{20,900}?)"""', txt, re.S)
            if mm:
                head = " ".join(mm.group(1).split())[:420]
        except OSError:
            pass

    mech = len(set(x.lower() for x in MECHANISM.findall(head + " " + blob[:6000])))
    score = (3 * len(self_assess) + 2 * mech + 2 * sum(ev.values())
             + (2 if head else 0))
    return {"cell": name, "score": score, "trying": head,
            "self_assessment": self_assess, "evidence": ev,
            "n_numbers": len(nums), "n_sub_unit_numbers": len(interesting),
            "mechanism_words": mech,
            "verdict_last": (str(m.get("verdict", "")) or "")[:60] if isinstance(m, dict) else ""}


HARD = re.compile(r"HARD[_ ]?PASS", re.I)


def scan_cell_tier(d: str, tier_pat) -> Optional[Dict]:
    """scan_cell with the tier pattern swapped. EXISTS SO THE TWO POPULATIONS ARE MEASURED BY THE
    IDENTICAL DETECTOR -- comparing my percentages against another tool's would be exactly the
    cross-scorer comparison this project forbids (standing discipline 11)."""
    global MIDDLE
    prev = MIDDLE
    MIDDLE = tier_pat
    try:
        return scan_cell(d)
    finally:
        MIDDLE = prev


def run(tier_pat=None) -> tuple:
    tier_pat = tier_pat if tier_pat is not None else MIDDLE
    dirs = [os.path.join(DATA, x) for x in os.listdir(DATA)
            if os.path.isdir(os.path.join(DATA, x))]
    hits = []
    for d in dirs:
        r = scan_cell_tier(d, tier_pat)
        if r:
            hits.append(r)
    hits.sort(key=lambda h: (-h["score"], h["cell"]))
    return len(dirs), hits


def compare() -> int:
    """Test the PLAN'S OWN PREMISE: is MIDDLE_BAND really where the honest self-assessments went?

    Same detector, same directories, same fields -- only the tier pattern differs. If the premise
    is right, MIDDLE_BAND should carry self-assessment and controls at a HIGHER rate. If it is
    wrong, that is worth more than another read list, because the owner authorised work on it.
    """
    n_dirs, mb = run(MIDDLE)
    _, hp = run(HARD)
    print(f"[compare] scanned {n_dirs} result directories, IDENTICAL detector on both tiers")
    print(f"[compare] MIDDLE_BAND {len(mb)} meaning-relevant | HARD_PASS {len(hp)}\n")
    rows = [("states a limitation about itself",
             lambda h: bool(h["self_assessment"]))]
    for k in ("ci", "null", "floor", "scramble", "heldout"):
        rows.append((f"carries a {k}", (lambda kk: (lambda h: h["evidence"][kk]))(k)))
    print(f"  {'property':38s} {'MIDDLE_BAND':>14s} {'HARD_PASS':>14s}   verdict")
    for label, fn in rows:
        a = sum(1 for h in mb if fn(h)) / max(len(mb), 1)
        b = sum(1 for h in hp if fn(h)) / max(len(hp), 1)
        tag = "MB higher" if a > b + 0.02 else ("HP higher" if b > a + 0.02 else "no difference")
        print(f"  {label:38s} {a * 100:13.1f}% {b * 100:13.1f}%   {tag}")
    print("\nNOTE THE DENOMINATORS AND DO NOT CROSS THEM WITH ANY OTHER TOOL'S. This is a "
          "same-detector comparison and its percentages are only meaningful against each other.")
    return 0


def self_test() -> int:
    ok = True

    def check(c, label):
        nonlocal ok
        print(f"[self-test] {'PASS' if c else 'FAIL'} {label}",
              file=sys.stdout if c else sys.stderr)
        ok = ok and bool(c)

    import tempfile
    td = tempfile.mkdtemp(prefix="mbminer_")

    def mk(name, obj):
        p = os.path.join(td, name)
        os.makedirs(p, exist_ok=True)
        with open(os.path.join(p, "metrics.json"), "w", encoding="utf-8") as fh:
            json.dump(obj, fh)
        return p

    a = mk("exp_word_meaning_thing_v1",
           {"verdict": "MIDDLE_BAND", "honest_limitations": "n too small",
            "delta": 0.12, "perm_p": 0.03, "ci_low": 0.01})
    r = scan_cell(a)
    check(r is not None, "finds a meaning-relevant MIDDLE_BAND cell")
    check(r and r["self_assessment"].get("honest_limitations"),
          "extracts the self-assessment field, which is the thesis of this population")
    check(r and r["evidence"]["ci"] and r["evidence"]["null"],
          "detects that it carried a CI and a null")

    b = mk("exp_hard_pass_thing_v1", {"verdict": "HARD_PASS", "delta": 0.2})
    check(scan_cell(b) is None, "ignores HARD_PASS -- that population is selected for over-claiming")

    c = mk("exp_capacity_scaling_law_v1", {"verdict": "MIDDLE_BAND", "delta": 0.2})
    check(scan_cell(c) is None, "excludes substrate-physics cells (capacity/scaling)")

    d = mk("exp_empty_v1", {})
    check(scan_cell(d) is None, "ignores a cell with no verdict at all")

    print(f"[self-test] leftover temp dir (not auto-removed, by design): {td}")
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--compare", action="store_true",
                    help="test the plan's premise: same detector on MIDDLE_BAND vs HARD_PASS")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.compare:
        return compare()

    n_dirs, hits = run()
    # ROWS SCANNED BEFORE RESULTS, always.
    print(f"[middle-band] scanned {n_dirs} result directories under data/")
    print(f"[middle-band] {len(hits)} meaning-relevant MIDDLE_BAND cells")
    if a.json:
        print(json.dumps({"n_dirs": n_dirs, "hits": hits}, indent=2))
        return 0
    with_self = sum(1 for h in hits if h["self_assessment"])
    print(f"[middle-band] {with_self} of them state a limitation ABOUT THEMSELVES "
          f"({100.0 * with_self / max(len(hits), 1):.0f}%)")
    for k in ("ci", "null", "floor", "scramble", "heldout"):
        n = sum(1 for h in hits if h["evidence"][k])
        print(f"    carries a {k:9s} {n:4d}  ({100.0 * n / max(len(hits), 1):.0f}%)")
    print(f"\nTOP {a.n} BY HOW MUCH MECHANISM IS IN THEM -- a READ LIST, not a result list:\n")
    for h in hits[:a.n]:
        print(f"  [{h['score']:3d}] {h['cell']}")
        if h["trying"]:
            print(f"        TRYING: {h['trying'][:220]}")
        for k, v in list(h["self_assessment"].items())[:2]:
            print(f"        SAYS ({k}): {v[:200]}")
    print("\nNOTHING HERE IS CITABLE. tools/vetting_ledger.py --cite still governs, and it still "
          "refuses every one of these.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
