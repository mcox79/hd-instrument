# PRE-REG: SCALE meaning-learning v2 -- CLEAN-WIN promotion (fix fusion + relational headroom + checkpoint)

- anchor: `scale_meaning_learn_arc_heldout_v2`
- cell: `experiments/exp_scale_meaning_learn_arc_heldout_v2.py`
- date: 2026-07-27
- author: exp_dev (hdi_exp_dev), per Director "convert the VET-confirmed partial win (seq 29590) to a clean win"
- base: v1 (`exp_scale_meaning_learn_arc_heldout_v1.py`) -- REUSES its exact leak-proof pipeline
  (concept-level scrub, corpus prep, controls, zero-overlap witness, both seeds). Training UNCHANGED.
- plan: `notes/scale_corpus_and_data_integrity_plan_2026-07-26.md`, `notes/WHERE_WE_ARE_NOW_2026-07-26.md`
- target queue: `overnight_queue` (GPU: remote RTX 4060 Ti) -- pushed + launched by orchestrator (exp_dev cannot push)
- compute class: (a) batched-GPU (transformer MLM + concept encode fully batched; AMP on cuda)
- storage strategy: no_composition (learned-encoder cell; no HD store / no bundled composition)

## Why v2 (the exact gaps the v1 VET named)
v1 FULL was VET-confirmed leak-proof and the from-scratch text encoder at ~121M trained tokens BEAT
grounding on held-out-NEW SEMANTIC concepts by +0.039 (both seeds). But v1's pre-registered PRIMARY was
the naive 50/50 FUSED arm, which UNDERPERFORMED text-alone (fusion HURT: 0.636 -> 0.605), so v1 scored
TIE_NULL. v2 closes the three named gaps so the real win reads as a clean win.

MEASURED v1 FULL (both seeds) @data/exp_scale_meaning_learn_arc_heldout_v1/metrics.json
(local copy: scratchpad scale_metrics.json):
- semantic raw_grounding = 0.5968 ; text-alone = 0.6356 (seed7 0.6340 / seed13 0.6372) ; fused_50/50 = 0.6045
- text-alone - raw = +0.0388 (per-seed min +0.0372) ; learn(text-random) = +0.1034 ; collapse 0.4964 pop 0.4968
- relational raw = 0.5617 ; fused_50/50 = 0.5679 ; (text-alone NOT computed in v1 relational = the missing headroom number)
- well-covered (>=100 mentions): raw 0.5931 / text 0.6328 / fused 0.6009

## Checkpoint resolution (gap-3 preflight; RESOLVED)
The VET believed a v1 text-encoder checkpoint (ckpt 7/13) existed -> EVAL-ONLY re-run. DISPROVEN off disk:
v1 cell has NO `torch.save` (grep), and the remote dir holds only `metrics.json` + `partial_metrics_7/13.json`
+ `_heartbeat.jsonl` + `_start_marker.json` (no `*.pt/*.ckpt/*.npz`). The `_ckpt_key` field is the
`_seed_checkpoint.write_partial` per-seed RESULT resume key, NOT model weights. => No checkpoint exists;
v2 must FULL-RETRAIN and SAVE the checkpoint this time.

## v2 changes (eval-side only; training identical to v1)
- GAP-1 FIX FUSION: PRIMARY = `ARM_FUSE_SELECTED` = the best-honest text+grounding combination SELECTED on
  the TRAIN-eval split (leak-proof model-selection) among {`ARM_RAW_TEXT` (text-alone), `ARM_FUSE_ZAVG`
  (per-query z-normalized average, fixes cross-modality scale mismatch), `ARM_FUSE_WTUNED`
  (w*text+(1-w)*ground, w tuned on train-eval over a 0..1 grid)}. Naive 1:1 `ARM_FUSED_EQ` retained as a
  DILUTION CONTROL. Selection + w* are computed on TRAIN concepts only, applied to held-out -> leak-proof.
  CREDIT/precedent: `grounding_gated_fusion_relation_inference_mammal_v1` = HARD_PASS_GATED_FUSION_RECOVERS_
  GROUNDING (KB cosine 0.363) established that naive 1:1 fusion dilutes and a gated/learned mix recovers grounding.
