# PRE-REG: Compress-and-Carry Comprehension Loop (CCL) v1

Anchor: `compress_and_carry_comprehension_loop_ccl_v1`
Date: 2026-07-19  Author: hdi_exp_dev (inline, foreground-local)
Design note: `notes/research_situation_model_guided_comprehension_loop_compress_and_carry_2026-07-19.md`
Baseline cell: `experiments/exp_learned_argstruct_parser_lccp_independent_gold_v1.py` (LCCP, atom 29338, commit 3c6ff0f3)
Gold: `data/gold_mcguffey_lccp_argstruct_v1.json` (280 items, 7 lessons = multi-sentence DOCUMENTS)

## Question
Does wiring a carried, situation-model DOCUMENT-COHERENCE cue into the LCCP scorer (integrated as ONE
weighted parallel cue, per Angle-2, NOT a late rerank), with macrorule-COMPRESSED carry + MAP/SHIFT
checkpoint, (a) RAISE precision on the within-frame-coherent-but-DOCUMENT-incoherent failure class the
sentence-local LCCP cannot catch, and (b) produce a POSITIVE within-document COMPOUNDING slope (precision /
doc-coh discriminative margin RISING across a document as the situation model grows)?

## Arms (ONE variable per step)
- ARM A = LCCP sentence-local (situation model OFF). MUST byte-reproduce LCCP arm C (positive control / Gate D).
- ARM B = A + Step-2b document-coherence cue (FLAT uncompressed carry) integrated as one weighted additive
  term in the per-verb-instance best-candidate scorer + DEFERRED state for base-vs-doc conflict. [A->B = the cue]
- ARM C = B + PE-triggered MAP/SHIFT macrorule-compressed carry + LTWM gist-cue retrieval. [B->C = compression]

The document-coherence cue is computed from the parser's OWN committed agents/patients + prior-sentence
content (NO gold leakage; causal/online: model reflects PRIOR sentences only). doc_weight fixed 0.5
(weighted, not a veto -> respects Angle-2 honest exception that strong local cues legitimately resist).

## Measured (decisive)
(a) PRECISION-RAISE: overall precision A/B/C (past the LCCP 0.500 ceiling?) + within-frame FP count/precision
    (the specifically named class) + FP-class split + recall retention.
(b) COMPOUNDING: within-document learning curve -- precision + doc-coh discriminative margin (mean doc-coh of
    TP-kept minus FP-kept) binned by position-in-document (first-half vs second-half + continuous slope w/
    bootstrap CI). ARM A (no situation model) precision-slope = construct-validity control (should be flat).
(c) COMPRESSION DISSOCIATION: C vs B doc-coh margin + precision on LONG docs (>= median sentences) vs SHORT.
(d) checkpoint firing: # SHIFTs detected + positions (NO human scene-boundary gold for this corpus -> report
    firing only; NO boundary-agreement claim -- honest caveat).

## DESIGN-GATE (pre-registered; verified at smoke BEFORE full)
- G1 REAL baseline = LCCP arm C sentence-local. MEASURED@data/exp_learned_argstruct_parser_lccp_independent_gold_v1/metrics.json:
  overall precision 0.500, within_frame_fp 6, recall 0.340, learning_curve.slope_first_minus_later -0.160.
- G2 baseline_in_band: 0.05 < arm-A precision < 0.95 (MEASURED 0.500 -> in band).
- G3 CAN-FAIL-BOTH-WAYS: doc-coh cue can HURT (suppress a true patient that is a legit scene-change / surprising
  new entity) as well as help; compounding slope can be positive OR flat/negative. Both reachable.
- G4 DISCRIMINATOR FIRES: arms differ (kept-set hashes A!=B!=C) AND doc-coh cue changes >0 decisions at smoke.
- G5 GATE-D POSITIVE CONTROL: ARM A kept-set hash == LCCP arm C kept-set hash (byte-exact reproduction at test
  regime). If mismatch -> HARD_FAIL_GATE_D_INVOCATION_MISMATCH; downstream arms suspect.

## Prior-signal (MEASURED at probe; sets honest expectation, NOT a claim)
- doc-coh RE-RANK among multi-candidate transitive instances = CHANCE (flat 10w/9l, recency 9w/10l,
  compressed 9w/10l over n=19). MEASURED@probe 2026-07-19.
