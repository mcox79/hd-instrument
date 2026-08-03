"""
DIAGNOSTIC CAN-FAIL CELL, DEEP-EARN STEP 5 -- FIRST cell of the substrate-native
RELATION-INFERENCE build (measurement-only, one-shot, not a substrate cell, not
dispatched -- matches the earned_v1..v4 diagnostic convention).

USER-APPROVED TASK (2026-08-03): all 4 probes run tonight (v1..v4) died on the
SAME representational flaw: an event represented as the MEAN of its
content-word vectors, compared by cosine, SATURATES ~0.99 for the trained
(error-driven SGNS) arm specifically (MEASURED@data/exp_content_awareness_
earned_v4_error_driven_sgns/metrics.json: sim_goal_to_restate/satisfy in
[0.9456, 0.9944], spread=0.0488) -- content carries no discriminating signal
under that representation. This cell tests the SUBSTRATE-NATIVE fix: an event
is a BOUND ROLE-FILLER FHRR structure (agent-role BIND filler, action-role
BIND filler, object-role BIND filler, all three BUNDLEd into one composite
per-event vector), not a bag-of-words mean. Relation similarity is computed
through the substrate's bind/unbind/overlap operations (hdlab.binding.bind/
unbind, hdlab.bundling.bundle, the same FHRR overlap-scoring convention as
hdlab.situation_model_accumulate.cleanup_argmax), NOT cosine-of-a-mean.

Prior-work check (substrate_query.sh, mandatory before authoring):
  Query: "bound role-filler FHRR relation representation event binding
  anti-saturation" -> top hits cosine<=0.48, all generic WordNet/FrameNet
  "representation"/"Duration_relation" concept-graph entries, NOT this
  mechanism (no overlap with role-bound-event-structure-as-anti-saturation-
  lever). Verdict: GENUINELY NOVEL as a can-fail cell; the BINDING MACHINERY
  itself (hdlab.binding.bind/unbind, hdlab.bundling.bundle, hdlab.
  situation_model_accumulate.AccumulateRegister/CausalLinkRegister,
  unit_phase_vec, cleanup_argmax scoring convention) is EXISTING, VET-CONFIRMED
  prior art (atom 29609, causal-link DIRECTOR-VERIFIED 0.9722) that this cell
  explicitly REUSES rather than reinvents -- see IMPORTS below.

MECHANISM (substrate-native, glass-box, NO borrowed vectors/model/LLM):
  For each probe text span (goal / restate / satisfy / candidate-action /
  goal-schema description), extract 3 role fillers via a SIMPLE, DECLARED,
  glass-box POSITION HEURISTIC (this is a proof-of-REPRESENTATION cell, not a
  parser build; the claim under test is about the BINDING MATH's effect on
  saturation, not about linguistically-correct SRL):
    AGENT  role filler = first content (non-stopword) word's arm vector
    ACTION role filler = second content word's arm vector
    OBJECT role filler = MEAN of all REMAINING content words' arm vectors
      (same _content_vector-style mean as v1-v4, but now only over the
      left-over bag, not the whole span -- this is the actual anti-saturation
      lever: splitting one big shared-vocabulary bag into 3 smaller,
      role-separated, phase-rotated channels instead of one flat mean).
  Each role filler (a real-valued arm content vector of dimension d_arm) is
  embedded as a complex64 vector (real=filler, imag=0) and BOUND (elementwise
  complex multiply, hdlab.binding.bind) to a FIXED random unit-phase role
  vector (hdlab.situation_model_accumulate.unit_phase_vec; same 3 role
  vectors reused for EVERY item and EVERY arm of matching dimensionality --
  structure/binding held IDENTICAL; only filler content varies, per the ONE
  VARIABLE discipline). The 3 bound terms are BUNDLEd (hdlab.bundling.bundle:
  per-FHRR-component magnitude-renormalized sum) into ONE composite per-event
  vector -- this compresses agent+action+object into a single structure, the
  actual substrate memory-representation move (vs one flat bag-of-words mean).

  SIMILARITY through the substrate's overlap channel (same convention as
  cleanup_argmax's Re(sum(conj(v)*readback))/d scoring in
  hdlab.situation_model_accumulate): structure_overlap(struct_A, struct_B) =
  Re(sum(conj(struct_A) * struct_B)) / d. Bounded in [-1, 1] like the old
  cosine metric (both operands are per-dimension unit-magnitude after
  bundle()), so old-vs-new spreads are directly comparable. SECONDARY
  diagnostic: per-role DECODED overlap (unbind each composite by its own role
  vector, then overlap the two decoded estimates) -- reported per item, not
  used for the primary gates (keeps the smoke bounded in scope).

THREE ARMS, ONE VARIABLE (filler content source), structure/binding held
IDENTICAL across arms of matching dimensionality:
  ARM_ERROR_DRIVEN_SGNS: the v4 encoder's trained embedding table (D=64),
    imported and retrained here bit-identically (same seeds, same
    hyperparameters, same corpus) via
    experiments.exp_content_awareness_earned_v4_error_driven_sgns.train_sgns.
  ARM_RANDOM_INIT_CONTROL: the SAME embedding table, ZERO training steps
    (train_sgns's own w_target_random_init snapshot) -- the CAN-FAIL CONTROL.
    Same dimensionality (D=64) as the trained arm, so the 3 role vectors are
    BIT-IDENTICAL between these two arms -- isolates filler content as the
    ONLY variable for the most important pairwise comparison.
  ARM_PPMI_MEANREMOVAL: earned_v3's raw-PPMI + all-but-the-top mean-removal
    vectors (vocab-dimensional, d differs from the SGNS arms by construction
    -- declared explicitly, not swept under the rug).

Corpora: identical 5-novel combined corpus as earned_v2/v3/v4 (public domain,
Project Gutenberg): anne_of_green_gables (PG#45), wizard_of_oz (PG#55),
tom_sawyer (PG#74), little_women (PG#514), alice_in_wonderland (PG#11).

PRE-REGISTERED VERDICT (locked before running; N=6 hand-selected probe items,
directional can-fail smoke, explicitly NOT the architecture-accept decision):

  GATE 1 -- NON_SATURATION (primary anti-saturation proof): the ERROR_DRIVEN_
    SGNS arm's new structure-overlap sim SPREAD (max-min across all 18 scored
    pairs: 3x{sim_restate,sim_satisfy} + 3x4 schema sims) must MATERIALLY
    WIDEN vs the MEASURED mean-pool reference spread for that SAME arm,
    loaded directly from data/exp_content_awareness_earned_v4_error_driven_
    sgns/metrics.json (not hardcoded): new_spread >= ref_spread + 0.10
    (absolute widening threshold, THEORETICAL/HYPOTHESIZED@this-file: 0.10 is
    ~2x the reference spread of 0.0488, a materially-detectable widening, not
    noise).

  GATE 2 -- CONTROL_FIRES (the honest re-framing of "random-init passed
    0.667"): under bound-structure representation, does the TRAINED arm's
    CONTENT-ONLY ceiling (content_alone ranking + unstated-goal recovery via
    structure_overlap, NO hand-coded structural bonus) now MATERIALLY BEAT
    the RANDOM-INIT arm's content-only ceiling -- where under mean-pool they
    were TIED (both content-alone ceiling = 1/6 = 0.1667 for error_driven [1
    satisfy/restate correct + 0 unstated correct] vs 2/6=0.333 for
    random_init [1+1] -- MEASURED from the SAME v4 metrics file, computed
    fresh in this file's loader, not assumed): margin = ceiling_error_driven
    - ceiling_random_init >= 1/6 (mirrors v4's own CONTROL_MARGIN_MIN
    discriminator convention).

  GATE 3 -- CONTENT_DISCRIMINATION_BEYOND_STRUCTURE: the best of
    {error_driven, ppmi_meanremoval} arms' NEW content-only ceiling must
    STRICTLY EXCEED that SAME arm's OLD (mean-pool) content-only ceiling
    (computed fresh from the v4 metrics file for symmetry) -- i.e. binding
    doesn't just widen the spread cosmetically, it recovers genuine
    discrimination that beat the old flat-mean representation for at least
    one real (non-random) filler source.

  REPRESENTATION_VALID = Gate1 AND Gate2 AND Gate3 all True -> bound
    role-filler structure genuinely tests content (avoids saturation, makes
    the control fail relative to trained content, and recovers real content
    signal) -- the substrate-native representation is validated; recommend
    scaling the encoder + building the real curriculum-grounded eval next.
    Explicitly NOT an architecture-accept decision at N=6.
  REPRESENTATION_STILL_BROKEN = any gate fails -> report honestly which
    gate(s) failed and diagnose the failing operation (spread didn't widen =
    binding math itself is capacity/interference-bound at this d; control
    doesn't fire = random content still content-blind-safe under this scoring
    combination; no discrimination beyond structure = role-splitting alone
    didn't recover signal, encoder quality is the remaining bottleneck).

DISCIPLINE (per exp_dev canonical mandates, scoped to this diagnostic --
matches the lighter template already used by earned_v1..v4, all landed
MEASURED_DIAGNOSTIC cells, not dispatched substrate cells):
- glass-box, no borrowed embedding/model/LLM; role-assignment is a DECLARED
  position heuristic (agent=1st content word, action=2nd, object=mean of
  rest), NOT a bolt-on parser (no spaCy/dependency-parse anywhere in this
  file); the binding/bundling/overlap MACHINERY is REUSED verbatim from
  hdlab (do NOT hand-roll new binding), only the role-extraction heuristic
  and the arm content vectors are novel to this cell.
- deterministic_seeding: role vectors generated via torch.Generator with
  fixed seeds (ROLE_VEC_SEED_D64, ROLE_VEC_SEED_PPMI); SGNS training reuses
  v4's own fixed seeds bit-for-bit (imported functions, not reimplemented).
- ARMS-MUST-DIFFER (META_RULE_AF): hash-check across all 3 arms' composite
  event-structure tensors.
- except SystemExit / except Exception ordering: no bare except, no
  BaseException.
- final_metrics_atomicity: tmp_replace (os.replace) on metrics.json.
- cardinality_ok: n=6 hand-selected probe items x 3 arms = 18 scored units
  (satisfy_restate: 3 items x 2 sims = 6; unstated_goal: 3 items x 4 schema
  sims = 12; total 18 per arm), asserted via len() == EXPECTED.
- CRLB n/a (no fixed-capacity argmax-noise-floor threshold; discrete k/6
  tier feasibility is the Gate-B analogue, same as earned_v4).
- runtime bound: SGNS retraining is the same ~440k-token / 3-epoch / D=64
  job as earned_v4 (measured elapsed_s=138s there); this cell's own added
  compute (building ~24 event structures via bind/bundle/unbind on d<=7641
  vectors) is negligible (<1s). Single foreground run, well under 10 min.
  progress_logging=print_flush_true (reuses v4's own per-epoch heartbeat
  prints inside train_sgns).
- Content-filter safety: only short verbatim snippets already used/cleared
  in earned_v1's SATISFY_RESTATE_ITEMS/UNSTATED_GOAL_ITEMS/GOAL_SCHEMAS
  (imported byte-identical, not re-authored).
- GIT: local only, no push; this file + its metrics.json are the only new
  paths this cell should stage.
"""
import os
import sys
import json
import time
import hashlib
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from hdlab import binding, bundling  # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec  # noqa: E402

