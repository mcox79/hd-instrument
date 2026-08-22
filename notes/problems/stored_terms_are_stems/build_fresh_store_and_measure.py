#!/usr/bin/env python3
"""End-to-end: build a FRESH store on HEAD code and measure its true-stem rate with the
SAME round-trip detector used on the stale store. Two purposes:
  - confirm no OTHER chopping step exists outside normalize_lemma (the brief's "somewhere
    grep does not reach" worry) -- this exercises the real tokenize->POS->content->lemma->store path;
  - test hypothesis (d): if a fresh build still has stems, they came from the CORPUS, not our code.
"""
import sys
import time
from collections import defaultdict

sys.path.insert(0, r"D:/AI/hd-instrument")
sys.path.insert(0, r"D:/AI/hd-instrument/notes/problems/stored_terms_are_stems")

from probe_stem_diagnosis import stem_suffix  # noqa: E402  # the SAME round-trip detector
from hdlab.substrate import Substrate  # noqa: E402

t0 = time.time()
s = Substrate(seed=7)
s.read(corpus="simplewiki", n_sentences=800, batch=50, max_patches=1, consolidate_every=200)
facts = s.state.store.live_facts()

by_src = defaultdict(set)
all_subs = set()
for f in facts:
    sub = getattr(f, "subject", None)
    if not isinstance(sub, str) or not sub:
        continue
    all_subs.add(sub)
    by_src[getattr(f, "source", "?")].add(sub)


def rate(subs):
    stems = [(t, stem_suffix(t)) for t in subs]
    stems = [(t, x) for t, x in stems if x]
    return len(stems), len(subs), stems


ns, nt, ex = rate(all_subs)
print(f"FRESH store (HEAD code): {len(facts)} facts, {nt} distinct subjects")
print(f"  TRUE-STEM RATE: {ns}/{nt} = {100*ns/max(1,nt):.2f}%   (stale v2_qualityfix was ~8.4%)")
print("  per source:")
for src in sorted(by_src, key=lambda k: -len(by_src[k])):
    a, b, _ = rate(by_src[src])
    if b >= 10:
        print(f"    {src:34s} {a:3d}/{b:4d} = {100*a/b:5.2f}%")
if ex:
    print("  stem tokens found (would be hypothesis (d) corpus-origin):")
    for t, suf in sorted(ex)[:40]:
        print(f"    {t:24s} +{suf} -> {t+suf}")
else:
    print("  ZERO stem tokens in the fresh store.")
print(f"elapsed {time.time()-t0:.0f}s")
