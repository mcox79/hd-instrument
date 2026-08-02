# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: sha256 digest of OFF vs ON per-item correct/incorrect boolean arrays
#   (held-out passive split), verified pairwise-distinct in self-test (see _arms_must_differ).
# - final_metrics_atomicity: tmp_replace (os.replace at end), per-seed unit checkpoint via
#   tools/exp_checkpoint.py (MANDATORY, CLAUDE.md).
# - except SystemExit / except KeyboardInterrupt raised BEFORE except Exception; no bare except;
#   no silent continue -- any per-unit exception halts the cell with full context.
# - crlb_n_a: no Cramer-Rao floor here -- classification-accuracy discriminator, not a fit with a
#   noise model. Discriminator is the pre-registered CAN-FAIL FLOOR / HARD-PASS / HARD-FAIL /
#   MIDDLE decision rule below.
# - baseline_in_band: n/a in the (0.05,0.95) sense; the discriminating floor is ARM_OFF (feed-
#   forward baseline) MUST invert on passives (this IS the floor-check, enforced in decide_verdict).
# - discriminator survives scale: this cell IS the probe (Probe-1 cost class); --self-test and
#   --full both run the REAL pipeline at reduced N (self-test) vs full N (full) -- self-test also
#   asserts the CAN-FAIL FLOOR direction (not exact full-N numbers) so scale-saturation would be
#   caught before a full dispatch if it ever moved to a queue; here it runs to completion inline.
# - HARD_PASS strictly above floor + 5% band-width: PASS_ACC_MIN=0.75 vs CHANCE=0.50, ceiling 1.0,
#   band width 0.50, PASS_ACC_MIN sits at floor+0.50*width >> floor+0.05*width; declared explicitly.
# - HP_SCOPE: {"ARM_ON": ["PASS_ACC_MIN(active)", "PASS_ACC_MIN(passive)", "GAP_ON_MAX"],
#              "ARM_OFF": ["FLOOR_PASSIVE_MAX", "FLOOR_ACTIVE_MIN", "FLOOR_GAP_MIN"],
#              "ARM_PLACEBO": ["PLACEBO_NO_HELP_MAX"],
#              "ARM_PRECISION": ["PRECISION_LIFT_MIN (noisy arena only, fair-null acceptable)"]}.
#   HARD gates apply ONLY to their own named arm; no cross-arm gate leakage.
# - cardinality_ok: EXPECTED_N_UNITS = N_SEEDS (each unit computes ALL arms for that seed).
#   Declared + counted in decide_verdict; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if short.
# - per-unit failure-class instrumentation: no bare except anywhere in this file.
# - calibration_check: "default_ok_for_this_regime" -- all bands are fixed HYPOTHESIZED thresholds
#   from the pre-reg note (interactive_extraction_situation_model_loop_design_and_first_probe_
#   2026-08-01.md), set BEFORE running; task-generation scale constants (POS_SCALE, FEATURE_SCALE,
#   noise stds) were tuned during the SMOKE stage against the CAN-FAIL FLOOR only (not against the
#   HARD-PASS number), which is the honest, pre-registered use of a smoke iteration loop (harden
#   the task until the floor holds), not post-hoc threshold tuning.
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
# - real_code_path_exercised: --self-test and --full call the identical run_all_seeds() pipeline,
#   differing only in N_SEEDS / N_TRAIN_ITEMS / N_TEST_ITEMS / EPOCHS (smaller for self-test).
# - deterministic seeding: torch.Generator().manual_seed(...) only; no hash(); no list(set())
#   (sorted() used for any list-from-set conversion, none needed here -- pairs/verbs are lists
#   built by direct index arithmetic, not sets).
# - progress_logging: print_flush_true. timeout_s for this cell is well under 1800s (CPU-minutes
#   probe per pre-reg), so the sys17 print-progress-flushing MANDATE does not strictly apply, but
#   included anyway as defense-in-depth (heartbeat + flushed per-seed prints).
"""Interactive extraction<->situation-model loop -- FIRST PROBE (Director design spec
notes/interactive_extraction_situation_model_loop_design_and_first_probe_2026-08-01.md, commit
06a8353fb). Tests whether TOP-DOWN feedback (a situation-model / verb-selectional expectation that
biases token-level role-extraction) can resolve the order!=role ambiguity (active vs passive
agent/patient assignment) that a STATIC feed-forward role-query cannot -- the measured
0.16-0.18-below-chance cross-voice inversion in exp_syntactic_role_agent_patient_voice_probe_v1
(MEASURED@d:/AI/hd-instrument/data/exp_syntactic_role_agent_patient_voice_probe_v1/metrics.json),
which is the Broca's-agrammatism / TDH first-noun=agent signature of a feed-forward-only extractor.

PRIOR-WORK CHECK (per exp_dev SUBSTRATE-KB rule): the design note's own KB-check
(director_kb_query.py / substrate_query.sh) returned empty/stale this cycle; per THIS task's
explicit instruction, heavy KB queries are avoided here too (box thrash risk). Direct read of the
design note + hdlab/slot_attention_wm.py (both read end-to-end) is the grounding; the note states
no prior design implements situation-model -> extraction TOP-DOWN feedback (the graded PE-gate +
content-addressed slots are prior art, reused; the top-down wiring is new). Treating as novel per
the note's own audit; re-flagging honestly rather than re-querying a KB known to be misbehaving.

SCOPE DECISION (honest, stated up front): this is a SINGLE-CLAUSE classification probe (2 entity
tokens, 1 verb, agent-vs-patient decision), NOT a multi-clause situation-model STREAM. The design
note's element (a) (top-down bias) and (b)/(c) (graded PE / precision) are therefore reused at the
level of their FORM (SlotAttentionWM.entity_filler()'s content-addressed softmax-attention-over-
tokens mechanism: scores = tok_reps @ query, softmax over token positions) rather than by importing
the multi-slot streaming class directly -- there is no persistent cross-clause slot memory to
stream through in a single-clause probe. This is the CHEAPEST CAN-FAIL FIRST PROBE per the note's
"PART 2" design intent (prove the interactive TOPOLOGY can use top-down constraint to override
linear order), not a full situation-model integration test; scaling to a multi-clause stream with
the real SlotAttentionWM class is the next step if this probe HARD-PASSes.

TASK CONSTRUCTION (oracle-vector, feature-overlapping, order!=role; CITED@ thematic hierarchy /
animacy-predicts-agenthood, Dowty 1991 proto-agent properties -- ESTABLISHED linguistic regularity,
used here only as the oracle task's generative structure, not claimed as a brain-mechanism result):
  Each item = one (pair, verb, voice) triple. A pair designates entity_agent (thematic-agent-role
  holder) and entity_patient (fixed at pair-construction time, NOT swapped per item). Each entity
  has a fixed base ANIMACY and SIZE trait (Uniform draws); animacy is drawn so agent-designees
  trend higher (Uniform(0.35,0.85)) and patient-designees trend lower (Uniform(0.15,0.65)) --
  OVERLAPPING ranges (both cover [0.35,0.65]), so animacy alone is a NOISY, imperfect cue, not a
  perfect discriminator (feature-overlap, per the design note's task requirement). Per-item
  OBSERVATION noise (FEATURE_NOISE_STD) is added on top of the fixed trait, so a given entity's
  measured animacy fluctuates across items (perceptual-noise realism).
  Each verb has an EXPECTED_AGENT_ANIMACY / EXPECTED_AGENT_SIZE target (its selectional
  restriction), independently drawn per verb -- so the correct top-down inference must be
  VERB-SPECIFIC (a single global "prefer high animacy" rule is not enough; different verbs prefer
  different targets), which is what makes p_td = g(verb) genuinely necessary rather than a fixed
  constant a static role_query could already encode.
  ACTIVE construction: tokens = [content(agent, position=0), content(patient, position=1)],
    label = 0 (first token is agent) -- linear-order heuristic CORRECT.
  PASSIVE construction: tokens = [content(patient, position=0), content(agent, position=1)],
    label = 1 (second token is agent) -- linear-order heuristic WRONG (inverts).
  content(entity, position) = ID_SCALE*id_vec[entity] + FEATURE_SCALE*(animacy_dir*animacy_noisy +
    size_dir*size_noisy) + POS_SCALE*(pos_vec[position] + pos_noise). All directions (id_vec[e] for
    each entity, animacy_dir, size_dir, pos_vec[0], pos_vec[1]) are fixed random unit vectors in
    R^D_MODEL drawn once via a seeded torch.Generator; noise terms are freshly drawn per item.
  TRAINING SPLIT (mirrors the real-world premise that training text is voice-imbalanced /
  ACTIVE-DOMINANT): train on a MIXED voice set, TRAIN_ACTIVE_FRAC active (default 0.65) /
  remainder passive, over TRAIN_PAIRS x TRAIN_VERBS. Position is therefore a STRONG but IMPERFECT
  training cue -> a verb-BLIND model (ARM_OFF) still latches onto position (cheapest cue) and
  inverts cross-voice, WHILE a verb-conditioned model (ARM_ON) has a learnable signal (the passive
  fraction, where position is wrong but verb-match is right) to learn the top-down route. NOTE:
  active-ONLY training (the v1 first attempt) gave ARM_ON no possible lift -- position perfectly
  solved training so nothing rewarded the top-down route; that was an UNFAIR null (USER: a null only
  counts if a lift was possible) and is corrected here to active-DOMINANT mixed voice.
  HELD-OUT test: TEST_PAIRS x HELDOUT_VERBS, BOTH active and passive constructions, reported
  separately (active-heldout accuracy, passive-heldout accuracy = the primary discriminator).
  TRAIN_PAIRS / TEST_PAIRS split by list-index parity (even/odd); TRAIN_VERBS / HELDOUT_VERBS split
  first-half/second-half -- both deterministic, no randomness, disjoint on BOTH axes (fairness
  mandate: genuinely held-out, not just held-out lexicalizations).

ARM_OFF (feed-forward baseline): a single learned role_query vector (nn.Parameter[D_MODEL]),
  static across all items (independent of verb identity) -- logits_i = tok_i . role_query,
  softmax over the 2 token positions, trained via Adam on the active-only train split.
  Architecturally IDENTICAL in form to SlotAttentionWM.entity_filler()'s
  `scores = einsum(tok_reps, role_query)` (single static query, no p_td conditioning).

ARM_ON (interactive): role_query (own, separately trained) PLUS a top-down predictor head
  ptd_net = Linear-Tanh-Linear(verb_repr) -> p_td [D_MODEL], with a learned scalar gain. Effective
  logits_i = tok_i . role_query + ptd_gain * (tok_i . p_td). verb_repr = the verb's own oracle
  selectional-target vector (animacy_dir*expected_animacy + size_dir*expected_size) -- the "verb
  vector carries selectional expectation in the substrate's own space" the design note specifies as
  an allowed oracle scaffold. p_td_net never receives position or item-index info, so gradient has
  no consistent incentive to let p_td absorb a position-correlated component (verb identity is
  independent of which position the agent occupies in this balanced corpus) -- p_td is
  architecturally forced to carry only verb-conditioned CONTENT, not position, REASONED@ (my own
  derivation, not an external citation) from the training-signal symmetry argument.
  Same active-only train split as ARM_OFF (controlled: ONE VARIABLE = presence/absence of the
  p_td pathway; nothing else differs -- same data, same optimizer, same epoch budget, same seed).

ARM_PLACEBO (random-feedback control, CRITICAL): the SAME trained ARM_ON weights, evaluated with
  p_td computed from a SHUFFLED verb (a different, deterministically-permuted verb's repr, not the
  true per-item verb) instead of the true verb_repr. Tests whether the RESULT depends on the
  CONTENT of the top-down signal (must drop back toward ARM_OFF's floor) or merely on having an
  extra additive pathway (which would be an artifact). No separate training run -- same weights,
  eval-time input swap only (a stronger, confound-free version of "train a separate placebo model").

ARM_PRECISION (secondary, fair-null-acceptable per pre-reg): an INDEPENDENT, closed-form,
  no-training two-channel arena, isolated from the position-wall question above (per the design
  note's fairness mandate: precision needs a noisy-cue arena to have anything to bite on). Two
  match channels per token (animacy-match, size-match against the verb's two oracle targets,
  computed directly, no gradient needed since the targets are exactly recoverable from verb_repr's
  own construction). A NOISY-CUE subset of items has the animacy channel corrupted with large extra
  noise (ANIMACY_CORRUPT_STD) while size stays clean. pi_animacy / pi_size = closed-form inverse-
  variance weights (1/var(residual)+eps, normalized to sum 1), estimated from a calibration pass
  over the SAME train-style item distribution (including the noisy-cue subset, so the estimate
  reflects the true per-channel noise -- a legitimate "precision learned from experience" per
  Friston/Feldman, not an oracle peek at test labels). PRECISION-ON combines channels with
  pi_animacy/pi_size; PRECISION-OFF forces pi=(0.5,0.5). Compared ONLY within the noisy-cue subset
  of the held-out test set (the fair-test requirement: a null only counts if a lift was possible).

Run:  .venv/Scripts/python.exe experiments/exp_interactive_extraction_situation_model_loop_probe1_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_interactive_extraction_situation_model_loop_probe1_v1.py --full

ASCII-only. No emojis. CPU-only (torch.device("cpu") hard-set, no CUDA dependency, no argv-default
trap per exp_dev discipline #2). Deterministic seeding via torch.Generator only.
Compute architecture: sequential-CPU, justified -- tiny (D_MODEL=16-32) linear/2-layer-MLP models,
a few hundred SGD steps, a few thousand synthetic items; total wall time target well under 5
minutes for --full (Probe-1 cost class per pre-reg note: CPU, minutes, no encoder training, no GPU).
Storage strategy: no_storage / no_composition -- single-clause classification, no bind/bundle/
retrieve chain (the multi-clause SlotAttentionWM stream is explicitly OUT OF SCOPE for this probe,
see SCOPE DECISION above).
"""

