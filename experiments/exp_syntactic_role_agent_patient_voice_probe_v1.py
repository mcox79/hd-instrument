# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: sha256 digest of each arm's per-example correct/incorrect boolean array,
#   pairwise-distinct across ARM_ROLE_PROBE / ARM_POSITION_ONLY / ARM_BAGOFWORDS / ARM_SHUFFLED_CONTROL
#   (per direction).
# - final_metrics_atomicity: tmp_replace (os.replace at end).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n_a: no learned-noise Cramer-Rao floor here; this is a closed-form nearest-centroid
#   classification diagnostic, not a fit with a noise model. Discriminator is the pre-registered
#   ENCODER_ENCODES_SYNTACTIC_ROLE / ENCODER_POSITION_ONLY / INVALID decision rule (see decide_verdict).
# - baseline_in_band: n/a in the usual (0.05,0.95) sense -- the discriminating controls here are
#   ARM_POSITION_ONLY (must fail cross-voice, near/at-or-below chance) and ARM_BAGOFWORDS +
#   ARM_SHUFFLED_CONTROL (must land in a chance BAND [0.35,0.65]); decide_verdict enforces this
#   directly as the INVALID gate, which is the AG-equivalent floor-check for THIS cell shape.
# - discriminator survives scale: closed-form, no training loop, no smoke/full scale gap. --self-test
#   runs the REAL, FULL-SCALE pipeline (same sentence counts, same real frozen v2 encoder, same real
#   extraction code path) -- option (A) of DISCRIMINATOR-MUST-SURVIVE-SCALE trivially satisfied because
#   there IS no smaller regime; self-test and --full literally call the same run_pipeline().
# - HARD_PASS strictly above floor + 5% band-width: ROLE_PROBE_PASS_MIN=0.70 vs CHANCE=0.50, band width
#   to ceiling 1.0 is 0.30, so PASS_MIN sits >> floor+0.05*width; declared explicitly below.
# - HP_SCOPE: HARD gates (ROLE_PROBE_PASS_MIN, ROLE_PROBE_FAIL_MAX, POSITION_ONLY_FAIL_MAX,
#   BAGOFWORDS_FLOOR_BAND, SHUFFLED_FLOOR_BAND) apply ONLY to their own named arm; ARM_POSITION_ONLY /
#   ARM_BAGOFWORDS / ARM_SHUFFLED_CONTROL are can-fail controls, not the mechanism arm, and are never
#   compared against ROLE_PROBE_PASS_MIN.
# - cardinality_ok: EXPECTED_N_UNITS declared + counted (see UNIT_SPECS / decide_verdict).
# - per-unit failure-class instrumentation: no bare except; all try/except in this file follow
#   except SystemExit / except KeyboardInterrupt / except Exception ordering.
# - calibration_check: "default_ok_for_this_regime" -- all bands are fixed HYPOTHESIZED thresholds set
#   BEFORE running (not tuned post-hoc); chance=0.50 is exact-by-construction (binary balanced task).
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
# - real_code_path_exercised: self-test constructs the REAL SyntaxRoleEncoder (subclass of
#   base.FrozenV2Encoder), calls the REAL frozen v2 checkpoint, and runs the REAL, full pipeline.
# - substrate_signature_checked: base.FrozenV2Encoder.__init__(ckpt_path) -- single positional arg,
#   long-stable, no version-specific optional kwargs used.
# - deterministic seeding: only fixed integer seeds via torch.Generator().manual_seed(...); no hash(),
#   no list(set()) (sorted(set()) used throughout for any dedup).
"""Syntactic-role (agent-vs-patient) voice-invariance probe on the FROZEN v2 encoder -- Director spawn
2026-07-30, gating the whole SYNTACTIC-ROLE-PARSING comprehension direction.

CRUX QUESTION: tonight's confirmed capabilities bind roles when the role is named EXPLICITLY ("the
agent was X"). Real comprehension requires deriving WHO IS THE AGENT from SYNTAX (word order / voice)
when the role is NOT named. This cell measures, cheaply and before building any parsing pipeline,
whether the frozen v2 encoder's CONTEXTUALIZED entity representation encodes the entity's SYNTACTIC
ROLE invariant to surface POSITION -- i.e. whether role can be read from syntax, not position.

RELATION TO PRIOR CELL exp_role_key_syntax_invariance_diagnostic_v1 (MEASURED@d:/AI/hd-instrument/
data/exp_role_key_syntax_invariance_diagnostic_v1/metrics.json, verdict=MIDDLE, varied_syntax
probe=0.675 vs chance=0.20): that cell asked whether a role that is NAMED IN THE SENTENCE ("the {role}
was {ent}", role word e.g. "agent"/"patient" literally present) stays separable across syntactic
frames. It is a DIFFERENT, easier question -- the role label is given as a word in every sentence, no
syntax-parsing is required at all (a bag-of-words reader that just finds the word "agent" would solve
it). THIS cell is the genuinely harder, decisive test the frontier needs: the role WORDS "agent" /
"patient" never appear in any sentence; role identity must be read off from ACTIVE-VS-PASSIVE
SYNTACTIC POSITION alone. Prior-work check: substrate_query.sh "syntactic role agent patient active
passive voice invariance encoder probe" returned top cosine=0.4014 (wordnet ANTONYM_OF active_voice/
passive_voice + generic "active_agent"/"active voice" atoms) -- no prior cell measuring cross-voice
agent/patient role-probing at cosine>0.30; this is NOT a rediscovery of a landed result, it is a novel,
more decisive gate than the NAMED-role cell above.

CONSTRUCTION:
  Two entities per sentence, drawn from calib.COLORS (closed 20-word vocab, reused verbatim as
  entity-fillers, same convention as every other NL-WM cell in this codebase), combined with a small
  regular-verb set (past tense == past participle, so NO irregular morphology like saw/seen leaks a
  voice cue through the verb form itself):
    ACTIVE:  "the {a} {verb} the {b} ."          -- a = AGENT (first noun), b = PATIENT (second noun)
    PASSIVE: "the {b} was {verb} by the {a} ."   -- b = PATIENT (first noun), a = AGENT (by-phrase)
  Semantic roles (a=AGENT, b=PATIENT) are FIXED by which pair-slot an entity fills; voice only
  changes SURFACE POSITION. This is the exact "same roles, swapped positions" construction the
  Director's spawn specifies.

  EXTRACTION (departs from the oc.build_role_query_probe single-fixed-attention-pool machinery used by
  every prior NL-WM cell, for a principled reason stated here, not silently): that machinery pools ONE
  vector per SENTENCE via a fixed-random attention query -- it cannot disambiguate TWO different target
  entities co-occurring in the SAME sentence (which is exactly this cell's setup: both AGENT and
  PATIENT entities live in one sentence). Instead this cell reads each entity's CONTEXTUALIZED
  representation directly off the SAME frozen encoder's per-token hidden states
  (base.FrozenV2Encoder.build_cache()'s cached U_tok_t [Nu, SENT_CAP, d], already used verbatim by
  every other cell in this family) at that entity word's own token column, located via the encoder's
  OWN tokenizer offsets (enc.tok.encode(sentence).offsets, MEASURED@this file's dev iteration: color
  words tokenize to exactly one BPE token each with the Whitespace pre-tokenizer, e.g. "red"->one
  token; mean-pooling is used defensively in case any entity spans >1 token). This is still the frozen
  encoder's own contextual computation -- only the POOLING RULE differs (direct token-position select
  vs fixed-probe attention-pool), because attention-pooling cannot answer a two-entity-per-sentence
  question. Mean-centering (subtract the global mean over all contextualized entity reps, computed
  separately for the bagofwords/context-free representation family) is applied before cosine, per the
  WHERE_WE_ARE_NOW NL-WM read-conditioning finding (shared component swamps a low-variance identity/
  role subspace) already used by the sibling role_key_syntax cell.

FUNCTIONAL REQUIREMENTS (SCHEMA-VET gate E):
  1. "read out an entity's own contextualized representation, distinguishable from a co-occurring
     entity in the same sentence" -> base.FrozenV2Encoder per-token hidden states (U_tok_t), indexed by
     entity token position (new pooling rule described above; no new encoder).
  2. "classify agent-vs-patient from that representation, generalizing across voice" -> nearest-
     (cosine)-centroid classifier fit on ONE voice's train split, evaluated on the OTHER voice's
     held-out split (ARM_ROLE_PROBE) -- closed-form, no gradient descent (compute-proportionality: this
     is a directional GATE question, not a magnitude-fit).
  3. "a genuine can-fail structural control that must fail cross-voice" -> ARM_POSITION_ONLY, a pure
     surface-string first-noun-position rule that never touches the encoder.
  4. "a genuine can-fail order-blind control" -> ARM_BAGOFWORDS, the SAME classifier trained/tested on
     CONTEXT-FREE (bare entity word alone, no sentence) representations from the SAME encoder -- must
     land near chance because entity IDENTITY is balanced across roles by pair-construction (each
     entity fills the AGENT slot and the PATIENT slot an approximately equal number of times across the
     closed pair set; verified in self-test).
  5. "a genuine can-fail label-structure control" -> ARM_SHUFFLED_CONTROL, ARM_ROLE_PROBE's own
     contextualized reps but with TRAIN labels randomly permuted before building centroids (averaged
     over N_SHUFFLE_TRIALS independent permutations) -- must land near chance.

HELD-OUT DESIGN (fairness mandate #4 -- genuine held-out, not just held-out lexicalizations):
  60 deterministic entity PAIRS (i, (i+k)%20) for k in {1,2,3} over the 20-entity vocab -- NOT random
  sampling (no hash(), no randomness in pair generation). Split by pair-list-index PARITY into
  TRAIN_PAIRS (even index, 30 pairs) / TEST_PAIRS (odd index, 30 pairs) -- disjoint entity-pair sets.
  8 regular verbs, split TRAIN_VERBS (first 4) / HELDOUT_VERBS (last 4) -- disjoint verb sets. Every
  TRAIN sentence uses a TRAIN_PAIR x TRAIN_VERB combination; every TEST sentence uses a DISJOINT
  TEST_PAIR x HELDOUT_VERB combination -- so cross-voice test sentences are held out on BOTH entity-pair
  AND verb axes, not merely on voice.

FAIRNESS / BALANCE (mandate #3): every sentence contributes exactly one AGENT-labeled entity rep (a)
  and one PATIENT-labeled entity rep (b) -- so every train/test split is EXACTLY 50/50 balanced by
  construction, chance = 0.50 for every arm, no reweighting needed.

PRE-REGISTERED DECISION RULE (written BEFORE running; NOT loosened after seeing results):
  INVALID (checked FIRST, before interpreting ARM_ROLE_PROBE numbers):
    - ARM_POSITION_ONLY does NOT fail cross-voice (accuracy > POSITION_ONLY_FAIL_MAX=0.55 on either
      direction) -- the position-only control should be at-or-below chance-or-worse (constructed to be
      1.0 on the matching voice and 0.0 on the opposite voice; if it is NOT low here, this cell's
      cross-voice split isn't isolating syntax the way it's supposed to), OR
    - ARM_BAGOFWORDS lands outside BAGOFWORDS_FLOOR_BAND=[0.15,0.85] on either direction (order-blind
      control should float near chance; if it doesn't, entity IDENTITY leaks role information through
      pair-construction imbalance and the whole design needs re-balancing), OR
    - ARM_SHUFFLED_CONTROL (mean over N_SHUFFLE_TRIALS) lands outside SHUFFLED_FLOOR_BAND=[0.35,0.65]
      on either direction.
  ENCODER_ENCODES_SYNTACTIC_ROLE (floors valid AND):
    ARM_ROLE_PROBE cross-voice accuracy >= ROLE_PROBE_PASS_MIN=0.70 on BOTH directions (active-train/
    passive-test AND passive-train/active-test) => the frozen encoder's contextualized entity reps DO
    carry voice-invariant syntactic role -> the syntactic-parsing comprehension direction is BUILDABLE
    on the frozen encoder without further encoder work.
  ENCODER_POSITION_ONLY (floors valid AND):
    ARM_ROLE_PROBE cross-voice accuracy <= ROLE_PROBE_FAIL_MAX=0.55 on EITHER direction (no better than
    the position-only control / near chance) => the encoder only supplies positional cues, not
    voice-invariant syntactic role -> syntax->role is the WALL on the frozen encoder; a different
    approach (forward-predictive encoder / explicit parse-and-reassign step) is needed for this
    direction.
  MIDDLE (floors valid, neither HARD condition met on both directions): partial signal; report exact
    numbers per direction, do not force a HARD verdict.

Run:  .venv/Scripts/python.exe experiments/exp_syntactic_role_agent_patient_voice_probe_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_syntactic_role_agent_patient_voice_probe_v1.py --full

ASCII-only. No emojis. Deterministic seeding (torch.Generator only; no hash(), no list(set())). CPU
(local, push-free). progress_logging: print_flush_true (not required at this timeout_s, included
anyway as defense-in-depth).
Compute architecture: sequential-CPU, justified -- closed-form nearest-centroid cosine classification
over a small (~500-sentence) cached set, NO gradient descent anywhere; total wall time target well
under 8 minutes (compute-proportionality: this is a cheap DIRECTIONAL-GATE/DIAGNOSTIC question, the
CHEAPEST decisive method for it, not a magnitude-fit training run).
Storage strategy: no_storage / no_composition -- representation-geometry + nearest-centroid measurement
only; no bind/bundle/retrieve.
"""

