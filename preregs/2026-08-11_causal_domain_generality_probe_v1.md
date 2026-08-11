# Pre-registration: causal_domain_generality_probe_v1

## Context / motivation (Director task)

The proven three-tier weak->strong + canonicalization pipeline was built and validated on ONE
gap-set: 121 material-composition MadeOf-bridge facts, relation classes
PART_OF/PRODUCES/CONSUMES/MOVES, ~15 processes
(`data/exp_state_of_mind_relevance_gather_reasoning_union_v1/metrics.json` HARD_PASS +
`data/exp_relation_canonicalization_learned_v1/metrics.json`). Open question: is the pipeline
GENERAL, or FIT to that one structure? This cell runs the SAME proven organs end-to-end on a
FRESH relation family (CAUSAL: X causes/enables/prevents Y) and reports honestly whether it
generalizes or overfits. An honest overfit finding is a valuable result; generality is not forced.

CAUSAL is the natural strong test: `exp_representation_canonicalization_v1` (commit e65de60f1)
declared `CANON_CAUSAL = "CAUSALLY_LINKED"` but explicitly never exercised it, and
`hdlab.verb_lexical_similarity`'s "relation" domain covers PART_OF/PRODUCES/CONSUMES/MOVES only --
CAUSAL markers are OOV of that domain by construction (verified, T4 below), so this is a genuinely
NEW relation family, not a held-out marker within the 4 trained classes.

## Prior-work check (mandatory, per exp_dev discipline)

`bash tools/substrate_query.sh "causal relation canonicalization generality cross-domain
three-tier weak-to-strong CauseNet /r/Causes force-dynamics"` -- top cosine=0.3438
(`entity='Cross-domain generalization'`, a general methodology memory note, not a prior arc
cell); #2/#3 `causation`/`Causation` (generic WordNet/FrameNet lexical entries). No prior arc cell
tests three-tier-pipeline generality on a causal relation family. Separately (grep, not
substrate_query): `exp_causal_enrichment_probe_recovery_v1`
(`preregs/2026-08-11_causal_enrichment_probe_recovery_v1.md`) exists and is RELATED (also causal,
also CauseNet/CSKG) but tests a DIFFERENT, disjoint question (KB-enrichment recall on CSKG graph
coverage; no gather_reason/ThreeTierLoop/canonicalization involved) -- not reused, noted for the
record. Verdict: genuinely novel, not a rediscovery.

## Reuse (wire-don't-island; cited per organ)

**Part A (weak->strong):** `hdlab.gather_reason.{ca3_relevance_gather, fanout_two_hop,
recovery_at, real_to_concat, top1}`; `hdlab.situation_model_accumulate.{RelationRegister,
unit_phase_vec}`; `hdlab.kg_traversal.KGStore`;
`experiments.exp_state_of_mind_relevance_gather_reasoning_union_v1.{build_reading_facts,
reading_vocab, reading_fact_set, build_cskg_bridges [wide/blind pool only], build_gap_set,
build_entity_index, fresh_kg, ingest_reading_hop1, ingest_bridge_hop2, build_material_codebook,
scramble_edges, voting_predict, run_self_test}`. `build_gap_set` is reused 100% VERBATIM -- it is
already generic over its `narrow: Dict[material, List[whole]]` argument, no `/r/MadeOf` hardcoded
in its own body.

**Part B (canonicalization):** `hdlab.verb_lexical_similarity.{classify_nway,
mean_similarity_to_seeds, in_lexicon, self_test}` REUSED VERBATIM, zero modification;
`experiments.exp_representation_canonicalization_v1.{canon_entity, build_anchor_set,
content_repr_vector}` (entity side, UNTOUCHED); `hdlab.lexical_similarity.self_test` +
`hdlab.hd_fact_store.{HDFactStore, _run_all_selftests}` (regression witnesses, same convention as
every prior cell in this arc).

## The new things (honestly disclosed, minimum the generality question needs)

1. `hdlab/verb_lexical_similarity.py`: additive `CAUSAL_MARKER_FEATURES` domain (new section (4),
   3 axes independently theory-grounded: `FORCE_DYNAMIC_ROLE` [Talmy 1988 force-dynamics -- the
   SAME citation already used in this file for POS/NEG affect polarity, here extended to its full
   CAUSE/ENABLE/PREVENT agonist-antagonist typology], `CAUSAL_NECESSITY` [Mackie 1965 INUS-
   condition causal theory], `EFFECT_SCALE` [Beavers 2011 scalar affectedness -- the SAME citation
   already used twice elsewhere in this file], + orthogonal `LEXICAL_REGISTER`) + one new
   `_DOMAINS["causal"]` key. Zero existing lines changed; existing `self_test()` re-verified
   unaffected (hardcodes `("outcome","goal")` loops, byte-identical before/after -- MEASURED, see
   Self-test section).
