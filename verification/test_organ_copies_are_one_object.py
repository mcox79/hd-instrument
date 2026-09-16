"""Standing witness: for every `hdlab/X.py` that has an `experiments/_X.py`, the two must be ONE OBJECT.

WHY THIS EXISTS.  Twice in one day the same defect was found by hand: a module promoted into `hdlab/`, the
live reader repointed at the organ, and the `experiments/_X.py` copy left behind for every cell and witness
to keep importing.  The two then drift, and the MEASUREMENTS describe a module the product does not run.

  pri 137  `_space_reader`   -- drifted four landings; a witness stubbed a function the reader had stopped
                               running, so both of its arms ran the lever ON and it could not fail.
  pri 139  `_belief_reader`  -- drifted one landing (the 2026-09-09 spaCy purge); W15 of
                               test_belief_at_t_end_to_end_organ.py reported `status_register_recall 0.600`
                               from a spaCy branch deleted from the organ.  On the organ it is 0.000.

Both were found by a person noticing.  This file is the mechanical version, so the THIRD one is found by a
test run instead.

HOW IT CLASSIFIES (and it resolves ONE level of hdlab-side re-export shim, because
`hdlab/temporal_order_register.py` is 34 lines that re-export `hdlab/temporal_model.py` -- comparing the
experiments copy against the shim would score "unrelated" and hide a real drift):

  ALIAS            the experiments file ends in `sys.modules[__name__] = <organ>`  -- ONE OBJECT. The goal.
  THIN SHIM        the experiments file is SHORT (<= 60 lines) and imports the organ -- no second
                   implementation, so no drift is possible.  The line cap matters:
                   `experiments/_structured_matcher.py` imports from hdlab and declares only two top-level
                   names, but it is 354 lines of its own implementation, so a "few names" rule would have
                   mis-cleared a real drifted copy.
  EXACT DUPLICATE  two files, byte-identical modulo trailing whitespace -- no drift TODAY, but two objects,
                   so it is one landing away from becoming a DRIFTED COPY. Reported, not failed.
  DRIFTED COPY     two independent implementations that already disagree. THE DEFECT.
  UNRELATED        no shared top-level def/class name -- not a promotion pair.

WHAT IT ASSERTS (it is GREEN today with 14 known drifted pairs, and can fail in three ways):
  W1  CENSUS COMPLETE -- every pair on disk is classified; nothing UNCLASSIFIED.
  W2  NO NEW DRIFT -- no drifted pair outside the dated baseline below.  A newly promoted module whose copy
      is left behind fails HERE, on the day it happens.
  W3  NO REGRESSION -- a pair recorded as COLLAPSED must still be ONE OBJECT.  Un-aliasing a collapsed pair
      fails here.
  W4  THE COLLAPSED PAIRS ARE REALLY ONE OBJECT -- asserted by IDENTITY at import (`is`), not by reading the
      source, so a file that merely LOOKS like an alias does not pass.

The baseline is an INVENTORY THAT SHOULD SHRINK, not a permanent allowance.  Every name in
KNOWN_DRIFTED is a LOCATED item for strategy; remove it from the list when its collapse lands.

Glass-box, NO LLM, deterministic, ASCII, CPU-only.  Reads source and imports modules; writes nothing.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# ---------------------------------------------------------------------------------------------------
# THE BASELINE, measured 2026-09-16.  16 hdlab/experiments pairs on disk.
# ---------------------------------------------------------------------------------------------------
# Pairs already collapsed to ONE OBJECT (must STAY collapsed -- W3/W4).
COLLAPSED = set([
    # "belief_reader",   # <- pri 139; uncomment when belief_one_organ_patch.diff lands
    # "space_reader",    # <- pri 137; uncomment when space_ground_lever_patch.diff lands
])

# Pairs KNOWN to be two drifting implementations on 2026-09-16.  Each one is a LOCATED item.
# Remove a name when its collapse lands; a name NOT in this set that is found drifted fails W2.
KNOWN_DRIFTED = {
    "aspect_interval",
    "belief_reader",                  # pri 139 -- diff written, awaiting landing
    "causal_network",
    "causal_reasoner",
    "composed_hub_predictor",
    "joint_relation_frontend",
    "occ_appraisal",
    "polarity_operator",
    "sem_event_segmenter",
    "space_reader",                   # pri 137 -- diff written, awaiting landing
    "structured_matcher",             # 354 lines, 2 top-level names -- short-name rules mis-clear it
    "temporal_order_register",        # organ resolved through the hdlab.temporal_model consolidation shim
    "temporal_ordering",              # ditto
    "temporal_ordering_multiframe",   # ditto
}

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("  -- " + detail if detail else ""))
    if not cond:
        FAILS.append(name)


def _read(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def _names(src):
    return set(re.findall(r"^(?:def|class)\s+(\w+)", src, re.M))


def _resolve_shim(stem, src):
    """If hdlab/<stem>.py is a re-export shim for another hdlab module, return that module's stem.

    `hdlab/temporal_order_register.py` is 34 lines that re-export `hdlab/temporal_model.py` (the 2026-09-11
    consolidation).  Comparing the experiments copy against the SHIM finds no shared names and would report
    UNRELATED -- hiding a 342-line copy of the real organ.  One level is enough for every pair on disk.
    """
    if len(_names(src)) > 2:
        return stem                                     # it has its own implementation; not a shim
    m = re.search(r"^from hdlab\.(\w+) import \(", src, re.M) or \
        re.search(r"^from hdlab\.(\w+) import ", src, re.M)
    if m and m.group(1) != stem and os.path.exists(os.path.join(REPO, "hdlab", m.group(1) + ".py")):
        return m.group(1)
    return stem


def classify(stem):
    organ_p = os.path.join(REPO, "hdlab", stem + ".py")
    copy_p = os.path.join(REPO, "experiments", "_" + stem + ".py")
    organ_src = _read(organ_p)
    copy_src = _read(copy_p)
    resolved = _resolve_shim(stem, organ_src)
    if resolved != stem:
        organ_src = _read(os.path.join(REPO, "hdlab", resolved + ".py"))

    if "sys.modules[__name__]" in copy_src:
        return "ALIAS", resolved, 0
    if re.search(r"from hdlab[. ]", copy_src) and len(copy_src.splitlines()) <= 60:
        return "THIN SHIM", resolved, 0

    a = [l.rstrip() for l in organ_src.splitlines()]
    z = [l.rstrip() for l in copy_src.splitlines()]
    shared = _names(organ_src) & _names(copy_src)
    if not shared:
        return "UNRELATED", resolved, 0
    import difflib
    sm = difflib.SequenceMatcher(None, z, a, autojunk=False)
    d = sum((i2 - i1) + (j2 - j1) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != "equal")
    return ("EXACT DUPLICATE" if d == 0 else "DRIFTED COPY"), resolved, d


def main():
    stems = []
    for f in sorted(os.listdir(os.path.join(REPO, "hdlab"))):
        if f.endswith(".py") and os.path.exists(os.path.join(REPO, "experiments", "_" + f)):
            stems.append(f[:-3])

    rows = []
    for s in stems:
        state, resolved, d = classify(s)
        rows.append((s, state, resolved, d))

    print("ORGAN / COPY CENSUS  (%d pairs on disk)\n" % len(rows))
    print("  %-30s %-16s %-28s %s" % ("pair", "state", "organ compared", "diff lines"))
    for s, state, resolved, d in rows:
        mark = "  " if state in ("ALIAS", "THIN SHIM") else ("!!" if state == "DRIFTED COPY" else " ?")
        print("%s%-30s %-16s %-28s %s" % (mark, s, state, ("hdlab." + resolved), d or ""))
    print()

    by_state = {}
    for s, state, _r, _d in rows:
        by_state.setdefault(state, []).append(s)

    # -- W1 census complete --------------------------------------------------------------------------
    known = {"ALIAS", "THIN SHIM", "EXACT DUPLICATE", "DRIFTED COPY", "UNRELATED"}
    check("W1 CENSUS COMPLETE: every hdlab/experiments pair is classified",
          set(by_state) <= known and bool(rows),
          "%d pairs; %s" % (len(rows), {k: len(v) for k, v in sorted(by_state.items())}))

    # -- W2 no NEW drift -----------------------------------------------------------------------------
    drifted = set(by_state.get("DRIFTED COPY", []))
    new = sorted(drifted - KNOWN_DRIFTED - COLLAPSED)
    check("W2 NO NEW DRIFT: no promotion has left a second copy behind since the 2026-09-16 baseline",
          not new,
          ("NEW DRIFTED PAIRS: %s -- a module was promoted into hdlab/ and its experiments copy was left "
           "for the cells to import. Collapse it with a sys.modules alias (pri 137/139 pattern)." % new)
          if new else "%d known drifted pairs, 0 new" % len(drifted))

    # -- W3 no regression on a collapsed pair --------------------------------------------------------
    regressed = sorted(s for s in COLLAPSED if dict((r[0], r[1]) for r in rows).get(s) not in ("ALIAS", "THIN SHIM"))
    check("W3 NO REGRESSION: every pair recorded as COLLAPSED is still one object on disk",
          not regressed, "regressed = %s" % (regressed or "none"))

    # -- W4 the collapsed pairs are really one OBJECT (identity, not source-reading) -------------------
    bad = []
    for s in sorted(COLLAPSED):
        try:
            import importlib
            organ = importlib.import_module("hdlab." + s)
            copy = importlib.import_module("experiments._" + s)
            if copy is not organ:
                bad.append((s, "imports to a DIFFERENT object"))
        except Exception as e:
            bad.append((s, "%s: %s" % (type(e).__name__, str(e)[:70])))
    check("W4 COLLAPSED PAIRS ARE ONE OBJECT BY IDENTITY (`is`), not by looking like an alias",
          not bad, "%d checked; problems = %s" % (len(COLLAPSED), bad or "none"))

    dup = by_state.get("EXACT DUPLICATE", [])
    if dup:
        print("\n  NOTE: %d EXACT DUPLICATE pair(s) -- identical today, two objects, one landing away from"
              " drifting: %s" % (len(dup), dup))
    if drifted:
        print("\n  LOCATED INVENTORY (%d drifted pairs; every one is a measurement that may describe a module"
              " the product does not run):\n    %s" % (len(drifted), ", ".join(sorted(drifted))))

    print("\n" + ("ALL 4 CHECKS PASS" if not FAILS else "WITNESS FAILED: " + "; ".join(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