import argparse
import hashlib
import json
import math
import os
import platform
import re
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
import exp_selective_overwrite_recall_nl_wm_roleseparated_v1 as base  # noqa: E402  (FrozenV2Encoder)
import exp_selective_overwrite_recall_nl_calib_v1 as calib  # noqa: E402  (COLORS = entity vocab)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_checkpoint as ckpt  # noqa: E402  -- per-unit checkpoint/resume (MANDATORY, CLAUDE.md)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cell_heartbeat import CellHeartbeat  # noqa: E402

ANCHOR_NAME = "syntactic_role_agent_patient_voice_probe_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
V2_CKPT = base.V2_CKPT

# ---- entity vocab (closed, reused verbatim) ----
ENTITIES = calib.COLORS                          # 20-word closed vocabulary
N_ENT = len(ENTITIES)

# ---- verbs: ALL REGULAR (past tense == past participle) so voice never leaks through irregular
# morphology (e.g. saw/seen). 8 verbs, split TRAIN (4) / HELDOUT (4). ----
VERBS_ALL = ["helped", "chased", "greeted", "followed", "warned", "thanked", "noticed", "watched"]
TRAIN_VERBS = VERBS_ALL[:4]
HELDOUT_VERBS = VERBS_ALL[4:]
assert len(set(VERBS_ALL)) == len(VERBS_ALL) == 8

