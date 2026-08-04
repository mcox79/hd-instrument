# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF): WITHIN_SPAN_FLOOR vs CROSS_SPAN_BOUND
#   attribution vectors hashed and asserted non-identical (differ via the recall lift on
#   grapp_mcca_004/005). CROSS_SPAN_BOUND vs RANDOM_DEGENERATE asserted non-identical
#   (RANDOM_DEGENERATE reaches zero matches by construction; CROSS_SPAN_BOUND reaches >=1).
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb: n/a -- fixed 4-item causal discriminator, no capacity sweep; theta reused
#   bit-identical from exp_grounded_appraisal_sim_earned_v1 (digest-verified, never retrained).
# - calibration_check: default_ok_for_this_regime (WINDOW_LINES=100 declared in the prereg
#   BEFORE scoring correctness, applied uniformly, not swept/tuned per item;
#   VICTIM_ENTITY_ALIASES/RANDOM_VOCAB imported unchanged from the parent cell).
# - deterministic_seeding: torch.Generator per seed/condition/unit; sorted() iteration; no
#   hash()-seed.
# - cell_chunked: true (per (arm, seed) causal-scoring unit via tools/exp_checkpoint.py).
# - all numbers MEASURED@ tagged in the completion report, not this file.
#
# See preregs/2026-08-04_cross_span_causal_binding_v1.md for the full design.
#
# THE FIX: exp_argument_structure_patient_extraction_v1's EXTRACTED_REAL arm extracts each
# candidate's patient ONLY from its own single cited span, which structurally cannot recover
# a victim link when the harm event and the victim mention are not co-located in that span
# (confirmed 0/4, PATIENT_FIX_REJECTED_REGRESSES_CAUSAL). This cell accumulates harm-adjacent
# events across a bounded neighborhood of the WHOLE PASSAGE (hdlab.situation_model_accumulate,
# the same VET-confirmed accumulate organ, atom 29609) around each candidate span, and checks
# cross-span victim coreference (the SAME corefers_with_victim/normalize_tokens primitive,
# unchanged) against every windowed sentence instead of only the cited span -- reachability,
# not a new selector. bridge_causal_antecedent itself is imported and called UNCHANGED.
"""Cross-span causal binding: accumulates per-candidate harm-adjacent patient evidence across
a bounded passage neighborhood (not just the single cited candidate span) into a situation-
model register, and tests whether this makes the TRUE blocker's victim link reachable where
within-span extraction structurally cannot reach it. Reports RECALL (reachability) separately
from END-TO-END selection (the existing unchanged bridge/selector), per the binding-vs-
selection decomposition; a random-degenerate floor; a positive control; and an explicit
contamination/no-gold-leakage check."""
import argparse
import hashlib
import json
import os
import platform
import re
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

ANCHOR_NAME = "cross_span_causal_binding_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS_DIR = os.path.join(REPO_ROOT, "experiments")
TOOLS_DIR = os.path.join(REPO_ROOT, "tools")
for _p in (REPO_ROOT, EXPERIMENTS_DIR, TOOLS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
EARNED_METRICS_PATH = os.path.join(
    REPO_ROOT, "data", "exp_grounded_appraisal_sim_earned_v1", "metrics.json")
GOLD_PATH = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1",
    "gold_grounded_appraisal_richer_v1.jsonl")

# ---- REUSED, UNCHANGED: parent cell's patient extractor, coref-gate, victim/random tables ----
import exp_grounded_appraisal_sim_earned_v1 as sim  # noqa: E402
from exp_causal_attribution_bridging_v1 import bridge_causal_antecedent  # noqa: E402
from exp_appraisal_structure_extraction_v1 import resolve_valence_fixed as VALENCE_FN  # noqa: E402
from hdlab.coreference_resolver import normalize_tokens  # noqa: E402
from hdlab.situation_model_accumulate import make_situation_register  # noqa: E402
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402
import exp_argument_structure_patient_extraction_v1 as PATV1  # noqa: E402
import exp_learned_argstruct_parser_lccp_independent_gold_v1 as AP  # noqa: E402

SEEDS = sim.SEEDS  # [0,1,2,3,4]
EXPECTED_N_SEEDS = len(SEEDS)
TRAIN_CFG = sim.FULL_CFG
ARMS = ["WITHIN_SPAN_FLOOR", "CROSS_SPAN_BOUND", "RANDOM_DEGENERATE"]

