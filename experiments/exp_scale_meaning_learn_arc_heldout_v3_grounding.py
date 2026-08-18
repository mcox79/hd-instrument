"""SCALE meaning-learning v3 grounding (experiential self-teacher): v2's from-scratch transformer + a
JOINT foundation-EXPERIENTIAL-GROUNDING auxiliary loss, teacher-free in the borrowed-vector sense (the
"teacher" is MEASURED HUMAN EXPERIENTIAL RATINGS -- Lancaster sensorimotor norms -- not a borrowed
transformer embedding), tested can-fail on held-out-NEW SEMANTIC and/or RELATIONAL AUC.

SIBLING CELL to exp_scale_meaning_learn_arc_heldout_v3_relobj.py (relational self-teacher, R1/R3). This
cell is the SECOND brain-faithful representation lever: bake EXPERIENTIAL GROUNDING into the encoder
DURING TRAINING (not just eval-time cosine fusion, the "un-maxed lever" this cell targets). Reuses the
relobj cell's ENTIRE leak-proof data/eval/checkpoint pipeline by IMPORT (see "Reuse discipline" below) --
the only genuinely new code is the grounding objective itself (GroundHead + L_ground + prep + verdict).

================================================================================================
BRAIN-FIDELITY ELEMENT AUDIT (USER 2026-07-28 mandate -- documented BEFORE building, not after)
================================================================================================
THE ELEMENT: how does the brain ground concept MEANING in experience, and does L_ground match it?

1. GROUNDED-IN-EXPERIENTIAL-FEATURES (Barsalou 1999 Perceptual Symbol Systems; Binder et al. 2016 "Toward
   a brain-based componential semantic representation," Cereb Cortex): a concept's neural representation
   is NOT an amodal symbolic tag -- it is (partially) constituted by re-activated sensorimotor/affective
   traces from perception and action; Binder's own method PREDICTS voxel-wise brain activation from a
   concept's rated experiential-feature profile (vision, audition, touch, action-effector, etc.), i.e. the
   feature-profile <-> neural-representation mapping is literally the object of study. MATCH: L_ground
   aligns the encoder's pooled contextual rep (via a trained projection head) to the concept's MEASURED
   Lancaster sensorimotor rating vector (11 perceptual+action modalities: aud/gus/hap/int/olf/vis/foot/
   hand/head/mouth/torso) -- structurally the same feature-profile-alignment relationship Binder's model
   assumes, applied as a TRAINING signal on the SAME encoder used for language (not a downstream probe).
2. PREDICTION-ERROR-DRIVEN (grounded cognition is not one-shot supervised labeling; it is repeated,
   error-corrective exposure -- perceptual learning theory, predictive-coding accounts of concept
   acquisition e.g. Clark 2013). MATCH: L_ground's gradient IS a prediction-error signal (predicted
   feature-profile vs measured, cosine loss), computed EVERY ground_every steps and backpropagated
   JOINTLY with L_mlm's own prediction-error signal into the SAME encoder weights -- genuinely joint
   (not a frozen-feature two-stage probe, the same discipline the relobj sibling cell established).
3. PARTIAL FOR ABSTRACT CONCEPTS (Binder himself + Vigliocco et al. 2009's finding that abstract concepts
   ground preferentially in AFFECTIVE/emotional rather than sensorimotor features; Lakoff & Johnson's
   metaphor-mediated grounding for abstraction). MATCH BY CONSTRUCTION: L_ground fires ONLY for concepts
   with a MEASURED Lancaster rating (the `has_lancaster` mask); a concept without norms contributes ZERO
   gradient to L_ground (never penalized, never forced toward an invented target) -- this directly encodes
   "grounding attenuates/is absent where there is no direct sensorimotor content," rather than papering
   over missing coverage with an imputed value. MEASURED@this session (nodes.jsonl scan): of the 23,542
   single-token grounded/lexname-bearing concepts, 16,976 (72%) have a Lancaster group at all, 13,041 (55%)
   at this cell's degree>=2 filter -- HIGHER than the previously-banked "4-6% of abstract SCIENCE terms"
   caveat, because that figure was scoped to a narrow abstract-vocabulary subset, not this cell's full
   concrete-skewed WordNet+ARC concept universe. Coverage is real and substantial, not a token gesture.
4. DECLARED GAP vs the brain (not glossed over): the brain's grounding is SITUATED RE-ENACTMENT -- a
   concept's meaning is (re-)constructed through simulated perception/action AT COMPREHENSION TIME
   (Barsalou's "situated simulation"), multi-modal and temporally dynamic. This cell grounds via STATIC
   crowd-rated feature vectors (a compressed, introspective proxy for the experiential trace, not the
   trace itself) FIT ONCE INTO ENCODER WEIGHTS AT TRAINING TIME -- no dynamic re-simulation at retrieval/
   comprehension time. This is a real, acknowledged shortfall relative to the brain's mechanism (same
   class of gap the substrate's whole grounding-testbed program already carries), but it is CLOSER to the
   brain's encoding-time mechanism than pure eval-time cosine fusion (v1/v2's RAW_GROUNDING arm): the norms
   now shape the encoder's own weights through gradient descent, not just a post-hoc score blend.
CONCLUSION: L_ground is a legitimate, if partial, brain-faithful instantiation of experiential grounding-
as-training-signal. The can-fail test below is honest about the two live possible outcomes: (a) grounding
transfers into the encoder's learned geometry (validates the encoding-time mechanism over eval-time fusion),
or (b) it does not (grounding stays too partial/architecture-bound to move held-out-NEW geometry at this
scale -- an honest null, reported as such, not spun).

================================================================================================
REUSE DISCIPLINE (why this file is short): imports the ENTIRE leak-proof data/eval/checkpoint pipeline
from exp_scale_meaning_learn_arc_heldout_v3_relobj.py (module alias `_r`) UNCHANGED -- concept universe
load, count/collect/tokenize passes, BPE build, TinyTransformer, encode_concept_text_reps, semantic +
relational eval (identical arm family/leak gates/controls), baseline-reuse-or-CITED-fallback (v2 ckpt),
checkpoint/eval-rep bundle I/O. THE RUNNING v3_relobj CELL FILE IS NEVER EDITED -- this is a read-only
import (safe: cells run one-process-per-invocation, so importing relobj's module here does not touch or
interfere with the separately-running relobj process on the GPU box). Deterministic held-out split is
IDENTICAL across v2/v3_relobj/v3_grounding (same CONCEPT_SPLIT_SALT, imported unchanged) so all three
runs share the exact same held-out-NEW concepts -- genuinely comparable, ONE variable = the training
OBJECTIVE (relational self-teacher vs experiential-grounding self-teacher vs MLM-only baseline).
_r.ANCHOR_NAME is rebound to THIS cell's anchor name immediately after import so every borrowed print/
log/heartbeat line inside the reused eval/baseline functions is labeled correctly for live audit (cosmetic
fix only; the borrowed functions carry no anchor-name-dependent LOGIC, verified by inspection before reuse
-- functions that DID embed anchor-coupled behavior, e.g. _save_checkpoint/_save_inprogress_ckpt/
_write_start_marker/_write_crash_metrics/_log, are reimplemented locally instead of imported).
THE NEW CODE (genuinely this cell's own): GroundHead (linear projection + L2-normalize), the Lancaster-
only standardized target-vector builder (TRAIN-eval-fit, leak-safe), groundobj_prep (anchor pool = TRAIN-
only concepts with Lancaster coverage + postings; a HELD concept can never be an anchor -- verified by an
explicit zero-intersection assertion, not just filtered-and-hoped), mlm_train_groundobj (the joint
L = L_mlm + lambda_ground * L_ground training loop), run_one_seed, build_verdict_ground.

WHAT (the run): identical DATA-INTEGRITY PREFLIGHT / CONCEPT-LEVEL held-out split / MLM pretraining / concept-
meaning-as-mention-pooled-rep / leak-proof held-out-NEW eval as v2/v3_relobj (see those docstrings for the
full mechanics); the ONE difference is the training objective: every ground_every MLM steps, a batch of
TRAIN-split concepts WITH a measured Lancaster sensorimotor rating is sampled; the SAME TinyTransformer's
SAME model.pooled() rep (used for MLM + for the eventual concept-text-rep) is projected through a small
trained head and cosine-aligned to the concept's standardized Lancaster vector; L = L_mlm + lambda_ground *
L_ground at those steps, else L = L_mlm. L_mlm and L_ground logged SEPARATELY.

ARMS (per-query AUC; base 0.5) -- SAME semantic/relational arms as v2/v3_relobj, computed on the v3
(grounding) encoder, PLUS the reused/cited MLM-ONLY baseline (v2's checkpoint, not retrained here):
  RAW_GROUNDING  : cosine over raw 20d grounding norms, NO learning.               [validity floor]
  RAW_TEXT (TEXT_ARM) : cosine over the joint-objective-trained text-rep alone.     [OBJ arm -- the test]
  FUSED / ZAVG / WTUNED / SELECTED : same leak-proof fusion family as v2/v3_relobj (reported).
  RANDOM_INIT    : cosine over text-rep from an UNTRAINED transformer.             [isolate learning]
  COLLAPSE_SHUFFLE: text-reps permuted across concept ids.                         [can-fail / leak witness ~0.5]
  POPULARITY     : rank candidates by mention-frequency / train-degree only.        [validity ~0.5]
  BASELINE_MLM_ONLY (semantic_eval + relational_eval, reused from v2's ckpt_seed_<seed>.pt where present,
    else CITED historical): the ONE-variable comparison point (same architecture/data, MLM objective only).

THE ONE NUMBER (pre-registered bands, BEFORE running; see preregs/2026-07-28_scale_meaning_learn_arc_
heldout_v3_grounding.md for the full envelope-fail-band spec). Per task instruction, the pass condition is
"SEMANTIC and/or RELATIONAL AUC lifts meaningfully" -- PRIMARY framing is SEMANTIC (grounding targets a
concept's own feature content, most naturally probed by same-lexname/meaning-similarity; relational
structure is a more indirect target for a content-grounding signal), RELATIONAL is an accepted alternate
win condition, both reported and gated:
  HARD_PASS_GROUNDOBJ_CLEAN_WIN = (TEXT_ARM semantic-AUC - BASELINE_MLM_ONLY semantic-AUC >= +0.03 on BOTH
    seeds, per-seed strictly > 0) OR (TEXT_ARM relational-AUC - BASELINE_MLM_ONLY relational-AUC >= +0.03
    on BOTH seeds, per-seed strictly > 0) -- EITHER clears it -- AND semantic does NOT regress > 0.02 vs
    baseline (objective-conflict guard, always enforced regardless of which arm wins), AND L_ground loss
    visibly decreases (real learning), AND the anchor-pool-excludes-held leak gate holds (zero-witness),
    AND validity holds (COLLAPSE in [0.44,0.56], POPULARITY in [0.44,0.56], RAW_GROUNDING >= 0.55, power ok).
  HARD_FAIL_NO_TRANSFER = both semantic AND relational margins stay within +/-0.02 of baseline despite
    L_ground loss visibly decreasing => grounding is too PARTIAL / architecture-bound to transfer into the
    encoder's held-out-NEW geometry at this scale -- an honest, reportable null (per task instruction: "if
    grounding too partial to help at scale -> report honestly"), NOT a training-dynamics bug.
  HARD_FAIL_GROUND_OBJECTIVE_NOT_LEARNING = L_ground never fired or never decreased -> training-dynamics
    bug, margin numbers not trustworthy.
  HARD_FAIL_LEAK = a held-out concept found in the grounding-loss anchor pool (should be structurally
    impossible; this is the last-line witness, not the primary gate).
  MIDDLE_BAND_GROUNDOBJ_PARTIAL = a margin positive but < +0.03, or semantic regresses beyond the guard.
  HARD_FAIL_INVALID = validity gate fails (collapse/popularity/raw-grounding/power controls).

HARD INVARIANTS (project locks): the grounding "teacher" is MEASURED HUMAN EXPERIENTIAL RATINGS (Lancaster
  sensorimotor norms), NOT a borrowed transformer/GloVe/BGE embedding anywhere -- token embeddings +
  Transformer are learned FROM SCRATCH by MLM exactly as in v2/v3_relobj; only the SUPERVISION TARGET for
  L_ground is external data (grounded human ratings are explicitly ALLOWED per project convention -- they
  are measured experience, not a borrowed learned representation). INDUCTIVE (held-out concepts never an
  L_ground anchor/target; encoded only at eval time from their own text+grounding). LEAK-PROOF (concept-
  level scrub inherited from v2 unchanged + a SECOND, grounding-specific gate: the anchor pool is built
  from split["train_eval_idx"] ONLY, with an explicit post-hoc zero-intersection assertion against
  held_idx). ASCII-only. AI2 ARC Corpus: INTERNAL research use only, do NOT redistribute corpus/derived text.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at run (META_RULE_AF; reused _r._arms_differ hash-test over RAW/TEXT/RANDOM reps)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace + per-seed
#     partials) PLUS periodic mid-training checkpoint (ckpt_seed_<seed>_inprogress.pt, tmp+os.replace,
#     every ckpt_every_steps -- CHECKPOINT-ALWAYS per task mandate)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: AUC discriminator base = 0.5 exactly; collapse + popularity + random-init controls witness it
# - baseline_in_band at smoke: collapse ~0.5; popularity ~0.5; raw_grounding a real >0.55 signal
# - discriminator survives scale: THEORETICAL coverage argument (13,041 Lancaster-eligible TRAIN concepts
#     at FULL, ~55% of the universe -- orders of magnitude above relobj's 2048-landmark pool) + SMOKE
#     preview measures L_ground loss decreasing at reduced scale (option B+C hybrid)
# - HARD_PASS strictly above floor: margin>=0.03 AND per-seed strictly >0 (not at-floor) on the winning arm
# - HP_SCOPE: gates apply to ARM_TEXT (TEXT_ARM, the OBJ arm) semantic-AUC and/or relational-AUC vs
#     BASELINE_MLM_ONLY primary; FUSED/ZAVG/WTUNED/SELECTED arms reported, not gated
# - no sweep axis -> cardinality_ok via EXPECTED_N_UNITS = n_seeds
# - per-unit failure-class instrumentation (no bare except; specific classes -> metrics)
# - calibration_check: default_ok_for_this_regime (AUC base=0.5 analytic; controls witness it empirically)
# - deterministic seeding: sha256 concept split (imported unchanged from _r, same salt) + fixed int seeds +
#     sorted(); no hash()/list(set()); anchor pool is a deterministic sorted() filter
# - real_code_path: --self-test constructs the REAL objects (concept universe, count/collect/tokenize
#     passes, build_bpe, mlm_train_groundobj incl. the L_ground step, groundobj_prep + leak assertion,
#     transformer encode, zero-overlap gate, both evals, baseline-reuse-or-CITED) at N~16
# - progress_logging: print_flush_true (MLM step logs + L_ground step logs + eval logs flush=True) +
#     _heartbeat.jsonl (timeout_s >> 1800)
# - device-agnostic: cuda+AMP on the GPU box, cpu for local smoke; no hard device assumption
"""