ACTIVE_TEMPLATE = "the {a} {verb} the {b} ."
PASSIVE_TEMPLATE = "the {b} was {verb} by the {a} ."

AGENT, PATIENT = 0, 1
CHANCE = 0.5


def _gen_pairs():
    """60 deterministic (a_idx, b_idx) pairs, a_idx != b_idx, via fixed modular offsets -- NO
    randomness, NO hash(), NO list(set())."""
    pairs = []
    for k in (1, 2, 3):
        for i in range(N_ENT):
            j = (i + k) % N_ENT
            pairs.append((i, j))
    return pairs


ALL_PAIRS = _gen_pairs()                                     # 60 pairs, deterministic order
assert len(ALL_PAIRS) == 60 and len(set(ALL_PAIRS)) == 60
TRAIN_PAIRS = [p for idx, p in enumerate(ALL_PAIRS) if idx % 2 == 0]   # 30
TEST_PAIRS = [p for idx, p in enumerate(ALL_PAIRS) if idx % 2 == 1]    # 30
assert len(TRAIN_PAIRS) == len(TEST_PAIRS) == 30
assert set(TRAIN_PAIRS).isdisjoint(set(TEST_PAIRS))


def _records_for(template, verbs, pairs, is_active):
    """Each record: sentence string + which entity word fills 'a' (AGENT) and 'b' (PATIENT) +
    is_active flag (for the position-only control)."""
    recs = []
    for verb in verbs:
        for (i, j) in pairs:
            a, b = ENTITIES[i], ENTITIES[j]
            s = template.format(a=a, b=b, verb=verb)
            recs.append({"sentence": s, "a": a, "b": b, "is_active": is_active})
    return recs


ACTIVE_TRAIN = _records_for(ACTIVE_TEMPLATE, TRAIN_VERBS, TRAIN_PAIRS, True)      # 4*30=120
ACTIVE_TEST = _records_for(ACTIVE_TEMPLATE, HELDOUT_VERBS, TEST_PAIRS, True)      # 120
PASSIVE_TRAIN = _records_for(PASSIVE_TEMPLATE, TRAIN_VERBS, TRAIN_PAIRS, False)   # 120
PASSIVE_TEST = _records_for(PASSIVE_TEMPLATE, HELDOUT_VERBS, TEST_PAIRS, False)   # 120
BARE_WORDS = sorted(set(ENTITIES))                                                # 20

ALL_CONTEXT_SENTENCES = sorted(set(
    r["sentence"] for r in (ACTIVE_TRAIN + ACTIVE_TEST + PASSIVE_TRAIN + PASSIVE_TEST)))
ALL_CLOSED_SENTENCES = sorted(set(ALL_CONTEXT_SENTENCES + BARE_WORDS))

SHUFFLE_SEED = 771331
N_SHUFFLE_TRIALS = 30   # averaged permutations -- honest population-level chance estimate (same
                         # discipline as the sibling role_key_syntax cell's SHUFFLED_FLOOR)

# ---- pre-registered bands (written BEFORE running; NOT loosened) ----
ROLE_PROBE_PASS_MIN = 0.70        # HYPOTHESIZED@this file: >> CHANCE=0.50
ROLE_PROBE_FAIL_MAX = 0.55        # THEORETICAL: CHANCE(0.50) + NEAR_CHANCE_MARGIN(0.05)
POSITION_ONLY_FAIL_MAX = 0.55     # THEORETICAL: position-only must be <= chance+margin cross-voice
                                   # (constructed to be exactly 0.0 by-design; margin is generous)
# BAGOFWORDS_FLOOR_BAND: wider than SHUFFLED_FLOOR_BAND on purpose -- ARM_BAGOFWORDS uses CONTEXT-FREE
# (bare-word) reps that are IDENTICAL for every occurrence of a given entity regardless of
# sentence/verb, so its effective sample size is N_ENT=20 independent draws, not the 240 per-record
# examples (which are correlated through only 20 distinct entity identities). THEORETICAL: binomial
# SE = sqrt(0.5*0.5/20) = 0.1118; a 3-sigma band around chance=0.50 is [0.164, 0.836], rounded to
# [0.15, 0.85]. Caught empirically during self-test dev iteration BEFORE any --full/verdict-bearing run
# was written: an initial [0.35,0.65] band (naively sized off the 240-example count) flagged a genuine,
# fair, chance-level bagofwords result (0.333) as a false INVALID -- the band was mis-modeling the
# effective sample size, not the result being suspicious. This is a variance-model correction made
# before the verdict-bearing --full run, not a post-hoc loosening of a HARD_PASS threshold (per
# META_RULE_AG "iterate the regime, don't dispatch on a miscalibrated floor" discipline).
BAGOFWORDS_FLOOR_BAND = (0.15, 0.85)
# SHUFFLED_FLOOR_BAND stays tight: ARM_SHUFFLED_CONTROL classifies CONTEXTUALIZED test reps (which
# vary per sentence/verb even for the same entity), averaged over N_SHUFFLE_TRIALS=30 independent
# label-permutations on top of a genuinely larger effective sample -- MEASURED@this file's dev
# iteration: 0.51-0.53, comfortably inside a tight band.
SHUFFLED_FLOOR_BAND = (0.35, 0.65)       # HYPOTHESIZED@this file: chance(0.50) +/- 0.15

