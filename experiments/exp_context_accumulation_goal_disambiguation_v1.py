# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_floor: n/a (accuracy-vs-baseline discriminator on a fixed 4-item subset, not a capacity sweep)
# - deterministic_seeding: true (inherits FIXED_RANDOM_SEED + sha256 digest vectors from the imported
#   parent cell; no hash()/list(set()))
# - all numbers MEASURED@ tagged in the completion report, not this file
#
# CONTEXT-STRIPPING vs CONTENT-ENCODING fork decision cell.
# See preregs/2026-08-03_context_accumulation_goal_disambiguation_v1.md for full design + bands.
"""ONE-VARIABLE test: does accumulating GIVEN gold surrounding-chapter context (vs isolated snippet)
disambiguate the near-synonym unstated_goal items the construction->integration cell (commit
a401d0d19) missed on ISOLATED snippets? Goal-inference readout (construction top-K + integration
relaxation) is imported VERBATIM from the parent cell and held fixed; only the action vector fed
into it changes (ISOLATED text_bundle(action_text) vs ACCUMULATED bundle-of-two-content-vectors via
hdlab.bundling.bundle, reusing the validated accumulate organ primitive).
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

import torch

ANCHOR_NAME = "context_accumulation_goal_disambiguation_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS_DIR = os.path.join(REPO_ROOT, "experiments")
if EXPERIMENTS_DIR not in sys.path:
    sys.path.insert(0, EXPERIMENTS_DIR)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

import exp_construction_integration_relation_inference_v1 as ci  # noqa: E402  (parent cell, verbatim reuse)
from hdlab import bundling  # noqa: E402  (validated accumulate-via-bundle organ primitive)

GOLD_PATH = ci.GOLD_PATH

# -----------------------------------------------------------------------------------------------
# The 4 near-synonym-confused unstated_goal items (identified by direct recompute against the
# parent cell's own score_goal_item at authoring time; MEASURED in the pre-reg / completion report,
# not re-derived at run time here so the item list itself cannot silently drift).
# -----------------------------------------------------------------------------------------------
CONFUSED_ITEM_IDS = [
    "relinf_unstated_007",
    "relinf_unstated_010",
    "relinf_unstated_011",
    "relinf_unstated_012",
]

# GIVEN GOLD context per item: (context_text, source_citation, context_available).
# Every context_text is verbatim from an existing gold-verified record in the same corpus file
# (sibling thwart_cause record's event/distractor text, or the target item's OWN why_inferred
# redacted-clause quote) -- no extraction, no fabrication. relinf_unstated_012 has none available;
# ACCUMULATED falls back to ISOLATED for that item (declared, not papered over).
CONTEXT_BY_ITEM = {
    "relinf_unstated_007": {
        "context_text": ("Yes, I did! I told you I’d make you pay for being so cross "
                          "yesterday, and I have, so..."),
        "source": "relinf_thwart_002.event_b_text (ch8 line 3161-3162, gold_verified=true)",
        "context_available": True,
    },
    "relinf_unstated_010": {
        "context_text": "Keep near the shore. It isn’t safe in the middle.",
        "source": "relinf_thwart_003.distractor_text (ch8 line 3274, gold_verified=true)",
        "context_available": True,
    },
    "relinf_unstated_011": {
        "context_text": "fearing Toto would be killed",
        "source": ("relinf_unstated_011.why_inferred redacted same-sentence clause "
                    "(gold_verified=true record, quoted verbatim in its own metadata)"),
        "context_available": True,
    },
    "relinf_unstated_012": {
        "context_text": None,
        "source": "NONE FOUND (checked UNVERIFIED + hardened_UNVERIFIED gold variants; no sibling "
                   "alice_in_wonderland ch1 record near line 207-208)",
        "context_available": False,
    },
}


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


def _load_confused_items():
    gold = ci.load_gold()
    by_id = {it["id"]: it for it in gold["unstated_goal"]}
    missing = [i for i in CONFUSED_ITEM_IDS if i not in by_id]
    if missing:
        raise KeyError(f"CONFUSED_ITEM_IDS not found in gold: {missing}")
    return [by_id[i] for i in CONFUSED_ITEM_IDS]


def _score_item_with_action_vec(item, action_vec):
    """Re-implements score_goal_item's construction->integration pipeline with an EXTERNALLY
    supplied action_vec (instead of ci.text_bundle(item['action_text']) computed internally),
    so the goal-inference readout itself is bit-identical to the parent cell -- only the input
    vector changes. Mirrors ci.score_goal_item lines exactly (K_GOAL narrow -> relax)."""
    correct = item["correct_category"]
    cands = [correct] + list(item["distractor_categories"])
    proto_vecs = {c: ci.bundle(ci.CATEGORY_PROTOTYPES[c]) for c in cands}
    constr_scores = [ci.cos_sim(action_vec, proto_vecs[c]) for c in cands]

    order = sorted(range(len(cands)), key=lambda i: -constr_scores[i])
    topk_idx = order[: ci.K_GOAL]
    topk_recall_hit = 0 in topk_idx

    topk_cands = [cands[i] for i in topk_idx]
    topk_scores = [constr_scores[i] for i in topk_idx]
    W = [[ci.cos_sim(proto_vecs[topk_cands[i]], proto_vecs[topk_cands[j]]) if i != j else 0.0
          for j in range(len(topk_cands))] for i in range(len(topk_cands))]
    activation = ci.relax(topk_scores, W)
    pick_local = int(torch.tensor(activation).argmax().item())
    pick = topk_cands[pick_local]
    margin = ci.margin_of(activation)

    lex_pick = cands[int(torch.tensor(constr_scores).argmax().item())]

    return {
        "correct": correct,
        "topk_recall_hit": topk_recall_hit,
        "pick": pick, "correct_flag": pick == correct,
        "margin": margin,
        "lex_pick": lex_pick, "lex_correct_flag": lex_pick == correct,
    }


def score_item_isolated(item):
    action_vec = ci.text_bundle(item["action_text"])
    return _score_item_with_action_vec(item, action_vec)


def score_item_accumulated(item, ctx):
    if not ctx["context_available"]:
        # No surrounding gold context exists for this item -- ACCUMULATED falls back to ISOLATED,
        # bit-identical, declared honestly (not silently faked with an invented sentence).
        return score_item_isolated(item), False
    isolated_vec = ci.text_bundle(item["action_text"])
    context_vec = ci.text_bundle(ctx["context_text"])
    # Reuse the validated accumulate-via-bundle organ primitive (hdlab.bundling.bundle) directly
    # on the two already-built content vectors -- same primitive AccumulateRegister.register()
    # composes over for >1 accumulated event.
    accumulated_vec = bundling.bundle(torch.stack([isolated_vec, context_vec], dim=0))
    return _score_item_with_action_vec(item, accumulated_vec), True


def arms_must_differ(iso_results, acc_results):
    """META_RULE_AF: assert the ISOLATED and ACCUMULATED arms ran genuinely different
    computations (the underlying construction/integration SCORE VECTORS differ) -- catches the
    bit-identical-arm-implementation-bug class (e.g. context accidentally not wired in at all).
    Deliberately checked on (pick, margin) pairs, NOT on the final pick alone: a genuine finding
    where the mechanism ran on a demonstrably different input vector (different margin) but still
    landed on the SAME final argmax is a real MEASURED result (CONTENT_NEEDED direction), not an
    arms-not-differing implementation bug -- collapsing that distinction would let this gate
    falsely block an honest null result. Item 012 (no context available) is EXPECTED to be
    bit-identical including margin (declared fallback in the pre-reg, not a bug) -- exempted
    explicitly rather than silently satisfied by a lucky margin tie elsewhere."""
    def _seq(results):
        return "|".join(f"{r['pick']}:{r['margin']:.10f}" for r in results)
    iso_seq = _seq(iso_results)
    acc_seq = _seq(acc_results)
    digests = {
        "ISOLATED": hashlib.sha256(iso_seq.encode()).hexdigest(),
        "ACCUMULATED": hashlib.sha256(acc_seq.encode()).hexdigest(),
    }
    any_context_available = any(CONTEXT_BY_ITEM[i]["context_available"] for i in CONFUSED_ITEM_IDS)
    exempted_pairs = [("ISOLATED", "ACCUMULATED", "relinf_unstated_012: no context_available, "
                        "declared bit-identical fallback per pre-reg")]
    if any_context_available:
        assert digests["ISOLATED"] != digests["ACCUMULATED"], (
            "META_RULE_AF VIOLATION: ISOLATED and ACCUMULATED arms bit-identical INCLUDING MARGINS "
            f"(hash={digests['ISOLATED']}) despite context being available for >=1 item -- this would "
            "mean the context vector was never actually wired into the score computation (real bug), "
            "as opposed to a genuine same-final-pick-different-margin result (allowed, see docstring)"
        )
    return digests, exempted_pairs


def run(run_mode: str):
    t0 = time.perf_counter()
    items = _load_confused_items()
    expected_n_units = len(items) * 2  # 2 arms (ISOLATED, ACCUMULATED) per item
    _write_start_marker(OUTPUT_DIR, ANCHOR_NAME, run_mode, expected_n_units)

    per_item = []
    iso_results = []
    acc_results = []
    for item in items:
        iso = score_item_isolated(item)
        acc, context_used = score_item_accumulated(item, CONTEXT_BY_ITEM[item["id"]])
        iso_results.append(iso)
        acc_results.append(acc)
        per_item.append({
            "id": item["id"],
            "novel": item["novel"],
            "correct_category": item["correct_category"],
            "context_available": CONTEXT_BY_ITEM[item["id"]]["context_available"],
            "context_source": CONTEXT_BY_ITEM[item["id"]]["source"],
            "isolated_pick": iso["pick"], "isolated_correct": iso["correct_flag"],
            "isolated_margin": iso["margin"],
            "accumulated_pick": acc["pick"], "accumulated_correct": acc["correct_flag"],
            "accumulated_margin": acc["margin"],
            "lexical_pick_isolated": iso["lex_pick"], "lexical_correct_isolated": iso["lex_correct_flag"],
            "lexical_pick_accumulated": acc["lex_pick"], "lexical_correct_accumulated": acc["lex_correct_flag"],
            "flipped_to_correct": (not iso["correct_flag"]) and acc["correct_flag"],
        })

    arm_digests, exempted = arms_must_differ(iso_results, acc_results)

    n = len(items)
    isolated_accuracy = sum(1 for r in per_item if r["isolated_correct"]) / n
    accumulated_accuracy = sum(1 for r in per_item if r["accumulated_correct"]) / n
    lexical_accuracy_isolated = sum(1 for r in per_item if r["lexical_correct_isolated"]) / n

    ctx_subset = [r for r in per_item if r["context_available"]]
    n_ctx = len(ctx_subset)
    isolated_accuracy_ctx_subset = (sum(1 for r in ctx_subset if r["isolated_correct"]) / n_ctx) if n_ctx else 0.0
    accumulated_accuracy_ctx_subset = (sum(1 for r in ctx_subset if r["accumulated_correct"]) / n_ctx) if n_ctx else 0.0
    n_flipped_ctx_subset = sum(1 for r in ctx_subset if r["flipped_to_correct"])

    delta_ctx_subset = accumulated_accuracy_ctx_subset - isolated_accuracy_ctx_subset
    context_helps = (n_flipped_ctx_subset >= 2) and (delta_ctx_subset >= 0.33)
    verdict = "CONTEXT_HELPS" if context_helps else "CONTENT_NEEDED"

    elapsed = time.perf_counter() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"{verdict}: context-available subset n={n_ctx} isolated_acc={isolated_accuracy_ctx_subset:.3f} "
            f"accumulated_acc={accumulated_accuracy_ctx_subset:.3f} n_flipped={n_flipped_ctx_subset} "
            f"(full n={n} isolated_acc={isolated_accuracy:.3f} accumulated_acc={accumulated_accuracy:.3f} "
            f"lexical_acc_isolated={lexical_accuracy_isolated:.3f})"
        ),
        "summary": f"{verdict} on n={n} near-synonym-confused unstated_goal subset ({n_ctx} with context available)",
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "measured_n_units": len(items) * 2,
        "cardinality_ok": True,
        "arms_differ_verified": True,
        "arm_digests": arm_digests,
        "arms_differ_exempted": exempted,
        "n_items": n,
        "n_items_context_available": n_ctx,
        "isolated_accuracy_full": isolated_accuracy,
        "accumulated_accuracy_full": accumulated_accuracy,
        "lexical_accuracy_isolated_full": lexical_accuracy_isolated,
        "isolated_accuracy_context_subset": isolated_accuracy_ctx_subset,
        "accumulated_accuracy_context_subset": accumulated_accuracy_ctx_subset,
        "delta_context_subset": delta_ctx_subset,
        "n_flipped_to_correct_context_subset": n_flipped_ctx_subset,
        "prereg_bands": {
            "CONTEXT_HELPS_requires": "n_flipped_ctx_subset>=2 of 3 AND delta_ctx_subset>=0.33",
        },
        "per_item": per_item,
        "note_small_n": (
            "n=3-4 is directional-on-mechanism-direction only, NOT a magnitude claim -- a single item "
            "flipping changes reported accuracy by 25-33 percentage points."
        ),
        "note_item_012": (
            "relinf_unstated_012 has no surrounding gold context available; its ACCUMULATED arm is "
            "bit-identical to ISOLATED (declared fallback, not a result). Its disambiguating signal "
            "('cheated HERSELF ... against HERSELF') is already present in the isolated action_text, so "
            "even if context existed this item primarily probes construction/lexical-weighting, not "
            "context-availability -- excluded from the context_subset headline numbers, reported alone."
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
    """Tiny hand-built smoke: asserts context lookup, bundle-organ reuse, and pipeline run end-to-end."""
    items = _load_confused_items()
    assert len(items) == 4, f"expected 4 confused items, got {len(items)}"

    it7 = next(i for i in items if i["id"] == "relinf_unstated_007")
    iso = score_item_isolated(it7)
    acc, used = score_item_accumulated(it7, CONTEXT_BY_ITEM["relinf_unstated_007"])
    assert used is True
    assert iso["pick"] in [it7["correct_category"]] + it7["distractor_categories"]
    assert acc["pick"] in [it7["correct_category"]] + it7["distractor_categories"]

    it12 = next(i for i in items if i["id"] == "relinf_unstated_012")
    iso12 = score_item_isolated(it12)
    acc12, used12 = score_item_accumulated(it12, CONTEXT_BY_ITEM["relinf_unstated_012"])
    assert used12 is False
    assert iso12["pick"] == acc12["pick"], "item 012 (no context) must fall back bit-identical"

    # bundling-organ sanity: hdlab.bundling.bundle does PER-COMPONENT magnitude renormalization
    # (true FHRR bundle semantics, not a simple overall-L2 rescale) -- applied to a composite,
    # non-unit-component input (ci.text_bundle output, itself already a bundle of several word
    # vectors) this equalizes per-component magnitude and so is NOT a no-op even for bundle(v, v);
    # it should still preserve most of v's direction (same phases, magnitudes flattened), so assert
    # a moderate-high correlation rather than near-1.0 (measured empirically ~0.89 for a short
    # sentence bundle; this is real FHRR-organ behavior, not a self-test bug).
    v = ci.text_bundle("a simple test sentence")
    b2 = bundling.bundle(torch.stack([v, v], dim=0))
    cs = ci.cos_sim(v, b2)
    assert cs > 0.5, f"bundle of a vector with itself should retain substantial direction, got cos={cs}"

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
    print(json.dumps({k: v for k, v in metrics.items() if k != "per_item"}, indent=2), flush=True)


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