- GAP-2 RELATIONAL HEADROOM: relational eval now also computes `ARM_RAW_TEXT` (text-alone) + `ARM_FUSE_ZAVG`
  + `ARM_FUSE_WTUNED` (v1 had only raw vs fused there). Reports text-alone vs grounding on the leak-proof
  relational bar = THE headroom number.
- GAP-3 SAVE CHECKPOINT: after training each seed, persist `ckpt_seed_<seed>.pt` (encoder weights + tokenizer
  + config) AND `evalreps_seed_<seed>.npz` (text/random/grounding reps + split + graph). `--eval-only` re-runs
  ALL arms from the .npz in minutes (verified in smoke) so future fusion iterations need no retrain.
- SCALE: FULL config kept IDENTICAL to v1 (one variable = the eval-side fix) so the clean win is a faithful
  reproduction of the measured +0.039, not confounded by a scale change. A scale-push (more steps/tokens) is
  a trivial deferrable follow-up (report the scale delta separately), NOT bundled here.

## Arms (per-query AUC; base 0.5) -- SEMANTIC and RELATIONAL
RAW_GROUNDING [ceiling to beat] | RAW_TEXT [text-at-scale] | FUSED_EQ [naive 1:1 -> dilution control] |
FUSE_ZAVG | FUSE_WTUNED | FUSE_SELECTED [PRIMARY = best-honest, train-selected] | RANDOM_INIT [isolate
learning] | COLLAPSE_SHUFFLE [can-fail/leak witness] | POPULARITY [validity].

## Pre-registered bands (SEMANTIC held-out-NEW same-lexname per-query AUC is THE one number)
- HARD_PASS_CLEAN_WIN: PRIMARY (`ARM_FUSE_SELECTED`) - RAW_GROUNDING >= 0.03 AND per-seed min margin > 0
  AND RAW_TEXT > RANDOM_INIT (learning is real), with VALIDITY holding. (text-alone alone already gives
  +0.0388 both seeds in v1 -> a candidate for the selected primary -> this band is expected reachable.)
- HARD_FAIL_DATASCALE_REFUTED: on WELL-COVERED subset (>=100 mentions) PRIMARY - RAW_GROUNDING <= 0 at scale.
- MIDDLE_BAND_TIE_NULL: |PRIMARY - RAW_GROUNDING| < 0.03.
- HARD_FAIL_INVALID: validity fails.
- VALIDITY (required): COLLAPSE_SHUFFLE in [0.44,0.56], POPULARITY in [0.44,0.56], RAW_GROUNDING >= 0.55,
  min held-out query power >= 120.
- HEADROOM (reported, not a gate): RELATIONAL RAW_TEXT - RAW_GROUNDING (does text-at-scale beat grounding
  on the leak-proof relational bar too?).

## Discriminator-must-survive-scale (option B: analytical + MEASURED at full scale)
The discriminator (learned text-at-scale > grounding) is ALREADY MEASURED at full scale in v1: text-alone
0.6356 > grounding 0.5968, both seeds (per-seed min margin +0.0372). It is near-chance at smoke/selftest
(undertrained model on a data-starved slice) BY DESIGN = the can-fail floor. v2 training is byte-for-byte
the v1 config, so the measured +0.039 is the expected FULL result; the only change is that it is now
reported as the PRIMARY. SMOKE PROVES: pipeline runs, leak-gate fires (witness 0), all 9 arms compute +
differ, fusion model-selection + w* wired, checkpoint saves + reloads, controls near chance.
Self-test MEASURED (selftest scale, undertrained -- floor as expected): raw=0.6068 text=0.4565
feq=0.6005 zavg=0.5482 wtuned=0.6053 primary(WTUNED,w*=0.10)=0.6053 collapse=0.5143 pop=0.4923
rel_raw=0.5592 rel_text=0.4754 n_query=52 witness=0. SELF-TEST PASS.

