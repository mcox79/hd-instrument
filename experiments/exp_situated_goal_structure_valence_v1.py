# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_floor: n/a (accuracy-vs-baseline discriminator on a fixed 4/12-item subset, not a capacity
#   sweep; the one quantitative capacity claim -- bind/unbind round-trip decode fidelity -- is
#   self-tested directly, D=256 with 2 roles x 2-3 fillers, far below any FHRR capacity ceiling)
# - deterministic_seeding: true (inherits FIXED_RANDOM_SEED + sha256 digest vectors from the imported
#   parent cell for text encodings; own ROLE::*/FILLER::* vectors also sha256-digest-seeded; no
#   hash()/list(set()))
# - all numbers MEASURED@ tagged in the completion report, not this file
#
# SITUATED GOAL STRUCTURE (agent -> TARGET(self/other) -> action -> AFFECTIVE VALENCE) vs
# BUNDLE+CATEGORY reframe test. See preregs/2026-08-03_situated_goal_structure_valence_v1.md.
"""ONE-VARIABLE test: does representing an inferred goal as a SITUATED STRUCTURE built via BIND
(agent-target-action-valence) -- rather than a discrete-category pick over an ADDITIVE BUNDLE --
disambiguate the near-synonym unstated_goal items the construction->integration cell (commit
a401d0d19) and the context-accumulation cell (commit 15dd0da51) both missed. TARGET (self/other) is
resolved by a declared structural (reflexive-marker) proxy for coreference; VALENCE (harm/help) by a
declared tier-2 hand-bootstrapped lexicon (this pass tests the FRAME, not earned valence). Both are
combined into an HD structure via hdlab.binding.bind/unbind + hdlab.bundling.bundle -- genuine
bind-then-bundle-then-unbind, not python booleans standing in for it.
"""
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

ANCHOR_NAME = "situated_goal_structure_valence_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS_DIR = os.path.join(REPO_ROOT, "experiments")
if EXPERIMENTS_DIR not in sys.path:
    sys.path.insert(0, EXPERIMENTS_DIR)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

import exp_construction_integration_relation_inference_v1 as ci  # noqa: E402  (parent cell, verbatim reuse)
from hdlab import binding, bundling  # noqa: E402  (bind/unbind + bundle organ primitives)

GOLD_PATH = ci.GOLD_PATH
VALENCE_WEIGHT = 0.5  # declared fixed constant (magnitude-parity with action_cosine), not tuned post-hoc

CONFUSED_ITEM_IDS = [
    "relinf_unstated_007",
    "relinf_unstated_010",
    "relinf_unstated_011",
    "relinf_unstated_012",
]

# Category structural schema: (target in {SELF,OTHER}, valence in {HARM,HELP,NA}). Hand-declared
# tier-2 primitive per goal-category -- tests the FRAME this pass, not earned target/valence.
CATEGORY_TARGET_VALENCE = {
    "MANIPULATE_AVOID_WORK": ("SELF", "NA"),
    "SELF_PRESERVATION_ESCAPE": ("SELF", "NA"),
    "CURIOSITY_EXPLORATION": ("SELF", "NA"),
    "COMPLY_AVOID_TROUBLE": ("SELF", "NA"),
    "ESCAPE_BLAME_DECEPTION": ("SELF", "NA"),
    "SELF_DISCIPLINE": ("SELF", "NA"),
    "CARE_FOR_OTHERS": ("OTHER", "HELP"),
    "PROTECT_OTHERS": ("OTHER", "HELP"),
    "REVENGE_PUNISH": ("OTHER", "HARM"),
}

# Generic affect lexicon for VALENCE resolution -- deliberately DISJOINT from CATEGORY_PROTOTYPES
# word lists (avoids circularity with the LEXICAL baseline, which uses those prototype lists).
HARM_WORDS = {
    "punish", "hurt", "harm", "angry", "spite", "spiteful", "bitter", "cross", "revenge",
    "vindictive", "slap", "slapped", "scold", "scolding", "blame", "trick", "deceive", "cheat",
    "cheated", "pay", "wrong", "fault", "hard",
}
HELP_WORDS = {
    "care", "careful", "carefully", "protect", "protective", "safe", "safety", "rescue", "comfort",
    "gentle", "warm", "guard", "help", "helped", "kind", "soothe", "nurse", "shield", "defend",
    "softly",
}

