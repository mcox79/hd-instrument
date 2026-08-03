"""exp_causal_link_comprehension_pilot_v1 (2026-08-02)

FIRST comprehension-arc cell past role-decode: does a passage-level CAUSE/EFFECT link
register -- reusing the VET'd accumulate situation-model organ's exact bind/unbind/bundle/
cleanup-argmax chain (atom 29609) -- recover the correct linked event on real, mostly
non-adjacent, cross-chapter causal facts from Anne of Green Gables (Trabasso & van den Broek
causal-network model of narrative comprehension), beating a most-recent-event (adjacency)
baseline and a random-link baseline on the require-integration subset?

See notes/prereg_causal_link_comprehension_pilot_v1_2026-08-02.md for the full pre-reg
(bands, gates, capacity note, honest-scope declaration) and
notes/inference_leap_scoping_beyond_role_decode_2026-08-02.md for the design source.

Reuses the PROMOTED hdlab module verbatim (real_code_path_and_signature_preflight):
  hdlab.situation_model_accumulate.CausalLinkRegister (new class added this session,
  subclasses AccumulateRegister -- same primitives, no new mechanism class).

GOLD-ISOLATION: feeds the GOLD cause_event/effect_event spans directly as the event
vocabulary. Does NOT run role/coref extraction on raw text -- isolates the causal-link
organ from the separately-measured ~14.5% coref extraction error.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (prediction-array not-all-identical check; guesses
    are ints not tensors, declared exempt from the tensor-hash form of AF)
  - final_metrics_atomicity = tmp_replace (single-shot)
  - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
  - crlb_n/a (closed-form structural can-fail); discriminator_reachability=true
  - baseline_in_band EXEMPTED for most_recent (can-fail arm near-floor on integration subset
    BY DESIGN; near ceiling on control subset BY DESIGN)
  - chunking / heartbeat EXEMPTED (single seed, single pass, wall time < 10s)
  - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the pre-reg
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.situation_model_accumulate import CausalLinkRegister  # noqa: E402

ANCHOR_NAME = "causal_link_comprehension_pilot_v1"
GOLD_REL = "data/eval_gold_mention_role_mcguffey_v1/gold_anne_comprehension_v1.jsonl"
RAW_TEXT_REL = "data/corpora/anne_of_green_gables/cleaned/anne_of_green_gables.clean.txt"
D_DIM = 1024
INTEGRATION_TYPES = {"cross_chapter_multi_event", "same_chapter_multi_fact_integration"}
CONTROL_TYPE = "local_adjacent_control"
DISTRACTOR_STRIDE = 200  # lines between candidate distractor events
DISTRACTOR_MIN_DIST = 20  # min line-distance from any real gold event to avoid collision


def repo_path(rel: str) -> str:
    return rel if os.path.isabs(rel) else os.path.join(REPO_ROOT, rel)


def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": os.environ.get("COMPUTERNAME", "unknown"),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


# ----------------------------- self-test (fixture: planted link decodes; non-link doesn't) --

def run_self_test() -> None:
    """3-event fixture, real CausalLinkRegister object (real_code_path exercised here too):
    event 0 causes event 1 (planted link). Assert query_effect_of(0)==1 and
    query_cause_of(1)==0. Event 2 has no recorded link at all -- assert both queries on it
    return (None, {}) (honest "no link known", not a spurious wrong guess)."""
    gen = torch.Generator().manual_seed(12345)
    reg = CausalLinkRegister(d=64, generator=gen, max_event_slots=3)
    reg.add_causal_link(cause_idx=0, effect_idx=1)

    eff, _ = reg.query_effect_of(0)
    assert eff == 1, f"SELF_TEST FAIL: query_effect_of(0) expected 1, got {eff}"
    cause, _ = reg.query_cause_of(1)
    assert cause == 0, f"SELF_TEST FAIL: query_cause_of(1) expected 0, got {cause}"

    # event 2 has no CAUSE fact and no EFFECT fact recorded -- must NOT hallucinate a link
    eff2, scores2 = reg.query_effect_of(2)
    assert eff2 is None, f"SELF_TEST FAIL: query_effect_of(2) expected None (no link), got {eff2}"
    cause2, scores2c = reg.query_cause_of(2)
    assert cause2 is None, f"SELF_TEST FAIL: query_cause_of(2) expected None (no link), got {cause2}"

    # event 1 has an EFFECT fact (cause=0) but NO CAUSE fact (it doesn't cause anything) --
    # query_effect_of(1) must also cleanly report "no link known", not guess.
    eff1, _ = reg.query_effect_of(1)
    assert eff1 is None, f"SELF_TEST FAIL: query_effect_of(1) expected None (event 1 has no outgoing CAUSE fact), got {eff1}"


# ----------------------------- gold loading + event dedup -----------------------------------

def _event_key(ev: dict) -> tuple:
    lr = ev["line_range"]
    return (ev["chapter"], lr[0], lr[1])


def mine_distractor_events(raw_text_path: str, real_line_starts: list, stride: int,
                            min_dist: int) -> list:
    """Densify the event vocabulary with REAL raw-text distractor spans at ~stride-line
    intervals, skipping any candidate within min_dist lines of a real gold event (avoids
    accidental collision with the causally-linked events under test). This is the fix for
    the design doc's explicitly-flagged risk: with only the ~25 curated gold events as the
    candidate pool, a "most-recent-in-vocab" adjacency baseline is unfairly weak (large real
    textual gaps collapse to "adjacent" in a sparse curated pool). Distractors give the
    adjacency baseline a genuinely dense candidate set to compete against, matching what a
    real "nearest preceding/following clause in the raw text" heuristic would see.
    Returns list of {key, chapter: None, line_start} dicts (chapter=None marks distractor;
    key is a synthetic tuple so it never collides with a real (chapter, line, line) key)."""
    with open(raw_text_path, "r", encoding="utf-8") as f:
        total_lines = sum(1 for _ in f)
    distractors = []
    for pos in range(1, total_lines, stride):
        if any(abs(pos - rl) < min_dist for rl in real_line_starts):
            continue
        distractors.append({"key": ("distractor", pos), "chapter": None, "line_start": pos})
    return distractors


def load_gold_and_build_vocab(path: str, raw_text_path: str, stride: int, min_dist: int) -> tuple:
    """Returns (items, event_order) where items is the list of gold dicts each augmented
    with cause_idx/effect_idx (global unique-event index), and event_order is the list of
    unique event dicts {key, chapter, line_start} SORTED chronologically (chapter, line_start)
    -- the ordering the most_recent baseline uses. event_order includes both the real gold
    events AND mined raw-text distractor events (see mine_distractor_events)."""
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))

    # dedup unique REAL events by exact (chapter, line_start, line_end) match
    key_to_event = {}
    for it in items:
        for side in ("cause_event", "effect_event"):
            ev = it[side]
            k = _event_key(ev)
            if k not in key_to_event:
                key_to_event[k] = {"key": k, "chapter": ev["chapter"], "line_start": ev["line_range"][0]}

    real_line_starts = [e["line_start"] for e in key_to_event.values()]
    distractors = mine_distractor_events(raw_text_path, real_line_starts, stride, min_dist)

    all_events = list(key_to_event.values()) + distractors
    # deterministic chronological order (sorted, no hash()-derived ordering per META gate F.5)
    event_order = sorted(all_events, key=lambda e: e["line_start"])
    key_to_idx = {e["key"]: i for i, e in enumerate(event_order)}

    for it in items:
        it["cause_idx"] = key_to_idx[_event_key(it["cause_event"])]
        it["effect_idx"] = key_to_idx[_event_key(it["effect_event"])]

    return items, event_order


# ----------------------------- baselines ------------------------------------------------------

def most_recent_effect_of(cause_idx: int, event_order: list) -> int:
    """Adjacency baseline: guess the NEXT event in chronological order (or the previous one
    if cause_idx is the last event -- keeps the guess always defined and always != self)."""
    n = len(event_order)
    if cause_idx + 1 < n:
        return cause_idx + 1
    return max(cause_idx - 1, 0) if n > 1 else cause_idx


def most_recent_cause_of(effect_idx: int, event_order: list) -> int:
    """Adjacency baseline: guess the PREVIOUS event in chronological order (or the next one
    if effect_idx is the first event)."""
    n = len(event_order)
    if effect_idx - 1 >= 0:
        return effect_idx - 1
    return min(effect_idx + 1, n - 1) if n > 1 else effect_idx


def random_other(idx: int, n: int, rng: torch.Generator) -> int:
    """Deterministic seeded-RNG uniform guess over all OTHER events (excludes self)."""
    if n <= 1:
        return idx
    pick = int(torch.randint(0, n - 1, (1,), generator=rng).item())
    return pick if pick < idx else pick + 1


# ----------------------------- main -----------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true", help="run correctness fixture only, tiny scale")
    parser.add_argument("--seed", type=int, default=20260802)
    parser.add_argument("--d", type=int, default=D_DIM)
    parser.add_argument("--gold", type=str, default=GOLD_REL)
    parser.add_argument("--timeout", type=float, default=60.0,
                         help="formula self-test timeout budget (declared; this cell runs in <10s)")
    args = parser.parse_args()

    run_mode = "smoke" if args.self_test else "full"
    output_dir = repo_path(f"data/exp_{ANCHOR_NAME}" + ("_smoke" if args.self_test else ""))
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units=14)

    run_self_test()
    if args.self_test:
        elapsed = time.perf_counter() - t0
        metrics = {
            "verdict": "SELF_TEST_PASS",
            "verdict_msg": "CausalLinkRegister fixture: planted link decodes both directions; non-linked event returns None (no hallucinated guess).",
            "summary": "SELF_TEST_PASS: real CausalLinkRegister object exercised, correctness verified.",
            "elapsed_s": elapsed,
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "anchor_name": ANCHOR_NAME,
            "run_mode": run_mode,
            "seed": args.seed,
        }
        tmp = os.path.join(output_dir, "metrics.json.tmp")
        final = os.path.join(output_dir, "metrics.json")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        os.replace(tmp, final)
        print(f"[{ANCHOR_NAME}] SELF_TEST_PASS -> {final}")
        return

    # ---- full run ----
    d = args.d
    gold_path = repo_path(args.gold)
    raw_text_path = repo_path(RAW_TEXT_REL)
    items, event_order = load_gold_and_build_vocab(
        gold_path, raw_text_path, DISTRACTOR_STRIDE, DISTRACTOR_MIN_DIST
    )
    n_unique = len(event_order)
    n_distractors = sum(1 for e in event_order if e["chapter"] is None)
    n_real_events = n_unique - n_distractors
    assert n_unique >= 3, f"expected a real multi-event vocabulary, got n_unique={n_unique}"

    gen = torch.Generator().manual_seed(args.seed)
    reg = CausalLinkRegister(d=d, generator=gen, max_event_slots=n_unique)

    for it in items:
        reg.add_causal_link(cause_idx=it["cause_idx"], effect_idx=it["effect_idx"])

    rng_random = torch.Generator().manual_seed(args.seed + 999)

    per_item = []
    for it in items:
        c_idx, e_idx = it["cause_idx"], it["effect_idx"]

        organ_eff, _ = reg.query_effect_of(c_idx)
        organ_cause, _ = reg.query_cause_of(e_idx)
        mr_eff = most_recent_effect_of(c_idx, event_order)
        mr_cause = most_recent_cause_of(e_idx, event_order)
        rand_eff = random_other(c_idx, n_unique, rng_random)
        rand_cause = random_other(e_idx, n_unique, rng_random)

        per_item.append({
            "id": it["id"],
            "item_type": it["item_type"],
            "chapter_gap": it["chapter_gap"],
            "cause_idx": c_idx,
            "effect_idx": e_idx,
            "organ_effect_of_correct": int(organ_eff == e_idx),
            "organ_cause_of_correct": int(organ_cause == c_idx),
            "most_recent_effect_of_correct": int(mr_eff == e_idx),
            "most_recent_cause_of_correct": int(mr_cause == c_idx),
            "random_effect_of_correct": int(rand_eff == e_idx),
            "random_cause_of_correct": int(rand_cause == c_idx),
        })

    # ---- ARMS-MUST-DIFFER (META_RULE_AF, int-prediction-array form; not tensor hash since
    # guesses are ints not tensors -- declared exemption from the tensor-hash form in pre-reg) --
    organ_preds = tuple((r["organ_effect_of_correct"], r["organ_cause_of_correct"]) for r in per_item)
    mr_preds = tuple((r["most_recent_effect_of_correct"], r["most_recent_cause_of_correct"]) for r in per_item)
    rand_preds = tuple((r["random_effect_of_correct"], r["random_cause_of_correct"]) for r in per_item)
    arms_differ = not (organ_preds == mr_preds == rand_preds)
    assert arms_differ, "META_RULE_AF VIOLATION: organ/most_recent/random arms produced identical predictions across all items"

    integration_items = [r for r in per_item if r["item_type"] in INTEGRATION_TYPES]
    control_items = [r for r in per_item if r["item_type"] == CONTROL_TYPE]
    assert len(integration_items) + len(control_items) == len(per_item), "unexpected item_type in gold"

    def combined(subset, arm):
        vals = []
        for r in subset:
            vals.append(r[f"{arm}_effect_of_correct"])
            vals.append(r[f"{arm}_cause_of_correct"])
        return (float(sum(vals)) / len(vals)) if vals else None

    organ_integration = combined(integration_items, "organ")
    organ_control = combined(control_items, "organ")
    mr_integration = combined(integration_items, "most_recent")
    mr_control = combined(control_items, "most_recent")
    rand_integration = combined(integration_items, "random")
    rand_control = combined(control_items, "random")

    chance = 1.0 / (n_unique - 1) if n_unique > 1 else 0.0

    # ---- can-fail gates ----
    gate_mr_near_floor_integration = mr_integration is not None and mr_integration <= chance + 0.15
    gate_mr_clears_control = mr_control is not None and mr_control >= 0.50
    gate_random_near_chance_integration = rand_integration is not None and abs(rand_integration - chance) <= 0.20
    gate_random_near_chance_control = rand_control is not None and abs(rand_control - chance) <= 0.20
    canfail_ok = (
        gate_mr_near_floor_integration and gate_mr_clears_control
        and gate_random_near_chance_integration and gate_random_near_chance_control
    )

    best_baseline_integration = max(v for v in (mr_integration, rand_integration) if v is not None)
    gap = (organ_integration - best_baseline_integration) if organ_integration is not None else None
    gate_hard_pass = canfail_ok and gap is not None and gap >= 0.30 and organ_integration >= 0.50
    gate_middle_band = canfail_ok and gap is not None and (
        (0.10 <= gap < 0.30) or (chance + 0.05 <= organ_integration < 0.50)
    )

    n_pilot = len(integration_items)
    pilot_flag = (
        f"PILOT (N={n_pilot} require-integration items); per pre-reg's own recommendation "
        f"this is undersized for a scored/landed capability claim -- mine the fuller gold set "
        f"(25-40 items) before treating this number as more than a directional pilot result."
    )

    if not canfail_ok:
        verdict = "HARD_FAIL_CANFAIL_VIOLATION"
        verdict_msg = (
            f"CAN-FAIL gate violated -- harness/vocab-construction bug suspected, investigate "
            f"before trusting the organ result. most_recent_integration={mr_integration:.4f} "
            f"(gate near-floor<= {chance+0.15:.4f}: {gate_mr_near_floor_integration}); "
            f"most_recent_control={mr_control:.4f} (gate>=0.50: {gate_mr_clears_control}); "
            f"random_integration={rand_integration:.4f} vs chance={chance:.4f} "
            f"(gate: {gate_random_near_chance_integration}); "
            f"random_control={rand_control:.4f} (gate: {gate_random_near_chance_control}). {pilot_flag}"
        )
    elif gate_hard_pass:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"WORKS-pilot: organ beats both baselines on the require-integration subset "
            f"(organ={organ_integration:.4f} vs best_baseline={best_baseline_integration:.4f}, "
            f"gap={gap:.4f} >= 0.30; most_recent collapses to {mr_integration:.4f} on "
            f"non-adjacent items as expected, chance={chance:.4f}); can-fail gates held "
            f"(most_recent clears control={mr_control:.4f}, random stays near chance both "
            f"subsets). {pilot_flag}"
        )
    elif gate_middle_band:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: organ beats baselines but below HARD_PASS bar (gap={gap:.4f}, "
            f"organ={organ_integration:.4f}). Can-fail gates held (harness trustworthy). {pilot_flag}"
        )
    else:
        verdict = "HARD_FAIL_MECHANISM"
        verdict_msg = (
            f"HARD_FAIL: can-fail gates held (harness trustworthy) but organ did NOT clearly "
            f"beat the baselines on the require-integration subset (gap="
            f"{gap if gap is not None else 'n/a'}, organ={organ_integration}). "
            f"Diagnose: event-slot vocabulary size (n_unique={n_unique}), cross-chapter "
            f"indexing, or causal-link binding capacity before re-attempting. {pilot_flag}"
        )

    gates = {
        "gate_mr_near_floor_integration": gate_mr_near_floor_integration,
        "gate_mr_clears_control": gate_mr_clears_control,
        "gate_random_near_chance_integration": gate_random_near_chance_integration,
        "gate_random_near_chance_control": gate_random_near_chance_control,
        "canfail_ok": canfail_ok,
        "gate_hard_pass": gate_hard_pass,
        "gate_middle_band": gate_middle_band,
    }

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"{verdict} | PILOT N_integration={n_pilot} N_control={len(control_items)} | "
            f"organ_integration={organ_integration:.4f} organ_control={organ_control:.4f} | "
            f"most_recent_integration={mr_integration:.4f} most_recent_control={mr_control:.4f} | "
            f"random_integration={rand_integration:.4f} random_control={rand_control:.4f} | "
            f"chance={chance:.4f} n_unique_events={n_unique}"
        ),
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "seed": args.seed,
        "d": d,
        "gold_path": gold_path,
        "n_items_total": len(per_item),
        "n_unique_events": n_unique,
        "n_real_gold_events": n_real_events,
        "n_distractor_events_mined": n_distractors,
        "distractor_stride_lines": DISTRACTOR_STRIDE,
        "distractor_min_dist_lines": DISTRACTOR_MIN_DIST,
        "max_event_slots_used": n_unique,
        "chance": chance,
        "organ_accuracy_integration": organ_integration,
        "organ_accuracy_control": organ_control,
        "most_recent_accuracy_integration": mr_integration,
        "most_recent_accuracy_control": mr_control,
        "random_accuracy_integration": rand_integration,
        "random_accuracy_control": rand_control,
        "gap_organ_vs_best_baseline_integration": gap,
        "gates": gates,
        "per_item_records": per_item,
        "arms_differ_verified": True,
        "capacity_note": (
            f"max_event_slots raised from AccumulateRegister default (8) to n_unique_events="
            f"{n_unique} ({n_real_events} real gold events + {n_distractors} mined raw-text "
            f"distractor events, densifying the adjacency-baseline candidate pool) to span the "
            f"whole-book chronological event vocabulary (chapter_gap up to 23 in this gold). At "
            f"d={d} and at most 2 bundled CAUSE/EFFECT facts per entity (the 3 genuine "
            f"multi-fact collisions in this gold: shared cause anne_causal_001/002, shared "
            f"effect anne_causal_010/011, 2-hop chain anne_causal_013->005 -- distractors carry "
            f"zero causal facts, only cleanup-competition vocabulary mass), this stays far below "
            f"FHRR's empirically observed cleanup capacity ceiling (prior organ still 0.66 "
            f"recall at bundle load 4, N=25-60 vocabulary far below typical d=1024 sqrt(d)-class "
            f"headroom). Single-bank CausalLinkRegister suffices for THIS pilot's scale; a "
            f"full-scale multi-book build (hundreds-thousands of events) would plausibly need "
            f"the multi-bank hdlab.working_memory backend a sibling agent is building this "
            f"session for capacity -- forward note, not required here."
        ),
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "passed_all_4_patterns_heartbeat_exempt_lt10s",
    }

    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, final_path)

    print(f"[{ANCHOR_NAME}] {verdict} elapsed={elapsed:.2f}s -> {final_path}")


if __name__ == "__main__":
    _output_dir_for_crash = repo_path(f"data/exp_{ANCHOR_NAME}")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_output_dir_for_crash, e)
        raise