## Leak-proofness (unchanged from v1 + selection leak-audit)
- Concept-level held-out split, sha256-ranked, freq-stratified (PYTHONHASHSEED-free).
- Every held-out concept's mentioning lines (exact + light inflections) SCRUBBED from BPE + MLM stream +
  train postings. BPE trained on TRAIN text only. VERIFIED-ZERO-OVERLAP GATE halts on any breach (witness must be 0).
- Relational target edge is NEVER an input to any rep (reps = grounding + text only) => relational bar leak-proof.
- NEW: fusion model-selection + weight-tuning use TRAIN-eval concepts ONLY; the selected arm + w* are then
  applied to held-out (standard inductive model-selection, no held-out label touched for selection).

## SCHEMA-VET declarations
- cardinality_ok: EXPECTED_N_UNITS = n_seeds (2 for FULL); verdict checks len(per_seed)==n_seeds.
- final_metrics_atomicity: tmp_replace (write_metrics os.replace) + per-seed partials (write_partial).
- except-ordering: `except SystemExit: raise` before `except Exception` (no BaseException / no bare except). VERIFIED by grep gate.
- crlb_n/a: AUC discriminator base = 0.5 exactly; collapse + popularity + random-init witness the floor empirically.
- baseline_in_band: v1 FULL collapse 0.4964 / pop 0.4968 / raw 0.5968 (0.05 < baseline < 0.95). PASS.
- HP_SCOPE: HARD_PASS gates apply to ARM_FUSE_SELECTED (semantic PRIMARY) only; relational is a reported bar; FUSED_EQ is a control.
- arms_differ_verified: True (sha256 hash-test over RAW/TEXT/RANDOM base rep matrices; halts if bit-identical).
- calibration_check: default_ok_for_this_regime (AUC base 0.5 analytic; controls witness it).
- defensive_error_checking: passed_all_4_patterns (start_marker + CELL_CRASHED crash-diag + traceback + _heartbeat.jsonl per MLM log step + specific-exception classes). cell_chunked: false (per-seed partials + shared bundle; single cell).
- real_code_path: --self-test constructs the REAL objects (load_concept_universe, count/collect/tokenize passes, build_bpe, mlm_train, encode, select_fusion_on_train, semantic+relational eval, checkpoint save + reload, zero-overlap gate) at tiny scale. SELF-TEST PASS.
- progress_logging: print_flush_true + _heartbeat.jsonl (timeout_s >> 1800). REQUIRED and present.
- test-design gates: no sweep axis (bracket/effective-param N/A); positive control = RAW_GROUNDING reproduced as the ceiling at the test regime; discriminator can-fail confirmed at smoke; FUSED_EQ dilution control present.

## HARD INVARIANTS
TEACHER-FREE. NO borrowed vectors anywhere (learned token embeddings + from-scratch Transformer; BPE vocab
built FROM ARC). INDUCTIVE (held-out placed from its own text + grounding; never a training target).
LEAK-PROOF (above). ASCII-only. Deterministic seeds. AI2 ARC Corpus = INTERNAL research use only.

## Remote dependencies (orchestrator: verify before launch -- SAME as v1, already staged)
- torch with CUDA on the GPU box (device-agnostic; AMP only when cuda).
- python package `tokenizers` (BPE trainer) in the remote venv.
- ARC corpus at `data/corpora/arc/ARC-V1-Feb2018-2/ARC_Corpus.txt` (staged for v1; unchanged).
- foundation `data/cskg_foundation_v1/` (nodes.jsonl + edges_shard_*.jsonl) staged (staged for v1; unchanged).
- NLTK WordNet (EVAL-only lexname truth); lexname cache regenerates if absent.

## Runtime + timeout
FULL config identical to v1 (max_lines=10M, train_token_budget=130M, vocab=16000, d512/6L/8H/seq128,
cap_mentions=128, heldout=800, mlm_steps=60000, 2 seeds). v1 FULL wall = 20363s (~5.65h) on RTX 4060 Ti.
v2 adds only checkpoint-save (seconds) + train-eval fusion selection (~30-60s/seed) + extra eval arms
(negligible). Est ~6h. Timeout 32400s (9h) generous.