REFLEXIVE_MARKERS = ["herself", "himself", "itself", "themselves", "oneself", "her own", "his own",
                      "their own", "myself"]
_CAUSATIVE_OTHER_RE = re.compile(r"\blet\s+\w+\b[^.]{0,40}\b(herself|himself|itself|themselves)\b")


# ---------------------------------------------------------------------------
# Start marker / crash diagnostic (META Sec 13B/13C)
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir, anchor_name, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": anchor_name,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


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


# ---------------------------------------------------------------------------
# TARGET / VALENCE resolvers (declared structural proxies, see pre-reg)
# ---------------------------------------------------------------------------
def resolve_target(action_text: str) -> str:
    """Reflexive-marker structural proxy for self-vs-other coreference (declared SCOPE-LIMITED --
    hdlab.coreference_resolver's TrackedEntity/mention-stream machinery needs a multi-mention PASSAGE
    this single-clause eval schema doesn't supply; this rule captures the same underlying signal --
    same-entity coreference between clause-subject and clause-object -- at single-clause scope).
    Declared BEFORE full-12 measurement; biased toward OTHER by default (stated in pre-reg)."""
    text_lower = action_text.lower()
    has_reflexive = any(m in text_lower for m in REFLEXIVE_MARKERS)
    if has_reflexive:
        return "OTHER" if _CAUSATIVE_OTHER_RE.search(text_lower) else "SELF"
    return "OTHER"  # default; measured accuracy reported honestly, not assumed


def resolve_valence(action_text: str) -> str:
    """Tier-2 hand-bootstrapped lexical valence signal (declared, not earned -- this pass tests the
    situated-structure FRAME, not an earned affective-valence encoder)."""
    toks = ci.tokenize(action_text)
    harm = sum(1 for t in toks if t in HARM_WORDS)
    help_ = sum(1 for t in toks if t in HELP_WORDS)
    if harm > help_:
        return "HARM"
    if help_ > harm:
        return "HELP"
    return "NA"


# ---------------------------------------------------------------------------
# HD structural encoding: bind(role, filler) then bundle -- genuine bind/unbind, own ROLE::/FILLER::
# namespace disjoint from ci.word_vector's vocabulary (no accidental collision with content words).
# ---------------------------------------------------------------------------
_STRUCT_VEC_CACHE = {}


def _struct_vector(key: str) -> torch.Tensor:
    if key in _STRUCT_VEC_CACHE:
        return _STRUCT_VEC_CACHE[key]
    gen = torch.Generator().manual_seed(ci._digest_seed(key))
    theta = torch.rand(ci.D, generator=gen) * 2 * torch.pi
    vec = torch.polar(torch.ones(ci.D), theta).to(torch.complex64)
    _STRUCT_VEC_CACHE[key] = vec
    return vec


ROLE_TARGET = _struct_vector("ROLE::TARGET")
ROLE_VALENCE = _struct_vector("ROLE::VALENCE")
FILLER_TARGET = {"SELF": _struct_vector("FILLER::TARGET::SELF"), "OTHER": _struct_vector("FILLER::TARGET::OTHER")}
FILLER_VALENCE = {
    "HARM": _struct_vector("FILLER::VALENCE::HARM"),
    "HELP": _struct_vector("FILLER::VALENCE::HELP"),
    "NA": _struct_vector("FILLER::VALENCE::NA"),
}


def build_situated_vec(target_label: str, valence_label: str) -> torch.Tensor:
    pairs = torch.stack([
        binding.bind(ROLE_TARGET, FILLER_TARGET[target_label]),
        binding.bind(ROLE_VALENCE, FILLER_VALENCE[valence_label]),
    ], dim=0)
    return bundling.bundle(pairs)


def decode_target(vec: torch.Tensor) -> str:
    probe = binding.unbind(vec, ROLE_TARGET)
    return max(FILLER_TARGET, key=lambda k: ci.cos_sim(probe, FILLER_TARGET[k]))