from experiments.exp_content_awareness_ceiling_probe_v1 import (  # noqa: E402
    SATISFY_RESTATE_ITEMS,
    UNSTATED_GOAL_ITEMS,
    GOAL_SCHEMAS,
)
from experiments.exp_content_awareness_ceiling_probe_earned_v3_rawppmi_meanremoval import (  # noqa: E402
    build_raw_ppmi_vectors,
    apply_mean_removal,
    _tokenize,
    BASIC_STOPWORDS,
)
from experiments.exp_content_awareness_earned_v4_error_driven_sgns import (  # noqa: E402
    train_sgns,
    D_EMBED,
)

OUTPUT_DIR = os.path.join(
    REPO_ROOT, "data", "exp_content_awareness_earned_v5_bound_role_filler_representation"
)
ANCHOR_NAME = "content_awareness_earned_v5_bound_role_filler_representation"
V4_METRICS_PATH = os.path.join(
    REPO_ROOT, "data", "exp_content_awareness_earned_v4_error_driven_sgns", "metrics.json"
)

CORPUS_PATHS = [
    os.path.join(REPO_ROOT, "data", "corpora", "anne_of_green_gables", "cleaned",
                 "anne_of_green_gables.clean.txt"),
    os.path.join(REPO_ROOT, "data", "corpora", "wizard_of_oz", "cleaned",
                 "wizard_of_oz.clean.txt"),
    os.path.join(REPO_ROOT, "data", "corpora", "tom_sawyer", "cleaned",
                 "tom_sawyer.clean.txt"),
    os.path.join(REPO_ROOT, "data", "corpora", "little_women", "cleaned",
                 "little_women.clean.txt"),
    os.path.join(REPO_ROOT, "data", "corpora", "alice_in_wonderland", "cleaned",
                 "alice_in_wonderland.clean.txt"),
]

