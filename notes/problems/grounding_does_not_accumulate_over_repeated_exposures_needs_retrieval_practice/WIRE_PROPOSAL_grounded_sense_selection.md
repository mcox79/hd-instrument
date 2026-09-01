# WIRE PROPOSAL (Q111 -- strategy lands; solver may NOT write hdlab/): grounded sense-selection cascade

## The diagnosis, localized to one line

`hdlab/reading_grounding_loop.py::canonicalize` (lines 896-911) is the failing read-out. It assigns a
newly-grounded word to the **single nearest anchor by distributional sign-bundle cosine**:

```python
    for anchor in space.anchors():
        ...
        c = _cos(new_bundle, ab)
        if c > best_cos:
            best_anchor, best_cos = anchor, c          # <-- DIST argmax; this is the wall
    if best_anchor is not None and best_cos >= thresh:
        return best_anchor, best_cos
```

That argmax is the `DIST` read-out measured at ~0.20-0.28 rank-1-correct on CONSOLIDATION_FAIL. The
correct sense is in the distributional top-K ~85% of the time but distributional cosine picks the
SYNTAGMATIC (topical) associate, not the PARADIGMATIC (same-meaning) anchor.

## The fix (brain-foundational, measured): a two-stage LASS cascade

Keep the distributional cosine as the STAGE-1 SHORTLIST (top-K eligible anchors), then SELECT stage-2
by GROUNDED-hub similarity (ATL hub-and-spoke; the richest available experiential spoke, morphology-
extended). Measured lift (2-seed smoke, CI-separated; full run queued): DIST ~0.24 -> ~0.45, roughly
DOUBLING correct sense selection. Re-fusing the distributional cue HURTS (it is confidently-wrong for
sense), so the cascade is grounded-DOMINANT, not equal fusion.

**Precision is not bought by relaxing the bar:** the `thresh` gate stays on the STAGE-1 DISTRIBUTIONAL
cosine (a candidate must still clear 0.45 to ground at all), so this does not add wrong meanings at a
lower bar (the brief's explicit prohibition). It only changes WHICH of the already-qualifying anchors
is chosen.

## Proposed change -- an ADDITIVE sibling (default path byte-for-byte unchanged)

Add a sibling function; do NOT modify `canonicalize` (keep its NO-MATCH self-return semantics intact).
A `grounded_lookup(lemma) -> Optional[np.ndarray]` returns the L2-normalized grounded vector for a
lemma or None (an OFFLINE foundation asset: Lancaster sensorimotor + Warriner affect + predicted-
Binder-65 experiential + morphological backoff; no LLM, no gold, built once).

```python
def canonicalize_grounded(new_lemma, new_raw_sum, space,
                          grounded_lookup,                      # lemma -> L2-normed grounded vec or None
                          thresh: float = SENSE_MATCH_THRESH,
                          eligible=None, topk: int = 20):
    """Two-stage sense assignment (LASS): distributional cosine SHORTLIST -> GROUNDED-hub SELECT.
    Byte-for-byte falls back to canonicalize() when the target or its shortlist lacks grounded
    coverage. The thresh gate stays on the DISTRIBUTIONAL cosine (does NOT relax the grounding bar).
    Brain-foundational: ATL hub-and-spoke sense selection (Lambon Ralph/Patterson/Rogers); the
    distributional spoke is the shortlist only, its confidence is not a valid SENSE cue."""
    new_bundle = np.sign(new_raw_sum)
    # STAGE 1: distributional shortlist -- top-K eligible anchors by sign-bundle cosine.
    scored = []
    for anchor in space.anchors():
        if anchor == new_lemma:
            continue
        if eligible is not None and not eligible(anchor):
            continue
        ab = space.bundle(anchor)
        if ab is None:
            continue
        scored.append((_cos(new_bundle, ab), anchor))
    if not scored:
        return new_lemma, 0.0
    scored.sort(reverse=True)                     # deterministic: cosine desc, then anchor name
    best_cos, best_anchor = scored[0]             # distributional nearest (the fallback pick)
    if best_cos < thresh:                         # STAGE-1 GATE unchanged -> no bar relaxation
        return new_lemma, best_cos
    shortlist = scored[:topk]
    # STAGE 2: grounded re-rank of the shortlist. Abstain to DIST if target/candidates uncovered.
    gq = grounded_lookup(new_lemma)
    if gq is None:
        return best_anchor, best_cos
    cand = [(a, grounded_lookup(a)) for (_, a) in shortlist]
    cand = [(a, g) for (a, g) in cand if g is not None]
    if len(cand) < 2:
        return best_anchor, best_cos
    gbest_anchor = max(cand, key=lambda ag: float(np.dot(gq, ag[1])))[0]
    gcos = dict((a, c) for (c, a) in shortlist)[gbest_anchor]   # report the DIST cosine of the pick
    return gbest_anchor, gcos
```

Plus a builder for `grounded_lookup` (offline; reuses `distributional_meaning_channel.build_grounded_hub`
+ the predicted-Binder-65 table + the morphology backoff already prototyped in
`experiments/exp_retrieval_practice_consolidation_v1.py::_build_binder65_hub_morph` /
`_morph_stem_candidates`). Promote those helpers into `hdlab/` alongside the sibling.

## Where it plugs in

The consolidation/grounding path that calls `canonicalize` (see `checkpoint` and the grounding gate in
`hdlab/grounding_acquisition_loop.py`). Add a DEFAULT-OFF flag (e.g. `grounded_select=False`) threaded
to the caller; when True, call `canonicalize_grounded(..., grounded_lookup)`. Off by default => zero
behavior change until the end-to-end measurement clears the bar.

## The end-to-end measurement that certifies the wire (the real solve criterion)

Before landing default-ON: measure CONSOLIDATION_FAIL grounding PRECISION (WordNet-correct rate)
end-to-end with the cascade vs (a) the distributional `canonicalize` and (b) an info-free twin
(shuffled grounded vectors). PASS = precision rises CI-separated above the ~0.30 distributional
ceiling, 2-seed, info-free twin loses, recall not bought by bar-relaxation (grounded-count not lower).
Full runs REMOTE. This is the wire's landing gate.

## Brain-foundational labelling
- STAGE-1 distributional shortlist -> STAGE-2 grounded select == LASS two-stage (Barsalou 2008): PINNED.
- Grounded-hub SELECT == ATL hub-and-spoke amodal disambiguation (Patterson 2007; Lambon Ralph 2017): PINNED.
- Grounded-dominant (not equal fusion) is EVIDENCE-DRIVEN: the distributional cue is confidently-wrong
  for sense (measured), so reliability-weighting by peakiness over-trusts it -- a refinement of the
  cue-combination literature, backed by the ablation. OUR-INVENTION-labelled: the predicted-Binder
  imputation + morphology backoff (coverage assets, adopt on measured lift).
