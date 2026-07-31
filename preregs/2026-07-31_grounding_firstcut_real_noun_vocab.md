# Pre-reg: grounding_firstcut_real_noun_vocab_v1 (GROUNDING FIRST-CUT -- vocab-expansion feasibility)

Cell: `experiments/exp_grounding_firstcut_real_noun_vocab_v1.py`
Anchor: `grounding_firstcut_real_noun_vocab_v1`
Author: exp_dev. Filed BEFORE the LITE run. Bands fixed before results.
Director spawn 2026-07-31 (GROUNDING first-cut, bounded measurement-first). Director+USER gated -- NOT the
full grounding program (no from-scratch re-pretrain, no wire/deploy).

## LOAD-BEARING DISK FINDING (corrects the spawn premise; MEASURED, not assumed)
The spawn framed the certified encoder as having a "CLOSED ~50-WORD VOCABULARY ... open-domain real text is
OOV-BLOCKED". VERIFIED ON DISK this is FALSE (the prior naturalistic-firstcut FAIRNESS FINDING conflated the
harness's 20-color TASK vocabulary with the ENCODER's training):
- `data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt` has
  MEASURED@ckpt.model_cfg = {vocab:16000, d_model:512, n_layers:6, max_len:128}, run_mode:full,
  anchor:scale_meaning_learn_arc_heldout_v2 = the AI2-ARC-corpus FULL run (~240M real tokens, byte-level BPE).
- MEASURED@ckpt.state_dict['tok_emb.weight']: all 16000 subword rows fully trained (norm median 18.89,
  std 0.60, ZERO rows with norm<0.01). Real nouns and colors are both near-orthogonal + differentiated
  (mean pairwise cos ~0.02-0.05). Byte-level BPE => ANY real text tokenizes with 0 <unk>.
So the encoder is ALREADY a real-vocab model. OOV-expansion + continue-pretrain is MOOT for reading real
nouns (all in-vocab, single-token, trained embeddings). CONSEQUENCE for this first-cut:
- (A) "does base reading work on the larger real vocab" is MEASURED DIRECTLY on the frozen encoder (no
  continue-pretrain needed); a continue-pretrain would only matter for REGISTER adaptation (ARC science text
  vs the templated harness register), and is a follow-up gated on (A) showing degradation -- NOT run here.
- The load-bearing feasibility variable becomes: does the CERTIFIED minimal-unfreeze entity fine-tune (atom
  29593) still TRANSFER when the harness ENTITIES/FILLERS are a FEW-HUNDRED REAL NOUNS (a genuine breadth
  expansion of the tight 20-color cluster), instead of the 20 colors? The certified arc ONLY ever tested the
  20-color cluster; real nouns are a broader, less mutually-contrastive set, and the frozen raw ENT-rep
  cross-frame separability is LOWER for real nouns than colors (MEASURED within-minus-cross 0.026 vs 0.083)
  => a genuinely harder, can-fail test with real headroom for the mechanism to close.

## The test (ONE variable = the harness symbol VOCABULARY: 20 colors [toy] vs a few-hundred real nouns [expanded])
Reuse VERBATIM: the certified v2 encoder + minimal-unfreeze (top-1 layer) fine-tune recipe (via
hc._finetune_weights depth=1) + the situation-model FHRR loop + pca_whiten conditioning + role_attn decode +
the loop-anchored corrected collapse guard (C1-C4) + the can-fail floors + POOLED_READER + MOST_RECENT. The
ONLY change = `install_vocab()` swaps the 20-color symbol vocabulary for N_NOUN single-token REAL NOUNS
(V_FILL grows to N_NOUN; FHRR codebooks resize; chance=1/N_NOUN). Everything downstream is byte-identical.

- (A) BASE READING on the larger real vocab: the tuned-noun ORACLE arm (perfect entity address; encoder reads
  the S/P real-noun filler) achieves acc well above chance => the encoder READS real-noun fillers; AND the
  frozen ENT reps differentiate real-noun entities (within-minus-cross > 0). If ORACLE craters near chance =>
  the encoder CANNOT handle the larger vocab (base reading fails) = a HARD-FAIL signal.
- (B) TRANSFER of the certified entity fine-tune on the real-noun harness: frozen vs certified minimal-unfreeze
  held-out loop (cross-frame entity re-id), guard, floors, generalization.

## Arms (all share identical real-noun held-out eval passages; the ONLY inter-arm difference = encoder weights)
- FROZEN_NOUN : frozen ARC-trained v2 encoder on the real-noun harness (the wall / baseline).
- TUNED_NOUN  : the CERTIFIED minimal-unfreeze (top-1 layer) fine-tune, trained on real-noun TRAIN entities,
  the robustness arm gated for HARD_PASS.