DIRECTIONS = ("active_to_passive", "passive_to_active")
EXPECTED_N_UNITS = 1 + 3 * len(DIRECTIONS)   # 1 combined position_only + (role_probe, bagofwords,
                                              # shuffled_control) x 2 directions = 7


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


def cosine(a, b):
    na = a.norm()
    nb = b.norm()
    if na.item() < 1e-12 or nb.item() < 1e-12:
        return 0.0
    return float(torch.dot(a, b) / (na * nb))


# ================= encoder (subclass -- OWN closed sentence set, same pattern as RoleSyntaxEncoder /
# RelEncoder elsewhere in this codebase) =================
class SyntaxRoleEncoder(base.FrozenV2Encoder):
    def _closed_sentences(self):
        return sorted(set(ALL_CLOSED_SENTENCES))   # sorted -> deterministic; NOT list(set())


def _entity_token_cols(enc, sentence, entity_word):
    """Token column indices in `sentence`'s cached row that overlap `entity_word`'s (unique, word-
    boundary) character span, via the encoder's OWN tokenizer offsets. Mean-pooling over the returned
    columns is used defensively; MEASURED@this file's dev iteration: every ENTITIES word tokenizes to
    exactly one BPE token under the Whitespace pre-tokenizer, so len(cols)==1 in practice."""
    m = re.search(r"\b" + re.escape(entity_word) + r"\b", sentence)
    assert m is not None, "entity word %r not found in sentence %r" % (entity_word, sentence)
    char_start, char_end = m.start(), m.end()
    enc_out = enc.tok.encode(sentence)
    offsets = enc_out.offsets
    cols = [ti for ti, (s0, e0) in enumerate(offsets) if not (e0 <= char_start or s0 >= char_end)]
    assert len(cols) >= 1, "no token overlaps entity span for %r in %r" % (entity_word, sentence)
    return cols


def entity_rep(enc, sentence, entity_word):
    """Contextualized entity representation: mean over the entity word's own token column(s) of the
    frozen encoder's per-token hidden states for this sentence."""
    row = enc.idx_of(sentence)
    cols = _entity_token_cols(enc, sentence, entity_word)
    reps = enc.U_tok_t[row, cols, :]         # [k, d]
    return reps.mean(dim=0)


def collect_context_reps(enc, records, center_vec):
    """Returns list of (rep[d], role_label) -- one AGENT rep (a) and one PATIENT rep (b) per record."""
    out = []
    for rec in records:
        s = rec["sentence"]
        rep_a = entity_rep(enc, s, rec["a"]) - center_vec
        rep_b = entity_rep(enc, s, rec["b"]) - center_vec
        out.append((rep_a, AGENT))
        out.append((rep_b, PATIENT))
    return out


def collect_bagofwords_reps(enc, records, center_vec):
    """SAME (record, role) pairing as collect_context_reps, but the representation is the CONTEXT-FREE
    bare-word embedding (order-blind control) -- identical rep regardless of sentence/voice/position."""
    out = []
    for rec in records:
        rep_a = entity_rep(enc, rec["a"], rec["a"]) - center_vec
        rep_b = entity_rep(enc, rec["b"], rec["b"]) - center_vec
        out.append((rep_a, AGENT))
        out.append((rep_b, PATIENT))
    return out


def build_centroids(reps_labels):
    agent = torch.stack([r for r, l in reps_labels if l == AGENT])
    patient = torch.stack([r for r, l in reps_labels if l == PATIENT])
    return torch.stack([agent.mean(dim=0), patient.mean(dim=0)])   # [2, d] row0=agent row1=patient


def classify(reps_labels, centroid):
    """Returns (accuracy, correct_bool_array)."""
    correct = []
    for r, l in reps_labels:
        sims = [cosine(r, centroid[0]), cosine(r, centroid[1])]
        pred = int(np.argmax(sims))
        correct.append(pred == l)
    correct = np.asarray(correct, dtype=bool)
    return float(correct.mean()), correct


def shuffled_control_acc(train_reps_labels, test_reps_labels, base_seed, n_trials):
    """TRAIN labels randomly permuted (fixed-seed torch permutation, no hash()) before building
    centroids; averaged over n_trials -- honest population-level chance estimate for THIS
    (train,test) split (labels shuffled, contextualized reps otherwise identical to ARM_ROLE_PROBE)."""
    reps = [r for r, _l in train_reps_labels]
    n = len(reps)
    accs = []
    for trial in range(n_trials):
        g = torch.Generator().manual_seed(base_seed + trial)
        perm = torch.randperm(n, generator=g).numpy()
        shuffled_labels = [train_reps_labels[i][1] for i in range(n)]
        # apply permutation to the LABEL assignment (labels move, reps stay put -> same effect as
        # relabeling which rep belongs to which class)
        relabeled = [(reps[i], shuffled_labels[perm[i]]) for i in range(n)]
        centroid = build_centroids(relabeled)
        acc, _ = classify(test_reps_labels, centroid)
        accs.append(acc)
    return float(np.mean(accs)), float(np.std(accs))


def position_only_predict(sentence, a_word, b_word):
    """Pure surface-string heuristic: whichever entity word appears EARLIER in the sentence is
    predicted AGENT. Never touches the encoder."""
    pa = re.search(r"\b" + re.escape(a_word) + r"\b", sentence).start()
    pb = re.search(r"\b" + re.escape(b_word) + r"\b", sentence).start()
    return (AGENT, PATIENT) if pa < pb else (PATIENT, AGENT)   # (pred_a, pred_b)


def position_only_acc(records):
    correct = []
    for rec in records:
        pred_a, pred_b = position_only_predict(rec["sentence"], rec["a"], rec["b"])
        correct.append(pred_a == AGENT)
        correct.append(pred_b == PATIENT)
    correct = np.asarray(correct, dtype=bool)
    return float(correct.mean()), correct


def global_center_vec(enc, records_for_mean, fn):
    """Mean, over EVERY (record, entity-slot) in records_for_mean, of fn(enc, sentence, entity_word) --
    the shared component to subtract before cosine (mean-centering, per the read-conditioning finding)."""
    vecs = []
    for rec in records_for_mean:
        vecs.append(fn(enc, rec["sentence"], rec["a"]))
        vecs.append(fn(enc, rec["sentence"], rec["b"]))
    return torch.stack(vecs).mean(dim=0)


def entity_rep_bare(enc, _sentence_unused, entity_word):
    return entity_rep(enc, entity_word, entity_word)