import argparse
import glob
import hashlib
import json
import os
import platform
import re
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
    get_output_dir,
    record_gate,
    write_metrics,
    write_partial,
    aggregate_partials,
)

# Reuse the ENTIRE leak-proof data/eval/checkpoint pipeline from the relobj sibling cell (READ-ONLY
# import; the running relobj process is a separate OS process and is never touched by this import --
# see "Reuse discipline" in the module docstring for exactly which functions are safe to borrow).
from experiments import exp_scale_meaning_learn_arc_heldout_v3_relobj as _r  # noqa: E402

ANCHOR_NAME = "scale_meaning_learn_arc_heldout_v3_grounding"
_r.ANCHOR_NAME = ANCHOR_NAME  # relabel borrowed _log/eval_from_reps/eval_baseline_arm print lines (cosmetic only; no borrowed function has anchor-coupled LOGIC, verified by inspection)

# v2 baseline checkpoint dir (BASELINE REUSE, not retrained here -- same convention as v3_relobj)
V2_CKPT_DIR = _r.V2_CKPT_DIR
CITED_BASELINE_RELATIONAL_AUC = _r.CITED_BASELINE_RELATIONAL_AUC
BASELINE_SOURCE_REUSED = _r.BASELINE_SOURCE_REUSED
BASELINE_SOURCE_CITED = _r.BASELINE_SOURCE_CITED

# Arms (identical family/constants to v2/v3_relobj -- imported, not redefined, so eval code stays
# byte-identical across sibling cells)
RAW_ARM = _r.RAW_ARM
TEXT_ARM = _r.TEXT_ARM
FUSED_ARM = _r.FUSED_ARM
FUSE_ZAVG_ARM = _r.FUSE_ZAVG_ARM
FUSE_WTUNED_ARM = _r.FUSE_WTUNED_ARM
FUSE_SELECTED_ARM = _r.FUSE_SELECTED_ARM
RANDINIT_ARM = _r.RANDINIT_ARM
SHUFFLE_ARM = _r.SHUFFLE_ARM
POP_ARM = _r.POP_ARM
PRIMARY_CANDIDATES = _r.PRIMARY_CANDIDATES
SEM_ARMS = _r.SEM_ARMS

