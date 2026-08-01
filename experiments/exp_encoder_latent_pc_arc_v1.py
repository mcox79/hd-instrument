"""Encoder-level LATENT PREDICTIVE CODING (JEPA-style) pretraining on ARC -- rep-quality lever #1.

WHY (notes/encoder_representation_lever_ranking_2026-07-29.md lever #1;
     notes/brain_foundational_component_analysis.md components 1+2):
  The founding-diagnosis objective gap: every prior encoder objective aligned to a STATIC target
  (MLM = bidirectional reconstruction of a masked token against a fixed vocab). The brain's cortex
  is FORWARD/latent-PREDICTIVE (Rao&Ballard 1999; Friston 2005). This cell builds the ENCODER-LEVEL,
  STANDALONE version of that fix (I-JEPA/V-JEPA, Assran 2023 / Bardes 2024; LeCun 2022): mask target
  SPANS and predict the TARGET-span LATENT from the CONTEXT latent via a predictor head, entirely in
  d-dim latent space -- NO token/pixel reconstruction, NO full-vocab logits. This is categorically
  OOM-free (no [B,L,vocab] tensor ANYWHERE), avoiding the v5 causal-LM OOM class.

  This is DISTINCT from the WM-coupled forward-predictive objective
  (notes/forward_predictive_objective_from_wm_state_design_2026-07-29.md): that predicts the next
  CLAUSE latent from a maintained SLOT STATE and is judged on the WM gate (MES/KD). THIS cell has
  NO working-memory module, NO slot state -- it is judged PURELY on representation quality (section 3
  of the ranking note), on a FROZEN encoder snapshot, so the two workstreams never confound.

WHAT (the run): five encoder arms (2026-07-30: added ARM_LPC_CAUSAL, renamed ARM_LPC->ARM_LPC_BIDIR),
  MATCHED training budget (same tokens/steps/architecture), each frozen and scored on the SAME
  independent rep-quality battery:
    ARM_LPC_CAUSAL : causal next-latent prediction (lower-triangular mask) + hold-then-revise role gate
                  (diagnostic) + clause-level hierarchy head -- PRIMARY, 2026-07-30 amendment.
    ARM_LPC_BIDIR : latent-PC (JEPA), UNCHANGED bidirectional masked-span -- CONTROL (was ARM_LPC).
                  EMA/stop-grad target encoder (SimSiam-style) + VICReg variance-floor + covariance/
                  decorrelation term (collapse guard, REQUIRED per lit).
    ARM_LPC_TC  : ARM_LPC_BIDIR + temporal-contiguity aux loss (Foldiak slow-feature). Wires the
                  ALREADY BANKED hdlab/temporal_trace.py primitive as a one-variable ABLATION arm.
    ARM_MLM     : the CURRENT MLM v2 encoder (imported from exp_scale_meaning_learn_arc_heldout_v2),
                  same architecture/steps/tokens -> the known-good reference (29591 baseline).
    ARM_RANDOM  : random-init encoder (same architecture, untrained) -> the floor.

REP-QUALITY BATTERY (frozen encoder; KB used READ-ONLY as a probe, NEVER a training target ->
  this is the exact distinction from the failed relObj contrastive-align-to-KB objective):
    1. graded_geometry_spearman : Spearman(encoder cosine, KB graded proximity {1-hop/2-hop/far})
                                  over held-out-NEW concepts. THE HEADLINE metric.
    2. heldout_probe_acc        : frozen closed-form ridge linear probe (lexname supersense) trained
                                  on TRAIN concepts, tested on held-out-NEW -> generalization, head
                                  can't cheat (linear, frozen).
    3. relational_auc           : per-query neighborhood AUC (reuses v2.relational_eval) -- leak-proof.
    4. rep_dispersion + collapse: per-dim concept-rep std + mean pairwise cosine (collapse witness)
                                  + training-time min target-embedding std (VICReg guard telemetry).

THE PRE-REGISTERED BANDS (deflated per lit-scan calibration; section 3 of the ranking note; this is
  the REP-QUALITY bonus criterion inherited from the prior lever -- the DECISIVE causal-encoder claim
  is the SEPARATE syntax-role cross-voice probe cell, see CAUSAL-ENCODER AMENDMENT note below):
  HARD_PASS  = ARM_LPC_CAUSAL graded_geometry beats ARM_MLM by >= +0.10 AND beats ARM_RANDOM by >= +0.15,
               in >= 1 of 2 seeds with the OTHER seed non-negative, AND held-out probe does NOT
               regress (>= MLM - 0.01), AND NO collapse (rep_std + target_std above floors).
  HARD_FAIL_NO_EFFECT = ARM_LPC_CAUSAL ties BOTH ARM_MLM and ARM_RANDOM within +/-0.03 on graded_geometry.
  FAIL_BY_COLLAPSE    = geometry metrics move but variance collapses (rep_std < floor OR training
                        target_std < floor) -> distinct diagnosis (mechanism class NOT refuted).
  MIDDLE_BAND         = anything else (real-but-below-band gain).
  ARM_LPC_TC is reported as an ABLATION (does temporal-contiguity add over bidirectional-LPC alone?);
  ARM_LPC_CAUSAL vs ARM_LPC_BIDIR (causal_vs_bidir_delta) is reported as a SECOND ablation (does the
  causal-mask amendment beat its own bidirectional control?). Both UNGATED (reported, not HP/FAIL gated).

CAPACITY-RATIO WATCH (SimSiam small-scale sensitivity finding, SCAN 1): collapse risk is
  capacity/data-ratio dependent, not simply "small data fails". FULL uses d_model=512 over ~130M
  tokens; a co-scaled SMALLER variant (--co-scaled: d_model=256, n_layers=4) is pre-registered as an
  optional follow-up if FULL shows collapse or over-capacity. The training-time target_std telemetry
  is the early-warning signal.

HARD INVARIANTS (project locks): TEACHER-FREE. NO GloVe/BGE/transformer WEIGHTS/borrowed vector
  ANYWHERE (token emb + Transformer learned FROM SCRATCH; BPE vocab built FROM ARC -- all inherited
  from the imported v2 pipeline). INDUCTIVE + LEAK-PROOF (held-out placed from its own text; KB read
  only as a diagnostic probe, never a training target; v2's concept-level scrub + zero-overlap witness
  reused verbatim). ASCII-only. AI2 ARC Corpus: INTERNAL research use only.

CUDA-DEVICE-SAFE (recurring bug class this session: WM.to(device) then cpu-Generator-used-with-cuda):
  every module (online/target/predictor) .to(device); EVERY torch.rand/randint/randperm/arange on the
  RUN device (from ids.device); NO torch.Generator in the hot path (numpy default_rng only for host-side
  window-index selection into a numpy array, then .to(device)); the ONLY host<->device crossing is the
  temporal_trace numpy primitive, done via explicit .detach().cpu().numpy() out and torch.from_numpy().to(device)
  back. A tiny end-to-end cuda sanity runs in --self-test WHEN cuda is present; when absent the identical
  device-routed step runs on cpu and a static device-parity audit is recorded (see _cuda_safety_audit).

BUILD-PLAN FIXES 2026-07-30 (notes/forward_predictive_second_encoder_build_plan_2026-07-30.md sec 2):
  Fix A  data-prep progress logging inside count/collect/tokenize passes (in v2, imported) -- every
         500k lines log n_read/rate/ETA + _heartbeat.jsonl (silent->visibly-alive).
  Fix B  (single-pass merge) NOT APPLIED -- FLAGGED. The pipeline is count_pass -> build_split ->
         collect_pass: collect's held/train line routing needs the SPLIT, which needs the full COUNTS.
         A correctness-preserving merge would need to buffer >cap_mentions postings for ALL concepts
         (unbounded memory at FULL) to survive post-hoc split routing; the cap-in-corpus-order posting
         semantics cannot be reproduced from a pre-split single pass. The actual failure (silent 5h
         death) is fully addressed by Fix A (visibility) + Fix D (cache: crash never repeats data-prep)
         + Fix C (headroom gate detects a too-slow env before FULL). Kept 3 correct passes.
  Fix C  --smoke data-prep-headroom gate: measure REAL lines/sec on a 2M-line slice, project to FULL,
         REFUSE FULL if projected > DATA_PREP_TIME_CEILING_S (4h). Prints DATA_PREP_OK|DATA_PREP_TOO_SLOW.
  Fix D  torch.save the prepare_data() bundle keyed by a sha256 digest of (data-cfg subset, corpus
         mtime); main() reuses it before re-running data-prep.
  Fix 2b OOM tripwire: _assert_no_vocab_dim on the loss-path latents (last-dim==d_model, != vocab).
  Fix 2c (seed, arm) checkpoint/resume via tools/exp_checkpoint.py (crash keeps completed arms' GPU-hrs).
  Fix 2d per-arm reusable ckpt (state_dict+model_cfg+tokenizer_json) = FrozenV2Encoder-shape, for sec 3.
  Fix 4  ARM_MLM reuses V2 ckpt_seed_{7,13}.pt at FULL (no retrain); FULL mlm_steps bumped 40000->60000
         to MATCH V2 FULL so the reused MLM arm and the fresh LPC arms share the step budget (flagged).

CAUSAL-ENCODER AMENDMENT 2026-07-30 (notes/brain_syntax_to_role_mechanism_and_forward_predictive_
  encoder_spec_2026-07-30.md Part 2; answers the measured wall in exp_syntactic_role_agent_patient_
  voice_probe_v1, 74d4ea0c1: frozen MLM cross-voice agent/patient probe = 0.18/0.16, INVERTS on
  passives). ONE axis changed (masked-bidirectional -> causal next-latent prediction) + two small NEW
  components, everything else above (VICReg guards, EMA/stop-grad, OOM-tripwire, Fix A/C/D/2b/2c/2d)
  carried forward VERBATIM:
  (a) CAUSAL objective: NEW arm ARM_LPC_CAUSAL trains with a lower-triangular attention mask (see
      `_causal_contextual`, a local wrapper around the SAME TinyTransformer -- no change to the
      imported v2 class, so ARM_MLM/ARM_RANDOM and every other v2 consumer is unaffected) + a
      left-truncated span rule (target span start >= 1, so there is always >=1 token of real left
      context; the SAME masked-span mechanism as before, just no longer allowed to start at t=0).
      The renamed ARM_LPC_BIDIR is the UNCHANGED prior bidirectional arm, kept as the causal-vs-
      bidirectional control (spec anchor-candidate #2).
  (b) HOLD-THEN-REVISE gate: `hold_then_revise_gate` + `role_hypothesis_pass` reuse the EXACT PBWM
      bistable-write math from hdlab/slot_attention_wm.py (`boundary = sigmoid((surprise-theta)/tau)`,
      REPLACE not blend at low tau) at token-to-clause granularity on the causal arm's own latents
      (diagnostic pass, logged as role_gate_mean_replace_rate; not wired into the training loss --
      the gate's job per the spec is role-state tracking, not an additional loss term).
  (c) HIERARCHY: `ClausePredictor` (d_model->d_model, same shape/pattern as `LatentPredictor`) adds a
      second smooth-L1+VICReg loss term on the causal arm only, predicting the NEXT WINDOW's pooled
      latent (EMA target, stop-grad) from the current window's last-valid-position causal latent.
      FLAG (spec-vs-code discrepancy, honest per META_RULE_AC): the spec's own text says this head
      "reuses the ForwardPredictor already designed in forward_predictive_objective_from_wm_state_
      design_2026-07-29.md section 2" -- grepped, no such importable class exists anywhere in the repo
      (design-note only). Built fresh at the same architecture PATTERN the spec mandates (d_model->
      d_model MLP + smooth-L1/VICReg, OOM-immune). "Next clause" is PROXIED as "next training window
      in corpus order" (no clause/sentence-boundary segmenter exists in this pipeline) -- this is a
      HYPOTHESIZED proxy for clause-adjacency, not a literal linguistic clause boundary; flagged, not
      oversold.
  (d) Glass-box: no change -- same TinyTransformer, same from-scratch tokenizer/BPE, gate operates on
      the encoder's own latents (no bolt-on parser).
  --lite REPURPOSED (2026-07-30, per Director's explicit spec; 2026-08-01 EXTENDED): trains
  ARM_LPC_CAUSAL + ARM_LPC_BIDIR + ARM_RANDOM at ONE seed, ~10x fewer steps, SAME architecture as FULL
  -> ckpt_seed_7_{ARM_LPC_CAUSAL,ARM_LPC_BIDIR,ARM_RANDOM}.pt, bundling the causal-vs-bidirectional-vs-
  random small-proxy comparison the cross-voice role probe needs (spec anchor #2). ARM_LPC_CAUSAL was
  already trained 2026-07-30 (LITE_COLLAPSE, rep_std marginally under floor); (seed,arm) checkpoint
  resume (Fix 2c) means this run only trains the two NEW arms. ARM_MLM intentionally excluded (the
  probe's own default V2_CKPT already IS the measured MLM reference, zero extra GPU cost). FLAG
  (breaking change, low risk, carried from 2026-07-30): this REPLACES the prior --lite semantics
  (which trained ARM_LPC[now ARM_LPC_BIDIR]+ARM_MLM+ARM_RANDOM for
  exp_context_invariance_lpc_lite_probe_v1.py) -- that OTHER probe cell's contract with --lite does not
  hold if invoked after this change.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at run (META_RULE_AF; hash of the 5 arms' held-out rep matrices)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace + per-seed partials)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: this is a representation-geometry comparison (Spearman/probe-acc), not a noise-floor
#     estimator; discriminator floor witnessed empirically by ARM_RANDOM (~chance geometry) + no-effect band
# - baseline_in_band at run: ARM_MLM graded_geometry in (0.05,0.95) (cited 0.56-0.63); ARM_RANDOM near floor
# - discriminator survives scale: analytical (objective gap is architectural; battery NOT saturated -- MLM
#     ~0.56-0.63 leaves >0.10 headroom, RANDOM near 0 gives >0.15 headroom) + smoke previews arm ordering
# - HARD_PASS strictly above floor: >= +0.10 over MLM AND >= +0.15 over RANDOM (both well above no-effect 0.03)
# - HP_SCOPE: HP gates apply to ARM_LPC_CAUSAL (primary, 2026-07-30). ARM_LPC_BIDIR = control
#     (unchanged bidirectional cell), ARM_LPC_TC = ablation (both reported, not gated for HP).
#     ARM_MLM/ARM_RANDOM = reference/floor (NOT gated).
# - no sweep axis -> cardinality_ok via EXPECTED_N_UNITS = n_seeds
# - per-unit failure-class instrumentation (no bare except; specific classes -> metrics)
# - calibration_check: default_ok_for_this_regime (VICReg gamma=1.0 std floor + off-diag cov are the
#     literature-standard defaults; collapse telemetry logged so the guard is observable, not assumed)
# - deterministic seeding: fixed int seeds + numpy default_rng(seed+k) + torch.manual_seed(seed); no hash()/list(set())
# - real_code_path: --self-test constructs the REAL objects (v2 BPE build + prepare_data + TinyTransformer +
#     lpc_train + mlm_train + full battery) at N~16 (SELFTEST_CFG IS the real pipeline at tiny scale)
# - progress_logging: print_flush_true (train step logs flush=True) + _heartbeat.jsonl (timeout_s >> 1800)
# - device-agnostic: cuda+AMP on the GPU box, cpu for local self-test; no hard device assumption
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, record_gate, write_metrics, write_partial, aggregate_partials,
)
# Reuse the PROVEN v2 data pipeline + encoder + MLM baseline verbatim (guarantees matched data /
# architecture across arms; the ONLY new machinery here is the LPC objective + the rep battery).
from experiments.exp_scale_meaning_learn_arc_heldout_v2 import (  # noqa: E402
    TinyTransformer, mlm_train, load_concept_universe, prepare_data, count_pass,
    encode_concept_text_reps, relational_eval, ARC_CORPUS,
    FULL_CFG as V2_FULL_CFG,  # noqa: F401  (to audit MLM-reuse budget parity)
    RAW_ARM as V2_RAW_ARM,  # noqa: F401  (imported to assert module wiring in self-test)
)
from hdlab.temporal_trace import TemporalTrace  # noqa: E402  (banked Foldiak slow-feature primitive)

# (seed, arm) per-unit checkpoint/resume (CLAUDE.md mandate; Fix 2c). Same path convention every cell
# uses: tools/ on sys.path, then `import exp_checkpoint`.
sys.path.insert(0, os.path.join(_REPO, "tools"))
import exp_checkpoint as ckpt  # noqa: E402

ANCHOR_NAME = "encoder_latent_pc_arc_v1"

# Reuse of V2's already-trained MLM checkpoints for ARM_MLM at FULL (section 4 cost fix; Fix 4): the
# MLM baseline arm is architecturally + data + BUDGET identical to V2's FULL MLM (see FULL_CFG note
# below), so we load V2's ckpt_seed_{7,13}.pt instead of retraining ~2 GPU-hr/seed. Graceful fallback
# to a fresh matched-budget MLM train when a seed's ckpt is absent (smoke/self-test/other seeds).
V2_CKPT_DIR = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v2")

# Data-prep-headroom smoke gate (Fix C) + resumable data-prep cache (Fix D).
DATA_PREP_SMOKE_LINES = 2_000_000        # real-corpus probe slice (measure lines/sec, extrapolate)
DATA_PREP_TIME_CEILING_S = 14400         # 4h ceiling on projected FULL data-prep (fail loud above)
N_DATA_PASSES = 3                        # count_pass + collect_pass + tokenize_train_stream (see Fix B flag)
_DATA_CFG_KEYS = ("min_deg", "cap_eval_concepts", "heldout_count", "min_mentions_eval", "max_lines",
                  "dedup_cap", "bpe_sample_lines", "cap_mentions", "vocab", "max_len",
                  "train_token_budget", "max_shards", "n_freq_buckets")

# Arms
ARM_LPC_CAUSAL = "ARM_LPC_CAUSAL"  # causal next-latent prediction + hold-then-revise + clause head -- PRIMARY (2026-07-30)
ARM_LPC_BIDIR = "ARM_LPC_BIDIR"    # UNCHANGED prior bidirectional masked-span latent-PC -- CONTROL (was ARM_LPC)
ARM_LPC_TC = "ARM_LPC_TC"         # bidirectional latent-PC + temporal-contiguity -- ABLATION (unaffected by causal axis)
ARM_MLM = "ARM_MLM"               # current MLM baseline (matched budget) -- reference
ARM_RANDOM = "ARM_RANDOM"         # random-init -- floor
# OBJECTIVE PIVOT 2026-08-01 v2 (CORRECTED after the run-5 broken-test retraction). All causal arms run
# through causal_realtarget_train (one code path -> truly one-variable). AXIS 1 2x2:
# {target: sampled_softmax(EXTERNAL token identity) | ema_latent(self-distill control)} x {reg: barlow|vicreg}.
# PRIMARY = EXT+barlow. AXIS 2 = EXT+barlow+k-WTA (structural sparse anti-collapse).
ARM_CAUSAL_EXT_BARLOW = "ARM_CAUSAL_EXT_BARLOW"    # PRIMARY: external token-identity (sampled softmax) + Barlow
ARM_CAUSAL_EXT_VICREG = "ARM_CAUSAL_EXT_VICREG"    # regularizer axis (external target held, barlow->vicreg)
ARM_CAUSAL_EMA_BARLOW = "ARM_CAUSAL_EMA_BARLOW"    # target axis (barlow held, external->ema self-distill)
ARM_CAUSAL_EMA_VICREG = "ARM_CAUSAL_EMA_VICREG"    # 2x2 4th cell (old EMA+VICReg recipe, SAME function)
ARM_CAUSAL_EXT_BARLOW_TOPK = "ARM_CAUSAL_EXT_BARLOW_TOPK"  # AXIS 2: PRIMARY + k-WTA sparse-latent anti-collapse
NEW_OBJECTIVE_ARMS = [ARM_CAUSAL_EXT_BARLOW, ARM_CAUSAL_EXT_VICREG, ARM_CAUSAL_EMA_BARLOW,
                      ARM_CAUSAL_EMA_VICREG, ARM_CAUSAL_EXT_BARLOW_TOPK]
ARMS = [ARM_LPC_CAUSAL, ARM_LPC_BIDIR, ARM_LPC_TC, ARM_MLM, ARM_RANDOM]
OBJECTIVE_ARMS = [ARM_LPC_CAUSAL, ARM_LPC_BIDIR, ARM_LPC_TC] + NEW_OBJECTIVE_ARMS   # arms carrying training-time collapse telemetry
# --lite (2026-07-30 REPURPOSED per Director spec for the causal-encoder cross-voice role-probe early
# read; 2026-08-01 EXTENDED): trains ARM_LPC_CAUSAL + ARM_LPC_BIDIR at ONE seed, ~10x fewer steps, SAME
# architecture as FULL, plus ARM_RANDOM (untrained floor control, no training cost). ARM_LPC_CAUSAL was
# already trained+checkpointed 2026-07-30 (LITE_COLLAPSE verdict, rep_std marginally under floor); the
# (seed,arm) checkpoint/resume (Fix 2c) means this run resumes it and only trains the two NEW arms --
# matched-budget causal-vs-bidirectional-vs-random bundle for the syntax-role probe's fair test (spec
# anchor #2, "bundle a bidirectional-vs-causal control arm"). ARM_MLM intentionally excluded here: the
# probe's own default ckpt (V2_CKPT) already serves as the already-measured MLM reference (0.16-0.18
# inverted) at zero extra GPU cost. Supersedes the prior lite semantics (ARM_LPC[now
# ARM_LPC_BIDIR]+ARM_MLM+ARM_RANDOM, for exp_context_invariance_lpc_lite_probe_v1.py) -- see header FLAG.
# OBJECTIVE-PIVOT COLLAPSE TEST 2026-08-01 (USER-approved): the 3 NEW-objective causal arms (real+barlow
# PRIMARY, real+vicreg, ema+barlow) + the OLD ARM_LPC_CAUSAL (ema+vicreg) baseline reference, all trained
# fresh at the SAME cheap 6000-step budget where EMA+VICReg collapsed (rep_std 0.0128/0.0180 < 0.020) --
# the decisive question is whether the real-target+Barlow objective clears the 0.020 rep_std floor. BIDIR
# (0.0248) + RANDOM (0.0121) resume from existing ckpts (free controls). Voice-role probe is run for
# RECORD only -- the proxy-limit finding (bidir+random both 0.0/0.0) means downstream de-inversion does not
# emerge at lite budget for ANY arm, so the go-signal here is rep_std clearing the floor, not the probe.
LITE_ARMS = [ARM_CAUSAL_EXT_BARLOW, ARM_CAUSAL_EXT_VICREG, ARM_CAUSAL_EMA_BARLOW, ARM_CAUSAL_EMA_VICREG,
             ARM_CAUSAL_EXT_BARLOW_TOPK, ARM_LPC_BIDIR, ARM_RANDOM]

# Pre-reg bands (headline = graded_geometry_spearman; deflated per lit-scan calibration)
HP_GG_OVER_MLM = 0.10            # ARM_LPC - ARM_MLM graded-geometry (break the reference)
HP_GG_OVER_RANDOM = 0.15         # ARM_LPC - ARM_RANDOM (learning is real, not vacuous)
PROBE_NOREGRESS_EPS = 0.01       # held-out probe must not regress below MLM by more than this
NO_EFFECT_EPS = 0.03             # |LPC - MLM| and |LPC - RANDOM| both under this = FAIL_BY_NO_EFFECT
COLLAPSE_REP_STD_FLOOR = 0.02    # frozen concept-rep per-dim std floor (below = representational collapse)
COLLAPSE_TARGET_STD_FLOOR = 0.05  # training-time target-embedding std floor (VICReg guard must hold)
MIN_QUERY_TASKS = 40             # power floor for the geometry/probe evals to be trustworthy

# LPC / VICReg defaults (literature-standard; calibration_check=default_ok_for_this_regime)
# VICReg (Bardes 2022): variance hinge gamma=1.0, covariance off-diag decorrelation.
# EMA target momentum 0.996 (BYOL/I-JEPA range). Predictor = 2-layer MLP (I-JEPA predictor is small).

# ---------------------------------------------------------------------------
# Config profiles (mirror v2's keys so prepare_data works verbatim; add LPC keys)
# ---------------------------------------------------------------------------
_LPC_COMMON = dict(
    lpc_mask_frac=0.20, lpc_ema_m=0.996, lpc_var_coef=1.0, lpc_cov_coef=0.04,
    lpc_pred_hidden_mult=2, lpc_tc_coef=0.5, lpc_tc_alpha=0.1,
    # causal amendment 2026-07-30: hold-then-revise gate (theta/tau reused from
    # hdlab/slot_attention_wm.py SlotAttentionWM.write_theta / write_tau_end=0.1, near-bistable) +
    # clause-head loss coefficient (same weight class as lpc_tc_coef).
    role_gate_theta=0.5, role_gate_tau=0.1, lpc_clause_coef=0.5,
    # OBJECTIVE PIVOT 2026-08-01: Barlow off-diagonal decorrelation weight (Zbontar 2021 uses ~0.005).
    lpc_barlow_lambda_od=0.005,
    # OBJECTIVE PIVOT v2 2026-08-01: sampled-softmax negatives per position (InfoNCE) + k-WTA sparsity k.
    lpc_softmax_negatives=64, lpc_sparse_topk=64,
    # ANTI-COLLAPSE 2026-08-01 (Probe 2a de-risking; ONE-VARIABLE fix): the causal arm uniquely
    # collapsed at the shared lite budget -- MEASURED@data/exp_encoder_latent_pc_arc_v1_lite/metrics.json
    # (remote): ARM_LPC_CAUSAL rep_std=0.0128 (< 0.020 floor; barely above ARM_RANDOM 0.0121) with a
    # HEALTHY EMA target (min_target_std=0.966) = the textbook JEPA/BYOL/SimSiam ONLINE-encoder collapse
    # mode, while ARM_LPC_BIDIR trained clean (rep_std=0.0248) at IDENTICAL LR/warmup/budget/tokens.
    # Lever chosen (single knob, causal-only): DOUBLE the VICReg variance-term weight for the causal arm
    # (1.0 -> 2.0). Directly opposes the measured symptom (per-dim std too low); LR/warmup are
    # demonstrably adequate (bidir is clean at the same LR) so lowering LR would treat a non-cause and
    # slow useful learning; this is the literature-standard anti-collapse knob (Bardes VICReg 2022).
    # Causal-only so the causal-vs-bidir contrast stays one-variable-clean AND so a resumed BIDIR/RANDOM
    # (from ckpt) is untouched. NOT in _DATA_CFG_KEYS -> data-prep bundle cache key unchanged (cache HIT).
    lpc_var_coef_causal=2.0,
)

SELFTEST_CFG = dict(
    run_mode="selftest", seeds=[7],
    min_deg=2, cap_eval_concepts=1500, heldout_count=60, min_mentions_eval=1,
    max_lines=120000, dedup_cap=160000, bpe_sample_lines=40000, cap_mentions=6,
    vocab=512, max_len=24, train_token_budget=600000, max_shards=6,
    d_model=32, n_layers=1, n_heads=2, ffn_mult=2,
    mlm_steps=40, mlm_batch=8, mlm_mask_frac=0.15, mlm_lr=3e-3,
    encode_batch=64, n_freq_buckets=4,
    **_LPC_COMMON,
)
SMOKE_CFG = dict(
    run_mode="smoke", seeds=[7],
    min_deg=2, cap_eval_concepts=2500, heldout_count=250, min_mentions_eval=2,
    max_lines=150000, dedup_cap=200000, bpe_sample_lines=80000, cap_mentions=16,
    vocab=4096, max_len=48, train_token_budget=4000000, max_shards=6,
    d_model=128, n_layers=2, n_heads=4, ffn_mult=2,
    mlm_steps=400, mlm_batch=64, mlm_mask_frac=0.15, mlm_lr=3e-3,
    encode_batch=256, n_freq_buckets=5,
    **_LPC_COMMON,
)
FULL_CFG = dict(
    run_mode="full", seeds=[7, 13],
    min_deg=2, cap_eval_concepts=None, heldout_count=800, min_mentions_eval=20,
    max_lines=10000000, dedup_cap=6000000, bpe_sample_lines=400000, cap_mentions=128,
    vocab=16000, max_len=128, train_token_budget=130000000, max_shards=16,
    d_model=512, n_layers=6, n_heads=8, ffn_mult=4,
    # mlm_steps=60000 MATCHES V2 FULL (exp_scale_meaning_learn_arc_heldout_v2.FULL_CFG.mlm_steps=60000).
    # This is the ONE scientific-parameter change vs the cell's prior 40000, made so ARM_MLM (now REUSED
    # from V2's 60000-step ckpt, Fix 4) and the fresh-trained ARM_LPC/ARM_LPC_TC share an IDENTICAL step
    # budget -> the one-variable (objective) comparison stays budget-matched. Flagged for Director
    # sign-off. A runtime parity assert (see _load_mlm_baseline_encoder use) guards against silent drift.
    mlm_steps=60000, mlm_batch=128, mlm_mask_frac=0.15, mlm_lr=3e-4,
    encode_batch=256, n_freq_buckets=8,
    **_LPC_COMMON,
)
# Co-scaled follow-up variant (capacity-ratio watch): smaller encoder over the same ~130M tokens.
FULL_COSCALED_OVERRIDE = dict(d_model=256, n_layers=4, n_heads=8, ffn_mult=4)

# LITE early-signal config (2026-07-30 REPURPOSED for the causal-encoder cross-voice role-probe early
# read; supersedes the prior ARM_LPC+ARM_MLM+ARM_RANDOM lite -- see header FLAG). The FULL GPU run
# (this same file, no --lite) trains for ~15-19h; this config buys an EARLY directional read on the
# causal-encoder question WITHOUT waiting for it. SAME ARCHITECTURE as FULL (d_model/n_layers/n_heads/
# ffn_mult/vocab/max_len UNCHANGED -- representativeness: an early signal from a smaller/shallower net
# would not transfer) but ~10x fewer steps (6000 vs 60000) and a much smaller data subset (faster
# data-prep + faster/seed). Trains ARM_LPC_CAUSAL + ARM_LPC_BIDIR + ARM_RANDOM (LITE_ARMS, 2026-08-01
# extended), ONE seed (7) -- saves ckpt_seed_7_{ARM_LPC_CAUSAL,ARM_LPC_BIDIR,ARM_RANDOM}.pt for the
# syntax-role probe's path-swap early read (causal-vs-bidir-vs-random bundle).
LITE_CFG = dict(
    run_mode="lite", seeds=[7],
    min_deg=2, cap_eval_concepts=3000, heldout_count=150, min_mentions_eval=5,
    max_lines=1200000, dedup_cap=900000, bpe_sample_lines=150000, cap_mentions=32,
    vocab=16000, max_len=128, train_token_budget=9000000, max_shards=10,
    d_model=512, n_layers=6, n_heads=8, ffn_mult=4,          # SAME architecture as FULL_CFG
    mlm_steps=6000, mlm_batch=64, mlm_mask_frac=0.15, mlm_lr=3e-4,
    encode_batch=256, n_freq_buckets=8,
    **_LPC_COMMON,   # RESTORED 2026-08-01 (iter-3 edit accidentally dropped this spread -> KeyError
                     # lpc_pred_hidden_mult crash on remote run-3; the shared LPC/VICReg/gate keys MUST
                     # be present in LITE_CFG exactly as in SELFTEST/SMOKE/FULL).
    # MINIMAL BUDGET BUMP 2026-08-01 iter-3 (LITE-ONLY, CAUSAL-ONLY): var_coef=2.0 alone moved the causal
    # arm rep_std 0.0128->0.0180 (monotone better) but STILL marginally under the 0.020 collapse floor
    # (MEASURED@remote run-2). One-variable lever = 2x optimizer steps for the CAUSAL arm ONLY (6000 ->
    # 12000), var_coef=2.0 kept. LITE-ONLY so FULL keeps its matched-budget contract; causal-only so the
    # resumed BIDIR/RANDOM ckpts are byte-untouched. NOTE (2026-08-01 objective pivot): set to 1.0 for the
    # NEW-objective collapse test (the objective must fix collapse at the SAME cheap 6000-step budget, not
    # via more steps); 2.0 is only for the superseded old-objective 2x-budget datapoint.
    # SET TO 1.0 for the 2026-08-01 objective-pivot collapse test: ALL causal arms (old + 3 new-objective)
    # train at the SAME cheap 6000-step budget, so the decisive question is whether the NEW objective clears
    # the 0.020 rep_std floor at the budget where the OLD EMA+VICReg recipe collapsed (0.0128 / 0.0180).
    lite_causal_steps_mult=1.0,
)


# ---------------------------------------------------------------------------
# Start marker / crash diagnostics / logging / heartbeat
# ---------------------------------------------------------------------------
def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node(),
                  cuda=bool(torch.cuda.is_available()))
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED",
                verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__),
                elapsed_s=0.0, traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _heartbeat(output_dir, unit_idx, total_units, elapsed_s, extra=None):
    row = dict(ts_iso=datetime.now(timezone.utc).isoformat(),
               unit_idx=int(unit_idx), total_units=int(total_units),
               elapsed_s=float(elapsed_s))
    if extra:
        row["extra"] = extra
    try:
        with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Latent predictor (I-JEPA-style small MLP; predicts target latent from context latent)
# ---------------------------------------------------------------------------
def _assert_no_vocab_dim(tensors, d_model, vocab_size):
    """OOM regression tripwire (Fix 2b): the latent-PC loss path is bounded by d_model and must NEVER
    materialize a vocab-sized [.,vocab] tensor (the v5 causal-LM OOM class). Verification-only guard."""
    for t in tensors:
        last = int(t.shape[-1])
        assert last == d_model, ("OOM_TRIPWIRE: loss-path latent last-dim=%d != d_model=%d" % (last, d_model))
        assert last != vocab_size, ("OOM_TRIPWIRE: loss-path tensor has vocab-sized last-dim=%d" % last)


class LatentPredictor(torch.nn.Module):
    def __init__(self, d_model, hidden_mult):
        super().__init__()
        h = max(d_model, hidden_mult * d_model)
        self.net = torch.nn.Sequential(
            torch.nn.Linear(d_model, h), torch.nn.GELU(), torch.nn.Linear(h, d_model))

    def forward(self, z):  # [T, d] -> [T, d]
        return self.net(z)


class ClausePredictor(torch.nn.Module):
    """d_model->d_model MLP predicting the NEXT-clause latent from the current causal state (spec Part
    2(c), hierarchy lever). Same shape/OOM-immunity class as LatentPredictor -- never [.,vocab]."""
    def __init__(self, d_model, hidden_mult):
        super().__init__()
        h = max(d_model, hidden_mult * d_model)
        self.net = torch.nn.Sequential(
            torch.nn.Linear(d_model, h), torch.nn.GELU(), torch.nn.Linear(h, d_model))

    def forward(self, z):  # [B, d] -> [B, d]
        return self.net(z)


# ---------------------------------------------------------------------------
# CAUSAL attention path (spec Part 2(a)): a LOCAL wrapper around the imported, UNCHANGED TinyTransformer
# -- reuses the model's own tok_emb/pos_emb/enc/norm, only flips the attention mask from full
# (bidirectional) to lower-triangular (causal). No architecture change to the v2 class itself, so every
# other consumer of TinyTransformer (ARM_MLM/ARM_RANDOM/v2's own MLM pipeline) is completely unaffected.
# ---------------------------------------------------------------------------
def _causal_contextual(model, ids):
    """Position t attends ONLY to positions <= t (strict lower-triangular incl. diagonal). Mirrors
    TinyTransformer._contextual exactly except for the added `mask=` argument to `model.enc(...)`."""
    pad_mask = (ids == model.pad_id)
    L = ids.shape[1]
    pos = torch.arange(L, device=ids.device).unsqueeze(0)
    h = model.tok_emb(ids) + model.pos_emb(pos)
    # torch.nn.TransformerEncoderLayer additive-mask convention: True/-inf positions are DISALLOWED.
    # triu(diagonal=1) marks strictly-upper (future) positions -> disallow those, allow diagonal+lower.
    causal_mask = torch.triu(torch.ones(L, L, device=ids.device, dtype=torch.bool), diagonal=1)
    h = model.enc(h, mask=causal_mask, src_key_padding_mask=pad_mask)
    return model.norm(h), pad_mask


# ---------------------------------------------------------------------------
# HOLD-THEN-REVISE gate (spec Part 2(b)): reuses the EXACT PBWM bistable-write math from
# hdlab/slot_attention_wm.py SlotAttentionWM.step (boundary = sigmoid((surprise-theta)/tau); REPLACE,
# not blend, at low/bistable tau), instantiated at token-to-clause granularity on the causal encoder's
# OWN latents (not a bolt-on parser). Diagnostic-only pass (role-state tracking telemetry; not wired
# into the training loss -- the spec's mechanism claim is about role-hypothesis tracking, not a loss).
# ---------------------------------------------------------------------------
def hold_then_revise_gate(h_role, new_val, pe, theta, tau):
    """h_role, new_val: [B,d]. pe: [B] per-row surprise (1-cos convention, matching slot_attention_wm).
    Returns (h_role_new, boundary[B]): boundary~0 = HOLD, boundary~1 = REPLACE (bistable at low tau)."""
    boundary = torch.sigmoid((pe - theta) / tau)          # [B]
    h_role_new = (1.0 - boundary).unsqueeze(-1) * h_role + boundary.unsqueeze(-1) * new_val
    return h_role_new, boundary


def role_hypothesis_pass(h_seq, theta, tau):
    """Run the hold-then-revise gate token-to-clause across a window's causal latents h_seq [B,L,d].
    h_role initialized from position 0 (the eADM/TDH canonical "first-mentioned-NP=provisional-agent"
    default, per spec Part 2(b): computing the default first is brain-faithful; the wrongness the
    measured wall showed is FAILING TO REVISE it). At each subsequent position, PE = 1-cos(h_role, cur);
    a spike triggers REPLACE (not blend). Returns (final h_role [B,d], boundary_trace [B,L-1])."""
    B, L, _D = h_seq.shape
    h_role = h_seq[:, 0, :].clone()
    if L < 2:
        return h_role, h_seq.new_zeros((B, 0))
    boundaries = []
    for t in range(1, L):
        cur = h_seq[:, t, :]
        pe = 1.0 - torch.nn.functional.cosine_similarity(h_role, cur, dim=-1)
        h_role, b = hold_then_revise_gate(h_role, cur, pe, theta, tau)
        boundaries.append(b)
    return h_role, torch.stack(boundaries, dim=1)


# ---------------------------------------------------------------------------
# VICReg collapse-guard terms (computed in float32; safe under AMP)
# ---------------------------------------------------------------------------
def _vicreg_variance(z, gamma=1.0, eps=1e-4):
    """Hinge on per-dim std >= gamma. z: [N, d] float32. Returns scalar tensor."""
    if z.shape[0] < 2:
        return z.new_zeros(())
    std = torch.sqrt(z.var(dim=0, unbiased=False) + eps)
    return torch.relu(gamma - std).mean()


def _vicreg_covariance(z):
    """Sum of squared off-diagonal covariances / d. z: [N, d] float32. Returns scalar tensor."""
    n, d = z.shape
    if n < 2:
        return z.new_zeros(())
    zc = z - z.mean(dim=0, keepdim=True)
    cov = (zc.T @ zc) / (n - 1)
    off = cov - torch.diag(torch.diag(cov))
    return (off.pow(2).sum()) / d


# ---------------------------------------------------------------------------
# BARLOW-TWINS cross-correlation-to-identity decorrelation (2026-08-01 objective pivot, drill RANK 3).
# Brain-faithful lateral-inhibition / redundancy-reduction analog (Barlow 1961; Zbontar 2021, CITED
# "does not rely on batch size"); the drill's method-comparison scan ranks it the MOST small-batch-robust
# AND most brain-faithful anti-collapse regularizer, replacing VICReg's fragile variance HINGE (weak
# per-dim-std repulsion at small batch). Single-view auto-correlation form (we have one representation
# stream, not two augmentations): mean-center, form the covariance, push its DIAGONAL -> 1 (unit variance
# per dim = structural anti-collapse) and OFF-DIAGONAL -> 0 (decorrelation). Symmetric (penalizes variance
# above AND below 1), unlike VICReg's one-sided hinge. Computed in float32 (AMP-safe).
# ---------------------------------------------------------------------------
def _barlow_decorrelation(z, lambda_od=0.005, eps=1e-4):
    """z: [N, d] float32. Returns scalar tensor. on-diag=(diag(cov)-1)^2 (variance->1, anti-collapse);
    off-diag=lambda*sum(cov_ij^2, i!=j) (decorrelation). N>=2 required (else zero)."""
    n, d = z.shape
    if n < 2:
        return z.new_zeros(())
    zc = z - z.mean(dim=0, keepdim=True)
    cov = (zc.T @ zc) / (n - 1)                       # [d,d] covariance
    diag = torch.diagonal(cov)
    on = ((diag - 1.0) ** 2).mean()                  # per-dim variance -> 1 (structural anti-collapse)
    off = (cov.pow(2).sum() - diag.pow(2).sum()) / d  # decorrelate off-diagonal
    return on + lambda_od * off


# ---------------------------------------------------------------------------
# Latent-predictive-coding (JEPA) training. CUDA-device-safe throughout.
# ---------------------------------------------------------------------------
def lpc_train(stream, spec, cfg, device, seed, out_dir, hb_total, temporal_contiguity=False, causal=False):
    """Train the online encoder by masked-span latent prediction against an EMA target encoder.

    Collapse guard = EMA/stop-grad target (SimSiam-style) + VICReg variance floor + covariance term.
    Optional temporal-contiguity aux loss wires hdlab.temporal_trace (Foldiak slow-feature).
    `causal=True` (spec Part 2, 2026-07-30): flips attention to lower-triangular (_causal_contextual),
    constrains masked-span starts to >=1 (left context always exists), adds the ClausePredictor
    next-window loss term, and runs the hold-then-revise role-hypothesis pass (diagnostic telemetry).
    `causal` and `temporal_contiguity` are mutually exclusive in practice (ARM_LPC_CAUSAL vs
    ARM_LPC_TC) but not asserted so, since nothing in the math actually forbids combining them.
    Returns (online_encoder: TinyTransformer, diag: dict). OOM-free: no vocab-sized tensor anywhere.
    """
    torch.manual_seed(seed)
    np.random.seed(seed)
    max_len = cfg["max_len"]

    def _mk():
        return TinyTransformer(spec["size"], max_len, cfg["d_model"], cfg["n_layers"],
                               cfg["n_heads"], cfg["ffn_mult"], spec["pad"]).to(device)

    online = _mk()
    target = _mk()
    target.load_state_dict(online.state_dict())
    for p in target.parameters():
        p.requires_grad_(False)
    target.eval()
    predictor = LatentPredictor(cfg["d_model"], cfg["lpc_pred_hidden_mult"]).to(device)
    clause_predictor = ClausePredictor(cfg["d_model"], cfg["lpc_pred_hidden_mult"]).to(device) if causal else None

    params = list(online.parameters()) + list(predictor.parameters())
    if causal:
        params += list(clause_predictor.parameters())
    n_enc_params = sum(p.numel() for p in online.parameters())
    _tag = "+TC" if temporal_contiguity else ("+CAUSAL" if causal else "")
    _log("  LPC%s online-encoder params=%.2fM predictor=%.3fM device=%s d=%d L=%d"
         % (_tag, n_enc_params / 1e6,
            sum(p.numel() for p in predictor.parameters()) / 1e6,
            device.type, cfg["d_model"], cfg["n_layers"]))
    opt = torch.optim.AdamW(params, lr=cfg["mlm_lr"])
    use_amp = (device.type == "cuda")
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)

    n_win = stream.shape[0] // max_len
    if n_win < 4:
        raise RuntimeError("train stream too short: %d tokens, %d windows" % (stream.shape[0], n_win))
    windows = stream[:n_win * max_len].reshape(n_win, max_len)
    g = np.random.default_rng(seed + 5)
    bs = min(cfg["mlm_batch"], n_win)
    steps = cfg["mlm_steps"]                     # matched budget: LPC steps == MLM steps
    mask_frac = cfg["lpc_mask_frac"]
    ema_m = cfg["lpc_ema_m"]
    # ANTI-COLLAPSE 2026-08-01 (one-variable fix): the causal arm uses a DOUBLED VICReg variance-term
    # weight (lpc_var_coef_causal, default 2.0) to counter the online-encoder collapse measured at the
    # lite budget; the bidirectional/TC arms keep the original lpc_var_coef=1.0 (they train clean), so
    # the causal-vs-bidir contrast changes exactly ONE knob. Falls back to lpc_var_coef if the causal
    # key is absent (older configs), so no cfg is broken.
    var_coef = cfg.get("lpc_var_coef_causal", cfg["lpc_var_coef"]) if causal else cfg["lpc_var_coef"]
    cov_coef = cfg["lpc_cov_coef"]
    tc_coef = cfg["lpc_tc_coef"] if temporal_contiguity else 0.0
    clause_coef = cfg["lpc_clause_coef"] if causal else 0.0
    role_theta, role_tau = cfg["role_gate_theta"], cfg["role_gate_tau"]
    mask_id, pad_id = spec["mask"], spec["pad"]
    trace = TemporalTrace(alpha=cfg["lpc_tc_alpha"], n_dim=cfg["d_model"]) if temporal_contiguity else None
    contextual_fn = (lambda m, x: _causal_contextual(m, x)) if causal else (lambda m, x: m._contextual(x))

    log_every = max(1, steps // 10)
    pred_hist, tgtstd_hist, tc_hist, clause_hist, replace_rate_hist = [], [], [], [], []
    t0 = time.perf_counter()
    online.train()
    predictor.train()
    for step in range(steps):
        if temporal_contiguity:
            # contiguous run of windows (in corpus/stream order) = a temporally-contiguous pseudo-document
            start = int(g.integers(0, max(1, n_win - bs)))
            sel = (np.arange(start, start + bs) % n_win)
            trace.reset()                         # document-boundary reset (scope-honest: designer-supplied contiguity)
        else:
            sel = g.integers(0, n_win, size=bs)
        ids = torch.from_numpy(windows[sel].astype(np.int64)).to(device)
        B, L = ids.shape
        pad = (ids == pad_id)
        span = max(1, int(round(mask_frac * L)))
        # per-row contiguous target span; ALL device tensors (cuda-safe: no torch.Generator, no cpu tensor)
        # causal (spec 2a, "left-truncated span rule"): start >= 1 so >=1 token of real left context
        # always precedes the target span (a causal encoder predicting a span starting at t=0 would have
        # NO left context to predict from -- the bidirectional arm has no such constraint).
        start_lo = 1 if (causal and L > 1) else 0
        starts = torch.randint(start_lo, max(start_lo + 1, L - span + 1), (B,), device=device)
        ar = torch.arange(L, device=device).unsqueeze(0)
        tgt_mask = (ar >= starts.unsqueeze(1)) & (ar < (starts.unsqueeze(1) + span))
        tgt_mask = tgt_mask & (~pad)
        none_rows = ~tgt_mask.any(dim=1)
        if bool(none_rows.any()):
            first_nonpad = (~pad).float().argmax(dim=1)
            tgt_mask[none_rows, first_nonpad[none_rows]] = True

        ctx_ids = ids.clone()
        ctx_ids[tgt_mask] = mask_id

        opt.zero_grad(set_to_none=True)
        with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=use_amp):
            h_ctx, _ = contextual_fn(online, ctx_ids)        # [B,L,d]  (causal: lower-triangular mask)
            with torch.no_grad():
                h_tgt, _ = contextual_fn(target, ids)        # [B,L,d] stop-grad EMA target
            zc = h_ctx[tgt_mask]                             # [T,d] context latents at target positions
            zt = h_tgt[tgt_mask].detach()                   # [T,d] target latents (stop-grad)
            zp = predictor(zc)                              # [T,d] predicted target latents
            if step == 0:
                _assert_no_vocab_dim((zc, zt, zp), cfg["d_model"], spec["size"])
            pred_loss = torch.nn.functional.smooth_l1_loss(zp, zt)
            zp32, zt32 = zp.float(), zt.float()
            var_loss = _vicreg_variance(zp32) + _vicreg_variance(zt32)
            cov_loss = _vicreg_covariance(zp32) + _vicreg_covariance(zt32)
            loss = pred_loss + var_coef * var_loss + cov_coef * cov_loss

            clause_val = 0.0
            if causal:
                # HIERARCHY (spec 2c): predict the NEXT window's pooled latent (EMA target, stop-grad;
                # clause-adjacency PROXIED as next-window-in-corpus-order, see header FLAG) from the
                # current window's last-valid (non-pad) causal position -- d_model->d_model only.
                last_valid = (~pad).float().cumsum(dim=1).argmax(dim=1)          # [B] last non-pad idx
                cur_state = h_ctx[torch.arange(B, device=device), last_valid]    # [B,d] grad-carrying
                sel_next = torch.from_numpy(((sel + 1) % n_win).astype(np.int64)).to(device)
                ids_next = torch.from_numpy(windows[sel_next.cpu().numpy()].astype(np.int64)).to(device)
                with torch.no_grad():
                    h_tgt_next, pad_next = contextual_fn(target, ids_next)
                    keep_next = (~pad_next).float().unsqueeze(-1)
                    pooled_next = (h_tgt_next * keep_next).sum(dim=1) / keep_next.sum(dim=1).clamp_min(1.0)
                clause_pred = clause_predictor(cur_state)
                if step == 0:
                    _assert_no_vocab_dim((cur_state, pooled_next, clause_pred), cfg["d_model"], spec["size"])
                clause_loss = torch.nn.functional.smooth_l1_loss(clause_pred, pooled_next.detach())
                loss = loss + clause_coef * clause_loss
                clause_val = float(clause_loss.detach())

            tc_val = 0.0
            if temporal_contiguity:
                pooled = online.pooled(ids)                 # [B,d] grad-carrying
                pooled_np = pooled.detach().cpu().numpy()   # explicit host crossing (cuda-safe)
                tc_targets, valid = [], []
                for b in range(B):
                    prev = trace.state                      # slow trace of PRIOR windows (None on step 0)
                    if prev is not None:
                        tc_targets.append(prev)
                        valid.append(b)
                    trace.update(pooled_np[b])
                if valid:
                    tgt_t = torch.from_numpy(np.stack(tc_targets)).to(device)   # back to run device
                    cur = pooled[valid]
                    tc_loss = torch.nn.functional.smooth_l1_loss(cur, tgt_t)
                    loss = loss + tc_coef * tc_loss
                    tc_val = float(tc_loss.detach())

        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite LPC loss step=%d seed=%d (pred=%.4f)"
                                     % (step, seed, float(pred_loss.detach())))
        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()
        # EMA target update (no_grad; buffers copied so LayerNorm running-state tracks)
        with torch.no_grad():
            for pt, po in zip(target.parameters(), online.parameters()):
                pt.mul_(ema_m).add_(po.detach(), alpha=1.0 - ema_m)
            for bt, bo in zip(target.buffers(), online.buffers()):
                bt.copy_(bo)

        tgt_std = float(zt32.std().detach())
        pred_hist.append(float(pred_loss.detach()))
        tgtstd_hist.append(tgt_std)
        tc_hist.append(tc_val)
        clause_hist.append(clause_val)
        if causal:
            # HOLD-THEN-REVISE diagnostic (spec 2b): run on the just-computed causal target latents
            # h_tgt (no_grad, stop-grad already) -- a role-tracking telemetry pass, not a loss term.
            with torch.no_grad():
                _, boundary_trace = role_hypothesis_pass(h_tgt, role_theta, role_tau)
                replace_rate_hist.append(float(boundary_trace.mean().detach()) if boundary_trace.numel() else 0.0)
        if (step % log_every == 0) or (step == steps - 1):
            el = time.perf_counter() - t0
            _log("  LPC%s seed=%d step=%d/%d pred=%.4f var=%.4f cov=%.4f tc=%.4f clause=%.4f tgt_std=%.4f (%.1fs)"
                 % (_tag, seed, step, steps,
                    float(pred_loss.detach()), float(var_loss.detach()), float(cov_loss.detach()),
                    tc_val, clause_val, tgt_std, el))
            _heartbeat(out_dir, step, hb_total, el,
                       extra={"pred_loss": float(pred_loss.detach()), "tgt_std": tgt_std, "seed": seed})

    online.eval()
    k = max(1, len(pred_hist) // 5)
    diag = dict(
        init_pred_loss=float(np.mean(pred_hist[:k])),
        final_pred_loss=float(np.mean(pred_hist[-k:])),
        min_target_std=float(np.min(tgtstd_hist)) if tgtstd_hist else 0.0,
        final_target_std=float(np.mean(tgtstd_hist[-k:])) if tgtstd_hist else 0.0,
        mean_tc_loss=float(np.mean(tc_hist)) if temporal_contiguity else None,
        init_clause_loss=float(np.mean(clause_hist[:k])) if causal else None,
        final_clause_loss=float(np.mean(clause_hist[-k:])) if causal else None,
        role_gate_mean_replace_rate=float(np.mean(replace_rate_hist)) if replace_rate_hist else None,
        causal=bool(causal),
        var_coef=float(var_coef),   # ANTI-COLLAPSE telemetry: effective VICReg variance weight this arm used
        n_steps=steps,
    )
    return online, diag


# ---------------------------------------------------------------------------
# k-WTA (top-k winner-take-all) sparse-latent nonlinearity (AXIS 2, drill's brain-faithful STRUCTURAL
# anti-collapse: k-WTA competition structurally forbids all units collapsing to one value; arXiv:1409.2752).
# Keep the top-k entries (by magnitude) per row, zero the rest. A degenerate constant cannot satisfy a hard
# sparsity pattern the way it satisfies a soft variance hinge. Applied identically in training + battery.
# ---------------------------------------------------------------------------
def _kwta(x, k):
    """x: [N, d] -> keep top-k by |value| per row, zero the rest. k>=d is a no-op."""
    d = x.shape[-1]
    if k is None or k >= d:
        return x
    thresh = torch.topk(x.abs(), k, dim=-1).values[:, -1:]     # [N,1] k-th largest |value| per row
    return x * (x.abs() >= thresh).to(x.dtype)


# ---------------------------------------------------------------------------
# OBJECTIVE PIVOT 2026-08-01 v2 (CORRECTED after an adversarial VET + brain-fidelity drill converged that
# run-5's real_emb arm was a BROKEN TEST: the "real target" = online.tok_emb(ids).detach() is the encoder's
# OWN learned + Barlow-regularized embedding table -> a co-adapting SELF-REFERENTIAL target -> the
# predictive task NEVER LEARNED (init_pred 0.420 -> final 0.419 FLAT) -> reps drifted together, WORSE than
# random (rep_std 0.0078 < RANDOM 0.0121, cos 0.968 > RANDOM 0.924). "Collapse-proof by construction" was
# defeated. Both diagnoses agreed on the fix, implemented here:
#   target_mode: "sampled_softmax" -> EXTERNAL, FIXED-ENTROPY target = the ACTUAL next-span token IDENTITY
#                via a SAMPLED-softmax / InfoNCE loss (score zp against the true token + K sampled negatives
#                through a SEPARATE output projection W_out, NOT the input tok_emb -> genuinely external, no
#                self-reference). Memory-cheap: no [B,L,vocab] logits (only [T,K+1] scores + [T,K+1,d]
#                gathered candidate embs); OOM-safe. This is cortical predictive coding (predict the real
#                external next signal, learn by error) and it is LEARNABLE (unlike regress-to-own-embedding).
#                "ema_latent" -> the OLD EMA self-distillation target, kept as the attribution control that
#                isolates the TARGET axis. Runs through THIS SAME function (not the old lpc_train) so the
#                2x2 is truly one-variable.
#   reg_mode:    "barlow" | "vicreg" -- the REGULARIZER axis.
# COUPLING FIX (the audit's defect #1): the anti-collapse reg is applied to online.pooled(ids) -- the SAME
# pooled representation the rep-quality battery measures the collapse verdict on (encode_concept_text_reps
# pools model.pooled then L2-norms), NOT a decoupled target-latent tensor. Train-time rep_std telemetry is
# now measured on that same pooled rep. reg terms are IDENTICAL across all four 2x2 cells (no target-only
# extra term). Optional sparse_topk applies k-WTA (AXIS 2) to the pooled rep in training (and, matched, in
# the battery post-hoc). CUDA-device-safe. OOM-free (assert no vocab-dim latent tensor).
# ---------------------------------------------------------------------------
def causal_realtarget_train(stream, spec, cfg, device, seed, out_dir, hb_total,
                            target_mode="sampled_softmax", reg_mode="barlow", sparse_topk=None):
    """Returns (online_encoder, diag). Causal masked-span prediction of an EXTERNAL token-identity target
    (sampled softmax) -- or, for the control, the EMA latent -- with a Barlow/VICReg decorrelation reg
    applied to the POOLED representation the battery measures."""
    assert target_mode in ("sampled_softmax", "ema_latent"), target_mode
    assert reg_mode in ("barlow", "vicreg"), reg_mode
    torch.manual_seed(seed)
    np.random.seed(seed)
    max_len = cfg["max_len"]
    vocab = int(spec["size"])
    K_neg = int(cfg.get("lpc_softmax_negatives", 64))

    def _mk():
        return TinyTransformer(spec["size"], max_len, cfg["d_model"], cfg["n_layers"],
                               cfg["n_heads"], cfg["ffn_mult"], spec["pad"]).to(device)

    online = _mk()
    predictor = LatentPredictor(cfg["d_model"], cfg["lpc_pred_hidden_mult"]).to(device)
    params = list(online.parameters()) + list(predictor.parameters())
    use_ema = (target_mode == "ema_latent")
    use_softmax = (target_mode == "sampled_softmax")
    target = None
    W_out = None
    if use_ema:
        target = _mk()
        target.load_state_dict(online.state_dict())
        for p in target.parameters():
            p.requires_grad_(False)
        target.eval()
    if use_softmax:
        # SEPARATE output projection (external readout; NOT tied to the input tok_emb -> no self-reference).
        W_out = torch.nn.Embedding(vocab, cfg["d_model"]).to(device)
        params += list(W_out.parameters())
    _tag = "CAUSAL[%s+%s%s]" % (target_mode, reg_mode, "+topk%d" % sparse_topk if sparse_topk else "")
    _log("  %s online-encoder params=%.2fM device=%s d=%d L=%d K_neg=%d topk=%s"
         % (_tag, sum(p.numel() for p in online.parameters()) / 1e6, device.type,
            cfg["d_model"], cfg["n_layers"], K_neg, sparse_topk))

    opt = torch.optim.AdamW(params, lr=cfg["mlm_lr"])
    use_amp = (device.type == "cuda")
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)

    n_win = stream.shape[0] // max_len
    if n_win < 4:
        raise RuntimeError("train stream too short: %d tokens, %d windows" % (stream.shape[0], n_win))
    windows = stream[:n_win * max_len].reshape(n_win, max_len)
    g = np.random.default_rng(seed + 5)
    bs = min(cfg["mlm_batch"], n_win)
    steps = cfg["mlm_steps"]
    mask_frac = cfg["lpc_mask_frac"]
    ema_m = cfg["lpc_ema_m"]
    var_coef = cfg.get("lpc_var_coef_causal", cfg["lpc_var_coef"])   # only used in vicreg reg_mode
    cov_coef = cfg["lpc_cov_coef"]
    barlow_od = cfg.get("lpc_barlow_lambda_od", 0.005)
    mask_id, pad_id = spec["mask"], spec["pad"]

    def _reg(z32):
        if reg_mode == "barlow":
            return _barlow_decorrelation(z32, lambda_od=barlow_od)
        return var_coef * _vicreg_variance(z32) + cov_coef * _vicreg_covariance(z32)

    log_every = max(1, steps // 10)
    pred_hist, repstd_hist = [], []
    t0 = time.perf_counter()
    online.train()
    predictor.train()
    for step in range(steps):
        sel = g.integers(0, n_win, size=bs)
        ids = torch.from_numpy(windows[sel].astype(np.int64)).to(device)
        B, L = ids.shape
        pad = (ids == pad_id)
        span = max(1, int(round(mask_frac * L)))
        start_lo = 1 if L > 1 else 0                 # causal: always >=1 token of real left context
        starts = torch.randint(start_lo, max(start_lo + 1, L - span + 1), (B,), device=device)
        ar = torch.arange(L, device=device).unsqueeze(0)
        tgt_mask = (ar >= starts.unsqueeze(1)) & (ar < (starts.unsqueeze(1) + span))
        tgt_mask = tgt_mask & (~pad)
        none_rows = ~tgt_mask.any(dim=1)
        if bool(none_rows.any()):
            first_nonpad = (~pad).float().argmax(dim=1)
            tgt_mask[none_rows, first_nonpad[none_rows]] = True

        ctx_ids = ids.clone()
        ctx_ids[tgt_mask] = mask_id

        opt.zero_grad(set_to_none=True)
        with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=use_amp):
            h_ctx, _ = _causal_contextual(online, ctx_ids)   # [B,L,d] causal (left-context only)
            zc = h_ctx[tgt_mask]                             # [T,d] causal latents at target positions
            zp = predictor(zc)                              # [T,d] prediction vector
            if use_softmax:
                # EXTERNAL token-identity target via sampled softmax (InfoNCE). true id + K sampled negatives.
                y = ids[tgt_mask]                            # [T] true next-span token ids (EXTERNAL label)
                T = y.shape[0]
                neg = torch.randint(0, vocab, (T, K_neg), device=device)   # [T,K] sampled negatives
                cand = torch.cat([y.unsqueeze(1), neg], dim=1)             # [T,K+1] col0 = true
                cand_emb = W_out(cand)                       # [T,K+1,d] gathered rows only (no [.,vocab])
                logits = (zp.unsqueeze(1) * cand_emb).sum(-1)  # [T,K+1] scores; NO vocab-sized activation
                labels = torch.zeros(T, dtype=torch.long, device=device)   # true is column 0
                if step == 0:
                    _assert_no_vocab_dim((zc, zp, cand_emb), cfg["d_model"], vocab)
                pred_loss = torch.nn.functional.cross_entropy(logits.float(), labels)
            else:
                with torch.no_grad():
                    h_tgt, _ = _causal_contextual(target, ids)
                zt = h_tgt[tgt_mask].detach()
                if step == 0:
                    _assert_no_vocab_dim((zc, zp, zt), cfg["d_model"], vocab)
                pred_loss = torch.nn.functional.smooth_l1_loss(zp, zt)

            # COUPLED anti-collapse: reg on the SAME pooled rep the battery measures the verdict on.
            pooled = online.pooled(ids)                      # [B,d] (matches encode_concept_text_reps)
            pooled32 = pooled.float()
            if sparse_topk:
                pooled32 = _kwta(pooled32, int(sparse_topk))
            reg_loss = _reg(pooled32)
            loss = pred_loss + reg_loss

        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite loss step=%d seed=%d mode=%s/%s (pred=%.4f)"
                                     % (step, seed, target_mode, reg_mode, float(pred_loss.detach())))
        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()
        if use_ema:
            with torch.no_grad():
                for pt, po in zip(target.parameters(), online.parameters()):
                    pt.mul_(ema_m).add_(po.detach(), alpha=1.0 - ema_m)
                for bt, bo in zip(target.buffers(), online.buffers()):
                    bt.copy_(bo)

        rep_std = float(pooled32.std(dim=0).mean().detach())  # rep_std on the COUPLED pooled rep
        pred_hist.append(float(pred_loss.detach()))
        repstd_hist.append(rep_std)
        if (step % log_every == 0) or (step == steps - 1):
            el = time.perf_counter() - t0
            _log("  %s seed=%d step=%d/%d pred=%.4f reg=%.4f pooled_rep_std=%.4f (%.1fs)"
                 % (_tag, seed, step, steps, float(pred_loss.detach()), float(reg_loss.detach()),
                    rep_std, el))
            _heartbeat(out_dir, step, hb_total, el,
                       extra={"pred_loss": float(pred_loss.detach()), "rep_std": rep_std, "seed": seed})

    online.eval()
    k = max(1, len(pred_hist) // 5)
    diag = dict(
        init_pred_loss=float(np.mean(pred_hist[:k])),
        final_pred_loss=float(np.mean(pred_hist[-k:])),
        min_train_rep_std=float(np.min(repstd_hist)) if repstd_hist else 0.0,
        final_train_rep_std=float(np.mean(repstd_hist[-k:])) if repstd_hist else 0.0,
        pred_drop=float(np.mean(pred_hist[:k]) - np.mean(pred_hist[-k:])),
        target_mode=target_mode, reg_mode=reg_mode, uses_ema=bool(use_ema),
        external_target=bool(use_softmax), softmax_negatives=(K_neg if use_softmax else None),
        sparse_topk=(int(sparse_topk) if sparse_topk else None),
        causal=True, n_steps=steps,
    )
    return online, diag


# ---------------------------------------------------------------------------
# Rep-quality battery (all on FROZEN concept reps; KB read-only)
# ---------------------------------------------------------------------------
def _rankdata(x):
    """Average ranks (tie-corrected)."""
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), dtype=np.float64)
    sx = x[order]
    i = 0
    n = len(x)
    while i < n:
        j = i
        while j + 1 < n and sx[j + 1] == sx[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return ranks


def _spearman(a, b):
    if len(a) < 3:
        return None
    ra, rb = _rankdata(np.asarray(a, dtype=np.float64)), _rankdata(np.asarray(b, dtype=np.float64))
    ra = ra - ra.mean()
    rb = rb - rb.mean()
    denom = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    if denom < 1e-12:
        return None
    return float((ra * rb).sum() / denom)


def graded_geometry_eval(reps, split, adj, seed, n_far=8, max_q=None):
    """Spearman(encoder cosine, KB graded proximity {1-hop=3, 2-hop=2, far=1}) over held-out concepts.
    Leak-proof: held-out reps carry ZERO relational input; KB proximity is a READ-ONLY probe."""
    held = split["held_idx"]
    train_set = set(int(x) for x in split["train_eval_idx"].tolist())
    have = np.linalg.norm(reps, axis=1) > 1e-8
    rng = np.random.default_rng(seed + 41)
    train_pool = sorted(i for i in train_set if have[i])
    if len(train_pool) < 20:
        return None, 0
    train_pool_arr = np.array(train_pool, dtype=np.int64)
    sp = []
    q_list = [int(h) for h in held.tolist() if have[h]]
    if max_q is not None and len(q_list) > max_q:
        q_list = sorted(rng.choice(np.array(q_list), size=max_q, replace=False).tolist())
    for h in q_list:
        nb1 = sorted(j for j in adj[h] if j in train_set and have[j] and j != h)
        if len(nb1) < 1:
            continue
        nb2set = set()
        for j in nb1:
            nb2set |= adj[j]
        nb1set = set(nb1)
        nb2 = sorted(j for j in nb2set if j in train_set and have[j] and j != h and j not in nb1set)
        excl = nb1set | set(nb2) | set(adj[h]) | {h}
        far_cands = [j for j in train_pool if j not in excl]
        if not far_cands or (len(nb1) + len(nb2)) < 2:
            continue
        take2 = nb2[:max(2, len(nb1))]
        n_far_take = min(n_far, len(far_cands))
        far = rng.choice(np.array(far_cands), size=n_far_take, replace=False).tolist()
        cand = list(nb1) + list(take2) + list(far)
        prox = ([3] * len(nb1)) + ([2] * len(take2)) + ([1] * len(far))
        if len(set(prox)) < 2 or len(cand) < 4:
            continue
        cos = reps[h] @ reps[np.array(cand, dtype=np.int64)].T
        s = _spearman(cos, np.array(prox, dtype=np.float64))
        if s is not None:
            sp.append(s)
    return (float(np.mean(sp)) if sp else None), len(sp)


def heldout_probe_eval(reps, universe, split, ridge=1.0):
    """Frozen closed-form ridge linear probe: lexname (supersense) trained on TRAIN concepts,
    tested on held-out-NEW. Head is linear + frozen -> gains attributable to rep quality only."""
    lex = universe["lexnames"]
    have = np.linalg.norm(reps, axis=1) > 1e-8
    tr = [int(i) for i in split["train_eval_idx"].tolist() if have[i] and lex[i] is not None]
    if len(tr) < 30:
        return None, 0
    classes = sorted(set(lex[i] for i in tr))
    cls_idx = {c: k for k, c in enumerate(classes)}
    if len(classes) < 2:
        return None, 0
    he = [int(i) for i in split["held_idx"].tolist()
          if have[i] and lex[i] is not None and lex[i] in cls_idx]
    if len(he) < 10:
        return None, 0
    Xtr = reps[np.array(tr, dtype=np.int64)].astype(np.float64)
    Ytr = np.zeros((len(tr), len(classes)), dtype=np.float64)
    for r, i in enumerate(tr):
        Ytr[r, cls_idx[lex[i]]] = 1.0
    d = Xtr.shape[1]
    W = np.linalg.solve(Xtr.T @ Xtr + ridge * np.eye(d), Xtr.T @ Ytr)   # closed-form ridge
    Xhe = reps[np.array(he, dtype=np.int64)].astype(np.float64)
    pred = np.argmax(Xhe @ W, axis=1)
    true = np.array([cls_idx[lex[i]] for i in he], dtype=np.int64)
    return float((pred == true).mean()), len(he)


def collapse_diag(reps, split, seed, max_pairs=4000):
    """Frozen-rep collapse witness: per-dim std across held-out concepts + mean pairwise abs cosine."""
    held = split["held_idx"]
    have = np.linalg.norm(reps, axis=1) > 1e-8
    idx = np.array([int(h) for h in held.tolist() if have[h]], dtype=np.int64)
    if idx.shape[0] < 3:
        return dict(rep_std=None, mean_pairwise_cos=None, n=int(idx.shape[0]))
    R = reps[idx]
    rep_std = float(R.std(axis=0).mean())
    rng = np.random.default_rng(seed + 61)
    n = R.shape[0]
    m = min(max_pairs, n * (n - 1) // 2)
    a = rng.integers(0, n, size=m)
    b = rng.integers(0, n, size=m)
    ok = a != b
    cos = np.abs((R[a[ok]] * R[b[ok]]).sum(axis=1))
    return dict(rep_std=rep_std, mean_pairwise_cos=float(cos.mean()), n=int(n))


# ---------------------------------------------------------------------------
# ARMS-MUST-DIFFER (META_RULE_AF)
# ---------------------------------------------------------------------------
def _arms_differ(rep_dict):
    dig = {}
    for name, arr in rep_dict.items():
        dig[name] = hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()
    names = sorted(dig)
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            assert dig[names[a]] != dig[names[b]], \
                "META_RULE_AF VIOLATION: %s and %s bit-identical" % (names[a], names[b])
    return dig


# ---------------------------------------------------------------------------
# MLM-baseline reuse (Fix 4): reuse V2's already-trained ckpt instead of retraining ARM_MLM.
# Returns (model, tok, spec, source) or (None,...,"fresh") when the seed's ckpt is absent.
# ---------------------------------------------------------------------------
def _load_mlm_baseline_encoder(seed, device):
    ckpt_path = os.path.join(V2_CKPT_DIR, "ckpt_seed_%d.pt" % seed)
    if not os.path.exists(ckpt_path):
        return None, None, None, "fresh_no_v2_ckpt"
    ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    mc = ck["model_cfg"]
    model = TinyTransformer(mc["vocab"], mc["max_len"], mc["d_model"], mc["n_layers"],
                            mc["n_heads"], mc["ffn_mult"], mc["pad_id"]).to(device)
    model.load_state_dict(ck["state_dict"])
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    from tokenizers import Tokenizer
    tok = Tokenizer.from_str(ck["tokenizer_json"])
    return model, tok, ck["spec"], "reused_v2_ckpt"


# ---------------------------------------------------------------------------
# Per-arm reusable checkpoint (Fix 2d): bit-identical dict shape to what FrozenV2Encoder loads
# (state_dict + model_cfg + tokenizer_json), so the downstream binding-compare cell needs zero new
# loader code -- only a path change. Saved for the arms section 3 consumes (ARM_LPC, ARM_MLM) plus
# ARM_LPC_TC for completeness (ARM_RANDOM skipped -- untrained, nothing to reuse).
# ---------------------------------------------------------------------------
def _save_arm_ckpt(out_dir, seed, arm, model, tok, spec, cfg):
    # 2026-08-01 AMENDMENT (Probe 2a+3 bundle): ARM_RANDOM used to be skipped ("untrained, nothing to
    # reuse") but the bundled causal-vs-bidir-vs-MLM-vs-random fair test on
    # exp_syntactic_role_agent_patient_voice_probe_v1.py needs a real FrozenV2Encoder-shaped ckpt for the
    # untrained-floor control arm too (path-swap pattern, zero new probe code) -- now saved like every
    # other arm. No cost: the model already exists in memory (no extra training).
    try:
        ck = dict(
            state_dict={k: v.detach().cpu() for k, v in model.state_dict().items()},
            spec=spec,
            model_cfg=dict(vocab=int(spec["size"]), max_len=int(cfg["max_len"]),
                           d_model=int(cfg["d_model"]), n_layers=int(cfg["n_layers"]),
                           n_heads=int(cfg["n_heads"]), ffn_mult=int(cfg["ffn_mult"]),
                           pad_id=int(spec["pad"])),
            tokenizer_json=tok.to_str(),
            seed=int(seed), run_mode=cfg["run_mode"], anchor=ANCHOR_NAME, arm=arm)
        path = os.path.join(out_dir, "ckpt_seed_%d_%s.pt" % (seed, arm))
        tmp = path + ".tmp"
        torch.save(ck, tmp)
        os.replace(tmp, path)
    except (OSError, RuntimeError, ValueError) as e:
        _log("  WARN arm-ckpt save failed (%s/%s): %s" % (arm, seed, str(e)[:200]))
        return None
    try:
        return os.path.relpath(path, _REPO)          # repo-relative in production
    except ValueError:
        return os.path.abspath(path)                 # cross-drive (self-test temp on another mount)


# ---------------------------------------------------------------------------
# Data-prep bundle cache (Fix D): torch.save the seed-independent prepare_data() bundle keyed by a hash
# of (data-affecting cfg subset, corpus mtime) so a crash DURING arm training does not repeat the
# ~2-3h data-prep on resume. Tokenizer serialized via to_str()/from_str() (numpy/python-native rest).
# ---------------------------------------------------------------------------
def _dataprep_cache_key(cfg):
    corpus_mtime = os.path.getmtime(ARC_CORPUS) if os.path.exists(ARC_CORPUS) else 0.0
    payload = dict(cfg_subset={k: cfg.get(k) for k in _DATA_CFG_KEYS},
                   corpus_mtime=round(float(corpus_mtime), 3), run_mode=cfg["run_mode"])
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def _bundle_cache_path(out_dir, cfg):
    return os.path.join(out_dir, "dataprep_bundle_%s.pt" % _dataprep_cache_key(cfg))


def _save_bundle_cache(path, bundle):
    b = dict(bundle)
    b["tok_json"] = b["tok"].to_str()
    b.pop("tok", None)
    tmp = path + ".tmp"
    torch.save(b, tmp)
    os.replace(tmp, path)


def _load_bundle_cache(path):
    from tokenizers import Tokenizer
    b = torch.load(path, map_location="cpu", weights_only=False)
    b["tok"] = Tokenizer.from_str(b.pop("tok_json"))
    return b


# ---------------------------------------------------------------------------
# Data-prep-headroom gate (Fix C): measure the REAL per-line rate on a bounded corpus slice, extrapolate
# to the full data-prep cost, and REFUSE FULL if the projected ETA exceeds the ceiling. Fails loud.
# ---------------------------------------------------------------------------
def _headroom_projection(measured_rate, full_lines, n_passes, ceiling_s):
    proj = ((full_lines / measured_rate) * n_passes) if measured_rate > 0 else float("inf")
    return dict(measured_lines_per_sec=float(measured_rate), projected_full_dataprep_s=float(proj),
                n_passes=int(n_passes), ceiling_s=int(ceiling_s), full_lines=int(full_lines),
                verdict=("DATA_PREP_OK" if proj <= ceiling_s else "DATA_PREP_TOO_SLOW"))


def _data_prep_headroom(out_dir):
    """Run count_pass over DATA_PREP_SMOKE_LINES of the REAL corpus at FULL cfg, measure lines/sec, and
    project the full data-prep ETA (n_passes single-line passes over FULL max_lines)."""
    full_uni = load_concept_universe(FULL_CFG)
    probe = dict(FULL_CFG)
    probe["max_lines"] = DATA_PREP_SMOKE_LINES
    _log("data-prep headroom probe: count_pass over %d REAL corpus lines (FULL cfg)..."
         % DATA_PREP_SMOKE_LINES)
    t0 = time.perf_counter()
    _counts, stats = count_pass(probe, full_uni["surf_to_idx"], out_dir=out_dir)
    el = time.perf_counter() - t0
    rate = (stats["n_read"] / el) if el > 0 else 0.0
    full_lines = FULL_CFG["max_lines"] or stats["n_read"]
    h = _headroom_projection(rate, full_lines, N_DATA_PASSES, DATA_PREP_TIME_CEILING_S)
    h.update(probe_lines=int(stats["n_read"]), probe_elapsed_s=float(el))
    return h


# ---------------------------------------------------------------------------
# Encoder builders per arm (each returns a frozen TinyTransformer + training diag + optional tok/spec
# override for the reused-MLM arm, which must encode with ITS OWN ckpt tokenizer).
# ---------------------------------------------------------------------------
def _build_encoder(arm, cfg, spec, device, seed, stream, out_dir, hb_total):
    if arm == ARM_MLM:
        if cfg["run_mode"] == "full":
            m, mtok, mspec, src = _load_mlm_baseline_encoder(seed, device)
            if m is not None:
                _log("  ARM_MLM: reused V2 ckpt_seed_%d.pt (no retrain; budget-matched at 60000 steps)"
                     % seed)
                return m, dict(reused_v2_ckpt=True, baseline_source=src), mtok, mspec
            _log("  ARM_MLM: V2 ckpt_seed_%d.pt ABSENT -> fresh matched-budget MLM train (fallback)"
                 % seed)
        model, final_loss = mlm_train(stream, spec, cfg, device, seed, out_dir, hb_total)
        return model, dict(final_mlm_loss=float(final_loss), reused_v2_ckpt=False), None, None
    if arm == ARM_RANDOM:
        torch.manual_seed(seed + 999)
        model = TinyTransformer(spec["size"], cfg["max_len"], cfg["d_model"], cfg["n_layers"],
                                cfg["n_heads"], cfg["ffn_mult"], spec["pad"]).to(device)
        model.eval()
        return model, dict(untrained=True), None, None
    if arm == ARM_LPC_BIDIR:
        m, d = lpc_train(stream, spec, cfg, device, seed, out_dir, hb_total,
                         temporal_contiguity=False, causal=False)
        return m, d, None, None
    if arm == ARM_LPC_TC:
        m, d = lpc_train(stream, spec, cfg, device, seed, out_dir, hb_total,
                         temporal_contiguity=True, causal=False)
        return m, d, None, None
    if arm == ARM_LPC_CAUSAL:
        # MINIMAL BUDGET BUMP 2026-08-01 iter-3 (LITE-only, causal-only): apply lite_causal_steps_mult to
        # the causal arm's optimizer steps to escape the marginal undertrained collapse. Only present in
        # LITE_CFG (defaults to 1.0 elsewhere), so FULL's matched-budget causal-vs-bidir contract is
        # untouched. Shallow-copy cfg so the bumped step count does NOT leak into the recorded matched_budget
        # of other arms; lpc_train records the actual n_steps used in its diag for landed verification.
        ccfg = dict(cfg)
        mult = float(cfg.get("lite_causal_steps_mult", 1.0))
        if mult != 1.0:
            ccfg["mlm_steps"] = int(round(cfg["mlm_steps"] * mult))
            _log("  ARM_LPC_CAUSAL: lite_causal_steps_mult=%.2f -> mlm_steps %d->%d (undertrained-collapse "
                 "budget bump; var_coef=2.0 kept)" % (mult, cfg["mlm_steps"], ccfg["mlm_steps"]))
        m, d = lpc_train(stream, spec, ccfg, device, seed, out_dir, hb_total,
                         temporal_contiguity=False, causal=True)
        return m, d, None, None
    # OBJECTIVE PIVOT v2 2026-08-01: all causal-family arms train via causal_realtarget_train (one path ->
    # one-variable 2x2). Same cheap budget (6000 steps) -- the OBJECTIVE, not more compute, is the lever.
    if arm in NEW_OBJECTIVE_ARMS:
        _EXT = (ARM_CAUSAL_EXT_BARLOW, ARM_CAUSAL_EXT_VICREG, ARM_CAUSAL_EXT_BARLOW_TOPK)
        _BARLOW = (ARM_CAUSAL_EXT_BARLOW, ARM_CAUSAL_EMA_BARLOW, ARM_CAUSAL_EXT_BARLOW_TOPK)
        tmode = "sampled_softmax" if arm in _EXT else "ema_latent"
        rmode = "barlow" if arm in _BARLOW else "vicreg"
        topk = cfg.get("lpc_sparse_topk", 64) if arm == ARM_CAUSAL_EXT_BARLOW_TOPK else None
        m, d = causal_realtarget_train(stream, spec, cfg, device, seed, out_dir, hb_total,
                                       target_mode=tmode, reg_mode=rmode, sparse_topk=topk)
        return m, d, None, None
    raise ValueError("unknown arm %s" % arm)


def run_one_seed(seed, cfg, device, out_dir, universe, bundle):
    t0 = time.perf_counter()
    split = bundle["split"]
    counts = bundle["counts"]
    tok = bundle["tok"]
    spec = bundle["spec"]
    postings = bundle["postings"]
    ground = bundle["ground"]           # noqa: F841  (grounding not scored here; encoder-only battery)
    adj, deg, n_shards = bundle["adj"], bundle["deg"], bundle["n_shards"]
    arms_to_run = LITE_ARMS if cfg["run_mode"] == "lite" else ARMS
    n_obj_arms_running = max(1, len([a for a in arms_to_run if a in OBJECTIVE_ARMS]))
    hb_total = cfg["mlm_steps"] * n_obj_arms_running

    arm_results = {}
    arm_digests = {}
    ckpt_paths = {}
    # (seed, arm) unit checkpoint/resume (Fix 2c): a crash in a later arm keeps every already-complete
    # arm's ~2.8-3.2 GPU-hr of work. Resume skips units already recorded in units.jsonl.
    done = ckpt.completed_units(out_dir)
    prior = ckpt.load_units(out_dir) if done else {}
    for arm in arms_to_run:
        key = ckpt.unit_key(seed, arm)
        if key in done:
            u = prior[key]                            # load_units already unwraps to the result dict
            arm_results[arm] = u["arm_result"]
            arm_digests[arm] = u["held_rep_digest"]
            ckpt_paths[arm] = u.get("ckpt_path")
            _log("seed=%d ARM=%s: RESUMED (already in units.jsonl; skip retrain)" % (seed, arm))
            continue
        _log("seed=%d ARM=%s: build encoder..." % (seed, arm))
        model, tdiag, enc_tok, enc_spec = _build_encoder(
            arm, cfg, spec, device, seed, bundle["stream"], out_dir, hb_total)
        use_tok = enc_tok if enc_tok is not None else tok
        use_spec = enc_spec if enc_spec is not None else spec
        # persist the reusable encoder ckpt BEFORE the (potentially long) rep battery, so a crash mid-
        # battery still leaves the trained weights on disk (Fix 2d).
        ckpt_paths[arm] = _save_arm_ckpt(out_dir, seed, arm, model, use_tok, use_spec, cfg)
        _log("seed=%d ARM=%s: encode concept reps..." % (seed, arm))
        reps, mrep_cnt = encode_concept_text_reps(model, use_tok, postings, cfg, device, use_spec)
        held = reps[split["held_idx"]].copy()
        digest = hashlib.sha256(np.ascontiguousarray(held).tobytes()).hexdigest()

        gg, gg_nq = graded_geometry_eval(reps, split, adj, seed, max_q=cfg.get("gg_max_q"))
        probe, probe_nq = heldout_probe_eval(reps, universe, split)
        rel = relational_eval(ground, reps, counts, universe, split, adj, deg, n_shards, seed, w_star=1.0)
        rel_auc = rel.get("ARM_RAW_TEXT") if rel else None   # text-alone neighborhood AUC = THIS encoder
        rel_nq = rel.get("_n_query", 0) if rel else 0
        cdiag = collapse_diag(reps, split, seed)

        arm_results[arm] = dict(
            graded_geometry=gg, graded_geometry_nq=gg_nq,
            heldout_probe=probe, heldout_probe_nq=probe_nq,
            relational_auc=rel_auc, relational_nq=rel_nq,
            rep_std=cdiag["rep_std"], mean_pairwise_cos=cdiag["mean_pairwise_cos"],
            mention_rep_coverage=float((mrep_cnt[split["held_idx"]] > 0).mean()),
            train_diag=tdiag,
        )
        arm_digests[arm] = digest
        ckpt.record_unit(out_dir, key, dict(arm_result=arm_results[arm], held_rep_digest=digest,
                                             ckpt_path=ckpt_paths[arm]))
        _log("seed=%d ARM=%s: gg=%s probe=%s rel=%s rep_std=%s (gg_nq=%d)"
             % (seed, arm, _fmt(gg), _fmt(probe), _fmt(rel_auc), _fmt(cdiag["rep_std"]), gg_nq))

    # ARMS-MUST-DIFFER (META_RULE_AF) -- NON-FATAL (2026-08-01): a COLLAPSE experiment can legitimately
    # produce two degenerate encoders whose held-rep matrices coincide; asserting here would crash the
    # whole (expensive) GPU run and DISCARD the rep_std collapse numbers we ran it to get. Record any
    # bit-identical pair as a flag instead; the decisive per-arm rep_std is written regardless. (Mirrors
    # the same fix applied to the voice-role probe cell's check_arms_differ.)
    _names = sorted(arm_digests)
    arm_collisions = []
    for _i in range(len(_names)):
        for _j in range(_i + 1, len(_names)):
            if arm_digests[_names[_i]] == arm_digests[_names[_j]]:
                arm_collisions.append([_names[_i], _names[_j]])
    if arm_collisions:
        _log("  META_RULE_AF WARN (non-fatal): bit-identical held-rep arm pairs %r -- likely mutual "
             "collapse/degeneracy at this budget; rep_std reported per arm regardless" % arm_collisions)
    return dict(seed=int(seed), run_mode=cfg["run_mode"], elapsed_s=float(time.perf_counter() - t0),
                ckpt_paths=ckpt_paths, arm_collisions=arm_collisions,
                arms=arm_results, arm_digests=arm_digests,
                matched_budget=dict(steps=cfg["mlm_steps"], batch=cfg["mlm_batch"],
                                    train_token_budget=cfg["train_token_budget"],
                                    d_model=cfg["d_model"], n_layers=cfg["n_layers"],
                                    matched_encoder_params=True,
                                    note="LPC adds a small predictor + non-trained EMA target; "
                                         "base-encoder architecture/params/steps/tokens matched across arms"))


def _fmt(x):
    return ("%.4f" % x) if isinstance(x, float) else str(x)


# ---------------------------------------------------------------------------
# LITE verdict (2026-07-30 coordinator-revised spec): this run is UNDERTRAINED BY CONSTRUCTION (6000
# steps vs FULL's 60000). It must NEVER be judged against build_verdict()'s HARD_PASS/HARD_FAIL bands --
# those bands are calibrated for the FULL budget and a lite null would be misreported as a refutation.
# This verdict ONLY certifies the 3 encoders trained/saved cleanly (no collapse, arms differ); the
# DECISIVE early-signal comparison (context-invariance / role-distinctness / filler-invariance) is a
# SEPARATE cell (exp_context_invariance_lpc_lite_probe_v1.py) that consumes the ckpts this run produces.
# A graded_geometry delta is reported here too, but tagged UNGATED/BONUS -- honesty per the "a null is
# inconclusive, a positive is encouraging" mandate.
# ---------------------------------------------------------------------------
def build_lite_verdict(per_seed, cfg):
    """OBJECTIVE-PIVOT COLLAPSE TEST v2 2026-08-01 (corrected after the run-5 broken-test retraction).
    FAIR PRIMARY METRIC (all on the PRIMARY arm ARM_CAUSAL_EXT_BARLOW = external sampled-softmax token
    identity + Barlow, at the cheap 6000-step budget):
      (a) LEARNS  -- pred_loss drops meaningfully (pred_drop >= LEARN_MIN_DROP), unlike run-5's flat 0.42;
      (b) NON-COLLAPSED -- rep_std >= COLLAPSE_REP_STD_FLOOR (0.020) AND BEATS RANDOM on BOTH rep_std
          (>) and mean_pairwise_cos (<).
    HARD-PASS (LITE_EXTERNAL_TARGET_FIXES_COLLAPSE) = (a) AND (b). If any trained causal arm is worse-than-
    random on rep_std or cos, the run is auto-flagged MIS-SPECIFIED (LITE_MISSPECIFIED) -- that backstop is
    exactly what run-5's REAL_BARLOW (0.0078 < RANDOM 0.0121) should have tripped. HARD-FAIL
    (LITE_COLLAPSE_PERSISTS) only if the primary genuinely LEARNS but still collapses (then it is scale/
    data, not the target). Reports the full 2x2 (target x reg) + AXIS-2 topk for attribution."""
    seeds = sorted(per_seed.keys(), key=lambda k: int(k))
    LEARN_MIN_DROP = 0.30            # cross-entropy must drop >= this from init (init ~ log(K+1) ~ 4.17)

    def arm_val(arm, key):
        vv = [per_seed[k]["arms"].get(arm, {}).get(key) for k in seeds]
        vv = [x for x in vv if x is not None]
        return float(np.mean(vv)) if vv else None

    def arm_diag(arm, key):
        vv = [(per_seed[k]["arms"].get(arm, {}).get("train_diag") or {}).get(key) for k in seeds]
        vv = [x for x in vv if x is not None]
        return float(np.mean(vv)) if vv else None

    primary = ARM_CAUSAL_EXT_BARLOW
    causal_family = [ARM_CAUSAL_EXT_BARLOW, ARM_CAUSAL_EXT_VICREG, ARM_CAUSAL_EMA_BARLOW,
                     ARM_CAUSAL_EMA_VICREG, ARM_CAUSAL_EXT_BARLOW_TOPK, ARM_LPC_BIDIR, ARM_RANDOM]
    present = [a for a in causal_family if any(a in per_seed[k].get("arms", {}) for k in seeds)]
    table = {a: {"rep_std": arm_val(a, "rep_std"), "cos": arm_val(a, "mean_pairwise_cos"),
                 "pred_drop": arm_diag(a, "pred_drop"),
                 "init_pred": arm_diag(a, "init_pred_loss"), "final_pred": arm_diag(a, "final_pred_loss")}
             for a in present}

    rand_rs = arm_val(ARM_RANDOM, "rep_std")
    rand_cos = arm_val(ARM_RANDOM, "mean_pairwise_cos")

    # BEAT-RANDOM sanity backstop (the audit's defect #3): any TRAINED causal arm worse-than-random.
    trained_arms = [a for a in present if a not in (ARM_RANDOM,)]
    misspec = []
    if rand_rs is not None and rand_cos is not None:
        for a in trained_arms:
            rs, cs = table[a]["rep_std"], table[a]["cos"]
            if rs is not None and cs is not None and (rs <= rand_rs or cs >= rand_cos):
                misspec.append(a)

    p_rs, p_cos, p_drop = arm_val(primary, "rep_std"), arm_val(primary, "mean_pairwise_cos"), arm_diag(primary, "pred_drop")
    all_trained = all(primary in per_seed[k].get("arms", {}) for k in seeds)
    ckpts_saved = all(per_seed[k].get("ckpt_paths", {}).get(primary) for k in seeds)
    learns = (p_drop is not None and p_drop >= LEARN_MIN_DROP)
    beats_random = (p_rs is not None and rand_rs is not None and p_rs > rand_rs
                    and p_cos is not None and rand_cos is not None and p_cos < rand_cos)
    clears_floor = (p_rs is not None and p_rs >= COLLAPSE_REP_STD_FLOOR)
    hard_pass = learns and clears_floor and beats_random

    if not (all_trained and ckpts_saved):
        verdict = "LITE_TRAIN_INCOMPLETE"
        vmsg = "LITE_TRAIN_INCOMPLETE: primary %s not trained+checkpointed (all_trained=%s ckpts_saved=%s)." % (
            primary, all_trained, ckpts_saved)
    elif primary in misspec and not learns:
        verdict = "LITE_MISSPECIFIED"
        vmsg = ("LITE_MISSPECIFIED: primary %s did NOT learn (pred_drop=%s < %.2f) and/or is worse-than-random "
                "(rep_std=%s vs RANDOM %s, cos=%s vs RANDOM %s). Broken-test backstop tripped; NOT a real "
                "collapse negative. mis-specified arms: %s." % (primary, _fmt(p_drop), LEARN_MIN_DROP,
                _fmt(p_rs), _fmt(rand_rs), _fmt(p_cos), _fmt(rand_cos), misspec))
    elif hard_pass:
        verdict = "LITE_EXTERNAL_TARGET_FIXES_COLLAPSE"
        vmsg = ("LITE_EXTERNAL_TARGET_FIXES_COLLAPSE: primary %s LEARNS (pred_drop=%s) AND stays non-collapsed "
                "(rep_std=%s>=%.3f, beats RANDOM rep_std %s + cos %s<%s) at the cheap 6000-step budget where "
                "the OLD EMA+VICReg recipe collapsed. The brain-faithful EXTERNAL predictive objective removes "
                "the collapse cause. Full 2x2: %s." % (primary, _fmt(p_drop), _fmt(p_rs), COLLAPSE_REP_STD_FLOOR,
                _fmt(rand_rs), _fmt(p_cos), _fmt(rand_cos), {a: {k2: (round(v2, 4) if isinstance(v2, float) else v2)
                for k2, v2 in table[a].items()} for a in present}))
    elif learns and not clears_floor:
        verdict = "LITE_COLLAPSE_PERSISTS"
        vmsg = ("LITE_COLLAPSE_PERSISTS: primary %s genuinely LEARNS (pred_drop=%s) but rep_std=%s still < %.3f "
                "-- collapse is scale/data at this proxy budget, not the target framing; fuller build needed. "
                "2x2: %s." % (primary, _fmt(p_drop), _fmt(p_rs), COLLAPSE_REP_STD_FLOOR,
                {a: {"rep_std": table[a]["rep_std"], "pred_drop": table[a]["pred_drop"]} for a in present}))
    else:
        verdict = "LITE_MISSPECIFIED"
        vmsg = ("LITE_MISSPECIFIED: primary %s learns=%s clears_floor=%s beats_random=%s -- inconclusive/"
                "broken-test guard (did not cleanly pass or fail-by-learned-collapse). mis-spec arms: %s. 2x2: %s."
                % (primary, learns, clears_floor, beats_random, misspec,
                   {a: {"rep_std": table[a]["rep_std"], "cos": table[a]["cos"], "pred_drop": table[a]["pred_drop"]} for a in present}))

    summary = dict(all_trained=all_trained, ckpts_saved=ckpts_saved, primary_arm=primary,
                   primary_rep_std=p_rs, primary_cos=p_cos, primary_pred_drop=p_drop,
                   learns=learns, clears_collapse_floor=clears_floor, beats_random=beats_random,
                   hard_pass=hard_pass, misspecified_arms=misspec,
                   random_rep_std=rand_rs, random_cos=rand_cos, collapse_floor=COLLAPSE_REP_STD_FLOOR,
                   learn_min_drop=LEARN_MIN_DROP, arm_table=table,
                   ckpt_paths={a: {k: per_seed[k].get("ckpt_paths", {}).get(a) for k in seeds} for a in present})
    gates = [record_gate("lite_primary_learns", p_drop if p_drop is not None else 0.0, LEARN_MIN_DROP, ">=",
                         note="PRIMARY %s pred_loss drop >= %.2f (task is learnable, not flat)" % (primary, LEARN_MIN_DROP)),
             record_gate("lite_primary_clears_collapse_floor", p_rs if p_rs is not None else 0.0,
                         COLLAPSE_REP_STD_FLOOR, ">=", note="PRIMARY rep_std >= %.3f" % COLLAPSE_REP_STD_FLOOR),
             record_gate("lite_primary_beats_random", 1.0 if beats_random else 0.0, 1.0, "==",
                         note="PRIMARY rep_std>RANDOM AND cos<RANDOM (beat-random backstop)"),
             record_gate("lite_no_misspecified_arm", 0.0 if misspec else 1.0, 1.0, "==",
                         note="no trained causal arm worse-than-random (mis-spec backstop)")]
    return verdict, vmsg, summary, gates


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def build_verdict(per_seed, cfg):
    seeds = sorted(per_seed.keys(), key=lambda k: int(k))

    def by_seed(arm, key):
        out = []
        for k in seeds:
            a = per_seed[k].get("arms", {}).get(arm, {})
            out.append(a.get(key))
        return out

    def mean(v):
        vv = [x for x in v if x is not None]
        return float(np.mean(vv)) if vv else None

    gg = {a: by_seed(a, "graded_geometry") for a in ARMS}
    probe = {a: by_seed(a, "heldout_probe") for a in ARMS}
    rel = {a: by_seed(a, "relational_auc") for a in ARMS}
    rep_std = {a: by_seed(a, "rep_std") for a in ARMS}
    # defensive .get on the arm: OBJECTIVE_ARMS now includes the 2026-08-01 new-objective arms, which are
    # only run in the LITE collapse-test (LITE_ARMS), NOT in the FULL/selftest ARMS -- skip absent arms.
    min_tgt_std = {a: [((per_seed[k].get("arms", {}).get(a, {}).get("train_diag") or {}).get("min_target_std"))
                       for k in seeds] for a in OBJECTIVE_ARMS if any(a in per_seed[k].get("arms", {}) for k in seeds)}

    m_gg = {a: mean(gg[a]) for a in ARMS}
    m_probe = {a: mean(probe[a]) for a in ARMS}
    m_rel = {a: mean(rel[a]) for a in ARMS}
    m_repstd = {a: mean(rep_std[a]) for a in ARMS}

    # per-seed deltas for the "1 of 2 seeds with other non-negative" rule (ARM_LPC_CAUSAL primary,
    # 2026-07-30 amendment). NOTE (honest flag): this cell's OWN HARD_PASS/FAIL bands below are the
    # PRIOR representation-quality lever's own criterion (graded_geometry Spearman vs MLM/RANDOM) --
    # UNCHANGED and still reported/gated here as a bonus rep-quality signal, but per the spec's own
    # "FAIR-TEST" section, the DECISIVE claim for the causal-encoder amendment is the SEPARATE
    # cross-voice syntax-role probe (exp_syntactic_role_agent_patient_voice_probe_v1.py, path-swapped
    # onto this cell's ARM_LPC_CAUSAL ckpt) -- this cell's verdict below does NOT itself certify or
    # refute the role-probe hypothesis.
    PRIMARY = ARM_LPC_CAUSAL

    def deltas(arm, ref):
        out = []
        for i in range(len(seeds)):
            va, vr = gg[arm][i], gg[ref][i]
            out.append((va - vr) if (va is not None and vr is not None) else None)
        return out

    d_mlm = deltas(PRIMARY, ARM_MLM)
    d_rand = deltas(PRIMARY, ARM_RANDOM)
    valid_pairs = [i for i in range(len(seeds)) if d_mlm[i] is not None and d_rand[i] is not None]

    def _one_of_n(dm, dr):
        if not valid_pairs:
            return False
        any_pass = any((dm[i] >= HP_GG_OVER_MLM and dr[i] >= HP_GG_OVER_RANDOM) for i in valid_pairs)
        others_nonneg = all((dm[i] >= 0.0 and dr[i] >= 0.0) for i in valid_pairs)
        return any_pass and others_nonneg

    lpc_hp_geometry = _one_of_n(d_mlm, d_rand)
    probe_no_regress = (m_probe[PRIMARY] is not None and m_probe[ARM_MLM] is not None
                        and m_probe[PRIMARY] >= m_probe[ARM_MLM] - PROBE_NOREGRESS_EPS)
    # collapse guard: frozen rep dispersion + training-time target std both above floor
    no_collapse_reps = (m_repstd[PRIMARY] is not None and m_repstd[PRIMARY] >= COLLAPSE_REP_STD_FLOOR)
    m_mintgt_lpc = mean(min_tgt_std.get(PRIMARY, []))
    no_collapse_train = (m_mintgt_lpc is not None and m_mintgt_lpc >= COLLAPSE_TARGET_STD_FLOOR)
    collapsed = (not no_collapse_reps) or (not no_collapse_train)

    # no-effect: causal arm ties BOTH MLM and RANDOM within eps on graded geometry
    no_effect = False
    if m_gg[PRIMARY] is not None and m_gg[ARM_MLM] is not None and m_gg[ARM_RANDOM] is not None:
        no_effect = (abs(m_gg[PRIMARY] - m_gg[ARM_MLM]) < NO_EFFECT_EPS
                     and abs(m_gg[PRIMARY] - m_gg[ARM_RANDOM]) < NO_EFFECT_EPS)

    # power
    min_gg_nq = min([per_seed[k]["arms"][PRIMARY].get("graded_geometry_nq", 0) for k in seeds] or [0])

    # ablations (both UNGATED, reported only): does temporal-contiguity add over bidirectional-LPC?
    # does the causal amendment beat its own bidirectional control (spec anchor #2)?
    tc_delta = (m_gg[ARM_LPC_TC] - m_gg[ARM_LPC_BIDIR]) if (m_gg[ARM_LPC_TC] is not None and m_gg[ARM_LPC_BIDIR] is not None) else None
    causal_vs_bidir_delta = (m_gg[PRIMARY] - m_gg[ARM_LPC_BIDIR]) if (m_gg[PRIMARY] is not None and m_gg[ARM_LPC_BIDIR] is not None) else None

    gates = []
    gates.append(record_gate("lpc_causal_gg_over_mlm", (m_gg[PRIMARY] - m_gg[ARM_MLM]) if (m_gg[PRIMARY] is not None and m_gg[ARM_MLM] is not None) else -9.0,
                             HP_GG_OVER_MLM, ">=", note="ARM_LPC_CAUSAL-ARM_MLM graded geometry (mean)"))
    gates.append(record_gate("lpc_causal_gg_over_random", (m_gg[PRIMARY] - m_gg[ARM_RANDOM]) if (m_gg[PRIMARY] is not None and m_gg[ARM_RANDOM] is not None) else -9.0,
                             HP_GG_OVER_RANDOM, ">=", note="ARM_LPC_CAUSAL-ARM_RANDOM graded geometry (mean)"))
    gates.append(record_gate("probe_no_regress", 1.0 if probe_no_regress else 0.0, 1.0, "==",
                             note="held-out probe >= MLM - %.2f" % PROBE_NOREGRESS_EPS))
    gates.append(record_gate("no_collapse_reps", m_repstd[PRIMARY] if m_repstd[PRIMARY] is not None else -1.0,
                             COLLAPSE_REP_STD_FLOOR, ">=", note="frozen rep per-dim std floor"))
    gates.append(record_gate("no_collapse_train", m_mintgt_lpc if m_mintgt_lpc is not None else -1.0,
                             COLLAPSE_TARGET_STD_FLOOR, ">=", note="training min target-embedding std floor"))
    gates.append(record_gate("power_min_gg_query", float(min_gg_nq), float(MIN_QUERY_TASKS), ">=",
                             note="graded-geometry query power floor"))

    run_mode = cfg["run_mode"]
    if run_mode in ("selftest", "smoke"):
        ran_ok = all(m_gg[a] is not None for a in ARMS) and all(m_repstd[a] is not None for a in ARMS)
        verdict = "SMOKE_PASS" if ran_ok else "SMOKE_INCOMPLETE"
        vmsg = ("SMOKE run_mode=%s gg[CAUSAL=%s BIDIR=%s TC=%s MLM=%s RAND=%s] probe[CAUSAL=%s MLM=%s] "
                "rel[CAUSAL=%s MLM=%s] rep_std[CAUSAL=%s RAND=%s] min_tgt_std_CAUSAL=%s tc_delta=%s "
                "causal_vs_bidir=%s gg_nq_min=%d"
                % (run_mode, _fmt(m_gg[PRIMARY]), _fmt(m_gg[ARM_LPC_BIDIR]), _fmt(m_gg[ARM_LPC_TC]),
                   _fmt(m_gg[ARM_MLM]), _fmt(m_gg[ARM_RANDOM]),
                   _fmt(m_probe[PRIMARY]), _fmt(m_probe[ARM_MLM]), _fmt(m_rel[PRIMARY]), _fmt(m_rel[ARM_MLM]),
                   _fmt(m_repstd[PRIMARY]), _fmt(m_repstd[ARM_RANDOM]), _fmt(m_mintgt_lpc), _fmt(tc_delta),
                   _fmt(causal_vs_bidir_delta), min_gg_nq))
    else:
        if collapsed:
            verdict = "FAIL_BY_COLLAPSE"
            vmsg = ("FAIL_BY_COLLAPSE: ARM_LPC_CAUSAL variance collapsed (rep_std=%s floor=%.3f; "
                    "min_target_std=%s floor=%.3f). Mechanism class NOT refuted; retune VICReg/EMA "
                    "or use --co-scaled (capacity-ratio). gg[CAUSAL=%s BIDIR=%s MLM=%s RAND=%s]"
                    % (_fmt(m_repstd[PRIMARY]), COLLAPSE_REP_STD_FLOOR, _fmt(m_mintgt_lpc),
                       COLLAPSE_TARGET_STD_FLOOR, _fmt(m_gg[PRIMARY]), _fmt(m_gg[ARM_LPC_BIDIR]),
                       _fmt(m_gg[ARM_MLM]), _fmt(m_gg[ARM_RANDOM])))
        elif min_gg_nq < MIN_QUERY_TASKS:
            verdict = "HARD_FAIL_UNDERPOWERED"
            vmsg = ("UNDERPOWERED: graded-geometry min query count %d < %d." % (min_gg_nq, MIN_QUERY_TASKS))
        elif lpc_hp_geometry and probe_no_regress:
            verdict = "HARD_PASS"
            vmsg = ("HARD_PASS (rep-quality bonus band, NOT the decisive role-probe claim -- see "
                    "separate probe cell): causal-LPC encoder BEATS MLM by >=+%.2f AND random-init by "
                    ">=+%.2f on graded-geometry (>=1/2 seeds, other non-negative), probe no-regress. "
                    "gg[CAUSAL=%s BIDIR=%s TC=%s MLM=%s RAND=%s] probe[CAUSAL=%s MLM=%s RAND=%s] "
                    "rel[CAUSAL=%s MLM=%s] d_mlm=%s d_rand=%s tc_ablation_delta=%s "
                    "causal_vs_bidir_delta=%s rep_std_CAUSAL=%s"
                    % (HP_GG_OVER_MLM, HP_GG_OVER_RANDOM, _fmt(m_gg[PRIMARY]), _fmt(m_gg[ARM_LPC_BIDIR]),
                       _fmt(m_gg[ARM_LPC_TC]), _fmt(m_gg[ARM_MLM]), _fmt(m_gg[ARM_RANDOM]),
                       _fmt(m_probe[PRIMARY]), _fmt(m_probe[ARM_MLM]), _fmt(m_probe[ARM_RANDOM]),
                       _fmt(m_rel[PRIMARY]), _fmt(m_rel[ARM_MLM]),
                       str([_fmt(x) for x in d_mlm]), str([_fmt(x) for x in d_rand]), _fmt(tc_delta),
                       _fmt(causal_vs_bidir_delta), _fmt(m_repstd[PRIMARY])))
        elif no_effect:
            verdict = "HARD_FAIL_NO_EFFECT"
            vmsg = ("HARD_FAIL_NO_EFFECT: causal-LPC ties BOTH MLM and random-init within +/-%.2f on "
                    "graded-geometry (rep-quality bonus band; does NOT itself decide the role-probe "
                    "hypothesis). gg[CAUSAL=%s BIDIR=%s MLM=%s RAND=%s] probe[CAUSAL=%s MLM=%s] "
                    "causal_vs_bidir=%s"
                    % (NO_EFFECT_EPS, _fmt(m_gg[PRIMARY]), _fmt(m_gg[ARM_LPC_BIDIR]), _fmt(m_gg[ARM_MLM]),
                       _fmt(m_gg[ARM_RANDOM]), _fmt(m_probe[PRIMARY]), _fmt(m_probe[ARM_MLM]),
                       _fmt(causal_vs_bidir_delta)))
        else:
            verdict = "MIDDLE_BAND"
            vmsg = ("MIDDLE_BAND: real-but-below-band. gg[CAUSAL=%s BIDIR=%s TC=%s MLM=%s RAND=%s] "
                    "d_mlm=%s d_rand=%s probe[CAUSAL=%s MLM=%s] tc_delta=%s causal_vs_bidir=%s "
                    "(HP needs CAUSAL-MLM>=%.2f AND CAUSAL-RAND>=%.2f, 1/2 seeds)"
                    % (_fmt(m_gg[PRIMARY]), _fmt(m_gg[ARM_LPC_BIDIR]), _fmt(m_gg[ARM_LPC_TC]),
                       _fmt(m_gg[ARM_MLM]), _fmt(m_gg[ARM_RANDOM]),
                       str([_fmt(x) for x in d_mlm]), str([_fmt(x) for x in d_rand]),
                       _fmt(m_probe[PRIMARY]), _fmt(m_probe[ARM_MLM]), _fmt(tc_delta),
                       _fmt(causal_vs_bidir_delta), HP_GG_OVER_MLM, HP_GG_OVER_RANDOM))

    summary = dict(
        graded_geometry={a: m_gg[a] for a in ARMS},
        heldout_probe={a: m_probe[a] for a in ARMS},
        relational_auc={a: m_rel[a] for a in ARMS},
        rep_std={a: m_repstd[a] for a in ARMS},
        min_target_std_causal=m_mintgt_lpc,
        min_target_std_lpc_tc=mean(min_tgt_std.get(ARM_LPC_TC, [])),
        lpc_gg_minus_mlm=(m_gg[PRIMARY] - m_gg[ARM_MLM]) if (m_gg[PRIMARY] is not None and m_gg[ARM_MLM] is not None) else None,
        lpc_gg_minus_random=(m_gg[PRIMARY] - m_gg[ARM_RANDOM]) if (m_gg[PRIMARY] is not None and m_gg[ARM_RANDOM] is not None) else None,
        tc_ablation_delta=tc_delta,
        causal_vs_bidir_delta=causal_vs_bidir_delta,
        per_seed_d_mlm=d_mlm, per_seed_d_rand=d_rand,
        collapsed=collapsed, no_effect=no_effect, min_gg_query=int(min_gg_nq),
        note="HARD_PASS/FAIL bands above are the rep-quality (graded_geometry) bonus criterion; the "
             "DECISIVE causal-encoder claim is the separate syntax-role cross-voice probe cell.",
    )
    return verdict, vmsg, summary, gates


# ---------------------------------------------------------------------------
# CUDA device-safety audit (runs the identical device-routed step; cuda when present)
# ---------------------------------------------------------------------------
def _cuda_safety_audit(device):
    """Run 2 end-to-end LPC steps on `device` with a tiny synthetic stream; assert finite + on-device.
    On cuda this catches the exact device bug class (cpu-tensor/Generator used with cuda). On cpu it
    exercises the identical device-routed code path (all tensors created with device=...)."""
    spec = dict(size=64, pad=0, mask=2, unk=1)
    cfg = dict(max_len=16, d_model=16, n_layers=1, n_heads=2, ffn_mult=2, mlm_steps=2, mlm_batch=8,
               mlm_lr=1e-3, lpc_mask_frac=0.25, lpc_ema_m=0.99, lpc_var_coef=1.0, lpc_cov_coef=0.04,
               lpc_pred_hidden_mult=2, lpc_tc_coef=0.5, lpc_tc_alpha=0.1,
               role_gate_theta=0.5, role_gate_tau=0.1, lpc_clause_coef=0.5)
    rng = np.random.default_rng(0)
    stream = rng.integers(3, 64, size=16 * 40).astype(np.int64)
    tmp = os.path.join(get_output_dir(ANCHOR_NAME), "_cuda_audit_tmp")
    os.makedirs(tmp, exist_ok=True)
    # temporal-contiguity path is the one with a host<->device crossing -> exercise it explicitly
    model, diag = lpc_train(stream, spec, cfg, device, seed=0, out_dir=tmp, hb_total=2, temporal_contiguity=True)
    dev_ok = all(p.device.type == device.type for p in model.parameters())
    assert dev_ok, "device audit: model params not on run device %s" % device
    assert np.isfinite(diag["final_pred_loss"]), "device audit: non-finite pred loss on %s" % device
    # causal path (2026-07-30) has its OWN host<->device crossing (clause-head next-window indexing via
    # sel_next.cpu().numpy()) -> exercise it explicitly too, same discipline as the TC path above.
    model_c, diag_c = lpc_train(stream, spec, cfg, device, seed=0, out_dir=tmp, hb_total=2, causal=True)
    dev_ok_c = all(p.device.type == device.type for p in model_c.parameters())
    assert dev_ok_c, "device audit: causal-path model params not on run device %s" % device
    assert np.isfinite(diag_c["final_pred_loss"]), "device audit: causal-path non-finite pred loss on %s" % device
    assert np.isfinite(diag_c["final_clause_loss"]), "device audit: causal-path non-finite clause loss on %s" % device
    # OBJECTIVE PIVOT 2026-08-01: exercise the NEW causal_realtarget_train path ON-DEVICE (real-target +
    # Barlow) so the queue_add REMOTE self-test (which runs on the GPU box's CUDA) actually EXERCISES the
    # new GPU/AMP code path before any full dispatch -- closing the "CPU self-test passes, real GPU run
    # crashes" gap (root-cause hardening after run-4's silent GPU death). All 3 dispatched new combos are
    # covered (real_emb/ema_latent x barlow/vicreg subset) so any combo-specific GPU/AMP/index bug fails
    # the self-test (blocks the ship) instead of a full run. cfg already carries lpc_var_coef_causal/
    # lpc_barlow_lambda_od (audit cfg extended below).
    rt_diags = {}
    for _tm, _rm, _tk in (("sampled_softmax", "barlow", None), ("sampled_softmax", "vicreg", None),
                          ("ema_latent", "barlow", None), ("sampled_softmax", "barlow", 4)):
        m_rt, d_rt = causal_realtarget_train(stream, spec, cfg, device, seed=0, out_dir=tmp, hb_total=2,
                                             target_mode=_tm, reg_mode=_rm, sparse_topk=_tk)
        _lbl = "%s+%s%s" % (_tm, _rm, "+topk%d" % _tk if _tk else "")
        assert all(p.device.type == device.type for p in m_rt.parameters()), \
            "device audit: realtarget[%s] params not on run device %s" % (_lbl, device)
        assert np.isfinite(d_rt["final_pred_loss"]), \
            "device audit: realtarget[%s] non-finite pred loss on %s" % (_lbl, device)
        assert np.isfinite(d_rt["final_train_rep_std"]), \
            "device audit: realtarget[%s] non-finite rep_std on %s" % (_lbl, device)
        rt_diags[_lbl] = float(d_rt["final_pred_loss"])
    return dict(device=device.type, cuda_tested=(device.type == "cuda"),
                final_pred_loss=diag["final_pred_loss"], params_on_device=(dev_ok and dev_ok_c),
                causal_final_pred_loss=diag_c["final_pred_loss"],
                causal_final_clause_loss=diag_c["final_clause_loss"],
                realtarget_final_pred_loss=rt_diags)


def _selftest_assertions(per_seed, summary, verdict, out_dir, audit):
    assert len(per_seed) >= 1, "no seed completed"
    sk = sorted(per_seed.keys())[0]
    r = per_seed[sk]
    for arm in ARMS:
        assert arm in r["arms"], "arm missing: %s" % arm
        a = r["arms"][arm]
        assert a["graded_geometry"] is not None, "graded_geometry missing for %s" % arm
        assert a["rep_std"] is not None, "rep_std missing for %s" % arm
    # loss DESCENDS on the tiny overfit -- only for OBJECTIVE_ARMS actually run in this selftest (the
    # 2026-08-01 new-objective arms run in LITE, not the selftest ARMS set; exercised in _selftest_plumbing).
    for arm in [a for a in OBJECTIVE_ARMS if a in r["arms"]]:
        td = r["arms"][arm]["train_diag"]
        assert td["final_pred_loss"] < td["init_pred_loss"], \
            "%s pred loss did not descend: init=%.4f final=%.4f" % (arm, td["init_pred_loss"], td["final_pred_loss"])
        # NO COLLAPSE on the tiny overfit (variance floor holds)
        assert td["min_target_std"] >= COLLAPSE_TARGET_STD_FLOOR, \
            "%s target embedding collapsed: min_target_std=%.4f < %.3f" % (arm, td["min_target_std"], COLLAPSE_TARGET_STD_FLOOR)
    # temporal-contiguity actually fired (aux loss computed)
    assert r["arms"][ARM_LPC_TC]["train_diag"].get("mean_tc_loss") is not None, "TC aux loss did not fire"
    # causal amendment (2026-07-30): clause-head loss descends + role gate fires + causal flag recorded
    causal_diag = r["arms"][ARM_LPC_CAUSAL]["train_diag"]
    assert causal_diag.get("causal") is True, "ARM_LPC_CAUSAL train_diag missing causal=True flag"
    assert causal_diag["final_clause_loss"] < causal_diag["init_clause_loss"], \
        "clause-head loss did not descend: init=%.4f final=%.4f" % (
            causal_diag["init_clause_loss"], causal_diag["final_clause_loss"])
    rr = causal_diag.get("role_gate_mean_replace_rate")
    assert rr is not None, "role_gate_mean_replace_rate missing (hold-then-revise diagnostic did not run)"
    # bidir arm must NOT carry causal-only diagnostics (proves the two training paths genuinely differ)
    bidir_diag = r["arms"][ARM_LPC_BIDIR]["train_diag"]
    assert bidir_diag.get("causal") is False, "ARM_LPC_BIDIR unexpectedly ran the causal path"
    assert bidir_diag.get("role_gate_mean_replace_rate") is None, \
        "ARM_LPC_BIDIR should not carry a role-gate diagnostic (causal-only pass)"
    # arms differ (bit-level)
    assert len(set(r["arm_digests"].values())) == len(ARMS), "arms not all distinct"
    # cuda-safety audit ran
    assert audit["params_on_device"], "cuda-safety audit failed device parity"
    assert verdict == "SMOKE_PASS", "selftest did not complete arms (%s)" % verdict


# ---------------------------------------------------------------------------
# Plumbing self-tests (fast, no corpus): headroom projection + arm-ckpt round-trip + (seed,arm) resume
# ---------------------------------------------------------------------------
def _selftest_plumbing():
    import shutil
    import tempfile
    from tokenizers import Tokenizer, models, pre_tokenizers, trainers

    # (a) Fix C headroom projection branch logic
    fast = _headroom_projection(20000.0, 10_000_000, N_DATA_PASSES, DATA_PREP_TIME_CEILING_S)
    assert fast["verdict"] == "DATA_PREP_OK", fast
    slow = _headroom_projection(500.0, 10_000_000, N_DATA_PASSES, DATA_PREP_TIME_CEILING_S)
    assert slow["verdict"] == "DATA_PREP_TOO_SLOW", slow
    edge_rate = (10_000_000 * N_DATA_PASSES) / float(DATA_PREP_TIME_CEILING_S)   # projected == ceiling
    assert _headroom_projection(edge_rate, 10_000_000, N_DATA_PASSES,
                                DATA_PREP_TIME_CEILING_S)["verdict"] == "DATA_PREP_OK"

    # (b) Fix 2d arm-ckpt round-trips into a fresh TinyTransformer (FrozenV2Encoder-shape loader)
    tmp = tempfile.mkdtemp(prefix="lpc_ckpt_selftest_")
    try:
        spec = dict(size=64, pad=0, unk=1, mask=2)
        cfg = dict(max_len=8, d_model=16, n_layers=1, n_heads=2, ffn_mult=2, run_mode="selftest")
        m = TinyTransformer(spec["size"], cfg["max_len"], cfg["d_model"], cfg["n_layers"],
                            cfg["n_heads"], cfg["ffn_mult"], spec["pad"])
        tok = Tokenizer(models.BPE(unk_token="[UNK]"))
        tok.pre_tokenizer = pre_tokenizers.Whitespace()
        tr = trainers.BpeTrainer(vocab_size=64, special_tokens=["[PAD]", "[UNK]", "[MASK]"],
                                 show_progress=False)
        tok.train_from_iterator(["red cat sat", "blue dog ran", "green fish swam"], trainer=tr)
        path = _save_arm_ckpt(tmp, 7, ARM_LPC_CAUSAL, m, tok, spec, cfg)
        assert path is not None, "arm-ckpt save returned None"
        ck = torch.load(os.path.join(_REPO, path), map_location="cpu", weights_only=False)
        for kk in ("state_dict", "spec", "model_cfg", "tokenizer_json", "seed", "arm"):
            assert kk in ck, "arm-ckpt missing key %s" % kk
        mc = ck["model_cfg"]
        for kk in ("vocab", "max_len", "d_model", "n_layers", "n_heads", "ffn_mult", "pad_id"):
            assert kk in mc, "model_cfg missing %s" % kk
        m2 = TinyTransformer(mc["vocab"], mc["max_len"], mc["d_model"], mc["n_layers"],
                             mc["n_heads"], mc["ffn_mult"], mc["pad_id"])
        m2.load_state_dict(ck["state_dict"])            # bit-identical to what FrozenV2Encoder does
        _ = Tokenizer.from_str(ck["tokenizer_json"])
        assert ck["arm"] == ARM_LPC_CAUSAL and int(ck["seed"]) == 7
        # 2026-08-01 amendment: ARM_RANDOM now saves a real ckpt too (needed as the untrained-floor
        # control for the syntax-role probe's bundled fair test) -- verify it round-trips identically.
        rnd_path = _save_arm_ckpt(tmp, 7, ARM_RANDOM, m, tok, spec, cfg)
        assert rnd_path is not None, "ARM_RANDOM must now save a real ckpt (2026-08-01 amendment)"
        rnd_ck = torch.load(os.path.join(_REPO, rnd_path), map_location="cpu", weights_only=False)
        assert rnd_ck["arm"] == ARM_RANDOM and int(rnd_ck["seed"]) == 7
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # (c) Fix 2c (seed, arm) checkpoint/resume: crash after 2 arms -> resume skips exactly those 2
    tmp2 = tempfile.mkdtemp(prefix="lpc_resume_selftest_")
    try:
        def _fake(a):
            return dict(arm_result={"graded_geometry": 0.5}, held_rep_digest="dg_" + a, ckpt_path=None)
        for a in ARMS[:2]:
            ckpt.record_unit(tmp2, ckpt.unit_key(7, a), _fake(a))
        done = ckpt.completed_units(tmp2)
        assert done == {ckpt.unit_key(7, a) for a in ARMS[:2]}, done
        n_skip = 0
        for a in ARMS:
            if ckpt.unit_key(7, a) in done:
                n_skip += 1
                continue
            ckpt.record_unit(tmp2, ckpt.unit_key(7, a), _fake(a))
        assert n_skip == 2, "resume did not skip exactly 2 completed arms (%d)" % n_skip
        assert len(ckpt.load_units(tmp2)) == len(ARMS), "resume did not complete remaining arms"
        assert ckpt.unit_key(7, ARM_LPC_CAUSAL) != ckpt.unit_key(13, ARM_LPC_CAUSAL), "seed-scoped keys collide"
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)

    # (d) Causal-mask correctness (spec 2a): position t must NOT see position t+1..L-1. Change a FUTURE
    # token's id and assert the causal encoder's output at all EARLIER positions is bit-identical; the
    # bidirectional (_contextual) path, by contrast, MUST change (control -- proves the test itself has
    # power, not just a numerically-quiet no-op).
    spec2 = dict(size=64, pad=0, unk=1, mask=2)
    m3 = TinyTransformer(spec2["size"], 12, 16, 1, 2, 2, spec2["pad"])
    m3.eval()
    rng2 = np.random.default_rng(1)
    base_ids = torch.from_numpy(rng2.integers(3, 64, size=(2, 12)).astype(np.int64))
    changed_ids = base_ids.clone()
    changed_ids[:, -1] = (changed_ids[:, -1] + 7) % 61 + 3          # perturb ONLY the LAST token
    with torch.no_grad():
        h_base, _ = _causal_contextual(m3, base_ids)
        h_changed, _ = _causal_contextual(m3, changed_ids)
        hb_base, _ = m3._contextual(base_ids)
        hb_changed, _ = m3._contextual(changed_ids)
    earlier = slice(0, -1)
    assert torch.allclose(h_base[:, earlier], h_changed[:, earlier], atol=1e-6), \
        "CAUSAL_LEAKAGE: perturbing the LAST token changed an earlier position's causal latent"
    assert not torch.allclose(hb_base[:, earlier], hb_changed[:, earlier], atol=1e-6), \
        "control failed: bidirectional path did not change on the same perturbation (test has no power)"
    assert not torch.allclose(h_base[:, -1], h_changed[:, -1], atol=1e-6), \
        "causal path did not react to a change at its OWN position (mask over-restrictive)"

    # (e) Hold-then-revise gate (spec 2b): low PE -> HOLD (h_role ~ unchanged); PE spike -> REPLACE
    # (h_role ~ new_val), bistable at the low tau this cell uses (ROLE_GATE_TAU family, self-test uses
    # tau=0.1 to match cfg default).
    h_role0 = torch.tensor([[1.0, 0.0, 0.0, 0.0]])
    new_val = torch.tensor([[0.0, 1.0, 0.0, 0.0]])
    low_pe = torch.tensor([0.01])     # well below theta=0.5 -> HOLD
    high_pe = torch.tensor([0.95])    # well above theta=0.5 -> REPLACE
    theta, tau = 0.5, 0.1
    h_hold, b_hold = hold_then_revise_gate(h_role0, new_val, low_pe, theta, tau)
    h_replace, b_replace = hold_then_revise_gate(h_role0, new_val, high_pe, theta, tau)
    assert float(b_hold[0]) < 0.05, "gate did not HOLD on low PE (boundary=%.4f)" % float(b_hold[0])
    assert float(b_replace[0]) > 0.95, "gate did not REPLACE on PE spike (boundary=%.4f)" % float(b_replace[0])
    assert torch.allclose(h_hold, h_role0, atol=3e-2), "HOLD case moved h_role too far from its prior value"
    assert torch.allclose(h_replace, new_val, atol=3e-2), "REPLACE case did not swap to new_val on spike"
    # role_hypothesis_pass end-to-end: a sequence with one abrupt latent change should show a boundary spike
    seq = torch.zeros(1, 6, 4)
    seq[:, :3, 0] = 1.0            # first 3 positions: role A
    seq[:, 3:, 1] = 1.0            # last 3 positions: abrupt switch to role B
    _, btrace = role_hypothesis_pass(seq, theta=0.5, tau=0.1)
    assert btrace.shape == (1, 5), "role_hypothesis_pass boundary trace wrong shape: %s" % (btrace.shape,)
    assert float(btrace[0, 2]) > 0.9, \
        "gate did not fire a REPLACE spike at the abrupt role switch (boundary=%.4f)" % float(btrace[0, 2])
    assert float(btrace[0, 0]) < 0.1, \
        "gate incorrectly fired on a HOLD-case transition (boundary=%.4f)" % float(btrace[0, 0])

    # (f) OBJECTIVE PIVOT 2026-08-01: exercise the REAL causal_realtarget_train code path (F.1 real-code-
    # path discipline) for BOTH target modes x BOTH reg modes at tiny scale, and the Barlow helper. Asserts
    # each combo trains without error, returns a trained encoder + diag with the collapse telemetry, and
    # the loss path stays OOM-safe (the _assert_no_vocab_dim inside fires on a real call).
    import tempfile as _tf
    # Barlow helper: a decorrelated unit-variance batch -> near-zero loss; a collapsed (constant) batch ->
    # large on-diagonal penalty (variance far below 1).
    zdec = torch.randn(256, 8)
    zcol = torch.ones(256, 8) * 0.5
    assert float(_barlow_decorrelation(zdec)) < float(_barlow_decorrelation(zcol)), \
        "Barlow: collapsed batch must incur a larger loss than a decorrelated one"
    st_spec = dict(size=64, pad=0, unk=1, mask=2)
    st_cfg = dict(max_len=12, d_model=16, n_layers=1, n_heads=2, ffn_mult=2, mlm_batch=8, mlm_steps=3,
                  mlm_lr=3e-3, lpc_mask_frac=0.25, lpc_ema_m=0.99, lpc_var_coef=1.0, lpc_var_coef_causal=2.0,
                  lpc_cov_coef=0.04, lpc_barlow_lambda_od=0.005, lpc_pred_hidden_mult=2,
                  lpc_softmax_negatives=8, lpc_sparse_topk=4, run_mode="selftest")
    st_rng = np.random.default_rng(3)
    st_stream = st_rng.integers(3, 64, size=12 * 40).astype(np.int64)
    st_tmp = _tf.mkdtemp(prefix="realtarget_selftest_")
    try:
        for tmode in ("sampled_softmax", "ema_latent"):
            for rmode in ("barlow", "vicreg"):
                for tk in ((None, 4) if tmode == "sampled_softmax" and rmode == "barlow" else (None,)):
                    enc, diag = causal_realtarget_train(st_stream, st_spec, st_cfg, torch.device("cpu"), 7,
                                                        st_tmp, 12, target_mode=tmode, reg_mode=rmode, sparse_topk=tk)
                    assert isinstance(enc, TinyTransformer), "%s/%s did not return an encoder" % (tmode, rmode)
                    assert diag["target_mode"] == tmode and diag["reg_mode"] == rmode, "diag mode mismatch"
                    assert diag["external_target"] == (tmode == "sampled_softmax"), "external_target flag wrong"
                    assert diag["sparse_topk"] == (tk if tk else None), "sparse_topk flag wrong"
                    assert diag["pred_drop"] is not None and diag["n_steps"] == 3, "diag telemetry missing"
    finally:
        shutil.rmtree(st_tmp, ignore_errors=True)

    _log("PLUMBING SELF-TEST PASS (headroom projection + arm-ckpt round-trip + (seed,arm) resume + "
         "causal no-leakage + hold-then-revise gate + real-target/Barlow objective 2x2)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def _select_device():
    return torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")


def _parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--lite", action="store_true",
                    help="early-signal cfg (2026-07-30 REPURPOSED, 2026-08-01 EXTENDED for the "
                         "causal-vs-bidirectional-vs-random bundled small-proxy test): SAME architecture "
                         "as FULL, ~10x fewer steps + a smaller data subset; trains ARM_LPC_CAUSAL "
                         "(resumed, already checkpointed 2026-07-30) + ARM_LPC_BIDIR + ARM_RANDOM, ONE "
                         "seed (LITE_ARMS=[ARM_LPC_CAUSAL, ARM_LPC_BIDIR, ARM_RANDOM]); writes to "
                         "data/exp_%s_lite/ (a DISTINCT dir from the FULL run's data/exp_%s/, so it "
                         "never collides with the in-progress FULL GPU run's checkpoints/units.jsonl)."
                         % (ANCHOR_NAME, ANCHOR_NAME))
    ap.add_argument("--lite-steps", type=int, default=None,
                    help="override LITE_CFG['mlm_steps'] (only applies with --lite). MEASURED CPU cost "
                         "(this repo, 2026-07-30, 6 torch threads): ~14.6s/step for the LPC objective at "
                         "d_model=512/L=6 -- 6000 steps is CPU-infeasible (~24h+); this cfg is sized for "
                         "GPU. Use --lite-steps to shrink for a bounded CPU/remote_cpu_queue run if GPU "
                         "placement is unavailable.")
    ap.add_argument("--co-scaled", action="store_true",
                    help="capacity-ratio follow-up: smaller encoder (d=256,L=4) over the same tokens")
    ap.add_argument("--device", default=None)
    args = ap.parse_args()
    # Runner-dispatch support (2026-08-01): the production queue runner (runner_v2_prod.py) invokes
    # every cell as `[sys.executable, "-u", script_path]` with NO CLI flags at all -- only
    # HDLAB_EXP_NAME / HDLAB_RUN_MODE env vars are injected (see run_one()). A CLI-only --lite flag is
    # therefore UNREACHABLE via the standard queue_add.sh -> runner_v2_prod.py dispatch path (the
    # 2026-07-30 lite run was launched by a direct manual invocation, not through the queue). Auto-detect
    # lite mode from HDLAB_EXP_NAME (the queue entry name, set by the runner) so a queue entry literally
    # named "..._lite" dispatches into lite mode like every other run-mode suffix convention in this repo
    # (SH-5's own _selftest/_smoke suffix isolation is the same pattern, one layer up).
    if not args.lite and "_lite" in os.environ.get("HDLAB_EXP_NAME", ""):
        args.lite = True
    return args


def _anchor_dir_name(args):
    return (ANCHOR_NAME + "_lite") if args.lite else ANCHOR_NAME


def main(args):
    if args.self_test:
        cfg = dict(SELFTEST_CFG)
    elif args.smoke:
        cfg = dict(SMOKE_CFG)
    elif args.lite:
        cfg = dict(LITE_CFG)
        if args.lite_steps is not None:
            cfg["mlm_steps"] = int(args.lite_steps)
    else:
        cfg = dict(FULL_CFG)
    if args.co_scaled:
        cfg.update(FULL_COSCALED_OVERRIDE)

    out_dir = get_output_dir(_anchor_dir_name(args))
    os.makedirs(out_dir, exist_ok=True)
    _write_start_marker(out_dir, cfg["run_mode"], len(cfg["seeds"]))

    if args.self_test:
        _selftest_plumbing()

    device = torch.device(args.device) if args.device else _select_device()
    _log("run_mode=%s device=%s seeds=%s cuda=%s co_scaled=%s"
         % (cfg["run_mode"], device.type, cfg["seeds"], torch.cuda.is_available(), args.co_scaled))

    audit = _cuda_safety_audit(device)
    _log("cuda-safety audit: device=%s cuda_tested=%s final_pred_loss=%.4f params_on_device=%s"
         % (audit["device"], audit["cuda_tested"], audit["final_pred_loss"], audit["params_on_device"]))

    if not os.path.exists(ARC_CORPUS):
        raise FileNotFoundError("ARC corpus not found at %s (remote staging?)" % ARC_CORPUS)

    # ---- data-prep-headroom gate (Fix C): fail loud BEFORE any full data-prep/dispatch if too slow ----
    headroom = None
    if args.smoke:
        headroom = _data_prep_headroom(out_dir)
        _log("data_prep_headroom: %s | measured=%.0f lines/s | projected_full_dataprep=%.0fs "
             "(%.1fh) ceiling=%ds n_passes=%d (probe %d lines in %.1fs)"
             % (headroom["verdict"], headroom["measured_lines_per_sec"],
                headroom["projected_full_dataprep_s"], headroom["projected_full_dataprep_s"] / 3600.0,
                headroom["ceiling_s"], headroom["n_passes"], headroom["probe_lines"],
                headroom["probe_elapsed_s"]))
        if headroom["verdict"] == "DATA_PREP_TOO_SLOW":
            raise RuntimeError(
                "DATA_PREP_TOO_SLOW: projected full data-prep %.0fs (%.1fh) > ceiling %ds at measured "
                "%.0f lines/s -- REFUSING to green-light FULL GPU dispatch (env too slow / a per-line "
                "regression). Investigate before FULL."
                % (headroom["projected_full_dataprep_s"], headroom["projected_full_dataprep_s"] / 3600.0,
                   headroom["ceiling_s"], headroom["measured_lines_per_sec"]))

    _log("loading concept universe...")
    universe = load_concept_universe(cfg)
    _log("concept universe: K=%d single-token grounded+lexname concepts" % universe["K"])

    # ---- data-prep bundle cache (Fix D): reuse across crash/resume so arm-training crashes never
    # repeat the ~2-3h data-prep ----
    cache_path = _bundle_cache_path(out_dir, cfg)
    if os.path.exists(cache_path):
        _log("data-prep bundle cache HIT: %s (skip re-prep)" % os.path.basename(cache_path))
        bundle = _load_bundle_cache(cache_path)
    else:
        _log("preparing shared data (seed-independent: split, tokenizer, postings, stream, graph)...")
        bundle = prepare_data(cfg, universe, out_dir=out_dir)
        try:
            _save_bundle_cache(cache_path, bundle)
            _log("data-prep bundle cached: %s" % os.path.basename(cache_path))
        except (OSError, RuntimeError, ValueError) as e:
            _log("WARN bundle cache save failed (%s): %s" % (type(e).__name__, str(e)[:200]))

    for seed in cfg["seeds"]:
        res = run_one_seed(seed, cfg, device, out_dir, universe, bundle)
        write_partial(out_dir, seed, res)
        _log("seed=%d done in %.1fs" % (seed, res["elapsed_s"]))

    per_seed = aggregate_partials(out_dir, cfg["seeds"])
    if cfg["run_mode"] == "lite":
        verdict, vmsg, summary, gates = build_lite_verdict(per_seed, cfg)
    else:
        verdict, vmsg, summary, gates = build_verdict(per_seed, cfg)
    _log("VERDICT: %s" % verdict)
    _log(vmsg)

    metrics = dict(
        verdict=verdict, verdict_msg=vmsg, summary=vmsg,
        anchor_name=ANCHOR_NAME, run_mode=cfg["run_mode"],
        ts_iso=datetime.now(timezone.utc).isoformat(),
        device=device.type, cuda=bool(torch.cuda.is_available()), co_scaled=bool(args.co_scaled),
        n_seeds=len(cfg["seeds"]),
        results_summary=summary, per_seed={k: per_seed[k] for k in per_seed},
        cuda_safety_audit=audit,
        bands=dict(hp_gg_over_mlm=HP_GG_OVER_MLM, hp_gg_over_random=HP_GG_OVER_RANDOM,
                   probe_noregress_eps=PROBE_NOREGRESS_EPS, no_effect_eps=NO_EFFECT_EPS,
                   collapse_rep_std_floor=COLLAPSE_REP_STD_FLOOR,
                   collapse_target_std_floor=COLLAPSE_TARGET_STD_FLOOR, min_query=MIN_QUERY_TASKS),
        cardinality_ok=(len(per_seed) == len(cfg["seeds"])),
        expected_n_units=len(cfg["seeds"]),
        data_prep_headroom=headroom,
        mlm_reuse=dict(v2_ckpt_dir=os.path.relpath(V2_CKPT_DIR, _REPO),
                       budget_matched_steps=int(cfg["mlm_steps"]),
                       note="ARM_MLM reuses V2 ckpt at FULL (mlm_steps matched to V2 FULL=60000)"),
        checkpoint=dict(unit_granularity="(seed, arm)", helper="tools/exp_checkpoint.py",
                        dataprep_bundle_cache=os.path.basename(cache_path),
                        per_arm_ckpts={str(s): per_seed[s].get("ckpt_paths") for s in per_seed}),
        progress_logging="print_flush_true",
        start_marker_written=True, crash_diagnostic_present=True,
        final_metrics_atomicity="tmp_replace", defensive_error_checking="passed_all_4_patterns",
    )
    write_metrics(out_dir, metrics, results=list(per_seed.values()), gate_claims=gates)

    if args.self_test:
        _selftest_assertions(per_seed, summary, verdict, out_dir, audit)
        _log("SELF-TEST PASS")


if __name__ == "__main__":
    _args = _parse_args()
    _out = get_output_dir(_anchor_dir_name(_args))
    try:
        main(_args)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
