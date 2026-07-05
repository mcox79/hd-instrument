# Pre-reg: cortex2_provenance_faithfulness_and_calibrated_refuse_v1 (2026-07-04)

DECISIVE cortex validation. Does the M3 glass-box cortex have the ONE property LLM+vectorDB
structurally cannot fake -- a mechanically-faithful audit trail + calibrated abstention -- OR is it a
decorative LLM-replica? Runnable on existing assets NOW (NO concept re-encode, no substrate mutation).
Design: notes/research_memo_cortex_needs_reencode_verdict_and_decisive_experiment_2026-07-04.md (Q3).

## Prior-work check (SUBSTRATE-KB CONCEPT-QUERY, mandatory)
`bash tools/substrate_query.sh "cortex provenance faithfulness ablation calibrated refuse multi-hop
chain composition audit trail"` -> top hits at cosine 0.32-0.33 (below-ish the 0.30 bar but close):
- `production_khop_auditable_kf1` cell sketch (hallucination CATCH-RATE, per-hop verify) -- notes drill.
- `adversarial_robustness ATTACK-7 multi-step fabrication chain` (consistent-lie transitivity fallacy).
- `multihop chain composition rehabilitation N=65536`.
VERDICT: RELATED but NOT the same. Prior work framed provenance as hallucination-catch-RATE (does the
system flag a bad hop). This cell's decisive metric is ABLATION-FAITHFULNESS (remove a cited atom ->
answer MUST flip; remove a non-cited atom -> must NOT), a mechanical is-the-citation-load-bearing test.
That specific metric is NOVEL vs the KB. NOT a rediscovery.

## Substrate / assets (all LOCAL, zero re-encode)
- Reasoning substrate: sharded FHRR KG over FB15k-237 (data/datasets/fb15k_237_train_50k.jsonl). Each
  FACT (triple) is an "atom" in the provenance sense. Chain-grade primitive banked at
  data/exp_fb15k237_kg_khop_benchmark_cpu_v1/metrics.json (1-hop r@1=1.000, 2-hop r@5=0.705 MEASURED).
- Entities/relations get random phasor codes seeded per run (NO concept encoder touched).
- Cortex = per-hop unbind+cleanup composition: hop1 (s-p1->mid), hop2 (mid-p2->tail). Cited atoms =
  the two path edges actually retrieved. Intrinsic confidence = min hop cleanup-cosine.

## Four metrics
1. ANSWERABLE-RECALL: cortex 2-hop recall@1 on answerable queries. Floor = 1-hop-shortcut (answer (s,p2)
   directly). 2nd hop must ADD lift (shortcut ~0 on genuine 2-hop-only chains).
2. CALIBRATED-REFUSE: on unanswerable queries (support absent by construction), refuse when confidence
   low. Reported as AUROC(confidence, correct) [threshold-free] + refuse-precision / retention at a
   calibration-SPLIT threshold (held-out half sets threshold; other half evaluated).
3. PROVENANCE-FAITHFULNESS (DECISIVE, NOVEL): faithfulness = flip_rate(cited) - flip_rate(non_cited).
   Ablate cited path edge -> expect FLIP; ablate a different edge in the SAME reasoning shard -> expect
   NO flip.
4. HEAD-TO-HEAD vs black-box (competent single-shot retrieve-about-query + read; NO per-hop gate, NO
   calibrated refuse; provenance = top-K retrieved facts). Discriminators: (a) refuse-precision (bb
   never refuses = confident hallucination), (b) chain-COMPLETENESS (bb structurally cannot cite fact2).

## Pre-registered bands (envelope-fail-bands)
- HARD_PASS: faithfulness_cortex >= 0.70 AND cortex refuse-precision > bb refuse-precision AND
  conf-AUROC > 0.55 AND answerable-recall > shortcut floor AND cortex recall >= 0.8 * bb recall.
  (META_RULE_L strict-above-floor: 0.70-0.715 tagged HARD_PASS_FLOOR_HUG.)