# Pre-reg bands (this cell's own; NOT imported -- distinct pass condition from relobj: semantic AND/OR
# relational, per task instruction)
HP_MARGIN_OVER_BASELINE = 0.03    # THE NUMBER: OBJ - BASELINE (semantic or relational) must exceed this
SEM_REGRESSION_MAX = 0.02         # objective-conflict guard: semantic-AUC may not regress more than this
RAW_SIGNAL_MIN = _r.RAW_SIGNAL_MIN
COLLAPSE_BAND = _r.COLLAPSE_BAND
MIN_QUERY_TASKS = _r.MIN_QUERY_TASKS

# ---------------------------------------------------------------------------
# Config profiles (mirror v3_relobj's cfg keys for architecture/data parity; ground_* keys replace rel_*)
# ---------------------------------------------------------------------------
# NOTE (2026-07-28): SELFTEST/SMOKE sized for a SINGLE local CPU blocking call (finish < ~90s each) so
# the local gate runs foreground-to-completion without auto-backgrounding. These are LOCAL GATES ONLY --
# the FULL config that ships to the GPU box is untouched (full scale). Self-test = code-path correctness;
# smoke = discriminator-fires (ground_loss descends on the shared encoder) + arms computed.
SELFTEST_CFG = dict(
    run_mode="selftest", seeds=[7],
    min_deg=2, cap_eval_concepts=250, heldout_count=60, min_mentions_eval=1,
    max_lines=40000, dedup_cap=60000, bpe_sample_lines=12000, cap_mentions=6,
    vocab=512, max_len=24, train_token_budget=250000, max_shards=6,
    d_model=32, n_layers=1, n_heads=2, ffn_mult=2,
    mlm_steps=15, mlm_batch=8, mlm_mask_frac=0.15, mlm_lr=3e-3,
    encode_batch=64, n_freq_buckets=4,
    # experiential-grounding self-teacher -- tiny scale, exercises the real code path
    lambda_ground=0.2, n_ground_batch=12, ground_every=3, min_ground_anchors=4, ckpt_every_steps=6,
)
SMOKE_CFG = dict(
    run_mode="smoke", seeds=[7],
    min_deg=2, cap_eval_concepts=320, heldout_count=100, min_mentions_eval=2,
    max_lines=70000, dedup_cap=90000, bpe_sample_lines=22000, cap_mentions=10,
    vocab=2048, max_len=40, train_token_budget=900000, max_shards=6,
    d_model=96, n_layers=2, n_heads=4, ffn_mult=2,
    mlm_steps=160, mlm_batch=64, mlm_mask_frac=0.15, mlm_lr=3e-3,
    encode_batch=256, n_freq_buckets=5,
    # discriminator-preview scale (option C): ground_every=5 over 160 steps -> ~32 grounding fires
    lambda_ground=0.2, n_ground_batch=48, ground_every=5, min_ground_anchors=20, ckpt_every_steps=60,
)
FULL_CFG = dict(
    run_mode="full", seeds=[7, 13],
    min_deg=2, cap_eval_concepts=None, heldout_count=800, min_mentions_eval=20,
    max_lines=10000000, dedup_cap=6000000, bpe_sample_lines=400000, cap_mentions=128,
    vocab=16000, max_len=128, train_token_budget=130000000, max_shards=16,
    d_model=512, n_layers=6, n_heads=8, ffn_mult=4,
    mlm_steps=60000, mlm_batch=128, mlm_mask_frac=0.15, mlm_lr=3e-4,
    encode_batch=256, n_freq_buckets=8,
    # experiential-grounding self-teacher: anchor pool ~13,041 Lancaster-eligible TRAIN concepts (MEASURED
    # this session, degree>=2 filter); ground_every=8 mirrors relobj's cadence for wall-time parity, but
    # per-step cost is CHEAPER than relobj's InfoNCE (single small linear head + cosine over dim=11, no
    # landmark cross-entropy matrix) so actual overhead should be LESS than relobj's measured +30-40%.
    # lambda_ground RAISED 0.2 -> 1.0 (2026-07-28) after the frozen-head geometry probe showed grounding
    # needs real pressure to transfer into the encoder: at tiny scale a FROZEN head transferred strongly at
    # lambda=5.0 (LSQ Lancaster-alignment delta +0.2552, selective anchor-move +0.0121) but not at 0.2-2.0;
    # FULL fires ~7500 grounding steps (25x the probe's 300) so cumulative pressure at lambda=1.0 sits in
    # the confirmed-transfer regime while the semantic-non-regression guard (<=0.02) protects MLM/meaning.
    lambda_ground=1.0, n_ground_batch=96, ground_every=8, min_ground_anchors=32, ckpt_every_steps=2000,
    ground_pool_chunk=32,   # OOM POOLING FIX (mirrors relobj rel_pool_chunk): chunk the grounding pooled-rows forward
)

_WORD_RE = re.compile(r"[a-z]+")


# ---------------------------------------------------------------------------
# Start marker / crash diagnostics / logging / heartbeat (LOCAL -- own ANCHOR_NAME; per exp_dev.md
# convention "no project-wide helper -- each cell defines its own")
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(
        pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode,
        expected_n_units=expected_n_units, host=platform.node(),
        cuda=bool(torch.cuda.is_available()),
    )
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(
        verdict="CELL_CRASHED",
        verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
        summary=("CELL_CRASHED: %s" % type(exc).__name__),
        elapsed_s=0.0, traceback=traceback.format_exc()[:5000],
        ts_iso=datetime.now(timezone.utc).isoformat(),
        pid=os.getpid(), anchor_name=ANCHOR_NAME,
    )
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _heartbeat(output_dir, unit_idx, total_units, elapsed_s, extra=None):
    row = dict(ts_iso=datetime.now(timezone.utc).isoformat(),
               unit_idx=int(unit_idx), total_units=int(total_units),
               elapsed_s=float(elapsed_s))
    if extra:
        row["extra"] = extra
    try:
        with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a",
                  encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Experiential-grounding self-teacher: Lancaster-only standardized target vectors (TRAIN-eval-fit)
# ---------------------------------------------------------------------------
def _lancaster_target_vectors(universe, split):
    """Standardize the Lancaster 11-dim sensorimotor sub-vector on TRAIN-eval concepts ONLY (leak-safe
    fit), L2-normalize. Returns (target[K,11] float32, has_lancaster[K] bool). has_lancaster mirrors
    universe['gpres'][:,0] (GROUPS order: lancaster is group 0)."""
    n_lan = len(_r.LANCASTER_KEYS)
    vals = universe["vals"]                      # [K,16]: lancaster(11) + concreteness(1) + vad(3) + aoa(1)
    lan = vals[:, :n_lan]
    has_lan = universe["gpres"][:, 0].astype(bool)
    tr = split["train_eval_idx"]
    tr_has = tr[has_lan[tr]]
    if tr_has.shape[0] < 10:
        raise RuntimeError("too few TRAIN-eval concepts with Lancaster coverage (%d) to fit target stats"
                           % tr_has.shape[0])
    import warnings as _w
    with _w.catch_warnings():
        _w.simplefilter("ignore", RuntimeWarning)
        mu = np.nanmean(lan[tr_has], axis=0)
        sd = np.nanstd(lan[tr_has], axis=0)
    mu = np.nan_to_num(mu, nan=0.0)
    sd = np.where(np.isnan(sd) | (sd < 1e-6), 1.0, sd)
    z = (lan - mu[None, :]) / sd[None, :]
    z = np.where(np.isnan(z), 0.0, z).astype(np.float32)
    nrm = np.linalg.norm(z, axis=1, keepdims=True)
    z = np.where(nrm > 1e-8, z / (nrm + 1e-8), z)
    return z, has_lan


