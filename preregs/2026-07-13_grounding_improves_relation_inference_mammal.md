# Pre-reg: GROUNDING-IMPROVES-REASONING (held-out RELATION inference, with/without grounding ablation)

- Anchor: `grounding_improves_relation_inference_mammal_v1`
- Cell: `experiments/exp_grounding_improves_relation_inference_mammal_v1.py`
- Date: 2026-07-13
- Queue target: `remote_cpu_queue` (CPU-cheap; N~128, nq~30, seconds/seed)

## Question (the deep-prize test the two prior grounding cells did NOT run)
Prior grounding cells measured ATTRIBUTE RECOVERY ("does channel B predict a held-out numeric
attribute") -- near-tautological, landed GROUNDING_REDUNDANT. This cell measures the KBLRN/LiteralE
result on our substrate: does fusing MEASURED attributes into the substrate improve the REASONING task
= inference of HELD-OUT RELATIONS (link prediction), via a with/without ablation?
CITED@notes B-field drill: LiteralE (Kristiadi et al. 2019, arXiv:1802.00934) + KBLRN
(Garcia-Duran & Niepert 2018, arXiv:1709.04676) -- fusing numeric literals into KG embeddings
improves link prediction by +0.01-0.04 MRR, documented with a with/without ablation.

## Domain + why attributes are RELATION-RELEVANT (fairness crux)
Entities = 65 mammal species (real). KG relations = phylogenetic taxonomy edges (species -HAS_ORDER->
order, -HAS_FAMILY-> family, -HAS_CLADE-> clade). Task = predict a held-out species' ORDER/FAMILY/CLADE
tail. Measured attributes = adult body mass, head-body length, max longevity, gestation, litter size
(CITED@AnAge/PanTHERIA/Walker's class). RELEVANT via PHYLOGENETIC SIGNAL in life-history: related taxa
share life-history scaling (long gestation+longevity+singleton litters = primates; short
gestation+large litters = rodents; Blomberg's K / Pagel's lambda, CITED@comparative life-history
theory). NOT tautological: a SINGLE attribute (mass) varies 10^6 WITHIN one order (mouse vs capybara
both Rodentia), so no single attribute recovers the relation -- only the JOINT trait vector carries the
phylogenetic signal a sparse-support held-out entity's relational code lacks. Grounding CAN help, and
must clear a SCRAMBLE control (attributes shuffled across entities) to prove it is the RIGHT attributes.

## Metric (PRIMARY = held-out RELATION inference, NOT attribute recovery)
Filtered MRR + hits@{1,3,10} rank-vs-all (KGE standard, degree-unbiased; no sampled-negative pool).
Held-out-HEAD split: withhold HELDOUT_ENTITY_FRAC=0.30 of species from every train edge; partition each
held-out species' edges into SUPPORT (SUPPORT_FRAC=0.34) + QUERY (scored). Query edges whose gold symbol
is train-absent are DROPPED (arena cannot answer). All arms scored PAIRED on the SAME query edges.

## Arms (SHARDED per-entity codes; the only bundle is a per-ENTITY anchor mean)
- RELATIONAL_ONLY (ablation baseline): held-out code = mean over support edges of (X[symbol]-D[r]).
- GROUNDED_FUSED (mechanism): RELATIONAL bundle FUSED (alpha=beta=1) with a grounded estimate = ridge
  map (fit on SEEN species only) from FPE random-Fourier features of the measured attributes into the
  learned latent (LiteralE: literals inform the embedding). Reuses the proven allometry FPE wiring
  (fpe_encode, decay Spearman 0.999).
- GROUNDED_ONLY (diagnostic): grounded estimate only (does grounding carry reasoning info at all).
- SCRAMBLE_FUSED (must-fail): fused with attributes SHUFFLED across species (right-attributes control).
- RANDOM_CODES (null); ORACLE_ADDITIVE (held-out folded in = arena-answerable ceiling); BASELINE_POP.

## PRE-REGISTERED BANDS (BOTH sides; ABSOLUTE, literature-anchored; NOT tuned on the smoke)
Ceiling-relative bands DO NOT transfer here: ORACLE saturates (~0.98) BY CONSTRUCTION (it trains on the
query edge), so its headroom is not a usable ceiling for a marginal ablation delta (regime-mismatch
discipline). ORACLE is the arena-answerable gate only. Bands = absolute LiteralE-scale:
- GROUNDING_IMPROVES_REASONING (HARD_PASS): mean (FUSED - RELATIONAL)_mrr >= 0.03 (strict end of the
  LiteralE +0.01-0.04 range) AND per-seed gain>0 in >=60% of seeds AND (FUSED - SCRAMBLE)_mrr >= 0.02
  AND ORACLE fires (>=3x RANDOM & headroom>=0.05) AND RELATIONAL above RANDOM (>=0.02) AND not broken.
- NO_IMPROVEMENT (MIDDLE_BAND = GROUNDING_REDUNDANT_FOR_REASONING): delta in (-0.03, 0.03) or fails
  consistency/scramble-margin.
- GROUNDING_HURTS_REASONING (HARD_FAIL): mean (FUSED - RELATIONAL)_mrr <= -0.03 with ORACLE firing.
- INCONCLUSIVE if ORACLE does not fire / too few held-out queries / RELATIONAL at floor / RANDOM beats
  RELATIONAL (broken).

## FULL config
k=16, epochs=300, n_neg=48, seeds=[7,13,17,23,29,31,37,41] (8), device cpu. Weak-point localization:
support-degree stratified ablation delta (expect gain concentrated at LOW support / cold species).

## Validity preflight (F.1-F.4 ENFORCE) + machinery
- F.1 real_code_path: self-test CALLS fit_kge_anchor1 + filtered_hits_from_scores on the planted arena.
- F.2/F.3 substrate_signature: fit_kge_anchor1 bound with BASE/portable kwargs only.
- F.4 guard_baseline_valid: RELATIONAL_ONLY validated above RANDOM floor.
- positive_control: PLANTED latent-consistent arena where attributes carry the latent -> FUSED MUST beat
  RELATIONAL and SCRAMBLE -> the ablation detects grounding-helps when it is real (ship gate).
- arms_differ (>=5 sigs), cardinality (n_seeds), no bare except, atomic metrics (tmp_replace),
  progress_logging=print_flush_true.

## Smoke result (3 seeds, real mammal KG) -- HINT ONLY (hold mechanism story until landed-VET)
MEASURED@data/exp_grounding_improves_relation_inference_mammal_v1_smoke/metrics.json:
verdict=HARD_PASS_GROUNDING_IMPROVES_REASONING (BORDERLINE). RELATIONAL_mrr=0.3246 FUSED=0.3564
(gain=+0.0318, just clears 0.03; per-seed gains +0.041/-0.022/+0.076 = 2/3 positive, seed13 negative).
SCRAMBLE=0.2858 (fusing WRONG attributes HURTS below relational; fused-scramble margin +0.071).
GROUNDED_ONLY=0.5167 (attributes ALONE beat pure-relational inductive inference by +0.19 -- the cleaner,
larger corroborating signal). ORACLE=0.9834 (39.9x RANDOM, fires). SELFTEST_PASS under enforce.
Caveat: the fused gain is borderline + seed-inconsistent at 3 seeds; the 8-seed FULL is the arbiter.
