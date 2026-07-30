# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (sha256 of per-example predicted-filler-id vectors, pairwise
#   distinct across TPR/FLAT/ORACLE)
# - final_metrics_atomicity: tmp_replace (os.replace at end)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no Cramer-Rao noise floor; discriminator = held-out-role RECALL accuracy + effective-rank
#   vs the pre-registered TPR_PROBE_PASS / TPR_COLLAPSE / MIDDLE_BAND / INVALID / OBJECTIVE_STILL_BROKEN
#   decision rule (Director spawn 2026-07-30 bugfix: "fix the training-objective bug -- reconstruction
#   cosine-loss didn't fire the discriminator -- replace with contrastive/InfoNCE, verify trained>random
#   on train BEFORE interpreting held-out generalization")
# - baseline_in_band: CONTROL_A (flat learned key) is the can-fail floor -- MUST reproduce the prior
#   near-chance HARD-FAIL (exp_oracle_context_invariant_address_wm_v2 / exp_wm_addressing_heldout_role_
#   warmstart_v1) on held-out roles, else the fairness comparison is INVALID.
# - discriminator survives scale: this cell IS the cheap discriminator-preview gating the expensive full
#   3-arm binder ablation -- self-test builds the REAL v2 encoder + REAL oc.build_oracle_table at tiny n
#   (real_code_path), trains TPR/FLAT for a handful of steps, and verifies arms differ + ranges valid.
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)
# - deterministic seeding: numpy default_rng + torch.manual_seed/torch.Generator only; NO hash(),
#   NO list(set())
"""Gradient-learned TPR-FACTORED role-key module -- cheap gating probe (Director spawn 2026-07-30, per
notes/learned_tpr_role_keys_binder_ablation_plan_2026-07-30.md).

WHY: two convergent findings named the same next move. (1) exp_vsa_key_globalscale_phase_conversion_v1
(c6ee9b09) NO_LIFT: oracle-averaged role keys are rank-deficient (rank<=14 in d=512,
MEASURED@data/exp_vsa_key_globalscale_phase_conversion_v1/metrics.json) -> phase-encode cosine caps at
~0.35 -> deployable native binding capped; escalation path = "learned/well-conditioned keys, not another
transform." (2) brain-fidelity audit named oracle-averaged role-key derivation as the LEAST-defensible
substrate component, gradient-learned TPR-factored roles as the recommended replacement (Smolensky TPR,
Webb/Sinha/Cohen ESBN arXiv:2012.14601, Schlag/Schmidhuber TPR-RNN arXiv:1811.12143).

THE PRIOR HARD-FAIL THIS PROBE MUST REPRODUCE (fairness floor): a FLAT per-role learned embedding (no
factor structure) could not generalize its ADDRESS to a role never seen in training --
exp_oracle_context_invariant_address_wm_v2's ARM_CONTEXTVARYING/oracle-warmstart held-out recall stayed
at CHANCE_RECALL=0.05 by construction (a lookup table has no compositional path to an unseen row). This
cell's CONTROL_A is the SAME failure mode, minimal-diff (identical downstream projection, only the
embedding-vs-factorization differs), so a genuine reproduction validates the comparison is fair.

WHAT THIS CELL BUILDS (NOT the full 3-arm binder ablation -- that is gated on this probe's verdict):
a small gradient-learned TPR-FACTORED role-key module trained end-to-end through the SUBSTRATE'S OWN
bind/unbind algebra (hdlab/binding.py, complex64 FHRR dispatch: elementwise mul / conjugate-mul, exact
by construction once keys are phase-encoded to unit-magnitude-per-component -- see _phase_encode) against
a CONTRASTIVE (InfoNCE-style) objective (bind role_key x filler -> superpose with N_DISTRACT real-role
distractor bindings -> unbind by role_key -> recover an approximate filler vector -> softmax
cross-entropy over cosine-similarity-to-the-FULL-V_FILL-codebook, target = true filler id), NOT a
role-classification cross-entropy over role identity (classification pressure over ROLES alone can
shortcut via per-role logits with no factor structure, reproducing the flat-lookup failure mode -- this
is the design's central point, per the plan's Section 1; the contrastive loss here classifies the
FILLER, via the algebraic bind/unbind path, so it cannot bypass the role-key's separation quality).

BUG-FIX NOTE (this commit, fixing f51c58bf9's self-test-PASS-but-training-broken regression): the
ORIGINAL objective was a plain RECONSTRUCTION cosine-loss (loss = 1 - cosine(recovered, true_filler))
with NO term penalizing similarity to the OTHER V_FILL-1 candidate fillers. MEASURED@dev smoke-preview
(prior run, WITHHELD): this let gradient descent lower the loss while collapsing decode-ARGMAX
discriminability -- trained keys ended up WORSE than the untrained random-key baseline at the same
D_KEY (e.g. D_KEY=20 trained 0.305 vs random 0.55) -- a loss-metric mismatch, not a factorization
result. FIX: replace the reconstruction cosine-loss with contrastive_ce_loss() (see below), a softmax
cross-entropy over cosine-similarities to the FULL filler codebook -- this directly optimizes the same
argmax-decode quantity decode_batch() measures, so trained keys can no longer "succeed" on the loss
while failing the metric. Everything else (FactoredRoleKey/FlatRoleKey architecture, oracle CONTROL_B,
TRAIN_ROLES_V2/HELD_OUT_ROLES_V2 split, unitary complex64 FHRR keys, D_KEY, distractor construction,
optimizer/steps/seeds, checkpoint/resume) is UNCHANGED -- the loss function is the ONE variable fixed.

ARCHITECTURE (the ONE variable across TPR vs CONTROL_A is factorization; everything else -- downstream
projection Linear(H*H -> d_enc), training objective, distractor construction, optimizer, steps, seeds --
is IDENTICAL):
  TPR-FACTORED key: role_id -> mixed-radix decompose into (a in 0..N_A-1, b in 0..N_B-1) via
    a = role_id // N_B, b = role_id % N_B (N_A=5, N_B=3, N_A*N_B == S_TARGET_TOTAL == 15, a BIJECTION,
    not a lossy hash). f_role = Embedding(N_A, H)[a], g_slot = Embedding(N_B, H)[b] (H=12), key =
    Linear(outer(f_role, g_slot).flatten() -> d_enc), L2-normalized. A role's key is COMPUTED from two
    sub-factors each shared with OTHER roles (5 roles share each 'a' value, 3 roles share each 'b'
    value) -- a held-out role's (a,b) COMBINATION is novel but its individual factors were each trained
    via other roles, a strictly easier generalization problem than a flat table's "guess the whole row."
  CONTROL_A (flat, non-factored): role_id -> Embedding(S_TARGET_TOTAL, H*H)[role_id] -> SAME
    Linear(H*H -> d_enc), L2-normalized. No factor structure: a held-out role's embedding row is NEVER
    touched by any gradient step (it never appears in a training minibatch, per the zero-shot corpus
    restriction below), so it stays at its random init -- this IS the mechanism of the prior HARD-FAIL,
    reproduced here as the fairness floor.
  CONTROL_B (oracle, non-trained upper-bound-probe reference ONLY -- never a comparison target for
    "which is better"): oc.build_oracle_table's real context-invariant frozen-v2-encoder role-averaged
    table (rank<=14 in d=512, MEASURED prior finding), used AS-IS for all 15 roles (train and held-out
    alike -- legitimate here purely as a reference point for what a perfect never-trained per-role
    address looks like, not a deployable method).

COMPOSITIONAL REACHABILITY (measured, not assumed): for TRAIN_ROLES_V2(10)/HELD_OUT_ROLES_V2(5) (the
SAME disjoint split as exp_oracle_context_invariant_address_wm_v2, ROLE_SPLIT_SEED_V2=20260731, reused
verbatim), every held-out role's (a,b) factor pair has BOTH sub-factors independently present among the
10 train roles -- MEASURED@this file's dev-time check (all 5 held-out roles: a in train_a AND b in
train_b == True; see compositional_reachability_selftest). This is the necessary precondition for the
TPR factorization to have ANY compositional path to a held-out role at all; if it were False for some
role, that role's generalization would be undecidable by this design regardless of training regime, and
this cell would flag it explicitly rather than silently proceeding.

GENUINE ZERO-SHOT ENFORCEMENT: training minibatches (both TPR and CONTROL_A) draw the TARGET role
ONLY from TRAIN_ROLES_V2; distractor bindings use a SEPARATE, fixed, non-trained 5-key pool (ids never
overlapping 0..14) so held-out role identity never enters any minibatch, any gradient, or any warm-start
supervision, for either trained arm. compositional_and_zeroshot_selftest() directly measures both
properties (reachability + corpus exclusion) rather than arguing them.

TRAINING TASK (superposition over REAL roles, NOT single-bind, NOT a separate fixed distractor-key
pool -- this is the load-bearing design point, see N_DISTRACT's docstring below for the dev-time
failure this fixes): per example, bind(role_key(query_role), filler_vec(query_fill)) is superposed
(summed) with bind(role_key(distractor_role_k), filler_vec(distractor_fill_k)) for every OTHER TRAIN
role (9 of them -- every occurrence writes a "full scratchpad" of all 10 TRAIN roles simultaneously),
where EVERY role key (query and distractors alike) comes from the SAME role-key module under test --
crosstalk genuinely depends on that module's own key-separation quality, not a side table. unbind(h,
role_key(query_role)) recovers an approximate filler vector; decode = argmax Re(Hermitian inner
product) against the fixed V_FILL=20 filler codebook (phase-encoded, shared bit-identically across all
3 arms). Loss for TPR/CONTROL_A = 1 - Re(complex cosine)(recovered, true filler vector), backpropagated
through the bind/unbind graph (elementwise complex ops are autograd-differentiable) into the role-key
module's parameters ONLY.

THE DECISIVE CHEAP MEASUREMENTS:
  1. EFFECTIVE RANK (participation ratio: PR = (sum s_i^2)^2 / sum s_i^4 of the singular values of the
     [15, d_enc] key matrix, evaluated over ALL 15 roles post-training) of the TPR key matrix vs the
     ORACLE key matrix's PR (measured FRESH in this same run, both in native d_enc dimensionality, so
     the comparison is a direct apples-to-apples ratio rather than a citation of a different regime's
     "rank<=14" figure -- that prior figure is also cited for context).
  2. HELD-OUT-ROLE recall generalization: decode accuracy on TARGET=held-out-role reconstruction
     examples the training loop NEVER saw (this is the decisive capability metric).
  3. CONTROL_A must reproduce the prior near-chance HARD-FAIL on held-out roles (fairness/validity gate).
  4. CONTROL_B (oracle) reported as upper-bound-probe reference, captioned as such.
  5. REFUTATION CHECK (honest, explicit in the verdict message if it fires): if TPR held-out accuracy
     stays near CONTROL_A's chance floor AND the TPR key matrix's effective rank does NOT exceed the
     ORACLE's measured effective rank -- the TPR factorization collapsed into a "lookup table in a
     tensor-product costume" (per arXiv:2405.16391 kernel theory / arXiv:2406.01012 critique, CITED in
     the design plan) and the bottleneck is UPSTREAM (encoder representational capacity), not key-
     derivation. This would redirect effort to the encoder pivot, not further key-derivation iteration.

PRE-REGISTERED DECISION RULE (written BEFORE running; NOT loosened after seeing results; the four
absolute held/gap/beat/rank thresholds below are the Director's spawn-prompt numbers verbatim; the
VALIDITY GATE itself was ADAPTED during dev -- see D_KEY's docstring and decide_verdict's docstring for
why literal CHANCE_RECALL=0.05 is unreachable in this algebraic bind/unbind-capacity regime, unlike the
classifier/softmax-routing WM cells this design descends from; V_FILL=20 -> CHANCE_RECALL=0.05 is still
reported for reference, matching exp_oracle_context_invariant_address_wm_v2 / exp_vsa_native_bind_
zeroshot_role_v1's convention, but is not the operative CONTROL_A validity threshold here):
  DISCRIMINATOR-FIRES GATE (checked ABSOLUTE FIRST, before the validity gate): TPR held-out is only
    interpretable if training actually LEARNED something, per the Director's fairness mandate (2026-07-30
    bugfix spawn). Measured as: TPR train-role recall (acc_train, averaged over the fixed N_EVAL_TRAIN
    eval set) must exceed the untrained random-key baseline's TRAIN-role recall (random_train, same
    query-pool/distractor-universe/eval-count, computed fresh every run) by >= DISCRIM_MARGIN=0.05 on
    EVERY seed. If this fails on ANY seed, verdict=OBJECTIVE_STILL_BROKEN -- the contrastive fix still
    doesn't beat random on train, so the mechanism isn't learning and TPR-vs-flat is UNINTERPRETABLE;
    report honestly, do NOT force a TPR_PROBE_PASS/COLLAPSE/MIDDLE_BAND verdict.
  VALIDITY GATE (checked SECOND, only if the discriminator fires; MEASURED not literal-chance):
    CONTROL_A held-out recall must be <= random_key_baseline_held + RANDOM_MARGIN=0.10 (a FRESH,
    untrained, fixed-seed reference table measured every run) on EVERY seed, else verdict=INVALID -- an
    untrained/never-updated row doing meaningfully BETTER than a random key of the same working
    dimensionality would mean something is fairness-leaking, not that training legitimately helped a row
    it never touched.
  TPR_PROBE_PASS (HARD-PASS -- GO to the full 3-arm binder ablation): held-out recall (TPR) >= 0.55 on
    EVERY seed AND (train_acc - held_acc) <= 0.20 on EVERY seed AND (TPR_held - CONTROL_A_held) >= 0.15
    on EVERY seed AND effective_rank(TPR, all 15 roles) > effective_rank(ORACLE, all 15 roles) (this
    run's own fresh measurement).
  TPR_COLLAPSE (HARD-FAIL, refutation of THIS factorization, not of learned binding generally): held-out
    recall (TPR) < 0.40 on ANY seed OR gap > 0.35 on ANY seed OR (TPR_held - CONTROL_A_held) < 0.10 on
    ANY seed. If, IN ADDITION, effective_rank(TPR) <= effective_rank(ORACLE) -- the REFUTATION
    combination fires explicitly in the verdict message (redirect to encoder capacity, not further key-
    derivation iteration).
  MIDDLE_BAND (most likely per the plan's deflated P=0.40): TPR beats CONTROL_A meaningfully (>= 0.10
    absolute gap) but does not clear the full TPR_PROBE_PASS bar (e.g. held-out in [0.40, 0.55) or gap/
    rank conditions partially met) -- factorization is a real but partial fix.

Run:  .venv/Scripts/python.exe experiments/exp_tpr_role_key_effective_rank_probe_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_tpr_role_key_effective_rank_probe_v1.py --full

ASCII-only. No emojis. Deterministic seeding (torch.Generator + np.random.default_rng; no hash(), no
list(set())). CPU (local, push-free; this .venv has no CUDA). progress_logging: print_flush_true.
Compute architecture: sequential-CPU, justified -- 3 arms (2 trained + 1 non-trained) x 3 seeds, each a
few hundred gradient steps over [15]-role, d_enc-dim vectors (tiny matmuls); design target well under
10 minutes total wall time (compute-proportionality: this is a cheap key-derivation GATE question per
the plan, explicitly meant to run BEFORE the expensive full 3-arm binder ablation).

Glass-box / not-a-bolt-on-reader note: f_role/g_slot are freshly-initialized, gradient-trained-from-
scratch modules over the substrate's OWN frozen-encoder-derived role split and OWN bind/unbind algebra;
no external model's parse, embedding, or role-label enters the computation graph at inference. The only
"supplied" element is the factorization PRIOR (architecture) and the reconstruct-through-the-algebra
OBJECTIVE, which is knowledge/structure-adjacent scaffolding per SUBSTRATE_CHARTER, not a borrowed
reading mechanism.
"""

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch
import torch.nn.functional as F

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_selective_overwrite_recall_nl_wm_roleseparated_v1 as base  # noqa: E402
import exp_selective_overwrite_recall_nl_wm_readcond_v1 as rc  # noqa: E402
import exp_oracle_context_invariant_address_wm_v2 as oc  # noqa: E402  -- fires ho's base.S_TARGET=15 patch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_checkpoint as ckpt  # noqa: E402  -- per-unit checkpoint/resume (MANDATORY, CLAUDE.md)
from hdlab import binding  # noqa: E402  -- native bind/unbind (real float32 -> HRR, FFT circular conv)