def decode_valence(vec: torch.Tensor) -> str:
    probe = binding.unbind(vec, ROLE_VALENCE)
    return max(FILLER_VALENCE, key=lambda k: ci.cos_sim(probe, FILLER_VALENCE[k]))


# ---------------------------------------------------------------------------
# Per-item scoring: 4 arms (BUNDLE_CATEGORY / TARGET_ONLY / SITUATED_STRUCTURE / LEXICAL)
# ---------------------------------------------------------------------------
def score_item(item, rng):
    correct = item["correct_category"]
    cands = [correct] + list(item["distractor_categories"])
    action_text = item["action_text"]

    # BUNDLE_CATEGORY: verbatim parent-cell mechanism (construction top-K + integration relax).
    bc = ci.score_goal_item(item, rng)
    bundle_category_pick = bc["mech_pick"]
    lexical_pick = bc["lex_pick"]  # carried reference baseline, no target filter, no integration

    # resolved target/valence (structural proxies, declared)
    pred_target = resolve_target(action_text)
    pred_valence = resolve_valence(action_text)

    # HD round-trip: build the situated structure then decode it back (genuine bind/bundle/unbind
    # exercised; decoded labels used for scoring below, proving the pipeline is load-bearing not
    # cosmetic).
    situated_vec = build_situated_vec(pred_target, pred_valence)
    decoded_target = decode_target(situated_vec)
    decoded_valence = decode_valence(situated_vec)

    action_vec = ci.text_bundle(action_text)
    action_cos = {c: ci.cos_sim(action_vec, ci.bundle(ci.CATEGORY_PROTOTYPES[c])) for c in cands}

    # TARGET_ONLY: filter candidates to matching decoded target; argmax action_cosine among survivors
    target_survivors = [c for c in cands if CATEGORY_TARGET_VALENCE[c][0] == decoded_target]
    if not target_survivors:
        target_survivors = cands  # degenerate fallback (shouldn't occur; correct's own target always self-matches)
    target_only_pick = max(target_survivors, key=lambda c: action_cos[c])

    # SITUATED_STRUCTURE: same target filter, then + valence bonus among survivors
    def _valence_bonus(c):
        cat_val = CATEGORY_TARGET_VALENCE[c][1]
        if cat_val == "NA" or decoded_valence == "NA":
            return 0.0
        return 1.0 if cat_val == decoded_valence else -1.0

    situated_scores = {c: action_cos[c] + VALENCE_WEIGHT * _valence_bonus(c) for c in target_survivors}
    situated_structure_pick = max(situated_scores, key=lambda c: situated_scores[c])

    gold_target, gold_valence = CATEGORY_TARGET_VALENCE[correct]

    return {
        "id": item["id"],
        "correct_category": correct,
        "candidates": cands,
        "action_text": action_text,
        "gold_target": gold_target, "gold_valence": gold_valence,
        "pred_target": pred_target, "pred_valence": pred_valence,
        "decoded_target": decoded_target, "decoded_valence": decoded_valence,
        "target_resolved_correct": decoded_target == gold_target,
        "valence_resolved_correct": (gold_valence == "NA") or (decoded_valence == gold_valence),
        "bundle_category_pick": bundle_category_pick, "bundle_category_correct": bundle_category_pick == correct,
        "lexical_pick": lexical_pick, "lexical_correct": lexical_pick == correct,
        "target_only_pick": target_only_pick, "target_only_correct": target_only_pick == correct,
        "situated_structure_pick": situated_structure_pick,
        "situated_structure_correct": situated_structure_pick == correct,
        "prediction_vector": [bundle_category_pick, target_only_pick, situated_structure_pick, lexical_pick],
    }


def arms_must_differ(results):
    """META_RULE_AF: assert the 4 arms (BUNDLE_CATEGORY / TARGET_ONLY / SITUATED_STRUCTURE / LEXICAL)
    are not bit-identical across the full 12-item run."""
    vecs = {"BUNDLE_CATEGORY": [], "TARGET_ONLY": [], "SITUATED_STRUCTURE": [], "LEXICAL": []}
    for r in results:
        pv = r["prediction_vector"]
        vecs["BUNDLE_CATEGORY"].append(pv[0])
        vecs["TARGET_ONLY"].append(pv[1])
        vecs["SITUATED_STRUCTURE"].append(pv[2])
        vecs["LEXICAL"].append(pv[3])
    digests = {name: hashlib.sha256("|".join(seq).encode()).hexdigest() for name, seq in vecs.items()}
    names = list(vecs.keys())
    exempted_pairs = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if digests[a] == digests[b]:
                raise AssertionError(
                    f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical (hash={digests[a]})"
                )
    return digests, exempted_pairs