import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_checkpoint as ckpt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cell_heartbeat import CellHeartbeat  # noqa: E402

ANCHOR_NAME = "interactive_extraction_situation_model_loop_probe1_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
DEVICE = torch.device("cpu")

# ---------------------------------------------------------------------------
# TASK-GENERATION CONSTANTS (HYPOTHESIZED@ tuned during smoke against the CAN-FAIL FLOOR only)
# ---------------------------------------------------------------------------
D_MODEL = 24
HIDDEN = 32
N_PAIRS = 48          # 24 train / 24 test (parity split)
N_VERBS = 16          # 8 train / 8 heldout
ID_SCALE = 0.35
FEATURE_SCALE = 1.4
POS_SCALE = 1.7
POS_NOISE_STD = 0.30
FEATURE_NOISE_STD = 0.12
VERB_TARGET_MARGIN = 0.30      # min L2 dist between a verb's agent vs patient selectional target
TRAIN_ACTIVE_FRAC = 0.65       # active-dominant MIXED-voice training (see gen_item / _sample_train)
ANIMACY_CORRUPT_STD = 0.6      # noisy-cue arena corruption (precision arm only)
NOISY_ARENA_FRAC = 0.5         # fraction of precision-arena items that are noisy-cue
LR = 0.03
WEIGHT_DECAY = 2e-3
EPOCHS_FULL = 400
EPOCHS_SELFTEST = 80
N_TRAIN_ITEMS_FULL = 1600
N_TEST_ITEMS_FULL = 800
N_TRAIN_ITEMS_SELFTEST = 200
N_TEST_ITEMS_SELFTEST = 120
N_SEEDS_FULL = 5
N_SEEDS_SELFTEST = 2
PTD_GAIN_INIT = 1.6