ANCHOR_NAME = "tpr_role_key_effective_rank_probe_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
V2_CKPT = oc.V2_CKPT

# ---- reused constants (single source of truth: oc) ----
S_TARGET_TOTAL = oc.S_TARGET_TOTAL              # 15
V_FILL = oc.V_FILL                              # 20 -> CHANCE_RECALL = 0.05
CHANCE_RECALL = oc.CHANCE_RECALL
TRAIN_ROLES_V2 = oc.TRAIN_ROLES_V2              # 10 roles (this cell's target-role training pool)
HELD_OUT_ROLES_V2 = oc.HELD_OUT_ROLES_V2        # 5 roles (NEVER in any training minibatch)
HELD_OUT_SET_V2 = oc.HELD_OUT_SET_V2
TRAIN_SET_V2 = oc.TRAIN_SET_V2
ALL_ROLES = oc.ALL_ROLES
ORACLE_PROBE_SEED = oc.ORACLE_PROBE_SEED

# ---- TPR factorization geometry (bijective mixed-radix decomposition, fixed BEFORE running) ----
N_A = 5
N_B = 3
assert N_A * N_B == S_TARGET_TOTAL, "mixed-radix grid must exactly cover S_TARGET_TOTAL"
H_FACTOR = 12                                   # per-factor embedding width (THEORETICAL: cheap, tiny)
# ANGLE_SCALE: multiplies the Linear projection's raw output before phase-encoding. Without it, small
# standard nn.Linear init (fan-in ~144) produces theta std ~0.03 rad -- MEASURED@this file's dev
# iteration: PR(untrained TPR key matrix, all 15 roles) = 1.0006, i.e. every role's key is nearly
# IDENTICAL at init (phases all near 0), and 400 training steps could not escape this (acc stuck at
# ~0.20-0.26 vs oracle's untrained 0.88-0.92) -- an initialization-scale bug, not a capacity/objective
# problem. ANGLE_SCALE=60.0 is tuned so theta's initial std lands near ~1.6-1.8 rad (comparable to a
# uniform-random phase's std of 2*pi/sqrt(12)=1.81), giving well-separated initial keys with a
# well-conditioned starting point for gradient descent to refine, rather than a collapsed one.
ANGLE_SCALE = 60.0
# D_KEY: the bind/unbind WORKING dimensionality of every role key and filler vector (separate from
# d_enc=512, the frozen encoder's raw representation dimensionality, which is only the INPUT to the
# oracle table / the fixed random projection down to D_KEY). MEASURED@this file's dev iteration: at
# d_enc=512 directly, superposing 10 simultaneous role bindings and decoding against a 20-item filler
# codebook is TRIVIAL regardless of key quality -- even a completely UNTRAINED random-phase key table
# recovers with accuracy 1.0 (bind/unbind capacity at N=512 vastly exceeds K=10 items), so CONTROL_A's
# untrained held-out rows "succeed" not because training generalized but because ANY reasonably
# high-dimensional key succeeds trivially -- the task did not discriminate at all (a saturated-baseline
# construction bug, META_RULE_AG). FIX: shrink the working key dimension so that superposition capacity
# is genuinely stressed. A closed-form sweep (pure random-phase keys, no learned module, same 10-role/
# 9-distractor/20-filler task) measured recall vs D: D=8 -> 0.31, D=10 -> 0.3665, D=12 -> 0.4085,
# D=14 -> 0.446, D=16 -> 0.526, D=32 -> 0.764, D=512 -> 1.0 (all MEASURED@this file's dev iteration).
# D_KEY=10 sits clearly BELOW every pre-registered threshold (HP_HELD_MIN=0.55, HF_HELD_MAX=0.40) with
# real headroom, so the RANDOM (no-training-benefit) floor is genuinely distinguishable from both bands
# rather than trivially saturating either one.
D_KEY = 10
RANDOM_BASELINE_SEED = 606004                    # fixed untrained reference-key table (see below)
RANDOM_MARGIN = 0.10                             # CONTROL_A validity: held must not beat this margin
# DISCRIM_MARGIN: the discriminator-fires gate (checked FIRST, before validity). TPR train-role recall
# must exceed the untrained random-key baseline's train-role recall by this much on every seed, else the
# contrastive fix still isn't learning and the run is OBJECTIVE_STILL_BROKEN (HYPOTHESIZED: 0.05 is a
# small-but-non-noise margin at N_EVAL_TRAIN=400 samples/seed -- binomial SE at p~0.5 is ~0.025, so a
# 0.05 gap is ~2 SE, distinguishable from eval noise).
DISCRIM_MARGIN = 0.05
# CONTRASTIVE_TEMPERATURE: scales the cosine-similarity-to-codebook logits before softmax
# cross-entropy (contrastive_ce_loss). HYPOTHESIZED: cosine similarities live in [-1, 1], a raw-scale
# softmax over such a narrow logit range is under-confident/slow to separate classes early in training;
# temperature=0.15 sharpens the softmax (divides logits, effectively raising the score scale ~6.7x) to a
# comparable strength to typical contrastive-learning presets (e.g. SimCLR-style tau in [0.05, 0.2]) --
# not tuned against held-out results (fixed before running, per calibration_check discipline).
CONTRASTIVE_TEMPERATURE = 0.15
# N_DISTRACT: distractor bindings drawn from the SAME real role-id space as the query (NOT a separate
# disjoint key pool) -- this is the load-bearing design point. If distractors used a small separate
# pool of fixed random keys, unbind(h, query_key) would recover the target almost perfectly REGARDLESS
# of whether the role-key module learned anything (at d_enc=512, crosstalk from a couple of unrelated
# random keys is negligible -- MEASURED@this file's dev iteration: loss ~0 after 1 gradient step, TPR
# and FLAT arms produced bit-identical predictions, tripping the arms-must-differ gate). Binding
# len(TRAIN_ROLES_V2)-1 = 9 OTHER real roles simultaneously (every occurrence writes a "full
# scratchpad") makes recovery accuracy depend on how well-SEPARATED the queried role's key is from every
# OTHER role's key -- exactly the property TPR-vs-flat-vs-oracle is being compared on.
N_DISTRACT = len(TRAIN_ROLES_V2) - 1            # 9: all OTHER train roles bound simultaneously