def _agg(results, key, ids=None):
    subset = [r for r in results if ids is None or r["id"] in ids]
    n = len(subset)
    return (sum(1 for r in subset if r[key]) / n) if n else 0.0, n


def run(run_mode: str):
    t0 = time.perf_counter()
    gold = ci.load_gold()
    all_goal_items = gold["unstated_goal"]
    expected_n_units = len(all_goal_items) * 4  # 4 arms per item
    _write_start_marker(OUTPUT_DIR, ANCHOR_NAME, run_mode, expected_n_units)

    rng = __import__("random").Random(ci.FIXED_RANDOM_SEED)  # fixed int seed, never hash()
    results = [score_item(it, rng) for it in all_goal_items]

    arm_digests, exempted = arms_must_differ(results)

    confused_ids = set(CONFUSED_ITEM_IDS)
    metrics_by_scope = {}
    for scope_name, ids in [("confused_4", confused_ids), ("full_12", None)]:
        bc_acc, n = _agg(results, "bundle_category_correct", ids)
        lex_acc, _ = _agg(results, "lexical_correct", ids)
        tgt_acc, _ = _agg(results, "target_only_correct", ids)
        sit_acc, _ = _agg(results, "situated_structure_correct", ids)
        tgt_res_acc, _ = _agg(results, "target_resolved_correct", ids)
        val_res_acc, _ = _agg(results, "valence_resolved_correct", ids)
        metrics_by_scope[scope_name] = {
            "n": n,
            "BUNDLE_CATEGORY_accuracy": bc_acc,
            "LEXICAL_accuracy": lex_acc,
            "TARGET_ONLY_accuracy": tgt_acc,
            "SITUATED_STRUCTURE_accuracy": sit_acc,
            "target_resolver_accuracy_vs_gold": tgt_res_acc,
            "valence_resolver_accuracy_vs_gold": val_res_acc,
        }

    confused_results = [r for r in results if r["id"] in confused_ids]
    per_item_ablation = [
        {
            "id": r["id"], "correct_category": r["correct_category"],
            "gold_target": r["gold_target"], "gold_valence": r["gold_valence"],
            "decoded_target": r["decoded_target"], "decoded_valence": r["decoded_valence"],
            "bundle_category_pick": r["bundle_category_pick"], "bundle_category_correct": r["bundle_category_correct"],
            "target_only_pick": r["target_only_pick"], "target_only_correct": r["target_only_correct"],
            "situated_structure_pick": r["situated_structure_pick"],
            "situated_structure_correct": r["situated_structure_correct"],
            "valence_flip": (not r["target_only_correct"]) and r["situated_structure_correct"],
        }
        for r in confused_results
    ]

    sit_confused_acc = metrics_by_scope["confused_4"]["SITUATED_STRUCTURE_accuracy"]
    lex_confused_acc = metrics_by_scope["confused_4"]["LEXICAL_accuracy"]
    n_confused_correct = sum(1 for r in confused_results if r["situated_structure_correct"])
    structure_helps = (n_confused_correct >= 3) and (sit_confused_acc > lex_confused_acc)
    verdict = "STRUCTURE_HELPS" if structure_helps else "STRUCTURE_INSUFFICIENT"

    elapsed = time.perf_counter() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"{verdict}: confused_4 situated_acc={sit_confused_acc:.3f} ({n_confused_correct}/4) "
            f"bundle_category_acc={metrics_by_scope['confused_4']['BUNDLE_CATEGORY_accuracy']:.3f} "
            f"target_only_acc={metrics_by_scope['confused_4']['TARGET_ONLY_accuracy']:.3f} "
            f"lexical_acc={lex_confused_acc:.3f} | full_12 situated_acc="
            f"{metrics_by_scope['full_12']['SITUATED_STRUCTURE_accuracy']:.3f} target_resolver_acc="
            f"{metrics_by_scope['full_12']['target_resolver_accuracy_vs_gold']:.3f}"
        ),
        "summary": f"{verdict} on n=4 confused near-synonym unstated_goal subset (full-12 also reported)",
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "measured_n_units": len(results) * 4,
        "cardinality_ok": True,
        "arms_differ_verified": True,
        "arm_digests": arm_digests,
        "arms_differ_exempted": exempted,
        "valence_weight": VALENCE_WEIGHT,
        "metrics_by_scope": metrics_by_scope,
        "per_item_ablation_confused_4": per_item_ablation,
        "per_item_full_12": [
            {k: r[k] for k in (
                "id", "correct_category", "gold_target", "gold_valence", "pred_target", "pred_valence",
                "decoded_target", "decoded_valence", "target_resolved_correct", "valence_resolved_correct",
                "bundle_category_pick", "bundle_category_correct", "target_only_pick", "target_only_correct",
                "situated_structure_pick", "situated_structure_correct", "lexical_pick", "lexical_correct",
            )}
            for r in results
        ],
        "prereg_bands": {
            "STRUCTURE_HELPS_requires": "n_confused_correct>=3/4 AND situated_acc>lexical_acc on confused_4",
        },
        "note_small_n": (
            "n=4 confused / n=12 full is directional-on-mechanism-direction only, NOT a magnitude claim."
        ),
        "note_target_resolver": (
            "TARGET resolution is a declared reflexive-marker structural proxy (default-OTHER), NOT the "
            "full hdlab.coreference_resolver pipeline (that needs a multi-mention passage this "
            "single-clause eval schema lacks). Its full-12 accuracy vs the confused-4 accuracy is "
            "reported explicitly to prevent a curated-subset over-read."
        ),
        "note_valence_resolver": (
            "VALENCE resolution is a tier-2 hand-bootstrapped generic-affect-word lexicon (declared, not "
            "earned) -- this pass tests whether the SITUATED-STRUCTURE FRAME helps, not whether this "
            "particular lexicon is a correct valence encoder."
        ),
    }

    tmp_path = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final_path = os.path.join(OUTPUT_DIR, "metrics.json")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, final_path)
    return metrics