- ORACLE_NOUN : perfect entity-address ceiling (tuned-noun encoder reads S/P filler) = headroom + base-reading(A).
- TRAIN_NOUN  : tuned-noun on TRAIN-entity passages = memorization control (train-minus-held loop).
- COLOR_ANCHOR (positive control, Gate D): restore the 20-color vocab; reproduce the certified frozen->tuned
  lift => proves the harness wiring + recipe are faithful at the matched (color) regime.
- CAN-FAIL floors (must COLLAPSE): random_addr, no_coref, wrongrole, shuffled, MOST_RECENT, POOLED_READER.

## Pre-registered bands (fixed BEFORE running; reuse the certified/harder-construction bar shape)
Gate on TUNED_NOUN (B) held-out; (A) is a gating sub-result (base reading must work + oracle headroom exists).
Let chance = 1/N_NOUN. Loop = mean held-out acc over the 3 query types.
- HARD_PASS (mechanism SURVIVES vocab expansion => grounding direction feasible, scale it):
  (A) BASE_READING_OK: oracle_noun_loop - chance >= BASE_READING_MARGIN (0.20) AND frozen within-minus-cross
      > 0 (encoder reads + differentiates real-noun entities) AND
  (B) mean(tuned_noun_loop - frozen_noun_loop) >= LIFT_MIN (0.05) AND capture >= HEADROOM_CAPTURE_MIN (0.35)
      of (oracle_noun - frozen_noun) headroom AND every seed lifts (min per-seed lift > 0) AND collapse guard
      HOLDS [C1 tuned>=frozen; C2 wc_drift<=0.15; C3 entcons>=0.85; C4 q_agree>=0.55] AND memorization gap
      (train-minus-held) <= MEMORIZE_GAP_MAX (0.15) AND
  non-triviality: ALL floors collapse (< bar) AND POOLED_READER NOT reservoir-decodable (< PROVEN_MIN 0.80)
      AND MOST_RECENT fails (< DECODE_FLOOR_BAR).
- HARD_FAIL (mechanism BREAKS / vocab-fragile => rethink before big compute):
  mean(tuned_noun_loop - frozen_noun_loop) <= TIE_BAND (0.02) [ties frozen on real nouns = the win was
  color-cluster-specific] OR collapse (guard C1 fails with cratered tuned loop) OR base reading FAILS
  (oracle_noun_loop - chance < BASE_READING_MARGIN => the encoder cannot read the larger vocab given a clean
  address = a reading wall, not a mechanism win).
- MIDDLE: moved but did not clear HARD_PASS -- reported with per-seed trajectory + (A) sub-result.
- INVALID (fix construction before trusting; NOT a substrate verdict):
  a can-fail floor did NOT collapse, OR POOLED_READER reservoir-decodable, OR the harness is UNINFORMATIVE
  (oracle_noun - frozen_noun headroom < CONSTRUCTION_HEADROOM_MIN 0.05 -> nothing to capture), OR the
  COLOR_ANCHOR positive control does NOT reproduce a lift (recipe/wiring broken).

### Number provenance
- v2 ckpt is ARC-FULL real-vocab (16000 BPE / 240M tokens): MEASURED@data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt:model_cfg + state_dict.tok_emb.weight norms
- frozen raw ENT within-minus-cross real-noun 0.026 vs color 0.083: MEASURED@this-session probe (raw pre-conditioning reps, templated register)
- certified color break frozen->tuned loop 0.52->0.83 via cross-frame entity re-id: CITED@atom seq 29593 (cert_ledger 2026-07-31) MEASURED@data/exp_situation_model_assembly_encoder_retrain_scale_v1/metrics.json
- LIFT_MIN 0.05 / HEADROOM_CAPTURE_MIN 0.35 / TIE_BAND 0.02 / guard C1-C4 / MEMORIZE_GAP_MAX 0.15:
  HYPOTHESIZED@this prereg (reuse the certified corrected-guard shape; hc.LIFT_MIN etc VERBATIM)
- BASE_READING_MARGIN 0.20 (oracle above chance): HYPOTHESIZED@this prereg (a clean-address filler read must
  clear chance by a wide margin if base reading works; the color oracle sat ~0.62-0.85 = far above chance)