def groundobj_prep(universe, split, postings, tok, spec, cfg):
    """Seed-independent grounding prep: Lancaster target vectors, TRAIN-only anchor pool (concepts with
    measured coverage AND >=1 mention posting), concept-window-id cache. LEAK GATE: anchor pool is built
    from non-held concepts only, THEN independently re-verified to have zero intersection with held_idx
    (defense-in-depth, not just filter-and-hope)."""
    target, has_lan = _lancaster_target_vectors(universe, split)
    is_held = split["is_held"]
    cap_m = cfg["cap_mentions"]
    anchor_pool = np.array(
        sorted(i for i in range(universe["K"])
              if (not is_held[i]) and has_lan[i] and postings[i][:cap_m]),
        dtype=np.int64)
    held_set = set(int(x) for x in split["held_idx"].tolist())
    n_leak = sum(1 for a in anchor_pool.tolist() if a in held_set)
    if n_leak != 0:
        raise RuntimeError("LEAK: %d held-out concepts present in grounding-loss anchor pool" % n_leak)
    needed = sorted(set(anchor_pool.tolist()))
    win_ids = _r.build_concept_window_ids(tok, spec, postings, cap_m, cfg["max_len"], needed)
    return dict(target=target, has_lancaster=has_lan, anchor_pool=anchor_pool, win_ids=win_ids,
               n_anchor_pool=int(anchor_pool.shape[0]),
               n_eligible_total=int(has_lan.sum()),
               n_held_with_lancaster=int(has_lan[split["held_idx"]].sum()),
               n_leak_verified_zero=(n_leak == 0))


# ---------------------------------------------------------------------------
# Grounding projection head: pooled encoder rep -> Lancaster-dim, L2-normalized
# ---------------------------------------------------------------------------
class GroundHead(torch.nn.Module):
    """FIXED (non-trainable) random readout from the encoder's pooled rep to Lancaster-dim.

    WHY FROZEN (2026-07-28 can-fail finding): with a TRAINABLE linear head, the geometry probe showed the
    head absorbs the Lancaster alignment (its ground_loss descends) while the shared ENCODER barely moves
    and NOT selectively at anchors (anchor-vs-nonanchor selective move ~0.0000, LSQ-readout lift +0.0048
    even at lambda=2.0) -- i.e. grounding never pressures the representation, so grounding-alone would land
    HARD_FAIL_NO_TRANSFER by construction. A FIXED random projection removes the absorbing free parameters:
    to reduce L_ground the encoder MUST arrange its pooled rep so a fixed readout points at the concept's
    experiential-feature target. This is also MORE brain-faithful (a fixed downstream readout; the
    representation earns the alignment, per the earn-meaning discipline) -- no borrowed vectors (the W is a
    deterministic Gaussian, column-normalized, seeded by a fixed constant so it is identical across
    training seeds for a fair comparison). No trainable parameters -> not added to the optimizer."""

    def __init__(self, d_model, out_dim, proj_seed=20260728):
        super().__init__()
        g = torch.Generator().manual_seed(int(proj_seed))
        W = torch.randn(d_model, out_dim, generator=g)
        W = W / (W.norm(dim=0, keepdim=True) + 1e-8)   # each target dim reads a unit-norm encoder direction
        self.register_buffer("W", W)                    # buffer = persisted, moved with .to(device), NO grad

    def forward(self, z):
        p = z @ self.W
        return p / (p.norm(dim=1, keepdim=True) + 1e-8)


def _save_inprogress_ckpt_ground(out_dir, seed, model, head, opt, step, spec, cfg):
    """Periodic mid-training checkpoint (CHECKPOINT-ALWAYS, non-negotiable). Atomic tmp+os.replace.
    Includes the small GroundHead state for genuine resumability (cheap; encoder dominates size)."""
    try:
        payload = dict(
            state_dict={k: v.detach().cpu() for k, v in model.state_dict().items()},
            head_state_dict={k: v.detach().cpu() for k, v in head.state_dict().items()},
            opt_state=opt.state_dict(), step=int(step), seed=int(seed),
            spec=spec, model_cfg=dict(vocab=int(spec["size"]), max_len=int(cfg["max_len"]),
                                       d_model=int(cfg["d_model"]), n_layers=int(cfg["n_layers"]),
                                       n_heads=int(cfg["n_heads"]), ffn_mult=int(cfg["ffn_mult"]),
                                       pad_id=int(spec["pad"])),
            ts_iso=datetime.now(timezone.utc).isoformat(), anchor=ANCHOR_NAME,
        )
        tmp = os.path.join(out_dir, "ckpt_seed_%d_inprogress.pt.tmp" % seed)
        final = os.path.join(out_dir, "ckpt_seed_%d_inprogress.pt" % seed)
        torch.save(payload, tmp)
        os.replace(tmp, final)
        return True
    except (OSError, RuntimeError) as e:
        _log("  WARN mid-training checkpoint save failed (%s): %s" % (type(e).__name__, str(e)[:200]))
        return False