2. `_causal_narrow_from_rows` / `build_causal_bridges_narrow`: a twin of `build_cskg_bridges`,
   narrow-scoped to `/r/Causes` instead of `/r/MadeOf` (wide/blind pool reused verbatim).
3. `learned_causal_canon_for_marker` / `learned_causal_canon_leave_one_out`: causal-domain twins
   of `exp_relation_canonicalization_learned_v1`'s own functions (same body shape, domain="causal").
4. `causenet_causal_corroboration_scan`: literal (material,effect) pair audit against
   CauseNet-precision -- informational only, does not gate the verdict.

Per compute-proportionality (this is a directional generality question, not an
extraction-robustness sweep), no new regex-template extraction machinery was built; Part B tests
canonicalization IDENTITY directly on resolved (subject,relation,object) triples.

## Gap-set construction audit (Step 1, MEASURED)

Reading facts (real extractor, real 15-process corpus) crossed with CSKG's real `/r/Causes` edges
FROM reading-vocab materials TO effect entities (`n_cskg_rows_scanned=1213912`, same corpus the
MadeOf domain scanned), absence-filtered against the reading fact set itself (zero leakage by
construction, `build_gap_set`'s own survive filter).

MEASURED@`data/exp_causal_domain_generality_probe_v1/metrics.json:gap_set_audit` (FULL run):
`raw_n=52, survive_n=52, unique_n=52` (100% survive candidates -- none was ever literally read).
`n_causal_bridge_materials=12` (of 70 reading-vocab words), `n_causal_bridge_edges=46` -- honestly
a SMALLER bridge than MadeOf's 316 edges (disclosed, not hidden: CAUSAL is a rarer CSKG relation
type in this vocab, 1904 `/r/Causes` edges total in CSKG vs comparable order for `/r/MadeOf`).
CauseNet cross-source corroboration (informational, MEASURED): 7 literal (material,effect) pairs
found (`(sugar,cavities)`, `(heat,pain)`, `(heat,irritation)`, `(oxygen,corrosion)`,
`(electricity,electrocution)`, `(car,pollution)`, `(breathing,pain)`) -- the DIRECT CONTRAST with
the MadeOf domain, where the identically-structured scan found ZERO CauseNet overlap.

## Part A: weak->strong arms (mirrors the source cell exactly)

arm0=structural single-source (=0 by construction), arm1=BLIND UNION (no cue, wide pool),
arm2=VOTING (co-occurrence, no chaining), arm3=STATE-OF-MIND CUED (CA3-gathered materials, narrow
`/r/Causes`-only pool). Controls: SCRAMBLE-THE-CHAIN (permute narrow material->effect attachment,
fixed seed, degree-preserving) + ABLATE-THE-CUE (arm1 vs arm3, by construction).

### Bands (REUSED UNCHANGED from the source cell's own calibration, not re-tuned for this domain)

- HARD_PASS: `delta(arm3-arm1)@5 >= 0.20` AND `arm3@5 >= 0.20` AND `scramble@5 <= 0.10` AND
  `ablation_delta >= 0.15`.
- HARD_FAIL: `arm3@5 <= arm1@5` OR `arm3@5 <= 0.05` OR `scramble@5 >= 0.5*arm3@5` OR
  `delta < 0.05`.
- Else MIDDLE_BAND.

### Discriminator-reachability (dev-probe, HYPOTHESIZED before FULL, then MEASURED in FULL)

