# exp_dev hand-off -- research: closing the SR-compose gap to the additive map

Filed-by: research sub-agent
Date: 2026-07-14
Trigger: notes/research_sr_compose_close_gap_to_additive_map_2026-07-14.md
Urgency: MEDIUM-HIGH -- Anchor 1 is a near-zero-build-cost cell (both ingredients already VET-confirmed FULL,
on disk) that could push the inductive-entity-generalization headline number past its current best (0.1282), or
cleanly rule out the combination and redirect effort -- either outcome is decision-relevant and cheap to obtain.

---

## Pause state

Anchors below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (score-combination formulas, sweep values, script structure) are to be authored by
exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: sr_additive_score_fusion_cskg_v1 (cheapest, highest leverage, run FIRST)

Anchor pointer: research note's "Cheap decisive test" section + HEADLINE points 5-6. Combine the ALREADY-LANDED
`exp_graph_spectral_compose_sr_ppmi_nystrom_v1` SR-compose score (MRR 0.0731-0.0738, `data/exp_graph_spectral_
compose_sr_ppmi_nystrom_v1/metrics.json`) with the ALREADY-LANDED `exp_anchor_compose_inductive_entity_cskg_v1`
additive/TransE score (MRR 0.1282, `data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json`) at SCORE level
(a non-learned combination rule over the two methods' already-computed per-query score vectors -- e.g. normalized
weighted-sum sweep, or reciprocal-rank fusion), NOT at embedding level. Both cells already use CSKG-12core,
`support_frac=0.50`, seeds `[7,13,17]` -- config-comparable, but exact per-entity query-id alignment across the two
independently-built splits has NOT been verified and is the one real prerequisite to check first (near-zero cost).
Substrate-product reading: two independent lit-scans converged on structural+relational fusion beating either
alone in the closest published analogs (GraIL, InGram), concentrated exactly where the additive map's own
degree-stratified data shows it is weakest (cold/d1 buckets, per `research_substrate_realizable_frontier_levers_
inductive_map_builder_2026-07-13.md`). A separate brain-grounded citation (positional-encoding literature,
arXiv:2505.13027) explains why score-level fusion is the SAFE way to combine them (avoiding a documented
additive-embedding-space coupling failure mode) rather than merging the two vector spaces directly.
Tier hint: local or remote_cpu_queue -- this is a pure post-hoc scoring-and-combination pass over two already-computed
score matrices, no new training, no new codebook fit, no GPU needed. Should be one of the cheapest cells in the
current queue.
Why-now: both ingredients are already VET-confirmed FULL and sitting on disk; this is a "combine two proven wins"
question, not a new mechanism bet -- exactly the kind of near-zero-risk, high-information dispatch that should not
wait behind larger builds.

Pre-reg bands:
  HARD-PASS: fused MRR >= 0.1282 + 0.02 absolute (genuinely exceeds the additive map alone, not merely ties it),
  with scramble-fusion controls (each real method fused with its own already-computed scramble counterpart) staying
  at or below the plain-additive-alone baseline (confirms the lift is relational on both sides, not a combination
  artifact).
  MIDDLE-BAND: fused MRR beats additive-alone by <0.02 but >0 -- degree-stratify (reuse `anchor_mrr_by_support_
  degree` machinery already built for the additive cell) to check whether SR specifically rescues the buckets
  where additive is weakest (cold/d1); if so, report as real-but-small and concentrated, not a uniform win.
  HARD-FAIL: best fused MRR <= 0.1282 (fusion adds nothing) AND SR-compose does not outperform additive-compose in
  ANY degree-stratified bucket -- informative negative: the two methods' errors are too correlated to gain from
  fusion; redirects effort fully to Anchor 2 (multi-gamma SR) or to refining the additive map alone.

### Anchor 2: sr_multi_gamma_compose_cskg_v1 (cheap, bundle alongside Anchor 1 if compute allows)

Anchor pointer: research note's HEADLINE points 3-4, ranked-lever table rank 2. Re-run the existing SR-compose
harness (verbatim, same split/seeds) at a small grid of discount factors (e.g. 3-4 values spanning the already-used
`SR_GAMMA=0.5`) instead of the single value currently used, concatenating or otherwise combining the resulting
per-gamma SR-compose codes before scoring.
Substrate-product reading: direct, named brain literature (Momennejad multi-scale-SR) states a single discount
factor is provably lossy for order/distance information, and gives a concrete, well-motivated degree of freedom
that has never been varied in this cell family. Honest counter-signal: Graph Diffusion Convolution's own ablation
found no inductive improvement from richer/learned multi-scale diffusion coefficients on a comparable (but not
identical) mechanism and task -- pre-register a MODEST bar, not an optimistic one.
Tier hint: remote_cpu_queue, same compute class as the already-landed SR cell (CPU-tractable, no GPU needed).
Why-now: cheap enough to bundle in the same dispatch as Anchor 1 (shares harness); resolves an honest tension
flagged in the research note (brain lit favorable, closest field precedent null) via cheap dispatch rather than
armchair judgment, per the standing "don't dismiss adjacent methods" discipline.

Pre-reg bands:
  HARD-PASS: multi-gamma SR-compose MRR >= single-gamma SR-compose (0.0731) + 0.015 absolute, with scramble control
  unchanged.
  HARD-FAIL: multi-gamma MRR within noise of single-gamma (< 0.005 absolute change either direction) -- would
  corroborate GDC's null-inductive-transfer caution for this substrate specifically.

---

## Context pointers (file paths, not summaries)

- notes/research_sr_compose_close_gap_to_additive_map_2026-07-14.md (this hand-off's trigger; full lever ranking,
  citations, cross-thread synthesis)
- data/exp_graph_spectral_compose_sr_ppmi_nystrom_v1/metrics.json (landed SR-compose result, full gate/credit spectrum)
- data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json (landed additive/TransE ceiling, degree-stratified
  data lives in the sibling `exp_anchor_compose_scaling_ladder_cskg_v3/metrics.json`)
- notes/research_drill_graph_structure_inductive_transfer_envelope_2026-07-14.md (designed the now-landed SR cell)
- notes/research_substrate_realizable_frontier_levers_inductive_map_builder_2026-07-13.md (cold/d1 degree-stratified
  floor table motivating why fusion should target the additive map's known weak spots)
- notes/project_relational_capability_is_the_core_requirement_make_it_real_USER_2026-07-10.md (program spine both
  anchors feed)

---

## Contract section

exp_dev owns: pre-registration file, smoke gate, exact score-combination/gamma-grid implementation, dispatch via
queue_add.sh, post-ship REMOTE VERIFY, self-test per formula-selftests. This hand-off does not prescribe
implementation details beyond the pre-reg bands above (per [[feedback-no-experiment-design-in-prompts]]).

## Autonomy declaration

Research does not decide dispatch tier, exact sweep grids, or code structure -- those are exp_dev's authored
decisions from this hand-off + the cited on-disk cells. Research's role ends at supplying the mechanism-level
rationale, the falsifiable pre-reg bands, and pointers to the exact on-disk artifacts needed to build without
re-deriving context from scratch.
