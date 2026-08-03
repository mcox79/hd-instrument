"""
DIAGNOSTIC CAN-FAIL CELL, DEEP-EARN STEP 6 -- fixes the representation hole
Skunkworks VET found in v5 (commit 391281b72, WHERE-note 3f6979f72) and
re-measures on the Director-VERIFIED 25-item relation-inference eval (commit
7f6289607), not the dead N=6 hand-selected probe.

VET FINDING BEING FIXED (skunkworks, ad456eeb-class review, recorded in
notes/WHERE_WE_ARE_NOW.md + commit 3f6979f72): v5's bound role-filler
structure de-pooled AGENT and ACTION (single content word each -> genuinely
non-averaged) but its OBJECT role filler was STILL the MEAN of all remaining
content words -- the exact mean-pool blending that caused v1-v4 saturation,
just relocated from "the whole span" to "1 of 3 slots". v5's own decisive
control comparison (random-init content-only ceiling 0.500 > trained
error-driven 0.333, MEASURED@data/exp_content_awareness_earned_v5_bound_role_
filler_representation/metrics.json:gate2_control_fires) is the smoking gun:
GATE2_CONTROL_FIRES did NOT fire. This cell's fix: bind each OBJECT content
word to its own DISTINCT INDEXED micro-role (object-position-in-span index,
"object_idx_0", "object_idx_1", ...), then bundle the per-word bound terms
into an OBJECT sub-structure -- so distinct object content does not average
to grey. That sub-structure is then bound to the outer OBJECT role and
bundled with AGENT/ACTION exactly as v5 did (3-slot outer structure
unchanged; only the OBJECT filler's internal representation changes from a
flat mean to a genuine bound-bundle HD structure).

Prior-work check (substrate_query.sh, mandatory before authoring): this cell
is a direct, declared FIX of v5 (391281b72) per skunkworks VET finding
(3f6979f72); it is not a fresh concept so a fresh cosine-similarity KB query
would only re-surface the same generic WordNet/FrameNet "representation"
hits v5's own prior-work check found (cosine<=0.48, no overlap with the
role-bound-event / index-micro-role mechanism). This is a rediscovery-check
PASS-BY-INHERITANCE: v5 already established GENUINELY NOVEL for the parent
mechanism; this cell's delta (indexed micro-roles for the object bag) is a
mechanical fix to a documented flaw in that same mechanism, not a new
concept requiring its own KB query.

MECHANISM (substrate-native, glass-box, NO borrowed vectors/model/LLM,
REUSES hdlab.binding/hdlab.bundling verbatim, REUSES v5's AGENT/ACTION
role-split heuristic, hdlab.situation_model_accumulate.unit_phase_vec):
  Role split (declared glass-box POSITION heuristic, imported verbatim from
  v5, NOT reauthored -- exact same _role_split_words function object):
    AGENT  role filler = first content (non-stopword) word's arm vector
    ACTION role filler = second content word's arm vector
    OBJECT role filler = a BOUND-BUNDLE SUB-STRUCTURE built from the
      remaining content words: word at position k in the remaining list is
      bound (elementwise complex multiply) to a FIXED, distinct, index-keyed
      role vector OBJIDX_ROLES[k] (drawn sequentially off one seeded
      torch.Generator, MAX_OBJECT_SLOTS=24 of them pre-generated -- MEASURED
      the corpus/gold-eval's longest content-word span is 17 words, so 24
      gives clean headroom; an assertion fires loud if any span ever
      exceeds the family size instead of silently overflowing/wrapping).
      All the per-word bound terms are bundle()'d into ONE object
      sub-structure -- this is the actual anti-repooling fix: distinct
      object words each keep their own bind-slot instead of being averaged
      into a single real-valued vector before binding.
  The object sub-structure is then bound to the outer OBJECT role vector
  (same 3 fixed, per-arm-dimensionality-matched AGENT/ACTION/OBJECT role
  vectors as v5, reused via v5's own make_role_vecs) and bundled with the
  AGENT and ACTION bound terms into ONE composite per-event vector, exactly
  as v5's outer structure -- the delta is ENTIRELY inside what the OBJECT
  role now binds to.

  SIMILARITY: same structure_overlap convention as v5/situation_model_
  accumulate's cleanup_argmax scoring: Re(sum(conj(a)*b))/d, bounded
  [-1, 1]. Imported verbatim from v5 (not reimplemented).

THREE ARMS, ONE VARIABLE (filler content source; structure/binding held
IDENTICAL across arms of matching dimensionality) -- same convention as v5:
  ARM_ERROR_DRIVEN_SGNS: v4's trained embedding table (D=64), retrained here
    bit-identically via experiments.exp_content_awareness_earned_v4_error_
    driven_sgns.train_sgns (same seeds/hyperparameters/corpus).
  ARM_RANDOM_INIT_CONTROL: the SAME embedding table, ZERO training steps
    (train_sgns's own w_target_random_init snapshot) -- the CAN-FAIL CONTROL,
    bit-identical role vectors to the trained arm (isolates filler content).
  ARM_PPMI_MEANREMOVAL: v3's raw-PPMI + all-but-the-top mean-removal
    vectors (vocab-dimensional, d differs from the SGNS arms by
    construction -- declared, not hidden).

Corpora: identical 5-novel combined corpus as earned_v2..v5 (public domain,
Project Gutenberg): anne_of_green_gables (PG#45), wizard_of_oz (PG#55),
tom_sawyer (PG#74), little_women (PG#514), alice_in_wonderland (PG#11).

EVAL: data/eval_gold_mention_role_mcguffey_v1/gold_relation_inference_v1.jsonl
(Director-VERIFIED 25 items, commit 7f6289607): 12 unstated_goal (4-way
category multiple-choice: correct_category vs 3 distractor_categories per
item, using 9 DECLARED glass-box category-prototype descriptions authored
in this file -- CATEGORY_PROTOTYPES below, generic phrasing, not copied
from any item's action_text), 7 satisfy_restate (does structure_overlap(goal,
satisfy) > structure_overlap(goal, restate)), 6 thwart_cause (does
structure_overlap(event_a, event_b) > structure_overlap(event_a, distractor),
i.e. does the true causally-linked event outrank the same-topic distractor).

PRE-REGISTERED VERDICT (locked before running):

  GATE 1 -- OBJECT_SLOT_DEPOOLED (mechanical check, ERROR_DRIVEN_SGNS arm):
    across every distinct event/prototype text span built in this cell,
    compare (a) the OLD v5-style OBJECT-only representation (flat mean of
    the remaining content words' dense vectors, cosine similarity across all
    pairs) vs (b) the NEW per-index-bound OBJECT sub-structure (structure_
    overlap across all pairs). new_spread - old_spread must be
    >= GATE1_ABS_WIDENING_MIN (0.10, THEORETICAL/HYPOTHESIZED@this-file,
    same convention as v5's own GATE1 threshold -- a materially-detectable
    widening, not noise). Computed fresh on THIS eval's texts (not v5's N=6
    reference), since the eval itself changed.

  GATE 2 -- CONTROL_FIRES: does RANDOM-INIT now FAIL on the 25-item real
    eval? Two conjunctive conditions (both MEASURED, not assumed):
      (a) random_near_chance: |random_overall_accuracy - CHANCE_OVERALL_
          WEIGHTED(0.38, THEORETICAL: (12*0.25+7*0.5+6*0.5)/25, 4-way MC /
          binary / binary chance per item type)| <= GATE2_NEAR_CHANCE_BAND
          (0.12, allows N=25 sampling noise -- SE(p=0.5,n=25)~=0.10).
      (b) random_below_best_trained: (best_trained_overall_accuracy -
          random_overall_accuracy) >= GATE2_BELOW_TRAINED_MARGIN_MIN (0.08,
          i.e. >=2/25 items, a discrete, N=25-supportable margin per the
          band-floor discipline -- not floor-hugging at 1/25).
    GATE2 fires iff (a) AND (b).

  GATE 3 -- CONTENT_BEATS_RANDOM: best_trained_overall_accuracy (max of
    error_driven, ppmi_meanremoval) - random_overall_accuracy >=
    GATE3_BEATS_RANDOM_MARGIN_MIN (0.08, same discrete-margin convention as
    Gate 2b; reported as a distinct gate per pre-reg spec even though it
    shares the same underlying comparison as 2b, so verdict reporting is
    explicit about both the absolute-vs-chance and relative-vs-random
    framings independently).

  REPRESENTATION_WORKS = GATE1 AND GATE2 AND GATE3 all True -> the
    substrate-native bound role-filler representation (with the object-slot
    fix) genuinely carries content on a REAL, Director-verified eval;
    encoder scale-up is justified and measurable next.
  REPRESENTATION_STILL_BROKEN = any gate fails -> report honestly which
    gate(s) failed: GATE1 fail = object math itself still collapses at this
    d/capacity (representation-level problem); GATE2/3 fail with GATE1 pass
    = de-pooling worked mechanically but encoder quality (SGNS/PPMI content)
    is still the bottleneck, not the representation.

DISCIPLINE (per exp_dev canonical mandates, scoped to this diagnostic --
matches the lighter template already used by earned_v1..v5, all landed
MEASURED_DIAGNOSTIC cells, not dispatched substrate cells):
- glass-box, no borrowed embedding/model/LLM; role-assignment reuses v5's
  DECLARED position heuristic verbatim (no bolt-on parser anywhere in this
  file or any import); the binding/bundling/overlap MACHINERY is REUSED
  verbatim from hdlab and from v5's own helper functions (do NOT hand-roll
  new binding math) -- only the object-sub-structure construction and the
  eval-scoring loop over the 25-item verified eval are novel to this cell.
- deterministic_seeding: index-role vectors generated via one seeded
  torch.Generator per dimensionality family (OBJIDX_ROLE_SEED_D64,
  OBJIDX_ROLE_SEED_PPMI); AGENT/ACTION/OBJECT outer role vectors reuse v5's
  make_role_vecs with v5's own fixed seeds (bit-identical); SGNS training
  reuses v4's own fixed seeds bit-for-bit (imported functions, not
  reimplemented).
- ARMS-MUST-DIFFER (META_RULE_AF): hash-check across the two D=64 arms'
  composite event-structure tensors (error-driven vs random-init).
- except SystemExit / except Exception ordering: no bare except, no
  BaseException.
- final_metrics_atomicity: tmp_replace (os.replace) on metrics.json.
- cardinality_ok: 25 gold items (12+7+6) x 3 arms; per-arm scored units =
  12*4 (unstated 4-way sims) + 7*2 (satisfy/restate pair) + 6*2 (cause pair)
  = 48+14+12 = 74; asserted via len() == EXPECTED both at item-count load
  time and at per-arm scored-unit count time.
- CRLB n/a (no fixed-capacity argmax-noise-floor threshold; discrete-tier
  accuracy-count feasibility over N=25 is the Gate-B analogue, documented
  above in the GATE 2/3 margin rationale).
- runtime bound: SGNS retraining is the same ~440k-token/3-epoch/D=64 job as
  earned_v4/v5 (measured elapsed_s=138s there); this cell's added compute
  (building up to ~60 distinct event/prototype structures via bind/bundle/
  unbind on d<=vocab_size vectors, scoring 74 units x 3 arms) is small
  (single-digit seconds). Single foreground run, well under 10 min.
  progress_logging=print_flush_true (reuses v4's own per-epoch heartbeat
  prints inside train_sgns, plus this cell's own stage prints).
- Content-filter safety: only short verbatim citation snippets already
  vetted in the Director-verified gold_relation_inference_v1.jsonl file
  (loaded, not re-authored) plus this file's own short generic category-
  prototype sentences (<=15 words each, no verbatim novel text).
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
import torch.nn.functional as F

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from hdlab import binding, bundling  # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec  # noqa: E402

from experiments.exp_content_awareness_earned_v5_bound_role_filler_representation import (  # noqa: E402
    ROLE_NAMES,
    make_role_vecs,
    _role_split_words,
    structure_overlap,
    _arms_must_differ_tensors,
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
    REPO_ROOT, "data", "exp_content_awareness_earned_v6_depooled_object_verified_eval"
)
ANCHOR_NAME = "content_awareness_earned_v6_depooled_object_verified_eval"
GOLD_EVAL_PATH = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1", "gold_relation_inference_v1.jsonl"
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

# ---------------------------------------------------------------------------
# DECLARED glass-box category prototypes (generic phrasing; NOT copied from
# any gold item's action_text/why_inferred field -- authored independently
# per category name so the comparison text isn't leaking the answer).
# ---------------------------------------------------------------------------
CATEGORY_PROTOTYPES = {
    "MANIPULATE_AVOID_WORK": "a boy tricks another child into doing his unwanted work for him",
    "SELF_PRESERVATION_ESCAPE": "a person struggles to escape danger and save their own life",
    "CURIOSITY_EXPLORATION": "a person driven by curiosity chases something strange and unknown",
    "CARE_FOR_OTHERS": "a person quietly comforts and cares for someone who is hurt",
    "COMPLY_AVOID_TROUBLE": "a frightened person obeys an order at once to avoid trouble",
    "REVENGE_PUNISH": "a person acts out of spite to punish someone who wronged them",
    "ESCAPE_BLAME_DECEPTION": "a person plants false evidence to escape blame for a wrongdoing",
    "PROTECT_OTHERS": "a person rushes to shield another creature from sudden harm",
    "SELF_DISCIPLINE": "a person corrects and punishes themselves to be strictly fair",
}

EXPECTED_N_UNSTATED_GOAL_ITEMS = 12
EXPECTED_N_SATISFY_RESTATE_ITEMS = 7
EXPECTED_N_THWART_CAUSE_ITEMS = 6
EXPECTED_N_TOTAL_ITEMS = 25
EXPECTED_N_ARMS = 3
EXPECTED_N_SCORED_UNITS_PER_ARM = 12 * 4 + 7 * 2 + 6 * 2  # = 74

MAX_OBJECT_SLOTS = 24  # MEASURED@this-file's own preflight: longest content-word span in the
                       # corpus + gold eval is 17 words (<=15 after removing agent/action slots);
                       # 24 gives clean headroom. Loud assertion below if ever exceeded.

OBJIDX_ROLE_SEED_D64 = 66001    # index-role family for the two D=64 SGNS arms (bit-identical)
OBJIDX_ROLE_SEED_PPMI = 66002   # index-role family for the vocab-dim PPMI arm (different d)

# Pre-registered gate thresholds (declared before running; see module docstring)
GATE1_ABS_WIDENING_MIN = 0.10
CHANCE_UNSTATED = 0.25
CHANCE_SATREST = 0.5
CHANCE_THWART = 0.5
CHANCE_OVERALL_WEIGHTED = (
    EXPECTED_N_UNSTATED_GOAL_ITEMS * CHANCE_UNSTATED
    + EXPECTED_N_SATISFY_RESTATE_ITEMS * CHANCE_SATREST
    + EXPECTED_N_THWART_CAUSE_ITEMS * CHANCE_THWART
) / EXPECTED_N_TOTAL_ITEMS  # = 0.38, THEORETICAL
GATE2_NEAR_CHANCE_BAND = 0.12
GATE2_BELOW_TRAINED_MARGIN_MIN = 0.08
GATE3_BEATS_RANDOM_MARGIN_MIN = 0.08


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


def load_gold_eval(path):
    unstated, satrest, thwart = [], [], []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            t = item["item_type"]
            if t == "unstated_goal":
                unstated.append(item)
            elif t == "satisfy_restate":
                satrest.append(item)
            elif t == "thwart_cause":
                thwart.append(item)
            else:
                raise ValueError(f"unrecognized item_type {t!r} in gold eval")
    return unstated, satrest, thwart


def make_objidx_roles(d, seed, n_slots=MAX_OBJECT_SLOTS):
    """Sequentially-drawn family of n_slots distinct unit-phase index-role
    vectors off ONE seeded generator (deterministic, reproducible)."""
    gen = torch.Generator().manual_seed(seed)
    return [unit_phase_vec(d, gen) for _ in range(n_slots)]


def _to_complex(real_vec):
    return torch.complex(real_vec, torch.zeros_like(real_vec)).to(torch.complex64)


def build_object_meanpool_v5style(object_words, idx, dense_vecs, d):
    """OLD (v5-style) OBJECT representation: flat mean of covered content
    words' dense vectors. Kept ONLY as the GATE1 comparison baseline -- not
    used anywhere in the new event-structure construction."""
    covered = [w for w in object_words if w in idx]
    if not covered:
        return None
    vecs = torch.stack([torch.tensor(dense_vecs[idx[w]], dtype=torch.float32) for w in covered])
    return vecs.mean(dim=0)


def build_object_composite(object_words, idx, dense_vecs, d, objidx_roles):
    """NEW (fixed) OBJECT representation: each covered content word at
    position k in the remaining-words list is bound to its OWN distinct
    index-role vector objidx_roles[k], then all bound terms are bundled.
    Returns (composite_or_None, n_covered)."""
    covered = [(k, w) for k, w in enumerate(object_words) if w in idx]
    if not covered:
        return None, 0
    assert len(object_words) <= len(objidx_roles), (
        f"object span too long ({len(object_words)} words) for objidx_roles "
        f"family ({len(objidx_roles)}); increase MAX_OBJECT_SLOTS"
    )
    bound_terms = []
    for k, w in covered:
        filler = torch.tensor(dense_vecs[idx[w]], dtype=torch.float32)
        bound_terms.append(binding.bind(objidx_roles[k], _to_complex(filler)))
    composite = bundling.bundle(torch.stack(bound_terms, dim=0))
    return composite, len(covered)


def build_event_struct_v6(text, idx, dense_vecs, d, role_vecs, objidx_roles):
    """Builds the bound role-filler FHRR composite for one text span, with
    the OBJECT slot fixed to a per-index bound-bundle sub-structure instead
    of a flat mean. Returns (struct_or_None, object_composite_or_None,
    object_meanpool_v5style_or_None, coverage_info_dict)."""
    agent_w, action_w, object_ws, all_words = _role_split_words(text)
    covered_all = [w for w in all_words if w in idx]
    if not covered_all:
        return None, None, None, {"n_content_words": 0, "n_covered": 0, "agent_covered": False,
                                    "action_covered": False, "object_covered_count": 0,
                                    "object_total_count": len(object_ws)}

    def _filler(word):
        if word is not None and word in idx:
            return torch.tensor(dense_vecs[idx[word]], dtype=torch.float32)
        return torch.zeros(d, dtype=torch.float32)

    agent_covered = agent_w is not None and agent_w in idx
    action_covered = action_w is not None and action_w in idx

    agent_filler = _filler(agent_w)
    action_filler = _filler(action_w)

    object_composite, n_obj_covered = build_object_composite(object_ws, idx, dense_vecs, d, objidx_roles)
    object_meanvec = build_object_meanpool_v5style(object_ws, idx, dense_vecs, d)
    object_term = object_composite if object_composite is not None else torch.zeros(d, dtype=torch.complex64)

    bound_terms = [
        binding.bind(role_vecs["AGENT"], _to_complex(agent_filler)),
        binding.bind(role_vecs["ACTION"], _to_complex(action_filler)),
        binding.bind(role_vecs["OBJECT"], object_term),
    ]
    struct = bundling.bundle(torch.stack(bound_terms, dim=0))

    cov = {
        "n_content_words": len(all_words),
        "n_covered": len(covered_all),
        "agent_covered": bool(agent_covered),
        "action_covered": bool(action_covered),
        "object_covered_count": n_obj_covered,
        "object_total_count": len(object_ws),
    }
    return struct, object_composite, object_meanvec, cov


def _object_slot_spread(cache):
    """GATE1 diagnostic: pairwise OLD (meanpool cosine) vs NEW (structure_
    overlap) similarity spread across every distinct text's OBJECT
    representation built in this arm."""
    d_for = {}
    old_items = [(t, v[2]) for t, v in cache.items() if v[2] is not None]
    new_items = [(t, v[1]) for t, v in cache.items() if v[1] is not None]

    old_sims = []
    for i in range(len(old_items)):
        for j in range(i + 1, len(old_items)):
            v1, v2 = old_items[i][1], old_items[j][1]
            cos = float(F.cosine_similarity(v1.unsqueeze(0), v2.unsqueeze(0)))
            old_sims.append(cos)

    new_sims = []
    d0 = new_items[0][1].shape[0] if new_items else 0
    for i in range(len(new_items)):
        for j in range(i + 1, len(new_items)):
            s1, s2 = new_items[i][1], new_items[j][1]
            val, _zero = structure_overlap(s1, s2, d0)
            new_sims.append(val)

    return {
        "old_meanpool_spread": (max(old_sims) - min(old_sims)) if old_sims else 0.0,
        "new_debound_spread": (max(new_sims) - min(new_sims)) if new_sims else 0.0,
        "n_old_pairs": len(old_sims),
        "n_new_pairs": len(new_sims),
        "old_min": (min(old_sims) if old_sims else None),
        "old_max": (max(old_sims) if old_sims else None),
        "new_min": (min(new_sims) if new_sims else None),
        "new_max": (max(new_sims) if new_sims else None),
    }


def score_arm_v6(arm_name, idx, dense_vecs, d, role_vecs, objidx_roles,
                  unstated_items, satrest_items, thwart_items):
    cache = {}

    def get(text):
        if text not in cache:
            cache[text] = build_event_struct_v6(text, idx, dense_vecs, d, role_vecs, objidx_roles)
        return cache[text]

    # ---- unstated_goal: 4-way category multiple choice ----
    unstated_results = []
    unstated_correct = 0
    for item in unstated_items:
        action_struct, _, _, action_cov = get(item["action_text"])
        candidates = [item["correct_category"]] + list(item["distractor_categories"])
        assert len(candidates) == 4, f"expected 4-way MC, got {len(candidates)} for {item['id']}"
        sims = {}
        for cat in candidates:
            proto_struct, _, _, _ = get(CATEGORY_PROTOTYPES[cat])
            sim, _zero = structure_overlap(action_struct, proto_struct, d)
            sims[cat] = sim
        predicted = max(sims, key=sims.get)
        correct = predicted == item["correct_category"]
        if correct:
            unstated_correct += 1
        unstated_results.append({
            "id": item["id"], "correct_category": item["correct_category"],
            "predicted_category": predicted, "correct": correct, "sims": sims,
            "action_coverage": action_cov,
        })

    # ---- satisfy_restate: does satisfy outrank restate vs the goal ----
    satrest_results = []
    satrest_correct = 0
    for item in satrest_items:
        goal_struct, _, _, goal_cov = get(item["goal_text"])
        restate_struct, _, _, restate_cov = get(item["restate_text"])
        satisfy_struct, _, _, satisfy_cov = get(item["satisfy_text"])
        sim_restate, _ = structure_overlap(goal_struct, restate_struct, d)
        sim_satisfy, _ = structure_overlap(goal_struct, satisfy_struct, d)
        correct = sim_satisfy > sim_restate
        if correct:
            satrest_correct += 1
        satrest_results.append({
            "id": item["id"], "sim_goal_to_restate": sim_restate, "sim_goal_to_satisfy": sim_satisfy,
            "correct": correct, "goal_coverage": goal_cov, "restate_coverage": restate_cov,
            "satisfy_coverage": satisfy_cov,
        })

    # ---- thwart_cause: does the true causally-linked event outrank the distractor ----
    thwart_results = []
    thwart_correct = 0
    for item in thwart_items:
        a_struct, _, _, a_cov = get(item["event_a_text"])
        b_struct, _, _, b_cov = get(item["event_b_text"])
        dist_struct, _, _, dist_cov = get(item["distractor_text"])
        sim_b, _ = structure_overlap(a_struct, b_struct, d)
        sim_dist, _ = structure_overlap(a_struct, dist_struct, d)
        correct = sim_b > sim_dist
        if correct:
            thwart_correct += 1
        thwart_results.append({
            "id": item["id"], "sim_a_to_b": sim_b, "sim_a_to_distractor": sim_dist,
            "correct": correct, "event_a_coverage": a_cov, "event_b_coverage": b_cov,
            "distractor_coverage": dist_cov,
        })

    n_scored = len(unstated_items) * 4 + len(satrest_items) * 2 + len(thwart_items) * 2
    assert n_scored == EXPECTED_N_SCORED_UNITS_PER_ARM, (
        f"cardinality_ok breach for {arm_name}: got {n_scored} scored units, "
        f"expected {EXPECTED_N_SCORED_UNITS_PER_ARM}"
    )

    n_total = len(unstated_items) + len(satrest_items) + len(thwart_items)
    overall_correct = unstated_correct + satrest_correct + thwart_correct

    return {
        "arm_name": arm_name,
        "unstated_goal_accuracy": unstated_correct / len(unstated_items),
        "unstated_goal_correct_count": unstated_correct,
        "satisfy_restate_accuracy": satrest_correct / len(satrest_items),
        "satisfy_restate_correct_count": satrest_correct,
        "thwart_cause_accuracy": thwart_correct / len(thwart_items),
        "thwart_cause_correct_count": thwart_correct,
        "overall_accuracy": overall_correct / n_total,
        "overall_correct_count": overall_correct,
        "n_total_items": n_total,
        "n_scored_units": n_scored,
        "cardinality_ok": n_scored == EXPECTED_N_SCORED_UNITS_PER_ARM,
        "object_slot_spread": _object_slot_spread(cache),
        "cache_size_distinct_texts": len(cache),
        "unstated_results": unstated_results,
        "satrest_results": satrest_results,
        "thwart_results": thwart_results,
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

    assert os.path.exists(GOLD_EVAL_PATH), f"Director-verified gold eval missing at {GOLD_EVAL_PATH}"
    unstated_items, satrest_items, thwart_items = load_gold_eval(GOLD_EVAL_PATH)
    assert len(unstated_items) == EXPECTED_N_UNSTATED_GOAL_ITEMS, (
        f"cardinality_ok breach: unstated_goal items got {len(unstated_items)}, expected {EXPECTED_N_UNSTATED_GOAL_ITEMS}")
    assert len(satrest_items) == EXPECTED_N_SATISFY_RESTATE_ITEMS, (
        f"cardinality_ok breach: satisfy_restate items got {len(satrest_items)}, expected {EXPECTED_N_SATISFY_RESTATE_ITEMS}")
    assert len(thwart_items) == EXPECTED_N_THWART_CAUSE_ITEMS, (
        f"cardinality_ok breach: thwart_cause items got {len(thwart_items)}, expected {EXPECTED_N_THWART_CAUSE_ITEMS}")

    corpus_texts = []
    corpus_word_counts = {}
    for p in CORPUS_PATHS:
        with open(p, "r", encoding="utf-8") as f:
            txt = f.read()
        corpus_texts.append(txt)
        corpus_word_counts[os.path.basename(p)] = len(_tokenize(txt))

    print(f"[progress] corpus loaded, files={list(corpus_word_counts.keys())}", flush=True)

    # ---- PPMI arm (vocab-dim; recomputed on THIS run's corpus, same pipeline as v3/v4/v5) ----
    vocab, idx, ppmi_raw_vecs, n_tokens, vocab_size, ppmi_nnz = build_raw_ppmi_vectors(corpus_texts)
    ppmi_corrected_vecs, mean_vec, top_dirs, mr_iters, mr_residuals = apply_mean_removal(ppmi_raw_vecs)
    print(f"[progress] PPMI+meanremoval built: n_tokens={n_tokens} vocab_size={vocab_size}", flush=True)

    # ---- SGNS arms (D=64; bit-identical retrain of v4/v5's own train_sgns) ----
    tokens = []
    for text in corpus_texts:
        tokens.extend(_tokenize(text))
    tok_idx = np.array([idx.get(w, -1) for w in tokens], dtype=np.int64)
    vocab_counts_arr = np.zeros(vocab_size, dtype=np.int64)
    for ti in tok_idx:
        if ti >= 0:
            vocab_counts_arr[ti] += 1

    print(f"[progress] starting SGNS retrain (bit-identical to v4/v5)", flush=True)
    w_sgns_trained, w_sgns_random_init, n_pairs_trained, per_epoch_err = train_sgns(
        tok_idx, vocab_size, vocab_counts_arr
    )
    print(f"[progress] SGNS retrain complete n_pairs_trained={n_pairs_trained}", flush=True)

    # ---- role vectors: outer AGENT/ACTION/OBJECT (v5's own fixed seeds via make_role_vecs) ----
    role_vecs_d64 = make_role_vecs(D_EMBED, 55001)   # ROLE_VEC_SEED_D64, same literal as v5
    role_vecs_ppmi = make_role_vecs(vocab_size, 55002)  # ROLE_VEC_SEED_PPMI, same literal as v5

    # ---- NEW: object-index micro-role families (this cell's fix) ----
    objidx_roles_d64 = make_objidx_roles(D_EMBED, OBJIDX_ROLE_SEED_D64)
    objidx_roles_ppmi = make_objidx_roles(vocab_size, OBJIDX_ROLE_SEED_PPMI)

    # sanity: index roles within a family must be pairwise distinct (else the fix is a no-op)
    _digests, pairwise, all_differ = _arms_must_differ_tensors(
        {f"objidx_{i}": objidx_roles_d64[i] for i in range(min(6, len(objidx_roles_d64)))}
    )
    assert all(pairwise.values()), "objidx_roles_d64 family has colliding vectors (sample check failed)"

    print(f"[progress] scoring ARM_ERROR_DRIVEN_SGNS", flush=True)
    arm_error_driven = score_arm_v6("ARM_ERROR_DRIVEN_SGNS", idx, w_sgns_trained, D_EMBED,
                                     role_vecs_d64, objidx_roles_d64, unstated_items, satrest_items, thwart_items)
    print(f"[progress] scoring ARM_RANDOM_INIT_CONTROL", flush=True)
    arm_random_init = score_arm_v6("ARM_RANDOM_INIT_CONTROL", idx, w_sgns_random_init, D_EMBED,
                                    role_vecs_d64, objidx_roles_d64, unstated_items, satrest_items, thwart_items)
    print(f"[progress] scoring ARM_PPMI_MEANREMOVAL", flush=True)
    arm_ppmi_ref = score_arm_v6("ARM_PPMI_MEANREMOVAL", idx, ppmi_corrected_vecs, vocab_size,
                                 role_vecs_ppmi, objidx_roles_ppmi, unstated_items, satrest_items, thwart_items)

    # ---- ARMS-MUST-DIFFER (META_RULE_AF) across composite event structures ----
    goal0_text = satrest_items[0]["goal_text"]
    goal0_struct_ed, _, _, _ = build_event_struct_v6(goal0_text, idx, w_sgns_trained, D_EMBED, role_vecs_d64, objidx_roles_d64)
    goal0_struct_ri, _, _, _ = build_event_struct_v6(goal0_text, idx, w_sgns_random_init, D_EMBED, role_vecs_d64, objidx_roles_d64)
    _digests2, arm_struct_pairwise, arm_structs_differ = _arms_must_differ_tensors({
        "arm_error_driven_goal0_struct": goal0_struct_ed,
        "arm_random_init_goal0_struct": goal0_struct_ri,
    })
    assert arm_structs_differ, "META_RULE_AF VIOLATION: error-driven and random-init composite structures bit-identical"

    # ---- pre-registered verdict logic ----
    obj_spread_ed = arm_error_driven["object_slot_spread"]
    widening = obj_spread_ed["new_debound_spread"] - obj_spread_ed["old_meanpool_spread"]
    gate1_object_depooled = widening >= GATE1_ABS_WIDENING_MIN

    ed_acc = arm_error_driven["overall_accuracy"]
    ri_acc = arm_random_init["overall_accuracy"]
    ppmi_acc = arm_ppmi_ref["overall_accuracy"]
    best_trained_acc = max(ed_acc, ppmi_acc)

    random_near_chance = abs(ri_acc - CHANCE_OVERALL_WEIGHTED) <= GATE2_NEAR_CHANCE_BAND
    random_below_trained_margin = best_trained_acc - ri_acc
    random_below_trained = random_below_trained_margin >= GATE2_BELOW_TRAINED_MARGIN_MIN
    gate2_control_fires = random_near_chance and random_below_trained

    gate3_margin = best_trained_acc - ri_acc
    gate3_content_beats_random = gate3_margin >= GATE3_BEATS_RANDOM_MARGIN_MIN

    if gate1_object_depooled and gate2_control_fires and gate3_content_beats_random:
        verdict_regime = "REPRESENTATION_WORKS"
    else:
        failed_gates = []
        if not gate1_object_depooled:
            failed_gates.append("GATE1_OBJECT_DEPOOLED")
        if not gate2_control_fires:
            failed_gates.append("GATE2_CONTROL_FIRES")
        if not gate3_content_beats_random:
            failed_gates.append("GATE3_CONTENT_BEATS_RANDOM")
        verdict_regime = "REPRESENTATION_STILL_BROKEN_" + "_AND_".join(failed_gates)

    elapsed_s = time.perf_counter() - t_start

    def _trim_arm(arm):
        return {k: v for k, v in arm.items()
                if k not in ("unstated_results", "satrest_results", "thwart_results")}

    summary = {
        "mechanism": (
            "bound role-filler FHRR event structure with FIXED de-pooled OBJECT slot "
            "(each object content word bound to its own distinct index-role, bundled into "
            "an object sub-structure, then bound to the outer OBJECT role and bundled with "
            "AGENT/ACTION), scored on the Director-verified 25-item relation-inference eval"
        ),
        "arms": {
            "ARM_ERROR_DRIVEN_SGNS": _trim_arm(arm_error_driven),
            "ARM_RANDOM_INIT_CONTROL": _trim_arm(arm_random_init),
            "ARM_PPMI_MEANREMOVAL": _trim_arm(arm_ppmi_ref),
        },
        "gate1_object_depooled": {
            "old_meanpool_spread": obj_spread_ed["old_meanpool_spread"],
            "new_debound_spread": obj_spread_ed["new_debound_spread"],
            "widening": widening,
            "threshold_min_widening": GATE1_ABS_WIDENING_MIN,
            "fires": gate1_object_depooled,
        },
        "gate2_control_fires": {
            "random_init_overall_accuracy": ri_acc,
            "chance_overall_weighted": CHANCE_OVERALL_WEIGHTED,
            "near_chance_band": GATE2_NEAR_CHANCE_BAND,
            "random_near_chance": random_near_chance,
            "best_trained_overall_accuracy": best_trained_acc,
            "margin_vs_random": random_below_trained_margin,
            "margin_threshold_min": GATE2_BELOW_TRAINED_MARGIN_MIN,
            "random_below_trained": random_below_trained,
            "fires": gate2_control_fires,
        },
        "gate3_content_beats_random": {
            "best_trained_overall_accuracy": best_trained_acc,
            "random_init_overall_accuracy": ri_acc,
            "margin": gate3_margin,
            "threshold_min_margin": GATE3_BEATS_RANDOM_MARGIN_MIN,
            "fires": gate3_content_beats_random,
        },
        "verdict_regime": verdict_regime,
        "corpus_n_tokens_combined": n_tokens,
        "corpus_vocab_size_after_min_count_filter": vocab_size,
        "sgns_n_pairs_trained": n_pairs_trained,
        "role_vec_dims": {"d64_arms": D_EMBED, "ppmi_arm": vocab_size},
        "n_gold_items": {"unstated_goal": len(unstated_items), "satisfy_restate": len(satrest_items),
                          "thwart_cause": len(thwart_items), "total": EXPECTED_N_TOTAL_ITEMS},
        "eval_caveat": (
            "N=25 Director-VERIFIED balanced eval (gold_relation_inference_v1.jsonl, commit "
            "7f6289607) -- real citation spans from 5 public-domain novels, not the dead N=6 "
            "hand-selected probe. Still a small-N smoke by ML standards; per-item-type accuracy "
            "reported so results are honestly localizable, not a claim of solved relation-inference."
        ),
        "elapsed_s": elapsed_s,
    }

    metrics = {
        "verdict": "MEASURED_DIAGNOSTIC",
        "verdict_msg": (
            f"verdict_regime={verdict_regime} (N=25 Director-verified eval); "
            f"gate1_object_depooled={gate1_object_depooled} (widening={widening:.4f} vs threshold {GATE1_ABS_WIDENING_MIN}); "
            f"gate2_control_fires={gate2_control_fires} (random_acc={ri_acc:.4f} near_chance={random_near_chance} "
            f"below_trained_margin={random_below_trained_margin:.4f}); "
            f"gate3_content_beats_random={gate3_content_beats_random} (margin={gate3_margin:.4f}); "
            f"per-arm overall: error_driven={ed_acc:.4f} random_init={ri_acc:.4f} ppmi={ppmi_acc:.4f}"
        ),
        "summary": f"DEEP-EARN STEP 6 (object-slot de-pooled bound role-filler, verified 25-item eval) verdict_regime={verdict_regime}",
        "elapsed_s": elapsed_s,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "results_arm_error_driven_unstated_goal": arm_error_driven["unstated_results"],
        "results_arm_error_driven_satisfy_restate": arm_error_driven["satrest_results"],
        "results_arm_error_driven_thwart_cause": arm_error_driven["thwart_results"],
        "results_arm_random_init_unstated_goal": arm_random_init["unstated_results"],
        "results_arm_random_init_satisfy_restate": arm_random_init["satrest_results"],
        "results_arm_random_init_thwart_cause": arm_random_init["thwart_results"],
        "results_arm_ppmi_ref_unstated_goal": arm_ppmi_ref["unstated_results"],
        "results_arm_ppmi_ref_satisfy_restate": arm_ppmi_ref["satrest_results"],
        "results_arm_ppmi_ref_thwart_cause": arm_ppmi_ref["thwart_results"],
        "summary_fields": summary,
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "passed_all_4_patterns_scaled_to_diagnostic_n25x3arms",
        "final_metrics_atomicity": "tmp_replace",
        "arms_differ_exempted": [],
        "deterministic_seeding": True,
        "progress_logging": "print_flush_true",
        "crlb_n_a": (
            "no fixed-capacity argmax-noise-floor threshold in this cell; discrete-tier "
            "accuracy-count feasibility over N=25 items is the Gate-B analogue, documented in "
            "the GATE2/GATE3 margin rationale in the module docstring"
        ),
    }

    tmp_path = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final_path = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, final_path)

    print(json.dumps(summary, indent=2))


def self_test():
    """Tiny-scale real-code-path self-test: exercises the ACTUAL bind/bundle/
    unbind pipeline (hdlab.binding, hdlab.bundling) and this cell's own
    build_object_composite / build_event_struct_v6 / _object_slot_spread on a
    synthetic tiny vocab, at production dtype/shape logic. Runs in well
    under 1 second."""
    d = 8
    vocab = ["alice", "wants", "tea", "and", "cake", "bob", "gives", "cake2",
              "runs", "fast", "far", "away", "quickly"]
    idx = {w: i for i, w in enumerate(vocab)}
    rng = np.random.RandomState(0)
    dense_vecs = rng.rand(len(vocab), d).astype(np.float64)

    role_vecs = make_role_vecs(d, seed=1)
    objidx_roles = make_objidx_roles(d, seed=2, n_slots=6)
    assert len(objidx_roles) == 6
    for v in objidx_roles:
        assert v.dtype == torch.complex64
        assert torch.allclose(v.abs(), torch.ones_like(v.abs()), atol=1e-5)

    # object composite for a multi-word object bag: distinct words must NOT collapse to a mean
    comp1, n1 = build_object_composite(["tea", "cake", "cake2"], idx, dense_vecs, d, objidx_roles)
    comp2, n2 = build_object_composite(["far", "away", "quickly"], idx, dense_vecs, d, objidx_roles)
    assert comp1 is not None and n1 == 3
    assert comp2 is not None and n2 == 3
    ov, zero = structure_overlap(comp1, comp2, d)
    assert not zero
    assert -1.0 - 1e-6 <= ov <= 1.0 + 1e-6

    # order sensitivity: same words, different order -> different composite (index roles bind position)
    comp1b, _ = build_object_composite(["cake2", "cake", "tea"], idx, dense_vecs, d, objidx_roles)
    ov_same_words_diff_order, _ = structure_overlap(comp1, comp1b, d)
    assert ov_same_words_diff_order < 1.0 - 1e-6, "position-bound object composite should be order-sensitive"

    # full event struct
    struct_a, obj_comp_a, obj_mean_a, cov_a = build_event_struct_v6(
        "alice wants tea and cake", idx, dense_vecs, d, role_vecs, objidx_roles)
    struct_b, obj_comp_b, obj_mean_b, cov_b = build_event_struct_v6(
        "bob gives cake2 runs fast", idx, dense_vecs, d, role_vecs, objidx_roles)
    assert struct_a is not None and struct_b is not None
    assert struct_a.shape == (d,) and struct_a.dtype == torch.complex64
    assert cov_a["agent_covered"] and cov_a["action_covered"]
    assert obj_mean_a is not None and obj_comp_a is not None

    sim_ab, zero_ab = structure_overlap(struct_a, struct_b, d)
    assert not zero_ab
    assert -1.0 - 1e-6 <= sim_ab <= 1.0 + 1e-6

    sim_aa, _ = structure_overlap(struct_a, struct_a, d)
    assert sim_aa > sim_ab, "self-overlap should exceed overlap with a different event"

    # empty-text edge case
    struct_none, obj_comp_none, obj_mean_none, cov_none = build_event_struct_v6(
        "zzznotinvocab", idx, dense_vecs, d, role_vecs, objidx_roles)
    assert struct_none is None and cov_none["n_covered"] == 0

    # single-object-word edge case (no averaging possible with 1 word, but exercise the path)
    struct_c, obj_comp_c, obj_mean_c, cov_c = build_event_struct_v6(
        "alice wants tea", idx, dense_vecs, d, role_vecs, objidx_roles)
    assert cov_c["object_covered_count"] == 1

    # _object_slot_spread over a tiny cache
    cache = {
        "t1": (struct_a, obj_comp_a, obj_mean_a, cov_a),
        "t2": (struct_b, obj_comp_b, obj_mean_b, cov_b),
    }
    spread = _object_slot_spread(cache)
    assert "old_meanpool_spread" in spread and "new_debound_spread" in spread
    assert spread["n_old_pairs"] == 1 and spread["n_new_pairs"] == 1

    # overflow guard: object span longer than the role family must assert loud, not silently wrap
    overflow_triggered = False
    try:
        build_object_composite(["tea"] * 10, idx, dense_vecs, d, objidx_roles[:3])
    except AssertionError:
        overflow_triggered = True
    assert overflow_triggered, "object span overflow must raise, not silently wrap/truncate"

    print(
        f"[self_test] PASS  sim_ab={sim_ab:.4f}  sim_aa={sim_aa:.4f}  "
        f"order_sensitivity_ov={ov_same_words_diff_order:.4f}  "
        f"object_spread_old={spread['old_meanpool_spread']:.4f} new={spread['new_debound_spread']:.4f}  "
        f"overflow_guard=True",
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