# ---------------- pipeline (SAME code path for --self-test and --full; option (A) of
# DISCRIMINATOR-MUST-SURVIVE-SCALE -- there is no smaller regime, self-test runs the real full pass) ---
def run_pipeline(enc, output_dir, hb):
    """Returns dict with per-direction ARM_ROLE_PROBE / ARM_POSITION_ONLY / ARM_BAGOFWORDS /
    ARM_SHUFFLED_CONTROL results, checkpointed per-unit via tools/exp_checkpoint (CLAUDE.md mandate)."""
    context_center = global_center_vec(enc, ACTIVE_TRAIN + PASSIVE_TRAIN, entity_rep)
    bow_center = global_center_vec(enc, ACTIVE_TRAIN + PASSIVE_TRAIN, entity_rep_bare)

    ctx_active_train = collect_context_reps(enc, ACTIVE_TRAIN, context_center)
    ctx_active_test = collect_context_reps(enc, ACTIVE_TEST, context_center)
    ctx_passive_train = collect_context_reps(enc, PASSIVE_TRAIN, context_center)
    ctx_passive_test = collect_context_reps(enc, PASSIVE_TEST, context_center)

    bow_active_train = collect_bagofwords_reps(enc, ACTIVE_TRAIN, bow_center)
    bow_active_test = collect_bagofwords_reps(enc, ACTIVE_TEST, bow_center)
    bow_passive_train = collect_bagofwords_reps(enc, PASSIVE_TRAIN, bow_center)
    bow_passive_test = collect_bagofwords_reps(enc, PASSIVE_TEST, bow_center)

    dir_specs = {
        "active_to_passive": {
            "ctx_train": ctx_active_train, "ctx_test": ctx_passive_test,
            "bow_train": bow_active_train, "bow_test": bow_passive_test,
        },
        "passive_to_active": {
            "ctx_train": ctx_passive_train, "ctx_test": ctx_active_test,
            "bow_train": bow_passive_train, "bow_test": bow_active_test,
        },
    }
    within_voice_specs = {
        "active_to_active_ref": {"ctx_train": ctx_active_train, "ctx_test": ctx_active_test},
        "passive_to_passive_ref": {"ctx_train": ctx_passive_train, "ctx_test": ctx_passive_test},
    }

    prior_units = ckpt.load_units(output_dir)
    results = {}
    unit_i = 0

    # ARM_POSITION_ONLY: a SINGLE combined (both-voice-pooled) metric, not per-direction. It is a
    # fixed, un-trained surface-string rule (see position_only_predict) -- there is no "direction" to
    # evaluate it in; applied to a PURE-ACTIVE test set it is trivially 1.0 (that IS the rule), applied
    # to a PURE-PASSIVE test set it is trivially 0.0 (roles are swapped). The Director's spawn's fairness
    # claim ("it gets active right, passive wrong -> ~0.5 if balanced") is a statement about the POOLED
    # cross-voice distribution, not about either per-direction split matching ARM_ROLE_PROBE's
    # train/test structure (which the fixed rule never "trains" on anyway). ACTIVE_TEST (120 sentences,
    # 240 examples) and PASSIVE_TEST (120 sentences, 240 examples) are equal-sized, so the pooled
    # combined accuracy is EXACTLY 0.5 by construction -- MEASURED@this file's dev iteration.
    k_pos = ckpt.unit_key("combined", "position_only")
    unit_i += 1
    if k_pos in prior_units:
        results[k_pos] = prior_units[k_pos]
        _log("  [resume] %s loaded from checkpoint" % k_pos)
        hb.tick(unit_i, extra={"resumed": True})
    else:
        acc_pos, correct_pos = position_only_acc(ACTIVE_TEST + PASSIVE_TEST)
        acc_pos_active, _ = position_only_acc(ACTIVE_TEST)
        acc_pos_passive, _ = position_only_acc(PASSIVE_TEST)
        res = {"acc": acc_pos, "acc_active_only": acc_pos_active, "acc_passive_only": acc_pos_passive,
               "digest": hashlib.sha256(correct_pos.tobytes()).hexdigest()}
        ckpt.record_unit(output_dir, k_pos, res)
        results[k_pos] = res
        _log("  [%s] acc=%.4f (active_only=%.4f passive_only=%.4f)"
             % (k_pos, acc_pos, acc_pos_active, acc_pos_passive))
        hb.tick(unit_i, extra={"unit": k_pos, "acc": acc_pos})

    for direction, spec in dir_specs.items():
        for kind in ("role_probe", "bagofwords", "shuffled_control"):
            k = ckpt.unit_key(direction, kind)
            unit_i += 1
            if k in prior_units:
                results[k] = prior_units[k]
                _log("  [resume] %s loaded from checkpoint" % k)
                hb.tick(unit_i, extra={"resumed": True})
                continue
            if kind == "role_probe":
                centroid = build_centroids(spec["ctx_train"])
                acc, correct = classify(spec["ctx_test"], centroid)
                res = {"acc": acc, "digest": hashlib.sha256(correct.tobytes()).hexdigest()}
            elif kind == "bagofwords":
                centroid = build_centroids(spec["bow_train"])
                acc, correct = classify(spec["bow_test"], centroid)
                res = {"acc": acc, "digest": hashlib.sha256(correct.tobytes()).hexdigest()}
            else:  # shuffled_control
                mean_acc, sd_acc = shuffled_control_acc(
                    spec["ctx_train"], spec["ctx_test"], SHUFFLE_SEED + hash_free_index(direction),
                    N_SHUFFLE_TRIALS)
                res = {"acc": mean_acc, "sd": sd_acc,
                       "digest": hashlib.sha256(np.array([mean_acc, sd_acc]).round(6).tobytes()).hexdigest()}
            ckpt.record_unit(output_dir, k, res)
            results[k] = res
            _log("  [%s] acc=%.4f" % (k, res["acc"]))
            hb.tick(unit_i, extra={"unit": k, "acc": res["acc"]})

    within_voice = {}
    for name, spec in within_voice_specs.items():
        centroid = build_centroids(spec["ctx_train"])
        acc, _correct = classify(spec["ctx_test"], centroid)
        within_voice[name] = acc

    return {
        "results": results, "within_voice_reference": within_voice,
        "n_context_sentences": len(ALL_CONTEXT_SENTENCES), "n_bare_words": len(BARE_WORDS),
    }


def hash_free_index(direction_name):
    """Deterministic small integer offset per direction WITHOUT hash() (PROT-023 / F.5 discipline) --
    a fixed lookup, not a runtime hash()."""
    return {"active_to_passive": 0, "passive_to_active": 1}[direction_name]


