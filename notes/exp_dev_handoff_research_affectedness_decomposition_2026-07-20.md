# exp_dev hand-off — research: affectedness decomposition (type-level lookup vs per-instance residual)

**Filed-by:** research (3x parallel Sonnet lit-scan + director synthesis), 2026-07-20.
**Trigger:** `notes/research_affectedness_decomposition_typelevel_lookup_vs_perinstance_2026-07-20.md` —
read that note in full before designing any cell. It decomposes the who-is-affected / patient-selection
problem (closed for TEXT-DERIVATION at atom 29375) into (a) a TYPE-LEVEL selectional-preference
component that is lookup-able from structured resources and storable as an edge (reusing the
single-edge lookup-store-recall-generalize machinery already validated at atom 29390, and the
location/artifact derived-typing precedent at atom 29391), and (b) a genuinely per-instance residual
that stays event-combinatorial and is NOT addressed by this anchor.
**Pause state:** respect `data/orchestrator_paused.flag` if present — do not ship without checking.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off gives anchor pointers and why-now
context, NOT a prescribed cell implementation. exp_dev owns cell design, pre-reg, smoke gate, and
dispatch.

## Why this is actionable now

29375 closed the TEXT-DERIVATION route for per-instance affectedness (6 self-supervised signals
failed). This drill found a DIFFERENT route — structured lookup of a decomposed, type-level piece
of the same problem — that has NOT been tested, reuses existing validated machinery (29390's
single-edge lookup-store-recall-generalize pipeline), and has three concrete, license-navigable,
static, glass-box-legal source candidates (VerbNet selectional restrictions, PropBank Arg1,
ATOMIC-2020 xEffect/oEffect) already inventoried in
`notes/research_plausibility_web_engineering_resources_adoptable_foundation_2026-07-20.md`. This
does NOT reopen 29375 — it is scoped strictly to whether a type-level edge recovers a bounded slice
of who-is-affected on the SAME eval items 29375 already has gold labels for.

## Anchor candidate (single, rank 1 by construction)

1. **Type-level affectedness lookup edge (VerbNet selectional-restriction on Patient/Product,
   OR PropBank Arg1 roleset-level typing, OR ATOMIC-2020 xEffect/oEffect outcome-type) as a
   candidate-filter/re-ranker on top of the closed 29375 text-derived baseline.**
   Build: for each verb (or VerbNet class) in the 29375/LCCP eval set, look up the selectional
   restriction on its Patient/Theme/Product role (VerbNet SELRESTRS, e.g. `+animate`/`+concrete`/
   `+liquid`) and store it as a static edge, structurally identical to the 29391 location/artifact
   type-edge (verb-class -> affected-role-TYPE). At eval time: does this edge (i) rule out
   candidates whose semantic type mismatches the restriction, and (ii) among remaining candidates,
   does argmax-by-type-fit beat the closed baseline's argmax-pick-gold rate (0.474) — specifically
   on the SUBSET of items where the two candidates have DIFFERENT semantic types under the verb's
   restriction (the type-discriminable subset)?
   Tier hint: LOW-MEDIUM effort — VerbNet/PropBank/SemLink are already static, downloadable,
   license-navigable resources (per the companion engineering-resources note); building the
   type-edge lookup table is a few hours of offline resource-parsing, reusing the SAME single-edge
   store/query pipeline validated at 29390. The eval itself reuses the EXISTING 29375/LCCP gold-
   patient item set and scoring harness — no new annotation.
   Why now: it is the cheapest, most direct test of whether the TYPE/INSTANCE decomposition this
   drill proposes actually carves the 29375 failure distribution usefully, before investing any
   further effort in either (a) a fuller lookup-KB build-out, or (b) escalating toward
   grounding/perception for the per-instance residual that this test will NOT touch.

## Design gate (verify at smoke before full run)

1. Real baseline = the EXISTING closed text-derived signal from 29375, run on the IDENTICAL item
   set/split — not a strawman.
2. Discriminator can-fail: the type-edge must be able to score WORSE than the closed baseline (on
   items where both candidates share the same coarse type, e.g. two animate NPs under a "hurt"-class
   verb, the type-edge should show ZERO discriminating power, not get a free pass via a hidden
   correlate).
3. Difficulty actually on: restrict primary reporting to the items 29375 actually failed on
   (ambiguous, both-syntactically-plausible-object cases) — do not cherry-pick the easy
   semantically-unambiguous subset for the headline number.
4. One variable differs: only the ADDITION of the type-lookup edge as a filter/re-ranker; same
   eval items, same gold labels, same scoring as 29375.

## Arms

(a) closed text-derived baseline alone [=29375, the real baseline, argmax-pick-gold 0.474];
(b) type-lookup edge alone (selectional-restriction filter + argmax-by-type-fit);
(c) type-lookup edge as a prior/filter COMBINED with the closed baseline (edge narrows candidates,
    baseline breaks remaining ties) — likely the more realistic production shape;