## SCHEMA-VET fields
- cardinality_ok: true. EXPECTED_N_UNITS = n_seeds (2 LITE). per-seed units.jsonl; verdict counts len(units).
- arms_differ_verified: true (FROZEN_NOUN vs TUNED_NOUN loop-digest OR q_agree OR encoder-geometry delta;
  an inert fine-tune would move NONE). arms_differ_exempted: none.
- final_metrics_atomicity: tmp_replace (os.replace) + per-seed units.jsonl (resumable per CLAUDE.md).
- except SystemExit: raise BEFORE except Exception (grep-clean; no bare except / BaseException).
- crlb_n/a: the SCORING loop is the zero-learned-param FHRR SituationWM (imported VERBATIM) + pca_whiten +
  role_attn decode; the ONLY learned params are the encoder top-1 layer (certified standout). Discriminator =
  held-out per-type loop (frozen vs tuned) + q_agree + entity_consistency + loop-anchored guard on the
  real-noun harness. Chance = 1/N_NOUN.
- discriminator_reachability: true. frozen real-noun loop is a wall (raw separability degraded vs colors);
  oracle shows headroom; the certified fine-tune has a real gap to close. Baseline NOT saturated.
- baseline_in_band: frozen_noun loop above chance but below oracle (measured at smoke); ORACLE ceiling; the
  6 floors + POOLED + MOST_RECENT are can-fail controls that MUST collapse.
- calibration_check: default_ok_for_this_regime (reuses the certified conditioner + guard verbatim; floors
  recompute at the new chance -- floor bars kept at the imported conservative 0.20/0.287 which strictly
  EXCEED the new tiny chance, so the floor-collapse gate stays valid/conservative).
- cell_chunked: false (2 seeds in-cell, per-seed write_partial/resume). start_marker_written /
  crash_diagnostic_present / heartbeat_present: true (heartbeat via per-seed logs; runs << 1800s/call).
- defensive_error_checking: passed_all_4_patterns.
- progress_logging: print_flush_true (line-buffered stdout + per-seed/arm flush prints).

## §15 composition/sweep gates
- sweep_alignment_verdict: ALIGNED. The ONE variable is the symbol vocabulary (20 colors vs N_NOUN real
  nouns); V_FILL, codebooks, chance, and the held/train split all scale consistently with it (patched across
  all 6 modules + asserted in self-test). No nominal/effective mismatch.
- discriminating_fraction: n/a-sweep. Smoke confirms the discriminator fires (floors collapse; frozen<oracle
  headroom present; base reading above chance; arms differ).
- composition_edges: rendered real-noun text -> frozen/tuned v2 encoder token reps -> pca_whiten -> role_attn
  ENT/S/P decode -> FHRR bind/unbind SituationWM (content-gated overwrite + competitive coref) -> filler
  cleanup vs V_FILL codebook -> per-type loop acc. SHAPE_MATCH at each edge (identical to the certified cell
  except V_FILL is larger; codebooks are generated at build_tables from V_FILL).
- positive_control_arms: COLOR_ANCHOR reproduces the certified frozen->tuned color lift at the matched regime
  (Gate D: reproduce prior chain-grade result AT test regime, tolerance -- lift must be positive). If the
  color anchor does NOT lift, the harness/recipe wiring is broken => INVALID (do not trust the noun arms).
- functional_requirements: (1) read real-noun fillers/entities on the larger vocab [ORACLE + separability, A];
  (2) cross-frame entity re-id lift via the certified fine-tune on real nouns [TUNED_NOUN vs FROZEN_NOUN, B];
  (3) prove the harness non-trivial [floors + POOLED + MOST_RECENT collapse]; (4) generalize to held-out
  real-noun entities [held/train disjoint split + mem gap]; (5) reproduce the certified color lift [Gate D].

## Compute architecture
- class (c) mixed with justification: top-1-layer SGD fine-tune (batched fwd+bwd, CPU) + closed-form FHRR
  eval loop with batched frozen-encoder forwards. Pure CPU (encoder d512/6L; V_FILL<=120). No GPU needed
  (the encoder is already trained; only a top-1-layer fine-tune runs, ~seconds-minutes CPU). Continue-pretrain
  (the only GPU-heavy path) is NOT run -- disk finding shows it is unnecessary for reading real nouns.
- storage strategy: SHARDED per-entity content-gated overwrite memory + FHRR-superposed roles (inherited).
- Smoke: N_NOUN=24, 1 seed, 24 steps, eval_n=20 (proves: patch works at non-20 V_FILL; base reading; floors
  collapse; arms differ; drift guard; non-triviality). LITE: N_NOUN=120, 2 seeds, 220 steps, eval_n=60,
  resumable per seed (budget-sec keeps each foreground call < 10 min).