# GIVEN, imported unchanged from the parent cell -- NOT redeclared, same tables, no new
# aliases added for this cell (no per-item tuning risk introduced here).
VICTIM_ENTITY_ALIASES = PATV1.VICTIM_ENTITY_ALIASES
RANDOM_VOCAB = PATV1.RANDOM_VOCAB
QUERY_TARGET = PATV1.QUERY_TARGET

# ONE VARIABLE (declared before any scoring): window size in lines, symmetric, uniform.
WINDOW_LINES = {"WITHIN_SPAN_FLOOR": 0, "CROSS_SPAN_BOUND": 100, "RANDOM_DEGENERATE": 100}

NOVEL_FILES = {
    "tom_sawyer": os.path.join(REPO_ROOT, "data/corpora/tom_sawyer/cleaned/tom_sawyer.clean.txt"),
    "little_women": os.path.join(REPO_ROOT, "data/corpora/little_women/cleaned/little_women.clean.txt"),
}
_LINES_CACHE = {}

# Declared field allowlist for the no-gold-leakage contamination check (asserted in self_test
# and logged in every unit's record): these are the ONLY item[...] keys this module reads.
ALLOWED_GOLD_FIELDS = frozenset(
    {"id", "item_type", "novel", "true_blocker_span", "distractor_span", "query_span"})
FORBIDDEN_GOLD_FIELDS = frozenset(
    {"true_blocker_agent", "distractor_agent", "recency_baseline_prediction",
     "recency_baseline_correct", "recency_note", "goal_owner"})


def _write_start_marker(output_dir, run_mode, expected):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected,
              "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, d):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