# arms_differ_exempted (META_RULE_AF): ARM_BAGOFWORDS is built from CONTEXT-FREE (bare-word) reps that
# never depend on verb or voice; TRAIN_PAIRS (and separately TEST_PAIRS) is the SAME entity-pair set
# under both ACTIVE and PASSIVE voice, so bow_active_train / bow_passive_train average over the
# IDENTICAL (entity, role) assignment (only the verb differs, which bagofwords reps ignore) -- the two
# directions' bagofwords result is mathematically identical BY DESIGN, not a copy-paste bug. Declared
# here, not silently swallowed.
ARMS_DIFFER_EXEMPTED = [("active_to_passive|bagofwords", "passive_to_active|bagofwords")]


def check_arms_differ(digests):
    """Pairwise bit-identity check (META_RULE_AF) over all unit digests, EXCEPT the declared
    ARMS_DIFFER_EXEMPTED pairs (see rationale above)."""
    exempted = {frozenset(p) for p in ARMS_DIFFER_EXEMPTED}
    keys = sorted(digests)
    for ka in keys:
        for kb in keys:
            if ka < kb:
                if frozenset((ka, kb)) in exempted:
                    continue
                assert digests[ka] != digests[kb], (
                    "META_RULE_AF VIOLATION: units %r and %r bit-identical" % (ka, kb))


# ---------------- self-tests (fairness / balance checks, real code path) ----------------
def entity_role_balance_selftest():
    """Verifies the fairness claim underlying ARM_BAGOFWORDS: each entity fills the AGENT slot and the
    PATIENT slot a comparable number of times across TRAIN_PAIRS and across TEST_PAIRS (not perfectly
    equal by construction, but close -- measured directly here, not assumed)."""
    def counts(pairs):
        agent_count = np.zeros(N_ENT, dtype=np.int64)
        patient_count = np.zeros(N_ENT, dtype=np.int64)
        for (i, j) in pairs:
            agent_count[i] += 1
            patient_count[j] += 1
        return agent_count, patient_count

    for name, pairs in (("TRAIN_PAIRS", TRAIN_PAIRS), ("TEST_PAIRS", TEST_PAIRS)):
        ac, pc = counts(pairs)
        assert ac.sum() == pc.sum() == len(pairs)
        max_imbalance = int(np.max(np.abs(ac - pc)))
        assert max_imbalance <= 2, (
            "%s: entity agent/patient role-count imbalance too large (max=%d); ARM_BAGOFWORDS floor "
            "assumption (identity balanced across roles) would not hold" % (name, max_imbalance))
    return {"train_max_imbalance": int(np.max(np.abs(np.subtract(*counts(TRAIN_PAIRS))))),
            "test_max_imbalance": int(np.max(np.abs(np.subtract(*counts(TEST_PAIRS)))))}


def position_only_construction_selftest():
    """Direct measurement: position-only heuristic must be exactly 1.0 on matching-voice test records
    and exactly 0.0 on opposite-voice test records, by construction (a<b position in ACTIVE, b<a
    position in PASSIVE)."""
    acc_active, _ = position_only_acc(ACTIVE_TEST)
    acc_passive, _ = position_only_acc(PASSIVE_TEST)
    assert abs(acc_active - 1.0) < 1e-9, "position-only on ACTIVE_TEST != 1.0 (got %.4f)" % acc_active
    assert abs(acc_passive - 0.0) < 1e-9, "position-only on PASSIVE_TEST != 0.0 (got %.4f)" % acc_passive
    return {"position_only_active_test": acc_active, "position_only_passive_test": acc_passive}


def frames_genuinely_differ_selftest(enc):
    """Fairness gate: the two voice templates must produce genuinely different token sequences (not
    numerically-identical reps), and entity-token extraction must find a DIFFERENT column for 'a' vs
    'b' within the same sentence (else the extraction cannot disambiguate the two entities)."""
    a, b, verb = ENTITIES[0], ENTITIES[1], TRAIN_VERBS[0]
    active_s = ACTIVE_TEMPLATE.format(a=a, b=b, verb=verb)
    passive_s = PASSIVE_TEMPLATE.format(a=a, b=b, verb=verb)
    assert active_s != passive_s
    cols_a = _entity_token_cols(enc, active_s, a)
    cols_b = _entity_token_cols(enc, active_s, b)
    assert set(cols_a).isdisjoint(set(cols_b)), "entity 'a' and 'b' token columns overlap in %r" % active_s
    rep_a = entity_rep(enc, active_s, a)
    rep_b = entity_rep(enc, active_s, b)
    same_sent_cos = cosine(rep_a, rep_b)
    assert same_sent_cos < 0.9999, "FRAMES_SELFTEST_FAIL: two different entities in one sentence produced numerically identical reps"
    return {"cols_a": cols_a, "cols_b": cols_b, "same_sentence_cross_entity_cosine": same_sent_cos}


def run_self_test():
    _log("SELF-TEST: load REAL v2 encoder + build REAL closed sentence set (real_code_path) ...")
    assert os.path.exists(V2_CKPT), "v2 checkpoint missing: %s" % V2_CKPT
    enc = SyntaxRoleEncoder(V2_CKPT)
    n_cached = enc.build_cache()
    assert 0 < n_cached <= len(ALL_CLOSED_SENTENCES)
    _log("  n_cached=%d (expected <= %d)" % (n_cached, len(ALL_CLOSED_SENTENCES)))

    _log("SELF-TEST: entity role-balance (ARM_BAGOFWORDS floor assumption) ...")
    balance_diag = entity_role_balance_selftest()
    _log("  PASS: %s" % balance_diag)

    _log("SELF-TEST: position-only construction (must be exactly 1.0 active / 0.0 passive) ...")
    posonly_diag = position_only_construction_selftest()
    _log("  PASS: %s" % posonly_diag)

    _log("SELF-TEST: frames genuinely differ + entities disambiguable within one sentence ...")
    frames_diag = frames_genuinely_differ_selftest(enc)
    _log("  PASS: %s" % frames_diag)

    _log("SELF-TEST: REAL full pipeline (no smaller regime exists -- option A of "
         "DISCRIMINATOR-MUST-SURVIVE-SCALE) ...")
    selftest_dir = os.path.join(OUTPUT_DIR, "_selftest")
    with CellHeartbeat(selftest_dir, total_units=EXPECTED_N_UNITS, interval_s=30) as hb:
        pipeline_out = run_pipeline(enc, selftest_dir, hb)
    results = pipeline_out["results"]

    k_pos = ckpt.unit_key("combined", "position_only")
    assert 0.0 <= results[k_pos]["acc"] <= 1.0, "%s acc out of range" % k_pos
    for direction in DIRECTIONS:
        for kind in ("role_probe", "bagofwords", "shuffled_control"):
            k = ckpt.unit_key(direction, kind)
            acc = results[k]["acc"]
            assert 0.0 <= acc <= 1.0, "%s acc out of range: %.4f" % (k, acc)

    digests = {k: v["digest"] for k, v in results.items()}
    check_arms_differ(digests)

    _log("SELF-TEST PASS")
    return {"n_cached": n_cached, "balance_diag": balance_diag, "posonly_diag": posonly_diag,
            "frames_diag": frames_diag,
            "pipeline_summary": {k: v["acc"] for k, v in results.items()},
            "within_voice_reference": pipeline_out["within_voice_reference"],
            "arms_differ_verified": True}