(d) random-type-mapping control (scrambled verb->type map — must NOT beat chance; sanity check
    against eval-harness leakage).

## HARD-PASS / HARD-FAIL bands (verbatim from the research note — do not loosen)

- **HARD-PASS:** on the type-discriminable subset (candidates of different semantic types under
  the verb's restriction), (b) or (c) beats the closed baseline's 0.474 argmax-pick-gold rate by
  >= 0.05 absolute accuracy, WITHOUT regressing accuracy on the type-indiscriminable subset below
  the closed baseline's own performance there.
- **HARD-FAIL:** no meaningful lift (< 0.02 accuracy difference) on the type-discriminable subset,
  OR the type-discriminable subset is a small minority (< 15-20%) of the 29375 failure set such
  that even a clean win there does not move the aggregate number. Either result means the
  type/instance split, while real in principle (see research note's brain + resource evidence),
  does not usefully carve the ACTUAL 29375 item distribution — a genuine-but-small or non-actionable
  win, not a strategic reopening of the affectedness wall.
- **Must-fail control:** arm (d) must not beat chance on the type-discriminable subset; if it does,
  the eval harness has a leakage/construction problem independent of this hypothesis.

## Context pointers (file paths, not summaries — read these, don't re-derive)

- `notes/research_affectedness_decomposition_typelevel_lookup_vs_perinstance_2026-07-20.md` (this
  drill's full note — brain type-vs-instance evidence, resource-by-resource lookup-ability
  assessment, residual-fraction estimate, full design-gate spec, deflated P)
- `notes/research_plausibility_web_engineering_resources_adoptable_foundation_2026-07-20.md`
  (VerbNet/PropBank/SemLink/ATOMIC-2020 resource inventory, license flags, COMET glass-box ruling)
- `notes/research_brain_patienthood_affectedness_grounding_2026-07-20.md` (original brain
  required-component list + the 6-signal text-derivation closure that this anchor does NOT reopen)
- `notes/research_functional_vs_topical_encoding_dependency_context_2026-07-20.md` (the sibling
  location/artifact type-edge precedent at atom 29391 — same storable-edge shape, same pipeline
  template to reuse for affectedness)
- Whatever module currently holds the single-edge lookup-store-recall-generalize machinery
  (atom 29390) — reuse it; do not re-derive from scratch.
- Whatever module holds the 29375/LCCP gold-patient eval harness and item set — reuse unchanged.

## Contract

- exp_dev authors + smokes locally, returns the exact `queue_add.sh` dispatch command if queue
  compute is needed at all (this may run inline/local given its low cost — offline resource lookup
  + eval over an existing item set, no training loop); orchestrator ships + REMOTE VERIFIES
  post-ship if queued, per locked ship policy.
- Pre-register per envelope-fail-bands using the HARD-PASS/HARD-FAIL thresholds given verbatim
  above — do not loosen them.
- Deflated confidence for this anchor per the research note: P(lookup route recovers a meaningful,
  actionable slice of who-is-affected) ~0.30 (deflated further below the standing 0.50
  novel-synthesis cap given (i) PropBank Arg1 is largely verb-specific not class-general per this
  cycle's lit-scan, weakening one of the three candidate sources; (ii) selectional-preference-only
  disambiguation has a documented real-world ceiling — Resnik 1997's own broad-coverage caveat,
  Heinzerling et al. 2017's marginal 65.60->65.90 F1 gain on a directly-analogous candidate-
  disambiguation task; (iii) no paper directly quantifies the type-discriminable fraction of a
  29375-shaped item set, so the HARD-FAIL band's minority-fraction risk is real, not hypothetical).
- Carry forward the design risk flagged in the research note: VerbNet's selectional restrictions
  are coarse (a handful of binary features) and known to be incompletely/inconsistently populated
  across classes (secondary-source claim, not independently quantified) — a HARD-FAIL could reflect
  restriction-coverage sparsity rather than the type/instance decomposition being wrong; if (b)/(c)
  underperform, check restriction coverage on the actual 29375 verb set before concluding the
  mechanism fails (same "diagnose sparsity before declaring mechanism-refuted" discipline used for
  the sibling dependency-PPMI anchor).

## Autonomy declaration

exp_dev owns: which of the three lookup sources (VerbNet SELRESTRS, PropBank Arg1, ATOMIC-2020
xEffect/oEffect) to build first or whether to combine them via SemLink's existing VerbNet<->PropBank
mapping; the exact type-taxonomy granularity (binary +animate/+concrete vs a richer type set); how
to compute "type-discriminable" (same coarse-type-bucket check) at eval time; smoke design; and
whether the HARD-PASS/HARD-FAIL result on this anchor warrants a fuller build-out of the lookup-KB
layer for other slot-typing needs (this is a separable follow-on decision, not gated by this
anchor's outcome).
