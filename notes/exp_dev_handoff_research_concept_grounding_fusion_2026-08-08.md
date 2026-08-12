# exp_dev hand-off — research: concept-grounding fusion prior art (decay-weighted hop + multi-source)

**Filed-by:** research sub-agent, 2026-08-08.
**Trigger:** `notes/research_concept_grounding_fusion_prior_art_2026-08-08.md` — prior-art scan for
densifying/fusing concept groundings on the sparse (~1.25 edges/concept) 100k ConceptNet slice.
Finding: the field's closest true precedent (Cohen et al. 2012, PSI, Random-Indexing bind+bundle
directly on a real sparse growing biomedical KG) confirms the current bind/bundle approach is
correct in kind, but surfaces two specific, cheap, literature-backed upgrades that the currently-
in-flight naive "2-hop densification" test does NOT include: (1) hop expansion should be
DECAY-WEIGHTED (Katz-index / random-walk-with-restart style — Haveliwala 2002, Tong/Faloutsos/Pan
2006, and directly: Klicpera et al. ICLR 2019 PPNP/APPNP + NeurIPS 2019 GDC, which show flat k-hop
expansion is "noisy and arbitrarily defined" vs. principled decay-weighted diffusion), not flat;
(2) multi-source fusion (adding WordNet/FrameNet/Wikidata alongside ConceptNet) should use a
shared base hyperdimensional space with an explicit provenance-role bind and per-source weight
(retrofitting's alpha/beta principle, Faruqui et al. 2015, re-expressed as a bundle coefficient),
NOT trained-then-geometrically-aligned separate embeddings (ConceptNet Numberbatch's hardest step,
which has no bind/bundle analog).

**Pause state:** check `data/orchestrator_paused.flag` before shipping; this hand-off is filed
regardless of pause state per research-role convention — it is not queue authorization by itself.

Per [[feedback-no-experiment-design-in-prompts]]: this file states WHAT to test and WHY
(falsifiable bands, context pointers) — exp_dev owns exact implementation (which decay constant,
exact WordNet relation subset, exact cell structure, seeds).

## Anchor candidates (rank-ordered)

### 1. `exp_concept_grounding_decay_weighted_hop_v1` (primary, do this first — cheapest, most precedented)

**Anchor pointer:** research note section (b) Test 1 — decay-weighted vs flat vs 1-hop featurization
on the existing WordNet-supersense-from-ConceptNet-features held-out harness.

**Substrate-product reading:** if this passes, it directly replaces whatever naive flat-2-hop
densification is currently in flight with a literature-endorsed principled weighting scheme, at
no added implementation cost (same neighbor-collection code, just a scalar decay multiplier on
2-hop contributions before bundling). This is a drop-in fix, not a new subsystem.

**Tier hint:** load-bearing if HARD-PASS — this would directly move the held-out accuracy number
(currently 0.184 vs 0.091 majority) that the whole densification effort is trying to improve, and
it would validate (or falsify) whether hop-WEIGHTING was ever the lever vs. hop-COVERAGE being a
hard ceiling on the 100k slice.

**Why now:** cheapest possible test — reuses the existing eval harness end to end; the only change
is the featurization function. No new infra, no external calls.

**Design (from the research note, exp_dev owns implementation details):**
1. Build three feature variants for the same concept/held-out split: (i) 1-hop-only (current
   baseline, reproduce exactly), (ii) flat 2-hop (equal-weight 2-hop neighbors added — whatever the
   in-flight naive densification test is already doing; reuse that code if it exists), (iii)
   decay-weighted 2-hop (2-hop contribution scaled by a FIXED decay constant chosen once, not
   swept/tuned per-concept — e.g. Katz-style beta in [0.3, 0.5] or RWR-style single-restart-step
   alpha; exp_dev picks one value and states why in the pre-reg, not a grid search for the best
   number).
2. Run all three through the UNCHANGED MDL learner + held-out gate.
3. Report held-out accuracy for all three plus the train/held-out generalization gap for each.

**Pre-registered bands:**
- HARD-PASS: (iii) beats (ii) by >= 2 percentage points held-out accuracy AND beats (i) by >= 15%
  relative (>= ~0.211 vs 0.184 baseline) AND the (iii) generalization gap is not worse than (i)'s.
- HARD-FAIL: (iii) is statistically indistinguishable from (ii) (within noise) — this means
  hop-WEIGHTING was never the lever; the problem is graph COVERAGE (too few edges reachable at any
  hop-distance on the 100k slice), not edge-weighting, and the real fix is acquiring more of the
  full ~34M-edge ConceptNet, not further weighting schemes.
- INVALID: (i) does not reproduce the previously-measured 0.184/0.091 baseline numbers on this
  exact split (harness/construction mismatch — fix before interpreting further).

### 2. `exp_concept_grounding_multisource_fusion_ablation_v1` (run after or alongside #1)

**Anchor pointer:** research note section (b) Test 2 — ConceptNet+WordNet shared-space fusion with
a source-ablation falsification control.

**Substrate-product reading:** if this passes, it's the first evidence that the substrate can fuse
multiple knowledge sources into one concept vector without one source drowning the other AND
without abandoning the no-gradient-training/glass-box invariant — the missing piece the prior-art
scan flagged as a genuine gap (no verified paper does provenance-weighted VSA multi-source fusion).
This is the mechanism that would let the grounding program later add FrameNet/VerbNet/Wikidata/
SimpleWiki without a redesign.

**Tier hint:** exploratory but decisive — the ablation control (not just the fused-vs-baseline
comparison) is what makes this a REAL test rather than a vacuous "more features never hurts" result;
do not skip the ablation arm.

**Design (from the research note, exp_dev owns implementation details):**
1. Encode WordNet hypernym/hyponym/meronym edges (nltk, already available) into the SAME base
   hyperdimensional space as the ConceptNet edges, using an explicit `bind(source_id,
   relation_edge)` provenance role before bundling into the concept vector — this bind is what
   makes the source ablation possible (zero out contributions with that source_id at eval time).
2. Compare three arms on the same held-out split: (i) ConceptNet-only (baseline), (ii)
   ConceptNet+WordNet fused, (iii) same fused pipeline with the WordNet-source term zeroed at eval
   time (the ablation/falsification control — NOT a separately-retrained model, the same fused
   vectors with that one term removed).
3. Report held-out accuracy for all three.

**Pre-registered bands:**
- HARD-PASS: (ii) beats (i) by a non-trivial margin (exp_dev states the exact threshold in the
  pre-reg, informed by (i)'s measurement noise/SE) AND (iii) drops back toward (i)'s level
  (confirming WordNet was contributing real signal, not just extra capacity/noise-tolerance).
- HARD-FAIL: (ii) does not beat (i), OR (iii) shows no drop relative to (ii) when WordNet is
  zeroed out (either outcome means the fusion mechanism itself isn't the active ingredient — most
  likely the same underlying coverage/density ceiling as Test 1's HARD-FAIL path, not a fusion-
  specific problem).
- INVALID: (i) does not reproduce baseline; or the provenance-bind implementation can't cleanly
  zero one source's contribution (construction bug in the bind, not a result).

## Context pointers (files, not summaries)

- `notes/research_concept_grounding_fusion_prior_art_2026-08-08.md` — full research synthesis,
  all 28 verified citations, glass-box ratings, the ranked mechanism table, calibration-deflated
  P estimates for both tests.
- `notes/tonight_plan_three_ways_over_the_grounding_wall_2026-08-08.md` — the adjacent "grounding
  wall decomposes" finding from the same day: word/concept-level grounding is the TRACTABLE half
  of the wall; this hand-off's two tests sit inside that tractable half and should not be conflated
  with the goal<->outcome relational residual described there.
- `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md` (top block) — current strategic state
  including the DesireDB reckoning and the auditability-edge finding; if Test 2 HARD-PASSes, the
  explicit provenance-bind is directly reusable for the auditability story (source-level trace on
  any grounded inference).
- Wherever the current 2-hop densification test / MDL-learner-on-ConceptNet-features harness lives
  in `experiments/` and `hdlab/` — exp_dev locates the exact files from the live session context
  (this hand-off is written from research's external vantage and does not have those live paths).

## Contract section

- exp_dev owns: exact decay constant value (state + justify once, don't grid-search it into the
  result), exact WordNet relation subset used for Test 2, exact cell/file naming, exact seed count,
  whether Test 1 and Test 2 run as one cell or two.
- Research (this hand-off + parent note) fixes: the falsifiable HARD-PASS/HARD-FAIL/INVALID bands,
  the mandatory ablation control in Test 2 (not optional, not exp_dev's to drop), and the
  glass-box/no-gradient-training/no-external-embedding invariant — nothing in either test may
  introduce a trained/opaque component or an external LLM/embedding call.
- Per no-bolt-on-reader / no-borrowed-embeddings invariants: WordNet edges are structural relation
  data (hypernym/hyponym/meronym graph edges), not a pretrained embedding — this is consistent with
  the existing ConceptNet-edges approach and does not introduce a new external-model dependency.

## Autonomy declaration

exp_dev decides cell file naming, exact hyperparameter values (decay constant, WordNet relation
subset), exact seed count, and whether to combine both tests into one cell or run separately.
The falsifiable bands and Test 2's mandatory ablation control are NOT exp_dev's to loosen without
flagging the change explicitly in the pre-reg.