def mlm_train_groundobj(stream, spec, cfg, device, seed, out_dir, hb_total, groundobj):
    """MLM-pretrain the transformer + a JOINT experiential-grounding cosine-alignment self-teacher term.
    L = L_mlm + lambda_ground * L_ground every ground_every steps, else L = L_mlm. SAME encoder, SAME
    optimizer.step() -- genuinely joint (mirrors v3_relobj's joint-objective discipline)."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    max_len = cfg["max_len"]
    model = _r.TinyTransformer(spec["size"], max_len, cfg["d_model"], cfg["n_layers"],
                               cfg["n_heads"], cfg["ffn_mult"], spec["pad"]).to(device)
    ground_dim = int(groundobj["target"].shape[1])
    head = GroundHead(cfg["d_model"], ground_dim).to(device)   # FIXED random readout -- no trainable params
    n_head_trainable = sum(p.numel() for p in head.parameters())   # == 0 by design (frozen readout)
    n_params = sum(p.numel() for p in model.parameters())
    _log("  model params=%.2fM head_trainable_params=%d (frozen readout) device=%s vocab=%d d=%d L=%d ground_dim=%d"
         % (n_params / 1e6, n_head_trainable, device.type, spec["size"], cfg["d_model"], cfg["n_layers"], ground_dim))
    n_win = stream.shape[0] // max_len
    if n_win < 4:
        raise RuntimeError("train stream too short: %d tokens, %d windows" % (stream.shape[0], n_win))
    windows = stream[:n_win * max_len].reshape(n_win, max_len)
    # ONLY the encoder is optimized -- the GroundHead is a FIXED random readout (frozen; see GroundHead
    # docstring), so L_ground gradients flow into the ENCODER, not an absorbing head.
    opt = torch.optim.AdamW(model.parameters(), lr=cfg["mlm_lr"])
    use_amp = (device.type == "cuda")
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)
    g = np.random.default_rng(seed + 5)
    ground_rng = np.random.default_rng(seed + 8191)
    bs = min(cfg["mlm_batch"], n_win)
    mask_frac = cfg["mlm_mask_frac"]
    mask_id = spec["mask"]
    log_every = max(1, cfg["mlm_steps"] // 10)
    ckpt_every = max(1, int(cfg.get("ckpt_every_steps", cfg["mlm_steps"])))

    anchor_pool = groundobj["anchor_pool"]
    target_np = groundobj["target"]
    win_ids = groundobj["win_ids"]
    ground_every = max(1, int(cfg["ground_every"]))
    lambda_ground = float(cfg["lambda_ground"])
    ground_ok = anchor_pool.shape[0] >= cfg["min_ground_anchors"]

    mlm_loss_curve = []
    ground_loss_curve = []
    n_ground_fired = 0
    n_ckpt_saves = 0

    last_loss = float("nan")
    t0 = time.perf_counter()
    model.train()
    head.train()
    for step in range(cfg["mlm_steps"]):
        sel = g.integers(0, n_win, size=bs)
        ids = torch.from_numpy(windows[sel].astype(np.int64)).to(device)
        rnd = torch.rand(ids.shape, device=device)
        mask = rnd < mask_frac
        if int(mask.sum()) < 1:
            mask[:, 0] = True
        target_ids = ids.clone()
        inp = ids.clone()
        inp[mask] = mask_id
        opt.zero_grad(set_to_none=True)
        with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=use_amp):
            logits = model.mlm_logits(inp)
            mlm_loss = torch.nn.functional.cross_entropy(logits[mask], target_ids[mask])
        loss = mlm_loss
        ground_loss_val = None
        if ground_ok and (step % ground_every == 0):
            a_bs = min(cfg["n_ground_batch"], anchor_pool.shape[0])
            a_idx = ground_rng.choice(anchor_pool, size=a_bs, replace=False)
            # OOM POOLING FIX (inherited from _r._pooled_for_rows, commit d8d6684fb): opt-in
            # torch.utils.checkpoint (non-reentrant) + batch-chunk the pooled rows so the joint-loss
            # pooling forward does not spike VRAM on the 8GB card. Correctness-neutral (batch-dim chunking
            # is exact; checkpoint recomputes in backward). chunk explicit + configurable, mirrors relobj.
            pool_chunk = int(cfg.get("ground_pool_chunk", 32))
            z_a = _r._pooled_for_rows(model, win_ids, a_idx, device, use_amp, chunk_size=pool_chunk)  # float32
            pred = head(z_a)
            tgt = torch.from_numpy(target_np[a_idx]).to(device=device, dtype=pred.dtype)
            cos = (pred * tgt).sum(dim=1)
            ground_loss = (1.0 - cos).mean()
            loss = loss + lambda_ground * ground_loss
            ground_loss_val = float(ground_loss.detach())
            n_ground_fired += 1
        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite joint loss step=%d seed=%d (mlm=%.4f ground=%s)"
                                     % (step, seed, float(mlm_loss.detach()), ground_loss_val))
        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()
        last_loss = float(mlm_loss.detach())
        mlm_loss_curve.append(last_loss)
        if ground_loss_val is not None:
            ground_loss_curve.append(ground_loss_val)
        if (step % log_every == 0) or (step == cfg["mlm_steps"] - 1):
            el = time.perf_counter() - t0
            _log("  MLM seed=%d step=%d/%d mlm_loss=%.4f ground_loss=%s (%.1fs)"
                 % (seed, step, cfg["mlm_steps"], last_loss,
                    ("%.4f" % ground_loss_val) if ground_loss_val is not None else "NA", el))
            _heartbeat(out_dir, step, hb_total, el,
                      extra={"mlm_loss": last_loss, "ground_loss": ground_loss_val, "seed": seed})
        if step > 0 and (step % ckpt_every == 0 or step == cfg["mlm_steps"] - 1):
            if _save_inprogress_ckpt_ground(out_dir, seed, model, head, opt, step, spec, cfg):
                n_ckpt_saves += 1
    model.eval()
    head.eval()
    ground_diag = dict(
        ground_ok=bool(ground_ok), n_ground_fired=int(n_ground_fired), n_ckpt_saves=int(n_ckpt_saves),
        n_anchor_pool=int(anchor_pool.shape[0]), ground_dim=ground_dim,
        ground_loss_first=(ground_loss_curve[0] if ground_loss_curve else None),
        ground_loss_last=(ground_loss_curve[-1] if ground_loss_curve else None),
        ground_loss_mean_first10=(float(np.mean(ground_loss_curve[:10])) if len(ground_loss_curve) >= 1 else None),
        ground_loss_mean_last10=(float(np.mean(ground_loss_curve[-10:])) if len(ground_loss_curve) >= 1 else None),
        mlm_loss_first=(mlm_loss_curve[0] if mlm_loss_curve else None),
        mlm_loss_last=(mlm_loss_curve[-1] if mlm_loss_curve else None),
        # "did L_ground learn" uses the MEAN of the first/last window (robust), NOT single first/last
        # firings -- a 2-point single-firing compare is noisy (each firing samples a fresh random anchor
        # batch), which False-flagged a genuinely-descending curve at smoke (first10=0.972 -> last10=0.940
        # decreasing, yet single first=1.0020 < last=1.0030). Falls back to the 2-point compare only when
        # there are too few firings to form windows.
        ground_loss_decreased=(
            bool(float(np.mean(ground_loss_curve[-10:])) < float(np.mean(ground_loss_curve[:10])))
            if len(ground_loss_curve) >= 4
            else (bool(ground_loss_curve[-1] < ground_loss_curve[0]) if len(ground_loss_curve) >= 2 else None)),
    )
    return model, last_loss, ground_diag


# ---------------------------------------------------------------------------
# Seed-independent data prep (identical to v3_relobj's own prepare_data, minus the relational-edge prep,
# plus groundobj_prep in its place)
# ---------------------------------------------------------------------------
def prepare_data(cfg, universe):
    _log("count pass...")
    counts, corpus_stats = _r.count_pass(cfg, universe["surf_to_idx"])
    _log("  corpus: read=%d kept=%d dup_rate=%.4f low_q=%d tokens=%d"
         % (corpus_stats["n_read"], corpus_stats["n_kept"], corpus_stats["dup_rate"],
            corpus_stats["n_lowq"], corpus_stats["total_alpha_tokens"]))
    split = _r.build_split(universe, counts, cfg)
    _log("  split: heldout=%d train_eval=%d median_mentions(elig)=%.0f"
         % (split["split_meta"]["n_heldout"], split["split_meta"]["n_train_eval"],
            split["split_meta"]["median_mentions_eligible"]))

    _log("collect pass (postings + BPE sample)...")
    postings, bpe_lines, collect_meta = _r.collect_pass(cfg, universe, split)
    _log("  train_lines=%d held_lines=%d bpe_sample=%d train_tokens_avail=%d"
         % (collect_meta["n_train_lines"], collect_meta["n_held_lines"],
            collect_meta["bpe_sample"], collect_meta["train_tokens_available"]))
    if len(bpe_lines) < 50:
        raise RuntimeError("too few BPE-sample lines (%d)" % len(bpe_lines))

    _log("build BPE (vocab=%d)..." % cfg["vocab"])
    tok, spec = _r.build_bpe(bpe_lines, cfg["vocab"])
    _log("  BPE size=%d pad=%d unk=%d mask=%d" % (spec["size"], spec["pad"], spec["unk"], spec["mask"]))

    _log("tokenize train stream (budget=%d)..." % cfg["train_token_budget"])
    stream, trained_tokens = _r.tokenize_train_stream(cfg, tok, split, spec)
    _log("  trained_tokens=%d windows=%d" % (trained_tokens, stream.shape[0] // cfg["max_len"]))

    witness_leaks = _r._zero_overlap_witness(cfg, split, sample_lines=20000)
    _log("  zero-overlap witness: %d leaked train lines (must be 0)" % witness_leaks)
    if witness_leaks != 0:
        raise RuntimeError("LEAK: %d train lines contain a held-out surface" % witness_leaks)

    ground = _r.build_grounding_reps(universe, split)
    _log("load relational adjacency (max_shards=%d)..." % cfg["max_shards"])
    adj, deg, n_shards = _r.load_adjacency(universe, cfg)

    _log("experiential-grounding self-teacher prep (Lancaster targets, TRAIN-only anchor pool)...")
    groundobj = groundobj_prep(universe, split, postings, tok, spec, cfg)
    _log("  anchor_pool=%d (of %d Lancaster-eligible, %d Lancaster-eligible held-out excluded) leak_zero=%s"
         % (groundobj["n_anchor_pool"], groundobj["n_eligible_total"],
            groundobj["n_held_with_lancaster"], groundobj["n_leak_verified_zero"]))
    if groundobj["n_anchor_pool"] < cfg["min_ground_anchors"]:
        raise RuntimeError(
            "META_RULE_AG-style regime-insufficient: ground anchor_pool=%d below min_ground_anchors=%d "
            "at this cfg -- re-spec cap_eval_concepts/min_deg, do not silently proceed with a vacuous "
            "L_ground" % (groundobj["n_anchor_pool"], cfg["min_ground_anchors"]))

    return dict(counts=counts, corpus_stats=corpus_stats, split=split,
                postings=postings, collect_meta=collect_meta, tok=tok, spec=spec,
                stream=stream, trained_tokens=trained_tokens, ground=ground,
                adj=adj, deg=deg, n_shards=n_shards, witness_leaks=witness_leaks,
                groundobj=groundobj)


# ---------------------------------------------------------------------------
# End-of-run checkpoint (LOCAL -- own ANCHOR_NAME; mirrors v3_relobj's _save_checkpoint)
# ---------------------------------------------------------------------------
def _save_checkpoint(out_dir, seed, model, tok, spec, cfg, universe, split, bundle,
                     text_reps, text_rand, ground, mrep_cnt, w_star, selected_arm):
    try:
        ckpt = dict(
            state_dict={k: v.detach().cpu() for k, v in model.state_dict().items()},
            spec=spec,
            model_cfg=dict(vocab=int(spec["size"]), max_len=int(cfg["max_len"]),
                           d_model=int(cfg["d_model"]), n_layers=int(cfg["n_layers"]),
                           n_heads=int(cfg["n_heads"]), ffn_mult=int(cfg["ffn_mult"]),
                           pad_id=int(spec["pad"])),
            tokenizer_json=tok.to_str(),
            seed=int(seed), run_mode=cfg["run_mode"], anchor=ANCHOR_NAME,
            w_star=float(w_star), selected_arm=str(selected_arm),
        )
        torch.save(ckpt, os.path.join(out_dir, "ckpt_seed_%d.pt" % seed))
        adj = bundle["adj"]
        indptr = np.zeros(len(adj) + 1, dtype=np.int64)
        flat = []
        for i, a in enumerate(adj):
            s = sorted(a)
            flat.extend(s)
            indptr[i + 1] = indptr[i] + len(s)
        np.savez_compressed(
            os.path.join(out_dir, "evalreps_seed_%d.npz" % seed),
            text_reps=text_reps.astype(np.float32), text_rand=text_rand.astype(np.float32),
            ground=ground.astype(np.float32), mrep_cnt=mrep_cnt.astype(np.int64),
            counts=bundle["counts"].astype(np.int64), deg=bundle["deg"].astype(np.int64),
            adj_indices=np.asarray(flat, dtype=np.int64), adj_indptr=indptr,
            held_idx=split["held_idx"], train_eval_idx=split["train_eval_idx"],
            is_held=split["is_held"],
            lexnames=np.array([x if x else "" for x in universe["lexnames"]], dtype=object),
            w_star=np.float64(w_star), selected_arm=np.array(str(selected_arm)),
            n_shards=np.int64(bundle["n_shards"]),
        )
        _log("  checkpoint saved: ckpt_seed_%d.pt + evalreps_seed_%d.npz" % (seed, seed))
        return True
    except (OSError, RuntimeError, ValueError) as e:
        _log("  WARN checkpoint save failed (%s): %s" % (type(e).__name__, str(e)[:200]))
        return False


# ---------------------------------------------------------------------------
# One seed (joint MLM+L_ground train + encode + eval; consumes the shared data bundle)
# ---------------------------------------------------------------------------
def run_one_seed(seed, cfg, device, out_dir, universe, bundle):
    t0 = time.perf_counter()
    split = bundle["split"]
    counts = bundle["counts"]
    tok = bundle["tok"]
    spec = bundle["spec"]
    postings = bundle["postings"]
    ground = bundle["ground"]

    _log("seed=%d: JOINT MLM+L_ground train (%d steps, ground_every=%d)..." % (seed, cfg["mlm_steps"], cfg["ground_every"]))
    model, final_loss, ground_diag = mlm_train_groundobj(bundle["stream"], spec, cfg, device, seed, out_dir,
                                                          cfg["mlm_steps"], bundle["groundobj"])
    _log("  MLM+L_ground done final_mlm_loss=%.4f ground_fired=%d ground_loss_first=%s ground_loss_last=%s"
         % (final_loss, ground_diag["n_ground_fired"], ground_diag["ground_loss_first"], ground_diag["ground_loss_last"]))

    _log("seed=%d: encode concept text-reps (trained)..." % seed)
    text_reps, mrep_cnt = _r.encode_concept_text_reps(model, tok, postings, cfg, device, spec)
    torch.manual_seed(seed + 999)
    rand_model = _r.TinyTransformer(spec["size"], cfg["max_len"], cfg["d_model"], cfg["n_layers"],
                                    cfg["n_heads"], cfg["ffn_mult"], spec["pad"]).to(device)
    rand_model.eval()
    _log("seed=%d: encode concept text-reps (random-init)..." % seed)
    text_rand, _ = _r.encode_concept_text_reps(rand_model, tok, postings, cfg, device, spec)

    _log("seed=%d: baseline-reuse eval (v2 MLM-only, if checkpoint present)..." % seed)
    baseline = _r.eval_baseline_arm(seed, cfg, device, universe, split, counts, postings, ground,
                                    bundle["adj"], bundle["deg"], bundle["n_shards"])
    _log("  baseline_source=%s rel_auc=%s sem_auc=%s"
         % (baseline["baseline_source"], baseline["baseline_relational_auc"], baseline["baseline_semantic_auc"]))

    w_star, selected_arm, _ = _r.select_fusion_on_train(
        ground, text_reps, text_rand, counts, universe, split, seed)
    _save_checkpoint(out_dir, seed, model, tok, spec, cfg, universe, split, bundle,
                     text_reps, text_rand, ground, mrep_cnt, w_star, selected_arm)
    inprog = os.path.join(out_dir, "ckpt_seed_%d_inprogress.pt" % seed)
    if os.path.exists(inprog):
        try:
            os.remove(inprog)
        except OSError:
            pass

    extra = dict(
        final_mlm_loss=float(final_loss), trained_tokens=int(bundle["trained_tokens"]),
        corpus_stats=bundle["corpus_stats"], collect_meta=bundle["collect_meta"],
        split_meta=split["split_meta"], bpe_size=int(spec["size"]),
        checkpoint_saved=True, ground_diag=ground_diag, baseline=baseline,
        ground_leak_gate=dict(
            n_anchor_pool=bundle["groundobj"]["n_anchor_pool"],
            n_eligible_total=bundle["groundobj"]["n_eligible_total"],
            n_held_with_lancaster=bundle["groundobj"]["n_held_with_lancaster"],
            n_leak_verified_zero=bundle["groundobj"]["n_leak_verified_zero"]),
    )
    return _r.eval_from_reps(seed, cfg["run_mode"], out_dir, universe, split, counts,
                             bundle["adj"], bundle["deg"], bundle["n_shards"],
                             ground, text_reps, text_rand, mrep_cnt,
                             time.perf_counter() - t0, extra=extra)


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def build_verdict_ground(per_seed, cfg):
    seeds = sorted(per_seed.keys(), key=lambda k: int(k))

    def col(section, arm):
        vals = []
        for k in seeds:
            sec = per_seed[k].get(section)
            if sec and sec.get(arm) is not None:
                vals.append(sec[arm])
        return vals

    def mean(v):
        return float(np.mean(v)) if v else None

    obj_rel = col("relational", TEXT_ARM)
    obj_sem = col("semantic_all", TEXT_ARM)
    baselines = [per_seed[k].get("baseline", {}) for k in seeds]
    base_rel = [b.get("baseline_relational_auc") for b in baselines]
    base_sem = [b.get("baseline_semantic_auc") for b in baselines]
    base_src = [b.get("baseline_source") for b in baselines]
    rel_margins = [o - b for o, b in zip(obj_rel, base_rel) if b is not None] if obj_rel else []
    rel_margin_mean = float(np.mean(rel_margins)) if rel_margins else None
    rel_margin_min = float(np.min(rel_margins)) if rel_margins else None
    sem_margins = [o - b for o, b in zip(obj_sem, base_sem) if b is not None] if obj_sem else []
    sem_margin_mean = float(np.mean(sem_margins)) if sem_margins else None
    sem_margin_min = float(np.min(sem_margins)) if sem_margins else None

    ground_diags = [per_seed[k].get("ground_diag", {}) for k in seeds]
    ground_loss_decreased_all = [d.get("ground_loss_decreased") for d in ground_diags]
    ground_ok_all = [bool(d.get("ground_ok")) for d in ground_diags]
    n_ground_fired_min = min([int(d.get("n_ground_fired", 0)) for d in ground_diags]) if ground_diags else 0
    ground_learning_real = all(ground_ok_all) and n_ground_fired_min > 0 and all(
        (x is True) for x in ground_loss_decreased_all if x is not None)

    leak_gates = [per_seed[k].get("ground_leak_gate", {}) for k in seeds]
    leak_zero_all = all(bool(g.get("n_leak_verified_zero")) for g in leak_gates) if leak_gates else False
    anchor_pool_min = min([int(g.get("n_anchor_pool", 0)) for g in leak_gates]) if leak_gates else 0
    eligible_min = min([int(g.get("n_eligible_total", 0)) for g in leak_gates]) if leak_gates else 0

    raw = col("semantic_all", RAW_ARM)
    txt = col("semantic_all", TEXT_ARM)
    feq = col("semantic_all", FUSED_ARM)
    fza = col("semantic_all", FUSE_ZAVG_ARM)
    fwt = col("semantic_all", FUSE_WTUNED_ARM)
    prim = col("semantic_all", FUSE_SELECTED_ARM)
    rnd = col("semantic_all", RANDINIT_ARM)
    sh = col("semantic_all", SHUFFLE_ARM)
    pop = col("semantic_all", POP_ARM)
    nq = [per_seed[k].get("semantic_all", {}).get("_n_query", 0) for k in seeds]
    sel_arms = [per_seed[k].get("semantic_all", {}).get("_selected_arm") for k in seeds]
    w_stars = [per_seed[k].get("semantic_all", {}).get("_w_star") for k in seeds]

    m_raw, m_txt, m_feq = mean(raw), mean(txt), mean(feq)
    m_fza, m_fwt, m_prim = mean(fza), mean(fwt), mean(prim)
    m_rnd, m_sh, m_pop = mean(rnd), mean(sh), mean(pop)
    learn_margins = [t - r for t, r in zip(txt, rnd)] if (txt and rnd and len(txt) == len(rnd)) else []
    learn_mean = float(np.mean(learn_margins)) if learn_margins else None

    rraw = col("relational", RAW_ARM)
    rtxt = col("relational", TEXT_ARM)
    m_rraw, m_rtxt = mean(rraw), mean(rtxt)

    min_nq = min(nq) if nq else 0
    validity = (
        _r._valid_band(m_sh, *COLLAPSE_BAND) and _r._valid_band(m_pop, *COLLAPSE_BAND)
        and (m_raw is not None and m_raw >= RAW_SIGNAL_MIN) and (min_nq >= MIN_QUERY_TASKS))

    gates = []
    gates.append(record_gate("collapse_in_band", 1.0 if _r._valid_band(m_sh, *COLLAPSE_BAND) else 0.0, 1.0, "==",
                             note="collapse=%.4f band=%s" % ((m_sh if m_sh else -1), COLLAPSE_BAND)))
    gates.append(record_gate("popularity_in_band", 1.0 if _r._valid_band(m_pop, *COLLAPSE_BAND) else 0.0, 1.0, "==",
                             note="pop=%.4f" % (m_pop if m_pop else -1)))
    gates.append(record_gate("raw_grounding_signal", m_raw if m_raw is not None else 0.0, RAW_SIGNAL_MIN, ">=",
                             note="raw grounding must be a real signal"))
    gates.append(record_gate("power_min_query", float(min_nq), float(MIN_QUERY_TASKS), ">=",
                             note="held-out query power floor"))
    gates.append(record_gate("learning_real_text_over_random", learn_mean if learn_mean is not None else -1.0,
                             0.0, ">", note="RAW_TEXT - RANDOM_INIT"))
    gates.append(record_gate("ground_anchor_pool_excludes_held", 1.0 if leak_zero_all else 0.0, 1.0, "==",
                             note="held-out concepts never in grounding-loss anchor pool (min anchor_pool=%d of %d eligible)"
                             % (anchor_pool_min, eligible_min)))
    gates.append(record_gate("ground_objective_learning_real", 1.0 if ground_learning_real else 0.0, 1.0, "==",
                             note="L_ground fired every seed AND ground_loss decreased (n_ground_fired_min=%d, per-seed ground_loss_decreased=%s)"
                             % (n_ground_fired_min, ground_loss_decreased_all)))
    gates.append(record_gate("semantic_margin_over_baseline", sem_margin_mean if sem_margin_mean is not None else -1.0,
                             HP_MARGIN_OVER_BASELINE, ">=", note="OBJ(TEXT_ARM semantic-AUC) - BASELINE(reused/cited)"))
    gates.append(record_gate("relational_margin_over_baseline", rel_margin_mean if rel_margin_mean is not None else -1.0,
                             HP_MARGIN_OVER_BASELINE, ">=", note="OBJ(TEXT_ARM relational-AUC) - BASELINE(reused/cited)"))

    run_mode = cfg["run_mode"]
    if run_mode in ("selftest", "smoke"):
        ran_ok = (m_raw is not None and m_prim is not None and m_txt is not None
                  and m_feq is not None and m_fza is not None and m_fwt is not None
                  and m_sh is not None and m_pop is not None and n_ground_fired_min > 0)
        verdict = "SMOKE_PASS" if ran_ok else "SMOKE_INCOMPLETE"
        vmsg = ("SMOKE run_mode=%s raw=%.4f text=%.4f collapse=%.4f pop=%.4f rel_raw=%.4f rel_text=%.4f "
                "baseline_src=%s base_sem=%s base_rel=%s sem_margin=%s rel_margin=%s n_ground_fired_min=%d "
                "ground_loss_decreased=%s anchor_pool_min=%d n_query_min=%d"
                % (run_mode, m_raw or -1, m_txt or -1, m_sh or -1, m_pop or -1, m_rraw or -1, m_rtxt or -1,
                   base_src, base_sem, base_rel,
                   ("%.4f" % sem_margin_mean) if sem_margin_mean is not None else "NA",
                   ("%.4f" % rel_margin_mean) if rel_margin_mean is not None else "NA",
                   n_ground_fired_min, ground_loss_decreased_all, anchor_pool_min, min_nq))
    else:
        sem_pass = (sem_margin_mean is not None and sem_margin_mean >= HP_MARGIN_OVER_BASELINE
                    and sem_margin_min is not None and sem_margin_min > 0.0)
        rel_pass = (rel_margin_mean is not None and rel_margin_mean >= HP_MARGIN_OVER_BASELINE
                    and rel_margin_min is not None and rel_margin_min > 0.0)
        sem_no_regress = (sem_margin_mean is None or sem_margin_mean >= -SEM_REGRESSION_MAX)
        if not validity:
            verdict = "HARD_FAIL_INVALID"
            vmsg = ("INVALID: validity gate failed (collapse=%s pop=%s raw=%s n_query_min=%d)."
                    % (m_sh, m_pop, m_raw, min_nq))
        elif not leak_zero_all:
            verdict = "HARD_FAIL_LEAK"
            vmsg = ("HARD_FAIL: a held-out concept was found in the grounding-loss anchor pool -- second "
                    "leak gate breached (anchor_pool_min=%d)." % anchor_pool_min)
        elif not ground_learning_real:
            verdict = "HARD_FAIL_GROUND_OBJECTIVE_NOT_LEARNING"
            vmsg = ("HARD_FAIL: L_ground training loss did not visibly decrease (or never fired) -- the "
                    "experiential-grounding self-teacher term is not learning; margin numbers below are "
                    "not trustworthy until training dynamics are fixed. ground_ok=%s n_ground_fired_min=%d "
                    "ground_loss_decreased=%s" % (ground_ok_all, n_ground_fired_min, ground_loss_decreased_all))
        elif (sem_pass or rel_pass) and sem_no_regress:
            which = ("SEMANTIC+RELATIONAL" if (sem_pass and rel_pass)
                     else ("SEMANTIC" if sem_pass else "RELATIONAL"))
            verdict = "HARD_PASS_GROUNDOBJ_CLEAN_WIN"
            vmsg = ("HARD_PASS_GROUNDOBJ_CLEAN_WIN(%s): joint MLM+Lancaster-sensorimotor self-teacher "
                    "OBJ(TEXT_ARM) beats the MLM-only BASELINE on held-out-NEW geometry. sem_margin=%s "
                    "rel_margin=%s (gate>=%.2f); obj_sem=%s base_sem=%s obj_rel=%s base_rel=%s (source=%s); "
                    "n_ground_fired_min=%d ground_loss(first->last)=%s->%s anchor_pool_min=%d"
                    % (which,
                       ("%.4f" % sem_margin_mean) if sem_margin_mean is not None else "NA",
                       ("%.4f" % rel_margin_mean) if rel_margin_mean is not None else "NA",
                       HP_MARGIN_OVER_BASELINE, obj_sem, base_sem, obj_rel, base_rel, base_src,
                       n_ground_fired_min, [d.get("ground_loss_first") for d in ground_diags],
                       [d.get("ground_loss_last") for d in ground_diags], anchor_pool_min))
        elif (sem_margin_mean is not None and -0.02 <= sem_margin_mean <= 0.02
              and rel_margin_mean is not None and -0.02 <= rel_margin_mean <= 0.02):
            verdict = "HARD_FAIL_NO_TRANSFER"
            vmsg = ("HARD_FAIL_NO_TRANSFER: neither semantic nor relational margin clears +/-0.02 of "
                    "baseline DESPITE L_ground loss visibly decreasing (ground_loss %s->%s) -- experiential "
                    "grounding is too PARTIAL / architecture-bound to transfer into the encoder's held-out-"
                    "NEW geometry at this scale. Honest null (per task instruction), not a training bug. "
                    "sem_margin=%s rel_margin=%s anchor_pool_min=%d (of %d Lancaster-eligible concepts)"
                    % ([d.get("ground_loss_first") for d in ground_diags],
                       [d.get("ground_loss_last") for d in ground_diags],
                       sem_margin_mean, rel_margin_mean, anchor_pool_min, eligible_min))
        else:
            verdict = "MIDDLE_BAND_GROUNDOBJ_PARTIAL"
            vmsg = ("MIDDLE_BAND: a margin positive but below +%.2f, or semantic regressed beyond the "
                    "guard (sem_margin=%s rel_margin=%s). obj_sem=%s base_sem=%s obj_rel=%s base_rel=%s "
                    "(source=%s)"
                    % (HP_MARGIN_OVER_BASELINE,
                       ("%.4f" % sem_margin_mean) if sem_margin_mean is not None else "NA",
                       ("%.4f" % rel_margin_mean) if rel_margin_mean is not None else "NA",
                       obj_sem, base_sem, obj_rel, base_rel, base_src))

    summary = dict(
        obj_semantic_auc=obj_sem, obj_relational_auc=obj_rel,
        baseline_semantic_auc=base_sem, baseline_relational_auc=base_rel, baseline_source=base_src,
        semantic_margin_over_baseline_mean=sem_margin_mean, semantic_margin_over_baseline_min=sem_margin_min,
        relational_margin_over_baseline_mean=rel_margin_mean, relational_margin_over_baseline_min=rel_margin_min,
        ground_learning_real=ground_learning_real, n_ground_fired_min=n_ground_fired_min,
        ground_loss_first=[d.get("ground_loss_first") for d in ground_diags],
        ground_loss_last=[d.get("ground_loss_last") for d in ground_diags],
        anchor_pool_min=anchor_pool_min, eligible_total_min=eligible_min,
        leak_zero_all=leak_zero_all,
        primary_arm_selected=sel_arms, w_star_per_seed=w_stars,
        semantic_raw_grounding=m_raw, semantic_text=m_txt,
        semantic_fused_eq_naive=m_feq, semantic_fuse_zavg=m_fza, semantic_fuse_wtuned=m_fwt,
        semantic_primary=m_prim,
        semantic_random_init=m_rnd, semantic_collapse=m_sh, semantic_popularity=m_pop,
        learning_text_minus_random=learn_mean,
        relational_raw=m_rraw, relational_text=m_rtxt,
        n_query_min=min_nq, validity=validity,
        trained_tokens=[per_seed[k].get("trained_tokens") for k in seeds],
    )
    return verdict, vmsg, summary, gates


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def _select_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", default=None)
    args = ap.parse_args()

    if args.self_test:
        cfg = SELFTEST_CFG
    elif args.smoke:
        cfg = SMOKE_CFG
    else:
        cfg = FULL_CFG

    out_dir = get_output_dir(ANCHOR_NAME)
    os.makedirs(out_dir, exist_ok=True)
    _write_start_marker(out_dir, cfg["run_mode"], len(cfg["seeds"]))

    device = torch.device(args.device) if args.device else _select_device()
    _log("run_mode=%s device=%s seeds=%s cuda=%s"
         % (cfg["run_mode"], device.type, cfg["seeds"], torch.cuda.is_available()))
    if not os.path.exists(_r.ARC_CORPUS):
        raise FileNotFoundError("ARC corpus not found at %s (remote staging?)" % _r.ARC_CORPUS)

    _log("loading concept universe...")
    universe = _r.load_concept_universe(cfg)
    _log("concept universe: K=%d single-token grounded+lexname concepts" % universe["K"])

    _log("preparing shared data (seed-independent: split, tokenizer, postings, stream, graph, groundobj)...")
    bundle = prepare_data(cfg, universe)

    for seed in cfg["seeds"]:
        res = run_one_seed(seed, cfg, device, out_dir, universe, bundle)
        write_partial(out_dir, seed, res)
        _log("seed=%d done in %.1fs" % (seed, res["elapsed_s"]))

    per_seed = aggregate_partials(out_dir, cfg["seeds"])
    verdict, vmsg, summary, gates = build_verdict_ground(per_seed, cfg)
    _log("VERDICT: %s" % verdict)
    _log(vmsg)

    metrics = dict(
        verdict=verdict, verdict_msg=vmsg, summary=vmsg,
        anchor_name=ANCHOR_NAME, run_mode=cfg["run_mode"],
        ts_iso=datetime.now(timezone.utc).isoformat(),
        device=device.type, cuda=bool(torch.cuda.is_available()),
        n_seeds=len(cfg["seeds"]),
        results_summary=summary,
        per_seed={k: per_seed[k] for k in per_seed},
        bands=dict(hp_margin_over_baseline=HP_MARGIN_OVER_BASELINE, raw_signal_min=RAW_SIGNAL_MIN,
                   collapse_band=list(COLLAPSE_BAND), min_query=MIN_QUERY_TASKS,
                   sem_regression_max=SEM_REGRESSION_MAX,
                   cited_baseline_relational_auc=CITED_BASELINE_RELATIONAL_AUC),
        cardinality_ok=(len(per_seed) == len(cfg["seeds"])),
        expected_n_units=len(cfg["seeds"]),
    )
    write_metrics(out_dir, metrics, results=list(per_seed.values()), gate_claims=gates)

    if args.self_test:
        _selftest_assertions(per_seed, summary, verdict, out_dir)
        _log("SELF-TEST PASS")


def _selftest_assertions(per_seed, summary, verdict, out_dir):
    assert len(per_seed) >= 1, "no seed completed"
    sk = sorted(per_seed.keys())[0]
    r = per_seed[sk]
    assert r["semantic_all"] is not None, "semantic eval did not run"
    for a in [RAW_ARM, TEXT_ARM, FUSED_ARM, FUSE_ZAVG_ARM, FUSE_WTUNED_ARM, FUSE_SELECTED_ARM]:
        assert r["semantic_all"].get(a) is not None, "semantic arm missing: %s" % a
        au = r["semantic_all"][a]
        assert 0.0 <= au <= 1.0, "AUC out of range for %s: %s" % (a, au)
    sel = r["semantic_all"].get("_selected_arm")
    assert sel in PRIMARY_CANDIDATES, "selected arm not a primary candidate: %s" % sel
    assert abs(r["semantic_all"][FUSE_SELECTED_ARM] - r["semantic_all"][sel]) < 1e-9, \
        "PRIMARY != selected-arm held-out AUC"
    assert r["relational"] is not None, "relational eval did not run"
    if r["relational"].get("_n_query", 0) > 0:
        for a in [RAW_ARM, TEXT_ARM, FUSE_ZAVG_ARM, FUSE_WTUNED_ARM]:
            assert r["relational"].get(a) is not None, "relational arm missing: %s" % a
    assert np.isfinite(r["final_mlm_loss"]), "MLM loss not finite"
    assert r["trained_tokens"] > 0, "no tokens trained on"
    ckpt_pt = os.path.join(out_dir, "ckpt_seed_%d.pt" % int(sk))
    ckpt_npz = os.path.join(out_dir, "evalreps_seed_%d.npz" % int(sk))
    assert os.path.exists(ckpt_pt), "checkpoint .pt not saved: %s" % ckpt_pt
    assert os.path.exists(ckpt_npz), "eval-rep bundle .npz not saved: %s" % ckpt_npz
    eb, _z = _r._load_eval_bundle(ckpt_npz)
    assert eb["text_reps"].shape[0] == eb["ground"].shape[0], "reloaded rep shape mismatch"
    assert verdict == "SMOKE_PASS", "selftest did not complete arms (%s)" % verdict
    # experiential-grounding self-teacher: real_code_path_exercised (L_ground must have actually fired
    # and the periodic mid-training checkpoint must have actually saved at least once)
    gd = r.get("ground_diag")
    assert gd is not None, "ground_diag missing (experiential-grounding self-teacher step did not run)"
    assert gd.get("ground_ok") is True, "ground_ok False -- anchor_pool below min_ground_anchors at selftest scale"
    assert gd.get("n_ground_fired", 0) > 0, "L_ground discriminator never fired in selftest (n_ground_fired=0)"
    assert gd.get("n_ckpt_saves", 0) > 0, "periodic mid-training checkpoint never saved (n_ckpt_saves=0)"
    assert gd.get("ground_loss_first") is not None and gd.get("ground_loss_last") is not None, \
        "ground_loss curve empty despite n_ground_fired>0"
    # SECOND leak gate: anchor pool built + verified to exclude every held-out concept
    leak = r.get("ground_leak_gate")
    assert leak is not None, "ground_leak_gate missing"
    assert leak.get("n_leak_verified_zero") is True, "ground anchor-pool leak witness did not verify zero"
    assert leak.get("n_anchor_pool", 0) > 0, "grounding anchor pool empty -- second leak gate not meaningfully active"
    # baseline-reuse path exercised (either reused a real checkpoint or explicitly fell back to CITED)
    base = r.get("baseline")
    assert base is not None, "baseline dict missing"
    assert base.get("baseline_source") in (BASELINE_SOURCE_REUSED, BASELINE_SOURCE_CITED), \
        "baseline_source not tagged: %s" % base.get("baseline_source")
    assert base.get("baseline_relational_auc") is not None, "baseline_relational_auc missing"


if __name__ == "__main__":
    _out = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