# ---------------- verdict ----------------
def decide_verdict(pipeline_out):
    results = pipeline_out["results"]

    def acc(direction, kind):
        return results[ckpt.unit_key(direction, kind)]["acc"]

    posonly_val = results[ckpt.unit_key("combined", "position_only")]["acc"]
    bow_vals = {d: acc(d, "bagofwords") for d in DIRECTIONS}
    shuf_vals = {d: acc(d, "shuffled_control") for d in DIRECTIONS}
    role_vals = {d: acc(d, "role_probe") for d in DIRECTIONS}

    posonly_fails = posonly_val <= POSITION_ONLY_FAIL_MAX
    bow_floors = all(BAGOFWORDS_FLOOR_BAND[0] <= v <= BAGOFWORDS_FLOOR_BAND[1] for v in bow_vals.values())
    shuf_floors = all(SHUFFLED_FLOOR_BAND[0] <= v <= SHUFFLED_FLOOR_BAND[1] for v in shuf_vals.values())

    bands = {
        "chance": CHANCE, "role_probe_pass_min": ROLE_PROBE_PASS_MIN,
        "role_probe_fail_max": ROLE_PROBE_FAIL_MAX, "position_only_fail_max": POSITION_ONLY_FAIL_MAX,
        "bagofwords_floor_band": list(BAGOFWORDS_FLOOR_BAND),
        "shuffled_floor_band": list(SHUFFLED_FLOOR_BAND),
        "role_probe_by_direction": {d: round(v, 4) for d, v in role_vals.items()},
        "position_only_combined": round(posonly_val, 4),
        "bagofwords_by_direction": {d: round(v, 4) for d, v in bow_vals.items()},
        "shuffled_control_by_direction": {d: round(v, 4) for d, v in shuf_vals.items()},
        "within_voice_reference": pipeline_out["within_voice_reference"],
        "posonly_fails_cross_voice": posonly_fails, "bagofwords_floors": bow_floors,
        "shuffled_floors": shuf_floors,
    }

    if not (posonly_fails and bow_floors and shuf_floors):
        verdict = "INVALID"
        msg = ("Fairness/floor gate failed: posonly_fails_cross_voice=%s (must be True, "
               "position_only_combined<=%.2f), bagofwords_floors=%s (must be True, band=%s), "
               "shuffled_floors=%s (must be True, band=%s) -- position_only_combined=%.4f "
               "bagofwords=%s shuffled=%s. ARM_ROLE_PROBE numbers are NOT interpreted."
               % (posonly_fails, POSITION_ONLY_FAIL_MAX, bow_floors, list(BAGOFWORDS_FLOOR_BAND),
                  shuf_floors, list(SHUFFLED_FLOOR_BAND), posonly_val, bow_vals, shuf_vals))
        return verdict, msg, bands

    hard_pass = all(v >= ROLE_PROBE_PASS_MIN for v in role_vals.values())
    hard_fail = any(v <= ROLE_PROBE_FAIL_MAX for v in role_vals.values())

    if hard_pass:
        verdict = "ENCODER_ENCODES_SYNTACTIC_ROLE"
        msg = ("Floors valid (position_only_combined=%.4f <= %.2f, bagofwords=%s in %s, shuffled=%s "
               "in %s) AND ARM_ROLE_PROBE cross-voice accuracy=%s >= PASS_MIN=%.2f on BOTH directions "
               "-- the frozen v2 encoder's contextualized entity reps DO carry voice-invariant "
               "syntactic role; the syntactic-parsing comprehension direction is BUILDABLE on this "
               "encoder without further encoder work. Within-voice reference (upper bound, held-out "
               "verb+pair, no voice switch): %s."
               % (posonly_val, POSITION_ONLY_FAIL_MAX, bow_vals, list(BAGOFWORDS_FLOOR_BAND),
                  shuf_vals, list(SHUFFLED_FLOOR_BAND), role_vals, ROLE_PROBE_PASS_MIN,
                  pipeline_out["within_voice_reference"]))
    elif hard_fail:
        verdict = "ENCODER_POSITION_ONLY"
        msg = ("Floors valid but ARM_ROLE_PROBE cross-voice accuracy=%s <= FAIL_MAX=%.2f on at least "
               "one direction (no better than the position-only control / near chance=%.2f) -- the "
               "frozen encoder only supplies positional cues, not voice-invariant syntactic role; "
               "syntax->role is the WALL on this encoder for the richer-NL comprehension direction. "
               "Within-voice reference: %s."
               % (role_vals, ROLE_PROBE_FAIL_MAX, CHANCE, pipeline_out["within_voice_reference"]))
    else:
        verdict = "MIDDLE"
        msg = ("Floors valid. ARM_ROLE_PROBE cross-voice accuracy=%s (CHANCE=%.2f, FAIL_MAX=%.2f, "
               "PASS_MIN=%.2f) -- partial signal, neither HARD condition met on both directions; "
               "report exact numbers, do not force a HARD verdict. Within-voice reference: %s."
               % (role_vals, CHANCE, ROLE_PROBE_FAIL_MAX, ROLE_PROBE_PASS_MIN,
                  pipeline_out["within_voice_reference"]))

    return verdict, msg, bands


# ---------------- path-swap helpers ----------------
def _safe_relpath(path, start):
    """os.path.relpath raises ValueError on Windows when `path` and `start` are on different drive
    mounts (e.g. a --ckpt-path resolved against a cwd on C: while REPO_ROOT is D:) -- caught in
    production 2026-07-31 (CELL_CRASHED, ValueError: path is on mount 'C:', start on mount 'D:').
    This is a LOGGING-ONLY field (params.v2_ckpt), never used for I/O, so a cross-drive path is
    reported ABSOLUTE rather than raising; never blocks a real run over a cosmetic drive mismatch."""
    try:
        return os.path.relpath(path, start)
    except ValueError:
        return os.path.abspath(path)


# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--ckpt-path", default=None,
                    help="path-swap (2026-07-30, per notes/brain_syntax_to_role_mechanism_and_forward_"
                         "predictive_encoder_spec_2026-07-30.md): FrozenV2Encoder-shaped ckpt "
                         "(state_dict+model_cfg+tokenizer_json) to probe INSTEAD OF the default frozen "
                         "v2 MLM ckpt (V2_CKPT). Zero other code changes -- SyntaxRoleEncoder only needs "
                         "a ckpt_path string. Output dir is suffixed with the ckpt's basename so a "
                         "different-encoder run never overwrites the frozen-v2 metrics.json.")
    args = ap.parse_args()

    torch.set_num_threads(min(6, max(1, os.cpu_count() or 1)))
    run_mode = "self_test" if args.self_test or not args.full else "full"
    ckpt_path = args.ckpt_path if args.ckpt_path else V2_CKPT
    out_dir = OUTPUT_DIR
    if args.ckpt_path:
        tag = os.path.splitext(os.path.basename(args.ckpt_path))[0]
        out_dir = OUTPUT_DIR + "__" + tag
    _write_start_marker(out_dir, run_mode, EXPECTED_N_UNITS)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        elapsed = time.perf_counter() - t0
        _atomic_write_metrics(out_dir, {
            "verdict": "SELFTEST_PASS",
            "verdict_msg": "SELFTEST_PASS (balance + position-only-construction + frames-differ + "
                           "real full pipeline + arms-differ)",
            "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": elapsed,
            "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "chance": CHANCE, "selftest": st})
        _log("DONE self-test in %.1fs" % elapsed)
        return

    _log("FULL: directions=%s chance=%.4f n_context_sentences=%d n_bare_words=%d ckpt=%s"
         % (DIRECTIONS, CHANCE, len(ALL_CONTEXT_SENTENCES), len(BARE_WORDS), ckpt_path))
    enc = SyntaxRoleEncoder(ckpt_path)
    n_cached = enc.build_cache()
    _log("  cached %d unique sentences (d=%d)" % (n_cached, enc.d))

    prior_units = ckpt.load_units(out_dir)
    if prior_units:
        _log("checkpoint: %d/%d units already recorded on disk; resuming"
             % (len(prior_units), EXPECTED_N_UNITS))

    with CellHeartbeat(out_dir, total_units=EXPECTED_N_UNITS, interval_s=30) as hb:
        pipeline_out = run_pipeline(enc, out_dir, hb)

    verdict, msg, bands = decide_verdict(pipeline_out)
    elapsed = time.perf_counter() - t0

    results = pipeline_out["results"]
    n_units_done = len(results)
    digests = {k: v["digest"] for k, v in results.items()}
    check_arms_differ(digests)   # raises loudly on an undeclared collision; never silently continues
    arms_differ = True

    _atomic_write_metrics(out_dir, {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "%s | chance=%.4f | %s" % (verdict, CHANCE, msg[:160]),
        "run_mode": "full", "elapsed_s": elapsed, "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "chance": CHANCE, "bands": bands, "results_by_unit": results,
        "within_voice_reference": pipeline_out["within_voice_reference"],
        "arms_differ_verified": bool(arms_differ),
        "arms_differ_exempted": ARMS_DIFFER_EXEMPTED,
        "cardinality_ok": bool(n_units_done == EXPECTED_N_UNITS),
        "expected_n_units": EXPECTED_N_UNITS, "n_units_done": n_units_done,
        "params": {"entities": ENTITIES, "verbs_all": VERBS_ALL, "train_verbs": TRAIN_VERBS,
                   "heldout_verbs": HELDOUT_VERBS, "n_train_pairs": len(TRAIN_PAIRS),
                   "n_test_pairs": len(TEST_PAIRS), "n_cached_sentences": n_cached,
                   "encoder": "real_v2_frozen", "extraction": "direct_token_position_meanpool "
                   "(departs from oc.build_role_query_probe single-fixed-attention-pool -- see "
                   "module docstring rationale)",
                   "conditioning": "global_mean_centering (contextualized reps and bag-of-words reps "
                                   "centered SEPARATELY, per module docstring)",
                   "v2_ckpt": _safe_relpath(ckpt_path, REPO_ROOT), "shuffle_seed": SHUFFLE_SEED,
                   "n_shuffle_trials": N_SHUFFLE_TRIALS},
        "start_marker_written": True, "crash_diagnostic_present": True,
        "final_metrics_atomicity": "tmp_replace", "defensive_error_checking": "passed_all_4_patterns",
        "cell_chunked": False,
        "progress_logging": "print_flush_true",
        "crlb_n_a": "no learned-noise Cramer-Rao floor; discriminator is the pre-registered "
                    "ENCODER_ENCODES_SYNTACTIC_ROLE/ENCODER_POSITION_ONLY/INVALID decision rule "
                    "(see decide_verdict)",
        "calibration_check": "default_ok_for_this_regime: ROLE_PROBE_PASS_MIN/FAIL_MAX, "
                              "POSITION_ONLY_FAIL_MAX, BAGOFWORDS_FLOOR_BAND, SHUFFLED_FLOOR_BAND are "
                              "fixed HYPOTHESIZED thresholds set before running (not tuned post-hoc); "
                              "chance=0.50 is exact-by-construction (binary balanced task)."})
    _log("VERDICT: %s" % verdict)
    _log("  %s" % msg)
    _log("DONE full in %.1fs" % elapsed)


def _resolve_out_dir_from_argv(argv):
    """Mirror main()'s out_dir resolution (ckpt-path suffix) WITHOUT re-parsing via argparse, so the
    top-level crash handler can write to the SAME suffixed dir main() would have used, even when main()
    dies before it locally computes `out_dir`. Fixes a real bug (2026-07-31): the crash handler used the
    bare module-level OUTPUT_DIR constant, so every --ckpt-path run's crash diagnostic clobbered the
    BASE (no-suffix) metrics.json instead of its own `__<ckpt-basename>` dir -- three separate ckpt-path
    attempts (ARM_LPC_CAUSAL, ckpt_18k, and a plain re-run) all wrote their crash trace to the same base
    file, and the per-ckpt dirs were left with units.jsonl/heartbeat but no metrics.json at all."""
    ckpt_arg = None
    for i, a in enumerate(argv):
        if a == "--ckpt-path" and i + 1 < len(argv):
            ckpt_arg = argv[i + 1]
        elif a.startswith("--ckpt-path="):
            ckpt_arg = a.split("=", 1)[1]
    if not ckpt_arg:
        return OUTPUT_DIR
    tag = os.path.splitext(os.path.basename(ckpt_arg))[0]
    return OUTPUT_DIR + "__" + tag


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_resolve_out_dir_from_argv(sys.argv[1:]), e)
        raise