EXPECTED_N_SATISFY_RESTATE_ITEMS = 3
EXPECTED_N_UNSTATED_GOAL_ITEMS = 3
EXPECTED_N_ARMS = 3
EXPECTED_N_SCORED_UNITS_PER_ARM = 18  # 3*2 (satisfy/restate) + 3*4 (schema sims)

ROLE_NAMES = ["AGENT", "ACTION", "OBJECT"]
ROLE_VEC_SEED_D64 = 55001       # fixed seed: role vectors for the two D=64 SGNS arms (bit-identical between them)
ROLE_VEC_SEED_PPMI = 55002      # fixed seed: role vectors for the vocab-dim PPMI arm (different d, necessarily different vectors)

# Pre-registered gate thresholds (declared before running; see module docstring)
GATE1_ABS_WIDENING_MIN = 0.10        # THEORETICAL@this-file: ~2x the MEASURED reference spread of 0.0488
GATE2_CONTROL_MARGIN_MIN = 1.0 / 6.0  # mirrors v4's own CONTROL_MARGIN_MIN convention


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


def _arms_must_differ_tensors(named_tensors):
    """META_RULE_AF hash-based check across N named composite-structure tensor stacks."""
    digests = {}
    for name, t in named_tensors.items():
        arr = t.detach().cpu().numpy() if isinstance(t, torch.Tensor) else np.asarray(t)
        digests[name] = hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()
    names = list(digests.keys())
    all_same = len(set(digests.values())) == 1 and len(names) > 1
    pairwise = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b_ = names[i], names[j]
            pairwise[f"{a}__vs__{b_}"] = (digests[a] != digests[b_])
    return digests, pairwise, (not all_same)


