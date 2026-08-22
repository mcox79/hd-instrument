#!/usr/bin/env python3
"""SOLVED.md reverify script for stored_terms_are_stems.

Runs, in order:
  (0) DETECTOR CONTROLS  -- positive (real chops flagged) + negative (real words, incl. function
      words, left alone). Aborts if the detector cannot fail safely.
  (1) BEFORE -- true-stem rate on the stale data/foundation/reading_grounding_v2_qualityfix store,
      per source, with the validated round-trip detector.
  (2) AFTER  -- build a FRESH store on HEAD code (simplewiki), same detector, per source.

The comparison that matters is READING-PRODUCED subjects: stale reading:* vs fresh reading:simplewiki.
"""
import json
import sys
import time
from collections import defaultdict

sys.path.insert(0, r"D:/AI/hd-instrument")
sys.path.insert(0, r"D:/AI/hd-instrument/notes/problems/stored_terms_are_stems")

from probe_stem_diagnosis import stem_suffix, validate_detector  # noqa: E402

STALE = r"D:/AI/hd-instrument/data/foundation/reading_grounding_v2_qualityfix/store/store_facts.json"


def rate(subs):
    stems = [(t, stem_suffix(t)) for t in subs]
    stems = [(t, x) for t, x in stems if x]
    return len(stems), len(subs), stems


def measure(facts, label):
    by_src = defaultdict(set)
    allsub = set()
    for f in facts:
        sub = f["subject"] if isinstance(f, dict) else getattr(f, "subject", None)
        if not isinstance(sub, str) or not sub:
            continue
        src = f.get("source", "?") if isinstance(f, dict) else getattr(f, "source", "?")
        by_src[src].add(sub)
        allsub.add(sub)
    ns, nt, ex = rate(allsub)
    print(f"\n=== {label}: {len(facts)} facts, {nt} distinct subjects ===")
    print(f"  ALL subjects true-stem rate: {ns}/{nt} = {100*ns/max(1,nt):.2f}%")
    for src in sorted(by_src, key=lambda k: -len(by_src[k])):
        a, b, _ = rate(by_src[src])
        if b >= 10:
            print(f"    {src:34s} {a:3d}/{b:4d} = {100*a/b:6.2f}%")
    if ex:
        print("  stem tokens:", ", ".join(f"{t}(+{s})" for t, s in sorted(ex)[:30]))
    return ns, nt


def main():
    t0 = time.time()
    if not validate_detector():
        print("DETECTOR FAILED ITS CONTROLS -- no measurement below can be trusted.")
        return 1

    stale = json.load(open(STALE, encoding="utf-8"))
    measure(stale, "BEFORE (stale v2_qualityfix, built pre-2026-08-13 fix)")

    from hdlab.substrate import Substrate
    s = Substrate(seed=7)
    s.read(corpus="simplewiki", n_sentences=800, batch=50, max_patches=1, consolidate_every=200)
    measure(s.state.store.live_facts(), "AFTER (fresh store, HEAD code)")

    print(f"\nelapsed {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
