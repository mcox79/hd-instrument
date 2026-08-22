"""RE-SCORE EVERY LANDED CELL AGAINST THE STRONGEST FLOOR IT ALREADY HAS ON DISK.

**THE 2026-08-18 AUDIT NAMED THIS "THE CHEAPEST FIX IN THE WHOLE BACKLOG, and it needs no new
experiment":** *"SEVERAL CELLS ALREADY COMPUTED THE RIGHT FLOOR AND THEN DISCRIMINATED AGAINST
SOMETHING ELSE."* It was named and never done. This does it.

IT IS ALSO PERSONAL. On 2026-08-19 I reported the assembled substrate as "losing to counting by
~10x" against a `COUNT_FLOOR` of 0.0125 -- while a stronger floor computable from the same data,
cosine over the same co-occurrence counts, scored 0.0300. **I committed the exact defect this tool
looks for, in a cell I wrote to catch that class of thing.** The rule is not hard to state and it
is evidently hard to follow, which is why it should be a tool and not a habit.

WHAT IT DOES. For every `metrics.json` under `data/`, it finds all FLOOR-LIKE numbers and all
TREATMENT-LIKE numbers, and flags two things:
  FLOOR_BEATS_TREATMENT  a floor the cell ITSELF computed is >= its own best treatment value.
  WEAKER_FLOOR_QUOTED    the cell's verdict text names a floor number that is NOT the largest
                         floor in its own metrics.

WHAT IT IS NOT. It is a TRIAGE that produces a READ LIST, not a verdict. Numeric keys are
heuristically classified and a cell can legitimately hold floors for several different arms,
populations or scorers -- comparing across those would be the very error this tool exists to
catch. **Every hit must be read by a human before it is called a defect.** Keep EXISTS /
IS-REACHED / IS-GOOD separate: this measures EXISTS.

USAGE
  python tools/strongest_floor_audit.py
  python tools/strongest_floor_audit.py --json --limit 0
  python tools/strongest_floor_audit.py --self-test
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(REPO, "data")

FLOOR_KEY = re.compile(
    r"floor|baseline|chance|majority|random|shuffle|scramble|control|null|naive|dumb|prior|"
    r"most_frequent|constant|prototype", re.I)
TREAT_KEY = re.compile(
    r"^(acc|accuracy|score|hit|hit@1|recall|precision|f1|auc|rho|correct|rate|mean_|delta_)"
    r"|_acc$|_score$|_auc$|_f1$|treatment|system|full|real|main|arm_", re.I)
# Keys that are counts, sizes, seeds or times, never a metric.
NOT_A_METRIC = re.compile(
    r"^n_|_n$|count|size|seed|dim|elapsed|second|_ms$|_utc$|idx|index|version|total_|steps?$|"
    r"epoch|budget|threshold|tau|alpha|beta|gamma|lr$|_id$", re.I)

# A DIFFERENCE IS NOT A FLOOR. `gate.real_minus_shuffle` matched the floor pattern on the word
# "shuffle" and was read as a 0.4592 floor -- it is a MARGIN. Caught on the first real run, and
# it is the same shape as every other defect in this file: a name that looks like the thing.
IS_A_DELTA = re.compile(r"minus|delta|diff|lift|gain|margin|_vs_|improve|change|drop", re.I)

# A cell that already calls itself a failure is not the interesting case. The defect this tool
# exists for is a cell claiming a PASS while its OWN floor beats its OWN treatment.
CLAIMS_A_PASS = re.compile(r"PASS|GREEN|UPHELD|MIDDLE", re.I)

# A self-test or a smoke is plumbing verification at tiny n. Its "PASS" means the code paths ran.
IS_NOT_A_RESULT = re.compile(r"selftest|self_test|smoke|gate_only|dry_run", re.I)


def _walk(obj, prefix: str, out: List[Tuple[str, float]], depth: int = 0) -> None:
    if depth > 5:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            _walk(v, f"{prefix}.{k}" if prefix else str(k), out, depth + 1)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:40]):
            _walk(v, f"{prefix}[{i}]", out, depth + 1)
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        try:
            f = float(obj)
        except (TypeError, ValueError):
            return
        # Metric-shaped only: a proportion. Keeps counts, losses and timings out.
        if 0.0 <= f <= 1.0:
            out.append((prefix, f))


def scan(path: str) -> Optional[Dict]:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            m = json.load(fh)
    except (OSError, json.JSONDecodeError, ValueError):
        return None
    if not isinstance(m, dict):
        return None
    vals: List[Tuple[str, float]] = []
    _walk(m, "", vals)
    floors = [(k, v) for k, v in vals
              if FLOOR_KEY.search(k) and not NOT_A_METRIC.search(k.split(".")[-1])
              and not IS_A_DELTA.search(k)]
    treats = [(k, v) for k, v in vals
              if TREAT_KEY.search(k.split(".")[-1]) and not FLOOR_KEY.search(k)
              and not NOT_A_METRIC.search(k.split(".")[-1])
              and not IS_A_DELTA.search(k)]
    if not floors or not treats:
        return None
    # Only cells that CLAIM something. A self-declared HARD_FAIL whose floor beats it is not a
    # defect, it is a cell being correct.
    claim = " ".join(str(m.get(k, "")) for k in ("verdict", "tier", "band"))
    if not CLAIMS_A_PASS.search(claim):
        return None
    # A SELF-TEST'S "PASS" IS NOT A CAPABILITY CLAIM, and this exclusion exists because the tool's
    # single most striking hit was one. `diag_stateful_core_gen_curve_v1` showed a random-init
    # control at 0.6250 beating a TRAINED arm at 0.5000 under a `SELFTEST_PASS` -- the
    # untrained-beats-trained shape this project has genuinely recorded once before. Checked it:
    # `run_mode: "selftest"`, and the cell's own message says "exercised at N~4-16". It was
    # verifying that code paths RUN, not claiming training worked. Not a defect.
    # The CELL NAME counts too: several `..._selftest` directories carry `verdict: HARD_PASS` and
    # a run_mode that does not say so, so filtering on run_mode alone let them straight back in.
    cell_name = os.path.basename(os.path.dirname(path))
    if IS_NOT_A_RESULT.search(str(m.get("run_mode", "")) + " " + claim + " " + cell_name):
        return None
    best_floor = max(floors, key=lambda t: t[1])
    best_treat = max(treats, key=lambda t: t[1])

    verdict = " ".join(str(m.get(k, "")) for k in ("verdict", "verdict_msg", "headline"))
    quoted = [float(x) for x in re.findall(r"0\.\d{2,6}", verdict)]
    weaker_quoted = None
    if quoted:
        near_floor = [q for q in quoted if any(abs(q - v) < 1e-6 for _, v in floors)]
        if near_floor and max(near_floor) < best_floor[1] - 1e-9:
            weaker_quoted = (max(near_floor), best_floor[1])

    flags = []
    # STRICTLY GREATER. `>=` fired on 1.0000 vs 1.0000 ties -- a tie at ceiling is a saturated
    # measurement, not a floor beating a treatment, and it flooded the first run with noise.
    if best_floor[1] > best_treat[1] + 1e-9:
        flags.append("FLOOR_BEATS_TREATMENT")
    if weaker_quoted:
        flags.append("WEAKER_FLOOR_QUOTED")
    if not flags:
        return None
    return {"cell": os.path.basename(os.path.dirname(path)),
            "flags": flags,
            "best_floor": {"key": best_floor[0], "value": best_floor[1]},
            "best_treatment": {"key": best_treat[0], "value": best_treat[1]},
            "weaker_floor_quoted": weaker_quoted,
            "n_floors": len(floors), "n_treatments": len(treats),
            "verdict": (str(m.get("verdict", "")) or "")[:40]}


def self_test() -> int:
    ok = True

    def check(c, label):
        nonlocal ok
        print(f"[self-test] {'PASS' if c else 'FAIL'} {label}",
              file=sys.stdout if c else sys.stderr)
        ok = ok and bool(c)

    import tempfile
    td = tempfile.mkdtemp(prefix="floors_")

    def mk(name, obj):
        d = os.path.join(td, name)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "metrics.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(obj, fh)
        return p

    a = scan(mk("a", {"accuracy": 0.40, "random_floor": 0.55, "verdict": "HARD_PASS"}))
    check(a and "FLOOR_BEATS_TREATMENT" in a["flags"],
          "flags a cell whose OWN floor beats its OWN treatment")

    b = scan(mk("b", {"accuracy": 0.90, "weak_floor": 0.10, "majority_floor": 0.80,
                      "verdict": "HARD_PASS", "verdict_msg": "beats floor 0.10"}))
    check(b and "WEAKER_FLOOR_QUOTED" in b["flags"],
          "flags a cell that QUOTED 0.10 while its own metrics hold a 0.80 floor")

    c = scan(mk("c", {"accuracy": 0.90, "majority_floor": 0.55,
                      "verdict_msg": "beats floor 0.55"}))
    check(c is None, "stays silent when the strongest floor IS the one quoted")

    d = scan(mk("d", {"n_items": 500, "seed": 7, "elapsed_s": 0.9}))
    check(d is None, "ignores counts, seeds and timings -- they are not metrics")

    e = scan(mk("e", {"accuracy": 0.9}))
    check(e is None, "stays silent when there is no floor to compare against")
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    n_files = 0
    hits: List[Dict] = []
    for name in sorted(os.listdir(DATA)):
        p = os.path.join(DATA, name, "metrics.json")
        if not os.path.isfile(p):
            continue
        n_files += 1
        r = scan(p)
        if r:
            hits.append(r)
    # ROWS SCANNED BEFORE RESULTS, always -- silence must never read as absence.
    print(f"[floors] scanned {n_files} metrics.json files under data/")
    print(f"[floors] {len(hits)} cell(s) flagged")
    # THE FLAG COUNT IS NOT A DEFECT COUNT, AND PRINTING IT ALONE IS HOW THAT WAS FORGOTTEN.
    # On 2026-08-22 this number ("238") became a standing operator item asserting that many
    # results overstated their claim. Re-adjudicated: 72.4% of flags compare two numbers this
    # project's own rule forbids comparing. The caution at the BOTTOM of this output said so all
    # along -- it just arrived 20 lines after the number, and only the number travelled.
    # So the decomposition is printed HERE, beside the count it qualifies.
    try:
        from tools.adjudicate_floor_flags import adjudicate      # late: it imports scan() from us
        d = {}
        for h in hits:
            k = adjudicate(h)["disposition"]
            d[k] = d.get(k, 0) + 1
        n = max(1, len(hits))
        print("[floors] OF THOSE FLAGS -- a flag is not a defect:")
        for k in sorted(d, key=lambda x: -d[x]):
            print(f"    {k:24s} {d[k]:4d}  ({100 * d[k] / n:.1f}%)")
        print("    (INADMISSIBLE_COMPARISON = the two numbers may not be compared at all.)")
    except Exception as e:                                       # never let this break the audit
        print(f"[floors] (adjudication unavailable: {e})")
    by = {}
    for h in hits:
        for f in h["flags"]:
            by.setdefault(f, []).append(h)
    for f, rows in sorted(by.items()):
        print(f"    {f:24s} {len(rows)}")
    if a.json:
        print(json.dumps({"n_files": n_files, "hits": hits}, indent=2))
        return 0
    show = hits if a.limit == 0 else hits[:a.limit]
    print(f"\nFIRST {len(show)} -- A READ LIST, NOT A VERDICT:\n")
    for h in show:
        print(f"  {h['cell']}  [{','.join(h['flags'])}]  verdict={h['verdict']}")
        print(f"      best floor     {h['best_floor']['value']:.4f}  ({h['best_floor']['key']})")
        print(f"      best treatment {h['best_treatment']['value']:.4f}  "
              f"({h['best_treatment']['key']})")
        if h["weaker_floor_quoted"]:
            print(f"      QUOTED {h['weaker_floor_quoted'][0]:.4f} while holding "
                  f"{h['weaker_floor_quoted'][1]:.4f}")
    print("\nTHIS MEASURES *EXISTS*. A cell may legitimately hold floors for different arms, "
          "populations or scorers -- comparing across those is the very error this looks for, "
          "so every hit needs a human read before it is called a defect.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
