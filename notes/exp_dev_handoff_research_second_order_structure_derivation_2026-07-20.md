# exp_dev hand-off — research: second-order layer, structure-derivation anchor

**Filed-by:** research (4x parallel Sonnet lit-scan + director synthesis), 2026-07-20.
**Trigger:** `notes/scour_second_order_build_and_prior_art_3x_2026-07-20.md` — the 3x build-drill +
prior-art scour across the four second-order elements (neuromodulatory multi-axis gating,
hierarchical multi-timescale predictive processing, consolidation/schema-extraction replay,
learned structure-derivation). Read that note in full before designing any cell; it contains the
per-element build angles, prior-art citations, glass-box-adoptability verdicts, and the
HARD-PASS/HARD-FAIL bands below.
**Pause state:** respect `data/orchestrator_paused.flag` if present — do not ship without checking.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off gives anchor pointers and why-now
context, NOT a prescribed cell implementation. exp_dev owns cell design, pre-reg, smoke gate, and
dispatch.

## Why this is the only actionable anchor from this scour right now

Of the four elements scoured, three (neuromodulatory gating, hierarchical timescale stacking,
consolidation/schema-extraction) are all STRICT second-order — each computes its signal from the
base contrastive-predictive-coding loop's own prediction-error/coherence stream, and that base
loop is not built yet (scoped separately). There is nothing to wire them to. The fourth,
**learned structure-derivation**, is the one exception the scour surfaced: it operates on raw
transition/co-occurrence statistics of the data itself and does NOT need the base loop to exist
first. It is therefore the only one of the four that produces a standalone, falsifiable, cheap
result today.

## Anchor candidate (single, rank 1 by construction — the only base-loop-independent one)

1. **Successor-representation / Laplacian-eigenvector structural-code derivation vs. the current
   hand-stipulated structural code.** Build the transition/co-occurrence matrix over whatever
   discrete units the current hand-stipulated structural code indexes (positions/roles/slots);
   TD-learn a successor-representation matrix M = (I - gamma*T)^-1 per Dayan (1993) / Stachenfeld,
   Botvinick & Gershman (2017), OR run Oja's-rule Hebbian PCA with a non-negativity constraint per
   Dordek, Soudry, Meir & Derdikman (2016); eigendecompose; quantize the top-k eigenvectors into
   the substrate's hyperdimensional space via a fixed random projection. Compare against the
   existing hand-stipulated code on (a) pairwise role-vector separation (mean |cosine|) and (b)
   downstream bind/unbind retrieval accuracy on whatever synthetic task already exercises the
   hand-stipulated code.
   Tier hint: LOW-MEDIUM effort — pure linear algebra (SVD/eigendecomposition or Oja's-rule
   incremental PCA) + one retrieval smoke against an EXISTING synthetic task; no new training loop,
   no base loop dependency. ~1 day theory + a few hours CPU per the scour note's cost estimate.
   Why now: it is the only one of the four second-order elements that can run TODAY without
   waiting on the base loop, and it directly tests whether "derive, don't stipulate" (the
   structural-code half of the brain-factorization anchor) is viable before investing further
   design effort in the three base-loop-gated elements.

## Context pointers (file paths, not summaries — read these, don't re-derive)

- `notes/scour_second_order_build_and_prior_art_3x_2026-07-20.md` (this drill's full note — all
  four elements, per-element 3x build angles, prior-art citations, ADOPT/ADAPT calls, deflated P,
  the cheap-decisive-test spec in full, and the per-element summary table)
- Whatever module currently holds the hand-stipulated structural/role code (the fixed-random role
  vectors per Plate/Kanerva convention) — locate via the existing VSA/HDC codebook construction
  code before building; do not re-derive from scratch what already exists on disk.
- Whatever existing synthetic task already exercises bind/unbind retrieval against the
  hand-stipulated code — reuse it as the comparison harness rather than building a new one.

## Contract

- exp_dev authors + smokes locally, returns the exact `queue_add.sh` dispatch command (if it
  needs queue compute at all — this may run inline/local given its low cost); orchestrator ships +
  REMOTE VERIFIES post-ship if queued, per locked ship policy.
- Pre-register per envelope-fail-bands using the HARD-PASS/HARD-FAIL thresholds given verbatim in
  the research note's "Falsifiable predictions / Element 9" section:
  - HARD-PASS: derived code's mean pairwise |cosine| among role vectors statistically
    indistinguishable from (or better than) the hand-stipulated code's, AND downstream retrieval
    accuracy within 5% of (or exceeding) the hand-stipulated baseline.
  - HARD-FAIL: derived code's separation collapses toward the random-codebook null (quantization
    destroys the eigenbasis structure), OR downstream retrieval accuracy drops >=5% vs. baseline.
- Deflated confidence for this anchor per the research note: 0.45 (already under the standing
  0.50 novel-synthesis cap — no further deflation needed, but do not round up).
- Carry forward the design risk flagged in the research note: the VSA field's own prior
  consensus (Plate 1995, Kanerva 2009) is that role vectors should be fixed/random, not derived,
  specifically to preserve generalization — check the derived code for the same overfitting
  failure mode the field warns learned embeddings are prone to, not just the two metrics above.

## Autonomy declaration

exp_dev owns: whether to use the TD-learned-SR route or the Oja's-rule-PCA route (or both, as a
comparison) for deriving M/the eigenbasis; the exact quantization/random-projection scheme into
the hyperdimensional space; smoke design; and whether the two comparison metrics (separation,
retrieval accuracy) warrant a fuller build at all — if either metric HARD-FAILs at smoke scale,
that is itself a valid kill decision on the "derive, don't stipulate" direction for structural
codes, reportable back through the normal verdict path, and does NOT reflect on the three
base-loop-gated elements (which remain queued behind the base loop regardless of this anchor's
outcome).
