# Pre-reg: compositional-surprise DECONF re-run (was "surprise inert" an extractor artifact?)

anchor: `ingest_gate_compositional_surprise_deconf_v1`
cell: `experiments/exp_ingest_gate_compositional_surprise_deconf_v1.py`
date: 2026-07-16
author: hdi_exp_dev (Director-dispatched)

## Question
The combination-rule race concluded SCHEMAFIT_CARRIES: additive-DIRECT surprise DECONF_AUC ~chance
(deconf_full flat=0.545 MEASURED@data/exp_ingest_gate_combination_rule_race_v1/metrics.json:agg.deconf_full.flat)
while schema_fit alone carried within-relation derivability (schemafit=0.719 MEASURED@ same). That "surprise" is the
additive-map DIRECT readout score(t) = -||X_h + D[r*] - X_t|| using the MEMORIZED whole-relation operator D[r*], which
captures whole-relation presence (~ a degree/frequency signal) and cannot separate derivable from underivable r*
facts. TEST: recompute surprise from a COMPOSITIONAL readout (compose the constituent operators along r* = r0 o r1),
re-run the SAME v4 within-trained-relation derivable-vs-underivable DECONF_AUC.

## Arms (all non-fitted; higher score = more UNDERIVABLE)
- ARM_ADD_FLAT   : 1 - RR(pred = X_h + D[r*])            (additive-DIRECT; reproduces race flat ~chance -- Gate D)
- ARM_SCHEMAFIT  : 1 - schema_fit(reachability)          (reproduces race schemafit ~0.72 -- REFERENCE)
- ARM_COMP_OP    : 1 - RR(pred = X_h + D[r0] + D[r1])    (NEW operator-composition along the generative path)
- ARM_COMP_PATH  : 1 - max_mid RR(pred=X_mid+D[r1]), mid in top-M of (h,r0)  (NEW discrete 2-hop traversal)
- ARM_RECUR      : deg(h)/(deg(h)+TAU)                   (graded recurrence/degree -- the confound probe)

## Decisive metric
DECONF_AUC per arm = AUC(score; UNDERIVABLE vs DERIVABLE), both held-out, SAME trained r* row, IDENTICAL v4 split
(split RNG derivation copied VERBATIM from race_seed). Full balanced held set (non-fitted arms -> matches deconf_full).

## Bands (HYPOTHESIZED@this-file; chance=0.50 self-checked by RANDLABEL)
- HP_DECONF_MIN = 0.65  (comp arm carries the signal; >chance+0.15, +5% band)
- HF_DECONF_MAX = 0.58  (arm ~chance)
- DECISIVE_MARGIN = 0.10 (comp decisively beats additive-flat)
- CONVERGE_EPS = 0.07   (comp converges with schema-fit -> free-energy "one quantity" view)

## Verdict tree
- EXTRACTOR_ARTIFACT_comp_carries : comp_op/comp_path >= 0.65 AND >= flat + 0.10 => "surprise inert" was an extractor
  artifact; compositional surprise recovers the signal. Sub-case CONVERGES_WITH_SCHEMAFIT if |comp - schemafit|<=0.07.
- SURPRISE_GENUINELY_INERT : comp_op AND comp_path <= 0.58 => surprise genuinely inert; schema-fit-direct stands.
- MIDDLE_BAND_partial : straddles.

## PASS / FAIL bands (envelope)
- PASS (either decisive outcome is a clean finding): harness_valid AND (EXTRACTOR_ARTIFACT or GENUINELY_INERT).
- MIDDLE: comp arms straddle 0.58..0.65 (underpowered / partial signal -> report, no over-claim).
- FAIL/INCONCLUSIVE: harness or Gate-D positive control not validated (split diverged from the race).

## Controls (harness-valid)
POSCTRL (corrupt-r* vs in-train-r*) >= 0.75; CONF (untrained-row confound) >= 0.70; RANDLABEL in [0.40,0.60];
rstar_train_mrr >= 0.30; infer_mrr in (0.05,0.95) and >= 0.40; class balance >= 0.20. Gate D positive control:
ADD_FLAT <= 0.60 (reproduces additive-inert) AND SCHEMAFIT >= flat + 0.08 (reproduces schema carries).

## Compute architecture
Sequential-CPU, device=cpu default (remote portability). Justification: this IS the additive-map substrate readout
being validated; tiny arena (N=300 smoke / 600 full); readouts are the already-chunked matmul additive_direct_scores;
3 independent seeds; total wall < 10 min. Not a batching candidate. No storage/composition of bundled items.
`crlb_n/a`: DECONF_AUC is a rank statistic over two measured score distributions; chance=0.5 self-calibrated by the
RANDLABEL must-fail control; no closed-form noise floor. deterministic_seeding: true (fixed int seeds; no hash()).

## Reuse
v4 gen_composed_arena / derivability_labels / _exact_path_labels / _balance_mask / _arena_cfg; v2 fit_foundation /
_to_int / _mean; v1 _auc / _recip_ranks / _surprise / build_schema_fit / schema_fit_edges / additive_direct_scores.
New: comp_op_surprise, comp_path_surprise, the head-to-head.

## Prior-work check (substrate-KB concept query)
Top hits at cosine ~0.42 were generic vocabulary nodes ('composition' wordnet/atoms, a K-extended prereg 'COMPOSITION
MAP') -- NO prior arc cell computes a compositional-surprise DECONF. Genuinely novel extension of the race machinery.