def load_gold_causal():
    items = []
    with open(GOLD_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return [it for it in items if it["item_type"] == "multi_candidate_causal_attribution"]


def load_earned_digests():
    with open(EARNED_METRICS_PATH, "r", encoding="utf-8") as f:
        d = json.load(f)
    return {int(k): v["arms_theta_digests"]["FULL"] for k, v in d["per_seed"].items()}


def reconstruct_full_theta(seed: int, cfg: dict):
    gen = torch.Generator().manual_seed(seed)
    cb = sim.Codebook(gen)
    g = torch.Generator().manual_seed(seed * 100 + sim.hash_variant("FULL"))
    theta = sim.train_theta(cb, g, "FULL", cfg["n_train"])
    digest = hashlib.sha256(theta.numpy().tobytes()).hexdigest()[:16]
    return cb, theta, digest


def _bridge_episode(cong, cope, cand_coh, cand_rec):
    cands = []
    for i in range(sim.N_CAND):
        if i < len(cand_coh):
            cands.append({"id_idx": 0, "coh": cand_coh[i], "rec": cand_rec[i]})
        else:
            cands.append({"id_idx": 0, "coh": 0, "rec": 0})
    return {"type": "TEXT_BRIDGE", "cong": cong, "cope": cope, "cands": cands, "pool": "eval"}


def _q(cb, theta, ep, action):
    return float(sim.phi(cb, ep, action, "FULL") @ theta)


# ---------------------------------------------------------------------------------------------
# WINDOWED CROSS-SPAN ACCUMULATION. Brain structure: DMN/Kintsch situation-model multi-event
# indexing (hdlab.situation_model_accumulate.AccumulateRegister, atom 29609) for the
# accumulate step; hippocampal relational identity-matching (coreference_resolver.
# normalize_tokens, reused verbatim as PATV1.corefers_with_victim) for the cross-span bind.
# ---------------------------------------------------------------------------------------------
def _load_novel_lines(novel: str):
    if novel not in _LINES_CACHE:
        with open(NOVEL_FILES[novel], "r", encoding="utf-8") as f:
            _LINES_CACHE[novel] = f.readlines()
    return _LINES_CACHE[novel]


def window_sentences(novel: str, span_text: str, center_line: int, window_lines: int):
    """window_lines=0: just the candidate span's own text (WITHIN_SPAN_FLOOR, one sentence).
    window_lines>0: AP.split_sents (the SAME regex sentence splitter
    exp_learned_argstruct_parser_lccp_independent_gold_v1 already uses) over a symmetric
    +/-window_lines neighborhood of the raw chapter text around the candidate span's own
    starting line -- the bounded 'local scene' the situation model accumulates over."""
    if window_lines <= 0:
        return [span_text]
    lines = _load_novel_lines(novel)
    lo = max(0, center_line - 1 - window_lines)
    hi = min(len(lines), center_line + window_lines)
    text = "".join(lines[lo:hi])
    return AP.split_sents(text)


def _stable_seed(*parts) -> int:
    """Deterministic int seed from stable parts (sha256, NOT hash()-seed, per discipline)."""
    h = hashlib.sha256("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()
    return int(h[:8], 16)


_ACCUM_CACHE = {}


def accumulate_cross_span(item_id, novel, span_text, center_line, arm, rng=None, d=256):
    """Builds one fresh situation-model register over the windowed sentences for this
    (item, candidate, arm) unit. Returns (reachable: bool, matched_sentence_previews: list,
    fidelity_margin: float|None, n_window_sentences: int, n_matched: int).

    WITHIN_SPAN_FLOOR/CROSS_SPAN_BOUND are seed-independent (no RNG consumed) -- memoized
    across the 5-seed sweep so the (deterministic) window text extraction + FHRR accumulate
    runs once per (item, candidate) instead of once per (item, candidate, seed). RANDOM_
    DEGENERATE is intentionally NOT cached (its rng draws are seed-varying by design)."""
    cache_key = (item_id, center_line, arm)
    if arm != "RANDOM_DEGENERATE" and cache_key in _ACCUM_CACHE:
        return _ACCUM_CACHE[cache_key]
    window_lines = WINDOW_LINES[arm]
    sents = window_sentences(novel, span_text, center_line, window_lines)
    gen = torch.Generator().manual_seed(_stable_seed(item_id, center_line, arm))
    reg = make_situation_register(
        role_vocab=["PATIENT_MATCH", "NO_MATCH_FILLER"], d=d, generator=gen,
        max_event_slots=max(1, len(sents)), backend="multibank")
    entity = f"{item_id}_{center_line}_{arm}"
    matched_idx = []
    matched_preview = []
    for i, s in enumerate(sents):
        if arm == "RANDOM_DEGENERATE":
            pset = PATV1.random_degenerate_patient_set(rng)
        else:
            pset = PATV1.extract_patient_set(s)
        if PATV1.corefers_with_victim(pset, item_id):
            reg.add_event(entity, "PATIENT_MATCH", i)
            matched_idx.append(i)
            matched_preview.append({"sent": s[:120], "patient_set": sorted(pset)})
    reachable = len(matched_idx) > 0
    fidelity_margin = None
    if reachable:
        # glass-box fidelity witness: decode the first matched slot back, confirm the register
        # genuinely carries PATIENT_MATCH over NO_MATCH_FILLER (a role that was never bound)
        # with positive margin -- proves the accumulate-bundle organ is doing real work here,
        # not just python-side bookkeeping.
        best, scores = reg.decode(entity, matched_idx[0])
        fidelity_margin = float(scores["PATIENT_MATCH"] - scores["NO_MATCH_FILLER"])
    result = (reachable, matched_preview, fidelity_margin, len(sents), len(matched_idx))
    if arm != "RANDOM_DEGENERATE":
        _ACCUM_CACHE[cache_key] = result
    return result


def score_causal_item(item, cb, theta, arm, rng=None):
    iid = item["id"]
    novel = item["novel"]
    true_span = item["true_blocker_span"]["text"]
    distr_span = item["distractor_span"]["text"]
    true_pos = item["true_blocker_span"]["line_range"][0]
    distr_pos = item["distractor_span"]["line_range"][0]

    rec = [1, 0] if true_pos > distr_pos else [0, 1]
    coh_oracle = [1, 0]

    true_reachable, true_matches, true_fid, true_nwin, true_nmatch = accumulate_cross_span(
        iid, novel, true_span, true_pos, arm, rng=rng)
    distr_reachable, distr_matches, distr_fid, distr_nwin, distr_nmatch = accumulate_cross_span(
        iid, novel, distr_span, distr_pos, arm, rng=rng)

    true_patient = QUERY_TARGET if true_reachable else "NOMATCH_TRUE_CAND"
    distr_patient = QUERY_TARGET if distr_reachable else "NOMATCH_DISTR_CAND"

    events = [
        {"item_id": iid + "_true", "position": 100, "agent": "TRUE_CAND",
         "patient": true_patient, "valence": VALENCE_FN(true_span)},
        {"item_id": iid + "_distr", "position": 200, "agent": "DISTR_CAND",
         "patient": distr_patient, "valence": VALENCE_FN(distr_span)},
    ]
    _prior, attributed, margin, used = bridge_causal_antecedent(QUERY_TARGET, 300, events)
    if attributed == "TRUE_CAND":
        coh_real = [1, 0]
    elif attributed == "DISTR_CAND":
        coh_real = [0, 1]
    else:
        coh_real = [0, 0]

    ep_a = _bridge_episode("HURT", "HIGH", coh_oracle, rec)
    ep_b = _bridge_episode("HURT", "HIGH", coh_real, rec)
    qa0, qa1 = _q(cb, theta, ep_a, sim.A_HARM0 + 0), _q(cb, theta, ep_a, sim.A_HARM0 + 1)
    qb0, qb1 = _q(cb, theta, ep_b, sim.A_HARM0 + 0), _q(cb, theta, ep_b, sim.A_HARM0 + 1)
    pred_a = 0 if qa0 > qa1 else (1 if qa1 > qa0 else -1)
    pred_b = 0 if qb0 > qb1 else (1 if qb1 > qb0 else -1)

    return {
        "id": iid, "arm": arm,
        "recall_true": true_reachable, "recall_distr": distr_reachable,
        "n_window_sentences_true": true_nwin, "n_matched_true": true_nmatch,
        "n_window_sentences_distr": distr_nwin, "n_matched_distr": distr_nmatch,
        "fidelity_margin_true": true_fid, "fidelity_margin_distr": distr_fid,
        "true_matches_preview": true_matches[:3], "distr_matches_preview": distr_matches[:3],
        "arm_a_pred_slot": pred_a, "arm_a_correct": pred_a == 0,
        "arm_b_pred_slot": pred_b, "arm_b_correct": pred_b == 0,
        "arm_b_attributed": attributed, "end_to_end_correct": attributed == "TRUE_CAND",
        "used_contamination": {
            "reads_true_blocker_agent_label": False, "reads_recency_fields": False,
            "victim_aliases_declared": VICTIM_ENTITY_ALIASES.get(iid, []),
            "window_lines": WINDOW_LINES[arm], "bridge_used": used,
        },
    }


def run_arm_seed(arm, seed):
    cb, theta, digest = reconstruct_full_theta(seed, TRAIN_CFG)
    items = load_gold_causal()
    if arm == "RANDOM_DEGENERATE":
        gen = torch.Generator().manual_seed(seed * 1000 + 13)
        rows = [score_causal_item(it, cb, theta, arm, rng=gen) for it in items]
    else:
        rows = [score_causal_item(it, cb, theta, arm) for it in items]
    return {"arm": arm, "seed": seed, "theta_digest": digest, "rows": rows}


# ---------------------------------------------------------------------------------------------
def arms_must_differ(per_arm_seed):
    """META_RULE_AF on the mechanism's actual output (attribution + recall_true/distr), not the
    rec-contaminated downstream pred_slot.

    The ARM UNDER TEST (CROSS_SPAN_BOUND) MUST differ from BOTH controls -- that is the real
    'the variable does something' requirement, and it is enforced hard. The
    {WITHIN_SPAN_FLOOR, RANDOM_DEGENERATE} pair is DECLARED EXEMPT: on this 4-item slice every
    item is cross-span by construction, so within-span extraction reaches ZERO victim-coreferent
    patients (all-None attribution, all-False recall) -- exactly what RANDOM_DEGENERATE also
    yields (it cannot corefer by construction). Their collapse to bit-identical is the
    INFORMATIVE floor result (within-span is genuinely 0/4, same as random), NOT a masking of
    the variable; disclosed here, exactly as the parent cell
    (exp_argument_structure_patient_extraction_v1) exempted its EXTRACTED_REAL vs
    RANDOM_DEGENERATE pair on the same all-zero-on-4-items grounds. If a future eval grows to
    include within-span-recoverable items this exemption stops applying (the floor would then
    differ from random) -- it is not a blanket waiver."""
    vecs = {a: [] for a in ARMS}
    for (arm, seed), rec in sorted(per_arm_seed.items()):
        for r in rec["rows"]:
            vecs[arm].append(f"{r['arm_b_attributed']}|{r['recall_true']}|{r['recall_distr']}")
    digests = {a: hashlib.sha256("|".join(v).encode()).hexdigest() for a, v in vecs.items()}
    exempt = {frozenset(("WITHIN_SPAN_FLOOR", "RANDOM_DEGENERATE"))}
    # Hard requirement: the arm under test differs from BOTH controls (no exemption).
    for control in ("WITHIN_SPAN_FLOOR", "RANDOM_DEGENERATE"):
        if digests["CROSS_SPAN_BOUND"] == digests[control]:
            raise AssertionError(
                f"META_RULE_AF VIOLATION: arm-under-test 'CROSS_SPAN_BOUND' bit-identical to "
                f"control {control!r} (hash={digests['CROSS_SPAN_BOUND']}) -- the window variable "
                f"produced no measurable change, cell is vacuous")
    for i, a in enumerate(ARMS):
        for b in ARMS[i + 1:]:
            if digests[a] == digests[b] and frozenset((a, b)) not in exempt:
                raise AssertionError(
                    f"META_RULE_AF VIOLATION: {a!r} and {b!r} bit-identical (hash={digests[a]})")
    return digests


def _rate(rows, key):
    n = len(rows)
    return (sum(1 for r in rows if r[key]) / n) if n else 0.0, n


def _det_count(per_arm_seed, arm, key):
    per_item = {}
    for s in SEEDS:
        for r in per_arm_seed[(arm, s)]["rows"]:
            per_item.setdefault(r["id"], 0)
            per_item[r["id"]] += int(r[key])
    n_full = sum(1 for c in per_item.values() if c == len(SEEDS))
    return n_full, per_item


def aggregate_and_verdict(per_arm_seed, earned_digests):
    seeds = sorted(SEEDS)

    def rows_of(arm):
        out = []
        for s in seeds:
            out.extend(per_arm_seed[(arm, s)]["rows"])
        return out

    within_rows = rows_of("WITHIN_SPAN_FLOOR")
    cross_rows = rows_of("CROSS_SPAN_BOUND")
    rand_rows = rows_of("RANDOM_DEGENERATE")

    digest_matches = {s: per_arm_seed[("WITHIN_SPAN_FLOOR", s)]["theta_digest"] == earned_digests.get(s)
                       for s in seeds}
    all_digests_match = all(digest_matches.values())

    recall_true_within, _ = _rate(within_rows, "recall_true")
    recall_true_cross, _ = _rate(cross_rows, "recall_true")
    recall_true_rand, _ = _rate(rand_rows, "recall_true")
    recall_distr_within, _ = _rate(within_rows, "recall_distr")
    recall_distr_cross, _ = _rate(cross_rows, "recall_distr")
    recall_distr_rand, _ = _rate(rand_rows, "recall_distr")

    e2e_within, _ = _rate(within_rows, "end_to_end_correct")
    e2e_cross, _ = _rate(cross_rows, "end_to_end_correct")
    e2e_rand, _ = _rate(rand_rows, "end_to_end_correct")

    det_recall_true_within, det_recall_true_within_items = _det_count(per_arm_seed, "WITHIN_SPAN_FLOOR", "recall_true")
    det_recall_true_cross, det_recall_true_cross_items = _det_count(per_arm_seed, "CROSS_SPAN_BOUND", "recall_true")
    det_recall_true_rand, det_recall_true_rand_items = _det_count(per_arm_seed, "RANDOM_DEGENERATE", "recall_true")

    det_e2e_within, det_e2e_within_items = _det_count(per_arm_seed, "WITHIN_SPAN_FLOOR", "end_to_end_correct")
    det_e2e_cross, det_e2e_cross_items = _det_count(per_arm_seed, "CROSS_SPAN_BOUND", "end_to_end_correct")
    det_e2e_rand, det_e2e_rand_items = _det_count(per_arm_seed, "RANDOM_DEGENERATE", "end_to_end_correct")

    arm_a_within, _ = _rate(within_rows, "arm_a_correct")
    arm_a_cross, _ = _rate(cross_rows, "arm_a_correct")
    arm_a_rand, _ = _rate(rand_rows, "arm_a_correct")
    positive_control_ok = (arm_a_within == 1.0 and arm_a_cross == 1.0 and arm_a_rand == 1.0)

    negctrl_ok = (det_recall_true_rand == 0 and det_e2e_rand == 0)
    floor_ok = det_recall_true_within <= 1  # established floor: WITHIN_SPAN recovers at most one
    # item's local extraction incidentally (grapp_mcca_004/005 style single-slot literal match).

    recall_lift = det_recall_true_cross > det_recall_true_within
    e2e_lift = det_e2e_cross > det_e2e_within

    if not all_digests_match:
        verdict = "GATE_FAILED_THETA_NOT_REUSED_DIGEST_MISMATCH"
    elif not positive_control_ok:
        verdict = "GATE_FAILED_POSITIVE_CONTROL"
    elif not negctrl_ok:
        verdict = "GATE_FAILED_NEGATIVE_CONTROL"
    elif recall_lift and e2e_lift:
        verdict = "CROSS_SPAN_BINDING_LIFTS_RECALL_AND_SELECTION"
    elif recall_lift and not e2e_lift:
        verdict = "CROSS_SPAN_BINDING_LIFTS_RECALL_SELECTION_UNRESOLVED"
    else:
        verdict = "CROSS_SPAN_BINDING_NO_RECALL_LIFT"

    summary = (
        f"RECALL_TRUE det_items within={det_recall_true_within} cross={det_recall_true_cross} "
        f"random={det_recall_true_rand} | RECALL_DISTR rate within={recall_distr_within:.3f} "
        f"cross={recall_distr_cross:.3f} random={recall_distr_rand:.3f} | "
        f"END_TO_END det_items within={det_e2e_within} cross={det_e2e_cross} random={det_e2e_rand} "
        f"| positive_control_ok={positive_control_ok} negative_control_ok={negctrl_ok} "
        f"theta_reuse_digest_match={all_digests_match}"
    )
    return {
        "verdict": verdict, "verdict_msg": f"{verdict}: {summary}", "summary": summary,
        "contamination_check": {
            "all_theta_digests_match_earned_run": all_digests_match,
            "per_seed_digest_match": digest_matches,
            "allowed_gold_fields": sorted(ALLOWED_GOLD_FIELDS),
            "forbidden_gold_fields_never_read": sorted(FORBIDDEN_GOLD_FIELDS),
        },
        "means": {
            "recall_true_rate_within": recall_true_within,
            "recall_true_rate_cross": recall_true_cross,
            "recall_true_rate_random": recall_true_rand,
            "recall_distr_rate_within": recall_distr_within,
            "recall_distr_rate_cross": recall_distr_cross,
            "recall_distr_rate_random": recall_distr_rand,
            "end_to_end_correct_rate_within": e2e_within,
            "end_to_end_correct_rate_cross": e2e_cross,
            "end_to_end_correct_rate_random": e2e_rand,
            "deterministic_recall_true_items": {
                "WITHIN_SPAN_FLOOR": det_recall_true_within, "CROSS_SPAN_BOUND": det_recall_true_cross,
                "RANDOM_DEGENERATE": det_recall_true_rand},
            "deterministic_end_to_end_items": {
                "WITHIN_SPAN_FLOOR": det_e2e_within, "CROSS_SPAN_BOUND": det_e2e_cross,
                "RANDOM_DEGENERATE": det_e2e_rand},
            "per_item_recall_true_counts": {
                "WITHIN_SPAN_FLOOR": det_recall_true_within_items, "CROSS_SPAN_BOUND": det_recall_true_cross_items,
                "RANDOM_DEGENERATE": det_recall_true_rand_items},
            "per_item_end_to_end_counts": {
                "WITHIN_SPAN_FLOOR": det_e2e_within_items, "CROSS_SPAN_BOUND": det_e2e_cross_items,
                "RANDOM_DEGENERATE": det_e2e_rand_items},
            "arm_a_positive_control_rate": {
                "WITHIN_SPAN_FLOOR": arm_a_within, "CROSS_SPAN_BOUND": arm_a_cross,
                "RANDOM_DEGENERATE": arm_a_rand},
        },
        "gates": {
            "positive_control_ok": positive_control_ok,
            "negative_control_ok": negctrl_ok,
            "within_span_floor_stays_low": floor_ok,
            "recall_lift_present": recall_lift,
            "end_to_end_lift_present": e2e_lift,
        },
        "per_item_seed0_examples": {
            "CROSS_SPAN_BOUND": {
                r["id"]: {
                    "recall_true": r["recall_true"], "recall_distr": r["recall_distr"],
                    "attributed": r["arm_b_attributed"], "end_to_end_correct": r["end_to_end_correct"],
                    "n_window_sentences_true": r["n_window_sentences_true"],
                    "n_matched_true": r["n_matched_true"],
                    "fidelity_margin_true": r["fidelity_margin_true"],
                    "true_matches_preview": r["true_matches_preview"],
                }
                for r in per_arm_seed[("CROSS_SPAN_BOUND", 0)]["rows"]
            },
            "WITHIN_SPAN_FLOOR": {
                r["id"]: {"recall_true": r["recall_true"], "recall_distr": r["recall_distr"],
                          "attributed": r["arm_b_attributed"], "end_to_end_correct": r["end_to_end_correct"]}
                for r in per_arm_seed[("WITHIN_SPAN_FLOOR", 0)]["rows"]
            },
        },
        "honest_caveats": [
            "n=4 causal items, all cross-span by construction (the only real gold slice "
            "available for this phenomenon) -- a tiny-n pilot, not a powered eval; a "
            "binomial test at n=4 cannot reject random at conventional alpha even at 4/4.",
            "WINDOW_LINES=100 was chosen once a priori from a design-time probe over the "
            "reused extraction+coref primitives only (no scoring/selector code exercised in "
            "that probe) and applied uniformly; it has not been validated on independent "
            "cross-span gold -- flagged as a construction-risk parameter, not a landed one.",
            "The windowed-accumulation ingredient (this cell's only new code) has no "
            "independent gold of its own; only its two REUSED sub-primitives (per-sentence "
            "extraction, victim coreference) carry the parent cell's n=100 anti-overfit "
            "validation. Recommend growing the multi_candidate_causal_attribution eval "
            "before treating any positive verdict here as more than a pilot.",
            "This cell tests RECALL/reachability only; the coherence-SELECTOR (M_backward, "
            "Gap 1 in the 2026-08-03 causal-coherence research drill) is deliberately not "
            "built here -- the existing _pick_strict_cb-backed selector is reused UNCHANGED "
            "and is recency-biased by construction (DISTR_CAND is always encoded at the "
            "higher synthetic position 200 > TRUE_CAND's 100), so an end-to-end lift was NOT "
            "expected even if recall lifts; see verdict band definitions.",
        ],
    }


def out_dir_for(run_mode):
    return OUTPUT_DIR if run_mode == "full" else f"{OUTPUT_DIR}_{run_mode}"


def run(run_mode):
    t0 = time.perf_counter()
    output_dir = out_dir_for(run_mode)
    n_units = len(ARMS) * len(SEEDS)
    _write_start_marker(output_dir, run_mode, n_units)
    earned_digests = load_earned_digests()

    done = completed_units(output_dir)
    for arm in ARMS:
        for seed in SEEDS:
            k = unit_key("causal", arm, seed)
            if k in done:
                print(f"[resume] arm={arm} seed={seed} already done, skipping", flush=True)
                continue
            ts = time.perf_counter()
            res = run_arm_seed(arm, seed)
            record_unit(output_dir, k, res)
            print(f"[progress] arm={arm} seed={seed} done in {time.perf_counter()-ts:.1f}s",
                  flush=True)

    units = load_units(output_dir)
    per_arm_seed = {}
    for k, v in units.items():
        parts = k.split("|")
        if parts[0] == "causal":
            per_arm_seed[(parts[1], int(parts[2]))] = v

    if len(per_arm_seed) != n_units:
        raise AssertionError(
            f"META_RULE_H CARDINALITY BREACH: got {len(per_arm_seed)} units, expected {n_units}")

    arm_digests = arms_must_differ(per_arm_seed)
    agg = aggregate_and_verdict(per_arm_seed, earned_digests)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = {"seeds": SEEDS, "train_cfg": TRAIN_CFG, "arms": ARMS,
                     "window_lines": WINDOW_LINES, "victim_entity_aliases": VICTIM_ENTITY_ALIASES,
                     "random_vocab": RANDOM_VOCAB}
    agg["expected_n_units"] = n_units
    agg["measured_n_units"] = len(per_arm_seed)
    agg["cardinality_ok"] = True
    agg["arms_differ_verified"] = True
    agg["arm_digests"] = arm_digests
    agg["arms_differ_exempted"] = [["WITHIN_SPAN_FLOOR", "RANDOM_DEGENERATE"]]
    agg["arms_differ_note"] = (
        "WITHIN_SPAN_FLOOR==RANDOM_DEGENERATE bit-identical is the disclosed, expected floor "
        "collapse (both reach zero victim-coref on all 4 cross-span items); the arm under test "
        "CROSS_SPAN_BOUND is hard-required to differ from both and does.")
    agg["per_arm_seed_causal"] = {f"{a}|{s}": v for (a, s), v in per_arm_seed.items()}
    _write_metrics(output_dir, agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.1f}s", flush=True)
    return agg


# ----------------------------------------------------------------------------- self-test
def self_test():
    """Asserts the TRUE invariants of cross-span causal binding (honest, not force-passing):
    (1) theta reuse digest matches earned cell for seed 0 (bit-identical reuse, no retrain).
    (2) RANDOM_VOCAB is disjoint from every declared victim alias (imported, re-verified here).
    (3) window_sentences(window=0) returns exactly the candidate span's own text (the floor
        really is the same mechanism with window collapsed to zero, not a separate reader).
    (4) grapp_mcca_005 TRUE candidate becomes recall_true=True under CROSS_SPAN_BOUND at the
        declared WINDOW_LINES=100 (measured reachability lift on at least one item -- if this
        ever goes False the windowing mechanism has regressed/broken, not just underperformed).
    (5) RANDOM_DEGENERATE never reaches recall_true=True on any item (structural negative floor).
    (6) the mechanism's actual output (recall_true + attribution) differs between
        WITHIN_SPAN_FLOOR and CROSS_SPAN_BOUND (arms-must-differ on the real signal).
    (7) no forbidden gold field name appears in this module's source text (static contamination
        guard -- catches an accidental future read, not just today's code)."""
    earned_digests = load_earned_digests()
    cb_full, theta_full, digest_full = reconstruct_full_theta(0, TRAIN_CFG)
    assert digest_full == earned_digests[0], (
        f"theta reuse FAILED: reconstructed digest {digest_full} != earned {earned_digests[0]}")

    all_alias_tokens = set()
    for aliases in VICTIM_ENTITY_ALIASES.values():
        for a in aliases:
            all_alias_tokens |= normalize_tokens(a)
    for w in RANDOM_VOCAB:
        assert w not in all_alias_tokens, f"RANDOM_VOCAB word {w!r} collides with a victim alias"

    items = load_gold_causal()
    by_id = {it["id"]: it for it in items}

    span0 = window_sentences("tom_sawyer", "hello world.", 100, 0)
    assert span0 == ["hello world."], f"window=0 must return exactly the span text, got {span0}"

    it005 = by_id["grapp_mcca_005"]
    true_reachable, matches, fid, nwin, nmatch = accumulate_cross_span(
        "grapp_mcca_005", it005["novel"], it005["true_blocker_span"]["text"],
        it005["true_blocker_span"]["line_range"][0], "CROSS_SPAN_BOUND")
    assert true_reachable, (
        f"expected grapp_mcca_005 TRUE candidate to become recall_true=True under "
        f"CROSS_SPAN_BOUND (window={WINDOW_LINES['CROSS_SPAN_BOUND']}), got False "
        f"(n_window_sentences={nwin})")
    assert fid is not None and fid > 0.0, (
        f"expected a positive glass-box fidelity margin on the matched slot, got {fid}")

    gen = torch.Generator().manual_seed(999)
    for iid, it in by_id.items():
        r, _m, _f, _nw, _nm = accumulate_cross_span(
            iid, it["novel"], it["true_blocker_span"]["text"],
            it["true_blocker_span"]["line_range"][0], "RANDOM_DEGENERATE", rng=gen)
        assert not r, f"RANDOM_DEGENERATE must never reach recall_true=True, got True on {iid}"
        r2, _m2, _f2, _nw2, _nm2 = accumulate_cross_span(
            iid, it["novel"], it["distractor_span"]["text"],
            it["distractor_span"]["line_range"][0], "RANDOM_DEGENERATE", rng=gen)
        assert not r2, f"RANDOM_DEGENERATE must never reach recall_distr=True, got True on {iid}"

    r_within = score_causal_item(it005, cb_full, theta_full, "WITHIN_SPAN_FLOOR")
    r_cross = score_causal_item(it005, cb_full, theta_full, "CROSS_SPAN_BOUND")
    assert (r_within["recall_true"], r_within["arm_b_attributed"]) != \
           (r_cross["recall_true"], r_cross["arm_b_attributed"]), (
        "expected WITHIN_SPAN_FLOOR and CROSS_SPAN_BOUND to differ on grapp_mcca_005's "
        "actual mechanism output (recall_true/attribution), got identical")

    src = open(__file__, "r", encoding="utf-8").read()
    for field in FORBIDDEN_GOLD_FIELDS:
        # allowed only inside the FORBIDDEN_GOLD_FIELDS declaration itself
        occurrences = src.count(f'"{field}"')
        assert occurrences <= 1, (
            f"forbidden gold field {field!r} appears {occurrences} times in source "
            f"(expected exactly 1, inside the FORBIDDEN_GOLD_FIELDS declaration only)")

    print(f"[self-test] mcca_005 within={r_within['recall_true']}/{r_within['arm_b_attributed']} "
          f"cross={r_cross['recall_true']}/{r_cross['arm_b_attributed']} fidelity={fid:.4f}",
          flush=True)
    print(f"[SELFTEST PASS] theta_digest_match={digest_full == earned_digests[0]}", flush=True)
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        ok = self_test()
        raise SystemExit(0 if ok else 1)
    if args.smoke:
        run("smoke")
        raise SystemExit(0)
    run("full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash(OUTPUT_DIR, e)
        raise
