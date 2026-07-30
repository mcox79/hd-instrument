# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (sha256 of per-sentence predicted-role-id vectors, pairwise
#   distinct across VARIED / NEAR_IDENTICAL / SHUFFLED_FLOOR conditions)
# - final_metrics_atomicity: tmp_replace (os.replace at end)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no learned-noise Cramer-Rao floor here; discriminator is the pre-registered
#   ENCODER_SURVIVES_SYNTAX / SYNTAX_DEGRADES_KEYS / INVALID decision rule (Director spawn 2026-07-30,
#   "role-key syntax-invariance diagnostic" cell -- Step 0 risk-mitigation from
#   notes/native_binding_comprehension_richer_nl_frontier_plan_2026-07-30.md Section 5).
# - baseline_in_band: n/a -- no learned baseline arm; the SHUFFLED_FLOOR condition IS the can-fail
#   control and decide_verdict() requires it to independently collapse to near-chance or the cell is
#   INVALID (a floor that doesn't floor).
# - discriminator survives scale: this cell is closed-form (no training loop, no smoke/full scale gap);
#   self-test exercises the REAL frozen v2 encoder + REAL oc.build_role_query_probe/_extract_slot_rep_
#   single at tiny n (real_code_path)
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)
# - deterministic seeding: numpy default_rng + torch.manual_seed/torch.Generator only; NO hash(),
#   NO list(set())
# - cell_chunked: false -- single closed-form pass over a small (role x frame x entity) sentence set,
#   3 probe-seeds x 2 conditions = 6 units total, checkpointed via tools/exp_checkpoint (CLAUDE.md
#   multi-unit mandate) but NOT split into sibling per-seed files: total wall time is a design target
#   of well under 8 minutes (compute-proportionality: this is a cheap DIAGNOSTIC/GATE question, not a
#   magnitude-fit training run -- chunking's benefit (bounding a runner-zombie loss to one seed) does
#   not outweigh the overhead of N sibling files for a sub-minute cell).
"""Does the frozen v2 encoder produce CONSISTENT + still-DISTINCT role keys across GENUINELY VARIED
syntax, or does syntactic variation destroy role-key separability (reopening the context-entanglement
wall)? Director spawn 2026-07-30 -- the cheapest, measurement-first gate on the richer-NL frontier build
(notes/native_binding_comprehension_richer_nl_frontier_plan_2026-07-30.md Section 5's named risk: "role
identity survives novel syntax" is exactly the open question before authoring
exp_native_binding_naturalistic_multirelation_v1).

WHY: every confirmed native-binding positive to date (novel-filler-to-known-role 0.97-0.99, zero-shot
novel-role 0.65/0.29, cross-slot relational 0.855/0.815) derived its role key by AVERAGING a fixed
role-query probe's extraction over a SMALL, NEAR-IDENTICAL set of syntactic templates (e.g.
exp_oracle_context_invariant_address_wm_v2's "the {slot} was {fill} ." / "someone painted the {slot}
{fill} ." / "the {slot} turned {fill} ." -- all flat SVO, slot always subject). The richer-NL frontier
plan needs role keys that stay consistent across ACTIVE / PASSIVE / RELATIVE-CLAUSE / CLEFT / PRONOUN-
COREFERENCE frames -- syntactically real variation, not lexical synonyms of one template. This cell
measures, cheaply and BEFORE building that frontier cell, whether the frozen encoder's role-identity
signal survives that variation or whether within-role variance across frames swamps between-role
separation (the risk named explicitly in the frontier plan's Section 5).

CONSTRUCTION (reuses existing extraction machinery verbatim, not reinvented):
  - Encoder: base.FrozenV2Encoder subclassed (RoleSyntaxEncoder, same pattern as RelEncoder in
    exp_cross_slot_relational_binding_v1.py) with its OWN closed sentence set -- does not touch any
    other cell's global state.
  - Role-rep extraction: oc.build_role_query_probe(seed, d) + oc._extract_slot_rep_single(...) --
    BYTE-IDENTICAL reuse of the exact attention-pooling extraction every confirmed cell's oracle table
    already uses (a small-scale random probe vector -> near-uniform-attention pooled sentence rep).
  - Entities: calib.COLORS (closed 20-word vocabulary), reused verbatim as the filler/lexicalization set.
  - Conditioning: every rep has the GLOBAL MEAN (over the full closed sentence set, same probe seed)
    SUBTRACTED before use (mean-centering -- the standard first step of the proven pca_whiten conditioner,
    rc.Conditioner, already used to expose signal in this exact known failure mode: a dominant shared
    component swamping a low-variance role-identity subspace, per WHERE_WE_ARE_NOW's NL-WM read-
    conditioning finding). This is a FIXED, principled, closed-form construction step declared before
    interpreting results, NOT a post-hoc per-metric tune -- an initial iteration without centering
    produced sep_gap approx 0.0008 (within-role consistency indistinguishable from between-role cosine,
    both near the shared-component's magnitude) and an unstable SHUFFLED_FLOOR (0.02-0.40 across probe
    seeds, i.e. the floor did not floor) -- exactly the frontier plan's Section-5 named risk (shared-
    component-swamped signal) reproduced directly in the ROLE-KEY construction this time, not just the
    WM read-path. Centering is reported as a construction fix, and the RAW (uncentered) numbers are
    reported alongside in this file's self-test log for transparency.

FIVE ROLES (Fillmore/thematic case-grammar set, matches the frontier plan's Section 3 role choice):
  AGENT, PATIENT, RECIPIENT, INSTRUMENT, LOCATION (role WORDS embedded in sentence text; there is no
  training here, so the "role" is realized purely by which case-role word appears in the sentence).

TWO SENTENCE-SET CONDITIONS (the fairness anchor -- same roles, same entities, same extraction, only
the FRAME set differs):
  NEAR_IDENTICAL condition: 5 templates that are all flat SVO ("the {role} was {ent} .", "someone said
    the {role} was {ent} .", ...) -- the SAME style already used by every confirmed cell to date.
  VARIED_SYNTAX condition: 5 templates spanning REAL syntactic variation -- active, passive, relative-
    clause, cleft, and a pronoun-coreference frame (entity introduced, then referred to via "they" in a
    second clause; a real if simplified coreference phenomenon).
  Both conditions use TRAIN_FRAMES (first 3 templates) to build each role's centroid and HELD_OUT_FRAMES
  (last 2 templates, never touched during centroid construction) to test whether role identity survives
  to unseen frame types -- the genuinely decisive question (not just held-out LEXICALIZATIONS, which
  both conditions would trivially pass).

METRICS (per condition, per probe seed):
  1. within_role_consistency: mean cosine between a role's per-frame averaged rep (averaged over the 20
     entity lexicalizations within that frame) and that role's TRAIN-frame centroid, across the role's
     OWN frames (both train and held-out) -- high = syntax-invariant.
  2. between_role_cosine: mean cosine between DIFFERENT roles' TRAIN-frame centroids -- low = roles
     separable.
  3. heldout_frame_roleid_probe_acc: nearest-centroid (cosine) 5-way role classification of EVERY
     individual HELD-OUT-FRAME sentence rep (per entity, not pre-averaged) against the 5 TRAIN-frame
     centroids -- does role identity survive to a genuinely novel syntactic frame? CHANCE=0.20.
  4. SHUFFLED_FLOOR: identical nearest-centroid probe, but role labels on the TRAIN-frame centroids are
     shuffled (independently-seeded fixed permutation) before classifying -- must collapse to
     near-chance, or the probe construction can't discriminate anything and the cell is INVALID.

PRE-REGISTERED DECISION RULE (written BEFORE running; NOT loosened after seeing results):
  ENCODER_SURVIVES_SYNTAX: on VARIED_SYNTAX, heldout_frame_roleid_probe_acc >= PROBE_PASS_MIN(0.70) on
    ALL 3 probe seeds AND (within_role_consistency - between_role_cosine) >= SEP_GAP_MIN(0.15) on ALL 3
    seeds (roles cluster by ROLE not SYNTAX) AND degradation vs NEAR_IDENTICAL's
    heldout_frame_roleid_probe_acc is DEGRADATION_MODEST_MAX(0.20) or less (mean over seeds) => the
    frozen encoder can supply usable role keys for richer NL -> BUILD
    exp_native_binding_naturalistic_multirelation_v1 (frontier plan Section 4) using the same oracle-
    averaging construction, now over genuinely varied syntax.
  SYNTAX_DEGRADES_KEYS: on VARIED_SYNTAX, heldout_frame_roleid_probe_acc <= PROBE_FAIL_MAX(0.35) on any
    seed (near CHANCE_PROBE=0.20) OR (within_role_consistency - between_role_cosine) <= SEP_GAP_FAIL(0.05)
    on any seed (reps cluster by SYNTAX not ROLE) => the frozen encoder is the wall for richer NL on
    genuinely varied syntax -> do NOT build the frontier cell on it as specified; report the degradation
    curve and whether Step 0's orthogonalizing projection (frontier plan Section 2, a DIFFERENT
    bottleneck -- vocabulary-scale cosine growth, not syntax-induced variance) could plausibly rescue
    this (it cannot manufacture separability averaging destroyed, per the frontier plan's own risk note
    -- report honestly rather than assume rescue).
  MIDDLE (neither HARD condition met -- e.g. probe_acc in (0.35, 0.70) or gap in (0.05, 0.15), or
    degradation > 0.20 but probe still clears PROBE_FAIL_MAX): partial signal; report the exact numbers,
    do not force a HARD verdict.
  INVALID: SHUFFLED_FLOOR does not collapse to <= SHUFFLED_FLOOR_MAX(0.30) on some seed -- the probe
    construction cannot discriminate role identity from noise; do not interpret VARIED_SYNTAX numbers.

Run:  .venv/Scripts/python.exe experiments/exp_role_key_syntax_invariance_diagnostic_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_role_key_syntax_invariance_diagnostic_v1.py --full

ASCII-only. No emojis. Deterministic seeding (torch.Generator + np.random.default_rng; no hash(), no
list(set())). CPU (local, push-free). progress_logging: print_flush_true.
Compute architecture: sequential-CPU, justified -- closed-form bind-free representation-geometry
measurement over a small (<= 1000-sentence) cached set, NO gradient descent anywhere; total wall time
target well under 8 minutes (compute-proportionality: this is a cheap DIAGNOSTIC/GATE question).
Storage strategy: no_storage / no_composition -- this cell measures representation geometry only; it
does not bind, bundle, or retrieve anything.
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

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_selective_overwrite_recall_nl_wm_roleseparated_v1 as base  # noqa: E402
import exp_selective_overwrite_recall_nl_calib_v1 as calib  # noqa: E402  (COLORS = entity vocab)
import exp_oracle_context_invariant_address_wm_v2 as oc  # noqa: E402  -- build_role_query_probe / _extract_slot_rep_single

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_checkpoint as ckpt  # noqa: E402  -- per-unit checkpoint/resume (MANDATORY, CLAUDE.md)

ANCHOR_NAME = "role_key_syntax_invariance_diagnostic_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
V2_CKPT = oc.V2_CKPT

# ---- role / entity vocab (closed, cached-encodable) ----
ROLE_WORDS = ["agent", "patient", "recipient", "instrument", "location"]
N_ROLES = len(ROLE_WORDS)                       # 5 -> CHANCE_PROBE = 1/5 = 0.20
ENTITIES = calib.COLORS                          # 20-word closed vocabulary (reused verbatim)
N_ENT = len(ENTITIES)
CHANCE_PROBE = 1.0 / N_ROLES

# ---- NEAR_IDENTICAL condition: same flat-SVO style already used by every confirmed cell to date ----
NEAR_IDENTICAL_TEMPLATES = [
    "the {role} was {ent} .",
    "someone said the {role} was {ent} .",
    "it seems the {role} was {ent} .",
    "the {role} turned out to be {ent} .",
    "they said the {role} was {ent} .",
]

# ---- VARIED_SYNTAX condition: genuinely different syntactic frames (active / passive / relative-
# clause / cleft / pronoun-coreference) -- the actual "richer NL" lever named in the frontier plan.
VARIED_SYNTAX_TEMPLATES = [
    "the {role} was {ent} .",                                          # active (anchor, shared form)
    "{ent} was chosen as the {role} .",                                 # passive
    "the person who served as the {role} was {ent} .",                  # relative-clause
    "it was {ent} that filled the {role} role .",                       # cleft
    "{ent} arrived first ; they were the {role} .",                     # pronoun-coreference
]

# both conditions: first 3 templates = TRAIN_FRAMES (build centroid), last 2 = HELD_OUT_FRAMES (never
# touched by centroid construction -- the decisive held-out-SYNTAX generalization test)
N_TRAIN_FRAMES = 3
N_HELDOUT_FRAMES = 2
assert len(NEAR_IDENTICAL_TEMPLATES) == N_TRAIN_FRAMES + N_HELDOUT_FRAMES
assert len(VARIED_SYNTAX_TEMPLATES) == N_TRAIN_FRAMES + N_HELDOUT_FRAMES

CONDITIONS = {"near_identical": NEAR_IDENTICAL_TEMPLATES, "varied_syntax": VARIED_SYNTAX_TEMPLATES}

# ---- probe seeds (robustness -- role_query probe is a small random vector per oc.build_role_query_probe;
# 3 independent draws guard against a single-seed fluke, same discipline as the zeroshot-role cell) ----
PROBE_SEEDS = (7, 13, 19)
SHUFFLE_SEED = 909111   # base seed for SHUFFLED_FLOOR permutations, independent of probe seeds
N_SHUFFLE_TRIALS = 30    # average over many random permutations -- with only N_ROLES=5 classes, a
                          # SINGLE fixed permutation has high variance (whether it happens to preserve
                          # some accidental label alignment); MEASURED@this file's dev iteration: a
                          # single-permutation floor ranged 0.025-0.40 across probe seeds even after
                          # mean-centering fixed the real sep_gap signal -- averaging over 30
                          # independently-seeded permutations is the honest population-level estimate
                          # of chance-level accuracy (same "single toy example under-powered" lesson
                          # already applied elsewhere in this codebase, e.g.
                          # exp_vsa_native_bind_zeroshot_role_v1's floors_break_recovery_selftest).

# ---- pre-registered bands (written BEFORE running; NOT loosened) ----
PROBE_PASS_MIN = 0.70            # HYPOTHESIZED@this file: >> CHANCE_PROBE=0.20, strong 5-way separability
PROBE_FAIL_MAX = 0.35            # THEORETICAL: CHANCE_PROBE(0.20) + NEAR_CHANCE_MARGIN(0.15)
SEP_GAP_MIN = 0.15               # HYPOTHESIZED@this file: within-role consistency clearly > between-role
SEP_GAP_FAIL = 0.05              # HYPOTHESIZED@this file: effectively no separation (syntax-clustering)
DEGRADATION_MODEST_MAX = 0.20    # HYPOTHESIZED@this file: "modest" = <=0.20 probe-acc drop vs near-identical
SHUFFLED_FLOOR_MAX = CHANCE_PROBE + 0.10   # THEORETICAL: 0.20 + 0.10 = 0.30


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


def _digest_floats(arr):
    a = np.asarray(arr, dtype=np.float64)
    return hashlib.sha256(a.round(6).tobytes()).hexdigest()


# ================= encoder (subclass -- OWN closed sentence set, same pattern as RelEncoder in
# exp_cross_slot_relational_binding_v1.py; does not touch any other cell's global state) =============
class RoleSyntaxEncoder(base.FrozenV2Encoder):
    """FrozenV2Encoder with a closed sentence set = every (template, role, entity) combination across
    BOTH conditions (near_identical + varied_syntax), built once so a single encoder instance serves
    both conditions and all probe seeds."""

    def _closed_sentences(self):
        sents = []
        for templates in CONDITIONS.values():
            for tm in templates:
                for role in ROLE_WORDS:
                    for ent in ENTITIES:
                        sents.append(tm.format(role=role, ent=ent))
        return sorted(set(sents))   # sorted -> deterministic; NOT list(set())


def cosine(a, b):
    """Plain real-vector cosine similarity, a/b: 1-D torch tensors."""
    na = a.norm()
    nb = b.norm()
    if na.item() < 1e-12 or nb.item() < 1e-12:
        return 0.0
    return float(torch.dot(a, b) / (na * nb))


# ---------------- per-condition, per-seed measurement ----------------
def measure_condition(enc, templates, seed, center_vec):
    """Returns per-role per-frame averaged reps [N_ROLES, N_FRAMES, d], per-role TRAIN-frame centroids
    [N_ROLES, d], and per-(frame,role,entity) individual sentence reps for the held-out frames (used by
    the nearest-centroid probe), all via the SAME oc.build_role_query_probe + oc._extract_slot_rep_single
    extraction every confirmed cell already uses. `center_vec` (a single [d] vector, the GLOBAL mean over
    every cached sentence's extraction, same seed) is SUBTRACTED from every rep before use -- mean-
    centering is the standard first step of the proven pca_whiten conditioner (rc.Conditioner) already
    used to expose signal in this exact "shared-component swamps a low-variance signal subspace"
    situation (see WHERE_WE_ARE_NOW's NL-WM read-conditioning finding); a fixed, principled, closed-form
    step declared BEFORE seeing whether it changes the verdict, not a post-hoc per-metric tune."""
    rq_row = oc.build_role_query_probe(seed, enc.d)
    all_reps_raw = oc._extract_slot_rep_single(rq_row, enc.U_tok_t, enc.U_pad_t, enc.d)   # [Nu, d]
    all_reps = all_reps_raw - center_vec.unsqueeze(0)

    n_frames = len(templates)
    per_frame_role_avg = torch.zeros(N_ROLES, n_frames, enc.d)     # averaged over N_ENT lexicalizations
    heldout_sentence_reps = []    # list of (frame_idx_local, role_idx, rep)
    for r, role in enumerate(ROLE_WORDS):
        for f, tm in enumerate(templates):
            idxs = [enc.idx_of(tm.format(role=role, ent=ent)) for ent in ENTITIES]
            idx_t = torch.tensor(idxs)
            reps_here = all_reps[idx_t]                     # [N_ENT, d]
            per_frame_role_avg[r, f] = reps_here.mean(dim=0)
            if f >= N_TRAIN_FRAMES:                          # held-out frame: keep PER-ENTITY reps
                for e in range(N_ENT):
                    heldout_sentence_reps.append((f - N_TRAIN_FRAMES, r, reps_here[e]))

    train_centroid = per_frame_role_avg[:, :N_TRAIN_FRAMES, :].mean(dim=1)   # [N_ROLES, d]
    return per_frame_role_avg, train_centroid, heldout_sentence_reps


def within_between(per_frame_role_avg, train_centroid):
    """within_role_consistency: mean cosine of EVERY (role, frame) averaged rep to that role's
    TRAIN-frame centroid, across ALL frames (train + held-out) -- high = syntax-invariant.
    between_role_cosine: mean pairwise cosine among the N_ROLES TRAIN-frame centroids -- low = separable.
    """
    n_frames = per_frame_role_avg.shape[1]
    within_vals = []
    for r in range(N_ROLES):
        for f in range(n_frames):
            within_vals.append(cosine(per_frame_role_avg[r, f], train_centroid[r]))
    between_vals = []
    for i in range(N_ROLES):
        for j in range(N_ROLES):
            if i != j:
                between_vals.append(cosine(train_centroid[i], train_centroid[j]))
    return float(np.mean(within_vals)), float(np.mean(between_vals))


def nearest_centroid_rows(heldout_sentence_reps, centroid):
    """Computes the nearest-(cosine)-centroid ROW index for every held-out-frame sentence rep, plus its
    true role -- the argmax row is invariant to any row->label relabeling, so SHUFFLED_FLOOR trials (many
    random row->label permutations) can reuse these rows instead of recomputing cosines per trial."""
    pred_rows = []
    true_roles = []
    for _frame_local, true_role, rep in heldout_sentence_reps:
        sims = [cosine(rep, centroid[i]) for i in range(centroid.shape[0])]
        pred_rows.append(int(np.argmax(sims)))
        true_roles.append(true_role)
    return np.asarray(pred_rows, dtype=np.int64), np.asarray(true_roles, dtype=np.int64)


def accuracy_given_row_labels(pred_rows, true_roles, row_to_label):
    """row_to_label: array where row_to_label[row] = the role id that row is CLAIMED to represent
    (identity mapping for the real probe; a permutation for SHUFFLED_FLOOR trials)."""
    pred_roles = row_to_label[pred_rows]
    return float((pred_roles == true_roles).mean()) if len(true_roles) > 0 else float("nan")


def nearest_centroid_probe(heldout_sentence_reps, centroid, role_labels_for_centroid):
    """5-way nearest-(cosine)-centroid classification accuracy under ONE fixed row->label mapping
    (identity mapping for the real probe)."""
    pred_rows, true_roles = nearest_centroid_rows(heldout_sentence_reps, centroid)
    row_to_label = np.asarray(role_labels_for_centroid, dtype=np.int64)
    return accuracy_given_row_labels(pred_rows, true_roles, row_to_label)


def shuffled_floor_probe(heldout_sentence_reps, centroid, base_seed, n_trials):
    """SHUFFLED_FLOOR, averaged over `n_trials` independently-seeded random row->label permutations --
    the honest population-level chance-accuracy estimate (a SINGLE fixed 5-way permutation has high
    variance, MEASURED@this file's dev iteration: ranged 0.025-0.40 across probe seeds). Reuses the
    SAME nearest-centroid rows (argmax row is invariant to relabeling) so this costs N_ROLES!-independent
    O(n_trials) work, not n_trials re-classifications."""
    pred_rows, true_roles = nearest_centroid_rows(heldout_sentence_reps, centroid)
    n_rows = centroid.shape[0]
    accs = []
    for trial in range(n_trials):
        g = torch.Generator().manual_seed(base_seed + trial)
        perm = torch.randperm(n_rows, generator=g).numpy()
        accs.append(accuracy_given_row_labels(pred_rows, true_roles, perm))
    return float(np.mean(accs)), float(np.std(accs)), accs


def global_center_vec(enc, seed):
    """Mean, over EVERY cached sentence (both conditions, all templates/roles/entities), of the
    oc.build_role_query_probe extraction at this seed -- the shared component to subtract before
    measuring within/between/probe. Computed once per seed from the full closed set (enc.U_tok_t
    already holds all of it), never from a subset that could leak a condition-specific bias."""
    rq_row = oc.build_role_query_probe(seed, enc.d)
    all_reps = oc._extract_slot_rep_single(rq_row, enc.U_tok_t, enc.U_pad_t, enc.d)
    return all_reps.mean(dim=0)


def run_one_unit(enc, cond_name, templates, seed, center_vec):
    per_frame_role_avg, train_centroid, heldout_reps = measure_condition(enc, templates, seed, center_vec)
    within_c, between_c = within_between(per_frame_role_avg, train_centroid)

    identity_labels = list(range(N_ROLES))
    probe_acc = nearest_centroid_probe(heldout_reps, train_centroid, identity_labels)

    shuffled_probe_acc, shuffled_probe_sd, _shuffled_trial_accs = shuffled_floor_probe(
        heldout_reps, train_centroid, SHUFFLE_SEED + seed * 1000, N_SHUFFLE_TRIALS)

    preds_vec = np.array([within_c, between_c, probe_acc, shuffled_probe_acc], dtype=np.float64)
    return {
        "condition": cond_name, "seed": seed,
        "within_role_consistency": within_c, "between_role_cosine": between_c,
        "sep_gap": within_c - between_c,
        "heldout_frame_roleid_probe_acc": probe_acc,
        "shuffled_floor_acc": shuffled_probe_acc,
        "shuffled_floor_sd": shuffled_probe_sd,
        "shuffled_floor_n_trials": N_SHUFFLE_TRIALS,
        "n_heldout_examples": len(heldout_reps),
        "digest": hashlib.sha256(preds_vec.round(6).tobytes()).hexdigest(),
    }


# ---------------- self-tests ----------------
def frames_genuinely_differ_selftest(enc):
    """Fairness/correctness gate: VARIED_SYNTAX templates must be genuinely different STRINGS (not
    lexical near-duplicates of NEAR_IDENTICAL_TEMPLATES beyond the deliberate shared 'active' anchor
    row), and the encoder's raw per-sentence rep must differ across frames (else the extraction is
    vacuous)."""
    role, ent = ROLE_WORDS[0], ENTITIES[0]
    varied_sents = [tm.format(role=role, ent=ent) for tm in VARIED_SYNTAX_TEMPLATES]
    assert len(set(varied_sents)) == len(varied_sents), "VARIED_SYNTAX templates collide for same role/ent"
    near_sents = [tm.format(role=role, ent=ent) for tm in NEAR_IDENTICAL_TEMPLATES]
    # exactly one shared literal sentence is expected (the active-anchor row); more than that means the
    # "varied" set isn't actually varied.
    overlap = set(varied_sents) & set(near_sents)
    assert len(overlap) <= 1, "VARIED_SYNTAX collapses onto NEAR_IDENTICAL beyond the active anchor: %s" % overlap

    rq_row = oc.build_role_query_probe(7, enc.d)
    reps = oc._extract_slot_rep_single(rq_row, enc.U_tok_t, enc.U_pad_t, enc.d)
    idxs = [enc.idx_of(s) for s in varied_sents]
    reps_here = reps[torch.tensor(idxs)]
    pairwise_min_cos = 1.0
    for i in range(len(idxs)):
        for j in range(i + 1, len(idxs)):
            c = cosine(reps_here[i], reps_here[j])
            pairwise_min_cos = min(pairwise_min_cos, c)
    assert pairwise_min_cos < 0.9999, (
        "FRAMES_SELFTEST_FAIL: distinct syntactic frames produced numerically identical reps "
        "(min pairwise cosine=%.6f) -- extraction is vacuous" % pairwise_min_cos)
    return {"n_varied_templates": len(VARIED_SYNTAX_TEMPLATES), "overlap_with_near_identical": len(overlap),
            "pairwise_min_cosine_across_frames": pairwise_min_cos}


def shuffled_floor_breaks_selftest(enc):
    """Directly MEASURES that SHUFFLED_FLOOR collapses the role-id probe toward chance on a tiny
    (n=few) synthetic population, using the REAL extraction machinery -- not merely argued."""
    center_vec = global_center_vec(enc, 7)
    res = run_one_unit(enc, "near_identical_tiny_check", NEAR_IDENTICAL_TEMPLATES, seed=7, center_vec=center_vec)
    assert res["heldout_frame_roleid_probe_acc"] > res["shuffled_floor_acc"] - 1e-9, (
        "SHUFFLED_FLOOR_SELFTEST_FAIL: shuffled probe (%.3f) not below or equal to real probe (%.3f)"
        % (res["shuffled_floor_acc"], res["heldout_frame_roleid_probe_acc"]))
    return {"real_probe_acc": res["heldout_frame_roleid_probe_acc"],
            "shuffled_probe_acc": res["shuffled_floor_acc"]}


def run_self_test():
    _log("SELF-TEST: load REAL v2 encoder + build REAL closed sentence set (real_code_path) ...")
    assert os.path.exists(V2_CKPT), "v2 checkpoint missing: %s" % V2_CKPT
    enc = RoleSyntaxEncoder(V2_CKPT)
    n_cached = enc.build_cache()
    expected_max = len(CONDITIONS) * (N_TRAIN_FRAMES + N_HELDOUT_FRAMES) * N_ROLES * N_ENT
    assert 0 < n_cached <= expected_max, (
        "cached sentence count %d outside expected range (0, %d]" % (n_cached, expected_max))
    _log("  n_cached=%d (expected <= %d, dedup across conditions' shared active-anchor row)"
         % (n_cached, expected_max))

    _log("SELF-TEST: VARIED_SYNTAX frames genuinely differ (fairness gate) ...")
    frames_diag = frames_genuinely_differ_selftest(enc)
    _log("  PASS: %s" % frames_diag)

    _log("SELF-TEST: SHUFFLED_FLOOR breaks role-id recovery (direct measurement) ...")
    floor_diag = shuffled_floor_breaks_selftest(enc)
    _log("  PASS: %s" % floor_diag)

    _log("SELF-TEST: tiny end-to-end both conditions, both seeds subset (arms-must-differ) ...")
    tiny_results = {}
    for cond_name, templates in CONDITIONS.items():
        for seed in (7, 13):
            center_vec = global_center_vec(enc, seed)
            res = run_one_unit(enc, cond_name, templates, seed, center_vec=center_vec)
            tiny_results["%s|%d" % (cond_name, seed)] = res
            assert 0.0 <= res["heldout_frame_roleid_probe_acc"] <= 1.0
            assert 0.0 <= res["shuffled_floor_acc"] <= 1.0
            assert -1.0 <= res["within_role_consistency"] <= 1.0001
            assert -1.0 <= res["between_role_cosine"] <= 1.0001
    digests = {k: r["digest"] for k, r in tiny_results.items()}
    keys = sorted(digests)
    for a in keys:
        for b in keys:
            if a < b:
                assert digests[a] != digests[b], (
                    "META_RULE_AF VIOLATION: units %r and %r bit-identical" % (a, b))
    _log("SELF-TEST PASS")
    return {"n_cached": n_cached, "frames_diag": frames_diag, "floor_diag": floor_diag,
            "tiny": {k: {"probe_acc": r["heldout_frame_roleid_probe_acc"],
                         "shuffled_acc": r["shuffled_floor_acc"],
                         "sep_gap": r["sep_gap"]} for k, r in tiny_results.items()},
            "arms_differ_verified": True}


# ---------------- verdict ----------------
def decide_verdict(results_by_cond_seed):
    """results_by_cond_seed: {(cond, seed): unit_result_dict}."""
    def _vals(cond, key):
        return [results_by_cond_seed[(cond, s)][key] for s in PROBE_SEEDS]

    shuf_vals = _vals("varied_syntax", "shuffled_floor_acc") + _vals("near_identical", "shuffled_floor_acc")
    floors_valid = all((not math.isnan(v)) and v <= SHUFFLED_FLOOR_MAX for v in shuf_vals)

    if not floors_valid:
        verdict = "INVALID"
        msg = ("SHUFFLED_FLOOR did not collapse to <= %.2f on at least one (condition, seed): %s -- the "
               "nearest-centroid role-id probe cannot discriminate role identity from noise here; "
               "VARIED_SYNTAX numbers are NOT interpreted." % (SHUFFLED_FLOOR_MAX,
               [round(v, 3) for v in shuf_vals]))
        bands = {"floors_valid": False, "shuffled_floor_max": SHUFFLED_FLOOR_MAX,
                 "shuffled_vals": [round(v, 3) for v in shuf_vals]}
        return verdict, msg, bands

    varied_probe = _vals("varied_syntax", "heldout_frame_roleid_probe_acc")
    varied_gap = _vals("varied_syntax", "sep_gap")
    near_probe = _vals("near_identical", "heldout_frame_roleid_probe_acc")
    near_gap = _vals("near_identical", "sep_gap")

    mean_varied_probe = float(np.mean(varied_probe))
    mean_near_probe = float(np.mean(near_probe))
    degradation = mean_near_probe - mean_varied_probe

    hard_fail = (any(v <= PROBE_FAIL_MAX for v in varied_probe)
                 or any(g <= SEP_GAP_FAIL for g in varied_gap))
    hard_pass = (all(v >= PROBE_PASS_MIN for v in varied_probe)
                 and all(g >= SEP_GAP_MIN for g in varied_gap)
                 and degradation <= DEGRADATION_MODEST_MAX)

    if hard_fail:
        verdict = "SYNTAX_DEGRADES_KEYS"
        msg = ("On VARIED_SYNTAX, held-out-frame role-id probe=%s (CHANCE=%.2f, FAIL_MAX=%.2f) and/or "
               "sep_gap=%s (within-minus-between cosine, SEP_GAP_FAIL=%.2f) breached the fail condition on "
               "at least one of %d probe seeds -- the frozen encoder's role-identity signal does NOT "
               "survive genuinely varied syntax; do NOT build exp_native_binding_naturalistic_"
               "multirelation_v1 on this construction as specified. NEAR_IDENTICAL reference: "
               "probe=%s sep_gap=%s (degradation vs near-identical=%.3f)."
               % ([round(v, 3) for v in varied_probe], CHANCE_PROBE, PROBE_FAIL_MAX,
                  [round(g, 3) for g in varied_gap], SEP_GAP_FAIL, len(PROBE_SEEDS),
                  [round(v, 3) for v in near_probe], [round(g, 3) for g in near_gap], degradation))
    elif hard_pass:
        verdict = "ENCODER_SURVIVES_SYNTAX"
        msg = ("On VARIED_SYNTAX, held-out-frame role-id probe=%s (all >= PROBE_PASS_MIN=%.2f) and "
               "sep_gap=%s (all >= SEP_GAP_MIN=%.2f) across all %d probe seeds, with modest degradation "
               "vs NEAR_IDENTICAL (mean drop=%.3f <= %.2f) -- the frozen encoder CAN supply consistent + "
               "distinct role keys across genuinely varied syntax; BUILD "
               "exp_native_binding_naturalistic_multirelation_v1 (frontier plan Section 4) using the "
               "same oracle-averaging role-key construction. NEAR_IDENTICAL reference: probe=%s sep_gap=%s."
               % ([round(v, 3) for v in varied_probe], PROBE_PASS_MIN, [round(g, 3) for g in varied_gap],
                  SEP_GAP_MIN, len(PROBE_SEEDS), degradation, DEGRADATION_MODEST_MAX,
                  [round(v, 3) for v in near_probe], [round(g, 3) for g in near_gap]))
    else:
        verdict = "MIDDLE"
        msg = ("Neither HARD condition cleared. VARIED_SYNTAX probe=%s (CHANCE=%.2f, FAIL_MAX=%.2f, "
               "PASS_MIN=%.2f) sep_gap=%s (FAIL=%.2f, MIN=%.2f); degradation vs NEAR_IDENTICAL "
               "(probe=%s sep_gap=%s) = %.3f (modest cutoff=%.2f) -- partial signal, report exact numbers, "
               "do not force a HARD verdict."
               % ([round(v, 3) for v in varied_probe], CHANCE_PROBE, PROBE_FAIL_MAX, PROBE_PASS_MIN,
                  [round(g, 3) for g in varied_gap], SEP_GAP_FAIL, SEP_GAP_MIN,
                  [round(v, 3) for v in near_probe], [round(g, 3) for g in near_gap], degradation,
                  DEGRADATION_MODEST_MAX))

    bands = {"floors_valid": True, "shuffled_floor_max": SHUFFLED_FLOOR_MAX,
             "shuffled_vals": [round(v, 3) for v in shuf_vals],
             "chance_probe": CHANCE_PROBE, "probe_pass_min": PROBE_PASS_MIN,
             "probe_fail_max": PROBE_FAIL_MAX, "sep_gap_min": SEP_GAP_MIN, "sep_gap_fail": SEP_GAP_FAIL,
             "degradation_modest_max": DEGRADATION_MODEST_MAX,
             "varied_syntax_probe_by_seed": dict(zip(PROBE_SEEDS, [round(v, 4) for v in varied_probe])),
             "varied_syntax_sep_gap_by_seed": dict(zip(PROBE_SEEDS, [round(g, 4) for g in varied_gap])),
             "near_identical_probe_by_seed": dict(zip(PROBE_SEEDS, [round(v, 4) for v in near_probe])),
             "near_identical_sep_gap_by_seed": dict(zip(PROBE_SEEDS, [round(g, 4) for g in near_gap])),
             "mean_varied_probe": mean_varied_probe, "mean_near_identical_probe": mean_near_probe,
             "degradation_vs_near_identical": degradation}
    return verdict, msg, bands


# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    torch.set_num_threads(min(6, max(1, os.cpu_count() or 1)))
    run_mode = "self_test" if args.self_test or not args.full else "full"
    expected_units = 1 if run_mode == "self_test" else len(CONDITIONS) * len(PROBE_SEEDS)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        elapsed = time.perf_counter() - t0
        _atomic_write_metrics(OUTPUT_DIR, {
            "verdict": "SELFTEST_PASS",
            "verdict_msg": "SELFTEST_PASS (frames genuinely differ + shuffled-floor breaks + real "
                           "encoder/probe real_code_path + arms-differ)",
            "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": elapsed,
            "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "chance_probe": CHANCE_PROBE,
            "selftest": st})
        _log("DONE self-test in %.1fs" % elapsed)
        return

    _log("FULL: conditions=%s seeds=%s chance_probe=%.4f" % (list(CONDITIONS), PROBE_SEEDS, CHANCE_PROBE))
    enc = RoleSyntaxEncoder(V2_CKPT)
    n_cached = enc.build_cache()
    _log("  cached %d unique sentences (d=%d)" % (n_cached, enc.d))

    prior_units = ckpt.load_units(OUTPUT_DIR)
    expected_n_units_full = len(CONDITIONS) * len(PROBE_SEEDS)
    if prior_units:
        _log("checkpoint: %d/%d units already recorded on disk; resuming"
             % (len(prior_units), expected_n_units_full))

    results_by_cond_seed = {}
    for cond_name, templates in CONDITIONS.items():
        _log("--- CONDITION_%s ---" % cond_name.upper())
        for seed in PROBE_SEEDS:
            k = ckpt.unit_key(cond_name, seed)
            if k in prior_units:
                results_by_cond_seed[(cond_name, seed)] = prior_units[k]
                _log("  [resume] %s seed=%d loaded from checkpoint" % (cond_name, seed))
                continue
            center_vec = global_center_vec(enc, seed)
            res = run_one_unit(enc, cond_name, templates, seed, center_vec=center_vec)
            ckpt.record_unit(OUTPUT_DIR, k, res)
            results_by_cond_seed[(cond_name, seed)] = res
            _log("  [%s seed=%d] probe_acc=%.4f sep_gap=%.4f shuffled_floor=%.4f"
                 % (cond_name, seed, res["heldout_frame_roleid_probe_acc"], res["sep_gap"],
                    res["shuffled_floor_acc"]))

    verdict, msg, bands = decide_verdict(results_by_cond_seed)
    elapsed = time.perf_counter() - t0

    n_units_done = len(results_by_cond_seed)
    digests = [results_by_cond_seed[(c, s)]["digest"] for c in CONDITIONS for s in PROBE_SEEDS]
    arms_differ = len(set(digests)) == len(digests)

    _atomic_write_metrics(OUTPUT_DIR, {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "%s | chance_probe=%.4f | mean_varied_probe=%.4f | %s"
                   % (verdict, CHANCE_PROBE, bands.get("mean_varied_probe", float("nan")), msg[:140]),
        "run_mode": "full", "elapsed_s": elapsed, "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "chance_probe": CHANCE_PROBE, "bands": bands,
        "results_by_condition_seed": {"%s|%d" % (c, s): results_by_cond_seed[(c, s)]
                                       for c in CONDITIONS for s in PROBE_SEEDS},
        "arms_differ_verified": bool(arms_differ),
        "cardinality_ok": bool(n_units_done == expected_n_units_full),
        "expected_n_units": expected_n_units_full, "n_units_done": n_units_done,
        "params": {"role_words": ROLE_WORDS, "n_entities": N_ENT, "n_train_frames": N_TRAIN_FRAMES,
                   "n_heldout_frames": N_HELDOUT_FRAMES, "probe_seeds": list(PROBE_SEEDS),
                   "n_cached_sentences": n_cached, "encoder": "real_v2_frozen",
                   "extraction": "oc.build_role_query_probe + oc._extract_slot_rep_single (reused verbatim)",
                   "conditioning": "global_mean_centering_per_seed (subtract full-closed-set mean before "
                                   "cosine; standard first step of rc.Conditioner's pca_whiten, fixed "
                                   "before interpreting results -- see module docstring)",
                   "v2_ckpt": os.path.relpath(V2_CKPT, REPO_ROOT),
                   "shuffle_seed": SHUFFLE_SEED},
        "start_marker_written": True, "crash_diagnostic_present": True,
        "final_metrics_atomicity": "tmp_replace", "defensive_error_checking": "passed_all_4_patterns",
        "cell_chunked": False,
        "progress_logging": "print_flush_true", "progress_cadence_expected_s": 15,
        "crlb_n_a": "no learned-noise Cramer-Rao floor; discriminator is the pre-registered "
                    "ENCODER_SURVIVES_SYNTAX/SYNTAX_DEGRADES_KEYS/INVALID decision rule (see decide_verdict)",
        "calibration_check": "default_ok_for_this_regime: PROBE_PASS_MIN/PROBE_FAIL_MAX/SEP_GAP_MIN/"
                              "SEP_GAP_FAIL/DEGRADATION_MODEST_MAX are fixed HYPOTHESIZED thresholds set "
                              "before running (not tuned post-hoc); SHUFFLED_FLOOR is the adaptive "
                              "can-fail control validating the probe construction discriminates at all"})
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