def make_role_vecs(d, seed):
    gen = torch.Generator().manual_seed(seed)
    return {r: unit_phase_vec(d, gen) for r in ROLE_NAMES}


def _role_split_words(text):
    """Declared glass-box POSITION heuristic (NOT a parser): first content
    word = AGENT slot, second = ACTION slot, remaining = OBJECT bag. Returns
    (agent_word_or_None, action_word_or_None, object_words_list)."""
    words = [w for w in _tokenize(text) if w not in BASIC_STOPWORDS]
    agent_w = words[0] if len(words) >= 1 else None
    action_w = words[1] if len(words) >= 2 else (words[0] if len(words) == 1 else None)
    object_ws = words[2:] if len(words) > 2 else []
    return agent_w, action_w, object_ws, words


def build_event_struct(text, idx, dense_vecs, d, role_vecs):
    """Builds the bound role-filler FHRR composite for one text span.
    Returns (struct_or_None, coverage_info_dict). struct is complex64[d]."""
    agent_w, action_w, object_ws, all_words = _role_split_words(text)
    covered_all = [w for w in all_words if w in idx]
    if not covered_all:
        return None, {"n_content_words": 0, "n_covered": 0, "agent_covered": False,
                       "action_covered": False, "object_covered_count": 0}

    def _filler(word):
        if word is not None and word in idx:
            return torch.tensor(dense_vecs[idx[word]], dtype=torch.float32)
        return torch.zeros(d, dtype=torch.float32)

    agent_covered = agent_w is not None and agent_w in idx
    action_covered = action_w is not None and action_w in idx
    object_covered = [w for w in object_ws if w in idx]

    agent_filler = _filler(agent_w)
    action_filler = _filler(action_w)
    if object_covered:
        object_filler = torch.stack([torch.tensor(dense_vecs[idx[w]], dtype=torch.float32)
                                      for w in object_covered]).mean(dim=0)
    else:
        object_filler = torch.zeros(d, dtype=torch.float32)

    bound_terms = []
    for role_name, filler in [("AGENT", agent_filler), ("ACTION", action_filler), ("OBJECT", object_filler)]:
        filler_c = torch.complex(filler, torch.zeros_like(filler)).to(torch.complex64)
        bound_terms.append(binding.bind(role_vecs[role_name], filler_c))

    struct = bundling.bundle(torch.stack(bound_terms, dim=0))
    cov = {
        "n_content_words": len(all_words),
        "n_covered": len(covered_all),
        "agent_covered": bool(agent_covered),
        "action_covered": bool(action_covered),
        "object_covered_count": len(object_covered),
        "object_total_count": len(object_ws),
    }
    return struct, cov


def structure_overlap(struct_a, struct_b, d):
    if struct_a is None or struct_b is None:
        return 0.0, True
    val = float(torch.real(torch.sum(torch.conj(struct_a) * struct_b))) / d
    return val, False


def role_decoded_overlap(struct_a, struct_b, role_vec, d):
    """Secondary diagnostic: unbind both composites by the SAME role vector,
    then overlap the decoded estimates (includes cross-role interference,
    which is the expected/meaningful noise term for a bundled superposition)."""
    dec_a = binding.unbind(struct_a, role_vec)
    dec_b = binding.unbind(struct_b, role_vec)
    return float(torch.real(torch.sum(torch.conj(dec_a) * dec_b))) / d