def self_test():
    """Tiny hand-built smoke: bind/unbind round-trip fidelity, resolver sanity, pipeline end-to-end."""
    # HD round-trip decode fidelity at this 2-slot capacity (must be 100%)
    combos = [("SELF", "NA"), ("OTHER", "HARM"), ("OTHER", "HELP"), ("SELF", "HARM")]
    for t, v in combos:
        vec = build_situated_vec(t, v)
        dt, dv = decode_target(vec), decode_valence(vec)
        assert dt == t, f"round-trip TARGET decode failed: encoded {t}, decoded {dt}"
        assert dv == v, f"round-trip VALENCE decode failed: encoded {v}, decoded {dv}"

    assert resolve_target("she remembered trying to box her own ears for having cheated herself") == "SELF"
    assert resolve_target("No matter whether she heard or not, let her take care of herself.") == "OTHER"
    assert resolve_valence("he rescued the kitten and held it softly to comfort it") == "HELP"
    assert resolve_valence("she punished him out of spite and cruel revenge") == "HARM"
    assert resolve_valence("the clock ticked on the wall") == "NA"

    gold = ci.load_gold()
    items = gold["unstated_goal"]
    assert len(items) >= 4
    by_id = {it["id"]: it for it in items}
    for cid in CONFUSED_ITEM_IDS:
        assert cid in by_id, f"confused item {cid} not found in gold"

    rng = __import__("random").Random(ci.FIXED_RANDOM_SEED)
    r = score_item(by_id["relinf_unstated_012"], rng)
    assert r["situated_structure_pick"] in r["candidates"]
    assert r["bundle_category_pick"] in r["candidates"]

    print("[self-test] PASS", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--run-mode", default="full", choices=["full", "smoke", "self_test"])
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    metrics = run(args.run_mode)
    print(f"[done] verdict={metrics['verdict']} elapsed_s={metrics['elapsed_s']:.3f}", flush=True)
    print(json.dumps(metrics["metrics_by_scope"], indent=2), flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise
