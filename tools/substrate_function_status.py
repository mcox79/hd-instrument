"""Where does every substrate function actually stand? -- enumerate from DISK, then reconcile.

**OWNER, 2026-08-21: *"Where are we on the different functions of substrate?"*** This answers it by
measurement rather than from the registry, because `CLAUDE.md` records that the registry's
`pipeline_status` is **wrong in BOTH directions** -- 19 rows claim `WIRED_BUT_NOT_PIPELINE_REACHABLE`
while measurably live, and 3 claim the reverse.

**THE ORDER MATTERS AND IS THE PROJECT'S OWN RULE:** *"enumerate from the filesystem, then reconcile
to the registry, never the reverse"* -- two audits missed a whole working subsystem by asking "does
the registry match disk?" instead of "what is on disk?".

**AND THE THIRD COLUMN IS THE ONE NEITHER OF THE OTHER TWO CAN GIVE: does a LIVE READ load it?**
*Static search gets this wrong in both directions in the same file -- three modules are imported
inside a function body and invisible to grep, while two names appear only in a string constant and a
comment. So reachability is measured by running the code and inspecting `sys.modules`.*

⚠️ **SCOPE, STATED SO IT CANNOT BE OVER-READ.** "Loaded by a live read" means loaded by
`Substrate().read()`. **A module absent from that column is NOT dead** -- it may serve query,
consolidation, or a different entry point entirely. It means only that the READING path does not
touch it.
"""
from __future__ import annotations

import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

REGISTRY = os.path.join(_REPO, "data", "capability_registry.jsonl")


def main():
    # ---- 1. ENUMERATE FROM DISK. Not from the registry.
    hdlab = os.path.join(_REPO, "hdlab")
    on_disk = sorted(f[:-3] for f in os.listdir(hdlab)
                     if f.endswith(".py") and not f.startswith("_"))

    # ---- 2. REGISTRY, reconciled TO the disk list
    reg = {}
    if os.path.exists(REGISTRY):
        for line in open(REGISTRY, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            for p in (d.get("path") or []):
                base = os.path.basename(str(p))
                if base.endswith(".py"):
                    reg.setdefault(base[:-3], []).append(d)

    # ---- 3. RUNTIME: what a live read actually loads
    import hdlab.substrate as S
    sub = S.Substrate()
    sub.read(n_sentences=60)
    live = {m.split(".")[-1] for m in sys.modules if m.startswith("hdlab.")}

    rows = []
    for m in on_disk:
        rs = reg.get(m, [])
        gate = rs[0].get("gate_decision", "-") if rs else "-"
        rows.append((m, bool(rs), gate, m in live))

    n_reg = sum(1 for _, r, _, _ in rows if r)
    n_live = sum(1 for _, _, _, l in rows if l)
    print("=" * 92)
    print("SUBSTRATE FUNCTION STATUS -- %d modules on disk, %d registered, %d loaded by a LIVE READ"
          % (len(rows), n_reg, n_live))
    print("=" * 92)

    print("\n--- LOADED BY A LIVE READ (the reading path actually runs these) ---")
    for m, r, g, l in rows:
        if l:
            print("  %-42s registry=%-4s gate=%s" % (m, "yes" if r else "NO", g))

    print("\n--- REGISTERED, GATE=WIRE, BUT NOT LOADED BY A LIVE READ ---")
    print("    (built and blessed, but the reading path never calls them --")
    print("     this is the WIRE-DON'T-ISLAND gap, and it is where the answer to")
    print("     'why did reading stall' is most likely to be found)")
    islanded = [(m, g) for m, r, g, l in rows if r and not l and str(g).upper().startswith("WIRE")]
    for m, g in islanded:
        print("  %-42s gate=%s" % (m, g))
    print("    -> %d modules" % len(islanded))

    print("\n--- ON DISK BUT NOT IN THE REGISTRY AT ALL ---")
    print("    (a registry-first audit is structurally blind to these)")
    unreg = [m for m, r, _, l in rows if not r]
    for i in range(0, min(len(unreg), 60), 3):
        print("  " + "  ".join("%-28s" % x for x in unreg[i:i + 3]))
    print("    -> %d modules, %d of which a live read DOES load"
          % (len(unreg), sum(1 for m in unreg if m in live)))

    print("\n" + "=" * 92)
    print("HOW TO READ THIS. Column 3 is the only one measured at RUNTIME and it answers exactly one")
    print("question: does the READING path touch this module. A module missing from it is NOT dead --")
    print("it may serve query, consolidation or another entry point. The registry columns are")
    print("reconciled TO the disk enumeration, never the other way round.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