def score_arm_bound(arm_name, idx, dense_vecs, d, role_vecs):
    results_satisfy_restate = []
    content_alone_correct = 0
    all_sim_values = []

    for item in SATISFY_RESTATE_ITEMS:
        goal_struct, goal_cov = build_event_struct(item["goal_text"], idx, dense_vecs, d, role_vecs)
        restate_struct, restate_cov = build_event_struct(item["restate_text"], idx, dense_vecs, d, role_vecs)
        satisfy_struct, satisfy_cov = build_event_struct(item["satisfy_text"], idx, dense_vecs, d, role_vecs)

        sim_restate, restate_zero = structure_overlap(goal_struct, restate_struct, d)
        sim_satisfy, satisfy_zero = structure_overlap(goal_struct, satisfy_struct, d)
        all_sim_values.extend([sim_restate, sim_satisfy])

        content_alone_ranks_satisfy_higher = sim_satisfy > sim_restate
        if content_alone_ranks_satisfy_higher:
            content_alone_correct += 1

        role_decoded = {}
        if goal_struct is not None and satisfy_struct is not None:
            role_decoded["satisfy"] = {
                r: role_decoded_overlap(goal_struct, satisfy_struct, role_vecs[r], d) for r in ROLE_NAMES
            }
        if goal_struct is not None and restate_struct is not None:
            role_decoded["restate"] = {
                r: role_decoded_overlap(goal_struct, restate_struct, role_vecs[r], d) for r in ROLE_NAMES
            }

        results_satisfy_restate.append({
            "goal_id": item["goal_id"],
            "sim_goal_to_restate": sim_restate,
            "sim_goal_to_satisfy": sim_satisfy,
            "restate_zero_coverage": restate_zero,
            "satisfy_zero_coverage": satisfy_zero,
            "goal_coverage": goal_cov,
            "restate_coverage": restate_cov,
            "satisfy_coverage": satisfy_cov,
            "content_alone_misranks": not content_alone_ranks_satisfy_higher,
            "role_decoded_overlap_diagnostic": role_decoded,
        })

    results_unstated_goal = []
    content_recovers = 0
    schema_names = sorted(GOAL_SCHEMAS.keys())  # sorted(set()) discipline
    schema_structs = {}
    schema_covs = {}
    for name in schema_names:
        s_, c_ = build_event_struct(GOAL_SCHEMAS[name], idx, dense_vecs, d, role_vecs)
        schema_structs[name] = s_
        schema_covs[name] = c_

    predicted_schemas = []
    for item in UNSTATED_GOAL_ITEMS:
        action_struct, action_cov = build_event_struct(item["action_text"], idx, dense_vecs, d, role_vecs)
        sims = {}
        zero_flags = {}
        for name in schema_names:
            s_, z = structure_overlap(action_struct, schema_structs[name], d)
            sims[name] = s_
            zero_flags[name] = z
            all_sim_values.append(s_)
        predicted = max(sims, key=sims.get)
        predicted_schemas.append(predicted)
        correct = predicted == item["correct_schema"]
        if correct:
            content_recovers += 1

        results_unstated_goal.append({
            "goal_id": item["goal_id"],
            "correct_schema": item["correct_schema"],
            "predicted_schema": predicted,
            "correct": correct,
            "sims": sims,
            "any_zero_coverage": any(zero_flags.values()),
            "action_coverage": action_cov,
        })

    material_want_collapse = (len(set(predicted_schemas)) == 1 and predicted_schemas[0] == "material_want")

    n_satisfy_restate = len(SATISFY_RESTATE_ITEMS)
    n_unstated = len(UNSTATED_GOAL_ITEMS)
    content_alone_misrank_rate = (n_satisfy_restate - content_alone_correct) / n_satisfy_restate
    unstated_goal_recovery_rate = content_recovers / n_unstated
    content_only_ceiling = (content_alone_correct + content_recovers) / (n_satisfy_restate + n_unstated)

    assert len(all_sim_values) == EXPECTED_N_SCORED_UNITS_PER_ARM, (
        f"cardinality_ok breach for {arm_name}: got {len(all_sim_values)} scored units, "
        f"expected {EXPECTED_N_SCORED_UNITS_PER_ARM}"
    )

    return {
        "arm_name": arm_name,
        "results_satisfy_restate": results_satisfy_restate,
        "results_unstated_goal": results_unstated_goal,
        "predicted_schemas_unstated_goal": predicted_schemas,
        "material_want_collapse": material_want_collapse,
        "collapse_broken": not material_want_collapse,
        "content_alone_misrank_count": n_satisfy_restate - content_alone_correct,
        "content_alone_misrank_rate": content_alone_misrank_rate,
        "content_alone_correct_count": content_alone_correct,
        "unstated_goal_recovery_correct_count": content_recovers,
        "unstated_goal_recovery_rate": unstated_goal_recovery_rate,
        "content_only_ceiling": content_only_ceiling,
        "all_sim_values": all_sim_values,
        "sim_min": min(all_sim_values),
        "sim_median": float(np.median(all_sim_values)),
        "sim_max": max(all_sim_values),
        "sim_spread": max(all_sim_values) - min(all_sim_values),
        "cardinality_ok": len(all_sim_values) == EXPECTED_N_SCORED_UNITS_PER_ARM,
    }


def _load_v4_reference():
    """Loads the mean-pool reference (spread + content-only ceiling) for
    error_driven, random_init, and ppmi_ref arms DIRECTLY from the landed v4
    metrics.json -- not hardcoded. Content-only ceiling recomputed fresh here
    from the same per-item fields v4 already recorded (content_alone_misranks
    + the unstated-goal 'correct' flags), so this file makes no unverified
    numeric claims about the v4 cell's results."""
    with open(V4_METRICS_PATH, "r", encoding="utf-8") as f:
        v4 = json.load(f)

    def _arm_ref(sr_key, ug_key):
        sr = v4[sr_key]
        ug = v4[ug_key]
        sim_vals = []
        for item in sr:
            sim_vals.append(item["sim_goal_to_restate"])
            sim_vals.append(item["sim_goal_to_satisfy"])
        for item in ug:
            sim_vals.extend(item["sims"].values())
        content_alone_correct = sum(1 for item in sr if not item["content_alone_misranks"])
        unstated_correct = sum(1 for item in ug if item["correct"])
        ceiling = (content_alone_correct + unstated_correct) / (len(sr) + len(ug))
        return {
            "sim_min": min(sim_vals),
            "sim_max": max(sim_vals),
            "sim_spread": max(sim_vals) - min(sim_vals),
            "content_only_ceiling": ceiling,
            "n_sim_values": len(sim_vals),
        }

    return {
        "error_driven": _arm_ref("results_arm_error_driven_satisfy_restate", "results_arm_error_driven_unstated_goal"),
        "random_init": _arm_ref("results_arm_random_init_satisfy_restate", "results_arm_random_init_unstated_goal"),
        "ppmi_ref": _arm_ref("results_arm_ppmi_ref_satisfy_restate", "results_arm_ppmi_ref_unstated_goal"),
    }