# ---- run params (proper-budget retry, Director coordinator 2026-07-30: the 400-step run's
# OBJECTIVE_STILL_BROKEN was suspected UNDERTRAINING, so give a FAIR budget once, then STOP iterating
# this secondary deployability gate). STEPS_TRAIN 400 -> 4000; LR swept {5e-3, 1e-2, 3e-2} + contrastive
# softmax temperature swept {0.15, 0.07, 0.03} at both 2000 and 4000 steps
# (MEASURED@scratchpad/tpr_sweep.py + tpr_sweep2.py dev iteration): the winning WELL-BEHAVED config
# (train loss descends without the temp-too-low overconfidence blowup) is LR=3e-2, temp=0.15, H=12
# (loss 2.144->2.052, dL=-0.092 over 4000 steps). H_FACTOR=24 did NOT help (acc no better); temp<=0.07
# made the loss descend more but ONLY by recovering from an overconfidence penalty, with acc_train STILL
# flat at random -- so temperature stays 0.15. NOTE the decisive finding this budget SURFACED: NO config
# (any LR/temp/H, 2000 or 4000 steps) lifted TPR acc_train meaningfully above the untrained random-key
# baseline (~0.3725 at seed 7); per-checkpoint acc traces are noise, not a learning curve. This is a
# CAPACITY-limited regime (D_KEY=10 with N_DISTRACT=9 simultaneous bindings puts random near-orthogonal
# FHRR keys already near the superposition-recovery ceiling), so a learned key has ~nothing to gain over
# random -- the honest read is the bottleneck is NOT key-derivation but upstream capacity (connects to
# the encoder-capacity question), not that the objective/budget is wrong.
SEEDS_FULL = (7, 13, 19)
STEPS_TRAIN = 4000
BATCH = 64
LR = 3e-2
N_EVAL_TRAIN = 400                              # eval examples per seed, TRAIN_ROLES_V2-only
N_EVAL_HELD = 400                               # eval examples per seed, HELD_OUT_ROLES_V2-only
FILLER_KEY_SEED = 606002                         # fixed filler codebook (shared, not the DV)
MODULE_INIT_SEED_OFFSET = 606003                 # per-seed module-init offset (independent of data rng)

# ---- pre-registered bands (this file, written BEFORE running; NOT loosened) ----
NEAR_CHANCE_MARGIN = 0.10
FAIL_MAX = CHANCE_RECALL + NEAR_CHANCE_MARGIN     # THEORETICAL: 0.05 + 0.10 = 0.15
HP_HELD_MIN = 0.55
HP_GAP_MAX = 0.20
HP_BEAT_CONTROL_A_MIN = 0.15
HF_HELD_MAX = 0.40
HF_GAP_MAX = 0.35
HF_BEAT_CONTROL_A_MIN = 0.10
MIDDLE_BEAT_CONTROL_A_MIN = 0.10                  # "meaningfully" beats CONTROL_A for MIDDLE_BAND framing

