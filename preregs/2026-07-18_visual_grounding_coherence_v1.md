# Pre-reg: visual_grounding_coherence_v1

Date: 2026-07-18 | Author: exp_dev | Cell: `experiments/exp_visual_grounding_coherence_v1.py`
Run mode: FOREGROUND-LOCAL (Director-authorized). NO queue_add / NO push / NO remote-persist.
Scope note: `notes/scope_visual_grounding_early_reader_words_substrate_native_2026-07-18.md`

## Question (drill-sharpened; NOT the solved "encode an image")
Does a concrete word's PERCEPTUAL grounding COHERE with + ADD to its RELATIONAL
(dictionary/WordNet) grounding, or merely re-encode it? A pass must BEAT a dictionary-only
control; else vision adds nothing yet -> DEFER vision (valid USER-endorsed win for the control).

## Prior-work check (concept-query, mandatory)
Top note hit = cross-domain-analogy drill (cosine 0.34, ConceptNet-as-relational; tangential).
Genuine prior arc = the two drills the scope note credits: cross-modal VSA (06-09) +
resonator-capacity (06-04). NO prior CELL on perceptual-relational coherence at cosine>0.30.
Verdict: GENUINELY NOVEL (a build on those two drills, credited; not a rediscovery).

## Glass-box invariant (load-bearing)
INGEST (scaffolding, external allowed): CLIP (transformers, clip-vit-base-patch32) = sensory
transducer pixels->512-d; WordNet (nltk) = independent relational grounding; QuickDraw (CC-BY 4.0)
= images. RUNTIME (glass-box, numpy, NO torch/transformers): FHRR bind/unbind + cosine-argmax
cleanup + Spearman. Every image (incl held-out queries) transduced at ingest, then reasoned over
in glass. CLIP never touched at runtime.

## Arms / baselines (design-gate)
- (a) CHANCE = 1/K.
- (b) SHUFFLED-grounding control -> MUST collapse (guards leakage/saturation).
- (c) DICTIONARY-ONLY = no-vision control the perceptual arm MUST BEAT (T1: structurally cannot
  map pixels->word -> chance; T2b: WordNet rates confusable pair near-identical -> 0.5).
- CAN-FAIL: weak sketch-CLIP -> T1~chance / T2b~0.5 -> HARD_FAIL -> DEFER (genuinely reachable).
- ONE VARIABLE: CLIP-scaffold perceptual arm. HDC-native front-end HELD for a 2nd cell (Frontier-2).

## Tests + PASS/FAIL bands (HYPOTHESIZED @ this prereg)
K_full=21 -> chance 0.048; K_smoke=6 -> chance 0.167.
- T1 picture->word (cross-modal, glass-box cleanup):
  PASS: t1_acc >= max(0.30, 3*chance) AND t1_acc > shuffled+0.10 AND shuffled collapsed.
  FAIL: t1_acc <= ~chance or not above shuffled.
- T2a coherence (Spearman rho, FHRR perceptual vs WordNet Wu-Palmer):
  PASS: rho >= 0.30 AND rho > null_p95 (500-perm shuffled-label null) AND emp_p < 0.05.
  FAIL: rho < 0.30 or not above null.  [strictly-above-floor per META_RULE_L]
- T2b ADD-delta (confusable 2-way; perceptual vs dictionary-only 0.5):
  PASS: t2b_perc >= 0.65 (delta >= +0.15).  FAIL: < 0.65 (vision adds nothing on discrimination).
- T3 scene-rep (substrate primitive sanity; grounded object vectors):
  PASS: t3_acc >= 0.85 AND shuffled-scene <= chance-band. (Sanity, NOT the novel claim.)

OVERALL HARD-PASS = T1 & T2a & T2b pass (AND T3 sanity holds) = vision-grounding genuinely helps.
OVERALL HARD-FAIL = any of T1/T2a/T2b fails = DEFER vision, advance text-first.
Deflate honestly; if HARD_FAIL, localize sketch-modality vs approach (photo upgrade = follow-up).

## Discriminator-survives-scale
Smoke runs at FULL-N (N_fhrr=4096) with K=6 (chance 0.167, EASIER than full 0.048). Mechanism
(sketch-CLIP carries word signal; FHRR preserves ranking) is scale-invariant for T2b (2-way) and
projection-preservation; coherence rho at K=6 (15 pairs) is noisy -> full K=21 (210 pairs) is the
real coherence number. Smoke = pipeline + discriminator-fires gate (perceptual > shuffled).

## SCHEMA-VET / cell-template compliance
- except SystemExit: raise BEFORE except Exception (no BaseException). No bare/silent except.
- final_metrics_atomicity: tmp_replace (os.replace).
- arms_differ_verified (META_RULE_AF hash-test on perceptual/text anchors + WordNet mat).
- calibration_check: adaptive_with_gate (gamma=1/sqrt(median_pairwise_d2), logged; shuffled+null
  controls verify discriminator fires).
- discriminator-fires gate: shuffled T1 must collapse to chance-band; else leakage -> not PASS.
- baseline_in_band: chance in measurable band (K>=6).
- crlb_n/a: recovery/coherence task; no closed-form noise floor. Chance/shuffled/null are the floors.
- Numbers here HYPOTHESIZED@this prereg; run is foreground-to-completion -> MEASURED numbers reported.
- self-test: offline, real FHRR/cleanup/scene/Spearman/npy-parse/arms-differ/WordNet paths (<10s).

## Brain-check (pre-registered)
Concrete-noun visual grounding = how children fast-map early vocab (picture<->word). A T1/T2
failure is presumed encoder/impl bug OR sketch-modality limit (photo upgrade follow-up), NOT a
structural bound -- localize which before accepting the negative.

## Credit
Frady/Kent/Olshausen/Sommer 2020; Renner et al. 2024; Hersche et al. 2023 (NVSA); Radford et al.
2021 (CLIP); Kanerva/Gayler/Plate (VSA scene-as-binding); Google Quick,Draw! (CC-BY 4.0).

## Compute architecture
Class (c) mixed: INGEST = torch/CLIP forward passes (batched CPU, cached to disk). RUNTIME =
sequential-CPU numpy over K<=21 anchors + a few hundred scene draws; wall << 10s at runtime.
Storage: sharded (each word its own anchor vector; no bundled composition of the anchor set).
Local CPU foreground; ~1-2 hr incl one-time CLIP model + QuickDraw partial download; $0.