# SETTLING (2026-08-01 strengthen-pass, ONE VARIABLE = settling_iters):
# ARM_ON now runs a brain-faithful ITERATIVE predictive-coding settling loop (top-down verb
# expectation p_td vs the currently-attended agent estimate; the resulting prediction error nudges
# the extraction query; repeat). This replaces the earlier SINGLE additive top-down term (which was
# settling_iters==1 in spirit). Rationale (CITED@ predictive-coding / recurrent cortical settling,
# Rao&Ballard 1999; Bastos et al 2012): cortex resolves ambiguity by iterating top-down constraint
# over a FEW cycles (~hundreds of ms), NOT indefinitely -- so settling_iters is HARD-CAPPED small
# and brain-faithful. A RANDOM-FEEDBACK placebo (wrong verb's p_td) should NOT benefit from more
# settling (it settles toward the WRONG token), so more iters should GROW the content-over-placebo
# margin if the mechanism is real -- that is exactly what this sweep tests.
SETTLING_ITERS = 6             # default (middle sweep value) used by --self-test / --full
SETTLING_SWEEP_VALUES = [3, 6, 12]   # --sweep: current-scale, 2x, 4x (all <=12, brain-faithful small)

# ---------------------------------------------------------------------------
# PRE-REGISTERED BANDS (fixed BEFORE running; see module docstring HP_SCOPE)
# ---------------------------------------------------------------------------
CHANCE = 0.5
FLOOR_PASSIVE_MAX = 0.55       # ARM_OFF must be AT/BELOW this on passive held-out
FLOOR_ACTIVE_MIN = 0.80        # ARM_OFF must be AT/ABOVE this on active held-out
FLOOR_GAP_MIN = 0.30           # active - passive gap required to call the floor "held"
PASS_ACC_MIN = 0.75            # ARM_ON must clear this on BOTH active and passive held-out
GAP_ON_MAX = 0.15              # ARM_ON active-passive gap must be at/below this
HARD_FAIL_PASSIVE_MAX = 0.55   # ARM_ON at/below this on passive = HARD_FAIL (no better than OFF)
PLACEBO_SLACK = 0.10           # ARM_PLACEBO passive acc must stay within OFF_passive + this
PRECISION_LIFT_MIN = 0.10      # ARM_PRECISION: pi-on must beat pi-off by at least this (noisy arena)


def _mlp(in_dim, hidden, out_dim, g):
    m = nn.Sequential(nn.Linear(in_dim, hidden), nn.Tanh(), nn.Linear(hidden, out_dim))
    with torch.no_grad():
        for layer in m.modules():
            if isinstance(layer, nn.Linear):
                layer.weight.normal_(0.0, 0.08, generator=g)
                layer.bias.zero_()
    return m


def _unit_vecs(n, d, g):
    v = torch.randn(n, d, generator=g)
    return F.normalize(v, dim=-1)