HYPOTHESIZED@dev probe (this cell's own authoring session, same code paths, different fresh-seed
draw than the final cell's own `SEED_KG_CAUSAL`/`SEED_FHRR_CAUSAL` namespace): arm1@5=0.0192,
arm2@5=0.0192, arm3@5=0.4615, delta=0.4423, scrambled@5=0.0962. Comfortably in the discriminating
band, not saturated/floored.

## Part B: canonicalization generality tests

- **T0 anti-collapse** (`run_causal_anti_collapse`): 9 seed leave-one-out probes (3/class x 3
  classes); CAUSES/ENABLES/PREVENTS must never cross-classify.
- **T1 held-out generalization** (`run_causal_held_out_generalization`): 3 held-out markers
  (induce/facilitate/inhibit) classified via `classify_nway` against the 9 seeds.
- **T2 scramble/circularity control** (`run_causal_held_out_generalization_scrambled`):
  fixed-seed (999) permutation of word->feature-tag assignment must collapse held-out accuracy
  (same recipe as every other scramble control in this codebase).
- **T3 real-data same-rep/distinct-rep** (`run_real_data_same_distinct_rep`): two DIFFERENT causal
  markers (one seed, one held-out) describing the IDENTICAL real gap fact must give an IDENTICAL
  `content_repr_vector`; the same cause-entity with a genuinely different real effect must give a
  DISTINCT vector; the same (cause,effect) pair under a different causal relation-class must give
  a DISTINCT vector. Entity side (`canon_entity`/`build_anchor_set`) reused verbatim, untouched.
- **T4 cross-domain OOV boundary** (`run_cross_domain_oov_boundary`, DIAGNOSTIC ONLY, does not gate
  the verdict): causal markers classified against the OLD 4-class "relation" domain, and vice
  versa -- both directions must ABSTAIN (OOV). This shows the classifier never forces a
  wrong-domain guess; it is NOT evidence the mechanism generalizes or fails to generalize across
  the domain boundary (an OOV abstain is trivial by construction) -- reported honestly as a
  boundary-respect sanity check, not a headline claim.

### Bands

- Part B HARD_PASS: `anti_collapse_ok` AND `held_out_generalization_rate == 1.0` AND
  `scrambled_generalization_rate <= 0.34` AND `t3_ok` (same_rep + both distinct-rep checks +
  no-leak all True).
- Part B HARD_FAIL: `not anti_collapse_ok` OR `held_out_generalization_rate <= 0.34` OR
  `not t3_ok`.
- `RELATION_CLASS_FLOOR=0.50` / `RELATION_CLASS_MARGIN=0.15` REUSED UNCHANGED from
  `exp_relation_canonicalization_learned_v1`'s own calibration (never re-tuned for this domain).
  Closed-form separation MEASURED@dev probe: held-out margin >= 0.68, seed leave-one-out margin
  >= 0.55, cross-class mean sim ~0.07 -- comfortably clears floor/margin.

## Overall verdict tree

`HARD_PASS_pipeline_generalizes_to_causal_domain` iff Part A HARD_PASS AND Part B HARD_PASS =>
GENERAL. `HARD_FAIL_domain_specific_overfit` iff Part A HARD_FAIL OR Part B HARD_FAIL => OVERFIT
(honestly scoped, names which part/control failed). Else `MIDDLE_BAND` => PARTIAL (directionally
informative, does not clear strict joint HARD_PASS margins, does not hit HARD_FAIL floors either).

## Compute architecture

Sequential-CPU, justified: this cell IS a diagnostic composition of already-certified primitives
(`KGStore.predict_one_hop_topk`, `iterative_attractor`) at a small regime (n_ent~4946,
n_targets=52) -- MEASURED wall time (FULL, this cell's own run) = 52.2s, comfortably under the
10s "batching candidate" threshold's spirit given the CSKG single-pass file scan (not matmul) is
the dominant cost. No GPU-batching opportunity (single deterministic pass, not a sweep).

## Self-test (real_code_path)

Calls `exp_state_of_mind_relevance_gather_reasoning_union_v1.run_self_test()` (reused fixture,
regression witness) + `hdlab.gather_reason.self_test()` (promoted-organ regression witness) +
a NEW tiny fixture for `_causal_narrow_from_rows` (4 synthetic rows: one genuine `/r/Causes` hit,
one wrong-relation row, one self-loop, one subject-not-in-vocab row -- must extract ONLY the
genuine edge) + real `classify_nway` calls against the real (production-scale for this ~12-word
domain) `CAUSAL_MARKER_FEATURES` lexicon (T0/T1/T2/T4, all real, no synthetic-only branch).
MEASURED: `SELF_TEST_PASS elapsed=0.23s`.

## SCHEMA-VET declarations

- `arms_differ_verified`: arm1 vs arm3 per-target top-1 index arrays hashed, asserted
  not-all-identical. MEASURED (FULL run): True.
- `final_metrics_atomicity`: `tmp_replace` (single-shot, `os.replace`).
- `except SystemExit / KeyboardInterrupt` re-raised BEFORE `except Exception` (no `BaseException`).
- `crlb_n/a`: discrete top-k retrieval accuracy (Part A) + discrete classification accuracy
  (Part B); `discriminator_reachability=true`, argued via dev-probe + closed-form separation
  above, reproduced by the cell's own FULL run.
- `baseline_in_band`: N/A for arm0 (structural, exempted, same as source cell); arm1/arm2 are
  the real gating baselines (both MEASURED near-floor: arm1@5=0.0, arm2@5=0.0192).
- `cardinality_ok`: Part A 52 real gap targets (FULL, MEASURED) / 43 (smoke, MEASURED); Part B 9
  leave-one-out + 3 held-out x2 (real+scrambled) + 3 real-data pair checks -- all counts logged in
  `metrics.json`.
- `calibration_check`: `default_ok_for_this_regime` (floor/margin reused unchanged, not re-tuned).
- `defensive_error_checking`: start-marker + crash-diagnostic + atomic write present; no heartbeat
  (single deterministic pass, `elapsed_s < 60s`, well under the 30-min `progress_logging`
  mandate threshold -- N/A).
- `progress_logging`: N/A (`timeout_s` declared 300s but MEASURED FULL elapsed 52.2s, well under
  the 1800s/30min mandate threshold; `print(..., flush=True)` used throughout regardless, no
  buffering risk).

## Dispatch

Local, inline, foreground only. NO queue/remote/push (per task constraints). Timeout declared
300.0s (smoke ~15-20s, FULL ~50-60s MEASURED, generous headroom).