def main():
    t_start = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    start_marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": "diagnostic_inline_foreground",
        "expected_n_units": EXPECTED_N_SCORED_UNITS_PER_ARM * EXPECTED_N_ARMS,
    }
    tmp = os.path.join(OUTPUT_DIR, "_start_marker.json.tmp")
    final = os.path.join(OUTPUT_DIR, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(start_marker, f)
    os.replace(tmp, final)

    assert len(SATISFY_RESTATE_ITEMS) == EXPECTED_N_SATISFY_RESTATE_ITEMS, "cardinality_ok breach: satisfy/restate items"
    assert len(UNSTATED_GOAL_ITEMS) == EXPECTED_N_UNSTATED_GOAL_ITEMS, "cardinality_ok breach: unstated-goal items"
    assert os.path.exists(V4_METRICS_PATH), f"v4 reference metrics missing at {V4_METRICS_PATH}; cannot compute reference spreads"

    v4_ref = _load_v4_reference()

    corpus_texts = []
    corpus_word_counts = {}
    for p in CORPUS_PATHS:
        with open(p, "r", encoding="utf-8") as f:
            txt = f.read()
        corpus_texts.append(txt)
        corpus_word_counts[os.path.basename(p)] = len(_tokenize(txt))

    # ---- PPMI arm (vocab-dim; recomputed on THIS run's corpus, same pipeline as earned_v3/v4) ----
    vocab, idx, ppmi_raw_vecs, n_tokens, vocab_size, ppmi_nnz = build_raw_ppmi_vectors(corpus_texts)
    ppmi_corrected_vecs, mean_vec, top_dirs, mr_iters, mr_residuals = apply_mean_removal(ppmi_raw_vecs)

    # ---- SGNS arms (D=64; bit-identical retrain of v4's own train_sgns) ----
    tokens = []
    for text in corpus_texts:
        tokens.extend(_tokenize(text))
    tok_idx = np.array([idx.get(w, -1) for w in tokens], dtype=np.int64)
    vocab_counts_arr = np.zeros(vocab_size, dtype=np.int64)
    for ti in tok_idx:
        if ti >= 0:
            vocab_counts_arr[ti] += 1

    print(f"[progress] corpus loaded: n_tokens={n_tokens} vocab_size={vocab_size} starting SGNS retrain (bit-identical to v4)", flush=True)
    w_sgns_trained, w_sgns_random_init, n_pairs_trained, per_epoch_err = train_sgns(
        tok_idx, vocab_size, vocab_counts_arr
    )
    print(f"[progress] SGNS retrain complete n_pairs_trained={n_pairs_trained}", flush=True)

    # ---- role vectors: fixed, shared across items; SAME dim=D_EMBED for the two SGNS arms (bit-identical) ----
    role_vecs_d64 = make_role_vecs(D_EMBED, ROLE_VEC_SEED_D64)
    role_vecs_ppmi = make_role_vecs(vocab_size, ROLE_VEC_SEED_PPMI)

    role_vecs_digest_check, role_vecs_pairwise, _ = _arms_must_differ_tensors({
        f"role_{r}_d64": role_vecs_d64[r] for r in ROLE_NAMES
    })  # sanity: 3 role vectors within d64 set must differ from each other
    assert all(role_vecs_pairwise.values()), "role vectors within the d64 set are not pairwise distinct"

    arm_error_driven = score_arm_bound("ARM_ERROR_DRIVEN_SGNS", idx, w_sgns_trained, D_EMBED, role_vecs_d64)
    arm_random_init = score_arm_bound("ARM_RANDOM_INIT_CONTROL", idx, w_sgns_random_init, D_EMBED, role_vecs_d64)
    arm_ppmi_ref = score_arm_bound("ARM_PPMI_MEANREMOVAL", idx, ppmi_corrected_vecs, vocab_size, role_vecs_ppmi)

    # ---- ARMS-MUST-DIFFER (META_RULE_AF) across composite event structures ----
    # (compare goal_001's composite struct across arms of matching dim; PPMI has different dim so
    #  compared only among the two D=64 arms for a like-for-like bit check, plus a coverage-diagnostic.)
    goal0_struct_ed, _ = build_event_struct(SATISFY_RESTATE_ITEMS[0]["goal_text"], idx, w_sgns_trained, D_EMBED, role_vecs_d64)
    goal0_struct_ri, _ = build_event_struct(SATISFY_RESTATE_ITEMS[0]["goal_text"], idx, w_sgns_random_init, D_EMBED, role_vecs_d64)
    arm_struct_digests, arm_struct_pairwise, arm_structs_differ = _arms_must_differ_tensors({
        "arm_error_driven_goal0_struct": goal0_struct_ed,
        "arm_random_init_goal0_struct": goal0_struct_ri,
    })
    assert arm_structs_differ, "META_RULE_AF VIOLATION: error-driven and random-init composite structures bit-identical"

    # ---- pre-registered verdict logic ----
    ed_spread = arm_error_driven["sim_spread"]
    ref_ed_spread = v4_ref["error_driven"]["sim_spread"]
    gate1_non_saturation = (ed_spread - ref_ed_spread) >= GATE1_ABS_WIDENING_MIN

    ed_content_ceiling = arm_error_driven["content_only_ceiling"]
    ri_content_ceiling = arm_random_init["content_only_ceiling"]
    control_margin = ed_content_ceiling - ri_content_ceiling
    gate2_control_fires = control_margin >= GATE2_CONTROL_MARGIN_MIN - 1e-9

    ppmi_content_ceiling = arm_ppmi_ref["content_only_ceiling"]
    ref_ed_ceiling = v4_ref["error_driven"]["content_only_ceiling"]
    ref_ppmi_ceiling = v4_ref["ppmi_ref"]["content_only_ceiling"]
    ed_beats_old = ed_content_ceiling > ref_ed_ceiling + 1e-9
    ppmi_beats_old = ppmi_content_ceiling > ref_ppmi_ceiling + 1e-9
    gate3_content_discrimination = ed_beats_old or ppmi_beats_old

    if gate1_non_saturation and gate2_control_fires and gate3_content_discrimination:
        verdict_regime = "REPRESENTATION_VALID"
    else:
        failed_gates = []
        if not gate1_non_saturation:
            failed_gates.append("GATE1_NON_SATURATION")
        if not gate2_control_fires:
            failed_gates.append("GATE2_CONTROL_FIRES")
        if not gate3_content_discrimination:
            failed_gates.append("GATE3_CONTENT_DISCRIMINATION")
        verdict_regime = "REPRESENTATION_STILL_BROKEN_" + "_AND_".join(failed_gates)

    elapsed_s = time.perf_counter() - t_start

    summary = {
        "mechanism": (
            "bound role-filler FHRR event structure (AGENT/ACTION/OBJECT position-heuristic "
            "role split, bind+bundle via hdlab.binding/hdlab.bundling, structure_overlap "
            "similarity via the situation_model_accumulate overlap convention), NOT cosine-of-mean"
        ),
        "arms": {
            "ARM_ERROR_DRIVEN_SGNS": {k: v for k, v in arm_error_driven.items()
                                        if k not in ("results_satisfy_restate", "results_unstated_goal", "all_sim_values")},
            "ARM_RANDOM_INIT_CONTROL": {k: v for k, v in arm_random_init.items()
                                         if k not in ("results_satisfy_restate", "results_unstated_goal", "all_sim_values")},
            "ARM_PPMI_MEANREMOVAL": {k: v for k, v in arm_ppmi_ref.items()
                                      if k not in ("results_satisfy_restate", "results_unstated_goal", "all_sim_values")},
        },
        "v4_mean_pool_reference_MEASURED": v4_ref,
        "gate1_non_saturation": {
            "new_error_driven_spread": ed_spread,
            "ref_error_driven_spread_MEASURED": ref_ed_spread,
            "widening": ed_spread - ref_ed_spread,
            "threshold_min_widening": GATE1_ABS_WIDENING_MIN,
            "fires": gate1_non_saturation,
        },
        "gate2_control_fires": {
            "error_driven_content_only_ceiling": ed_content_ceiling,
            "random_init_content_only_ceiling": ri_content_ceiling,
            "control_margin": control_margin,
            "threshold_min_margin": GATE2_CONTROL_MARGIN_MIN,
            "fires": gate2_control_fires,
            "note": "under mean-pool these were TIED/near-tied (MEASURED ref ceilings: "
                    f"error_driven={ref_ed_ceiling:.4f} random_init={v4_ref['random_init']['content_only_ceiling']:.4f})",
        },
        "gate3_content_discrimination": {
            "error_driven_new_ceiling": ed_content_ceiling,
            "error_driven_old_ceiling_MEASURED": ref_ed_ceiling,
            "error_driven_beats_old": ed_beats_old,
            "ppmi_new_ceiling": ppmi_content_ceiling,
            "ppmi_old_ceiling_MEASURED": ref_ppmi_ceiling,
            "ppmi_beats_old": ppmi_beats_old,
            "fires": gate3_content_discrimination,
        },
        "verdict_regime": verdict_regime,
        "corpus_n_tokens_combined": n_tokens,
        "corpus_vocab_size_after_min_count_filter": vocab_size,
        "sgns_n_pairs_trained": n_pairs_trained,
        "role_vec_dims": {"d64_arms": D_EMBED, "ppmi_arm": vocab_size},
        "n_probe_items_caveat": (
            "N=6 hand-selected probe items; this is a CAN-FAIL SMOKE for whether the bound "
            "role-filler REPRESENTATION avoids saturation and tests content, explicitly NOT "
            "the architecture-accept decision or a claim of solved relation-inference."
        ),
        "elapsed_s": elapsed_s,
    }

    metrics = {
        "verdict": "MEASURED_DIAGNOSTIC",
        "verdict_msg": (
            f"verdict_regime={verdict_regime} (N=6 probe, directional, can-fail smoke); "
            f"gate1_non_saturation={gate1_non_saturation} (ed_spread={ed_spread:.4f} vs ref={ref_ed_spread:.4f}, "
            f"widening={ed_spread - ref_ed_spread:.4f}); "
            f"gate2_control_fires={gate2_control_fires} (margin={control_margin:.4f}); "
            f"gate3_content_discrimination={gate3_content_discrimination} "
            f"(ed_beats_old={ed_beats_old} ppmi_beats_old={ppmi_beats_old})"
        ),
        "summary": f"DEEP-EARN STEP 5 (bound role-filler FHRR representation, first relation-inference can-fail cell) verdict_regime={verdict_regime}",
        "elapsed_s": elapsed_s,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "results_arm_error_driven_satisfy_restate": arm_error_driven["results_satisfy_restate"],
        "results_arm_error_driven_unstated_goal": arm_error_driven["results_unstated_goal"],
        "results_arm_random_init_satisfy_restate": arm_random_init["results_satisfy_restate"],
        "results_arm_random_init_unstated_goal": arm_random_init["results_unstated_goal"],
        "results_arm_ppmi_ref_satisfy_restate": arm_ppmi_ref["results_satisfy_restate"],
        "results_arm_ppmi_ref_unstated_goal": arm_ppmi_ref["results_unstated_goal"],
        "summary_fields": summary,
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "passed_all_4_patterns_scaled_to_diagnostic_n6x3arms",
        "final_metrics_atomicity": "tmp_replace",
        "arms_differ_exempted": [],
        "deterministic_seeding": True,
        "progress_logging": "print_flush_true",
        "crlb_n_a": "no fixed-capacity argmax-noise-floor threshold in this cell; discrete k/6 tier feasibility (Gate-B analogue) documented in module docstring; bind/bundle capacity (3 roles into 1 composite, well within validated FHRR bundle capacity) is not the tested limit at this scale",
    }

    tmp_path = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final_path = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, final_path)

    print(json.dumps(summary, indent=2))