- doc-coh mean margin (true-false) POSITIVE and compression-sharpened: flat +0.073, recency +0.077,
  compressed +0.083 (n_pairs 38). MEASURED@probe 2026-07-19.
- => Expectation: precision-raise WEAK (a weak cue vs strong learned local cues; Angle-2 honest exception);
  compounding is the riskier/novel axis. A PARTIAL or HARD_FAIL on precision with a detectable margin signal
  is the honest likely landing. Bands set so HARD_PASS is genuinely reachable-but-unlikely, HARD_FAIL reachable.

## VERDICT BANDS (pre-registered; strictly above floor per META_RULE_L)
- AXIS-1 precision-raise PASS: overall precision(C) >= 0.55 (baseline 0.500 + 0.05) AND within_frame_fp(C) <=
  within_frame_fp(A) AND recall retention (C/A) >= 0.60. FAIL: precision(C) <= 0.50 (no raise).
- AXIS-2 compounding PASS: C within-document margin slope > 0 with bootstrap 90% CI excluding 0, OR C
  precision second-half > first-half by >= 0.05 WHILE arm-A second-vs-first flat (|slope_A| < axis-2 margin).
  FAIL: C slope flat/negative (CI includes 0 AND second-half not > first-half).
- HARD_PASS_CCL = AXIS-1 PASS AND AXIS-2 PASS.
- PARTIAL_CCL = exactly one axis passes (report WHICH; precision-raise alone = real component win; compounding
  alone = novel property met).
- HARD_FAIL_CCL = neither axis passes (report honestly; the improving-as-reads property not achievable this
  way = crucial finding, per Angle-3's evidentiary gap in both directions).

## BRAIN-CHECK (outcome NOT pre-assumed)
Situation-model-guided CI + macrorule-compressed carry is brain-faithful (Kintsch/van Dijk CI + leading-edge;
Ericsson&Kintsch LTWM; Zwaan/Gernsbacher MAP/SHIFT; Crain&Steedman/MacDonald immediate discourse integration).
HONEST bounds: (1) some mis-attachments resist discourse-context override even in human wetware when a local
obligatory-argument cue is strong (Mitchell/Corley/Garnham 1992; Britt 1994) -> weighted-feature not veto,
expect residual FPs = real shared ceiling, ACCEPT. (2) within-single-document compounding has NO direct human
precedent in EITHER direction (Angle-3) -> a null is a genuinely informative negative, the FIRST direct test.
(3) Tier-2 bundle is subject to the same N/16-32 crosstalk ceiling biology hits -> compression relocates the
bound, does not lift it. Where's the real bound? Likely: the doc-coh cue is too weak relative to the strong
learned local cues to move hard decisions (probe = chance re-rank) -> precision-raise fails, matches Angle-2.

## COMPUTE ARCHITECTURE (mandatory)
Class (b) sequential-CPU with justification: ~225 reader candidates, a few hundred GloVe cosines + reuse of
LCCP's tiny logistic; per-document situation-model accretion is inherently sequential (step N depends on the
document read so far). Wall < ~90s. Storage: no_storage (extraction-precision measurement). Determinism:
OMP/MKL/OPENBLAS=1, fixed int seeds, deterministic hashlib; no salted builtin hash / list(set); numpy default
RNG seeded. progress_logging: print_flush_true (though wall < 30min so not gate-required). Foreground local-to-
completion (NO queue; NO push; NO remote-persist).

## CELL-TEMPLATE (subset for a LOCAL foreground measurement; NOT queue-dispatched)
arms_differ_verified (A/B/C kept-set hashes differ); final_metrics_atomicity: tmp_replace; except SystemExit:
raise BEFORE except Exception (no BaseException); baseline_in_band at smoke; discriminator fires; Gate-D
positive control (A == LCCP-C); scaffold-free witness (a real within-frame doc-incoherent case C catches that A
keeps, + a within-document case where the carried model constrains a later parse); deterministic seeding; all
numbers tagged MEASURED@/CITED@ (printed at run). CLAIM-VET-pending; single-annotator gold (caveated).
