#!/usr/bin/env python
"""wiring_debt.py -- the DERIVED, rot-proof wiring-debt view.

Answers ONE question the owner keeps asking: of everything we built, what is
actually WIRED into the live reader, what is a promoted-but-islanded organ, and
what earned a landing that was never even promoted to hdlab/?

Derives everything from disk on every run (like substrate_map.py) so it cannot
go stale:
  - notes/problems/*/SOLVED.md   -> integrated? landing state? wiring hint?
  - data/capability_registry.jsonl -> integration_status + gate_decision_target
  - hdlab/situation_reader.py + substrate.py -> what the LIVE path imports
  - hdlab/*.py -> what has been promoted at all

Usage:
  python tools/wiring_debt.py            # summary tiers + counts
  python tools/wiring_debt.py --full     # every item with its wire-step
  python tools/wiring_debt.py --tier promotion|wiring|negative|live
Companion human ledger: notes/WIRING_MAP.md (refresh it from this tool).
"""
import json, os, re, glob, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROB = os.path.join(ROOT, "notes", "problems")
REG = os.path.join(ROOT, "data", "capability_registry.jsonl")

def live_imports():
    mods = set()
    for f in ("hdlab/situation_reader.py", "hdlab/substrate.py"):
        p = os.path.join(ROOT, f)
        if not os.path.isfile(p):
            continue
        t = open(p, encoding="utf-8", errors="ignore").read()
        for m in re.finditer(r"from hdlab\.([a-z_][a-z0-9_]*)", t):
            mods.add(m.group(1))
        for m in re.finditer(r"import hdlab\.([a-z_][a-z0-9_]*)", t):
            mods.add(m.group(1))
    return mods

def hdlab_modules():
    return {os.path.splitext(os.path.basename(p))[0]
            for p in glob.glob(os.path.join(ROOT, "hdlab", "*.py"))}

def classify_submissions():
    out = []
    for d in sorted(glob.glob(os.path.join(PROB, "*"))):
        slug = os.path.basename(d)
        sol = os.path.join(d, "SOLVED.md")
        own = os.path.join(d, "OWNER_NOTES.md")
        if not os.path.isfile(sol):
            continue
        stext = open(sol, encoding="utf-8", errors="ignore").read()
        if "INTEGRATED_BY_STRATEGY" not in stext:
            continue
        blk = stext[stext.find("INTEGRATED_BY_STRATEGY"):]
        low = blk.lower()
        if re.search(r"no hdlab landing|no landing earned|net-zero|route closed|rigorous negative", low):
            state = "negative"
        elif re.search(r"landing queued|queued \(q111|landing next|queued proven-ready|remains the one queued|queued coupled|landing earned", low):
            state = "queued"
        elif re.search(r"landed|promoted.*hdlab|wired|registered", low):
            state = "landed"
        else:
            state = "unclear"
        hint = ""
        for m in re.finditer(r"[^.]*\b(promote `?hdlab|promote `?experiments|wire [a-z]|hdlab landing|coupled|needs the|blocked on|default-off)\b[^.]*\.", blk, re.I):
            h = m.group(0).strip().replace("\n", " ")
            h = re.sub(r"\s+", " ", h)
            if len(h) > 40:
                hint = h[:260]; break
        out.append({"slug": slug, "state": state, "hint": hint})
    return out

def registry_rows():
    rows = []
    if not os.path.isfile(REG):
        return rows
    for line in open(REG, encoding="utf-8", errors="ignore"):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows

def main():
    full = "--full" in sys.argv
    live = live_imports()
    hd = hdlab_modules()
    subs = classify_submissions()
    reg = registry_rows()

    st = collections.Counter(s["state"] for s in subs)
    print("=" * 78)
    print("WIRING DEBT -- derived from disk (%d integrated submissions)" % len(subs))
    print("=" * 78)
    print("Landing state of integrated submissions:")
    for k in ("landed", "queued", "negative", "unclear"):
        print("  %-10s %d" % (k, st.get(k, 0)))

    # registry integration tiers
    rc = collections.Counter(r.get("integration_status", "?") for r in reg)
    live_reach = island = 0
    for r in reg:
        if r.get("integration_status") != "WIRED":
            continue
        ub = r.get("used_by") or []
        if any(("situation_reader" in u) or ("substrate.py" in u) for u in ub):
            live_reach += 1
        elif ub and all(("verification/" in u) or ("experiments/" in u) or ("composed-reachable" in u) for u in ub):
            island += 1
    print()
    print("Registry (%d capabilities):" % len(reg))
    for k, v in rc.most_common():
        print("  %-16s %d" % (k, v))
    print("  of WIRED: reach the LIVE reader/substrate: %d ; island-only: %d" % (live_reach, island))
    print()
    print("LIVE reader/substrate imports %d hdlab modules (of %d total in hdlab/):" % (len(live), len(hd)))
    print("  " + ", ".join(sorted(live)))

    if full:
        print()
        print("--- QUEUED landings (earned, not confirmed live) ---")
        for s in subs:
            if s["state"] == "queued":
                print("  * " + s["slug"])
                if s["hint"]:
                    print("      " + s["hint"])
        print()
        print("--- NEGATIVE (correct no-landing; DO NOT re-attempt) ---")
        for s in subs:
            if s["state"] == "negative":
                print("  * " + s["slug"])
    print()
    print("Refresh the human ledger notes/WIRING_MAP.md from this view. "
          "Registry is the machine source of truth for per-organ status.")

if __name__ == "__main__":
    main()