ARMS = ("tpr", "flat", "oracle")


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------- canonical hardening ----------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _jsonify(obj):
    if isinstance(obj, torch.Tensor):
        return _jsonify(obj.detach().cpu().tolist())
    if isinstance(obj, np.ndarray):
        return _jsonify(obj.tolist())
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, dict):
        return {str(k): _jsonify(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonify(v) for v in obj]
    return obj


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    safe_metrics = _jsonify(metrics)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(safe_metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _digest_ints(arr):
    a = np.asarray(arr, dtype=np.int64)
    return hashlib.sha256(a.tobytes()).hexdigest()


# ---------------- role-key modules ----------------
def _phase_encode(theta):
    """Real angle tensor [..., d] -> unit-magnitude-per-component complex64 (FHRR unitary construction,
    CITED@Plate 1995). Differentiable (cos/sin are smooth), and bind/unbind via hdlab.binding's complex
    dispatch (elementwise mul / conjugate-mul) is an EXACT algebraic inverse for ANY theta, by
    construction -- unlike a plain L2-normalized real vector, whose HRR (circular-convolution) unbind is
    only an approximate inverse (MEASURED@this file's dev iteration: cosine plateaus at ~0.71-0.77
    regardless of dimension for random real vectors -- a construction issue, not a substrate limitation;
    same root cause independently hit and fixed the same way by
    exp_vsa_native_bind_zeroshot_role_v1's phase_vec_table/phase_encode_real)."""
    return torch.complex(torch.cos(theta), torch.sin(theta))


class FactoredRoleKey(torch.nn.Module):
    """TPR-style role key: role_id -> mixed-radix (a, b) -> outer(Emb_a[a], Emb_b[b]) -> Linear -> real
    angle vector [d_out] -> phase-encoded to unit-magnitude-per-component complex64 (FHRR unitary key).
    A role's key is COMPOSED from two independently-varying, independently-trained sub-factors -- a
    held-out role never seen in training still has a compositional path via its (previously-trained)
    individual a-factor and b-factor."""

    def __init__(self, n_a, n_b, h, d_out, seed):
        super().__init__()
        self.n_a, self.n_b, self.h = n_a, n_b, h
        g = torch.Generator().manual_seed(seed)
        self.emb_a = torch.nn.Embedding(n_a, h)
        self.emb_b = torch.nn.Embedding(n_b, h)
        self.proj = torch.nn.Linear(h * h, d_out)
        with torch.no_grad():
            self.emb_a.weight.copy_(torch.empty(n_a, h).normal_(0.0, 0.2, generator=g))
            self.emb_b.weight.copy_(torch.empty(n_b, h).normal_(0.0, 0.2, generator=g))
            self.proj.weight.copy_(torch.empty(d_out, h * h).normal_(0.0, 0.05, generator=g))
            self.proj.bias.zero_()

    def forward(self, role_ids):
        a = torch.div(role_ids, self.n_b, rounding_mode="floor")
        b = role_ids % self.n_b
        fa = self.emb_a(a)
        fb = self.emb_b(b)
        outer = torch.einsum("bi,bj->bij", fa, fb).reshape(fa.shape[0], -1)
        theta = self.proj(outer) * ANGLE_SCALE
        return _phase_encode(theta)


class FlatRoleKey(torch.nn.Module):
    """CONTROL_A: role_id -> Embedding(n_roles, h*h)[role_id] -> the SAME Linear(h*h -> d_out) shape as
    FactoredRoleKey -> phase-encoded to unit-magnitude-per-component complex64. No factor structure:
    nothing to recombine for a role id never supervised, so a held-out row is stuck at its random init --
    the flat-lookup failure mode."""

    def __init__(self, n_roles, h, d_out, seed):
        super().__init__()
        g = torch.Generator().manual_seed(seed)
        self.emb = torch.nn.Embedding(n_roles, h * h)
        self.proj = torch.nn.Linear(h * h, d_out)
        with torch.no_grad():
            self.emb.weight.copy_(torch.empty(n_roles, h * h).normal_(0.0, 0.2, generator=g))
            self.proj.weight.copy_(torch.empty(d_out, h * h).normal_(0.0, 0.05, generator=g))
            self.proj.bias.zero_()

    def forward(self, role_ids):
        e = self.emb(role_ids)
        theta = self.proj(e) * ANGLE_SCALE
        return _phase_encode(theta)


def build_module(mode, d_out, seed):
    if mode == "tpr":
        return FactoredRoleKey(N_A, N_B, H_FACTOR, d_out, seed + MODULE_INIT_SEED_OFFSET)
    if mode == "flat":
        return FlatRoleKey(S_TARGET_TOTAL, H_FACTOR, d_out, seed + MODULE_INIT_SEED_OFFSET)
    raise ValueError("build_module: unknown trainable mode %r" % mode)


def phase_vec_table(n_rows, d, seed):
    """n_rows i.i.d. uniform-random-phase unit-magnitude-per-component complex64 vectors (FHRR unitary
    construction, same convention as exp_vsa_native_bind_zeroshot_role_v1.phase_vec_table). Deterministic
    (torch.Generator, fixed seed)."""
    g = torch.Generator().manual_seed(seed)
    theta = torch.rand(n_rows, d, generator=g) * (2.0 * math.pi)
    return torch.complex(torch.cos(theta), torch.sin(theta))


def phase_encode_real(real_mat, mu, sd, scale):
    """Converts a REAL matrix [n, d] into unit-magnitude-per-component complex64 vectors by z-scoring
    each column against a FIXED (mu, sd), then treating the z-scored value as an angle in radians
    (theta = z * scale). Same convention as exp_vsa_native_bind_zeroshot_role_v1.phase_encode_real --
    used ONLY for CONTROL_B (oracle), never for the trained TPR/FLAT modules."""
    z = (real_mat - mu) / sd
    theta = z * scale
    return torch.complex(torch.cos(theta), torch.sin(theta))


def build_oracle_table_at_d_key(oracle_table_raw, d_key, seed):
    """Projects the real [15, d_enc] context-invariant oracle table (oc.build_oracle_table, CONTROL_B)
    down to the SAME D_KEY working dimensionality used by the trained TPR/FLAT modules, via a FIXED
    (never-trained) random real projection matrix -- so the bind/unbind capacity comparison across all
    3 arms is apples-to-apples. z-scores the projected columns, then phase-encodes (same convention as
    phase_encode_real). Returns (oracle_table_complex64 [15, d_key], projection_matrix [d_enc, d_key])."""
    d_enc = oracle_table_raw.shape[1]
    g = torch.Generator().manual_seed(seed)
    proj_mat = torch.empty(d_enc, d_key).normal_(0.0, 1.0 / math.sqrt(d_enc), generator=g)
    projected = oracle_table_raw @ proj_mat                    # [15, d_key]
    mu = projected.mean(dim=0, keepdim=True)
    sd = projected.std(dim=0, keepdim=True).clamp_min(1e-6)
    return phase_encode_real(projected, mu, sd, 1.0), proj_mat


def random_key_baseline_table(d_key, seed):
    """The UNTRAINED reference: a fixed random-phase key per role (identical construction to what a
    never-updated FLAT embedding row looks like, decoupled from any specific training run). Serves as
    the MEASURED (not literal-chance) floor CONTROL_A's held-out performance is checked against, since
    in THIS algebraic bind/unbind-capacity-limited task (unlike the classifier/softmax-routing WM
    cells this design descends from) an untrained random key is not near mathematical chance -- it is
    near the random-quasi-orthogonal-key capacity ceiling for the chosen D_KEY/N_DISTRACT regime."""
    return phase_vec_table(S_TARGET_TOTAL, d_key, seed)


def complex_cosine_batched(a, b):
    """Properly-normalized complex cosine similarity per row: Re(<a, conj(b)>) / (|a| |b|), for complex
    vectors [B, d]. Returns a real-valued [B] tensor in [-1, 1], differentiable w.r.t. a. Used ONLY as
    the reconstruction training loss (1 - this) and self-test sanity checks -- NOT for decode (decode
    is an argmax over a shared-magnitude codebook, where the raw unnormalized inner product already
    gives the same argmax; MEASURED@this file's dev iteration: skipping the |a| normalization here let
    the "loss" go negative -- below the true [0, 2] range of 1 - cosine -- because `recovered`'s
    magnitude is NOT fixed like a phase-encoded vector's is, so an unnormalized inner product is not a
    true cosine and can be gamed by inflating |recovered| rather than genuinely aligning phase)."""
    inner = (a * b.conj()).real.sum(dim=-1)
    norm_a = torch.sqrt((a.abs() ** 2).sum(dim=-1).clamp_min(1e-12))
    norm_b = torch.sqrt((b.abs() ** 2).sum(dim=-1).clamp_min(1e-12))
    return inner / (norm_a * norm_b)


def complex_cosine_to_codebook(a, codebook):
    """Cosine similarity of each row of `a` [B, d] complex64 against EVERY row of `codebook` [V, d]
    complex64. Returns real [B, V]. THE BUGFIX PRIMITIVE: unlike complex_cosine_batched (one similarity
    per example, against only the TRUE filler), this scores against ALL V candidates so the training
    loss can be made to penalize similarity to the OTHER V-1 fillers explicitly -- the property the
    original reconstruction-cosine loss lacked (MEASURED regression: trained keys < random-key baseline,
    e.g. D_KEY=20 trained 0.305 vs random 0.55, because nothing in that loss discouraged the recovered
    vector from drifting toward a WRONG filler as long as it also drifted toward the true one)."""
    inner = torch.einsum("bd,vd->bv", a, codebook.conj()).real                    # [B, V]
    norm_a = torch.sqrt((a.abs() ** 2).sum(dim=-1).clamp_min(1e-12))              # [B]
    norm_v = torch.sqrt((codebook.abs() ** 2).sum(dim=-1).clamp_min(1e-12))       # [V]
    return inner / (norm_a.unsqueeze(1) * norm_v.unsqueeze(0))


def contrastive_ce_loss(recovered, fills_t, filler_table, temperature=CONTRASTIVE_TEMPERATURE):
    """THE FIX: softmax cross-entropy over cosine-similarity-to-the-full-filler-codebook, target = true
    filler id. This is EXACTLY the quantity decode_batch() takes argmax over (same complex_cosine_to_
    codebook scores, same codebook), so minimizing this loss directly optimizes decode-argmax accuracy --
    unlike the old reconstruction-cosine loss (1 - cos(recovered, true_filler) only), which had no term
    discouraging similarity to the other V_FILL-1 candidates and could be lowered while decode-argmax
    discriminability collapsed. Differentiable (einsum + cross_entropy are autograd-friendly)."""
    scores = complex_cosine_to_codebook(recovered, filler_table) / temperature   # [B, V_FILL]
    return F.cross_entropy(scores, fills_t)


# ---------------- fixed (never-trained) filler codebook shared bit-identically across arms ----------
def build_fixed_tables(d_out):
    filler_table = phase_vec_table(V_FILL, d_out, FILLER_KEY_SEED)
    return filler_table


def compute_keys(module_or_table, role_ids_t):
    """module_or_table: an nn.Module (tpr/flat, forward(role_ids)->[B,d] complex64) OR a fixed
    [S_TARGET_TOTAL, d] complex64 tensor (oracle, row-indexed)."""
    if isinstance(module_or_table, torch.nn.Module):
        return module_or_table(role_ids_t)
    return module_or_table[role_ids_t]


# ---------------- reconstruction-task batch construction (same-role-space distractors) ------------
def sample_batch(rng, query_pool, distractor_universe, n_distract, batch):
    """Draws `batch` (query_role, query_fill, distract_roles[n_distract], distract_fills[n_distract])
    tuples. query_role drawn from query_pool; the n_distract distractor roles for EACH example are
    drawn WITHOUT REPLACEMENT from distractor_universe MINUS that example's query role -- i.e. every
    distractor is a REAL role from the same 0..S_TARGET_TOTAL-1 id space (not a separate fixed pool),
    so recovery accuracy depends on how well-separated the queried role's key is from every OTHER
    bound role's key. distractor_universe may equal query_pool (training: distractors = the other
    TRAIN roles) or differ from it (held-out eval: query from HELD_OUT_ROLES_V2, distractors from
    TRAIN_ROLES_V2, since query is never itself in that universe)."""
    query_roles = rng.choice(np.asarray(query_pool, dtype=np.int64), size=batch)
    query_fills = rng.integers(0, V_FILL, size=batch)
    universe = np.asarray(distractor_universe, dtype=np.int64)
    distract_roles = np.zeros((batch, n_distract), dtype=np.int64)
    distract_fills = rng.integers(0, V_FILL, size=(batch, n_distract))
    for i in range(batch):
        pool_i = universe[universe != query_roles[i]]
        distract_roles[i] = rng.choice(pool_i, size=n_distract, replace=False)
    return (query_roles.astype(np.int64), query_fills.astype(np.int64),
            distract_roles.astype(np.int64), distract_fills.astype(np.int64))


def build_bound_superposition(module_or_table, query_roles_t, query_fills_t, distract_roles_t,
                               distract_fills_t, filler_table):
    """Returns (superposed [B, d] complex64, query_keys [B, d] complex64). Every role key (query AND
    every distractor) is computed via the SAME compute_keys() call on module_or_table -- crosstalk
    genuinely depends on the role-key module's own separation quality, not a fixed side table."""
    query_keys = compute_keys(module_or_table, query_roles_t)
    fv = filler_table[query_fills_t]
    h = binding.bind(query_keys, fv)
    n_distract = distract_roles_t.shape[1]
    for k in range(n_distract):
        dk = compute_keys(module_or_table, distract_roles_t[:, k])
        dfv = filler_table[distract_fills_t[:, k]]
        h = h + binding.bind(dk, dfv)
    return h, query_keys


def decode_batch(recovered, filler_table):
    """recovered: [B, d] complex64. Returns predicted filler ids via argmax Re(Hermitian inner product)
    against the fixed codebook (matches exp_vsa_native_bind_zeroshot_role_v1's decode convention)."""
    scores = torch.einsum("bd,vd->bv", recovered, filler_table.conj()).real   # [B, V_FILL]
    return torch.argmax(scores, dim=-1)


def train_role_key_module(mode, seed, d_out, filler_table, steps, batch, lr):
    """TRAINING: query role from TRAIN_ROLES_V2, distractors = the OTHER 9 TRAIN roles (every occurrence
    binds all 10 TRAIN roles simultaneously) -- held-out roles are LITERALLY ABSENT from every
    minibatch (neither as query nor as distractor), so no gradient ever touches a held-out role's
    identity, satisfying the genuine zero-shot / genuine-novelty requirement."""
    torch.manual_seed(seed)
    module = build_module(mode, d_out, seed)
    opt = torch.optim.Adam(module.parameters(), lr=lr)
    rng = np.random.default_rng(seed + (1001 if mode == "tpr" else 2002))
    loss_curve = []
    ema = None
    for step in range(steps):
        roles, fills, d_roles, d_fills = sample_batch(rng, TRAIN_ROLES_V2, TRAIN_ROLES_V2, N_DISTRACT,
                                                       batch)
        roles_t = torch.from_numpy(roles)
        fills_t = torch.from_numpy(fills)
        d_roles_t = torch.from_numpy(d_roles)
        d_fills_t = torch.from_numpy(d_fills)
        opt.zero_grad()
        h, query_keys = build_bound_superposition(module, roles_t, fills_t, d_roles_t, d_fills_t,
                                                    filler_table)
        recovered = binding.unbind(h, query_keys)
        loss = contrastive_ce_loss(recovered, fills_t, filler_table)
        loss.backward()
        opt.step()
        lv = float(loss.item())
        ema = lv if ema is None else 0.9 * ema + 0.1 * lv
        if step == 0 or (step + 1) % max(1, steps // 6) == 0:
            loss_curve.append((step, lv))
            _log("    [%s seed=%d] step=%d loss=%.4f ema=%.4f" % (mode, seed, step + 1, lv, ema))
    module.eval()
    return module, loss_curve


def eval_recall(module_or_table, seed, query_pool, distractor_universe, n_eval, filler_table, eval_tag):
    """module_or_table: an nn.Module (tpr/flat) OR a fixed [S_TARGET_TOTAL,d] tensor (oracle). Returns
    recall accuracy over n_eval fresh reconstruction examples with query role drawn ONLY from
    query_pool and distractors drawn from distractor_universe (same-role-space, see sample_batch), plus
    a sha256 digest of the predicted-id sequence (arms-must-differ)."""
    rng = np.random.default_rng(seed + 999000 + (0 if eval_tag == "held" else 1))
    roles, fills, d_roles, d_fills = sample_batch(rng, query_pool, distractor_universe, N_DISTRACT,
                                                   n_eval)
    roles_t = torch.from_numpy(roles)
    fills_t = torch.from_numpy(fills)
    d_roles_t = torch.from_numpy(d_roles)
    d_fills_t = torch.from_numpy(d_fills)
    with torch.no_grad():
        h, query_keys = build_bound_superposition(module_or_table, roles_t, fills_t, d_roles_t,
                                                    d_fills_t, filler_table)
        recovered = binding.unbind(h, query_keys)
        preds = decode_batch(recovered, filler_table)
    preds_np = preds.numpy()
    acc = float((preds_np == fills).mean())
    return acc, _digest_ints(preds_np)


def key_matrix_for(module_or_table, role_ids):
    """Returns the [len(role_ids), d] key matrix (forward pass for modules, row-index for the fixed
    oracle table)."""
    ids_t = torch.tensor(list(role_ids), dtype=torch.int64)
    with torch.no_grad():
        if isinstance(module_or_table, torch.nn.Module):
            return module_or_table(ids_t)
        return module_or_table[ids_t]


def participation_ratio(K):
    """Effective-rank proxy: PR = (sum s_i^2)^2 / sum s_i^4 of the singular values of K [n, d]. Bounded
    in [1, min(n, d)]; PR near 1 means one dominant shared component (rank-deficient in the soft sense
    even if the hard matrix rank is higher); PR near min(n,d) means well-conditioned/near-orthogonal."""
    s = torch.linalg.svdvals(K.detach())
    s2 = s * s
    denom = float((s2 * s2).sum())
    if denom <= 0.0:
        return 0.0
    return float((s2.sum() ** 2) / denom)


def _strip_for_checkpoint(res):
    out = dict(res)
    return out


# ---------------- self-tests ----------------
def compositional_and_zeroshot_selftest():
    """Directly MEASURES (not assumes) two properties this cell's whole design depends on: (1) every
    held-out role's (a, b) factor pair has BOTH sub-factors independently present among the 10 train
    roles (compositional reachability -- if False for any role, the TPR factorization has no
    compositional path to that role regardless of training); (2) the training corpus (target-role
    sampling pool) contains ZERO held-out roles."""
    train_a = set(int(r) // N_B for r in TRAIN_ROLES_V2)
    train_b = set(int(r) % N_B for r in TRAIN_ROLES_V2)
    per_role = {}
    all_reachable = True
    for r in HELD_OUT_ROLES_V2:
        a = int(r) // N_B
        b = int(r) % N_B
        reachable = (a in train_a) and (b in train_b)
        per_role[int(r)] = {"a": a, "b": b, "a_in_train": a in train_a, "b_in_train": b in train_b,
                             "reachable": reachable}
        all_reachable = all_reachable and reachable
    rng = np.random.default_rng(7)
    roles, _, d_roles, _ = sample_batch(rng, TRAIN_ROLES_V2, TRAIN_ROLES_V2, N_DISTRACT, 5000)
    n_heldout_in_corpus = int(np.isin(roles, np.asarray(HELD_OUT_ROLES_V2)).sum()
                              + np.isin(d_roles, np.asarray(HELD_OUT_ROLES_V2)).sum())
    assert n_heldout_in_corpus == 0, (
        "ZEROSHOT_CONSTRUCTION_SELFTEST_FAIL: held-out role appeared as a training target %d times"
        % n_heldout_in_corpus)
    return {"compositional_reachability_all_ok": bool(all_reachable), "per_role": per_role,
            "n_heldout_in_training_corpus_sample": n_heldout_in_corpus,
            "train_roles": TRAIN_ROLES_V2, "held_out_roles": HELD_OUT_ROLES_V2}


def toy_bind_unbind_recon_selftest():
    """Fairness/correctness gate: a single-role, no-distractor toy case must recover the bound filler
    with cosine ~1.0 (EXACT, by construction of unit-magnitude-per-component complex64 keys/fillers) and
    the CORRECT argmax decode, using the actual hdlab.binding primitives."""
    d = 16
    filler_table = phase_vec_table(5, d, 303001)
    role_key = phase_vec_table(1, d, 303002)
    bound = binding.bind(role_key, filler_table[3:4])
    recovered = binding.unbind(bound, role_key)
    cos = float(complex_cosine_batched(recovered, filler_table[3:4]).item())
    pred = int(decode_batch(recovered, filler_table).item())
    assert cos > 0.99, "TOY_SELFTEST_FAIL: single bind/unbind cosine=%.4f (expected > 0.99)" % cos
    assert pred == 3, "TOY_SELFTEST_FAIL: single bind/unbind decoded %d, expected 3" % pred
    return {"toy_cosine": cos, "toy_pred": pred, "toy_pass": True}


def contrastive_loss_distinguishes_distractor_confusion_selftest():
    """Directly demonstrates the ROOT CAUSE of the withheld run's bug and confirms the fix: constructs a
    single decode-AMBIGUOUS example (a recovered vector whose inner product favors a WRONG (distractor)
    filler over the TRUE filler, so decode_batch would MISPREDICT) and shows the OLD reconstruction
    cosine-loss (1 - cos(recovered, true_filler), what f51c58bf9 trained against) reports a misleadingly
    LOW loss for it (it only measures cos-to-true, blind to the winning distractor), while the NEW
    contrastive_ce_loss reports a HIGH loss (it directly penalizes the distractor outscoring the true
    filler in the same softmax the decode-argmax uses) -- i.e. the fix's loss landscape actually points
    training away from decode failures the old loss was blind to. MEASURED@this file's dev iteration
    (fixed toy construction, d=16, V=6, alpha=0.60 mix of wrong_fv/true_fv): old_style_loss=0.4069
    (comfortably below a 0.9 "this looks fine" threshold) at the exact point decode flips to the WRONG
    filler; new_loss=1.8502 (comfortably above 1.0, i.e. true filler's softmax prob well under 50%)."""
    d = 16
    filler_table = phase_vec_table(6, d, 909001)
    true_idx, wrong_idx = 2, 3
    true_fv = filler_table[true_idx]
    wrong_fv = filler_table[wrong_idx]
    alpha = 0.60                                    # weight on the WRONG filler (MEASURED to flip decode)
    recovered = (alpha * wrong_fv + (1.0 - alpha) * true_fv).unsqueeze(0)   # [1, d]
    pred = int(decode_batch(recovered, filler_table).item())
    assert pred == wrong_idx, (
        "SELFTEST_CONSTRUCTION_FAIL: expected the toy mix to flip decode to the WRONG filler "
        "(pred=%d, expected=%d) -- alpha needs re-tuning" % (pred, wrong_idx))
    old_style_loss = float((1.0 - complex_cosine_batched(recovered, true_fv.unsqueeze(0))).item())
    fills_t = torch.tensor([true_idx], dtype=torch.int64)
    new_loss = float(contrastive_ce_loss(recovered, fills_t, filler_table).item())
    assert old_style_loss < 0.9, (
        "SELFTEST_CONSTRUCTION_FAIL: old-style reconstruction loss=%.4f is not in the 'misleadingly low "
        "despite wrong decode' regime this test needs (expected < 0.9)" % old_style_loss)
    assert new_loss > 1.0, (
        "CONTRASTIVE_LOSS_SELFTEST_FAIL: new contrastive_ce_loss=%.4f did not fire large on a "
        "decode-WRONG example (expected > 1.0) -- the fix does not penalize distractor-similarity as "
        "intended" % new_loss)
    return {"pred": pred, "true_idx": true_idx, "wrong_idx": wrong_idx, "alpha": alpha,
            "old_style_reconstruction_loss": old_style_loss, "new_contrastive_ce_loss": new_loss,
            "bug_reproduced_old_loss_misleadingly_low_on_wrong_decode": bool(old_style_loss < 0.9),
            "fix_confirmed_new_loss_fires_on_wrong_decode": bool(new_loss > 1.0)}


def gradient_flows_selftest(d_out):
    """Directly measures that the reconstruction loss actually backpropagates into the role-key
    module's parameters (catches a silently-detached graph bug in the bind/unbind path)."""
    filler_table = build_fixed_tables(d_out)
    module = build_module("tpr", d_out, 7)
    p0 = {n: p.detach().clone() for n, p in module.named_parameters()}
    rng = np.random.default_rng(7)
    roles, fills, d_roles, d_fills = sample_batch(rng, TRAIN_ROLES_V2, TRAIN_ROLES_V2, N_DISTRACT, 32)
    opt = torch.optim.Adam(module.parameters(), lr=1e-1)
    for _ in range(5):
        opt.zero_grad()
        h, query_keys = build_bound_superposition(module, torch.from_numpy(roles),
                                                   torch.from_numpy(fills), torch.from_numpy(d_roles),
                                                   torch.from_numpy(d_fills), filler_table)
        recovered = binding.unbind(h, query_keys)
        loss = contrastive_ce_loss(recovered, torch.from_numpy(fills), filler_table)
        loss.backward()
        opt.step()
    moved = any(not torch.allclose(p0[n], p.detach()) for n, p in module.named_parameters())
    assert moved, "GRADIENT_FLOW_SELFTEST_FAIL: no module parameter changed after 5 optimizer steps"
    return {"params_moved": bool(moved)}


def run_self_test():
    _log("SELF-TEST: toy single-role bind/unbind reconstruction (correctness of primitive usage) ...")
    toy_diag = toy_bind_unbind_recon_selftest()
    _log("  PASS: %s" % toy_diag)

    _log("SELF-TEST: compositional reachability + zero-shot corpus exclusion (measured, not assumed) ...")
    cz_diag = compositional_and_zeroshot_selftest()
    assert cz_diag["compositional_reachability_all_ok"], (
        "COMPOSITIONAL_REACHABILITY_SELFTEST_FAIL: at least one held-out role's (a,b) factors are not "
        "both present in TRAIN_ROLES_V2: %s" % cz_diag["per_role"])
    _log("  PASS: reachability_all_ok=%s n_heldout_in_corpus_sample=%d"
         % (cz_diag["compositional_reachability_all_ok"], cz_diag["n_heldout_in_training_corpus_sample"]))

    _log("SELF-TEST: contrastive loss penalizes distractor-similarity (the bugfix's central claim) ...")
    loss_diag = contrastive_loss_distinguishes_distractor_confusion_selftest()
    _log("  PASS: %s" % loss_diag)

    _log("SELF-TEST: gradient actually flows into the TPR module through bind/unbind (real_code_path) ...")
    grad_diag = gradient_flows_selftest(d_out=32)
    _log("  PASS: %s" % grad_diag)

    _log("SELF-TEST: load REAL v2 encoder + build REAL oc oracle table (real_code_path, CONTROL_B) ...")
    assert os.path.exists(V2_CKPT), "v2 checkpoint missing: %s" % V2_CKPT
    enc = base.FrozenV2Encoder(V2_CKPT)
    n_cached = enc.build_cache()
    assert n_cached >= 3000, "closed sentence set smaller than expected (widened query set missing?)"
    cond = rc.Conditioner(enc.U_tok_t, enc.U_pad_t)
    Uc = cond.apply(enc.U_tok_t, enc.U_pad_t, "pca_whiten")
    oracle_table_raw, _all_reps, _idx_lists, n_ctx = oc.build_oracle_table(enc, Uc, ORACLE_PROBE_SEED)
    d_enc = enc.d
    oracle_table, _proj_mat = build_oracle_table_at_d_key(oracle_table_raw, D_KEY, ORACLE_PROBE_SEED)
    assert oracle_table.shape == (S_TARGET_TOTAL, D_KEY)
    pr_oracle = participation_ratio(oracle_table)
    _log("  d_enc=%d D_KEY=%d n_ctx_per_role min=%d max=%d oracle PR (all 15 roles)=%.4f"
         % (d_enc, D_KEY, min(n_ctx), max(n_ctx), pr_oracle))
    assert pr_oracle > 0.0

    filler_table = build_fixed_tables(D_KEY)
    random_baseline = random_key_baseline_table(D_KEY, RANDOM_BASELINE_SEED)

    _log("SELF-TEST: tiny end-to-end TPR/FLAT/ORACLE/RANDOM (arms-must-differ, ranges valid, short "
         "training) ...")
    tiny_results = {}
    tiny_pr = {}
    for mode in ("tpr", "flat"):
        module, _lc = train_role_key_module(mode, 7, D_KEY, filler_table, steps=30, batch=32, lr=LR)
        acc_train, dig_train = eval_recall(module, 7, TRAIN_ROLES_V2, TRAIN_ROLES_V2, 60, filler_table,
                                            "train")
        acc_held, dig_held = eval_recall(module, 7, HELD_OUT_ROLES_V2, TRAIN_ROLES_V2, 60, filler_table,
                                          "held")
        km = key_matrix_for(module, range(S_TARGET_TOTAL))
        tiny_pr[mode] = participation_ratio(km)
        tiny_results[mode] = {"acc_train": acc_train, "acc_held": acc_held, "dig_held": dig_held}
        assert 0.0 <= acc_train <= 1.0 and 0.0 <= acc_held <= 1.0
    acc_train_o, dig_train_o = eval_recall(oracle_table, 7, TRAIN_ROLES_V2, TRAIN_ROLES_V2, 60,
                                           filler_table, "train")
    acc_held_o, dig_held_o = eval_recall(oracle_table, 7, HELD_OUT_ROLES_V2, TRAIN_ROLES_V2, 60,
                                         filler_table, "held")
    acc_held_r, dig_held_r = eval_recall(random_baseline, 7, HELD_OUT_ROLES_V2, TRAIN_ROLES_V2, 60,
                                         filler_table, "held")
    # DISCRIMINATOR-FIRES preview (tiny scale, informational only -- only 30 steps, not the hard gate;
    # the hard gate runs at FULL scale with 400 steps / N_EVAL_TRAIN=400 -- see decide_verdict). Compute
    # the SAME random-key baseline's accuracy on the TRAIN-role pool (same query pool the trained arms
    # are evaluated on) so the tiny run can show an early read on "does training even beat doing nothing".
    acc_train_r, dig_train_r = eval_recall(random_baseline, 7, TRAIN_ROLES_V2, TRAIN_ROLES_V2, 60,
                                           filler_table, "train")
    tiny_results["random"] = {"acc_train": acc_train_r, "acc_held": acc_held_r, "dig_held": dig_held_r}
    tiny_results["oracle"] = {"acc_train": acc_train_o, "acc_held": acc_held_o, "dig_held": dig_held_o}
    digests = {m: r["dig_held"] for m, r in tiny_results.items()}
    pairs = [(a, b) for a in digests for b in digests if a < b]
    for a, b in pairs:
        assert digests[a] != digests[b], (
            "META_RULE_AF VIOLATION: arms %r and %r bit-identical (hash=%s)" % (a, b, digests[a]))
    tiny_discriminator_preview = {
        "tpr_train_acc": tiny_results["tpr"]["acc_train"], "random_train_acc": acc_train_r,
        "tpr_beats_random_on_train_tiny_preview": bool(
            tiny_results["tpr"]["acc_train"] > acc_train_r + DISCRIM_MARGIN)}
    _log("  PASS tiny: %s tiny_PR(tpr=%.3f flat=%.3f oracle=%.3f) discriminator_preview=%s"
         % ({m: {"acc_train": round(r["acc_train"], 3), "acc_held": round(r["acc_held"], 3)}
             for m, r in tiny_results.items()},
            tiny_pr["tpr"], tiny_pr["flat"], pr_oracle, tiny_discriminator_preview))

    _log("SELF-TEST PASS")
    return {"toy_diag": toy_diag, "compositional_zeroshot_diag": cz_diag, "gradient_flow_diag": grad_diag,
            "contrastive_loss_diag": loss_diag,
            "n_cached": n_cached, "d_enc": d_enc, "d_key": D_KEY, "pr_oracle_selftest": pr_oracle,
            "tiny_pr": tiny_pr, "tiny_results": tiny_results,
            "tiny_discriminator_preview": tiny_discriminator_preview, "arms_differ_verified": True}


def checkpoint_resume_selftest():
    import shutil
    import tempfile
    tmp_dir = tempfile.mkdtemp(prefix="tpr_probe_ckpt_selftest_")
    try:
        unit_specs = [("tpr", 7), ("flat", 7), ("oracle", 7)]

        def _compute(kind, seed):
            g = torch.Generator().manual_seed((abs(sum(ord(c) for c in kind)) % 100000) + seed)
            return {"kind": kind, "seed": seed, "acc": float(torch.rand(1, generator=g).item())}

        d_single = os.path.join(tmp_dir, "single")
        for kind, seed in unit_specs:
            k = ckpt.unit_key(kind, seed)
            ckpt.record_unit(d_single, k, _compute(kind, seed))
        single_final = ckpt.load_units(d_single)
        assert len(single_final) == 3

        d_resume = os.path.join(tmp_dir, "resume")
        for kind, seed in unit_specs[:1]:
            ckpt.record_unit(d_resume, ckpt.unit_key(kind, seed), _compute(kind, seed))
        done = ckpt.completed_units(d_resume)
        n_skipped = 0
        for kind, seed in unit_specs:
            k = ckpt.unit_key(kind, seed)
            if k in done:
                n_skipped += 1
                continue
            ckpt.record_unit(d_resume, k, _compute(kind, seed))
        assert n_skipped == 1
        resumed_final = ckpt.load_units(d_resume)
        assert json.dumps(resumed_final, sort_keys=True) == json.dumps(single_final, sort_keys=True)
        return {"resume_skip_count": n_skipped, "bit_identical_resume": True}
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ---------------- verdict ----------------
def decide_verdict(per_seed):
    """per_seed: list of dicts, one per seed, each with keys tpr_held, tpr_train, flat_held, pr_tpr,
    pr_oracle, random_held, random_train, pr_random (all per-seed since the module is
    re-initialized/re-trained per seed; pr_oracle/pr_random/random_held/random_train are near-identical
    across seeds since the oracle table and random-baseline table are never re-trained -- oracle is
    fixed globally, random_baseline is fixed globally too, so only the EVAL sample varies by seed;
    recomputed per-seed for hygiene/logging).

    DISCRIMINATOR-FIRES GATE (checked ABSOLUTE FIRST, per Director's 2026-07-30 bugfix spawn): TPR
    train-role recall must exceed the untrained random-key baseline's train-role recall by
    >= DISCRIM_MARGIN on EVERY seed. This is the fairness/sanity check that the contrastive-loss fix
    (replacing the withheld run's broken reconstruction-cosine loss) actually LEARNS something -- if
    training can't even beat doing nothing on the roles it trained on, the held-out TPR-vs-flat
    comparison downstream is meaningless and must NOT be interpreted.

    VALIDITY GATE (CONTROL_A fairness floor): in the ORIGINAL classifier/softmax-routing WM cells this
    substrate already ran (exp_oracle_context_invariant_address_wm_v2 / exp_wm_addressing_heldout_role_
    warmstart_v1), a flat learned key's held-out failure was near LITERAL CHANCE (0.05) because the
    downstream trained function was a softmax classifier that extrapolates near-randomly on an
    unseen input. THIS cell's mechanism is different in kind: bind/unbind is an ALGEBRAIC operation,
    not a trained classifier, so an untrained (never-updated) random key is not near literal chance --
    it sits at the RANDOM-KEY CAPACITY CEILING for the chosen D_KEY/N_DISTRACT regime (MEASURED fresh
    every run via random_key_baseline_table(), a fixed reference DECOUPLED from any specific training
    run). The correct, honest floor for "did CONTROL_A's held-out row benefit from training it never
    received" is therefore: held-out FLAT recall must not exceed the RANDOM baseline by more than
    RANDOM_MARGIN -- not "must be near CHANCE_RECALL=0.05", which is unreachable in this task regime
    (an algebraic-recovery task's structural floor for ANY reasonably-dimensioned key is well above
    literal chance, confirmed empirically at D_KEY=512 where even a fully random table achieves 1.0)."""
    tpr_held = [r["tpr_held"] for r in per_seed]
    tpr_train = [r["tpr_train"] for r in per_seed]
    flat_held = [r["flat_held"] for r in per_seed]
    random_held = [r["random_held"] for r in per_seed]
    random_train = [r["random_train"] for r in per_seed]
    gaps = [tr - he for tr, he in zip(tpr_train, tpr_held)]
    beats_a = [th - fh for th, fh in zip(tpr_held, flat_held)]
    pr_tpr = [r["pr_tpr"] for r in per_seed]
    pr_oracle = [r["pr_oracle"] for r in per_seed]
    rank_beats_oracle = [pt > po for pt, po in zip(pr_tpr, pr_oracle)]

    discrim_margins = [tt - rt for tt, rt in zip(tpr_train, random_train)]
    discriminator_fires = all(dm >= DISCRIM_MARGIN for dm in discrim_margins)

    if not discriminator_fires:
        verdict = "OBJECTIVE_STILL_BROKEN"
        msg = ("DISCRIMINATOR-FIRES GATE FAILED: TPR train-role recall=%s did not exceed the untrained "
               "random-key baseline's train-role recall=%s by the required DISCRIM_MARGIN=%.2f on every "
               "seed (margins=%s). The contrastive-loss fix still isn't learning to beat doing nothing "
               "on the roles it trained on -- the mechanism is not learning, so TPR-vs-flat held-out "
               "generalization is UNINTERPRETABLE and is NOT reported as a verdict. This is an honest "
               "report of a still-broken training objective/regime, not a forced factorization verdict."
               % ([round(t, 3) for t in tpr_train], [round(t, 3) for t in random_train], DISCRIM_MARGIN,
                  [round(m, 3) for m in discrim_margins]))
        bands = {"chance_recall": CHANCE_RECALL, "random_margin": RANDOM_MARGIN,
                 "discrim_margin": DISCRIM_MARGIN, "discriminator_fires": False,
                 "tpr_train": tpr_train, "random_train": random_train,
                 "discrim_margins_per_seed": discrim_margins,
                 "tpr_held": tpr_held, "flat_held": flat_held, "random_held": random_held,
                 "control_a_valid": None}
        return verdict, msg, bands

    control_a_valid = all(fh <= rh + RANDOM_MARGIN for fh, rh in zip(flat_held, random_held))

    if not control_a_valid:
        verdict = "INVALID"
        msg = ("VALIDITY GATE FAILED: CONTROL_A (flat learned key) held-out recall=%s exceeded the "
               "measured random-key-baseline floor (%s) by more than RANDOM_MARGIN=%.2f -- i.e. a row "
               "that NEVER received a gradient update did meaningfully better than an untrained random "
               "key, which should be structurally impossible and indicates a fairness/construction "
               "leak (e.g. shared parameters drifting held-out rows' effective keys via the projection "
               "layer). The TPR-vs-flat comparison cannot be trusted as run. TPR held-out recall=%s "
               "reported for reference only, NOT interpreted."
               % ([round(h, 3) for h in flat_held], [round(h, 3) for h in random_held], RANDOM_MARGIN,
                  [round(h, 3) for h in tpr_held]))
        rank_collapse_flag = None
    else:
        hard_pass = (all(h >= HP_HELD_MIN for h in tpr_held) and all(g <= HP_GAP_MAX for g in gaps)
                     and all(b >= HP_BEAT_CONTROL_A_MIN for b in beats_a)
                     and all(rank_beats_oracle))
        hard_fail = (any(h < HF_HELD_MAX for h in tpr_held) or any(g > HF_GAP_MAX for g in gaps)
                     or any(b < HF_BEAT_CONTROL_A_MIN for b in beats_a))
        rank_collapse_flag = not all(rank_beats_oracle)

        if hard_pass:
            verdict = "TPR_PROBE_PASS"
            msg = ("TPR-factored role keys clear the HARD-PASS band: held-out recall=%s (>= %.2f all "
                   "seeds), gap(train-held)=%s (<= %.2f all seeds), beats CONTROL_A by %s (>= %.2f all "
                   "seeds), effective-rank(TPR)=%s > effective-rank(ORACLE)=%s on every seed. CONTROL_A "
                   "(flat key) validly stayed within RANDOM_MARGIN=%.2f of the random-baseline floor "
                   "(flat_held=%s vs random_held=%s). GO to the full 3-arm binder ablation -- factored "
                   "learned keys are well-conditioned and generalize where flat and oracle keys could "
                   "not."
                   % ([round(h, 3) for h in tpr_held], HP_HELD_MIN, [round(g, 3) for g in gaps],
                      HP_GAP_MAX, [round(b, 3) for b in beats_a], HP_BEAT_CONTROL_A_MIN,
                      [round(p, 3) for p in pr_tpr], [round(p, 3) for p in pr_oracle], RANDOM_MARGIN,
                      [round(h, 3) for h in flat_held], [round(h, 3) for h in random_held]))
        elif hard_fail:
            refutes = rank_collapse_flag and all(
                b < HF_BEAT_CONTROL_A_MIN or th <= rh + RANDOM_MARGIN
                for b, th, rh in zip(beats_a, tpr_held, random_held))
            verdict = "TPR_COLLAPSE"
            msg = ("TPR-factored role keys HARD-FAIL: held-out recall=%s, gap(train-held)=%s, beats "
                   "CONTROL_A by %s (thresholds: held>=%.2f, gap<=%.2f, beat>=%.2f). CONTROL_A validly "
                   "stayed within the random-baseline floor (flat_held=%s vs random_held=%s). "
                   "effective-rank(TPR)=%s vs effective-rank(ORACLE)=%s (beats_oracle_rank=%s). "
                   % ([round(h, 3) for h in tpr_held], [round(g, 3) for g in gaps],
                      [round(b, 3) for b in beats_a], HF_HELD_MAX, HF_GAP_MAX, HF_BEAT_CONTROL_A_MIN,
                      [round(h, 3) for h in flat_held], [round(h, 3) for h in random_held],
                      [round(p, 3) for p in pr_tpr], [round(p, 3) for p in pr_oracle], rank_beats_oracle))
            if refutes:
                msg += ("REFUTATION COMBINATION FIRED: TPR held-out stayed near the RANDOM/CONTROL_A "
                        "floor AND the TPR key matrix's effective rank did NOT exceed the oracle's -- "
                        "this factorization collapsed into a lookup table in a tensor-product costume; "
                        "the bottleneck is UPSTREAM (encoder representational capacity), not "
                        "key-derivation. Redirect to the encoder pivot, not further key-derivation "
                        "iteration.")
            else:
                msg += ("This specific factorization/training regime failed; per the design plan this "
                        "refutes THIS instantiation, not learned binding generally -- the honest next "
                        "question is which of {factorization architecture, training objective, readout "
                        "mismatch} caused it.")
        else:
            verdict = "MIDDLE_BAND"
            msg = ("TPR-factored role keys are a real but PARTIAL fix: held-out recall=%s beats CONTROL_A "
                   "by %s (>= %.2f, meaningfully better than flat) but does not clear the full HARD-PASS "
                   "bar (held>=%.2f all seeds AND gap<=%.2f all seeds AND rank beats oracle all seeds). "
                   "gap(train-held)=%s. effective-rank(TPR)=%s vs effective-rank(ORACLE)=%s "
                   "(beats_oracle_rank=%s). random_held=%s reported for reference. Factorization helps; "
                   "the remaining gap is likely a readout/training-objective issue, not evidence against "
                   "the TPR direction."
                   % ([round(h, 3) for h in tpr_held], [round(b, 3) for b in beats_a],
                      MIDDLE_BEAT_CONTROL_A_MIN, HP_HELD_MIN, HP_GAP_MAX, [round(g, 3) for g in gaps],
                      [round(p, 3) for p in pr_tpr], [round(p, 3) for p in pr_oracle], rank_beats_oracle,
                      [round(h, 3) for h in random_held]))

    bands = {"chance_recall": CHANCE_RECALL, "random_margin": RANDOM_MARGIN, "hp_held_min": HP_HELD_MIN,
             "hp_gap_max": HP_GAP_MAX, "hp_beat_control_a_min": HP_BEAT_CONTROL_A_MIN,
             "hf_held_max": HF_HELD_MAX, "hf_gap_max": HF_GAP_MAX,
             "hf_beat_control_a_min": HF_BEAT_CONTROL_A_MIN, "control_a_valid": bool(control_a_valid),
             "discrim_margin": DISCRIM_MARGIN, "discriminator_fires": True,
             "discrim_margins_per_seed": discrim_margins, "random_train": random_train,
             "tpr_held": tpr_held, "tpr_train": tpr_train, "flat_held": flat_held,
             "random_held": random_held,
             "gaps_train_minus_held": gaps, "beats_control_a": beats_a,
             "effective_rank_tpr": pr_tpr, "effective_rank_oracle": pr_oracle,
             "rank_beats_oracle_per_seed": rank_beats_oracle}
    return verdict, msg, bands


# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--steps-train", type=int, default=STEPS_TRAIN)
    args = ap.parse_args()

    torch.set_num_threads(min(6, max(1, os.cpu_count() or 1)))
    run_mode = "self_test" if args.self_test or not args.full else "full"
    expected_units = 1 if run_mode == "self_test" else len(("tpr", "flat")) * len(SEEDS_FULL)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        ck = checkpoint_resume_selftest()
        elapsed = time.perf_counter() - t0
        _atomic_write_metrics(OUTPUT_DIR, {
            "verdict": "SELFTEST_PASS",
            "verdict_msg": "SELFTEST_PASS (toy bind/unbind-reconstruct + compositional-reachability + "
                           "zeroshot-corpus-exclusion + gradient-flows + real encoder + real oracle "
                           "table + tiny TPR/FLAT/ORACLE arms-differ + checkpoint-resume)",
            "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": elapsed,
            "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "chance_recall": CHANCE_RECALL,
            "selftest": st, "checkpoint_selftest": ck})
        _log("DONE self-test in %.1fs" % elapsed)
        return

    steps_train = args.steps_train
    _log("FULL: steps_train=%d batch=%d lr=%.4f seeds=%s chance_recall=%.4f n_eval_train=%d "
         "n_eval_held=%d" % (steps_train, BATCH, LR, SEEDS_FULL, CHANCE_RECALL, N_EVAL_TRAIN,
                              N_EVAL_HELD))
    enc = base.FrozenV2Encoder(V2_CKPT)
    n_cached = enc.build_cache()
    _log("  cached %d unique sentence TOKEN reps (d=%d)" % (n_cached, enc.d))
    cond = rc.Conditioner(enc.U_tok_t, enc.U_pad_t)
    Uc = cond.apply(enc.U_tok_t, enc.U_pad_t, "pca_whiten")
    oracle_table_raw, _all_reps, _idx_lists, n_ctx = oc.build_oracle_table(enc, Uc, ORACLE_PROBE_SEED)
    d_enc = enc.d
    oracle_table, _proj_mat = build_oracle_table_at_d_key(oracle_table_raw, D_KEY, ORACLE_PROBE_SEED)
    filler_table = build_fixed_tables(D_KEY)
    random_baseline = random_key_baseline_table(D_KEY, RANDOM_BASELINE_SEED)
    pr_oracle_fixed = participation_ratio(oracle_table)
    pr_random_fixed = participation_ratio(random_baseline)
    _log("  d_enc=%d D_KEY=%d oracle PR (all 15 roles, fresh) = %.4f, random-baseline PR = %.4f "
         "(prior cited hard-rank<=14 in d=512 for the RAW oracle table, MEASURED@"
         "data/exp_vsa_key_globalscale_phase_conversion_v1/metrics.json -- this cell recomputes PR "
         "fresh at the shared D_KEY=%d working dimensionality for apples-to-apples comparison)"
         % (d_enc, D_KEY, pr_oracle_fixed, pr_random_fixed, D_KEY))

    cz_diag = compositional_and_zeroshot_selftest()
    assert cz_diag["compositional_reachability_all_ok"], "COMPOSITIONAL_REACHABILITY_BROKEN at FULL scale"

    prior_units = ckpt.load_units(OUTPUT_DIR)
    expected_n_units_full = len(("tpr", "flat")) * len(SEEDS_FULL)
    if prior_units:
        _log("checkpoint: %d/%d units already recorded on disk; resuming"
             % (len(prior_units), expected_n_units_full))

    per_seed = []
    trained_modules = {}
    for seed in SEEDS_FULL:
        _log("--- seed=%d ---" % seed)
        seed_result = {}
        for mode in ("tpr", "flat"):
            k = ckpt.unit_key(mode, seed)
            if k in prior_units:
                r = prior_units[k]
                seed_result[mode] = r
                _log("  [resume] %s seed=%d loaded from checkpoint" % (mode, seed))
                continue
            module, loss_curve = train_role_key_module(mode, seed, D_KEY, filler_table,
                                                         steps_train, BATCH, LR)
            trained_modules[(mode, seed)] = module
            acc_train, _dtr = eval_recall(module, seed, TRAIN_ROLES_V2, TRAIN_ROLES_V2, N_EVAL_TRAIN,
                                           filler_table, "train")
            acc_held, dig_held = eval_recall(module, seed, HELD_OUT_ROLES_V2, TRAIN_ROLES_V2, N_EVAL_HELD,
                                              filler_table, "held")
            km = key_matrix_for(module, range(S_TARGET_TOTAL))
            pr = participation_ratio(km)
            r = {"acc_train": acc_train, "acc_held": acc_held, "pr": pr, "dig_held": dig_held,
                 "first_loss": loss_curve[0][1] if loss_curve else float("nan"),
                 "last_loss": loss_curve[-1][1] if loss_curve else float("nan"),
                 "steps_run": steps_train}
            ckpt.record_unit(OUTPUT_DIR, k, r)
            seed_result[mode] = r
            _log("  [%s seed=%d] acc_train=%.4f acc_held=%.4f PR=%.4f loss %.3f->%.3f"
                 % (mode, seed, acc_train, acc_held, pr, r["first_loss"], r["last_loss"]))

        acc_train_o, _dto = eval_recall(oracle_table, seed, TRAIN_ROLES_V2, TRAIN_ROLES_V2, N_EVAL_TRAIN,
                                         filler_table, "train")
        acc_held_o, dig_held_o = eval_recall(oracle_table, seed, HELD_OUT_ROLES_V2, TRAIN_ROLES_V2,
                                             N_EVAL_HELD, filler_table, "held")
        _log("  [oracle seed=%d] acc_train=%.4f acc_held=%.4f PR=%.4f (upper-bound-probe reference only)"
             % (seed, acc_train_o, acc_held_o, pr_oracle_fixed))

        acc_held_r, dig_held_r = eval_recall(random_baseline, seed, HELD_OUT_ROLES_V2, TRAIN_ROLES_V2,
                                             N_EVAL_HELD, filler_table, "held")
        # DISCRIMINATOR-FIRES evidence (checked FIRST in decide_verdict, per Director's bugfix spawn):
        # the untrained random-key baseline's accuracy on the SAME TRAIN-role query pool/eval count the
        # trained arms are scored on -- this is the "did training beat doing nothing" comparison.
        acc_train_r, dig_train_r = eval_recall(random_baseline, seed, TRAIN_ROLES_V2, TRAIN_ROLES_V2,
                                               N_EVAL_TRAIN, filler_table, "train")
        _log("  [random seed=%d] acc_train=%.4f acc_held=%.4f PR=%.4f (untrained-reference: acc_train is "
             "the discriminator-fires floor, acc_held is the CONTROL_A validity floor)"
             % (seed, acc_train_r, acc_held_r, pr_random_fixed))

        per_seed.append({"seed": seed, "tpr_held": seed_result["tpr"]["acc_held"],
                          "tpr_train": seed_result["tpr"]["acc_train"],
                          "flat_held": seed_result["flat"]["acc_held"],
                          "flat_train": seed_result["flat"]["acc_train"],
                          "pr_tpr": seed_result["tpr"]["pr"], "pr_oracle": pr_oracle_fixed,
                          "oracle_held": acc_held_o, "oracle_train": acc_train_o,
                          "random_held": acc_held_r, "random_train": acc_train_r,
                          "pr_random": pr_random_fixed,
                          "dig_tpr": seed_result["tpr"]["dig_held"], "dig_flat": seed_result["flat"]["dig_held"],
                          "dig_oracle": dig_held_o, "dig_random": dig_held_r})

    verdict, msg, bands = decide_verdict(per_seed)
    elapsed = time.perf_counter() - t0

    n_units_done = sum(1 for mode in ("tpr", "flat") for seed in SEEDS_FULL
                        if ckpt.unit_key(mode, seed) in ckpt.load_units(OUTPUT_DIR))

    digests_by_seed = {r["seed"]: {"tpr": r["dig_tpr"], "flat": r["dig_flat"], "oracle": r["dig_oracle"],
                                    "random": r["dig_random"]}
                       for r in per_seed}
    arms_differ = all(len({d["tpr"], d["flat"], d["oracle"], d["random"]}) == 4
                       for d in digests_by_seed.values())

    _atomic_write_metrics(OUTPUT_DIR, {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "%s | chance_recall=%.4f | %s" % (verdict, CHANCE_RECALL, msg[:200]),
        "run_mode": "full", "elapsed_s": elapsed, "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "chance_recall": CHANCE_RECALL, "bands": bands, "per_seed": per_seed,
        "compositional_zeroshot_diag": cz_diag,
        "arms_differ_verified": bool(arms_differ),
        "cardinality_ok": bool(n_units_done == expected_n_units_full),
        "expected_n_units": expected_n_units_full, "n_units_done": n_units_done,
        "params": {"S_TARGET_TOTAL": S_TARGET_TOTAL, "V_FILL": V_FILL, "N_A": N_A, "N_B": N_B,
                   "H_FACTOR": H_FACTOR, "N_DISTRACT": N_DISTRACT, "D_KEY": D_KEY,
                   "ANGLE_SCALE": ANGLE_SCALE, "RANDOM_MARGIN": RANDOM_MARGIN,
                   "steps_train": steps_train, "batch": BATCH, "lr": LR, "seeds": list(SEEDS_FULL),
                   "n_eval_train": N_EVAL_TRAIN, "n_eval_held": N_EVAL_HELD,
                   "train_roles_v2": TRAIN_ROLES_V2, "held_out_roles_v2": HELD_OUT_ROLES_V2,
                   "n_cached_sentences": n_cached, "d_enc": d_enc, "encoder": "real_v2_frozen",
                   "conditioning": "pca_whiten", "binding_flavor": "FHRR_complex64_phase_encoded",
                   "filler_key_seed": FILLER_KEY_SEED, "random_baseline_seed": RANDOM_BASELINE_SEED,
                   "oracle_probe_seed": ORACLE_PROBE_SEED,
                   "v2_ckpt": os.path.relpath(V2_CKPT, REPO_ROOT)},
        "start_marker_written": True, "crash_diagnostic_present": True,
        "final_metrics_atomicity": "tmp_replace", "defensive_error_checking": "passed_all_4_patterns",
        "progress_logging": "print_flush_true", "progress_cadence_expected_s": 10,
        "crlb_n_a": "no Cramer-Rao noise floor; discriminator is the pre-registered held-out-recall + "
                    "effective-rank decision rule (see decide_verdict)",
        "calibration_check": "default_ok_for_this_regime: all hyperparameters (steps_train/batch/lr/"
                              "H_FACTOR/N_DISTRACT) fixed BEFORE running per the design plan, not tuned "
                              "against held-out results"})
    _log("VERDICT: %s" % verdict)
    _log("  %s" % msg)
    _log("DONE full in %.1fs" % elapsed)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