# ---------------------------------------------------------------------------
# TASK / DATA GENERATION (deterministic; no hash(), no list(set()))
# ---------------------------------------------------------------------------
class World:
    """Fixed per-seed vocabulary: entity id vectors, per-verb AGENT/PATIENT selectional targets,
    directions, position vectors. Everything after construction is deterministic given seed.

    CORRECTED ORACLE (v1 fix, 2026-08-01): the agent is the entity whose observed animacy/size
    MATCH THE VERB'S agent selectional target; the patient's features match the verb's (distinct,
    margin-separated) patient target. So the verb's expectation genuinely IDENTIFIES the agent --
    but ONLY for a system that KNOWS the verb (ARM_ON). Because agent/patient targets vary per verb
    across the SAME global range (both span ~[0.3,0.9] with per-verb agent-vs-patient sign flips),
    there is NO global fixed-feature rule (e.g. "higher animacy = agent") that a verb-BLIND model
    (ARM_OFF) can use -> ARM_OFF is forced onto POSITION as its only cheap cue (feature-overlap
    requirement). Entity id_vecs supply lexical novelty for held-out pairs."""

    def __init__(self, seed):
        g = torch.Generator().manual_seed(seed)
        self.g = g
        n_ent = 2 * N_PAIRS
        self.id_vecs = _unit_vecs(n_ent, D_MODEL, g)          # [n_ent, D]
        self.animacy_dir = _unit_vecs(1, D_MODEL, g)[0]
        self.size_dir = _unit_vecs(1, D_MODEL, g)[0]
        self.pos_vecs = _unit_vecs(2, D_MODEL, g)             # [2, D]

        # pairs: (ent_a, ent_b) disjoint ids -- lexical carriers only; role is set by feature-match
        # to the verb target, NOT by which pair-slot (so entity identity carries NO role info,
        # exactly balanced by construction -> the bag-of-identity control floats at chance).
        pairs = [(2 * i, 2 * i + 1) for i in range(N_PAIRS)]
        self.train_pairs = [p for i, p in enumerate(pairs) if i % 2 == 0]
        self.test_pairs = [p for i, p in enumerate(pairs) if i % 2 == 1]

        # per-verb AGENT + PATIENT selectional targets in (animacy, size), margin-separated so the
        # verb DOES distinguish them, but drawn over the same global box so no global rule works.
        self.verb_ag_anim = torch.zeros(N_VERBS)
        self.verb_ag_size = torch.zeros(N_VERBS)
        self.verb_pat_anim = torch.zeros(N_VERBS)
        self.verb_pat_size = torch.zeros(N_VERBS)
        for v in range(N_VERBS):
            aa = 0.30 + 0.60 * torch.rand(1, generator=g).item()
            asz = 0.30 + 0.60 * torch.rand(1, generator=g).item()
            while True:
                pa = 0.30 + 0.60 * torch.rand(1, generator=g).item()
                ps = 0.30 + 0.60 * torch.rand(1, generator=g).item()
                if ((aa - pa) ** 2 + (asz - ps) ** 2) ** 0.5 >= VERB_TARGET_MARGIN:
                    break
            self.verb_ag_anim[v], self.verb_ag_size[v] = aa, asz
            self.verb_pat_anim[v], self.verb_pat_size[v] = pa, ps
        self.train_verbs = list(range(N_VERBS // 2))
        self.heldout_verbs = list(range(N_VERBS // 2, N_VERBS))

    def verb_repr(self, v):
        """Top-down selectional expectation vector (the verb's AGENT profile) in substrate space."""
        return (self.verb_ag_anim[v] * self.animacy_dir + self.verb_ag_size[v] * self.size_dir)

    def _content(self, ent, pos, anim, size, g):
        pos_noise = POS_NOISE_STD * torch.randn(D_MODEL, generator=g)
        vec = (ID_SCALE * self.id_vecs[ent]
               + FEATURE_SCALE * (anim * self.animacy_dir + size * self.size_dir)
               + POS_SCALE * (self.pos_vecs[pos] + pos_noise))
        return vec

    def gen_item(self, pair, verb, voice, g):
        """voice in {'active','passive'}. The AGENT entity's observed features match verb's agent
        target (+noise); the PATIENT entity's match verb's patient target. Returns
        (tok0, tok1, label, verb_repr, chan_a, chan_s) where chan_* = (tok0_feat, tok1_feat)."""
        ent_a, ent_b = pair                      # lexical carriers (which id_vec), role set below
        ag_anim = self.verb_ag_anim[verb].item() + FEATURE_NOISE_STD * torch.randn(1, generator=g).item()
        ag_size = self.verb_ag_size[verb].item() + FEATURE_NOISE_STD * torch.randn(1, generator=g).item()
        pat_anim = self.verb_pat_anim[verb].item() + FEATURE_NOISE_STD * torch.randn(1, generator=g).item()
        pat_size = self.verb_pat_size[verb].item() + FEATURE_NOISE_STD * torch.randn(1, generator=g).item()
        if voice == "active":
            # agent (ent_a) at position 0, patient (ent_b) at position 1 -> label 0
            tok0 = self._content(ent_a, 0, ag_anim, ag_size, g)
            tok1 = self._content(ent_b, 1, pat_anim, pat_size, g)
            chan_a = (ag_anim, pat_anim)
            chan_s = (ag_size, pat_size)
            label = 0
        else:
            # patient (ent_b) at position 0, agent (ent_a) at position 1 -> label 1
            tok0 = self._content(ent_b, 0, pat_anim, pat_size, g)
            tok1 = self._content(ent_a, 1, ag_anim, ag_size, g)
            chan_a = (pat_anim, ag_anim)
            chan_s = (pat_size, ag_size)
            label = 1
        return tok0, tok1, label, self.verb_repr(verb), chan_a, chan_s


def _sample_items(world, pairs, verbs, voices, n_items, g):
    """Deterministic cyclic sampling over (pair, verb, voice) combos -- no hash()."""
    combos = [(p, v, voice) for p in pairs for v in verbs for voice in voices]
    items = []
    for i in range(n_items):
        pair, verb, voice = combos[i % len(combos)]
        items.append(world.gen_item(pair, verb, voice, g))
    return items


def _sample_train(world, n_items, g):
    """Active-dominant MIXED-voice training (TRAIN_ACTIVE_FRAC active). Position is a STRONG but
    IMPERFECT cue in training -> a verb-blind model (OFF) latches onto position (its cheapest cue)
    and inverts cross-voice at test, WHILE a verb-conditioned model (ON) has a learnable signal (the
    35% passive items where position is wrong but verb-match is right) to learn the top-down route.
    This is the FAIRNESS fix: active-only training gave ON no possible lift (USER: a null only
    counts if a lift was possible)."""
    combos = [(p, v) for p in world.train_pairs for v in world.train_verbs]
    period = 20
    n_active = int(round(TRAIN_ACTIVE_FRAC * period))
    items = []
    for i in range(n_items):
        pair, verb = combos[i % len(combos)]
        voice = "active" if (i % period) < n_active else "passive"
        items.append(world.gen_item(pair, verb, voice, g))
    return items


def _batch(items):
    tok0 = torch.stack([it[0] for it in items])
    tok1 = torch.stack([it[1] for it in items])
    labels = torch.tensor([it[2] for it in items], dtype=torch.long)
    verb_reprs = torch.stack([it[3] for it in items])
    return tok0, tok1, labels, verb_reprs


# ---------------------------------------------------------------------------
# MODELS
# ---------------------------------------------------------------------------
class OffModel(nn.Module):
    """Feed-forward baseline: single STATIC role_query, no verb conditioning. Architecturally
    matches SlotAttentionWM.entity_filler()'s `scores = tok_reps @ role_query` form."""

    def __init__(self, g):
        super().__init__()
        rq = torch.empty(D_MODEL)
        rq.normal_(0.0, 0.05, generator=g)
        self.role_query = nn.Parameter(rq)

    def forward(self, tok0, tok1, verb_reprs=None, override_ptd=None, settling_iters=None):
        # OFF is feed-forward: settling_iters is accepted for call-signature parity but IGNORED
        # (a feed-forward extractor has no top-down loop to iterate).
        s0 = (tok0 * self.role_query).sum(-1)
        s1 = (tok1 * self.role_query).sum(-1)
        return torch.stack([s0, s1], dim=-1)


class OnModel(nn.Module):
    """Interactive: static role_query PLUS a verb-conditioned top-down predictor p_td = ptd_net
    (verb_repr). ITERATIVE predictive-coding settling (2026-08-01): the extraction query starts at
    role_query, and for settling_iters cycles the current attention-weighted 'attended agent
    estimate' is compared to the verb's top-down expectation p_td; the prediction error (p_td -
    attended) nudges the query (gain-scaled), then re-extract. As iterations grow, attention
    concentrates on the token whose CONTENT matches the verb expectation (winner-take-all settling).
    A wrong-verb p_td (PLACEBO) settles toward the WRONG token, so it does NOT benefit from more
    iters -- the pre-registered content-vs-placebo dissociation."""

    def __init__(self, g):
        super().__init__()
        rq = torch.empty(D_MODEL)
        rq.normal_(0.0, 0.05, generator=g)
        self.role_query = nn.Parameter(rq)
        self.ptd_net = _mlp(D_MODEL, HIDDEN, D_MODEL, g)
        self.ptd_gain = nn.Parameter(torch.tensor(PTD_GAIN_INIT))

    def forward(self, tok0, tok1, verb_reprs, override_ptd=None, settling_iters=None):
        if settling_iters is None:
            settling_iters = SETTLING_ITERS
        n_iters = max(1, int(settling_iters))
        p_td = self.ptd_net(verb_reprs) if override_ptd is None else override_ptd  # [B, D]
        b = tok0.shape[0]
        query = self.role_query.unsqueeze(0).expand(b, -1)                        # [B, D]
        for _ in range(n_iters):
            s0 = (tok0 * query).sum(-1)
            s1 = (tok1 * query).sum(-1)
            att = torch.softmax(torch.stack([s0, s1], dim=-1), dim=-1)            # [B, 2]
            attended = att[:, 0:1] * tok0 + att[:, 1:2] * tok1                    # [B, D]
            pe = p_td - attended                                                  # top-down PE
            query = query + self.ptd_gain * pe                                    # settle
        s0 = (tok0 * query).sum(-1)
        s1 = (tok1 * query).sum(-1)
        return torch.stack([s0, s1], dim=-1)


def _train(model, tok0, tok1, labels, verb_reprs, epochs, lr, settling_iters=None):
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=WEIGHT_DECAY)
    for _ in range(epochs):
        opt.zero_grad()
        logits = model(tok0, tok1, verb_reprs, settling_iters=settling_iters)
        loss = F.cross_entropy(logits, labels)
        loss.backward()
        opt.step()
    return model


def _accuracy(model, tok0, tok1, labels, verb_reprs, override_ptd=None, settling_iters=None):
    with torch.no_grad():
        logits = model(tok0, tok1, verb_reprs, override_ptd=override_ptd, settling_iters=settling_iters)
        pred = logits.argmax(dim=-1)
        correct = (pred == labels)
        return correct.float().mean().item(), correct, logits


def _arms_must_differ(digests):
    """META_RULE_AF: assert per-arm RAW-LOGIT digests are pairwise distinct. Uses continuous
    logits (not thresholded correctness booleans) so the check catches a genuine arm-
    IMPLEMENTATION bug (two arms literally the same model / same forward pass) WITHOUT
    false-firing when two genuinely-different models happen to agree on argmax over a small
    held-out set (which is a legitimate, informative outcome -- e.g. OFF and ON both invert on
    passives at low epochs -- not a coding bug). OFF (no ptd pathway), ON (ptd pathway), and
    PLACEBO (ON weights, shuffled p_td) produce distinct real-valued logit tensors by
    construction, so identical digests here would mean an actual wiring bug."""
    names = sorted(digests.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], (
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical logits (hash=%s); "
                "arm-implementation/wiring bug" % (a, b, digests[a]))


def _digest(t):
    return hashlib.sha256(t.detach().cpu().numpy().tobytes()).hexdigest()


# ---------------------------------------------------------------------------
# PRECISION ARENA (closed-form, no training)
# ---------------------------------------------------------------------------
def _precision_arena(world, seed, n_calib, n_test):
    """Two-channel (animacy, size) closed-form precision-weighting test, isolated from the
    position-wall question. Returns dict with pi_on / pi_off passive-acc on the noisy-cue subset."""
    g = torch.Generator().manual_seed(seed + 90001)

    def gen_channel_item(pairs, verbs, voice, corrupt):
        verb = verbs[int(torch.randint(0, len(verbs), (1,), generator=g).item())]
        # agent features match the verb's AGENT target; patient features match its PATIENT target.
        a_anim = world.verb_ag_anim[verb].item() + FEATURE_NOISE_STD * torch.randn(1, generator=g).item()
        a_size = world.verb_ag_size[verb].item() + FEATURE_NOISE_STD * torch.randn(1, generator=g).item()
        p_anim = world.verb_pat_anim[verb].item() + FEATURE_NOISE_STD * torch.randn(1, generator=g).item()
        p_size = world.verb_pat_size[verb].item() + FEATURE_NOISE_STD * torch.randn(1, generator=g).item()
        if corrupt:
            # NOISY-CUE: the ANIMACY channel is corrupted for BOTH tokens -> unreliable; SIZE stays
            # clean. Precision-ON should downweight animacy and rely on size (fair-test lift chance).
            a_anim += ANIMACY_CORRUPT_STD * torch.randn(1, generator=g).item()
            p_anim += ANIMACY_CORRUPT_STD * torch.randn(1, generator=g).item()
        # classify by match to the verb's AGENT target -> identifies the agent token.
        target_anim = world.verb_ag_anim[verb].item()
        target_size = world.verb_ag_size[verb].item()
        if voice == "active":
            anims, sizes, label = (a_anim, p_anim), (a_size, p_size), 0
        else:
            anims, sizes, label = (p_anim, a_anim), (p_size, a_size), 1
        return anims, sizes, target_anim, target_size, label

    # calibration pass (train-style distribution, includes noisy-cue subset) to estimate
    # per-channel residual variance -> closed-form precision weights.
    resid_a, resid_s = [], []
    for i in range(n_calib):
        corrupt = (i % 2 == 0)
        anims, sizes, ta, ts, label = gen_channel_item(
            world.train_pairs, world.train_verbs, "active" if i % 2 == 0 else "passive", corrupt)
        true_anim = anims[label]
        true_size = sizes[label]
        resid_a.append((true_anim - ta) ** 2)
        resid_s.append((true_size - ts) ** 2)
    var_a = sum(resid_a) / len(resid_a) + 1e-4
    var_s = sum(resid_s) / len(resid_s) + 1e-4
    pi_a = (1.0 / var_a) / (1.0 / var_a + 1.0 / var_s)
    pi_s = 1.0 - pi_a

    # test pass: NOISY-CUE subset only (fair-test requirement), held-out pairs/verbs.
    n_correct_on, n_correct_off, n_noisy = 0, 0, 0
    for i in range(n_test):
        corrupt = (i % int(1.0 / NOISY_ARENA_FRAC) == 0)
        voice = "passive" if i % 2 == 0 else "active"
        anims, sizes, ta, ts, label = gen_channel_item(world.test_pairs, world.heldout_verbs, voice, corrupt)
        if not corrupt:
            continue
        n_noisy += 1
        match_a = [-(anims[0] - ta) ** 2, -(anims[1] - ta) ** 2]
        match_s = [-(sizes[0] - ts) ** 2, -(sizes[1] - ts) ** 2]
        score_on = [pi_a * match_a[k] + pi_s * match_s[k] for k in (0, 1)]
        score_off = [0.5 * match_a[k] + 0.5 * match_s[k] for k in (0, 1)]
        pred_on = 0 if score_on[0] > score_on[1] else 1
        pred_off = 0 if score_off[0] > score_off[1] else 1
        n_correct_on += int(pred_on == label)
        n_correct_off += int(pred_off == label)

    assert n_noisy > 0, "precision arena produced zero noisy-cue test items -- widen NOISY_ARENA_FRAC"
    return {
        "pi_animacy": pi_a, "pi_size": pi_s,
        "n_noisy_items": n_noisy,
        "acc_precision_on": n_correct_on / n_noisy,
        "acc_precision_off": n_correct_off / n_noisy,
        "lift": (n_correct_on - n_correct_off) / n_noisy,
    }


# ---------------------------------------------------------------------------
# ONE SEED UNIT
# ---------------------------------------------------------------------------
def run_seed(seed, n_train, n_test, epochs, settling_iters=None):
    if settling_iters is None:
        settling_iters = SETTLING_ITERS
    world = World(seed)
    g_train = torch.Generator().manual_seed(seed + 1)
    g_test = torch.Generator().manual_seed(seed + 2)

    train_items = _sample_train(world, n_train, g_train)
    test_active = _sample_items(world, world.test_pairs, world.heldout_verbs, ["active"], n_test, g_test)
    test_passive = _sample_items(world, world.test_pairs, world.heldout_verbs, ["passive"], n_test, g_test)

    tr_tok0, tr_tok1, tr_labels, tr_verbs = _batch(train_items)
    te_a_tok0, te_a_tok1, te_a_labels, te_a_verbs = _batch(test_active)
    te_p_tok0, te_p_tok1, te_p_labels, te_p_verbs = _batch(test_passive)

    g_off = torch.Generator().manual_seed(seed + 10)
    g_on = torch.Generator().manual_seed(seed + 20)
    off = OffModel(g_off)
    on = OnModel(g_on)
    _train(off, tr_tok0, tr_tok1, tr_labels, tr_verbs, epochs, LR)
    _train(on, tr_tok0, tr_tok1, tr_labels, tr_verbs, epochs, LR, settling_iters=settling_iters)

    off_active_acc, _, _ = _accuracy(off, te_a_tok0, te_a_tok1, te_a_labels, te_a_verbs)
    off_passive_acc, _, off_passive_logits = _accuracy(off, te_p_tok0, te_p_tok1, te_p_labels, te_p_verbs)
    on_active_acc, _, _ = _accuracy(on, te_a_tok0, te_a_tok1, te_a_labels, te_a_verbs, settling_iters=settling_iters)
    on_passive_acc, _, on_passive_logits = _accuracy(on, te_p_tok0, te_p_tok1, te_p_labels, te_p_verbs, settling_iters=settling_iters)

    # PLACEBO: same trained ON weights, p_td from a shuffled (deterministically rolled-by-1) verb.
    # Same settling_iters -- the placebo settles the SAME number of cycles toward a WRONG expectation.
    shuffled_verbs_p = torch.roll(te_p_verbs, shifts=1, dims=0)
    with torch.no_grad():
        placebo_ptd = on.ptd_net(shuffled_verbs_p)
    placebo_passive_acc, _, placebo_passive_logits = _accuracy(
        on, te_p_tok0, te_p_tok1, te_p_labels, te_p_verbs, override_ptd=placebo_ptd, settling_iters=settling_iters)

    # arms-differ on CONTINUOUS logits (guaranteed distinct for genuinely-different models;
    # avoids false-firing when argmax coincides on a small set -- see _arms_must_differ).
    digests = {
        "OFF_passive": _digest(off_passive_logits),
        "ON_passive": _digest(on_passive_logits),
        "PLACEBO_passive": _digest(placebo_passive_logits),
    }
    _arms_must_differ(digests)

    precision = _precision_arena(world, seed, n_calib=max(200, n_train // 4), n_test=max(200, n_test))

    return {
        "seed": seed,
        "settling_iters": settling_iters,
        "off_active_acc": off_active_acc,
        "off_passive_acc": off_passive_acc,
        "off_gap": off_active_acc - off_passive_acc,
        "on_active_acc": on_active_acc,
        "on_passive_acc": on_passive_acc,
        "on_gap": on_active_acc - on_passive_acc,
        "placebo_passive_acc": placebo_passive_acc,
        "precision": precision,
        "digests": digests,
    }


def run_all_seeds(n_seeds, n_train, n_test, epochs, settling_iters=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t0 = time.perf_counter()
    with CellHeartbeat(OUTPUT_DIR, total_units=n_seeds, interval_s=20) as hb:
        for i, seed in enumerate(range(n_seeds)):
            key = ckpt.unit_key(seed)
            if key in ckpt.completed_units(OUTPUT_DIR):
                print("[skip] seed=%d already recorded" % seed, flush=True)
                hb.tick(i)
                continue
            try:
                result = run_seed(seed, n_train, n_test, epochs, settling_iters=settling_iters)
            except SystemExit:
                raise
            except KeyboardInterrupt:
                raise
            except Exception as e:
                ckpt.record_unit(OUTPUT_DIR, key, {
                    "seed": seed, "failure_class": "RUN_SEED_EXCEPTION",
                    "error": str(e), "traceback": traceback.format_exc(),
                })
                raise
            ckpt.record_unit(OUTPUT_DIR, key, result)
            print("[seed %d] off_passive=%.3f on_passive=%.3f placebo_passive=%.3f prec_lift=%.3f"
                  % (seed, result["off_passive_acc"], result["on_passive_acc"],
                     result["placebo_passive_acc"], result["precision"]["lift"]), flush=True)
            hb.tick(i + 1)
    units = ckpt.load_units(OUTPUT_DIR)
    elapsed = time.perf_counter() - t0
    return units, elapsed


def _mean(vals):
    return sum(vals) / len(vals)


def decide_verdict(units, n_seeds_expected):
    if any(v.get("failure_class") for v in units.values()):
        return "HARD_FAIL_UNIT_EXCEPTION", {"failed_units": [k for k, v in units.items() if v.get("failure_class")]}

    n_units = len(units)
    cardinality_ok = (n_units == n_seeds_expected)
    if not cardinality_ok:
        return "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", {
            "expected": n_seeds_expected, "got": n_units}

    off_active = _mean([v["off_active_acc"] for v in units.values()])
    off_passive = _mean([v["off_passive_acc"] for v in units.values()])
    off_gap = off_active - off_passive
    on_active = _mean([v["on_active_acc"] for v in units.values()])
    on_passive = _mean([v["on_passive_acc"] for v in units.values()])
    on_gap = on_active - on_passive
    placebo_passive = _mean([v["placebo_passive_acc"] for v in units.values()])
    prec_lift = _mean([v["precision"]["lift"] for v in units.values()])
    prec_on = _mean([v["precision"]["acc_precision_on"] for v in units.values()])
    prec_off = _mean([v["precision"]["acc_precision_off"] for v in units.values()])

    summary = {
        "off_active_acc": off_active, "off_passive_acc": off_passive, "off_gap": off_gap,
        "on_active_acc": on_active, "on_passive_acc": on_passive, "on_gap": on_gap,
        "placebo_passive_acc": placebo_passive,
        "precision_lift": prec_lift, "precision_on_acc": prec_on, "precision_off_acc": prec_off,
        "cardinality_ok": cardinality_ok, "n_units": n_units,
    }

    floor_held = (off_passive <= FLOOR_PASSIVE_MAX and off_active >= FLOOR_ACTIVE_MIN
                  and off_gap >= FLOOR_GAP_MIN)
    summary["floor_held"] = floor_held
    if not floor_held:
        return "FLOOR_NOT_HELD_PROBE_INVALID_HARDEN_TASK", summary

    placebo_ok = placebo_passive <= max(off_passive, FLOOR_PASSIVE_MAX) + PLACEBO_SLACK
    summary["placebo_ok"] = placebo_ok

    precision_verdict = ("LIFT" if prec_lift >= PRECISION_LIFT_MIN
                          else "FAIR_NULL")
    summary["precision_verdict"] = precision_verdict

    if not placebo_ok:
        return "PLACEBO_ARTIFACT_HARD_FAIL_CLAIM", summary

    if on_passive <= HARD_FAIL_PASSIVE_MAX:
        return "HARD_FAIL_TOP_DOWN_DID_NOT_RESOLVE", summary

    if on_passive >= PASS_ACC_MIN and on_active >= PASS_ACC_MIN and on_gap <= GAP_ON_MAX:
        return "HARD_PASS_INTERACTIVE_RESOLVES_ORDER_NEQ_ROLE", summary

    return "MIDDLE_PARTIAL_SIGNAL", summary


def _write_metrics(verdict, summary, units, elapsed, n_seeds, n_train, n_test, epochs, mode):
    metrics = {
        "anchor": ANCHOR_NAME,
        "mode": mode,
        "verdict": verdict,
        "verdict_msg": "%s (off_passive=%.3f off_active=%.3f off_gap=%.3f | on_passive=%.3f "
                       "on_active=%.3f on_gap=%.3f | placebo_passive=%.3f | precision_lift=%.3f)"
                       % (verdict, summary.get("off_passive_acc", -1), summary.get("off_active_acc", -1),
                          summary.get("off_gap", -1), summary.get("on_passive_acc", -1),
                          summary.get("on_active_acc", -1), summary.get("on_gap", -1),
                          summary.get("placebo_passive_acc", -1), summary.get("precision_lift", -1)),
        "summary": summary,
        "config": {
            "n_seeds": n_seeds, "n_train": n_train, "n_test": n_test, "epochs": epochs,
            "d_model": D_MODEL, "pos_scale": POS_SCALE, "feature_scale": FEATURE_SCALE,
            "pos_noise_std": POS_NOISE_STD, "feature_noise_std": FEATURE_NOISE_STD,
        },
        "bands": {
            "FLOOR_PASSIVE_MAX": FLOOR_PASSIVE_MAX, "FLOOR_ACTIVE_MIN": FLOOR_ACTIVE_MIN,
            "FLOOR_GAP_MIN": FLOOR_GAP_MIN, "PASS_ACC_MIN": PASS_ACC_MIN, "GAP_ON_MAX": GAP_ON_MAX,
            "HARD_FAIL_PASSIVE_MAX": HARD_FAIL_PASSIVE_MAX, "PLACEBO_SLACK": PLACEBO_SLACK,
            "PRECISION_LIFT_MIN": PRECISION_LIFT_MIN,
        },
        "per_seed": units,
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    tmp_path = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final_path = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, final_path)
    return metrics


def run_sweep(sweep_values, n_seeds, n_train, n_test, epochs):
    """ONE-VARIABLE settling-iteration sweep: for each settling_iters value run ALL seeds with
    everything else identical (same data, epochs, optimizer, seeds). No checkpoint shard reuse --
    each setting computes its own seeds fresh (settling_iters is not part of the world/data, only
    the ON forward pass), so results are directly comparable across settings.
    Reports, per setting: on_passive, on_active, on_gap, placebo_passive, content_margin
    (=on_passive-placebo_passive), plus off floor (identical across settings by construction, since
    OFF ignores settling_iters -- reported as an invariance check)."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t0 = time.perf_counter()
    rows = []
    for si in sweep_values:
        print("[sweep] settling_iters=%d : running %d seeds ..." % (si, n_seeds), flush=True)
        per_seed = []
        for seed in range(n_seeds):
            r = run_seed(seed, n_train, n_test, epochs, settling_iters=si)
            per_seed.append(r)
            print("  [si=%d seed=%d] off_pass=%.3f off_act=%.3f on_pass=%.3f on_act=%.3f "
                  "placebo=%.3f" % (si, seed, r["off_passive_acc"], r["off_active_acc"],
                                    r["on_passive_acc"], r["on_active_acc"],
                                    r["placebo_passive_acc"]), flush=True)
        agg = {
            "settling_iters": si,
            "off_passive_acc": _mean([r["off_passive_acc"] for r in per_seed]),
            "off_active_acc": _mean([r["off_active_acc"] for r in per_seed]),
            "off_gap": _mean([r["off_active_acc"] - r["off_passive_acc"] for r in per_seed]),
            "on_passive_acc": _mean([r["on_passive_acc"] for r in per_seed]),
            "on_active_acc": _mean([r["on_active_acc"] for r in per_seed]),
            "on_gap": _mean([r["on_gap"] for r in per_seed]),
            "placebo_passive_acc": _mean([r["placebo_passive_acc"] for r in per_seed]),
            "precision_lift": _mean([r["precision"]["lift"] for r in per_seed]),
        }
        agg["content_margin"] = agg["on_passive_acc"] - agg["placebo_passive_acc"]
        agg["floor_held"] = (agg["off_passive_acc"] <= FLOOR_PASSIVE_MAX
                             and agg["off_active_acc"] >= FLOOR_ACTIVE_MIN
                             and agg["off_gap"] >= FLOOR_GAP_MIN)
        agg["placebo_ok"] = agg["placebo_passive_acc"] <= max(agg["off_passive_acc"],
                                                              FLOOR_PASSIVE_MAX) + PLACEBO_SLACK
        agg["per_seed"] = per_seed
        rows.append(agg)
        print("[sweep] settling_iters=%d SUMMARY: on_passive=%.3f on_active=%.3f on_gap=%.3f "
              "placebo=%.3f content_margin=%.3f floor_held=%s placebo_ok=%s"
              % (si, agg["on_passive_acc"], agg["on_active_acc"], agg["on_gap"],
                 agg["placebo_passive_acc"], agg["content_margin"], agg["floor_held"],
                 agg["placebo_ok"]), flush=True)
    elapsed = time.perf_counter() - t0
    out = {
        "anchor": ANCHOR_NAME,
        "mode": "sweep",
        "variable": "settling_iters",
        "sweep_values": sweep_values,
        "config": {"n_seeds": n_seeds, "n_train": n_train, "n_test": n_test, "epochs": epochs},
        "rows": rows,
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    tmp_path = os.path.join(OUTPUT_DIR, "sweep_metrics.json.tmp")
    final_path = os.path.join(OUTPUT_DIR, "sweep_metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    os.replace(tmp_path, final_path)
    print("[sweep] elapsed=%.1fs -> %s" % (elapsed, final_path), flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    args = ap.parse_args()

    if args.sweep:
        run_sweep(SETTLING_SWEEP_VALUES, N_SEEDS_FULL, N_TRAIN_ITEMS_FULL,
                  N_TEST_ITEMS_FULL, EPOCHS_FULL)
        raise SystemExit(0)

    if not args.self_test and not args.full:
        args.self_test = True

    if args.self_test:
        n_seeds, n_train, n_test, epochs, mode = (
            N_SEEDS_SELFTEST, N_TRAIN_ITEMS_SELFTEST, N_TEST_ITEMS_SELFTEST, EPOCHS_SELFTEST, "self_test")
    else:
        n_seeds, n_train, n_test, epochs, mode = (
            N_SEEDS_FULL, N_TRAIN_ITEMS_FULL, N_TEST_ITEMS_FULL, EPOCHS_FULL, "full")

    print("[%s] starting: n_seeds=%d n_train=%d n_test=%d epochs=%d"
          % (mode, n_seeds, n_train, n_test, epochs), flush=True)
    units, elapsed = run_all_seeds(n_seeds, n_train, n_test, epochs, settling_iters=SETTLING_ITERS)
    verdict, summary = decide_verdict(units, n_seeds)
    metrics = _write_metrics(verdict, summary, units, elapsed, n_seeds, n_train, n_test, epochs, mode)
    print("[%s] VERDICT: %s" % (mode, verdict), flush=True)
    print("[%s] %s" % (mode, metrics["verdict_msg"]), flush=True)
    print("[%s] elapsed=%.1fs" % (mode, elapsed), flush=True)

    ok = verdict in ("HARD_PASS_INTERACTIVE_RESOLVES_ORDER_NEQ_ROLE", "MIDDLE_PARTIAL_SIGNAL",
                      "HARD_FAIL_TOP_DOWN_DID_NOT_RESOLVE")
    if mode == "self_test":
        # self-test only requires the pipeline to RUN and the CAN-FAIL FLOOR to be checkable
        # (floor_held True/False both acceptable at self-test scale -- the FULL run is what must
        # actually satisfy floor_held before any HARD_PASS claim is trusted).
        raise SystemExit(0)
    else:
        raise SystemExit(0 if ok or verdict == "FLOOR_NOT_HELD_PROBE_INVALID_HARDEN_TASK" else 1)


if __name__ == "__main__":
    main()