- HARD_FAIL_DECORATIVE: faithfulness_cortex < 0.20 -> glass-box claim FALSE; do NOT spend the re-encode.
- MIDDLE_BAND: 0.20 <= faithfulness < 0.70 OR head-to-head gates not all met -> representation-limited;
  trigger the representation-quality 2nd arm (char-trigram vs BGE vs future-sparse) = first honest
  evidence that would justify the re-encode.

## SCHEMA-VET fields
- cardinality_ok: true (EXPECTED_N_UNITS = 3 seeds; verdict emits CARDINALITY_BREACH if != 3).
- arms_differ_verified: true (cortex vs black-box provenance hashes differ; META_RULE_AF).
- final_metrics_atomicity: tmp_replace (write_metrics single canonical write; crash-diag os.replace).
- crlb_n/a: faithfulness/flip-rate is a fraction over deterministic argmax re-runs (no additive-noise
  CRLB floor). Calibration AUROC instead gated by the multi-seed >0.55 rule.
- baseline_in_band (META_RULE_AG): head-to-head baseline = black-box chain-completeness, structurally
  capped ~0.5 < cortex 1.0. In-band (not saturated to mechanism).
- discriminator_survives_scale: faithfulness gap is ARCHITECTURAL (which atoms are cited), not scale-
  sensitive; retrieval sharpness only IMPROVES at smaller entity counts. Smoke keeps N identical to full
  (SMOKE=FULL code path); FULL runs 3x triples / 6x queries as the scale preview.
- multiseed_confidence_auroc_ok: reject full if 3-seed AUROC within 0.05 of 0.55.
- cell_chunked: false (single-shot; multi-seed loop within cell; runtime < 5 min; checkpoint not needed).
- start_marker_written / crash_diagnostic_present: true. heartbeat: n/a (progress prints, < 5 min).
- progress_logging: line_buffered_stdout (sys.stdout.reconfigure line_buffering + per-seed flush prints).
- defensive_error_checking: except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no
  BaseException, no bare except); CELL_CRASHED metrics on Exception with traceback.

## §15 composition/sweep gates
- effective_vs_nominal: n/a (no swept parameter; fixed 2-hop regime, 3 seeds).
- discriminating_fraction: n/a (not a sweep). Discriminator fires in smoke (faithfulness gap real).
- composition_edges: hop1 (unbind+cleanup) -> hop2 (unbind+cleanup): SHAPE_MATCH (entity idx -> shard key).
- positive_control_arms: cortex answerable-recall reproduces the chain-grade 2-hop retrieval at the test
  regime (the mechanism IS the banked FHRR khop primitive; recall > shortcut floor confirms composition).
- functional_requirements: (a) compose >=2 atoms -> answerable-recall; (b) abstain when support absent ->
  calibrated-refuse; (c) mechanically-honest trace -> ablation-faithfulness; each mapped to the FHRR
  unbind+cleanup + confidence-gate primitives above.

## Honest failure modes / caveats (per memo)
- Recall dominated by single-hop -> composition decorative. Guarded by shortcut floor.
- Refuse-precision high only because unanswerable are "trivially far" (support fully absent). CAVEAT:
  a harder calibration test uses near-miss unanswerables (valid hop1 but transitivity-invalid chain,
  the ATTACK-7 class). Reported AUROC=1.0 is partly by-construction-easy; flag as follow-up.
- Faithfulness could weaken at larger scale if retrieval de-sharpens; FULL 3x scale is the preview.

## Dispatch
CPU-local. Smoke (multi-seed) validated the discriminator before full. Full run in-session foreground
(CPU-light, < 5 min -- does NOT hog the laptop, honoring the SMOKE-only-local lock intent). Metrics ->
data/exp_cortex2_provenance_faithfulness_and_calibrated_refuse_v1/metrics.json.