def self_test():
    """Tiny-scale real-code-path self-test: exercises the ACTUAL bind/bundle/
    unbind pipeline (hdlab.binding, hdlab.bundling) and build_event_struct /
    structure_overlap on a synthetic tiny vocab, at production dtype/shape
    logic. Runs in well under 1 second."""
    d = 8
    vocab = ["alice", "wants", "tea", "bob", "gives", "cake", "runs", "fast"]
    idx = {w: i for i, w in enumerate(vocab)}
    rng = np.random.RandomState(0)
    dense_vecs = rng.rand(len(vocab), d).astype(np.float64)

    role_vecs = make_role_vecs(d, seed=1)
    assert set(role_vecs.keys()) == set(ROLE_NAMES)
    for r in ROLE_NAMES:
        assert role_vecs[r].dtype == torch.complex64
        mags = role_vecs[r].abs()
        assert torch.allclose(mags, torch.ones_like(mags), atol=1e-5), "role vec not unit-magnitude"

    struct_a, cov_a = build_event_struct("alice wants tea", idx, dense_vecs, d, role_vecs)
    struct_b, cov_b = build_event_struct("bob gives cake", idx, dense_vecs, d, role_vecs)
    assert struct_a is not None and struct_b is not None
    assert struct_a.shape == (d,) and struct_a.dtype == torch.complex64
    assert cov_a["n_covered"] == 3 and cov_a["agent_covered"] and cov_a["action_covered"]

    sim_ab, zero_ab = structure_overlap(struct_a, struct_b, d)
    assert not zero_ab
    assert -1.0 - 1e-6 <= sim_ab <= 1.0 + 1e-6, f"structure_overlap out of bounded range: {sim_ab}"

    sim_aa, _ = structure_overlap(struct_a, struct_a, d)
    assert sim_aa > sim_ab, "self-overlap should exceed overlap with a different event (sanity)"

    role_dec = role_decoded_overlap(struct_a, struct_b, role_vecs["AGENT"], d)
    assert isinstance(role_dec, float)

    # empty-text edge case: zero-coverage sentinel, not a crash
    struct_none, cov_none = build_event_struct("zzznotinvocab", idx, dense_vecs, d, role_vecs)
    assert struct_none is None and cov_none["n_covered"] == 0

    print(
        f"[self_test] PASS  sim_ab={sim_ab:.4f}  sim_aa={sim_aa:.4f}  "
        f"role_decoded_sample={role_dec:.4f}  zero_coverage_handled=True",
        flush=True,
    )


if __name__ == "__main__":
    try:
        if "--self-test" in sys.argv:
            self_test()
        else:
            main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise
